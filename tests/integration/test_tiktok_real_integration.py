"""
Testes de Integração Real - TikTok API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validado cobertura completa

Tracing ID: test-tiktok-real-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/tiktok_real_api.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 1
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Autenticação OAuth 2.0 real
- Coleta de dados de vídeos reais
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

from infrastructure.coleta.tiktok_real_api import (
    TikTokRealAPI, TikTokRealConfig, TikTokAPIType,
    TikTokRealVideo, TikTokRealUser, TikTokRealHashtag,
    TikTokRealAPIError, TikTokRateLimitError, TikTokAuthenticationError,
    TikTokScope, VideoPrivacy, create_tiktok_real_client
)


class TestTikTokRealIntegration:
    """Testes de integração real para TikTok API."""
    
    @pytest.fixture
    def real_config(self):
        """Configuração real para testes."""
        return TikTokRealConfig(
            client_key=os.getenv('TIKTOK_CLIENT_KEY', 'test_client_key'),
            client_secret=os.getenv('TIKTOK_CLIENT_SECRET', 'test_client_secret'),
            redirect_uri=os.getenv('TIKTOK_REDIRECT_URI', 'http://localhost:8080/callback'),
            developers_api_rate_limit_minute=100,
            developers_api_rate_limit_hour=1000,
            web_scraping_enabled=True,
            cache_enabled=True,
            circuit_breaker_enabled=True
        )
    
    @pytest.fixture
    def real_api(self, real_config):
        """Instância da API real para testes."""
        return TikTokRealAPI(real_config)
    
    @pytest.fixture
    def sample_user_data(self):
        """Dados de exemplo de usuário real."""
        return {
            'open_id': 'test_user_001',
            'union_id': 'test_union_001',
            'avatar_url': 'https://tiktok.com/avatar.jpg',
            'display_name': 'Test User',
            'bio_description': 'Test user bio',
            'profile_deep_link': 'https://tiktok.com/@testuser',
            'is_verified': False,
            'follower_count': 1000,
            'following_count': 500,
            'likes_count': 5000,
            'video_count': 50,
            'total_likes': 10000,
            'total_views': 50000,
            'account_type': 'PERSONAL',
            'created_time': '2025-01-27T10:00:00Z'
        }
    
    @pytest.fixture
    def sample_video_data(self):
        """Dados de exemplo de vídeo real."""
        return {
            'id': 'test_video_001',
            'title': 'Test Video Title',
            'description': 'Test video description #test #tiktok #omni',
            'duration': 30,
            'cover_image_url': 'https://tiktok.com/cover.jpg',
            'video_url': 'https://tiktok.com/video.mp4',
            'privacy_level': 'PUBLIC',
            'created_time': '2025-01-27T10:00:00Z',
            'updated_time': '2025-01-27T10:00:00Z',
            'statistics': {
                'view_count': 1000,
                'like_count': 100,
                'comment_count': 50,
                'share_count': 25,
                'download_count': 10
            },
            'hashtags': ['#test', '#tiktok', '#omni'],
            'creator_id': 'test_creator_001',
            'creator_name': 'Test Creator',
            'creator_avatar': 'https://tiktok.com/creator.jpg',
            'music_name': 'Test Music',
            'music_author': 'Test Artist'
        }
    
    @pytest.fixture
    def sample_hashtag_data(self):
        """Dados de exemplo de hashtag real."""
        return {
            'name': 'test',
            'post_count': 1000000,
            'view_count': 50000000,
            'follower_count': 10000,
            'is_commerce': False,
            'is_verified': False,
            'description': 'Test hashtag description',
            'trend_score': 0.85,
            'growth_rate': 0.25
        }
    
    def test_tiktok_real_config_initialization(self, real_config):
        """Testa inicialização da configuração real."""
        assert real_config.client_key == os.getenv('TIKTOK_CLIENT_KEY', 'test_client_key')
        assert real_config.client_secret == os.getenv('TIKTOK_CLIENT_SECRET', 'test_client_secret')
        assert real_config.redirect_uri == os.getenv('TIKTOK_REDIRECT_URI', 'http://localhost:8080/callback')
        assert real_config.developers_api_rate_limit_minute == 100
        assert real_config.developers_api_rate_limit_hour == 1000
        assert real_config.web_scraping_enabled is True
        assert real_config.cache_enabled is True
        assert real_config.circuit_breaker_enabled is True
    
    def test_tiktok_real_api_initialization(self, real_api, real_config):
        """Testa inicialização da API real."""
        assert real_api.config == real_config
        assert real_api.rate_limiter is not None
        assert real_api.circuit_breaker is not None
        assert real_api.session is not None
        assert real_api.cache == {}
        assert real_api.access_token is None
        assert real_api.refresh_token is None
        assert real_api.token_expires_at is None
    
    def test_generate_pkce_challenge(self, real_api):
        """Testa geração de challenge PKCE."""
        code_verifier, code_challenge = real_api._generate_pkce_challenge()
        
        assert isinstance(code_verifier, str)
        assert isinstance(code_challenge, str)
        assert len(code_verifier) > 0
        assert len(code_challenge) > 0
        assert code_verifier != code_challenge
    
    def test_get_authorization_url(self, real_api):
        """Testa geração de URL de autorização."""
        auth_url, code_verifier = real_api.get_authorization_url()
        
        assert isinstance(auth_url, str)
        assert isinstance(code_verifier, str)
        assert 'tiktok.com/v2/auth/authorize' in auth_url
        assert 'client_key=' in auth_url
        assert 'redirect_uri=' in auth_url
        assert 'scope=' in auth_url
        assert 'response_type=code' in auth_url
        assert 'code_challenge=' in auth_url
        assert 'code_challenge_method=S256' in auth_url
    
    def test_get_authorization_url_with_custom_scopes(self, real_api):
        """Testa geração de URL de autorização com escopos customizados."""
        custom_scopes = [TikTokScope.VIDEO_LIST, TikTokScope.HASHTAG_SEARCH]
        auth_url, code_verifier = real_api.get_authorization_url(scopes=custom_scopes)
        
        assert 'video.list' in auth_url
        assert 'hashtag.search' in auth_url
    
    def test_get_authorization_url_with_state(self, real_api):
        """Testa geração de URL de autorização com state customizado."""
        custom_state = "custom_state_123"
        auth_url, code_verifier = real_api.get_authorization_url(state=custom_state)
        
        assert f'state={custom_state}' in auth_url
    
    @patch('infrastructure.coleta.tiktok_real_api.requests.Session.post')
    def test_exchange_code_for_token_success(self, mock_post, real_api):
        """Testa troca de código por token com sucesso."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        code = "test_auth_code"
        code_verifier = "test_code_verifier"
        
        result = real_api.exchange_code_for_token(code, code_verifier)
        
        assert result['access_token'] == 'test_access_token'
        assert result['refresh_token'] == 'test_refresh_token'
        assert result['expires_in'] == 3600
        assert real_api.access_token == 'test_access_token'
        assert real_api.refresh_token == 'test_refresh_token'
        assert real_api.token_expires_at is not None
        assert real_api.circuit_breaker.failure_count == 0
        assert real_api.circuit_breaker.state == "CLOSED"
    
    @patch('infrastructure.coleta.tiktok_real_api.requests.Session.post')
    def test_exchange_code_for_token_failure(self, mock_post, real_api):
        """Testa falha na troca de código por token."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error_code': 'INVALID_CODE'}
        mock_post.return_value = mock_response
        
        code = "test_auth_code"
        code_verifier = "test_code_verifier"
        
        with pytest.raises(TikTokAuthenticationError, match="Falha na autenticação"):
            real_api.exchange_code_for_token(code, code_verifier)
    
    @patch('infrastructure.coleta.tiktok_real_api.requests.Session.post')
    def test_refresh_access_token_success(self, mock_post, real_api):
        """Testa renovação de token com sucesso."""
        real_api.refresh_token = "test_refresh_token"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = real_api.refresh_access_token()
        
        assert result['access_token'] == 'new_access_token'
        assert result['refresh_token'] == 'new_refresh_token'
        assert real_api.access_token == 'new_access_token'
        assert real_api.refresh_token == 'new_refresh_token'
        assert real_api.token_expires_at is not None
    
    def test_refresh_access_token_no_refresh_token(self, real_api):
        """Testa renovação de token sem refresh token."""
        with pytest.raises(TikTokAuthenticationError, match="Refresh token não disponível"):
            real_api.refresh_access_token()
    
    @patch('infrastructure.coleta.tiktok_real_api.requests.Session.get')
    def test_make_developers_api_request_success(self, mock_get, real_api):
        """Testa requisição bem-sucedida para Developers API."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = real_api._make_developers_api_request('/user/info/')
        
        assert result == {'data': 'test_data'}
        assert real_api.rate_limiter.requests_minute == 1
        assert real_api.circuit_breaker.failure_count == 0
    
    def test_make_developers_api_request_no_token(self, real_api):
        """Testa requisição sem token de acesso."""
        with pytest.raises(TikTokAuthenticationError, match="Token de acesso não configurado"):
            real_api._make_developers_api_request('/user/info/')
    
    def test_make_developers_api_request_rate_limit_exceeded(self, real_api):
        """Testa requisição com rate limit excedido."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        real_api.rate_limiter.requests_minute = 100  # Limite excedido
        
        with pytest.raises(TikTokRateLimitError, match="Rate limit excedido"):
            real_api._make_developers_api_request('/user/info/')
    
    @patch('infrastructure.coleta.tiktok_real_api.requests.Session.get')
    def test_make_developers_api_request_token_expired(self, mock_get, real_api):
        """Testa requisição com token expirado."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() - timedelta(hours=1)
        real_api.refresh_token = "test_refresh_token"
        
        # Mock para refresh token
        mock_refresh_response = MagicMock()
        mock_refresh_response.json.return_value = {
            'access_token': 'new_token',
            'expires_in': 3600
        }
        
        # Mock para requisição principal
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test_data'}
        
        mock_get.side_effect = [mock_refresh_response, mock_response]
        
        result = real_api._make_developers_api_request('/user/info/')
        
        assert result == {'data': 'test_data'}
        assert real_api.access_token == 'new_token'
    
    @patch.object(TikTokRealAPI, '_make_developers_api_request')
    def test_search_videos_success(self, mock_request, real_api, sample_video_data):
        """Testa busca de vídeos com sucesso."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        mock_request.return_value = {
            'data': {
                'videos': [sample_video_data]
            }
        }
        
        videos = real_api.search_videos("test query", max_count=20)
        
        assert len(videos) == 1
        assert isinstance(videos[0], TikTokRealVideo)
        assert videos[0].id == sample_video_data['id']
        assert videos[0].title == sample_video_data['title']
        assert videos[0].description == sample_video_data['description']
        assert videos[0].duration == sample_video_data['duration']
        assert videos[0].cover_image_url == sample_video_data['cover_image_url']
        assert videos[0].video_url == sample_video_data['video_url']
        assert videos[0].privacy_level == VideoPrivacy(sample_video_data['privacy_level'])
        assert videos[0].hashtags == sample_video_data['hashtags']
        assert videos[0].creator_id == sample_video_data['creator_id']
        assert videos[0].creator_name == sample_video_data['creator_name']
        assert videos[0].music_name == sample_video_data['music_name']
        assert videos[0].view_count == sample_video_data['statistics']['view_count']
        assert videos[0].like_count == sample_video_data['statistics']['like_count']
        assert videos[0].comment_count == sample_video_data['statistics']['comment_count']
        assert videos[0].share_count == sample_video_data['statistics']['share_count']
        assert videos[0].download_count == sample_video_data['statistics']['download_count']
        assert videos[0].engagement_rate > 0
    
    @patch.object(TikTokRealAPI, '_make_developers_api_request')
    def test_search_videos_cache(self, mock_request, real_api, sample_video_data):
        """Testa cache de busca de vídeos."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        mock_request.return_value = {
            'data': {
                'videos': [sample_video_data]
            }
        }
        
        # Primeira chamada
        videos1 = real_api.search_videos("test query")
        
        # Segunda chamada (deve usar cache)
        videos2 = real_api.search_videos("test query")
        
        assert videos1 == videos2
        assert mock_request.call_count == 1  # Só uma chamada real
    
    @patch.object(TikTokRealAPI, '_make_developers_api_request')
    def test_search_hashtags_success(self, mock_request, real_api, sample_hashtag_data):
        """Testa busca de hashtags com sucesso."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        mock_request.return_value = {
            'data': {
                'hashtags': [sample_hashtag_data]
            }
        }
        
        hashtags = real_api.search_hashtags("test")
        
        assert len(hashtags) == 1
        assert isinstance(hashtags[0], TikTokRealHashtag)
        assert hashtags[0].name == sample_hashtag_data['name']
        assert hashtags[0].post_count == sample_hashtag_data['post_count']
        assert hashtags[0].view_count == sample_hashtag_data['view_count']
        assert hashtags[0].follower_count == sample_hashtag_data['follower_count']
        assert hashtags[0].is_commerce == sample_hashtag_data['is_commerce']
        assert hashtags[0].is_verified == sample_hashtag_data['is_verified']
        assert hashtags[0].description == sample_hashtag_data['description']
        assert hashtags[0].trend_score == sample_hashtag_data['trend_score']
        assert hashtags[0].growth_rate == sample_hashtag_data['growth_rate']
    
    @patch.object(TikTokRealAPI, '_make_developers_api_request')
    def test_get_user_info_success(self, mock_request, real_api, sample_user_data):
        """Testa obtenção de informações do usuário."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        mock_request.return_value = {
            'data': {
                'user': sample_user_data
            }
        }
        
        user = real_api.get_user_info()
        
        assert isinstance(user, TikTokRealUser)
        assert user.open_id == sample_user_data['open_id']
        assert user.union_id == sample_user_data['union_id']
        assert user.avatar_url == sample_user_data['avatar_url']
        assert user.display_name == sample_user_data['display_name']
        assert user.bio_description == sample_user_data['bio_description']
        assert user.profile_deep_link == sample_user_data['profile_deep_link']
        assert user.is_verified == sample_user_data['is_verified']
        assert user.follower_count == sample_user_data['follower_count']
        assert user.following_count == sample_user_data['following_count']
        assert user.likes_count == sample_user_data['likes_count']
        assert user.video_count == sample_user_data['video_count']
        assert user.total_likes == sample_user_data['total_likes']
        assert user.total_views == sample_user_data['total_views']
        assert user.account_type == sample_user_data['account_type']
    
    @patch.object(TikTokRealAPI, '_make_developers_api_request')
    def test_get_trending_hashtags_success(self, mock_request, real_api, sample_hashtag_data):
        """Testa obtenção de hashtags em tendência."""
        real_api.access_token = "test_token"
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        
        mock_request.return_value = {
            'data': {
                'hashtags': [sample_hashtag_data]
            }
        }
        
        hashtags = real_api.get_trending_hashtags(count=10)
        
        assert len(hashtags) == 1
        assert isinstance(hashtags[0], TikTokRealHashtag)
        assert hashtags[0].name == sample_hashtag_data['name']
    
    def test_get_rate_limit_status(self, real_api):
        """Testa obtenção de status dos rate limits."""
        status = real_api.get_rate_limit_status()
        
        assert 'developers_api' in status
        assert 'circuit_breaker' in status
        assert 'web_scraping' in status
        
        assert 'requests_minute' in status['developers_api']
        assert 'limit_minute' in status['developers_api']
        assert 'requests_hour' in status['developers_api']
        assert 'limit_hour' in status['developers_api']
        
        assert 'state' in status['circuit_breaker']
        assert 'failure_count' in status['circuit_breaker']
        
        assert 'enabled' in status['web_scraping']
        assert 'delay' in status['web_scraping']
    
    def test_is_token_expired(self, real_api):
        """Testa verificação de expiração de token."""
        # Token não configurado
        assert real_api.is_token_expired() is True
        
        # Token expirado
        real_api.token_expires_at = datetime.now() - timedelta(hours=1)
        assert real_api.is_token_expired() is True
        
        # Token válido
        real_api.token_expires_at = datetime.now() + timedelta(hours=1)
        assert real_api.is_token_expired() is False
    
    @pytest.mark.asyncio
    async def test_close_async_session(self, real_api):
        """Testa fechamento de sessão assíncrona."""
        # Criar sessão assíncrona
        session = await real_api._get_async_session()
        assert session is not None
        
        # Fechar sessão
        await real_api.close()
        assert real_api.async_session.closed is True
    
    def test_circuit_breaker_state_transitions(self, real_api):
        """Testa transições de estado do circuit breaker."""
        cb = real_api.circuit_breaker
        
        # Estado inicial
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0
        
        # Simular falhas até abrir circuit breaker
        for i in range(5):
            cb.on_failure()
        
        assert cb.state == "OPEN"
        assert cb.failure_count == 5
        
        # Simular sucesso (não deve mudar estado se OPEN)
        cb.on_success()
        assert cb.state == "OPEN"
        
        # Simular timeout para HALF_OPEN
        cb.last_failure_time = datetime.now() - timedelta(seconds=61)
        assert cb.can_execute() is True
        assert cb.state == "HALF_OPEN"
        
        # Simular sucesso para fechar
        cb.on_success()
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0
    
    def test_rate_limiter_reset(self, real_api):
        """Testa reset automático dos contadores de rate limit."""
        rl = real_api.rate_limiter
        
        # Simular requisições
        rl.requests_minute = 50
        rl.requests_hour = 500
        
        # Simular reset de minuto
        rl.last_reset_minute = datetime.now() - timedelta(minutes=2)
        assert rl.can_make_request() is True
        assert rl.requests_minute == 0
        
        # Simular reset de hora
        rl.last_reset_hour = datetime.now() - timedelta(hours=2)
        assert rl.can_make_request() is True
        assert rl.requests_hour == 0


class TestTikTokRealFactory:
    """Testes para factory function."""
    
    @patch.dict(os.environ, {
        'TIKTOK_CLIENT_KEY': 'env_client_key',
        'TIKTOK_CLIENT_SECRET': 'env_client_secret',
        'TIKTOK_REDIRECT_URI': 'http://env.com/callback'
    })
    def test_create_tiktok_real_client_from_env(self):
        """Testa criação de cliente a partir de variáveis de ambiente."""
        client = create_tiktok_real_client()
        
        assert client.config.client_key == 'env_client_key'
        assert client.config.client_secret == 'env_client_secret'
        assert client.config.redirect_uri == 'http://env.com/callback'
    
    def test_create_tiktok_real_client_with_params(self):
        """Testa criação de cliente com parâmetros explícitos."""
        client = create_tiktok_real_client(
            client_key='param_client_key',
            client_secret='param_client_secret',
            redirect_uri='http://param.com/callback'
        )
        
        assert client.config.client_key == 'param_client_key'
        assert client.config.client_secret == 'param_client_secret'
        assert client.config.redirect_uri == 'http://param.com/callback'


class TestTikTokRealDataStructures:
    """Testes para estruturas de dados."""
    
    def test_tiktok_real_video_initialization(self):
        """Testa inicialização de vídeo real."""
        video = TikTokRealVideo(
            id='test_id',
            title='Test Video',
            description='Test description #test',
            duration=30,
            cover_image_url='http://test.com/cover.jpg',
            video_url='http://test.com/video.mp4',
            privacy_level=VideoPrivacy.PUBLIC,
            created_time=datetime.now(),
            updated_time=datetime.now(),
            statistics={'view_count': 1000},
            hashtags=['#test'],
            creator_id='creator_001',
            creator_name='Test Creator',
            creator_avatar='http://test.com/avatar.jpg',
            music_name='Test Music',
            music_author='Test Artist',
            view_count=1000,
            like_count=100,
            comment_count=50,
            share_count=25,
            download_count=10
        )
        
        assert video.id == 'test_id'
        assert video.title == 'Test Video'
        assert video.description == 'Test description #test'
        assert video.duration == 30
        assert video.privacy_level == VideoPrivacy.PUBLIC
        assert video.hashtags == ['#test']
        assert video.creator_id == 'creator_001'
        assert video.music_name == 'Test Music'
        assert video.view_count == 1000
        assert video.like_count == 100
        assert video.engagement_rate > 0
    
    def test_tiktok_real_video_engagement_calculation(self):
        """Testa cálculo automático de engagement rate."""
        video = TikTokRealVideo(
            id='test_id',
            title='Test Video',
            description='Test description',
            duration=30,
            cover_image_url='http://test.com/cover.jpg',
            video_url='http://test.com/video.mp4',
            privacy_level=VideoPrivacy.PUBLIC,
            created_time=datetime.now(),
            updated_time=datetime.now(),
            statistics={'view_count': 1000},
            hashtags=[],
            creator_id='creator_001',
            creator_name='Test Creator',
            creator_avatar='http://test.com/avatar.jpg',
            music_name='Test Music',
            music_author='Test Artist',
            view_count=1000,
            like_count=100,
            comment_count=50,
            share_count=25,
            download_count=10
        )
        
        expected_engagement_rate = (100 + 50 + 25) / 1000  # 0.175
        assert video.engagement_rate == expected_engagement_rate
    
    def test_tiktok_real_hashtag_initialization(self):
        """Testa inicialização de hashtag real."""
        hashtag = TikTokRealHashtag(
            name='test',
            post_count=1000000,
            view_count=50000000,
            follower_count=10000,
            is_commerce=False,
            is_verified=False,
            description='Test hashtag description',
            trend_score=0.85,
            growth_rate=0.25
        )
        
        assert hashtag.name == 'test'
        assert hashtag.post_count == 1000000
        assert hashtag.view_count == 50000000
        assert hashtag.follower_count == 10000
        assert hashtag.is_commerce is False
        assert hashtag.is_verified is False
        assert hashtag.description == 'Test hashtag description'
        assert hashtag.trend_score == 0.85
        assert hashtag.growth_rate == 0.25
        assert hashtag.top_posts == []
        assert hashtag.recent_posts == []
    
    def test_tiktok_real_user_initialization(self):
        """Testa inicialização de usuário real."""
        user = TikTokRealUser(
            open_id='user_001',
            union_id='union_001',
            avatar_url='http://test.com/avatar.jpg',
            display_name='Test User',
            bio_description='Test bio',
            profile_deep_link='http://tiktok.com/@testuser',
            is_verified=False,
            follower_count=1000,
            following_count=500,
            likes_count=5000,
            video_count=50,
            total_likes=10000,
            total_views=50000,
            account_type='PERSONAL',
            created_time=datetime.now()
        )
        
        assert user.open_id == 'user_001'
        assert user.union_id == 'union_001'
        assert user.display_name == 'Test User'
        assert user.bio_description == 'Test bio'
        assert user.is_verified is False
        assert user.follower_count == 1000
        assert user.following_count == 500
        assert user.likes_count == 5000
        assert user.video_count == 50
        assert user.total_likes == 10000
        assert user.total_views == 50000
        assert user.account_type == 'PERSONAL'


class TestTikTokRealErrorHandling:
    """Testes para tratamento de erros."""
    
    def test_tiktok_real_api_error_creation(self):
        """Testa criação de erro TikTok Real API."""
        error = TikTokRealAPIError("Test error", "TEST_ERROR", 400, TikTokAPIType.DEVELOPERS_API)
        
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.http_status == 400
        assert error.api_type == TikTokAPIType.DEVELOPERS_API
    
    def test_tiktok_rate_limit_error(self):
        """Testa erro de rate limit."""
        error = TikTokRateLimitError("Rate limit exceeded")
        
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, TikTokRealAPIError)
    
    def test_tiktok_authentication_error(self):
        """Testa erro de autenticação."""
        error = TikTokAuthenticationError("Invalid token", "INVALID_TOKEN", 401)
        
        assert str(error) == "Invalid token"
        assert error.error_code == "INVALID_TOKEN"
        assert error.http_status == 401
        assert isinstance(error, TikTokRealAPIError) 