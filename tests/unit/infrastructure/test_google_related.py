#!/usr/bin/env python3
"""
Testes Unitários - Google Related
================================

Tracing ID: TEST_GOOGLE_RELATED_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/google_related.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 3.2
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any, Optional
from datetime import datetime

# Importar classes e funções reais do sistema
from infrastructure.coleta.google_related import GoogleRelatedColetor
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.utils.normalizador_central import NormalizadorCentral
from infrastructure.processamento.validador_keywords import ValidadorKeywords


class TestGoogleRelatedColetor:
    """Testes para classe GoogleRelatedColetor."""
    
    @pytest.fixture
    def mock_cache(self):
        """Fixture para cache mockado."""
        return Mock(spec=CacheDistribuido)
    
    @pytest.fixture
    def mock_logger(self):
        """Fixture para logger mockado."""
        return Mock()
    
    @pytest.fixture
    def mock_session(self):
        """Fixture para sessão HTTP mockada."""
        return Mock(spec=aiohttp.ClientSession)
    
    @pytest.fixture
    def coletor(self, mock_cache, mock_logger, mock_session):
        """Fixture para GoogleRelatedColetor."""
        with patch('infrastructure.coleta.google_related.CacheDistribuido'), \
             patch('infrastructure.coleta.google_related.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_related.NormalizadorCentral'):
            return GoogleRelatedColetor(
                cache=mock_cache,
                logger_=mock_logger,
                session=mock_session
            )
    
    def test_google_related_coletor_initialization(self, mock_cache, mock_logger):
        """Testa inicialização do GoogleRelatedColetor."""
        with patch('infrastructure.coleta.google_related.CacheDistribuido'), \
             patch('infrastructure.coleta.google_related.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_related.NormalizadorCentral'):
            
            coletor = GoogleRelatedColetor(
                cache=mock_cache,
                logger_=mock_logger
            )
            
            assert coletor.nome == "google_related"
            assert coletor.base_url == "https://www.google.com/search"
            assert "User-Agent" in coletor.headers
            assert "Accept-Language" in coletor.headers
            assert coletor.cache == mock_cache
            assert coletor.logger == mock_logger
            assert coletor.normalizador is not None
            assert coletor._session_lock is not None
    
    @pytest.mark.asyncio
    async def test_context_manager_enter(self, coletor):
        """Testa gerenciamento de contexto - entrada."""
        # Mock session fechada
        coletor.session = None
        
        async with coletor as ctx_coletor:
            assert ctx_coletor == coletor
            assert coletor.session is not None
    
    @pytest.mark.asyncio
    async def test_context_manager_exit(self, coletor):
        """Testa gerenciamento de contexto - saída."""
        # Mock session aberta
        coletor.session = Mock()
        coletor.session.closed = False
        coletor.session.close = AsyncMock()
        
        async with coletor:
            pass
        
        coletor.session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session_new(self, coletor):
        """Testa obtenção de nova sessão."""
        coletor.session = None
        
        session = await coletor._get_session()
        
        assert session is not None
        assert coletor.session == session
    
    @pytest.mark.asyncio
    async def test_get_session_existing(self, coletor):
        """Testa obtenção de sessão existente."""
        existing_session = Mock()
        existing_session.closed = False
        coletor.session = existing_session
        
        session = await coletor._get_session()
        
        assert session == existing_session
    
    @pytest.mark.asyncio
    async def test_get_session_recreate_closed(self, coletor):
        """Testa recriação de sessão fechada."""
        closed_session = Mock()
        closed_session.closed = True
        coletor.session = closed_session
        
        session = await coletor._get_session()
        
        assert session is not None
        assert session != closed_session
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_cache_hit(self, coletor):
        """Testa extração de sugestões com cache hit."""
        cached_suggestions = ["marketing digital", "marketing online", "marketing na internet"]
        coletor.cache.get = AsyncMock(return_value=cached_suggestions)
        
        result = await coletor.extrair_sugestoes("marketing")
        
        assert result == cached_suggestions
        coletor.cache.get.assert_called_once_with("sugestoes:marketing")
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_cache_invalid_format(self, coletor):
        """Testa extração de sugestões com cache em formato inválido."""
        coletor.cache.get = AsyncMock(return_value="invalid_format")
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={})
            mock_response.text = AsyncMock(return_value="<html></html>")
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes("marketing")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_json_success(self, coletor):
        """Testa extração de sugestões via JSON com sucesso."""
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        json_response = {
            "suggestions": [
                {"value": "marketing digital"},
                {"value": "marketing online"},
                "marketing na internet"
            ]
        }
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=json_response)
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes("marketing")
            
            expected_suggestions = ["marketing digital", "marketing online", "marketing na internet"]
            assert result == expected_suggestions
            coletor.cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_html_fallback(self, coletor):
        """Testa fallback para parsing HTML."""
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        html_content = """
        <html>
            <div class="BNeawe">marketing digital</div>
            <div class="BNeawe">marketing online</div>
            <div class="BNeawe">marketing na internet</div>
        </html>
        """
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session, \
             patch('bs4.BeautifulSoup') as mock_soup:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(side_effect=Exception("Not JSON"))
            mock_response.text = AsyncMock(return_value=html_content)
            
            # Mock BeautifulSoup
            mock_div1 = Mock()
            mock_div1.get_text.return_value = "marketing digital"
            mock_div2 = Mock()
            mock_div2.get_text.return_value = "marketing online"
            mock_div3 = Mock()
            mock_div3.get_text.return_value = "marketing na internet"
            
            mock_soup_instance = Mock()
            mock_soup_instance.find_all.return_value = [mock_div1, mock_div2, mock_div3]
            mock_soup.return_value = mock_soup_instance
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes("marketing")
            
            expected_suggestions = ["marketing digital", "marketing online", "marketing na internet"]
            assert result == expected_suggestions
            coletor.cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_http_error(self, coletor):
        """Testa tratamento de erro HTTP."""
        coletor.cache.get = AsyncMock(return_value=None)
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 404
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes("marketing")
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_exception(self, coletor):
        """Testa tratamento de exceção geral."""
        coletor.cache.get = AsyncMock(side_effect=Exception("Cache error"))
        
        result = await coletor.extrair_sugestoes("marketing")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_cache_hit(self, coletor):
        """Testa extração de métricas com cache hit."""
        cached_metrics = {
            "total_resultados": 1000000,
            "ads_count": 5,
            "volume": 1000,
            "concorrencia": 0.5,
            "tendencia": 0.1,
            "intencao": IntencaoBusca.INFORMACIONAL
        }
        coletor.cache.get = AsyncMock(return_value=cached_metrics)
        
        result = await coletor.extrair_metricas_especificas("marketing digital")
        
        assert result == cached_metrics
        coletor.cache.get.assert_called_once_with("metricas:marketing digital")
    
    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_success(self, coletor):
        """Testa extração de métricas com sucesso."""
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        html_content = """
        <html>
            <div id="result-stats">Aproximadamente 1.500.000 resultados</div>
            <div class="ads">Ad 1</div>
            <div class="ads">Ad 2</div>
        </html>
        """
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session, \
             patch('bs4.BeautifulSoup') as mock_soup, \
             patch.object(coletor.analisador, 'calcular_tendencia', return_value=0.2):
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=html_content)
            
            # Mock BeautifulSoup
            mock_stats_div = Mock()
            mock_stats_div.get_text.return_value = "Aproximadamente 1.500.000 resultados"
            
            mock_ads_div1 = Mock()
            mock_ads_div2 = Mock()
            
            mock_soup_instance = Mock()
            mock_soup_instance.find.return_value = mock_stats_div
            mock_soup_instance.find_all.return_value = [mock_ads_div1, mock_ads_div2]
            mock_soup.return_value = mock_soup_instance
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_metricas_especificas("marketing digital")
            
            assert result["total_resultados"] == 1500000
            assert result["ads_count"] == 2
            assert result["volume"] == 1500
            assert result["concorrencia"] == 0.2
            assert result["tendencia"] == 0.2
            assert result["intencao"] == IntencaoBusca.INFORMACIONAL
            coletor.cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_http_error(self, coletor):
        """Testa tratamento de erro HTTP em métricas."""
        coletor.cache.get = AsyncMock(return_value=None)
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 500
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_metricas_especificas("marketing digital")
            
            expected_default = {
                "total_resultados": 0,
                "ads_count": 0,
                "volume": 0,
                "concorrencia": 0.0,
                "tendencia": 0.0,
                "intencao": IntencaoBusca.NAVEGACIONAL
            }
            assert result == expected_default
    
    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_exception(self, coletor):
        """Testa tratamento de exceção em métricas."""
        coletor.cache.get = AsyncMock(side_effect=Exception("Cache error"))
        
        result = await coletor.extrair_metricas_especificas("marketing digital")
        
        expected_default = {
            "total_resultados": 0,
            "ads_count": 0,
            "volume": 0,
            "concorrencia": 0.0,
            "tendencia": 0.0,
            "intencao": IntencaoBusca.NAVEGACIONAL
        }
        assert result == expected_default
    
    @pytest.mark.asyncio
    async def test_coletar_keywords_success(self, coletor):
        """Testa coleta de keywords com sucesso."""
        # Mock validação de termo
        coletor.validar_termo = AsyncMock(return_value=True)
        
        # Mock extração de sugestões
        sugestoes = [
            "marketing digital para pequenas empresas",
            "estratégias de marketing digital 2024",
            "curso de marketing digital online"
        ]
        coletor.extrair_sugestoes = AsyncMock(return_value=sugestoes)
        
        # Mock extração de métricas
        metricas = {
            "volume": 500,
            "cpc": 2.50,
            "concorrencia": 0.3,
            "intencao": IntencaoBusca.INFORMACIONAL
        }
        coletor.extrair_metricas_especificas = AsyncMock(return_value=metricas)
        
        result = await coletor.coletar_keywords("marketing digital", limite=10)
        
        assert len(result) == 3
        for keyword in result:
            assert isinstance(keyword, Keyword)
            assert keyword.termo in sugestoes
            assert keyword.volume_busca == 500
            assert keyword.cpc == 2.50
            assert keyword.concorrencia == 0.3
            assert keyword.intencao == IntencaoBusca.INFORMACIONAL
    
    @pytest.mark.asyncio
    async def test_coletar_keywords_invalid_term(self, coletor):
        """Testa coleta de keywords com termo inválido."""
        coletor.validar_termo = AsyncMock(return_value=False)
        
        result = await coletor.coletar_keywords("", limite=10)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_coletar_keywords_exception(self, coletor):
        """Testa tratamento de exceção na coleta de keywords."""
        coletor.validar_termo = AsyncMock(return_value=True)
        coletor.extrair_sugestoes = AsyncMock(side_effect=Exception("API Error"))
        
        result = await coletor.coletar_keywords("marketing digital", limite=10)
        
        assert result == []
    
    def test_determinar_intencao_informacional(self, coletor):
        """Testa determinação de intenção informacional."""
        result = coletor._determinar_intencao("como fazer marketing digital", 1000000, 2)
        assert result == IntencaoBusca.INFORMACIONAL
    
    def test_determinar_intencao_transacional(self, coletor):
        """Testa determinação de intenção transacional."""
        result = coletor._determinar_intencao("comprar curso marketing digital", 500000, 8)
        assert result == IntencaoBusca.TRANSACIONAL
    
    def test_determinar_intencao_navegacional(self, coletor):
        """Testa determinação de intenção navegacional."""
        result = coletor._determinar_intencao("login marketing digital", 100000, 1)
        assert result == IntencaoBusca.NAVEGACIONAL
    
    def test_determinar_intencao_by_ads_count(self, coletor):
        """Testa determinação de intenção baseada no número de anúncios."""
        result = coletor._determinar_intencao("marketing digital", 100000, 6)
        assert result == IntencaoBusca.TRANSACIONAL
    
    def test_determinar_intencao_by_total_results(self, coletor):
        """Testa determinação de intenção baseada no total de resultados."""
        result = coletor._determinar_intencao("marketing digital", 2000000, 2)
        assert result == IntencaoBusca.INFORMACIONAL
    
    @pytest.mark.asyncio
    async def test_validar_termo_especifico_valid(self, coletor):
        """Testa validação de termo específico válido."""
        with patch('infrastructure.coleta.google_related.ValidadorKeywords') as mock_validador_class:
            mock_validador = Mock()
            mock_validador.validar_keyword.return_value = (True, "Válido")
            mock_validador_class.return_value = mock_validador
            
            result = await coletor.validar_termo_especifico("marketing digital")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_validar_termo_especifico_invalid_size(self, coletor):
        """Testa validação de termo específico com tamanho inválido."""
        long_term = "a" * 101  # Mais de 100 caracteres
        
        result = await coletor.validar_termo_especifico(long_term)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validar_termo_especifico_empty(self, coletor):
        """Testa validação de termo específico vazio."""
        result = await coletor.validar_termo_especifico("")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validar_termo_especifico_rejected(self, coletor):
        """Testa validação de termo específico rejeitado pelo validador."""
        with patch('infrastructure.coleta.google_related.ValidadorKeywords') as mock_validador_class:
            mock_validador = Mock()
            mock_validador.validar_keyword.return_value = (False, "Termo proibido")
            mock_validador_class.return_value = mock_validador
            
            result = await coletor.validar_termo_especifico("termo proibido")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_classificar_intencao(self, coletor):
        """Testa classificação de intenção para lista de keywords."""
        keywords = [
            "como fazer marketing digital",
            "comprar curso marketing",
            "melhor plataforma marketing",
            "marketing digital"
        ]
        
        result = await coletor.classificar_intencao(keywords)
        
        expected_intencoes = [
            IntencaoBusca.INFORMACIONAL,  # "como"
            IntencaoBusca.TRANSACIONAL,   # "comprar"
            IntencaoBusca.COMPARACAO,     # "melhor"
            IntencaoBusca.NAVEGACIONAL    # default
        ]
        
        assert result == expected_intencoes
    
    @pytest.mark.asyncio
    async def test_coletar_metricas_success(self, coletor):
        """Testa coleta de métricas para lista de keywords."""
        keywords = ["marketing digital", "seo", "ads"]
        
        metricas_mock = {
            "total_resultados": 1000000,
            "ads_count": 5,
            "volume": 1000,
            "concorrencia": 0.5,
            "tendencia": 0.1,
            "intencao": IntencaoBusca.INFORMACIONAL
        }
        
        coletor.extrair_metricas_especificas = AsyncMock(return_value=metricas_mock)
        
        result = await coletor.coletar_metricas(keywords)
        
        assert len(result) == 3
        for metricas in result:
            assert metricas == metricas_mock
        assert coletor.extrair_metricas_especificas.call_count == 3
    
    @pytest.mark.asyncio
    async def test_coletar_metricas_with_error(self, coletor):
        """Testa coleta de métricas com erro em um termo."""
        keywords = ["marketing digital", "seo", "ads"]
        
        # Mock sucesso para primeiro termo, erro para segundo, sucesso para terceiro
        coletor.extrair_metricas_especificas = AsyncMock(side_effect=[
            {
                "total_resultados": 1000000,
                "ads_count": 5,
                "volume": 1000,
                "concorrencia": 0.5,
                "tendencia": 0.1,
                "intencao": IntencaoBusca.INFORMACIONAL
            },
            Exception("API Error"),
            {
                "total_resultados": 500000,
                "ads_count": 3,
                "volume": 500,
                "concorrencia": 0.3,
                "tendencia": 0.05,
                "intencao": IntencaoBusca.TRANSACIONAL
            }
        ])
        
        result = await coletor.coletar_metricas(keywords)
        
        assert len(result) == 3
        
        # Primeiro termo - sucesso
        assert result[0]["total_resultados"] == 1000000
        
        # Segundo termo - erro (métricas padrão)
        assert result[1]["total_resultados"] == 0
        assert result[1]["ads_count"] == 0
        assert result[1]["concorrencia"] == 0.5
        assert result[1]["intencao"] == IntencaoBusca.NAVEGACIONAL
        
        # Terceiro termo - sucesso
        assert result[2]["total_resultados"] == 500000


class TestGoogleRelatedColetorIntegration:
    """Testes de integração para GoogleRelatedColetor."""
    
    @pytest.fixture
    def mock_cache(self):
        """Fixture para cache mockado."""
        return Mock(spec=CacheDistribuido)
    
    @pytest.fixture
    def coletor(self, mock_cache):
        """Fixture para coletor com mocks."""
        with patch('infrastructure.coleta.google_related.CacheDistribuido'), \
             patch('infrastructure.coleta.google_related.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_related.NormalizadorCentral'):
            return GoogleRelatedColetor(cache=mock_cache)
    
    @pytest.mark.asyncio
    async def test_full_workflow_suggestions_and_metrics(self, coletor):
        """Testa workflow completo de sugestões e métricas."""
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock validação
        coletor.validar_termo = AsyncMock(return_value=True)
        
        # Mock sugestões
        sugestoes = ["marketing digital para empresas", "estratégias marketing digital"]
        coletor.extrair_sugestoes = AsyncMock(return_value=sugestoes)
        
        # Mock métricas
        metricas = {
            "volume": 800,
            "cpc": 3.00,
            "concorrencia": 0.4,
            "intencao": IntencaoBusca.INFORMACIONAL
        }
        coletor.extrair_metricas_especificas = AsyncMock(return_value=metricas)
        
        result = await coletor.coletar_keywords("marketing digital", limite=5)
        
        assert len(result) == 2
        for keyword in result:
            assert isinstance(keyword, Keyword)
            assert keyword.termo in sugestoes
            assert keyword.volume_busca == 800
            assert keyword.cpc == 3.00
            assert keyword.concorrencia == 0.4
    
    @pytest.mark.asyncio
    async def test_session_management_integration(self, coletor):
        """Testa gerenciamento de sessão em workflow completo."""
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock sessão
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"suggestions": [{"value": "test"}]})
        
        mock_session.get = AsyncMock(return_value=mock_response)
        coletor._get_session = AsyncMock(return_value=mock_session)
        
        result = await coletor.extrair_sugestoes("test")
        
        assert result == ["test"]
        coletor._get_session.assert_called_once()


class TestGoogleRelatedColetorEdgeCases:
    """Testes para casos edge do GoogleRelatedColetor."""
    
    @pytest.fixture
    def mock_cache(self):
        """Fixture para cache mockado."""
        return Mock(spec=CacheDistribuido)
    
    @pytest.fixture
    def coletor(self, mock_cache):
        """Fixture para coletor."""
        with patch('infrastructure.coleta.google_related.CacheDistribuido'), \
             patch('infrastructure.coleta.google_related.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_related.NormalizadorCentral'):
            return GoogleRelatedColetor(cache=mock_cache)
    
    @pytest.mark.asyncio
    async def test_empty_term_suggestions(self, coletor):
        """Testa extração de sugestões com termo vazio."""
        result = await coletor.extrair_sugestoes("")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_empty_term_metrics(self, coletor):
        """Testa extração de métricas com termo vazio."""
        result = await coletor.extrair_metricas_especificas("")
        
        expected_default = {
            "total_resultados": 0,
            "ads_count": 0,
            "volume": 0,
            "concorrencia": 0.0,
            "tendencia": 0.0,
            "intencao": IntencaoBusca.NAVEGACIONAL
        }
        assert result == expected_default
    
    @pytest.mark.asyncio
    async def test_special_characters_term(self, coletor):
        """Testa extração com caracteres especiais."""
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"suggestions": []})
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes("marketing@digital#2024")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_very_long_term(self, coletor):
        """Testa extração com termo muito longo."""
        long_term = "a" * 200
        
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"suggestions": []})
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes(long_term)
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_unicode_term(self, coletor):
        """Testa extração com termo Unicode."""
        unicode_term = "marketing digital com acentos: ação, coração"
        
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"suggestions": []})
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes(unicode_term)
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_no_suggestions_found(self, coletor):
        """Testa quando nenhuma sugestão é encontrada."""
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={})
            mock_response.text = AsyncMock(return_value="<html><body></body></html>")
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            result = await coletor.extrair_sugestoes("termo sem sugestões")
            
            assert result == []
            coletor.cache.set.assert_called_once()


class TestGoogleRelatedColetorPerformance:
    """Testes de performance para GoogleRelatedColetor."""
    
    @pytest.fixture
    def mock_cache(self):
        """Fixture para cache mockado."""
        return Mock(spec=CacheDistribuido)
    
    @pytest.fixture
    def coletor(self, mock_cache):
        """Fixture para coletor."""
        with patch('infrastructure.coleta.google_related.CacheDistribuido'), \
             patch('infrastructure.coleta.google_related.AnalisadorTendencias'), \
             patch('infrastructure.coleta.google_related.NormalizadorCentral'):
            return GoogleRelatedColetor(cache=mock_cache)
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, coletor):
        """Testa performance do cache."""
        import time
        
        # Mock cache com dados
        cached_data = ["sugestao1", "sugestao2", "sugestao3"]
        coletor.cache.get = AsyncMock(return_value=cached_data)
        
        start_time = time.time()
        result = await coletor.extrair_sugestoes("test")
        cache_time = time.time() - start_time
        
        # Cache deve ser muito rápido (< 100ms)
        assert cache_time < 0.1
        assert result == cached_data
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, coletor):
        """Testa requisições concorrentes."""
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        with patch.object(coletor, '_get_session') as mock_get_session, \
             patch('aiohttp.ClientSession') as mock_client_session:
            
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"suggestions": [{"value": "test"}]})
            
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_get_session.return_value = mock_session
            
            # Executar múltiplas requisições concorrentes
            tasks = [
                coletor.extrair_sugestoes("termo1"),
                coletor.extrair_sugestoes("termo2"),
                coletor.extrair_sugestoes("termo3")
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            for result in results:
                assert result == ["test"]


if __name__ == "__main__":
    pytest.main([__file__]) 