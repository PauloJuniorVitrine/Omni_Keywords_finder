import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.discord import DiscordColetor
import asyncio
import sys
from typing import Dict, List, Optional, Any

@pytest.fixture
def mock_logger():
    """Fixture que fornece um mock do logger."""
    with patch("infrastructure.coleta.base.logger") as mock:
        yield mock

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_resposta_valida():
    coletor = DiscordColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[{"content": "#hashtag <#1234> palavra1", "channel_id": "1234", "author": {"id": "a"}}])), \
         patch.object(coletor, '_obter_canal', AsyncMock(return_value={"name": "canal1"})):
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "hashtag" in sugestoes
        assert "canal1" in sugestoes
        assert "palavra1" in sugestoes
        cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_com_cache():
    coletor = DiscordColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    sugestoes = await coletor.extrair_sugestoes("input")
    assert "cache1" in sugestoes
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_erro(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(side_effect=Exception("erro"))):
        sugestoes = await coletor.extrair_sugestoes("input")
        mock_logger.error.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_resposta_valida():
    coletor = DiscordColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[{"channel_id": "1234", "author": {"id": "a"}, "content": "msg", "reactions": [], "timestamp": "1680000000"}])), \
         patch.object(coletor, '_obter_canal', AsyncMock(return_value={"name": "canal1"})), \
         patch.object(coletor, '_analisar_tendencias', AsyncMock(return_value={})):
        metricas = await coletor.extrair_metricas_especificas("input")
        assert "total_mensagens" in metricas
        assert "total_canais" in metricas
        cache_mock.set.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_com_cache():
    coletor = DiscordColetor()
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value={"total_mensagens": 10})
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    metricas = await coletor.extrair_metricas_especificas("input")
    assert metricas["total_mensagens"] == 10
    cache_mock.set.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_erro(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(side_effect=Exception("erro"))):
        metricas = await coletor.extrair_metricas_especificas("input")
        mock_logger.error.assert_called()

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_valido():
    coletor = DiscordColetor()
    resultado = await coletor.validar_termo_especifico("termo valido")
    assert resultado is True

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_longo():
    coletor = DiscordColetor()
    resultado = await coletor.validar_termo_especifico("t" * 101)
    assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_validar_termo_especifico_invalido_logs(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    resultado = await coletor.validar_termo_especifico("t" * 101)
    mock_logger.error.assert_called()
    assert resultado is False

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_concorrente():
    coletor = DiscordColetor()
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[{"content": "#hashtag palavra1", "channel_id": "1234", "author": {"id": "a"}}])), \
         patch.object(coletor, '_obter_canal', AsyncMock(return_value={"name": "canal1"})):
        results = await asyncio.gather(
            coletor.extrair_sugestoes("input1"),
            coletor.extrair_sugestoes("input2"),
            coletor.extrair_sugestoes("input3")
        )
        assert all(isinstance(r, list) for r in results)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_log_sucesso(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[{"content": "#hashtag <#1234> palavra1", "channel_id": "1234", "author": {"id": "a"}}])), \
         patch.object(coletor, '_obter_canal', AsyncMock(return_value={"name": "canal1"})):
        sugestoes = await coletor.extrair_sugestoes("input")
        mock_logger.info.assert_called()
        assert "hashtag" in sugestoes
        assert "canal1" in sugestoes
        assert "palavra1" in sugestoes

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_log_sucesso(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[{"channel_id": "1234", "author": {"id": "a"}, "content": "msg", "reactions": [], "timestamp": "1680000000"}])), \
         patch.object(coletor, '_obter_canal', AsyncMock(return_value={"name": "canal1"})), \
         patch.object(coletor, '_analisar_tendencias', AsyncMock(return_value={})):
        metricas = await coletor.extrair_metricas_especificas("input")
        mock_logger.info.assert_called()
        assert "total_mensagens" in metricas
        assert "total_canais" in metricas

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_obter_canal_erro(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[{"content": "#hashtag <#1234>", "channel_id": "1234", "author": {"id": "a"}}])), \
         patch.object(coletor, '_obter_canal', AsyncMock(side_effect=Exception("erro canal"))):
        sugestoes = await coletor.extrair_sugestoes("input")
        mock_logger.error.assert_not_called()  # erro é tratado silenciosamente
        assert "hashtag" in sugestoes

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_metricas_especificas_analisar_tendencias_erro(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[{"channel_id": "1234", "author": {"id": "a"}, "content": "msg", "reactions": [], "timestamp": "1680000000"}])), \
         patch.object(coletor, '_obter_canal', AsyncMock(return_value={"name": "canal1"})), \
         patch.object(coletor, '_analisar_tendencias', AsyncMock(side_effect=Exception("erro tendencias"))):
        metricas = await coletor.extrair_metricas_especificas("input")
        mock_logger.error.assert_called()
        assert metricas["total_mensagens"] == 1

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_servidores_vazio(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[])):
        sugestoes = await coletor.extrair_sugestoes("input")
        mock_logger.info.assert_called()
        assert sugestoes == []

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_extrair_sugestoes_mensagens_vazia(mock_logger):
    coletor = DiscordColetor(logger_=mock_logger)
    cache_mock = MagicMock()
    cache_mock.get = AsyncMock(return_value=None)
    cache_mock.set = AsyncMock()
    coletor.cache = cache_mock
    with patch.object(coletor, '_listar_servidores', AsyncMock(return_value=[{"id": "1"}])), \
         patch.object(coletor, '_buscar_mensagens', AsyncMock(return_value=[])):
        sugestoes = await coletor.extrair_sugestoes("input")
        mock_logger.info.assert_called()
        assert sugestoes == [] 