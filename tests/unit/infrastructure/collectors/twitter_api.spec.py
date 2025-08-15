"""
Testes Unitários - Twitter API Integration

Tracing ID: INT_002_TWITTER_TEST_2025_001
Data/Hora: 2025-01-27 17:30:00 UTC
Versão: 1.0
Status: 🧪 TESTES CRIADOS

📐 CoCoT - Comprovação: Testes seguem padrões pytest e unittest
📐 CoCoT - Causalidade: Garantir qualidade e robustez da integração Twitter
📐 CoCoT - Contexto: Sistema de coleta com streaming e viral detection
📐 CoCoT - Tendência: Testes assíncronos com mocks e fixtures

🌲 ToT - Caminho escolhido: Testes unitários + integração + performance + streaming
♻️ ReAct - Simulação: Cobertura 95%+ com edge cases e error handling
"""

import pytest
import asyncio
import aiohttp
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any

from infrastructure.coleta.twitter_api import (
    TwitterCollector,
    TwitterConfig,
    TwitterTweet,
    TwitterTrend,
    TwitterHashtag,
    TwitterAPIError,
    TwitterRateLimitError,
    TwitterAuthError,
    TwitterStreamingError,
    create_twitter_collector
)

# Fixtures
@pytest.fixture
def twitter_config():
    """Configuração de teste para Twitter"""
    return TwitterConfig(
        api_key="test_api_key",
        api_secret="test_api_secret",
        bearer_token="test_bearer_token",
        access_token="test_access_token",
        access_token_secret="test_access_token_secret",
        rate_limit_per_15min=10,
        rate_limit_per_day=100
    )

@pytest.fixture
def mock_redis():
    """Mock do Redis"""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.incr.return_value = 1
    redis_mock.expire.return_value = True
    return redis_mock

@pytest.fixture
def sample_tweet_data():
    """Dados de exemplo de tweet"""
    return {
        "id": "1234567890",
        "text": "Test tweet with #hashtag and @mention",
        "author_id": "987654321",
        "created_at": "2025-01-27T17:30:00Z",
        "public_metrics": {
            "retweet_count": 10,
            "reply_count": 5,
            "like_count": 25,
            "quote_count": 3
        },
        "lang": "en",
        "referenced_tweets": []
    }

@pytest.fixture
def sample_trend_data():
    """Dados de exemplo de tendência"""
    return {
        "name": "test_trend",
        "tweet_volume": 1000,
        "url": "https://twitter.com/search?q=%23test_trend"
    }

@pytest.fixture
def sample_hashtag_data():
    """Dados de exemplo de hashtag"""
    return {
        "hashtag": "test_hashtag",
        "tweet_count": 500,
        "reach": 10000,
        "engagement": 250
    }

# Testes para estruturas de dados
class TestTwitterConfig:
    """Testes para TwitterConfig"""
    
    def test_twitter_config_creation(self, twitter_config):
        """Testar criação da configuração"""
        assert twitter_config.api_key == "test_api_key"
        assert twitter_config.api_secret == "test_api_secret"
        assert twitter_config.bearer_token == "test_bearer_token"
        assert twitter_config.access_token == "test_access_token"
        assert twitter_config.access_token_secret == "test_access_token_secret"
        assert twitter_config.api_version == "v2"
        assert twitter_config.base_url == "https://api.twitter.com"
        assert twitter_config.rate_limit_per_15min == 10
        assert twitter_config.rate_limit_per_day == 100
        assert twitter_config.cache_ttl == 1800
        assert twitter_config.circuit_breaker_threshold == 5
        assert twitter_config.circuit_breaker_timeout == 60
        assert twitter_config.streaming_buffer_size == 1000

class TestTwitterTweet:
    """Testes para TwitterTweet"""
    
    def test_twitter_tweet_creation(self, sample_tweet_data):
        """Testar criação de TwitterTweet"""
        tweet = TwitterTweet(
            id=sample_tweet_data["id"],
            text=sample_tweet_data["text"],
            author_id=sample_tweet_data["author_id"],
            created_at=datetime.fromisoformat(sample_tweet_data["created_at"].replace("Z", "+00:00")),
            engagement_metrics={"likes": 25, "retweets": 10, "replies": 5},
            hashtags=["#hashtag"],
            keywords=["test", "tweet"],
            language="en",
            is_retweet=False,
            is_quote=False,
            is_reply=False,
            viral_score=0.75
        )
        
        assert tweet.id == "1234567890"
        assert tweet.text == "Test tweet with #hashtag and @mention"
        assert tweet.author_id == "987654321"
        assert tweet.hashtags == ["#hashtag"]
        assert tweet.keywords == ["test", "tweet"]
        assert tweet.language == "en"
        assert tweet.viral_score == 0.75

class TestTwitterTrend:
    """Testes para TwitterTrend"""
    
    def test_twitter_trend_creation(self):
        """Testar criação de TwitterTrend"""
        trend = TwitterTrend(
            keyword="test_trend",
            frequency=1000,
            growth_rate=0.15,
            viral_score=0.8,
            hashtag=True,
            region="1",
            timestamp=datetime.now(),
            sentiment_score=0.6
        )
        
        assert trend.keyword == "test_trend"
        assert trend.frequency == 1000
        assert trend.growth_rate == 0.15
        assert trend.viral_score == 0.8
        assert trend.hashtag is True
        assert trend.region == "1"
        assert trend.sentiment_score == 0.6

class TestTwitterHashtag:
    """Testes para TwitterHashtag"""
    
    def test_twitter_hashtag_creation(self):
        """Testar criação de TwitterHashtag"""
        hashtag = TwitterHashtag(
            hashtag="test_hashtag",
            frequency=500,
            reach=10000,
            engagement_rate=0.025,
            trending_score=0.85,
            timestamp=datetime.now()
        )
        
        assert hashtag.hashtag == "test_hashtag"
        assert hashtag.frequency == 500
        assert hashtag.reach == 10000
        assert hashtag.engagement_rate == 0.025
        assert hashtag.trending_score == 0.85

# Testes para exceções
class TestTwitterExceptions:
    """Testes para exceções customizadas"""
    
    def test_twitter_api_error(self):
        """Testar TwitterAPIError"""
        error = TwitterAPIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_twitter_rate_limit_error(self):
        """Testar TwitterRateLimitError"""
        error = TwitterRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, TwitterAPIError)
    
    def test_twitter_auth_error(self):
        """Testar TwitterAuthError"""
        error = TwitterAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, TwitterAPIError)
    
    def test_twitter_streaming_error(self):
        """Testar TwitterStreamingError"""
        error = TwitterStreamingError("Streaming failed")
        assert str(error) == "Streaming failed"
        assert isinstance(error, TwitterAPIError)

# Testes principais para TwitterCollector
class TestTwitterCollector:
    """Testes para TwitterCollector"""
    
    @pytest.mark.asyncio
    async def test_collector_initialization(self, twitter_config, mock_redis):
        """Testar inicialização do coletor"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            assert collector.config == twitter_config
            assert collector.redis_client == mock_redis
            assert collector.request_count == 0
            assert collector.session is None
            assert collector.streaming_session is None
            assert collector.is_streaming is False
            assert len(collector.streaming_buffer) == 0
    
    @pytest.mark.asyncio
    async def test_context_manager(self, twitter_config, mock_redis):
        """Testar context manager"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            async with collector as c:
                assert c.session is not None
                assert isinstance(c.session, aiohttp.ClientSession)
            
            # Sessions devem ser fechadas após sair do context
            assert collector.session is None
            assert collector.streaming_session is None
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, twitter_config, mock_redis):
        """Testar autenticação bem-sucedida"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta HTTP com sucesso
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.session = AsyncMock()
            
            result = await collector.authenticate()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_authenticate_failure(self, twitter_config, mock_redis):
        """Testar falha na autenticação"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta HTTP com erro 401
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.session = AsyncMock()
            
            result = await collector.authenticate()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, twitter_config, mock_redis):
        """Testar verificação de rate limit bem-sucedida"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            result = await collector._check_rate_limit()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, twitter_config, mock_redis):
        """Testar rate limit excedido"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            # Mock do Redis retornando limite excedido
            mock_redis.get.return_value = b"10"  # Limite por minuto atingido
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            result = await collector._check_rate_limit()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, twitter_config, mock_redis):
        """Testar requisição bem-sucedida"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP com sucesso
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"data": "test"})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.session = AsyncMock()
            
            result = await collector._make_request("test/endpoint")
            
            assert result == {"data": "test"}
            mock_breaker.on_success.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, twitter_config, mock_redis):
        """Testar erro de rate limit na requisição"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP com erro 429
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.session = AsyncMock()
            
            with pytest.raises(TwitterRateLimitError):
                await collector._make_request("test/endpoint")
            
            mock_breaker.on_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_auth_error(self, twitter_config, mock_redis):
        """Testar erro de autenticação na requisição"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP com erro 401
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.session = AsyncMock()
            
            with pytest.raises(TwitterAuthError):
                await collector._make_request("test/endpoint")
            
            mock_breaker.on_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_tweets_success(self, twitter_config, mock_redis, sample_tweet_data):
        """Testar coleta de tweets bem-sucedida"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta da API
            mock_request.return_value = {
                "data": [sample_tweet_data],
                "includes": {
                    "users": [{"id": "987654321", "username": "testuser"}]
                }
            }
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            tweets = await collector.collect_tweets(["test"], limit=10)
            
            assert len(tweets) == 1
            assert tweets[0].id == "1234567890"
            assert tweets[0].text == "Test tweet with #hashtag and @mention"
            assert tweets[0].author_id == "987654321"
            mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_tweets_with_cache(self, twitter_config, mock_redis):
        """Testar coleta de tweets com cache"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache = AsyncMock()
            cached_tweets = [
                TwitterTweet(
                    id="123",
                    text="Cached tweet",
                    author_id="456",
                    created_at=datetime.now(),
                    engagement_metrics={},
                    hashtags=[],
                    keywords=[],
                    language="en",
                    is_retweet=False,
                    is_quote=False,
                    is_reply=False,
                    viral_score=0.5
                )
            ]
            mock_cache.get.return_value = cached_tweets
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            tweets = await collector.collect_tweets(["test"], limit=10)
            
            assert len(tweets) == 1
            assert tweets[0].id == "123"
            assert tweets[0].text == "Cached tweet"
    
    @pytest.mark.asyncio
    async def test_collect_trends_success(self, twitter_config, mock_redis, sample_trend_data):
        """Testar coleta de tendências bem-sucedida"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta da API
            mock_request.return_value = {
                "data": [sample_trend_data]
            }
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            trends = await collector.collect_trends(region="1")
            
            assert len(trends) == 1
            assert trends[0].keyword == "test_trend"
            assert trends[0].frequency == 1000
            mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_hashtags_success(self, twitter_config, mock_redis, sample_hashtag_data):
        """Testar coleta de hashtags bem-sucedida"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta da API
            mock_request.return_value = {
                "data": [sample_hashtag_data]
            }
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            hashtags = await collector.collect_hashtags(limit=10)
            
            assert len(hashtags) == 1
            assert hashtags[0].hashtag == "test_hashtag"
            assert hashtags[0].frequency == 500
            mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_streaming_success(self, twitter_config, mock_redis):
        """Testar início do streaming"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.post') as mock_post, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            # Mock das respostas HTTP
            mock_post_response = AsyncMock()
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"data": []})
            mock_post.return_value.__aenter__.return_value = mock_post_response
            
            mock_get_response = AsyncMock()
            mock_get_response.status = 200
            mock_get_response.content.iter_any = AsyncMock(return_value=[
                json.dumps({"data": {"id": "123", "text": "Test tweet"}}).encode()
            ])
            mock_get.return_value.__aenter__.return_value = mock_get_response
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.streaming_session = AsyncMock()
            
            # Testar streaming
            async for tweet in collector.start_streaming(["test"]):
                assert tweet.id == "123"
                assert tweet.text == "Test tweet"
                break  # Parar após primeiro tweet para teste
    
    @pytest.mark.asyncio
    async def test_stop_streaming(self, twitter_config, mock_redis):
        """Testar parada do streaming"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.is_streaming = True
            collector.streaming_session = AsyncMock()
            
            await collector.stop_streaming()
            
            assert collector.is_streaming is False
    
    def test_extract_hashtags(self, twitter_config, mock_redis):
        """Testar extração de hashtags"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            text = "Test tweet with #hashtag1 and #hashtag2"
            hashtags = collector._extract_hashtags(text)
            
            assert hashtags == ["#hashtag1", "#hashtag2"]
    
    def test_extract_keywords(self, twitter_config, mock_redis):
        """Testar extração de keywords"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            text = "This is a test tweet with important keywords"
            keywords = collector._extract_keywords(text)
            
            assert "test" in keywords
            assert "tweet" in keywords
            assert "important" in keywords
            assert "keywords" in keywords
    
    def test_calculate_viral_score(self, twitter_config, mock_redis, sample_tweet_data):
        """Testar cálculo de viral score"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            viral_score = collector._calculate_viral_score(sample_tweet_data)
            
            assert 0.0 <= viral_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, twitter_config, mock_redis):
        """Testar status de saúde"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache = AsyncMock()
            mock_cache.get_hit_ratio.return_value = 0.85
            mock_cache_class.return_value = mock_cache
            
            mock_breaker = MagicMock()
            mock_breaker.is_closed.return_value = True
            mock_breaker.state = "closed"
            mock_breaker_class.return_value = mock_breaker
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            health = await collector.get_health_status()
            
            assert health["service"] == "twitter_api"
            assert health["status"] == "healthy"
            assert health["circuit_breaker_state"] == "closed"
            assert health["cache_hit_ratio"] == 0.85
            assert health["tracing_id"] == "INT_002_TWITTER_2025_001"

# Testes para factory function
class TestFactoryFunction:
    """Testes para factory function"""
    
    @pytest.mark.asyncio
    async def test_create_twitter_collector(self):
        """Testar factory function"""
        with patch('infrastructure.coleta.twitter_api.redis.from_url') as mock_redis_from_url, \
             patch('infrastructure.coleta.twitter_api.TwitterCollector') as mock_collector_class:
            
            mock_redis = AsyncMock()
            mock_redis_from_url.return_value = mock_redis
            
            mock_collector = AsyncMock()
            mock_collector.authenticate.return_value = True
            mock_collector_class.return_value = mock_collector
            
            collector = await create_twitter_collector(
                api_key="test_key",
                api_secret="test_secret",
                bearer_token="test_bearer",
                access_token="test_access",
                access_token_secret="test_access_secret"
            )
            
            assert collector == mock_collector
            mock_collector.authenticate.assert_called_once()

# Testes de Performance
class TestTwitterPerformance:
    """Testes de performance"""
    
    @pytest.mark.asyncio
    async def test_collect_tweets_performance(self, twitter_config, mock_redis):
        """Testar performance da coleta de tweets"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"data": []}
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            start_time = datetime.now()
            await collector.collect_tweets(["test"], limit=100)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            assert duration < 5.0  # Deve completar em menos de 5 segundos
    
    @pytest.mark.asyncio
    async def test_streaming_performance(self, twitter_config, mock_redis):
        """Testar performance do streaming"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.post') as mock_post, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            mock_post_response = AsyncMock()
            mock_post_response.status = 200
            mock_post_response.json = AsyncMock(return_value={"data": []})
            mock_post.return_value.__aenter__.return_value = mock_post_response
            
            mock_get_response = AsyncMock()
            mock_get_response.status = 200
            mock_get_response.content.iter_any = AsyncMock(return_value=[])
            mock_get.return_value.__aenter__.return_value = mock_get_response
            
            collector = TwitterCollector(twitter_config, mock_redis)
            collector.streaming_session = AsyncMock()
            
            start_time = datetime.now()
            await collector.start_streaming(["test"])
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            assert duration < 3.0  # Deve iniciar em menos de 3 segundos

# Testes de Integração
class TestTwitterIntegration:
    """Testes de integração"""
    
    @pytest.mark.asyncio
    async def test_full_collection_workflow(self, twitter_config, mock_redis):
        """Testar workflow completo de coleta"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock de diferentes respostas da API
            mock_request.side_effect = [
                {"data": [{"id": "123", "text": "Test tweet"}]},  # Tweets
                {"data": [{"name": "trend", "tweet_volume": 100}]},  # Trends
                {"data": [{"hashtag": "test", "tweet_count": 50}]}  # Hashtags
            ]
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            # Coletar tweets
            tweets = await collector.collect_tweets(["test"], limit=10)
            assert len(tweets) == 1
            
            # Coletar tendências
            trends = await collector.collect_trends()
            assert len(trends) == 1
            
            # Coletar hashtags
            hashtags = await collector.collect_hashtags(limit=10)
            assert len(hashtags) == 1
            
            # Verificar cache foi usado
            assert mock_cache.set.call_count == 3

# Testes de Edge Cases
class TestTwitterEdgeCases:
    """Testes de edge cases"""
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self, twitter_config, mock_redis):
        """Testar tratamento de resposta vazia"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"data": []}
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            tweets = await collector.collect_tweets(["nonexistent"], limit=10)
            assert len(tweets) == 0
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, twitter_config, mock_redis):
        """Testar tratamento de resposta malformada"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"invalid": "response"}
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            tweets = await collector.collect_tweets(["test"], limit=10)
            assert len(tweets) == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_activation(self, twitter_config, mock_redis):
        """Testar ativação do circuit breaker"""
        with patch('infrastructure.coleta.twitter_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.twitter_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(TwitterCollector, '_make_request') as mock_request:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = False  # Circuit breaker aberto
            mock_breaker_class.return_value = mock_breaker
            
            collector = TwitterCollector(twitter_config, mock_redis)
            
            with pytest.raises(TwitterAPIError, match="Circuit breaker aberto"):
                await collector._make_request("test/endpoint")

if __name__ == "__main__":
    pytest.main([__file__, "-value", "--tb=short"]) 