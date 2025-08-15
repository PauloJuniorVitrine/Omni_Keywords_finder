"""
Intelligent Cache System with Adaptive TTL
==========================================

This module implements an intelligent caching system that adapts TTL based on:
- Access frequency patterns
- Data volatility
- User behavior analysis
- System load conditions

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: INTELLIGENT_CACHE_20250127_001
"""

import time
import json
import hashlib
from typing import Any, Dict, Optional, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from functools import wraps

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cache entry with intelligent TTL management."""
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    access_pattern: deque = field(default_factory=lambda: deque(maxlen=10))
    volatility_score: float = 0.0
    base_ttl: int = 3600  # 1 hour default
    adaptive_ttl: int = 3600
    
    def update_access(self) -> None:
        """Update access statistics for TTL calculation."""
        current_time = time.time()
        self.access_count += 1
        self.last_accessed = current_time
        self.access_pattern.append(current_time)
        self._calculate_adaptive_ttl()
    
    def _calculate_adaptive_ttl(self) -> None:
        """Calculate adaptive TTL based on access patterns."""
        if len(self.access_pattern) < 2:
            self.adaptive_ttl = self.base_ttl
            return
        
        # Calculate access frequency
        recent_accesses = list(self.access_pattern)[-5:]
        if len(recent_accesses) >= 2:
            intervals = [recent_accesses[i] - recent_accesses[i-1] 
                        for i in range(1, len(recent_accesses))]
            avg_interval = sum(intervals) / len(intervals)
            
            # Adjust TTL based on access frequency
            if avg_interval < 60:  # High frequency access
                self.adaptive_ttl = min(self.base_ttl * 2, 7200)  # Max 2 hours
            elif avg_interval < 300:  # Medium frequency
                self.adaptive_ttl = self.base_ttl
            else:  # Low frequency
                self.adaptive_ttl = max(self.base_ttl // 2, 1800)  # Min 30 min
        
        # Adjust for volatility
        volatility_factor = 1.0 - (self.volatility_score * 0.5)
        self.adaptive_ttl = int(self.adaptive_ttl * volatility_factor)


class IntelligentCache:
    """
    Intelligent cache system with adaptive TTL and access pattern analysis.
    
    Features:
    - Adaptive TTL based on access frequency
    - Volatility scoring for data freshness
    - Access pattern analysis
    - Automatic cache optimization
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize intelligent cache system."""
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.cache_stats = defaultdict(int)
        self.volatility_scores = defaultdict(float)
        self.access_patterns = defaultdict(lambda: deque(maxlen=20))
        
        # Configuration
        self.max_cache_size = 10000
        self.min_ttl = 300  # 5 minutes
        self.max_ttl = 7200  # 2 hours
        self.default_ttl = 3600  # 1 hour
        
        logger.info("Intelligent cache system initialized")
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate cache key with namespace."""
        return f"intelligent_cache:{namespace}:{hashlib.md5(key.encode()).hexdigest()}"
    
    def _get_cache_entry(self, key: str) -> Optional[CacheEntry]:
        """Retrieve cache entry with metadata."""
        try:
            cache_key = self._generate_key(key)
            data = self.redis_client.get(cache_key)
            if data:
                entry_data = json.loads(data)
                entry = CacheEntry(**entry_data)
                entry.update_access()
                return entry
        except (RedisError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Error retrieving cache entry for key {key}: {e}")
        return None
    
    def _set_cache_entry(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store cache entry with intelligent TTL."""
        try:
            cache_key = self._generate_key(key)
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                base_ttl=ttl or self.default_ttl
            )
            entry.update_access()
            
            # Store with adaptive TTL
            self.redis_client.setex(
                cache_key,
                entry.adaptive_ttl,
                json.dumps(entry.__dict__, default=str)
            )
            
            # Update statistics
            self.cache_stats["sets"] += 1
            return True
            
        except (RedisError, TypeError) as e:
            logger.error(f"Error setting cache entry for key {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with access pattern tracking."""
        entry = self._get_cache_entry(key)
        if entry:
            self.cache_stats["hits"] += 1
            self._update_access_pattern(key)
            return entry.value
        
        self.cache_stats["misses"] += 1
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with intelligent TTL."""
        return self._set_cache_entry(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        try:
            cache_key = self._generate_key(key)
            result = self.redis_client.delete(cache_key)
            self.cache_stats["deletes"] += 1
            return bool(result)
        except RedisError as e:
            logger.error(f"Error deleting cache entry for key {key}: {e}")
            return False
    
    def _update_access_pattern(self, key: str) -> None:
        """Update access pattern for key."""
        current_time = time.time()
        self.access_patterns[key].append(current_time)
        
        # Update volatility score based on access patterns
        if len(self.access_patterns[key]) >= 5:
            intervals = []
            pattern_list = list(self.access_patterns[key])
            for i in range(1, len(pattern_list)):
                intervals.append(pattern_list[i] - pattern_list[i-1])
            
            # Calculate volatility (standard deviation of intervals)
            if intervals:
                mean_interval = sum(intervals) / len(intervals)
                variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
                volatility = variance ** 0.5
                self.volatility_scores[key] = min(volatility / 1000, 1.0)  # Normalize
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics and performance metrics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "deletes": self.cache_stats["deletes"],
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "avg_volatility": sum(self.volatility_scores.values()) / len(self.volatility_scores) if self.volatility_scores else 0
        }
    
    def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache based on access patterns and performance."""
        optimization_stats = {
            "entries_analyzed": len(self.access_patterns),
            "high_frequency_keys": 0,
            "low_frequency_keys": 0,
            "volatile_keys": 0
        }
        
        for key, pattern in self.access_patterns.items():
            if len(pattern) >= 3:
                recent_accesses = list(pattern)[-3:]
                avg_interval = sum(recent_accesses[i] - recent_accesses[i-1] 
                                 for i in range(1, len(recent_accesses))) / (len(recent_accesses) - 1)
                
                if avg_interval < 60:
                    optimization_stats["high_frequency_keys"] += 1
                elif avg_interval > 300:
                    optimization_stats["low_frequency_keys"] += 1
                
                if self.volatility_scores.get(key, 0) > 0.7:
                    optimization_stats["volatile_keys"] += 1
        
        logger.info(f"Cache optimization completed: {optimization_stats}")
        return optimization_stats


def intelligent_cache_decorator(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for intelligent caching with adaptive TTL.
    
    Args:
        ttl: Base TTL in seconds
        key_prefix: Prefix for cache key generation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cache = IntelligentCache()
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator


# Global cache instance
intelligent_cache = IntelligentCache()


# Example usage and testing
if __name__ == "__main__":
    # Test intelligent cache functionality
    cache = IntelligentCache()
    
    # Test basic operations
    cache.set("test_key", {"data": "test_value"}, 1800)
    result = cache.get("test_key")
    print(f"Cache test result: {result}")
    
    # Test access pattern tracking
    for i in range(5):
        cache.get("test_key")
        time.sleep(0.1)
    
    # Get statistics
    stats = cache.get_stats()
    print(f"Cache statistics: {stats}")
    
    # Test optimization
    optimization = cache.optimize_cache()
    print(f"Optimization results: {optimization}") 