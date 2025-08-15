# Caching System
from typing import Any, Optional
import json
import time
from collections import OrderedDict

class Cache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.ttl: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check TTL
        if key in self.ttl and time.time() > self.ttl[key]:
            self.delete(key)
            return None
        
        # Move to end (LRU)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        # Remove if exists
        if key in self.cache:
            self.cache.pop(key)
        
        # Check size limit
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            self.cache.popitem(last=False)
        
        # Add new item
        self.cache[key] = value
        self.ttl[key] = time.time() + ttl
        return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            self.cache.pop(key)
            self.ttl.pop(key, None)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.ttl.clear()

cache = Cache()

def cache_response(ttl: int = 3600):
    """Cache decorator for API responses"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator 