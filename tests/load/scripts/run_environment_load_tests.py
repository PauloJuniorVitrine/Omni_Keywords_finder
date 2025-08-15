#!/usr/bin/env python3
"""
Script de Execução dos Testes de Ambiente - Omni Keywords Finder
Tracing ID: ENV_LOAD_TESTS_20250127_001

Este script executa todos os testes de ambiente implementados:
- Testes de staging
- Testes de ambiente similar à produção
- Testes multi-região
- Gerador de dados de teste
- Configurações de teste
- Monitoramento de testes

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import os
import sys
import argparse
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.load.medium.environment.environment_staging_test import EnvironmentStagingTest
from tests.load.medium.environment.environment_production_like_test import EnvironmentProductionLikeTest
from tests.load.medium.environment.environment_multi_region_test import EnvironmentMultiRegionTest
from tests.load.medium.environment.environment_test_data_generator import EnvironmentTestDataGenerator
from tests.load.medium.environment.environment_test_configuration import EnvironmentTestConfiguration
from tests.load.medium.environment.environment_test_monitoring import EnvironmentTestMonitoring


class EnvironmentLoadTestRunner:
    """
    Executor de testes de carga de ambiente
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.results = {}
        self.start_time = datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log estruturado com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def run_test(self, test_class, test_name: str) -> dict:
        """Executa um teste específico"""
        self.log(f"Iniciando teste: {test_name}")
        
        try:
            # Criar instância do teste
            test_instance = test_class(host=self.host, verbose=self.verbose)
            
            # Executar teste
            start_time = time.time()
            result = test_instance.run()
            end_time = time.time()
            
            # Calcular métricas
            execution_time = end_time - start_time
            success = result.get('success', False)
            
            test_result = {
                'test_name': test_name,
                'success': success,
                'execution_time': execution_time,
                'details': result,
                'timestamp': datetime.now().isoformat()
            }
            
            status = "✅ SUCESSO" if success else "❌ FALHA"
            self.log(f"Teste {test_name} concluído: {status} ({execution_time:.2f}s)")
            
            return test_result
            
        except Exception as e:
            self.log(f"Erro no teste {test_name}: {str(e)}", "ERROR")
            return {
                'test_name': test_name,
                'success': False,
                'execution_time': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_all_tests(self) -> dict:
        """Executa todos os testes de ambiente"""
        self.log("🚀 Iniciando execução de todos os testes de ambiente")
        
        # Lista de testes a executar
        tests = [
            (EnvironmentStagingTest, "Testes de Ambiente de Staging"),
            (EnvironmentProductionLikeTest, "Testes de Ambiente Similar à Produção"),
            (EnvironmentMultiRegionTest, "Testes Multi-Região"),
            (EnvironmentTestDataGenerator, "Gerador de Dados de Teste"),
            (EnvironmentTestConfiguration, "Configurações de Teste"),
            (EnvironmentTestMonitoring, "Monitoramento de Testes")
        ]
        
        # Executar cada teste
        for test_class, test_name in tests:
            result = self.run_test(test_class, test_name)
            self.results[test_name] = result
            
            # Pequena pausa entre testes
            time.sleep(1)
        
        return self.generate_report()
    
    def generate_report(self) -> dict:
        """Gera relatório final dos testes"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        # Calcular estatísticas
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Tempo total de execução
        total_execution_time = sum(r['execution_time'] for r in self.results.values())
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'total_execution_time': total_execution_time,
                'total_wall_time': total_time,
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat()
            },
            'results': self.results,
            'host': self.host,
            'tracing_id': 'ENV_LOAD_TESTS_20250127_001'
        }
        
        return report
    
    def print_report(self, report: dict):
        """Imprime relatório formatado"""
        summary = report['summary']
        
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE TESTES DE AMBIENTE - OMNI KEYWORDS FINDER")
        print("="*80)
        print(f"🔗 Host: {report['host']}")
        print(f"🆔 Tracing ID: {report['tracing_id']}")
        print(f"⏰ Início: {summary['start_time']}")
        print(f"⏰ Fim: {summary['end_time']}")
        print(f"⏱️  Tempo Total: {summary['total_wall_time']:.2f}s")
        print(f"⚡ Tempo de Execução: {summary['total_execution_time']:.2f}s")
        print()
        
        print("📈 ESTATÍSTICAS:")
        print(f"   • Total de Testes: {summary['total_tests']}")
        print(f"   • Testes Bem-sucedidos: {summary['successful_tests']}")
        print(f"   • Testes Falharam: {summary['failed_tests']}")
        print(f"   • Taxa de Sucesso: {summary['success_rate']:.1f}%")
        print()
        
        print("📋 DETALHES POR TESTE:")
        for test_name, result in report['results'].items():
            status = "✅" if result['success'] else "❌"
            execution_time = result['execution_time']
            print(f"   {status} {test_name}: {execution_time:.2f}s")
            
            if not result['success'] and 'error' in result:
                print(f"      Erro: {result['error']}")
        
        print("="*80)
        
        # Status final
        if summary['success_rate'] == 100:
            print("🎉 TODOS OS TESTES PASSARAM!")
        elif summary['success_rate'] >= 80:
            print("⚠️  MAIORIA DOS TESTES PASSOU - VERIFICAR FALHAS")
        else:
            print("🚨 MUITOS TESTES FALHARAM - INVESTIGAR URGENTEMENTE")
        
        print("="*80)
    
    def save_report(self, report: dict, output_file: str = None):
        """Salva relatório em arquivo JSON"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"environment_load_test_report_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.log(f"Relatório salvo em: {output_file}")
            return output_file
            
        except Exception as e:
            self.log(f"Erro ao salvar relatório: {str(e)}", "ERROR")
            return None


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Executor de Testes de Carga de Ambiente - Omni Keywords Finder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_environment_load_tests.py
  python run_environment_load_tests.py --host http://staging.example.com
  python run_environment_load_tests.py --verbose --output report.json
        """
    )
    
    parser.add_argument(
        '--host',
        default='http://localhost:8000',
        help='URL do host para testar (padrão: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verboso para logs detalhados'
    )
    
    parser.add_argument(
        '--output',
        help='Arquivo de saída para o relatório JSON'
    )
    
    parser.add_argument(
        '--test',
        choices=[
            'staging',
            'production-like',
            'multi-region',
            'data-generator',
            'configuration',
            'monitoring',
            'all'
        ],
        default='all',
        help='Teste específico a executar (padrão: all)'
    )
    
    args = parser.parse_args()
    
    # Criar executor
    runner = EnvironmentLoadTestRunner(host=args.host, verbose=args.verbose)
    
    try:
        if args.test == 'all':
            # Executar todos os testes
            report = runner.run_all_tests()
        else:
            # Executar teste específico
            test_map = {
                'staging': (EnvironmentStagingTest, "Testes de Ambiente de Staging"),
                'production-like': (EnvironmentProductionLikeTest, "Testes de Ambiente Similar à Produção"),
                'multi-region': (EnvironmentMultiRegionTest, "Testes Multi-Região"),
                'data-generator': (EnvironmentTestDataGenerator, "Gerador de Dados de Teste"),
                'configuration': (EnvironmentTestConfiguration, "Configurações de Teste"),
                'monitoring': (EnvironmentTestMonitoring, "Monitoramento de Testes")
            }
            
            test_class, test_name = test_map[args.test]
            result = runner.run_test(test_class, test_name)
            report = {
                'summary': {
                    'total_tests': 1,
                    'successful_tests': 1 if result['success'] else 0,
                    'failed_tests': 0 if result['success'] else 1,
                    'success_rate': 100 if result['success'] else 0,
                    'total_execution_time': result['execution_time'],
                    'total_wall_time': result['execution_time'],
                    'start_time': runner.start_time.isoformat(),
                    'end_time': datetime.now().isoformat()
                },
                'results': {test_name: result},
                'host': args.host,
                'tracing_id': 'ENV_LOAD_TESTS_20250127_001'
            }
        
        # Imprimir relatório
        runner.print_report(report)
        
        # Salvar relatório
        if args.output:
            runner.save_report(report, args.output)
        else:
            runner.save_report(report)
        
        # Código de saída baseado no sucesso
        success_rate = report['summary']['success_rate']
        if success_rate == 100:
            sys.exit(0)  # Sucesso total
        elif success_rate >= 80:
            sys.exit(1)  # Maioria passou
        else:
            sys.exit(2)  # Muitas falhas
            
    except KeyboardInterrupt:
        print("\n⚠️  Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 