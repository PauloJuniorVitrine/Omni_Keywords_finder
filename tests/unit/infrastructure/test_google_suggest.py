#!/usr/bin/env python3
"""
Testes Unitários - Google Suggest
================================

Tracing ID: TEST_GOOGLE_SUGGEST_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/google_suggest.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 3.3
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List
from datetime import datetime

from infrastructure.coleta.google_suggest import GoogleSuggestColetor
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.utils.normalizador_central import NormalizadorCentral
from infrastructure.processamento.validador_keywords import ValidadorKeywords


class TestGoogleSuggestColetor:
    @pytest.fixture
    def mock_cache(self):
        return Mock(spec=CacheDistribuido)

    @pytest.fixture
    def mock_logger(self):
        return Mock()

    @pytest.fixture
    def mock_session(self):
        return Mock(spec=aiohttp.ClientSession)

    @pytest.fixture
    def coletor(self, mock_cache, mock_logger, mock_session):
        with patch('infrastructure.coleta.google_suggest.CacheDistribuido'), \
             patch('infrastructure.coleta.google_suggest.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_suggest.NormalizadorCentral'):
            return GoogleSuggestColetor(
                cache=mock_cache,
                logger_=mock_logger,
                session=mock_session
            )

    def test_inicializacao(self, mock_cache, mock_logger):
        with patch('infrastructure.coleta.google_suggest.CacheDistribuido'), \
             patch('infrastructure.coleta.google_suggest.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_suggest.NormalizadorCentral'):
            coletor = GoogleSuggestColetor(cache=mock_cache, logger_=mock_logger)
            assert coletor.nome == "google_suggest"
            assert coletor.base_url.startswith("https://suggestqueries.google.com")
            assert coletor.cache == mock_cache
            assert coletor.logger == mock_logger
            assert coletor.normalizador is not None

    @pytest.mark.asyncio
    async def test_context_manager(self, coletor):
        coletor.session = None
        async with coletor as ctx:
            assert ctx == coletor
            assert coletor.session is not None

    @pytest.mark.asyncio
    async def test_extrair_sugestoes_cache_hit(self, coletor):
        cached = ["marketing digital", "seo", "ads"]
        coletor.cache.get = AsyncMock(return_value=cached)
        result = await coletor.extrair_sugestoes("marketing digital")
        assert result == cached

    @pytest.mark.asyncio
    async def test_extrair_sugestoes_json_success(self, coletor):
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        json_response = ["marketing digital", ["marketing digital avançado", "seo avançado"]]
        with patch.object(coletor, '_get_session') as mock_get_session:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=json_response)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            result = await coletor.extrair_sugestoes("marketing digital")
            assert result == ["marketing digital avançado", "seo avançado"]
            coletor.cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_extrair_sugestoes_http_error(self, coletor):
        coletor.cache.get = AsyncMock(return_value=None)
        with patch.object(coletor, '_get_session') as mock_get_session:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 500
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            result = await coletor.extrair_sugestoes("marketing digital")
            assert result == []

    @pytest.mark.asyncio
    async def test_extrair_sugestoes_exception(self, coletor):
        coletor.cache.get = AsyncMock(side_effect=Exception("Cache error"))
        result = await coletor.extrair_sugestoes("marketing digital")
        assert result == []

    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_cache_hit(self, coletor):
        cached = {"total_sugestoes": 2, "total_variantes": 1, "volume": 100, "concorrencia": 0.2}
        coletor.cache.get = AsyncMock(return_value=cached)
        result = await coletor.extrair_metricas_especificas("marketing digital")
        assert result == cached

    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_success(self, coletor):
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        coletor.extrair_sugestoes = AsyncMock(side_effect=[["marketing digital"], ["como marketing digital"]]*4)
        coletor.analisador = Mock()
        coletor.analisador.calcular_tendencia.return_value = 0.3
        coletor.analisador.registrar_acesso = Mock()
        result = await coletor.extrair_metricas_especificas("marketing digital")
        assert "total_sugestoes" in result
        assert "sazonalidade" in result
        assert "intencoes" in result
        assert "volume" in result
        assert "concorrencia" in result
        coletor.cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_coletar_keywords_success(self, coletor):
        coletor.validar_termo = AsyncMock(return_value=True)
        coletor.extrair_sugestoes = AsyncMock(return_value=["marketing digital para empresas", "estratégias de marketing digital"])
        coletor.extrair_metricas_especificas = AsyncMock(return_value={"volume": 100, "cpc": 2.0, "concorrencia": 0.3})
        result = await coletor.coletar_keywords("marketing digital", limite=10)
        assert all(isinstance(k, Keyword) for k in result)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_coletar_keywords_invalid_term(self, coletor):
        coletor.validar_termo = AsyncMock(return_value=False)
        result = await coletor.coletar_keywords("", limite=10)
        assert result == []

    @pytest.mark.asyncio
    async def test_validar_termo_especifico_valid(self, coletor):
        with patch('infrastructure.coleta.google_suggest.ValidadorKeywords') as mock_validador_class:
            mock_validador = Mock()
            mock_validador.validar_keyword.return_value = (True, "Válido")
            mock_validador_class.return_value = mock_validador
            result = await coletor.validar_termo_especifico("marketing digital")
            assert result is True

    @pytest.mark.asyncio
    async def test_validar_termo_especifico_invalid(self, coletor):
        with patch('infrastructure.coleta.google_suggest.ValidadorKeywords') as mock_validador_class:
            mock_validador = Mock()
            mock_validador.validar_keyword.return_value = (False, "Inválido")
            mock_validador_class.return_value = mock_validador
            result = await coletor.validar_termo_especifico("termo proibido")
            assert result is False

    @pytest.mark.asyncio
    async def test_classificar_intencao(self, coletor):
        keywords = [
            "como fazer marketing digital",
            "comprar curso marketing",
            "melhor plataforma marketing",
            "marketing digital"
        ]
        result = await coletor.classificar_intencao(keywords)
        assert result == [
            IntencaoBusca.INFORMACIONAL,
            IntencaoBusca.TRANSACIONAL,
            IntencaoBusca.COMPARACAO,
            IntencaoBusca.NAVEGACIONAL
        ]

    @pytest.mark.asyncio
    async def test_coletar_metricas_success(self, coletor):
        keywords = ["marketing digital", "seo"]
        coletor.extrair_metricas_especificas = AsyncMock(return_value={"volume": 100, "concorrencia": 0.2, "sazonalidade": 0.1, "tendencia": 0.3})
        result = await coletor.coletar_metricas(keywords)
        assert len(result) == 2
        for m in result:
            assert "volume" in m
            assert "concorrencia" in m

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

    @pytest.mark.asyncio
    async def test_performance_cache(self, coletor):
        import time
        cached = ["sugestao1", "sugestao2"]
        coletor.cache.get = AsyncMock(return_value=cached)
        start = time.time()
        result = await coletor.extrair_sugestoes("test")
        elapsed = time.time() - start
        assert elapsed < 0.1
        assert result == cached 