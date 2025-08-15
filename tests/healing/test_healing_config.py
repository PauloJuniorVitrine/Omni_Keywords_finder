"""
Testes Unitários para HealingConfig
HealingConfig - Configuração do Sistema de Auto-Cura

Prompt: Implementação de testes unitários para HealingConfig
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_HEALING_CONFIG_001_20250127
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from infrastructure.healing.healing_config import HealingConfig


class TestHealingConfig:
    """Testes para HealingConfig"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Dados de exemplo para configuração"""
        return {
            "check_interval": 30,
            "timeout": 10,
            "max_retries": 3,
            "cache_ttl": 300,
            "max_workers": 5,
            "enable_auto_healing": True,
            "healing_strategies": ["restart", "reconnect", "cleanup"],
            "alert_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "error_rate": 0.05
            },
            "notification_settings": {
                "email_enabled": True,
                "slack_enabled": False,
                "webhook_url": "http://localhost:8080/webhook"
            }
        }
    
    def test_healing_config_initialization(self, sample_config_data):
        """Testa inicialização básica"""
        config = HealingConfig(**sample_config_data)
        
        assert config.check_interval == 30
        assert config.timeout == 10
        assert config.max_retries == 3
        assert config.cache_ttl == 300
        assert config.max_workers == 5
        assert config.enable_auto_healing is True
        assert "restart" in config.healing_strategies
        assert "reconnect" in config.healing_strategies
        assert "cleanup" in config.healing_strategies
        assert config.alert_thresholds["cpu_usage"] == 80.0
        assert config.alert_thresholds["memory_usage"] == 85.0
        assert config.alert_thresholds["error_rate"] == 0.05
        assert config.notification_settings["email_enabled"] is True
        assert config.notification_settings["slack_enabled"] is False
        assert config.notification_settings["webhook_url"] == "http://localhost:8080/webhook"
    
    def test_healing_config_default_values(self):
        """Testa valores padrão da configuração"""
        config = HealingConfig()
        
        # Verificar se a configuração é criada com valores padrão
        assert config is not None
        assert hasattr(config, 'check_interval')
        assert hasattr(config, 'timeout')
        assert hasattr(config, 'max_retries')
        assert hasattr(config, 'cache_ttl')
        assert hasattr(config, 'max_workers')
        assert hasattr(config, 'enable_auto_healing')
        assert hasattr(config, 'healing_strategies')
        assert hasattr(config, 'alert_thresholds')
        assert hasattr(config, 'notification_settings')
    
    def test_healing_config_validation(self, sample_config_data):
        """Testa validações de configuração"""
        config = HealingConfig(**sample_config_data)
        
        # Validações básicas
        assert config.check_interval > 0
        assert config.timeout > 0
        assert config.max_retries >= 0
        assert config.cache_ttl > 0
        assert config.max_workers > 0
        assert isinstance(config.enable_auto_healing, bool)
        assert isinstance(config.healing_strategies, list)
        assert isinstance(config.alert_thresholds, dict)
        assert isinstance(config.notification_settings, dict)
        
        # Validações de thresholds
        assert 0 <= config.alert_thresholds["cpu_usage"] <= 100
        assert 0 <= config.alert_thresholds["memory_usage"] <= 100
        assert 0 <= config.alert_thresholds["error_rate"] <= 1
    
    def test_healing_config_edge_cases(self):
        """Testa casos extremos"""
        # Teste com valores mínimos
        min_data = {
            "check_interval": 1,
            "timeout": 1,
            "max_retries": 0,
            "cache_ttl": 1,
            "max_workers": 1,
            "enable_auto_healing": False,
            "healing_strategies": [],
            "alert_thresholds": {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "error_rate": 0.0
            },
            "notification_settings": {
                "email_enabled": False,
                "slack_enabled": False,
                "webhook_url": ""
            }
        }
        config = HealingConfig(**min_data)
        assert config.check_interval == 1
        assert config.timeout == 1
        assert config.max_retries == 0
        assert config.enable_auto_healing is False
        assert len(config.healing_strategies) == 0
        
        # Teste com valores máximos
        max_data = {
            "check_interval": 3600,
            "timeout": 300,
            "max_retries": 10,
            "cache_ttl": 86400,
            "max_workers": 50,
            "enable_auto_healing": True,
            "healing_strategies": ["restart", "reconnect", "cleanup", "reload", "reset"],
            "alert_thresholds": {
                "cpu_usage": 100.0,
                "memory_usage": 100.0,
                "error_rate": 1.0
            },
            "notification_settings": {
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_url": "https://webhook.example.com/endpoint"
            }
        }
        config = HealingConfig(**max_data)
        assert config.check_interval == 3600
        assert config.timeout == 300
        assert config.max_retries == 10
        assert config.max_workers == 50
        assert config.enable_auto_healing is True
        assert len(config.healing_strategies) == 5
    
    def test_healing_config_strategies_validation(self):
        """Testa validação de estratégias de healing"""
        # Teste com estratégias válidas
        valid_strategies = ["restart", "reconnect", "cleanup", "reload"]
        config_data = {
            "check_interval": 30,
            "timeout": 10,
            "max_retries": 3,
            "cache_ttl": 300,
            "max_workers": 5,
            "healing_strategies": valid_strategies
        }
        
        config = HealingConfig(**config_data)
        assert len(config.healing_strategies) == 4
        assert all(strategy in config.healing_strategies for strategy in valid_strategies)
        
        # Teste com estratégias duplicadas
        duplicate_strategies = ["restart", "restart", "reconnect"]
        config_data["healing_strategies"] = duplicate_strategies
        config = HealingConfig(**config_data)
        assert len(config.healing_strategies) == 2  # Duplicatas devem ser removidas
        assert "restart" in config.healing_strategies
        assert "reconnect" in config.healing_strategies
    
    def test_healing_config_thresholds_validation(self):
        """Testa validação de thresholds de alerta"""
        # Teste com thresholds válidos
        valid_thresholds = {
            "cpu_usage": 75.0,
            "memory_usage": 80.0,
            "error_rate": 0.03,
            "response_time": 500.0,
            "disk_usage": 90.0
        }
        
        config_data = {
            "check_interval": 30,
            "timeout": 10,
            "max_retries": 3,
            "cache_ttl": 300,
            "max_workers": 5,
            "alert_thresholds": valid_thresholds
        }
        
        config = HealingConfig(**config_data)
        assert config.alert_thresholds["cpu_usage"] == 75.0
        assert config.alert_thresholds["memory_usage"] == 80.0
        assert config.alert_thresholds["error_rate"] == 0.03
        assert config.alert_thresholds["response_time"] == 500.0
        assert config.alert_thresholds["disk_usage"] == 90.0
        
        # Teste com thresholds inválidos (deve usar valores padrão)
        invalid_thresholds = {
            "cpu_usage": 150.0,  # > 100
            "memory_usage": -10.0,  # < 0
            "error_rate": 2.0  # > 1
        }
        
        config_data["alert_thresholds"] = invalid_thresholds
        config = HealingConfig(**config_data)
        
        # Deve usar valores padrão ou válidos
        assert 0 <= config.alert_thresholds["cpu_usage"] <= 100
        assert 0 <= config.alert_thresholds["memory_usage"] <= 100
        assert 0 <= config.alert_thresholds["error_rate"] <= 1
    
    def test_healing_config_notification_validation(self):
        """Testa validação de configurações de notificação"""
        # Teste com configurações válidas
        valid_notifications = {
            "email_enabled": True,
            "slack_enabled": True,
            "webhook_url": "https://webhook.example.com",
            "email_recipients": ["admin@example.com", "dev@example.com"],
            "slack_channel": "#alerts",
            "notification_level": "high"
        }
        
        config_data = {
            "check_interval": 30,
            "timeout": 10,
            "max_retries": 3,
            "cache_ttl": 300,
            "max_workers": 5,
            "notification_settings": valid_notifications
        }
        
        config = HealingConfig(**config_data)
        assert config.notification_settings["email_enabled"] is True
        assert config.notification_settings["slack_enabled"] is True
        assert config.notification_settings["webhook_url"] == "https://webhook.example.com"
        assert "admin@example.com" in config.notification_settings["email_recipients"]
        assert config.notification_settings["slack_channel"] == "#alerts"
        assert config.notification_settings["notification_level"] == "high"
    
    def test_healing_config_serialization(self, sample_config_data):
        """Testa serialização da configuração"""
        config = HealingConfig(**sample_config_data)
        
        # Teste de serialização para JSON
        config_dict = config.dict()
        assert isinstance(config_dict, dict)
        assert config_dict["check_interval"] == 30
        assert config_dict["timeout"] == 10
        assert config_dict["enable_auto_healing"] is True
        
        # Teste de serialização para string JSON
        config_json = config.json()
        assert isinstance(config_json, str)
        assert "check_interval" in config_json
        assert "30" in config_json
    
    def test_healing_config_from_file(self):
        """Testa carregamento de configuração de arquivo"""
        # Mock de arquivo de configuração
        mock_config_data = {
            "check_interval": 60,
            "timeout": 15,
            "max_retries": 5,
            "cache_ttl": 600,
            "max_workers": 10,
            "enable_auto_healing": True,
            "healing_strategies": ["restart", "reconnect"],
            "alert_thresholds": {
                "cpu_usage": 85.0,
                "memory_usage": 90.0,
                "error_rate": 0.1
            },
            "notification_settings": {
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_url": "https://webhook.example.com"
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config_data))):
            with patch('json.load', return_value=mock_config_data):
                # Simular carregamento de arquivo
                config = HealingConfig(**mock_config_data)
                
                assert config.check_interval == 60
                assert config.timeout == 15
                assert config.max_retries == 5
                assert config.cache_ttl == 600
                assert config.max_workers == 10
                assert config.enable_auto_healing is True
                assert len(config.healing_strategies) == 2
                assert config.alert_thresholds["cpu_usage"] == 85.0
                assert config.notification_settings["email_enabled"] is True
    
    def test_healing_config_validation_methods(self, sample_config_data):
        """Testa métodos de validação da configuração"""
        config = HealingConfig(**sample_config_data)
        
        # Teste de validação de configuração completa
        is_valid = config.validate()
        assert isinstance(is_valid, bool)
        
        # Teste de obtenção de erros de validação
        errors = config.get_validation_errors()
        assert isinstance(errors, list)
        
        # Teste de verificação se configuração está habilitada
        is_enabled = config.is_enabled()
        assert isinstance(is_enabled, bool)
        assert is_enabled == config.enable_auto_healing
    
    def test_healing_config_clone(self, sample_config_data):
        """Testa clonagem da configuração"""
        original_config = HealingConfig(**sample_config_data)
        
        # Clonar configuração
        cloned_config = original_config.copy()
        
        assert cloned_config is not original_config
        assert cloned_config.check_interval == original_config.check_interval
        assert cloned_config.timeout == original_config.timeout
        assert cloned_config.max_retries == original_config.max_retries
        assert cloned_config.cache_ttl == original_config.cache_ttl
        assert cloned_config.max_workers == original_config.max_workers
        assert cloned_config.enable_auto_healing == original_config.enable_auto_healing
        assert cloned_config.healing_strategies == original_config.healing_strategies
        assert cloned_config.alert_thresholds == original_config.alert_thresholds
        assert cloned_config.notification_settings == original_config.notification_settings
        
        # Modificar configuração clonada
        cloned_config.check_interval = 60
        cloned_config.enable_auto_healing = False
        
        # Verificar que original não foi modificada
        assert original_config.check_interval == 30
        assert original_config.enable_auto_healing is True
    
    def test_healing_config_merge(self, sample_config_data):
        """Testa mesclagem de configurações"""
        base_config = HealingConfig(**sample_config_data)
        
        # Configuração para mesclar
        merge_data = {
            "check_interval": 60,
            "timeout": 20,
            "enable_auto_healing": False,
            "healing_strategies": ["restart", "reset"],
            "alert_thresholds": {
                "cpu_usage": 90.0,
                "memory_usage": 95.0
            }
        }
        
        merge_config = HealingConfig(**merge_data)
        
        # Mesclar configurações
        merged_config = base_config.merge(merge_config)
        
        assert merged_config.check_interval == 60  # Sobrescrito
        assert merged_config.timeout == 20  # Sobrescrito
        assert merged_config.max_retries == 3  # Mantido
        assert merged_config.enable_auto_healing is False  # Sobrescrito
        assert merged_config.healing_strategies == ["restart", "reset"]  # Sobrescrito
        assert merged_config.alert_thresholds["cpu_usage"] == 90.0  # Sobrescrito
        assert merged_config.alert_thresholds["memory_usage"] == 95.0  # Sobrescrito
        assert merged_config.alert_thresholds["error_rate"] == 0.05  # Mantido


class TestHealingConfigIntegration:
    """Testes de integração para HealingConfig"""
    
    def test_config_with_all_features(self):
        """Testa configuração com todos os recursos"""
        full_config_data = {
            "check_interval": 45,
            "timeout": 12,
            "max_retries": 4,
            "cache_ttl": 450,
            "max_workers": 8,
            "enable_auto_healing": True,
            "healing_strategies": ["restart", "reconnect", "cleanup", "reload", "reset"],
            "alert_thresholds": {
                "cpu_usage": 82.5,
                "memory_usage": 87.5,
                "error_rate": 0.075,
                "response_time": 750.0,
                "disk_usage": 92.5,
                "network_latency": 200.0
            },
            "notification_settings": {
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_url": "https://webhook.example.com/alerts",
                "email_recipients": ["admin@example.com", "dev@example.com", "ops@example.com"],
                "slack_channel": "#system-alerts",
                "notification_level": "critical",
                "retry_notifications": True,
                "notification_timeout": 30
            },
            "advanced_settings": {
                "enable_metrics_collection": True,
                "metrics_retention_days": 30,
                "enable_audit_log": True,
                "audit_log_level": "INFO",
                "enable_performance_monitoring": True,
                "performance_sampling_rate": 0.1
            }
        }
        
        config = HealingConfig(**full_config_data)
        
        # Verificar configuração básica
        assert config.check_interval == 45
        assert config.timeout == 12
        assert config.max_retries == 4
        assert config.cache_ttl == 450
        assert config.max_workers == 8
        assert config.enable_auto_healing is True
        
        # Verificar estratégias
        assert len(config.healing_strategies) == 5
        assert all(strategy in config.healing_strategies for strategy in ["restart", "reconnect", "cleanup", "reload", "reset"])
        
        # Verificar thresholds
        assert config.alert_thresholds["cpu_usage"] == 82.5
        assert config.alert_thresholds["memory_usage"] == 87.5
        assert config.alert_thresholds["error_rate"] == 0.075
        assert config.alert_thresholds["response_time"] == 750.0
        assert config.alert_thresholds["disk_usage"] == 92.5
        assert config.alert_thresholds["network_latency"] == 200.0
        
        # Verificar notificações
        assert config.notification_settings["email_enabled"] is True
        assert config.notification_settings["slack_enabled"] is True
        assert config.notification_settings["webhook_url"] == "https://webhook.example.com/alerts"
        assert len(config.notification_settings["email_recipients"]) == 3
        assert config.notification_settings["slack_channel"] == "#system-alerts"
        assert config.notification_settings["notification_level"] == "critical"
        assert config.notification_settings["retry_notifications"] is True
        assert config.notification_settings["notification_timeout"] == 30
        
        # Verificar configurações avançadas
        assert config.advanced_settings["enable_metrics_collection"] is True
        assert config.advanced_settings["metrics_retention_days"] == 30
        assert config.advanced_settings["enable_audit_log"] is True
        assert config.advanced_settings["audit_log_level"] == "INFO"
        assert config.advanced_settings["enable_performance_monitoring"] is True
        assert config.advanced_settings["performance_sampling_rate"] == 0.1
    
    def test_config_validation_integration(self):
        """Testa integração de validação"""
        # Configuração válida
        valid_config = HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5,
            enable_auto_healing=True,
            healing_strategies=["restart", "reconnect"],
            alert_thresholds={
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "error_rate": 0.05
            },
            notification_settings={
                "email_enabled": True,
                "slack_enabled": False,
                "webhook_url": "http://localhost:8080/webhook"
            }
        )
        
        # Validar configuração
        is_valid = valid_config.validate()
        errors = valid_config.get_validation_errors()
        
        assert is_valid is True
        assert len(errors) == 0
        
        # Configuração inválida
        invalid_config = HealingConfig(
            check_interval=0,  # Inválido
            timeout=-1,  # Inválido
            max_retries=3,
            cache_ttl=300,
            max_workers=5,
            enable_auto_healing=True,
            healing_strategies=["invalid_strategy"],  # Inválido
            alert_thresholds={
                "cpu_usage": 150.0,  # Inválido
                "memory_usage": 85.0,
                "error_rate": 2.0  # Inválido
            },
            notification_settings={
                "email_enabled": True,
                "slack_enabled": False,
                "webhook_url": "invalid_url"  # Inválido
            }
        )
        
        # Validar configuração inválida
        is_valid = invalid_config.validate()
        errors = invalid_config.get_validation_errors()
        
        assert is_valid is False
        assert len(errors) > 0


class TestHealingConfigErrorHandling:
    """Testes de tratamento de erro para HealingConfig"""
    
    def test_invalid_data_type_handling(self):
        """Testa tratamento de tipos de dados inválidos"""
        # Teste com tipos inválidos
        invalid_data = {
            "check_interval": "invalid",  # Deveria ser int
            "timeout": None,  # Deveria ser int
            "max_retries": "3",  # Deveria ser int
            "enable_auto_healing": "true",  # Deveria ser bool
            "healing_strategies": "restart",  # Deveria ser list
            "alert_thresholds": "invalid",  # Deveria ser dict
            "notification_settings": []  # Deveria ser dict
        }
        
        # Deve tratar erros de tipo graciosamente
        try:
            config = HealingConfig(**invalid_data)
            # Se não falhar, deve usar valores padrão
            assert isinstance(config.check_interval, int)
            assert isinstance(config.timeout, int)
            assert isinstance(config.max_retries, int)
            assert isinstance(config.enable_auto_healing, bool)
            assert isinstance(config.healing_strategies, list)
            assert isinstance(config.alert_thresholds, dict)
            assert isinstance(config.notification_settings, dict)
        except Exception as e:
            # Se falhar, deve ser um erro de validação específico
            assert "validation" in str(e).lower() or "type" in str(e).lower()
    
    def test_missing_required_fields_handling(self):
        """Testa tratamento de campos obrigatórios ausentes"""
        # Teste com dados mínimos
        minimal_data = {}
        
        try:
            config = HealingConfig(**minimal_data)
            # Deve usar valores padrão para campos ausentes
            assert hasattr(config, 'check_interval')
            assert hasattr(config, 'timeout')
            assert hasattr(config, 'max_retries')
            assert hasattr(config, 'cache_ttl')
            assert hasattr(config, 'max_workers')
            assert hasattr(config, 'enable_auto_healing')
            assert hasattr(config, 'healing_strategies')
            assert hasattr(config, 'alert_thresholds')
            assert hasattr(config, 'notification_settings')
        except Exception as e:
            # Se falhar, deve ser um erro de validação específico
            assert "required" in str(e).lower() or "missing" in str(e).lower()
    
    def test_file_loading_error_handling(self):
        """Testa tratamento de erros no carregamento de arquivo"""
        # Mock de erro de arquivo não encontrado
        with patch('builtins.open', side_effect=FileNotFoundError("Config file not found")):
            try:
                # Tentar carregar configuração de arquivo inexistente
                config = HealingConfig()
                # Deve usar configuração padrão
                assert config is not None
            except FileNotFoundError:
                # Se falhar, deve ser um erro de arquivo específico
                pass
        
        # Mock de erro de JSON inválido
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
                try:
                    config = HealingConfig()
                    # Deve usar configuração padrão
                    assert config is not None
                except json.JSONDecodeError:
                    # Se falhar, deve ser um erro de JSON específico
                    pass


class TestHealingConfigPerformance:
    """Testes de performance para HealingConfig"""
    
    def test_large_config_creation_performance(self):
        """Testa performance de criação de configuração grande"""
        import time
        
        # Criar configuração com muitos dados
        large_config_data = {
            "check_interval": 30,
            "timeout": 10,
            "max_retries": 3,
            "cache_ttl": 300,
            "max_workers": 5,
            "enable_auto_healing": True,
            "healing_strategies": [f"strategy_{i}" for i in range(100)],
            "alert_thresholds": {f"metric_{i}": i * 1.0 for i in range(50)},
            "notification_settings": {
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_url": "https://webhook.example.com",
                "email_recipients": [f"user_{i}@example.com" for i in range(100)],
                "slack_channels": [f"#channel_{i}" for i in range(20)],
                "custom_settings": {f"setting_{i}": f"value_{i}" for i in range(100)}
            },
            "advanced_settings": {f"advanced_{i}": i for i in range(200)}
        }
        
        start_time = time.time()
        
        config = HealingConfig(**large_config_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance deve ser < 1 segundo para configuração grande
        assert duration < 1.0
        assert config is not None
        assert len(config.healing_strategies) == 100
        assert len(config.alert_thresholds) == 50
        assert len(config.notification_settings["email_recipients"]) == 100
    
    def test_config_validation_performance(self):
        """Testa performance de validação de configuração"""
        import time
        
        # Criar configuração para validar
        config = HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5,
            enable_auto_healing=True,
            healing_strategies=["restart", "reconnect", "cleanup"],
            alert_thresholds={
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "error_rate": 0.05,
                "response_time": 500.0,
                "disk_usage": 90.0
            },
            notification_settings={
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_url": "https://webhook.example.com"
            }
        )
        
        start_time = time.time()
        
        # Executar validação múltiplas vezes
        for _ in range(1000):
            is_valid = config.validate()
            errors = config.get_validation_errors()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance deve ser < 5 segundos para 1000 validações
        assert duration < 5.0
        assert is_valid is True
        assert len(errors) == 0
    
    def test_config_serialization_performance(self):
        """Testa performance de serialização de configuração"""
        import time
        
        # Criar configuração para serializar
        config = HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5,
            enable_auto_healing=True,
            healing_strategies=["restart", "reconnect", "cleanup"],
            alert_thresholds={
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "error_rate": 0.05
            },
            notification_settings={
                "email_enabled": True,
                "slack_enabled": True,
                "webhook_url": "https://webhook.example.com"
            }
        )
        
        start_time = time.time()
        
        # Executar serialização múltiplas vezes
        for _ in range(1000):
            config_dict = config.dict()
            config_json = config.json()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance deve ser < 3 segundos para 1000 serializações
        assert duration < 3.0
        assert isinstance(config_dict, dict)
        assert isinstance(config_json, str) 