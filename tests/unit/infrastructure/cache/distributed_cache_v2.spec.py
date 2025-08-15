"""
Testes Unitários - Sistema de Cache Distribuído Redis

Tracing ID: IMP001_CACHE_TESTS_001
Data: 2025-01-27
Versão: 1.0
Status: Em Implementação

Testa todas as funcionalidades do sistema de cache distribuído:
- Cache L1 (Memory)
- Cache L2 (Redis)
- Cache warming
- Métricas
- Decorators
"""

import pytest
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Importa módulos do sistema de cache
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'infrastructure'))

from cache.distributed_cache import (
    DistributedCache,
    L1MemoryCache,
    L2RedisCache,
    CacheConfig,
    CacheLevel,
    CacheMetrics,
    CacheKeyGenerator,
    CacheWarming,
    cache_decorator,
    get_cache,
    init_cache
)


class TestCacheConfig:
    """Testes para configuração do cache"""
    
    def test_cache_config_defaults(self):
        """Testa valores padrão da configuração"""
        config = CacheConfig()
        
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_db == 0
        assert config.redis_password is None
        assert config.default_ttl == 3600
        assert config.max_memory_size == 100 * 1024 * 1024
        assert config.enable_cache_warming is True
        assert config.cache_warming_threshold == 10
        assert config.enable_metrics is True
        assert config.fallback_to_db is True
    
    def test_cache_config_custom(self):
        """Testa configuração customizada"""
        config = CacheConfig(
            redis_host="redis.example.com",
            redis_port=6380,
            redis_db=1,
            redis_password="secret",
            default_ttl=7200,
            max_memory_size=200 * 1024 * 1024,
            enable_cache_warming=False,
            cache_warming_threshold=5,
            enable_metrics=False,
            fallback_to_db=False
        )
        
        assert config.redis_host == "redis.example.com"
        assert config.redis_port == 6380
        assert config.redis_db == 1
        assert config.redis_password == "secret"
        assert config.default_ttl == 7200
        assert config.max_memory_size == 200 * 1024 * 1024
        assert config.enable_cache_warming is False
        assert config.cache_warming_threshold == 5
        assert config.enable_metrics is False
        assert config.fallback_to_db is False


class TestCacheKeyGenerator:
    """Testes para geração de chaves de cache"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.key_generator = CacheKeyGenerator()
    
    def test_generate_key_simple(self):
        """Testa geração de chave simples"""
        key = self.key_generator.generate_key("test", "value1", "value2")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length
    
    def test_generate_key_with_kwargs(self):
        """Testa geração de chave com kwargs"""
        key = self.key_generator.generate_key("test", param1="value1", param2="value2")
        assert isinstance(key, str)
        assert len(key) == 32
    
    def test_generate_key_with_dict(self):
        """Testa geração de chave com dicionário"""
        data = {"key1": "value1", "key2": "value2"}
        key = self.key_generator.generate_key("test", data)
        assert isinstance(key, str)
        assert len(key) == 32
    
    def test_generate_key_consistent(self):
        """Testa que chaves iguais geram o mesmo hash"""
        key1 = self.key_generator.generate_key("test", "value1", "value2")
        key2 = self.key_generator.generate_key("test", "value1", "value2")
        assert key1 == key2
    
    def test_generate_key_different(self):
        """Testa que chaves diferentes geram hashes diferentes"""
        key1 = self.key_generator.generate_key("test", "value1")
        key2 = self.key_generator.generate_key("test", "value2")
        assert key1 != key2


class TestL1MemoryCache:
    """Testes para cache L1 (Memory)"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.cache = L1MemoryCache(max_size=1024)
    
    def test_set_and_get(self):
        """Testa set e get básico"""
        self.cache.set("test_key", "test_value", 3600)
        value = self.cache.get("test_key")
        assert value == "test_value"
    
    def test_get_nonexistent(self):
        """Testa get de chave inexistente"""
        value = self.cache.get("nonexistent_key")
        assert value is None
    
    def test_expiration(self):
        """Testa expiração de itens"""
        self.cache.set("test_key", "test_value", 1)  # 1 segundo
        time.sleep(1.1)  # Espera expirar
        value = self.cache.get("test_key")
        assert value is None
    
    def test_delete(self):
        """Testa remoção de item"""
        self.cache.set("test_key", "test_value", 3600)
        self.cache.delete("test_key")
        value = self.cache.get("test_key")
        assert value is None
    
    def test_clear(self):
        """Testa limpeza do cache"""
        self.cache.set("key1", "value1", 3600)
        self.cache.set("key2", "value2", 3600)
        self.cache.clear()
        
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
    
    def test_memory_eviction(self):
        """Testa evicção por memória"""
        # Cria cache pequeno
        small_cache = L1MemoryCache(max_size=100)
        
        # Adiciona itens até exceder o limite
        for index in range(10):
            small_cache.set(f"key{index}", "value" * 50, 3600)
        
        # Verifica que alguns itens foram removidos
        stats = small_cache.get_stats()
        assert stats['size'] <= 100
    
    def test_get_stats(self):
        """Testa obtenção de estatísticas"""
        self.cache.set("key1", "value1", 3600)
        self.cache.set("key2", "value2", 3600)
        
        stats = self.cache.get_stats()
        assert 'size' in stats
        assert 'max_size' in stats
        assert 'items_count' in stats
        assert 'hit_ratio' in stats
        assert stats['items_count'] == 2


class TestL2RedisCache:
    """Testes para cache L2 (Redis)"""
    
    @patch('cache.distributed_cache.redis')
    def setup_method(self, mock_redis):
        """Setup para cada teste"""
        self.mock_redis_client = Mock()
        mock_redis.Redis.return_value = self.mock_redis_client
        self.config = CacheConfig(redis_host="localhost", redis_port=6379)
        self.cache = L2RedisCache(self.config)
    
    def test_set_and_get(self):
        """Testa set e get básico"""
        # Mock do Redis
        self.mock_redis_client.get.return_value = json.dumps("test_value")
        
        # Testa set
        self.cache.set("test_key", "test_value", 3600)
        self.mock_redis_client.setex.assert_called_once_with("test_key", 3600, json.dumps("test_value"))
        
        # Testa get
        value = self.cache.get("test_key")
        assert value == "test_value"
        self.mock_redis_client.get.assert_called_once_with("test_key")
    
    def test_get_nonexistent(self):
        """Testa get de chave inexistente"""
        self.mock_redis_client.get.return_value = None
        
        value = self.cache.get("nonexistent_key")
        assert value is None
    
    def test_get_with_error(self):
        """Testa get com erro do Redis"""
        self.mock_redis_client.get.side_effect = Exception("Redis error")
        
        value = self.cache.get("test_key")
        assert value is None
    
    def test_delete(self):
        """Testa remoção de item"""
        self.cache.delete("test_key")
        self.mock_redis_client.delete.assert_called_once_with("test_key")
    
    def test_clear(self):
        """Testa limpeza do cache"""
        self.cache.clear()
        self.mock_redis_client.flushdb.assert_called_once()
    
    def test_get_stats(self):
        """Testa obtenção de estatísticas"""
        self.mock_redis_client.info.return_value = {
            'used_memory': 1024,
            'used_memory_peak': 2048,
            'keyspace_hits': 100,
            'keyspace_misses': 10,
            'total_commands_processed': 1000
        }
        
        stats = self.cache.get_stats()
        assert stats['connected'] is True
        assert stats['used_memory'] == 1024
        assert stats['keyspace_hits'] == 100


class TestCacheMetrics:
    """Testes para métricas do cache"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.metrics = CacheMetrics()
    
    def test_record_hit(self):
        """Testa registro de hit"""
        with patch('cache.distributed_cache.logging') as mock_logging:
            self.metrics.record_hit(CacheLevel.L1_MEMORY)
            mock_logging.info.assert_called_once_with("Cache HIT - Level: l1_memory")
    
    def test_record_miss(self):
        """Testa registro de miss"""
        with patch('cache.distributed_cache.logging') as mock_logging:
            self.metrics.record_miss(CacheLevel.L2_REDIS)
            mock_logging.info.assert_called_once_with("Cache MISS - Level: l2_redis")
    
    def test_record_operation(self):
        """Testa registro de operação"""
        with patch('cache.distributed_cache.logging') as mock_logging:
            self.metrics.record_operation("get", 0.1)
            mock_logging.debug.assert_called_once_with("Cache operation: get took 0.1000s")


class TestCacheWarming:
    """Testes para cache warming"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = CacheConfig(enable_cache_warming=True, cache_warming_threshold=3)
        self.warming = CacheWarming(self.config)
    
    def test_record_access(self):
        """Testa registro de acesso"""
        self.warming.record_access("test_key")
        assert self.warming.access_patterns["test_key"] == 1
    
    def test_cache_warming_trigger(self):
        """Testa trigger do cache warming"""
        # Registra acessos até o threshold
        for index in range(3):
            self.warming.record_access("test_key")
        
        # Verifica se warming foi executado
        assert "test_key" in self.warming.warmed_keys
    
    def test_cache_warming_disabled(self):
        """Testa cache warming desabilitado"""
        config = CacheConfig(enable_cache_warming=False)
        warming = CacheWarming(config)
        
        # Registra acessos
        for index in range(10):
            warming.record_access("test_key")
        
        # Verifica que warming não foi executado
        assert "test_key" not in warming.warmed_keys


class TestDistributedCache:
    """Testes para cache distribuído principal"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = CacheConfig()
        self.cache = DistributedCache(self.config)
    
    def test_get_from_l1(self):
        """Testa get do cache L1"""
        # Popula L1 diretamente
        self.cache.l1_cache.set("test_key", "test_value", 3600)
        
        # Testa get
        value = self.cache.get("test_key")
        assert value == "test_value"
    
    def test_get_from_l2(self):
        """Testa get do cache L2"""
        # Popula L2 diretamente
        self.cache.l2_cache.set("test_key", "test_value", 3600)
        
        # Testa get
        value = self.cache.get("test_key")
        assert value == "test_value"
        
        # Verifica que L1 foi populada
        l1_value = self.cache.l1_cache.get("test_key")
        assert l1_value == "test_value"
    
    def test_get_miss(self):
        """Testa cache miss"""
        value = self.cache.get("nonexistent_key")
        assert value is None
    
    def test_set(self):
        """Testa set em ambos os níveis"""
        self.cache.set("test_key", "test_value", 3600)
        
        # Verifica L1
        l1_value = self.cache.l1_cache.get("test_key")
        assert l1_value == "test_value"
        
        # Verifica L2
        l2_value = self.cache.l2_cache.get("test_key")
        assert l2_value == "test_value"
    
    def test_delete(self):
        """Testa delete em ambos os níveis"""
        # Popula cache
        self.cache.set("test_key", "test_value", 3600)
        
        # Deleta
        self.cache.delete("test_key")
        
        # Verifica que foi removido de ambos
        assert self.cache.l1_cache.get("test_key") is None
        assert self.cache.l2_cache.get("test_key") is None
    
    def test_clear(self):
        """Testa limpeza completa"""
        # Popula cache
        self.cache.set("key1", "value1", 3600)
        self.cache.set("key2", "value2", 3600)
        
        # Limpa
        self.cache.clear()
        
        # Verifica que foi limpo
        assert self.cache.l1_cache.get("key1") is None
        assert self.cache.l1_cache.get("key2") is None
    
    def test_get_stats(self):
        """Testa obtenção de estatísticas"""
        stats = self.cache.get_stats()
        assert 'l1_cache' in stats
        assert 'l2_cache' in stats
        assert 'config' in stats


class TestCacheDecorator:
    """Testes para decorator de cache"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.cache = DistributedCache()
    
    def test_cache_decorator(self):
        """Testa decorator de cache"""
        call_count = 0
        
        @cache_decorator("test_func", 3600)
        def test_function(param1, param2):
            nonlocal call_count
            call_count += 1
            return f"result_{param1}_{param2}"
        
        # Primeira chamada - executa função
        result1 = test_function("a", "b")
        assert result1 == "result_a_b"
        assert call_count == 1
        
        # Segunda chamada - usa cache
        result2 = test_function("a", "b")
        assert result2 == "result_a_b"
        assert call_count == 1  # Não incrementou
    
    def test_cache_decorator_different_params(self):
        """Testa decorator com parâmetros diferentes"""
        call_count = 0
        
        @cache_decorator("test_func", 3600)
        def test_function(param1, param2):
            nonlocal call_count
            call_count += 1
            return f"result_{param1}_{param2}"
        
        # Chamadas com parâmetros diferentes
        test_function("a", "b")
        test_function("a", "c")
        
        assert call_count == 2  # Ambas executaram


class TestCacheGlobal:
    """Testes para instância global do cache"""
    
    def test_get_cache(self):
        """Testa obtenção da instância global"""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2
    
    def test_init_cache(self):
        """Testa inicialização do cache"""
        config = CacheConfig(redis_host="test")
        cache = init_cache(config)
        assert cache.config.redis_host == "test"


class TestCacheIntegration:
    """Testes de integração do cache"""
    
    def test_full_cache_flow(self):
        """Testa fluxo completo do cache"""
        cache = DistributedCache()
        
        # Simula dados do database
        def fetch_from_db(key):
            return {"data": f"value_for_{key}", "timestamp": time.time()}
        
        # Primeira busca - cache miss
        with patch('cache.distributed_cache.logging') as mock_logging:
            result1 = cache.get("user_123")
            assert result1 is None
        
        # Simula busca do database e cacheia
        db_data = fetch_from_db("user_123")
        cache.set("user_123", db_data, 3600)
        
        # Segunda busca - cache hit
        result2 = cache.get("user_123")
        assert result2 == db_data
    
    def test_cache_warming_integration(self):
        """Testa integração do cache warming"""
        config = CacheConfig(enable_cache_warming=True, cache_warming_threshold=2)
        cache = DistributedCache(config)
        
        # Simula múltiplos acessos
        for index in range(3):
            cache.get("frequently_accessed_key")
        
        # Verifica que warming foi executado
        assert "frequently_accessed_key" in cache.cache_warming.warmed_keys


class TestCachePerformance:
    """Testes de performance do cache"""
    
    def test_cache_performance_improvement(self):
        """Testa melhoria de performance com cache"""
        cache = DistributedCache()
        
        # Simula função custosa
        def expensive_function(param):
            time.sleep(0.1)  # Simula processamento
            return f"expensive_result_{param}"
        
        # Primeira execução - sem cache
        start_time = time.time()
        result1 = expensive_function("test")
        time_without_cache = time.time() - start_time
        
        # Cacheia resultado
        cache.set("expensive_function_test", result1, 3600)
        
        # Segunda execução - com cache
        start_time = time.time()
        result2 = cache.get("expensive_function_test")
        time_with_cache = time.time() - start_time
        
        # Verifica que cache é mais rápido
        assert time_with_cache < time_without_cache
        assert result1 == result2
    
    def test_memory_usage(self):
        """Testa uso de memória do cache"""
        cache = DistributedCache()
        
        # Adiciona muitos itens
        for index in range(1000):
            cache.set(f"key_{index}", f"value_{index}" * 100, 3600)
        
        # Verifica que não excedeu o limite
        stats = cache.get_stats()
        assert stats['l1_cache']['size'] <= cache.config.max_memory_size


class TestCacheErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_redis_connection_error(self):
        """Testa erro de conexão com Redis"""
        config = CacheConfig(redis_host="invalid_host")
        cache = DistributedCache(config)
        
        # Deve funcionar apenas com L1
        cache.set("test_key", "test_value", 3600)
        value = cache.get("test_key")
        assert value == "test_value"
    
    def test_invalid_data_serialization(self):
        """Testa serialização de dados inválidos"""
        cache = DistributedCache()
        
        # Tenta cachear objeto não serializável
        class NonSerializable:
            pass
        
        # Deve não falhar
        cache.set("test_key", NonSerializable(), 3600)
        # L1 deve funcionar, L2 pode falhar silenciosamente


# Fixtures para pytest
@pytest.fixture
def cache_config():
    """Fixture para configuração de cache"""
    return CacheConfig(
        redis_host="localhost",
        redis_port=6379,
        default_ttl=3600,
        enable_cache_warming=True
    )


@pytest.fixture
def distributed_cache(cache_config):
    """Fixture para cache distribuído"""
    return DistributedCache(cache_config)


@pytest.fixture
def l1_cache():
    """Fixture para cache L1"""
    return L1MemoryCache(max_size=1024)


@pytest.fixture
def cache_metrics():
    """Fixture para métricas de cache"""
    return CacheMetrics()


# Testes parametrizados
@pytest.mark.parametrize("key,value,ttl", [
    ("string_key", "string_value", 3600),
    ("int_key", 123, 1800),
    ("list_key", [1, 2, 3], 7200),
    ("dict_key", {"a": 1, "b": 2}, 3600),
])
def test_cache_different_data_types(distributed_cache, key, value, ttl):
    """Testa cache com diferentes tipos de dados"""
    distributed_cache.set(key, value, ttl)
    retrieved_value = distributed_cache.get(key)
    assert retrieved_value == value


@pytest.mark.parametrize("cache_level", [
    CacheLevel.L1_MEMORY,
    CacheLevel.L2_REDIS,
])
def test_cache_levels(cache_metrics, cache_level):
    """Testa diferentes níveis de cache"""
    with patch('cache.distributed_cache.logging') as mock_logging:
        cache_metrics.record_hit(cache_level)
        mock_logging.info.assert_called_once_with(f"Cache HIT - Level: {cache_level.value}")


if __name__ == "__main__":
    # Executa testes
    pytest.main([__file__, "-value"]) 