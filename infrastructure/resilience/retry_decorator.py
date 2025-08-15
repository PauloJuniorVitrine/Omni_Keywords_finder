"""
Retry Decorator Implementation
==============================

Decorators especializados para retry com configurações específicas por contexto.
Facilita a aplicação de retry em diferentes tipos de operações.

Tracing ID: RETRY_DECORATOR_001_20250127
Ruleset: enterprise_control_layer.yaml
Execução: 2025-01-27T10:00:00Z
"""

import asyncio
import functools
import logging
from typing import Any, Callable, List, Type, Union

from .retry_strategy import RetryConfig, RetryStrategy, RetryExecutor
from .exponential_backoff import ExponentialBackoffConfig, ExponentialBackoffExecutor

logger = logging.getLogger(__name__)


def retry_api_call(
    max_attempts: int = 5,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    retryable_exceptions: List[Type[Exception]] = None
):
    """
    Decorator para chamadas de API externas.
    Configuração otimizada para APIs com rate limiting.
    """
    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.15,
            retryable_exceptions=retryable_exceptions or [
                ConnectionError, TimeoutError, OSError
            ]
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return executor.execute_sync(func, *args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return await executor.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_database_operation(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retryable_exceptions: List[Type[Exception]] = None
):
    """
    Decorator para operações de banco de dados.
    Configuração otimizada para falhas transitórias de DB.
    """
    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=False,
            retryable_exceptions=retryable_exceptions or [
                ConnectionError, TimeoutError
            ]
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return executor.execute_sync(func, *args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return await executor.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_file_operation(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    retryable_exceptions: List[Type[Exception]] = None
):
    """
    Decorator para operações de arquivo.
    Configuração otimizada para operações de I/O.
    """
    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.1,
            retryable_exceptions=retryable_exceptions or [
                OSError, IOError, PermissionError
            ]
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return executor.execute_sync(func, *args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return await executor.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_google_api(
    max_attempts: int = 5,
    base_delay: float = 2.0,
    max_delay: float = 30.0
):
    """
    Decorator específico para APIs do Google.
    Configuração otimizada para rate limiting do Google.
    """
    def decorator(func: Callable) -> Callable:
        config = ExponentialBackoffConfig(
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=2.0,
            max_attempts=max_attempts,
            jitter=True,
            jitter_factor=0.15
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return executor.execute_sync(
                func, 
                *args, 
                retryable_exceptions=[
                    ConnectionError, TimeoutError, OSError, 
                    Exception  # Google APIs podem retornar diferentes tipos de erro
                ],
                **kwargs
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return await executor.execute_async(
                func, 
                *args, 
                retryable_exceptions=[
                    ConnectionError, TimeoutError, OSError,
                    Exception
                ],
                **kwargs
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_youtube_api(
    max_attempts: int = 4,
    base_delay: float = 1.0,
    max_delay: float = 20.0
):
    """
    Decorator específico para APIs do YouTube.
    Configuração otimizada para rate limiting do YouTube.
    """
    def decorator(func: Callable) -> Callable:
        config = ExponentialBackoffConfig(
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=1.8,
            max_attempts=max_attempts,
            jitter=True,
            jitter_factor=0.1
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return executor.execute_sync(
                func, 
                *args, 
                retryable_exceptions=[
                    ConnectionError, TimeoutError, OSError,
                    Exception
                ],
                **kwargs
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return await executor.execute_async(
                func, 
                *args, 
                retryable_exceptions=[
                    ConnectionError, TimeoutError, OSError,
                    Exception
                ],
                **kwargs
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_reddit_api(
    max_attempts: int = 6,
    base_delay: float = 3.0,
    max_delay: float = 45.0
):
    """
    Decorator específico para APIs do Reddit.
    Configuração otimizada para rate limiting do Reddit.
    """
    def decorator(func: Callable) -> Callable:
        config = ExponentialBackoffConfig(
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=2.2,
            max_attempts=max_attempts,
            jitter=True,
            jitter_factor=0.2
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return executor.execute_sync(
                func, 
                *args, 
                retryable_exceptions=[
                    ConnectionError, TimeoutError, OSError,
                    Exception
                ],
                **kwargs
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return await executor.execute_async(
                func, 
                *args, 
                retryable_exceptions=[
                    ConnectionError, TimeoutError, OSError,
                    Exception
                ],
                **kwargs
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_network_operation(
    max_attempts: int = 4,
    base_delay: float = 1.0,
    max_delay: float = 15.0
):
    """
    Decorator para operações de rede.
    Configuração otimizada para falhas de conectividade.
    """
    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            jitter_factor=0.1,
            retryable_exceptions=[
                ConnectionError, TimeoutError, OSError,
                ConnectionRefusedError, ConnectionResetError
            ]
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return executor.execute_sync(func, *args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return await executor.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_critical_operation(
    max_attempts: int = 7,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """
    Decorator para operações críticas.
    Configuração com mais tentativas para operações essenciais.
    """
    def decorator(func: Callable) -> Callable:
        config = ExponentialBackoffConfig(
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=2.0,
            max_attempts=max_attempts,
            jitter=True,
            jitter_factor=0.15
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return executor.execute_sync(
                func, 
                *args, 
                retryable_exceptions=[Exception],  # Retenta qualquer exceção
                **kwargs
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            executor = ExponentialBackoffExecutor(config)
            return await executor.execute_async(
                func, 
                *args, 
                retryable_exceptions=[Exception],
                **kwargs
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Decorators de conveniência para casos específicos
retry_google_keyword_planner = retry_google_api(max_attempts=5, base_delay=2.0, max_delay=30.0)
retry_youtube_search = retry_youtube_api(max_attempts=4, base_delay=1.0, max_delay=20.0)
retry_reddit_search = retry_reddit_api(max_attempts=6, base_delay=3.0, max_delay=45.0)
retry_database_query = retry_database_operation(max_attempts=3, base_delay=1.0, max_delay=10.0)
retry_file_read = retry_file_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
retry_network_request = retry_network_operation(max_attempts=4, base_delay=1.0, max_delay=15.0) 