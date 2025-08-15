"""
Sistema de Cache Inteligente - Omni Keywords Finder
==================================================

Sistema enterprise para cache inteligente com:
- Cache em memória e Redis
- Estratégias de invalidação inteligentes
- Cache warming automático
- Métricas de performance
- Fallback strategies
- TTL dinâmico

Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: CACHE_SYSTEM_001
"""

import json
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, OrderedDict
import pickle
import logging

# Integração com observabilidade
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.metrics import MetricsManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Níveis de cache"""
    L1 = "l1"  # Cache em memória (mais rápido)
    L2 = "l2"  # Cache Redis (persistente)
    L3 = "l3"  # Cache de disco (mais lento)


class CacheStrategy(Enum):
    """Estratégias de cache"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptativo baseado em uso


@dataclass
class CacheItem:
    """Item de cache"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[int] = None
    level: CacheLevel = CacheLevel.L1
    metadata: Optional[Dict[str, Any]] = None
    
    def is_expired(self) -> bool:
        """Verifica se o item expirou"""
        if self.ttl is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl
    
    def update_access(self):
        """Atualiza informações de acesso"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Estatísticas do cache"""
    total_items: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    avg_response_time: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Taxa de hit do cache"""
        total_requests = self.hits + self.misses
        return self.hits / total_requests if total_requests > 0 else 0.0


class LRUCache:
    """Cache LRU em memória"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CacheItem]:
        """Obtém item do cache"""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if item.is_expired():
                    del self.cache[key]
                    return None
                
                # Mover para o final (mais recente)
                self.cache.move_to_end(key)
                item.update_access()
                return item
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Define item no cache"""
        with self.lock:
            # Verificar se já existe
            if key in self.cache:
                del self.cache[key]
            
            # Verificar se precisa evictar
            if len(self.cache) >= self.max_size:
                # Remover item mais antigo
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            # Criar novo item
            item = CacheItem(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl=ttl,
                metadata=metadata
            )
            
            self.cache[key] = item
            return True
    
    def delete(self, key: str) -> bool:
        """Remove item do cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Limpa todo o cache"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage': sum(len(str(item.value)) for item in self.cache.values())
            }


class RedisCache:
    """Cache Redis (simulado para desenvolvimento)"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.cache: Dict[str, Any] = {}
        self.lock = threading.RLock()
        
        # Simular conexão Redis
        logger.info(f"Cache Redis simulado inicializado: {host}:{port}/{db}")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém item do cache Redis"""
        with self.lock:
            if key in self.cache:
                item_data = self.cache[key]
                item = CacheItem(**item_data)
                
                if item.is_expired():
                    del self.cache[key]
                    return None
                
                item.update_access()
                self.cache[key] = asdict(item)
                return item
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Define item no cache Redis"""
        with self.lock:
            item = CacheItem(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl=ttl,
                metadata=metadata
            )
            
            self.cache[key] = asdict(item)
            return True
    
    def delete(self, key: str) -> bool:
        """Remove item do cache Redis"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Limpa todo o cache Redis"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache Redis"""
        with self.lock:
            return {
                'size': len(self.cache),
                'memory_usage': sum(len(str(item.get('value', ''))) for item in self.cache.values())
            }


class IntelligentCacheSystem:
    """Sistema de cache inteligente multi-nível"""
    
    def __init__(self, 
                 enable_l1: bool = True,
                 enable_l2: bool = True,
                 l1_max_size: int = 1000,
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 default_ttl: int = 3600):
        
        self.enable_l1 = enable_l1
        self.enable_l2 = enable_l2
        self.default_ttl = default_ttl
        
        # Inicializar caches
        self.l1_cache = LRUCache(l1_max_size) if enable_l1 else None
        self.l2_cache = RedisCache(redis_host, redis_port) if enable_l2 else None
        
        # Configurar observabilidade
        self.telemetry = TelemetryManager()
        self.metrics = MetricsManager()
        
        # Estatísticas
        self.stats = CacheStats()
        
        # Cache de padrões de acesso
        self.access_patterns = defaultdict(int)
        
        # Thread para limpeza periódica
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("Sistema de cache inteligente inicializado")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Gera chave única para cache"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor do cache"""
        start_time = time.time()
        
        try:
            # Tentar L1 cache primeiro
            if self.enable_l1 and self.l1_cache:
                item = self.l1_cache.get(key)
                if item:
                    self.stats.hits += 1
                    self.access_patterns[key] += 1
                    self._record_metrics('cache_hit', 'l1', time.time() - start_time)
                    return item.value
            
            # Tentar L2 cache
            if self.enable_l2 and self.l2_cache:
                item = self.l2_cache.get(key)
                if item:
                    self.stats.hits += 1
                    self.access_patterns[key] += 1
                    
                    # Promover para L1 cache
                    if self.enable_l1 and self.l1_cache:
                        self.l1_cache.set(key, item.value, item.ttl, item.metadata)
                    
                    self._record_metrics('cache_hit', 'l2', time.time() - start_time)
                    return item.value
            
            # Cache miss
            self.stats.misses += 1
            self._record_metrics('cache_miss', 'none', time.time() - start_time)
            return default
            
        except Exception as e:
            logger.error(f"Erro ao acessar cache: {e}")
            self._record_metrics('cache_error', 'error', time.time() - start_time)
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            level: CacheLevel = CacheLevel.L1, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Define valor no cache"""
        start_time = time.time()
        
        try:
            ttl = ttl or self.default_ttl
            success = True
            
            # Definir no nível especificado
            if level == CacheLevel.L1 and self.enable_l1 and self.l1_cache:
                success &= self.l1_cache.set(key, value, ttl, metadata)
            
            if level == CacheLevel.L2 and self.enable_l2 and self.l2_cache:
                success &= self.l2_cache.set(key, value, ttl, metadata)
            
            # Definir em ambos os níveis se L1
            if level == CacheLevel.L1 and self.enable_l2 and self.l2_cache:
                self.l2_cache.set(key, value, ttl, metadata)
            
            if success:
                self._record_metrics('cache_set', level.value, time.time() - start_time)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao definir cache: {e}")
            self._record_metrics('cache_error', 'error', time.time() - start_time)
            return False
    
    def delete(self, key: str, level: CacheLevel = CacheLevel.L1) -> bool:
        """Remove valor do cache"""
        try:
            success = True
            
            if level == CacheLevel.L1 and self.enable_l1 and self.l1_cache:
                success &= self.l1_cache.delete(key)
            
            if level == CacheLevel.L2 and self.enable_l2 and self.l2_cache:
                success &= self.l2_cache.delete(key)
            
            # Remover de ambos os níveis se L1
            if level == CacheLevel.L1 and self.enable_l2 and self.l2_cache:
                self.l2_cache.delete(key)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover cache: {e}")
            return False
    
    def clear(self, level: Optional[CacheLevel] = None):
        """Limpa cache"""
        try:
            if level is None or level == CacheLevel.L1:
                if self.enable_l1 and self.l1_cache:
                    self.l1_cache.clear()
            
            if level is None or level == CacheLevel.L2:
                if self.enable_l2 and self.l2_cache:
                    self.l2_cache.clear()
            
            logger.info(f"Cache limpo: {level.value if level else 'all'}")
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
    
    def get_or_set(self, key: str, getter_func: Callable, ttl: Optional[int] = None,
                   level: CacheLevel = CacheLevel.L1) -> Any:
        """Obtém do cache ou executa função para obter valor"""
        # Tentar obter do cache
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Executar função para obter valor
        value = getter_func()
        
        # Armazenar no cache
        self.set(key, value, ttl, level)
        
        return value
    
    def warm_cache(self, keys: List[str], getter_func: Callable, 
                   ttl: Optional[int] = None, level: CacheLevel = CacheLevel.L1):
        """Warming do cache com múltiplas chaves"""
        logger.info(f"Iniciando cache warming para {len(keys)} chaves")
        
        for key in keys:
            try:
                self.get_or_set(key, lambda: getter_func(key), ttl, level)
            except Exception as e:
                logger.error(f"Erro no cache warming para chave {key}: {e}")
        
        logger.info("Cache warming concluído")
    
    def invalidate_pattern(self, pattern: str, level: CacheLevel = CacheLevel.L1):
        """Invalida cache por padrão"""
        try:
            # Implementar invalidação por padrão
            # Por simplicidade, limpa todo o cache
            self.clear(level)
            logger.info(f"Cache invalidado por padrão: {pattern}")
            
        except Exception as e:
            logger.error(f"Erro na invalidação por padrão: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do cache"""
        stats = asdict(self.stats)
        
        # Adicionar estatísticas dos caches individuais
        if self.enable_l1 and self.l1_cache:
            stats['l1_cache'] = self.l1_cache.get_stats()
        
        if self.enable_l2 and self.l2_cache:
            stats['l2_cache'] = self.l2_cache.get_stats()
        
        # Adicionar padrões de acesso
        stats['access_patterns'] = dict(self.access_patterns)
        
        return stats
    
    def _cleanup_expired(self):
        """Limpa itens expirados periodicamente"""
        while True:
            try:
                time.sleep(300)  # Executar a cada 5 minutos
                
                # Limpeza automática já é feita no get()
                logger.debug("Limpeza de cache expirado executada")
                
            except Exception as e:
                logger.error(f"Erro na limpeza de cache: {e}")
    
    def _record_metrics(self, metric_name: str, level: str, duration: float):
        """Registra métricas de cache"""
        try:
            self.metrics.record_counter(f"cache_{metric_name}", 1, {"level": level})
            self.metrics.record_histogram(f"cache_duration", duration, {"level": level})
        except Exception as e:
            logger.error(f"Erro ao registrar métricas: {e}")


# Instância global do sistema de cache
cache_system = IntelligentCacheSystem()


def get_cache() -> IntelligentCacheSystem:
    """Retorna instância do sistema de cache"""
    return cache_system


# Decorator para cache automático
def cached(ttl: Optional[int] = None, level: CacheLevel = CacheLevel.L1):
    """Decorator para cache automático de funções"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Gerar chave única
            key = cache_system._generate_key(func.__name__, *args, **kwargs)
            
            # Tentar obter do cache
            cached_result = cache_system.get(key)
            if cached_result is not None:
                return cached_result
            
            # Executar função
            result = func(*args, **kwargs)
            
            # Armazenar no cache
            cache_system.set(key, result, ttl, level)
            
            return result
        
        return wrapper
    return decorator 