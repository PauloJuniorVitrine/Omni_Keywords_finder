"""
Implementação do coletor de keywords do TikTok.
"""
from typing import List, Dict, Optional
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    TIKTOK_CONFIG,
    CACHE_CONFIG,
    SENTIMENT_CONFIG,
    TRENDS_CONFIG
)
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.sentiment import AnalisadorSentimento
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from infrastructure.coleta.utils.music import AnalisadorMusica
from infrastructure.coleta.utils.hashtags import AnalisadorHashtags
from infrastructure.coleta.utils.challenges import AnalisadorDesafios
from shared.logger import logger
from infrastructure.processamento.validador_keywords import ValidadorKeywords
import time
import uuid
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

class TikTokColetor(KeywordColetorBase):
    """Implementação do coletor de keywords do TikTok."""

    def __init__(self, cache=None, logger_=None):
        """
        Inicializa o coletor com configurações específicas.
        Permite injeção de cache e logger para testes e rastreabilidade.
        Args:
            cache: Instância de cache assíncrono (opcional)
            logger_: Logger customizado (opcional)
        """
        super().__init__(
            nome="tiktok",
            config=TIKTOK_CONFIG
        )
        self.base_url = "https://www.tiktok.com"
        self.api_url = f"{self.base_url}/api"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.session = None
        self.cache = cache if cache is not None else CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["tiktok"],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"]
        )
        self.logger = logger_ if logger_ is not None else logger
        self.max_videos = TIKTOK_CONFIG["max_videos"]
        self.max_hashtags = TIKTOK_CONFIG["max_hashtags"]
        self.max_challenges = TIKTOK_CONFIG["max_challenges"]
        self.credentials = TIKTOK_CONFIG["credentials"]
        self.analisador_sentimento = AnalisadorSentimento()
        self.analisador_tendencias = AnalisadorTendencias()
        self.analisador_musica = AnalisadorMusica()
        self.analisador_hashtags = AnalisadorHashtags()
        self.analisador_desafios = AnalisadorDesafios()
        self._auth_token = None
        self._last_auth = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP autenticada."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
            await self._autenticar()
        elif self._precisa_reautenticar():
            await self._autenticar()
        return self.session

    async def _autenticar(self) -> None:
        """Realiza autenticação no TikTok."""
        try:
            if not self.credentials:
                raise ValueError("Credenciais não configuradas")

            async with self.session.post(
                f"{self.api_url}/auth/login/",
                json={
                    "username": self.credentials["username"],
                    "password": self.credentials["password"]
                },
                headers={"X-CSRFToken": await self._get_csrf_token()}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro na autenticação: {response.status}")
                    
                data = await response.json()
                if not data.get("is_logged_in"):
                    raise Exception("Autenticação falhou")
                    
                self._auth_token = response.cookies.get("sessionid")
                self._last_auth = datetime.utcnow()
                
                self.headers.update({
                    "X-TT-Token": data.get("tt_token"),
                    "Cookie": f"sessionid={self._auth_token}"
                })
                
                self.registrar_sucesso(
                    "autenticacao",
                    {"username": self.credentials["username"]}
                )
                
        except Exception as e:
            self.registrar_erro(
                "Erro durante autenticação no TikTok",
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

    @breaker
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError))
    )
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de busca do TikTok com resiliência e logging estruturado.
        """
        uuid_req = str(uuid.uuid4())
        inicio = time.time()
        cache_key = f"sugestoes:{termo}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        try:
            session = await self._get_session()
            params = {
                "keyword": termo,
                "count": 30,
                "from_page": "search"
            }
            async with session.get(
                f"{self.api_url}/search/suggest/",
                params=params,
                proxy=self.proxy_config if self.proxy_enabled else None
            ) as response:
                if response.status != 200:
                    self.logger.error({
                        "uuid": uuid_req,
                        "coletor": "tiktok",
                        "termo": termo,
                        "status": "erro_http",
                        "http_status": response.status,
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev")
                    })
                    return []
                data = await response.json()
                sugestoes = []
                for hashtag in data.get("hashtags", []):
                    nome = hashtag.get("name", "").strip()
                    if nome and nome != termo:
                        sugestoes.append(f"#{nome}")
                for challenge in data.get("challenges", []):
                    nome = challenge.get("title", "").strip()
                    if nome and nome != termo:
                        sugestoes.append(nome)
                for music in data.get("music", []):
                    titulo = music.get("title", "").strip()
                    artista = music.get("author_name", "").strip()
                    if titulo and artista:
                        sugestoes.append(f"{titulo} - {artista}")
                await self.cache.set(
                    cache_key,
                    sugestoes,
                    ttl=CACHE_CONFIG["ttl_keywords"]
                )
                self.logger.info({
                    "uuid": uuid_req,
                    "coletor": "tiktok",
                    "termo": termo,
                    "status": "sucesso",
                    "latencia_ms": int((time.time() - inicio) * 1000),
                    "ambiente": self.config.get("env", "dev"),
                    "total_sugestoes": len(sugestoes)
                })
                return sugestoes
        except Exception as e:
            self.logger.error({
                "uuid": uuid_req,
                "coletor": "tiktok",
                "termo": termo,
                "status": "erro",
                "erro": str(e),
                "latencia_ms": int((time.time() - inicio) * 1000),
                "ambiente": self.config.get("env", "dev")
            })
            # Fallback: retorna cache ou lista vazia
            return await self.cache.get(cache_key) or []

    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        """
        Extrai métricas específicas do TikTok.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do TikTok
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
                    f"{self.api_url}/hashtag/info/",
                    params={"name": hashtag},
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erro ao acessar hashtag: {response.status}")
                        
                    data = await response.json()
                    hashtag_info = data.get("hashtag_info", {})
                    
                    # Registra hashtag para análise
                    await self.analisador_hashtags.registrar_hashtag(
                        hashtag=hashtag,
                        total_videos=hashtag_info.get("video_count", 0),
                        total_views=hashtag_info.get("view_count", 0),
                        categorias=hashtag_info.get("categories", []),
                        relacionadas=hashtag_info.get("related", [])
                    )
                    
                    # Analisa métricas
                    metricas = await self.analisador_hashtags.analisar_hashtag(hashtag)
                    
            elif termo.startswith("@"):
                # Métricas de perfil
                username = termo.replace("@", "")
                async with session.get(
                    f"{self.api_url}/user/info/",
                    params={"username": username},
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erro ao acessar perfil: {response.status}")
                        
                    data = await response.json()
                    user = data.get("user", {})
                    stats = user.get("stats", {})
                    
                    metricas = {
                        "seguidores": stats.get("follower_count", 0),
                        "seguindo": stats.get("following_count", 0),
                        "total_likes": stats.get("heart_count", 0),
                        "total_videos": stats.get("video_count", 0),
                        "tipo": "perfil",
                        "engagement_rate": self._calcular_engagement_rate(stats),
                        "is_verified": user.get("is_verified", False)
                    }
                    
            else:
                # Métricas de busca geral
                async with session.get(
                    f"{self.api_url}/search/general/",
                    params={"keyword": termo},
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erro ao buscar termo: {response.status}")
                        
                    data = await response.json()
                    
                    # Extrai métricas por tipo
                    videos = data.get("videos", [])
                    hashtags = data.get("hashtags", [])
                    challenges = data.get("challenges", [])
                    music = data.get("music", [])
                    
                    # Registra músicas para análise
                    for m in music:
                        await self.analisador_musica.registrar_musica(
                            musica_id=m.get("id"),
                            titulo=m.get("title", ""),
                            artista=m.get("author_name", ""),
                            duracao=m.get("duration", 0),
                            total_videos=m.get("video_count", 0),
                            total_views=m.get("view_count", 0)
                        )
                        
                    # Registra desafios para análise
                    for c in challenges:
                        await self.analisador_desafios.registrar_desafio(
                            desafio_id=c.get("id"),
                            nome=c.get("title", ""),
                            descricao=c.get("desc", ""),
                            total_videos=c.get("video_count", 0),
                            total_views=c.get("view_count", 0),
                            hashtags=c.get("hashtags", []),
                            criador=c.get("author", {}).get("unique_id")
                        )
                        
                    # Analisa tendências
                    tendencias_musica = await self.analisador_musica.analisar_tendencias(
                        [m.get("id") for m in music]
                    )
                    
                    tendencias_desafios = await self.analisador_desafios.analisar_tendencias(
                        min_crescimento=50.0
                    )
                    
                    metricas = {
                        "total_videos": len(videos),
                        "total_hashtags": len(hashtags),
                        "total_challenges": len(challenges),
                        "total_music": len(music),
                        "tipo": "busca",
                        "relevancia": self._calcular_relevancia(len(videos)),
                        "tendencias": {
                            "musicas": tendencias_musica,
                            "desafios": tendencias_desafios
                        }
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
                "Erro ao extrair métricas do TikTok",
                {"erro": str(e), "termo": termo}
            )
            return {
                "volume": 0,
                "concorrencia": 0.5,
                "tipo": "desconhecido",
                "erro": str(e),
                "stats": {}
            }

    def _calcular_engagement_rate(self, stats: Dict) -> float:
        """Calcula taxa de engajamento baseado nos dados."""
        try:
            total_likes = stats.get("heart_count", 0)
            total_videos = stats.get("video_count", 0)
            seguidores = stats.get("follower_count", 1)
            
            if total_videos == 0:
                return 0.0
                
            return (total_likes / total_videos) / seguidores * 100
            
        except Exception:
            return 0.0

    def _calcular_volume(self, metricas: Dict) -> int:
        """Calcula volume estimado baseado nas métricas."""
        if metricas["tipo"] == "hashtag":
            total_videos = metricas.get("total_videos", 0)
            if total_videos == 0:
                return 10
            elif total_videos < 1000:
                return 50
            elif total_videos < 10000:
                return 100
            elif total_videos < 100000:
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
            return metricas.get("total_videos", 0)

    def _calcular_concorrencia(self, metricas: Dict) -> float:
        """Calcula nível de concorrência baseado nas métricas."""
        if metricas["tipo"] == "hashtag":
            videos = metricas.get("total_videos", 0)
            if videos == 0:
                return 0.1
            elif videos < 1000:
                return 0.3
            elif videos < 10000:
                return 0.5
            elif videos < 100000:
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
            return min(metricas.get("total_videos", 0) / 1000, 1.0)

    def _calcular_relevancia(self, total_videos: int) -> float:
        """Calcula score de relevância baseado nos resultados."""
        if total_videos == 0:
            return 0.0
        elif total_videos < 10:
            return 0.2
        elif total_videos < 100:
            return 0.4
        elif total_videos < 1000:
            return 0.6
        elif total_videos < 10000:
            return 0.8
        else:
            return 1.0

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o TikTok, usando ValidadorKeywords.
        Retorna False imediatamente se termo for vazio, None, > 100 caracteres ou com caracteres especiais não permitidos.
        """
        if not termo or not termo.strip():
            self.registrar_erro(
                "Termo inválido para TikTok",
                {"termo": termo, "motivo": "vazio"}
            )
            self.logger.error(f"Termo inválido para TikTok: {termo}")
            return False
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo para TikTok",
                {"termo": termo}
            )
            self.logger.error(f"Termo muito longo para TikTok: {termo}")
            return False
        if not re.fullmatch(r'^[\w\string_data\-.,?!]+$', termo):
            self.registrar_erro(
                "Termo contém caracteres especiais não permitidos",
                {"termo": termo}
            )
            self.logger.error(f"Termo contém caracteres especiais não permitidos para TikTok: {termo}")
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
        Coleta keywords relacionadas do TikTok.
        
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
            # Extrai sugestões
            sugestoes = await self.extrair_sugestoes(termo)
            
            # Coleta métricas para cada sugestão
            for sugestao in sugestoes[:limite]:
                if sugestao != termo:
                    metricas = await self.extrair_metricas_especificas(sugestao)
                    
                    keyword = Keyword(
                        termo=sugestao,
                        fonte=self.nome,
                        data_coleta=self.obter_data_atual(),
                        volume_busca=metricas.get("volume", 0),
                        concorrencia=metricas.get("concorrencia", 0.5),
                        score_relevancia=self._calcular_relevancia(metricas.get("total_videos", 0)),
                        intencao=IntencaoBusca.INFORMACIONAL,
                        metadados={
                            "tipo": metricas.get("tipo", "desconhecido"),
                            "total_videos": metricas.get("total_videos", 0),
                            "total_hashtags": metricas.get("total_hashtags", 0),
                            "total_challenges": metricas.get("total_challenges", 0),
                            "total_music": metricas.get("total_music", 0)
                        }
                    )
                    
                    # Filtro de cauda longa
                    if len(keyword.termo.split()) >= 3 and len(keyword.termo) >= 15 and keyword.concorrencia <= 0.5:
                        keywords.append(keyword)
                    else:
                        self.registrar_sucesso(
                            "descartada_nao_cauda_longa",
                            {
                                "termo": keyword.termo,
                                "motivo": "nao_atende_criterio_cauda_longa",
                                "palavras": len(keyword.termo.split()),
                                "caracteres": len(keyword.termo),
                                "concorrencia": keyword.concorrencia
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
                "Erro durante coleta do TikTok",
                {"erro": str(e)}
            )
            return []

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """Stub mínimo para testes."""
        return [IntencaoBusca.NAVEGACIONAL for _ in keywords]

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """Stub mínimo para testes."""
        return [{} for _ in keywords] 