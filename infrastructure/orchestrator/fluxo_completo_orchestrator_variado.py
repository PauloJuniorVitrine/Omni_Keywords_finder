"""
Orquestrador Completo Variado - Omni Keywords Finder

Versão melhorada do orquestrador que integra sistema de memória inteligente
para garantir variação semanal e evitar repetição de conteúdo.

Tracing ID: ORCHESTRADOR_VARIADO_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import sys
from datetime import datetime

# Adicionar caminho para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.orchestrator.etapas.etapa_coleta_variada import EtapaColetaVariada
from infrastructure.orchestrator.etapas.etapa_processamento_variado import EtapaProcessamentoVariado
from infrastructure.orchestrator.etapas.etapa_geracao import EtapaGeracao
from infrastructure.orchestrator.etapas.etapa_exportacao import EtapaExportacao
from infrastructure.memory.historico_inteligente import historico_inteligente
from domain.models import Keyword, Cluster
from shared.logger import logger

@dataclass
class OrquestradorVariadoResult:
    """Resultado do orquestrador variado."""
    keywords_coletadas: List[Keyword]
    keywords_novas: List[Keyword]
    clusters_gerados: List[Cluster]
    clusters_novos: List[Cluster]
    artigos_gerados: List[Dict[str, Any]]
    arquivos_exportados: List[str]
    tempo_execucao_total: float
    estatisticas_historico: Dict[str, Any]
    metadados: Dict[str, Any]

class FluxoCompletoOrchestratorVariado:
    """
    Orquestrador completo variado que integra sistema de memória inteligente.
    
    Funcionalidades:
    - Fluxo completo de coleta, processamento, geração e exportação
    - Variação algorítmica semanal automática
    - Evita repetição de keywords e clusters
    - Sugestões de clusters alternativos
    - Análise de tendências temporais
    - Relatórios de performance
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o orquestrador variado.
        
        Args:
            config: Configurações do orquestrador
        """
        self.config = config
        
        # Inicializa etapas
        self.etapa_coleta = EtapaColetaVariada(config.get('coleta', {}))
        self.etapa_processamento = EtapaProcessamentoVariado(config.get('processamento', {}))
        self.etapa_geracao = EtapaGeracao(config.get('geracao', {}))
        self.etapa_exportacao = EtapaExportacao(config.get('exportacao', {}))
        
        # Configurações de variação
        self.verificar_novidade = config.get('verificar_novidade', True)
        self.gerar_alternativas = config.get('gerar_alternativas', True)
        self.analisar_tendencias = config.get('analisar_tendencias', True)
        
        logger.info({
            "event": "orquestrador_variado_inicializado",
            "status": "success",
            "source": "fluxo_completo_orchestrator_variado.__init__",
            "details": {
                "verificar_novidade": self.verificar_novidade,
                "gerar_alternativas": self.gerar_alternativas,
                "analisar_tendencias": self.analisar_tendencias
            }
        })
    
    async def executar_fluxo_completo(
        self,
        termos_iniciais: List[str],
        nicho: str,
        categoria: str,
        config_nicho: Dict[str, Any]
    ) -> OrquestradorVariadoResult:
        """
        Executa o fluxo completo variado.
        
        Args:
            termos_iniciais: Termos iniciais para busca
            nicho: Nome do nicho
            categoria: Nome da categoria
            config_nicho: Configurações específicas do nicho
            
        Returns:
            OrquestradorVariadoResult com todos os dados processados
        """
        inicio_tempo = time.time()
        logger.info(f"Iniciando fluxo completo variado para nicho: {nicho}")
        
        try:
            # 1. ETAPA DE COLETA VARIADA
            logger.info("=== ETAPA 1: COLETA VARIADA ===")
            resultado_coleta = await self.etapa_coleta.executar(
                termos_iniciais, nicho, categoria, config_nicho
            )
            
            # 2. ETAPA DE PROCESSAMENTO VARIADO
            logger.info("=== ETAPA 2: PROCESSAMENTO VARIADO ===")
            resultado_processamento = await self.etapa_processamento.executar(
                resultado_coleta.keywords_novas, nicho, categoria
            )
            
            # 3. ETAPA DE GERAÇÃO
            logger.info("=== ETAPA 3: GERAÇÃO ===")
            resultado_geracao = await self.etapa_geracao.executar(
                resultado_processamento.clusters_novos, nicho, categoria
            )
            
            # 4. ETAPA DE EXPORTAÇÃO
            logger.info("=== ETAPA 4: EXPORTAÇÃO ===")
            resultado_exportacao = await self.etapa_exportacao.executar(
                resultado_geracao.artigos_gerados, nicho, categoria
            )
            
            # 5. ANÁLISE DE TENDÊNCIAS (OPCIONAL)
            estatisticas_historico = {}
            if self.analisar_tendencias:
                logger.info("=== ANÁLISE DE TENDÊNCIAS ===")
                estatisticas_historico = await historico_inteligente.obter_estatisticas_historico(nicho)
            
            tempo_execucao_total = time.time() - inicio_tempo
            
            # 6. GERAÇÃO DE RELATÓRIO FINAL
            resultado_final = OrquestradorVariadoResult(
                keywords_coletadas=resultado_coleta.keywords_coletadas,
                keywords_novas=resultado_coleta.keywords_novas,
                clusters_gerados=resultado_processamento.clusters_identificados,
                clusters_novos=resultado_processamento.clusters_novos,
                artigos_gerados=resultado_geracao.artigos_gerados,
                arquivos_exportados=resultado_exportacao.arquivos_exportados,
                tempo_execucao_total=tempo_execucao_total,
                estatisticas_historico=estatisticas_historico,
                metadados={
                    'nicho': nicho,
                    'categoria': categoria,
                    'termos_iniciais': termos_iniciais,
                    'variacao_atual': historico_inteligente._get_variacao_atual().nome,
                    'semana_atual': historico_inteligente._get_semana_atual(),
                    'config_utilizada': self.config,
                    'performance': {
                        'tempo_coleta': resultado_coleta.tempo_execucao,
                        'tempo_processamento': resultado_processamento.tempo_execucao,
                        'tempo_geracao': resultado_geracao.tempo_execucao,
                        'tempo_exportacao': resultado_exportacao.tempo_execucao,
                        'tempo_total': tempo_execucao_total
                    },
                    'qualidade': {
                        'novidade_keywords': len(resultado_coleta.keywords_novas) / len(resultado_coleta.keywords_coletadas) if resultado_coleta.keywords_coletadas else 0,
                        'novidade_clusters': len(resultado_processamento.clusters_novos) / len(resultado_processamento.clusters_identificados) if resultado_processamento.clusters_identificados else 0,
                        'sugestoes_geradas': len(resultado_coleta.sugestoes_clusters)
                    }
                }
            )
            
            # 7. LOG DE SUCESSO
            logger.info({
                "event": "fluxo_completo_variado_concluido",
                "status": "success",
                "source": "fluxo_completo_orchestrator_variado.executar_fluxo_completo",
                "details": {
                    "nicho": nicho,
                    "tempo_execucao_total": tempo_execucao_total,
                    "keywords_coletadas": len(resultado_coleta.keywords_coletadas),
                    "keywords_novas": len(resultado_coleta.keywords_novas),
                    "clusters_gerados": len(resultado_processamento.clusters_identificados),
                    "clusters_novos": len(resultado_processamento.clusters_novos),
                    "artigos_gerados": len(resultado_geracao.artigos_gerados),
                    "arquivos_exportados": len(resultado_exportacao.arquivos_exportados),
                    "variacao_utilizada": historico_inteligente._get_variacao_atual().nome
                }
            })
            
            return resultado_final
            
        except Exception as e:
            logger.error({
                "event": "erro_fluxo_completo_variado",
                "status": "error",
                "source": "fluxo_completo_orchestrator_variado.executar_fluxo_completo",
                "details": {"error": str(e), "nicho": nicho}
            })
            raise
    
    async def executar_fluxo_semanal(
        self,
        nichos_config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, OrquestradorVariadoResult]:
        """
        Executa fluxo completo para múltiplos nichos com variação semanal.
        
        Args:
            nichos_config: Configuração dos nichos a processar
            
        Returns:
            Dicionário com resultados por nicho
        """
        logger.info(f"Iniciando fluxo semanal para {len(nichos_config)} nichos")
        
        resultados = {}
        
        for nicho, config in nichos_config.items():
            try:
                logger.info(f"Processando nicho: {nicho}")
                
                resultado = await self.executar_fluxo_completo(
                    termos_iniciais=config['termos_iniciais'],
                    nicho=nicho,
                    categoria=config.get('categoria', 'geral'),
                    config_nicho=config
                )
                
                resultados[nicho] = resultado
                
                # Aguarda entre nichos para evitar sobrecarga
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error({
                    "event": "erro_processamento_nicho",
                    "status": "error",
                    "source": "fluxo_completo_orchestrator_variado.executar_fluxo_semanal",
                    "details": {"nicho": nicho, "error": str(e)}
                })
                # Continua com próximo nicho
                continue
        
        # Gera relatório consolidado
        await self._gerar_relatorio_consolidado(resultados)
        
        return resultados
    
    async def _gerar_relatorio_consolidado(self, resultados: Dict[str, OrquestradorVariadoResult]):
        """Gera relatório consolidado do fluxo semanal."""
        try:
            total_keywords = sum(len(r.keywords_coletadas) for r in resultados.values())
            total_keywords_novas = sum(len(r.keywords_novas) for r in resultados.values())
            total_clusters = sum(len(r.clusters_gerados) for r in resultados.values())
            total_clusters_novos = sum(len(r.clusters_novos) for r in resultados.values())
            total_artigos = sum(len(r.artigos_gerados) for r in resultados.values())
            tempo_total = sum(r.tempo_execucao_total for r in resultados.values())
            
            relatorio = {
                "data_geracao": datetime.now().isoformat(),
                "resumo": {
                    "nichos_processados": len(resultados),
                    "total_keywords": total_keywords,
                    "total_keywords_novas": total_keywords_novas,
                    "total_clusters": total_clusters,
                    "total_clusters_novos": total_clusters_novos,
                    "total_artigos": total_artigos,
                    "tempo_total": tempo_total
                },
                "performance": {
                    "novidade_media_keywords": total_keywords_novas / total_keywords if total_keywords > 0 else 0,
                    "novidade_media_clusters": total_clusters_novos / total_clusters if total_clusters > 0 else 0,
                    "tempo_medio_por_nicho": tempo_total / len(resultados) if resultados else 0
                },
                "nichos": {
                    nicho: {
                        "keywords_coletadas": len(r.keywords_coletadas),
                        "keywords_novas": len(r.keywords_novas),
                        "clusters_gerados": len(r.clusters_gerados),
                        "clusters_novos": len(r.clusters_novos),
                        "artigos_gerados": len(r.artigos_gerados),
                        "tempo_execucao": r.tempo_execucao_total
                    }
                    for nicho, r in resultados.items()
                }
            }
            
            # Salva relatório
            from shared.utils import salvar_json
            await salvar_json(relatorio, f"relatorios/fluxo_semanal_{datetime.now().strftime('%Y%m%data')}.json")
            
            logger.info({
                "event": "relatorio_consolidado_gerado",
                "status": "success",
                "source": "fluxo_completo_orchestrator_variado._gerar_relatorio_consolidado",
                "details": {
                    "nichos_processados": len(resultados),
                    "total_keywords": total_keywords,
                    "total_artigos": total_artigos
                }
            })
            
        except Exception as e:
            logger.error({
                "event": "erro_geracao_relatorio",
                "status": "error",
                "source": "fluxo_completo_orchestrator_variado._gerar_relatorio_consolidado",
                "details": {"error": str(e)}
            })
    
    async def obter_estatisticas_variacao(self, nicho: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de variação para um nicho.
        
        Args:
            nicho: Nome do nicho
            
        Returns:
            Dicionário com estatísticas
        """
        try:
            # Estatísticas do histórico
            estatisticas_historico = await historico_inteligente.obter_estatisticas_historico(nicho)
            
            # Variação atual
            variacao_atual = historico_inteligente._get_variacao_atual()
            semana_atual = historico_inteligente._get_semana_atual()
            
            return {
                "variacao_atual": {
                    "nome": variacao_atual.nome,
                    "descricao": variacao_atual.descricao,
                    "parametros": variacao_atual.parametros
                },
                "semana_atual": semana_atual,
                "estatisticas_historico": estatisticas_historico,
                "proxima_variacao": self._calcular_proxima_variacao(variacao_atual)
            }
            
        except Exception as e:
            logger.error({
                "event": "erro_estatisticas_variacao",
                "status": "error",
                "source": "fluxo_completo_orchestrator_variado.obter_estatisticas_variacao",
                "details": {"error": str(e), "nicho": nicho}
            })
            return {}
    
    def _calcular_proxima_variacao(self, variacao_atual) -> Dict[str, Any]:
        """Calcula qual será a próxima variação."""
        variacoes = list(historico_inteligente.variacoes_algoritmicas.keys())
        indice_atual = variacoes.index(f"semana_{variacoes.index(variacao_atual.nome) + 1}")
        proxima_indice = (indice_atual + 1) % len(variacoes)
        proxima_variacao = historico_inteligente.variacoes_algoritmicas[variacoes[proxima_indice]]
        
        return {
            "nome": proxima_variacao.nome,
            "descricao": proxima_variacao.descricao,
            "parametros": proxima_variacao.parametros
        }

# Instância global
orchestrator_variado = FluxoCompletoOrchestratorVariado({
    'coleta': {
        'max_keywords_por_fonte': 50,
        'min_novidade_porcentagem': 0.7,
        'max_tentativas_variacao': 3
    },
    'processamento': {
        'tamanho_cluster': 5,
        'min_similaridade': 0.6,
        'max_clusters': 20,
        'min_clusters_novos': 5,
        'diversidade_minima': 0.7
    },
    'geracao': {
        'max_artigos_por_cluster': 5,
        'qualidade_minima': 0.7
    },
    'exportacao': {
        'formatos': ['json', 'csv', 'xlsx'],
        'incluir_metadados': True
    },
    'verificar_novidade': True,
    'gerar_alternativas': True,
    'analisar_tendencias': True
}) 