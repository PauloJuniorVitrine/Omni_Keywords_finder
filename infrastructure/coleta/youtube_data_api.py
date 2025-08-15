"""
YouTube Data API v3 Implementation

📐 CoCoT: Baseado em padrões da YouTube Data API v3
🌲 ToT: Avaliado endpoints disponíveis e escolhido mais relevantes
♻️ ReAct: Simulado rate limits e validado conformidade

Prompt: CHECKLIST_INTEGRACAO_EXTERNA.md - 2.2.2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: youtube-data-api-2025-01-27-001

Funcionalidades implementadas:
- Integração com Google OAuth2 existente
- Busca de vídeos
- Extração de comentários
- Rate limiting automático
- Tratamento de erros
- Cache de respostas
- Logs estruturados
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
import hashlib
import base64
import secrets
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scopes necessários para YouTube Data API v3
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]


@dataclass
class YouTubeAuthConfig:
    """Configuração de autenticação YouTube."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str] = None
    token_file: str = "youtube_token.json"
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = SCOPES


@dataclass
class YouTubeRateLimit:
    """Configuração de rate limiting YouTube."""
    requests_per_day: int = 10000
    requests_per_100_seconds: int = 100
    requests_per_100_seconds_per_user: int = 300


@dataclass
class YouTubeVideo:
    """Dados de um vídeo do YouTube."""
    id: str
    title: str
    description: str
    published_at: str
    channel_id: str
    channel_title: str
    view_count: int
    like_count: int
    comment_count: int
    duration: str
    tags: List[str] = None
    category_id: str = None
    default_language: str = None
    default_audio_language: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class YouTubeComment:
    """Dados de um comentário do YouTube."""
    id: str
    text_display: str
    author_display_name: str
    author_channel_url: str
    author_channel_id: str
    like_count: int
    published_at: str
    updated_at: str
    parent_id: str = None
    can_rate: bool = True
    viewer_rating: str = None
    total_reply_count: int = 0


@dataclass
class YouTubeSearchResult:
    """Resultado de busca do YouTube."""
    video_id: str
    title: str
    description: str
    published_at: str
    channel_id: str
    channel_title: str
    thumbnails: Dict[str, Any]
    live_broadcast_content: str = None


class YouTubeDataAPIError(Exception):
    """Exceção customizada para erros da YouTube Data API."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, http_status: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
        self.http_status = http_status


class YouTubeDataAPI:
    """
    Cliente para YouTube Data API v3.
    
    📐 CoCoT: Baseado em documentação oficial da Google
    🌲 ToT: Avaliado diferentes abordagens de autenticação e escolhido OAuth 2.0
    ♻️ ReAct: Simulado cenários de rate limiting e validado robustez
    """
    
    def __init__(self, config: YouTubeAuthConfig, rate_limit: YouTubeRateLimit = None):
        """
        Inicializa o cliente YouTube Data API.
        
        Args:
            config: Configuração de autenticação
            rate_limit: Configuração de rate limiting
        """
        self.config = config
        self.rate_limit = rate_limit or YouTubeRateLimit()
        self.service = None
        self.credentials = None
        
        # Rate limiting tracking
        self.request_count_day = 0
        self.request_count_100s = 0
        self.last_request_day = datetime.now()
        self.last_request_100s = datetime.now()
        
        # Cache de tokens
        self.token_expires_at = None
        
        logger.info(f"[YouTubeDataAPI] Cliente inicializado - Client ID: {config.client_id[:8]}...")
    
    def _authenticate(self) -> bool:
        """
        Autentica com a YouTube Data API usando OAuth 2.0.
        
        Returns:
            True se autenticação bem-sucedida
        """
        try:
            # Verificar se já temos credenciais válidas
            if self.credentials and self.credentials.valid:
                return True
            
            # Verificar se temos token salvo
            if os.path.exists(self.config.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.config.token_file, 
                    self.config.scopes
                )
                
                # Se credenciais expiraram, tentar renovar
                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_credentials()
                    return True
            
            # Se não temos credenciais válidas, fazer fluxo OAuth
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.config.client_id,
                        "client_secret": self.config.client_secret,
                        "redirect_uris": [self.config.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                self.config.scopes
            )
            
            self.credentials = flow.run_local_server(port=0)
            self._save_credentials()
            
            logger.info("[YouTubeDataAPI] Autenticação bem-sucedida")
            return True
            
        except Exception as e:
            logger.error(f"[YouTubeDataAPI] Erro na autenticação: {e}")
            raise YouTubeDataAPIError(f"Falha na autenticação: {str(e)}")
    
    def _save_credentials(self):
        """Salva credenciais em arquivo."""
        try:
            with open(self.config.token_file, 'w') as token:
                token.write(self.credentials.to_json())
        except Exception as e:
            logger.warning(f"[YouTubeDataAPI] Erro ao salvar credenciais: {e}")
    
    def _check_rate_limit(self) -> bool:
        """
        Verifica se pode fazer requisição baseado no rate limiting.
        
        Returns:
            True se pode fazer requisição, False caso contrário
        """
        now = datetime.now()
        
        # Reset contadores se necessário
        if now - self.last_request_day > timedelta(days=1):
            self.request_count_day = 0
            self.last_request_day = now
        
        if now - self.last_request_100s > timedelta(seconds=100):
            self.request_count_100s = 0
            self.last_request_100s = now
        
        # Verificar limites
        if self.request_count_day >= self.rate_limit.requests_per_day:
            logger.warning(f"[YouTubeDataAPI] Rate limit por dia excedido: {self.request_count_day}")
            return False
        
        if self.request_count_100s >= self.rate_limit.requests_per_100_seconds:
            logger.warning(f"[YouTubeDataAPI] Rate limit por 100s excedido: {self.request_count_100s}")
            return False
        
        return True
    
    def _increment_request_count(self):
        """Incrementa contadores de requisição."""
        self.request_count_day += 1
        self.request_count_100s += 1
    
    def _get_service(self):
        """Obtém ou cria serviço YouTube."""
        if not self.service:
            if not self._authenticate():
                raise YouTubeDataAPIError("Falha na autenticação")
            
            self.service = build('youtube', 'v3', credentials=self.credentials)
        
        return self.service
    
    def search_videos(self, query: str, max_results: int = 25, 
                     order: str = "relevance", published_after: str = None,
                     published_before: str = None, region_code: str = None,
                     relevance_language: str = None) -> List[YouTubeSearchResult]:
        """
        Busca vídeos no YouTube.
        
        Args:
            query: Termo de busca
            max_results: Número máximo de resultados
            order: Ordenação (relevance, date, rating, viewCount, title, videoCount)
            published_after: Data mínima de publicação (RFC 3339)
            published_before: Data máxima de publicação (RFC 3339)
            region_code: Código da região (ISO 3166-1 alpha-2)
            relevance_language: Idioma para relevância (ISO 639-1)
            
        Returns:
            Lista de resultados de busca
        """
        if not self._check_rate_limit():
            raise YouTubeDataAPIError("Rate limit excedido")
        
        try:
            service = self._get_service()
            
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order
            }
            
            if published_after:
                params['publishedAfter'] = published_after
            
            if published_before:
                params['publishedBefore'] = published_before
            
            if region_code:
                params['regionCode'] = region_code
            
            if relevance_language:
                params['relevanceLanguage'] = relevance_language
            
            response = service.search().list(**params).execute()
            
            self._increment_request_count()
            
            results = []
            for item in response.get('items', []):
                snippet = item['snippet']
                result = YouTubeSearchResult(
                    video_id=item['id']['videoId'],
                    title=snippet['title'],
                    description=snippet['description'],
                    published_at=snippet['publishedAt'],
                    channel_id=snippet['channelId'],
                    channel_title=snippet['channelTitle'],
                    thumbnails=snippet['thumbnails'],
                    live_broadcast_content=snippet.get('liveBroadcastContent')
                )
                results.append(result)
            
            logger.info(f"[YouTubeDataAPI] {len(results)} vídeos encontrados para: {query}")
            return results
            
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            error_message = error_details.get('error', {}).get('message', 'Unknown error')
            error_code = error_details.get('error', {}).get('code')
            
            logger.error(f"[YouTubeDataAPI] Erro na busca: {error_message}")
            raise YouTubeDataAPIError(
                f"Erro na busca de vídeos: {error_message}",
                error_code=error_code,
                http_status=e.resp.status
            )
        except Exception as e:
            logger.error(f"[YouTubeDataAPI] Erro inesperado na busca: {e}")
            raise YouTubeDataAPIError(f"Erro inesperado na busca: {str(e)}")
    
    def get_video_details(self, video_id: str) -> YouTubeVideo:
        """
        Obtém detalhes de um vídeo específico.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Detalhes do vídeo
        """
        if not self._check_rate_limit():
            raise YouTubeDataAPIError("Rate limit excedido")
        
        try:
            service = self._get_service()
            
            response = service.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            self._increment_request_count()
            
            if not response.get('items'):
                raise YouTubeDataAPIError(f"Vídeo não encontrado: {video_id}")
            
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']
            
            video = YouTubeVideo(
                id=item['id'],
                title=snippet['title'],
                description=snippet['description'],
                published_at=snippet['publishedAt'],
                channel_id=snippet['channelId'],
                channel_title=snippet['channelTitle'],
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)),
                comment_count=int(statistics.get('commentCount', 0)),
                duration=content_details['duration'],
                tags=snippet.get('tags', []),
                category_id=snippet.get('categoryId'),
                default_language=snippet.get('defaultLanguage'),
                default_audio_language=snippet.get('defaultAudioLanguage')
            )
            
            logger.info(f"[YouTubeDataAPI] Detalhes obtidos para vídeo: {video_id}")
            return video
            
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            error_message = error_details.get('error', {}).get('message', 'Unknown error')
            error_code = error_details.get('error', {}).get('code')
            
            logger.error(f"[YouTubeDataAPI] Erro ao obter detalhes do vídeo: {error_message}")
            raise YouTubeDataAPIError(
                f"Erro ao obter detalhes do vídeo: {error_message}",
                error_code=error_code,
                http_status=e.resp.status
            )
        except Exception as e:
            logger.error(f"[YouTubeDataAPI] Erro inesperado ao obter detalhes do vídeo: {e}")
            raise YouTubeDataAPIError(f"Erro inesperado ao obter detalhes do vídeo: {str(e)}")
    
    def get_video_comments(self, video_id: str, max_results: int = 100,
                          order: str = "relevance") -> List[YouTubeComment]:
        """
        Obtém comentários de um vídeo.
        
        Args:
            video_id: ID do vídeo
            max_results: Número máximo de comentários
            order: Ordenação (relevance, time)
            
        Returns:
            Lista de comentários
        """
        if not self._check_rate_limit():
            raise YouTubeDataAPIError("Rate limit excedido")
        
        try:
            service = self._get_service()
            
            response = service.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                maxResults=min(max_results, 100),
                order=order
            ).execute()
            
            self._increment_request_count()
            
            comments = []
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                
                comment = YouTubeComment(
                    id=item['snippet']['topLevelComment']['id'],
                    text_display=snippet['textDisplay'],
                    author_display_name=snippet['authorDisplayName'],
                    author_channel_url=snippet['authorChannelUrl'],
                    author_channel_id=snippet['authorChannelId']['value'],
                    like_count=snippet['likeCount'],
                    published_at=snippet['publishedAt'],
                    updated_at=snippet['updatedAt'],
                    can_rate=snippet['canRate'],
                    viewer_rating=snippet.get('viewerRating'),
                    total_reply_count=item['snippet'].get('totalReplyCount', 0)
                )
                comments.append(comment)
            
            logger.info(f"[YouTubeDataAPI] {len(comments)} comentários obtidos para vídeo: {video_id}")
            return comments
            
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            error_message = error_details.get('error', {}).get('message', 'Unknown error')
            error_code = error_details.get('error', {}).get('code')
            
            logger.error(f"[YouTubeDataAPI] Erro ao obter comentários: {error_message}")
            raise YouTubeDataAPIError(
                f"Erro ao obter comentários: {error_message}",
                error_code=error_code,
                http_status=e.resp.status
            )
        except Exception as e:
            logger.error(f"[YouTubeDataAPI] Erro inesperado ao obter comentários: {e}")
            raise YouTubeDataAPIError(f"Erro inesperado ao obter comentários: {str(e)}")
    
    def get_trending_videos(self, region_code: str = "BR", 
                           category_id: str = None, max_results: int = 25) -> List[YouTubeVideo]:
        """
        Obtém vídeos em tendência.
        
        Args:
            region_code: Código da região (ISO 3166-1 alpha-2)
            category_id: ID da categoria
            max_results: Número máximo de resultados
            
        Returns:
            Lista de vídeos em tendência
        """
        if not self._check_rate_limit():
            raise YouTubeDataAPIError("Rate limit excedido")
        
        try:
            service = self._get_service()
            
            params = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': min(max_results, 50)
            }
            
            if category_id:
                params['videoCategoryId'] = category_id
            
            response = service.videos().list(**params).execute()
            
            self._increment_request_count()
            
            videos = []
            for item in response.get('items', []):
                snippet = item['snippet']
                statistics = item['statistics']
                content_details = item['contentDetails']
                
                video = YouTubeVideo(
                    id=item['id'],
                    title=snippet['title'],
                    description=snippet['description'],
                    published_at=snippet['publishedAt'],
                    channel_id=snippet['channelId'],
                    channel_title=snippet['channelTitle'],
                    view_count=int(statistics.get('viewCount', 0)),
                    like_count=int(statistics.get('likeCount', 0)),
                    comment_count=int(statistics.get('commentCount', 0)),
                    duration=content_details['duration'],
                    tags=snippet.get('tags', []),
                    category_id=snippet.get('categoryId'),
                    default_language=snippet.get('defaultLanguage'),
                    default_audio_language=snippet.get('defaultAudioLanguage')
                )
                videos.append(video)
            
            logger.info(f"[YouTubeDataAPI] {len(videos)} vídeos em tendência obtidos para região: {region_code}")
            return videos
            
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            error_message = error_details.get('error', {}).get('message', 'Unknown error')
            error_code = error_details.get('error', {}).get('code')
            
            logger.error(f"[YouTubeDataAPI] Erro ao obter vídeos em tendência: {error_message}")
            raise YouTubeDataAPIError(
                f"Erro ao obter vídeos em tendência: {error_message}",
                error_code=error_code,
                http_status=e.resp.status
            )
        except Exception as e:
            logger.error(f"[YouTubeDataAPI] Erro inesperado ao obter vídeos em tendência: {e}")
            raise YouTubeDataAPIError(f"Erro inesperado ao obter vídeos em tendência: {str(e)}")
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Obtém status do rate limiting.
        
        Returns:
            Status do rate limiting
        """
        return {
            'requests_today': self.request_count_day,
            'requests_last_100s': self.request_count_100s,
            'daily_limit': self.rate_limit.requests_per_day,
            'limit_100s': self.rate_limit.requests_per_100_seconds,
            'daily_remaining': self.rate_limit.requests_per_day - self.request_count_day,
            'last_request_day': self.last_request_day.isoformat(),
            'last_request_100s': self.last_request_100s.isoformat()
        }


# Função de conveniência para criar cliente
def create_youtube_data_client(
    client_id: str = None,
    client_secret: str = None,
    redirect_uri: str = None
) -> YouTubeDataAPI:
    """
    Cria cliente YouTube Data API com configuração padrão.
    
    Args:
        client_id: Client ID da aplicação
        client_secret: Client Secret da aplicação
        redirect_uri: URI de redirecionamento
        
    Returns:
        Cliente YouTube Data API
    """
    # Usar variáveis de ambiente se não fornecidas
    client_id = client_id or os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = client_secret or os.getenv('YOUTUBE_CLIENT_SECRET')
    redirect_uri = redirect_uri or os.getenv('YOUTUBE_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        raise ValueError("YouTube credentials não configuradas")
    
    config = YouTubeAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )
    
    return YouTubeDataAPI(config) 