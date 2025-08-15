"""
Coletor de palavras-chave relacionadas do Google Search.
"""
from typing import List, Dict, Optional, Any
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from urllib.parse import quote
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    CACHE_CONFIG,
    GOOGLE_RELATED_CONFIG,
    TRENDS_CONFIG
)
from infrastructure.coleta.utils.cache import CacheDistribuido
from infrastructure.coleta.utils.trends import AnalisadorTendencias
from shared.logger import logger
from shared.utils.normalizador_central import NormalizadorCentral, normalizar_termo, validar_termo
from infrastructure.processamento.validador_keywords import ValidadorKeywords

class GoogleRelatedColetor(KeywordColetorBase):
    """Implementação do coletor de Related Searches do Google."""

    def __init__(self, cache=None, logger_=None, session=None):
        """Inicializa o coletor com configurações específicas e dependências injetáveis."""
        super().__init__(
            nome="google_related",
            config=GOOGLE_RELATED_CONFIG
        )
        self.base_url = "https://www.google.com/search"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        # Cache injetável
        self.cache = cache or CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["google_related"],
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
        
        # Normalizador central
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            min_caracteres=self.min_caracteres,
            max_caracteres=self.max_caracteres
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

    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões relacionadas do Google Search ou de resposta JSON.
        """
        try:
            # Verifica cache
            cache_key = f"sugestoes:{termo}"
            cached = await self.cache.get(cache_key)
            if cached is not None:
                if isinstance(cached, list):
                    self.registrar_sucesso(
                        "cache_hit_sugestoes",
                        {
                            "termo": termo,
                            "total_sugestoes": len(cached)
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

            # Prepara a sessão e parâmetros
            async with self as coletor:
                session = await coletor._get_session()
                params = {
                    "q": termo,
                    "hl": "pt-BR",
                    "gl": "BR"
                }
                self.registrar_sucesso(
                    "iniciando_requisicao_related",
                    {
                        "termo": termo,
                        "params": params
                    }
                )
                async with session.get(
                    self.base_url,
                    params=params,
                    proxy=self.proxy_config if self.proxy_enabled else None
                ) as response:
                    if response.status != 200:
                        self.registrar_erro(
                            "Erro ao acessar Google Search",
                            {
                                "status": response.status,
                                "termo": termo
                            }
                        )
                        return []

                    sugestoes = []
                    # Tenta parsing JSON primeiro
                    try:
                        data = await response.json()
                        if isinstance(data, dict) and "suggestions" in data:
                            suggestions = data["suggestions"]
                            if isinstance(suggestions, list):
                                for item in suggestions:
                                    if isinstance(item, dict):
                                        valor = item.get("value", "").strip()
                                        if valor and valor != termo:
                                            sugestoes.append(valor)
                                    elif isinstance(item, str):
                                        valor = item.strip()
                                        if valor and valor != termo:
                                            sugestoes.append(valor)
                        # Se encontrou sugestões, salva e retorna
                        if sugestoes:
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
                    except Exception:
                        # Não é JSON ou não tem suggestions, segue para parsing HTML
                        pass

                    # Parsing HTML (fallback)
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    for div in soup.find_all("div", class_="BNeawe"):
                        sugestao = div.get_text().strip()
                        if sugestao and sugestao != termo:
                            sugestoes.append(sugestao)
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
                "Erro ao extrair sugestões do Google Search",
                {
                    "erro": str(e),
                    "termo": termo
                }
            )
            return []

    async def extrair_metricas_especificas(self, termo: str) -> Dict[str, Any]:
        """
        Extrai métricas específicas para uma keyword.
        """
        try:
            # Blindar acesso ao cache
            try:
                cache_key = f"metricas:{termo}"
                cached = await self.cache.get(cache_key)
                if cached is not None:
                    if isinstance(cached, dict):
                        self.registrar_sucesso(
                            "cache_hit_metricas",
                            {
                                "termo": termo,
                                "metricas": cached
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
            except Exception as e_cache:
                self.registrar_erro(
                    "Erro ao acessar cache de metricas",
                    {"erro": str(e_cache), "termo": termo}
                )

            # Prepara a sessão e parâmetros
            async with self as coletor:
                try:
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
                                "Erro ao acessar Google Search",
                                {
                                    "status": response.status,
                                    "termo": termo
                                }
                            )
                            return {
                                "total_resultados": 0,
                                "ads_count": 0,
                                "volume": 0,
                                "concorrencia": 0.0,
                                "tendencia": 0.0,
                                "intencao": IntencaoBusca.NAVEGACIONAL
                            }
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        # Extrai total de resultados
                        total_resultados = 0
                        stats_div = soup.find("div", id="result-stats")
                        if stats_div:
                            stats_text = stats_div.get_text()
                            match = re.search(r"(\data+(?:\.\data+)?)", stats_text)
                            if match:
                                total_resultados = int(match.group(1).replace(".", ""))
                        # Conta anúncios
                        ads_count = len(soup.find_all("div", class_="ads"))
                        # Calcula métricas
                        volume = total_resultados // 1000 if total_resultados > 0 else 0
                        concorrencia = min(1.0, ads_count / 10) if ads_count > 0 else 0.0
                        tendencia = await self.analisador.calcular_tendencia(termo)
                        intencao = self._determinar_intencao(termo, total_resultados, ads_count)
                        metricas = {
                            "total_resultados": total_resultados,
                            "ads_count": ads_count,
                            "volume": volume,
                            "concorrencia": concorrencia,
                            "tendencia": tendencia,
                            "intencao": intencao
                        }
                        # Salva no cache
                        await self.cache.set(
                            cache_key,
                            metricas,
                            ttl=CACHE_CONFIG["ttl_metricas"]
                        )
                        self.registrar_sucesso(
                            "extracao_metricas",
                            {
                                "termo": termo,
                                "metricas": metricas
                            }
                        )
                        return metricas
                except Exception as e_sessao:
                    self.registrar_erro(
                        "Erro ao acessar sessão ou processar resposta",
                        {"erro": str(e_sessao), "termo": termo}
                    )
                    raise e_sessao
        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do Google Search",
                {
                    "erro": str(e),
                    "termo": termo
                }
            )
            return {
                "total_resultados": 0,
                "ads_count": 0,
                "volume": 0,
                "concorrencia": 0.0,
                "tendencia": 0.0,
                "intencao": IntencaoBusca.NAVEGACIONAL
            }

    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[Keyword]:
        """
        Coleta keywords relacionadas ao termo fornecido, priorizando cauda longa.
        """
        keywords = []
        if not await self.validar_termo(termo):
            return keywords
        try:
            sugestoes = await self.extrair_sugestoes(termo)
            for sugestao in sugestoes[:limite]:
                try:
                    metricas = await self.extrair_metricas_especificas(sugestao)
                    keyword = Keyword(
                        termo=sugestao,
                        volume_busca=metricas.get("volume", 0),
                        cpc=metricas.get("cpc", 0.0),
                        concorrencia=metricas.get("concorrencia", 0.0),
                        intencao=metricas.get("intencao", IntencaoBusca.NAVEGACIONAL)
                    )
                    # Filtro de cauda longa: pelo menos 3 palavras, concorrência <= 0.5, termo >= 15 caracteres
                    if len(keyword.termo.split()) >= 3 and keyword.concorrencia <= 0.5 and len(keyword.termo) >= 15:
                        keywords.append(keyword)
                except Exception as e:
                    self.registrar_erro(
                        "Erro ao processar sugestão",
                        {"erro": str(e), "sugestao": sugestao}
                    )
                    continue
            self.registrar_sucesso(
                "coleta_related",
                {"termo_base": termo, "total_sugestoes": len(sugestoes), "keywords_geradas": len(keywords)}
            )
            self.atualizar_metricas(len(keywords))
            return keywords
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar keywords",
                {"erro": str(e), "termo": termo}
            )
            return keywords

    def _determinar_intencao(
        self,
        termo: str,
        total_resultados: int,
        ads_count: int
    ) -> IntencaoBusca:
        """
        Determina a intenção de busca com base nas métricas.
        """
        informacional = ["como", "o que", "qual", "quando", "onde", "por que", "quem"]
        transacional = ["comprar", "preço", "desconto", "promoção", "loja", "vender"]
        navegacional = ["login", "entrar", "acessar", "site", "página"]
        termo_lower = termo.lower()
        for palavra in informacional:
            if palavra in termo_lower:
                return IntencaoBusca.INFORMACIONAL
        for palavra in transacional:
            if palavra in termo_lower:
                return IntencaoBusca.TRANSACIONAL
        for palavra in navegacional:
            if palavra in termo_lower:
                return IntencaoBusca.NAVEGACIONAL
        # Priorizar ads_count > 5
        if ads_count > 5:
            return IntencaoBusca.TRANSACIONAL
        if total_resultados > 1000000:
            return IntencaoBusca.INFORMACIONAL
        return IntencaoBusca.NAVEGACIONAL

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o Google Search, usando ValidadorKeywords.
        """
        if not termo or len(termo) > 100:
            self.registrar_erro(
                "Termo inválido para Google Search",
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
                    "total_resultados": 0,
                    "ads_count": 0,
                    "volume": 0,
                    "concorrencia": 0.5,
                    "tendencia": 0,
                    "intencao": IntencaoBusca.NAVEGACIONAL
                })
        return metricas 