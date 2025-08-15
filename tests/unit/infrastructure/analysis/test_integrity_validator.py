"""
Testes Unitários para IntegrityValidator
========================================

Testes para o sistema de validação de integridade do projeto.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.2
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from infrastructure.analysis.integrity_validator import (
    IntegrityValidator,
    ValidationType,
    ValidationStatus,
    ValidationIssue,
    ValidationResult,
    IntegrityReport
)


class TestIntegrityValidator:
    """Testes para IntegrityValidator."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Cria diretório temporário para projeto de teste."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir()
            yield project_dir
    
    @pytest.fixture
    def integrity_validator(self, temp_project_dir):
        """Cria instância do IntegrityValidator para testes."""
        return IntegrityValidator(
            project_root=str(temp_project_dir),
            enable_all_validations=True
        )
    
    @pytest.fixture
    def sample_python_file(self, temp_project_dir):
        """Cria arquivo Python de exemplo para testes."""
        file_path = temp_project_dir / "test_module.py"
        content = '''
"""
Módulo de teste para validação de integridade.
"""

import os
import sys

def test_function(param):
    """Função de teste."""
    return param * 2

class TestClass:
    """Classe de teste."""
    
    def __init__(self):
        self.value = 42
'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        validator = IntegrityValidator()
        
        assert validator.project_root == Path(".")
        assert validator.enable_all_validations is True
        assert validator.validation_config == {}
        assert "structural" in validator.default_config
        assert "imports" in validator.default_config
    
    def test_init_custom_values(self, temp_project_dir):
        """Testa inicialização com valores customizados."""
        custom_config = {
            'structural': {'enabled': False},
            'imports': {'enabled': True}
        }
        
        validator = IntegrityValidator(
            project_root=str(temp_project_dir),
            enable_all_validations=False,
            validation_config=custom_config
        )
        
        assert validator.project_root == temp_project_dir
        assert validator.enable_all_validations is False
        assert validator.validation_config == custom_config
        assert validator.default_config['structural']['enabled'] is False
    
    def test_validate_structural_success(self, integrity_validator, temp_project_dir):
        """Testa validação estrutural bem-sucedida."""
        # Criar diretórios obrigatórios
        for dir_name in ['tests', 'docs', 'scripts', 'config']:
            (temp_project_dir / dir_name).mkdir()
        
        result = integrity_validator._validate_structural()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.STRUCTURAL
        assert result.status == ValidationStatus.PASS
        assert len(result.issues) == 0
        assert result.passed_checks == 1
        assert result.failed_checks == 0
    
    def test_validate_structural_missing_dirs(self, integrity_validator):
        """Testa validação estrutural com diretórios faltantes."""
        result = integrity_validator._validate_structural()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.STRUCTURAL
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
        assert result.passed_checks == 0
        assert result.failed_checks > 0
        
        # Verificar que issues são sobre diretórios faltantes
        issue_types = [issue.description for issue in result.issues]
        assert any("Diretório obrigatório" in desc for desc in issue_types)
    
    def test_validate_imports_success(self, integrity_validator, sample_python_file):
        """Testa validação de imports bem-sucedida."""
        result = integrity_validator._validate_imports()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.IMPORTS
        assert result.passed_checks >= 1  # Pelo menos o arquivo de exemplo
        assert result.processing_time > 0
    
    def test_validate_imports_with_issues(self, integrity_validator, temp_project_dir):
        """Testa validação de imports com problemas."""
        # Criar arquivo com sintaxe inválida
        invalid_file = temp_project_dir / "invalid.py"
        with open(invalid_file, 'w') as f:
            f.write("import invalid syntax")
        
        result = integrity_validator._validate_imports()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.IMPORTS
        assert result.failed_checks > 0
    
    def test_validate_dependencies_success(self, integrity_validator, temp_project_dir):
        """Testa validação de dependências bem-sucedida."""
        # Criar requirements.txt
        requirements_file = temp_project_dir / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write("flask>=2.3.0\nrequests>=2.32.0")
        
        result = integrity_validator._validate_dependencies()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.DEPENDENCIES
        assert result.status == ValidationStatus.PASS
        assert len(result.issues) == 0
    
    def test_validate_dependencies_missing_requirements(self, integrity_validator):
        """Testa validação de dependências sem requirements.txt."""
        result = integrity_validator._validate_dependencies()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.DEPENDENCIES
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
        
        # Verificar que issue é sobre requirements.txt faltante
        issue_descriptions = [issue.description for issue in result.issues]
        assert any("requirements.txt" in desc for desc in issue_descriptions)
    
    def test_validate_dependencies_empty_requirements(self, integrity_validator, temp_project_dir):
        """Testa validação de dependências com requirements.txt vazio."""
        # Criar requirements.txt vazio
        requirements_file = temp_project_dir / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write("")
        
        result = integrity_validator._validate_dependencies()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.DEPENDENCIES
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
        
        # Verificar que issue é sobre requirements.txt vazio
        issue_descriptions = [issue.description for issue in result.issues]
        assert any("vazio" in desc for desc in issue_descriptions)
    
    def test_validate_configuration_success(self, integrity_validator, temp_project_dir):
        """Testa validação de configuração bem-sucedida."""
        # Criar arquivos de configuração
        config_file = temp_project_dir / "config.py"
        with open(config_file, 'w') as f:
            f.write("# Configuração do projeto")
        
        env_example = temp_project_dir / ".env.example"
        with open(env_example, 'w') as f:
            f.write("# Variáveis de ambiente")
        
        result = integrity_validator._validate_configuration()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.CONFIGURATION
        assert result.status == ValidationStatus.PASS
        assert len(result.issues) == 0
    
    def test_validate_configuration_missing_files(self, integrity_validator):
        """Testa validação de configuração com arquivos faltantes."""
        result = integrity_validator._validate_configuration()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.CONFIGURATION
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
    
    def test_validate_security_success(self, integrity_validator, sample_python_file):
        """Testa validação de segurança bem-sucedida."""
        result = integrity_validator._validate_security()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.SECURITY
        assert result.processing_time > 0
    
    def test_validate_security_with_hardcoded_secrets(self, integrity_validator, temp_project_dir):
        """Testa validação de segurança com secrets hardcoded."""
        # Criar arquivo com secret hardcoded
        secret_file = temp_project_dir / "secret.py"
        with open(secret_file, 'w') as f:
            f.write('password = "admin123"\napi_key = "sk-1234567890abcdef"')
        
        result = integrity_validator._validate_security()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.SECURITY
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
        
        # Verificar que issues são sobre secrets hardcoded
        issue_descriptions = [issue.description for issue in result.issues]
        assert any("secret hardcoded" in desc.lower() for desc in issue_descriptions)
    
    def test_validate_performance_success(self, integrity_validator, sample_python_file):
        """Testa validação de performance bem-sucedida."""
        result = integrity_validator._validate_performance()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.PERFORMANCE
        assert result.processing_time > 0
    
    def test_validate_performance_large_file(self, integrity_validator, temp_project_dir):
        """Testa validação de performance com arquivo grande."""
        # Criar arquivo grande
        large_file = temp_project_dir / "large_file.py"
        large_content = "x" * (15 * 1024 * 1024)  # 15MB
        
        with open(large_file, 'w') as f:
            f.write(large_content)
        
        result = integrity_validator._validate_performance()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.PERFORMANCE
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
        
        # Verificar que issues são sobre arquivo grande
        issue_descriptions = [issue.description for issue in result.issues]
        assert any("grande" in desc.lower() for desc in issue_descriptions)
    
    def test_validate_documentation_success(self, integrity_validator, temp_project_dir):
        """Testa validação de documentação bem-sucedida."""
        # Criar README
        readme_file = temp_project_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write("# Projeto de Teste\n\nDocumentação do projeto.")
        
        # Criar diretório de docs
        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir()
        
        result = integrity_validator._validate_documentation()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.DOCUMENTATION
        assert result.status == ValidationStatus.PASS
        assert len(result.issues) == 0
    
    def test_validate_documentation_missing_files(self, integrity_validator):
        """Testa validação de documentação com arquivos faltantes."""
        result = integrity_validator._validate_documentation()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.DOCUMENTATION
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
        
        # Verificar que issues são sobre documentação faltante
        issue_descriptions = [issue.description for issue in result.issues]
        assert any("README" in desc for desc in issue_descriptions)
    
    def test_validate_testing_success(self, integrity_validator, temp_project_dir):
        """Testa validação de testes bem-sucedida."""
        # Criar diretório de testes
        tests_dir = temp_project_dir / "tests"
        tests_dir.mkdir()
        
        # Criar arquivo de teste
        test_file = tests_dir / "test_example.py"
        with open(test_file, 'w') as f:
            f.write("def test_example(): pass")
        
        result = integrity_validator._validate_testing()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.TESTING
        assert result.status == ValidationStatus.PASS
        assert len(result.issues) == 0
    
    def test_validate_testing_missing_tests(self, integrity_validator):
        """Testa validação de testes sem estrutura de testes."""
        result = integrity_validator._validate_testing()
        
        assert isinstance(result, ValidationResult)
        assert result.validation_type == ValidationType.TESTING
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) > 0
        
        # Verificar que issues são sobre testes faltantes
        issue_descriptions = [issue.description for issue in result.issues]
        assert any("teste" in desc.lower() for desc in issue_descriptions)
    
    def test_calculate_overall_status_all_pass(self, integrity_validator):
        """Testa cálculo de status geral com todos passando."""
        results = [
            ValidationResult(
                validation_type=ValidationType.STRUCTURAL,
                status=ValidationStatus.PASS,
                issues=[],
                total_issues=0,
                passed_checks=1,
                failed_checks=0,
                warnings=0,
                skipped_checks=0,
                processing_time=1.0,
                metadata={}
            )
        ]
        
        status = integrity_validator._calculate_overall_status(results)
        assert status == ValidationStatus.PASS
    
    def test_calculate_overall_status_with_fail(self, integrity_validator):
        """Testa cálculo de status geral com falha."""
        results = [
            ValidationResult(
                validation_type=ValidationType.STRUCTURAL,
                status=ValidationStatus.FAIL,
                issues=[ValidationIssue(ValidationType.STRUCTURAL, ValidationStatus.FAIL, description="Test")],
                total_issues=1,
                passed_checks=0,
                failed_checks=1,
                warnings=0,
                skipped_checks=0,
                processing_time=1.0,
                metadata={}
            )
        ]
        
        status = integrity_validator._calculate_overall_status(results)
        assert status == ValidationStatus.FAIL
    
    def test_calculate_overall_status_with_warning(self, integrity_validator):
        """Testa cálculo de status geral com warning."""
        results = [
            ValidationResult(
                validation_type=ValidationType.STRUCTURAL,
                status=ValidationStatus.WARNING,
                issues=[ValidationIssue(ValidationType.STRUCTURAL, ValidationStatus.WARNING, description="Test")],
                total_issues=1,
                passed_checks=0,
                failed_checks=0,
                warnings=1,
                skipped_checks=0,
                processing_time=1.0,
                metadata={}
            )
        ]
        
        status = integrity_validator._calculate_overall_status(results)
        assert status == ValidationStatus.WARNING
    
    def test_count_issues_by_severity(self, integrity_validator):
        """Testa contagem de issues por severidade."""
        results = [
            ValidationResult(
                validation_type=ValidationType.STRUCTURAL,
                status=ValidationStatus.FAIL,
                issues=[
                    ValidationIssue(ValidationType.STRUCTURAL, ValidationStatus.FAIL, description="Critical", severity="critical"),
                    ValidationIssue(ValidationType.STRUCTURAL, ValidationStatus.FAIL, description="High", severity="high"),
                    ValidationIssue(ValidationType.STRUCTURAL, ValidationStatus.WARNING, description="Medium", severity="medium"),
                    ValidationIssue(ValidationType.STRUCTURAL, ValidationStatus.WARNING, description="Low", severity="low")
                ],
                total_issues=4,
                passed_checks=0,
                failed_checks=2,
                warnings=2,
                skipped_checks=0,
                processing_time=1.0,
                metadata={}
            )
        ]
        
        counts = integrity_validator._count_issues_by_severity(results)
        
        assert counts['critical'] == 1
        assert counts['high'] == 1
        assert counts['medium'] == 1
        assert counts['low'] == 1
    
    def test_validate_all_integration(self, integrity_validator, temp_project_dir):
        """Testa validação completa do projeto."""
        # Criar estrutura básica
        (temp_project_dir / "tests").mkdir()
        (temp_project_dir / "docs").mkdir()
        
        requirements_file = temp_project_dir / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write("flask>=2.3.0")
        
        readme_file = temp_project_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write("# Test Project")
        
        result = integrity_validator.validate_all()
        
        assert isinstance(result, IntegrityReport)
        assert result.overall_status in [ValidationStatus.PASS, ValidationStatus.WARNING, ValidationStatus.FAIL]
        assert result.total_issues >= 0
        assert result.processing_time > 0
        assert len(result.results) > 0
    
    def test_generate_report(self, integrity_validator, temp_project_dir):
        """Testa geração de relatório."""
        # Criar resultado de teste
        result = ValidationResult(
            validation_type=ValidationType.STRUCTURAL,
            status=ValidationStatus.FAIL,
            issues=[
                ValidationIssue(
                    validation_type=ValidationType.STRUCTURAL,
                    status=ValidationStatus.FAIL,
                    description="Diretório tests não encontrado",
                    suggestion="Criar diretório tests",
                    severity="high"
                )
            ],
            total_issues=1,
            passed_checks=0,
            failed_checks=1,
            warnings=0,
            skipped_checks=0,
            processing_time=1.0,
            metadata={}
        )
        
        report = IntegrityReport(
            results=[result],
            overall_status=ValidationStatus.FAIL,
            total_issues=1,
            critical_issues=0,
            high_issues=1,
            medium_issues=0,
            low_issues=0,
            processing_time=1.0,
            timestamp=integrity_validator.validate_all().timestamp,
            metadata={}
        )
        
        report_text = integrity_validator.generate_report(report)
        
        assert isinstance(report_text, str)
        assert "Relatório de Validação de Integridade" in report_text
        assert "1" in report_text  # Total de issues
        assert "high" in report_text.lower()  # Severidade


class TestValidationIssue:
    """Testes para ValidationIssue."""
    
    def test_validation_issue_creation(self):
        """Testa criação de ValidationIssue."""
        issue = ValidationIssue(
            validation_type=ValidationType.STRUCTURAL,
            status=ValidationStatus.FAIL,
            file_path="test.py",
            line_number=10,
            description="Teste de issue",
            suggestion="Corrigir problema",
            severity="high"
        )
        
        assert issue.validation_type == ValidationType.STRUCTURAL
        assert issue.status == ValidationStatus.FAIL
        assert issue.file_path == "test.py"
        assert issue.line_number == 10
        assert issue.description == "Teste de issue"
        assert issue.suggestion == "Corrigir problema"
        assert issue.severity == "high"


class TestValidationResult:
    """Testes para ValidationResult."""
    
    def test_validation_result_creation(self):
        """Testa criação de ValidationResult."""
        issues = [
            ValidationIssue(ValidationType.STRUCTURAL, ValidationStatus.FAIL, description="Test")
        ]
        
        result = ValidationResult(
            validation_type=ValidationType.STRUCTURAL,
            status=ValidationStatus.FAIL,
            issues=issues,
            total_issues=1,
            passed_checks=0,
            failed_checks=1,
            warnings=0,
            skipped_checks=0,
            processing_time=1.5,
            metadata={"test": "data"}
        )
        
        assert result.validation_type == ValidationType.STRUCTURAL
        assert result.status == ValidationStatus.FAIL
        assert len(result.issues) == 1
        assert result.total_issues == 1
        assert result.passed_checks == 0
        assert result.failed_checks == 1
        assert result.processing_time == 1.5
        assert result.metadata["test"] == "data"


class TestIntegrityReport:
    """Testes para IntegrityReport."""
    
    def test_integrity_report_creation(self):
        """Testa criação de IntegrityReport."""
        results = [
            ValidationResult(
                validation_type=ValidationType.STRUCTURAL,
                status=ValidationStatus.FAIL,
                issues=[],
                total_issues=0,
                passed_checks=1,
                failed_checks=0,
                warnings=0,
                skipped_checks=0,
                processing_time=1.0,
                metadata={}
            )
        ]
        
        report = IntegrityReport(
            results=results,
            overall_status=ValidationStatus.PASS,
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
            processing_time=1.0,
            timestamp=IntegrityValidator().validate_all().timestamp,
            metadata={"test": "data"}
        )
        
        assert len(report.results) == 1
        assert report.overall_status == ValidationStatus.PASS
        assert report.total_issues == 0
        assert report.processing_time == 1.0
        assert report.metadata["test"] == "data" 