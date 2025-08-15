import pytest
import asyncio
from infrastructure.coleta.utils.async_coletor_v1 import AsyncColetor
from typing import Dict, List, Optional, Any

@pytest.mark.asyncio
async def test_coletar_sucesso():
    async def fonte1(termo, **filtros):
        return [{"fonte": "f1", "termo": termo}]
    async def fonte2(termo, **filtros):
        return [{"fonte": "f2", "termo": termo}]
    coletor = AsyncColetor([fonte1, fonte2])
    result = await coletor.coletar("abc")
    assert any(r["fonte"] == "f1" for r in result)
    assert any(r["fonte"] == "f2" for r in result)

@pytest.mark.asyncio
async def test_coletar_cache_hit():
    class DummyCache:
        def __init__(self): self._d = {}
        async def get(self, key): return self._d.get(key)
        async def set(self, key, value): self._d[key] = value
    cache = DummyCache()
    cache._d["keywords:abc:{}"] = [{"fonte": "cache", "termo": "abc"}]
    async def fonte(termo, **filtros): return [{"fonte": "f", "termo": termo}]
    coletor = AsyncColetor([fonte], cache=cache)
    result = await coletor.coletar("abc")
    assert result[0]["fonte"] == "cache"

@pytest.mark.asyncio
async def test_coletar_fonte_falha():
    async def fonte_ok(termo, **filtros): return [{"fonte": "ok", "termo": termo}]
    async def fonte_fail(termo, **filtros): raise Exception("erro")
    coletor = AsyncColetor([fonte_ok, fonte_fail])
    result = await coletor.coletar("abc")
    assert any(r["fonte"] == "ok" for r in result) 