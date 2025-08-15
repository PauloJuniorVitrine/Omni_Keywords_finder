"""
Circuit Breaker Pattern Implementation
Omni Keywords Finder - Infrastructure Resilience

Tracing ID: CIRCUIT_BREAKER_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO
"""

import time
import logging
from typing import Callable, Any, Optional, Dict
from enum import Enum
from dataclasses import dataclass
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Estados do circuit breaker"""
    CLOSED = "CLOSED"      # Funcionando normalmente
    OPEN = "OPEN"          # Circuito aberto (falhas)
    HALF_OPEN = "HALF_OPEN"  # Testando recuperação


@dataclass
class CircuitBreakerConfig:
    """Configuração do circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: type = Exception
    name: str = "default"
    fallback_function: Optional[Callable] = None


class CircuitBreaker:
    """
    Implementação do padrão Circuit Breaker
    
    Previne cascata de falhas isolando serviços problemáticos
    e permitindo recuperação automática.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
        # Métricas Prometheus
        self.circuit_state_gauge = Gauge(
            f'circuit_breaker_state_{config.name}',
            f'Estado do circuit breaker {config.name}',
            ['state']
        )
        self.failure_counter = Counter(
            f'circuit_breaker_failures_{config.name}',
            f'Falhas no circuit breaker {config.name}'
        )
        self.success_counter = Counter(
            f'circuit_breaker_successes_{config.name}',
            f'Sucessos no circuit breaker {config.name}'
        )
        self.call_duration = Histogram(
            f'circuit_breaker_call_duration_{config.name}',
            f'Duração das chamadas no circuit breaker {config.name}'
        )
        
        # Inicializar métricas
        self._update_metrics()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função com proteção do circuit breaker
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função ou fallback
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.config.name} tentando reset")
            else:
                logger.warning(f"Circuit breaker {self.config.name} está OPEN, usando fallback")
                return self._execute_fallback(*args, **kwargs)
        
        try:
            with self.call_duration.time():
                result = func(*args, **kwargs)
                self._on_success()
                return result
                
        except self.config.expected_exception as e:
            self._on_failure(e)
            return self._execute_fallback(*args, **kwargs)
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar reset do circuit breaker"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time > self.config.recovery_timeout
    
    def _on_success(self):
        """Callback executado em caso de sucesso"""
        self.success_count += 1
        self.success_counter.inc()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            logger.info(f"Circuit breaker {self.config.name} resetado com sucesso")
        
        self._update_metrics()
    
    def _on_failure(self, exception: Exception):
        """Callback executado em caso de falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.failure_counter.inc()
        
        logger.warning(
            f"Falha no circuit breaker {self.config.name}: {exception} "
            f"(falhas: {self.failure_count}/{self.config.failure_threshold})"
        )
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker {self.config.name} aberto")
        
        self._update_metrics()
    
    def _execute_fallback(self, *args, **kwargs) -> Any:
        """Executa função de fallback"""
        if self.config.fallback_function:
            try:
                return self.config.fallback_function(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback também falhou: {e}")
                raise
        
        # Fallback padrão: retorna None
        logger.warning(f"Sem fallback configurado para {self.config.name}")
        return None
    
    def _update_metrics(self):
        """Atualiza métricas Prometheus"""
        # Reset todas as métricas de estado
        for state in CircuitState:
            self.circuit_state_gauge.labels(state=state.value).set(0)
        
        # Define estado atual
        self.circuit_state_gauge.labels(state=self.state.value).set(1)
    
    def get_state(self) -> CircuitState:
        """Retorna estado atual do circuit breaker"""
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do circuit breaker"""
        return {
            'name': self.config.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time,
            'failure_threshold': self.config.failure_threshold,
            'recovery_timeout': self.config.recovery_timeout
        }
    
    def reset(self):
        """Reseta manualmente o circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self._update_metrics()
        logger.info(f"Circuit breaker {self.config.name} resetado manualmente")


def circuit_breaker(config: CircuitBreakerConfig):
    """
    Decorator para aplicar circuit breaker a funções
    
    Args:
        config: Configuração do circuit breaker
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        cb = CircuitBreaker(config)
        
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        # Adiciona atributos úteis ao wrapper
        wrapper.circuit_breaker = cb
        wrapper.get_state = cb.get_state
        wrapper.get_stats = cb.get_stats
        wrapper.reset = cb.reset
        
        return wrapper
    
    return decorator 