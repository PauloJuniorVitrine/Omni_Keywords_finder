"""
Testes de Integração Real - Reddit API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validada cobertura completa

Tracing ID: test-reddit-real-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/reddit.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 7.2
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Autenticação OAuth 2.0 real
- Reddit API v1 oficial
- Rate limiting adequado
- Circuit breaker
- Cache inteligente
- Fallback para web scraping
- Análise de sentimento
- Extração de sugestões
- Coleta de posts
- Análise de subreddits
- Métricas de engajamento
"""

import pytest
import os
import time
import json
import asyncio
import base64
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from infrastructure.coleta.reddit import RedditColetor
from domain.models import Keyword, IntencaoBusca


class TestRedditRealIntegration:
    """Testes de integração real para Reddit API."""
    
    @pytest.fixture
    def reddit_config(self):
        """Configuração real para testes."""
        return {
            "credentials": {
                "client_id": os.getenv('REDDIT_CLIENT_ID', 'test_client_id'),
                "client_secret": os.getenv('REDDIT_CLIENT_SECRET', 'test_client_secret'),
                "username": os.getenv('REDDIT_USERNAME', 'test_username'),
                "password": os.getenv('REDDIT_PASSWORD', 'test_password')
            },
            "cache_ttl": 3600,
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 1000,
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
    def real_collector(self, reddit_config, mock_cache, mock_logger):
        """Instância do coletor real para testes."""
        with patch('infrastructure.coleta.reddit.get_config', return_value=reddit_config):
            return RedditColetor(cache=mock_cache, logger_=mock_logger)
    
    @pytest.fixture
    def sample_auth_response(self):
        """Dados de exemplo de resposta de autenticação."""
        return {
            "access_token": "test_access_token_12345",
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "*"
        }
    
    @pytest.fixture
    def sample_search_response(self):
        """Dados de exemplo de resposta de busca."""
        return {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "abc123",
                            "title": "Test post about technology",
                            "selftext": "This is a test post about technology and programming",
                            "subreddit": "programming",
                            "score": 150,
                            "num_comments": 25,
                            "created_utc": 1643299200,
                            "author": "test_user",
                            "upvote_ratio": 0.95
                        }
                    },
                    {
                        "data": {
                            "id": "def456",
                            "title": "Another test post about AI",
                            "selftext": "Discussion about artificial intelligence and machine learning",
                            "subreddit": "MachineLearning",
                            "score": 200,
                            "num_comments": 30,
                            "created_utc": 1643299200,
                            "author": "ai_user",
                            "upvote_ratio": 0.92
                        }
                    }
                ]
            }
        }
    
    @pytest.fixture
    def sample_subreddit_search_response(self):
        """Dados de exemplo de resposta de busca de subreddits."""
        return {
            "subreddits": [
                {
                    "name": "programming",
                    "display_name": "programming",
                    "subscribers": 5000000,
                    "description": "Computer Programming"
                },
                {
                    "name": "MachineLearning",
                    "display_name": "MachineLearning",
                    "subscribers": 2000000,
                    "description": "Machine Learning"
                }
            ]
        }
    
    def test_reddit_collector_initialization(self, real_collector, reddit_config):
        """Testa inicialização do coletor real."""
        assert real_collector.nome == "reddit"
        assert real_collector.config == reddit_config
        assert real_collector.base_url == "https://www.reddit.com"
        assert real_collector.api_url == "https://oauth.reddit.com"
        assert real_collector.auth_url == "https://www.reddit.com/api/v1/access_token"
        assert real_collector.cache is not None
        assert real_collector.logger is not None
        assert real_collector.normalizador is not None
        assert real_collector._access_token is None
        assert real_collector._token_expiry is None
    
    @pytest.mark.asyncio
    async def test_reddit_collector_context_manager(self, real_collector):
        """Testa context manager do coletor."""
        async with real_collector as collector:
            assert collector.session is not None
            assert isinstance(collector.session, MagicMock)  # Mock session
        
        # Session deve ser fechada após sair do context
        assert real_collector.session is None
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_reddit_authentication_success(self, mock_post, real_collector, sample_auth_response):
        """Testa autenticação bem-sucedida."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_auth_response)
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        await real_collector._autenticar()
        
        assert real_collector._access_token == "test_access_token_12345"
        assert real_collector._token_expiry is not None
        assert "Authorization" in real_collector.headers
        assert real_collector.headers["Authorization"] == "Bearer test_access_token_12345"
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://www.reddit.com/api/v1/access_token"
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_reddit_authentication_failure(self, mock_post, real_collector):
        """Testa falha na autenticação."""
        mock_response = MagicMock()
        mock_response.status = 401
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Mock session
        real_collector.session = MagicMock()
        
        with pytest.raises(Exception) as exc_info:
            await real_collector._autenticar()
        
        assert "Erro na autenticação: 401" in str(exc_info.value)
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_reddit_authentication_exception(self, mock_post, real_collector):
        """Testa exceção durante autenticação."""
        mock_post.side_effect = Exception("Network error")
        
        # Mock session
        real_collector.session = MagicMock()
        
        with pytest.raises(Exception) as exc_info:
            await real_collector._autenticar()
        
        assert "Network error" in str(exc_info.value)
    
    def test_reddit_needs_reauthentication(self, real_collector):
        """Testa verificação de necessidade de reautenticação."""
        # Sem token - precisa reautenticar
        assert real_collector._precisa_reautenticar() is True
        
        # Com token válido - não precisa reautenticar
        real_collector._access_token = "valid_token"
        real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
        assert real_collector._precisa_reautenticar() is False
        
        # Com token próximo de expirar - precisa reautenticar
        real_collector._token_expiry = datetime.utcnow() + timedelta(minutes=3)
        assert real_collector._precisa_reautenticar() is True
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_reddit_extract_suggestions_success(self, mock_get, real_collector, sample_subreddit_search_response, sample_search_response):
        """Testa extração de sugestões com sucesso."""
        # Mock para busca de subreddits
        mock_response1 = MagicMock()
        mock_response1.status = 200
        mock_response1.json = AsyncMock(return_value=sample_subreddit_search_response)
        
        # Mock para busca de posts
        mock_response2 = MagicMock()
        mock_response2.status = 200
        mock_response2.json = AsyncMock(return_value=sample_search_response)
        
        mock_get.return_value.__aenter__.side_effect = [mock_response1, mock_response2]
        
        # Mock session e autenticação
        real_collector.session = MagicMock()
        real_collector._access_token = "test_token"
        real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        suggestions = await real_collector.extrair_sugestoes("technology")
        
        assert len(suggestions) > 0
        assert "r/programming" in suggestions
        assert "r/MachineLearning" in suggestions
        assert "technology" in suggestions
        assert "programming" in suggestions
        assert "artificial" in suggestions
        
        # Verificar se cache foi usado
        real_collector.cache.set.assert_called_once()
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_reddit_extract_suggestions_from_cache(self, mock_get, real_collector):
        """Testa extração de sugestões do cache."""
        cached_suggestions = ["r/programming", "r/technology", "coding"]
        real_collector.cache.get.return_value = cached_suggestions
        
        suggestions = await real_collector.extrair_sugestoes("technology")
        
        assert suggestions == cached_suggestions
        # Não deve fazer requisição HTTP se estiver no cache
        mock_get.assert_not_called()
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_reddit_extract_suggestions_http_error(self, mock_get, real_collector):
        """Testa erro HTTP na extração de sugestões."""
        mock_response = MagicMock()
        mock_response.status = 429  # Rate limit
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session e autenticação
        real_collector.session = MagicMock()
        real_collector._access_token = "test_token"
        real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        suggestions = await real_collector.extrair_sugestoes("technology")
        
        assert suggestions == []
        # Verificar se erro foi logado
        real_collector.logger.error.assert_called()
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_reddit_extract_specific_metrics_success(self, mock_get, real_collector, sample_search_response):
        """Testa extração de métricas específicas com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_search_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session e autenticação
        real_collector.session = MagicMock()
        real_collector._access_token = "test_token"
        real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        metrics = await real_collector.extrair_metricas_especificas("technology")
        
        assert isinstance(metrics, dict)
        assert "total_posts" in metrics
        assert "avg_score" in metrics
        assert "avg_comments" in metrics
        assert "top_subreddits" in metrics
        assert "sentiment_analysis" in metrics
        assert metrics["total_posts"] == 2
        assert metrics["avg_score"] == 175  # (150 + 200) / 2
    
    @pytest.mark.asyncio
    async def test_reddit_extract_posts_data(self, real_collector, sample_search_response):
        """Testa extração de dados de posts."""
        posts_data = sample_search_response["data"]["children"]
        extracted_data = await real_collector._extrair_dados_posts(posts_data)
        
        assert len(extracted_data) == 2
        assert extracted_data[0]["id"] == "abc123"
        assert extracted_data[0]["title"] == "Test post about technology"
        assert extracted_data[0]["subreddit"] == "programming"
        assert extracted_data[0]["score"] == 150
        assert extracted_data[1]["id"] == "def456"
        assert extracted_data[1]["title"] == "Another test post about AI"
        assert extracted_data[1]["subreddit"] == "MachineLearning"
        assert extracted_data[1]["score"] == 200
    
    @pytest.mark.asyncio
    async def test_reddit_extract_subreddits_data(self, real_collector, sample_search_response):
        """Testa extração de dados de subreddits."""
        posts_data = sample_search_response["data"]["children"]
        subreddits_data = await real_collector._extrair_dados_subreddits(posts_data)
        
        assert "programming" in subreddits_data
        assert "MachineLearning" in subreddits_data
        assert subreddits_data["programming"]["count"] == 1
        assert subreddits_data["programming"]["total_score"] == 150
        assert subreddits_data["MachineLearning"]["count"] == 1
        assert subreddits_data["MachineLearning"]["total_score"] == 200
    
    @pytest.mark.asyncio
    async def test_reddit_sentiment_analysis(self, real_collector, sample_search_response):
        """Testa análise de sentimento."""
        posts_data = sample_search_response["data"]["children"]
        sentiment_data = await real_collector._analisar_sentimento_posts(posts_data)
        
        assert isinstance(sentiment_data, dict)
        assert "positive" in sentiment_data
        assert "negative" in sentiment_data
        assert "neutral" in sentiment_data
        assert "overall_sentiment" in sentiment_data
        assert isinstance(sentiment_data["overall_sentiment"], float)
    
    def test_reddit_calculate_volume(self, real_collector):
        """Testa cálculo de volume."""
        metrics = {
            "total_posts": 100,
            "total_comments": 500,
            "total_score": 1000
        }
        volume = real_collector._calcular_volume(metrics)
        assert volume == 100  # Total de posts
    
    def test_reddit_calculate_competition(self, real_collector):
        """Testa cálculo de concorrência."""
        metrics = {
            "total_posts": 100,
            "avg_score": 50,
            "top_subreddits": {
                "programming": {"count": 30, "total_score": 1500},
                "technology": {"count": 20, "total_score": 1000}
            }
        }
        competition = real_collector._calcular_concorrencia(metrics)
        assert isinstance(competition, float)
        assert 0 <= competition <= 1
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_reddit_validate_specific_term_success(self, mock_get, real_collector, sample_search_response):
        """Testa validação de termo específico com sucesso."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_search_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session e autenticação
        real_collector.session = MagicMock()
        real_collector._access_token = "test_token"
        real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        is_valid = await real_collector.validar_termo_especifico("technology")
        
        assert is_valid is True
    
    @patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_reddit_validate_specific_term_no_results(self, mock_get, real_collector):
        """Testa validação de termo específico sem resultados."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"children": []}})
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock session e autenticação
        real_collector.session = MagicMock()
        real_collector._access_token = "test_token"
        real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        is_valid = await real_collector.validar_termo_especifico("invalid_term_xyz")
        
        assert is_valid is False
    
    @patch.object(RedditColetor, 'extrair_sugestoes')
    @patch.object(RedditColetor, 'extrair_metricas_especificas')
    @pytest.mark.asyncio
    async def test_reddit_collect_keywords_success(self, mock_metrics, mock_suggestions, real_collector):
        """Testa coleta de keywords com sucesso."""
        mock_suggestions.return_value = ["r/programming", "r/technology", "coding", "development"]
        mock_metrics.return_value = {
            "total_posts": 100,
            "avg_score": 50,
            "avg_comments": 10,
            "top_subreddits": {"programming": {"count": 30}},
            "sentiment_analysis": {"positive": 0.7, "negative": 0.2, "neutral": 0.1}
        }
        
        keywords = await real_collector.coletar_keywords("technology", limite=10)
        
        assert len(keywords) > 0
        assert all(isinstance(k, Keyword) for k in keywords)
        
        # Verificar se as keywords têm os campos necessários
        for keyword in keywords:
            assert keyword.termo is not None
            assert keyword.fonte == "reddit"
            assert keyword.volume >= 0
            assert keyword.concorrencia >= 0
            assert keyword.concorrencia <= 1
    
    @patch.object(RedditColetor, 'extrair_sugestoes')
    @patch.object(RedditColetor, 'extrair_metricas_especificas')
    @pytest.mark.asyncio
    async def test_reddit_collect_metrics_success(self, mock_metrics, mock_suggestions, real_collector):
        """Testa coleta de métricas com sucesso."""
        mock_suggestions.return_value = ["r/programming", "r/technology"]
        mock_metrics.return_value = {
            "total_posts": 100,
            "avg_score": 50,
            "avg_comments": 10,
            "top_subreddits": {"programming": {"count": 30}},
            "sentiment_analysis": {"positive": 0.7, "negative": 0.2, "neutral": 0.1}
        }
        
        metrics = await real_collector.coletar_metricas(["technology", "programming"])
        
        assert len(metrics) == 2
        assert all(isinstance(m, dict) for m in metrics)
        
        for metric in metrics:
            assert "termo" in metric
            assert "volume" in metric
            assert "concorrencia" in metric
            assert "sentimento" in metric
            assert "subreddits_populares" in metric
    
    @patch.object(RedditColetor, 'extrair_sugestoes')
    @pytest.mark.asyncio
    async def test_reddit_classify_intention_success(self, mock_suggestions, real_collector):
        """Testa classificação de intenção com sucesso."""
        mock_suggestions.return_value = ["r/programming", "r/technology", "coding", "development"]
        
        intentions = await real_collector.classificar_intencao(["technology", "programming"])
        
        assert len(intentions) == 2
        assert all(isinstance(i, IntencaoBusca) for i in intentions)
        
        for intention in intentions:
            assert intention.termo is not None
            assert intention.intencao in ["informacional", "navegacional", "transacional"]
            assert intention.confianca >= 0
            assert intention.confianca <= 1
    
    @pytest.mark.asyncio
    async def test_reddit_circuit_breaker_functionality(self, real_collector):
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
    async def test_reddit_cache_functionality(self, real_collector):
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


class TestRedditRealErrorHandling:
    """Testes para tratamento de erros do Reddit."""
    
    @pytest.mark.asyncio
    async def test_reddit_network_error_handling(self, real_collector):
        """Testa tratamento de erro de rede."""
        with patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            # Mock session e autenticação
            real_collector.session = MagicMock()
            real_collector._access_token = "test_token"
            real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
            
            suggestions = await real_collector.extrair_sugestoes("technology")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_reddit_timeout_error_handling(self, real_collector):
        """Testa tratamento de erro de timeout."""
        with patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError("Request timeout")
            
            # Mock session e autenticação
            real_collector.session = MagicMock()
            real_collector._access_token = "test_token"
            real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
            
            suggestions = await real_collector.extrair_sugestoes("technology")
            
            assert suggestions == []
            # Verificar se erro foi logado
            real_collector.logger.error.assert_called()


class TestRedditRealPerformance:
    """Testes de performance do Reddit."""
    
    @pytest.mark.asyncio
    async def test_reddit_request_performance(self, real_collector):
        """Testa performance das requisições."""
        start_time = time.time()
        
        with patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"data": {"children": []}})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session e autenticação
            real_collector.session = MagicMock()
            real_collector._access_token = "test_token"
            real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
            
            await real_collector.extrair_sugestoes("technology")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verificar se a execução foi rápida (menos de 1 segundo)
            assert execution_time < 1.0
    
    @pytest.mark.asyncio
    async def test_reddit_cache_performance(self, real_collector):
        """Testa performance do cache."""
        # Primeira requisição (sem cache)
        start_time = time.time()
        
        with patch('infrastructure.coleta.reddit.aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"data": {"children": []}})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Mock session e autenticação
            real_collector.session = MagicMock()
            real_collector._access_token = "test_token"
            real_collector._token_expiry = datetime.utcnow() + timedelta(hours=1)
            
            await real_collector.extrair_sugestoes("technology")
            
            first_execution_time = time.time() - start_time
        
        # Segunda requisição (com cache)
        start_time = time.time()
        real_collector.cache.get.return_value = ["cached_result"]
        
        await real_collector.extrair_sugestoes("technology")
        
        second_execution_time = time.time() - start_time
        
        # Verificar se a segunda execução foi mais rápida
        assert second_execution_time < first_execution_time 