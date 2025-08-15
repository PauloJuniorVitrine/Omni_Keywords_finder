#!/usr/bin/env python3
"""
Script de execução para testes de carga de cache

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_CACHE_20250127_001

Funcionalidades:
- Execução de testes de carga para cache
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
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Executar testes de carga de cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_cache_load_tests.py -u 50 -r 10 --host http://localhost:8000
  python run_cache_load_tests.py -u 100 -r 20 --duration 300 --cache-stress
  python run_cache_load_tests.py -u 200 -r 50 --host https://api.example.com --html-report
        """
    )
    
    # Parâmetros básicos
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
        type=int,
        default=300,
        help='Duração do teste em segundos (padrão: 300)'
    )
    
    # Parâmetros específicos de cache
    parser.add_argument(
        '--cache-stress',
        action='store_true',
        help='Executar testes de stress no cache'
    )
    
    parser.add_argument(
        '--cache-warming',
        action='store_true',
        help='Incluir testes de cache warming'
    )
    
    parser.add_argument(
        '--cache-invalidation',
        action='store_true',
        help='Incluir testes de invalidação de cache'
    )
    
    parser.add_argument(
        '--cache-metrics',
        action='store_true',
        help='Incluir testes de métricas de cache'
    )
    
    # Parâmetros de relatório
    parser.add_argument(
        '--html-report',
        action='store_true',
        help='Gerar relatório HTML'
    )
    
    parser.add_argument(
        '--json-report',
        action='store_true',
        help='Gerar relatório JSON'
    )
    
    parser.add_argument(
        '--csv-report',
        action='store_true',
        help='Gerar relatório CSV'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports/cache_load_tests',
        help='Diretório de saída dos relatórios (padrão: reports/cache_load_tests)'
    )
    
    # Parâmetros de configuração
    parser.add_argument(
        '--locustfile',
        type=str,
        default='tests/load/medium/infrastructure/locustfile_cache_load_v1.py',
        help='Arquivo locustfile a ser executado'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Executar em modo headless (sem interface web)'
    )
    
    parser.add_argument(
        '--stop-timeout',
        type=int,
        default=30,
        help='Timeout para parar o teste em segundos (padrão: 30)'
    )
    
    return parser.parse_args()

def validate_environment():
    """Validar ambiente de execução"""
    print("🔍 Validando ambiente de execução...")
    
    # Verificar se o locustfile existe
    locustfile_path = Path('tests/load/medium/infrastructure/locustfile_cache_load_v1.py')
    if not locustfile_path.exists():
        print(f"❌ Locustfile não encontrado: {locustfile_path}")
        return False
    
    # Verificar se o diretório de relatórios existe
    output_dir = Path('reports/cache_load_tests')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("✅ Ambiente validado com sucesso")
    return True

def build_locust_command(args):
    """Construir comando do Locust"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Comando base
    cmd = [
        'locust',
        '-f', args.locustfile,
        '--host', args.host,
        '--users', str(args.users),
        '--spawn-rate', str(args.spawn_rate),
        '--run-time', f'{args.duration}s',
        '--stop-timeout', str(args.stop_timeout)
    ]
    
    # Adicionar parâmetros de relatório
    if args.html_report:
        html_file = f'reports/cache_load_tests/cache_load_test_{timestamp}.html'
        cmd.extend(['--html', html_file])
    
    if args.json_report:
        json_file = f'reports/cache_load_tests/cache_load_test_{timestamp}.json'
        cmd.extend(['--json', json_file])
    
    if args.csv_report:
        csv_prefix = f'reports/cache_load_tests/cache_load_test_{timestamp}'
        cmd.extend(['--csv', csv_prefix])
    
    # Modo headless
    if args.headless:
        cmd.append('--headless')
    
    return cmd

def run_cache_load_test(args):
    """Executar teste de carga de cache"""
    print("🚀 Iniciando teste de carga de cache...")
    print(f"   - Usuários: {args.users}")
    print(f"   - Taxa de spawn: {args.spawn_rate}/s")
    print(f"   - Host: {args.host}")
    print(f"   - Duração: {args.duration}s")
    print(f"   - Modo: {'Headless' if args.headless else 'Web UI'}")
    
    # Construir comando
    cmd = build_locust_command(args)
    
    print(f"📋 Comando: {' '.join(cmd)}")
    
    try:
        # Executar comando
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=args.duration + 60)
        end_time = time.time()
        
        # Analisar resultado
        if result.returncode == 0:
            print("✅ Teste de carga de cache concluído com sucesso")
            print(f"   - Tempo de execução: {end_time - start_time:.2f}s")
            
            # Analisar saída
            if result.stdout:
                print("📊 Resumo da execução:")
                lines = result.stdout.split('\n')
                for line in lines[-10:]:  # Últimas 10 linhas
                    if line.strip():
                        print(f"   {line}")
            
            return True
        else:
            print("❌ Teste de carga de cache falhou")
            print(f"   - Código de retorno: {result.returncode}")
            if result.stderr:
                print(f"   - Erro: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Teste de carga de cache atingiu timeout")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False

def generate_test_report(args):
    """Gerar relatório do teste"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report_data = {
        'test_info': {
            'name': 'Cache Load Test',
            'timestamp': timestamp,
            'duration': args.duration,
            'users': args.users,
            'spawn_rate': args.spawn_rate,
            'host': args.host
        },
        'configuration': {
            'cache_stress': args.cache_stress,
            'cache_warming': args.cache_warming,
            'cache_invalidation': args.cache_invalidation,
            'cache_metrics': args.cache_metrics
        },
        'results': {
            'status': 'completed',
            'execution_time': None,
            'total_requests': None,
            'avg_response_time': None,
            'error_rate': None
        }
    }
    
    # Salvar relatório JSON
    report_file = f'reports/cache_load_tests/cache_load_test_report_{timestamp}.json'
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"📄 Relatório gerado: {report_file}")
    return report_file

def main():
    """Função principal"""
    print("=" * 60)
    print("🧪 TESTE DE CARGA DE CACHE - OMNI KEYWORDS FINDER")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Tracing ID: LOAD_CACHE_20250127_001")
    print()
    
    # Parse argumentos
    args = parse_arguments()
    
    # Validar ambiente
    if not validate_environment():
        sys.exit(1)
    
    # Executar teste
    success = run_cache_load_test(args)
    
    # Gerar relatório
    if success:
        report_file = generate_test_report(args)
        print(f"📊 Relatório salvo em: {report_file}")
    
    # Resumo final
    print()
    print("=" * 60)
    if success:
        print("✅ TESTE DE CARGA DE CACHE CONCLUÍDO COM SUCESSO")
    else:
        print("❌ TESTE DE CARGA DE CACHE FALHOU")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 