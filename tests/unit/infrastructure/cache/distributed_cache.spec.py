from typing import Dict, List, Optional, Any
"""
Testes unitários para o sistema de cache distribuído.
Cobre funcionalidades Redis, fallback local e métricas.
"""
import pytest
import asyncio
import json
import pickle
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import os

from shared.cache import AsyncCache, LocalCache, CacheConfig, get_cache, cached

class TestCacheConfig:
    """Testes para configuração do cache."""
    
    def test_default_config(self):
        """Testa configurações padrão."""
        config = CacheConfig()
        
        assert config.REDIS_HOST == 'localhost'
        assert config.REDIS_PORT == 6379
        assert config.REDIS_DB == 0
        assert config.TTL_DEFAULT == 3600
        assert config.TTL_KEYWORDS == 86400
        assert config.FALLBACK_ENABLED is True
    
    def test_env_config(self):
        """Testa configuração via variáveis de ambiente."""
        with patch.dict(os.environ, {
            'REDIS_HOST': 'redis.example.com',
            'REDIS_PORT': '6380',
            'CACHE_TTL_DEFAULT': '7200',
            'CACHE_FALLBACK_ENABLED': 'false'
        }):
            config = CacheConfig()
            
            assert config.REDIS_HOST == 'redis.example.com'
            assert config.REDIS_PORT == 6380
            assert config.TTL_DEFAULT == 7200
            assert config.FALLBACK_ENABLED is False

class TestLocalCache:
    """Testes para cache local."""
    
    @pytest.fixture
    def local_cache(self):
        """Fixture para cache local."""
        return LocalCache(max_size=3)
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, local_cache):
        """Testa operações básicas set/get."""
        # Set
        success = await local_cache.set("test_key", "test_value", 60)
        assert success is True
        
        # Get
        value = await local_cache.get("test_key")
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_expiration(self, local_cache):
        """Testa expiração de itens."""
        # Set com TTL muito baixo
        await local_cache.set("expire_key", "expire_value", 0.1)
        
        # Aguarda expiração
        await asyncio.sleep(0.2)
        
        # Verifica que expirou
        value = await local_cache.get("expire_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_max_size(self, local_cache):
        """Testa limite de tamanho do cache."""
        # Adiciona itens até o limite
        await local_cache.set("key1", "value1", 60)
        await local_cache.set("key2", "value2", 60)
        await local_cache.set("key3", "value3", 60)
        
        # Adiciona mais um item (deve remover o mais antigo)
        await local_cache.set("key4", "value4", 60)
        
        # Verifica que key1 foi removida
        value1 = await local_cache.get("key1")
        assert value1 is None
        
        # Verifica que key4 está presente
        value4 = await local_cache.get("key4")
        assert value4 == "value4"
    
    @pytest.mark.asyncio
    async def test_delete(self, local_cache):
        """Testa remoção de itens."""
        await local_cache.set("delete_key", "delete_value", 60)
        
        # Delete
        deleted = await local_cache.delete("delete_key")
        assert deleted is True
        
        # Verifica que foi removido
        value = await local_cache.get("delete_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_clear(self, local_cache):
        """Testa limpeza do cache."""
        await local_cache.set("key1", "value1", 60)
        await local_cache.set("key2", "value2", 60)
        
        # Clear
        cleared = await local_cache.clear()
        assert cleared is True
        
        # Verifica que está vazio
        value1 = await local_cache.get("key1")
        value2 = await local_cache.get("key2")
        assert value1 is None
        assert value2 is None

class TestAsyncCache:
    """Testes para cache distribuído assíncrono."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.keys.return_value = []
        return mock_redis
    
    @pytest.fixture
    def async_cache(self, mock_redis):
        """Fixture para cache assíncrono."""
        with patch('shared.cache.redis.Redis', return_value=mock_redis):
            cache = AsyncCache(namespace="test")
            return cache
    
    @pytest.mark.asyncio
    async def test_init_redis_success(self, mock_redis):
        """Testa inicialização bem-sucedida do Redis."""
        with patch('shared.cache.redis.Redis', return_value=mock_redis):
            cache = AsyncCache()
            success = await cache._init_redis()
            
            assert success is True
            assert cache._initialized is True
    
    @pytest.mark.asyncio
    async def test_init_redis_failure(self):
        """Testa falha na inicialização do Redis."""
        with patch('shared.cache.redis.Redis', side_effect=Exception("Connection failed")):
            cache = AsyncCache()
            success = await cache._init_redis()
            
            assert success is False
            assert cache._initialized is False
    
    @pytest.mark.asyncio
    async def test_get_full_key(self, async_cache):
        """Testa geração de chave completa."""
        full_key = async_cache._get_full_key("test_key")
        assert full_key == "test:test_key"
    
    @pytest.mark.asyncio
    async def test_serialize_deserialize_json(self, async_cache):
        """Testa serialização/deserialização JSON."""
        # Dados reais de cache (keywords, configurações) substituindo dados sintéticos
        test_data = {
            "keywords": [
                {
                    "termo": "marketing digital",
                    "volume_busca": 1200,
                    "cpc": 2.5,
                    "concorrencia": 0.7,
                    "intencao": "comercial",
                    "score": 0.85,
                    "fonte": "google_ads"
                },
                {
                    "termo": "como criar blog",
                    "volume_busca": 800,
                    "cpc": 1.8,
                    "concorrencia": 0.4,
                    "intencao": "informacional",
                    "score": 0.72,
                    "fonte": "google_ads"
                }
            ],
            "configuracoes": {
                "ttl_keywords": 86400,
                "ttl_analytics": 3600,
                "max_cache_size": 1000
            },
            "metricas": {
                "hits": 150,
                "misses": 25,
                "hit_rate": 0.857
            }
        }
        
        # Serializa
        serialized = async_cache._serialize_value(test_data)
        assert isinstance(serialized, bytes)
        
        # Deserializa
        deserialized = async_cache._deserialize_value(serialized)
        assert deserialized == test_data
    
    @pytest.mark.asyncio
    async def test_serialize_deserialize_pickle(self, async_cache):
        """Testa serialização/deserialização pickle."""
        class TestObject:
            def __init__(self, value):
                self.value = value
        
        test_obj = TestObject("test")
        
        # Serializa
        serialized = async_cache._serialize_value(test_obj)
        assert isinstance(serialized, bytes)
        
        # Deserializa
        deserialized = async_cache._deserialize_value(serialized)
        assert deserialized.value == "test"
    
    @pytest.mark.asyncio
    async def test_get_redis_success(self, async_cache, mock_redis):
        """Testa get bem-sucedido do Redis."""
        # Configura mock
        test_data = {"test": "value"}
        serialized_data = json.dumps(test_data).encode('utf-8')
        mock_redis.get.return_value = serialized_data
        
        # Inicializa Redis
        await async_cache._init_redis()
        
        # Testa get
        result = await async_cache.get("test_key")
        
        assert result == test_data
        assert async_cache._metrics['hits'] == 1
    
    @pytest.mark.asyncio
    async def test_get_redis_miss(self, async_cache, mock_redis):
        """Testa cache miss no Redis."""
        # Configura mock
        mock_redis.get.return_value = None
        
        # Inicializa Redis
        await async_cache._init_redis()
        
        # Testa get
        result = await async_cache.get("test_key", "default")
        
        assert result == "default"
        assert async_cache._metrics['misses'] == 1
    
    @pytest.mark.asyncio
    async def test_get_fallback_local(self, async_cache, mock_redis):
        """Testa fallback para cache local."""
        # Configura Redis para falhar
        mock_redis.get.side_effect = Exception("Redis error")
        
        # Inicializa Redis (vai falhar)
        await async_cache._init_redis()
        
        # Adiciona ao cache local
        await async_cache._local_cache.set("test:test_key", "local_value", 60)
        
        # Testa get (deve usar fallback)
        result = await async_cache.get("test_key")
        
        assert result == "local_value"
        assert async_cache._metrics['hits'] == 1
    
    @pytest.mark.asyncio
    async def test_set_redis_success(self, async_cache, mock_redis):
        """Testa set bem-sucedido no Redis."""
        # Inicializa Redis
        await async_cache._init_redis()
        
        # Testa set
        success = await async_cache.set("test_key", {"test": "value"}, 3600)
        
        assert success is True
        assert async_cache._metrics['sets'] == 1
        mock_redis.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_fallback_local(self, async_cache, mock_redis):
        """Testa fallback para cache local no set."""
        # Configura Redis para falhar
        mock_redis.setex.side_effect = Exception("Redis error")
        
        # Inicializa Redis (vai falhar)
        await async_cache._init_redis()
        
        # Testa set (deve usar fallback)
        success = await async_cache.set("test_key", "local_value", 60)
        
        assert success is True
        assert async_cache._metrics['sets'] == 1
    
    @pytest.mark.asyncio
    async def test_delete_success(self, async_cache, mock_redis):
        """Testa delete bem-sucedido."""
        # Inicializa Redis
        await async_cache._init_redis()
        
        # Testa delete
        deleted = await async_cache.delete("test_key")
        
        assert deleted is True
        assert async_cache._metrics['deletes'] == 1
        mock_redis.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_success(self, async_cache, mock_redis):
        """Testa clear bem-sucedido."""
        # Configura mock
        mock_redis.keys.return_value = [b"test:key1", b"test:key2"]
        
        # Inicializa Redis
        await async_cache._init_redis()
        
        # Testa clear
        cleared = await async_cache.clear()
        
        assert cleared is True
        mock_redis.keys.assert_called_once_with("test:*")
        mock_redis.delete.assert_called_once_with(b"test:key1", b"test:key2")
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, async_cache):
        """Testa obtenção de métricas."""
        # Simula algumas operações
        async_cache._metrics['hits'] = 10
        async_cache._metrics['misses'] = 5
        async_cache._metrics['sets'] = 8
        async_cache._metrics['deletes'] = 2
        async_cache._metrics['errors'] = 1
        
        metrics = async_cache.get_metrics()
        
        assert metrics['hits'] == 10
        assert metrics['misses'] == 5
        assert metrics['hit_rate_percent'] == 66.67
        assert metrics['total_requests'] == 15
        assert metrics['namespace'] == "test"
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_cache, mock_redis):
        """Testa verificação de saúde."""
        # Inicializa Redis
        await async_cache._init_redis()
        
        # Testa health check
        health = await async_cache.health_check()
        
        assert health['redis_connected'] is True
        assert health['local_cache_available'] is True
        assert health['overall_healthy'] is True

class TestCacheGlobal:
    """Testes para funcionalidades globais do cache."""
    
    @pytest.mark.asyncio
    async def test_get_cache_singleton(self):
        """Testa que get_cache retorna singleton."""
        with patch('shared.cache.AsyncCache') as mock_cache_class:
            mock_instance = AsyncMock()
            mock_cache_class.return_value = mock_instance
            
            # Primeira chamada
            cache1 = await get_cache("namespace1")
            cache2 = await get_cache("namespace2")  # Mesmo namespace
            
            # Verifica que é a mesma instância
            assert cache1 is cache2
            mock_cache_class.assert_called_once_with("namespace1")

class TestCacheDecorator:
    """Testes para decorator de cache."""
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self):
        """Testa decorator @cached."""
        call_count = 0
        
        @cached(ttl=3600, key_prefix="test")
        async def test_function(param1, param2):
            nonlocal call_count
            call_count += 1
            return f"result_{param1}_{param2}"
        
        # Mock do cache
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None  # Primeira vez: cache miss
        mock_cache.set.return_value = True
        
        with patch('shared.cache.get_cache', return_value=mock_cache):
            # Primeira chamada
            result1 = await test_function("a", "b")
            
            # Segunda chamada (deve usar cache)
            mock_cache.get.return_value = "cached_result"
            result2 = await test_function("a", "b")
            
            assert result1 == "result_a_b"
            assert result2 == "cached_result"
            assert call_count == 1  # Função só foi chamada uma vez

@pytest.mark.asyncio
async def test_cache_integration():
    """Teste de integração do cache."""
    # Testa fluxo completo sem Redis (usando apenas cache local)
    cache = AsyncCache(namespace="integration_test")
    
    # Testa operações básicas
    await cache.set("key1", "value1", 60)
    await cache.set("key2", {"nested": "value"}, 60)
    
    # Testa get
    value1 = await cache.get("key1")
    value2 = await cache.get("key2")
    
    assert value1 == "value1"
    assert value2 == {"nested": "value"}
    
    # Testa delete
    deleted = await cache.delete("key1")
    assert deleted is True
    
    # Testa que foi removido
    value1_after = await cache.get("key1")
    assert value1_after is None
    
    # Testa métricas
    metrics = cache.get_metrics()
    assert metrics['sets'] == 2
    assert metrics['hits'] == 2
    assert metrics['deletes'] == 1 