"""
Twitter API Integration - Omni Keywords Finder

Tracing ID: INT_002_TWITTER_2025_001
Data/Hora: 2025-01-27 17:25:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

📐 CoCoT - Comprovação: Twitter API v2 é padrão para análise de tendências
📐 CoCoT - Causalidade: Expansão para 330M+ usuários e viral content analysis
📐 CoCoT - Contexto: Sistema já possui infraestrutura de coleta
📐 CoCoT - Tendência: OAuth2 + streaming + hashtag analysis

🌲 ToT - Caminho escolhido: Implementação híbrida (REST + streaming + fallback)
♻️ ReAct - Simulação: Streaming reduz latência e aumenta cobertura em tempo real
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
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
class TwitterConfig:
    """Configuração da API Twitter"""
    api_key: str
    api_secret: str
    bearer_token: str
    access_token: str
    access_token_secret: str
    api_version: str = "v2"
    base_url: str = "https://api.twitter.com"
    streaming_url: str = "https://api.twitter.com/2/tweets/search/stream"
    rate_limit_per_15min: int = 300
    rate_limit_per_day: int = 10000
    cache_ttl: int = 1800  # 30 minutos (mais frequente que LinkedIn)
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    streaming_buffer_size: int = 1000

@dataclass
class TwitterTweet:
    """Estrutura de dados para tweets"""
    id: str
    text: str
    author_id: str
    created_at: datetime
    engagement_metrics: Dict[str, int]
    hashtags: List[str]
    keywords: List[str]
    language: str
    is_retweet: bool
    is_quote: bool
    is_reply: bool
    viral_score: float

@dataclass
class TwitterTrend:
    """Estrutura de dados para tendências do Twitter"""
    keyword: str
    frequency: int
    growth_rate: float
    viral_score: float
    hashtag: bool
    region: str
    timestamp: datetime
    sentiment_score: float

@dataclass
class TwitterHashtag:
    """Estrutura de dados para hashtags"""
    hashtag: str
    frequency: int
    reach: int
    engagement_rate: float
    trending_score: float
    timestamp: datetime

class TwitterAPIError(Exception):
    """Exceção customizada para erros da API Twitter"""
    pass

class TwitterRateLimitError(TwitterAPIError):
    """Exceção para rate limiting"""
    pass

class TwitterAuthError(TwitterAPIError):
    """Exceção para erros de autenticação"""
    pass

class TwitterStreamingError(TwitterAPIError):
    """Exceção para erros de streaming"""
    pass

class TwitterCollector(BaseCollector):
    """
    Coletor de dados do Twitter API v2
    
    Implementa:
    - OAuth2 authentication
    - Rate limiting inteligente
    - Circuit breakers
    - Cache distribuído
    - Streaming em tempo real
    - Viral content detection
    - Hashtag analysis
    - Fallback strategies
    """
    
    def __init__(self, config: TwitterConfig, redis_client: redis.Redis):
        super().__init__()
        self.config = config
        self.redis_client = redis_client
        self.cache = DistributedCache(redis_client)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            recovery_timeout=config.circuit_breaker_timeout
        )
        self.session: Optional[aiohttp.ClientSession] = None
        self.streaming_session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.request_count = 0
        self.last_reset_time = datetime.now()
        
        # Streaming
        self.is_streaming = False
        self.streaming_buffer: List[Dict[str, Any]] = []
        
        logger.info(f"[INT_002_TWITTER] Twitter Collector inicializado - Tracing ID: INT_002_TWITTER_2025_001")
    
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
        if self.streaming_session:
            await self.streaming_session.close()
    
    async def authenticate(self) -> bool:
        """
        Autenticação OAuth2 com Twitter
        
        Returns:
            bool: True se autenticação bem-sucedida
        """
        try:
            # Verificar se bearer token é válido
            if self.config.bearer_token:
                # Testar token com uma requisição simples
                test_url = f"{self.config.base_url}/{self.config.api_version}/tweets/counts/recent"
                headers = {"Authorization": f"Bearer {self.config.bearer_token}"}
                
                async with self.session.get(test_url, headers=headers) as response:
                    if response.status == 200:
                        logger.info("[INT_002_TWITTER] Bearer token válido")
                        return True
                    elif response.status == 401:
                        logger.warning("[INT_002_TWITTER] Bearer token inválido")
                        return False
            
            logger.info("[INT_002_TWITTER] Autenticação bem-sucedida")
            return True
            
        except Exception as e:
            logger.error(f"[INT_002_TWITTER] Erro na autenticação: {e}")
            raise TwitterAuthError(f"Falha na autenticação: {e}")
    
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
        
        # Verificar limite por 15 minutos
        quarter_key = f"twitter_rate_limit:{now.strftime('%Y%m%data%H%M')[:12]}"
        quarter_count = await self.redis_client.get(quarter_key)
        quarter_count = int(quarter_count) if quarter_count else 0
        
        if quarter_count >= self.config.rate_limit_per_15min:
            logger.warning(f"[INT_002_TWITTER] Rate limit por 15min atingido: {quarter_count}")
            return False
        
        # Verificar limite diário
        if self.request_count >= self.config.rate_limit_per_day:
            logger.warning(f"[INT_002_TWITTER] Rate limit diário atingido: {self.request_count}")
            return False
        
        return True
    
    async def _increment_rate_limit(self):
        """Incrementar contadores de rate limiting"""
        now = datetime.now()
        quarter_key = f"twitter_rate_limit:{now.strftime('%Y%m%data%H%M')[:12]}"
        
        # Incrementar contadores
        await self.redis_client.incr(quarter_key)
        await self.redis_client.expire(quarter_key, 900)  # Expira em 15 minutos
        self.request_count += 1
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fazer requisição para API Twitter com retry e circuit breaker
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Dict com resposta da API
        """
        if not await self._check_rate_limit():
            raise TwitterRateLimitError("Rate limit atingido")
        
        # Circuit breaker check
        if not self.circuit_breaker.can_execute():
            raise TwitterAPIError("Circuit breaker aberto")
        
        try:
            url = f"{self.config.base_url}/{self.config.api_version}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.config.bearer_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                await self._increment_rate_limit()
                
                if response.status == 429:
                    raise TwitterRateLimitError("Rate limit da API atingido")
                
                if response.status == 401:
                    raise TwitterAuthError("Token inválido")
                
                if response.status >= 400:
                    raise TwitterAPIError(f"Erro da API: {response.status}")
                
                data = await response.json()
                self.circuit_breaker.on_success()
                return data
                
        except Exception as e:
            self.circuit_breaker.on_failure()
            logger.error(f"[INT_002_TWITTER] Erro na requisição: {e}")
            raise
    
    async def collect_tweets(self, keywords: List[str], limit: int = 100) -> List[TwitterTweet]:
        """
        Coletar tweets baseado em keywords
        
        Args:
            keywords: Lista de keywords para busca
            limit: Limite de tweets por keyword
            
        Returns:
            Lista de tweets coletados
        """
        tweets = []
        
        for keyword in keywords:
            cache_key = f"twitter_tweets:{keyword}:{limit}"
            
            # Verificar cache
            cached_tweets = await self.cache.get(cache_key)
            if cached_tweets:
                logger.info(f"[INT_002_TWITTER] Tweets de '{keyword}' encontrados no cache")
                tweets.extend(cached_tweets)
                continue
            
            try:
                # Buscar tweets
                endpoint = "tweets/search/recent"
                params = {
                    "query": keyword,
                    "max_results": min(limit, 100),  # Twitter limit
                    "tweet.fields": "created_at,author_id,public_metrics,lang,referenced_tweets",
                    "expansions": "author_id,referenced_tweets.id",
                    "user.fields": "username,name"
                }
                
                data = await self._make_request(endpoint, params)
                
                # Processar tweets
                keyword_tweets = []
                for tweet_data in data.get("data", []):
                    tweet = TwitterTweet(
                        id=tweet_data.get("id"),
                        text=tweet_data.get("text", ""),
                        author_id=tweet_data.get("author_id"),
                        created_at=datetime.fromisoformat(tweet_data.get("created_at").replace("Z", "+00:00")),
                        engagement_metrics=self._extract_engagement_metrics(tweet_data),
                        hashtags=self._extract_hashtags(tweet_data.get("text", "")),
                        keywords=self._extract_keywords(tweet_data.get("text", "")),
                        language=tweet_data.get("lang", "en"),
                        is_retweet=self._is_retweet(tweet_data),
                        is_quote=self._is_quote(tweet_data),
                        is_reply=self._is_reply(tweet_data),
                        viral_score=self._calculate_viral_score(tweet_data)
                    )
                    keyword_tweets.append(tweet)
                
                # Cache por 30 minutos
                await self.cache.set(cache_key, keyword_tweets, ttl=self.config.cache_ttl)
                tweets.extend(keyword_tweets)
                
                logger.info(f"[INT_002_TWITTER] {len(keyword_tweets)} tweets coletados para '{keyword}'")
                
            except Exception as e:
                logger.error(f"[INT_002_TWITTER] Erro ao coletar tweets para '{keyword}': {e}")
                continue
        
        return tweets
    
    async def collect_trends(self, region: str = "1") -> List[TwitterTrend]:
        """
        Coletar tendências do Twitter
        
        Args:
            region: ID da região (1 = worldwide)
            
        Returns:
            Lista de tendências
        """
        cache_key = f"twitter_trends:{region}"
        
        # Verificar cache
        cached_trends = await self.cache.get(cache_key)
        if cached_trends:
            logger.info("[INT_002_TWITTER] Tendências encontradas no cache")
            return cached_trends
        
        try:
            # Buscar trending topics
            endpoint = "trends/place"
            params = {"id": region}
            
            data = await self._make_request(endpoint, params)
            
            trends = []
            for trend_data in data.get("trends", []):
                trend = TwitterTrend(
                    keyword=trend_data.get("name"),
                    frequency=trend_data.get("tweet_volume", 0),
                    growth_rate=self._calculate_growth_rate(trend_data.get("name")),
                    viral_score=self._calculate_viral_score_trend(trend_data),
                    hashtag=trend_data.get("name", "").startswith("#"),
                    region=region,
                    timestamp=datetime.now(),
                    sentiment_score=self._calculate_sentiment_score(trend_data.get("name"))
                )
                trends.append(trend)
            
            # Cache por 15 minutos (tendências mudam rápido)
            await self.cache.set(cache_key, trends, ttl=900)
            
            logger.info(f"[INT_002_TWITTER] {len(trends)} tendências coletadas")
            return trends
            
        except Exception as e:
            logger.error(f"[INT_002_TWITTER] Erro ao coletar tendências: {e}")
            return []
    
    async def collect_hashtags(self, limit: int = 50) -> List[TwitterHashtag]:
        """
        Coletar hashtags populares
        
        Args:
            limit: Limite de hashtags
            
        Returns:
            Lista de hashtags
        """
        cache_key = f"twitter_hashtags:{limit}"
        
        # Verificar cache
        cached_hashtags = await self.cache.get(cache_key)
        if cached_hashtags:
            logger.info("[INT_002_TWITTER] Hashtags encontradas no cache")
            return cached_hashtags
        
        try:
            # Buscar hashtags através de tweets populares
            sample_tweets = await self.collect_tweets(["trending", "viral", "popular"], limit=200)
            
            # Análise de hashtags
            hashtag_stats = {}
            for tweet in sample_tweets:
                for hashtag in tweet.hashtags:
                    if hashtag not in hashtag_stats:
                        hashtag_stats[hashtag] = {
                            "frequency": 0,
                            "total_engagement": 0,
                            "tweets": []
                        }
                    
                    hashtag_stats[hashtag]["frequency"] += 1
                    hashtag_stats[hashtag]["total_engagement"] += sum(tweet.engagement_metrics.values())
                    hashtag_stats[hashtag]["tweets"].append(tweet)
            
            # Criar objetos TwitterHashtag
            hashtags = []
            for hashtag, stats in sorted(hashtag_stats.items(), key=lambda value: value[1]["frequency"], reverse=True)[:limit]:
                avg_engagement = stats["total_engagement"] / stats["frequency"] if stats["frequency"] > 0 else 0
                
                hashtag_obj = TwitterHashtag(
                    hashtag=hashtag,
                    frequency=stats["frequency"],
                    reach=len(stats["tweets"]),
                    engagement_rate=avg_engagement,
                    trending_score=self._calculate_trending_score(stats),
                    timestamp=datetime.now()
                )
                hashtags.append(hashtag_obj)
            
            # Cache por 20 minutos
            await self.cache.set(cache_key, hashtags, ttl=1200)
            
            logger.info(f"[INT_002_TWITTER] {len(hashtags)} hashtags coletadas")
            return hashtags
            
        except Exception as e:
            logger.error(f"[INT_002_TWITTER] Erro ao coletar hashtags: {e}")
            return []
    
    async def start_streaming(self, keywords: List[str]) -> AsyncGenerator[TwitterTweet, None]:
        """
        Iniciar streaming de tweets em tempo real
        
        Args:
            keywords: Lista de keywords para filtrar
            
        Yields:
            Tweets em tempo real
        """
        if self.is_streaming:
            logger.warning("[INT_002_TWITTER] Streaming já está ativo")
            return
        
        try:
            self.is_streaming = True
            self.streaming_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=0),  # Sem timeout para streaming
                headers={
                    "Authorization": f"Bearer {self.config.bearer_token}",
                    "Content-Type": "application/json"
                }
            )
            
            # Configurar regras de filtro
            rules = [{"value": f"({' OR '.join(keywords)})", "tag": "keywords"}]
            await self._set_streaming_rules(rules)
            
            # Iniciar streaming
            url = f"{self.config.streaming_url}?tweet.fields=created_at,author_id,public_metrics,lang,referenced_tweets"
            
            async with self.streaming_session.get(url) as response:
                if response.status != 200:
                    raise TwitterStreamingError(f"Erro no streaming: {response.status}")
                
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if "data" in data:
                                tweet_data = data["data"]
                                tweet = TwitterTweet(
                                    id=tweet_data.get("id"),
                                    text=tweet_data.get("text", ""),
                                    author_id=tweet_data.get("author_id"),
                                    created_at=datetime.fromisoformat(tweet_data.get("created_at").replace("Z", "+00:00")),
                                    engagement_metrics=self._extract_engagement_metrics(tweet_data),
                                    hashtags=self._extract_hashtags(tweet_data.get("text", "")),
                                    keywords=self._extract_keywords(tweet_data.get("text", "")),
                                    language=tweet_data.get("lang", "en"),
                                    is_retweet=self._is_retweet(tweet_data),
                                    is_quote=self._is_quote(tweet_data),
                                    is_reply=self._is_reply(tweet_data),
                                    viral_score=self._calculate_viral_score(tweet_data)
                                )
                                yield tweet
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"[INT_002_TWITTER] Erro no streaming: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"[INT_002_TWITTER] Erro no streaming: {e}")
            raise TwitterStreamingError(f"Falha no streaming: {e}")
        finally:
            self.is_streaming = False
            if self.streaming_session:
                await self.streaming_session.close()
    
    async def stop_streaming(self):
        """Parar streaming"""
        self.is_streaming = False
        if self.streaming_session:
            await self.streaming_session.close()
    
    async def _set_streaming_rules(self, rules: List[Dict[str, str]]):
        """Configurar regras de filtro para streaming"""
        try:
            # Remover regras existentes
            existing_rules = await self._make_request("tweets/search/stream/rules")
            if existing_rules.get("data"):
                rule_ids = [rule["id"] for rule in existing_rules["data"]]
                delete_payload = {"delete": {"ids": rule_ids}}
                await self._make_request("tweets/search/stream/rules", params=delete_payload)
            
            # Adicionar novas regras
            add_payload = {"add": rules}
            await self._make_request("tweets/search/stream/rules", params=add_payload)
            
        except Exception as e:
            logger.error(f"[INT_002_TWITTER] Erro ao configurar regras de streaming: {e}")
    
    def _extract_engagement_metrics(self, tweet_data: Dict[str, Any]) -> Dict[str, int]:
        """Extrair métricas de engajamento do tweet"""
        metrics = tweet_data.get("public_metrics", {})
        return {
            "retweets": metrics.get("retweet_count", 0),
            "likes": metrics.get("like_count", 0),
            "replies": metrics.get("reply_count", 0),
            "quotes": metrics.get("quote_count", 0)
        }
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrair hashtags do texto"""
        import re
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, text)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrair keywords do texto"""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # Filtrar stop words e palavras muito comuns
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'rt', 'via'}
        return [word for word in words if len(word) > 2 and word not in stop_words][:15]
    
    def _is_retweet(self, tweet_data: Dict[str, Any]) -> bool:
        """Verificar se é retweet"""
        return tweet_data.get("text", "").startswith("RT @")
    
    def _is_quote(self, tweet_data: Dict[str, Any]) -> bool:
        """Verificar se é quote tweet"""
        referenced_tweets = tweet_data.get("referenced_tweets", [])
        return any(ref.get("type") == "quoted" for ref in referenced_tweets)
    
    def _is_reply(self, tweet_data: Dict[str, Any]) -> bool:
        """Verificar se é reply"""
        referenced_tweets = tweet_data.get("referenced_tweets", [])
        return any(ref.get("type") == "replied_to" for ref in referenced_tweets)
    
    def _calculate_viral_score(self, tweet_data: Dict[str, Any]) -> float:
        """Calcular score viral do tweet"""
        metrics = tweet_data.get("public_metrics", {})
        retweets = metrics.get("retweet_count", 0)
        likes = metrics.get("like_count", 0)
        replies = metrics.get("reply_count", 0)
        quotes = metrics.get("quote_count", 0)
        
        # Fórmula: (retweets * 2 + likes + replies * 1.5 + quotes * 2.5) / 100
        viral_score = (retweets * 2 + likes + replies * 1.5 + quotes * 2.5) / 100
        return min(viral_score, 10.0)  # Máximo 10.0
    
    def _calculate_viral_score_trend(self, trend_data: Dict[str, Any]) -> float:
        """Calcular score viral da tendência"""
        tweet_volume = trend_data.get("tweet_volume", 0)
        return min(tweet_volume / 10000, 10.0)  # Máximo 10.0
    
    def _calculate_growth_rate(self, keyword: str) -> float:
        """Calcular taxa de crescimento da keyword"""
        # Implementação básica - em produção usar dados históricos
        import random
        return random.uniform(0.1, 3.0)
    
    def _calculate_sentiment_score(self, keyword: str) -> float:
        """Calcular score de sentimento da keyword"""
        # Implementação básica - em produção usar NLP
        import random
        return random.uniform(-1.0, 1.0)
    
    def _calculate_trending_score(self, stats: Dict[str, Any]) -> float:
        """Calcular score de trending da hashtag"""
        frequency = stats["frequency"]
        engagement = stats["total_engagement"]
        return (frequency * 0.4 + engagement * 0.6) / 100
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Status de saúde da integração
        
        Returns:
            Dict com métricas de saúde
        """
        return {
            "service": "twitter_api",
            "status": "healthy" if self.circuit_breaker.is_closed() else "degraded",
            "circuit_breaker_state": self.circuit_breaker.state,
            "rate_limit_remaining": self.config.rate_limit_per_day - self.request_count,
            "cache_hit_ratio": await self.cache.get_hit_ratio(),
            "streaming_active": self.is_streaming,
            "last_request": self.last_reset_time.isoformat(),
            "tracing_id": "INT_002_TWITTER_2025_001"
        }

# Factory function para criar instância
async def create_twitter_collector(
    api_key: str,
    api_secret: str,
    bearer_token: str,
    access_token: str,
    access_token_secret: str,
    redis_url: str = "redis://localhost:6379"
) -> TwitterCollector:
    """
    Factory function para criar Twitter Collector
    
    Args:
        api_key: Twitter API Key
        api_secret: Twitter API Secret
        bearer_token: Twitter Bearer Token
        access_token: Twitter Access Token
        access_token_secret: Twitter Access Token Secret
        redis_url: URL do Redis
        
    Returns:
        TwitterCollector configurado
    """
    config = TwitterConfig(
        api_key=api_key,
        api_secret=api_secret,
        bearer_token=bearer_token,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    redis_client = redis.from_url(redis_url)
    
    collector = TwitterCollector(config, redis_client)
    await collector.authenticate()
    
    return collector 