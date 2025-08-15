"""
Testes Unitários para ChaosConfig
ChaosConfig - Sistema de configuração para chaos engineering

Prompt: Implementação de testes unitários para ChaosConfig
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_CHAOS_CONFIG_001_20250127
"""

import pytest
import json
import yaml
import threading
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import os

from infrastructure.chaos.chaos_config import (
    Environment,
    ConfigScope,
    ChaosConfig,
    ExperimentTemplate,
    MonitoringConfig,
    AlertingConfig,
    RollbackConfig,
    ConfigManager,
    ConfigFileHandler,
    create_config_manager
)


class TestEnvironment:
    """Testes para Environment"""
    
    def test_environment_values(self):
        """Testa valores dos ambientes"""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TESTING.value == "testing"
    
    def test_environment_enumeration(self):
        """Testa enumeração completa dos ambientes"""
        expected_environments = [
            "development", "staging", "production", "testing"
        ]
        actual_environments = [env.value for env in Environment]
        assert actual_environments == expected_environments
    
    def test_environment_validation(self):
        """Testa validação de ambiente"""
        # Teste com ambiente válido
        valid_env = Environment.PRODUCTION
        assert valid_env.value == "production"
        
        # Teste com ambiente de desenvolvimento
        dev_env = Environment.DEVELOPMENT
        assert dev_env.value == "development"


class TestConfigScope:
    """Testes para ConfigScope"""
    
    def test_config_scope_values(self):
        """Testa valores dos escopos de configuração"""
        assert ConfigScope.GLOBAL.value == "global"
        assert ConfigScope.EXPERIMENT.value == "experiment"
        assert ConfigScope.MONITORING.value == "monitoring"
        assert ConfigScope.ALERTING.value == "alerting"
        assert ConfigScope.ROLLBACK.value == "rollback"
    
    def test_config_scope_enumeration(self):
        """Testa enumeração completa dos escopos"""
        expected_scopes = [
            "global", "experiment", "monitoring", "alerting", "rollback"
        ]
        actual_scopes = [scope.value for scope in ConfigScope]
        assert actual_scopes == expected_scopes


class TestChaosConfig:
    """Testes para ChaosConfig"""
    
    @pytest.fixture
    def sample_chaos_config_data(self):
        """Dados de exemplo para configuração de chaos"""
        return {
            "environment": Environment.PRODUCTION,
            "enabled": True,
            "max_concurrent_experiments": 5,
            "default_timeout": 600,
            "auto_rollback": True,
            "rollback_threshold": 0.4,
            "metrics_interval": 10,
            "log_level": "DEBUG",
            "safety_checks": True,
            "max_impact_threshold": 0.25,
            "blackout_hours": [0, 1, 2, 3, 4, 5, 6, 22, 23],
            "allowed_days": [1, 2, 3, 4, 5],
            "notify_on_start": True,
            "notify_on_completion": True,
            "notify_on_failure": True,
            "notify_on_rollback": True,
            "save_results": True,
            "results_retention_days": 60,
            "export_format": "yaml"
        }
    
    def test_chaos_config_initialization(self, sample_chaos_config_data):
        """Testa inicialização da configuração de chaos"""
        config = ChaosConfig(**sample_chaos_config_data)
        
        assert config.environment == Environment.PRODUCTION
        assert config.enabled is True
        assert config.max_concurrent_experiments == 5
        assert config.default_timeout == 600
        assert config.auto_rollback is True
        assert config.rollback_threshold == 0.4
        assert config.metrics_interval == 10
        assert config.log_level == "DEBUG"
        assert config.safety_checks is True
        assert config.max_impact_threshold == 0.25
        assert config.blackout_hours == [0, 1, 2, 3, 4, 5, 6, 22, 23]
        assert config.allowed_days == [1, 2, 3, 4, 5]
        assert config.notify_on_start is True
        assert config.notify_on_completion is True
        assert config.notify_on_failure is True
        assert config.notify_on_rollback is True
        assert config.save_results is True
        assert config.results_retention_days == 60
        assert config.export_format == "yaml"
    
    def test_chaos_config_defaults(self):
        """Testa valores padrão da configuração"""
        config = ChaosConfig(environment=Environment.DEVELOPMENT)
        
        assert config.enabled is True
        assert config.max_concurrent_experiments == 3
        assert config.default_timeout == 300
        assert config.auto_rollback is True
        assert config.rollback_threshold == 0.5
        assert config.metrics_interval == 5
        assert config.log_level == "INFO"
        assert config.safety_checks is True
        assert config.max_impact_threshold == 0.3
        assert config.blackout_hours == [0, 1, 2, 3, 4, 5, 6, 22, 23]
        assert config.allowed_days == [1, 2, 3, 4, 5]
        assert config.notify_on_start is True
        assert config.notify_on_completion is True
        assert config.notify_on_failure is True
        assert config.notify_on_rollback is True
        assert config.save_results is True
        assert config.results_retention_days == 30
        assert config.export_format == "json"
    
    def test_chaos_config_post_init(self):
        """Testa inicialização pós-construção"""
        # Teste sem especificar blackout_hours e allowed_days
        config = ChaosConfig(
            environment=Environment.STAGING,
            blackout_hours=None,
            allowed_days=None
        )
        
        # Verificar que valores padrão foram definidos
        assert config.blackout_hours == [0, 1, 2, 3, 4, 5, 6, 22, 23]
        assert config.allowed_days == [1, 2, 3, 4, 5]
    
    def test_chaos_config_custom_values(self):
        """Testa configuração com valores customizados"""
        custom_config = ChaosConfig(
            environment=Environment.TESTING,
            blackout_hours=[23, 0, 1, 2],
            allowed_days=[0, 6],  # Domingo e Sábado
            max_concurrent_experiments=1,
            default_timeout=120,
            log_level="ERROR"
        )
        
        assert custom_config.blackout_hours == [23, 0, 1, 2]
        assert custom_config.allowed_days == [0, 6]
        assert custom_config.max_concurrent_experiments == 1
        assert custom_config.default_timeout == 120
        assert custom_config.log_level == "ERROR"


class TestExperimentTemplate:
    """Testes para ExperimentTemplate"""
    
    @pytest.fixture
    def sample_template_data(self):
        """Dados de exemplo para template"""
        return {
            "name": "network_latency_template",
            "description": "Template para testes de latência de rede",
            "type": "network_latency",
            "category": "network",
            "duration": 180,
            "steady_state_duration": 30,
            "chaos_duration": 90,
            "observation_duration": 30,
            "max_impact": 0.2,
            "auto_rollback": True,
            "rollback_threshold": 0.4,
            "parameters": {
                "latency_ms": 100,
                "packet_loss_percent": 0.0
            },
            "metrics_interval": 3,
            "alert_thresholds": {
                "error_rate": 0.05,
                "response_time": 300.0
            },
            "prerequisites": [
                "Network connectivity stable",
                "Service health check passed"
            ],
            "success_criteria": [
                "Error rate < 5%",
                "Response time < 300ms"
            ]
        }
    
    def test_experiment_template_initialization(self, sample_template_data):
        """Testa inicialização do template"""
        template = ExperimentTemplate(**sample_template_data)
        
        assert template.name == "network_latency_template"
        assert template.description == "Template para testes de latência de rede"
        assert template.type == "network_latency"
        assert template.category == "network"
        assert template.duration == 180
        assert template.steady_state_duration == 30
        assert template.chaos_duration == 90
        assert template.observation_duration == 30
        assert template.max_impact == 0.2
        assert template.auto_rollback is True
        assert template.rollback_threshold == 0.4
        assert template.parameters["latency_ms"] == 100
        assert template.metrics_interval == 3
        assert template.alert_thresholds["error_rate"] == 0.05
        assert len(template.prerequisites) == 2
        assert len(template.success_criteria) == 2
    
    def test_experiment_template_defaults(self):
        """Testa valores padrão do template"""
        minimal_template = ExperimentTemplate(
            name="minimal_template",
            description="Minimal template",
            type="cpu_stress",
            category="performance"
        )
        
        assert minimal_template.duration == 300
        assert minimal_template.steady_state_duration == 60
        assert minimal_template.chaos_duration == 120
        assert minimal_template.observation_duration == 60
        assert minimal_template.max_impact == 0.3
        assert minimal_template.auto_rollback is True
        assert minimal_template.rollback_threshold == 0.5
        assert minimal_template.metrics_interval == 5
        assert minimal_template.parameters == {}
        assert minimal_template.alert_thresholds == {}
        assert minimal_template.prerequisites == []
        assert minimal_template.success_criteria == []
    
    def test_experiment_template_validation(self):
        """Testa validação do template"""
        # Teste com max_impact válido
        valid_template = ExperimentTemplate(
            name="valid_template",
            description="Valid template",
            type="memory_stress",
            category="performance",
            max_impact=0.5
        )
        assert valid_template.max_impact == 0.5
        
        # Teste com max_impact inválido
        with pytest.raises(ValueError, match="max_impact must be between 0 and 1"):
            ExperimentTemplate(
                name="invalid_template",
                description="Invalid template",
                type="disk_stress",
                category="performance",
                max_impact=1.5
            )
        
        # Teste com rollback_threshold inválido
        with pytest.raises(ValueError, match="rollback_threshold must be between 0 and 1"):
            ExperimentTemplate(
                name="invalid_template",
                description="Invalid template",
                type="service_failure",
                category="availability",
                rollback_threshold=-0.1
            )


class TestMonitoringConfig:
    """Testes para MonitoringConfig"""
    
    @pytest.fixture
    def sample_monitoring_data(self):
        """Dados de exemplo para configuração de monitoramento"""
        return {
            "enabled": True,
            "metrics_interval": 10,
            "retention_period": 7200,
            "collect_cpu": True,
            "collect_memory": True,
            "collect_disk": False,
            "collect_network": True,
            "collect_application": True,
            "cpu_threshold": 0.9,
            "memory_threshold": 0.85,
            "disk_threshold": 0.95,
            "error_rate_threshold": 0.1,
            "response_time_threshold": 3.0,
            "export_to_prometheus": True,
            "export_to_grafana": False,
            "export_to_logs": True
        }
    
    def test_monitoring_config_initialization(self, sample_monitoring_data):
        """Testa inicialização da configuração de monitoramento"""
        config = MonitoringConfig(**sample_monitoring_data)
        
        assert config.enabled is True
        assert config.metrics_interval == 10
        assert config.retention_period == 7200
        assert config.collect_cpu is True
        assert config.collect_memory is True
        assert config.collect_disk is False
        assert config.collect_network is True
        assert config.collect_application is True
        assert config.cpu_threshold == 0.9
        assert config.memory_threshold == 0.85
        assert config.disk_threshold == 0.95
        assert config.error_rate_threshold == 0.1
        assert config.response_time_threshold == 3.0
        assert config.export_to_prometheus is True
        assert config.export_to_grafana is False
        assert config.export_to_logs is True
    
    def test_monitoring_config_defaults(self):
        """Testa valores padrão da configuração de monitoramento"""
        config = MonitoringConfig()
        
        assert config.enabled is True
        assert config.metrics_interval == 5
        assert config.retention_period == 3600
        assert config.collect_cpu is True
        assert config.collect_memory is True
        assert config.collect_disk is True
        assert config.collect_network is True
        assert config.collect_application is True
        assert config.cpu_threshold == 0.8
        assert config.memory_threshold == 0.8
        assert config.disk_threshold == 0.9
        assert config.error_rate_threshold == 0.05
        assert config.response_time_threshold == 2.0
        assert config.export_to_prometheus is True
        assert config.export_to_grafana is True
        assert config.export_to_logs is True


class TestAlertingConfig:
    """Testes para AlertingConfig"""
    
    @pytest.fixture
    def sample_alerting_data(self):
        """Dados de exemplo para configuração de alertas"""
        return {
            "enabled": True,
            "email_enabled": True,
            "slack_enabled": True,
            "webhook_enabled": False,
            "console_enabled": True,
            "email_recipients": ["admin@company.com", "dev@company.com"],
            "email_smtp_server": "smtp.company.com",
            "email_smtp_port": 465,
            "email_username": "alerts@company.com",
            "email_password": "secure_password",
            "slack_webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz",
            "slack_channel": "#chaos-alerts",
            "slack_username": "Chaos Alert Bot",
            "webhook_url": "https://api.company.com/webhooks/chaos",
            "webhook_headers": {"Authorization": "Bearer token"},
            "group_alerts": True,
            "alert_cooldown": 600,
            "max_alerts_per_hour": 5
        }
    
    def test_alerting_config_initialization(self, sample_alerting_data):
        """Testa inicialização da configuração de alertas"""
        config = AlertingConfig(**sample_alerting_data)
        
        assert config.enabled is True
        assert config.email_enabled is True
        assert config.slack_enabled is True
        assert config.webhook_enabled is False
        assert config.console_enabled is True
        assert config.email_recipients == ["admin@company.com", "dev@company.com"]
        assert config.email_smtp_server == "smtp.company.com"
        assert config.email_smtp_port == 465
        assert config.email_username == "alerts@company.com"
        assert config.email_password == "secure_password"
        assert config.slack_webhook_url == "https://hooks.slack.com/services/xxx/yyy/zzz"
        assert config.slack_channel == "#chaos-alerts"
        assert config.slack_username == "Chaos Alert Bot"
        assert config.webhook_url == "https://api.company.com/webhooks/chaos"
        assert config.webhook_headers["Authorization"] == "Bearer token"
        assert config.group_alerts is True
        assert config.alert_cooldown == 600
        assert config.max_alerts_per_hour == 5
    
    def test_alerting_config_defaults(self):
        """Testa valores padrão da configuração de alertas"""
        config = AlertingConfig()
        
        assert config.enabled is True
        assert config.email_enabled is False
        assert config.slack_enabled is True
        assert config.webhook_enabled is False
        assert config.console_enabled is True
        assert config.email_recipients == []
        assert config.email_smtp_server == ""
        assert config.email_smtp_port == 587
        assert config.email_username == ""
        assert config.email_password == ""
        assert config.slack_webhook_url == ""
        assert config.slack_channel == "#chaos-engineering"
        assert config.slack_username == "Chaos Bot"
        assert config.webhook_url == ""
        assert config.webhook_headers == {}
        assert config.group_alerts is True
        assert config.alert_cooldown == 300
        assert config.max_alerts_per_hour == 10


class TestRollbackConfig:
    """Testes para RollbackConfig"""
    
    @pytest.fixture
    def sample_rollback_data(self):
        """Dados de exemplo para configuração de rollback"""
        return {
            "enabled": True,
            "auto_rollback": True,
            "error_rate_threshold": 0.3,
            "availability_threshold": 0.7,
            "response_time_threshold": 3.0,
            "rollback_delay": 60,
            "max_rollback_time": 600,
            "strategies": {
                "network_latency": {
                    "type": "immediate",
                    "timeout": 30
                },
                "service_failure": {
                    "type": "gradual",
                    "timeout": 120
                }
            },
            "notify_on_rollback": True,
            "notify_on_rollback_failure": True
        }
    
    def test_rollback_config_initialization(self, sample_rollback_data):
        """Testa inicialização da configuração de rollback"""
        config = RollbackConfig(**sample_rollback_data)
        
        assert config.enabled is True
        assert config.auto_rollback is True
        assert config.error_rate_threshold == 0.3
        assert config.availability_threshold == 0.7
        assert config.response_time_threshold == 3.0
        assert config.rollback_delay == 60
        assert config.max_rollback_time == 600
        assert config.strategies["network_latency"]["type"] == "immediate"
        assert config.strategies["service_failure"]["type"] == "gradual"
        assert config.notify_on_rollback is True
        assert config.notify_on_rollback_failure is True
    
    def test_rollback_config_defaults(self):
        """Testa valores padrão da configuração de rollback"""
        config = RollbackConfig()
        
        assert config.enabled is True
        assert config.auto_rollback is True
        assert config.error_rate_threshold == 0.5
        assert config.availability_threshold == 0.5
        assert config.response_time_threshold == 5.0
        assert config.rollback_delay == 30
        assert config.max_rollback_time == 300
        assert config.strategies == {}
        assert config.notify_on_rollback is True
        assert config.notify_on_rollback_failure is True


class TestConfigManager:
    """Testes para ConfigManager"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Diretório temporário para configurações"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Instância do ConfigManager para testes"""
        with patch('infrastructure.chaos.chaos_config.Observer'):
            manager = ConfigManager(config_dir=temp_config_dir)
            return manager
    
    def test_config_manager_initialization(self, config_manager, temp_config_dir):
        """Testa inicialização do ConfigManager"""
        assert config_manager.config_dir == Path(temp_config_dir)
        assert config_manager.chaos_config_file == Path(temp_config_dir) / "chaos_config.yaml"
        assert config_manager.templates_file == Path(temp_config_dir) / "templates.yaml"
        assert config_manager.monitoring_config_file == Path(temp_config_dir) / "monitoring.yaml"
        assert config_manager.alerting_config_file == Path(temp_config_dir) / "alerting.yaml"
        assert config_manager.rollback_config_file == Path(temp_config_dir) / "rollback.yaml"
        assert isinstance(config_manager.lock, threading.RLock)
        assert isinstance(config_manager.watchers, list)
        assert config_manager.last_modified == 0.0
    
    def test_config_manager_load_all_configs(self, config_manager):
        """Testa carregamento de todas as configurações"""
        # Verificar que configurações padrão foram criadas
        assert config_manager.chaos_config is not None
        assert config_manager.monitoring_config is not None
        assert config_manager.alerting_config is not None
        assert config_manager.rollback_config is not None
        assert isinstance(config_manager.templates, dict)
    
    def test_config_manager_get_chaos_config(self, config_manager):
        """Testa obtenção da configuração de chaos"""
        chaos_config = config_manager.get_chaos_config()
        assert chaos_config is not None
        assert isinstance(chaos_config, ChaosConfig)
        assert chaos_config.environment == Environment.DEVELOPMENT
    
    def test_config_manager_get_monitoring_config(self, config_manager):
        """Testa obtenção da configuração de monitoramento"""
        monitoring_config = config_manager.get_monitoring_config()
        assert monitoring_config is not None
        assert isinstance(monitoring_config, MonitoringConfig)
        assert monitoring_config.enabled is True
    
    def test_config_manager_get_alerting_config(self, config_manager):
        """Testa obtenção da configuração de alertas"""
        alerting_config = config_manager.get_alerting_config()
        assert alerting_config is not None
        assert isinstance(alerting_config, AlertingConfig)
        assert alerting_config.enabled is True
    
    def test_config_manager_get_rollback_config(self, config_manager):
        """Testa obtenção da configuração de rollback"""
        rollback_config = config_manager.get_rollback_config()
        assert rollback_config is not None
        assert isinstance(rollback_config, RollbackConfig)
        assert rollback_config.enabled is True
    
    def test_config_manager_add_template(self, config_manager):
        """Testa adição de template"""
        template = ExperimentTemplate(
            name="test_template",
            description="Test template",
            type="cpu_stress",
            category="performance"
        )
        
        config_manager.add_template(template)
        
        assert "test_template" in config_manager.templates
        assert config_manager.templates["test_template"] == template
    
    def test_config_manager_remove_template(self, config_manager):
        """Testa remoção de template"""
        template = ExperimentTemplate(
            name="test_template",
            description="Test template",
            type="cpu_stress",
            category="performance"
        )
        
        config_manager.add_template(template)
        assert "test_template" in config_manager.templates
        
        result = config_manager.remove_template("test_template")
        assert result is True
        assert "test_template" not in config_manager.templates
    
    def test_config_manager_remove_template_not_found(self, config_manager):
        """Testa remoção de template inexistente"""
        result = config_manager.remove_template("nonexistent")
        assert result is False
    
    def test_config_manager_get_template(self, config_manager):
        """Testa obtenção de template"""
        template = ExperimentTemplate(
            name="test_template",
            description="Test template",
            type="cpu_stress",
            category="performance"
        )
        
        config_manager.add_template(template)
        
        retrieved_template = config_manager.get_template("test_template")
        assert retrieved_template == template
    
    def test_config_manager_get_template_not_found(self, config_manager):
        """Testa obtenção de template inexistente"""
        template = config_manager.get_template("nonexistent")
        assert template is None
    
    def test_config_manager_list_templates(self, config_manager):
        """Testa listagem de templates"""
        template1 = ExperimentTemplate(
            name="template1",
            description="Template 1",
            type="cpu_stress",
            category="performance"
        )
        template2 = ExperimentTemplate(
            name="template2",
            description="Template 2",
            type="memory_stress",
            category="performance"
        )
        
        config_manager.add_template(template1)
        config_manager.add_template(template2)
        
        templates = config_manager.list_templates()
        assert len(templates) == 2
        assert templates[0]["name"] == "template1"
        assert templates[1]["name"] == "template2"
    
    def test_config_manager_list_templates_by_category(self, config_manager):
        """Testa listagem de templates por categoria"""
        template1 = ExperimentTemplate(
            name="template1",
            description="Template 1",
            type="cpu_stress",
            category="performance"
        )
        template2 = ExperimentTemplate(
            name="template2",
            description="Template 2",
            type="network_latency",
            category="network"
        )
        
        config_manager.add_template(template1)
        config_manager.add_template(template2)
        
        performance_templates = config_manager.list_templates(category="performance")
        assert len(performance_templates) == 1
        assert performance_templates[0]["name"] == "template1"
        
        network_templates = config_manager.list_templates(category="network")
        assert len(network_templates) == 1
        assert network_templates[0]["name"] == "template2"
    
    def test_config_manager_update_chaos_config(self, config_manager):
        """Testa atualização da configuração de chaos"""
        original_timeout = config_manager.chaos_config.default_timeout
        
        config_manager.update_chaos_config(default_timeout=600)
        
        assert config_manager.chaos_config.default_timeout == 600
        assert config_manager.chaos_config.default_timeout != original_timeout
    
    def test_config_manager_update_monitoring_config(self, config_manager):
        """Testa atualização da configuração de monitoramento"""
        original_interval = config_manager.monitoring_config.metrics_interval
        
        config_manager.update_monitoring_config(metrics_interval=10)
        
        assert config_manager.monitoring_config.metrics_interval == 10
        assert config_manager.monitoring_config.metrics_interval != original_interval
    
    def test_config_manager_update_alerting_config(self, config_manager):
        """Testa atualização da configuração de alertas"""
        original_cooldown = config_manager.alerting_config.alert_cooldown
        
        config_manager.update_alerting_config(alert_cooldown=600)
        
        assert config_manager.alerting_config.alert_cooldown == 600
        assert config_manager.alerting_config.alert_cooldown != original_cooldown
    
    def test_config_manager_update_rollback_config(self, config_manager):
        """Testa atualização da configuração de rollback"""
        original_delay = config_manager.rollback_config.rollback_delay
        
        config_manager.update_rollback_config(rollback_delay=60)
        
        assert config_manager.rollback_config.rollback_delay == 60
        assert config_manager.rollback_config.rollback_delay != original_delay
    
    def test_config_manager_validate_experiment_config(self, config_manager):
        """Testa validação de configuração de experimento"""
        valid_config = {
            "name": "test_experiment",
            "type": "cpu_stress",
            "duration": 300,
            "max_impact": 0.3
        }
        
        errors = config_manager.validate_experiment_config(valid_config)
        assert len(errors) == 0
        
        invalid_config = {
            "name": "",  # Nome vazio
            "type": "invalid_type",  # Tipo inválido
            "duration": -1,  # Duração negativa
            "max_impact": 1.5  # Impacto inválido
        }
        
        errors = config_manager.validate_experiment_config(invalid_config)
        assert len(errors) > 0
    
    def test_config_manager_is_experiment_allowed(self, config_manager):
        """Testa verificação se experimento é permitido"""
        # Configurar horário de blackout
        config_manager.chaos_config.blackout_hours = [0, 1, 2, 3, 4, 5, 6, 22, 23]
        
        # Teste com horário permitido (12:00)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 27, 12, 0, 0)
            
            config = {"name": "test", "type": "cpu_stress"}
            allowed = config_manager.is_experiment_allowed(config)
            assert allowed is True
        
        # Teste com horário de blackout (2:00)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 27, 2, 0, 0)
            
            config = {"name": "test", "type": "cpu_stress"}
            allowed = config_manager.is_experiment_allowed(config)
            assert allowed is False
    
    def test_config_manager_export_config(self, config_manager):
        """Testa exportação de configuração"""
        # Adicionar template para teste
        template = ExperimentTemplate(
            name="test_template",
            description="Test template",
            type="cpu_stress",
            category="performance"
        )
        config_manager.add_template(template)
        
        # Exportar em YAML
        yaml_config = config_manager.export_config(format="yaml")
        assert "chaos_config:" in yaml_config
        assert "templates:" in yaml_config
        assert "monitoring_config:" in yaml_config
        assert "alerting_config:" in yaml_config
        assert "rollback_config:" in yaml_config
        
        # Exportar em JSON
        json_config = config_manager.export_config(format="json")
        config_data = json.loads(json_config)
        assert "chaos_config" in config_data
        assert "templates" in config_data
        assert "monitoring_config" in config_data
        assert "alerting_config" in config_data
        assert "rollback_config" in config_data
    
    def test_config_manager_import_config(self, config_manager):
        """Testa importação de configuração"""
        # Configuração de teste
        test_config = {
            "chaos_config": {
                "environment": "production",
                "enabled": True,
                "max_concurrent_experiments": 5
            },
            "templates": [
                {
                    "name": "imported_template",
                    "description": "Imported template",
                    "type": "memory_stress",
                    "category": "performance"
                }
            ]
        }
        
        yaml_config = yaml.dump(test_config)
        
        result = config_manager.import_config(yaml_config, format="yaml")
        assert result is True
        
        # Verificar se configuração foi importada
        chaos_config = config_manager.get_chaos_config()
        assert chaos_config.environment == Environment.PRODUCTION
        assert chaos_config.max_concurrent_experiments == 5
        
        template = config_manager.get_template("imported_template")
        assert template is not None
        assert template.name == "imported_template"
    
    def test_config_manager_add_watcher(self, config_manager):
        """Testa adição de watcher"""
        watcher = Mock()
        
        config_manager.add_watcher(watcher)
        
        assert watcher in config_manager.watchers
        assert len(config_manager.watchers) == 1
    
    def test_config_manager_cleanup(self, config_manager):
        """Testa limpeza de recursos"""
        with patch.object(config_manager.observer, 'stop') as mock_stop:
            config_manager.cleanup()
            mock_stop.assert_called_once()


class TestConfigFileHandler:
    """Testes para ConfigFileHandler"""
    
    def test_config_file_handler_initialization(self):
        """Testa inicialização do handler de arquivos"""
        config_manager = Mock()
        handler = ConfigFileHandler(config_manager)
        
        assert handler.config_manager == config_manager
    
    def test_config_file_handler_on_modified(self):
        """Testa tratamento de modificação de arquivo"""
        config_manager = Mock()
        handler = ConfigFileHandler(config_manager)
        
        # Mock de evento de arquivo
        event = Mock()
        event.src_path = "/path/to/chaos_config.yaml"
        event.is_directory = False
        
        # Mock de tempo
        with patch('time.time') as mock_time:
            mock_time.return_value = 1234567890.0
            
            handler.on_modified(event)
            
            # Verificar se reload foi chamado
            config_manager.reload_config.assert_called_once()


class TestConfigManagerIntegration:
    """Testes de integração para ConfigManager"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Diretório temporário para configurações"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_full_config_lifecycle(self, temp_config_dir):
        """Testa ciclo completo de vida da configuração"""
        with patch('infrastructure.chaos.chaos_config.Observer'):
            # Criar manager
            manager = ConfigManager(config_dir=temp_config_dir)
            
            # Adicionar template
            template = ExperimentTemplate(
                name="lifecycle_template",
                description="Template for lifecycle test",
                type="cpu_stress",
                category="performance"
            )
            manager.add_template(template)
            
            # Verificar template foi adicionado
            assert "lifecycle_template" in manager.templates
            
            # Exportar configuração
            exported = manager.export_config(format="yaml")
            assert "lifecycle_template" in exported
            
            # Importar configuração
            result = manager.import_config(exported, format="yaml")
            assert result is True
            
            # Verificar template ainda existe
            assert "lifecycle_template" in manager.templates
    
    def test_config_persistence(self, temp_config_dir):
        """Testa persistência de configuração"""
        with patch('infrastructure.chaos.chaos_config.Observer'):
            # Criar manager
            manager = ConfigManager(config_dir=temp_config_dir)
            
            # Modificar configuração
            manager.update_chaos_config(default_timeout=600)
            
            # Verificar arquivo foi criado
            assert manager.chaos_config_file.exists()
            
            # Criar novo manager no mesmo diretório
            new_manager = ConfigManager(config_dir=temp_config_dir)
            
            # Verificar configuração foi persistida
            assert new_manager.chaos_config.default_timeout == 600


class TestConfigManagerErrorHandling:
    """Testes de tratamento de erro para ConfigManager"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Diretório temporário para configurações"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_config_manager_with_invalid_yaml(self, temp_config_dir):
        """Testa comportamento com YAML inválido"""
        with patch('infrastructure.chaos.chaos_config.Observer'):
            manager = ConfigManager(config_dir=temp_config_dir)
            
            # Criar arquivo YAML inválido
            invalid_yaml = "invalid: yaml: content: ["
            manager.chaos_config_file.write_text(invalid_yaml)
            
            # Tentar recarregar
            with patch('yaml.safe_load') as mock_load:
                mock_load.side_effect = yaml.YAMLError("Invalid YAML")
                
                # Deve continuar funcionando com configuração padrão
                chaos_config = manager.get_chaos_config()
                assert chaos_config is not None
    
    def test_config_manager_import_invalid_config(self, temp_config_dir):
        """Testa importação de configuração inválida"""
        with patch('infrastructure.chaos.chaos_config.Observer'):
            manager = ConfigManager(config_dir=temp_config_dir)
            
            invalid_config = "invalid json content"
            
            result = manager.import_config(invalid_config, format="json")
            assert result is False


class TestConfigManagerPerformance:
    """Testes de performance para ConfigManager"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Diretório temporário para configurações"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_config_manager_initialization_performance(self, temp_config_dir):
        """Testa performance de inicialização"""
        with patch('infrastructure.chaos.chaos_config.Observer'):
            start_time = time.time()
            manager = ConfigManager(config_dir=temp_config_dir)
            end_time = time.time()
            
            # Inicialização deve ser rápida (< 1 segundo)
            assert (end_time - start_time) < 1.0
    
    def test_config_manager_template_operations_performance(self, temp_config_dir):
        """Testa performance de operações com templates"""
        with patch('infrastructure.chaos.chaos_config.Observer'):
            manager = ConfigManager(config_dir=temp_config_dir)
            
            # Adicionar múltiplos templates
            start_time = time.time()
            for i in range(100):
                template = ExperimentTemplate(
                    name=f"template_{i}",
                    description=f"Template {i}",
                    type="cpu_stress",
                    category="performance"
                )
                manager.add_template(template)
            end_time = time.time()
            
            # Operações devem ser rápidas (< 5 segundos para 100 templates)
            assert (end_time - start_time) < 5.0
            assert len(manager.templates) == 100


def test_create_config_manager():
    """Testa função factory create_config_manager"""
    with patch('infrastructure.chaos.chaos_config.ConfigManager') as mock_manager_class:
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        manager = create_config_manager("test_config_dir")
        
        assert manager == mock_manager
        mock_manager_class.assert_called_once_with(config_dir="test_config_dir") 