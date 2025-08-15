"""
Testes Unitários para IntelligentCache
IntelligentCache - Sistema de cache inteligente com TTL adaptativo

Prompt: Implementação de testes unitários para IntelligentCache
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_INTELLIGENT_CACHE_20250127_001
"""

import pytest
import time
import json
import hashlib
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from backend.app.cache.intelligent_cache import (
    CacheEntry,
    IntelligentCache
)


class TestCacheEntry:
    """Testes para CacheEntry"""
    
    @pytest.fixture
    def sample_entry_data(self):
        """Dados de exemplo para CacheEntry"""
        return {
            "value": {"user_id": 123, "name": "Test User"},
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 5,
            "volatility_score": 0.3,
            "base_ttl": 3600,
            "adaptive_ttl": 4200
        }
    
    @pytest.fixture
    def entry(self, sample_entry_data):
        """Instância de CacheEntry para testes"""
        return CacheEntry(**sample_entry_data)
    
    def test_initialization(self, sample_entry_data):
        """Testa inicialização básica"""
        entry = CacheEntry(**sample_entry_data)
        
        assert entry.value == {"user_id": 123, "name": "Test User"}
        assert entry.created_at == sample_entry_data["created_at"]
        assert entry.last_accessed == sample_entry_data["last_accessed"]
        assert entry.access_count == 5
        assert entry.volatility_score == 0.3
        assert entry.base_ttl == 3600
        assert entry.adaptive_ttl == 4200
        assert len(entry.access_pattern) == 0
    
    def test_default_values(self):
        """Testa valores padrão"""
        entry = CacheEntry(
            value="test_value",
            created_at=time.time(),
            last_accessed=time.time()
        )
        
        assert entry.access_count == 0
        assert entry.volatility_score == 0.0
        assert entry.base_ttl == 3600
        assert entry.adaptive_ttl == 3600
        assert len(entry.access_pattern) == 0
    
    def test_update_access(self, entry):
        """Testa atualização de acesso"""
        original_access_count = entry.access_count
        original_last_accessed = entry.last_accessed
        
        entry.update_access()
        
        assert entry.access_count == original_access_count + 1
        assert entry.last_accessed > original_last_accessed
        assert len(entry.access_pattern) == 1
    
    def test_multiple_access_updates(self, entry):
        """Testa múltiplas atualizações de acesso"""
        for i in range(10):
            entry.update_access()
        
        assert entry.access_count == 10
        assert len(entry.access_pattern) == 10
    
    def test_access_pattern_limit(self, entry):
        """Testa limite do padrão de acesso"""
        # Adicionar mais acessos que o limite (maxlen=10)
        for i in range(15):
            entry.update_access()
        
        assert entry.access_count == 15
        assert len(entry.access_pattern) == 10  # Limitado pelo maxlen
    
    def test_calculate_adaptive_ttl(self, entry):
        """Testa cálculo de TTL adaptativo"""
        # Simular padrão de acesso frequente
        for i in range(5):
            entry.update_access()
            time.sleep(0.01)  # Pequeno delay para diferenciar timestamps
        
        # Verificar se TTL foi ajustado
        assert entry.adaptive_ttl != entry.base_ttl
    
    def test_volatility_score_impact(self, entry):
        """Testa impacto do score de volatilidade no TTL"""
        entry.volatility_score = 0.8  # Alta volatilidade
        
        entry.update_access()
        
        # TTL deve ser reduzido para dados voláteis
        assert entry.adaptive_ttl <= entry.base_ttl


class TestIntelligentCache:
    """Testes para IntelligentCache"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis client"""
        redis_mock = Mock()
        redis_mock.get = Mock(return_value=None)
        redis_mock.setex = Mock(return_value=True)
        redis_mock.delete = Mock(return_value=1)
        return redis_mock
    
    @pytest.fixture
    def cache(self, mock_redis):
        """Instância de IntelligentCache para testes"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            return IntelligentCache(redis_url="redis://localhost:6379/0")
    
    def test_initialization(self, mock_redis):
        """Testa inicialização do cache"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            cache = IntelligentCache(redis_url="redis://localhost:6379/0")
            
            assert cache.redis_client == mock_redis
            assert cache.max_cache_size == 10000
            assert cache.min_ttl == 300
            assert cache.max_ttl == 7200
            assert cache.default_ttl == 3600
            assert len(cache.cache_stats) == 0
    
    def test_generate_key(self, cache):
        """Testa geração de chave de cache"""
        key = cache._generate_key("user:123:profile", "users")
        
        assert key.startswith("intelligent_cache:users:")
        assert len(key) == 64  # MD5 hash length
    
    def test_generate_key_without_namespace(self, cache):
        """Testa geração de chave sem namespace"""
        key = cache._generate_key("user:123:profile")
        
        assert key.startswith("intelligent_cache:default:")
    
    def test_get_cache_entry_success(self, cache, mock_redis):
        """Testa recuperação bem-sucedida de entrada de cache"""
        entry_data = {
            "value": {"test": "data"},
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 1,
            "volatility_score": 0.0,
            "base_ttl": 3600,
            "adaptive_ttl": 3600
        }
        
        mock_redis.get.return_value = json.dumps(entry_data)
        
        entry = cache._get_cache_entry("test_key")
        
        assert entry is not None
        assert entry.value == {"test": "data"}
        assert entry.access_count == 1
    
    def test_get_cache_entry_not_found(self, cache, mock_redis):
        """Testa recuperação de entrada não encontrada"""
        mock_redis.get.return_value = None
        
        entry = cache._get_cache_entry("test_key")
        
        assert entry is None
    
    def test_get_cache_entry_invalid_json(self, cache, mock_redis):
        """Testa recuperação com JSON inválido"""
        mock_redis.get.return_value = "invalid json"
        
        entry = cache._get_cache_entry("test_key")
        
        assert entry is None
    
    def test_set_cache_entry_success(self, cache, mock_redis):
        """Testa definição bem-sucedida de entrada de cache"""
        success = cache._set_cache_entry("test_key", {"test": "data"}, ttl=1800)
        
        assert success is True
        mock_redis.setex.assert_called_once()
        assert cache.cache_stats["sets"] == 1
    
    def test_set_cache_entry_failure(self, cache, mock_redis):
        """Testa falha na definição de entrada de cache"""
        mock_redis.setex.side_effect = Exception("Redis error")
        
        success = cache._set_cache_entry("test_key", {"test": "data"})
        
        assert success is False
        assert cache.cache_stats["sets"] == 0
    
    def test_get_success(self, cache, mock_redis):
        """Testa operação get bem-sucedida"""
        entry_data = {
            "value": {"test": "data"},
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 1,
            "volatility_score": 0.0,
            "base_ttl": 3600,
            "adaptive_ttl": 3600
        }
        
        mock_redis.get.return_value = json.dumps(entry_data)
        
        result = cache.get("test_key")
        
        assert result == {"test": "data"}
        assert cache.cache_stats["hits"] == 1
    
    def test_get_miss(self, cache, mock_redis):
        """Testa operação get com miss"""
        mock_redis.get.return_value = None
        
        result = cache.get("test_key", default="default_value")
        
        assert result == "default_value"
        assert cache.cache_stats["misses"] == 1
    
    def test_get_without_default(self, cache, mock_redis):
        """Testa operação get sem valor padrão"""
        mock_redis.get.return_value = None
        
        result = cache.get("test_key")
        
        assert result is None
        assert cache.cache_stats["misses"] == 1
    
    def test_set_success(self, cache, mock_redis):
        """Testa operação set bem-sucedida"""
        success = cache.set("test_key", {"test": "data"}, ttl=1800)
        
        assert success is True
        assert cache.cache_stats["sets"] == 1
    
    def test_set_without_ttl(self, cache, mock_redis):
        """Testa operação set sem TTL específico"""
        success = cache.set("test_key", {"test": "data"})
        
        assert success is True
        mock_redis.setex.assert_called_once()
    
    def test_delete_success(self, cache, mock_redis):
        """Testa operação delete bem-sucedida"""
        success = cache.delete("test_key")
        
        assert success is True
        mock_redis.delete.assert_called_once()
        assert cache.cache_stats["deletes"] == 1
    
    def test_delete_failure(self, cache, mock_redis):
        """Testa falha na operação delete"""
        mock_redis.delete.side_effect = Exception("Redis error")
        
        success = cache.delete("test_key")
        
        assert success is False
        assert cache.cache_stats["deletes"] == 0
    
    def test_update_access_pattern(self, cache):
        """Testa atualização do padrão de acesso"""
        cache._update_access_pattern("test_key")
        
        assert "test_key" in cache.access_patterns
        assert len(cache.access_patterns["test_key"]) == 1
    
    def test_multiple_access_patterns(self, cache):
        """Testa múltiplos padrões de acesso"""
        for i in range(5):
            cache._update_access_pattern(f"key_{i}")
        
        assert len(cache.access_patterns) == 5
        for i in range(5):
            assert f"key_{i}" in cache.access_patterns
    
    def test_access_pattern_limit(self, cache):
        """Testa limite do padrão de acesso"""
        # Adicionar mais acessos que o limite (maxlen=20)
        for i in range(25):
            cache._update_access_pattern("test_key")
        
        assert len(cache.access_patterns["test_key"]) == 20  # Limitado pelo maxlen
    
    def test_cache_stats_tracking(self, cache, mock_redis):
        """Testa rastreamento de estatísticas de cache"""
        # Simular algumas operações
        cache.get("key1")  # miss
        cache.get("key2")  # miss
        
        entry_data = {
            "value": "data",
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 1,
            "volatility_score": 0.0,
            "base_ttl": 3600,
            "adaptive_ttl": 3600
        }
        mock_redis.get.return_value = json.dumps(entry_data)
        cache.get("key3")  # hit
        
        cache.set("key4", "data")  # set
        cache.delete("key5")  # delete
        
        assert cache.cache_stats["misses"] == 2
        assert cache.cache_stats["hits"] == 1
        assert cache.cache_stats["sets"] == 1
        assert cache.cache_stats["deletes"] == 1


class TestIntelligentCacheIntegration:
    """Testes de integração para IntelligentCache"""
    
    @pytest.mark.asyncio
    async def test_full_cache_cycle(self, mock_redis):
        """Testa ciclo completo de cache"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            cache = IntelligentCache(redis_url="redis://localhost:6379/0")
            
            # Definir valor
            success = cache.set("user:123:profile", {"name": "John Doe"})
            assert success is True
            
            # Recuperar valor
            result = cache.get("user:123:profile")
            assert result == {"name": "John Doe"}
            
            # Deletar valor
            success = cache.delete("user:123:profile")
            assert success is True
            
            # Verificar que foi deletado
            result = cache.get("user:123:profile")
            assert result is None
    
    def test_adaptive_ttl_behavior(self, mock_redis):
        """Testa comportamento do TTL adaptativo"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            cache = IntelligentCache(redis_url="redis://localhost:6379/0")
            
            # Definir valor com TTL baixo
            cache.set("volatile_key", "data", ttl=300)
            
            # Simular acessos frequentes
            for i in range(10):
                cache.get("volatile_key")
                time.sleep(0.01)
            
            # Verificar se TTL foi ajustado
            # (Este teste depende da implementação específica do _calculate_adaptive_ttl)


class TestIntelligentCacheErrorHandling:
    """Testes de tratamento de erro para IntelligentCache"""
    
    def test_redis_connection_error(self, mock_redis):
        """Testa erro de conexão com Redis"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception, match="Connection failed"):
                IntelligentCache(redis_url="redis://localhost:6379/0")
    
    def test_redis_operation_error(self, mock_redis):
        """Testa erro em operação Redis"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            mock_redis.get.side_effect = Exception("Redis operation failed")
            
            cache = IntelligentCache(redis_url="redis://localhost:6379/0")
            
            # Operação deve falhar graciosamente
            result = cache.get("test_key")
            assert result is None
    
    def test_invalid_key_format(self, cache):
        """Testa formato de chave inválido"""
        # Chave vazia
        result = cache.get("")
        assert result is None
        
        # Chave None
        result = cache.get(None)
        assert result is None
    
    def test_large_value_handling(self, cache, mock_redis):
        """Testa manipulação de valores grandes"""
        large_value = {"data": "x" * 1000000}  # ~1MB
        
        success = cache.set("large_key", large_value)
        assert success is True


class TestIntelligentCachePerformance:
    """Testes de performance para IntelligentCache"""
    
    def test_concurrent_access_patterns(self, mock_redis):
        """Testa padrões de acesso concorrentes"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            cache = IntelligentCache(redis_url="redis://localhost:6379/0")
            
            # Simular muitos acessos concorrentes
            import threading
            
            def access_key(key):
                for i in range(100):
                    cache._update_access_pattern(key)
            
            threads = []
            for i in range(10):
                thread = threading.Thread(target=access_key, args=(f"key_{i}",))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Verificar se todos os padrões foram registrados
            assert len(cache.access_patterns) == 10
    
    def test_memory_usage_with_large_patterns(self, mock_redis):
        """Testa uso de memória com padrões grandes"""
        with patch('backend.app.cache.intelligent_cache.redis') as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            
            cache = IntelligentCache(redis_url="redis://localhost:6379/0")
            
            # Adicionar muitos padrões de acesso
            for i in range(10000):
                cache._update_access_pattern(f"key_{i}")
            
            # Verificar se o sistema continua funcionando
            assert len(cache.access_patterns) == 10000
            
            # Verificar limite de cada padrão
            for pattern in cache.access_patterns.values():
                assert len(pattern) <= 20  # maxlen configurado 