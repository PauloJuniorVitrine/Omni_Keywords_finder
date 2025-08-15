"""
Implementação do coletor de dados do Google Trends.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
from pytrends.request import TrendReq
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    CACHE_CONFIG,
    TRENDS_CONFIG
)
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.logger import logger
from infrastructure.processamento.validador_keywords import ValidadorKeywords
import time
import uuid
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker
from bs4 import BeautifulSoup
from urllib.parse import quote
import json
from shared.utils.normalizador_central import NormalizadorCentral

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

class GoogleTrendsColetor(KeywordColetorBase):
    """Implementação do coletor de dados do Google Trends."""

    def __init__(self, logger_=None, session=None):
        """Inicializa o coletor com configurações específicas."""
        super().__init__(
            nome="google_trends",
            config=TRENDS_CONFIG
        )
        self.periodo_analise = self.config.get("janela_analise", 90)
        self.pais = self.config.get("pais", "BR")
        self._client = None
        self.session = session
        self.logger = logger_ or logger
        
        # Cache com namespace específico
        self.cache = CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["google_trends"],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"]
        )
        
        # Analisador de tendências
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

    def _get_client(self) -> TrendReq:
        """Obtém ou cria um cliente PyTrends."""
        if not self._client:
            self._client = TrendReq(
                hl='pt-BR',
                tz=360,
                timeout=(10, 25),
                retries=2,
                backoff_factor=0.1
            )
        return self._client

    async def _build_payload(self, termo: str):
        """
        Constrói o payload da requisição de forma assíncrona.
        
        Args:
            termo: Termo para análise
        """
        # Configura período de análise
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=self.periodo_analise)
        timeframe = f"{data_inicio.strftime('%Y-%m-%data')} {data_fim.strftime('%Y-%m-%data')}"
        
        # Executa build_payload em thread separada pois é bloqueante
        await asyncio.to_thread(
            self._get_client().build_payload,
            [termo],
            cat=0,  # Todas as categorias
            timeframe=timeframe,
            geo=self.pais
        )

    @breaker
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError))
    )
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        uuid_req = str(uuid.uuid4())
        inicio = time.time()
        try:
            cache_key = f"sugestoes:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            await self._build_payload(termo)
            related_queries = getattr(self._get_client(), "related_queries", {})
            sugestoes = set()
            dados_queries = {}
            rising = related_queries.get(termo, {}).get('rising', None)
            if isinstance(rising, dict):
                sugestoes.update(rising.keys())
                dados_queries['rising'] = rising
            top = related_queries.get(termo, {}).get('top', None)
            if isinstance(top, dict):
                sugestoes.update(top.keys())
                dados_queries['top'] = top
            await self.cache.set(
                f"queries:{termo}",
                dados_queries,
                ttl=CACHE_CONFIG["ttl_metricas"]
            )
            sugestoes_lista = list(sugestoes)
            await self.cache.set(
                cache_key,
                sugestoes_lista,
                ttl=CACHE_CONFIG["ttl_keywords"]
            )
            self.logger.info({
                "uuid": uuid_req,
                "coletor": "google_trends",
                "termo": termo,
                "status": "sucesso",
                "latencia_ms": int((time.time() - inicio) * 1000),
                "ambiente": self.config.get("env", "dev"),
                "total_sugestoes": len(sugestoes_lista)
            })
            return sugestoes_lista
        except Exception as e:
            self.logger.error({
                "uuid": uuid_req,
                "coletor": "google_trends",
                "termo": termo,
                "status": "erro",
                "erro": str(e),
                "latencia_ms": int((time.time() - inicio) * 1000),
                "ambiente": self.config.get("env", "dev")
            })
            # Fallback: retorna cache ou lista vazia
            return await self.cache.get(f"sugestoes:{termo}") or []

    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        """
        Extrai métricas específicas do Google Trends.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do Trends
        """
        try:
            # Verifica cache
            cache_key = f"metricas:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            # Verifica cache de queries
            dados_queries = await self.cache.get(f"queries:{termo}")
            if not dados_queries:
                # Se não está em cache, busca dados
                await self._build_payload(termo)
                related_queries = self._get_client().related_queries
                dados_queries = {
                    'rising': related_queries.get(termo, {}).get('rising', {}),
                    'top': related_queries.get(termo, {}).get('top', {})
                }
                
                # Salva queries no cache
                await self.cache.set(
                    f"queries:{termo}",
                    dados_queries,
                    ttl=CACHE_CONFIG["ttl_metricas"]
                )
                
            rising = dados_queries.get('rising', {})
            top = dados_queries.get('top', {})
            
            # Calcula métricas
            volume = 0
            crescimento = 0
            
            # Volume baseado em posição no top
            if termo in top:
                posicao = list(top.keys()).index(termo)
                volume = max(10, 100 - (posicao * 10))
                
            # Crescimento baseado em rising
            if termo in rising:
                crescimento = rising[termo]
                
            # Estima concorrência baseada em volume e crescimento
            if crescimento > 5000:  # Crescimento explosivo
                concorrencia = 0.9
            elif crescimento > 1000:
                concorrencia = 0.7
            elif crescimento > 100:
                concorrencia = 0.5
            else:
                concorrencia = 0.3
                
            # Determina intenção
            termo_lower = termo.lower()
            if any(p in termo_lower for p in ['como', 'tutorial', 'guia']):
                intencao = IntencaoBusca.INFORMACIONAL
            elif any(p in termo_lower for p in ['comprar', 'preço', 'onde']):
                intencao = IntencaoBusca.TRANSACIONAL
            elif any(p in termo_lower for p in ['melhor', 'vs', 'comparar']):
                intencao = IntencaoBusca.COMPARACAO
            else:
                intencao = IntencaoBusca.NAVEGACIONAL
                
            metricas = {
                "volume": volume,
                "cpc": 0.0,  # Trends não fornece CPC
                "concorrencia": concorrencia,
                "intencao": intencao,
                "crescimento": crescimento,
                "tendencia": self.analisador.calcular_tendencia(termo)
            }
            
            # Salva no cache
            await self.cache.set(
                cache_key,
                metricas,
                ttl=CACHE_CONFIG["ttl_metricas"]
            )
            
            # Registra acesso para análise de tendências
            self.analisador.registrar_acesso(termo)
            
            return metricas

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do Google Trends",
                {"erro": str(e), "termo": termo}
            )
            return {
                "volume": 0,
                "cpc": 0.0,
                "concorrencia": 0.5,
                "intencao": IntencaoBusca.NAVEGACIONAL,
                "crescimento": 0,
                "tendencia": 0
            }

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o Google Trends, usando ValidadorKeywords.
        """
        if not termo or len(termo) > 100:
            self.registrar_erro(
                "Termo inválido para Google Trends",
                {"termo": termo, "motivo": "tamanho"}
            )
            self.logger.error(f"Termo inválido para Google Trends: {termo}")
            return False
        if len(termo.split()) < 2:
            self.registrar_erro(
                "Termo muito genérico para Google Trends",
                {"termo": termo}
            )
            self.logger.error(f"Termo muito genérico para Google Trends: {termo}")
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
        Implementação específica de coleta de keywords do Trends.
        
        Args:
            termo: Termo base para busca
            limite: Número máximo de keywords a retornar
            
        Returns:
            Lista de objetos Keyword com dados do Trends
        """
        if not await self.validar_termo(termo) or not await self.validar_termo_especifico(termo):
            return []
            
        try:
            # Coleta sugestões relacionadas
            sugestoes = await self.extrair_sugestoes(termo)
            if not sugestoes:
                return []
                
            # Limita quantidade
            sugestoes = sugestoes[:limite]
            
            # Converte sugestões em keywords
            keywords = []
            for sugestao in sugestoes:
                try:
                    metricas = await self.extrair_metricas_especificas(sugestao)
                    keyword = Keyword(
                        termo=sugestao,
                        volume_busca=metricas.get("volume", 0),
                        cpc=metricas.get("cpc", 0.0),
                        concorrencia=metricas.get("concorrencia", 0.5),
                        intencao=metricas.get("intencao"),
                        fonte=self.nome,
                        metadados={
                            "crescimento": metricas.get("crescimento", 0),
                            "tendencia": metricas.get("tendencia", 0)
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
                except Exception as e:
                    self.registrar_erro(
                        f"Erro ao processar sugestao: {sugestao}",
                        {"erro": str(e)}
                    )
                    
            self.registrar_sucesso("coleta_trends", {
                "termo_base": termo,
                "total_sugestoes": len(sugestoes),
                "keywords_geradas": len(keywords)
            })
            
            self.atualizar_metricas(len(keywords))
            return keywords
            
        except Exception as e:
            self.registrar_erro(
                "Erro durante coleta do Trends",
                {"erro": str(e), "termo": termo}
            )
            return []

    async def __aenter__(self):
        """Gerenciamento de contexto para início de sessão."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gerenciamento de contexto para fechamento de sessão."""
        if self._client:
            self._client = None 

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """Stub mínimo para testes."""
        return [IntencaoBusca.NAVEGACIONAL for _ in keywords]

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """Stub mínimo para testes."""
        return [{} for _ in keywords]

    async def coletar(self, termo: str, session=None) -> List[str]:
        """
        Coleta tendências do Google Trends para o termo informado.
        Compatível com os testes unitários.
        Args:
            termo: termo base para busca
            session: sessão aiohttp opcional (para testes/mocks)
        Returns:
            Lista de tendências (strings)
        """
        cache_key = f"trends:{termo}"
        try:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            import aiohttp
            sess = session or self.session or aiohttp.ClientSession()
            close_session = session is None and self.session is None
            try:
                url = "https://trends.google.com/trends/api/dailytrends"
                params = {
                    "hl": "pt-BR",
                    "tz": "-180",
                    "geo": self.pais,
                    "ns": 15,
                    "ed": datetime.now().strftime("%Y%m%data"),
                }
                async with sess.get(url, params=params) as resp:
                    if resp.status != 200:
                        self.registrar_erro(
                            "Erro ao acessar Google Trends",
                            {"status": resp.status, "termo": termo}
                        )
                        return []
                    try:
                        data = await resp.json()
                    except Exception:
                        try:
                            text = await resp.text()
                            import json
                            if text.startswith(")]}'"):
                                text = text[4:]
                            data = json.loads(text)
                        except Exception as e:
                            self.registrar_erro(
                                "Erro ao processar resposta do Google Trends",
                                {"erro": str(e), "termo": termo}
                            )
                            return []
                    trends = []
                    try:
                        days = data.get("default", {}).get("trendingSearchesDays", [])
                        for day in days:
                            for trend in day.get("trendingSearches", []):
                                query = trend.get("title", {}).get("query", "")
                                if query:
                                    trends.append(query)
                        # Incluir sugestões se existirem
                        suggestions = data.get("suggestions", [])
                        for string_data in suggestions:
                            valor = string_data.get("value") if isinstance(string_data, dict) else string_data
                            if valor and valor not in trends:
                                trends.append(valor)
                    except Exception as e:
                        self.registrar_erro(
                            "Erro ao extrair tendências do Google Trends",
                            {"erro": str(e), "termo": termo}
                        )
                        return []
                    await self.cache.set(cache_key, trends)
                    return trends
            except Exception as e:
                self.registrar_erro(
                    "Erro de rede ao acessar Google Trends",
                    {"erro": str(e), "termo": termo}
                )
                return []
            finally:
                if close_session:
                    await sess.close()
        except Exception as e:
            self.registrar_erro(
                "Erro inesperado no método coletar",
                {"erro": str(e), "termo": termo}
            )
            return [] 