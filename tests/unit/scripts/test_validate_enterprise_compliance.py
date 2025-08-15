from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Testes unitários para Enterprise Compliance Validation Script
Tracing ID: TEST_VALIDATION_ENTERPRISE_20250127_001

Testa todas as funcionalidades do sistema de validação enterprise:
- Validação de qualidade de documentação
- Validação de similaridade semântica
- Validação de segurança
- Validação de sistema de rollback
- Validação de métricas de performance
- Validação de compliance
"""

import asyncio
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import pytest

# Importar o script de validação
from scripts.validate_enterprise_compliance import EnterpriseComplianceValidator


class TestEnterpriseComplianceValidator:
    """
    Testes para o validador principal de conformidade enterprise.
    """
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.validator = EnterpriseComplianceValidator()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Limpeza após cada teste."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Testa inicialização correta do validador."""
        assert self.validator.tracing_id.startswith("VALIDATION_")
        assert self.validator.results["status"] == "running"
        assert "validation_id" in self.validator.results
        assert "timestamp" in self.validator.results
        assert "metrics" in self.validator.results
        assert "violations" in self.validator.results
        assert "recommendations" in self.validator.results
    
    @patch('scripts.validate_enterprise_compliance.DocQualityAnalyzer')
    @patch('scripts.validate_enterprise_compliance.Path')
    async def test_validate_doc_quality_success(self, mock_path, mock_analyzer):
        """Testa validação de qualidade de documentação com sucesso."""
        # Mock do analisador de qualidade
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.calculate_doc_quality_score.return_value = 0.90
        mock_analyzer_instance.analyze_completeness.return_value = 0.85
        mock_analyzer_instance.analyze_coherence.return_value = 0.88
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Mock de arquivos de documentação
        mock_doc_file = MagicMock()
        mock_doc_file.__str__.return_value = "docs/test.md"
        mock_path.return_value.rglob.return_value = [mock_doc_file]
        
        # Mock de leitura de arquivo
        with patch('builtins.open', mock_open(read_data="# Test Documentation\n\nThis is a test doc.")):
            result = await self.validator.validate_doc_quality()
        
        assert "doc_quality_scores" in result
        assert "completeness" in result
        assert "coherence" in result
        assert "threshold_violations" in result
        assert len(result["threshold_violations"]) == 0  # Score > 0.85
    
    @patch('scripts.validate_enterprise_compliance.DocQualityAnalyzer')
    @patch('scripts.validate_enterprise_compliance.Path')
    async def test_validate_doc_quality_threshold_violation(self, mock_path, mock_analyzer):
        """Testa detecção de violação de threshold de qualidade."""
        # Mock do analisador com score baixo
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.calculate_doc_quality_score.return_value = 0.70
        mock_analyzer_instance.analyze_completeness.return_value = 0.65
        mock_analyzer_instance.analyze_coherence.return_value = 0.75
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Mock de arquivos de documentação
        mock_doc_file = MagicMock()
        mock_doc_file.__str__.return_value = "docs/poor_quality.md"
        mock_path.return_value.rglob.return_value = [mock_doc_file]
        
        # Mock de leitura de arquivo
        with patch('builtins.open', mock_open(read_data="# Poor Documentation\n\nIncomplete doc.")):
            result = await self.validator.validate_doc_quality()
        
        assert len(result["threshold_violations"]) > 0
        violation = result["threshold_violations"][0]
        assert violation["score"] == 0.70
        assert violation["threshold"] == 0.85
        assert violation["type"] == "doc_quality"
    
    @patch('scripts.validate_enterprise_compliance.SemanticEmbeddingService')
    @patch('scripts.validate_enterprise_compliance.Path')
    @patch('scripts.validate_enterprise_compliance.ast')
    async def test_validate_semantic_similarity_success(self, mock_ast, mock_path, mock_embedding):
        """Testa validação de similaridade semântica com sucesso."""
        # Mock do serviço de embeddings
        mock_embedding_instance = MagicMock()
        mock_embedding_instance.calculate_similarity.return_value = 0.90
        mock_embedding.return_value = mock_embedding_instance
        
        # Mock de arquivos Python
        mock_py_file = MagicMock()
        mock_py_file.__str__.return_value = "test_module.py"
        mock_path.return_value.rglob.return_value = [mock_py_file]
        
        # Mock de AST
        mock_function = MagicMock()
        mock_function.name = "test_function"
        mock_function.__class__.__name__ = "FunctionDef"
        mock_ast.get_docstring.return_value = "Test function documentation"
        
        mock_tree = MagicMock()
        mock_ast.walk.return_value = [mock_function]
        mock_ast.parse.return_value = mock_tree
        
        # Mock de leitura de arquivo
        with patch('builtins.open', mock_open(read_data="def test_function():\n    pass")):
            result = await self.validator.validate_semantic_similarity()
        
        assert "function_similarities" in result
        assert "threshold_violations" in result
        assert len(result["threshold_violations"]) == 0  # Similarity > 0.85
    
    @patch('scripts.validate_enterprise_compliance.SemanticEmbeddingService')
    @patch('scripts.validate_enterprise_compliance.Path')
    @patch('scripts.validate_enterprise_compliance.ast')
    async def test_validate_semantic_similarity_low_similarity(self, mock_ast, mock_path, mock_embedding):
        """Testa detecção de similaridade semântica baixa."""
        # Mock do serviço com similaridade baixa
        mock_embedding_instance = MagicMock()
        mock_embedding_instance.calculate_similarity.return_value = 0.60
        mock_embedding.return_value = mock_embedding_instance
        
        # Mock de arquivos Python
        mock_py_file = MagicMock()
        mock_py_file.__str__.return_value = "test_module.py"
        mock_path.return_value.rglob.return_value = [mock_py_file]
        
        # Mock de AST
        mock_function = MagicMock()
        mock_function.name = "test_function"
        mock_function.__class__.__name__ = "FunctionDef"
        mock_ast.get_docstring.return_value = "Poor documentation"
        
        mock_tree = MagicMock()
        mock_ast.walk.return_value = [mock_function]
        mock_ast.parse.return_value = mock_tree
        
        # Mock de leitura de arquivo
        with patch('builtins.open', mock_open(read_data="def test_function():\n    pass")):
            result = await self.validator.validate_semantic_similarity()
        
        assert len(result["threshold_violations"]) > 0
        violation = result["threshold_violations"][0]
        assert violation["similarity"] == 0.60
        assert violation["threshold"] == 0.85
        assert violation["type"] == "semantic_similarity"
    
    @patch('scripts.validate_enterprise_compliance.SensitiveDataDetector')
    @patch('scripts.validate_enterprise_compliance.Path')
    async def test_validate_security_no_sensitive_data(self, mock_path, mock_detector):
        """Testa validação de segurança sem dados sensíveis."""
        # Mock do detector de dados sensíveis
        mock_detector_instance = MagicMock()
        mock_detector_instance.scan_documentation.return_value = []
        mock_detector_instance.sanitize_content.return_value = "Clean content"
        mock_detector.return_value = mock_detector_instance
        
        # Mock de arquivos
        mock_file = MagicMock()
        mock_file.__str__.return_value = "test.md"
        mock_path.return_value.rglob.return_value = [mock_file]
        
        # Mock de leitura de arquivo
        with patch('builtins.open', mock_open(read_data="Clean content")):
            result = await self.validator.validate_security()
        
        assert "sensitive_data_found" in result
        assert "security_score" in result
        assert len(result["sensitive_data_found"]) == 0
        assert result["security_score"] == 1.0  # Todos os arquivos seguros
    
    @patch('scripts.validate_enterprise_compliance.SensitiveDataDetector')
    @patch('scripts.validate_enterprise_compliance.Path')
    async def test_validate_security_with_sensitive_data(self, mock_path, mock_detector):
        """Testa detecção de dados sensíveis."""
        # Mock do detector com dados sensíveis encontrados
        mock_detector_instance = MagicMock()
        mock_detector_instance.scan_documentation.return_value = ["AWS_KEY=abc123"]
        mock_detector_instance.sanitize_content.return_value = "Sanitized content"
        mock_detector.return_value = mock_detector_instance
        
        # Mock de arquivos
        mock_file = MagicMock()
        mock_file.__str__.return_value = "config.md"
        mock_path.return_value.rglob.return_value = [mock_file]
        
        # Mock de leitura de arquivo
        with patch('builtins.open', mock_open(read_data="AWS_KEY=abc123")):
            result = await self.validator.validate_security()
        
        assert len(result["sensitive_data_found"]) > 0
        sensitive_data = result["sensitive_data_found"][0]
        assert sensitive_data["file"] == "config.md"
        assert "AWS_KEY=abc123" in sensitive_data["sensitive_data"]
        assert sensitive_data["severity"] == "high"
    
    @patch('scripts.validate_enterprise_compliance.RollbackSystem')
    async def test_validate_rollback_system_success(self, mock_rollback):
        """Testa validação do sistema de rollback com sucesso."""
        # Mock do sistema de rollback
        mock_rollback_instance = MagicMock()
        mock_rollback_instance.create_snapshot.return_value = "snapshot_123"
        mock_rollback_instance.detect_divergence_and_rollback.return_value = False
        mock_rollback_instance.restore_snapshot.return_value = True
        mock_rollback.return_value = mock_rollback_instance
        
        result = await self.validator.validate_rollback_system()
        
        assert result["snapshot_creation"] is True
        assert result["snapshot_restoration"] is True
        assert result["divergence_detection"] is True
    
    @patch('scripts.validate_enterprise_compliance.RollbackSystem')
    async def test_validate_rollback_system_failure(self, mock_rollback):
        """Testa falha no sistema de rollback."""
        # Mock do sistema de rollback com falha
        mock_rollback_instance = MagicMock()
        mock_rollback_instance.create_snapshot.side_effect = Exception("Rollback failed")
        mock_rollback.return_value = mock_rollback_instance
        
        result = await self.validator.validate_rollback_system()
        
        assert result["snapshot_creation"] is False
        assert result["snapshot_restoration"] is False
        assert result["divergence_detection"] is False
    
    @patch('scripts.validate_enterprise_compliance.MetricsCollector')
    async def test_validate_performance_metrics_success(self, mock_collector):
        """Testa validação de métricas de performance com sucesso."""
        # Mock do coletor de métricas
        mock_collector_instance = MagicMock()
        mock_collector_instance.collect_metrics.return_value = {
            "generation_time": 120.0,  # 2 minutos
            "tokens_consumed": 5000,
            "coverage": 0.98
        }
        mock_collector.return_value = mock_collector_instance
        
        result = await self.validator.validate_performance_metrics()
        
        assert result["generation_time"] == 120.0
        assert result["tokens_consumed"] == 5000
        assert result["documentation_coverage"] == 0.98
        assert len(result["threshold_violations"]) == 0  # Todos dentro dos thresholds
    
    @patch('scripts.validate_enterprise_compliance.MetricsCollector')
    async def test_validate_performance_metrics_threshold_violations(self, mock_collector):
        """Testa detecção de violações de threshold de performance."""
        # Mock do coletor com métricas fora do threshold
        mock_collector_instance = MagicMock()
        mock_collector_instance.collect_metrics.return_value = {
            "generation_time": 400.0,  # 6.7 minutos (> 5)
            "tokens_consumed": 15000,   # > 10000
            "coverage": 0.85           # < 0.95
        }
        mock_collector.return_value = mock_collector_instance
        
        result = await self.validator.validate_performance_metrics()
        
        assert len(result["threshold_violations"]) == 3
        
        # Verificar violações específicas
        violations = {value["metric"]: value for value in result["threshold_violations"]}
        assert "generation_time" in violations
        assert "tokens_consumed" in violations
        assert "documentation_coverage" in violations
    
    @patch('scripts.validate_enterprise_compliance.ComplianceValidator')
    async def test_validate_compliance_success(self, mock_compliance):
        """Testa validação de compliance com sucesso."""
        # Mock do validador de compliance
        mock_compliance_instance = MagicMock()
        mock_compliance_instance.validate_pci_dss.return_value = {
            "compliant": True,
            "violations": []
        }
        mock_compliance_instance.validate_lgpd.return_value = {
            "compliant": True,
            "violations": []
        }
        mock_compliance_instance.perform_security_audit.return_value = {
            "passed": True,
            "findings": []
        }
        mock_compliance.return_value = mock_compliance_instance
        
        result = await self.validator.validate_compliance()
        
        assert result["pci_dss_compliance"] is True
        assert result["lgpd_compliance"] is True
        assert result["security_audit"] is True
        assert len(result["violations"]) == 0
    
    @patch('scripts.validate_enterprise_compliance.ComplianceValidator')
    async def test_validate_compliance_violations(self, mock_compliance):
        """Testa detecção de violações de compliance."""
        # Mock do validador com violações
        mock_compliance_instance = MagicMock()
        mock_compliance_instance.validate_pci_dss.return_value = {
            "compliant": False,
            "violations": ["PCI-DSS 6.3: Missing encryption"]
        }
        mock_compliance_instance.validate_lgpd.return_value = {
            "compliant": True,
            "violations": []
        }
        mock_compliance_instance.perform_security_audit.return_value = {
            "passed": False,
            "findings": ["Security vulnerability detected"]
        }
        mock_compliance.return_value = mock_compliance_instance
        
        result = await self.validator.validate_compliance()
        
        assert result["pci_dss_compliance"] is False
        assert result["lgpd_compliance"] is True
        assert result["security_audit"] is False
        assert len(result["violations"]) == 2
    
    @patch('scripts.validate_enterprise_compliance.asyncio.gather')
    async def test_run_complete_validation_success(self, mock_gather):
        """Testa execução completa da validação com sucesso."""
        # Mock de todos os resultados de validação
        mock_gather.return_value = [
            {"doc_quality_scores": {}, "threshold_violations": []},
            {"function_similarities": {}, "threshold_violations": []},
            {"sensitive_data_found": [], "security_score": 1.0},
            {"snapshot_creation": True, "snapshot_restoration": True},
            {"generation_time": 120.0, "threshold_violations": []},
            {"pci_dss_compliance": True, "violations": []}
        ]
        
        result = await self.validator.run_complete_validation()
        
        assert result["status"] == "passed"
        assert "metrics" in result
        assert "total_execution_time" in result
        assert len(result["violations"]) == 0
        assert "recommendations" in result
    
    @patch('scripts.validate_enterprise_compliance.asyncio.gather')
    async def test_run_complete_validation_with_violations(self, mock_gather):
        """Testa execução completa com violações detectadas."""
        # Mock de resultados com violações
        mock_gather.return_value = [
            {"doc_quality_scores": {}, "threshold_violations": [{"type": "doc_quality"}]},
            {"function_similarities": {}, "threshold_violations": []},
            {"sensitive_data_found": [], "security_score": 1.0},
            {"snapshot_creation": True, "snapshot_restoration": True},
            {"generation_time": 120.0, "threshold_violations": []},
            {"pci_dss_compliance": True, "violations": []}
        ]
        
        result = await self.validator.run_complete_validation()
        
        assert result["status"] == "failed"
        assert len(result["violations"]) > 0
        assert len(result["recommendations"]) > 0
    
    @patch('scripts.validate_enterprise_compliance.asyncio.gather')
    async def test_run_complete_validation_exception(self, mock_gather):
        """Testa tratamento de exceções na validação completa."""
        # Mock de exceção
        mock_gather.side_effect = Exception("Validation failed")
        
        result = await self.validator.run_complete_validation()
        
        assert result["status"] == "error"
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_generate_recommendations_quality_violations(self):
        """Testa geração de recomendações para violações de qualidade."""
        self.validator.results["violations"] = [
            {"type": "doc_quality", "file": "test.md"},
            {"type": "semantic_similarity", "function": "test_func"}
        ]
        
        recommendations = self.validator._generate_recommendations()
        
        assert len(recommendations) > 0
        assert any("qualidade da documentação" in rec for rec in recommendations)
    
    def test_generate_recommendations_performance_violations(self):
        """Testa geração de recomendações para violações de performance."""
        self.validator.results["violations"] = [
            {"metric": "generation_time", "value": 400},
            {"metric": "tokens_consumed", "value": 15000}
        ]
        
        recommendations = self.validator._generate_recommendations()
        
        assert len(recommendations) > 0
        assert any("performance" in rec for rec in recommendations)
    
    def test_generate_recommendations_compliance_violations(self):
        """Testa geração de recomendações para violações de compliance."""
        self.validator.results["violations"] = [
            {"type": "pci_dss", "violation": "Missing encryption"},
            {"type": "lgpd", "violation": "Data processing without consent"}
        ]
        
        recommendations = self.validator._generate_recommendations()
        
        assert len(recommendations) > 0
        assert any("compliance" in rec for rec in recommendations)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_results_success(self, mock_json_dump, mock_file):
        """Testa salvamento bem-sucedido dos resultados."""
        self.validator.results["status"] = "passed"
        
        self.validator.save_results("test_results.json")
        
        mock_file.assert_called_once_with("test_results.json", 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    @patch('builtins.open')
    def test_save_results_exception(self, mock_file):
        """Testa tratamento de exceção no salvamento."""
        mock_file.side_effect = Exception("File write failed")
        
        # Não deve levantar exceção
        self.validator.save_results("test_results.json")


class TestMainFunction:
    """Testes para a função main do script."""
    
    @patch('scripts.validate_enterprise_compliance.EnterpriseComplianceValidator')
    @patch('scripts.validate_enterprise_compliance.asyncio.run')
    async def test_main_success(self, mock_run, mock_validator_class):
        """Testa execução bem-sucedida da função main."""
        # Mock do validador
        mock_validator = MagicMock()
        mock_validator.run_complete_validation.return_value = {
            "status": "passed",
            "violations": [],
            "recommendations": []
        }
        mock_validator_class.return_value = mock_validator
        
        # Mock de asyncio.run
        mock_run.return_value = 0
        
        # Importar e executar main
        from scripts.validate_enterprise_compliance import main
        result = await main()
        
        assert result == 0
        mock_validator.run_complete_validation.assert_called_once()
        mock_validator.save_results.assert_called_once()
    
    @patch('scripts.validate_enterprise_compliance.EnterpriseComplianceValidator')
    @patch('scripts.validate_enterprise_compliance.asyncio.run')
    async def test_main_with_violations(self, mock_run, mock_validator_class):
        """Testa execução da função main com violações."""
        # Mock do validador com violações
        mock_validator = MagicMock()
        mock_validator.run_complete_validation.return_value = {
            "status": "failed",
            "violations": [{"type": "doc_quality"}],
            "recommendations": ["Fix documentation"]
        }
        mock_validator_class.return_value = mock_validator
        
        # Mock de asyncio.run
        mock_run.return_value = 1
        
        # Importar e executar main
        from scripts.validate_enterprise_compliance import main
        result = await main()
        
        assert result == 1
        mock_validator.run_complete_validation.assert_called_once()
        mock_validator.save_results.assert_called_once()
    
    @patch('scripts.validate_enterprise_compliance.EnterpriseComplianceValidator')
    @patch('scripts.validate_enterprise_compliance.asyncio.run')
    async def test_main_exception(self, mock_run, mock_validator_class):
        """Testa tratamento de exceção na função main."""
        # Mock de exceção
        mock_validator_class.side_effect = Exception("Validator creation failed")
        
        # Mock de asyncio.run
        mock_run.return_value = 1
        
        # Importar e executar main
        from scripts.validate_enterprise_compliance import main
        result = await main()
        
        assert result == 1


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-value"]) 