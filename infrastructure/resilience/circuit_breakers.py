"""
Sistema de Circuit Breakers e Resiliência
Tracing ID: IMP004_CIRCUIT_BREAKERS_001
Data: 2025-01-27
Versão: 1.0
Status: Em Implementação

Sistema avançado de circuit breakers com:
- Múltiplos estados (Closed, Open, Half-Open)
- Fallback strategies
- Retry policies
- Timeout policies
- Bulkhead pattern
- Graceful degradation
"""

import time
import asyncio
import logging
import random
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import statistics
from functools import wraps

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Estados do circuit breaker"""
    CLOSED = "closed"      # Funcionando normalmente
    OPEN = "open"          # Circuito aberto (falhas)
    HALF_OPEN = "half_open"  # Testando se pode fechar

class FailureType(Enum):
    """Tipos de falha"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    HTTP_ERROR = "http_error"
    CONNECTION_ERROR = "connection_error"
    RATE_LIMIT = "rate_limit"

@dataclass
class CircuitBreakerConfig:
    """Configuração do circuit breaker"""
    failure_threshold: int = 5           # Número de falhas para abrir
    recovery_timeout: int = 60           # Tempo para tentar fechar (segundos)
    expected_exception: type = Exception # Exceção esperada
    timeout: float = 30.0                # Timeout da operação
    max_retries: int = 3                 # Máximo de tentativas
    retry_delay: float = 1.0             # Delay entre tentativas
    success_threshold: int = 2           # Sucessos para fechar
    monitor_interval: int = 10           # Intervalo de monitoramento

@dataclass
class RetryConfig:
    """Configuração de retry"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[type] = field(default_factory=lambda: [Exception])

@dataclass
class TimeoutConfig:
    """Configuração de timeout"""
    default_timeout: float = 30.0
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0

@dataclass
class BulkheadConfig:
    """Configuração do bulkhead pattern"""
    max_concurrent_calls: int = 10
    max_wait_duration: float = 60.0
    max_queue_size: int = 100

class CircuitBreaker:
    """Implementação do circuit breaker pattern"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()
        self._lock = threading.Lock()
        
        # Métricas
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_timeouts = 0
        
        # Histórico de latência
        self.response_times = []
        self.max_history_size = 100
        
        logger.info(f"Circuit Breaker '{name}' inicializado")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com circuit breaker"""
        self.total_requests += 1
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._set_state(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' está aberto")
        
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self._on_success(execution_time)
            return result
            
        except Exception as e:
            self._on_failure(e)
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função assíncrona com circuit breaker"""
        self.total_requests += 1
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._set_state(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' está aberto")
        
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self._on_success(execution_time)
            return result
            
        except Exception as e:
            self._on_failure(e)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuit breaker"""
        if self.last_failure_time is None:
            return False
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout
    
    def _on_success(self, execution_time: float):
        """Chamado quando a operação é bem-sucedida"""
        with self._lock:
            self.success_count += 1
            self.failure_count = 0
            self.total_successes += 1
            
            # Adicionar tempo de resposta ao histórico
            self.response_times.append(execution_time)
            if len(self.response_times) > self.max_history_size:
                self.response_times.pop(0)
            
            if self.state == CircuitState.HALF_OPEN:
                if self.success_count >= self.config.success_threshold:
                    self._set_state(CircuitState.CLOSED)
                    logger.info(f"Circuit breaker '{self.name}' fechado após {self.success_count} sucessos")
    
    def _on_failure(self, exception: Exception):
        """Chamado quando a operação falha"""
        with self._lock:
            self.failure_count += 1
            self.total_failures += 1
            self.last_failure_time = datetime.now()
            
            if isinstance(exception, TimeoutError):
                self.total_timeouts += 1
            
            if self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self._set_state(CircuitState.OPEN)
                    logger.warning(f"Circuit breaker '{self.name}' aberto após {self.failure_count} falhas")
            elif self.state == CircuitState.HALF_OPEN:
                self._set_state(CircuitState.OPEN)
                logger.warning(f"Circuit breaker '{self.name}' reaberto após falha em half-open")
    
    def _set_state(self, new_state: CircuitState):
        """Altera o estado do circuit breaker"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.last_state_change = datetime.now()
            
            if new_state == CircuitState.CLOSED:
                self.success_count = 0
            elif new_state == CircuitState.OPEN:
                self.success_count = 0
            
            logger.info(f"Circuit breaker '{self.name}' mudou de {old_state.value} para {new_state.value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do circuit breaker"""
        with self._lock:
            success_rate = (self.total_successes / max(self.total_requests, 1)) * 100
            avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
            
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_requests": self.total_requests,
                "total_failures": self.total_failures,
                "total_successes": self.total_successes,
                "total_timeouts": self.total_timeouts,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 3),
                "last_state_change": self.last_state_change.isoformat(),
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
            }

class RetryPolicy:
    """Implementação de política de retry"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com política de retry"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except tuple(self.config.retry_on_exceptions) as e:
                last_exception = e
                
                if attempt == self.config.max_attempts:
                    logger.error(f"Retry falhou após {attempt} tentativas: {e}")
                    raise
                
                delay = self._calculate_delay(attempt)
                logger.warning(f"Tentativa {attempt} falhou, tentando novamente em {delay}string_data: {e}")
                time.sleep(delay)
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função assíncrona com política de retry"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except tuple(self.config.retry_on_exceptions) as e:
                last_exception = e
                
                if attempt == self.config.max_attempts:
                    logger.error(f"Retry assíncrono falhou após {attempt} tentativas: {e}")
                    raise
                
                delay = self._calculate_delay(attempt)
                logger.warning(f"Tentativa assíncrona {attempt} falhou, tentando novamente em {delay}string_data: {e}")
                await asyncio.sleep(delay)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calcula delay para próxima tentativa"""
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        
        if self.config.jitter:
            delay *= (0.5 + random.random() * 0.5)  # Jitter de 50%
        
        return min(delay, self.config.max_delay)

class TimeoutPolicy:
    """Implementação de política de timeout"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
    
    def execute(self, func: Callable, timeout: Optional[float] = None, *args, **kwargs) -> Any:
        """Executa função com timeout"""
        timeout = timeout or self.config.default_timeout
        
        try:
            return asyncio.run(asyncio.wait_for(
                self._async_wrapper(func, *args, **kwargs),
                timeout=timeout
            ))
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operação excedeu timeout de {timeout}string_data")
    
    async def execute_async(self, func: Callable, timeout: Optional[float] = None, *args, **kwargs) -> Any:
        """Executa função assíncrona com timeout"""
        timeout = timeout or self.config.default_timeout
        
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operação assíncrona excedeu timeout de {timeout}string_data")
    
    async def _async_wrapper(self, func: Callable, *args, **kwargs):
        """Wrapper para executar função síncrona de forma assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

class Bulkhead:
    """Implementação do bulkhead pattern"""
    
    def __init__(self, name: str, config: BulkheadConfig):
        self.name = name
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent_calls)
        self.queue = asyncio.Queue(maxsize=config.max_queue_size)
        self.active_calls = 0
        self._lock = threading.Lock()
        
        logger.info(f"Bulkhead '{name}' inicializado com {config.max_concurrent_calls} chamadas concorrentes")
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com bulkhead"""
        try:
            async with self.semaphore:
                with self._lock:
                    self.active_calls += 1
                
                try:
                    return await func(*args, **kwargs)
                finally:
                    with self._lock:
                        self.active_calls -= 1
        except asyncio.QueueFull:
            raise BulkheadFullError(f"Bulkhead '{self.name}' está cheio")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do bulkhead"""
        with self._lock:
            return {
                "name": self.name,
                "active_calls": self.active_calls,
                "max_concurrent_calls": self.config.max_concurrent_calls,
                "queue_size": self.queue.qsize(),
                "max_queue_size": self.config.max_queue_size,
                "available_slots": self.config.max_concurrent_calls - self.active_calls
            }

class FallbackStrategy:
    """Implementação de estratégias de fallback"""
    
    @staticmethod
    def return_default(default_value: Any):
        """Retorna valor padrão em caso de falha"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Fallback para valor padrão: {e}")
                    return default_value
            return wrapper
        return decorator
    
    @staticmethod
    def call_alternative(alternative_func: Callable):
        """Chama função alternativa em caso de falha"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Fallback para função alternativa: {e}")
                    return alternative_func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def cache_result(cache_duration: int = 300):
        """Cache do resultado por um período"""
        def decorator(func: Callable) -> Callable:
            cache = {}
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = str(args) + str(sorted(kwargs.items()))
                now = time.time()
                
                if cache_key in cache:
                    result, timestamp = cache[cache_key]
                    if now - timestamp < cache_duration:
                        logger.info("Retornando resultado do cache")
                        return result
                
                try:
                    result = func(*args, **kwargs)
                    cache[cache_key] = (result, now)
                    return result
                except Exception as e:
                    # Tentar usar cache mesmo que expirado
                    if cache_key in cache:
                        result, _ = cache[cache_key]
                        logger.warning(f"Usando cache expirado devido a erro: {e}")
                        return result
                    raise
            return wrapper
        return decorator

class ResilienceManager:
    """Gerenciador de resiliência"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.timeout_policies: Dict[str, TimeoutPolicy] = {}
        self.bulkheads: Dict[str, Bulkhead] = {}
        self.fallback_strategies: Dict[str, Callable] = {}
    
    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Adiciona circuit breaker"""
        circuit_breaker = CircuitBreaker(name, config)
        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker
    
    def add_retry_policy(self, name: str, config: RetryConfig) -> RetryPolicy:
        """Adiciona política de retry"""
        retry_policy = RetryPolicy(config)
        self.retry_policies[name] = retry_policy
        return retry_policy
    
    def add_timeout_policy(self, name: str, config: TimeoutConfig) -> TimeoutPolicy:
        """Adiciona política de timeout"""
        timeout_policy = TimeoutPolicy(config)
        self.timeout_policies[name] = timeout_policy
        return timeout_policy
    
    def add_bulkhead(self, name: str, config: BulkheadConfig) -> Bulkhead:
        """Adiciona bulkhead"""
        bulkhead = Bulkhead(name, config)
        self.bulkheads[name] = bulkhead
        return bulkhead
    
    def add_fallback_strategy(self, name: str, strategy: Callable):
        """Adiciona estratégia de fallback"""
        self.fallback_strategies[name] = strategy
    
    def execute_resilient(self, 
                         func: Callable,
                         circuit_breaker_name: Optional[str] = None,
                         retry_policy_name: Optional[str] = None,
                         timeout_policy_name: Optional[str] = None,
                         bulkhead_name: Optional[str] = None,
                         fallback_strategy_name: Optional[str] = None,
                         *args, **kwargs) -> Any:
        """Executa função com todas as políticas de resiliência"""
        
        # Aplicar fallback se especificado
        if fallback_strategy_name and fallback_strategy_name in self.fallback_strategies:
            func = self.fallback_strategies[fallback_strategy_name](func)
        
        # Aplicar timeout se especificado
        if timeout_policy_name and timeout_policy_name in self.timeout_policies:
            timeout_policy = self.timeout_policies[timeout_policy_name]
            func = lambda *a, **kw: timeout_policy.execute(func, *a, **kw)
        
        # Aplicar retry se especificado
        if retry_policy_name and retry_policy_name in self.retry_policies:
            retry_policy = self.retry_policies[retry_policy_name]
            func = lambda *a, **kw: retry_policy.execute(func, *a, **kw)
        
        # Aplicar circuit breaker se especificado
        if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[circuit_breaker_name]
            return circuit_breaker.call(func, *args, **kwargs)
        
        # Executar função sem circuit breaker
        return func(*args, **kwargs)
    
    async def execute_resilient_async(self,
                                    func: Callable,
                                    circuit_breaker_name: Optional[str] = None,
                                    retry_policy_name: Optional[str] = None,
                                    timeout_policy_name: Optional[str] = None,
                                    bulkhead_name: Optional[str] = None,
                                    fallback_strategy_name: Optional[str] = None,
                                    *args, **kwargs) -> Any:
        """Executa função assíncrona com todas as políticas de resiliência"""
        
        # Aplicar fallback se especificado
        if fallback_strategy_name and fallback_strategy_name in self.fallback_strategies:
            func = self.fallback_strategies[fallback_strategy_name](func)
        
        # Aplicar timeout se especificado
        if timeout_policy_name and timeout_policy_name in self.timeout_policies:
            timeout_policy = self.timeout_policies[timeout_policy_name]
            func = lambda *a, **kw: timeout_policy.execute_async(func, *a, **kw)
        
        # Aplicar retry se especificado
        if retry_policy_name and retry_policy_name in self.retry_policies:
            retry_policy = self.retry_policies[retry_policy_name]
            func = lambda *a, **kw: retry_policy.execute_async(func, *a, **kw)
        
        # Aplicar bulkhead se especificado
        if bulkhead_name and bulkhead_name in self.bulkheads:
            bulkhead = self.bulkheads[bulkhead_name]
            func = lambda *a, **kw: bulkhead.execute(func, *a, **kw)
        
        # Aplicar circuit breaker se especificado
        if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[circuit_breaker_name]
            return await circuit_breaker.call_async(func, *args, **kwargs)
        
        # Executar função sem circuit breaker
        return await func(*args, **kwargs)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de todos os componentes"""
        return {
            "circuit_breakers": {
                name: cb.get_metrics() 
                for name, cb in self.circuit_breakers.items()
            },
            "bulkheads": {
                name: bh.get_metrics() 
                for name, bh in self.bulkheads.items()
            },
            "timestamp": datetime.now().isoformat()
        }

# Exceções customizadas
class CircuitBreakerOpenError(Exception):
    """Exceção lançada quando circuit breaker está aberto"""
    pass

class BulkheadFullError(Exception):
    """Exceção lançada quando bulkhead está cheio"""
    pass

# Instância global do gerenciador de resiliência
resilience_manager = ResilienceManager()

# Decoradores para facilitar uso
def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator para circuit breaker"""
    if config is None:
        config = CircuitBreakerConfig()
    
    def decorator(func: Callable) -> Callable:
        cb = resilience_manager.add_circuit_breaker(name, config)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await cb.call_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator

def retry_policy(name: str, config: Optional[RetryConfig] = None):
    """Decorator para retry policy"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        retry = resilience_manager.add_retry_policy(name, config)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry.execute(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await retry.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator

def timeout_policy(name: str, config: Optional[TimeoutConfig] = None):
    """Decorator para timeout policy"""
    if config is None:
        config = TimeoutConfig()
    
    def decorator(func: Callable) -> Callable:
        timeout = resilience_manager.add_timeout_policy(name, config)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return timeout.execute(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await timeout.execute_async(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator

def bulkhead(name: str, config: Optional[BulkheadConfig] = None):
    """Decorator para bulkhead (apenas para funções assíncronas)"""
    if config is None:
        config = BulkheadConfig()
    
    def decorator(func: Callable) -> Callable:
        bh = resilience_manager.add_bulkhead(name, config)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await bh.execute(func, *args, **kwargs)
        
        return wrapper
    
    return decorator 