#!/usr/bin/env python3
"""
Testes de Performance - Pacote Principal
========================================

Tracing ID: PERFORMANCE_PACKAGE_001
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTAÇÃO

Pacote contendo todos os testes de performance do sistema Omni Keywords Finder.
"""

__version__ = "1.0.0"
__author__ = "Paulo Júnior"
__description__ = "Testes de Performance para Omni Keywords Finder"

# Módulos de teste de performance
__all__ = [
    "test_response_time",
    "test_memory_usage", 
    "test_concurrency"
]

# Configurações de performance
PERFORMANCE_CONFIG = {
    "timeout_seconds": 30,
    "memory_limit_mb": 512,
    "concurrency_threads": 10,
    "scalability_factor": 0.8
}

# Limites de performance
PERFORMANCE_LIMITS = {
    "keyword_creation": 0.001,      # 1ms
    "cluster_creation": 0.005,      # 5ms
    "prompt_generation": 0.010,     # 10ms
    "async_collection": 0.100,      # 100ms
    "cache_operation": 0.001,       # 1ms
    "serialization": 0.002,         # 2ms
    "validation": 0.003,            # 3ms
    "memory_keyword": 1024,         # 1KB por keyword
    "memory_cluster": 10240,        # 10KB por cluster
    "memory_prompt": 2048,          # 2KB por prompt
    "memory_cache": 512,            # 512B por entrada de cache
    "memory_bulk": 1048576,         # 1MB para operações em lote
    "memory_leak": 0.1,             # 10% de crescimento máximo
    "thread_safety": 0.001,         # 1ms para operações thread-safe
    "async_operation": 0.100,       # 100ms para operações assíncronas
    "concurrent_creation": 0.005,   # 5ms para criação concorrente
    "race_condition": 0.001,        # 1ms para evitar race conditions
    "deadlock_timeout": 5.0,        # 5s timeout para deadlocks
    "scalability_factor": 0.8,      # 80% de eficiência em escala
}

# Funções utilitárias para testes de performance
def get_performance_config():
    """Retorna configuração de performance."""
    return PERFORMANCE_CONFIG.copy()

def get_performance_limits():
    """Retorna limites de performance."""
    return PERFORMANCE_LIMITS.copy()

def validate_performance_result(operation_name: str, actual_time: float, expected_limit: float) -> bool:
    """
    Valida se resultado de performance está dentro do limite esperado.
    
    Args:
        operation_name: Nome da operação testada
        actual_time: Tempo real medido
        expected_limit: Limite esperado
        
    Returns:
        True se performance está dentro do limite, False caso contrário
    """
    is_within_limit = actual_time <= expected_limit
    if not is_within_limit:
        print(f"⚠️ Performance Warning: {operation_name} took {actual_time:.6f}s (limit: {expected_limit:.6f}s)")
    return is_within_limit

def log_performance_metric(operation_name: str, actual_time: float, expected_limit: float, success: bool):
    """
    Registra métrica de performance.
    
    Args:
        operation_name: Nome da operação testada
        actual_time: Tempo real medido
        expected_limit: Limite esperado
        success: Se o teste passou
    """
    status = "✅ PASS" if success else "❌ FAIL"
    efficiency = (expected_limit / actual_time * 100) if actual_time > 0 else 0
    print(f"{status} {operation_name}: {actual_time:.6f}s (limit: {expected_limit:.6f}s, efficiency: {efficiency:.1f}%)")

# Configuração de pytest para testes de performance
pytest_plugins = [
    "tests.unit.performance.test_response_time",
    "tests.unit.performance.test_memory_usage",
    "tests.unit.performance.test_concurrency"
]

# Marcadores de pytest para testes de performance
def pytest_configure(config):
    """Configura marcadores de pytest para testes de performance."""
    config.addinivalue_line(
        "markers", "performance: marca teste como teste de performance"
    )
    config.addinivalue_line(
        "markers", "response_time: marca teste como teste de tempo de resposta"
    )
    config.addinivalue_line(
        "markers", "memory_usage: marca teste como teste de uso de memória"
    )
    config.addinivalue_line(
        "markers", "concurrency: marca teste como teste de concorrência"
    )
    config.addinivalue_line(
        "markers", "thread_safety: marca teste como teste de thread safety"
    )
    config.addinivalue_line(
        "markers", "scalability: marca teste como teste de escalabilidade"
    )
    config.addinivalue_line(
        "markers", "race_condition: marca teste como teste de race condition"
    )
    config.addinivalue_line(
        "markers", "deadlock: marca teste como teste de deadlock"
    )
    config.addinivalue_line(
        "markers", "memory_leak: marca teste como teste de vazamento de memória"
    )

# Fixtures comuns para testes de performance
import pytest
import time
import psutil
import os

@pytest.fixture
def performance_timer():
    """Fixture para medir tempo de performance."""
    start_time = time.time()
    yield start_time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"⏱️ Performance Timer: {elapsed_time:.6f}s")

@pytest.fixture
def memory_monitor():
    """Fixture para monitorar uso de memória."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    yield initial_memory
    final_memory = process.memory_info().rss
    memory_used = final_memory - initial_memory
    print(f"💾 Memory Usage: {memory_used / 1024 / 1024:.2f}MB")

@pytest.fixture
def performance_validator():
    """Fixture para validar resultados de performance."""
    def validate(operation_name: str, actual_time: float, expected_limit: float):
        success = validate_performance_result(operation_name, actual_time, expected_limit)
        log_performance_metric(operation_name, actual_time, expected_limit, success)
        return success
    return validate

# Configuração de logging para testes de performance
import logging

# Configurar logger para testes de performance
performance_logger = logging.getLogger("performance_tests")
performance_logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)

# Adicionar handler ao logger
performance_logger.addHandler(console_handler)

def log_performance_event(event_type: str, details: dict):
    """
    Registra evento de performance.
    
    Args:
        event_type: Tipo do evento (test_start, test_end, performance_check, etc.)
        details: Detalhes do evento
    """
    performance_logger.info(f"PERFORMANCE_EVENT: {event_type} - {details}")

# Configuração de relatórios de performance
PERFORMANCE_REPORTS = {
    "response_time": {
        "enabled": True,
        "output_file": "performance_response_time.json",
        "metrics": ["min", "max", "avg", "p95", "p99"]
    },
    "memory_usage": {
        "enabled": True,
        "output_file": "performance_memory_usage.json",
        "metrics": ["peak", "average", "leak_detection"]
    },
    "concurrency": {
        "enabled": True,
        "output_file": "performance_concurrency.json",
        "metrics": ["throughput", "latency", "scalability"]
    }
}

def get_performance_reports_config():
    """Retorna configuração de relatórios de performance."""
    return PERFORMANCE_REPORTS.copy()

# Configuração de alertas de performance
PERFORMANCE_ALERTS = {
    "response_time_threshold": 0.1,  # 100ms
    "memory_usage_threshold": 100,   # 100MB
    "concurrency_failure_rate": 0.05,  # 5%
    "scalability_degradation": 0.2,    # 20%
}

def get_performance_alerts_config():
    """Retorna configuração de alertas de performance."""
    return PERFORMANCE_ALERTS.copy()

# Função para executar todos os testes de performance
def run_all_performance_tests():
    """
    Executa todos os testes de performance.
    
    Returns:
        dict: Resultados dos testes de performance
    """
    import subprocess
    import json
    
    results = {
        "response_time": {},
        "memory_usage": {},
        "concurrency": {},
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "performance_issues": 0
        }
    }
    
    try:
        # Executar testes de tempo de resposta
        log_performance_event("test_suite_start", {"suite": "response_time"})
        response_result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit/performance/test_response_time.py", "-v", "--json-report"],
            capture_output=True,
            text=True
        )
        results["response_time"]["status"] = "completed"
        results["response_time"]["exit_code"] = response_result.returncode
        
        # Executar testes de uso de memória
        log_performance_event("test_suite_start", {"suite": "memory_usage"})
        memory_result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit/performance/test_memory_usage.py", "-v", "--json-report"],
            capture_output=True,
            text=True
        )
        results["memory_usage"]["status"] = "completed"
        results["memory_usage"]["exit_code"] = memory_result.returncode
        
        # Executar testes de concorrência
        log_performance_event("test_suite_start", {"suite": "concurrency"})
        concurrency_result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit/performance/test_concurrency.py", "-v", "--json-report"],
            capture_output=True,
            text=True
        )
        results["concurrency"]["status"] = "completed"
        results["concurrency"]["exit_code"] = concurrency_result.returncode
        
        # Calcular resumo
        total_exit_codes = [
            results["response_time"]["exit_code"],
            results["memory_usage"]["exit_code"],
            results["concurrency"]["exit_code"]
        ]
        
        results["summary"]["total_tests"] = len(total_exit_codes)
        results["summary"]["passed"] = sum(1 for code in total_exit_codes if code == 0)
        results["summary"]["failed"] = sum(1 for code in total_exit_codes if code != 0)
        
        log_performance_event("test_suite_complete", results["summary"])
        
    except Exception as e:
        log_performance_event("test_suite_error", {"error": str(e)})
        results["error"] = str(e)
    
    return results

# Configuração de ambiente para testes de performance
PERFORMANCE_ENVIRONMENT = {
    "python_version": "3.8+",
    "required_packages": [
        "pytest",
        "pytest-asyncio",
        "psutil",
        "asyncio",
        "threading",
        "concurrent.futures"
    ],
    "optional_packages": [
        "pytest-benchmark",
        "pytest-profiling",
        "memory-profiler"
    ],
    "system_requirements": {
        "min_memory": "512MB",
        "min_cpu_cores": 2,
        "recommended_memory": "2GB",
        "recommended_cpu_cores": 4
    }
}

def get_performance_environment():
    """Retorna configuração do ambiente de performance."""
    return PERFORMANCE_ENVIRONMENT.copy()

def check_performance_environment():
    """
    Verifica se o ambiente está adequado para testes de performance.
    
    Returns:
        dict: Status do ambiente
    """
    import sys
    import multiprocessing
    
    status = {
        "python_version": sys.version_info >= (3, 8),
        "cpu_cores": multiprocessing.cpu_count(),
        "memory_available": psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
        "packages_available": {}
    }
    
    # Verificar pacotes disponíveis
    required_packages = PERFORMANCE_ENVIRONMENT["required_packages"]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            status["packages_available"][package] = True
        except ImportError:
            status["packages_available"][package] = False
    
    # Verificar requisitos do sistema
    system_reqs = PERFORMANCE_ENVIRONMENT["system_requirements"]
    status["system_requirements"] = {
        "memory_adequate": status["memory_available"] >= float(system_reqs["min_memory"].replace("MB", "")) / 1024,
        "cpu_adequate": status["cpu_cores"] >= int(system_reqs["min_cpu_cores"])
    }
    
    return status

# Configuração de métricas de performance
PERFORMANCE_METRICS = {
    "response_time": {
        "unit": "seconds",
        "precision": 6,
        "aggregation": ["min", "max", "avg", "median", "p95", "p99"]
    },
    "memory_usage": {
        "unit": "bytes",
        "precision": 0,
        "aggregation": ["peak", "average", "growth_rate"]
    },
    "concurrency": {
        "unit": "operations_per_second",
        "precision": 2,
        "aggregation": ["throughput", "latency", "efficiency"]
    },
    "scalability": {
        "unit": "percentage",
        "precision": 2,
        "aggregation": ["linear_growth", "efficiency_ratio"]
    }
}

def get_performance_metrics_config():
    """Retorna configuração de métricas de performance."""
    return PERFORMANCE_METRICS.copy()

# Função para gerar relatório de performance
def generate_performance_report(test_results: dict, output_file: str = "performance_report.json"):
    """
    Gera relatório de performance baseado nos resultados dos testes.
    
    Args:
        test_results: Resultados dos testes de performance
        output_file: Arquivo de saída para o relatório
    """
    import json
    from datetime import datetime
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "version": __version__,
        "test_results": test_results,
        "performance_limits": PERFORMANCE_LIMITS,
        "environment": check_performance_environment(),
        "summary": {
            "total_tests": test_results.get("summary", {}).get("total_tests", 0),
            "passed": test_results.get("summary", {}).get("passed", 0),
            "failed": test_results.get("summary", {}).get("failed", 0),
            "success_rate": 0.0
        }
    }
    
    # Calcular taxa de sucesso
    total = report["summary"]["total_tests"]
    passed = report["summary"]["passed"]
    if total > 0:
        report["summary"]["success_rate"] = (passed / total) * 100
    
    # Salvar relatório
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        log_performance_event("report_generated", {"file": output_file})
    except Exception as e:
        log_performance_event("report_error", {"error": str(e)})
    
    return report

# Configuração de exportação
__all__.extend([
    "get_performance_config",
    "get_performance_limits", 
    "validate_performance_result",
    "log_performance_metric",
    "run_all_performance_tests",
    "check_performance_environment",
    "generate_performance_report"
]) 