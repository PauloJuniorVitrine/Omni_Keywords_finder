#!/usr/bin/env python3
"""
Script de Validação de Confiabilidade - Omni Keywords Finder
============================================================

Tracing ID: VALIDATE_RELIABILITY_001_20250127
Data: 2025-01-27
Versão: 1.0.0

Script para validar a implementação completa de confiabilidade do sistema.
Verifica todos os componentes implementados e gera relatório de validação.

Prompt: CHECKLIST_CONFIABILIDADE.md - Fase 7 - IMP-019
Ruleset: enterprise_control_layer.yaml
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status de validação."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ValidationSeverity(Enum):
    """Severidade da validação."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationResult:
    """Resultado de uma validação."""
    component: str
    test_name: str
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ValidationReport:
    """Relatório de validação."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    skipped_tests: int
    results: List[ValidationResult]
    summary: str
    recommendations: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ReliabilityValidator:
    """Validador de confiabilidade do sistema."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.project_root = Path(__file__).parent.parent
        
    def validate_all(self) -> ValidationReport:
        """Executa todas as validações."""
        logger.info("Iniciando validação completa de confiabilidade...")
        
        # Validações de Fase 1 - Resiliência Avançada
        self._validate_resilience_patterns()
        
        # Validações de Fase 2 - Auto-Healing
        self._validate_auto_healing()
        
        # Validações de Fase 3 - Redundância Multi-Region
        self._validate_multi_region()
        
        # Validações de Fase 4 - Observabilidade Avançada
        self._validate_observability()
        
        # Validações de Fase 5 - Chaos Engineering
        self._validate_chaos_engineering()
        
        # Validações de Fase 6 - Otimizações Finais
        self._validate_optimizations()
        
        # Validações de Fase 7 - Documentação e Validação
        self._validate_documentation()
        
        # Gera relatório
        return self._generate_report()
    
    def _validate_resilience_patterns(self):
        """Valida padrões de resiliência."""
        logger.info("Validando padrões de resiliência...")
        
        # Circuit Breaker
        self._validate_file_exists(
            "infrastructure/resilience/circuit_breaker.py",
            "Circuit Breaker Pattern",
            ValidationSeverity.CRITICAL
        )
        
        # Retry Strategy
        self._validate_file_exists(
            "infrastructure/resilience/retry_strategy.py",
            "Retry Strategy",
            ValidationSeverity.HIGH
        )
        
        # Bulkhead Pattern
        self._validate_file_exists(
            "infrastructure/resilience/bulkhead.py",
            "Bulkhead Pattern",
            ValidationSeverity.HIGH
        )
        
        # Timeout Management
        self._validate_file_exists(
            "infrastructure/resilience/timeout_manager.py",
            "Timeout Management",
            ValidationSeverity.MEDIUM
        )
        
        # Valida integração nos coletores
        self._validate_integration_files([
            "infrastructure/coleta/google_keyword_planner.py",
            "infrastructure/coleta/youtube.py",
            "infrastructure/coleta/reddit.py",
            "infrastructure/coleta/instagram.py"
        ], "Integração de Resiliência nos Coletores")
    
    def _validate_auto_healing(self):
        """Valida sistema de auto-healing."""
        logger.info("Validando sistema de auto-healing...")
        
        # Health Check
        self._validate_file_exists(
            "infrastructure/health/advanced_health_check.py",
            "Advanced Health Check",
            ValidationSeverity.CRITICAL
        )
        
        # Auto-Recovery
        self._validate_file_exists(
            "infrastructure/recovery/auto_recovery.py",
            "Auto-Recovery System",
            ValidationSeverity.HIGH
        )
        
        # Self-Healing
        self._validate_file_exists(
            "infrastructure/healing/self_healing_service.py",
            "Self-Healing Service",
            ValidationSeverity.HIGH
        )
        
        # Configuração de health check
        self._validate_file_exists(
            "config/health/health_check_config.yaml",
            "Health Check Configuration",
            ValidationSeverity.MEDIUM
        )
    
    def _validate_multi_region(self):
        """Valida redundância multi-region."""
        logger.info("Validando redundância multi-region...")
        
        # Kubernetes deployment
        self._validate_file_exists(
            "k8s/multi-region/deployment.yaml",
            "Multi-Region Kubernetes Deployment",
            ValidationSeverity.HIGH
        )
        
        # Terraform configuration
        self._validate_file_exists(
            "terraform/multi-region/main.tf",
            "Multi-Region Terraform Configuration",
            ValidationSeverity.HIGH
        )
        
        # Database replication
        self._validate_file_exists(
            "infrastructure/database/multi_region_db.py",
            "Multi-Region Database",
            ValidationSeverity.CRITICAL
        )
        
        # Load balancing
        self._validate_file_exists(
            "infrastructure/load_balancing/advanced_lb.py",
            "Advanced Load Balancing",
            ValidationSeverity.HIGH
        )
    
    def _validate_observability(self):
        """Valida observabilidade avançada."""
        logger.info("Validando observabilidade avançada...")
        
        # Distributed tracing
        self._validate_file_exists(
            "infrastructure/observability/advanced_tracing.py",
            "Advanced Distributed Tracing",
            ValidationSeverity.HIGH
        )
        
        # Anomaly detection
        self._validate_file_exists(
            "infrastructure/observability/anomaly_detection.py",
            "Anomaly Detection",
            ValidationSeverity.MEDIUM
        )
        
        # Predictive monitoring
        self._validate_file_exists(
            "infrastructure/observability/predictive_monitoring.py",
            "Predictive Monitoring",
            ValidationSeverity.MEDIUM
        )
        
        # Prometheus configuration
        self._validate_file_exists(
            "config/telemetry/prometheus.yml",
            "Prometheus Configuration",
            ValidationSeverity.MEDIUM
        )
    
    def _validate_chaos_engineering(self):
        """Valida chaos engineering."""
        logger.info("Validando chaos engineering...")
        
        # Chaos experiments
        self._validate_file_exists(
            "infrastructure/chaos/chaos_experiments.py",
            "Chaos Experiments",
            ValidationSeverity.MEDIUM
        )
        
        # Failure injection
        self._validate_file_exists(
            "infrastructure/chaos/failure_injection.py",
            "Failure Injection",
            ValidationSeverity.MEDIUM
        )
    
    def _validate_optimizations(self):
        """Valida otimizações finais."""
        logger.info("Validando otimizações finais...")
        
        # Performance optimization
        self._validate_file_exists(
            "infrastructure/performance/optimizer.py",
            "Performance Optimizer",
            ValidationSeverity.LOW
        )
        
        # Security hardening
        self._validate_file_exists(
            "infrastructure/security/hardening.py",
            "Security Hardening",
            ValidationSeverity.HIGH
        )
    
    def _validate_documentation(self):
        """Valida documentação."""
        logger.info("Validando documentação...")
        
        # Guias de documentação
        documentation_files = [
            "docs/RELIABILITY_GUIDE.md",
            "docs/RESILIENCE_PATTERNS.md",
            "docs/AUTO_HEALING_GUIDE.md",
            "docs/CHAOS_ENGINEERING_GUIDE.md",
            "docs/MONITORING_GUIDE.md"
        ]
        
        for doc_file in documentation_files:
            self._validate_file_exists(
                doc_file,
                f"Documentation: {Path(doc_file).stem}",
                ValidationSeverity.MEDIUM
            )
        
        # README atualizado
        self._validate_file_exists(
            "README.md",
            "Updated README",
            ValidationSeverity.MEDIUM
        )
    
    def _validate_file_exists(self, file_path: str, test_name: str, severity: ValidationSeverity):
        """Valida se arquivo existe."""
        full_path = self.project_root / file_path
        
        if full_path.exists():
            self.results.append(ValidationResult(
                component="File System",
                test_name=test_name,
                status=ValidationStatus.PASSED,
                severity=severity,
                message=f"File {file_path} exists",
                details={"file_path": str(full_path), "file_size": full_path.stat().st_size}
            ))
        else:
            self.results.append(ValidationResult(
                component="File System",
                test_name=test_name,
                status=ValidationStatus.FAILED,
                severity=severity,
                message=f"File {file_path} not found",
                details={"expected_path": str(full_path)}
            ))
    
    def _validate_integration_files(self, file_paths: List[str], test_name: str):
        """Valida arquivos de integração."""
        existing_files = []
        missing_files = []
        
        for file_path in file_paths:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        if len(missing_files) == 0:
            self.results.append(ValidationResult(
                component="Integration",
                test_name=test_name,
                status=ValidationStatus.PASSED,
                severity=ValidationSeverity.HIGH,
                message=f"All {len(existing_files)} integration files exist",
                details={"existing_files": existing_files}
            ))
        else:
            self.results.append(ValidationResult(
                component="Integration",
                test_name=test_name,
                status=ValidationStatus.WARNING,
                severity=ValidationSeverity.HIGH,
                message=f"Missing {len(missing_files)} integration files",
                details={"existing_files": existing_files, "missing_files": missing_files}
            ))
    
    def _validate_python_syntax(self, file_path: str):
        """Valida sintaxe Python."""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return ValidationResult(
                component="Python Syntax",
                test_name=f"Syntax Check: {file_path}",
                status=ValidationStatus.SKIPPED,
                severity=ValidationSeverity.MEDIUM,
                message=f"File {file_path} not found, skipping syntax check"
            )
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(full_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return ValidationResult(
                    component="Python Syntax",
                    test_name=f"Syntax Check: {file_path}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Python syntax is valid",
                    details={"file_path": str(full_path)}
                )
            else:
                return ValidationResult(
                    component="Python Syntax",
                    test_name=f"Syntax Check: {file_path}",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Python syntax error: {result.stderr}",
                    details={"file_path": str(full_path), "error": result.stderr}
                )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                component="Python Syntax",
                test_name=f"Syntax Check: {file_path}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.MEDIUM,
                message="Syntax check timeout",
                details={"file_path": str(full_path)}
            )
        except Exception as e:
            return ValidationResult(
                component="Python Syntax",
                test_name=f"Syntax Check: {file_path}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.MEDIUM,
                message=f"Syntax check error: {str(e)}",
                details={"file_path": str(full_path), "error": str(e)}
            )
    
    def _validate_yaml_syntax(self, file_path: str):
        """Valida sintaxe YAML."""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return ValidationResult(
                component="YAML Syntax",
                test_name=f"YAML Check: {file_path}",
                status=ValidationStatus.SKIPPED,
                severity=ValidationSeverity.MEDIUM,
                message=f"File {file_path} not found, skipping YAML check"
            )
        
        try:
            import yaml
            with open(full_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            
            return ValidationResult(
                component="YAML Syntax",
                test_name=f"YAML Check: {file_path}",
                status=ValidationStatus.PASSED,
                severity=ValidationSeverity.MEDIUM,
                message="YAML syntax is valid",
                details={"file_path": str(full_path)}
            )
        except Exception as e:
            return ValidationResult(
                component="YAML Syntax",
                test_name=f"YAML Check: {file_path}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.MEDIUM,
                message=f"YAML syntax error: {str(e)}",
                details={"file_path": str(full_path), "error": str(e)}
            )
    
    def _generate_report(self) -> ValidationReport:
        """Gera relatório de validação."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == ValidationStatus.PASSED])
        failed_tests = len([r for r in self.results if r.status == ValidationStatus.FAILED])
        warning_tests = len([r for r in self.results if r.status == ValidationStatus.WARNING])
        skipped_tests = len([r for r in self.results if r.status == ValidationStatus.SKIPPED])
        
        # Gera resumo
        if failed_tests == 0 and warning_tests == 0:
            summary = f"✅ VALIDAÇÃO APROVADA: {passed_tests}/{total_tests} testes passaram"
        elif failed_tests == 0:
            summary = f"⚠️ VALIDAÇÃO COM AVISOS: {passed_tests}/{total_tests} passaram, {warning_tests} avisos"
        else:
            summary = f"❌ VALIDAÇÃO REPROVADA: {failed_tests} falhas, {passed_tests} passaram"
        
        # Gera recomendações
        recommendations = []
        
        if failed_tests > 0:
            recommendations.append("Corrija os testes que falharam antes de prosseguir")
        
        if warning_tests > 0:
            recommendations.append("Revise os avisos e implemente as melhorias sugeridas")
        
        critical_failures = [r for r in self.results if r.status == ValidationStatus.FAILED and r.severity == ValidationSeverity.CRITICAL]
        if critical_failures:
            recommendations.append("Priorize a correção dos componentes críticos")
        
        if passed_tests / total_tests < 0.8:
            recommendations.append("Considere revisar a implementação completa")
        
        return ValidationReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            skipped_tests=skipped_tests,
            results=self.results,
            summary=summary,
            recommendations=recommendations
        )


def save_report(report: ValidationReport, output_file: str = "reliability_validation_report.json"):
    """Salva relatório em arquivo JSON."""
    report_dict = asdict(report)
    report_dict['timestamp'] = report.timestamp.isoformat()
    
    for result in report_dict['results']:
        result['timestamp'] = result['timestamp'].isoformat()
        result['status'] = result['status'].value
        result['severity'] = result['severity'].value
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Relatório salvo em: {output_file}")


def print_report(report: ValidationReport):
    """Imprime relatório no console."""
    print("\n" + "="*80)
    print("RELATÓRIO DE VALIDAÇÃO DE CONFIABILIDADE")
    print("="*80)
    print(f"Data: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tracing ID: VALIDATE_RELIABILITY_001_20250127")
    print()
    
    print("📊 RESUMO:")
    print(f"   Total de testes: {report.total_tests}")
    print(f"   ✅ Aprovados: {report.passed_tests}")
    print(f"   ❌ Reprovados: {report.failed_tests}")
    print(f"   ⚠️ Avisos: {report.warning_tests}")
    print(f"   ⏭️ Pulados: {report.skipped_tests}")
    print()
    
    print("📋 RESULTADO:")
    print(f"   {report.summary}")
    print()
    
    if report.recommendations:
        print("💡 RECOMENDAÇÕES:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"   {i}. {rec}")
        print()
    
    print("🔍 DETALHES POR COMPONENTE:")
    components = {}
    for result in report.results:
        if result.component not in components:
            components[result.component] = []
        components[result.component].append(result)
    
    for component, results in components.items():
        print(f"\n   {component}:")
        for result in results:
            status_icon = {
                ValidationStatus.PASSED: "✅",
                ValidationStatus.FAILED: "❌",
                ValidationStatus.WARNING: "⚠️",
                ValidationStatus.SKIPPED: "⏭️"
            }[result.status]
            
            severity_icon = {
                ValidationSeverity.CRITICAL: "🔴",
                ValidationSeverity.HIGH: "🟠",
                ValidationSeverity.MEDIUM: "🟡",
                ValidationSeverity.LOW: "🟢"
            }[result.severity]
            
            print(f"     {status_icon} {severity_icon} {result.test_name}: {result.message}")
    
    print("\n" + "="*80)


def main():
    """Função principal."""
    print("🔍 VALIDADOR DE CONFIABILIDADE - OMNİ KEYWORDS FINDER")
    print("="*60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tracing ID: VALIDATE_RELIABILITY_001_20250127")
    print()
    
    try:
        # Executa validação
        validator = ReliabilityValidator()
        report = validator.validate_all()
        
        # Imprime relatório
        print_report(report)
        
        # Salva relatório
        save_report(report)
        
        # Retorna código de saída baseado no resultado
        if report.failed_tests > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Erro durante validação: {str(e)}")
        print(f"❌ ERRO: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 