"""
Sistema de Rate Limiting Inteligente - Omni Keywords Finder
Tracing ID: RATE_LIMITING_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa rate limiting avançado com:
- Algoritmo sliding window
- Detecção de padrões anômalos
- Rate limiting adaptativo
- Integração com Redis
- Quotas dinâmicas
- Fallback inteligente
"""

import time
import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import threading

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis não disponível. Rate limiting será limitado à memória local.")

try:
    from infrastructure.observability.telemetry import get_telemetry_manager
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logging.warning("Telemetria não disponível. Métricas de rate limiting serão limitadas.")


class RateLimitStrategy(Enum):
    """Estratégias de rate limiting."""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class AnomalyType(Enum):
    """Tipos de anomalias detectadas."""
    BURST_TRAFFIC = "burst_traffic"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    TIME_ANOMALY = "time_anomaly"
    USER_BEHAVIOR_ANOMALY = "user_behavior_anomaly"


@dataclass
class RateLimitConfig:
    """Configuração de rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    window_size: int = 60  # segundos
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    enable_anomaly_detection: bool = True
    anomaly_threshold: float = 2.0
    adaptive_learning: bool = True
    fallback_enabled: bool = True
    redis_ttl: int = 3600  # 1 hora


@dataclass
class RateLimitResult:
    """Resultado da verificação de rate limiting."""
    allowed: bool
    remaining_requests: int
    reset_time: int
    retry_after: Optional[int] = None
    anomaly_detected: bool = False
    anomaly_type: Optional[AnomalyType] = None
    adaptive_adjustment: Optional[float] = None
    reason: Optional[str] = None


@dataclass
class AnomalyData:
    """Dados de anomalia detectada."""
    anomaly_type: AnomalyType
    severity: float
    timestamp: float
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    endpoint: Optional[str] = None
    pattern_data: Dict[str, Any] = None


class AnomalyDetector:
    """
    Detector de anomalias para rate limiting inteligente.
    """
    
    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold
        self.patterns = defaultdict(list)
        self.user_profiles = defaultdict(dict)
        self.geographic_patterns = defaultdict(list)
        self.time_patterns = defaultdict(list)
        
    def detect_burst_traffic(self, user_id: str, request_count: int, 
                           time_window: int) -> Optional[AnomalyData]:
        """
        Detecta tráfego em burst.
        
        Args:
            user_id: ID do usuário
            request_count: Número de requisições
            time_window: Janela de tempo em segundos
            
        Returns:
            Dados da anomalia se detectada
        """
        # Calcular taxa de requisições por segundo
        requests_per_second = request_count / time_window
        
        # Verificar se excede o threshold
        if requests_per_second > self.threshold:
            return AnomalyData(
                anomaly_type=AnomalyType.BURST_TRAFFIC,
                severity=requests_per_second / self.threshold,
                timestamp=time.time(),
                user_id=user_id,
                pattern_data={
                    "requests_per_second": requests_per_second,
                    "time_window": time_window,
                    "threshold": self.threshold
                }
            )
        return None
    
    def detect_suspicious_pattern(self, user_id: str, endpoint: str, 
                                request_data: Dict[str, Any]) -> Optional[AnomalyData]:
        """
        Detecta padrões suspeitos de requisições.
        
        Args:
            user_id: ID do usuário
            endpoint: Endpoint acessado
            request_data: Dados da requisição
            
        Returns:
            Dados da anomalia se detectada
        """
        # Verificar padrões conhecidos de ataque
        suspicious_patterns = [
            "sql_injection",
            "xss_attack",
            "path_traversal",
            "command_injection"
        ]
        
        # Analisar dados da requisição
        request_string = json.dumps(request_data, sort_keys=True).lower()
        
        for pattern in suspicious_patterns:
            if pattern in request_string:
                return AnomalyData(
                    anomaly_type=AnomalyType.SUSPICIOUS_PATTERN,
                    severity=3.0,  # Alta severidade
                    timestamp=time.time(),
                    user_id=user_id,
                    endpoint=endpoint,
                    pattern_data={
                        "detected_pattern": pattern,
                        "request_data": request_data
                    }
                )
        return None
    
    def detect_geographic_anomaly(self, user_id: str, ip_address: str, 
                                country: str, city: str) -> Optional[AnomalyData]:
        """
        Detecta anomalias geográficas.
        
        Args:
            user_id: ID do usuário
            ip_address: Endereço IP
            country: País
            city: Cidade
            
        Returns:
            Dados da anomalia se detectada
        """
        # Verificar se o usuário já tem perfil geográfico
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            
            if "usual_country" in profile and profile["usual_country"] != country:
                return AnomalyData(
                    anomaly_type=AnomalyType.GEOGRAPHIC_ANOMALY,
                    severity=2.0,
                    timestamp=time.time(),
                    user_id=user_id,
                    ip_address=ip_address,
                    pattern_data={
                        "usual_country": profile["usual_country"],
                        "current_country": country,
                        "usual_city": profile.get("usual_city"),
                        "current_city": city
                    }
                )
        
        # Atualizar perfil do usuário
        self.user_profiles[user_id] = {
            "usual_country": country,
            "usual_city": city,
            "last_update": time.time()
        }
        
        return None
    
    def detect_time_anomaly(self, user_id: str, timestamp: float) -> Optional[AnomalyData]:
        """
        Detecta anomalias de tempo.
        
        Args:
            user_id: ID do usuário
            timestamp: Timestamp da requisição
            
        Returns:
            Dados da anomalia se detectada
        """
        current_hour = time.localtime(timestamp).tm_hour
        
        # Verificar se é horário incomum para o usuário
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            
            if "usual_hours" in profile:
                usual_hours = profile["usual_hours"]
                if current_hour not in usual_hours:
                    return AnomalyData(
                        anomaly_type=AnomalyType.TIME_ANOMALY,
                        severity=1.5,
                        timestamp=timestamp,
                        user_id=user_id,
                        pattern_data={
                            "current_hour": current_hour,
                            "usual_hours": usual_hours
                        }
                    )
        
        # Atualizar perfil de horários
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        
        if "usual_hours" not in self.user_profiles[user_id]:
            self.user_profiles[user_id]["usual_hours"] = []
        
        if current_hour not in self.user_profiles[user_id]["usual_hours"]:
            self.user_profiles[user_id]["usual_hours"].append(current_hour)
        
        return None


class AdaptiveRateLimiter:
    """
    Rate limiter adaptativo que ajusta limites baseado em comportamento.
    """
    
    def __init__(self, base_config: RateLimitConfig):
        self.base_config = base_config
        self.user_behavior = defaultdict(dict)
        self.learning_rate = 0.1
        self.min_adjustment = 0.5
        self.max_adjustment = 2.0
        
    def calculate_adaptive_limit(self, user_id: str, current_usage: float) -> float:
        """
        Calcula limite adaptativo baseado no comportamento do usuário.
        
        Args:
            user_id: ID do usuário
            current_usage: Uso atual (0.0 a 1.0)
            
        Returns:
            Fator de ajuste do limite
        """
        if user_id not in self.user_behavior:
            self.user_behavior[user_id] = {
                "usage_history": [],
                "adjustment_factor": 1.0,
                "last_update": time.time()
            }
        
        behavior = self.user_behavior[user_id]
        behavior["usage_history"].append(current_usage)
        
        # Manter apenas os últimos 100 registros
        if len(behavior["usage_history"]) > 100:
            behavior["usage_history"] = behavior["usage_history"][-100:]
        
        # Calcular uso médio
        avg_usage = sum(behavior["usage_history"]) / len(behavior["usage_history"])
        
        # Ajustar limite baseado no uso médio
        if avg_usage < 0.3:  # Usuário conservador
            adjustment = 1.0 + self.learning_rate
        elif avg_usage > 0.8:  # Usuário agressivo
            adjustment = 1.0 - self.learning_rate
        else:  # Usuário normal
            adjustment = 1.0
        
        # Aplicar limites mínimo e máximo
        adjustment = max(self.min_adjustment, min(self.max_adjustment, adjustment))
        
        # Atualizar fator de ajuste
        behavior["adjustment_factor"] = adjustment
        behavior["last_update"] = time.time()
        
        return adjustment


class RateLimitingInteligente:
    """
    Sistema de rate limiting inteligente com detecção de anomalias
    e ajuste adaptativo de limites.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.redis_client = None
        self.anomaly_detector = AnomalyDetector(self.config.anomaly_threshold)
        self.adaptive_limiter = AdaptiveRateLimiter(self.config)
        self.request_history = defaultdict(list)
        self.blocked_ips = set()
        self.whitelist_ips = set()
        self._lock = threading.RLock()
        
        # Inicializar Redis se disponível
        if REDIS_AVAILABLE:
            self._setup_redis()
        
        # Inicializar telemetria se disponível
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry_manager()
        else:
            self.telemetry = None
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_redis(self) -> None:
        """Configura conexão com Redis."""
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_db = int(os.getenv("REDIS_DB", "0"))
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Testar conexão
            self.redis_client.ping()
            self.logger.info("Redis conectado para rate limiting")
            
        except Exception as e:
            self.logger.warning(f"Redis não disponível: {e}")
            self.redis_client = None
    
    def _get_cache_key(self, identifier: str, window: str) -> str:
        """
        Gera chave de cache para Redis.
        
        Args:
            identifier: Identificador (IP, user_id, etc.)
            window: Janela de tempo (minute, hour, day)
            
        Returns:
            Chave de cache
        """
        return f"rate_limit:{identifier}:{window}:{int(time.time() // 60)}"
    
    def _get_redis_data(self, key: str) -> Dict[str, Any]:
        """
        Obtém dados do Redis.
        
        Args:
            key: Chave do Redis
            
        Returns:
            Dados armazenados
        """
        if not self.redis_client:
            return {}
        
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            self.logger.error(f"Erro ao ler do Redis: {e}")
        
        return {}
    
    def _set_redis_data(self, key: str, data: Dict[str, Any], ttl: int = None) -> None:
        """
        Armazena dados no Redis.
        
        Args:
            key: Chave do Redis
            data: Dados para armazenar
            ttl: Time to live em segundos
        """
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or self.config.redis_ttl
            self.redis_client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            self.logger.error(f"Erro ao escrever no Redis: {e}")
    
    def _sliding_window_count(self, identifier: str, window_seconds: int) -> int:
        """
        Conta requisições usando sliding window.
        
        Args:
            identifier: Identificador
            window_seconds: Tamanho da janela em segundos
            
        Returns:
            Número de requisições na janela
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Limpar requisições antigas
        self.request_history[identifier] = [
            req_time for req_time in self.request_history[identifier]
            if req_time > window_start
        ]
        
        return len(self.request_history[identifier])
    
    def _check_rate_limit(self, identifier: str, limit: int, 
                         window_seconds: int) -> Tuple[bool, int]:
        """
        Verifica se o rate limit foi excedido.
        
        Args:
            identifier: Identificador
            limit: Limite de requisições
            window_seconds: Janela de tempo
            
        Returns:
            Tuple (permitido, requisições restantes)
        """
        current_count = self._sliding_window_count(identifier, window_seconds)
        remaining = max(0, limit - current_count)
        allowed = current_count < limit
        
        return allowed, remaining
    
    def _detect_anomalies(self, user_id: str, ip_address: str, 
                         endpoint: str, request_data: Dict[str, Any]) -> List[AnomalyData]:
        """
        Detecta anomalias na requisição.
        
        Args:
            user_id: ID do usuário
            ip_address: Endereço IP
            endpoint: Endpoint acessado
            request_data: Dados da requisição
            
        Returns:
            Lista de anomalias detectadas
        """
        anomalies = []
        
        # Detectar burst traffic
        burst_anomaly = self.anomaly_detector.detect_burst_traffic(
            user_id, 1, 1  # 1 requisição em 1 segundo
        )
        if burst_anomaly:
            anomalies.append(burst_anomaly)
        
        # Detectar padrões suspeitos
        suspicious_anomaly = self.anomaly_detector.detect_suspicious_pattern(
            user_id, endpoint, request_data
        )
        if suspicious_anomaly:
            anomalies.append(suspicious_anomaly)
        
        # Detectar anomalias geográficas (se dados disponíveis)
        if "country" in request_data and "city" in request_data:
            geo_anomaly = self.anomaly_detector.detect_geographic_anomaly(
                user_id, ip_address, request_data["country"], request_data["city"]
            )
            if geo_anomaly:
                anomalies.append(geo_anomaly)
        
        # Detectar anomalias de tempo
        time_anomaly = self.anomaly_detector.detect_time_anomaly(
            user_id, time.time()
        )
        if time_anomaly:
            anomalies.append(time_anomaly)
        
        return anomalies
    
    def check_rate_limit(self, identifier: str, user_id: Optional[str] = None,
                        ip_address: Optional[str] = None, endpoint: Optional[str] = None,
                        request_data: Optional[Dict[str, Any]] = None) -> RateLimitResult:
        """
        Verifica rate limit para um identificador.
        
        Args:
            identifier: Identificador único (IP, user_id, etc.)
            user_id: ID do usuário (opcional)
            ip_address: Endereço IP (opcional)
            endpoint: Endpoint acessado (opcional)
            request_data: Dados da requisição (opcional)
            
        Returns:
            Resultado da verificação de rate limit
        """
        with self._lock:
            # Verificar whitelist
            if ip_address and ip_address in self.whitelist_ips:
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=999999,
                    reset_time=int(time.time() + 3600),
                    reason="IP na whitelist"
                )
            
            # Verificar blacklist
            if ip_address and ip_address in self.blocked_ips:
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=int(time.time() + 3600),
                    retry_after=3600,
                    reason="IP bloqueado"
                )
            
            # Detectar anomalias
            anomalies = []
            if self.config.enable_anomaly_detection and user_id and ip_address:
                anomalies = self._detect_anomalies(
                    user_id, ip_address, endpoint or "", request_data or {}
                )
            
            # Aplicar ajustes adaptativos
            adaptive_factor = 1.0
            if self.config.adaptive_learning and user_id:
                adaptive_factor = self.adaptive_limiter.calculate_adaptive_limit(
                    user_id, 0.5  # Uso médio estimado
                )
            
            # Verificar limites por janela de tempo
            current_time = time.time()
            
            # Limite por minuto
            minute_allowed, minute_remaining = self._check_rate_limit(
                f"{identifier}:minute",
                int(self.config.requests_per_minute * adaptive_factor),
                60
            )
            
            # Limite por hora
            hour_allowed, hour_remaining = self._check_rate_limit(
                f"{identifier}:hour",
                int(self.config.requests_per_hour * adaptive_factor),
                3600
            )
            
            # Limite por dia
            day_allowed, day_remaining = self._check_rate_limit(
                f"{identifier}:day",
                int(self.config.requests_per_day * adaptive_factor),
                86400
            )
            
            # Determinar se a requisição é permitida
            allowed = minute_allowed and hour_allowed and day_allowed
            
            # Registrar requisição se permitida
            if allowed:
                self.request_history[f"{identifier}:minute"].append(current_time)
                self.request_history[f"{identifier}:hour"].append(current_time)
                self.request_history[f"{identifier}:day"].append(current_time)
            
            # Calcular tempo de reset
            reset_time = int(current_time + 60)  # Reset em 1 minuto
            
            # Calcular retry_after se bloqueado
            retry_after = None
            if not allowed:
                if not minute_allowed:
                    retry_after = 60
                elif not hour_allowed:
                    retry_after = 3600
                elif not day_allowed:
                    retry_after = 86400
            
            # Registrar métricas
            if self.telemetry:
                self.telemetry.record_metric(
                    "rate_limit_requests_total",
                    1,
                    {"identifier": identifier, "allowed": str(allowed)}
                )
                
                if anomalies:
                    self.telemetry.record_metric(
                        "rate_limit_anomalies_total",
                        len(anomalies),
                        {"identifier": identifier}
                    )
            
            return RateLimitResult(
                allowed=allowed,
                remaining_requests=min(minute_remaining, hour_remaining, day_remaining),
                reset_time=reset_time,
                retry_after=retry_after,
                anomaly_detected=len(anomalies) > 0,
                anomaly_type=anomalies[0].anomaly_type if anomalies else None,
                adaptive_adjustment=adaptive_factor,
                reason="Rate limit excedido" if not allowed else None
            )
    
    def add_to_whitelist(self, ip_address: str) -> None:
        """Adiciona IP à whitelist."""
        with self._lock:
            self.whitelist_ips.add(ip_address)
            self.logger.info(f"IP {ip_address} adicionado à whitelist")
    
    def remove_from_whitelist(self, ip_address: str) -> None:
        """Remove IP da whitelist."""
        with self._lock:
            self.whitelist_ips.discard(ip_address)
            self.logger.info(f"IP {ip_address} removido da whitelist")
    
    def add_to_blacklist(self, ip_address: str, duration: int = 3600) -> None:
        """Adiciona IP à blacklist."""
        with self._lock:
            self.blocked_ips.add(ip_address)
            self.logger.warning(f"IP {ip_address} adicionado à blacklist por {duration}string_data")
            
            # Remover automaticamente após o tempo especificado
            if duration > 0:
                threading.Timer(duration, lambda: self.remove_from_blacklist(ip_address)).start()
    
    def remove_from_blacklist(self, ip_address: str) -> None:
        """Remove IP da blacklist."""
        with self._lock:
            self.blocked_ips.discard(ip_address)
            self.logger.info(f"IP {ip_address} removido da blacklist")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do rate limiting.
        
        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            return {
                "total_identifiers": len(self.request_history),
                "whitelisted_ips": len(self.whitelist_ips),
                "blocked_ips": len(self.blocked_ips),
                "anomaly_detection_enabled": self.config.enable_anomaly_detection,
                "adaptive_learning_enabled": self.config.adaptive_learning,
                "redis_available": self.redis_client is not None,
                "telemetry_available": self.telemetry is not None
            }
    
    def reset_limits(self, identifier: str) -> None:
        """
        Reseta limites para um identificador.
        
        Args:
            identifier: Identificador para resetar
        """
        with self._lock:
            for key in list(self.request_history.keys()):
                if key.startswith(identifier):
                    del self.request_history[key]
            
            self.logger.info(f"Limites resetados para {identifier}")


# Instância global do rate limiter
rate_limiter = RateLimitingInteligente()


def get_rate_limiter() -> RateLimitingInteligente:
    """Retorna a instância global do rate limiter."""
    return rate_limiter


def initialize_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimitingInteligente:
    """
    Inicializa e retorna o sistema de rate limiting.
    
    Args:
        config: Configuração do rate limiting
        
    Returns:
        Instância configurada do RateLimitingInteligente
    """
    global rate_limiter
    rate_limiter = RateLimitingInteligente(config)
    return rate_limiter


# Decorador para rate limiting automático
def rate_limited(identifier_key: str = "ip_address", 
                user_id_key: str = "user_id",
                endpoint_key: str = "endpoint"):
    """
    Decorador para aplicar rate limiting automaticamente.
    
    Args:
        identifier_key: Chave para identificar o usuário/IP
        user_id_key: Chave para ID do usuário
        endpoint_key: Chave para endpoint
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extrair informações da requisição
            request = kwargs.get('request') or args[0] if args else None
            
            if not request:
                return func(*args, **kwargs)
            
            # Obter identificador
            identifier = getattr(request, identifier_key, None)
            if not identifier:
                identifier = request.remote_addr
            
            # Obter informações adicionais
            user_id = getattr(request, user_id_key, None)
            endpoint = getattr(request, endpoint_key, None) or request.path
            ip_address = request.remote_addr
            
            # Verificar rate limit
            result = rate_limiter.check_rate_limit(
                identifier=identifier,
                user_id=user_id,
                ip_address=ip_address,
                endpoint=endpoint,
                request_data=request.get_json() if hasattr(request, 'get_json') else {}
            )
            
            if not result.allowed:
                # Retornar erro 429 (Too Many Requests)
                from flask import jsonify
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": result.retry_after,
                    "reason": result.reason
                }), 429, {
                    "X-RateLimit-Remaining": result.remaining_requests,
                    "X-RateLimit-Reset": result.reset_time,
                    "Retry-After": result.retry_after or 60
                }
            
            # Adicionar headers de rate limit
            response = func(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Remaining"] = result.remaining_requests
                response.headers["X-RateLimit-Reset"] = result.reset_time
            
            return response
        
        return wrapper
    return decorator 