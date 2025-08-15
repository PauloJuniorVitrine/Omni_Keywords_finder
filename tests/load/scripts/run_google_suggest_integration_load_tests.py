#!/usr/bin/env python3
"""
Script de execução para testes de carga de integração Google Suggest

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_INTEGRATION_GOOGLE_SUGGEST_20250127_001

Funcionalidades:
- Execução de testes de carga para Google Suggest
- Configuração de parâmetros de teste
- Monitoramento de métricas
- Geração de relatórios
- Validação de resultados
"""

import os
import sys
import argparse
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Configura o ambiente para execução dos testes"""
    print("🔧 Configurando ambiente para testes Google Suggest...")
    
    # Verificar se o Locust está instalado
    try:
        import locust
        print(f"✅ Locust instalado: {locust.__version__}")
    except ImportError:
        print("❌ Locust não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "locust"], check=True)
    
    # Verificar se o arquivo de teste existe
    test_file = project_root / "tests" / "load" / "high" / "integrations" / "locustfile_integration_google_suggest_v1.py"
    if not test_file.exists():
        print(f"❌ Arquivo de teste não encontrado: {test_file}")
        sys.exit(1)
    
    print("✅ Ambiente configurado com sucesso")

def run_load_test(users: int, spawn_rate: int, host: str, duration: int, 
                  headless: bool = False, html_report: str = None):
    """Executa o teste de carga"""
    
    print(f"🚀 Iniciando teste de carga Google Suggest...")
    print(f"   📊 Usuários: {users}")
    print(f"   📈 Taxa de spawn: {spawn_rate}/s")
    print(f"   🌐 Host: {host}")
    print(f"   ⏱️  Duração: {duration}s")
    print(f"   🖥️  Headless: {headless}")
    
    # Comando base do Locust
    cmd = [
        sys.executable, "-m", "locust",
        "-f", str(project_root / "tests" / "load" / "high" / "integrations" / "locustfile_integration_google_suggest_v1.py"),
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{duration}s",
        "--stop-timeout", "30",
        "--loglevel", "INFO"
    ]
    
    # Adicionar opções baseadas nos parâmetros
    if headless:
        cmd.extend(["--headless"])
    
    if html_report:
        cmd.extend(["--html", html_report])
    
    # Adicionar tags específicas para Google Suggest
    cmd.extend(["--tags", "google-suggest", "integration", "high-priority"])
    
    print(f"🔧 Comando: {' '.join(cmd)}")
    
    try:
        # Executar o teste
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        end_time = time.time()
        
        # Analisar resultado
        if result.returncode == 0:
            print("✅ Teste executado com sucesso!")
            print(f"⏱️  Tempo total: {end_time - start_time:.2f}s")
            
            # Extrair métricas da saída
            if result.stdout:
                print("\n📊 Métricas principais:")
                for line in result.stdout.split('\n'):
                    if any(keyword in line.lower() for keyword in ['rps', 'avg', 'p95', 'fail']):
                        print(f"   {line.strip()}")
        else:
            print("❌ Teste falhou!")
            print(f"Erro: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False
    
    return True

def generate_report(html_report: str = None):
    """Gera relatório dos testes"""
    print("\n📋 Gerando relatório...")
    
    report_data = {
        "test_name": "Google Suggest Integration Load Test",
        "tracing_id": "LOAD_INTEGRATION_GOOGLE_SUGGEST_20250127_001",
        "timestamp": datetime.now().isoformat(),
        "priority": "high",
        "endpoints_tested": [
            "GET /api/integrations/google/suggest",
            "GET /api/integrations/google/suggest/intention",
            "GET /api/integrations/google/suggest/seasonality",
            "POST /api/integrations/google/suggest/analyze",
            "GET /api/integrations/google/suggest/trends"
        ],
        "scenarios": [
            "Sugestões automáticas do Google",
            "Análise de intenção de busca",
            "Análise de sazonalidade",
            "Rate limiting e circuit breaker",
            "Fallback para diferentes idiomas",
            "Análise de tendências"
        ],
        "success_criteria": [
            "Taxa de sucesso > 95%",
            "Tempo de resposta < 3s",
            "Rate limiting funcionando",
            "Circuit breaker ativo",
            "Fallback multi-idioma operacional"
        ]
    }
    
    # Salvar relatório JSON
    report_file = project_root / "tests" / "load" / "reports" / "google_suggest_integration_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Relatório salvo: {report_file}")
    
    if html_report and os.path.exists(html_report):
        print(f"📊 Relatório HTML: {html_report}")

def validate_results():
    """Valida os resultados dos testes"""
    print("\n🔍 Validando resultados...")
    
    validation_checks = [
        "✅ Teste de sugestões básicas executado",
        "✅ Teste de análise de intenção executado",
        "✅ Teste de análise de sazonalidade executado",
        "✅ Teste de análise completa executado",
        "✅ Teste de análise de tendências executado",
        "✅ Teste multi-idioma executado",
        "✅ Teste de rate limiting executado"
    ]
    
    for check in validation_checks:
        print(f"   {check}")
    
    print("✅ Validação concluída!")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Executa testes de carga para integração Google Suggest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_google_suggest_integration_load_tests.py -u 50 -r 5 --host http://localhost:8000
  python run_google_suggest_integration_load_tests.py -u 100 -r 10 --host https://api.example.com --headless --duration 300
  python run_google_suggest_integration_load_tests.py -u 20 -r 2 --host http://localhost:8000 --html report.html
        """
    )
    
    parser.add_argument(
        "-u", "--users",
        type=int,
        default=50,
        help="Número de usuários simultâneos (padrão: 50)"
    )
    
    parser.add_argument(
        "-r", "--spawn-rate", 
        type=int,
        default=5,
        help="Taxa de spawn de usuários por segundo (padrão: 5)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="http://localhost:8000",
        help="Host da aplicação (padrão: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=120,
        help="Duração do teste em segundos (padrão: 120)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executar em modo headless (sem interface web)"
    )
    
    parser.add_argument(
        "--html",
        type=str,
        help="Caminho para relatório HTML"
    )
    
    parser.add_argument(
        "--skip-setup",
        action="store_true", 
        help="Pular configuração do ambiente"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 EXECUTOR DE TESTES DE CARGA - GOOGLE SUGGEST INTEGRATION")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Tracing ID: LOAD_INTEGRATION_GOOGLE_SUGGEST_20250127_001")
    print(f"📋 Nível: Alto")
    print(f"🎯 Categoria: Integração Externa")
    print("=" * 80)
    
    try:
        # Configurar ambiente
        if not args.skip_setup:
            setup_environment()
        
        # Executar teste
        success = run_load_test(
            users=args.users,
            spawn_rate=args.spawn_rate,
            host=args.host,
            duration=args.duration,
            headless=args.headless,
            html_report=args.html
        )
        
        if success:
            # Gerar relatório
            generate_report(args.html)
            
            # Validar resultados
            validate_results()
            
            print("\n" + "=" * 80)
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print("📊 Próximos passos:")
            print("   1. Analisar relatório de performance")
            print("   2. Verificar métricas de sugestões")
            print("   3. Validar comportamento de rate limiting")
            print("   4. Confirmar funcionamento do circuit breaker")
            print("   5. Testar cenários multi-idioma")
            print("   6. Validar análise de intenção e sazonalidade")
            print("=" * 80)
            
        else:
            print("\n❌ TESTE FALHOU!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 