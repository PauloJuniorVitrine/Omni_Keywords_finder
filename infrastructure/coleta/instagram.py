"""
Implementação do coletor de keywords do Instagram.
"""
from typing import List, Dict, Optional
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
from textblob import TextBlob
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    INSTAGRAM_CONFIG,
    CACHE_CONFIG,
    SENTIMENT_CONFIG,
    TRENDS_CONFIG
)
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.sentiment import AnalisadorSentimento
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.logger import logger
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from shared.utils.normalizador_central import NormalizadorCentral

# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

class InstagramColetor(KeywordColetorBase):
    """Implementação do coletor de keywords do Instagram."""

    def __init__(self):
        """Inicializa o coletor com configurações específicas."""
        super().__init__(
            nome="instagram",
            config=INSTAGRAM_CONFIG
        )
        self.base_url = "https://www.instagram.com"
        self.api_url = f"{self.base_url}/api/v1"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.session = None
        
        # Configurações específicas
        self.max_posts = INSTAGRAM_CONFIG["max_posts"]
        self.max_stories = INSTAGRAM_CONFIG["max_stories"]
        self.max_reels = INSTAGRAM_CONFIG["max_reels"]
        self.credentials = INSTAGRAM_CONFIG["credentials"]
        
        # Cache com namespace específico
        self.cache = CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["instagram"],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"]
        )
        
        # Analisadores
        self.analisador_sentimento = AnalisadorSentimento()
        self.analisador_tendencias = AnalisadorTendencias()
        
        # Normalizador centralizado
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-.,?!@#]+$',
            min_caracteres=3,
            max_caracteres=100
        )
        
        # Estado da sessão
        self._auth_token = None
        self._last_auth = None
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()

    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para Instagram API
        self.instagram_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="instagram_api",
                fallback_function=self._fallback_instagram_error
            )
        )
        
        # Configurações de retry
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        # Configurações de bulkhead
        self.bulkhead_config = BulkheadConfig(
            max_concurrent_calls=8,
            max_wait_duration=5.0,
            max_failure_count=3,
            name="instagram_coletor"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=30.0,
            name="instagram_coletor"
        )

    def _fallback_instagram_error(self, *args, **kwargs):
        """Fallback quando Instagram API falha"""
        logger.warning("Instagram API falhou, usando fallback")
        return {"error": "Instagram indisponível", "fallback": True}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP autenticada."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
            await self._autenticar()
        elif self._precisa_reautenticar():
            await self._autenticar()
        return self.session

    async def _autenticar(self) -> None:
        """Realiza autenticação no Instagram."""
        try:
            if not self.credentials:
                raise ValueError("Credenciais não configuradas")

            async with self.session.post(
                f"{self.base_url}/accounts/login/ajax/",
                json={
                    "username": self.credentials["username"],
                    "password": self.credentials["password"],
                    "enc_password": None
                },
                headers={"X-CSRFToken": await self._get_csrf_token()}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro na autenticação: {response.status}")
                    
                data = await response.json()
                if not data.get("authenticated"):
                    raise Exception("Autenticação falhou")
                    
                self._auth_token = response.cookies.get("sessionid")
                self._last_auth = datetime.utcnow()
                
                self.headers.update({
                    "X-IG-App-ID": "936619743392459",
                    "Cookie": f"sessionid={self._auth_token}"
                })
                
                self.registrar_sucesso(
                    "autenticacao",
                    {"username": self.credentials["username"]}
                )
                
        except Exception as e:
            self.registrar_erro(
                "Erro durante autenticação no Instagram",
                {"erro": str(e)}
            )
            raise

    async def _get_csrf_token(self) -> str:
        """Obtém token CSRF para autenticação."""
        async with self.session.get(self.base_url) as response:
            if response.status != 200:
                raise Exception("Erro ao obter CSRF token")
            return response.cookies.get("csrftoken")

    def _precisa_reautenticar(self) -> bool:
        """Verifica se é necessário reautenticar."""
        if not self._last_auth or not self._auth_token:
            return True
            
        # Reautentica a cada 12 horas
        return datetime.utcnow() - self._last_auth > timedelta(hours=12)

    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=8, max_wait_duration=5.0)
    @timeout(timeout_seconds=30.0)
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de busca do Instagram com padrões de resiliência.
        
        Args:
            termo: Termo base para busca
            
        Returns:
            Lista de sugestões relacionadas
        """
        try:
            # Verifica cache
            cache_key = f"sugestoes:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            session = await self._get_session()
            params = {
                "q": termo,
                "context": "blended",
                "count": 30
            }
            
            async with session.get(
                f"{self.api_url}/tags/search/",
                params=params,
                proxy=self.proxy_config if self.proxy_enabled else None
            ) as response:
                if response.status != 200:
                    self.registrar_erro(
                        "Erro ao acessar busca do Instagram",
                        {"status": response.status}
                    )
                    return []
                    
                data = await response.json()
                sugestoes = []
                
                # Extrai hashtags e termos relacionados
                for result in data.get("results", []):
                    name = result.get("name", "").strip()
                    if name and name != termo:
                        sugestoes.append(f"#{name}")
                        
                # Busca também por contas relacionadas
                async with session.get(
                    f"{self.api_url}/users/search/",
                    params=params,
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for user in data.get("users", []):
                            username = user.get("username", "").strip()
                            if username:
                                sugestoes.append(f"@{username}")
                                
                # Salva no cache
                await self.cache.set(
                    cache_key,
                    sugestoes,
                    ttl=CACHE_CONFIG["ttl_keywords"]
                )
                
                self.registrar_sucesso(
                    "extracao_sugestoes",
                    {
                        "termo": termo,
                        "total_sugestoes": len(sugestoes)
                    }
                )
                
                return sugestoes

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair sugestões do Instagram",
                {"erro": str(e), "termo": termo}
            )
            return []

    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        """
        Extrai métricas específicas do Instagram.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do Instagram
        """
        try:
            # Verifica cache
            cache_key = f"metricas:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            session = await self._get_session()
            
            if termo.startswith("#"):
                # Métricas de hashtag
                hashtag = termo.replace("#", "")
                async with session.get(
                    f"{self.api_url}/tags/{hashtag}/info/",
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erro ao acessar hashtag: {response.status}")
                        
                    data = await response.json()
                    metricas = {
                        "total_posts": data.get("media_count", 0),
                        "tipo": "hashtag",
                        "engagement_rate": self._calcular_engagement_rate(data),
                        "trending_score": self._calcular_trending_score(data)
                    }
                    
            elif termo.startswith("@"):
                # Métricas de perfil
                username = termo.replace("@", "")
                async with session.get(
                    f"{self.api_url}/users/{username}/info/",
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erro ao acessar perfil: {response.status}")
                        
                    data = await response.json()
                    user = data.get("user", {})
                    metricas = {
                        "seguidores": user.get("follower_count", 0),
                        "seguindo": user.get("following_count", 0),
                        "total_posts": user.get("media_count", 0),
                        "tipo": "perfil",
                        "engagement_rate": self._calcular_engagement_rate(user),
                        "is_verified": user.get("is_verified", False)
                    }
            else:
                # Métricas gerais de busca
                async with session.get(
                    f"{self.api_url}/discover/search/",
                    params={"query": termo},
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erro ao buscar termo: {response.status}")
                        
                    data = await response.json()
                    total_resultados = len(data.get("results", []))
                    metricas = {
                        "total_resultados": total_resultados,
                        "tipo": "busca",
                        "relevancia": self._calcular_relevancia(total_resultados)
                    }
                    
            # Adiciona métricas comuns
            metricas.update({
                "volume": self._calcular_volume(metricas),
                "concorrencia": self._calcular_concorrencia(metricas),
                "data_coleta": datetime.utcnow().isoformat()
            })
            
            # Salva no cache
            await self.cache.set(
                cache_key,
                metricas,
                ttl=CACHE_CONFIG["ttl_metricas"]
            )
            
            # Atualiza contadores de popularidade
            await self.cache.zadd(
                "popularidade",
                termo,
                metricas["volume"]
            )
            
            return metricas

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do Instagram",
                {"erro": str(e), "termo": termo}
            )
            return {
                "volume": 0,
                "concorrencia": 0.5,
                "tipo": "desconhecido",
                "erro": str(e),
                "metricas": {}
            }

    def _calcular_engagement_rate(self, data: Dict) -> float:
        """Calcula taxa de engajamento baseado nos dados."""
        try:
            if "media_count" in data:  # Hashtag
                total_engagement = sum(
                    post.get("like_count", 0) + post.get("comment_count", 0)
                    for post in data.get("top_posts", [])
                )
                return total_engagement / max(1, len(data.get("top_posts", [])))
            else:  # Perfil
                media = data.get("media", {}).get("nodes", [])
                if not media:
                    return 0.0
                    
                total_engagement = sum(
                    post.get("likes", {}).get("count", 0) + 
                    post.get("comments", {}).get("count", 0)
                    for post in media
                )
                return total_engagement / (max(1, len(media)) * max(1, data.get("follower_count", 1)))
                
        except Exception:
            return 0.0

    def _calcular_trending_score(self, data: Dict) -> float:
        """Calcula score de tendência para hashtags."""
        try:
            recent_posts = len(data.get("recent_posts", []))
            total_posts = data.get("media_count", 0)
            
            if total_posts == 0:
                return 0.0
                
            # Score baseado na proporção de posts recentes
            score = recent_posts / max(1, total_posts)
            
            # Ajusta baseado no crescimento
            if "edge_hashtag_to_media" in data:
                week_posts = data["edge_hashtag_to_media"].get("count", 0)
                if week_posts > 0:
                    score *= (week_posts / max(1, total_posts))
                    
            return min(score, 1.0)
            
        except Exception:
            return 0.0

    def _calcular_volume(self, metricas: Dict) -> int:
        """Calcula volume estimado baseado nas métricas."""
        if metricas["tipo"] == "hashtag":
            total_posts = metricas.get("total_posts", 0)
            if total_posts == 0:
                return 10
            elif total_posts < 1000:
                return 50
            elif total_posts < 10000:
                return 100
            elif total_posts < 100000:
                return 500
            else:
                return 1000
        elif metricas["tipo"] == "perfil":
            seguidores = metricas.get("seguidores", 0)
            if seguidores == 0:
                return 10
            elif seguidores < 1000:
                return 30
            elif seguidores < 10000:
                return 100
            elif seguidores < 100000:
                return 300
            else:
                return 1000
        else:
            return metricas.get("total_resultados", 0)

    def _calcular_concorrencia(self, metricas: Dict) -> float:
        """Calcula nível de concorrência baseado nas métricas."""
        if metricas["tipo"] == "hashtag":
            posts = metricas.get("total_posts", 0)
            if posts == 0:
                return 0.1
            elif posts < 1000:
                return 0.3
            elif posts < 10000:
                return 0.5
            elif posts < 100000:
                return 0.7
            else:
                return 0.9
        elif metricas["tipo"] == "perfil":
            seguidores = metricas.get("seguidores", 0)
            if seguidores == 0:
                return 0.1
            elif seguidores < 1000:
                return 0.2
            elif seguidores < 10000:
                return 0.4
            elif seguidores < 100000:
                return 0.6
            else:
                return 0.8
        else:
            return min(metricas.get("total_resultados", 0) / 1000, 1.0)

    def _calcular_relevancia(self, total_resultados: int) -> float:
        """Calcula score de relevância baseado nos resultados."""
        if total_resultados == 0:
            return 0.0
        elif total_resultados < 10:
            return 0.2
        elif total_resultados < 100:
            return 0.4
        elif total_resultados < 1000:
            return 0.6
        elif total_resultados < 10000:
            return 0.8
        else:
            return 1.0

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o Instagram, usando ValidadorKeywords.
        Retorna False imediatamente se termo for vazio, None ou > 100 caracteres.
        """
        if not termo or not termo.strip():
            self.registrar_erro(
                "Termo inválido para Instagram",
                {"termo": termo, "motivo": "vazio"}
            )
            return False
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo para Instagram",
                {"termo": termo}
            )
            return False
        if termo.startswith("#") or termo.startswith("@"):  # Mantém validação de hashtag/menção
            if len(termo) < 2:
                self.registrar_erro(
                    "Termo muito curto para Instagram",
                    {"termo": termo}
                )
                return False
            termo_limpo = termo[1:]
            if not termo_limpo.replace("_", "").isalnum():
                self.registrar_erro(
                    "Termo contém caracteres inválidos",
                    {"termo": termo}
                )
                return False
        validador = ValidadorKeywords()
        kw = Keyword(termo=termo, volume_busca=0, cpc=0.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
        valido, motivo = validador.validar_keyword(kw)
        if not valido:
            self.registrar_erro(
                "Termo rejeitado pelo ValidadorKeywords",
                {"termo": termo, "motivo": motivo}
            )
        return valido

    async def __aenter__(self):
        """Gerenciamento de contexto para início de sessão."""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gerenciamento de contexto para fechamento de sessão."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[Keyword]:
        """
        Coleta keywords relacionadas do Instagram.
        
        Args:
            termo: Termo base para busca
            limite: Número máximo de keywords a retornar
            
        Returns:
            Lista de objetos Keyword com dados coletados
        """
        if not await self.validar_termo(termo):
            return []

        keywords = []
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # 1. Coleta hashtags relacionadas
                hashtags = await self._coletar_hashtags_relacionadas(session, termo)
                for hashtag in hashtags:
                    if hashtag != termo:
                        keyword = Keyword(
                            termo=hashtag,
                            fonte=self.nome,
                            data_coleta=self.obter_data_atual(),
                            score_relevancia=self.calcular_relevancia(hashtag, termo),
                            metadados={"tipo": "hashtag"},
                            intencao=IntencaoBusca.INFORMACIONAL
                        )
                        if len(keyword.termo.split()) >= 3 and len(keyword.termo) >= 15:
                            keywords.append(keyword)
                        else:
                            self.registrar_sucesso(
                                "descartada_nao_cauda_longa",
                                {
                                    "termo": keyword.termo,
                                    "motivo": "nao_atende_criterio_cauda_longa",
                                    "palavras": len(keyword.termo.split()),
                                    "caracteres": len(keyword.termo)
                                }
                            )

                # 2. Coleta menções em captions
                captions = await self._coletar_captions_relacionadas(session, termo)
                for caption in captions:
                    keywords_caption = self._extrair_keywords_texto(caption)
                    for keyword_caption in keywords_caption:
                        if keyword_caption != termo:
                            keyword = Keyword(
                                termo=keyword_caption,
                                fonte=self.nome,
                                data_coleta=self.obter_data_atual(),
                                score_relevancia=self.calcular_relevancia(keyword_caption, termo),
                                metadados={"tipo": "caption"},
                                intencao=IntencaoBusca.INFORMACIONAL
                            )
                            if len(keyword.termo.split()) >= 3 and len(keyword.termo) >= 15:
                                keywords.append(keyword)
                            else:
                                self.registrar_sucesso(
                                    "descartada_nao_cauda_longa",
                                    {
                                        "termo": keyword.termo,
                                        "motivo": "nao_atende_criterio_cauda_longa",
                                        "palavras": len(keyword.termo.split()),
                                        "caracteres": len(keyword.termo)
                                    }
                                )

                # 3. Coleta perfis relacionados
                perfis = await self._coletar_perfis_relacionados(session, termo)
                for perfil in perfis:
                    if perfil != termo:
                        keyword = Keyword(
                            termo=perfil,
                            fonte=self.nome,
                            data_coleta=self.obter_data_atual(),
                            score_relevancia=self.calcular_relevancia(perfil, termo),
                            metadados={"tipo": "perfil"},
                            intencao=IntencaoBusca.INFORMACIONAL
                        )
                        if len(keyword.termo.split()) >= 3 and len(keyword.termo) >= 15:
                            keywords.append(keyword)
                        else:
                            self.registrar_sucesso(
                                "descartada_nao_cauda_longa",
                                {
                                    "termo": keyword.termo,
                                    "motivo": "nao_atende_criterio_cauda_longa",
                                    "palavras": len(keyword.termo.split()),
                                    "caracteres": len(keyword.termo)
                                }
                            )

            self.atualizar_metricas(len(keywords))
            self.registrar_sucesso("coleta_keywords", {
                "termo_base": termo,
                "total_coletado": len(keywords)
            })
            
            return keywords[:limite]

        except Exception as e:
            self.registrar_erro(
                "Erro durante coleta do Instagram",
                {"erro": str(e)}
            )
            return []

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """Stub mínimo para testes."""
        return [{} for _ in keywords]

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """Stub mínimo para testes."""
        return [IntencaoBusca.NAVEGACIONAL for _ in keywords]

    async def _coletar_hashtags_relacionadas(
        self,
        session: aiohttp.ClientSession,
        termo: str
    ) -> List[str]:
        """Coleta hashtags relacionadas ao termo."""
        hashtags = []
        try:
            # Simula busca de hashtag
            params = {
                "query_hash": "9b498c08113f1e09617a1703c22b2f32",
                "variables": json.dumps({
                    "tag_name": termo.replace("#", ""),
                    "first": 50
                })
            }
            
            async with session.get(
                self.graphql_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    edges = data.get("data", {}).get("hashtag", {}).get("edge_hashtag_to_related_tags", {}).get("edges", [])
                    
                    for edge in edges:
                        hashtag = f"#{edge['node']['name']}"
                        hashtags.append(hashtag)
                        
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar hashtags relacionadas",
                {"erro": str(e)}
            )
            
        return hashtags

    async def _coletar_captions_relacionadas(
        self,
        session: aiohttp.ClientSession,
        termo: str
    ) -> List[str]:
        """Coleta captions de posts relacionados ao termo."""
        captions = []
        try:
            # Simula busca de posts
            params = {
                "query_hash": "bc3296d1ce80a24b1b6e40b1e72903f5",
                "variables": json.dumps({
                    "tag_name": termo.replace("#", ""),
                    "first": 50
                })
            }
            
            async with session.get(
                self.graphql_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    edges = data.get("data", {}).get("hashtag", {}).get("edge_hashtag_to_media", {}).get("edges", [])
                    
                    for edge in edges:
                        caption = edge.get("node", {}).get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", "")
                        if caption:
                            captions.append(caption)
                        
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar captions relacionadas",
                {"erro": str(e)}
            )
            
        return captions

    async def _coletar_perfis_relacionados(
        self,
        session: aiohttp.ClientSession,
        termo: str
    ) -> List[str]:
        """Coleta perfis relacionados ao termo."""
        perfis = []
        try:
            # Simula busca de perfis
            params = {
                "query_hash": "c9100bf9110dd6361671f113dd02e7d6",
                "variables": json.dumps({
                    "search_query": termo,
                    "first": 50
                })
            }
            
            async with session.get(
                self.graphql_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get("data", {}).get("users", [])
                    
                    for user in users:
                        username = f"@{user['username']}"
                        perfis.append(username)
                        
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar perfis relacionados",
                {"erro": str(e)}
            )
            
        return perfis

    async def _coletar_reels(
        self,
        session: aiohttp.ClientSession,
        termo: str
    ) -> List[Dict]:
        """Coleta dados de Reels relacionados ao termo."""
        try:
            params = {
                "query_hash": "e769aa130647d2354c40ea6a439bfc08",
                "variables": json.dumps({
                    "tag_name": termo.replace("#", ""),
                    "first": 50,
                    "include_reel": True
                })
            }
            
            async with session.get(
                f"{self.api_url}/clips/search",
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    reels = []
                    
                    for edge in data.get("data", {}).get("clips", {}).get("edges", []):
                        reel = edge.get("node", {})
                        if reel:
                            reels.append({
                                "id": reel.get("id"),
                                "views": reel.get("video_view_count", 0),
                                "plays": reel.get("video_play_count", 0),
                                "likes": reel.get("like_count", 0),
                                "comments": reel.get("comment_count", 0),
                                "shares": reel.get("share_count", 0),
                                "duration": reel.get("video_duration", 0),
                                "music": reel.get("music_info", {}).get("title"),
                                "hashtags": [
                                    tag.get("name")
                                    for tag in reel.get("hashtags", [])
                                ]
                            })
                    
                    return reels
                    
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar Reels",
                {"erro": str(e)}
            )
            
        return []

    async def _coletar_stories(
        self,
        session: aiohttp.ClientSession,
        termo: str
    ) -> List[Dict]:
        """Coleta dados de Stories relacionados ao termo."""
        try:
            params = {
                "query_hash": "45246d3fe16ccc6577e0bd297a5db1ab",
                "variables": json.dumps({
                    "tag_name": termo.replace("#", ""),
                    "first": 50,
                    "include_stories": True
                })
            }
            
            async with session.get(
                f"{self.api_url}/stories/tags",
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    stories = []
                    
                    for story in data.get("data", {}).get("stories", []):
                        if story:
                            stories.append({
                                "id": story.get("id"),
                                "views": story.get("view_count", 0),
                                "tipo": story.get("type", "image"),
                                "duration": story.get("video_duration", 0) if story.get("type") == "video" else 0,
                                "hashtags": [
                                    tag.get("name")
                                    for tag in story.get("hashtags", [])
                                ],
                                "mentions": [
                                    mention.get("username")
                                    for mention in story.get("mentions", [])
                                ]
                            })
                    
                    return stories
                    
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar Stories",
                {"erro": str(e)}
            )
            
        return []

    async def _analisar_tendencias_temporais(
        self,
        session: aiohttp.ClientSession,
        termo: str,
        dias: int = 7
    ) -> Dict:
        """
        Analisa tendências temporais para um termo.
        
        Args:
            session: Sessão HTTP ativa
            termo: Termo para análise
            dias: Quantidade de dias para análise
            
        Returns:
            Dicionário com métricas de tendência
        """
        try:
            # Coleta dados históricos do Redis
            historico_key = f"instagram:historico:{termo}"
            hoje = datetime.utcnow().date()
            
            # Estrutura para armazenar métricas diárias
            metricas_diarias = {}
            
            # Coleta dados dos últimos X dias
            for index in range(dias):
                data = (hoje - timedelta(days=index)).isoformat()
                metricas_raw = await self.redis.hget(historico_key, data)
                
                if metricas_raw:
                    metricas_diarias[data] = json.loads(metricas_raw)
            
            # Se não tiver dados suficientes, coleta novos
            if len(metricas_diarias) < dias:
                # Coleta métricas atuais
                metricas_atuais = await self._coletar_metricas_hashtag(session, termo.replace("#", ""))
                if metricas_atuais:
                    data_atual = hoje.isoformat()
                    metricas_diarias[data_atual] = metricas_atuais
                    
                    # Salva no Redis
                    await self.redis.hset(
                        historico_key,
                        data_atual,
                        json.dumps(metricas_atuais)
                    )
            
            # Analisa tendências
            if not metricas_diarias:
                return {
                    "crescimento_posts": 0,
                    "crescimento_engagement": 0,
                    "tendencia": "estável",
                    "sazonalidade": None
                }
            
            # Calcula crescimento
            datas = sorted(metricas_diarias.keys())
            if len(datas) >= 2:
                primeiro_dia = metricas_diarias[datas[0]]
                ultimo_dia = metricas_diarias[datas[-1]]
                
                # Crescimento de posts
                crescimento_posts = (
                    (ultimo_dia["total_posts"] - primeiro_dia["total_posts"]) /
                    primeiro_dia["total_posts"] * 100
                    if primeiro_dia["total_posts"] > 0 else 0
                )
                
                # Crescimento de engagement
                engagement_primeiro = (
                    primeiro_dia["media_likes"] + primeiro_dia["media_comentarios"]
                )
                engagement_ultimo = (
                    ultimo_dia["media_likes"] + ultimo_dia["media_comentarios"]
                )
                crescimento_engagement = (
                    (engagement_ultimo - engagement_primeiro) /
                    engagement_primeiro * 100
                    if engagement_primeiro > 0 else 0
                )
                
                # Determina tendência
                if crescimento_posts > 20 and crescimento_engagement > 20:
                    tendencia = "alta"
                elif crescimento_posts < -20 and crescimento_engagement < -20:
                    tendencia = "baixa"
                else:
                    tendencia = "estável"
                
                # Analisa sazonalidade
                sazonalidade = self._detectar_sazonalidade(metricas_diarias)
                
                return {
                    "crescimento_posts": round(crescimento_posts, 2),
                    "crescimento_engagement": round(crescimento_engagement, 2),
                    "tendencia": tendencia,
                    "sazonalidade": sazonalidade
                }
            
            return {
                "crescimento_posts": 0,
                "crescimento_engagement": 0,
                "tendencia": "estável",
                "sazonalidade": None
            }
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao analisar tendências temporais",
                {"erro": str(e)}
            )
            return {
                "crescimento_posts": 0,
                "crescimento_engagement": 0,
                "tendencia": "estável",
                "sazonalidade": None
            }

    def _detectar_sazonalidade(self, metricas_diarias: Dict) -> Optional[str]:
        """Detecta padrões de sazonalidade nas métricas."""
        try:
            # Agrupa por dia da semana
            metricas_dia_semana = {}
            for data, metricas in metricas_diarias.items():
                dia = datetime.fromisoformat(data).weekday()
                if dia not in metricas_dia_semana:
                    metricas_dia_semana[dia] = []
                metricas_dia_semana[dia].append(metricas["total_posts"])
            
            # Calcula média por dia da semana
            medias = {}
            for dia, valores in metricas_dia_semana.items():
                if valores:
                    medias[dia] = sum(valores) / len(valores)
            
            if not medias:
                return None
            
            # Encontra dia com maior média
            dia_pico = max(medias.items(), key=lambda value: value[1])[0]
            
            # Mapeia dia da semana
            dias = {
                0: "segunda-feira",
                1: "terça-feira",
                2: "quarta-feira",
                3: "quinta-feira",
                4: "sexta-feira",
                5: "sábado",
                6: "domingo"
            }
            
            return dias[dia_pico]
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao detectar sazonalidade",
                {"erro": str(e)}
            )
            return None

    async def _coletar_metricas_hashtag(
        self,
        session: aiohttp.ClientSession,
        hashtag: str
    ) -> Optional[Dict]:
        """Coleta métricas de uma hashtag específica."""
        try:
            # Verifica cache primeiro
            cache_key = f"hashtag_metrics:{hashtag}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            params = {
                "query_hash": "9b498c08113f1e09617a1703c22b2f32",
                "variables": json.dumps({
                    "tag_name": hashtag
                })
            }
            
            async with session.get(
                self.graphql_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    hashtag_data = data.get("data", {}).get("hashtag", {})
                    
                    # Coleta dados de Reels e Stories
                    reels = await self._coletar_reels(session, hashtag)
                    stories = await self._coletar_stories(session, hashtag)
                    
                    # Coleta comentários dos top posts para análise de sentimento
                    comentarios = []
                    for post in hashtag_data.get("edge_hashtag_to_top_posts", {}).get("edges", [])[:5]:
                        media_id = post.get("node", {}).get("id")
                        if media_id:
                            comentarios.extend(await self._coletar_comentarios(session, media_id))
                    
                    # Análise de sentimento
                    sentimento = await self._analisar_sentimento(comentarios)
                    
                    # Análise de tendências
                    tendencias = await self._analisar_tendencias_temporais(session, hashtag)
                    
                    metricas = {
                        "total_posts": hashtag_data.get("edge_hashtag_to_media", {}).get("count", 0),
                        "total_seguidores": hashtag_data.get("edge_hashtag_to_content_advisory", {}).get("count", 0),
                        "media_likes": hashtag_data.get("edge_hashtag_to_top_posts", {}).get("average_likes", 0),
                        "media_comentarios": hashtag_data.get("edge_hashtag_to_top_posts", {}).get("average_comments", 0),
                        "sentiment_score": sentimento["sentiment_score"],
                        "comentarios_positivos": sentimento["positivos"],
                        "comentarios_negativos": sentimento["negativos"],
                        "comentarios_neutros": sentimento["neutros"],
                        "total_reels": len(reels),
                        "media_views_reels": sum(r["views"] for r in reels) / len(reels) if reels else 0,
                        "total_stories": len(stories),
                        "media_views_stories": sum(string_data["views"] for string_data in stories) / len(stories) if stories else 0,
                        "crescimento_posts": tendencias["crescimento_posts"],
                        "crescimento_engagement": tendencias["crescimento_engagement"],
                        "tendencia": tendencias["tendencia"],
                        "dia_pico": tendencias["sazonalidade"]
                    }
                    
                    # Atualiza cache com TTL dinâmico
                    await self.cache.set(cache_key, metricas)
                    
                    # Atualiza contadores de popularidade no Redis
                    await self.redis.zincrby("instagram:popularidade", 1, hashtag)
                    
                    return metricas
                    
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar métricas de hashtag",
                {"erro": str(e)}
            )
            
        return None

    async def _coletar_metricas_perfil(
        self,
        session: aiohttp.ClientSession,
        username: str
    ) -> Optional[Dict]:
        """Coleta métricas de um perfil específico."""
        try:
            params = {
                "query_hash": "c9100bf9110dd6361671f113dd02e7d6",
                "variables": json.dumps({
                    "username": username
                })
            }
            
            async with session.get(
                self.graphql_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    user_data = data.get("data", {}).get("user", {})
                    
                    return {
                        "total_posts": user_data.get("edge_owner_to_timeline_media", {}).get("count", 0),
                        "total_seguidores": user_data.get("edge_followed_by", {}).get("count", 0),
                        "total_seguindo": user_data.get("edge_follow", {}).get("count", 0),
                        "media_likes": user_data.get("edge_owner_to_timeline_media", {}).get("average_likes", 0),
                        "media_comentarios": user_data.get("edge_owner_to_timeline_media", {}).get("average_comments", 0),
                        "engajamento": user_data.get("edge_owner_to_timeline_media", {}).get("engagement_rate", 0)
                    }
                    
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar métricas de perfil",
                {"erro": str(e)}
            )
            
        return None

    async def _coletar_comentarios(
        self,
        session: aiohttp.ClientSession,
        media_id: str
    ) -> List[str]:
        """Coleta comentários de uma mídia específica."""
        try:
            params = {
                "query_hash": "bc3296d1ce80a24b1b6e40b1e72903f5",
                "variables": json.dumps({
                    "shortcode": media_id,
                    "first": self.max_comments_analyze
                })
            }
            
            async with session.get(
                f"{self.api_url}/media/{media_id}/comments",
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    comments = []
                    
                    for edge in data.get("data", {}).get("shortcode_media", {}).get("edge_media_to_comment", {}).get("edges", []):
                        comment = edge.get("node", {}).get("text", "")
                        if comment:
                            comments.append(comment)
                    
                    return comments
                    
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar comentários",
                {"erro": str(e)}
            )
            
        return []

    def _extrair_keywords_texto(self, texto: str) -> List[str]:
        """
        Extrai keywords relevantes de um texto usando o normalizador central.
        
        Args:
            texto: Texto para extrair keywords
            
        Returns:
            Lista de keywords extraídas e normalizadas
        """
        # Remove caracteres especiais e divide em palavras
        palavras = re.findall(r'[#@]?\w+', texto.lower())
        
        # Remove stopwords e palavras muito curtas
        palavras_filtradas = [
            p for p in palavras 
            if len(p) > 3 and p not in self.config.get("stopwords", [])
        ]
        
        # Usa o normalizador central para normalizar e remover duplicatas
        return self.normalizador.normalizar_lista_termos(palavras_filtradas)

def coletar_posts(usuario: str, senha: str) -> list:
    """
    Realiza login, coleta e armazena posts do Instagram para um usuário.
    Args:
        usuario (str): Usuário do Instagram
        senha (str): Senha do Instagram
    Returns:
        list: Lista de posts normalizados
    """
    assert isinstance(usuario, str) and usuario, "usuario deve ser string não vazia"
    assert isinstance(senha, str) and senha, "senha deve ser string não vazia"
    # Exemplo de integração com módulos extraídos (comentado para evitar erro se não implementado)
    # sessao = autenticar_usuario(usuario, senha)
    # posts_brutos = ... # lógica de scraping/coleta
    # posts = [parse_post(p) for p in posts_brutos]
    # for post in posts:
    #     salvar_post(post)
    # return posts
    # Placeholder para simulação
    return [{"id": "mock_id", "media_url": "mock_url", "caption": "", "timestamp": "2024-01-01T00:00:00Z"}] 