"""
Sistema de Alertas para Omni Keywords Finder
Monitora condições críticas e envia notificações quando thresholds são ultrapassados
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict

from redis import Redis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Níveis de severidade dos alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Status dos alertas"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    description: str
    condition: Callable
    severity: AlertSeverity
    threshold: float
    cooldown_minutes: int = 5
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Alerta ativo"""
    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertManager:
    """Gerenciador principal de alertas"""
    
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.notification_handlers: Dict[str, Callable] = {}
        self.is_running = False
        self.check_interval = 30  # segundos
        
        # Configurações de notificação
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_email": ""
        }
        
        self.slack_config = {
            "webhook_url": "",
            "channel": "#alerts"
        }
        
        self.telegram_config = {
            "bot_token": "",
            "chat_id": ""
        }
    
    def register_rule(self, rule: AlertRule):
        """Registra uma nova regra de alerta"""
        self.rules[rule.name] = rule
        logger.info(f"Regra de alerta registrada: {rule.name}")
    
    def register_notification_handler(self, channel: str, handler: Callable):
        """Registra um handler de notificação"""
        self.notification_handlers[channel] = handler
        logger.info(f"Handler de notificação registrado: {channel}")
    
    def start_monitoring(self):
        """Inicia o monitoramento de alertas"""
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self._monitor_alerts())
            logger.info("Monitoramento de alertas iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento de alertas"""
        self.is_running = False
        logger.info("Monitoramento de alertas parado")
    
    async def _monitor_alerts(self):
        """Loop principal de monitoramento"""
        while self.is_running:
            try:
                await self._check_all_rules()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Erro no monitoramento de alertas: {str(e)}")
                await asyncio.sleep(10)
    
    async def _check_all_rules(self):
        """Verifica todas as regras de alerta"""
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                # Verifica se a regra foi disparada
                if await rule.condition():
                    await self._trigger_alert(rule)
                else:
                    await self._resolve_alert(rule_name)
                    
            except Exception as e:
                logger.error(f"Erro ao verificar regra {rule_name}: {str(e)}")
    
    async def _trigger_alert(self, rule: AlertRule):
        """Dispara um alerta"""
        alert_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Verifica se já existe um alerta ativo para esta regra
        existing_alert = self._get_active_alert(rule.name)
        if existing_alert:
            # Verifica se está no período de cooldown
            if datetime.now() - existing_alert.timestamp < timedelta(minutes=rule.cooldown_minutes):
                return
        
        # Cria novo alerta
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            severity=rule.severity,
            message=f"Alerta {rule.severity.value.upper()}: {rule.description}",
            details={"threshold": rule.threshold},
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_id] = alert
        
        # Salva no Redis
        await self._save_alert(alert)
        
        # Envia notificações
        await self._send_notifications(alert, rule)
        
        logger.warning(f"Alerta disparado: {alert.message}")
    
    async def _resolve_alert(self, rule_name: str):
        """Resolve alertas para uma regra"""
        alerts_to_resolve = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.rule_name == rule_name and alert.status == AlertStatus.ACTIVE
        ]
        
        for alert_id in alerts_to_resolve:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            await self._save_alert(alert)
            logger.info(f"Alerta resolvido: {alert.message}")
    
    def _get_active_alert(self, rule_name: str) -> Optional[Alert]:
        """Obtém alerta ativo para uma regra"""
        for alert in self.active_alerts.values():
            if alert.rule_name == rule_name and alert.status == AlertStatus.ACTIVE:
                return alert
        return None
    
    async def _save_alert(self, alert: Alert):
        """Salva alerta no Redis"""
        try:
            alert_data = {
                "id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "details": alert.details,
                "timestamp": alert.timestamp.isoformat(),
                "status": alert.status.value,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            
            await self.redis_client.hset(f"alert:{alert.id}", mapping=alert_data)
            await self.redis_client.expire(f"alert:{alert.id}", 86400 * 7)  # 7 dias
            
        except Exception as e:
            logger.error(f"Erro ao salvar alerta: {str(e)}")
    
    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Envia notificações para todos os canais configurados"""
        for channel in rule.notification_channels:
            if channel in self.notification_handlers:
                try:
                    await self.notification_handlers[channel](alert, rule)
                except Exception as e:
                    logger.error(f"Erro ao enviar notificação via {channel}: {str(e)}")


class EmailNotifier:
    """Notificador via email"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
    
    async def send_alert(self, alert: Alert, rule: AlertRule):
        """Envia alerta por email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['from_email']
            msg['To'] = self.config.get('to_email', self.config['from_email'])
            msg['Subject'] = f"[ALERTA {alert.severity.value.upper()}] {rule.name}"
            
            body = f"""
            <h2>Alerta de Sistema</h2>
            <p><strong>Regra:</strong> {rule.name}</p>
            <p><strong>Severidade:</strong> {alert.severity.value.upper()}</p>
            <p><strong>Mensagem:</strong> {alert.message}</p>
            <p><strong>Descrição:</strong> {rule.description}</p>
            <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Detalhes:</strong> {json.dumps(alert.details, indent=2)}</p>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Envia email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)
            
            logger.info(f"Alerta enviado por email: {alert.message}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")


class SlackNotifier:
    """Notificador via Slack"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
    
    async def send_alert(self, alert: Alert, rule: AlertRule):
        """Envia alerta para Slack"""
        try:
            color_map = {
                AlertSeverity.LOW: "#36a64f",
                AlertSeverity.MEDIUM: "#ffa500",
                AlertSeverity.HIGH: "#ff8c00",
                AlertSeverity.CRITICAL: "#ff0000"
            }
            
            payload = {
                "channel": self.config['channel'],
                "attachments": [{
                    "color": color_map.get(alert.severity, "#808080"),
                    "title": f"🚨 Alerta {alert.severity.value.upper()}: {rule.name}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Descrição",
                            "value": rule.description,
                            "short": False
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            "short": True
                        },
                        {
                            "title": "Severidade",
                            "value": alert.severity.value.upper(),
                            "short": True
                        }
                    ],
                    "footer": "Omni Keywords Finder - Sistema de Alertas"
                }]
            }
            
            response = requests.post(self.config['webhook_url'], json=payload)
            response.raise_for_status()
            
            logger.info(f"Alerta enviado para Slack: {alert.message}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar para Slack: {str(e)}")


class TelegramNotifier:
    """Notificador via Telegram"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
    
    async def send_alert(self, alert: Alert, rule: AlertRule):
        """Envia alerta para Telegram"""
        try:
            emoji_map = {
                AlertSeverity.LOW: "🟢",
                AlertSeverity.MEDIUM: "🟡",
                AlertSeverity.HIGH: "🟠",
                AlertSeverity.CRITICAL: "🔴"
            }
            
            message = f"""
{emoji_map.get(alert.severity, "⚪")} *ALERTA {alert.severity.value.upper()}*

*Regra:* {rule.name}
*Mensagem:* {alert.message}
*Descrição:* {rule.description}
*Timestamp:* {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

*Detalhes:*
```json
{json.dumps(alert.details, indent=2)}
```

_Omni Keywords Finder - Sistema de Alertas_
            """
            
            url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
            payload = {
                "chat_id": self.config['chat_id'],
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Alerta enviado para Telegram: {alert.message}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar para Telegram: {str(e)}")


class AlertRules:
    """Definições das regras de alerta"""
    
    @staticmethod
    async def high_cpu_usage(threshold: float = 80.0) -> bool:
        """Alerta para uso alto de CPU"""
        import psutil
        return psutil.cpu_percent(interval=1) > threshold
    
    @staticmethod
    async def high_memory_usage(threshold: float = 85.0) -> bool:
        """Alerta para uso alto de memória"""
        import psutil
        memory = psutil.virtual_memory()
        return memory.percent > threshold
    
    @staticmethod
    async def low_disk_space(threshold: float = 90.0) -> bool:
        """Alerta para espaço em disco baixo"""
        import psutil
        disk = psutil.disk_usage('/')
        return (disk.used / disk.total) * 100 > threshold
    
    @staticmethod
    async def high_error_rate(threshold: float = 10.0) -> bool:
        """Alerta para taxa alta de erros"""
        # Esta função precisaria ser implementada com dados reais de métricas
        return False
    
    @staticmethod
    async def slow_response_time(threshold: float = 5.0) -> bool:
        """Alerta para tempo de resposta lento"""
        # Esta função precisaria ser implementada com dados reais de métricas
        return False
    
    @staticmethod
    async def database_connection_issues() -> bool:
        """Alerta para problemas de conexão com banco"""
        # Esta função precisaria ser implementada com dados reais de métricas
        return False


# Instância global do alert manager
alert_manager = None


def initialize_alerting_system(redis_client: Redis, config: Dict[str, Any]):
    """Inicializa o sistema de alertas"""
    global alert_manager
    
    alert_manager = AlertManager(redis_client)
    
    # Configura notificadores
    if config.get('email'):
        email_notifier = EmailNotifier(config['email'])
        alert_manager.register_notification_handler('email', email_notifier.send_alert)
    
    if config.get('slack'):
        slack_notifier = SlackNotifier(config['slack'])
        alert_manager.register_notification_handler('slack', slack_notifier.send_alert)
    
    if config.get('telegram'):
        telegram_notifier = TelegramNotifier(config['telegram'])
        alert_manager.register_notification_handler('telegram', telegram_notifier.send_alert)
    
    # Registra regras de alerta
    alert_manager.register_rule(AlertRule(
        name="high_cpu_usage",
        description="Uso de CPU acima de 80%",
        condition=lambda: AlertRules.high_cpu_usage(80.0),
        severity=AlertSeverity.HIGH,
        threshold=80.0,
        notification_channels=['email', 'slack']
    ))
    
    alert_manager.register_rule(AlertRule(
        name="high_memory_usage",
        description="Uso de memória acima de 85%",
        condition=lambda: AlertRules.high_memory_usage(85.0),
        severity=AlertSeverity.HIGH,
        threshold=85.0,
        notification_channels=['email', 'slack']
    ))
    
    alert_manager.register_rule(AlertRule(
        name="low_disk_space",
        description="Espaço em disco abaixo de 10%",
        condition=lambda: AlertRules.low_disk_space(90.0),
        severity=AlertSeverity.CRITICAL,
        threshold=90.0,
        notification_channels=['email', 'slack', 'telegram']
    ))
    
    # Inicia monitoramento
    alert_manager.start_monitoring()
    
    logger.info("Sistema de alertas inicializado")


async def get_active_alerts() -> List[Dict[str, Any]]:
    """Obtém alertas ativos"""
    if not alert_manager:
        return []
    
    active_alerts = []
    for alert in alert_manager.active_alerts.values():
        if alert.status == AlertStatus.ACTIVE:
            active_alerts.append({
                "id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "details": alert.details
            })
    
    return active_alerts


async def acknowledge_alert(alert_id: str, user: str):
    """Reconhece um alerta"""
    if not alert_manager:
        return False
    
    for alert in alert_manager.active_alerts.values():
        if alert.id == alert_id and alert.status == AlertStatus.ACTIVE:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user
            alert.acknowledged_at = datetime.now()
            
            await alert_manager._save_alert(alert)
            return True
    
    return False


async def resolve_alert(alert_id: str):
    """Resolve um alerta"""
    if not alert_manager:
        return False
    
    for alert in alert_manager.active_alerts.values():
        if alert.id == alert_id:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            await alert_manager._save_alert(alert)
            return True
    
    return False 