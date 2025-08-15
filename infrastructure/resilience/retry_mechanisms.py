"""
🔄 Mecanismos de Retry Avançados - Sistema de Resiliência

Tracing ID: retry-mechanisms-2025-01-27-001
Timestamp: 2025-01-27T19:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Mecanismos baseados em padrões reais de retry e recuperação
🌲 ToT: Avaliadas múltiplas estratégias de retry (exponencial, linear, customizado)
♻️ ReAct: Simulado cenários de falha e validada estratégia de retry

Implementa mecanismos de retry incluindo:
- Retry com backoff exponencial
- Retry com jitter para evitar thundering herd
- Retry com timeout configurável
- Retry com circuit breaker
- Retry com fallback
- Retry com métricas detalhadas
- Retry com logging estruturado
"""

import asyncio
import time
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, Type, Tuple
from enum import Enum
import logging
from dataclasses import dataclass, field
import functools
import inspect
from contextlib import asynccontextmanager
import json

# Importar circuit breaker
from .advanced_circuit_breaker import AdvancedCircuitBreaker, CircuitBreakerConfig

# Configuração de logging
logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """Estratégias de retry disponíveis"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"
    FIBONACCI = "fibonacci"
    CUSTOM = "custom"

class RetryCondition(Enum):
    """Condições para retry"""
    ALWAYS = "always"
    ON_EXCEPTION = "on_exception"
    ON_RESULT = "on_result"
    ON_TIMEOUT = "on_timeout"
    CUSTOM = "custom"

@dataclass
class RetryConfig:
    """Configuração de retry"""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0  # segundos
    max_delay: float = 60.0  # segundos
    multiplier: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    timeout: float = 30.0  # segundos
    timeout_per_attempt: bool = True
    retry_on_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    retry_on_result: Optional[Callable[[Any], bool]] = None
    retry_on_timeout: bool = True
    enable_circuit_breaker: bool = True
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None
    enable_fallback: bool = True
    fallback_func: Optional[Callable] = None
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_monitoring: bool = True
    custom_delays: List[float] = field(default_factory=list)
    custom_conditions: List[Callable] = field(default_factory=list)

@dataclass
class RetryMetrics:
    """Métricas de retry"""
    total_retries: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    timeout_retries: int = 0
    exception_retries: int = 0
    result_retries: int = 0
    circuit_breaker_retries: int = 0
    fallback_used: int = 0
    total_attempts: int = 0
    total_delay_time: float = 0.0
    retry_delays: List[float] = field(default_factory=list)
    last_retry_time: Optional[datetime] = None
    retry_reasons: Dict[str, int] = field(default_factory=dict)
    
    def add_retry(self, reason: str, delay: float, success: bool):
        """Adiciona métrica de retry"""
        self.total_retries += 1
        self.total_attempts += 1
        self.total_delay_time += delay
        self.retry_delays.append(delay)
        self.last_retry_time = datetime.now()
        
        if success:
            self.successful_retries += 1
        else:
            self.failed_retries += 1
            
        self.retry_reasons[reason] = self.retry_reasons.get(reason, 0) + 1
        
        # Manter apenas os últimos 100 delays
        if len(self.retry_delays) > 100:
            self.retry_delays.pop(0)
            
    def add_timeout_retry(self):
        """Adiciona retry por timeout"""
        self.timeout_retries += 1
        
    def add_exception_retry(self):
        """Adiciona retry por exceção"""
        self.exception_retries += 1
        
    def add_result_retry(self):
        """Adiciona retry por resultado"""
        self.result_retries += 1
        
    def add_circuit_breaker_retry(self):
        """Adiciona retry por circuit breaker"""
        self.circuit_breaker_retries += 1
        
    def add_fallback_usage(self):
        """Adiciona uso de fallback"""
        self.fallback_used += 1
        
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        return {
            'total_retries': self.total_retries,
            'successful_retries': self.successful_retries,
            'failed_retries': self.failed_retries,
            'success_rate': self.successful_retries / self.total_retries if self.total_retries > 0 else 0,
            'timeout_retries': self.timeout_retries,
            'exception_retries': self.exception_retries,
            'result_retries': self.result_retries,
            'circuit_breaker_retries': self.circuit_breaker_retries,
            'fallback_used': self.fallback_used,
            'total_attempts': self.total_attempts,
            'average_delay': self.total_delay_time / self.total_retries if self.total_retries > 0 else 0,
            'total_delay_time': self.total_delay_time,
            'retry_reasons': self.retry_reasons,
            'last_retry_time': self.last_retry_time.isoformat() if self.last_retry_time else None,
            'delay_stats': {
                'min': min(self.retry_delays) if self.retry_delays else 0,
                'max': max(self.retry_delays) if self.retry_delays else 0,
                'mean': statistics.mean(self.retry_delays) if self.retry_delays else 0,
                'median': statistics.median(self.retry_delays) if self.retry_delays else 0
            }
        }

class RetryMechanism:
    """Mecanismo de retry avançado"""
    
    def __init__(self, name: str, config: Optional[RetryConfig] = None):
        self.name = name
        self.config = config or RetryConfig()
        self.metrics = RetryMetrics()
        self.circuit_breaker = None
        
        if self.config.enable_circuit_breaker:
            cb_config = self.config.circuit_breaker_config or CircuitBreakerConfig()
            self.circuit_breaker = AdvancedCircuitBreaker(f"{name}_retry", cb_config)
            
        logger.info(f"Retry Mechanism '{name}' inicializado com configuração: {self.config}")
        
    def calculate_delay(self, attempt: int) -> float:
        """Calcula delay para tentativa específica"""
        if self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (self.config.multiplier ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.CONSTANT:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            delay = self.config.base_delay * self._fibonacci(attempt)
        elif self.config.strategy == RetryStrategy.CUSTOM:
            if attempt <= len(self.config.custom_delays):
                delay = self.config.custom_delays[attempt - 1]
            else:
                delay = self.config.max_delay
        else:
            delay = self.config.base_delay
            
        # Aplicar limite máximo
        delay = min(delay, self.config.max_delay)
        
        # Aplicar jitter
        if self.config.jitter:
            jitter = delay * self.config.jitter_factor * random.uniform(-1, 1)
            delay = max(0, delay + jitter)
            
        return delay
        
    def _fibonacci(self, n: int) -> int:
        """Calcula número de Fibonacci"""
        if n <= 1:
            return n
        return self._fibonacci(n - 1) + self._fibonacci(n - 2)
        
    def should_retry(self, attempt: int, exception: Optional[Exception] = None, 
                    result: Optional[Any] = None, timeout: bool = False) -> bool:
        """Determina se deve fazer retry"""
        if attempt >= self.config.max_attempts:
            return False
            
        # Verificar circuit breaker
        if self.circuit_breaker and self.circuit_breaker.is_open():
            return False
            
        # Verificar timeout
        if timeout and self.config.retry_on_timeout:
            return True
            
        # Verificar exceção
        if exception and any(isinstance(exception, exc_type) for exc_type in self.config.retry_on_exceptions):
            return True
            
        # Verificar resultado
        if result is not None and self.config.retry_on_result:
            if self.config.retry_on_result(result):
                return True
                
        # Verificar condições customizadas
        for condition in self.config.custom_conditions:
            if condition(attempt, exception, result, timeout):
                return True
                
        return False
        
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com retry"""
        last_exception = None
        last_result = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                # Verificar circuit breaker antes da tentativa
                if self.circuit_breaker and self.circuit_breaker.is_open():
                    logger.warning(f"Circuit breaker aberto para '{self.name}', tentativa {attempt} cancelada")
                    self.metrics.add_circuit_breaker_retry()
                    break
                    
                # Executar função com timeout se configurado
                if self.config.timeout_per_attempt:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs),
                        timeout=self.config.timeout
                    )
                else:
                    result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                    
                # Verificar se resultado requer retry
                if self.should_retry(attempt, result=result):
                    last_result = result
                    self.metrics.add_result_retry()
                    if self.config.enable_logging:
                        logger.info(f"Retry {attempt} para '{self.name}' devido ao resultado")
                else:
                    # Sucesso
                    if attempt > 1:
                        self.metrics.add_retry("success", 0, True)
                    return result
                    
            except asyncio.TimeoutError as e:
                last_exception = e
                self.metrics.add_timeout_retry()
                if self.config.enable_logging:
                    logger.warning(f"Timeout na tentativa {attempt} para '{self.name}': {e}")
                    
            except Exception as e:
                last_exception = e
                self.metrics.add_exception_retry()
                if self.config.enable_logging:
                    logger.warning(f"Exceção na tentativa {attempt} para '{self.name}': {e}")
                    
            # Verificar se deve fazer retry
            if attempt < self.config.max_attempts and self.should_retry(attempt, last_exception, last_result):
                delay = self.calculate_delay(attempt)
                
                if self.config.enable_logging:
                    logger.info(f"Aguardando {delay:.2f}s antes da tentativa {attempt + 1} para '{self.name}'")
                    
                await asyncio.sleep(delay)
                self.metrics.add_retry("retry", delay, False)
                
            else:
                break
                
        # Todas as tentativas falharam
        if self.config.enable_fallback and self.config.fallback_func:
            logger.info(f"Usando fallback para '{self.name}' após {attempt} tentativas")
            self.metrics.add_fallback_usage()
            return await self.config.fallback_func(*args, **kwargs)
            
        # Re-raise última exceção ou retornar último resultado
        if last_exception:
            raise last_exception
        else:
            return last_result
            
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de retry"""
        return self.metrics.get_summary() if self.config.enable_metrics else {}
        
    def reset_metrics(self):
        """Reseta métricas"""
        self.metrics = RetryMetrics()

class RetryManager:
    """Gerenciador de mecanismos de retry"""
    
    def __init__(self):
        self.retry_mechanisms: Dict[str, RetryMechanism] = {}
        self._lock = asyncio.Lock()
        
    async def get_retry_mechanism(self, name: str, config: Optional[RetryConfig] = None) -> RetryMechanism:
        """Obtém ou cria mecanismo de retry"""
        async with self._lock:
            if name not in self.retry_mechanisms:
                self.retry_mechanisms[name] = RetryMechanism(name, config)
            return self.retry_mechanisms[name]
            
    async def execute_with_retry(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Executa função com retry específico"""
        retry_mechanism = await self.get_retry_mechanism(name)
        return await retry_mechanism.execute(func, *args, **kwargs)
        
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Retorna métricas de todos os mecanismos de retry"""
        return {name: rm.get_metrics() for name, rm in self.retry_mechanisms.items()}
        
    def reset_all_metrics(self):
        """Reseta métricas de todos os mecanismos de retry"""
        for rm in self.retry_mechanisms.values():
            rm.reset_metrics()

# Instância global do gerenciador
retry_manager = RetryManager()

# Decorator para usar retry
def retry(name: str, config: Optional[RetryConfig] = None):
    """Decorator para aplicar retry a função"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retry_mechanism = await retry_manager.get_retry_mechanism(name, config)
            return await retry_mechanism.execute(func, *args, **kwargs)
        return wrapper
    return decorator

# Context manager para retry
@asynccontextmanager
async def retry_context(name: str, config: Optional[RetryConfig] = None):
    """Context manager para retry"""
    retry_mechanism = await retry_manager.get_retry_mechanism(name, config)
    try:
        yield retry_mechanism
    finally:
        pass

# Funções utilitárias
async def execute_with_retry(name: str, func: Callable, *args, **kwargs) -> Any:
    """Executa função com retry"""
    return await retry_manager.execute_with_retry(name, func, *args, **kwargs)

def get_retry_metrics(name: str) -> Optional[Dict[str, Any]]:
    """Obtém métricas de retry específico"""
    if name in retry_manager.retry_mechanisms:
        return retry_manager.retry_mechanisms[name].get_metrics()
    return None

def get_all_retry_metrics() -> Dict[str, Dict[str, Any]]:
    """Obtém métricas de todos os retries"""
    return retry_manager.get_all_metrics()

def reset_retry_metrics(name: str):
    """Reseta métricas de retry específico"""
    if name in retry_manager.retry_mechanisms:
        retry_manager.retry_mechanisms[name].reset_metrics()

def reset_all_retry_metrics():
    """Reseta métricas de todos os retries"""
    retry_manager.reset_all_metrics()

# Configurações predefinidas
def create_exponential_retry_config(max_attempts: int = 3, base_delay: float = 1.0) -> RetryConfig:
    """Cria configuração de retry exponencial"""
    return RetryConfig(
        max_attempts=max_attempts,
        strategy=RetryStrategy.EXPONENTIAL,
        base_delay=base_delay,
        multiplier=2.0,
        jitter=True
    )

def create_linear_retry_config(max_attempts: int = 3, base_delay: float = 1.0) -> RetryConfig:
    """Cria configuração de retry linear"""
    return RetryConfig(
        max_attempts=max_attempts,
        strategy=RetryStrategy.LINEAR,
        base_delay=base_delay,
        jitter=True
    )

def create_constant_retry_config(max_attempts: int = 3, delay: float = 1.0) -> RetryConfig:
    """Cria configuração de retry constante"""
    return RetryConfig(
        max_attempts=max_attempts,
        strategy=RetryStrategy.CONSTANT,
        base_delay=delay,
        jitter=True
    )

def create_fibonacci_retry_config(max_attempts: int = 3, base_delay: float = 1.0) -> RetryConfig:
    """Cria configuração de retry Fibonacci"""
    return RetryConfig(
        max_attempts=max_attempts,
        strategy=RetryStrategy.FIBONACCI,
        base_delay=base_delay,
        jitter=True
    )

def create_custom_retry_config(max_attempts: int, delays: List[float]) -> RetryConfig:
    """Cria configuração de retry customizada"""
    return RetryConfig(
        max_attempts=max_attempts,
        strategy=RetryStrategy.CUSTOM,
        custom_delays=delays,
        jitter=True
    )

# Exemplo de uso
if __name__ == "__main__":
    import asyncio
    
    async def test_retry():
        # Configuração de retry exponencial
        config = create_exponential_retry_config(max_attempts=5, base_delay=0.5)
        
        # Função que pode falhar
        async def unreliable_function():
            import random
            if random.random() < 0.7:  # 70% de chance de falha
                raise Exception("Erro simulado")
            return {"data": "sucesso"}
        
        # Testar retry
        try:
            result = await execute_with_retry("test_api", unreliable_function)
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Falha final: {e}")
            
        # Mostrar métricas
        metrics = get_retry_metrics("test_api")
        print(f"Métricas: {json.dumps(metrics, indent=2)}")
    
    asyncio.run(test_retry()) 