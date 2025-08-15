#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 ALERT MANAGER - OMNİ KEYWORDS FINDER

Tracing ID: alert-manager-2025-01-27-001
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Script principal para gerenciamento de alertas automáticos
com integração PagerDuty, Slack, Email e políticas de escalação.
"""

import os
import sys
import json
import time
import logging
import requests
import smtplib
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import redis
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge
from prometheus_client.exposition import start_http_server

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler('/var/log/alert-manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuração de métricas Prometheus
registry = CollectorRegistry()
alert_counter = Counter('alert_manager_alerts_total', 'Total alerts processed', ['severity', 'team', 'component'], registry=registry)
alert_duration = Histogram('alert_manager_alert_duration_seconds', 'Alert resolution time', ['severity'], registry=registry)
active_alerts = Gauge('alert_manager_active_alerts', 'Number of active alerts', ['severity'], registry=registry)

@dataclass
class Alert:
    """Classe para representar um alerta"""
    id: str
    name: str
    severity: str
    team: str
    component: str
    description: str
    instance: str
    status: str  # firing, resolved
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    escalation_level: int = 0
    notification_count: int = 0
    last_notification: Optional[datetime] = None

@dataclass
class NotificationConfig:
    """Configuração de notificação"""
    type: str  # slack, email, pagerduty, webhook
    config: Dict[str, Any]
    enabled: bool = True
    retry_count: int = 3
    retry_delay: int = 30

class AlertManager:
    """Gerenciador principal de alertas"""
    
    def __init__(self, config_path: str = "infrastructure/monitoring/alerts.yaml"):
        """Inicializa o AlertManager"""
        self.config_path = config_path
        self.config = self._load_config()
        self.alerts: Dict[str, Alert] = {}
        self.notification_configs = self._setup_notifications()
        self.redis_client = self._setup_redis()
        self.escalation_policies = self._setup_escalation_policies()
        self.silence_rules = self._load_silence_rules()
        
        # Métricas
        self.start_metrics_server()
        
        logger.info("AlertManager inicializado com sucesso")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuração carregada de {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def _setup_redis(self) -> redis.Redis:
        """Configura conexão Redis para cache de alertas"""
        try:
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True
            )
            redis_client.ping()
            logger.info("Conexão Redis estabelecida")
            return redis_client
        except Exception as e:
            logger.warning(f"Redis não disponível: {e}")
            return None
    
    def _setup_notifications(self) -> Dict[str, NotificationConfig]:
        """Configura notificações baseadas na configuração"""
        notifications = {}
        
        # Slack
        if 'slack_api_url' in self.config.get('global', {}):
            notifications['slack'] = NotificationConfig(
                type='slack',
                config={
                    'webhook_url': self.config['global']['slack_api_url'],
                    'default_channel': '#alerts'
                }
            )
        
        # PagerDuty
        if 'pagerduty_url' in self.config.get('global', {}):
            notifications['pagerduty'] = NotificationConfig(
                type='pagerduty',
                config={
                    'url': self.config['global']['pagerduty_url'],
                    'routing_key': os.getenv('PAGERDUTY_ROUTING_KEY', 'your-pagerduty-routing-key')
                }
            )
        
        # Email
        if 'smtp_smarthost' in self.config.get('global', {}):
            notifications['email'] = NotificationConfig(
                type='email',
                config={
                    'smtp_host': self.config['global']['smtp_smarthost'].split(':')[0],
                    'smtp_port': int(self.config['global']['smtp_smarthost'].split(':')[1]),
                    'username': self.config['global']['smtp_auth_username'],
                    'password': self.config['global']['smtp_auth_password'],
                    'from_email': self.config['global']['smtp_from']
                }
            )
        
        logger.info(f"Configuradas {len(notifications)} notificações")
        return notifications
    
    def _setup_escalation_policies(self) -> Dict[str, List[Dict]]:
        """Configura políticas de escalação"""
        policies = {
            'critical': [
                {'delay': 5, 'receiver': 'pagerduty-critical'},
                {'delay': 15, 'receiver': 'email-critical'},
                {'delay': 30, 'receiver': 'slack-notifications'}
            ],
            'warning': [
                {'delay': 10, 'receiver': 'slack-warnings'},
                {'delay': 30, 'receiver': 'email-critical'}
            ]
        }
        return policies
    
    def _load_silence_rules(self) -> List[Dict]:
        """Carrega regras de silêncio"""
        return self.config.get('silence_rules', [])
    
    def start_metrics_server(self, port: int = 9093):
        """Inicia servidor de métricas Prometheus"""
        try:
            start_http_server(port, registry=registry)
            logger.info(f"Servidor de métricas iniciado na porta {port}")
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor de métricas: {e}")
    
    def process_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """Processa um novo alerta"""
        alert_id = alert_data.get('id', f"alert_{int(time.time())}")
        
        # Verifica se deve ser silenciado
        if self._should_silence(alert_data):
            logger.info(f"Alerta {alert_id} silenciado")
            return None
        
        # Cria objeto Alert
        alert = Alert(
            id=alert_id,
            name=alert_data.get('name', 'Unknown'),
            severity=alert_data.get('severity', 'info'),
            team=alert_data.get('team', 'unknown'),
            component=alert_data.get('component', 'unknown'),
            description=alert_data.get('description', ''),
            instance=alert_data.get('instance', 'unknown'),
            status='firing',
            created_at=datetime.now()
        )
        
        # Armazena alerta
        self.alerts[alert_id] = alert
        
        # Atualiza métricas
        alert_counter.labels(
            severity=alert.severity,
            team=alert.team,
            component=alert.component
        ).inc()
        active_alerts.labels(severity=alert.severity).inc()
        
        # Cache no Redis
        if self.redis_client:
            self.redis_client.setex(
                f"alert:{alert_id}",
                3600,  # 1 hora
                json.dumps(asdict(alert), default=str)
            )
        
        logger.info(f"Alerta processado: {alert_id} - {alert.name}")
        return alert
    
    def _should_silence(self, alert_data: Dict[str, Any]) -> bool:
        """Verifica se alerta deve ser silenciado"""
        current_time = datetime.now()
        
        for rule in self.silence_rules:
            if self._matches_silence_rule(alert_data, rule, current_time):
                return True
        
        return False
    
    def _matches_silence_rule(self, alert_data: Dict[str, Any], rule: Dict, current_time: datetime) -> bool:
        """Verifica se alerta corresponde à regra de silêncio"""
        # Implementação simplificada - pode ser expandida
        return False
    
    def send_notification(self, alert: Alert, receiver: str) -> bool:
        """Envia notificação para o receiver especificado"""
        try:
            if receiver == 'slack-notifications':
                return self._send_slack_notification(alert, '#alerts')
            elif receiver == 'slack-warnings':
                return self._send_slack_notification(alert, '#alerts-warnings')
            elif receiver == 'pagerduty-critical':
                return self._send_pagerduty_notification(alert)
            elif receiver == 'email-critical':
                return self._send_email_notification(alert, 'oncall@omni-keywords.com')
            elif receiver == 'business-alerts':
                return self._send_email_notification(alert, 'business@omni-keywords.com')
            else:
                logger.warning(f"Receiver desconhecido: {receiver}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            return False
    
    def _send_slack_notification(self, alert: Alert, channel: str) -> bool:
        """Envia notificação para Slack"""
        if 'slack' not in self.notification_configs:
            return False
        
        config = self.notification_configs['slack']
        
        message = {
            "channel": channel,
            "text": f"🚨 *{alert.name}*",
            "attachments": [{
                "color": "danger" if alert.severity == "critical" else "warning",
                "fields": [
                    {"title": "Severity", "value": alert.severity, "short": True},
                    {"title": "Team", "value": alert.team, "short": True},
                    {"title": "Component", "value": alert.component, "short": True},
                    {"title": "Description", "value": alert.description, "short": False}
                ],
                "footer": f"AlertManager • {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}"
            }]
        }
        
        try:
            response = requests.post(
                config.config['webhook_url'],
                json=message,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Notificação Slack enviada para {channel}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Slack: {e}")
            return False
    
    def _send_pagerduty_notification(self, alert: Alert) -> bool:
        """Envia notificação para PagerDuty"""
        if 'pagerduty' not in self.notification_configs:
            return False
        
        config = self.notification_configs['pagerduty']
        
        payload = {
            "routing_key": config.config['routing_key'],
            "event_action": "trigger",
            "payload": {
                "summary": f"{alert.name} - {alert.description}",
                "severity": alert.severity,
                "source": alert.instance,
                "custom_details": {
                    "team": alert.team,
                    "component": alert.component,
                    "alert_id": alert.id
                }
            }
        }
        
        try:
            response = requests.post(
                config.config['url'],
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info("Notificação PagerDuty enviada")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar notificação PagerDuty: {e}")
            return False
    
    def _send_email_notification(self, alert: Alert, to_email: str) -> bool:
        """Envia notificação por email"""
        if 'email' not in self.notification_configs:
            return False
        
        config = self.notification_configs['email']
        
        msg = MIMEMultipart()
        msg['From'] = config.config['from_email']
        msg['To'] = to_email
        msg['Subject'] = f"🚨 {alert.severity.upper()}: {alert.name}"
        
        body = f"""
        <h2>🚨 Alerta: {alert.name}</h2>
        <p><strong>Severity:</strong> {alert.severity}</p>
        <p><strong>Team:</strong> {alert.team}</p>
        <p><strong>Component:</strong> {alert.component}</p>
        <p><strong>Instance:</strong> {alert.instance}</p>
        <p><strong>Description:</strong> {alert.description}</p>
        <p><strong>Created:</strong> {alert.created_at.strftime('%Y-%m-%data %H:%M:%S')}</p>
        <hr>
        <p><em>Enviado por AlertManager - Omni Keywords Finder</em></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        try:
            server = smtplib.SMTP(config.config['smtp_host'], config.config['smtp_port'])
            server.starttls()
            server.login(config.config['username'], config.config['password'])
            server.send_message(msg)
            server.quit()
            logger.info(f"Email enviado para {to_email}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str = None) -> bool:
        """Resolve um alerta"""
        if alert_id not in self.alerts:
            logger.warning(f"Alerta {alert_id} não encontrado")
            return False
        
        alert = self.alerts[alert_id]
        alert.status = 'resolved'
        alert.resolved_at = datetime.now()
        alert.acknowledged_by = resolved_by
        
        # Atualiza métricas
        active_alerts.labels(severity=alert.severity).dec()
        
        # Remove do cache Redis
        if self.redis_client:
            self.redis_client.delete(f"alert:{alert_id}")
        
        logger.info(f"Alerta {alert_id} resolvido por {resolved_by}")
        return True
    
    def check_escalation(self):
        """Verifica e executa escalações necessárias"""
        current_time = datetime.now()
        
        for alert_id, alert in self.alerts.items():
            if alert.status != 'firing':
                continue
            
            # Verifica se precisa escalar
            escalation_policy = self.escalation_policies.get(alert.severity, [])
            
            for escalation in escalation_policy:
                delay_minutes = escalation['delay']
                receiver = escalation['receiver']
                
                # Verifica se já passou tempo suficiente
                time_since_creation = (current_time - alert.created_at).total_seconds() / 60
                
                if (time_since_creation >= delay_minutes and 
                    alert.escalation_level < len(escalation_policy)):
                    
                    # Envia notificação de escalação
                    if self.send_notification(alert, receiver):
                        alert.escalation_level += 1
                        alert.last_notification = current_time
                        logger.info(f"Escalação executada para alerta {alert_id}: {receiver}")
    
    def cleanup_old_alerts(self, max_age_hours: int = 24):
        """Remove alertas antigos"""
        current_time = datetime.now()
        alerts_to_remove = []
        
        for alert_id, alert in self.alerts.items():
            age_hours = (current_time - alert.created_at).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
            if self.redis_client:
                self.redis_client.delete(f"alert:{alert_id}")
        
        if alerts_to_remove:
            logger.info(f"Removidos {len(alerts_to_remove)} alertas antigos")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos alertas"""
        stats = {
            'total_alerts': len(self.alerts),
            'active_alerts': len([a for a in self.alerts.values() if a.status == 'firing']),
            'resolved_alerts': len([a for a in self.alerts.values() if a.status == 'resolved']),
            'by_severity': {},
            'by_team': {},
            'by_component': {}
        }
        
        for alert in self.alerts.values():
            # Por severidade
            stats['by_severity'][alert.severity] = stats['by_severity'].get(alert.severity, 0) + 1
            
            # Por time
            stats['by_team'][alert.team] = stats['by_team'].get(alert.team, 0) + 1
            
            # Por componente
            stats['by_component'][alert.component] = stats['by_component'].get(alert.component, 0) + 1
        
        return stats
    
    def run_scheduled_tasks(self):
        """Executa tarefas agendadas"""
        try:
            # Verifica escalações
            self.check_escalation()
            
            # Limpa alertas antigos
            self.cleanup_old_alerts()
            
            # Log de estatísticas
            stats = self.get_alert_statistics()
            logger.info(f"Estatísticas: {stats}")
            
        except Exception as e:
            logger.error(f"Erro nas tarefas agendadas: {e}")
    
    def start(self):
        """Inicia o AlertManager"""
        logger.info("AlertManager iniciado")
        
        # Agenda tarefas
        schedule.every(1).minutes.do(self.check_escalation)
        schedule.every(1).hours.do(self.cleanup_old_alerts)
        schedule.every(5).minutes.do(self.run_scheduled_tasks)
        
        # Loop principal
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
            except KeyboardInterrupt:
                logger.info("AlertManager interrompido")
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(60)

def main():
    """Função principal"""
    try:
        alert_manager = AlertManager()
        alert_manager.start()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 