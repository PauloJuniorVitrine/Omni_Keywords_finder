"""
Testes Unitários para Memory Management
Sistema de Gerenciamento de Memória - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de gerenciamento de memória
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import time
import threading
import gc
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.performance.memory_management import (
    MemoryManager, MemoryConfig, MemoryPolicy, CacheLevel,
    CacheItem, MemoryStats, create_memory_manager
)


class TestMemoryConfig:
    """Testes para MemoryConfig"""
    
    def test_memory_config_initialization(self):
        """Testa inicialização de MemoryConfig"""
        config = MemoryConfig(
            max_memory_mb=2048,
            max_cache_size=2000,
            gc_threshold=0.9,
            cleanup_interval=600,
            enable_monitoring=True,
            enable_compression=True,
            compression_threshold=2048,
            cache_policy=MemoryPolicy.LFU,
            enable_persistence=True,
            persistence_path="cache/",
            enable_stats=True,
            stats_interval=120
        )
        
        assert config.max_memory_mb == 2048
        assert config.max_cache_size == 2000
        assert config.gc_threshold == 0.9
        assert config.cleanup_interval == 600
        assert config.enable_monitoring is True
        assert config.enable_compression is True
        assert config.compression_threshold == 2048
        assert config.cache_policy == MemoryPolicy.LFU
        assert config.enable_persistence is True
        assert config.persistence_path == "cache/"
        assert config.enable_stats is True
        assert config.stats_interval == 120
    
    def test_memory_config_validation_max_memory_negative(self):
        """Testa validação de max memory negativo"""
        with pytest.raises(ValueError, match="Max memory deve ser positivo"):
            MemoryConfig(max_memory_mb=0)
    
    def test_memory_config_validation_max_cache_size_negative(self):
        """Testa validação de max cache size negativo"""
        with pytest.raises(ValueError, match="Max cache size deve ser positivo"):
            MemoryConfig(max_cache_size=0)
    
    def test_memory_config_validation_gc_threshold_invalid(self):
        """Testa validação de gc threshold inválido"""
        with pytest.raises(ValueError, match="GC threshold deve estar entre 0 e 1"):
            MemoryConfig(gc_threshold=1.5)
    
    def test_memory_config_validation_cleanup_interval_negative(self):
        """Testa validação de cleanup interval negativo"""
        with pytest.raises(ValueError, match="Cleanup interval deve ser positivo"):
            MemoryConfig(cleanup_interval=0)
    
    def test_memory_config_validation_compression_threshold_negative(self):
        """Testa validação de compression threshold negativo"""
        with pytest.raises(ValueError, match="Compression threshold deve ser positivo"):
            MemoryConfig(compression_threshold=0)
    
    def test_memory_config_validation_stats_interval_negative(self):
        """Testa validação de stats interval negativo"""
        with pytest.raises(ValueError, match="Stats interval deve ser positivo"):
            MemoryConfig(stats_interval=0)


class TestCacheItem:
    """Testes para CacheItem"""
    
    def test_cache_item_initialization(self):
        """Testa inicialização de CacheItem"""
        item = CacheItem(
            key="test-key",
            value="test-value",
            ttl=3600,
            size_bytes=1024,
            compressed=False,
            metadata={"source": "test"}
        )
        
        assert item.key == "test-key"
        assert item.value == "test-value"
        assert item.ttl == 3600
        assert item.size_bytes == 1024
        assert item.compressed is False
        assert item.metadata == {"source": "test"}
        assert item.access_count == 0
    
    def test_is_expired_not_expired(self):
        """Testa verificação de expiração - não expirado"""
        item = CacheItem(
            key="test",
            value="value",
            ttl=3600,
            created_at=datetime.utcnow()
        )
        
        assert item.is_expired() is False
    
    def test_is_expired_expired(self):
        """Testa verificação de expiração - expirado"""
        item = CacheItem(
            key="test",
            value="value",
            ttl=1,
            created_at=datetime.utcnow() - timedelta(seconds=2)
        )
        
        assert item.is_expired() is True
    
    def test_is_expired_no_ttl(self):
        """Testa verificação de expiração - sem TTL"""
        item = CacheItem(
            key="test",
            value="value",
            ttl=None
        )
        
        assert item.is_expired() is False
    
    def test_update_access(self):
        """Testa atualização de acesso"""
        item = CacheItem(key="test", value="value")
        original_count = item.access_count
        original_time = item.accessed_at
        
        time.sleep(0.1)  # Pequeno delay para garantir diferença de tempo
        item.update_access()
        
        assert item.access_count == original_count + 1
        assert item.accessed_at > original_time
    
    def test_get_age(self):
        """Testa cálculo de idade"""
        item = CacheItem(key="test", value="value")
        
        age = item.get_age()
        assert age >= 0
    
    def test_get_idle_time(self):
        """Testa cálculo de tempo ocioso"""
        item = CacheItem(key="test", value="value")
        
        idle_time = item.get_idle_time()
        assert idle_time >= 0


class TestMemoryStats:
    """Testes para MemoryStats"""
    
    def test_memory_stats_initialization(self):
        """Testa inicialização de MemoryStats"""
        stats = MemoryStats(
            total_memory_mb=8192.0,
            used_memory_mb=4096.0,
            available_memory_mb=4096.0,
            memory_percentage=0.5,
            cache_size=100,
            cache_hits=80,
            cache_misses=20,
            hit_rate=0.8,
            evictions=5,
            compressions=3,
            gc_runs=2
        )
        
        assert stats.total_memory_mb == 8192.0
        assert stats.used_memory_mb == 4096.0
        assert stats.available_memory_mb == 4096.0
        assert stats.memory_percentage == 0.5
        assert stats.cache_size == 100
        assert stats.cache_hits == 80
        assert stats.cache_misses == 20
        assert stats.hit_rate == 0.8
        assert stats.evictions == 5
        assert stats.compressions == 3
        assert stats.gc_runs == 2
    
    def test_update_hit_rate_with_requests(self):
        """Testa atualização de taxa de hit com requisições"""
        stats = MemoryStats(cache_hits=80, cache_misses=20)
        
        stats.update_hit_rate()
        assert stats.hit_rate == 0.8
    
    def test_update_hit_rate_no_requests(self):
        """Testa atualização de taxa de hit sem requisições"""
        stats = MemoryStats(cache_hits=0, cache_misses=0)
        
        stats.update_hit_rate()
        assert stats.hit_rate == 0.0


class TestMemoryManager:
    """Testes para MemoryManager"""
    
    @pytest.fixture
    def memory_manager(self):
        """Instância de MemoryManager para testes"""
        config = MemoryConfig(
            max_memory_mb=512,
            max_cache_size=10,
            cleanup_interval=1,
            stats_interval=1,
            enable_monitoring=False
        )
        return MemoryManager(config)
    
    def test_memory_manager_initialization(self):
        """Testa inicialização do MemoryManager"""
        manager = MemoryManager()
        
        assert manager.config is not None
        assert len(manager.caches) == 3
        assert CacheLevel.L1 in manager.caches
        assert CacheLevel.L2 in manager.caches
        assert CacheLevel.L3 in manager.caches
        assert manager.running is False
        assert manager.stats is not None
    
    def test_get_nonexistent_item(self, memory_manager):
        """Testa obtenção de item inexistente"""
        value = memory_manager.get("nonexistent")
        assert value is None
    
    def test_set_and_get_item(self, memory_manager):
        """Testa definição e obtenção de item"""
        # Definir item
        success = memory_manager.set("test-key", "test-value")
        assert success is True
        
        # Obter item
        value = memory_manager.get("test-key")
        assert value == "test-value"
    
    def test_set_item_with_ttl(self, memory_manager):
        """Testa definição de item com TTL"""
        # Definir item com TTL curto
        success = memory_manager.set("test-key", "test-value", ttl=1)
        assert success is True
        
        # Verificar que existe
        assert memory_manager.exists("test-key") is True
        
        # Aguardar expiração
        time.sleep(1.1)
        
        # Verificar que expirou
        assert memory_manager.exists("test-key") is False
        assert memory_manager.get("test-key") is None
    
    def test_set_item_with_metadata(self, memory_manager):
        """Testa definição de item com metadados"""
        metadata = {"source": "test", "priority": "high"}
        
        success = memory_manager.set("test-key", "test-value", metadata=metadata)
        assert success is True
        
        # Verificar que foi definido
        assert memory_manager.exists("test-key") is True
    
    def test_delete_item(self, memory_manager):
        """Testa remoção de item"""
        # Definir item
        memory_manager.set("test-key", "test-value")
        assert memory_manager.exists("test-key") is True
        
        # Remover item
        success = memory_manager.delete("test-key")
        assert success is True
        
        # Verificar que foi removido
        assert memory_manager.exists("test-key") is False
    
    def test_delete_nonexistent_item(self, memory_manager):
        """Testa remoção de item inexistente"""
        success = memory_manager.delete("nonexistent")
        assert success is False
    
    def test_clear_cache_level(self, memory_manager):
        """Testa limpeza de nível específico do cache"""
        # Definir itens em diferentes níveis
        memory_manager.set("key1", "value1", level=CacheLevel.L1)
        memory_manager.set("key2", "value2", level=CacheLevel.L2)
        
        # Limpar apenas L1
        removed = memory_manager.clear(level=CacheLevel.L1)
        assert removed == 1
        
        # Verificar que L1 foi limpo
        assert memory_manager.exists("key1", level=CacheLevel.L1) is False
        assert memory_manager.exists("key2", level=CacheLevel.L2) is True
    
    def test_clear_all_caches(self, memory_manager):
        """Testa limpeza de todos os caches"""
        # Definir itens em diferentes níveis
        memory_manager.set("key1", "value1", level=CacheLevel.L1)
        memory_manager.set("key2", "value2", level=CacheLevel.L2)
        memory_manager.set("key3", "value3", level=CacheLevel.L3)
        
        # Limpar todos
        removed = memory_manager.clear()
        assert removed == 3
        
        # Verificar que todos foram limpos
        assert memory_manager.exists("key1", level=CacheLevel.L1) is False
        assert memory_manager.exists("key2", level=CacheLevel.L2) is False
        assert memory_manager.exists("key3", level=CacheLevel.L3) is False
    
    def test_exists_item(self, memory_manager):
        """Testa verificação de existência de item"""
        # Item não existe
        assert memory_manager.exists("nonexistent") is False
        
        # Definir item
        memory_manager.set("test-key", "test-value")
        assert memory_manager.exists("test-key") is True
    
    def test_get_keys(self, memory_manager):
        """Testa obtenção de chaves"""
        # Definir itens
        memory_manager.set("key1", "value1")
        memory_manager.set("key2", "value2")
        
        keys = memory_manager.get_keys()
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys
    
    def test_get_stats(self, memory_manager):
        """Testa obtenção de estatísticas"""
        # Definir alguns itens
        memory_manager.set("key1", "value1")
        memory_manager.set("key2", "value2")
        
        # Obter estatísticas
        stats = memory_manager.get_stats()
        
        assert "total_memory_mb" in stats
        assert "used_memory_mb" in stats
        assert "available_memory_mb" in stats
        assert "memory_percentage" in stats
        assert "cache_size" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "hit_rate" in stats
        assert "evictions" in stats
        assert "compressions" in stats
        assert "gc_runs" in stats
        assert "cache_levels" in stats
    
    def test_cache_hit_miss_stats(self, memory_manager):
        """Testa estatísticas de hit/miss"""
        # Definir item
        memory_manager.set("test-key", "test-value")
        
        # Hit
        memory_manager.get("test-key")
        
        # Miss
        memory_manager.get("nonexistent")
        
        stats = memory_manager.get_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1
        assert stats["hit_rate"] == 0.5
    
    def test_start_stop_manager(self, memory_manager):
        """Testa início e parada do gerenciador"""
        # Iniciar
        memory_manager.start()
        assert memory_manager.running is True
        
        # Parar
        memory_manager.stop()
        assert memory_manager.running is False
    
    def test_force_gc(self, memory_manager):
        """Testa execução forçada do GC"""
        result = memory_manager.force_gc()
        
        assert "collected_objects" in result
        assert "memory_before" in result
        assert "memory_after" in result
        assert "timestamp" in result
        assert memory_manager.stats.gc_runs > 0
    
    def test_cache_eviction_lru(self, memory_manager):
        """Testa evição de cache com política LRU"""
        # Configurar cache pequeno
        memory_manager.config.max_cache_size = 2
        
        # Definir 3 itens (deve evictar o primeiro)
        memory_manager.set("key1", "value1")
        memory_manager.set("key2", "value2")
        memory_manager.set("key3", "value3")
        
        # Verificar que key1 foi evictado
        assert memory_manager.exists("key1") is False
        assert memory_manager.exists("key2") is True
        assert memory_manager.exists("key3") is True
        
        # Verificar estatísticas
        stats = memory_manager.get_stats()
        assert stats["evictions"] > 0
    
    def test_cache_eviction_lfu(self, memory_manager):
        """Testa evição de cache com política LFU"""
        memory_manager.config.cache_policy = MemoryPolicy.LFU
        memory_manager.config.max_cache_size = 2
        
        # Definir itens
        memory_manager.set("key1", "value1")
        memory_manager.set("key2", "value2")
        
        # Acessar key1 várias vezes
        memory_manager.get("key1")
        memory_manager.get("key1")
        memory_manager.get("key1")
        
        # Acessar key2 uma vez
        memory_manager.get("key2")
        
        # Adicionar terceiro item (deve evictar key2 que foi menos usado)
        memory_manager.set("key3", "value3")
        
        # Verificar que key2 foi evictado
        assert memory_manager.exists("key1") is True
        assert memory_manager.exists("key2") is False
        assert memory_manager.exists("key3") is True
    
    def test_cache_eviction_fifo(self, memory_manager):
        """Testa evição de cache com política FIFO"""
        memory_manager.config.cache_policy = MemoryPolicy.FIFO
        memory_manager.config.max_cache_size = 2
        
        # Definir itens
        memory_manager.set("key1", "value1")
        memory_manager.set("key2", "value2")
        memory_manager.set("key3", "value3")
        
        # Verificar que key1 foi evictado (primeiro a entrar)
        assert memory_manager.exists("key1") is False
        assert memory_manager.exists("key2") is True
        assert memory_manager.exists("key3") is True
    
    def test_cache_eviction_ttl(self, memory_manager):
        """Testa evição de cache com política TTL"""
        memory_manager.config.cache_policy = MemoryPolicy.TTL
        memory_manager.config.max_cache_size = 2
        
        # Definir itens com TTLs diferentes
        memory_manager.set("key1", "value1", ttl=10)
        memory_manager.set("key2", "value2", ttl=5)
        memory_manager.set("key3", "value3", ttl=15)
        
        # Aguardar um pouco
        time.sleep(0.1)
        
        # Adicionar quarto item (deve evictar o mais antigo)
        memory_manager.set("key4", "value4", ttl=20)
        
        # Verificar que algum item foi evictado
        assert memory_manager.get_stats()["evictions"] > 0
    
    def test_cache_eviction_adaptive(self, memory_manager):
        """Testa evição de cache com política adaptativa"""
        memory_manager.config.cache_policy = MemoryPolicy.ADAPTIVE
        memory_manager.config.max_cache_size = 2
        
        # Definir itens
        memory_manager.set("key1", "value1")
        memory_manager.set("key2", "value2")
        
        # Acessar key1 várias vezes
        memory_manager.get("key1")
        memory_manager.get("key1")
        
        # Adicionar terceiro item
        memory_manager.set("key3", "value3")
        
        # Verificar que algum item foi evictado
        assert memory_manager.get_stats()["evictions"] > 0
    
    def test_compression_enabled(self, memory_manager):
        """Testa compressão habilitada"""
        memory_manager.config.enable_compression = True
        memory_manager.config.compression_threshold = 10  # Baixo para teste
        
        # Definir item grande
        large_value = "x" * 100
        
        success = memory_manager.set("large-key", large_value)
        assert success is True
        
        # Verificar que foi definido
        value = memory_manager.get("large-key")
        assert value == large_value
    
    def test_different_cache_levels(self, memory_manager):
        """Testa diferentes níveis de cache"""
        # Definir itens em diferentes níveis
        memory_manager.set("key1", "value1", level=CacheLevel.L1)
        memory_manager.set("key2", "value2", level=CacheLevel.L2)
        memory_manager.set("key3", "value3", level=CacheLevel.L3)
        
        # Verificar que existem nos níveis corretos
        assert memory_manager.exists("key1", level=CacheLevel.L1) is True
        assert memory_manager.exists("key2", level=CacheLevel.L2) is True
        assert memory_manager.exists("key3", level=CacheLevel.L3) is True
        
        # Verificar que não existem em outros níveis
        assert memory_manager.exists("key1", level=CacheLevel.L2) is False
        assert memory_manager.exists("key2", level=CacheLevel.L3) is False
        assert memory_manager.exists("key3", level=CacheLevel.L1) is False
    
    def test_callback_on_eviction(self, memory_manager):
        """Testa callback de evição"""
        evicted_key = None
        evicted_value = None
        
        def on_eviction(key, value):
            nonlocal evicted_key, evicted_value
            evicted_key = key
            evicted_value = value
        
        memory_manager.on_eviction = on_eviction
        memory_manager.config.max_cache_size = 1
        
        # Definir dois itens (deve evictar o primeiro)
        memory_manager.set("key1", "value1")
        memory_manager.set("key2", "value2")
        
        # Verificar callback
        assert evicted_key == "key1"
        assert evicted_value == "value1"
    
    def test_callback_on_compression(self, memory_manager):
        """Testa callback de compressão"""
        compressed_key = None
        original_size = None
        compressed_size = None
        
        def on_compression(key, orig_size, comp_size):
            nonlocal compressed_key, original_size, compressed_size
            compressed_key = key
            original_size = orig_size
            compressed_size = comp_size
        
        memory_manager.on_compression = on_compression
        memory_manager.config.enable_compression = True
        memory_manager.config.compression_threshold = 10
        
        # Definir item grande
        large_value = "x" * 100
        memory_manager.set("large-key", large_value)
        
        # Verificar callback
        assert compressed_key == "large-key"
        assert original_size > 0
        assert compressed_size > 0
    
    def test_callback_on_gc(self, memory_manager):
        """Testa callback de GC"""
        gc_memory_percentage = None
        
        def on_gc(memory_percentage):
            nonlocal gc_memory_percentage
            gc_memory_percentage = memory_percentage
        
        memory_manager.on_gc = on_gc
        
        # Executar GC
        memory_manager.force_gc()
        
        # Verificar callback
        assert gc_memory_percentage is not None
        assert 0 <= gc_memory_percentage <= 1


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_memory_manager_default(self):
        """Testa criação de MemoryManager com configurações padrão"""
        manager = create_memory_manager()
        
        assert isinstance(manager, MemoryManager)
        assert manager.config is not None
    
    def test_create_memory_manager_custom(self):
        """Testa criação de MemoryManager com configurações customizadas"""
        config = MemoryConfig(
            max_memory_mb=2048,
            max_cache_size=500,
            cache_policy=MemoryPolicy.LFU
        )
        
        manager = create_memory_manager(config)
        
        assert manager.config.max_memory_mb == 2048
        assert manager.config.max_cache_size == 500
        assert manager.config.cache_policy == MemoryPolicy.LFU


class TestMemoryManagerIntegration:
    """Testes de integração para Memory Manager"""
    
    def test_complete_workflow(self):
        """Testa workflow completo do gerenciador de memória"""
        config = MemoryConfig(
            max_memory_mb=256,
            max_cache_size=5,
            cleanup_interval=1,
            stats_interval=1,
            enable_monitoring=False
        )
        
        manager = MemoryManager(config)
        manager.start()
        
        try:
            # Definir itens
            manager.set("key1", "value1", ttl=5)
            manager.set("key2", "value2", metadata={"priority": "high"})
            manager.set("key3", "value3", level=CacheLevel.L2)
            
            # Verificar existência
            assert manager.exists("key1") is True
            assert manager.exists("key2") is True
            assert manager.exists("key3", level=CacheLevel.L2) is True
            
            # Obter itens
            assert manager.get("key1") == "value1"
            assert manager.get("key2") == "value2"
            assert manager.get("key3", level=CacheLevel.L2) == "value3"
            
            # Verificar estatísticas
            stats = manager.get_stats()
            assert stats["cache_size"] == 3
            assert stats["cache_hits"] == 3
            assert stats["hit_rate"] == 1.0
            
            # Aguardar limpeza automática
            time.sleep(1.5)
            
            # Verificar que key1 expirou
            assert manager.exists("key1") is False
            
        finally:
            manager.stop()
    
    def test_memory_pressure_handling(self):
        """Testa tratamento de pressão de memória"""
        config = MemoryConfig(
            max_memory_mb=1,  # Muito baixo para forçar GC
            max_cache_size=10,
            gc_threshold=0.1,  # Baixo para forçar GC
            enable_monitoring=False
        )
        
        manager = MemoryManager(config)
        
        # Tentar definir muitos itens
        for i in range(20):
            success = manager.set(f"key{i}", "value" * 1000)
            if not success:
                break
        
        # Verificar que alguns itens foram definidos
        stats = manager.get_stats()
        assert stats["cache_size"] > 0
        
        # Verificar que GC foi executado
        assert stats["gc_runs"] > 0
    
    def test_concurrent_access(self):
        """Testa acesso concorrente ao cache"""
        manager = MemoryManager(MemoryConfig(enable_monitoring=False))
        
        def worker(worker_id):
            for i in range(10):
                key = f"worker{worker_id}_key{i}"
                manager.set(key, f"value{i}")
                value = manager.get(key)
                assert value == f"value{i}"
        
        # Criar threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar threads terminarem
        for thread in threads:
            thread.join()
        
        # Verificar que todos os itens foram definidos
        stats = manager.get_stats()
        assert stats["cache_size"] == 30  # 3 workers * 10 itens cada


if __name__ == "__main__":
    pytest.main([__file__]) 