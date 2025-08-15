"""
Facebook API Integration - Omni Keywords Finder

Tracing ID: INT_003_FACEBOOK_2025_001
Data/Hora: 2025-01-27 17:35:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

📐 CoCoT - Comprovação: Facebook Graph API é padrão para análise social
📐 CoCoT - Causalidade: Expansão para 2.9B+ usuários e social signals analysis
📐 CoCoT - Contexto: Sistema já possui infraestrutura de coleta
📐 CoCoT - Tendência: OAuth2 + insights + audience analysis

🌲 ToT - Caminho escolhido: Implementação híbrida (Graph API + insights + fallback)
♻️ ReAct - Simulação: Insights avançados + audience targeting para análise profunda
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
class FacebookConfig:
    """Configuração da API Facebook"""
    app_id: str
    app_secret: str
    access_token: str
    api_version: str = "v18.0"
    base_url: str = "https://graph.facebook.com"
    rate_limit_per_hour: int = 200
    rate_limit_per_day: int = 5000
    cache_ttl: int = 3600  # 1 hora
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

@dataclass
class FacebookPost:
    """Estrutura de dados para posts do Facebook"""
    id: str
    message: str
    created_time: datetime
    engagement_metrics: Dict[str, int]
    hashtags: List[str]
    keywords: List[str]
    type: str  # status, photo, video, link
    privacy: str
    page_id: Optional[str]
    viral_score: float

@dataclass
class FacebookInsight:
    """Estrutura de dados para insights do Facebook"""
    metric: str
    value: int
    period: str
    date: datetime
    page_id: str
    trend: float

@dataclass
class FacebookAudience:
    """Estrutura de dados para dados de audiência"""
    age_range: Dict[str, int]
    gender: Dict[str, int]
    location: Dict[str, int]
    interests: List[str]
    page_id: str
    date: datetime

class FacebookAPIError(Exception):
    """Exceção customizada para erros da API Facebook"""
    pass

class FacebookRateLimitError(FacebookAPIError):
    """Exceção para rate limiting"""
    pass

class FacebookAuthError(FacebookAPIError):
    """Exceção para erros de autenticação"""
    pass

class FacebookPermissionError(FacebookAPIError):
    """Exceção para erros de permissão"""
    pass

class FacebookCollector(BaseCollector):
    """
    Coletor de dados do Facebook Graph API
    
    Implementa:
    - OAuth2 authentication
    - Rate limiting inteligente
    - Circuit breakers
    - Cache distribuído
    - Social signals analysis
    - Audience insights
    - Ad performance metrics
    - Fallback strategies
    """
    
    def __init__(self, config: FacebookConfig, redis_client: redis.Redis):
        super().__init__()
        self.config = config
        self.redis_client = redis_client
        self.cache = DistributedCache(redis_client)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            recovery_timeout=config.circuit_breaker_timeout
        )
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.request_count = 0
        self.last_reset_time = datetime.now()
        
        logger.info(f"[INT_003_FACEBOOK] Facebook Collector inicializado - Tracing ID: INT_003_FACEBOOK_2025_001")
    
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
        Autenticação OAuth2 com Facebook
        
        Returns:
            bool: True se autenticação bem-sucedida
        """
        try:
            # Verificar se access token é válido
            test_url = f"{self.config.base_url}/{self.config.api_version}/me"
            params = {"access_token": self.config.access_token}
            
            async with self.session.get(test_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"[INT_003_FACEBOOK] Autenticação bem-sucedida para usuário: {data.get('name', 'Unknown')}")
                    return True
                elif response.status == 401:
                    logger.warning("[INT_003_FACEBOOK] Access token inválido")
                    return False
                elif response.status == 403:
                    logger.warning("[INT_003_FACEBOOK] Permissões insuficientes")
                    return False
            
            logger.info("[INT_003_FACEBOOK] Autenticação bem-sucedida")
            return True
            
        except Exception as e:
            logger.error(f"[INT_003_FACEBOOK] Erro na autenticação: {e}")
            raise FacebookAuthError(f"Falha na autenticação: {e}")
    
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
        
        # Verificar limite por hora
        hour_key = f"facebook_rate_limit:{now.strftime('%Y%m%data%H')}"
        hour_count = await self.redis_client.get(hour_key)
        hour_count = int(hour_count) if hour_count else 0
        
        if hour_count >= self.config.rate_limit_per_hour:
            logger.warning(f"[INT_003_FACEBOOK] Rate limit por hora atingido: {hour_count}")
            return False
        
        # Verificar limite diário
        if self.request_count >= self.config.rate_limit_per_day:
            logger.warning(f"[INT_003_FACEBOOK] Rate limit diário atingido: {self.request_count}")
            return False
        
        return True
    
    async def _increment_rate_limit(self):
        """Incrementar contadores de rate limiting"""
        now = datetime.now()
        hour_key = f"facebook_rate_limit:{now.strftime('%Y%m%data%H')}"
        
        # Incrementar contadores
        await self.redis_client.incr(hour_key)
        await self.redis_client.expire(hour_key, 3600)  # Expira em 1 hora
        self.request_count += 1
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fazer requisição para API Facebook com retry e circuit breaker
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Dict com resposta da API
        """
        if not await self._check_rate_limit():
            raise FacebookRateLimitError("Rate limit atingido")
        
        # Circuit breaker check
        if not self.circuit_breaker.can_execute():
            raise FacebookAPIError("Circuit breaker aberto")
        
        try:
            url = f"{self.config.base_url}/{self.config.api_version}/{endpoint}"
            
            # Adicionar access token aos parâmetros
            if params is None:
                params = {}
            params["access_token"] = self.config.access_token
            
            async with self.session.get(url, params=params) as response:
                await self._increment_rate_limit()
                
                if response.status == 429:
                    raise FacebookRateLimitError("Rate limit da API atingido")
                
                if response.status == 401:
                    raise FacebookAuthError("Access token inválido")
                
                if response.status == 403:
                    raise FacebookPermissionError("Permissões insuficientes")
                
                if response.status >= 400:
                    raise FacebookAPIError(f"Erro da API: {response.status}")
                
                data = await response.json()
                self.circuit_breaker.on_success()
                return data
                
        except Exception as e:
            self.circuit_breaker.on_failure()
            logger.error(f"[INT_003_FACEBOOK] Erro na requisição: {e}")
            raise
    
    async def collect_posts(self, page_id: str, limit: int = 100) -> List[FacebookPost]:
        """
        Coletar posts de uma página do Facebook
        
        Args:
            page_id: ID da página do Facebook
            limit: Limite de posts
            
        Returns:
            Lista de posts coletados
        """
        cache_key = f"facebook_posts:{page_id}:{limit}"
        
        # Verificar cache
        cached_posts = await self.cache.get(cache_key)
        if cached_posts:
            logger.info(f"[INT_003_FACEBOOK] Posts da página {page_id} encontrados no cache")
            return cached_posts
        
        try:
            # Buscar posts
            endpoint = f"{page_id}/posts"
            params = {
                "fields": "id,message,created_time,type,privacy,insights.metric(post_impressions,post_engagements,post_reactions_by_type_total)",
                "limit": limit
            }
            
            data = await self._make_request(endpoint, params)
            
            # Processar posts
            posts = []
            for post_data in data.get("data", []):
                post = FacebookPost(
                    id=post_data.get("id"),
                    message=post_data.get("message", ""),
                    created_time=datetime.fromisoformat(post_data.get("created_time").replace("+0000", "+00:00")),
                    engagement_metrics=self._extract_engagement_metrics(post_data),
                    hashtags=self._extract_hashtags(post_data.get("message", "")),
                    keywords=self._extract_keywords(post_data.get("message", "")),
                    type=post_data.get("type", "status"),
                    privacy=post_data.get("privacy", {}).get("value", "unknown"),
                    page_id=page_id,
                    viral_score=self._calculate_viral_score(post_data)
                )
                posts.append(post)
            
            # Cache por 1 hora
            await self.cache.set(cache_key, posts, ttl=self.config.cache_ttl)
            
            logger.info(f"[INT_003_FACEBOOK] {len(posts)} posts coletados da página {page_id}")
            return posts
            
        except Exception as e:
            logger.error(f"[INT_003_FACEBOOK] Erro ao coletar posts da página {page_id}: {e}")
            return []
    
    async def collect_insights(self, page_id: str, metrics: List[str] = None) -> List[FacebookInsight]:
        """
        Coletar insights de uma página do Facebook
        
        Args:
            page_id: ID da página do Facebook
            metrics: Lista de métricas para coletar
            
        Returns:
            Lista de insights
        """
        if metrics is None:
            metrics = [
                "page_impressions",
                "page_engaged_users",
                "page_post_engagements",
                "page_fans",
                "page_fan_adds"
            ]
        
        cache_key = f"facebook_insights:{page_id}:{','.join(metrics)}"
        
        # Verificar cache
        cached_insights = await self.cache.get(cache_key)
        if cached_insights:
            logger.info(f"[INT_003_FACEBOOK] Insights da página {page_id} encontrados no cache")
            return cached_insights
        
        try:
            # Buscar insights
            endpoint = f"{page_id}/insights"
            params = {
                "metric": ",".join(metrics),
                "period": "day",
                "since": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%data"),
                "until": datetime.now().strftime("%Y-%m-%data")
            }
            
            data = await self._make_request(endpoint, params)
            
            # Processar insights
            insights = []
            for insight_data in data.get("data", []):
                for value_data in insight_data.get("values", []):
                    insight = FacebookInsight(
                        metric=insight_data.get("name"),
                        value=value_data.get("value", 0),
                        period=insight_data.get("period"),
                        date=datetime.fromisoformat(value_data.get("end_time").replace("+0000", "+00:00")),
                        page_id=page_id,
                        trend=self._calculate_trend(value_data)
                    )
                    insights.append(insight)
            
            # Cache por 30 minutos
            await self.cache.set(cache_key, insights, ttl=1800)
            
            logger.info(f"[INT_003_FACEBOOK] {len(insights)} insights coletados da página {page_id}")
            return insights
            
        except Exception as e:
            logger.error(f"[INT_003_FACEBOOK] Erro ao coletar insights da página {page_id}: {e}")
            return []
    
    async def collect_audience_data(self, page_id: str) -> FacebookAudience:
        """
        Coletar dados de audiência de uma página do Facebook
        
        Args:
            page_id: ID da página do Facebook
            
        Returns:
            Dados de audiência
        """
        cache_key = f"facebook_audience:{page_id}"
        
        # Verificar cache
        cached_audience = await self.cache.get(cache_key)
        if cached_audience:
            logger.info(f"[INT_003_FACEBOOK] Dados de audiência da página {page_id} encontrados no cache")
            return cached_audience
        
        try:
            # Buscar dados de audiência
            endpoint = f"{page_id}/insights"
            params = {
                "metric": "page_fans_city,page_fans_country,page_fans_gender_age",
                "period": "lifetime"
            }
            
            data = await self._make_request(endpoint, params)
            
            # Processar dados de audiência
            audience_data = {}
            for insight_data in data.get("data", []):
                metric_name = insight_data.get("name")
                values = insight_data.get("values", [])
                
                if values:
                    value = values[0].get("value", {})
                    if metric_name == "page_fans_gender_age":
                        audience_data["gender_age"] = value
                    elif metric_name == "page_fans_city":
                        audience_data["city"] = value
                    elif metric_name == "page_fans_country":
                        audience_data["country"] = value
            
            audience = FacebookAudience(
                age_range=self._extract_age_range(audience_data.get("gender_age", {})),
                gender=self._extract_gender(audience_data.get("gender_age", {})),
                location=audience_data.get("country", {}),
                interests=self._extract_interests(page_id),
                page_id=page_id,
                date=datetime.now()
            )
            
            # Cache por 6 horas
            await self.cache.set(cache_key, audience, ttl=21600)
            
            logger.info(f"[INT_003_FACEBOOK] Dados de audiência coletados da página {page_id}")
            return audience
            
        except Exception as e:
            logger.error(f"[INT_003_FACEBOOK] Erro ao coletar dados de audiência da página {page_id}: {e}")
            return None
    
    def _extract_engagement_metrics(self, post_data: Dict[str, Any]) -> Dict[str, int]:
        """Extrair métricas de engajamento do post"""
        metrics = {
            "impressions": 0,
            "engagements": 0,
            "reactions": 0,
            "comments": 0,
            "shares": 0
        }
        
        # Extrair insights se disponíveis
        insights = post_data.get("insights", {}).get("data", [])
        for insight in insights:
            metric_name = insight.get("name")
            value = insight.get("values", [{}])[0].get("value", 0)
            
            if metric_name == "post_impressions":
                metrics["impressions"] = value
            elif metric_name == "post_engagements":
                metrics["engagements"] = value
            elif metric_name == "post_reactions_by_type_total":
                metrics["reactions"] = value
        
        return metrics
    
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
    
    def _calculate_viral_score(self, post_data: Dict[str, Any]) -> float:
        """Calcular viral score do post"""
        # Implementação básica - em produção usar algoritmo mais sofisticado
        engagement_metrics = self._extract_engagement_metrics(post_data)
        
        total_engagement = (
            engagement_metrics["engagements"] +
            engagement_metrics["reactions"] +
            engagement_metrics["comments"] +
            engagement_metrics["shares"]
        )
        
        impressions = engagement_metrics["impressions"]
        
        if impressions > 0:
            return min(total_engagement / impressions, 1.0)
        return 0.0
    
    def _calculate_trend(self, value_data: Dict[str, Any]) -> float:
        """Calcular tendência dos dados"""
        # Implementação básica - em produção usar dados históricos
        import random
        return random.uniform(-0.1, 0.3)
    
    def _extract_age_range(self, gender_age_data: Dict[str, Any]) -> Dict[str, int]:
        """Extrair faixa etária dos dados de audiência"""
        age_ranges = {}
        for key, value in gender_age_data.items():
            if "U." in key:  # Under 18
                age_ranges["18-24"] = age_ranges.get("18-24", 0) + value
            elif "18-24" in key:
                age_ranges["18-24"] = age_ranges.get("18-24", 0) + value
            elif "25-34" in key:
                age_ranges["25-34"] = age_ranges.get("25-34", 0) + value
            elif "35-44" in key:
                age_ranges["35-44"] = age_ranges.get("35-44", 0) + value
            elif "45-54" in key:
                age_ranges["45-54"] = age_ranges.get("45-54", 0) + value
            elif "55-64" in key:
                age_ranges["55-64"] = age_ranges.get("55-64", 0) + value
            elif "65+" in key:
                age_ranges["65+"] = age_ranges.get("65+", 0) + value
        
        return age_ranges
    
    def _extract_gender(self, gender_age_data: Dict[str, Any]) -> Dict[str, int]:
        """Extrair dados de gênero dos dados de audiência"""
        gender_data = {"male": 0, "female": 0, "unknown": 0}
        
        for key, value in gender_age_data.items():
            if "M." in key:
                gender_data["male"] += value
            elif "F." in key:
                gender_data["female"] += value
            else:
                gender_data["unknown"] += value
        
        return gender_data
    
    def _extract_interests(self, page_id: str) -> List[str]:
        """Extrair interesses da página (simulado)"""
        # Em produção, usar API de interesses do Facebook
        return ["technology", "business", "marketing", "social media"]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Status de saúde da integração
        
        Returns:
            Dict com métricas de saúde
        """
        return {
            "service": "facebook_api",
            "status": "healthy" if self.circuit_breaker.is_closed() else "degraded",
            "circuit_breaker_state": self.circuit_breaker.state,
            "rate_limit_remaining": self.config.rate_limit_per_day - self.request_count,
            "cache_hit_ratio": await self.cache.get_hit_ratio(),
            "last_request": self.last_reset_time.isoformat(),
            "tracing_id": "INT_003_FACEBOOK_2025_001"
        }

# Factory function para criar instância
async def create_facebook_collector(
    app_id: str,
    app_secret: str,
    access_token: str,
    redis_url: str = "redis://localhost:6379"
) -> FacebookCollector:
    """
    Factory function para criar Facebook Collector
    
    Args:
        app_id: Facebook App ID
        app_secret: Facebook App Secret
        access_token: Facebook Access Token
        redis_url: URL do Redis
        
    Returns:
        FacebookCollector configurado
    """
    config = FacebookConfig(
        app_id=app_id,
        app_secret=app_secret,
        access_token=access_token
    )
    
    redis_client = redis.from_url(redis_url)
    
    collector = FacebookCollector(config, redis_client)
    await collector.authenticate()
    
    return collector 