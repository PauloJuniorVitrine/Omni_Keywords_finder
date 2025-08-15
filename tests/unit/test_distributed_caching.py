"""
Testes Unitários para Cache Distribuído
Sistema de Cache Distribuído com Sincronização - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de cache distribuído
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.scaling.distributed_caching import (
    DistributedCache, CacheNodeStatus, CacheConsistencyLevel,
    CacheNode, CacheEntry, DistributedCacheConfig,
    create_distributed_cache
)


class TestCacheNode:
    """Testes para CacheNode"""
    
    def test_cache_node_initialization(self):
        """Testa inicialização de CacheNode"""
        node = CacheNode(
            id="node-1",
            host="localhost",
            port=6379,
            status=CacheNodeStatus.ONLINE,
            memory_usage=512.0,
            hit_rate=0.85,
            load=0.3,
            version="1.0.0"
        )
        
        assert node.id == "node-1"
        assert node.host == "localhost"
        assert node.port == 6379
        assert node.status == CacheNodeStatus.ONLINE
        assert node.memory_usage == 512.0
        assert node.hit_rate == 0.85
        assert node.load == 0.3
        assert node.version == "1.0.0"
    
    def test_cache_node_validation_id_empty(self):
        """Testa validação de ID vazio"""
        with pytest.raises(ValueError, match="ID do nó não pode ser vazio"):
            CacheNode(id="", host="localhost", port=6379)
    
    def test_cache_node_validation_host_empty(self):
        """Testa validação de host vazio"""
        with pytest.raises(ValueError, match="Host não pode ser vazio"):
            CacheNode(id="node-1", host="", port=6379)
    
    def test_cache_node_validation_port_invalid(self):
        """Testa validação de porta inválida"""
        with pytest.raises(ValueError, match="Porta deve estar entre 1 e 65535"):
            CacheNode(id="node-1", host="localhost", port=0)
    
    def test_cache_node_validation_memory_usage_negative(self):
        """Testa validação de memory usage negativo"""
        with pytest.raises(ValueError, match="Memory usage não pode ser negativo"):
            CacheNode(id="node-1", host="localhost", port=6379, memory_usage=-1.0)
    
    def test_cache_node_validation_hit_rate_invalid(self):
        """Testa validação de hit rate inválido"""
        with pytest.raises(ValueError, match="Hit rate deve estar entre 0 e 1"):
            CacheNode(id="node-1", host="localhost", port=6379, hit_rate=1.5)
    
    def test_cache_node_validation_load_invalid(self):
        """Testa validação de load inválido"""
        with pytest.raises(ValueError, match="Load deve estar entre 0 e 1"):
            CacheNode(id="node-1", host="localhost", port=6379, load=1.5)
    
    def test_is_online(self):
        """Testa verificação se nó está online"""
        online_node = CacheNode(
            id="online",
            host="localhost",
            port=6379,
            status=CacheNodeStatus.ONLINE
        )
        
        offline_node = CacheNode(
            id="offline",
            host="localhost",
            port=6379,
            status=CacheNodeStatus.OFFLINE
        )
        
        assert online_node.is_online() is True
        assert offline_node.is_online() is False
    
    def test_get_health_score(self):
        """Testa cálculo de score de saúde"""
        node = CacheNode(
            id="test",
            host="localhost",
            port=6379,
            status=CacheNodeStatus.ONLINE,
            memory_usage=500.0,  # 500MB
            hit_rate=0.8,
            load=0.4
        )
        
        score = node.get_health_score()
        assert 0.0 <= score <= 1.0
    
    def test_get_health_score_offline(self):
        """Testa score de saúde de nó offline"""
        node = CacheNode(
            id="test",
            host="localhost",
            port=6379,
            status=CacheNodeStatus.OFFLINE
        )
        
        score = node.get_health_score()
        assert score == 0.0


class TestCacheEntry:
    """Testes para CacheEntry"""
    
    def test_cache_entry_initialization(self):
        """Testa inicialização de CacheEntry"""
        entry = CacheEntry(
            key="test-key",
            value="test-value",
            ttl=3600,
            version=1
        )
        
        assert entry.key == "test-key"
        assert entry.value == "test-value"
        assert entry.ttl == 3600
        assert entry.version == 1
        assert entry.checksum != ""
        assert entry.expires_at is not None
    
    def test_cache_entry_validation_key_empty(self):
        """Testa validação de chave vazia"""
        with pytest.raises(ValueError, match="Chave não pode ser vazia"):
            CacheEntry(key="", value="test")
    
    def test_cache_entry_validation_ttl_negative(self):
        """Testa validação de TTL negativo"""
        with pytest.raises(ValueError, match="TTL não pode ser negativo"):
            CacheEntry(key="test", value="test", ttl=-1)
    
    def test_cache_entry_validation_version_invalid(self):
        """Testa validação de version inválido"""
        with pytest.raises(ValueError, match="Version deve ser pelo menos 1"):
            CacheEntry(key="test", value="test", version=0)
    
    def test_is_expired_not_expired(self):
        """Testa verificação de expiração - não expirado"""
        entry = CacheEntry(
            key="test",
            value="test",
            ttl=3600
        )
        
        assert entry.is_expired() is False
    
    def test_is_expired_expired(self):
        """Testa verificação de expiração - expirado"""
        entry = CacheEntry(
            key="test",
            value="test",
            ttl=1,
            expires_at=datetime.utcnow() - timedelta(seconds=10)
        )
        
        assert entry.is_expired() is True
    
    def test_get_remaining_ttl(self):
        """Testa obtenção de TTL restante"""
        entry = CacheEntry(
            key="test",
            value="test",
            ttl=3600
        )
        
        remaining = entry.get_remaining_ttl()
        assert 0 <= remaining <= 3600
    
    def test_get_remaining_ttl_expired(self):
        """Testa TTL restante de entrada expirada"""
        entry = CacheEntry(
            key="test",
            value="test",
            ttl=1,
            expires_at=datetime.utcnow() - timedelta(seconds=10)
        )
        
        remaining = entry.get_remaining_ttl()
        assert remaining == 0


class TestDistributedCacheConfig:
    """Testes para DistributedCacheConfig"""
    
    def test_distributed_cache_config_initialization(self):
        """Testa inicialização de DistributedCacheConfig"""
        config = DistributedCacheConfig(
            consistency_level=CacheConsistencyLevel.STRONG,
            replication_factor=3,
            sync_interval=60,
            heartbeat_interval=15,
            max_memory_mb=2048,
            eviction_policy="lfu"
        )
        
        assert config.consistency_level == CacheConsistencyLevel.STRONG
        assert config.replication_factor == 3
        assert config.sync_interval == 60
        assert config.heartbeat_interval == 15
        assert config.max_memory_mb == 2048
        assert config.eviction_policy == "lfu"
    
    def test_distributed_cache_config_validation_replication_factor(self):
        """Testa validação de replication factor"""
        with pytest.raises(ValueError, match="Replication factor deve ser pelo menos 1"):
            DistributedCacheConfig(replication_factor=0)
    
    def test_distributed_cache_config_validation_sync_interval(self):
        """Testa validação de sync interval"""
        with pytest.raises(ValueError, match="Sync interval deve ser pelo menos 1 segundo"):
            DistributedCacheConfig(sync_interval=0)
    
    def test_distributed_cache_config_validation_heartbeat_interval(self):
        """Testa validação de heartbeat interval"""
        with pytest.raises(ValueError, match="Heartbeat interval deve ser pelo menos 1 segundo"):
            DistributedCacheConfig(heartbeat_interval=0)
    
    def test_distributed_cache_config_validation_max_memory(self):
        """Testa validação de max memory"""
        with pytest.raises(ValueError, match="Max memory deve ser pelo menos 1MB"):
            DistributedCacheConfig(max_memory_mb=0)
    
    def test_distributed_cache_config_validation_eviction_policy(self):
        """Testa validação de eviction policy"""
        with pytest.raises(ValueError, match="Eviction policy deve ser lru, lfu ou fifo"):
            DistributedCacheConfig(eviction_policy="invalid")


class TestDistributedCache:
    """Testes para DistributedCache"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return DistributedCacheConfig(
            consistency_level=CacheConsistencyLevel.EVENTUAL,
            replication_factor=2,
            sync_interval=30,
            heartbeat_interval=10,
            max_memory_mb=1024
        )
    
    @pytest.fixture
    def distributed_cache(self, sample_config):
        """Instância de DistributedCache para testes"""
        return DistributedCache(sample_config)
    
    @pytest.fixture
    def sample_node(self):
        """Nó de exemplo para testes"""
        return CacheNode(
            id="node-1",
            host="localhost",
            port=6379,
            status=CacheNodeStatus.ONLINE
        )
    
    def test_distributed_cache_initialization(self, sample_config):
        """Testa inicialização do DistributedCache"""
        cache = DistributedCache(sample_config)
        
        assert cache.config == sample_config
        assert len(cache.nodes) == 0
        assert len(cache.cache) == 0
        assert len(cache.node_assignments) == 0
        assert cache.is_running is False
        assert cache.sync_task is None
        assert cache.heartbeat_task is None
    
    def test_add_node(self, distributed_cache, sample_node):
        """Testa adição de nó"""
        distributed_cache.add_node(sample_node)
        
        assert len(distributed_cache.nodes) == 1
        assert "node-1" in distributed_cache.nodes
        assert distributed_cache.nodes["node-1"] == sample_node
    
    def test_add_duplicate_node(self, distributed_cache, sample_node):
        """Testa adição de nó duplicado"""
        distributed_cache.add_node(sample_node)
        
        with pytest.raises(ValueError, match="Nó com ID node-1 já existe"):
            distributed_cache.add_node(sample_node)
    
    def test_remove_node(self, distributed_cache, sample_node):
        """Testa remoção de nó"""
        distributed_cache.add_node(sample_node)
        
        distributed_cache.remove_node("node-1")
        
        assert len(distributed_cache.nodes) == 0
        assert "node-1" not in distributed_cache.nodes
    
    def test_remove_nonexistent_node(self, distributed_cache):
        """Testa remoção de nó inexistente"""
        with pytest.raises(ValueError, match="Nó com ID nonexistent não encontrado"):
            distributed_cache.remove_node("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, distributed_cache):
        """Testa obtenção de chave inexistente"""
        value = await distributed_cache.get("nonexistent", default="default")
        assert value == "default"
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, distributed_cache):
        """Testa definição e obtenção de valor"""
        # Definir valor
        success = await distributed_cache.set("test-key", "test-value", ttl=3600)
        assert success is True
        
        # Obter valor
        value = await distributed_cache.get("test-key")
        assert value == "test-value"
    
    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, distributed_cache):
        """Testa definição com TTL customizado"""
        success = await distributed_cache.set("test-key", "test-value", ttl=60)
        assert success is True
        
        # Verificar se foi criado com TTL correto
        entry = distributed_cache.cache["test-key"]
        assert entry.ttl == 60
    
    @pytest.mark.asyncio
    async def test_get_expired_entry(self, distributed_cache):
        """Testa obtenção de entrada expirada"""
        # Criar entrada expirada
        entry = CacheEntry(
            key="expired",
            value="expired-value",
            ttl=1,
            expires_at=datetime.utcnow() - timedelta(seconds=10)
        )
        distributed_cache.cache["expired"] = entry
        
        # Tentar obter
        value = await distributed_cache.get("expired", default="default")
        assert value == "default"
        
        # Verificar se foi removida
        assert "expired" not in distributed_cache.cache
    
    @pytest.mark.asyncio
    async def test_delete_existing_key(self, distributed_cache):
        """Testa remoção de chave existente"""
        # Definir valor
        await distributed_cache.set("test-key", "test-value")
        
        # Remover
        success = await distributed_cache.delete("test-key")
        assert success is True
        
        # Verificar se foi removida
        assert "test-key" not in distributed_cache.cache
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, distributed_cache):
        """Testa remoção de chave inexistente"""
        success = await distributed_cache.delete("nonexistent")
        assert success is True  # Deve retornar True mesmo se não existir
    
    @pytest.mark.asyncio
    async def test_exists_existing_key(self, distributed_cache):
        """Testa verificação de existência - chave existente"""
        await distributed_cache.set("test-key", "test-value")
        
        exists = await distributed_cache.exists("test-key")
        assert exists is True
    
    @pytest.mark.asyncio
    async def test_exists_nonexistent_key(self, distributed_cache):
        """Testa verificação de existência - chave inexistente"""
        exists = await distributed_cache.exists("nonexistent")
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_exists_expired_key(self, distributed_cache):
        """Testa verificação de existência - chave expirada"""
        # Criar entrada expirada
        entry = CacheEntry(
            key="expired",
            value="expired-value",
            ttl=1,
            expires_at=datetime.utcnow() - timedelta(seconds=10)
        )
        distributed_cache.cache["expired"] = entry
        
        exists = await distributed_cache.exists("expired")
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, distributed_cache):
        """Testa limpeza do cache"""
        # Adicionar algumas entradas
        await distributed_cache.set("key1", "value1")
        await distributed_cache.set("key2", "value2")
        
        # Limpar
        success = await distributed_cache.clear()
        assert success is True
        
        # Verificar se foi limpo
        assert len(distributed_cache.cache) == 0
        assert len(distributed_cache.node_assignments) == 0
    
    def test_get_metrics(self, distributed_cache):
        """Testa obtenção de métricas"""
        metrics = distributed_cache.get_metrics()
        
        assert "hits" in metrics
        assert "misses" in metrics
        assert "hit_rate" in metrics
        assert "sets" in metrics
        assert "deletes" in metrics
        assert "evictions" in metrics
        assert "sync_operations" in metrics
        assert "total_entries" in metrics
        assert "total_nodes" in metrics
        assert "online_nodes" in metrics
    
    def test_get_node_status(self, distributed_cache, sample_node):
        """Testa obtenção de status dos nós"""
        distributed_cache.add_node(sample_node)
        
        status = distributed_cache.get_node_status()
        
        assert "node-1" in status
        node_status = status["node-1"]
        assert "host" in node_status
        assert "port" in node_status
        assert "status" in node_status
        assert "memory_usage" in node_status
        assert "hit_rate" in node_status
        assert "load" in node_status
        assert "health_score" in node_status
        assert "last_heartbeat" in node_status
        assert "version" in node_status
    
    @pytest.mark.asyncio
    async def test_start_stop_sync(self, distributed_cache):
        """Testa início e parada de sincronização"""
        # Iniciar sincronização
        await distributed_cache.start_sync()
        assert distributed_cache.is_running is True
        assert distributed_cache.sync_task is not None
        assert distributed_cache.heartbeat_task is not None
        
        # Parar sincronização
        await distributed_cache.stop_sync()
        assert distributed_cache.is_running is False
    
    @pytest.mark.asyncio
    async def test_multiple_start_sync(self, distributed_cache):
        """Testa múltiplos inícios de sincronização"""
        await distributed_cache.start_sync()
        await distributed_cache.start_sync()  # Deve ser ignorado
        
        assert distributed_cache.is_running is True
        await distributed_cache.stop_sync()
    
    def test_node_assignment_with_nodes(self, distributed_cache):
        """Testa atribuição de nós para chaves"""
        # Adicionar nós
        node1 = CacheNode(id="node-1", host="localhost", port=6379)
        node2 = CacheNode(id="node-2", host="localhost", port=6380)
        node3 = CacheNode(id="node-3", host="localhost", port=6381)
        
        distributed_cache.add_node(node1)
        distributed_cache.add_node(node2)
        distributed_cache.add_node(node3)
        
        # Verificar atribuição de chaves
        nodes_for_key1 = distributed_cache._get_nodes_for_key("key1")
        nodes_for_key2 = distributed_cache._get_nodes_for_key("key2")
        
        assert len(nodes_for_key1) == 2  # replication_factor = 2
        assert len(nodes_for_key2) == 2
        assert all(nid in distributed_cache.nodes for nid in nodes_for_key1)
        assert all(nid in distributed_cache.nodes for nid in nodes_for_key2)
    
    def test_node_assignment_no_nodes(self, distributed_cache):
        """Testa atribuição de nós sem nós disponíveis"""
        nodes = distributed_cache._get_nodes_for_key("key1")
        assert len(nodes) == 0
    
    def test_node_assignment_offline_nodes(self, distributed_cache):
        """Testa atribuição de nós com nós offline"""
        # Adicionar nó offline
        offline_node = CacheNode(
            id="offline",
            host="localhost",
            port=6379,
            status=CacheNodeStatus.OFFLINE
        )
        distributed_cache.add_node(offline_node)
        
        nodes = distributed_cache._get_nodes_for_key("key1")
        assert len(nodes) == 0  # Nenhum nó online
    
    @pytest.mark.asyncio
    async def test_consistency_verification_strong(self, distributed_cache):
        """Testa verificação de consistência com nível forte"""
        distributed_cache.config.consistency_level = CacheConsistencyLevel.STRONG
        
        # Adicionar nós
        node1 = CacheNode(id="node-1", host="localhost", port=6379)
        node2 = CacheNode(id="node-2", host="localhost", port=6380)
        distributed_cache.add_node(node1)
        distributed_cache.add_node(node2)
        
        # Criar entrada
        entry = CacheEntry(key="test", value="value", ttl=3600)
        distributed_cache.cache["test"] = entry
        
        # Verificar consistência
        is_consistent = await distributed_cache._verify_consistency("test", entry)
        assert isinstance(is_consistent, bool)
    
    @pytest.mark.asyncio
    async def test_eviction_policy_lru(self, distributed_cache):
        """Testa política de eviction LRU"""
        distributed_cache.config.eviction_policy = "lru"
        distributed_cache.config.max_memory_mb = 1  # 1MB para forçar eviction
        
        # Adicionar muitas entradas
        for i in range(100):
            await distributed_cache.set(f"key{i}", "x" * 10000)  # 10KB cada
        
        # Verificar se algumas foram evictadas
        assert len(distributed_cache.cache) < 100


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_distributed_cache_default(self):
        """Testa criação de DistributedCache com configurações padrão"""
        cache = create_distributed_cache()
        
        assert isinstance(cache, DistributedCache)
        assert cache.config.consistency_level == CacheConsistencyLevel.EVENTUAL
        assert cache.config.replication_factor == 2
    
    def test_create_distributed_cache_custom_consistency(self):
        """Testa criação com nível de consistência customizado"""
        cache = create_distributed_cache(consistency_level=CacheConsistencyLevel.STRONG)
        
        assert cache.config.consistency_level == CacheConsistencyLevel.STRONG
    
    def test_create_distributed_cache_custom_replication(self):
        """Testa criação com fator de replicação customizado"""
        cache = create_distributed_cache(replication_factor=3)
        
        assert cache.config.replication_factor == 3


class TestDistributedCacheIntegration:
    """Testes de integração para Cache Distribuído"""
    
    @pytest.mark.asyncio
    async def test_complete_cache_workflow(self):
        """Testa workflow completo do cache"""
        # Criar cache
        cache = create_distributed_cache(
            consistency_level=CacheConsistencyLevel.EVENTUAL,
            replication_factor=2
        )
        
        # Adicionar nós
        node1 = CacheNode(id="node-1", host="localhost", port=6379)
        node2 = CacheNode(id="node-2", host="localhost", port=6380)
        cache.add_node(node1)
        cache.add_node(node2)
        
        # Definir valores
        await cache.set("user:1", {"name": "John", "email": "john@example.com"})
        await cache.set("user:2", {"name": "Jane", "email": "jane@example.com"})
        
        # Obter valores
        user1 = await cache.get("user:1")
        user2 = await cache.get("user:2")
        
        assert user1["name"] == "John"
        assert user2["name"] == "Jane"
        
        # Verificar existência
        assert await cache.exists("user:1") is True
        assert await cache.exists("user:3") is False
        
        # Remover valor
        await cache.delete("user:1")
        assert await cache.exists("user:1") is False
        
        # Verificar métricas
        metrics = cache.get_metrics()
        assert metrics["sets"] == 2
        assert metrics["hits"] == 2
        assert metrics["deletes"] == 1
    
    @pytest.mark.asyncio
    async def test_node_failure_scenario(self):
        """Testa cenário de falha de nó"""
        cache = create_distributed_cache(replication_factor=2)
        
        # Adicionar nós
        node1 = CacheNode(id="node-1", host="localhost", port=6379)
        node2 = CacheNode(id="node-2", host="localhost", port=6380)
        node3 = CacheNode(id="node-3", host="localhost", port=6381)
        
        cache.add_node(node1)
        cache.add_node(node2)
        cache.add_node(node3)
        
        # Definir valor
        await cache.set("test-key", "test-value")
        
        # Simular falha de nó
        node1.status = CacheNodeStatus.OFFLINE
        
        # Verificar se ainda consegue obter o valor
        value = await cache.get("test-key")
        assert value == "test-value"
        
        # Verificar status dos nós
        status = cache.get_node_status()
        assert status["node-1"]["status"] == "offline"
        assert status["node-2"]["status"] == "online"
        assert status["node-3"]["status"] == "online"
    
    @pytest.mark.asyncio
    async def test_consistency_levels_comparison(self):
        """Testa comparação entre níveis de consistência"""
        # Cache com consistência eventual
        eventual_cache = create_distributed_cache(CacheConsistencyLevel.EVENTUAL)
        
        # Cache com consistência forte
        strong_cache = create_distributed_cache(CacheConsistencyLevel.STRONG)
        
        # Adicionar nós
        node = CacheNode(id="node-1", host="localhost", port=6379)
        eventual_cache.add_node(node)
        strong_cache.add_node(node)
        
        # Definir valores
        await eventual_cache.set("key", "value")
        await strong_cache.set("key", "value")
        
        # Obter valores
        eventual_value = await eventual_cache.get("key")
        strong_value = await strong_cache.get("key")
        
        assert eventual_value == "value"
        assert strong_value == "value"
        
        # Verificar se strong cache faz verificação de consistência
        entry = strong_cache.cache["key"]
        is_consistent = await strong_cache._verify_consistency("key", entry)
        assert isinstance(is_consistent, bool)


if __name__ == "__main__":
    pytest.main([__file__]) 