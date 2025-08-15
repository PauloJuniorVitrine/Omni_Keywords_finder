import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from infrastructure.coleta.gsc import GSCColetor
from domain.models import IntencaoBusca
import asyncio
from typing import Dict, List, Optional, Any

@pytest.mark.asyncio
async def test_extrair_sugestoes_resposta_valida():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletor.sites = {"site1": {}}
        mock_service = MagicMock()
        mock_query = MagicMock()
        mock_query.execute = MagicMock(return_value={"rows": [{"keys": ["palavra chave para gsc"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 2.0}]})
        mock_service.searchanalytics.return_value.query.return_value = mock_query
        coletor.service = mock_service
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "palavra chave para gsc" in sugestoes
        cache_mock.set.assert_called()

@pytest.mark.asyncio
async def test_extrair_sugestoes_com_cache():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=["cache1", "cache2"])
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        sugestoes = await coletor.extrair_sugestoes("input")
        assert "cache1" in sugestoes
        cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_sugestoes_erro_api():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletor.sites = {"site1": {}}
        mock_service = MagicMock()
        mock_query = MagicMock()
        mock_query.execute = MagicMock(side_effect=Exception("erro"))
        mock_service.searchanalytics.return_value.query.return_value = mock_query
        coletor.service = mock_service
        sugestoes = await coletor.extrair_sugestoes("input")
        assert sugestoes == []

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_resposta_valida():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletor.sites = {"site1": {}}
        mock_service = MagicMock()
        mock_query = MagicMock()
        mock_query.execute = MagicMock(return_value={"rows": [{"keys": ["palavra chave para gsc"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 2.0}]})
        mock_service.searchanalytics.return_value.query.return_value = mock_query
        coletor.service = mock_service
        metricas = await coletor.extrair_metricas_especificas("input")
        assert "impressoes" in metricas and "cliques" in metricas
        cache_mock.set.assert_called()

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_com_cache():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value={"impressoes": 100, "cliques": 10})
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["impressoes"] == 100
        assert metricas["cliques"] == 10
        cache_mock.set.assert_not_called()

@pytest.mark.asyncio
async def test_extrair_metricas_especificas_erro():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        cache_mock = MagicMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock()
        coletor.cache = cache_mock
        coletor.sites = {"site1": {}}
        mock_service = MagicMock()
        mock_query = MagicMock()
        mock_query.execute = MagicMock(side_effect=Exception("erro"))
        mock_service.searchanalytics.return_value.query.return_value = mock_query
        coletor.service = mock_service
        metricas = await coletor.extrair_metricas_especificas("input")
        assert metricas["impressoes"] == 0
        assert metricas["cliques"] == 0

@pytest.mark.asyncio
async def test_validar_termo_especifico_valido():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        resultado = await coletor.validar_termo_especifico("palavra chave para gsc")
        assert resultado is True

@pytest.mark.asyncio
async def test_validar_termo_especifico_vazio():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}), \
         patch.object(GSCColetor, 'validar_termo_especifico', return_value=False):
        coletor = GSCColetor()
        resultado = await coletor.validar_termo_especifico("")
        assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_longo():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch.object(GSCColetor, 'service', create=True), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}), \
         patch.object(GSCColetor, 'validar_termo_especifico', return_value=False):
        coletor = GSCColetor()
        resultado = await coletor.validar_termo_especifico("t" * 101)
        assert resultado is False

@pytest.mark.asyncio
async def test_validar_termo_especifico_invalido_logs():
    with patch.object(GSCColetor, '_carregar_sites', return_value={"site1": {}}), \
         patch("infrastructure.coleta.gsc.Credentials.from_authorized_user_info", return_value=MagicMock()), \
         patch("infrastructure.coleta.gsc.GSC_CONFIG", {"credentials": {}}):
        coletor = GSCColetor()
        with patch.object(coletor, 'registrar_erro') as erro_mock:
            resultado = await coletor.validar_termo_especifico("t" * 201)
            erro_mock.assert_called()
            assert resultado is False 