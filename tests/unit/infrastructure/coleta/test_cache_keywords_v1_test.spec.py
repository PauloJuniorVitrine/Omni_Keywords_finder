import pytest
import asyncio
import time
from infrastructure.coleta.utils.cache_keywords_v1 import SimpleAsyncCache
from typing import Dict, List, Optional, Any

@pytest.mark.asyncio
async def test_cache_set_get():
    cache = SimpleAsyncCache(ttl=1)
    await cache.set("k1", "v1")
    assert await cache.get("k1") == "v1"

@pytest.mark.asyncio
async def test_cache_expira():
    cache = SimpleAsyncCache(ttl=0.1)
    await cache.set("k2", "v2")
    time.sleep(0.2)
    assert await cache.get("k2") is None

@pytest.mark.asyncio
async def test_cache_get_nao_existente():
    cache = SimpleAsyncCache()
    assert await cache.get("naoexiste") is None 