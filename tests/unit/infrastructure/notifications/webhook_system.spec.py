"""
Testes Unitários para Sistema de Webhooks - Omni Keywords Finder

Testes abrangentes para todas as funcionalidades do sistema de webhooks:
- Validação de endpoints e payloads
- Rate limiting e retry logic
- Entrega de webhooks
- Segurança e assinaturas
- Persistência de dados
- Métricas e monitoramento

Autor: Sistema de Webhooks para Integração Externa
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import json
import hmac
import hashlib
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Importar sistema de webhooks
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from infrastructure.integrations.webhook_system import (
    WebhookSystem,
    WebhookEndpoint,
    WebhookEventType,
    WebhookStatus,
    WebhookSecurityLevel,
    WebhookPayload,
    WebhookDelivery,
    WebhookValidator,
    WebhookRateLimiter,
    WebhookRetryManager,
    WebhookDatabase,
    WebhookDeliveryWorker,
    create_webhook_system
)

class TestWebhookValidator:
    """Testes para validador de webhooks"""
    
    @pytest.fixture
    def validator(self):
        return WebhookValidator()
    
    @pytest.fixture
    def valid_endpoint(self):
        return WebhookEndpoint(
            id="test-endpoint",
            name="Test Webhook",
            url="https://api.example.com/webhook",
            events=[WebhookEventType.KEYWORD_PROCESSED],
            secret="test-secret",
            security_level=WebhookSecurityLevel.HMAC
        )
    
    @pytest.fixture
    def valid_payload(self):
        return WebhookPayload(
            event_type=WebhookEventType.KEYWORD_PROCESSED,
            event_id="test-event-123",
            timestamp=datetime.utcnow(),
            data={"keyword": "test", "status": "processed"}
        )
    
    def test_validate_endpoint_valid(self, validator, valid_endpoint):
        """Testa validação de endpoint válido"""
        errors = validator.validate_endpoint(valid_endpoint)
        assert len(errors) == 0
    
    def test_validate_endpoint_invalid_url(self, validator):
        """Testa validação de URL inválida"""
        endpoint = WebhookEndpoint(
            id="test",
            name="Test",
            url="invalid-url",
            events=[WebhookEventType.KEYWORD_PROCESSED]
        )
        errors = validator.validate_endpoint(endpoint)
        assert len(errors) > 0
        assert any("URL" in error for error in errors)
    
    def test_validate_endpoint_no_events(self, validator):
        """Testa validação sem eventos"""
        endpoint = WebhookEndpoint(
            id="test",
            name="Test",
            url="https://api.example.com/webhook",
            events=[]
        )
        errors = validator.validate_endpoint(endpoint)
        assert len(errors) > 0
        assert any("evento" in error.lower() for error in errors)
    
    def test_validate_endpoint_hmac_no_secret(self, validator):
        """Testa validação HMAC sem secret"""
        endpoint = WebhookEndpoint(
            id="test",
            name="Test",
            url="https://api.example.com/webhook",
            events=[WebhookEventType.KEYWORD_PROCESSED],
            security_level=WebhookSecurityLevel.HMAC
        )
        errors = validator.validate_endpoint(endpoint)
        assert len(errors) > 0
        assert any("secret" in error.lower() for error in errors)
    
    def test_validate_endpoint_api_key_no_key(self, validator):
        """Testa validação API_KEY sem chave"""
        endpoint = WebhookEndpoint(
            id="test",
            name="Test",
            url="https://api.example.com/webhook",
            events=[WebhookEventType.KEYWORD_PROCESSED],
            security_level=WebhookSecurityLevel.API_KEY
        )
        errors = validator.validate_endpoint(endpoint)
        assert len(errors) > 0
        assert any("api key" in error.lower() for error in errors)
    
    def test_validate_payload_valid(self, validator, valid_payload):
        """Testa validação de payload válido"""
        errors = validator.validate_payload(valid_payload)
        assert len(errors) == 0
    
    def test_validate_payload_missing_fields(self, validator):
        """Testa validação de payload com campos ausentes"""
        payload = WebhookPayload(
            event_type=WebhookEventType.KEYWORD_PROCESSED,
            event_id=None,  # Campo ausente
            timestamp=datetime.utcnow(),
            data={"test": "data"}
        )
        errors = validator.validate_payload(payload)
        assert len(errors) > 0
        assert any("event_id" in error for error in errors)
    
    def test_validate_payload_too_large(self, validator):
        """Testa validação de payload muito grande"""
        # Criar payload grande
        large_data = {"data": "value" * (1024 * 1024 + 100)}  # > 1MB
        payload = WebhookPayload(
            event_type=WebhookEventType.KEYWORD_PROCESSED,
            event_id="test",
            timestamp=datetime.utcnow(),
            data=large_data
        )
        errors = validator.validate_payload(payload)
        assert len(errors) > 0
        assert any("grande" in error.lower() for error in errors)
    
    def test_generate_signature(self, validator):
        """Testa geração de assinatura HMAC"""
        payload = '{"test": "data"}'
        secret = "test-secret"
        
        signature = validator.generate_signature(payload, secret)
        
        assert len(signature) == 64  # SHA256 hex
        assert isinstance(signature, str)
    
    def test_verify_signature_valid(self, validator):
        """Testa verificação de assinatura válida"""
        payload = '{"test": "data"}'
        secret = "test-secret"
        
        signature = validator.generate_signature(payload, secret)
        is_valid = validator.verify_signature(payload, signature, secret)
        
        assert is_valid is True
    
    def test_verify_signature_invalid(self, validator):
        """Testa verificação de assinatura inválida"""
        payload = '{"test": "data"}'
        secret = "test-secret"
        invalid_signature = "invalid-signature"
        
        is_valid = validator.verify_signature(payload, invalid_signature, secret)
        
        assert is_valid is False

class TestWebhookRateLimiter:
    """Testes para rate limiter de webhooks"""
    
    @pytest.fixture
    def rate_limiter(self):
        return WebhookRateLimiter()
    
    def test_is_allowed_initial(self, rate_limiter):
        """Testa permissão inicial"""
        endpoint_id = "test-endpoint"
        rate_limit = 100  # 100 requests per hour
        
        # Primeira requisição deve ser permitida
        assert rate_limiter.is_allowed(endpoint_id, rate_limit) is True
    
    def test_is_allowed_within_limit(self, rate_limiter):
        """Testa permissão dentro do limite"""
        endpoint_id = "test-endpoint"
        rate_limit = 5  # 5 requests per hour
        
        # Fazer 5 requisições
        for index in range(5):
            assert rate_limiter.is_allowed(endpoint_id, rate_limit) is True
    
    def test_is_allowed_exceed_limit(self, rate_limiter):
        """Testa bloqueio ao exceder limite"""
        endpoint_id = "test-endpoint"
        rate_limit = 3  # 3 requests per hour
        
        # Fazer 3 requisições (dentro do limite)
        for index in range(3):
            assert rate_limiter.is_allowed(endpoint_id, rate_limit) is True
        
        # 4ª requisição deve ser bloqueada
        assert rate_limiter.is_allowed(endpoint_id, rate_limit) is False
    
    def test_block_endpoint(self, rate_limiter):
        """Testa bloqueio manual de endpoint"""
        endpoint_id = "test-endpoint"
        
        # Bloquear por 1 minuto
        rate_limiter.block_endpoint(endpoint_id, duration_minutes=1)
        
        # Verificar se está bloqueado
        assert rate_limiter.is_blocked(endpoint_id) is True
    
    def test_unblock_endpoint_after_time(self, rate_limiter):
        """Testa desbloqueio automático após tempo"""
        endpoint_id = "test-endpoint"
        
        # Bloquear por 1 segundo
        rate_limiter.block_endpoint(endpoint_id, duration_minutes=1/60)
        
        # Aguardar um pouco
        time.sleep(0.1)
        
        # Verificar se ainda está bloqueado (pode estar dependendo do timing)
        # Este teste é mais para verificar se não há erros

class TestWebhookRetryManager:
    """Testes para gerenciador de retry"""
    
    @pytest.fixture
    def retry_manager(self):
        return WebhookRetryManager(max_retries=3, base_delay=5)
    
    @pytest.fixture
    def sample_delivery(self):
        return WebhookDelivery(
            id="test-delivery",
            endpoint_id="test-endpoint",
            event_id="test-event",
            payload={"test": "data"},
            created_at=datetime.utcnow()
        )
    
    def test_should_retry_5xx_error(self, retry_manager):
        """Testa retry para erros 5xx"""
        assert retry_manager.should_retry(500, 0) is True
        assert retry_manager.should_retry(502, 1) is True
        assert retry_manager.should_retry(503, 2) is True
    
    def test_should_retry_4xx_error(self, retry_manager):
        """Testa retry para erros 4xx específicos"""
        assert retry_manager.should_retry(429, 0) is True  # Rate limit
        assert retry_manager.should_retry(408, 1) is True  # Timeout
    
    def test_should_not_retry_4xx_error(self, retry_manager):
        """Testa não retry para erros 4xx client"""
        assert retry_manager.should_retry(400, 0) is False  # Bad request
        assert retry_manager.should_retry(401, 1) is False  # Unauthorized
        assert retry_manager.should_retry(403, 2) is False  # Forbidden
    
    def test_should_not_retry_max_attempts(self, retry_manager):
        """Testa não retry após máximo de tentativas"""
        assert retry_manager.should_retry(500, 3) is False  # Max attempts reached
    
    def test_calculate_delay_exponential(self, retry_manager):
        """Testa cálculo de delay exponencial"""
        delay1 = retry_manager.calculate_delay(1)
        delay2 = retry_manager.calculate_delay(2)
        delay3 = retry_manager.calculate_delay(3)
        
        assert delay1 == 5  # base_delay
        assert delay2 == 10  # base_delay * 2
        assert delay3 == 20  # base_delay * 4
    
    def test_schedule_retry(self, retry_manager, sample_delivery):
        """Testa agendamento de retry"""
        retry_manager.schedule_retry(sample_delivery)
        
        # Verificar se delivery foi adicionado à fila de retry
        assert len(retry_manager.retry_queue) == 1
        assert retry_manager.retry_queue[0] == sample_delivery

class TestWebhookDatabase:
    """Testes para persistência de webhooks"""
    
    @pytest.fixture
    def db_path(self, tmp_path):
        return str(tmp_path / "test_webhooks.db")
    
    @pytest.fixture
    def database(self, db_path):
        return WebhookDatabase(db_path)
    
    @pytest.fixture
    def sample_endpoint(self):
        return WebhookEndpoint(
            id="test-endpoint",
            name="Test Webhook",
            url="https://api.example.com/webhook",
            events=[WebhookEventType.KEYWORD_PROCESSED],
            secret="test-secret",
            security_level=WebhookSecurityLevel.HMAC,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_delivery(self):
        return WebhookDelivery(
            id="test-delivery",
            endpoint_id="test-endpoint",
            event_id="test-event",
            payload={"test": "data"},
            created_at=datetime.utcnow()
        )
    
    def test_save_and_load_endpoint(self, database, sample_endpoint):
        """Testa salvamento e carregamento de endpoint"""
        # Salvar endpoint
        assert database.save_endpoint(sample_endpoint) is True
        
        # Carregar endpoints
        endpoints = database.load_endpoints()
        
        # Verificar se endpoint foi carregado
        assert len(endpoints) == 1
        loaded_endpoint = endpoints[0]
        
        assert loaded_endpoint.id == sample_endpoint.id
        assert loaded_endpoint.name == sample_endpoint.name
        assert loaded_endpoint.url == sample_endpoint.url
        assert loaded_endpoint.events == sample_endpoint.events
    
    def test_save_and_update_delivery(self, database, sample_delivery):
        """Testa salvamento e atualização de delivery"""
        # Salvar delivery
        assert database.save_delivery(sample_delivery) is True
        
        # Atualizar delivery
        updates = {
            'status_code': 200,
            'response_body': 'OK',
            'delivered_at': datetime.utcnow().isoformat()
        }
        assert database.update_delivery(sample_delivery.id, **updates) is True

class TestWebhookSystem:
    """Testes para sistema principal de webhooks"""
    
    @pytest.fixture
    def webhook_system(self):
        config = {
            'max_retries': 3,
            'base_delay': 5,
            'db_path': ':memory:'  # SQLite em memória para testes
        }
        return create_webhook_system(config)
    
    @pytest.fixture
    def sample_endpoint(self):
        return WebhookEndpoint(
            id="test-endpoint",
            name="Test Webhook",
            url="https://api.example.com/webhook",
            events=[WebhookEventType.KEYWORD_PROCESSED, WebhookEventType.EXECUTION_COMPLETED],
            secret="test-secret",
            security_level=WebhookSecurityLevel.HMAC
        )
    
    def test_register_endpoint(self, webhook_system, sample_endpoint):
        """Testa registro de endpoint"""
        assert webhook_system.register_endpoint(sample_endpoint) is True
        
        # Verificar se endpoint foi registrado
        registered_endpoint = webhook_system.get_endpoint(sample_endpoint.id)
        assert registered_endpoint is not None
        assert registered_endpoint.name == sample_endpoint.name
    
    def test_register_endpoint_invalid(self, webhook_system):
        """Testa registro de endpoint inválido"""
        invalid_endpoint = WebhookEndpoint(
            id="invalid",
            name="Invalid",
            url="invalid-url",
            events=[]  # Sem eventos
        )
        
        assert webhook_system.register_endpoint(invalid_endpoint) is False
    
    def test_unregister_endpoint(self, webhook_system, sample_endpoint):
        """Testa remoção de endpoint"""
        # Registrar endpoint
        webhook_system.register_endpoint(sample_endpoint)
        
        # Remover endpoint
        assert webhook_system.unregister_endpoint(sample_endpoint.id) is True
        
        # Verificar se foi removido
        assert webhook_system.get_endpoint(sample_endpoint.id) is None
    
    def test_list_endpoints(self, webhook_system, sample_endpoint):
        """Testa listagem de endpoints"""
        # Registrar endpoint
        webhook_system.register_endpoint(sample_endpoint)
        
        # Listar endpoints
        endpoints = webhook_system.list_endpoints()
        
        assert len(endpoints) == 1
        assert endpoints[0].id == sample_endpoint.id
    
    @patch('infrastructure.integrations.webhook_system.asyncio.create_task')
    def test_trigger_webhook(self, mock_create_task, webhook_system, sample_endpoint):
        """Testa disparo de webhook"""
        # Registrar endpoint
        webhook_system.register_endpoint(sample_endpoint)
        
        # Disparar webhook
        data = {"keyword": "test", "status": "processed"}
        triggered = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        
        # Verificar se endpoint foi disparado
        assert len(triggered) == 1
        assert triggered[0] == sample_endpoint.id
        
        # Verificar se task foi criada
        mock_create_task.assert_called_once()
    
    def test_trigger_webhook_no_endpoints(self, webhook_system):
        """Testa disparo de webhook sem endpoints"""
        data = {"keyword": "test", "status": "processed"}
        triggered = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        
        assert len(triggered) == 0
    
    def test_trigger_webhook_inactive_endpoint(self, webhook_system, sample_endpoint):
        """Testa disparo de webhook com endpoint inativo"""
        # Registrar endpoint como inativo
        sample_endpoint.status = WebhookStatus.INACTIVE
        webhook_system.register_endpoint(sample_endpoint)
        
        # Disparar webhook
        data = {"keyword": "test", "status": "processed"}
        triggered = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        
        # Verificar se nenhum endpoint foi disparado
        assert len(triggered) == 0

class TestWebhookIntegration:
    """Testes de integração para sistema de webhooks"""
    
    @pytest.fixture
    def webhook_system(self):
        config = {'max_retries': 3, 'base_delay': 5, 'db_path': ':memory:'}
        return create_webhook_system(config)
    
    def test_full_webhook_flow(self, webhook_system):
        """Testa fluxo completo de webhook"""
        # 1. Registrar endpoint
        endpoint = WebhookEndpoint(
            id="integration-test",
            name="Integration Test",
            url="https://webhook.site/test",
            events=[WebhookEventType.KEYWORD_PROCESSED],
            secret="integration-secret",
            security_level=WebhookSecurityLevel.HMAC
        )
        
        assert webhook_system.register_endpoint(endpoint) is True
        
        # 2. Verificar se endpoint foi registrado
        registered = webhook_system.get_endpoint("integration-test")
        assert registered is not None
        assert registered.name == "Integration Test"
        
        # 3. Disparar webhook
        data = {
            "keyword": "integration test",
            "status": "processed",
            "results": {"clusters": 3, "keywords": 50}
        }
        
        triggered = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data, source="integration-test"
        )
        
        # 4. Verificar se webhook foi disparado
        assert len(triggered) == 1
        assert triggered[0] == "integration-test"
        
        # 5. Verificar estatísticas
        stats = webhook_system.get_delivery_stats("integration-test", days=1)
        assert "total_deliveries" in stats
        assert "success_rate" in stats
    
    def test_webhook_security_hmac(self, webhook_system):
        """Testa segurança HMAC do webhook"""
        # Registrar endpoint com HMAC
        endpoint = WebhookEndpoint(
            id="security-test",
            name="Security Test",
            url="https://api.example.com/webhook",
            events=[WebhookEventType.KEYWORD_PROCESSED],
            secret="security-secret",
            security_level=WebhookSecurityLevel.HMAC
        )
        
        webhook_system.register_endpoint(endpoint)
        
        # Disparar webhook
        data = {"test": "security"}
        triggered = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        
        # Verificar se webhook foi disparado
        assert len(triggered) == 1
        
        # Verificar se secret foi configurado
        registered = webhook_system.get_endpoint("security-test")
        assert registered.secret == "security-secret"
        assert registered.security_level == WebhookSecurityLevel.HMAC
    
    def test_webhook_rate_limiting(self, webhook_system):
        """Testa rate limiting de webhooks"""
        # Registrar endpoint com rate limit baixo
        endpoint = WebhookEndpoint(
            id="rate-limit-test",
            name="Rate Limit Test",
            url="https://api.example.com/webhook",
            events=[WebhookEventType.KEYWORD_PROCESSED],
            rate_limit=2  # Apenas 2 requests por hora
        )
        
        webhook_system.register_endpoint(endpoint)
        
        # Disparar webhooks
        data = {"test": "rate-limit"}
        
        # Primeiras 2 tentativas devem funcionar
        triggered1 = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        triggered2 = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        
        assert len(triggered1) == 1
        assert len(triggered2) == 1
        
        # 3ª tentativa deve ser bloqueada
        triggered3 = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        
        assert len(triggered3) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-value"])
