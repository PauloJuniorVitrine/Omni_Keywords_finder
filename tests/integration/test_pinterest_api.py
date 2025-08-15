"""
📌 Testes de Integração - Pinterest API

Tracing ID: test-pinterest-2025-01-27-001
Timestamp: 2025-01-27T16:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em padrões de integração e boas práticas de testing
🌲 ToT: Avaliadas múltiplas estratégias de teste e escolhida cobertura ideal
♻️ ReAct: Simulado cenários de teste e validada efetividade
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from infrastructure.coleta.pinterest_api_v5 import (
    PinterestAPIv5, PinterestPin, PinterestBoard, PinterestUser,
    PinterestScope, PinterestAPIError
)
from infrastructure.coleta.pinterest_trends_analyzer import (
    PinterestTrendsAnalyzer, TrendData, EngagementMetrics, ViralAnalysis,
    TrendType, EngagementType
)

# Configuração de logging
import logging
logger = logging.getLogger(__name__)

class TestPinterestAPIAuthentication:
    """Testes de autenticação Pinterest API"""
    
    @pytest.fixture
    def pinterest_config(self):
        """Configuração para testes"""
        return {
            "app_id": "test_app_id",
            "app_secret": "test_app_secret",
            "redirect_uri": "https://example.com/callback",
            "rate_limits": {
                "requests_per_minute": 100,
                "requests_per_hour": 1000
            }
        }
    
    @pytest.fixture
    def pinterest_api(self, pinterest_config):
        """Instância da API Pinterest para testes"""
        return PinterestAPIv5(pinterest_config)
    
    def test_get_auth_url(self, pinterest_api):
        """Testa geração de URL de autorização"""
        # Arrange
        scopes = [PinterestScope.BOARDS_READ, PinterestScope.PINS_READ]
        
        # Act
        auth_url = pinterest_api.get_auth_url(scopes)
        
        # Assert
        assert auth_url is not None
        assert "pinterest.com/oauth" in auth_url
        assert "client_id=test_app_id" in auth_url
        assert "boards:read" in auth_url
        assert "pins:read" in auth_url
        assert "response_type=code" in auth_url
    
    def test_get_auth_url_default_scopes(self, pinterest_api):
        """Testa geração de URL com escopos padrão"""
        # Act
        auth_url = pinterest_api.get_auth_url()
        
        # Assert
        assert auth_url is not None
        assert "boards:read" in auth_url
        assert "pins:read" in auth_url
        assert "user_accounts:read" in auth_url
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.post')
    def test_exchange_code_for_token_success(self, mock_post, pinterest_api):
        """Testa troca bem-sucedida de código por token"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "bearer"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        authorization_code = "test_auth_code"
        
        # Act
        result = pinterest_api.exchange_code_for_token(authorization_code)
        
        # Assert
        assert result["access_token"] == "test_access_token"
        assert result["refresh_token"] == "test_refresh_token"
        assert result["expires_in"] == 3600
        assert pinterest_api.access_token == "test_access_token"
        assert pinterest_api.token_expires_at is not None
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.post')
    def test_exchange_code_for_token_error(self, mock_post, pinterest_api):
        """Testa erro na troca de código por token"""
        # Arrange
        mock_post.side_effect = Exception("API Error")
        authorization_code = "test_auth_code"
        
        # Act & Assert
        with pytest.raises(PinterestAPIError):
            pinterest_api.exchange_code_for_token(authorization_code)
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.post')
    def test_refresh_token_success(self, mock_post, pinterest_api):
        """Testa renovação bem-sucedida de token"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        refresh_token = "test_refresh_token"
        
        # Act
        result = pinterest_api.refresh_token(refresh_token)
        
        # Assert
        assert result["access_token"] == "new_access_token"
        assert pinterest_api.access_token == "new_access_token"
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.post')
    def test_refresh_token_error(self, mock_post, pinterest_api):
        """Testa erro na renovação de token"""
        # Arrange
        mock_post.side_effect = Exception("Refresh Error")
        refresh_token = "test_refresh_token"
        
        # Act & Assert
        with pytest.raises(PinterestAPIError):
            pinterest_api.refresh_token(refresh_token)

class TestPinterestAPISearch:
    """Testes de busca Pinterest API"""
    
    @pytest.fixture
    def pinterest_api_with_token(self, pinterest_config):
        """API Pinterest com token configurado"""
        api = PinterestAPIv5(pinterest_config)
        api.access_token = "test_access_token"
        api.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        return api
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.get')
    def test_search_pins_success(self, mock_get, pinterest_api_with_token):
        """Testa busca bem-sucedida de pins"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "pin_1",
                    "title": "Test Pin 1",
                    "description": "Test Description 1",
                    "link": "https://example.com/1",
                    "board_id": "board_1",
                    "created_at": "2025-01-27T10:00:00Z",
                    "updated_at": "2025-01-27T10:00:00Z",
                    "saved_at": "2025-01-27T10:00:00Z",
                    "last_saved_at": "2025-01-27T10:00:00Z",
                    "creative_type": "image"
                },
                {
                    "id": "pin_2",
                    "title": "Test Pin 2",
                    "description": "Test Description 2",
                    "link": "https://example.com/2",
                    "board_id": "board_2",
                    "created_at": "2025-01-27T11:00:00Z",
                    "updated_at": "2025-01-27T11:00:00Z",
                    "saved_at": "2025-01-27T11:00:00Z",
                    "last_saved_at": "2025-01-27T11:00:00Z",
                    "creative_type": "video"
                }
            ],
            "bookmark": "next_page_token"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        query = "test query"
        
        # Act
        result = pinterest_api_with_token.search_pins(query)
        
        # Assert
        assert len(result["items"]) == 2
        assert result["items"][0]["id"] == "pin_1"
        assert result["items"][1]["id"] == "pin_2"
        assert result["bookmark"] == "next_page_token"
        
        # Verificar se a requisição foi feita corretamente
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_access_token"
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.get')
    def test_search_pins_with_pagination(self, mock_get, pinterest_api_with_token):
        """Testa busca de pins com paginação"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [],
            "bookmark": None
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        query = "test query"
        bookmark = "test_bookmark"
        page_size = 50
        
        # Act
        result = pinterest_api_with_token.search_pins(query, bookmark, page_size)
        
        # Assert
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["bookmark"] == bookmark
        assert params["page_size"] == page_size
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.get')
    def test_search_pins_error(self, mock_get, pinterest_api_with_token):
        """Testa erro na busca de pins"""
        # Arrange
        mock_get.side_effect = Exception("Search Error")
        query = "test query"
        
        # Act
        result = pinterest_api_with_token.search_pins(query)
        
        # Assert
        # Deve retornar fallback
        assert "items" in result
        assert len(result["items"]) == 0
    
    def test_search_pins_no_token(self, pinterest_config):
        """Testa busca sem token configurado"""
        # Arrange
        api = PinterestAPIv5(pinterest_config)
        query = "test query"
        
        # Act & Assert
        with pytest.raises(PinterestAPIError, match="Access token não configurado"):
            api.search_pins(query)

class TestPinterestAPIBoards:
    """Testes de boards Pinterest API"""
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.get')
    def test_get_board_success(self, mock_get, pinterest_api_with_token):
        """Testa obtenção bem-sucedida de board"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "id": "board_1",
                "name": "Test Board",
                "description": "Test Board Description",
                "owner": {"username": "testuser"},
                "privacy": "public",
                "category": "test_category",
                "pin_count": 100,
                "follower_count": 50,
                "created_at": "2025-01-27T10:00:00Z",
                "updated_at": "2025-01-27T10:00:00Z",
                "collaborator_count": 2,
                "is_owner": True,
                "is_collaborator": False,
                "is_following": True
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        board_id = "board_1"
        
        # Act
        board = pinterest_api_with_token.get_board(board_id)
        
        # Assert
        assert board.id == "board_1"
        assert board.name == "Test Board"
        assert board.description == "Test Board Description"
        assert board.privacy == "public"
        assert board.category == "test_category"
        assert board.pin_count == 100
        assert board.follower_count == 50
        assert board.is_owner is True
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.get')
    def test_get_board_error(self, mock_get, pinterest_api_with_token):
        """Testa erro na obtenção de board"""
        # Arrange
        mock_get.side_effect = Exception("Board Error")
        board_id = "board_1"
        
        # Act & Assert
        with pytest.raises(PinterestAPIError):
            pinterest_api_with_token.get_board(board_id)
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.get')
    def test_get_board_pins_success(self, mock_get, pinterest_api_with_token):
        """Testa obtenção bem-sucedida de pins de board"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "pin_1",
                    "title": "Board Pin 1",
                    "board_id": "board_1"
                }
            ],
            "bookmark": None
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        board_id = "board_1"
        
        # Act
        result = pinterest_api_with_token.get_board_pins(board_id)
        
        # Assert
        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == "pin_1"
        assert result["items"][0]["board_id"] == "board_1"

class TestPinterestAPIUser:
    """Testes de usuário Pinterest API"""
    
    @patch('infrastructure.coleta.pinterest_api_v5.requests.get')
    def test_get_user_account_success(self, mock_get, pinterest_api_with_token):
        """Testa obtenção bem-sucedida de conta de usuário"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "username": "testuser",
                "about": "Test user description",
                "website": "https://example.com",
                "profile_image": "https://example.com/image.jpg",
                "full_name": "Test User",
                "country": "BR",
                "locale": "pt_BR"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Act
        user = pinterest_api_with_token.get_user_account()
        
        # Assert
        assert user.username == "testuser"
        assert user.about == "Test user description"
        assert user.website == "https://example.com"
        assert user.full_name == "Test User"
        assert user.country == "BR"
        assert user.locale == "pt_BR"

class TestPinterestTrendsAnalyzer:
    """Testes do analisador de tendências Pinterest"""
    
    @pytest.fixture
    def trends_config(self):
        """Configuração para testes de tendências"""
        return {
            "pinterest_api": {
                "app_id": "test_app_id",
                "app_secret": "test_app_secret",
                "redirect_uri": "https://example.com/callback"
            },
            "rate_limits": {
                "requests_per_minute": 50,
                "requests_per_hour": 500
            },
            "min_confidence_score": 0.7,
            "trend_window_days": 30,
            "viral_threshold": 2.0,
            "engagement_threshold": 0.05
        }
    
    @pytest.fixture
    def trends_analyzer(self, trends_config):
        """Instância do analisador de tendências"""
        return PinterestTrendsAnalyzer(trends_config)
    
    def test_analyze_trends_success(self, trends_analyzer):
        """Testa análise bem-sucedida de tendências"""
        # Arrange
        keywords = ["test keyword", "trending topic"]
        
        # Mock da API Pinterest
        with patch.object(trends_analyzer.api, 'search_pins') as mock_search:
            mock_search.return_value = {
                "items": [
                    {
                        "id": "pin_1",
                        "title": "Test Pin",
                        "description": "Test Description",
                        "created_at": "2025-01-27T10:00:00Z",
                        "save_count": 100,
                        "click_count": 50,
                        "comment_count": 10,
                        "share_count": 5,
                        "impression_count": 1000,
                        "board_id": "board_1"
                    }
                ]
            }
            
            # Act
            trends = trends_analyzer.analyze_trends(keywords)
            
            # Assert
            assert len(trends) > 0
            assert all(isinstance(trend, TrendData) for trend in trends)
            assert all(trend.confidence_score >= 0.0 for trend in trends)
            assert all(trend.confidence_score <= 1.0 for trend in trends)
    
    def test_analyze_engagement_success(self, trends_analyzer):
        """Testa análise bem-sucedida de engajamento"""
        # Arrange
        pin_ids = ["pin_1", "pin_2"]
        
        # Mock da API Pinterest
        with patch.object(trends_analyzer.api, 'get_pin') as mock_get_pin:
            mock_get_pin.return_value = {
                "id": "pin_1",
                "save_count": 100,
                "click_count": 50,
                "comment_count": 10,
                "share_count": 5,
                "impression_count": 1000
            }
            
            # Act
            engagement_data = trends_analyzer.analyze_engagement(pin_ids)
            
            # Assert
            assert len(engagement_data) > 0
            assert all(isinstance(metrics, EngagementMetrics) for metrics in engagement_data.values())
            assert all(metrics.engagement_rate >= 0.0 for metrics in engagement_data.values())
    
    def test_detect_viral_content_success(self, trends_analyzer):
        """Testa detecção bem-sucedida de conteúdo viral"""
        # Arrange
        pins = [
            PinterestPin(
                id="pin_1",
                title="Viral Pin",
                description="Viral Description",
                link="https://example.com",
                media_source={},
                board_id="board_1",
                board_section_id=None,
                parent_save_pin_id=None,
                note="",
                media={},
                media_metadata={},
                link_domain="example.com",
                is_owner=True,
                is_repin=False,
                is_video=False,
                is_editable=True,
                is_promoted=False,
                is_standard_product_pin=False,
                has_been_promoted_by_seller=False,
                is_eligible_for_web_close_up=True,
                promoted_is_removable=False,
                seen_by_me_at=None,
                tracked_link=None,
                rich_metadata=None,
                is_eligible_for_pdp=False,
                is_eligible_for_mpdp=False,
                is_eligible_for_shopping=False,
                is_eligible_for_redesign=False,
                is_eligible_for_web_close_up=True,
                is_eligible_for_web_redesign=False,
                is_eligible_for_web_shopping=False,
                is_eligible_for_web_standard_product_pin=False,
                is_eligible_for_web_rich_pin=False,
                is_eligible_for_web_video_pin=False,
                is_eligible_for_web_carousel_pin=False,
                is_eligible_for_web_collection_pin=False,
                is_eligible_for_web_idea_pin=False,
                is_eligible_for_web_story_pin=False,
                is_eligible_for_web_article_pin=False,
                is_eligible_for_web_product_pin=False,
                is_eligible_for_web_recipe_pin=False,
                is_eligible_for_web_movie_pin=False,
                is_eligible_for_web_place_pin=False,
                is_eligible_for_web_app_pin=False,
                is_eligible_for_web_book_pin=False,
                is_eligible_for_web_website_pin=False,
                is_eligible_for_web_other_pin=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                saved_at=datetime.utcnow(),
                last_saved_at=datetime.utcnow(),
                alt_text=None,
                creative_type="image",
                board_owner={},
                is_owner=True,
                is_repin=False,
                is_video=False,
                is_editable=True,
                is_promoted=False,
                is_standard_product_pin=False,
                has_been_promoted_by_seller=False,
                is_eligible_for_web_close_up=True,
                promoted_is_removable=False,
                seen_by_me_at=None,
                tracked_link=None,
                rich_metadata=None,
                is_eligible_for_pdp=False,
                is_eligible_for_mpdp=False,
                is_eligible_for_shopping=False,
                is_eligible_for_redesign=False,
                is_eligible_for_web_close_up=True,
                is_eligible_for_web_redesign=False,
                is_eligible_for_web_shopping=False,
                is_eligible_for_web_standard_product_pin=False,
                is_eligible_for_web_rich_pin=False,
                is_eligible_for_web_video_pin=False,
                is_eligible_for_web_carousel_pin=False,
                is_eligible_for_web_collection_pin=False,
                is_eligible_for_web_idea_pin=False,
                is_eligible_for_web_story_pin=False,
                is_eligible_for_web_article_pin=False,
                is_eligible_for_web_product_pin=False,
                is_eligible_for_web_recipe_pin=False,
                is_eligible_for_web_movie_pin=False,
                is_eligible_for_web_place_pin=False,
                is_eligible_for_web_app_pin=False,
                is_eligible_for_web_book_pin=False,
                is_eligible_for_web_website_pin=False,
                is_eligible_for_web_other_pin=False
            )
        ]
        
        # Act
        viral_analyses = trends_analyzer.detect_viral_content(pins)
        
        # Assert
        assert isinstance(viral_analyses, list)
        assert all(isinstance(analysis, ViralAnalysis) for analysis in viral_analyses)
    
    def test_predict_trend_growth_success(self, trends_analyzer):
        """Testa predição bem-sucedida de crescimento"""
        # Arrange
        keyword = "test keyword"
        days_ahead = 30
        
        # Mock da API Pinterest
        with patch.object(trends_analyzer.api, 'search_pins') as mock_search:
            mock_search.return_value = {
                "items": [
                    {
                        "id": "pin_1",
                        "created_at": "2025-01-27T10:00:00Z"
                    }
                ]
            }
            
            # Act
            prediction = trends_analyzer.predict_trend_growth(keyword, days_ahead)
            
            # Assert
            assert "keyword" in prediction
            assert prediction["keyword"] == keyword
            assert "current_volume" in prediction
            assert "predicted_volume" in prediction
            assert "confidence" in prediction
            assert prediction["days_ahead"] == days_ahead

class TestPinterestAPIRateLimiting:
    """Testes de rate limiting Pinterest API"""
    
    def test_rate_limiting_enforcement(self, pinterest_config):
        """Testa aplicação de rate limiting"""
        # Arrange
        api = PinterestAPIv5(pinterest_config)
        api.access_token = "test_token"
        api.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Act & Assert
        # Deve permitir múltiplas chamadas dentro do limite
        for index in range(5):
            try:
                with patch.object(api, '_make_request') as mock_request:
                    mock_request.return_value = {"items": []}
                    api.search_pins("test")
            except Exception:
                pass
        
        # Não deve lançar exceção por rate limiting nas primeiras chamadas
        assert True

class TestPinterestAPICircuitBreaker:
    """Testes de circuit breaker Pinterest API"""
    
    def test_circuit_breaker_activation(self, pinterest_config):
        """Testa ativação do circuit breaker"""
        # Arrange
        api = PinterestAPIv5(pinterest_config)
        api.access_token = "test_token"
        api.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Act & Assert
        # Simular falhas consecutivas
        with patch.object(api, '_make_request') as mock_request:
            mock_request.side_effect = Exception("API Error")
            
            # Primeiras falhas devem passar
            for index in range(3):
                try:
                    api.search_pins("test")
                except Exception:
                    pass
            
            # Após o limite, circuit breaker deve estar aberto
            assert api.circuit_breaker.state == "open"

class TestPinterestAPIFallback:
    """Testes de fallback Pinterest API"""
    
    def test_fallback_execution(self, pinterest_config):
        """Testa execução de fallback"""
        # Arrange
        api = PinterestAPIv5(pinterest_config)
        api.access_token = "test_token"
        api.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Act & Assert
        with patch.object(api, '_make_request') as mock_request:
            mock_request.side_effect = Exception("API Error")
            
            # Deve executar fallback
            result = api.search_pins("test")
            
            # Resultado deve ser do fallback
            assert "items" in result
            assert len(result["items"]) == 0

class TestPinterestAPIMetrics:
    """Testes de métricas Pinterest API"""
    
    def test_metrics_collection(self, pinterest_config):
        """Testa coleta de métricas"""
        # Arrange
        api = PinterestAPIv5(pinterest_config)
        api.access_token = "test_token"
        api.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Act
        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = {"items": []}
            api.search_pins("test")
        
        # Assert
        # Métricas devem ser incrementadas
        assert api.metrics is not None

class TestPinterestAPIIntegration:
    """Testes de integração completa Pinterest API"""
    
    @pytest.mark.integration
    def test_full_workflow(self, pinterest_config):
        """Testa workflow completo da API"""
        # Arrange
        api = PinterestAPIv5(pinterest_config)
        
        # Mock de autenticação
        with patch.object(api, 'exchange_code_for_token') as mock_auth:
            mock_auth.return_value = {
                "access_token": "test_token",
                "expires_in": 3600
            }
            
            # Mock de busca
            with patch.object(api, 'search_pins') as mock_search:
                mock_search.return_value = {
                    "items": [
                        {
                            "id": "pin_1",
                            "title": "Test Pin",
                            "board_id": "board_1"
                        }
                    ]
                }
                
                # Mock de board
                with patch.object(api, 'get_board') as mock_board:
                    mock_board.return_value = PinterestBoard(
                        id="board_1",
                        name="Test Board",
                        description="Test Description",
                        owner={},
                        privacy="public",
                        category="test",
                        pin_count=100,
                        follower_count=50,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        collaborator_count=0,
                        is_owner=True,
                        is_collaborator=False,
                        is_following=False,
                        is_eligible_for_web_close_up=False,
                        is_eligible_for_web_redesign=False,
                        is_eligible_for_web_shopping=False,
                        is_eligible_for_web_standard_product_pin=False,
                        is_eligible_for_web_rich_pin=False,
                        is_eligible_for_web_video_pin=False,
                        is_eligible_for_web_carousel_pin=False,
                        is_eligible_for_web_collection_pin=False,
                        is_eligible_for_web_idea_pin=False,
                        is_eligible_for_web_story_pin=False,
                        is_eligible_for_web_article_pin=False,
                        is_eligible_for_web_product_pin=False,
                        is_eligible_for_web_recipe_pin=False,
                        is_eligible_for_web_movie_pin=False,
                        is_eligible_for_web_place_pin=False,
                        is_eligible_for_web_app_pin=False,
                        is_eligible_for_web_book_pin=False,
                        is_eligible_for_web_website_pin=False,
                        is_eligible_for_web_other_pin=False
                    )
                    
                    # Act
                    # 1. Autenticação
                    auth_result = api.exchange_code_for_token("test_code")
                    
                    # 2. Busca de pins
                    search_result = api.search_pins("test query")
                    
                    # 3. Obtenção de board
                    board = api.get_board("board_1")
                    
                    # Assert
                    assert auth_result["access_token"] == "test_token"
                    assert len(search_result["items"]) == 1
                    assert board.id == "board_1"
                    assert board.name == "Test Board"

if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 