"""
Testes Unitários para Webhook Logger
Logger Especializado para Webhooks - Omni Keywords Finder

Prompt: Implementação de testes unitários para logger de webhooks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import logging
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List

from backend.app.utils.webhook_logger import (
    WebhookLogger,
    WebhookLogEntry,
    WebhookLogLevel,
    WebhookEventType
)


class TestWebhookLogLevel:
    """Testes para enum WebhookLogLevel"""
    
    def test_webhook_log_level_values(self):
        """Testa valores do enum WebhookLogLevel"""
        assert WebhookLogLevel.INFO.value == "info"
        assert WebhookLogLevel.WARNING.value == "warning"
        assert WebhookLogLevel.ERROR.value == "error"
        assert WebhookLogLevel.SECURITY.value == "security"
        assert WebhookLogLevel.AUDIT.value == "audit"
    
    def test_webhook_log_level_comparison(self):
        """Testa comparação entre níveis de log"""
        assert WebhookLogLevel.INFO != WebhookLogLevel.WARNING
        assert WebhookLogLevel.SECURITY != WebhookLogLevel.AUDIT
        assert WebhookLogLevel.INFO == WebhookLogLevel.INFO


class TestWebhookEventType:
    """Testes para enum WebhookEventType"""
    
    def test_webhook_event_type_values(self):
        """Testa valores do enum WebhookEventType"""
        assert WebhookEventType.CREATED.value == "webhook_created"
        assert WebhookEventType.UPDATED.value == "webhook_updated"
        assert WebhookEventType.DELETED.value == "webhook_deleted"
        assert WebhookEventType.TRIGGERED.value == "webhook_triggered"
        assert WebhookEventType.DELIVERED.value == "webhook_delivered"
        assert WebhookEventType.FAILED.value == "webhook_failed"
        assert WebhookEventType.RETRY.value == "webhook_retry"
        assert WebhookEventType.SIGNATURE_VALIDATED.value == "signature_validated"
        assert WebhookEventType.SIGNATURE_INVALID.value == "signature_invalid"
        assert WebhookEventType.RATE_LIMITED.value == "rate_limited"
        assert WebhookEventType.UNAUTHORIZED.value == "unauthorized"
        assert WebhookEventType.MALFORMED.value == "malformed_payload"
    
    def test_webhook_event_type_comparison(self):
        """Testa comparação entre tipos de eventos"""
        assert WebhookEventType.CREATED != WebhookEventType.UPDATED
        assert WebhookEventType.TRIGGERED != WebhookEventType.DELIVERED
        assert WebhookEventType.CREATED == WebhookEventType.CREATED


class TestWebhookLogEntry:
    """Testes para WebhookLogEntry"""
    
    def test_webhook_log_entry_creation(self):
        """Testa criação de WebhookLogEntry"""
        entry = WebhookLogEntry(
            log_id="test_log_123",
            timestamp="2025-01-27T10:00:00Z",
            level="info",
            event_type="webhook_created",
            endpoint_id="endpoint_123",
            event_id="event_456",
            user_id="user_789",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            message="Webhook criado com sucesso",
            details={"name": "test_webhook"},
            signature_valid=True,
            rate_limited=False,
            security_score=85,
            response_time=0.5,
            payload_size=1024
        )
        
        assert entry.log_id == "test_log_123"
        assert entry.timestamp == "2025-01-27T10:00:00Z"
        assert entry.level == "info"
        assert entry.event_type == "webhook_created"
        assert entry.endpoint_id == "endpoint_123"
        assert entry.event_id == "event_456"
        assert entry.user_id == "user_789"
        assert entry.ip_address == "192.168.1.1"
        assert entry.user_agent == "Mozilla/5.0"
        assert entry.message == "Webhook criado com sucesso"
        assert entry.details == {"name": "test_webhook"}
        assert entry.signature_valid is True
        assert entry.rate_limited is False
        assert entry.security_score == 85
        assert entry.response_time == 0.5
        assert entry.payload_size == 1024
        assert entry.source == "webhook_system"
        assert entry.version == "1.0"
        assert entry.environment == "production"
    
    def test_webhook_log_entry_default_values(self):
        """Testa valores padrão de WebhookLogEntry"""
        entry = WebhookLogEntry(
            log_id="test_log_123",
            timestamp="2025-01-27T10:00:00Z",
            level="info",
            event_type="webhook_created",
            message="Test message"
        )
        
        assert entry.endpoint_id is None
        assert entry.event_id is None
        assert entry.user_id is None
        assert entry.ip_address is None
        assert entry.user_agent is None
        assert entry.details is None
        assert entry.signature_valid is None
        assert entry.rate_limited is None
        assert entry.security_score is None
        assert entry.response_time is None
        assert entry.payload_size is None
        assert entry.source == "webhook_system"
        assert entry.version == "1.0"
        assert entry.environment == "production"


class TestWebhookLogger:
    """Testes para WebhookLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def webhook_logger(self, temp_log_file):
        """Instância do WebhookLogger para testes"""
        return WebhookLogger(log_file=temp_log_file)
    
    def test_webhook_logger_initialization(self, webhook_logger, temp_log_file):
        """Testa inicialização do WebhookLogger"""
        assert webhook_logger.log_file == temp_log_file
        assert webhook_logger.logger is not None
        assert isinstance(webhook_logger.logger, logging.Logger)
        assert webhook_logger.logger.name == "webhook_logger"
    
    def test_setup_logger(self, webhook_logger):
        """Testa configuração do logger"""
        logger = webhook_logger._setup_logger()
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "webhook_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_create_log_entry(self, webhook_logger):
        """Testa criação de entrada de log"""
        entry = webhook_logger._create_log_entry(
            level=WebhookLogLevel.INFO,
            event_type=WebhookEventType.CREATED,
            message="Test message",
            endpoint_id="endpoint_123",
            user_id="user_456"
        )
        
        assert isinstance(entry, WebhookLogEntry)
        assert entry.level == "info"
        assert entry.event_type == "webhook_created"
        assert entry.message == "Test message"
        assert entry.endpoint_id == "endpoint_123"
        assert entry.user_id == "user_456"
        assert entry.log_id is not None
        assert entry.timestamp is not None
        assert entry.source == "webhook_system"
        assert entry.version == "1.0"
        assert entry.environment == "production"
    
    def test_log_entry_info(self, webhook_logger, temp_log_file):
        """Testa log de entrada com nível INFO"""
        entry = WebhookLogEntry(
            log_id="test_123",
            timestamp="2025-01-27T10:00:00Z",
            level="info",
            event_type="webhook_created",
            message="Test info message"
        )
        
        webhook_logger._log_entry(entry)
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Test info message" in log_content
    
    def test_log_entry_error(self, webhook_logger, temp_log_file):
        """Testa log de entrada com nível ERROR"""
        entry = WebhookLogEntry(
            log_id="test_123",
            timestamp="2025-01-27T10:00:00Z",
            level="error",
            event_type="webhook_failed",
            message="Test error message"
        )
        
        webhook_logger._log_entry(entry)
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Test error message" in log_content
    
    def test_log_entry_security(self, webhook_logger, temp_log_file):
        """Testa log de entrada com nível SECURITY"""
        entry = WebhookLogEntry(
            log_id="test_123",
            timestamp="2025-01-27T10:00:00Z",
            level="security",
            event_type="unauthorized",
            message="Test security message"
        )
        
        webhook_logger._log_entry(entry)
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "[SECURITY]" in log_content
            assert "Test security message" in log_content
    
    def test_log_entry_audit(self, webhook_logger, temp_log_file):
        """Testa log de entrada com nível AUDIT"""
        entry = WebhookLogEntry(
            log_id="test_123",
            timestamp="2025-01-27T10:00:00Z",
            level="audit",
            event_type="webhook_created",
            message="Test audit message"
        )
        
        webhook_logger._log_entry(entry)
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "[AUDIT]" in log_content
            assert "Test audit message" in log_content
    
    def test_log_webhook_created(self, webhook_logger, temp_log_file):
        """Testa log de webhook criado"""
        webhook_logger.log_webhook_created(
            endpoint_id="endpoint_123",
            name="Test Webhook",
            url="https://example.com/webhook",
            events=["user.created", "user.updated"],
            user_id="user_456",
            ip_address="192.168.1.1",
            security_level="hmac"
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Webhook criado: Test Webhook" in log_content
            assert "endpoint_123" in log_content
            assert "user_456" in log_content
            assert "192.168.1.1" in log_content
    
    def test_log_webhook_updated(self, webhook_logger, temp_log_file):
        """Testa log de webhook atualizado"""
        changes = {"url": "https://new-example.com/webhook", "events": ["user.deleted"]}
        
        webhook_logger.log_webhook_updated(
            endpoint_id="endpoint_123",
            changes=changes,
            user_id="user_456",
            ip_address="192.168.1.1"
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Webhook atualizado: endpoint_123" in log_content
            assert "user_456" in log_content
            assert "192.168.1.1" in log_content
    
    def test_log_webhook_deleted(self, webhook_logger, temp_log_file):
        """Testa log de webhook deletado"""
        webhook_logger.log_webhook_deleted(
            endpoint_id="endpoint_123",
            name="Test Webhook",
            user_id="user_456",
            ip_address="192.168.1.1"
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Webhook deletado: Test Webhook" in log_content
            assert "endpoint_123" in log_content
            assert "user_456" in log_content
            assert "192.168.1.1" in log_content
    
    def test_log_webhook_triggered(self, webhook_logger, temp_log_file):
        """Testa log de webhook disparado"""
        webhook_logger.log_webhook_triggered(
            endpoint_id="endpoint_123",
            event_id="event_456",
            event_type="user.created",
            payload_size=1024,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Webhook disparado: user.created" in log_content
            assert "endpoint_123" in log_content
            assert "event_456" in log_content
            assert "192.168.1.1" in log_content
    
    def test_log_webhook_delivered(self, webhook_logger, temp_log_file):
        """Testa log de webhook entregue"""
        webhook_logger.log_webhook_delivered(
            endpoint_id="endpoint_123",
            event_id="event_456",
            response_status=200,
            response_time=0.5
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Webhook entregue: 200" in log_content
            assert "endpoint_123" in log_content
            assert "event_456" in log_content
    
    def test_log_webhook_failed(self, webhook_logger, temp_log_file):
        """Testa log de falha na entrega do webhook"""
        webhook_logger.log_webhook_failed(
            endpoint_id="endpoint_123",
            event_id="event_456",
            error_message="Connection timeout",
            attempt_count=3
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Falha na entrega: Connection timeout" in log_content
            assert "endpoint_123" in log_content
            assert "event_456" in log_content
    
    def test_log_webhook_retry(self, webhook_logger, temp_log_file):
        """Testa log de retry de webhook"""
        next_retry = datetime.now(timezone.utc)
        
        webhook_logger.log_webhook_retry(
            endpoint_id="endpoint_123",
            event_id="event_456",
            attempt_count=2,
            next_retry=next_retry
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Retry agendado: tentativa 2" in log_content
            assert "endpoint_123" in log_content
            assert "event_456" in log_content
    
    def test_log_signature_validated_valid(self, webhook_logger, temp_log_file):
        """Testa log de validação de assinatura válida"""
        webhook_logger.log_signature_validated(
            endpoint_id="endpoint_123",
            signature_valid=True,
            timestamp="2025-01-27T10:00:00Z"
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Assinatura válida" in log_content
            assert "endpoint_123" in log_content
            assert "[SECURITY]" in log_content
    
    def test_log_signature_validated_invalid(self, webhook_logger, temp_log_file):
        """Testa log de validação de assinatura inválida"""
        webhook_logger.log_signature_validated(
            endpoint_id="endpoint_123",
            signature_valid=False,
            timestamp="2025-01-27T10:00:00Z"
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Assinatura inválida" in log_content
            assert "endpoint_123" in log_content
            assert "[SECURITY]" in log_content
    
    def test_log_rate_limited(self, webhook_logger, temp_log_file):
        """Testa log de rate limiting"""
        webhook_logger.log_rate_limited(
            endpoint_id="endpoint_123",
            ip_address="192.168.1.1",
            rate_limit=100,
            current_count=101
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Rate limit excedido: 101/100" in log_content
            assert "endpoint_123" in log_content
            assert "192.168.1.1" in log_content
    
    def test_log_unauthorized(self, webhook_logger, temp_log_file):
        """Testa log de acesso não autorizado"""
        webhook_logger.log_unauthorized(
            endpoint_id="endpoint_123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            reason="Invalid API key"
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Acesso não autorizado: Invalid API key" in log_content
            assert "endpoint_123" in log_content
            assert "192.168.1.1" in log_content
            assert "[SECURITY]" in log_content
    
    def test_log_malformed_payload(self, webhook_logger, temp_log_file):
        """Testa log de payload malformado"""
        errors = ["Invalid JSON", "Missing required field"]
        
        webhook_logger.log_malformed_payload(
            endpoint_id="endpoint_123",
            ip_address="192.168.1.1",
            errors=errors
        )
        
        # Verificar se o log foi escrito no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Payload malformado: 2 erros" in log_content
            assert "endpoint_123" in log_content
            assert "192.168.1.1" in log_content
    
    def test_calculate_security_score_https_both(self, webhook_logger):
        """Testa cálculo de score de segurança com HTTPS e both"""
        score = webhook_logger._calculate_security_score("https://example.com/webhook", "both")
        
        assert score == 70  # 30 (HTTPS) + 40 (both)
    
    def test_calculate_security_score_https_hmac(self, webhook_logger):
        """Testa cálculo de score de segurança com HTTPS e HMAC"""
        score = webhook_logger._calculate_security_score("https://example.com/webhook", "hmac")
        
        assert score == 60  # 30 (HTTPS) + 30 (hmac)
    
    def test_calculate_security_score_https_api_key(self, webhook_logger):
        """Testa cálculo de score de segurança com HTTPS e API key"""
        score = webhook_logger._calculate_security_score("https://example.com/webhook", "api_key")
        
        assert score == 50  # 30 (HTTPS) + 20 (api_key)
    
    def test_calculate_security_score_http_none(self, webhook_logger):
        """Testa cálculo de score de segurança com HTTP e none"""
        score = webhook_logger._calculate_security_score("http://example.com/webhook", "none")
        
        assert score == 10  # 10 (HTTP) + 0 (none)
    
    def test_calculate_security_score_localhost(self, webhook_logger):
        """Testa cálculo de score de segurança com localhost"""
        score = webhook_logger._calculate_security_score("https://localhost/webhook", "hmac")
        
        assert score == 40  # 30 (HTTPS) + 30 (hmac) - 20 (localhost)
    
    def test_calculate_security_score_minimum(self, webhook_logger):
        """Testa cálculo de score de segurança mínimo"""
        score = webhook_logger._calculate_security_score("http://localhost/webhook", "none")
        
        assert score == 0  # 10 (HTTP) + 0 (none) - 20 (localhost) = -10, mas mínimo é 0
    
    def test_calculate_security_score_maximum(self, webhook_logger):
        """Testa cálculo de score de segurança máximo"""
        score = webhook_logger._calculate_security_score("https://example.com/webhook", "both")
        
        assert score == 70  # 30 (HTTPS) + 40 (both) = 70, máximo é 100
    
    def test_get_security_report(self, webhook_logger):
        """Testa geração de relatório de segurança"""
        start_date = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        
        report = webhook_logger.get_security_report(start_date, end_date, "endpoint_123")
        
        assert report["period"]["start"] == start_date.isoformat()
        assert report["period"]["end"] == end_date.isoformat()
        assert report["endpoint_id"] == "endpoint_123"
        assert report["total_events"] == 0
        assert report["security_events"] == 0
        assert report["failed_deliveries"] == 0
        assert report["rate_limit_violations"] == 0
        assert report["unauthorized_access"] == 0
        assert report["average_security_score"] == 0
        assert isinstance(report["recommendations"], list)
    
    def test_export_logs(self, webhook_logger):
        """Testa exportação de logs"""
        start_date = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        
        logs = webhook_logger.export_logs(
            start_date,
            end_date,
            [WebhookEventType.CREATED, WebhookEventType.FAILED],
            "endpoint_123"
        )
        
        assert isinstance(logs, list)


class TestWebhookLoggerIntegration:
    """Testes de integração para WebhookLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def webhook_logger(self, temp_log_file):
        """Instância do WebhookLogger para testes"""
        return WebhookLogger(log_file=temp_log_file)
    
    def test_complete_webhook_lifecycle_logging(self, webhook_logger, temp_log_file):
        """Testa logging completo do ciclo de vida de um webhook"""
        # Criar webhook
        webhook_logger.log_webhook_created(
            endpoint_id="endpoint_123",
            name="Test Webhook",
            url="https://example.com/webhook",
            events=["user.created"],
            user_id="user_456",
            ip_address="192.168.1.1",
            security_level="hmac"
        )
        
        # Atualizar webhook
        webhook_logger.log_webhook_updated(
            endpoint_id="endpoint_123",
            changes={"url": "https://new-example.com/webhook"},
            user_id="user_456",
            ip_address="192.168.1.1"
        )
        
        # Disparar webhook
        webhook_logger.log_webhook_triggered(
            endpoint_id="endpoint_123",
            event_id="event_456",
            event_type="user.created",
            payload_size=512,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Validar assinatura
        webhook_logger.log_signature_validated(
            endpoint_id="endpoint_123",
            signature_valid=True,
            timestamp="2025-01-27T10:00:00Z"
        )
        
        # Entregar webhook
        webhook_logger.log_webhook_delivered(
            endpoint_id="endpoint_123",
            event_id="event_456",
            response_status=200,
            response_time=0.3
        )
        
        # Verificar logs no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            
            # Verificar se todos os eventos foram logados
            assert "Webhook criado: Test Webhook" in log_content
            assert "Webhook atualizado: endpoint_123" in log_content
            assert "Webhook disparado: user.created" in log_content
            assert "Assinatura válida" in log_content
            assert "Webhook entregue: 200" in log_content
            
            # Verificar se os IDs estão presentes
            assert "endpoint_123" in log_content
            assert "event_456" in log_content
            assert "user_456" in log_content
    
    def test_security_incident_logging(self, webhook_logger, temp_log_file):
        """Testa logging de incidentes de segurança"""
        # Tentativa de acesso não autorizado
        webhook_logger.log_unauthorized(
            endpoint_id="endpoint_123",
            ip_address="192.168.1.100",
            user_agent="curl/7.68.0",
            reason="Invalid API key"
        )
        
        # Rate limiting
        webhook_logger.log_rate_limited(
            endpoint_id="endpoint_123",
            ip_address="192.168.1.100",
            rate_limit=100,
            current_count=150
        )
        
        # Assinatura inválida
        webhook_logger.log_signature_validated(
            endpoint_id="endpoint_123",
            signature_valid=False,
            timestamp="2025-01-27T10:00:00Z"
        )
        
        # Payload malformado
        webhook_logger.log_malformed_payload(
            endpoint_id="endpoint_123",
            ip_address="192.168.1.100",
            errors=["Invalid JSON format", "Missing required field: user_id"]
        )
        
        # Verificar logs no arquivo
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            
            # Verificar se todos os incidentes foram logados
            assert "Acesso não autorizado: Invalid API key" in log_content
            assert "Rate limit excedido: 150/100" in log_content
            assert "Assinatura inválida" in log_content
            assert "Payload malformado: 2 erros" in log_content
            
            # Verificar se os logs de segurança estão marcados
            assert "[SECURITY]" in log_content


class TestWebhookLoggerErrorHandling:
    """Testes de tratamento de erros para WebhookLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def webhook_logger(self, temp_log_file):
        """Instância do WebhookLogger para testes"""
        return WebhookLogger(log_file=temp_log_file)
    
    def test_log_entry_with_json_error(self, webhook_logger, temp_log_file):
        """Testa log de entrada com erro de JSON"""
        # Criar entrada com dados não serializáveis
        entry = WebhookLogEntry(
            log_id="test_123",
            timestamp="2025-01-27T10:00:00Z",
            level="info",
            event_type="webhook_created",
            message="Test message",
            details={"non_serializable": lambda x: x}  # Função não serializável
        )
        
        # Deve fazer fallback para log simples
        webhook_logger._log_entry(entry)
        
        # Verificar se o fallback funcionou
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert "Log simples: Test message" in log_content


class TestWebhookLoggerPerformance:
    """Testes de performance para WebhookLogger"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Arquivo de log temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        yield temp_file
        
        # Limpar arquivo após teste
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    @pytest.fixture
    def webhook_logger(self, temp_log_file):
        """Instância do WebhookLogger para testes"""
        return WebhookLogger(log_file=temp_log_file)
    
    def test_multiple_log_entries_performance(self, webhook_logger, temp_log_file):
        """Testa performance de múltiplas entradas de log"""
        import time
        
        start_time = time.time()
        
        # Criar múltiplas entradas de log
        for i in range(1000):
            webhook_logger.log_webhook_triggered(
                endpoint_id=f"endpoint_{i}",
                event_id=f"event_{i}",
                event_type="user.created",
                payload_size=512,
                ip_address=f"192.168.1.{i % 256}",
                user_agent="Mozilla/5.0"
            )
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 10.0  # Menos de 10 segundos para 1000 logs
        
        # Verificar se todos os logs foram escritos
        with open(temp_log_file, 'r') as f:
            log_lines = f.readlines()
            assert len(log_lines) == 1000


if __name__ == "__main__":
    pytest.main([__file__]) 