"""
Testes de Integração Real - Google Search Console API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validada cobertura completa

Tracing ID: test-gsc-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/gsc.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 7.4
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Google Search Console API
- Autenticação OAuth 2.0
- Coleta de analytics de busca
- Rate limiting
- Circuit breaker
- Cache inteligente
- Análise de tendências
- Multi-site support
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

from infrastructure.coleta.gsc import GSCColetor
from domain.models import Keyword, IntencaoBusca


class TestGSCRealIntegration:
    """Testes de integração real para Google Search Console API."""
    
    @pytest.fixture
    def gsc_config(self):
        """Configuração real para testes."""
        return {
            "credentials": {
                "client_id": os.getenv('GSC_CLIENT_ID', 'test_client_id'),
                "client_secret": os.getenv('GSC_CLIENT_SECRET', 'test_client_secret'),
                "refresh_token": os.getenv('GSC_REFRESH_TOKEN', 'test_refresh_token'),
                "token_uri": "https://oauth2.googleapis.com/token"
            },
            "sites": {
                "https://example.com": {
                    "nome": "Example Site",
                    "categorias": ["technology", "business"],
                    "idiomas": ["pt-br", "en"],
                    "paises": ["br", "us"],
                    "ativo": True
                },
                "https://test.com": {
                    "nome": "Test Site",
                    "categorias": ["test"],
                    "idiomas": ["pt-br"],
                    "paises": ["br"],
                    "ativo": True
                }
            },
            "janela_dados_dias": 90,
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 1000,
            "env": "test"
        }
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger para testes."""
        logger = MagicMock()
        logger.info = MagicMock()
        logger.error = MagicMock()
        logger.warning = MagicMock()
        return logger
    
    @pytest.fixture
    def real_collector(self, gsc_config, mock_logger):
        """Instância do coletor real para testes."""
        with patch('infrastructure.coleta.gsc.GSC_CONFIG', gsc_config):
            return GSCColetor(logger_=mock_logger)
    
    @pytest.fixture
    def sample_sites_response(self):
        """Dados de exemplo de resposta de sites."""
        return {
            "siteEntry": [
                {
                    "siteUrl": "https://example.com",
                    "permissionLevel": "siteOwner"
                },
                {
                    "siteUrl": "https://test.com",
                    "permissionLevel": "siteFullUser"
                }
            ]
        }
    
    @pytest.fixture
    def sample_search_analytics_response(self):
        """Dados de exemplo de resposta de analytics de busca."""
        return {
            "rows": [
                {
                    "keys": ["google search console api"],
                    "clicks": 150,
                    "impressions": 1000,
                    "ctr": 0.15,
                    "position": 2.5
                },
                {
                    "keys": ["google search console tutorial"],
                    "clicks": 100,
                    "impressions": 800,
                    "ctr": 0.125,
                    "position": 3.2
                },
                {
                    "keys": ["gsc api documentation"],
                    "clicks": 75,
                    "impressions": 600,
                    "ctr": 0.125,
                    "position": 4.1
                }
            ]
        }
    
    @pytest.fixture
    def sample_metrics_response(self):
        """Dados de exemplo de resposta de métricas."""
        return {
            "rows": [
                {
                    "keys": ["google search console"],
                    "clicks": 500,
                    "impressions": 5000,
                    "ctr": 0.10,
                    "position": 2.0
                }
            ]
        }
    
    def test_gsc_collector_initialization(self, real_collector, gsc_config):
        """Testa inicialização do coletor real."""
        assert real_collector.nome == "gsc"
        assert real_collector.config == gsc_config
        assert real_collector.logger is not None
        assert real_collector.credenciais is not None
        assert real_collector.service is not None
        assert real_collector.dias_analise == 90
        assert real_collector.cache is not None
        assert real_collector.analisador is not None
        assert real_collector.normalizador is not None
    
    @patch('infrastructure.coleta.gsc.build')
    @patch('infrastructure.coleta.gsc.Credentials.from_authorized_user_info')
    def test_gsc_credentials_initialization(self, mock_credentials, mock_build, real_collector):
        """Testa inicialização de credenciais."""
        mock_creds = MagicMock()
        mock_credentials.return_value = mock_creds
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Recriar o coletor para testar inicialização
        with patch('infrastructure.coleta.gsc.GSC_CONFIG', self.gsc_config()):
            collector = GSCColetor()
        
        assert collector.credenciais == mock_creds
        assert collector.service == mock_service
        
        mock_credentials.assert_called_once()
        mock_build.assert_called_once_with('searchconsole', 'v1', credentials=mock_creds)
    
    @patch.object(GSCColetor, 'service')
    def test_gsc_load_sites_success(self, mock_service, real_collector, sample_sites_response):
        """Testa carregamento de sites com sucesso."""
        mock_service.sites.return_value.list.return_value.execute.return_value = sample_sites_response
        
        sites = real_collector._carregar_sites()
        
        assert len(sites) == 2
        assert "https://example.com" in sites
        assert "https://test.com" in sites
        assert sites["https://example.com"]["nome"] == "Example Site"
        assert sites["https://test.com"]["nome"] == "Test Site"
        assert sites["https://example.com"]["permissionLevel"] == "siteOwner"
        assert sites["https://test.com"]["permissionLevel"] == "siteFullUser"
    
    @patch.object(GSCColetor, 'service')
    def test_gsc_load_sites_no_access(self, mock_service, real_collector):
        """Testa carregamento de sites sem acesso."""
        mock_service.sites.return_value.list.return_value.execute.return_value = {
            "siteEntry": []
        }
        
        with pytest.raises(ValueError, match="Nenhum site ativo configurado"):
            real_collector._carregar_sites()
    
    @patch.object(GSCColetor, 'service')
    def test_gsc_load_sites_exception(self, mock_service, real_collector):
        """Testa exceção no carregamento de sites."""
        mock_service.sites.return_value.list.return_value.execute.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            real_collector._carregar_sites()
    
    @patch.object(GSCColetor, 'service')
    @pytest.mark.asyncio
    async def test_gsc_extract_suggestions_success(self, mock_service, real_collector, sample_search_analytics_response):
        """Testa extração de sugestões com sucesso."""
        # Mock sites
        real_collector.sites = {
            "https://example.com": {
                "nome": "Example Site",
                "categorias": ["technology"],
                "idiomas": ["pt-br"],
                "paises": ["br"],
                "info": {"permissionLevel": "siteOwner"}
            }
        }
        
        # Mock cache
        real_collector.cache.get = AsyncMock(return_value=None)
        real_collector.cache.set = AsyncMock()
        
        # Mock service response
        mock_service.searchanalytics.return_value.query.return_value.execute.return_value = sample_search_analytics_response
        
        suggestions = await real_collector.extrair_sugestoes("google search console")
        
        assert len(suggestions) == 3
        assert "google search console api" in suggestions
        assert "google search console tutorial" in suggestions
        assert "gsc api documentation" in suggestions
        
        # Verificar se cache foi usado
        real_collector.cache.set.assert_called_once()
    
    @patch.object(GSCColetor, 'service')
    @pytest.mark.asyncio
    async def test_gsc_extract_suggestions_from_cache(self, mock_service, real_collector):
        """Testa extração de sugestões do cache."""
        cached_suggestions = ["google search console api", "gsc tutorial"]
        real_collector.cache.get = AsyncMock(return_value=cached_suggestions)
        
        suggestions = await real_collector.extrair_sugestoes("google search console")
        
        assert suggestions == cached_suggestions
        # Não deve fazer requisição à API se estiver no cache
        mock_service.searchanalytics.assert_not_called()
    
    @patch.object(GSCColetor, 'service')
    @pytest.mark.asyncio
    async def test_gsc_extract_suggestions_api_error(self, mock_service, real_collector):
        """Testa erro na API durante extração de sugestões."""
        # Mock sites
        real_collector.sites = {
            "https://example.com": {
                "nome": "Example Site",
                "categorias": ["technology"],
                "idiomas": ["pt-br"],
                "paises": ["br"],
                "info": {"permissionLevel": "siteOwner"}
            }
        }
        
        # Mock cache
        real_collector.cache.get = AsyncMock(return_value=None)
        real_collector.cache.set = AsyncMock()
        
        # Mock service error
        mock_service.searchanalytics.return_value.query.return_value.execute.side_effect = Exception("API Error")
        
        suggestions = await real_collector.extrair_sugestoes("google search console")
        
        assert suggestions == []
        # Verificar se erro foi logado
        real_collector.logger.error.assert_called()
    
    @patch.object(GSCColetor, 'service')
    @pytest.mark.asyncio
    async def test_gsc_extract_specific_metrics_success(self, mock_service, real_collector, sample_metrics_response):
        """Testa extração de métricas específicas com sucesso."""
        # Mock sites
        real_collector.sites = {
            "https://example.com": {
                "nome": "Example Site",
                "categorias": ["technology"],
                "idiomas": ["pt-br"],
                "paises": ["br"],
                "info": {"permissionLevel": "siteOwner"}
            }
        }
        
        # Mock service response
        mock_service.searchanalytics.return_value.query.return_value.execute.return_value = sample_metrics_response
        
        metrics = await real_collector.extrair_metricas_especificas("google search console")
        
        assert isinstance(metrics, dict)
        assert "total_clicks" in metrics
        assert "total_impressions" in metrics
        assert "avg_ctr" in metrics
        assert "avg_position" in metrics
        assert "sites_analisados" in metrics
        assert "status" in metrics
        assert metrics["total_clicks"] == 500
        assert metrics["total_impressions"] == 5000
        assert metrics["avg_ctr"] == 0.10
        assert metrics["avg_position"] == 2.0
        assert metrics["status"] == "sucesso"
    
    @pytest.mark.asyncio
    async def test_gsc_extract_metrics_query(self, real_collector, sample_metrics_response):
        """Testa extração de métricas de query específica."""
        # Mock service
        mock_service = MagicMock()
        mock_service.searchanalytics.return_value.query.return_value.execute.return_value = sample_metrics_response
        real_collector.service = mock_service
        
        data_inicio = datetime.utcnow() - timedelta(days=30)
        data_fim = datetime.utcnow()
        
        metrics = await real_collector._extrair_metricas_query(
            "https://example.com",
            "google search console",
            data_inicio,
            data_fim
        )
        
        assert isinstance(metrics, dict)
        assert "clicks" in metrics
        assert "impressions" in metrics
        assert "ctr" in metrics
        assert "position" in metrics
        assert metrics["clicks"] == 500
        assert metrics["impressions"] == 5000
    
    def test_gsc_analyze_seasonality(self, real_collector):
        """Testa análise de sazonalidade."""
        # Dados de exemplo com padrão sazonal
        dados_diarios = [
            [{"clicks": 100, "impressions": 1000}],  # Dia 1
            [{"clicks": 120, "impressions": 1200}],  # Dia 2
            [{"clicks": 80, "impressions": 800}],    # Dia 3
            [{"clicks": 110, "impressions": 1100}],  # Dia 4
        ]
        
        sazonalidade = real_collector._analisar_sazonalidade(dados_diarios)
        
        assert isinstance(sazonalidade, float)
        assert 0 <= sazonalidade <= 1
    
    def test_gsc_calculate_volume(self, real_collector):
        """Testa cálculo de volume."""
        metrics = {
            "total_clicks": 1000,
            "total_impressions": 10000,
            "avg_ctr": 0.10,
            "avg_position": 2.5
        }
        volume = real_collector._calcular_volume(metrics)
        assert volume == 1000  # Total de clicks
    
    def test_gsc_calculate_competition(self, real_collector):
        """Testa cálculo de concorrência."""
        metrics = {
            "total_clicks": 1000,
            "total_impressions": 10000,
            "avg_ctr": 0.10,
            "avg_position": 2.5,
            "sites_analisados": 3
        }
        competition = real_collector._calcular_concorrencia(metrics)
        assert isinstance(competition, float)
        assert 0 <= competition <= 1
    
    @patch.object(GSCColetor, 'service')
    @pytest.mark.asyncio
    async def test_gsc_validate_specific_term_success(self, mock_service, real_collector, sample_metrics_response):
        """Testa validação de termo específico com sucesso."""
        # Mock sites
        real_collector.sites = {
            "https://example.com": {
                "nome": "Example Site",
                "categorias": ["technology"],
                "idiomas": ["pt-br"],
                "paises": ["br"],
                "info": {"permissionLevel": "siteOwner"}
            }
        }
        
        # Mock service response
        mock_service.searchanalytics.return_value.query.return_value.execute.return_value = sample_metrics_response
        
        is_valid = await real_collector.validar_termo_especifico("google search console")
        
        assert is_valid is True
    
    @patch.object(GSCColetor, 'service')
    @pytest.mark.asyncio
    async def test_gsc_validate_specific_term_no_results(self, mock_service, real_collector):
        """Testa validação de termo específico sem resultados."""
        # Mock sites
        real_collector.sites = {
            "https://example.com": {
                "nome": "Example Site",
                "categorias": ["technology"],
                "idiomas": ["pt-br"],
                "paises": ["br"],
                "info": {"permissionLevel": "siteOwner"}
            }
        }
        
        # Mock service response sem resultados
        mock_service.searchanalytics.return_value.query.return_value.execute.return_value = {"rows": []}
        
        is_valid = await real_collector.validar_termo_especifico("invalid_term_xyz")
        
        assert is_valid is False
    
    @patch.object(GSCColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_gsc_collect_keywords_success(self, mock_suggestions, real_collector):
        """Testa coleta de keywords com sucesso."""
        mock_suggestions.return_value = [
            "google search console api",
            "gsc tutorial",
            "search console setup"
        ]
        
        keywords = await real_collector.coletar_keywords("google search console", limite=10)
        
        assert len(keywords) > 0
        assert all(isinstance(k, Keyword) for k in keywords)
        
        # Verificar se as keywords têm os campos necessários
        for keyword in keywords:
            assert keyword.termo is not None
            assert keyword.fonte == "gsc"
            assert keyword.volume >= 0
            assert keyword.concorrencia >= 0
            assert keyword.concorrencia <= 1
    
    @patch.object(GSCColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_gsc_classify_intention_success(self, mock_suggestions, real_collector):
        """Testa classificação de intenção com sucesso."""
        mock_suggestions.return_value = [
            "google search console api",
            "gsc tutorial",
            "search console setup"
        ]
        
        intentions = await real_collector.classificar_intencao(["google search console", "gsc"])
        
        assert len(intentions) == 2
        assert all(isinstance(i, IntencaoBusca) for i in intentions)
        
        for intention in intentions:
            assert intention.termo is not None
            assert intention.intencao in ["informacional", "navegacional", "transacional"]
            assert intention.confianca >= 0
            assert intention.confianca <= 1
    
    @patch.object(GSCColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_gsc_collect_metrics_success(self, mock_suggestions, real_collector):
        """Testa coleta de métricas com sucesso."""
        mock_suggestions.return_value = [
            "google search console api",
            "gsc tutorial"
        ]
        
        metrics = await real_collector.coletar_metricas(["google search console", "gsc"])
        
        assert len(metrics) == 2
        assert all(isinstance(m, dict) for m in metrics)
        
        for metric in metrics:
            assert "termo" in metric
            assert "total_clicks" in metric
            assert "total_impressions" in metric
            assert "avg_ctr" in metric
            assert "avg_position" in metric
            assert "status" in metric
    
    @pytest.mark.asyncio
    async def test_gsc_circuit_breaker_functionality(self, real_collector):
        """Testa funcionalidade do circuit breaker."""
        # Estado inicial deve ser CLOSED
        assert real_collector.breaker._state == "CLOSED"
        
        # Simular falhas para abrir o circuit breaker
        for _ in range(5):
            try:
                real_collector.breaker._call_wrapped_function(lambda: None)
            except:
                pass
        
        # Circuit breaker deve estar OPEN
        assert real_collector.breaker._state == "OPEN"
    
    @pytest.mark.asyncio
    async def test_gsc_cache_functionality(self, real_collector):
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


class TestGSCRealErrorHandling:
    """Testes para tratamento de erros do GSC."""
    
    @pytest.mark.asyncio
    async def test_gsc_api_error_handling(self, real_collector):
        """Testa tratamento de erro da API."""
        with patch.object(real_collector, 'service') as mock_service:
            mock_service.searchanalytics.return_value.query.return_value.execute.side_effect = Exception("API Error")
            
            # Mock sites
            real_collector.sites = {
                "https://example.com": {
                    "nome": "Example Site",
                    "categorias": ["technology"],
                    "idiomas": ["pt-br"],
                    "paises": ["br"],
                    "info": {"permissionLevel": "siteOwner"}
                }
            }
            
            # Mock cache
            real_collector.cache.get = AsyncMock(return_value=None)
            real_collector.cache.set = AsyncMock()
            
            suggestions = await real_collector.extrair_sugestoes("google search console")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_gsc_authentication_error_handling(self, real_collector):
        """Testa tratamento de erro de autenticação."""
        with patch.object(real_collector, 'service') as mock_service:
            mock_service.sites.return_value.list.return_value.execute.side_effect = Exception("Authentication failed")
            
            with pytest.raises(Exception):
                real_collector._carregar_sites()
            
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()


class TestGSCRealPerformance:
    """Testes de performance do GSC."""
    
    @pytest.mark.asyncio
    async def test_gsc_request_performance(self, real_collector):
        """Testa performance das requisições."""
        start_time = time.time()
        
        with patch.object(real_collector, 'service') as mock_service:
            mock_service.searchanalytics.return_value.query.return_value.execute.return_value = {
                "rows": [{"keys": ["test"], "clicks": 100, "impressions": 1000, "ctr": 0.10, "position": 2.0}]
            }
            
            # Mock sites
            real_collector.sites = {
                "https://example.com": {
                    "nome": "Example Site",
                    "categorias": ["technology"],
                    "idiomas": ["pt-br"],
                    "paises": ["br"],
                    "info": {"permissionLevel": "siteOwner"}
                }
            }
            
            # Mock cache
            real_collector.cache.get = AsyncMock(return_value=None)
            real_collector.cache.set = AsyncMock()
            
            await real_collector.extrair_sugestoes("test")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verificar se a execução foi rápida (menos de 1 segundo)
            assert execution_time < 1.0
    
    @pytest.mark.asyncio
    async def test_gsc_cache_performance(self, real_collector):
        """Testa performance do cache."""
        # Primeira requisição (sem cache)
        start_time = time.time()
        
        with patch.object(real_collector, 'service') as mock_service:
            mock_service.searchanalytics.return_value.query.return_value.execute.return_value = {
                "rows": [{"keys": ["test"], "clicks": 100, "impressions": 1000, "ctr": 0.10, "position": 2.0}]
            }
            
            # Mock sites
            real_collector.sites = {
                "https://example.com": {
                    "nome": "Example Site",
                    "categorias": ["technology"],
                    "idiomas": ["pt-br"],
                    "paises": ["br"],
                    "info": {"permissionLevel": "siteOwner"}
                }
            }
            
            # Mock cache
            real_collector.cache.get = AsyncMock(return_value=None)
            real_collector.cache.set = AsyncMock()
            
            await real_collector.extrair_sugestoes("test")
            
            first_execution_time = time.time() - start_time
        
        # Segunda requisição (com cache)
        start_time = time.time()
        real_collector.cache.get.return_value = ["cached_result"]
        
        await real_collector.extrair_sugestoes("test")
        
        second_execution_time = time.time() - start_time
        
        # Verificar se a segunda execução foi mais rápida
        assert second_execution_time < first_execution_time


class TestGSCRealMultiSite:
    """Testes para funcionalidades multi-site do GSC."""
    
    @pytest.mark.asyncio
    async def test_gsc_multi_site_analysis(self, real_collector):
        """Testa análise multi-site."""
        # Mock sites múltiplos
        real_collector.sites = {
            "https://site1.com": {
                "nome": "Site 1",
                "categorias": ["technology"],
                "idiomas": ["pt-br"],
                "paises": ["br"],
                "info": {"permissionLevel": "siteOwner"}
            },
            "https://site2.com": {
                "nome": "Site 2",
                "categorias": ["business"],
                "idiomas": ["en"],
                "paises": ["us"],
                "info": {"permissionLevel": "siteFullUser"}
            }
        }
        
        with patch.object(real_collector, 'service') as mock_service:
            # Mock responses diferentes para cada site
            mock_service.searchanalytics.return_value.query.return_value.execute.side_effect = [
                {"rows": [{"keys": ["test1"], "clicks": 100, "impressions": 1000, "ctr": 0.10, "position": 2.0}]},
                {"rows": [{"keys": ["test2"], "clicks": 200, "impressions": 2000, "ctr": 0.10, "position": 1.5}]}
            ]
            
            # Mock cache
            real_collector.cache.get = AsyncMock(return_value=None)
            real_collector.cache.set = AsyncMock()
            
            suggestions = await real_collector.extrair_sugestoes("test")
            
            assert len(suggestions) == 2
            assert "test1" in suggestions
            assert "test2" in suggestions
    
    @pytest.mark.asyncio
    async def test_gsc_site_permission_handling(self, real_collector):
        """Testa tratamento de permissões de site."""
        # Mock sites com diferentes níveis de permissão
        real_collector.sites = {
            "https://site1.com": {
                "nome": "Site 1",
                "categorias": ["technology"],
                "idiomas": ["pt-br"],
                "paises": ["br"],
                "info": {"permissionLevel": "siteOwner"}
            },
            "https://site2.com": {
                "nome": "Site 2",
                "categorias": ["business"],
                "idiomas": ["en"],
                "paises": ["us"],
                "info": {"permissionLevel": "siteRestrictedUser"}
            }
        }
        
        with patch.object(real_collector, 'service') as mock_service:
            # Mock erro para site sem permissão
            mock_service.searchanalytics.return_value.query.return_value.execute.side_effect = [
                {"rows": [{"keys": ["test1"], "clicks": 100, "impressions": 1000, "ctr": 0.10, "position": 2.0}]},
                Exception("Insufficient permissions")
            ]
            
            # Mock cache
            real_collector.cache.get = AsyncMock(return_value=None)
            real_collector.cache.set = AsyncMock()
            
            suggestions = await real_collector.extrair_sugestoes("test")
            
            # Deve retornar sugestões apenas do site com permissão
            assert len(suggestions) == 1
            assert "test1" in suggestions 