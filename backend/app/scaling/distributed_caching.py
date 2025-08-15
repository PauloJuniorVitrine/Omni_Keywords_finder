"""
Sistema de Cache Distribuído
Melhora performance em múltiplos servidores através de cache distribuído
"""

import asyncio
import time
import json
import hashlib
import pickle
import gzip
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import socket
import threading
from functools import wraps

import redis.asyncio as redis
import aioredis
from cachetools import TTLCache, LRUCache

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    LRU = "lru"
    TTL = "ttl"
    LFU = "lfu"
    CONSISTENT_HASH = "consistent_hash"


class CacheNode:
    """
    Nó de cache individual
    """
    
    def __init__(self, node_id: str, host: str, port: int, weight: int = 1):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.weight = weight
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
        self.last_heartbeat = None
        self.error_count = 0
        self.response_time = 0.0
    
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis_client = redis.from_url(f"redis://{self.host}:{self.port}")
            await self.redis_client.ping()
            self.is_connected = True
            self.last_heartbeat = datetime.now()
            self.error_count = 0
            logger.info(f"Connected to cache node: {self.node_id}")
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            logger.error(f"Failed to connect to cache node {self.node_id}: {e}")
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if not self.is_connected:
            return None
        
        try:
            start_time = time.time()
            value = await self.redis_client.get(key)
            self.response_time = time.time() - start_time
            
            if value:
                return self._deserialize_value(value)
            return None
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error getting from cache node {self.node_id}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        if not self.is_connected:
            return False
        
        try:
            start_time = time.time()
            serialized_value = self._serialize_value(value)
            
            if ttl:
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)
            
            self.response_time = time.time() - start_time
            return True
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error setting in cache node {self.node_id}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error deleting from cache node {self.node_id}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Limpa cache"""
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error clearing cache node {self.node_id}: {e}")
            return False
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serializa valor"""
        try:
            data = pickle.dumps(value)
            return gzip.compress(data)
        except Exception:
            return str(value).encode('utf-8')
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserializa valor"""
        try:
            decompressed = gzip.decompress(data)
            return pickle.loads(decompressed)
        except Exception:
            return data.decode('utf-8')


class DistributedCache:
    """
    Cache distribuído com múltiplos nós
    """
    
    def __init__(self, strategy: CacheStrategy = CacheStrategy.CONSISTENT_HASH,
                 config: Optional[Dict] = None):
        self.strategy = strategy
        self.config = config or {}
        self.nodes: Dict[str, CacheNode] = {}
        self.virtual_nodes = self.config.get('virtual_nodes', 150)
        self.hash_ring: Dict[int, str] = {}
        
        # Cache local
        self.local_cache = TTLCache(
            maxsize=self.config.get('local_cache_size', 1000),
            ttl=self.config.get('local_cache_ttl', 300)
        )
        
        # Configurações
        self.replication_factor = self.config.get('replication_factor', 2)
        self.compression_enabled = self.config.get('compression_enabled', True)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        
        # Métricas
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
            'total_requests': 0
        }
        
        # Health check
        self.health_check_task = None
        self.is_running = False
        self._lock = threading.Lock()
    
    async def start(self):
        """Inicia o cache distribuído"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Conectar a todos os nós
        await self._connect_all_nodes()
        
        # Construir hash ring
        self._build_hash_ring()
        
        # Iniciar health check
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("Distributed cache started")
    
    async def stop(self):
        """Para o cache distribuído"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Desconectar todos os nós
        for node in self.nodes.values():
            await node.disconnect()
        
        logger.info("Distributed cache stopped")
    
    def add_node(self, node_id: str, host: str, port: int, weight: int = 1) -> bool:
        """Adiciona nó ao cache"""
        try:
            node = CacheNode(node_id, host, port, weight)
            self.nodes[node_id] = node
            
            if self.is_running:
                asyncio.create_task(node.connect())
                self._build_hash_ring()
            
            logger.info(f"Cache node added: {node_id} ({host}:{port})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding cache node {node_id}: {e}")
            return False
    
    def remove_node(self, node_id: str) -> bool:
        """Remove nó do cache"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            asyncio.create_task(node.disconnect())
            del self.nodes[node_id]
            self._build_hash_ring()
            
            logger.info(f"Cache node removed: {node_id}")
            return True
        return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        self.metrics['total_requests'] += 1
        
        # Verificar cache local primeiro
        if key in self.local_cache:
            self.metrics['hits'] += 1
            return self.local_cache[key]
        
        # Determinar nó responsável
        node = self._get_responsible_node(key)
        if not node:
            self.metrics['misses'] += 1
            return None
        
        # Tentar obter do nó
        for attempt in range(self.retry_attempts):
            value = await node.get(key)
            if value is not None:
                # Armazenar no cache local
                self.local_cache[key] = value
                self.metrics['hits'] += 1
                return value
            
            # Tentar nó de backup
            backup_node = self._get_backup_node(key, node)
            if backup_node and backup_node != node:
                value = await backup_node.get(key)
                if value is not None:
                    self.local_cache[key] = value
                    self.metrics['hits'] += 1
                    return value
        
        self.metrics['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        self.metrics['total_requests'] += 1
        
        # Armazenar no cache local
        self.local_cache[key] = value
        
        # Determinar nós responsáveis
        primary_node = self._get_responsible_node(key)
        if not primary_node:
            self.metrics['errors'] += 1
            return False
        
        # Replicar para múltiplos nós
        nodes_to_update = [primary_node]
        
        # Adicionar nós de backup
        for i in range(self.replication_factor - 1):
            backup_node = self._get_backup_node(key, primary_node, i + 1)
            if backup_node and backup_node not in nodes_to_update:
                nodes_to_update.append(backup_node)
        
        # Atualizar todos os nós
        success = True
        for node in nodes_to_update:
            if not await node.set(key, value, ttl):
                success = False
                self.metrics['errors'] += 1
        
        if success:
            self.metrics['sets'] += 1
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        self.metrics['total_requests'] += 1
        
        # Remover do cache local
        if key in self.local_cache:
            del self.local_cache[key]
        
        # Determinar nós responsáveis
        primary_node = self._get_responsible_node(key)
        if not primary_node:
            return False
        
        # Remover de todos os nós
        nodes_to_update = [primary_node]
        
        for i in range(self.replication_factor - 1):
            backup_node = self._get_backup_node(key, primary_node, i + 1)
            if backup_node and backup_node not in nodes_to_update:
                nodes_to_update.append(backup_node)
        
        success = True
        for node in nodes_to_update:
            if not await node.delete(key):
                success = False
        
        if success:
            self.metrics['deletes'] += 1
        
        return success
    
    async def clear(self) -> bool:
        """Limpa todo o cache"""
        # Limpar cache local
        self.local_cache.clear()
        
        # Limpar todos os nós
        success = True
        for node in self.nodes.values():
            if not await node.clear():
                success = False
        
        return success
    
    def _get_responsible_node(self, key: str) -> Optional[CacheNode]:
        """Obtém nó responsável pela chave"""
        if not self.nodes:
            return None
        
        if self.strategy == CacheStrategy.CONSISTENT_HASH:
            return self._consistent_hash_get_node(key)
        elif self.strategy == CacheStrategy.LRU:
            return self._lru_get_node(key)
        else:
            return self._round_robin_get_node(key)
    
    def _consistent_hash_get_node(self, key: str) -> Optional[CacheNode]:
        """Obtém nó usando hash consistente"""
        if not self.hash_ring:
            return None
        
        # Calcular hash da chave
        key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)
        
        # Encontrar próximo nó no ring
        sorted_hashes = sorted(self.hash_ring.keys())
        
        for hash_value in sorted_hashes:
            if hash_value >= key_hash:
                node_id = self.hash_ring[hash_value]
                return self.nodes.get(node_id)
        
        # Se não encontrou, usar o primeiro
        if sorted_hashes:
            node_id = self.hash_ring[sorted_hashes[0]]
            return self.nodes.get(node_id)
        
        return None
    
    def _lru_get_node(self, key: str) -> Optional[CacheNode]:
        """Obtém nó usando LRU"""
        # Implementação simplificada - retorna nó com menor carga
        healthy_nodes = [n for n in self.nodes.values() if n.is_connected]
        if not healthy_nodes:
            return None
        
        return min(healthy_nodes, key=lambda n: n.response_time)
    
    def _round_robin_get_node(self, key: str) -> Optional[CacheNode]:
        """Obtém nó usando round robin"""
        healthy_nodes = [n for n in self.nodes.values() if n.is_connected]
        if not healthy_nodes:
            return None
        
        # Hash da chave para distribuição
        key_hash = hash(key)
        index = key_hash % len(healthy_nodes)
        return healthy_nodes[index]
    
    def _get_backup_node(self, key: str, primary_node: CacheNode, offset: int = 1) -> Optional[CacheNode]:
        """Obtém nó de backup"""
        if self.strategy == CacheStrategy.CONSISTENT_HASH:
            return self._consistent_hash_get_backup_node(key, primary_node, offset)
        else:
            # Para outras estratégias, usar round robin
            healthy_nodes = [n for n in self.nodes.values() if n.is_connected and n != primary_node]
            if not healthy_nodes:
                return None
            
            key_hash = hash(key)
            index = (key_hash + offset) % len(healthy_nodes)
            return healthy_nodes[index]
    
    def _consistent_hash_get_backup_node(self, key: str, primary_node: CacheNode, offset: int) -> Optional[CacheNode]:
        """Obtém nó de backup usando hash consistente"""
        if not self.hash_ring:
            return None
        
        key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)
        sorted_hashes = sorted(self.hash_ring.keys())
        
        # Encontrar posição do nó primário
        primary_index = None
        for i, hash_value in enumerate(sorted_hashes):
            if self.hash_ring[hash_value] == primary_node.node_id:
                primary_index = i
                break
        
        if primary_index is None:
            return None
        
        # Calcular índice do nó de backup
        backup_index = (primary_index + offset) % len(sorted_hashes)
        backup_node_id = self.hash_ring[sorted_hashes[backup_index]]
        
        return self.nodes.get(backup_node_id)
    
    def _build_hash_ring(self):
        """Constrói ring de hash consistente"""
        self.hash_ring.clear()
        
        for node in self.nodes.values():
            # Criar nós virtuais
            for i in range(self.virtual_nodes):
                virtual_key = f"{node.node_id}:{i}"
                virtual_hash = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                self.hash_ring[virtual_hash] = node.node_id
    
    async def _connect_all_nodes(self):
        """Conecta a todos os nós"""
        tasks = []
        for node in self.nodes.values():
            tasks.append(node.connect())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _health_check_loop(self):
        """Loop de verificação de saúde"""
        while self.is_running:
            try:
                await self._check_nodes_health()
                await asyncio.sleep(30)  # Verificar a cada 30 segundos
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_nodes_health(self):
        """Verifica saúde dos nós"""
        for node in self.nodes.values():
            try:
                if node.is_connected:
                    # Testar conexão
                    await node.redis_client.ping()
                    node.last_heartbeat = datetime.now()
                    node.error_count = 0
                else:
                    # Tentar reconectar
                    await node.connect()
            except Exception as e:
                node.error_count += 1
                if node.error_count > 5:
                    node.is_connected = False
                logger.warning(f"Health check failed for node {node.node_id}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do cache"""
        metrics = self.metrics.copy()
        
        if metrics['total_requests'] > 0:
            metrics['hit_rate'] = metrics['hits'] / metrics['total_requests']
        else:
            metrics['hit_rate'] = 0.0
        
        metrics['node_count'] = len(self.nodes)
        metrics['connected_nodes'] = len([n for n in self.nodes.values() if n.is_connected])
        
        return metrics
    
    def get_node_status(self) -> List[Dict[str, Any]]:
        """Obtém status dos nós"""
        return [
            {
                'node_id': node.node_id,
                'host': node.host,
                'port': node.port,
                'weight': node.weight,
                'is_connected': node.is_connected,
                'last_heartbeat': node.last_heartbeat.isoformat() if node.last_heartbeat else None,
                'error_count': node.error_count,
                'response_time': node.response_time
            }
            for node in self.nodes.values()
        ]


# Funções utilitárias
def create_distributed_cache(strategy: CacheStrategy = CacheStrategy.CONSISTENT_HASH,
                           config: Optional[Dict] = None) -> DistributedCache:
    """Cria cache distribuído"""
    return DistributedCache(strategy, config)


# Instância global
distributed_cache = DistributedCache()


# Decorator para cache distribuído
def with_distributed_cache(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator para usar cache distribuído"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave do cache
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Tentar obter do cache
            cached_value = await distributed_cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Armazenar no cache
            await distributed_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator 