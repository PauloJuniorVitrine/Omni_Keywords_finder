"""
Testes Unitários - Facebook API Integration

Tracing ID: INT_003_FACEBOOK_TEST_2025_001
Data/Hora: 2025-01-27 17:40:00 UTC
Versão: 1.0
Status: 🧪 TESTES CRIADOS

📐 CoCoT - Comprovação: Testes seguem padrões pytest e unittest
📐 CoCoT - Causalidade: Garantir qualidade e robustez da integração Facebook
📐 CoCoT - Contexto: Sistema de coleta com insights e audience analysis
📐 CoCoT - Tendência: Testes assíncronos com mocks e fixtures

🌲 ToT - Caminho escolhido: Testes unitários + integração + performance + insights
♻️ ReAct - Simulação: Cobertura 95%+ com edge cases e error handling
"""

import pytest
import asyncio
import aiohttp
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Any

from infrastructure.coleta.facebook_api import (
    FacebookCollector,
    FacebookConfig,
    FacebookPost,
    FacebookInsight,
    FacebookAudience,
    FacebookAPIError,
    FacebookRateLimitError,
    FacebookAuthError,
    FacebookPermissionError,
    create_facebook_collector
)

# Fixtures
@pytest.fixture
def facebook_config():
    """Configuração de teste para Facebook"""
    return FacebookConfig(
        app_id="test_app_id",
        app_secret="test_app_secret",
        access_token="test_access_token",
        rate_limit_per_hour=200,
        rate_limit_per_day=5000
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
def sample_post_data():
    """Dados de exemplo de post do Facebook"""
    return {
        "id": "1234567890_987654321",
        "message": "Test post with #hashtag and keywords",
        "created_time": "2025-01-27T17:40:00+0000",
        "type": "status",
        "privacy": {"value": "EVERYONE"},
        "insights": {
            "data": [
                {
                    "name": "post_impressions",
                    "values": [{"value": 1000}]
                },
                {
                    "name": "post_engagements",
                    "values": [{"value": 150}]
                },
                {
                    "name": "post_reactions_by_type_total",
                    "values": [{"value": 100}]
                }
            ]
        }
    }

@pytest.fixture
def sample_insight_data():
    """Dados de exemplo de insight do Facebook"""
    return {
        "data": [
            {
                "name": "page_impressions",
                "period": "day",
                "values": [
                    {
                        "value": 5000,
                        "end_time": "2025-01-27T00:00:00+0000"
                    }
                ]
            },
            {
                "name": "page_engaged_users",
                "period": "day",
                "values": [
                    {
                        "value": 800,
                        "end_time": "2025-01-27T00:00:00+0000"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def sample_audience_data():
    """Dados de exemplo de audiência do Facebook"""
    return {
        "data": [
            {
                "name": "page_fans_gender_age",
                "values": [
                    {
                        "value": {
                            "M.18-24": 100,
                            "F.18-24": 150,
                            "M.25-34": 200,
                            "F.25-34": 250
                        }
                    }
                ]
            },
            {
                "name": "page_fans_country",
                "values": [
                    {
                        "value": {
                            "BR": 500,
                            "US": 300,
                            "CA": 100
                        }
                    }
                ]
            }
        ]
    }

# Testes para estruturas de dados
class TestFacebookConfig:
    """Testes para FacebookConfig"""
    
    def test_facebook_config_creation(self, facebook_config):
        """Testar criação da configuração"""
        assert facebook_config.app_id == "test_app_id"
        assert facebook_config.app_secret == "test_app_secret"
        assert facebook_config.access_token == "test_access_token"
        assert facebook_config.api_version == "v18.0"
        assert facebook_config.base_url == "https://graph.facebook.com"
        assert facebook_config.rate_limit_per_hour == 200
        assert facebook_config.rate_limit_per_day == 5000
        assert facebook_config.cache_ttl == 3600
        assert facebook_config.circuit_breaker_threshold == 5
        assert facebook_config.circuit_breaker_timeout == 60

class TestFacebookPost:
    """Testes para FacebookPost"""
    
    def test_facebook_post_creation(self, sample_post_data):
        """Testar criação de FacebookPost"""
        post = FacebookPost(
            id=sample_post_data["id"],
            message=sample_post_data["message"],
            created_time=datetime.fromisoformat(sample_post_data["created_time"].replace("+0000", "+00:00")),
            engagement_metrics={"impressions": 1000, "engagements": 150, "reactions": 100},
            hashtags=["#hashtag"],
            keywords=["test", "post", "keywords"],
            type="status",
            privacy="EVERYONE",
            page_id="1234567890",
            viral_score=0.25
        )
        
        assert post.id == "1234567890_987654321"
        assert post.message == "Test post with #hashtag and keywords"
        assert post.hashtags == ["#hashtag"]
        assert post.keywords == ["test", "post", "keywords"]
        assert post.type == "status"
        assert post.privacy == "EVERYONE"
        assert post.page_id == "1234567890"
        assert post.viral_score == 0.25

class TestFacebookInsight:
    """Testes para FacebookInsight"""
    
    def test_facebook_insight_creation(self):
        """Testar criação de FacebookInsight"""
        insight = FacebookInsight(
            metric="page_impressions",
            value=5000,
            period="day",
            date=datetime.now(),
            page_id="1234567890",
            trend=0.15
        )
        
        assert insight.metric == "page_impressions"
        assert insight.value == 5000
        assert insight.period == "day"
        assert insight.page_id == "1234567890"
        assert insight.trend == 0.15

class TestFacebookAudience:
    """Testes para FacebookAudience"""
    
    def test_facebook_audience_creation(self):
        """Testar criação de FacebookAudience"""
        audience = FacebookAudience(
            age_range={"18-24": 250, "25-34": 450},
            gender={"male": 300, "female": 400},
            location={"BR": 500, "US": 300},
            interests=["technology", "business"],
            page_id="1234567890",
            date=datetime.now()
        )
        
        assert audience.age_range["18-24"] == 250
        assert audience.age_range["25-34"] == 450
        assert audience.gender["male"] == 300
        assert audience.gender["female"] == 400
        assert audience.location["BR"] == 500
        assert audience.interests == ["technology", "business"]
        assert audience.page_id == "1234567890"

# Testes para exceções
class TestFacebookExceptions:
    """Testes para exceções customizadas"""
    
    def test_facebook_api_error(self):
        """Testar FacebookAPIError"""
        error = FacebookAPIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_facebook_rate_limit_error(self):
        """Testar FacebookRateLimitError"""
        error = FacebookRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, FacebookAPIError)
    
    def test_facebook_auth_error(self):
        """Testar FacebookAuthError"""
        error = FacebookAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, FacebookAPIError)
    
    def test_facebook_permission_error(self):
        """Testar FacebookPermissionError"""
        error = FacebookPermissionError("Permission denied")
        assert str(error) == "Permission denied"
        assert isinstance(error, FacebookAPIError)

# Testes principais para FacebookCollector
class TestFacebookCollector:
    """Testes para FacebookCollector"""
    
    @pytest.mark.asyncio
    async def test_collector_initialization(self, facebook_config, mock_redis):
        """Testar inicialização do coletor"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            assert collector.config == facebook_config
            assert collector.redis_client == mock_redis
            assert collector.request_count == 0
            assert collector.session is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, facebook_config, mock_redis):
        """Testar context manager"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            async with collector as c:
                assert c.session is not None
                assert isinstance(c.session, aiohttp.ClientSession)
            
            # Session deve ser fechada após sair do context
            assert collector.session is None
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, facebook_config, mock_redis):
        """Testar autenticação bem-sucedida"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta HTTP com sucesso
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"name": "Test User", "id": "123"})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = FacebookCollector(facebook_config, mock_redis)
            collector.session = AsyncMock()
            
            result = await collector.authenticate()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_authenticate_failure(self, facebook_config, mock_redis):
        """Testar falha na autenticação"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta HTTP com erro 401
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = FacebookCollector(facebook_config, mock_redis)
            collector.session = AsyncMock()
            
            result = await collector.authenticate()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, facebook_config, mock_redis):
        """Testar verificação de rate limit bem-sucedida"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            result = await collector._check_rate_limit()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, facebook_config, mock_redis):
        """Testar rate limit excedido"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            # Mock do Redis retornando limite excedido
            mock_redis.get.return_value = b"200"  # Limite por hora atingido
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            result = await collector._check_rate_limit()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, facebook_config, mock_redis):
        """Testar requisição bem-sucedida"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
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
            
            collector = FacebookCollector(facebook_config, mock_redis)
            collector.session = AsyncMock()
            
            result = await collector._make_request("test/endpoint")
            
            assert result == {"data": "test"}
            mock_breaker.on_success.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, facebook_config, mock_redis):
        """Testar erro de rate limit na requisição"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP com erro 429
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = FacebookCollector(facebook_config, mock_redis)
            collector.session = AsyncMock()
            
            with pytest.raises(FacebookRateLimitError):
                await collector._make_request("test/endpoint")
            
            mock_breaker.on_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_auth_error(self, facebook_config, mock_redis):
        """Testar erro de autenticação na requisição"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = True
            mock_breaker_class.return_value = mock_breaker
            
            # Mock da resposta HTTP com erro 401
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_get.return_value.__aenter__.return_value = mock_response
            
            collector = FacebookCollector(facebook_config, mock_redis)
            collector.session = AsyncMock()
            
            with pytest.raises(FacebookAuthError):
                await collector._make_request("test/endpoint")
            
            mock_breaker.on_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_posts_success(self, facebook_config, mock_redis, sample_post_data):
        """Testar coleta de posts bem-sucedida"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta da API
            mock_request.return_value = {
                "data": [sample_post_data]
            }
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            posts = await collector.collect_posts("1234567890", limit=10)
            
            assert len(posts) == 1
            assert posts[0].id == "1234567890_987654321"
            assert posts[0].message == "Test post with #hashtag and keywords"
            assert posts[0].type == "status"
            mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_posts_with_cache(self, facebook_config, mock_redis):
        """Testar coleta de posts com cache"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache = AsyncMock()
            cached_posts = [
                FacebookPost(
                    id="123",
                    message="Cached post",
                    created_time=datetime.now(),
                    engagement_metrics={},
                    hashtags=[],
                    keywords=[],
                    type="status",
                    privacy="EVERYONE",
                    page_id="1234567890",
                    viral_score=0.5
                )
            ]
            mock_cache.get.return_value = cached_posts
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            posts = await collector.collect_posts("1234567890", limit=10)
            
            assert len(posts) == 1
            assert posts[0].id == "123"
            assert posts[0].message == "Cached post"
    
    @pytest.mark.asyncio
    async def test_collect_insights_success(self, facebook_config, mock_redis, sample_insight_data):
        """Testar coleta de insights bem-sucedida"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta da API
            mock_request.return_value = sample_insight_data
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            insights = await collector.collect_insights("1234567890")
            
            assert len(insights) == 2
            assert insights[0].metric == "page_impressions"
            assert insights[0].value == 5000
            assert insights[1].metric == "page_engaged_users"
            assert insights[1].value == 800
            mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_audience_data_success(self, facebook_config, mock_redis, sample_audience_data):
        """Testar coleta de dados de audiência bem-sucedida"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock da resposta da API
            mock_request.return_value = sample_audience_data
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            audience = await collector.collect_audience_data("1234567890")
            
            assert audience is not None
            assert audience.page_id == "1234567890"
            assert "18-24" in audience.age_range
            assert "male" in audience.gender
            assert "BR" in audience.location
            mock_cache.set.assert_called_once()
    
    def test_extract_hashtags(self, facebook_config, mock_redis):
        """Testar extração de hashtags"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            text = "Test post with #hashtag1 and #hashtag2"
            hashtags = collector._extract_hashtags(text)
            
            assert hashtags == ["#hashtag1", "#hashtag2"]
    
    def test_extract_keywords(self, facebook_config, mock_redis):
        """Testar extração de keywords"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            text = "This is a test post with important keywords"
            keywords = collector._extract_keywords(text)
            
            assert "test" in keywords
            assert "post" in keywords
            assert "important" in keywords
            assert "keywords" in keywords
    
    def test_calculate_viral_score(self, facebook_config, mock_redis, sample_post_data):
        """Testar cálculo de viral score"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            viral_score = collector._calculate_viral_score(sample_post_data)
            
            assert 0.0 <= viral_score <= 1.0
    
    def test_extract_age_range(self, facebook_config, mock_redis):
        """Testar extração de faixa etária"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            gender_age_data = {
                "M.18-24": 100,
                "F.18-24": 150,
                "M.25-34": 200,
                "F.25-34": 250
            }
            
            age_ranges = collector._extract_age_range(gender_age_data)
            
            assert age_ranges["18-24"] == 250
            assert age_ranges["25-34"] == 450
    
    def test_extract_gender(self, facebook_config, mock_redis):
        """Testar extração de dados de gênero"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker_class.return_value = MagicMock()
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            gender_age_data = {
                "M.18-24": 100,
                "F.18-24": 150,
                "M.25-34": 200,
                "F.25-34": 250
            }
            
            gender_data = collector._extract_gender(gender_age_data)
            
            assert gender_data["male"] == 300
            assert gender_data["female"] == 400
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, facebook_config, mock_redis):
        """Testar status de saúde"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class:
            
            mock_cache = AsyncMock()
            mock_cache.get_hit_ratio.return_value = 0.85
            mock_cache_class.return_value = mock_cache
            
            mock_breaker = MagicMock()
            mock_breaker.is_closed.return_value = True
            mock_breaker.state = "closed"
            mock_breaker_class.return_value = mock_breaker
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            health = await collector.get_health_status()
            
            assert health["service"] == "facebook_api"
            assert health["status"] == "healthy"
            assert health["circuit_breaker_state"] == "closed"
            assert health["cache_hit_ratio"] == 0.85
            assert health["tracing_id"] == "INT_003_FACEBOOK_2025_001"

# Testes para factory function
class TestFactoryFunction:
    """Testes para factory function"""
    
    @pytest.mark.asyncio
    async def test_create_facebook_collector(self):
        """Testar factory function"""
        with patch('infrastructure.coleta.facebook_api.redis.from_url') as mock_redis_from_url, \
             patch('infrastructure.coleta.facebook_api.FacebookCollector') as mock_collector_class:
            
            mock_redis = AsyncMock()
            mock_redis_from_url.return_value = mock_redis
            
            mock_collector = AsyncMock()
            mock_collector.authenticate.return_value = True
            mock_collector_class.return_value = mock_collector
            
            collector = await create_facebook_collector(
                app_id="test_app_id",
                app_secret="test_app_secret",
                access_token="test_access_token"
            )
            
            assert collector == mock_collector
            mock_collector.authenticate.assert_called_once()

# Testes de Performance
class TestFacebookPerformance:
    """Testes de performance"""
    
    @pytest.mark.asyncio
    async def test_collect_posts_performance(self, facebook_config, mock_redis):
        """Testar performance da coleta de posts"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"data": []}
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            start_time = datetime.now()
            await collector.collect_posts("1234567890", limit=100)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            assert duration < 5.0  # Deve completar em menos de 5 segundos
    
    @pytest.mark.asyncio
    async def test_collect_insights_performance(self, facebook_config, mock_redis):
        """Testar performance da coleta de insights"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"data": []}
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            start_time = datetime.now()
            await collector.collect_insights("1234567890")
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            assert duration < 3.0  # Deve completar em menos de 3 segundos

# Testes de Integração
class TestFacebookIntegration:
    """Testes de integração"""
    
    @pytest.mark.asyncio
    async def test_full_collection_workflow(self, facebook_config, mock_redis):
        """Testar workflow completo de coleta"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            # Mock de diferentes respostas da API
            mock_request.side_effect = [
                {"data": [{"id": "123", "message": "Test post"}]},  # Posts
                {"data": [{"name": "page_impressions", "values": [{"value": 1000}]}]},  # Insights
                {"data": [{"name": "page_fans_gender_age", "values": [{"value": {}}]}]}  # Audience
            ]
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            # Coletar posts
            posts = await collector.collect_posts("1234567890", limit=10)
            assert len(posts) == 1
            
            # Coletar insights
            insights = await collector.collect_insights("1234567890")
            assert len(insights) == 1
            
            # Coletar dados de audiência
            audience = await collector.collect_audience_data("1234567890")
            assert audience is not None
            
            # Verificar cache foi usado
            assert mock_cache.set.call_count == 3

# Testes de Edge Cases
class TestFacebookEdgeCases:
    """Testes de edge cases"""
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self, facebook_config, mock_redis):
        """Testar tratamento de resposta vazia"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"data": []}
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            posts = await collector.collect_posts("nonexistent", limit=10)
            assert len(posts) == 0
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, facebook_config, mock_redis):
        """Testar tratamento de resposta malformada"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache = AsyncMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            mock_breaker_class.return_value = MagicMock()
            
            mock_request.return_value = {"invalid": "response"}
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            posts = await collector.collect_posts("1234567890", limit=10)
            assert len(posts) == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_activation(self, facebook_config, mock_redis):
        """Testar ativação do circuit breaker"""
        with patch('infrastructure.coleta.facebook_api.DistributedCache') as mock_cache_class, \
             patch('infrastructure.coleta.facebook_api.CircuitBreaker') as mock_breaker_class, \
             patch.object(FacebookCollector, '_make_request') as mock_request:
            
            mock_cache_class.return_value = AsyncMock()
            mock_breaker = MagicMock()
            mock_breaker.can_execute.return_value = False  # Circuit breaker aberto
            mock_breaker_class.return_value = mock_breaker
            
            collector = FacebookCollector(facebook_config, mock_redis)
            
            with pytest.raises(FacebookAPIError, match="Circuit breaker aberto"):
                await collector._make_request("test/endpoint")

if __name__ == "__main__":
    pytest.main([__file__, "-value", "--tb=short"]) 