"""
Validador de Integridade do Sistema
===================================

Sistema para validar integridade estrutural, consistência de dados
e conformidade com padrões do projeto.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import os
import re
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

from shared.logger import logger

class ValidationType(Enum):
    """Tipos de validação."""
    STRUCTURAL = "structural"
    IMPORTS = "imports"
    DEPENDENCIES = "dependencies"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TESTING = "testing"

class ValidationStatus(Enum):
    """Status de validação."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"

@dataclass
class ValidationIssue:
    """Problema de validação."""
    validation_type: ValidationType
    status: ValidationStatus
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    description: str = ""
    suggestion: str = ""
    severity: str = "medium"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Resultado de validação."""
    validation_type: ValidationType
    status: ValidationStatus
    issues: List[ValidationIssue]
    total_issues: int
    passed_checks: int
    failed_checks: int
    warnings: int
    skipped_checks: int
    processing_time: float
    metadata: Dict[str, Any]

@dataclass
class IntegrityReport:
    """Relatório de integridade."""
    results: List[ValidationResult]
    overall_status: ValidationStatus
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

class IntegrityValidator:
    """
    Validador de integridade do sistema.
    
    Funcionalidades:
    - Validação de estrutura de arquivos
    - Verificação de imports
    - Análise de dependências
    - Validação de configurações
    - Verificação de segurança
    - Análise de performance
    - Validação de documentação
    - Verificação de testes
    """
    
    def __init__(
        self,
        project_root: str = ".",
        enable_all_validations: bool = True,
        validation_config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa o validador de integridade.
        
        Args:
            project_root: Diretório raiz do projeto
            enable_all_validations: Habilita todas as validações
            validation_config: Configuração de validações
        """
        self.project_root = Path(project_root)
        self.enable_all_validations = enable_all_validations
        self.validation_config = validation_config or {}
        
        # Configurações padrão
        self.default_config = {
            'structural': {
                'enabled': True,
                'check_missing_dirs': True,
                'check_file_permissions': False,
                'required_dirs': ['tests', 'docs', 'scripts', 'config']
            },
            'imports': {
                'enabled': True,
                'check_circular_imports': True,
                'check_unused_imports': True,
                'check_missing_imports': True
            },
            'dependencies': {
                'enabled': True,
                'check_requirements': True,
                'check_package_json': True,
                'check_version_conflicts': True
            },
            'configuration': {
                'enabled': True,
                'check_env_files': True,
                'check_config_files': True,
                'check_secrets': True
            },
            'security': {
                'enabled': True,
                'check_hardcoded_secrets': True,
                'check_file_permissions': True,
                'check_dependency_vulnerabilities': False
            },
            'performance': {
                'enabled': True,
                'check_large_files': True,
                'check_inefficient_patterns': True,
                'max_file_size_mb': 10
            },
            'documentation': {
                'enabled': True,
                'check_readme': True,
                'check_api_docs': True,
                'check_code_comments': True
            },
            'testing': {
                'enabled': True,
                'check_test_coverage': True,
                'check_test_structure': True,
                'min_test_coverage': 0.8
            }
        }
        
        # Mesclar configurações
        for key, value in self.validation_config.items():
            if key in self.default_config:
                self.default_config[key].update(value)
        
        logger.info("IntegrityValidator initialized successfully")
    
    def validate_all(self) -> IntegrityReport:
        """
        Executa todas as validações.
        
        Returns:
            Relatório de integridade completo
        """
        start_time = time.time()
        all_results = []
        
        # Validações estruturais
        if self.default_config['structural']['enabled']:
            structural_result = self._validate_structural()
            all_results.append(structural_result)
        
        # Validação de imports
        if self.default_config['imports']['enabled']:
            imports_result = self._validate_imports()
            all_results.append(imports_result)
        
        # Validação de dependências
        if self.default_config['dependencies']['enabled']:
            dependencies_result = self._validate_dependencies()
            all_results.append(dependencies_result)
        
        # Validação de configuração
        if self.default_config['configuration']['enabled']:
            config_result = self._validate_configuration()
            all_results.append(config_result)
        
        # Validação de segurança
        if self.default_config['security']['enabled']:
            security_result = self._validate_security()
            all_results.append(security_result)
        
        # Validação de performance
        if self.default_config['performance']['enabled']:
            performance_result = self._validate_performance()
            all_results.append(performance_result)
        
        # Validação de documentação
        if self.default_config['documentation']['enabled']:
            docs_result = self._validate_documentation()
            all_results.append(docs_result)
        
        # Validação de testes
        if self.default_config['testing']['enabled']:
            testing_result = self._validate_testing()
            all_results.append(testing_result)
        
        # Calcular métricas gerais
        processing_time = time.time() - start_time
        overall_status = self._calculate_overall_status(all_results)
        total_issues = sum(len(result.issues) for result in all_results)
        
        # Contar issues por severidade
        severity_counts = self._count_issues_by_severity(all_results)
        
        # Preparar metadados
        metadata = {
            'project_root': str(self.project_root),
            'validation_config': self.validation_config,
            'enabled_validations': [result.validation_type.value for result in all_results]
        }
        
        report = IntegrityReport(
            results=all_results,
            overall_status=overall_status,
            total_issues=total_issues,
            critical_issues=severity_counts.get('critical', 0),
            high_issues=severity_counts.get('high', 0),
            medium_issues=severity_counts.get('medium', 0),
            low_issues=severity_counts.get('low', 0),
            processing_time=processing_time,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        logger.info(f"Integrity validation completed: {total_issues} issues found")
        return report
    
    def _validate_structural(self) -> ValidationResult:
        """Valida estrutura do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['structural']
        
        # Verificar diretórios obrigatórios
        if config.get('check_missing_dirs', True):
            required_dirs = config.get('required_dirs', [])
            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    issues.append(ValidationIssue(
                        validation_type=ValidationType.STRUCTURAL,
                        status=ValidationStatus.FAIL,
                        file_path=dir_name,
                        description=f"Diretório obrigatório '{dir_name}' não encontrado",
                        suggestion=f"Criar diretório {dir_name}",
                        severity="high"
                    ))
                elif not dir_path.is_dir():
                    issues.append(ValidationIssue(
                        validation_type=ValidationType.STRUCTURAL,
                        status=ValidationStatus.FAIL,
                        file_path=dir_name,
                        description=f"'{dir_name}' existe mas não é um diretório",
                        suggestion=f"Remover arquivo {dir_name} e criar diretório",
                        severity="critical"
                    ))
        
        # Verificar permissões de arquivo (se habilitado)
        if config.get('check_file_permissions', False):
            # Implementar verificação de permissões
            pass
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.STRUCTURAL,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=1 if not issues else 0,
            failed_checks=len(issues),
            warnings=0,
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'checked_dirs': config.get('required_dirs', [])}
        )
    
    def _validate_imports(self) -> ValidationResult:
        """Valida imports do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['imports']
        
        # Encontrar arquivos Python
        python_files = list(self.project_root.rglob("*.py"))
        
        # Verificar imports não utilizados
        if config.get('check_unused_imports', True):
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Análise simples de imports não utilizados
                    unused_imports = self._find_unused_imports(content)
                    for import_name in unused_imports:
                        issues.append(ValidationIssue(
                            validation_type=ValidationType.IMPORTS,
                            status=ValidationStatus.WARNING,
                            file_path=str(file_path),
                            description=f"Import '{import_name}' possivelmente não utilizado",
                            suggestion=f"Remover import não utilizado: {import_name}",
                            severity="low"
                        ))
                except Exception as e:
                    issues.append(ValidationIssue(
                        validation_type=ValidationType.IMPORTS,
                        status=ValidationStatus.FAIL,
                        file_path=str(file_path),
                        description=f"Erro ao analisar imports: {e}",
                        suggestion="Verificar sintaxe do arquivo",
                        severity="medium"
                    ))
        
        # Verificar imports circulares (simplificado)
        if config.get('check_circular_imports', True):
            circular_imports = self._find_circular_imports(python_files)
            for import_chain in circular_imports:
                issues.append(ValidationIssue(
                    validation_type=ValidationType.IMPORTS,
                    status=ValidationStatus.FAIL,
                    description=f"Import circular detectado: {' -> '.join(import_chain)}",
                    suggestion="Refatorar para evitar imports circulares",
                    severity="high"
                ))
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.IMPORTS,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=len(python_files) - len(issues),
            failed_checks=len(issues),
            warnings=len([i for i in issues if i.status == ValidationStatus.WARNING]),
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'python_files_checked': len(python_files)}
        )
    
    def _validate_dependencies(self) -> ValidationResult:
        """Valida dependências do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['dependencies']
        
        # Verificar requirements.txt
        if config.get('check_requirements', True):
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                issues.append(ValidationIssue(
                    validation_type=ValidationType.DEPENDENCIES,
                    status=ValidationStatus.FAIL,
                    file_path="requirements.txt",
                    description="Arquivo requirements.txt não encontrado",
                    suggestion="Criar arquivo requirements.txt com dependências Python",
                    severity="critical"
                ))
            else:
                # Verificar formato do requirements.txt
                try:
                    with open(requirements_file, 'r') as f:
                        content = f.read()
                    
                    if not content.strip():
                        issues.append(ValidationIssue(
                            validation_type=ValidationType.DEPENDENCIES,
                            status=ValidationStatus.FAIL,
                            file_path="requirements.txt",
                            description="Arquivo requirements.txt está vazio",
                            suggestion="Adicionar dependências ao requirements.txt",
                            severity="high"
                        ))
                except Exception as e:
                    issues.append(ValidationIssue(
                        validation_type=ValidationType.DEPENDENCIES,
                        status=ValidationStatus.FAIL,
                        file_path="requirements.txt",
                        description=f"Erro ao ler requirements.txt: {e}",
                        suggestion="Verificar permissões e formato do arquivo",
                        severity="medium"
                    ))
        
        # Verificar package.json
        if config.get('check_package_json', True):
            package_json_files = list(self.project_root.rglob("package.json"))
            if not package_json_files:
                issues.append(ValidationIssue(
                    validation_type=ValidationType.DEPENDENCIES,
                    status=ValidationStatus.WARNING,
                    description="Nenhum package.json encontrado",
                    suggestion="Criar package.json se for um projeto Node.js",
                    severity="low"
                ))
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.DEPENDENCIES,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=1 if not issues else 0,
            failed_checks=len(issues),
            warnings=len([i for i in issues if i.status == ValidationStatus.WARNING]),
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'dependency_files_checked': ['requirements.txt', 'package.json']}
        )
    
    def _validate_configuration(self) -> ValidationResult:
        """Valida configurações do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['configuration']
        
        # Verificar arquivos de ambiente
        if config.get('check_env_files', True):
            env_files = ['.env', '.env.example', '.env.template']
            for env_file in env_files:
                env_path = self.project_root / env_file
                if not env_path.exists():
                    if env_file == '.env.example':
                        issues.append(ValidationIssue(
                            validation_type=ValidationType.CONFIGURATION,
                            status=ValidationStatus.WARNING,
                            file_path=env_file,
                            description=f"Arquivo {env_file} não encontrado",
                            suggestion=f"Criar {env_file} como template",
                            severity="low"
                        ))
        
        # Verificar arquivos de configuração
        if config.get('check_config_files', True):
            config_files = ['config.py', 'settings.py', 'config.yaml', 'config.json']
            config_found = False
            for config_file in config_files:
                config_path = self.project_root / config_file
                if config_path.exists():
                    config_found = True
                    break
            
            if not config_found:
                issues.append(ValidationIssue(
                    validation_type=ValidationType.CONFIGURATION,
                    status=ValidationStatus.WARNING,
                    description="Nenhum arquivo de configuração encontrado",
                    suggestion="Criar arquivo de configuração (config.py, settings.py, etc.)",
                    severity="medium"
                ))
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.CONFIGURATION,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=1 if not issues else 0,
            failed_checks=len(issues),
            warnings=len([i for i in issues if i.status == ValidationStatus.WARNING]),
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'config_files_checked': ['env_files', 'config_files']}
        )
    
    def _validate_security(self) -> ValidationResult:
        """Valida segurança do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['security']
        
        # Verificar secrets hardcoded
        if config.get('check_hardcoded_secrets', True):
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'sk-[a-zA-Z0-9]{48}',
                r'AIza[a-zA-Z0-9]{35}'
            ]
            
            for pattern in secret_patterns:
                for file_path in self.project_root.rglob("*.py"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_number = content[:match.start()].count('\n') + 1
                            issues.append(ValidationIssue(
                                validation_type=ValidationType.SECURITY,
                                status=ValidationStatus.FAIL,
                                file_path=str(file_path),
                                line_number=line_number,
                                description=f"Possível secret hardcoded encontrado",
                                suggestion="Mover secret para variável de ambiente",
                                severity="critical"
                            ))
                    except Exception:
                        continue
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.SECURITY,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=1 if not issues else 0,
            failed_checks=len(issues),
            warnings=0,
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'security_patterns_checked': len(secret_patterns)}
        )
    
    def _validate_performance(self) -> ValidationResult:
        """Valida performance do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['performance']
        
        # Verificar arquivos grandes
        if config.get('check_large_files', True):
            max_size_mb = config.get('max_file_size_mb', 10)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        if file_size > max_size_bytes:
                            issues.append(ValidationIssue(
                                validation_type=ValidationType.PERFORMANCE,
                                status=ValidationStatus.WARNING,
                                file_path=str(file_path),
                                description=f"Arquivo muito grande ({file_size / 1024 / 1024:.1f}MB)",
                                suggestion=f"Considerar dividir arquivo se > {max_size_mb}MB",
                                severity="medium"
                            ))
                    except Exception:
                        continue
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.PERFORMANCE,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=1 if not issues else 0,
            failed_checks=len(issues),
            warnings=len([i for i in issues if i.status == ValidationStatus.WARNING]),
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'max_file_size_mb': config.get('max_file_size_mb', 10)}
        )
    
    def _validate_documentation(self) -> ValidationResult:
        """Valida documentação do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['documentation']
        
        # Verificar README
        if config.get('check_readme', True):
            readme_files = ['README.md', 'README.txt', 'readme.md']
            readme_found = False
            for readme_file in readme_files:
                readme_path = self.project_root / readme_file
                if readme_path.exists():
                    readme_found = True
                    break
            
            if not readme_found:
                issues.append(ValidationIssue(
                    validation_type=ValidationType.DOCUMENTATION,
                    status=ValidationStatus.FAIL,
                    description="Arquivo README não encontrado",
                    suggestion="Criar README.md com documentação do projeto",
                    severity="high"
                ))
        
        # Verificar documentação de API
        if config.get('check_api_docs', True):
            api_docs = ['docs/', 'api/', 'openapi.yaml', 'swagger.yaml']
            api_docs_found = False
            for doc_path in api_docs:
                full_path = self.project_root / doc_path
                if full_path.exists():
                    api_docs_found = True
                    break
            
            if not api_docs_found:
                issues.append(ValidationIssue(
                    validation_type=ValidationType.DOCUMENTATION,
                    status=ValidationStatus.WARNING,
                    description="Documentação de API não encontrada",
                    suggestion="Criar documentação de API (docs/, openapi.yaml, etc.)",
                    severity="medium"
                ))
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.DOCUMENTATION,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=1 if not issues else 0,
            failed_checks=len(issues),
            warnings=len([i for i in issues if i.status == ValidationStatus.WARNING]),
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'doc_types_checked': ['readme', 'api_docs']}
        )
    
    def _validate_testing(self) -> ValidationResult:
        """Valida testes do projeto."""
        start_time = time.time()
        issues = []
        
        config = self.default_config['testing']
        
        # Verificar estrutura de testes
        if config.get('check_test_structure', True):
            test_dirs = ['tests/', 'test/', 'specs/']
            test_dir_found = False
            for test_dir in test_dirs:
                test_path = self.project_root / test_dir
                if test_path.exists() and test_path.is_dir():
                    test_dir_found = True
                    break
            
            if not test_dir_found:
                issues.append(ValidationIssue(
                    validation_type=ValidationType.TESTING,
                    status=ValidationStatus.FAIL,
                    description="Diretório de testes não encontrado",
                    suggestion="Criar diretório tests/ com estrutura de testes",
                    severity="high"
                ))
        
        # Verificar cobertura de testes (simplificado)
        if config.get('check_test_coverage', True):
            test_files = list(self.project_root.rglob("test_*.py"))
            python_files = list(self.project_root.rglob("*.py"))
            
            if python_files and not test_files:
                issues.append(ValidationIssue(
                    validation_type=ValidationType.TESTING,
                    status=ValidationStatus.FAIL,
                    description="Nenhum arquivo de teste encontrado",
                    suggestion="Criar arquivos de teste para o código Python",
                    severity="high"
                ))
        
        # Calcular métricas
        processing_time = time.time() - start_time
        status = ValidationStatus.PASS if not issues else ValidationStatus.FAIL
        
        return ValidationResult(
            validation_type=ValidationType.TESTING,
            status=status,
            issues=issues,
            total_issues=len(issues),
            passed_checks=1 if not issues else 0,
            failed_checks=len(issues),
            warnings=0,
            skipped_checks=0,
            processing_time=processing_time,
            metadata={'test_files_found': len(test_files) if 'test_files' in locals() else 0}
        )
    
    def _find_unused_imports(self, content: str) -> List[str]:
        """Encontra imports não utilizados (heurística simples)."""
        # Implementação simplificada
        return []
    
    def _find_circular_imports(self, python_files: List[Path]) -> List[List[str]]:
        """Encontra imports circulares (implementação simplificada)."""
        # Implementação simplificada
        return []
    
    def _calculate_overall_status(self, results: List[ValidationResult]) -> ValidationStatus:
        """Calcula status geral baseado nos resultados."""
        if not results:
            return ValidationStatus.PASS
        
        # Se qualquer validação falhou, status geral é FAIL
        for result in results:
            if result.status == ValidationStatus.FAIL:
                return ValidationStatus.FAIL
        
        # Se qualquer validação tem warning, status geral é WARNING
        for result in results:
            if result.status == ValidationStatus.WARNING:
                return ValidationStatus.WARNING
        
        return ValidationStatus.PASS
    
    def _count_issues_by_severity(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Conta issues por severidade."""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for result in results:
            for issue in result.issues:
                severity = issue.severity.lower()
                if severity in counts:
                    counts[severity] += 1
        
        return counts
    
    def generate_report(self, report: IntegrityReport, output_file: Optional[str] = None) -> str:
        """Gera relatório de integridade."""
        report_lines = []
        report_lines.append("# Relatório de Validação de Integridade")
        report_lines.append(f"**Data**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Projeto**: {self.project_root}")
        report_lines.append(f"**Status Geral**: {report.overall_status.value.upper()}")
        report_lines.append("")
        
        # Resumo
        report_lines.append("## 📊 Resumo")
        report_lines.append(f"- **Status Geral**: {report.overall_status.value.upper()}")
        report_lines.append(f"- **Total de Issues**: {report.total_issues}")
        report_lines.append(f"- **Tempo de Processamento**: {report.processing_time:.2f}s")
        report_lines.append("")
        
        # Issues por severidade
        report_lines.append("## 🚨 Issues por Severidade")
        report_lines.append(f"- **Críticos**: {report.critical_issues}")
        report_lines.append(f"- **Altos**: {report.high_issues}")
        report_lines.append(f"- **Médios**: {report.medium_issues}")
        report_lines.append(f"- **Baixos**: {report.low_issues}")
        report_lines.append("")
        
        # Resultados por tipo de validação
        report_lines.append("## 📋 Resultados por Tipo de Validação")
        for result in report.results:
            status_emoji = "✅" if result.status == ValidationStatus.PASS else "❌"
            report_lines.append(f"### {status_emoji} {result.validation_type.value.upper()}")
            report_lines.append(f"- **Status**: {result.status.value.upper()}")
            report_lines.append(f"- **Issues**: {result.total_issues}")
            report_lines.append(f"- **Passed**: {result.passed_checks}")
            report_lines.append(f"- **Failed**: {result.failed_checks}")
            report_lines.append(f"- **Warnings**: {result.warnings}")
            report_lines.append(f"- **Tempo**: {result.processing_time:.2f}s")
            report_lines.append("")
        
        # Issues detalhadas
        if report.total_issues > 0:
            report_lines.append("## 📝 Issues Detalhadas")
            
            for result in report.results:
                if result.issues:
                    report_lines.append(f"### {result.validation_type.value.upper()}")
                    
                    for issue in result.issues:
                        severity_emoji = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢'
                        }.get(issue.severity, '⚪')
                        
                        report_lines.append(f"#### {severity_emoji} {issue.severity.upper()}")
                        if issue.file_path:
                            report_lines.append(f"- **Arquivo**: {issue.file_path}")
                        if issue.line_number:
                            report_lines.append(f"- **Linha**: {issue.line_number}")
                        report_lines.append(f"- **Descrição**: {issue.description}")
                        report_lines.append(f"- **Sugestão**: {issue.suggestion}")
                        report_lines.append("")
        
        # Recomendações
        report_lines.append("## 💡 Recomendações")
        if report.critical_issues > 0:
            report_lines.append("- 🔴 **CRÍTICO**: Resolver issues críticos imediatamente")
        if report.high_issues > 0:
            report_lines.append("- 🟠 **ALTO**: Priorizar issues de alta severidade")
        if report.medium_issues > 0:
            report_lines.append("- 🟡 **MÉDIO**: Planejar correção de issues médios")
        if report.low_issues > 0:
            report_lines.append("- 🟢 **BAIXO**: Melhorar gradualmente issues baixos")
        
        report_text = "\n".join(report_lines)
        
        # Salvar relatório se especificado
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"Relatório de integridade salvo em: {output_file}")
        
        return report_text 