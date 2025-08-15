"""
Retry Strategy Implementation
============================

Implementa estratégias de retry com backoff exponencial para APIs externas.
Baseado em padrões da indústria para resiliência em sistemas distribuídos.

Tracing ID: RETRY_STRATEGY_001_20250127
Ruleset: enterprise_control_layer.yaml
Execução: 2025-01-27T10:00:00Z
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Estratégias de retry disponíveis."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CONSTANT_BACKOFF = "constant_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"


class RetryableError(Exception):
    """Exceção base para erros que devem ser retentados."""
    pass


class NonRetryableError(Exception):
    """Exceção para erros que não devem ser retentados."""
    pass


@dataclass
class RetryConfig:
    """Configuração para estratégias de retry."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_exceptions: List[Type[Exception]] = None
    non_retryable_exceptions: List[Type[Exception]] = None
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [RetryableError, ConnectionError, TimeoutError]
        if self.non_retryable_exceptions is None:
            self.non_retryable_exceptions = [NonRetryableError, ValueError, TypeError]


class BackoffCalculator(ABC):
    """Calculadora abstrata para diferentes estratégias de backoff."""
    
    @abstractmethod
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calcula o delay para uma tentativa específica."""
        pass


class ExponentialBackoffCalculator(BackoffCalculator):
    """Calculadora de backoff exponencial."""
    
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calcula delay exponencial com jitter opcional."""
        delay = min(
            config.base_delay * (config.exponential_base ** (attempt - 1)),
            config.max_delay
        )
        
        if config.jitter:
            jitter = delay * config.jitter_factor * random.uniform(-1, 1)
            delay = max(0, delay + jitter)
        
        return delay


class LinearBackoffCalculator(BackoffCalculator):
    """Calculadora de backoff linear."""
    
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calcula delay linear com jitter opcional."""
        delay = min(config.base_delay * attempt, config.max_delay)
        
        if config.jitter:
            jitter = delay * config.jitter_factor * random.uniform(-1, 1)
            delay = max(0, delay + jitter)
        
        return delay


class FibonacciBackoffCalculator(BackoffCalculator):
    """Calculadora de backoff baseada na sequência de Fibonacci."""
    
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calcula delay baseado na sequência de Fibonacci."""
        if attempt <= 2:
            delay = config.base_delay
        else:
            a, b = config.base_delay, config.base_delay
            for _ in range(3, attempt + 1):
                a, b = b, a + b
            delay = min(b, config.max_delay)
        
        if config.jitter:
            jitter = delay * config.jitter_factor * random.uniform(-1, 1)
            delay = max(0, delay + jitter)
        
        return delay


class RetryStrategyManager:
    """Gerenciador de estratégias de retry."""
    
    def __init__(self):
        self._calculators = {
            RetryStrategy.EXPONENTIAL_BACKOFF: ExponentialBackoffCalculator(),
            RetryStrategy.LINEAR_BACKOFF: LinearBackoffCalculator(),
            RetryStrategy.FIBONACCI_BACKOFF: FibonacciBackoffCalculator(),
        }
    
    def get_calculator(self, strategy: RetryStrategy) -> BackoffCalculator:
        """Obtém a calculadora para uma estratégia específica."""
        return self._calculators.get(strategy, ExponentialBackoffCalculator())
    
    def should_retry(self, exception: Exception, config: RetryConfig) -> bool:
        """Determina se uma exceção deve ser retentada."""
        # Verifica exceções não retentáveis primeiro
        for non_retryable in config.non_retryable_exceptions:
            if isinstance(exception, non_retryable):
                return False
        
        # Verifica exceções retentáveis
        for retryable in config.retryable_exceptions:
            if isinstance(exception, retryable):
                return True
        
        return False


class RetryExecutor:
    """Executor de operações com retry."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.strategy_manager = RetryStrategyManager()
        self.calculator = self.strategy_manager.get_calculator(config.strategy)
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função assíncrona com retry."""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"Retry successful on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self.strategy_manager.should_retry(e, self.config):
                    logger.warning(f"Non-retryable error on attempt {attempt}: {e}")
                    raise e
                
                if attempt < self.config.max_attempts:
                    delay = self.calculator.calculate_delay(attempt, self.config)
                    logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_attempts} attempts failed")
        
        raise last_exception
    
    def execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função síncrona com retry."""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"Retry successful on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self.strategy_manager.should_retry(e, self.config):
                    logger.warning(f"Non-retryable error on attempt {attempt}: {e}")
                    raise e
                
                if attempt < self.config.max_attempts:
                    delay = self.calculator.calculate_delay(attempt, self.config)
                    logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_attempts} attempts failed")
        
        raise last_exception


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    retryable_exceptions: List[Type[Exception]] = None,
    non_retryable_exceptions: List[Type[Exception]] = None,
    jitter: bool = True
):
    """Decorator para aplicar retry em funções."""
    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy,
            retryable_exceptions=retryable_exceptions,
            non_retryable_exceptions=non_retryable_exceptions,
            jitter=jitter
        )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return executor.execute_sync(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return await executor.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Configurações pré-definidas para diferentes cenários
API_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    jitter=True
)

DATABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=10.0,
    strategy=RetryStrategy.LINEAR_BACKOFF,
    jitter=False
)

EXTERNAL_SERVICE_RETRY_CONFIG = RetryConfig(
    max_attempts=7,
    base_delay=1.0,
    max_delay=60.0,
    strategy=RetryStrategy.FIBONACCI_BACKOFF,
    jitter=True
) 