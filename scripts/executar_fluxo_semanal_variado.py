#!/usr/bin/env python3
"""
Script de Execução do Fluxo Semanal Variado - Omni Keywords Finder

Executa automaticamente o fluxo completo com variação semanal para evitar
repetição de keywords e clusters.

Tracing ID: SCRIPT_FLUXO_SEMANAL_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Adicionar caminho para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.orchestrator.fluxo_completo_orchestrator_variado import orchestrator_variado
from infrastructure.memory.historico_inteligente import historico_inteligente
from shared.logger import logger

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler(f'logs/fluxo_semanal_{datetime.now().strftime("%Y%m%data")}.log'),
        logging.StreamHandler()
    ]
)

# Configuração dos nichos para execução semanal
NICHOS_CONFIG = {
    "tecnologia": {
        "termos_iniciais": [
            "melhor smartphone 2024",
            "laptop gaming",
            "inteligência artificial",
            "programação python",
            "desenvolvimento web"
        ],
        "categoria": "tecnologia",
        "coletores_prioritarios": ["google_suggest", "google_trends", "youtube", "reddit"],
        "max_keywords": 200,
        "min_score": 0.6
    },
    "saude": {
        "termos_iniciais": [
            "exercícios em casa",
            "alimentação saudável",
            "meditação",
            "bem-estar mental",
            "fitness"
        ],
        "categoria": "saude",
        "coletores_prioritarios": ["google_suggest", "youtube", "reddit", "quora"],
        "max_keywords": 150,
        "min_score": 0.7
    },
    "financas": {
        "termos_iniciais": [
            "investimentos para iniciantes",
            "economia pessoal",
            "criptomoedas",
            "bolsa de valores",
            "poupança"
        ],
        "categoria": "financas",
        "coletores_prioritarios": ["google_suggest", "google_trends", "reddit", "quora"],
        "max_keywords": 180,
        "min_score": 0.65
    },
    "educacao": {
        "termos_iniciais": [
            "cursos online",
            "aprendizado de idiomas",
            "estudar para concursos",
            "técnicas de estudo",
            "educação infantil"
        ],
        "categoria": "educacao",
        "coletores_prioritarios": ["google_suggest", "youtube", "quora", "reddit"],
        "max_keywords": 160,
        "min_score": 0.6
    },
    "lazer": {
        "termos_iniciais": [
            "filmes 2024",
            "jogos online",
            "viagens baratas",
            "hobbies criativos",
            "música"
        ],
        "categoria": "lazer",
        "coletores_prioritarios": ["google_suggest", "youtube", "reddit", "twitter"],
        "max_keywords": 140,
        "min_score": 0.5
    }
}

async def verificar_necessidade_execucao() -> bool:
    """
    Verifica se é necessário executar o fluxo semanal.
    
    Returns:
        True se deve executar, False caso contrário
    """
    try:
        # Verifica se já foi executado esta semana
        semana_atual = historico_inteligente._get_semana_atual()
        
        # Busca última execução no histórico
        conn = sqlite3.connect(historico_inteligente.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(data_criacao) FROM historico_clusters 
            WHERE semana_ano = ?
        """, (semana_atual,))
        
        ultima_execucao = cursor.fetchone()[0]
        conn.close()
        
        if ultima_execucao:
            # Já foi executado esta semana
            logger.info({
                "event": "fluxo_semanal_ja_executado",
                "status": "info",
                "source": "verificar_necessidade_execucao",
                "details": {
                    "semana_atual": semana_atual,
                    "ultima_execucao": ultima_execucao
                }
            })
            return False
        
        # Verifica se é dia de execução (segunda-feira)
        hoje = datetime.now()
        if hoje.weekday() != 0:  # 0 = segunda-feira
            logger.info({
                "event": "nao_e_dia_execucao",
                "status": "info",
                "source": "verificar_necessidade_execucao",
                "details": {"dia_semana": hoje.strftime("%A")}
            })
            return False
        
        return True
        
    except Exception as e:
        logger.error({
            "event": "erro_verificacao_execucao",
            "status": "error",
            "source": "verificar_necessidade_execucao",
            "details": {"error": str(e)}
        })
        return True  # Em caso de erro, executa por segurança

async def executar_fluxo_semanal():
    """Executa o fluxo semanal variado."""
    try:
        logger.info("=== INICIANDO FLUXO SEMANAL VARIADO ===")
        
        # Verifica se deve executar
        if not await verificar_necessidade_execucao():
            logger.info("Fluxo semanal não necessário. Saindo.")
            return
        
        # Obtém variação atual
        variacao_atual = historico_inteligente._get_variacao_atual()
        semana_atual = historico_inteligente._get_semana_atual()
        
        logger.info({
            "event": "iniciando_fluxo_semanal",
            "status": "info",
            "source": "executar_fluxo_semanal",
            "details": {
                "variacao_atual": variacao_atual.nome,
                "semana_atual": semana_atual,
                "nichos_configurados": len(NICHOS_CONFIG)
            }
        })
        
        # Executa fluxo para todos os nichos
        resultados = await orchestrator_variado.executar_fluxo_semanal(NICHOS_CONFIG)
        
        # Gera relatório de execução
        await gerar_relatorio_execucao(resultados, variacao_atual, semana_atual)
        
        logger.info({
            "event": "fluxo_semanal_concluido",
            "status": "success",
            "source": "executar_fluxo_semanal",
            "details": {
                "nichos_processados": len(resultados),
                "total_keywords": sum(len(r.keywords_coletadas) for r in resultados.values()),
                "total_artigos": sum(len(r.artigos_gerados) for r in resultados.values())
            }
        })
        
    except Exception as e:
        logger.error({
            "event": "erro_fluxo_semanal",
            "status": "error",
            "source": "executar_fluxo_semanal",
            "details": {"error": str(e)}
        })
        raise

async def gerar_relatorio_execucao(
    resultados: Dict[str, Any],
    variacao_atual,
    semana_atual: str
):
    """Gera relatório detalhado da execução semanal."""
    try:
        # Estatísticas gerais
        total_keywords = sum(len(r.keywords_coletadas) for r in resultados.values())
        total_keywords_novas = sum(len(r.keywords_novas) for r in resultados.values())
        total_clusters = sum(len(r.clusters_gerados) for r in resultados.values())
        total_clusters_novos = sum(len(r.clusters_novos) for r in resultados.values())
        total_artigos = sum(len(r.artigos_gerados) for r in resultados.values())
        tempo_total = sum(r.tempo_execucao_total for r in resultados.values())
        
        relatorio = {
            "execucao": {
                "data": datetime.now().isoformat(),
                "semana": semana_atual,
                "variacao_algoritmica": variacao_atual.nome,
                "descricao_variacao": variacao_atual.descricao,
                "parametros_variacao": variacao_atual.parametros
            },
            "resumo_executivo": {
                "nichos_processados": len(resultados),
                "total_keywords_coletadas": total_keywords,
                "total_keywords_novas": total_keywords_novas,
                "total_clusters_gerados": total_clusters,
                "total_clusters_novos": total_clusters_novos,
                "total_artigos_gerados": total_artigos,
                "tempo_execucao_total": tempo_total,
                "novidade_keywords": total_keywords_novas / total_keywords if total_keywords > 0 else 0,
                "novidade_clusters": total_clusters_novos / total_clusters if total_clusters > 0 else 0
            },
            "performance_por_nicho": {
                nicho: {
                    "keywords_coletadas": len(r.keywords_coletadas),
                    "keywords_novas": len(r.keywords_novas),
                    "clusters_gerados": len(r.clusters_gerados),
                    "clusters_novos": len(r.clusters_novos),
                    "artigos_gerados": len(r.artigos_gerados),
                    "tempo_execucao": r.tempo_execucao_total,
                    "novidade_keywords": len(r.keywords_novas) / len(r.keywords_coletadas) if r.keywords_coletadas else 0,
                    "novidade_clusters": len(r.clusters_novos) / len(r.clusters_gerados) if r.clusters_gerados else 0
                }
                for nicho, r in resultados.items()
            },
            "estatisticas_historico": {
                nicho: r.estatisticas_historico
                for nicho, r in resultados.items()
                if r.estatisticas_historico
            },
            "proxima_execucao": {
                "data_estimada": (datetime.now() + timedelta(days=7)).isoformat(),
                "proxima_variacao": orchestrator_variado._calcular_proxima_variacao(variacao_atual)
            }
        }
        
        # Salva relatório
        from shared.utils import salvar_json
        nome_arquivo = f"relatorios/execucao_semanal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        await salvar_json(relatorio, nome_arquivo)
        
        logger.info({
            "event": "relatorio_execucao_gerado",
            "status": "success",
            "source": "gerar_relatorio_execucao",
            "details": {"arquivo": nome_arquivo}
        })
        
    except Exception as e:
        logger.error({
            "event": "erro_geracao_relatorio_execucao",
            "status": "error",
            "source": "gerar_relatorio_execucao",
            "details": {"error": str(e)}
        })

async def executar_fluxo_manual(nicho: str, termos: List[str]):
    """
    Executa fluxo manual para um nicho específico.
    
    Args:
        nicho: Nome do nicho
        termos: Lista de termos iniciais
    """
    try:
        logger.info(f"Executando fluxo manual para nicho: {nicho}")
        
        config_nicho = NICHOS_CONFIG.get(nicho, {
            "termos_iniciais": termos,
            "categoria": "geral",
            "max_keywords": 100,
            "min_score": 0.5
        })
        
        resultado = await orchestrator_variado.executar_fluxo_completo(
            termos_iniciais=termos,
            nicho=nicho,
            categoria=config_nicho.get("categoria", "geral"),
            config_nicho=config_nicho
        )
        
        logger.info({
            "event": "fluxo_manual_concluido",
            "status": "success",
            "source": "executar_fluxo_manual",
            "details": {
                "nicho": nicho,
                "keywords_coletadas": len(resultado.keywords_coletadas),
                "artigos_gerados": len(resultado.artigos_gerados)
            }
        })
        
        return resultado
        
    except Exception as e:
        logger.error({
            "event": "erro_fluxo_manual",
            "status": "error",
            "source": "executar_fluxo_manual",
            "details": {"error": str(e), "nicho": nicho}
        })
        raise

async def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Executa fluxo semanal variado do Omni Keywords Finder')
    parser.add_argument('--modo', choices=['semanal', 'manual'], default='semanal',
                       help='Modo de execução: semanal (automático) ou manual')
    parser.add_argument('--nicho', type=str, help='Nicho para execução manual')
    parser.add_argument('--termos', nargs='+', help='Termos iniciais para execução manual')
    
    args = parser.parse_args()
    
    try:
        if args.modo == 'semanal':
            await executar_fluxo_semanal()
        elif args.modo == 'manual':
            if not args.nicho or not args.termos:
                print("Para modo manual, especifique --nicho e --termos")
                return
            await executar_fluxo_manual(args.nicho, args.termos)
        
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 