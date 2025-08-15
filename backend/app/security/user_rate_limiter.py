"""
User Rate Limiter - Omni Keywords Finder
Tracing ID: USER_RATE_LIMITER_20250127_001

Sistema de rate limiting por usuário/plano com limites diferenciados
baseados no tipo de conta e comportamento do usuário.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import hashlib
import ipaddress

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import jwt

# Configuração de logging
logger = logging.getLogger(__name__)

class UserPlan(Enum):
    """Planos de usuário"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserStatus(Enum):
    """Status do usuário"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    WHITELISTED = "whitelisted"

@dataclass
class UserRateLimitConfig:
    """Configuração de rate limit por usuário"""
    user_id: str
    plan: UserPlan
    status: UserStatus
    base_limit: int  # Limite base por minuto
    burst_limit: int  # Limite de burst
    window_size: int  # Janela de tempo em segundos
    priority: int  # Prioridade (1-10, 10 = mais alta)
    custom_limits: Dict[str, int] = field(default_factory=dict)  # Limites customizados por endpoint
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class UserRateLimitMetrics:
    """Métricas de rate limit por usuário"""
    user_id: str
    plan: UserPlan
    requests_count: int
    limit: int
    remaining: int
    reset_time: float
    status: str
    response_time: float
    timestamp: float
    endpoint: str

class UserRateLimiter:
    """
    Rate limiter por usuário com limites diferenciados por plano
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        jwt_secret: str = "your-secret-key",
        enable_analytics: bool = True,
        analytics_window: int = 3600  # 1 hora
    ):
        self.redis_url = redis_url
        self.jwt_secret = jwt_secret
        self.enable_analytics = enable_analytics
        self.analytics_window = analytics_window
        
        # Configurações padrão por plano
        self.plan_configs = {
            UserPlan.FREE: {
                'base_limit': 50,
                'burst_limit': 100,
                'window_size': 60,
                'priority': 1
            },
            UserPlan.STARTER: {
                'base_limit': 200,
                'burst_limit': 400,
                'window_size': 60,
                'priority': 3
            },
            UserPlan.PRO: {
                'base_limit': 500,
                'burst_limit': 1000,
                'window_size': 60,
                'priority': 5
            },
            UserPlan.ENTERPRISE: {
                'base_limit': 2000,
                'burst_limit': 5000,
                'window_size': 60,
                'priority': 10
            }
        }
        
        # Configurações por endpoint
        self.endpoint_configs = {
            '/api/keywords/analyze': {
                'multiplier': 2.0,  # 2x o limite normal
                'priority': 8
            },
            '/api/keywords/generate': {
                'multiplier': 1.5,
                'priority': 6
            },
            '/api/analytics/export': {
                'multiplier': 0.5,  # 0.5x o limite normal (mais restritivo)
                'priority': 4
            },
            '/api/admin/': {
                'multiplier': 3.0,  # 3x o limite normal para admin
                'priority': 10
            }
        }
        
        # Estado do sistema
        self.user_configs: Dict[str, UserRateLimitConfig] = {}
        self.analytics_data: Dict[str, Any] = defaultdict(dict)
        
        # Threading
        self._lock = threading.RLock()
        self._analytics_thread = None
        self._stop_event = threading.Event()
        
        # Redis connection
        self._redis_client = None
        self._setup_redis()
        
        # JWT security
        self.security = HTTPBearer()
        
        # Callbacks
        self._limit_exceeded_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self._plan_upgrade_callbacks: List[Callable[[str, UserPlan], None]] = []
        self._user_suspended_callbacks: List[Callable[[str, str], None]] = []
        
        logger.info("User rate limiter initialized")
    
    def _setup_redis(self):
        """Configura conexão com Redis"""
        try:
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self._redis_client.ping()
            logger.info("Redis connection established for user rate limiter")
        except Exception as e:
            logger.warning(f"Redis connection failed for user rate limiter: {e}")
            self._redis_client = None
    
    def add_limit_exceeded_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Adiciona callback para quando limite é excedido"""
        self._limit_exceeded_callbacks.append(callback)
    
    def add_plan_upgrade_callback(self, callback: Callable[[str, UserPlan], None]):
        """Adiciona callback para upgrade de plano"""
        self._plan_upgrade_callbacks.append(callback)
    
    def add_user_suspended_callback(self, callback: Callable[[str, str], None]):
        """Adiciona callback para usuário suspenso"""
        self._user_suspended_callbacks.append(callback)
    
    def start_analytics(self):
        """Inicia analytics de uso"""
        if self._analytics_thread:
            logger.warning("Analytics already running")
            return
        
        self._stop_event.clear()
        
        self._analytics_thread = threading.Thread(
            target=self._analytics_loop,
            daemon=True,
            name="UserRateLimiterAnalytics"
        )
        self._analytics_thread.start()
        
        logger.info("User rate limiter analytics started")
    
    def stop_analytics(self):
        """Para analytics"""
        if not self._analytics_thread:
            return
        
        self._stop_event.set()
        self._analytics_thread.join(timeout=5)
        self._analytics_thread = None
        
        logger.info("User rate limiter analytics stopped")
    
    def _analytics_loop(self):
        """Loop principal de analytics"""
        while not self._stop_event.is_set():
            try:
                # Analisar padrões de uso
                self._analyze_usage_patterns()
                
                # Verificar upgrades recomendados
                self._check_upgrade_recommendations()
                
                # Aguardar próximo ciclo
                self._stop_event.wait(self.analytics_window)
                
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")
                self._stop_event.wait(60)
    
    def _analyze_usage_patterns(self):
        """Analisa padrões de uso dos usuários"""
        try:
            with self._lock:
                for user_id, config in self.user_configs.items():
                    # Calcular métricas de uso
                    usage_metrics = self._calculate_user_usage_metrics(user_id)
                    
                    if usage_metrics:
                        self.analytics_data[user_id] = usage_metrics
                        
                        # Verificar se usuário está próximo do limite
                        utilization_rate = usage_metrics['total_requests'] / config.base_limit
                        
                        if utilization_rate > 0.8:  # 80% do limite
                            logger.info(f"User {user_id} approaching rate limit: {utilization_rate:.2f}")
                        
                        # Verificar se usuário está subutilizando
                        elif utilization_rate < 0.1:  # 10% do limite
                            logger.info(f"User {user_id} underutilizing: {utilization_rate:.2f}")
                            
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
    
    def _calculate_user_usage_metrics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Calcula métricas de uso para um usuário"""
        try:
            if self._redis_client:
                # Obter dados do Redis
                key = f"user_usage:{user_id}"
                usage_data = self._redis_client.hgetall(key)
                
                if usage_data:
                    return {
                        'total_requests': int(usage_data.get('total_requests', 0)),
                        'total_errors': int(usage_data.get('total_errors', 0)),
                        'avg_response_time': float(usage_data.get('avg_response_time', 0)),
                        'last_request': float(usage_data.get('last_request', 0)),
                        'endpoint_usage': json.loads(usage_data.get('endpoint_usage', '{}'))
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating usage metrics for {user_id}: {e}")
            return None
    
    def _check_upgrade_recommendations(self):
        """Verifica se há recomendações de upgrade"""
        try:
            with self._lock:
                for user_id, analytics in self.analytics_data.items():
                    config = self.user_configs.get(user_id)
                    if not config:
                        continue
                    
                    # Verificar se usuário está consistentemente próximo do limite
                    total_requests = analytics.get('total_requests', 0)
                    utilization_rate = total_requests / config.base_limit
                    
                    if utilization_rate > 0.9:  # 90% do limite
                        # Recomendar upgrade
                        self._recommend_upgrade(user_id, config.plan)
                        
        except Exception as e:
            logger.error(f"Error checking upgrade recommendations: {e}")
    
    def _recommend_upgrade(self, user_id: str, current_plan: UserPlan):
        """Recomenda upgrade de plano"""
        try:
            # Determinar próximo plano
            plan_order = [UserPlan.FREE, UserPlan.STARTER, UserPlan.PRO, UserPlan.ENTERPRISE]
            current_index = plan_order.index(current_plan)
            
            if current_index < len(plan_order) - 1:
                next_plan = plan_order[current_index + 1]
                
                # Notificar callbacks
                for callback in self._plan_upgrade_callbacks:
                    try:
                        callback(user_id, next_plan)
                    except Exception as e:
                        logger.error(f"Error in plan upgrade callback: {e}")
                
                logger.info(f"Upgrade recommended for user {user_id}: {current_plan.value} -> {next_plan.value}")
                
        except Exception as e:
            logger.error(f"Error recommending upgrade: {e}")
    
    async def check_user_rate_limit(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> UserRateLimitMetrics:
        """Verifica rate limit para um usuário"""
        try:
            # Extrair e validar token JWT
            user_id, plan, status = await self._extract_user_info(credentials.credentials)
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Verificar status do usuário
            if status == UserStatus.BANNED:
                raise HTTPException(status_code=403, detail="User banned")
            
            if status == UserStatus.SUSPENDED:
                # Notificar callbacks
                for callback in self._user_suspended_callbacks:
                    try:
                        callback(user_id, "User suspended")
                    except Exception as e:
                        logger.error(f"Error in user suspended callback: {e}")
                
                raise HTTPException(status_code=403, detail="User suspended")
            
            # Obter ou criar configuração do usuário
            config = self._get_or_create_user_config(user_id, plan, status)
            
            # Verificar se está em whitelist
            if status == UserStatus.WHITELISTED:
                return UserRateLimitMetrics(
                    user_id=user_id,
                    plan=plan,
                    requests_count=0,
                    limit=config.base_limit,
                    remaining=config.base_limit,
                    reset_time=time.time() + config.window_size,
                    status="whitelisted",
                    response_time=0.0,
                    timestamp=time.time(),
                    endpoint=request.url.path
                )
            
            # Calcular limite baseado no endpoint
            endpoint = request.url.path
            endpoint_limit = self._calculate_endpoint_limit(config, endpoint)
            
            # Verificar rate limit
            current_time = time.time()
            window_start = current_time - config.window_size
            
            # Contar requisições na janela
            request_count = await self._count_user_requests_in_window(
                user_id, window_start, current_time
            )
            
            # Verificar se excedeu o limite
            if request_count >= endpoint_limit:
                # Verificar burst allowance
                if request_count < config.burst_limit:
                    status_str = "limited"
                else:
                    status_str = "blocked"
                
                # Notificar callbacks
                self._notify_limit_exceeded_callbacks(user_id, {
                    'request_count': request_count,
                    'limit': endpoint_limit,
                    'burst_limit': config.burst_limit,
                    'endpoint': endpoint,
                    'status': status_str
                })
                
                if status_str == "blocked":
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded: {request_count}/{endpoint_limit}"
                    )
            else:
                status_str = "allowed"
            
            # Registrar requisição
            await self._record_user_request(user_id, current_time, endpoint)
            
            # Atualizar analytics
            if self.enable_analytics:
                self._update_user_analytics(user_id, endpoint, current_time)
            
            return UserRateLimitMetrics(
                user_id=user_id,
                plan=plan,
                requests_count=request_count,
                limit=endpoint_limit,
                remaining=max(0, endpoint_limit - request_count),
                reset_time=current_time + config.window_size,
                status=status_str,
                response_time=0.0,  # Será atualizado após processamento
                timestamp=current_time,
                endpoint=endpoint
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking user rate limit: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def _extract_user_info(self, token: str) -> Tuple[Optional[str], UserPlan, UserStatus]:
        """Extrai informações do usuário do token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            user_id = payload.get('user_id')
            plan_str = payload.get('plan', 'free')
            status_str = payload.get('status', 'active')
            
            # Converter para enum
            plan = UserPlan(plan_str)
            status = UserStatus(status_str)
            
            return user_id, plan, status
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None, UserPlan.FREE, UserStatus.SUSPENDED
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None, UserPlan.FREE, UserStatus.SUSPENDED
        except Exception as e:
            logger.error(f"Error extracting user info: {e}")
            return None, UserPlan.FREE, UserStatus.SUSPENDED
    
    def _get_or_create_user_config(self, user_id: str, plan: UserPlan, status: UserStatus) -> UserRateLimitConfig:
        """Obtém ou cria configuração do usuário"""
        with self._lock:
            if user_id not in self.user_configs:
                # Criar nova configuração
                plan_config = self.plan_configs[plan]
                config = UserRateLimitConfig(
                    user_id=user_id,
                    plan=plan,
                    status=status,
                    base_limit=plan_config['base_limit'],
                    burst_limit=plan_config['burst_limit'],
                    window_size=plan_config['window_size'],
                    priority=plan_config['priority']
                )
                self.user_configs[user_id] = config
                logger.info(f"Created rate limit config for user {user_id}: {plan.value}")
            else:
                # Atualizar configuração existente se necessário
                config = self.user_configs[user_id]
                if config.plan != plan or config.status != status:
                    config.plan = plan
                    config.status = status
                    config.updated_at = time.time()
                    
                    # Atualizar limites baseado no novo plano
                    plan_config = self.plan_configs[plan]
                    config.base_limit = plan_config['base_limit']
                    config.burst_limit = plan_config['burst_limit']
                    config.priority = plan_config['priority']
                    
                    logger.info(f"Updated rate limit config for user {user_id}: {plan.value}")
            
            return config
    
    def _calculate_endpoint_limit(self, config: UserRateLimitConfig, endpoint: str) -> int:
        """Calcula limite específico para um endpoint"""
        base_limit = config.base_limit
        
        # Aplicar multiplicador do endpoint
        for endpoint_pattern, endpoint_config in self.endpoint_configs.items():
            if endpoint.startswith(endpoint_pattern):
                multiplier = endpoint_config['multiplier']
                base_limit = int(base_limit * multiplier)
                break
        
        # Aplicar limites customizados do usuário
        if endpoint in config.custom_limits:
            base_limit = config.custom_limits[endpoint]
        
        return base_limit
    
    async def _count_user_requests_in_window(
        self, 
        user_id: str, 
        window_start: float, 
        window_end: float
    ) -> int:
        """Conta requisições do usuário em uma janela de tempo"""
        try:
            if self._redis_client:
                # Usar Redis para contagem
                key = f"user_rate_limit:{user_id}:{int(window_start)}"
                count = self._redis_client.zcount(key, window_start, window_end)
                return count
            else:
                # Contagem em memória (fallback)
                return 0
                
        except Exception as e:
            logger.error(f"Error counting user requests: {e}")
            return 0
    
    async def _record_user_request(self, user_id: str, timestamp: float, endpoint: str):
        """Registra uma requisição do usuário"""
        try:
            if self._redis_client:
                # Registrar no Redis
                key = f"user_rate_limit:{user_id}:{int(timestamp)}"
                self._redis_client.zadd(key, {f"{timestamp}:{endpoint}": timestamp})
                self._redis_client.expire(key, 3600)  # Expirar em 1 hora
                
        except Exception as e:
            logger.error(f"Error recording user request: {e}")
    
    def _update_user_analytics(self, user_id: str, endpoint: str, timestamp: float):
        """Atualiza analytics do usuário"""
        try:
            if self._redis_client:
                key = f"user_usage:{user_id}"
                
                # Incrementar contadores
                self._redis_client.hincrby(key, 'total_requests', 1)
                self._redis_client.hset(key, 'last_request', timestamp)
                
                # Atualizar uso por endpoint
                endpoint_usage_key = 'endpoint_usage'
                current_usage = self._redis_client.hget(key, endpoint_usage_key)
                
                if current_usage:
                    usage_data = json.loads(current_usage)
                else:
                    usage_data = {}
                
                usage_data[endpoint] = usage_data.get(endpoint, 0) + 1
                self._redis_client.hset(key, endpoint_usage_key, json.dumps(usage_data))
                
                # Expirar após 24 horas
                self._redis_client.expire(key, 86400)
                
        except Exception as e:
            logger.error(f"Error updating user analytics: {e}")
    
    def _notify_limit_exceeded_callbacks(self, user_id: str, data: Dict[str, Any]):
        """Notifica callbacks de limite excedido"""
        for callback in self._limit_exceeded_callbacks:
            try:
                callback(user_id, data)
            except Exception as e:
                logger.error(f"Error in limit exceeded callback: {e}")
    
    def set_user_plan(self, user_id: str, plan: UserPlan):
        """Define plano do usuário"""
        with self._lock:
            if user_id in self.user_configs:
                config = self.user_configs[user_id]
                config.plan = plan
                config.updated_at = time.time()
                
                # Atualizar limites baseado no novo plano
                plan_config = self.plan_configs[plan]
                config.base_limit = plan_config['base_limit']
                config.burst_limit = plan_config['burst_limit']
                config.priority = plan_config['priority']
                
                logger.info(f"Updated user {user_id} plan to {plan.value}")
    
    def set_user_status(self, user_id: str, status: UserStatus):
        """Define status do usuário"""
        with self._lock:
            if user_id in self.user_configs:
                config = self.user_configs[user_id]
                config.status = status
                config.updated_at = time.time()
                
                logger.info(f"Updated user {user_id} status to {status.value}")
    
    def set_custom_limit(self, user_id: str, endpoint: str, limit: int):
        """Define limite customizado para um endpoint"""
        with self._lock:
            if user_id in self.user_configs:
                config = self.user_configs[user_id]
                config.custom_limits[endpoint] = limit
                config.updated_at = time.time()
                
                logger.info(f"Set custom limit for user {user_id} endpoint {endpoint}: {limit}")
    
    def get_user_config(self, user_id: str) -> Optional[UserRateLimitConfig]:
        """Obtém configuração do usuário"""
        with self._lock:
            return self.user_configs.get(user_id)
    
    def get_user_analytics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtém analytics do usuário"""
        return self.analytics_data.get(user_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do rate limiter"""
        try:
            with self._lock:
                total_users = len(self.user_configs)
                plan_distribution = defaultdict(int)
                status_distribution = defaultdict(int)
                
                for config in self.user_configs.values():
                    plan_distribution[config.plan.value] += 1
                    status_distribution[config.status.value] += 1
                
                return {
                    'total_users': total_users,
                    'plan_distribution': dict(plan_distribution),
                    'status_distribution': dict(status_distribution),
                    'analytics_enabled': self.enable_analytics,
                    'redis_connected': self._redis_client is not None,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}

# Instância global do user rate limiter
_user_rate_limiter: Optional[UserRateLimiter] = None

def get_user_rate_limiter() -> UserRateLimiter:
    """Obtém instância global do user rate limiter"""
    global _user_rate_limiter
    if _user_rate_limiter is None:
        raise RuntimeError("User rate limiter not initialized")
    return _user_rate_limiter

def initialize_user_rate_limiter(redis_url: str = "redis://localhost:6379", **kwargs) -> UserRateLimiter:
    """Inicializa user rate limiter global"""
    global _user_rate_limiter
    if _user_rate_limiter is None:
        _user_rate_limiter = UserRateLimiter(redis_url, **kwargs)
    return _user_rate_limiter

def shutdown_user_rate_limiter():
    """Desliga user rate limiter global"""
    global _user_rate_limiter
    if _user_rate_limiter:
        _user_rate_limiter.stop_analytics()
        _user_rate_limiter = None 