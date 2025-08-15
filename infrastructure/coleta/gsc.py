"""
Implementação do coletor de dados do Google Search Console com suporte multi-site.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import asyncio
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base_keyword import KeywordColetorBase
from shared.config import (
    GSC_CONFIG,
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
from shared.utils.normalizador_central import NormalizadorCentral

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

class GSCColetor(KeywordColetorBase):
    """Implementação do coletor de dados do Google Search Console."""

    def __init__(self, logger_=None):
        """Inicializa o coletor do GSC."""
        super().__init__(
            nome="gsc",
            config=GSC_CONFIG
        )
        self.logger = logger_ or logger
        self.credenciais = Credentials.from_authorized_user_info(
            GSC_CONFIG["credentials"]
        )
        self.service = build(
            'searchconsole',
            'v1',
            credentials=self.credenciais
        )
        self.sites = self._carregar_sites()
        self.dias_analise = GSC_CONFIG.get("janela_dados_dias", 90)
        
        # Cache com namespace específico
        self.cache = CacheDistribuido(
            namespace=CACHE_CONFIG["namespaces"]["gsc"],
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

    def _carregar_sites(self) -> Dict[str, Dict]:
        """Carrega configurações de sites do GSC."""
        sites_config = self.config.get("sites", {})
        sites_ativos = {}
        
        try:
            # Lista sites disponíveis na conta
            sites_disponiveis = self.service.sites().list().execute()
            
            for site_url, config in sites_config.items():
                if not config.get("ativo", True):
                    continue
                    
                # Verifica se temos acesso ao site
                site_info = next(
                    (string_data for string_data in sites_disponiveis.get("siteEntry", [])
                     if string_data["siteUrl"] == site_url),
                    None
                )
                
                if site_info and site_info.get("permissionLevel") in ["siteOwner", "siteFullUser"]:
                    sites_ativos[site_url] = {
                        "nome": config.get("nome", site_url),
                        "categorias": config.get("categorias", []),
                        "idiomas": config.get("idiomas", ["pt-br"]),
                        "paises": config.get("paises", ["br"]),
                        "info": site_info
                    }
                    
            if not sites_ativos:
                raise ValueError("Nenhum site ativo configurado")
                
            return sites_ativos
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao carregar sites do GSC",
                {"erro": str(e)}
            )
            raise

    @breaker
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError))
    )
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de busca do GSC com resiliência e logging estruturado.
        """
        uuid_req = str(uuid.uuid4())
        inicio = time.time()
        cache_key = f"sugestoes:{termo}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        try:
            sugestoes = set()
            data_fim = datetime.utcnow()
            data_inicio = data_fim - timedelta(days=self.dias_analise)
            for site_url, site_config in self.sites.items():
                try:
                    body = {
                        'startDate': data_inicio.strftime('%Y-%m-%data'),
                        'endDate': data_fim.strftime('%Y-%m-%data'),
                        'dimensions': ['query'],
                        'dimensionFilterGroups': [{
                            'filters': [{
                                'dimension': 'query',
                                'operator': 'contains',
                                'expression': termo
                            }]
                        }],
                        'rowLimit': 100
                    }
                    response = await asyncio.to_thread(
                        self.service.searchanalytics().query(
                            siteUrl=site_url,
                            body=body
                        ).execute
                    )
                    for row in response.get('rows', []):
                        query = row['keys'][0]
                        if query != termo:
                            sugestoes.add(query)
                except Exception as e:
                    self.logger.error({
                        "uuid": uuid_req,
                        "coletor": "gsc",
                        "termo": termo,
                        "site": site_url,
                        "status": "erro_site",
                        "erro": str(e),
                        "latencia_ms": int((time.time() - inicio) * 1000),
                        "ambiente": self.config.get("env", "dev")
                    })
            sugestoes_lista = list(sugestoes)
            await self.cache.set(
                cache_key,
                sugestoes_lista,
                ttl=CACHE_CONFIG["ttl_keywords"]
            )
            self.logger.info({
                "uuid": uuid_req,
                "coletor": "gsc",
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
                "coletor": "gsc",
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
        Extrai métricas específicas do GSC.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do GSC
        """
        try:
            # Verifica cache
            cache_key = f"metricas:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            data_fim = datetime.utcnow()
            data_inicio = data_fim - timedelta(days=self.dias_analise)
            
            metricas_agregadas = {
                "impressoes": 0,
                "cliques": 0,
                "ctr": 0.0,
                "posicao": 0.0,
                "sites": []
            }
            
            # Coleta métricas de todos os sites ativos
            for site_url, site_config in self.sites.items():
                try:
                    metricas_site = await self._extrair_metricas_query(
                        site_url,
                        termo,
                        data_inicio,
                        data_fim
                    )
                    
                    if metricas_site:
                        metricas_agregadas["impressoes"] += metricas_site["impressoes"]
                        metricas_agregadas["cliques"] += metricas_site["cliques"]
                        metricas_agregadas["sites"].append({
                            "nome": site_config["nome"],
                            "metricas": metricas_site
                        })
                        
                except Exception as e:
                    self.registrar_erro(
                        f"Erro ao extrair métricas do site {site_url}",
                        {"erro": str(e)}
                    )
            
            # Calcula médias
            total_sites = len(metricas_agregadas["sites"])
            if total_sites > 0:
                metricas_agregadas["ctr"] = (
                    metricas_agregadas["cliques"] /
                    metricas_agregadas["impressoes"]
                    if metricas_agregadas["impressoes"] > 0
                    else 0.0
                )
                metricas_agregadas["posicao"] = sum(
                    site["metricas"]["posicao"]
                    for site in metricas_agregadas["sites"]
                ) / total_sites
            
            # Adiciona métricas calculadas
            metricas_agregadas.update({
                "volume": self._calcular_volume(metricas_agregadas),
                "concorrencia": self._calcular_concorrencia(metricas_agregadas),
                "tendencia": self.analisador.calcular_tendencia(termo),
                "sazonalidade": self._analisar_sazonalidade(
                    [
                        site["metricas"]["dados_diarios"]
                        for site in metricas_agregadas["sites"]
                        if "dados_diarios" in site["metricas"]
                    ]
                )
            })
            
            # Salva no cache
            await self.cache.set(
                cache_key,
                metricas_agregadas,
                ttl=CACHE_CONFIG["ttl_metricas"]
            )
            
            # Registra acesso para análise de tendências
            self.analisador.registrar_acesso(termo)
            
            return metricas_agregadas

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do GSC",
                {"erro": str(e), "termo": termo}
            )
            return {
                "impressoes": 0,
                "cliques": 0,
                "ctr": 0.0,
                "posicao": 0.0,
                "volume": 0,
                "concorrencia": 0.5,
                "tendencia": 0,
                "sazonalidade": 0,
                "sites": []
            }

    async def _extrair_metricas_query(
        self,
        site_url: str,
        query: str,
        data_inicio: datetime,
        data_fim: datetime
    ) -> Dict:
        """
        Extrai métricas detalhadas para uma query específica.
        
        Args:
            site_url: URL do site no GSC
            query: Query para análise
            data_inicio: Data inicial do período
            data_fim: Data final do período
            
        Returns:
            Dicionário com métricas da query
        """
        try:
            # Verifica cache
            cache_key = f"metricas_query:{site_url}:{query}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
                
            # Coleta dados do período atual
            body_atual = {
                'startDate': data_inicio.strftime('%Y-%m-%data'),
                'endDate': data_fim.strftime('%Y-%m-%data'),
                'dimensions': ['query', 'date'],
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'query',
                        'operator': 'equals',
                        'expression': query
                    }]
                }]
            }
            
            # Coleta dados do período anterior para comparação
            periodo_anterior = data_fim - data_inicio
            data_inicio_anterior = data_inicio - periodo_anterior
            data_fim_anterior = data_inicio
            
            body_anterior = {
                'startDate': data_inicio_anterior.strftime('%Y-%m-%data'),
                'endDate': data_fim_anterior.strftime('%Y-%m-%data'),
                'dimensions': ['query', 'date'],
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'query',
                        'operator': 'equals',
                        'expression': query
                    }]
                }]
            }
            
            # Executa as duas consultas em paralelo
            atual_task = asyncio.create_task(
                asyncio.to_thread(
                    self.service.searchanalytics().query(
                        siteUrl=site_url,
                        body=body_atual
                    ).execute
                )
            )
            
            anterior_task = asyncio.create_task(
                asyncio.to_thread(
                    self.service.searchanalytics().query(
                        siteUrl=site_url,
                        body=body_anterior
                    ).execute
                )
            )
            
            atual_response, anterior_response = await asyncio.gather(
                atual_task,
                anterior_task
            )
            
            # Processa dados atuais
            dados_atuais = atual_response.get('rows', [])
            impressoes = sum(row['impressions'] for row in dados_atuais)
            cliques = sum(row['clicks'] for row in dados_atuais)
            ctr = cliques / impressoes if impressoes > 0 else 0
            posicao = sum(row['position'] * row['impressions'] for row in dados_atuais) / impressoes if impressoes > 0 else 0
            
            # Calcula variação em relação ao período anterior
            dados_anteriores = anterior_response.get('rows', [])
            impressoes_anterior = sum(row['impressions'] for row in dados_anteriores)
            variacao = (
                (impressoes - impressoes_anterior) / impressoes_anterior * 100
                if impressoes_anterior > 0
                else 0
            )
            
            metricas = {
                "impressoes": impressoes,
                "cliques": cliques,
                "ctr": ctr,
                "posicao": posicao,
                "variacao": variacao,
                "dados_diarios": [
                    {
                        "data": row["keys"][1],
                        "impressoes": row["impressions"],
                        "cliques": row["clicks"],
                        "ctr": row["ctr"],
                        "posicao": row["position"]
                    }
                    for row in dados_atuais
                ]
            }
            
            # Salva no cache
            await self.cache.set(
                cache_key,
                metricas,
                ttl=CACHE_CONFIG["ttl_metricas"]
            )
            
            return metricas
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas de query",
                {
                    "erro": str(e),
                    "site": site_url,
                    "query": query
                }
            )
            return None

    def _analisar_sazonalidade(self, dados_diarios_sites: List[List[Dict]]) -> float:
        """
        Analisa padrões de sazonalidade nos dados.
        
        Args:
            dados_diarios_sites: Lista de dados diários de cada site
            
        Returns:
            Score de sazonalidade (0 a 1)
        """
        try:
            if not dados_diarios_sites:
                return 0
                
            # Agrupa dados por dia da semana
            dias_semana = {index: [] for index in range(7)}
            
            for site_dados in dados_diarios_sites:
                for dado in site_dados:
                    data = datetime.strptime(dado["data"], "%Y-%m-%data")
                    dia_semana = data.weekday()
                    dias_semana[dia_semana].append(dado["impressoes"])
            
            # Calcula média e desvio por dia
            medias = {}
            desvios = {}
            
            for dia, valores in dias_semana.items():
                if valores:
                    media = sum(valores) / len(valores)
                    desvio = (
                        sum((value - media) ** 2 for value in valores) / len(valores)
                    ) ** 0.5
                    medias[dia] = media
                    desvios[dia] = desvio
            
            if not medias:
                return 0
                
            # Calcula variação entre dias
            media_geral = sum(medias.values()) / len(medias)
            variacao = sum(
                abs(media - media_geral)
                for media in medias.values()
            ) / len(medias)
            
            # Normaliza score
            max_variacao = media_geral
            score = min(variacao / max_variacao if max_variacao > 0 else 0, 1)
            
            return score
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao analisar sazonalidade",
                {"erro": str(e)}
            )
            return 0

    def _calcular_volume(self, metricas: Dict) -> int:
        """
        Calcula volume estimado baseado nas impressões.
        
        Args:
            metricas: Dicionário com métricas
            
        Returns:
            Volume estimado
        """
        impressoes = metricas.get("impressoes", 0)
        
        if impressoes == 0:
            return 10
        elif impressoes < 1000:
            return 50
        elif impressoes < 10000:
            return 100
        elif impressoes < 100000:
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
            posicao = metricas.get("posicao", 0)
            ctr = metricas.get("ctr", 0)
            
            if posicao == 0:
                return 0.5
                
            # Considera posição média e CTR
            score = (
                (1 - min(posicao / 10, 1)) * 0.7 +  # Peso maior para posição
                (ctr * 0.3)  # Peso menor para CTR
            )
            
            return min(max(score, 0), 1)
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao calcular concorrência",
                {"erro": str(e)}
            )
            return 0.5

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o GSC, usando ValidadorKeywords.
        """
        if len(termo) > 200:
            self.registrar_erro(
                "Termo muito longo para GSC",
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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gerenciamento de contexto para fechamento de sessão."""
        pass

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """Stub mínimo para testes."""
        return [IntencaoBusca.NAVEGACIONAL for _ in keywords]

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """Stub mínimo para testes."""
        return [{} for _ in keywords] 