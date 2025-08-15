import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.amazon import AmazonColetor
from domain.models import IntencaoBusca, Keyword
from infrastructure.processamento.validador_keywords import ValidadorKeywords
import asyncio
from typing import Dict, List, Optional, Any

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_resposta_valida():
    coletor = AmazonColetor()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "produto exemplo teste"}, {"value": "produto para teste"}]})
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "produto exemplo teste" in sugestoes and "produto para teste" in sugestoes

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_resposta_vazia():
    coletor = AmazonColetor()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": []})
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_status_nao_200():
    coletor = AmazonColetor()
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro_json():
    coletor = AmazonColetor()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(side_effect=Exception("json error"))
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro_rede():
    coletor = AmazonColetor()
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=Exception("erro"))):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_timeout():
    coletor = AmazonColetor()
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=TimeoutError)):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_com_cache():
    coletor = AmazonColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    sugestoes = await coletor.extrair_sugestoes("input")
    assert "cache1" in sugestoes
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_cache_set():
    coletor = AmazonColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "produto exemplo teste"}]})
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "produto exemplo teste" in sugestoes
    cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_parametros_edge():
    coletor = AmazonColetor()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={})
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        sugestoes = await coletor.extrair_sugestoes("")
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_concorrente():
    logger_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "produto exemplo teste"}]})
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    coletores = []
    for _ in range(3):
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor = AmazonColetor(cache=cache_mock, logger_=logger_mock)
        coletores.append(coletor)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        results = await asyncio.gather(
            coletores[0].extrair_sugestoes("input1"),
            coletores[1].extrair_sugestoes("input2"),
            coletores[2].extrair_sugestoes("input3")
        )
    assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_resposta_valida():
    coletor = AmazonColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value="<html></html>")
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager), \
         patch.object(coletor, "_extrair_dados_produtos", AsyncMock(return_value=[{"preco": 10, "prime": True, "rating": 4.5, "total_reviews": 10, "categoria": "cat1"}])), \
         patch.object(coletor, "_extrair_categorias", AsyncMock(return_value={"cat1": 1})):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["total_produtos"] == 1
        assert metricas["produtos_prime"] == 1
        assert metricas["categoria"] == "cat1"
        assert "precos" in metricas
        cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_status_nao_200():
    coletor = AmazonColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["volume"] == 0
        assert metricas["concorrencia"] == 0.5
        assert metricas["categoria"] == "other"

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro_rede():
    coletor = AmazonColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=Exception("erro"))):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["volume"] == 0
        assert metricas["concorrencia"] == 0.5
        assert metricas["categoria"] == "other"

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_valido():
    coletor = AmazonColetor()
    termo = "produto exemplo teste"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_invalido():
    coletor = AmazonColetor()
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_invalido_logs():
    coletor = AmazonColetor()
    with patch.object(coletor, "registrar_erro") as registrar_erro_mock:
        resultado = await coletor.validar_termo_especifico("t" * 101)
        registrar_erro_mock.assert_called()
        assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_classificar_intencao():
    coletor = AmazonColetor()
    keywords = [
        "Como comprar barato",
        "Promoção exclusiva",
        "Melhor produto",
        "Acesse agora"
    ]
    intencoes = await coletor.classificar_intencao(keywords)
    assert intencoes[0] == IntencaoBusca.INFORMACIONAL
    assert intencoes[1] == IntencaoBusca.TRANSACIONAL
    assert intencoes[2] == IntencaoBusca.COMERCIAL
    assert intencoes[3] == IntencaoBusca.NAVEGACIONAL

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_resposta_valida():
    coletor = AmazonColetor()
    termo = "produto exemplo teste"  # termo válido
    mock_resp_sugestao = MagicMock()
    mock_resp_sugestao.status = 200
    mock_resp_sugestao.json = AsyncMock(return_value={"suggestions": [{"value": termo}]})
    mock_context_manager_sugestao = MagicMock()
    mock_context_manager_sugestao.__aenter__ = AsyncMock(return_value=mock_resp_sugestao)
    mock_context_manager_sugestao.__aexit__ = AsyncMock(return_value=None)
    mock_resp_search = MagicMock()
    mock_resp_search.status = 200
    mock_resp_search.text = AsyncMock(return_value="<html></html>")
    mock_context_manager_search = MagicMock()
    mock_context_manager_search.__aenter__ = AsyncMock(return_value=mock_resp_search)
    mock_context_manager_search.__aexit__ = AsyncMock(return_value=None)

    # Mock BeautifulSoup para garantir que o parsing retorna o termo esperado
    mock_bs_instance = MagicMock()
    mock_bs_instance.find_all.return_value = [MagicMock(get_text=MagicMock(return_value=termo))]

    with patch("aiohttp.ClientSession.get", side_effect=[mock_context_manager_sugestao, mock_context_manager_search]):
        with patch("infrastructure.coleta.amazon.BeautifulSoup", return_value=mock_bs_instance):
            keywords = await coletor.coletar_keywords(termo, limite=10)
            assert any(key.termo == termo for key in keywords)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_termo_invalido():
    coletor = AmazonColetor()
    with patch.object(coletor, "validar_termo", AsyncMock(return_value=False)):
        keywords = await coletor.coletar_keywords("t" * 101)
        assert keywords == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_keywords_erro_rede():
    coletor = AmazonColetor()
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=Exception("erro"))):
        keywords = await coletor.coletar_keywords("input")
        assert keywords == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_metricas_resposta_valida():
    coletor = AmazonColetor()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value="<html></html>")
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        with patch("infrastructure.coleta.amazon.BeautifulSoup", MagicMock()):
            metricas = await coletor.coletar_metricas(["produto exemplo teste"])
            assert isinstance(metricas, list)
            assert "keyword" in metricas[0]
            assert metricas[0]["keyword"] == "produto exemplo teste"

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_coletar_metricas_erro_rede():
    coletor = AmazonColetor()
    with patch("aiohttp.ClientSession.get", AsyncMock(side_effect=Exception("erro"))):
        metricas = await coletor.coletar_metricas(["produto exemplo teste"])
        assert metricas == []

def make_keyword(termo):
    return Keyword(
        termo=termo,
        volume_busca=100,
        cpc=1.0,
        concorrencia=0.5,
        intencao=IntencaoBusca.INFORMACIONAL
    )

@pytest.mark.parametrize("termo,modo_especial,esperado", [
    ("palavra1 palavra2", False, False),  # 2 palavras, rejeita
    ("palavra1 palavra2 palavra3", False, True),  # 3 palavras, aceita
    ("um dois tres quatro cinco seis sete", False, True),  # 7 palavras, aceita
    ("um dois tres quatro cinco seis sete oito", False, False),  # 8 palavras, rejeita
    ("um dois tres quatro cinco seis sete oito", True, True),  # 8 palavras, aceita especial
    ("um dois tres quatro cinco seis sete oito nove", True, True),  # 9 palavras, aceita especial
    ("um dois tres quatro cinco seis sete oito nove dez", False, False),  # 10 palavras, rejeita
    ("um dois tres quatro cinco seis sete oito nove dez", True, False),  # 10 palavras, rejeita especial
])
@pytest.mark.timeout(10)
def test_validar_quantidade_palavras(termo, modo_especial, esperado):
    validador = ValidadorKeywords()
    kw = make_keyword(termo)
    valido, motivo = validador.validar_keyword(kw, modo_especial=modo_especial)
    assert valido is esperado, f"Termo: '{termo}' | Modo especial: {modo_especial} | Esperado: {esperado} | Motivo: {motivo}"

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro_cache():
    coletor = AmazonColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro_cache_get"))
    cache_mock.set = AsyncMock(side_effect=Exception("erro_cache_set"))
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "produto exemplo teste"}]})
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "produto exemplo teste" in sugestoes

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro_cache():
    coletor = AmazonColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(side_effect=Exception("erro_cache_get"))
    cache_mock.set = AsyncMock(side_effect=Exception("erro_cache_set"))
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.text = AsyncMock(return_value="<html></html>")
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    with patch("aiohttp.ClientSession.get", return_value=mock_context_manager), \
         patch.object(coletor, "_extrair_dados_produtos", AsyncMock(return_value=[{"preco": 10, "prime": True, "rating": 4.5, "total_reviews": 10, "categoria": "cat1"}])), \
         patch.object(coletor, "_extrair_categorias", AsyncMock(return_value={"cat1": 1})):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["total_produtos"] == 1
        assert metricas["produtos_prime"] == 1
        assert metricas["categoria"] == "cat1" 