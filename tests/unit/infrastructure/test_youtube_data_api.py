#!/usr/bin/env python3
"""
Testes Unitários - YouTube Data API
==================================

Tracing ID: TEST_YOUTUBE_DATA_API_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/youtube_data_api.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 3.5
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import os

from infrastructure.coleta.youtube_data_api import (
    YouTubeDataAPI, YouTubeAuthConfig, YouTubeRateLimit,
    YouTubeVideo, YouTubeComment, YouTubeSearchResult,
    YouTubeDataAPIError, create_youtube_data_client
)


class TestYouTubeDataAPI:
    @pytest.fixture
    def auth_config(self):
        return YouTubeAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8080/callback"
        )

    @pytest.fixture
    def rate_limit(self):
        return YouTubeRateLimit(
            requests_per_day=1000,
            requests_per_100_seconds=10
        )

    @pytest.fixture
    def api_client(self, auth_config, rate_limit):
        return YouTubeDataAPI(auth_config, rate_limit)

    def test_youtube_auth_config_initialization(self):
        """Testa inicialização da configuração de autenticação."""
        config = YouTubeAuthConfig(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="http://test.com"
        )
        assert config.client_id == "test_id"
        assert config.client_secret == "test_secret"
        assert config.redirect_uri == "http://test.com"
        assert config.scopes is not None
        assert config.token_file == "youtube_token.json"

    def test_youtube_rate_limit_initialization(self):
        """Testa inicialização da configuração de rate limiting."""
        rate_limit = YouTubeRateLimit()
        assert rate_limit.requests_per_day == 10000
        assert rate_limit.requests_per_100_seconds == 100
        assert rate_limit.requests_per_100_seconds_per_user == 300

    def test_youtube_video_dataclass(self):
        """Testa criação de objeto YouTubeVideo."""
        video = YouTubeVideo(
            id="test_id",
            title="Test Video",
            description="Test Description",
            published_at="2023-01-01T00:00:00Z",
            channel_id="channel_id",
            channel_title="Channel Name",
            view_count=1000,
            like_count=100,
            comment_count=50,
            duration="PT10M30S"
        )
        assert video.id == "test_id"
        assert video.title == "Test Video"
        assert video.view_count == 1000
        assert video.tags == []

    def test_youtube_comment_dataclass(self):
        """Testa criação de objeto YouTubeComment."""
        comment = YouTubeComment(
            id="comment_id",
            text_display="Great video!",
            author_display_name="User",
            author_channel_url="http://youtube.com/user",
            author_channel_id="user_id",
            like_count=5,
            published_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z"
        )
        assert comment.id == "comment_id"
        assert comment.text_display == "Great video!"
        assert comment.author_display_name == "User"
        assert comment.total_reply_count == 0

    def test_youtube_search_result_dataclass(self):
        """Testa criação de objeto YouTubeSearchResult."""
        result = YouTubeSearchResult(
            video_id="video_id",
            title="Search Result",
            description="Description",
            published_at="2023-01-01T00:00:00Z",
            channel_id="channel_id",
            channel_title="Channel",
            thumbnails={"default": {"url": "http://test.com"}}
        )
        assert result.video_id == "video_id"
        assert result.title == "Search Result"
        assert "default" in result.thumbnails

    def test_youtube_data_api_initialization(self, auth_config, rate_limit):
        """Testa inicialização do cliente YouTube Data API."""
        client = YouTubeDataAPI(auth_config, rate_limit)
        assert client.config == auth_config
        assert client.rate_limit == rate_limit
        assert client.service is None
        assert client.credentials is None
        assert client.request_count_day == 0
        assert client.request_count_100s == 0

    def test_youtube_data_api_error(self):
        """Testa criação de exceção customizada."""
        error = YouTubeDataAPIError("Test error", "QUOTA_EXCEEDED", 403)
        assert str(error) == "Test error"
        assert error.error_code == "QUOTA_EXCEEDED"
        assert error.http_status == 403

    @patch('os.path.exists')
    @patch('google.oauth2.credentials.Credentials')
    def test_authenticate_with_existing_credentials(self, mock_credentials, mock_exists, api_client):
        """Testa autenticação com credenciais existentes."""
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        result = api_client._authenticate()
        assert result is True
        assert api_client.credentials == mock_creds

    @patch('os.path.exists')
    @patch('google.oauth2.credentials.Credentials')
    @patch('google_auth_oauthlib.flow.InstalledAppFlow')
    def test_authenticate_new_flow(self, mock_flow, mock_credentials, mock_exists, api_client):
        """Testa autenticação com novo fluxo OAuth."""
        mock_exists.return_value = False
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = Mock()
        mock_flow.from_client_config.return_value = mock_flow_instance
        
        result = api_client._authenticate()
        assert result is True
        mock_flow_instance.run_local_server.assert_called_once()

    def test_check_rate_limit_within_limits(self, api_client):
        """Testa verificação de rate limit dentro dos limites."""
        api_client.request_count_day = 500
        api_client.request_count_100s = 5
        
        result = api_client._check_rate_limit()
        assert result is True

    def test_check_rate_limit_exceeded_daily(self, api_client):
        """Testa verificação de rate limit excedido diariamente."""
        api_client.request_count_day = 1001  # Excede limite de 1000
        api_client.request_count_100s = 5
        
        result = api_client._check_rate_limit()
        assert result is False

    def test_check_rate_limit_exceeded_100s(self, api_client):
        """Testa verificação de rate limit excedido em 100s."""
        api_client.request_count_day = 500
        api_client.request_count_100s = 11  # Excede limite de 10
        
        result = api_client._check_rate_limit()
        assert result is False

    def test_increment_request_count(self, api_client):
        """Testa incremento dos contadores de requisição."""
        initial_day = api_client.request_count_day
        initial_100s = api_client.request_count_100s
        
        api_client._increment_request_count()
        
        assert api_client.request_count_day == initial_day + 1
        assert api_client.request_count_100s == initial_100s + 1

    @patch.object(YouTubeDataAPI, '_authenticate')
    @patch('googleapiclient.discovery.build')
    def test_get_service(self, mock_build, mock_authenticate, api_client):
        """Testa obtenção do serviço YouTube."""
        mock_authenticate.return_value = True
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        service = api_client._get_service()
        
        assert service == mock_service
        assert api_client.service == mock_service
        mock_build.assert_called_once_with('youtube', 'v3', credentials=api_client.credentials)

    @patch.object(YouTubeDataAPI, '_check_rate_limit')
    @patch.object(YouTubeDataAPI, '_get_service')
    def test_search_videos_success(self, mock_get_service, mock_check_rate_limit, api_client):
        """Testa busca de vídeos com sucesso."""
        mock_check_rate_limit.return_value = True
        mock_service = Mock()
        mock_search = Mock()
        mock_list = Mock()
        mock_execute = Mock()
        
        mock_execute.return_value = {
            'items': [{
                'id': {'videoId': 'test_video_id'},
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test Description',
                    'publishedAt': '2023-01-01T00:00:00Z',
                    'channelId': 'channel_id',
                    'channelTitle': 'Channel Name',
                    'thumbnails': {'default': {'url': 'http://test.com'}},
                    'liveBroadcastContent': 'none'
                }
            }]
        }
        
        mock_list.execute = mock_execute
        mock_search.list.return_value = mock_list
        mock_service.search.return_value = mock_search
        mock_get_service.return_value = mock_service
        
        results = api_client.search_videos("test query")
        
        assert len(results) == 1
        assert isinstance(results[0], YouTubeSearchResult)
        assert results[0].video_id == "test_video_id"
        assert results[0].title == "Test Video"

    @patch.object(YouTubeDataAPI, '_check_rate_limit')
    def test_search_videos_rate_limit_exceeded(self, mock_check_rate_limit, api_client):
        """Testa busca de vídeos com rate limit excedido."""
        mock_check_rate_limit.return_value = False
        
        with pytest.raises(YouTubeDataAPIError, match="Rate limit excedido"):
            api_client.search_videos("test query")

    @patch.object(YouTubeDataAPI, '_check_rate_limit')
    @patch.object(YouTubeDataAPI, '_get_service')
    def test_get_video_details_success(self, mock_get_service, mock_check_rate_limit, api_client):
        """Testa obtenção de detalhes de vídeo com sucesso."""
        mock_check_rate_limit.return_value = True
        mock_service = Mock()
        mock_videos = Mock()
        mock_list = Mock()
        mock_execute = Mock()
        
        mock_execute.return_value = {
            'items': [{
                'id': 'test_video_id',
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test Description',
                    'publishedAt': '2023-01-01T00:00:00Z',
                    'channelId': 'channel_id',
                    'channelTitle': 'Channel Name',
                    'tags': ['tag1', 'tag2'],
                    'categoryId': '22',
                    'defaultLanguage': 'pt',
                    'defaultAudioLanguage': 'pt'
                },
                'statistics': {
                    'viewCount': '1000',
                    'likeCount': '100',
                    'commentCount': '50'
                },
                'contentDetails': {
                    'duration': 'PT10M30S'
                }
            }]
        }
        
        mock_list.execute = mock_execute
        mock_videos.list.return_value = mock_list
        mock_service.videos.return_value = mock_videos
        mock_get_service.return_value = mock_service
        
        video = api_client.get_video_details("test_video_id")
        
        assert isinstance(video, YouTubeVideo)
        assert video.id == "test_video_id"
        assert video.title == "Test Video"
        assert video.view_count == 1000
        assert video.like_count == 100
        assert video.comment_count == 50
        assert video.tags == ['tag1', 'tag2']

    @patch.object(YouTubeDataAPI, '_check_rate_limit')
    @patch.object(YouTubeDataAPI, '_get_service')
    def test_get_video_comments_success(self, mock_get_service, mock_check_rate_limit, api_client):
        """Testa obtenção de comentários de vídeo com sucesso."""
        mock_check_rate_limit.return_value = True
        mock_service = Mock()
        mock_comment_threads = Mock()
        mock_list = Mock()
        mock_execute = Mock()
        
        mock_execute.return_value = {
            'items': [{
                'snippet': {
                    'topLevelComment': {
                        'id': 'comment_id',
                        'snippet': {
                            'textDisplay': 'Great video!',
                            'authorDisplayName': 'User',
                            'authorChannelUrl': 'http://youtube.com/user',
                            'authorChannelId': {'value': 'user_id'},
                            'likeCount': 5,
                            'publishedAt': '2023-01-01T00:00:00Z',
                            'updatedAt': '2023-01-01T00:00:00Z',
                            'canRate': True,
                            'viewerRating': 'none'
                        }
                    },
                    'totalReplyCount': 2
                }
            }]
        }
        
        mock_list.execute = mock_execute
        mock_comment_threads.list.return_value = mock_list
        mock_service.commentThreads.return_value = mock_comment_threads
        mock_get_service.return_value = mock_service
        
        comments = api_client.get_video_comments("test_video_id")
        
        assert len(comments) == 1
        assert isinstance(comments[0], YouTubeComment)
        assert comments[0].id == "comment_id"
        assert comments[0].text_display == "Great video!"
        assert comments[0].total_reply_count == 2

    @patch.object(YouTubeDataAPI, '_check_rate_limit')
    @patch.object(YouTubeDataAPI, '_get_service')
    def test_get_trending_videos_success(self, mock_get_service, mock_check_rate_limit, api_client):
        """Testa obtenção de vídeos em tendência com sucesso."""
        mock_check_rate_limit.return_value = True
        mock_service = Mock()
        mock_videos = Mock()
        mock_list = Mock()
        mock_execute = Mock()
        
        mock_execute.return_value = {
            'items': [{
                'id': 'trending_video_id',
                'snippet': {
                    'title': 'Trending Video',
                    'description': 'Trending Description',
                    'publishedAt': '2023-01-01T00:00:00Z',
                    'channelId': 'channel_id',
                    'channelTitle': 'Channel Name',
                    'tags': ['trending'],
                    'categoryId': '22'
                },
                'statistics': {
                    'viewCount': '10000',
                    'likeCount': '1000',
                    'commentCount': '500'
                },
                'contentDetails': {
                    'duration': 'PT15M45S'
                }
            }]
        }
        
        mock_list.execute = mock_execute
        mock_videos.list.return_value = mock_list
        mock_service.videos.return_value = mock_videos
        mock_get_service.return_value = mock_service
        
        videos = api_client.get_trending_videos("BR")
        
        assert len(videos) == 1
        assert isinstance(videos[0], YouTubeVideo)
        assert videos[0].id == "trending_video_id"
        assert videos[0].title == "Trending Video"
        assert videos[0].view_count == 10000

    def test_get_rate_limit_status(self, api_client):
        """Testa obtenção do status do rate limiting."""
        api_client.request_count_day = 500
        api_client.request_count_100s = 5
        api_client.last_request_day = datetime.now()
        api_client.last_request_100s = datetime.now()
        
        status = api_client.get_rate_limit_status()
        
        assert status['requests_today'] == 500
        assert status['requests_last_100s'] == 5
        assert status['daily_limit'] == 1000
        assert status['limit_100s'] == 10
        assert status['daily_remaining'] == 500
        assert 'last_request_day' in status
        assert 'last_request_100s' in status

    @patch.dict(os.environ, {
        'YOUTUBE_CLIENT_ID': 'env_client_id',
        'YOUTUBE_CLIENT_SECRET': 'env_client_secret',
        'YOUTUBE_REDIRECT_URI': 'http://env.com/callback'
    })
    def test_create_youtube_data_client_with_env_vars(self):
        """Testa criação de cliente com variáveis de ambiente."""
        client = create_youtube_data_client()
        assert client.config.client_id == 'env_client_id'
        assert client.config.client_secret == 'env_client_secret'
        assert client.config.redirect_uri == 'http://env.com/callback'

    def test_create_youtube_data_client_with_params(self):
        """Testa criação de cliente com parâmetros."""
        client = create_youtube_data_client(
            client_id="param_client_id",
            client_secret="param_client_secret",
            redirect_uri="http://param.com/callback"
        )
        assert client.config.client_id == 'param_client_id'
        assert client.config.client_secret == 'param_client_secret'
        assert client.config.redirect_uri == 'http://param.com/callback'

    def test_create_youtube_data_client_missing_credentials(self):
        """Testa criação de cliente sem credenciais."""
        with pytest.raises(ValueError, match="YouTube credentials não configuradas"):
            create_youtube_data_client()

    @patch.object(YouTubeDataAPI, '_check_rate_limit')
    @patch.object(YouTubeDataAPI, '_get_service')
    def test_search_videos_with_filters(self, mock_get_service, mock_check_rate_limit, api_client):
        """Testa busca de vídeos com filtros."""
        mock_check_rate_limit.return_value = True
        mock_service = Mock()
        mock_search = Mock()
        mock_list = Mock()
        mock_execute = Mock()
        
        mock_execute.return_value = {'items': []}
        mock_list.execute = mock_execute
        mock_search.list.return_value = mock_list
        mock_service.search.return_value = mock_search
        mock_get_service.return_value = mock_service
        
        api_client.search_videos(
            query="test",
            max_results=10,
            order="date",
            published_after="2023-01-01T00:00:00Z",
            published_before="2023-12-31T23:59:59Z",
            region_code="BR",
            relevance_language="pt"
        )
        
        # Verifica se os parâmetros foram passados corretamente
        mock_search.list.assert_called_once()
        call_args = mock_search.list.call_args[1]
        assert call_args['q'] == "test"
        assert call_args['maxResults'] == 10
        assert call_args['order'] == "date"
        assert call_args['publishedAfter'] == "2023-01-01T00:00:00Z"
        assert call_args['publishedBefore'] == "2023-12-31T23:59:59Z"
        assert call_args['regionCode'] == "BR"
        assert call_args['relevanceLanguage'] == "pt"

    def test_edge_cases(self, api_client):
        """Testa casos edge."""
        # Rate limit reset após 1 dia
        api_client.last_request_day = datetime.now() - timedelta(days=2)
        api_client.request_count_day = 1000
        api_client._check_rate_limit()
        assert api_client.request_count_day == 0
        
        # Rate limit reset após 100s
        api_client.last_request_100s = datetime.now() - timedelta(seconds=150)
        api_client.request_count_100s = 10
        api_client._check_rate_limit()
        assert api_client.request_count_100s == 0


if __name__ == "__main__":
    pytest.main([__file__]) 