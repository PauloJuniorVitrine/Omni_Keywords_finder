"""
Etapa de Coleta Variada - Omni Keywords Finder

Versão melhorada da etapa de coleta que integra sistema de memória inteligente
para garantir variação semanal e evitar repetição de keywords.

Tracing ID: ETAPA_COLETA_VARIADA_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys

# Adicionar caminho para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.coleta.base_keyword import KeywordColetorBase
from infrastructure.coleta.google_suggest import GoogleSuggestColetor
from infrastructure.coleta.google_keyword_planner import GoogleKeywordPlannerColetor
from infrastructure.coleta.google_trends import GoogleTrendsColetor
from infrastructure.coleta.youtube import YouTubeColetor
from infrastructure.coleta.amazon import AmazonColetor
from infrastructure.coleta.bing import BingColetor
from infrastructure.coleta.yahoo import YahooColetor
from infrastructure.coleta.duckduckgo import DuckDuckGoColetor
from infrastructure.coleta.reddit import RedditColetor
from infrastructure.coleta.quora import QuoraColetor
from infrastructure.coleta.twitter import TwitterColetor
from infrastructure.coleta.facebook import FacebookColetor
from infrastructure.memory.historico_inteligente import historico_inteligente
from domain.models import Keyword
from shared.logger import logger

@dataclass
class ColetaVariadaResult:
    """Resultado da etapa de coleta variada."""
    keywords_coletadas: List[Keyword]
    keywords_novas: List[Keyword]
    keywords_repetidas: List[Keyword]
    sugestoes_clusters: List[Dict[str, Any]]
    tempo_execucao: float
    metadados: Dict[str, Any]

class EtapaColetaVariada:
    """
    Etapa de coleta variada que integra sistema de memória inteligente.
    
    Funcionalidades:
    - Coleta de keywords de múltiplas fontes
    - Verificação de novidade baseada no histórico
    - Sugestão de clusters alternativos
    - Variação algorítmica semanal
    - Evita repetição de conteúdo
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a etapa de coleta variada.
        
        Args:
            config: Configurações da etapa de coleta
        """
        self.config = config
        self.coletores = self._inicializar_coletores()
        
        # Configurações de variação
        self.max_keywords_por_fonte = config.get('max_keywords_por_fonte', 50)
        self.min_novidade_porcentagem = config.get('min_novidade_porcentagem', 0.7)
        self.max_tentativas_variacao = config.get('max_tentativas_variacao', 3)
        
        logger.info({
            "event": "etapa_coleta_variada_inicializada",
            "status": "success",
            "source": "etapa_coleta_variada.__init__",
            "details": {
                "coletores_configurados": len(self.coletores),
                "max_keywords_por_fonte": self.max_keywords_por_fonte,
                "min_novidade_porcentagem": self.min_novidade_porcentagem
            }
        })
    
    def _inicializar_coletores(self) -> Dict[str, KeywordColetorBase]:
        """Inicializa todos os coletores disponíveis."""
        coletores = {}
        
        # Coletores principais
        coletores_config = {
            'google_suggest': GoogleSuggestColetor,
            'google_keyword_planner': GoogleKeywordPlannerColetor,
            'google_trends': GoogleTrendsColetor,
            'youtube': YouTubeColetor,
            'amazon': AmazonColetor,
            'bing': BingColetor,
            'yahoo': YahooColetor,
            'duckduckgo': DuckDuckGoColetor,
            'reddit': RedditColetor,
            'quora': QuoraColetor,
            'twitter': TwitterColetor,
            'facebook': FacebookColetor
        }
        
        for nome, coletor_class in coletores_config.items():
            try:
                coletores[nome] = coletor_class()
                logger.info({
                    "event": "coletor_inicializado",
                    "status": "success",
                    "source": "etapa_coleta_variada._inicializar_coletores",
                    "details": {"coletor": nome}
                })
            except Exception as e:
                logger.warning({
                    "event": "erro_inicializacao_coletor",
                    "status": "warning",
                    "source": "etapa_coleta_variada._inicializar_coletores",
                    "details": {"coletor": nome, "error": str(e)}
                })
        
        return coletores
    
    async def executar(
        self, 
        termos_iniciais: List[str], 
        nicho: str,
        categoria: str,
        config_nicho: Dict[str, Any]
    ) -> ColetaVariadaResult:
        """
        Executa a etapa de coleta variada.
        
        Args:
            termos_iniciais: Termos iniciais para busca
            nicho: Nome do nicho
            categoria: Nome da categoria
            config_nicho: Configurações específicas do nicho
            
        Returns:
            ColetaVariadaResult com os dados coletados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando coleta variada para nicho: {nicho} - {len(termos_iniciais)} termos iniciais")
        
        try:
            # 1. Coleta inicial de keywords
            keywords_coletadas = await self._coletar_keywords_inicial(termos_iniciais, nicho)
            
            # 2. Verificar novidade baseada no histórico
            keywords_novas, keywords_repetidas = await historico_inteligente.verificar_novidade_keywords(
                keywords_coletadas, nicho
            )
            
            # 3. Se não há keywords suficientes novas, tentar variação
            if len(keywords_novas) / len(keywords_coletadas) < self.min_novidade_porcentagem:
                logger.info({
                    "event": "novidade_insuficiente",
                    "status": "info",
                    "source": "etapa_coleta_variada.executar",
                    "details": {
                        "novidade_porcentagem": len(keywords_novas) / len(keywords_coletadas),
                        "min_requerido": self.min_novidade_porcentagem
                    }
                })
                
                keywords_variadas = await self._coletar_keywords_variadas(
                    termos_iniciais, nicho, categoria
                )
                
                # Adiciona keywords variadas às novas
                keywords_novas.extend(keywords_variadas)
            
            # 4. Registrar keywords no histórico
            await historico_inteligente.registrar_keywords(keywords_novas, nicho, categoria)
            
            # 5. Gerar sugestões de clusters alternativos
            sugestoes_clusters = await historico_inteligente.sugerir_clusters_alternativos(
                keywords_novas, nicho, categoria
            )
            
            tempo_execucao = time.time() - inicio_tempo
            
            resultado = ColetaVariadaResult(
                keywords_coletadas=keywords_coletadas,
                keywords_novas=keywords_novas,
                keywords_repetidas=keywords_repetidas,
                sugestoes_clusters=sugestoes_clusters,
                tempo_execucao=tempo_execucao,
                metadados={
                    'nicho': nicho,
                    'categoria': categoria,
                    'termos_iniciais': termos_iniciais,
                    'total_coletadas': len(keywords_coletadas),
                    'total_novas': len(keywords_novas),
                    'total_repetidas': len(keywords_repetidas),
                    'novidade_porcentagem': len(keywords_novas) / len(keywords_coletadas) if keywords_coletadas else 0,
                    'sugestoes_geradas': len(sugestoes_clusters),
                    'config_utilizada': self.config
                }
            )
            
            logger.info({
                "event": "coleta_variada_concluida",
                "status": "success",
                "source": "etapa_coleta_variada.executar",
                "details": {
                    "nicho": nicho,
                    "total_coletadas": len(keywords_coletadas),
                    "total_novas": len(keywords_novas),
                    "novidade_porcentagem": resultado.metadados['novidade_porcentagem'],
                    "tempo_execucao": tempo_execucao
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "event": "erro_coleta_variada",
                "status": "error",
                "source": "etapa_coleta_variada.executar",
                "details": {"error": str(e), "nicho": nicho}
            })
            raise
    
    async def _coletar_keywords_inicial(self, termos: List[str], nicho: str) -> List[Keyword]:
        """Executa coleta inicial de keywords."""
        keywords_coletadas = []
        
        # Seleciona coletores baseados na configuração
        coletores_ativos = self._selecionar_coletores_ativos(nicho)
        
        # Executa coleta em paralelo
        tasks = []
        for nome_coletor, coletor in coletores_ativos.items():
            task = self._coletar_por_fonte(coletor, termos, nome_coletor)
            tasks.append(task)
        
        resultados = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processa resultados
        for resultado in resultados:
            if isinstance(resultado, list):
                keywords_coletadas.extend(resultado)
            else:
                logger.warning({
                    "event": "erro_coleta_fonte",
                    "status": "warning",
                    "source": "etapa_coleta_variada._coletar_keywords_inicial",
                    "details": {"error": str(resultado)}
                })
        
        # Remove duplicatas
        keywords_unicas = self._remover_duplicatas(keywords_coletadas)
        
        logger.info({
            "event": "coleta_inicial_concluida",
            "status": "success",
            "source": "etapa_coleta_variada._coletar_keywords_inicial",
            "details": {
                "total_keywords": len(keywords_unicas),
                "coletores_utilizados": len(coletores_ativos)
            }
        })
        
        return keywords_unicas
    
    async def _coletar_keywords_variadas(self, termos: List[str], nicho: str, categoria: str) -> List[Keyword]:
        """Coleta keywords com variação algorítmica para aumentar novidade."""
        keywords_variadas = []
        
        # Obtém variação atual
        variacao = historico_inteligente._get_variacao_atual()
        
        # Gera termos variados baseados na variação
        termos_variados = self._gerar_termos_variados(termos, variacao)
        
        # Seleciona coletores específicos para variação
        coletores_variacao = self._selecionar_coletores_variacao(variacao)
        
        # Executa coleta com termos variados
        for nome_coletor, coletor in coletores_variacao.items():
            try:
                keywords_fonte = await self._coletar_por_fonte(coletor, termos_variados, nome_coletor)
                keywords_variadas.extend(keywords_fonte)
                
                # Verifica se já tem keywords suficientes
                if len(keywords_variadas) >= self.max_keywords_por_fonte * 2:
                    break
                    
            except Exception as e:
                logger.warning({
                    "event": "erro_coleta_variacao",
                    "status": "warning",
                    "source": "etapa_coleta_variada._coletar_keywords_variadas",
                    "details": {"coletor": nome_coletor, "error": str(e)}
                })
        
        # Remove duplicatas
        keywords_variadas_unicas = self._remover_duplicatas(keywords_variadas)
        
        logger.info({
            "event": "coleta_variada_concluida",
            "status": "success",
            "source": "etapa_coleta_variada._coletar_keywords_variadas",
            "details": {
                "total_keywords_variadas": len(keywords_variadas_unicas),
                "variacao_utilizada": variacao.nome,
                "termos_variados": len(termos_variados)
            }
        })
        
        return keywords_variadas_unicas
    
    def _selecionar_coletores_ativos(self, nicho: str) -> Dict[str, KeywordColetorBase]:
        """Seleciona coletores ativos baseados na configuração."""
        coletores_ativos = {}
        
        # Configuração padrão de coletores
        coletores_padrao = [
            'google_suggest',
            'google_trends',
            'youtube',
            'bing'
        ]
        
        # Adiciona coletores específicos do nicho se configurado
        coletores_nicho = self.config.get('coletores_por_nicho', {}).get(nicho, [])
        
        for nome in coletores_padrao + coletores_nicho:
            if nome in self.coletores:
                coletores_ativos[nome] = self.coletores[nome]
        
        return coletores_ativos
    
    def _selecionar_coletores_variacao(self, variacao) -> Dict[str, KeywordColetorBase]:
        """Seleciona coletores específicos para variação algorítmica."""
        coletores_variacao = {}
        
        if variacao.nome == "Alta Diversidade":
            # Coletores que geram keywords diversas
            coletores_diversos = ['reddit', 'quora', 'duckduckgo', 'yahoo']
            for nome in coletores_diversos:
                if nome in self.coletores:
                    coletores_variacao[nome] = self.coletores[nome]
        
        elif variacao.nome == "Tendências Emergentes":
            # Coletores que capturam tendências
            coletores_tendencias = ['google_trends', 'twitter', 'youtube', 'reddit']
            for nome in coletores_tendencias:
                if nome in self.coletores:
                    coletores_variacao[nome] = self.coletores[nome]
        
        elif variacao.nome == "Cauda Longa":
            # Coletores que geram keywords específicas
            coletores_cauda_longa = ['amazon', 'bing', 'duckduckgo', 'yahoo']
            for nome in coletores_cauda_longa:
                if nome in self.coletores:
                    coletores_variacao[nome] = self.coletores[nome]
        
        else:  # Otimização Balanceada
            # Usa todos os coletores disponíveis
            coletores_variacao = self.coletores.copy()
        
        return coletores_variacao
    
    def _gerar_termos_variados(self, termos: List[str], variacao) -> List[str]:
        """Gera termos variados baseados na variação algorítmica."""
        termos_variados = []
        
        # Adiciona termos originais
        termos_variados.extend(termos)
        
        # Gera variações baseadas na estratégia
        if variacao.nome == "Alta Diversidade":
            # Adiciona sinônimos e termos relacionados
            for termo in termos:
                termos_variados.extend(self._gerar_sinonimos(termo))
                termos_variados.extend(self._gerar_termos_relacionados(termo))
        
        elif variacao.nome == "Tendências Emergentes":
            # Adiciona termos de tendência
            for termo in termos:
                termos_variados.extend(self._gerar_termos_tendencia(termo))
        
        elif variacao.nome == "Cauda Longa":
            # Adiciona termos específicos e longos
            for termo in termos:
                termos_variados.extend(self._gerar_termos_cauda_longa(termo))
        
        # Remove duplicatas
        return list(set(termos_variados))
    
    def _gerar_sinonimos(self, termo: str) -> List[str]:
        """Gera sinônimos para um termo (implementação básica)."""
        # Dicionário básico de sinônimos
        sinonimos = {
            'melhor': ['top', 'excelente', 'superior', 'ótimo'],
            'como': ['tutorial', 'guia', 'passo a passo'],
            'preço': ['valor', 'custo', 'quanto custa'],
            'reviews': ['avaliações', 'opiniões', 'críticas'],
            'comparativo': ['comparação', 'vs', 'diferenças'],
            'dicas': ['truques', 'conselhos', 'sugestões']
        }
        
        for palavra, lista_sinonimos in sinonimos.items():
            if palavra in termo.lower():
                return [termo.replace(palavra, sinonimo) for sinonimo in lista_sinonimos]
        
        return []
    
    def _gerar_termos_relacionados(self, termo: str) -> List[str]:
        """Gera termos relacionados (implementação básica)."""
        # Adiciona sufixos comuns
        sufixos = [' 2024', ' tutorial', ' guia', ' dicas', ' reviews']
        return [termo + sufixo for sufixo in sufixos]
    
    def _gerar_termos_tendencia(self, termo: str) -> List[str]:
        """Gera termos de tendência (implementação básica)."""
        # Adiciona termos de tendência
        tendencias = ['tendência', 'popular', 'viral', 'em alta', 'trending']
        return [termo + ' ' + tendencia for tendencia in tendencias]
    
    def _gerar_termos_cauda_longa(self, termo: str) -> List[str]:
        """Gera termos de cauda longa (implementação básica)."""
        # Adiciona modificadores específicos
        modificadores = [
            'melhor preço', 'mais barato', 'onde comprar',
            'como escolher', 'qual comprar', 'diferenças entre'
        ]
        return [modificador + ' ' + termo for modificador in modificadores]
    
    async def _coletar_por_fonte(self, coletor: KeywordColetorBase, termos: List[str], nome_fonte: str) -> List[Keyword]:
        """Coleta keywords de uma fonte específica."""
        try:
            # Limita número de termos por fonte
            termos_limitados = termos[:self.max_keywords_por_fonte]
            
            keywords = await coletor.coletar_keywords(termos_limitados)
            
            logger.info({
                "event": "coleta_fonte_concluida",
                "status": "success",
                "source": "etapa_coleta_variada._coletar_por_fonte",
                "details": {
                    "fonte": nome_fonte,
                    "termos_enviados": len(termos_limitados),
                    "keywords_coletadas": len(keywords)
                }
            })
            
            return keywords
            
        except Exception as e:
            logger.error({
                "event": "erro_coleta_fonte",
                "status": "error",
                "source": "etapa_coleta_variada._coletar_por_fonte",
                "details": {"fonte": nome_fonte, "error": str(e)}
            })
            return []
    
    def _remover_duplicatas(self, keywords: List[Keyword]) -> List[Keyword]:
        """Remove keywords duplicadas baseadas no termo."""
        termos_unicos = set()
        keywords_unicas = []
        
        for keyword in keywords:
            termo_normalizado = keyword.termo.lower().strip()
            if termo_normalizado not in termos_unicos:
                termos_unicos.add(termo_normalizado)
                keywords_unicas.append(keyword)
        
        return keywords_unicas 