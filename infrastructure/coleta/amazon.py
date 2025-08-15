"""
Implementação do coletor de keywords da Amazon com análise avançada.
"""
from typing import List, Dict, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
import re
import time
import uuid
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import get_config, AMAZON_CONFIG
from shared.logger import logger
from shared.cache import AsyncCache
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from shared.utils.normalizador_central import NormalizadorCentral

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

class AmazonColetor(KeywordColetorBase):
    """Implementação do coletor de keywords da Amazon com análise avançada."""

    def __init__(self, cache=None, logger_=None):
        """
        Inicializa o coletor com configurações específicas.
        Permite injeção de cache e logger para testes e rastreabilidade.
        Args:
            cache: Instância de cache assíncrono (opcional)
            logger_: Logger customizado (opcional)
        """
        config = get_config("coletores.amazon")
        if config is None:
            config = AMAZON_CONFIG
        super().__init__(
            nome="amazon",
            config=config
        )
        self.logger = logger_ if logger_ is not None else logger
        self.base_url = "https://www.amazon.com.br"
        self.search_url = f"{self.base_url}/string_data"
        self.suggest_url = f"{self.base_url}/api/complete"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.session = None
        self.cache = cache if cache is not None else AsyncCache(
            namespace="amazon",
            ttl=self.config.get("cache_ttl", 3600)  # 1 hora padrão
        )
        self._categorias_cache = {}
        
        # Normalizador centralizado
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-.,?!]+$',
            min_caracteres=3,
            max_caracteres=100
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    @breaker
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError))
    )
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        uuid_req = str(uuid.uuid4())
        inicio = time.time()
        cache_key = f"sugestoes:{termo}"
        sugestoes = []
        try:
            cached = None
            try:
                cached = await self.cache.get(cache_key)
            except Exception as e_cache:
                self.logger.error({
                    "uuid": uuid_req,
                    "coletor": "amazon",
                    "termo": termo,
                    "status": "erro_cache_get",
                    "erro": str(e_cache),
                    "latencia_ms": int((time.time() - inicio) * 1000),
                    "ambiente": self.config.get("env", "dev")
                })
            if cached:
                return cached
            session = await self._get_session()
            params = {"key": termo, "ref": "nb_sb_noss"}
            async with session.get(self.suggest_url, params=params, proxy=self.config.get("proxy")) as response:
                if response.status != 200:
                    return []
                data = await response.json()
                for suggestion in data.get("suggestions", []):
                    termo_sugerido = suggestion.get("value", "").strip()
                    if termo_sugerido and termo_sugerido != termo:
                        sugestoes.append(termo_sugerido)
                try:
                    await self.cache.set(cache_key, sugestoes)
                except Exception as e_cache_set:
                    self.logger.error({
                        "uuid": uuid_req,
                        "coletor": "amazon",
                        "termo": termo,
                        "status": "erro_cache_set",
                        "erro": str(e_cache_set),
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev")
                    })
                self.logger.info({
                    "uuid": uuid_req,
                    "coletor": "amazon",
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
                "coletor": "amazon",
                "termo": termo,
                "status": "erro",
                "erro": str(e),
                "latencia_ms": int((time.time() - inicio) * 1000),
                "ambiente": self.config.get("env", "dev")
            })
            # Fallback: retorna cache ou lista vazia
            try:
                cached = await self.cache.get(cache_key)
            except Exception:
                cached = None
            return cached or []

    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        cache_key = f"metricas:{termo}"
        cached = None
        try:
            try:
                cached = await self.cache.get(cache_key)
            except Exception as e_cache:
                self.registrar_erro(
                    "erro_cache_get_metricas",
                    {"erro": str(e_cache), "termo": termo}
                )
            if cached:
                return cached
            session = await self._get_session()
            params = {
                "key": termo,
                "ref": "nb_sb_noss"
            }
            async with session.get(
                self.search_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro ao acessar Amazon: {response.status}")
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                produtos = await self._extrair_dados_produtos(soup)
                categorias = await self._extrair_categorias(soup)
                categoria_principal = max(
                    categorias.items(),
                    key=lambda value: value[1]
                )[0] if categorias else "other"
                
                # Calcula métricas
                metricas = {
                    "total_produtos": len(produtos),
                    "produtos_prime": sum(1 for p in produtos if p.get("prime", False)),
                    "categoria": categoria_principal,
                    "categorias": categorias,
                    "precos": {
                        "minimo": min((p["preco"] for p in produtos if p["preco"] > 0), default=0),
                        "maximo": max((p["preco"] for p in produtos if p["preco"] > 0), default=0),
                        "medio": sum(p["preco"] for p in produtos if p["preco"] > 0) /
                                max(1, len([p for p in produtos if p["preco"] > 0]))
                    },
                    "reviews": {
                        "total": sum(p["total_reviews"] for p in produtos),
                        "media_rating": sum(p["rating"] * p["total_reviews"] for p in produtos) /
                                      max(1, sum(p["total_reviews"] for p in produtos)),
                        "sentimento": self._analisar_sentimento_reviews(produtos)
                    }
                }
                
                # Adiciona métricas calculadas
                metricas.update({
                    "volume": self._calcular_volume(metricas),
                    "concorrencia": self._calcular_concorrencia(metricas),
                    "data_coleta": datetime.utcnow().isoformat()
                })
                try:
                    await self.cache.set(cache_key, metricas)
                except Exception as e_cache_set:
                    self.registrar_erro(
                        "erro_cache_set_metricas",
                        {"erro": str(e_cache_set), "termo": termo}
                    )
                return metricas
        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas da Amazon",
                {"erro": str(e), "termo": termo}
            )
            return {
                "volume": 0,
                "concorrencia": 0.5,
                "categoria": "other",
                "erro": str(e)
            }

    async def _extrair_dados_produtos(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai dados detalhados dos produtos."""
        produtos = []
        
        for produto_div in soup.find_all("div", {"data-component-type": "string_data-search-result"}):
            try:
                # Extrai preço com tratamento de variações
                preco = self._extrair_preco(produto_div)
                
                # Extrai dados de review
                rating_span = produto_div.find("span", {"class": "a-icon-alt"})
                rating = 0.0
                if rating_span:
                    try:
                        rating_text = rating_span.get_text()
                        rating = float(re.search(r"(\data+[.,]\data+)", rating_text).group(1).replace(",", "."))
                    except (AttributeError, ValueError):
                        pass
                
                reviews_link = produto_div.find("a", {"class": "a-link-normal", "href": re.compile(r"#customerReviews$")})
                total_reviews = 0
                if reviews_link:
                    try:
                        reviews_text = reviews_link.get_text()
                        total_reviews = int(''.join(filter(str.isdigit, reviews_text)))
                    except (AttributeError, ValueError):
                        pass
                
                # Verifica se é Prime
                prime_badge = produto_div.find("index", {"class": "a-icon-prime"})
                
                # Extrai categoria do produto
                categoria = self._extrair_categoria_produto(produto_div)
                
                produtos.append({
                    "preco": preco,
                    "rating": rating,
                    "total_reviews": total_reviews,
                    "prime": bool(prime_badge),
                    "categoria": categoria
                })
                
            except Exception as e:
                self.registrar_erro(
                    "Erro ao extrair dados de produto",
                    {"erro": str(e)}
                )
                
        return produtos

    def _extrair_preco(self, produto_div: BeautifulSoup) -> float:
        """Extrai e processa preço do produto."""
        try:
            # Tenta primeiro o preço com desconto
            preco_span = produto_div.find("span", {"class": "a-price-whole"})
            if not preco_span:
                # Tenta preço regular
                preco_span = produto_div.find("span", {"class": "a-price"})
            
            if preco_span:
                preco_text = preco_span.get_text().strip()
                # Remove símbolos de moeda e formata
                preco_limpo = re.sub(r'[^\data,.]', '', preco_text)
                return float(preco_limpo.replace(".", "").replace(",", "."))
                
            return 0.0
            
        except (AttributeError, ValueError):
            return 0.0

    async def _extrair_categorias(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extrai e analisa categorias dos produtos."""
        categorias = {}
        
        try:
            # Extrai do menu de navegação
            nav_items = soup.find_all("a", {"class": "a-link-normal string_data-navigation-item"})
            for item in nav_items:
                categoria = item.get_text().strip().lower()
                if categoria:
                    categorias[categoria] = categorias.get(categoria, 0) + 1
                    
            # Extrai dos breadcrumbs
            breadcrumbs = soup.find_all("a", {"class": "a-link-normal a-color-tertiary"})
            for crumb in breadcrumbs:
                categoria = crumb.get_text().strip().lower()
                if categoria:
                    categorias[categoria] = categorias.get(categoria, 0) + 1
                    
            # Atualiza cache de categorias
            self._categorias_cache.update(categorias)
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair categorias",
                {"erro": str(e)}
            )
            
        return categorias

    def _extrair_categoria_produto(self, produto_div: BeautifulSoup) -> str:
        """Extrai categoria específica do produto."""
        try:
            # Tenta extrair da descrição do produto
            descricao = produto_div.get_text().lower()
            
            # Usa cache de categorias para identificar
            for categoria, _ in sorted(
                self._categorias_cache.items(),
                key=lambda value: len(value[0]),
                reverse=True
            ):
                if categoria in descricao:
                    return categoria
                    
            return "other"
            
        except Exception:
            return "other"

    def _analisar_sentimento_reviews(self, produtos: List[Dict]) -> float:
        """Analisa sentimento geral dos reviews."""
        try:
            total_peso = 0
            soma_ponderada = 0
            
            for produto in produtos:
                reviews = produto["total_reviews"]
                if reviews > 0:
                    # Normaliza rating para -1 a 1
                    sentimento = (produto["rating"] - 2.5) / 2.5
                    # Pondera pelo número de reviews
                    soma_ponderada += sentimento * reviews
                    total_peso += reviews
                    
            return soma_ponderada / max(1, total_peso)
            
        except Exception:
            return 0.0

    def _calcular_volume(self, metricas: Dict) -> int:
        """Calcula volume estimado baseado nas métricas."""
        total_produtos = metricas.get("total_produtos", 0)
        if total_produtos == 0:
            return 10
        elif total_produtos < 100:
            return 50
        elif total_produtos < 1000:
            return 100
        elif total_produtos < 10000:
            return 500
        else:
            return 1000

    def _calcular_concorrencia(self, metricas: Dict) -> float:
        """Calcula nível de concorrência baseado nas métricas."""
        try:
            # Base na quantidade de produtos
            total_produtos = metricas.get("total_produtos", 0)
            if total_produtos == 0:
                return 0.1
                
            # Ajusta baseado na proporção de Prime
            produtos_prime = metricas.get("produtos_prime", 0)
            prop_prime = produtos_prime / max(1, total_produtos)
            
            # Ajusta baseado nos preços
            precos = metricas.get("precos", {})
            amplitude_precos = (precos.get("maximo", 0) - precos.get("minimo", 0))
            if amplitude_precos > 0:
                variacao_precos = amplitude_precos / max(1, precos.get("medio", 1))
            else:
                variacao_precos = 0
                
            # Combina fatores
            concorrencia = min(1.0, (
                (total_produtos / 1000) * 0.4 +  # Peso dos produtos
                prop_prime * 0.3 +               # Peso do Prime
                variacao_precos * 0.3            # Peso da variação de preços
            ))
            
            return max(0.1, concorrencia)
            
        except Exception:
            return 0.5

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para a Amazon, usando ValidadorKeywords.
        """
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo para Amazon",
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
        Coleta keywords relacionadas da Amazon.
        
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
                # 1. Coleta sugestões de busca
                params = {
                    "q": termo,
                    "mid": "ATVPDKIKX0DER",
                    "alias": "aps",
                    "prefix": termo
                }
                
                async with session.get(
                    self.suggest_url,
                    params=params,
                    proxy=self.config.get("proxy")
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        sugestoes = data.get("suggestions", [])
                        
                        for sugestao in sugestoes:
                            termo_sugerido = sugestao.get("value", "").strip()
                            if termo_sugerido and termo_sugerido != termo:
                                keyword = Keyword(
                                    termo=termo_sugerido,
                                    volume_busca=0,
                                    cpc=0.0,
                                    concorrencia=0.5,
                                    intencao=IntencaoBusca.NAVEGACIONAL,
                                    fonte=self.nome,
                                    data_coleta=self.obter_data_atual()
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
                
                # 2. Coleta de produtos e categorias relacionadas
                params = {
                    "key": termo,
                    "ref": "nb_sb_noss"
                }
                
                async with session.get(
                    self.search_url,
                    params=params,
                    proxy=self.config.get("proxy")
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Extrai categorias relacionadas
                        for categoria in soup.find_all("a", {"class": "a-link-normal string_data-navigation-item"}):
                            nome_categoria = categoria.get_text().strip()
                            if nome_categoria:
                                keyword = Keyword(
                                    termo=nome_categoria,
                                    volume_busca=0,
                                    cpc=0.0,
                                    concorrencia=0.5,
                                    intencao=IntencaoBusca.NAVEGACIONAL,
                                    fonte=self.nome,
                                    data_coleta=self.obter_data_atual()
                                )
                                if len(keyword.termo.split()) >= 3 and len(keyword.termo) >= 15 and keyword.concorrencia <= 0.5:
                                    keywords.append(keyword)
                        
                        # Extrai termos de títulos de produtos
                        for produto in soup.find_all("div", {"data-component-type": "string_data-search-result"}):
                            titulo = produto.find("span", {"class": "a-text-normal"})
                            if titulo:
                                texto_titulo = titulo.get_text().strip()
                                termos_produto = self._extrair_keywords_texto(texto_titulo)
                                
                                for termo_produto in termos_produto:
                                    if termo_produto != termo:
                                        keyword = Keyword(
                                            termo=termo_produto,
                                            volume_busca=0,
                                            cpc=0.0,
                                            concorrencia=0.5,
                                            intencao=IntencaoBusca.NAVEGACIONAL,
                                            fonte=self.nome,
                                            data_coleta=self.obter_data_atual()
                                        )
                                        if len(keyword.termo.split()) >= 3 and len(keyword.termo) >= 15 and keyword.concorrencia <= 0.5:
                                            keywords.append(keyword)

            self.atualizar_metricas(len(keywords))
            self.registrar_sucesso("coleta_keywords", {
                "termo_base": termo,
                "total_coletado": len(keywords)
            })
            
            return keywords[:limite]

        except Exception as e:
            self.registrar_erro(
                "Erro durante coleta da Amazon",
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
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                for keyword in keywords:
                    params = {
                        "key": keyword,
                        "ref": "nb_sb_noss"
                    }
                    
                    async with session.get(
                        self.search_url,
                        params=params,
                        proxy=self.config.get("proxy")
                    ) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, "html.parser")
                            
                            # Coleta métricas dos resultados
                            total_produtos = len(soup.find_all("div", {"data-component-type": "string_data-search-result"}))
                            total_prime = len(soup.find_all("index", {"class": "a-icon-prime"}))
                            
                            # Extrai faixa de preços
                            precos = []
                            for preco in soup.find_all("span", {"class": "a-price-whole"}):
                                try:
                                    valor = float(preco.get_text().replace(".", "").replace(",", "."))
                                    precos.append(valor)
                                except (ValueError, AttributeError):
                                    continue
                            
                            metricas.append({
                                "keyword": keyword,
                                "total_produtos": total_produtos,
                                "produtos_prime": total_prime,
                                "preco_minimo": min(precos) if precos else None,
                                "preco_maximo": max(precos) if precos else None,
                                "preco_medio": sum(precos) / len(precos) if precos else None,
                                "data_coleta": datetime.utcnow().isoformat()
                            })
                    
                    # Respeita rate limiting
                    await asyncio.sleep(self.config.get("delay_entre_requisicoes", 1))
            
            return metricas
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao coletar métricas da Amazon",
                {"erro": str(e)}
            )
            return []

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
            # Análise heurística específica para Amazon
            keyword_lower = keyword.lower()
            
            if any(termo in keyword_lower for termo in ["como", "qual", "onde", "quando", "guia", "manual"]):
                intencao = IntencaoBusca.INFORMACIONAL
            elif any(termo in keyword_lower for termo in ["comprar", "preço", "promoção", "desconto", "frete"]):
                intencao = IntencaoBusca.TRANSACIONAL
            elif any(termo in keyword_lower for termo in ["vs", "versus", "melhor", "comparar", "review", "avaliação"]):
                intencao = IntencaoBusca.COMERCIAL
            else:
                intencao = IntencaoBusca.NAVEGACIONAL
                
            intencoes.append(intencao)
            
        return intencoes

    def _extrair_keywords_texto(self, texto: str) -> List[str]:
        """
        Extrai keywords relevantes de um texto usando o normalizador central.
        
        Args:
            texto: Texto para extrair keywords
            
        Returns:
            Lista de keywords extraídas e normalizadas
        """
        # Remove caracteres especiais e divide em palavras
        palavras = texto.lower().split()
        
        # Remove stopwords e palavras muito curtas
        palavras_filtradas = [
            p for p in palavras 
            if len(p) > 3 and p not in self.config.get("stopwords", [])
        ]
        
        # Usa o normalizador central para normalizar e remover duplicatas
        return self.normalizador.normalizar_lista_termos(palavras_filtradas) 