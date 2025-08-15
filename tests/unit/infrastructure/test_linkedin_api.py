#!/usr/bin/env python3
"""
Testes Unitários - LinkedIn API
==============================

Tracing ID: TEST_LINKEDIN_API_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/linkedin_api.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 4.5
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json
import os
import asyncio
import redis.asyncio as redis

from infrastructure.coleta.linkedin_api import (
    LinkedInCollector, LinkedInConfig, LinkedInPost, LinkedInTrend,
    LinkedInAPIError, LinkedInRateLimitError, LinkedInAuthError,
    create_linkedin_collector
)


class TestLinkedInAPI:
    @pytest.fixture
    def linkedin_config(self):
        return LinkedInConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://example.com/callback"
        )

    @pytest.fixture
    def mock_redis_client(self):
        return AsyncMock(spec=redis.Redis)

    @pytest.fixture
    def linkedin_collector(self, linkedin_config, mock_redis_client):
        return LinkedInCollector(linkedin_config, mock_redis_client)

    def test_linkedin_config_dataclass(self):
        """Testa criação de objeto LinkedInConfig."""
        config = LinkedInConfig(
            client_id="client123",
            client_secret="secret123",
            redirect_uri="https://app.com/callback",
            api_version="v2",
            rate_limit_per_minute=100,
            rate_limit_per_day=5000
        )
        assert config.client_id == "client123"
        assert config.client_secret == "secret123"
        assert config.redirect_uri == "https://app.com/callback"
        assert config.api_version == "v2"
        assert config.rate_limit_per_minute == 100
        assert config.rate_limit_per_day == 5000

    def test_linkedin_post_dataclass(self):
        """Testa criação de objeto LinkedInPost."""
        post = LinkedInPost(
            id="post123",
            author_id="user123",
            content="Test LinkedIn post content",
            created_time=datetime.now(),
            engagement_metrics={"likes": 25, "comments": 10, "shares": 5},
            hashtags=["#linkedin", "#test"],
            keywords=["linkedin", "test", "post"],
            language="en",
            visibility="PUBLIC"
        )
        assert post.id == "post123"
        assert post.content == "Test LinkedIn post content"
        assert post.language == "en"
        assert post.visibility == "PUBLIC"
        assert len(post.hashtags) == 2

    def test_linkedin_trend_dataclass(self):
        """Testa criação de objeto LinkedInTrend."""
        trend = LinkedInTrend(
            keyword="artificial intelligence",
            frequency=500,
            growth_rate=0.25,
            industry="technology",
            region="global",
            timestamp=datetime.now()
        )
        assert trend.keyword == "artificial intelligence"
        assert trend.frequency == 500
        assert trend.growth_rate == 0.25
        assert trend.industry == "technology"
        assert trend.region == "global"

    def test_linkedin_api_error(self):
        """Testa criação de exceção customizada."""
        error = LinkedInAPIError("Test error")
        assert str(error) == "Test error"

    def test_linkedin_rate_limit_error(self):
        """Testa criação de exceção de rate limit."""
        error = LinkedInRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, LinkedInAPIError)

    def test_linkedin_auth_error(self):
        """Testa criação de exceção de autenticação."""
        error = LinkedInAuthError("Invalid credentials")
        assert str(error) == "Invalid credentials"
        assert isinstance(error, LinkedInAPIError)

    def test_linkedin_collector_initialization(self, linkedin_config, mock_redis_client):
        """Testa inicialização do LinkedInCollector."""
        collector = LinkedInCollector(linkedin_config, mock_redis_client)
        assert collector.config == linkedin_config
        assert collector.redis_client == mock_redis_client
        assert collector.request_count == 0
        assert collector.session is None
        assert collector.access_token is None
        assert collector.token_expires_at is None

    @pytest.mark.asyncio
    async def test_context_manager(self, linkedin_collector):
        """Testa uso como context manager."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            async with linkedin_collector as collector:
                assert collector.session == mock_session
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_with_valid_token(self, linkedin_collector):
        """Testa autenticação com token válido."""
        linkedin_collector.access_token = "valid_token"
        linkedin_collector.token_expires_at = datetime.now() + timedelta(hours=1)
        
        result = await linkedin_collector.authenticate()
        assert result is True

    @pytest.mark.asyncio
    async def test_authenticate_with_expired_token(self, linkedin_collector):
        """Testa autenticação com token expirado."""
        linkedin_collector.access_token = "expired_token"
        linkedin_collector.token_expires_at = datetime.now() - timedelta(hours=1)
        
        result = await linkedin_collector.authenticate()
        assert result is True
        assert linkedin_collector.access_token == "simulated_access_token"

    @pytest.mark.asyncio
    async def test_authenticate_without_token(self, linkedin_collector):
        """Testa autenticação sem token."""
        result = await linkedin_collector.authenticate()
        assert result is True
        assert linkedin_collector.access_token == "simulated_access_token"
        assert linkedin_collector.token_expires_at is not None

    @pytest.mark.asyncio
    async def test_authenticate_exception(self, linkedin_collector):
        """Testa autenticação com exceção."""
        with patch.object(linkedin_collector, 'access_token', side_effect=Exception("Auth error")):
            with pytest.raises(LinkedInAuthError, match="Falha na autenticação"):
                await linkedin_collector.authenticate()

    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, linkedin_collector):
        """Testa verificação de rate limit bem-sucedida."""
        linkedin_collector.mock_redis_client.get.return_value = "50"
        
        result = await linkedin_collector._check_rate_limit()
        assert result is True

    @pytest.mark.asyncio
    async def test_check_rate_limit_minute_exceeded(self, linkedin_collector):
        """Testa rate limit por minuto excedido."""
        linkedin_collector.mock_redis_client.get.return_value = "120"
        
        result = await linkedin_collector._check_rate_limit()
        assert result is False

    @pytest.mark.asyncio
    async def test_check_rate_limit_day_exceeded(self, linkedin_collector):
        """Testa rate limit diário excedido."""
        linkedin_collector.request_count = 6000
        linkedin_collector.mock_redis_client.get.return_value = "50"
        
        result = await linkedin_collector._check_rate_limit()
        assert result is False

    @pytest.mark.asyncio
    async def test_increment_rate_limit(self, linkedin_collector):
        """Testa incremento de rate limit."""
        await linkedin_collector._increment_rate_limit()
        
        linkedin_collector.mock_redis_client.incr.assert_called_once()
        linkedin_collector.mock_redis_client.expire.assert_called_once_with(
            linkedin_collector.mock_redis_client.incr.return_value, 60
        )
        assert linkedin_collector.request_count == 1

    @pytest.mark.asyncio
    async def test_make_request_success(self, linkedin_collector):
        """Testa requisição bem-sucedida."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})
        mock_session.get.return_value.__aenter__.return_value = mock_response
        linkedin_collector.session = mock_session
        linkedin_collector.access_token = "test_token"
        
        with patch.object(linkedin_collector, '_check_rate_limit', return_value=True):
            with patch.object(linkedin_collector, '_increment_rate_limit'):
                with patch.object(linkedin_collector.circuit_breaker, 'can_execute', return_value=True):
                    with patch.object(linkedin_collector.circuit_breaker, 'on_success'):
                        result = await linkedin_collector._make_request("test/endpoint")
                        assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_exceeded(self, linkedin_collector):
        """Testa requisição com rate limit excedido."""
        with patch.object(linkedin_collector, '_check_rate_limit', return_value=False):
            with pytest.raises(LinkedInRateLimitError, match="Rate limit atingido"):
                await linkedin_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_circuit_breaker_open(self, linkedin_collector):
        """Testa requisição com circuit breaker aberto."""
        with patch.object(linkedin_collector, '_check_rate_limit', return_value=True):
            with patch.object(linkedin_collector.circuit_breaker, 'can_execute', return_value=False):
                with pytest.raises(LinkedInAPIError, match="Circuit breaker aberto"):
                    await linkedin_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_api_error(self, linkedin_collector):
        """Testa requisição com erro da API."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_session.get.return_value.__aenter__.return_value = mock_response
        linkedin_collector.session = mock_session
        linkedin_collector.access_token = "test_token"
        
        with patch.object(linkedin_collector, '_check_rate_limit', return_value=True):
            with patch.object(linkedin_collector, '_increment_rate_limit'):
                with patch.object(linkedin_collector.circuit_breaker, 'can_execute', return_value=True):
                    with patch.object(linkedin_collector.circuit_breaker, 'on_failure'):
                        with pytest.raises(LinkedInAPIError, match="Erro da API: 400"):
                            await linkedin_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_collect_posts_success(self, linkedin_collector):
        """Testa coleta de posts bem-sucedida."""
        mock_posts = [
            LinkedInPost(
                id="post1",
                author_id="user1",
                content="Test LinkedIn post",
                created_time=datetime.now(),
                engagement_metrics={"likes": 10, "comments": 5},
                hashtags=["#linkedin"],
                keywords=["linkedin", "test"],
                language="en",
                visibility="PUBLIC"
            )
        ]
        
        with patch.object(linkedin_collector.cache, 'get', return_value=None):
            with patch.object(linkedin_collector, '_make_request', return_value={
                "elements": [{
                    "id": "post1",
                    "author": {"id": "user1"},
                    "content": {
                        "text": "Test LinkedIn post",
                        "locale": {"language": "en"}
                    },
                    "created": {"time": "2023-01-01T00:00:00"},
                    "visibility": "PUBLIC",
                    "socialActivity": {
                        "totalSocialActivity": 10,
                        "commentCount": 5,
                        "shareCount": 2
                    }
                }]
            }):
                with patch.object(linkedin_collector.cache, 'set'):
                    posts = await linkedin_collector.collect_posts(["linkedin"])
                    assert len(posts) == 1
                    assert posts[0].id == "post1"
                    assert posts[0].content == "Test LinkedIn post"

    @pytest.mark.asyncio
    async def test_collect_posts_from_cache(self, linkedin_collector):
        """Testa coleta de posts do cache."""
        cached_posts = [
            LinkedInPost(
                id="post1",
                author_id="user1",
                content="Cached post",
                created_time=datetime.now(),
                engagement_metrics={},
                hashtags=[],
                keywords=[],
                language="en",
                visibility="PUBLIC"
            )
        ]
        
        with patch.object(linkedin_collector.cache, 'get', return_value=cached_posts):
            posts = await linkedin_collector.collect_posts(["linkedin"])
            assert posts == cached_posts

    @pytest.mark.asyncio
    async def test_collect_trends_success(self, linkedin_collector):
        """Testa coleta de tendências bem-sucedida."""
        sample_posts = [
            LinkedInPost(
                id="post1",
                author_id="user1",
                content="AI is trending",
                created_time=datetime.now(),
                engagement_metrics={},
                hashtags=[],
                keywords=["ai", "trending"],
                language="en",
                visibility="PUBLIC"
            )
        ]
        
        with patch.object(linkedin_collector.cache, 'get', return_value=None):
            with patch.object(linkedin_collector, 'collect_posts', return_value=sample_posts):
                with patch.object(linkedin_collector.cache, 'set'):
                    trends = await linkedin_collector.collect_trends("technology", "global")
                    assert len(trends) == 2
                    assert trends[0].keyword == "ai"
                    assert trends[0].industry == "technology"
                    assert trends[0].region == "global"

    @pytest.mark.asyncio
    async def test_collect_trends_from_cache(self, linkedin_collector):
        """Testa coleta de tendências do cache."""
        cached_trends = [
            LinkedInTrend(
                keyword="ai",
                frequency=100,
                growth_rate=0.5,
                industry="technology",
                region="global",
                timestamp=datetime.now()
            )
        ]
        
        with patch.object(linkedin_collector.cache, 'get', return_value=cached_trends):
            trends = await linkedin_collector.collect_trends()
            assert trends == cached_trends

    def test_extract_engagement_metrics(self, linkedin_collector):
        """Testa extração de métricas de engajamento."""
        post_data = {
            "socialActivity": {
                "totalSocialActivity": 50,
                "commentCount": 10,
                "shareCount": 5
            }
        }
        
        metrics = linkedin_collector._extract_engagement_metrics(post_data)
        assert metrics["likes"] == 50
        assert metrics["comments"] == 10
        assert metrics["shares"] == 5

    def test_extract_hashtags(self, linkedin_collector):
        """Testa extração de hashtags."""
        content = "This is a #linkedin post about #business and #networking"
        hashtags = linkedin_collector._extract_hashtags(content)
        assert "#linkedin" in hashtags
        assert "#business" in hashtags
        assert "#networking" in hashtags

    def test_extract_keywords(self, linkedin_collector):
        """Testa extração de keywords."""
        content = "This is a professional post about business development and networking"
        keywords = linkedin_collector._extract_keywords(content)
        assert "professional" in keywords
        assert "business" in keywords
        assert "development" in keywords
        assert "networking" in keywords

    def test_calculate_growth_rate(self, linkedin_collector):
        """Testa cálculo de taxa de crescimento."""
        growth_rate = linkedin_collector._calculate_growth_rate("test_keyword")
        assert 0.1 <= growth_rate <= 2.0

    @pytest.mark.asyncio
    async def test_get_health_status(self, linkedin_collector):
        """Testa obtenção de status de saúde."""
        with patch.object(linkedin_collector.circuit_breaker, 'is_closed', return_value=True):
            with patch.object(linkedin_collector.cache, 'get_hit_ratio', return_value=0.85):
                health = await linkedin_collector.get_health_status()
                assert health["service"] == "linkedin_api"
                assert health["status"] == "healthy"
                assert health["cache_hit_ratio"] == 0.85
                assert health["tracing_id"] == "INT_001_LINKEDIN_2025_001"

    @pytest.mark.asyncio
    async def test_create_linkedin_collector(self):
        """Testa função factory."""
        with patch('redis.asyncio.from_url') as mock_redis_from_url:
            mock_redis_client = AsyncMock()
            mock_redis_from_url.return_value = mock_redis_client
            
            with patch('infrastructure.coleta.linkedin_api.LinkedInCollector') as mock_collector_class:
                mock_collector = AsyncMock()
                mock_collector_class.return_value = mock_collector
                mock_collector.authenticate.return_value = True
                
                result = await create_linkedin_collector(
                    client_id="test_client",
                    client_secret="test_secret",
                    redirect_uri="https://app.com/callback"
                )
                
                assert result == mock_collector
                mock_collector.authenticate.assert_called_once()

    def test_edge_cases(self, linkedin_collector):
        """Testa casos edge."""
        # Teste de extração de hashtags com conteúdo vazio
        hashtags = linkedin_collector._extract_hashtags("")
        assert hashtags == []
        
        # Teste de extração de keywords com conteúdo vazio
        keywords = linkedin_collector._extract_keywords("")
        assert keywords == []
        
        # Teste de métricas de engajamento com dados vazios
        post_data = {}
        metrics = linkedin_collector._extract_engagement_metrics(post_data)
        assert metrics["likes"] == 0
        assert metrics["comments"] == 0
        assert metrics["shares"] == 0

    @pytest.mark.asyncio
    async def test_collect_posts_error_handling(self, linkedin_collector):
        """Testa tratamento de erro na coleta de posts."""
        with patch.object(linkedin_collector.cache, 'get', return_value=None):
            with patch.object(linkedin_collector, '_make_request', side_effect=LinkedInAPIError("API Error")):
                posts = await linkedin_collector.collect_posts(["error_keyword"])
                assert posts == []

    @pytest.mark.asyncio
    async def test_collect_trends_error_handling(self, linkedin_collector):
        """Testa tratamento de erro na coleta de tendências."""
        with patch.object(linkedin_collector.cache, 'get', return_value=None):
            with patch.object(linkedin_collector, 'collect_posts', side_effect=LinkedInAPIError("API Error")):
                trends = await linkedin_collector.collect_trends()
                assert trends == []

    def test_keyword_extraction_with_stop_words(self, linkedin_collector):
        """Testa extração de keywords filtrando stop words."""
        content = "The and or but in on at to for of with by business development"
        keywords = linkedin_collector._extract_keywords(content)
        assert "the" not in keywords
        assert "and" not in keywords
        assert "business" in keywords
        assert "development" in keywords

    def test_hashtag_extraction_with_special_characters(self, linkedin_collector):
        """Testa extração de hashtags com caracteres especiais."""
        content = "Post about #AI-ML #data_science #cloud-computing"
        hashtags = linkedin_collector._extract_hashtags(content)
        assert "#AI-ML" in hashtags
        assert "#data_science" in hashtags
        assert "#cloud-computing" in hashtags


if __name__ == "__main__":
    pytest.main([__file__]) 