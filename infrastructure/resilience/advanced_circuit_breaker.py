"""
Advanced Circuit Breaker Pattern Implementation
Omni Keywords Finder - Infrastructure Resilience

Tracing ID: ADVANCED_CIRCUIT_BREAKER_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO
"""

import time
import asyncio
import logging
from typing import Callable, Any, Optional, Dict, List, Union
from enum import Enum
from dataclasses import dataclass, field
from prometheus_client import Counter, Histogram, Gauge, Summary
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class AdvancedCircuitState(Enum):
    """Estados avançados do circuit breaker"""
    CLOSED = "CLOSED"           # Funcionando normalmente
    OPEN = "OPEN"               # Circuito aberto (falhas)
    HALF_OPEN = "HALF_OPEN"     # Testando recuperação
    FORCED_OPEN = "FORCED_OPEN" # Forçado a abrir
    FORCED_CLOSED = "FORCED_CLOSED" # Forçado a fechar


@dataclass
class AdvancedCircuitBreakerConfig:
    """Configuração avançada do circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    expected_exception: type = Exception
    name: str = "default"
    fallback_function: Optional[Callable] = None
    timeout: Optional[float] = None
    max_concurrent_calls: int = 10
    error_percentage_threshold: float = 50.0
    window_size: int = 100
    enable_metrics: bool = True
    enable_async: bool = False


@dataclass
class CallResult:
    """Resultado de uma chamada"""
    success: bool
    duration: float
    exception: Optional[Exception] = None
    timestamp: float = field(default_factory=time.time)


class AdvancedCircuitBreaker:
    """
    Implementação avançada do padrão Circuit Breaker
    
    Recursos adicionais:
    - Timeout configurável
    - Limite de chamadas concorrentes
    - Threshold baseado em porcentagem de erro
    - Janela deslizante para estatísticas
    - Suporte a async/await
    - Forçar estados manualmente
    """
    
    def __init__(self, config: AdvancedCircuitBreakerConfig):
        self.config = config
        self.state = AdvancedCircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # Janela deslizante para estatísticas
        self.call_results: List[CallResult] = []
        self.call_results_lock = threading.Lock()
        
        # Controle de concorrência
        self.semaphore = asyncio.Semaphore(config.max_concurrent_calls) if config.enable_async else threading.Semaphore(config.max_concurrent_calls)
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_calls)
        
        # Métricas Prometheus (se habilitado)
        if config.enable_metrics:
            self._setup_metrics()
        else:
            self._setup_dummy_metrics()
        
        # Inicializar métricas
        self._update_metrics()
    
    def _setup_metrics(self):
        """Configura métricas Prometheus"""
        self.circuit_state_gauge = Gauge(
            f'advanced_circuit_breaker_state_{self.config.name}',
            f'Estado do circuit breaker avançado {self.config.name}',
            ['state']
        )
        self.failure_counter = Counter(
            f'advanced_circuit_breaker_failures_{self.config.name}',
            f'Falhas no circuit breaker avançado {self.config.name}'
        )
        self.success_counter = Counter(
            f'advanced_circuit_breaker_successes_{self.config.name}',
            f'Sucessos no circuit breaker avançado {self.config.name}'
        )
        self.call_duration = Histogram(
            f'advanced_circuit_breaker_call_duration_{self.config.name}',
            f'Duração das chamadas no circuit breaker avançado {self.config.name}'
        )
        self.error_percentage = Gauge(
            f'advanced_circuit_breaker_error_percentage_{self.config.name}',
            f'Porcentagem de erro no circuit breaker avançado {self.config.name}'
        )
        self.concurrent_calls = Gauge(
            f'advanced_circuit_breaker_concurrent_calls_{self.config.name}',
            f'Chamadas concorrentes no circuit breaker avançado {self.config.name}'
        )
    
    def _setup_dummy_metrics(self):
        """Configura métricas dummy para quando métricas estão desabilitadas"""
        class DummyMetric:
            def inc(self): pass
            def set(self, value): pass
            def time(self): return DummyContext()
            def labels(self, **kwargs): return self
        
        class DummyContext:
            def __enter__(self): return self
            def __exit__(self, *args): pass
        
        self.circuit_state_gauge = DummyMetric()
        self.failure_counter = DummyMetric()
        self.success_counter = DummyMetric()
        self.call_duration = DummyMetric()
        self.error_percentage = DummyMetric()
        self.concurrent_calls = DummyMetric()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função com proteção do circuit breaker avançado
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função ou fallback
        """
        if self.state == AdvancedCircuitState.FORCED_OPEN:
            logger.warning(f"Circuit breaker {self.config.name} está FORCED_OPEN")
            return self._execute_fallback(*args, **kwargs)
        
        if self.state == AdvancedCircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = AdvancedCircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.config.name} tentando reset")
            else:
                logger.warning(f"Circuit breaker {self.config.name} está OPEN, usando fallback")
                return self._execute_fallback(*args, **kwargs)
        
        # Verificar limite de concorrência
        if not self._acquire_semaphore():
            logger.warning(f"Limite de concorrência atingido para {self.config.name}")
            return self._execute_fallback(*args, **kwargs)
        
        try:
            start_time = time.time()
            
            # Executar com timeout se configurado
            if self.config.timeout:
                result = self._execute_with_timeout(func, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            duration = time.time() - start_time
            self._record_call_result(True, duration)
            self._on_success()
            return result
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            self._record_call_result(False, duration, e)
            self._on_failure(e)
            return self._execute_fallback(*args, **kwargs)
        finally:
            self._release_semaphore()
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função assíncrona com proteção do circuit breaker
        
        Args:
            func: Função assíncrona a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função ou fallback
        """
        if not self.config.enable_async:
            raise ValueError("Async não está habilitado para este circuit breaker")
        
        if self.state == AdvancedCircuitState.FORCED_OPEN:
            logger.warning(f"Circuit breaker {self.config.name} está FORCED_OPEN")
            return await self._execute_fallback_async(*args, **kwargs)
        
        if self.state == AdvancedCircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = AdvancedCircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.config.name} tentando reset")
            else:
                logger.warning(f"Circuit breaker {self.config.name} está OPEN, usando fallback")
                return await self._execute_fallback_async(*args, **kwargs)
        
        # Verificar limite de concorrência
        try:
            await self.semaphore.acquire()
        except asyncio.TimeoutError:
            logger.warning(f"Limite de concorrência atingido para {self.config.name}")
            return await self._execute_fallback_async(*args, **kwargs)
        
        try:
            start_time = time.time()
            
            # Executar com timeout se configurado
            if self.config.timeout:
                result = await self._execute_with_timeout_async(func, *args, **kwargs)
            else:
                result = await func(*args, **kwargs)
            
            duration = time.time() - start_time
            self._record_call_result(True, duration)
            self._on_success()
            return result
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            self._record_call_result(False, duration, e)
            self._on_failure(e)
            return await self._execute_fallback_async(*args, **kwargs)
        finally:
            self.semaphore.release()
    
    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com timeout"""
        future = self.executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=self.config.timeout)
        except Exception as e:
            future.cancel()
            raise e
    
    async def _execute_with_timeout_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função assíncrona com timeout"""
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout após {self.config.timeout} segundos")
    
    def _acquire_semaphore(self) -> bool:
        """Adquire semáforo para controle de concorrência"""
        try:
            return self.semaphore.acquire(blocking=False)
        except AttributeError:
            # Para semáforos assíncronos, sempre retorna True
            return True
    
    def _release_semaphore(self):
        """Libera semáforo"""
        try:
            self.semaphore.release()
        except (AttributeError, ValueError):
            # Ignora erros de liberação
            pass
    
    def _record_call_result(self, success: bool, duration: float, exception: Optional[Exception] = None):
        """Registra resultado de uma chamada"""
        with self.call_results_lock:
            result = CallResult(success=success, duration=duration, exception=exception)
            self.call_results.append(result)
            
            # Manter apenas os últimos resultados na janela
            if len(self.call_results) > self.config.window_size:
                self.call_results.pop(0)
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar reset do circuit breaker"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time > self.config.recovery_timeout
    
    def _on_success(self):
        """Callback executado em caso de sucesso"""
        self.success_count += 1
        self.last_success_time = time.time()
        self.success_counter.inc()
        
        if self.state == AdvancedCircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self.state = AdvancedCircuitState.CLOSED
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
        
        # Verificar se deve abrir baseado em threshold ou porcentagem de erro
        should_open = (
            self.failure_count >= self.config.failure_threshold or
            self._get_error_percentage() >= self.config.error_percentage_threshold
        )
        
        if should_open:
            self.state = AdvancedCircuitState.OPEN
            logger.error(f"Circuit breaker {self.config.name} aberto")
        
        self._update_metrics()
    
    def _get_error_percentage(self) -> float:
        """Calcula porcentagem de erro na janela deslizante"""
        with self.call_results_lock:
            if not self.call_results:
                return 0.0
            
            error_count = sum(1 for result in self.call_results if not result.success)
            return (error_count / len(self.call_results)) * 100.0
    
    def _execute_fallback(self, *args, **kwargs) -> Any:
        """Executa função de fallback"""
        if self.config.fallback_function:
            try:
                return self.config.fallback_function(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback também falhou: {e}")
                raise
        
        logger.warning(f"Sem fallback configurado para {self.config.name}")
        return None
    
    async def _execute_fallback_async(self, *args, **kwargs) -> Any:
        """Executa função de fallback assíncrona"""
        if self.config.fallback_function:
            try:
                if asyncio.iscoroutinefunction(self.config.fallback_function):
                    return await self.config.fallback_function(*args, **kwargs)
                else:
                    return self.config.fallback_function(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback também falhou: {e}")
                raise
        
        logger.warning(f"Sem fallback configurado para {self.config.name}")
        return None
    
    def _update_metrics(self):
        """Atualiza métricas Prometheus"""
        # Reset todas as métricas de estado
        for state in AdvancedCircuitState:
            self.circuit_state_gauge.labels(state=state.value).set(0)
        
        # Define estado atual
        self.circuit_state_gauge.labels(state=self.state.value).set(1)
        
        # Atualizar porcentagem de erro
        error_percentage = self._get_error_percentage()
        self.error_percentage.set(error_percentage)
        
        # Atualizar chamadas concorrentes
        try:
            concurrent_calls = self.config.max_concurrent_calls - self.semaphore._value
            self.concurrent_calls.set(concurrent_calls)
        except AttributeError:
            # Para semáforos assíncronos, não é possível obter o valor atual
            pass
    
    def get_state(self) -> AdvancedCircuitState:
        """Retorna estado atual do circuit breaker"""
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do circuit breaker"""
        return {
            'name': self.config.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time,
            'last_success_time': self.last_success_time,
            'failure_threshold': self.config.failure_threshold,
            'recovery_timeout': self.config.recovery_timeout,
            'error_percentage': self._get_error_percentage(),
            'window_size': len(self.call_results),
            'max_concurrent_calls': self.config.max_concurrent_calls
        }
    
    def force_open(self):
        """Força o circuit breaker a abrir"""
        self.state = AdvancedCircuitState.FORCED_OPEN
        self._update_metrics()
        logger.info(f"Circuit breaker {self.config.name} forçado a abrir")
    
    def force_closed(self):
        """Força o circuit breaker a fechar"""
        self.state = AdvancedCircuitState.FORCED_CLOSED
        self._update_metrics()
        logger.info(f"Circuit breaker {self.config.name} forçado a fechar")
    
    def reset(self):
        """Reseta manualmente o circuit breaker"""
        self.state = AdvancedCircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        with self.call_results_lock:
            self.call_results.clear()
        
        self._update_metrics()
        logger.info(f"Circuit breaker {self.config.name} resetado manualmente")


def advanced_circuit_breaker(config: AdvancedCircuitBreakerConfig):
    """
    Decorator para aplicar circuit breaker avançado a funções
    
    Args:
        config: Configuração do circuit breaker avançado
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        cb = AdvancedCircuitBreaker(config)
        
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        async def async_wrapper(*args, **kwargs):
            return await cb.call_async(func, *args, **kwargs)
        
        # Adiciona atributos úteis ao wrapper
        wrapper.circuit_breaker = cb
        wrapper.get_state = cb.get_state
        wrapper.get_stats = cb.get_stats
        wrapper.reset = cb.reset
        wrapper.force_open = cb.force_open
        wrapper.force_closed = cb.force_closed
        
        # Se a função é assíncrona, retorna o wrapper assíncrono
        if asyncio.iscoroutinefunction(func):
            async_wrapper.circuit_breaker = cb
            async_wrapper.get_state = cb.get_state
            async_wrapper.get_stats = cb.get_stats
            async_wrapper.reset = cb.reset
            async_wrapper.force_open = cb.force_open
            async_wrapper.force_closed = cb.force_closed
            return async_wrapper
        
        return wrapper
    
    return decorator 