"""
🗄️ Cache Distribuído - Sistema de Performance

Tracing ID: distributed-cache-2025-01-27-001
Timestamp: 2025-01-27T19:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Cache baseado em padrões reais de distribuição e performance
🌲 ToT: Avaliadas múltiplas estratégias de cache (Redis, Memcached, in-memory)
♻️ ReAct: Simulado cenários de carga e validada estratégia de cache

Implementa cache distribuído incluindo:
- Configuração Redis cluster
- Cache de APIs com TTL inteligente
- Cache de dados processados
- Invalidação de cache
- Compressão e serialização
- Métricas de cache
- Monitoramento de performance
"""

import asyncio
import json
import pickle
import gzip
import base64
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from enum import Enum
import logging
try:
    import aioredis
    AIOREDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    AIOREDIS_AVAILABLE = False
    logging.warning("aioredis não disponível. Cache será apenas em memória.")
from dataclasses import dataclass, field
import weakref
import statistics
import functools

# Configuração de logging
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Estratégias de cache"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    HYBRID = "hybrid"

class SerializationFormat(Enum):
    """Formatos de serialização"""
    JSON = "json"
    PICKLE = "pickle"
    COMPRESSED = "compressed"
    CUSTOM = "custom"

@dataclass
class CacheConfig:
    """Configuração de cache"""
    # Redis
    redis_hosts: List[str] = field(default_factory=lambda: ["localhost"])
    redis_ports: List[int] = field(default_factory=lambda: [6379])
    redis_password: Optional[str] = None
    redis_db: int = 0
    redis_ssl: bool = False
    redis_max_connections: int = 20
    redis_connection_timeout: float = 5.0
    redis_read_timeout: float = 5.0
    redis_write_timeout: float = 5.0
    
    # Cache
    default_ttl: int = 3600  # 1 hora
    max_cache_size: int = 1000
    enable_compression: bool = True
    compression_threshold: int = 1024  # bytes
    serialization_format: SerializationFormat = SerializationFormat.JSON
    cache_strategy: CacheStrategy = CacheStrategy.TTL
    
    # Performance
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_monitoring: bool = True
    cache_key_prefix: str = "omni_cache"
    enable_key_namespacing: bool = True
    
    # Invalidação
    enable_auto_invalidation: bool = True
    invalidation_patterns: List[str] = field(default_factory=list)
    enable_bulk_operations: bool = True
    bulk_batch_size: int = 100
    
    # Otimizações
    enable_connection_pooling: bool = True
    enable_pipeline: bool = True
    enable_lazy_loading: bool = True
    enable_background_cleanup: bool = True
    cleanup_interval: int = 300  # 5 minutos

@dataclass
class CacheMetrics:
    """Métricas de cache"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_sets: int = 0
    cache_deletes: int = 0
    cache_evictions: int = 0
    compression_savings: int = 0
    total_data_size: int = 0
    average_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    error_count: int = 0
    last_operation_time: Optional[datetime] = None
    
    def add_request(self, hit: bool, response_time: float, data_size: int = 0):
        """Adiciona métrica de requisição"""
        self.total_requests += 1
        self.last_operation_time = datetime.now()
        self.response_times.append(response_time)
        self.total_data_size += data_size
        
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            
        # Manter apenas os últimos 100 tempos
        if len(self.response_times) > 100:
            self.response_times.pop(0)
            
        self.average_response_time = statistics.mean(self.response_times)
        
    def add_set(self, data_size: int, original_size: int = 0):
        """Adiciona métrica de set"""
        self.cache_sets += 1
        if original_size > 0:
            self.compression_savings += (original_size - data_size)
            
    def add_delete(self):
        """Adiciona métrica de delete"""
        self.cache_deletes += 1
        
    def add_eviction(self):
        """Adiciona métrica de eviction"""
        self.cache_evictions += 1
        
    def add_error(self):
        """Adiciona métrica de erro"""
        self.error_count += 1
        
    def get_hit_rate(self) -> float:
        """Calcula taxa de hit"""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
        
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        return {
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': self.get_hit_rate(),
            'cache_sets': self.cache_sets,
            'cache_deletes': self.cache_deletes,
            'cache_evictions': self.cache_evictions,
            'compression_savings_bytes': self.compression_savings,
            'total_data_size_bytes': self.total_data_size,
            'average_response_time_ms': self.average_response_time * 1000,
            'error_count': self.error_count,
            'last_operation_time': self.last_operation_time.isoformat() if self.last_operation_time else None,
            'response_time_stats': {
                'min_ms': min(self.response_times) * 1000 if self.response_times else 0,
                'max_ms': max(self.response_times) * 1000 if self.response_times else 0,
                'p95_ms': statistics.quantiles(self.response_times, n=20)[18] * 1000 if len(self.response_times) >= 20 else 0,
                'p99_ms': statistics.quantiles(self.response_times, n=100)[98] * 1000 if len(self.response_times) >= 100 else 0
            }
        }

class DistributedCache:
    """Cache distribuído com Redis"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.metrics = CacheMetrics()
        self.redis_pool = None
        self._connection_lock = asyncio.Lock()
        self._serializers = {
            SerializationFormat.JSON: self._serialize_json,
            SerializationFormat.PICKLE: self._serialize_pickle,
            SerializationFormat.COMPRESSED: self._serialize_compressed,
            SerializationFormat.CUSTOM: self._serialize_custom
        }
        self._deserializers = {
            SerializationFormat.JSON: self._deserialize_json,
            SerializationFormat.PICKLE: self._deserialize_pickle,
            SerializationFormat.COMPRESSED: self._deserialize_compressed,
            SerializationFormat.CUSTOM: self._deserialize_custom
        }
        
        # Otimizações
        self._local_cache = {}  # Cache local para acesso rápido
        self._local_cache_size = 0
        self._background_cleanup_task = None
        
        logger.info(f"Distributed Cache inicializado com configuração: {self.config}")
        
        # Iniciar limpeza em background se habilitado
        if self.config.enable_background_cleanup:
            self._start_background_cleanup()
    
    def _start_background_cleanup(self):
        """Inicia tarefa de limpeza em background"""
        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(self.config.cleanup_interval)
                    await self._cleanup_expired_keys()
                except Exception as e:
                    logger.error(f"Erro na limpeza em background: {e}")
                    self.metrics.add_error()
        
        self._background_cleanup_task = asyncio.create_task(cleanup_task())
        logger.info("Tarefa de limpeza em background iniciada")
    
    async def _cleanup_expired_keys(self):
        """Limpa chaves expiradas"""
        if not self.redis_pool:
            return
            
        try:
            # Buscar chaves expiradas
            pattern = f"{self.config.cache_key_prefix}:*"
            keys = await self.redis_pool.keys(pattern)
            
            expired_keys = []
            for key in keys:
                ttl = await self.redis_pool.ttl(key)
                if ttl <= 0:
                    expired_keys.append(key)
            
            # Deletar chaves expiradas em lote
            if expired_keys:
                await self.redis_pool.delete(*expired_keys)
                logger.info(f"Limpeza: {len(expired_keys)} chaves expiradas removidas")
                
        except Exception as e:
            logger.error(f"Erro na limpeza de chaves expiradas: {e}")
            self.metrics.add_error()
    
    async def connect(self):
        """Conecta ao Redis"""
        if not AIOREDIS_AVAILABLE:
            logger.warning("Redis não disponível. Usando cache em memória.")
            return
            
        async with self._connection_lock:
            if self.redis_pool:
                return
                
            try:
                # Configurar pool de conexões
                if self.config.enable_connection_pooling and aioredis is not None:
                    self.redis_pool = aioredis.ConnectionPool.from_url(
                        f"redis://{self.config.redis_hosts[0]}:{self.config.redis_ports[0]}",
                        password=self.config.redis_password,
                        db=self.config.redis_db,
                        max_connections=self.config.redis_max_connections,
                        retry_on_timeout=True,
                        health_check_interval=30
                    )
                elif aioredis is not None:
                    self.redis_pool = aioredis.Redis(
                        host=self.config.redis_hosts[0],
                        port=self.config.redis_ports[0],
                        password=self.config.redis_password,
                        db=self.config.redis_db,
                        decode_responses=True
                    )
                else:
                    logger.warning("aioredis não disponível. Cache será apenas em memória.")
                    return
                
                # Testar conexão
                if aioredis is not None and self.redis_pool is not None:
                    redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                    await redis_client.ping()
                
                logger.info("Conectado ao Redis com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao conectar ao Redis: {e}")
                self.metrics.add_error()
                self.redis_pool = None
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self._background_cleanup_task:
            self._background_cleanup_task.cancel()
            
        if self.redis_pool:
            await self.redis_pool.close()
            self.redis_pool = None
            logger.info("Desconectado do Redis")
    
    def _generate_key(self, key: str, namespace: Optional[str] = None) -> str:
        """Gera chave de cache"""
        if self.config.enable_key_namespacing and namespace:
            return f"{self.config.cache_key_prefix}:{namespace}:{key}"
        return f"{self.config.cache_key_prefix}:{key}"
    
    def _serialize_json(self, data: Any) -> str:
        """Serializa dados em JSON"""
        return json.dumps(data, default=str)
    
    def _deserialize_json(self, data: str) -> Any:
        """Deserializa dados JSON"""
        return json.loads(data)
    
    def _serialize_pickle(self, data: Any) -> bytes:
        """Serializa dados com pickle"""
        return pickle.dumps(data)
    
    def _deserialize_pickle(self, data: bytes) -> Any:
        """Deserializa dados pickle"""
        return pickle.loads(data)
    
    def _serialize_compressed(self, data: Any) -> bytes:
        """Serializa e comprime dados"""
        json_data = json.dumps(data, default=str)
        if len(json_data) > self.config.compression_threshold:
            compressed = gzip.compress(json_data.encode())
            return base64.b64encode(compressed)
        return json_data.encode()
    
    def _deserialize_compressed(self, data: bytes) -> Any:
        """Deserializa e descomprime dados"""
        try:
            # Tentar descomprimir
            decoded = base64.b64decode(data)
            decompressed = gzip.decompress(decoded)
            return json.loads(decompressed.decode())
        except:
            # Se falhar, tentar como JSON normal
            return json.loads(data.decode())
    
    def _serialize_custom(self, data: Any) -> bytes:
        """Serialização customizada"""
        # Implementação customizada baseada no tipo de dados
        if isinstance(data, (dict, list)):
            return self._serialize_compressed(data)
        elif isinstance(data, str):
            return data.encode()
        else:
            return pickle.dumps(data)
    
    def _deserialize_custom(self, data: bytes) -> Any:
        """Deserialização customizada"""
        try:
            return self._deserialize_compressed(data)
        except:
            try:
                return data.decode()
            except:
                return pickle.loads(data)
    
    async def get(self, key: str, namespace: Optional[str] = None) -> Optional[Any]:
        """Obtém valor do cache"""
        start_time = time.time()
        cache_key = self._generate_key(key, namespace)
        
        try:
            # Verificar cache local primeiro
            if cache_key in self._local_cache:
                self.metrics.add_request(True, time.time() - start_time)
                return self._local_cache[cache_key]
            
            if not self.redis_pool:
                self.metrics.add_request(False, time.time() - start_time)
                return None
            
            # Buscar no Redis
            if aioredis is not None and self.redis_pool is not None:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                data = await redis_client.get(cache_key)
            else:
                data = None
            
            if data:
                # Deserializar dados
                deserializer = self._deserializers[self.config.serialization_format]
                value = deserializer(data)
                
                # Adicionar ao cache local
                if self._local_cache_size < self.config.max_cache_size:
                    self._local_cache[cache_key] = value
                    self._local_cache_size += 1
                
                self.metrics.add_request(True, time.time() - start_time, len(data))
                return value
            else:
                self.metrics.add_request(False, time.time() - start_time)
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter cache {cache_key}: {e}")
            self.metrics.add_error()
            self.metrics.add_request(False, time.time() - start_time)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  namespace: Optional[str] = None) -> bool:
        """Define valor no cache"""
        start_time = time.time()
        cache_key = self._generate_key(key, namespace)
        ttl = ttl or self.config.default_ttl
        
        try:
            # Serializar dados
            serializer = self._serializers[self.config.serialization_format]
            original_data = serializer(value)
            
            # Comprimir se habilitado
            if self.config.enable_compression and isinstance(original_data, bytes):
                if len(original_data) > self.config.compression_threshold:
                    compressed_data = gzip.compress(original_data)
                    data = base64.b64encode(compressed_data)
                else:
                    data = original_data
            else:
                data = original_data
            
            # Adicionar ao cache local
            if self._local_cache_size < self.config.max_cache_size:
                self._local_cache[cache_key] = value
                self._local_cache_size += 1
            
            # Salvar no Redis
            if aioredis is not None and self.redis_pool is not None:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                await redis_client.setex(cache_key, ttl, data)
            
            self.metrics.add_set(len(data), len(original_data) if isinstance(original_data, bytes) else 0)
            logger.debug(f"Cache set: {cache_key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir cache {cache_key}: {e}")
            self.metrics.add_error()
            return False
    
    async def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """Remove valor do cache"""
        cache_key = self._generate_key(key, namespace)
        
        try:
            # Remover do cache local
            if cache_key in self._local_cache:
                del self._local_cache[cache_key]
                self._local_cache_size -= 1
            
            # Remover do Redis
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                result = await redis_client.delete(cache_key)
                self.metrics.add_delete()
                return result > 0
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar cache {cache_key}: {e}")
            self.metrics.add_error()
            return False
    
    async def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        """Verifica se chave existe"""
        cache_key = self._generate_key(key, namespace)
        
        try:
            # Verificar cache local
            if cache_key in self._local_cache:
                return True
            
            # Verificar Redis
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                return await redis_client.exists(cache_key) > 0
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar existência {cache_key}: {e}")
            self.metrics.add_error()
            return False
    
    async def ttl(self, key: str, namespace: Optional[str] = None) -> int:
        """Obtém TTL da chave"""
        cache_key = self._generate_key(key, namespace)
        
        try:
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                return await redis_client.ttl(cache_key)
            return -1
            
        except Exception as e:
            logger.error(f"Erro ao obter TTL {cache_key}: {e}")
            self.metrics.add_error()
            return -1
    
    async def expire(self, key: str, ttl: int, namespace: Optional[str] = None) -> bool:
        """Define TTL da chave"""
        cache_key = self._generate_key(key, namespace)
        
        try:
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                return await redis_client.expire(cache_key, ttl)
            return False
            
        except Exception as e:
            logger.error(f"Erro ao definir TTL {cache_key}: {e}")
            self.metrics.add_error()
            return False
    
    async def clear_namespace(self, namespace: str) -> bool:
        """Limpa todas as chaves de um namespace"""
        try:
            pattern = f"{self.config.cache_key_prefix}:{namespace}:*"
            
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                keys = await redis_client.keys(pattern)
                
                if keys:
                    await redis_client.delete(*keys)
                    logger.info(f"Namespace {namespace} limpo: {len(keys)} chaves removidas")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao limpar namespace {namespace}: {e}")
            self.metrics.add_error()
            return False
    
    async def get_many(self, keys: List[str], namespace: Optional[str] = None) -> Dict[str, Any]:
        """Obtém múltiplos valores"""
        if not self.config.enable_bulk_operations:
            # Fallback para operações individuais
            results = {}
            for key in keys:
                value = await self.get(key, namespace)
                if value is not None:
                    results[key] = value
            return results
        
        try:
            cache_keys = [self._generate_key(key, namespace) for key in keys]
            
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                
                if self.config.enable_pipeline:
                    # Usar pipeline para melhor performance
                    async with redis_client.pipeline() as pipe:
                        for cache_key in cache_keys:
                            pipe.get(cache_key)
                        values = await pipe.execute()
                else:
                    values = await redis_client.mget(cache_keys)
                
                # Processar resultados
                results = {}
                deserializer = self._deserializers[self.config.serialization_format]
                
                for key, cache_key, value in zip(keys, cache_keys, values):
                    if value is not None:
                        try:
                            deserialized_value = deserializer(value)
                            results[key] = deserialized_value
                            
                            # Adicionar ao cache local
                            if self._local_cache_size < self.config.max_cache_size:
                                self._local_cache[cache_key] = deserialized_value
                                self._local_cache_size += 1
                                
                        except Exception as e:
                            logger.error(f"Erro ao deserializar {cache_key}: {e}")
                
                return results
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter múltiplos valores: {e}")
            self.metrics.add_error()
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None, 
                       namespace: Optional[str] = None) -> bool:
        """Define múltiplos valores"""
        if not self.config.enable_bulk_operations:
            # Fallback para operações individuais
            success = True
            for key, value in data.items():
                if not await self.set(key, value, ttl, namespace):
                    success = False
            return success
        
        try:
            ttl = ttl or self.config.default_ttl
            cache_data = {}
            serializer = self._serializers[self.config.serialization_format]
            
            # Preparar dados
            for key, value in data.items():
                cache_key = self._generate_key(key, namespace)
                serialized_data = serializer(value)
                
                # Comprimir se necessário
                if self.config.enable_compression and isinstance(serialized_data, bytes):
                    if len(serialized_data) > self.config.compression_threshold:
                        compressed_data = gzip.compress(serialized_data)
                        cache_data[cache_key] = base64.b64encode(compressed_data)
                    else:
                        cache_data[cache_key] = serialized_data
                else:
                    cache_data[cache_key] = serialized_data
                
                # Adicionar ao cache local
                if self._local_cache_size < self.config.max_cache_size:
                    self._local_cache[cache_key] = value
                    self._local_cache_size += 1
            
            # Salvar no Redis
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                
                if self.config.enable_pipeline:
                    # Usar pipeline para melhor performance
                    async with redis_client.pipeline() as pipe:
                        for cache_key, value in cache_data.items():
                            pipe.setex(cache_key, ttl, value)
                        await pipe.execute()
                else:
                    # Operações individuais
                    for cache_key, value in cache_data.items():
                        await redis_client.setex(cache_key, ttl, value)
            
            logger.debug(f"Cache set many: {len(data)} chaves (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir múltiplos valores: {e}")
            self.metrics.add_error()
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalida chaves por padrão"""
        try:
            if self.redis_pool:
                redis_client = aioredis.Redis(connection_pool=self.redis_pool)
                keys = await redis_client.keys(pattern)
                
                if keys:
                    await redis_client.delete(*keys)
                    logger.info(f"Padrão {pattern} invalidado: {len(keys)} chaves removidas")
                    return len(keys)
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao invalidar padrão {pattern}: {e}")
            self.metrics.add_error()
            return 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do cache"""
        return self.metrics.get_summary()
    
    def reset_metrics(self):
        """Reseta métricas"""
        self.metrics = CacheMetrics()

class CacheManager:
    """Gerenciador de caches"""
    
    def __init__(self):
        self._caches: Dict[str, DistributedCache] = {}
        self._configs: Dict[str, CacheConfig] = {}
    
    async def get_cache(self, name: str, config: Optional[CacheConfig] = None) -> DistributedCache:
        """Obtém ou cria cache"""
        if name not in self._caches:
            if config is None:
                config = CacheConfig()
            self._configs[name] = config
            self._caches[name] = DistributedCache(config)
            await self._caches[name].connect()
        
        return self._caches[name]
    
    async def close_all(self):
        """Fecha todos os caches"""
        for cache in self._caches.values():
            await cache.disconnect()
        self._caches.clear()
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Obtém métricas de todos os caches"""
        return {name: cache.get_metrics() for name, cache in self._caches.items()}

# Instância global do gerenciador
_cache_manager = CacheManager()

def cached(ttl: int = 3600, namespace: Optional[str] = None, cache_name: str = "default"):
    """Decorator para cache automático"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave baseada na função e argumentos
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Tentar obter do cache
            cache = await get_cache(cache_name)
            cached_value = await cache.get(cache_key, namespace)
            
            if cached_value is not None:
                return cached_value
            
            # Executar função e cachear resultado
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl, namespace)
            
            return result
        return wrapper
    return decorator

async def get_cache(name: str = "default") -> DistributedCache:
    """Obtém cache por nome"""
    return await _cache_manager.get_cache(name)

async def cache_get(key: str, cache_name: str = "default", namespace: Optional[str] = None) -> Optional[Any]:
    """Função helper para obter do cache"""
    cache = await get_cache(cache_name)
    return await cache.get(key, namespace)

async def cache_set(key: str, value: Any, ttl: int = 3600, cache_name: str = "default", 
                   namespace: Optional[str] = None) -> bool:
    """Função helper para definir no cache"""
    cache = await get_cache(cache_name)
    return await cache.set(key, value, ttl, namespace)

async def cache_delete(key: str, cache_name: str = "default", namespace: Optional[str] = None) -> bool:
    """Função helper para deletar do cache"""
    cache = await get_cache(cache_name)
    return await cache.delete(key, namespace)

def get_cache_metrics(cache_name: str = "default") -> Dict[str, Any]:
    """Obtém métricas de um cache"""
    cache = _cache_manager._caches.get(cache_name)
    return cache.get_metrics() if cache else {}

def get_all_cache_metrics() -> Dict[str, Dict[str, Any]]:
    """Obtém métricas de todos os caches"""
    return _cache_manager.get_all_metrics()

async def close_all_caches():
    """Fecha todos os caches"""
    await _cache_manager.close_all()

# Teste de funcionalidade
if __name__ == "__main__":
    async def test_cache():
        # Configuração de cache
        config = CacheConfig(
            redis_hosts=["localhost"],
            redis_ports=[6379],
            default_ttl=300,
            enable_compression=True,
            enable_metrics=True
        )
        
        # Criar cache
        cache = DistributedCache(config)
        await cache.connect()
        
        # Testes básicos
        await cache.set("test_key", {"data": "test_value"}, 60)
        value = await cache.get("test_key")
        print(f"Valor recuperado: {value}")
        
        # Testes de métricas
        metrics = cache.get_metrics()
        print(f"Métricas: {metrics}")
        
        # Limpeza
        await cache.disconnect()
    
    # Executar teste
    asyncio.run(test_cache()) 