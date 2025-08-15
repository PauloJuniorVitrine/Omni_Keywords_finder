"""
Testes Unitários - LinkedIn API Integration

Tracing ID: INT_001_LINKEDIN_TEST_2025_001
Data/Hora: 2025-01-27 17:15:00 UTC
Versão: 1.0
Status: 🧪 TESTES CRIADOS

📐 CoCoT - Comprovação: Testes seguem padrões pytest e unittest
📐 CoCoT - Causalidade: Garantir qualidade e robustez da integração
📐 CoCoT - Contexto: Sistema de coleta com rate limiting e cache
📐 CoCoT - Tendência: Testes assíncronos com mocks e fixtures

🌲 ToT - Caminho escolhido: Testes unitários + integração + performance
♻️ ReAct - Simulação: Cobertura 95%+ com edge cases e error handling
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any

from infrastructure.coleta.linkedin_api import (
    LinkedInCollector,
    LinkedInConfig,
    LinkedInPost,
    LinkedInTrend,
    LinkedInAPIError,
    LinkedInRateLimitError,
    LinkedInAuthError,
    create_linkedin_collector
)

# Fixtures
@pytest.fixture
def linkedin_config():
    """Configuração de teste para LinkedIn"""
    return LinkedInConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/callback",
        rate_limit_per_minute=10,
        rate_limit_per_day=100
    )

@pytest.fixture
def mock_redis():
    """Mock do Redis para testes"""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = "0"
    redis_mock.incr.return_value = 1
    redis_mock.expire.return_value = True
    return redis_mock

@pytest.fixture
def mock_distributed_cache():
    """Mock do DistributedCache"""
    cache_mock = AsyncMock()
    cache_mock.get.return_value = None
    cache_mock.set.return_value = True
    cache_mock.get_hit_ratio.return_value = 0.85
    return cache_mock

@pytest.fixture
def mock_circuit_breaker():
    """Mock do CircuitBreaker"""
    breaker_mock = MagicMock()
    breaker_mock.can_execute.return_value = True
    breaker_mock.is_closed.return_value = True
    breaker_mock.state = "CLOSED"
    breaker_mock.on_success = MagicMock()
    breaker_mock.on_failure = MagicMock()
    return breaker_mock

@pytest.fixture
def sample_linkedin_post():
    """Post de exemplo do LinkedIn"""
    return LinkedInPost(
        id="urn:li:activity:123456789",
        author_id="urn:li:person:987654321",
        content="Test post content with #hashtag and keywords",
        created_time=datetime.now(),
        engagement_metrics={"likes": 10, "comments": 5, "shares": 2},
        hashtags=["#hashtag"],
        keywords=["test", "post", "content"],
        language="en",
        visibility="PUBLIC"
    )

@pytest.fixture
def sample_linkedin_trend():
    """Tendência de exemplo do LinkedIn"""
    return LinkedInTrend(
        keyword="artificial intelligence",
        frequency=150,
        growth_rate=1.5,
        industry="technology",
        region="global",
        timestamp=datetime.now()
    )

class TestLinkedInConfig:
    """Testes para LinkedInConfig"""
    
    def test_linkedin_config_creation(self, linkedin_config):
        """Testar criação da configuração"""
        assert linkedin_config.client_id == "test_client_id"
        assert linkedin_config.client_secret == "test_client_secret"
        assert linkedin_config.redirect_uri == "http://localhost:8000/callback"
        assert linkedin_config.api_version == "v2"
        assert linkedin_config.base_url == "https://api.linkedin.com"
        assert linkedin_config.rate_limit_per_minute == 10
        assert linkedin_config.rate_limit_per_day == 100
        assert linkedin_config.cache_ttl == 3600

class TestLinkedInPost:
    """Testes para LinkedInPost"""
    
    def test_linkedin_post_creation(self, sample_linkedin_post):
        """Testar criação de LinkedInPost"""
        assert sample_linkedin_post.id == "urn:li:activity:123456789"
        assert sample_linkedin_post.author_id == "urn:li:person:987654321"
        assert "Test post content" in sample_linkedin_post.content
        assert sample_linkedin_post.hashtags == ["#hashtag"]
        assert sample_linkedin_post.keywords == ["test", "post", "content"]
        assert sample_linkedin_post.language == "en"
        assert sample_linkedin_post.visibility == "PUBLIC"
        assert sample_linkedin_post.engagement_metrics["likes"] == 10

class TestLinkedInTrend:
    """Testes para LinkedInTrend"""
    
    def test_linkedin_trend_creation(self, sample_linkedin_trend):
        """Testar criação de LinkedInTrend"""
        assert sample_linkedin_trend.keyword == "artificial intelligence"
        assert sample_linkedin_trend.frequency == 150
        assert sample_linkedin_trend.growth_rate == 1.5
        assert sample_linkedin_trend.industry == "technology"
        assert sample_linkedin_trend.region == "global"

class TestLinkedInCollector:
    """Testes para LinkedInCollector"""
    
    @pytest.mark.asyncio
    async def test_collector_initialization(self, linkedin_config, mock_redis):
        """Testar inicialização do coletor"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            assert collector.config == linkedin_config
            assert collector.redis_client == mock_redis
            assert collector.request_count == 0
            assert collector.access_token is None
            assert collector.token_expires_at is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, linkedin_config, mock_redis):
        """Testar context manager"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            async with collector as c:
                assert c.session is not None
                assert isinstance(c.session, aiohttp.ClientSession)
            
            # Session deve ser fechada após sair do context
            assert collector.session is None
    
    @pytest.mark.asyncio
    async def test_authenticate_with_valid_token(self, linkedin_config, mock_redis):
        """Testar autenticação com token válido"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.access_token = "valid_token"
            collector.token_expires_at = datetime.now() + timedelta(hours=1)
            
            result = await collector.authenticate()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_authenticate_with_expired_token(self, linkedin_config, mock_redis):
        """Testar autenticação com token expirado"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.access_token = "expired_token"
            collector.token_expires_at = datetime.now() - timedelta(hours=1)
            
            result = await collector.authenticate()
            assert result is True
            assert collector.access_token == "simulated_access_token"
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_under_limit(self, linkedin_config, mock_redis):
        """Testar rate limiting abaixo do limite"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.request_count = 5  # Abaixo do limite diário
            
            result = await collector._check_rate_limit()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_over_daily_limit(self, linkedin_config, mock_redis):
        """Testar rate limiting acima do limite diário"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.request_count = 150  # Acima do limite diário
            
            result = await collector._check_rate_limit()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_over_minute_limit(self, linkedin_config, mock_redis):
        """Testar rate limiting acima do limite por minuto"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            mock_redis.get.return_value = "15"  # Acima do limite por minuto
            
            result = await collector._check_rate_limit()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, linkedin_config, mock_redis):
        """Testar requisição bem-sucedida"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"elements": []}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.access_token = "test_token"
            collector.session = AsyncMock()
            
            result = await collector._make_request("test/endpoint")
            
            assert result == {"elements": []}
            mock_breaker.on_success.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, linkedin_config, mock_redis):
        """Testar erro de rate limiting na requisição"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP com erro 429
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.access_token = "test_token"
            collector.session = AsyncMock()
            
            with pytest.raises(LinkedInRateLimitError):
                await collector._make_request("test/endpoint")
            
            mock_breaker.on_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_auth_error(self, linkedin_config, mock_redis):
        """Testar erro de autenticação na requisição"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP com erro 401
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.access_token = "test_token"
            collector.session = AsyncMock()
            
            with pytest.raises(LinkedInAuthError):
                await collector._make_request("test/endpoint")
            
            mock_breaker.on_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_posts_with_cache(self, linkedin_config, mock_redis, sample_linkedin_post):
        """Testar coleta de posts com cache"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = [sample_linkedin_post]
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            posts = await collector.collect_posts(["test"], limit=10)
            
            assert len(posts) == 1
            assert posts[0] == sample_linkedin_post
            mock_cache.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_posts_without_cache(self, linkedin_config, mock_redis):
        """Testar coleta de posts sem cache"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(LinkedInCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta da API
            mock_request.return_value = {
                "elements": [
                    {
                        "id": "urn:li:activity:123",
                        "author": {"id": "urn:li:person:456"},
                        "content": {"text": "Test content"},
                        "created": {"time": datetime.now().isoformat()},
                        "visibility": "PUBLIC"
                    }
                ]
            }
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.access_token = "test_token"
            
            posts = await collector.collect_posts(["test"], limit=10)
            
            assert len(posts) == 1
            assert posts[0].id == "urn:li:activity:123"
            mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_trends(self, linkedin_config, mock_redis, sample_linkedin_trend):
        """Testar coleta de tendências"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(LinkedInCollector, 'collect_posts') as mock_collect_posts:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock de posts para análise de tendências
            mock_post = MagicMock()
            mock_post.keywords = ["ai", "machine", "learning"]
            mock_collect_posts.return_value = [mock_post] * 10
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            trends = await collector.collect_trends(industry="technology")
            
            assert len(trends) > 0
            mock_cache.set.assert_called_once()
    
    def test_extract_hashtags(self, linkedin_config, mock_redis):
        """Testar extração de hashtags"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            content = "This is a test post with #hashtag1 and #hashtag2"
            hashtags = collector._extract_hashtags(content)
            
            assert "#hashtag1" in hashtags
            assert "#hashtag2" in hashtags
            assert len(hashtags) == 2
    
    def test_extract_keywords(self, linkedin_config, mock_redis):
        """Testar extração de keywords"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            content = "This is a test post about artificial intelligence and machine learning"
            keywords = collector._extract_keywords(content)
            
            assert "test" in keywords
            assert "post" in keywords
            assert "artificial" in keywords
            assert "intelligence" in keywords
            assert len(keywords) <= 10
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, linkedin_config, mock_redis):
        """Testar status de saúde"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache = AsyncMock()
            mock_cache.get_hit_ratio.return_value = 0.85
            mock_cache_class.return_value = mock_cache
            
            mock_breaker = MagicMock()
            mock_breaker.is_closed.return_value = True
            mock_breaker.state = "CLOSED"
            mock_breaker_class.return_value = mock_breaker
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            health = await collector.get_health_status()
            
            assert health["service"] == "linkedin_api"
            assert health["status"] == "healthy"
            assert health["circuit_breaker_state"] == "CLOSED"
            assert health["cache_hit_ratio"] == 0.85
            assert "tracing_id" in health

class TestLinkedInExceptions:
    """Testes para exceções customizadas"""
    
    def test_linkedin_api_error(self):
        """Testar LinkedInAPIError"""
        error = LinkedInAPIError("Test error")
        assert str(error) == "Test error"
    
    def test_linkedin_rate_limit_error(self):
        """Testar LinkedInRateLimitError"""
        error = LinkedInRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, LinkedInAPIError)
    
    def test_linkedin_auth_error(self):
        """Testar LinkedInAuthError"""
        error = LinkedInAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, LinkedInAPIError)

class TestFactoryFunction:
    """Testes para factory function"""
    
    @pytest.mark.asyncio
    async def test_create_linkedin_collector(self):
        """Testar factory function"""
        with patch('infrastructure.coleta.linkedin_api.redis.from_url') as mock_redis_from_url, \
             patch('infrastructure.coleta.linkedin_api.LinkedInCollector') as mock_collector_class:
            
            mock_redis = AsyncMock()
            mock_redis_from_url.return_value = mock_redis
            
            mock_collector = AsyncMock()
            mock_collector.authenticate.return_value = True
            mock_collector_class.return_value = mock_collector
            
            collector = await create_linkedin_collector(
                client_id="test_id",
                client_secret="test_secret",
                redirect_uri="http://localhost:8000/callback"
            )
            
            assert collector == mock_collector
            mock_collector.authenticate.assert_called_once()

# Testes de Performance
class TestLinkedInPerformance:
    """Testes de performance"""
    
    @pytest.mark.asyncio
    async def test_collect_posts_performance(self, linkedin_config, mock_redis):
        """Testar performance da coleta de posts"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(LinkedInCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"elements": []}
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            collector.access_token = "test_token"
            
            start_time = datetime.now()
            await collector.collect_posts(["test"], limit=100)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            assert duration < 5.0  # Deve completar em menos de 5 segundos

# Testes de Edge Cases
class TestLinkedInEdgeCases:
    """Testes de edge cases"""
    
    @pytest.mark.asyncio
    async def test_empty_keywords_list(self, linkedin_config, mock_redis):
        """Testar lista vazia de keywords"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            posts = await collector.collect_posts([], limit=10)
            assert posts == []
    
    @pytest.mark.asyncio
    async def test_zero_limit(self, linkedin_config, mock_redis):
        """Testar limite zero"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            posts = await collector.collect_posts(["test"], limit=0)
            assert posts == []
    
    def test_extract_keywords_empty_content(self, linkedin_config, mock_redis):
        """Testar extração de keywords de conteúdo vazio"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            keywords = collector._extract_keywords("")
            assert keywords == []
    
    def test_extract_hashtags_no_hashtags(self, linkedin_config, mock_redis):
        """Testar extração de hashtags sem hashtags"""
        with patch('infrastructure.coleta.linkedin_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.linkedin_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = LinkedInCollector(linkedin_config, mock_redis)
            
            hashtags = collector._extract_hashtags("This is a post without hashtags")
            assert hashtags == [] 