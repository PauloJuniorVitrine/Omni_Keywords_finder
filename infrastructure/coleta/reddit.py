"""
Implementação do coletor de keywords do Reddit com autenticação OAuth e análise de sentimento.
"""
from typing import List, Dict, Optional
import aiohttp
import asyncio
from datetime import datetime, timedelta
import base64
from bs4 import BeautifulSoup
import re
from textblob import TextBlob
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import get_config, REDDIT_CONFIG
from shared.logger import logger
from shared.cache import AsyncCache
from shared.utils.normalizador_central import NormalizadorCentral
from infrastructure.processamento.validador_keywords import ValidadorKeywords
import time
import uuid
# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

class RedditColetor(KeywordColetorBase):
    """Implementação do coletor de keywords do Reddit com análise avançada."""

    def __init__(self, cache=None, logger_=None):
        """
        Inicializa o coletor com configurações específicas.
        Permite injeção de cache e logger para testes e rastreabilidade.
        Args:
            cache: Instância de cache assíncrono (opcional)
            logger_: Logger customizado (opcional)
        """
        config = get_config("coletores.reddit")
        if config is None:
            config = REDDIT_CONFIG
        super().__init__(
            nome="reddit",
            config=config
        )
        self.base_url = "https://www.reddit.com"
        self.api_url = "https://oauth.reddit.com"
        self.auth_url = "https://www.reddit.com/api/v1/access_token"
        self.headers = {
            "User-Agent": "OmniKeywordsFinder/1.0 (by /u/OmniKeywordsFinder)"
        }
        self.session = None
        self.cache = cache if cache is not None else AsyncCache(
            namespace="reddit",
            ttl=self.config.get("cache_ttl", 3600)  # 1 hora padrão
        )
        self.logger = logger_ if logger_ is not None else logger
        # Normalizador central para padronização de keywords
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-,.!?@#]+$',
            min_caracteres=3,
            max_caracteres=100
        )
        self._access_token = None
        self._token_expiry = None
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()

    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para Reddit API
        self.reddit_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="reddit_api",
                fallback_function=self._fallback_reddit_error
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
            name="reddit_coletor"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=30.0,
            name="reddit_coletor"
        )

    def _fallback_reddit_error(self, *args, **kwargs):
        """Fallback quando Reddit API falha"""
        logger.warning("Reddit API falhou, usando fallback")
        return {"error": "Reddit indisponível", "fallback": True}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP autenticada."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
            await self._autenticar()
        elif self._precisa_reautenticar():
            await self._autenticar()
        return self.session

    async def _autenticar(self) -> None:
        """Realiza autenticação OAuth no Reddit."""
        try:
            credentials = self.config.get("credentials", {})
            if not credentials:
                raise ValueError("Credenciais não configuradas")
                
            client_auth = base64.b64encode(
                f"{credentials['client_id']}:{credentials['client_secret']}".encode()
            ).decode()
            
            headers = {
                **self.headers,
                "Authorization": f"Basic {client_auth}"
            }
            
            data = {
                "grant_type": "password",
                "username": credentials["username"],
                "password": credentials["password"]
            }
            
            async with self.session.post(
                self.auth_url,
                headers=headers,
                data=data
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro na autenticação: {response.status}")
                    
                auth_data = await response.json()
                self._access_token = auth_data["access_token"]
                self._token_expiry = datetime.utcnow() + timedelta(
                    seconds=auth_data["expires_in"]
                )
                
                # Atualiza headers com token
                self.headers.update({
                    "Authorization": f"Bearer {self._access_token}"
                })
                
        except Exception as e:
            self.registrar_erro(
                "Erro durante autenticação no Reddit",
                {"erro": str(e)}
            )
            raise

    def _precisa_reautenticar(self) -> bool:
        """Verifica se é necessário reautenticar."""
        if not self._access_token or not self._token_expiry:
            return True
            
        # Renova se faltar menos de 5 minutos para expirar
        return datetime.utcnow() + timedelta(minutes=5) >= self._token_expiry

    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=8, max_wait_duration=5.0)
    @timeout(timeout_seconds=30.0)
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de busca do Reddit com resiliência e logging estruturado.
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
                "q": termo,
                "type": ["sr", "link"],
                "limit": 25
            }
            async with session.get(
                f"{self.api_url}/api/search_reddit_names",
                params=params
            ) as response:
                if response.status != 200:
                    self.logger.error({
                        "uuid": uuid_req,
                        "coletor": "reddit",
                        "termo": termo,
                        "status": "erro_http",
                        "http_status": response.status,
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev")
                    })
                    return []
                data = await response.json()
                sugestoes = []
                for subreddit in data.get("subreddits", []):
                    nome = subreddit.get("name", "").strip()
                    if nome and nome.lower() != termo.lower():
                        sugestoes.append(f"r/{nome}")
                async with session.get(
                    f"{self.api_url}/search",
                    params={"q": termo, "limit": 100}
                ) as response2:
                    if response2.status == 200:
                        posts = await response2.json()
                        for post in posts.get("data", {}).get("children", []):
                            titulo = post["data"].get("title", "")
                            palavras = re.findall(r'\w+', titulo.lower())
                            for palavra in palavras:
                                if (
                                    len(palavra) > 3 and
                                    palavra != termo.lower() and
                                    palavra not in sugestoes
                                ):
                                    sugestoes.append(palavra)
                await self.cache.set(cache_key, sugestoes)
                self.logger.info({
                    "uuid": uuid_req,
                    "coletor": "reddit",
                    "termo": termo,
                    "status": "sucesso",
                    "latencia_ms": int((time.time() - inicio) * 1000),
                    "ambiente": self.config.get("env", "dev"),
                    "total_sugestoes": len(sugestoes)
                })
                if not sugestoes:
                    self.logger.info({
                        "uuid": uuid_req,
                        "coletor": "reddit",
                        "termo": termo,
                        "status": "nenhuma_sugestao",
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev")
                    })
                return sugestoes
        except Exception as e:
            self.logger.error({
                "uuid": uuid_req,
                "coletor": "reddit",
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
        Extrai métricas específicas do Reddit.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do Reddit
        """
        cache_key = f"metricas:{termo}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        try:
            session = await self._get_session()
            params = {
                "q": termo,
                "limit": 100
            }
            async with session.get(
                f"{self.api_url}/search",
                params=params
            ) as response:
                if response.status != 200:
                    logger.error(f"Erro ao acessar métricas do Reddit: status {response.status}")
                    return {}
                data = await response.json()
                posts = data.get("data", {}).get("children", [])
                if not posts:
                    logger.info(f"Nenhum post encontrado para termo: {termo}")
                    return {}
                metricas = {
                    "total_posts": len(posts),
                    "media_score": sum(p["data"].get("score", 0) for p in posts) / max(len(posts), 1),
                    "media_comentarios": sum(p["data"].get("num_comments", 0) for p in posts) / max(len(posts), 1)
                }
                await self.cache.set(cache_key, metricas)
                logger.info(f"Métricas extraídas para termo: {termo}")
                return metricas

        except Exception as e:
            logger.error(f"Erro ao extrair métricas do Reddit: {e}")
            return {}

    async def _extrair_dados_posts(self, posts: List[Dict]) -> List[Dict]:
        """Extrai dados relevantes dos posts."""
        dados = []
        
        for post in posts:
            post_data = post.get("data", {})
            dados.append({
                "id": post_data.get("id", ""),
                "titulo": post_data.get("title", ""),
                "subreddit": post_data.get("subreddit", ""),
                "autor": post_data.get("author", ""),
                "score": post_data.get("score", 0),
                "upvote_ratio": post_data.get("upvote_ratio", 0.0),
                "num_comments": post_data.get("num_comments", 0),
                "created_utc": post_data.get("created_utc", 0)
            })
            
        return dados

    async def _extrair_dados_subreddits(self, posts: List[Dict]) -> Dict[str, Dict]:
        """Extrai e agrega dados dos subreddits."""
        subreddits = {}
        
        for post in posts:
            subreddit = post.get("data", {}).get("subreddit", "")
            if not subreddit:
                continue
                
            if subreddit not in subreddits:
                # Busca dados do subreddit
                try:
                    session = await self._get_session()
                    async with session.get(
                        f"{self.api_url}/r/{subreddit}/about"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            subreddits[subreddit] = {
                                "nome": subreddit,
                                "titulo": data.get("data", {}).get("title", ""),
                                "descricao": data.get("data", {}).get("description", ""),
                                "subscribers": data.get("data", {}).get("subscribers", 0),
                                "posts": 1
                            }
                        else:
                            subreddits[subreddit] = {
                                "nome": subreddit,
                                "posts": 1
                            }
                except Exception:
                    subreddits[subreddit] = {
                        "nome": subreddit,
                        "posts": 1
                    }
            else:
                subreddits[subreddit]["posts"] += 1
                
        return subreddits

    async def _analisar_sentimento_posts(self, posts: List[Dict]) -> Dict:
        """Analisa sentimento dos posts e comentários."""
        try:
            textos = []
            
            # Coleta textos dos posts
            for post in posts:
                post_data = post.get("data", {})
                textos.append(post_data.get("title", ""))
                textos.append(post_data.get("selftext", ""))
                
                # Coleta comentários do post
                try:
                    session = await self._get_session()
                    async with session.get(
                        f"{self.api_url}/comments/{post_data.get('id')}",
                        params={"limit": 100}
                    ) as response:
                        if response.status == 200:
                            comentarios = await response.json()
                            for comentario in comentarios[1].get("data", {}).get("children", []):
                                texto = comentario.get("data", {}).get("body", "")
                                if texto:
                                    textos.append(texto)
                except Exception:
                    pass
                    
            # Analisa sentimento
            total_textos = len(textos)
            if total_textos == 0:
                return {
                    "polaridade": 0,
                    "subjetividade": 0,
                    "positivos": 0,
                    "negativos": 0,
                    "neutros": 0
                }
                
            polaridade_total = 0
            subjetividade_total = 0
            positivos = 0
            negativos = 0
            neutros = 0
            
            for texto in textos:
                analise = TextBlob(texto)
                polaridade = analise.sentiment.polarity
                subjetividade = analise.sentiment.subjectivity
                
                polaridade_total += polaridade
                subjetividade_total += subjetividade
                
                if polaridade > 0.1:
                    positivos += 1
                elif polaridade < -0.1:
                    negativos += 1
                else:
                    neutros += 1
                    
            return {
                "polaridade": polaridade_total / total_textos,
                "subjetividade": subjetividade_total / total_textos,
                "positivos": positivos,
                "negativos": negativos,
                "neutros": neutros
            }
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao analisar sentimento",
                {"erro": str(e)}
            )
            return {
                "polaridade": 0,
                "subjetividade": 0,
                "positivos": 0,
                "negativos": 0,
                "neutros": 0
            }

    def _calcular_volume(self, metricas: Dict) -> int:
        """Calcula volume estimado baseado nas métricas."""
        total_posts = metricas.get("total_posts", 0)
        if total_posts == 0:
            return 10
        elif total_posts < 10:
            return 30
        elif total_posts < 50:
            return 100
        elif total_posts < 200:
            return 300
        else:
            return 1000

    def _calcular_concorrencia(self, metricas: Dict) -> float:
        """Calcula nível de concorrência baseado nas métricas."""
        try:
            # Base na quantidade de posts
            total_posts = metricas.get("total_posts", 0)
            if total_posts == 0:
                return 0.1
                
            # Ajusta baseado no engajamento
            posts_data = metricas.get("posts", {})
            media_score = posts_data.get("media_score", 0)
            media_comentarios = posts_data.get("media_comentarios", 0)
            
            # Normaliza métricas
            score_norm = min(1.0, media_score / 1000)
            comentarios_norm = min(1.0, media_comentarios / 100)
            
            # Combina fatores
            concorrencia = min(1.0, (
                (total_posts / 200) * 0.4 +     # Peso dos posts
                score_norm * 0.3 +              # Peso do score
                comentarios_norm * 0.3          # Peso dos comentários
            ))
            
            return max(0.1, concorrencia)
            
        except Exception:
            return 0.5

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o Reddit, usando ValidadorKeywords.
        Retorna False imediatamente se o termo for vazio ou None.
        """
        if not termo or not termo.strip():
            self.registrar_erro(
                "Termo inválido para Reddit",
                {"termo": termo, "motivo": "vazio"}
            )
            logger.error(f"Termo inválido para Reddit: {termo}")
            return False
        if len(termo) > 250:
            self.registrar_erro(
                "Termo muito longo para Reddit",
                {"termo": termo}
            )
            logger.error(f"Termo muito longo para Reddit: {termo}")
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
        Coleta keywords relacionadas do Reddit.
        
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
                # 1. Coleta de subreddits relacionados
                params = {
                    "q": termo,
                    "type": "sr",
                    "sort": "relevance",
                    "limit": limite // 2
                }
                
                async with session.get(
                    self.search_url,
                    params=params,
                    proxy=self.config.get("proxy")
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Extrai subreddits relacionados
                        for subreddit in soup.find_all("a", {"class": "subreddit"}):
                            nome = subreddit.get_text().strip()
                            if nome and nome != termo:
                                keyword = Keyword(
                                    termo=nome,
                                    fonte=self.nome,
                                    data_coleta=self.obter_data_atual(),
                                    score_relevancia=self.calcular_relevancia(nome, termo)
                                )
                                keywords.append(keyword)
                
                # 2. Coleta de títulos e tags populares
                params = {
                    "q": termo,
                    "sort": "relevance",
                    "t": "month",
                    "limit": limite // 2
                }
                
                async with session.get(
                    self.search_url,
                    params=params,
                    proxy=self.config.get("proxy")
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Extrai títulos e tags
                        termos = set()
                        for post in soup.find_all("div", {"class": "thing"}):
                            # Extrai título
                            titulo = post.find("a", {"class": "title"})
                            if titulo:
                                termos.add(titulo.get_text().strip())
                            
                            # Extrai flair/tags
                            flair = post.find("span", {"class": "flair"})
                            if flair:
                                termos.add(flair.get_text().strip())
                        
                        for termo_encontrado in termos:
                            if termo_encontrado and termo_encontrado != termo:
                                keyword = Keyword(
                                    termo=termo_encontrado,
                                    fonte=self.nome,
                                    data_coleta=self.obter_data_atual(),
                                    score_relevancia=self.calcular_relevancia(termo_encontrado, termo)
                                )
                                if len(keyword.termo.split()) >= 3 and len(keyword.termo) >= 15:
                                    keywords.append(keyword)

            self.atualizar_metricas(len(keywords))
            self.registrar_sucesso("coleta_keywords", {
                "termo_base": termo,
                "total_coletado": len(keywords)
            })
            
            return keywords[:limite]

        except Exception as e:
            self.registrar_erro(
                "Erro durante coleta do Reddit",
                {"erro": str(e)}
            )
            return []

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """
        Coleta métricas adicionais para as keywords.
        
        Args:
            keywords: Lista de keywords para coletar métricas
            
        Returns:
            Lista de dicionários com métricas por keyword
        """
        metricas = []
        
        for keyword in keywords:
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    # Tenta primeiro como subreddit
                    url = f"{self.subreddit_url}/{keyword}"
                    async with session.get(
                        url,
                        proxy=self.config.get("proxy")
                    ) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, "html.parser")
                            
                            # Extrai métricas do subreddit
                            membros = 0
                            online = 0
                            
                            membros_div = soup.find("div", {"class": "subscribers"})
                            if membros_div:
                                membros_texto = membros_div.get_text().strip()
                                membros = int(''.join(filter(str.isdigit, membros_texto)) or 0)
                            
                            online_div = soup.find("div", {"class": "users-online"})
                            if online_div:
                                online_texto = online_div.get_text().strip()
                                online = int(''.join(filter(str.isdigit, online_texto)) or 0)
                            
                            metricas.append({
                                "keyword": keyword,
                                "tipo": "subreddit",
                                "membros": membros,
                                "usuarios_online": online
                            })
                        else:
                            # Se não é subreddit, busca como termo
                            params = {
                                "q": keyword,
                                "sort": "relevance",
                                "t": "month"
                            }
                            
                            async with session.get(
                                self.search_url,
                                params=params,
                                proxy=self.config.get("proxy")
                            ) as response:
                                if response.status == 200:
                                    html = await response.text()
                                    soup = BeautifulSoup(html, "html.parser")
                                    
                                    # Conta resultados e engajamento
                                    posts = soup.find_all("div", {"class": "thing"})
                                    total_posts = len(posts)
                                    total_score = 0
                                    total_comentarios = 0
                                    
                                    for post in posts:
                                        score_div = post.find("div", {"class": "score"})
                                        if score_div:
                                            score = int(''.join(filter(str.isdigit, score_div.get_text())) or 0)
                                            total_score += score
                                        
                                        comentarios_link = post.find("a", {"class": "comments"})
                                        if comentarios_link:
                                            comentarios = int(''.join(filter(str.isdigit, comentarios_link.get_text())) or 0)
                                            total_comentarios += comentarios
                                    
                                    metricas.append({
                                        "keyword": keyword,
                                        "tipo": "termo",
                                        "total_posts": total_posts,
                                        "media_score": total_score / max(1, total_posts),
                                        "media_comentarios": total_comentarios / max(1, total_posts)
                                    })
                
                # Respeita rate limiting
                await asyncio.sleep(self.config.get("delay_entre_requisicoes", 1))

            except Exception as e:
                self.registrar_erro(
                    f"Erro ao coletar métricas para {keyword}",
                    {"erro": str(e)}
                )
                metricas.append({
                    "keyword": keyword,
                    "erro": str(e)
                })

        return metricas

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """
        Classifica a intenção de busca das keywords.
        
        Args:
            keywords: Lista de keywords para classificar
            
        Returns:
            Lista de enums IntencaoBusca para cada keyword
        """
        intencoes = []
        
        for keyword in keywords:
            # Análise heurística específica para Reddit
            keyword_lower = keyword.lower()
            
            if any(termo in keyword_lower for termo in ["how", "como", "help", "ajuda", "tutorial"]):
                intencao = IntencaoBusca.INFORMACIONAL
            elif any(termo in keyword_lower for termo in ["vs", "versus", "review", "análise", "melhor"]):
                intencao = IntencaoBusca.COMPARACAO
            elif any(termo in keyword_lower for termo in ["buy", "comprar", "price", "preço", "where", "onde"]):
                intencao = IntencaoBusca.TRANSACIONAL
            else:
                intencao = IntencaoBusca.NAVEGACIONAL
                
            intencoes.append(intencao)
            
        return intencoes 