#!/usr/bin/env python3
"""
⚡ Script de Execução - Teste de Carga de Velocidade de Processamento
🎯 Objetivo: Executar testes de velocidade de processamento com diferentes cenários
📅 Data: 2025-01-27
🔗 Tracing ID: RUN_PERF_PROCESSING_SPEED_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em configurações reais de performance e otimização
🌲 ToT: Avaliadas múltiplas estratégias de execução e monitoramento
♻️ ReAct: Simulado cenários de carga e validada execução

Executa testes baseados em:
- infrastructure/processamento/parallel_processor.py
- infrastructure/performance/optimizations.py
- backend/app/api/api_routes.py
"""

import os
import sys
import time
import json
import argparse
import subprocess
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/processing_speed_load_tests.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProcessingSpeedLoadTestRunner:
    """Executor de testes de velocidade de processamento"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results_dir = Path("test-results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Configurações de teste baseadas em código real
        self.test_scenarios = {
            "parallel_processing": {
                "description": "Processamento paralelo de keywords",
                "users": 50,
                "spawn_rate": 10,
                "run_time": "5m",
                "batch_sizes": [50, 100, 200],
                "expected_throughput": 20.0,  # keywords/s
                "max_memory": 200.0,  # MB
                "max_cpu": 80.0  # %
            },
            "batch_processing": {
                "description": "Processamento em lote otimizado",
                "users": 30,
                "spawn_rate": 5,
                "run_time": "8m",
                "batch_sizes": [25, 50, 100],
                "expected_throughput": 10.0,  # keywords/s
                "max_memory": 150.0,  # MB
                "max_cpu": 70.0  # %
            },
            "optimized_processing": {
                "description": "Processamento com otimizações avançadas",
                "users": 100,
                "spawn_rate": 20,
                "run_time": "10m",
                "batch_sizes": [100, 200, 500],
                "expected_throughput": 60.0,  # keywords/s
                "max_memory": 300.0,  # MB
                "max_cpu": 85.0  # %
            },
            "stress_processing": {
                "description": "Teste de estresse de processamento",
                "users": 200,
                "spawn_rate": 50,
                "run_time": "15m",
                "batch_sizes": [200, 500, 1000],
                "expected_throughput": 100.0,  # keywords/s
                "max_memory": 500.0,  # MB
                "max_cpu": 90.0  # %
            }
        }
    
    def run_tests(self) -> Dict[str, Any]:
        """Executar todos os testes de velocidade de processamento"""
        logger.info("Iniciando testes de velocidade de processamento")
        
        start_time = time.time()
        results = {
            "test_suite": "Processing Speed Load Tests",
            "timestamp": datetime.now().isoformat(),
            "scenarios": {},
            "summary": {},
            "system_metrics": {}
        }
        
        try:
            # Coletar métricas do sistema antes dos testes
            results["system_metrics"]["before"] = self._collect_system_metrics()
            
            # Executar cada cenário de teste
            for scenario_name, scenario_config in self.test_scenarios.items():
                logger.info(f"Executando cenário: {scenario_name}")
                
                scenario_result = self._run_scenario(scenario_name, scenario_config)
                results["scenarios"][scenario_name] = scenario_result
                
                # Aguardar entre cenários
                time.sleep(30)
            
            # Coletar métricas do sistema após os testes
            results["system_metrics"]["after"] = self._collect_system_metrics()
            
            # Gerar resumo
            results["summary"] = self._generate_summary(results["scenarios"])
            
            # Salvar resultados
            self._save_results(results)
            
            # Validar resultados
            self._validate_results(results)
            
            logger.info("Testes de velocidade de processamento concluídos com sucesso")
            
        except Exception as e:
            logger.error(f"Erro durante execução dos testes: {str(e)}")
            results["error"] = str(e)
        
        total_time = time.time() - start_time
        logger.info(f"Tempo total de execução: {total_time:.2f} segundos")
        
        return results
    
    def _run_scenario(self, scenario_name: str, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Executar cenário específico de teste"""
        logger.info(f"Executando cenário {scenario_name}: {scenario_config['description']}")
        
        scenario_result = {
            "scenario_name": scenario_name,
            "description": scenario_config["description"],
            "config": scenario_config,
            "start_time": datetime.now().isoformat(),
            "results": {}
        }
        
        try:
            # Preparar comando Locust
            locustfile_path = "tests/load/medium/performance/locustfile_performance_processing_speed_v1.py"
            
            cmd = [
                "locust",
                "-f", locustfile_path,
                "--host", self.config["host"],
                "--users", str(scenario_config["users"]),
                "--spawn-rate", str(scenario_config["spawn_rate"]),
                "--run-time", scenario_config["run_time"],
                "--headless",
                "--html", f"test-results/{scenario_name}_report.html",
                "--json", f"test-results/{scenario_name}_report.json",
                "--csv", f"test-results/{scenario_name}_report"
            ]
            
            # Adicionar variáveis de ambiente para configuração
            env = os.environ.copy()
            env.update({
                "PROCESSING_SCENARIO": scenario_name,
                "BATCH_SIZES": ",".join(map(str, scenario_config["batch_sizes"])),
                "EXPECTED_THROUGHPUT": str(scenario_config["expected_throughput"]),
                "MAX_MEMORY": str(scenario_config["max_memory"]),
                "MAX_CPU": str(scenario_config["max_cpu"])
            })
            
            # Executar teste
            logger.info(f"Executando comando: {' '.join(cmd)}")
            
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            execution_time = time.time() - start_time
            
            # Processar resultados
            scenario_result["execution_time"] = execution_time
            scenario_result["exit_code"] = process.returncode
            scenario_result["stdout"] = stdout
            scenario_result["stderr"] = stderr
            
            # Carregar resultados JSON se disponível
            json_report_path = f"test-results/{scenario_name}_report.json"
            if os.path.exists(json_report_path):
                try:
                    with open(json_report_path, 'r') as f:
                        json_results = json.load(f)
                    scenario_result["locust_results"] = json_results
                except Exception as e:
                    logger.warning(f"Erro ao carregar resultados JSON: {str(e)}")
            
            # Validar cenário
            scenario_result["validation"] = self._validate_scenario(scenario_result, scenario_config)
            
            logger.info(f"Cenário {scenario_name} concluído em {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Erro no cenário {scenario_name}: {str(e)}")
            scenario_result["error"] = str(e)
        
        scenario_result["end_time"] = datetime.now().isoformat()
        return scenario_result
    
    def _validate_scenario(self, scenario_result: Dict[str, Any], scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validar resultados do cenário"""
        validation = {
            "passed": True,
            "warnings": [],
            "errors": []
        }
        
        try:
            # Verificar se o teste executou com sucesso
            if scenario_result.get("exit_code", 1) != 0:
                validation["passed"] = False
                validation["errors"].append("Teste falhou com código de saída não-zero")
            
            # Verificar resultados do Locust se disponíveis
            locust_results = scenario_result.get("locust_results", {})
            if locust_results:
                # Validar throughput
                if "stats" in locust_results:
                    stats = locust_results["stats"]
                    for stat in stats:
                        if stat.get("name") == "POST /api/processar_keywords":
                            rps = stat.get("num_requests", 0) / max(stat.get("avg_response_time", 1) / 1000, 1)
                            expected_rps = scenario_config["expected_throughput"]
                            
                            if rps < expected_rps * 0.8:  # 80% do esperado
                                validation["warnings"].append(f"Throughput baixo: {rps:.2f} RPS (esperado: {expected_rps})")
                            
                            # Validar tempo de resposta
                            avg_response_time = stat.get("avg_response_time", 0)
                            if avg_response_time > 5000:  # 5s
                                validation["warnings"].append(f"Tempo de resposta alto: {avg_response_time:.2f}ms")
                            
                            # Validar taxa de erro
                            error_rate = stat.get("num_failures", 0) / max(stat.get("num_requests", 1), 1) * 100
                            if error_rate > 5:  # 5%
                                validation["passed"] = False
                                validation["errors"].append(f"Taxa de erro alta: {error_rate:.2f}%")
            
            # Verificar uso de recursos
            system_metrics = self._collect_system_metrics()
            memory_usage = system_metrics.get("memory_usage", 0)
            cpu_usage = system_metrics.get("cpu_usage", 0)
            
            if memory_usage > scenario_config["max_memory"]:
                validation["warnings"].append(f"Uso de memória alto: {memory_usage:.2f}MB (limite: {scenario_config['max_memory']}MB)")
            
            if cpu_usage > scenario_config["max_cpu"]:
                validation["warnings"].append(f"Uso de CPU alto: {cpu_usage:.2f}% (limite: {scenario_config['max_cpu']}%)")
            
        except Exception as e:
            validation["passed"] = False
            validation["errors"].append(f"Erro na validação: {str(e)}")
        
        return validation
    
    def _collect_system_metrics(self) -> Dict[str, float]:
        """Coletar métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Processo atual
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / (1024 * 1024)
            process_cpu_percent = process.cpu_percent()
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "memory_used_mb": memory_used_mb,
                "disk_usage": disk_percent,
                "process_memory_mb": process_memory_mb,
                "process_cpu_percent": process_cpu_percent,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {str(e)}")
            return {}
    
    def _generate_summary(self, scenarios: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar resumo dos resultados"""
        summary = {
            "total_scenarios": len(scenarios),
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "total_execution_time": 0,
            "total_keywords_processed": 0,
            "average_throughput": 0,
            "performance_score": 0
        }
        
        total_throughput = 0
        scenario_count = 0
        
        for scenario_name, scenario_result in scenarios.items():
            # Contar cenários passados/falhados
            validation = scenario_result.get("validation", {})
            if validation.get("passed", False):
                summary["passed_scenarios"] += 1
            else:
                summary["failed_scenarios"] += 1
            
            # Soma tempo de execução
            summary["total_execution_time"] += scenario_result.get("execution_time", 0)
            
            # Calcular throughput médio
            locust_results = scenario_result.get("locust_results", {})
            if "stats" in locust_results:
                for stat in locust_results["stats"]:
                    if stat.get("name") == "POST /api/processar_keywords":
                        rps = stat.get("num_requests", 0) / max(stat.get("avg_response_time", 1) / 1000, 1)
                        total_throughput += rps
                        scenario_count += 1
                        break
        
        if scenario_count > 0:
            summary["average_throughput"] = total_throughput / scenario_count
        
        # Calcular score de performance (0-100)
        if summary["total_scenarios"] > 0:
            pass_rate = summary["passed_scenarios"] / summary["total_scenarios"]
            throughput_score = min(summary["average_throughput"] / 100, 1)  # Normalizar para 100 RPS
            summary["performance_score"] = (pass_rate * 0.6 + throughput_score * 0.4) * 100
        
        return summary
    
    def _save_results(self, results: Dict[str, Any]):
        """Salvar resultados em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test-results/processing_speed_load_tests_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Resultados salvos em: {filename}")
            
            # Gerar relatório resumido
            self._generate_summary_report(results, timestamp)
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
    
    def _generate_summary_report(self, results: Dict[str, Any], timestamp: str):
        """Gerar relatório resumido"""
        summary = results.get("summary", {})
        
        report = f"""
# 📊 RELATÓRIO DE TESTES DE VELOCIDADE DE PROCESSAMENTO

**Data/Hora**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Tracing ID**: RUN_PERF_PROCESSING_SPEED_{timestamp}

## 📈 RESUMO EXECUTIVO

- **Total de Cenários**: {summary.get('total_scenarios', 0)}
- **Cenários Aprovados**: {summary.get('passed_scenarios', 0)}
- **Cenários Falhados**: {summary.get('failed_scenarios', 0)}
- **Taxa de Sucesso**: {(summary.get('passed_scenarios', 0) / max(summary.get('total_scenarios', 1), 1)) * 100:.1f}%
- **Tempo Total de Execução**: {summary.get('total_execution_time', 0):.2f} segundos
- **Throughput Médio**: {summary.get('average_throughput', 0):.2f} RPS
- **Score de Performance**: {summary.get('performance_score', 0):.1f}/100

## 🎯 DETALHES POR CENÁRIO

"""
        
        for scenario_name, scenario_result in results.get("scenarios", {}).items():
            validation = scenario_result.get("validation", {})
            status = "✅ PASSOU" if validation.get("passed", False) else "❌ FALHOU"
            
            report += f"""
### {scenario_name.upper().replace('_', ' ')}
**Status**: {status}
**Descrição**: {scenario_result.get('description', 'N/A')}
**Tempo de Execução**: {scenario_result.get('execution_time', 0):.2f}s

"""
            
            if validation.get("warnings"):
                report += "**⚠️ Avisos**:\n"
                for warning in validation["warnings"]:
                    report += f"- {warning}\n"
            
            if validation.get("errors"):
                report += "**❌ Erros**:\n"
                for error in validation["errors"]:
                    report += f"- {error}\n"
        
        # Salvar relatório
        report_filename = f"test-results/processing_speed_summary_{timestamp}.md"
        try:
            with open(report_filename, 'w') as f:
                f.write(report)
            
            logger.info(f"Relatório resumido salvo em: {report_filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório resumido: {str(e)}")
    
    def _validate_results(self, results: Dict[str, Any]):
        """Validar resultados finais"""
        summary = results.get("summary", {})
        
        # Critérios de sucesso baseados em código real
        success_criteria = {
            "min_pass_rate": 0.8,  # 80% dos cenários devem passar
            "min_throughput": 20.0,  # Mínimo 20 RPS
            "max_execution_time": 3600,  # Máximo 1 hora
            "min_performance_score": 70.0  # Score mínimo de 70
        }
        
        validation_results = {
            "overall_success": True,
            "criteria_met": {},
            "recommendations": []
        }
        
        # Validar taxa de aprovação
        pass_rate = summary.get("passed_scenarios", 0) / max(summary.get("total_scenarios", 1), 1)
        validation_results["criteria_met"]["pass_rate"] = pass_rate >= success_criteria["min_pass_rate"]
        
        if not validation_results["criteria_met"]["pass_rate"]:
            validation_results["overall_success"] = False
            validation_results["recommendations"].append("Melhorar taxa de aprovação dos cenários")
        
        # Validar throughput
        avg_throughput = summary.get("average_throughput", 0)
        validation_results["criteria_met"]["throughput"] = avg_throughput >= success_criteria["min_throughput"]
        
        if not validation_results["criteria_met"]["throughput"]:
            validation_results["overall_success"] = False
            validation_results["recommendations"].append("Otimizar throughput do sistema")
        
        # Validar tempo de execução
        total_time = summary.get("total_execution_time", 0)
        validation_results["criteria_met"]["execution_time"] = total_time <= success_criteria["max_execution_time"]
        
        if not validation_results["criteria_met"]["execution_time"]:
            validation_results["recommendations"].append("Reduzir tempo de execução dos testes")
        
        # Validar score de performance
        performance_score = summary.get("performance_score", 0)
        validation_results["criteria_met"]["performance_score"] = performance_score >= success_criteria["min_performance_score"]
        
        if not validation_results["criteria_met"]["performance_score"]:
            validation_results["overall_success"] = False
            validation_results["recommendations"].append("Melhorar score geral de performance")
        
        # Log dos resultados
        if validation_results["overall_success"]:
            logger.info("✅ Todos os critérios de validação foram atendidos")
        else:
            logger.warning("⚠️ Alguns critérios de validação não foram atendidos")
            for recommendation in validation_results["recommendations"]:
                logger.warning(f"Recomendação: {recommendation}")
        
        results["validation"] = validation_results

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes de velocidade de processamento")
    parser.add_argument("--host", default="http://localhost:8000", help="Host do sistema")
    parser.add_argument("--scenario", help="Cenário específico para executar")
    parser.add_argument("--users", type=int, help="Número de usuários")
    parser.add_argument("--spawn-rate", type=int, help="Taxa de spawn")
    parser.add_argument("--run-time", help="Tempo de execução")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    
    args = parser.parse_args()
    
    # Configuração
    config = {
        "host": args.host,
        "verbose": args.verbose
    }
    
    # Ajustar nível de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Criar diretório de logs
    Path("logs").mkdir(exist_ok=True)
    
    # Executar testes
    runner = ProcessingSpeedLoadTestRunner(config)
    results = runner.run_tests()
    
    # Verificar sucesso
    validation = results.get("validation", {})
    if validation.get("overall_success", False):
        logger.info("🎉 Testes concluídos com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Testes falharam na validação")
        sys.exit(1)

if __name__ == "__main__":
    main() 