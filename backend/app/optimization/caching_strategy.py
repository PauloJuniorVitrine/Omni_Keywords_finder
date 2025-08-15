"""
Sistema de Estratégia de Cache
Otimiza performance do backend através de cache inteligente
"""

import asyncio
import json
import hashlib
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from functools import wraps
import pickle
import gzip

import redis.asyncio as redis
from cachetools import TTLCache, LRUCache
import aioredis

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    LRU = "lru"
    TTL = "ttl"
    LFU = "lfu"
    FIFO = "fifo"


class CacheLevel(Enum):
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"


@dataclass
class CacheConfig:
    strategy: CacheStrategy
    ttl: int = 3600  # 1 hora
    max_size: int = 1000
    compression: bool = False
    serialize: bool = True
    key_prefix: str = "cache"
    namespace: str = "default"


@dataclass
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    avg_response_time: float = 0.0


class CacheManager:
    """
    Gerenciador de cache com múltiplas estratégias
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig(strategy=CacheStrategy.TTL)
        self.memory_cache: Optional[TTLCache] = None
        self.redis_client: Optional[redis.Redis] = None
        self.metrics = CacheMetrics()
        self._initialize_caches()
    
    def _initialize_caches(self):
        """Inicializa caches baseado na estratégia"""
        if self.config.strategy == CacheStrategy.TTL:
            self.memory_cache = TTLCache(
                maxsize=self.config.max_size,
                ttl=self.config.ttl
            )
        elif self.config.strategy == CacheStrategy.LRU:
            self.memory_cache = LRUCache(maxsize=self.config.max_size)
        else:
            self.memory_cache = TTLCache(
                maxsize=self.config.max_size,
                ttl=self.config.ttl
            )
    
    async def connect_redis(self, redis_url: str = "redis://localhost:6379"):
        """Conecta ao Redis"""
        try:
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")
            self.redis_client = None
    
    def _generate_key(self, key: str) -> str:
        """Gera chave de cache com namespace"""
        return f"{self.config.namespace}:{self.config.key_prefix}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serializa valor para cache"""
        if not self.config.serialize:
            return str(value).encode('utf-8')
        
        try:
            data = pickle.dumps(value)
            if self.config.compression:
                return gzip.compress(data)
            return data
        except Exception as e:
            logger.error(f"Erro ao serializar valor: {e}")
            return str(value).encode('utf-8')
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserializa valor do cache"""
        if not self.config.serialize:
            return data.decode('utf-8')
        
        try:
            if self.config.compression:
                data = gzip.decompress(data)
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Erro ao deserializar valor: {e}")
            return data.decode('utf-8')
    
    async def get(self, key: str, level: CacheLevel = CacheLevel.MEMORY) -> Optional[Any]:
        """Obtém valor do cache"""
        start_time = time.time()
        cache_key = self._generate_key(key)
        
        try:
            self.metrics.total_requests += 1
            
            if level == CacheLevel.MEMORY and self.memory_cache:
                value = self.memory_cache.get(cache_key)
                if value is not None:
                    self.metrics.hits += 1
                    self._update_metrics(start_time)
                    return value
                else:
                    self.metrics.misses += 1
            
            elif level == CacheLevel.REDIS and self.redis_client:
                value = await self.redis_client.get(cache_key)
                if value is not None:
                    self.metrics.hits += 1
                    self._update_metrics(start_time)
                    return self._deserialize_value(value)
                else:
                    self.metrics.misses += 1
            
            self._update_metrics(start_time)
            return None
            
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Erro ao obter cache {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  level: CacheLevel = CacheLevel.MEMORY) -> bool:
        """Define valor no cache"""
        start_time = time.time()
        cache_key = self._generate_key(key)
        ttl = ttl or self.config.ttl
        
        try:
            if level == CacheLevel.MEMORY and self.memory_cache:
                self.memory_cache[cache_key] = value
                self.metrics.sets += 1
            
            elif level == CacheLevel.REDIS and self.redis_client:
                serialized_value = self._serialize_value(value)
                await self.redis_client.setex(cache_key, ttl, serialized_value)
                self.metrics.sets += 1
            
            self._update_metrics(start_time)
            return True
            
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Erro ao definir cache {key}: {e}")
            return False
    
    async def delete(self, key: str, level: CacheLevel = CacheLevel.MEMORY) -> bool:
        """Remove valor do cache"""
        cache_key = self._generate_key(key)
        
        try:
            if level == CacheLevel.MEMORY and self.memory_cache:
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    self.metrics.deletes += 1
            
            elif level == CacheLevel.REDIS and self.redis_client:
                result = await self.redis_client.delete(cache_key)
                if result > 0:
                    self.metrics.deletes += 1
            
            return True
            
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    async def clear(self, level: CacheLevel = CacheLevel.MEMORY) -> bool:
        """Limpa cache"""
        try:
            if level == CacheLevel.MEMORY and self.memory_cache:
                self.memory_cache.clear()
            
            elif level == CacheLevel.REDIS and self.redis_client:
                pattern = f"{self.config.namespace}:{self.config.key_prefix}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def _update_metrics(self, start_time: float):
        """Atualiza métricas de performance"""
        response_time = time.time() - start_time
        self.metrics.avg_response_time = (
            (self.metrics.avg_response_time * (self.metrics.total_requests - 1) + response_time) 
            / self.metrics.total_requests
        )
        
        if self.metrics.total_requests > 0:
            self.metrics.hit_rate = self.metrics.hits / self.metrics.total_requests
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do cache"""
        return asdict(self.metrics)
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Obtém informações do cache"""
        info = {
            'config': asdict(self.config),
            'metrics': self.get_metrics(),
            'memory_cache_size': len(self.memory_cache) if self.memory_cache else 0,
            'redis_connected': self.redis_client is not None
        }
        
        if self.redis_client:
            try:
                info['redis_info'] = await self.redis_client.info()
            except Exception as e:
                info['redis_error'] = str(e)
        
        return info


class MultiLevelCache:
    """
    Cache com múltiplos níveis (memória + Redis)
    """
    
    def __init__(self, configs: Dict[CacheLevel, CacheConfig]):
        self.configs = configs
        self.caches: Dict[CacheLevel, CacheManager] = {}
        self._initialize_caches()
    
    def _initialize_caches(self):
        """Inicializa caches para cada nível"""
        for level, config in self.configs.items():
            self.caches[level] = CacheManager(config)
    
    async def connect_redis(self, redis_url: str = "redis://localhost:6379"):
        """Conecta Redis para todos os caches"""
        for cache in self.caches.values():
            await cache.connect_redis(redis_url)
    
    async def get(self, key: str, levels: List[CacheLevel] = None) -> Optional[Any]:
        """Obtém valor dos caches em ordem de prioridade"""
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        for level in levels:
            if level in self.caches:
                value = await self.caches[level].get(key, level)
                if value is not None:
                    # Populate other levels
                    await self._populate_other_levels(key, value, levels, level)
                    return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                  levels: List[CacheLevel] = None) -> bool:
        """Define valor em múltiplos níveis"""
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        success = True
        for level in levels:
            if level in self.caches:
                result = await self.caches[level].set(key, value, ttl, level)
                success = success and result
        
        return success
    
    async def _populate_other_levels(self, key: str, value: Any, 
                                   levels: List[CacheLevel], source_level: CacheLevel):
        """Popula outros níveis com valor encontrado"""
        for level in levels:
            if level != source_level and level in self.caches:
                await self.caches[level].set(key, value, level=level)
    
    def get_metrics(self) -> Dict[CacheLevel, Dict[str, Any]]:
        """Obtém métricas de todos os caches"""
        return {level: cache.get_metrics() for level, cache in self.caches.items()}


class CacheDecorator:
    """
    Decorator para cache automático
    """
    
    def __init__(self, cache_manager: CacheManager, ttl: int = 3600, 
                 key_generator: Optional[Callable] = None):
        self.cache_manager = cache_manager
        self.ttl = ttl
        self.key_generator = key_generator or self._default_key_generator
    
    def _default_key_generator(self, func: Callable, *args, **kwargs) -> str:
        """Gera chave padrão para cache"""
        # Hash dos argumentos
        args_str = str(args) + str(sorted(kwargs.items()))
        return f"{func.__module__}.{func.__name__}:{hashlib.md5(args_str.encode()).hexdigest()}"
    
    def __call__(self, func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = self.key_generator(func, *args, **kwargs)
            
            # Tentar obter do cache
            cached_value = await self.cache_manager.get(key)
            if cached_value is not None:
                return cached_value
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Armazenar no cache
            await self.cache_manager.set(key, result, self.ttl)
            
            return result
        
        return wrapper


class CacheInvalidator:
    """
    Sistema de invalidação de cache
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.invalidation_patterns: List[str] = []
    
    def add_pattern(self, pattern: str):
        """Adiciona padrão de invalidação"""
        self.invalidation_patterns.append(pattern)
    
    async def invalidate_by_pattern(self, pattern: str):
        """Invalida cache por padrão"""
        if self.cache_manager.redis_client:
            keys = await self.cache_manager.redis_client.keys(pattern)
            if keys:
                await self.cache_manager.redis_client.delete(*keys)
    
    async def invalidate_all(self):
        """Invalida todo o cache"""
        await self.cache_manager.clear()


class CacheAnalytics:
    """
    Analytics para cache
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.analytics_data: List[Dict[str, Any]] = []
    
    async def record_access(self, key: str, hit: bool, response_time: float):
        """Registra acesso ao cache"""
        data = {
            'key': key,
            'hit': hit,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.analytics_data.append(data)
        
        # Manter apenas últimos 1000 registros
        if len(self.analytics_data) > 1000:
            self.analytics_data = self.analytics_data[-1000:]
    
    def get_analytics(self) -> Dict[str, Any]:
        """Obtém analytics do cache"""
        if not self.analytics_data:
            return {}
        
        total_accesses = len(self.analytics_data)
        hits = sum(1 for data in self.analytics_data if data['hit'])
        misses = total_accesses - hits
        
        avg_response_time = sum(data['response_time'] for data in self.analytics_data) / total_accesses
        
        # Top keys acessadas
        key_counts = {}
        for data in self.analytics_data:
            key = data['key']
            key_counts[key] = key_counts.get(key, 0) + 1
        
        top_keys = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_accesses': total_accesses,
            'hits': hits,
            'misses': misses,
            'hit_rate': hits / total_accesses if total_accesses > 0 else 0,
            'avg_response_time': avg_response_time,
            'top_keys': top_keys
        }


# Funções utilitárias
def create_cache_manager(strategy: CacheStrategy = CacheStrategy.TTL, 
                        ttl: int = 3600, max_size: int = 1000) -> CacheManager:
    """Cria gerenciador de cache"""
    config = CacheConfig(
        strategy=strategy,
        ttl=ttl,
        max_size=max_size
    )
    return CacheManager(config)


def create_multi_level_cache() -> MultiLevelCache:
    """Cria cache multi-nível"""
    configs = {
        CacheLevel.MEMORY: CacheConfig(
            strategy=CacheStrategy.TTL,
            ttl=300,  # 5 minutos
            max_size=1000
        ),
        CacheLevel.REDIS: CacheConfig(
            strategy=CacheStrategy.TTL,
            ttl=3600,  # 1 hora
            max_size=10000
        )
    }
    return MultiLevelCache(configs)


# Instância global
_cache_manager: Optional[CacheManager] = None
_multi_level_cache: Optional[MultiLevelCache] = None


def get_cache_manager() -> CacheManager:
    """Obtém instância global do cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = create_cache_manager()
    return _cache_manager


def get_multi_level_cache() -> MultiLevelCache:
    """Obtém instância global do multi-level cache"""
    global _multi_level_cache
    if _multi_level_cache is None:
        _multi_level_cache = create_multi_level_cache()
    return _multi_level_cache


# Decorator simplificado
def cached(ttl: int = 3600, key_generator: Optional[Callable] = None):
    """Decorator simplificado para cache"""
    cache_manager = get_cache_manager()
    return CacheDecorator(cache_manager, ttl, key_generator) 