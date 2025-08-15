#!/usr/bin/env python3
"""
🎯 FASE 4 - SCRIPT DE VALIDAÇÃO DA INTEGRAÇÃO COM OBSERVABILIDADE
Tracing ID: OBSERVABILIDADE_VALIDATION_001_20250127

Este script valida se todos os componentes da Fase 4 foram integrados corretamente
com os serviços existentes do Omni Keywords Finder.
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Optional
from datetime import datetime

# Adicionar paths necessários
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def log_validation(message: str, level: str = "INFO") -> None:
    """Log de validação com timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def check_module_imports(module_name: str, expected_imports: List[str]) -> Dict[str, bool]:
    """
    Verifica se um módulo pode ser importado e se contém as importações esperadas.
    
    Args:
        module_name: Nome do módulo a verificar
        expected_imports: Lista de importações esperadas
        
    Returns:
        Dicionário com resultados da validação
    """
    results = {
        "module_importable": False,
        "imports_found": [],
        "imports_missing": []
    }
    
    try:
        module = importlib.import_module(module_name)
        results["module_importable"] = True
        
        # Verificar importações
        module_source = inspect.getsource(module)
        for import_name in expected_imports:
            if import_name in module_source:
                results["imports_found"].append(import_name)
            else:
                results["imports_missing"].append(import_name)
                
    except ImportError as e:
        log_validation(f"Erro ao importar {module_name}: {e}", "ERROR")
    except Exception as e:
        log_validation(f"Erro inesperado ao verificar {module_name}: {e}", "ERROR")
    
    return results

def check_decorators_in_file(file_path: str, expected_decorators: List[str]) -> Dict[str, Any]:
    """
    Verifica se um arquivo contém os decorators esperados.
    
    Args:
        file_path: Caminho do arquivo
        expected_decorators: Lista de decorators esperados
        
    Returns:
        Dicionário com resultados da validação
    """
    results = {
        "file_exists": False,
        "decorators_found": [],
        "decorators_missing": [],
        "functions_with_decorators": []
    }
    
    if not os.path.exists(file_path):
        log_validation(f"Arquivo não encontrado: {file_path}", "ERROR")
        return results
    
    results["file_exists"] = True
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar decorators
        for decorator in expected_decorators:
            if decorator in content:
                results["decorators_found"].append(decorator)
            else:
                results["decorators_missing"].append(decorator)
        
        # Encontrar funções com decorators
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if any(decorator in line for decorator in expected_decorators):
                # Procurar função na próxima linha
                if i + 1 < len(lines) and 'def ' in lines[i + 1]:
                    func_name = lines[i + 1].split('def ')[1].split('(')[0].strip()
                    results["functions_with_decorators"].append(func_name)
                    
    except Exception as e:
        log_validation(f"Erro ao ler arquivo {file_path}: {e}", "ERROR")
    
    return results

def validate_backend_integration() -> Dict[str, Any]:
    """Valida integração com o backend principal."""
    log_validation("🔍 Validando integração com backend principal...")
    
    results = {
        "main_py": {},
        "execucao_service": {},
        "overall_status": "PENDING"
    }
    
    # Verificar main.py
    main_py_path = "backend/app/main.py"
    expected_decorators = ["@trace_function"]
    results["main_py"] = check_decorators_in_file(main_py_path, expected_decorators)
    
    # Verificar execucao_service.py
    execucao_service_path = "backend/app/services/execucao_service.py"
    results["execucao_service"] = check_decorators_in_file(execucao_service_path, expected_decorators)
    
    # Verificar importações no main.py
    expected_imports = [
        "from infrastructure.observability.advanced_tracing import AdvancedTracing",
        "from infrastructure.observability.trace_decorator import trace_function",
        "from infrastructure.observability.anomaly_detection import AnomalyDetection",
        "from infrastructure.observability.predictive_monitoring import PredictiveMonitoring"
    ]
    
    import_results = check_module_imports("backend.app.main", expected_imports)
    results["main_imports"] = import_results
    
    # Determinar status geral
    all_checks = [
        results["main_py"]["file_exists"],
        results["main_py"]["decorators_found"],
        results["execucao_service"]["file_exists"],
        results["execucao_service"]["decorators_found"],
        import_results["module_importable"]
    ]
    
    if all(all_checks):
        results["overall_status"] = "SUCCESS"
    elif any(all_checks):
        results["overall_status"] = "PARTIAL"
    else:
        results["overall_status"] = "FAILED"
    
    return results

def validate_coleta_integration() -> Dict[str, Any]:
    """Valida integração com o sistema de coleta."""
    log_validation("🔍 Validando integração com sistema de coleta...")
    
    results = {
        "base_keyword": {},
        "overall_status": "PENDING"
    }
    
    # Verificar base_keyword.py
    base_keyword_path = "infrastructure/coleta/base_keyword.py"
    expected_decorators = ["@trace_function"]
    results["base_keyword"] = check_decorators_in_file(base_keyword_path, expected_decorators)
    
    # Verificar importações
    expected_imports = [
        "from infrastructure.observability.trace_decorator import trace_function",
        "from infrastructure.observability.anomaly_detection import AnomalyDetection",
        "from infrastructure.observability.predictive_monitoring import PredictiveMonitoring"
    ]
    
    import_results = check_module_imports("infrastructure.coleta.base_keyword", expected_imports)
    results["imports"] = import_results
    
    # Determinar status geral
    all_checks = [
        results["base_keyword"]["file_exists"],
        results["base_keyword"]["decorators_found"],
        import_results["module_importable"]
    ]
    
    if all(all_checks):
        results["overall_status"] = "SUCCESS"
    elif any(all_checks):
        results["overall_status"] = "PARTIAL"
    else:
        results["overall_status"] = "FAILED"
    
    return results

def validate_observability_components() -> Dict[str, Any]:
    """Valida se os componentes de observabilidade existem."""
    log_validation("🔍 Validando componentes de observabilidade...")
    
    components = [
        "infrastructure.observability.advanced_tracing",
        "infrastructure.observability.trace_context",
        "infrastructure.observability.trace_decorator",
        "infrastructure.observability.trace_config",
        "infrastructure.observability.anomaly_detection",
        "infrastructure.observability.anomaly_alerting",
        "infrastructure.observability.anomaly_config",
        "infrastructure.observability.predictive_monitoring",
        "infrastructure.observability.prediction_models",
        "infrastructure.observability.prediction_alerting",
        "infrastructure.observability.prediction_config"
    ]
    
    results = {
        "components": {},
        "overall_status": "PENDING"
    }
    
    for component in components:
        try:
            module = importlib.import_module(component)
            results["components"][component] = {
                "importable": True,
                "has_initialize": hasattr(module, 'initialize'),
                "has_config": hasattr(module, 'Config') or 'config' in dir(module)
            }
        except ImportError as e:
            results["components"][component] = {
                "importable": False,
                "error": str(e)
            }
    
    # Determinar status geral
    importable_count = sum(1 for comp in results["components"].values() if comp.get("importable", False))
    total_count = len(components)
    
    if importable_count == total_count:
        results["overall_status"] = "SUCCESS"
    elif importable_count > total_count // 2:
        results["overall_status"] = "PARTIAL"
    else:
        results["overall_status"] = "FAILED"
    
    return results

def validate_configuration_files() -> Dict[str, Any]:
    """Valida arquivos de configuração."""
    log_validation("🔍 Validando arquivos de configuração...")
    
    config_files = [
        "config/observability_dashboards.yml"
    ]
    
    results = {
        "files": {},
        "overall_status": "PENDING"
    }
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                results["files"][config_file] = {
                    "exists": True,
                    "has_grafana_config": "grafana:" in content,
                    "has_alerts_config": "alerts:" in content,
                    "has_channels_config": "alert_channels:" in content,
                    "size_bytes": len(content)
                }
            except Exception as e:
                results["files"][config_file] = {
                    "exists": True,
                    "error": str(e)
                }
        else:
            results["files"][config_file] = {
                "exists": False
            }
    
    # Determinar status geral
    existing_files = sum(1 for file_info in results["files"].values() if file_info.get("exists", False))
    total_files = len(config_files)
    
    if existing_files == total_files:
        results["overall_status"] = "SUCCESS"
    elif existing_files > 0:
        results["overall_status"] = "PARTIAL"
    else:
        results["overall_status"] = "FAILED"
    
    return results

def generate_validation_report(results: Dict[str, Any]) -> None:
    """Gera relatório de validação."""
    log_validation("📊 GERANDO RELATÓRIO DE VALIDAÇÃO DA FASE 4")
    log_validation("=" * 60)
    
    # Backend Integration
    backend_results = results["backend_integration"]
    log_validation(f"🔧 Backend Integration: {backend_results['overall_status']}")
    
    if backend_results["main_py"]["file_exists"]:
        log_validation(f"  ✅ main.py: {len(backend_results['main_py']['decorators_found'])}/{len(backend_results['main_py']['decorators_found'] + backend_results['main_py']['decorators_missing'])} decorators")
        for func in backend_results["main_py"]["functions_with_decorators"]:
            log_validation(f"    - {func}")
    
    if backend_results["execucao_service"]["file_exists"]:
        log_validation(f"  ✅ execucao_service.py: {len(backend_results['execucao_service']['decorators_found'])}/{len(backend_results['execucao_service']['decorators_found'] + backend_results['execucao_service']['decorators_missing'])} decorators")
        for func in backend_results["execucao_service"]["functions_with_decorators"]:
            log_validation(f"    - {func}")
    
    # Coleta Integration
    coleta_results = results["coleta_integration"]
    log_validation(f"🔍 Coleta Integration: {coleta_results['overall_status']}")
    
    if coleta_results["base_keyword"]["file_exists"]:
        log_validation(f"  ✅ base_keyword.py: {len(coleta_results['base_keyword']['decorators_found'])}/{len(coleta_results['base_keyword']['decorators_found'] + coleta_results['base_keyword']['decorators_missing'])} decorators")
    
    # Observability Components
    obs_results = results["observability_components"]
    log_validation(f"🎯 Observability Components: {obs_results['overall_status']}")
    
    importable_count = sum(1 for comp in obs_results["components"].values() if comp.get("importable", False))
    total_count = len(obs_results["components"])
    log_validation(f"  📦 Components: {importable_count}/{total_count} importable")
    
    for component, info in obs_results["components"].items():
        status = "✅" if info.get("importable", False) else "❌"
        log_validation(f"    {status} {component}")
    
    # Configuration Files
    config_results = results["configuration_files"]
    log_validation(f"⚙️ Configuration Files: {config_results['overall_status']}")
    
    for config_file, info in config_results["files"].items():
        status = "✅" if info.get("exists", False) else "❌"
        log_validation(f"    {status} {config_file}")
        if info.get("exists", False) and "size_bytes" in info:
            log_validation(f"      📏 Size: {info['size_bytes']} bytes")
    
    # Overall Status
    overall_statuses = [
        backend_results["overall_status"],
        coleta_results["overall_status"],
        obs_results["overall_status"],
        config_results["overall_status"]
    ]
    
    if all(status == "SUCCESS" for status in overall_statuses):
        overall_status = "SUCCESS"
    elif any(status == "SUCCESS" for status in overall_statuses):
        overall_status = "PARTIAL"
    else:
        overall_status = "FAILED"
    
    log_validation("=" * 60)
    log_validation(f"🎯 OVERALL STATUS: {overall_status}")
    
    if overall_status == "SUCCESS":
        log_validation("✅ FASE 4 - OBSERVABILIDADE AVANÇADA INTEGRADA COM SUCESSO!")
    elif overall_status == "PARTIAL":
        log_validation("⚠️ FASE 4 - INTEGRAÇÃO PARCIAL. Verificar itens pendentes.")
    else:
        log_validation("❌ FASE 4 - INTEGRAÇÃO FALHOU. Revisar implementação.")

def main():
    """Função principal de validação."""
    log_validation("🚀 INICIANDO VALIDAÇÃO DA FASE 4 - OBSERVABILIDADE AVANÇADA")
    log_validation("Tracing ID: OBSERVABILIDADE_VALIDATION_001_20250127")
    log_validation("=" * 60)
    
    results = {
        "backend_integration": validate_backend_integration(),
        "coleta_integration": validate_coleta_integration(),
        "observability_components": validate_observability_components(),
        "configuration_files": validate_configuration_files()
    }
    
    generate_validation_report(results)
    
    log_validation("=" * 60)
    log_validation("🏁 VALIDAÇÃO CONCLUÍDA")

if __name__ == "__main__":
    main() 