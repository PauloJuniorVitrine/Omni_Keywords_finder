"""
🧪 Testes de Dashboards e Alertas

Tracing ID: dashboards-alerts-tests-2025-01-27-001
Timestamp: 2025-01-27T20:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de monitoramento
🌲 ToT: Avaliadas múltiplas estratégias de teste
♻️ ReAct: Simulado cenários de produção e validada funcionalidade

Testa sistema de dashboards e alertas incluindo:
- Testes de métricas e coletores
- Testes de alertas e regras
- Testes de notificações (Slack, Email, Discord)
- Testes de dashboards Grafana
- Testes de performance
- Testes de integração
- Testes de configuração
- Testes de exportação de dados
"""

import pytest
import json
import time
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
import threading
import asyncio
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from infrastructure.monitoring.dashboards import (
    AlertSeverity, AlertStatus, NotificationChannel, MetricType,
    Metric, Alert, Dashboard, MetricsCollector, AlertManager,
    Notifier, SlackNotifier, EmailNotifier, DiscordNotifier,
    DashboardManager, MonitoringSystem, create_monitoring_system
)

class TestAlertSeverity:
    """Testes de severidades de alerta"""
    
    def test_alert_severity_values(self):
        """Testa valores das severidades"""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"

class TestAlertStatus:
    """Testes de status de alerta"""
    
    def test_alert_status_values(self):
        """Testa valores dos status"""
        assert AlertStatus.ACTIVE.value == "active"
        assert AlertStatus.ACKNOWLEDGED.value == "acknowledged"
        assert AlertStatus.RESOLVED.value == "resolved"
        assert AlertStatus.SILENCED.value == "silenced"

class TestNotificationChannel:
    """Testes de canais de notificação"""
    
    def test_notification_channel_values(self):
        """Testa valores dos canais"""
        assert NotificationChannel.SLACK.value == "slack"
        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.DISCORD.value == "discord"
        assert NotificationChannel.WEBHOOK.value == "webhook"
        assert NotificationChannel.SMS.value == "sms"
        assert NotificationChannel.PAGERDUTY.value == "pagerduty"

class TestMetricType:
    """Testes de tipos de métrica"""
    
    def test_metric_type_values(self):
        """Testa valores dos tipos"""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.SUMMARY.value == "summary"

class TestMetric:
    """Testes de métricas"""
    
    def test_metric_creation(self):
        """Testa criação de métrica"""
        metric = Metric(
            name="test_metric",
            type=MetricType.GAUGE,
            value=42.5,
            labels={"service": "test", "instance": "localhost"},
            description="Test metric",
            unit="requests/second"
        )
        
        assert metric.name == "test_metric"
        assert metric.type == MetricType.GAUGE
        assert metric.value == 42.5
        assert metric.labels["service"] == "test"
        assert metric.labels["instance"] == "localhost"
        assert metric.description == "Test metric"
        assert metric.unit == "requests/second"
        assert metric.timestamp is not None
    
    def test_metric_to_dict(self):
        """Testa conversão para dicionário"""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        metric = Metric(
            name="test_metric",
            type=MetricType.COUNTER,
            value=100,
            labels={"service": "test"},
            timestamp=timestamp,
            description="Test metric",
            unit="count"
        )
        
        metric_dict = metric.to_dict()
        
        assert metric_dict["name"] == "test_metric"
        assert metric_dict["type"] == "counter"
        assert metric_dict["value"] == 100
        assert metric_dict["labels"]["service"] == "test"
        assert metric_dict["timestamp"] == timestamp.isoformat()
        assert metric_dict["description"] == "Test metric"
        assert metric_dict["unit"] == "count"
    
    def test_metric_to_prometheus(self):
        """Testa conversão para formato Prometheus"""
        metric = Metric(
            name="http_requests_total",
            type=MetricType.COUNTER,
            value=1500,
            labels={"method": "GET", "endpoint": "/api/users"}
        )
        
        prometheus_str = metric.to_prometheus()
        
        assert "http_requests_total" in prometheus_str
        assert 'method="GET"' in prometheus_str
        assert 'endpoint="/api/users"' in prometheus_str
        assert "1500" in prometheus_str
    
    def test_metric_to_prometheus_no_labels(self):
        """Testa conversão para Prometheus sem labels"""
        metric = Metric(
            name="cpu_usage",
            type=MetricType.GAUGE,
            value=75.5
        )
        
        prometheus_str = metric.to_prometheus()
        
        assert prometheus_str == f"cpu_usage {75.5} {int(metric.timestamp.timestamp() * 1000)}"

class TestAlert:
    """Testes de alertas"""
    
    def test_alert_creation(self):
        """Testa criação de alerta"""
        triggered_at = datetime.now(timezone.utc)
        alert = Alert(
            id="alert123",
            name="High CPU Usage",
            description="CPU usage is above 80%",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=80.0,
            current_value=85.5,
            triggered_at=triggered_at,
            labels={"service": "web", "instance": "server1"},
            annotations={"runbook": "https://runbook.example.com/cpu"}
        )
        
        assert alert.id == "alert123"
        assert alert.name == "High CPU Usage"
        assert alert.description == "CPU usage is above 80%"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.status == AlertStatus.ACTIVE
        assert alert.condition == ">"
        assert alert.threshold == 80.0
        assert alert.current_value == 85.5
        assert alert.triggered_at == triggered_at
        assert alert.labels["service"] == "web"
        assert alert.annotations["runbook"] == "https://runbook.example.com/cpu"
    
    def test_alert_to_dict(self):
        """Testa conversão para dicionário"""
        triggered_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        resolved_at = datetime(2023, 1, 1, 12, 5, 0, tzinfo=timezone.utc)
        
        alert = Alert(
            id="alert123",
            name="High CPU Usage",
            description="CPU usage is above 80%",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.RESOLVED,
            condition=">",
            threshold=80.0,
            current_value=75.0,
            triggered_at=triggered_at,
            resolved_at=resolved_at
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict["id"] == "alert123"
        assert alert_dict["name"] == "High CPU Usage"
        assert alert_dict["severity"] == "warning"
        assert alert_dict["status"] == "resolved"
        assert alert_dict["triggered_at"] == triggered_at.isoformat()
        assert alert_dict["resolved_at"] == resolved_at.isoformat()
    
    def test_alert_is_active(self):
        """Testa verificação de alerta ativo"""
        alert = Alert(
            id="alert123",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.ERROR,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        
        assert alert.is_active() is True
        
        alert.status = AlertStatus.RESOLVED
        assert alert.is_active() is False
    
    def test_alert_is_resolved(self):
        """Testa verificação de alerta resolvido"""
        alert = Alert(
            id="alert123",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.ERROR,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        
        assert alert.is_resolved() is False
        
        alert.status = AlertStatus.RESOLVED
        assert alert.is_resolved() is True
    
    def test_alert_duration(self):
        """Testa cálculo de duração do alerta"""
        triggered_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        resolved_at = datetime(2023, 1, 1, 12, 5, 0, tzinfo=timezone.utc)
        
        alert = Alert(
            id="alert123",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.ERROR,
            status=AlertStatus.RESOLVED,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=triggered_at,
            resolved_at=resolved_at
        )
        
        duration = alert.duration()
        assert duration == timedelta(minutes=5)

class TestDashboard:
    """Testes de dashboards"""
    
    def test_dashboard_creation(self):
        """Testa criação de dashboard"""
        panels = [
            {
                "title": "CPU Usage",
                "type": "graph",
                "targets": [{"expr": "cpu_usage_percent"}]
            },
            {
                "title": "Memory Usage",
                "type": "graph",
                "targets": [{"expr": "memory_usage_bytes"}]
            }
        ]
        
        dashboard = Dashboard(
            id="performance",
            name="Performance Overview",
            description="System performance metrics",
            panels=panels,
            refresh_interval=30,
            time_range="1h",
            tags=["performance", "monitoring"]
        )
        
        assert dashboard.id == "performance"
        assert dashboard.name == "Performance Overview"
        assert dashboard.description == "System performance metrics"
        assert len(dashboard.panels) == 2
        assert dashboard.refresh_interval == 30
        assert dashboard.time_range == "1h"
        assert "performance" in dashboard.tags
        assert dashboard.created_at is not None
        assert dashboard.updated_at is not None
    
    def test_dashboard_to_dict(self):
        """Testa conversão para dicionário"""
        dashboard = Dashboard(
            id="test",
            name="Test Dashboard",
            description="Test",
            panels=[],
            tags=["test"]
        )
        
        dashboard_dict = dashboard.to_dict()
        
        assert dashboard_dict["id"] == "test"
        assert dashboard_dict["name"] == "Test Dashboard"
        assert dashboard_dict["description"] == "Test"
        assert dashboard_dict["panels"] == []
        assert dashboard_dict["tags"] == ["test"]
        assert dashboard_dict["created_at"] is not None
        assert dashboard_dict["updated_at"] is not None
    
    def test_dashboard_to_grafana(self):
        """Testa conversão para formato Grafana"""
        dashboard = Dashboard(
            id="test",
            name="Test Dashboard",
            description="Test",
            panels=[{"title": "Test Panel", "type": "graph"}],
            refresh_interval=60,
            time_range="2h",
            tags=["test"]
        )
        
        grafana_format = dashboard.to_grafana()
        
        assert grafana_format["dashboard"]["title"] == "Test Dashboard"
        assert grafana_format["dashboard"]["description"] == "Test"
        assert grafana_format["dashboard"]["tags"] == ["test"]
        assert grafana_format["dashboard"]["time"]["from"] == "now-2h"
        assert grafana_format["dashboard"]["time"]["to"] == "now"
        assert grafana_format["dashboard"]["refresh"] == "60s"
        assert len(grafana_format["dashboard"]["panels"]) == 1
        assert grafana_format["folderId"] == 0
        assert grafana_format["overwrite"] is True

class TestMetricsCollector:
    """Testes do coletor de métricas"""
    
    def test_metrics_collector_creation(self):
        """Testa criação do coletor"""
        collector = MetricsCollector()
        
        assert len(collector.metrics) == 0
        assert len(collector.collectors) == 0
        assert collector.collection_interval == 30
    
    def test_add_metric(self):
        """Testa adição de métrica"""
        collector = MetricsCollector()
        metric = Metric("test_metric", MetricType.GAUGE, 42.5)
        
        collector.add_metric(metric)
        
        assert len(collector.metrics) == 1
        assert "test_metric" in collector.metrics
    
    def test_get_metric(self):
        """Testa obtenção de métrica"""
        collector = MetricsCollector()
        metric = Metric("test_metric", MetricType.GAUGE, 42.5)
        
        collector.add_metric(metric)
        
        retrieved_metric = collector.get_metric("test_metric")
        assert retrieved_metric == metric
        
        # Métrica inexistente
        assert collector.get_metric("nonexistent") is None
    
    def test_get_metrics(self):
        """Testa obtenção de métricas"""
        collector = MetricsCollector()
        
        metric1 = Metric("cpu_usage", MetricType.GAUGE, 75.0)
        metric2 = Metric("memory_usage", MetricType.GAUGE, 80.0)
        metric3 = Metric("disk_usage", MetricType.GAUGE, 60.0)
        
        collector.add_metric(metric1)
        collector.add_metric(metric2)
        collector.add_metric(metric3)
        
        # Todas as métricas
        all_metrics = collector.get_metrics()
        assert len(all_metrics) == 3
        
        # Métricas com padrão
        cpu_metrics = collector.get_metrics("cpu")
        assert len(cpu_metrics) == 1
        assert cpu_metrics[0].name == "cpu_usage"
        
        usage_metrics = collector.get_metrics("usage")
        assert len(usage_metrics) == 3
    
    def test_add_collector(self):
        """Testa adição de coletor"""
        collector = MetricsCollector()
        
        def test_collector():
            return [Metric("test_metric", MetricType.GAUGE, 42.5)]
        
        collector.add_collector(test_collector)
        
        assert len(collector.collectors) == 1
    
    def test_collect_metrics(self):
        """Testa coleta de métricas"""
        collector = MetricsCollector()
        
        def test_collector():
            return [Metric("test_metric", MetricType.GAUGE, 42.5)]
        
        collector.add_collector(test_collector)
        collector.collect_metrics()
        
        assert len(collector.metrics) == 1
        assert "test_metric" in collector.metrics
    
    def test_collect_metrics_error_handling(self):
        """Testa tratamento de erro na coleta"""
        collector = MetricsCollector()
        
        def error_collector():
            raise ValueError("Test error")
        
        collector.add_collector(error_collector)
        
        # Não deve levantar exceção
        collector.collect_metrics()
        
        assert len(collector.metrics) == 0
    
    def test_export_prometheus(self):
        """Testa exportação Prometheus"""
        collector = MetricsCollector()
        
        metric1 = Metric("cpu_usage", MetricType.GAUGE, 75.0, {"instance": "server1"})
        metric2 = Metric("memory_usage", MetricType.GAUGE, 80.0, {"instance": "server1"})
        
        collector.add_metric(metric1)
        collector.add_metric(metric2)
        
        prometheus_export = collector.export_prometheus()
        
        assert "cpu_usage" in prometheus_export
        assert "memory_usage" in prometheus_export
        assert 'instance="server1"' in prometheus_export
        assert "75.0" in prometheus_export
        assert "80.0" in prometheus_export
    
    def test_export_json(self):
        """Testa exportação JSON"""
        collector = MetricsCollector()
        
        metric = Metric("test_metric", MetricType.GAUGE, 42.5)
        collector.add_metric(metric)
        
        json_export = collector.export_json()
        metrics_data = json.loads(json_export)
        
        assert len(metrics_data) == 1
        assert metrics_data[0]["name"] == "test_metric"
        assert metrics_data[0]["value"] == 42.5

class TestAlertManager:
    """Testes do gerenciador de alertas"""
    
    def test_alert_manager_creation(self):
        """Testa criação do gerenciador"""
        manager = AlertManager()
        
        assert len(manager.alerts) == 0
        assert len(manager.rules) == 0
        assert len(manager.notifiers) == 0
        assert manager.evaluation_interval == 30
    
    def test_add_alert_rule(self):
        """Testa adição de regra de alerta"""
        manager = AlertManager()
        
        rule = {
            "name": "High CPU Usage",
            "description": "CPU usage is above 80%",
            "metric": "cpu_usage_percent",
            "condition": ">",
            "threshold": 80.0,
            "severity": "warning"
        }
        
        manager.add_alert_rule(rule)
        
        assert len(manager.rules) == 1
        assert manager.rules[0]["name"] == "High CPU Usage"
    
    def test_add_notifier(self):
        """Testa adição de notificador"""
        manager = AlertManager()
        
        class TestNotifier(Notifier):
            def send_alert(self, alert): pass
            def send_resolution(self, alert): pass
        
        notifier = TestNotifier()
        manager.add_notifier(notifier)
        
        assert len(manager.notifiers) == 1
    
    def test_evaluate_alerts(self):
        """Testa avaliação de alertas"""
        manager = AlertManager()
        
        # Adicionar regra
        rule = {
            "name": "High CPU Usage",
            "description": "CPU usage is above 80%",
            "metric": "cpu_usage_percent",
            "condition": ">",
            "threshold": 80.0,
            "severity": "warning"
        }
        manager.add_alert_rule(rule)
        
        # Métrica que dispara alerta
        metrics = [Metric("cpu_usage_percent", MetricType.GAUGE, 85.0)]
        manager.evaluate_alerts(metrics)
        
        # Verificar se alerta foi criado
        active_alerts = manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].name == "High CPU Usage"
        assert active_alerts[0].current_value == 85.0
    
    def test_evaluate_alerts_resolution(self):
        """Testa resolução de alertas"""
        manager = AlertManager()
        
        # Adicionar regra
        rule = {
            "name": "High CPU Usage",
            "description": "CPU usage is above 80%",
            "metric": "cpu_usage_percent",
            "condition": ">",
            "threshold": 80.0,
            "severity": "warning"
        }
        manager.add_alert_rule(rule)
        
        # Disparar alerta
        metrics = [Metric("cpu_usage_percent", MetricType.GAUGE, 85.0)]
        manager.evaluate_alerts(metrics)
        
        # Verificar alerta ativo
        assert len(manager.get_active_alerts()) == 1
        
        # Resolver alerta
        metrics = [Metric("cpu_usage_percent", MetricType.GAUGE, 75.0)]
        manager.evaluate_alerts(metrics)
        
        # Verificar que alerta foi resolvido
        assert len(manager.get_active_alerts()) == 0
        all_alerts = manager.get_all_alerts()
        assert len(all_alerts) == 1
        assert all_alerts[0].is_resolved()
    
    def test_acknowledge_alert(self):
        """Testa reconhecimento de alerta"""
        manager = AlertManager()
        
        # Criar alerta manualmente
        alert = Alert(
            id="test_alert",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        
        manager.alerts["test_alert"] = alert
        
        # Reconhecer alerta
        manager.acknowledge_alert("test_alert", "admin")
        
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "admin"
        assert alert.acknowledged_at is not None
    
    def test_resolve_alert(self):
        """Testa resolução de alerta"""
        manager = AlertManager()
        
        # Criar alerta manualmente
        alert = Alert(
            id="test_alert",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        
        manager.alerts["test_alert"] = alert
        
        # Resolver alerta
        manager.resolve_alert("test_alert")
        
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None

class TestNotifiers:
    """Testes de notificadores"""
    
    @patch('requests.post')
    def test_slack_notifier_alert(self, mock_post):
        """Testa notificação de alerta no Slack"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        notifier = SlackNotifier("https://hooks.slack.com/test", "#alerts")
        
        alert = Alert(
            id="test_alert",
            name="High CPU Usage",
            description="CPU usage is above 80%",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=80.0,
            current_value=85.0,
            triggered_at=datetime.now(timezone.utc)
        )
        
        notifier.send_alert(alert)
        
        # Verificar se requisição foi feita
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/test"
        
        # Verificar payload
        payload = call_args[1]['json']
        assert payload['channel'] == "#alerts"
        assert len(payload['attachments']) == 1
        assert "🚨 High CPU Usage" in payload['attachments'][0]['title']
    
    @patch('requests.post')
    def test_slack_notifier_resolution(self, mock_post):
        """Testa notificação de resolução no Slack"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        notifier = SlackNotifier("https://hooks.slack.com/test", "#alerts")
        
        alert = Alert(
            id="test_alert",
            name="High CPU Usage",
            description="CPU usage is above 80%",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.RESOLVED,
            condition=">",
            threshold=80.0,
            current_value=75.0,
            triggered_at=datetime.now(timezone.utc),
            resolved_at=datetime.now(timezone.utc)
        )
        
        notifier.send_resolution(alert)
        
        # Verificar se requisição foi feita
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Verificar payload
        payload = call_args[1]['json']
        assert "✅ High CPU Usage - RESOLVIDO" in payload['attachments'][0]['title']
    
    @patch('smtplib.SMTP_SSL')
    def test_email_notifier_alert(self, mock_smtp):
        """Testa notificação de alerta por email"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        notifier = EmailNotifier(
            "smtp.gmail.com", 587, "test@example.com", "password", "alerts@example.com"
        )
        
        alert = Alert(
            id="test_alert",
            name="High CPU Usage",
            description="CPU usage is above 80%",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=80.0,
            current_value=85.0,
            triggered_at=datetime.now(timezone.utc)
        )
        
        notifier.send_alert(alert)
        
        # Verificar se email foi enviado
        mock_server.login.assert_called_once_with("test@example.com", "password")
        mock_server.send_message.assert_called_once()
    
    @patch('requests.post')
    def test_discord_notifier_alert(self, mock_post):
        """Testa notificação de alerta no Discord"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        notifier = DiscordNotifier("https://discord.com/api/webhooks/test")
        
        alert = Alert(
            id="test_alert",
            name="High CPU Usage",
            description="CPU usage is above 80%",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=80.0,
            current_value=85.0,
            triggered_at=datetime.now(timezone.utc)
        )
        
        notifier.send_alert(alert)
        
        # Verificar se requisição foi feita
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Verificar payload
        payload = call_args[1]['json']
        assert len(payload['embeds']) == 1
        assert "🚨 High CPU Usage" in payload['embeds'][0]['title']

class TestDashboardManager:
    """Testes do gerenciador de dashboards"""
    
    @patch('requests.post')
    def test_create_dashboard(self, mock_post):
        """Testa criação de dashboard"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        manager = DashboardManager("http://localhost:3000", "test-token")
        
        dashboard = Dashboard(
            id="test",
            name="Test Dashboard",
            description="Test",
            panels=[]
        )
        
        result = manager.create_dashboard(dashboard)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verificar headers
        call_args = mock_post.call_args
        headers = call_args[1]['headers']
        assert headers['Authorization'] == 'Bearer test-token'
        assert headers['Content-Type'] == 'application/json'
    
    @patch('requests.put')
    def test_update_dashboard(self, mock_put):
        """Testa atualização de dashboard"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        manager = DashboardManager("http://localhost:3000", "test-token")
        
        dashboard = Dashboard(
            id="test",
            name="Updated Dashboard",
            description="Updated",
            panels=[]
        )
        
        result = manager.update_dashboard(dashboard)
        
        assert result is True
        mock_put.assert_called_once()
    
    @patch('requests.delete')
    def test_delete_dashboard(self, mock_delete):
        """Testa deleção de dashboard"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        manager = DashboardManager("http://localhost:3000", "test-token")
        
        # Adicionar dashboard localmente
        dashboard = Dashboard(id="test", name="Test", description="Test")
        manager.dashboards["test"] = dashboard
        
        result = manager.delete_dashboard("test")
        
        assert result is True
        mock_delete.assert_called_once()
        assert "test" not in manager.dashboards
    
    def test_get_dashboard(self):
        """Testa obtenção de dashboard"""
        manager = DashboardManager("http://localhost:3000", "test-token")
        
        dashboard = Dashboard(id="test", name="Test", description="Test")
        manager.dashboards["test"] = dashboard
        
        retrieved_dashboard = manager.get_dashboard("test")
        assert retrieved_dashboard == dashboard
        
        # Dashboard inexistente
        assert manager.get_dashboard("nonexistent") is None
    
    def test_get_all_dashboards(self):
        """Testa obtenção de todos os dashboards"""
        manager = DashboardManager("http://localhost:3000", "test-token")
        
        dashboard1 = Dashboard(id="test1", name="Test1", description="Test1")
        dashboard2 = Dashboard(id="test2", name="Test2", description="Test2")
        
        manager.dashboards["test1"] = dashboard1
        manager.dashboards["test2"] = dashboard2
        
        all_dashboards = manager.get_all_dashboards()
        assert len(all_dashboards) == 2
        assert dashboard1 in all_dashboards
        assert dashboard2 in all_dashboards

class TestMonitoringSystem:
    """Testes do sistema de monitoramento"""
    
    def test_monitoring_system_creation(self):
        """Testa criação do sistema"""
        config = {
            'grafana': {
                'url': 'http://localhost:3000',
                'token': 'test-token'
            }
        }
        
        system = MonitoringSystem(config)
        
        assert system.metrics_collector is not None
        assert system.alert_manager is not None
        assert system.dashboard_manager is not None
    
    def test_monitoring_system_without_grafana(self):
        """Testa criação sem configuração Grafana"""
        system = MonitoringSystem()
        
        assert system.metrics_collector is not None
        assert system.alert_manager is not None
        assert system.dashboard_manager is None
    
    def test_get_metrics(self):
        """Testa obtenção de métricas"""
        system = MonitoringSystem()
        
        # Adicionar métrica manualmente
        metric = Metric("test_metric", MetricType.GAUGE, 42.5)
        system.metrics_collector.add_metric(metric)
        
        metrics = system.get_metrics()
        assert len(metrics) == 1
        assert metrics[0].name == "test_metric"
    
    def test_get_alerts(self):
        """Testa obtenção de alertas"""
        system = MonitoringSystem()
        
        # Adicionar alerta manualmente
        alert = Alert(
            id="test_alert",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        system.alert_manager.alerts["test_alert"] = alert
        
        alerts = system.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].name == "Test Alert"
    
    def test_get_active_alerts(self):
        """Testa obtenção de alertas ativos"""
        system = MonitoringSystem()
        
        # Adicionar alerta ativo
        active_alert = Alert(
            id="active_alert",
            name="Active Alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        system.alert_manager.alerts["active_alert"] = active_alert
        
        # Adicionar alerta resolvido
        resolved_alert = Alert(
            id="resolved_alert",
            name="Resolved Alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.RESOLVED,
            condition=">",
            threshold=10.0,
            current_value=5.0,
            triggered_at=datetime.now(timezone.utc),
            resolved_at=datetime.now(timezone.utc)
        )
        system.alert_manager.alerts["resolved_alert"] = resolved_alert
        
        active_alerts = system.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].name == "Active Alert"
    
    def test_acknowledge_alert(self):
        """Testa reconhecimento de alerta"""
        system = MonitoringSystem()
        
        alert = Alert(
            id="test_alert",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        system.alert_manager.alerts["test_alert"] = alert
        
        system.acknowledge_alert("test_alert", "admin")
        
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "admin"
    
    def test_resolve_alert(self):
        """Testa resolução de alerta"""
        system = MonitoringSystem()
        
        alert = Alert(
            id="test_alert",
            name="Test Alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            condition=">",
            threshold=10.0,
            current_value=15.0,
            triggered_at=datetime.now(timezone.utc)
        )
        system.alert_manager.alerts["test_alert"] = alert
        
        system.resolve_alert("test_alert")
        
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
    
    def test_export_prometheus_metrics(self):
        """Testa exportação de métricas Prometheus"""
        system = MonitoringSystem()
        
        metric = Metric("test_metric", MetricType.GAUGE, 42.5)
        system.metrics_collector.add_metric(metric)
        
        prometheus_export = system.export_prometheus_metrics()
        
        assert "test_metric" in prometheus_export
        assert "42.5" in prometheus_export
    
    def test_get_dashboard_url(self):
        """Testa obtenção de URL do dashboard"""
        config = {
            'grafana': {
                'url': 'http://localhost:3000',
                'token': 'test-token'
            }
        }
        
        system = MonitoringSystem(config)
        
        dashboard = Dashboard(id="test", name="Test", description="Test")
        system.dashboard_manager.dashboards["test"] = dashboard
        
        url = system.get_dashboard_url("test")
        assert url == "http://localhost:3000/d/test"
        
        # Dashboard inexistente
        assert system.get_dashboard_url("nonexistent") is None

class TestIntegration:
    """Testes de integração"""
    
    def test_full_monitoring_workflow(self):
        """Testa workflow completo de monitoramento"""
        # Configurar sistema
        config = {
            'alert_rules': [
                {
                    'name': 'High CPU Usage',
                    'description': 'CPU usage is above 80%',
                    'metric': 'cpu_usage_percent',
                    'condition': '>',
                    'threshold': 80.0,
                    'severity': 'warning'
                }
            ]
        }
        
        system = MonitoringSystem(config)
        
        # Adicionar métrica que dispara alerta
        metric = Metric("cpu_usage_percent", MetricType.GAUGE, 85.0)
        system.metrics_collector.add_metric(metric)
        
        # Avaliar alertas
        system.alert_manager.evaluate_alerts([metric])
        
        # Verificar alerta criado
        active_alerts = system.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].name == "High CPU Usage"
        assert active_alerts[0].current_value == 85.0
        
        # Adicionar métrica que resolve alerta
        resolved_metric = Metric("cpu_usage_percent", MetricType.GAUGE, 75.0)
        system.metrics_collector.add_metric(resolved_metric)
        
        # Avaliar alertas novamente
        system.alert_manager.evaluate_alerts([resolved_metric])
        
        # Verificar que alerta foi resolvido
        assert len(system.get_active_alerts()) == 0
        all_alerts = system.get_alerts()
        assert len(all_alerts) == 1
        assert all_alerts[0].is_resolved()
    
    def test_metrics_collection_and_export(self):
        """Testa coleta e exportação de métricas"""
        system = MonitoringSystem()
        
        # Adicionar coletores
        def test_collector():
            return [
                Metric("cpu_usage", MetricType.GAUGE, 75.0),
                Metric("memory_usage", MetricType.GAUGE, 80.0)
            ]
        
        system.metrics_collector.add_collector(test_collector)
        
        # Coletar métricas
        system.metrics_collector.collect_metrics()
        
        # Verificar métricas coletadas
        metrics = system.get_metrics()
        assert len(metrics) == 2
        assert any(m.name == "cpu_usage" for m in metrics)
        assert any(m.name == "memory_usage" for m in metrics)
        
        # Exportar Prometheus
        prometheus_export = system.export_prometheus_metrics()
        assert "cpu_usage" in prometheus_export
        assert "memory_usage" in prometheus_export
        assert "75.0" in prometheus_export
        assert "80.0" in prometheus_export

# Teste de funcionalidade
if __name__ == "__main__":
    # Teste básico
    system = MonitoringSystem()
    
    # Adicionar métrica
    metric = Metric("test_metric", MetricType.GAUGE, 42.5)
    system.metrics_collector.add_metric(metric)
    
    # Mostrar métricas
    metrics = system.get_metrics()
    print(f"Métricas: {len(metrics)}")
    
    # Exportar Prometheus
    prometheus_export = system.export_prometheus_metrics()
    print(f"Prometheus:\n{prometheus_export}") 