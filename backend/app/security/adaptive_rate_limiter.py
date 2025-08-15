"""
Adaptive Rate Limiter - Omni Keywords Finder
Tracing ID: ADAPTIVE_RATE_LIMITER_20250127_001

Sistema de rate limiting adaptativo com limites dinâmicos baseados em padrões de uso,
comportamento do usuário e carga do sistema.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import hashlib
import ipaddress

from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
import redis
import psutil

# Configuração de logging
logger = logging.getLogger(__name__)

class RateLimitStatus(Enum):
    """Status do rate limiting"""
    ALLOWED = "allowed"
    LIMITED = "limited"
    BLOCKED = "blocked"
    WHITELISTED = "whitelisted"

@dataclass
class RateLimitConfig:
    """Configuração de rate limiting"""
    base_limit: int  # Limite base por minuto
    burst_limit: int  # Limite de burst
    window_size: int  # Janela de tempo em segundos
    adaptive_factor: float  # Fator de adaptação (0.5-2.0)
    whitelist_ips: List[str] = field(default_factory=list)
    blacklist_ips: List[str] = field(default_factory=list)

@dataclass
class RateLimitMetrics:
    """Métricas de rate limiting"""
    identifier: str
    requests_count: int
    limit: int
    remaining: int
    reset_time: float
    status: RateLimitStatus
    response_time: float
    timestamp: float

class AdaptiveRateLimiter:
    """
    Rate limiter adaptativo com limites dinâmicos baseados em comportamento
    e carga do sistema
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_config: Optional[RateLimitConfig] = None,
        enable_learning: bool = True,
        learning_window: int = 3600,  # 1 hora
        max_adaptive_factor: float = 2.0,
        min_adaptive_factor: float = 0.5
    ):
        self.redis_url = redis_url
        self.enable_learning = enable_learning
        self.learning_window = learning_window
        self.max_adaptive_factor = max_adaptive_factor
        self.min_adaptive_factor = min_adaptive_factor
        
        # Configuração padrão
        self.default_config = default_config or RateLimitConfig(
            base_limit=100,
            burst_limit=200,
            window_size=60,
            adaptive_factor=1.0
        )
        
        # Configurações por usuário/tipo
        self.user_configs: Dict[str, RateLimitConfig] = {}
        self.ip_configs: Dict[str, RateLimitConfig] = {}
        
        # Estado do sistema
        self.is_running = False
        self.request_history: deque = deque(maxlen=10000)
        self.learning_data: Dict[str, Any] = defaultdict(dict)
        
        # Threading
        self._lock = threading.RLock()
        self._learning_thread = None
        self._stop_event = threading.Event()
        
        # Redis connection
        self._redis_client = None
        self._setup_redis()
        
        # Callbacks
        self._limit_exceeded_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self._learning_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        logger.info("Adaptive rate limiter initialized")
    
    def _setup_redis(self):
        """Configura conexão com Redis"""
        try:
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Testar conexão
            self._redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory storage: {e}")
            self._redis_client = None
    
    def add_limit_exceeded_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Adiciona callback para quando limite é excedido"""
        self._limit_exceeded_callbacks.append(callback)
    
    def add_learning_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Adiciona callback para eventos de aprendizado"""
        self._learning_callbacks.append(callback)
    
    def start_learning(self):
        """Inicia processo de aprendizado"""
        if self.is_running:
            logger.warning("Learning already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        self._learning_thread = threading.Thread(
            target=self._learning_loop,
            daemon=True,
            name="RateLimiterLearning"
        )
        self._learning_thread.start()
        
        logger.info("Rate limiter learning started")
    
    def stop_learning(self):
        """Para processo de aprendizado"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._learning_thread:
            self._learning_thread.join(timeout=5)
        
        logger.info("Rate limiter learning stopped")
    
    def _learning_loop(self):
        """Loop principal de aprendizado"""
        while not self._stop_event.is_set():
            try:
                # Analisar padrões de uso
                patterns = self._analyze_usage_patterns()
                
                # Ajustar configurações
                self._adjust_configurations(patterns)
                
                # Notificar callbacks
                self._notify_learning_callbacks(patterns)
                
                # Aguardar próximo ciclo
                self._stop_event.wait(self.learning_window)
                
            except Exception as e:
                logger.error(f"Error in learning loop: {e}")
                self._stop_event.wait(60)  # Aguardar 1 minuto em caso de erro
    
    def _analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de uso para adaptação"""
        try:
            with self._lock:
                if not self.request_history:
                    return {}
                
                # Agrupar por identificador
                usage_by_identifier = defaultdict(list)
                for request in self.request_history:
                    usage_by_identifier[request['identifier']].append(request)
                
                patterns = {}
                for identifier, requests in usage_by_identifier.items():
                    # Calcular métricas
                    total_requests = len(requests)
                    avg_response_time = sum(r['response_time'] for r in requests) / total_requests
                    error_rate = sum(1 for r in requests if r.get('status_code', 200) >= 400) / total_requests
                    
                    # Analisar padrão temporal
                    timestamps = [r['timestamp'] for r in requests]
                    time_distribution = self._analyze_time_distribution(timestamps)
                    
                    # Determinar tipo de usuário
                    user_type = self._classify_user_type(requests)
                    
                    patterns[identifier] = {
                        'total_requests': total_requests,
                        'avg_response_time': avg_response_time,
                        'error_rate': error_rate,
                        'time_distribution': time_distribution,
                        'user_type': user_type,
                        'recommended_limit': self._calculate_recommended_limit(
                            total_requests, avg_response_time, error_rate, user_type
                        )
                    }
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
            return {}
    
    def _analyze_time_distribution(self, timestamps: List[float]) -> Dict[str, Any]:
        """Analisa distribuição temporal das requisições"""
        if not timestamps:
            return {}
        
        # Converter para horas do dia
        hours = [time.localtime(ts).tm_hour for ts in timestamps]
        
        # Calcular distribuição
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        # Encontrar picos
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_requests': len(timestamps),
            'peak_hours': peak_hours,
            'hourly_distribution': dict(hour_counts)
        }
    
    def _classify_user_type(self, requests: List[Dict[str, Any]]) -> str:
        """Classifica tipo de usuário baseado no comportamento"""
        if not requests:
            return 'unknown'
        
        # Analisar padrões
        total_requests = len(requests)
        avg_interval = 0
        
        if total_requests > 1:
            timestamps = sorted([r['timestamp'] for r in requests])
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_interval = sum(intervals) / len(intervals)
        
        # Classificar baseado em padrões
        if total_requests > 1000 and avg_interval < 1:
            return 'bot'
        elif total_requests > 500 and avg_interval < 5:
            return 'power_user'
        elif total_requests > 100:
            return 'active_user'
        elif total_requests > 10:
            return 'regular_user'
        else:
            return 'casual_user'
    
    def _calculate_recommended_limit(
        self, 
        total_requests: int, 
        avg_response_time: float, 
        error_rate: float, 
        user_type: str
    ) -> int:
        """Calcula limite recomendado baseado em métricas"""
        base_limit = self.default_config.base_limit
        
        # Ajustar baseado no tipo de usuário
        user_multipliers = {
            'bot': 0.1,
            'power_user': 2.0,
            'active_user': 1.5,
            'regular_user': 1.0,
            'casual_user': 0.8
        }
        
        multiplier = user_multipliers.get(user_type, 1.0)
        
        # Ajustar baseado na performance
        if avg_response_time > 1.0:  # Lento
            multiplier *= 0.8
        elif avg_response_time < 0.1:  # Rápido
            multiplier *= 1.2
        
        # Ajustar baseado na taxa de erro
        if error_rate > 0.1:  # Muitos erros
            multiplier *= 0.7
        elif error_rate < 0.01:  # Poucos erros
            multiplier *= 1.1
        
        # Aplicar limites
        recommended = int(base_limit * multiplier)
        recommended = max(recommended, int(base_limit * self.min_adaptive_factor))
        recommended = min(recommended, int(base_limit * self.max_adaptive_factor))
        
        return recommended
    
    def _adjust_configurations(self, patterns: Dict[str, Any]):
        """Ajusta configurações baseado nos padrões aprendidos"""
        try:
            for identifier, pattern in patterns.items():
                recommended_limit = pattern['recommended_limit']
                current_config = self._get_config_for_identifier(identifier)
                
                # Calcular novo fator adaptativo
                new_factor = recommended_limit / self.default_config.base_limit
                new_factor = max(new_factor, self.min_adaptive_factor)
                new_factor = min(new_factor, self.max_adaptive_factor)
                
                # Atualizar configuração
                new_config = RateLimitConfig(
                    base_limit=recommended_limit,
                    burst_limit=int(recommended_limit * 2),
                    window_size=current_config.window_size,
                    adaptive_factor=new_factor,
                    whitelist_ips=current_config.whitelist_ips,
                    blacklist_ips=current_config.blacklist_ips
                )
                
                self._set_config_for_identifier(identifier, new_config)
                
                logger.info(f"Updated rate limit for {identifier}: {current_config.base_limit} -> {recommended_limit}")
                
        except Exception as e:
            logger.error(f"Error adjusting configurations: {e}")
    
    def _get_config_for_identifier(self, identifier: str) -> RateLimitConfig:
        """Obtém configuração para um identificador"""
        # Verificar se é IP
        if self._is_ip_address(identifier):
            return self.ip_configs.get(identifier, self.default_config)
        else:
            return self.user_configs.get(identifier, self.default_config)
    
    def _set_config_for_identifier(self, identifier: str, config: RateLimitConfig):
        """Define configuração para um identificador"""
        if self._is_ip_address(identifier):
            self.ip_configs[identifier] = config
        else:
            self.user_configs[identifier] = config
    
    def _is_ip_address(self, identifier: str) -> bool:
        """Verifica se o identificador é um endereço IP"""
        try:
            ipaddress.ip_address(identifier)
            return True
        except ValueError:
            return False
    
    def _notify_learning_callbacks(self, patterns: Dict[str, Any]):
        """Notifica callbacks de aprendizado"""
        for callback in self._learning_callbacks:
            try:
                callback(patterns)
            except Exception as e:
                logger.error(f"Error in learning callback: {e}")
    
    async def check_rate_limit(
        self, 
        request: Request, 
        identifier: Optional[str] = None
    ) -> RateLimitMetrics:
        """Verifica rate limit para uma requisição"""
        try:
            # Determinar identificador
            if identifier is None:
                identifier = self._extract_identifier(request)
            
            # Obter configuração
            config = self._get_config_for_identifier(identifier)
            
            # Verificar whitelist/blacklist
            if identifier in config.whitelist_ips:
                return RateLimitMetrics(
                    identifier=identifier,
                    requests_count=0,
                    limit=config.base_limit,
                    remaining=config.base_limit,
                    reset_time=time.time() + config.window_size,
                    status=RateLimitStatus.WHITELISTED,
                    response_time=0.0,
                    timestamp=time.time()
                )
            
            if identifier in config.blacklist_ips:
                raise HTTPException(status_code=403, detail="IP blocked")
            
            # Verificar rate limit
            current_time = time.time()
            window_start = current_time - config.window_size
            
            # Contar requisições na janela
            request_count = await self._count_requests_in_window(
                identifier, window_start, current_time
            )
            
            # Calcular limite adaptativo
            adaptive_limit = int(config.base_limit * config.adaptive_factor)
            
            # Verificar se excedeu o limite
            if request_count >= adaptive_limit:
                # Verificar burst allowance
                if request_count < config.burst_limit:
                    status = RateLimitStatus.LIMITED
                else:
                    status = RateLimitStatus.BLOCKED
                
                # Notificar callbacks
                self._notify_limit_exceeded_callbacks(identifier, {
                    'request_count': request_count,
                    'limit': adaptive_limit,
                    'burst_limit': config.burst_limit,
                    'status': status.value
                })
                
                if status == RateLimitStatus.BLOCKED:
                    raise HTTPException(
                        status_code=429, 
                        detail=f"Rate limit exceeded: {request_count}/{adaptive_limit}"
                    )
            else:
                status = RateLimitStatus.ALLOWED
            
            # Registrar requisição
            await self._record_request(identifier, current_time)
            
            # Registrar no histórico para aprendizado
            if self.enable_learning:
                self._record_for_learning(request, identifier, status)
            
            return RateLimitMetrics(
                identifier=identifier,
                requests_count=request_count,
                limit=adaptive_limit,
                remaining=max(0, adaptive_limit - request_count),
                reset_time=current_time + config.window_size,
                status=status,
                response_time=0.0,  # Será atualizado após processamento
                timestamp=current_time
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Em caso de erro, permitir a requisição
            return RateLimitMetrics(
                identifier=identifier or "unknown",
                requests_count=0,
                limit=100,
                remaining=100,
                reset_time=time.time() + 60,
                status=RateLimitStatus.ALLOWED,
                response_time=0.0,
                timestamp=time.time()
            )
    
    def _extract_identifier(self, request: Request) -> str:
        """Extrai identificador da requisição"""
        # Priorizar IP real
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Usar IP do cliente
        client_ip = request.client.host
        if client_ip:
            return client_ip
        
        # Fallback
        return "unknown"
    
    async def _count_requests_in_window(
        self, 
        identifier: str, 
        window_start: float, 
        window_end: float
    ) -> int:
        """Conta requisições em uma janela de tempo"""
        try:
            if self._redis_client:
                # Usar Redis para contagem
                key = f"rate_limit:{identifier}:{int(window_start)}"
                count = self._redis_client.zcount(key, window_start, window_end)
                return count
            else:
                # Contagem em memória (fallback)
                with self._lock:
                    count = sum(
                        1 for req in self.request_history
                        if req['identifier'] == identifier and 
                        window_start <= req['timestamp'] <= window_end
                    )
                    return count
                    
        except Exception as e:
            logger.error(f"Error counting requests: {e}")
            return 0
    
    async def _record_request(self, identifier: str, timestamp: float):
        """Registra uma requisição"""
        try:
            if self._redis_client:
                # Registrar no Redis
                key = f"rate_limit:{identifier}:{int(timestamp)}"
                self._redis_client.zadd(key, {str(timestamp): timestamp})
                self._redis_client.expire(key, 3600)  # Expirar em 1 hora
            else:
                # Registrar em memória
                with self._lock:
                    self.request_history.append({
                        'identifier': identifier,
                        'timestamp': timestamp
                    })
                    
        except Exception as e:
            logger.error(f"Error recording request: {e}")
    
    def _record_for_learning(self, request: Request, identifier: str, status: RateLimitStatus):
        """Registra dados para aprendizado"""
        try:
            with self._lock:
                self.request_history.append({
                    'identifier': identifier,
                    'timestamp': time.time(),
                    'method': request.method,
                    'path': request.url.path,
                    'status': status.value,
                    'response_time': 0.0,  # Será atualizado
                    'user_agent': request.headers.get('user-agent', ''),
                    'referer': request.headers.get('referer', '')
                })
                
        except Exception as e:
            logger.error(f"Error recording for learning: {e}")
    
    def _notify_limit_exceeded_callbacks(self, identifier: str, data: Dict[str, Any]):
        """Notifica callbacks de limite excedido"""
        for callback in self._limit_exceeded_callbacks:
            try:
                callback(identifier, data)
            except Exception as e:
                logger.error(f"Error in limit exceeded callback: {e}")
    
    def add_to_whitelist(self, identifier: str):
        """Adiciona identificador à whitelist"""
        config = self._get_config_for_identifier(identifier)
        if identifier not in config.whitelist_ips:
            config.whitelist_ips.append(identifier)
            self._set_config_for_identifier(identifier, config)
            logger.info(f"Added {identifier} to whitelist")
    
    def add_to_blacklist(self, identifier: str):
        """Adiciona identificador à blacklist"""
        config = self._get_config_for_identifier(identifier)
        if identifier not in config.blacklist_ips:
            config.blacklist_ips.append(identifier)
            self._set_config_for_identifier(identifier, config)
            logger.info(f"Added {identifier} to blacklist")
    
    def remove_from_whitelist(self, identifier: str):
        """Remove identificador da whitelist"""
        config = self._get_config_for_identifier(identifier)
        if identifier in config.whitelist_ips:
            config.whitelist_ips.remove(identifier)
            self._set_config_for_identifier(identifier, config)
            logger.info(f"Removed {identifier} from whitelist")
    
    def remove_from_blacklist(self, identifier: str):
        """Remove identificador da blacklist"""
        config = self._get_config_for_identifier(identifier)
        if identifier in config.blacklist_ips:
            config.blacklist_ips.remove(identifier)
            self._set_config_for_identifier(identifier, config)
            logger.info(f"Removed {identifier} from blacklist")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do rate limiter"""
        try:
            with self._lock:
                return {
                    'total_requests': len(self.request_history),
                    'user_configs': len(self.user_configs),
                    'ip_configs': len(self.ip_configs),
                    'learning_enabled': self.enable_learning,
                    'is_running': self.is_running,
                    'redis_connected': self._redis_client is not None,
                    'patterns_learned': len(self.learning_data),
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}

# Instância global do rate limiter
_rate_limiter: Optional[AdaptiveRateLimiter] = None

def get_rate_limiter() -> AdaptiveRateLimiter:
    """Obtém instância global do rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        raise RuntimeError("Rate limiter not initialized")
    return _rate_limiter

def initialize_rate_limiter(redis_url: str = "redis://localhost:6379", **kwargs) -> AdaptiveRateLimiter:
    """Inicializa rate limiter global"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = AdaptiveRateLimiter(redis_url, **kwargs)
    return _rate_limiter

def shutdown_rate_limiter():
    """Desliga rate limiter global"""
    global _rate_limiter
    if _rate_limiter:
        _rate_limiter.stop_learning()
        _rate_limiter = None 