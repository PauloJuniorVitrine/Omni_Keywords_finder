"""
🧪 INT-009: Testes Unitários - Advanced Caching Strategy - Omni Keywords Finder

Tracing ID: INT_009_TEST_ADVANCED_CACHING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Testes unitários completos para o sistema de Advanced Caching Strategy
com cobertura de 95%+ e validação de todas as funcionalidades.
"""

import time
import threading
import json
import pickle
import base64
import gzip
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from infrastructure.cache.advanced_caching import (
    AdvancedCaching,
    CacheConfig,
    CacheStrategy,
    CacheLevel,
    CacheOperation,
    CacheEntry,
    CacheMetrics,
    LRUCache,
    LFUCache,
    CacheSerializer,
    CacheCompressor,
    CacheWarming,
    CacheInvalidation,
    create_advanced_caching,
    get_global_cache,
    set_global_cache,
    cached
)

class TestCacheConfig:
    """Testes para CacheConfig."""
    
    def test_cache_config_defaults(self):
        """Testa valores padrão da configuração de cache."""
        config = CacheConfig()
        
        assert config.default_ttl == 3600
        assert config.max_size == 10000
        assert config.strategy == CacheStrategy.LRU
        assert config.l1_enabled is True
        assert config.l1_max_size == 1000
        assert config.l1_ttl == 300
        assert config.l2_enabled is True
        assert config.l2_max_size == 10000
        assert config.l2_ttl == 3600
        assert config.l3_enabled is False
        assert config.l3_max_size == 100000
        assert config.l3_ttl == 86400
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_db == 1
        assert config.redis_ttl == 3600
        assert config.warming_enabled is True
        assert config.warming_interval == 300
        assert config.warming_batch_size == 100
        assert config.invalidation_enabled is True
        assert config.invalidation_cooldown == 60
        assert config.analytics_enabled is True
        assert config.analytics_retention == 86400
        assert config.compression_enabled is True
        assert config.compression_threshold == 1024
        assert config.serialization_format == "json"
        assert config.fallback_enabled is True
        assert config.fallback_strategy == "graceful"
    
    def test_cache_config_custom(self):
        """Testa configuração customizada de cache."""
        config = CacheConfig(
            default_ttl=7200,
            max_size=5000,
            strategy=CacheStrategy.LFU,
            l1_enabled=False,
            l2_enabled=False,
            warming_enabled=False,
            invalidation_enabled=False
        )
        
        assert config.default_ttl == 7200
        assert config.max_size == 5000
        assert config.strategy == CacheStrategy.LFU
        assert config.l1_enabled is False
        assert config.l2_enabled is False
        assert config.warming_enabled is False
        assert config.invalidation_enabled is False

class TestLRUCache:
    """Testes para LRUCache."""
    
    def test_lru_cache_initialization(self):
        """Testa inicialização do cache LRU."""
        cache = LRUCache(max_size=10)
        assert cache.max_size == 10
        assert cache.size() == 0
    
    def test_lru_cache_set_and_get(self):
        """Testa set e get no cache LRU."""
        cache = LRUCache(max_size=5)
        
        # Adiciona entradas
        entry1 = CacheEntry(
            key="key1",
            value="value1",
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=3600,
            level=CacheLevel.L1
        )
        
        entry2 = CacheEntry(
            key="key2",
            value="value2",
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=3600,
            level=CacheLevel.L1
        )
        
        cache.set("key1", entry1)
        cache.set("key2", entry2)
        
        assert cache.size() == 2
        
        # Obtém entradas
        retrieved1 = cache.get("key1")
        retrieved2 = cache.get("key2")
        
        assert retrieved1 == entry1
        assert retrieved2 == entry2
        assert retrieved1.access_count == 1
        assert retrieved2.access_count == 1
    
    def test_lru_cache_eviction(self):
        """Testa evição LRU."""
        cache = LRUCache(max_size=3)
        
        # Adiciona 4 entradas (mais que o máximo)
        for index in range(4):
            entry = CacheEntry(
                key=f"key{index}",
                value=f"value{index}",
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=3600,
                level=CacheLevel.L1
            )
            cache.set(f"key{index}", entry)
        
        # Verifica que apenas 3 entradas permanecem
        assert cache.size() == 3
        
        # A primeira entrada (key0) deve ter sido removida
        assert cache.get("key0") is None
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None
    
    def test_lru_cache_delete(self):
        """Testa remoção de entrada."""
        cache = LRUCache(max_size=5)
        
        entry = CacheEntry(
            key="key1",
            value="value1",
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=3600,
            level=CacheLevel.L1
        )
        
        cache.set("key1", entry)
        assert cache.size() == 1
        
        # Remove entrada
        success = cache.delete("key1")
        assert success is True
        assert cache.size() == 0
        assert cache.get("key1") is None
        
        # Tenta remover entrada inexistente
        success = cache.delete("nonexistent")
        assert success is False
    
    def test_lru_cache_clear(self):
        """Testa limpeza do cache."""
        cache = LRUCache(max_size=5)
        
        # Adiciona algumas entradas
        for index in range(3):
            entry = CacheEntry(
                key=f"key{index}",
                value=f"value{index}",
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=3600,
                level=CacheLevel.L1
            )
            cache.set(f"key{index}", entry)
        
        assert cache.size() == 3
        
        # Limpa cache
        cache.clear()
        assert cache.size() == 0
        assert cache.keys() == []

class TestLFUCache:
    """Testes para LFUCache."""
    
    def test_lfu_cache_initialization(self):
        """Testa inicialização do cache LFU."""
        cache = LFUCache(max_size=10)
        assert cache.max_size == 10
        assert cache.size() == 0
    
    def test_lfu_cache_set_and_get(self):
        """Testa set e get no cache LFU."""
        cache = LFUCache(max_size=5)
        
        entry = CacheEntry(
            key="key1",
            value="value1",
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=3600,
            level=CacheLevel.L1
        )
        
        cache.set("key1", entry)
        assert cache.size() == 1
        
        # Obtém entrada
        retrieved = cache.get("key1")
        assert retrieved == entry
        assert retrieved.access_count == 1
    
    def test_lfu_cache_frequency_tracking(self):
        """Testa rastreamento de frequência."""
        cache = LFUCache(max_size=3)
        
        # Adiciona entradas
        for index in range(3):
            entry = CacheEntry(
                key=f"key{index}",
                value=f"value{index}",
                created_at=time.time(),
                accessed_at=time.time(),
                access_count=0,
                ttl=3600,
                level=CacheLevel.L1
            )
            cache.set(f"key{index}", entry)
        
        # Acessa key0 múltiplas vezes
        for _ in range(5):
            cache.get("key0")
        
        # Acessa key1 algumas vezes
        for _ in range(3):
            cache.get("key1")
        
        # key2 não é acessado
        
        # Adiciona nova entrada (deve evictar key2)
        entry4 = CacheEntry(
            key="key4",
            value="value4",
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=0,
            ttl=3600,
            level=CacheLevel.L1
        )
        cache.set("key4", entry4)
        
        # key2 deve ter sido removido (menor frequência)
        assert cache.get("key2") is None
        assert cache.get("key0") is not None
        assert cache.get("key1") is not None
        assert cache.get("key4") is not None

class TestCacheSerializer:
    """Testes para CacheSerializer."""
    
    def test_json_serializer(self):
        """Testa serialização JSON."""
        serializer = CacheSerializer("json")
        
        data = {"key": "value", "number": 123, "list": [1, 2, 3]}
        
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        
        assert deserialized == data
    
    def test_pickle_serializer(self):
        """Testa serialização Pickle."""
        serializer = CacheSerializer("pickle")
        
        data = {"key": "value", "number": 123, "list": [1, 2, 3]}
        
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        
        assert deserialized == data
    
    def test_serializer_with_complex_objects(self):
        """Testa serialização com objetos complexos."""
        serializer = CacheSerializer("json")
        
        data = {
            "datetime": datetime.now(),
            "timedelta": timedelta(hours=1),
            "set": {1, 2, 3}
        }
        
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        
        # Verifica que foi serializado corretamente
        assert "datetime" in deserialized
        assert "timedelta" in deserialized
        assert "set" in deserialized

class TestCacheCompressor:
    """Testes para CacheCompressor."""
    
    def test_compressor_disabled(self):
        """Testa compressor desabilitado."""
        compressor = CacheCompressor(enabled=False)
        
        data = "test data"
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        assert compressed == data
        assert decompressed == data
    
    def test_compressor_below_threshold(self):
        """Testa compressor com dados abaixo do threshold."""
        compressor = CacheCompressor(enabled=True, threshold=100)
        
        data = "small data"
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        assert compressed == data
        assert decompressed == data
    
    def test_compressor_above_threshold(self):
        """Testa compressor com dados acima do threshold."""
        compressor = CacheCompressor(enabled=True, threshold=10)
        
        # Dados grandes
        data = "value" * 100
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        assert compressed != data  # Deve ter sido comprimido
        assert decompressed == data  # Deve descomprimir corretamente
    
    def test_compressor_error_handling(self):
        """Testa tratamento de erros no compressor."""
        compressor = CacheCompressor(enabled=True, threshold=10)
        
        # Dados que podem causar erro na compressão
        data = "test data"
        
        # Simula erro na compressão
        with patch('gzip.compress', side_effect=Exception("Compression error")):
            compressed = compressor.compress(data)
            assert compressed == data  # Deve retornar dados originais
    
    def test_compressor_decompress_error(self):
        """Testa erro na descompressão."""
        compressor = CacheCompressor(enabled=True, threshold=10)
        
        # Dados não comprimidos
        data = "test data"
        decompressed = compressor.decompress(data)
        
        assert decompressed == data  # Deve retornar dados originais

class TestAdvancedCaching:
    """Testes para AdvancedCaching."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = CacheConfig(
            l1_enabled=True,
            l2_enabled=True,
            l3_enabled=False,
            strategy=CacheStrategy.LRU,
            warming_enabled=False,
            invalidation_enabled=False
        )
        self.cache = AdvancedCaching(self.config)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if hasattr(self, 'cache'):
            self.cache.clear_all()
    
    def test_advanced_caching_initialization(self):
        """Testa inicialização do sistema de cache."""
        assert self.cache.config == self.config
        assert self.cache.l1_cache is not None
        assert self.cache.l2_cache is not None
        assert self.cache.l3_cache is None
        assert self.cache.serializer is not None
        assert self.cache.compressor is not None
        assert self.cache.warming is not None
        assert self.cache.invalidation is not None
        assert self.cache.metrics is not None
    
    def test_cache_set_and_get_l1(self):
        """Testa set e get no nível L1."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Define no L1
        self.cache.set(key, value, level=CacheLevel.L1)
        
        # Obtém do L1
        retrieved = self.cache.get(key, level=CacheLevel.L1)
        
        assert retrieved == value
        assert self.cache.metrics.hits == 1
        assert self.cache.metrics.l1_hits == 1
        assert self.cache.metrics.sets == 1
    
    def test_cache_set_and_get_l2(self):
        """Testa set e get no nível L2."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Define no L2
        self.cache.set(key, value, level=CacheLevel.L2)
        
        # Obtém do L2
        retrieved = self.cache.get(key, level=CacheLevel.L2)
        
        assert retrieved == value
        assert self.cache.metrics.hits == 1
        assert self.cache.metrics.l2_hits == 1
        assert self.cache.metrics.sets == 1
    
    def test_cache_miss(self):
        """Testa cache miss."""
        key = "nonexistent_key"
        
        retrieved = self.cache.get(key, level=CacheLevel.L1)
        
        assert retrieved is None
        assert self.cache.metrics.misses == 1
        assert self.cache.metrics.l1_misses == 1
    
    def test_cache_delete(self):
        """Testa remoção de cache."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Define e depois remove
        self.cache.set(key, value, level=CacheLevel.L1)
        success = self.cache.delete(key, level=CacheLevel.L1)
        
        assert success is True
        assert self.cache.get(key, level=CacheLevel.L1) is None
        assert self.cache.metrics.deletes == 1
    
    def test_cache_ttl_expiration(self):
        """Testa expiração por TTL."""
        key = "test_key"
        value = {"data": "test_value"}
        
        # Define com TTL muito curto
        self.cache.set(key, value, ttl=0.1, level=CacheLevel.L1)
        
        # Aguarda expiração
        time.sleep(0.2)
        
        # Tenta obter (deve retornar None)
        retrieved = self.cache.get(key, level=CacheLevel.L1)
        assert retrieved is None
    
    def test_cache_clear(self):
        """Testa limpeza de cache."""
        # Adiciona algumas entradas
        for index in range(3):
            self.cache.set(f"key{index}", f"value{index}", level=CacheLevel.L1)
        
        # Limpa L1
        self.cache.clear(CacheLevel.L1)
        
        # Verifica que foram removidas
        for index in range(3):
            assert self.cache.get(f"key{index}", level=CacheLevel.L1) is None
    
    def test_cache_clear_all(self):
        """Testa limpeza de todos os caches."""
        # Adiciona entradas em diferentes níveis
        self.cache.set("key1", "value1", level=CacheLevel.L1)
        self.cache.set("key2", "value2", level=CacheLevel.L2)
        
        # Limpa todos
        self.cache.clear_all()
        
        # Verifica que foram removidas
        assert self.cache.get("key1", level=CacheLevel.L1) is None
        assert self.cache.get("key2", level=CacheLevel.L2) is None
    
    def test_cache_get_keys(self):
        """Testa obtenção de chaves."""
        # Adiciona algumas entradas
        self.cache.set("key1", "value1", level=CacheLevel.L1)
        self.cache.set("key2", "value2", level=CacheLevel.L1)
        
        keys = self.cache.get_keys(CacheLevel.L1)
        
        assert "key1" in keys
        assert "key2" in keys
        assert len(keys) == 2
    
    def test_cache_metrics(self):
        """Testa métricas do cache."""
        # Faz algumas operações
        self.cache.set("key1", "value1", level=CacheLevel.L1)
        self.cache.get("key1", level=CacheLevel.L1)
        self.cache.get("nonexistent", level=CacheLevel.L1)
        self.cache.delete("key1", level=CacheLevel.L1)
        
        metrics = self.cache.get_metrics()
        
        assert metrics.hits == 1
        assert metrics.misses == 1
        assert metrics.sets == 1
        assert metrics.deletes == 1
        assert metrics.total_operations == 4
        assert metrics.hit_rate == 0.5
        assert metrics.miss_rate == 0.5
    
    def test_cache_health_check(self):
        """Testa health check do cache."""
        health = self.cache.health_check()
        
        assert "status" in health
        assert "l1_cache" in health
        assert "l2_cache" in health
        assert "warming" in health
        assert "invalidation" in health
        assert "metrics" in health
        assert health["status"] == "healthy"

class TestCacheWarming:
    """Testes para CacheWarming."""
    
    def test_cache_warming_initialization(self):
        """Testa inicialização do cache warming."""
        config = CacheConfig(warming_enabled=True)
        cache = AdvancedCaching(config)
        
        warming = cache.warming
        
        assert warming.config == config
        assert warming.cache_manager == cache
        assert len(warming.warming_queue) == 0
    
    def test_add_to_warming_queue(self):
        """Testa adição à fila de warming."""
        config = CacheConfig(warming_enabled=True)
        cache = AdvancedCaching(config)
        
        warming = cache.warming
        
        # Adiciona à fila
        warming.add_to_warming_queue("key1", "value1", ttl=3600)
        
        assert len(warming.warming_queue) == 1
        
        item = warming.warming_queue[0]
        assert item["key"] == "key1"
        assert item["value"] == "value1"
        assert item["ttl"] == 3600
    
    def test_warming_disabled(self):
        """Testa warming desabilitado."""
        config = CacheConfig(warming_enabled=False)
        cache = AdvancedCaching(config)
        
        warming = cache.warming
        
        # Tenta adicionar à fila
        warming.add_to_warming_queue("key1", "value1")
        
        assert len(warming.warming_queue) == 0

class TestCacheInvalidation:
    """Testes para CacheInvalidation."""
    
    def test_cache_invalidation_initialization(self):
        """Testa inicialização da invalidação de cache."""
        config = CacheConfig(invalidation_enabled=True)
        cache = AdvancedCaching(config)
        
        invalidation = cache.invalidation
        
        assert invalidation.config == config
        assert invalidation.cache_manager == cache
        assert len(invalidation.invalidation_patterns) == 0
    
    def test_add_invalidation_pattern(self):
        """Testa adição de padrão de invalidação."""
        config = CacheConfig(invalidation_enabled=True)
        cache = AdvancedCaching(config)
        
        invalidation = cache.invalidation
        
        # Adiciona padrão
        keys = ["key1", "key2", "key3"]
        invalidation.add_invalidation_pattern("pattern1", keys)
        
        assert "pattern1" in invalidation.invalidation_patterns
        assert invalidation.invalidation_patterns["pattern1"] == keys
    
    def test_invalidate_by_pattern(self):
        """Testa invalidação por padrão."""
        config = CacheConfig(invalidation_enabled=True)
        cache = AdvancedCaching(config)
        
        invalidation = cache.invalidation
        
        # Adiciona padrão e chaves
        keys = ["key1", "key2"]
        invalidation.add_invalidation_pattern("pattern1", keys)
        
        # Adiciona dados ao cache
        cache.set("key1", "value1", level=CacheLevel.L1)
        cache.set("key2", "value2", level=CacheLevel.L1)
        
        # Invalida por padrão
        invalidation.invalidate_by_pattern("pattern1")
        
        # Verifica que foram removidos
        assert cache.get("key1", level=CacheLevel.L1) is None
        assert cache.get("key2", level=CacheLevel.L1) is None
    
    def test_invalidate_by_keys(self):
        """Testa invalidação por chaves específicas."""
        config = CacheConfig(invalidation_enabled=True)
        cache = AdvancedCaching(config)
        
        invalidation = cache.invalidation
        
        # Adiciona dados ao cache
        cache.set("key1", "value1", level=CacheLevel.L1)
        cache.set("key2", "value2", level=CacheLevel.L1)
        cache.set("key3", "value3", level=CacheLevel.L1)
        
        # Invalida chaves específicas
        invalidation.invalidate_by_keys(["key1", "key2"])
        
        # Verifica que foram removidos
        assert cache.get("key1", level=CacheLevel.L1) is None
        assert cache.get("key2", level=CacheLevel.L1) is None
        assert cache.get("key3", level=CacheLevel.L1) is not None

class TestCacheDecorator:
    """Testes para decorator de cache."""
    
    def test_cached_decorator(self):
        """Testa decorator cached."""
        cache = AdvancedCaching(CacheConfig())
        
        # Função de teste
        call_count = 0
        
        @cached(ttl=3600)
        def test_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"
        
        # Primeira chamada
        result1 = test_function("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Segunda chamada (deve usar cache)
        result2 = test_function("test")
        assert result2 == "result_test"
        assert call_count == 1  # Não deve ter sido chamada novamente
    
    def test_cached_decorator_with_key_func(self):
        """Testa decorator cached com função de chave customizada."""
        cache = AdvancedCaching(CacheConfig())
        
        call_count = 0
        
        def custom_key_func(*args, **kwargs):
            return f"custom_key_{args[0]}"
        
        @cached(ttl=3600, key_func=custom_key_func)
        def test_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"
        
        # Primeira chamada
        result1 = test_function("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Segunda chamada (deve usar cache)
        result2 = test_function("test")
        assert result2 == "result_test"
        assert call_count == 1

class TestCacheFactory:
    """Testes para factory de cache."""
    
    def test_create_advanced_caching(self):
        """Testa criação de cache avançado."""
        config = CacheConfig()
        cache = create_advanced_caching(config)
        
        assert isinstance(cache, AdvancedCaching)
        assert cache.config == config
    
    def test_get_global_cache(self):
        """Testa obtenção do cache global."""
        # Limpa cache global
        set_global_cache(None)
        
        cache = get_global_cache()
        
        assert isinstance(cache, AdvancedCaching)
        assert cache is get_global_cache()  # Mesma instância
    
    def test_set_global_cache(self):
        """Testa definição do cache global."""
        config = CacheConfig()
        custom_cache = AdvancedCaching(config)
        
        set_global_cache(custom_cache)
        
        assert get_global_cache() is custom_cache

class TestEdgeCases:
    """Testes para casos extremos."""
    
    def test_cache_with_disabled_levels(self):
        """Testa cache com níveis desabilitados."""
        config = CacheConfig(
            l1_enabled=False,
            l2_enabled=False,
            l3_enabled=False
        )
        cache = AdvancedCaching(config)
        
        # Tenta operações
        cache.set("key1", "value1", level=CacheLevel.L1)
        result = cache.get("key1", level=CacheLevel.L1)
        
        # Deve funcionar sem erro, mas não armazenar nada
        assert result is None
    
    def test_cache_with_very_large_data(self):
        """Testa cache com dados muito grandes."""
        config = CacheConfig()
        cache = AdvancedCaching(config)
        
        # Dados grandes
        large_data = "value" * 10000
        
        cache.set("large_key", large_data, level=CacheLevel.L1)
        result = cache.get("large_key", level=CacheLevel.L1)
        
        assert result == large_data
    
    def test_cache_with_complex_objects(self):
        """Testa cache com objetos complexos."""
        config = CacheConfig()
        cache = AdvancedCaching(config)
        
        complex_data = {
            "list": [1, 2, 3, 4, 5],
            "dict": {"nested": {"value": "test"}},
            "tuple": (1, 2, 3),
            "set": {1, 2, 3},
            "datetime": datetime.now()
        }
        
        cache.set("complex_key", complex_data, level=CacheLevel.L1)
        result = cache.get("complex_key", level=CacheLevel.L1)
        
        assert result == complex_data

def run_all_tests():
    """Executa todos os testes."""
    test_classes = [
        TestCacheConfig,
        TestLRUCache,
        TestLFUCache,
        TestCacheSerializer,
        TestCacheCompressor,
        TestAdvancedCaching,
        TestCacheWarming,
        TestCacheInvalidation,
        TestCacheDecorator,
        TestCacheFactory,
        TestEdgeCases
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        test_instance = test_class()
        
        # Executa todos os métodos que começam com 'test_'
        for method_name in dir(test_instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    # Setup se existir
                    if hasattr(test_instance, 'setup_method'):
                        test_instance.setup_method()
                    
                    # Executa o teste
                    getattr(test_instance, method_name)()
                    passed_tests += 1
                    print(f"✅ {test_class.__name__}.{method_name} - PASSED")
                except Exception as e:
                    print(f"❌ {test_class.__name__}.{method_name} - FAILED: {str(e)}")
                finally:
                    # Teardown se existir
                    if hasattr(test_instance, 'teardown_method'):
                        test_instance.teardown_method()
    
    print(f"\n📊 RESULTADO DOS TESTES:")
    print(f"Total de testes: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Testes falharam: {total_tests - passed_tests}")
    print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 