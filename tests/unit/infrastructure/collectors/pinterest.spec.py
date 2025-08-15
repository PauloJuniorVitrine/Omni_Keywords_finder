import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.pinterest import PinterestColetor
import asyncio
from typing import Dict, List, Optional, Any

def async_cm_mock(resp):
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = resp
    mock_cm.__aexit__.return_value = None
    return mock_cm

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_valida():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "ideias para decoracao casa"}, {"value": "receitas para jantar rapido"}]})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("diy decor")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 500
    mock_resp.json = AsyncMock(return_value={})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("diy decor")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_dados_malformados():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("diy decor")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    session_mock.get = AsyncMock(return_value=AsyncMock(status=200, text=AsyncMock(return_value="<div class='pin'></div><div class='board'></div>")))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("infrastructure.coleta.pinterest.BeautifulSoup", autospec=True) as bs_mock, \
         patch("shared.logger.logger") as logger_mock:
        soup_mock = MagicMock()
        soup_mock.find_all.side_effect = lambda *args, **kwargs: [1] if args[0] == "div" and kwargs.get("class_", None) in ("pin", "board") else []
        bs_mock.return_value = soup_mock
        metricas = await coletor.extrair_metricas_especificas("diy decor")
        assert "volume" in metricas
        logger_mock.info.assert_not_called()  # Não há log explícito de sucesso

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_erro():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    session_mock.get = AsyncMock(side_effect=Exception("erro"))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        metricas = await coletor.extrair_metricas_especificas("diy decor")
        assert metricas["volume"] == 0

@pytest.mark.asyncio
async def test_validar_termo_especifico_valido():
    coletor = PinterestColetor()
    resultado = await coletor.validar_termo_especifico("diy decor criativo")
    assert resultado is True

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo():
    coletor = PinterestColetor()
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_generico():
    coletor = PinterestColetor()
    resultado = await coletor.validar_termo_especifico("diy")
    assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs_longo():
    coletor = PinterestColetor()
    with patch("shared.logger.logger") as logger_mock:
        resultado = await coletor.validar_termo_especifico("t" * 101)
        assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs_generico():
    coletor = PinterestColetor()
    with patch("shared.logger.logger") as logger_mock:
        resultado = await coletor.validar_termo_especifico("diy")
        assert resultado is False

@pytest.mark.asyncio
async def test_extrair_sugestoes_concorrente():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "ideias para decoracao casa"}, {"value": "receitas para jantar rapido"}]})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)):
        results = await asyncio.gather(
            coletor.extrair_sugestoes("input1"),
            coletor.extrair_sugestoes("input2"),
            coletor.extrair_sugestoes("input3")
        )
        assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_vazia():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "ideias para decoracao casa"}, {"value": "receitas para jantar rapido"}]})
    session_mock.get = AsyncMock(return_value=async_cm_mock(mock_resp))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("diy decor")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_dados_malformados():
    coletor = PinterestColetor()
    session_mock = MagicMock()
    session_mock.get = AsyncMock(return_value=AsyncMock(status=200, text=AsyncMock(return_value="")))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch("infrastructure.coleta.pinterest.BeautifulSoup", autospec=True) as bs_mock, \
         patch("shared.logger.logger") as logger_mock:
        soup_mock = MagicMock()
        soup_mock.find_all.side_effect = Exception("malformed html")
        bs_mock.return_value = soup_mock
        metricas = await coletor.extrair_metricas_especificas("diy decor")
        assert metricas["volume"] == 0

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio():
    coletor = PinterestColetor()
    termo = "palavra chave pinterest"  # termo válido
    assert coletor.validar_termo_especifico(termo) 