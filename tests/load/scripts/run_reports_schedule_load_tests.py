#!/usr/bin/env python3
"""
Script de Execução - Testes de Carga para Agendamento de Relatórios
Baseado em: /api/reports/schedule

Tracing ID: LOAD_TEST_REPORTS_SCHEDULE_SCRIPT_20250127_001
Data/Hora: 2025-01-27 20:00:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades:
- Execução de testes de agendamento de relatórios
- Validação de métricas de performance
- Geração de relatórios de teste
- Monitoramento de recursos
- Análise de resultados
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReportsScheduleLoadTestRunner:
    """
    Executor de testes de carga para agendamento de relatórios
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results_dir = Path("tests/load/results/reports_schedule")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações baseadas no código real
        self.test_scenarios = {
            "normal": {
                "users": 10,
                "spawn_rate": 2,
                "run_time": "5m",
                "description": "Teste normal de agendamento"
            },
            "stress": {
                "users": 50,
                "spawn_rate": 5,
                "run_time": "10m",
                "description": "Teste de stress de agendamento"
            },
            "peak": {
                "users": 100,
                "spawn_rate": 10,
                "run_time": "15m",
                "description": "Teste de pico de agendamento"
            },
            "endurance": {
                "users": 25,
                "spawn_rate": 2,
                "run_time": "30m",
                "description": "Teste de resistência de agendamento"
            },
            "spike": {
                "users": 200,
                "spawn_rate": 50,
                "run_time": "2m",
                "description": "Teste de spike de agendamento"
            }
        }
        
        # Métricas de validação baseadas no código real
        self.validation_metrics = {
            "response_time_p95": 2000,  # ms
            "response_time_p99": 5000,  # ms
            "error_rate": 0.05,  # 5%
            "throughput_min": 10,  # requests/sec
            "success_rate": 0.95  # 95%
        }

    def run_test_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Executa um cenário de teste específico
        """
        logger.info(f"🚀 Iniciando cenário: {scenario_name}")
        
        if scenario_name not in self.test_scenarios:
            raise ValueError(f"Cenário '{scenario_name}' não encontrado")
        
        scenario = self.test_scenarios[scenario_name]
        
        # Preparar comando Locust
        locustfile = "tests/load/high/analytics/locustfile_reports_schedule_v1.py"
        
        cmd = [
            "locust",
            "-f", locustfile,
            "--host", self.config["target_host"],
            "--users", str(scenario["users"]),
            "--spawn-rate", str(scenario["spawn_rate"]),
            "--run-time", scenario["run_time"],
            "--headless",
            "--html", str(self.results_dir / f"reports_schedule_{scenario_name}.html"),
            "--json", str(self.results_dir / f"reports_schedule_{scenario_name}.json"),
            "--csv", str(self.results_dir / f"reports_schedule_{scenario_name}"),
            "--loglevel", "INFO"
        ]
        
        # Adicionar variáveis de ambiente
        env = os.environ.copy()
        env.update({
            "LOAD_TEST_SCENARIO": scenario_name,
            "LOAD_TEST_TYPE": "reports_schedule",
            "LOAD_TEST_TIMESTAMP": datetime.now().isoformat(),
            "TARGET_HOST": self.config["target_host"]
        })
        
        logger.info(f"Executando comando: {' '.join(cmd)}")
        
        try:
            # Executar teste
            start_time = time.time()
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=int(scenario["run_time"].replace("m", "")) * 60 + 300  # +5min buffer
            )
            end_time = time.time()
            
            # Processar resultados
            test_result = {
                "scenario": scenario_name,
                "description": scenario["description"],
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            # Analisar resultados JSON se disponível
            json_file = self.results_dir / f"reports_schedule_{scenario_name}.json"
            if json_file.exists():
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                    test_result["metrics"] = self._extract_metrics(json_data)
                    test_result["validation"] = self._validate_metrics(test_result["metrics"])
            
            logger.info(f"✅ Cenário {scenario_name} concluído em {test_result['duration']:.2f}s")
            return test_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout no cenário {scenario_name}")
            return {
                "scenario": scenario_name,
                "success": False,
                "error": "Timeout expired",
                "duration": time.time() - start_time
            }
        except Exception as e:
            logger.error(f"❌ Erro no cenário {scenario_name}: {str(e)}")
            return {
                "scenario": scenario_name,
                "success": False,
                "error": str(e)
            }

    def _extract_metrics(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai métricas relevantes dos resultados JSON
        """
        try:
            # Métricas baseadas no código real de agendamento
            metrics = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "response_times": [],
                "error_rates": {},
                "throughput": 0,
                "schedule_operations": {
                    "create": 0,
                    "cancel": 0,
                    "modify": 0,
                    "list": 0,
                    "batch": 0,
                    "advanced": 0,
                    "error_scenarios": 0
                }
            }
            
            # Processar dados do Locust
            if "stats" in json_data:
                for stat in json_data["stats"]:
                    name = stat.get("name", "")
                    num_requests = stat.get("num_requests", 0)
                    num_failures = stat.get("num_failures", 0)
                    avg_response_time = stat.get("avg_response_time", 0)
                    
                    metrics["total_requests"] += num_requests
                    metrics["successful_requests"] += (num_requests - num_failures)
                    metrics["failed_requests"] += num_failures
                    
                    if avg_response_time > 0:
                        metrics["response_times"].append(avg_response_time)
                    
                    # Categorizar operações de agendamento
                    if "schedule_normal" in name:
                        metrics["schedule_operations"]["create"] += num_requests
                    elif "schedule_cancel" in name:
                        metrics["schedule_operations"]["cancel"] += num_requests
                    elif "schedule_modify" in name:
                        metrics["schedule_operations"]["modify"] += num_requests
                    elif "schedule_list" in name:
                        metrics["schedule_operations"]["list"] += num_requests
                    elif "schedule_batch" in name:
                        metrics["schedule_operations"]["batch"] += num_requests
                    elif "schedule_advanced" in name:
                        metrics["schedule_operations"]["advanced"] += num_requests
                    elif "error_scenario" in name:
                        metrics["schedule_operations"]["error_scenarios"] += num_requests
            
            # Calcular métricas derivadas
            if metrics["total_requests"] > 0:
                metrics["success_rate"] = metrics["successful_requests"] / metrics["total_requests"]
                metrics["error_rate"] = metrics["failed_requests"] / metrics["total_requests"]
                
                if metrics["response_times"]:
                    metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
                    metrics["max_response_time"] = max(metrics["response_times"])
                    metrics["min_response_time"] = min(metrics["response_times"])
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao extrair métricas: {str(e)}")
            return {}

    def _validate_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida métricas contra thresholds definidos
        """
        validation = {
            "passed": True,
            "checks": {},
            "recommendations": []
        }
        
        try:
            # Validar tempo de resposta P95
            if "avg_response_time" in metrics:
                if metrics["avg_response_time"] > self.validation_metrics["response_time_p95"]:
                    validation["checks"]["response_time_p95"] = {
                        "passed": False,
                        "expected": f"< {self.validation_metrics['response_time_p95']}ms",
                        "actual": f"{metrics['avg_response_time']:.2f}ms"
                    }
                    validation["passed"] = False
                    validation["recommendations"].append("Otimizar performance de agendamento")
                else:
                    validation["checks"]["response_time_p95"] = {
                        "passed": True,
                        "actual": f"{metrics['avg_response_time']:.2f}ms"
                    }
            
            # Validar taxa de erro
            if "error_rate" in metrics:
                if metrics["error_rate"] > self.validation_metrics["error_rate"]:
                    validation["checks"]["error_rate"] = {
                        "passed": False,
                        "expected": f"< {self.validation_metrics['error_rate']*100}%",
                        "actual": f"{metrics['error_rate']*100:.2f}%"
                    }
                    validation["passed"] = False
                    validation["recommendations"].append("Investigar causas de falhas")
                else:
                    validation["checks"]["error_rate"] = {
                        "passed": True,
                        "actual": f"{metrics['error_rate']*100:.2f}%"
                    }
            
            # Validar taxa de sucesso
            if "success_rate" in metrics:
                if metrics["success_rate"] < self.validation_metrics["success_rate"]:
                    validation["checks"]["success_rate"] = {
                        "passed": False,
                        "expected": f"> {self.validation_metrics['success_rate']*100}%",
                        "actual": f"{metrics['success_rate']*100:.2f}%"
                    }
                    validation["passed"] = False
                    validation["recommendations"].append("Melhorar confiabilidade do sistema")
                else:
                    validation["checks"]["success_rate"] = {
                        "passed": True,
                        "actual": f"{metrics['success_rate']*100:.2f}%"
                    }
            
            # Validar throughput mínimo
            if "total_requests" in metrics and "duration" in metrics:
                throughput = metrics["total_requests"] / metrics.get("duration", 1)
                if throughput < self.validation_metrics["throughput_min"]:
                    validation["checks"]["throughput"] = {
                        "passed": False,
                        "expected": f"> {self.validation_metrics['throughput_min']} req/s",
                        "actual": f"{throughput:.2f} req/s"
                    }
                    validation["passed"] = False
                    validation["recommendations"].append("Otimizar capacidade de processamento")
                else:
                    validation["checks"]["throughput"] = {
                        "passed": True,
                        "actual": f"{throughput:.2f} req/s"
                    }
            
            # Validar distribuição de operações
            if "schedule_operations" in metrics:
                ops = metrics["schedule_operations"]
                total_ops = sum(ops.values())
                if total_ops > 0:
                    for op_type, count in ops.items():
                        percentage = (count / total_ops) * 100
                        validation["checks"][f"operation_{op_type}"] = {
                            "passed": True,
                            "count": count,
                            "percentage": f"{percentage:.1f}%"
                        }
            
        except Exception as e:
            logger.error(f"Erro na validação de métricas: {str(e)}")
            validation["passed"] = False
            validation["error"] = str(e)
        
        return validation

    def run_all_scenarios(self) -> Dict[str, Any]:
        """
        Executa todos os cenários de teste
        """
        logger.info("🚀 Iniciando execução de todos os cenários de agendamento")
        
        results = {
            "test_suite": "reports_schedule_load_tests",
            "timestamp": datetime.now().isoformat(),
            "target_host": self.config["target_host"],
            "scenarios": {},
            "summary": {
                "total_scenarios": len(self.test_scenarios),
                "passed_scenarios": 0,
                "failed_scenarios": 0,
                "total_duration": 0
            }
        }
        
        for scenario_name in self.test_scenarios.keys():
            try:
                scenario_result = self.run_test_scenario(scenario_name)
                results["scenarios"][scenario_name] = scenario_result
                
                if scenario_result.get("success", False):
                    results["summary"]["passed_scenarios"] += 1
                else:
                    results["summary"]["failed_scenarios"] += 1
                
                results["summary"]["total_duration"] += scenario_result.get("duration", 0)
                
                # Aguardar entre cenários
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Erro no cenário {scenario_name}: {str(e)}")
                results["scenarios"][scenario_name] = {
                    "success": False,
                    "error": str(e)
                }
                results["summary"]["failed_scenarios"] += 1
        
        # Gerar relatório final
        self._generate_final_report(results)
        
        return results

    def _generate_final_report(self, results: Dict[str, Any]):
        """
        Gera relatório final dos testes
        """
        report_file = self.results_dir / f"reports_schedule_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"📊 Relatório final salvo em: {report_file}")
            
            # Log do resumo
            summary = results["summary"]
            logger.info(f"""
🎯 RESUMO DOS TESTES DE AGENDAMENTO DE RELATÓRIOS
================================================
Total de Cenários: {summary['total_scenarios']}
Cenários Aprovados: {summary['passed_scenarios']}
Cenários Reprovados: {summary['failed_scenarios']}
Duração Total: {summary['total_duration']:.2f}s
Taxa de Sucesso: {(summary['passed_scenarios']/summary['total_scenarios'])*100:.1f}%
            """)
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório final: {str(e)}")

def main():
    """
    Função principal do script
    """
    parser = argparse.ArgumentParser(description="Executor de testes de carga para agendamento de relatórios")
    parser.add_argument("--host", default="http://localhost:8000", help="Host alvo para testes")
    parser.add_argument("--scenario", help="Cenário específico para executar")
    parser.add_argument("--all", action="store_true", help="Executar todos os cenários")
    parser.add_argument("--config", help="Arquivo de configuração JSON")
    
    args = parser.parse_args()
    
    # Configuração padrão
    config = {
        "target_host": args.host,
        "timeout": 300,
        "retries": 3
    }
    
    # Carregar configuração customizada se fornecida
    if args.config:
        try:
            with open(args.config, 'r') as f:
                custom_config = json.load(f)
                config.update(custom_config)
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            sys.exit(1)
    
    # Criar executor
    runner = ReportsScheduleLoadTestRunner(config)
    
    try:
        if args.scenario:
            # Executar cenário específico
            logger.info(f"Executando cenário específico: {args.scenario}")
            result = runner.run_test_scenario(args.scenario)
            print(json.dumps(result, indent=2, default=str))
            
        elif args.all:
            # Executar todos os cenários
            logger.info("Executando todos os cenários")
            results = runner.run_all_scenarios()
            print(json.dumps(results, indent=2, default=str))
            
        else:
            # Executar cenário padrão (normal)
            logger.info("Executando cenário padrão: normal")
            result = runner.run_test_scenario("normal")
            print(json.dumps(result, indent=2, default=str))
            
    except KeyboardInterrupt:
        logger.info("Teste interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro na execução: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 