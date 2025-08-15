"""
Sistema de Alertas em Tempo Real - Omni Keywords Finder
Alertas automáticos para eventos críticos e anomalias

Prompt: Implementação de sistema de alertas em tempo real
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import smtplib
import requests
import asyncio
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Níveis de severidade de alerta"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Tipos de alerta"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    ERROR = "error"
    BUSINESS = "business"
    SYSTEM = "system"

@dataclass
class AlertRule:
    """Regra de alerta"""
    id: str
    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    conditions: Dict[str, Any]
    enabled: bool = True
    cooldown_minutes: int = 5
    channels: List[str] = None
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = ['email']

@dataclass
class AlertEvent:
    """Evento de alerta"""
    id: str
    rule_id: str
    timestamp: datetime
    severity: AlertSeverity
    alert_type: AlertType
    message: str
    details: Dict[str, Any]
    source: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    request_id: Optional[str] = None

class NotificationChannel:
    """Canal de notificação base"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unknown')
    
    def send(self, alert: AlertEvent) -> bool:
        """Envia notificação"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Verifica se canal está disponível"""
        return True

class EmailChannel(NotificationChannel):
    """Canal de notificação por email"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = config.get('smtp_server', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email')
        self.to_emails = config.get('to_emails', [])
        self.use_tls = config.get('use_tls', True)
    
    def send(self, alert: AlertEvent) -> bool:
        """Envia alerta por email"""
        try:
            # Criar mensagem
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[ALERTA {alert.severity.value.upper()}] {alert.alert_type.value.title()}"
            
            # Corpo da mensagem
            body = self._create_email_body(alert)
            msg.attach(MimeText(body, 'html'))
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg)
            
            logger.info(f"Alerta enviado por email: {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta por email: {str(e)}")
            return False
    
    def _create_email_body(self, alert: AlertEvent) -> str:
        """Cria corpo do email"""
        severity_colors = {
            AlertSeverity.LOW: '#28a745',
            AlertSeverity.MEDIUM: '#ffc107',
            AlertSeverity.HIGH: '#fd7e14',
            AlertSeverity.CRITICAL: '#dc3545'
        }
        
        color = severity_colors.get(alert.severity, '#6c757d')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert {{ border: 2px solid {color}; padding: 15px; margin: 10px 0; }}
                .header {{ background-color: {color}; color: white; padding: 10px; }}
                .details {{ margin-top: 15px; }}
                .detail-row {{ margin: 5px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <div class="header">
                    <h2>🚨 Alerta de Segurança</h2>
                </div>
                <div class="details">
                    <div class="detail-row">
                        <span class="label">Tipo:</span> {alert.alert_type.value.title()}
                    </div>
                    <div class="detail-row">
                        <span class="label">Severidade:</span> {alert.severity.value.upper()}
                    </div>
                    <div class="detail-row">
                        <span class="label">Data/Hora:</span> {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S UTC')}
                    </div>
                    <div class="detail-row">
                        <span class="label">Mensagem:</span> {alert.message}
                    </div>
                    <div class="detail-row">
                        <span class="label">Fonte:</span> {alert.source}
                    </div>
                    {f'<div class="detail-row"><span class="label">Usuário:</span> {alert.user_id}</div>' if alert.user_id else ''}
                    {f'<div class="detail-row"><span class="label">IP:</span> {alert.ip_address}</div>' if alert.ip_address else ''}
                    {f'<div class="detail-row"><span class="label">Request ID:</span> {alert.request_id}</div>' if alert.request_id else ''}
                </div>
                <div class="details">
                    <h3>Detalhes Técnicos:</h3>
                    <pre>{json.dumps(alert.details, indent=2, ensure_ascii=False)}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

class SlackChannel(NotificationChannel):
    """Canal de notificação por Slack"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url')
        self.channel = config.get('channel', '#alerts')
        self.username = config.get('username', 'Omni Keywords Finder')
    
    def send(self, alert: AlertEvent) -> bool:
        """Envia alerta para Slack"""
        try:
            # Criar payload do Slack
            payload = self._create_slack_payload(alert)
            
            # Enviar para webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Alerta enviado para Slack: {alert.id}")
                return True
            else:
                logger.error(f"Erro ao enviar para Slack: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar alerta para Slack: {str(e)}")
            return False
    
    def _create_slack_payload(self, alert: AlertEvent) -> Dict[str, Any]:
        """Cria payload para Slack"""
        severity_colors = {
            AlertSeverity.LOW: '#28a745',
            AlertSeverity.MEDIUM: '#ffc107',
            AlertSeverity.HIGH: '#fd7e14',
            AlertSeverity.CRITICAL: '#dc3545'
        }
        
        color = severity_colors.get(alert.severity, '#6c757d')
        
        # Criar campos
        fields = [
            {
                "title": "Tipo",
                "value": alert.alert_type.value.title(),
                "short": True
            },
            {
                "title": "Severidade",
                "value": alert.severity.value.upper(),
                "short": True
            },
            {
                "title": "Fonte",
                "value": alert.source,
                "short": True
            }
        ]
        
        if alert.user_id:
            fields.append({
                "title": "Usuário",
                "value": alert.user_id,
                "short": True
            })
        
        if alert.ip_address:
            fields.append({
                "title": "IP",
                "value": alert.ip_address,
                "short": True
            })
        
        return {
            "channel": self.channel,
            "username": self.username,
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 Alerta de Segurança - {alert.alert_type.value.title()}",
                    "text": alert.message,
                    "fields": fields,
                    "footer": f"Omni Keywords Finder • {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S UTC')}",
                    "ts": int(alert.timestamp.timestamp())
                }
            ]
        }

class AlertSystem:
    """Sistema de alertas em tempo real"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = self._load_alert_rules()
        self.channels = self._setup_channels()
        self.alert_history = []
        self.cooldowns = {}  # rule_id -> last_alert_time
        self.enabled = config.get('enabled', True)
        
        # Thread para processamento assíncrono
        self.alert_queue = asyncio.Queue()
        self.processing_thread = None
        self.start_processing()
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Carrega regras de alerta"""
        default_rules = [
            AlertRule(
                id="security_unauthorized_access",
                name="Acesso Não Autorizado",
                description="Detecta tentativas de acesso não autorizado",
                alert_type=AlertType.SECURITY,
                severity=AlertSeverity.HIGH,
                conditions={
                    "event_type": "unauthorized_access",
                    "threshold": 3,  # 3 tentativas em 5 minutos
                    "time_window": 300
                },
                cooldown_minutes=10
            ),
            AlertRule(
                id="security_suspicious_activity",
                name="Atividade Suspeita",
                description="Detecta atividades suspeitas do usuário",
                alert_type=AlertType.SECURITY,
                severity=AlertSeverity.MEDIUM,
                conditions={
                    "event_type": "suspicious_activity",
                    "threshold": 1
                },
                cooldown_minutes=5
            ),
            AlertRule(
                id="performance_high_error_rate",
                name="Taxa de Erro Alta",
                description="Detecta alta taxa de erros no sistema",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.HIGH,
                conditions={
                    "error_rate_threshold": 0.1,  # 10% de erro
                    "time_window": 300
                },
                cooldown_minutes=15
            ),
            AlertRule(
                id="business_payment_failure",
                name="Falha em Pagamento",
                description="Detecta falhas em transações de pagamento",
                alert_type=AlertType.BUSINESS,
                severity=AlertSeverity.CRITICAL,
                conditions={
                    "event_type": "payment_failed",
                    "threshold": 1
                },
                cooldown_minutes=5
            ),
            AlertRule(
                id="system_database_error",
                name="Erro de Banco de Dados",
                description="Detecta erros críticos de banco de dados",
                alert_type=AlertType.SYSTEM,
                severity=AlertSeverity.CRITICAL,
                conditions={
                    "event_type": "database_error",
                    "threshold": 1
                },
                cooldown_minutes=5
            )
        ]
        
        # Carregar regras customizadas do config
        custom_rules = self.config.get('alert_rules', [])
        for rule_config in custom_rules:
            default_rules.append(AlertRule(**rule_config))
        
        return default_rules
    
    def _setup_channels(self) -> Dict[str, NotificationChannel]:
        """Configura canais de notificação"""
        channels = {}
        
        # Email
        email_config = self.config.get('email', {})
        if email_config.get('enabled', False):
            channels['email'] = EmailChannel(email_config)
        
        # Slack
        slack_config = self.config.get('slack', {})
        if slack_config.get('enabled', False):
            channels['slack'] = SlackChannel(slack_config)
        
        return channels
    
    def start_processing(self):
        """Inicia thread de processamento de alertas"""
        if self.processing_thread is None:
            self.processing_thread = threading.Thread(
                target=self._process_alerts_loop,
                daemon=True
            )
            self.processing_thread.start()
    
    def _process_alerts_loop(self):
        """Loop de processamento de alertas"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._alert_processor())
        except Exception as e:
            logger.error(f"Erro no processamento de alertas: {str(e)}")
        finally:
            loop.close()
    
    async def _alert_processor(self):
        """Processador de alertas assíncrono"""
        while True:
            try:
                # Processar alerta da fila
                alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)
                await self._process_alert(alert)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erro ao processar alerta: {str(e)}")
    
    async def _process_alert(self, alert: AlertEvent):
        """Processa um alerta individual"""
        try:
            # Verificar cooldown
            if not self._should_send_alert(alert.rule_id):
                logger.info(f"Alerta em cooldown: {alert.rule_id}")
                return
            
            # Enviar para todos os canais configurados
            rule = self._get_rule(alert.rule_id)
            if not rule:
                return
            
            success_count = 0
            for channel_name in rule.channels:
                if channel_name in self.channels:
                    channel = self.channels[channel_name]
                    if channel.send(alert):
                        success_count += 1
            
            # Atualizar cooldown
            if success_count > 0:
                self.cooldowns[alert.rule_id] = datetime.now(timezone.utc)
                self.alert_history.append(alert)
                
                # Manter apenas últimos 1000 alertas
                if len(self.alert_history) > 1000:
                    self.alert_history = self.alert_history[-1000:]
            
            logger.info(f"Alerta processado: {alert.id} - {success_count} canais")
            
        except Exception as e:
            logger.error(f"Erro ao processar alerta {alert.id}: {str(e)}")
    
    def check_event(self, event_data: Dict[str, Any]) -> Optional[AlertEvent]:
        """Verifica se evento deve gerar alerta"""
        if not self.enabled:
            return None
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._matches_rule(event_data, rule):
                alert = self._create_alert(rule, event_data)
                if alert:
                    # Adicionar à fila de processamento
                    asyncio.create_task(self.alert_queue.put(alert))
                    return alert
        
        return None
    
    def _matches_rule(self, event_data: Dict[str, Any], rule: AlertRule) -> bool:
        """Verifica se evento corresponde à regra"""
        conditions = rule.conditions
        
        # Verificar tipo de evento
        if 'event_type' in conditions:
            if event_data.get('event_type') != conditions['event_type']:
                return False
        
        # Verificar threshold
        if 'threshold' in conditions:
            threshold = conditions['threshold']
            time_window = conditions.get('time_window', 300)
            
            # Contar eventos similares na janela de tempo
            count = self._count_similar_events(
                event_data, 
                time_window
            )
            
            if count < threshold:
                return False
        
        # Verificar taxa de erro
        if 'error_rate_threshold' in conditions:
            error_rate = self._calculate_error_rate(
                conditions.get('time_window', 300)
            )
            
            if error_rate < conditions['error_rate_threshold']:
                return False
        
        return True
    
    def _count_similar_events(self, event_data: Dict[str, Any], time_window: int) -> int:
        """Conta eventos similares na janela de tempo"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=time_window)
        
        count = 0
        for alert in self.alert_history:
            if alert.timestamp < cutoff_time:
                continue
            
            # Verificar se é similar (mesmo tipo, usuário, IP)
            if (alert.alert_type.value == event_data.get('event_type') and
                alert.user_id == event_data.get('user_id') and
                alert.ip_address == event_data.get('ip_address')):
                count += 1
        
        return count
    
    def _calculate_error_rate(self, time_window: int) -> float:
        """Calcula taxa de erro na janela de tempo"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=time_window)
        
        total_events = 0
        error_events = 0
        
        for alert in self.alert_history:
            if alert.timestamp < cutoff_time:
                continue
            
            total_events += 1
            if alert.alert_type == AlertType.ERROR:
                error_events += 1
        
        return error_events / total_events if total_events > 0 else 0.0
    
    def _create_alert(self, rule: AlertRule, event_data: Dict[str, Any]) -> Optional[AlertEvent]:
        """Cria evento de alerta"""
        try:
            import uuid
            
            alert = AlertEvent(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                timestamp=datetime.now(timezone.utc),
                severity=rule.severity,
                alert_type=rule.alert_type,
                message=self._create_alert_message(rule, event_data),
                details=event_data,
                source=event_data.get('source', 'unknown'),
                user_id=event_data.get('user_id'),
                ip_address=event_data.get('ip_address'),
                request_id=event_data.get('request_id')
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {str(e)}")
            return None
    
    def _create_alert_message(self, rule: AlertRule, event_data: Dict[str, Any]) -> str:
        """Cria mensagem do alerta"""
        messages = {
            "security_unauthorized_access": "Detectadas múltiplas tentativas de acesso não autorizado",
            "security_suspicious_activity": "Atividade suspeita detectada no sistema",
            "performance_high_error_rate": "Taxa de erro alta detectada no sistema",
            "business_payment_failure": "Falha em transação de pagamento detectada",
            "system_database_error": "Erro crítico de banco de dados detectado"
        }
        
        return messages.get(rule.id, f"Alerta: {rule.name}")
    
    def _should_send_alert(self, rule_id: str) -> bool:
        """Verifica se deve enviar alerta (cooldown)"""
        if rule_id not in self.cooldowns:
            return True
        
        rule = self._get_rule(rule_id)
        if not rule:
            return True
        
        last_alert = self.cooldowns[rule_id]
        cooldown_duration = timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now(timezone.utc) - last_alert > cooldown_duration
    
    def _get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Obtém regra por ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def get_alert_history(self, limit: int = 100) -> List[AlertEvent]:
        """Obtém histórico de alertas"""
        return self.alert_history[-limit:]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de alertas"""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        stats = {
            'total_alerts': len(self.alert_history),
            'alerts_24h': len([a for a in self.alert_history if a.timestamp > last_24h]),
            'alerts_7d': len([a for a in self.alert_history if a.timestamp > last_7d]),
            'by_severity': {},
            'by_type': {},
            'by_rule': {}
        }
        
        # Estatísticas por severidade
        for alert in self.alert_history:
            severity = alert.severity.value
            alert_type = alert.alert_type.value
            rule_id = alert.rule_id
            
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            stats['by_type'][alert_type] = stats['by_type'].get(alert_type, 0) + 1
            stats['by_rule'][rule_id] = stats['by_rule'].get(rule_id, 0) + 1
        
        return stats
    
    def disable_rule(self, rule_id: str):
        """Desabilita regra de alerta"""
        rule = self._get_rule(rule_id)
        if rule:
            rule.enabled = False
            logger.info(f"Regra de alerta desabilitada: {rule_id}")
    
    def enable_rule(self, rule_id: str):
        """Habilita regra de alerta"""
        rule = self._get_rule(rule_id)
        if rule:
            rule.enabled = True
            logger.info(f"Regra de alerta habilitada: {rule_id}")
    
    def add_rule(self, rule: AlertRule):
        """Adiciona nova regra de alerta"""
        self.rules.append(rule)
        logger.info(f"Nova regra de alerta adicionada: {rule.id}")
    
    def remove_rule(self, rule_id: str):
        """Remove regra de alerta"""
        self.rules = [r for r in self.rules if r.id != rule_id]
        logger.info(f"Regra de alerta removida: {rule_id}")

# Instância global
alert_system = None

def init_alert_system(config: Dict[str, Any]):
    """Inicializa sistema de alertas global"""
    global alert_system
    alert_system = AlertSystem(config)
    return alert_system

def get_alert_system() -> AlertSystem:
    """Obtém instância do sistema de alertas"""
    return alert_system 