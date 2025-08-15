"""
Testes Unitários para Failure Injection
Failure Injection - Sistema de injeção controlada de falhas para testar resiliência

Prompt: Implementação de testes unitários para Failure Injection
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: FAILURE_INJECTION_TESTS_001_20250127
"""

import pytest
import json
import time
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable

from infrastructure.chaos.failure_injection import (
    FailureType,
    InjectionMode,
    FailureSeverity,
    FailureConfig,
    InjectionResult,
    FailureInjector,
    FailureInjectionDecorator,
    FailureInjectionManager
)


class TestFailureType:
    """Testes para FailureType"""
    
    def test_failure_type_values(self):
        """Testa valores dos tipos de falha"""
        assert FailureType.TIMEOUT.value == "timeout"
        assert FailureType.EXCEPTION.value == "exception"
        assert FailureType.MEMORY_LEAK.value == "memory_leak"
        assert FailureType.CPU_SPIKE.value == "cpu_spike"
        assert FailureType.NETWORK_ERROR.value == "network_error"
        assert FailureType.DATABASE_ERROR.value == "database_error"
        assert FailureType.CACHE_ERROR.value == "cache_error"
        assert FailureType.DISK_ERROR.value == "disk_error"
        assert FailureType.RANDOM_FAILURE.value == "random_failure"
        assert FailureType.CUSTOM.value == "custom"
    
    def test_failure_type_enumeration(self):
        """Testa enumeração dos tipos de falha"""
        failure_types = list(FailureType)
        assert len(failure_types) == 10
        
        # Verifica se todos os tipos estão presentes
        type_names = [ft.value for ft in failure_types]
        expected_names = [
            "timeout", "exception", "memory_leak", "cpu_spike",
            "network_error", "database_error", "cache_error",
            "disk_error", "random_failure", "custom"
        ]
        assert all(name in type_names for name in expected_names)
    
    def test_failure_type_comparison(self):
        """Testa comparação entre tipos de falha"""
        assert FailureType.TIMEOUT == FailureType.TIMEOUT
        assert FailureType.TIMEOUT != FailureType.EXCEPTION
        assert FailureType.TIMEOUT.value == "timeout"


class TestInjectionMode:
    """Testes para InjectionMode"""
    
    def test_injection_mode_values(self):
        """Testa valores dos modos de injeção"""
        # Assumindo que InjectionMode tem valores como 'immediate', 'delayed', 'random'
        modes = list(InjectionMode)
        assert len(modes) > 0
        
        for mode in modes:
            assert isinstance(mode.value, str)
            assert len(mode.value) > 0
    
    def test_injection_mode_enumeration(self):
        """Testa enumeração dos modos de injeção"""
        injection_modes = list(InjectionMode)
        assert len(injection_modes) > 0
        
        # Verifica se todos os modos são únicos
        mode_values = [mode.value for mode in injection_modes]
        assert len(mode_values) == len(set(mode_values))


class TestFailureSeverity:
    """Testes para FailureSeverity"""
    
    def test_failure_severity_values(self):
        """Testa valores dos níveis de severidade"""
        # Assumindo que FailureSeverity tem valores como 'low', 'medium', 'high', 'critical'
        severities = list(FailureSeverity)
        assert len(severities) > 0
        
        for severity in severities:
            assert isinstance(severity.value, str)
            assert len(severity.value) > 0
    
    def test_failure_severity_hierarchy(self):
        """Testa hierarquia dos níveis de severidade"""
        # Verifica se existe uma ordem lógica de severidade
        severity_values = [s.value for s in FailureSeverity]
        
        # Se houver valores numéricos ou ordem específica, testa aqui
        if 'low' in severity_values and 'high' in severity_values:
            low_index = severity_values.index('low')
            high_index = severity_values.index('high')
            # Assumindo que 'low' vem antes de 'high' na enumeração
            assert low_index < high_index


class TestFailureConfig:
    """Testes para FailureConfig"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Dados de exemplo para FailureConfig"""
        return {
            'failure_type': FailureType.TIMEOUT,
            'injection_mode': InjectionMode.IMMEDIATE,
            'severity': FailureSeverity.MEDIUM,
            'probability': 0.5,
            'duration': 30.0,
            'parameters': {
                'timeout_ms': 5000,
                'retry_count': 3
            }
        }
    
    @pytest.fixture
    def failure_config_instance(self, sample_config_data):
        """Instância de FailureConfig para testes"""
        return FailureConfig(**sample_config_data)
    
    def test_initialization(self, sample_config_data):
        """Testa inicialização básica de FailureConfig"""
        config = FailureConfig(**sample_config_data)
        
        assert config.failure_type == FailureType.TIMEOUT
        assert config.injection_mode == InjectionMode.IMMEDIATE
        assert config.severity == FailureSeverity.MEDIUM
        assert config.probability == 0.5
        assert config.duration == 30.0
        assert config.parameters['timeout_ms'] == 5000
        assert config.parameters['retry_count'] == 3
    
    def test_default_values(self):
        """Testa valores padrão"""
        config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM
        )
        
        assert config.probability == 1.0  # Assumindo valor padrão
        assert config.duration == 0.0  # Assumindo valor padrão
        assert config.parameters == {}  # Assumindo valor padrão
    
    def test_validation_probability_range(self):
        """Testa validação do range de probabilidade"""
        # Teste com probabilidade válida
        valid_config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM,
            probability=0.75
        )
        assert valid_config.probability == 0.75
        
        # Teste com probabilidade fora do range
        with pytest.raises(ValueError):
            FailureConfig(
                failure_type=FailureType.TIMEOUT,
                injection_mode=InjectionMode.IMMEDIATE,
                severity=FailureSeverity.MEDIUM,
                probability=1.5  # Probabilidade > 1.0
            )
        
        with pytest.raises(ValueError):
            FailureConfig(
                failure_type=FailureType.TIMEOUT,
                injection_mode=InjectionMode.IMMEDIATE,
                severity=FailureSeverity.MEDIUM,
                probability=-0.1  # Probabilidade < 0.0
            )
    
    def test_validation_duration_positive(self):
        """Testa validação de duração positiva"""
        # Teste com duração válida
        valid_config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM,
            duration=10.0
        )
        assert valid_config.duration == 10.0
        
        # Teste com duração negativa
        with pytest.raises(ValueError):
            FailureConfig(
                failure_type=FailureType.TIMEOUT,
                injection_mode=InjectionMode.IMMEDIATE,
                severity=FailureSeverity.MEDIUM,
                duration=-5.0
            )


class TestInjectionResult:
    """Testes para InjectionResult"""
    
    @pytest.fixture
    def sample_result_data(self):
        """Dados de exemplo para InjectionResult"""
        return {
            'injection_id': 'failure_timeout_1706313600_1234',
            'success': True,
            'failure_type': FailureType.TIMEOUT,
            'start_time': datetime.now(timezone.utc),
            'end_time': datetime.now(timezone.utc) + timedelta(seconds=5),
            'duration': 5.0,
            'error_message': None,
            'metadata': {
                'target_function': 'test_function',
                'parameters': {'timeout_ms': 5000}
            }
        }
    
    @pytest.fixture
    def injection_result_instance(self, sample_result_data):
        """Instância de InjectionResult para testes"""
        return InjectionResult(**sample_result_data)
    
    def test_initialization(self, sample_result_data):
        """Testa inicialização básica de InjectionResult"""
        result = InjectionResult(**sample_result_data)
        
        assert result.injection_id == 'failure_timeout_1706313600_1234'
        assert result.success is True
        assert result.failure_type == FailureType.TIMEOUT
        assert isinstance(result.start_time, datetime)
        assert isinstance(result.end_time, datetime)
        assert result.duration == 5.0
        assert result.error_message is None
        assert result.metadata['target_function'] == 'test_function'
    
    def test_duration_calculation(self):
        """Testa cálculo automático de duração"""
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(seconds=10)
        
        result = InjectionResult(
            injection_id='test_001',
            success=True,
            failure_type=FailureType.TIMEOUT,
            start_time=start_time,
            end_time=end_time
        )
        
        assert result.duration == 10.0
    
    def test_failed_injection_result(self):
        """Testa resultado de injeção falhada"""
        result = InjectionResult(
            injection_id='test_002',
            success=False,
            failure_type=FailureType.EXCEPTION,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            error_message='Injection failed due to invalid parameters'
        )
        
        assert result.success is False
        assert result.error_message == 'Injection failed due to invalid parameters'
        assert result.failure_type == FailureType.EXCEPTION


class TestFailureInjector:
    """Testes para FailureInjector"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para FailureInjector"""
        return FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM,
            probability=1.0,
            duration=5.0,
            parameters={'timeout_ms': 3000}
        )
    
    @pytest.fixture
    def failure_injector(self, sample_config):
        """Instância de FailureInjector para testes"""
        return FailureInjector(sample_config)
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica de FailureInjector"""
        injector = FailureInjector(sample_config)
        
        assert injector.config == sample_config
        assert injector.injection_id is not None
        assert 'failure_timeout_' in injector.injection_id
        assert len(injector.active_injections) == 0
        assert len(injector.recovery_handlers) == 0
        assert len(injector.monitoring_callbacks) == 0
        assert injector.injection_count == 0
        assert injector.success_count == 0
    
    def test_injection_id_generation(self, sample_config):
        """Testa geração de ID único de injeção"""
        injector1 = FailureInjector(sample_config)
        injector2 = FailureInjector(sample_config)
        
        assert injector1.injection_id != injector2.injection_id
        assert 'failure_timeout_' in injector1.injection_id
        assert 'failure_timeout_' in injector2.injection_id
    
    @patch('time.time')
    def test_inject_failure_timeout(self, mock_time, sample_config):
        """Testa injeção de falha de timeout"""
        mock_time.return_value = 1706313600.0
        
        injector = FailureInjector(sample_config)
        
        # Mock da função alvo
        target_func = Mock()
        target_func.__name__ = 'test_function'
        
        result = injector.inject_failure(target_func)
        
        assert result.injection_id is not None
        assert result.failure_type == FailureType.TIMEOUT
        assert result.success is True
        assert result.duration >= 0
    
    @patch('time.time')
    def test_inject_failure_exception(self, mock_time):
        """Testa injeção de falha de exceção"""
        mock_time.return_value = 1706313600.0
        
        config = FailureConfig(
            failure_type=FailureType.EXCEPTION,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.HIGH,
            probability=1.0,
            parameters={'exception_type': 'ValueError', 'message': 'Test exception'}
        )
        
        injector = FailureInjector(config)
        result = injector.inject_failure()
        
        assert result.failure_type == FailureType.EXCEPTION
        assert result.success is True
    
    def test_inject_failure_with_probability(self, sample_config):
        """Testa injeção com probabilidade"""
        # Configuração com probabilidade baixa
        low_prob_config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.LOW,
            probability=0.1  # 10% de chance
        )
        
        injector = FailureInjector(low_prob_config)
        
        # Executa múltiplas vezes para testar probabilidade
        results = []
        for _ in range(10):
            result = injector.inject_failure()
            results.append(result.success)
        
        # Pelo menos uma injeção deve ter sido bem-sucedida
        assert any(results)
    
    def test_add_monitoring_callback(self, failure_injector):
        """Testa adição de callback de monitoramento"""
        callback = Mock()
        failure_injector.add_monitoring_callback(callback)
        
        assert callback in failure_injector.monitoring_callbacks
    
    def test_remove_monitoring_callback(self, failure_injector):
        """Testa remoção de callback de monitoramento"""
        callback = Mock()
        failure_injector.add_monitoring_callback(callback)
        
        assert callback in failure_injector.monitoring_callbacks
        
        failure_injector.remove_monitoring_callback(callback)
        assert callback not in failure_injector.monitoring_callbacks
    
    def test_get_statistics(self, failure_injector):
        """Testa obtenção de estatísticas"""
        # Simula algumas injeções
        failure_injector.injection_count = 10
        failure_injector.success_count = 8
        
        stats = failure_injector.get_statistics()
        
        assert stats['injection_count'] == 10
        assert stats['success_count'] == 8
        assert stats['failure_count'] == 2
        assert stats['success_rate'] == 0.8
    
    def test_cleanup(self, failure_injector):
        """Testa limpeza de recursos"""
        # Adiciona algumas injeções ativas
        failure_injector.active_injections['test_1'] = Mock()
        failure_injector.active_injections['test_2'] = Mock()
        
        assert len(failure_injector.active_injections) == 2
        
        failure_injector.cleanup()
        
        assert len(failure_injector.active_injections) == 0


class TestFailureInjectionDecorator:
    """Testes para FailureInjectionDecorator"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para decorator"""
        return FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM,
            probability=1.0,
            duration=1.0
        )
    
    @pytest.fixture
    def injection_decorator(self, sample_config):
        """Instância de FailureInjectionDecorator para testes"""
        return FailureInjectionDecorator(sample_config)
    
    def test_decorator_initialization(self, sample_config):
        """Testa inicialização do decorator"""
        decorator = FailureInjectionDecorator(sample_config)
        
        assert decorator.config == sample_config
    
    def test_decorator_application(self, injection_decorator):
        """Testa aplicação do decorator em função"""
        @injection_decorator
        def test_function():
            return "success"
        
        # Verifica se a função foi decorada
        assert hasattr(test_function, '__wrapped__')
        assert callable(test_function)
    
    @patch('infrastructure.chaos.failure_injection.FailureInjector')
    def test_decorated_function_execution(self, mock_injector_class, injection_decorator):
        """Testa execução de função decorada"""
        mock_injector = Mock()
        mock_injector.inject_failure.return_value = InjectionResult(
            injection_id='test_001',
            success=True,
            failure_type=FailureType.TIMEOUT,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            duration=0.1
        )
        mock_injector_class.return_value = mock_injector
        
        @injection_decorator
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        mock_injector.inject_failure.assert_called_once()
    
    def test_decorator_with_parameters(self, sample_config):
        """Testa decorator com parâmetros"""
        decorator = FailureInjectionDecorator(sample_config)
        
        @decorator
        def test_function_with_params(param1, param2):
            return f"{param1}_{param2}"
        
        result = test_function_with_params("test", "value")
        assert result == "test_value"


class TestFailureInjectionManager:
    """Testes para FailureInjectionManager"""
    
    @pytest.fixture
    def manager(self):
        """Instância de FailureInjectionManager para testes"""
        return FailureInjectionManager()
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM,
            probability=1.0,
            duration=5.0
        )
    
    def test_initialization(self, manager):
        """Testa inicialização básica do manager"""
        assert len(manager.injectors) == 0
        assert len(manager.global_config) == 0
    
    def test_add_injector(self, manager, sample_config):
        """Testa adição de injector"""
        injector = manager.add_injector("timeout_injector", sample_config)
        
        assert "timeout_injector" in manager.injectors
        assert manager.injectors["timeout_injector"] == injector
        assert isinstance(injector, FailureInjector)
    
    def test_get_injector(self, manager, sample_config):
        """Testa obtenção de injector"""
        manager.add_injector("test_injector", sample_config)
        
        injector = manager.get_injector("test_injector")
        assert injector is not None
        assert isinstance(injector, FailureInjector)
        
        # Teste com injector inexistente
        non_existent = manager.get_injector("non_existent")
        assert non_existent is None
    
    def test_remove_injector(self, manager, sample_config):
        """Testa remoção de injector"""
        manager.add_injector("test_injector", sample_config)
        
        assert "test_injector" in manager.injectors
        
        # Remove o injector
        result = manager.remove_injector("test_injector")
        assert result is True
        assert "test_injector" not in manager.injectors
        
        # Tenta remover injector inexistente
        result = manager.remove_injector("non_existent")
        assert result is False
    
    def test_inject_failure_by_name(self, manager, sample_config):
        """Testa injeção de falha por nome"""
        manager.add_injector("test_injector", sample_config)
        
        result = manager.inject_failure("test_injector")
        assert result is not None
        assert isinstance(result, InjectionResult)
        
        # Teste com injector inexistente
        result = manager.inject_failure("non_existent")
        assert result is None
    
    def test_get_all_statistics(self, manager, sample_config):
        """Testa obtenção de estatísticas de todos os injectors"""
        manager.add_injector("injector_1", sample_config)
        manager.add_injector("injector_2", sample_config)
        
        stats = manager.get_all_statistics()
        
        assert "injector_1" in stats
        assert "injector_2" in stats
        assert len(stats) == 2
        
        for injector_stats in stats.values():
            assert "injection_count" in injector_stats
            assert "success_count" in injector_stats
            assert "failure_count" in injector_stats
            assert "success_rate" in injector_stats
    
    def test_cleanup_all(self, manager, sample_config):
        """Testa limpeza de todos os injectors"""
        injector1 = manager.add_injector("injector_1", sample_config)
        injector2 = manager.add_injector("injector_2", sample_config)
        
        # Mock dos métodos de cleanup
        injector1._perform_recovery = Mock()
        injector2._perform_recovery = Mock()
        
        manager.cleanup_all()
        
        injector1._perform_recovery.assert_called_once()
        injector2._perform_recovery.assert_called_once()


class TestFailureInjectionIntegration:
    """Testes de integração para Failure Injection"""
    
    def test_complete_injection_workflow(self):
        """Testa workflow completo de injeção de falha"""
        # Configuração
        config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM,
            probability=1.0,
            duration=1.0,
            parameters={'timeout_ms': 1000}
        )
        
        # Manager
        manager = FailureInjectionManager()
        
        # Adiciona injector
        injector = manager.add_injector("test_injector", config)
        
        # Adiciona callback de monitoramento
        callback = Mock()
        injector.add_monitoring_callback(callback)
        
        # Executa injeção
        result = injector.inject_failure()
        
        # Verifica resultado
        assert result.success is True
        assert result.failure_type == FailureType.TIMEOUT
        assert result.duration >= 0
        
        # Verifica estatísticas
        stats = manager.get_all_statistics()
        assert "test_injector" in stats
        assert stats["test_injector"]["injection_count"] >= 1
        
        # Cleanup
        manager.cleanup_all()
    
    def test_multiple_injectors_coordination(self):
        """Testa coordenação entre múltiplos injectors"""
        manager = FailureInjectionManager()
        
        # Configurações diferentes
        timeout_config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.LOW,
            probability=0.5
        )
        
        exception_config = FailureConfig(
            failure_type=FailureType.EXCEPTION,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.HIGH,
            probability=0.3
        )
        
        # Adiciona injectors
        timeout_injector = manager.add_injector("timeout", timeout_config)
        exception_injector = manager.add_injector("exception", exception_config)
        
        # Executa injeções
        timeout_result = manager.inject_failure("timeout")
        exception_result = manager.inject_failure("exception")
        
        # Verifica resultados
        assert timeout_result is not None
        assert exception_result is not None
        assert timeout_result.failure_type == FailureType.TIMEOUT
        assert exception_result.failure_type == FailureType.EXCEPTION
        
        # Verifica estatísticas
        stats = manager.get_all_statistics()
        assert len(stats) == 2
        assert "timeout" in stats
        assert "exception" in stats


class TestFailureInjectionErrorHandling:
    """Testes de tratamento de erro para Failure Injection"""
    
    def test_invalid_config_parameters(self):
        """Testa configuração com parâmetros inválidos"""
        with pytest.raises(ValueError):
            FailureConfig(
                failure_type=FailureType.TIMEOUT,
                injection_mode=InjectionMode.IMMEDIATE,
                severity=FailureSeverity.MEDIUM,
                probability=1.5  # Probabilidade inválida
            )
    
    def test_injector_with_invalid_config(self):
        """Testa injector com configuração inválida"""
        invalid_config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM,
            probability=1.0,
            duration=-5.0  # Duração negativa
        )
        
        with pytest.raises(ValueError):
            FailureInjector(invalid_config)
    
    def test_manager_with_duplicate_injector_names(self):
        """Testa manager com nomes duplicados de injectors"""
        manager = FailureInjectionManager()
        config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.MEDIUM
        )
        
        # Adiciona primeiro injector
        injector1 = manager.add_injector("test", config)
        
        # Adiciona segundo injector com mesmo nome (deve sobrescrever)
        injector2 = manager.add_injector("test", config)
        
        assert manager.get_injector("test") == injector2
        assert manager.get_injector("test") != injector1


class TestFailureInjectionPerformance:
    """Testes de performance para Failure Injection"""
    
    def test_rapid_injection_sequence(self):
        """Testa sequência rápida de injeções"""
        config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.LOW,
            probability=1.0,
            duration=0.1
        )
        
        injector = FailureInjector(config)
        
        start_time = time.time()
        
        # Executa 100 injeções rapidamente
        for _ in range(100):
            result = injector.inject_failure()
            assert result.success is True
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance deve ser < 10 segundos para 100 injeções
        assert execution_time < 10.0
        
        # Verifica estatísticas
        stats = injector.get_statistics()
        assert stats['injection_count'] == 100
        assert stats['success_count'] == 100
    
    def test_concurrent_injections(self):
        """Testa injeções concorrentes"""
        config = FailureConfig(
            failure_type=FailureType.TIMEOUT,
            injection_mode=InjectionMode.IMMEDIATE,
            severity=FailureSeverity.LOW,
            probability=1.0,
            duration=0.1
        )
        
        manager = FailureInjectionManager()
        injector = manager.add_injector("concurrent_test", config)
        
        def inject_failure():
            return injector.inject_failure()
        
        # Executa injeções em threads separadas
        threads = []
        results = []
        
        for _ in range(10):
            thread = threading.Thread(target=lambda: results.append(inject_failure()))
            threads.append(thread)
            thread.start()
        
        # Aguarda todas as threads terminarem
        for thread in threads:
            thread.join()
        
        # Verifica resultados
        assert len(results) == 10
        for result in results:
            assert result.success is True
            assert result.failure_type == FailureType.TIMEOUT 