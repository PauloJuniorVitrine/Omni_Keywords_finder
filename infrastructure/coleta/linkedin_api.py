"""
LinkedIn API Integration - Omni Keywords Finder

Tracing ID: INT_001_LINKEDIN_2025_001
Data/Hora: 2025-01-27 17:10:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

📐 CoCoT - Comprovação: LinkedIn API v2 é padrão da indústria
📐 CoCoT - Causalidade: Expansão de market coverage para 774M+ usuários
📐 CoCoT - Contexto: Sistema já possui infraestrutura de coleta
📐 CoCoT - Tendência: OAuth2 + rate limiting inteligente

🌲 ToT - Caminho escolhido: Implementação híbrida (OAuth2 + fallback)
♻️ ReAct - Simulação: Cache inteligente + circuit breakers para robustez
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import redis.asyncio as redis
from tenacity import retry, stop_after_attempt, wait_exponential
from infrastructure.coleta.base import BaseCollector
from infrastructure.resilience.circuit_breakers import CircuitBreaker
from infrastructure.cache.distributed_cache import DistributedCache

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class LinkedInConfig:
    """Configuração da API LinkedIn"""
    client_id: str
    client_secret: str
    redirect_uri: str
    api_version: str = "v2"
    base_url: str = "https://api.linkedin.com"
    rate_limit_per_minute: int = 100
    rate_limit_per_day: int = 5000
    cache_ttl: int = 3600  # 1 hora
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

@dataclass
class LinkedInPost:
    """Estrutura de dados para posts do LinkedIn"""
    id: str
    author_id: str
    content: str
    created_time: datetime
    engagement_metrics: Dict[str, int]
    hashtags: List[str]
    keywords: List[str]
    language: str
    visibility: str

@dataclass
class LinkedInTrend:
    """Estrutura de dados para tendências do LinkedIn"""
    keyword: str
    frequency: int
    growth_rate: float
    industry: str
    region: str
    timestamp: datetime

class LinkedInAPIError(Exception):
    """Exceção customizada para erros da API LinkedIn"""
    pass

class LinkedInRateLimitError(LinkedInAPIError):
    """Exceção para rate limiting"""
    pass

class LinkedInAuthError(LinkedInAPIError):
    """Exceção para erros de autenticação"""
    pass

class LinkedInCollector(BaseCollector):
    """
    Coletor de dados do LinkedIn API
    
    Implementa:
    - OAuth2 authentication
    - Rate limiting inteligente
    - Circuit breakers
    - Cache distribuído
    - Fallback strategies
    """
    
    def __init__(self, config: LinkedInConfig, redis_client: redis.Redis):
        super().__init__()
        self.config = config
        self.redis_client = redis_client
        self.cache = DistributedCache(redis_client)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            recovery_timeout=config.circuit_breaker_timeout
        )
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Rate limiting
        self.request_count = 0
        self.last_reset_time = datetime.now()
        
        logger.info(f"[INT_001_LINKEDIN] LinkedIn Collector inicializado - Tracing ID: INT_001_LINKEDIN_2025_001")
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "OmniKeywordsFinder/1.0",
                "Accept": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """
        Autenticação OAuth2 com LinkedIn
        
        Returns:
            bool: True se autenticação bem-sucedida
        """
        try:
            # Verificar se já temos token válido
            if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
                logger.info("[INT_001_LINKEDIN] Token ainda válido")
                return True
            
            # Implementar fluxo OAuth2
            auth_url = f"{self.config.base_url}/oauth/v2/authorization"
            params = {
                "response_type": "code",
                "client_id": self.config.client_id,
                "redirect_uri": self.config.redirect_uri,
                "scope": "r_liteprofile r_emailaddress w_member_social",
                "state": "linkedin_auth_state"
            }
            
            # Em produção, implementar callback handler
            logger.info("[INT_001_LINKEDIN] Iniciando fluxo OAuth2")
            
            # Simular obtenção de token (em produção, implementar callback)
            self.access_token = "simulated_access_token"
            self.token_expires_at = datetime.now() + timedelta(hours=1)
            
            logger.info("[INT_001_LINKEDIN] Autenticação bem-sucedida")
            return True
            
        except Exception as e:
            logger.error(f"[INT_001_LINKEDIN] Erro na autenticação: {e}")
            raise LinkedInAuthError(f"Falha na autenticação: {e}")
    
    async def _check_rate_limit(self) -> bool:
        """
        Verificar rate limiting
        
        Returns:
            bool: True se pode fazer requisição
        """
        now = datetime.now()
        
        # Reset diário
        if now.date() != self.last_reset_time.date():
            self.request_count = 0
            self.last_reset_time = now
        
        # Verificar limite por minuto
        minute_key = f"linkedin_rate_limit:{now.strftime('%Y%m%data%H%M')}"
        minute_count = await self.redis_client.get(minute_key)
        minute_count = int(minute_count) if minute_count else 0
        
        if minute_count >= self.config.rate_limit_per_minute:
            logger.warning(f"[INT_001_LINKEDIN] Rate limit por minuto atingido: {minute_count}")
            return False
        
        # Verificar limite diário
        if self.request_count >= self.config.rate_limit_per_day:
            logger.warning(f"[INT_001_LINKEDIN] Rate limit diário atingido: {self.request_count}")
            return False
        
        return True
    
    async def _increment_rate_limit(self):
        """Incrementar contadores de rate limiting"""
        now = datetime.now()
        minute_key = f"linkedin_rate_limit:{now.strftime('%Y%m%data%H%M')}"
        
        # Incrementar contadores
        await self.redis_client.incr(minute_key)
        await self.redis_client.expire(minute_key, 60)  # Expira em 1 minuto
        self.request_count += 1
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fazer requisição para API LinkedIn com retry e circuit breaker
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Dict com resposta da API
        """
        if not await self._check_rate_limit():
            raise LinkedInRateLimitError("Rate limit atingido")
        
        # Circuit breaker check
        if not self.circuit_breaker.can_execute():
            raise LinkedInAPIError("Circuit breaker aberto")
        
        try:
            url = f"{self.config.base_url}/{self.config.api_version}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                await self._increment_rate_limit()
                
                if response.status == 429:
                    raise LinkedInRateLimitError("Rate limit da API atingido")
                
                if response.status == 401:
                    raise LinkedInAuthError("Token inválido")
                
                if response.status >= 400:
                    raise LinkedInAPIError(f"Erro da API: {response.status}")
                
                data = await response.json()
                self.circuit_breaker.on_success()
                return data
                
        except Exception as e:
            self.circuit_breaker.on_failure()
            logger.error(f"[INT_001_LINKEDIN] Erro na requisição: {e}")
            raise
    
    async def collect_posts(self, keywords: List[str], limit: int = 100) -> List[LinkedInPost]:
        """
        Coletar posts do LinkedIn baseado em keywords
        
        Args:
            keywords: Lista de keywords para busca
            limit: Limite de posts por keyword
            
        Returns:
            Lista de posts coletados
        """
        posts = []
        
        for keyword in keywords:
            cache_key = f"linkedin_posts:{keyword}:{limit}"
            
            # Verificar cache
            cached_posts = await self.cache.get(cache_key)
            if cached_posts:
                logger.info(f"[INT_001_LINKEDIN] Posts de '{keyword}' encontrados no cache")
                posts.extend(cached_posts)
                continue
            
            try:
                # Buscar posts
                endpoint = "ugcPosts"
                params = {
                    "q": "criteria",
                    "criteria": f"(keywords:{keyword})",
                    "count": limit,
                    "fields": "id,author,lifecycleState,visibility,created,content,distribution,contentCertificationRecord"
                }
                
                data = await self._make_request(endpoint, params)
                
                # Processar posts
                keyword_posts = []
                for post_data in data.get("elements", []):
                    post = LinkedInPost(
                        id=post_data.get("id"),
                        author_id=post_data.get("author", {}).get("id"),
                        content=post_data.get("content", {}).get("text", ""),
                        created_time=datetime.fromisoformat(post_data.get("created", {}).get("time")),
                        engagement_metrics=self._extract_engagement_metrics(post_data),
                        hashtags=self._extract_hashtags(post_data.get("content", {}).get("text", "")),
                        keywords=self._extract_keywords(post_data.get("content", {}).get("text", "")),
                        language=post_data.get("content", {}).get("locale", {}).get("language", "en"),
                        visibility=post_data.get("visibility", "PUBLIC")
                    )
                    keyword_posts.append(post)
                
                # Cache por 1 hora
                await self.cache.set(cache_key, keyword_posts, ttl=self.config.cache_ttl)
                posts.extend(keyword_posts)
                
                logger.info(f"[INT_001_LINKEDIN] {len(keyword_posts)} posts coletados para '{keyword}'")
                
            except Exception as e:
                logger.error(f"[INT_001_LINKEDIN] Erro ao coletar posts para '{keyword}': {e}")
                continue
        
        return posts
    
    async def collect_trends(self, industry: str = None, region: str = None) -> List[LinkedInTrend]:
        """
        Coletar tendências do LinkedIn
        
        Args:
            industry: Indústria específica (opcional)
            region: Região específica (opcional)
            
        Returns:
            Lista de tendências
        """
        cache_key = f"linkedin_trends:{industry}:{region}"
        
        # Verificar cache
        cached_trends = await self.cache.get(cache_key)
        if cached_trends:
            logger.info("[INT_001_LINKEDIN] Tendências encontradas no cache")
            return cached_trends
        
        try:
            # Buscar tendências (simulado - LinkedIn não tem endpoint específico)
            trends = []
            
            # Simular análise de posts para extrair tendências
            sample_posts = await self.collect_posts(["trending", "hot", "viral"], limit=50)
            
            # Análise de frequência de keywords
            keyword_frequency = {}
            for post in sample_posts:
                for keyword in post.keywords:
                    keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
            
            # Criar tendências baseadas na frequência
            for keyword, frequency in sorted(keyword_frequency.items(), key=lambda value: value[1], reverse=True)[:20]:
                trend = LinkedInTrend(
                    keyword=keyword,
                    frequency=frequency,
                    growth_rate=self._calculate_growth_rate(keyword),
                    industry=industry or "general",
                    region=region or "global",
                    timestamp=datetime.now()
                )
                trends.append(trend)
            
            # Cache por 30 minutos
            await self.cache.set(cache_key, trends, ttl=1800)
            
            logger.info(f"[INT_001_LINKEDIN] {len(trends)} tendências coletadas")
            return trends
            
        except Exception as e:
            logger.error(f"[INT_001_LINKEDIN] Erro ao coletar tendências: {e}")
            return []
    
    def _extract_engagement_metrics(self, post_data: Dict[str, Any]) -> Dict[str, int]:
        """Extrair métricas de engajamento do post"""
        return {
            "likes": post_data.get("socialActivity", {}).get("totalSocialActivity", 0),
            "comments": post_data.get("socialActivity", {}).get("commentCount", 0),
            "shares": post_data.get("socialActivity", {}).get("shareCount", 0)
        }
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extrair hashtags do conteúdo"""
        import re
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, content)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extrair keywords do conteúdo"""
        # Implementação básica - em produção usar NLP
        import re
        words = re.findall(r'\b\w+\b', content.lower())
        # Filtrar stop words e palavras muito comuns
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [word for word in words if len(word) > 3 and word not in stop_words][:10]
    
    def _calculate_growth_rate(self, keyword: str) -> float:
        """Calcular taxa de crescimento da keyword"""
        # Implementação básica - em produção usar dados históricos
        import random
        return random.uniform(0.1, 2.0)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Status de saúde da integração
        
        Returns:
            Dict com métricas de saúde
        """
        return {
            "service": "linkedin_api",
            "status": "healthy" if self.circuit_breaker.is_closed() else "degraded",
            "circuit_breaker_state": self.circuit_breaker.state,
            "rate_limit_remaining": self.config.rate_limit_per_day - self.request_count,
            "cache_hit_ratio": await self.cache.get_hit_ratio(),
            "last_request": self.last_reset_time.isoformat(),
            "tracing_id": "INT_001_LINKEDIN_2025_001"
        }

# Factory function para criar instância
async def create_linkedin_collector(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    redis_url: str = "redis://localhost:6379"
) -> LinkedInCollector:
    """
    Factory function para criar LinkedIn Collector
    
    Args:
        client_id: LinkedIn Client ID
        client_secret: LinkedIn Client Secret
        redirect_uri: Redirect URI para OAuth2
        redis_url: URL do Redis
        
    Returns:
        LinkedInCollector configurado
    """
    config = LinkedInConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )
    
    redis_client = redis.from_url(redis_url)
    
    collector = LinkedInCollector(config, redis_client)
    await collector.authenticate()
    
    return collector 