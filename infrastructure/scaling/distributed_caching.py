"""
Módulo de Cache Distribuído para Sistemas Enterprise
Sistema de cache distribuído com sincronização e replicação - Omni Keywords Finder

Prompt: Implementação de sistema de cache distribuído enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import asyncio
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor
import pickle
import base64
import random

logger = logging.getLogger(__name__)


class CacheNodeStatus(Enum):
    """Status dos nós de cache."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    SYNCING = "syncing"
    MAINTENANCE = "maintenance"


class CacheConsistencyLevel(Enum):
    """Níveis de consistência do cache."""
    EVENTUAL = "eventual"  # Consistência eventual
    STRONG = "strong"      # Consistência forte
    WEAK = "weak"          # Consistência fraca


@dataclass
class CacheNode:
    """Nó de cache distribuído."""
    id: str
    host: str
    port: int
    status: CacheNodeStatus = CacheNodeStatus.ONLINE
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    memory_usage: float = 0.0  # em MB
    hit_rate: float = 0.0  # taxa de acerto (0-1)
    load: float = 0.0  # carga atual (0-1)
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.id or len(self.id.strip()) == 0:
            raise ValueError("ID do nó não pode ser vazio")
        if not self.host or len(self.host.strip()) == 0:
            raise ValueError("Host não pode ser vazio")
        if not 1 <= self.port <= 65535:
            raise ValueError("Porta deve estar entre 1 e 65535")
        if self.memory_usage < 0:
            raise ValueError("Memory usage não pode ser negativo")
        if not 0 <= self.hit_rate <= 1:
            raise ValueError("Hit rate deve estar entre 0 e 1")
        if not 0 <= self.load <= 1:
            raise ValueError("Load deve estar entre 0 e 1")
        
        # Normalizar campos
        self.id = self.id.strip()
        self.host = self.host.strip()
    
    def is_online(self) -> bool:
        """Verifica se o nó está online."""
        return self.status == CacheNodeStatus.ONLINE
    
    def get_health_score(self) -> float:
        """Calcula score de saúde do nó (0-1)."""
        if not self.is_online():
            return 0.0
        
        # Fatores que afetam a saúde
        memory_factor = max(0.0, 1.0 - (self.memory_usage / 1000.0))  # 1GB como referência
        hit_factor = self.hit_rate
        load_factor = 1.0 - self.load
        
        # Score combinado
        score = (memory_factor * 0.3 + 
                hit_factor * 0.4 + 
                load_factor * 0.3)
        
        return max(0.0, min(1.0, score))


@dataclass
class CacheEntry:
    """Entrada de cache."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    ttl: int = 3600  # TTL em segundos
    version: int = 1
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.key or len(self.key.strip()) == 0:
            raise ValueError("Chave não pode ser vazia")
        if self.ttl < 0:
            raise ValueError("TTL não pode ser negativo")
        if self.version < 1:
            raise ValueError("Version deve ser pelo menos 1")
        
        # Normalizar campos
        self.key = self.key.strip()
        
        # Calcular expires_at se não fornecido
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl)
        
        # Calcular checksum
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calcula checksum da entrada."""
        data = f"{self.key}:{self.value}:{self.version}:{self.created_at.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_remaining_ttl(self) -> int:
        """Obtém TTL restante em segundos."""
        if self.expires_at is None:
            return self.ttl
        
        remaining = (self.expires_at - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))


@dataclass
class DistributedCacheConfig:
    """Configuração do cache distribuído."""
    consistency_level: CacheConsistencyLevel = CacheConsistencyLevel.EVENTUAL
    replication_factor: int = 2
    sync_interval: int = 30  # segundos
    heartbeat_interval: int = 10  # segundos
    max_memory_mb: int = 1024  # MB
    eviction_policy: str = "lru"  # lru, lfu, fifo
    enable_compression: bool = True
    enable_encryption: bool = False
    encryption_key: str = ""
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.replication_factor < 1:
            raise ValueError("Replication factor deve ser pelo menos 1")
        if self.sync_interval < 1:
            raise ValueError("Sync interval deve ser pelo menos 1 segundo")
        if self.heartbeat_interval < 1:
            raise ValueError("Heartbeat interval deve ser pelo menos 1 segundo")
        if self.max_memory_mb < 1:
            raise ValueError("Max memory deve ser pelo menos 1MB")
        if self.eviction_policy not in ["lru", "lfu", "fifo"]:
            raise ValueError("Eviction policy deve ser lru, lfu ou fifo")


class DistributedCache:
    """Cache distribuído enterprise com sincronização e replicação."""
    
    def __init__(self, config: DistributedCacheConfig):
        """
        Inicializa o cache distribuído.
        
        Args:
            config: Configuração do cache
        """
        self.config = config
        self.nodes: Dict[str, CacheNode] = {}
        self.cache: Dict[str, CacheEntry] = {}
        self.node_assignments: Dict[str, List[str]] = {}  # key -> node_ids
        self.sync_task = None
        self.heartbeat_task = None
        self.is_running = False
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "sync_operations": 0
        }
        
        logger.info(f"DistributedCache inicializado - Config: {config}")
    
    def add_node(self, node: CacheNode) -> None:
        """Adiciona um nó ao cluster."""
        if node.id in self.nodes:
            raise ValueError(f"Nó com ID {node.id} já existe")
        
        self.nodes[node.id] = node
        logger.info(f"Nó adicionado: {node.host}:{node.port} ({node.id})")
    
    def remove_node(self, node_id: str) -> None:
        """Remove um nó do cluster."""
        if node_id not in self.nodes:
            raise ValueError(f"Nó com ID {node_id} não encontrado")
        
        # Rebalancear dados
        self._rebalance_data(node_id)
        
        del self.nodes[node_id]
        logger.info(f"Nó removido: {node_id}")
    
    def _rebalance_data(self, removed_node_id: str) -> None:
        """Rebalanceia dados após remoção de nó."""
        # Encontrar chaves que estavam no nó removido
        keys_to_rebalance = []
        for key, node_ids in self.node_assignments.items():
            if removed_node_id in node_ids:
                keys_to_rebalance.append(key)
        
        # Redistribuir chaves
        available_nodes = [nid for nid in self.nodes.keys() if nid != removed_node_id]
        if not available_nodes:
            return
        
        for key in keys_to_rebalance:
            # Remover nó antigo
            self.node_assignments[key].remove(removed_node_id)
            
            # Adicionar novo nó se necessário
            if len(self.node_assignments[key]) < self.config.replication_factor:
                new_node = self._select_node_for_key(key, available_nodes)
                if new_node:
                    self.node_assignments[key].append(new_node)
    
    def _select_node_for_key(self, key: str, available_nodes: List[str]) -> Optional[str]:
        """Seleciona nó para uma chave baseado em hash."""
        if not available_nodes:
            return None
        
        # Hash da chave para distribuição consistente
        hash_value = hash(key) % len(available_nodes)
        return available_nodes[hash_value]
    
    def _get_nodes_for_key(self, key: str) -> List[str]:
        """Obtém nós responsáveis por uma chave."""
        if key not in self.node_assignments:
            # Criar nova atribuição
            available_nodes = [nid for nid, node in self.nodes.items() if node.is_online()]
            if not available_nodes:
                return []
            
            node_ids = []
            for _ in range(min(self.config.replication_factor, len(available_nodes))):
                node_id = self._select_node_for_key(key, available_nodes)
                if node_id and node_id not in node_ids:
                    node_ids.append(node_id)
                    available_nodes.remove(node_id)
            
            self.node_assignments[key] = node_ids
        
        return self.node_assignments[key]
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor do cache.
        
        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado
            
        Returns:
            Valor do cache ou default
        """
        if key not in self.cache:
            self.metrics["misses"] += 1
            return default
        
        entry = self.cache[key]
        
        # Verificar expiração
        if entry.is_expired():
            await self.delete(key)
            self.metrics["misses"] += 1
            return default
        
        # Verificar consistência se necessário
        if self.config.consistency_level == CacheConsistencyLevel.STRONG:
            if not await self._verify_consistency(key, entry):
                # Inconsistência detectada, tentar sincronizar
                await self._sync_key(key)
        
        self.metrics["hits"] += 1
        return entry.value
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Define valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: TTL em segundos (opcional)
            
        Returns:
            True se definido com sucesso, False caso contrário
        """
        try:
            # Criar entrada
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self.config.max_memory_mb * 60  # TTL baseado em memória
            )
            
            # Verificar espaço disponível
            if not await self._ensure_space():
                return False
            
            # Armazenar localmente
            self.cache[key] = entry
            
            # Replicar para outros nós
            await self._replicate_key(key, entry)
            
            self.metrics["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir chave {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Remove valor do cache.
        
        Args:
            key: Chave a ser removida
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            # Remover localmente
            if key in self.cache:
                del self.cache[key]
            
            # Remover de outros nós
            await self._delete_from_nodes(key)
            
            # Limpar atribuições
            if key in self.node_assignments:
                del self.node_assignments[key]
            
            self.metrics["deletes"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover chave {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Verifica se uma chave existe no cache.
        
        Args:
            key: Chave a ser verificada
            
        Returns:
            True se existe, False caso contrário
        """
        if key not in self.cache:
            return False
        
        entry = self.cache[key]
        if entry.is_expired():
            await self.delete(key)
            return False
        
        return True
    
    async def clear(self) -> bool:
        """
        Limpa todo o cache.
        
        Returns:
            True se limpo com sucesso, False caso contrário
        """
        try:
            self.cache.clear()
            self.node_assignments.clear()
            
            # Limpar em todos os nós
            for node_id in self.nodes.keys():
                await self._clear_node(node_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    async def _ensure_space(self) -> bool:
        """Garante espaço disponível no cache."""
        current_memory = sum(len(str(entry.value)) for entry in self.cache.values()) / (1024 * 1024)  # MB
        
        if current_memory < self.config.max_memory_mb:
            return True
        
        # Evict entries baseado na política
        await self._evict_entries()
        return True
    
    async def _evict_entries(self) -> None:
        """Remove entradas baseado na política de eviction."""
        if self.config.eviction_policy == "lru":
            # Least Recently Used
            entries = sorted(self.cache.items(), key=lambda x: x[1].created_at)
        elif self.config.eviction_policy == "lfu":
            # Least Frequently Used (simulado)
            entries = sorted(self.cache.items(), key=lambda x: x[1].metadata.get("access_count", 0))
        else:  # fifo
            # First In First Out
            entries = sorted(self.cache.items(), key=lambda x: x[1].created_at)
        
        # Remover 10% das entradas mais antigas
        to_remove = max(1, len(entries) // 10)
        for key, _ in entries[:to_remove]:
            await self.delete(key)
            self.metrics["evictions"] += 1
    
    async def _replicate_key(self, key: str, entry: CacheEntry) -> None:
        """Replica chave para outros nós."""
        node_ids = self._get_nodes_for_key(key)
        
        for node_id in node_ids:
            if node_id in self.nodes and self.nodes[node_id].is_online():
                try:
                    await self._set_on_node(node_id, key, entry)
                except Exception as e:
                    logger.warning(f"Erro ao replicar chave {key} para nó {node_id}: {e}")
    
    async def _set_on_node(self, node_id: str, key: str, entry: CacheEntry) -> None:
        """Define chave em um nó específico."""
        # Simular operação de rede
        await asyncio.sleep(0.001)  # 1ms de latência
        
        # Atualizar métricas do nó
        if node_id in self.nodes:
            self.nodes[node_id].memory_usage += len(str(entry.value)) / (1024 * 1024)  # MB
    
    async def _delete_from_nodes(self, key: str) -> None:
        """Remove chave de todos os nós."""
        node_ids = self._get_nodes_for_key(key)
        
        for node_id in node_ids:
            if node_id in self.nodes and self.nodes[node_id].is_online():
                try:
                    await self._delete_from_node(node_id, key)
                except Exception as e:
                    logger.warning(f"Erro ao remover chave {key} do nó {node_id}: {e}")
    
    async def _delete_from_node(self, node_id: str, key: str) -> None:
        """Remove chave de um nó específico."""
        # Simular operação de rede
        await asyncio.sleep(0.001)  # 1ms de latência
    
    async def _clear_node(self, node_id: str) -> None:
        """Limpa cache de um nó específico."""
        # Simular operação de rede
        await asyncio.sleep(0.001)  # 1ms de latência
        
        if node_id in self.nodes:
            self.nodes[node_id].memory_usage = 0.0
    
    async def _verify_consistency(self, key: str, entry: CacheEntry) -> bool:
        """Verifica consistência de uma chave."""
        node_ids = self._get_nodes_for_key(key)
        
        # Verificar checksum em todos os nós
        for node_id in node_ids:
            if node_id in self.nodes and self.nodes[node_id].is_online():
                try:
                    node_checksum = await self._get_checksum_from_node(node_id, key)
                    if node_checksum != entry.checksum:
                        return False
                except Exception:
                    return False
        
        return True
    
    async def _get_checksum_from_node(self, node_id: str, key: str) -> str:
        """Obtém checksum de um nó específico."""
        # Simular operação de rede
        await asyncio.sleep(0.001)  # 1ms de latência
        return "simulated_checksum"
    
    async def _sync_key(self, key: str) -> None:
        """Sincroniza chave entre nós."""
        if key not in self.cache:
            return
        
        entry = self.cache[key]
        await self._replicate_key(key, entry)
        self.metrics["sync_operations"] += 1
    
    async def start_sync(self) -> None:
        """Inicia sincronização periódica."""
        if self.is_running:
            return
        
        self.is_running = True
        self.sync_task = asyncio.create_task(self._sync_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Sincronização iniciada")
    
    async def stop_sync(self) -> None:
        """Para sincronização."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.sync_task:
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Sincronização parada")
    
    async def _sync_loop(self) -> None:
        """Loop principal de sincronização."""
        while self.is_running:
            try:
                await self._perform_sync()
                await asyncio.sleep(self.config.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no sync loop: {e}")
                await asyncio.sleep(5)
    
    async def _heartbeat_loop(self) -> None:
        """Loop de heartbeat."""
        while self.is_running:
            try:
                await self._perform_heartbeat()
                await asyncio.sleep(self.config.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no heartbeat loop: {e}")
                await asyncio.sleep(5)
    
    async def _perform_sync(self) -> None:
        """Executa sincronização."""
        # Sincronizar entradas expiradas
        expired_keys = []
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        # Sincronizar inconsistências
        if self.config.consistency_level == CacheConsistencyLevel.STRONG:
            for key in self.cache.keys():
                if not await self._verify_consistency(key, self.cache[key]):
                    await self._sync_key(key)
    
    async def _perform_heartbeat(self) -> None:
        """Executa heartbeat."""
        current_time = datetime.utcnow()
        
        for node in self.nodes.values():
            # Simular heartbeat
            node.last_heartbeat = current_time
            
            # Simular mudanças de status
            if random.random() < 0.01:  # 1% de chance de mudança
                if node.status == CacheNodeStatus.ONLINE:
                    node.status = CacheNodeStatus.DEGRADED
                elif node.status == CacheNodeStatus.DEGRADED:
                    node.status = CacheNodeStatus.ONLINE
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do cache."""
        total_requests = self.metrics["hits"] + self.metrics["misses"]
        hit_rate = self.metrics["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            "hits": self.metrics["hits"],
            "misses": self.metrics["misses"],
            "hit_rate": hit_rate,
            "sets": self.metrics["sets"],
            "deletes": self.metrics["deletes"],
            "evictions": self.metrics["evictions"],
            "sync_operations": self.metrics["sync_operations"],
            "total_entries": len(self.cache),
            "total_nodes": len(self.nodes),
            "online_nodes": len([n for n in self.nodes.values() if n.is_online()])
        }
    
    def get_node_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtém status de todos os nós."""
        status = {}
        for node_id, node in self.nodes.items():
            status[node_id] = {
                "host": node.host,
                "port": node.port,
                "status": node.status.value,
                "memory_usage": node.memory_usage,
                "hit_rate": node.hit_rate,
                "load": node.load,
                "health_score": node.get_health_score(),
                "last_heartbeat": node.last_heartbeat.isoformat(),
                "version": node.version
            }
        return status


# Função de conveniência para criar cache distribuído
def create_distributed_cache(consistency_level: CacheConsistencyLevel = CacheConsistencyLevel.EVENTUAL,
                           replication_factor: int = 2) -> DistributedCache:
    """
    Cria um cache distribuído com configurações padrão.
    
    Args:
        consistency_level: Nível de consistência
        replication_factor: Fator de replicação
        
    Returns:
        Instância configurada do DistributedCache
    """
    config = DistributedCacheConfig(
        consistency_level=consistency_level,
        replication_factor=replication_factor
    )
    return DistributedCache(config) 