"""
Implementação do coletor de sugestões do Google com suporte multi-idioma e análise de sazonalidade.
"""
from typing import List, Dict, Optional, Set
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
import re
from urllib.parse import quote
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    CACHE_CONFIG,
    GOOGLE_SUGGEST_CONFIG,
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
from shared.utils.normalizador_central import NormalizadorCentral

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

class GoogleSuggestColetor(KeywordColetorBase):
    """Implementação do coletor de sugestões do Google com análise avançada."""

    def __init__(self, cache=None, logger_=None, session=None):
        """Inicializa o coletor com configurações específicas e dependências injetáveis."""
        super().__init__(
            nome="google_suggest",
            config=GOOGLE_SUGGEST_CONFIG
        )
        self.base_url = "https://suggestqueries.google.com/complete/search"
        self.cache = cache or CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["google_suggest"],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"]
        )
        self.logger = logger_ or logger
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
        self._configuracoes_idiomas = self._carregar_configuracoes_idiomas()
        self._session_lock = asyncio.Lock()
        self.session = session

    @breaker
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError))
    )
    async def extrair_sugestoes(self, termo: str, idioma: str = "pt-BR") -> List[str]:
        """
        Extrai sugestões do Google Suggest com resiliência e logging estruturado.
        """
        uuid_req = str(uuid.uuid4())
        inicio = time.time()
        cache_key = f"sugestoes:{idioma}:{termo}"
        cached = None
        try:
            try:
                cached = await self.cache.get(cache_key)
            except Exception as e_cache:
                self.logger.error({
                    "uuid": uuid_req,
                    "coletor": "google_suggest",
                    "termo": termo,
                    "idioma": idioma,
                    "status": "erro_cache_get",
                    "erro": str(e_cache),
                    "latencia_ms": int((time.time() - inicio) * 1000),
                    "ambiente": self.config.get("env", "dev")
                })
            if cached is not None:
                if isinstance(cached, list):
                    self.logger.info({
                        "uuid": uuid_req,
                        "coletor": "google_suggest",
                        "termo": termo,
                        "idioma": idioma,
                        "status": "cache_hit",
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev"),
                        "total_sugestoes": len(cached)
                    })
                    return cached
            async with self as coletor:
                session = await coletor._get_session()
                config_idioma = self._configuracoes_idiomas.get(idioma, self._configuracoes_idiomas["pt-BR"])
                params = {
                    "client": "chrome",
                    "q": termo,
                    "hl": config_idioma["hl"],
                    "gl": config_idioma["gl"]
                }
                async with session.get(
                    self.base_url,
                    params=params,
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        self.logger.error({
                            "uuid": uuid_req,
                            "coletor": "google_suggest",
                            "termo": termo,
                            "idioma": idioma,
                            "status": "erro_http",
                            "http_status": response.status,
                            "latencia_ms": int((time.time() - inicio) * 1000),
                            "ambiente": self.config.get("env", "dev")
                        })
                        return []
                    data = await response.json()
                    if not data or len(data) < 2:
                        self.logger.error({
                            "uuid": uuid_req,
                            "coletor": "google_suggest",
                            "termo": termo,
                            "idioma": idioma,
                            "status": "resposta_invalida",
                            "latencia_ms": int((time.time() - inicio) * 1000),
                            "ambiente": self.config.get("env", "dev")
                        })
                        return []
                    sugestoes = data[1]
                    if not isinstance(sugestoes, list):
                        self.logger.error({
                            "uuid": uuid_req,
                            "coletor": "google_suggest",
                            "termo": termo,
                            "idioma": idioma,
                            "status": "formato_invalido",
                            "latencia_ms": int((time.time() - inicio) * 1000),
                            "ambiente": self.config.get("env", "dev")
                        })
                        return []
                    sugestoes_processadas = []
                    for sugestao in sugestoes:
                        if isinstance(sugestao, list) and len(sugestao) > 0:
                            sugestoes_processadas.append(sugestao[0])
                        elif isinstance(sugestao, str):
                            sugestoes_processadas.append(sugestao)
                    try:
                        await self.cache.set(
                            cache_key,
                            sugestoes_processadas,
                            ttl=CACHE_CONFIG["ttl_keywords"]
                        )
                    except Exception as e_cache_set:
                        self.logger.error({
                            "uuid": uuid_req,
                            "coletor": "google_suggest",
                            "termo": termo,
                            "idioma": idioma,
                            "status": "erro_cache_set",
                            "erro": str(e_cache_set),
                            "latencia_ms": int((time.time() - inicio) * 1000),
                            "ambiente": self.config.get("env", "dev")
                        })
                    self.logger.info({
                        "uuid": uuid_req,
                        "coletor": "google_suggest",
                        "termo": termo,
                        "idioma": idioma,
                        "status": "sucesso",
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev"),
                        "total_sugestoes": len(sugestoes_processadas)
                    })
                    return sugestoes_processadas
        except Exception as e:
            self.logger.error({
                "uuid": uuid_req,
                "coletor": "google_suggest",
                "termo": termo,
                "idioma": idioma,
                "status": "erro",
                "erro": str(e),
                "latencia_ms": int((time.time() - inicio) * 1000),
                "ambiente": self.config.get("env", "dev")
            })
            # Fallback: retorna lista vazia (nunca await no cache aqui)
            return []

    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[Keyword]:
        """
        Coleta keywords relacionadas ao termo fornecido.
        
        Args:
            termo: Termo base para busca
            limite: Número máximo de keywords a retornar
            
        Returns:
            Lista de objetos Keyword com dados preenchidos
        """
        keywords = []
        
        # Valida o termo
        if not await self.validar_termo(termo):
            return keywords
            
        try:
            # Extrai sugestões
            sugestoes = await self.extrair_sugestoes(termo)
            
            # Processa cada sugestão
            for sugestao in sugestoes[:limite]:
                try:
                    # Coleta métricas
                    metricas = await self.extrair_metricas_especificas(sugestao)
                    
                    # Cria objeto Keyword
                    keyword = Keyword(
                        termo=sugestao,
                        volume_busca=metricas.get("volume", 0),
                        cpc=metricas.get("cpc", 0.0),
                        concorrencia=metricas.get("concorrencia", 0.0),
                        intencao=IntencaoBusca.NAVEGACIONAL
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
                        "Erro ao processar sugestão",
                        {
                            "erro": str(e),
                            "sugestao": sugestao
                        }
                    )
                    continue
            
            # Registra métricas
            self.registrar_sucesso(
                "coleta_suggest",
                {
                    "termo_base": termo,
                    "total_sugestoes": len(sugestoes),
                    "keywords_geradas": len(keywords)
                }
            )
            
            # Atualiza métricas do coletor
            self.atualizar_metricas(len(keywords))
            
            return keywords
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar keywords",
                {
                    "erro": str(e),
                    "termo": termo
                }
            )
            return keywords

    def _carregar_configuracoes_idiomas(self) -> Dict[str, Dict[str, str]]:
        """
        Carrega as configurações de idiomas suportados.
        
        Returns:
            Dicionário com configurações por idioma
        """
        return {
            "pt-BR": {"hl": "pt-BR", "gl": "BR"},
            "en-US": {"hl": "en-US", "gl": "US"},
            "es-ES": {"hl": "es-ES", "gl": "ES"}
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP."""
        async with self._session_lock:
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession(headers=self.headers)
            return self.session

    async def extrair_metricas_especificas(
        self,
        termo: str,
        idioma: str = "pt-BR"
    ) -> Dict:
        """
        Extrai métricas específicas do Google Suggest.
        
        Args:
            termo: Termo para análise
            idioma: Código do idioma
            
        Returns:
            Dicionário com métricas do Google Suggest
        """
        try:
            # Verifica cache
            cache_key = f"metricas:{idioma}:{termo}"
            cached = await self.cache.get(cache_key)
            if cached is not None:
                if isinstance(cached, dict):
                    return cached
                else:
                    self.registrar_erro(
                        "Cache com formato inválido",
                        {
                            "termo": termo,
                            "idioma": idioma,
                            "tipo_cache": type(cached).__name__
                        }
                    )

            # Coleta sugestões em diferentes variações
            sugestoes_base = await self.extrair_sugestoes(termo, idioma)
            sugestoes_prefixo = []
            
            # Testa diferentes prefixos comuns
            prefixos = ["como", "onde", "qual", "quando", "quem", "por que"]
            for prefixo in prefixos:
                sugestoes = await self.extrair_sugestoes(f"{prefixo} {termo}", idioma)
                sugestoes_prefixo.extend(sugestoes)
                
            # Analisa sazonalidade
            sazonalidade = await self._analisar_sazonalidade(
                termo,
                sugestoes_base + sugestoes_prefixo,
                idioma
            )
            
            # Analisa tipos de intenção
            intencoes = self._analisar_intencoes(
                sugestoes_base + sugestoes_prefixo,
                idioma
            )
            
            # Calcula métricas
            metricas = {
                "total_sugestoes": len(sugestoes_base),
                "total_variantes": len(sugestoes_prefixo),
                "sazonalidade": sazonalidade,
                "intencoes": intencoes,
                "idioma": idioma,
                "data_coleta": datetime.utcnow().isoformat()
            }
            
            # Adiciona métricas calculadas
            metricas.update({
                "volume": self._calcular_volume(metricas),
                "concorrencia": self._calcular_concorrencia(metricas),
                "tendencia": self.analisador.calcular_tendencia(termo)
            })
            
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
                "Erro ao extrair métricas do Google Suggest",
                {"erro": str(e), "termo": termo}
            )
            return {
                "total_sugestoes": 0,
                "total_variantes": 0,
                "sazonalidade": 0,
                "intencoes": {},
                "volume": 0,
                "concorrencia": 0.5,
                "tendencia": 0,
                "erro": str(e)
            }

    async def _analisar_sazonalidade(
        self,
        termo: str,
        sugestoes: List[str],
        idioma: str
    ) -> float:
        """
        Analisa padrões de sazonalidade nas sugestões.
        
        Args:
            termo: Termo base
            sugestoes: Lista de sugestões
            idioma: Código do idioma
            
        Returns:
            Score de sazonalidade (0 a 1)
        """
        try:
            config_idioma = self._configuracoes_idiomas[idioma]
            meses = config_idioma["meses"]
            
            # Procura referências a meses nas sugestões
            referencias_meses = {}
            for sugestao in sugestoes:
                for mes, num in meses.items():
                    if mes in sugestao.lower():
                        referencias_meses[num] = referencias_meses.get(num, 0) + 1
            
            if not referencias_meses:
                return 0
                
            # Calcula distribuição ao longo do ano
            total_refs = sum(referencias_meses.values())
            distribuicao = {
                mes: refs / total_refs
                for mes, refs in referencias_meses.items()
            }
            
            # Calcula variação na distribuição
            media = 1 / 12  # Distribuição uniforme
            variacao = sum(
                abs(dist - media)
                for dist in distribuicao.values()
            ) / len(distribuicao)
            
            # Normaliza score
            return min(variacao * 2, 1)
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao analisar sazonalidade",
                {"erro": str(e), "termo": termo}
            )
            return 0

    def _analisar_intencoes(
        self,
        sugestoes: List[str],
        idioma: str
    ) -> Dict[str, int]:
        """
        Analisa tipos de intenção nas sugestões.
        
        Args:
            sugestoes: Lista de sugestões
            idioma: Código do idioma
            
        Returns:
            Dicionário com contagem por tipo de intenção
        """
        intencoes = {
            "informacional": 0,
            "navegacional": 0,
            "transacional": 0,
            "comercial": 0
        }
        
        for sugestao in sugestoes:
            sugestao_lower = sugestao.lower()
            
            if any(p in sugestao_lower for p in ["como", "what", "how"]):
                intencoes["informacional"] += 1
            elif any(p in sugestao_lower for p in ["comprar", "preço", "buy", "price"]):
                intencoes["transacional"] += 1
            elif any(p in sugestao_lower for p in ["melhor", "vs", "comparar", "best"]):
                intencoes["comercial"] += 1
            else:
                intencoes["navegacional"] += 1
                
        return intencoes

    def _calcular_volume(self, metricas: Dict) -> int:
        """
        Calcula volume estimado baseado nas métricas.
        
        Args:
            metricas: Dicionário com métricas
            
        Returns:
            Volume estimado
        """
        total_sugestoes = metricas["total_sugestoes"]
        total_variantes = metricas["total_variantes"]
        
        if total_sugestoes == 0:
            return 10
        elif total_sugestoes < 5:
            return 50
        elif total_sugestoes < 10:
            return 100
        elif total_sugestoes < 20:
            return 500
        else:
            return 1000

    def _calcular_concorrencia(self, metricas: Dict) -> float:
        """
        Calcula nível de concorrência baseado nas métricas.
        
        Args:
            metricas: Dicionário com métricas
            
        Returns:
            Score de concorrência (0 a 1)
        """
        try:
            # Considera distribuição de intenções
            intencoes = metricas["intencoes"]
            total_intencoes = sum(intencoes.values())
            
            if total_intencoes == 0:
                return 0.5
                
            # Calcula peso por tipo de intenção
            pesos = {
                "transacional": 0.4,  # Maior peso
                "comercial": 0.3,
                "informacional": 0.2,
                "navegacional": 0.1  # Menor peso
            }
            
            score = sum(
                (intencoes[tipo] / total_intencoes) * peso
                for tipo, peso in pesos.items()
            )
            
            # Ajusta baseado no volume de sugestões
            volume_normalizado = min(
                metricas["total_sugestoes"] / 20,
                1
            )
            
            score = (score * 0.7) + (volume_normalizado * 0.3)
            
            return min(max(score, 0), 1)
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao calcular concorrência",
                {"erro": str(e)}
            )
            return 0.5

    async def validar_termo(self, termo: str) -> bool:
        """
        Validação geral para o termo.
        
        Args:
            termo: Termo a ser validado
            
        Returns:
            True se o termo é válido
        """
        if not termo:
            self.registrar_erro(
                "Termo vazio",
                {"termo": termo}
            )
            return False
            
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo",
                {"termo": termo, "tamanho": len(termo)}
            )
            return False
            
        return True

    async def validar_termo_especifico(self, termo: str, idioma: str = "pt-BR") -> bool:
        """
        Validação específica para o Google Suggest, usando ValidadorKeywords.
        """
        if not termo or len(termo) > 100:
            self.registrar_erro(
                "Termo inválido para Google Suggest",
                {"termo": termo, "motivo": "tamanho"}
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
        async with self._session_lock:
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gerenciamento de contexto para fechamento de sessão."""
        async with self._session_lock:
            if self.session and not self.session.closed:
                await self.session.close()
                self.session = None

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """
        Classifica a intenção de busca para uma lista de keywords.
        
        Args:
            keywords: Lista de termos para classificar
            
        Returns:
            Lista de intenções de busca correspondentes
        """
        intencoes = []
        for termo in keywords:
            termo_lower = termo.lower()
            if any(p in termo_lower for p in ['como', 'tutorial', 'guia']):
                intencoes.append(IntencaoBusca.INFORMACIONAL)
            elif any(p in termo_lower for p in ['comprar', 'preço', 'onde']):
                intencoes.append(IntencaoBusca.TRANSACIONAL)
            elif any(p in termo_lower for p in ['melhor', 'vs', 'comparar']):
                intencoes.append(IntencaoBusca.COMPARACAO)
            else:
                intencoes.append(IntencaoBusca.NAVEGACIONAL)
        return intencoes

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """
        Coleta métricas para uma lista de keywords.
        
        Args:
            keywords: Lista de termos para coletar métricas
            
        Returns:
            Lista de dicionários com métricas para cada termo
        """
        metricas = []
        for termo in keywords:
            try:
                metricas_termo = await self.extrair_metricas_especificas(termo)
                metricas.append(metricas_termo)
            except Exception as e:
                self.registrar_erro(
                    f"Erro ao coletar métricas para: {termo}",
                    {"erro": str(e)}
                )
                metricas.append({
                    "volume": 0,
                    "concorrencia": 0.5,
                    "sazonalidade": 0,
                    "tendencia": 0
                })
        return metricas

    def registrar_erro(self, mensagem, detalhes=None):
        self.logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_coletor",
            "status": "error",
            "source": "coletor.google_suggest",
            "message": mensagem,
            "details": detalhes or {}
        })

    def registrar_sucesso(self, evento, detalhes=None):
        self.logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": evento,
            "status": "success",
            "source": "coletor.google_suggest",
            "details": detalhes or {}
        }) 