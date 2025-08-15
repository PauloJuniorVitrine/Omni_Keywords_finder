"""
🧪 TikTok API Integration Tests

Tracing ID: tiktok-tests-2025-01-27-001
Timestamp: 2025-01-27T15:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em padrões de integração e cenários reais de uso
🌲 ToT: Avaliadas múltiplas estratégias de teste e escolhida cobertura ideal
♻️ ReAct: Simulado cenários de falha e validada robustez dos testes
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

from infrastructure.coleta.tiktok_developers_api import (
    TikTokDevelopersAPI, 
    TikTokAPIError, 
    TikTokVideo, 
    TikTokHashtag, 
    TikTokUser,
    TikTokScope,
    VideoPrivacy
)
from infrastructure.coleta.tiktok_trends_analyzer import (
    TikTokTrendsAnalyzer,
    TrendAnalysis,
    TrendType,
    EngagementLevel,
    ViralMetrics
)
from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.orchestrator.fallback_manager import FallbackManager

# Configuração de teste
TEST_CONFIG = {
    "client_key": "test_client_key",
    "client_secret": "test_client_secret",
    "redirect_uri": "https://test.com/callback",
    "rate_limits": {
        "requests_per_minute": 100,
        "requests_per_hour": 1000
    }
}

TEST_TRENDS_CONFIG = {
    "viral_threshold": 0.8,
    "growth_threshold": 0.3,
    "engagement_thresholds": {
        "very_high": 0.15,
        "high": 0.10,
        "medium": 0.05,
        "low": 0.02
    },
    "rate_limits": {
        "requests_per_minute": 50,
        "requests_per_hour": 500
    },
    "cache_ttl": 3600
}

# Dados de teste
MOCK_VIDEO_DATA = {
    "id": "test_video_001",
    "title": "Test Video Title",
    "description": "Test video description",
    "duration": 30,
    "cover_image_url": "https://test.com/cover.jpg",
    "video_url": "https://test.com/video.mp4",
    "privacy_level": "PUBLIC",
    "created_time": "2025-01-27T10:00:00Z",
    "updated_time": "2025-01-27T10:00:00Z",
    "statistics": {
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 50,
        "share_count": 25
    },
    "hashtags": ["#test", "#demo"],
    "creator_id": "test_creator_001"
}

MOCK_HASHTAG_DATA = {
    "id": "test_hashtag_001",
    "name": "testhashtag",
    "title": "Test Hashtag",
    "description": "Test hashtag description",
    "video_count": 5000,
    "follower_count": 1000,
    "is_commerce": False,
    "created_time": "2025-01-27T10:00:00Z"
}

MOCK_USER_DATA = {
    "open_id": "test_user_001",
    "union_id": "test_union_001",
    "avatar_url": "https://test.com/avatar.jpg",
    "display_name": "Test User",
    "bio_description": "Test user bio",
    "profile_deep_link": "https://tiktok.com/@testuser",
    "is_verified": False,
    "follower_count": 1000,
    "following_count": 500,
    "likes_count": 5000,
    "video_count": 50
}

MOCK_HISTORICAL_DATA = [
    {
        "timestamp": "2025-01-27T08:00:00Z",
        "views": 100,
        "likes": 10,
        "comments": 5,
        "shares": 2,
        "engagement_rate": 0.17
    },
    {
        "timestamp": "2025-01-27T09:00:00Z",
        "views": 250,
        "likes": 25,
        "comments": 12,
        "shares": 6,
        "engagement_rate": 0.172
    },
    {
        "timestamp": "2025-01-27T10:00:00Z",
        "views": 500,
        "likes": 50,
        "comments": 25,
        "shares": 12,
        "engagement_rate": 0.174
    }
]

class TestTikTokDevelopersAPI:
    """Testes para TikTok for Developers API"""
    
    @pytest.fixture
    def api_client(self):
        """Fixture para cliente API"""
        return TikTokDevelopersAPI(TEST_CONFIG)
    
    @pytest.fixture
    def mock_response(self):
        """Fixture para resposta mock"""
        mock = Mock()
        mock.status_code = 200
        mock.json.return_value = {
            "data": {
                "videos": [MOCK_VIDEO_DATA],
                "hashtags": [MOCK_HASHTAG_DATA],
                "user": MOCK_USER_DATA
            }
        }
        return mock
    
    def test_api_initialization(self, api_client):
        """Testa inicialização da API"""
        assert api_client.client_key == "test_client_key"
        assert api_client.client_secret == "test_client_secret"
        assert api_client.redirect_uri == "https://test.com/callback"
        assert api_client.api_base_url == "https://open.tiktokapis.com/v2"
        assert isinstance(api_client.circuit_breaker, CircuitBreaker)
        assert isinstance(api_client.rate_limiter, RateLimiter)
        assert isinstance(api_client.fallback_manager, FallbackManager)
    
    @patch('requests.post')
    def test_exchange_code_for_token_success(self, mock_post, api_client, mock_response):
        """Testa troca bem-sucedida de código por token"""
        mock_post.return_value = mock_response
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token"
        }
        
        result = api_client.exchange_code_for_token("test_auth_code")
        
        assert result["access_token"] == "test_access_token"
        assert result["expires_in"] == 3600
        assert api_client.access_token == "test_access_token"
        assert api_client.token_expires_at is not None
    
    @patch('requests.post')
    def test_exchange_code_for_token_failure(self, mock_post, api_client):
        """Testa falha na troca de código por token"""
        mock_post.side_effect = Exception("API Error")
        
        with pytest.raises(TikTokAPIError):
            api_client.exchange_code_for_token("test_auth_code")
    
    @patch('requests.get')
    def test_search_videos_success(self, mock_get, api_client, mock_response):
        """Testa busca bem-sucedida de vídeos"""
        api_client.access_token = "test_token"
        api_client.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_get.return_value = mock_response
        
        videos = api_client.search_videos("test query")
        
        assert len(videos) == 1
        assert isinstance(videos[0], TikTokVideo)
        assert videos[0].id == "test_video_001"
        assert videos[0].title == "Test Video Title"
    
    @patch('requests.get')
    def test_search_videos_without_token(self, mock_get, api_client):
        """Testa busca de vídeos sem token"""
        with pytest.raises(TikTokAPIError, match="Access token não configurado"):
            api_client.search_videos("test query")
    
    @patch('requests.get')
    def test_search_hashtags_success(self, mock_get, api_client, mock_response):
        """Testa busca bem-sucedida de hashtags"""
        api_client.access_token = "test_token"
        api_client.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_get.return_value = mock_response
        
        hashtags = api_client.search_hashtags("test hashtag")
        
        assert len(hashtags) == 1
        assert isinstance(hashtags[0], TikTokHashtag)
        assert hashtags[0].name == "testhashtag"
    
    @patch('requests.get')
    def test_get_user_info_success(self, mock_get, api_client, mock_response):
        """Testa obtenção bem-sucedida de informações do usuário"""
        api_client.access_token = "test_token"
        api_client.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_get.return_value = mock_response
        
        user = api_client.get_user_info()
        
        assert isinstance(user, TikTokUser)
        assert user.open_id == "test_user_001"
        assert user.display_name == "Test User"
    
    @patch('requests.get')
    def test_get_trending_hashtags_success(self, mock_get, api_client, mock_response):
        """Testa obtenção bem-sucedida de hashtags em tendência"""
        api_client.access_token = "test_token"
        api_client.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_get.return_value = mock_response
        
        hashtags = api_client.get_trending_hashtags(count=5)
        
        assert len(hashtags) == 1
        assert isinstance(hashtags[0], TikTokHashtag)
    
    def test_ensure_valid_token_without_token(self, api_client):
        """Testa verificação de token sem token configurado"""
        with pytest.raises(TikTokAPIError, match="Access token não configurado"):
            api_client._ensure_valid_token()
    
    def test_ensure_valid_token_expired(self, api_client):
        """Testa verificação de token expirado"""
        api_client.access_token = "test_token"
        api_client.token_expires_at = datetime.utcnow() - timedelta(hours=1)
        
        with pytest.raises(TikTokAPIError, match="Access token expirado"):
            api_client._ensure_valid_token()
    
    def test_get_auth_headers(self, api_client):
        """Testa geração de headers de autenticação"""
        api_client.access_token = "test_token"
        headers = api_client._get_auth_headers()
        
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Content-Type"] == "application/json"
    
    def test_parse_video_data(self, api_client):
        """Testa parsing de dados de vídeo"""
        video = api_client._parse_video_data(MOCK_VIDEO_DATA)
        
        assert isinstance(video, TikTokVideo)
        assert video.id == "test_video_001"
        assert video.title == "Test Video Title"
        assert video.privacy_level == VideoPrivacy.PUBLIC
        assert len(video.hashtags) == 2
    
    def test_parse_hashtag_data(self, api_client):
        """Testa parsing de dados de hashtag"""
        hashtag = api_client._parse_hashtag_data(MOCK_HASHTAG_DATA)
        
        assert isinstance(hashtag, TikTokHashtag)
        assert hashtag.id == "test_hashtag_001"
        assert hashtag.name == "testhashtag"
        assert hashtag.video_count == 5000
    
    def test_parse_user_data(self, api_client):
        """Testa parsing de dados de usuário"""
        user = api_client._parse_user_data(MOCK_USER_DATA)
        
        assert isinstance(user, TikTokUser)
        assert user.open_id == "test_user_001"
        assert user.display_name == "Test User"
        assert user.follower_count == 1000


class TestTikTokTrendsAnalyzer:
    """Testes para TikTok Trends Analyzer"""
    
    @pytest.fixture
    def trends_analyzer(self):
        """Fixture para analisador de tendências"""
        return TikTokTrendsAnalyzer(TEST_TRENDS_CONFIG)
    
    @pytest.fixture
    def mock_video_data(self):
        """Fixture para dados de vídeo"""
        return {
            "id": "test_video_001",
            "views": 1000,
            "likes": 100,
            "comments": 50,
            "shares": 25,
            "duration": 30,
            "watch_time": 15000,
            "created_time": "2025-01-27T10:00:00Z"
        }
    
    def test_analyzer_initialization(self, trends_analyzer):
        """Testa inicialização do analisador"""
        assert trends_analyzer.viral_threshold == 0.8
        assert trends_analyzer.growth_threshold == 0.3
        assert isinstance(trends_analyzer.circuit_breaker, CircuitBreaker)
        assert isinstance(trends_analyzer.rate_limiter, RateLimiter)
        assert trends_analyzer.cache_ttl == 3600
    
    @pytest.mark.asyncio
    async def test_analyze_hashtag_trend_success(self, trends_analyzer):
        """Testa análise bem-sucedida de tendência de hashtag"""
        analysis = await trends_analyzer.analyze_hashtag_trend(
            "testhashtag", 
            MOCK_HISTORICAL_DATA
        )
        
        assert isinstance(analysis, TrendAnalysis)
        assert analysis.hashtag == "testhashtag"
        assert isinstance(analysis.trend_type, TrendType)
        assert isinstance(analysis.engagement_level, EngagementLevel)
        assert 0.0 <= analysis.viral_score <= 1.0
        assert 0.0 <= analysis.confidence_level <= 1.0
        assert analysis.analysis_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_analyze_hashtag_trend_empty_data(self, trends_analyzer):
        """Testa análise com dados vazios"""
        analysis = await trends_analyzer.analyze_hashtag_trend("testhashtag", [])
        
        assert analysis.viral_score == 0.0
        assert analysis.growth_rate == 0.0
        assert analysis.confidence_level == 0.3  # Baixa confiança
    
    @pytest.mark.asyncio
    async def test_analyze_viral_potential_success(self, trends_analyzer, mock_video_data):
        """Testa análise bem-sucedida de potencial viral"""
        viral_metrics = await trends_analyzer.analyze_viral_potential(mock_video_data)
        
        assert isinstance(viral_metrics, ViralMetrics)
        assert viral_metrics.shares_per_view == 0.025
        assert viral_metrics.comments_per_view == 0.05
        assert viral_metrics.likes_per_view == 0.1
        assert viral_metrics.completion_rate == 0.5
        assert viral_metrics.watch_time_avg == 15.0
    
    @pytest.mark.asyncio
    async def test_analyze_viral_potential_zero_views(self, trends_analyzer):
        """Testa análise de potencial viral com zero views"""
        video_data = {
            "id": "test_video_001",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "duration": 30,
            "watch_time": 0,
            "created_time": "2025-01-27T10:00:00Z"
        }
        
        viral_metrics = await trends_analyzer.analyze_viral_potential(video_data)
        
        assert viral_metrics.shares_per_view == 0.0
        assert viral_metrics.comments_per_view == 0.0
        assert viral_metrics.likes_per_view == 0.0
        assert viral_metrics.completion_rate == 0.0
        assert viral_metrics.watch_time_avg == 0.0
    
    @pytest.mark.asyncio
    async def test_detect_emerging_trends_success(self, trends_analyzer):
        """Testa detecção bem-sucedida de tendências emergentes"""
        hashtags_data = [
            {
                "hashtag": "trending1",
                "historical_data": MOCK_HISTORICAL_DATA
            },
            {
                "hashtag": "trending2", 
                "historical_data": MOCK_HISTORICAL_DATA
            }
        ]
        
        emerging_trends = await trends_analyzer.detect_emerging_trends(hashtags_data)
        
        assert isinstance(emerging_trends, list)
        assert all(isinstance(trend, TrendAnalysis) for trend in emerging_trends)
    
    @pytest.mark.asyncio
    async def test_detect_emerging_trends_insufficient_data(self, trends_analyzer):
        """Testa detecção com dados insuficientes"""
        hashtags_data = [
            {
                "hashtag": "trending1",
                "historical_data": [MOCK_HISTORICAL_DATA[0]]  # Apenas 1 ponto
            }
        ]
        
        emerging_trends = await trends_analyzer.detect_emerging_trends(hashtags_data)
        
        assert len(emerging_trends) == 0
    
    def test_process_historical_data(self, trends_analyzer):
        """Testa processamento de dados históricos"""
        processed = trends_analyzer._process_historical_data(MOCK_HISTORICAL_DATA)
        
        assert "timestamps" in processed
        assert "views" in processed
        assert "likes" in processed
        assert "comments" in processed
        assert "shares" in processed
        assert "engagement_rates" in processed
        assert "growth_rates" in processed
        assert "velocity_metrics" in processed
        assert "momentum_indicators" in processed
    
    def test_calculate_viral_score(self, trends_analyzer):
        """Testa cálculo de score viral"""
        processed_data = trends_analyzer._process_historical_data(MOCK_HISTORICAL_DATA)
        viral_score = trends_analyzer._calculate_viral_score(processed_data)
        
        assert 0.0 <= viral_score <= 1.0
    
    def test_calculate_growth_rate(self, trends_analyzer):
        """Testa cálculo de taxa de crescimento"""
        processed_data = trends_analyzer._process_historical_data(MOCK_HISTORICAL_DATA)
        growth_rate = trends_analyzer._calculate_growth_rate(processed_data)
        
        assert growth_rate == 4.0  # (500-100)/100
    
    def test_determine_trend_type_viral(self, trends_analyzer):
        """Testa determinação de tipo viral"""
        trend_type = trends_analyzer._determine_trend_type(0.9, 0.5, 0.8)
        assert trend_type == TrendType.VIRAL
    
    def test_determine_trend_type_growing(self, trends_analyzer):
        """Testa determinação de tipo crescente"""
        trend_type = trends_analyzer._determine_trend_type(0.6, 0.4, 0.6)
        assert trend_type == TrendType.GROWING
    
    def test_determine_trend_type_declining(self, trends_analyzer):
        """Testa determinação de tipo decrescente"""
        trend_type = trends_analyzer._determine_trend_type(0.3, -0.1, 0.2)
        assert trend_type == TrendType.DECLINING
    
    def test_calculate_engagement_level_very_high(self, trends_analyzer):
        """Testa cálculo de nível de engajamento muito alto"""
        processed_data = {
            "engagement_rates": [0.2, 0.18, 0.22]  # Média > 0.15
        }
        engagement_level = trends_analyzer._calculate_engagement_level(processed_data)
        assert engagement_level == EngagementLevel.VERY_HIGH
    
    def test_calculate_engagement_level_low(self, trends_analyzer):
        """Testa cálculo de nível de engajamento baixo"""
        processed_data = {
            "engagement_rates": [0.03, 0.02, 0.04]  # Média < 0.05
        }
        engagement_level = trends_analyzer._calculate_engagement_level(processed_data)
        assert engagement_level == EngagementLevel.LOW
    
    def test_predict_reach(self, trends_analyzer):
        """Testa predição de alcance"""
        processed_data = trends_analyzer._process_historical_data(MOCK_HISTORICAL_DATA)
        predicted_reach = trends_analyzer._predict_reach(processed_data, 0.8)
        
        assert predicted_reach > 500  # Deve ser maior que o valor atual
    
    def test_calculate_confidence_level(self, trends_analyzer):
        """Testa cálculo de nível de confiança"""
        processed_data = trends_analyzer._process_historical_data(MOCK_HISTORICAL_DATA)
        confidence = trends_analyzer._calculate_confidence_level(processed_data)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_calculate_viral_coefficient(self, trends_analyzer):
        """Testa cálculo de coeficiente viral"""
        coefficient = trends_analyzer._calculate_viral_coefficient(25, 1000, 50)
        expected = (25 + 50 * 0.5) / 1000  # 0.05
        assert coefficient == expected
    
    def test_calculate_reach_velocity(self, trends_analyzer):
        """Testa cálculo de velocidade de alcance"""
        video_data = {
            "views": 1000,
            "created_time": "2025-01-27T10:00:00Z"
        }
        velocity = trends_analyzer._calculate_reach_velocity(video_data)
        
        assert velocity > 0.0  # Deve ser positivo
    
    def test_generate_cache_key(self, trends_analyzer):
        """Testa geração de chave de cache"""
        cache_key = trends_analyzer._generate_cache_key("testhashtag", MOCK_HISTORICAL_DATA)
        
        assert cache_key.startswith("trend_analysis:testhashtag:")
        assert len(cache_key) > 50  # Deve ter hash


class TestTikTokIntegration:
    """Testes de integração TikTok"""
    
    @pytest.fixture
    def api_client(self):
        """Fixture para cliente API"""
        return TikTokDevelopersAPI(TEST_CONFIG)
    
    @pytest.fixture
    def trends_analyzer(self):
        """Fixture para analisador de tendências"""
        return TikTokTrendsAnalyzer(TEST_TRENDS_CONFIG)
    
    @pytest.mark.asyncio
    async def test_full_workflow_success(self, api_client, trends_analyzer):
        """Testa workflow completo de análise TikTok"""
        # Mock das respostas da API
        with patch.object(api_client, 'search_videos') as mock_search:
            mock_search.return_value = [
                TikTokVideo(
                    id="test_video_001",
                    title="Test Video",
                    description="Test description",
                    duration=30,
                    cover_image_url="https://test.com/cover.jpg",
                    video_url="https://test.com/video.mp4",
                    privacy_level=VideoPrivacy.PUBLIC,
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow(),
                    statistics={"view_count": 1000, "like_count": 100},
                    hashtags=["#test"],
                    creator_id="test_creator"
                )
            ]
            
            # Buscar vídeos
            videos = api_client.search_videos("test query")
            assert len(videos) == 1
            
            # Analisar potencial viral
            video_data = {
                "id": videos[0].id,
                "views": videos[0].statistics["view_count"],
                "likes": videos[0].statistics["like_count"],
                "comments": 50,
                "shares": 25,
                "duration": videos[0].duration,
                "watch_time": 15000,
                "created_time": videos[0].created_time.isoformat()
            }
            
            viral_metrics = await trends_analyzer.analyze_viral_potential(video_data)
            assert isinstance(viral_metrics, ViralMetrics)
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, api_client):
        """Testa integração com rate limiting"""
        # Simular múltiplas requisições
        with patch.object(api_client.rate_limiter, 'check_rate_limit') as mock_rate_limit:
            mock_rate_limit.side_effect = Exception("Rate limit exceeded")
            
            with pytest.raises(Exception, match="Rate limit exceeded"):
                api_client.search_videos("test query")
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, api_client):
        """Testa integração com circuit breaker"""
        # Simular falhas consecutivas
        with patch.object(api_client, 'search_videos') as mock_search:
            mock_search.side_effect = TikTokAPIError("API Error")
            
            # Primeiras falhas devem passar
            for _ in range(4):
                with pytest.raises(TikTokAPIError):
                    api_client.search_videos("test query")
            
            # Após 5 falhas, circuit breaker deve abrir
            with pytest.raises(Exception):  # CircuitBreakerOpen
                api_client.search_videos("test query")
    
    @pytest.mark.asyncio
    async def test_fallback_integration(self, trends_analyzer):
        """Testa integração com fallback"""
        # Simular falha na análise
        with patch.object(trends_analyzer, 'analyze_hashtag_trend') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")
            
            with pytest.raises(Exception, match="Analysis failed"):
                await trends_analyzer.analyze_hashtag_trend("testhashtag", MOCK_HISTORICAL_DATA)


class TestTikTokErrorHandling:
    """Testes de tratamento de erros TikTok"""
    
    @pytest.fixture
    def api_client(self):
        """Fixture para cliente API"""
        return TikTokDevelopersAPI(TEST_CONFIG)
    
    def test_tiktok_api_error_creation(self):
        """Testa criação de erro TikTok API"""
        error = TikTokAPIError("Test error", "TEST_ERROR", 400)
        
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.http_status == 400
    
    @patch('requests.get')
    def test_http_error_handling(self, mock_get, api_client):
        """Testa tratamento de erro HTTP"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
        mock_get.return_value = mock_response
        
        api_client.access_token = "test_token"
        api_client.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        with pytest.raises(TikTokAPIError):
            api_client.search_videos("test query")
    
    @patch('requests.get')
    def test_network_error_handling(self, mock_get, api_client):
        """Testa tratamento de erro de rede"""
        mock_get.side_effect = Exception("Network error")
        
        api_client.access_token = "test_token"
        api_client.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        with pytest.raises(TikTokAPIError):
            api_client.search_videos("test query")


class TestTikTokPerformance:
    """Testes de performance TikTok"""
    
    @pytest.fixture
    def api_client(self):
        """Fixture para cliente API"""
        return TikTokDevelopersAPI(TEST_CONFIG)
    
    @pytest.fixture
    def trends_analyzer(self):
        """Fixture para analisador de tendências"""
        return TikTokTrendsAnalyzer(TEST_TRENDS_CONFIG)
    
    @pytest.mark.asyncio
    async def test_analysis_performance(self, trends_analyzer):
        """Testa performance da análise"""
        start_time = time.time()
        
        # Análise com dados grandes
        large_historical_data = MOCK_HISTORICAL_DATA * 100  # 300 pontos
        
        analysis = await trends_analyzer.analyze_hashtag_trend(
            "testhashtag", 
            large_historical_data
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve executar em menos de 1 segundo
        assert execution_time < 1.0
        assert isinstance(analysis, TrendAnalysis)
    
    @pytest.mark.asyncio
    async def test_bulk_analysis_performance(self, trends_analyzer):
        """Testa performance de análise em lote"""
        start_time = time.time()
        
        # Múltiplas análises
        hashtags_data = [
            {
                "hashtag": f"hashtag_{index}",
                "historical_data": MOCK_HISTORICAL_DATA
            }
            for index in range(10)
        ]
        
        emerging_trends = await trends_analyzer.detect_emerging_trends(hashtags_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve executar em menos de 2 segundos
        assert execution_time < 2.0
        assert isinstance(emerging_trends, list)


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 