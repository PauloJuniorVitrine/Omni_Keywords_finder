#!/usr/bin/env python3
"""
Script de Execução dos Testes de Memory Leaks
Omni Keywords Finder - Tracing ID: MEMORY_LEAK_RUNNER_20250127_001

Este script executa todos os testes de memory leaks:
- Detecção de Memory Leaks
- Testes de Longa Duração
- Testes de Stress de Memória

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

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar testes de memory leak
from low.chaos.memory_leak_detection_test import MemoryLeakDetectionTest
from low.chaos.memory_leak_long_running_test import MemoryLeakLongRunningTest
from low.chaos.memory_leak_stress_test import MemoryLeakStressTest


class MemoryLeakTestRunner:
    """
    Executor de todos os testes de memory leaks
    """
    
    def __init__(self, host: str = "http://localhost:8000", verbose: bool = False, output_file: str = None):
        self.host = host
        self.verbose = verbose
        self.output_file = output_file
        self.tracing_id = "MEMORY_LEAK_RUNNER_20250127_001"
        self.start_time = datetime.now()
        
        # Configurar logging
        self.setup_logging()
        
        # Resultados dos testes
        self.test_results = {
            'tracing_id': self.tracing_id,
            'start_time': self.start_time.isoformat(),
            'host': self.host,
            'tests': {},
            'summary': {},
            'recommendations': []
        }
        
    def setup_logging(self):
        """Configura logging básico"""
        import logging
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
        )
        self.logger = logging.getLogger(f"MemoryLeakTestRunner_{self.tracing_id}")
        
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
    
    def run_detection_test(self) -> Dict[str, Any]:
        """Executa teste de detecção de memory leaks"""
        self.log("🔍 Iniciando teste de detecção de memory leaks")
        
        try:
            test = MemoryLeakDetectionTest(host=self.host, verbose=self.verbose)
            result = test.run()
            
            self.log(f"✅ Teste de detecção concluído: {result.get('success', False)}")
            return result
            
        except Exception as e:
            error_msg = f"Erro no teste de detecção: {str(e)}"
            self.log(error_msg, "ERROR")
            return {'success': False, 'error': error_msg}
    
    def run_long_running_test(self) -> Dict[str, Any]:
        """Executa teste de memory leaks de longa duração"""
        self.log("⏰ Iniciando teste de memory leaks de longa duração")
        
        try:
            test = MemoryLeakLongRunningTest(host=self.host, verbose=self.verbose)
            result = test.run()
            
            self.log(f"✅ Teste de longa duração concluído: {result.get('success', False)}")
            return result
            
        except Exception as e:
            error_msg = f"Erro no teste de longa duração: {str(e)}"
            self.log(error_msg, "ERROR")
            return {'success': False, 'error': error_msg}
    
    def run_stress_test(self) -> Dict[str, Any]:
        """Executa teste de stress de memória"""
        self.log("💥 Iniciando teste de stress de memória")
        
        try:
            test = MemoryLeakStressTest(host=self.host, verbose=self.verbose)
            result = test.run()
            
            self.log(f"✅ Teste de stress concluído: {result.get('success', False)}")
            return result
            
        except Exception as e:
            error_msg = f"Erro no teste de stress: {str(e)}"
            self.log(error_msg, "ERROR")
            return {'success': False, 'error': error_msg}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de memory leaks"""
        self.log("🚀 Iniciando execução de todos os testes de memory leaks")
        
        try:
            # Executar teste de detecção
            self.log("="*60)
            self.log("TESTE 1: Detecção de Memory Leaks")
            self.log("="*60)
            detection_result = self.run_detection_test()
            self.test_results['tests']['detection'] = detection_result
            
            # Pausa entre testes
            time.sleep(5)
            
            # Executar teste de longa duração
            self.log("="*60)
            self.log("TESTE 2: Memory Leaks de Longa Duração")
            self.log("="*60)
            long_running_result = self.run_long_running_test()
            self.test_results['tests']['long_running'] = long_running_result
            
            # Pausa entre testes
            time.sleep(5)
            
            # Executar teste de stress
            self.log("="*60)
            self.log("TESTE 3: Stress de Memória")
            self.log("="*60)
            stress_result = self.run_stress_test()
            self.test_results['tests']['stress'] = stress_result
            
            # Gerar resumo geral
            self.test_results['summary'] = self.generate_overall_summary()
            self.test_results['recommendations'] = self.generate_recommendations()
            self.test_results['end_time'] = datetime.now().isoformat()
            
            # Salvar resultados se arquivo especificado
            if self.output_file:
                self.save_results()
            
            self.log("✅ Todos os testes de memory leaks concluídos")
            
        except Exception as e:
            error_msg = f"Erro durante execução dos testes: {str(e)}"
            self.log(error_msg, "ERROR")
            self.test_results['success'] = False
            self.test_results['error'] = error_msg
        
        return self.test_results
    
    def generate_overall_summary(self) -> Dict[str, Any]:
        """Gera resumo geral dos resultados"""
        tests = self.test_results['tests']
        
        total_tests = len(tests)
        successful_tests = sum(1 for test in tests.values() if test.get('success', False))
        
        # Análise por tipo de teste
        test_analysis = {}
        for test_name, test_result in tests.items():
            test_analysis[test_name] = {
                'success': test_result.get('success', False),
                'scenarios_executed': 0,
                'memory_leaks_detected': 0,
                'thresholds_exceeded': 0
            }
            
            # Extrair métricas específicas
            if test_name == 'detection':
                summary = test_result.get('summary', {})
                test_analysis[test_name]['scenarios_executed'] = summary.get('total_scenarios', 0)
                test_analysis[test_name]['memory_leaks_detected'] = summary.get('leaks_detected', 0)
            
            elif test_name == 'long_running':
                summary = test_result.get('summary', {})
                test_analysis[test_name]['scenarios_executed'] = summary.get('total_scenarios', 0)
                test_analysis[test_name]['thresholds_exceeded'] = summary.get('threshold_exceeded', 0)
            
            elif test_name == 'stress':
                summary = test_result.get('summary', {})
                test_analysis[test_name]['scenarios_executed'] = summary.get('total_scenarios', 0)
                test_analysis[test_name]['thresholds_exceeded'] = summary.get('targets_reached', 0)
        
        # Calcular métricas gerais
        total_scenarios = sum(analysis['scenarios_executed'] for analysis in test_analysis.values())
        total_leaks_detected = sum(analysis['memory_leaks_detected'] for analysis in test_analysis.values())
        total_thresholds_exceeded = sum(analysis['thresholds_exceeded'] for analysis in test_analysis.values())
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'total_scenarios': total_scenarios,
            'total_leaks_detected': total_leaks_detected,
            'total_thresholds_exceeded': total_thresholds_exceeded,
            'test_analysis': test_analysis,
            'overall_success': successful_tests == total_tests
        }
    
    def generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        summary = self.test_results['summary']
        
        # Análise de sucesso geral
        if summary.get('success_rate', 0) < 0.8:
            recommendations.append("⚠️ Taxa de sucesso baixa. Revisar configurações dos testes.")
        
        # Análise de memory leaks detectados
        if summary.get('total_leaks_detected', 0) > 0:
            recommendations.append("🚨 Memory leaks detectados. Investigar e corrigir vazamentos.")
        
        # Análise de thresholds excedidos
        if summary.get('total_thresholds_exceeded', 0) > 0:
            recommendations.append("📈 Thresholds de memória excedidos. Otimizar uso de memória.")
        
        # Análise por teste
        test_analysis = summary.get('test_analysis', {})
        
        if not test_analysis.get('detection', {}).get('success', False):
            recommendations.append("🔍 Teste de detecção falhou. Verificar configurações de monitoramento.")
        
        if not test_analysis.get('long_running', {}).get('success', False):
            recommendations.append("⏰ Teste de longa duração falhou. Verificar estabilidade do sistema.")
        
        if not test_analysis.get('stress', {}).get('success', False):
            recommendations.append("💥 Teste de stress falhou. Verificar limites de memória.")
        
        # Recomendações de otimização
        if summary.get('total_scenarios', 0) > 0:
            leak_rate = summary.get('total_leaks_detected', 0) / summary.get('total_scenarios', 1)
            if leak_rate > 0.1:
                recommendations.append("🔧 Taxa de memory leaks alta. Implementar otimizações de memória.")
        
        # Se não há recomendações específicas
        if not recommendations:
            recommendations.append("✅ Todos os testes passaram. Sistema está estável em relação a memory leaks.")
        
        return recommendations
    
    def save_results(self):
        """Salva os resultados em arquivo JSON"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
            
            self.log(f"💾 Resultados salvos em: {self.output_file}")
            
        except Exception as e:
            self.log(f"Erro ao salvar resultados: {str(e)}", "ERROR")
    
    def print_results(self):
        """Imprime os resultados de forma formatada"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO COMPLETO DOS TESTES DE MEMORY LEAKS")
        print("="*80)
        print(f"🆔 Tracing ID: {self.test_results['tracing_id']}")
        print(f"🔗 Host: {self.test_results['host']}")
        print(f"⏰ Início: {self.test_results['start_time']}")
        print(f"⏰ Fim: {self.test_results['end_time']}")
        
        # Resumo geral
        summary = self.test_results['summary']
        print(f"\n📈 RESUMO GERAL:")
        print(f"   • Testes Executados: {summary['total_tests']}")
        print(f"   • Testes Bem-sucedidos: {summary['successful_tests']}")
        print(f"   • Taxa de Sucesso: {summary['success_rate']:.1%}")
        print(f"   • Cenários Totais: {summary['total_scenarios']}")
        print(f"   • Memory Leaks Detectados: {summary['total_leaks_detected']}")
        print(f"   • Thresholds Excedidos: {summary['total_thresholds_exceeded']}")
        print(f"   • Sucesso Geral: {'✅ SIM' if summary['overall_success'] else '❌ NÃO'}")
        
        # Análise por teste
        print(f"\n🔍 ANÁLISE POR TESTE:")
        test_analysis = summary.get('test_analysis', {})
        for test_name, analysis in test_analysis.items():
            status = "✅ PASSOU" if analysis['success'] else "❌ FALHOU"
            print(f"   • {test_name.replace('_', ' ').title()}: {status}")
            print(f"     - Cenários: {analysis['scenarios_executed']}")
            print(f"     - Memory Leaks: {analysis['memory_leaks_detected']}")
            print(f"     - Thresholds: {analysis['thresholds_exceeded']}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        recommendations = self.test_results.get('recommendations', [])
        for i, recommendation in enumerate(recommendations, 1):
            print(f"   {i}. {recommendation}")
        
        print("="*80)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executor de Testes de Memory Leaks")
    parser.add_argument('--host', default='http://localhost:8000', help='Host para testar')
    parser.add_argument('--verbose', action='store_true', help='Modo verboso')
    parser.add_argument('--output', help='Arquivo para salvar resultados JSON')
    parser.add_argument('--test', choices=['detection', 'long_running', 'stress', 'all'], 
                       default='all', help='Tipo de teste a executar')
    
    args = parser.parse_args()
    
    # Criar executor
    runner = MemoryLeakTestRunner(
        host=args.host,
        verbose=args.verbose,
        output_file=args.output
    )
    
    try:
        if args.test == 'all':
            # Executar todos os testes
            result = runner.run_all_tests()
        else:
            # Executar teste específico
            if args.test == 'detection':
                result = runner.run_detection_test()
            elif args.test == 'long_running':
                result = runner.run_long_running_test()
            elif args.test == 'stress':
                result = runner.run_stress_test()
            
            runner.test_results['tests'][args.test] = result
            runner.test_results['summary'] = runner.generate_overall_summary()
            runner.test_results['recommendations'] = runner.generate_recommendations()
            runner.test_results['end_time'] = datetime.now().isoformat()
        
        # Imprimir resultados
        runner.print_results()
        
        # Retornar código de saída
        summary = runner.test_results['summary']
        if summary.get('overall_success', False):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 