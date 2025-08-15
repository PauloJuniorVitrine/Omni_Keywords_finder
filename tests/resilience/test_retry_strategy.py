"""
Test Retry Strategy
==================

Testes abrangentes para estratégias de retry com diferentes cenários.
Baseado em padrões de teste para resiliência em sistemas distribuídos.

Tracing ID: TEST_RETRY_STRATEGY_001_20250127
Ruleset: enterprise_control_layer.yaml
Execução: 2025-01-27T10:00:00Z
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock

from infrastructure.resilience.retry_strategy import (
    RetryConfig,
    RetryStrategy,
    RetryExecutor,
    RetryableError,
    NonRetryableError,
    ExponentialBackoffCalculator,
    LinearBackoffCalculator,
    FibonacciBackoffCalculator,
    API_RETRY_CONFIG,
    DATABASE_RETRY_CONFIG,
    EXTERNAL_SERVICE_RETRY_CONFIG
)


class TestRetryConfig:
    """Testes para configuração de retry."""
    
    def test_retry_config_defaults(self):
        """Testa valores padrão da configuração."""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
        assert config.jitter is True
        assert config.jitter_factor == 0.1
    
    def test_retry_config_custom_values(self):
        """Testa configuração com valores customizados."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=30.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=False
        )
        
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0
        assert config.strategy == RetryStrategy.LINEAR_BACKOFF
        assert config.jitter is False
    
    def test_retry_config_exception_lists(self):
        """Testa listas de exceções padrão."""
        config = RetryConfig()
        
        assert RetryableError in config.retryable_exceptions
        assert ConnectionError in config.retryable_exceptions
        assert TimeoutError in config.retryable_exceptions
        
        assert NonRetryableError in config.non_retryable_exceptions
        assert ValueError in config.non_retryable_exceptions
        assert TypeError in config.non_retryable_exceptions


class TestBackoffCalculators:
    """Testes para calculadoras de backoff."""
    
    def test_exponential_backoff_calculator(self):
        """Testa calculadora de backoff exponencial."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0)
        calculator = ExponentialBackoffCalculator()
        
        # Testa cálculos sem jitter
        config.jitter = False
        assert calculator.calculate_delay(1, config) == 1.0
        assert calculator.calculate_delay(2, config) == 2.0
        assert calculator.calculate_delay(3, config) == 4.0
        assert calculator.calculate_delay(4, config) == 8.0
    
    def test_exponential_backoff_with_jitter(self):
        """Testa backoff exponencial com jitter."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=True, jitter_factor=0.1)
        calculator = ExponentialBackoffCalculator()
        
        delay = calculator.calculate_delay(2, config)
        # Deve estar entre 1.8 e 2.2 (2.0 ± 10%)
        assert 1.8 <= delay <= 2.2
    
    def test_exponential_backoff_with_cap(self):
        """Testa backoff exponencial com limite máximo."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=5.0)
        calculator = ExponentialBackoffCalculator()
        
        # O delay não deve exceder o máximo
        delay = calculator.calculate_delay(10, config)
        assert delay <= 5.0
    
    def test_linear_backoff_calculator(self):
        """Testa calculadora de backoff linear."""
        config = RetryConfig(base_delay=1.0)
        calculator = LinearBackoffCalculator()
        
        assert calculator.calculate_delay(1, config) == 1.0
        assert calculator.calculate_delay(2, config) == 2.0
        assert calculator.calculate_delay(3, config) == 3.0
    
    def test_fibonacci_backoff_calculator(self):
        """Testa calculadora de backoff Fibonacci."""
        config = RetryConfig(base_delay=1.0)
        calculator = FibonacciBackoffCalculator()
        
        assert calculator.calculate_delay(1, config) == 1.0
        assert calculator.calculate_delay(2, config) == 1.0
        assert calculator.calculate_delay(3, config) == 2.0
        assert calculator.calculate_delay(4, config) == 3.0
        assert calculator.calculate_delay(5, config) == 5.0


class TestRetryExecutor:
    """Testes para executor de retry."""
    
    def test_retry_executor_success_on_first_attempt(self):
        """Testa sucesso na primeira tentativa."""
        config = RetryConfig(max_attempts=3)
        executor = RetryExecutor(config)
        
        mock_func = Mock(return_value="success")
        
        result = executor.execute_sync(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_executor_success_on_retry(self):
        """Testa sucesso após retry."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        executor = RetryExecutor(config)
        
        mock_func = Mock(side_effect=[ConnectionError(), ConnectionError(), "success"])
        
        result = executor.execute_sync(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_executor_max_attempts_exceeded(self):
        """Testa quando máximo de tentativas é excedido."""
        config = RetryConfig(max_attempts=2, base_delay=0.1)
        executor = RetryExecutor(config)
        
        mock_func = Mock(side_effect=ConnectionError())
        
        with pytest.raises(ConnectionError):
            executor.execute_sync(mock_func)
        
        assert mock_func.call_count == 2
    
    def test_retry_executor_non_retryable_exception(self):
        """Testa exceção não retentável."""
        config = RetryConfig(max_attempts=3)
        executor = RetryExecutor(config)
        
        mock_func = Mock(side_effect=ValueError("Invalid input"))
        
        with pytest.raises(ValueError):
            executor.execute_sync(mock_func)
        
        assert mock_func.call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_executor_async_success(self):
        """Testa executor assíncrono com sucesso."""
        config = RetryConfig(max_attempts=3)
        executor = RetryExecutor(config)
        
        async def async_func():
            return "async_success"
        
        result = await executor.execute_async(async_func)
        
        assert result == "async_success"
    
    @pytest.mark.asyncio
    async def test_retry_executor_async_with_retry(self):
        """Testa executor assíncrono com retry."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        executor = RetryExecutor(config)
        
        call_count = 0
        
        async def async_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError()
            return "async_success"
        
        result = await executor.execute_async(async_func)
        
        assert result == "async_success"
        assert call_count == 3


class TestRetryDecorator:
    """Testes para decorator de retry."""
    
    def test_retry_decorator_sync(self):
        """Testa decorator síncrono."""
        from infrastructure.resilience.retry_strategy import retry
        
        call_count = 0
        
        @retry(max_attempts=3, base_delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError()
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_decorator_async(self):
        """Testa decorator assíncrono."""
        from infrastructure.resilience.retry_strategy import retry
        
        call_count = 0
        
        @retry(max_attempts=3, base_delay=0.1)
        async def async_test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError()
            return "async_success"
        
        result = await async_test_func()
        
        assert result == "async_success"
        assert call_count == 3


class TestPredefinedConfigs:
    """Testes para configurações pré-definidas."""
    
    def test_api_retry_config(self):
        """Testa configuração de retry para APIs."""
        assert API_RETRY_CONFIG.max_attempts == 5
        assert API_RETRY_CONFIG.base_delay == 2.0
        assert API_RETRY_CONFIG.max_delay == 30.0
        assert API_RETRY_CONFIG.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
        assert API_RETRY_CONFIG.jitter is True
    
    def test_database_retry_config(self):
        """Testa configuração de retry para banco de dados."""
        assert DATABASE_RETRY_CONFIG.max_attempts == 3
        assert DATABASE_RETRY_CONFIG.base_delay == 1.0
        assert DATABASE_RETRY_CONFIG.max_delay == 10.0
        assert DATABASE_RETRY_CONFIG.strategy == RetryStrategy.LINEAR_BACKOFF
        assert DATABASE_RETRY_CONFIG.jitter is False
    
    def test_external_service_retry_config(self):
        """Testa configuração de retry para serviços externos."""
        assert EXTERNAL_SERVICE_RETRY_CONFIG.max_attempts == 7
        assert EXTERNAL_SERVICE_RETRY_CONFIG.base_delay == 1.0
        assert EXTERNAL_SERVICE_RETRY_CONFIG.max_delay == 60.0
        assert EXTERNAL_SERVICE_RETRY_CONFIG.strategy == RetryStrategy.FIBONACCI_BACKOFF
        assert EXTERNAL_SERVICE_RETRY_CONFIG.jitter is True


class TestRetryStrategyManager:
    """Testes para gerenciador de estratégias de retry."""
    
    def test_should_retry_retryable_exception(self):
        """Testa se exceção retentável deve ser retentada."""
        from infrastructure.resilience.retry_strategy import RetryStrategyManager
        
        manager = RetryStrategyManager()
        config = RetryConfig()
        
        assert manager.should_retry(ConnectionError(), config) is True
        assert manager.should_retry(TimeoutError(), config) is True
        assert manager.should_retry(RetryableError(), config) is True
    
    def test_should_retry_non_retryable_exception(self):
        """Testa se exceção não retentável não deve ser retentada."""
        from infrastructure.resilience.retry_strategy import RetryStrategyManager
        
        manager = RetryStrategyManager()
        config = RetryConfig()
        
        assert manager.should_retry(ValueError(), config) is False
        assert manager.should_retry(TypeError(), config) is False
        assert manager.should_retry(NonRetryableError(), config) is False
    
    def test_get_calculator(self):
        """Testa obtenção de calculadora."""
        from infrastructure.resilience.retry_strategy import RetryStrategyManager
        
        manager = RetryStrategyManager()
        
        calculator = manager.get_calculator(RetryStrategy.EXPONENTIAL_BACKOFF)
        assert isinstance(calculator, ExponentialBackoffCalculator)
        
        calculator = manager.get_calculator(RetryStrategy.LINEAR_BACKOFF)
        assert isinstance(calculator, LinearBackoffCalculator)
        
        calculator = manager.get_calculator(RetryStrategy.FIBONACCI_BACKOFF)
        assert isinstance(calculator, FibonacciBackoffCalculator)


class TestPerformance:
    """Testes de performance."""
    
    def test_retry_performance_without_retries(self):
        """Testa performance sem retries."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        executor = RetryExecutor(config)
        
        mock_func = Mock(return_value="success")
        
        start_time = time.time()
        result = executor.execute_sync(mock_func)
        end_time = time.time()
        
        assert result == "success"
        assert end_time - start_time < 0.1  # Deve ser rápido sem retries
    
    def test_retry_performance_with_retries(self):
        """Testa performance com retries."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        executor = RetryExecutor(config)
        
        mock_func = Mock(side_effect=[ConnectionError(), ConnectionError(), "success"])
        
        start_time = time.time()
        result = executor.execute_sync(mock_func)
        end_time = time.time()
        
        assert result == "success"
        # Deve levar pelo menos o tempo dos delays
        assert end_time - start_time >= 0.2  # 2 delays de 0.1s cada


class TestEdgeCases:
    """Testes para casos extremos."""
    
    def test_zero_max_attempts(self):
        """Testa com zero tentativas máximas."""
        config = RetryConfig(max_attempts=0)
        executor = RetryExecutor(config)
        
        mock_func = Mock(side_effect=ConnectionError())
        
        with pytest.raises(ConnectionError):
            executor.execute_sync(mock_func)
        
        assert mock_func.call_count == 0
    
    def test_very_large_delays(self):
        """Testa com delays muito grandes."""
        config = RetryConfig(base_delay=1000.0, max_delay=2000.0)
        executor = RetryExecutor(config)
        
        mock_func = Mock(side_effect=[ConnectionError(), "success"])
        
        start_time = time.time()
        result = executor.execute_sync(mock_func)
        end_time = time.time()
        
        assert result == "success"
        # Deve respeitar o delay
        assert end_time - start_time >= 1000.0
    
    def test_negative_delays(self):
        """Testa com delays negativos."""
        config = RetryConfig(base_delay=-1.0)
        executor = RetryExecutor(config)
        
        mock_func = Mock(side_effect=[ConnectionError(), "success"])
        
        # Deve funcionar mesmo com delay negativo (será tratado como 0)
        result = executor.execute_sync(mock_func)
        
        assert result == "success" 