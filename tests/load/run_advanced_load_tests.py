"""
🧪 INT-011: Script Principal de Advanced Load Testing - Omni Keywords Finder

Tracing ID: INT_011_SCRIPT_MAIN_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 PRONTO PARA EXECUÇÃO

Objetivo: Script principal para executar todos os testes de carga avançados
conforme especificado no checklist INT-011.

Como executar:
    python tests/load/run_advanced_load_tests.py
    python tests/load/run_advanced_load_tests.py --scenario stress
    python tests/load/run_advanced_load_tests.py --all
"""

import asyncio
import argparse
import logging
import sys
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from tests.load.advanced_load_tests import (
    AdvancedLoadTesting,
    LoadTestConfig,
    LoadTestType,
    LoadPattern,
    load_load_scenarios,
    run_load_test_suite
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler('load_test_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AdvancedLoadTestRunner:
    """Runner principal para testes de carga avançados."""
    
    def __init__(self):
        self.scenarios_file = "tests/load/load_scenarios.yaml"
        self.results_dir = "tests/load/results"
        self.reports_dir = "tests/load/reports"
        
        # Criar diretórios se não existirem
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def run_single_scenario(self, scenario_name: str) -> bool:
        """
        Executa um cenário específico.
        
        Args:
            scenario_name: Nome do cenário a executar
            
        Returns:
            True se executado com sucesso, False caso contrário
        """
        try:
            logger.info(f"Executando cenário: {scenario_name}")
            
            # Carrega cenários do arquivo YAML
            scenarios = load_load_scenarios(self.scenarios_file)
            
            # Encontra o cenário específico
            target_scenario = None
            for scenario in scenarios:
                if scenario.test_type.value == scenario_name.lower():
                    target_scenario = scenario
                    break
            
            if not target_scenario:
                logger.error(f"Cenário '{scenario_name}' não encontrado")
                return False
            
            # Executa o teste
            load_test = AdvancedLoadTesting(target_scenario)
            result = await load_test.run_load_test()
            
            # Salva resultado
            self._save_result(result, scenario_name)
            
            # Gera relatório
            self._generate_report(result, scenario_name)
            
            logger.info(f"✅ Cenário '{scenario_name}' executado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar cenário '{scenario_name}': {e}")
            return False
    
    async def run_all_scenarios(self) -> bool:
        """
        Executa todos os cenários de teste.
        
        Returns:
            True se todos executados com sucesso, False caso contrário
        """
        try:
            logger.info("Executando todos os cenários de teste")
            
            # Carrega cenários do arquivo YAML
            scenarios = load_load_scenarios(self.scenarios_file)
            
            if not scenarios:
                logger.error("Nenhum cenário encontrado no arquivo YAML")
                return False
            
            # Executa suite completa
            results = await run_load_test_suite(scenarios)
            
            # Salva resultados
            for index, result in enumerate(results):
                scenario_name = f"scenario_{index+1}_{result.test_type.value}"
                self._save_result(result, scenario_name)
                self._generate_report(result, scenario_name)
            
            # Gera relatório consolidado
            self._generate_consolidated_report(results)
            
            logger.info(f"✅ Todos os {len(results)} cenários executados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar todos os cenários: {e}")
            return False
    
    async def run_stress_tests(self) -> bool:
        """Executa apenas testes de stress."""
        return await self._run_test_type("stress")
    
    async def run_spike_tests(self) -> bool:
        """Executa apenas testes de spike."""
        return await self._run_test_type("spike")
    
    async def run_endurance_tests(self) -> bool:
        """Executa apenas testes de endurance."""
        return await self._run_test_type("endurance")
    
    async def run_scalability_tests(self) -> bool:
        """Executa apenas testes de escalabilidade."""
        return await self._run_test_type("scalability")
    
    async def _run_test_type(self, test_type: str) -> bool:
        """Executa testes de um tipo específico."""
        try:
            logger.info(f"Executando testes de {test_type}")
            
            scenarios = load_load_scenarios(self.scenarios_file)
            type_scenarios = [string_data for string_data in scenarios if string_data.test_type.value == test_type]
            
            if not type_scenarios:
                logger.warning(f"Nenhum cenário de {test_type} encontrado")
                return True
            
            results = await run_load_test_suite(type_scenarios)
            
            for index, result in enumerate(results):
                scenario_name = f"{test_type}_{index+1}"
                self._save_result(result, scenario_name)
                self._generate_report(result, scenario_name)
            
            logger.info(f"✅ Testes de {test_type} executados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar testes de {test_type}: {e}")
            return False
    
    def _save_result(self, result, scenario_name: str):
        """Salva resultado do teste."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_dir}/{scenario_name}_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                f.write(result.to_json(indent=2))
            logger.info(f"Resultado salvo em: {filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar resultado: {e}")
    
    def _generate_report(self, result, scenario_name: str):
        """Gera relatório individual."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.reports_dir}/{scenario_name}_report_{timestamp}.html"
        
        try:
            # Aqui você pode implementar a geração de relatório HTML
            # Por enquanto, vamos criar um relatório simples
            report_content = self._create_simple_report(result, scenario_name)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Relatório gerado em: {filename}")
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
    
    def _generate_consolidated_report(self, results: List):
        """Gera relatório consolidado de todos os testes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.reports_dir}/consolidated_report_{timestamp}.html"
        
        try:
            report_content = self._create_consolidated_report(results)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Relatório consolidado gerado em: {filename}")
        except Exception as e:
            logger.error(f"Erro ao gerar relatório consolidado: {e}")
    
    def _create_simple_report(self, result, scenario_name: str) -> str:
        """Cria relatório HTML simples."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - {scenario_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Load Test Report - {scenario_name}</h1>
        <p>Test Type: {result.test_type.value}</p>
        <p>Start Time: {result.start_time}</p>
        <p>Duration: {result.duration:.2f} seconds</p>
        <p>Status: {result.status.value}</p>
    </div>
    
    <div class="metric">
        <h2>Performance Metrics</h2>
        <p>Total Requests: {result.total_requests}</p>
        <p>Successful Requests: {result.successful_requests}</p>
        <p>Failed Requests: {result.failed_requests}</p>
        <p>Error Rate: {result.error_rate:.2%}</p>
        <p>Average Response Time: {result.avg_response_time:.2f}ms</p>
        <p>P95 Response Time: {result.p95_response_time:.2f}ms</p>
        <p>Requests per Second: {result.requests_per_second:.2f}</p>
    </div>
    
    <div class="metric">
        <h2>Test Summary</h2>
        <p class="{'success' if result.success else 'error'}">
            Overall Result: {'PASS' if result.success else 'FAIL'}
        </p>
    </div>
</body>
</html>
        """
    
    def _create_consolidated_report(self, results: List) -> str:
        """Cria relatório HTML consolidado."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Consolidated Load Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; padding: 15px; border: 2px solid #ddd; border-radius: 5px; }}
        .test-result {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ border-left: 5px solid green; }}
        .error {{ border-left: 5px solid red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Consolidated Load Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <p>Total Tests: {total_tests}</p>
        <p>Passed: {passed_tests}</p>
        <p>Failed: {failed_tests}</p>
        <p>Success Rate: {(passed_tests/total_tests)*100:.1f}%</p>
    </div>
    
    <h2>Individual Test Results</h2>
    {''.join([f'''
    <div class="test-result {'success' if r.success else 'error'}">
        <h3>{r.test_type.value} Test</h3>
        <p>Status: {r.status.value}</p>
        <p>Duration: {r.duration:.2f}string_data</p>
        <p>Error Rate: {r.error_rate:.2%}</p>
        <p>Avg Response Time: {r.avg_response_time:.2f}ms</p>
    </div>
    ''' for r in results])}
</body>
</html>
        """

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Advanced Load Testing Runner')
    parser.add_argument('--scenario', type=str, help='Executar cenário específico')
    parser.add_argument('--all', action='store_true', help='Executar todos os cenários')
    parser.add_argument('--stress', action='store_true', help='Executar apenas testes de stress')
    parser.add_argument('--spike', action='store_true', help='Executar apenas testes de spike')
    parser.add_argument('--endurance', action='store_true', help='Executar apenas testes de endurance')
    parser.add_argument('--scalability', action='store_true', help='Executar apenas testes de escalabilidade')
    
    args = parser.parse_args()
    
    runner = AdvancedLoadTestRunner()
    
    try:
        if args.scenario:
            success = asyncio.run(runner.run_single_scenario(args.scenario))
        elif args.all:
            success = asyncio.run(runner.run_all_scenarios())
        elif args.stress:
            success = asyncio.run(runner.run_stress_tests())
        elif args.spike:
            success = asyncio.run(runner.run_spike_tests())
        elif args.endurance:
            success = asyncio.run(runner.run_endurance_tests())
        elif args.scalability:
            success = asyncio.run(runner.run_scalability_tests())
        else:
            print("Por favor, especifique uma opção. Use --help para ver as opções disponíveis.")
            return
        
        if success:
            print("✅ Todos os testes executados com sucesso!")
            sys.exit(0)
        else:
            print("❌ Alguns testes falharam.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 