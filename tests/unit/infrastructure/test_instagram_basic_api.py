#!/usr/bin/env python3
"""
Testes Unitários - Instagram Basic API
=====================================

Tracing ID: TEST_INSTAGRAM_BASIC_API_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/instagram_basic_api.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 4.1
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import os
import base64
import hashlib
import secrets

from infrastructure.coleta.instagram_basic_api import (
    InstagramBasicAPI, InstagramAuthConfig, InstagramRateLimit,
    InstagramPost, InstagramUser, InstagramBasicCollector,
    create_instagram_basic_client
)


class TestInstagramBasicAPI:
    @pytest.fixture
    def auth_config(self):
        return InstagramAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8080/callback"
        )

    @pytest.fixture
    def rate_limit(self):
        return InstagramRateLimit(
            requests_per_hour=100,
            requests_per_day=1000
        )

    @pytest.fixture
    def api_client(self, auth_config, rate_limit):
        return InstagramBasicAPI(auth_config, rate_limit)

    def test_instagram_auth_config_initialization(self):
        """Testa inicialização da configuração de autenticação."""
        config = InstagramAuthConfig(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://test.com"
        )
        assert config.client_id == "test_id"
        assert config.client_secret == "test_secret"
        assert config.redirect_uri == "http://test.com"
        assert config.scope == "user_profile,user_media"
        assert config.state_parameter is True
        assert config.pkce_enabled is True

    def test_instagram_rate_limit_initialization(self):
        """Testa inicialização da configuração de rate limiting."""
        rate_limit = InstagramRateLimit()
        assert rate_limit.requests_per_hour == 200
        assert rate_limit.requests_per_day == 5000
        assert rate_limit.window_size_hours == 1
        assert rate_limit.window_size_days == 24

    def test_instagram_post_dataclass(self):
        """Testa criação de objeto InstagramPost."""
        post = InstagramPost(
            id="post_id",
            media_type="IMAGE",
            media_url="http://test.com/image.jpg",
            permalink="http://instagram.com/p/post_id",
            timestamp="2023-01-01T00:00:00Z",
            like_count=100,
            comments_count=10,
            caption="Test caption #test #instagram"
        )
        assert post.id == "post_id"
        assert post.media_type == "IMAGE"
        assert post.like_count == 100
        assert post.hashtags == ["#test", "#instagram"]

    def test_instagram_user_dataclass(self):
        """Testa criação de objeto InstagramUser."""
        user = InstagramUser(
            id="user_id",
            username="testuser",
            account_type="PERSONAL",
            media_count=50,
            profile_picture_url="http://test.com/profile.jpg"
        )
        assert user.id == "user_id"
        assert user.username == "testuser"
        assert user.account_type == "PERSONAL"
        assert user.media_count == 50

    def test_instagram_basic_api_initialization(self, auth_config, rate_limit):
        """Testa inicialização do cliente Instagram Basic API."""
        client = InstagramBasicAPI(auth_config, rate_limit)
        assert client.config == auth_config
        assert client.rate_limit == rate_limit
        assert client.access_token is None
        assert client.token_expires_at is None
        assert client.request_count_hour == 0
        assert client.request_count_day == 0

    def test_generate_pkce_challenge(self, api_client):
        """Testa geração de challenge PKCE."""
        code_verifier, code_challenge = api_client._generate_pkce_challenge()
        
        assert len(code_verifier) > 0
        assert len(code_challenge) > 0
        assert code_verifier != code_challenge
        
        # Verificar se code_challenge é SHA256 do code_verifier
        expected_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        assert code_challenge == expected_challenge

    def test_get_authorization_url_without_pkce(self, auth_config):
        """Testa geração de URL de autorização sem PKCE."""
        auth_config.pkce_enabled = False
        client = InstagramBasicAPI(auth_config)
        
        auth_url, code_verifier = client.get_authorization_url("test_state")
        
        assert "api.instagram.com/oauth/authorize" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "redirect_uri=http%3A//localhost%3A8080/callback" in auth_url
        assert "state=test_state" in auth_url
        assert code_verifier is None

    def test_get_authorization_url_with_pkce(self, api_client):
        """Testa geração de URL de autorização com PKCE."""
        auth_url, code_verifier = api_client.get_authorization_url("test_state")
        
        assert "api.instagram.com/oauth/authorize" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "code_challenge=" in auth_url
        assert "code_challenge_method=S256" in auth_url
        assert code_verifier is not None

    @patch('requests.Session.post')
    def test_exchange_code_for_token_success(self, mock_post, api_client):
        """Testa troca de código por token com sucesso."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = api_client.exchange_code_for_token("test_code", "test_verifier")
        
        assert result['access_token'] == 'test_access_token'
        assert api_client.access_token == 'test_access_token'
        assert api_client.token_expires_at is not None

    @patch('requests.Session.post')
    def test_exchange_code_for_token_without_pkce(self, mock_post, api_client):
        """Testa troca de código por token sem PKCE."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = api_client.exchange_code_for_token("test_code")
        
        assert result['access_token'] == 'test_access_token'
        assert 'code_verifier' not in mock_post.call_args[1]['data']

    def test_check_rate_limit_within_limits(self, api_client):
        """Testa verificação de rate limit dentro dos limites."""
        api_client.request_count_hour = 50
        api_client.request_count_day = 500
        
        result = api_client._check_rate_limit()
        assert result is True

    def test_check_rate_limit_exceeded_hourly(self, api_client):
        """Testa verificação de rate limit excedido por hora."""
        api_client.request_count_hour = 101  # Excede limite de 100
        api_client.request_count_day = 500
        
        result = api_client._check_rate_limit()
        assert result is False

    def test_check_rate_limit_exceeded_daily(self, api_client):
        """Testa verificação de rate limit excedido diariamente."""
        api_client.request_count_hour = 50
        api_client.request_count_day = 1001  # Excede limite de 1000
        
        result = api_client._check_rate_limit()
        assert result is False

    def test_increment_request_count(self, api_client):
        """Testa incremento dos contadores de requisição."""
        initial_hour = api_client.request_count_hour
        initial_day = api_client.request_count_day
        
        api_client._increment_request_count()
        
        assert api_client.request_count_hour == initial_hour + 1
        assert api_client.request_count_day == initial_day + 1

    @patch.object(InstagramBasicAPI, '_check_rate_limit')
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get, mock_check_rate_limit, api_client):
        """Testa requisição bem-sucedida."""
        mock_check_rate_limit.return_value = True
        api_client.access_token = "test_token"
        
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = api_client._make_request('/me')
        
        assert result == {'data': 'test_data'}
        mock_get.assert_called_once()
        assert 'access_token=test_token' in mock_get.call_args[1]['params']

    @patch.object(InstagramBasicAPI, '_check_rate_limit')
    def test_make_request_rate_limit_exceeded(self, mock_check_rate_limit, api_client):
        """Testa requisição com rate limit excedido."""
        mock_check_rate_limit.return_value = False
        
        with pytest.raises(Exception, match="Rate limit excedido"):
            api_client._make_request('/me')

    def test_make_request_no_token(self, api_client):
        """Testa requisição sem token de acesso."""
        with pytest.raises(Exception, match="Token de acesso não configurado"):
            api_client._make_request('/me')

    @patch.object(InstagramBasicAPI, '_make_request')
    def test_get_user_profile_success(self, mock_make_request, api_client):
        """Testa obtenção de perfil do usuário."""
        mock_make_request.return_value = {
            'id': 'user_id',
            'username': 'testuser',
            'account_type': 'PERSONAL',
            'media_count': 50,
            'profile_picture_url': 'http://test.com/profile.jpg'
        }
        
        user = api_client.get_user_profile()
        
        assert isinstance(user, InstagramUser)
        assert user.id == 'user_id'
        assert user.username == 'testuser'
        assert user.account_type == 'PERSONAL'
        assert user.media_count == 50

    @patch.object(InstagramBasicAPI, '_make_request')
    def test_get_user_media_success(self, mock_make_request, api_client):
        """Testa obtenção de mídia do usuário."""
        mock_make_request.return_value = {
            'data': [{
                'id': 'post_id',
                'media_type': 'IMAGE',
                'media_url': 'http://test.com/image.jpg',
                'permalink': 'http://instagram.com/p/post_id',
                'timestamp': '2023-01-01T00:00:00Z',
                'like_count': 100,
                'comments_count': 10,
                'caption': 'Test caption #test #instagram'
            }]
        }
        
        posts = api_client.get_user_media(limit=25)
        
        assert len(posts) == 1
        assert isinstance(posts[0], InstagramPost)
        assert posts[0].id == 'post_id'
        assert posts[0].hashtags == ['#test', '#instagram']

    @patch.object(InstagramBasicAPI, '_make_request')
    def test_get_user_media_with_pagination(self, mock_make_request, api_client):
        """Testa obtenção de mídia com paginação."""
        mock_make_request.return_value = {'data': []}
        
        api_client.get_user_media(limit=10, after="cursor_123")
        
        call_args = mock_make_request.call_args
        assert call_args[1]['params']['limit'] == 10
        assert call_args[1]['params']['after'] == "cursor_123"

    @patch.object(InstagramBasicAPI, '_make_request')
    def test_get_media_by_id_success(self, mock_make_request, api_client):
        """Testa obtenção de mídia por ID."""
        mock_make_request.return_value = {
            'id': 'post_id',
            'media_type': 'VIDEO',
            'media_url': 'http://test.com/video.mp4',
            'permalink': 'http://instagram.com/p/post_id',
            'timestamp': '2023-01-01T00:00:00Z',
            'like_count': 200,
            'comments_count': 20,
            'caption': 'Video caption #video #test'
        }
        
        post = api_client.get_media_by_id('post_id')
        
        assert isinstance(post, InstagramPost)
        assert post.id == 'post_id'
        assert post.media_type == 'VIDEO'
        assert post.hashtags == ['#video', '#test']

    @patch.object(InstagramBasicAPI, '_make_request')
    def test_get_media_children_success(self, mock_make_request, api_client):
        """Testa obtenção de posts filhos."""
        mock_make_request.return_value = {
            'data': [{
                'id': 'child_id',
                'media_type': 'IMAGE',
                'media_url': 'http://test.com/child.jpg',
                'permalink': 'http://instagram.com/p/child_id',
                'timestamp': '2023-01-01T00:00:00Z'
            }]
        }
        
        posts = api_client.get_media_children('parent_id')
        
        assert len(posts) == 1
        assert isinstance(posts[0], InstagramPost)
        assert posts[0].id == 'child_id'

    @patch('requests.Session.post')
    def test_refresh_token_success(self, mock_post, api_client):
        """Testa renovação de token."""
        api_client.access_token = "old_token"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'new_token',
            'expires_in': 7200
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = api_client.refresh_token()
        
        assert result['access_token'] == 'new_token'
        assert api_client.access_token == 'new_token'

    def test_refresh_token_no_token(self, api_client):
        """Testa renovação de token sem token existente."""
        with pytest.raises(Exception, match="Token de acesso não configurado"):
            api_client.refresh_token()

    def test_is_token_expired_no_token(self, api_client):
        """Testa verificação de expiração sem token."""
        assert api_client.is_token_expired() is True

    def test_is_token_expired_valid_token(self, api_client):
        """Testa verificação de expiração com token válido."""
        api_client.token_expires_at = datetime.now() + timedelta(hours=2)
        assert api_client.is_token_expired() is False

    def test_is_token_expired_expiring_soon(self, api_client):
        """Testa verificação de expiração com token expirando em breve."""
        api_client.token_expires_at = datetime.now() + timedelta(minutes=30)
        assert api_client.is_token_expired() is True

    def test_get_rate_limit_status(self, api_client):
        """Testa obtenção do status do rate limiting."""
        api_client.request_count_hour = 50
        api_client.request_count_day = 500
        api_client.last_request_hour = datetime.now()
        api_client.last_request_day = datetime.now()
        
        status = api_client.get_rate_limit_status()
        
        assert status['requests_hour'] == 50
        assert status['requests_day'] == 500
        assert status['limit_hour'] == 100
        assert status['limit_day'] == 1000
        assert status['remaining_hour'] == 50
        assert status['remaining_day'] == 500


class TestInstagramBasicCollector:
    @pytest.fixture
    def api_client(self):
        config = InstagramAuthConfig(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://test.com"
        )
        return InstagramBasicAPI(config)

    @pytest.fixture
    def collector(self, api_client):
        return InstagramBasicCollector(api_client)

    @patch.object(InstagramBasicAPI, 'is_token_expired')
    @patch.object(InstagramBasicAPI, 'refresh_token')
    @patch.object(InstagramBasicAPI, 'get_user_profile')
    @patch.object(InstagramBasicAPI, 'get_user_media')
    def test_collect_user_data_success(self, mock_get_media, mock_get_profile, mock_refresh, mock_expired, collector):
        """Testa coleta de dados do usuário."""
        mock_expired.return_value = False
        
        mock_user = InstagramUser(
            id="user_id",
            username="testuser",
            account_type="PERSONAL",
            media_count=2
        )
        mock_get_profile.return_value = mock_user
        
        mock_posts = [
            InstagramPost(
                id="post1",
                media_type="IMAGE",
                media_url="http://test.com/1.jpg",
                permalink="http://instagram.com/p/1",
                timestamp="2023-01-01T00:00:00Z",
                like_count=100,
                comments_count=10,
                caption="Post 1 #test"
            ),
            InstagramPost(
                id="post2",
                media_type="VIDEO",
                media_url="http://test.com/2.mp4",
                permalink="http://instagram.com/p/2",
                timestamp="2023-01-02T00:00:00Z",
                like_count=200,
                comments_count=20,
                caption="Post 2 #instagram"
            )
        ]
        mock_get_media.return_value = mock_posts
        
        result = collector.collect_user_data()
        
        assert result['user']['id'] == 'user_id'
        assert len(result['posts']) == 2
        assert result['metrics']['total_posts'] == 2
        assert result['metrics']['total_likes'] == 300
        assert result['metrics']['total_comments'] == 30
        assert result['metrics']['avg_engagement'] == 165.0
        assert len(result['metrics']['hashtags']) == 2

    @patch.object(InstagramBasicAPI, 'get_user_media')
    def test_collect_hashtag_data_success(self, mock_get_media, collector):
        """Testa coleta de dados de hashtag."""
        mock_posts = [
            InstagramPost(
                id="post1",
                media_type="IMAGE",
                media_url="http://test.com/1.jpg",
                permalink="http://instagram.com/p/1",
                timestamp="2023-01-01T00:00:00Z",
                like_count=100,
                comments_count=10,
                caption="Post with #test hashtag"
            )
        ]
        mock_get_media.return_value = mock_posts
        
        result = collector.collect_hashtag_data("#test")
        
        assert result['hashtag'] == "#test"
        assert result['posts_found'] == 1
        assert result['total_likes'] == 100
        assert result['total_comments'] == 10
        assert result['avg_engagement'] == 110.0

    @patch.object(InstagramBasicAPI, 'get_user_media')
    def test_collect_hashtag_data_not_found(self, mock_get_media, collector):
        """Testa coleta de dados de hashtag não encontrada."""
        mock_posts = [
            InstagramPost(
                id="post1",
                media_type="IMAGE",
                media_url="http://test.com/1.jpg",
                permalink="http://instagram.com/p/1",
                timestamp="2023-01-01T00:00:00Z",
                like_count=100,
                comments_count=10,
                caption="Post without hashtag"
            )
        ]
        mock_get_media.return_value = mock_posts
        
        result = collector.collect_hashtag_data("#nonexistent")
        
        assert result['hashtag'] == "#nonexistent"
        assert result['posts_found'] == 0
        assert result['total_likes'] == 0
        assert result['total_comments'] == 0
        assert result['avg_engagement'] == 0


class TestCreateInstagramBasicClient:
    @patch.dict(os.environ, {
        'INSTAGRAM_CLIENT_ID': 'env_client_id',
        'INSTAGRAM_CLIENT_SECRET': 'env_client_secret',
        'INSTAGRAM_REDIRECT_URI': 'http://env.com/callback'
    })
    def test_create_instagram_basic_client_with_env_vars(self):
        """Testa criação de cliente com variáveis de ambiente."""
        client = create_instagram_basic_client()
        assert client.config.client_id == 'env_client_id'
        assert client.config.client_secret == 'env_client_secret'
        assert client.config.redirect_uri == 'http://env.com/callback'

    def test_create_instagram_basic_client_with_params(self):
        """Testa criação de cliente com parâmetros."""
        client = create_instagram_basic_client(
            client_id="param_client_id",
            client_secret="param_client_secret",
            redirect_uri="http://param.com/callback"
        )
        assert client.config.client_id == 'param_client_id'
        assert client.config.client_secret == 'param_client_secret'
        assert client.config.redirect_uri == 'http://param.com/callback'

    def test_create_instagram_basic_client_missing_credentials(self):
        """Testa criação de cliente sem credenciais."""
        with pytest.raises(ValueError, match="Instagram credentials não configuradas"):
            create_instagram_basic_client()


if __name__ == "__main__":
    pytest.main([__file__]) 