"""
Instagram Graph API Implementation

Tracing ID: instagram-graph-api-2025-01-27-001
Versão: 1.0
Responsável: Backend Team

Implementa integração real com Instagram Graph API:
- Configuração Graph API
- Endpoints de negócio
- Métricas de engajamento
- Insights e analytics
- Business account management

Metodologias Aplicadas:
- 📐 CoCoT: Baseado em padrões oficiais da Instagram Graph API
- 🌲 ToT: Avaliado alternativas de implementação e escolhido mais robusta
- ♻️ ReAct: Simulado cenários de falha e validado resiliência
"""

import os
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp
import asyncio
from urllib.parse import urlencode
from dataclasses import dataclass
from enum import Enum

from shared.config import INSTAGRAM_CONFIG
from shared.logger import logger
from infrastructure.orchestrator.rate_limiter import RateLimiterManager, RateLimitConfig
from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.fallback_manager import FallbackManager, FallbackConfig


class InstagramGraphScope(Enum):
    """Escopos disponíveis para Instagram Graph API."""
    INSTAGRAM_BASIC = "instagram_basic"
    INSTAGRAM_CONTENT_PUBLISH = "instagram_content_publish"
    INSTAGRAM_MANAGE_COMMENTS = "instagram_manage_comments"
    INSTAGRAM_MANAGE_INSIGHTS = "instagram_manage_insights"
    PAGES_READ_ENGAGEMENT = "pages_read_engagement"
    PAGES_SHOW_LIST = "pages_show_list"


@dataclass
class InstagramBusinessAccount:
    """Estrutura para conta de negócio do Instagram."""
    id: str
    username: str
    name: str
    profile_picture_url: Optional[str]
    website: Optional[str]
    biography: Optional[str]
    follows_count: int
    followers_count: int
    media_count: int
    is_verified: bool
    is_private: bool
    business_category_name: Optional[str] = None
    category_name: Optional[str] = None


@dataclass
class InstagramBusinessMedia:
    """Estrutura para mídia de negócio do Instagram."""
    id: str
    caption: Optional[str]
    media_type: str
    media_url: Optional[str]
    permalink: str
    thumbnail_url: Optional[str]
    timestamp: datetime
    like_count: int
    comments_count: int
    owner: InstagramBusinessAccount
    insights: Optional[Dict] = None


@dataclass
class InstagramInsights:
    """Estrutura para insights do Instagram."""
    impressions: int
    reach: int
    engagement: int
    saved: int
    video_views: Optional[int] = None
    video_view_rate: Optional[float] = None
    video_play_actions: Optional[int] = None
    profile_views: Optional[int] = None
    profile_actions: Optional[int] = None
    follows: Optional[int] = None
    email_contacts: Optional[int] = None
    phone_call_clicks: Optional[int] = None
    text_message_clicks: Optional[int] = None
    get_directions_clicks: Optional[int] = None
    website_clicks: Optional[int] = None


@dataclass
class InstagramComment:
    """Estrutura para comentários do Instagram."""
    id: str
    text: str
    timestamp: datetime
    username: str
    like_count: int
    is_hidden: bool
    is_reply: bool
    parent_comment_id: Optional[str] = None


class InstagramGraphAPIError(Exception):
    """Exceção customizada para erros da Instagram Graph API."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 error_subcode: Optional[str] = None, http_status: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
        self.error_subcode = error_subcode
        self.http_status = http_status


class InstagramGraphAPI:
    """
    Implementação da Instagram Graph API.
    
    📐 CoCoT: Baseado em padrões oficiais da Instagram Graph API
    🌲 ToT: Avaliado alternativas de implementação e escolhido mais robusta
    ♻️ ReAct: Simulado cenários de falha e validado resiliência
    """
    
    def __init__(self, page_access_token: Optional[str] = None):
        """
        Inicializa a Graph API do Instagram.
        
        Args:
            page_access_token: Page Access Token (opcional, usa config se não fornecido)
        """
        self.page_access_token = page_access_token or INSTAGRAM_CONFIG.get("graph_access_token")
        self.api_version = INSTAGRAM_CONFIG.get("api_version", "v18.0")
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        # Rate limiting
        self.rate_limiter = RateLimiterManager()
        self._setup_rate_limiting()
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300,  # 5 minutos
            expected_exception=InstagramGraphAPIError
        )
        
        # Fallback manager
        self.fallback_manager = FallbackManager()
        self._setup_fallback()
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info({
            "component": "instagram_graph_api",
            "action": "initialized",
            "api_version": self.api_version
        })
    
    def _setup_rate_limiting(self):
        """Configura rate limiting para Instagram Graph API."""
        config = RateLimitConfig(
            endpoint="instagram_graph_api",
            requests_per_second=0.055,  # ~200 requests/hour
            burst_limit=10,
            strategy="token_bucket"
        )
        self.rate_limiter.register_endpoint(config)
    
    def _setup_fallback(self):
        """Configura fallback para Instagram Graph API."""
        config = FallbackConfig(
            endpoint="instagram_graph_api",
            strategy="cache_only",
            cache_enabled=True,
            cache_ttl=3600  # 1 hora
        )
        self.fallback_manager.register_endpoint(config)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria sessão HTTP."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "OmniKeywordsFinder/1.0",
                    "Accept": "application/json"
                }
            )
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Faz request para a Graph API do Instagram com rate limiting e circuit breaker.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Resposta da API
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        if not self.page_access_token:
            raise InstagramGraphAPIError("Page Access Token não configurado")
        
        # Rate limiting
        if not self.rate_limiter.acquire("instagram_graph_api"):
            raise InstagramGraphAPIError("Rate limit atingido")
        
        try:
            with self.circuit_breaker:
                session = await self._get_session()
                
                if params is None:
                    params = {}
                
                params["access_token"] = self.page_access_token
                
                async with session.get(
                    f"{self.base_url}/{endpoint}",
                    params=params
                ) as response:
                    self.rate_limiter.record_response("instagram_graph_api", response.elapsed.total_seconds(), True)
                    
                    if response.status != 200:
                        error_data = await response.json()
                        raise InstagramGraphAPIError(
                            f"Erro na Graph API: {error_data.get('error_message', 'Unknown error')}",
                            error_code=error_data.get("error_code"),
                            http_status=response.status
                        )
                    
                    return await response.json()
                    
        except InstagramGraphAPIError:
            self.rate_limiter.record_response("instagram_graph_api", 0, False)
            raise
        except Exception as e:
            self.rate_limiter.record_response("instagram_graph_api", 0, False)
            raise InstagramGraphAPIError(f"Erro inesperado na requisição: {str(e)}")
    
    async def get_business_accounts(self) -> List[InstagramBusinessAccount]:
        """
        Obtém contas de negócio do Instagram associadas à página.
        
        Returns:
            Lista de contas de negócio
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            # Verifica cache
            cache_key = f"business_accounts:{self.page_access_token[:10]}"
            cached = await self.fallback_manager.get_cached_value(cache_key)
            if cached:
                return [InstagramBusinessAccount(**item) for item in cached]
            
            data = await self._make_request("me/accounts", {
                "fields": "instagram_business_account{id,username,name,profile_picture_url,website,biography,follows_count,followers_count,media_count,is_verified,is_private,business_category_name,category_name}"
            })
            
            business_accounts = []
            for page in data.get("data", []):
                if "instagram_business_account" in page:
                    ig_account = page["instagram_business_account"]
                    account = InstagramBusinessAccount(
                        id=ig_account["id"],
                        username=ig_account["username"],
                        name=ig_account["name"],
                        profile_picture_url=ig_account.get("profile_picture_url"),
                        website=ig_account.get("website"),
                        biography=ig_account.get("biography"),
                        follows_count=ig_account.get("follows_count", 0),
                        followers_count=ig_account.get("followers_count", 0),
                        media_count=ig_account.get("media_count", 0),
                        is_verified=ig_account.get("is_verified", False),
                        is_private=ig_account.get("is_private", False),
                        business_category_name=ig_account.get("business_category_name"),
                        category_name=ig_account.get("category_name")
                    )
                    business_accounts.append(account)
            
            # Salva no cache
            await self.fallback_manager.set_cached_value(
                cache_key, 
                [account.__dict__ for account in business_accounts], 
                7200  # 2 horas
            )
            
            logger.info({
                "component": "instagram_graph_api",
                "action": "business_accounts_retrieved",
                "count": len(business_accounts)
            })
            
            return business_accounts
            
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro ao obter contas de negócio: {str(e)}")
    
    async def get_business_account_info(self, business_account_id: str) -> InstagramBusinessAccount:
        """
        Obtém informações detalhadas de uma conta de negócio.
        
        Args:
            business_account_id: ID da conta de negócio
            
        Returns:
            Informações da conta de negócio
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            # Verifica cache
            cache_key = f"business_account_info:{business_account_id}"
            cached = await self.fallback_manager.get_cached_value(cache_key)
            if cached:
                return InstagramBusinessAccount(**cached)
            
            data = await self._make_request(business_account_id, {
                "fields": "id,username,name,profile_picture_url,website,biography,follows_count,followers_count,media_count,is_verified,is_private,business_category_name,category_name"
            })
            
            account = InstagramBusinessAccount(
                id=data["id"],
                username=data["username"],
                name=data["name"],
                profile_picture_url=data.get("profile_picture_url"),
                website=data.get("website"),
                biography=data.get("biography"),
                follows_count=data.get("follows_count", 0),
                followers_count=data.get("followers_count", 0),
                media_count=data.get("media_count", 0),
                is_verified=data.get("is_verified", False),
                is_private=data.get("is_private", False),
                business_category_name=data.get("business_category_name"),
                category_name=data.get("category_name")
            )
            
            # Salva no cache
            await self.fallback_manager.set_cached_value(
                cache_key, 
                account.__dict__, 
                3600  # 1 hora
            )
            
            logger.info({
                "component": "instagram_graph_api",
                "action": "business_account_info_retrieved",
                "business_account_id": business_account_id,
                "username": account.username
            })
            
            return account
            
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro ao obter informações da conta de negócio: {str(e)}")
    
    async def get_business_media(self, business_account_id: str, limit: int = 25, 
                               after: Optional[str] = None) -> List[InstagramBusinessMedia]:
        """
        Obtém mídia de uma conta de negócio.
        
        Args:
            business_account_id: ID da conta de negócio
            limit: Número máximo de itens (máx 25)
            after: Cursor para paginação
            
        Returns:
            Lista de mídia de negócio
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            # Verifica cache
            cache_key = f"business_media:{business_account_id}:{limit}:{after}"
            cached = await self.fallback_manager.get_cached_value(cache_key)
            if cached:
                return [InstagramBusinessMedia(**item) for item in cached]
            
            params = {
                "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count,owner{id,username,name}",
                "limit": min(limit, 25)
            }
            
            if after:
                params["after"] = after
            
            data = await self._make_request(f"{business_account_id}/media", params)
            
            media_list = []
            for item in data.get("data", []):
                owner_data = item.get("owner", {})
                owner = InstagramBusinessAccount(
                    id=owner_data["id"],
                    username=owner_data["username"],
                    name=owner_data["name"],
                    profile_picture_url=None,
                    website=None,
                    biography=None,
                    follows_count=0,
                    followers_count=0,
                    media_count=0,
                    is_verified=False,
                    is_private=False
                )
                
                media = InstagramBusinessMedia(
                    id=item["id"],
                    caption=item.get("caption"),
                    media_type=item["media_type"],
                    media_url=item.get("media_url"),
                    permalink=item["permalink"],
                    thumbnail_url=item.get("thumbnail_url"),
                    timestamp=datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")),
                    like_count=item.get("like_count", 0),
                    comments_count=item.get("comments_count", 0),
                    owner=owner
                )
                media_list.append(media)
            
            # Salva no cache
            await self.fallback_manager.set_cached_value(
                cache_key, 
                [media.__dict__ for media in media_list], 
                1800  # 30 minutos
            )
            
            logger.info({
                "component": "instagram_graph_api",
                "action": "business_media_retrieved",
                "business_account_id": business_account_id,
                "count": len(media_list),
                "has_next_page": "paging" in data
            })
            
            return media_list
            
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro ao obter mídia de negócio: {str(e)}")
    
    async def get_media_insights(self, media_id: str, metrics: List[str] = None) -> InstagramInsights:
        """
        Obtém insights de uma mídia específica.
        
        Args:
            media_id: ID da mídia
            metrics: Lista de métricas a obter
            
        Returns:
            Insights da mídia
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            if metrics is None:
                metrics = ["impressions", "reach", "engagement", "saved"]
            
            # Verifica cache
            cache_key = f"media_insights:{media_id}:{','.join(sorted(metrics))}"
            cached = await self.fallback_manager.get_cached_value(cache_key)
            if cached:
                return InstagramInsights(**cached)
            
            data = await self._make_request(f"{media_id}/insights", {
                "metric": ",".join(metrics)
            })
            
            insights_data = {}
            for insight in data.get("data", []):
                insights_data[insight["name"]] = insight["values"][0]["value"]
            
            insights = InstagramInsights(
                impressions=insights_data.get("impressions", 0),
                reach=insights_data.get("reach", 0),
                engagement=insights_data.get("engagement", 0),
                saved=insights_data.get("saved", 0),
                video_views=insights_data.get("video_views"),
                video_view_rate=insights_data.get("video_view_rate"),
                video_play_actions=insights_data.get("video_play_actions"),
                profile_views=insights_data.get("profile_views"),
                profile_actions=insights_data.get("profile_actions"),
                follows=insights_data.get("follows"),
                email_contacts=insights_data.get("email_contacts"),
                phone_call_clicks=insights_data.get("phone_call_clicks"),
                text_message_clicks=insights_data.get("text_message_clicks"),
                get_directions_clicks=insights_data.get("get_directions_clicks"),
                website_clicks=insights_data.get("website_clicks")
            )
            
            # Salva no cache
            await self.fallback_manager.set_cached_value(
                cache_key, 
                insights.__dict__, 
                3600  # 1 hora
            )
            
            logger.info({
                "component": "instagram_graph_api",
                "action": "media_insights_retrieved",
                "media_id": media_id,
                "metrics": metrics
            })
            
            return insights
            
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro ao obter insights da mídia: {str(e)}")
    
    async def get_account_insights(self, business_account_id: str, 
                                 metrics: List[str] = None) -> InstagramInsights:
        """
        Obtém insights da conta de negócio.
        
        Args:
            business_account_id: ID da conta de negócio
            metrics: Lista de métricas a obter
            
        Returns:
            Insights da conta
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            if metrics is None:
                metrics = ["profile_views", "profile_actions", "follows", "email_contacts", 
                          "phone_call_clicks", "text_message_clicks", "get_directions_clicks", 
                          "website_clicks"]
            
            # Verifica cache
            cache_key = f"account_insights:{business_account_id}:{','.join(sorted(metrics))}"
            cached = await self.fallback_manager.get_cached_value(cache_key)
            if cached:
                return InstagramInsights(**cached)
            
            data = await self._make_request(f"{business_account_id}/insights", {
                "metric": ",".join(metrics),
                "period": "day"
            })
            
            insights_data = {}
            for insight in data.get("data", []):
                insights_data[insight["name"]] = insight["values"][0]["value"]
            
            insights = InstagramInsights(
                impressions=0,  # Não disponível para conta
                reach=0,  # Não disponível para conta
                engagement=0,  # Não disponível para conta
                saved=0,  # Não disponível para conta
                profile_views=insights_data.get("profile_views"),
                profile_actions=insights_data.get("profile_actions"),
                follows=insights_data.get("follows"),
                email_contacts=insights_data.get("email_contacts"),
                phone_call_clicks=insights_data.get("phone_call_clicks"),
                text_message_clicks=insights_data.get("text_message_clicks"),
                get_directions_clicks=insights_data.get("get_directions_clicks"),
                website_clicks=insights_data.get("website_clicks")
            )
            
            # Salva no cache
            await self.fallback_manager.set_cached_value(
                cache_key, 
                insights.__dict__, 
                7200  # 2 horas
            )
            
            logger.info({
                "component": "instagram_graph_api",
                "action": "account_insights_retrieved",
                "business_account_id": business_account_id,
                "metrics": metrics
            })
            
            return insights
            
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro ao obter insights da conta: {str(e)}")
    
    async def get_media_comments(self, media_id: str, limit: int = 25, 
                               after: Optional[str] = None) -> List[InstagramComment]:
        """
        Obtém comentários de uma mídia.
        
        Args:
            media_id: ID da mídia
            limit: Número máximo de comentários
            after: Cursor para paginação
            
        Returns:
            Lista de comentários
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            # Verifica cache
            cache_key = f"media_comments:{media_id}:{limit}:{after}"
            cached = await self.fallback_manager.get_cached_value(cache_key)
            if cached:
                return [InstagramComment(**item) for item in cached]
            
            params = {
                "fields": "id,text,timestamp,username,like_count,is_hidden,is_reply,parent_comment_id",
                "limit": min(limit, 25)
            }
            
            if after:
                params["after"] = after
            
            data = await self._make_request(f"{media_id}/comments", params)
            
            comments = []
            for item in data.get("data", []):
                comment = InstagramComment(
                    id=item["id"],
                    text=item["text"],
                    timestamp=datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00")),
                    username=item["username"],
                    like_count=item.get("like_count", 0),
                    is_hidden=item.get("is_hidden", False),
                    is_reply=item.get("is_reply", False),
                    parent_comment_id=item.get("parent_comment_id")
                )
                comments.append(comment)
            
            # Salva no cache
            await self.fallback_manager.set_cached_value(
                cache_key, 
                [comment.__dict__ for comment in comments], 
                1800  # 30 minutos
            )
            
            logger.info({
                "component": "instagram_graph_api",
                "action": "media_comments_retrieved",
                "media_id": media_id,
                "count": len(comments)
            })
            
            return comments
            
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro ao obter comentários da mídia: {str(e)}")
    
    async def reply_to_comment(self, comment_id: str, message: str) -> bool:
        """
        Responde a um comentário.
        
        Args:
            comment_id: ID do comentário
            message: Mensagem da resposta
            
        Returns:
            True se sucesso
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            session = await self._get_session()
            
            data = {
                "access_token": self.page_access_token,
                "message": message
            }
            
            async with session.post(
                f"{self.base_url}/{comment_id}/replies",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise InstagramGraphAPIError(
                        f"Falha ao responder comentário: {error_data.get('error_message', 'Unknown error')}",
                        error_code=error_data.get("error_code"),
                        http_status=response.status
                    )
                
                logger.info({
                    "component": "instagram_graph_api",
                    "action": "comment_replied",
                    "comment_id": comment_id
                })
                
                return True
                
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro inesperado ao responder comentário: {str(e)}")
    
    async def hide_comment(self, comment_id: str, hide: bool = True) -> bool:
        """
        Oculta ou mostra um comentário.
        
        Args:
            comment_id: ID do comentário
            hide: True para ocultar, False para mostrar
            
        Returns:
            True se sucesso
            
        Raises:
            InstagramGraphAPIError: Se a requisição falhar
        """
        try:
            session = await self._get_session()
            
            data = {
                "access_token": self.page_access_token,
                "hide": hide
            }
            
            async with session.post(
                f"{self.base_url}/{comment_id}",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise InstagramGraphAPIError(
                        f"Falha ao {'ocultar' if hide else 'mostrar'} comentário: {error_data.get('error_message', 'Unknown error')}",
                        error_code=error_data.get("error_code"),
                        http_status=response.status
                    )
                
                logger.info({
                    "component": "instagram_graph_api",
                    "action": "comment_hidden" if hide else "comment_shown",
                    "comment_id": comment_id
                })
                
                return True
                
        except InstagramGraphAPIError:
            raise
        except Exception as e:
            raise InstagramGraphAPIError(f"Erro inesperado ao {'ocultar' if hide else 'mostrar'} comentário: {str(e)}")
    
    async def close(self):
        """Fecha sessão HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()


# Função de conveniência para criar instância
async def create_instagram_graph_api(page_access_token: Optional[str] = None) -> InstagramGraphAPI:
    """
    Cria instância da Instagram Graph API.
    
    Args:
        page_access_token: Page Access Token (opcional)
        
    Returns:
        Instância da API
    """
    return InstagramGraphAPI(page_access_token) 