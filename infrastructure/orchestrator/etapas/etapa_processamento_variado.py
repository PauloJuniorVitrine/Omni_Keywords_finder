"""
Etapa de Processamento Variado - Omni Keywords Finder

Versão melhorada da etapa de processamento que integra sistema de memória inteligente
para gerar clusters variados e evitar repetição.

Tracing ID: ETAPA_PROCESSAMENTO_VARIADO_001_20241227
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

from infrastructure.processamento.clusterizador_semantico import ClusterizadorSemantico
from infrastructure.processamento.analisador_semantico_cauda_longa import AnalisadorSemanticoCaudaLonga
from infrastructure.processamento.complexidade_semantica import ComplexidadeSemantica
from infrastructure.processamento.score_composto_inteligente import ScoreCompostoInteligente
from infrastructure.processamento.tendencias_cauda_longa import TendenciasCaudaLonga
from infrastructure.memory.historico_inteligente import historico_inteligente
from domain.models import Keyword, Cluster
from shared.logger import logger

@dataclass
class ProcessamentoVariadoResult:
    """Resultado da etapa de processamento variado."""
    keywords_processadas: List[Keyword]
    clusters_identificados: List[Cluster]
    clusters_novos: List[Cluster]
    clusters_alternativos: List[Dict[str, Any]]
    scores_calculados: Dict[str, float]
    tendencias_identificadas: List[Dict[str, Any]]
    tempo_execucao: float
    metadados: Dict[str, Any]

class EtapaProcessamentoVariado:
    """
    Etapa de processamento variado que integra sistema de memória inteligente.
    
    Funcionalidades:
    - Processamento de keywords com variação algorítmica
    - Geração de clusters únicos baseados no histórico
    - Sugestão de clusters alternativos
    - Análise de tendências temporais
    - Evita repetição de clusters
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a etapa de processamento variado.
        
        Args:
            config: Configurações da etapa de processamento
        """
        self.config = config
        
        # Inicializa processadores
        self.clusterizador = ClusterizadorSemantico(
            tamanho_cluster=config.get('tamanho_cluster', 5),
            min_similaridade=config.get('min_similaridade', 0.6),
            criterio_diversidade=True,
            max_clusters=config.get('max_clusters', 20)
        )
        
        self.analisador_semantico = AnalisadorSemanticoCaudaLonga()
        self.complexidade_semantica = ComplexidadeSemantica()
        self.score_composto = ScoreCompostoInteligente()
        self.tendencias = TendenciasCaudaLonga()
        
        # Configurações de variação
        self.min_clusters_novos = config.get('min_clusters_novos', 5)
        self.max_tentativas_variacao = config.get('max_tentativas_variacao', 3)
        self.diversidade_minima = config.get('diversidade_minima', 0.7)
        
        logger.info({
            "event": "etapa_processamento_variado_inicializada",
            "status": "success",
            "source": "etapa_processamento_variado.__init__",
            "details": {
                "tamanho_cluster": self.clusterizador.tamanho_cluster,
                "min_similaridade": self.clusterizador.min_similaridade,
                "max_clusters": self.clusterizador.max_clusters
            }
        })
    
    async def executar(self, keywords: List[Keyword], nicho: str, categoria: str) -> ProcessamentoVariadoResult:
        """
        Executa a etapa de processamento variado.
        
        Args:
            keywords: Lista de keywords para processar
            nicho: Nome do nicho
            categoria: Nome da categoria
            
        Returns:
            ProcessamentoVariadoResult com os dados processados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando processamento variado para nicho: {nicho} - {len(keywords)} keywords")
        
        try:
            # 1. Processar keywords com análise semântica
            keywords_processadas = await self._processar_keywords(keywords, nicho)
            
            # 2. Gerar clusters com variação algorítmica
            clusters_identificados = await self._gerar_clusters_variados(
                keywords_processadas, nicho, categoria
            )
            
            # 3. Verificar novidade dos clusters
            clusters_novos, clusters_repetidos = await self._verificar_novidade_clusters(
                clusters_identificados, nicho, categoria
            )
            
            # 4. Se não há clusters suficientes novos, gerar alternativos
            if len(clusters_novos) < self.min_clusters_novos:
                logger.info({
                    "event": "clusters_novos_insuficientes",
                    "status": "info",
                    "source": "etapa_processamento_variado.executar",
                    "details": {
                        "clusters_novos": len(clusters_novos),
                        "min_requerido": self.min_clusters_novos
                    }
                })
                
                clusters_alternativos = await self._gerar_clusters_alternativos(
                    keywords_processadas, nicho, categoria
                )
                
                # Adiciona clusters alternativos aos novos
                clusters_novos.extend(clusters_alternativos)
            
            # 5. Registrar clusters no histórico
            for cluster in clusters_novos:
                await historico_inteligente.registrar_cluster(cluster, nicho, categoria)
            
            # 6. Calcular scores e tendências
            scores_calculados = await self._calcular_scores(keywords_processadas)
            tendencias_identificadas = await self._identificar_tendencias(keywords_processadas, nicho)
            
            tempo_execucao = time.time() - inicio_tempo
            
            resultado = ProcessamentoVariadoResult(
                keywords_processadas=keywords_processadas,
                clusters_identificados=clusters_identificados,
                clusters_novos=clusters_novos,
                clusters_alternativos=[],
                scores_calculados=scores_calculados,
                tendencias_identificadas=tendencias_identificadas,
                tempo_execucao=tempo_execucao,
                metadados={
                    'nicho': nicho,
                    'categoria': categoria,
                    'total_keywords': len(keywords),
                    'total_processadas': len(keywords_processadas),
                    'total_clusters': len(clusters_identificados),
                    'total_clusters_novos': len(clusters_novos),
                    'novidade_porcentagem': len(clusters_novos) / len(clusters_identificados) if clusters_identificados else 0,
                    'config_utilizada': self.config
                }
            )
            
            logger.info({
                "event": "processamento_variado_concluido",
                "status": "success",
                "source": "etapa_processamento_variado.executar",
                "details": {
                    "nicho": nicho,
                    "total_clusters": len(clusters_identificados),
                    "total_clusters_novos": len(clusters_novos),
                    "novidade_porcentagem": resultado.metadados['novidade_porcentagem'],
                    "tempo_execucao": tempo_execucao
                }
            })
            
            return resultado
            
        except Exception as e:
            logger.error({
                "event": "erro_processamento_variado",
                "status": "error",
                "source": "etapa_processamento_variado.executar",
                "details": {"error": str(e), "nicho": nicho}
            })
            raise
    
    async def _processar_keywords(self, keywords: List[Keyword], nicho: str) -> List[Keyword]:
        """Processa keywords com análise semântica."""
        keywords_processadas = []
        
        for keyword in keywords:
            try:
                # Análise semântica
                analise_semantica = await self.analisador_semantico.analisar_keyword(keyword)
                
                # Complexidade semântica
                complexidade = await self.complexidade_semantica.calcular_complexidade(keyword)
                
                # Score composto
                score = await self.score_composto.calcular_score_composto(keyword)
                
                # Atualiza keyword com dados processados
                keyword.score = score
                keyword.metadados = keyword.metadados or {}
                keyword.metadados.update({
                    'analise_semantica': analise_semantica,
                    'complexidade': complexidade,
                    'nicho': nicho
                })
                
                keywords_processadas.append(keyword)
                
            except Exception as e:
                logger.warning({
                    "event": "erro_processamento_keyword",
                    "status": "warning",
                    "source": "etapa_processamento_variado._processar_keywords",
                    "details": {"keyword": keyword.termo, "error": str(e)}
                })
                # Adiciona keyword mesmo com erro
                keywords_processadas.append(keyword)
        
        return keywords_processadas
    
    async def _gerar_clusters_variados(self, keywords: List[Keyword], nicho: str, categoria: str) -> List[Cluster]:
        """Gera clusters com variação algorítmica."""
        # Obtém variação atual
        variacao = historico_inteligente._get_variacao_atual()
        
        # Ajusta parâmetros do clusterizador baseado na variação
        self._ajustar_clusterizador_por_variacao(variacao)
        
        # Gera clusters
        resultado_clusterizacao = self.clusterizador.gerar_clusters(
            keywords=keywords,
            categoria=categoria,
            blog_dominio=nicho
        )
        
        clusters = resultado_clusterizacao.get('clusters', [])
        
        logger.info({
            "event": "clusters_variados_gerados",
            "status": "success",
            "source": "etapa_processamento_variado._gerar_clusters_variados",
            "details": {
                "total_clusters": len(clusters),
                "variacao_utilizada": variacao.nome,
                "parametros": variacao.parametros
            }
        })
        
        return clusters
    
    def _ajustar_clusterizador_por_variacao(self, variacao):
        """Ajusta parâmetros do clusterizador baseado na variação."""
        parametros = variacao.parametros
        
        if 'min_similaridade' in parametros:
            self.clusterizador.min_similaridade = parametros['min_similaridade']
        
        if 'max_clusters' in parametros:
            self.clusterizador.max_clusters = parametros['max_clusters']
        
        # Ajusta critérios de diversidade
        if variacao.nome == "Alta Diversidade":
            self.clusterizador.criterio_diversidade = True
        elif variacao.nome == "Tendências Emergentes":
            self.clusterizador.criterio_diversidade = False
        elif variacao.nome == "Cauda Longa":
            self.clusterizador.criterio_diversidade = True
    
    async def _verificar_novidade_clusters(self, clusters: List[Cluster], nicho: str, categoria: str) -> Tuple[List[Cluster], List[Cluster]]:
        """Verifica quais clusters são novos e quais já foram processados."""
        clusters_novos = []
        clusters_repetidos = []
        
        for cluster in clusters:
            # Verifica se cluster já existe no histórico
            conn = sqlite3.connect(historico_inteligente.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cluster_id FROM historico_clusters 
                WHERE cluster_id = ? AND nicho = ? AND categoria = ?
            """, (cluster.id, nicho, categoria))
            
            if cursor.fetchone():
                clusters_repetidos.append(cluster)
            else:
                clusters_novos.append(cluster)
            
            conn.close()
        
        logger.info({
            "event": "verificacao_novidade_clusters",
            "status": "success",
            "source": "etapa_processamento_variado._verificar_novidade_clusters",
            "details": {
                "total_clusters": len(clusters),
                "clusters_novos": len(clusters_novos),
                "clusters_repetidos": len(clusters_repetidos)
            }
        })
        
        return clusters_novos, clusters_repetidos
    
    async def _gerar_clusters_alternativos(self, keywords: List[Keyword], nicho: str, categoria: str) -> List[Cluster]:
        """Gera clusters alternativos quando não há suficientes novos."""
        clusters_alternativos = []
        
        # Obtém sugestões do histórico
        sugestoes = await historico_inteligente.sugerir_clusters_alternativos(
            keywords, nicho, categoria
        )
        
        # Gera clusters baseados nas sugestões
        for sugestao in sugestoes:
            if sugestao['tipo'] == 'cluster_alternativo':
                # Cria cluster baseado na sugestão
                cluster = await self._criar_cluster_por_sugestao(
                    sugestao, keywords, nicho, categoria
                )
                if cluster:
                    clusters_alternativos.append(cluster)
        
        logger.info({
            "event": "clusters_alternativos_gerados",
            "status": "success",
            "source": "etapa_processamento_variado._gerar_clusters_alternativos",
            "details": {
                "total_alternativos": len(clusters_alternativos),
                "sugestoes_processadas": len(sugestoes)
            }
        })
        
        return clusters_alternativos
    
    async def _criar_cluster_por_sugestao(self, sugestao: Dict[str, Any], keywords: List[Keyword], nicho: str, categoria: str) -> Optional[Cluster]:
        """Cria cluster baseado em uma sugestão do histórico."""
        try:
            # Filtra keywords que estão na sugestão
            keywords_sugeridas = sugestao.get('keywords_sugeridas', [])
            keywords_cluster = [
                kw for kw in keywords
                if kw.termo.lower() in [key.lower() for key in keywords_sugeridas]
            ]
            
            if len(keywords_cluster) < 3:  # Mínimo para cluster
                return None
            
            # Cria cluster
            cluster = Cluster(
                id=f"alt_{len(keywords_cluster)}_{hash(tuple([kw.termo for kw in keywords_cluster]))}",
                keywords=keywords_cluster,
                similaridade_media=sugestao.get('score_historico', 0.7),
                fase_funil="awareness",
                categoria=categoria,
                blog_dominio=nicho,
                data_criacao=datetime.utcnow(),
                status_geracao="alternativo"
            )
            
            return cluster
            
        except Exception as e:
            logger.warning({
                "event": "erro_criacao_cluster_alternativo",
                "status": "warning",
                "source": "etapa_processamento_variado._criar_cluster_por_sugestao",
                "details": {"error": str(e)}
            })
            return None
    
    async def _calcular_scores(self, keywords: List[Keyword]) -> Dict[str, float]:
        """Calcula scores para as keywords processadas."""
        scores = {}
        
        for keyword in keywords:
            try:
                score = await self.score_composto.calcular_score_composto(keyword)
                scores[keyword.termo] = score
            except Exception as e:
                logger.warning({
                    "event": "erro_calculo_score",
                    "status": "warning",
                    "source": "etapa_processamento_variado._calcular_scores",
                    "details": {"keyword": keyword.termo, "error": str(e)}
                })
                scores[keyword.termo] = 0.0
        
        return scores
    
    async def _identificar_tendencias(self, keywords: List[Keyword], nicho: str) -> List[Dict[str, Any]]:
        """Identifica tendências nas keywords processadas."""
        try:
            tendencias = await self.tendencias.identificar_tendencias(keywords, nicho)
            return tendencias
        except Exception as e:
            logger.warning({
                "event": "erro_identificacao_tendencias",
                "status": "warning",
                "source": "etapa_processamento_variado._identificar_tendencias",
                "details": {"error": str(e)}
            })
            return [] 