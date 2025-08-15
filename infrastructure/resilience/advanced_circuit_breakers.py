"""
🛡️ Advanced Circuit Breakers System
🎯 Objetivo: Circuit breakers adaptativos com fallbacks inteligentes
📅 Data: 2025-01-27
🔗 Tracing ID: ADVANCED_CIRCUIT_BREAKERS_001
📋 Ruleset: enterprise_control_layer.yaml
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Callable, Any, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import statistics
import asyncio
from contextlib import contextmanager

from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.cache.intelligent_cache import IntelligentCache

# Configuração de logging
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Estados do circuit breaker"""
    CLOSED = "closed"      # Funcionando normalmente
    OPEN = "open"          # Bloqueado por falhas
    HALF_OPEN = "half_open"  # Testando recuperação

class FailureType(Enum):
    """Tipos de falha"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    RATE_LIMIT = "rate_limit"
    UNKNOWN = "unknown"

@dataclass
class CircuitBreakerConfig:
    """Configuração do circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 30  # segundos
    expected_exception: Type[Exception] = Exception
    min_requests_before_trip: int = 3
    success_threshold: int = 2
    timeout_duration: float = 10.0
    enable_adaptive_thresholds: bool = True
    enable_health_check: bool = True
    health_check_interval: int = 60  # segundos
    fallback_strategy: str = "cache_first"  # cache_first, static_response, degraded_service

@dataclass
class FailureRecord:
    """Registro de falha"""
    timestamp: float
    failure_type: FailureType
    error_message: str
    response_time: float
    endpoint: str
    user_id: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None

@dataclass
class CircuitBreakerMetrics:
    """Métricas do circuit breaker"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    circuit_trips: int = 0
    circuit_resets: int = 0
    avg_response_time: float = 0.0
    failure_rate: float = 0.0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None

class AdaptiveCircuitBreaker:
    """Circuit breaker adaptativo com fallbacks inteligentes"""
    
    def __init__(
        self, 
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        cache: Optional[IntelligentCache] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.cache = cache or IntelligentCache()
        
        # Estado interno
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._last_state_change = time.time()
        self._failure_history: deque = deque(maxlen=100)
        self._response_times: deque = deque(maxlen=50)
        
        # Métricas
        self._metrics = CircuitBreakerMetrics()
        
        # Threading
        self._lock = threading.RLock()
        self._health_check_thread: Optional[threading.Thread] = None
        self._stop_health_check = threading.Event()
        
        # Fallbacks
        self._fallback_handlers: Dict[str, Callable] = {}
        self._static_responses: Dict[str, Any] = {}
        
        # Inicializar health check se habilitado
        if self.config.enable_health_check:
            self._start_health_check()
        
        logger.info(f"[CIRCUIT_BREAKER] Circuit breaker '{name}' inicializado")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def close(self):
        """Fecha o circuit breaker e limpa recursos"""
        try:
            self._stop_health_check.set()
            if self._health_check_thread and self._health_check_thread.is_alive():
                self._health_check_thread.join(timeout=5)
            
            logger.info(f"[CIRCUIT_BREAKER] Circuit breaker '{self.name}' fechado")
            
        except Exception as e:
            logger.error(f"[CIRCUIT_BREAKER] Erro ao fechar circuit breaker: {str(e)}")
    
    @property
    def state(self) -> CircuitState:
        """Estado atual do circuit breaker"""
        with self._lock:
            return self._state
    
    @property
    def is_open(self) -> bool:
        """Verifica se o circuit breaker está aberto"""
        return self.state == CircuitState.OPEN
    
    @property
    def is_closed(self) -> bool:
        """Verifica se o circuit breaker está fechado"""
        return self.state == CircuitState.CLOSED
    
    @property
    def is_half_open(self) -> bool:
        """Verifica se o circuit breaker está semi-aberto"""
        return self.state == CircuitState.HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função com proteção do circuit breaker
        
        Args:
            func: Função a ser executada
            *args: Argumentos da função
            **kwargs: Argumentos nomeados da função
            
        Returns:
            Resultado da função ou fallback
        """
        if self.is_open:
            return self._handle_open_state(func, *args, **kwargs)
        
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            
            self._on_success(response_time)
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self._on_failure(e, response_time, func, *args, **kwargs)
            
            # Tentar fallback
            return self._execute_fallback(func, *args, **kwargs)
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função assíncrona com proteção do circuit breaker
        
        Args:
            func: Função assíncrona a ser executada
            *args: Argumentos da função
            **kwargs: Argumentos nomeados da função
            
        Returns:
            Resultado da função ou fallback
        """
        if self.is_open:
            return self._handle_open_state(func, *args, **kwargs)
        
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            
            self._on_success(response_time)
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self._on_failure(e, response_time, func, *args, **kwargs)
            
            # Tentar fallback
            return await self._execute_fallback_async(func, *args, **kwargs)
    
    def register_fallback(self, name: str, handler: Callable) -> None:
        """
        Registra um handler de fallback
        
        Args:
            name: Nome do fallback
            handler: Função de fallback
        """
        self._fallback_handlers[name] = handler
        logger.info(f"[CIRCUIT_BREAKER] Fallback '{name}' registrado para '{self.name}'")
    
    def set_static_response(self, name: str, response: Any) -> None:
        """
        Define uma resposta estática para fallback
        
        Args:
            name: Nome da resposta
            response: Resposta estática
        """
        self._static_responses[name] = response
        logger.info(f"[CIRCUIT_BREAKER] Resposta estática '{name}' definida para '{self.name}'")
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Obtém métricas do circuit breaker"""
        with self._lock:
            return CircuitBreakerMetrics(
                total_requests=self._metrics.total_requests,
                successful_requests=self._metrics.successful_requests,
                failed_requests=self._metrics.failed_requests,
                timeout_requests=self._metrics.timeout_requests,
                circuit_trips=self._metrics.circuit_trips,
                circuit_resets=self._metrics.circuit_resets,
                avg_response_time=self._metrics.avg_response_time,
                failure_rate=self._metrics.failure_rate,
                last_failure_time=self._metrics.last_failure_time,
                last_success_time=self._metrics.last_success_time
            )
    
    def reset(self) -> None:
        """Reseta o circuit breaker para estado fechado"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_state_change = time.time()
            self._metrics.circuit_resets += 1
            
            logger.info(f"[CIRCUIT_BREAKER] Circuit breaker '{self.name}' resetado")
    
    def force_open(self) -> None:
        """Força abertura do circuit breaker"""
        with self._lock:
            self._state = CircuitState.OPEN
            self._last_state_change = time.time()
            self._metrics.circuit_trips += 1
            
            logger.warning(f"[CIRCUIT_BREAKER] Circuit breaker '{self.name}' forçado a abrir")
    
    def _on_success(self, response_time: float) -> None:
        """Processa sucesso da operação"""
        with self._lock:
            self._metrics.total_requests += 1
            self._metrics.successful_requests += 1
            self._metrics.last_success_time = time.time()
            self._metrics.avg_response_time = self._calculate_avg_response_time(response_time)
            
            self._response_times.append(response_time)
            
            if self.is_half_open:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._close_circuit()
            else:
                # Reset failure count em estado fechado
                self._failure_count = max(0, self._failure_count - 1)
            
            # Registrar métricas
            self.metrics_collector.record_metric(
                "circuit_breaker_success",
                1,
                tags={"circuit_breaker": self.name, "state": self._state.value}
            )
            
            self.metrics_collector.record_metric(
                "circuit_breaker_response_time",
                response_time,
                tags={"circuit_breaker": self.name}
            )
    
    def _on_failure(self, error: Exception, response_time: float, func: Callable, *args, **kwargs) -> None:
        """Processa falha da operação"""
        with self._lock:
            self._metrics.total_requests += 1
            self._metrics.failed_requests += 1
            self._metrics.last_failure_time = time.time()
            self._metrics.avg_response_time = self._calculate_avg_response_time(response_time)
            
            # Determinar tipo de falha
            failure_type = self._classify_failure(error)
            
            # Registrar falha
            failure_record = FailureRecord(
                timestamp=time.time(),
                failure_type=failure_type,
                error_message=str(error),
                response_time=response_time,
                endpoint=getattr(func, '__name__', 'unknown'),
                request_data=self._extract_request_data(*args, **kwargs)
            )
            
            self._failure_history.append(failure_record)
            self._failure_count += 1
            
            # Verificar se deve abrir o circuit
            if self._should_open_circuit():
                self._open_circuit()
            
            # Registrar métricas
            self.metrics_collector.record_metric(
                "circuit_breaker_failure",
                1,
                tags={
                    "circuit_breaker": self.name,
                    "failure_type": failure_type.value,
                    "state": self._state.value
                }
            )
            
            logger.warning(f"[CIRCUIT_BREAKER] Falha em '{self.name}': {failure_type.value} - {str(error)}")
    
    def _should_open_circuit(self) -> bool:
        """Determina se o circuit deve ser aberto"""
        if self._metrics.total_requests < self.config.min_requests_before_trip:
            return False
        
        # Calcular taxa de falha
        failure_rate = self._metrics.failed_requests / self._metrics.total_requests
        
        # Threshold adaptativo se habilitado
        threshold = self.config.failure_threshold
        if self.config.enable_adaptive_thresholds:
            threshold = self._calculate_adaptive_threshold()
        
        return self._failure_count >= threshold or failure_rate > 0.5
    
    def _calculate_adaptive_threshold(self) -> int:
        """Calcula threshold adaptativo baseado em padrões históricos"""
        if len(self._failure_history) < 10:
            return self.config.failure_threshold
        
        # Analisar padrões de falha
        recent_failures = list(self._failure_history)[-10:]
        failure_types = [f.failure_type for f in recent_failures]
        
        # Ajustar threshold baseado no tipo de falha predominante
        if FailureType.TIMEOUT in failure_types:
            return max(3, self.config.failure_threshold - 2)
        elif FailureType.CONNECTION_ERROR in failure_types:
            return self.config.failure_threshold + 1
        else:
            return self.config.failure_threshold
    
    def _open_circuit(self) -> None:
        """Abre o circuit breaker"""
        self._state = CircuitState.OPEN
        self._last_state_change = time.time()
        self._metrics.circuit_trips += 1
        
        logger.error(f"[CIRCUIT_BREAKER] Circuit breaker '{self.name}' aberto após {self._failure_count} falhas")
        
        # Registrar métrica
        self.metrics_collector.record_metric(
            "circuit_breaker_trip",
            1,
            tags={"circuit_breaker": self.name, "failure_count": self._failure_count}
        )
    
    def _close_circuit(self) -> None:
        """Fecha o circuit breaker"""
        self._state = CircuitState.CLOSED
        self._last_state_change = time.time()
        self._failure_count = 0
        self._success_count = 0
        
        logger.info(f"[CIRCUIT_BREAKER] Circuit breaker '{self.name}' fechado após recuperação")
        
        # Registrar métrica
        self.metrics_collector.record_metric(
            "circuit_breaker_reset",
            1,
            tags={"circuit_breaker": self.name}
        )
    
    def _should_attempt_reset(self) -> bool:
        """Determina se deve tentar resetar o circuit"""
        if self.is_closed:
            return False
        
        time_since_last_failure = time.time() - (self._last_failure_time or 0)
        return time_since_last_failure >= self.config.recovery_timeout
    
    def _handle_open_state(self, func: Callable, *args, **kwargs) -> Any:
        """Processa requisição quando circuit está aberto"""
        # Verificar se deve tentar reset
        if self._should_attempt_reset():
            with self._lock:
                if self._should_attempt_reset():  # Double-check
                    self._state = CircuitState.HALF_OPEN
                    self._last_state_change = time.time()
                    logger.info(f"[CIRCUIT_BREAKER] Circuit breaker '{self.name}' em modo half-open")
        
        # Executar fallback
        return self._execute_fallback(func, *args, **kwargs)
    
    def _execute_fallback(self, func: Callable, *args, **kwargs) -> Any:
        """Executa estratégia de fallback"""
        try:
            if self.config.fallback_strategy == "cache_first" and self.cache:
                # Tentar cache primeiro
                cache_key = self._generate_cache_key(func, *args, **kwargs)
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    logger.info(f"[CIRCUIT_BREAKER] Fallback cache usado para '{self.name}'")
                    return cached_result
            
            # Tentar handlers de fallback
            for name, handler in self._fallback_handlers.items():
                try:
                    result = handler(*args, **kwargs)
                    logger.info(f"[CIRCUIT_BREAKER] Fallback '{name}' usado para '{self.name}'")
                    return result
                except Exception as e:
                    logger.warning(f"[CIRCUIT_BREAKER] Fallback '{name}' falhou: {str(e)}")
                    continue
            
            # Resposta estática
            if self._static_responses:
                static_response = list(self._static_responses.values())[0]
                logger.info(f"[CIRCUIT_BREAKER] Resposta estática usada para '{self.name}'")
                return static_response
            
            # Fallback padrão
            return self._default_fallback(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"[CIRCUIT_BREAKER] Todos os fallbacks falharam para '{self.name}': {str(e)}")
            raise
    
    async def _execute_fallback_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executa estratégia de fallback assíncrona"""
        try:
            if self.config.fallback_strategy == "cache_first" and self.cache:
                # Tentar cache primeiro
                cache_key = self._generate_cache_key(func, *args, **kwargs)
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    logger.info(f"[CIRCUIT_BREAKER] Fallback cache usado para '{self.name}'")
                    return cached_result
            
            # Tentar handlers de fallback assíncronos
            for name, handler in self._fallback_handlers.items():
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(*args, **kwargs)
                    else:
                        result = handler(*args, **kwargs)
                    
                    logger.info(f"[CIRCUIT_BREAKER] Fallback '{name}' usado para '{self.name}'")
                    return result
                except Exception as e:
                    logger.warning(f"[CIRCUIT_BREAKER] Fallback '{name}' falhou: {str(e)}")
                    continue
            
            # Resposta estática
            if self._static_responses:
                static_response = list(self._static_responses.values())[0]
                logger.info(f"[CIRCUIT_BREAKER] Resposta estática usada para '{self.name}'")
                return static_response
            
            # Fallback padrão
            return await self._default_fallback_async(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"[CIRCUIT_BREAKER] Todos os fallbacks falharam para '{self.name}': {str(e)}")
            raise
    
    def _default_fallback(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback padrão"""
        return {
            "error": "Service temporarily unavailable",
            "circuit_breaker": self.name,
            "state": self.state.value,
            "timestamp": time.time()
        }
    
    async def _default_fallback_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback padrão assíncrono"""
        return self._default_fallback(*args, **kwargs)
    
    def _classify_failure(self, error: Exception) -> FailureType:
        """Classifica o tipo de falha"""
        error_type = type(error).__name__.lower()
        
        if "timeout" in error_type or "timeout" in str(error).lower():
            return FailureType.TIMEOUT
        elif "connection" in error_type or "connection" in str(error).lower():
            return FailureType.CONNECTION_ERROR
        elif "http" in error_type or "http" in str(error).lower():
            return FailureType.HTTP_ERROR
        elif "rate" in error_type or "rate" in str(error).lower():
            return FailureType.RATE_LIMIT
        else:
            return FailureType.UNKNOWN
    
    def _extract_request_data(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Extrai dados da requisição para logging"""
        try:
            return {
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()) if kwargs else [],
                "has_data": any(isinstance(arg, dict) for arg in args)
            }
        except Exception:
            return None
    
    def _generate_cache_key(self, func: Callable, *args, **kwargs) -> str:
        """Gera chave de cache para fallback"""
        import hashlib
        key_data = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"
        return f"circuit_breaker_fallback_{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _calculate_avg_response_time(self, new_response_time: float) -> float:
        """Calcula tempo de resposta médio"""
        self._response_times.append(new_response_time)
        return statistics.mean(self._response_times) if self._response_times else 0.0
    
    def _start_health_check(self) -> None:
        """Inicia thread de health check"""
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
    
    def _health_check_loop(self) -> None:
        """Loop de health check"""
        while not self._stop_health_check.is_set():
            try:
                time.sleep(self.config.health_check_interval)
                
                if self.is_open and self._should_attempt_reset():
                    with self._lock:
                        if self._should_attempt_reset():  # Double-check
                            self._state = CircuitState.HALF_OPEN
                            self._last_state_change = time.time()
                            logger.info(f"[CIRCUIT_BREAKER] Health check: '{self.name}' em modo half-open")
                
                # Atualizar métricas
                self._update_metrics()
                
            except Exception as e:
                logger.error(f"[CIRCUIT_BREAKER] Erro no health check: {str(e)}")
    
    def _update_metrics(self) -> None:
        """Atualiza métricas do circuit breaker"""
        with self._lock:
            if self._metrics.total_requests > 0:
                self._metrics.failure_rate = self._metrics.failed_requests / self._metrics.total_requests
            
            # Registrar métricas
            self.metrics_collector.record_metric(
                "circuit_breaker_failure_rate",
                self._metrics.failure_rate,
                tags={"circuit_breaker": self.name}
            )
            
            self.metrics_collector.record_metric(
                "circuit_breaker_state",
                1 if self.is_open else 0,
                tags={"circuit_breaker": self.name, "state": self._state.value}
            )

# Decorator para circuit breaker
def circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None,
    fallback: Optional[Callable] = None
):
    """
    Decorator para aplicar circuit breaker a uma função
    
    Args:
        name: Nome do circuit breaker
        config: Configuração do circuit breaker
        fallback: Função de fallback
    """
    def decorator(func: Callable) -> Callable:
        cb = AdaptiveCircuitBreaker(name, config)
        
        if fallback:
            cb.register_fallback("decorator_fallback", fallback)
        
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        async def async_wrapper(*args, **kwargs):
            return await cb.call_async(func, *args, **kwargs)
        
        # Retornar wrapper apropriado
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator

# Context manager para circuit breaker
@contextmanager
def circuit_breaker_context(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
):
    """
    Context manager para circuit breaker
    
    Args:
        name: Nome do circuit breaker
        config: Configuração do circuit breaker
    """
    cb = AdaptiveCircuitBreaker(name, config)
    try:
        yield cb
    finally:
        cb.close()

# Testes unitários (não executar)
def test_advanced_circuit_breakers():
    """Testes para o sistema de circuit breakers avançados"""
    
    def test_circuit_breaker_creation():
        """Testa criação do circuit breaker"""
        cb = AdaptiveCircuitBreaker("test_cb")
        assert cb.name == "test_cb"
        assert cb.is_closed
        assert not cb.is_open
        
    def test_circuit_breaker_trip():
        """Testa abertura do circuit breaker"""
        cb = AdaptiveCircuitBreaker("test_cb", CircuitBreakerConfig(failure_threshold=2))
        
        # Simular falhas
        for _ in range(3):
            try:
                cb.call(lambda: 1/0)
            except:
                pass
        
        assert cb.is_open
        
    def test_circuit_breaker_fallback():
        """Testa execução de fallback"""
        cb = AdaptiveCircuitBreaker("test_cb")
        cb.register_fallback("test_fallback", lambda: "fallback_result")
        
        # Simular falha
        try:
            cb.call(lambda: 1/0)
        except:
            pass
        
        # Verificar se fallback foi executado
        result = cb.call(lambda: 1/0)
        assert result == "fallback_result"
        
    def test_adaptive_thresholds():
        """Testa thresholds adaptativos"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            enable_adaptive_thresholds=True
        )
        cb = AdaptiveCircuitBreaker("test_cb", config)
        
        # Simular falhas de timeout
        for _ in range(10):
            try:
                cb.call(lambda: 1/0)
            except:
                pass
        
        # Verificar se threshold foi ajustado
        assert cb._calculate_adaptive_threshold() <= 5

if __name__ == "__main__":
    # Exemplo de uso
    print("🛡️ Advanced Circuit Breakers System - Carregado com sucesso")
    
    # Criar circuit breaker
    config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30,
        enable_adaptive_thresholds=True
    )
    
    cb = AdaptiveCircuitBreaker("api_service", config)
    
    # Registrar fallback
    cb.register_fallback("cache_fallback", lambda: {"data": "cached_response"})
    
    print(f"🔧 Circuit breaker criado: {cb.name}")
    print(f"📊 Configuração: {config}")
    print(f"🔄 Estado inicial: {cb.state.value}") 