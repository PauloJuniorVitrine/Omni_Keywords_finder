#!/usr/bin/env python3
"""
Testes Unitários - Google Keyword Planner
========================================

Tracing ID: TEST_GOOGLE_KEYWORD_PLANNER_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/google_keyword_planner.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 3.1
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import asyncio
import time
import json
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Importar classes e funções reais do sistema
from infrastructure.coleta.google_keyword_planner import (
    KeywordPlannerData,
    GoogleKeywordPlannerColetor
)

from domain.models import IntencaoBusca


class TestKeywordPlannerData:
    """Testes para dataclass KeywordPlannerData."""
    
    def test_keyword_planner_data_creation(self):
        """Testa criação de KeywordPlannerData."""
        data = KeywordPlannerData(
            keyword="marketing digital",
            avg_monthly_searches=10000,
            competition="MEDIUM",
            low_top_of_page_bid=1.50,
            high_top_of_page_bid=3.00,
            suggested_bid=2.25,
            search_volume_trend=[8000, 9000, 10000, 11000],
            competition_index=0.5,
            low_competition_bid=1.00,
            high_competition_bid=2.50,
            year_over_year_change=0.15,
            seasonality={"janeiro": 0.8, "dezembro": 1.2}
        )
        
        assert data.keyword == "marketing digital"
        assert data.avg_monthly_searches == 10000
        assert data.competition == "MEDIUM"
        assert data.low_top_of_page_bid == 1.50
        assert data.high_top_of_page_bid == 3.00
        assert data.suggested_bid == 2.25
        assert data.search_volume_trend == [8000, 9000, 10000, 11000]
        assert data.competition_index == 0.5
        assert data.low_competition_bid == 1.00
        assert data.high_competition_bid == 2.50
        assert data.year_over_year_change == 0.15
        assert data.seasonality == {"janeiro": 0.8, "dezembro": 1.2}
    
    def test_keyword_planner_data_minimal(self):
        """Testa criação com dados mínimos."""
        data = KeywordPlannerData(
            keyword="seo",
            avg_monthly_searches=5000,
            competition="LOW",
            low_top_of_page_bid=0.50,
            high_top_of_page_bid=1.00,
            suggested_bid=0.75,
            search_volume_trend=[],
            competition_index=0.25,
            low_competition_bid=0.25,
            high_competition_bid=0.75,
            year_over_year_change=0.0,
            seasonality={}
        )
        
        assert data.keyword == "seo"
        assert data.avg_monthly_searches == 5000
        assert data.competition == "LOW"
        assert data.search_volume_trend == []
        assert data.seasonality == {}


class TestGoogleKeywordPlannerColetor:
    """Testes para classe GoogleKeywordPlannerColetor."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração do coletor."""
        return {
            "api_enabled": True,
            "scraping_enabled": True,
            "max_keywords_per_request": 100,
            "rate_limit_delay": 2.0,
            "customer_id": "123456789",
            "proxy_enabled": False,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    @pytest.fixture
    def coletor(self, config):
        """Fixture para GoogleKeywordPlannerColetor."""
        with patch('infrastructure.coleta.google_keyword_planner.build'), \
             patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            return GoogleKeywordPlannerColetor(config)
    
    def test_google_keyword_planner_coletor_initialization(self, config):
        """Testa inicialização do GoogleKeywordPlannerColetor."""
        with patch('infrastructure.coleta.google_keyword_planner.build'), \
             patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            
            coletor = GoogleKeywordPlannerColetor(config)
            
            assert coletor.api_enabled is True
            assert coletor.scraping_enabled is True
            assert coletor.max_keywords_per_request == 100
            assert coletor.rate_limit_delay == 2.0
            assert coletor.customer_id == "123456789"
            assert coletor.name == "google_keyword_planner"
    
    @patch('infrastructure.coleta.google_keyword_planner.Credentials.from_authorized_user_file')
    @patch('infrastructure.coleta.google_keyword_planner.InstalledAppFlow.from_client_secrets_file')
    @patch('infrastructure.coleta.google_keyword_planner.build')
    def test_init_google_ads_api_success(self, mock_build, mock_flow, mock_creds, config):
        """Testa inicialização bem-sucedida da Google Ads API."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', create=True), \
             patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            
            # Mock credenciais válidas
            mock_creds.return_value.valid = True
            mock_creds.return_value.expired = False
            
            coletor = GoogleKeywordPlannerColetor(config)
            
            assert coletor.api_enabled is True
            assert coletor.credentials is not None
            assert coletor.service is not None
    
    @patch('infrastructure.coleta.google_keyword_planner.Credentials.from_authorized_user_file')
    @patch('infrastructure.coleta.google_keyword_planner.build')
    def test_init_google_ads_api_error(self, mock_build, mock_creds, config):
        """Testa inicialização com erro da Google Ads API."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', create=True), \
             patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            
            # Mock erro na inicialização
            mock_build.side_effect = Exception("API Error")
            
            coletor = GoogleKeywordPlannerColetor(config)
            
            assert coletor.api_enabled is False
            assert coletor.credentials is None
            assert coletor.service is None
    
    @patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome')
    def test_init_web_scraping_success(self, mock_chrome, config):
        """Testa inicialização bem-sucedida do web scraping."""
        with patch('infrastructure.coleta.google_keyword_planner.build'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            
            coletor = GoogleKeywordPlannerColetor(config)
            
            assert coletor.scraping_enabled is True
            assert coletor.driver is not None
    
    @patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome')
    def test_init_web_scraping_error(self, mock_chrome, config):
        """Testa inicialização com erro do web scraping."""
        with patch('infrastructure.coleta.google_keyword_planner.build'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            
            # Mock erro na inicialização
            mock_chrome.side_effect = Exception("Chrome Error")
            
            coletor = GoogleKeywordPlannerColetor(config)
            
            assert coletor.scraping_enabled is False
            assert coletor.driver is None
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_cache_hit(self, coletor):
        """Testa extração de sugestões com cache hit."""
        # Mock cache com dados
        cached_suggestions = ["marketing digital", "marketing online", "marketing na internet"]
        coletor.cache.get = AsyncMock(return_value=cached_suggestions)
        
        result = await coletor.extrair_sugestoes("marketing")
        
        assert result == cached_suggestions
        coletor.cache.get.assert_called_once_with("keyword_planner_suggestions:marketing")
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_api_success(self, coletor):
        """Testa extração de sugestões via API com sucesso."""
        # Mock cache vazio
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response
        mock_response = {
            'entries': [
                {
                    'data': [
                        {'key': 'KEYWORD_TEXT', 'value': 'marketing digital'},
                        {'key': 'KEYWORD_TEXT', 'value': 'marketing online'},
                        {'key': 'KEYWORD_TEXT', 'value': 'marketing na internet'}
                    ]
                }
            ]
        }
        
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.extrair_sugestoes("marketing")
        
        assert result == ["marketing digital", "marketing online", "marketing na internet"]
        coletor.cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_api_fallback_scraping(self, coletor):
        """Testa fallback para web scraping quando API falha."""
        # Mock cache vazio
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API falhando
        coletor.service.TargetingIdeaService.return_value.get.side_effect = Exception("API Error")
        
        # Mock web scraping
        mock_suggestions = ["marketing digital", "marketing online"]
        coletor._get_suggestions_scraping = AsyncMock(return_value=mock_suggestions)
        
        result = await coletor.extrair_sugestoes("marketing")
        
        assert result == mock_suggestions
        coletor._get_suggestions_scraping.assert_called_once_with("marketing")
    
    @pytest.mark.asyncio
    async def test_extrair_sugestoes_all_fail(self, coletor):
        """Testa quando API e scraping falham."""
        # Mock cache vazio
        coletor.cache.get = AsyncMock(return_value=None)
        
        # Mock API falhando
        coletor.service.TargetingIdeaService.return_value.get.side_effect = Exception("API Error")
        
        # Mock scraping falhando
        coletor._get_suggestions_scraping = AsyncMock(side_effect=Exception("Scraping Error"))
        
        result = await coletor.extrair_sugestoes("marketing")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_suggestions_api_rate_limit(self, coletor):
        """Testa tratamento de rate limit na API."""
        from googleapiclient.errors import HttpError
        
        # Mock cache vazio
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock rate limit error
        mock_response = Mock()
        mock_response.status = 429
        rate_limit_error = HttpError(mock_response, b"Rate limit exceeded")
        
        coletor.service.TargetingIdeaService.return_value.get.side_effect = [
            rate_limit_error,
            {'entries': [{'data': [{'key': 'KEYWORD_TEXT', 'value': 'marketing digital'}]}]}
        ]
        
        with patch('time.sleep') as mock_sleep:
            result = await coletor.extrair_sugestoes("marketing")
        
        assert result == ["marketing digital"]
        mock_sleep.assert_called_with(60)  # Rate limit delay
    
    @pytest.mark.asyncio
    async def test_get_suggestions_scraping_success(self, coletor):
        """Testa web scraping de sugestões com sucesso."""
        # Mock elementos do Selenium
        mock_search_box = Mock()
        mock_search_button = Mock()
        mock_suggestion_elements = [
            Mock(find_element=Mock(return_value=Mock(text="marketing digital"))),
            Mock(find_element=Mock(return_value=Mock(text="marketing online")))
        ]
        
        coletor.driver.get = Mock()
        coletor.driver.find_element = Mock(side_effect=[mock_search_box, mock_search_button])
        coletor.driver.find_elements = Mock(return_value=mock_suggestion_elements)
        
        with patch('infrastructure.coleta.google_keyword_planner.WebDriverWait') as mock_wait:
            result = await coletor._get_suggestions_scraping("marketing")
        
        assert result == ["marketing digital", "marketing online"]
        coletor.driver.get.assert_called_once_with("https://ads.google.com/um/Welcome/Home")
    
    @pytest.mark.asyncio
    async def test_get_suggestions_scraping_error(self, coletor):
        """Testa erro no web scraping de sugestões."""
        coletor.driver.get = Mock(side_effect=Exception("Navigation Error"))
        
        result = await coletor._get_suggestions_scraping("marketing")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_cache_hit(self, coletor):
        """Testa extração de métricas com cache hit."""
        # Mock cache com dados
        cached_metrics = {
            'volume': 10000,
            'cpc': 2.50,
            'concorrencia': 0.5
        }
        coletor.cache.get = AsyncMock(return_value=cached_metrics)
        
        result = await coletor.extrair_metricas_especificas("marketing digital")
        
        assert result == cached_metrics
        coletor.cache.get.assert_called_once_with("keyword_planner_metrics:marketing digital")
    
    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_api_success(self, coletor):
        """Testa extração de métricas via API com sucesso."""
        # Mock cache vazio
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response
        mock_response = {
            'entries': [
                {
                    'data': [
                        {'key': 'AVERAGE_MONTHLY_SEARCHES', 'value': '10000'},
                        {'key': 'COMPETITION', 'value': 'MEDIUM'},
                        {'key': 'LOW_TOP_OF_PAGE_BID', 'value': '1.50'},
                        {'key': 'HIGH_TOP_OF_PAGE_BID', 'value': '3.00'},
                        {'key': 'SUGGESTED_BID', 'value': '2.25'}
                    ]
                }
            ]
        }
        
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.extrair_metricas_especificas("marketing digital")
        
        expected_metrics = {
            'volume': 10000,
            'concorrencia': 0.5,
            'cpc_min': 1.50,
            'cpc_max': 3.00,
            'cpc_suggested': 2.25,
            'cpc': 2.25
        }
        
        assert result == expected_metrics
        coletor.cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extrair_metricas_especificas_fallback_default(self, coletor):
        """Testa fallback para métricas padrão quando tudo falha."""
        # Mock cache vazio
        coletor.cache.get = AsyncMock(return_value=None)
        
        # Mock API falhando
        coletor.service.TargetingIdeaService.return_value.get.side_effect = Exception("API Error")
        
        # Mock scraping falhando
        coletor._get_metrics_scraping = AsyncMock(side_effect=Exception("Scraping Error"))
        
        result = await coletor.extrair_metricas_especificas("marketing digital")
        
        expected_default = {
            'volume': 0,
            'cpc': 0.0,
            'concorrencia': 0.5,
            'intencao': IntencaoBusca.INFORMACIONAL
        }
        
        assert result == expected_default
    
    @pytest.mark.asyncio
    async def test_get_metrics_scraping_success(self, coletor):
        """Testa web scraping de métricas com sucesso."""
        # Mock elementos do Selenium
        mock_search_box = Mock()
        mock_search_button = Mock()
        mock_volume_element = Mock(text="10,000")
        mock_competition_element = Mock(text="Média")
        mock_cpc_element = Mock(text="R$ 2,50")
        
        coletor.driver.get = Mock()
        coletor.driver.find_element = Mock(side_effect=[
            mock_search_box, mock_search_button,
            mock_volume_element, mock_competition_element, mock_cpc_element
        ])
        
        with patch('infrastructure.coleta.google_keyword_planner.WebDriverWait') as mock_wait:
            result = await coletor._get_metrics_scraping("marketing digital")
        
        expected_metrics = {
            'volume': 10000,
            'concorrencia': 0.5,
            'cpc': 2.50
        }
        
        assert result == expected_metrics
    
    def test_parse_competition(self, coletor):
        """Testa parsing de strings de concorrência."""
        assert coletor._parse_competition("LOW") == 0.25
        assert coletor._parse_competition("MEDIUM") == 0.5
        assert coletor._parse_competition("HIGH") == 0.75
        assert coletor._parse_competition("Baixa") == 0.25
        assert coletor._parse_competition("Média") == 0.5
        assert coletor._parse_competition("Alta") == 0.75
        assert coletor._parse_competition("Unknown") == 0.5  # Default
    
    def test_get_default_metrics(self, coletor):
        """Testa obtenção de métricas padrão."""
        default_metrics = coletor._get_default_metrics()
        
        assert default_metrics['volume'] == 0
        assert default_metrics['cpc'] == 0.0
        assert default_metrics['concorrencia'] == 0.5
        assert default_metrics['intencao'] == IntencaoBusca.INFORMACIONAL
    
    @pytest.mark.asyncio
    async def test_get_keyword_ideas_success(self, coletor):
        """Testa obtenção de ideias de keywords com sucesso."""
        seed_keywords = ["marketing", "digital"]
        
        # Mock API response
        mock_response = {
            'entries': [
                {
                    'data': [
                        {'key': 'KEYWORD_TEXT', 'value': 'marketing digital'},
                        {'key': 'AVERAGE_MONTHLY_SEARCHES', 'value': '10000'},
                        {'key': 'COMPETITION', 'value': 'MEDIUM'},
                        {'key': 'LOW_TOP_OF_PAGE_BID', 'value': '1.50'},
                        {'key': 'HIGH_TOP_OF_PAGE_BID', 'value': '3.00'},
                        {'key': 'SUGGESTED_BID', 'value': '2.25'}
                    ]
                }
            ]
        }
        
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.get_keyword_ideas(seed_keywords)
        
        expected_idea = {
            'keyword': 'marketing digital',
            'avg_monthly_searches': 10000,
            'competition': 'MEDIUM',
            'low_top_of_page_bid': 1.50,
            'high_top_of_page_bid': 3.00,
            'suggested_bid': 2.25
        }
        
        assert len(result) == 1
        assert result[0] == expected_idea
    
    @pytest.mark.asyncio
    async def test_get_keyword_ideas_api_disabled(self, coletor):
        """Testa obtenção de ideias quando API está desabilitada."""
        coletor.api_enabled = False
        
        result = await coletor.get_keyword_ideas(["marketing"])
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_keyword_ideas_error(self, coletor):
        """Testa erro na obtenção de ideias de keywords."""
        seed_keywords = ["marketing"]
        
        # Mock API error
        coletor.service.TargetingIdeaService.return_value.get.side_effect = Exception("API Error")
        
        result = await coletor.get_keyword_ideas(seed_keywords)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_historical_metrics_success(self, coletor):
        """Testa obtenção de métricas históricas com sucesso."""
        keyword = "marketing digital"
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        
        # Mock API response
        mock_response = {
            'entries': [
                {
                    'data': [
                        {'key': 'HISTORICAL_QUALITY_SCORE', 'value': '8'},
                        {'key': 'HISTORICAL_CREATIVE_QUALITY_SCORE', 'value': '7'},
                        {'key': 'HISTORICAL_POST_CLICK_QUALITY_SCORE', 'value': '9'},
                        {'key': 'HISTORICAL_SEARCH_PREDICTED_CTR', 'value': '0.05'}
                    ]
                }
            ]
        }
        
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.get_historical_metrics(keyword, start_date, end_date)
        
        expected_metrics = {
            'quality_score': 8,
            'creative_quality': 7,
            'post_click_quality': 9,
            'predicted_ctr': 0.05
        }
        
        assert result == expected_metrics
    
    @pytest.mark.asyncio
    async def test_get_historical_metrics_api_disabled(self, coletor):
        """Testa obtenção de métricas históricas quando API está desabilitada."""
        coletor.api_enabled = False
        
        result = await coletor.get_historical_metrics("marketing", "2024-01-01", "2024-12-31")
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_get_historical_metrics_error(self, coletor):
        """Testa erro na obtenção de métricas históricas."""
        keyword = "marketing digital"
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        
        # Mock API error
        coletor.service.TargetingIdeaService.return_value.get.side_effect = Exception("API Error")
        
        result = await coletor.get_historical_metrics(keyword, start_date, end_date)
        
        assert result == {}
    
    def test_del_cleanup(self, coletor):
        """Testa cleanup no destruidor."""
        # Mock driver
        coletor.driver = Mock()
        coletor.driver.quit = Mock()
        
        # Chamar destruidor
        coletor.__del__()
        
        coletor.driver.quit.assert_called_once()


class TestGoogleKeywordPlannerIntegration:
    """Testes de integração para GoogleKeywordPlannerColetor."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return {
            "api_enabled": True,
            "scraping_enabled": True,
            "max_keywords_per_request": 50,
            "rate_limit_delay": 1.0,
            "customer_id": "123456789"
        }
    
    @pytest.fixture
    def coletor(self, config):
        """Fixture para coletor com mocks."""
        with patch('infrastructure.coleta.google_keyword_planner.build'), \
             patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            return GoogleKeywordPlannerColetor(config)
    
    @pytest.mark.asyncio
    async def test_full_workflow_suggestions(self, coletor):
        """Testa workflow completo de extração de sugestões."""
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response
        mock_response = {
            'entries': [
                {
                    'data': [
                        {'key': 'KEYWORD_TEXT', 'value': 'marketing digital'},
                        {'key': 'KEYWORD_TEXT', 'value': 'marketing online'},
                        {'key': 'KEYWORD_TEXT', 'value': 'marketing na internet'}
                    ]
                }
            ]
        }
        
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.extrair_sugestoes("marketing")
        
        assert len(result) == 3
        assert "marketing digital" in result
        assert "marketing online" in result
        assert "marketing na internet" in result
        
        # Verificar se foi salvo no cache
        coletor.cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_full_workflow_metrics(self, coletor):
        """Testa workflow completo de extração de métricas."""
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response
        mock_response = {
            'entries': [
                {
                    'data': [
                        {'key': 'AVERAGE_MONTHLY_SEARCHES', 'value': '15000'},
                        {'key': 'COMPETITION', 'value': 'HIGH'},
                        {'key': 'LOW_TOP_OF_PAGE_BID', 'value': '2.00'},
                        {'key': 'HIGH_TOP_OF_PAGE_BID', 'value': '5.00'},
                        {'key': 'SUGGESTED_BID', 'value': '3.50'}
                    ]
                }
            ]
        }
        
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.extrair_metricas_especificas("marketing digital")
        
        expected_metrics = {
            'volume': 15000,
            'concorrencia': 0.75,
            'cpc_min': 2.00,
            'cpc_max': 5.00,
            'cpc_suggested': 3.50,
            'cpc': 3.50
        }
        
        assert result == expected_metrics
        
        # Verificar se foi salvo no cache
        coletor.cache.set.assert_called_once()


class TestGoogleKeywordPlannerEdgeCases:
    """Testes para casos edge do GoogleKeywordPlannerColetor."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return {
            "api_enabled": True,
            "scraping_enabled": True,
            "max_keywords_per_request": 10,
            "rate_limit_delay": 0.1
        }
    
    @pytest.fixture
    def coletor(self, config):
        """Fixture para coletor."""
        with patch('infrastructure.coleta.google_keyword_planner.build'), \
             patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            return GoogleKeywordPlannerColetor(config)
    
    @pytest.mark.asyncio
    async def test_empty_term_suggestions(self, coletor):
        """Testa extração de sugestões com termo vazio."""
        result = await coletor.extrair_sugestoes("")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_empty_term_metrics(self, coletor):
        """Testa extração de métricas com termo vazio."""
        result = await coletor.extrair_metricas_especificas("")
        
        # Deve retornar métricas padrão
        assert result['volume'] == 0
        assert result['cpc'] == 0.0
    
    @pytest.mark.asyncio
    async def test_special_characters_term(self, coletor):
        """Testa extração com caracteres especiais."""
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response
        mock_response = {'entries': []}
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.extrair_sugestoes("marketing@digital#2024")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_very_long_term(self, coletor):
        """Testa extração com termo muito longo."""
        long_term = "a" * 1000
        
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response
        mock_response = {'entries': []}
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.extrair_sugestoes(long_term)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_max_keywords_limit(self, coletor):
        """Testa limite máximo de keywords por requisição."""
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response com mais keywords que o limite
        mock_response = {
            'entries': [
                {
                    'data': [
                        {'key': 'KEYWORD_TEXT', 'value': f'keyword_{i}'}
                        for i in range(20)  # Mais que o limite de 10
                    ]
                }
            ]
        }
        
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        with patch('time.sleep'):
            result = await coletor.extrair_sugestoes("test")
        
        assert len(result) == 10  # Limite máximo
        assert result[0] == "keyword_0"
        assert result[9] == "keyword_9"


class TestGoogleKeywordPlannerPerformance:
    """Testes de performance para GoogleKeywordPlannerColetor."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return {
            "api_enabled": True,
            "scraping_enabled": False,  # Desabilitar scraping para testes de API
            "max_keywords_per_request": 100,
            "rate_limit_delay": 0.1  # Delay baixo para testes
        }
    
    @pytest.fixture
    def coletor(self, config):
        """Fixture para coletor."""
        with patch('infrastructure.coleta.google_keyword_planner.build'), \
             patch('infrastructure.coleta.google_keyword_planner.webdriver.Chrome'), \
             patch('infrastructure.coleta.google_keyword_planner.requests.Session'):
            return GoogleKeywordPlannerColetor(config)
    
    @pytest.mark.asyncio
    async def test_rate_limiting_respect(self, coletor):
        """Testa se o rate limiting é respeitado."""
        # Mock cache
        coletor.cache.get = AsyncMock(return_value=None)
        coletor.cache.set = AsyncMock()
        
        # Mock API response
        mock_response = {'entries': [{'data': [{'key': 'KEYWORD_TEXT', 'value': 'test'}]}]}
        coletor.service.TargetingIdeaService.return_value.get.return_value = mock_response
        
        start_time = time.time()
        
        with patch('time.sleep') as mock_sleep:
            await coletor.extrair_sugestoes("test1")
            await coletor.extrair_sugestoes("test2")
        
        # Verificar se sleep foi chamado
        assert mock_sleep.call_count >= 2
        
        # Verificar se o delay foi respeitado
        for call in mock_sleep.call_args_list:
            assert call[0][0] >= coletor.rate_limit_delay
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, coletor):
        """Testa performance do cache."""
        # Mock cache com dados
        cached_data = ["cached_keyword_1", "cached_keyword_2"]
        coletor.cache.get = AsyncMock(return_value=cached_data)
        
        start_time = time.time()
        result = await coletor.extrair_sugestoes("test")
        cache_time = time.time() - start_time
        
        # Cache deve ser muito rápido (< 100ms)
        assert cache_time < 0.1
        assert result == cached_data


if __name__ == "__main__":
    pytest.main([__file__]) 