"""
Implementação do coletor de People Also Ask do Google.
"""
import aiohttp
import asyncio
from typing import List, Dict, Set, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from domain.models import IntencaoBusca, Keyword
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    CACHE_CONFIG,
    TRENDS_CONFIG,
    GOOGLE_PAA_CONFIG
)
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.logger import logger
from shared.utils.normalizador_central import NormalizadorCentral
from datetime import datetime

class GooglePAAColetor(KeywordColetorBase):
    """Implementação do coletor de People Also Ask do Google."""

    def __init__(self, cache=None, logger_=None, session=None):
        """Inicializa o coletor com configurações específicas e dependências injetáveis."""
        super().__init__(
            nome="google_paa",
            config=GOOGLE_PAA_CONFIG
        )
        self.base_url = "https://www.google.com/search"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.max_depth = self.config.get("max_depth", 3)
        self.perguntas_coletadas: Set[str] = set()
        # Cache injetável
        self.cache = cache or CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["google_paa"],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"]
        )
        # Logger injetável
        self.logger = logger_ or logger
        # Analisador de tendências
        self.analisador = AnalisadorTendencias(
            janela_analise=TRENDS_CONFIG["janela_analise"]
        )
        self._session_lock = asyncio.Lock()
        self.session = session
        
        # Normalizador centralizado
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-.,?!]+$',
            min_caracteres=3,
            max_caracteres=100
        )

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

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP."""
        async with self._session_lock:
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession(headers=self.headers)
            return self.session

    async def _extrair_perguntas_pagina(self, html: str) -> List[str]:
        """
        Extrai perguntas PAA do HTML da página.
        
        Args:
            html: HTML da página de resultados
            
        Returns:
            Lista de perguntas encontradas
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            perguntas = []
            
            # Localiza os elementos PAA
            paa_divs = soup.find_all('div', {'class': 'related-question-pair'})
            for div in paa_divs:
                pergunta = div.get_text().strip()
                if pergunta and pergunta not in self.perguntas_coletadas:
                    perguntas.append(pergunta)
                    self.perguntas_coletadas.add(pergunta)
                    
            self.registrar_sucesso(
                "extracao_perguntas_pagina",
                {
                    "total_perguntas": len(perguntas),
                    "total_coletadas": len(self.perguntas_coletadas)
                }
            )
                    
            return perguntas
        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair perguntas da página",
                {"erro": str(e)}
            )
            return []

    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai perguntas relacionadas do Google PAA.
        """
        try:
            cache_key = f"sugestoes:{termo}"
            cached = None
            try:
                cached = await self.cache.get(cache_key)
            except Exception as e_cache:
                self.registrar_erro(
                    "erro_cache_get_sugestoes",
                    {"erro": str(e_cache), "termo": termo}
                )
            if cached is not None:
                if isinstance(cached, list):
                    self.registrar_sucesso(
                        "cache_hit_sugestoes",
                        {
                            "termo": termo,
                            "total_perguntas": len(cached)
                        }
                    )
                    return cached
                else:
                    self.registrar_erro(
                        "Cache com formato inválido",
                        {
                            "termo": termo,
                            "tipo_cache": type(cached).__name__
                        }
                    )
            async with self as coletor:
                session = await coletor._get_session()
                params = {
                    "q": termo,
                    "hl": "pt-BR",
                    "gl": "BR"
                }
                async with session.get(
                    self.base_url,
                    params=params,
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        self.registrar_erro(
                            "Erro ao acessar Google PAA",
                            {
                                "status": response.status,
                                "termo": termo
                            }
                        )
                        return []
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    perguntas = []
                    for div in soup.find_all("div", class_="related-question-pair"):
                        pergunta = div.get_text().strip()
                        if pergunta and pergunta != termo:
                            perguntas.append(pergunta)
                    try:
                        await self.cache.set(
                            cache_key,
                            perguntas,
                            ttl=CACHE_CONFIG["ttl_keywords"]
                        )
                    except Exception as e_cache_set:
                        self.registrar_erro(
                            "erro_cache_set_sugestoes",
                            {"erro": str(e_cache_set), "termo": termo}
                        )
                    self.registrar_sucesso(
                        "extracao_perguntas",
                        {
                            "termo": termo,
                            "total_perguntas": len(perguntas)
                        }
                    )
                    return perguntas
        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair perguntas PAA",
                {
                    "erro": str(e),
                    "termo": termo
                }
            )
            return []

    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        """
        Extrai métricas específicas para o termo.
        Para o Google PAA, usamos heurísticas baseadas no tipo de pergunta.
        """
        try:
            cache_key = f"metricas:{termo}"
            cached = None
            try:
                cached = await self.cache.get(cache_key)
            except Exception as e_cache:
                self.registrar_erro(
                    "erro_cache_get_metricas",
                    {"erro": str(e_cache), "termo": termo}
                )
            if cached is not None:
                if isinstance(cached, dict):
                    return cached
                else:
                    self.registrar_erro(
                        "Cache com formato inválido",
                        {
                            "termo": termo,
                            "tipo_cache": type(cached).__name__
                        }
                    )
            termo_lower = termo.lower()
            palavras_interrogativas = {
                'como': 3,
                'qual': 2,
                'quando': 2,
                'onde': 2,
                'por que': 3,
                'quem': 1,
                'o que': 2
            }
            score_complexidade = 1
            for palavra, peso in palavras_interrogativas.items():
                if palavra in termo_lower:
                    score_complexidade = peso
                    break
            volume = max(10, 100 - (score_complexidade * 20))
            concorrencia = max(0.1, 1.0 - (score_complexidade * 0.2))
            if any(p in termo_lower for p in ['como', 'qual a melhor forma']):
                intencao = IntencaoBusca.INFORMACIONAL
            elif any(p in termo_lower for p in ['onde comprar', 'preço', 'custo']):
                intencao = IntencaoBusca.TRANSACIONAL
            elif any(p in termo_lower for p in ['qual melhor', 'comparar', 'diferença entre']):
                intencao = IntencaoBusca.COMPARACAO
            else:
                intencao = IntencaoBusca.INFORMACIONAL
            metricas = {
                "volume": volume,
                "cpc": 0.0,
                "concorrencia": concorrencia,
                "intencao": intencao,
                "score_complexidade": score_complexidade,
                "tendencia": self.analisador.calcular_tendencia(termo)
            }
            try:
                await self.cache.set(
                    cache_key,
                    metricas,
                    ttl=CACHE_CONFIG["ttl_metricas"]
                )
            except Exception as e_cache_set:
                self.registrar_erro(
                    "erro_cache_set_metricas",
                    {"erro": str(e_cache_set), "termo": termo}
                )
            self.analisador.registrar_acesso(termo)
            return metricas
        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do PAA",
                {"erro": str(e), "termo": termo}
            )
            return {
                "volume": 0,
                "cpc": 0.0,
                "concorrencia": 0.5,
                "intencao": IntencaoBusca.INFORMACIONAL,
                "score_complexidade": 1,
                "tendencia": 0
            }

    async def validar_termo_especifico(self, termo: str, idioma: str = "pt-BR") -> bool:
        """
        Validação específica para termos do Google PAA.
        
        Args:
            termo: Termo a ser validado
            idioma: Código do idioma (ex: pt-BR, en-US)
            
        Returns:
            True se o termo é válido, False caso contrário
        """
        if not termo:
            self.registrar_erro(
                "Termo vazio",
                {"termo": termo}
            )
            return False
            
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo para PAA",
                {"termo": termo, "tamanho": len(termo)}
            )
            return False
            
        return True

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
            # Extrai perguntas
            perguntas = await self.extrair_sugestoes(termo)
            
            # Processa cada pergunta
            for pergunta in perguntas[:limite]:
                try:
                    # Coleta métricas
                    metricas = await self.extrair_metricas_especificas(pergunta)
                    
                    # Cria objeto Keyword
                    keyword = Keyword(
                        termo=pergunta,
                        volume_busca=metricas.get("volume", 0),
                        cpc=metricas.get("cpc", 0.0),
                        concorrencia=metricas.get("concorrencia", 0.0),
                        intencao=metricas.get("intencao", IntencaoBusca.NAVEGACIONAL)
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
                        "Erro ao processar pergunta",
                        {
                            "erro": str(e),
                            "pergunta": pergunta
                        }
                    )
                    continue
            
            # Registra métricas
            self.registrar_sucesso(
                "coleta_paa",
                {
                    "termo_base": termo,
                    "total_perguntas": len(perguntas),
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
            if any(p in termo_lower for p in ['como', 'qual a melhor forma']):
                intencoes.append(IntencaoBusca.INFORMACIONAL)
            elif any(p in termo_lower for p in ['onde comprar', 'preço', 'custo']):
                intencoes.append(IntencaoBusca.TRANSACIONAL)
            elif any(p in termo_lower for p in ['qual melhor', 'comparar', 'diferença entre']):
                intencoes.append(IntencaoBusca.COMPARACAO)
            else:
                intencoes.append(IntencaoBusca.INFORMACIONAL)
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
                    "cpc": 0.0,
                    "concorrencia": 0.5,
                    "intencao": IntencaoBusca.INFORMACIONAL,
                    "score_complexidade": 1,
                    "tendencia": 0
                })
        return metricas

    def registrar_erro(self, mensagem, detalhes=None):
        self.logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_coletor",
            "status": "error",
            "source": "coletor.google_paa",
            "message": mensagem,
            "details": detalhes or {}
        })

    def registrar_sucesso(self, evento, detalhes=None):
        self.logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": evento,
            "status": "success",
            "source": "coletor.google_paa",
            "details": detalhes or {}
        }) 