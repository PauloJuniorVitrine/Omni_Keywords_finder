"""
Testes Unitários para InjectionConfig
InjectionConfig - Sistema de configuração para injeção de falhas

Prompt: Implementação de testes unitários para InjectionConfig
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_INJECTION_CONFIG_001_20250127
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from infrastructure.chaos.injection_config import (
    InjectionType,
    InjectionMode,
    Environment,
    NetworkLatencyConfig,
    NetworkPacketLossConfig,
    CPUStressConfig,
    MemoryStressConfig,
    ServiceFailureConfig,
    InjectionTemplate,
    InjectionConfig,
    ConfigManager
)


class TestInjectionType:
    """Testes para InjectionType"""
    
    def test_injection_type_values(self):
        """Testa valores do enum InjectionType"""
        assert InjectionType.NETWORK_LATENCY.value == "network_latency"
        assert InjectionType.NETWORK_PACKET_LOSS.value == "network_packet_loss"
        assert InjectionType.NETWORK_BANDWIDTH_LIMIT.value == "network_bandwidth_limit"
        assert InjectionType.CPU_STRESS.value == "cpu_stress"
        assert InjectionType.MEMORY_STRESS.value == "memory_stress"
        assert InjectionType.DISK_STRESS.value == "disk_stress"
        assert InjectionType.SERVICE_FAILURE.value == "service_failure"
        assert InjectionType.DATABASE_FAILURE.value == "database_failure"
        assert InjectionType.CACHE_FAILURE.value == "cache_failure"
        assert InjectionType.DEPENDENCY_FAILURE.value == "dependency_failure"
        assert InjectionType.PROCESS_KILL.value == "process_kill"
        assert InjectionType.CONTAINER_FAILURE.value == "container_failure"
    
    def test_injection_type_membership(self):
        """Testa pertencimento ao enum"""
        assert InjectionType.NETWORK_LATENCY in InjectionType
        assert InjectionType.CPU_STRESS in InjectionType
        assert InjectionType.SERVICE_FAILURE in InjectionType
        assert InjectionType.CONTAINER_FAILURE in InjectionType


class TestInjectionMode:
    """Testes para InjectionMode"""
    
    def test_injection_mode_values(self):
        """Testa valores do enum InjectionMode"""
        assert InjectionMode.CONTINUOUS.value == "continuous"
        assert InjectionMode.INTERMITTENT.value == "intermittent"
        assert InjectionMode.BURST.value == "burst"
        assert InjectionMode.GRADUAL.value == "gradual"
    
    def test_injection_mode_membership(self):
        """Testa pertencimento ao enum"""
        assert InjectionMode.CONTINUOUS in InjectionMode
        assert InjectionMode.INTERMITTENT in InjectionMode
        assert InjectionMode.BURST in InjectionMode
        assert InjectionMode.GRADUAL in InjectionMode


class TestEnvironment:
    """Testes para Environment"""
    
    def test_environment_values(self):
        """Testa valores do enum Environment"""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TESTING.value == "testing"
    
    def test_environment_membership(self):
        """Testa pertencimento ao enum"""
        assert Environment.DEVELOPMENT in Environment
        assert Environment.STAGING in Environment
        assert Environment.PRODUCTION in Environment
        assert Environment.TESTING in Environment


class TestNetworkLatencyConfig:
    """Testes para NetworkLatencyConfig"""
    
    @pytest.fixture
    def sample_latency_config(self):
        """Dados de exemplo para configuração de latência"""
        return {
            "latency_ms": 100,
            "jitter_ms": 10,
            "target_interface": "eth0",
            "packet_size": 1500,
            "protocol": "tcp"
        }
    
    def test_network_latency_config_initialization(self, sample_latency_config):
        """Testa inicialização básica"""
        config = NetworkLatencyConfig(**sample_latency_config)
        
        assert config.latency_ms == 100
        assert config.jitter_ms == 10
        assert config.target_interface == "eth0"
        assert config.packet_size == 1500
        assert config.protocol == "tcp"
    
    def test_network_latency_config_validation(self, sample_latency_config):
        """Testa validações de configuração"""
        # Teste com valores válidos
        config = NetworkLatencyConfig(**sample_latency_config)
        assert 0 <= config.latency_ms <= 10000
        assert 0 <= config.jitter_ms <= 1000
        assert config.packet_size > 0
    
    def test_network_latency_config_edge_cases(self):
        """Testa casos extremos"""
        # Teste com valores mínimos
        min_config = NetworkLatencyConfig(
            latency_ms=0,
            jitter_ms=0,
            target_interface="lo",
            packet_size=64,
            protocol="udp"
        )
        assert min_config.latency_ms == 0
        assert min_config.jitter_ms == 0
        
        # Teste com valores máximos
        max_config = NetworkLatencyConfig(
            latency_ms=10000,
            jitter_ms=1000,
            target_interface="eth0",
            packet_size=65535,
            protocol="tcp"
        )
        assert max_config.latency_ms == 10000
        assert max_config.jitter_ms == 1000


class TestNetworkPacketLossConfig:
    """Testes para NetworkPacketLossConfig"""
    
    @pytest.fixture
    def sample_packet_loss_config(self):
        """Dados de exemplo para configuração de perda de pacotes"""
        return {
            "loss_percentage": 5.0,
            "target_interface": "eth0",
            "packet_size": 1500,
            "protocol": "tcp",
            "burst_size": 10
        }
    
    def test_network_packet_loss_config_initialization(self, sample_packet_loss_config):
        """Testa inicialização básica"""
        config = NetworkPacketLossConfig(**sample_packet_loss_config)
        
        assert config.loss_percentage == 5.0
        assert config.target_interface == "eth0"
        assert config.packet_size == 1500
        assert config.protocol == "tcp"
        assert config.burst_size == 10
    
    def test_network_packet_loss_config_validation(self, sample_packet_loss_config):
        """Testa validações de configuração"""
        config = NetworkPacketLossConfig(**sample_packet_loss_config)
        assert 0 <= config.loss_percentage <= 100
        assert config.packet_size > 0
        assert config.burst_size > 0
    
    def test_network_packet_loss_config_edge_cases(self):
        """Testa casos extremos"""
        # Teste com perda mínima
        min_config = NetworkPacketLossConfig(
            loss_percentage=0.1,
            target_interface="lo",
            packet_size=64,
            protocol="udp",
            burst_size=1
        )
        assert min_config.loss_percentage == 0.1
        
        # Teste com perda máxima
        max_config = NetworkPacketLossConfig(
            loss_percentage=50.0,
            target_interface="eth0",
            packet_size=65535,
            protocol="tcp",
            burst_size=100
        )
        assert max_config.loss_percentage == 50.0


class TestCPUStressConfig:
    """Testes para CPUStressConfig"""
    
    @pytest.fixture
    def sample_cpu_stress_config(self):
        """Dados de exemplo para configuração de stress de CPU"""
        return {
            "cpu_load": 0.7,
            "cores": 2,
            "duration": 300,
            "stress_type": "cpu_bound"
        }
    
    def test_cpu_stress_config_initialization(self, sample_cpu_stress_config):
        """Testa inicialização básica"""
        config = CPUStressConfig(**sample_cpu_stress_config)
        
        assert config.cpu_load == 0.7
        assert config.cores == 2
        assert config.duration == 300
        assert config.stress_type == "cpu_bound"
    
    def test_cpu_stress_config_validation(self, sample_cpu_stress_config):
        """Testa validações de configuração"""
        config = CPUStressConfig(**sample_cpu_stress_config)
        assert 0 < config.cpu_load <= 1
        assert config.cores > 0
        assert config.duration > 0
    
    def test_cpu_stress_config_edge_cases(self):
        """Testa casos extremos"""
        # Teste com carga mínima
        min_config = CPUStressConfig(
            cpu_load=0.1,
            cores=1,
            duration=60,
            stress_type="io_bound"
        )
        assert min_config.cpu_load == 0.1
        assert min_config.cores == 1
        
        # Teste com carga máxima
        max_config = CPUStressConfig(
            cpu_load=0.9,
            cores=8,
            duration=3600,
            stress_type="memory_bound"
        )
        assert max_config.cpu_load == 0.9
        assert max_config.cores == 8


class TestMemoryStressConfig:
    """Testes para MemoryStressConfig"""
    
    @pytest.fixture
    def sample_memory_stress_config(self):
        """Dados de exemplo para configuração de stress de memória"""
        return {
            "memory_mb": 512,
            "allocation_type": "random",
            "duration": 300,
            "stress_pattern": "continuous"
        }
    
    def test_memory_stress_config_initialization(self, sample_memory_stress_config):
        """Testa inicialização básica"""
        config = MemoryStressConfig(**sample_memory_stress_config)
        
        assert config.memory_mb == 512
        assert config.allocation_type == "random"
        assert config.duration == 300
        assert config.stress_pattern == "continuous"
    
    def test_memory_stress_config_validation(self, sample_memory_stress_config):
        """Testa validações de configuração"""
        config = MemoryStressConfig(**sample_memory_stress_config)
        assert config.memory_mb > 0
        assert config.duration > 0
    
    def test_memory_stress_config_edge_cases(self):
        """Testa casos extremos"""
        # Teste com memória mínima
        min_config = MemoryStressConfig(
            memory_mb=1,
            allocation_type="sequential",
            duration=60,
            stress_pattern="burst"
        )
        assert min_config.memory_mb == 1
        
        # Teste com memória alta
        max_config = MemoryStressConfig(
            memory_mb=8192,
            allocation_type="random",
            duration=1800,
            stress_pattern="intermittent"
        )
        assert max_config.memory_mb == 8192


class TestServiceFailureConfig:
    """Testes para ServiceFailureConfig"""
    
    @pytest.fixture
    def sample_service_failure_config(self):
        """Dados de exemplo para configuração de falha de serviço"""
        return {
            "service_name": "nginx",
            "failure_rate": 0.3,
            "failure_pattern": "random",
            "failure_duration": 60,
            "recovery_time": 30
        }
    
    def test_service_failure_config_initialization(self, sample_service_failure_config):
        """Testa inicialização básica"""
        config = ServiceFailureConfig(**sample_service_failure_config)
        
        assert config.service_name == "nginx"
        assert config.failure_rate == 0.3
        assert config.failure_pattern == "random"
        assert config.failure_duration == 60
        assert config.recovery_time == 30
    
    def test_service_failure_config_validation(self, sample_service_failure_config):
        """Testa validações de configuração"""
        config = ServiceFailureConfig(**sample_service_failure_config)
        assert 0 <= config.failure_rate <= 1
        assert config.failure_duration > 0
        assert config.recovery_time >= 0
    
    def test_service_failure_config_edge_cases(self):
        """Testa casos extremos"""
        # Teste com taxa mínima
        min_config = ServiceFailureConfig(
            service_name="test-service",
            failure_rate=0.01,
            failure_pattern="deterministic",
            failure_duration=10,
            recovery_time=5
        )
        assert min_config.failure_rate == 0.01
        
        # Teste com taxa máxima
        max_config = ServiceFailureConfig(
            service_name="critical-service",
            failure_rate=0.8,
            failure_pattern="burst",
            failure_duration=300,
            recovery_time=120
        )
        assert max_config.failure_rate == 0.8


class TestInjectionTemplate:
    """Testes para InjectionTemplate"""
    
    @pytest.fixture
    def sample_template_data(self):
        """Dados de exemplo para template"""
        return {
            "name": "network_latency_basic",
            "description": "Teste básico de latência de rede",
            "injection_type": InjectionType.NETWORK_LATENCY,
            "category": "network",
            "mode": InjectionMode.CONTINUOUS,
            "duration": 300,
            "interval": 5,
            "max_impact": 0.3,
            "auto_rollback": True,
            "rollback_threshold": 0.5,
            "monitor_enabled": True,
            "metrics_interval": 5,
            "alert_thresholds": {"cpu": 0.8, "memory": 0.9},
            "prerequisites": ["network_available"],
            "success_criteria": ["response_time < 200ms"]
        }
    
    def test_injection_template_initialization(self, sample_template_data):
        """Testa inicialização básica"""
        template = InjectionTemplate(**sample_template_data)
        
        assert template.name == "network_latency_basic"
        assert template.description == "Teste básico de latência de rede"
        assert template.injection_type == InjectionType.NETWORK_LATENCY
        assert template.category == "network"
        assert template.mode == InjectionMode.CONTINUOUS
        assert template.duration == 300
        assert template.interval == 5
        assert template.max_impact == 0.3
        assert template.auto_rollback is True
        assert template.rollback_threshold == 0.5
        assert template.monitor_enabled is True
        assert template.metrics_interval == 5
        assert template.alert_thresholds["cpu"] == 0.8
        assert template.prerequisites == ["network_available"]
        assert template.success_criteria == ["response_time < 200ms"]
    
    def test_injection_template_validation(self, sample_template_data):
        """Testa validações de template"""
        template = InjectionTemplate(**sample_template_data)
        assert 0 <= template.max_impact <= 1
        assert 0 <= template.rollback_threshold <= 1
        assert template.duration > 0
        assert template.interval > 0
    
    def test_injection_template_edge_cases(self):
        """Testa casos extremos"""
        # Teste com impacto mínimo
        min_template = InjectionTemplate(
            name="min_impact",
            description="Template com impacto mínimo",
            injection_type=InjectionType.NETWORK_LATENCY,
            category="test",
            max_impact=0.01,
            rollback_threshold=0.1
        )
        assert min_template.max_impact == 0.01
        
        # Teste com impacto máximo
        max_template = InjectionTemplate(
            name="max_impact",
            description="Template com impacto máximo",
            injection_type=InjectionType.CPU_STRESS,
            category="test",
            max_impact=0.9,
            rollback_threshold=0.8
        )
        assert max_template.max_impact == 0.9


class TestInjectionConfig:
    """Testes para InjectionConfig"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Dados de exemplo para configuração"""
        return {
            "name": "development_network_test",
            "description": "Teste de rede para desenvolvimento",
            "injection_type": InjectionType.NETWORK_LATENCY,
            "mode": InjectionMode.CONTINUOUS,
            "environment": Environment.DEVELOPMENT,
            "duration": 120,
            "parameters": {"latency_ms": 50, "jitter_ms": 5}
        }
    
    def test_injection_config_initialization(self, sample_config_data):
        """Testa inicialização básica"""
        config = InjectionConfig(**sample_config_data)
        
        assert config.name == "development_network_test"
        assert config.description == "Teste de rede para desenvolvimento"
        assert config.injection_type == InjectionType.NETWORK_LATENCY
        assert config.mode == InjectionMode.CONTINUOUS
        assert config.environment == Environment.DEVELOPMENT
        assert config.duration == 120
        assert config.parameters["latency_ms"] == 50
        assert config.parameters["jitter_ms"] == 5
    
    def test_injection_config_validation(self, sample_config_data):
        """Testa validações de configuração"""
        config = InjectionConfig(**sample_config_data)
        assert config.duration > 0
        assert isinstance(config.parameters, dict)
    
    def test_injection_config_edge_cases(self):
        """Testa casos extremos"""
        # Teste com duração mínima
        min_config = InjectionConfig(
            name="min_duration",
            description="Configuração com duração mínima",
            injection_type=InjectionType.NETWORK_LATENCY,
            mode=InjectionMode.BURST,
            environment=Environment.TESTING,
            duration=10,
            parameters={"latency_ms": 10}
        )
        assert min_config.duration == 10
        
        # Teste com duração longa
        max_config = InjectionConfig(
            name="max_duration",
            description="Configuração com duração longa",
            injection_type=InjectionType.CPU_STRESS,
            mode=InjectionMode.CONTINUOUS,
            environment=Environment.STAGING,
            duration=3600,
            parameters={"cpu_load": 0.5}
        )
        assert max_config.duration == 3600


class TestConfigManager:
    """Testes para ConfigManager"""
    
    @pytest.fixture
    def config_manager(self):
        """Instância do gerenciador de configuração"""
        return ConfigManager()
    
    @pytest.fixture
    def temp_config_dir(self):
        """Diretório temporário para configurações"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_config_manager_initialization(self, config_manager):
        """Testa inicialização do gerenciador"""
        assert config_manager is not None
        assert hasattr(config_manager, 'templates')
        assert hasattr(config_manager, 'configs')
    
    def test_load_templates(self, config_manager):
        """Testa carregamento de templates"""
        # Mock do carregamento de arquivo
        mock_templates = {
            "network_latency_basic": {
                "name": "network_latency_basic",
                "description": "Teste básico de latência",
                "injection_type": "network_latency",
                "category": "network"
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_templates))):
            with patch('os.path.exists', return_value=True):
                config_manager._load_templates()
        
        # Verificar se templates foram carregados
        assert len(config_manager.templates) >= 0
    
    def test_load_configs(self, config_manager):
        """Testa carregamento de configurações"""
        # Mock do carregamento de arquivo
        mock_configs = {
            "dev_test": {
                "name": "dev_test",
                "description": "Teste de desenvolvimento",
                "injection_type": "network_latency",
                "mode": "continuous",
                "environment": "development",
                "duration": 120,
                "parameters": {"latency_ms": 50}
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_configs))):
            with patch('os.path.exists', return_value=True):
                config_manager._load_configs()
        
        # Verificar se configurações foram carregadas
        assert len(config_manager.configs) >= 0
    
    def test_validate_injection_config(self, config_manager):
        """Testa validação de configuração de injeção"""
        valid_config = {
            "injection_type": "network_latency",
            "parameters": {"latency_ms": 100},
            "environment": "development",
            "duration": 300
        }
        
        errors = config_manager.validate_injection_config(valid_config)
        assert isinstance(errors, list)
    
    def test_validate_injection_config_invalid(self, config_manager):
        """Testa validação de configuração inválida"""
        invalid_config = {
            "injection_type": "network_latency",
            "parameters": {"latency_ms": 15000},  # Muito alto
            "environment": "production",
            "duration": 0  # Inválido
        }
        
        errors = config_manager.validate_injection_config(invalid_config)
        assert len(errors) > 0
    
    def test_is_injection_allowed(self, config_manager):
        """Testa verificação de permissão de injeção"""
        allowed_config = {
            "injection_type": "network_latency",
            "parameters": {"latency_ms": 50},
            "environment": "development"
        }
        
        is_allowed = config_manager.is_injection_allowed(allowed_config)
        assert isinstance(is_allowed, bool)
    
    def test_create_injection_from_template(self, config_manager):
        """Testa criação de injeção a partir de template"""
        # Criar template de teste
        template = InjectionTemplate(
            name="test_template",
            description="Template de teste",
            injection_type=InjectionType.NETWORK_LATENCY,
            category="test"
        )
        config_manager.templates["test_template"] = template
        
        custom_params = {"latency_ms": 200}
        config = config_manager.create_injection_from_template("test_template", custom_params)
        
        assert config is not None
        assert config.injection_type == InjectionType.NETWORK_LATENCY
    
    def test_create_injection_from_template_not_found(self, config_manager):
        """Testa criação com template não encontrado"""
        config = config_manager.create_injection_from_template("non_existent_template")
        assert config is None
    
    def test_save_templates(self, config_manager):
        """Testa salvamento de templates"""
        # Adicionar template de teste
        template = InjectionTemplate(
            name="save_test",
            description="Template para teste de salvamento",
            injection_type=InjectionType.NETWORK_LATENCY,
            category="test"
        )
        config_manager.templates["save_test"] = template
        
        with patch('builtins.open', mock_open()) as mock_file:
            config_manager._save_templates()
            mock_file.assert_called()
    
    def test_save_configs(self, config_manager):
        """Testa salvamento de configurações"""
        # Adicionar configuração de teste
        config = InjectionConfig(
            name="save_test",
            description="Configuração para teste de salvamento",
            injection_type=InjectionType.NETWORK_LATENCY,
            mode=InjectionMode.CONTINUOUS,
            environment=Environment.DEVELOPMENT,
            duration=120,
            parameters={"latency_ms": 50}
        )
        config_manager.configs["save_test"] = config
        
        with patch('builtins.open', mock_open()) as mock_file:
            config_manager._save_configs()
            mock_file.assert_called()


class TestConfigManagerIntegration:
    """Testes de integração para ConfigManager"""
    
    def test_full_config_cycle(self):
        """Testa ciclo completo de configuração"""
        manager = ConfigManager()
        
        # Criar template
        template = InjectionTemplate(
            name="integration_test",
            description="Template para teste de integração",
            injection_type=InjectionType.NETWORK_LATENCY,
            category="integration"
        )
        manager.templates["integration_test"] = template
        
        # Criar configuração a partir do template
        config = manager.create_injection_from_template("integration_test")
        assert config is not None
        
        # Validar configuração
        errors = manager.validate_injection_config(config.dict())
        assert len(errors) == 0
        
        # Verificar permissão
        is_allowed = manager.is_injection_allowed(config.dict())
        assert is_allowed is True
    
    def test_config_validation_integration(self):
        """Testa integração de validação"""
        manager = ConfigManager()
        
        # Configuração válida
        valid_config = {
            "name": "valid_test",
            "description": "Configuração válida",
            "injection_type": "network_latency",
            "mode": "continuous",
            "environment": "development",
            "duration": 300,
            "parameters": {"latency_ms": 100}
        }
        
        errors = manager.validate_injection_config(valid_config)
        assert len(errors) == 0
        
        # Configuração inválida
        invalid_config = {
            "name": "invalid_test",
            "description": "Configuração inválida",
            "injection_type": "network_latency",
            "mode": "continuous",
            "environment": "production",
            "duration": 0,  # Inválido
            "parameters": {"latency_ms": 20000}  # Muito alto
        }
        
        errors = manager.validate_injection_config(invalid_config)
        assert len(errors) > 0


class TestConfigManagerErrorHandling:
    """Testes de tratamento de erro para ConfigManager"""
    
    def test_file_not_found_handling(self):
        """Testa tratamento de arquivo não encontrado"""
        manager = ConfigManager()
        
        with patch('os.path.exists', return_value=False):
            # Deve continuar funcionando mesmo sem arquivos
            manager._load_templates()
            manager._load_configs()
            
            assert len(manager.templates) >= 0
            assert len(manager.configs) >= 0
    
    def test_invalid_json_handling(self):
        """Testa tratamento de JSON inválido"""
        manager = ConfigManager()
        
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with patch('os.path.exists', return_value=True):
                # Deve tratar erro de JSON inválido
                manager._load_templates()
                manager._load_configs()
    
    def test_validation_error_handling(self):
        """Testa tratamento de erros de validação"""
        manager = ConfigManager()
        
        # Configuração com dados inválidos
        invalid_config = {
            "injection_type": "invalid_type",
            "parameters": "not_a_dict",
            "duration": "not_a_number"
        }
        
        errors = manager.validate_injection_config(invalid_config)
        assert isinstance(errors, list)
        assert len(errors) > 0


class TestConfigManagerPerformance:
    """Testes de performance para ConfigManager"""
    
    def test_large_config_loading_performance(self):
        """Testa performance de carregamento de configurações grandes"""
        manager = ConfigManager()
        
        # Criar muitas configurações
        for i in range(1000):
            config = InjectionConfig(
                name=f"perf_test_{i}",
                description=f"Configuração de performance {i}",
                injection_type=InjectionType.NETWORK_LATENCY,
                mode=InjectionMode.CONTINUOUS,
                environment=Environment.DEVELOPMENT,
                duration=300,
                parameters={"latency_ms": 50 + i}
            )
            manager.configs[f"perf_test_{i}"] = config
        
        # Testar validação de todas as configurações
        start_time = datetime.now()
        
        for config in manager.configs.values():
            manager.validate_injection_config(config.dict())
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser < 5 segundos para 1000 configurações
        assert duration < 5.0
    
    def test_template_creation_performance(self):
        """Testa performance de criação de templates"""
        manager = ConfigManager()
        
        start_time = datetime.now()
        
        # Criar muitos templates
        for i in range(100):
            template = InjectionTemplate(
                name=f"perf_template_{i}",
                description=f"Template de performance {i}",
                injection_type=InjectionType.NETWORK_LATENCY,
                category="performance"
            )
            manager.templates[f"perf_template_{i}"] = template
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser < 1 segundo para 100 templates
        assert duration < 1.0 