import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.reddit import RedditColetor
import asyncio
from typing import Dict, List, Optional, Any

def async_cm_mock(resp):
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = resp
    mock_cm.__aexit__.return_value = None
    return mock_cm

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_valida():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    session_mock = MagicMock()
    mock_resp1 = MagicMock()
    mock_resp1.status = 200
    mock_resp1.json = AsyncMock(return_value={"suggestions": [{"value": "subreddit para aprender python"}, {"value": "discussao sobre tecnologia"}]})
    mock_resp2 = MagicMock()
    mock_resp2.status = 200
    mock_resp2.json = AsyncMock(return_value={"data": {"children": [{"data": {"title": "Aprenda Python"}}]}})
    session_mock.get = AsyncMock(side_effect=[async_cm_mock(mock_resp1), async_cm_mock(mock_resp2)])
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("python")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_com_cache():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    sugestoes = await coletor.extrair_sugestoes("input")
    assert "cache1" in sugestoes
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock(side_effect=Exception("erro"))), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"data": {"children": []}})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        metricas = await coletor.extrair_metricas_especificas("python")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_com_cache():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"total_posts": 10})
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    metricas = await coletor.extrair_metricas_especificas("input")
    assert metricas["total_posts"] == 10
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_erro():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock(side_effect=Exception("erro"))), \
         patch("shared.logger.logger") as logger_mock:
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_validar_termo_especifico_valido():
    coletor = RedditColetor()
    termo = "subreddit exemplo teste"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo():
    coletor = RedditColetor()
    resultado = await coletor.validar_termo_especifico("t" * 251)
    assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs():
    coletor = RedditColetor()
    with patch("shared.logger.logger") as logger_mock:
        resultado = await coletor.validar_termo_especifico("t" * 251)
        assert resultado is False

@pytest.mark.asyncio
async def test_extrair_sugestoes_concorrente():
    coletor = RedditColetor()
    session_mock = MagicMock()
    session_mock.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"subreddits": [], "data": {"children": []}})))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)):
        results = await asyncio.gather(
            coletor.extrair_sugestoes("input1"),
            coletor.extrair_sugestoes("input2"),
            coletor.extrair_sugestoes("input3")
        )
        assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_vazia():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    session_mock = MagicMock()
    mock_resp1 = MagicMock()
    mock_resp1.status = 200
    mock_resp1.json = AsyncMock(return_value={"suggestions": []})
    mock_resp2 = MagicMock()
    mock_resp2.status = 200
    mock_resp2.json = AsyncMock(return_value={"data": {"children": []}})
    session_mock.get = AsyncMock(side_effect=[async_cm_mock(mock_resp1), async_cm_mock(mock_resp2)])
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("python")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_dados_malformados():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    session_mock = MagicMock()
    mock_resp1 = MagicMock()
    mock_resp1.status = 200
    mock_resp1.json = AsyncMock(return_value={})
    mock_resp2 = MagicMock()
    mock_resp2.status = 200
    mock_resp2.json = AsyncMock(return_value={})
    session_mock.get = AsyncMock(side_effect=[async_cm_mock(mock_resp1), async_cm_mock(mock_resp2)])
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("python")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_vazia():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"data": {"children": []}})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        metricas = await coletor.extrair_metricas_especificas("python")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_dados_malformados():
    coletor = RedditColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        metricas = await coletor.extrair_metricas_especificas("python")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio():
    coletor = RedditColetor()
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False  # Termo vazio deve ser rejeitado 