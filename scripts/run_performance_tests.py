#!/usr/bin/env python3
"""
🚀 Script de Execução de Testes de Performance - Credenciais
🎯 Objetivo: Executar testes de performance para validação de credenciais
📅 Criado: 2024-12-27
🔄 Versão: 1.0.0

Tracing ID: PERFORMANCE_RUNNER_001
Ruleset: enterprise_control_layer.yaml
"""

import os
import sys
import subprocess
import time
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

class PerformanceTestRunner:
    """Executor de testes de performance para credenciais."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.results_dir = self.project_root / "performance_results"
        self.logs_dir = self.project_root / "logs"
        
        # Criar diretórios se não existirem
        self.results_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurações
        self.test_timeout = 300  # 5 minutos
        self.max_workers = 4
        self.performance_markers = [
            "performance",
            "load", 
            "benchmark",
            "stress"
        ]
    
    def setup_environment(self) -> bool:
        """Configura ambiente para testes de performance."""
        print("🔧 Configurando ambiente para testes de performance...")
        
        try:
            # Verificar se o ambiente virtual está ativo
            if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                print("⚠️  Ambiente virtual não detectado. Recomenda-se usar um venv.")
            
            # Verificar dependências
            required_packages = ["pytest", "psutil", "asyncio", "pytest-asyncio"]
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
                print("💡 Execute: pip install -r requirements.txt")
                return False
            
            # Verificar se o backend está rodando (opcional)
            try:
                import requests
                response = requests.get("http://localhost:5000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend detectado e funcionando")
                else:
                    print("⚠️  Backend não está respondendo corretamente")
            except Exception as e:
                print(f"⚠️  Backend não detectado: {e}")
                print("💡 Inicie o backend antes de executar os testes")
            
            print("✅ Ambiente configurado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar ambiente: {e}")
            return False
    
    def discover_performance_tests(self) -> List[str]:
        """Descobre todos os testes de performance."""
        print("🔍 Descobrindo testes de performance...")
        
        test_files = []
        
        # Procurar por arquivos de teste de performance
        for marker in self.performance_markers:
            pattern = f"*{marker}*.py"
            test_files.extend(self.tests_dir.rglob(pattern))
        
        # Remover duplicatas e ordenar
        test_files = sorted(list(set(test_files)))
        
        print(f"📁 Encontrados {len(test_files)} arquivos de teste:")
        for test_file in test_files:
            print(f"   - {test_file.relative_to(self.project_root)}")
        
        return [str(f) for f in test_files]
    
    def run_single_test(self, test_file: str, marker: str = None) -> Dict[str, Any]:
        """Executa um teste de performance específico."""
        print(f"\n🧪 Executando teste: {Path(test_file).name}")
        
        # Comando pytest
        cmd = [
            "python", "-m", "pytest",
            test_file,
            "-value",
            "--tb=short",
            f"--timeout={self.test_timeout}",
            "--durations=10",
            "--capture=no"
        ]
        
        if marker:
            cmd.extend(["-m", marker])
        
        # Adicionar relatório HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = self.results_dir / f"performance_report_{timestamp}.html"
        cmd.extend(["--html", str(html_report), "--self-contained-html"])
        
        # Adicionar relatório JSON
        json_report = self.results_dir / f"performance_metrics_{timestamp}.json"
        cmd.extend(["--json-report", "--json-report-file", str(json_report)])
        
        start_time = time.time()
        
        try:
            # Executar teste
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.test_timeout + 60  # Extra timeout para setup
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Analisar resultado
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            # Extrair métricas do output
            metrics = self.extract_metrics_from_output(output)
            
            return {
                "test_file": test_file,
                "success": success,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "output": output,
                "error": error,
                "metrics": metrics,
                "html_report": str(html_report) if html_report.exists() else None,
                "json_report": str(json_report) if json_report.exists() else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "test_file": test_file,
                "success": False,
                "execution_time": self.test_timeout + 60,
                "return_code": -1,
                "output": "",
                "error": "Teste excedeu o tempo limite",
                "metrics": {},
                "html_report": None,
                "json_report": None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "test_file": test_file,
                "success": False,
                "execution_time": 0,
                "return_code": -1,
                "output": "",
                "error": str(e),
                "metrics": {},
                "html_report": None,
                "json_report": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def extract_metrics_from_output(self, output: str) -> Dict[str, Any]:
        """Extrai métricas de performance do output do teste."""
        metrics = {}
        
        try:
            # Procurar por padrões de métricas no output
            lines = output.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Tempo de execução
                if "Tempo:" in line and "ms" in line:
                    try:
                        time_value = float(line.split("Tempo:")[1].split("ms")[0].strip())
                        metrics["execution_time_ms"] = time_value
                    except:
                        pass
                
                # Throughput
                if "Throughput:" in line and "RPS" in line:
                    try:
                        throughput = float(line.split("Throughput:")[1].split("RPS")[0].strip())
                        metrics["throughput_rps"] = throughput
                    except:
                        pass
                
                # Memória
                if "Memória:" in line and "MB" in line:
                    try:
                        memory = float(line.split("Memória:")[1].split("MB")[0].strip())
                        metrics["memory_mb"] = memory
                    except:
                        pass
                
                # CPU
                if "CPU:" in line and "%" in line:
                    try:
                        cpu = float(line.split("CPU:")[1].split("%")[0].strip())
                        metrics["cpu_percent"] = cpu
                    except:
                        pass
                
                # Requests por segundo
                if "requests_per_second" in line:
                    try:
                        rps = float(line.split(":")[1].strip())
                        metrics["requests_per_second"] = rps
                    except:
                        pass
                
                # Taxa de erro
                if "error_rate" in line:
                    try:
                        error_rate = float(line.split(":")[1].strip())
                        metrics["error_rate"] = error_rate
                    except:
                        pass
        
        except Exception as e:
            print(f"⚠️  Erro ao extrair métricas: {e}")
        
        return metrics
    
    def run_all_performance_tests(self, markers: List[str] = None) -> Dict[str, Any]:
        """Executa todos os testes de performance."""
        print("🚀 Iniciando execução de todos os testes de performance...")
        
        if not self.setup_environment():
            return {"success": False, "error": "Falha na configuração do ambiente"}
        
        test_files = self.discover_performance_tests()
        
        if not test_files:
            print("❌ Nenhum teste de performance encontrado")
            return {"success": False, "error": "Nenhum teste encontrado"}
        
        results = []
        successful_tests = 0
        total_tests = len(test_files)
        
        for test_file in test_files:
            result = self.run_single_test(test_file)
            results.append(result)
            
            if result["success"]:
                successful_tests += 1
                print(f"✅ {Path(test_file).name} - SUCESSO")
            else:
                print(f"❌ {Path(test_file).name} - FALHA")
        
        # Gerar relatório consolidado
        summary = self.generate_summary_report(results)
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"performance_summary_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 RELATÓRIO DE PERFORMANCE")
        print(f"   Testes executados: {total_tests}")
        print(f"   Testes bem-sucedidos: {successful_tests}")
        print(f"   Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
        print(f"   Relatório salvo em: {report_file}")
        
        return {
            "success": successful_tests == total_tests,
            "summary": summary,
            "results": results,
            "report_file": str(report_file)
        }
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera relatório resumido dos testes."""
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]
        
        # Calcular métricas agregadas
        execution_times = [r["execution_time"] for r in successful_results]
        throughput_values = []
        memory_values = []
        cpu_values = []
        
        for result in successful_results:
            metrics = result.get("metrics", {})
            if "throughput_rps" in metrics:
                throughput_values.append(metrics["throughput_rps"])
            if "memory_mb" in metrics:
                memory_values.append(metrics["memory_mb"])
            if "cpu_percent" in metrics:
                cpu_values.append(metrics["cpu_percent"])
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "success_rate": len(successful_results) / len(results) if results else 0,
            "avg_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "min_execution_time": min(execution_times) if execution_times else 0,
            "max_execution_time": max(execution_times) if execution_times else 0,
            "avg_throughput": sum(throughput_values) / len(throughput_values) if throughput_values else 0,
            "avg_memory_usage": sum(memory_values) / len(memory_values) if memory_values else 0,
            "avg_cpu_usage": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "failed_test_files": [Path(r["test_file"]).name for r in failed_results],
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def run_specific_marker(self, marker: str) -> Dict[str, Any]:
        """Executa testes com um marcador específico."""
        print(f"🎯 Executando testes com marcador: {marker}")
        
        if not self.setup_environment():
            return {"success": False, "error": "Falha na configuração do ambiente"}
        
        # Executar todos os testes com o marcador
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir),
            "-value",
            "-m", marker,
            f"--timeout={self.test_timeout}",
            "--durations=10",
            "--capture=no"
        ]
        
        # Adicionar relatórios
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = self.results_dir / f"performance_{marker}_{timestamp}.html"
        json_report = self.results_dir / f"performance_{marker}_{timestamp}.json"
        
        cmd.extend([
            "--html", str(html_report),
            "--self-contained-html",
            "--json-report",
            "--json-report-file", str(json_report)
        ])
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.test_timeout * 2
            )
            
            end_time = time.time()
            
            return {
                "success": result.returncode == 0,
                "marker": marker,
                "execution_time": end_time - start_time,
                "return_code": result.returncode,
                "output": result.stdout,
                "error": result.stderr,
                "html_report": str(html_report) if html_report.exists() else None,
                "json_report": str(json_report) if json_report.exists() else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "marker": marker,
                "execution_time": 0,
                "return_code": -1,
                "output": "",
                "error": str(e),
                "html_report": None,
                "json_report": None,
                "timestamp": datetime.now().isoformat()
            }


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Executor de testes de performance para credenciais")
    parser.add_argument("--marker", "-m", help="Marcador específico para executar (performance, load, benchmark, stress)")
    parser.add_argument("--test-file", "-f", help="Arquivo de teste específico para executar")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout em segundos (padrão: 300)")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Número de workers (padrão: 4)")
    parser.add_argument("--verbose", "-value", action="store_true", help="Modo verboso")
    
    args = parser.parse_args()
    
    runner = PerformanceTestRunner()
    runner.test_timeout = args.timeout
    runner.max_workers = args.workers
    
    print("🚀 EXECUTOR DE TESTES DE PERFORMANCE - CREDENCIAIS")
    print("=" * 60)
    
    if args.test_file:
        # Executar teste específico
        result = runner.run_single_test(args.test_file)
        if result["success"]:
            print("✅ Teste executado com sucesso")
        else:
            print("❌ Teste falhou")
            if args.verbose:
                print(f"Erro: {result['error']}")
    elif args.marker:
        # Executar testes com marcador específico
        result = runner.run_specific_marker(args.marker)
        if result["success"]:
            print("✅ Testes executados com sucesso")
        else:
            print("❌ Testes falharam")
            if args.verbose:
                print(f"Erro: {result['error']}")
    else:
        # Executar todos os testes de performance
        result = runner.run_all_performance_tests()
        if result["success"]:
            print("✅ Todos os testes executados com sucesso")
        else:
            print("❌ Alguns testes falharam")
    
    print("\n🎯 Execução concluída!")


if __name__ == "__main__":
    main() 