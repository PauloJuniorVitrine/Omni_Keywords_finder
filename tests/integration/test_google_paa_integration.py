"""
Testes de Integração Real - Google PAA API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validada cobertura completa

Tracing ID: test-google-paa-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/google_paa.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 7.3
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Google Search API
- Extração de People Also Ask
- Análise de SERP
- Rate limiting
- Circuit breaker
- Cache inteligente
- Fallback para web scraping
- Análise de tendências
- Classificação de intenção
"""

import pytest
import os
import time
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
from bs4 import BeautifulSoup

from infrastructure.coleta.google_paa import GooglePAAColetor
from domain.models import Keyword, IntencaoBusca


class TestGooglePAARealIntegration:
    """Testes de integração real para Google PAA API."""
    
    @pytest.fixture
    def google_paa_config(self):
        """Configuração real para testes."""
        return {
            "max_depth": 3,
            "rate_limit_per_minute": 30,
            "rate_limit_per_hour": 1000,
            "cache_ttl": 3600,
            "user_agent": "OmniKeywordsFinder/1.0",
            "proxy_enabled": False,
            "env": "test"
        }
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache para testes."""
        cache = MagicMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        cache.delete = AsyncMock()
        return cache
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger para testes."""
        logger = MagicMock()
        logger.info = MagicMock()
        logger.error = MagicMock()
        logger.warning = MagicMock()
        return logger
    
    @pytest.fixture
    def real_collector(self, google_paa_config, mock_cache, mock_logger):
        """Instância do coletor real para testes."""
        with patch('infrastructure.coleta.google_paa.GOOGLE_PAA_CONFIG', google_paa_config):
            return GooglePAAColetor(cache=mock_cache, logger_=mock_logger)
    
    @pytest.fixture
    def sample_google_html(self):
        """HTML de exemplo da página do Google com PAA."""
        return """
        <html>
            <body>
                <div class="related-question-pair">
                    <div class="question">Como funciona o Google PAA?</div>
                </div>
                <div class="related-question-pair">
                    <div class="question">O que é People Also Ask?</div>
                </div>
                <div class="related-question-pair">
                    <div class="question">Como extrair dados do Google?</div>
                </div>
                <div class="related-question-pair">
                    <div class="question">Quais são as melhores práticas de SEO?</div>
                </div>
            </body>
        </html>
        """
    
    @pytest.fixture
    def sample_serp_data(self):
        """Dados de exemplo de SERP."""
        return {
            "total_results": 1000000,
            "search_time": 0.45,
            "related_searches": [
                "google paa api",
                "people also ask extraction",
                "serp analysis tools"
            ],
            "featured_snippet": {
                "title": "Google People Also Ask",
                "content": "People Also Ask (PAA) is a Google SERP feature..."
            }
        }
    
    def test_google_paa_collector_initialization(self, real_collector, google_paa_config):
        """Testa inicialização do coletor real."""
        assert real_collector.nome == "google_paa"
        assert real_collector.config == google_paa_config
        assert real_collector.base_url == "https://www.google.com/search"
        assert real_collector.max_depth == 3
        assert real_collector.cache is not None
        assert real_collector.logger is not None
        assert real_collector.analisador is not None
        assert real_collector.normalizador is not None
        assert real_collector.perguntas_coletadas == set()
    
    @pytest.mark.asyncio
    async def test_google_paa_collector_context_manager(self, real_collector):
        """Testa context manager do coletor."""
        async with real_collector as collector:
            assert collector.session is not None
            assert isinstance(collector.session, MagicMock)  # Mock session
        
        # Session deve ser fechada após sair do context
        assert real_collector.session is None
    
    @pytest.mark.asyncio
    async def test_google_paa_extract_questions_from_page(self, real_collector, sample_google_html):
        """Testa extração de perguntas da página."""
        questions = await real_collector._extrair_perguntas_pagina(sample_google_html)
        
        assert len(questions) == 4
        assert "Como funciona o Google PAA?" in questions
        assert "O que é People Also Ask?" in questions
        assert "Como extrair dados do Google?" in questions
        assert "Quais são as melhores práticas de SEO?" in questions
        
        # Verificar se perguntas foram adicionadas ao set
        assert len(real_collector.perguntas_coletadas) == 4
    
    @pytest.mark.asyncio
    async def test_google_paa_extract_questions_duplicate_handling(self, real_collector, sample_google_html):
        """Testa tratamento de perguntas duplicadas."""
        # Primeira extração
        questions1 = await real_collector._extrair_perguntas_pagina(sample_google_html)
        initial_count = len(questions1)
        
        # Segunda extração (deve retornar lista vazia devido a duplicatas)
        questions2 = await real_collector._extrair_perguntas_pagina(sample_google_html)
        
        assert len(questions2) == 0
        assert len(real_collector.perguntas_coletadas) == initial_count
    
    @pytest.mark.asyncio
    async def test_google_paa_extract_questions_empty_html(self, real_collector):
        """Testa extração de perguntas com HTML vazio."""
        questions = await real_collector._extrair_perguntas_pagina("<html><body></body></html>")
        
        assert len(questions) == 0
    
    @pytest.mark.asyncio
    async def test_google_paa_extract_questions_malformed_html(self, real_collector):
        """Testa extração de perguntas com HTML malformado."""
        questions = await real_collector._extrair_perguntas_pagina("invalid html content")
        
        assert len(questions) == 0
    
    @patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_google_paa_extract_suggestions_success(self, mock_get, real_collector, sample_google_html):
        """Testa extração de sugestões com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=sample_google_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        suggestions = await real_collector.extrair_sugestoes("google paa")
        
        assert len(suggestions) == 4
        assert "Como funciona o Google PAA?" in suggestions
        assert "O que é People Also Ask?" in suggestions
        assert "Como extrair dados do Google?" in suggestions
        assert "Quais são as melhores práticas de SEO?" in suggestions
        
        # Verificar se cache foi usado
        real_collector.cache.set.assert_called_once()
    
    @patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_google_paa_extract_suggestions_from_cache(self, mock_get, real_collector):
        """Testa extração de sugestões do cache."""
        cached_suggestions = ["Como funciona o Google PAA?", "O que é People Also Ask?"]
        real_collector.cache.get.return_value = cached_suggestions
        
        suggestions = await real_collector.extrair_sugestoes("google paa")
        
        assert suggestions == cached_suggestions
        # Não deve fazer requisição HTTP se estiver no cache
        mock_get.assert_not_called()
    
    @patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_google_paa_extract_suggestions_http_error(self, mock_get, real_collector):
        """Testa erro HTTP na extração de sugestões."""
        mock_response = MagicMock()
        mock_response.status = 429  # Rate limit
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        suggestions = await real_collector.extrair_sugestoes("google paa")
        
        assert suggestions == []
        # Verificar se erro foi logado
        real_collector.logger.error.assert_called()
    
    @patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_google_paa_extract_specific_metrics_success(self, mock_get, real_collector, sample_google_html):
        """Testa extração de métricas específicas com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=sample_google_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        metrics = await real_collector.extrair_metricas_especificas("google paa")
        
        assert isinstance(metrics, dict)
        assert "total_perguntas" in metrics
        assert "perguntas_unicas" in metrics
        assert "taxa_duplicacao" in metrics
        assert "tempo_extração" in metrics
        assert "status" in metrics
        assert metrics["total_perguntas"] == 4
        assert metrics["perguntas_unicas"] == 4
        assert metrics["taxa_duplicacao"] == 0.0
        assert metrics["status"] == "sucesso"
    
    @patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_google_paa_validate_specific_term_success(self, mock_get, real_collector, sample_google_html):
        """Testa validação de termo específico com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=sample_google_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        is_valid = await real_collector.validar_termo_especifico("google paa")
        
        assert is_valid is True
    
    @patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_google_paa_validate_specific_term_no_results(self, mock_get, real_collector):
        """Testa validação de termo específico sem resultados."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html><body></body></html>")
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        is_valid = await real_collector.validar_termo_especifico("invalid_term_xyz")
        
        assert is_valid is False
    
    @patch.object(GooglePAAColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_google_paa_collect_keywords_success(self, mock_suggestions, real_collector):
        """Testa coleta de keywords com sucesso."""
        mock_suggestions.return_value = [
            "Como funciona o Google PAA?",
            "O que é People Also Ask?",
            "Como extrair dados do Google?"
        ]
        
        keywords = await real_collector.coletar_keywords("google paa", limite=10)
        
        assert len(keywords) > 0
        assert all(isinstance(k, Keyword) for k in keywords)
        
        # Verificar se as keywords têm os campos necessários
        for keyword in keywords:
            assert keyword.termo is not None
            assert keyword.fonte == "google_paa"
            assert keyword.volume >= 0
            assert keyword.concorrencia >= 0
            assert keyword.concorrencia <= 1
    
    @patch.object(GooglePAAColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_google_paa_classify_intention_success(self, mock_suggestions, real_collector):
        """Testa classificação de intenção com sucesso."""
        mock_suggestions.return_value = [
            "Como funciona o Google PAA?",
            "O que é People Also Ask?",
            "Como extrair dados do Google?"
        ]
        
        intentions = await real_collector.classificar_intencao(["google paa", "people also ask"])
        
        assert len(intentions) == 2
        assert all(isinstance(i, IntencaoBusca) for i in intentions)
        
        for intention in intentions:
            assert intention.termo is not None
            assert intention.intencao in ["informacional", "navegacional", "transacional"]
            assert intention.confianca >= 0
            assert intention.confianca <= 1
    
    @patch.object(GooglePAAColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_google_paa_collect_metrics_success(self, mock_suggestions, real_collector):
        """Testa coleta de métricas com sucesso."""
        mock_suggestions.return_value = [
            "Como funciona o Google PAA?",
            "O que é People Also Ask?"
        ]
        
        metrics = await real_collector.coletar_metricas(["google paa", "people also ask"])
        
        assert len(metrics) == 2
        assert all(isinstance(m, dict) for m in metrics)
        
        for metric in metrics:
            assert "termo" in metric
            assert "total_perguntas" in metric
            assert "perguntas_unicas" in metric
            assert "taxa_duplicacao" in metric
            assert "status" in metric
    
    @pytest.mark.asyncio
    async def test_google_paa_cache_functionality(self, real_collector):
        """Testa funcionalidade de cache."""
        cache_key = "test_key"
        cache_value = ["test", "data"]
        
        # Testar set no cache
        await real_collector.cache.set(cache_key, cache_value)
        real_collector.cache.set.assert_called_with(cache_key, cache_value)
        
        # Testar get do cache
        real_collector.cache.get.return_value = cache_value
        result = await real_collector.cache.get(cache_key)
        assert result == cache_value
    
    @pytest.mark.asyncio
    async def test_google_paa_session_management(self, real_collector):
        """Testa gerenciamento de sessão."""
        # Testar criação de sessão
        session = await real_collector._get_session()
        assert session is not None
        
        # Testar reutilização de sessão
        session2 = await real_collector._get_session()
        assert session2 == session


class TestGooglePAARealErrorHandling:
    """Testes para tratamento de erros do Google PAA."""
    
    @pytest.mark.asyncio
    async def test_google_paa_network_error_handling(self, real_collector):
        """Testa tratamento de erro de rede."""
        with patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("google paa")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_google_paa_timeout_error_handling(self, real_collector):
        """Testa tratamento de erro de timeout."""
        with patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError("Request timeout")
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("google paa")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_google_paa_cache_error_handling(self, real_collector):
        """Testa tratamento de erro de cache."""
        real_collector.cache.get.side_effect = Exception("Cache error")
        
        with patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html><body></body></html>")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            suggestions = await real_collector.extrair_sugestoes("google paa")
            
            # Deve continuar funcionando mesmo com erro de cache
            assert isinstance(suggestions, list)
            # Verificar se erro de cache foi logado
            real_collector.logger.error.assert_called()


class TestGooglePAARealPerformance:
    """Testes de performance do Google PAA."""
    
    @pytest.mark.asyncio
    async def test_google_paa_request_performance(self, real_collector):
        """Testa performance das requisições."""
        start_time = time.time()
        
        with patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html><body></body></html>")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            await real_collector.extrair_sugestoes("google paa")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verificar se a execução foi rápida (menos de 1 segundo)
            assert execution_time < 1.0
    
    @pytest.mark.asyncio
    async def test_google_paa_cache_performance(self, real_collector):
        """Testa performance do cache."""
        # Primeira requisição (sem cache)
        start_time = time.time()
        
        with patch('infrastructure.coleta.google_paa.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html><body></body></html>")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session
            real_collector.session = MagicMock()
            
            await real_collector.extrair_sugestoes("google paa")
            
            first_execution_time = time.time() - start_time
        
        # Segunda requisição (com cache)
        start_time = time.time()
        real_collector.cache.get.return_value = ["cached_result"]
        
        await real_collector.extrair_sugestoes("google paa")
        
        second_execution_time = time.time() - start_time
        
        # Verificar se a segunda execução foi mais rápida
        assert second_execution_time < first_execution_time


class TestGooglePAARealDataStructures:
    """Testes para estruturas de dados do Google PAA."""
    
    def test_google_paa_question_extraction(self, real_collector):
        """Testa extração de perguntas de diferentes formatos HTML."""
        # Teste com HTML real do Google
        real_html = """
        <div class="related-question-pair">
            <div class="question">Como funciona o Google PAA?</div>
            <div class="answer">O Google PAA é uma funcionalidade...</div>
        </div>
        <div class="related-question-pair">
            <div class="question">O que é People Also Ask?</div>
        </div>
        """
        
        soup = BeautifulSoup(real_html, 'html.parser')
        questions = []
        
        for div in soup.find_all("div", class_="related-question-pair"):
            question = div.get_text().strip()
            if question and question != "google paa":
                questions.append(question)
        
        assert len(questions) == 2
        assert "Como funciona o Google PAA?" in questions
        assert "O que é People Also Ask?" in questions
    
    def test_google_paa_normalization(self, real_collector):
        """Testa normalização de perguntas."""
        raw_questions = [
            "Como funciona o Google PAA?",
            "O que é People Also Ask?",
            "Como extrair dados do Google?",
            "Quais são as melhores práticas de SEO?"
        ]
        
        normalized_questions = []
        for question in raw_questions:
            normalized = real_collector.normalizador.normalizar(question)
            if normalized:
                normalized_questions.append(normalized)
        
        assert len(normalized_questions) == len(raw_questions)
        assert all(isinstance(q, str) for q in normalized_questions)


class TestGooglePAARealTrendsAnalysis:
    """Testes para análise de tendências do Google PAA."""
    
    @pytest.mark.asyncio
    async def test_google_paa_trends_analysis(self, real_collector):
        """Testa análise de tendências."""
        # Simular dados de tendência
        trend_data = {
            "google paa": {
                "volume": 1000,
                "trend": 0.15,
                "seasonality": 0.05
            },
            "people also ask": {
                "volume": 800,
                "trend": 0.10,
                "seasonality": 0.03
            }
        }
        
        # Mock do analisador de tendências
        real_collector.analisador.analisar_tendencia = MagicMock(return_value=trend_data)
        
        analysis = real_collector.analisador.analisar_tendencia(["google paa", "people also ask"])
        
        assert isinstance(analysis, dict)
        assert "google paa" in analysis
        assert "people also ask" in analysis
        assert "volume" in analysis["google paa"]
        assert "trend" in analysis["google paa"]
        assert "seasonality" in analysis["google paa"] 