"""
Exemplo: Fluxo Completo - Coleta → Processamento → Validação Google
Demonstra como os dados dos coletores são validados pelo Google Keyword Planner

Prompt: Google Keyword Planner como Validador
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
"""

import os
import yaml
from typing import List
from datetime import datetime

from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from infrastructure.coleta.google import GoogleColetor
from infrastructure.coleta.reddit import RedditColetor
from infrastructure.coleta.youtube import YouTubeColetor
from shared.logger import logger

def carregar_configuracao() -> dict:
    """Carrega configuração do sistema."""
    config_path = "config/google_keyword_planner.yaml"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    return config

def simular_coleta_multiplas_fontes() -> List[Keyword]:
    """
    Simula coleta de keywords de múltiplas fontes.
    Em produção, isso seria feito pelos coletores reais.
    """
    print("🔄 **FASE 1: COLETA DE KEYWORDS**")
    print("=" * 50)
    
    keywords_coletadas = []
    
    # Simular coleta do Google
    print("📊 Coletando do Google...")
    google_keywords = [
        Keyword(
            termo="marketing digital",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.COMERCIAL,
            fonte="google"
        ),
        Keyword(
            termo="curso de python",
            volume_busca=5000,
            cpc=1.8,
            concorrencia=0.6,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google"
        )
    ]
    keywords_coletadas.extend(google_keywords)
    print(f"  ✅ Google: {len(google_keywords)} keywords coletadas")
    
    # Simular coleta do Reddit
    print("📊 Coletando do Reddit...")
    reddit_keywords = [
        Keyword(
            termo="como aprender python",
            volume_busca=800,
            cpc=1.2,
            concorrencia=0.4,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="reddit"
        ),
        Keyword(
            termo="melhor curso python 2024",
            volume_busca=1200,
            cpc=2.1,
            concorrencia=0.6,
            intencao=IntencaoBusca.COMERCIAL,
            fonte="reddit"
        )
    ]
    keywords_coletadas.extend(reddit_keywords)
    print(f"  ✅ Reddit: {len(reddit_keywords)} keywords coletadas")
    
    # Simular coleta do YouTube
    print("📊 Coletando do YouTube...")
    youtube_keywords = [
        Keyword(
            termo="tutorial python iniciantes",
            volume_busca=3000,
            cpc=1.5,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="youtube"
        ),
        Keyword(
            termo="python para data science",
            volume_busca=2500,
            cpc=2.8,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="youtube"
        )
    ]
    keywords_coletadas.extend(youtube_keywords)
    print(f"  ✅ YouTube: {len(youtube_keywords)} keywords coletadas")
    
    print(f"\n📈 **TOTAL COLETADO: {len(keywords_coletadas)} keywords**")
    print("=" * 50)
    
    return keywords_coletadas

def processar_e_validar_keywords(keywords_coletadas: List[Keyword], config: dict):
    """
    Processa e valida as keywords coletadas usando Google Keyword Planner.
    """
    print("\n🔄 **FASE 2: PROCESSAMENTO E VALIDAÇÃO**")
    print("=" * 50)
    
    # Criar processador com validação Google Keyword Planner
    processador = ProcessadorKeywords(config=config)
    
    print("🔍 Iniciando processamento com validação Google Keyword Planner...")
    print("   - Pré-processamento (normalização, deduplicação)")
    print("   - Validação via Google Keyword Planner")
    print("   - Cálculo de score de qualidade")
    print("   - Pós-processamento (metadados, métricas)")
    
    # Processar com validação em cascata
    keywords_aprovadas = processador.processar_keywords(
        keywords_coletadas, 
        estrategia_validacao="cascata"
    )
    
    print(f"\n✅ **VALIDAÇÃO CONCLUÍDA**")
    print(f"   - Keywords iniciais: {len(keywords_coletadas)}")
    print(f"   - Keywords aprovadas: {len(keywords_aprovadas)}")
    print(f"   - Taxa de aprovação: {len(keywords_aprovadas) / len(keywords_coletadas):.1%}")
    
    return keywords_aprovadas, processador

def analisar_resultados_por_fonte(keywords_aprovadas: List[Keyword]):
    """
    Analisa os resultados por fonte de coleta.
    """
    print("\n📊 **ANÁLISE POR FONTE**")
    print("=" * 50)
    
    # Agrupar por fonte
    keywords_por_fonte = {}
    for kw in keywords_aprovadas:
        fonte = kw.fonte
        if fonte not in keywords_por_fonte:
            keywords_por_fonte[fonte] = []
        keywords_por_fonte[fonte].append(kw)
    
    # Mostrar resultados por fonte
    for fonte, keywords in keywords_por_fonte.items():
        print(f"\n🔗 **{fonte.upper()}**")
        print(f"   Keywords aprovadas: {len(keywords)}")
        
        # Mostrar top keywords por score
        keywords_com_score = []
        for kw in keywords:
            score = getattr(kw, 'score_qualidade', 0)
            keywords_com_score.append((kw, score))
        
        # Ordenar por score
        keywords_com_score.sort(key=lambda value: value[1], reverse=True)
        
        print("   Top keywords:")
        for kw, score in keywords_com_score[:3]:
            print(f"     ✅ {kw.termo} (Score: {score:.1f})")

def mostrar_metricas_detalhadas(processador: ProcessadorKeywords):
    """
    Mostra métricas detalhadas do processamento.
    """
    print("\n📈 **MÉTRICAS DETALHADAS**")
    print("=" * 50)
    
    metricas = processador.get_metricas_completas()
    
    # Métricas do processador
    proc_metrics = metricas["processador"]
    print(f"🔄 **Processador**")
    print(f"   - Total execuções: {proc_metrics['total_execucoes']}")
    print(f"   - Keywords processadas: {proc_metrics['total_keywords_processadas']}")
    print(f"   - Keywords aprovadas: {proc_metrics['total_keywords_aprovadas']}")
    print(f"   - Taxa aprovação: {proc_metrics['total_keywords_aprovadas'] / proc_metrics['total_keywords_processadas']:.1%}")
    print(f"   - Tempo total execução: {proc_metrics['tempo_total_execucao']:.2f}string_data")
    print(f"   - Estratégia utilizada: {proc_metrics['estrategia_ultima_execucao']}")
    
    # Métricas do validador avançado
    if "validador_avancado" in metricas:
        val_metrics = metricas["validador_avancado"]
        print(f"\n🔍 **Validador Avançado**")
        print(f"   - Total execuções: {val_metrics['total_executions']}")
        print(f"   - Keywords processadas: {val_metrics['total_keywords_processed']}")
        print(f"   - Keywords aprovadas: {val_metrics['total_keywords_approved']}")
        print(f"   - Taxa aprovação geral: {val_metrics['overall_approval_rate']:.1%}")
        print(f"   - Tempo execução: {val_metrics['total_execution_time']:.2f}string_data")
        
        # Métricas por validador
        if "validadores" in val_metrics:
            print(f"\n🔧 **Validadores Específicos**")
            for val_nome, val_stats in val_metrics["validadores"].items():
                print(f"   📊 {val_nome}:")
                print(f"     - Validadas: {val_stats['total_validated']}")
                print(f"     - Rejeitadas: {val_stats['total_rejected']}")
                print(f"     - Taxa rejeição: {val_stats['taxa_rejeicao']:.1%}")

def simular_fluxo_producao():
    """
    Simula o fluxo completo de produção.
    """
    print("🚀 **FLUXO COMPLETO: COLETA → PROCESSAMENTO → VALIDAÇÃO**")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.utcnow().strftime('%Y-%m-%data %H:%M:%S')} UTC")
    print("=" * 70)
    
    try:
        # 1. Carregar configuração
        config = carregar_configuracao()
        
        # 2. Simular coleta de múltiplas fontes
        keywords_coletadas = simular_coleta_multiplas_fontes()
        
        # 3. Processar e validar com Google Keyword Planner
        keywords_aprovadas, processador = processar_e_validar_keywords(keywords_coletadas, config)
        
        # 4. Analisar resultados por fonte
        analisar_resultados_por_fonte(keywords_aprovadas)
        
        # 5. Mostrar métricas detalhadas
        mostrar_metricas_detalhadas(processador)
        
        print("\n✅ **FLUXO CONCLUÍDO COM SUCESSO!**")
        print("=" * 70)
        print("🎯 **RESUMO:**")
        print(f"   📊 Keywords coletadas: {len(keywords_coletadas)}")
        print(f"   ✅ Keywords validadas: {len(keywords_aprovadas)}")
        print(f"   📈 Taxa aprovação: {len(keywords_aprovadas) / len(keywords_coletadas):.1%}")
        print(f"   🔍 Validador: Google Keyword Planner")
        print(f"   🎯 Estratégia: Cascata")
        
    except Exception as e:
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_fluxo_completo",
            "status": "error",
            "source": "fluxo_completo_exemplo.simular_fluxo_producao",
            "details": {"erro": str(e)}
        })
        print(f"\n❌ **Erro durante execução: {str(e)}**")

if __name__ == "__main__":
    simular_fluxo_producao() 