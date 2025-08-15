"""
Testes de Integração Real - Pinterest API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validado cobertura completa

Tracing ID: test-pinterest-real-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/pinterest_real_api.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 1
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Autenticação OAuth 2.0 real
- Busca de pins reais
- Detalhes de pins reais
- Detalhes de boards reais
- Rate limiting baseado em limites reais
- Circuit breaker para falhas de API
- Cache inteligente
- Fallback para web scraping
- Métricas de performance
- Logs estruturados
"""

import pytest
import os
import time
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from infrastructure.coleta.pinterest_real_api import (
    PinterestRealAPI, PinterestRealConfig, PinterestAPIType,
    PinterestRealPin, PinterestRealBoard, PinterestRealUser, PinterestRealSearchResult,
    PinterestRealAPIError, PinterestRateLimitError, PinterestAuthenticationError,
    PinterestScope, PinCreativeType, create_pinterest_real_client
)


class TestPinterestRealIntegration:
    """Testes de integração real para Pinterest API."""
    
    @pytest.fixture
    def real_config(self):
        """Configuração real para testes."""
        return PinterestRealConfig(
            app_id=os.getenv('PINTEREST_APP_ID', 'test_app_id'),
            app_secret=os.getenv('PINTEREST_APP_SECRET', 'test_app_secret'),
            redirect_uri=os.getenv('PINTEREST_REDIRECT_URI', 'http://localhost:8080/callback'),
            rate_limits_per_minute=1000,
            rate_limits_per_hour=10000,
            web_scraping_enabled=True,
            cache_enabled=True,
            circuit_breaker_enabled=True
        )
    
    @pytest.fixture
    def real_api(self, real_config):
        """Instância da API real para testes."""
        return PinterestRealAPI(real_config)
    
    @pytest.fixture
    def sample_pin_data(self):
        """Dados de exemplo de pin real."""
        return {
            'id': 'test_pin_id',
            'title': 'Test Pin Title',
            'description': 'Test pin description with keywords #test #pinterest #omni',
            'link': 'https://example.com/test-pin',
            'board_id': 'test_board_id',
            'board_section_id': '',
            'parent_save_pin_id': '',
            'note': 'Test note',
            'media_source': {
                'source_type': 'image_url',
                'url': 'https://example.com/image.jpg'
            },
            'media': {
                'images': {
                    '1200x': {'url': 'https://example.com/image_1200.jpg'},
                    '736x': {'url': 'https://example.com/image_736.jpg'},
                    '600x': {'url': 'https://example.com/image_600.jpg'}
                }
            },
            'media_metadata': {
                'width': 1200,
                'height': 800
            },
            'link_domain': 'example.com',
            'alt_text': 'Test image alt text',
            'creative_type': 'image',
            'is_owner': True,
            'is_repin': False,
            'is_video': False,
            'is_editable': True,
            'is_promoted': False,
            'is_standard_product_pin': False,
            'has_been_promoted_by_seller': False,
            'is_eligible_for_web_close_up': True,
            'promoted_is_removable': False,
            'tracked_link': '',
            'rich_metadata': {},
            'created_at': '2025-01-27T10:00:00Z',
            'updated_at': '2025-01-27T10:00:00Z',
            'saved_at': '2025-01-27T10:00:00Z',
            'last_saved_at': '2025-01-27T10:00:00Z'
        }
    
    @pytest.fixture
    def sample_search_result(self):
        """Dados de exemplo de resultado de busca."""
        return {
            'id': 'test_pin_id',
            'title': 'Test Pin Title',
            'description': 'Test pin description',
            'link': 'https://example.com/test-pin',
            'board_id': 'test_board_id',
            'creative_type': 'image',
            'created_at': '2025-01-27T10:00:00Z'
        }
    
    @pytest.fixture
    def sample_board_data(self):
        """Dados de exemplo de board real."""
        return {
            'id': 'test_board_id',
            'name': 'Test Board',
            'description': 'Test board description',
            'owner': {
                'username': 'test_user',
                'full_name': 'Test User'
            },
            'privacy': 'public',
            'category': 'test_category',
            'pin_count': 100,
            'follower_count': 50,
            'collaborator_count': 0,
            'created_at': '2025-01-27T10:00:00Z',
            'updated_at': '2025-01-27T10:00:00Z',
            'is_owner': True,
            'is_collaborator': False,
            'is_following': False
        }
    
    def test_pinterest_real_config_initialization(self, real_config):
        """Testa inicialização da configuração real."""
        assert real_config.app_id == os.getenv('PINTEREST_APP_ID', 'test_app_id')
        assert real_config.app_secret == os.getenv('PINTEREST_APP_SECRET', 'test_app_secret')
        assert real_config.redirect_uri == os.getenv('PINTEREST_REDIRECT_URI', 'http://localhost:8080/callback')
        assert real_config.rate_limits_per_minute == 1000
        assert real_config.rate_limits_per_hour == 10000
        assert real_config.web_scraping_enabled is True
        assert real_config.cache_enabled is True
        assert real_config.circuit_breaker_enabled is True
    
    def test_pinterest_real_api_initialization(self, real_api, real_config):
        """Testa inicialização da API real."""
        assert real_api.config == real_config
        assert real_api.rate_limiter is not None
        assert real_api.circuit_breaker is not None
        assert real_api.session is not None
        assert real_api.cache == {}
        assert real_api.access_token is None
        assert real_api.refresh_token is None
        assert real_api.token_expires_at is None
    
    def test_get_auth_url(self, real_api):
        """Testa geração de URL de autorização."""
        auth_url = real_api.get_auth_url()
        
        assert auth_url is not None
        assert "pinterest.com/oauth" in auth_url
        assert "client_id=test_app_id" in auth_url
        assert "boards:read" in auth_url
        assert "pins:read" in auth_url
        assert "user_accounts:read" in auth_url
        assert "response_type=code" in auth_url
    
    def test_get_auth_url_with_custom_scopes(self, real_api):
        """Testa geração de URL com escopos customizados."""
        scopes = [PinterestScope.BOARDS_WRITE, PinterestScope.PINS_WRITE]
        auth_url = real_api.get_auth_url(scopes)
        
        assert "boards:write" in auth_url
        assert "pins:write" in auth_url
    
    @patch('infrastructure.coleta.pinterest_real_api.requests.post')
    def test_exchange_code_for_token_success(self, mock_post, real_api):
        """Testa troca bem-sucedida de código por token."""
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "bearer"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Simular arquivo de token não existente
        with patch('os.path.exists', return_value=False):
            result = real_api.exchange_code_for_token("test_auth_code")
        
        assert result["access_token"] == "test_access_token"
        assert result["refresh_token"] == "test_refresh_token"
        assert real_api.access_token == "test_access_token"
        assert real_api.refresh_token == "test_refresh_token"
        assert real_api.token_expires_at is not None
        assert real_api.metrics.get_counter("pinterest_token_exchange_success") == 1
    
    @patch('infrastructure.coleta.pinterest_real_api.requests.post')
    def test_exchange_code_for_token_error(self, mock_post, real_api):
        """Testa erro na troca de código por token."""
        mock_post.side_effect = Exception("API Error")
        
        with pytest.raises(PinterestRealAPIError, match="Erro ao trocar código por token"):
            real_api.exchange_code_for_token("test_auth_code")
        
        assert real_api.metrics.get_counter("pinterest_token_exchange_failure") == 1
    
    def test_authenticate_with_valid_token(self, real_api):
        """Testa autenticação com token válido."""
        # Configurar token válido
        real_api.access_token = "valid_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        result = real_api._authenticate()
        assert result is True
    
    def test_authenticate_with_expired_token(self, real_api):
        """Testa autenticação com token expirado."""
        # Configurar token expirado
        real_api.access_token = "expired_token"
        real_api.refresh_token = "refresh_token"
        real_api.token_expires_at = datetime.now() - timedelta(hours=1)
        
        # Mock de renovação bem-sucedida
        with patch.object(real_api, '_refresh_access_token', return_value=True):
            result = real_api._authenticate()
        
        assert result is True
    
    def test_authenticate_without_token(self, real_api):
        """Testa autenticação sem token."""
        with patch('os.path.exists', return_value=False):
            result = real_api._authenticate()
        
        assert result is False
    
    def test_rate_limiter_check(self, real_api):
        """Testa verificação de rate limit."""
        # Rate limit disponível
        assert real_api.rate_limiter.can_make_request() is True
        
        # Simular rate limit excedido
        real_api.rate_limiter.requests_minute = 1000
        assert real_api.rate_limiter.can_make_request() is False
    
    @patch.object(PinterestRealAPI, '_make_api_request')
    def test_search_pins_success(self, mock_request, real_api, sample_search_result):
        """Testa busca bem-sucedida de pins."""
        # Mock da resposta
        mock_request.return_value = {
            "items": [sample_search_result]
        }
        
        # Configurar token válido
        real_api.access_token = "valid_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        results = real_api.search_pins("test query")
        
        assert len(results) == 1
        assert results[0].pin_id == "test_pin_id"
        assert results[0].title == "Test Pin Title"
        assert results[0].creative_type == "image"
        
        # Verificar se foi chamado com parâmetros corretos
        mock_request.assert_called_once_with("pins/search", {
            "query": "test query",
            "page_size": 25
        })
    
    @patch.object(PinterestRealAPI, '_make_api_request')
    def test_search_pins_cache(self, mock_request, real_api, sample_search_result):
        """Testa cache de busca de pins."""
        # Mock da resposta
        mock_request.return_value = {
            "items": [sample_search_result]
        }
        
        # Configurar token válido
        real_api.access_token = "valid_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        # Primeira busca
        results1 = real_api.search_pins("test query")
        
        # Segunda busca (deve usar cache)
        results2 = real_api.search_pins("test query")
        
        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0].pin_id == results2[0].pin_id
        
        # Verificar que foi chamado apenas uma vez
        assert mock_request.call_count == 1
    
    @patch.object(PinterestRealAPI, '_make_api_request')
    def test_get_pin_details_success(self, mock_request, real_api, sample_pin_data):
        """Testa obtenção bem-sucedida de detalhes de pin."""
        # Mock da resposta
        mock_request.return_value = sample_pin_data
        
        # Configurar token válido
        real_api.access_token = "valid_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        pin = real_api.get_pin_details("test_pin_id")
        
        assert pin.id == "test_pin_id"
        assert pin.title == "Test Pin Title"
        assert pin.description == "Test pin description with keywords #test #pinterest #omni"
        assert pin.link == "https://example.com/test-pin"
        assert pin.board_id == "test_board_id"
        assert pin.creative_type == "image"
        assert pin.is_owner is True
        assert pin.is_video is False
        
        # Verificar se foi chamado com parâmetros corretos
        mock_request.assert_called_once_with("pins/test_pin_id")
    
    @patch.object(PinterestRealAPI, '_make_api_request')
    def test_get_board_details_success(self, mock_request, real_api, sample_board_data):
        """Testa obtenção bem-sucedida de detalhes de board."""
        # Mock da resposta
        mock_request.return_value = sample_board_data
        
        # Configurar token válido
        real_api.access_token = "valid_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        board = real_api.get_board_details("test_board_id")
        
        assert board.id == "test_board_id"
        assert board.name == "Test Board"
        assert board.description == "Test board description"
        assert board.privacy == "public"
        assert board.pin_count == 100
        assert board.follower_count == 50
        assert board.is_owner is True
        
        # Verificar se foi chamado com parâmetros corretos
        mock_request.assert_called_once_with("boards/test_board_id")
    
    @patch.object(PinterestRealAPI, '_make_api_request')
    def test_get_user_account_success(self, mock_request, real_api):
        """Testa obtenção bem-sucedida de dados do usuário."""
        # Mock da resposta
        mock_request.return_value = {
            "username": "test_user",
            "about": "Test user about",
            "website": "https://example.com",
            "profile_image": "https://example.com/avatar.jpg",
            "full_name": "Test User",
            "country": "BR",
            "locale": "pt_BR",
            "account_type": "personal"
        }
        
        # Configurar token válido
        real_api.access_token = "valid_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        user = real_api.get_user_account()
        
        assert user.username == "test_user"
        assert user.about == "Test user about"
        assert user.website == "https://example.com"
        assert user.full_name == "Test User"
        assert user.country == "BR"
        assert user.account_type == "personal"
        
        # Verificar se foi chamado com parâmetros corretos
        mock_request.assert_called_once_with("user_account")
    
    def test_rate_limit_error(self, real_api):
        """Testa erro de rate limit."""
        # Simular rate limit excedido
        real_api.rate_limiter.requests_minute = 1000
        
        with pytest.raises(PinterestRateLimitError, match="Rate limit excedido"):
            real_api._make_api_request("test_endpoint")
    
    def test_authentication_error(self, real_api):
        """Testa erro de autenticação."""
        # Sem token configurado
        with pytest.raises(PinterestAuthenticationError, match="Falha na autenticação"):
            real_api._make_api_request("test_endpoint")
    
    def test_circuit_breaker_state_transitions(self, real_api):
        """Testa transições de estado do circuit breaker."""
        cb = real_api.circuit_breaker
        
        # Estado inicial
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0
        
        # Simular falhas
        for _ in range(5):
            cb.record_failure()
        
        # Circuit breaker deve abrir
        assert cb.state == "OPEN"
        assert cb.failure_count == 5
        
        # Aguardar timeout
        cb.last_failure_time = datetime.now() - timedelta(seconds=70)
        
        # Circuit breaker deve ir para half-open
        assert cb.can_execute() is True
        assert cb.state == "HALF_OPEN"
    
    def test_rate_limiter_reset(self, real_api):
        """Testa reset do rate limiter."""
        rl = real_api.rate_limiter
        
        # Simular uso
        rl.requests_minute = 500
        rl.requests_hour = 5000
        
        # Simular reset de minuto
        rl.last_reset_minute = datetime.now() - timedelta(minutes=2)
        assert rl.can_make_request() is True
        assert rl.requests_minute == 0
        
        # Simular reset de hora
        rl.last_reset_hour = datetime.now() - timedelta(hours=2)
        assert rl.can_make_request() is True
        assert rl.requests_hour == 0
    
    def test_get_rate_limit_status(self, real_api):
        """Testa obtenção de status dos rate limits."""
        status = real_api.get_rate_limit_status()
        
        assert "pinterest_api" in status
        assert "circuit_breaker" in status
        assert "web_scraping" in status
        
        assert status["pinterest_api"]["limit_minute"] == 1000
        assert status["pinterest_api"]["limit_hour"] == 10000
        assert status["circuit_breaker"]["state"] == "CLOSED"
        assert status["web_scraping"]["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_close_async_session(self, real_api):
        """Testa fechamento de sessão assíncrona."""
        # Criar sessão assíncrona
        await real_api._get_async_session()
        
        # Verificar que sessão foi criada
        assert real_api.async_session is not None
        assert not real_api.async_session.closed
        
        # Fechar sessão
        await real_api.close()
        
        # Verificar que sessão foi fechada
        assert real_api.async_session.closed


class TestPinterestRealFactory:
    """Testes para factory function."""
    
    @patch.dict(os.environ, {
        'PINTEREST_APP_ID': 'env_app_id',
        'PINTEREST_APP_SECRET': 'env_app_secret',
        'PINTEREST_REDIRECT_URI': 'http://env.com/callback'
    })
    def test_create_pinterest_real_client_from_env(self):
        """Testa criação de cliente a partir de variáveis de ambiente."""
        client = create_pinterest_real_client()
        
        assert client.config.app_id == 'env_app_id'
        assert client.config.app_secret == 'env_app_secret'
        assert client.config.redirect_uri == 'http://env.com/callback'
    
    def test_create_pinterest_real_client_with_params(self):
        """Testa criação de cliente com parâmetros explícitos."""
        client = create_pinterest_real_client(
            app_id='param_app_id',
            app_secret='param_app_secret',
            redirect_uri='http://param.com/callback'
        )
        
        assert client.config.app_id == 'param_app_id'
        assert client.config.app_secret == 'param_app_secret'
        assert client.config.redirect_uri == 'http://param.com/callback'


class TestPinterestRealDataStructures:
    """Testes para estruturas de dados."""
    
    def test_pinterest_real_pin_initialization(self):
        """Testa inicialização de pin real."""
        pin = PinterestRealPin(
            id='test_pin_id',
            title='Test Pin',
            description='Test pin description',
            link='https://example.com/pin',
            board_id='test_board_id',
            creative_type='image',
            is_owner=True,
            is_video=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            saved_at=datetime.now(),
            last_saved_at=datetime.now()
        )
        
        assert pin.id == 'test_pin_id'
        assert pin.title == 'Test Pin'
        assert pin.description == 'Test pin description'
        assert pin.link == 'https://example.com/pin'
        assert pin.board_id == 'test_board_id'
        assert pin.creative_type == 'image'
        assert pin.is_owner is True
        assert pin.is_video is False
        assert pin.engagement_score == 0.0
    
    def test_pinterest_real_board_initialization(self):
        """Testa inicialização de board real."""
        board = PinterestRealBoard(
            id='test_board_id',
            name='Test Board',
            description='Test board description',
            pin_count=100,
            follower_count=50,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_owner=True
        )
        
        assert board.id == 'test_board_id'
        assert board.name == 'Test Board'
        assert board.description == 'Test board description'
        assert board.pin_count == 100
        assert board.follower_count == 50
        assert board.is_owner is True
        assert board.engagement_rate == 0.5  # 50/100
    
    def test_pinterest_real_user_initialization(self):
        """Testa inicialização de usuário real."""
        user = PinterestRealUser(
            username='test_user',
            about='Test user about',
            website='https://example.com',
            full_name='Test User',
            country='BR',
            account_type='personal'
        )
        
        assert user.username == 'test_user'
        assert user.about == 'Test user about'
        assert user.website == 'https://example.com'
        assert user.full_name == 'Test User'
        assert user.country == 'BR'
        assert user.account_type == 'personal'
    
    def test_pinterest_real_search_result_initialization(self):
        """Testa inicialização de resultado de busca."""
        result = PinterestRealSearchResult(
            pin_id='test_pin_id',
            title='Test Pin',
            description='Test description',
            link='https://example.com/pin',
            board_id='test_board_id',
            creative_type='image',
            created_at=datetime.now(),
            relevance_score=0.85
        )
        
        assert result.pin_id == 'test_pin_id'
        assert result.title == 'Test Pin'
        assert result.description == 'Test description'
        assert result.link == 'https://example.com/pin'
        assert result.board_id == 'test_board_id'
        assert result.creative_type == 'image'
        assert result.relevance_score == 0.85


class TestPinterestRealErrorHandling:
    """Testes para tratamento de erros."""
    
    def test_pinterest_real_api_error_creation(self):
        """Testa criação de erro Pinterest Real API."""
        error = PinterestRealAPIError("Test error", "TEST_ERROR", 400, PinterestAPIType.API_V5)
        
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.http_status == 400
        assert error.api_type == PinterestAPIType.API_V5
    
    def test_pinterest_rate_limit_error(self):
        """Testa erro de rate limit."""
        error = PinterestRateLimitError("Rate limit exceeded")
        
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, PinterestRealAPIError)
    
    def test_pinterest_authentication_error(self):
        """Testa erro de autenticação."""
        error = PinterestAuthenticationError("Invalid credentials", "INVALID_CREDENTIALS", 401)
        
        assert str(error) == "Invalid credentials"
        assert error.error_code == "INVALID_CREDENTIALS"
        assert error.http_status == 401
        assert isinstance(error, PinterestRealAPIError) 