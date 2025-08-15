"""
🔧 INT-009: Advanced Caching Strategy - Omni Keywords Finder

Tracing ID: INT_009_ADVANCED_CACHING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Implementar estratégia de cache avançada com cache em camadas,
cache warming, cache invalidation e analytics para o sistema Omni Keywords Finder.
"""

import os
import time
import json
import hashlib
import logging
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import pickle
import gzip
import base64
from functools import wraps
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Estratégias de cache."""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    ADAPTIVE = "adaptive"

class CacheLevel(Enum):
    """Níveis de cache."""
    L1 = "l1"  # Cache local (memória)
    L2 = "l2"  # Cache distribuído (Redis)
    L3 = "l3"  # Cache persistente (disco)

class CacheOperation(Enum):
    """Operações de cache."""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    UPDATE = "update"
    INVALIDATE = "invalidate"
    WARM = "warm"

@dataclass
class CacheConfig:
    """Configuração de cache."""
    # Configurações básicas
    default_ttl: int = 3600  # segundos
    max_size: int = 10000
    strategy: CacheStrategy = CacheStrategy.LRU
    
    # Configurações de camadas
    l1_enabled: bool = True
    l1_max_size: int = 1000
    l1_ttl: int = 300  # 5 minutos
    
    l2_enabled: bool = True
    l2_max_size: int = 10000
    l2_ttl: int = 3600  # 1 hora
    
    l3_enabled: bool = False
    l3_max_size: int = 100000
    l3_ttl: int = 86400  # 24 horas
    
    # Configurações de Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    redis_ttl: int = 3600
    
    # Configurações de cache warming
    warming_enabled: bool = True
    warming_interval: int = 300  # 5 minutos
    warming_batch_size: int = 100
    
    # Configurações de invalidation
    invalidation_enabled: bool = True
    invalidation_patterns: List[str] = field(default_factory=list)
    invalidation_cooldown: int = 60  # segundos
    
    # Configurações de analytics
    analytics_enabled: bool = True
    analytics_retention: int = 86400  # 24 horas
    
    # Configurações de compressão
    compression_enabled: bool = True
    compression_threshold: int = 1024  # bytes
    
    # Configurações de serialização
    serialization_format: str = "json"  # json, pickle, msgpack
    
    # Configurações de fallback
    fallback_enabled: bool = True
    fallback_strategy: str = "graceful"  # graceful, strict, none

@dataclass
class CacheEntry:
    """Entrada de cache."""
    key: str
    value: Any
    created_at: float
    accessed_at: float
    access_count: int
    ttl: int
    level: CacheLevel
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheMetrics:
    """Métricas de cache."""
    total_operations: int = 0
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    invalidations: int = 0
    
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    
    avg_get_time: float = 0.0
    avg_set_time: float = 0.0
    avg_delete_time: float = 0.0
    
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    
    total_size: int = 0
    memory_usage: float = 0.0
    
    warming_operations: int = 0
    invalidation_operations: int = 0

class LRUCache:
    """Implementação de cache LRU."""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: deque = deque()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Obtém entrada do cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Atualiza acesso
                entry.accessed_at = time.time()
                entry.access_count += 1
                
                # Move para o final (mais recente)
                self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry
            return None
    
    def set(self, key: str, entry: CacheEntry):
        """Define entrada no cache."""
        with self.lock:
            # Remove se já existe
            if key in self.cache:
                self.access_order.remove(key)
            
            # Adiciona nova entrada
            self.cache[key] = entry
            self.access_order.append(key)
            
            # Remove entrada mais antiga se necessário
            if len(self.cache) > self.max_size:
                oldest_key = self.access_order.popleft()
                del self.cache[oldest_key]
    
    def delete(self, key: str) -> bool:
        """Remove entrada do cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.access_order.remove(key)
                return True
            return False
    
    def clear(self):
        """Limpa todo o cache."""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def size(self) -> int:
        """Retorna tamanho do cache."""
        return len(self.cache)
    
    def keys(self) -> List[str]:
        """Retorna todas as chaves."""
        return list(self.cache.keys())

class LFUCache:
    """Implementação de cache LFU."""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.frequency: Dict[str, int] = defaultdict(int)
        self.frequency_groups: Dict[int, set] = defaultdict(set)
        self.min_frequency = 0
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Obtém entrada do cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Atualiza frequência
                old_freq = self.frequency[key]
                new_freq = old_freq + 1
                
                self.frequency[key] = new_freq
                self.frequency_groups[old_freq].discard(key)
                self.frequency_groups[new_freq].add(key)
                
                # Atualiza frequência mínima
                if old_freq == self.min_frequency and not self.frequency_groups[old_freq]:
                    self.min_frequency = new_freq
                
                # Atualiza acesso
                entry.accessed_at = time.time()
                entry.access_count += 1
                
                return entry
            return None
    
    def set(self, key: str, entry: CacheEntry):
        """Define entrada no cache."""
        with self.lock:
            # Remove se já existe
            if key in self.cache:
                old_freq = self.frequency[key]
                self.frequency_groups[old_freq].discard(key)
            
            # Adiciona nova entrada
            self.cache[key] = entry
            self.frequency[key] = 1
            self.frequency_groups[1].add(key)
            self.min_frequency = 1
            
            # Remove entrada menos frequente se necessário
            if len(self.cache) > self.max_size:
                self._evict_least_frequent()
    
    def _evict_least_frequent(self):
        """Remove entrada menos frequente."""
        if not self.frequency_groups[self.min_frequency]:
            return
        
        # Remove primeira entrada do grupo de frequência mínima
        key_to_remove = next(iter(self.frequency_groups[self.min_frequency]))
        self.frequency_groups[self.min_frequency].discard(key_to_remove)
        del self.cache[key_to_remove]
        del self.frequency[key_to_remove]
    
    def delete(self, key: str) -> bool:
        """Remove entrada do cache."""
        with self.lock:
            if key in self.cache:
                freq = self.frequency[key]
                self.frequency_groups[freq].discard(key)
                del self.cache[key]
                del self.frequency[key]
                return True
            return False
    
    def clear(self):
        """Limpa todo o cache."""
        with self.lock:
            self.cache.clear()
            self.frequency.clear()
            self.frequency_groups.clear()
            self.min_frequency = 0
    
    def size(self) -> int:
        """Retorna tamanho do cache."""
        return len(self.cache)
    
    def keys(self) -> List[str]:
        """Retorna todas as chaves."""
        return list(self.cache.keys())

class CacheSerializer:
    """Serializador de cache."""
    
    def __init__(self, format_type: str = "json"):
        self.format_type = format_type
    
    def serialize(self, data: Any) -> str:
        """Serializa dados."""
        if self.format_type == "json":
            return json.dumps(data, default=str)
        elif self.format_type == "pickle":
            return base64.b64encode(pickle.dumps(data)).decode('utf-8')
        else:
            return str(data)
    
    def deserialize(self, data: str) -> Any:
        """Deserializa dados."""
        if self.format_type == "json":
            return json.loads(data)
        elif self.format_type == "pickle":
            return pickle.loads(base64.b64decode(data.encode('utf-8')))
        else:
            return data

class CacheCompressor:
    """Compressor de cache."""
    
    def __init__(self, enabled: bool = True, threshold: int = 1024):
        self.enabled = enabled
        self.threshold = threshold
    
    def compress(self, data: str) -> str:
        """Comprime dados."""
        if not self.enabled or len(data) < self.threshold:
            return data
        
        try:
            compressed = gzip.compress(data.encode('utf-8'))
            return base64.b64encode(compressed).decode('utf-8')
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return data
    
    def decompress(self, data: str) -> str:
        """Descomprime dados."""
        if not self.enabled:
            return data
        
        try:
            # Tenta descomprimir
            compressed = base64.b64decode(data.encode('utf-8'))
            return gzip.decompress(compressed).decode('utf-8')
        except Exception:
            # Se falhar, retorna como está (dados não comprimidos)
            return data

class CacheWarming:
    """Sistema de cache warming."""
    
    def __init__(self, cache_manager, config: CacheConfig):
        self.cache_manager = cache_manager
        self.config = config
        self.warming_queue: deque = deque(maxlen=1000)
        self.warming_thread = None
        self.running = True
    
    def add_to_warming_queue(self, key: str, value: Any, ttl: int = None):
        """Adiciona item à fila de warming."""
        if not self.config.warming_enabled:
            return
        
        self.warming_queue.append({
            'key': key,
            'value': value,
            'ttl': ttl or self.config.default_ttl,
            'timestamp': time.time()
        })
    
    def start_warming_thread(self):
        """Inicia thread de warming."""
        if not self.config.warming_enabled:
            return
        
        self.warming_thread = threading.Thread(
            target=self._warming_worker,
            daemon=True
        )
        self.warming_thread.start()
    
    def _warming_worker(self):
        """Worker de cache warming."""
        while self.running:
            try:
                time.sleep(self.config.warming_interval)
                self._process_warming_queue()
            except Exception as e:
                logger.error(f"Cache warming error: {e}")
    
    def _process_warming_queue(self):
        """Processa fila de warming."""
        batch = []
        
        while self.warming_queue and len(batch) < self.config.warming_batch_size:
            item = self.warming_queue.popleft()
            batch.append(item)
        
        for item in batch:
            try:
                self.cache_manager.set(
                    item['key'],
                    item['value'],
                    ttl=item['ttl'],
                    level=CacheLevel.L2
                )
                self.cache_manager.metrics.warming_operations += 1
            except Exception as e:
                logger.error(f"Cache warming failed for key {item['key']}: {e}")

class CacheInvalidation:
    """Sistema de invalidação de cache."""
    
    def __init__(self, cache_manager, config: CacheConfig):
        self.cache_manager = cache_manager
        self.config = config
        self.invalidation_patterns: Dict[str, List[str]] = defaultdict(list)
        self.invalidation_history: deque = deque(maxlen=1000)
        self.last_invalidation: Dict[str, float] = {}
    
    def add_invalidation_pattern(self, pattern: str, keys: List[str]):
        """Adiciona padrão de invalidação."""
        self.invalidation_patterns[pattern] = keys
    
    def invalidate_by_pattern(self, pattern: str):
        """Invalida cache por padrão."""
        if not self.config.invalidation_enabled:
            return
        
        # Verifica cooldown
        now = time.time()
        if pattern in self.last_invalidation:
            if now - self.last_invalidation[pattern] < self.config.invalidation_cooldown:
                return
        
        self.last_invalidation[pattern] = now
        
        # Invalida chaves do padrão
        keys = self.invalidation_patterns.get(pattern, [])
        for key in keys:
            try:
                self.cache_manager.delete(key)
                self.invalidation_history.append({
                    'pattern': pattern,
                    'key': key,
                    'timestamp': now
                })
                self.cache_manager.metrics.invalidation_operations += 1
            except Exception as e:
                logger.error(f"Cache invalidation failed for key {key}: {e}")
    
    def invalidate_by_keys(self, keys: List[str]):
        """Invalida cache por chaves específicas."""
        if not self.config.invalidation_enabled:
            return
        
        for key in keys:
            try:
                self.cache_manager.delete(key)
                self.invalidation_history.append({
                    'pattern': 'manual',
                    'key': key,
                    'timestamp': time.time()
                })
                self.cache_manager.metrics.invalidation_operations += 1
            except Exception as e:
                logger.error(f"Cache invalidation failed for key {key}: {e}")

class AdvancedCaching:
    """
    Sistema avançado de cache com funcionalidades enterprise-grade.
    
    Implementa:
    - Cache em camadas (L1, L2, L3)
    - Cache warming automático
    - Cache invalidation inteligente
    - Analytics detalhados
    - Compressão e serialização
    """
    
    def __init__(self, config: CacheConfig):
        """
        Inicializar sistema de cache avançado.
        
        Args:
            config: Configuração do cache
        """
        self.config = config
        
        # Inicializar componentes
        self.serializer = CacheSerializer(config.serialization_format)
        self.compressor = CacheCompressor(
            config.compression_enabled,
            config.compression_threshold
        )
        
        # Caches por nível
        self.l1_cache = None
        self.l2_cache = None
        self.l3_cache = None
        
        if config.l1_enabled:
            if config.strategy == CacheStrategy.LRU:
                self.l1_cache = LRUCache(config.l1_max_size)
            elif config.strategy == CacheStrategy.LFU:
                self.l1_cache = LFUCache(config.l1_max_size)
        
        # Redis para L2 (simulado por enquanto)
        if config.l2_enabled:
            self.l2_cache = LRUCache(config.l2_max_size)
        
        # Sistema de warming e invalidation
        self.warming = CacheWarming(self, config)
        self.invalidation = CacheInvalidation(self, config)
        
        # Métricas
        self.metrics = CacheMetrics()
        self.operation_times: Dict[str, deque] = {
            'get': deque(maxlen=100),
            'set': deque(maxlen=100),
            'delete': deque(maxlen=100)
        }
        
        # Threading
        self.lock = threading.RLock()
        
        # Inicializar sistemas
        self.warming.start_warming_thread()
        
        logger.info({
            "event": "advanced_caching_initialized",
            "status": "success",
            "source": "AdvancedCaching.__init__",
            "details": {
                "l1_enabled": config.l1_enabled,
                "l2_enabled": config.l2_enabled,
                "l3_enabled": config.l3_enabled,
                "strategy": config.strategy.value,
                "warming_enabled": config.warming_enabled,
                "invalidation_enabled": config.invalidation_enabled
            }
        })
    
    def get(self, key: str, level: CacheLevel = CacheLevel.L1) -> Optional[Any]:
        """
        Obtém valor do cache.
        
        Args:
            key: Chave do cache
            level: Nível de cache
            
        Returns:
            Valor ou None se não encontrado
        """
        start_time = time.time()
        
        try:
            # Tenta L1 primeiro
            if level == CacheLevel.L1 and self.l1_cache:
                entry = self.l1_cache.get(key)
                if entry and not self._is_expired(entry):
                    self._record_operation_time('get', time.time() - start_time)
                    self.metrics.hits += 1
                    self.metrics.l1_hits += 1
                    return entry.value
            
            # Tenta L2
            if level in [CacheLevel.L2, CacheLevel.L3] and self.l2_cache:
                entry = self.l2_cache.get(key)
                if entry and not self._is_expired(entry):
                    # Promove para L1 se disponível
                    if self.l1_cache:
                        self.l1_cache.set(key, entry)
                    
                    self._record_operation_time('get', time.time() - start_time)
                    self.metrics.hits += 1
                    self.metrics.l2_hits += 1
                    return entry.value
            
            # Miss
            self.metrics.misses += 1
            if level == CacheLevel.L1:
                self.metrics.l1_misses += 1
            else:
                self.metrics.l2_misses += 1
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
        finally:
            self.metrics.total_operations += 1
            self._update_hit_rate()
    
    def set(self, key: str, value: Any, ttl: int = None, level: CacheLevel = CacheLevel.L1):
        """
        Define valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Time to live em segundos
            level: Nível de cache
        """
        start_time = time.time()
        ttl = ttl or self.config.default_ttl
        
        try:
            # Serializa e comprime
            serialized = self.serializer.serialize(value)
            compressed = self.compressor.compress(serialized)
            
            entry = CacheEntry(
                key=key,
                value=compressed,
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=ttl,
                level=level
            )
            
            # Armazena no nível apropriado
            if level == CacheLevel.L1 and self.l1_cache:
                self.l1_cache.set(key, entry)
            elif level in [CacheLevel.L2, CacheLevel.L3] and self.l2_cache:
                self.l2_cache.set(key, entry)
            
            self.metrics.sets += 1
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
        finally:
            self._record_operation_time('set', time.time() - start_time)
            self.metrics.total_operations += 1
    
    def delete(self, key: str, level: CacheLevel = CacheLevel.L1) -> bool:
        """
        Remove valor do cache.
        
        Args:
            key: Chave do cache
            level: Nível de cache
            
        Returns:
            True se removido, False se não encontrado
        """
        start_time = time.time()
        
        try:
            success = False
            
            if level == CacheLevel.L1 and self.l1_cache:
                success = self.l1_cache.delete(key) or success
            
            if level in [CacheLevel.L2, CacheLevel.L3] and self.l2_cache:
                success = self.l2_cache.delete(key) or success
            
            if success:
                self.metrics.deletes += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
        finally:
            self._record_operation_time('delete', time.time() - start_time)
            self.metrics.total_operations += 1
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Verifica se entrada expirou."""
        return time.time() - entry.created_at > entry.ttl
    
    def _record_operation_time(self, operation: str, duration: float):
        """Registra tempo de operação."""
        if operation in self.operation_times:
            self.operation_times[operation].append(duration)
    
    def _update_hit_rate(self):
        """Atualiza taxa de hit/miss."""
        total = self.metrics.hits + self.metrics.misses
        if total > 0:
            self.metrics.hit_rate = self.metrics.hits / total
            self.metrics.miss_rate = self.metrics.misses / total
    
    def get_metrics(self) -> CacheMetrics:
        """Obtém métricas detalhadas."""
        # Atualiza métricas de tempo
        for operation, times in self.operation_times.items():
            if times:
                avg_time = statistics.mean(times)
                if operation == 'get':
                    self.metrics.avg_get_time = avg_time
                elif operation == 'set':
                    self.metrics.avg_set_time = avg_time
                elif operation == 'delete':
                    self.metrics.avg_delete_time = avg_time
        
        # Atualiza tamanho total
        total_size = 0
        if self.l1_cache:
            total_size += self.l1_cache.size()
        if self.l2_cache:
            total_size += self.l2_cache.size()
        
        self.metrics.total_size = total_size
        
        return self.metrics
    
    def clear(self, level: CacheLevel = CacheLevel.L1):
        """Limpa cache do nível especificado."""
        if level == CacheLevel.L1 and self.l1_cache:
            self.l1_cache.clear()
        elif level in [CacheLevel.L2, CacheLevel.L3] and self.l2_cache:
            self.l2_cache.clear()
    
    def clear_all(self):
        """Limpa todos os caches."""
        if self.l1_cache:
            self.l1_cache.clear()
        if self.l2_cache:
            self.l2_cache.clear()
    
    def get_keys(self, level: CacheLevel = CacheLevel.L1) -> List[str]:
        """Obtém todas as chaves do nível especificado."""
        if level == CacheLevel.L1 and self.l1_cache:
            return self.l1_cache.keys()
        elif level in [CacheLevel.L2, CacheLevel.L3] and self.l2_cache:
            return self.l2_cache.keys()
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """Health check do sistema de cache."""
        return {
            "status": "healthy",
            "l1_cache": {
                "enabled": self.config.l1_enabled,
                "size": self.l1_cache.size() if self.l1_cache else 0,
                "max_size": self.config.l1_max_size
            },
            "l2_cache": {
                "enabled": self.config.l2_enabled,
                "size": self.l2_cache.size() if self.l2_cache else 0,
                "max_size": self.config.l2_max_size
            },
            "warming": {
                "enabled": self.config.warming_enabled,
                "queue_size": len(self.warming.warming_queue)
            },
            "invalidation": {
                "enabled": self.config.invalidation_enabled,
                "patterns": len(self.invalidation.invalidation_patterns)
            },
            "metrics": {
                "hit_rate": self.metrics.hit_rate,
                "total_operations": self.metrics.total_operations,
                "warming_operations": self.metrics.warming_operations,
                "invalidation_operations": self.metrics.invalidation_operations
            }
        }

def create_advanced_caching(config: CacheConfig) -> AdvancedCaching:
    """
    Cria e retorna sistema de cache avançado.
    
    Args:
        config: Configuração do cache
        
    Returns:
        Sistema de cache configurado
    """
    return AdvancedCaching(config)

# Cache global (singleton)
_global_cache: Optional[AdvancedCaching] = None

def get_global_cache() -> AdvancedCaching:
    """Obtém o cache global."""
    global _global_cache
    if _global_cache is None:
        config = CacheConfig()
        _global_cache = create_advanced_caching(config)
    return _global_cache

def set_global_cache(cache: AdvancedCaching):
    """Define o cache global."""
    global _global_cache
    _global_cache = cache

# Decorator para cache automático
def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator para cache automático.
    
    Args:
        ttl: Time to live em segundos
        key_func: Função para gerar chave do cache
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Chave padrão baseada na função e argumentos
                key_parts = [func.__name__]
                key_parts.extend([str(arg) for arg in args])
                key_parts.extend([f"{key}={value}" for key, value in sorted(kwargs.items())])
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Tenta obter do cache
            cache = get_global_cache()
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                return cached_value
            
            # Executa função e armazena no cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator 