#!/usr/bin/env python3
"""
Script de Execução - Testes de Carga Geração de Relatórios
Baseado em: locustfile_reports_generate_v1.py

Tracing ID: RUN_REPORTS_GENERATE_20250127_001
Data/Hora: 2025-01-27 19:00:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades:
- Execução de testes de geração de relatórios
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

# Configurações padrão
DEFAULT_CONFIG = {
    "base_url": "http://localhost:8000",
    "users": 50,
    "spawn_rate": 10,
    "run_time": "10m",
    "host": "http://localhost:8000",
    "locustfile": "tests/load/high/analytics/locustfile_reports_generate_v1.py",
    "html_report": "reports/load_tests/reports_generate_report.html",
    "json_report": "reports/load_tests/reports_generate_report.json",
    "csv_report": "reports/load_tests/reports_generate_report.csv",
    "log_file": "logs/load_tests/reports_generate_test.log"
}

# Thresholds de qualidade
QUALITY_THRESHOLDS = {
    "response_time_p95": 5000,  # 5 segundos
    "response_time_p99": 10000,  # 10 segundos
    "error_rate": 0.05,  # 5%
    "requests_per_second": 10,
    "success_rate": 0.95  # 95%
}

class ReportsGenerateLoadTestRunner:
    """
    Executor de testes de carga para geração de relatórios
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = {**DEFAULT_CONFIG, **config}
        self.tracing_id = f"RUN_REPORTS_GENERATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = None
        self.end_time = None
        self.results = {}
        
        # Criar diretórios necessários
        self._create_directories()
        
        print(f"🚀 [REPORTS_GENERATE] Iniciando executor de testes")
        print(f"📋 Tracing ID: {self.tracing_id}")
        print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Configuração: {json.dumps(self.config, indent=2)}")
    
    def _create_directories(self):
        """Criar diretórios necessários"""
        directories = [
            REPORTS_DIR,
            LOGS_DIR,
            REPORTS_DIR / "reports_generate",
            LOGS_DIR / "reports_generate"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def run_test(self, test_type: str = "normal") -> Dict[str, Any]:
        """
        Executar teste de carga específico
        
        Args:
            test_type: Tipo de teste (normal, complex, batch, scheduled, stress)
            
        Returns:
            Resultados do teste
        """
        print(f"\n📊 [REPORTS_GENERATE] Executando teste: {test_type}")
        
        # Configurar parâmetros específicos do teste
        test_config = self._get_test_config(test_type)
        
        # Construir comando Locust
        cmd = self._build_locust_command(test_config)
        
        # Executar teste
        self.start_time = datetime.now()
        result = self._execute_locust_test(cmd, test_type)
        self.end_time = datetime.now()
        
        # Processar resultados
        processed_result = self._process_results(result, test_type)
        
        # Validar thresholds
        validation_result = self._validate_thresholds(processed_result, test_type)
        
        # Salvar resultados
        self._save_results(processed_result, test_type)
        
        # Gerar relatório
        self._generate_report(processed_result, test_type)
        
        return {
            "test_type": test_type,
            "success": validation_result["passed"],
            "results": processed_result,
            "validation": validation_result,
            "duration": (self.end_time - self.start_time).total_seconds()
        }
    
    def _get_test_config(self, test_type: str) -> Dict[str, Any]:
        """Obter configuração específica do teste"""
        base_config = self.config.copy()
        
        if test_type == "normal":
            base_config.update({
                "users": 30,
                "spawn_rate": 5,
                "run_time": "5m"
            })
        elif test_type == "complex":
            base_config.update({
                "users": 20,
                "spawn_rate": 3,
                "run_time": "8m"
            })
        elif test_type == "batch":
            base_config.update({
                "users": 15,
                "spawn_rate": 2,
                "run_time": "6m"
            })
        elif test_type == "scheduled":
            base_config.update({
                "users": 10,
                "spawn_rate": 2,
                "run_time": "4m"
            })
        elif test_type == "stress":
            base_config.update({
                "users": 50,
                "spawn_rate": 10,
                "run_time": "15m"
            })
        
        return base_config
    
    def _build_locust_command(self, config: Dict[str, Any]) -> List[str]:
        """Construir comando Locust"""
        cmd = [
            "locust",
            "--locustfile", config["locustfile"],
            "--host", config["host"],
            "--users", str(config["users"]),
            "--spawn-rate", str(config["spawn_rate"]),
            "--run-time", config["run_time"],
            "--headless",
            "--html", config["html_report"],
            "--json", config["json_report"],
            "--csv", config["csv_report"],
            "--logfile", config["log_file"],
            "--loglevel", "INFO"
        ]
        
        return cmd
    
    def _execute_locust_test(self, cmd: List[str], test_type: str) -> Dict[str, Any]:
        """Executar teste Locust"""
        print(f"🔧 [REPORTS_GENERATE] Comando: {' '.join(cmd)}")
        
        try:
            # Executar comando
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=PROJECT_ROOT
            )
            
            stdout, stderr = process.communicate()
            
            # Verificar se executou com sucesso
            if process.returncode != 0:
                print(f"❌ [REPORTS_GENERATE] Erro na execução: {stderr}")
                return {
                    "success": False,
                    "error": stderr,
                    "stdout": stdout,
                    "return_code": process.returncode
                }
            
            print(f"✅ [REPORTS_GENERATE] Teste executado com sucesso")
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": process.returncode
            }
            
        except Exception as e:
            print(f"❌ [REPORTS_GENERATE] Exceção na execução: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "exception": True
            }
    
    def _process_results(self, result: Dict[str, Any], test_type: str) -> Dict[str, Any]:
        """Processar resultados do teste"""
        if not result["success"]:
            return {
                "test_type": test_type,
                "success": False,
                "error": result.get("error", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }
        
        # Ler relatório JSON
        json_report_path = self.config["json_report"]
        if os.path.exists(json_report_path):
            try:
                with open(json_report_path, 'r') as f:
                    report_data = json.load(f)
                
                # Extrair métricas principais
                metrics = {
                    "test_type": test_type,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "total_requests": report_data.get("total_requests", 0),
                    "total_failures": report_data.get("total_failures", 0),
                    "total_median_response_time": report_data.get("total_median_response_time", 0),
                    "total_avg_response_time": report_data.get("total_avg_response_time", 0),
                    "total_min_response_time": report_data.get("total_min_response_time", 0),
                    "total_max_response_time": report_data.get("total_max_response_time", 0),
                    "total_rps": report_data.get("total_rps", 0),
                    "total_fail_per_sec": report_data.get("total_fail_per_sec", 0),
                    "response_time_percentiles": report_data.get("response_time_percentiles", {}),
                    "num_requests": report_data.get("num_requests", {}),
                    "num_failures": report_data.get("num_failures", {}),
                    "median_response_time": report_data.get("median_response_time", {}),
                    "avg_response_time": report_data.get("avg_response_time", {}),
                    "min_response_time": report_data.get("min_response_time", {}),
                    "max_response_time": report_data.get("max_response_time", {}),
                    "current_rps": report_data.get("current_rps", {}),
                    "current_fail_per_sec": report_data.get("current_fail_per_sec", {})
                }
                
                # Calcular métricas derivadas
                metrics["error_rate"] = (
                    metrics["total_failures"] / metrics["total_requests"]
                    if metrics["total_requests"] > 0 else 0
                )
                metrics["success_rate"] = 1 - metrics["error_rate"]
                
                return metrics
                
            except Exception as e:
                print(f"❌ [REPORTS_GENERATE] Erro ao processar relatório: {str(e)}")
                return {
                    "test_type": test_type,
                    "success": False,
                    "error": f"Erro ao processar relatório: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "test_type": test_type,
                "success": False,
                "error": "Relatório JSON não encontrado",
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_thresholds(self, results: Dict[str, Any], test_type: str) -> Dict[str, Any]:
        """Validar thresholds de qualidade"""
        if not results.get("success", False):
            return {
                "passed": False,
                "errors": [results.get("error", "Teste falhou")]
            }
        
        errors = []
        warnings = []
        
        # Validar response time P95
        p95_response_time = results.get("response_time_percentiles", {}).get("95", 0)
        if p95_response_time > QUALITY_THRESHOLDS["response_time_p95"]:
            errors.append(f"P95 response time ({p95_response_time}ms) excede threshold ({QUALITY_THRESHOLDS['response_time_p95']}ms)")
        
        # Validar response time P99
        p99_response_time = results.get("response_time_percentiles", {}).get("99", 0)
        if p99_response_time > QUALITY_THRESHOLDS["response_time_p99"]:
            errors.append(f"P99 response time ({p99_response_time}ms) excede threshold ({QUALITY_THRESHOLDS['response_time_p99']}ms)")
        
        # Validar error rate
        error_rate = results.get("error_rate", 0)
        if error_rate > QUALITY_THRESHOLDS["error_rate"]:
            errors.append(f"Error rate ({error_rate:.2%}) excede threshold ({QUALITY_THRESHOLDS['error_rate']:.2%})")
        
        # Validar requests per second
        rps = results.get("total_rps", 0)
        if rps < QUALITY_THRESHOLDS["requests_per_second"]:
            warnings.append(f"RPS ({rps:.2f}) abaixo do threshold ({QUALITY_THRESHOLDS['requests_per_second']})")
        
        # Validar success rate
        success_rate = results.get("success_rate", 0)
        if success_rate < QUALITY_THRESHOLDS["success_rate"]:
            errors.append(f"Success rate ({success_rate:.2%}) abaixo do threshold ({QUALITY_THRESHOLDS['success_rate']:.2%})")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "thresholds": QUALITY_THRESHOLDS
        }
    
    def _save_results(self, results: Dict[str, Any], test_type: str):
        """Salvar resultados do teste"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports_generate_{test_type}_{timestamp}.json"
        filepath = REPORTS_DIR / "reports_generate" / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"💾 [REPORTS_GENERATE] Resultados salvos: {filepath}")
            
        except Exception as e:
            print(f"❌ [REPORTS_GENERATE] Erro ao salvar resultados: {str(e)}")
    
    def _generate_report(self, results: Dict[str, Any], test_type: str):
        """Gerar relatório executivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports_generate_{test_type}_report_{timestamp}.md"
        filepath = REPORTS_DIR / "reports_generate" / filename
        
        try:
            report_content = self._create_report_content(results, test_type)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"📄 [REPORTS_GENERATE] Relatório gerado: {filepath}")
            
        except Exception as e:
            print(f"❌ [REPORTS_GENERATE] Erro ao gerar relatório: {str(e)}")
    
    def _create_report_content(self, results: Dict[str, Any], test_type: str) -> str:
        """Criar conteúdo do relatório"""
        content = f"""# 📊 Relatório de Teste de Carga - Geração de Relatórios

**Tracing ID**: {self.tracing_id}  
**Data/Hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Tipo de Teste**: {test_type.upper()}  
**Versão**: 1.0  

## 🎯 Resumo Executivo

### Status do Teste
- **Sucesso**: {'✅ PASSOU' if results.get('success') else '❌ FALHOU'}
- **Duração**: {(self.end_time - self.start_time).total_seconds():.2f} segundos
- **Tipo**: {test_type}

### Métricas Principais
- **Total de Requests**: {results.get('total_requests', 0):,}
- **Total de Falhas**: {results.get('total_failures', 0):,}
- **Taxa de Erro**: {results.get('error_rate', 0):.2%}
- **Taxa de Sucesso**: {results.get('success_rate', 0):.2%}
- **RPS Médio**: {results.get('total_rps', 0):.2f}

### Response Times
- **Médio**: {results.get('total_avg_response_time', 0):.2f}ms
- **Mediana**: {results.get('total_median_response_time', 0):.2f}ms
- **Mínimo**: {results.get('total_min_response_time', 0):.2f}ms
- **Máximo**: {results.get('total_max_response_time', 0):.2f}ms

### Percentis
"""
        
        # Adicionar percentis
        percentiles = results.get('response_time_percentiles', {})
        for p in [50, 75, 90, 95, 99]:
            value = percentiles.get(str(p), 0)
            content += f"- **P{p}**: {value:.2f}ms\n"
        
        content += f"""
## 📈 Análise Detalhada

### Configuração do Teste
- **Base URL**: {self.config['base_url']}
- **Usuários**: {self.config['users']}
- **Spawn Rate**: {self.config['spawn_rate']}
- **Duração**: {self.config['run_time']}

### Thresholds de Qualidade
"""
        
        for threshold, value in QUALITY_THRESHOLDS.items():
            content += f"- **{threshold}**: {value}\n"
        
        content += f"""
### Validação de Thresholds
"""
        
        validation = self._validate_thresholds(results, test_type)
        if validation["passed"]:
            content += "✅ **Todos os thresholds foram atendidos**\n"
        else:
            content += "❌ **Alguns thresholds não foram atendidos:**\n"
            for error in validation["errors"]:
                content += f"- {error}\n"
        
        if validation["warnings"]:
            content += "\n⚠️ **Avisos:**\n"
            for warning in validation["warnings"]:
                content += f"- {warning}\n"
        
        content += f"""
## 🔧 Recomendações

### Performance
- Analisar otimizações para response times altos
- Considerar cache para relatórios frequentes
- Implementar processamento assíncrono para relatórios complexos

### Escalabilidade
- Monitorar uso de recursos durante picos
- Considerar auto-scaling baseado em demanda
- Implementar rate limiting inteligente

### Qualidade
- Revisar tratamento de erros
- Melhorar validação de entrada
- Implementar retry logic para falhas temporárias

## 📋 Próximos Passos

1. **Análise de Performance**: Investigar gargalos identificados
2. **Otimização**: Implementar melhorias baseadas nos resultados
3. **Monitoramento**: Configurar alertas para métricas críticas
4. **Testes Regulares**: Agendar execução periódica dos testes

---
**Gerado automaticamente pelo sistema de testes de carga**  
**Tracing ID**: {self.tracing_id}
"""
        
        return content
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executar todos os tipos de teste"""
        print(f"\n🚀 [REPORTS_GENERATE] Executando suite completa de testes")
        
        test_types = ["normal", "complex", "batch", "scheduled", "stress"]
        all_results = {}
        
        for test_type in test_types:
            print(f"\n{'='*60}")
            print(f"🧪 Executando teste: {test_type.upper()}")
            print(f"{'='*60}")
            
            result = self.run_test(test_type)
            all_results[test_type] = result
            
            # Aguardar entre testes
            if test_type != test_types[-1]:
                print(f"⏳ Aguardando 30 segundos antes do próximo teste...")
                time.sleep(30)
        
        # Gerar relatório consolidado
        self._generate_consolidated_report(all_results)
        
        return all_results
    
    def _generate_consolidated_report(self, all_results: Dict[str, Any]):
        """Gerar relatório consolidado de todos os testes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports_generate_consolidated_report_{timestamp}.md"
        filepath = REPORTS_DIR / "reports_generate" / filename
        
        try:
            content = self._create_consolidated_report_content(all_results)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n📄 [REPORTS_GENERATE] Relatório consolidado gerado: {filepath}")
            
        except Exception as e:
            print(f"❌ [REPORTS_GENERATE] Erro ao gerar relatório consolidado: {str(e)}")
    
    def _create_consolidated_report_content(self, all_results: Dict[str, Any]) -> str:
        """Criar conteúdo do relatório consolidado"""
        content = f"""# 📊 Relatório Consolidado - Testes de Carga Geração de Relatórios

**Tracing ID**: {self.tracing_id}  
**Data/Hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Versão**: 1.0  

## 🎯 Resumo Executivo

### Status Geral
"""
        
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results.values() if r.get("success", False))
        
        content += f"""
- **Total de Testes**: {total_tests}
- **Testes Aprovados**: {passed_tests}
- **Testes Reprovados**: {total_tests - passed_tests}
- **Taxa de Sucesso**: {passed_tests/total_tests:.2%}
"""

        content += """
### Resumo por Tipo de Teste
| Tipo | Status | Duração | Requests | Taxa de Erro | RPS |
|------|--------|---------|----------|--------------|-----|
"""
        
        for test_type, result in all_results.items():
            results_data = result.get("results", {})
            status = "✅ PASSOU" if result.get("success", False) else "❌ FALHOU"
            duration = f"{result.get('duration', 0):.2f}s"
            requests = f"{results_data.get('total_requests', 0):,}"
            error_rate = f"{results_data.get('error_rate', 0):.2%}"
            rps = f"{results_data.get('total_rps', 0):.2f}"
            
            content += f"| {test_type.upper()} | {status} | {duration} | {requests} | {error_rate} | {rps} |\n"
        
        content += f"""
## 📈 Análise Detalhada por Teste

"""
        
        for test_type, result in all_results.items():
            content += f"### {test_type.upper()}\n\n"
            
            if result.get("success", False):
                results_data = result.get("results", {})
                validation = result.get("validation", {})
                
                content += f"**Status**: ✅ PASSOU\n"
                content += f"**Duração**: {result.get('duration', 0):.2f} segundos\n\n"
                
                content += "**Métricas Principais**:\n"
                content += f"- Requests: {results_data.get('total_requests', 0):,}\n"
                content += f"- Falhas: {results_data.get('total_failures', 0):,}\n"
                content += f"- Taxa de Erro: {results_data.get('error_rate', 0):.2%}\n"
                content += f"- RPS: {results_data.get('total_rps', 0):.2f}\n"
                content += f"- Response Time Médio: {results_data.get('total_avg_response_time', 0):.2f}ms\n\n"
                
                if validation.get("warnings"):
                    content += "**Avisos**:\n"
                    for warning in validation["warnings"]:
                        content += f"- {warning}\n"
                    content += "\n"
            else:
                content += f"**Status**: ❌ FALHOU\n"
                content += f"**Erro**: {result.get('results', {}).get('error', 'Erro desconhecido')}\n\n"
            
            content += "---\n\n"
        
        content += f"""
## 🔧 Recomendações Gerais

### Performance
- Implementar cache para relatórios frequentes
- Otimizar queries de banco de dados
- Considerar processamento assíncrono

### Escalabilidade
- Implementar auto-scaling
- Otimizar uso de recursos
- Melhorar rate limiting

### Qualidade
- Revisar tratamento de erros
- Implementar retry logic
- Melhorar validação de entrada

## 📋 Próximos Passos

1. **Análise**: Investigar gargalos identificados
2. **Otimização**: Implementar melhorias
3. **Monitoramento**: Configurar alertas
4. **Testes Regulares**: Agendar execução periódica

---
**Gerado automaticamente pelo sistema de testes de carga**  
**Tracing ID**: {self.tracing_id}
"""
        
        return content

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executor de testes de carga para geração de relatórios")
    parser.add_argument("--test-type", choices=["normal", "complex", "batch", "scheduled", "stress", "all"],
                       default="all", help="Tipo de teste a executar")
    parser.add_argument("--users", type=int, help="Número de usuários")
    parser.add_argument("--spawn-rate", type=int, help="Taxa de spawn")
    parser.add_argument("--run-time", help="Tempo de execução")
    parser.add_argument("--base-url", help="URL base da aplicação")
    
    args = parser.parse_args()
    
    # Configuração
    config = {}
    if args.users:
        config["users"] = args.users
    if args.spawn_rate:
        config["spawn_rate"] = args.spawn_rate
    if args.run_time:
        config["run_time"] = args.run_time
    if args.base_url:
        config["base_url"] = args.base_url
        config["host"] = args.base_url
    
    # Executar testes
    runner = ReportsGenerateLoadTestRunner(config)
    
    if args.test_type == "all":
        results = runner.run_all_tests()
    else:
        results = runner.run_test(args.test_type)
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"🎉 EXECUÇÃO CONCLUÍDA")
    print(f"{'='*60}")
    
    if isinstance(results, dict) and "test_type" in results:
        # Teste único
        success = results.get("success", False)
        print(f"✅ Status: {'PASSOU' if success else 'FALHOU'}")
        print(f"📊 Tipo: {results.get('test_type', 'unknown')}")
        print(f"⏱️ Duração: {results.get('duration', 0):.2f}s")
    else:
        # Múltiplos testes
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r.get("success", False))
        print(f"📊 Total de Testes: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Reprovados: {total_tests - passed_tests}")
        print(f"📈 Taxa de Sucesso: {passed_tests/total_tests:.2%}")
    
    print(f"📋 Tracing ID: {runner.tracing_id}")
    print(f"📁 Relatórios: {REPORTS_DIR / 'reports_generate'}")
    print(f"📝 Logs: {LOGS_DIR / 'reports_generate'}")

if __name__ == "__main__":
    main() 