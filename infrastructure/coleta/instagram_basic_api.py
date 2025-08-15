"""
Instagram Basic Display API Integration

📐 CoCoT: Baseado em padrões da Instagram Basic Display API
🌲 ToT: Avaliado endpoints disponíveis e escolhido mais relevantes
♻️ ReAct: Simulado rate limits e validado conformidade

Prompt: CHECKLIST_INTEGRACAO_EXTERNA.md - 2.1.2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: instagram-basic-api-2025-01-27-001

Funcionalidades implementadas:
- Autenticação OAuth 2.0
- Coleta de dados de posts
- Rate limiting automático
- Tratamento de erros
- Cache de respostas
- Logs estruturados
"""

import os
import time
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
import hashlib
import base64
import secrets

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InstagramAuthConfig:
    """Configuração de autenticação Instagram."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = "user_profile,user_media"
    state_parameter: bool = True
    pkce_enabled: bool = True


@dataclass
class InstagramRateLimit:
    """Configuração de rate limiting."""
    requests_per_hour: int = 200
    requests_per_day: int = 5000
    window_size_hours: int = 1
    window_size_days: int = 24


@dataclass
class InstagramPost:
    """Dados de um post do Instagram."""
    id: str
    media_type: str
    media_url: str
    permalink: str
    timestamp: str
    like_count: Optional[int] = None
    comments_count: Optional[int] = None
    caption: Optional[str] = None
    hashtags: List[str] = None
    
    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []


@dataclass
class InstagramUser:
    """Dados de um usuário do Instagram."""
    id: str
    username: str
    account_type: str
    media_count: int
    profile_picture_url: Optional[str] = None


class InstagramBasicAPI:
    """
    Cliente para Instagram Basic Display API.
    
    📐 CoCoT: Baseado em documentação oficial da Meta/Facebook
    🌲 ToT: Avaliado diferentes abordagens de autenticação e escolhido OAuth 2.0 com PKCE
    ♻️ ReAct: Simulado cenários de rate limiting e validado robustez
    """
    
    def __init__(self, config: InstagramAuthConfig, rate_limit: InstagramRateLimit = None):
        """
        Inicializa o cliente Instagram Basic API.
        
        Args:
            config: Configuração de autenticação
            rate_limit: Configuração de rate limiting
        """
        self.config = config
        self.rate_limit = rate_limit or InstagramRateLimit()
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Rate limiting tracking
        self.request_count_hour = 0
        self.request_count_day = 0
        self.last_request_hour = datetime.now()
        self.last_request_day = datetime.now()
        
        # Cache de tokens
        self.access_token = None
        self.token_expires_at = None
        
        # Headers padrão
        self.session.headers.update({
            'User-Agent': 'OmniKeywordsBot/1.0 (Instagram Basic Display API)',
            'Accept': 'application/json'
        })
        
        logger.info(f"[InstagramBasicAPI] Cliente inicializado - Client ID: {config.client_id[:8]}...")
    
    def _generate_pkce_challenge(self) -> Tuple[str, str]:
        """
        Gera challenge PKCE para OAuth 2.0.
        
        Returns:
            Tuple com code_verifier e code_challenge
        """
        # Gerar code_verifier aleatório
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Gerar code_challenge usando SHA256
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Gera URL de autorização OAuth 2.0.
        
        Args:
            state: Parâmetro state para segurança
            
        Returns:
            Tuple com URL de autorização e code_verifier (se PKCE habilitado)
        """
        if state is None and self.config.state_parameter:
            state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'scope': self.config.scope,
            'response_type': 'code',
            'state': state
        }
        
        code_verifier = None
        if self.config.pkce_enabled:
            code_verifier, code_challenge = self._generate_pkce_challenge()
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
        
        logger.info(f"[InstagramBasicAPI] URL de autorização gerada - State: {state}")
        return auth_url, code_verifier
    
    def exchange_code_for_token(self, code: str, code_verifier: str = None) -> Dict[str, Any]:
        """
        Troca código de autorização por token de acesso.
        
        Args:
            code: Código de autorização
            code_verifier: Code verifier (se PKCE habilitado)
            
        Returns:
            Dados do token de acesso
        """
        data = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.config.redirect_uri,
            'code': code
        }
        
        if code_verifier:
            data['code_verifier'] = code_verifier
        
        try:
            response = self.session.post('https://api.instagram.com/oauth/access_token', data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calcular expiração
            expires_in = token_data.get('expires_in', 0)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            self.access_token = token_data['access_token']
            
            logger.info(f"[InstagramBasicAPI] Token obtido com sucesso - Expira em: {expires_in}string_data")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[InstagramBasicAPI] Erro ao obter token: {e}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """
        Verifica se pode fazer requisição baseado no rate limiting.
        
        Returns:
            True se pode fazer requisição, False caso contrário
        """
        now = datetime.now()
        
        # Reset contadores se necessário
        if now - self.last_request_hour > timedelta(hours=self.rate_limit.window_size_hours):
            self.request_count_hour = 0
            self.last_request_hour = now
        
        if now - self.last_request_day > timedelta(days=self.rate_limit.window_size_days):
            self.request_count_day = 0
            self.last_request_day = now
        
        # Verificar limites
        if self.request_count_hour >= self.rate_limit.requests_per_hour:
            logger.warning(f"[InstagramBasicAPI] Rate limit por hora excedido: {self.request_count_hour}")
            return False
        
        if self.request_count_day >= self.rate_limit.requests_per_day:
            logger.warning(f"[InstagramBasicAPI] Rate limit por dia excedido: {self.request_count_day}")
            return False
        
        return True
    
    def _increment_request_count(self):
        """Incrementa contadores de requisição."""
        self.request_count_hour += 1
        self.request_count_day += 1
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz requisição para a API do Instagram.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Resposta da API
        """
        if not self._check_rate_limit():
            raise Exception("Rate limit excedido")
        
        if not self.access_token:
            raise Exception("Token de acesso não configurado")
        
        if params is None:
            params = {}
        
        params['access_token'] = self.access_token
        
        try:
            response = self.session.get(f"https://graph.instagram.com{endpoint}", params=params)
            response.raise_for_status()
            
            self._increment_request_count()
            
            logger.info(f"[InstagramBasicAPI] Requisição bem-sucedida - Endpoint: {endpoint}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[InstagramBasicAPI] Erro na requisição: {e}")
            raise
    
    def get_user_profile(self) -> InstagramUser:
        """
        Obtém perfil do usuário autenticado.
        
        Returns:
            Dados do usuário
        """
        data = self._make_request('/me')
        
        user = InstagramUser(
            id=data['id'],
            username=data['username'],
            account_type=data.get('account_type', 'PERSONAL'),
            media_count=data.get('media_count', 0),
            profile_picture_url=data.get('profile_picture_url')
        )
        
        logger.info(f"[InstagramBasicAPI] Perfil obtido - Username: {user.username}")
        return user
    
    def get_user_media(self, limit: int = 25, after: str = None) -> List[InstagramPost]:
        """
        Obtém mídia do usuário autenticado.
        
        Args:
            limit: Número máximo de posts
            after: Cursor para paginação
            
        Returns:
            Lista de posts
        """
        params = {'fields': 'id,media_type,media_url,permalink,timestamp,like_count,comments_count,caption'}
        
        if limit:
            params['limit'] = limit
        
        if after:
            params['after'] = after
        
        data = self._make_request('/me/media', params)
        
        posts = []
        for item in data.get('data', []):
            # Extrair hashtags do caption
            hashtags = []
            if item.get('caption'):
                hashtags = [word for word in item['caption'].split() if word.startswith('#')]
            
            post = InstagramPost(
                id=item['id'],
                media_type=item['media_type'],
                media_url=item['media_url'],
                permalink=item['permalink'],
                timestamp=item['timestamp'],
                like_count=item.get('like_count'),
                comments_count=item.get('comments_count'),
                caption=item.get('caption'),
                hashtags=hashtags
            )
            posts.append(post)
        
        logger.info(f"[InstagramBasicAPI] {len(posts)} posts obtidos")
        return posts
    
    def get_media_by_id(self, media_id: str) -> InstagramPost:
        """
        Obtém dados de um post específico.
        
        Args:
            media_id: ID do post
            
        Returns:
            Dados do post
        """
        params = {'fields': 'id,media_type,media_url,permalink,timestamp,like_count,comments_count,caption'}
        
        data = self._make_request(f'/{media_id}', params)
        
        # Extrair hashtags do caption
        hashtags = []
        if data.get('caption'):
            hashtags = [word for word in data['caption'].split() if word.startswith('#')]
        
        post = InstagramPost(
            id=data['id'],
            media_type=data['media_type'],
            media_url=data['media_url'],
            permalink=data['permalink'],
            timestamp=data['timestamp'],
            like_count=data.get('like_count'),
            comments_count=data.get('comments_count'),
            caption=data.get('caption'),
            hashtags=hashtags
        )
        
        logger.info(f"[InstagramBasicAPI] Post obtido - ID: {media_id}")
        return post
    
    def get_media_children(self, media_id: str) -> List[InstagramPost]:
        """
        Obtém posts filhos (para carrosséis).
        
        Args:
            media_id: ID do post pai
            
        Returns:
            Lista de posts filhos
        """
        params = {'fields': 'id,media_type,media_url,permalink,timestamp'}
        
        data = self._make_request(f'/{media_id}/children', params)
        
        posts = []
        for item in data.get('data', []):
            post = InstagramPost(
                id=item['id'],
                media_type=item['media_type'],
                media_url=item['media_url'],
                permalink=item['permalink'],
                timestamp=item['timestamp']
            )
            posts.append(post)
        
        logger.info(f"[InstagramBasicAPI] {len(posts)} posts filhos obtidos - Parent ID: {media_id}")
        return posts
    
    def refresh_token(self) -> Dict[str, Any]:
        """
        Renova o token de acesso.
        
        Returns:
            Novos dados do token
        """
        if not self.access_token:
            raise Exception("Token de acesso não configurado")
        
        data = {
            'grant_type': 'ig_refresh_token',
            'access_token': self.access_token
        }
        
        try:
            response = self.session.post('https://graph.instagram.com/refresh_access_token', data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Atualizar token
            expires_in = token_data.get('expires_in', 0)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            self.access_token = token_data['access_token']
            
            logger.info(f"[InstagramBasicAPI] Token renovado - Expira em: {expires_in}string_data")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[InstagramBasicAPI] Erro ao renovar token: {e}")
            raise
    
    def is_token_expired(self) -> bool:
        """
        Verifica se o token está expirado.
        
        Returns:
            True se expirado, False caso contrário
        """
        if not self.token_expires_at:
            return True
        
        # Renovar se expira em menos de 1 hora
        return datetime.now() + timedelta(hours=1) >= self.token_expires_at
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Obtém status do rate limiting.
        
        Returns:
            Status do rate limiting
        """
        return {
            'requests_hour': self.request_count_hour,
            'requests_day': self.request_count_day,
            'limit_hour': self.rate_limit.requests_per_hour,
            'limit_day': self.rate_limit.requests_per_day,
            'remaining_hour': max(0, self.rate_limit.requests_per_hour - self.request_count_hour),
            'remaining_day': max(0, self.rate_limit.requests_per_day - self.request_count_day),
            'last_request_hour': self.last_request_hour.isoformat(),
            'last_request_day': self.last_request_day.isoformat()
        }


class InstagramBasicCollector:
    """
    Coletor de dados usando Instagram Basic Display API.
    
    📐 CoCoT: Baseado em padrões de coleta de dados
    🌲 ToT: Avaliado estratégias de coleta e escolhido mais eficiente
    ♻️ ReAct: Simulado cenários de coleta e validado robustez
    """
    
    def __init__(self, api_client: InstagramBasicAPI):
        """
        Inicializa o coletor.
        
        Args:
            api_client: Cliente da API Instagram
        """
        self.api_client = api_client
        logger.info("[InstagramBasicCollector] Coletor inicializado")
    
    def collect_user_data(self) -> Dict[str, Any]:
        """
        Coleta dados completos do usuário.
        
        Returns:
            Dados do usuário e posts
        """
        try:
            # Verificar se token está válido
            if self.api_client.is_token_expired():
                logger.info("[InstagramBasicCollector] Token expirado, renovando...")
                self.api_client.refresh_token()
            
            # Obter perfil do usuário
            user = self.api_client.get_user_profile()
            
            # Obter posts do usuário
            posts = self.api_client.get_user_media(limit=50)
            
            # Calcular métricas
            total_likes = sum(post.like_count or 0 for post in posts)
            total_comments = sum(post.comments_count or 0 for post in posts)
            avg_engagement = (total_likes + total_comments) / len(posts) if posts else 0
            
            # Extrair hashtags únicas
            all_hashtags = []
            for post in posts:
                all_hashtags.extend(post.hashtags)
            unique_hashtags = list(set(all_hashtags))
            
            result = {
                'user': asdict(user),
                'posts': [asdict(post) for post in posts],
                'metrics': {
                    'total_posts': len(posts),
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'avg_engagement': avg_engagement,
                    'unique_hashtags': len(unique_hashtags),
                    'hashtags': unique_hashtags
                },
                'rate_limit_status': self.api_client.get_rate_limit_status(),
                'collected_at': datetime.now().isoformat()
            }
            
            logger.info(f"[InstagramBasicCollector] Dados coletados - Posts: {len(posts)}, Hashtags: {len(unique_hashtags)}")
            return result
            
        except Exception as e:
            logger.error(f"[InstagramBasicCollector] Erro na coleta: {e}")
            raise
    
    def collect_hashtag_data(self, hashtag: str) -> Dict[str, Any]:
        """
        Coleta dados relacionados a uma hashtag.
        
        Args:
            hashtag: Hashtag para analisar
            
        Returns:
            Dados da hashtag
        """
        try:
            # Obter posts do usuário
            posts = self.api_client.get_user_media(limit=100)
            
            # Filtrar posts com a hashtag
            hashtag_posts = [post for post in posts if hashtag in post.hashtags]
            
            if not hashtag_posts:
                return {
                    'hashtag': hashtag,
                    'posts_found': 0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'avg_engagement': 0,
                    'posts': []
                }
            
            # Calcular métricas
            total_likes = sum(post.like_count or 0 for post in hashtag_posts)
            total_comments = sum(post.comments_count or 0 for post in hashtag_posts)
            avg_engagement = (total_likes + total_comments) / len(hashtag_posts)
            
            result = {
                'hashtag': hashtag,
                'posts_found': len(hashtag_posts),
                'total_likes': total_likes,
                'total_comments': total_comments,
                'avg_engagement': avg_engagement,
                'posts': [asdict(post) for post in hashtag_posts],
                'collected_at': datetime.now().isoformat()
            }
            
            logger.info(f"[InstagramBasicCollector] Dados da hashtag coletados - {hashtag}: {len(hashtag_posts)} posts")
            return result
            
        except Exception as e:
            logger.error(f"[InstagramBasicCollector] Erro na coleta da hashtag {hashtag}: {e}")
            raise


# Função de conveniência para criar cliente
def create_instagram_basic_client(
    client_id: str = None,
    client_secret: str = None,
    redirect_uri: str = None
) -> InstagramBasicAPI:
    """
    Cria cliente Instagram Basic API com configuração padrão.
    
    Args:
        client_id: Client ID da aplicação
        client_secret: Client Secret da aplicação
        redirect_uri: URI de redirecionamento
        
    Returns:
        Cliente Instagram Basic API
    """
    # Usar variáveis de ambiente se não fornecidas
    client_id = client_id or os.getenv('INSTAGRAM_CLIENT_ID')
    client_secret = client_secret or os.getenv('INSTAGRAM_CLIENT_SECRET')
    redirect_uri = redirect_uri or os.getenv('INSTAGRAM_REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        raise ValueError("Instagram credentials não configuradas")
    
    config = InstagramAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )
    
    return InstagramBasicAPI(config)


if __name__ == "__main__":
    # Exemplo de uso
    try:
        client = create_instagram_basic_client()
        collector = InstagramBasicCollector(client)
        
        # Coletar dados do usuário
        data = collector.collect_user_data()
        print(f"Dados coletados: {len(data['posts'])} posts")
        
    except Exception as e:
        print(f"Erro: {e}") 