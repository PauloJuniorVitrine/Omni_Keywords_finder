"""
Testes Unitários para Webhooks Seguros - Omni Keywords Finder
Testes abrangentes de segurança para webhooks
Prompt: Revisão de segurança de webhooks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import time
import uuid
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from backend.app.schemas.webhook_schemas import (
    WebhookEndpointSchema,
    WebhookPayloadSchema,
    WebhookSignatureSchema,
    WebhookHMACValidator
)
from backend.app.utils.webhook_logger import WebhookLogger, WebhookLogLevel, WebhookEventType
from backend.app.utils.webhook_rate_limiter import WebhookRateLimiter, ClientTier, RateLimitResult

class TestWebhookSchemas:
    """Testes para schemas de validação de webhooks"""
    
    def test_webhook_endpoint_schema_valid(self):
        """Testa schema de endpoint válido"""
        data = {
            "name": "Test Webhook",
            "url": "https://api.exemplo.com/webhook",
            "events": ["user.created", "payment.succeeded"],
            "secret": "my_secret_key_123456789",
            "security_level": "hmac",
            "timeout": 30,
            "retry_attempts": 3,
            "rate_limit": 100
        }
        
        webhook = WebhookEndpointSchema(**data)
        assert webhook.name == "Test Webhook"
        assert str(webhook.url) == "https://api.exemplo.com/webhook"
        assert webhook.events == ["user.created", "payment.succeeded"]
        assert webhook.secret == "my_secret_key_123456789"
        assert webhook.security_level == "hmac"
    
    def test_webhook_endpoint_schema_invalid_url(self):
        """Testa URL inválida"""
        data = {
            "name": "Test Webhook",
            "url": "http://localhost/webhook",  # HTTP não permitido
            "events": ["user.created"],
            "secret": "my_secret_key_123456789"
        }
        
        with pytest.raises(ValueError, match="URL deve usar HTTPS"):
            WebhookEndpointSchema(**data)
    
    def test_webhook_endpoint_schema_invalid_events(self):
        """Testa eventos inválidos"""
        data = {
            "name": "Test Webhook",
            "url": "https://api.exemplo.com/webhook",
            "events": ["invalid.event", "user.created"],
            "secret": "my_secret_key_123456789"
        }
        
        with pytest.raises(ValueError, match="Evento não suportado"):
            WebhookEndpointSchema(**data)
    
    def test_webhook_endpoint_schema_short_secret(self):
        """Testa secret muito curto"""
        data = {
            "name": "Test Webhook",
            "url": "https://api.exemplo.com/webhook",
            "events": ["user.created"],
            "secret": "short"  # Muito curto
        }
        
        with pytest.raises(ValueError, match="Secret deve ter pelo menos 16 caracteres"):
            WebhookEndpointSchema(**data)
    
    def test_webhook_endpoint_schema_xss_sanitization(self):
        """Testa sanitização contra XSS"""
        data = {
            "name": "Test<script>alert('xss')</script>",
            "url": "https://api.exemplo.com/webhook",
            "events": ["user.created"],
            "secret": "my_secret_key_123456789"
        }
        
        webhook = WebhookEndpointSchema(**data)
        assert "<script>" not in webhook.name
        assert "alert('xss')" not in webhook.name
    
    def test_webhook_payload_schema_valid(self):
        """Testa schema de payload válido"""
        data = {
            "event": "user.created",
            "data": {"user_id": "123", "email": "test@example.com"},
            "id": str(uuid.uuid4()),
            "source": "api",
            "version": "1.0"
        }
        
        payload = WebhookPayloadSchema(**data)
        assert payload.event == "user.created"
        assert payload.data["user_id"] == "123"
        assert payload.id == data["id"]
    
    def test_webhook_payload_schema_invalid_event(self):
        """Testa evento inválido no payload"""
        data = {
            "event": "invalid.event",
            "data": {"user_id": "123"},
            "id": str(uuid.uuid4())
        }
        
        with pytest.raises(ValueError, match="Evento não suportado"):
            WebhookPayloadSchema(**data)
    
    def test_webhook_payload_schema_invalid_id(self):
        """Testa ID inválido no payload"""
        data = {
            "event": "user.created",
            "data": {"user_id": "123"},
            "id": "invalid-uuid"
        }
        
        with pytest.raises(ValueError, match="ID deve ser um UUID válido"):
            WebhookPayloadSchema(**data)

class TestWebhookHMACValidator:
    """Testes para validação HMAC"""
    
    def test_generate_signature(self):
        """Testa geração de assinatura HMAC"""
        payload = '{"test": "data"}'
        secret = "my_secret_key_123456789"
        timestamp = "1640995200"
        
        signature = WebhookHMACValidator.generate_signature(payload, secret, timestamp)
        
        assert signature is not None
        assert len(signature) > 0
        # Verificar se é base64 válido
        import base64
        try:
            base64.b64decode(signature)
        except Exception:
            pytest.fail("Signature não é base64 válido")
    
    def test_validate_signature_valid(self):
        """Testa validação de assinatura válida"""
        payload = '{"test": "data"}'
        secret = "my_secret_key_123456789"
        timestamp = str(int(time.time()))
        
        signature = WebhookHMACValidator.generate_signature(payload, secret, timestamp)
        is_valid = WebhookHMACValidator.validate_signature(payload, signature, secret, timestamp)
        
        assert is_valid is True
    
    def test_validate_signature_invalid(self):
        """Testa validação de assinatura inválida"""
        payload = '{"test": "data"}'
        secret = "my_secret_key_123456789"
        timestamp = str(int(time.time()))
        
        # Assinatura incorreta
        invalid_signature = "invalid_signature"
        is_valid = WebhookHMACValidator.validate_signature(payload, invalid_signature, secret, timestamp)
        
        assert is_valid is False
    
    def test_validate_signature_old_timestamp(self):
        """Testa validação com timestamp antigo"""
        payload = '{"test": "data"}'
        secret = "my_secret_key_123456789"
        timestamp = str(int(time.time()) - 400)  # 400 segundos atrás
        
        signature = WebhookHMACValidator.generate_signature(payload, secret, timestamp)
        is_valid = WebhookHMACValidator.validate_signature(payload, signature, secret, timestamp)
        
        assert is_valid is False
    
    def test_validate_signature_future_timestamp(self):
        """Testa validação com timestamp futuro"""
        payload = '{"test": "data"}'
        secret = "my_secret_key_123456789"
        timestamp = str(int(time.time()) + 400)  # 400 segundos no futuro
        
        signature = WebhookHMACValidator.generate_signature(payload, secret, timestamp)
        is_valid = WebhookHMACValidator.validate_signature(payload, signature, secret, timestamp)
        
        assert is_valid is False

class TestWebhookLogger:
    """Testes para logger de webhooks"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.logger = WebhookLogger("test_webhooks.log")
    
    def test_log_webhook_created(self):
        """Testa log de webhook criado"""
        with patch.object(self.logger, '_log_entry') as mock_log:
            self.logger.log_webhook_created(
                endpoint_id="test-id",
                name="Test Webhook",
                url="https://api.exemplo.com/webhook",
                events=["user.created"],
                user_id="user-123",
                ip_address="192.168.1.1"
            )
            
            mock_log.assert_called_once()
            entry = mock_log.call_args[0][0]
            assert entry.event_type == WebhookEventType.CREATED.value
            assert entry.endpoint_id == "test-id"
            assert entry.user_id == "user-123"
            assert entry.ip_address == "192.168.1.1"
    
    def test_log_unauthorized(self):
        """Testa log de acesso não autorizado"""
        with patch.object(self.logger, '_log_entry') as mock_log:
            self.logger.log_unauthorized(
                endpoint_id="test-id",
                ip_address="192.168.1.1",
                user_agent="Test Agent",
                reason="Missing authentication"
            )
            
            mock_log.assert_called_once()
            entry = mock_log.call_args[0][0]
            assert entry.event_type == WebhookEventType.UNAUTHORIZED.value
            assert entry.level == WebhookLogLevel.SECURITY.value
            assert entry.details["reason"] == "Missing authentication"
    
    def test_log_rate_limited(self):
        """Testa log de rate limiting"""
        with patch.object(self.logger, '_log_entry') as mock_log:
            self.logger.log_rate_limited(
                endpoint_id="test-id",
                ip_address="192.168.1.1",
                rate_limit=100,
                current_count=101
            )
            
            mock_log.assert_called_once()
            entry = mock_log.call_args[0][0]
            assert entry.event_type == WebhookEventType.RATE_LIMITED.value
            assert entry.rate_limited is True
            assert entry.details["rate_limit"] == 100
            assert entry.details["current_count"] == 101
    
    def test_calculate_security_score(self):
        """Testa cálculo de score de segurança"""
        # HTTPS + HMAC
        score = self.logger._calculate_security_score(
            "https://api.exemplo.com/webhook",
            "hmac"
        )
        assert score >= 60
        
        # HTTP + none
        score = self.logger._calculate_security_score(
            "http://api.exemplo.com/webhook",
            "none"
        )
        assert score <= 30
        
        # localhost
        score = self.logger._calculate_security_score(
            "https://localhost/webhook",
            "hmac"
        )
        assert score < 60  # Penalizado por localhost

class TestWebhookRateLimiter:
    """Testes para rate limiter de webhooks"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.rate_limiter = WebhookRateLimiter()
    
    def test_get_client_tier_free(self):
        """Testa determinação de tier free"""
        tier = self.rate_limiter._get_client_tier()
        assert tier == ClientTier.FREE
    
    def test_get_client_tier_premium(self):
        """Testa determinação de tier premium"""
        tier = self.rate_limiter._get_client_tier(api_key="premium_key_123")
        assert tier == ClientTier.PREMIUM
    
    def test_get_client_tier_enterprise(self):
        """Testa determinação de tier enterprise"""
        tier = self.rate_limiter._get_client_tier(api_key="enterprise_key_123")
        assert tier == ClientTier.ENTERPRISE
    
    def test_get_identifier_api_key(self):
        """Testa geração de identificador com API key"""
        identifier = self.rate_limiter._get_identifier(
            "192.168.1.1",
            api_key="test_key"
        )
        assert identifier == "webhook:api:test_key"
    
    def test_get_identifier_user_id(self):
        """Testa geração de identificador com user_id"""
        identifier = self.rate_limiter._get_identifier(
            "192.168.1.1",
            user_id="user_123"
        )
        assert identifier == "webhook:user:user_123"
    
    def test_get_identifier_ip_only(self):
        """Testa geração de identificador apenas com IP"""
        identifier = self.rate_limiter._get_identifier("192.168.1.1")
        assert identifier == "webhook:ip:192.168.1.1"
    
    def test_check_rate_limit_allowed(self):
        """Testa rate limit permitido"""
        result = self.rate_limiter.check_rate_limit(
            ip_address="192.168.1.1"
        )
        assert result.allowed is True
        assert result.remaining >= 0
    
    def test_check_rate_limit_exceeded(self):
        """Testa rate limit excedido"""
        # Fazer múltiplas requisições para exceder o limite
        for i in range(10):  # Exceder limite de burst
            result = self.rate_limiter.check_rate_limit(
                ip_address="192.168.1.2"
            )
            if not result.allowed:
                break
        
        # A última deve ser bloqueada
        assert result.allowed is False
        assert result.reason is not None
        assert result.retry_after is not None
    
    def test_get_rate_limit_info(self):
        """Testa obtenção de informações de rate limit"""
        info = self.rate_limiter.get_rate_limit_info(
            ip_address="192.168.1.1"
        )
        
        assert "client_tier" in info
        assert "limits" in info
        assert "requests_per_hour" in info["limits"]
        assert "requests_per_minute" in info["limits"]
        assert "burst_limit" in info["limits"]
    
    def test_reset_rate_limit(self):
        """Testa reset de rate limit"""
        # Fazer algumas requisições
        for i in range(5):
            self.rate_limiter.check_rate_limit(ip_address="192.168.1.3")
        
        # Resetar
        success = self.rate_limiter.reset_rate_limit(ip_address="192.168.1.3")
        assert success is True
        
        # Verificar se foi resetado
        result = self.rate_limiter.check_rate_limit(ip_address="192.168.1.3")
        assert result.allowed is True

class TestWebhookSecurityIntegration:
    """Testes de integração de segurança"""
    
    def test_end_to_end_webhook_creation(self):
        """Testa criação completa de webhook com validação"""
        # Dados válidos
        data = {
            "name": "Secure Webhook",
            "url": "https://api.exemplo.com/webhook",
            "events": ["user.created", "payment.succeeded"],
            "secret": "my_very_secure_secret_key_123456789",
            "security_level": "hmac",
            "timeout": 30,
            "retry_attempts": 3,
            "rate_limit": 100
        }
        
        # Validar schema
        webhook = WebhookEndpointSchema(**data)
        assert webhook.name == "Secure Webhook"
        assert webhook.security_level == "hmac"
        
        # Simular payload
        payload_data = {
            "event": "user.created",
            "data": {"user_id": "123", "email": "test@example.com"},
            "id": str(uuid.uuid4()),
            "source": "api"
        }
        
        payload = WebhookPayloadSchema(**payload_data)
        assert payload.event == "user.created"
        
        # Gerar assinatura
        payload_str = json.dumps(payload_data)
        timestamp = str(int(time.time()))
        signature = WebhookHMACValidator.generate_signature(
            payload_str, webhook.secret, timestamp
        )
        
        # Validar assinatura
        is_valid = WebhookHMACValidator.validate_signature(
            payload_str, signature, webhook.secret, timestamp
        )
        assert is_valid is True
    
    def test_security_validation_chain(self):
        """Testa cadeia completa de validação de segurança"""
        # 1. Validar endpoint
        endpoint_data = {
            "name": "Test Endpoint",
            "url": "https://secure-api.com/webhook",
            "events": ["user.created"],
            "secret": "secure_secret_123456789",
            "security_level": "hmac"
        }
        
        endpoint = WebhookEndpointSchema(**endpoint_data)
        
        # 2. Validar payload
        payload_data = {
            "event": "user.created",
            "data": {"user_id": "123"},
            "id": str(uuid.uuid4())
        }
        
        payload = WebhookPayloadSchema(**payload_data)
        
        # 3. Gerar e validar assinatura
        payload_str = json.dumps(payload_data)
        timestamp = str(int(time.time()))
        signature = WebhookHMACValidator.generate_signature(
            payload_str, endpoint.secret, timestamp
        )
        
        is_valid = WebhookHMACValidator.validate_signature(
            payload_str, signature, endpoint.secret, timestamp
        )
        
        # 4. Verificar rate limiting
        rate_limiter = WebhookRateLimiter()
        rate_result = rate_limiter.check_rate_limit(ip_address="192.168.1.1")
        
        # Todas as validações devem passar
        assert endpoint.name == "Test Endpoint"
        assert payload.event == "user.created"
        assert is_valid is True
        assert rate_result.allowed is True
    
    def test_malicious_payload_detection(self):
        """Testa detecção de payloads maliciosos"""
        # Payload com tentativa de XSS
        malicious_data = {
            "name": "Test<script>alert('xss')</script>",
            "url": "https://api.exemplo.com/webhook",
            "events": ["user.created"],
            "secret": "my_secret_key_123456789"
        }
        
        # Deve sanitizar automaticamente
        webhook = WebhookEndpointSchema(**malicious_data)
        assert "<script>" not in webhook.name
        assert "alert('xss')" not in webhook.name
        
        # Payload com eventos inválidos
        invalid_events_data = {
            "name": "Test",
            "url": "https://api.exemplo.com/webhook",
            "events": ["invalid.event", "user.created"],
            "secret": "my_secret_key_123456789"
        }
        
        with pytest.raises(ValueError, match="Evento não suportado"):
            WebhookEndpointSchema(**invalid_events_data)
    
    def test_rate_limiting_different_tiers(self):
        """Testa rate limiting para diferentes tiers"""
        rate_limiter = WebhookRateLimiter()
        
        # Free tier
        free_result = rate_limiter.check_rate_limit(ip_address="192.168.1.1")
        free_info = rate_limiter.get_rate_limit_info(ip_address="192.168.1.1")
        assert free_info["client_tier"] == "free"
        assert free_info["limits"]["requests_per_hour"] == 100
        
        # Premium tier
        premium_result = rate_limiter.check_rate_limit(
            ip_address="192.168.1.2",
            api_key="premium_key_123"
        )
        premium_info = rate_limiter.get_rate_limit_info(
            ip_address="192.168.1.2",
            api_key="premium_key_123"
        )
        assert premium_info["client_tier"] == "premium"
        assert premium_info["limits"]["requests_per_hour"] == 10000
    
    def test_logging_security_events(self):
        """Testa logging de eventos de segurança"""
        logger = WebhookLogger()
        
        with patch.object(logger, '_log_entry') as mock_log:
            # Log de webhook criado
            logger.log_webhook_created(
                endpoint_id="test-id",
                name="Test Webhook",
                url="https://api.exemplo.com/webhook",
                events=["user.created"],
                user_id="user-123",
                ip_address="192.168.1.1"
            )
            
            # Log de acesso não autorizado
            logger.log_unauthorized(
                endpoint_id="test-id",
                ip_address="192.168.1.1",
                user_agent="Malicious Agent",
                reason="Invalid signature"
            )
            
            # Log de rate limiting
            logger.log_rate_limited(
                endpoint_id="test-id",
                ip_address="192.168.1.1",
                rate_limit=100,
                current_count=101
            )
            
            # Verificar se todos os logs foram registrados
            assert mock_log.call_count == 3
            
            # Verificar tipos de eventos
            calls = mock_log.call_args_list
            event_types = [call[0][0].event_type for call in calls]
            assert "webhook_created" in event_types
            assert "unauthorized" in event_types
            assert "rate_limited" in event_types 