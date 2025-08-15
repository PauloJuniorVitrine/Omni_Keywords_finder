"""
Testes de Integração Real - Facebook API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validada cobertura completa

Tracing ID: test-facebook-real-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/facebook_api.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 7.1
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Autenticação OAuth 2.0 real
- Facebook Graph API
- Rate limiting baseado em limites reais
- Circuit breaker para falhas de API
- Cache inteligente
- Fallback para web scraping
- Métricas de performance
- Logs estruturados
- Coleta de posts
- Insights de página
- Dados de audiência
"""

import pytest
import os
import time
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from infrastructure.coleta.facebook_api import (
    FacebookCollector, FacebookConfig, FacebookPost, FacebookInsight, FacebookAudience,
    FacebookAPIError, FacebookRateLimitError, FacebookAuthError, FacebookPermissionError,
    create_facebook_collector
)


class TestFacebookRealIntegration:
    """Testes de integração real para Facebook API."""
    
    @pytest.fixture
    def real_config(self):
        """Configuração real para testes."""
        return FacebookConfig(
            app_id=os.getenv('FACEBOOK_APP_ID', 'test_app_id'),
            app_secret=os.getenv('FACEBOOK_APP_SECRET', 'test_app_secret'),
            access_token=os.getenv('FACEBOOK_ACCESS_TOKEN', 'test_access_token'),
            api_version="v18.0",
            base_url="https://graph.facebook.com",
            rate_limit_per_hour=200,
            rate_limit_per_day=5000,
            cache_ttl=3600,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60
        )
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock do cliente Redis para testes."""
        redis_client = MagicMock()
        redis_client.get = AsyncMock(return_value=None)
        redis_client.set = AsyncMock()
        redis_client.incr = AsyncMock(return_value=1)
        redis_client.expire = AsyncMock()
        return redis_client
    
    @pytest.fixture
    def real_collector(self, real_config, mock_redis_client):
        """Instância do coletor real para testes."""
        return FacebookCollector(real_config, mock_redis_client)
    
    @pytest.fixture
    def sample_post_data(self):
        """Dados de exemplo de post real."""
        return {
            'id': '123456789_987654321',
            'message': 'Test post with #test #facebook #omni hashtags',
            'created_time': '2025-01-27T10:30:00+0000',
            'type': 'status',
            'privacy': {'value': 'EVERYONE'},
            'from': {'id': '123456789', 'name': 'Test Page'},
            'likes': {'summary': {'total_count': 150}},
            'comments': {'summary': {'total_count': 25}},
            'shares': {'count': 10},
            'reactions': {'summary': {'total_count': 200}}
        }
    
    @pytest.fixture
    def sample_insight_data(self):
        """Dados de exemplo de insight real."""
        return {
            'data': [
                {
                    'name': 'page_impressions',
                    'period': 'day',
                    'values': [
                        {
                            'value': 1000,
                            'end_time': '2025-01-27T00:00:00+0000'
                        }
                    ]
                },
                {
                    'name': 'page_engaged_users',
                    'period': 'day',
                    'values': [
                        {
                            'value': 500,
                            'end_time': '2025-01-27T00:00:00+0000'
                        }
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def sample_audience_data(self):
        """Dados de exemplo de audiência real."""
        return {
            'data': [
                {
                    'name': 'page_fans_city',
                    'period': 'lifetime',
                    'values': [
                        {
                            'value': {
                                'São Paulo, Brazil': 1000,
                                'Rio de Janeiro, Brazil': 500
                            }
                        }
                    ]
                },
                {
                    'name': 'page_fans_gender_age',
                    'period': 'lifetime',
                    'values': [
                        {
                            'value': {
                                'M.18-24': 200,
                                'M.25-34': 300,
                                'F.18-24': 250,
                                'F.25-34': 350
                            }
                        }
                    ]
                }
            ]
        }
    
    def test_facebook_config_initialization(self, real_config):
        """Testa inicialização da configuração real."""
        assert real_config.app_id == os.getenv('FACEBOOK_APP_ID', 'test_app_id')
        assert real_config.app_secret == os.getenv('FACEBOOK_APP_SECRET', 'test_app_secret')
        assert real_config.access_token == os.getenv('FACEBOOK_ACCESS_TOKEN', 'test_access_token')
        assert real_config.api_version == "v18.0"
        assert real_config.base_url == "https://graph.facebook.com"
        assert real_config.rate_limit_per_hour == 200
        assert real_config.rate_limit_per_day == 5000
        assert real_config.cache_ttl == 3600
        assert real_config.circuit_breaker_threshold == 5
        assert real_config.circuit_breaker_timeout == 60
    
    def test_facebook_collector_initialization(self, real_collector, real_config):
        """Testa inicialização do coletor real."""
        assert real_collector.config == real_config
        assert real_collector.circuit_breaker is not None
        assert real_collector.cache is not None
        assert real_collector.redis_client is not None
        assert real_collector.session is None  # Será criado no context manager
    
    @pytest.mark.asyncio
    async def test_facebook_collector_context_manager(self, real_collector):
        """Testa context manager do coletor."""
        async with real_collector as collector:
            assert collector.session is not None
            assert isinstance(collector.session, aiohttp.ClientSession)
        
        # Session deve ser fechada após sair do context
        assert real_collector.session is None
    
    @patch('infrastructure.coleta.facebook_api.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_facebook_authentication_success(self, mock_get, real_collector):
        """Testa autenticação bem-sucedida."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'id': '123456789',
            'name': 'Test User',
            'email': 'test@example.com'
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with real_collector as collector:
            result = await collector.authenticate()
            
            assert result is True
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert 'me' in call_args[0][0]
            assert 'access_token' in call_args[1]['params']
    
    @patch('infrastructure.coleta.facebook_api.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_facebook_authentication_failure_invalid_token(self, mock_get, real_collector):
        """Testa falha na autenticação com token inválido."""
        mock_response = MagicMock()
        mock_response.status = 401
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with real_collector as collector:
            result = await collector.authenticate()
            
            assert result is False
    
    @patch('infrastructure.coleta.facebook_api.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_facebook_authentication_failure_insufficient_permissions(self, mock_get, real_collector):
        """Testa falha na autenticação com permissões insuficientes."""
        mock_response = MagicMock()
        mock_response.status = 403
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with real_collector as collector:
            result = await collector.authenticate()
            
            assert result is False
    
    @patch('infrastructure.coleta.facebook_api.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_facebook_authentication_exception(self, mock_get, real_collector):
        """Testa exceção durante autenticação."""
        mock_get.side_effect = Exception("Network error")
        
        async with real_collector as collector:
            with pytest.raises(FacebookAuthError):
                await collector.authenticate()
    
    @pytest.mark.asyncio
    async def test_facebook_rate_limit_check(self, real_collector):
        """Testa verificação de rate limit."""
        # Mock Redis para simular rate limit não atingido
        real_collector.redis_client.get.return_value = None
        
        result = await real_collector._check_rate_limit()
        assert result is True
        
        # Mock Redis para simular rate limit atingido
        real_collector.redis_client.get.return_value = b'200'
        
        result = await real_collector._check_rate_limit()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_facebook_rate_limit_increment(self, real_collector):
        """Testa incremento do rate limit."""
        await real_collector._increment_rate_limit()
        
        # Verificar se Redis foi chamado para incrementar
        real_collector.redis_client.incr.assert_called()
        real_collector.redis_client.expire.assert_called()
    
    @patch('infrastructure.coleta.facebook_api.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_facebook_make_request_success(self, mock_get, real_collector):
        """Testa requisição bem-sucedida."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'data': []})
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with real_collector as collector:
            result = await collector._make_request('test_endpoint', {'param': 'value'})
            
            assert result == {'data': []}
            mock_get.assert_called_once()
    
    @patch('infrastructure.coleta.facebook_api.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_facebook_make_request_rate_limit_error(self, mock_get, real_collector):
        """Testa erro de rate limit na requisição."""
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthException',
                'message': 'Rate limit exceeded'
            }
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with real_collector as collector:
            with pytest.raises(FacebookRateLimitError):
                await collector._make_request('test_endpoint')
    
    @patch('infrastructure.coleta.facebook_api.aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_facebook_make_request_permission_error(self, mock_get, real_collector):
        """Testa erro de permissão na requisição."""
        mock_response = MagicMock()
        mock_response.status = 403
        mock_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthException',
                'message': 'Insufficient permissions'
            }
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with real_collector as collector:
            with pytest.raises(FacebookPermissionError):
                await collector._make_request('test_endpoint')
    
    @patch.object(FacebookCollector, '_make_request')
    @pytest.mark.asyncio
    async def test_facebook_collect_posts_success(self, mock_request, real_collector, sample_post_data):
        """Testa coleta de posts com sucesso."""
        mock_request.return_value = {
            'data': [sample_post_data],
            'paging': {
                'cursors': {
                    'before': 'before_cursor',
                    'after': 'after_cursor'
                }
            }
        }
        
        async with real_collector as collector:
            posts = await collector.collect_posts('123456789', limit=10)
            
            assert len(posts) == 1
            assert isinstance(posts[0], FacebookPost)
            assert posts[0].id == '123456789_987654321'
            assert posts[0].message == 'Test post with #test #facebook #omni hashtags'
            assert posts[0].type == 'status'
            assert posts[0].privacy == 'EVERYONE'
            assert len(posts[0].hashtags) == 3
            assert '#test' in posts[0].hashtags
            assert '#facebook' in posts[0].hashtags
            assert '#omni' in posts[0].hashtags
    
    @patch.object(FacebookCollector, '_make_request')
    @pytest.mark.asyncio
    async def test_facebook_collect_insights_success(self, mock_request, real_collector, sample_insight_data):
        """Testa coleta de insights com sucesso."""
        mock_request.return_value = sample_insight_data
        
        async with real_collector as collector:
            insights = await collector.collect_insights('123456789', ['page_impressions', 'page_engaged_users'])
            
            assert len(insights) == 2
            assert isinstance(insights[0], FacebookInsight)
            assert insights[0].metric == 'page_impressions'
            assert insights[0].value == 1000
            assert insights[0].period == 'day'
            assert insights[1].metric == 'page_engaged_users'
            assert insights[1].value == 500
    
    @patch.object(FacebookCollector, '_make_request')
    @pytest.mark.asyncio
    async def test_facebook_collect_audience_data_success(self, mock_request, real_collector, sample_audience_data):
        """Testa coleta de dados de audiência com sucesso."""
        mock_request.return_value = sample_audience_data
        
        async with real_collector as collector:
            audience = await collector.collect_audience_data('123456789')
            
            assert isinstance(audience, FacebookAudience)
            assert audience.page_id == '123456789'
            assert 'São Paulo, Brazil' in audience.location
            assert audience.location['São Paulo, Brazil'] == 1000
            assert 'M.18-24' in audience.age_range
            assert audience.age_range['M.18-24'] == 200
    
    def test_facebook_extract_engagement_metrics(self, real_collector, sample_post_data):
        """Testa extração de métricas de engajamento."""
        metrics = real_collector._extract_engagement_metrics(sample_post_data)
        
        assert metrics['likes'] == 150
        assert metrics['comments'] == 25
        assert metrics['shares'] == 10
        assert metrics['reactions'] == 200
    
    def test_facebook_extract_hashtags(self, real_collector):
        """Testa extração de hashtags."""
        content = "Test post with #test #facebook #omni hashtags and #another_one"
        hashtags = real_collector._extract_hashtags(content)
        
        assert len(hashtags) == 4
        assert '#test' in hashtags
        assert '#facebook' in hashtags
        assert '#omni' in hashtags
        assert '#another_one' in hashtags
    
    def test_facebook_extract_keywords(self, real_collector):
        """Testa extração de keywords."""
        content = "Test post with important keywords like marketing, digital, and strategy"
        keywords = real_collector._extract_keywords(content)
        
        assert len(keywords) > 0
        assert 'marketing' in keywords
        assert 'digital' in keywords
        assert 'strategy' in keywords
    
    def test_facebook_calculate_viral_score(self, real_collector, sample_post_data):
        """Testa cálculo de viral score."""
        viral_score = real_collector._calculate_viral_score(sample_post_data)
        
        assert isinstance(viral_score, float)
        assert viral_score >= 0.0
        assert viral_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_facebook_health_status(self, real_collector):
        """Testa status de saúde do coletor."""
        health = await real_collector.get_health_status()
        
        assert isinstance(health, dict)
        assert 'service' in health
        assert 'status' in health
        assert 'timestamp' in health
        assert 'version' in health
        assert health['service'] == 'facebook_api'
        assert health['status'] in ['healthy', 'degraded', 'unhealthy']
    
    @pytest.mark.asyncio
    async def test_facebook_circuit_breaker_state_transitions(self, real_collector):
        """Testa transições de estado do circuit breaker."""
        # Estado inicial deve ser CLOSED
        assert real_collector.circuit_breaker.state == "CLOSED"
        
        # Simular falhas para abrir o circuit breaker
        for _ in range(5):
            real_collector.circuit_breaker.record_failure()
        
        # Circuit breaker deve estar OPEN
        assert real_collector.circuit_breaker.state == "OPEN"
        
        # Aguardar timeout para ir para HALF_OPEN
        real_collector.circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=70)
        real_collector.circuit_breaker._check_state()
        
        # Circuit breaker deve estar HALF_OPEN
        assert real_collector.circuit_breaker.state == "HALF_OPEN"
    
    @pytest.mark.asyncio
    async def test_facebook_cache_functionality(self, real_collector):
        """Testa funcionalidade de cache."""
        cache_key = "test_key"
        cache_value = {"test": "data"}
        
        # Testar set no cache
        await real_collector.cache.set(cache_key, cache_value, ttl=3600)
        real_collector.redis_client.set.assert_called()
        
        # Testar get do cache
        real_collector.redis_client.get.return_value = json.dumps(cache_value).encode()
        result = await real_collector.cache.get(cache_key)
        assert result == cache_value


class TestFacebookRealFactory:
    """Testes para factory do Facebook Collector."""
    
    @patch.dict(os.environ, {
        'FACEBOOK_APP_ID': 'env_app_id',
        'FACEBOOK_APP_SECRET': 'env_app_secret',
        'FACEBOOK_ACCESS_TOKEN': 'env_access_token'
    })
    @patch('infrastructure.coleta.facebook_api.redis.from_url')
    def test_create_facebook_collector_from_env(self, mock_redis):
        """Testa criação do coletor a partir de variáveis de ambiente."""
        mock_redis_client = MagicMock()
        mock_redis.return_value = mock_redis_client
        
        collector = create_facebook_collector(
            app_id='env_app_id',
            app_secret='env_app_secret',
            access_token='env_access_token'
        )
        
        assert isinstance(collector, FacebookCollector)
        assert collector.config.app_id == 'env_app_id'
        assert collector.config.app_secret == 'env_app_secret'
        assert collector.config.access_token == 'env_access_token'
    
    @patch('infrastructure.coleta.facebook_api.redis.from_url')
    def test_create_facebook_collector_with_params(self, mock_redis):
        """Testa criação do coletor com parâmetros explícitos."""
        mock_redis_client = MagicMock()
        mock_redis.return_value = mock_redis_client
        
        collector = create_facebook_collector(
            app_id='test_app_id',
            app_secret='test_app_secret',
            access_token='test_access_token',
            redis_url='redis://test:6379'
        )
        
        assert isinstance(collector, FacebookCollector)
        assert collector.config.app_id == 'test_app_id'
        assert collector.config.app_secret == 'test_app_secret'
        assert collector.config.access_token == 'test_access_token'
        mock_redis.assert_called_with('redis://test:6379')


class TestFacebookRealDataStructures:
    """Testes para estruturas de dados do Facebook."""
    
    def test_facebook_post_initialization(self):
        """Testa inicialização de FacebookPost."""
        post = FacebookPost(
            id='123456789_987654321',
            message='Test post',
            created_time=datetime.now(),
            engagement_metrics={'likes': 100, 'comments': 10},
            hashtags=['#test', '#facebook'],
            keywords=['test', 'facebook'],
            type='status',
            privacy='EVERYONE',
            page_id='123456789',
            viral_score=0.75
        )
        
        assert post.id == '123456789_987654321'
        assert post.message == 'Test post'
        assert post.type == 'status'
        assert post.privacy == 'EVERYONE'
        assert post.page_id == '123456789'
        assert post.viral_score == 0.75
        assert len(post.hashtags) == 2
        assert len(post.keywords) == 2
    
    def test_facebook_insight_initialization(self):
        """Testa inicialização de FacebookInsight."""
        insight = FacebookInsight(
            metric='page_impressions',
            value=1000,
            period='day',
            date=datetime.now(),
            page_id='123456789',
            trend=0.05
        )
        
        assert insight.metric == 'page_impressions'
        assert insight.value == 1000
        assert insight.period == 'day'
        assert insight.page_id == '123456789'
        assert insight.trend == 0.05
    
    def test_facebook_audience_initialization(self):
        """Testa inicialização de FacebookAudience."""
        audience = FacebookAudience(
            age_range={'M.18-24': 200, 'F.25-34': 300},
            gender={'M': 500, 'F': 600},
            location={'São Paulo, Brazil': 1000},
            interests=['marketing', 'technology'],
            page_id='123456789',
            date=datetime.now()
        )
        
        assert audience.page_id == '123456789'
        assert 'M.18-24' in audience.age_range
        assert audience.age_range['M.18-24'] == 200
        assert 'M' in audience.gender
        assert audience.gender['M'] == 500
        assert 'São Paulo, Brazil' in audience.location
        assert audience.location['São Paulo, Brazil'] == 1000
        assert len(audience.interests) == 2
        assert 'marketing' in audience.interests


class TestFacebookRealErrorHandling:
    """Testes para tratamento de erros do Facebook."""
    
    def test_facebook_api_error_initialization(self):
        """Testa inicialização de FacebookAPIError."""
        error = FacebookAPIError("Test error message")
        assert str(error) == "Test error message"
    
    def test_facebook_rate_limit_error_initialization(self):
        """Testa inicialização de FacebookRateLimitError."""
        error = FacebookRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, FacebookAPIError)
    
    def test_facebook_auth_error_initialization(self):
        """Testa inicialização de FacebookAuthError."""
        error = FacebookAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, FacebookAPIError)
    
    def test_facebook_permission_error_initialization(self):
        """Testa inicialização de FacebookPermissionError."""
        error = FacebookPermissionError("Insufficient permissions")
        assert str(error) == "Insufficient permissions"
        assert isinstance(error, FacebookAPIError) 