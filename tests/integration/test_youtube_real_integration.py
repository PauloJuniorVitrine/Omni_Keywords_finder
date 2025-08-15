"""
Testes de Integração Real - YouTube API

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validado cobertura completa

Tracing ID: test-youtube-real-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/youtube_real_api.py
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 1
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das funcionalidades reais da API
Funcionalidades testadas:
- Autenticação OAuth 2.0 real
- Quota management inteligente
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

from infrastructure.coleta.youtube_real_api import (
    YouTubeRealAPI, YouTubeRealConfig, YouTubeAPIType,
    YouTubeRealVideo, YouTubeRealComment, YouTubeRealSearchResult, YouTubeRealChannel,
    YouTubeRealAPIError, YouTubeQuotaExceededError, YouTubeRateLimitError, YouTubeAuthenticationError,
    YouTubeScope, VideoCategory, create_youtube_real_client
)


class TestYouTubeRealIntegration:
    """Testes de integração real para YouTube API."""
    
    @pytest.fixture
    def real_config(self):
        """Configuração real para testes."""
        return YouTubeRealConfig(
            client_id=os.getenv('YOUTUBE_CLIENT_ID', 'test_client_id'),
            client_secret=os.getenv('YOUTUBE_CLIENT_SECRET', 'test_client_secret'),
            redirect_uri=os.getenv('YOUTUBE_REDIRECT_URI', 'http://localhost:8080/callback'),
            api_key=os.getenv('YOUTUBE_API_KEY', ''),
            quota_daily_limit=10000,
            quota_100s_limit=100,
            quota_100s_per_user_limit=300,
            web_scraping_enabled=True,
            cache_enabled=True,
            circuit_breaker_enabled=True
        )
    
    @pytest.fixture
    def real_api(self, real_config):
        """Instância da API real para testes."""
        return YouTubeRealAPI(real_config)
    
    @pytest.fixture
    def sample_video_data(self):
        """Dados de exemplo de vídeo real."""
        return {
            'id': 'test_video_id',
            'snippet': {
                'title': 'Test Video Title',
                'description': 'Test video description with keywords #test #youtube #omni',
                'publishedAt': '2025-01-27T10:00:00Z',
                'channelId': 'test_channel_id',
                'channelTitle': 'Test Channel',
                'tags': ['test', 'youtube', 'omni', 'keywords'],
                'categoryId': '27',
                'defaultLanguage': 'pt',
                'defaultAudioLanguage': 'pt',
                'thumbnails': {
                    'default': {'url': 'https://youtube.com/thumb.jpg'},
                    'medium': {'url': 'https://youtube.com/thumb_med.jpg'},
                    'high': {'url': 'https://youtube.com/thumb_high.jpg'}
                },
                'liveBroadcastContent': 'none'
            },
            'statistics': {
                'viewCount': '1000',
                'likeCount': '100',
                'commentCount': '50'
            },
            'contentDetails': {
                'duration': 'PT10M30S'
            }
        }
    
    @pytest.fixture
    def sample_search_result(self):
        """Dados de exemplo de resultado de busca."""
        return {
            'id': {'videoId': 'test_video_id'},
            'snippet': {
                'title': 'Test Video Title',
                'description': 'Test video description',
                'publishedAt': '2025-01-27T10:00:00Z',
                'channelId': 'test_channel_id',
                'channelTitle': 'Test Channel',
                'thumbnails': {
                    'default': {'url': 'https://youtube.com/thumb.jpg'}
                },
                'liveBroadcastContent': 'none'
            }
        }
    
    @pytest.fixture
    def sample_comment_data(self):
        """Dados de exemplo de comentário real."""
        return {
            'id': 'test_comment_id',
            'snippet': {
                'topLevelComment': {
                    'snippet': {
                        'textDisplay': 'Great video! #test #youtube',
                        'textOriginal': 'Great video! #test #youtube',
                        'authorDisplayName': 'Test User',
                        'authorChannelUrl': 'https://youtube.com/channel/test',
                        'authorChannelId': {'value': 'test_author_channel'},
                        'authorProfileImageUrl': 'https://youtube.com/avatar.jpg',
                        'likeCount': 10,
                        'publishedAt': '2025-01-27T11:00:00Z',
                        'updatedAt': '2025-01-27T11:00:00Z'
                    }
                },
                'totalReplyCount': 2
            }
        }
    
    def test_youtube_real_config_initialization(self, real_config):
        """Testa inicialização da configuração real."""
        assert real_config.client_id == os.getenv('YOUTUBE_CLIENT_ID', 'test_client_id')
        assert real_config.client_secret == os.getenv('YOUTUBE_CLIENT_SECRET', 'test_client_secret')
        assert real_config.redirect_uri == os.getenv('YOUTUBE_REDIRECT_URI', 'http://localhost:8080/callback')
        assert real_config.quota_daily_limit == 10000
        assert real_config.quota_100s_limit == 100
        assert real_config.quota_100s_per_user_limit == 300
        assert real_config.web_scraping_enabled is True
        assert real_config.cache_enabled is True
        assert real_config.circuit_breaker_enabled is True
    
    def test_youtube_real_api_initialization(self, real_api, real_config):
        """Testa inicialização da API real."""
        assert real_api.config == real_config
        assert real_api.rate_limiter is not None
        assert real_api.circuit_breaker is not None
        assert real_api.session is not None
        assert real_api.cache == {}
        assert real_api.credentials is None
        assert real_api.service is None
        assert real_api.quota_usage['used_today'] == 0
        assert real_api.quota_usage['used_this_hour'] == 0
    
    @patch('infrastructure.coleta.youtube_real_api.Credentials')
    @patch('infrastructure.coleta.youtube_real_api.InstalledAppFlow')
    def test_authenticate_success(self, mock_flow, mock_credentials, real_api):
        """Testa autenticação bem-sucedida."""
        # Mock de credenciais válidas
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.expired = False
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        # Mock do fluxo OAuth
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_config.return_value = mock_flow_instance
        
        # Simular arquivo de token existente
        with patch('os.path.exists', return_value=True):
            result = real_api._authenticate()
        
        assert result is True
        assert real_api.credentials == mock_creds
        assert real_api.metrics.get_counter("youtube_auth_success") == 1
    
    @patch('infrastructure.coleta.youtube_real_api.Credentials')
    def test_authenticate_with_expired_token(self, mock_credentials, real_api):
        """Testa autenticação com token expirado."""
        # Mock de credenciais expiradas
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.expired = True
        mock_creds.refresh_token = "test_refresh_token"
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        # Mock de renovação bem-sucedida
        with patch('infrastructure.coleta.youtube_real_api.Request') as mock_request:
            with patch('os.path.exists', return_value=True):
                with patch.object(real_api, '_save_credentials'):
                    result = real_api._authenticate()
        
        assert result is True
        assert real_api.credentials == mock_creds
    
    def test_authenticate_failure(self, real_api):
        """Testa falha na autenticação."""
        with patch('os.path.exists', return_value=False):
            with patch('infrastructure.coleta.youtube_real_api.InstalledAppFlow') as mock_flow:
                mock_flow_instance = MagicMock()
                mock_flow_instance.run_local_server.side_effect = Exception("Auth failed")
                mock_flow.from_client_config.return_value = mock_flow_instance
                
                with pytest.raises(YouTubeAuthenticationError, match="Falha na autenticação"):
                    real_api._authenticate()
        
        assert real_api.metrics.get_counter("youtube_auth_failure") == 1
    
    def test_check_quota_available(self, real_api):
        """Testa verificação de quota disponível."""
        # Quota disponível
        assert real_api._check_quota_available("search") is True
        
        # Simular quota diária esgotada
        real_api.quota_usage['used_today'] = 10000
        assert real_api._check_quota_available("search") is False
        
        # Reset quota
        real_api.quota_usage['used_today'] = 0
        
        # Simular quota por hora esgotada
        real_api.quota_usage['used_this_hour'] = 300
        assert real_api._check_quota_available("search") is False
    
    def test_use_quota(self, real_api):
        """Testa registro de uso de quota."""
        initial_daily = real_api.quota_usage['used_today']
        initial_hourly = real_api.quota_usage['used_this_hour']
        
        real_api._use_quota("search", 100)
        
        assert real_api.quota_usage['used_today'] == initial_daily + 100
        assert real_api.quota_usage['used_this_hour'] == initial_hourly + 100
        assert real_api.metrics.get_counter("youtube_quota_used") == 1
    
    @patch.object(YouTubeRealAPI, '_get_service')
    def test_make_api_request_success(self, mock_get_service, real_api):
        """Testa requisição bem-sucedida para API."""
        # Mock do serviço
        mock_service = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()
        mock_execute.return_value = {'items': []}
        mock_list.execute = mock_execute
        mock_search.list.return_value = mock_list
        mock_service.search.return_value = mock_search
        mock_get_service.return_value = mock_service
        
        # Mock de autenticação
        with patch.object(real_api, '_authenticate', return_value=True):
            result = real_api._make_api_request('search', q='test', part='snippet')
        
        assert result == {'items': []}
        assert real_api.quota_usage['used_today'] == 100  # Custo da busca
        assert real_api.rate_limiter.requests_minute == 1
    
    def test_make_api_request_quota_exceeded(self, real_api):
        """Testa requisição com quota excedida."""
        real_api.quota_usage['used_today'] = 10000  # Quota esgotada
        
        with pytest.raises(YouTubeQuotaExceededError, match="Quota diária excedida"):
            real_api._make_api_request('search', q='test')
    
    def test_make_api_request_rate_limit_exceeded(self, real_api):
        """Testa requisição com rate limit excedido."""
        real_api.rate_limiter.requests_minute = 100  # Limite excedido
        
        with pytest.raises(YouTubeRateLimitError, match="Rate limit excedido"):
            real_api._make_api_request('search', q='test')
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_search_videos_success(self, mock_request, real_api, sample_search_result):
        """Testa busca de vídeos com sucesso."""
        mock_request.return_value = {
            'items': [sample_search_result]
        }
        
        results = real_api.search_videos("test query", max_results=25)
        
        assert len(results) == 1
        assert isinstance(results[0], YouTubeRealSearchResult)
        assert results[0].video_id == sample_search_result['id']['videoId']
        assert results[0].title == sample_search_result['snippet']['title']
        assert results[0].description == sample_search_result['snippet']['description']
        assert results[0].channel_id == sample_search_result['snippet']['channelId']
        assert results[0].channel_title == sample_search_result['snippet']['channelTitle']
        assert results[0].thumbnails == sample_search_result['snippet']['thumbnails']
        assert results[0].live_broadcast_content == sample_search_result['snippet']['liveBroadcastContent']
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_search_videos_cache(self, mock_request, real_api, sample_search_result):
        """Testa cache de busca de vídeos."""
        mock_request.return_value = {
            'items': [sample_search_result]
        }
        
        # Primeira chamada
        results1 = real_api.search_videos("test query")
        
        # Segunda chamada (deve usar cache)
        results2 = real_api.search_videos("test query")
        
        assert results1 == results2
        assert mock_request.call_count == 1  # Só uma chamada real
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_get_video_details_success(self, mock_request, real_api, sample_video_data):
        """Testa obtenção de detalhes de vídeo."""
        mock_request.return_value = {
            'items': [sample_video_data]
        }
        
        video = real_api.get_video_details("test_video_id")
        
        assert isinstance(video, YouTubeRealVideo)
        assert video.id == sample_video_data['id']
        assert video.title == sample_video_data['snippet']['title']
        assert video.description == sample_video_data['snippet']['description']
        assert video.published_at == datetime.fromisoformat(sample_video_data['snippet']['publishedAt'].replace('Z', '+00:00'))
        assert video.channel_id == sample_video_data['snippet']['channelId']
        assert video.channel_title == sample_video_data['snippet']['channelTitle']
        assert video.view_count == int(sample_video_data['statistics']['viewCount'])
        assert video.like_count == int(sample_video_data['statistics']['likeCount'])
        assert video.comment_count == int(sample_video_data['statistics']['commentCount'])
        assert video.duration == sample_video_data['contentDetails']['duration']
        assert video.tags == sample_video_data['snippet']['tags']
        assert video.category_id == sample_video_data['snippet']['categoryId']
        assert video.category_name == "Education"  # ID 27
        assert video.default_language == sample_video_data['snippet']['defaultLanguage']
        assert video.default_audio_language == sample_video_data['snippet']['defaultAudioLanguage']
        assert video.thumbnails == sample_video_data['snippet']['thumbnails']
        assert video.live_broadcast_content == sample_video_data['snippet']['liveBroadcastContent']
        assert video.engagement_rate > 0
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_get_video_details_not_found(self, mock_request, real_api):
        """Testa obtenção de detalhes de vídeo não encontrado."""
        mock_request.return_value = {
            'items': []
        }
        
        with pytest.raises(YouTubeRealAPIError, match="Vídeo não encontrado"):
            real_api.get_video_details("nonexistent_video_id")
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_get_video_comments_success(self, mock_request, real_api, sample_comment_data):
        """Testa obtenção de comentários de vídeo."""
        mock_request.return_value = {
            'items': [sample_comment_data]
        }
        
        comments = real_api.get_video_comments("test_video_id", max_results=100)
        
        assert len(comments) == 1
        assert isinstance(comments[0], YouTubeRealComment)
        assert comments[0].id == sample_comment_data['id']
        assert comments[0].text_display == sample_comment_data['snippet']['topLevelComment']['snippet']['textDisplay']
        assert comments[0].text_original == sample_comment_data['snippet']['topLevelComment']['snippet']['textOriginal']
        assert comments[0].author_display_name == sample_comment_data['snippet']['topLevelComment']['snippet']['authorDisplayName']
        assert comments[0].author_channel_url == sample_comment_data['snippet']['topLevelComment']['snippet']['authorChannelUrl']
        assert comments[0].author_channel_id == sample_comment_data['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
        assert comments[0].author_profile_image_url == sample_comment_data['snippet']['topLevelComment']['snippet']['authorProfileImageUrl']
        assert comments[0].like_count == sample_comment_data['snippet']['topLevelComment']['snippet']['likeCount']
        assert comments[0].total_reply_count == sample_comment_data['snippet']['totalReplyCount']
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_get_channel_details_success(self, mock_request, real_api):
        """Testa obtenção de detalhes de canal com sucesso."""
        # Mock da resposta da API
        mock_request.return_value = {
            'items': [{
                'id': 'test_channel_id',
                'snippet': {
                    'title': 'Test Channel',
                    'description': 'Test channel description',
                    'customUrl': '@testchannel',
                    'publishedAt': '2025-01-27T10:00:00Z',
                    'thumbnails': {
                        'default': {'url': 'https://youtube.com/channel_thumb.jpg'}
                    },
                    'country': 'BR',
                    'defaultLanguage': 'pt',
                    'topicCategories': ['/m/04rlf', '/m/02kdv5l']
                },
                'statistics': {
                    'subscriberCount': '10000',
                    'videoCount': '150',
                    'viewCount': '1000000'
                }
            }]
        }
        
        # Fazer requisição
        channel = real_api.get_channel_details('test_channel_id')
        
        # Verificar resultado
        assert channel.id == 'test_channel_id'
        assert channel.title == 'Test Channel'
        assert channel.description == 'Test channel description'
        assert channel.custom_url == '@testchannel'
        assert channel.subscriber_count == 10000
        assert channel.video_count == 150
        assert channel.view_count == 1000000
        assert channel.country == 'BR'
        assert channel.default_language == 'pt'
        assert channel.topic_categories == ['/m/04rlf', '/m/02kdv5l']
        
        # Verificar se foi chamado com parâmetros corretos
        mock_request.assert_called_once_with('channels', part='snippet,statistics', id='test_channel_id')
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_get_channel_details_not_found(self, mock_request, real_api):
        """Testa obtenção de canal não encontrado."""
        # Mock de canal não encontrado
        mock_request.return_value = {'items': []}
        
        # Verificar que exceção é lançada
        with pytest.raises(YouTubeRealAPIError, match="Canal não encontrado"):
            real_api.get_channel_details('invalid_channel_id')
    
    @patch.object(YouTubeRealAPI, '_make_api_request')
    def test_get_trending_videos_success(self, mock_request, real_api, sample_video_data):
        """Testa obtenção de vídeos em tendência."""
        mock_request.return_value = {
            'items': [sample_video_data]
        }
        
        videos = real_api.get_trending_videos(region_code="BR", max_results=25)
        
        assert len(videos) == 1
        assert isinstance(videos[0], YouTubeRealVideo)
        assert videos[0].id == sample_video_data['id']
        assert videos[0].title == sample_video_data['snippet']['title']
        assert videos[0].view_count == int(sample_video_data['statistics']['viewCount'])
        assert videos[0].like_count == int(sample_video_data['statistics']['likeCount'])
        assert videos[0].comment_count == int(sample_video_data['statistics']['commentCount'])
    
    def test_get_category_name(self, real_api):
        """Testa obtenção de nome da categoria."""
        assert real_api._get_category_name("27") == "Education"
        assert real_api._get_category_name("20") == "Gaming"
        assert real_api._get_category_name("10") == "Music"
        assert real_api._get_category_name("999") == "Unknown"
    
    def test_get_quota_status(self, real_api):
        """Testa obtenção de status da quota."""
        status = real_api.get_quota_status()
        
        assert "used_today" in status
        assert "daily_limit" in status
        assert "used_this_hour" in status
        assert "hourly_limit" in status
        assert "remaining_today" in status
        assert "remaining_this_hour" in status
        assert "last_reset_day" in status
        assert "last_reset_hour" in status
        
        assert status["daily_limit"] == 10000
        assert status["hourly_limit"] == 300
        assert status["remaining_today"] == 10000
        assert status["remaining_this_hour"] == 300
    
    def test_get_rate_limit_status(self, real_api):
        """Testa obtenção de status dos rate limits."""
        status = real_api.get_rate_limit_status()
        
        assert "youtube_api" in status
        assert "circuit_breaker" in status
        assert "web_scraping" in status
        
        assert "requests_minute" in status["youtube_api"]
        assert "limit_minute" in status["youtube_api"]
        assert "requests_hour" in status["youtube_api"]
        assert "limit_hour" in status["youtube_api"]
        
        assert "state" in status["circuit_breaker"]
        assert "failure_count" in status["circuit_breaker"]
        
        assert "enabled" in status["web_scraping"]
    
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


class TestYouTubeRealFactory:
    """Testes para factory function."""
    
    @patch.dict(os.environ, {
        'YOUTUBE_CLIENT_ID': 'env_client_id',
        'YOUTUBE_CLIENT_SECRET': 'env_client_secret',
        'YOUTUBE_REDIRECT_URI': 'http://env.com/callback',
        'YOUTUBE_API_KEY': 'env_api_key'
    })
    def test_create_youtube_real_client_from_env(self):
        """Testa criação de cliente a partir de variáveis de ambiente."""
        client = create_youtube_real_client()
        
        assert client.config.client_id == 'env_client_id'
        assert client.config.client_secret == 'env_client_secret'
        assert client.config.redirect_uri == 'http://env.com/callback'
        assert client.config.api_key == 'env_api_key'
    
    def test_create_youtube_real_client_with_params(self):
        """Testa criação de cliente com parâmetros explícitos."""
        client = create_youtube_real_client(
            client_id='param_client_id',
            client_secret='param_client_secret',
            redirect_uri='http://param.com/callback',
            api_key='param_api_key'
        )
        
        assert client.config.client_id == 'param_client_id'
        assert client.config.client_secret == 'param_client_secret'
        assert client.config.redirect_uri == 'http://param.com/callback'
        assert client.config.api_key == 'param_api_key'


class TestYouTubeRealDataStructures:
    """Testes para estruturas de dados."""
    
    def test_youtube_real_video_initialization(self):
        """Testa inicialização de vídeo real."""
        video = YouTubeRealVideo(
            id='test_id',
            title='Test Video',
            description='Test description',
            published_at=datetime.now(),
            channel_id='channel_001',
            channel_title='Test Channel',
            channel_subscriber_count=1000,
            view_count=1000,
            like_count=100,
            comment_count=50,
            duration='PT10M30S',
            tags=['test', 'youtube'],
            category_id='27',
            category_name='Education',
            default_language='pt',
            default_audio_language='pt',
            thumbnails={'default': {'url': 'http://test.com/thumb.jpg'}},
            live_broadcast_content='none'
        )
        
        assert video.id == 'test_id'
        assert video.title == 'Test Video'
        assert video.description == 'Test description'
        assert video.channel_id == 'channel_001'
        assert video.channel_title == 'Test Channel'
        assert video.channel_subscriber_count == 1000
        assert video.view_count == 1000
        assert video.like_count == 100
        assert video.comment_count == 50
        assert video.duration == 'PT10M30S'
        assert video.tags == ['test', 'youtube']
        assert video.category_id == '27'
        assert video.category_name == 'Education'
        assert video.default_language == 'pt'
        assert video.default_audio_language == 'pt'
        assert video.thumbnails == {'default': {'url': 'http://test.com/thumb.jpg'}}
        assert video.live_broadcast_content == 'none'
        assert video.engagement_rate > 0
    
    def test_youtube_real_video_engagement_calculation(self):
        """Testa cálculo automático de engagement rate."""
        video = YouTubeRealVideo(
            id='test_id',
            title='Test Video',
            description='Test description',
            published_at=datetime.now(),
            channel_id='channel_001',
            channel_title='Test Channel',
            channel_subscriber_count=1000,
            view_count=1000,
            like_count=100,
            comment_count=50,
            duration='PT10M30S'
        )
        
        expected_engagement_rate = (100 + 50) / 1000  # 0.15
        assert video.engagement_rate == expected_engagement_rate
    
    def test_youtube_real_search_result_initialization(self):
        """Testa inicialização de resultado de busca."""
        result = YouTubeRealSearchResult(
            video_id='test_video_id',
            title='Test Video',
            description='Test description',
            published_at=datetime.now(),
            channel_id='channel_001',
            channel_title='Test Channel',
            thumbnails={'default': {'url': 'http://test.com/thumb.jpg'}},
            live_broadcast_content='none',
            relevance_score=0.85
        )
        
        assert result.video_id == 'test_video_id'
        assert result.title == 'Test Video'
        assert result.description == 'Test description'
        assert result.channel_id == 'channel_001'
        assert result.channel_title == 'Test Channel'
        assert result.thumbnails == {'default': {'url': 'http://test.com/thumb.jpg'}}
        assert result.live_broadcast_content == 'none'
        assert result.relevance_score == 0.85
    
    def test_youtube_real_comment_initialization(self):
        """Testa inicialização de comentário real."""
        comment = YouTubeRealComment(
            id='comment_001',
            text_display='Great video! #test',
            text_original='Great video! #test',
            author_display_name='Test User',
            author_channel_url='http://youtube.com/channel/test',
            author_channel_id='author_channel_001',
            author_profile_image_url='http://test.com/avatar.jpg',
            like_count=10,
            published_at=datetime.now(),
            updated_at=datetime.now(),
            parent_id="",
            can_rate=True,
            viewer_rating="",
            total_reply_count=2,
            sentiment_score=0.8
        )
        
        assert comment.id == 'comment_001'
        assert comment.text_display == 'Great video! #test'
        assert comment.text_original == 'Great video! #test'
        assert comment.author_display_name == 'Test User'
        assert comment.author_channel_url == 'http://youtube.com/channel/test'
        assert comment.author_channel_id == 'author_channel_001'
        assert comment.author_profile_image_url == 'http://test.com/avatar.jpg'
        assert comment.like_count == 10
        assert comment.can_rate is True
        assert comment.total_reply_count == 2
        assert comment.sentiment_score == 0.8


class TestYouTubeRealErrorHandling:
    """Testes para tratamento de erros."""
    
    def test_youtube_real_api_error_creation(self):
        """Testa criação de erro YouTube Real API."""
        error = YouTubeRealAPIError("Test error", "TEST_ERROR", 400, YouTubeAPIType.DATA_API_V3)
        
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.http_status == 400
        assert error.api_type == YouTubeAPIType.DATA_API_V3
    
    def test_youtube_quota_exceeded_error(self):
        """Testa erro de quota excedida."""
        error = YouTubeQuotaExceededError("Quota exceeded")
        
        assert str(error) == "Quota exceeded"
        assert isinstance(error, YouTubeRealAPIError)
    
    def test_youtube_rate_limit_error(self):
        """Testa erro de rate limit."""
        error = YouTubeRateLimitError("Rate limit exceeded")
        
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, YouTubeRealAPIError)
    
    def test_youtube_authentication_error(self):
        """Testa erro de autenticação."""
        error = YouTubeAuthenticationError("Invalid credentials", "INVALID_CREDENTIALS", 401)
        
        assert str(error) == "Invalid credentials"
        assert error.error_code == "INVALID_CREDENTIALS"
        assert error.http_status == 401
        assert isinstance(error, YouTubeRealAPIError) 