#!/usr/bin/env python3
"""
Script de Execução - Testes de Carga de Integração Externa
Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - 5. APIs de Integração Externa
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: RUN_INTEGRATION_LOAD_TESTS_20250127_001

Funcionalidades:
- Execução de testes de carga para integrações externas
- Configuração de parâmetros por categoria
- Geração de relatórios de performance
- Monitoramento de métricas em tempo real
- Validação de thresholds de qualidade
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configurações
BASE_DIR = Path(__file__).parent.parent
INTEGRATION_TESTS_DIR = BASE_DIR / "high" / "integrations"
REPORTS_DIR = BASE_DIR / "reports" / "integration"
LOGS_DIR = BASE_DIR / "logs" / "integration"

# Configurações de teste por categoria
TEST_CONFIGS = {
    "google_trends": {
        "locustfile": "locustfile_integration_google_trends_v1.py",
        "users": 50,
        "spawn_rate": 5,
        "run_time": "2m",
        "description": "Teste de carga para Google Trends API"
    },
    "consumo_externo": {
        "locustfile": "locustfile_integration_consumo_externo_v1.py",
        "users": 30,
        "spawn_rate": 3,
        "run_time": "3m",
        "description": "Teste de carga para consumo de APIs externas"
    },
    "instagram": {
        "locustfile": "locustfile_integration_instagram_v1.py",
        "users": 20,
        "spawn_rate": 2,
        "run_time": "2m",
        "description": "Teste de carga para Instagram API"
    },
    "tiktok": {
        "locustfile": "locustfile_integration_tiktok_v1.py",
        "users": 20,
        "spawn_rate": 2,
        "run_time": "2m",
        "description": "Teste de carga para TikTok API"
    },
    "youtube": {
        "locustfile": "locustfile_integration_youtube_v1.py",
        "users": 25,
        "spawn_rate": 3,
        "run_time": "2m",
        "description": "Teste de carga para YouTube API"
    },
    "pinterest": {
        "locustfile": "locustfile_integration_pinterest_v1.py",
        "users": 15,
        "spawn_rate": 2,
        "run_time": "2m",
        "description": "Teste de carga para Pinterest API"
    }
}

# Thresholds de qualidade
QUALITY_THRESHOLDS = {
    "response_time_p95": 2000,  # ms
    "error_rate": 5.0,  # %
    "throughput_min": 10,  # requests/sec
    "success_rate": 95.0  # %
}

def setup_directories():
    """Cria diretórios necessários"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def run_single_test(test_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa um teste de carga específico
    
    Args:
        test_name: Nome do teste
        config: Configuração do teste
        
    Returns:
        Resultados do teste
    """
    print(f"\n🚀 Executando teste: {test_name}")
    print(f"📝 Descrição: {config['description']}")
    print(f"👥 Usuários: {config['users']}")
    print(f"📈 Taxa de spawn: {config['spawn_rate']}/s")
    print(f"⏱️  Duração: {config['run_time']}")
    
    # Arquivo de teste
    locustfile = INTEGRATION_TESTS_DIR / config["locustfile"]
    
    if not locustfile.exists():
        print(f"❌ Arquivo de teste não encontrado: {locustfile}")
        return {
            "test_name": test_name,
            "status": "error",
            "error": "Arquivo de teste não encontrado"
        }
    
    # Timestamp para logs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"{test_name}_{timestamp}.log"
    report_file = REPORTS_DIR / f"{test_name}_{timestamp}.json"
    
    # Comando Locust
    cmd = [
        "locust",
        "-f", str(locustfile),
        "--users", str(config["users"]),
        "--spawn-rate", str(config["spawn_rate"]),
        "--run-time", config["run_time"],
        "--headless",
        "--json", str(report_file),
        "--logfile", str(log_file),
        "--loglevel", "INFO"
    ]
    
    start_time = time.time()
    
    try:
        # Executa o teste
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        execution_time = time.time() - start_time
        
        # Analisa resultados
        if result.returncode == 0:
            # Lê relatório JSON
            if report_file.exists():
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                
                # Extrai métricas
                stats = report_data.get("stats", [])
                if stats:
                    # Calcula métricas agregadas
                    total_requests = sum(stat.get("num_requests", 0) for stat in stats)
                    total_failures = sum(stat.get("num_failures", 0) for stat in stats)
                    avg_response_time = sum(stat.get("avg_response_time", 0) * stat.get("num_requests", 0) for stat in stats) / total_requests if total_requests > 0 else 0
                    
                    # P95 response time (aproximado)
                    response_times = []
                    for stat in stats:
                        response_times.extend([stat.get("avg_response_time", 0)] * stat.get("num_requests", 0))
                    response_times.sort()
                    p95_index = int(len(response_times) * 0.95)
                    p95_response_time = response_times[p95_index] if response_times else 0
                    
                    # Calcula rates
                    success_rate = ((total_requests - total_failures) / total_requests * 100) if total_requests > 0 else 0
                    error_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0
                    throughput = total_requests / execution_time if execution_time > 0 else 0
                    
                    # Valida thresholds
                    threshold_results = {
                        "response_time_p95": p95_response_time <= QUALITY_THRESHOLDS["response_time_p95"],
                        "error_rate": error_rate <= QUALITY_THRESHOLDS["error_rate"],
                        "throughput": throughput >= QUALITY_THRESHOLDS["throughput_min"],
                        "success_rate": success_rate >= QUALITY_THRESHOLDS["success_rate"]
                    }
                    
                    all_thresholds_passed = all(threshold_results.values())
                    
                    test_result = {
                        "test_name": test_name,
                        "status": "passed" if all_thresholds_passed else "failed",
                        "execution_time": execution_time,
                        "metrics": {
                            "total_requests": total_requests,
                            "total_failures": total_failures,
                            "avg_response_time": avg_response_time,
                            "p95_response_time": p95_response_time,
                            "success_rate": success_rate,
                            "error_rate": error_rate,
                            "throughput": throughput
                        },
                        "threshold_results": threshold_results,
                        "report_file": str(report_file),
                        "log_file": str(log_file)
                    }
                    
                    # Log de resultados
                    print(f"✅ Teste concluído: {test_name}")
                    print(f"📊 Métricas:")
                    print(f"   - Requisições totais: {total_requests}")
                    print(f"   - Falhas: {total_failures}")
                    print(f"   - Taxa de sucesso: {success_rate:.2f}%")
                    print(f"   - Tempo médio de resposta: {avg_response_time:.2f}ms")
                    print(f"   - P95 tempo de resposta: {p95_response_time:.2f}ms")
                    print(f"   - Throughput: {throughput:.2f} req/s")
                    
                    if all_thresholds_passed:
                        print(f"🎯 Todos os thresholds passaram!")
                    else:
                        print(f"⚠️  Alguns thresholds falharam:")
                        for threshold, passed in threshold_results.items():
                            status = "✅" if passed else "❌"
                            print(f"   {status} {threshold}")
                    
                    return test_result
                else:
                    return {
                        "test_name": test_name,
                        "status": "error",
                        "error": "Nenhuma estatística encontrada no relatório"
                    }
            else:
                return {
                    "test_name": test_name,
                    "status": "error",
                    "error": "Arquivo de relatório não gerado"
                }
        else:
            return {
                "test_name": test_name,
                "status": "error",
                "error": f"Comando falhou: {result.stderr}",
                "returncode": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            "test_name": test_name,
            "status": "error",
            "error": "Timeout na execução do teste"
        }
    except Exception as e:
        return {
            "test_name": test_name,
            "status": "error",
            "error": f"Erro inesperado: {str(e)}"
        }

def run_all_integration_tests() -> Dict[str, Any]:
    """
    Executa todos os testes de integração
    
    Returns:
        Resultados consolidados
    """
    print("🔗 INICIANDO TESTES DE CARGA - INTEGRAÇÕES EXTERNAS")
    print("=" * 60)
    
    setup_directories()
    
    results = []
    passed_tests = 0
    failed_tests = 0
    error_tests = 0
    
    start_time = time.time()
    
    for test_name, config in TEST_CONFIGS.items():
        result = run_single_test(test_name, config)
        results.append(result)
        
        if result["status"] == "passed":
            passed_tests += 1
        elif result["status"] == "failed":
            failed_tests += 1
        else:
            error_tests += 1
    
    total_time = time.time() - start_time
    
    # Relatório consolidado
    consolidated_report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "error_tests": error_tests,
        "total_execution_time": total_time,
        "success_rate": (passed_tests / len(results) * 100) if results else 0,
        "results": results
    }
    
    # Salva relatório consolidado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    consolidated_file = REPORTS_DIR / f"integration_tests_consolidated_{timestamp}.json"
    
    with open(consolidated_file, 'w') as f:
        json.dump(consolidated_report, f, indent=2)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📋 RESUMO FINAL - TESTES DE INTEGRAÇÃO")
    print("=" * 60)
    print(f"✅ Testes aprovados: {passed_tests}")
    print(f"❌ Testes reprovados: {failed_tests}")
    print(f"⚠️  Testes com erro: {error_tests}")
    print(f"📊 Taxa de sucesso: {consolidated_report['success_rate']:.2f}%")
    print(f"⏱️  Tempo total: {total_time:.2f}s")
    print(f"📄 Relatório: {consolidated_file}")
    
    return consolidated_report

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executa testes de carga de integração externa")
    parser.add_argument(
        "--test", 
        choices=list(TEST_CONFIGS.keys()),
        help="Executa apenas um teste específico"
    )
    parser.add_argument(
        "--list", 
        action="store_true",
        help="Lista todos os testes disponíveis"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 TESTES DE INTEGRAÇÃO DISPONÍVEIS:")
        print("=" * 50)
        for test_name, config in TEST_CONFIGS.items():
            print(f"🔗 {test_name}: {config['description']}")
        return
    
    if args.test:
        if args.test in TEST_CONFIGS:
            config = TEST_CONFIGS[args.test]
            result = run_single_test(args.test, config)
            print(f"\n📊 Resultado: {result['status']}")
        else:
            print(f"❌ Teste '{args.test}' não encontrado")
            return
    else:
        # Executa todos os testes
        run_all_integration_tests()

if __name__ == "__main__":
    main() 