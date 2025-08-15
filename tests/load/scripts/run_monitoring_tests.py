#!/usr/bin/env python3
"""
Script para Executar Todos os Testes de Monitoramento
Omni Keywords Finder - Tracing ID: RUN_MONITORING_TESTS_20250127_001

Este script executa todos os testes de monitoramento:
- Métricas do Sistema
- Métricas da Aplicação  
- Métricas de Negócio
- Coleta de Logs
- Tracing Distribuído
- Alertas

Autor: IA-Cursor
Data: 2025-01-27
Versão: 1.0
"""

import os
import sys
import time
import json
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class MonitoringTestRunner:
    """Executor de testes de monitoramento"""
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False):
        self.host = host
        self.verbose = verbose
        self.tracing_id = "RUN_MONITORING_TESTS_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar diretórios
        self.base_dir = Path(__file__).parent.parent
        self.monitoring_dir = self.base_dir / "low" / "monitoring"
        self.logs_dir = Path("logs")
        self.results_dir = Path("test_results")
        
        # Criar diretórios se não existirem
        self.logs_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        # Lista de testes de monitoramento
        self.monitoring_tests = [
            {
                'name': 'Métricas do Sistema',
                'file': 'monitoring_system_metrics_test.py',
                'description': 'Teste de métricas do sistema sob carga',
                'category': 'system_metrics'
            },
            {
                'name': 'Métricas da Aplicação',
                'file': 'monitoring_application_metrics_test.py',
                'description': 'Teste de métricas da aplicação sob carga',
                'category': 'application_metrics'
            },
            {
                'name': 'Métricas de Negócio',
                'file': 'monitoring_business_metrics_test.py',
                'description': 'Teste de métricas de negócio sob carga',
                'category': 'business_metrics'
            },
            {
                'name': 'Coleta de Logs',
                'file': 'monitoring_log_generation_test.py',
                'description': 'Teste de coleta de logs sob carga',
                'category': 'log_generation'
            },
            {
                'name': 'Tracing Distribuído',
                'file': 'monitoring_distributed_tracing_test.py',
                'description': 'Teste de tracing distribuído sob carga',
                'category': 'distributed_tracing'
            },
            {
                'name': 'Alertas',
                'file': 'monitoring_alerts_test.py',
                'description': 'Teste de alertas sob carga',
                'category': 'alerts'
            }
        ]
        
        # Resultados dos testes
        self.test_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'tests': [],
            'summary': {},
            'success': False
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log estruturado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] [{self.tracing_id}] {message}")
    
    def run_single_test(self, test_info: Dict) -> Dict[str, Any]:
        """Executa um teste individual"""
        test_name = test_info['name']
        test_file = test_info['file']
        test_path = self.monitoring_dir / test_file
        
        self.log(f"🚀 Executando teste: {test_name}")
        
        result = {
            'name': test_name,
            'file': test_file,
            'category': test_info['category'],
            'start_time': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'output': None
        }
        
        try:
            # Verificar se o arquivo existe
            if not test_path.exists():
                raise FileNotFoundError(f"Arquivo de teste não encontrado: {test_path}")
            
            # Construir comando
            cmd = [
                sys.executable,
                str(test_path),
                '--host', self.host
            ]
            
            if self.verbose:
                cmd.append('--verbose')
            
            # Executar teste
            self.log(f"Executando comando: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.base_dir
            )
            
            stdout, stderr = process.communicate(timeout=3600)  # 1 hora de timeout
            
            # Analisar resultado
            result['output'] = stdout
            result['error_output'] = stderr
            result['return_code'] = process.returncode
            
            if process.returncode == 0:
                result['success'] = True
                self.log(f"✅ Teste {test_name} executado com sucesso")
            else:
                result['success'] = False
                result['error'] = f"Teste falhou com código {process.returncode}"
                self.log(f"❌ Teste {test_name} falhou: {result['error']}")
                if stderr:
                    self.log(f"Erro: {stderr}", "ERROR")
            
        except subprocess.TimeoutExpired:
            result['success'] = False
            result['error'] = "Teste excedeu o tempo limite de 1 hora"
            self.log(f"⏰ Teste {test_name} excedeu timeout", "WARNING")
            
        except FileNotFoundError as e:
            result['success'] = False
            result['error'] = str(e)
            self.log(f"📁 Erro de arquivo no teste {test_name}: {e}", "ERROR")
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            self.log(f"💥 Erro inesperado no teste {test_name}: {e}", "ERROR")
        
        result['end_time'] = datetime.now().isoformat()
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de monitoramento"""
        self.log("🚀 Iniciando execução de todos os testes de monitoramento")
        self.log(f"🔗 Host: {self.host}")
        self.log(f"📁 Diretório base: {self.base_dir}")
        
        try:
            # Executar cada teste
            for i, test_info in enumerate(self.monitoring_tests):
                self.log(f"Executando teste {i+1}/{len(self.monitoring_tests)}: {test_info['name']}")
                
                test_result = self.run_single_test(test_info)
                self.test_results['tests'].append(test_result)
                
                # Pausa entre testes
                if i < len(self.monitoring_tests) - 1:
                    self.log("⏳ Aguardando 30 segundos antes do próximo teste...")
                    time.sleep(30)
            
            # Gerar resumo
            self.test_results['summary'] = self.generate_summary()
            self.test_results['end_time'] = datetime.now().isoformat()
            
            # Calcular sucesso geral
            total_tests = len(self.test_results['tests'])
            successful_tests = sum(1 for t in self.test_results['tests'] if t['success'])
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            
            self.test_results['success'] = success_rate >= 0.8
            
            self.log(f"✅ Execução concluída: {success_rate:.1%} de sucesso ({successful_tests}/{total_tests})")
            
        except KeyboardInterrupt:
            self.log("⚠️ Execução interrompida pelo usuário", "WARNING")
            self.test_results['success'] = False
            self.test_results['error'] = "Execução interrompida pelo usuário"
            
        except Exception as e:
            self.log(f"💥 Erro durante execução: {str(e)}", "ERROR")
            self.test_results['success'] = False
            self.test_results['error'] = str(e)
        
        return self.test_results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Gera resumo dos resultados"""
        tests = self.test_results['tests']
        
        total_tests = len(tests)
        successful_tests = sum(1 for t in tests if t['success'])
        failed_tests = total_tests - successful_tests
        
        # Análise por categoria
        category_analysis = {}
        for test in tests:
            category = test['category']
            if category not in category_analysis:
                category_analysis[category] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            
            category_analysis[category]['total'] += 1
            if test['success']:
                category_analysis[category]['successful'] += 1
            else:
                category_analysis[category]['failed'] += 1
        
        # Calcular taxas de sucesso por categoria
        for category in category_analysis:
            total = category_analysis[category]['total']
            successful = category_analysis[category]['successful']
            category_analysis[category]['success_rate'] = successful / total if total > 0 else 0
        
        # Tempo total de execução
        start_time = datetime.fromisoformat(self.test_results['start_time'])
        end_time = datetime.fromisoformat(self.test_results['end_time'])
        total_duration = (end_time - start_time).total_seconds()
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'total_duration_seconds': total_duration,
            'category_analysis': category_analysis
        }
    
    def save_results(self, filename: str = None):
        """Salva os resultados em arquivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_test_results_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
            
            self.log(f"💾 Resultados salvos em: {filepath}")
            return filepath
            
        except Exception as e:
            self.log(f"❌ Erro ao salvar resultados: {e}", "ERROR")
            return None
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        summary = self.test_results.get('summary', {})
        
        print("\n" + "="*80)
        print("📊 RESUMO DOS TESTES DE MONITORAMENTO")
        print("="*80)
        print(f"🆔 Tracing ID: {self.test_results['tracing_id']}")
        print(f"🔗 Host: {self.test_results['host']}")
        print(f"⏰ Início: {self.test_results['start_time']}")
        print(f"⏰ Fim: {self.test_results['end_time']}")
        print(f"✅ Sucesso Geral: {self.test_results['success']}")
        
        if summary:
            print(f"\n📈 ESTATÍSTICAS GERAIS:")
            print(f"   • Total de Testes: {summary['total_tests']}")
            print(f"   • Testes Bem-sucedidos: {summary['successful_tests']}")
            print(f"   • Testes Falharam: {summary['failed_tests']}")
            print(f"   • Taxa de Sucesso: {summary['success_rate']:.1%}")
            print(f"   • Duração Total: {summary['total_duration_seconds']:.1f} segundos")
            
            print(f"\n📋 ANÁLISE POR CATEGORIA:")
            for category, analysis in summary.get('category_analysis', {}).items():
                print(f"   • {category.replace('_', ' ').title()}:")
                print(f"     - Total: {analysis['total']}")
                print(f"     - Sucessos: {analysis['successful']}")
                print(f"     - Falhas: {analysis['failed']}")
                print(f"     - Taxa: {analysis['success_rate']:.1%}")
        
        print(f"\n📝 DETALHES DOS TESTES:")
        for i, test in enumerate(self.test_results['tests'], 1):
            status = "✅" if test['success'] else "❌"
            print(f"   {i}. {status} {test['name']}")
            if not test['success'] and test.get('error'):
                print(f"      Erro: {test['error']}")
        
        print("="*80)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executor de Testes de Monitoramento")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    parser.add_argument('--save-results', action='store_true', help='Salvar resultados em arquivo')
    parser.add_argument('--results-file', help='Nome do arquivo para salvar resultados')
    
    args = parser.parse_args()
    
    # Criar e executar runner
    runner = MonitoringTestRunner(host=args.host, verbose=args.verbose)
    results = runner.run_all_tests()
    
    # Imprimir resumo
    runner.print_summary()
    
    # Salvar resultados se solicitado
    if args.save_results:
        runner.save_results(args.results_file)
    
    # Retornar código de saída baseado no sucesso
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main() 