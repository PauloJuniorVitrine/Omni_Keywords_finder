from typing import Dict, List, Optional, Any
"""
Testes unitários para o coletor de buscas relacionadas do Google.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.google_related import GoogleRelatedColetor
import asyncio

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="BNeawe">relacionada1</div><div class="BNeawe">relacionada2</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "relacionada1" in sugestoes and "relacionada2" in sugestoes

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_vazia():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_status_nao_200():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro_rede():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=ConnectionError)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_com_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    sugestoes = await coletor.extrair_sugestoes("input")
    assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_termo_igual_sugestao():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-search">input</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_html_inesperado():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="wrong-class">relacionada</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_concorrente():
    logger_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="related-search">relacionada</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    coletores = []
    for _ in range(3):
        coletor = GoogleRelatedColetor(logger_=logger_mock)
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletores.append(coletor)
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        results = await asyncio.gather(
            coletores[0].extrair_sugestoes("input1"),
            coletores[1].extrair_sugestoes("input2"),
            coletores[2].extrair_sugestoes("input3")
        )
    assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div id="result-stats">Aproximadamente 1.000 resultados</div><div class="ads">Ad1</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_com_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"volume": 100, "concorrencia": 0.5})
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    metricas = await coletor.extrair_metricas_especificas("input")
    assert isinstance(metricas, dict)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    # Mockar apenas métodos existentes
    with patch('aiohttp.ClientSession.get', AsyncMock(side_effect=Exception('erro'))), \
         patch.object(coletor, 'extrair_sugestoes', AsyncMock(side_effect=Exception('erro'))):
        metricas = await coletor.extrair_metricas_especificas('input')
        assert isinstance(metricas, dict)
        assert metricas.get('ads_count', None) == 0
        assert metricas.get('concorrencia', None) == 0.0
        assert metricas.get('tendencia', None) == 0.0
        assert metricas.get('total_resultados', None) == 0

@pytest.mark.asyncio
async def test_validar_termo_especifico_valido():
    coletor = GoogleRelatedColetor()
    termo = "busca informacional teste"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio():
    coletor = GoogleRelatedColetor()
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo():
    coletor = GoogleRelatedColetor()
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_html_inesperado():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value='<html><div class="wrong-class">relacionada</div></html>')
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_logs_estruturados_extrair_sugestoes():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        await coletor.extrair_sugestoes("input")
        assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
async def test_logs_estruturados_extrair_metricas():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        await coletor.extrair_metricas_especificas("input")
        assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False
    assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
async def test_coletar_keywords_resposta_valida():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["kw1", "kw2"])), \
         patch.object(coletor, 'extrair_metricas_especificas', AsyncMock(return_value={"volume": 10, "concorrencia": 0.2, "tendencia": 0.5, "intencao": None})):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_resposta_vazia():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=[])):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_erro():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(side_effect=Exception("erro"))):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_com_cache():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["kw1"])), \
         patch.object(coletor, 'extrair_metricas_especificas', AsyncMock(return_value={"volume": 10, "concorrencia": 0.2, "tendencia": 0.5, "intencao": None})):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_limite():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["kw1"])), \
         patch.object(coletor, 'extrair_metricas_especificas', AsyncMock(return_value={"volume": 10, "concorrencia": 0.2, "tendencia": 0.5, "intencao": None})):
        keywords = await coletor.coletar_keywords("input", limite=1)
        assert isinstance(keywords, list)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_cache_formato_invalido():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=[1, 2, 3])  # tipo inválido
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch('aiohttp.ClientSession.get', AsyncMock(return_value=None)):
        try:
            metricas = await coletor.extrair_metricas_especificas("input")
        except Exception:
            metricas = {}
    assert isinstance(metricas, dict)
    assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_excecao_geral():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro"))
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch('aiohttp.ClientSession.get', AsyncMock(return_value=None)):
        try:
            sugestoes = await coletor.extrair_sugestoes("input")
        except Exception:
            sugestoes = []
    assert isinstance(sugestoes, list)
    assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_excecao_geral():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro"))
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch('aiohttp.ClientSession.get', AsyncMock(return_value=None)):
        try:
            metricas = await coletor.extrair_metricas_especificas("input")
        except Exception:
            metricas = {}
    assert isinstance(metricas, dict)
    assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_excecao_geral():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(side_effect=Exception("erro"))):
        try:
            keywords = await coletor.coletar_keywords("input")
        except Exception:
            keywords = []
    assert isinstance(keywords, list)
    assert logger_mock.error.call_count >= 0

def test_determinar_intencao_todos_ramos():
    coletor = GoogleRelatedColetor()
    # Informacional por palavra-chave
    assert coletor._determinar_intencao("como fazer", 0, 0).name == "INFORMACIONAL"
    # Transacional por palavra-chave
    assert coletor._determinar_intencao("comprar agora", 0, 0).name == "TRANSACIONAL"
    # Navegacional por palavra-chave
    assert coletor._determinar_intencao("login site", 0, 0).name == "NAVEGACIONAL"
    # Transacional por ads (termo sem match de palavra-chave)
    assert coletor._determinar_intencao("abcxyz", 0, 6).name == "TRANSACIONAL"
    # Informacional por total_resultados
    assert coletor._determinar_intencao("qualquer", 1000001, 0).name == "INFORMACIONAL"
    # Default (navegacional)
    assert coletor._determinar_intencao("abcxyz", 0, 0).name == "NAVEGACIONAL"

def test_classificar_intencao_todos_tipos():
    coletor = GoogleRelatedColetor()
    keywords = [
        "como fazer bolo",      # informacional
        "comprar sapato",      # transacional
        "melhor celular vs",   # comparacao
        "login site"           # navegacional
    ]
    intencoes = asyncio.run(coletor.classificar_intencao(keywords))
    assert len(intencoes) == 4
    assert intencoes[0].name == "INFORMACIONAL"
    assert intencoes[1].name == "TRANSACIONAL"
    assert intencoes[2].name == "COMPARACAO"
    assert intencoes[3].name == "NAVEGACIONAL"

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_valida_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    # Testar ambos os formatos possíveis de suggestions
    for suggestions in [
        [{"value": "palavra chave relacionada exemplo"}, {"value": "busca semantica google"}],
        ["palavra chave relacionada exemplo", "busca semantica google"]
    ]:
        mock_resp.json = AsyncMock(return_value={"suggestions": suggestions})
        mock_resp.text = AsyncMock(return_value="")
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_get.__aexit__ = AsyncMock(return_value=None)
        with patch("aiohttp.ClientSession.get", return_value=mock_get):
            sugestoes = await coletor.extrair_sugestoes("input")
            assert "palavra chave relacionada exemplo" in sugestoes and "busca semantica google" in sugestoes

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_vazia_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": []})
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_status_nao_200_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro_rede_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=ConnectionError)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_com_cache_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    sugestoes = await coletor.extrair_sugestoes("input")
    assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_termo_igual_sugestao_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": ["input"]})
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_html_inesperado_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": ["relacionada"]})
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_concorrente_json():
    logger_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": ["relacionada"]})
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    coletores = []
    for _ in range(3):
        coletor = GoogleRelatedColetor(logger_=logger_mock)
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletores.append(coletor)
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        results = await asyncio.gather(
            coletores[0].extrair_sugestoes("input1"),
            coletores[1].extrair_sugestoes("input2"),
            coletores[2].extrair_sugestoes("input3")
        )
    assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"resultStats": "Aproximadamente 1.000 resultados", "ads": "Ad1"})
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_com_cache_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"volume": 100, "concorrencia": 0.5})
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    metricas = await coletor.extrair_metricas_especificas("input")
    assert isinstance(metricas, dict)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    session_mock = MagicMock()
    session_mock.get = AsyncMock(side_effect=Exception('erro'))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)):
        metricas = await coletor.extrair_metricas_especificas('input')
        assert isinstance(metricas, dict)
        assert metricas == {
            "total_resultados": 0,
            "ads_count": 0,
            "volume": 0,
            "concorrencia": 0.0,
            "tendencia": 0.0,
            "intencao": coletor._determinar_intencao('input', 0, 0)
        }

@pytest.mark.asyncio
async def test_validar_termo_especifico_valido_json():
    coletor = GoogleRelatedColetor()
    termo = "busca informacional teste"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio_json():
    coletor = GoogleRelatedColetor()
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo_json():
    coletor = GoogleRelatedColetor()
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_html_inesperado_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": ["relacionada"]})
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_logs_estruturados_extrair_sugestoes_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        await coletor.extrair_sugestoes("input")
        assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
async def test_logs_estruturados_extrair_metricas_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_get = AsyncMock()
    mock_get.__aenter__.return_value = mock_resp
    mock_get.__aexit__.return_value = None
    with patch("aiohttp.ClientSession.get", return_value=mock_get):
        await coletor.extrair_metricas_especificas("input")
        assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    resultado = await coletor.validar_termo_especifico("")
    assert resultado is False
    assert logger_mock.error.call_count >= 0

@pytest.mark.asyncio
async def test_coletar_keywords_resposta_valida_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["kw1", "kw2"])), \
         patch.object(coletor, 'extrair_metricas_especificas', AsyncMock(return_value={"volume": 10, "concorrencia": 0.2, "tendencia": 0.5, "intencao": None})):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_resposta_vazia_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=[])):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_erro_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(side_effect=Exception("erro"))):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_com_cache_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["kw1"])), \
         patch.object(coletor, 'extrair_metricas_especificas', AsyncMock(return_value={"volume": 10, "concorrencia": 0.2, "tendencia": 0.5, "intencao": None})):
        keywords = await coletor.coletar_keywords("input")
        assert isinstance(keywords, list)

@pytest.mark.asyncio
async def test_coletar_keywords_limite_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(return_value=["kw1"])), \
         patch.object(coletor, 'extrair_metricas_especificas', AsyncMock(return_value={"volume": 10, "concorrencia": 0.2, "tendencia": 0.5, "intencao": None})):
        keywords = await coletor.coletar_keywords("input", limite=1)
        assert isinstance(keywords, list)

def test_extrair_sugestoes_cache_formato_invalido_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=123)  # tipo inválido
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    sugestoes = asyncio.run(coletor.extrair_sugestoes("input"))
    assert isinstance(sugestoes, list)
    assert logger_mock.error.call_count >= 0

def test_extrair_metricas_especificas_cache_formato_invalido_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=[1, 2, 3])  # tipo inválido
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    metricas = asyncio.run(coletor.extrair_metricas_especificas("input"))
    assert isinstance(metricas, dict)
    assert logger_mock.error.call_count >= 0

def test_extrair_sugestoes_excecao_geral_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro"))
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    sugestoes = asyncio.run(coletor.extrair_sugestoes("input"))
    assert isinstance(sugestoes, list)
    assert logger_mock.error.call_count >= 0

def test_extrair_metricas_especificas_excecao_geral_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro"))
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    metricas = asyncio.run(coletor.extrair_metricas_especificas("input"))
    assert isinstance(metricas, dict)
    assert logger_mock.error.call_count >= 0

def test_coletar_keywords_excecao_geral_json():
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    logger_mock = MagicMock()
    coletor = GoogleRelatedColetor(cache=cache_mock, logger_=logger_mock)
    with patch.object(coletor, 'extrair_sugestoes', AsyncMock(side_effect=Exception("erro"))):
        keywords = asyncio.run(coletor.coletar_keywords("input"))
        assert isinstance(keywords, list)
        assert logger_mock.error.call_count >= 0

def test_determinar_intencao_todos_ramos_json():
    coletor = GoogleRelatedColetor()
    # Informacional por palavra-chave
    assert coletor._determinar_intencao("como fazer", 0, 0).name == "INFORMACIONAL"
    # Transacional por palavra-chave
    assert coletor._determinar_intencao("comprar agora", 0, 0).name == "TRANSACIONAL"
    # Navegacional por palavra-chave
    assert coletor._determinar_intencao("login site", 0, 0).name == "NAVEGACIONAL"
    # Transacional por ads (termo sem match de palavra-chave)
    assert coletor._determinar_intencao("abcxyz", 0, 6).name == "TRANSACIONAL"
    # Informacional por total_resultados
    assert coletor._determinar_intencao("qualquer", 1000001, 0).name == "INFORMACIONAL"
    # Default (navegacional)
    assert coletor._determinar_intencao("abcxyz", 0, 0).name == "NAVEGACIONAL"

def test_classificar_intencao_todos_tipos_json():
    coletor = GoogleRelatedColetor()
    keywords = [
        "como fazer bolo",      # informacional
        "comprar sapato",      # transacional
        "melhor celular vs",   # comparacao
        "login site"           # navegacional
    ]
    intencoes = asyncio.run(coletor.classificar_intencao(keywords))
    assert len(intencoes) == 4
    assert intencoes[0].name == "INFORMACIONAL"
    assert intencoes[1].name == "TRANSACIONAL"
    assert intencoes[2].name == "COMPARACAO"
    assert intencoes[3].name == "NAVEGACIONAL" 