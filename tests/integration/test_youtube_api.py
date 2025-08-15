"""
YouTube Data API v3 Integration Tests

📐 CoCoT: Baseado em estratégias de teste para YouTube API
🌲 ToT: Avaliado cenários de teste e escolhido cobertura ideal
♻️ ReAct: Simulado falhas de API e validado recuperação

Prompt: CHECKLIST_INTEGRACAO_EXTERNA.md - 2.2.5
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: youtube-api-tests-2025-01-27-001

Funcionalidades testadas:
- Testes de integração
- Teste de quota management
- Validação de análise de tendências
- Testes de recuperação de falhas
- Logs estruturados
"""

import os
import sys
import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.coleta.youtube_data_api import (
    YouTubeDataAPI, 
    YouTubeAuthConfig, 
    YouTubeRateLimit,
    YouTubeVideo,
    YouTubeComment,
    YouTubeSearchResult,
    create_youtube_data_client
)
from infrastructure.coleta.youtube_trends_analyzer import (
    YouTubeTrendsAnalyzer,
    VideoTrend,
    TrendMetrics,
    TrendPattern,
    create_youtube_trends_analyzer
)
from infrastructure.coleta.youtube_quota_manager import (
    YouTubeQuotaManager,
    QuotaConfig,
    CacheConfig,
    QuotaStatus,
    CacheStrategy,
    create_youtube_quota_manager
)


class TestYouTubeDataAPI:
    """Testes para YouTube Data API v3."""
    
    @pytest.fixture
    def mock_auth_config(self):
        """Configuração de autenticação mock."""
        return YouTubeAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:5000/callback"
        )
    
    @pytest.fixture
    def mock_rate_limit(self):
        """Configuração de rate limit mock."""
        return YouTubeRateLimit(
            requests_per_day=1000,
            requests_per_100_seconds=100,
            requests_per_100_seconds_per_user=300
        )
    
    @pytest.fixture
    def youtube_api(self, mock_auth_config, mock_rate_limit):
        """Instância da API YouTube mock."""
        with patch('infrastructure.coleta.youtube_data_api.build') as mock_build:
            with patch('infrastructure.coleta.youtube_data_api.Credentials') as mock_credentials:
                # Mock das credenciais
                mock_creds = Mock()
                mock_creds.valid = True
                mock_creds.expired = False
                mock_credentials.from_authorized_user_file.return_value = mock_creds
                
                # Mock do serviço
                mock_service = Mock()
                mock_build.return_value = mock_service
                
                api = YouTubeDataAPI(mock_auth_config, mock_rate_limit)
                api.service = mock_service
                api.credentials = mock_creds
                
                yield api
    
    def test_youtube_api_initialization(self, mock_auth_config, mock_rate_limit):
        """Testa inicialização da API YouTube."""
        # 📐 CoCoT: Baseado em padrões de inicialização da YouTube API
        # 🌲 ToT: Avaliado diferentes configurações e escolhido mais robusta
        # ♻️ ReAct: Simulado cenário de inicialização e validado configuração
        
        with patch('infrastructure.coleta.youtube_data_api.build'):
            with patch('infrastructure.coleta.youtube_data_api.Credentials'):
                api = YouTubeDataAPI(mock_auth_config, mock_rate_limit)
                
                assert api.config == mock_auth_config
                assert api.rate_limit == mock_rate_limit
                assert api.quota_usage.used_today == 0
                assert api.quota_usage.used_this_hour == 0
    
    def test_search_videos_success(self, youtube_api):
        """Testa busca de vídeos com sucesso."""
        # Mock da resposta da API
        mock_response = {
            'items': [
                {
                    'id': {'videoId': 'test_video_id_1'},
                    'snippet': {
                        'title': 'Test Video 1',
                        'description': 'Test description 1',
                        'publishedAt': '2025-01-27T10:00:00Z',
                        'channelId': 'test_channel_1',
                        'channelTitle': 'Test Channel 1',
                        'thumbnails': {'default': {'url': 'http://test.com/thumb1.jpg'}}
                    }
                },
                {
                    'id': {'videoId': 'test_video_id_2'},
                    'snippet': {
                        'title': 'Test Video 2',
                        'description': 'Test description 2',
                        'publishedAt': '2025-01-27T11:00:00Z',
                        'channelId': 'test_channel_2',
                        'channelTitle': 'Test Channel 2',
                        'thumbnails': {'default': {'url': 'http://test.com/thumb2.jpg'}}
                    }
                }
            ]
        }
        
        youtube_api.service.search.return_value.list.return_value.execute.return_value = mock_response
        
        # Executar busca
        results = youtube_api.search_videos("python tutorial", max_results=2)
        
        # Validações
        assert len(results) == 2
        assert isinstance(results[0], YouTubeSearchResult)
        assert results[0].video_id == 'test_video_id_1'
        assert results[0].title == 'Test Video 1'
        assert results[1].video_id == 'test_video_id_2'
        assert results[1].title == 'Test Video 2'
        
        # Verificar se a API foi chamada corretamente
        youtube_api.service.search.return_value.list.assert_called_once()
        call_args = youtube_api.service.search.return_value.list.call_args[1]
        assert call_args['q'] == 'python tutorial'
        assert call_args['maxResults'] == 2
        assert call_args['type'] == 'video'
    
    def test_get_video_details_success(self, youtube_api):
        """Testa obtenção de detalhes de vídeo com sucesso."""
        # Mock da resposta da API
        mock_response = {
            'items': [
                {
                    'id': 'test_video_id',
                    'snippet': {
                        'title': 'Test Video Title',
                        'description': 'Test video description',
                        'publishedAt': '2025-01-27T10:00:00Z',
                        'channelId': 'test_channel_id',
                        'channelTitle': 'Test Channel',
                        'tags': ['python', 'tutorial', 'programming'],
                        'categoryId': '27',
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
                }
            ]
        }
        
        youtube_api.service.videos.return_value.list.return_value.execute.return_value = mock_response
        
        # Executar obtenção de detalhes
        video = youtube_api.get_video_details('test_video_id')
        
        # Validações
        assert isinstance(video, YouTubeVideo)
        assert video.id == 'test_video_id'
        assert video.title == 'Test Video Title'
        assert video.view_count == 1000
        assert video.like_count == 100
        assert video.comment_count == 50
        assert video.duration == 'PT10M30S'
        assert video.tags == ['python', 'tutorial', 'programming']
        assert video.category_id == '27'
        assert video.default_language == 'pt'
    
    def test_get_video_comments_success(self, youtube_api):
        """Testa obtenção de comentários com sucesso."""
        # Mock da resposta da API
        mock_response = {
            'items': [
                {
                    'snippet': {
                        'topLevelComment': {
                            'id': 'comment_id_1',
                            'snippet': {
                                'textDisplay': 'Great video!',
                                'authorDisplayName': 'User1',
                                'authorChannelUrl': 'http://youtube.com/user1',
                                'authorChannelId': {'value': 'channel_id_1'},
                                'likeCount': 10,
                                'publishedAt': '2025-01-27T10:30:00Z',
                                'updatedAt': '2025-01-27T10:30:00Z',
                                'canRate': True,
                                'viewerRating': 'none'
                            }
                        },
                        'totalReplyCount': 2
                    }
                },
                {
                    'snippet': {
                        'topLevelComment': {
                            'id': 'comment_id_2',
                            'snippet': {
                                'textDisplay': 'Very helpful tutorial',
                                'authorDisplayName': 'User2',
                                'authorChannelUrl': 'http://youtube.com/user2',
                                'authorChannelId': {'value': 'channel_id_2'},
                                'likeCount': 5,
                                'publishedAt': '2025-01-27T11:00:00Z',
                                'updatedAt': '2025-01-27T11:00:00Z',
                                'canRate': True,
                                'viewerRating': 'like'
                            }
                        },
                        'totalReplyCount': 0
                    }
                }
            ]
        }
        
        youtube_api.service.commentThreads.return_value.list.return_value.execute.return_value = mock_response
        
        # Executar obtenção de comentários
        comments = youtube_api.get_video_comments('test_video_id', max_results=2)
        
        # Validações
        assert len(comments) == 2
        assert isinstance(comments[0], YouTubeComment)
        assert comments[0].id == 'comment_id_1'
        assert comments[0].text_display == 'Great video!'
        assert comments[0].author_display_name == 'User1'
        assert comments[0].like_count == 10
        assert comments[0].total_reply_count == 2
        
        assert comments[1].id == 'comment_id_2'
        assert comments[1].text_display == 'Very helpful tutorial'
        assert comments[1].author_display_name == 'User2'
        assert comments[1].like_count == 5
        assert comments[1].total_reply_count == 0
    
    def test_quota_exceeded_error(self, youtube_api):
        """Testa erro quando quota é excedida."""
        from infrastructure.coleta.youtube_data_api import YouTubeDataAPIError
        
        # Mock de erro de quota excedida
        mock_error = Mock()
        mock_error.resp.status = 403
        mock_error.content = json.dumps({
            'error': {
                'code': 403,
                'message': 'Quota exceeded for quota group \'default\' and limit \'youtube.googleapis.com/read_quota\' of 10000 per day.'
            }
        }).encode()
        
        youtube_api.service.search.return_value.list.return_value.execute.side_effect = mock_error
        
        # Executar busca e verificar erro
        with pytest.raises(YouTubeDataAPIError) as exc_info:
            youtube_api.search_videos("python tutorial")
        
        assert "Quota exceeded" in str(exc_info.value)
        assert exc_info.value.http_status == 403
    
    def test_rate_limit_check(self, youtube_api):
        """Testa verificação de rate limit."""
        # Configurar uso de quota
        youtube_api.quota_usage.used_today = 9999  # Próximo do limite
        
        # Verificar se ainda há quota disponível
        assert youtube_api.check_quota_available("search") == True
        
        # Usar toda a quota
        youtube_api.quota_usage.used_today = 10000
        
        # Verificar se não há mais quota
        assert youtube_api.check_quota_available("search") == False


class TestYouTubeTrendsAnalyzer:
    """Testes para analisador de tendências do YouTube."""
    
    @pytest.fixture
    def trends_analyzer(self):
        """Instância do analisador de tendências."""
        config = {
            'min_trend_score': 0.7,
            'min_growth_rate': 0.1,
            'trend_window_hours': 24,
            'min_views_threshold': 1000,
            'min_engagement_threshold': 0.05
        }
        return YouTubeTrendsAnalyzer(config)
    
    def test_analyze_video_trend_success(self, trends_analyzer):
        """Testa análise de tendência de vídeo com sucesso."""
        # Dados de vídeo de teste
        video_data = {
            'id': 'test_video_id',
            'title': 'Python Tutorial for Beginners',
            'description': 'Learn Python programming from scratch',
            'published_at': '2025-01-27T10:00:00Z',
            'channel_id': 'test_channel_id',
            'channel_title': 'Programming Channel',
            'view_count': 5000,
            'like_count': 500,
            'comment_count': 100,
            'duration': 'PT15M30S',
            'tags': ['python', 'tutorial', 'programming'],
            'category_id': '27'
        }
        
        # Dados históricos simulados
        historical_data = [
            {'timestamp': '2025-01-27T09:00:00Z', 'view_count': 3000},
            {'timestamp': '2025-01-27T09:30:00Z', 'view_count': 3500},
            {'timestamp': '2025-01-27T10:00:00Z', 'view_count': 5000}
        ]
        
        # Executar análise
        video_trend = trends_analyzer.analyze_video_trend(video_data, historical_data)
        
        # Validações
        assert isinstance(video_trend, VideoTrend)
        assert video_trend.video_id == 'test_video_id'
        assert video_trend.title == 'Python Tutorial for Beginners'
        assert video_trend.channel_id == 'test_channel_id'
        assert video_trend.category == 'education'
        assert video_trend.language == 'en'
        assert video_trend.duration_seconds == 930  # 15:30 = 930 segundos
        
        # Validar métricas de tendência
        assert isinstance(video_trend.trend_metrics, TrendMetrics)
        assert video_trend.trend_metrics.engagement_rate > 0
        assert video_trend.trend_metrics.viral_potential >= 0
        assert video_trend.trend_metrics.viral_potential <= 1
        
        # Validar padrão de tendência
        assert isinstance(video_trend.pattern, TrendPattern)
        assert video_trend.pattern.pattern_type in ['exponential_growth', 'linear_growth', 'slow_growth', 'stable', 'declining']
        
        # Validar keywords extraídas
        assert len(video_trend.keywords) > 0
        assert 'python' in [kw.lower() for kw in video_trend.keywords]
    
    def test_detect_viral_potential(self, trends_analyzer):
        """Testa detecção de potencial viral."""
        # Vídeo com alto potencial viral
        viral_video_data = {
            'view_count': 50000,
            'like_count': 5000,
            'comment_count': 1000,
            'published_at': '2025-01-27T10:00:00Z'
        }
        
        viral_score = trends_analyzer.detect_viral_potential(viral_video_data)
        assert viral_score > 0.5  # Alto potencial viral
        
        # Vídeo com baixo potencial viral
        low_viral_video_data = {
            'view_count': 100,
            'like_count': 5,
            'comment_count': 1,
            'published_at': '2025-01-27T10:00:00Z'
        }
        
        low_viral_score = trends_analyzer.detect_viral_potential(low_viral_video_data)
        assert low_viral_score < 0.3  # Baixo potencial viral
    
    def test_analyze_category_trends(self, trends_analyzer):
        """Testa análise de tendências por categoria."""
        # Dados de vídeos de teste
        videos_data = [
            {
                'id': 'video_1',
                'category_id': '27',  # Education
                'view_count': 1000,
                'like_count': 100,
                'comment_count': 20
            },
            {
                'id': 'video_2',
                'category_id': '27',  # Education
                'view_count': 2000,
                'like_count': 200,
                'comment_count': 40
            },
            {
                'id': 'video_3',
                'category_id': '20',  # Gaming
                'view_count': 5000,
                'like_count': 500,
                'comment_count': 100
            }
        ]
        
        # Executar análise
        category_trends = trends_analyzer.analyze_category_trends(videos_data)
        
        # Validações
        assert len(category_trends) == 2  # Education e Gaming
        
        # Encontrar categoria Education
        education_trend = next((ct for ct in category_trends if ct.category_id == '27'), None)
        assert education_trend is not None
        assert education_trend.category_name == 'Education'
        assert education_trend.total_videos == 2
        assert education_trend.avg_engagement > 0
        
        # Encontrar categoria Gaming
        gaming_trend = next((ct for ct in category_trends if ct.category_id == '20'), None)
        assert gaming_trend is not None
        assert gaming_trend.category_name == 'Gaming'
        assert gaming_trend.total_videos == 1
        assert gaming_trend.avg_engagement > 0


class TestYouTubeQuotaManager:
    """Testes para gerenciador de quota do YouTube."""
    
    @pytest.fixture
    def quota_config(self):
        """Configuração de quota de teste."""
        return QuotaConfig(
            daily_limit=1000,
            warning_threshold=0.8,
            critical_threshold=0.95,
            cost_per_request={
                'search': 100,
                'videos': 1,
                'comments': 1
            }
        )
    
    @pytest.fixture
    def cache_config(self):
        """Configuração de cache de teste."""
        return CacheConfig(
            strategy=CacheStrategy.INTELLIGENT,
            default_ttl=3600,
            redis_url="redis://localhost:6379"
        )
    
    @pytest.fixture
    def quota_manager(self, quota_config, cache_config):
        """Instância do gerenciador de quota."""
        with patch('infrastructure.coleta.youtube_quota_manager.redis.from_url'):
            return YouTubeQuotaManager(quota_config, cache_config)
    
    def test_quota_manager_initialization(self, quota_config, cache_config):
        """Testa inicialização do gerenciador de quota."""
        with patch('infrastructure.coleta.youtube_quota_manager.redis.from_url'):
            manager = YouTubeQuotaManager(quota_config, cache_config)
            
            assert manager.quota_config == quota_config
            assert manager.cache_config == cache_config
            assert manager.quota_usage.used_today == 0
            assert len(manager.alert_callbacks) == 0
    
    def test_check_quota_available(self, quota_manager):
        """Testa verificação de quota disponível."""
        # Quota inicial disponível
        assert quota_manager.check_quota_available("search") == True
        assert quota_manager.check_quota_available("videos") == True
        
        # Usar quota
        quota_manager.quota_usage.used_today = 900  # 90% usado
        
        # Ainda deve estar disponível
        assert quota_manager.check_quota_available("videos") == True
        
        # Usar toda a quota
        quota_manager.quota_usage.used_today = 1000
        
        # Não deve estar mais disponível
        assert quota_manager.check_quota_available("search") == False
        assert quota_manager.check_quota_available("videos") == False
    
    def test_reserve_quota(self, quota_manager):
        """Testa reserva de quota."""
        # Reservar quota para busca
        assert quota_manager.reserve_quota("search") == True
        assert quota_manager.quota_usage.used_today == 100
        
        # Reservar quota para vídeo
        assert quota_manager.reserve_quota("videos") == True
        assert quota_manager.quota_usage.used_today == 101
        
        # Tentar reservar mais do que disponível
        quota_manager.quota_usage.used_today = 1000
        assert quota_manager.reserve_quota("search") == False
    
    def test_get_quota_status(self, quota_manager):
        """Testa obtenção de status da quota."""
        # Status inicial
        status = quota_manager.get_quota_status()
        assert status == QuotaStatus.AVAILABLE
        
        # Status de warning
        quota_manager.quota_usage.used_today = 800  # 80%
        status = quota_manager.get_quota_status()
        assert status == QuotaStatus.WARNING
        
        # Status crítico
        quota_manager.quota_usage.used_today = 950  # 95%
        status = quota_manager.get_quota_status()
        assert status == QuotaStatus.CRITICAL
        
        # Status esgotado
        quota_manager.quota_usage.used_today = 1000  # 100%
        status = quota_manager.get_quota_status()
        assert status == QuotaStatus.EXHAUSTED
    
    def test_cache_operations(self, quota_manager):
        """Testa operações de cache."""
        # Definir valor no cache
        success = quota_manager.set_cached_value("test_key", "test_value", ttl=3600, operation="search")
        assert success == True
        
        # Obter valor do cache
        value = quota_manager.get_cached_value("test_key")
        assert value == "test_value"
        
        # Obter valor inexistente
        value = quota_manager.get_cached_value("nonexistent_key")
        assert value is None
    
    def test_optimize_requests(self, quota_manager):
        """Testa otimização de requisições."""
        # Definir alguns valores no cache
        quota_manager.set_cached_value("cached_key", "cached_value", operation="search")
        
        # Lista de operações
        operations = [
            ("search", "cached_key"),      # Já está no cache
            ("search", "new_key"),         # Nova operação
            ("videos", "video_key"),       # Nova operação
            ("comments", "comment_key")    # Nova operação
        ]
        
        # Otimizar requisições
        optimized = quota_manager.optimize_requests(operations)
        
        # A operação cacheada deve ter sido removida
        assert len(optimized) == 3
        assert ("search", "cached_key") not in optimized
        assert ("search", "new_key") in optimized
        assert ("videos", "video_key") in optimized
        assert ("comments", "comment_key") in optimized


class TestYouTubeIntegration:
    """Testes de integração completa do YouTube."""
    
    @pytest.fixture
    def youtube_integration(self):
        """Setup de integração completa."""
        # Mock das dependências
        with patch('infrastructure.coleta.youtube_data_api.build'):
            with patch('infrastructure.coleta.youtube_data_api.Credentials'):
                with patch('infrastructure.coleta.youtube_quota_manager.redis.from_url'):
                    # Criar componentes
                    api = create_youtube_data_client()
                    analyzer = create_youtube_trends_analyzer()
                    quota_manager = create_youtube_quota_manager()
                    
                    return {
                        'api': api,
                        'analyzer': analyzer,
                        'quota_manager': quota_manager
                    }
    
    def test_complete_workflow(self, youtube_integration):
        """Testa workflow completo de análise de vídeo."""
        api = youtube_integration['api']
        analyzer = youtube_integration['analyzer']
        quota_manager = youtube_integration['quota_manager']
        
        # Mock das respostas da API
        mock_search_response = {
            'items': [
                {
                    'id': {'videoId': 'test_video_id'},
                    'snippet': {
                        'title': 'Python Tutorial',
                        'description': 'Learn Python programming',
                        'publishedAt': '2025-01-27T10:00:00Z',
                        'channelId': 'test_channel',
                        'channelTitle': 'Programming Channel',
                        'thumbnails': {'default': {'url': 'http://test.com/thumb.jpg'}}
                    }
                }
            ]
        }
        
        mock_video_response = {
            'items': [
                {
                    'id': 'test_video_id',
                    'snippet': {
                        'title': 'Python Tutorial',
                        'description': 'Learn Python programming',
                        'publishedAt': '2025-01-27T10:00:00Z',
                        'channelId': 'test_channel',
                        'channelTitle': 'Programming Channel',
                        'tags': ['python', 'tutorial'],
                        'categoryId': '27'
                    },
                    'statistics': {
                        'viewCount': '5000',
                        'likeCount': '500',
                        'commentCount': '100'
                    },
                    'contentDetails': {
                        'duration': 'PT15M30S'
                    }
                }
            ]
        }
        
        api.service.search.return_value.list.return_value.execute.return_value = mock_search_response
        api.service.videos.return_value.list.return_value.execute.return_value = mock_video_response
        
        # 1. Verificar quota
        assert quota_manager.check_quota_available("search")
        assert quota_manager.reserve_quota("search")
        
        # 2. Buscar vídeos
        search_results = api.search_videos("python tutorial", max_results=1)
        assert len(search_results) == 1
        
        # 3. Obter detalhes do vídeo
        assert quota_manager.check_quota_available("videos")
        assert quota_manager.reserve_quota("videos")
        
        video_details = api.get_video_details("test_video_id")
        assert video_details.title == "Python Tutorial"
        
        # 4. Analisar tendência
        video_data = {
            'id': 'test_video_id',
            'title': 'Python Tutorial',
            'description': 'Learn Python programming',
            'published_at': '2025-01-27T10:00:00Z',
            'channel_id': 'test_channel',
            'channel_title': 'Programming Channel',
            'view_count': 5000,
            'like_count': 500,
            'comment_count': 100,
            'duration': 'PT15M30S',
            'tags': ['python', 'tutorial'],
            'category_id': '27'
        }
        
        video_trend = analyzer.analyze_video_trend(video_data)
        assert video_trend.video_id == 'test_video_id'
        assert video_trend.category == 'education'
        
        # 5. Verificar status final
        quota_usage = quota_manager.get_quota_usage()
        assert quota_usage['used_today'] > 0
        assert quota_usage['status'] in ['available', 'warning']


# Testes de performance
class TestYouTubePerformance:
    """Testes de performance do YouTube."""
    
    def test_api_response_time(self):
        """Testa tempo de resposta da API."""
        with patch('infrastructure.coleta.youtube_data_api.build'):
            with patch('infrastructure.coleta.youtube_data_api.Credentials'):
                api = create_youtube_data_client()
                
                start_time = time.time()
                
                # Simular chamada da API
                with patch.object(api.service, 'search') as mock_search:
                    mock_search.return_value.list.return_value.execute.return_value = {'items': []}
                    api.search_videos("test", max_results=1)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Tempo de resposta deve ser menor que 1 segundo
                assert response_time < 1.0
    
    def test_cache_performance(self):
        """Testa performance do cache."""
        with patch('infrastructure.coleta.youtube_quota_manager.redis.from_url'):
            manager = create_youtube_quota_manager()
            
            # Testar velocidade de escrita
            start_time = time.time()
            for index in range(100):
                manager.set_cached_value(f"key_{index}", f"value_{index}", operation="test")
            write_time = time.time() - start_time
            
            # Testar velocidade de leitura
            start_time = time.time()
            for index in range(100):
                manager.get_cached_value(f"key_{index}")
            read_time = time.time() - start_time
            
            # Operações devem ser rápidas
            assert write_time < 1.0
            assert read_time < 1.0


# Testes de recuperação de falhas
class TestYouTubeRecovery:
    """Testes de recuperação de falhas."""
    
    def test_api_failure_recovery(self):
        """Testa recuperação de falhas da API."""
        with patch('infrastructure.coleta.youtube_data_api.build'):
            with patch('infrastructure.coleta.youtube_data_api.Credentials'):
                api = create_youtube_data_client()
                
                # Simular falha da API
                with patch.object(api.service, 'search') as mock_search:
                    mock_search.return_value.list.return_value.execute.side_effect = Exception("API Error")
                    
                    # Deve lançar exceção
                    with pytest.raises(Exception):
                        api.search_videos("test")
    
    def test_quota_exhaustion_recovery(self):
        """Testa recuperação quando quota é esgotada."""
        with patch('infrastructure.coleta.youtube_quota_manager.redis.from_url'):
            manager = create_youtube_quota_manager()
            
            # Esgotar quota
            manager.quota_usage.used_today = 10000
            
            # Tentar reservar quota deve falhar
            assert manager.reserve_quota("search") == False
            
            # Status deve ser esgotado
            assert manager.get_quota_status() == QuotaStatus.EXHAUSTED


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 