"""
Bulkhead Pattern Implementation
==============================

Implementa o padrão Bulkhead para isolamento de recursos e falhas.
Baseado em padrões da indústria para resiliência em sistemas distribuídos.

Tracing ID: BULKHEAD_001_20250127
Ruleset: enterprise_control_layer.yaml
Execução: 2025-01-27T10:00:00Z
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union
from contextlib import asynccontextmanager, contextmanager

logger = logging.getLogger(__name__)


class BulkheadState(Enum):
    """Estados do bulkhead."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class BulkheadConfig:
    """Configuração para bulkhead."""
    max_concurrent_calls: int = 10
    max_wait_duration: float = 5.0
    max_failure_count: int = 5
    failure_threshold_percentage: float = 50.0
    recovery_timeout: float = 60.0
    isolation_timeout: float = 30.0
    name: str = "default"
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if self.max_concurrent_calls <= 0:
            raise ValueError("max_concurrent_calls must be positive")
        if self.max_wait_duration <= 0:
            raise ValueError("max_wait_duration must be positive")
        if self.max_failure_count <= 0:
            raise ValueError("max_failure_count must be positive")
        if not 0 <= self.failure_threshold_percentage <= 100:
            raise ValueError("failure_threshold_percentage must be between 0 and 100")


class BulkheadMetrics:
    """Métricas do bulkhead."""
    
    def __init__(self):
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0
        self.current_concurrent_calls = 0
        self.max_concurrent_calls_reached = 0
        self.last_failure_time = None
        self.last_success_time = None
    
    def record_call(self, success: bool):
        """Registra uma chamada."""
        self.total_calls += 1
        if success:
            self.successful_calls += 1
            self.last_success_time = time.time()
        else:
            self.failed_calls += 1
            self.last_failure_time = time.time()
    
    def record_rejection(self):
        """Registra uma rejeição."""
        self.rejected_calls += 1
    
    def record_concurrent_call(self):
        """Registra uma chamada concorrente."""
        self.current_concurrent_calls += 1
        if self.current_concurrent_calls > self.max_concurrent_calls_reached:
            self.max_concurrent_calls_reached = self.current_concurrent_calls
    
    def record_concurrent_call_end(self):
        """Registra o fim de uma chamada concorrente."""
        self.current_concurrent_calls = max(0, self.current_concurrent_calls - 1)
    
    def get_failure_rate(self) -> float:
        """Calcula a taxa de falha."""
        if self.total_calls == 0:
            return 0.0
        return (self.failed_calls / self.total_calls) * 100
    
    def get_success_rate(self) -> float:
        """Calcula a taxa de sucesso."""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
    
    def reset(self):
        """Reseta as métricas."""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0
        self.current_concurrent_calls = 0
        self.max_concurrent_calls_reached = 0
        self.last_failure_time = None
        self.last_success_time = None


class Bulkhead:
    """Implementação do padrão Bulkhead."""
    
    def __init__(self, config: BulkheadConfig):
        self.config = config
        self.state = BulkheadState.CLOSED
        self.metrics = BulkheadMetrics()
        self._lock = threading.RLock()
        self._semaphore = asyncio.Semaphore(config.max_concurrent_calls)
        self._failure_count = 0
        self._last_failure_time = None
        self._recovery_timer = None
    
    def _should_open_bulkhead(self) -> bool:
        """Determina se o bulkhead deve ser aberto."""
        if self._failure_count >= self.config.max_failure_count:
            return True
        
        if self.metrics.get_failure_rate() >= self.config.failure_threshold_percentage:
            return True
        
        return False
    
    def _should_close_bulkhead(self) -> bool:
        """Determina se o bulkhead deve ser fechado."""
        if self.state != BulkheadState.OPEN:
            return False
        
        # Verifica se passou tempo suficiente para tentar recuperação
        if self._last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self._last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _record_failure(self):
        """Registra uma falha."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            self.metrics.record_call(success=False)
            
            if self._should_open_bulkhead():
                self.state = BulkheadState.OPEN
                logger.warning(f"Bulkhead '{self.config.name}' opened due to failures")
    
    def _record_success(self):
        """Registra um sucesso."""
        with self._lock:
            self._failure_count = 0
            self.metrics.record_call(success=True)
            
            if self.state == BulkheadState.OPEN and self._should_close_bulkhead():
                self.state = BulkheadState.CLOSED
                logger.info(f"Bulkhead '{self.config.name}' closed after recovery")
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função assíncrona com bulkhead."""
        # Verifica se o bulkhead está aberto
        if self.state == BulkheadState.OPEN:
            self.metrics.record_rejection()
            raise BulkheadOpenError(f"Bulkhead '{self.config.name}' is open")
        
        # Tenta adquirir semáforo
        try:
            await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=self.config.max_wait_duration
            )
        except asyncio.TimeoutError:
            self.metrics.record_rejection()
            raise BulkheadTimeoutError(f"Bulkhead '{self.config.name}' timeout")
        
        try:
            self.metrics.record_concurrent_call()
            
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Executa função síncrona em thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, *args, **kwargs)
            
            self._record_success()
            return result
            
        except Exception as e:
            self._record_failure()
            raise e
        finally:
            self._semaphore.release()
            self.metrics.record_concurrent_call_end()
    
    def execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função síncrona com bulkhead."""
        # Verifica se o bulkhead está aberto
        if self.state == BulkheadState.OPEN:
            self.metrics.record_rejection()
            raise BulkheadOpenError(f"Bulkhead '{self.config.name}' is open")
        
        # Tenta adquirir semáforo
        try:
            if not self._semaphore.locked():
                self._semaphore.acquire()
            else:
                # Para operações síncronas, usa timeout simples
                start_time = time.time()
                while self._semaphore.locked():
                    if time.time() - start_time > self.config.max_wait_duration:
                        self.metrics.record_rejection()
                        raise BulkheadTimeoutError(f"Bulkhead '{self.config.name}' timeout")
                    time.sleep(0.01)
                self._semaphore.acquire()
        except Exception:
            self.metrics.record_rejection()
            raise BulkheadTimeoutError(f"Bulkhead '{self.config.name}' timeout")
        
        try:
            self.metrics.record_concurrent_call()
            result = func(*args, **kwargs)
            self._record_success()
            return result
            
        except Exception as e:
            self._record_failure()
            raise e
        finally:
            self._semaphore.release()
            self.metrics.record_concurrent_call_end()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do bulkhead."""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "total_calls": self.metrics.total_calls,
            "successful_calls": self.metrics.successful_calls,
            "failed_calls": self.metrics.failed_calls,
            "rejected_calls": self.metrics.rejected_calls,
            "current_concurrent_calls": self.metrics.current_concurrent_calls,
            "max_concurrent_calls_reached": self.metrics.max_concurrent_calls_reached,
            "failure_rate": self.metrics.get_failure_rate(),
            "success_rate": self.metrics.get_success_rate(),
            "failure_count": self._failure_count,
            "last_failure_time": self._last_failure_time,
            "last_success_time": self.metrics.last_success_time
        }
    
    def reset(self):
        """Reseta o bulkhead."""
        with self._lock:
            self.state = BulkheadState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None
            self.metrics.reset()
            # Reseta o semáforo
            while not self._semaphore.locked():
                self._semaphore.release()


class BulkheadError(Exception):
    """Exceção base para erros de bulkhead."""
    pass


class BulkheadOpenError(BulkheadError):
    """Exceção quando o bulkhead está aberto."""
    pass


class BulkheadTimeoutError(BulkheadError):
    """Exceção quando há timeout no bulkhead."""
    pass


def bulkhead(
    max_concurrent_calls: int = 10,
    max_wait_duration: float = 5.0,
    max_failure_count: int = 5,
    failure_threshold_percentage: float = 50.0,
    recovery_timeout: float = 60.0,
    name: str = "default"
):
    """Decorator para aplicar bulkhead em funções."""
    def decorator(func: Callable) -> Callable:
        config = BulkheadConfig(
            max_concurrent_calls=max_concurrent_calls,
            max_wait_duration=max_wait_duration,
            max_failure_count=max_failure_count,
            failure_threshold_percentage=failure_threshold_percentage,
            recovery_timeout=recovery_timeout,
            name=name
        )
        bulkhead_instance = Bulkhead(config)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return bulkhead_instance.execute_sync(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await bulkhead_instance.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Configurações pré-definidas para diferentes cenários
API_BULKHEAD_CONFIG = BulkheadConfig(
    max_concurrent_calls=20,
    max_wait_duration=10.0,
    max_failure_count=10,
    failure_threshold_percentage=30.0,
    recovery_timeout=120.0,
    name="api_bulkhead"
)

DATABASE_BULKHEAD_CONFIG = BulkheadConfig(
    max_concurrent_calls=5,
    max_wait_duration=5.0,
    max_failure_count=3,
    failure_threshold_percentage=20.0,
    recovery_timeout=60.0,
    name="database_bulkhead"
)

FILE_OPERATION_BULKHEAD_CONFIG = BulkheadConfig(
    max_concurrent_calls=3,
    max_wait_duration=3.0,
    max_failure_count=5,
    failure_threshold_percentage=40.0,
    recovery_timeout=30.0,
    name="file_operation_bulkhead"
)

CRITICAL_OPERATION_BULKHEAD_CONFIG = BulkheadConfig(
    max_concurrent_calls=2,
    max_wait_duration=15.0,
    max_failure_count=2,
    failure_threshold_percentage=10.0,
    recovery_timeout=300.0,
    name="critical_operation_bulkhead"
) 