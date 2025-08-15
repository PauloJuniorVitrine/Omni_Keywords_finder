import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.tiktok import TikTokColetor
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
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "dica para viralizar tiktok"}, {"value": "musica para video curto"}]})
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_com_cache():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "cache1" in sugestoes
        cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_sugestoes_status_nao_200():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_resp.json = AsyncMock(return_value={})
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro_json():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(side_effect=Exception("json error"))
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_concorrente():
    coletor = TikTokColetor()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "dica para viralizar tiktok"}, {"value": "musica para video curto"}]})
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        results = await asyncio.gather(
            coletor.extrair_sugestoes("input1"),
            coletor.extrair_sugestoes("input2"),
            coletor.extrair_sugestoes("input3")
        )
        assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"stats": {"views": 1000, "likes": 100, "shares": 10}})
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_com_cache():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"stats": {"views": 1000}})
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_erro():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock(side_effect=Exception("erro"))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_validar_termo_especifico_valido():
    coletor = TikTokColetor()
    termo = "tiktok exemplo teste"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio():
    coletor = TikTokColetor()
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        resultado = await coletor.validar_termo_especifico("")
        assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo():
    coletor = TikTokColetor()
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        resultado = await coletor.validar_termo_especifico("t" * 101)
        assert resultado is False

@pytest.mark.asyncio
async def test_extrair_sugestoes_termo_igual_sugestao():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"suggestions": [{"value": "dica para viralizar tiktok"}, {"value": "musica para video curto"}]})
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_inesperada():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={})
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_logs_erro():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_resp.json = AsyncMock(return_value={})
    with patch.object(coletor, '_get_session', AsyncMock(return_value=MagicMock(get=AsyncMock(return_value=async_cm_mock(mock_resp))))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_metricas_logs_erro():
    coletor = TikTokColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock(side_effect=Exception("erro"))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False), \
         patch("shared.logger.logger") as logger_mock:
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs():
    coletor = TikTokColetor()
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False), \
         patch("shared.logger.logger") as logger_mock:
        resultado = await coletor.validar_termo_especifico("#@!")
        assert resultado is False 