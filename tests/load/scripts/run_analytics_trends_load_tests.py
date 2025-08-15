#!/usr/bin/env python3
"""
Script de Execução - Testes de Carga Analytics Trends
Baseado em: locustfile_analytics_trends_v1.py

Tracing ID: RUN_ANALYTICS_TRENDS_20250127_001
Data/Hora: 2025-01-27 18:30:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades:
- Execução de testes de analytics trends
- Configuração de parâmetros
- Geração de relatórios
- Validação de thresholds
- Monitoramento de métricas
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configuração de paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests" / "load"
REPORTS_DIR = PROJECT_ROOT / "reports" / "load_tests"
LOGS_DIR = PROJECT_ROOT / "logs" / "load_tests"

# Criar diretórios se não existirem
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class AnalyticsTrendsLoadTestRunner:
    """
    Executor de testes de carga para Analytics Trends
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_id = f"analytics_trends_{self.timestamp}"
        
        # Configurações de teste
        self.base_url = config.get("base_url", "http://localhost:8000")
        self.locustfile = TESTS_DIR / "high" / "analytics" / "locustfile_analytics_trends_v1.py"
        self.report_file = REPORTS_DIR / f"analytics_trends_report_{self.timestamp}.json"
        self.log_file = LOGS_DIR / f"analytics_trends_{self.timestamp}.log"
        
        # Thresholds de qualidade
        self.thresholds = {
            "response_time_p95": 2000,  # ms
            "response_time_p99": 5000,  # ms
            "error_rate": 5.0,  # %
            "throughput_min": 10,  # req/s
            "success_rate": 95.0  # %
        }
        
        # Métricas coletadas
        self.metrics = {
            "test_id": self.test_id,
            "start_time": None,
            "end_time": None,
            "duration": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "error_rates": {},
            "throughput": 0,
            "thresholds_passed": True,
            "threshold_violations": []
        }

    def validate_environment(self) -> bool:
        """
        Valida o ambiente antes da execução
        """
        print("🔍 Validando ambiente...")
        
        # Verificar se o locustfile existe
        if not self.locustfile.exists():
            print(f"❌ Locustfile não encontrado: {self.locustfile}")
            return False
        
        # Verificar se o locust está instalado
        try:
            subprocess.run(["locust", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Locust não está instalado ou não está no PATH")
            return False
        
        # Verificar conectividade com o servidor
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print(f"⚠️ Servidor respondeu com status {response.status_code}")
        except Exception as e:
            print(f"⚠️ Não foi possível conectar ao servidor: {e}")
        
        print("✅ Ambiente validado")
        return True

    def run_load_test(self, scenario: str = "normal") -> bool:
        """
        Executa o teste de carga
        """
        print(f"🚀 Iniciando teste de carga - Cenário: {scenario}")
        
        # Configurações baseadas no cenário
        scenarios = {
            "normal": {
                "users": 10,
                "spawn_rate": 2,
                "run_time": "5m"
            },
            "stress": {
                "users": 50,
                "spawn_rate": 5,
                "run_time": "10m"
            },
            "peak": {
                "users": 100,
                "spawn_rate": 10,
                "run_time": "15m"
            },
            "endurance": {
                "users": 20,
                "spawn_rate": 2,
                "run_time": "30m"
            }
        }
        
        if scenario not in scenarios:
            print(f"❌ Cenário inválido: {scenario}")
            return False
        
        config = scenarios[scenario]
        
        # Comando do Locust
        cmd = [
            "locust",
            "-f", str(self.locustfile),
            "--host", self.base_url,
            "--users", str(config["users"]),
            "--spawn-rate", str(config["spawn_rate"]),
            "--run-time", config["run_time"],
            "--headless",
            "--json",
            "--html", str(REPORTS_DIR / f"analytics_trends_{scenario}_{self.timestamp}.html"),
            "--csv", str(REPORTS_DIR / f"analytics_trends_{scenario}_{self.timestamp}")
        ]
        
        # Executar teste
        self.metrics["start_time"] = datetime.now().isoformat()
        
        try:
            print(f"📊 Executando: {' '.join(cmd)}")
            
            with open(self.log_file, 'w') as log_file:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Monitorar execução
                while process.poll() is None:
                    time.sleep(1)
                
                stdout, stderr = process.communicate()
                
                # Log da execução
                log_file.write(f"=== ANALYTICS TRENDS LOAD TEST ===\n")
                log_file.write(f"Timestamp: {self.timestamp}\n")
                log_file.write(f"Scenario: {scenario}\n")
                log_file.write(f"Command: {' '.join(cmd)}\n\n")
                log_file.write(f"STDOUT:\n{stdout}\n\n")
                log_file.write(f"STDERR:\n{stderr}\n")
            
            self.metrics["end_time"] = datetime.now().isoformat()
            self.metrics["duration"] = (
                datetime.fromisoformat(self.metrics["end_time"]) - 
                datetime.fromisoformat(self.metrics["start_time"])
            ).total_seconds()
            
            # Processar resultados
            success = self.process_results(scenario)
            
            if success:
                print(f"✅ Teste de carga concluído - Cenário: {scenario}")
            else:
                print(f"❌ Teste de carga falhou - Cenário: {scenario}")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro na execução: {e}")
            self.metrics["end_time"] = datetime.now().isoformat()
            return False

    def process_results(self, scenario: str) -> bool:
        """
        Processa os resultados do teste
        """
        print("📈 Processando resultados...")
        
        # Ler arquivo CSV de resultados
        csv_file = REPORTS_DIR / f"analytics_trends_{scenario}_{self.timestamp}_stats.csv"
        
        if not csv_file.exists():
            print(f"⚠️ Arquivo de resultados não encontrado: {csv_file}")
            return False
        
        try:
            import pandas as pd
            
            # Ler dados do CSV
            df = pd.read_csv(csv_file)
            
            # Extrair métricas
            if not df.empty:
                # Métricas gerais
                self.metrics["total_requests"] = int(df["num_requests"].sum())
                self.metrics["successful_requests"] = int(df["num_failures"].sum())
                self.metrics["failed_requests"] = int(df["num_failures"].sum())
                
                # Response times
                self.metrics["response_times"] = {
                    "avg": float(df["avg_response_time"].mean()),
                    "median": float(df["median_response_time"].mean()),
                    "p95": float(df["response_time_p95"].mean()),
                    "p99": float(df["response_time_p99"].mean()),
                    "min": float(df["min_response_time"].min()),
                    "max": float(df["max_response_time"].max())
                }
                
                # Throughput
                self.metrics["throughput"] = float(df["requests_per_sec"].mean())
                
                # Error rates por endpoint
                error_rates = {}
                for _, row in df.iterrows():
                    endpoint = row["name"]
                    total_reqs = row["num_requests"]
                    failed_reqs = row["num_failures"]
                    if total_reqs > 0:
                        error_rate = (failed_reqs / total_reqs) * 100
                        error_rates[endpoint] = error_rate
                
                self.metrics["error_rates"] = error_rates
                
                # Calcular taxa de sucesso geral
                total_reqs = self.metrics["total_requests"]
                failed_reqs = self.metrics["failed_requests"]
                if total_reqs > 0:
                    self.metrics["success_rate"] = ((total_reqs - failed_reqs) / total_reqs) * 100
                
                # Validar thresholds
                self.validate_thresholds()
                
                print("✅ Resultados processados com sucesso")
                return True
            else:
                print("⚠️ Nenhum dado encontrado no arquivo de resultados")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao processar resultados: {e}")
            return False

    def validate_thresholds(self):
        """
        Valida os thresholds de qualidade
        """
        print("🎯 Validando thresholds...")
        
        violations = []
        
        # Response time P95
        p95 = self.metrics["response_times"]["p95"]
        if p95 > self.thresholds["response_time_p95"]:
            violations.append(f"P95 response time ({p95}ms) excedeu threshold ({self.thresholds['response_time_p95']}ms)")
        
        # Response time P99
        p99 = self.metrics["response_times"]["p99"]
        if p99 > self.thresholds["response_time_p99"]:
            violations.append(f"P99 response time ({p99}ms) excedeu threshold ({self.thresholds['response_time_p99']}ms)")
        
        # Error rate
        error_rate = 100 - self.metrics["success_rate"]
        if error_rate > self.thresholds["error_rate"]:
            violations.append(f"Error rate ({error_rate:.2f}%) excedeu threshold ({self.thresholds['error_rate']}%)")
        
        # Throughput
        throughput = self.metrics["throughput"]
        if throughput < self.thresholds["throughput_min"]:
            violations.append(f"Throughput ({throughput:.2f} req/s) abaixo do threshold ({self.thresholds['throughput_min']} req/s)")
        
        # Success rate
        success_rate = self.metrics["success_rate"]
        if success_rate < self.thresholds["success_rate"]:
            violations.append(f"Success rate ({success_rate:.2f}%) abaixo do threshold ({self.thresholds['success_rate']}%)")
        
        self.metrics["threshold_violations"] = violations
        self.metrics["thresholds_passed"] = len(violations) == 0
        
        if violations:
            print(f"❌ {len(violations)} violações de threshold encontradas:")
            for violation in violations:
                print(f"   - {violation}")
        else:
            print("✅ Todos os thresholds foram atendidos")

    def generate_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo do teste
        """
        print("📋 Gerando relatório...")
        
        report = {
            "test_info": {
                "test_id": self.test_id,
                "test_type": "analytics_trends_load_test",
                "timestamp": self.timestamp,
                "start_time": self.metrics["start_time"],
                "end_time": self.metrics["end_time"],
                "duration_seconds": self.metrics["duration"]
            },
            "configuration": {
                "base_url": self.base_url,
                "locustfile": str(self.locustfile),
                "thresholds": self.thresholds
            },
            "results": {
                "total_requests": self.metrics["total_requests"],
                "successful_requests": self.metrics["successful_requests"],
                "failed_requests": self.metrics["failed_requests"],
                "success_rate_percent": self.metrics["success_rate"],
                "throughput_req_per_sec": self.metrics["throughput"],
                "response_times_ms": self.metrics["response_times"],
                "error_rates_percent": self.metrics["error_rates"]
            },
            "quality_assessment": {
                "thresholds_passed": self.metrics["thresholds_passed"],
                "threshold_violations": self.metrics["threshold_violations"],
                "overall_status": "PASS" if self.metrics["thresholds_passed"] else "FAIL"
            },
            "recommendations": self.generate_recommendations()
        }
        
        # Salvar relatório
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Relatório salvo: {self.report_file}")
        return report

    def generate_recommendations(self) -> List[str]:
        """
        Gera recomendações baseadas nos resultados
        """
        recommendations = []
        
        # Análise de response time
        p95 = self.metrics["response_times"]["p95"]
        if p95 > 1000:
            recommendations.append("Considerar otimização de performance para reduzir response times")
        
        # Análise de error rate
        error_rate = 100 - self.metrics["success_rate"]
        if error_rate > 2:
            recommendations.append("Investigar causas dos erros e implementar melhorias de resiliência")
        
        # Análise de throughput
        throughput = self.metrics["throughput"]
        if throughput < 20:
            recommendations.append("Considerar escalabilidade horizontal para aumentar throughput")
        
        # Análise de violações de threshold
        if self.metrics["threshold_violations"]:
            recommendations.append("Revisar e ajustar thresholds ou otimizar performance do sistema")
        
        if not recommendations:
            recommendations.append("Performance está dentro dos parâmetros esperados")
        
        return recommendations

    def run_full_test_suite(self) -> bool:
        """
        Executa suite completa de testes
        """
        print("🎯 Executando suite completa de testes de Analytics Trends")
        
        scenarios = ["normal", "stress", "peak", "endurance"]
        results = {}
        
        for scenario in scenarios:
            print(f"\n{'='*50}")
            print(f"Executando cenário: {scenario.upper()}")
            print(f"{'='*50}")
            
            success = self.run_load_test(scenario)
            results[scenario] = success
            
            if success:
                report = self.generate_report()
                print(f"📊 Relatório do cenário {scenario}:")
                print(f"   - Status: {report['quality_assessment']['overall_status']}")
                print(f"   - Requests: {report['results']['total_requests']}")
                print(f"   - Success Rate: {report['results']['success_rate_percent']:.2f}%")
                print(f"   - Throughput: {report['results']['throughput_req_per_sec']:.2f} req/s")
                print(f"   - P95 Response Time: {report['results']['response_times_ms']['p95']:.2f}ms")
            else:
                print(f"❌ Cenário {scenario} falhou")
            
            # Pausa entre cenários
            if scenario != scenarios[-1]:
                print("⏳ Aguardando 30 segundos antes do próximo cenário...")
                time.sleep(30)
        
        # Resumo final
        print(f"\n{'='*50}")
        print("RESUMO FINAL")
        print(f"{'='*50}")
        
        passed_scenarios = sum(1 for success in results.values() if success)
        total_scenarios = len(scenarios)
        
        print(f"Cenários executados: {total_scenarios}")
        print(f"Cenários aprovados: {passed_scenarios}")
        print(f"Taxa de sucesso: {(passed_scenarios/total_scenarios)*100:.1f}%")
        
        return passed_scenarios == total_scenarios

def main():
    """
    Função principal
    """
    parser = argparse.ArgumentParser(description="Executor de testes de carga para Analytics Trends")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="URL base do servidor")
    parser.add_argument("--scenario", choices=["normal", "stress", "peak", "endurance", "all"],
                       default="normal", help="Cenário de teste")
    parser.add_argument("--thresholds", type=str, 
                       help="Arquivo JSON com thresholds customizados")
    parser.add_argument("--output-dir", type=str,
                       help="Diretório de saída para relatórios")
    
    args = parser.parse_args()
    
    # Configuração
    config = {
        "base_url": args.base_url,
        "scenario": args.scenario
    }
    
    # Carregar thresholds customizados se fornecido
    if args.thresholds:
        try:
            with open(args.thresholds, 'r') as f:
                custom_thresholds = json.load(f)
                config["thresholds"] = custom_thresholds
        except Exception as e:
            print(f"⚠️ Erro ao carregar thresholds customizados: {e}")
    
    # Configurar diretório de saída
    if args.output_dir:
        global REPORTS_DIR, LOGS_DIR
        REPORTS_DIR = Path(args.output_dir) / "reports"
        LOGS_DIR = Path(args.output_dir) / "logs"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Executar testes
    runner = AnalyticsTrendsLoadTestRunner(config)
    
    if not runner.validate_environment():
        print("❌ Validação do ambiente falhou")
        sys.exit(1)
    
    if args.scenario == "all":
        success = runner.run_full_test_suite()
    else:
        success = runner.run_load_test(args.scenario)
        if success:
            runner.generate_report()
    
    if success:
        print("✅ Todos os testes executados com sucesso")
        sys.exit(0)
    else:
        print("❌ Alguns testes falharam")
        sys.exit(1)

if __name__ == "__main__":
    main() 