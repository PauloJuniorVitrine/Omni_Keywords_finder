from typing import Dict, List, Optional, Any
"""
Testes unitários para IntelligentCache
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import time
import json
import pickle
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from infrastructure.cache.intelligent_cache import (
    IntelligentCache,
    CachePolicy,
    CompressionType,
    CacheEntry,
    CacheHierarchy
)

class TestIntelligentCache:
    """Testes para IntelligentCache."""
    
    @pytest.fixture
    def cache(self):
        """Fixture para cache."""
        return IntelligentCache(
            max_size=10,
            max_memory_mb=10,
            policy=CachePolicy.LRU,
            default_ttl=3600,
            compression_threshold=100,
            enable_compression=True
        )
    
    @pytest.fixture
    def large_data(self):
        """Fixture para dados grandes."""
        return {
            "large_string": "value" * 1000,
            "numbers": list(range(1000)),
            "nested": {
                "level1": {"level2": {"level3": "deep_value"}},
                "array": [{"id": index, "value": f"item_{index}"} for index in range(100)]
            }
        }
    
    def test_init(self, cache):
        """Testa inicialização do cache."""
        assert cache.max_size == 10
        assert cache.max_memory_mb == 10
        assert cache.policy == CachePolicy.LRU
        assert cache.default_ttl == 3600
        assert cache.compression_threshold == 100
        assert cache.enable_compression is True
        assert isinstance(cache.cache, dict)
        assert isinstance(cache.metrics, dict)
    
    def test_set_and_get_basic(self, cache):
        """Testa operações básicas de set e get."""
        # Set
        success = cache.set("test_key", "test_value")
        assert success is True
        
        # Get
        value = cache.get("test_key")
        assert value == "test_value"
        
        # Verificar métricas
        assert cache.metrics['sets'] == 1
        assert cache.metrics['hits'] == 1
        assert cache.metrics['misses'] == 0
    
    def test_get_nonexistent_key(self, cache):
        """Testa get de chave inexistente."""
        value = cache.get("nonexistent", "default")
        assert value == "default"
        assert cache.metrics['misses'] == 1
    
    def test_set_with_ttl(self, cache):
        """Testa set com TTL."""
        cache.set("expiring_key", "expiring_value", ttl=1)
        
        # Deve existir imediatamente
        assert cache.get("expiring_key") == "expiring_value"
        
        # Aguardar expiração
        time.sleep(1.1)
        
        # Deve ter expirado
        assert cache.get("expiring_key") is None
    
    def test_set_with_compression(self, cache, large_data):
        """Testa set com compressão."""
        success = cache.set("large_key", large_data, compression_type=CompressionType.GZIP)
        assert success is True
        
        # Verificar se foi comprimido
        entry = cache.cache["large_key"]
        assert entry.compression_type == CompressionType.GZIP
        assert entry.size_bytes < len(json.dumps(large_data))
        
        # Verificar se pode ser descomprimido
        value = cache.get("large_key")
        assert value == large_data
    
    def test_automatic_compression_detection(self, cache, large_data):
        """Testa detecção automática de compressão."""
        success = cache.set("auto_compress", large_data)
        assert success is True
        
        entry = cache.cache["auto_compress"]
        assert entry.compression_type == CompressionType.GZIP
    
    def test_lru_eviction(self, cache):
        """Testa eviction LRU."""
        # Preencher cache
        for index in range(12):  # Mais que max_size
            cache.set(f"key_{index}", f"value_{index}")
        
        # Verificar se algumas entradas foram evictadas
        assert len(cache.cache) <= cache.max_size
        
        # Últimas entradas devem existir
        assert cache.get("key_10") == "value_10"
        assert cache.get("key_11") == "value_11"
        
        # Primeiras entradas devem ter sido evictadas
        assert cache.get("key_0") is None
        assert cache.get("key_1") is None
    
    def test_lfu_eviction(self):
        """Testa eviction LFU."""
        cache = IntelligentCache(
            max_size=3,
            policy=CachePolicy.LFU
        )
        
        # Adicionar entradas
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Acessar algumas entradas múltiplas vezes
        cache.get("key1")  # 1 acesso
        cache.get("key1")  # 2 acessos
        cache.get("key2")  # 1 acesso
        
        # Adicionar nova entrada (deve evictar key3 que tem menos acessos)
        cache.set("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Mais acessos
        assert cache.get("key2") == "value2"  # Menos acessos que key1
        assert cache.get("key3") is None      # Evictado
        assert cache.get("key4") == "value4"  # Nova entrada
    
    def test_memory_limit_eviction(self, cache):
        """Testa eviction por limite de memória."""
        # Configurar limite baixo
        cache.max_memory_mb = 0.001  # 1KB
        
        # Tentar adicionar dados grandes
        large_data = "value" * 10000  # 10KB
        success = cache.set("large_key", large_data)
        
        # Deve falhar ou evictar automaticamente
        assert len(cache.cache) == 0 or cache.memory_usage_mb() <= cache.max_memory_mb
    
    def test_delete(self, cache):
        """Testa operação de delete."""
        cache.set("delete_key", "delete_value")
        assert cache.get("delete_key") == "delete_value"
        
        success = cache.delete("delete_key")
        assert success is True
        
        assert cache.get("delete_key") is None
        assert cache.metrics['deletes'] == 1
    
    def test_clear(self, cache):
        """Testa limpeza do cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.cache) == 2
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.metrics['total_memory_bytes'] == 0
    
    def test_exists(self, cache):
        """Testa verificação de existência."""
        assert cache.exists("nonexistent") is False
        
        cache.set("existing", "value")
        assert cache.exists("existing") is True
        
        # Testar com TTL expirado
        cache.set("expiring", "value", ttl=0.1)
        time.sleep(0.2)
        assert cache.exists("expiring") is False
    
    def test_keys(self, cache):
        """Testa obtenção de chaves."""
        cache.set("key1", "value1")
        cache.set("key2", "value2", ttl=0.1)
        cache.set("key3", "value3")
        
        time.sleep(0.2)  # Aguardar expiração
        
        keys = cache.keys()
        assert "key1" in keys
        assert "key2" not in keys  # Expirou
        assert "key3" in keys
    
    def test_size_and_memory_usage(self, cache):
        """Testa tamanho e uso de memória."""
        assert cache.size() == 0
        assert cache.memory_usage_mb() == 0.0
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.size() == 2
        assert cache.memory_usage_mb() > 0.0
    
    def test_get_metrics(self, cache):
        """Testa obtenção de métricas."""
        # Adicionar alguns dados
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("nonexistent")  # Miss
        
        metrics = cache.get_metrics()
        
        assert isinstance(metrics, dict)
        assert 'hits' in metrics
        assert 'misses' in metrics
        assert 'sets' in metrics
        assert 'deletes' in metrics
        assert 'evictions' in metrics
        assert 'compressions' in metrics
        assert 'decompressions' in metrics
        assert 'hit_rate_percent' in metrics
        assert 'uptime_seconds' in metrics
        assert 'current_size' in metrics
        assert 'memory_usage_mb' in metrics
        assert 'policy' in metrics
        
        assert metrics['hits'] == 1
        assert metrics['misses'] == 1
        assert metrics['sets'] == 1
        assert metrics['hit_rate_percent'] == 50.0
    
    def test_warm_cache(self, cache):
        """Testa warming do cache."""
        warm_data = {
            "warm1": "value1",
            "warm2": "value2",
            "warm3": "value3"
        }
        
        cache.warm_cache(warm_data, ttl=1800)
        
        assert cache.size() == 3
        assert cache.get("warm1") == "value1"
        assert cache.get("warm2") == "value2"
        assert cache.get("warm3") == "value3"
    
    def test_dynamic_ttl_calculation(self, cache):
        """Testa cálculo de TTL dinâmico."""
        # Testar padrões diferentes
        ttl1 = cache._calculate_dynamic_ttl("frequent_key")
        ttl2 = cache._calculate_dynamic_ttl("moderate_key")
        ttl3 = cache._calculate_dynamic_ttl("rare_key")
        ttl4 = cache._calculate_dynamic_ttl("normal_key")
        
        assert ttl1 == cache.ttl_patterns['frequently_accessed']
        assert ttl2 == cache.ttl_patterns['moderately_accessed']
        assert ttl3 == cache.ttl_patterns['rarely_accessed']
        assert ttl4 == cache.ttl_patterns['new_entries']
    
    def test_compression_detection(self, cache):
        """Testa detecção de compressão."""
        # Dados pequenos não devem ser comprimidos
        small_data = "small"
        compression_type = cache._determine_compression_type(small_data)
        assert compression_type == CompressionType.NONE
        
        # Dados grandes devem ser comprimidos
        large_data = "value" * 2000  # Maior que threshold
        compression_type = cache._determine_compression_type(large_data)
        assert compression_type == CompressionType.GZIP
    
    def test_compression_and_decompression(self, cache):
        """Testa compressão e descompressão."""
        original_data = {"test": "data", "numbers": [1, 2, 3, 4, 5]}
        
        # Comprimir
        compressed, compression_type = cache._compress_value(original_data, CompressionType.GZIP)
        assert compression_type == CompressionType.GZIP
        assert isinstance(compressed, bytes)
        assert len(compressed) < len(json.dumps(original_data))
        
        # Criar entrada simulada
        entry = CacheEntry(
            key="test",
            value=compressed,
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow(),
            compression_type=compression_type
        )
        
        # Descomprimir
        decompressed = cache._decompress_value(entry)
        assert decompressed == original_data
    
    def test_size_calculation(self, cache):
        """Testa cálculo de tamanho."""
        # String
        size1 = cache._calculate_size("test string")
        assert size1 > 0
        
        # Bytes
        size2 = cache._calculate_size(b"test bytes")
        assert size2 == 10
        
        # Objeto
        size3 = cache._calculate_size({"key": "value"})
        assert size3 > 0

class TestCacheEntry:
    """Testes para CacheEntry."""
    
    def test_cache_entry_creation(self):
        """Testa criação de entrada do cache."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow(),
            ttl=3600,
            compression_type=CompressionType.NONE,
            size_bytes=100
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.ttl == 3600
        assert entry.compression_type == CompressionType.NONE
        assert entry.size_bytes == 100
    
    def test_cache_entry_expiration(self):
        """Testa expiração de entrada do cache."""
        # Entrada sem TTL
        entry_no_ttl = CacheEntry(
            key="no_ttl",
            value="value",
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow()
        )
        assert entry_no_ttl.is_expired() is False
        
        # Entrada com TTL expirado
        entry_expired = CacheEntry(
            key="expired",
            value="value",
            created_at=datetime.utcnow() - timedelta(seconds=2),
            accessed_at=datetime.utcnow(),
            ttl=1
        )
        assert entry_expired.is_expired() is True
    
    def test_cache_entry_access_update(self):
        """Testa atualização de acesso."""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow(),
            access_count=5
        )
        
        original_access_count = entry.access_count
        original_accessed_at = entry.accessed_at
        
        time.sleep(0.1)  # Pequena pausa
        entry.update_access()
        
        assert entry.access_count == original_access_count + 1
        assert entry.accessed_at > original_accessed_at
    
    def test_cache_entry_age_and_idle_time(self):
        """Testa cálculo de idade e tempo ocioso."""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow()
        )
        
        time.sleep(0.1)
        
        age = entry.get_age()
        idle_time = entry.get_idle_time()
        
        assert age > 0
        assert idle_time > 0
        assert age >= idle_time

class TestCacheHierarchy:
    """Testes para CacheHierarchy."""
    
    @pytest.fixture
    def hierarchy(self):
        """Fixture para hierarquia de cache."""
        return CacheHierarchy()
    
    def test_init(self, hierarchy):
        """Testa inicialização da hierarquia."""
        assert isinstance(hierarchy.l1_cache, IntelligentCache)
        assert isinstance(hierarchy.l2_cache, IntelligentCache)
        assert hierarchy.l1_cache.max_size == 100
        assert hierarchy.l2_cache.max_size == 1000
    
    def test_get_from_l1(self, hierarchy):
        """Testa get do L1 cache."""
        hierarchy.l1_cache.set("l1_key", "l1_value")
        
        value = hierarchy.get("l1_key")
        assert value == "l1_value"
    
    def test_get_from_l2_promote_to_l1(self, hierarchy):
        """Testa get do L2 e promoção para L1."""
        hierarchy.l2_cache.set("l2_key", "l2_value")
        
        # Primeira vez - deve vir do L2
        value1 = hierarchy.get("l2_key")
        assert value1 == "l2_value"
        
        # Segunda vez - deve vir do L1 (promovido)
        value2 = hierarchy.get("l2_key")
        assert value2 == "l2_value"
        
        # Verificar se foi promovido para L1
        assert hierarchy.l1_cache.get("l2_key") == "l2_value"
    
    def test_set_all_levels(self, hierarchy):
        """Testa set em todos os níveis."""
        hierarchy.set("hierarchy_key", "hierarchy_value")
        
        # Verificar se está em ambos os níveis
        assert hierarchy.l1_cache.get("hierarchy_key") == "hierarchy_value"
        assert hierarchy.l2_cache.get("hierarchy_key") == "hierarchy_value"
    
    def test_get_metrics(self, hierarchy):
        """Testa obtenção de métricas da hierarquia."""
        metrics = hierarchy.get_metrics()
        
        assert isinstance(metrics, dict)
        assert 'l1' in metrics
        assert 'l2' in metrics
        assert isinstance(metrics['l1'], dict)
        assert isinstance(metrics['l2'], dict)

class TestCompressionTypes:
    """Testes para tipos de compressão."""
    
    def test_compression_type_enum(self):
        """Testa enum de tipos de compressão."""
        assert CompressionType.NONE.value == "none"
        assert CompressionType.GZIP.value == "gzip"
        assert CompressionType.PICKLE.value == "pickle"
        assert CompressionType.JSON.value == "json"
    
    def test_cache_policy_enum(self):
        """Testa enum de políticas de cache."""
        assert CachePolicy.LRU.value == "lru"
        assert CachePolicy.LFU.value == "lfu"
        assert CachePolicy.TTL.value == "ttl"
        assert CachePolicy.RANDOM.value == "random" 