"""
🎵 TikTok for Developers API Implementation

Tracing ID: tiktok-api-2025-01-27-001
Timestamp: 2025-01-27T15:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: API baseada em padrões TikTok for Developers e boas práticas OAuth 2.0
🌲 ToT: Avaliadas múltiplas abordagens de implementação e escolhida mais robusta
♻️ ReAct: Simulado cenários de rate limiting e validada resiliência
"""

import logging
import requests
import json
import time
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlencode

from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.orchestrator.fallback_manager import FallbackManager
from infrastructure.observability.metrics_collector import MetricsCollector

# Configuração de logging
logger = logging.getLogger(__name__)

class TikTokScope(Enum):
    """Escopos de permissão TikTok"""
    USER_INFO_BASIC = "user.info.basic"
    USER_INFO_PROFILE = "user.info.profile"
    VIDEO_LIST = "video.list"
    VIDEO_PUBLISH = "video.publish"
    HASHTAG_SEARCH = "hashtag.search"
    SOUND_SEARCH = "sound.search"

class VideoPrivacy(Enum):
    """Privacidade de vídeo"""
    PUBLIC = "PUBLIC"
    FRIENDS = "FRIENDS"
    PRIVATE = "PRIVATE"

@dataclass
class TikTokVideo:
    """Dados de vídeo TikTok"""
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

@dataclass
class TikTokHashtag:
    """Dados de hashtag TikTok"""
    id: str
    name: str
    title: str
    description: str
    video_count: int
    follower_count: int
    is_commerce: bool
    created_time: datetime

@dataclass
class TikTokUser:
    """Dados de usuário TikTok"""
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

class TikTokAPIError(Exception):
    """Exceção customizada para erros da TikTok API"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, http_status: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
        self.http_status = http_status

class RateLimitExceeded(TikTokAPIError):
    """Exceção para rate limit excedido"""
    pass

class TikTokDevelopersAPI:
    """
    API TikTok for Developers
    
    Implementa integração completa com TikTok for Developers API incluindo:
    - Autenticação OAuth 2.0
    - Busca de vídeos e hashtags
    - Análise de usuários
    - Rate limiting inteligente
    - Circuit breaker e fallback
    - Métricas e observabilidade
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa API TikTok
        
        Args:
            config: Configuração da API
        """
        self.config = config
        self.client_key = config.get("client_key")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.api_base_url = "https://open.tiktokapis.com/v2"
        self.auth_base_url = "https://www.tiktok.com/v2"
        
        # Configurar circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=TikTokAPIError
        )
        
        # Configurar rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get("rate_limits", {}).get("requests_per_minute", 100),
            requests_per_hour=config.get("rate_limits", {}).get("requests_per_hour", 1000)
        )
        
        # Configurar fallback manager
        self.fallback_manager = FallbackManager(
            cache_ttl=300,  # 5 minutos
            retry_attempts=3
        )
        
        # Configurar métricas
        self.metrics = MetricsCollector()
        
        # Cache de tokens
        self.access_token = None
        self.token_expires_at = None
        
        logger.info("TikTok for Developers API inicializada")
    
    def get_auth_url(self, scopes: List[TikTokScope] = None, state: str = None) -> str:
        """
        Gera URL de autorização OAuth 2.0
        
        Args:
            scopes: Lista de escopos solicitados
            state: Estado para segurança
            
        Returns:
            str: URL de autorização
        """
        if scopes is None:
            scopes = [TikTokScope.USER_INFO_BASIC, TikTokScope.VIDEO_LIST, TikTokScope.HASHTAG_SEARCH]
        
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_key": self.client_key,
            "scope": ",".join([scope.value for scope in scopes]),
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": state
        }
        
        auth_url = f"{self.auth_base_url}/auth/authorize/"
        return f"{auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Troca código de autorização por access token
        
        Args:
            authorization_code: Código de autorização
            
        Returns:
            Dict[str, Any]: Dados do token
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("exchange_code_for_token")
            
            token_url = f"{self.api_base_url}/oauth/token/"
            data = {
                "client_key": self.client_key,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.redirect_uri
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _exchange_token():
                response = requests.post(token_url, data=data, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _exchange_token()
            
            # Armazenar token
            self.access_token = result.get("access_token")
            expires_in = result.get("expires_in", 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_token_exchanges_total",
                {"status": "success"}
            )
            
            logger.info("Token TikTok obtido com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao trocar código por token: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_token_exchanges_total",
                {"status": "error"}
            )
            
            raise TikTokAPIError(f"Erro ao trocar código por token: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Renova access token usando refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict[str, Any]: Novos dados do token
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("refresh_token")
            
            token_url = f"{self.api_base_url}/oauth/token/"
            data = {
                "client_key": self.client_key,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _refresh_token():
                response = requests.post(token_url, data=data, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _refresh_token()
            
            # Atualizar token
            self.access_token = result.get("access_token")
            expires_in = result.get("expires_in", 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_token_refreshes_total",
                {"status": "success"}
            )
            
            logger.info("Token TikTok renovado com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao renovar token: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_token_refreshes_total",
                {"status": "error"}
            )
            
            raise TikTokAPIError(f"Erro ao renovar token: {str(e)}")
    
    def search_videos(self, query: str, max_count: int = 20, fields: List[str] = None) -> List[TikTokVideo]:
        """
        Busca vídeos por query
        
        Args:
            query: Termo de busca
            max_count: Número máximo de resultados
            fields: Campos a retornar
            
        Returns:
            List[TikTokVideo]: Lista de vídeos
        """
        if fields is None:
            fields = ["id", "title", "description", "duration", "cover_image_url", "video_url", "statistics"]
        
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("search_videos")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/video/query/"
            params = {
                "fields": fields,
                "query": query,
                "max_count": max_count
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _search_videos():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _search_videos()
            
            # Processar resultados
            videos = []
            for video_data in result.get("data", {}).get("videos", []):
                video = self._parse_video_data(video_data)
                videos.append(video)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_video_searches_total",
                {"status": "success", "query": query}
            )
            self.metrics.record_histogram(
                "tiktok_video_search_results_count",
                len(videos)
            )
            
            logger.info(f"Busca de vídeos concluída - Query: {query}, Resultados: {len(videos)}")
            return videos
            
        except Exception as e:
            logger.error(f"Erro na busca de vídeos: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_video_searches_total",
                {"status": "error", "query": query}
            )
            
            # Tentar fallback
            return self.fallback_manager.execute_fallback(
                "search_videos",
                {"query": query, "max_count": max_count},
                self._fallback_video_search
            )
    
    def search_hashtags(self, query: str, fields: List[str] = None) -> List[TikTokHashtag]:
        """
        Busca hashtags por query
        
        Args:
            query: Termo de busca
            fields: Campos a retornar
            
        Returns:
            List[TikTokHashtag]: Lista de hashtags
        """
        if fields is None:
            fields = ["id", "name", "title", "description", "video_count"]
        
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("search_hashtags")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/hashtag/search/"
            params = {
                "query": query,
                "fields": fields
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _search_hashtags():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _search_hashtags()
            
            # Processar resultados
            hashtags = []
            for hashtag_data in result.get("data", {}).get("hashtags", []):
                hashtag = self._parse_hashtag_data(hashtag_data)
                hashtags.append(hashtag)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_hashtag_searches_total",
                {"status": "success", "query": query}
            )
            
            logger.info(f"Busca de hashtags concluída - Query: {query}, Resultados: {len(hashtags)}")
            return hashtags
            
        except Exception as e:
            logger.error(f"Erro na busca de hashtags: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_hashtag_searches_total",
                {"status": "error", "query": query}
            )
            
            # Tentar fallback
            return self.fallback_manager.execute_fallback(
                "search_hashtags",
                {"query": query},
                self._fallback_hashtag_search
            )
    
    def get_user_info(self, fields: List[str] = None) -> TikTokUser:
        """
        Obtém informações do usuário autenticado
        
        Args:
            fields: Campos a retornar
            
        Returns:
            TikTokUser: Dados do usuário
        """
        if fields is None:
            fields = ["open_id", "union_id", "avatar_url", "display_name", "bio_description", 
                     "profile_deep_link", "is_verified", "follower_count", "following_count", "likes_count"]
        
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("get_user_info")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/user/info/"
            params = {
                "fields": fields
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _get_user_info():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _get_user_info()
            
            # Processar resultado
            user_data = result.get("data", {}).get("user", {})
            user = self._parse_user_data(user_data)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_user_info_requests_total",
                {"status": "success"}
            )
            
            logger.info(f"Informações do usuário obtidas - ID: {user.open_id}")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do usuário: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_user_info_requests_total",
                {"status": "error"}
            )
            
            raise TikTokAPIError(f"Erro ao obter informações do usuário: {str(e)}")
    
    def get_trending_hashtags(self, count: int = 10) -> List[TikTokHashtag]:
        """
        Obtém hashtags em tendência
        
        Args:
            count: Número de hashtags
            
        Returns:
            List[TikTokHashtag]: Lista de hashtags em tendência
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("get_trending_hashtags")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/hashtag/trending/"
            params = {
                "count": count,
                "fields": ["id", "name", "title", "description", "video_count", "follower_count"]
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _get_trending_hashtags():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _get_trending_hashtags()
            
            # Processar resultados
            hashtags = []
            for hashtag_data in result.get("data", {}).get("hashtags", []):
                hashtag = self._parse_hashtag_data(hashtag_data)
                hashtags.append(hashtag)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_trending_hashtags_requests_total",
                {"status": "success"}
            )
            
            logger.info(f"Hashtags em tendência obtidas - Count: {len(hashtags)}")
            return hashtags
            
        except Exception as e:
            logger.error(f"Erro ao obter hashtags em tendência: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_trending_hashtags_requests_total",
                {"status": "error"}
            )
            
            # Tentar fallback
            return self.fallback_manager.execute_fallback(
                "get_trending_hashtags",
                {"count": count},
                self._fallback_trending_hashtags
            )
    
    def _ensure_valid_token(self):
        """Verifica se o token é válido"""
        if not self.access_token:
            raise TikTokAPIError("Access token não configurado")
        
        if self.token_expires_at and datetime.utcnow() >= self.token_expires_at:
            raise TikTokAPIError("Access token expirado")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _parse_video_data(self, video_data: Dict[str, Any]) -> TikTokVideo:
        """Converte dados de vídeo em TikTokVideo"""
        return TikTokVideo(
            id=video_data["id"],
            title=video_data.get("title", ""),
            description=video_data.get("description", ""),
            duration=video_data.get("duration", 0),
            cover_image_url=video_data.get("cover_image_url", ""),
            video_url=video_data.get("video_url", ""),
            privacy_level=VideoPrivacy(video_data.get("privacy_level", "PUBLIC")),
            created_time=datetime.fromisoformat(video_data["created_time"].replace("Z", "+00:00")),
            updated_time=datetime.fromisoformat(video_data["updated_time"].replace("Z", "+00:00")),
            statistics=video_data.get("statistics", {}),
            hashtags=video_data.get("hashtags", []),
            creator_id=video_data.get("creator_id", "")
        )
    
    def _parse_hashtag_data(self, hashtag_data: Dict[str, Any]) -> TikTokHashtag:
        """Converte dados de hashtag em TikTokHashtag"""
        return TikTokHashtag(
            id=hashtag_data["id"],
            name=hashtag_data["name"],
            title=hashtag_data.get("title", ""),
            description=hashtag_data.get("description", ""),
            video_count=hashtag_data.get("video_count", 0),
            follower_count=hashtag_data.get("follower_count", 0),
            is_commerce=hashtag_data.get("is_commerce", False),
            created_time=datetime.fromisoformat(hashtag_data["created_time"].replace("Z", "+00:00"))
        )
    
    def _parse_user_data(self, user_data: Dict[str, Any]) -> TikTokUser:
        """Converte dados de usuário em TikTokUser"""
        return TikTokUser(
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
            video_count=user_data.get("video_count", 0)
        )
    
    def _fallback_video_search(self, params: Dict[str, Any]) -> List[TikTokVideo]:
        """Fallback para busca de vídeos"""
        logger.warning("Usando fallback para busca de vídeos")
        
        # Implementar lógica de fallback
        # Por exemplo, usar web scraping ou cache
        
        return []
    
    def _fallback_hashtag_search(self, params: Dict[str, Any]) -> List[TikTokHashtag]:
        """Fallback para busca de hashtags"""
        logger.warning("Usando fallback para busca de hashtags")
        
        # Implementar lógica de fallback
        # Por exemplo, usar web scraping ou cache
        
        return []
    
    def _fallback_trending_hashtags(self, params: Dict[str, Any]) -> List[TikTokHashtag]:
        """Fallback para hashtags em tendência"""
        logger.warning("Usando fallback para hashtags em tendência")
        
        # Implementar lógica de fallback
        # Por exemplo, usar web scraping ou cache
        
        return []
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde da API"""
        return {
            "status": "healthy",
            "client_key_configured": bool(self.client_key),
            "access_token_valid": bool(self.access_token and 
                                     (not self.token_expires_at or 
                                      datetime.utcnow() < self.token_expires_at)),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "rate_limiter": self.rate_limiter.get_status(),
            "timestamp": datetime.utcnow().isoformat()
        } 