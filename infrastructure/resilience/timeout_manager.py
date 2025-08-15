"""
Timeout Manager Implementation
=============================

Implementa gerenciamento de timeout para operações com controle granular.
Baseado em padrões da indústria para resiliência em sistemas distribuídos.

Tracing ID: TIMEOUT_MANAGER_001_20250127
Ruleset: enterprise_control_layer.yaml
Execução: 2025-01-27T10:00:00Z
"""

import asyncio
import logging
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union
from contextlib import asynccontextmanager, contextmanager

logger = logging.getLogger(__name__)


class TimeoutStrategy(Enum):
    """Estratégias de timeout disponíveis."""
    CANCEL_OPERATION = "cancel_operation"
    RETURN_DEFAULT = "return_default"
    RAISE_EXCEPTION = "raise_exception"
    RETRY_WITH_BACKOFF = "retry_with_backoff"


@dataclass
class TimeoutConfig:
    """Configuração para timeout."""
    timeout_seconds: float = 30.0
    strategy: TimeoutStrategy = TimeoutStrategy.RAISE_EXCEPTION
    default_value: Any = None
    retry_attempts: int = 3
    retry_backoff_factor: float = 2.0
    name: str = "default"
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be non-negative")
        if self.retry_backoff_factor <= 0:
            raise ValueError("retry_backoff_factor must be positive")


class TimeoutError(Exception):
    """Exceção para timeout."""
    def __init__(self, message: str, operation_name: str = None, timeout_seconds: float = None):
        super().__init__(message)
        self.operation_name = operation_name
        self.timeout_seconds = timeout_seconds


class TimeoutManager:
    """Gerenciador de timeout para operações."""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._task_lock = threading.Lock()
    
    async def execute_async(
        self, 
        func: Callable, 
        *args, 
        timeout_override: Optional[float] = None,
        **kwargs
    ) -> Any:
        """Executa função assíncrona com timeout."""
        timeout = timeout_override or self.config.timeout_seconds
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            else:
                # Executa função síncrona em thread pool
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(self._executor, func, *args, **kwargs),
                    timeout=timeout
                )
            
            return result
            
        except asyncio.TimeoutError:
            await self._handle_timeout(func, args, kwargs, timeout)
    
    def execute_sync(
        self, 
        func: Callable, 
        *args, 
        timeout_override: Optional[float] = None,
        **kwargs
    ) -> Any:
        """Executa função síncrona com timeout."""
        timeout = timeout_override or self.config.timeout_seconds
        
        try:
            future = self._executor.submit(func, *args, **kwargs)
            result = future.result(timeout=timeout)
            return result
            
        except FutureTimeoutError:
            self._handle_sync_timeout(func, args, kwargs, timeout)
    
    async def _handle_timeout(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: dict, 
        timeout: float
    ) -> Any:
        """Gerencia timeout para operações assíncronas."""
        logger.warning(
            f"Operation '{self.config.name}' timed out after {timeout}s"
        )
        
        if self.config.strategy == TimeoutStrategy.RETURN_DEFAULT:
            return self.config.default_value
        
        elif self.config.strategy == TimeoutStrategy.RETRY_WITH_BACKOFF:
            return await self._retry_with_backoff(func, args, kwargs, timeout)
        
        else:  # RAISE_EXCEPTION
            raise TimeoutError(
                f"Operation '{self.config.name}' timed out after {timeout}s",
                self.config.name,
                timeout
            )
    
    def _handle_sync_timeout(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: dict, 
        timeout: float
    ) -> Any:
        """Gerencia timeout para operações síncronas."""
        logger.warning(
            f"Operation '{self.config.name}' timed out after {timeout}s"
        )
        
        if self.config.strategy == TimeoutStrategy.RETURN_DEFAULT:
            return self.config.default_value
        
        elif self.config.strategy == TimeoutStrategy.RETRY_WITH_BACKOFF:
            return self._retry_sync_with_backoff(func, args, kwargs, timeout)
        
        else:  # RAISE_EXCEPTION
            raise TimeoutError(
                f"Operation '{self.config.name}' timed out after {timeout}s",
                self.config.name,
                timeout
            )
    
    async def _retry_with_backoff(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: dict, 
        base_timeout: float
    ) -> Any:
        """Retenta operação com backoff exponencial."""
        for attempt in range(self.config.retry_attempts):
            try:
                # Aumenta timeout para cada tentativa
                timeout = base_timeout * (self.config.retry_backoff_factor ** attempt)
                
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                else:
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(self._executor, func, *args, **kwargs),
                        timeout=timeout
                    )
                
                logger.info(f"Operation '{self.config.name}' succeeded on retry attempt {attempt + 1}")
                return result
                
            except asyncio.TimeoutError:
                logger.warning(
                    f"Operation '{self.config.name}' timed out on retry attempt {attempt + 1}"
                )
                if attempt == self.config.retry_attempts - 1:
                    # Última tentativa falhou
                    if self.config.strategy == TimeoutStrategy.RETURN_DEFAULT:
                        return self.config.default_value
                    else:
                        raise TimeoutError(
                            f"Operation '{self.config.name}' failed after {self.config.retry_attempts} retries",
                            self.config.name,
                            base_timeout
                        )
        
        return self.config.default_value
    
    def _retry_sync_with_backoff(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: dict, 
        base_timeout: float
    ) -> Any:
        """Retenta operação síncrona com backoff exponencial."""
        for attempt in range(self.config.retry_attempts):
            try:
                # Aumenta timeout para cada tentativa
                timeout = base_timeout * (self.config.retry_backoff_factor ** attempt)
                
                future = self._executor.submit(func, *args, **kwargs)
                result = future.result(timeout=timeout)
                
                logger.info(f"Operation '{self.config.name}' succeeded on retry attempt {attempt + 1}")
                return result
                
            except FutureTimeoutError:
                logger.warning(
                    f"Operation '{self.config.name}' timed out on retry attempt {attempt + 1}"
                )
                if attempt == self.config.retry_attempts - 1:
                    # Última tentativa falhou
                    if self.config.strategy == TimeoutStrategy.RETURN_DEFAULT:
                        return self.config.default_value
                    else:
                        raise TimeoutError(
                            f"Operation '{self.config.name}' failed after {self.config.retry_attempts} retries",
                            self.config.name,
                            base_timeout
                        )
        
        return self.config.default_value
    
    def cancel_all_tasks(self):
        """Cancela todas as tarefas ativas."""
        with self._task_lock:
            for task_id, task in self._active_tasks.items():
                if not task.done():
                    task.cancel()
                    logger.info(f"Cancelled task: {task_id}")
    
    def shutdown(self):
        """Desliga o gerenciador de timeout."""
        self.cancel_all_tasks()
        self._executor.shutdown(wait=True)


class TimeoutDecorator:
    """Decorator para aplicar timeout em funções."""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
        self.manager = TimeoutManager(config)
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return self.manager.execute_sync(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self.manager.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


def timeout(
    timeout_seconds: float = 30.0,
    strategy: TimeoutStrategy = TimeoutStrategy.RAISE_EXCEPTION,
    default_value: Any = None,
    retry_attempts: int = 3,
    retry_backoff_factor: float = 2.0,
    name: str = "default"
):
    """Decorator para aplicar timeout em funções."""
    def decorator(func: Callable) -> Callable:
        config = TimeoutConfig(
            timeout_seconds=timeout_seconds,
            strategy=strategy,
            default_value=default_value,
            retry_attempts=retry_attempts,
            retry_backoff_factor=retry_backoff_factor,
            name=name
        )
        return TimeoutDecorator(config)(func)
    
    return decorator


@asynccontextmanager
async def timeout_context(timeout_seconds: float, operation_name: str = "operation"):
    """Context manager para timeout."""
    try:
        yield
    except asyncio.TimeoutError:
        logger.warning(f"Operation '{operation_name}' timed out after {timeout_seconds}s")
        raise TimeoutError(
            f"Operation '{operation_name}' timed out after {timeout_seconds}s",
            operation_name,
            timeout_seconds
        )


@contextmanager
def timeout_context_sync(timeout_seconds: float, operation_name: str = "operation"):
    """Context manager síncrono para timeout."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError(
            f"Operation '{operation_name}' timed out after {timeout_seconds}s",
            operation_name,
            timeout_seconds
        )
    
    # Configura signal handler para timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(timeout_seconds))
    
    try:
        yield
    finally:
        signal.alarm(0)  # Cancela o alarme
        signal.signal(signal.SIGALRM, old_handler)  # Restaura handler original


# Configurações pré-definidas para diferentes cenários
API_TIMEOUT_CONFIG = TimeoutConfig(
    timeout_seconds=30.0,
    strategy=TimeoutStrategy.RETRY_WITH_BACKOFF,
    retry_attempts=3,
    retry_backoff_factor=2.0,
    name="api_timeout"
)

DATABASE_TIMEOUT_CONFIG = TimeoutConfig(
    timeout_seconds=10.0,
    strategy=TimeoutStrategy.RAISE_EXCEPTION,
    name="database_timeout"
)

FILE_OPERATION_TIMEOUT_CONFIG = TimeoutConfig(
    timeout_seconds=5.0,
    strategy=TimeoutStrategy.RETURN_DEFAULT,
    default_value=None,
    name="file_operation_timeout"
)

CRITICAL_OPERATION_TIMEOUT_CONFIG = TimeoutConfig(
    timeout_seconds=60.0,
    strategy=TimeoutStrategy.RETRY_WITH_BACKOFF,
    retry_attempts=5,
    retry_backoff_factor=1.5,
    name="critical_operation_timeout"
)

FAST_OPERATION_TIMEOUT_CONFIG = TimeoutConfig(
    timeout_seconds=1.0,
    strategy=TimeoutStrategy.RETURN_DEFAULT,
    default_value=None,
    name="fast_operation_timeout"
)


# Decorators de conveniência para casos específicos
timeout_api_call = timeout(30.0, TimeoutStrategy.RETRY_WITH_BACKOFF, retry_attempts=3, name="api_call")
timeout_database_query = timeout(10.0, TimeoutStrategy.RAISE_EXCEPTION, name="database_query")
timeout_file_operation = timeout(5.0, TimeoutStrategy.RETURN_DEFAULT, name="file_operation")
timeout_critical_operation = timeout(60.0, TimeoutStrategy.RETRY_WITH_BACKOFF, retry_attempts=5, name="critical_operation")
timeout_fast_operation = timeout(1.0, TimeoutStrategy.RETURN_DEFAULT, name="fast_operation") 