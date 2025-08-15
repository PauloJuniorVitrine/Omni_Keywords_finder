from typing import Dict, List, Optional, Any
"""
Testes unitários para SimpleAsyncCache (cache_keywords_v1.py)
"""
import pytest
import asyncio
import time
from infrastructure.coleta.utils.cache_keywords_v1 import SimpleAsyncCache

@pytest.mark.asyncio
async def test_set_get_cache():
    cache = SimpleAsyncCache(ttl=1)
    await cache.set("k1", 123)
    value = await cache.get("k1")
    assert value == 123

@pytest.mark.asyncio
async def test_expiracao_cache():
    cache = SimpleAsyncCache(ttl=0.1)
    await cache.set("k2", 456)
    await asyncio.sleep(0.2)
    value = await cache.get("k2")
    assert value is None

@pytest.mark.asyncio
async def test_cache_edge_cases():
    cache = SimpleAsyncCache(ttl=1)
    value = await cache.get("nao_existe")
    assert value is None 