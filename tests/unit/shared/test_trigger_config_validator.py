from typing import Dict, List, Optional, Any
"""
Testes Unitários para TriggerConfigValidator

Tracing ID: TEST_TRIGGER_CONFIG_VALIDATOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação Inicial

Responsável: Sistema de Documentação Enterprise
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from shared.trigger_config_validator import (
    TriggerConfigValidator, 
    ValidationResult, 
    ValidationSeverity,
    TriggerConfig
)


class TestTriggerConfigValidator:
    """Testes para TriggerConfigValidator"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.validator = TriggerConfigValidator()
        
        # Configuração de exemplo válida
        self.valid_config = {
            "sensitive_files": [
                ".env",
                "config/secrets.json",
                "keys/private.pem"
            ],
            "auto_rerun_patterns": [
                r"\.py$",
                r"\.md$",
                r"test_.*\.py$"
            ],
            "exclusion_patterns": [
                r"__pycache__",
                r"\.git",
                r"node_modules"
            ],
            "semantic_threshold": 0.85,
            "rollback_config": {
                "enabled": True,
                "max_snapshots": 10,
                "auto_rollback_threshold": 0.7
            },
            "compliance_config": {
                "pci_dss": {
                    "enabled": True,
                    "strict_mode": False
                },
                "lgpd": {
                    "enabled": True,
                    "strict_mode": True
                }
            }
        }
    
    def test_load_config_success(self):
        """Teste de carregamento bem-sucedido de configuração"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.valid_config))):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.validator.load_config()
                
                assert result.is_valid is True
                assert result.severity == ValidationSeverity.INFO
                assert "sucesso" in result.message.lower()
                assert self.validator.config is not None
                assert len(self.validator.config.sensitive_files) == 3
                assert self.validator.config.semantic_threshold == 0.85
    
    def test_load_config_file_not_found(self):
        """Teste de carregamento com arquivo não encontrado"""
        with patch('pathlib.Path.exists', return_value=False):
            result = self.validator.load_config()
            
            assert result.is_valid is False
            assert result.severity == ValidationSeverity.ERROR
            assert "não encontrado" in result.message
    
    def test_load_config_invalid_json(self):
        """Teste de carregamento com JSON inválido"""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.validator.load_config()
                
                assert result.is_valid is False
                assert result.severity == ValidationSeverity.ERROR
                assert "JSON" in result.message
    
    def test_load_config_missing_fields(self):
        """Teste de carregamento com campos obrigatórios ausentes"""
        incomplete_config = {"sensitive_files": []}
        
        with patch('builtins.open', mock_open(read_data=json.dumps(incomplete_config))):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.validator.load_config()
                
                assert result.is_valid is False
                assert result.severity == ValidationSeverity.ERROR
                assert "obrigatórios ausentes" in result.message
                assert result.details is not None
                assert "missing_fields" in result.details
    
    def test_validate_sensitive_files_success(self):
        """Teste de validação bem-sucedida de arquivos sensíveis"""
        self.validator.config = TriggerConfig(
            sensitive_files=[".env", "config/secrets.json"],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            result = self.validator.validate_sensitive_files()
            
            assert result.is_valid is True
            assert result.severity == ValidationSeverity.INFO
            assert "aprovada" in result.message
    
    def test_validate_sensitive_files_empty_list(self):
        """Teste de validação com lista vazia de arquivos sensíveis"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_sensitive_files()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "vazia" in result.message
    
    def test_validate_sensitive_files_not_found(self):
        """Teste de validação com arquivo sensível não encontrado"""
        self.validator.config = TriggerConfig(
            sensitive_files=["arquivo_inexistente.txt"],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        with patch('pathlib.Path.exists', return_value=False):
            result = self.validator.validate_sensitive_files()
            
            assert result.is_valid is False
            assert result.severity == ValidationSeverity.WARNING
            assert "não encontrado" in result.message
    
    def test_validate_patterns_success(self):
        """Teste de validação bem-sucedida de padrões"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[r"\.py$", r"\.md$"],
            exclusion_patterns=[r"__pycache__", r"\.git"],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_patterns()
        
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO
        assert "aprovada" in result.message
    
    def test_validate_patterns_invalid_regex(self):
        """Teste de validação com regex inválido"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[r"invalid[regex"],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_patterns()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "inválido" in result.message
    
    def test_validate_patterns_duplicate(self):
        """Teste de validação com padrões duplicados"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[r"\.py$"],
            exclusion_patterns=[r"\.py$"],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_patterns()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "duplicado" in result.message
    
    def test_validate_semantic_threshold_success(self):
        """Teste de validação bem-sucedida de threshold semântico"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_semantic_threshold()
        
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO
        assert "válido" in result.message
    
    def test_validate_semantic_threshold_invalid_type(self):
        """Teste de validação com tipo inválido de threshold"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold="invalid",
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_semantic_threshold()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert "número" in result.message
    
    def test_validate_semantic_threshold_out_of_range(self):
        """Teste de validação com threshold fora do range"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=1.5,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_semantic_threshold()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert "entre 0.0 e 1.0" in result.message
    
    def test_validate_semantic_threshold_too_low(self):
        """Teste de validação com threshold muito baixo"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.5,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_semantic_threshold()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "muito baixo" in result.message
    
    def test_validate_semantic_threshold_too_high(self):
        """Teste de validação com threshold muito alto"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.98,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_semantic_threshold()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "muito alto" in result.message
    
    def test_validate_rollback_config_success(self):
        """Teste de validação bem-sucedida de configuração de rollback"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={
                "enabled": True,
                "max_snapshots": 10,
                "auto_rollback_threshold": 0.7
            },
            compliance_config={}
        )
        
        result = self.validator.validate_rollback_config()
        
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO
        assert "válida" in result.message
    
    def test_validate_rollback_config_missing_fields(self):
        """Teste de validação com campos obrigatórios ausentes"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={"enabled": True},
            compliance_config={}
        )
        
        result = self.validator.validate_rollback_config()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "obrigatório ausente" in result.message
    
    def test_validate_rollback_config_invalid_types(self):
        """Teste de validação com tipos inválidos"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={
                "enabled": "invalid",
                "max_snapshots": -1,
                "auto_rollback_threshold": 1.5
            },
            compliance_config={}
        )
        
        result = self.validator.validate_rollback_config()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "deve ser" in result.message
    
    def test_validate_compliance_config_success(self):
        """Teste de validação bem-sucedida de configuração de compliance"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={
                "pci_dss": {"enabled": True, "strict_mode": False},
                "lgpd": {"enabled": True, "strict_mode": True}
            }
        )
        
        result = self.validator.validate_compliance_config()
        
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO
        assert "válida" in result.message
    
    def test_validate_compliance_config_empty(self):
        """Teste de validação com configuração de compliance vazia"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={}
        )
        
        result = self.validator.validate_compliance_config()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "nenhum padrão" in result.message
    
    def test_validate_compliance_config_invalid_structure(self):
        """Teste de validação com estrutura inválida"""
        self.validator.config = TriggerConfig(
            sensitive_files=[],
            auto_rerun_patterns=[],
            exclusion_patterns=[],
            semantic_threshold=0.85,
            rollback_config={},
            compliance_config={
                "pci_dss": "invalid_structure"
            }
        )
        
        result = self.validator.validate_compliance_config()
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.WARNING
        assert "deve ser um objeto" in result.message
    
    def test_validate_all_success(self):
        """Teste de validação completa bem-sucedida"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.valid_config))):
            with patch('pathlib.Path.exists', return_value=True):
                results = self.validator.validate_all()
                
                assert len(results) == 6  # load_config + 5 validations
                assert all(r.is_valid for r in results)
    
    def test_validate_all_with_errors(self):
        """Teste de validação completa com erros"""
        invalid_config = {"sensitive_files": []}  # Configuração incompleta
        
        with patch('builtins.open', mock_open(read_data=json.dumps(invalid_config))):
            with patch('pathlib.Path.exists', return_value=True):
                results = self.validator.validate_all()
                
                # Primeira validação (load_config) deve falhar
                assert not results[0].is_valid
                assert len(results) == 1  # Para após falha no carregamento
    
    def test_get_summary_success(self):
        """Teste de geração de resumo bem-sucedida"""
        # Simular resultados de validação
        self.validator.validation_results = [
            ValidationResult(True, ValidationSeverity.INFO, "Sucesso 1"),
            ValidationResult(True, ValidationSeverity.INFO, "Sucesso 2"),
            ValidationResult(False, ValidationSeverity.WARNING, "Aviso 1"),
            ValidationResult(False, ValidationSeverity.ERROR, "Erro 1")
        ]
        
        summary = self.validator.get_summary()
        
        assert summary["overall_valid"] is False
        assert summary["total_validations"] == 4
        assert summary["errors"] == 1
        assert summary["warnings"] == 1
        assert summary["infos"] == 2
        assert "details" in summary
    
    def test_get_summary_no_validations(self):
        """Teste de resumo sem validações executadas"""
        summary = self.validator.get_summary()
        
        assert "error" in summary
        assert "Nenhuma validação executada" in summary["error"]
    
    def test_generate_report(self):
        """Teste de geração de relatório"""
        # Simular resultados de validação
        self.validator.validation_results = [
            ValidationResult(True, ValidationSeverity.INFO, "Validação bem-sucedida"),
            ValidationResult(False, ValidationSeverity.WARNING, "Aviso encontrado", {"details": "test"})
        ]
        
        report = self.validator.generate_report()
        
        assert "RELATÓRIO DE VALIDAÇÃO" in report
        assert "Status Geral" in report
        assert "Estatísticas" in report
        assert "Detalhes" in report
        assert "Validação bem-sucedida" in report
        assert "Aviso encontrado" in report


class TestValidationResult:
    """Testes para ValidationResult"""
    
    def test_validation_result_creation(self):
        """Teste de criação de ValidationResult"""
        result = ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message="Teste",
            details={"key": "value"}
        )
        
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO
        assert result.message == "Teste"
        assert result.details == {"key": "value"}
    
    def test_validation_result_without_details(self):
        """Teste de ValidationResult sem detalhes"""
        result = ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message="Erro"
        )
        
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert result.message == "Erro"
        assert result.details is None


class TestTriggerConfig:
    """Testes para TriggerConfig"""
    
    def test_trigger_config_creation(self):
        """Teste de criação de TriggerConfig"""
        config = TriggerConfig(
            sensitive_files=[".env"],
            auto_rerun_patterns=[r"\.py$"],
            exclusion_patterns=[r"__pycache__"],
            semantic_threshold=0.85,
            rollback_config={"enabled": True},
            compliance_config={"pci_dss": {"enabled": True}}
        )
        
        assert len(config.sensitive_files) == 1
        assert len(config.auto_rerun_patterns) == 1
        assert len(config.exclusion_patterns) == 1
        assert config.semantic_threshold == 0.85
        assert config.rollback_config["enabled"] is True
        assert config.compliance_config["pci_dss"]["enabled"] is True


if __name__ == "__main__":
    pytest.main([__file__]) 