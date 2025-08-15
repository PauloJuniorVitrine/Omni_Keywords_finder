"""
Testes Unitários para Performance Monitor
Sistema de Monitoramento de Performance - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de monitoramento de performance
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.performance.performance_monitor import (
    PerformanceMonitor, PerformanceConfig, MetricConfig, MetricType,
    AlertRule, AlertSeverity, Alert, AlertStatus, MetricValue,
    MetricAggregation, create_performance_monitor
)


class TestPerformanceConfig:
    """Testes para PerformanceConfig"""
    
    def test_performance_config_initialization(self):
        """Testa inicialização de PerformanceConfig"""
        config = PerformanceConfig(
            enable_system_metrics=False,
            enable_application_metrics=False,
            enable_custom_metrics=False,
            collection_interval=30,
            retention_days=60,
            aggregation_interval=600,
            enable_alerting=False,
            enable_dashboard=False,
            enable_export=False,
            export_format="csv",
            enable_webhook=True,
            webhook_url="https://webhook.example.com",
            enable_email_alerts=True,
            email_recipients=["admin@example.com"],
            enable_slack_alerts=True,
            slack_webhook_url="https://hooks.slack.com/...",
            enable_metrics_api=False,
            api_port=9090,
            enable_health_checks=False,
            health_check_interval=60
        )
        
        assert config.enable_system_metrics is False
        assert config.enable_application_metrics is False
        assert config.enable_custom_metrics is False
        assert config.collection_interval == 30
        assert config.retention_days == 60
        assert config.aggregation_interval == 600
        assert config.enable_alerting is False
        assert config.enable_dashboard is False
        assert config.enable_export is False
        assert config.export_format == "csv"
        assert config.enable_webhook is True
        assert config.webhook_url == "https://webhook.example.com"
        assert config.enable_email_alerts is True
        assert config.email_recipients == ["admin@example.com"]
        assert config.enable_slack_alerts is True
        assert config.slack_webhook_url == "https://hooks.slack.com/..."
        assert config.enable_metrics_api is False
        assert config.api_port == 9090
        assert config.enable_health_checks is False
        assert config.health_check_interval == 60
    
    def test_performance_config_validation_collection_interval_negative(self):
        """Testa validação de collection interval negativo"""
        with pytest.raises(ValueError, match="Collection interval deve ser positivo"):
            PerformanceConfig(collection_interval=0)
    
    def test_performance_config_validation_retention_days_negative(self):
        """Testa validação de retention days negativo"""
        with pytest.raises(ValueError, match="Retention days deve ser positivo"):
            PerformanceConfig(retention_days=0)
    
    def test_performance_config_validation_aggregation_interval_negative(self):
        """Testa validação de aggregation interval negativo"""
        with pytest.raises(ValueError, match="Aggregation interval deve ser positivo"):
            PerformanceConfig(aggregation_interval=0)
    
    def test_performance_config_validation_health_check_interval_negative(self):
        """Testa validação de health check interval negativo"""
        with pytest.raises(ValueError, match="Health check interval deve ser positivo"):
            PerformanceConfig(health_check_interval=0)
    
    def test_performance_config_validation_api_port_invalid(self):
        """Testa validação de API port inválido"""
        with pytest.raises(ValueError, match="API port deve estar entre 1 e 65535"):
            PerformanceConfig(api_port=0)
        
        with pytest.raises(ValueError, match="API port deve estar entre 1 e 65535"):
            PerformanceConfig(api_port=70000)


class TestMetricConfig:
    """Testes para MetricConfig"""
    
    def test_metric_config_initialization(self):
        """Testa inicialização de MetricConfig"""
        config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric description",
            unit="requests/sec",
            labels=["service", "endpoint"],
            interval=30,
            retention_days=7,
            aggregation_window=60,
            enable_alerting=True,
            thresholds={"warning": 80.0, "critical": 95.0}
        )
        
        assert config.name == "test_metric"
        assert config.type == MetricType.GAUGE
        assert config.description == "Test metric description"
        assert config.unit == "requests/sec"
        assert config.labels == ["service", "endpoint"]
        assert config.interval == 30
        assert config.retention_days == 7
        assert config.aggregation_window == 60
        assert config.enable_alerting is True
        assert config.thresholds == {"warning": 80.0, "critical": 95.0}
    
    def test_metric_config_validation_name_empty(self):
        """Testa validação de nome vazio"""
        with pytest.raises(ValueError, match="Nome da métrica não pode ser vazio"):
            MetricConfig(
                name="",
                type=MetricType.GAUGE,
                description="Test"
            )
    
    def test_metric_config_validation_interval_negative(self):
        """Testa validação de interval negativo"""
        with pytest.raises(ValueError, match="Interval deve ser positivo"):
            MetricConfig(
                name="test",
                type=MetricType.GAUGE,
                description="Test",
                interval=0
            )
    
    def test_metric_config_validation_retention_days_negative(self):
        """Testa validação de retention days negativo"""
        with pytest.raises(ValueError, match="Retention days deve ser positivo"):
            MetricConfig(
                name="test",
                type=MetricType.GAUGE,
                description="Test",
                retention_days=0
            )
    
    def test_metric_config_validation_aggregation_window_negative(self):
        """Testa validação de aggregation window negativo"""
        with pytest.raises(ValueError, match="Aggregation window deve ser positivo"):
            MetricConfig(
                name="test",
                type=MetricType.GAUGE,
                description="Test",
                aggregation_window=0
            )


class TestMetricValue:
    """Testes para MetricValue"""
    
    def test_metric_value_initialization(self):
        """Testa inicialização de MetricValue"""
        value = MetricValue(
            metric_name="test_metric",
            value=42.5,
            timestamp=datetime.utcnow(),
            labels={"service": "api", "endpoint": "/users"},
            metadata={"source": "test"}
        )
        
        assert value.metric_name == "test_metric"
        assert value.value == 42.5
        assert value.timestamp is not None
        assert value.labels == {"service": "api", "endpoint": "/users"}
        assert value.metadata == {"source": "test"}
    
    def test_metric_value_validation_name_empty(self):
        """Testa validação de nome vazio"""
        with pytest.raises(ValueError, match="Nome da métrica não pode ser vazio"):
            MetricValue(
                metric_name="",
                value=42.5,
                timestamp=datetime.utcnow()
            )
    
    def test_metric_value_validation_value_not_numeric(self):
        """Testa validação de valor não numérico"""
        with pytest.raises(ValueError, match="Valor deve ser numérico"):
            MetricValue(
                metric_name="test",
                value="not_a_number",
                timestamp=datetime.utcnow()
            )


class TestMetricAggregation:
    """Testes para MetricAggregation"""
    
    def test_metric_aggregation_initialization(self):
        """Testa inicialização de MetricAggregation"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=5)
        window_end = now
        
        aggregation = MetricAggregation(
            metric_name="test_metric",
            aggregation_type="avg",
            value=45.2,
            timestamp=now,
            window_start=window_start,
            window_end=window_end,
            sample_count=10,
            labels={"service": "api"}
        )
        
        assert aggregation.metric_name == "test_metric"
        assert aggregation.aggregation_type == "avg"
        assert aggregation.value == 45.2
        assert aggregation.timestamp == now
        assert aggregation.window_start == window_start
        assert aggregation.window_end == window_end
        assert aggregation.sample_count == 10
        assert aggregation.labels == {"service": "api"}


class TestAlertRule:
    """Testes para AlertRule"""
    
    def test_alert_rule_initialization(self):
        """Testa inicialização de AlertRule"""
        rule = AlertRule(
            name="high_cpu_usage",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            description="CPU usage is too high",
            enabled=True,
            cooldown_period=300,
            labels={"service": "system"}
        )
        
        assert rule.name == "high_cpu_usage"
        assert rule.metric_name == "cpu_usage"
        assert rule.condition == ">"
        assert rule.threshold == 90.0
        assert rule.severity == AlertSeverity.CRITICAL
        assert rule.description == "CPU usage is too high"
        assert rule.enabled is True
        assert rule.cooldown_period == 300
        assert rule.labels == {"service": "system"}
    
    def test_alert_rule_validation_name_empty(self):
        """Testa validação de nome vazio"""
        with pytest.raises(ValueError, match="Nome da regra não pode ser vazio"):
            AlertRule(
                name="",
                metric_name="cpu_usage",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                description="Test"
            )
    
    def test_alert_rule_validation_metric_name_empty(self):
        """Testa validação de metric name vazio"""
        with pytest.raises(ValueError, match="Nome da métrica não pode ser vazio"):
            AlertRule(
                name="test",
                metric_name="",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                description="Test"
            )
    
    def test_alert_rule_validation_invalid_condition(self):
        """Testa validação de condição inválida"""
        with pytest.raises(ValueError, match="Condição inválida"):
            AlertRule(
                name="test",
                metric_name="cpu_usage",
                condition="invalid",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                description="Test"
            )
    
    def test_alert_rule_validation_cooldown_negative(self):
        """Testa validação de cooldown negativo"""
        with pytest.raises(ValueError, match="Cooldown period não pode ser negativo"):
            AlertRule(
                name="test",
                metric_name="cpu_usage",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                description="Test",
                cooldown_period=-1
            )


class TestAlert:
    """Testes para Alert"""
    
    def test_alert_initialization(self):
        """Testa inicialização de Alert"""
        alert = Alert(
            id="alert_1",
            rule_name="high_cpu_usage",
            metric_name="cpu_usage",
            severity=AlertSeverity.CRITICAL,
            message="CPU usage is 95%",
            value=95.0,
            threshold=90.0,
            timestamp=datetime.utcnow(),
            status=AlertStatus.ACTIVE,
            labels={"service": "system"}
        )
        
        assert alert.id == "alert_1"
        assert alert.rule_name == "high_cpu_usage"
        assert alert.metric_name == "cpu_usage"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.message == "CPU usage is 95%"
        assert alert.value == 95.0
        assert alert.threshold == 90.0
        assert alert.status == AlertStatus.ACTIVE
        assert alert.labels == {"service": "system"}


class TestPerformanceMonitor:
    """Testes para PerformanceMonitor"""
    
    @pytest.fixture
    def config(self):
        """Configuração para testes"""
        return PerformanceConfig(
            enable_system_metrics=False,
            enable_alerting=True,
            collection_interval=1,
            aggregation_interval=1,
            health_check_interval=1
        )
    
    @pytest.fixture
    def monitor(self, config):
        """Instância de PerformanceMonitor para testes"""
        return PerformanceMonitor(config)
    
    def test_performance_monitor_initialization(self):
        """Testa inicialização do PerformanceMonitor"""
        monitor = PerformanceMonitor()
        
        assert monitor.config is not None
        assert len(monitor.metrics) == 0
        assert len(monitor.metric_values) == 0
        assert len(monitor.aggregations) == 0
        assert len(monitor.alert_rules) == 0
        assert len(monitor.active_alerts) == 0
        assert len(monitor.alert_history) == 0
        assert monitor.running is False
    
    def test_register_metric_success(self, monitor):
        """Testa registro de métrica com sucesso"""
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        
        success = monitor.register_metric(metric_config)
        assert success is True
        assert "test_metric" in monitor.metrics
    
    def test_register_metric_duplicate(self, monitor):
        """Testa registro de métrica duplicada"""
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        
        # Primeiro registro
        success1 = monitor.register_metric(metric_config)
        assert success1 is True
        
        # Segundo registro (deve falhar)
        success2 = monitor.register_metric(metric_config)
        assert success2 is False
    
    def test_record_metric_success(self, monitor):
        """Testa registro de valor de métrica com sucesso"""
        # Registrar métrica primeiro
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        monitor.register_metric(metric_config)
        
        # Registrar valor
        success = monitor.record_metric("test_metric", 42.5, {"service": "api"})
        assert success is True
        
        # Verificar que valor foi registrado
        values = monitor.get_metric_values("test_metric")
        assert len(values) == 1
        assert values[0].value == 42.5
        assert values[0].labels == {"service": "api"}
    
    def test_record_metric_not_registered(self, monitor):
        """Testa registro de valor de métrica não registrada"""
        success = monitor.record_metric("unregistered_metric", 42.5)
        assert success is False
    
    def test_get_metric_values(self, monitor):
        """Testa obtenção de valores de métrica"""
        # Registrar métrica e valores
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        monitor.register_metric(metric_config)
        
        monitor.record_metric("test_metric", 10.0)
        monitor.record_metric("test_metric", 20.0)
        monitor.record_metric("test_metric", 30.0)
        
        # Obter valores
        values = monitor.get_metric_values("test_metric")
        assert len(values) == 3
        assert values[0].value == 10.0
        assert values[1].value == 20.0
        assert values[2].value == 30.0
        
        # Obter com limite
        values_limited = monitor.get_metric_values("test_metric", limit=2)
        assert len(values_limited) == 2
        assert values_limited[0].value == 20.0
        assert values_limited[1].value == 30.0
    
    def test_get_metric_values_not_found(self, monitor):
        """Testa obtenção de valores de métrica inexistente"""
        values = monitor.get_metric_values("nonexistent_metric")
        assert len(values) == 0
    
    def test_add_alert_rule_success(self, monitor):
        """Testa adição de regra de alerta com sucesso"""
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            description="CPU usage too high"
        )
        
        success = monitor.add_alert_rule(rule)
        assert success is True
        assert "high_cpu" in monitor.alert_rules
    
    def test_add_alert_rule_duplicate(self, monitor):
        """Testa adição de regra de alerta duplicada"""
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            description="CPU usage too high"
        )
        
        # Primeira adição
        success1 = monitor.add_alert_rule(rule)
        assert success1 is True
        
        # Segunda adição (deve falhar)
        success2 = monitor.add_alert_rule(rule)
        assert success2 is False
    
    def test_remove_alert_rule_success(self, monitor):
        """Testa remoção de regra de alerta com sucesso"""
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            description="CPU usage too high"
        )
        
        monitor.add_alert_rule(rule)
        assert "high_cpu" in monitor.alert_rules
        
        success = monitor.remove_alert_rule("high_cpu")
        assert success is True
        assert "high_cpu" not in monitor.alert_rules
    
    def test_remove_alert_rule_not_found(self, monitor):
        """Testa remoção de regra de alerta inexistente"""
        success = monitor.remove_alert_rule("nonexistent")
        assert success is False
    
    def test_get_active_alerts(self, monitor):
        """Testa obtenção de alertas ativos"""
        # Criar alerta ativo
        alert = Alert(
            id="alert_1",
            rule_name="high_cpu",
            metric_name="cpu_usage",
            severity=AlertSeverity.CRITICAL,
            message="CPU usage is 95%",
            value=95.0,
            threshold=90.0,
            timestamp=datetime.utcnow()
        )
        monitor.active_alerts["alert_1"] = alert
        
        # Obter alertas ativos
        alerts = monitor.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].id == "alert_1"
        
        # Filtrar por severidade
        critical_alerts = monitor.get_active_alerts(AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 1
        
        warning_alerts = monitor.get_active_alerts(AlertSeverity.WARNING)
        assert len(warning_alerts) == 0
    
    def test_acknowledge_alert_success(self, monitor):
        """Testa reconhecimento de alerta com sucesso"""
        # Criar alerta ativo
        alert = Alert(
            id="alert_1",
            rule_name="high_cpu",
            metric_name="cpu_usage",
            severity=AlertSeverity.CRITICAL,
            message="CPU usage is 95%",
            value=95.0,
            threshold=90.0,
            timestamp=datetime.utcnow()
        )
        monitor.active_alerts["alert_1"] = alert
        
        # Reconhecer alerta
        success = monitor.acknowledge_alert("alert_1", "admin")
        assert success is True
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "admin"
        assert alert.acknowledged_at is not None
    
    def test_acknowledge_alert_not_found(self, monitor):
        """Testa reconhecimento de alerta inexistente"""
        success = monitor.acknowledge_alert("nonexistent", "admin")
        assert success is False
    
    def test_resolve_alert_success(self, monitor):
        """Testa resolução de alerta com sucesso"""
        # Criar alerta ativo
        alert = Alert(
            id="alert_1",
            rule_name="high_cpu",
            metric_name="cpu_usage",
            severity=AlertSeverity.CRITICAL,
            message="CPU usage is 95%",
            value=95.0,
            threshold=90.0,
            timestamp=datetime.utcnow()
        )
        monitor.active_alerts["alert_1"] = alert
        
        # Resolver alerta
        success = monitor.resolve_alert("alert_1")
        assert success is True
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
        assert "alert_1" not in monitor.active_alerts
        assert len(monitor.alert_history) == 1
    
    def test_resolve_alert_not_found(self, monitor):
        """Testa resolução de alerta inexistente"""
        success = monitor.resolve_alert("nonexistent")
        assert success is False
    
    def test_get_performance_stats(self, monitor):
        """Testa obtenção de estatísticas de performance"""
        stats = monitor.get_performance_stats()
        
        assert "system" in stats
        assert "metrics" in stats
        assert "alerts" in stats
        assert "timestamp" in stats
        
        metrics_stats = stats["metrics"]
        assert "total_metrics" in metrics_stats
        assert "total_values" in metrics_stats
        assert "total_aggregations" in metrics_stats
        
        alerts_stats = stats["alerts"]
        assert "total_rules" in alerts_stats
        assert "active_alerts" in alerts_stats
        assert "alert_history" in alerts_stats
    
    def test_export_metrics_json(self, monitor):
        """Testa exportação de métricas em JSON"""
        # Registrar métrica e valores
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        monitor.register_metric(metric_config)
        
        monitor.record_metric("test_metric", 42.5, {"service": "api"})
        
        # Exportar
        export_data = monitor.export_metrics("json")
        data = json.loads(export_data)
        
        assert "export_time" in data
        assert "start_time" in data
        assert "end_time" in data
        assert "metrics" in data
        assert "test_metric" in data["metrics"]
        assert len(data["metrics"]["test_metric"]) == 1
        assert data["metrics"]["test_metric"][0]["value"] == 42.5
    
    def test_export_metrics_csv(self, monitor):
        """Testa exportação de métricas em CSV"""
        # Registrar métrica e valores
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        monitor.register_metric(metric_config)
        
        monitor.record_metric("test_metric", 42.5, {"service": "api"})
        
        # Exportar
        export_data = monitor.export_metrics("csv")
        lines = export_data.split("\n")
        
        assert lines[0] == "metric_name,timestamp,value,labels"
        assert len(lines) >= 2
        assert "test_metric" in lines[1]
        assert "42.5" in lines[1]
    
    def test_export_metrics_prometheus(self, monitor):
        """Testa exportação de métricas em Prometheus"""
        # Registrar métrica e valores
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        monitor.register_metric(metric_config)
        
        monitor.record_metric("test_metric", 42.5, {"service": "api"})
        
        # Exportar
        export_data = monitor.export_metrics("prometheus")
        lines = export_data.split("\n")
        
        assert len(lines) >= 1
        assert "test_metric" in lines[0]
        assert "42.5" in lines[0]
    
    def test_export_metrics_invalid_format(self, monitor):
        """Testa exportação com formato inválido"""
        with pytest.raises(ValueError, match="Formato não suportado"):
            monitor.export_metrics("invalid_format")
    
    def test_start_stop_monitor(self, monitor):
        """Testa início e parada do monitor"""
        # Iniciar
        monitor.start()
        assert monitor.running is True
        
        # Parar
        monitor.stop()
        assert monitor.running is False
    
    def test_alert_triggering(self, monitor):
        """Testa disparo de alertas"""
        # Registrar métrica
        metric_config = MetricConfig(
            name="cpu_usage",
            type=MetricType.GAUGE,
            description="CPU usage"
        )
        monitor.register_metric(metric_config)
        
        # Adicionar regra de alerta
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            description="CPU usage too high"
        )
        monitor.add_alert_rule(rule)
        
        # Registrar valor que dispara alerta
        monitor.record_metric("cpu_usage", 95.0)
        
        # Verificar que alerta foi disparado
        alerts = monitor.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].rule_name == "high_cpu"
        assert alerts[0].value == 95.0
        assert alerts[0].threshold == 90.0
    
    def test_alert_cooldown(self, monitor):
        """Testa cooldown de alertas"""
        # Registrar métrica
        metric_config = MetricConfig(
            name="cpu_usage",
            type=MetricType.GAUGE,
            description="CPU usage"
        )
        monitor.register_metric(metric_config)
        
        # Adicionar regra de alerta com cooldown
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            description="CPU usage too high",
            cooldown_period=10
        )
        monitor.add_alert_rule(rule)
        
        # Primeiro valor (dispara alerta)
        monitor.record_metric("cpu_usage", 95.0)
        alerts1 = monitor.get_active_alerts()
        assert len(alerts1) == 1
        
        # Segundo valor (não dispara devido ao cooldown)
        monitor.record_metric("cpu_usage", 95.0)
        alerts2 = monitor.get_active_alerts()
        assert len(alerts2) == 1  # Mesmo número de alertas
    
    def test_callback_on_metric_collected(self, monitor):
        """Testa callback de métrica coletada"""
        collected_metrics = []
        
        def on_metric_collected(metric_value):
            collected_metrics.append(metric_value)
        
        monitor.on_metric_collected = on_metric_collected
        
        # Registrar métrica
        metric_config = MetricConfig(
            name="test_metric",
            type=MetricType.GAUGE,
            description="Test metric"
        )
        monitor.register_metric(metric_config)
        
        # Registrar valor
        monitor.record_metric("test_metric", 42.5)
        
        assert len(collected_metrics) == 1
        assert collected_metrics[0].metric_name == "test_metric"
        assert collected_metrics[0].value == 42.5
    
    def test_callback_on_alert_triggered(self, monitor):
        """Testa callback de alerta disparado"""
        triggered_alerts = []
        
        def on_alert_triggered(alert):
            triggered_alerts.append(alert)
        
        monitor.on_alert_triggered = on_alert_triggered
        
        # Registrar métrica
        metric_config = MetricConfig(
            name="cpu_usage",
            type=MetricType.GAUGE,
            description="CPU usage"
        )
        monitor.register_metric(metric_config)
        
        # Adicionar regra de alerta
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition=">",
            threshold=90.0,
            severity=AlertSeverity.CRITICAL,
            description="CPU usage too high"
        )
        monitor.add_alert_rule(rule)
        
        # Registrar valor que dispara alerta
        monitor.record_metric("cpu_usage", 95.0)
        
        assert len(triggered_alerts) == 1
        assert triggered_alerts[0].rule_name == "high_cpu"
    
    def test_callback_on_alert_resolved(self, monitor):
        """Testa callback de alerta resolvido"""
        resolved_alerts = []
        
        def on_alert_resolved(alert):
            resolved_alerts.append(alert)
        
        monitor.on_alert_resolved = on_alert_resolved
        
        # Criar alerta ativo
        alert = Alert(
            id="alert_1",
            rule_name="high_cpu",
            metric_name="cpu_usage",
            severity=AlertSeverity.CRITICAL,
            message="CPU usage is 95%",
            value=95.0,
            threshold=90.0,
            timestamp=datetime.utcnow()
        )
        monitor.active_alerts["alert_1"] = alert
        
        # Resolver alerta
        monitor.resolve_alert("alert_1")
        
        assert len(resolved_alerts) == 1
        assert resolved_alerts[0].id == "alert_1"


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_performance_monitor_default(self):
        """Testa criação de PerformanceMonitor com configurações padrão"""
        monitor = create_performance_monitor()
        
        assert isinstance(monitor, PerformanceMonitor)
        assert monitor.config is not None
    
    def test_create_performance_monitor_custom(self):
        """Testa criação de PerformanceMonitor com configurações customizadas"""
        config = PerformanceConfig(
            enable_system_metrics=False,
            collection_interval=30,
            enable_alerting=False
        )
        
        monitor = create_performance_monitor(config)
        
        assert monitor.config.enable_system_metrics is False
        assert monitor.config.collection_interval == 30
        assert monitor.config.enable_alerting is False


class TestPerformanceMonitorIntegration:
    """Testes de integração para Performance Monitor"""
    
    def test_complete_workflow(self):
        """Testa workflow completo do monitor"""
        config = PerformanceConfig(
            enable_system_metrics=False,
            enable_alerting=True,
            collection_interval=1,
            aggregation_interval=1
        )
        
        monitor = PerformanceMonitor(config)
        monitor.start()
        
        try:
            # Registrar métricas
            cpu_metric = MetricConfig(
                name="cpu_usage",
                type=MetricType.GAUGE,
                description="CPU usage percentage"
            )
            monitor.register_metric(cpu_metric)
            
            memory_metric = MetricConfig(
                name="memory_usage",
                type=MetricType.GAUGE,
                description="Memory usage percentage"
            )
            monitor.register_metric(memory_metric)
            
            # Adicionar regras de alerta
            cpu_rule = AlertRule(
                name="high_cpu",
                metric_name="cpu_usage",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                description="CPU usage too high"
            )
            monitor.add_alert_rule(cpu_rule)
            
            memory_rule = AlertRule(
                name="high_memory",
                metric_name="memory_usage",
                condition=">",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                description="Memory usage too high"
            )
            monitor.add_alert_rule(memory_rule)
            
            # Registrar valores
            monitor.record_metric("cpu_usage", 75.0, {"host": "server1"})
            monitor.record_metric("memory_usage", 80.0, {"host": "server1"})
            
            # Aguardar um pouco para processamento
            time.sleep(0.1)
            
            # Verificar valores
            cpu_values = monitor.get_metric_values("cpu_usage")
            assert len(cpu_values) == 1
            assert cpu_values[0].value == 75.0
            
            memory_values = monitor.get_metric_values("memory_usage")
            assert len(memory_values) == 1
            assert memory_values[0].value == 80.0
            
            # Registrar valor que dispara alerta
            monitor.record_metric("cpu_usage", 95.0, {"host": "server1"})
            
            # Aguardar processamento
            time.sleep(0.1)
            
            # Verificar alertas
            alerts = monitor.get_active_alerts()
            assert len(alerts) == 1
            assert alerts[0].rule_name == "high_cpu"
            assert alerts[0].value == 95.0
            
            # Verificar estatísticas
            stats = monitor.get_performance_stats()
            assert stats["metrics"]["total_metrics"] == 2
            assert stats["alerts"]["total_rules"] == 2
            assert stats["alerts"]["active_alerts"] == 1
            
        finally:
            monitor.stop()
    
    def test_metric_aggregation(self):
        """Testa agregação de métricas"""
        config = PerformanceConfig(
            enable_system_metrics=False,
            aggregation_interval=1
        )
        
        monitor = PerformanceMonitor(config)
        monitor.start()
        
        try:
            # Registrar métrica
            metric_config = MetricConfig(
                name="response_time",
                type=MetricType.HISTOGRAM,
                description="API response time"
            )
            monitor.register_metric(metric_config)
            
            # Registrar múltiplos valores
            for i in range(10):
                monitor.record_metric("response_time", 100.0 + i)
                time.sleep(0.1)
            
            # Aguardar agregação
            time.sleep(1.5)
            
            # Verificar agregações
            min_agg = monitor.get_metric_aggregation("response_time", "min", 1)
            max_agg = monitor.get_metric_aggregation("response_time", "max", 1)
            avg_agg = monitor.get_metric_aggregation("response_time", "avg", 1)
            
            assert min_agg is not None
            assert max_agg is not None
            assert avg_agg is not None
            assert min_agg.value == 100.0
            assert max_agg.value == 109.0
            assert 104.0 <= avg_agg.value <= 105.0
            
        finally:
            monitor.stop()
    
    def test_alert_workflow(self):
        """Testa workflow completo de alertas"""
        config = PerformanceConfig(
            enable_system_metrics=False,
            enable_alerting=True
        )
        
        monitor = PerformanceMonitor(config)
        
        # Registrar métrica
        metric_config = MetricConfig(
            name="error_rate",
            type=MetricType.GAUGE,
            description="Error rate percentage"
        )
        monitor.register_metric(metric_config)
        
        # Adicionar regra de alerta
        rule = AlertRule(
            name="high_error_rate",
            metric_name="error_rate",
            condition=">",
            threshold=5.0,
            severity=AlertSeverity.ERROR,
            description="Error rate too high"
        )
        monitor.add_alert_rule(rule)
        
        # Disparar alerta
        monitor.record_metric("error_rate", 10.0)
        
        # Verificar alerta ativo
        alerts = monitor.get_active_alerts()
        assert len(alerts) == 1
        alert = alerts[0]
        
        # Reconhecer alerta
        monitor.acknowledge_alert(alert.id, "admin")
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "admin"
        
        # Resolver alerta
        monitor.resolve_alert(alert.id)
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
        
        # Verificar que foi movido para histórico
        assert len(monitor.get_active_alerts()) == 0
        assert len(monitor.alert_history) == 1


if __name__ == "__main__":
    pytest.main([__file__]) 