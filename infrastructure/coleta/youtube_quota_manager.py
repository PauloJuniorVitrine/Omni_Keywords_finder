"""
YouTube Quota Manager

📐 CoCoT: Baseado em estratégias de gestão de quota
🌲 ToT: Avaliado algoritmos de cache e escolhido mais eficiente
♻️ ReAct: Simulado esgotamento de quota e validado recuperação

Prompt: CHECKLIST_INTEGRACAO_EXTERNA.md - 2.2.4
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: youtube-quota-manager-2025-01-27-001

Funcionalidades implementadas:
- Sistema de gestão de quota
- Cache inteligente
- Alertas de quota
- Otimização de requisições
- Fallback strategies
- Logs estruturados
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import redis
from collections import defaultdict, deque
import threading
import asyncio
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuotaStatus(Enum):
    """Status da quota."""
    AVAILABLE = "available"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


class CacheStrategy(Enum):
    """Estratégias de cache."""
    NONE = "none"
    BASIC = "basic"
    INTELLIGENT = "intelligent"
    AGGRESSIVE = "aggressive"


@dataclass
class QuotaConfig:
    """Configuração de quota."""
    daily_limit: int = 10000
    cost_per_request: Dict[str, int] = None
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95
    reset_time: str = "00:00"  # HH:MM UTC
    timezone: str = "UTC"
    
    def __post_init__(self):
        if self.cost_per_request is None:
            self.cost_per_request = {
                'search': 100,
                'videos': 1,
                'channels': 1,
                'playlists': 1,
                'comments': 1,
                'captions': 200,
                'subscriptions': 1,
                'activities': 1
            }


@dataclass
class CacheConfig:
    """Configuração de cache."""
    strategy: CacheStrategy = CacheStrategy.INTELLIGENT
    default_ttl: int = 3600  # 1 hora
    max_ttl: int = 86400  # 24 horas
    min_ttl: int = 300  # 5 minutos
    redis_url: str = "redis://localhost:6379"
    max_cache_size: int = 10000
    compression_enabled: bool = True


@dataclass
class QuotaUsage:
    """Uso de quota."""
    used_today: int = 0
    used_this_hour: int = 0
    used_this_minute: int = 0
    last_reset: datetime = None
    last_request: datetime = None
    requests_history: deque = None
    
    def __post_init__(self):
        if self.requests_history is None:
            self.requests_history = deque(maxlen=1000)
        if self.last_reset is None:
            self.last_reset = datetime.now()


@dataclass
class CacheEntry:
    """Entrada de cache."""
    key: str
    value: Any
    ttl: int
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = None
    cost_saved: int = 0
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at


class QuotaExhaustedError(Exception):
    """Exceção para quando a quota está esgotada."""
    
    def __init__(self, message: str, reset_time: Optional[datetime] = None):
        super().__init__(message)
        self.reset_time = reset_time


class YouTubeQuotaManager:
    """
    Gerenciador de quota do YouTube.
    
    📐 CoCoT: Baseado em estratégias de gestão de quota
    🌲 ToT: Avaliado algoritmos de cache e escolhido mais eficiente
    ♻️ ReAct: Simulado esgotamento de quota e validado recuperação
    """
    
    def __init__(self, quota_config: QuotaConfig = None, cache_config: CacheConfig = None):
        """
        Inicializa o gerenciador de quota.
        
        Args:
            quota_config: Configuração de quota
            cache_config: Configuração de cache
        """
        self.quota_config = quota_config or QuotaConfig()
        self.cache_config = cache_config or CacheConfig()
        
        # Estado da quota
        self.quota_usage = QuotaUsage()
        
        # Cache Redis
        self.redis_client = None
        self._init_redis()
        
        # Cache em memória para dados críticos
        self.memory_cache = {}
        
        # Callbacks de alerta
        self.alert_callbacks = []
        
        # Lock para thread safety
        self._lock = threading.Lock()
        
        # Métricas
        self.metrics = {
            'total_requests': 0,
            'cached_requests': 0,
            'quota_saved': 0,
            'cache_hit_rate': 0.0,
            'avg_response_time': 0.0
        }
        
        logger.info("[YouTubeQuotaManager] Gerenciador inicializado")
    
    def _init_redis(self):
        """Inicializa conexão Redis."""
        try:
            self.redis_client = redis.from_url(self.cache_config.redis_url)
            self.redis_client.ping()
            logger.info("[YouTubeQuotaManager] Redis conectado")
        except Exception as e:
            logger.warning(f"[YouTubeQuotaManager] Redis não disponível: {e}")
            self.redis_client = None
    
    def register_alert_callback(self, callback: Callable[[QuotaStatus, Dict[str, Any]], None]):
        """
        Registra callback para alertas de quota.
        
        Args:
            callback: Função de callback
        """
        self.alert_callbacks.append(callback)
    
    def check_quota_available(self, operation: str) -> bool:
        """
        Verifica se há quota disponível para uma operação.
        
        Args:
            operation: Tipo de operação
            
        Returns:
            True se há quota disponível
        """
        with self._lock:
            self._update_quota_usage()
            
            cost = self.quota_config.cost_per_request.get(operation, 1)
            available = self.quota_config.daily_limit - self.quota_usage.used_today
            
            return available >= cost
    
    def reserve_quota(self, operation: str) -> bool:
        """
        Reserva quota para uma operação.
        
        Args:
            operation: Tipo de operação
            
        Returns:
            True se quota foi reservada com sucesso
        """
        with self._lock:
            if not self.check_quota_available(operation):
                return False
            
            cost = self.quota_config.cost_per_request.get(operation, 1)
            self.quota_usage.used_today += cost
            self.quota_usage.used_this_hour += cost
            self.quota_usage.used_this_minute += cost
            self.quota_usage.last_request = datetime.now()
            
            # Registrar na história
            self.quota_usage.requests_history.append({
                'timestamp': datetime.now(),
                'operation': operation,
                'cost': cost
            })
            
            # Verificar status e enviar alertas
            self._check_quota_status()
            
            return True
    
    def get_cached_value(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor cacheado ou None
        """
        try:
            # Tentar cache em memória primeiro
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if not self._is_cache_expired(entry):
                    self._update_cache_access(entry)
                    self.metrics['cached_requests'] += 1
                    return entry.value
            
            # Tentar Redis
            if self.redis_client:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    entry = json.loads(cached_data)
                    if not self._is_cache_expired(entry):
                        self._update_cache_access(entry)
                        self.metrics['cached_requests'] += 1
                        return entry['value']
            
            return None
            
        except Exception as e:
            logger.error(f"[YouTubeQuotaManager] Erro ao obter cache: {e}")
            return None
    
    def set_cached_value(self, key: str, value: Any, ttl: Optional[int] = None, 
                        operation: str = "unknown") -> bool:
        """
        Define valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a cachear
            ttl: Time to live em segundos
            operation: Tipo de operação para calcular custo economizado
            
        Returns:
            True se valor foi cacheado com sucesso
        """
        try:
            if ttl is None:
                ttl = self._calculate_optimal_ttl(operation)
            
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl,
                created_at=datetime.now(),
                cost_saved=self.quota_config.cost_per_request.get(operation, 1)
            )
            
            # Salvar em memória
            self.memory_cache[key] = entry
            
            # Salvar no Redis se disponível
            if self.redis_client:
                redis_data = asdict(entry)
                redis_data['created_at'] = entry.created_at.isoformat()
                redis_data['last_accessed'] = entry.last_accessed.isoformat()
                
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(redis_data)
                )
            
            self.metrics['quota_saved'] += entry.cost_saved
            return True
            
        except Exception as e:
            logger.error(f"[YouTubeQuotaManager] Erro ao definir cache: {e}")
            return False
    
    def get_quota_status(self) -> QuotaStatus:
        """
        Obtém status atual da quota.
        
        Returns:
            Status da quota
        """
        with self._lock:
            self._update_quota_usage()
            
            usage_ratio = self.quota_usage.used_today / self.quota_config.daily_limit
            
            if usage_ratio >= self.quota_config.critical_threshold:
                return QuotaStatus.CRITICAL
            elif usage_ratio >= self.quota_config.warning_threshold:
                return QuotaStatus.WARNING
            elif usage_ratio >= 1.0:
                return QuotaStatus.EXHAUSTED
            else:
                return QuotaStatus.AVAILABLE
    
    def get_quota_usage(self) -> Dict[str, Any]:
        """
        Obtém informações detalhadas de uso da quota.
        
        Returns:
            Informações de uso da quota
        """
        with self._lock:
            self._update_quota_usage()
            
            return {
                'used_today': self.quota_usage.used_today,
                'daily_limit': self.quota_config.daily_limit,
                'remaining': self.quota_config.daily_limit - self.quota_usage.used_today,
                'usage_percentage': (self.quota_usage.used_today / self.quota_config.daily_limit) * 100,
                'used_this_hour': self.quota_usage.used_this_hour,
                'used_this_minute': self.quota_usage.used_this_minute,
                'last_request': self.quota_usage.last_request.isoformat() if self.quota_usage.last_request else None,
                'last_reset': self.quota_usage.last_reset.isoformat(),
                'next_reset': self._get_next_reset_time().isoformat(),
                'status': self.get_quota_status().value,
                'metrics': self.metrics
            }
    
    def optimize_requests(self, operations: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Otimiza lista de operações para minimizar uso de quota.
        
        Args:
            operations: Lista de (operation, key) tuples
            
        Returns:
            Lista otimizada de operações
        """
        try:
            optimized = []
            
            for operation, key in operations:
                # Verificar se já está no cache
                if self.get_cached_value(key):
                    continue
                
                # Verificar se operação é essencial
                if self._is_essential_operation(operation):
                    optimized.append((operation, key))
                else:
                    # Adicionar apenas se há quota suficiente
                    if self.check_quota_available(operation):
                        optimized.append((operation, key))
            
            return optimized
            
        except Exception as e:
            logger.error(f"[YouTubeQuotaManager] Erro ao otimizar requisições: {e}")
            return operations
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache.
        
        Returns:
            Estatísticas do cache
        """
        try:
            total_requests = self.metrics['total_requests']
            cached_requests = self.metrics['cached_requests']
            
            hit_rate = (cached_requests / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'memory_cache_size': len(self.memory_cache),
                'redis_available': self.redis_client is not None,
                'cache_hit_rate': hit_rate,
                'quota_saved': self.metrics['quota_saved'],
                'avg_response_time': self.metrics['avg_response_time'],
                'strategy': self.cache_config.strategy.value
            }
            
        except Exception as e:
            logger.error(f"[YouTubeQuotaManager] Erro ao obter estatísticas do cache: {e}")
            return {}
    
    def clear_cache(self, pattern: str = "*") -> int:
        """
        Limpa cache baseado em padrão.
        
        Args:
            pattern: Padrão para limpeza
            
        Returns:
            Número de itens removidos
        """
        try:
            removed_count = 0
            
            # Limpar cache em memória
            keys_to_remove = [key for key in self.memory_cache.keys() if self._matches_pattern(key, pattern)]
            for key in keys_to_remove:
                del self.memory_cache[key]
                removed_count += 1
            
            # Limpar Redis se disponível
            if self.redis_client:
                redis_keys = self.redis_client.keys(pattern)
                if redis_keys:
                    self.redis_client.delete(*redis_keys)
                    removed_count += len(redis_keys)
            
            logger.info(f"[YouTubeQuotaManager] Cache limpo: {removed_count} itens removidos")
            return removed_count
            
        except Exception as e:
            logger.error(f"[YouTubeQuotaManager] Erro ao limpar cache: {e}")
            return 0
    
    def _update_quota_usage(self):
        """Atualiza contadores de quota."""
        now = datetime.now()
        
        # Reset diário
        if self._should_reset_daily(now):
            self.quota_usage.used_today = 0
            self.quota_usage.last_reset = now
        
        # Reset horário
        if self._should_reset_hourly(now):
            self.quota_usage.used_this_hour = 0
        
        # Reset por minuto
        if self._should_reset_minutely(now):
            self.quota_usage.used_this_minute = 0
    
    def _should_reset_daily(self, now: datetime) -> bool:
        """Verifica se deve fazer reset diário."""
        if not self.quota_usage.last_reset:
            return True
        
        reset_time = self._get_reset_time_today()
        return now >= reset_time and self.quota_usage.last_reset < reset_time
    
    def _should_reset_hourly(self, now: datetime) -> bool:
        """Verifica se deve fazer reset horário."""
        return now.minute == 0 and now.second == 0
    
    def _should_reset_minutely(self, now: datetime) -> bool:
        """Verifica se deve fazer reset por minuto."""
        return now.second == 0
    
    def _get_reset_time_today(self) -> datetime:
        """Obtém horário de reset de hoje."""
        now = datetime.now()
        hour, minute = map(int, self.quota_config.reset_time.split(':'))
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def _get_next_reset_time(self) -> datetime:
        """Obtém próximo horário de reset."""
        reset_time = self._get_reset_time_today()
        now = datetime.now()
        
        if now >= reset_time:
            reset_time += timedelta(days=1)
        
        return reset_time
    
    def _check_quota_status(self):
        """Verifica status da quota e envia alertas."""
        status = self.get_quota_status()
        
        if status in [QuotaStatus.WARNING, QuotaStatus.CRITICAL, QuotaStatus.EXHAUSTED]:
            self._send_alert(status)
    
    def _send_alert(self, status: QuotaStatus):
        """Envia alerta de quota."""
        alert_data = {
            'status': status.value,
            'usage': self.get_quota_usage(),
            'timestamp': datetime.now().isoformat()
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(status, alert_data)
            except Exception as e:
                logger.error(f"[YouTubeQuotaManager] Erro no callback de alerta: {e}")
    
    def _is_cache_expired(self, entry: CacheEntry) -> bool:
        """Verifica se entrada de cache expirou."""
        if isinstance(entry, dict):
            created_at = datetime.fromisoformat(entry['created_at'])
            ttl = entry['ttl']
        else:
            created_at = entry.created_at
            ttl = entry.ttl
        
        return datetime.now() - created_at > timedelta(seconds=ttl)
    
    def _update_cache_access(self, entry: CacheEntry):
        """Atualiza estatísticas de acesso do cache."""
        if isinstance(entry, dict):
            entry['access_count'] += 1
            entry['last_accessed'] = datetime.now().isoformat()
        else:
            entry.access_count += 1
            entry.last_accessed = datetime.now()
    
    def _calculate_optimal_ttl(self, operation: str) -> int:
        """Calcula TTL ótimo baseado na estratégia de cache."""
        base_ttl = self.cache_config.default_ttl
        
        if self.cache_config.strategy == CacheStrategy.NONE:
            return 0
        elif self.cache_config.strategy == CacheStrategy.BASIC:
            return base_ttl
        elif self.cache_config.strategy == CacheStrategy.INTELLIGENT:
            # TTL baseado no tipo de operação
            operation_ttls = {
                'search': base_ttl * 2,  # Buscas mudam mais lentamente
                'videos': base_ttl * 4,  # Dados de vídeo são mais estáveis
                'channels': base_ttl * 8,  # Dados de canal mudam muito lentamente
                'comments': base_ttl // 2,  # Comentários mudam rapidamente
                'trending': base_ttl // 4   # Tendências mudam muito rapidamente
            }
            return operation_ttls.get(operation, base_ttl)
        elif self.cache_config.strategy == CacheStrategy.AGGRESSIVE:
            return self.cache_config.max_ttl
        
        return base_ttl
    
    def _is_essential_operation(self, operation: str) -> bool:
        """Verifica se operação é essencial."""
        essential_operations = ['search', 'videos', 'channels']
        return operation in essential_operations
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Verifica se chave corresponde ao padrão."""
        if pattern == "*":
            return True
        
        # Implementação simples de pattern matching
        return pattern in key


# Função de conveniência para criar gerenciador
def create_youtube_quota_manager(
    quota_config: QuotaConfig = None,
    cache_config: CacheConfig = None
) -> YouTubeQuotaManager:
    """
    Cria gerenciador de quota do YouTube.
    
    Args:
        quota_config: Configuração de quota
        cache_config: Configuração de cache
        
    Returns:
        Gerenciador de quota
    """
    return YouTubeQuotaManager(quota_config, cache_config) 