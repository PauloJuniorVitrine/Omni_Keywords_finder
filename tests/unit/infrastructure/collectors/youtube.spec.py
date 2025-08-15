import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.youtube import YouTubeColetor
from domain.models import IntencaoBusca
import asyncio
from typing import Dict, List, Optional, Any

def async_cm_mock(resp):
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = resp
    mock_cm.__aexit__.return_value = None
    return mock_cm

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_valida():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "video exemplo teste"}, {"value": "canal para aprendizado"}]})
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_com_cache():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    sugestoes = await coletor.extrair_sugestoes("input")
    assert "cache1" in sugestoes
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_sugestoes_status_nao_200():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_resp.json = AsyncMock(return_value=[])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro_json():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(side_effect=Exception("json error"))
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
async def test_extrair_sugestoes_concorrente():
    coletor = YouTubeColetor()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", ["sugestao"]])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))):
        results = await asyncio.gather(
            coletor.extrair_sugestoes("input1"),
            coletor.extrair_sugestoes("input2"),
            coletor.extrair_sugestoes("input3")
        )
        assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value="<html></html>")
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))), \
         patch("infrastructure.coleta.youtube.BeautifulSoup", MagicMock()) as bs_mock:
        bs_instance = bs_mock.return_value
        bs_instance.select.side_effect = lambda value: [MagicMock(get="href")] if value == "a.video-title" else []
        bs_instance.select.return_value = []
        bs_instance.find_all.return_value = []
        bs_instance.get_text.return_value = ""
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_com_cache():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"total_resultados": 100, "volume": 10})
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    metricas = await coletor.extrair_metricas_especificas("input")
    assert metricas["total_resultados"] == 100
    assert metricas["volume"] == 10
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_erro():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=Exception("erro"))):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["total_resultados"] == 0
        assert metricas["volume"] == 0

@pytest.mark.asyncio
async def test_validar_termo_especifico_valido():
    coletor = YouTubeColetor()
    termo = "video tutorial exemplo"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio():
    coletor = YouTubeColetor()
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo():
    coletor = YouTubeColetor()
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
async def test_extrair_sugestoes_termo_igual_sugestao():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", ["input"]])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
async def test_extrair_sugestoes_html_inesperado():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", ["sugestao1"]])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))), \
         patch("infrastructure.coleta.youtube.BeautifulSoup", MagicMock()) as bs_mock:
        bs_instance = bs_mock.return_value
        bs_instance.select.side_effect = Exception("HTML malformado")
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["total_resultados"] == 0
        assert metricas["volume"] == 0

@pytest.mark.asyncio
async def test_extrair_sugestoes_logs_erro():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_resp.json = AsyncMock(return_value=[])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=async_cm_mock(mock_resp))):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_metricas_logs_erro():
    coletor = YouTubeColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=Exception("erro"))):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs():
    coletor = YouTubeColetor()
    resultado = await coletor.validar_termo_especifico("#@!")
    assert resultado is False 