"""
Error Handler - Omni Keywords Finder

Sistema centralizado de tratamento de erros com circuit breaker,
retry logic com exponential backoff e logging estruturado.

Tracing ID: ERROR_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import time
import logging
import functools
from typing import Dict, Any, Optional, Callable, Type, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
import traceback

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Níveis de severidade de erro."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Tipos de erro categorizados."""
    NETWORK = "network"
    API_LIMIT = "api_limit"
    VALIDATION = "validation"
    PROCESSING = "processing"
    STORAGE = "storage"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Informações detalhadas sobre um erro."""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    @property
    def should_retry(self) -> bool:
        """Verifica se o erro deve ser retry."""
        return self.retry_count < self.max_retries and self.severity != ErrorSeverity.CRITICAL


@dataclass
class CircuitBreakerState:
    """Estado do circuit breaker."""
    name: str
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    threshold: int = 5
    timeout_seconds: int = 60
    success_count: int = 0
    success_threshold: int = 2
    
    def should_allow_request(self) -> bool:
        """Verifica se a requisição deve ser permitida."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def on_success(self):
        """Chamado quando uma requisição é bem-sucedida."""
        self.success_count += 1
        self.failure_count = 0
        
        if self.state == "HALF_OPEN" and self.success_count >= self.success_threshold:
            self.state = "CLOSED"
            self.success_count = 0
            logger.info(f"Circuit breaker '{self.name}' fechado (sucesso)")
    
    def on_failure(self):
        """Chamado quando uma requisição falha."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker '{self.name}' aberto (falhas: {self.failure_count})")


class ErrorHandler:
    """Sistema centralizado de tratamento de erros."""
    
    def __init__(self):
        """Inicializa o error handler."""
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.error_history: Dict[str, list] = {}
        self.lock = threading.Lock()
        
        logger.info("ErrorHandler inicializado")
    
    def register_circuit_breaker(
        self, 
        name: str, 
        threshold: int = 5, 
        timeout_seconds: int = 60
    ) -> CircuitBreakerState:
        """
        Registra um novo circuit breaker.
        
        Args:
            name: Nome do circuit breaker
            threshold: Número de falhas para abrir
            timeout_seconds: Tempo para tentar fechar novamente
            
        Returns:
            CircuitBreakerState criado
        """
        with self.lock:
            circuit_breaker = CircuitBreakerState(
                name=name,
                threshold=threshold,
                timeout_seconds=timeout_seconds
            )
            self.circuit_breakers[name] = circuit_breaker
            
            logger.info(f"Circuit breaker registrado: {name}")
            return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreakerState]:
        """Obtém um circuit breaker pelo nome."""
        return self.circuit_breakers.get(name)
    
    def with_circuit_breaker(
        self, 
        name: str, 
        threshold: int = 5, 
        timeout_seconds: int = 60
    ):
        """
        Decorator para aplicar circuit breaker a uma função.
        
        Args:
            name: Nome do circuit breaker
            threshold: Número de falhas para abrir
            timeout_seconds: Tempo para tentar fechar novamente
        """
        def decorator(func: Callable) -> Callable:
            circuit_breaker = self.register_circuit_breaker(name, threshold, timeout_seconds)
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not circuit_breaker.should_allow_request():
                    raise Exception(f"Circuit breaker '{name}' está aberto")
                
                try:
                    result = func(*args, **kwargs)
                    circuit_breaker.on_success()
                    return result
                except Exception as e:
                    circuit_breaker.on_failure()
                    raise e
            
            return wrapper
        return decorator
    
    def with_retry(
        self, 
        max_retries: int = 3, 
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Decorator para aplicar retry logic com exponential backoff.
        
        Args:
            max_retries: Número máximo de tentativas
            base_delay: Delay inicial em segundos
            max_delay: Delay máximo em segundos
            exponential_base: Base para cálculo exponencial
            exceptions: Tipos de exceção para retry
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == max_retries:
                            logger.error(f"Função {func.__name__} falhou após {max_retries} tentativas: {e}")
                            raise e
                        
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)
                        logger.warning(f"Tentativa {attempt + 1} falhou para {func.__name__}, retry em {delay:.1f}string_data: {e}")
                        time.sleep(delay)
                
                raise last_exception
            
            return wrapper
        return decorator
    
    def handle_error(
        self, 
        error: Exception, 
        error_type: ErrorType = ErrorType.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorInfo:
        """
        Processa um erro e retorna informações estruturadas.
        
        Args:
            error: Exceção capturada
            error_type: Tipo do erro
            severity: Severidade do erro
            context: Contexto adicional
            
        Returns:
            ErrorInfo com detalhes do erro
        """
        error_info = ErrorInfo(
            error_type=error_type,
            severity=severity,
            message=str(error),
            context=context or {},
            traceback=traceback.format_exc()
        )
        
        # Log baseado na severidade
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"ERRO CRÍTICO [{error_type.value}]: {error}")
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"ERRO ALTO [{error_type.value}]: {error}")
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"ERRO MÉDIO [{error_type.value}]: {error}")
        else:
            logger.info(f"ERRO BAIXO [{error_type.value}]: {error}")
        
        # Armazenar no histórico
        with self.lock:
            if error_type.value not in self.error_history:
                self.error_history[error_type.value] = []
            self.error_history[error_type.value].append(error_info)
        
        return error_info
    
    def classify_error(self, error: Exception) -> tuple[ErrorType, ErrorSeverity]:
        """
        Classifica automaticamente um erro.
        
        Args:
            error: Exceção para classificar
            
        Returns:
            Tupla (ErrorType, ErrorSeverity)
        """
        error_str = str(error).lower()
        
        # Classificação por tipo
        if any(word in error_str for word in ['timeout', 'timed out', 'connection']):
            return ErrorType.TIMEOUT, ErrorSeverity.MEDIUM
        elif any(word in error_str for word in ['rate limit', 'quota', 'limit exceeded']):
            return ErrorType.API_LIMIT, ErrorSeverity.HIGH
        elif any(word in error_str for word in ['network', 'connection', 'http']):
            return ErrorType.NETWORK, ErrorSeverity.MEDIUM
        elif any(word in error_str for word in ['validation', 'invalid', 'format']):
            return ErrorType.VALIDATION, ErrorSeverity.LOW
        elif any(word in error_str for word in ['storage', 'disk', 'file']):
            return ErrorType.STORAGE, ErrorSeverity.HIGH
        elif any(word in error_str for word in ['processing', 'algorithm', 'computation']):
            return ErrorType.PROCESSING, ErrorSeverity.MEDIUM
        else:
            return ErrorType.UNKNOWN, ErrorSeverity.MEDIUM
    
    def safe_execute(
        self, 
        func: Callable, 
        *args, 
        error_type: Optional[ErrorType] = None,
        severity: Optional[ErrorSeverity] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Executa uma função de forma segura com tratamento de erro.
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            error_type: Tipo de erro (se None, classifica automaticamente)
            severity: Severidade (se None, classifica automaticamente)
            context: Contexto adicional
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função ou None se falhar
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if error_type is None or severity is None:
                error_type, severity = self.classify_error(e)
            
            error_info = self.handle_error(e, error_type, severity, context)
            
            if error_info.should_retry:
                logger.info(f"Tentando retry para {func.__name__}")
                return self.safe_execute(func, *args, error_type=error_type, 
                                       severity=severity, context=context, **kwargs)
            
            return None
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de erros."""
        with self.lock:
            stats = {
                "total_errors": sum(len(errors) for errors in self.error_history.values()),
                "errors_by_type": {error_type: len(errors) for error_type, errors in self.error_history.items()},
                "circuit_breakers": {
                    name: {
                        "state": cb.state,
                        "failure_count": cb.failure_count,
                        "success_count": cb.success_count
                    } for name, cb in self.circuit_breakers.items()
                }
            }
            return stats
    
    def clear_error_history(self):
        """Limpa o histórico de erros."""
        with self.lock:
            self.error_history.clear()
            logger.info("Histórico de erros limpo")
    
    def reset_circuit_breakers(self):
        """Reseta todos os circuit breakers."""
        with self.lock:
            for cb in self.circuit_breakers.values():
                cb.state = "CLOSED"
                cb.failure_count = 0
                cb.success_count = 0
            logger.info("Circuit breakers resetados")


# Instância global
error_handler = ErrorHandler()


def obter_error_handler() -> ErrorHandler:
    """Obtém a instância global do error handler."""
    return error_handler


# Decorators úteis
def with_error_handling(
    error_type: Optional[ErrorType] = None,
    severity: Optional[ErrorSeverity] = None
):
    """
    Decorator para aplicar tratamento de erro automático.
    
    Args:
        error_type: Tipo de erro específico
        severity: Severidade específica
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return error_handler.safe_execute(
                func, *args, 
                error_type=error_type, 
                severity=severity, 
                context={"function": func.__name__},
                **kwargs
            )
        return wrapper
    return decorator


def with_circuit_breaker_and_retry(
    circuit_breaker_name: str,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """
    Decorator combinando circuit breaker e retry.
    
    Args:
        circuit_breaker_name: Nome do circuit breaker
        max_retries: Número máximo de tentativas
        base_delay: Delay base para retry
    """
    def decorator(func: Callable) -> Callable:
        @error_handler.with_circuit_breaker(circuit_breaker_name)
        @error_handler.with_retry(max_retries=max_retries, base_delay=base_delay)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator 