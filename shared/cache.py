"""
Sistema de cache distribuído com Redis e fallback local.
Implementa cache de alta performance com TTL configurável e métricas.
"""
import json
import pickle
import asyncio
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
import os
from functools import wraps
import hashlib

try:
    import redis.asyncio as redis
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    aioredis = None

from shared.logger import logger

class CacheConfig:
    """Configuração centralizada do cache."""
    
    # Configurações Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_SSL = os.getenv('REDIS_SSL', 'false').lower() == 'true'
    
    # Configurações de TTL
    TTL_DEFAULT = int(os.getenv('CACHE_TTL_DEFAULT', 3600))  # 1 hora
    TTL_KEYWORDS = int(os.getenv('CACHE_TTL_KEYWORDS', 86400))  # 24 horas
    TTL_METRICS = int(os.getenv('CACHE_TTL_METRICS', 43200))  # 12 horas
    TTL_TRENDS = int(os.getenv('CACHE_TTL_TRENDS', 21600))  # 6 horas
    
    # Configurações de fallback
    FALLBACK_ENABLED = os.getenv('CACHE_FALLBACK_ENABLED', 'true').lower() == 'true'
    FALLBACK_TTL = int(os.getenv('CACHE_FALLBACK_TTL', 300))  # 5 minutos
    
    # Configurações de performance
    MAX_MEMORY_MB = int(os.getenv('CACHE_MAX_MEMORY_MB', 100))
    COMPRESSION_THRESHOLD = int(os.getenv('CACHE_COMPRESSION_THRESHOLD', 1024))  # bytes

class LocalCache:
    """Cache local como fallback quando Redis não está disponível."""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache local."""
        async with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if datetime.now() < item['expires_at']:
                    return item['value']
                else:
                    del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Define valor no cache local."""
        async with self._lock:
            if len(self._cache) >= self._max_size:
                # Remove item mais antigo
                oldest_key = min(self._cache.keys(), 
                               key=lambda key: self._cache[key]['created_at'])
                del self._cache[oldest_key]
            
            self._cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=ttl)
            }
            return True
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache local."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self) -> bool:
        """Limpa todo o cache local."""
        async with self._lock:
            self._cache.clear()
            return True

class AsyncCache:
    """
    Cache distribuído assíncrono com Redis e fallback local.
    Implementa métricas, compressão e TTL configurável.
    """
    
    def __init__(self, namespace: str = "omni_keywords", config: Optional[CacheConfig] = None):
        self.namespace = namespace
        self.config = config or CacheConfig()
        self._redis_client: Optional[redis.Redis] = None
        self._local_cache = LocalCache() if self.config.FALLBACK_ENABLED else None
        self._metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        self._initialized = False
    
    async def _init_redis(self) -> bool:
        """Inicializa conexão com Redis."""
        if not REDIS_AVAILABLE:
            logger.warning({
                "event": "redis_not_available",
                "status": "warning",
                "source": "cache._init_redis",
                "details": {"fallback": "local_cache"}
            })
            return False
        
        try:
            self._redis_client = redis.Redis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB,
                password=self.config.REDIS_PASSWORD,
                ssl=self.config.REDIS_SSL,
                decode_responses=False,  # Para suportar pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Testa conexão
            await self._redis_client.ping()
            self._initialized = True
            
            logger.info({
                "event": "redis_connected",
                "status": "success",
                "source": "cache._init_redis",
                "details": {
                    "host": self.config.REDIS_HOST,
                    "port": self.config.REDIS_PORT,
                    "db": self.config.REDIS_DB
                }
            })
            return True
            
        except Exception as e:
            logger.error({
                "event": "redis_connection_failed",
                "status": "error",
                "source": "cache._init_redis",
                "details": {"error": str(e)}
            })
            return False
    
    def _get_full_key(self, key: str) -> str:
        """Gera chave completa com namespace."""
        return f"{self.namespace}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serializa valor para armazenamento."""
        try:
            # Tenta JSON primeiro (mais eficiente)
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                return json.dumps(value, ensure_ascii=False).encode('utf-8')
            else:
                # Fallback para pickle
                return pickle.dumps(value)
        except Exception as e:
            logger.error({
                "event": "serialization_error",
                "status": "error",
                "source": "cache._serialize_value",
                "details": {"error": str(e), "value_type": str(type(value))}
            })
            raise
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserializa valor do armazenamento."""
        try:
            # Tenta JSON primeiro
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback para pickle
                return pickle.loads(data)
        except Exception as e:
            logger.error({
                "event": "deserialization_error",
                "status": "error",
                "source": "cache._deserialize_value",
                "details": {"error": str(e)}
            })
            raise
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor do cache.
        
        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado
            
        Returns:
            Valor do cache ou default
        """
        full_key = self._get_full_key(key)
        
        # Tenta Redis primeiro
        if self._redis_client and self._initialized:
            try:
                data = await self._redis_client.get(full_key)
                if data is not None:
                    value = self._deserialize_value(data)
                    self._metrics['hits'] += 1
                    logger.debug({
                        "event": "cache_hit",
                        "status": "success",
                        "source": "cache.get",
                        "details": {"key": key, "namespace": self.namespace}
                    })
                    return value
                else:
                    self._metrics['misses'] += 1
            except Exception as e:
                self._metrics['errors'] += 1
                logger.warning({
                    "event": "redis_get_error",
                    "status": "warning",
                    "source": "cache.get",
                    "details": {"error": str(e), "key": key}
                })
        
        # Fallback para cache local
        if self._local_cache:
            try:
                value = await self._local_cache.get(full_key)
                if value is not None:
                    self._metrics['hits'] += 1
                    logger.debug({
                        "event": "cache_hit_local",
                        "status": "success",
                        "source": "cache.get",
                        "details": {"key": key, "fallback": True}
                    })
                    return value
                else:
                    self._metrics['misses'] += 1
            except Exception as e:
                self._metrics['errors'] += 1
                logger.error({
                    "event": "local_cache_error",
                    "status": "error",
                    "source": "cache.get",
                    "details": {"error": str(e), "key": key}
                })
        
        logger.debug({
            "event": "cache_miss",
            "status": "info",
            "source": "cache.get",
            "details": {"key": key, "namespace": self.namespace}
        })
        return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Define valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (None = TTL padrão)
            
        Returns:
            True se sucesso, False caso contrário
        """
        if ttl is None:
            ttl = self.config.TTL_DEFAULT
        
        full_key = self._get_full_key(key)
        serialized_value = self._serialize_value(value)
        
        success = False
        
        # Tenta Redis primeiro
        if self._redis_client and self._initialized:
            try:
                await self._redis_client.setex(full_key, ttl, serialized_value)
                self._metrics['sets'] += 1
                success = True
                logger.debug({
                    "event": "cache_set",
                    "status": "success",
                    "source": "cache.set",
                    "details": {"key": key, "ttl": ttl, "namespace": self.namespace}
                })
            except Exception as e:
                self._metrics['errors'] += 1
                logger.warning({
                    "event": "redis_set_error",
                    "status": "warning",
                    "source": "cache.set",
                    "details": {"error": str(e), "key": key}
                })
        
        # Fallback para cache local
        if self._local_cache and not success:
            try:
                await self._local_cache.set(full_key, value, ttl)
                self._metrics['sets'] += 1
                success = True
                logger.debug({
                    "event": "cache_set_local",
                    "status": "success",
                    "source": "cache.set",
                    "details": {"key": key, "ttl": ttl, "fallback": True}
                })
            except Exception as e:
                self._metrics['errors'] += 1
                logger.error({
                    "event": "local_cache_set_error",
                    "status": "error",
                    "source": "cache.set",
                    "details": {"error": str(e), "key": key}
                })
        
        return success
    
    async def delete(self, key: str) -> bool:
        """
        Remove valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            True se removido, False se não encontrado
        """
        full_key = self._get_full_key(key)
        deleted = False
        
        # Remove do Redis
        if self._redis_client and self._initialized:
            try:
                result = await self._redis_client.delete(full_key)
                if result > 0:
                    deleted = True
                    self._metrics['deletes'] += 1
            except Exception as e:
                self._metrics['errors'] += 1
                logger.warning({
                    "event": "redis_delete_error",
                    "status": "warning",
                    "source": "cache.delete",
                    "details": {"error": str(e), "key": key}
                })
        
        # Remove do cache local
        if self._local_cache:
            try:
                if await self._local_cache.delete(full_key):
                    deleted = True
                    self._metrics['deletes'] += 1
            except Exception as e:
                self._metrics['errors'] += 1
                logger.error({
                    "event": "local_cache_delete_error",
                    "status": "error",
                    "source": "cache.delete",
                    "details": {"error": str(e), "key": key}
                })
        
        return deleted
    
    async def clear(self) -> bool:
        """
        Limpa todo o cache do namespace.
        
        Returns:
            True se sucesso
        """
        success = False
        
        # Limpa Redis
        if self._redis_client and self._initialized:
            try:
                pattern = f"{self.namespace}:*"
                keys = await self._redis_client.keys(pattern)
                if keys:
                    await self._redis_client.delete(*keys)
                success = True
                logger.info({
                    "event": "cache_cleared",
                    "status": "success",
                    "source": "cache.clear",
                    "details": {"namespace": self.namespace, "keys_deleted": len(keys)}
                })
            except Exception as e:
                logger.error({
                    "event": "redis_clear_error",
                    "status": "error",
                    "source": "cache.clear",
                    "details": {"error": str(e)}
                })
        
        # Limpa cache local
        if self._local_cache:
            try:
                await self._local_cache.clear()
                success = True
            except Exception as e:
                logger.error({
                    "event": "local_cache_clear_error",
                    "status": "error",
                    "source": "cache.clear",
                    "details": {"error": str(e)}
                })
        
        return success
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas do cache.
        
        Returns:
            Dicionário com métricas
        """
        total_requests = self._metrics['hits'] + self._metrics['misses']
        hit_rate = (self._metrics['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._metrics,
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests,
            'redis_available': self._initialized,
            'fallback_enabled': self.config.FALLBACK_ENABLED,
            'namespace': self.namespace
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde do cache.
        
        Returns:
            Status de saúde
        """
        status = {
            'redis_connected': False,
            'local_cache_available': self._local_cache is not None,
            'overall_healthy': False
        }
        
        if self._redis_client and self._initialized:
            try:
                await self._redis_client.ping()
                status['redis_connected'] = True
            except Exception:
                pass
        
        status['overall_healthy'] = status['redis_connected'] or status['local_cache_available']
        
        return status

# Instância global do cache
_cache_instance: Optional[AsyncCache] = None

async def get_cache(namespace: str = "omni_keywords") -> AsyncCache:
    """
    Obtém instância global do cache.
    
    Args:
        namespace: Namespace do cache
        
    Returns:
        Instância do cache
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AsyncCache(namespace)
        await _cache_instance._init_redis()
    return _cache_instance

# Decorator para cache automático
def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator para cache automático de funções.
    
    Args:
        ttl: Tempo de vida do cache
        key_prefix: Prefixo para a chave do cache
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gera chave única baseada na função e argumentos
            func_name = func.__name__
            args_hash = hashlib.md5(
                f"{args}:{sorted(kwargs.items())}".encode()
            ).hexdigest()
            cache_key = f"{key_prefix}:{func_name}:{args_hash}"
            
            # Tenta obter do cache
            cache = await get_cache()
            cached_result = await cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Executa função e armazena resultado
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator 