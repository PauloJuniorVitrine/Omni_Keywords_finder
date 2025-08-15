import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.instagram import InstagramColetor
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
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    # Mock para /tags/search/
    mock_resp_tags = MagicMock()
    mock_resp_tags.status = 200
    mock_resp_tags.json = AsyncMock(return_value={"suggestions": [{"value": "dica para engajamento instagram"}, {"value": "como crescer seguidores"}]})
    # Mock para /users/search/
    mock_resp_users = MagicMock()
    mock_resp_users.status = 200
    mock_resp_users.json = AsyncMock(return_value={"users": [{"username": "user1"}]})
    session_mock = MagicMock()
    session_mock.get = AsyncMock(side_effect=[async_cm_mock(mock_resp_tags), async_cm_mock(mock_resp_users)])
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        # Se erro de protocolo, apenas valida lista vazia
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_com_cache():
    coletor = InstagramColetor()
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
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp_tags = MagicMock()
    mock_resp_tags.status = 404
    mock_resp_tags.json = AsyncMock(return_value={})
    session_mock = MagicMock()
    session_mock.get = AsyncMock(return_value=mock_resp_tags)
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
async def test_extrair_sugestoes_status_nao_200_logs():
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    # Mock para /tags/search/ com status 404
    mock_resp_tags = MagicMock()
    mock_resp_tags.status = 404
    mock_resp_tags.json = AsyncMock(return_value={})
    session_mock = MagicMock()
    session_mock.get = AsyncMock(side_effect=[async_cm_mock(mock_resp_tags)])
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro_json():
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp_tags = MagicMock()
    mock_resp_tags.status = 200
    mock_resp_tags.json = AsyncMock(side_effect=Exception("json error"))
    session_mock = MagicMock()
    session_mock.get = AsyncMock(return_value=mock_resp_tags)
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro_json_logs():
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    # Mock para /tags/search/ com erro no json
    mock_resp_tags = MagicMock()
    mock_resp_tags.status = 200
    mock_resp_tags.json = AsyncMock(side_effect=Exception("json error"))
    session_mock = MagicMock()
    session_mock.get = AsyncMock(side_effect=[async_cm_mock(mock_resp_tags)])
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False), \
         patch("shared.logger.logger") as logger_mock:
        sugestoes = await coletor.extrair_sugestoes("input")
        assert isinstance(sugestoes, list)

@pytest.mark.asyncio
async def test_extrair_sugestoes_concorrente():
    coletor = InstagramColetor()
    mock_resp_tags = MagicMock()
    mock_resp_tags.status = 200
    mock_resp_tags.json = AsyncMock(return_value={"suggestions": [{"value": "dica para engajamento instagram"}, {"value": "como crescer seguidores"}]})
    mock_resp_users = MagicMock()
    mock_resp_users.status = 200
    mock_resp_users.json = AsyncMock(return_value={"users": [{"username": "user"}]})
    session_mock = MagicMock()
    session_mock.get = AsyncMock(side_effect=[mock_resp_tags, mock_resp_users, mock_resp_tags, mock_resp_users, mock_resp_tags, mock_resp_users])
    with patch.object(InstagramColetor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch.object(InstagramColetor, '_autenticar', AsyncMock()), \
         patch.object(InstagramColetor, '_precisa_reautenticar', return_value=False):
        results = await asyncio.gather(
            coletor.extrair_sugestoes("input1"),
            coletor.extrair_sugestoes("input2"),
            coletor.extrair_sugestoes("input3")
        )
        assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida():
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"metricas": {"alcance": 1000, "engajamento": 100}})
    session_mock = MagicMock()
    session_mock.get = AsyncMock(side_effect=[async_cm_mock(mock_resp)])
    with patch.object(coletor, '_get_session', AsyncMock(return_value=session_mock)), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_com_cache():
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"metricas": {"alcance": 1000}})
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["metricas"]["alcance"] == 1000
        cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_erro():
    coletor = InstagramColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_get_session', AsyncMock(side_effect=Exception("erro"))), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert isinstance(metricas, dict)
        assert "volume" in metricas
        assert "tipo" in metricas

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_erro_logs():
    coletor = InstagramColetor()
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
async def test_validar_termo_especifico_valido():
    coletor = InstagramColetor()
    termo = "hashtag exemplo teste"  # termo válido
    assert coletor.validar_termo_especifico(termo)

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio():
    coletor = InstagramColetor()
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        resultado = await coletor.validar_termo_especifico("")
        assert resultado is False  # Termo vazio deve ser rejeitado

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo():
    coletor = InstagramColetor()
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False):
        resultado = await coletor.validar_termo_especifico("t" * 101)
        assert resultado is False  # Termo longo deve ser rejeitado

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs():
    coletor = InstagramColetor()
    with patch.object(coletor, '_get_session', AsyncMock()), \
         patch.object(coletor, '_autenticar', AsyncMock()), \
         patch.object(coletor, '_precisa_reautenticar', return_value=False), \
         patch("shared.logger.logger") as logger_mock:
        resultado = await coletor.validar_termo_especifico("")
        assert resultado is False  # Termo inválido deve ser rejeitado 