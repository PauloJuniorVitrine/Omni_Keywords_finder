"""
Testes Unitários para HealingStrategies
HealingStrategies - Estratégias de Auto-Cura para Serviços

Prompt: Implementação de testes unitários para HealingStrategies
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_HEALING_STRATEGIES_001_20250127
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.healing.healing_strategies import (
    HealingStrategy,
    ServiceRestartStrategy,
    ConnectionRecoveryStrategy,
    ResourceCleanupStrategy,
    ConfigurationReloadStrategy,
    HealingStrategyFactory,
    HealingResult
)
from infrastructure.healing.healing_config import HealingConfig
from infrastructure.healing.self_healing_service import ProblemReport, ProblemType


class TestHealingResult:
    """Testes para HealingResult"""
    
    @pytest.fixture
    def sample_healing_result_data(self):
        """Dados de exemplo para resultado de healing"""
        return {
            "success": True,
            "strategy_applied": "service_restart",
            "service_name": "test-service",
            "duration": 15.5,
            "attempts": 1,
            "message": "Service restarted successfully",
            "timestamp": datetime.now(timezone.utc),
            "details": {
                "restart_method": "systemctl",
                "health_check_passed": True,
                "recovery_time": 12.3
            }
        }
    
    def test_healing_result_initialization(self, sample_healing_result_data):
        """Testa inicialização básica"""
        result = HealingResult(**sample_healing_result_data)
        
        assert result.success is True
        assert result.strategy_applied == "service_restart"
        assert result.service_name == "test-service"
        assert result.duration == 15.5
        assert result.attempts == 1
        assert result.message == "Service restarted successfully"
        assert isinstance(result.timestamp, datetime)
        assert result.details["restart_method"] == "systemctl"
        assert result.details["health_check_passed"] is True
        assert result.details["recovery_time"] == 12.3
    
    def test_healing_result_validation(self, sample_healing_result_data):
        """Testa validações de resultado"""
        result = HealingResult(**sample_healing_result_data)
        
        # Validações básicas
        assert isinstance(result.success, bool)
        assert result.strategy_applied is not None
        assert result.service_name is not None
        assert result.duration >= 0
        assert result.attempts >= 0
        assert result.message is not None
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.details, dict)
    
    def test_healing_result_edge_cases(self):
        """Testa casos extremos"""
        # Teste com resultado de falha
        failure_data = {
            "success": False,
            "strategy_applied": "connection_recovery",
            "service_name": "failed-service",
            "duration": 0.0,
            "attempts": 3,
            "message": "Connection recovery failed",
            "timestamp": datetime.now(timezone.utc),
            "details": {
                "error": "Connection timeout",
                "max_attempts_reached": True
            }
        }
        result = HealingResult(**failure_data)
        assert result.success is False
        assert result.attempts == 3
        assert "failed" in result.message.lower()
        
        # Teste com resultado mínimo
        min_data = {
            "success": True,
            "strategy_applied": "minimal",
            "service_name": "min-service",
            "duration": 0.1,
            "attempts": 1,
            "message": "Minimal success",
            "timestamp": datetime.now(timezone.utc),
            "details": {}
        }
        result = HealingResult(**min_data)
        assert result.success is True
        assert result.duration == 0.1
        assert len(result.details) == 0


class TestHealingStrategy:
    """Testes para HealingStrategy (classe abstrata)"""
    
    @pytest.fixture
    def healing_config(self):
        """Configuração de healing para testes"""
        return HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5
        )
    
    def test_healing_strategy_initialization(self, healing_config):
        """Testa inicialização da estratégia base"""
        # Criar uma implementação concreta para teste
        class TestStrategy(HealingStrategy):
            async def apply(self, problem_report):
                return True
        
        strategy = TestStrategy(healing_config)
        
        assert strategy.config == healing_config
        assert strategy.attempt_count == 0
        assert strategy.last_attempt is None
        assert strategy.max_attempts == healing_config.max_retries
    
    def test_can_attempt_validation(self, healing_config):
        """Testa validação de tentativas permitidas"""
        class TestStrategy(HealingStrategy):
            async def apply(self, problem_report):
                return True
        
        strategy = TestStrategy(healing_config)
        
        # Deve permitir tentativa inicial
        assert strategy._can_attempt() is True
        
        # Simular tentativas até o limite
        for i in range(healing_config.max_retries):
            strategy._record_attempt()
        
        # Deve bloquear após exceder limite
        assert strategy._can_attempt() is False
    
    def test_record_attempt(self, healing_config):
        """Testa registro de tentativas"""
        class TestStrategy(HealingStrategy):
            async def apply(self, problem_report):
                return True
        
        strategy = TestStrategy(healing_config)
        
        initial_count = strategy.attempt_count
        initial_time = strategy.last_attempt
        
        strategy._record_attempt()
        
        assert strategy.attempt_count == initial_count + 1
        assert strategy.last_attempt is not None
        assert strategy.last_attempt > initial_time if initial_time else True


class TestServiceRestartStrategy:
    """Testes para ServiceRestartStrategy"""
    
    @pytest.fixture
    def healing_config(self):
        """Configuração de healing para testes"""
        return HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5
        )
    
    @pytest.fixture
    def restart_strategy(self, healing_config):
        """Instância da estratégia de restart"""
        return ServiceRestartStrategy(healing_config)
    
    @pytest.fixture
    def sample_problem_report(self):
        """Relatório de problema de exemplo"""
        return ProblemReport(
            service_name="test-service",
            problem_type=ProblemType.SERVICE_CRASH,
            severity="high",
            description="Service crashed",
            timestamp=datetime.now(timezone.utc),
            metrics={"cpu_usage": 95.0},
            context={"error": "crash"}
        )
    
    def test_service_restart_strategy_initialization(self, restart_strategy):
        """Testa inicialização da estratégia de restart"""
        assert restart_strategy is not None
        assert hasattr(restart_strategy, 'config')
        assert hasattr(restart_strategy, 'attempt_count')
        assert hasattr(restart_strategy, 'max_attempts')
    
    @pytest.mark.asyncio
    async def test_apply_service_restart_success(self, restart_strategy, sample_problem_report):
        """Testa aplicação bem-sucedida de restart"""
        # Mock das operações de restart
        with patch.object(restart_strategy, '_is_service_running', new_callable=AsyncMock) as mock_running:
            with patch.object(restart_strategy, '_restart_service', new_callable=AsyncMock) as mock_restart:
                with patch.object(restart_strategy, '_wait_for_service_ready', new_callable=AsyncMock) as mock_wait:
                    
                    mock_running.return_value = True
                    mock_restart.return_value = True
                    mock_wait.return_value = True
                    
                    result = await restart_strategy.apply(sample_problem_report)
                    
                    assert result is True
                    mock_running.assert_called_once_with("test-service")
                    mock_restart.assert_called_once_with("test-service")
                    mock_wait.assert_called_once_with("test-service")
    
    @pytest.mark.asyncio
    async def test_apply_service_restart_not_running(self, restart_strategy, sample_problem_report):
        """Testa restart quando serviço não está rodando"""
        with patch.object(restart_strategy, '_is_service_running', new_callable=AsyncMock) as mock_running:
            with patch.object(restart_strategy, '_start_service', new_callable=AsyncMock) as mock_start:
                with patch.object(restart_strategy, '_wait_for_service_ready', new_callable=AsyncMock) as mock_wait:
                    
                    mock_running.return_value = False
                    mock_start.return_value = True
                    mock_wait.return_value = True
                    
                    result = await restart_strategy.apply(sample_problem_report)
                    
                    assert result is True
                    mock_running.assert_called_once_with("test-service")
                    mock_start.assert_called_once_with("test-service")
                    mock_wait.assert_called_once_with("test-service")
    
    @pytest.mark.asyncio
    async def test_apply_service_restart_failure(self, restart_strategy, sample_problem_report):
        """Testa falha na aplicação de restart"""
        with patch.object(restart_strategy, '_is_service_running', new_callable=AsyncMock) as mock_running:
            with patch.object(restart_strategy, '_restart_service', new_callable=AsyncMock) as mock_restart:
                
                mock_running.return_value = True
                mock_restart.return_value = False
                
                result = await restart_strategy.apply(sample_problem_report)
                
                assert result is False
                mock_running.assert_called_once_with("test-service")
                mock_restart.assert_called_once_with("test-service")
    
    @pytest.mark.asyncio
    async def test_apply_service_restart_max_attempts(self, restart_strategy, sample_problem_report):
        """Testa limite de tentativas de restart"""
        # Simular tentativas até o limite
        for i in range(restart_strategy.max_attempts):
            restart_strategy._record_attempt()
        
        result = await restart_strategy.apply(sample_problem_report)
        
        assert result is False  # Deve falhar por limite de tentativas
    
    @pytest.mark.asyncio
    async def test_is_service_running(self, restart_strategy):
        """Testa verificação se serviço está rodando"""
        # Mock do psutil
        mock_process = Mock()
        mock_process.status.return_value = "running"
        
        with patch('psutil.process_iter', return_value=[mock_process]):
            with patch.object(mock_process, 'name', return_value="test-service"):
                result = await restart_strategy._is_service_running("test-service")
                assert result is True
    
    @pytest.mark.asyncio
    async def test_restart_service(self, restart_strategy):
        """Testa restart de serviço"""
        # Mock de subprocess
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await restart_strategy._restart_service("test-service")
            
            assert result is True
            mock_subprocess.assert_called()
    
    @pytest.mark.asyncio
    async def test_start_service(self, restart_strategy):
        """Testa início de serviço"""
        # Mock de subprocess
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await restart_strategy._start_service("test-service")
            
            assert result is True
            mock_subprocess.assert_called()
    
    @pytest.mark.asyncio
    async def test_wait_for_service_ready(self, restart_strategy):
        """Testa espera por serviço ficar pronto"""
        with patch.object(restart_strategy, '_check_service_health', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            result = await restart_strategy._wait_for_service_ready("test-service")
            
            assert result is True
            mock_health.assert_called()
    
    @pytest.mark.asyncio
    async def test_check_service_health(self, restart_strategy):
        """Testa verificação de saúde do serviço"""
        # Mock de aiohttp
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "healthy"})
        
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await restart_strategy._check_service_health("test-service")
            
            assert result is True
            mock_get.assert_called_once()


class TestConnectionRecoveryStrategy:
    """Testes para ConnectionRecoveryStrategy"""
    
    @pytest.fixture
    def healing_config(self):
        """Configuração de healing para testes"""
        return HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5
        )
    
    @pytest.fixture
    def recovery_strategy(self, healing_config):
        """Instância da estratégia de recuperação"""
        return ConnectionRecoveryStrategy(healing_config)
    
    @pytest.fixture
    def sample_problem_report(self):
        """Relatório de problema de exemplo"""
        return ProblemReport(
            service_name="database-service",
            problem_type=ProblemType.CONNECTION_ERROR,
            severity="medium",
            description="Database connection lost",
            timestamp=datetime.now(timezone.utc),
            metrics={"error_rate": 0.15},
            context={"connection_type": "database"}
        )
    
    def test_connection_recovery_strategy_initialization(self, recovery_strategy):
        """Testa inicialização da estratégia de recuperação"""
        assert recovery_strategy is not None
        assert hasattr(recovery_strategy, 'config')
        assert hasattr(recovery_strategy, 'attempt_count')
        assert hasattr(recovery_strategy, 'max_attempts')
    
    @pytest.mark.asyncio
    async def test_apply_connection_recovery_database(self, recovery_strategy, sample_problem_report):
        """Testa recuperação de conexão de banco de dados"""
        with patch.object(recovery_strategy, '_identify_connection_type', return_value="database"):
            with patch.object(recovery_strategy, '_recover_database_connection', new_callable=AsyncMock) as mock_db:
                mock_db.return_value = True
                
                result = await recovery_strategy.apply(sample_problem_report)
                
                assert result is True
                mock_db.assert_called_once_with("database-service")
    
    @pytest.mark.asyncio
    async def test_apply_connection_recovery_cache(self, recovery_strategy, sample_problem_report):
        """Testa recuperação de conexão de cache"""
        sample_problem_report.service_name = "cache-service"
        
        with patch.object(recovery_strategy, '_identify_connection_type', return_value="cache"):
            with patch.object(recovery_strategy, '_recover_cache_connection', new_callable=AsyncMock) as mock_cache:
                mock_cache.return_value = True
                
                result = await recovery_strategy.apply(sample_problem_report)
                
                assert result is True
                mock_cache.assert_called_once_with("cache-service")
    
    @pytest.mark.asyncio
    async def test_apply_connection_recovery_api(self, recovery_strategy, sample_problem_report):
        """Testa recuperação de conexão de API"""
        sample_problem_report.service_name = "api-service"
        
        with patch.object(recovery_strategy, '_identify_connection_type', return_value="api"):
            with patch.object(recovery_strategy, '_recover_api_connection', new_callable=AsyncMock) as mock_api:
                mock_api.return_value = True
                
                result = await recovery_strategy.apply(sample_problem_report)
                
                assert result is True
                mock_api.assert_called_once_with("api-service")
    
    @pytest.mark.asyncio
    async def test_apply_connection_recovery_generic(self, recovery_strategy, sample_problem_report):
        """Testa recuperação de conexão genérica"""
        with patch.object(recovery_strategy, '_identify_connection_type', return_value="unknown"):
            with patch.object(recovery_strategy, '_recover_generic_connection', new_callable=AsyncMock) as mock_generic:
                mock_generic.return_value = True
                
                result = await recovery_strategy.apply(sample_problem_report)
                
                assert result is True
                mock_generic.assert_called_once_with("database-service")
    
    @pytest.mark.asyncio
    async def test_apply_connection_recovery_failure(self, recovery_strategy, sample_problem_report):
        """Testa falha na recuperação de conexão"""
        with patch.object(recovery_strategy, '_identify_connection_type', return_value="database"):
            with patch.object(recovery_strategy, '_recover_database_connection', new_callable=AsyncMock) as mock_db:
                mock_db.return_value = False
                
                result = await recovery_strategy.apply(sample_problem_report)
                
                assert result is False
                mock_db.assert_called_once_with("database-service")
    
    def test_identify_connection_type(self, recovery_strategy):
        """Testa identificação do tipo de conexão"""
        # Teste para serviços de banco de dados
        assert recovery_strategy._identify_connection_type("database-service") == "database"
        assert recovery_strategy._identify_connection_type("postgres-service") == "database"
        assert recovery_strategy._identify_connection_type("mysql-service") == "database"
        
        # Teste para serviços de cache
        assert recovery_strategy._identify_connection_type("redis-service") == "cache"
        assert recovery_strategy._identify_connection_type("memcached-service") == "cache"
        
        # Teste para serviços de API
        assert recovery_strategy._identify_connection_type("api-gateway") == "api"
        assert recovery_strategy._identify_connection_type("rest-service") == "api"
        
        # Teste para serviços desconhecidos
        assert recovery_strategy._identify_connection_type("unknown-service") == "generic"
    
    @pytest.mark.asyncio
    async def test_recover_database_connection(self, recovery_strategy):
        """Testa recuperação de conexão de banco de dados"""
        # Mock de operações de banco de dados
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch.object(recovery_strategy, '_test_database_connection', new_callable=AsyncMock) as mock_test:
                mock_test.return_value = True
                
                result = await recovery_strategy._recover_database_connection("database-service")
                
                assert result is True
                mock_test.assert_called()
    
    @pytest.mark.asyncio
    async def test_recover_cache_connection(self, recovery_strategy):
        """Testa recuperação de conexão de cache"""
        # Mock de operações de cache
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch.object(recovery_strategy, '_test_cache_connection', new_callable=AsyncMock) as mock_test:
                mock_test.return_value = True
                
                result = await recovery_strategy._recover_cache_connection("cache-service")
                
                assert result is True
                mock_test.assert_called()
    
    @pytest.mark.asyncio
    async def test_recover_api_connection(self, recovery_strategy):
        """Testa recuperação de conexão de API"""
        # Mock de operações de API
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch.object(recovery_strategy, '_test_api_connection', new_callable=AsyncMock) as mock_test:
                mock_test.return_value = True
                
                result = await recovery_strategy._recover_api_connection("api-service")
                
                assert result is True
                mock_test.assert_called()
    
    @pytest.mark.asyncio
    async def test_recover_generic_connection(self, recovery_strategy):
        """Testa recuperação de conexão genérica"""
        # Mock de operações genéricas
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch.object(recovery_strategy, '_test_generic_connection', new_callable=AsyncMock) as mock_test:
                mock_test.return_value = True
                
                result = await recovery_strategy._recover_generic_connection("generic-service")
                
                assert result is True
                mock_test.assert_called()


class TestResourceCleanupStrategy:
    """Testes para ResourceCleanupStrategy"""
    
    @pytest.fixture
    def healing_config(self):
        """Configuração de healing para testes"""
        return HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5
        )
    
    @pytest.fixture
    def cleanup_strategy(self, healing_config):
        """Instância da estratégia de limpeza"""
        return ResourceCleanupStrategy(healing_config)
    
    @pytest.fixture
    def sample_problem_report(self):
        """Relatório de problema de exemplo"""
        return ProblemReport(
            service_name="memory-service",
            problem_type=ProblemType.MEMORY_LEAK,
            severity="high",
            description="Memory leak detected",
            timestamp=datetime.now(timezone.utc),
            metrics={"memory_usage": 95.0},
            context={"leak_type": "memory"}
        )
    
    def test_resource_cleanup_strategy_initialization(self, cleanup_strategy):
        """Testa inicialização da estratégia de limpeza"""
        assert cleanup_strategy is not None
        assert hasattr(cleanup_strategy, 'config')
        assert hasattr(cleanup_strategy, 'attempt_count')
        assert hasattr(cleanup_strategy, 'max_attempts')
    
    @pytest.mark.asyncio
    async def test_apply_resource_cleanup_success(self, cleanup_strategy, sample_problem_report):
        """Testa aplicação bem-sucedida de limpeza de recursos"""
        with patch.object(cleanup_strategy, '_cleanup_memory', new_callable=AsyncMock) as mock_memory:
            with patch.object(cleanup_strategy, '_cleanup_disk', new_callable=AsyncMock) as mock_disk:
                with patch.object(cleanup_strategy, '_cleanup_network', new_callable=AsyncMock) as mock_network:
                    
                    mock_memory.return_value = True
                    mock_disk.return_value = True
                    mock_network.return_value = True
                    
                    result = await cleanup_strategy.apply(sample_problem_report)
                    
                    assert result is True
                    mock_memory.assert_called_once_with("memory-service")
                    mock_disk.assert_called_once_with("memory-service")
                    mock_network.assert_called_once_with("memory-service")
    
    @pytest.mark.asyncio
    async def test_apply_resource_cleanup_failure(self, cleanup_strategy, sample_problem_report):
        """Testa falha na limpeza de recursos"""
        with patch.object(cleanup_strategy, '_cleanup_memory', new_callable=AsyncMock) as mock_memory:
            with patch.object(cleanup_strategy, '_cleanup_disk', new_callable=AsyncMock) as mock_disk:
                with patch.object(cleanup_strategy, '_cleanup_network', new_callable=AsyncMock) as mock_network:
                    
                    mock_memory.return_value = False
                    mock_disk.return_value = True
                    mock_network.return_value = True
                    
                    result = await cleanup_strategy.apply(sample_problem_report)
                    
                    assert result is False
                    mock_memory.assert_called_once_with("memory-service")
    
    @pytest.mark.asyncio
    async def test_cleanup_memory(self, cleanup_strategy):
        """Testa limpeza de memória"""
        # Mock de operações de memória
        with patch('gc.collect', return_value=0):
            with patch('psutil.virtual_memory') as mock_vm:
                mock_vm.return_value = Mock(percent=50.0)
                
                result = await cleanup_strategy._cleanup_memory("memory-service")
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_cleanup_disk(self, cleanup_strategy):
        """Testa limpeza de disco"""
        # Mock de operações de disco
        with patch('os.path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                mock_remove.return_value = None
                
                result = await cleanup_strategy._cleanup_disk("disk-service")
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_cleanup_network(self, cleanup_strategy):
        """Testa limpeza de rede"""
        # Mock de operações de rede
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.close.return_value = None
            
            result = await cleanup_strategy._cleanup_network("network-service")
            
            assert result is True


class TestConfigurationReloadStrategy:
    """Testes para ConfigurationReloadStrategy"""
    
    @pytest.fixture
    def healing_config(self):
        """Configuração de healing para testes"""
        return HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5
        )
    
    @pytest.fixture
    def reload_strategy(self, healing_config):
        """Instância da estratégia de reload"""
        return ConfigurationReloadStrategy(healing_config)
    
    @pytest.fixture
    def sample_problem_report(self):
        """Relatório de problema de exemplo"""
        return ProblemReport(
            service_name="config-service",
            problem_type=ProblemType.API_ERROR,
            severity="medium",
            description="Configuration needs reload",
            timestamp=datetime.now(timezone.utc),
            metrics={"error_rate": 0.1},
            context={"config_type": "application"}
        )
    
    def test_configuration_reload_strategy_initialization(self, reload_strategy):
        """Testa inicialização da estratégia de reload"""
        assert reload_strategy is not None
        assert hasattr(reload_strategy, 'config')
        assert hasattr(reload_strategy, 'attempt_count')
        assert hasattr(reload_strategy, 'max_attempts')
    
    @pytest.mark.asyncio
    async def test_apply_configuration_reload_success(self, reload_strategy, sample_problem_report):
        """Testa aplicação bem-sucedida de reload de configuração"""
        with patch.object(reload_strategy, '_reload_app_config', new_callable=AsyncMock) as mock_app:
            with patch.object(reload_strategy, '_reload_database_config', new_callable=AsyncMock) as mock_db:
                with patch.object(reload_strategy, '_reload_cache_config', new_callable=AsyncMock) as mock_cache:
                    
                    mock_app.return_value = True
                    mock_db.return_value = True
                    mock_cache.return_value = True
                    
                    result = await reload_strategy.apply(sample_problem_report)
                    
                    assert result is True
                    mock_app.assert_called_once_with("config-service")
                    mock_db.assert_called_once_with("config-service")
                    mock_cache.assert_called_once_with("config-service")
    
    @pytest.mark.asyncio
    async def test_apply_configuration_reload_failure(self, reload_strategy, sample_problem_report):
        """Testa falha no reload de configuração"""
        with patch.object(reload_strategy, '_reload_app_config', new_callable=AsyncMock) as mock_app:
            with patch.object(reload_strategy, '_reload_database_config', new_callable=AsyncMock) as mock_db:
                with patch.object(reload_strategy, '_reload_cache_config', new_callable=AsyncMock) as mock_cache:
                    
                    mock_app.return_value = False
                    mock_db.return_value = True
                    mock_cache.return_value = True
                    
                    result = await reload_strategy.apply(sample_problem_report)
                    
                    assert result is False
                    mock_app.assert_called_once_with("config-service")
    
    @pytest.mark.asyncio
    async def test_reload_app_config(self, reload_strategy):
        """Testa reload de configuração de aplicação"""
        # Mock de operações de configuração
        with patch('builtins.open', mock_open(read_data='{"config": "value"}')):
            with patch('json.load', return_value={"config": "value"}):
                
                result = await reload_strategy._reload_app_config("app-service")
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_reload_database_config(self, reload_strategy):
        """Testa reload de configuração de banco de dados"""
        # Mock de operações de banco de dados
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch.object(reload_strategy, '_test_database_connection', new_callable=AsyncMock) as mock_test:
                mock_test.return_value = True
                
                result = await reload_strategy._reload_database_config("db-service")
                
                assert result is True
                mock_test.assert_called()
    
    @pytest.mark.asyncio
    async def test_reload_cache_config(self, reload_strategy):
        """Testa reload de configuração de cache"""
        # Mock de operações de cache
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch.object(reload_strategy, '_test_cache_connection', new_callable=AsyncMock) as mock_test:
                mock_test.return_value = True
                
                result = await reload_strategy._reload_cache_config("cache-service")
                
                assert result is True
                mock_test.assert_called()


class TestHealingStrategyFactory:
    """Testes para HealingStrategyFactory"""
    
    @pytest.fixture
    def healing_config(self):
        """Configuração de healing para testes"""
        return HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5
        )
    
    def test_healing_strategy_factory_initialization(self):
        """Testa inicialização da factory"""
        factory = HealingStrategyFactory()
        assert factory is not None
    
    def test_create_service_restart_strategy(self, healing_config):
        """Testa criação de estratégia de restart de serviço"""
        strategy = HealingStrategyFactory.create_strategy('service_restart', healing_config)
        
        assert isinstance(strategy, ServiceRestartStrategy)
        assert strategy.config == healing_config
    
    def test_create_connection_recovery_strategy(self, healing_config):
        """Testa criação de estratégia de recuperação de conexão"""
        strategy = HealingStrategyFactory.create_strategy('connection_recovery', healing_config)
        
        assert isinstance(strategy, ConnectionRecoveryStrategy)
        assert strategy.config == healing_config
    
    def test_create_resource_cleanup_strategy(self, healing_config):
        """Testa criação de estratégia de limpeza de recursos"""
        strategy = HealingStrategyFactory.create_strategy('resource_cleanup', healing_config)
        
        assert isinstance(strategy, ResourceCleanupStrategy)
        assert strategy.config == healing_config
    
    def test_create_configuration_reload_strategy(self, healing_config):
        """Testa criação de estratégia de reload de configuração"""
        strategy = HealingStrategyFactory.create_strategy('configuration_reload', healing_config)
        
        assert isinstance(strategy, ConfigurationReloadStrategy)
        assert strategy.config == healing_config
    
    def test_create_unknown_strategy(self, healing_config):
        """Testa criação de estratégia desconhecida"""
        with pytest.raises(ValueError, match="Estratégia desconhecida"):
            HealingStrategyFactory.create_strategy('unknown_strategy', healing_config)
    
    def test_create_all_strategies(self, healing_config):
        """Testa criação de todas as estratégias"""
        strategies = [
            'service_restart',
            'connection_recovery',
            'resource_cleanup',
            'configuration_reload'
        ]
        
        for strategy_type in strategies:
            strategy = HealingStrategyFactory.create_strategy(strategy_type, healing_config)
            assert strategy is not None
            assert strategy.config == healing_config


class TestHealingStrategiesIntegration:
    """Testes de integração para HealingStrategies"""
    
    @pytest.mark.asyncio
    async def test_full_healing_cycle(self, healing_config):
        """Testa ciclo completo de healing"""
        # Criar estratégias
        restart_strategy = ServiceRestartStrategy(healing_config)
        recovery_strategy = ConnectionRecoveryStrategy(healing_config)
        cleanup_strategy = ResourceCleanupStrategy(healing_config)
        reload_strategy = ConfigurationReloadStrategy(healing_config)
        
        # Criar relatórios de problema
        restart_problem = ProblemReport(
            service_name="restart-service",
            problem_type=ProblemType.SERVICE_CRASH,
            severity="high",
            description="Service crashed",
            timestamp=datetime.now(timezone.utc),
            metrics={},
            context={}
        )
        
        recovery_problem = ProblemReport(
            service_name="recovery-service",
            problem_type=ProblemType.CONNECTION_ERROR,
            severity="medium",
            description="Connection lost",
            timestamp=datetime.now(timezone.utc),
            metrics={},
            context={}
        )
        
        # Mock de todas as operações
        with patch.object(restart_strategy, '_is_service_running', new_callable=AsyncMock) as mock_running:
            with patch.object(restart_strategy, '_restart_service', new_callable=AsyncMock) as mock_restart:
                with patch.object(restart_strategy, '_wait_for_service_ready', new_callable=AsyncMock) as mock_wait:
                    with patch.object(recovery_strategy, '_identify_connection_type', return_value="database"):
                        with patch.object(recovery_strategy, '_recover_database_connection', new_callable=AsyncMock) as mock_db:
                            
                            mock_running.return_value = True
                            mock_restart.return_value = True
                            mock_wait.return_value = True
                            mock_db.return_value = True
                            
                            # Aplicar estratégias
                            restart_result = await restart_strategy.apply(restart_problem)
                            recovery_result = await recovery_strategy.apply(recovery_problem)
                            
                            assert restart_result is True
                            assert recovery_result is True
    
    @pytest.mark.asyncio
    async def test_strategy_factory_integration(self, healing_config):
        """Testa integração com factory"""
        # Criar estratégias via factory
        strategies = {}
        strategy_types = ['service_restart', 'connection_recovery', 'resource_cleanup', 'configuration_reload']
        
        for strategy_type in strategy_types:
            strategies[strategy_type] = HealingStrategyFactory.create_strategy(strategy_type, healing_config)
        
        # Verificar se todas foram criadas corretamente
        assert len(strategies) == 4
        assert isinstance(strategies['service_restart'], ServiceRestartStrategy)
        assert isinstance(strategies['connection_recovery'], ConnectionRecoveryStrategy)
        assert isinstance(strategies['resource_cleanup'], ResourceCleanupStrategy)
        assert isinstance(strategies['configuration_reload'], ConfigurationReloadStrategy)
        
        # Verificar se todas têm a mesma configuração
        for strategy in strategies.values():
            assert strategy.config == healing_config


class TestHealingStrategiesErrorHandling:
    """Testes de tratamento de erro para HealingStrategies"""
    
    @pytest.mark.asyncio
    async def test_strategy_application_error_handling(self, healing_config):
        """Testa tratamento de erros na aplicação de estratégias"""
        restart_strategy = ServiceRestartStrategy(healing_config)
        
        problem_report = ProblemReport(
            service_name="error-service",
            problem_type=ProblemType.SERVICE_CRASH,
            severity="high",
            description="Service crashed",
            timestamp=datetime.now(timezone.utc),
            metrics={},
            context={}
        )
        
        # Mock que simula erro
        with patch.object(restart_strategy, '_is_service_running', side_effect=Exception("Test error")):
            result = await restart_strategy.apply(problem_report)
            
            # Deve retornar False em caso de erro
            assert result is False
    
    @pytest.mark.asyncio
    async def test_factory_error_handling(self, healing_config):
        """Testa tratamento de erros na factory"""
        # Teste com tipo de estratégia inválido
        with pytest.raises(ValueError):
            HealingStrategyFactory.create_strategy('invalid_strategy', healing_config)
        
        # Teste com configuração inválida
        with pytest.raises(Exception):
            HealingStrategyFactory.create_strategy('service_restart', None)


class TestHealingStrategiesPerformance:
    """Testes de performance para HealingStrategies"""
    
    @pytest.mark.asyncio
    async def test_strategy_application_performance(self, healing_config):
        """Testa performance da aplicação de estratégias"""
        restart_strategy = ServiceRestartStrategy(healing_config)
        
        problem_report = ProblemReport(
            service_name="perf-service",
            problem_type=ProblemType.SERVICE_CRASH,
            severity="high",
            description="Service crashed",
            timestamp=datetime.now(timezone.utc),
            metrics={},
            context={}
        )
        
        start_time = datetime.now()
        
        with patch.object(restart_strategy, '_is_service_running', new_callable=AsyncMock) as mock_running:
            with patch.object(restart_strategy, '_restart_service', new_callable=AsyncMock) as mock_restart:
                with patch.object(restart_strategy, '_wait_for_service_ready', new_callable=AsyncMock) as mock_wait:
                    
                    mock_running.return_value = True
                    mock_restart.return_value = True
                    mock_wait.return_value = True
                    
                    result = await restart_strategy.apply(problem_report)
                    
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    # Performance deve ser < 1 segundo
                    assert duration < 1.0
                    assert result is True
    
    def test_factory_creation_performance(self, healing_config):
        """Testa performance da criação de estratégias"""
        start_time = datetime.now()
        
        # Criar muitas estratégias
        for i in range(100):
            strategy = HealingStrategyFactory.create_strategy('service_restart', healing_config)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser < 1 segundo para 100 estratégias
        assert duration < 1.0 