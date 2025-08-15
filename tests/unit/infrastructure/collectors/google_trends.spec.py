import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.google_trends import GoogleTrendsColetor
from domain.models import IntencaoBusca
import asyncio
from typing import Dict, List, Optional, Any

class AsyncContextManagerMock:
    def __init__(self, resp):
        self.resp = resp
    async def __aenter__(self):
        if isinstance(self.resp, Exception):
            raise self.resp
        return self.resp
    async def __aexit__(self, exc_type, exc, tb):
        return None

@pytest.mark.asyncio
def make_coletor_with_logger(logger_mock=None, session=None):
    logger_ = logger_mock or MagicMock()
    return GoogleTrendsColetor(logger_=logger_, session=session)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_resposta_valida():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"default": {"trendingSearchesDays": [{"trendingSearches": [{"title": {"query": "trend1"}}, {"title": {"query": "trend2"}}]}]}})
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("input", session=session_mock)
    assert "trend1" in trends and "trend2" in trends

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_resposta_vazia():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"default": {"trendingSearchesDays": []}})
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("input", session=session_mock)
    assert trends == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_status_nao_200():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 404
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("input", session=session_mock)
    assert trends == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_erro_json():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(side_effect=Exception("json error"))
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("input", session=session_mock)
    assert trends == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_erro_rede():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(Exception("erro"))
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("input", session=session_mock)
    assert trends == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_timeout():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(TimeoutError())
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("input", session=session_mock)
    assert trends == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_com_cache():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    trends = await coletor.coletar("input", session=session_mock)
    assert "cache1" in trends
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_cache_set():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"default": {"trendingSearchesDays": [{"trendingSearches": [{"title": {"query": "trend"}}]}]}})
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    trends = await coletor.coletar("input", session=session_mock)
    assert "trend" in trends
    cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_parametros_edge():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={})
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("", session=session_mock)
    assert trends == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_concorrente():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"default": {"trendingSearchesDays": [{"trendingSearches": [{"title": {"query": "trend"}}]}]}})
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    # Cria 3 coletores independentes, cada um com cache mockado
    coletores = []
    for _ in range(3):
        coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletores.append(coletor)
    results = await asyncio.gather(
        coletores[0].coletar("input1", session=session_mock),
        coletores[1].coletar("input2", session=session_mock),
        coletores[2].coletar("input3", session=session_mock)
    )
    assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_resposta_valida():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_client') as client_mock, \
         patch.object(coletor, '_build_payload', AsyncMock()):
        client_instance = client_mock.return_value
        client_instance.related_queries = {"input": {"rising": {"trend1": 100}, "top": {"trend2": 200}}}
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "trend1" in sugestoes and "trend2" in sugestoes
        cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_com_cache():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    sugestoes = await coletor.extrair_sugestoes("input")
    assert "cache1" in sugestoes
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro_pytrends():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_client', side_effect=Exception("erro pytrends")), \
         patch.object(coletor, '_build_payload', AsyncMock()):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_concorrente():
    logger_mock = MagicMock()
    with patch.object(GoogleTrendsColetor, '_get_client') as client_mock, \
         patch.object(GoogleTrendsColetor, '_build_payload', AsyncMock()):
        client_instance = client_mock.return_value
        client_instance.related_queries = {
            "input1": {"rising": {"trend": 1}},
            "input2": {"top": {"trend": 2}},
            "input3": {}
        }
        coletores = []
        for _ in range(3):
            coletor = GoogleTrendsColetor(logger_=logger_mock)
            cache_mock = MagicMock()
            cache_mock.get = AsyncMock(return_value=None)
            cache_mock.set = AsyncMock()
            coletor.cache = cache_mock
            coletores.append(coletor)
        results = await asyncio.gather(
            coletores[0].extrair_sugestoes("input1"),
            coletores[1].extrair_sugestoes("input2"),
            coletores[2].extrair_sugestoes("input3")
        )
        assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_resposta_valida():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_client') as client_mock, \
         patch.object(coletor, '_build_payload', AsyncMock()):
        client_instance = client_mock.return_value
        client_instance.related_queries = {"input": {"rising": {"input": 1000}, "top": {"input": 1}}}
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)
        assert metricas["volume"] > 0
        cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_com_cache():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=[{"volume": 10, "cpc": 0.0, "concorrencia": 0.5, "intencao": IntencaoBusca.NAVEGACIONAL, "crescimento": 0, "tendencia": 0}, None])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    metricas = await coletor.extrair_metricas_especificas("input")
    assert metricas["volume"] == 10
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro_cache_get"))
    cache_mock.set = AsyncMock(side_effect=Exception("erro_cache_set"))
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_client', side_effect=Exception("erro pytrends")), \
         patch.object(coletor, '_build_payload', AsyncMock()):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)
        assert metricas["volume"] == 0
        assert metricas["intencao"] == IntencaoBusca.NAVEGACIONAL

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_valido():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    assert await coletor.validar_termo_especifico("como fazer bolo de cenoura")

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_vazio():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    assert not await coletor.validar_termo_especifico("")

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_longo():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    termo = "a" * 101
    assert not await coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_invalido_logs():
    logger_mock = MagicMock()
    coletor = GoogleTrendsColetor(logger_=logger_mock)
    assert not await coletor.validar_termo_especifico("preço")

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_trends_resposta_valida_with_suggestions():
    logger_mock = MagicMock()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={
        "default": {"trendingSearchesDays": [{"trendingSearches": [{"title": {"query": "trend1"}}]}]},
        "suggestions": [{"value": "sugestao1"}, "sugestao2"]
    })
    session_mock.get = lambda *args, **kwargs: AsyncContextManagerMock(mock_resp)
    coletor = GoogleTrendsColetor(logger_=logger_mock, session=session_mock)
    trends = await coletor.coletar("input", session=session_mock)
    assert "trend1" in trends and "sugestao1" in trends and "sugestao2" in trends 