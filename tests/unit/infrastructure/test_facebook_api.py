#!/usr/bin/env python3
"""
Testes Unitários - Facebook API
==============================

Tracing ID: TEST_FACEBOOK_API_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/facebook_api.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 4.3
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json
import os
import asyncio
import redis.asyncio as redis

from infrastructure.coleta.facebook_api import (
    FacebookCollector, FacebookConfig, FacebookPost, FacebookInsight,
    FacebookAudience, FacebookAPIError, FacebookRateLimitError,
    FacebookAuthError, FacebookPermissionError, create_facebook_collector
)


class TestFacebookAPI:
    @pytest.fixture
    def facebook_config(self):
        return FacebookConfig(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_access_token"
        )

    @pytest.fixture
    def mock_redis_client(self):
        return AsyncMock(spec=redis.Redis)

    @pytest.fixture
    def facebook_collector(self, facebook_config, mock_redis_client):
        return FacebookCollector(facebook_config, mock_redis_client)

    def test_facebook_config_dataclass(self):
        """Testa criação de objeto FacebookConfig."""
        config = FacebookConfig(
            app_id="app123",
            app_secret="secret123",
            access_token="token123",
            api_version="v18.0",
            rate_limit_per_hour=200,
            rate_limit_per_day=5000
        )
        assert config.app_id == "app123"
        assert config.app_secret == "secret123"
        assert config.access_token == "token123"
        assert config.api_version == "v18.0"
        assert config.rate_limit_per_hour == 200
        assert config.rate_limit_per_day == 5000

    def test_facebook_post_dataclass(self):
        """Testa criação de objeto FacebookPost."""
        post = FacebookPost(
            id="post123",
            message="Test post message",
            created_time=datetime.now(),
            engagement_metrics={"impressions": 1000, "engagements": 100},
            hashtags=["#test", "#facebook"],
            keywords=["test", "post", "message"],
            type="status",
            privacy="public",
            page_id="page123",
            viral_score=0.1
        )
        assert post.id == "post123"
        assert post.message == "Test post message"
        assert post.type == "status"
        assert post.viral_score == 0.1
        assert len(post.hashtags) == 2

    def test_facebook_insight_dataclass(self):
        """Testa criação de objeto FacebookInsight."""
        insight = FacebookInsight(
            metric="page_impressions",
            value=1000,
            period="day",
            date=datetime.now(),
            page_id="page123",
            trend=0.05
        )
        assert insight.metric == "page_impressions"
        assert insight.value == 1000
        assert insight.period == "day"
        assert insight.trend == 0.05

    def test_facebook_audience_dataclass(self):
        """Testa criação de objeto FacebookAudience."""
        audience = FacebookAudience(
            age_range={"18-24": 100, "25-34": 200},
            gender={"male": 150, "female": 150},
            location={"US": 200, "BR": 100},
            interests=["technology", "business"],
            page_id="page123",
            date=datetime.now()
        )
        assert audience.age_range["18-24"] == 100
        assert audience.gender["male"] == 150
        assert len(audience.interests) == 2

    def test_facebook_api_error(self):
        """Testa criação de exceção customizada."""
        error = FacebookAPIError("Test error")
        assert str(error) == "Test error"

    def test_facebook_rate_limit_error(self):
        """Testa criação de exceção de rate limit."""
        error = FacebookRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, FacebookAPIError)

    def test_facebook_auth_error(self):
        """Testa criação de exceção de autenticação."""
        error = FacebookAuthError("Invalid token")
        assert str(error) == "Invalid token"
        assert isinstance(error, FacebookAPIError)

    def test_facebook_permission_error(self):
        """Testa criação de exceção de permissão."""
        error = FacebookPermissionError("Insufficient permissions")
        assert str(error) == "Insufficient permissions"
        assert isinstance(error, FacebookAPIError)

    def test_facebook_collector_initialization(self, facebook_config, mock_redis_client):
        """Testa inicialização do FacebookCollector."""
        collector = FacebookCollector(facebook_config, mock_redis_client)
        assert collector.config == facebook_config
        assert collector.redis_client == mock_redis_client
        assert collector.request_count == 0
        assert collector.session is None

    @pytest.mark.asyncio
    async def test_context_manager(self, facebook_collector):
        """Testa uso como context manager."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            async with facebook_collector as collector:
                assert collector.session == mock_session
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, facebook_collector):
        """Testa autenticação bem-sucedida."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"name": "Test User"})
        mock_session.get.return_value.__aenter__.return_value = mock_response
        facebook_collector.session = mock_session
        
        result = await facebook_collector.authenticate()
        assert result is True

    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, facebook_collector):
        """Testa autenticação com token inválido."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_session.get.return_value.__aenter__.return_value = mock_response
        facebook_collector.session = mock_session
        
        result = await facebook_collector.authenticate()
        assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_insufficient_permissions(self, facebook_collector):
        """Testa autenticação com permissões insuficientes."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_session.get.return_value.__aenter__.return_value = mock_response
        facebook_collector.session = mock_session
        
        result = await facebook_collector.authenticate()
        assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_exception(self, facebook_collector):
        """Testa autenticação com exceção."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("Network error")
        facebook_collector.session = mock_session
        
        with pytest.raises(FacebookAuthError, match="Falha na autenticação"):
            await facebook_collector.authenticate()

    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, facebook_collector):
        """Testa verificação de rate limit bem-sucedida."""
        facebook_collector.mock_redis_client.get.return_value = "50"
        
        result = await facebook_collector._check_rate_limit()
        assert result is True

    @pytest.mark.asyncio
    async def test_check_rate_limit_hour_exceeded(self, facebook_collector):
        """Testa rate limit por hora excedido."""
        facebook_collector.mock_redis_client.get.return_value = "250"
        
        result = await facebook_collector._check_rate_limit()
        assert result is False

    @pytest.mark.asyncio
    async def test_check_rate_limit_day_exceeded(self, facebook_collector):
        """Testa rate limit diário excedido."""
        facebook_collector.request_count = 6000
        facebook_collector.mock_redis_client.get.return_value = "50"
        
        result = await facebook_collector._check_rate_limit()
        assert result is False

    @pytest.mark.asyncio
    async def test_increment_rate_limit(self, facebook_collector):
        """Testa incremento de rate limit."""
        await facebook_collector._increment_rate_limit()
        
        facebook_collector.mock_redis_client.incr.assert_called_once()
        facebook_collector.mock_redis_client.expire.assert_called_once()
        assert facebook_collector.request_count == 1

    @pytest.mark.asyncio
    async def test_make_request_success(self, facebook_collector):
        """Testa requisição bem-sucedida."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})
        mock_session.get.return_value.__aenter__.return_value = mock_response
        facebook_collector.session = mock_session
        
        with patch.object(facebook_collector, '_check_rate_limit', return_value=True):
            with patch.object(facebook_collector, '_increment_rate_limit'):
                with patch.object(facebook_collector.circuit_breaker, 'can_execute', return_value=True):
                    with patch.object(facebook_collector.circuit_breaker, 'on_success'):
                        result = await facebook_collector._make_request("test/endpoint")
                        assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_exceeded(self, facebook_collector):
        """Testa requisição com rate limit excedido."""
        with patch.object(facebook_collector, '_check_rate_limit', return_value=False):
            with pytest.raises(FacebookRateLimitError, match="Rate limit atingido"):
                await facebook_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_circuit_breaker_open(self, facebook_collector):
        """Testa requisição com circuit breaker aberto."""
        with patch.object(facebook_collector, '_check_rate_limit', return_value=True):
            with patch.object(facebook_collector.circuit_breaker, 'can_execute', return_value=False):
                with pytest.raises(FacebookAPIError, match="Circuit breaker aberto"):
                    await facebook_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_http_errors(self, facebook_collector):
        """Testa requisição com diferentes erros HTTP."""
        mock_session = AsyncMock()
        facebook_collector.session = mock_session
        
        # Teste erro 429 (Rate Limit)
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(facebook_collector, '_check_rate_limit', return_value=True):
            with patch.object(facebook_collector, '_increment_rate_limit'):
                with patch.object(facebook_collector.circuit_breaker, 'can_execute', return_value=True):
                    with patch.object(facebook_collector.circuit_breaker, 'on_failure'):
                        with pytest.raises(FacebookRateLimitError, match="Rate limit da API atingido"):
                            await facebook_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_collect_posts_success(self, facebook_collector):
        """Testa coleta de posts bem-sucedida."""
        mock_posts = [
            FacebookPost(
                id="post1",
                message="Test post 1",
                created_time=datetime.now(),
                engagement_metrics={"impressions": 1000},
                hashtags=["#test"],
                keywords=["test"],
                type="status",
                privacy="public",
                page_id="page123",
                viral_score=0.1
            )
        ]
        
        with patch.object(facebook_collector.cache, 'get', return_value=None):
            with patch.object(facebook_collector, '_make_request', return_value={
                "data": [{
                    "id": "post1",
                    "message": "Test post 1",
                    "created_time": "2023-01-01T00:00:00+0000",
                    "type": "status",
                    "privacy": {"value": "public"},
                    "insights": {"data": []}
                }]
            }):
                with patch.object(facebook_collector.cache, 'set'):
                    posts = await facebook_collector.collect_posts("page123")
                    assert len(posts) == 1
                    assert posts[0].id == "post1"

    @pytest.mark.asyncio
    async def test_collect_posts_from_cache(self, facebook_collector):
        """Testa coleta de posts do cache."""
        cached_posts = [
            FacebookPost(
                id="post1",
                message="Cached post",
                created_time=datetime.now(),
                engagement_metrics={},
                hashtags=[],
                keywords=[],
                type="status",
                privacy="public",
                page_id="page123",
                viral_score=0.0
            )
        ]
        
        with patch.object(facebook_collector.cache, 'get', return_value=cached_posts):
            posts = await facebook_collector.collect_posts("page123")
            assert posts == cached_posts

    @pytest.mark.asyncio
    async def test_collect_insights_success(self, facebook_collector):
        """Testa coleta de insights bem-sucedida."""
        with patch.object(facebook_collector.cache, 'get', return_value=None):
            with patch.object(facebook_collector, '_make_request', return_value={
                "data": [{
                    "name": "page_impressions",
                    "period": "day",
                    "values": [{
                        "value": 1000,
                        "end_time": "2023-01-01T00:00:00+0000"
                    }]
                }]
            }):
                with patch.object(facebook_collector.cache, 'set'):
                    insights = await facebook_collector.collect_insights("page123")
                    assert len(insights) == 1
                    assert insights[0].metric == "page_impressions"
                    assert insights[0].value == 1000

    @pytest.mark.asyncio
    async def test_collect_audience_data_success(self, facebook_collector):
        """Testa coleta de dados de audiência bem-sucedida."""
        with patch.object(facebook_collector.cache, 'get', return_value=None):
            with patch.object(facebook_collector, '_make_request', return_value={
                "data": [{
                    "name": "page_fans_gender_age",
                    "values": [{
                        "value": {
                            "M.18-24": 100,
                            "F.25-34": 200
                        }
                    }]
                }]
            }):
                with patch.object(facebook_collector.cache, 'set'):
                    audience = await facebook_collector.collect_audience_data("page123")
                    assert audience is not None
                    assert audience.page_id == "page123"

    def test_extract_engagement_metrics(self, facebook_collector):
        """Testa extração de métricas de engajamento."""
        post_data = {
            "insights": {
                "data": [
                    {"name": "post_impressions", "values": [{"value": 1000}]},
                    {"name": "post_engagements", "values": [{"value": 100}]}
                ]
            }
        }
        
        metrics = facebook_collector._extract_engagement_metrics(post_data)
        assert metrics["impressions"] == 1000
        assert metrics["engagements"] == 100

    def test_extract_hashtags(self, facebook_collector):
        """Testa extração de hashtags."""
        content = "This is a #test post with #facebook #api"
        hashtags = facebook_collector._extract_hashtags(content)
        assert "#test" in hashtags
        assert "#facebook" in hashtags
        assert "#api" in hashtags

    def test_extract_keywords(self, facebook_collector):
        """Testa extração de keywords."""
        content = "This is a test post about technology and business"
        keywords = facebook_collector._extract_keywords(content)
        assert "test" in keywords
        assert "technology" in keywords
        assert "business" in keywords

    def test_calculate_viral_score(self, facebook_collector):
        """Testa cálculo de viral score."""
        post_data = {
            "insights": {
                "data": [
                    {"name": "post_impressions", "values": [{"value": 1000}]},
                    {"name": "post_engagements", "values": [{"value": 100}]}
                ]
            }
        }
        
        viral_score = facebook_collector._calculate_viral_score(post_data)
        assert viral_score == 0.1

    def test_calculate_viral_score_zero_impressions(self, facebook_collector):
        """Testa cálculo de viral score com zero impressões."""
        post_data = {
            "insights": {
                "data": [
                    {"name": "post_impressions", "values": [{"value": 0}]}
                ]
            }
        }
        
        viral_score = facebook_collector._calculate_viral_score(post_data)
        assert viral_score == 0.0

    def test_extract_age_range(self, facebook_collector):
        """Testa extração de faixa etária."""
        gender_age_data = {
            "M.18-24": 100,
            "F.25-34": 200,
            "M.35-44": 150
        }
        
        age_ranges = facebook_collector._extract_age_range(gender_age_data)
        assert age_ranges["18-24"] == 100
        assert age_ranges["25-34"] == 200
        assert age_ranges["35-44"] == 150

    def test_extract_gender(self, facebook_collector):
        """Testa extração de dados de gênero."""
        gender_age_data = {
            "M.18-24": 100,
            "F.25-34": 200,
            "U.35-44": 50
        }
        
        gender_data = facebook_collector._extract_gender(gender_age_data)
        assert gender_data["male"] == 100
        assert gender_data["female"] == 200
        assert gender_data["unknown"] == 50

    def test_extract_interests(self, facebook_collector):
        """Testa extração de interesses."""
        interests = facebook_collector._extract_interests("page123")
        assert "technology" in interests
        assert "business" in interests
        assert "marketing" in interests

    @pytest.mark.asyncio
    async def test_get_health_status(self, facebook_collector):
        """Testa obtenção de status de saúde."""
        with patch.object(facebook_collector.circuit_breaker, 'is_closed', return_value=True):
            with patch.object(facebook_collector.cache, 'get_hit_ratio', return_value=0.8):
                health = await facebook_collector.get_health_status()
                assert health["service"] == "facebook_api"
                assert health["status"] == "healthy"
                assert health["tracing_id"] == "INT_003_FACEBOOK_2025_001"

    @pytest.mark.asyncio
    async def test_create_facebook_collector(self):
        """Testa função factory."""
        with patch('redis.asyncio.from_url') as mock_redis_from_url:
            mock_redis_client = AsyncMock()
            mock_redis_from_url.return_value = mock_redis_client
            
            with patch('infrastructure.coleta.facebook_api.FacebookCollector') as mock_collector_class:
                mock_collector = AsyncMock()
                mock_collector_class.return_value = mock_collector
                mock_collector.authenticate.return_value = True
                
                result = await create_facebook_collector(
                    app_id="test_app",
                    app_secret="test_secret",
                    access_token="test_token"
                )
                
                assert result == mock_collector
                mock_collector.authenticate.assert_called_once()

    def test_edge_cases(self, facebook_collector):
        """Testa casos edge."""
        # Teste de extração de hashtags com conteúdo vazio
        hashtags = facebook_collector._extract_hashtags("")
        assert hashtags == []
        
        # Teste de extração de keywords com conteúdo vazio
        keywords = facebook_collector._extract_keywords("")
        assert keywords == []
        
        # Teste de extração de métricas sem insights
        metrics = facebook_collector._extract_engagement_metrics({})
        assert metrics["impressions"] == 0
        assert metrics["engagements"] == 0


if __name__ == "__main__":
    pytest.main([__file__]) 