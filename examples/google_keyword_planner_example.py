"""
Exemplo de Uso: Google Keyword Planner Validator
Demonstra como usar o validador avançado com Google Keyword Planner

Prompt: Google Keyword Planner como Validador
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
"""

import os
import yaml
from typing import List
from datetime import datetime

from domain.models import Keyword
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from infrastructure.validacao import ValidadorAvancado
from shared.logger import logger

def carregar_configuracao() -> dict:
    """
    Carrega configuração do arquivo YAML.
    
    Returns:
        Configuração carregada
    """
    config_path = "config/google_keyword_planner.yaml"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    # Substituir variáveis de ambiente
    config = substituir_variaveis_ambiente(config)
    
    return config

def substituir_variaveis_ambiente(config: dict) -> dict:
    """
    Substitui variáveis de ambiente na configuração.
    
    Args:
        config: Configuração original
        
    Returns:
        Configuração com variáveis substituídas
    """
    config_str = str(config)
    
    # Substituir variáveis de ambiente
    for key, value in os.environ.items():
        config_str = config_str.replace(f"${{{key}}}", value)
    
    # Converter de volta para dict
    return eval(config_str)

def criar_keywords_exemplo() -> List[Keyword]:
    """
    Cria lista de keywords de exemplo para teste.
    
    Returns:
        Lista de keywords
    """
    from domain.models import IntencaoBusca
    
    keywords = [
        Keyword(
            termo="marketing digital",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.COMERCIAL,
            fonte="exemplo"
        ),
        Keyword(
            termo="curso de python",
            volume_busca=5000,
            cpc=1.8,
            concorrencia=0.6,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="exemplo"
        ),
        Keyword(
            termo="receita bolo chocolate",
            volume_busca=800,
            cpc=0.5,
            concorrencia=0.3,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="exemplo"
        ),
        Keyword(
            termo="exercicios em casa",
            volume_busca=3000,
            cpc=1.2,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="exemplo"
        ),
        Keyword(
            termo="dicas viagem",
            volume_busca=2000,
            cpc=1.5,
            concorrencia=0.6,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="exemplo"
        )
    ]
    
    return keywords

def exemplo_validacao_cascata():
    """
    Exemplo de validação em cascata.
    """
    print("🔄 **EXEMPLO: Validação em Cascata**")
    print("=" * 50)
    
    # Carregar configuração
    config = carregar_configuracao()
    
    # Criar processador
    processador = ProcessadorKeywords(config=config)
    
    # Criar keywords de exemplo
    keywords = criar_keywords_exemplo()
    
    print(f"📊 Keywords iniciais: {len(keywords)}")
    for kw in keywords:
        print(f"  - {kw.termo}")
    
    # Processar com validação em cascata
    keywords_aprovadas = processador.processar_keywords(
        keywords, 
        estrategia_validacao="cascata"
    )
    
    print(f"\n✅ Keywords aprovadas: {len(keywords_aprovadas)}")
    for kw in keywords_aprovadas:
        score = getattr(kw, 'score_qualidade', 'N/A')
        print(f"  - {kw.termo} (Score: {score})")
    
    # Mostrar métricas
    metricas = processador.get_metricas_completas()
    print(f"\n📈 Métricas de Processamento:")
    print(f"  - Total execuções: {metricas['processador']['total_execucoes']}")
    print(f"  - Taxa aprovação: {metricas['processador']['total_keywords_aprovadas'] / metricas['processador']['total_keywords_processadas']:.2%}")

def exemplo_validacao_paralela():
    """
    Exemplo de validação paralela.
    """
    print("\n🔄 **EXEMPLO: Validação Paralela**")
    print("=" * 50)
    
    # Carregar configuração
    config = carregar_configuracao()
    
    # Criar validador avançado diretamente
    validador = ValidadorAvancado(config.get("validacao", {}))
    
    # Criar keywords de exemplo
    keywords = criar_keywords_exemplo()
    
    print(f"📊 Keywords iniciais: {len(keywords)}")
    
    # Validar em paralelo
    keywords_aprovadas = validador.validar_keywords(
        keywords, 
        estrategia="paralela"
    )
    
    print(f"\n✅ Keywords aprovadas: {len(keywords_aprovadas)}")
    for kw in keywords_aprovadas:
        print(f"  - {kw.termo}")
    
    # Mostrar estatísticas
    estatisticas = validador.get_estatisticas()
    print(f"\n📈 Estatísticas do Validador:")
    print(f"  - Total execuções: {estatisticas['validador_avancado']['total_executions']}")
    print(f"  - Taxa aprovação: {estatisticas['validador_avancado']['overall_approval_rate']:.2%}")

def exemplo_validacao_consenso():
    """
    Exemplo de validação por consenso.
    """
    print("\n🔄 **EXEMPLO: Validação por Consenso**")
    print("=" * 50)
    
    # Carregar configuração
    config = carregar_configuracao()
    
    # Criar validador avançado
    validador = ValidadorAvancado(config.get("validacao", {}))
    
    # Criar keywords de exemplo
    keywords = criar_keywords_exemplo()
    
    print(f"📊 Keywords iniciais: {len(keywords)}")
    
    # Validar por consenso
    keywords_aprovadas = validador.validar_keywords(
        keywords, 
        estrategia="consenso"
    )
    
    print(f"\n✅ Keywords aprovadas por consenso: {len(keywords_aprovadas)}")
    for kw in keywords_aprovadas:
        print(f"  - {kw.termo}")

def exemplo_metricas_google():
    """
    Exemplo de obtenção de métricas específicas do Google.
    """
    print("\n🔄 **EXEMPLO: Métricas do Google Keyword Planner**")
    print("=" * 50)
    
    # Carregar configuração
    config = carregar_configuracao()
    
    # Criar validador Google Keyword Planner
    from infrastructure.validacao.google_keyword_planner_validator import GoogleKeywordPlannerValidator
    
    google_config = config.get("validacao", {}).get("google_keyword_planner", {})
    validador = GoogleKeywordPlannerValidator(google_config)
    
    # Keywords para obter métricas
    keywords_teste = ["marketing digital", "curso python", "receita bolo"]
    
    for keyword in keywords_teste:
        print(f"\n🔍 Obtendo métricas para: '{keyword}'")
        
        try:
            metricas = validador.obter_metricas(keyword)
            
            if metricas:
                print(f"  📊 Volume de busca: {metricas.get('search_volume', 'N/A')}")
                print(f"  🏆 Competição: {metricas.get('competition', 'N/A')}")
                print(f"  💰 CPC: ${metricas.get('cpc', 'N/A')}")
                print(f"  📈 Índice competição: {metricas.get('competition_index', 'N/A')}")
                print(f"  🕒 Última atualização: {metricas.get('last_updated', 'N/A')}")
                print(f"  🔗 Fonte: {metricas.get('source', 'N/A')}")
            else:
                print(f"  ❌ Métricas não disponíveis")
                
        except Exception as e:
            print(f"  ❌ Erro ao obter métricas: {str(e)}")

def main():
    """
    Função principal que executa todos os exemplos.
    """
    print("🚀 **GOOGLE KEYWORD PLANNER VALIDATOR - EXEMPLOS**")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.utcnow().strftime('%Y-%m-%data %H:%M:%S')} UTC")
    print("=" * 60)
    
    try:
        # Exemplo 1: Validação em Cascata
        exemplo_validacao_cascata()
        
        # Exemplo 2: Validação Paralela
        exemplo_validacao_paralela()
        
        # Exemplo 3: Validação por Consenso
        exemplo_validacao_consenso()
        
        # Exemplo 4: Métricas do Google
        exemplo_metricas_google()
        
        print("\n✅ **Todos os exemplos executados com sucesso!**")
        
    except Exception as e:
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "erro_execucao_exemplos",
            "status": "error",
            "source": "google_keyword_planner_example.main",
            "details": {"erro": str(e)}
        })
        print(f"\n❌ **Erro durante execução: {str(e)}**")

if __name__ == "__main__":
    main() 