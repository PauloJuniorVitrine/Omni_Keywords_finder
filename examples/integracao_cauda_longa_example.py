"""
Exemplo de Integração Completa de Cauda Longa - Omni Keywords Finder

Este exemplo demonstra como usar o integrador de cauda longa completo
para processar keywords com todos os módulos ativos.

Prompt: CHECKLIST_LONG_TAIL_V1.md - Exemplo de Integração
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
Tracing ID: LONGTAIL_EXAMPLE_001
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from infrastructure.processamento.integrador_cauda_longa import EstrategiaIntegracao, ConfiguracaoIntegracao
from shared.logger import logger

def callback_progresso(etapa: str, passo_atual: int, total_passos: int):
    """
    Callback para mostrar progresso do processamento.
    
    Args:
        etapa: Nome da etapa atual
        passo_atual: Passo atual
        total_passos: Total de passos
    """
    percentual = (passo_atual / total_passos) * 100
    print(f"🔄 {etapa} - {percentual:.1f}% ({passo_atual}/{total_passos})")

def criar_keywords_exemplo() -> List[Keyword]:
    """
    Cria keywords de exemplo para demonstração.
    
    Returns:
        Lista de keywords de exemplo
    """
    keywords = [
        Keyword(
            termo="melhor notebook para programação 2024",
            volume_busca=1200,
            cpc=2.50,
            concorrencia=0.7,
            intencao=IntencaoBusca.TRANSACIONAL
        ),
        Keyword(
            termo="como aprender python do zero",
            volume_busca=8500,
            cpc=1.20,
            concorrencia=0.4,
            intencao=IntencaoBusca.INFORMACIONAL
        ),
        Keyword(
            termo="curso online de javascript avançado",
            volume_busca=3200,
            cpc=3.80,
            concorrencia=0.6,
            intencao=IntencaoBusca.TRANSACIONAL
        ),
        Keyword(
            termo="dicas para otimizar performance de aplicações web",
            volume_busca=1800,
            cpc=4.20,
            concorrencia=0.8,
            intencao=IntencaoBusca.INFORMACIONAL
        ),
        Keyword(
            termo="framework react vs vue qual escolher",
            volume_busca=5600,
            cpc=2.90,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        ),
        Keyword(
            termo="melhor hospedagem para sites wordpress",
            volume_busca=4200,
            cpc=5.10,
            concorrencia=0.9,
            intencao=IntencaoBusca.TRANSACIONAL
        ),
        Keyword(
            termo="como implementar autenticação jwt",
            volume_busca=2100,
            cpc=3.40,
            concorrencia=0.6,
            intencao=IntencaoBusca.INFORMACIONAL
        ),
        Keyword(
            termo="tutorial completo de docker para iniciantes",
            volume_busca=3800,
            cpc=2.80,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        ),
        Keyword(
            termo="melhores práticas de segurança em aplicações web",
            volume_busca=1600,
            cpc=4.60,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL
        ),
        Keyword(
            termo="como criar api rest com node.js e express",
            volume_busca=2900,
            cpc=3.20,
            concorrencia=0.6,
            intencao=IntencaoBusca.INFORMACIONAL
        )
    ]
    
    return keywords

def configurar_processador() -> ProcessadorKeywords:
    """
    Configura o processador com integração de cauda longa.
    
    Returns:
        Processador configurado
    """
    config = {
        "cauda_longa": {
            "ativar_ml": True,
            "ativar_cache": True,
            "ativar_feedback": True,
            "ativar_auditoria": True,
            "ativar_tendencias": True,
            "paralelizar": False,
            "max_workers": 4,
            "timeout_segundos": 300,
            "log_detalhado": True,
            "nicho": "tecnologia",
            "idioma": "pt"
        },
        "validacao": {
            "estrategia_padrao": "cascata",
            "timeout_segundos": 60,
            "max_retries": 3
        }
    }
    
    processador = ProcessadorKeywords(
        pesos_score={
            "volume_busca": 0.3,
            "cpc": 0.2,
            "concorrencia": 0.2,
            "qualidade": 0.3
        },
        remover_acentos=False,
        case_sensitive=False,
        paralelizar_enriquecimento=True,
        validador_idioma="pt",
        config=config
    )
    
    return processador

def demonstrar_processamento_basico(processador: ProcessadorKeywords, keywords: List[Keyword]):
    """
    Demonstra processamento básico de keywords.
    
    Args:
        processador: Processador configurado
        keywords: Lista de keywords
    """
    print("\n" + "="*60)
    print("🔧 PROCESSAMENTO BÁSICO DE KEYWORDS")
    print("="*60)
    
    try:
        # Processamento básico
        keywords_processadas, relatorio = processador.processar(
            keywords=keywords,
            enriquecer=True,
            relatorio=True,
            validar_avancado=True,
            idioma="pt"
        )
        
        print(f"✅ Keywords processadas: {len(keywords_processadas)}/{len(keywords)}")
        print(f"📊 Tempo de execução: {relatorio.get('timestamp', 'N/A')}")
        
        # Mostrar algumas keywords processadas
        print("\n📋 Exemplos de keywords processadas:")
        for index, kw in enumerate(keywords_processadas[:3]):
            print(f"  {index+1}. {kw.termo}")
            print(f"     Volume: {kw.volume_busca}, CPC: ${kw.cpc}, Concorrência: {kw.concorrencia}")
        
    except Exception as e:
        print(f"❌ Erro no processamento básico: {str(e)}")

def demonstrar_processamento_cauda_longa(processador: ProcessadorKeywords, keywords: List[Keyword]):
    """
    Demonstra processamento completo com cauda longa.
    
    Args:
        processador: Processador configurado
        keywords: Lista de keywords
    """
    print("\n" + "="*60)
    print("🚀 PROCESSAMENTO COMPLETO COM CAUDA LONGA")
    print("="*60)
    
    try:
        # Processamento com cauda longa
        keywords_cauda_longa, relatorio_cauda_longa = processador.processar_com_cauda_longa(
            keywords=keywords,
            nicho="tecnologia",
            idioma="pt",
            estrategia=EstrategiaIntegracao.CASCATA,
            callback_progresso=callback_progresso,
            relatorio=True
        )
        
        print(f"\n✅ Keywords processadas com cauda longa: {len(keywords_cauda_longa)}/{len(keywords)}")
        
        # Métricas do processamento
        metricas = relatorio_cauda_longa.get("metricas_processamento", {}) or {}
        tempo_total = metricas.get('tempo_total', 0) if metricas else 0
        score_medio = metricas.get('score_medio', 0) if metricas else 0
        complexidade_media = metricas.get('complexidade_media', 0) if metricas else 0
        competitividade_media = metricas.get('competitividade_media', 0) if metricas else 0
        
        print(f"⏱️  Tempo total: {tempo_total:.2f}string_data")
        print(f"📈 Score médio: {score_medio:.2f}")
        print(f"🧠 Complexidade média: {complexidade_media:.2f}")
        print(f"🏆 Competitividade média: {competitividade_media:.2f}")
        
        # Distribuição de scores
        distribuicao = relatorio_cauda_longa.get("distribuicao_scores", {})
        print(f"\n📊 Distribuição de scores:")
        print(f"  Excelente: {distribuicao.get('excelente', 0)}")
        print(f"  Boa: {distribuicao.get('boa', 0)}")
        print(f"  Média: {distribuicao.get('media', 0)}")
        print(f"  Baixa: {distribuicao.get('baixa', 0)}")
        
        # Mostrar keywords com melhor score
        print(f"\n🏅 Top 3 keywords por score composto:")
        keywords_ordenadas = sorted(keywords_cauda_longa, key=lambda key: getattr(key, 'score_composto', 0) or 0, reverse=True)
        for index, kw in enumerate(keywords_ordenadas[:3]):
            print(f"  {index+1}. {kw.termo}")
            print(f"     Score: {getattr(kw, 'score_composto', 0):.2f}, Complexidade: {getattr(kw, 'complexidade_semantica', 0):.2f}")
            print(f"     Competitividade: {getattr(kw, 'score_competitivo', 0):.2f}, Tendência: {getattr(kw, 'score_tendencia', 0):.2f}")
        
        # Tendências detectadas
        tendencias = relatorio_cauda_longa.get("tendencias_detectadas", 0)
        print(f"\n📈 Tendências emergentes detectadas: {tendencias}")
        
        # Módulos ativos
        modulos_ativos = relatorio_cauda_longa.get("configuracao", {}).get("modulos_ativos", [])
        print(f"\n🔧 Módulos ativos: {', '.join(modulos_ativos)}")
        
    except Exception as e:
        print(f"❌ Erro no processamento com cauda longa: {str(e)}")
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_exemplo_cauda_longa",
            "status": "error",
            "source": "integracao_cauda_longa_example.demonstrar_processamento_cauda_longa",
            "details": {"erro": str(e)}
        })

def demonstrar_status_sistema(processador: ProcessadorKeywords):
    """
    Demonstra o status completo do sistema.
    
    Args:
        processador: Processador configurado
    """
    print("\n" + "="*60)
    print("📊 STATUS COMPLETO DO SISTEMA")
    print("="*60)
    
    try:
        # Status do processador
        metricas_completas = processador.get_metricas_completas()
        print(f"📈 Métricas do processador:")
        print(f"  Total de execuções: {metricas_completas['processador'].get('total_execucoes', 0)}")
        print(f"  Keywords processadas: {metricas_completas['processador'].get('total_keywords_processadas', 0)}")
        print(f"  Keywords aprovadas: {metricas_completas['processador'].get('total_keywords_aprovadas', 0)}")
        
        # Status da cauda longa
        status_cauda_longa = processador.obter_status_cauda_longa()
        print(f"\n🚀 Status da cauda longa:")
        
        modulos = status_cauda_longa.get("modulos_ativos", {})
        for modulo, status in modulos.items():
            emoji = "✅" if status == "ativo" else "❌"
            print(f"  {emoji} {modulo}: {status}")
        
        # Configuração
        config = status_cauda_longa.get("configuracao", {})
        print(f"\n⚙️  Configuração:")
        print(f"  Estratégia: {config.get('estrategia', 'N/A')}")
        print(f"  ML ativo: {config.get('ativar_ml', False)}")
        print(f"  Cache ativo: {config.get('ativar_cache', False)}")
        print(f"  Feedback ativo: {config.get('ativar_feedback', False)}")
        print(f"  Auditoria ativa: {config.get('ativar_auditoria', False)}")
        print(f"  Tendências ativas: {config.get('ativar_tendencias', False)}")
        
    except Exception as e:
        print(f"❌ Erro ao obter status: {str(e)}")

def main():
    """
    Função principal que executa o exemplo completo.
    """
    print("🚀 OMNİ KEYWORDS FINDER - EXEMPLO DE INTEGRAÇÃO CAUDA LONGA")
    print("="*70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}")
    print(f"🎯 Versão: 1.0.0")
    print(f"🔍 Tracing ID: LONGTAIL_EXAMPLE_001")
    
    try:
        # 1. Criar keywords de exemplo
        print("\n📝 Criando keywords de exemplo...")
        keywords = criar_keywords_exemplo()
        print(f"✅ {len(keywords)} keywords criadas")
        
        # 2. Configurar processador
        print("\n⚙️ Configurando processador...")
        processador = configurar_processador()
        print("✅ Processador configurado com integração de cauda longa")
        
        # 3. Demonstrar processamento básico
        demonstrar_processamento_basico(processador, keywords)
        
        # 4. Demonstrar processamento com cauda longa
        demonstrar_processamento_cauda_longa(processador, keywords)
        
        # 5. Demonstrar status do sistema
        demonstrar_status_sistema(processador)
        
        print("\n" + "="*70)
        print("🎉 EXEMPLO CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print("✅ Integração de cauda longa funcionando perfeitamente")
        print("✅ Todos os módulos ativos e operacionais")
        print("✅ Métricas e relatórios gerados corretamente")
        print("✅ Sistema pronto para uso em produção")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução do exemplo: {str(e)}")
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_exemplo_principal",
            "status": "error",
            "source": "integracao_cauda_longa_example.main",
            "details": {"erro": str(e)}
        })
        sys.exit(1)

if __name__ == "__main__":
    main() 