"""
🚀 Script de Execução - Testes de Resiliência
=============================================

Tracing ID: run-resilience-load-tests-2025-01-27-001
Timestamp: 2025-01-27T20:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Baseado em padrões reais de execução de testes de carga
🌲 ToT: Avaliadas múltiplas estratégias de execução e escolhido mais eficiente
♻️ ReAct: Simulado execução e validado estratégia de teste

Executa testes de resiliência implementados:
- Circuit Breakers
- Retry Logic
- Graceful Degradation
"""

import asyncio
import time
import json
import logging
import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resilience_load_tests.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ResilienceTestConfig:
    """Configuração para execução dos testes de resiliência"""
    base_url: str = "http://localhost:8000"
    test_duration: int = 300  # 5 minutos
    concurrent_users: int = 50
    enable_circuit_breaker: bool = True
    enable_retry_logic: bool = True
    enable_graceful_degradation: bool = True
    parallel_execution: bool = False
    generate_reports: bool = True
    cleanup_reports: bool = False
    validate_thresholds: bool = True
    enable_monitoring: bool = True

@dataclass
class ResilienceTestThresholds:
    """Thresholds para validação dos testes de resiliência"""
    min_success_rate: float = 0.8  # 80%
    max_avg_response_time: float = 3.0  # 3 segundos
    max_p95_response_time: float = 8.0  # 8 segundos
    max_degradation_rate: float = 0.3  # 30%
    min_ux_score: float = 0.6  # 0.6
    max_circuit_open_rate: float = 0.2  # 20%
    min_retry_success_rate: float = 0.5  # 50%

class ResilienceLoadTestRunner:
    """Executor de testes de carga de resiliência"""
    
    def __init__(self, config: ResilienceTestConfig, thresholds: ResilienceTestThresholds):
        self.config = config
        self.thresholds = thresholds
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # Configurar paths
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.resilience_dir = os.path.join(self.test_dir, "..", "high", "resilience")
        self.reports_dir = os.path.join(self.test_dir, "..", "..", "reports", "resilience")
        
        # Criar diretório de relatórios se não existir
        os.makedirs(self.reports_dir, exist_ok=True)
        
        logger.info(f"Resilience Load Test Runner inicializado: {config}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de resiliência"""
        logger.info("🚀 Iniciando execução de todos os testes de resiliência")
        
        self.start_time = datetime.now()
        
        # Lista de testes a executar
        tests_to_run = []
        
        if self.config.enable_circuit_breaker:
            tests_to_run.append(("Circuit Breaker", self._run_circuit_breaker_test))
        
        if self.config.enable_retry_logic:
            tests_to_run.append(("Retry Logic", self._run_retry_logic_test))
        
        if self.config.enable_graceful_degradation:
            tests_to_run.append(("Graceful Degradation", self._run_graceful_degradation_test))
        
        # Executar testes
        if self.config.parallel_execution:
            results = await self._run_tests_parallel(tests_to_run)
        else:
            results = await self._run_tests_sequential(tests_to_run)
        
        self.end_time = datetime.now()
        
        # Gerar relatório consolidado
        consolidated_report = self._generate_consolidated_report(results)
        
        # Validar thresholds
        if self.config.validate_thresholds:
            validation_results = self._validate_thresholds(consolidated_report)
            consolidated_report["validation"] = validation_results
        
        # Salvar relatório
        if self.config.generate_reports:
            self._save_consolidated_report(consolidated_report)
        
        logger.info("✅ Execução de todos os testes de resiliência concluída")
        return consolidated_report
    
    async def _run_tests_parallel(self, tests_to_run: List[tuple]) -> Dict[str, Any]:
        """Executa testes em paralelo"""
        logger.info("🔄 Executando testes em paralelo")
        
        async def run_single_test(test_name: str, test_func):
            try:
                logger.info(f"🔄 Iniciando teste: {test_name}")
                result = await test_func()
                logger.info(f"✅ Teste concluído: {test_name}")
                return test_name, result
            except Exception as e:
                logger.error(f"❌ Erro no teste {test_name}: {e}")
                return test_name, {"error": str(e)}
        
        # Executar todos os testes em paralelo
        tasks = [run_single_test(test_name, test_func) for test_name, test_func in tests_to_run]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        test_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Erro na execução paralela: {result}")
                continue
            
            test_name, test_result = result
            test_results[test_name] = test_result
        
        return test_results
    
    async def _run_tests_sequential(self, tests_to_run: List[tuple]) -> Dict[str, Any]:
        """Executa testes sequencialmente"""
        logger.info("📋 Executando testes sequencialmente")
        
        test_results = {}
        
        for test_name, test_func in tests_to_run:
            try:
                logger.info(f"🔄 Iniciando teste: {test_name}")
                result = await test_func()
                test_results[test_name] = result
                logger.info(f"✅ Teste concluído: {test_name}")
                
                # Aguardar entre testes
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Erro no teste {test_name}: {e}")
                test_results[test_name] = {"error": str(e)}
        
        return test_results
    
    async def _run_circuit_breaker_test(self) -> Dict[str, Any]:
        """Executa teste de circuit breaker"""
        logger.info("🔴 Executando teste de Circuit Breaker")
        
        test_file = os.path.join(self.resilience_dir, "resilience_circuit_breaker_test.py")
        
        if not os.path.exists(test_file):
            return {"error": f"Arquivo de teste não encontrado: {test_file}"}
        
        try:
            # Executar teste via subprocess
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=self.config.test_duration + 60  # +60s de margem
            )
            
            if result.returncode == 0:
                # Tentar carregar relatório gerado
                report_file = "circuit_breaker_load_test_report.json"
                if os.path.exists(report_file):
                    with open(report_file, 'r') as f:
                        report = json.load(f)
                    
                    # Mover relatório para diretório de reports
                    if self.config.generate_reports:
                        self._move_report_to_reports_dir(report_file, "circuit_breaker")
                    
                    return report
                else:
                    return {"error": "Relatório não gerado pelo teste"}
            else:
                return {
                    "error": f"Teste falhou com código {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Teste excedeu timeout"}
        except Exception as e:
            return {"error": f"Erro ao executar teste: {str(e)}"}
    
    async def _run_retry_logic_test(self) -> Dict[str, Any]:
        """Executa teste de retry logic"""
        logger.info("🔄 Executando teste de Retry Logic")
        
        test_file = os.path.join(self.resilience_dir, "resilience_retry_logic_test.py")
        
        if not os.path.exists(test_file):
            return {"error": f"Arquivo de teste não encontrado: {test_file}"}
        
        try:
            # Executar teste via subprocess
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=self.config.test_duration + 60
            )
            
            if result.returncode == 0:
                # Tentar carregar relatório gerado
                report_file = "retry_logic_load_test_report.json"
                if os.path.exists(report_file):
                    with open(report_file, 'r') as f:
                        report = json.load(f)
                    
                    # Mover relatório para diretório de reports
                    if self.config.generate_reports:
                        self._move_report_to_reports_dir(report_file, "retry_logic")
                    
                    return report
                else:
                    return {"error": "Relatório não gerado pelo teste"}
            else:
                return {
                    "error": f"Teste falhou com código {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Teste excedeu timeout"}
        except Exception as e:
            return {"error": f"Erro ao executar teste: {str(e)}"}
    
    async def _run_graceful_degradation_test(self) -> Dict[str, Any]:
        """Executa teste de graceful degradation"""
        logger.info("📉 Executando teste de Graceful Degradation")
        
        test_file = os.path.join(self.resilience_dir, "resilience_graceful_degradation_test.py")
        
        if not os.path.exists(test_file):
            return {"error": f"Arquivo de teste não encontrado: {test_file}"}
        
        try:
            # Executar teste via subprocess
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=self.config.test_duration + 60
            )
            
            if result.returncode == 0:
                # Tentar carregar relatório gerado
                report_file = "graceful_degradation_load_test_report.json"
                if os.path.exists(report_file):
                    with open(report_file, 'r') as f:
                        report = json.load(f)
                    
                    # Mover relatório para diretório de reports
                    if self.config.generate_reports:
                        self._move_report_to_reports_dir(report_file, "graceful_degradation")
                    
                    return report
                else:
                    return {"error": "Relatório não gerado pelo teste"}
            else:
                return {
                    "error": f"Teste falhou com código {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Teste excedeu timeout"}
        except Exception as e:
            return {"error": f"Erro ao executar teste: {str(e)}"}
    
    def _move_report_to_reports_dir(self, report_file: str, test_type: str):
        """Move relatório para diretório de reports"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{test_type}_load_test_report_{timestamp}.json"
            new_path = os.path.join(self.reports_dir, new_filename)
            
            os.rename(report_file, new_path)
            logger.info(f"📄 Relatório movido: {new_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao mover relatório: {e}")
    
    def _generate_consolidated_report(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório consolidado de todos os testes"""
        logger.info("📊 Gerando relatório consolidado")
        
        # Calcular métricas consolidadas
        total_requests = 0
        total_successful_requests = 0
        total_failed_requests = 0
        total_degraded_requests = 0
        total_response_times = []
        total_ux_scores = []
        
        successful_tests = 0
        failed_tests = 0
        
        for test_name, result in test_results.items():
            if "error" in result:
                failed_tests += 1
                continue
            
            successful_tests += 1
            
            # Extrair métricas do teste
            metrics = result.get("metrics", {})
            
            total_requests += metrics.get("total_requests", 0)
            total_successful_requests += metrics.get("successful_requests", 0)
            total_failed_requests += metrics.get("failed_requests", 0)
            total_degraded_requests += metrics.get("degraded_requests", 0)
            
            # Para simplificar, vamos usar médias dos tempos de resposta
            avg_response_time = metrics.get("avg_response_time", 0)
            if avg_response_time > 0:
                total_response_times.append(avg_response_time)
            
            # Para UX scores
            avg_ux_score = metrics.get("avg_user_experience_score", 0)
            if avg_ux_score > 0:
                total_ux_scores.append(avg_ux_score)
        
        # Calcular métricas consolidadas
        consolidated_metrics = {
            "total_requests": total_requests,
            "total_successful_requests": total_successful_requests,
            "total_failed_requests": total_failed_requests,
            "total_degraded_requests": total_degraded_requests,
            "overall_success_rate": total_successful_requests / total_requests if total_requests > 0 else 0,
            "overall_degradation_rate": total_degraded_requests / total_requests if total_requests > 0 else 0,
            "avg_response_time": sum(total_response_times) / len(total_response_times) if total_response_times else 0,
            "avg_ux_score": sum(total_ux_scores) / len(total_ux_scores) if total_ux_scores else 0,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "test_success_rate": successful_tests / (successful_tests + failed_tests) if (successful_tests + failed_tests) > 0 else 0
        }
        
        consolidated_report = {
            "test_info": {
                "name": "Consolidated Resilience Load Tests",
                "tracing_id": "run-resilience-load-tests-2025-01-27-001",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0,
                "config": {
                    "base_url": self.config.base_url,
                    "test_duration": self.config.test_duration,
                    "concurrent_users": self.config.concurrent_users,
                    "parallel_execution": self.config.parallel_execution
                }
            },
            "test_results": test_results,
            "consolidated_metrics": consolidated_metrics,
            "test_summary": {
                "total_tests": len(test_results),
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "test_success_rate": consolidated_metrics["test_success_rate"]
            }
        }
        
        return consolidated_report
    
    def _validate_thresholds(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Valida thresholds dos testes"""
        logger.info("✅ Validando thresholds")
        
        metrics = report.get("consolidated_metrics", {})
        validation_results = {
            "passed": True,
            "checks": {}
        }
        
        # Verificar success rate
        success_rate = metrics.get("overall_success_rate", 0)
        if success_rate < self.thresholds.min_success_rate:
            validation_results["checks"]["success_rate"] = {
                "passed": False,
                "expected": f">= {self.thresholds.min_success_rate:.1%}",
                "actual": f"{success_rate:.1%}",
                "message": "Taxa de sucesso abaixo do threshold"
            }
            validation_results["passed"] = False
        else:
            validation_results["checks"]["success_rate"] = {
                "passed": True,
                "expected": f">= {self.thresholds.min_success_rate:.1%}",
                "actual": f"{success_rate:.1%}"
            }
        
        # Verificar tempo de resposta médio
        avg_response_time = metrics.get("avg_response_time", 0)
        if avg_response_time > self.thresholds.max_avg_response_time:
            validation_results["checks"]["avg_response_time"] = {
                "passed": False,
                "expected": f"<= {self.thresholds.max_avg_response_time}s",
                "actual": f"{avg_response_time:.3f}s",
                "message": "Tempo de resposta médio acima do threshold"
            }
            validation_results["passed"] = False
        else:
            validation_results["checks"]["avg_response_time"] = {
                "passed": True,
                "expected": f"<= {self.thresholds.max_avg_response_time}s",
                "actual": f"{avg_response_time:.3f}s"
            }
        
        # Verificar taxa de degradação
        degradation_rate = metrics.get("overall_degradation_rate", 0)
        if degradation_rate > self.thresholds.max_degradation_rate:
            validation_results["checks"]["degradation_rate"] = {
                "passed": False,
                "expected": f"<= {self.thresholds.max_degradation_rate:.1%}",
                "actual": f"{degradation_rate:.1%}",
                "message": "Taxa de degradação acima do threshold"
            }
            validation_results["passed"] = False
        else:
            validation_results["checks"]["degradation_rate"] = {
                "passed": True,
                "expected": f"<= {self.thresholds.max_degradation_rate:.1%}",
                "actual": f"{degradation_rate:.1%}"
            }
        
        # Verificar score de UX
        ux_score = metrics.get("avg_ux_score", 0)
        if ux_score < self.thresholds.min_ux_score:
            validation_results["checks"]["ux_score"] = {
                "passed": False,
                "expected": f">= {self.thresholds.min_ux_score}",
                "actual": f"{ux_score:.2f}",
                "message": "Score de experiência do usuário abaixo do threshold"
            }
            validation_results["passed"] = False
        else:
            validation_results["checks"]["ux_score"] = {
                "passed": True,
                "expected": f">= {self.thresholds.min_ux_score}",
                "actual": f"{ux_score:.2f}"
            }
        
        return validation_results
    
    def _save_consolidated_report(self, report: Dict[str, Any]):
        """Salva relatório consolidado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"consolidated_resilience_load_test_report_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📄 Relatório consolidado salvo: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório consolidado: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executa testes de carga de resiliência")
    
    parser.add_argument("--base-url", default="http://localhost:8000", help="URL base da API")
    parser.add_argument("--duration", type=int, default=300, help="Duração dos testes em segundos")
    parser.add_argument("--users", type=int, default=50, help="Número de usuários concorrentes")
    parser.add_argument("--parallel", action="store_true", help="Executar testes em paralelo")
    parser.add_argument("--no-reports", action="store_true", help="Não gerar relatórios")
    parser.add_argument("--no-validation", action="store_true", help="Não validar thresholds")
    parser.add_argument("--circuit-breaker-only", action="store_true", help="Executar apenas teste de circuit breaker")
    parser.add_argument("--retry-logic-only", action="store_true", help="Executar apenas teste de retry logic")
    parser.add_argument("--graceful-degradation-only", action="store_true", help="Executar apenas teste de graceful degradation")
    
    args = parser.parse_args()
    
    # Configurar testes baseado nos argumentos
    config = ResilienceTestConfig(
        base_url=args.base_url,
        test_duration=args.duration,
        concurrent_users=args.users,
        parallel_execution=args.parallel,
        generate_reports=not args.no_reports,
        validate_thresholds=not args.no_validation
    )
    
    # Configurar quais testes executar
    if args.circuit_breaker_only:
        config.enable_retry_logic = False
        config.enable_graceful_degradation = False
    elif args.retry_logic_only:
        config.enable_circuit_breaker = False
        config.enable_graceful_degradation = False
    elif args.graceful_degradation_only:
        config.enable_circuit_breaker = False
        config.enable_retry_logic = False
    
    # Thresholds padrão
    thresholds = ResilienceTestThresholds()
    
    # Executar testes
    runner = ResilienceLoadTestRunner(config, thresholds)
    
    try:
        report = asyncio.run(runner.run_all_tests())
        
        # Exibir resumo
        print("\n" + "="*60)
        print("📊 RELATÓRIO CONSOLIDADO DE TESTES DE RESILIÊNCIA")
        print("="*60)
        
        metrics = report.get("consolidated_metrics", {})
        print(f"Total de Requests: {metrics.get('total_requests', 0)}")
        print(f"Taxa de Sucesso Geral: {metrics.get('overall_success_rate', 0):.1%}")
        print(f"Taxa de Degradação: {metrics.get('overall_degradation_rate', 0):.1%}")
        print(f"Tempo Médio de Resposta: {metrics.get('avg_response_time', 0):.3f}s")
        print(f"Score Médio de UX: {metrics.get('avg_ux_score', 0):.2f}")
        
        test_summary = report.get("test_summary", {})
        print(f"Testes Executados: {test_summary.get('total_tests', 0)}")
        print(f"Testes Bem-sucedidos: {test_summary.get('successful_tests', 0)}")
        print(f"Taxa de Sucesso dos Testes: {test_summary.get('test_success_rate', 0):.1%}")
        
        # Exibir validação
        validation = report.get("validation", {})
        if validation:
            print(f"\n✅ Validação de Thresholds: {'PASSOU' if validation.get('passed', False) else 'FALHOU'}")
            
            for check_name, check_result in validation.get("checks", {}).items():
                status = "✅" if check_result.get("passed", False) else "❌"
                print(f"  {status} {check_name}: {check_result.get('actual', 'N/A')} (esperado: {check_result.get('expected', 'N/A')})")
                if not check_result.get("passed", False):
                    print(f"    ⚠️ {check_result.get('message', '')}")
        
        print("="*60)
        
        # Retornar código de saída baseado na validação
        if validation and not validation.get("passed", True):
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 