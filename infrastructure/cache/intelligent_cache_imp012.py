#!/usr/bin/env python3
"""
🚀 IMP-012: Sistema de Cache Inteligente com TTL Dinâmico
🎯 Objetivo: Implementar cache inteligente com hit rate > 90%
📅 Criado: 2024-12-27
🔄 Versão: 1.0
"""

import os
import json
import time
import hashlib
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from collections import OrderedDict, defaultdict
from enum import Enum
import logging
import pickle
import gzip
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Níveis de cache."""
    L1 = "l1"  # Memória local (mais rápido)
    L2 = "l2"  # Redis (distribuído)
    L3 = "l3"  # Disco (persistente)

class EvictionPolicy(Enum):
    """Políticas de evição."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptativa baseada em padrões

@dataclass
class CacheItem:
    """Item do cache com metadados."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 1
    ttl: Optional[int] = None
    size: int = 0
    compression_ratio: float = 1.0
    hit_rate: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def is_expired(self) -> bool:
        """Verifica se o item expirou."""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def update_access(self):
        """Atualiza estatísticas de acesso."""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def calculate_size(self) -> int:
        """Calcula tamanho do item."""
        try:
            serialized = pickle.dumps(self.value)
            self.size = len(serialized)
            return self.size
        except Exception:
            self.size = len(str(self.value))
            return self.size
    
    def compress(self) -> bool:
        """Comprime o item se possível."""
        try:
            if self.size > 1024:  # Comprimir apenas itens grandes
                serialized = pickle.dumps(self.value)
                compressed = gzip.compress(serialized)
                if len(compressed) < self.size:
                    self.value = compressed
                    self.compression_ratio = len(compressed) / self.size
                    return True
        except Exception:
            pass
        return False
    
    def decompress(self) -> bool:
        """Descomprime o item se necessário."""
        try:
            if isinstance(self.value, bytes) and self.compression_ratio < 1.0:
                decompressed = gzip.decompress(self.value)
                self.value = pickle.loads(decompressed)
                return True
        except Exception:
            pass
        return False

@dataclass
class CacheMetrics:
    """Métricas do cache."""
    total_requests: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    avg_response_time: float = 0.0
    compression_savings: float = 0.0
    ttl_adaptations: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Taxa de hit do cache."""
        return self.hits / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Taxa de miss do cache."""
        return self.misses / self.total_requests if self.total_requests > 0 else 0.0

class AdaptiveTTLManager:
    """Gerenciador de TTL adaptativo."""
    
    def __init__(self):
        self.access_patterns = defaultdict(list)
        self.ttl_history = defaultdict(list)
        self.adaptation_threshold = 0.1  # 10% de variação
    
    def record_access(self, key: str, ttl: int, was_hit: bool):
        """Registra acesso para análise de padrões."""
        self.access_patterns[key].append({
            'timestamp': datetime.now(),
            'ttl': ttl,
            'was_hit': was_hit
        })
        
        # Manter apenas últimos 100 acessos
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-100:]
    
    def calculate_optimal_ttl(self, key: str, current_ttl: int) -> int:
        """Calcula TTL ótimo baseado em padrões de acesso."""
        if key not in self.access_patterns:
            return current_ttl
        
        accesses = self.access_patterns[key]
        if len(accesses) < 10:
            return current_ttl
        
        # Analisar padrões de acesso
        hit_rate = sum(1 for a in accesses if a['was_hit']) / len(accesses)
        avg_interval = self._calculate_access_interval(accesses)
        
        # Ajustar TTL baseado em padrões
        if hit_rate > 0.8 and avg_interval > current_ttl * 0.5:
            # Aumentar TTL se hit rate alto e intervalo grande
            new_ttl = min(current_ttl * 1.5, 86400)  # Máximo 24h
        elif hit_rate < 0.3 or avg_interval < current_ttl * 0.2:
            # Diminuir TTL se hit rate baixo ou intervalo pequeno
            new_ttl = max(current_ttl * 0.7, 60)  # Mínimo 1min
        else:
            new_ttl = current_ttl
        
        # Registrar adaptação
        self.ttl_history[key].append({
            'timestamp': datetime.now(),
            'old_ttl': current_ttl,
            'new_ttl': new_ttl,
            'hit_rate': hit_rate
        })
        
        return int(new_ttl)
    
    def _calculate_access_interval(self, accesses: List[Dict]) -> float:
        """Calcula intervalo médio entre acessos."""
        if len(accesses) < 2:
            return 0.0
        
        intervals = []
        for index in range(1, len(accesses)):
            interval = (accesses[index]['timestamp'] - accesses[index-1]['timestamp']).total_seconds()
            intervals.append(interval)
        
        return statistics.mean(intervals) if intervals else 0.0

class L1Cache:
    """Cache L1 em memória com política LRU."""
    
    def __init__(self, max_size: int = 1000, eviction_policy: EvictionPolicy = EvictionPolicy.LRU):
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.lock = threading.RLock()
        self.metrics = CacheMetrics()
    
    def get(self, key: str) -> Optional[CacheItem]:
        """Obtém item do cache L1."""
        with self.lock:
            self.metrics.total_requests += 1
            
            if key in self.cache:
                item = self.cache[key]
                if item.is_expired():
                    del self.cache[key]
                    self.metrics.misses += 1
                    return None
                
                # Atualizar acesso
                item.update_access()
                self.cache.move_to_end(key)  # LRU
                self.metrics.hits += 1
                return item
            
            self.metrics.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Define item no cache L1."""
        with self.lock:
            # Verificar se já existe
            if key in self.cache:
                del self.cache[key]
            
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
            
            # Calcular tamanho e comprimir se necessário
            item.calculate_size()
            if item.size > 1024:
                item.compress()
            
            # Verificar se precisa evictar
            if len(self.cache) >= self.max_size:
                self._evict_item()
            
            self.cache[key] = item
            self.metrics.memory_usage += item.size
            return True
    
    def _evict_item(self):
        """Evicta item baseado na política."""
        if not self.cache:
            return
        
        if self.eviction_policy == EvictionPolicy.LRU:
            # Remove item mais antigo (primeiro da OrderedDict)
            key_to_remove = next(iter(self.cache))
        elif self.eviction_policy == EvictionPolicy.LFU:
            # Remove item menos acessado
            key_to_remove = min(self.cache.keys(), 
                              key=lambda key: self.cache[key].access_count)
        elif self.eviction_policy == EvictionPolicy.FIFO:
            # Remove primeiro item inserido
            key_to_remove = next(iter(self.cache))
        elif self.eviction_policy == EvictionPolicy.TTL:
            # Remove item com menor TTL restante
            key_to_remove = min(self.cache.keys(),
                              key=lambda key: self.cache[key].ttl or float('inf'))
        else:  # ADAPTIVE
            # Remove baseado em score combinado
            key_to_remove = self._get_adaptive_eviction_key()
        
        removed_item = self.cache.pop(key_to_remove)
        self.metrics.memory_usage -= removed_item.size
        self.metrics.evictions += 1
    
    def _get_adaptive_eviction_key(self) -> str:
        """Calcula chave para evição adaptativa."""
        scores = {}
        now = datetime.now()
        
        for key, item in self.cache.items():
            # Score baseado em múltiplos fatores
            age_factor = (now - item.created_at).total_seconds() / 3600  # Horas
            access_factor = 1.0 / max(item.access_count, 1)
            ttl_factor = 1.0 / max(item.ttl or 3600, 1)
            
            scores[key] = age_factor * 0.4 + access_factor * 0.4 + ttl_factor * 0.2
        
        return min(scores.keys(), key=lambda key: scores[key])
    
    def delete(self, key: str) -> bool:
        """Remove item do cache L1."""
        with self.lock:
            if key in self.cache:
                removed_item = self.cache.pop(key)
                self.metrics.memory_usage -= removed_item.size
                return True
            return False
    
    def clear(self):
        """Limpa todo o cache L1."""
        with self.lock:
            self.cache.clear()
            self.metrics.memory_usage = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache L1."""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage': self.metrics.memory_usage,
                'hit_rate': self.metrics.hit_rate,
                'evictions': self.metrics.evictions,
                'eviction_policy': self.eviction_policy.value
            }

class L2Cache:
    """Cache L2 (Redis simulado para desenvolvimento)."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.metrics = CacheMetrics()
        
        logger.info(f"Cache L2 (Redis simulado) inicializado: {host}:{port}/{db}")
    
    def get(self, key: str) -> Optional[CacheItem]:
        """Obtém item do cache L2."""
        with self.lock:
            self.metrics.total_requests += 1
            
            if key in self.cache:
                item_data = self.cache[key]
                item = CacheItem(**item_data)
                
                if item.is_expired():
                    del self.cache[key]
                    self.metrics.misses += 1
                    return None
                
                # Descomprimir se necessário
                item.decompress()
                item.update_access()
                self.cache[key] = asdict(item)
                self.metrics.hits += 1
                return item
            
            self.metrics.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Define item no cache L2."""
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
            
            # Calcular tamanho e comprimir
            item.calculate_size()
            if item.size > 512:  # Comprimir itens médios e grandes
                item.compress()
            
            self.cache[key] = asdict(item)
            self.metrics.memory_usage += item.size
            return True
    
    def delete(self, key: str) -> bool:
        """Remove item do cache L2."""
        with self.lock:
            if key in self.cache:
                removed_item = self.cache.pop(key)
                self.metrics.memory_usage -= removed_item.get('size', 0)
                return True
            return False
    
    def clear(self):
        """Limpa todo o cache L2."""
        with self.lock:
            self.cache.clear()
            self.metrics.memory_usage = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache L2."""
        with self.lock:
            return {
                'size': len(self.cache),
                'memory_usage': self.metrics.memory_usage,
                'hit_rate': self.metrics.hit_rate,
                'compression_savings': self.metrics.compression_savings
            }

class IntelligentCacheSystem:
    """Sistema de cache inteligente multi-nível com TTL dinâmico."""
    
    def __init__(self, 
                 enable_l1: bool = True,
                 enable_l2: bool = True,
                 l1_max_size: int = 1000,
                 l1_eviction_policy: EvictionPolicy = EvictionPolicy.ADAPTIVE,
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 default_ttl: int = 3600,
                 enable_compression: bool = True,
                 enable_adaptive_ttl: bool = True):
        
        self.enable_l1 = enable_l1
        self.enable_l2 = enable_l2
        self.default_ttl = default_ttl
        self.enable_compression = enable_compression
        self.enable_adaptive_ttl = enable_adaptive_ttl
        
        # Inicializar caches
        self.l1_cache = L1Cache(l1_max_size, l1_eviction_policy) if enable_l1 else None
        self.l2_cache = L2Cache(redis_host, redis_port) if enable_l2 else None
        
        # Gerenciador de TTL adaptativo
        self.ttl_manager = AdaptiveTTLManager() if enable_adaptive_ttl else None
        
        # Métricas globais
        self.global_metrics = CacheMetrics()
        
        # Cache de padrões de acesso
        self.access_patterns = defaultdict(int)
        
        # Thread para limpeza periódica
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("Sistema de cache inteligente inicializado")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Gera chave única para cache."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor do cache multi-nível."""
        start_time = time.time()
        
        # Tentar L1 primeiro
        if self.l1_cache:
            item = self.l1_cache.get(key)
            if item:
                self._record_access(key, True)
                self.global_metrics.avg_response_time = (
                    self.global_metrics.avg_response_time + (time.time() - start_time)
                ) / 2
                return item.value
        
        # Tentar L2
        if self.l2_cache:
            item = self.l2_cache.get(key)
            if item:
                # Promover para L1
                if self.l1_cache:
                    self.l1_cache.set(key, item.value, item.ttl, item.metadata)
                
                self._record_access(key, True)
                self.global_metrics.avg_response_time = (
                    self.global_metrics.avg_response_time + (time.time() - start_time)
                ) / 2
                return item.value
        
        self._record_access(key, False)
        self.global_metrics.avg_response_time = (
            self.global_metrics.avg_response_time + (time.time() - start_time)
        ) / 2
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Define valor no cache multi-nível."""
        if ttl is None:
            ttl = self.default_ttl
        
        # Aplicar TTL adaptativo se habilitado
        if self.ttl_manager and self.enable_adaptive_ttl:
            optimal_ttl = self.ttl_manager.calculate_optimal_ttl(key, ttl)
            if optimal_ttl != ttl:
                ttl = optimal_ttl
                self.global_metrics.ttl_adaptations += 1
        
        success = True
        
        # Definir em L1
        if self.l1_cache:
            success &= self.l1_cache.set(key, value, ttl, metadata)
        
        # Definir em L2
        if self.l2_cache:
            success &= self.l2_cache.set(key, value, ttl, metadata)
        
        return success
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache multi-nível."""
        success = True
        
        if self.l1_cache:
            success &= self.l1_cache.delete(key)
        
        if self.l2_cache:
            success &= self.l2_cache.delete(key)
        
        return success
    
    def clear(self):
        """Limpa todo o cache."""
        if self.l1_cache:
            self.l1_cache.clear()
        
        if self.l2_cache:
            self.l2_cache.clear()
    
    def _record_access(self, key: str, was_hit: bool):
        """Registra acesso para análise de padrões."""
        self.access_patterns[key] += 1
        
        if self.ttl_manager:
            # Encontrar TTL atual
            current_ttl = self.default_ttl
            if self.l1_cache and key in self.l1_cache.cache:
                current_ttl = self.l1_cache.cache[key].ttl or self.default_ttl
            elif self.l2_cache and key in self.l2_cache.cache:
                current_ttl = self.l2_cache.cache[key].get('ttl', self.default_ttl)
            
            self.ttl_manager.record_access(key, current_ttl, was_hit)
    
    def _cleanup_expired(self):
        """Thread para limpeza periódica de itens expirados."""
        while True:
            try:
                # Limpar L1
                if self.l1_cache:
                    with self.l1_cache.lock:
                        expired_keys = [
                            key for key, item in self.l1_cache.cache.items()
                            if item.is_expired()
                        ]
                        for key in expired_keys:
                            self.l1_cache.delete(key)
                
                # Limpar L2
                if self.l2_cache:
                    with self.l2_cache.lock:
                        expired_keys = [
                            key for key, item_data in self.l2_cache.cache.items()
                            if CacheItem(**item_data).is_expired()
                        ]
                        for key in expired_keys:
                            self.l2_cache.delete(key)
                
                time.sleep(60)  # Limpar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na limpeza de cache: {e}")
                time.sleep(60)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do sistema."""
        stats = {
            'global': {
                'total_requests': self.global_metrics.total_requests,
                'avg_response_time': self.global_metrics.avg_response_time,
                'ttl_adaptations': self.global_metrics.ttl_adaptations,
                'compression_savings': self.global_metrics.compression_savings
            },
            'l1_cache': self.l1_cache.get_stats() if self.l1_cache else None,
            'l2_cache': self.l2_cache.get_stats() if self.l2_cache else None,
            'access_patterns': dict(self.access_patterns),
            'configuration': {
                'enable_l1': self.enable_l1,
                'enable_l2': self.enable_l2,
                'enable_compression': self.enable_compression,
                'enable_adaptive_ttl': self.enable_adaptive_ttl,
                'default_ttl': self.default_ttl
            }
        }
        
        # Calcular hit rate global
        total_hits = 0
        total_requests = 0
        
        if self.l1_cache:
            total_hits += self.l1_cache.metrics.hits
            total_requests += self.l1_cache.metrics.total_requests
        
        if self.l2_cache:
            total_hits += self.l2_cache.metrics.hits
            total_requests += self.l2_cache.metrics.total_requests
        
        stats['global']['hit_rate'] = total_hits / total_requests if total_requests > 0 else 0.0
        
        return stats

def cache_decorator(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator para cache automático."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Gerar chave única
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Tentar obter do cache
            cached_value = cache_system.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Executar função
            result = func(*args, **kwargs)
            
            # Armazenar no cache
            cache_system.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Instância global do sistema de cache
cache_system = IntelligentCacheSystem(
    enable_l1=True,
    enable_l2=True,
    l1_max_size=1000,
    l1_eviction_policy=EvictionPolicy.ADAPTIVE,
    enable_compression=True,
    enable_adaptive_ttl=True
)

# Exemplo de uso
if __name__ == "__main__":
    # Teste do sistema de cache
    print("🧪 Testando sistema de cache inteligente...")
    
    # Teste básico
    cache_system.set("test_key", "test_value", ttl=60)
    result = cache_system.get("test_key")
    print(f"✅ Teste básico: {result}")
    
    # Teste de compressão
    large_data = "value" * 10000
    cache_system.set("large_key", large_data, ttl=60)
    result = cache_system.get("large_key")
    print(f"✅ Teste de compressão: {len(result) if result else 0} caracteres")
    
    # Teste de TTL adaptativo
    for index in range(10):
        cache_system.get("test_key")  # Simular acessos frequentes
    
    # Obter estatísticas
    stats = cache_system.get_stats()
    print(f"📊 Estatísticas: {json.dumps(stats, indent=2, default=str)}")
    
    print("�� Teste concluído!") 