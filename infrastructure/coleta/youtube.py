"""
Implementação do coletor de keywords do YouTube.
"""
from typing import List, Dict, Optional
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote, parse_qs, urlparse
import re
from textblob import TextBlob
from youtube_transcript_api import YouTubeTranscriptApi
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    YOUTUBE_CONFIG,
    CACHE_CONFIG,
    SENTIMENT_CONFIG,
    TRENDS_CONFIG
)
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.logger import logger
from shared.utils.normalizador_central import NormalizadorCentral
from infrastructure.processamento.validador_keywords import ValidadorKeywords
import time
import uuid
# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

class YouTubeColetor(KeywordColetorBase):
    """Implementação do coletor de keywords do YouTube."""

    def __init__(self, cache=None, logger_=None):
        """
        Inicializa o coletor com configurações específicas.
        Permite injeção de cache e logger para testes e rastreabilidade.
        Args:
            cache: Instância de cache assíncrono (opcional)
            logger_: Logger customizado (opcional)
        """
        super().__init__(
            nome="youtube",
            config=YOUTUBE_CONFIG
        )
        self.base_url = "https://www.youtube.com"
        self.search_url = f"{self.base_url}/results"
        self.suggest_url = f"{self.base_url}/complete/search"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.session = None
        self.cache = cache if cache is not None else CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["youtube"],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"],
            ttl_min=CACHE_CONFIG["ttl_min"],
            ttl_max=CACHE_CONFIG["ttl_max"],
            janela_analise=TRENDS_CONFIG["janela_analise"]
        )
        self.logger = logger_ if logger_ is not None else logger
        self.analisador = AnalisadorTendencias(
            janela_analise=TRENDS_CONFIG["janela_analise"]
        )
        # Normalizador central para padronização de keywords
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-,.!?@#]+$',
            min_caracteres=3,
            max_caracteres=100
        )
        self.max_videos_transcricao = self.config.get("max_videos_transcricao", 5)
        self.min_palavras_topico = self.config.get("min_palavras_topico", 3)
        self.max_topicos = self.config.get("max_topicos", 10)
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()

    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para YouTube API
        self.youtube_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="youtube_api",
                fallback_function=self._fallback_youtube_error
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
            max_concurrent_calls=10,
            max_wait_duration=5.0,
            max_failure_count=3,
            name="youtube_coletor"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=30.0,
            name="youtube_coletor"
        )

    def _fallback_youtube_error(self, *args, **kwargs):
        """Fallback quando YouTube API falha"""
        logger.warning("YouTube API falhou, usando fallback")
        return {"error": "YouTube indisponível", "fallback": True}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=10, max_wait_duration=5.0)
    @timeout(timeout_seconds=30.0)
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de busca do YouTube com resiliência e logging estruturado.
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
                "client": "youtube",
                "ds": "yt",
                "q": termo
            }
            async with session.get(
                self.suggest_url,
                params=params,
                proxy=self.proxy_config if self.proxy_enabled else None
            ) as response:
                if response.status != 200:
                    self.logger.error({
                        "uuid": uuid_req,
                        "coletor": "youtube",
                        "termo": termo,
                        "status": "erro_http",
                        "http_status": response.status,
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev")
                    })
                    return []
                data = await response.json()
                sugestoes = data[1] if len(data) > 1 else []
                await self.cache.set(cache_key, sugestoes)
                self.logger.info({
                    "uuid": uuid_req,
                    "coletor": "youtube",
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
                "coletor": "youtube",
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
        Extrai métricas específicas do YouTube.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do YouTube
        """
        try:
            # Verifica cache
            cache_key = f"metricas:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            session = await self._get_session()
            params = {"search_query": termo}
            
            async with session.get(
                self.search_url,
                params=params,
                proxy=self.proxy_config if self.proxy_enabled else None
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro ao buscar termo: {response.status}")
                    
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                # Extrai métricas básicas
                total_resultados = self._extrair_total_resultados(soup)
                tipo_conteudo = self._analisar_tipo_conteudo(soup)
                
                # Extrai contadores específicos
                videos_count = len(soup.select("div.video-count"))
                playlists_count = len(soup.select("div.playlist-count"))
                anuncios = len(soup.select("div.ad-badge"))
                
                # Analisa transcrições dos primeiros vídeos
                video_ids = []
                for link in soup.select("a.video-title"):
                    video_id = self._extrair_video_id(link.get("href", ""))
                    if video_id:
                        video_ids.append(video_id)
                        if len(video_ids) >= self.max_videos_transcricao:
                            break
                            
                transcricoes = []
                for video_id in video_ids:
                    transcricao = await self._analisar_transcricao(video_id, termo)
                    if transcricao:
                        transcricoes.append(transcricao)
                        
                # Detecta tópicos nas transcrições
                analise_topicos = await self._detectar_topicos(transcricoes, termo)
                
                metricas = {
                    "total_resultados": total_resultados,
                    "total_videos": videos_count,
                    "total_playlists": playlists_count,
                    "anuncios": anuncios,
                    "tipo_conteudo": tipo_conteudo,
                    "volume": self._calcular_volume(total_resultados),
                    "concorrencia": self._calcular_concorrencia(anuncios, videos_count),
                    "analise_transcricoes": {
                        "total_analisadas": len(transcricoes),
                        "topicos": analise_topicos["topicos_principais"],
                        "palavras_frequentes": analise_topicos["palavras_mais_frequentes"],
                        "sentiment_medio": analise_topicos["sentiment_medio"]
                    }
                }
                
                # Salva no cache com TTL dinâmico
                await self.cache.set(cache_key, metricas)
                
                # Atualiza contadores de popularidade
                await self.cache.zadd(
                    "popularidade",
                    termo,
                    metricas["volume"]
                )
                
                return metricas

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do YouTube",
                {"erro": str(e), "termo": termo}
            )
            return {
                "total_resultados": 0,
                "total_videos": 0,
                "total_playlists": 0,
                "anuncios": 0,
                "tipo_conteudo": "desconhecido",
                "volume": 0,
                "concorrencia": 0.5,
                "analise_transcricoes": {
                    "total_analisadas": 0,
                    "topicos": [],
                    "palavras_frequentes": {},
                    "sentiment_medio": 0
                }
            }

    def _extrair_total_resultados(self, soup: BeautifulSoup) -> int:
        """Extrai total de resultados da busca."""
        try:
            texto = soup.select_one("div.result-count").text
            return int(re.sub(r"\D", "", texto))
        except Exception:
            return 0

    def _analisar_tipo_conteudo(self, soup: BeautifulSoup) -> str:
        """Analisa tipo predominante de conteúdo."""
        tipos = {
            "tutorial": len(soup.find_all(text=re.compile(r"como|tutorial|passo a passo"))),
            "review": len(soup.find_all(text=re.compile(r"review|análise|avaliação"))),
            "gameplay": len(soup.find_all(text=re.compile(r"gameplay|jogando|playthrough"))),
            "vlog": len(soup.find_all(text=re.compile(r"vlog|daily|rotina"))),
            "música": len(soup.find_all(text=re.compile(r"música|clipe|show|ao vivo")))
        }
        
        if not any(tipos.values()):
            return "outros"
            
        return max(tipos.items(), key=lambda value: value[1])[0]

    def _calcular_volume(self, total_resultados: int) -> int:
        """Calcula volume estimado baseado nos resultados."""
        if total_resultados == 0:
            return 10
        elif total_resultados < 1000:
            return 50
        elif total_resultados < 10000:
            return 100
        elif total_resultados < 100000:
            return 500
        else:
            return 1000

    def _calcular_concorrencia(self, anuncios: int, videos_count: int) -> float:
        """Calcula nível de concorrência baseado nas métricas."""
        if videos_count == 0:
            return 0.5
            
        # Considera número de anúncios e vídeos
        score = min((anuncios / max(1, videos_count)) * 2, 1.0)
        
        # Ajusta baseado no volume de vídeos
        if videos_count < 100:
            score *= 0.5
        elif videos_count < 1000:
            score *= 0.7
        elif videos_count < 10000:
            score *= 0.9
            
        return min(score, 1.0)

    def _determinar_intencao(self, termo: str, tipo_conteudo: str) -> IntencaoBusca:
        """Determina intenção de busca baseado no termo e tipo de conteúdo."""
        termo_lower = termo.lower()
        
        if tipo_conteudo == "tutorial" or any(
            palavra in termo_lower
            for palavra in ["como", "tutorial", "aprenda", "passo"]
        ):
            return IntencaoBusca.INFORMACIONAL
            
        elif tipo_conteudo == "review" or any(
            palavra in termo_lower
            for palavra in ["review", "análise", "comparativo", "melhor"]
        ):
            return IntencaoBusca.COMPARACAO
            
        elif any(
            palavra in termo_lower
            for palavra in ["comprar", "preço", "onde", "loja"]
        ):
            return IntencaoBusca.TRANSACIONAL
            
        return IntencaoBusca.NAVEGACIONAL

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o YouTube.
        Retorna False imediatamente se termo for vazio, None, > 100 caracteres ou com caracteres especiais não permitidos.
        """
        if not termo or not termo.strip():
            self.registrar_erro(
                "Termo inválido para YouTube",
                {"termo": termo, "motivo": "vazio"}
            )
            return False
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo para YouTube",
                {"termo": termo}
            )
            return False
        if not re.fullmatch(r'^[\w\string_data\-.,?!]+$', termo):
            self.registrar_erro(
                "Termo contém caracteres especiais não permitidos para YouTube",
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

    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[Keyword]:
        """
        Coleta keywords relacionadas do YouTube.
        
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
            for sugestao in sugestoes:
                if sugestao != termo:
                    metricas = await self.extrair_metricas_especificas(sugestao)
                    
                    keyword = Keyword(
                        termo=sugestao,
                        fonte=self.nome,
                        data_coleta=self.obter_data_atual(),
                        volume_busca=metricas["volume"],
                        concorrencia=metricas["concorrencia"],
                        score_relevancia=self.calcular_relevancia(sugestao, termo),
                        intencao_busca=self._determinar_intencao(
                            sugestao,
                            metricas["tipo_conteudo"]
                        ),
                        metadados={
                            "tipo_conteudo": metricas["tipo_conteudo"],
                            "total_videos": metricas["total_videos"],
                            "total_playlists": metricas["total_playlists"],
                            "analise_transcricoes": metricas["analise_transcricoes"]
                        }
                    )
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
                    
                    # Registra acesso para análise de tendências
                    self.analisador.registrar_acesso(sugestao)
                    
                    # Pequeno delay entre requisições
                    await asyncio.sleep(self.config.get("delay_entre_requisicoes", 1))

            self.atualizar_metricas(len(keywords))
            self.registrar_sucesso("coleta_keywords", {
                "termo_base": termo,
                "total_coletado": len(keywords)
            })
            
            return keywords[:limite]

        except Exception as e:
            self.registrar_erro(
                "Erro durante coleta do YouTube",
                {"erro": str(e)}
            )
            return []

    async def __aenter__(self):
        """Gerenciamento de contexto para início de sessão."""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gerenciamento de contexto para fechamento de sessão."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """Stub mínimo para testes."""
        return [IntencaoBusca.NAVEGACIONAL for _ in keywords]

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """Stub mínimo para testes."""
        return [{} for _ in keywords] 