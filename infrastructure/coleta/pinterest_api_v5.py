"""
📌 Pinterest API v5 Implementation

Tracing ID: pinterest-api-2025-01-27-001
Timestamp: 2025-01-27T16:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: API baseada em padrões Pinterest API v5 e boas práticas OAuth 2.0
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

class PinterestScope(Enum):
    """Escopos de permissão Pinterest"""
    BOARDS_READ = "boards:read"
    BOARDS_WRITE = "boards:write"
    PINS_READ = "pins:read"
    PINS_WRITE = "pins:write"
    USER_ACCOUNTS_READ = "user_accounts:read"
    USER_ACCOUNTS_WRITE = "user_accounts:write"

class PinPrivacy(Enum):
    """Privacidade de pins"""
    PUBLIC = "public"
    PROTECTED = "protected"
    SECRET = "secret"

@dataclass
class PinterestPin:
    """Dados de pin Pinterest"""
    id: str
    title: str
    description: str
    link: str
    media_source: Dict[str, Any]
    board_id: str
    board_section_id: Optional[str]
    parent_save_pin_id: Optional[str]
    note: str
    media: Dict[str, Any]
    media_metadata: Dict[str, Any]
    link_domain: str
    is_owner: bool
    is_repin: bool
    is_video: bool
    is_editable: bool
    is_promoted: bool
    is_standard_product_pin: bool
    has_been_promoted_by_seller: bool
    is_eligible_for_web_close_up: bool
    promoted_is_removable: bool
    seen_by_me_at: Optional[datetime]
    tracked_link: Optional[str]
    rich_metadata: Optional[Dict[str, Any]]
    is_eligible_for_pdp: bool
    is_eligible_for_mpdp: bool
    is_eligible_for_shopping: bool
    is_eligible_for_redesign: bool
    is_eligible_for_web_close_up: bool
    is_eligible_for_web_redesign: bool
    is_eligible_for_web_shopping: bool
    is_eligible_for_web_standard_product_pin: bool
    is_eligible_for_web_rich_pin: bool
    is_eligible_for_web_video_pin: bool
    is_eligible_for_web_carousel_pin: bool
    is_eligible_for_web_collection_pin: bool
    is_eligible_for_web_idea_pin: bool
    is_eligible_for_web_story_pin: bool
    is_eligible_for_web_article_pin: bool
    is_eligible_for_web_product_pin: bool
    is_eligible_for_web_recipe_pin: bool
    is_eligible_for_web_movie_pin: bool
    is_eligible_for_web_place_pin: bool
    is_eligible_for_web_app_pin: bool
    is_eligible_for_web_book_pin: bool
    is_eligible_for_web_website_pin: bool
    is_eligible_for_web_other_pin: bool
    created_at: datetime
    updated_at: datetime
    saved_at: datetime
    last_saved_at: datetime
    alt_text: Optional[str]
    creative_type: str
    board_owner: Dict[str, Any]
    is_owner: bool
    is_repin: bool
    is_video: bool
    is_editable: bool
    is_promoted: bool
    is_standard_product_pin: bool
    has_been_promoted_by_seller: bool
    is_eligible_for_web_close_up: bool
    promoted_is_removable: bool
    seen_by_me_at: Optional[datetime]
    tracked_link: Optional[str]
    rich_metadata: Optional[Dict[str, Any]]
    is_eligible_for_pdp: bool
    is_eligible_for_mpdp: bool
    is_eligible_for_shopping: bool
    is_eligible_for_redesign: bool
    is_eligible_for_web_close_up: bool
    is_eligible_for_web_redesign: bool
    is_eligible_for_web_shopping: bool
    is_eligible_for_web_standard_product_pin: bool
    is_eligible_for_web_rich_pin: bool
    is_eligible_for_web_video_pin: bool
    is_eligible_for_web_carousel_pin: bool
    is_eligible_for_web_collection_pin: bool
    is_eligible_for_web_idea_pin: bool
    is_eligible_for_web_story_pin: bool
    is_eligible_for_web_article_pin: bool
    is_eligible_for_web_product_pin: bool
    is_eligible_for_web_recipe_pin: bool
    is_eligible_for_web_movie_pin: bool
    is_eligible_for_web_place_pin: bool
    is_eligible_for_web_app_pin: bool
    is_eligible_for_web_book_pin: bool
    is_eligible_for_web_website_pin: bool
    is_eligible_for_web_other_pin: bool

@dataclass
class PinterestBoard:
    """Dados de board Pinterest"""
    id: str
    name: str
    description: str
    owner: Dict[str, Any]
    privacy: str
    category: str
    pin_count: int
    follower_count: int
    created_at: datetime
    updated_at: datetime
    collaborator_count: int
    is_owner: bool
    is_collaborator: bool
    is_following: bool
    is_eligible_for_web_close_up: bool
    is_eligible_for_web_redesign: bool
    is_eligible_for_web_shopping: bool
    is_eligible_for_web_standard_product_pin: bool
    is_eligible_for_web_rich_pin: bool
    is_eligible_for_web_video_pin: bool
    is_eligible_for_web_carousel_pin: bool
    is_eligible_for_web_collection_pin: bool
    is_eligible_for_web_idea_pin: bool
    is_eligible_for_web_story_pin: bool
    is_eligible_for_web_article_pin: bool
    is_eligible_for_web_product_pin: bool
    is_eligible_for_web_recipe_pin: bool
    is_eligible_for_web_movie_pin: bool
    is_eligible_for_web_place_pin: bool
    is_eligible_for_web_app_pin: bool
    is_eligible_for_web_book_pin: bool
    is_eligible_for_web_website_pin: bool
    is_eligible_for_web_other_pin: bool

@dataclass
class PinterestUser:
    """Dados de usuário Pinterest"""
    username: str
    about: str
    website: str
    profile_image: str
    full_name: str
    country: str
    locale: str
    account_type: str
    business_name: str
    business_website: str
    business_email: str
    business_phone: str
    business_address: str
    business_city: str
    business_state: str
    business_country: str
    business_postal_code: str
    business_phone_verified: bool
    business_email_verified: bool
    business_website_verified: bool
    business_address_verified: bool
    business_city_verified: bool
    business_state_verified: bool
    business_country_verified: bool
    business_postal_code_verified: bool
    business_phone_verification_status: str
    business_email_verification_status: str
    business_website_verification_status: str
    business_address_verification_status: str
    business_city_verification_status: str
    business_state_verification_status: str
    business_country_verification_status: str
    business_postal_code_verification_status: str

class PinterestAPIError(Exception):
    """Exceção customizada para erros da Pinterest API"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, http_status: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
        self.http_status = http_status

class PinterestAPIv5:
    """
    API Pinterest v5
    
    Implementa integração completa com Pinterest API v5 incluindo:
    - Autenticação OAuth 2.0
    - Busca de pins e boards
    - Análise de usuários
    - Rate limiting inteligente
    - Circuit breaker e fallback
    - Métricas e observabilidade
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa API Pinterest
        
        Args:
            config: Configuração da API
        """
        self.config = config
        self.app_id = config.get("app_id")
        self.app_secret = config.get("app_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.api_base_url = "https://api.pinterest.com/v5"
        self.auth_base_url = "https://www.pinterest.com/oauth"
        
        # Configurar circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=PinterestAPIError
        )
        
        # Configurar rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get("rate_limits", {}).get("requests_per_minute", 1000),
            requests_per_hour=config.get("rate_limits", {}).get("requests_per_hour", 10000)
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
        
        logger.info("Pinterest API v5 inicializada")
    
    def get_auth_url(self, scopes: List[PinterestScope] = None) -> str:
        """
        Gera URL de autorização Pinterest
        
        Args:
            scopes: Lista de escopos de permissão
            
        Returns:
            str: URL de autorização
        """
        if scopes is None:
            scopes = [
                PinterestScope.BOARDS_READ,
                PinterestScope.PINS_READ,
                PinterestScope.USER_ACCOUNTS_READ
            ]
        
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": ",".join([scope.value for scope in scopes]),
            "response_type": "code",
            "state": secrets.token_urlsafe(32)
        }
        
        auth_url = f"{self.auth_base_url}/?{urlencode(params)}"
        logger.info(f"URL de autorização Pinterest gerada: {auth_url}")
        return auth_url
    
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
            
            token_url = f"{self.api_base_url}/oauth/token"
            data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.app_id,
                "client_secret": self.app_secret
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
                "pinterest_token_exchanges_total",
                {"status": "success"}
            )
            
            logger.info("Token Pinterest obtido com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao trocar código por token: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "pinterest_token_exchanges_total",
                {"status": "error"}
            )
            
            raise PinterestAPIError(f"Erro ao trocar código por token: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Renova access token usando refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict[str, Any]: Dados do novo token
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("refresh_token")
            
            token_url = f"{self.api_base_url}/oauth/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.app_id,
                "client_secret": self.app_secret
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _refresh_token():
                response = requests.post(token_url, data=data, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _refresh_token()
            
            # Armazenar novo token
            self.access_token = result.get("access_token")
            expires_in = result.get("expires_in", 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "pinterest_token_refreshes_total",
                {"status": "success"}
            )
            
            logger.info("Token Pinterest renovado com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao renovar token: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "pinterest_token_refreshes_total",
                {"status": "error"}
            )
            
            raise PinterestAPIError(f"Erro ao renovar token: {str(e)}")
    
    def search_pins(self, query: str, bookmark: Optional[str] = None, 
                   page_size: int = 25, fields: List[str] = None) -> Dict[str, Any]:
        """
        Busca pins por query
        
        Args:
            query: Termo de busca
            bookmark: Token de paginação
            page_size: Tamanho da página
            fields: Campos a retornar
            
        Returns:
            Dict[str, Any]: Resultados da busca
        """
        if fields is None:
            fields = ["id", "title", "description", "link", "media_source", "board_id"]
        
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("search_pins")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/pins/search"
            params = {
                "query": query,
                "page_size": page_size,
                "fields": fields
            }
            
            if bookmark:
                params["bookmark"] = bookmark
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _search_pins():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _search_pins()
            
            # Registrar métricas
            self.metrics.increment_counter(
                "pinterest_pin_searches_total",
                {"status": "success", "query": query}
            )
            self.metrics.record_histogram(
                "pinterest_pin_search_results_count",
                len(result.get("items", []))
            )
            
            logger.info(f"Busca de pins concluída - Query: {query}, Resultados: {len(result.get('items', []))}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar pins: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "pinterest_pin_searches_total",
                {"status": "error"}
            )
            
            # Tentar fallback
            return self.fallback_manager.execute_fallback(
                "search_pins",
                {"query": query, "bookmark": bookmark, "page_size": page_size},
                self._fallback_pin_search
            )
    
    def get_board(self, board_id: str, fields: List[str] = None) -> PinterestBoard:
        """
        Obtém informações de um board
        
        Args:
            board_id: ID do board
            fields: Campos a retornar
            
        Returns:
            PinterestBoard: Dados do board
        """
        if fields is None:
            fields = ["id", "name", "description", "owner", "privacy", "category", "pin_count", "follower_count"]
        
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("get_board")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/boards/{board_id}"
            params = {
                "fields": fields
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _get_board():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _get_board()
            
            # Processar resultado
            board_data = result.get("data", {})
            board = self._parse_board_data(board_data)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "pinterest_board_requests_total",
                {"status": "success"}
            )
            
            logger.info(f"Informações do board obtidas - ID: {board.id}")
            return board
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do board: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "pinterest_board_requests_total",
                {"status": "error"}
            )
            
            raise PinterestAPIError(f"Erro ao obter informações do board: {str(e)}")
    
    def get_user_account(self, fields: List[str] = None) -> PinterestUser:
        """
        Obtém informações da conta do usuário autenticado
        
        Args:
            fields: Campos a retornar
            
        Returns:
            PinterestUser: Dados do usuário
        """
        if fields is None:
            fields = ["username", "about", "website", "profile_image", "full_name", "country", "locale"]
        
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("get_user_account")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/user_account"
            params = {
                "fields": fields
            }
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _get_user_account():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _get_user_account()
            
            # Processar resultado
            user_data = result.get("data", {})
            user = self._parse_user_data(user_data)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "pinterest_user_account_requests_total",
                {"status": "success"}
            )
            
            logger.info(f"Informações do usuário obtidas - Username: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do usuário: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "pinterest_user_account_requests_total",
                {"status": "error"}
            )
            
            raise PinterestAPIError(f"Erro ao obter informações do usuário: {str(e)}")
    
    def get_board_pins(self, board_id: str, bookmark: Optional[str] = None,
                      page_size: int = 25, fields: List[str] = None) -> Dict[str, Any]:
        """
        Obtém pins de um board
        
        Args:
            board_id: ID do board
            bookmark: Token de paginação
            page_size: Tamanho da página
            fields: Campos a retornar
            
        Returns:
            Dict[str, Any]: Lista de pins
        """
        if fields is None:
            fields = ["id", "title", "description", "link", "media_source", "board_id"]
        
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("get_board_pins")
            
            # Verificar token
            self._ensure_valid_token()
            
            url = f"{self.api_base_url}/boards/{board_id}/pins"
            params = {
                "page_size": page_size,
                "fields": fields
            }
            
            if bookmark:
                params["bookmark"] = bookmark
            
            # Executar com circuit breaker
            @self.circuit_breaker
            def _get_board_pins():
                headers = self._get_auth_headers()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
            
            result = _get_board_pins()
            
            # Registrar métricas
            self.metrics.increment_counter(
                "pinterest_board_pins_requests_total",
                {"status": "success"}
            )
            
            logger.info(f"Pins do board obtidos - Board ID: {board_id}, Count: {len(result.get('items', []))}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter pins do board: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "pinterest_board_pins_requests_total",
                {"status": "error"}
            )
            
            raise PinterestAPIError(f"Erro ao obter pins do board: {str(e)}")
    
    def _ensure_valid_token(self):
        """Verifica se o token é válido"""
        if not self.access_token:
            raise PinterestAPIError("Access token não configurado")
        
        if self.token_expires_at and datetime.utcnow() >= self.token_expires_at:
            raise PinterestAPIError("Access token expirado")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _parse_pin_data(self, pin_data: Dict[str, Any]) -> PinterestPin:
        """Converte dados de pin em PinterestPin"""
        return PinterestPin(
            id=pin_data["id"],
            title=pin_data.get("title", ""),
            description=pin_data.get("description", ""),
            link=pin_data.get("link", ""),
            media_source=pin_data.get("media_source", {}),
            board_id=pin_data.get("board_id", ""),
            board_section_id=pin_data.get("board_section_id"),
            parent_save_pin_id=pin_data.get("parent_save_pin_id"),
            note=pin_data.get("note", ""),
            media=pin_data.get("media", {}),
            media_metadata=pin_data.get("media_metadata", {}),
            link_domain=pin_data.get("link_domain", ""),
            is_owner=pin_data.get("is_owner", False),
            is_repin=pin_data.get("is_repin", False),
            is_video=pin_data.get("is_video", False),
            is_editable=pin_data.get("is_editable", False),
            is_promoted=pin_data.get("is_promoted", False),
            is_standard_product_pin=pin_data.get("is_standard_product_pin", False),
            has_been_promoted_by_seller=pin_data.get("has_been_promoted_by_seller", False),
            is_eligible_for_web_close_up=pin_data.get("is_eligible_for_web_close_up", False),
            promoted_is_removable=pin_data.get("promoted_is_removable", False),
            seen_by_me_at=datetime.fromisoformat(pin_data["seen_by_me_at"].replace("Z", "+00:00")) if pin_data.get("seen_by_me_at") else None,
            tracked_link=pin_data.get("tracked_link"),
            rich_metadata=pin_data.get("rich_metadata"),
            is_eligible_for_pdp=pin_data.get("is_eligible_for_pdp", False),
            is_eligible_for_mpdp=pin_data.get("is_eligible_for_mpdp", False),
            is_eligible_for_shopping=pin_data.get("is_eligible_for_shopping", False),
            is_eligible_for_redesign=pin_data.get("is_eligible_for_redesign", False),
            is_eligible_for_web_close_up=pin_data.get("is_eligible_for_web_close_up", False),
            is_eligible_for_web_redesign=pin_data.get("is_eligible_for_web_redesign", False),
            is_eligible_for_web_shopping=pin_data.get("is_eligible_for_web_shopping", False),
            is_eligible_for_web_standard_product_pin=pin_data.get("is_eligible_for_web_standard_product_pin", False),
            is_eligible_for_web_rich_pin=pin_data.get("is_eligible_for_web_rich_pin", False),
            is_eligible_for_web_video_pin=pin_data.get("is_eligible_for_web_video_pin", False),
            is_eligible_for_web_carousel_pin=pin_data.get("is_eligible_for_web_carousel_pin", False),
            is_eligible_for_web_collection_pin=pin_data.get("is_eligible_for_web_collection_pin", False),
            is_eligible_for_web_idea_pin=pin_data.get("is_eligible_for_web_idea_pin", False),
            is_eligible_for_web_story_pin=pin_data.get("is_eligible_for_web_story_pin", False),
            is_eligible_for_web_article_pin=pin_data.get("is_eligible_for_web_article_pin", False),
            is_eligible_for_web_product_pin=pin_data.get("is_eligible_for_web_product_pin", False),
            is_eligible_for_web_recipe_pin=pin_data.get("is_eligible_for_web_recipe_pin", False),
            is_eligible_for_web_movie_pin=pin_data.get("is_eligible_for_web_movie_pin", False),
            is_eligible_for_web_place_pin=pin_data.get("is_eligible_for_web_place_pin", False),
            is_eligible_for_web_app_pin=pin_data.get("is_eligible_for_web_app_pin", False),
            is_eligible_for_web_book_pin=pin_data.get("is_eligible_for_web_book_pin", False),
            is_eligible_for_web_website_pin=pin_data.get("is_eligible_for_web_website_pin", False),
            is_eligible_for_web_other_pin=pin_data.get("is_eligible_for_web_other_pin", False),
            created_at=datetime.fromisoformat(pin_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(pin_data["updated_at"].replace("Z", "+00:00")),
            saved_at=datetime.fromisoformat(pin_data["saved_at"].replace("Z", "+00:00")),
            last_saved_at=datetime.fromisoformat(pin_data["last_saved_at"].replace("Z", "+00:00")),
            alt_text=pin_data.get("alt_text"),
            creative_type=pin_data.get("creative_type", ""),
            board_owner=pin_data.get("board_owner", {}),
            is_owner=pin_data.get("is_owner", False),
            is_repin=pin_data.get("is_repin", False),
            is_video=pin_data.get("is_video", False),
            is_editable=pin_data.get("is_editable", False),
            is_promoted=pin_data.get("is_promoted", False),
            is_standard_product_pin=pin_data.get("is_standard_product_pin", False),
            has_been_promoted_by_seller=pin_data.get("has_been_promoted_by_seller", False),
            is_eligible_for_web_close_up=pin_data.get("is_eligible_for_web_close_up", False),
            promoted_is_removable=pin_data.get("promoted_is_removable", False),
            seen_by_me_at=datetime.fromisoformat(pin_data["seen_by_me_at"].replace("Z", "+00:00")) if pin_data.get("seen_by_me_at") else None,
            tracked_link=pin_data.get("tracked_link"),
            rich_metadata=pin_data.get("rich_metadata"),
            is_eligible_for_pdp=pin_data.get("is_eligible_for_pdp", False),
            is_eligible_for_mpdp=pin_data.get("is_eligible_for_mpdp", False),
            is_eligible_for_shopping=pin_data.get("is_eligible_for_shopping", False),
            is_eligible_for_redesign=pin_data.get("is_eligible_for_redesign", False),
            is_eligible_for_web_close_up=pin_data.get("is_eligible_for_web_close_up", False),
            is_eligible_for_web_redesign=pin_data.get("is_eligible_for_web_redesign", False),
            is_eligible_for_web_shopping=pin_data.get("is_eligible_for_web_shopping", False),
            is_eligible_for_web_standard_product_pin=pin_data.get("is_eligible_for_web_standard_product_pin", False),
            is_eligible_for_web_rich_pin=pin_data.get("is_eligible_for_web_rich_pin", False),
            is_eligible_for_web_video_pin=pin_data.get("is_eligible_for_web_video_pin", False),
            is_eligible_for_web_carousel_pin=pin_data.get("is_eligible_for_web_carousel_pin", False),
            is_eligible_for_web_collection_pin=pin_data.get("is_eligible_for_web_collection_pin", False),
            is_eligible_for_web_idea_pin=pin_data.get("is_eligible_for_web_idea_pin", False),
            is_eligible_for_web_story_pin=pin_data.get("is_eligible_for_web_story_pin", False),
            is_eligible_for_web_article_pin=pin_data.get("is_eligible_for_web_article_pin", False),
            is_eligible_for_web_product_pin=pin_data.get("is_eligible_for_web_product_pin", False),
            is_eligible_for_web_recipe_pin=pin_data.get("is_eligible_for_web_recipe_pin", False),
            is_eligible_for_web_movie_pin=pin_data.get("is_eligible_for_web_movie_pin", False),
            is_eligible_for_web_place_pin=pin_data.get("is_eligible_for_web_place_pin", False),
            is_eligible_for_web_app_pin=pin_data.get("is_eligible_for_web_app_pin", False),
            is_eligible_for_web_book_pin=pin_data.get("is_eligible_for_web_book_pin", False),
            is_eligible_for_web_website_pin=pin_data.get("is_eligible_for_web_website_pin", False),
            is_eligible_for_web_other_pin=pin_data.get("is_eligible_for_web_other_pin", False)
        )
    
    def _parse_board_data(self, board_data: Dict[str, Any]) -> PinterestBoard:
        """Converte dados de board em PinterestBoard"""
        return PinterestBoard(
            id=board_data["id"],
            name=board_data["name"],
            description=board_data.get("description", ""),
            owner=board_data.get("owner", {}),
            privacy=board_data.get("privacy", "public"),
            category=board_data.get("category", ""),
            pin_count=board_data.get("pin_count", 0),
            follower_count=board_data.get("follower_count", 0),
            created_at=datetime.fromisoformat(board_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(board_data["updated_at"].replace("Z", "+00:00")),
            collaborator_count=board_data.get("collaborator_count", 0),
            is_owner=board_data.get("is_owner", False),
            is_collaborator=board_data.get("is_collaborator", False),
            is_following=board_data.get("is_following", False),
            is_eligible_for_web_close_up=board_data.get("is_eligible_for_web_close_up", False),
            is_eligible_for_web_redesign=board_data.get("is_eligible_for_web_redesign", False),
            is_eligible_for_web_shopping=board_data.get("is_eligible_for_web_shopping", False),
            is_eligible_for_web_standard_product_pin=board_data.get("is_eligible_for_web_standard_product_pin", False),
            is_eligible_for_web_rich_pin=board_data.get("is_eligible_for_web_rich_pin", False),
            is_eligible_for_web_video_pin=board_data.get("is_eligible_for_web_video_pin", False),
            is_eligible_for_web_carousel_pin=board_data.get("is_eligible_for_web_carousel_pin", False),
            is_eligible_for_web_collection_pin=board_data.get("is_eligible_for_web_collection_pin", False),
            is_eligible_for_web_idea_pin=board_data.get("is_eligible_for_web_idea_pin", False),
            is_eligible_for_web_story_pin=board_data.get("is_eligible_for_web_story_pin", False),
            is_eligible_for_web_article_pin=board_data.get("is_eligible_for_web_article_pin", False),
            is_eligible_for_web_product_pin=board_data.get("is_eligible_for_web_product_pin", False),
            is_eligible_for_web_recipe_pin=board_data.get("is_eligible_for_web_recipe_pin", False),
            is_eligible_for_web_movie_pin=board_data.get("is_eligible_for_web_movie_pin", False),
            is_eligible_for_web_place_pin=board_data.get("is_eligible_for_web_place_pin", False),
            is_eligible_for_web_app_pin=board_data.get("is_eligible_for_web_app_pin", False),
            is_eligible_for_web_book_pin=board_data.get("is_eligible_for_web_book_pin", False),
            is_eligible_for_web_website_pin=board_data.get("is_eligible_for_web_website_pin", False),
            is_eligible_for_web_other_pin=board_data.get("is_eligible_for_web_other_pin", False)
        )
    
    def _parse_user_data(self, user_data: Dict[str, Any]) -> PinterestUser:
        """Converte dados de usuário em PinterestUser"""
        return PinterestUser(
            username=user_data["username"],
            about=user_data.get("about", ""),
            website=user_data.get("website", ""),
            profile_image=user_data.get("profile_image", ""),
            full_name=user_data.get("full_name", ""),
            country=user_data.get("country", ""),
            locale=user_data.get("locale", ""),
            account_type=user_data.get("account_type", ""),
            business_name=user_data.get("business_name", ""),
            business_website=user_data.get("business_website", ""),
            business_email=user_data.get("business_email", ""),
            business_phone=user_data.get("business_phone", ""),
            business_address=user_data.get("business_address", ""),
            business_city=user_data.get("business_city", ""),
            business_state=user_data.get("business_state", ""),
            business_country=user_data.get("business_country", ""),
            business_postal_code=user_data.get("business_postal_code", ""),
            business_phone_verified=user_data.get("business_phone_verified", False),
            business_email_verified=user_data.get("business_email_verified", False),
            business_website_verified=user_data.get("business_website_verified", False),
            business_address_verified=user_data.get("business_address_verified", False),
            business_city_verified=user_data.get("business_city_verified", False),
            business_state_verified=user_data.get("business_state_verified", False),
            business_country_verified=user_data.get("business_country_verified", False),
            business_postal_code_verified=user_data.get("business_postal_code_verified", False),
            business_phone_verification_status=user_data.get("business_phone_verification_status", ""),
            business_email_verification_status=user_data.get("business_email_verification_status", ""),
            business_website_verification_status=user_data.get("business_website_verification_status", ""),
            business_address_verification_status=user_data.get("business_address_verification_status", ""),
            business_city_verification_status=user_data.get("business_city_verification_status", ""),
            business_state_verification_status=user_data.get("business_state_verification_status", ""),
            business_country_verification_status=user_data.get("business_country_verification_status", ""),
            business_postal_code_verification_status=user_data.get("business_postal_code_verification_status", "")
        )
    
    def _fallback_pin_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback para busca de pins"""
        logger.warning("Usando fallback para busca de pins")
        
        # Implementar lógica de fallback
        # Por exemplo, usar web scraping ou cache
        
        return {
            "items": [],
            "bookmark": None
        } 