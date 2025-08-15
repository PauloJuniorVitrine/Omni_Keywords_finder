"""
Módulo de Gerenciamento de Memória para Sistemas Enterprise
Sistema de cache, garbage collection e otimização - Omni Keywords Finder

Prompt: Implementação de sistema de gerenciamento de memória enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import gc
import psutil
import time
import threading
import logging
import weakref
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict, defaultdict
import json
import pickle
import hashlib
from datetime import datetime, timedelta
import asyncio
import tracemalloc

logger = logging.getLogger(__name__)


class MemoryPolicy(Enum):
    """Políticas de gerenciamento de memória."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptativa baseada em uso


class CacheLevel(Enum):
    """Níveis de cache."""
    L1 = "l1"  # Cache mais rápido, menor
    L2 = "l2"  # Cache intermediário
    L3 = "l3"  # Cache mais lento, maior


@dataclass
class MemoryConfig:
    """Configuração de gerenciamento de memória."""
    max_memory_mb: int = 1024  # MB
    max_cache_size: int = 1000  # itens
    gc_threshold: float = 0.8  # 80% de uso
    cleanup_interval: int = 300  # segundos
    enable_monitoring: bool = True
    enable_compression: bool = False
    compression_threshold: int = 1024  # bytes
    cache_policy: MemoryPolicy = MemoryPolicy.LRU
    enable_persistence: bool = False
    persistence_path: str = "cache/"
    enable_stats: bool = True
    stats_interval: int = 60  # segundos

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.max_memory_mb <= 0:
            raise ValueError("Max memory deve ser positivo")
        if self.max_cache_size <= 0:
            raise ValueError("Max cache size deve ser positivo")
        if not 0 < self.gc_threshold < 1:
            raise ValueError("GC threshold deve estar entre 0 e 1")
        if self.cleanup_interval <= 0:
            raise ValueError("Cleanup interval deve ser positivo")
        if self.compression_threshold <= 0:
            raise ValueError("Compression threshold deve ser positivo")
        if self.stats_interval <= 0:
            raise ValueError("Stats interval deve ser positivo")


@dataclass
class CacheItem:
    """Item do cache."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[int] = None  # segundos
    compressed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Verifica se o item expirou."""
        if self.ttl is None:
            return False
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl

    def update_access(self) -> None:
        """Atualiza informações de acesso."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1

    def get_age(self) -> float:
        """Retorna idade do item em segundos."""
        return (datetime.utcnow() - self.created_at).total_seconds()

    def get_idle_time(self) -> float:
        """Retorna tempo ocioso em segundos."""
        return (datetime.utcnow() - self.accessed_at).total_seconds()


@dataclass
class MemoryStats:
    """Estatísticas de memória."""
    total_memory_mb: float = 0.0
    used_memory_mb: float = 0.0
    available_memory_mb: float = 0.0
    memory_percentage: float = 0.0
    cache_size: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0
    evictions: int = 0
    compressions: int = 0
    gc_runs: int = 0
    last_gc_time: Optional[datetime] = None
    last_cleanup_time: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def update_hit_rate(self) -> None:
        """Atualiza taxa de hit."""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            self.hit_rate = self.cache_hits / total_requests
        else:
            self.hit_rate = 0.0


class MemoryManager:
    """Gerenciador de memória enterprise."""
    
    def __init__(self, config: MemoryConfig = None):
        """
        Inicializa o gerenciador de memória.
        
        Args:
            config: Configuração do gerenciador
        """
        self.config = config or MemoryConfig()
        
        # Caches por nível
        self.caches: Dict[CacheLevel, Dict[str, CacheItem]] = {
            CacheLevel.L1: OrderedDict(),
            CacheLevel.L2: OrderedDict(),
            CacheLevel.L3: OrderedDict()
        }
        
        # Estatísticas
        self.stats = MemoryStats()
        
        # Controles
        self.running = False
        self.cleanup_thread = None
        self.stats_thread = None
        self.lock = threading.RLock()
        
        # Callbacks
        self.on_eviction: Optional[Callable[[str, Any], None]] = None
        self.on_compression: Optional[Callable[[str, int, int], None]] = None
        self.on_gc: Optional[Callable[[float], None]] = None
        
        # Inicializar monitoramento
        if self.config.enable_monitoring:
            tracemalloc.start()
        
        logger.info(f"MemoryManager inicializado - Max memory: {self.config.max_memory_mb}MB")
    
    def get(self, key: str, level: CacheLevel = CacheLevel.L1) -> Optional[Any]:
        """
        Obtém um item do cache.
        
        Args:
            key: Chave do item
            level: Nível do cache
            
        Returns:
            Valor do item ou None se não encontrado
        """
        with self.lock:
            cache = self.caches[level]
            
            if key in cache:
                item = cache[key]
                
                # Verificar expiração
                if item.is_expired():
                    del cache[key]
                    self.stats.cache_misses += 1
                    return None
                
                # Atualizar acesso
                item.update_access()
                
                # Mover para o final (LRU)
                if self.config.cache_policy == MemoryPolicy.LRU:
                    cache.move_to_end(key)
                
                self.stats.cache_hits += 1
                return item.value
            else:
                self.stats.cache_misses += 1
                return None
    
    def set(self, key: str, value: Any, level: CacheLevel = CacheLevel.L1,
            ttl: Optional[int] = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Define um item no cache.
        
        Args:
            key: Chave do item
            value: Valor do item
            level: Nível do cache
            ttl: Time to live em segundos
            metadata: Metadados adicionais
            
        Returns:
            True se definido com sucesso, False caso contrário
        """
        with self.lock:
            # Verificar limite de memória
            if not self._check_memory_limit():
                return False
            
            # Verificar limite do cache
            cache = self.caches[level]
            if len(cache) >= self.config.max_cache_size:
                self._evict_item(level)
            
            # Calcular tamanho
            size_bytes = self._calculate_size(value)
            
            # Comprimir se necessário
            compressed = False
            if (self.config.enable_compression and 
                size_bytes > self.config.compression_threshold):
                value = self._compress_value(value)
                compressed = True
                self.stats.compressions += 1
            
            # Criar item
            item = CacheItem(
                key=key,
                value=value,
                ttl=ttl,
                size_bytes=size_bytes,
                compressed=compressed,
                metadata=metadata or {}
            )
            
            # Adicionar ao cache
            cache[key] = item
            
            # Atualizar estatísticas
            self.stats.cache_size = sum(len(c) for c in self.caches.values())
            
            logger.debug(f"Item definido no cache: {key} (nível: {level.value})")
            return True
    
    def delete(self, key: str, level: CacheLevel = CacheLevel.L1) -> bool:
        """
        Remove um item do cache.
        
        Args:
            key: Chave do item
            level: Nível do cache
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        with self.lock:
            cache = self.caches[level]
            
            if key in cache:
                item = cache[key]
                del cache[key]
                
                # Atualizar estatísticas
                self.stats.cache_size = sum(len(c) for c in self.caches.values())
                
                logger.debug(f"Item removido do cache: {key} (nível: {level.value})")
                return True
            
            return False
    
    def clear(self, level: Optional[CacheLevel] = None) -> int:
        """
        Limpa o cache.
        
        Args:
            level: Nível específico ou None para todos
            
        Returns:
            Número de itens removidos
        """
        with self.lock:
            if level:
                cache = self.caches[level]
                count = len(cache)
                cache.clear()
                logger.info(f"Cache {level.value} limpo - {count} itens removidos")
            else:
                count = 0
                for level, cache in self.caches.items():
                    count += len(cache)
                    cache.clear()
                logger.info(f"Todos os caches limpos - {count} itens removidos")
            
            self.stats.cache_size = 0
            return count
    
    def exists(self, key: str, level: CacheLevel = CacheLevel.L1) -> bool:
        """
        Verifica se um item existe no cache.
        
        Args:
            key: Chave do item
            level: Nível do cache
            
        Returns:
            True se existe, False caso contrário
        """
        with self.lock:
            cache = self.caches[level]
            
            if key in cache:
                item = cache[key]
                if item.is_expired():
                    del cache[key]
                    return False
                return True
            
            return False
    
    def get_keys(self, level: CacheLevel = CacheLevel.L1) -> List[str]:
        """
        Obtém todas as chaves do cache.
        
        Args:
            level: Nível do cache
            
        Returns:
            Lista de chaves
        """
        with self.lock:
            cache = self.caches[level]
            return list(cache.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do gerenciador.
        
        Returns:
            Dicionário com estatísticas
        """
        with self.lock:
            # Atualizar estatísticas de memória do sistema
            self._update_system_memory()
            
            # Atualizar taxa de hit
            self.stats.update_hit_rate()
            
            return {
                "total_memory_mb": self.stats.total_memory_mb,
                "used_memory_mb": self.stats.used_memory_mb,
                "available_memory_mb": self.stats.available_memory_mb,
                "memory_percentage": self.stats.memory_percentage,
                "cache_size": self.stats.cache_size,
                "cache_hits": self.stats.cache_hits,
                "cache_misses": self.stats.cache_misses,
                "hit_rate": self.stats.hit_rate,
                "evictions": self.stats.evictions,
                "compressions": self.stats.compressions,
                "gc_runs": self.stats.gc_runs,
                "last_gc_time": self.stats.last_gc_time.isoformat() if self.stats.last_gc_time else None,
                "last_cleanup_time": self.stats.last_cleanup_time.isoformat() if self.stats.last_cleanup_time else None,
                "timestamp": self.stats.timestamp.isoformat(),
                "cache_levels": {
                    level.value: len(cache) for level, cache in self.caches.items()
                }
            }
    
    def start(self) -> None:
        """Inicia o gerenciador de memória."""
        if self.running:
            return
        
        self.running = True
        
        # Iniciar thread de limpeza
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        # Iniciar thread de estatísticas
        if self.config.enable_stats:
            self.stats_thread = threading.Thread(target=self._stats_loop, daemon=True)
            self.stats_thread.start()
        
        logger.info("MemoryManager iniciado")
    
    def stop(self) -> None:
        """Para o gerenciador de memória."""
        if not self.running:
            return
        
        self.running = False
        
        # Aguardar threads terminarem
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        
        if self.stats_thread:
            self.stats_thread.join(timeout=5)
        
        # Parar monitoramento
        if self.config.enable_monitoring:
            tracemalloc.stop()
        
        logger.info("MemoryManager parado")
    
    def force_gc(self) -> Dict[str, Any]:
        """
        Força execução do garbage collector.
        
        Returns:
            Estatísticas do GC
        """
        with self.lock:
            # Executar GC
            collected = gc.collect()
            
            # Atualizar estatísticas
            self.stats.gc_runs += 1
            self.stats.last_gc_time = datetime.utcnow()
            
            # Atualizar memória do sistema
            self._update_system_memory()
            
            result = {
                "collected_objects": collected,
                "memory_before": self.stats.used_memory_mb,
                "memory_after": self.stats.used_memory_mb,
                "timestamp": self.stats.last_gc_time.isoformat()
            }
            
            if self.on_gc:
                self.on_gc(self.stats.memory_percentage)
            
            logger.info(f"GC forçado - {collected} objetos coletados")
            return result
    
    def _check_memory_limit(self) -> bool:
        """Verifica se está dentro do limite de memória."""
        self._update_system_memory()
        
        if self.stats.memory_percentage > self.config.gc_threshold:
            # Executar GC automático
            self.force_gc()
            
            # Verificar novamente
            self._update_system_memory()
            if self.stats.memory_percentage > self.config.gc_threshold:
                logger.warning(f"Limite de memória excedido: {self.stats.memory_percentage:.2%}")
                return False
        
        return True
    
    def _evict_item(self, level: CacheLevel) -> None:
        """Remove um item do cache baseado na política."""
        cache = self.caches[level]
        
        if not cache:
            return
        
        if self.config.cache_policy == MemoryPolicy.LRU:
            # Remove o item menos recentemente usado
            key, item = cache.popitem(last=False)
        elif self.config.cache_policy == MemoryPolicy.LFU:
            # Remove o item menos frequentemente usado
            key = min(cache.keys(), key=lambda k: cache[k].access_count)
            item = cache.pop(key)
        elif self.config.cache_policy == MemoryPolicy.FIFO:
            # Remove o primeiro item
            key, item = cache.popitem(last=False)
        elif self.config.cache_policy == MemoryPolicy.TTL:
            # Remove o item mais antigo
            key = min(cache.keys(), key=lambda k: cache[k].created_at)
            item = cache.pop(key)
        else:  # ADAPTIVE
            # Combina LRU e LFU
            key = min(cache.keys(), 
                     key=lambda k: cache[k].access_count * cache[k].get_idle_time())
            item = cache.pop(key)
        
        self.stats.evictions += 1
        
        if self.on_eviction:
            self.on_eviction(key, item.value)
        
        logger.debug(f"Item evictado: {key} (nível: {level.value})")
    
    def _calculate_size(self, value: Any) -> int:
        """Calcula tamanho aproximado de um valor."""
        try:
            return len(pickle.dumps(value))
        except:
            return 1024  # Tamanho padrão
    
    def _compress_value(self, value: Any) -> Any:
        """Comprime um valor."""
        try:
            import zlib
            if isinstance(value, str):
                return zlib.compress(value.encode())
            elif isinstance(value, bytes):
                return zlib.compress(value)
            else:
                return zlib.compress(pickle.dumps(value))
        except:
            return value  # Retorna original se falhar
    
    def _decompress_value(self, value: Any) -> Any:
        """Descomprime um valor."""
        try:
            import zlib
            decompressed = zlib.decompress(value)
            try:
                return pickle.loads(decompressed)
            except:
                return decompressed.decode()
        except:
            return value  # Retorna original se falhar
    
    def _update_system_memory(self) -> None:
        """Atualiza estatísticas de memória do sistema."""
        try:
            memory = psutil.virtual_memory()
            self.stats.total_memory_mb = memory.total / (1024 * 1024)
            self.stats.used_memory_mb = memory.used / (1024 * 1024)
            self.stats.available_memory_mb = memory.available / (1024 * 1024)
            self.stats.memory_percentage = memory.percent / 100
        except:
            # Fallback se psutil não estiver disponível
            pass
    
    def _cleanup_loop(self) -> None:
        """Loop de limpeza automática."""
        while self.running:
            try:
                time.sleep(self.config.cleanup_interval)
                
                with self.lock:
                    # Remover itens expirados
                    for level, cache in self.caches.items():
                        expired_keys = [
                            key for key, item in cache.items() 
                            if item.is_expired()
                        ]
                        for key in expired_keys:
                            del cache[key]
                    
                    # Atualizar estatísticas
                    self.stats.cache_size = sum(len(c) for c in self.caches.values())
                    self.stats.last_cleanup_time = datetime.utcnow()
                    
                    logger.debug("Limpeza automática executada")
                
            except Exception as e:
                logger.error(f"Erro na limpeza automática: {e}")
    
    def _stats_loop(self) -> None:
        """Loop de atualização de estatísticas."""
        while self.running:
            try:
                time.sleep(self.config.stats_interval)
                
                with self.lock:
                    self._update_system_memory()
                    self.stats.update_hit_rate()
                    self.stats.timestamp = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Erro na atualização de estatísticas: {e}")


# Função de conveniência para criar memory manager
def create_memory_manager(config: MemoryConfig = None) -> MemoryManager:
    """
    Cria um gerenciador de memória com configurações padrão.
    
    Args:
        config: Configuração customizada
        
    Returns:
        Instância configurada do MemoryManager
    """
    return MemoryManager(config) 