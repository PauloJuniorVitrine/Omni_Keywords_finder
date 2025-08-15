"""
Rate Limiter Adaptativo
Responsável por rate limiting adaptativo com algoritmos de adaptação dinâmica.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import time
import asyncio
import random
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import deque

from shared.logger import logger

class RateLimitAlgorithm(Enum):
    """Algoritmos de rate limiting."""
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    SLIDING_WINDOW = "sliding_window"
    ADAPTIVE = "adaptive"

class SystemLoad(Enum):
    """Níveis de carga do sistema."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RateLimitConfig:
    """Configuração do rate limiter."""
    initial_rate: int = 100  # requests per second
    min_rate: int = 10
    max_rate: int = 1000
    burst_size: int = 50
    window_size: int = 60  # seconds
    adaptation_factor: float = 0.1
    load_thresholds: Dict[SystemLoad, float] = field(default_factory=lambda: {
        SystemLoad.LOW: 0.3,
        SystemLoad.MEDIUM: 0.6,
        SystemLoad.HIGH: 0.8,
        SystemLoad.CRITICAL: 0.95
    })

@dataclass
class RateLimitMetrics:
    """Métricas do rate limiter."""
    current_rate: int
    allowed_requests: int
    blocked_requests: int
    system_load: float
    adaptation_count: int
    last_adaptation: datetime
    avg_response_time: float
    error_rate: float

class AdaptiveRateLimiter:
    """
    Rate limiter adaptativo com feedback loop.
    
    Características:
    - Adaptação dinâmica baseada em carga do sistema
    - Múltiplos algoritmos de rate limiting
    - Burst handling inteligente
    - Priority queuing
    - Graceful degradation
    """
    
    def __init__(self, config: RateLimitConfig = None):
        """Inicializar rate limiter adaptativo."""
        self.config = config or RateLimitConfig()
        self.current_rate = self.config.initial_rate
        self.tokens = self.config.burst_size
        self.last_refill = time.time()
        
        # Histórico de requisições
        self.request_history = deque(maxlen=1000)
        self.response_times = deque(maxlen=100)
        self.error_history = deque(maxlen=100)
        
        # Métricas
        self.metrics = {
            'allowed_requests': 0,
            'blocked_requests': 0,
            'adaptation_count': 0,
            'last_adaptation': datetime.utcnow(),
            'avg_response_time': 0.0,
            'error_rate': 0.0
        }
        
        # Callbacks
        self.load_monitor_callback: Optional[Callable] = None
        self.adaptation_callback: Optional[Callable] = None
        
        # Priority queue
        self.priority_queue = {
            'high': deque(),
            'medium': deque(),
            'low': deque()
        }
        
        logger.info(f"AdaptiveRateLimiter inicializado: rate={self.current_rate}/string_data, "
                   f"burst={self.config.burst_size}")
    
    def set_load_monitor_callback(self, callback: Callable[[], float]):
        """Definir callback para monitoramento de carga."""
        self.load_monitor_callback = callback
    
    def set_adaptation_callback(self, callback: Callable[[int, int], None]):
        """Definir callback para adaptação."""
        self.adaptation_callback = callback
    
    async def allow_request(
        self,
        client_id: str = "default",
        priority: str = "medium",
        timeout: float = 1.0
    ) -> bool:
        """
        Verificar se requisição pode ser processada.
        
        Args:
            client_id: ID do cliente
            priority: Prioridade da requisição
            timeout: Timeout para espera
            
        Returns:
            True se requisição pode ser processada
        """
        start_time = time.time()
        
        # Atualizar tokens
        self._refill_tokens()
        
        # Verificar se há tokens disponíveis
        if self.tokens > 0:
            self.tokens -= 1
            self._record_request(start_time, True)
            self.metrics['allowed_requests'] += 1
            return True
        
        # Se não há tokens, verificar prioridade
        if priority == 'high':
            # Requisições de alta prioridade podem usar burst
            if self.config.burst_size > 0:
                self.config.burst_size -= 1
                self._record_request(start_time, True)
                self.metrics['allowed_requests'] += 1
                return True
        
        # Adicionar à fila de prioridade se necessário
        if timeout > 0:
            return await self._wait_in_queue(priority, timeout)
        
        # Bloquear requisição
        self._record_request(start_time, False)
        self.metrics['blocked_requests'] += 1
        return False
    
    async def _wait_in_queue(self, priority: str, timeout: float) -> bool:
        """Esperar na fila de prioridade."""
        queue = self.priority_queue.get(priority, self.priority_queue['medium'])
        
        # Adicionar à fila
        future = asyncio.Future()
        queue.append((time.time(), future))
        
        try:
            # Aguardar com timeout
            await asyncio.wait_for(future, timeout=timeout)
            return future.result()
        except asyncio.TimeoutError:
            # Remover da fila se timeout
            queue[:] = [(t, f) for t, f in queue if f != future]
            return False
    
    def _refill_tokens(self):
        """Reabastecer tokens baseado no tempo decorrido."""
        now = time.time()
        time_passed = now - self.last_refill
        
        # Calcular tokens a adicionar
        tokens_to_add = time_passed * self.current_rate
        
        # Adicionar tokens (respeitando burst size)
        self.tokens = min(
            self.config.burst_size,
            self.tokens + tokens_to_add
        )
        
        self.last_refill = now
    
    def _record_request(self, start_time: float, allowed: bool):
        """Registrar requisição para métricas."""
        duration = time.time() - start_time
        
        self.request_history.append({
            'timestamp': time.time(),
            'allowed': allowed,
            'duration': duration
        })
        
        if allowed:
            self.response_times.append(duration)
    
    def record_response_time(self, response_time: float):
        """Registrar tempo de resposta."""
        self.response_times.append(response_time)
    
    def record_error(self, error: str):
        """Registrar erro."""
        self.error_history.append({
            'timestamp': time.time(),
            'error': error
        })
    
    def adapt_rate(self):
        """Adaptar rate baseado em métricas do sistema."""
        # Obter carga atual do sistema
        current_load = self._get_system_load()
        
        # Calcular métricas
        avg_response_time = self._calculate_avg_response_time()
        error_rate = self._calculate_error_rate()
        
        # Determinar nova taxa
        new_rate = self._calculate_adaptive_rate(current_load, avg_response_time, error_rate)
        
        # Aplicar adaptação
        if abs(new_rate - self.current_rate) > self.current_rate * self.config.adaptation_factor:
            old_rate = self.current_rate
            self.current_rate = max(self.config.min_rate, min(self.config.max_rate, new_rate))
            
            # Atualizar métricas
            self.metrics['adaptation_count'] += 1
            self.metrics['last_adaptation'] = datetime.utcnow()
            self.metrics['avg_response_time'] = avg_response_time
            self.metrics['error_rate'] = error_rate
            
            # Log da adaptação
            logger.info(f"Rate adaptado: {old_rate} -> {self.current_rate}/string_data "
                       f"(load={current_load:.2f}, response_time={avg_response_time:.3f}string_data, "
                       f"error_rate={error_rate:.2%})")
            
            # Callback de adaptação
            if self.adaptation_callback:
                self.adaptation_callback(old_rate, self.current_rate)
    
    def _get_system_load(self) -> float:
        """Obter carga atual do sistema."""
        if self.load_monitor_callback:
            return self.load_monitor_callback()
        
        # Implementação padrão baseada em métricas locais
        recent_requests = [
            req for req in self.request_history
            if time.time() - req['timestamp'] < 60
        ]
        
        if not recent_requests:
            return 0.0
        
        # Calcular carga baseada em volume de requisições
        request_rate = len(recent_requests) / 60.0
        return min(1.0, request_rate / self.current_rate)
    
    def _calculate_avg_response_time(self) -> float:
        """Calcular tempo médio de resposta."""
        if not self.response_times:
            return 0.0
        
        recent_times = [
            rt for rt in self.response_times
            if time.time() - rt < 300  # Últimos 5 minutos
        ]
        
        if not recent_times:
            return 0.0
        
        return sum(recent_times) / len(recent_times)
    
    def _calculate_error_rate(self) -> float:
        """Calcular taxa de erro."""
        if not self.error_history:
            return 0.0
        
        recent_errors = [
            err for err in self.error_history
            if time.time() - err['timestamp'] < 300  # Últimos 5 minutos
        ]
        
        recent_requests = [
            req for req in self.request_history
            if time.time() - req['timestamp'] < 300
        ]
        
        if not recent_requests:
            return 0.0
        
        return len(recent_errors) / len(recent_requests)
    
    def _calculate_adaptive_rate(
        self,
        system_load: float,
        avg_response_time: float,
        error_rate: float
    ) -> int:
        """Calcular nova taxa baseada em métricas."""
        # Fatores de ajuste
        load_factor = 1.0 - (system_load * 0.5)  # Reduzir se carga alta
        response_factor = 1.0 - (avg_response_time * 10)  # Reduzir se resposta lenta
        error_factor = 1.0 - (error_rate * 2)  # Reduzir se muitos erros
        
        # Combinar fatores
        adjustment_factor = (load_factor + response_factor + error_factor) / 3
        
        # Calcular nova taxa
        new_rate = int(self.current_rate * adjustment_factor)
        
        # Aplicar limites
        new_rate = max(self.config.min_rate, min(self.config.max_rate, new_rate))
        
        return new_rate
    
    def get_metrics(self) -> RateLimitMetrics:
        """Obter métricas atuais."""
        return RateLimitMetrics(
            current_rate=self.current_rate,
            allowed_requests=self.metrics['allowed_requests'],
            blocked_requests=self.metrics['blocked_requests'],
            system_load=self._get_system_load(),
            adaptation_count=self.metrics['adaptation_count'],
            last_adaptation=self.metrics['last_adaptation'],
            avg_response_time=self._calculate_avg_response_time(),
            error_rate=self._calculate_error_rate()
        )
    
    def get_system_load_level(self) -> SystemLoad:
        """Obter nível de carga do sistema."""
        load = self._get_system_load()
        
        if load >= self.config.load_thresholds[SystemLoad.CRITICAL]:
            return SystemLoad.CRITICAL
        elif load >= self.config.load_thresholds[SystemLoad.HIGH]:
            return SystemLoad.HIGH
        elif load >= self.config.load_thresholds[SystemLoad.MEDIUM]:
            return SystemLoad.MEDIUM
        else:
            return SystemLoad.LOW
    
    def reset_metrics(self):
        """Resetar métricas."""
        self.metrics = {
            'allowed_requests': 0,
            'blocked_requests': 0,
            'adaptation_count': 0,
            'last_adaptation': datetime.utcnow(),
            'avg_response_time': 0.0,
            'error_rate': 0.0
        }
        self.request_history.clear()
        self.response_times.clear()
        self.error_history.clear()
        logger.info("Métricas do rate limiter resetadas")

class TokenBucketRateLimiter:
    """Implementação do algoritmo Token Bucket."""
    
    def __init__(self, rate: int, capacity: int):
        """Inicializar token bucket."""
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
    
    def allow_request(self) -> bool:
        """Verificar se requisição pode ser processada."""
        self._refill_tokens()
        
        if self.tokens > 0:
            self.tokens -= 1
            return True
        
        return False
    
    def _refill_tokens(self):
        """Reabastecer tokens."""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

class LeakyBucketRateLimiter:
    """Implementação do algoritmo Leaky Bucket."""
    
    def __init__(self, rate: int, capacity: int):
        """Inicializar leaky bucket."""
        self.rate = rate
        self.capacity = capacity
        self.queue = deque(maxlen=capacity)
        self.last_leak = time.time()
    
    def allow_request(self) -> bool:
        """Verificar se requisição pode ser processada."""
        self._leak_tokens()
        
        if len(self.queue) < self.capacity:
            self.queue.append(time.time())
            return True
        
        return False
    
    def _leak_tokens(self):
        """Vazar tokens da fila."""
        now = time.time()
        time_passed = now - self.last_leak
        tokens_to_remove = int(time_passed * self.rate)
        
        for _ in range(min(tokens_to_remove, len(self.queue))):
            self.queue.popleft()
        
        self.last_leak = now

class SlidingWindowRateLimiter:
    """Implementação do algoritmo Sliding Window."""
    
    def __init__(self, rate: int, window_size: int):
        """Inicializar sliding window."""
        self.rate = rate
        self.window_size = window_size
        self.requests = deque()
    
    def allow_request(self) -> bool:
        """Verificar se requisição pode ser processada."""
        now = time.time()
        
        # Remover requisições antigas
        while self.requests and now - self.requests[0] > self.window_size:
            self.requests.popleft()
        
        # Verificar se pode adicionar nova requisição
        if len(self.requests) < self.rate:
            self.requests.append(now)
            return True
        
        return False 