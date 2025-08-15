"""
🔒 INT-007: Advanced Rate Limiting - Omni Keywords Finder

Tracing ID: INT_007_RATE_LIMITING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Implementar rate limiting avançado com adaptive rate limiting,
per-client limits, burst handling e graceful degradation para o sistema
Omni Keywords Finder.
"""

import os
import time
import json
import hashlib
import logging
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import redis
from functools import wraps
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Estratégias de rate limiting."""
    FIXED = "fixed"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"
    BURST_AWARE = "burst_aware"

class ClientTier(Enum):
    """Níveis de cliente para rate limiting."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"

class ThreatLevel(Enum):
    """Níveis de ameaça."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RateLimitConfig:
    """Configuração de rate limiting."""
    # Configurações básicas
    requests_per_second: int = 10
    requests_per_minute: int = 600
    requests_per_hour: int = 36000
    requests_per_day: int = 864000
    
    # Configurações de burst
    burst_limit: int = 20
    burst_window: int = 5  # segundos
    burst_cooldown: int = 60  # segundos
    
    # Configurações adaptativas
    adaptive_enabled: bool = True
    adaptive_learning_period: int = 3600  # segundos
    adaptive_threshold: float = 2.0
    adaptive_min_rate: float = 1.0
    adaptive_max_rate: float = 100.0
    
    # Configurações por cliente
    per_client_enabled: bool = True
    client_tiers: Dict[ClientTier, Dict[str, int]] = field(default_factory=lambda: {
        ClientTier.FREE: {"requests_per_minute": 60, "burst_limit": 5},
        ClientTier.BASIC: {"requests_per_minute": 300, "burst_limit": 15},
        ClientTier.PREMIUM: {"requests_per_minute": 1000, "burst_limit": 50},
        ClientTier.ENTERPRISE: {"requests_per_minute": 5000, "burst_limit": 200},
        ClientTier.INTERNAL: {"requests_per_minute": 10000, "burst_limit": 500}
    })
    
    # Configurações de Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 2
    redis_ttl: int = 3600
    
    # Configurações de graceful degradation
    graceful_degradation_enabled: bool = True
    degradation_threshold: float = 0.8  # 80% de uso
    degradation_factor: float = 0.5  # reduz pela metade
    
    # Configurações de alertas
    alert_threshold: int = 100
    alert_cooldown: int = 3600  # segundos
    
    # Configurações de whitelist/blacklist
    whitelist_ips: List[str] = field(default_factory=list)
    blacklist_ips: List[str] = field(default_factory=list)

@dataclass
class RateLimitResult:
    """Resultado da verificação de rate limit."""
    allowed: bool
    remaining_requests: int
    reset_time: int
    retry_after: Optional[int] = None
    reason: Optional[str] = None
    client_tier: Optional[ClientTier] = None
    threat_level: ThreatLevel = ThreatLevel.LOW
    adaptive_rate: Optional[float] = None
    burst_status: Optional[str] = None

@dataclass
class RequestInfo:
    """Informações da requisição."""
    timestamp: float
    client_id: str
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    payload_size: int
    response_time: float
    status_code: int
    user_id: Optional[str] = None
    client_tier: Optional[ClientTier] = None

class TokenBucket:
    """Implementação de Token Bucket para rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Tenta adquirir tokens do bucket."""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Reabastece o bucket com tokens."""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_tokens(self) -> float:
        """Retorna o número atual de tokens."""
        with self.lock:
            self._refill()
            return self.tokens

class SlidingWindow:
    """Implementação de Sliding Window para rate limiting."""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self.lock = threading.Lock()
    
    def is_allowed(self) -> bool:
        """Verifica se a requisição é permitida."""
        with self.lock:
            now = time.time()
            
            # Remove requisições antigas
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            # Verifica se há espaço
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_remaining(self) -> int:
        """Retorna o número de requisições restantes."""
        with self.lock:
            now = time.time()
            
            # Remove requisições antigas
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            return max(0, self.max_requests - len(self.requests))

class BurstDetector:
    """Detector de burst para rate limiting."""
    
    def __init__(self, burst_window: int, burst_cooldown: int):
        self.burst_window = burst_window
        self.burst_cooldown = burst_cooldown
        self.burst_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.burst_cooldowns: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def detect_burst(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """Detecta se há burst de requisições."""
        with self.lock:
            now = time.time()
            
            # Verifica se está em cooldown
            if client_id in self.burst_cooldowns:
                if now < self.burst_cooldowns[client_id]:
                    return True, "burst_cooldown"
                else:
                    del self.burst_cooldowns[client_id]
            
            # Analisa histórico de requisições
            requests = self.burst_history[client_id]
            recent_requests = [req for req in requests if now - req < self.burst_window]
            
            if len(recent_requests) > self.burst_window * 2:  # Mais de 2 req/seg
                # Ativa cooldown
                self.burst_cooldowns[client_id] = now + self.burst_cooldown
                return True, "burst_detected"
            
            return False, None
    
    def add_request(self, client_id: str):
        """Adiciona uma requisição ao histórico."""
        with self.lock:
            self.burst_history[client_id].append(time.time())

class AdaptiveRateLimiter:
    """Rate limiter adaptativo baseado em padrões de uso."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.adaptive_rates: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def calculate_adaptive_rate(self, client_id: str, current_usage: float) -> float:
        """Calcula taxa adaptativa baseada no histórico de uso."""
        with self.lock:
            history = self.usage_history[client_id]
            
            if len(history) < 10:  # Precisa de mais dados
                return self.config.requests_per_minute
            
            # Calcula estatísticas
            mean_usage = statistics.mean(history)
            std_usage = statistics.stdev(history) if len(history) > 1 else 0
            
            # Calcula score de anomalia
            if std_usage > 0:
                anomaly_score = abs(current_usage - mean_usage) / std_usage
            else:
                anomaly_score = 0
            
            # Ajusta taxa baseada na anomalia
            if anomaly_score > self.config.adaptive_threshold:
                # Reduz taxa para comportamento anômalo
                adaptive_rate = max(
                    self.config.adaptive_min_rate,
                    self.config.requests_per_minute * (1 - anomaly_score * 0.1)
                )
            else:
                # Aumenta taxa para comportamento normal
                adaptive_rate = min(
                    self.config.adaptive_max_rate,
                    self.config.requests_per_minute * (1 + 0.1)
                )
            
            # Atualiza histórico
            history.append(current_usage)
            self.adaptive_rates[client_id] = adaptive_rate
            
            return adaptive_rate
    
    def get_adaptive_rate(self, client_id: str) -> float:
        """Retorna a taxa adaptativa atual para um cliente."""
        return self.adaptive_rates.get(client_id, self.config.requests_per_minute)

class AdvancedRateLimiting:
    """
    Sistema avançado de rate limiting com funcionalidades enterprise-grade.
    
    Implementa:
    - Adaptive rate limiting
    - Per-client limits
    - Burst handling
    - Graceful degradation
    - Redis integration
    - Threat detection
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Inicializar sistema de rate limiting avançado.
        
        Args:
            config: Configuração do rate limiting
        """
        self.config = config or RateLimitConfig()
        
        # Inicializar componentes
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindow] = {}
        self.burst_detector = BurstDetector(
            self.config.burst_window,
            self.config.burst_cooldown
        )
        self.adaptive_limiter = AdaptiveRateLimiter(self.config)
        
        # Redis para cache distribuído
        self.redis_client = None
        self._setup_redis()
        
        # Cache local
        self.local_cache: Dict[str, Any] = {}
        self.cache_lock = threading.RLock()
        
        # Métricas
        self.metrics = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'burst_detections': 0,
            'adaptive_adjustments': 0,
            'graceful_degradations': 0,
            'redis_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Threading
        self.lock = threading.RLock()
        
        # Background tasks
        self._start_background_tasks()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "advanced_rate_limiting_initialized",
            "status": "success",
            "source": "AdvancedRateLimiting.__init__",
            "details": {
                "requests_per_minute": self.config.requests_per_minute,
                "burst_limit": self.config.burst_limit,
                "adaptive_enabled": self.config.adaptive_enabled,
                "redis_available": self.redis_client is not None
            }
        })
    
    def _setup_redis(self):
        """Configurar conexão com Redis."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Testar conexão
            self.redis_client.ping()
            logger.info("Redis conectado para rate limiting distribuído")
            
        except Exception as e:
            logger.warning(f"Redis não disponível: {str(e)}")
            self.redis_client = None
    
    def _start_background_tasks(self):
        """Iniciar tarefas em background."""
        # Thread para limpeza de cache
        cleanup_thread = threading.Thread(
            target=self._cleanup_cache_worker,
            daemon=True
        )
        cleanup_thread.start()
        
        # Thread para métricas
        metrics_thread = threading.Thread(
            target=self._metrics_worker,
            daemon=True
        )
        metrics_thread.start()
    
    def _cleanup_cache_worker(self):
        """Worker para limpeza de cache."""
        while True:
            try:
                time.sleep(300)  # Limpar a cada 5 minutos
                self._cleanup_expired_cache()
            except Exception as e:
                logger.error(f"Erro no worker de limpeza: {str(e)}")
    
    def _metrics_worker(self):
        """Worker para coleta de métricas."""
        while True:
            try:
                time.sleep(60)  # Coletar a cada minuto
                self._update_metrics()
            except Exception as e:
                logger.error(f"Erro no worker de métricas: {str(e)}")
    
    def _cleanup_expired_cache(self):
        """Limpar cache expirado."""
        with self.cache_lock:
            current_time = time.time()
            expired_keys = []
            
            for key, value in self.local_cache.items():
                if isinstance(value, dict) and 'expires_at' in value:
                    if current_time > value['expires_at']:
                        expired_keys.append(key)
            
            for key in expired_keys:
                del self.local_cache[key]
    
    def _update_metrics(self):
        """Atualizar métricas do sistema."""
        # Métricas podem ser enviadas para sistemas externos
        # como Prometheus, Grafana, etc.
        pass
    
    def _get_client_tier(self, client_id: str, user_id: Optional[str] = None) -> ClientTier:
        """Determinar tier do cliente."""
        # Lógica para determinar tier baseado em client_id ou user_id
        # Por simplicidade, retorna BASIC como padrão
        return ClientTier.BASIC
    
    def _get_cache_key(self, client_id: str, window: str) -> str:
        """Gerar chave de cache."""
        return f"rate_limit:{client_id}:{window}"
    
    def _is_whitelisted(self, ip_address: str) -> bool:
        """Verificar se IP está na whitelist."""
        return ip_address in self.config.whitelist_ips
    
    def _is_blacklisted(self, ip_address: str) -> bool:
        """Verificar se IP está na blacklist."""
        return ip_address in self.config.blacklist_ips
    
    def _get_threat_level(self, client_id: str, request_info: RequestInfo) -> ThreatLevel:
        """Determinar nível de ameaça da requisição."""
        # Lógica simplificada para determinar threat level
        # Em produção, seria mais sofisticada
        
        # Verificar padrões suspeitos
        suspicious_patterns = [
            request_info.payload_size > 1000000,  # Payload muito grande
            request_info.response_time > 10,  # Resposta muito lenta
            request_info.status_code >= 500,  # Erros de servidor
        ]
        
        threat_score = sum(suspicious_patterns)
        
        if threat_score >= 3:
            return ThreatLevel.CRITICAL
        elif threat_score >= 2:
            return ThreatLevel.HIGH
        elif threat_score >= 1:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def check_rate_limit(
        self,
        client_id: str,
        request_info: RequestInfo,
        strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE
    ) -> RateLimitResult:
        """
        Verificar rate limit para um cliente.
        
        Args:
            client_id: ID único do cliente
            request_info: Informações da requisição
            strategy: Estratégia de rate limiting
            
        Returns:
            Resultado da verificação de rate limit
        """
        with self.lock:
            self.metrics['total_requests'] += 1
            
            # Verificações básicas
            if self._is_whitelisted(request_info.ip_address):
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=999999,
                    reset_time=int(time.time() + 3600),
                    reason="IP na whitelist"
                )
            
            if self._is_blacklisted(request_info.ip_address):
                self.metrics['blocked_requests'] += 1
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=int(time.time() + 3600),
                    retry_after=3600,
                    reason="IP na blacklist"
                )
            
            # Determinar tier do cliente
            client_tier = self._get_client_tier(client_id, request_info.user_id)
            tier_config = self.config.client_tiers.get(client_tier, {})
            
            # Obter limites baseados no tier
            requests_per_minute = tier_config.get('requests_per_minute', self.config.requests_per_minute)
            burst_limit = tier_config.get('burst_limit', self.config.burst_limit)
            
            # Verificar burst
            burst_detected, burst_reason = self.burst_detector.detect_burst(client_id)
            if burst_detected:
                self.metrics['burst_detections'] += 1
                self.metrics['blocked_requests'] += 1
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=int(time.time() + self.config.burst_cooldown),
                    retry_after=self.config.burst_cooldown,
                    reason=burst_reason,
                    client_tier=client_tier,
                    burst_status="blocked"
                )
            
            # Adicionar requisição ao detector de burst
            self.burst_detector.add_request(client_id)
            
            # Aplicar estratégia de rate limiting
            if strategy == RateLimitStrategy.TOKEN_BUCKET:
                allowed, remaining = self._check_token_bucket(client_id, requests_per_minute, burst_limit)
            elif strategy == RateLimitStrategy.SLIDING_WINDOW:
                allowed, remaining = self._check_sliding_window(client_id, requests_per_minute)
            elif strategy == RateLimitStrategy.ADAPTIVE:
                allowed, remaining = self._check_adaptive(client_id, requests_per_minute, request_info)
            else:
                allowed, remaining = self._check_fixed(client_id, requests_per_minute)
            
            # Determinar threat level
            threat_level = self._get_threat_level(client_id, request_info)
            
            # Aplicar graceful degradation se necessário
            if self.config.graceful_degradation_enabled and not allowed:
                allowed, remaining = self._apply_graceful_degradation(client_id, requests_per_minute)
            
            # Atualizar métricas
            if allowed:
                self.metrics['allowed_requests'] += 1
            else:
                self.metrics['blocked_requests'] += 1
            
            return RateLimitResult(
                allowed=allowed,
                remaining_requests=remaining,
                reset_time=int(time.time() + 60),
                retry_after=60 if not allowed else None,
                reason="rate_limit_exceeded" if not allowed else None,
                client_tier=client_tier,
                threat_level=threat_level,
                adaptive_rate=self.adaptive_limiter.get_adaptive_rate(client_id) if strategy == RateLimitStrategy.ADAPTIVE else None,
                burst_status="normal"
            )
    
    def _check_token_bucket(self, client_id: str, requests_per_minute: int, burst_limit: int) -> Tuple[bool, int]:
        """Verificar rate limit usando Token Bucket."""
        bucket_key = f"{client_id}:token_bucket"
        
        if bucket_key not in self.token_buckets:
            # Criar novo bucket
            refill_rate = requests_per_minute / 60.0  # tokens por segundo
            self.token_buckets[bucket_key] = TokenBucket(burst_limit, refill_rate)
        
        bucket = self.token_buckets[bucket_key]
        allowed = bucket.acquire(1)
        remaining = int(bucket.get_tokens())
        
        return allowed, remaining
    
    def _check_sliding_window(self, client_id: str, requests_per_minute: int) -> Tuple[bool, int]:
        """Verificar rate limit usando Sliding Window."""
        window_key = f"{client_id}:sliding_window"
        
        if window_key not in self.sliding_windows:
            self.sliding_windows[window_key] = SlidingWindow(60, requests_per_minute)
        
        window = self.sliding_windows[window_key]
        allowed = window.is_allowed()
        remaining = window.get_remaining()
        
        return allowed, remaining
    
    def _check_adaptive(self, client_id: str, base_rate: int, request_info: RequestInfo) -> Tuple[bool, int]:
        """Verificar rate limit usando estratégia adaptativa."""
        # Calcular taxa adaptativa
        current_usage = 1  # Simplificado - seria calculado baseado no histórico
        adaptive_rate = self.adaptive_limiter.calculate_adaptive_rate(client_id, current_usage)
        
        # Usar sliding window com taxa adaptativa
        window_key = f"{client_id}:adaptive_window"
        
        if window_key not in self.sliding_windows:
            self.sliding_windows[window_key] = SlidingWindow(60, int(adaptive_rate))
        else:
            # Atualizar taxa do window existente
            self.sliding_windows[window_key].max_requests = int(adaptive_rate)
        
        window = self.sliding_windows[window_key]
        allowed = window.is_allowed()
        remaining = window.get_remaining()
        
        if allowed:
            self.metrics['adaptive_adjustments'] += 1
        
        return allowed, remaining
    
    def _check_fixed(self, client_id: str, requests_per_minute: int) -> Tuple[bool, int]:
        """Verificar rate limit usando estratégia fixa."""
        return self._check_sliding_window(client_id, requests_per_minute)
    
    def _apply_graceful_degradation(self, client_id: str, base_rate: int) -> Tuple[bool, int]:
        """Aplicar graceful degradation."""
        # Reduzir taxa pela metade
        degraded_rate = int(base_rate * self.config.degradation_factor)
        
        window_key = f"{client_id}:degraded_window"
        
        if window_key not in self.sliding_windows:
            self.sliding_windows[window_key] = SlidingWindow(60, degraded_rate)
        
        window = self.sliding_windows[window_key]
        allowed = window.is_allowed()
        remaining = window.get_remaining()
        
        if allowed:
            self.metrics['graceful_degradations'] += 1
        
        return allowed, remaining
    
    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """Obter estatísticas de um cliente."""
        stats = {
            'client_id': client_id,
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'burst_detections': 0,
            'adaptive_rate': self.adaptive_limiter.get_adaptive_rate(client_id),
            'client_tier': self._get_client_tier(client_id).value
        }
        
        # Adicionar estatísticas de buckets e windows
        bucket_key = f"{client_id}:token_bucket"
        if bucket_key in self.token_buckets:
            stats['token_bucket_tokens'] = self.token_buckets[bucket_key].get_tokens()
        
        window_key = f"{client_id}:sliding_window"
        if window_key in self.sliding_windows:
            stats['sliding_window_remaining'] = self.sliding_windows[window_key].get_remaining()
        
        return stats
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obter métricas do sistema."""
        total = self.metrics['total_requests']
        
        return {
            **self.metrics,
            'allowance_rate': (self.metrics['allowed_requests'] / total * 100) if total > 0 else 0,
            'block_rate': (self.metrics['blocked_requests'] / total * 100) if total > 0 else 0,
            'burst_detection_rate': (self.metrics['burst_detections'] / total * 100) if total > 0 else 0,
            'adaptive_adjustment_rate': (self.metrics['adaptive_adjustments'] / total * 100) if total > 0 else 0,
            'graceful_degradation_rate': (self.metrics['graceful_degradations'] / total * 100) if total > 0 else 0,
            'cache_hit_rate': (self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100) if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0,
            'redis_available': self.redis_client is not None,
            'active_buckets': len(self.token_buckets),
            'active_windows': len(self.sliding_windows)
        }
    
    def reset_client(self, client_id: str):
        """Resetar contadores de um cliente."""
        with self.lock:
            # Remover buckets e windows
            bucket_key = f"{client_id}:token_bucket"
            if bucket_key in self.token_buckets:
                del self.token_buckets[bucket_key]
            
            window_keys = [key for key in self.sliding_windows.keys() if key.startswith(f"{client_id}:")]
            for key in window_keys:
                del self.sliding_windows[key]
            
            # Resetar detector de burst
            self.burst_detector.burst_history[client_id].clear()
            if client_id in self.burst_detector.burst_cooldowns:
                del self.burst_detector.burst_cooldowns[client_id]
            
            # Resetar rate adaptativo
            if client_id in self.adaptive_limiter.adaptive_rates:
                del self.adaptive_limiter.adaptive_rates[client_id]
            
            logger.info(f"Contadores resetados para cliente: {client_id}")
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do sistema."""
        return {
            'status': 'healthy',
            'redis_connection': self.redis_client is not None,
            'active_components': {
                'token_buckets': len(self.token_buckets),
                'sliding_windows': len(self.sliding_windows),
                'burst_detector': True,
                'adaptive_limiter': True
            },
            'timestamp': datetime.utcnow().isoformat()
        }

# Configuração padrão
DEFAULT_RATE_LIMIT_CONFIG = RateLimitConfig(
    requests_per_minute=600,
    burst_limit=20,
    adaptive_enabled=True,
    per_client_enabled=True,
    graceful_degradation_enabled=True
)

def create_advanced_rate_limiting(config: Optional[RateLimitConfig] = None) -> AdvancedRateLimiting:
    """Criar instância do sistema de rate limiting avançado."""
    if config is None:
        config = DEFAULT_RATE_LIMIT_CONFIG
    
    return AdvancedRateLimiting(config)

# Decorator para uso em endpoints
def rate_limited(
    requests_per_minute: int = 60,
    strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE,
    client_id_func: Optional[callable] = None
):
    """
    Decorator para aplicar rate limiting em endpoints.
    
    Args:
        requests_per_minute: Limite de requisições por minuto
        strategy: Estratégia de rate limiting
        client_id_func: Função para extrair client_id da requisição
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extrair client_id
            client_id = "default"
            if client_id_func:
                try:
                    client_id = client_id_func(*args, **kwargs)
                except Exception:
                    pass
            
            # Criar request_info básico
            request_info = RequestInfo(
                timestamp=time.time(),
                client_id=client_id,
                ip_address="127.0.0.1",
                user_agent="",
                endpoint=func.__name__,
                method="GET",
                payload_size=0,
                response_time=0.0,
                status_code=200
            )
            
            # Verificar rate limit
            rate_limiter = create_advanced_rate_limiting()
            result = rate_limiter.check_rate_limit(client_id, request_info, strategy)
            
            if not result.allowed:
                raise Exception(f"Rate limit exceeded: {result.reason}")
            
            # Executar função
            return func(*args, **kwargs)
        
        return wrapper
    return decorator 