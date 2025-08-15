"""
Sistema de Rate Limiting Inteligente.
Implementa proteção adaptativa contra abuso com detecção de padrões.
"""
import asyncio
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import os
from collections import defaultdict, deque

from shared.cache import get_cache
from shared.logger import logger

class RateLimitStrategy(Enum):
    """Estratégias de rate limiting."""
    FIXED = "fixed"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    ADAPTIVE = "adaptive"

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
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    
    # Configurações avançadas
    burst_limit: int = 10
    window_size: int = 60  # segundos
    cooldown_period: int = 300  # segundos
    
    # Configurações adaptativas
    adaptive_enabled: bool = True
    learning_period: int = 3600  # segundos
    anomaly_threshold: float = 2.0
    
    # Configurações de whitelist/blacklist
    whitelist_ips: List[str] = field(default_factory=list)
    blacklist_ips: List[str] = field(default_factory=list)
    
    # Configurações de notificação
    alert_threshold: int = 100
    alert_cooldown: int = 3600  # segundos

@dataclass
class RequestInfo:
    """Informações de uma requisição."""
    timestamp: float
    ip: str
    user_agent: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    payload_size: int = 0

class PatternDetector:
    """Detector de padrões suspeitos."""
    
    def __init__(self, window_size: int = 300):
        self.window_size = window_size
        self.patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.anomaly_scores: Dict[str, float] = defaultdict(float)
    
    def add_request(self, request: RequestInfo) -> float:
        """
        Adiciona requisição e calcula score de anomalia.
        
        Args:
            request: Informações da requisição
            
        Returns:
            Score de anomalia (0-1)
        """
        key = f"{request.ip}:{request.endpoint}"
        self.patterns[key].append(request)
        
        # Calcula métricas
        recent_requests = list(self.patterns[key])[-50:]  # Últimas 50 requisições
        
        if len(recent_requests) < 10:
            return 0.0
        
        # Análise de padrões
        scores = []
        
        # 1. Frequência de requisições
        freq_score = self._analyze_frequency(recent_requests)
        scores.append(freq_score)
        
        # 2. Padrão de horário
        time_score = self._analyze_time_pattern(recent_requests)
        scores.append(time_score)
        
        # 3. Padrão de payload
        payload_score = self._analyze_payload_pattern(recent_requests)
        scores.append(payload_score)
        
        # 4. Padrão de user agent
        ua_score = self._analyze_user_agent_pattern(recent_requests)
        scores.append(ua_score)
        
        # 5. Padrão de resposta
        response_score = self._analyze_response_pattern(recent_requests)
        scores.append(response_score)
        
        # Score final (média ponderada)
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        final_score = sum(string_data * w for string_data, w in zip(scores, weights))
        
        # Atualiza score de anomalia
        self.anomaly_scores[key] = final_score
        
        return final_score
    
    def _analyze_frequency(self, requests: List[RequestInfo]) -> float:
        """Analisa frequência de requisições."""
        if len(requests) < 2:
            return 0.0
        
        intervals = []
        for index in range(1, len(requests)):
            interval = requests[index].timestamp - requests[index-1].timestamp
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Detecta padrões muito regulares (bot-like)
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((value - mean_interval) ** 2 for value in intervals) / len(intervals)
        
        # Score baseado na regularidade
        regularity_score = 1.0 / (1.0 + variance)
        
        # Score baseado na frequência
        freq_score = min(1.0, mean_interval / 2.0)  # Muito frequente = suspeito
        
        return (regularity_score + freq_score) / 2.0
    
    def _analyze_time_pattern(self, requests: List[RequestInfo]) -> float:
        """Analisa padrão temporal."""
        if len(requests) < 10:
            return 0.0
        
        # Analisa distribuição por hora do dia
        hours = [datetime.fromtimestamp(r.timestamp).hour for r in requests]
        hour_counts = defaultdict(int)
        
        for hour in hours:
            hour_counts[hour] += 1
        
        # Detecta atividade 24/7 (suspeito)
        active_hours = len(hour_counts)
        if active_hours > 20:  # Ativo em mais de 20 horas
            return 0.8
        
        # Detecta atividade em horários suspeitos (2-6 AM)
        suspicious_hours = sum(1 for h in hours if 2 <= h <= 6)
        suspicious_ratio = suspicious_hours / len(hours)
        
        return suspicious_ratio
    
    def _analyze_payload_pattern(self, requests: List[RequestInfo]) -> float:
        """Analisa padrão de payload."""
        if not requests:
            return 0.0
        
        payload_sizes = [r.payload_size for r in requests]
        
        # Detecta payloads idênticos (suspeito)
        unique_sizes = len(set(payload_sizes))
        if unique_sizes == 1 and len(payload_sizes) > 5:
            return 0.9
        
        # Detecta payloads muito grandes ou pequenos
        avg_size = sum(payload_sizes) / len(payload_sizes)
        if avg_size > 10000 or avg_size < 10:
            return 0.6
        
        return 0.0
    
    def _analyze_user_agent_pattern(self, requests: List[RequestInfo]) -> float:
        """Analisa padrão de user agent."""
        if not requests:
            return 0.0
        
        user_agents = [r.user_agent for r in requests]
        unique_agents = len(set(user_agents))
        
        # Muitos user agents diferentes = suspeito
        if unique_agents > len(user_agents) * 0.8:
            return 0.7
        
        # User agent vazio ou suspeito
        suspicious_agents = sum(1 for ua in user_agents 
                              if not ua or 'bot' in ua.lower() or 'crawler' in ua.lower())
        suspicious_ratio = suspicious_agents / len(user_agents)
        
        return suspicious_ratio
    
    def _analyze_response_pattern(self, requests: List[RequestInfo]) -> float:
        """Analisa padrão de resposta."""
        if not requests:
            return 0.0
        
        # Detecta muitas requisições com erro
        error_requests = sum(1 for r in requests if r.status_code >= 400)
        error_ratio = error_requests / len(requests)
        
        # Detecta tempos de resposta muito consistentes (bot-like)
        response_times = [r.response_time for r in requests]
        if len(response_times) > 5:
            mean_time = sum(response_times) / len(response_times)
            variance = sum((t - mean_time) ** 2 for t in response_times) / len(response_times)
            
            # Tempos muito consistentes = suspeito
            if variance < 0.001:
                return 0.8
        
        return error_ratio
    
    def get_threat_level(self, ip: str, endpoint: str) -> ThreatLevel:
        """Obtém nível de ameaça para IP/endpoint."""
        key = f"{ip}:{endpoint}"
        score = self.anomaly_scores.get(key, 0.0)
        
        if score > 0.8:
            return ThreatLevel.CRITICAL
        elif score > 0.6:
            return ThreatLevel.HIGH
        elif score > 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

class AdaptiveRateLimiter:
    """Rate limiter adaptativo com detecção de padrões."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.cache = None
        self.pattern_detector = PatternDetector()
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_ips: Dict[str, float] = {}
        self.alert_history: Dict[str, float] = {}
        
        # Métricas
        self.metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'rate_limited_requests': 0,
            'anomalies_detected': 0,
            'alerts_sent': 0
        }
    
    async def _get_cache(self):
        """Obtém instância do cache."""
        if self.cache is None:
            self.cache = await get_cache("rate_limiting")
        return self.cache
    
    def _get_client_key(self, ip: str, user_id: Optional[str] = None) -> str:
        """Gera chave única para cliente."""
        if user_id:
            return f"rate_limit:{user_id}:{ip}"
        return f"rate_limit:anonymous:{ip}"
    
    def _is_whitelisted(self, ip: str) -> bool:
        """Verifica se IP está na whitelist."""
        return ip in self.config.whitelist_ips
    
    def _is_blacklisted(self, ip: str) -> bool:
        """Verifica se IP está na blacklist."""
        return ip in self.config.blacklist_ips
    
    def _is_blocked(self, ip: str) -> bool:
        """Verifica se IP está temporariamente bloqueado."""
        if ip in self.blocked_ips:
            block_until = self.blocked_ips[ip]
            if time.time() < block_until:
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    async def _get_rate_limit_data(self, key: str) -> Dict[str, Any]:
        """Obtém dados de rate limit do cache."""
        cache = await self._get_cache()
        data = await cache.get(key, {})
        
        if not isinstance(data, dict):
            return {}
        
        return data
    
    async def _set_rate_limit_data(self, key: str, data: Dict[str, Any], ttl: int = 3600):
        """Define dados de rate limit no cache."""
        cache = await self._get_cache()
        await cache.set(key, data, ttl)
    
    async def _check_rate_limit(self, key: str, strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifica rate limit para uma chave.
        
        Args:
            key: Chave do cliente
            strategy: Estratégia de rate limiting
            
        Returns:
            (allowed, info)
        """
        data = await self._get_rate_limit_data(key)
        now = time.time()
        
        # Inicializa dados se necessário
        if not data:
            data = {
                'requests': [],
                'last_reset': now,
                'current_window': 0,
                'tokens': self.config.burst_limit
            }
        
        # Remove requisições antigas
        window_start = now - self.config.window_size
        data['requests'] = [req for req in data['requests'] if req > window_start]
        
        # Adiciona requisição atual
        data['requests'].append(now)
        
        # Aplica estratégia
        if strategy == RateLimitStrategy.FIXED:
            allowed = len(data['requests']) <= self.config.requests_per_minute
        elif strategy == RateLimitStrategy.SLIDING_WINDOW:
            allowed = len(data['requests']) <= self.config.requests_per_minute
        elif strategy == RateLimitStrategy.TOKEN_BUCKET:
            # Implementação simplificada de token bucket
            tokens = data.get('tokens', self.config.burst_limit)
            if tokens > 0:
                data['tokens'] = tokens - 1
                allowed = True
            else:
                allowed = False
        else:  # ADAPTIVE
            allowed = len(data['requests']) <= self.config.requests_per_minute
        
        # Salva dados
        await self._set_rate_limit_data(key, data)
        
        info = {
            'remaining': max(0, self.config.requests_per_minute - len(data['requests'])),
            'reset_time': now + self.config.window_size,
            'current_count': len(data['requests'])
        }
        
        return allowed, info
    
    async def process_request(self, request: RequestInfo, user_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Processa uma requisição e aplica rate limiting.
        
        Args:
            request: Informações da requisição
            user_id: ID do usuário (opcional)
            
        Returns:
            (allowed, info)
        """
        self.metrics['total_requests'] += 1
        
        # Verificações básicas
        if self._is_whitelisted(request.ip):
            return True, {'whitelisted': True}
        
        if self._is_blacklisted(request.ip):
            self.metrics['blocked_requests'] += 1
            return False, {'blocked': True, 'reason': 'blacklisted'}
        
        if self._is_blocked(request.ip):
            self.metrics['blocked_requests'] += 1
            return False, {'blocked': True, 'reason': 'temporarily_blocked'}
        
        # Detecção de padrões
        anomaly_score = self.pattern_detector.add_request(request)
        threat_level = self.pattern_detector.get_threat_level(request.ip, request.endpoint)
        
        if anomaly_score > 0.5:
            self.metrics['anomalies_detected'] += 1
        
        # Rate limiting adaptativo
        key = self._get_client_key(request.ip, user_id)
        
        # Ajusta limites baseado no nível de ameaça
        if threat_level == ThreatLevel.CRITICAL:
            # Bloqueia temporariamente
            self.blocked_ips[request.ip] = time.time() + self.config.cooldown_period
            self.metrics['blocked_requests'] += 1
            
            logger.warning({
                "event": "ip_blocked_critical",
                "status": "warning",
                "source": "rate_limiting.process_request",
                "details": {
                    "ip": request.ip,
                    "threat_level": threat_level.value,
                    "anomaly_score": anomaly_score,
                    "block_duration": self.config.cooldown_period
                }
            })
            
            return False, {
                'blocked': True,
                'reason': 'critical_threat',
                'threat_level': threat_level.value,
                'anomaly_score': anomaly_score
            }
        
        elif threat_level == ThreatLevel.HIGH:
            # Rate limit muito restritivo
            original_limit = self.config.requests_per_minute
            self.config.requests_per_minute = max(5, original_limit // 10)
        
        elif threat_level == ThreatLevel.MEDIUM:
            # Rate limit moderado
            original_limit = self.config.requests_per_minute
            self.config.requests_per_minute = max(10, original_limit // 5)
        
        # Verifica rate limit
        allowed, info = await self._check_rate_limit(key)
        
        if not allowed:
            self.metrics['rate_limited_requests'] += 1
            
            # Envia alerta se necessário
            await self._send_alert(request, threat_level, anomaly_score)
        
        # Restaura limite original se foi alterado
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.MEDIUM]:
            self.config.requests_per_minute = 60  # Valor padrão
        
        # Adiciona informações extras
        info.update({
            'threat_level': threat_level.value,
            'anomaly_score': anomaly_score,
            'ip': request.ip,
            'endpoint': request.endpoint
        })
        
        return allowed, info
    
    async def _send_alert(self, request: RequestInfo, threat_level: ThreatLevel, anomaly_score: float):
        """Envia alerta sobre atividade suspeita."""
        alert_key = f"alert:{request.ip}"
        now = time.time()
        
        # Evita spam de alertas
        if alert_key in self.alert_history:
            last_alert = self.alert_history[alert_key]
            if now - last_alert < self.config.alert_cooldown:
                return
        
        self.alert_history[alert_key] = now
        self.metrics['alerts_sent'] += 1
        
        logger.warning({
            "event": "rate_limit_alert",
            "status": "warning",
            "source": "rate_limiting._send_alert",
            "details": {
                "ip": request.ip,
                "threat_level": threat_level.value,
                "anomaly_score": anomaly_score,
                "endpoint": request.endpoint,
                "user_agent": request.user_agent
            }
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do rate limiter."""
        total = self.metrics['total_requests']
        
        return {
            **self.metrics,
            'block_rate': (self.metrics['blocked_requests'] / total * 100) if total > 0 else 0,
            'rate_limit_rate': (self.metrics['rate_limited_requests'] / total * 100) if total > 0 else 0,
            'anomaly_rate': (self.metrics['anomalies_detected'] / total * 100) if total > 0 else 0,
            'blocked_ips_count': len(self.blocked_ips),
            'alert_rate': (self.metrics['alerts_sent'] / total * 100) if total > 0 else 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do rate limiter."""
        try:
            cache = await self._get_cache()
            cache_health = await cache.health_check()
            
            return {
                'rate_limiter_healthy': True,
                'cache_healthy': cache_health.get('overall_healthy', False),
                'pattern_detector_healthy': True,
                'blocked_ips_count': len(self.blocked_ips),
                'metrics': self.get_metrics()
            }
        except Exception as e:
            return {
                'rate_limiter_healthy': False,
                'error': str(e)
            }

# Instância global
_rate_limiter: Optional[AdaptiveRateLimiter] = None

async def get_rate_limiter() -> AdaptiveRateLimiter:
    """Obtém instância global do rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = AdaptiveRateLimiter()
    return _rate_limiter

# Decorator para rate limiting automático
def rate_limited(requests_per_minute: int = 60, strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE):
    """
    Decorator para rate limiting automático.
    
    Args:
        requests_per_minute: Limite de requisições por minuto
        strategy: Estratégia de rate limiting
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extrai informações da requisição (assumindo Flask/FastAPI)
            request_info = RequestInfo(
                timestamp=time.time(),
                ip="127.0.0.1",  # Será extraído da requisição real
                user_agent="",
                endpoint=func.__name__,
                method="GET",
                response_time=0.0,
                status_code=200
            )
            
            # Aplica rate limiting
            rate_limiter = await get_rate_limiter()
            allowed, info = await rate_limiter.process_request(request_info)
            
            if not allowed:
                raise Exception(f"Rate limit exceeded: {info}")
            
            # Executa função
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator 