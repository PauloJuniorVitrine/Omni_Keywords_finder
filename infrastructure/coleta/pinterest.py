"""
Implementação do coletor de keywords do Pinterest.
"""
from typing import List, Dict, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import get_config, PINTEREST_CONFIG
from shared.config import CACHE_CONFIG
from shared.logger import logger
from shared.utils.normalizador_central import NormalizadorCentral
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from infrastructure.coleta.utils.cache import CacheDistribuido

class PinterestColetor(KeywordColetorBase):
    """Implementação do coletor de keywords do Pinterest."""

    def __init__(self, cache=None, logger_=None):
        """
        Inicializa o coletor com configurações específicas.
        Permite injeção de cache e logger para testes e rastreabilidade.
        Args:
            cache: Instância de cache assíncrono (opcional)
            logger_: Logger customizado (opcional)
        """
        super().__init__(
            nome="pinterest",
            config=PINTEREST_CONFIG
        )
        self.base_url = "https://www.pinterest.com"
        self.search_url = f"{self.base_url}/search/pins"
        self.suggest_url = f"{self.base_url}/resource/AdvancedTypeaheadResource/get"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.session = None
        self.cache = cache if cache is not None else CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["pinterest"],
            ttl_padrao=CACHE_CONFIG["ttl_padrao"]
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

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de busca do Pinterest.
        
        Args:
            termo: Termo base para busca
            
        Returns:
            Lista de sugestões relacionadas
        """
        try:
            session = await self._get_session()
            params = {
                "source_url": "/search/pins/",
                "data": {
                    "options": {
                        "term": termo,
                        "pin_scope": "pins",
                        "scope": "pins",
                        "no_fetch": True
                    }
                }
            }
            
            async with session.get(
                self.suggest_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status != 200:
                    self.registrar_erro(
                        "Erro ao acessar sugestões do Pinterest",
                        {"status": response.status}
                    )
                    logger.error(f"Erro ao acessar sugestões do Pinterest: status {response.status}")
                    return []
                    
                data = await response.json()
                sugestoes = []
                
                # Extrai sugestões do response
                for item in data.get("resource_response", {}).get("data", []):
                    termo_sugerido = item.get("name", "").strip()
                    if termo_sugerido and termo_sugerido != termo:
                        sugestoes.append(termo_sugerido)
                        
                if not sugestoes:
                    logger.info(f"Nenhuma sugestão encontrada para termo: {termo}")
                self.registrar_sucesso("extracao_sugestoes", {
                    "termo": termo,
                    "total_sugestoes": len(sugestoes)
                })
                
                return sugestoes

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair sugestões do Pinterest",
                {"erro": str(e), "termo": termo}
            )
            logger.error(f"Erro ao extrair sugestões do Pinterest: {e}")
            return []

    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        """
        Extrai métricas específicas do Pinterest.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do Pinterest
        """
        try:
            session = await self._get_session()
            params = {
                "q": termo
            }
            
            async with session.get(
                self.search_url,
                params=params,
                proxy=self.config.get("proxy")
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro ao acessar Pinterest: {response.status}")
                    
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                # Extrai métricas da página
                total_pins = len(soup.find_all("div", {"class": "pin"}))
                total_boards = len(soup.find_all("div", {"class": "board"}))
                
                # Analisa categorias predominantes
                categorias = self._analisar_categorias(soup)
                categoria_principal = max(categorias.items(), key=lambda value: value[1])[0] if categorias else "other"
                
                # Calcula métricas derivadas
                volume = self._calcular_volume(total_pins)
                concorrencia = self._calcular_concorrencia(total_pins, total_boards)
                intencao = self._determinar_intencao(termo, categoria_principal)
                
                return {
                    "volume": volume,
                    "cpc": 0.0,  # Pinterest não fornece CPC
                    "concorrencia": concorrencia,
                    "intencao": intencao,
                    "categoria": categoria_principal,
                    "total_pins": total_pins,
                    "total_boards": total_boards,
                    "categorias": categorias
                }

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do Pinterest",
                {"erro": str(e), "termo": termo}
            )
            logger.error(f"Erro ao extrair métricas do Pinterest: {e}")
            return {
                "volume": 0,
                "cpc": 0.0,
                "concorrencia": 0.5,
                "intencao": IntencaoBusca.NAVEGACIONAL,
                "categoria": "other",
                "total_pins": 0,
                "total_boards": 0,
                "categorias": {}
            }

    def _analisar_categorias(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analisa as categorias predominantes nos resultados."""
        try:
            categorias = {
                "diy": 0,
                "home": 0,
                "fashion": 0,
                "food": 0,
                "travel": 0,
                "art": 0,
                "other": 0
            }
            
            # Analisa descrições e tags dos pins
            for pin in soup.find_all("div", {"class": "pin"}):
                descricao = pin.get_text().lower()
                
                if any(w in descricao for w in ["diy", "faça você mesmo", "tutorial", "how to"]):
                    categorias["diy"] += 1
                elif any(w in descricao for w in ["casa", "decoração", "home", "decor"]):
                    categorias["home"] += 1
                elif any(w in descricao for w in ["moda", "fashion", "style", "outfit"]):
                    categorias["fashion"] += 1
                elif any(w in descricao for w in ["receita", "food", "recipe", "cooking"]):
                    categorias["food"] += 1
                elif any(w in descricao for w in ["viagem", "travel", "destination", "trip"]):
                    categorias["travel"] += 1
                elif any(w in descricao for w in ["arte", "art", "design", "illustration"]):
                    categorias["art"] += 1
                else:
                    categorias["other"] += 1
                    
            return categorias
            
        except Exception:
            return {"other": 1}

    def _calcular_volume(self, total_pins: int) -> int:
        """Calcula volume estimado baseado no total de pins."""
        if total_pins == 0:
            return 10
        elif total_pins < 100:
            return 50
        elif total_pins < 1000:
            return 100
        elif total_pins < 10000:
            return 500
        elif total_pins < 100000:
            return 1000
        else:
            return 5000

    def _calcular_concorrencia(self, total_pins: int, total_boards: int) -> float:
        """Calcula nível de concorrência baseado em pins e boards."""
        if total_pins == 0:
            return 0.1
            
        # Base na quantidade de pins
        concorrencia_base = min(total_pins / 1000, 1.0)
        
        # Ajusta baseado na proporção de boards
        if total_boards > 0:
            razao_pins_boards = total_pins / total_boards
            if razao_pins_boards > 100:  # Muitos repins = alta concorrência
                concorrencia_base += 0.3
            elif razao_pins_boards > 50:
                concorrencia_base += 0.2
            elif razao_pins_boards > 20:
                concorrencia_base += 0.1
                
        return min(concorrencia_base, 1.0)

    def _determinar_intencao(self, termo: str, categoria: str) -> IntencaoBusca:
        """Determina intenção de busca baseado no termo e categoria."""
        termo_lower = termo.lower()
        
        # Análise por categoria
        if categoria in ["diy", "food"]:
            return IntencaoBusca.INFORMACIONAL
        elif categoria in ["fashion", "home"]:
            return IntencaoBusca.COMERCIAL
            
        # Análise por palavras no termo
        if any(w in termo_lower for w in ["como fazer", "diy", "tutorial", "passo a passo"]):
            return IntencaoBusca.INFORMACIONAL
        elif any(w in termo_lower for w in ["comprar", "preço", "onde encontrar"]):
            return IntencaoBusca.TRANSACIONAL
        elif any(w in termo_lower for w in ["ideias", "inspiração", "modelos"]):
            return IntencaoBusca.NAVEGACIONAL
        else:
            return IntencaoBusca.NAVEGACIONAL

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o Pinterest, usando ValidadorKeywords.
        Retorna False imediatamente se o termo for vazio ou None.
        """
        if not termo or not termo.strip():
            self.registrar_erro(
                "Termo inválido para Pinterest",
                {"termo": termo, "motivo": "vazio"}
            )
            logger.error(f"Termo inválido para Pinterest: {termo}")
            return False
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo para Pinterest",
                {"termo": termo}
            )
            logger.error(f"Termo muito longo para Pinterest: {termo}")
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
        Implementação específica de coleta de keywords do Pinterest.
        
        Args:
            termo: Termo base para busca
            limite: Número máximo de keywords a retornar
            
        Returns:
            Lista de objetos Keyword com dados do Pinterest
        """
        if not await self.validar_termo(termo) or not await self.validar_termo_especifico(termo):
            return []
        try:
            sugestoes = await self.extrair_sugestoes(termo)
            if not sugestoes:
                return []
            sugestoes = sugestoes[:limite]
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
                            "categoria": metricas.get("categoria", "other"),
                            "total_pins": metricas.get("total_pins", 0),
                            "total_boards": metricas.get("total_boards", 0),
                            "categorias": metricas.get("categorias", {})
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
                        f"Erro ao processar sugestão: {sugestao}",
                        {"erro": str(e)}
                    )
            self.registrar_sucesso("coleta_pinterest", {
                "termo_base": termo,
                "total_sugestoes": len(sugestoes),
                "keywords_geradas": len(keywords)
            })
            self.atualizar_metricas(len(keywords))
            return keywords
        except Exception as e:
            self.registrar_erro(
                "Erro durante coleta do Pinterest",
                {"erro": str(e), "termo": termo}
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

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """Stub mínimo para testes."""
        return [{} for _ in keywords]

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """Stub mínimo para testes."""
        return [IntencaoBusca.NAVEGACIONAL for _ in keywords] 