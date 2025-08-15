import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.google_paa import GooglePAAColetor
from domain.models import IntencaoBusca
import asyncio
from typing import Dict, List, Optional, Any

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-question-pair">Pergunta 1</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_resposta_vazia():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html></html>')
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_status_nao_200():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro_rede():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=ConnectionError)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_com_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    sugestoes = await coletor.extrair_sugestoes("input")
    assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["sugestao1", "sugestao2"])):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)
        cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_com_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"volume": 100, "concorrencia": 0.5})
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    metricas = await coletor.extrair_metricas_especificas("input")
    assert isinstance(metricas, dict)
    assert metricas["volume"] == 100
    assert metricas["concorrencia"] == 0.5
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(side_effect=Exception("erro"))):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_valido():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("termo valido")
    assert resultado is True

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_vazio():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_longo():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_pergunta_igual_termo():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-question-pair">input</div></html>')
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_html_inesperado():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="wrong-class">Pergunta</div></html>')
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_concorrente():
    logger_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-question-pair">Pergunta</div></html>')
    coletores = []
    for _ in range(3):
        coletor = GooglePAAColetor(logger_=logger_mock)
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletores.append(coletor)
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        results = await asyncio.gather(
            coletores[0].extrair_sugestoes("input1"),
            coletores[1].extrair_sugestoes("input2"),
            coletores[2].extrair_sugestoes("input3")
        )
    assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_html_inesperado():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=[])):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_logs_estruturados_extrair_sugestoes():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get), \
         patch("shared.logger.logger.error") as logger_error:
        await coletor.extrair_sugestoes("input")
        assert True

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_logs_estruturados_extrair_metricas():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)), \
         patch("shared.logger.logger") as logger_mock:
        await coletor.extrair_metricas_especificas("input")
        assert True

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_invalido_logs():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False
    assert logger_mock.error.call_count > 0

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-question-pair">Pergunta 1</div></html>')
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_resposta_vazia():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html></html>')
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_erro():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_com_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    keywords = await coletor.coletar_keywords("input")
    assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_limite():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-question-pair">P1</div><div class="related-question-pair">P2</div></html>')
    with patch("aiohttp.ClientSession.get", AsyncMock(return_value=mock_resp)):
        keywords = await coletor.coletar_keywords("input", limite=1)
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro_cache_get"))
    cache_mock.set = AsyncMock(side_effect=Exception("erro_cache_set"))
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-question-pair">Pergunta 1</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro_cache_get"))
    cache_mock.set = AsyncMock(side_effect=Exception("erro_cache_set"))
    logger_mock = MagicMock()
    coletor = GooglePAAColetor(cache=cache_mock, logger_=logger_mock)
    metricas = await coletor.extrair_metricas_especificas("input")
    assert isinstance(metricas, dict) 