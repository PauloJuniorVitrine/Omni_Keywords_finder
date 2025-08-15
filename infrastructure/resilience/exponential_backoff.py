"""
Exponential Backoff Implementation
==================================

Implementação especializada de exponential backoff para casos de uso específicos.
Otimizada para APIs externas com diferentes padrões de falha.

Tracing ID: EXPONENTIAL_BACKOFF_001_20250127
Ruleset: enterprise_control_layer.yaml
Execução: 2025-01-27T10:00:00Z
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class BackoffType(Enum):
    """Tipos de backoff disponíveis."""
    EXPONENTIAL = "exponential"
    EXPONENTIAL_WITH_JITTER = "exponential_with_jitter"
    EXPONENTIAL_WITH_CAP = "exponential_with_cap"
    EXPONENTIAL_WITH_DECAY = "exponential_with_decay"


@dataclass
class ExponentialBackoffConfig:
    """Configuração para exponential backoff."""
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    max_attempts: int = 5
    decay_factor: float = 0.9
    cap_enabled: bool = True
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if self.base_delay <= 0:
            raise ValueError("base_delay must be positive")
        if self.max_delay <= 0:
            raise ValueError("max_delay must be positive")
        if self.exponential_base <= 1:
            raise ValueError("exponential_base must be greater than 1")
        if self.jitter_factor < 0 or self.jitter_factor > 1:
            raise ValueError("jitter_factor must be between 0 and 1")


class ExponentialBackoffCalculator:
    """Calculadora de exponential backoff com diferentes estratégias."""
    
    def __init__(self, config: ExponentialBackoffConfig):
        self.config = config
    
    def calculate_delay(self, attempt: int) -> float:
        """Calcula o delay para uma tentativa específica."""
        if attempt <= 0:
            return 0
        
        # Cálculo base exponencial
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        
        # Aplicar cap se habilitado
        if self.config.cap_enabled:
            delay = min(delay, self.config.max_delay)
        
        # Aplicar jitter se habilitado
        if self.config.jitter:
            jitter = delay * self.config.jitter_factor * random.uniform(-1, 1)
            delay = max(0, delay + jitter)
        
        # Aplicar decay se configurado
        if hasattr(self.config, 'decay_factor') and self.config.decay_factor < 1:
            delay *= (self.config.decay_factor ** (attempt - 1))
        
        return max(0, delay)
    
    def calculate_delay_with_reset(self, attempt: int, last_success_time: float) -> float:
        """Calcula delay com reset baseado no tempo do último sucesso."""
        current_time = time.time()
        time_since_success = current_time - last_success_time
        
        # Reset se muito tempo passou desde o último sucesso
        if time_since_success > self.config.max_delay * 2:
            return self.config.base_delay
        
        return self.calculate_delay(attempt)


class AdaptiveExponentialBackoff:
    """Backoff exponencial adaptativo que se ajusta baseado no histórico."""
    
    def __init__(self, initial_config: ExponentialBackoffConfig):
        self.config = initial_config
        self.success_count = 0
        self.failure_count = 0
        self.last_success_time = time.time()
        self.last_failure_time = time.time()
        self.consecutive_failures = 0
    
    def record_success(self):
        """Registra um sucesso e ajusta a configuração."""
        self.success_count += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        
        # Reduz o delay base se muitos sucessos consecutivos
        if self.success_count > 10:
            self.config.base_delay = max(0.1, self.config.base_delay * 0.95)
            self.success_count = 0
    
    def record_failure(self):
        """Registra uma falha e ajusta a configuração."""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        
        # Aumenta o delay base se muitas falhas consecutivas
        if self.consecutive_failures > 3:
            self.config.base_delay = min(self.config.max_delay, self.config.base_delay * 1.2)
    
    def calculate_delay(self, attempt: int) -> float:
        """Calcula delay adaptativo."""
        calculator = ExponentialBackoffCalculator(self.config)
        return calculator.calculate_delay_with_reset(attempt, self.last_success_time)


class ExponentialBackoffExecutor:
    """Executor de operações com exponential backoff."""
    
    def __init__(self, config: ExponentialBackoffConfig):
        self.config = config
        self.calculator = ExponentialBackoffCalculator(config)
        self.adaptive_backoff = AdaptiveExponentialBackoff(config)
    
    async def execute_async(
        self, 
        func: Callable, 
        *args, 
        retryable_exceptions: List[Type[Exception]] = None,
        **kwargs
    ) -> Any:
        """Executa função assíncrona com exponential backoff."""
        if retryable_exceptions is None:
            retryable_exceptions = [Exception]
        
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                self.adaptive_backoff.record_success()
                
                if attempt > 1:
                    logger.info(f"Exponential backoff successful on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Verifica se é uma exceção retentável
                if not any(isinstance(e, exc_type) for exc_type in retryable_exceptions):
                    logger.warning(f"Non-retryable error on attempt {attempt}: {e}")
                    raise e
                
                self.adaptive_backoff.record_failure()
                
                if attempt < self.config.max_attempts:
                    delay = self.adaptive_backoff.calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {delay:.2f}s (exponential backoff)..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_attempts} attempts failed with exponential backoff")
        
        raise last_exception
    
    def execute_sync(
        self, 
        func: Callable, 
        *args, 
        retryable_exceptions: List[Type[Exception]] = None,
        **kwargs
    ) -> Any:
        """Executa função síncrona com exponential backoff."""
        if retryable_exceptions is None:
            retryable_exceptions = [Exception]
        
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                
                self.adaptive_backoff.record_success()
                
                if attempt > 1:
                    logger.info(f"Exponential backoff successful on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Verifica se é uma exceção retentável
                if not any(isinstance(e, exc_type) for exc_type in retryable_exceptions):
                    logger.warning(f"Non-retryable error on attempt {attempt}: {e}")
                    raise e
                
                self.adaptive_backoff.record_failure()
                
                if attempt < self.config.max_attempts:
                    delay = self.adaptive_backoff.calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {delay:.2f}s (exponential backoff)..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_attempts} attempts failed with exponential backoff")
        
        raise last_exception


def exponential_backoff(
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    max_attempts: int = 5,
    jitter: bool = True,
    jitter_factor: float = 0.1,
    retryable_exceptions: List[Type[Exception]] = None
):
    """Decorator para aplicar exponential backoff em funções."""
    def decorator(func: Callable) -> Callable:
        config = ExponentialBackoffConfig(
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            max_attempts=max_attempts,
            jitter=jitter,
            jitter_factor=jitter_factor
        )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return executor.execute_sync(func, *args, retryable_exceptions=retryable_exceptions, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return await executor.execute_async(func, *args, retryable_exceptions=retryable_exceptions, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Configurações pré-definidas para diferentes cenários
GOOGLE_API_BACKOFF_CONFIG = ExponentialBackoffConfig(
    base_delay=2.0,
    max_delay=30.0,
    exponential_base=2.0,
    max_attempts=5,
    jitter=True,
    jitter_factor=0.15
)

YOUTUBE_API_BACKOFF_CONFIG = ExponentialBackoffConfig(
    base_delay=1.0,
    max_delay=20.0,
    exponential_base=1.8,
    max_attempts=4,
    jitter=True,
    jitter_factor=0.1
)

REDDIT_API_BACKOFF_CONFIG = ExponentialBackoffConfig(
    base_delay=3.0,
    max_delay=45.0,
    exponential_base=2.2,
    max_attempts=6,
    jitter=True,
    jitter_factor=0.2
)

DATABASE_BACKOFF_CONFIG = ExponentialBackoffConfig(
    base_delay=0.5,
    max_delay=10.0,
    exponential_base=1.5,
    max_attempts=3,
    jitter=False
) 