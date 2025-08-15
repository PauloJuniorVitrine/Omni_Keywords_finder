#!/usr/bin/env python3
"""
Script de execução para testes de carga de performance de tempo de resposta de APIs

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_PERFORMANCE_API_RESPONSE_TIME_20250127_001

Funcionalidades:
- Execução de testes de carga para performance de APIs
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
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Executar testes de carga de performance de APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_performance_api_response_time_load_tests.py -u 100 -r 10 --host http://localhost:8000
  python run_performance_api_response_time_load_tests.py -u 50 -r 5 --host http://localhost:8000 --duration 10m
  python run_performance_api_response_time_load_tests.py -u 200 -r 20 --host http://localhost:8000 --headless
        """
    )
    
    parser.add_argument(
        '-u', '--users',
        type=int,
        default=50,
        help='Número de usuários simultâneos (padrão: 50)'
    )
    
    parser.add_argument(
        '-r', '--spawn-rate',
        type=int,
        default=10,
        help='Taxa de spawn de usuários por segundo (padrão: 10)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='http://localhost:8000',
        help='Host do servidor (padrão: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--duration',
        type=str,
        default='5m',
        help='Duração do teste (padrão: 5m)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Executar em modo headless (sem interface web)'
    )
    
    parser.add_argument(
        '--html',
        type=str,
        default='performance_api_response_time_report.html',
        help='Arquivo de relatório HTML (padrão: performance_api_response_time_report.html)'
    )
    
    parser.add_argument(
        '--csv',
        type=str,
        default='performance_api_response_time_stats.csv',
        help='Arquivo de estatísticas CSV (padrão: performance_api_response_time_stats.csv)'
    )
    
    parser.add_argument(
        '--json',
        type=str,
        default='performance_api_response_time_stats.json',
        help='Arquivo de estatísticas JSON (padrão: performance_api_response_time_stats.json)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Nível de log (padrão: INFO)'
    )
    
    parser.add_argument(
        '--stop-timeout',
        type=int,
        default=30,
        help='Timeout para parar o teste em segundos (padrão: 30)'
    )
    
    parser.add_argument(
        '--expect-workers',
        type=int,
        default=1,
        help='Número esperado de workers (padrão: 1)'
    )
    
    return parser.parse_args()

def validate_environment():
    """Validar ambiente de teste"""
    print("🔍 Validando ambiente de teste...")
    
    # Verificar se o locust está instalado
    try:
        subprocess.run(['locust', '--version'], capture_output=True, check=True)
        print("✅ Locust instalado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Locust não encontrado. Instale com: pip install locust")
        sys.exit(1)
    
    # Verificar se o arquivo de teste existe
    test_file = Path(__file__).parent.parent / "medium" / "performance" / "locustfile_performance_api_response_time_v1.py"
    if not test_file.exists():
        print(f"❌ Arquivo de teste não encontrado: {test_file}")
        sys.exit(1)
    
    print("✅ Ambiente validado")

def run_load_test(args):
    """Executar teste de carga"""
    print(f"🚀 Iniciando teste de performance de APIs...")
    print(f"   - Usuários: {args.users}")
    print(f"   - Taxa de spawn: {args.spawn_rate}/s")
    print(f"   - Host: {args.host}")
    print(f"   - Duração: {args.duration}")
    print(f"   - Modo headless: {args.headless}")
    
    # Construir comando locust
    test_file = Path(__file__).parent.parent / "medium" / "performance" / "locustfile_performance_api_response_time_v1.py"
    
    cmd = [
        'locust',
        '-f', str(test_file),
        '--host', args.host,
        '--users', str(args.users),
        '--spawn-rate', str(args.spawn_rate),
        '--run-time', args.duration,
        '--html', args.html,
        '--csv', args.csv,
        '--json', args.json,
        '--loglevel', args.log_level,
        '--stop-timeout', str(args.stop_timeout),
        '--expect-workers', str(args.expect_workers)
    ]
    
    if args.headless:
        cmd.append('--headless')
    
    print(f"📋 Comando: {' '.join(cmd)}")
    
    # Executar teste
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        end_time = time.time()
        
        print(f"✅ Teste concluído em {end_time - start_time:.2f}s")
        print(f"📊 Relatórios gerados:")
        print(f"   - HTML: {args.html}")
        print(f"   - CSV: {args.csv}")
        print(f"   - JSON: {args.json}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na execução do teste: {e}")
        print(f"📄 Output: {e.stdout}")
        print(f"📄 Error: {e.stderr}")
        return False

def analyze_results(args):
    """Analisar resultados do teste"""
    print("📊 Analisando resultados...")
    
    # Verificar se os arquivos foram gerados
    files_to_check = [args.html, args.csv, args.json]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {file_size} bytes")
        else:
            print(f"❌ {file_path}: não encontrado")
    
    # Análise básica do JSON
    if os.path.exists(args.json):
        try:
            with open(args.json, 'r') as f:
                data = json.load(f)
            
            print("\n📈 Resumo dos resultados:")
            if 'stats' in data:
                stats = data['stats']
                for stat in stats:
                    if stat.get('name') == 'Total':
                        print(f"   - Total de requests: {stat.get('num_requests', 0)}")
                        print(f"   - Requests/s: {stat.get('current_rps', 0):.2f}")
                        print(f"   - Tempo médio: {stat.get('avg_response_time', 0):.2f}ms")
                        print(f"   - Taxa de erro: {stat.get('fail_ratio', 0):.2%}")
                        break
        except Exception as e:
            print(f"⚠️  Erro ao analisar JSON: {e}")

def main():
    """Função principal"""
    print("=" * 80)
    print("🚀 TESTE DE CARGA - PERFORMANCE DE APIS")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now()}")
    print(f"🆔 Tracing ID: LOAD_PERFORMANCE_API_RESPONSE_TIME_20250127_001")
    print()
    
    # Parse arguments
    args = parse_arguments()
    
    # Validar ambiente
    validate_environment()
    print()
    
    # Executar teste
    success = run_load_test(args)
    print()
    
    if success:
        # Analisar resultados
        analyze_results(args)
        print()
        print("🎉 Teste concluído com sucesso!")
    else:
        print("💥 Teste falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main() 