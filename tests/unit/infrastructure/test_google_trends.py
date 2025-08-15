#!/usr/bin/env python3
"""
Testes Unitários - Google Trends
===============================

Tracing ID: TEST_GOOGLE_TRENDS_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/google_trends.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 3.4
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from infrastructure.coleta.google_trends import GoogleTrendsColetor
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.utils.normalizador_central import NormalizadorCentral
from infrastructure.processamento.validador_keywords import ValidadorKeywords

class TestGoogleTrendsColetor:
    @pytest.fixture
    def mock_cache(self):
        return Mock(spec=CacheDistribuido)

    @pytest.fixture
    def mock_logger(self):
        return Mock()

    @pytest.fixture
    def coletor(self, mock_cache, mock_logger):
        with patch('infrastructure.coleta.google_trends.CacheDistribuido'), \
             patch('infrastructure.coleta.google_trends.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_trends.NormalizadorCentral'):
            return GoogleTrendsColetor(logger_=mock_logger)

    def test_inicializacao(self, mock_logger):
        with patch('infrastructure.coleta.google_trends.CacheDistribuido'), \
             patch('infrastructure.coleta.google_trends.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_trends.NormalizadorCentral'):
            coletor = GoogleTrendsColetor(logger_=mock_logger)
            assert coletor.nome == "google_trends"
            assert hasattr(coletor, 'cache')
            assert hasattr(coletor, 'analisador')
            assert hasattr(coletor, 'normalizador')

    @pytest.mark.asyncio
    async def test_extrair_sugestoes_cache_hit(self, coletor):
        coletor.cache.get = AsyncMock(return_value=["termo1", "termo2"])
        result = await coletor.extrair_sugestoes("marketing digital")
        assert result == ["termo1", "termo2"]

    @pytest.mark.asyncio
    async def test_extrair_sugestoes_api_success(self, coletor):
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        with patch.object(coletor, '_build_payload', new=AsyncMock()), \
             patch.object(coletor, '_get_client') as mock_client:
            mock_related = {"marketing digital": {"rising": {"termo1": 100}, "top": {"termo2": 200}}}
            mock_client.return_value.related_queries = mock_related
            result = await coletor.extrair_sugestoes("marketing digital")
            assert set(result) == {"termo1", "termo2"}
            coletor.cache.set.assert_any_call('queries:marketing digital', {'rising': {"termo1": 100}, 'top': {"termo2": 200}}, ttl=Mock.ANY)
            coletor.cache.set.assert_any_call('sugestoes:marketing digital', ['termo1', 'termo2'], ttl=Mock.ANY)

    @pytest.mark.asyncio
    async def test_extrair_sugestoes_api_error(self, coletor):
        coletor.cache.get = AsyncMock(return_value=None)
        with patch.object(coletor, '_build_payload', new=AsyncMock(side_effect=Exception("API error"))):
            result = await coletor.extrair_sugestoes("marketing digital")
            assert result == []

    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_cache_hit(self, coletor):
        cached = {"volume": 100, "concorrencia": 0.2, "intencao": IntencaoBusca.INFORMACIONAL}
        coletor.cache.get = AsyncMock(return_value=cached)
        result = await coletor.extrair_metricas_especificas("marketing digital")
        assert result == cached

    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_success(self, coletor):
        coletor.cache.get = AsyncMock(side_effect=[None, {'rising': {}, 'top': {}}])
        coletor.cache.set = AsyncMock()
        with patch.object(coletor, '_build_payload', new=AsyncMock()), \
             patch.object(coletor, '_get_client') as mock_client:
            mock_client.return_value.related_queries = {"termo": {"rising": {}, "top": {}}}
            coletor.analisador = Mock()
            coletor.analisador.calcular_tendencia.return_value = 0.3
            coletor.analisador.registrar_acesso = Mock()
            result = await coletor.extrair_metricas_especificas("termo")
            assert "volume" in result
            assert "concorrencia" in result
            assert "intencao" in result
            coletor.cache.set.assert_called()

    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_error(self, coletor):
        coletor.cache.get = AsyncMock(side_effect=Exception("Cache error"))
        result = await coletor.extrair_metricas_especificas("termo")
        assert result["volume"] == 0
        assert result["concorrencia"] == 0.5

    @pytest.mark.asyncio
    async def test_validar_termo_especifico_valid(self, coletor):
        with patch('infrastructure.coleta.google_trends.ValidadorKeywords') as mock_validador_class:
            mock_validador = Mock()
            mock_validador.validar_keyword.return_value = (True, "Válido")
            mock_validador_class.return_value = mock_validador
            result = await coletor.validar_termo_especifico("marketing digital avançado")
            assert result is True

    @pytest.mark.asyncio
    async def test_validar_termo_especifico_invalid(self, coletor):
        with patch('infrastructure.coleta.google_trends.ValidadorKeywords') as mock_validador_class:
            mock_validador = Mock()
            mock_validador.validar_keyword.return_value = (False, "Inválido")
            mock_validador_class.return_value = mock_validador
            result = await coletor.validar_termo_especifico("termo proibido")
            assert result is False

    @pytest.mark.asyncio
    async def test_coletar_keywords_success(self, coletor):
        coletor.validar_termo = AsyncMock(return_value=True)
        coletor.validar_termo_especifico = AsyncMock(return_value=True)
        coletor.extrair_sugestoes = AsyncMock(return_value=["marketing digital para empresas", "estratégias de marketing digital"])
        coletor.extrair_metricas_especificas = AsyncMock(return_value={"volume": 100, "cpc": 2.0, "concorrencia": 0.3, "intencao": IntencaoBusca.INFORMACIONAL, "crescimento": 10, "tendencia": 0.2})
        result = await coletor.coletar_keywords("marketing digital", limite=10)
        assert all(isinstance(k, Keyword) for k in result)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_coletar_keywords_invalid_term(self, coletor):
        coletor.validar_termo = AsyncMock(return_value=False)
        coletor.validar_termo_especifico = AsyncMock(return_value=False)
        result = await coletor.coletar_keywords("", limite=10)
        assert result == []

    @pytest.mark.asyncio
    async def test_coletar_keywords_edge_cases(self, coletor):
        coletor.validar_termo = AsyncMock(return_value=True)
        coletor.validar_termo_especifico = AsyncMock(return_value=True)
        coletor.extrair_sugestoes = AsyncMock(return_value=[])
        result = await coletor.coletar_keywords("marketing digital", limite=10)
        assert result == []

    @pytest.mark.asyncio
    async def test_coletar_trends_api_success(self, coletor):
        coletor.cache.get = AsyncMock(return_value=None)
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"default": {"trendingSearchesDays": [{"trendingSearches": [{"title": {"query": "trend1"}}]}]}, "suggestions": [{"value": "trend2"}]})
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_class.return_value = mock_session
            result = await coletor.coletar("marketing digital")
            assert "trend1" in result and "trend2" in result

    @pytest.mark.asyncio
    async def test_coletar_trends_api_error(self, coletor):
        coletor.cache.get = AsyncMock(return_value=None)
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 500
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_class.return_value = mock_session
            result = await coletor.coletar("marketing digital")
            assert result == []

    @pytest.mark.asyncio
    async def test_edge_cases(self, coletor):
        # Termo vazio
        result = await coletor.extrair_sugestoes("")
        assert result == []
        # Termo longo
        result = await coletor.extrair_sugestoes("a"*200)
        assert result == []
        # Unicode
        result = await coletor.extrair_sugestoes("ação coração")
        assert isinstance(result, list) 