"""
🧪 Testes Unitários - Estratégia de Cache
========================================

Tracing ID: TEST_CACHING_STRATEGY_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTAÇÃO

Testes para o módulo backend/app/optimization/caching_strategy.py
Baseado exclusivamente no código real do Omni Keywords Finder
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, Optional

# Importações do código real
from backend.app.optimization.caching_strategy import (
    CacheStrategy,
    CacheLevel,
    CacheConfig,
    CacheMetrics,
    CacheManager,
    MultiLevelCache,
    CacheDecorator,
    CacheInvalidator,
    CacheAnalytics,
    create_cache_manager,
    create_multi_level_cache,
    get_cache_manager,
    get_multi_level_cache,
    cached
)


class TestCacheStrategy:
    """Testes para enum CacheStrategy"""
    
    def test_cache_strategy_values(self):
        """Testa valores do enum CacheStrategy"""
        assert CacheStrategy.LRU.value == "lru"
        assert CacheStrategy.TTL.value == "ttl"
        assert CacheStrategy.LFU.value == "lfu"
        assert CacheStrategy.FIFO.value == "fifo"
    
    def test_cache_strategy_membership(self):
        """Testa pertencimento ao enum"""
        assert "lru" in [strategy.value for strategy in CacheStrategy]
        assert "ttl" in [strategy.value for strategy in CacheStrategy]
        assert "lfu" in [strategy.value for strategy in CacheStrategy]
        assert "fifo" in [strategy.value for strategy in CacheStrategy]


class TestCacheLevel:
    """Testes para enum CacheLevel"""
    
    def test_cache_level_values(self):
        """Testa valores do enum CacheLevel"""
        assert CacheLevel.MEMORY.value == "memory"
        assert CacheLevel.REDIS.value == "redis"
        assert CacheLevel.DISK.value == "disk"
    
    def test_cache_level_membership(self):
        """Testa pertencimento ao enum"""
        assert "memory" in [level.value for level in CacheLevel]
        assert "redis" in [level.value for level in CacheLevel]
        assert "disk" in [level.value for level in CacheLevel]


class TestCacheConfig:
    """Testes para dataclass CacheConfig"""
    
    def test_cache_config_default_values(self):
        """Testa valores padrão do CacheConfig"""
        config = CacheConfig(strategy=CacheStrategy.TTL)
        
        assert config.strategy == CacheStrategy.TTL
        assert config.ttl == 3600
        assert config.max_size == 1000
        assert config.compression is False
        assert config.serialize is True
        assert config.key_prefix == "cache"
        assert config.namespace == "default"
    
    def test_cache_config_custom_values(self):
        """Testa valores customizados do CacheConfig"""
        config = CacheConfig(
            strategy=CacheStrategy.LRU,
            ttl=1800,
            max_size=500,
            compression=True,
            serialize=False,
            key_prefix="custom",
            namespace="test"
        )
        
        assert config.strategy == CacheStrategy.LRU
        assert config.ttl == 1800
        assert config.max_size == 500
        assert config.compression is True
        assert config.serialize is False
        assert config.key_prefix == "custom"
        assert config.namespace == "test"
    
    def test_cache_config_asdict(self):
        """Testa conversão para dicionário"""
        config = CacheConfig(strategy=CacheStrategy.TTL)
        config_dict = asdict(config)
        
        assert config_dict["strategy"] == CacheStrategy.TTL
        assert config_dict["ttl"] == 3600
        assert config_dict["max_size"] == 1000


class TestCacheMetrics:
    """Testes para dataclass CacheMetrics"""
    
    def test_cache_metrics_default_values(self):
        """Testa valores padrão do CacheMetrics"""
        metrics = CacheMetrics()
        
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.sets == 0
        assert metrics.deletes == 0
        assert metrics.errors == 0
        assert metrics.total_requests == 0
        assert metrics.hit_rate == 0.0
        assert metrics.avg_response_time == 0.0
    
    def test_cache_metrics_custom_values(self):
        """Testa valores customizados do CacheMetrics"""
        metrics = CacheMetrics(
            hits=100,
            misses=50,
            sets=150,
            deletes=10,
            errors=2,
            total_requests=150,
            hit_rate=0.67,
            avg_response_time=0.05
        )
        
        assert metrics.hits == 100
        assert metrics.misses == 50
        assert metrics.sets == 150
        assert metrics.deletes == 10
        assert metrics.errors == 2
        assert metrics.total_requests == 150
        assert metrics.hit_rate == 0.67
        assert metrics.avg_response_time == 0.05


class TestCacheManager:
    """Testes para classe CacheManager"""
    
    @pytest.fixture
    def cache_manager(self):
        """Fixture para CacheManager"""
        config = CacheConfig(strategy=CacheStrategy.TTL)
        return CacheManager(config)
    
    @pytest.fixture
    def lru_cache_manager(self):
        """Fixture para CacheManager com estratégia LRU"""
        config = CacheConfig(strategy=CacheStrategy.LRU)
        return CacheManager(config)
    
    def test_cache_manager_initialization(self, cache_manager):
        """Testa inicialização do CacheManager"""
        assert cache_manager.config.strategy == CacheStrategy.TTL
        assert cache_manager.memory_cache is not None
        assert cache_manager.redis_client is None
        assert isinstance(cache_manager.metrics, CacheMetrics)
    
    def test_cache_manager_lru_initialization(self, lru_cache_manager):
        """Testa inicialização do CacheManager com LRU"""
        assert lru_cache_manager.config.strategy == CacheStrategy.LRU
        assert lru_cache_manager.memory_cache is not None
    
    def test_cache_manager_default_config(self):
        """Testa CacheManager com configuração padrão"""
        manager = CacheManager()
        assert manager.config.strategy == CacheStrategy.TTL
        assert manager.config.ttl == 3600
    
    def test_generate_key(self, cache_manager):
        """Testa geração de chaves de cache"""
        key = cache_manager._generate_key("test_key")
        assert key == "cache:default:test_key"
        
        # Testa com namespace customizado
        cache_manager.config.namespace = "custom"
        key = cache_manager._generate_key("test_key")
        assert key == "cache:custom:test_key"
    
    def test_serialize_value(self, cache_manager):
        """Testa serialização de valores"""
        test_data = {"key": "value", "number": 123}
        serialized = cache_manager._serialize_value(test_data)
        
        assert isinstance(serialized, bytes)
        # Verifica se pode ser deserializado
        deserialized = cache_manager._deserialize_value(serialized)
        assert deserialized == test_data
    
    def test_serialize_value_with_compression(self):
        """Testa serialização com compressão"""
        config = CacheConfig(strategy=CacheStrategy.TTL, compression=True)
        manager = CacheManager(config)
        
        test_data = {"key": "value", "number": 123}
        serialized = manager._serialize_value(test_data)
        
        assert isinstance(serialized, bytes)
        deserialized = manager._deserialize_value(serialized)
        assert deserialized == test_data
    
    @pytest.mark.asyncio
    async def test_get_memory_cache(self, cache_manager):
        """Testa obtenção de valor do cache em memória"""
        # Simula cache em memória
        cache_manager.memory_cache["test_key"] = "test_value"
        
        result = await cache_manager.get("test_key", CacheLevel.MEMORY)
        assert result == "test_value"
    
    @pytest.mark.asyncio
    async def test_get_memory_cache_miss(self, cache_manager):
        """Testa miss no cache em memória"""
        result = await cache_manager.get("nonexistent_key", CacheLevel.MEMORY)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_memory_cache(self, cache_manager):
        """Testa definição de valor no cache em memória"""
        success = await cache_manager.set("test_key", "test_value", level=CacheLevel.MEMORY)
        assert success is True
        
        # Verifica se foi armazenado
        result = await cache_manager.get("test_key", CacheLevel.MEMORY)
        assert result == "test_value"
    
    @pytest.mark.asyncio
    async def test_delete_memory_cache(self, cache_manager):
        """Testa remoção de valor do cache em memória"""
        # Primeiro adiciona um valor
        await cache_manager.set("test_key", "test_value", level=CacheLevel.MEMORY)
        
        # Remove o valor
        success = await cache_manager.delete("test_key", level=CacheLevel.MEMORY)
        assert success is True
        
        # Verifica se foi removido
        result = await cache_manager.get("test_key", CacheLevel.MEMORY)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_clear_memory_cache(self, cache_manager):
        """Testa limpeza do cache em memória"""
        # Adiciona alguns valores
        await cache_manager.set("key1", "value1", level=CacheLevel.MEMORY)
        await cache_manager.set("key2", "value2", level=CacheLevel.MEMORY)
        
        # Limpa o cache
        success = await cache_manager.clear(level=CacheLevel.MEMORY)
        assert success is True
        
        # Verifica se foram removidos
        assert await cache_manager.get("key1", CacheLevel.MEMORY) is None
        assert await cache_manager.get("key2", CacheLevel.MEMORY) is None
    
    @pytest.mark.asyncio
    async def test_redis_operations_with_mock(self, cache_manager):
        """Testa operações Redis com mock"""
        # Mock do cliente Redis
        mock_redis = AsyncMock()
        cache_manager.redis_client = mock_redis
        
        # Testa get
        mock_redis.get.return_value = b'{"key": "value"}'
        result = await cache_manager.get("test_key", CacheLevel.REDIS)
        assert result == {"key": "value"}
        
        # Testa set
        mock_redis.set.return_value = True
        success = await cache_manager.set("test_key", {"key": "value"}, level=CacheLevel.REDIS)
        assert success is True
        
        # Testa delete
        mock_redis.delete.return_value = 1
        success = await cache_manager.delete("test_key", level=CacheLevel.REDIS)
        assert success is True
    
    def test_update_metrics(self, cache_manager):
        """Testa atualização de métricas"""
        start_time = time.time()
        time.sleep(0.01)  # Simula operação
        
        cache_manager._update_metrics(start_time)
        
        assert cache_manager.metrics.total_requests > 0
        assert cache_manager.metrics.avg_response_time > 0
    
    def test_get_metrics(self, cache_manager):
        """Testa obtenção de métricas"""
        metrics = cache_manager.get_metrics()
        
        assert "hits" in metrics
        assert "misses" in metrics
        assert "sets" in metrics
        assert "deletes" in metrics
        assert "errors" in metrics
        assert "total_requests" in metrics
        assert "hit_rate" in metrics
        assert "avg_response_time" in metrics
    
    @pytest.mark.asyncio
    async def test_get_cache_info(self, cache_manager):
        """Testa obtenção de informações do cache"""
        info = await cache_manager.get_cache_info()
        
        assert "strategy" in info
        assert "ttl" in info
        assert "max_size" in info
        assert "compression" in info
        assert "serialize" in info
        assert "metrics" in info


class TestMultiLevelCache:
    """Testes para classe MultiLevelCache"""
    
    @pytest.fixture
    def multi_level_cache(self):
        """Fixture para MultiLevelCache"""
        configs = {
            CacheLevel.MEMORY: CacheConfig(strategy=CacheStrategy.TTL, ttl=300),
            CacheLevel.REDIS: CacheConfig(strategy=CacheStrategy.TTL, ttl=3600)
        }
        return MultiLevelCache(configs)
    
    def test_multi_level_cache_initialization(self, multi_level_cache):
        """Testa inicialização do MultiLevelCache"""
        assert len(multi_level_cache.caches) == 2
        assert CacheLevel.MEMORY in multi_level_cache.caches
        assert CacheLevel.REDIS in multi_level_cache.caches
    
    @pytest.mark.asyncio
    async def test_multi_level_get(self, multi_level_cache):
        """Testa obtenção em múltiplos níveis"""
        # Simula valor no cache L1
        multi_level_cache.caches[CacheLevel.MEMORY]["test_key"] = "test_value"
        
        result = await multi_level_cache.get("test_key")
        assert result == "test_value"
    
    @pytest.mark.asyncio
    async def test_multi_level_set(self, multi_level_cache):
        """Testa definição em múltiplos níveis"""
        success = await multi_level_cache.set("test_key", "test_value")
        assert success is True
        
        # Verifica se foi armazenado em todos os níveis
        assert "test_key" in multi_level_cache.caches[CacheLevel.MEMORY]
        assert "test_key" in multi_level_cache.caches[CacheLevel.REDIS]
    
    def test_multi_level_metrics(self, multi_level_cache):
        """Testa métricas de múltiplos níveis"""
        metrics = multi_level_cache.get_metrics()
        
        assert CacheLevel.MEMORY in metrics
        assert CacheLevel.REDIS in metrics


class TestCacheDecorator:
    """Testes para classe CacheDecorator"""
    
    @pytest.fixture
    def cache_manager(self):
        """Fixture para CacheManager"""
        return CacheManager()
    
    @pytest.fixture
    def cache_decorator(self, cache_manager):
        """Fixture para CacheDecorator"""
        return CacheDecorator(cache_manager, ttl=1800)
    
    def test_cache_decorator_initialization(self, cache_decorator, cache_manager):
        """Testa inicialização do CacheDecorator"""
        assert cache_decorator.cache_manager == cache_manager
        assert cache_decorator.ttl == 1800
        assert cache_decorator.key_generator is not None
    
    def test_default_key_generator(self, cache_decorator):
        """Testa gerador de chaves padrão"""
        def test_function(arg1, arg2, kwarg1="default"):
            return f"{arg1}_{arg2}_{kwarg1}"
        
        key = cache_decorator._default_key_generator(test_function, "value1", "value2", kwarg1="custom")
        
        assert "test_function" in key
        assert "value1" in key
        assert "value2" in key
        assert "custom" in key
    
    @pytest.mark.asyncio
    async def test_cache_decorator_function(self, cache_decorator):
        """Testa decorator em função"""
        call_count = 0
        
        @cache_decorator
        async def test_function(param1, param2):
            nonlocal call_count
            call_count += 1
            return f"result_{param1}_{param2}"
        
        # Primeira chamada - deve executar a função
        result1 = await test_function("a", "b")
        assert result1 == "result_a_b"
        assert call_count == 1
        
        # Segunda chamada - deve retornar do cache
        result2 = await test_function("a", "b")
        assert result2 == "result_a_b"
        assert call_count == 1  # Não deve incrementar


class TestCacheInvalidator:
    """Testes para classe CacheInvalidator"""
    
    @pytest.fixture
    def cache_manager(self):
        """Fixture para CacheManager"""
        return CacheManager()
    
    @pytest.fixture
    def cache_invalidator(self, cache_manager):
        """Fixture para CacheInvalidator"""
        return CacheInvalidator(cache_manager)
    
    def test_cache_invalidator_initialization(self, cache_invalidator, cache_manager):
        """Testa inicialização do CacheInvalidator"""
        assert cache_invalidator.cache_manager == cache_manager
        assert cache_invalidator.patterns == []
    
    def test_add_pattern(self, cache_invalidator):
        """Testa adição de padrão"""
        cache_invalidator.add_pattern("user:*")
        assert "user:*" in cache_invalidator.patterns
    
    @pytest.mark.asyncio
    async def test_invalidate_by_pattern(self, cache_invalidator):
        """Testa invalidação por padrão"""
        # Adiciona alguns valores ao cache
        await cache_invalidator.cache_manager.set("user:123", "data1")
        await cache_invalidator.cache_manager.set("user:456", "data2")
        await cache_invalidator.cache_manager.set("product:789", "data3")
        
        # Adiciona padrão e invalida
        cache_invalidator.add_pattern("user:*")
        await cache_invalidator.invalidate_by_pattern("user:*")
        
        # Verifica se apenas os valores do padrão foram removidos
        assert await cache_invalidator.cache_manager.get("user:123") is None
        assert await cache_invalidator.cache_manager.get("user:456") is None
        assert await cache_invalidator.cache_manager.get("product:789") is not None
    
    @pytest.mark.asyncio
    async def test_invalidate_all(self, cache_invalidator):
        """Testa invalidação completa"""
        # Adiciona alguns valores
        await cache_invalidator.cache_manager.set("key1", "value1")
        await cache_invalidator.cache_manager.set("key2", "value2")
        
        # Invalida tudo
        await cache_invalidator.invalidate_all()
        
        # Verifica se foram removidos
        assert await cache_invalidator.cache_manager.get("key1") is None
        assert await cache_invalidator.cache_manager.get("key2") is None


class TestCacheAnalytics:
    """Testes para classe CacheAnalytics"""
    
    @pytest.fixture
    def cache_manager(self):
        """Fixture para CacheManager"""
        return CacheManager()
    
    @pytest.fixture
    def cache_analytics(self, cache_manager):
        """Fixture para CacheAnalytics"""
        return CacheAnalytics(cache_manager)
    
    def test_cache_analytics_initialization(self, cache_analytics, cache_manager):
        """Testa inicialização do CacheAnalytics"""
        assert cache_analytics.cache_manager == cache_manager
        assert cache_analytics.access_log == []
    
    @pytest.mark.asyncio
    async def test_record_access(self, cache_analytics):
        """Testa registro de acesso"""
        await cache_analytics.record_access("test_key", True, 0.05)
        
        assert len(cache_analytics.access_log) == 1
        assert cache_analytics.access_log[0]["key"] == "test_key"
        assert cache_analytics.access_log[0]["hit"] is True
        assert cache_analytics.access_log[0]["response_time"] == 0.05
    
    def test_get_analytics(self, cache_analytics):
        """Testa obtenção de analytics"""
        analytics = cache_analytics.get_analytics()
        
        assert "total_accesses" in analytics
        assert "hit_rate" in analytics
        assert "avg_response_time" in analytics
        assert "slow_queries" in analytics
        assert "popular_keys" in analytics


class TestFactoryFunctions:
    """Testes para funções factory"""
    
    def test_create_cache_manager(self):
        """Testa função create_cache_manager"""
        manager = create_cache_manager(CacheStrategy.LRU, ttl=1800, max_size=500)
        
        assert isinstance(manager, CacheManager)
        assert manager.config.strategy == CacheStrategy.LRU
        assert manager.config.ttl == 1800
        assert manager.config.max_size == 500
    
    def test_create_multi_level_cache(self):
        """Testa função create_multi_level_cache"""
        cache = create_multi_level_cache()
        
        assert isinstance(cache, MultiLevelCache)
        assert len(cache.caches) > 0
    
    def test_get_cache_manager_singleton(self):
        """Testa função get_cache_manager"""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()
        
        assert manager1 is manager2  # Deve ser singleton
    
    def test_get_multi_level_cache_singleton(self):
        """Testa função get_multi_level_cache"""
        cache1 = get_multi_level_cache()
        cache2 = get_multi_level_cache()
        
        assert cache1 is cache2  # Deve ser singleton


class TestCachedDecorator:
    """Testes para decorator cached"""
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self):
        """Testa decorator cached"""
        call_count = 0
        
        @cached(ttl=1800)
        async def test_function(param1, param2):
            nonlocal call_count
            call_count += 1
            return f"result_{param1}_{param2}"
        
        # Primeira chamada
        result1 = await test_function("a", "b")
        assert result1 == "result_a_b"
        assert call_count == 1
        
        # Segunda chamada - deve usar cache
        result2 = await test_function("a", "b")
        assert result2 == "result_a_b"
        assert call_count == 1  # Não deve incrementar
    
    @pytest.mark.asyncio
    async def test_cached_decorator_custom_key_generator(self):
        """Testa decorator cached com gerador de chaves customizado"""
        call_count = 0
        
        def custom_key_generator(func, *args, **kwargs):
            return f"custom_{func.__name__}_{args[0]}"
        
        @cached(ttl=1800, key_generator=custom_key_generator)
        async def test_function(param1, param2):
            nonlocal call_count
            call_count += 1
            return f"result_{param1}_{param2}"
        
        # Primeira chamada
        result1 = await test_function("a", "b")
        assert result1 == "result_a_b"
        assert call_count == 1
        
        # Segunda chamada - deve usar cache
        result2 = await test_function("a", "c")  # param2 diferente
        assert result2 == "result_a_c"
        assert call_count == 2  # Deve incrementar pois chave é diferente


class TestIntegrationScenarios:
    """Testes de cenários de integração"""
    
    @pytest.mark.asyncio
    async def test_cache_strategy_workflow(self):
        """Testa workflow completo de estratégia de cache"""
        # Cria cache manager
        manager = CacheManager(CacheConfig(strategy=CacheStrategy.TTL, ttl=60))
        
        # Adiciona valores
        await manager.set("key1", "value1")
        await manager.set("key2", "value2")
        
        # Recupera valores
        assert await manager.get("key1") == "value1"
        assert await manager.get("key2") == "value2"
        
        # Verifica métricas
        metrics = manager.get_metrics()
        assert metrics["sets"] == 2
        assert metrics["hits"] == 2
        
        # Remove valor
        await manager.delete("key1")
        assert await manager.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_multi_level_cache_workflow(self):
        """Testa workflow completo de cache multi-nível"""
        configs = {
            CacheLevel.MEMORY: CacheConfig(strategy=CacheStrategy.TTL, ttl=30),
            CacheLevel.REDIS: CacheConfig(strategy=CacheStrategy.TTL, ttl=300)
        }
        cache = MultiLevelCache(configs)
        
        # Adiciona valor
        await cache.set("key1", "value1")
        
        # Recupera valor
        result = await cache.get("key1")
        assert result == "value1"
        
        # Verifica métricas
        metrics = cache.get_metrics()
        assert CacheLevel.MEMORY in metrics
        assert CacheLevel.REDIS in metrics
    
    @pytest.mark.asyncio
    async def test_cache_decorator_workflow(self):
        """Testa workflow completo de decorator de cache"""
        manager = CacheManager()
        decorator = CacheDecorator(manager, ttl=60)
        
        call_count = 0
        
        @decorator
        async def expensive_operation(param):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simula operação cara
            return f"result_{param}"
        
        # Primeira execução
        result1 = await expensive_operation("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Segunda execução - deve usar cache
        result2 = await expensive_operation("test")
        assert result2 == "result_test"
        assert call_count == 1  # Não deve incrementar 