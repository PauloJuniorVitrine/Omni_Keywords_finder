#!/usr/bin/env python3
"""
Sistema Completo de Resiliência - Fase 4
Responsável por retry policies básicas e fallback simples.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 4
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import time
import random
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, TypeVar, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryStrategy(Enum):
    """Estratégias de retry."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"
    RANDOM = "random"

class FallbackStrategy(Enum):
    """Estratégias de fallback."""
    DEFAULT_VALUE = "default_value"
    ALTERNATIVE_FUNCTION = "alternative_function"
    CACHE = "cache"
    CIRCUIT_BREAKER = "circuit_breaker"

@dataclass
class RetryConfig:
    """Configuração de retry."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[type] = field(default_factory=lambda: [Exception])
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL

@dataclass
class FallbackConfig:
    """Configuração de fallback."""
    strategy: FallbackStrategy
    default_value: Any = None
    alternative_function: Optional[Callable] = None
    cache_duration: int = 300  # 5 minutos
    circuit_breaker_threshold: int = 5

class RetryPolicy:
    """Implementação de política de retry."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.attempt_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com política de retry."""
        func_name = func.__name__
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Registrar sucesso
                self._record_attempt(func_name, attempt, True, time.time() - start_time)
                
                return result
                
            except tuple(self.config.retry_on_exceptions) as e:
                last_exception = e
                execution_time = time.time() - start_time
                
                # Registrar falha
                self._record_attempt(func_name, attempt, False, execution_time, str(e))
                
                if attempt == self.config.max_attempts:
                    logger.error(f"Retry falhou após {attempt} tentativas para {func_name}: {e}")
                    raise
                
                delay = self._calculate_delay(attempt)
                logger.warning(f"Tentativa {attempt} falhou para {func_name}, tentando novamente em {delay:.1f}string_data: {e}")
                time.sleep(delay)
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função assíncrona com política de retry."""
        func_name = func.__name__
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Registrar sucesso
                self._record_attempt(func_name, attempt, True, time.time() - start_time)
                
                return result
                
            except tuple(self.config.retry_on_exceptions) as e:
                last_exception = e
                execution_time = time.time() - start_time
                
                # Registrar falha
                self._record_attempt(func_name, attempt, False, execution_time, str(e))
                
                if attempt == self.config.max_attempts:
                    logger.error(f"Retry assíncrono falhou após {attempt} tentativas para {func_name}: {e}")
                    raise
                
                delay = self._calculate_delay(attempt)
                logger.warning(f"Tentativa assíncrona {attempt} falhou para {func_name}, tentando novamente em {delay:.1f}string_data: {e}")
                await asyncio.sleep(delay)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calcula delay para próxima tentativa."""
        if self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            delay = self.config.base_delay * self._fibonacci(attempt)
        elif self.config.strategy == RetryStrategy.RANDOM:
            delay = self.config.base_delay * random.uniform(0.5, 2.0) * attempt
        else:
            delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        
        if self.config.jitter:
            delay *= (0.5 + random.random() * 0.5)  # Jitter de 50%
        
        return min(delay, self.config.max_delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calcula número de Fibonacci."""
        if n <= 1:
            return n
        return self._fibonacci(n - 1) + self._fibonacci(n - 2)
    
    def _record_attempt(self, func_name: str, attempt: int, success: bool, execution_time: float, error: str = None):
        """Registra tentativa de retry."""
        record = {
            'attempt': attempt,
            'success': success,
            'execution_time': execution_time,
            'timestamp': datetime.utcnow(),
            'error': error
        }
        
        self.attempt_history[func_name].append(record)
        
        # Manter apenas os últimos 100 registros
        if len(self.attempt_history[func_name]) > 100:
            self.attempt_history[func_name] = self.attempt_history[func_name][-100:]

class FallbackStrategy:
    """Implementação de estratégias de fallback."""
    
    def __init__(self, config: FallbackConfig):
        self.config = config
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.failure_count: Dict[str, int] = defaultdict(int)
        self.circuit_breaker_state: Dict[str, str] = defaultdict(lambda: "closed")
        self.circuit_breaker_last_failure: Dict[str, datetime] = {}
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com fallback."""
        func_name = func.__name__
        
        # Verificar circuit breaker
        if self._is_circuit_breaker_open(func_name):
            return self._execute_fallback(func_name, *args, **kwargs)
        
        try:
            result = func(*args, **kwargs)
            
            # Reset circuit breaker em caso de sucesso
            self._reset_circuit_breaker(func_name)
            
            # Cache o resultado se configurado
            if self.config.strategy == FallbackStrategy.CACHE:
                self._cache_result(func_name, result)
            
            return result
            
        except Exception as e:
            # Incrementar contador de falhas
            self.failure_count[func_name] += 1
            self.circuit_breaker_last_failure[func_name] = datetime.utcnow()
            
            # Abrir circuit breaker se necessário
            if self.failure_count[func_name] >= self.config.circuit_breaker_threshold:
                self.circuit_breaker_state[func_name] = "open"
                logger.warning(f"Circuit breaker aberto para {func_name} após {self.failure_count[func_name]} falhas")
            
            logger.warning(f"Falha em {func_name}, executando fallback: {e}")
            return self._execute_fallback(func_name, *args, **kwargs)
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função assíncrona com fallback."""
        func_name = func.__name__
        
        # Verificar circuit breaker
        if self._is_circuit_breaker_open(func_name):
            return await self._execute_fallback_async(func_name, *args, **kwargs)
        
        try:
            result = await func(*args, **kwargs)
            
            # Reset circuit breaker em caso de sucesso
            self._reset_circuit_breaker(func_name)
            
            # Cache o resultado se configurado
            if self.config.strategy == FallbackStrategy.CACHE:
                self._cache_result(func_name, result)
            
            return result
            
        except Exception as e:
            # Incrementar contador de falhas
            self.failure_count[func_name] += 1
            self.circuit_breaker_last_failure[func_name] = datetime.utcnow()
            
            # Abrir circuit breaker se necessário
            if self.failure_count[func_name] >= self.config.circuit_breaker_threshold:
                self.circuit_breaker_state[func_name] = "open"
                logger.warning(f"Circuit breaker aberto para {func_name} após {self.failure_count[func_name]} falhas")
            
            logger.warning(f"Falha em {func_name}, executando fallback: {e}")
            return await self._execute_fallback_async(func_name, *args, **kwargs)
    
    def _is_circuit_breaker_open(self, func_name: str) -> bool:
        """Verifica se circuit breaker está aberto."""
        if self.circuit_breaker_state[func_name] != "open":
            return False
        
        # Tentar fechar circuit breaker após timeout
        last_failure = self.circuit_breaker_last_failure.get(func_name)
        if last_failure and datetime.utcnow() - last_failure > timedelta(minutes=5):
            self.circuit_breaker_state[func_name] = "half_open"
            logger.info(f"Circuit breaker em half-open para {func_name}")
        
        return self.circuit_breaker_state[func_name] == "open"
    
    def _reset_circuit_breaker(self, func_name: str):
        """Reset circuit breaker."""
        self.circuit_breaker_state[func_name] = "closed"
        self.failure_count[func_name] = 0
    
    def _execute_fallback(self, func_name: str, *args, **kwargs) -> Any:
        """Executa estratégia de fallback."""
        if self.config.strategy == FallbackStrategy.DEFAULT_VALUE:
            return self.config.default_value
        
        elif self.config.strategy == FallbackStrategy.ALTERNATIVE_FUNCTION:
            if self.config.alternative_function:
                return self.config.alternative_function(*args, **kwargs)
            else:
                return self.config.default_value
        
        elif self.config.strategy == FallbackStrategy.CACHE:
            cached_result = self._get_cached_result(func_name)
            if cached_result is not None:
                return cached_result
            else:
                return self.config.default_value
        
        else:
            return self.config.default_value
    
    async def _execute_fallback_async(self, func_name: str, *args, **kwargs) -> Any:
        """Executa estratégia de fallback assíncrona."""
        if self.config.strategy == FallbackStrategy.DEFAULT_VALUE:
            return self.config.default_value
        
        elif self.config.strategy == FallbackStrategy.ALTERNATIVE_FUNCTION:
            if self.config.alternative_function:
                if asyncio.iscoroutinefunction(self.config.alternative_function):
                    return await self.config.alternative_function(*args, **kwargs)
                else:
                    return self.config.alternative_function(*args, **kwargs)
            else:
                return self.config.default_value
        
        elif self.config.strategy == FallbackStrategy.CACHE:
            cached_result = self._get_cached_result(func_name)
            if cached_result is not None:
                return cached_result
            else:
                return self.config.default_value
        
        else:
            return self.config.default_value
    
    def _cache_result(self, func_name: str, result: Any):
        """Cache resultado."""
        self.cache[func_name] = result
        self.cache_timestamps[func_name] = datetime.utcnow()
    
    def _get_cached_result(self, func_name: str) -> Optional[Any]:
        """Obtém resultado do cache."""
        if func_name not in self.cache:
            return None
        
        timestamp = self.cache_timestamps.get(func_name)
        if timestamp and datetime.utcnow() - timestamp > timedelta(seconds=self.config.cache_duration):
            # Cache expirado
            del self.cache[func_name]
            del self.cache_timestamps[func_name]
            return None
        
        return self.cache[func_name]

class ResilienceManager:
    """Gerenciador de resiliência."""
    
    def __init__(self):
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.fallback_strategies: Dict[str, FallbackStrategy] = {}
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def add_retry_policy(self, name: str, config: RetryConfig) -> RetryPolicy:
        """Adiciona política de retry."""
        retry_policy = RetryPolicy(config)
        self.retry_policies[name] = retry_policy
        return retry_policy
    
    def add_fallback_strategy(self, name: str, config: FallbackConfig) -> FallbackStrategy:
        """Adiciona estratégia de fallback."""
        fallback_strategy = FallbackStrategy(config)
        self.fallback_strategies[name] = fallback_strategy
        return fallback_strategy
    
    def execute_resilient(self, 
                         func: Callable,
                         retry_policy_name: Optional[str] = None,
                         fallback_strategy_name: Optional[str] = None,
                         *args, **kwargs) -> Any:
        """Executa função com resiliência."""
        start_time = time.time()
        func_name = func.__name__
        
        try:
            # Aplicar retry se especificado
            if retry_policy_name and retry_policy_name in self.retry_policies:
                retry_policy = self.retry_policies[retry_policy_name]
                result = retry_policy.execute(func, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Registrar sucesso
            self._record_metric(func_name, "success", time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Registrar falha
            self._record_metric(func_name, "failure", time.time() - start_time, str(e))
            
            # Aplicar fallback se especificado
            if fallback_strategy_name and fallback_strategy_name in self.fallback_strategies:
                fallback_strategy = self.fallback_strategies[fallback_strategy_name]
                return fallback_strategy.execute(func, *args, **kwargs)
            else:
                raise
    
    async def execute_resilient_async(self,
                                    func: Callable,
                                    retry_policy_name: Optional[str] = None,
                                    fallback_strategy_name: Optional[str] = None,
                                    *args, **kwargs) -> Any:
        """Executa função assíncrona com resiliência."""
        start_time = time.time()
        func_name = func.__name__
        
        try:
            # Aplicar retry se especificado
            if retry_policy_name and retry_policy_name in self.retry_policies:
                retry_policy = self.retry_policies[retry_policy_name]
                result = await retry_policy.execute_async(func, *args, **kwargs)
            else:
                result = await func(*args, **kwargs)
            
            # Registrar sucesso
            self._record_metric(func_name, "success", time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Registrar falha
            self._record_metric(func_name, "failure", time.time() - start_time, str(e))
            
            # Aplicar fallback se especificado
            if fallback_strategy_name and fallback_strategy_name in self.fallback_strategies:
                fallback_strategy = self.fallback_strategies[fallback_strategy_name]
                return await fallback_strategy.execute_async(func, *args, **kwargs)
            else:
                raise
    
    def _record_metric(self, func_name: str, status: str, execution_time: float, error: str = None):
        """Registra métrica de execução."""
        if func_name not in self.metrics:
            self.metrics[func_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_execution_time': 0.0,
                'avg_execution_time': 0.0,
                'last_error': None
            }
        
        metric = self.metrics[func_name]
        metric['total_calls'] += 1
        metric['total_execution_time'] += execution_time
        metric['avg_execution_time'] = metric['total_execution_time'] / metric['total_calls']
        
        if status == "success":
            metric['successful_calls'] += 1
        else:
            metric['failed_calls'] += 1
            metric['last_error'] = error
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Obtém métricas de resiliência."""
        return dict(self.metrics)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Obtém resumo de saúde."""
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_functions': len(self.metrics),
            'healthy_functions': 0,
            'degraded_functions': 0,
            'unhealthy_functions': 0,
            'functions': {}
        }
        
        for func_name, metric in self.metrics.items():
            success_rate = metric['successful_calls'] / metric['total_calls'] if metric['total_calls'] > 0 else 0
            
            if success_rate >= 0.95:
                status = "healthy"
                summary['healthy_functions'] += 1
            elif success_rate >= 0.80:
                status = "degraded"
                summary['degraded_functions'] += 1
            else:
                status = "unhealthy"
                summary['unhealthy_functions'] += 1
            
            summary['functions'][func_name] = {
                'status': status,
                'success_rate': success_rate,
                'avg_execution_time': metric['avg_execution_time'],
                'total_calls': metric['total_calls'],
                'last_error': metric['last_error']
            }
        
        return summary

# Instância global
resilience_manager = ResilienceManager()

# Configurações padrão
def get_default_retry_config() -> RetryConfig:
    """Retorna configuração de retry padrão."""
    return RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=60.0,
        exponential_base=2.0,
        jitter=True,
        retry_on_exceptions=[Exception],
        strategy=RetryStrategy.EXPONENTIAL
    )

def get_default_fallback_config(default_value: Any = None) -> FallbackConfig:
    """Retorna configuração de fallback padrão."""
    return FallbackConfig(
        strategy=FallbackStrategy.DEFAULT_VALUE,
        default_value=default_value,
        cache_duration=300,
        circuit_breaker_threshold=5
    )

# Decorators de conveniência
def with_retry(config: RetryConfig = None):
    """Decorator para aplicar retry."""
    if config is None:
        config = get_default_retry_config()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_policy = RetryPolicy(config)
            return retry_policy.execute(func, *args, **kwargs)
        return wrapper
    return decorator

def with_fallback(config: FallbackConfig):
    """Decorator para aplicar fallback."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            fallback_strategy = FallbackStrategy(config)
            return fallback_strategy.execute(func, *args, **kwargs)
        return wrapper
    return decorator

def with_resilience(retry_config: RetryConfig = None, fallback_config: FallbackConfig = None):
    """Decorator para aplicar resiliência completa."""
    if retry_config is None:
        retry_config = get_default_retry_config()
    if fallback_config is None:
        fallback_config = get_default_fallback_config()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return resilience_manager.execute_resilient(
                func,
                retry_policy_name="default",
                fallback_strategy_name="default",
                *args, **kwargs
            )
        return wrapper
    return decorator

# Funções de conveniência
def get_resilience_manager() -> ResilienceManager:
    """Obtém gerenciador de resiliência."""
    return resilience_manager

def add_default_policies():
    """Adiciona políticas padrão."""
    resilience_manager.add_retry_policy("default", get_default_retry_config())
    resilience_manager.add_fallback_strategy("default", get_default_fallback_config())

if __name__ == "__main__":
    # Exemplo de uso
    add_default_policies()
    
    # Função que pode falhar
    def unreliable_function():
        if random.random() < 0.7:  # 70% chance de falhar
            raise Exception("Erro aleatório")
        return "sucesso"
    
    # Executar com resiliência
    try:
        result = resilience_manager.execute_resilient(
            unreliable_function,
            retry_policy_name="default",
            fallback_strategy_name="default"
        )
        print(f"Resultado: {result}")
    except Exception as e:
        print(f"Falha final: {e}")
    
    # Métricas
    metrics = resilience_manager.get_metrics()
    print(f"Métricas: {metrics}")
    
    # Health summary
    health = resilience_manager.get_health_summary()
    print(f"Health: {health}") 