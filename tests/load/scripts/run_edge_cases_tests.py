#!/usr/bin/env python3
"""
Script para Executar Testes de Edge Cases
Omni Keywords Finder - Tracing ID: EDGE_CASES_RUNNER_20250127_001

Este script executa todos os testes de Edge Cases implementados:
- Dados Inválidos
- Requisições Malformadas
- Valores Extremos
- Acesso Concorrente

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar os testes de Edge Cases
from tests.load.low.chaos.edge_cases_invalid_data_test import EdgeCasesInvalidDataTest
from tests.load.low.chaos.edge_cases_malformed_requests_test import EdgeCasesMalformedRequestsTest
from tests.load.low.chaos.edge_cases_extreme_values_test import EdgeCasesExtremeValuesTest
from tests.load.low.chaos.edge_cases_concurrent_access_test import EdgeCasesConcurrentAccessTest


class EdgeCasesTestRunner:
    """
    Runner para executar todos os testes de Edge Cases
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False, output_file: str = None):
        self.host = host
        self.verbose = verbose
        self.output_file = output_file
        self.tracing_id = "EDGE_CASES_RUNNER_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Testes disponíveis
        self.available_tests = {
            'invalid_data': {
                'name': 'Dados Inválidos',
                'class': EdgeCasesInvalidDataTest,
                'description': 'Testa comportamento com dados inválidos'
            },
            'malformed_requests': {
                'name': 'Requisições Malformadas',
                'class': EdgeCasesMalformedRequestsTest,
                'description': 'Testa comportamento com requisições malformadas'
            },
            'extreme_values': {
                'name': 'Valores Extremos',
                'class': EdgeCasesExtremeValuesTest,
                'description': 'Testa comportamento com valores extremos'
            },
            'concurrent_access': {
                'name': 'Acesso Concorrente',
                'class': EdgeCasesConcurrentAccessTest,
                'description': 'Testa comportamento com acesso concorrente'
            }
        }
        
        # Resultados coletados
        self.results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'tests_executed': [],
            'summary': {},
            'success': False
        }
        
    def setup_logging(self):
        """Configura logging básico"""
        import logging
        
        level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=level,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
        )
        self.logger = logging.getLogger(f"EdgeCasesRunner_{self.tracing_id}")
    
    def log(self, message: str, level: str = "INFO"):
        """Log estruturado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] [{self.tracing_id}] {message}"
        
        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def run_single_test(self, test_key: str) -> Dict[str, Any]:
        """Executa um teste específico"""
        if test_key not in self.available_tests:
            raise ValueError(f"Teste '{test_key}' não encontrado")
        
        test_info = self.available_tests[test_key]
        self.log(f"🚀 Executando teste: {test_info['name']}")
        
        try:
            # Criar instância do teste
            test_instance = test_info['class'](host=self.host, verbose=self.verbose)
            
            # Executar teste
            start_time = time.time()
            result = test_instance.run()
            end_time = time.time()
            
            # Adicionar metadados
            result['test_key'] = test_key
            result['test_name'] = test_info['name']
            result['execution_time'] = end_time - start_time
            result['start_time'] = datetime.fromtimestamp(start_time).isoformat()
            result['end_time'] = datetime.fromtimestamp(end_time).isoformat()
            
            self.log(f"✅ Teste {test_info['name']} concluído em {result['execution_time']:.2f}s")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao executar teste {test_info['name']}: {str(e)}"
            self.log(error_msg, "ERROR")
            
            return {
                'test_key': test_key,
                'test_name': test_info['name'],
                'success': False,
                'error': error_msg,
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat()
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de Edge Cases"""
        self.log("🚀 Iniciando execução de todos os testes de Edge Cases")
        
        try:
            # Executar cada teste
            for test_key, test_info in self.available_tests.items():
                self.log(f"Executando {test_info['name']}...")
                
                test_result = self.run_single_test(test_key)
                self.results['tests_executed'].append(test_result)
                
                # Pausa entre testes
                time.sleep(2)
            
            # Gerar resumo
            self.results['summary'] = self.generate_summary()
            self.results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            successful_tests = sum(1 for t in self.results['tests_executed'] if t.get('success', False))
            total_tests = len(self.results['tests_executed'])
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            
            self.results['success'] = success_rate >= 0.75  # 75% de sucesso mínimo
            
            self.log(f"✅ Todos os testes concluídos: {success_rate:.1%} de sucesso")
            
        except Exception as e:
            error_msg = f"Erro durante execução dos testes: {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['success'] = False
            self.results['error'] = error_msg
        
        return self.results
    
    def run_specific_tests(self, test_keys: List[str]) -> Dict[str, Any]:
        """Executa testes específicos"""
        self.log(f"🚀 Iniciando execução de testes específicos: {', '.join(test_keys)}")
        
        try:
            # Executar testes especificados
            for test_key in test_keys:
                if test_key not in self.available_tests:
                    self.log(f"⚠️ Teste '{test_key}' não encontrado, pulando...", "WARNING")
                    continue
                
                test_result = self.run_single_test(test_key)
                self.results['tests_executed'].append(test_result)
                
                # Pausa entre testes
                time.sleep(2)
            
            # Gerar resumo
            self.results['summary'] = self.generate_summary()
            self.results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            successful_tests = sum(1 for t in self.results['tests_executed'] if t.get('success', False))
            total_tests = len(self.results['tests_executed'])
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            
            self.results['success'] = success_rate >= 0.75  # 75% de sucesso mínimo
            
            self.log(f"✅ Testes específicos concluídos: {success_rate:.1%} de sucesso")
            
        except Exception as e:
            error_msg = f"Erro durante execução dos testes: {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['success'] = False
            self.results['error'] = error_msg
        
        return self.results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Gera resumo dos resultados"""
        tests_executed = self.results['tests_executed']
        
        if not tests_executed:
            return {
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'success_rate': 0.0,
                'total_execution_time': 0.0
            }
        
        total_tests = len(tests_executed)
        successful_tests = sum(1 for t in tests_executed if t.get('success', False))
        failed_tests = total_tests - successful_tests
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # Calcular tempo total de execução
        total_execution_time = sum(t.get('execution_time', 0) for t in tests_executed)
        
        # Análise por tipo de teste
        test_type_analysis = {}
        for test in tests_executed:
            test_key = test.get('test_key', 'unknown')
            if test_key not in test_type_analysis:
                test_type_analysis[test_key] = {
                    'name': test.get('test_name', 'Unknown'),
                    'success': test.get('success', False),
                    'execution_time': test.get('execution_time', 0)
                }
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'total_execution_time': total_execution_time,
            'test_type_analysis': test_type_analysis
        }
    
    def save_results(self, results: Dict[str, Any]):
        """Salva os resultados em arquivo"""
        if not self.output_file:
            return
        
        try:
            # Criar diretório se não existir
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Salvar resultados
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            self.log(f"📄 Resultados salvos em: {self.output_file}")
            
        except Exception as e:
            self.log(f"Erro ao salvar resultados: {str(e)}", "ERROR")
    
    def print_results(self, results: Dict[str, Any]):
        """Imprime os resultados de forma formatada"""
        print("\n" + "="*80)
        print("📊 RESULTADOS DOS TESTES DE EDGE CASES")
        print("="*80)
        print(f"🆔 Tracing ID: {results['tracing_id']}")
        print(f"🔗 Host: {results['host']}")
        print(f"⏰ Início: {results['start_time']}")
        print(f"⏰ Fim: {results['end_time']}")
        print(f"✅ Sucesso Geral: {results['success']}")
        
        if 'summary' in results:
            summary = results['summary']
            print(f"\n📈 RESUMO GERAL:")
            print(f"   • Total de Testes: {summary['total_tests']}")
            print(f"   • Testes Bem-sucedidos: {summary['successful_tests']}")
            print(f"   • Testes Falharam: {summary['failed_tests']}")
            print(f"   • Taxa de Sucesso: {summary['success_rate']:.1%}")
            print(f"   • Tempo Total de Execução: {summary['total_execution_time']:.2f}s")
        
        if 'tests_executed' in results:
            print(f"\n🧪 DETALHES DOS TESTES:")
            for i, test in enumerate(results['tests_executed'], 1):
                test_name = test.get('test_name', 'Unknown')
                success = test.get('success', False)
                execution_time = test.get('execution_time', 0)
                status = "✅ PASSOU" if success else "❌ FALHOU"
                
                print(f"   {i}. {test_name}: {status} ({execution_time:.2f}s)")
                
                if not success and 'error' in test:
                    print(f"      Erro: {test['error']}")
        
        if 'summary' in results and 'test_type_analysis' in results['summary']:
            print(f"\n🔍 ANÁLISE POR TIPO DE TESTE:")
            for test_key, analysis in results['summary']['test_type_analysis'].items():
                status = "✅ PASSOU" if analysis['success'] else "❌ FALHOU"
                print(f"   • {analysis['name']}: {status} ({analysis['execution_time']:.2f}s)")
        
        print("="*80)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar Testes de Edge Cases")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    parser.add_argument('--output', help='Arquivo para salvar resultados (JSON)')
    parser.add_argument('--test', choices=['invalid_data', 'malformed_requests', 'extreme_values', 'concurrent_access'], 
                       help='Executar teste específico')
    parser.add_argument('--list', action='store_true', help='Listar testes disponíveis')
    
    args = parser.parse_args()
    
    # Listar testes disponíveis
    if args.list:
        print("🧪 TESTES DE EDGE CASES DISPONÍVEIS:")
        print("="*50)
        runner = EdgeCasesTestRunner()
        for test_key, test_info in runner.available_tests.items():
            print(f"• {test_key}: {test_info['name']}")
            print(f"  {test_info['description']}")
            print()
        return
    
    # Criar runner
    runner = EdgeCasesTestRunner(
        host=args.host,
        verbose=args.verbose,
        output_file=args.output
    )
    
    try:
        # Executar testes
        if args.test:
            # Executar teste específico
            results = runner.run_specific_tests([args.test])
        else:
            # Executar todos os testes
            results = runner.run_all_tests()
        
        # Salvar resultados
        if args.output:
            runner.save_results(results)
        
        # Imprimir resultados
        runner.print_results(results)
        
        # Retornar código de saída
        sys.exit(0 if results['success'] else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 