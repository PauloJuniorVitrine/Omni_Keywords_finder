#!/usr/bin/env python3
"""
Testes Unitários - Twitter API
=============================

Tracing ID: TEST_TWITTER_API_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/twitter_api.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 4.4
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json
import os
import asyncio
import redis.asyncio as redis

from infrastructure.coleta.twitter_api import (
    TwitterCollector, TwitterConfig, TwitterTweet, TwitterTrend,
    TwitterHashtag, TwitterAPIError, TwitterRateLimitError,
    TwitterAuthError, TwitterStreamingError, create_twitter_collector
)


class TestTwitterAPI:
    @pytest.fixture
    def twitter_config(self):
        return TwitterConfig(
            api_key="test_api_key",
            api_secret="test_api_secret",
            bearer_token="test_bearer_token",
            access_token="test_access_token",
            access_token_secret="test_access_token_secret"
        )

    @pytest.fixture
    def mock_redis_client(self):
        return AsyncMock(spec=redis.Redis)

    @pytest.fixture
    def twitter_collector(self, twitter_config, mock_redis_client):
        return TwitterCollector(twitter_config, mock_redis_client)

    def test_twitter_config_dataclass(self):
        """Testa criação de objeto TwitterConfig."""
        config = TwitterConfig(
            api_key="key123",
            api_secret="secret123",
            bearer_token="bearer123",
            access_token="access123",
            access_token_secret="access_secret123",
            api_version="v2",
            rate_limit_per_15min=300,
            rate_limit_per_day=10000
        )
        assert config.api_key == "key123"
        assert config.bearer_token == "bearer123"
        assert config.api_version == "v2"
        assert config.rate_limit_per_15min == 300
        assert config.rate_limit_per_day == 10000

    def test_twitter_tweet_dataclass(self):
        """Testa criação de objeto TwitterTweet."""
        tweet = TwitterTweet(
            id="tweet123",
            text="Test tweet message",
            author_id="user123",
            created_at=datetime.now(),
            engagement_metrics={"retweets": 10, "likes": 50},
            hashtags=["#test", "#twitter"],
            keywords=["test", "tweet", "message"],
            language="en",
            is_retweet=False,
            is_quote=False,
            is_reply=False,
            viral_score=0.5
        )
        assert tweet.id == "tweet123"
        assert tweet.text == "Test tweet message"
        assert tweet.language == "en"
        assert tweet.viral_score == 0.5
        assert len(tweet.hashtags) == 2

    def test_twitter_trend_dataclass(self):
        """Testa criação de objeto TwitterTrend."""
        trend = TwitterTrend(
            keyword="#trending",
            frequency=1000,
            growth_rate=0.15,
            viral_score=0.8,
            hashtag=True,
            region="1",
            timestamp=datetime.now(),
            sentiment_score=0.2
        )
        assert trend.keyword == "#trending"
        assert trend.frequency == 1000
        assert trend.growth_rate == 0.15
        assert trend.hashtag is True
        assert trend.sentiment_score == 0.2

    def test_twitter_hashtag_dataclass(self):
        """Testa criação de objeto TwitterHashtag."""
        hashtag = TwitterHashtag(
            hashtag="#viral",
            frequency=500,
            reach=1000,
            engagement_rate=0.75,
            trending_score=0.9,
            timestamp=datetime.now()
        )
        assert hashtag.hashtag == "#viral"
        assert hashtag.frequency == 500
        assert hashtag.engagement_rate == 0.75
        assert hashtag.trending_score == 0.9

    def test_twitter_api_error(self):
        """Testa criação de exceção customizada."""
        error = TwitterAPIError("Test error")
        assert str(error) == "Test error"

    def test_twitter_rate_limit_error(self):
        """Testa criação de exceção de rate limit."""
        error = TwitterRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, TwitterAPIError)

    def test_twitter_auth_error(self):
        """Testa criação de exceção de autenticação."""
        error = TwitterAuthError("Invalid token")
        assert str(error) == "Invalid token"
        assert isinstance(error, TwitterAPIError)

    def test_twitter_streaming_error(self):
        """Testa criação de exceção de streaming."""
        error = TwitterStreamingError("Streaming failed")
        assert str(error) == "Streaming failed"
        assert isinstance(error, TwitterAPIError)

    def test_twitter_collector_initialization(self, twitter_config, mock_redis_client):
        """Testa inicialização do TwitterCollector."""
        collector = TwitterCollector(twitter_config, mock_redis_client)
        assert collector.config == twitter_config
        assert collector.redis_client == mock_redis_client
        assert collector.request_count == 0
        assert collector.session is None
        assert collector.is_streaming is False

    @pytest.mark.asyncio
    async def test_context_manager(self, twitter_collector):
        """Testa uso como context manager."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            async with twitter_collector as collector:
                assert collector.session == mock_session
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, twitter_collector):
        """Testa autenticação bem-sucedida."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.get.return_value.__aenter__.return_value = mock_response
        twitter_collector.session = mock_session
        
        result = await twitter_collector.authenticate()
        assert result is True

    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, twitter_collector):
        """Testa autenticação com token inválido."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_session.get.return_value.__aenter__.return_value = mock_response
        twitter_collector.session = mock_session
        
        result = await twitter_collector.authenticate()
        assert result is False

    @pytest.mark.asyncio
    async def test_authenticate_exception(self, twitter_collector):
        """Testa autenticação com exceção."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("Network error")
        twitter_collector.session = mock_session
        
        with pytest.raises(TwitterAuthError, match="Falha na autenticação"):
            await twitter_collector.authenticate()

    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, twitter_collector):
        """Testa verificação de rate limit bem-sucedida."""
        twitter_collector.mock_redis_client.get.return_value = "50"
        
        result = await twitter_collector._check_rate_limit()
        assert result is True

    @pytest.mark.asyncio
    async def test_check_rate_limit_15min_exceeded(self, twitter_collector):
        """Testa rate limit por 15 minutos excedido."""
        twitter_collector.mock_redis_client.get.return_value = "350"
        
        result = await twitter_collector._check_rate_limit()
        assert result is False

    @pytest.mark.asyncio
    async def test_check_rate_limit_day_exceeded(self, twitter_collector):
        """Testa rate limit diário excedido."""
        twitter_collector.request_count = 11000
        twitter_collector.mock_redis_client.get.return_value = "50"
        
        result = await twitter_collector._check_rate_limit()
        assert result is False

    @pytest.mark.asyncio
    async def test_increment_rate_limit(self, twitter_collector):
        """Testa incremento de rate limit."""
        await twitter_collector._increment_rate_limit()
        
        twitter_collector.mock_redis_client.incr.assert_called_once()
        twitter_collector.mock_redis_client.expire.assert_called_once()
        assert twitter_collector.request_count == 1

    @pytest.mark.asyncio
    async def test_make_request_success(self, twitter_collector):
        """Testa requisição bem-sucedida."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})
        mock_session.get.return_value.__aenter__.return_value = mock_response
        twitter_collector.session = mock_session
        
        with patch.object(twitter_collector, '_check_rate_limit', return_value=True):
            with patch.object(twitter_collector, '_increment_rate_limit'):
                with patch.object(twitter_collector.circuit_breaker, 'can_execute', return_value=True):
                    with patch.object(twitter_collector.circuit_breaker, 'on_success'):
                        result = await twitter_collector._make_request("test/endpoint")
                        assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_exceeded(self, twitter_collector):
        """Testa requisição com rate limit excedido."""
        with patch.object(twitter_collector, '_check_rate_limit', return_value=False):
            with pytest.raises(TwitterRateLimitError, match="Rate limit atingido"):
                await twitter_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_circuit_breaker_open(self, twitter_collector):
        """Testa requisição com circuit breaker aberto."""
        with patch.object(twitter_collector, '_check_rate_limit', return_value=True):
            with patch.object(twitter_collector.circuit_breaker, 'can_execute', return_value=False):
                with pytest.raises(TwitterAPIError, match="Circuit breaker aberto"):
                    await twitter_collector._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_collect_tweets_success(self, twitter_collector):
        """Testa coleta de tweets bem-sucedida."""
        mock_tweets = [
            TwitterTweet(
                id="tweet1",
                text="Test tweet 1",
                author_id="user1",
                created_at=datetime.now(),
                engagement_metrics={"retweets": 5, "likes": 25},
                hashtags=["#test"],
                keywords=["test"],
                language="en",
                is_retweet=False,
                is_quote=False,
                is_reply=False,
                viral_score=0.3
            )
        ]
        
        with patch.object(twitter_collector.cache, 'get', return_value=None):
            with patch.object(twitter_collector, '_make_request', return_value={
                "data": [{
                    "id": "tweet1",
                    "text": "Test tweet 1",
                    "author_id": "user1",
                    "created_at": "2023-01-01T00:00:00Z",
                    "lang": "en",
                    "public_metrics": {"retweet_count": 5, "like_count": 25}
                }]
            }):
                with patch.object(twitter_collector.cache, 'set'):
                    tweets = await twitter_collector.collect_tweets(["test"])
                    assert len(tweets) == 1
                    assert tweets[0].id == "tweet1"

    @pytest.mark.asyncio
    async def test_collect_tweets_from_cache(self, twitter_collector):
        """Testa coleta de tweets do cache."""
        cached_tweets = [
            TwitterTweet(
                id="tweet1",
                text="Cached tweet",
                author_id="user1",
                created_at=datetime.now(),
                engagement_metrics={},
                hashtags=[],
                keywords=[],
                language="en",
                is_retweet=False,
                is_quote=False,
                is_reply=False,
                viral_score=0.0
            )
        ]
        
        with patch.object(twitter_collector.cache, 'get', return_value=cached_tweets):
            tweets = await twitter_collector.collect_tweets(["test"])
            assert tweets == cached_tweets

    @pytest.mark.asyncio
    async def test_collect_trends_success(self, twitter_collector):
        """Testa coleta de tendências bem-sucedida."""
        with patch.object(twitter_collector.cache, 'get', return_value=None):
            with patch.object(twitter_collector, '_make_request', return_value={
                "trends": [{
                    "name": "#trending",
                    "tweet_volume": 1000
                }]
            }):
                with patch.object(twitter_collector.cache, 'set'):
                    trends = await twitter_collector.collect_trends("1")
                    assert len(trends) == 1
                    assert trends[0].keyword == "#trending"
                    assert trends[0].frequency == 1000

    @pytest.mark.asyncio
    async def test_collect_hashtags_success(self, twitter_collector):
        """Testa coleta de hashtags bem-sucedida."""
        sample_tweets = [
            TwitterTweet(
                id="tweet1",
                text="Test #viral tweet",
                author_id="user1",
                created_at=datetime.now(),
                engagement_metrics={"retweets": 10, "likes": 50},
                hashtags=["#viral"],
                keywords=["test", "viral"],
                language="en",
                is_retweet=False,
                is_quote=False,
                is_reply=False,
                viral_score=0.5
            )
        ]
        
        with patch.object(twitter_collector.cache, 'get', return_value=None):
            with patch.object(twitter_collector, 'collect_tweets', return_value=sample_tweets):
                with patch.object(twitter_collector.cache, 'set'):
                    hashtags = await twitter_collector.collect_hashtags(10)
                    assert len(hashtags) == 1
                    assert hashtags[0].hashtag == "#viral"

    @pytest.mark.asyncio
    async def test_start_streaming_success(self, twitter_collector):
        """Testa início de streaming bem-sucedido."""
        mock_streaming_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = AsyncMock()
        mock_response.content.__aiter__.return_value = [
            b'{"data": {"id": "tweet1", "text": "Stream tweet", "author_id": "user1", "created_at": "2023-01-01T00:00:00Z", "lang": "en", "public_metrics": {}}}'
        ]
        mock_streaming_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_streaming_session):
            with patch.object(twitter_collector, '_set_streaming_rules'):
                async for tweet in twitter_collector.start_streaming(["test"]):
                    assert tweet.id == "tweet1"
                    assert tweet.text == "Stream tweet"
                    break

    @pytest.mark.asyncio
    async def test_stop_streaming(self, twitter_collector):
        """Testa parada de streaming."""
        mock_streaming_session = AsyncMock()
        twitter_collector.streaming_session = mock_streaming_session
        twitter_collector.is_streaming = True
        
        await twitter_collector.stop_streaming()
        
        assert twitter_collector.is_streaming is False
        mock_streaming_session.close.assert_called_once()

    def test_extract_engagement_metrics(self, twitter_collector):
        """Testa extração de métricas de engajamento."""
        tweet_data = {
            "public_metrics": {
                "retweet_count": 10,
                "like_count": 50,
                "reply_count": 5,
                "quote_count": 3
            }
        }
        
        metrics = twitter_collector._extract_engagement_metrics(tweet_data)
        assert metrics["retweets"] == 10
        assert metrics["likes"] == 50
        assert metrics["replies"] == 5
        assert metrics["quotes"] == 3

    def test_extract_hashtags(self, twitter_collector):
        """Testa extração de hashtags."""
        text = "This is a #test tweet with #twitter #api"
        hashtags = twitter_collector._extract_hashtags(text)
        assert "#test" in hashtags
        assert "#twitter" in hashtags
        assert "#api" in hashtags

    def test_extract_keywords(self, twitter_collector):
        """Testa extração de keywords."""
        text = "This is a test tweet about technology and business"
        keywords = twitter_collector._extract_keywords(text)
        assert "test" in keywords
        assert "technology" in keywords
        assert "business" in keywords

    def test_is_retweet(self, twitter_collector):
        """Testa detecção de retweet."""
        tweet_data = {"text": "RT @user: Original tweet"}
        assert twitter_collector._is_retweet(tweet_data) is True
        
        tweet_data = {"text": "Original tweet"}
        assert twitter_collector._is_retweet(tweet_data) is False

    def test_is_quote(self, twitter_collector):
        """Testa detecção de quote tweet."""
        tweet_data = {
            "referenced_tweets": [{"type": "quoted"}]
        }
        assert twitter_collector._is_quote(tweet_data) is True
        
        tweet_data = {"referenced_tweets": []}
        assert twitter_collector._is_quote(tweet_data) is False

    def test_is_reply(self, twitter_collector):
        """Testa detecção de reply."""
        tweet_data = {
            "referenced_tweets": [{"type": "replied_to"}]
        }
        assert twitter_collector._is_reply(tweet_data) is True
        
        tweet_data = {"referenced_tweets": []}
        assert twitter_collector._is_reply(tweet_data) is False

    def test_calculate_viral_score(self, twitter_collector):
        """Testa cálculo de viral score."""
        tweet_data = {
            "public_metrics": {
                "retweet_count": 10,
                "like_count": 50,
                "reply_count": 5,
                "quote_count": 3
            }
        }
        
        viral_score = twitter_collector._calculate_viral_score(tweet_data)
        # (10*2 + 50 + 5*1.5 + 3*2.5) / 100 = 0.875
        assert viral_score == 0.875

    def test_calculate_viral_score_max(self, twitter_collector):
        """Testa cálculo de viral score com valor máximo."""
        tweet_data = {
            "public_metrics": {
                "retweet_count": 1000,
                "like_count": 5000,
                "reply_count": 500,
                "quote_count": 300
            }
        }
        
        viral_score = twitter_collector._calculate_viral_score(tweet_data)
        assert viral_score == 10.0  # Máximo

    def test_calculate_viral_score_trend(self, twitter_collector):
        """Testa cálculo de viral score de tendência."""
        trend_data = {"tweet_volume": 50000}
        viral_score = twitter_collector._calculate_viral_score_trend(trend_data)
        assert viral_score == 5.0  # 50000 / 10000

    def test_calculate_trending_score(self, twitter_collector):
        """Testa cálculo de trending score."""
        stats = {
            "frequency": 100,
            "total_engagement": 500
        }
        trending_score = twitter_collector._calculate_trending_score(stats)
        # (100 * 0.4 + 500 * 0.6) / 100 = 3.4
        assert trending_score == 3.4

    @pytest.mark.asyncio
    async def test_get_health_status(self, twitter_collector):
        """Testa obtenção de status de saúde."""
        with patch.object(twitter_collector.circuit_breaker, 'is_closed', return_value=True):
            with patch.object(twitter_collector.cache, 'get_hit_ratio', return_value=0.8):
                health = await twitter_collector.get_health_status()
                assert health["service"] == "twitter_api"
                assert health["status"] == "healthy"
                assert health["streaming_active"] is False
                assert health["tracing_id"] == "INT_002_TWITTER_2025_001"

    @pytest.mark.asyncio
    async def test_create_twitter_collector(self):
        """Testa função factory."""
        with patch('redis.asyncio.from_url') as mock_redis_from_url:
            mock_redis_client = AsyncMock()
            mock_redis_from_url.return_value = mock_redis_client
            
            with patch('infrastructure.coleta.twitter_api.TwitterCollector') as mock_collector_class:
                mock_collector = AsyncMock()
                mock_collector_class.return_value = mock_collector
                mock_collector.authenticate.return_value = True
                
                result = await create_twitter_collector(
                    api_key="test_key",
                    api_secret="test_secret",
                    bearer_token="test_bearer",
                    access_token="test_access",
                    access_token_secret="test_access_secret"
                )
                
                assert result == mock_collector
                mock_collector.authenticate.assert_called_once()

    def test_edge_cases(self, twitter_collector):
        """Testa casos edge."""
        # Teste de extração de hashtags com texto vazio
        hashtags = twitter_collector._extract_hashtags("")
        assert hashtags == []
        
        # Teste de extração de keywords com texto vazio
        keywords = twitter_collector._extract_keywords("")
        assert keywords == []
        
        # Teste de viral score com métricas vazias
        tweet_data = {"public_metrics": {}}
        viral_score = twitter_collector._calculate_viral_score(tweet_data)
        assert viral_score == 0.0


if __name__ == "__main__":
    pytest.main([__file__]) 