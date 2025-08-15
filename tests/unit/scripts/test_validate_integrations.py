from typing import Dict, List, Optional, Any
"""
Testes Unitários para Ferramenta de Validação de Integrações - Omni Keywords Finder

Testes para validar a ferramenta de validação de integrações externas:
- Testa criação de configuração
- Valida execução de testes
- Verifica geração de relatórios
- Confirma tratamento de erros

Autor: Sistema de Testes de Validação
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: VALIDATION_TOOL_TEST_001
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Importa classes da ferramenta
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "scripts"))

from validate_integrations import (
    IntegrationValidator,
    IntegrationTest,
    IntegrationResult,
    IntegrationStatus,
    IntegrationType
)

class TestIntegrationValidator:
    """Testes para o validador de integrações"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return {
            "integrations": {
                "oauth2": {
                    "google": {
                        "enabled": True,
                        "endpoint": "https://accounts.google.com/.well-known/openid_configuration",
                        "timeout": 10
                    }
                },
                "payment": {
                    "stripe": {
                        "enabled": True,
                        "endpoint": "https://api.stripe.com/v1/account",
                        "timeout": 15,
                        "auth_required": True
                    }
                }
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Arquivo de configuração temporário"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f)
            yield f.name
        
        # Limpa arquivo temporário
        Path(f.name).unlink(missing_ok=True)
    
    def test_validator_initialization(self):
        """Testa inicialização do validador"""
        validator = IntegrationValidator()
        assert validator.config_file is None
        assert validator.results == []
        assert validator.session is None
    
    def test_validator_with_config_file(self, temp_config_file):
        """Testa inicialização com arquivo de configuração"""
        validator = IntegrationValidator(temp_config_file)
        assert validator.config_file == temp_config_file
    
    def test_load_config_default(self):
        """Testa carregamento de configuração padrão"""
        validator = IntegrationValidator()
        config = validator.load_config()
        
        assert "integrations" in config
        assert "oauth2" in config["integrations"]
        assert "payment" in config["integrations"]
        assert "webhook" in config["integrations"]
        assert "api_external" in config["integrations"]
        assert "notification" in config["integrations"]
        assert "backup" in config["integrations"]
    
    def test_load_config_from_file(self, temp_config_file, sample_config):
        """Testa carregamento de configuração de arquivo"""
        validator = IntegrationValidator(temp_config_file)
        config = validator.load_config()
        
        assert config == sample_config
    
    def test_create_tests(self, sample_config):
        """Testa criação de testes a partir da configuração"""
        validator = IntegrationValidator()
        tests = validator.create_tests(sample_config)
        
        assert len(tests) == 2
        
        # Verifica teste OAuth2
        oauth2_test = next(t for t in tests if t.name == "oauth2_google")
        assert oauth2_test.type == IntegrationType.OAUTH2
        assert oauth2_test.endpoint == "https://accounts.google.com/.well-known/openid_configuration"
        assert oauth2_test.timeout == 10
        assert not oauth2_test.auth_required
        
        # Verifica teste Payment
        payment_test = next(t for t in tests if t.name == "payment_stripe")
        assert payment_test.type == IntegrationType.PAYMENT
        assert payment_test.endpoint == "https://api.stripe.com/v1/account"
        assert payment_test.timeout == 15
        assert payment_test.auth_required
    
    def test_create_tests_disabled_integration(self):
        """Testa criação de testes com integração desabilitada"""
        config = {
            "integrations": {
                "oauth2": {
                    "google": {
                        "enabled": False,
                        "endpoint": "https://test.com",
                        "timeout": 10
                    }
                }
            }
        }
        
        validator = IntegrationValidator()
        tests = validator.create_tests(config)
        
        assert len(tests) == 0
    
    @pytest.mark.asyncio
    async def test_test_integration_success(self):
        """Testa teste de integração bem-sucedido"""
        test = IntegrationTest(
            name="test_integration",
            type=IntegrationType.OAUTH2,
            endpoint="https://httpbin.org/status/200",
            timeout=10
        )
        
        async with IntegrationValidator() as validator:
            result = await validator.test_integration(test)
            
            assert result.name == "test_integration"
            assert result.type == IntegrationType.OAUTH2
            assert result.status == IntegrationStatus.HEALTHY
            assert result.status_code == 200
            assert result.response_time > 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_test_integration_failure(self):
        """Testa teste de integração com falha"""
        test = IntegrationTest(
            name="test_integration",
            type=IntegrationType.OAUTH2,
            endpoint="https://httpbin.org/status/500",
            timeout=10
        )
        
        async with IntegrationValidator() as validator:
            result = await validator.test_integration(test)
            
            assert result.name == "test_integration"
            assert result.type == IntegrationType.OAUTH2
            assert result.status == IntegrationStatus.FAILED
            assert result.status_code == 500
            assert result.response_time > 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_test_integration_timeout(self):
        """Testa teste de integração com timeout"""
        test = IntegrationTest(
            name="test_integration",
            type=IntegrationType.OAUTH2,
            endpoint="https://httpbin.org/delay/5",
            timeout=1
        )
        
        async with IntegrationValidator() as validator:
            result = await validator.test_integration(test)
            
            assert result.name == "test_integration"
            assert result.type == IntegrationType.OAUTH2
            assert result.status == IntegrationStatus.FAILED
            assert result.status_code is None
            assert result.response_time > 0
            assert "Timeout" in result.error_message
    
    @pytest.mark.asyncio
    async def test_validate_all(self, sample_config):
        """Testa validação de todas as integrações"""
        with patch.object(IntegrationValidator, 'load_config', return_value=sample_config):
            async with IntegrationValidator() as validator:
                results = await validator.validate_all()
                
                assert len(results) == 2
                assert all(isinstance(r, IntegrationResult) for r in results)
    
    def test_generate_report_empty_results(self):
        """Testa geração de relatório sem resultados"""
        validator = IntegrationValidator()
        report = validator.generate_report()
        
        assert "error" in report
        assert report["error"] == "Nenhum resultado disponível"
    
    def test_generate_report_with_results(self):
        """Testa geração de relatório com resultados"""
        validator = IntegrationValidator()
        
        # Adiciona resultados de teste
        validator.results = [
            IntegrationResult(
                name="test1",
                type=IntegrationType.OAUTH2,
                status=IntegrationStatus.HEALTHY,
                response_time=1.0,
                status_code=200
            ),
            IntegrationResult(
                name="test2",
                type=IntegrationType.PAYMENT,
                status=IntegrationStatus.FAILED,
                response_time=2.0,
                error_message="Connection failed"
            )
        ]
        
        report = validator.generate_report()
        
        assert "timestamp" in report
        assert "summary" in report
        assert "by_type" in report
        assert "details" in report
        
        summary = report["summary"]
        assert summary["total"] == 2
        assert summary["healthy"] == 1
        assert summary["failed"] == 1
        assert summary["health_percentage"] == 50.0
        assert summary["avg_response_time"] == 1.5
    
    def test_generate_report_save_to_file(self):
        """Testa salvamento de relatório em arquivo"""
        validator = IntegrationValidator()
        validator.results = [
            IntegrationResult(
                name="test1",
                type=IntegrationType.OAUTH2,
                status=IntegrationStatus.HEALTHY,
                response_time=1.0,
                status_code=200
            )
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            report = validator.generate_report(output_file)
            
            # Verifica se arquivo foi criado
            assert Path(output_file).exists()
            
            # Verifica conteúdo do arquivo
            with open(output_file, 'r') as f:
                saved_report = json.load(f)
            
            assert saved_report == report
            
        finally:
            Path(output_file).unlink(missing_ok=True)
    
    def test_print_summary(self, capsys):
        """Testa impressão do resumo"""
        validator = IntegrationValidator()
        validator.results = [
            IntegrationResult(
                name="test1",
                type=IntegrationType.OAUTH2,
                status=IntegrationStatus.HEALTHY,
                response_time=1.0,
                status_code=200
            ),
            IntegrationResult(
                name="test2",
                type=IntegrationType.PAYMENT,
                status=IntegrationStatus.FAILED,
                response_time=2.0,
                error_message="Connection failed"
            )
        ]
        
        report = validator.generate_report()
        validator.print_summary(report)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "RELATÓRIO DE VALIDAÇÃO DE INTEGRAÇÕES" in output
        assert "Total de Integrações: 2" in output
        assert "Saudáveis: 1" in output
        assert "Falharam: 1" in output
        assert "Saúde Geral: 50.0%" in output


class TestIntegrationTest:
    """Testes para a classe IntegrationTest"""
    
    def test_integration_test_creation(self):
        """Testa criação de teste de integração"""
        test = IntegrationTest(
            name="test_name",
            type=IntegrationType.OAUTH2,
            endpoint="https://test.com",
            method="POST",
            timeout=30,
            expected_status=201,
            headers={"Content-Type": "application/json"},
            data={"key": "value"},
            auth_required=True,
            fallback_enabled=True
        )
        
        assert test.name == "test_name"
        assert test.type == IntegrationType.OAUTH2
        assert test.endpoint == "https://test.com"
        assert test.method == "POST"
        assert test.timeout == 30
        assert test.expected_status == 201
        assert test.headers == {"Content-Type": "application/json"}
        assert test.data == {"key": "value"}
        assert test.auth_required is True
        assert test.fallback_enabled is True
    
    def test_integration_test_defaults(self):
        """Testa valores padrão do teste de integração"""
        test = IntegrationTest(
            name="test_name",
            type=IntegrationType.OAUTH2,
            endpoint="https://test.com"
        )
        
        assert test.method == "GET"
        assert test.timeout == 30
        assert test.expected_status == 200
        assert test.headers is None
        assert test.data is None
        assert test.auth_required is False
        assert test.fallback_enabled is False


class TestIntegrationResult:
    """Testes para a classe IntegrationResult"""
    
    def test_integration_result_creation(self):
        """Testa criação de resultado de integração"""
        result = IntegrationResult(
            name="test_name",
            type=IntegrationType.OAUTH2,
            status=IntegrationStatus.HEALTHY,
            response_time=1.5,
            status_code=200,
            error_message=None,
            fallback_used=False
        )
        
        assert result.name == "test_name"
        assert result.type == IntegrationType.OAUTH2
        assert result.status == IntegrationStatus.HEALTHY
        assert result.response_time == 1.5
        assert result.status_code == 200
        assert result.error_message is None
        assert result.fallback_used is False
        assert result.timestamp is not None
    
    def test_integration_result_timestamp_auto(self):
        """Testa geração automática de timestamp"""
        before = datetime.utcnow()
        result = IntegrationResult(
            name="test_name",
            type=IntegrationType.OAUTH2,
            status=IntegrationStatus.HEALTHY,
            response_time=1.0
        )
        after = datetime.utcnow()
        
        timestamp = datetime.fromisoformat(result.timestamp)
        assert before <= timestamp <= after
    
    def test_integration_result_custom_timestamp(self):
        """Testa timestamp customizado"""
        custom_timestamp = "2024-12-19T10:00:00"
        result = IntegrationResult(
            name="test_name",
            type=IntegrationType.OAUTH2,
            status=IntegrationStatus.HEALTHY,
            response_time=1.0,
            timestamp=custom_timestamp
        )
        
        assert result.timestamp == custom_timestamp


class TestIntegrationStatus:
    """Testes para o enum IntegrationStatus"""
    
    def test_integration_status_values(self):
        """Testa valores do enum IntegrationStatus"""
        assert IntegrationStatus.HEALTHY.value == "healthy"
        assert IntegrationStatus.DEGRADED.value == "degraded"
        assert IntegrationStatus.FAILED.value == "failed"
        assert IntegrationStatus.NOT_CONFIGURED.value == "not_configured"


class TestIntegrationType:
    """Testes para o enum IntegrationType"""
    
    def test_integration_type_values(self):
        """Testa valores do enum IntegrationType"""
        assert IntegrationType.OAUTH2.value == "oauth2"
        assert IntegrationType.PAYMENT.value == "payment"
        assert IntegrationType.WEBHOOK.value == "webhook"
        assert IntegrationType.API_EXTERNAL.value == "api_external"
        assert IntegrationType.NOTIFICATION.value == "notification"
        assert IntegrationType.BACKUP.value == "backup" 