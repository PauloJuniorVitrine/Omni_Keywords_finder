from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Testes unitários para o script de geração de documentação enterprise
Tracing ID: TEST_GENERATE_ENTERPRISE_DOCS_20250127_001
Data: 2025-01-27
Versão: 1.0

Objetivo: Validar funcionalidade completa do EnterpriseDocGenerator
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import traceback

# Adicionar diretório raiz ao path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from scripts.generate_enterprise_docs import (
    EnterpriseDocGenerator,
    GenerationConfig,
    GenerationResult,
    main
)


class TestGenerationConfig:
    """Testes para a classe GenerationConfig"""
    
    def test_generation_config_defaults(self):
        """Testar valores padrão da configuração"""
        config = GenerationConfig()
        
        assert config.docs_path == "docs/"
        assert config.output_path == "docs/enterprise/"
        assert config.backup_enabled is True
        assert config.quality_threshold == 0.85
        assert config.security_threshold == 1.0
        assert config.compliance_threshold == 0.90
        assert config.max_workers == 4
        assert config.verbose is False
    
    def test_generation_config_custom_values(self):
        """Testar configuração com valores customizados"""
        config = GenerationConfig(
            docs_path="/custom/docs",
            output_path="/custom/output",
            backup_enabled=False,
            quality_threshold=0.90,
            max_workers=8,
            verbose=True
        )
        
        assert config.docs_path == "/custom/docs"
        assert config.output_path == "/custom/output"
        assert config.backup_enabled is False
        assert config.quality_threshold == 0.90
        assert config.max_workers == 8
        assert config.verbose is True


class TestGenerationResult:
    """Testes para a classe GenerationResult"""
    
    def test_generation_result_creation(self):
        """Testar criação de resultado de geração"""
        result = GenerationResult(
            timestamp="2025-01-27T10:00:00",
            tracing_id="TEST_001",
            success=True,
            duration=120.5,
            files_generated=7,
            files_processed=7,
            quality_score=0.88,
            security_score=1.0,
            compliance_score=0.92,
            errors=[],
            warnings=[],
            metrics={"avg_generation_time": 120.5}
        )
        
        assert result.timestamp == "2025-01-27T10:00:00"
        assert result.tracing_id == "TEST_001"
        assert result.success is True
        assert result.duration == 120.5
        assert result.files_generated == 7
        assert result.files_processed == 7
        assert result.quality_score == 0.88
        assert result.security_score == 1.0
        assert result.compliance_score == 0.92
        assert result.errors == []
        assert result.warnings == []
        assert result.metrics["avg_generation_time"] == 120.5
    
    def test_generation_result_with_errors(self):
        """Testar resultado com erros"""
        errors = [
            {"type": "ERROR", "message": "Falha na geração de APIs"}
        ]
        warnings = [
            {"type": "WARNING", "message": "Qualidade baixa detectada"}
        ]
        
        result = GenerationResult(
            timestamp="2025-01-27T10:00:00",
            tracing_id="TEST_002",
            success=False,
            duration=60.0,
            files_generated=3,
            files_processed=7,
            quality_score=0.70,
            security_score=1.0,
            compliance_score=0.85,
            errors=errors,
            warnings=warnings,
            metrics={}
        )
        
        assert result.success is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert result.files_generated == 3
        assert result.files_processed == 7


class TestEnterpriseDocGenerator:
    """Testes para a classe EnterpriseDocGenerator"""
    
    @pytest.fixture
    def temp_test_env(self):
        """Configurar ambiente de teste temporário"""
        temp_dir = tempfile.mkdtemp()
        docs_dir = Path(temp_dir) / "docs"
        docs_dir.mkdir()
        
        # Criar arquivos de teste
        test_files = [
            ("test1.md", "# Teste 1\n\nConteúdo de qualidade."),
            ("test2.md", "# Teste 2\n\nConteúdo pobre."),
            ("sensitive.md", "# Sensível\n\nAPI_KEY=abc123\nPASSWORD=secret")
        ]
        
        for filename, content in test_files:
            file_path = docs_dir / filename
            file_path.write_text(content)
        
        yield {
            'temp_dir': temp_dir,
            'docs_dir': str(docs_dir)
        }
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_services(self):
        """Mock dos serviços dependentes"""
        with patch('scripts.generate_enterprise_docs.SemanticEmbeddingService') as mock_semantic, \
             patch('scripts.generate_enterprise_docs.DocQualityAnalyzer') as mock_quality, \
             patch('scripts.generate_enterprise_docs.SensitiveDataDetector') as mock_security, \
             patch('scripts.generate_enterprise_docs.RollbackSystem') as mock_rollback, \
             patch('scripts.generate_enterprise_docs.MetricsCollector') as mock_metrics, \
             patch('scripts.generate_enterprise_docs.MetricsAnalyzer') as mock_analyzer, \
             patch('scripts.generate_enterprise_docs.SemanticContractsGenerator') as mock_contracts, \
             patch('scripts.generate_enterprise_docs.LogAnalyzer') as mock_logs, \
             patch('scripts.generate_enterprise_docs.APIDocsGenerator') as mock_api, \
             patch('scripts.generate_enterprise_docs.TriggerConfigValidator') as mock_trigger, \
             patch('scripts.generate_enterprise_docs.ComplianceValidator') as mock_compliance, \
             patch('scripts.generate_enterprise_docs.DocComplianceValidator') as mock_checker:
            
            # Configurar mocks
            mock_quality.return_value.calculate_doc_quality_score.return_value = 0.85
            mock_security.return_value.scan_documentation.return_value = []
            mock_rollback.return_value.create_snapshot.return_value = "snapshot_001"
            mock_metrics.return_value.collect_all_metrics.return_value = {
                'avg_generation_time': 120,
                'avg_tokens_used': 5000,
                'documentation_coverage': 0.95
            }
            mock_analyzer.return_value.analyze_metrics.return_value = {
                'trends': ['Performance melhorando'],
                'optimizations': ['Reduzir tokens']
            }
            mock_contracts.return_value.generate_module_docs.return_value = {
                'module1': 'Documentação do módulo 1'
            }
            mock_contracts.return_value.generate_function_docs.return_value = {
                'func1': 'Documentação da função 1'
            }
            mock_logs.return_value.extract_suggestions.return_value = [
                'Melhorar logging',
                'Otimizar performance'
            ]
            mock_logs.return_value.prioritize_improvements.return_value = [
                'Prioridade alta: Segurança',
                'Prioridade média: Performance'
            ]
            mock_api.return_value.generate_graphql_docs.return_value = "# GraphQL Docs"
            mock_api.return_value.generate_protobuf_docs.return_value = "# Protobuf Docs"
            mock_api.return_value.generate_openapi_docs.return_value = "# OpenAPI Docs"
            mock_compliance.return_value.validate_all_standards.return_value = {
                'overall_score': 0.90,
                'violations': []
            }
            
            # Mock do compliance checker
            mock_report = Mock()
            mock_report.quality_score = 0.85
            mock_report.security_score = 1.0
            mock_report.compliance_score = 0.90
            mock_checker.return_value.run_validation.return_value = mock_report
            
            yield {
                'semantic': mock_semantic,
                'quality': mock_quality,
                'security': mock_security,
                'rollback': mock_rollback,
                'metrics': mock_metrics,
                'analyzer': mock_analyzer,
                'contracts': mock_contracts,
                'logs': mock_logs,
                'api': mock_api,
                'trigger': mock_trigger,
                'compliance': mock_compliance,
                'checker': mock_checker
            }
    
    def test_generator_initialization(self, mock_services):
        """Testar inicialização do gerador"""
        config = GenerationConfig()
        generator = EnterpriseDocGenerator(config)
        
        assert generator.config == config
        assert "ENTERPRISE_DOCS_" in generator.tracing_id
        assert generator.quality_analyzer is not None
        assert generator.security_detector is not None
        assert generator.rollback_system is not None
    
    def test_setup_logging(self, mock_services):
        """Testar configuração de logging"""
        config = GenerationConfig(verbose=True)
        generator = EnterpriseDocGenerator(config)
        
        assert generator.logger is not None
        assert len(generator.logger.handlers) >= 2  # Console + arquivo
    
    def test_create_backup_success(self, mock_services):
        """Testar criação de backup com sucesso"""
        config = GenerationConfig(backup_enabled=True)
        generator = EnterpriseDocGenerator(config)
        
        result = generator.create_backup()
        
        assert result is True
        mock_services['rollback'].return_value.create_snapshot.assert_called_once()
    
    def test_create_backup_disabled(self, mock_services):
        """Testar criação de backup desabilitada"""
        config = GenerationConfig(backup_enabled=False)
        generator = EnterpriseDocGenerator(config)
        
        result = generator.create_backup()
        
        assert result is True
        mock_services['rollback'].return_value.create_snapshot.assert_not_called()
    
    def test_create_backup_failure(self, mock_services):
        """Testar falha na criação de backup"""
        config = GenerationConfig(backup_enabled=True)
        generator = EnterpriseDocGenerator(config)
        
        # Configurar mock para falhar
        mock_services['rollback'].return_value.create_snapshot.side_effect = Exception("Backup failed")
        
        result = generator.create_backup()
        
        assert result is False
    
    def test_validate_environment_success(self, temp_test_env, mock_services):
        """Testar validação de ambiente com sucesso"""
        config = GenerationConfig(
            docs_path=temp_test_env['docs_dir'],
            output_path=temp_test_env['temp_dir'] + "/output"
        )
        generator = EnterpriseDocGenerator(config)
        
        # Criar arquivo de configuração de teste
        trigger_config = Path(temp_test_env['temp_dir']) / "trigger_config.json"
        trigger_config.write_text('{"sensitive_files": []}')
        
        with patch('scripts.generate_enterprise_docs.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.mkdir.return_value = None
            
            valid, errors = generator.validate_environment()
            
            assert valid is True
            assert len(errors) == 0
    
    def test_validate_environment_missing_config(self, temp_test_env, mock_services):
        """Testar validação com configuração ausente"""
        config = GenerationConfig(docs_path=temp_test_env['docs_dir'])
        generator = EnterpriseDocGenerator(config)
        
        with patch('scripts.generate_enterprise_docs.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            
            valid, errors = generator.validate_environment()
            
            assert valid is False
            assert len(errors) > 0
            assert any("configuração" in error.lower() for error in errors)
    
    def test_generate_semantic_contracts_success(self, temp_test_env, mock_services):
        """Testar geração de contratos semânticos com sucesso"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        success, errors = generator.generate_semantic_contracts()
        
        assert success is True
        assert len(errors) == 0
        mock_services['contracts'].return_value.generate_module_docs.assert_called_once()
        mock_services['contracts'].return_value.generate_function_docs.assert_called_once()
    
    def test_generate_semantic_contracts_failure(self, temp_test_env, mock_services):
        """Testar falha na geração de contratos semânticos"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        # Configurar mock para falhar
        mock_services['contracts'].return_value.generate_module_docs.side_effect = Exception("Generation failed")
        
        success, errors = generator.generate_semantic_contracts()
        
        assert success is False
        assert len(errors) == 1
        assert "erro na geração" in errors[0]['message'].lower()
    
    def test_generate_log_based_suggestions_success(self, temp_test_env, mock_services):
        """Testar geração de sugestões baseadas em logs com sucesso"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        success, errors = generator.generate_log_based_suggestions()
        
        assert success is True
        assert len(errors) == 0
        mock_services['logs'].return_value.extract_suggestions.assert_called_once()
        mock_services['logs'].return_value.prioritize_improvements.assert_called_once()
    
    def test_generate_api_documentation_success(self, temp_test_env, mock_services):
        """Testar geração de documentação de APIs com sucesso"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        success, errors = generator.generate_api_documentation()
        
        assert success is True
        assert len(errors) == 0
        mock_services['api'].return_value.generate_graphql_docs.assert_called_once()
        mock_services['api'].return_value.generate_protobuf_docs.assert_called_once()
        mock_services['api'].return_value.generate_openapi_docs.assert_called_once()
    
    def test_generate_quality_report_success(self, temp_test_env, mock_services):
        """Testar geração de relatório de qualidade com sucesso"""
        config = GenerationConfig(
            docs_path=temp_test_env['docs_dir'],
            output_path=temp_test_env['temp_dir']
        )
        generator = EnterpriseDocGenerator(config)
        
        success, errors = generator.generate_quality_report()
        
        assert success is True
        assert len(errors) == 0
        # Verificar se o arquivo foi criado
        quality_file = Path(temp_test_env['temp_dir']) / "quality_report.md"
        assert quality_file.exists()
    
    def test_generate_security_report_success(self, temp_test_env, mock_services):
        """Testar geração de relatório de segurança com sucesso"""
        config = GenerationConfig(
            docs_path=temp_test_env['docs_dir'],
            output_path=temp_test_env['temp_dir']
        )
        generator = EnterpriseDocGenerator(config)
        
        success, errors = generator.generate_security_report()
        
        assert success is True
        assert len(errors) == 0
        # Verificar se o arquivo foi criado
        security_file = Path(temp_test_env['temp_dir']) / "security_report.md"
        assert security_file.exists()
    
    def test_generate_security_report_with_incidents(self, temp_test_env, mock_services):
        """Testar geração de relatório de segurança com incidentes"""
        config = GenerationConfig(
            docs_path=temp_test_env['docs_dir'],
            output_path=temp_test_env['temp_dir']
        )
        generator = EnterpriseDocGenerator(config)
        
        # Configurar mock para detectar dados sensíveis
        mock_services['security'].return_value.scan_documentation.return_value = [
            {'type': 'AWS_KEY', 'line': 3, 'pattern': 'AKIA...'}
        ]
        
        success, errors = generator.generate_security_report()
        
        assert success is True
        assert len(errors) == 0
        
        # Verificar conteúdo do arquivo
        security_file = Path(temp_test_env['temp_dir']) / "security_report.md"
        content = security_file.read_text()
        assert "incidentes encontrados" in content.lower()
        assert "aws_key" in content.lower()
    
    def test_generate_compliance_report_success(self, temp_test_env, mock_services):
        """Testar geração de relatório de compliance com sucesso"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        success, errors = generator.generate_compliance_report()
        
        assert success is True
        assert len(errors) == 0
        mock_services['compliance'].return_value.validate_all_standards.assert_called_once()
        
        # Verificar se o arquivo foi criado
        compliance_file = Path(temp_test_env['temp_dir']) / "compliance_report.md"
        assert compliance_file.exists()
    
    def test_generate_metrics_report_success(self, temp_test_env, mock_services):
        """Testar geração de relatório de métricas com sucesso"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        success, errors = generator.generate_metrics_report()
        
        assert success is True
        assert len(errors) == 0
        mock_services['metrics'].return_value.collect_all_metrics.assert_called_once()
        mock_services['analyzer'].return_value.analyze_metrics.assert_called_once()
        
        # Verificar se o arquivo foi criado
        metrics_file = Path(temp_test_env['temp_dir']) / "metrics_report.md"
        assert metrics_file.exists()
    
    def test_generate_summary_report_success(self, temp_test_env, mock_services):
        """Testar geração de relatório resumo com sucesso"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        results = {
            'success': True,
            'duration': 120.5,
            'files_generated': 7,
            'files_processed': 7,
            'quality_score': 0.88,
            'security_score': 1.0,
            'compliance_score': 0.92,
            'errors': [],
            'warnings': []
        }
        
        success = generator.generate_summary_report(results)
        
        assert success is True
        
        # Verificar se o arquivo foi criado
        summary_file = Path(temp_test_env['temp_dir']) / "summary_report.md"
        assert summary_file.exists()
        
        # Verificar conteúdo
        content = summary_file.read_text()
        assert "relatório resumo" in content.lower()
        assert "sucesso" in content.lower()
        assert "7" in content  # files_generated
    
    def test_generate_summary_report_with_errors(self, temp_test_env, mock_services):
        """Testar geração de relatório resumo com erros"""
        config = GenerationConfig(output_path=temp_test_env['temp_dir'])
        generator = EnterpriseDocGenerator(config)
        
        results = {
            'success': False,
            'duration': 60.0,
            'files_generated': 3,
            'files_processed': 7,
            'quality_score': 0.70,
            'security_score': 1.0,
            'compliance_score': 0.85,
            'errors': [{"type": "ERROR", "message": "Falha na geração"}],
            'warnings': [{"type": "WARNING", "message": "Qualidade baixa"}]
        }
        
        success = generator.generate_summary_report(results)
        
        assert success is True
        
        # Verificar conteúdo
        summary_file = Path(temp_test_env['temp_dir']) / "summary_report.md"
        content = summary_file.read_text()
        assert "falha" in content.lower()
        assert "erros" in content.lower()
        assert "avisos" in content.lower()
    
    def test_run_generation_pipeline_success(self, temp_test_env, mock_services):
        """Testar pipeline completo com sucesso"""
        config = GenerationConfig(
            docs_path=temp_test_env['docs_dir'],
            output_path=temp_test_env['temp_dir'],
            max_workers=2
        )
        generator = EnterpriseDocGenerator(config)
        
        result = generator.run_generation_pipeline()
        
        assert isinstance(result, GenerationResult)
        assert result.success is True
        assert result.files_generated == 7  # Todas as tarefas
        assert result.files_processed == 7
        assert result.duration > 0
        assert len(result.errors) == 0
        assert result.quality_score == 0.85
        assert result.security_score == 1.0
        assert result.compliance_score == 0.90
    
    def test_run_generation_pipeline_with_errors(self, temp_test_env, mock_services):
        """Testar pipeline com erros"""
        config = GenerationConfig(
            docs_path=temp_test_env['docs_dir'],
            output_path=temp_test_env['temp_dir']
        )
        generator = EnterpriseDocGenerator(config)
        
        # Configurar mock para falhar em algumas tarefas
        mock_services['contracts'].return_value.generate_module_docs.side_effect = Exception("Contract generation failed")
        mock_services['api'].return_value.generate_graphql_docs.side_effect = Exception("API generation failed")
        
        result = generator.run_generation_pipeline()
        
        assert isinstance(result, GenerationResult)
        assert result.success is False
        assert result.files_generated < 7  # Menos arquivos gerados
        assert len(result.errors) >= 2  # Pelo menos 2 erros
    
    def test_run_generation_pipeline_environment_failure(self, temp_test_env, mock_services):
        """Testar pipeline com falha na validação de ambiente"""
        config = GenerationConfig(
            docs_path="/invalid/path",
            output_path=temp_test_env['temp_dir']
        )
        generator = EnterpriseDocGenerator(config)
        
        result = generator.run_generation_pipeline()
        
        assert isinstance(result, GenerationResult)
        assert result.success is False
        assert len(result.errors) >= 1
        assert any("ambiente inválido" in error['message'].lower() for error in result.errors)
    
    def test_save_result(self, temp_test_env, mock_services):
        """Testar salvamento de resultado"""
        config = GenerationConfig()
        generator = EnterpriseDocGenerator(config)
        
        result = GenerationResult(
            timestamp="2025-01-27T10:00:00",
            tracing_id="TEST_001",
            success=True,
            duration=120.5,
            files_generated=7,
            files_processed=7,
            quality_score=0.88,
            security_score=1.0,
            compliance_score=0.92,
            errors=[],
            warnings=[],
            metrics={}
        )
        
        output_path = Path(temp_test_env['temp_dir']) / "result.json"
        generator.save_result(result, str(output_path))
        
        # Verificar se arquivo foi criado
        assert output_path.exists()
        
        # Verificar conteúdo
        with open(output_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['tracing_id'] == "TEST_001"
        assert saved_data['success'] is True
        assert saved_data['files_generated'] == 7
    
    def test_print_summary(self, temp_test_env, mock_services, capsys):
        """Testar impressão do resumo"""
        config = GenerationConfig()
        generator = EnterpriseDocGenerator(config)
        
        result = GenerationResult(
            timestamp="2025-01-27T10:00:00",
            tracing_id="TEST_001",
            success=True,
            duration=120.5,
            files_generated=7,
            files_processed=7,
            quality_score=0.88,
            security_score=1.0,
            compliance_score=0.92,
            errors=[],
            warnings=[],
            metrics={}
        )
        
        generator.print_summary(result)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Verificar se contém elementos esperados
        assert "RELATÓRIO DE GERAÇÃO" in output
        assert "TEST_001" in output
        assert "SUCESSO" in output
        assert "7" in output  # files_generated
        assert "0.88" in output  # quality_score
    
    def test_print_summary_with_errors(self, temp_test_env, mock_services, capsys):
        """Testar impressão do resumo com erros"""
        config = GenerationConfig()
        generator = EnterpriseDocGenerator(config)
        
        result = GenerationResult(
            timestamp="2025-01-27T10:00:00",
            tracing_id="TEST_002",
            success=False,
            duration=60.0,
            files_generated=3,
            files_processed=7,
            quality_score=0.70,
            security_score=1.0,
            compliance_score=0.85,
            errors=[{"type": "ERROR", "message": "Falha na geração"}],
            warnings=[{"type": "WARNING", "message": "Qualidade baixa"}],
            metrics={}
        )
        
        generator.print_summary(result)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "FALHA" in output
        assert "ERROS" in output
        assert "AVISOS" in output
        assert "Falha na geração" in output


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
        
        yield {
            'temp_dir': temp_dir,
            'docs_dir': str(docs_dir)
        }
        
        shutil.rmtree(temp_dir)
    
    @patch('scripts.generate_enterprise_docs.EnterpriseDocGenerator')
    def test_main_success(self, mock_generator_class, temp_test_env):
        """Testar execução bem-sucedida da função main"""
        # Configurar mock
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_generator.run_generation_pipeline.return_value = mock_result
        mock_generator_class.return_value = mock_generator
        
        # Executar main
        with patch('sys.argv', ['generate_enterprise_docs.py', '--docs-path', temp_test_env['docs_dir']]), \
             patch('sys.exit') as mock_exit:
            main()
        
        # Verificar se foi chamado corretamente
        mock_generator.run_generation_pipeline.assert_called_once()
        mock_generator.save_result.assert_called_once()
        mock_generator.print_summary.assert_called_once()
        mock_exit.assert_called_once_with(0)
    
    @patch('scripts.generate_enterprise_docs.EnterpriseDocGenerator')
    def test_main_with_failure(self, mock_generator_class, temp_test_env):
        """Testar execução com falha"""
        # Configurar mock
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_generator.run_generation_pipeline.return_value = mock_result
        mock_generator_class.return_value = mock_generator
        
        # Executar main
        with patch('sys.argv', ['generate_enterprise_docs.py', '--docs-path', temp_test_env['docs_dir']]), \
             patch('sys.exit') as mock_exit:
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('scripts.generate_enterprise_docs.EnterpriseDocGenerator')
    def test_main_with_exception(self, mock_generator_class, temp_test_env):
        """Testar execução com exceção"""
        # Configurar mock para lançar exceção
        mock_generator_class.side_effect = Exception("Initialization failed")
        
        # Executar main
        with patch('sys.argv', ['generate_enterprise_docs.py', '--docs-path', temp_test_env['docs_dir']]), \
             patch('sys.exit') as mock_exit:
            main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('scripts.generate_enterprise_docs.EnterpriseDocGenerator')
    def test_main_with_verbose_flag(self, mock_generator_class, temp_test_env):
        """Testar execução com flag verbose"""
        # Configurar mock
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_generator.run_generation_pipeline.return_value = mock_result
        mock_generator_class.return_value = mock_generator
        
        # Executar main com verbose
        with patch('sys.argv', ['generate_enterprise_docs.py', '--verbose', '--docs-path', temp_test_env['docs_dir']]), \
             patch('sys.exit') as mock_exit:
            main()
        
        # Verificar se verbose foi configurado
        mock_exit.assert_called_once_with(0)
    
    @patch('scripts.generate_enterprise_docs.EnterpriseDocGenerator')
    def test_main_with_custom_config(self, mock_generator_class, temp_test_env):
        """Testar execução com configuração customizada"""
        # Configurar mock
        mock_generator = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_generator.run_generation_pipeline.return_value = mock_result
        mock_generator_class.return_value = mock_generator
        
        # Executar main com configurações customizadas
        with patch('sys.argv', [
            'generate_enterprise_docs.py',
            '--docs-path', temp_test_env['docs_dir'],
            '--output-path', temp_test_env['temp_dir'] + '/custom',
            '--quality-threshold', '0.90',
            '--max-workers', '8',
            '--no-backup'
        ]), patch('sys.exit') as mock_exit:
            main()
        
        # Verificar se configuração foi passada corretamente
        mock_generator_class.assert_called_once()
        call_args = mock_generator_class.call_args[0][0]
        assert call_args.docs_path == temp_test_env['docs_dir']
        assert call_args.output_path == temp_test_env['temp_dir'] + '/custom'
        assert call_args.quality_threshold == 0.90
        assert call_args.max_workers == 8
        assert call_args.backup_enabled is False
        
        mock_exit.assert_called_once_with(0)


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
    
    def test_full_generation_workflow(self, complex_test_env, mock_services):
        """Testar workflow completo de geração"""
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
        
        config = GenerationConfig(
            docs_path=complex_test_env,
            output_path=Path(complex_test_env).parent / "output",
            max_workers=2
        )
        
        generator = EnterpriseDocGenerator(config)
        result = generator.run_generation_pipeline()
        
        # Verificar resultados
        assert isinstance(result, GenerationResult)
        assert result.files_generated >= 5  # Pelo menos 5 tarefas bem-sucedidas
        assert result.files_processed == 7  # Total de tarefas
        assert result.quality_score == 0.85  # Score do mock
        assert result.security_score == 1.0  # Score do mock
        assert result.compliance_score == 0.90  # Score do mock
        
        # Verificar se arquivos foram gerados
        output_path = Path(complex_test_env).parent / "output"
        expected_files = [
            "semantic_contracts.md",
            "log_based_suggestions.md",
            "api_documentation.md",
            "quality_report.md",
            "security_report.md",
            "compliance_report.md",
            "metrics_report.md",
            "summary_report.md"
        ]
        
        for expected_file in expected_files:
            file_path = output_path / expected_file
            assert file_path.exists(), f"Arquivo {expected_file} não foi gerado"
    
    def test_error_recovery_and_rollback(self, complex_test_env, mock_services):
        """Testar recuperação de erro e rollback"""
        config = GenerationConfig(
            docs_path=complex_test_env,
            output_path=Path(complex_test_env).parent / "output",
            backup_enabled=True
        )
        
        generator = EnterpriseDocGenerator(config)
        
        # Configurar mock para falhar na validação de ambiente
        with patch.object(generator, 'validate_environment', return_value=(False, ["Erro de teste"])):
            result = generator.run_generation_pipeline()
        
        # Verificar que rollback foi tentado
        assert isinstance(result, GenerationResult)
        assert result.success is False
        assert len(result.errors) >= 1
        assert any("ambiente inválido" in error['message'].lower() for error in result.errors)
        
        # Verificar se rollback foi chamado
        mock_services['rollback'].return_value.restore_latest_snapshot.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 