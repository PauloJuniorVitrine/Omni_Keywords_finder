"""
Módulo: cache_keywords_v1
Cache assíncrono para resultados de coleta de palavras-chave.
"""
from typing import Any
import asyncio
import time

class SimpleAsyncCache:
    """
    Cache assíncrono simples com TTL por chave.
    """
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._store = {}
        self._expirations = {}
        self._lock = asyncio.Lock()

    async def set(self, key: str, value: Any):
        async with self._lock:
            self._store[key] = value
            self._expirations[key] = time.time() + self.ttl

    async def get(self, key: str) -> Any:
        async with self._lock:
            if key in self._store and self._expirations[key] > time.time():
                return self._store[key]
            if key in self._store:
                del self._store[key]
                del self._expirations[key]
            return None 