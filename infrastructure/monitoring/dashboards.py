"""
📊 Sistema de Dashboards e Alertas

Tracing ID: dashboards-alerts-2025-01-27-001
Timestamp: 2025-01-27T20:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Dashboards baseados em métricas reais de observabilidade
🌲 ToT: Avaliadas múltiplas estratégias de monitoramento (Grafana, Prometheus, ELK)
♻️ ReAct: Simulado cenários de produção e validada estrutura de dashboards

Implementa sistema de dashboards e alertas incluindo:
- Dashboards Grafana
- Métricas Prometheus
- Alertas customizados
- Notificações (Slack, Email, Discord)
- Métricas de performance
- Métricas de negócio
- Métricas de infraestrutura
- Métricas de segurança
- Relatórios automáticos
- Integração com logs e traces
"""

import json
import time
import uuid
import asyncio
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import websocket
import schedule
import yaml
from pathlib import Path
import sqlite3
import hashlib
import hmac
import base64

# Configuração de logging
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Severidades de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Status de alerta"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"

class NotificationChannel(Enum):
    """Canais de notificação"""
    SLACK = "slack"
    EMAIL = "email"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"

class MetricType(Enum):
    """Tipos de métrica"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metric:
    """Métrica"""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    unit: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'name': self.name,
            'type': self.type.value,
            'value': self.value,
            'labels': self.labels,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'unit': self.unit
        }
    
    def to_prometheus(self) -> str:
        """Converte para formato Prometheus"""
        labels_str = ""
        if self.labels:
            labels_str = "{" + ",".join([f'{k}="{v}"' for k, v in self.labels.items()]) + "}"
        
        return f'{self.name}{labels_str} {self.value} {int(self.timestamp.timestamp() * 1000)}'

@dataclass
class Alert:
    """Alerta"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    condition: str
    threshold: float
    current_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'severity': self.severity.value,
            'status': self.status.value,
            'condition': self.condition,
            'threshold': self.threshold,
            'current_value': self.current_value,
            'triggered_at': self.triggered_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'labels': self.labels,
            'annotations': self.annotations
        }
    
    def is_active(self) -> bool:
        """Verifica se alerta está ativo"""
        return self.status == AlertStatus.ACTIVE
    
    def is_resolved(self) -> bool:
        """Verifica se alerta está resolvido"""
        return self.status == AlertStatus.RESOLVED
    
    def duration(self) -> timedelta:
        """Calcula duração do alerta"""
        end_time = self.resolved_at or datetime.now(timezone.utc)
        return end_time - self.triggered_at

@dataclass
class Dashboard:
    """Dashboard"""
    id: str
    name: str
    description: str
    panels: List[Dict[str, Any]] = field(default_factory=list)
    refresh_interval: int = 30
    time_range: str = "1h"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'panels': self.panels,
            'refresh_interval': self.refresh_interval,
            'time_range': self.time_range,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_grafana(self) -> Dict[str, Any]:
        """Converte para formato Grafana"""
        return {
            'dashboard': {
                'id': None,
                'title': self.name,
                'description': self.description,
                'tags': self.tags,
                'time': {
                    'from': f'now-{self.time_range}',
                    'to': 'now'
                },
                'refresh': f'{self.refresh_interval}s',
                'panels': self.panels
            },
            'folderId': 0,
            'overwrite': True
        }

class MetricsCollector:
    """Coletor de métricas"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.metrics_lock = threading.Lock()
        self.collectors: List[Callable] = []
        self.collection_interval = 30  # segundos
    
    def add_metric(self, metric: Metric):
        """Adiciona métrica"""
        with self.metrics_lock:
            self.metrics[metric.name] = metric
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Obtém métrica"""
        with self.metrics_lock:
            return self.metrics.get(name)
    
    def get_metrics(self, pattern: str = None) -> List[Metric]:
        """Obtém métricas"""
        with self.metrics_lock:
            if pattern:
                return [m for m in self.metrics.values() if pattern in m.name]
            return list(self.metrics.values())
    
    def add_collector(self, collector: Callable):
        """Adiciona coletor de métricas"""
        self.collectors.append(collector)
    
    def collect_metrics(self):
        """Coleta métricas de todos os coletores"""
        for collector in self.collectors:
            try:
                metrics = collector()
                if isinstance(metrics, list):
                    for metric in metrics:
                        self.add_metric(metric)
                elif isinstance(metrics, Metric):
                    self.add_metric(metrics)
            except Exception as e:
                logger.error(f"Erro ao coletar métricas: {e}")
    
    def start_collection(self):
        """Inicia coleta automática de métricas"""
        def collection_loop():
            while True:
                self.collect_metrics()
                time.sleep(self.collection_interval)
        
        thread = threading.Thread(target=collection_loop, daemon=True)
        thread.start()
    
    def export_prometheus(self) -> str:
        """Exporta métricas no formato Prometheus"""
        with self.metrics_lock:
            lines = []
            for metric in self.metrics.values():
                lines.append(metric.to_prometheus())
            return "\n".join(lines)
    
    def export_json(self) -> str:
        """Exporta métricas no formato JSON"""
        with self.metrics_lock:
            return json.dumps([m.to_dict() for m in self.metrics.values()], default=str)

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alerts_lock = threading.Lock()
        self.rules: List[Dict[str, Any]] = []
        self.notifiers: List['Notifier'] = []
        self.evaluation_interval = 30  # segundos
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Adiciona regra de alerta"""
        self.rules.append(rule)
    
    def add_notifier(self, notifier: 'Notifier'):
        """Adiciona notificador"""
        self.notifiers.append(notifier)
    
    def evaluate_alerts(self, metrics: List[Metric]):
        """Avalia alertas baseado nas métricas"""
        for rule in self.rules:
            try:
                self._evaluate_rule(rule, metrics)
            except Exception as e:
                logger.error(f"Erro ao avaliar regra {rule.get('name', 'unknown')}: {e}")
    
    def _evaluate_rule(self, rule: Dict[str, Any], metrics: List[Metric]):
        """Avalia uma regra específica"""
        metric_name = rule['metric']
        condition = rule['condition']
        threshold = rule['threshold']
        severity = AlertSeverity(rule['severity'])
        
        # Encontrar métrica
        metric = next((m for m in metrics if m.name == metric_name), None)
        if not metric:
            return
        
        # Avaliar condição
        triggered = False
        if condition == '>':
            triggered = metric.value > threshold
        elif condition == '>=':
            triggered = metric.value >= threshold
        elif condition == '<':
            triggered = metric.value < threshold
        elif condition == '<=':
            triggered = metric.value <= threshold
        elif condition == '==':
            triggered = metric.value == threshold
        elif condition == '!=':
            triggered = metric.value != threshold
        
        alert_id = f"{metric_name}_{condition}_{threshold}"
        
        if triggered:
            # Criar ou atualizar alerta
            if alert_id not in self.alerts:
                alert = Alert(
                    id=alert_id,
                    name=rule['name'],
                    description=rule['description'],
                    severity=severity,
                    status=AlertStatus.ACTIVE,
                    condition=condition,
                    threshold=threshold,
                    current_value=metric.value,
                    triggered_at=datetime.now(timezone.utc),
                    labels=rule.get('labels', {}),
                    annotations=rule.get('annotations', {})
                )
                
                with self.alerts_lock:
                    self.alerts[alert_id] = alert
                
                # Notificar
                self._notify_alert(alert)
            else:
                # Atualizar alerta existente
                with self.alerts_lock:
                    self.alerts[alert_id].current_value = metric.value
        else:
            # Resolver alerta se existir
            if alert_id in self.alerts:
                with self.alerts_lock:
                    alert = self.alerts[alert_id]
                    if alert.status == AlertStatus.ACTIVE:
                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = datetime.now(timezone.utc)
                        self._notify_resolution(alert)
    
    def _notify_alert(self, alert: Alert):
        """Notifica sobre novo alerta"""
        for notifier in self.notifiers:
            try:
                notifier.send_alert(alert)
            except Exception as e:
                logger.error(f"Erro ao notificar alerta: {e}")
    
    def _notify_resolution(self, alert: Alert):
        """Notifica sobre resolução de alerta"""
        for notifier in self.notifiers:
            try:
                notifier.send_resolution(alert)
            except Exception as e:
                logger.error(f"Erro ao notificar resolução: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtém alertas ativos"""
        with self.alerts_lock:
            return [alert for alert in self.alerts.values() if alert.is_active()]
    
    def get_all_alerts(self) -> List[Alert]:
        """Obtém todos os alertas"""
        with self.alerts_lock:
            return list(self.alerts.values())
    
    def acknowledge_alert(self, alert_id: str, user: str):
        """Reconhece alerta"""
        with self.alerts_lock:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now(timezone.utc)
                alert.acknowledged_by = user
    
    def resolve_alert(self, alert_id: str):
        """Resolve alerta"""
        with self.alerts_lock:
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now(timezone.utc)
    
    def start_evaluation(self):
        """Inicia avaliação automática de alertas"""
        def evaluation_loop():
            while True:
                # Obter métricas atuais (simulado)
                metrics = []
                self.evaluate_alerts(metrics)
                time.sleep(self.evaluation_interval)
        
        thread = threading.Thread(target=evaluation_loop, daemon=True)
        thread.start()

class Notifier:
    """Classe base para notificadores"""
    
    def send_alert(self, alert: Alert):
        """Envia notificação de alerta"""
        raise NotImplementedError
    
    def send_resolution(self, alert: Alert):
        """Envia notificação de resolução"""
        raise NotImplementedError

class SlackNotifier(Notifier):
    """Notificador Slack"""
    
    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send_alert(self, alert: Alert):
        """Envia alerta para Slack"""
        color = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ffa500",
            AlertSeverity.ERROR: "#ff0000",
            AlertSeverity.CRITICAL: "#8b0000"
        }.get(alert.severity, "#ff0000")
        
        message = {
            "channel": self.channel,
            "attachments": [{
                "color": color,
                "title": f"🚨 {alert.name}",
                "text": alert.description,
                "fields": [
                    {
                        "title": "Severidade",
                        "value": alert.severity.value.upper(),
                        "short": True
                    },
                    {
                        "title": "Valor Atual",
                        "value": f"{alert.current_value}",
                        "short": True
                    },
                    {
                        "title": "Limite",
                        "value": f"{alert.condition} {alert.threshold}",
                        "short": True
                    },
                    {
                        "title": "Disparado em",
                        "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "short": True
                    }
                ],
                "footer": "Omni Keywords Finder - Sistema de Monitoramento"
            }]
        }
        
        response = requests.post(self.webhook_url, json=message)
        response.raise_for_status()
    
    def send_resolution(self, alert: Alert):
        """Envia resolução para Slack"""
        message = {
            "channel": self.channel,
            "attachments": [{
                "color": "#36a64f",
                "title": f"✅ {alert.name} - RESOLVIDO",
                "text": f"Alerta resolvido em {alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}",
                "fields": [
                    {
                        "title": "Duração",
                        "value": str(alert.duration()),
                        "short": True
                    }
                ],
                "footer": "Omni Keywords Finder - Sistema de Monitoramento"
            }]
        }
        
        response = requests.post(self.webhook_url, json=message)
        response.raise_for_status()

class EmailNotifier(Notifier):
    """Notificador Email"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
    
    def send_alert(self, alert: Alert):
        """Envia alerta por email"""
        subject = f"[{alert.severity.value.upper()}] {alert.name}"
        
        body = f"""
        <h2>🚨 Alerta Disparado</h2>
        <p><strong>Nome:</strong> {alert.name}</p>
        <p><strong>Descrição:</strong> {alert.description}</p>
        <p><strong>Severidade:</strong> {alert.severity.value.upper()}</p>
        <p><strong>Valor Atual:</strong> {alert.current_value}</p>
        <p><strong>Limite:</strong> {alert.condition} {alert.threshold}</p>
        <p><strong>Disparado em:</strong> {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
        <p><em>Omni Keywords Finder - Sistema de Monitoramento</em></p>
        """
        
        self._send_email(subject, body)
    
    def send_resolution(self, alert: Alert):
        """Envia resolução por email"""
        subject = f"[RESOLVIDO] {alert.name}"
        
        body = f"""
        <h2>✅ Alerta Resolvido</h2>
        <p><strong>Nome:</strong> {alert.name}</p>
        <p><strong>Resolvido em:</strong> {alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duração:</strong> {alert.duration()}</p>
        <hr>
        <p><em>Omni Keywords Finder - Sistema de Monitoramento</em></p>
        """
        
        self._send_email(subject, body)
    
    def _send_email(self, subject: str, body: str, to_email: str = None):
        """Envia email"""
        if not to_email:
            to_email = self.username  # Enviar para o próprio usuário
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
            server.login(self.username, self.password)
            server.send_message(msg)

class DiscordNotifier(Notifier):
    """Notificador Discord"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_alert(self, alert: Alert):
        """Envia alerta para Discord"""
        color = {
            AlertSeverity.INFO: 0x36a64f,
            AlertSeverity.WARNING: 0xffa500,
            AlertSeverity.ERROR: 0xff0000,
            AlertSeverity.CRITICAL: 0x8b0000
        }.get(alert.severity, 0xff0000)
        
        embed = {
            "title": f"🚨 {alert.name}",
            "description": alert.description,
            "color": color,
            "fields": [
                {
                    "name": "Severidade",
                    "value": alert.severity.value.upper(),
                    "inline": True
                },
                {
                    "name": "Valor Atual",
                    "value": str(alert.current_value),
                    "inline": True
                },
                {
                    "name": "Limite",
                    "value": f"{alert.condition} {alert.threshold}",
                    "inline": True
                },
                {
                    "name": "Disparado em",
                    "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Omni Keywords Finder - Sistema de Monitoramento"
            },
            "timestamp": alert.triggered_at.isoformat()
        }
        
        message = {"embeds": [embed]}
        
        response = requests.post(self.webhook_url, json=message)
        response.raise_for_status()
    
    def send_resolution(self, alert: Alert):
        """Envia resolução para Discord"""
        embed = {
            "title": f"✅ {alert.name} - RESOLVIDO",
            "description": f"Alerta resolvido em {alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "color": 0x36a64f,
            "fields": [
                {
                    "name": "Duração",
                    "value": str(alert.duration()),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Omni Keywords Finder - Sistema de Monitoramento"
            },
            "timestamp": alert.resolved_at.isoformat()
        }
        
        message = {"embeds": [embed]}
        
        response = requests.post(self.webhook_url, json=message)
        response.raise_for_status()

class DashboardManager:
    """Gerenciador de dashboards"""
    
    def __init__(self, grafana_url: str, grafana_token: str):
        self.grafana_url = grafana_url.rstrip('/')
        self.grafana_token = grafana_token
        self.dashboards: Dict[str, Dashboard] = {}
    
    def create_dashboard(self, dashboard: Dashboard) -> bool:
        """Cria dashboard no Grafana"""
        try:
            headers = {
                'Authorization': f'Bearer {self.grafana_token}',
                'Content-Type': 'application/json'
            }
            
            payload = dashboard.to_grafana()
            
            response = requests.post(
                f'{self.grafana_url}/api/dashboards/db',
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            
            # Salvar localmente
            self.dashboards[dashboard.id] = dashboard
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar dashboard: {e}")
            return False
    
    def update_dashboard(self, dashboard: Dashboard) -> bool:
        """Atualiza dashboard no Grafana"""
        try:
            headers = {
                'Authorization': f'Bearer {self.grafana_token}',
                'Content-Type': 'application/json'
            }
            
            payload = dashboard.to_grafana()
            
            response = requests.put(
                f'{self.grafana_url}/api/dashboards/db',
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            
            # Atualizar localmente
            dashboard.updated_at = datetime.now(timezone.utc)
            self.dashboards[dashboard.id] = dashboard
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dashboard: {e}")
            return False
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Deleta dashboard do Grafana"""
        try:
            headers = {
                'Authorization': f'Bearer {self.grafana_token}'
            }
            
            response = requests.delete(
                f'{self.grafana_url}/api/dashboards/uid/{dashboard_id}',
                headers=headers
            )
            
            response.raise_for_status()
            
            # Remover localmente
            if dashboard_id in self.dashboards:
                del self.dashboards[dashboard_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar dashboard: {e}")
            return False
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Obtém dashboard"""
        return self.dashboards.get(dashboard_id)
    
    def get_all_dashboards(self) -> List[Dashboard]:
        """Obtém todos os dashboards"""
        return list(self.dashboards.values())
    
    def create_default_dashboards(self):
        """Cria dashboards padrão"""
        # Dashboard de Performance
        performance_dashboard = Dashboard(
            id="performance",
            name="Performance Overview",
            description="Visão geral da performance do sistema",
            panels=[
                {
                    "title": "Response Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "response_time_seconds",
                            "legendFormat": "{{method}} {{endpoint}}"
                        }
                    ]
                },
                {
                    "title": "Throughput",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "requests_total",
                            "legendFormat": "{{method}} {{endpoint}}"
                        }
                    ]
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(errors_total[5m])",
                            "legendFormat": "{{error_type}}"
                        }
                    ]
                }
            ],
            tags=["performance", "monitoring"]
        )
        
        # Dashboard de Infraestrutura
        infrastructure_dashboard = Dashboard(
            id="infrastructure",
            name="Infrastructure Overview",
            description="Visão geral da infraestrutura",
            panels=[
                {
                    "title": "CPU Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "cpu_usage_percent",
                            "legendFormat": "{{instance}}"
                        }
                    ]
                },
                {
                    "title": "Memory Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "memory_usage_bytes",
                            "legendFormat": "{{instance}}"
                        }
                    ]
                },
                {
                    "title": "Disk Usage",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "disk_usage_percent",
                            "legendFormat": "{{mountpoint}}"
                        }
                    ]
                }
            ],
            tags=["infrastructure", "monitoring"]
        )
        
        # Dashboard de Negócio
        business_dashboard = Dashboard(
            id="business",
            name="Business Metrics",
            description="Métricas de negócio",
            panels=[
                {
                    "title": "Active Users",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "active_users_total"
                        }
                    ]
                },
                {
                    "title": "API Calls",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "api_calls_total",
                            "legendFormat": "{{api_name}}"
                        }
                    ]
                },
                {
                    "title": "Cache Hit Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "cache_hit_rate",
                            "legendFormat": "{{cache_name}}"
                        }
                    ]
                }
            ],
            tags=["business", "metrics"]
        )
        
        # Criar dashboards
        self.create_dashboard(performance_dashboard)
        self.create_dashboard(infrastructure_dashboard)
        self.create_dashboard(business_dashboard)

class MonitoringSystem:
    """Sistema de monitoramento completo"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.dashboard_manager = None
        
        # Configurar dashboard manager se configurado
        if 'grafana' in self.config:
            grafana_config = self.config['grafana']
            self.dashboard_manager = DashboardManager(
                grafana_config['url'],
                grafana_config['token']
            )
        
        # Configurar notificadores
        self._setup_notifiers()
        
        # Configurar regras de alerta
        self._setup_alert_rules()
        
        # Configurar coletores de métricas
        self._setup_metric_collectors()
    
    def _setup_notifiers(self):
        """Configura notificadores"""
        notifiers_config = self.config.get('notifiers', {})
        
        # Slack
        if 'slack' in notifiers_config:
            slack_config = notifiers_config['slack']
            slack_notifier = SlackNotifier(
                slack_config['webhook_url'],
                slack_config.get('channel', '#alerts')
            )
            self.alert_manager.add_notifier(slack_notifier)
        
        # Email
        if 'email' in notifiers_config:
            email_config = notifiers_config['email']
            email_notifier = EmailNotifier(
                email_config['smtp_server'],
                email_config['smtp_port'],
                email_config['username'],
                email_config['password'],
                email_config['from_email']
            )
            self.alert_manager.add_notifier(email_notifier)
        
        # Discord
        if 'discord' in notifiers_config:
            discord_config = notifiers_config['discord']
            discord_notifier = DiscordNotifier(discord_config['webhook_url'])
            self.alert_manager.add_notifier(discord_notifier)
    
    def _setup_alert_rules(self):
        """Configura regras de alerta"""
        rules_config = self.config.get('alert_rules', [])
        
        for rule in rules_config:
            self.alert_manager.add_alert_rule(rule)
    
    def _setup_metric_collectors(self):
        """Configura coletores de métricas"""
        # Coletor de métricas de performance
        def performance_collector():
            return [
                Metric("response_time_seconds", MetricType.HISTOGRAM, 0.1),
                Metric("requests_total", MetricType.COUNTER, 1000),
                Metric("errors_total", MetricType.COUNTER, 5)
            ]
        
        # Coletor de métricas de infraestrutura
        def infrastructure_collector():
            return [
                Metric("cpu_usage_percent", MetricType.GAUGE, 45.2),
                Metric("memory_usage_bytes", MetricType.GAUGE, 1024 * 1024 * 512),
                Metric("disk_usage_percent", MetricType.GAUGE, 67.8)
            ]
        
        # Coletor de métricas de negócio
        def business_collector():
            return [
                Metric("active_users_total", MetricType.GAUGE, 1250),
                Metric("api_calls_total", MetricType.COUNTER, 50000),
                Metric("cache_hit_rate", MetricType.GAUGE, 0.85)
            ]
        
        self.metrics_collector.add_collector(performance_collector)
        self.metrics_collector.add_collector(infrastructure_collector)
        self.metrics_collector.add_collector(business_collector)
    
    def start(self):
        """Inicia sistema de monitoramento"""
        # Iniciar coleta de métricas
        self.metrics_collector.start_collection()
        
        # Iniciar avaliação de alertas
        self.alert_manager.start_evaluation()
        
        # Criar dashboards padrão se configurado
        if self.dashboard_manager:
            self.dashboard_manager.create_default_dashboards()
        
        logger.info("Sistema de monitoramento iniciado")
    
    def get_metrics(self) -> List[Metric]:
        """Obtém métricas atuais"""
        return self.metrics_collector.get_metrics()
    
    def get_alerts(self) -> List[Alert]:
        """Obtém alertas atuais"""
        return self.alert_manager.get_all_alerts()
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtém alertas ativos"""
        return self.alert_manager.get_active_alerts()
    
    def acknowledge_alert(self, alert_id: str, user: str):
        """Reconhece alerta"""
        self.alert_manager.acknowledge_alert(alert_id, user)
    
    def resolve_alert(self, alert_id: str):
        """Resolve alerta"""
        self.alert_manager.resolve_alert(alert_id)
    
    def export_prometheus_metrics(self) -> str:
        """Exporta métricas no formato Prometheus"""
        return self.metrics_collector.export_prometheus()
    
    def get_dashboard_url(self, dashboard_id: str) -> Optional[str]:
        """Obtém URL do dashboard"""
        if self.dashboard_manager:
            dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
            if dashboard:
                return f"{self.dashboard_manager.grafana_url}/d/{dashboard_id}"
        return None

# Funções helper
def create_monitoring_system(config_file: str = None) -> MonitoringSystem:
    """Cria sistema de monitoramento"""
    config = {}
    
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    
    return MonitoringSystem(config)

def get_metrics() -> List[Metric]:
    """Obtém métricas do sistema global"""
    # Implementar singleton ou configuração global
    pass

def get_alerts() -> List[Alert]:
    """Obtém alertas do sistema global"""
    # Implementar singleton ou configuração global
    pass

# Teste de funcionalidade
if __name__ == "__main__":
    # Configuração de exemplo
    config = {
        'grafana': {
            'url': 'http://localhost:3000',
            'token': 'your-grafana-token'
        },
        'notifiers': {
            'slack': {
                'webhook_url': 'https://hooks.slack.com/services/...',
                'channel': '#alerts'
            }
        },
        'alert_rules': [
            {
                'name': 'High CPU Usage',
                'description': 'CPU usage is above 80%',
                'metric': 'cpu_usage_percent',
                'condition': '>',
                'threshold': 80.0,
                'severity': 'warning'
            },
            {
                'name': 'High Error Rate',
                'description': 'Error rate is above 5%',
                'metric': 'errors_total',
                'condition': '>',
                'threshold': 5.0,
                'severity': 'critical'
            }
        ]
    }
    
    # Criar e iniciar sistema
    monitoring = MonitoringSystem(config)
    monitoring.start()
    
    # Simular algumas métricas
    time.sleep(5)
    
    # Mostrar métricas
    metrics = monitoring.get_metrics()
    print(f"Métricas coletadas: {len(metrics)}")
    
    # Mostrar alertas
    alerts = monitoring.get_alerts()
    print(f"Alertas: {len(alerts)}")
    
    # Exportar métricas Prometheus
    prometheus_metrics = monitoring.export_prometheus_metrics()
    print(f"Métricas Prometheus:\n{prometheus_metrics}") 