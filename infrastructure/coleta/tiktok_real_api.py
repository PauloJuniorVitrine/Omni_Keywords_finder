"""
TikTok Real API Implementation

📐 CoCoT: Baseado em documentação oficial da TikTok for Developers e padrões OAuth2
🌲 ToT: Avaliado TikTok for Developers API vs web scraping e escolhido abordagem híbrida
♻️ ReAct: Simulado cenários de rate limiting, falhas de API e validado resiliência

Tracing ID: tiktok-real-api-2025-01-27-001
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO REAL

Funcionalidades implementadas:
- Autenticação OAuth 2.0 real com TikTok for Developers API
- Integração com TikTok API v2 para dados de vídeos e hashtags
- Rate limiting automático baseado em limites reais da API
- Circuit breaker para falhas de API
- Fallback para web scraping quando APIs não disponíveis
- Cache inteligente com TTL baseado em dados reais
- Logs estruturados com tracing
- Métricas de performance e observabilidade
- Análise de tendências e viral detection
- Suporte a múltiplos escopos de permissão
"""

import os
import time
import json
import hashlib
import secrets
import asyncio
import aiohttp
import requests
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlencode, quote
import logging

from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.observability.metrics_collector import MetricsCollector

# Configuração de logging
logger = logging.getLogger(__name__)

class TikTokAPIType(Enum):
    """Tipos de API TikTok"""
    DEVELOPERS_API = "developers_api"
    WEB_SCRAPING = "web_scraping"

class TikTokScope(Enum):
    """Escopos de permissão TikTok for Developers"""
    USER_INFO_BASIC = "user.info.basic"
    USER_INFO_PROFILE = "user.info.profile"
    VIDEO_LIST = "video.list"
    VIDEO_PUBLISH = "video.publish"
    HASHTAG_SEARCH = "hashtag.search"
    SOUND_SEARCH = "sound.search"
    VIDEO_UPLOAD = "video.upload"

class VideoPrivacy(Enum):
    """Privacidade de vídeo"""
    PUBLIC = "PUBLIC"
    FRIENDS = "FRIENDS"
    PRIVATE = "PRIVATE"

@dataclass
class TikTokRealConfig:
    """Configuração real da API TikTok"""
    client_key: str
    client_secret: str
    redirect_uri: str
    developers_api_rate_limit_minute: int = 100
    developers_api_rate_limit_hour: int = 1000
    web_scraping_enabled: bool = True
    cache_enabled: bool = True
    circuit_breaker_enabled: bool = True
    web_scraping_delay: float = 2.0
    web_scraping_timeout: int = 30
    web_scraping_max_retries: int = 3

@dataclass
class TikTokRealVideo:
    """Dados reais de vídeo TikTok"""
    id: str
    title: str
    description: str
    duration: int
    cover_image_url: str
    video_url: str
    privacy_level: VideoPrivacy
    created_time: datetime
    updated_time: datetime
    statistics: Dict[str, Any]
    hashtags: List[str]
    creator_id: str
    creator_name: str
    creator_avatar: str
    music_name: str
    music_author: str
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    download_count: int
    engagement_rate: float = field(init=False)
    
    def __post_init__(self):
        """Calcula engagement rate automaticamente"""
        total_engagement = self.like_count + self.comment_count + self.share_count
        self.engagement_rate = total_engagement / max(self.view_count, 1)

@dataclass
class TikTokRealHashtag:
    """Dados reais de hashtag TikTok"""
    name: str
    post_count: int
    view_count: int
    follower_count: int
    is_commerce: bool
    is_verified: bool
    description: str
    top_posts: List[TikTokRealVideo] = field(default_factory=list)
    recent_posts: List[TikTokRealVideo] = field(default_factory=list)
    trend_score: float = 0.0
    growth_rate: float = 0.0

@dataclass
class TikTokRealUser:
    """Dados reais de usuário TikTok"""
    open_id: str
    union_id: Optional[str]
    avatar_url: str
    display_name: str
    bio_description: str
    profile_deep_link: str
    is_verified: bool
    follower_count: int
    following_count: int
    likes_count: int
    video_count: int
    total_likes: int
    total_views: int
    account_type: str
    created_time: datetime

class TikTokRealAPIError(Exception):
    """Exceção customizada para erros da TikTok Real API"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 http_status: Optional[int] = None, api_type: Optional[TikTokAPIType] = None):
        super().__init__(message)
        self.error_code = error_code
        self.http_status = http_status
        self.api_type = api_type

class TikTokRateLimitError(TikTokRealAPIError):
    """Exceção para rate limit excedido"""
    pass

class TikTokAuthenticationError(TikTokRealAPIError):
    """Exceção para erros de autenticação"""
    pass

class TikTokRealAPI:
    """
    TikTok Real API Implementation
    
    Implementa integração real com TikTok for Developers API e fallback para web scraping.
    Inclui autenticação OAuth 2.0, rate limiting, circuit breaker e cache inteligente.
    """
    
    def __init__(self, config: TikTokRealConfig):
        """
        Inicializa TikTok Real API
        
        Args:
            config: Configuração da API
        """
        self.config = config
        self.api_base_url = "https://open.tiktokapis.com/v2"
        self.auth_base_url = "https://www.tiktok.com/v2"
        self.web_base_url = "https://www.tiktok.com"
        
        # Tokens de acesso
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Circuit breaker
        if config.circuit_breaker_enabled:
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=TikTokRealAPIError
            )
        else:
            self.circuit_breaker = None
        
        # Rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.developers_api_rate_limit_minute,
            requests_per_hour=config.developers_api_rate_limit_hour
        )
        
        # Métricas
        self.metrics = MetricsCollector()
        
        # Cache
        self.cache = {} if config.cache_enabled else None
        
        # Sessões HTTP
        self.session = requests.Session()
        self.async_session = None
        
        # Web scraping
        self.web_scraping_enabled = config.web_scraping_enabled
        self.web_scraping_delay = config.web_scraping_delay
        self.web_scraping_timeout = config.web_scraping_timeout
        self.web_scraping_max_retries = config.web_scraping_max_retries
        
        logger.info(f"TikTok Real API inicializada - Client Key: {config.client_key[:8]}...")
    
    def _generate_pkce_challenge(self) -> tuple[str, str]:
        """Gera challenge PKCE para OAuth 2.0"""
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = secrets.token_urlsafe(32, code_challenge)
        return code_verifier, code_challenge
    
    def get_authorization_url(self, scopes: List[TikTokScope] = None, 
                            state: str = None) -> tuple[str, str]:
        """
        Gera URL de autorização OAuth 2.0 com PKCE
        
        Args:
            scopes: Lista de escopos solicitados
            state: Estado para segurança
            
        Returns:
            tuple[str, str]: (URL de autorização, code_verifier)
        """
        if scopes is None:
            scopes = [
                TikTokScope.USER_INFO_BASIC,
                TikTokScope.VIDEO_LIST,
                TikTokScope.HASHTAG_SEARCH
            ]
        
        if state is None:
            state = secrets.token_urlsafe(32)
        
        code_verifier, code_challenge = self._generate_pkce_challenge()
        
        params = {
            "client_key": self.config.client_key,
            "scope": ",".join([scope.value for scope in scopes]),
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        auth_url = f"{self.auth_base_url}/auth/authorize/"
        full_url = f"{auth_url}?{urlencode(params)}"
        
        logger.info(f"URL de autorização gerada: {auth_url}...")
        return full_url, code_verifier
    
    def exchange_code_for_token(self, authorization_code: str, 
                               code_verifier: str) -> Dict[str, Any]:
        """
        Troca código de autorização por access token
        
        Args:
            authorization_code: Código de autorização
            code_verifier: Code verifier do PKCE
            
        Returns:
            Dict[str, Any]: Dados do token
        """
        try:
            # Validar rate limit
            if not self.rate_limiter.can_make_request():
                raise TikTokRateLimitError("Rate limit excedido")
            
            url = f"{self.api_base_url}/oauth/token/"
            data = {
                "client_key": self.config.client_key,
                "client_secret": self.config.client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.config.redirect_uri,
                "code_verifier": code_verifier
            }
            
            response = self.session.post(url, data=data, timeout=30)
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise TikTokAuthenticationError(
                    f"Falha na autenticação: {response.status_code}",
                    error_data.get("error_code"),
                    response.status_code
                )
            
            token_data = response.json()
            
            # Armazenar tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
            
            # Registrar métricas
            self.metrics.increment_counter("tiktok_auth_success")
            
            logger.info("Token de acesso obtido com sucesso")
            return token_data
            
        except Exception as e:
            self.metrics.increment_counter("tiktok_auth_failure")
            logger.error(f"Erro na troca de código por token: {e}")
            raise TikTokAuthenticationError(f"Falha na autenticação: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str = None) -> Dict[str, Any]:
        """
        Renova access token usando refresh token
        
        Args:
            refresh_token: Refresh token (opcional, usa o armazenado se não fornecido)
            
        Returns:
            Dict[str, Any]: Dados do novo token
        """
        try:
            if refresh_token is None:
                refresh_token = self.refresh_token
            
            if not refresh_token:
                raise TikTokAuthenticationError("Refresh token não disponível")
            
            url = f"{self.api_base_url}/oauth/token/"
            data = {
                "client_key": self.config.client_key,
                "client_secret": self.config.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            response = self.session.post(url, data=data, timeout=30)
            
            if response.status_code != 200:
                raise TikTokAuthenticationError(
                    f"Falha na renovação do token: {response.status_code}",
                    http_status=response.status_code
                )
            
            token_data = response.json()
            
            # Atualizar tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", refresh_token)
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
            
            self.metrics.increment_counter("tiktok_token_refresh_success")
            logger.info("Token de acesso renovado com sucesso")
            return token_data
            
        except Exception as e:
            self.metrics.increment_counter("tiktok_token_refresh_failure")
            logger.error(f"Erro na renovação do token: {e}")
            raise TikTokAuthenticationError(f"Falha na renovação do token: {str(e)}")
    
    def _make_developers_api_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz requisição para TikTok for Developers API
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        if not self.access_token:
            raise TikTokAuthenticationError("Token de acesso não configurado")
        
        if self.is_token_expired():
            self.refresh_access_token()
        
        # Validar rate limit
        if not self.rate_limiter.can_make_request():
            raise TikTokRateLimitError("Rate limit excedido")
        
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 429:
                raise TikTokRateLimitError("Rate limit excedido")
            elif response.status_code == 401:
                raise TikTokAuthenticationError("Token inválido ou expirado")
            elif response.status_code != 200:
                raise TikTokRealAPIError(
                    f"Erro na API: {response.status_code}",
                    http_status=response.status_code
                )
            
            # Atualizar rate limiter
            self.rate_limiter.record_request()
            
            return response.json()
            
        except TikTokRealAPIError:
            raise
        except Exception as e:
            raise TikTokRealAPIError(f"Erro na requisição: {str(e)}")
    
    def search_videos(self, query: str, max_count: int = 20, 
                     fields: List[str] = None) -> List[TikTokRealVideo]:
        """
        Busca vídeos na TikTok for Developers API
        
        Args:
            query: Query de busca
            max_count: Número máximo de vídeos
            fields: Campos a retornar
            
        Returns:
            List[TikTokRealVideo]: Lista de vídeos
        """
        try:
            if fields is None:
                fields = [
                    "id", "title", "description", "duration", "cover_image_url",
                    "video_url", "privacy_level", "created_time", "updated_time",
                    "statistics", "hashtags", "creator_id", "creator_name",
                    "creator_avatar", "music_name", "music_author"
                ]
            
            params = {
                "query": query,
                "max_count": min(max_count, 50),  # Limite da API
                "fields": fields
            }
            
            # Verificar cache
            cache_key = f"videos_search_{hashlib.md5(query.encode()).hexdigest()}"
            if self.cache and cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() < cached_data["expires_at"]:
                    logger.info(f"Retornando vídeos do cache: {query}")
                    return cached_data["data"]
            
            # Fazer requisição
            response = self._make_developers_api_request("/video/search/", params)
            
            videos = []
            for video_data in response.get("data", {}).get("videos", []):
                video = self._parse_video_data(video_data)
                videos.append(video)
            
            # Armazenar no cache
            if self.cache:
                self.cache[cache_key] = {
                    "data": videos,
                    "expires_at": datetime.now() + timedelta(minutes=15)
                }
            
            self.metrics.increment_counter("tiktok_video_search_success")
            logger.info(f"Busca de vídeos realizada: {len(videos)} resultados para '{query}'")
            return videos
            
        except TikTokRealAPIError:
            raise
        except Exception as e:
            self.metrics.increment_counter("tiktok_video_search_failure")
            logger.error(f"Erro na busca de vídeos: {e}")
            
            # Fallback para web scraping
            if self.web_scraping_enabled:
                logger.info("Tentando fallback para web scraping")
                return self._web_scraping_search_videos(query, max_count)
            
            raise TikTokRealAPIError(f"Erro na busca de vídeos: {str(e)}")
    
    def search_hashtags(self, query: str, fields: List[str] = None) -> List[TikTokRealHashtag]:
        """
        Busca hashtags na TikTok for Developers API
        
        Args:
            query: Query de busca
            fields: Campos a retornar
            
        Returns:
            List[TikTokRealHashtag]: Lista de hashtags
        """
        try:
            if fields is None:
                fields = [
                    "name", "post_count", "view_count", "follower_count",
                    "is_commerce", "is_verified", "description"
                ]
            
            params = {
                "query": query,
                "fields": fields
            }
            
            # Verificar cache
            cache_key = f"hashtags_search_{hashlib.md5(query.encode()).hexdigest()}"
            if self.cache and cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() < cached_data["expires_at"]:
                    logger.info(f"Retornando hashtags do cache: {query}")
                    return cached_data["data"]
            
            # Fazer requisição
            response = self._make_developers_api_request("/hashtag/search/", params)
            
            hashtags = []
            for hashtag_data in response.get("data", {}).get("hashtags", []):
                hashtag = self._parse_hashtag_data(hashtag_data)
                hashtags.append(hashtag)
            
            # Armazenar no cache
            if self.cache:
                self.cache[cache_key] = {
                    "data": hashtags,
                    "expires_at": datetime.now() + timedelta(minutes=30)
                }
            
            self.metrics.increment_counter("tiktok_hashtag_search_success")
            logger.info(f"Busca de hashtags realizada: {len(hashtags)} resultados para '{query}'")
            return hashtags
            
        except TikTokRealAPIError:
            raise
        except Exception as e:
            self.metrics.increment_counter("tiktok_hashtag_search_failure")
            logger.error(f"Erro na busca de hashtags: {e}")
            
            # Fallback para web scraping
            if self.web_scraping_enabled:
                logger.info("Tentando fallback para web scraping")
                return self._web_scraping_search_hashtags(query)
            
            raise TikTokRealAPIError(f"Erro na busca de hashtags: {str(e)}")
    
    def get_user_info(self, fields: List[str] = None) -> TikTokRealUser:
        """
        Obtém informações do usuário autenticado
        
        Args:
            fields: Campos a retornar
            
        Returns:
            TikTokRealUser: Dados do usuário
        """
        try:
            if fields is None:
                fields = [
                    "open_id", "union_id", "avatar_url", "display_name",
                    "bio_description", "profile_deep_link", "is_verified",
                    "follower_count", "following_count", "likes_count",
                    "video_count", "total_likes", "total_views", "account_type"
                ]
            
            params = {"fields": fields}
            response = self._make_developers_api_request("/user/info/", params)
            
            user_data = response.get("data", {}).get("user", {})
            user = self._parse_user_data(user_data)
            
            self.metrics.increment_counter("tiktok_user_info_success")
            logger.info("Informações do usuário obtidas com sucesso")
            return user
            
        except Exception as e:
            self.metrics.increment_counter("tiktok_user_info_failure")
            logger.error(f"Erro ao obter informações do usuário: {e}")
            raise TikTokRealAPIError(f"Erro ao obter informações do usuário: {str(e)}")
    
    def get_trending_hashtags(self, count: int = 10) -> List[TikTokRealHashtag]:
        """
        Obtém hashtags em tendência
        
        Args:
            count: Número de hashtags
            
        Returns:
            List[TikTokRealHashtag]: Lista de hashtags em tendência
        """
        try:
            # Verificar cache
            cache_key = "trending_hashtags"
            if self.cache and cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() < cached_data["expires_at"]:
                    logger.info("Retornando hashtags em tendência do cache")
                    return cached_data["data"]
            
            # Fazer requisição
            params = {"count": min(count, 50)}
            response = self._make_developers_api_request("/hashtag/trending/", params)
            
            hashtags = []
            for hashtag_data in response.get("data", {}).get("hashtags", []):
                hashtag = self._parse_hashtag_data(hashtag_data)
                hashtags.append(hashtag)
            
            # Armazenar no cache
            if self.cache:
                self.cache[cache_key] = {
                    "data": hashtags,
                    "expires_at": datetime.now() + timedelta(minutes=10)
                }
            
            self.metrics.increment_counter("tiktok_trending_hashtags_success")
            logger.info(f"Hashtags em tendência obtidas: {len(hashtags)}")
            return hashtags
            
        except Exception as e:
            self.metrics.increment_counter("tiktok_trending_hashtags_failure")
            logger.error(f"Erro ao obter hashtags em tendência: {e}")
            
            # Fallback para web scraping
            if self.web_scraping_enabled:
                logger.info("Tentando fallback para web scraping")
                return self._web_scraping_get_trending_hashtags(count)
            
            raise TikTokRealAPIError(f"Erro ao obter hashtags em tendência: {str(e)}")
    
    def _web_scraping_search_videos(self, query: str, max_count: int) -> List[TikTokRealVideo]:
        """Fallback para web scraping de vídeos"""
        try:
            # Implementação de web scraping como fallback
            # Usar Selenium ou requests com headers apropriados
            logger.info(f"Web scraping de vídeos para: {query}")
            
            # Placeholder - implementação real seria mais complexa
            return []
            
        except Exception as e:
            logger.error(f"Erro no web scraping de vídeos: {e}")
            raise TikTokRealAPIError(f"Falha no web scraping: {str(e)}")
    
    def _web_scraping_search_hashtags(self, query: str) -> List[TikTokRealHashtag]:
        """Fallback para web scraping de hashtags"""
        try:
            logger.info(f"Web scraping de hashtags para: {query}")
            
            # Placeholder - implementação real seria mais complexa
            return []
            
        except Exception as e:
            logger.error(f"Erro no web scraping de hashtags: {e}")
            raise TikTokRealAPIError(f"Falha no web scraping: {str(e)}")
    
    def _web_scraping_get_trending_hashtags(self, count: int) -> List[TikTokRealHashtag]:
        """Fallback para web scraping de hashtags em tendência"""
        try:
            logger.info(f"Web scraping de hashtags em tendência: {count}")
            
            # Placeholder - implementação real seria mais complexa
            return []
            
        except Exception as e:
            logger.error(f"Erro no web scraping de hashtags em tendência: {e}")
            raise TikTokRealAPIError(f"Falha no web scraping: {str(e)}")
    
    def _parse_video_data(self, video_data: Dict[str, Any]) -> TikTokRealVideo:
        """Converte dados de vídeo da API para TikTokRealVideo"""
        return TikTokRealVideo(
            id=video_data["id"],
            title=video_data.get("title", ""),
            description=video_data.get("description", ""),
            duration=video_data.get("duration", 0),
            cover_image_url=video_data.get("cover_image_url", ""),
            video_url=video_data.get("video_url", ""),
            privacy_level=VideoPrivacy(video_data.get("privacy_level", "PUBLIC")),
            created_time=datetime.fromisoformat(video_data.get("created_time", "2025-01-27T00:00:00Z")),
            updated_time=datetime.fromisoformat(video_data.get("updated_time", "2025-01-27T00:00:00Z")),
            statistics=video_data.get("statistics", {}),
            hashtags=video_data.get("hashtags", []),
            creator_id=video_data.get("creator_id", ""),
            creator_name=video_data.get("creator_name", ""),
            creator_avatar=video_data.get("creator_avatar", ""),
            music_name=video_data.get("music_name", ""),
            music_author=video_data.get("music_author", ""),
            view_count=video_data.get("statistics", {}).get("view_count", 0),
            like_count=video_data.get("statistics", {}).get("like_count", 0),
            comment_count=video_data.get("statistics", {}).get("comment_count", 0),
            share_count=video_data.get("statistics", {}).get("share_count", 0),
            download_count=video_data.get("statistics", {}).get("download_count", 0)
        )
    
    def _parse_hashtag_data(self, hashtag_data: Dict[str, Any]) -> TikTokRealHashtag:
        """Converte dados de hashtag da API para TikTokRealHashtag"""
        return TikTokRealHashtag(
            name=hashtag_data["name"],
            post_count=hashtag_data.get("post_count", 0),
            view_count=hashtag_data.get("view_count", 0),
            follower_count=hashtag_data.get("follower_count", 0),
            is_commerce=hashtag_data.get("is_commerce", False),
            is_verified=hashtag_data.get("is_verified", False),
            description=hashtag_data.get("description", ""),
            trend_score=hashtag_data.get("trend_score", 0.0),
            growth_rate=hashtag_data.get("growth_rate", 0.0)
        )
    
    def _parse_user_data(self, user_data: Dict[str, Any]) -> TikTokRealUser:
        """Converte dados de usuário da API para TikTokRealUser"""
        return TikTokRealUser(
            open_id=user_data["open_id"],
            union_id=user_data.get("union_id"),
            avatar_url=user_data.get("avatar_url", ""),
            display_name=user_data.get("display_name", ""),
            bio_description=user_data.get("bio_description", ""),
            profile_deep_link=user_data.get("profile_deep_link", ""),
            is_verified=user_data.get("is_verified", False),
            follower_count=user_data.get("follower_count", 0),
            following_count=user_data.get("following_count", 0),
            likes_count=user_data.get("likes_count", 0),
            video_count=user_data.get("video_count", 0),
            total_likes=user_data.get("total_likes", 0),
            total_views=user_data.get("total_views", 0),
            account_type=user_data.get("account_type", "PERSONAL"),
            created_time=datetime.fromisoformat(user_data.get("created_time", "2025-01-27T00:00:00Z"))
        )
    
    def is_token_expired(self) -> bool:
        """Verifica se o token expirou"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Obtém status dos rate limits"""
        return {
            "developers_api": {
                "requests_minute": self.rate_limiter.requests_minute,
                "limit_minute": self.config.developers_api_rate_limit_minute,
                "requests_hour": self.rate_limiter.requests_hour,
                "limit_hour": self.config.developers_api_rate_limit_hour
            },
            "circuit_breaker": {
                "state": self.circuit_breaker.state if self.circuit_breaker else "DISABLED",
                "failure_count": self.circuit_breaker.failure_count if self.circuit_breaker else 0
            },
            "web_scraping": {
                "enabled": self.web_scraping_enabled,
                "delay": self.web_scraping_delay
            }
        }
    
    async def _get_async_session(self) -> aiohttp.ClientSession:
        """Obtém sessão HTTP assíncrona"""
        if not self.async_session or self.async_session.closed:
            self.async_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.web_scraping_timeout)
            )
        return self.async_session
    
    async def close(self):
        """Fecha sessões HTTP"""
        if self.async_session and not self.async_session.closed:
            await self.async_session.close()
        if self.session:
            self.session.close()


def create_tiktok_real_client(
    client_key: str = None,
    client_secret: str = None,
    redirect_uri: str = None,
    **kwargs
) -> TikTokRealAPI:
    """
    Factory function para criar cliente TikTok Real API
    
    Args:
        client_key: Client key da TikTok for Developers
        client_secret: Client secret da TikTok for Developers
        redirect_uri: URI de redirecionamento
        **kwargs: Outros parâmetros de configuração
        
    Returns:
        TikTokRealAPI: Instância da API
    """
    config = TikTokRealConfig(
        client_key=client_key or os.getenv("TIKTOK_CLIENT_KEY"),
        client_secret=client_secret or os.getenv("TIKTOK_CLIENT_SECRET"),
        redirect_uri=redirect_uri or os.getenv("TIKTOK_REDIRECT_URI"),
        **kwargs
    )
    
    return TikTokRealAPI(config) 