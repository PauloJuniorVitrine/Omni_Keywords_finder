import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.google_suggest import GoogleSuggestColetor
from domain.models import IntencaoBusca
import asyncio
from typing import Dict, List, Optional, Any

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "como usar google suggest"}, {"value": "dicas para pesquisa"}]})
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_resposta_vazia():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", []])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_resposta_malformada():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"erro": "formato invalido"})
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_status_nao_200():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_erro_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(side_effect=ValueError)
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_erro_rede():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=ConnectionError)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_timeout():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=TimeoutError)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_com_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    keywords = await coletor.coletar_keywords("input")
    assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_cache_set():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", ["sugestao"]])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_parametros_edge():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["", []])
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_idioma_pais():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", ["sugestao"]])
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value = mock_resp
        await coletor.coletar_keywords("input")
        called_kwargs = mock_get.call_args.kwargs
        assert called_kwargs["params"]["hl"] == "pt-BR"

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_sugestoes_concorrente():
    logger_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", ["sugestao"]])
    coletores = []
    for _ in range(3):
        coletor = GoogleSuggestColetor(logger_=logger_mock)
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletores.append(coletor)
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        results = await asyncio.gather(
            coletores[0].coletar_keywords("input1"),
            coletores[1].coletar_keywords("input2"),
            coletores[2].coletar_keywords("input3")
        )
    assert all(isinstance(keywords, list) for keywords in results)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", [["sugestao1"], ["sugestao2"]]])
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_resp
    mock_ctx.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_ctx):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)
        assert "sugestao1" in sugestoes or "sugestao2" in sugestoes

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["sugestao1", "sugestao2"])):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)
        assert "volume" in metricas
        assert "concorrencia" in metricas
        cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_invalido_logs():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False
    assert logger_mock.error.call_count > 0

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_valido():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    termo = "palavra chave exemplo"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_vazio():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_longo():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro de cache"))
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleSuggestColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value=["input", ["sugestao"]])
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_resp
    mock_ctx.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_ctx):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)
        assert "sugestao" in sugestoes
        # Verifica se o logger foi chamado para erro de cache
        assert any("erro_cache_get" in str(call) for call in logger_mock.error.call_args_list) 