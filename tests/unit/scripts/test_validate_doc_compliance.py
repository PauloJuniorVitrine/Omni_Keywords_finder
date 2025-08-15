from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Testes unitários para o script de validação de conformidade de documentação
Tracing ID: TEST_VALIDATE_DOC_COMPLIANCE_20250127_001
Data: 2025-01-27
Versão: 1.0

Objetivo: Validar funcionalidade completa do DocComplianceValidator
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar diretório raiz ao path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from scripts.validate_doc_compliance import (
    DocComplianceValidator,
    ComplianceReport,
    main
)


class TestComplianceReport:
    """Testes para a classe ComplianceReport"""
    
    def test_compliance_report_creation(self):
        """Testar criação de relatório de compliance"""
        report = ComplianceReport(
            timestamp="2025-01-27T10:00:00",
            tracing_id="TEST_001",
            overall_score=0.85,
            quality_score=0.90,
            security_score=1.0,
            compliance_score=0.80,
            performance_score=0.75,
            issues=[],
            recommendations=["Teste"],
            status="PASS"
        )
        
        assert report.timestamp == "2025-01-27T10:00:00"
        assert report.tracing_id == "TEST_001"
        assert report.overall_score == 0.85
        assert report.quality_score == 0.90
        assert report.security_score == 1.0
        assert report.compliance_score == 0.80
        assert report.performance_score == 0.75
        assert report.issues == []
        assert report.recommendations == ["Teste"]
        assert report.status == "PASS"
    
    def test_compliance_report_with_issues(self):
        """Testar relatório com problemas"""
        issues = [
            {
                "type": "WARNING",
                "message": "Qualidade baixa",
                "file": "test.md"
            }
        ]
        
        report = ComplianceReport(
            timestamp="2025-01-27T10:00:00",
            tracing_id="TEST_002",
            overall_score=0.70,
            quality_score=0.60,
            security_score=1.0,
            compliance_score=0.80,
            performance_score=0.75,
            issues=issues,
            recommendations=["Melhorar qualidade"],
            status="WARNING"
        )
        
        assert len(report.issues) == 1
        assert report.issues[0]["type"] == "WARNING"
        assert report.status == "WARNING"


class TestDocComplianceValidator:
    """Testes para a classe DocComplianceValidator"""
    
    @pytest.fixture
    def temp_docs_dir(self):
        """Criar diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        docs_dir = Path(temp_dir) / "docs"
        docs_dir.mkdir()
        
        # Criar arquivo de teste
        test_file = docs_dir / "test.md"
        test_file.write_text("# Teste\n\nConteúdo de teste.")
        
        yield str(docs_dir)
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_services(self):
        """Mock dos serviços dependentes"""
        with patch('scripts.validate_doc_compliance.DocQualityAnalyzer') as mock_quality, \
             patch('scripts.validate_doc_compliance.SensitiveDataDetector') as mock_security, \
             patch('scripts.validate_doc_compliance.MetricsCollector') as mock_metrics, \
             patch('scripts.validate_doc_compliance.TriggerConfigValidator') as mock_trigger, \
             patch('scripts.validate_doc_compliance.ComplianceValidator') as mock_compliance, \
             patch('scripts.validate_doc_compliance.RollbackSystem') as mock_rollback, \
             patch('scripts.validate_doc_compliance.SemanticEmbeddingService') as mock_semantic:
            
            # Configurar mocks
            mock_quality.return_value.calculate_doc_quality_score.return_value = 0.85
            mock_security.return_value.scan_documentation.return_value = []
            mock_metrics.return_value.collect_all_metrics.return_value = {
                'avg_generation_time': 120,
                'avg_tokens_used': 5000,
                'documentation_coverage': 0.95
            }
            mock_trigger.return_value.validate_config_file.return_value = {
                'is_valid': True,
                'errors': []
            }
            mock_compliance.return_value.validate_all_standards.return_value = {
                'overall_score': 0.90,
                'violations': []
            }
            
            yield {
                'quality': mock_quality,
                'security': mock_security,
                'metrics': mock_metrics,
                'trigger': mock_trigger,
                'compliance': mock_compliance,
                'rollback': mock_rollback,
                'semantic': mock_semantic
            }
    
    def test_validator_initialization(self, mock_services):
        """Testar inicialização do validador"""
        validator = DocComplianceValidator()
        
        assert validator.quality_threshold == 0.85
        assert validator.security_threshold == 1.0
        assert validator.compliance_threshold == 0.90
        assert validator.performance_threshold == 0.80
        assert "DOC_COMPLIANCE_" in validator.tracing_id
    
    def test_validate_quality_success(self, temp_docs_dir, mock_services):
        """Testar validação de qualidade com sucesso"""
        validator = DocComplianceValidator()
        
        quality_score, issues = validator.validate_quality(temp_docs_dir)
        
        assert quality_score == 0.85
        assert len(issues) == 0
        mock_services['quality'].return_value.calculate_doc_quality_score.assert_called_once()
    
    def test_validate_quality_below_threshold(self, temp_docs_dir, mock_services):
        """Testar validação de qualidade abaixo do threshold"""
        # Configurar mock para retornar score baixo
        mock_services['quality'].return_value.calculate_doc_quality_score.return_value = 0.70
        
        validator = DocComplianceValidator()
        
        quality_score, issues = validator.validate_quality(temp_docs_dir)
        
        assert quality_score == 0.70
        assert len(issues) == 1
        assert issues[0]["type"] == "WARNING"
        assert "threshold" in issues[0]["message"]
    
    def test_validate_quality_missing_directory(self, mock_services):
        """Testar validação com diretório inexistente"""
        validator = DocComplianceValidator()
        
        quality_score, issues = validator.validate_quality("/path/inexistente")
        
        assert quality_score == 0.0
        assert len(issues) == 1
        assert issues[0]["type"] == "CRITICAL"
        assert "não encontrado" in issues[0]["message"]
    
    def test_validate_security_success(self, temp_docs_dir, mock_services):
        """Testar validação de segurança com sucesso"""
        validator = DocComplianceValidator()
        
        security_score, issues = validator.validate_security(temp_docs_dir)
        
        assert security_score == 1.0
        assert len(issues) == 0
        mock_services['security'].return_value.scan_documentation.assert_called_once()
    
    def test_validate_security_with_sensitive_data(self, temp_docs_dir, mock_services):
        """Testar validação de segurança com dados sensíveis"""
        # Configurar mock para detectar dados sensíveis
        mock_services['security'].return_value.scan_documentation.return_value = [
            {
                'type': 'AWS_KEY',
                'line': 10,
                'pattern': 'AKIA...'
            }
        ]
        
        validator = DocComplianceValidator()
        
        security_score, issues = validator.validate_security(temp_docs_dir)
        
        assert security_score == 0.0
        assert len(issues) == 1
        assert issues[0]["type"] == "CRITICAL"
        assert "dados sensíveis" in issues[0]["message"]
    
    def test_validate_compliance_success(self, mock_services):
        """Testar validação de compliance com sucesso"""
        validator = DocComplianceValidator()
        
        compliance_score, issues = validator.validate_compliance()
        
        assert compliance_score == 0.90
        assert len(issues) == 0
        mock_services['compliance'].return_value.validate_all_standards.assert_called_once()
    
    def test_validate_compliance_with_violations(self, mock_services):
        """Testar validação de compliance com violações"""
        # Configurar mock para retornar violações
        mock_services['compliance'].return_value.validate_all_standards.return_value = {
            'overall_score': 0.70,
            'violations': [
                {
                    'description': 'Violação PCI-DSS',
                    'standard': 'PCI-DSS',
                    'severity': 'high'
                }
            ]
        }
        
        validator = DocComplianceValidator()
        
        compliance_score, issues = validator.validate_compliance()
        
        assert compliance_score == 0.70
        assert len(issues) == 1
        assert issues[0]["type"] == "CRITICAL"
        assert "violation" in issues[0]["message"]
    
    def test_validate_performance_success(self, mock_services):
        """Testar validação de performance com sucesso"""
        validator = DocComplianceValidator()
        
        performance_score, issues = validator.validate_performance()
        
        assert performance_score == 1.0
        assert len(issues) == 0
        mock_services['metrics'].return_value.collect_all_metrics.assert_called_once()
    
    def test_validate_performance_high_generation_time(self, mock_services):
        """Testar validação de performance com tempo alto"""
        # Configurar mock para tempo alto
        mock_services['metrics'].return_value.collect_all_metrics.return_value = {
            'avg_generation_time': 400,  # > 300s
            'avg_tokens_used': 5000,
            'documentation_coverage': 0.95
        }
        
        validator = DocComplianceValidator()
        
        performance_score, issues = validator.validate_performance()
        
        assert performance_score == 0.8  # 1.0 - 0.2
        assert len(issues) == 1
        assert issues[0]["type"] == "WARNING"
        assert "tempo de geração" in issues[0]["message"]
    
    def test_validate_performance_high_tokens(self, mock_services):
        """Testar validação de performance com tokens altos"""
        # Configurar mock para tokens altos
        mock_services['metrics'].return_value.collect_all_metrics.return_value = {
            'avg_generation_time': 120,
            'avg_tokens_used': 15000,  # > 10000
            'documentation_coverage': 0.95
        }
        
        validator = DocComplianceValidator()
        
        performance_score, issues = validator.validate_performance()
        
        assert performance_score == 0.8  # 1.0 - 0.2
        assert len(issues) == 1
        assert issues[0]["type"] == "WARNING"
        assert "tokens consumidos" in issues[0]["message"]
    
    def test_validate_performance_low_coverage(self, mock_services):
        """Testar validação de performance com cobertura baixa"""
        # Configurar mock para cobertura baixa
        mock_services['metrics'].return_value.collect_all_metrics.return_value = {
            'avg_generation_time': 120,
            'avg_tokens_used': 5000,
            'documentation_coverage': 0.80  # < 0.95
        }
        
        validator = DocComplianceValidator()
        
        performance_score, issues = validator.validate_performance()
        
        assert performance_score == 0.7  # 1.0 - 0.3
        assert len(issues) == 1
        assert issues[0]["type"] == "WARNING"
        assert "cobertura" in issues[0]["message"]
    
    def test_validate_trigger_config_success(self, mock_services):
        """Testar validação de trigger config com sucesso"""
        validator = DocComplianceValidator()
        
        config_score, issues = validator.validate_trigger_config()
        
        assert config_score == 1.0
        assert len(issues) == 0
        mock_services['trigger'].return_value.validate_config_file.assert_called_once()
    
    def test_validate_trigger_config_invalid(self, mock_services):
        """Testar validação de trigger config inválida"""
        # Configurar mock para config inválida
        mock_services['trigger'].return_value.validate_config_file.return_value = {
            'is_valid': False,
            'errors': ['Arquivo não encontrado']
        }
        
        validator = DocComplianceValidator()
        
        config_score, issues = validator.validate_trigger_config()
        
        assert config_score == 0.0
        assert len(issues) == 1
        assert issues[0]["type"] == "CRITICAL"
        assert "erro na configuração" in issues[0]["message"]
    
    def test_generate_recommendations_no_issues(self):
        """Testar geração de recomendações sem problemas"""
        validator = DocComplianceValidator()
        
        recommendations = validator.generate_recommendations([])
        
        assert len(recommendations) == 0
    
    def test_generate_recommendations_with_critical_issues(self):
        """Testar geração de recomendações com problemas críticos"""
        validator = DocComplianceValidator()
        
        issues = [
            {
                "type": "CRITICAL",
                "message": "Dados sensíveis detectados"
            }
        ]
        
        recommendations = validator.generate_recommendations(issues)
        
        assert len(recommendations) >= 1
        assert any("CRÍTICO" in rec for rec in recommendations)
        assert any("dados sensíveis" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_with_warning_issues(self):
        """Testar geração de recomendações com avisos"""
        validator = DocComplianceValidator()
        
        issues = [
            {
                "type": "WARNING",
                "message": "Qualidade abaixo do threshold"
            }
        ]
        
        recommendations = validator.generate_recommendations(issues)
        
        assert len(recommendations) >= 1
        assert any("ATENÇÃO" in rec for rec in recommendations)
        assert any("qualidade" in rec.lower() for rec in recommendations)
    
    def test_determine_status_pass(self):
        """Testar determinação de status PASS"""
        validator = DocComplianceValidator()
        
        scores = {
            'quality': 0.90,
            'security': 1.0,
            'compliance': 0.95,
            'performance': 0.85
        }
        
        status = validator.determine_status(scores)
        
        assert status == "PASS"
    
    def test_determine_status_fail_security(self):
        """Testar determinação de status FAIL por segurança"""
        validator = DocComplianceValidator()
        
        scores = {
            'quality': 0.90,
            'security': 0.0,  # Falha crítica
            'compliance': 0.95,
            'performance': 0.85
        }
        
        status = validator.determine_status(scores)
        
        assert status == "FAIL"
    
    def test_determine_status_fail_compliance(self):
        """Testar determinação de status FAIL por compliance"""
        validator = DocComplianceValidator()
        
        scores = {
            'quality': 0.90,
            'security': 1.0,
            'compliance': 0.80,  # < 0.90
            'performance': 0.85
        }
        
        status = validator.determine_status(scores)
        
        assert status == "FAIL"
    
    def test_determine_status_warning_quality(self):
        """Testar determinação de status WARNING por qualidade"""
        validator = DocComplianceValidator()
        
        scores = {
            'quality': 0.80,  # < 0.85
            'security': 1.0,
            'compliance': 0.95,
            'performance': 0.85
        }
        
        status = validator.determine_status(scores)
        
        assert status == "WARNING"
    
    def test_determine_status_warning_performance(self):
        """Testar determinação de status WARNING por performance"""
        validator = DocComplianceValidator()
        
        scores = {
            'quality': 0.90,
            'security': 1.0,
            'compliance': 0.95,
            'performance': 0.70  # < 0.80
        }
        
        status = validator.determine_status(scores)
        
        assert status == "WARNING"
    
    def test_run_validation_success(self, temp_docs_dir, mock_services):
        """Testar execução completa da validação com sucesso"""
        validator = DocComplianceValidator()
        
        report = validator.run_validation(temp_docs_dir)
        
        assert isinstance(report, ComplianceReport)
        assert report.status == "PASS"
        assert report.overall_score > 0.8
        assert len(report.issues) == 0
        assert "DOC_COMPLIANCE_" in report.tracing_id
    
    def test_run_validation_with_issues(self, temp_docs_dir, mock_services):
        """Testar execução completa da validação com problemas"""
        # Configurar mocks para retornar problemas
        mock_services['quality'].return_value.calculate_doc_quality_score.return_value = 0.70
        mock_services['security'].return_value.scan_documentation.return_value = [
            {'type': 'AWS_KEY', 'line': 1, 'pattern': 'test'}
        ]
        
        validator = DocComplianceValidator()
        
        report = validator.run_validation(temp_docs_dir)
        
        assert isinstance(report, ComplianceReport)
        assert report.status == "FAIL"  # Falha de segurança
        assert len(report.issues) >= 2  # Pelo menos 2 problemas
        assert len(report.recommendations) >= 1
    
    def test_save_report(self, temp_docs_dir, mock_services):
        """Testar salvamento do relatório"""
        validator = DocComplianceValidator()
        report = validator.run_validation(temp_docs_dir)
        
        # Criar arquivo temporário para teste
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            validator.save_report(report, output_path)
            
            # Verificar se arquivo foi criado
            assert Path(output_path).exists()
            
            # Verificar conteúdo
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data['tracing_id'] == report.tracing_id
            assert saved_data['status'] == report.status
            assert saved_data['overall_score'] == report.overall_score
            
        finally:
            # Limpar arquivo temporário
            Path(output_path).unlink(missing_ok=True)
    
    def test_print_summary(self, temp_docs_dir, mock_services, capsys):
        """Testar impressão do resumo"""
        validator = DocComplianceValidator()
        report = validator.run_validation(temp_docs_dir)
        
        validator.print_summary(report)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Verificar se contém elementos esperados
        assert "RELATÓRIO DE CONFORMIDADE" in output
        assert report.tracing_id in output
        assert report.status in output
        assert str(report.overall_score) in output


class TestMainFunction:
    """Testes para a função main"""
    
    @pytest.fixture
    def temp_test_env(self):
        """Configurar ambiente de teste temporário"""
        temp_dir = tempfile.mkdtemp()
        docs_dir = Path(temp_dir) / "docs"
        docs_dir.mkdir()
        
        # Criar arquivo de teste
        test_file = docs_dir / "test.md"
        test_file.write_text("# Teste\n\nConteúdo de teste.")
        
        # Criar config de teste
        config_file = docs_dir / "trigger_config.json"
        config_file.write_text('{"sensitive_files": [], "auto_rerun_patterns": []}')
        
        yield {
            'temp_dir': temp_dir,
            'docs_dir': str(docs_dir),
            'config_file': str(config_file)
        }
        
        shutil.rmtree(temp_dir)
    
    @patch('scripts.validate_doc_compliance.DocComplianceValidator')
    def test_main_success(self, mock_validator_class, temp_test_env):
        """Testar execução bem-sucedida da função main"""
        # Configurar mock
        mock_validator = Mock()
        mock_report = Mock()
        mock_report.status = "PASS"
        mock_validator.run_validation.return_value = mock_report
        mock_validator_class.return_value = mock_validator
        
        # Executar main
        with patch('sys.argv', ['validate_doc_compliance.py', '--docs-path', temp_test_env['docs_dir']]):
            result = main()
        
        # Verificar se foi chamado corretamente
        mock_validator.run_validation.assert_called_once_with(temp_test_env['docs_dir'])
        mock_validator.save_report.assert_called_once()
        mock_validator.print_summary.assert_called_once()
    
    @patch('scripts.validate_doc_compliance.DocComplianceValidator')
    def test_main_with_fail_status(self, mock_validator_class, temp_test_env):
        """Testar execução com status FAIL"""
        # Configurar mock
        mock_validator = Mock()
        mock_report = Mock()
        mock_report.status = "FAIL"
        mock_validator.run_validation.return_value = mock_report
        mock_validator_class.return_value = mock_validator
        
        # Executar main e verificar se sai com código 1
        with patch('sys.argv', ['validate_doc_compliance.py', '--docs-path', temp_test_env['docs_dir']]), \
             patch('sys.exit') as mock_exit:
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('scripts.validate_doc_compliance.DocComplianceValidator')
    def test_main_with_warning_status(self, mock_validator_class, temp_test_env):
        """Testar execução com status WARNING"""
        # Configurar mock
        mock_validator = Mock()
        mock_report = Mock()
        mock_report.status = "WARNING"
        mock_validator.run_validation.return_value = mock_report
        mock_validator_class.return_value = mock_validator
        
        # Executar main e verificar se sai com código 2
        with patch('sys.argv', ['validate_doc_compliance.py', '--docs-path', temp_test_env['docs_dir']]), \
             patch('sys.exit') as mock_exit:
            main()
        
        mock_exit.assert_called_once_with(2)
    
    @patch('scripts.validate_doc_compliance.DocComplianceValidator')
    def test_main_with_exception(self, mock_validator_class, temp_test_env):
        """Testar execução com exceção"""
        # Configurar mock para lançar exceção
        mock_validator_class.side_effect = Exception("Erro de teste")
        
        # Executar main e verificar se sai com código 1
        with patch('sys.argv', ['validate_doc_compliance.py', '--docs-path', temp_test_env['docs_dir']]), \
             patch('sys.exit') as mock_exit:
            main()
        
        mock_exit.assert_called_once_with(1)


class TestIntegrationScenarios:
    """Testes de cenários de integração"""
    
    @pytest.fixture
    def complex_test_env(self):
        """Configurar ambiente de teste complexo"""
        temp_dir = tempfile.mkdtemp()
        docs_dir = Path(temp_dir) / "docs"
        docs_dir.mkdir()
        
        # Criar múltiplos arquivos de teste
        files = [
            ("good.md", "# Bom arquivo\n\nConteúdo de qualidade."),
            ("bad.md", "# Arquivo ruim\n\nConteúdo pobre."),
            ("sensitive.md", "# Arquivo sensível\n\nAPI_KEY=abc123\nPASSWORD=secret")
        ]
        
        for filename, content in files:
            file_path = docs_dir / filename
            file_path.write_text(content)
        
        yield str(docs_dir)
        
        shutil.rmtree(temp_dir)
    
    def test_full_validation_workflow(self, complex_test_env, mock_services):
        """Testar workflow completo de validação"""
        # Configurar mocks para cenário realista
        def quality_score_side_effect(content):
            if "qualidade" in content:
                return 0.90
            elif "pobre" in content:
                return 0.60
            else:
                return 0.85
        
        def security_scan_side_effect(content):
            if "API_KEY" in content or "PASSWORD" in content:
                return [
                    {'type': 'API_KEY', 'line': 3, 'pattern': 'API_KEY=abc123'},
                    {'type': 'PASSWORD', 'line': 4, 'pattern': 'PASSWORD=secret'}
                ]
            return []
        
        mock_services['quality'].return_value.calculate_doc_quality_score.side_effect = quality_score_side_effect
        mock_services['security'].return_value.scan_documentation.side_effect = security_scan_side_effect
        
        validator = DocComplianceValidator()
        report = validator.run_validation(complex_test_env)
        
        # Verificar resultados
        assert report.status == "FAIL"  # Devido aos dados sensíveis
        assert len(report.issues) >= 3  # Pelo menos 3 problemas
        assert any("dados sensíveis" in issue["message"] for issue in report.issues)
        assert any("qualidade" in issue["message"] for issue in report.issues)
        
        # Verificar recomendações
        assert len(report.recommendations) >= 2
        assert any("CRÍTICO" in rec for rec in report.recommendations)
        assert any("dados sensíveis" in rec.lower() for rec in report.recommendations)


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 