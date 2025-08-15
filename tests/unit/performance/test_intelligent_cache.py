"""
Test Intelligent Cache System
============================

Unit tests for the intelligent cache system with adaptive TTL.

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: TEST_INTELLIGENT_CACHE_20250127_001
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.cache.intelligent_cache import (
    IntelligentCache, 
    CacheEntry, 
    intelligent_cache_decorator
)


class TestCacheEntry:
    """Test CacheEntry functionality."""
    
    def test_cache_entry_creation(self):
        """Test CacheEntry creation with default values."""
        entry = CacheEntry(
            value={"test": "data"},
            created_at=time.time(),
            last_accessed=time.time()
        )
        
        assert entry.value == {"test": "data"}
        assert entry.access_count == 0
        assert entry.base_ttl == 3600
        assert entry.adaptive_ttl == 3600
    
    def test_cache_entry_update_access(self):
        """Test access tracking and TTL calculation."""
        entry = CacheEntry(
            value="test_value",
            created_at=time.time(),
            last_accessed=time.time()
        )
        
        # Update access multiple times
        for i in range(5):
            entry.update_access()
            time.sleep(0.1)
        
        assert entry.access_count == 5
        assert len(entry.access_pattern) == 5
        assert entry.adaptive_ttl > 0
    
    def test_cache_entry_adaptive_ttl_calculation(self):
        """Test adaptive TTL calculation based on access patterns."""
        entry = CacheEntry(
            value="test_value",
            created_at=time.time(),
            last_accessed=time.time(),
            base_ttl=3600
        )
        
        # Simulate high frequency access
        for i in range(10):
            entry.update_access()
            time.sleep(0.05)  # Very frequent access
        
        # TTL should be increased for high frequency
        assert entry.adaptive_ttl >= entry.base_ttl
    
    def test_cache_entry_volatility_adjustment(self):
        """Test TTL adjustment based on volatility score."""
        entry = CacheEntry(
            value="test_value",
            created_at=time.time(),
            last_accessed=time.time(),
            base_ttl=3600,
            volatility_score=0.8  # High volatility
        )
        
        entry.update_access()
        
        # High volatility should reduce TTL
        assert entry.adaptive_ttl < entry.base_ttl


class TestIntelligentCache:
    """Test IntelligentCache functionality."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        with patch('app.cache.intelligent_cache.redis') as mock_redis:
            mock_client = Mock()
            mock_redis.from_url.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def cache(self, mock_redis):
        """Create IntelligentCache instance with mocked Redis."""
        return IntelligentCache()
    
    def test_cache_initialization(self, cache):
        """Test cache initialization."""
        assert cache.max_cache_size == 10000
        assert cache.min_ttl == 300
        assert cache.max_ttl == 7200
        assert cache.default_ttl == 3600
    
    def test_generate_key(self, cache):
        """Test cache key generation."""
        key = cache._generate_key("test_key", "namespace")
        assert key.startswith("intelligent_cache:namespace:")
        assert len(key) > 30  # Should be hashed
    
    def test_set_cache_entry_success(self, cache, mock_redis):
        """Test successful cache entry setting."""
        mock_redis.setex.return_value = True
        
        result = cache._set_cache_entry("test_key", "test_value", 1800)
        
        assert result is True
        mock_redis.setex.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_redis.setex.call_args
        assert call_args[0][0].startswith("intelligent_cache:default:")
        assert call_args[0][1] > 0  # TTL should be set
        assert isinstance(call_args[0][2], str)  # JSON string
    
    def test_set_cache_entry_failure(self, cache, mock_redis):
        """Test cache entry setting failure."""
        mock_redis.setex.side_effect = Exception("Redis error")
        
        result = cache._set_cache_entry("test_key", "test_value")
        
        assert result is False
    
    def test_get_cache_entry_success(self, cache, mock_redis):
        """Test successful cache entry retrieval."""
        # Mock cache entry data
        entry_data = {
            "value": "test_value",
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 0,
            "access_pattern": [],
            "volatility_score": 0.0,
            "base_ttl": 3600,
            "adaptive_ttl": 3600
        }
        
        mock_redis.get.return_value = json.dumps(entry_data)
        
        entry = cache._get_cache_entry("test_key")
        
        assert entry is not None
        assert entry.value == "test_value"
        assert isinstance(entry, CacheEntry)
    
    def test_get_cache_entry_not_found(self, cache, mock_redis):
        """Test cache entry retrieval when not found."""
        mock_redis.get.return_value = None
        
        entry = cache._get_cache_entry("test_key")
        
        assert entry is None
    
    def test_get_cache_entry_invalid_json(self, cache, mock_redis):
        """Test cache entry retrieval with invalid JSON."""
        mock_redis.get.return_value = "invalid json"
        
        entry = cache._get_cache_entry("test_key")
        
        assert entry is None
    
    def test_get_success(self, cache, mock_redis):
        """Test successful get operation."""
        entry_data = {
            "value": "test_value",
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 0,
            "access_pattern": [],
            "volatility_score": 0.0,
            "base_ttl": 3600,
            "adaptive_ttl": 3600
        }
        
        mock_redis.get.return_value = json.dumps(entry_data)
        
        result = cache.get("test_key")
        
        assert result == "test_value"
        assert cache.cache_stats["hits"] == 1
        assert cache.cache_stats["misses"] == 0
    
    def test_get_miss(self, cache, mock_redis):
        """Test cache miss operation."""
        mock_redis.get.return_value = None
        
        result = cache.get("test_key", "default_value")
        
        assert result == "default_value"
        assert cache.cache_stats["hits"] == 0
        assert cache.cache_stats["misses"] == 1
    
    def test_set_success(self, cache, mock_redis):
        """Test successful set operation."""
        mock_redis.setex.return_value = True
        
        result = cache.set("test_key", "test_value", 1800)
        
        assert result is True
        assert cache.cache_stats["sets"] == 1
    
    def test_delete_success(self, cache, mock_redis):
        """Test successful delete operation."""
        mock_redis.delete.return_value = 1
        
        result = cache.delete("test_key")
        
        assert result is True
        assert cache.cache_stats["deletes"] == 1
    
    def test_delete_failure(self, cache, mock_redis):
        """Test delete operation failure."""
        mock_redis.delete.side_effect = Exception("Redis error")
        
        result = cache.delete("test_key")
        
        assert result is False
    
    def test_update_access_pattern(self, cache):
        """Test access pattern tracking."""
        cache._update_access_pattern("test_key")
        
        assert "test_key" in cache.access_patterns
        assert len(cache.access_patterns["test_key"]) == 1
    
    def test_get_stats(self, cache):
        """Test statistics retrieval."""
        # Simulate some operations
        cache.cache_stats["hits"] = 10
        cache.cache_stats["misses"] = 5
        cache.cache_stats["sets"] = 8
        cache.cache_stats["deletes"] = 2
        
        stats = cache.get_stats()
        
        assert stats["hits"] == 10
        assert stats["misses"] == 5
        assert stats["sets"] == 8
        assert stats["deletes"] == 2
        assert stats["hit_rate"] == 66.67  # 10/(10+5)*100
        assert stats["total_requests"] == 15
    
    def test_optimize_cache(self, cache):
        """Test cache optimization."""
        # Add some access patterns
        for i in range(5):
            cache._update_access_pattern(f"key_{i}")
            time.sleep(0.1)
        
        optimization = cache.optimize_cache()
        
        assert "entries_analyzed" in optimization
        assert "high_frequency_keys" in optimization
        assert "low_frequency_keys" in optimization
        assert "volatile_keys" in optimization


class TestIntelligentCacheDecorator:
    """Test intelligent cache decorator."""
    
    @pytest.fixture
    def mock_cache(self):
        """Mock cache for decorator testing."""
        with patch('app.cache.intelligent_cache.IntelligentCache') as mock_cache_class:
            mock_cache = Mock()
            mock_cache_class.return_value = mock_cache
            yield mock_cache
    
    def test_cache_decorator_hit(self, mock_cache):
        """Test cache decorator with cache hit."""
        mock_cache.get.return_value = "cached_result"
        
        @intelligent_cache_decorator(ttl=1800, key_prefix="test")
        def test_function(arg1, arg2):
            return f"result_{arg1}_{arg2}"
        
        result = test_function("value1", "value2")
        
        assert result == "cached_result"
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()
    
    def test_cache_decorator_miss(self, mock_cache):
        """Test cache decorator with cache miss."""
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        
        @intelligent_cache_decorator(ttl=1800, key_prefix="test")
        def test_function(arg1, arg2):
            return f"result_{arg1}_{arg2}"
        
        result = test_function("value1", "value2")
        
        assert result == "result_value1_value2"
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
    
    def test_cache_decorator_key_generation(self, mock_cache):
        """Test cache key generation in decorator."""
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        
        @intelligent_cache_decorator(ttl=1800, key_prefix="test")
        def test_function(arg1, arg2, kwarg1="default"):
            return f"result_{arg1}_{arg2}_{kwarg1}"
        
        test_function("value1", "value2", kwarg1="custom")
        
        # Verify key generation
        call_args = mock_cache.get.call_args[0][0]
        assert call_args.startswith("test:test_function:")
        assert "value1" in call_args
        assert "value2" in call_args
        assert "custom" in call_args


class TestCacheIntegration:
    """Integration tests for cache system."""
    
    @pytest.fixture
    def cache_with_mock_redis(self):
        """Create cache with mocked Redis for integration testing."""
        with patch('app.cache.intelligent_cache.redis') as mock_redis:
            mock_client = Mock()
            mock_redis.from_url.return_value = mock_client
            cache = IntelligentCache()
            yield cache, mock_client
    
    def test_full_cache_cycle(self, cache_with_mock_redis):
        """Test complete cache set/get cycle."""
        cache, mock_redis = cache_with_mock_redis
        
        # Mock successful operations
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        
        # Set value
        set_result = cache.set("test_key", "test_value", 1800)
        assert set_result is True
        
        # Mock get operation
        entry_data = {
            "value": "test_value",
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 0,
            "access_pattern": [],
            "volatility_score": 0.0,
            "base_ttl": 1800,
            "adaptive_ttl": 1800
        }
        mock_redis.get.return_value = json.dumps(entry_data)
        
        # Get value
        get_result = cache.get("test_key")
        assert get_result == "test_value"
        
        # Delete value
        delete_result = cache.delete("test_key")
        assert delete_result is True
        
        # Verify statistics
        stats = cache.get_stats()
        assert stats["sets"] == 1
        assert stats["hits"] == 1
        assert stats["deletes"] == 1
    
    def test_cache_with_complex_data(self, cache_with_mock_redis):
        """Test cache with complex data structures."""
        cache, mock_redis = cache_with_mock_redis
        
        complex_data = {
            "user_id": 123,
            "profile": {
                "name": "Test User",
                "email": "test@example.com",
                "preferences": ["keyword1", "keyword2"]
            },
            "analytics": {
                "total_searches": 150,
                "last_search": "2025-01-27T10:00:00Z"
            }
        }
        
        mock_redis.setex.return_value = True
        
        # Set complex data
        result = cache.set("user_profile:123", complex_data, 3600)
        assert result is True
        
        # Verify the data was serialized properly
        call_args = mock_redis.setex.call_args
        serialized_data = call_args[0][2]
        deserialized = json.loads(serialized_data)
        
        assert "value" in deserialized
        assert deserialized["value"]["user_id"] == 123
        assert deserialized["value"]["profile"]["name"] == "Test User"


if __name__ == "__main__":
    pytest.main([__file__]) 