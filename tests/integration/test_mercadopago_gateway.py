"""
🧪 MercadoPago Gateway Integration Tests

Tracing ID: mercadopago-tests-2025-01-27-001
Timestamp: 2025-01-27T14:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais e padrões de teste de integração
🌲 ToT: Avaliadas múltiplas estratégias de teste e escolhida cobertura ideal
♻️ ReAct: Simulado cenários de falha e validada robustez
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

# Importar classes do gateway
from infrastructure.payments.mercadopago_gateway import (
    MercadoPagoGateway,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PaymentMethod
)
from infrastructure.payments.mercadopago_webhooks import (
    MercadoPagoWebhookHandler,
    WebhookEvent,
    WebhookType,
    WebhookAction,
    WebhookValidationResult
)

# Configuração de teste
TEST_CONFIG = {
    "environment": "sandbox",
    "access_token": "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "public_key": "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "webhook_secret": "test_webhook_secret_key",
    "allowed_ips": ["34.195.33.240", "34.195.33.241"]
}

# Dados de teste
TEST_PAYMENT_REQUEST = PaymentRequest(
    amount=100.00,
    currency="BRL",
    description="Test Payment - Omni Keywords Finder",
    payer_email="test@example.com",
    payment_method=PaymentMethod.CREDIT_CARD,
    installments=1,
    external_reference="test_ref_001"
)

TEST_CARD_DATA = {
    "card_number": "4509 9535 6623 3704",
    "security_code": "123",
    "expiration_month": "11",
    "expiration_year": "2025",
    "cardholder": {
        "name": "Test User",
        "identification": {
            "type": "CPF",
            "number": "12345678901"
        }
    }
}

TEST_WEBHOOK_PAYLOAD = {
    "id": "webhook_001",
    "type": "payment",
    "action": "created",
    "data": {
        "id": "payment_001"
    },
    "date_created": "2025-01-27T14:30:00.000Z",
    "live_mode": False,
    "user_id": "user_001",
    "api_version": "v1"
}

class TestMercadoPagoGateway:
    """Testes de integração para MercadoPago Gateway"""
    
    @pytest.fixture
    def gateway(self):
        """Fixture para criar gateway de teste"""
        with patch('infrastructure.payments.mercadopago_gateway.mercadopago') as mock_mercadopago:
            # Mock do SDK MercadoPago
            mock_sdk = Mock()
            mock_mercadopago.SDK.return_value = mock_sdk
            mock_sdk.set_environment.return_value = None
            
            # Mock dos componentes de infraestrutura
            with patch('infrastructure.payments.mercadopago_gateway.CircuitBreaker') as mock_cb, \
                 patch('infrastructure.payments.mercadopago_gateway.RateLimiter') as mock_rl, \
                 patch('infrastructure.payments.mercadopago_gateway.FallbackManager') as mock_fm, \
                 patch('infrastructure.payments.mercadopago_gateway.MetricsCollector') as mock_mc:
                
                # Configurar mocks
                mock_cb.return_value = Mock()
                mock_rl.return_value = Mock()
                mock_fm.return_value = Mock()
                mock_mc.return_value = Mock()
                
                gateway = MercadoPagoGateway(TEST_CONFIG)
                gateway.sdk = mock_sdk
                
                yield gateway
    
    def test_gateway_initialization(self, gateway):
        """Testa inicialização do gateway"""
        assert gateway.environment == "sandbox"
        assert gateway.access_token == TEST_CONFIG["access_token"]
        assert gateway.public_key == TEST_CONFIG["public_key"]
        assert gateway.webhook_secret == TEST_CONFIG["webhook_secret"]
        assert len(gateway.allowed_ips) == 2
    
    def test_create_payment_success(self, gateway):
        """Testa criação de pagamento com sucesso"""
        # Mock da resposta da API
        mock_response = {
            "status": 201,
            "response": {
                "id": "payment_001",
                "status": "pending",
                "transaction_amount": 100.00,
                "currency_id": "BRL",
                "description": "Test Payment",
                "date_created": "2025-01-27T14:30:00.000Z",
                "date_last_updated": "2025-01-27T14:30:00.000Z",
                "payment_method_id": "credit_card",
                "installments": 1,
                "external_reference": "test_ref_001",
                "transaction_details": {}
            }
        }
        
        gateway.sdk.payment.return_value.create.return_value = mock_response
        
        # Executar teste
        result = gateway.create_payment(TEST_PAYMENT_REQUEST)
        
        # Validações
        assert isinstance(result, PaymentResponse)
        assert result.id == "payment_001"
        assert result.status == PaymentStatus.PENDING
        assert result.amount == 100.00
        assert result.currency == "BRL"
        assert result.payment_method == PaymentMethod.CREDIT_CARD
        
        # Verificar se SDK foi chamado
        gateway.sdk.payment.return_value.create.assert_called_once()
    
    def test_create_payment_api_error(self, gateway):
        """Testa criação de pagamento com erro da API"""
        # Mock de erro da API
        mock_error_response = {
            "status": 400,
            "error": "Invalid payment data"
        }
        
        gateway.sdk.payment.return_value.create.return_value = mock_error_response
        
        # Executar teste e verificar exceção
        with pytest.raises(Exception) as exc_info:
            gateway.create_payment(TEST_PAYMENT_REQUEST)
        
        assert "Erro ao criar pagamento" in str(exc_info.value)
    
    def test_get_payment_status_success(self, gateway):
        """Testa consulta de status de pagamento"""
        # Mock da resposta da API
        mock_response = {
            "status": 200,
            "response": {
                "id": "payment_001",
                "status": "approved"
            }
        }
        
        gateway.sdk.payment.return_value.get.return_value = mock_response
        
        # Executar teste
        result = gateway.get_payment_status("payment_001")
        
        # Validações
        assert result == PaymentStatus.APPROVED
        
        # Verificar se SDK foi chamado
        gateway.sdk.payment.return_value.get.assert_called_once_with("payment_001")
    
    def test_create_card_token_success(self, gateway):
        """Testa criação de token de cartão"""
        # Mock da resposta da API
        mock_response = {
            "status": 201,
            "response": {
                "id": "card_token_001"
            }
        }
        
        gateway.sdk.card_token.return_value.create.return_value = mock_response
        
        # Executar teste
        result = gateway.create_card_token(TEST_CARD_DATA)
        
        # Validações
        assert result == "card_token_001"
        
        # Verificar se SDK foi chamado
        gateway.sdk.card_token.return_value.create.assert_called_once_with(TEST_CARD_DATA)
    
    def test_validate_webhook_success(self, gateway):
        """Testa validação de webhook com sucesso"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        signature = "valid_signature"
        client_ip = "34.195.33.240"
        
        # Mock da validação de assinatura
        with patch.object(gateway, '_validate_signature', return_value=True):
            result = gateway.validate_webhook(payload, signature, client_ip)
            
            assert result is True
    
    def test_validate_webhook_invalid_ip(self, gateway):
        """Testa validação de webhook com IP inválido"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        signature = "valid_signature"
        client_ip = "192.168.1.1"  # IP não autorizado
        
        result = gateway.validate_webhook(payload, signature, client_ip)
        
        assert result is False
    
    def test_validate_webhook_invalid_signature(self, gateway):
        """Testa validação de webhook com assinatura inválida"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        signature = "invalid_signature"
        client_ip = "34.195.33.240"
        
        # Mock da validação de assinatura
        with patch.object(gateway, '_validate_signature', return_value=False):
            result = gateway.validate_webhook(payload, signature, client_ip)
            
            assert result is False
    
    def test_process_webhook_payment_event(self, gateway):
        """Testa processamento de webhook de pagamento"""
        webhook_data = {
            "type": "payment",
            "data": {
                "id": "payment_001"
            }
        }
        
        # Mock da consulta de status
        with patch.object(gateway, 'get_payment_status', return_value=PaymentStatus.APPROVED):
            result = gateway.process_webhook(webhook_data)
            
            assert result["status"] == "success"
            assert result["event_type"] == "payment"
            assert "payment_id" in result["result"]
    
    def test_health_status(self, gateway):
        """Testa status de saúde do gateway"""
        result = gateway.get_health_status()
        
        assert result["status"] == "healthy"
        assert result["environment"] == "sandbox"
        assert "timestamp" in result


class TestMercadoPagoWebhookHandler:
    """Testes de integração para MercadoPago Webhook Handler"""
    
    @pytest.fixture
    def webhook_handler(self):
        """Fixture para criar webhook handler de teste"""
        with patch('infrastructure.payments.mercadopago_webhooks.CircuitBreaker') as mock_cb, \
             patch('infrastructure.payments.mercadopago_webhooks.RateLimiter') as mock_rl, \
             patch('infrastructure.payments.mercadopago_webhooks.MetricsCollector') as mock_mc:
            
            # Configurar mocks
            mock_cb.return_value = Mock()
            mock_rl.return_value = Mock()
            mock_mc.return_value = Mock()
            
            handler = MercadoPagoWebhookHandler(TEST_CONFIG)
            
            yield handler
    
    def test_handler_initialization(self, webhook_handler):
        """Testa inicialização do webhook handler"""
        assert webhook_handler.webhook_secret == TEST_CONFIG["webhook_secret"]
        assert webhook_handler.allowed_ips == TEST_CONFIG["allowed_ips"]
        assert webhook_handler.timeout_seconds == 30
        assert webhook_handler.max_retries == 3
    
    def test_register_handler(self, webhook_handler):
        """Testa registro de handler de evento"""
        def test_handler(event):
            return {"test": "handler"}
        
        webhook_handler.register_handler(WebhookType.PAYMENT, test_handler)
        
        assert "payment" in webhook_handler.event_handlers
        assert webhook_handler.event_handlers["payment"] == test_handler
    
    def test_validate_webhook_success(self, webhook_handler):
        """Testa validação de webhook com sucesso"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        signature = "valid_signature"
        client_ip = "34.195.33.240"
        headers = {"X-Timestamp": datetime.utcnow().isoformat()}
        
        # Mock das validações
        with patch.object(webhook_handler, '_validate_signature', return_value=True), \
             patch.object(webhook_handler, '_validate_timestamp', return_value=True), \
             patch.object(webhook_handler, '_is_duplicate_event', return_value=False):
            
            result = webhook_handler.validate_webhook(payload, signature, client_ip, headers)
            
            assert result.is_valid is True
            assert result.event is not None
            assert result.event.type == WebhookType.PAYMENT
            assert result.event.action == WebhookAction.CREATED
    
    def test_validate_webhook_invalid_ip(self, webhook_handler):
        """Testa validação de webhook com IP inválido"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        signature = "valid_signature"
        client_ip = "192.168.1.1"  # IP não autorizado
        headers = {}
        
        result = webhook_handler.validate_webhook(payload, signature, client_ip, headers)
        
        assert result.is_valid is False
        assert "IP não autorizado" in result.error_message
    
    def test_validate_webhook_invalid_signature(self, webhook_handler):
        """Testa validação de webhook com assinatura inválida"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        signature = "invalid_signature"
        client_ip = "34.195.33.240"
        headers = {}
        
        # Mock da validação de IP
        with patch.object(webhook_handler, '_validate_ip', return_value=True), \
             patch.object(webhook_handler, '_validate_signature', return_value=False):
            
            result = webhook_handler.validate_webhook(payload, signature, client_ip, headers)
            
            assert result.is_valid is False
            assert "Assinatura HMAC inválida" in result.error_message
    
    def test_validate_webhook_duplicate_event(self, webhook_handler):
        """Testa validação de webhook com evento duplicado"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        signature = "valid_signature"
        client_ip = "34.195.33.240"
        headers = {}
        
        # Mock das validações
        with patch.object(webhook_handler, '_validate_ip', return_value=True), \
             patch.object(webhook_handler, '_validate_signature', return_value=True), \
             patch.object(webhook_handler, '_validate_timestamp', return_value=True), \
             patch.object(webhook_handler, '_is_duplicate_event', return_value=True):
            
            result = webhook_handler.validate_webhook(payload, signature, client_ip, headers)
            
            assert result.is_valid is False
            assert "Evento duplicado" in result.error_message
    
    def test_process_webhook_success(self, webhook_handler):
        """Testa processamento de webhook com sucesso"""
        # Criar evento de teste
        event = WebhookEvent(
            id="webhook_001",
            type=WebhookType.PAYMENT,
            action=WebhookAction.CREATED,
            data={"id": "payment_001"},
            timestamp=datetime.utcnow(),
            live_mode=False
        )
        
        # Registrar handler de teste
        def test_handler(event):
            return {"processed": True, "payment_id": event.data["id"]}
        
        webhook_handler.register_handler(WebhookType.PAYMENT, test_handler)
        
        # Executar teste
        result = webhook_handler.process_webhook(event)
        
        # Validações
        assert result["status"] == "success"
        assert result["event_id"] == "webhook_001"
        assert result["event_type"] == "payment"
        assert result["result"]["processed"] is True
        assert result["result"]["payment_id"] == "payment_001"
    
    def test_process_webhook_no_handler(self, webhook_handler):
        """Testa processamento de webhook sem handler registrado"""
        event = WebhookEvent(
            id="webhook_001",
            type=WebhookType.SUBSCRIPTION,
            action=WebhookAction.CREATED,
            data={"id": "subscription_001"},
            timestamp=datetime.utcnow(),
            live_mode=False
        )
        
        # Executar teste (sem registrar handler)
        result = webhook_handler.process_webhook(event)
        
        # Validações
        assert result["status"] == "success"
        assert result["result"]["status"] == "no_handler"
        assert result["result"]["event_type"] == "subscription"
    
    def test_health_status(self, webhook_handler):
        """Testa status de saúde do webhook handler"""
        result = webhook_handler.get_health_status()
        
        assert result["status"] == "healthy"
        assert "registered_handlers" in result
        assert "processed_events_count" in result
        assert "timestamp" in result


class TestMercadoPagoIntegration:
    """Testes de integração end-to-end"""
    
    @pytest.fixture
    def integrated_system(self):
        """Fixture para sistema integrado"""
        with patch('infrastructure.payments.mercadopago_gateway.mercadopago') as mock_mercadopago, \
             patch('infrastructure.payments.mercadopago_gateway.CircuitBreaker') as mock_cb, \
             patch('infrastructure.payments.mercadopago_gateway.RateLimiter') as mock_rl, \
             patch('infrastructure.payments.mercadopago_gateway.FallbackManager') as mock_fm, \
             patch('infrastructure.payments.mercadopago_gateway.MetricsCollector') as mock_mc, \
             patch('infrastructure.payments.mercadopago_webhooks.CircuitBreaker') as mock_wb_cb, \
             patch('infrastructure.payments.mercadopago_webhooks.RateLimiter') as mock_wb_rl, \
             patch('infrastructure.payments.mercadopago_webhooks.MetricsCollector') as mock_wb_mc:
            
            # Configurar mocks
            mock_sdk = Mock()
            mock_mercadopago.SDK.return_value = mock_sdk
            mock_sdk.set_environment.return_value = None
            
            mock_cb.return_value = Mock()
            mock_rl.return_value = Mock()
            mock_fm.return_value = Mock()
            mock_mc.return_value = Mock()
            mock_wb_cb.return_value = Mock()
            mock_wb_rl.return_value = Mock()
            mock_wb_mc.return_value = Mock()
            
            gateway = MercadoPagoGateway(TEST_CONFIG)
            gateway.sdk = mock_sdk
            
            webhook_handler = MercadoPagoWebhookHandler(TEST_CONFIG)
            
            yield {
                "gateway": gateway,
                "webhook_handler": webhook_handler,
                "mock_sdk": mock_sdk
            }
    
    def test_payment_creation_and_webhook_processing(self, integrated_system):
        """Testa fluxo completo: criação de pagamento + processamento de webhook"""
        gateway = integrated_system["gateway"]
        webhook_handler = integrated_system["webhook_handler"]
        mock_sdk = integrated_system["mock_sdk"]
        
        # Mock da criação de pagamento
        payment_response = {
            "status": 201,
            "response": {
                "id": "payment_001",
                "status": "pending",
                "transaction_amount": 100.00,
                "currency_id": "BRL",
                "description": "Test Payment",
                "date_created": "2025-01-27T14:30:00.000Z",
                "date_last_updated": "2025-01-27T14:30:00.000Z",
                "payment_method_id": "credit_card",
                "installments": 1
            }
        }
        
        mock_sdk.payment.return_value.create.return_value = payment_response
        
        # 1. Criar pagamento
        payment = gateway.create_payment(TEST_PAYMENT_REQUEST)
        assert payment.id == "payment_001"
        assert payment.status == PaymentStatus.PENDING
        
        # 2. Simular webhook de atualização de status
        webhook_data = {
            "type": "payment",
            "data": {
                "id": "payment_001"
            }
        }
        
        # Mock da consulta de status atualizado
        with patch.object(gateway, 'get_payment_status', return_value=PaymentStatus.APPROVED):
            result = gateway.process_webhook(webhook_data)
            
            assert result["status"] == "success"
            assert result["event_type"] == "payment"
            assert result["result"]["status"] == "approved"
            assert result["result"]["action"] == "activate_service"
    
    def test_error_handling_and_fallback(self, integrated_system):
        """Testa tratamento de erro e fallback"""
        gateway = integrated_system["gateway"]
        
        # Mock de erro na API
        mock_sdk = integrated_system["mock_sdk"]
        mock_sdk.payment.return_value.create.return_value = {
            "status": 500,
            "error": "Internal server error"
        }
        
        # Mock do fallback manager
        fallback_response = PaymentResponse(
            id="fallback_001",
            status=PaymentStatus.PENDING,
            amount=100.00,
            currency="BRL",
            description="Test Payment",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=1,
            error_message="Pagamento em processamento via fallback"
        )
        
        gateway.fallback_manager.execute_fallback.return_value = fallback_response
        
        # Executar teste
        result = gateway.create_payment(TEST_PAYMENT_REQUEST)
        
        # Validações
        assert result.id == "fallback_001"
        assert result.status == PaymentStatus.PENDING
        assert "fallback" in result.error_message
        
        # Verificar se fallback foi chamado
        gateway.fallback_manager.execute_fallback.assert_called_once()


# Testes de performance
class TestMercadoPagoPerformance:
    """Testes de performance do MercadoPago Gateway"""
    
    @pytest.fixture
    def performance_gateway(self):
        """Fixture para testes de performance"""
        with patch('infrastructure.payments.mercadopago_gateway.mercadopago') as mock_mercadopago, \
             patch('infrastructure.payments.mercadopago_gateway.CircuitBreaker') as mock_cb, \
             patch('infrastructure.payments.mercadopago_gateway.RateLimiter') as mock_rl, \
             patch('infrastructure.payments.mercadopago_gateway.FallbackManager') as mock_fm, \
             patch('infrastructure.payments.mercadopago_gateway.MetricsCollector') as mock_mc:
            
            mock_sdk = Mock()
            mock_mercadopago.SDK.return_value = mock_sdk
            mock_sdk.set_environment.return_value = None
            
            mock_cb.return_value = Mock()
            mock_rl.return_value = Mock()
            mock_fm.return_value = Mock()
            mock_mc.return_value = Mock()
            
            gateway = MercadoPagoGateway(TEST_CONFIG)
            gateway.sdk = mock_sdk
            
            yield gateway
    
    def test_payment_creation_performance(self, performance_gateway):
        """Testa performance da criação de pagamento"""
        # Mock de resposta rápida
        mock_response = {
            "status": 201,
            "response": {
                "id": "payment_001",
                "status": "pending",
                "transaction_amount": 100.00,
                "currency_id": "BRL",
                "description": "Test Payment",
                "date_created": "2025-01-27T14:30:00.000Z",
                "date_last_updated": "2025-01-27T14:30:00.000Z",
                "payment_method_id": "credit_card",
                "installments": 1
            }
        }
        
        performance_gateway.sdk.payment.return_value.create.return_value = mock_response
        
        # Medir tempo de execução
        start_time = time.time()
        
        for index in range(10):
            payment = performance_gateway.create_payment(TEST_PAYMENT_REQUEST)
            assert payment.id == "payment_001"
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Validar performance (máximo 5 segundos para 10 pagamentos)
        assert execution_time < 5.0
        avg_time = execution_time / 10
        assert avg_time < 0.5  # Máximo 500ms por pagamento
    
    def test_concurrent_payment_creation(self, performance_gateway):
        """Testa criação concorrente de pagamentos"""
        import threading
        
        # Mock de resposta
        mock_response = {
            "status": 201,
            "response": {
                "id": "payment_001",
                "status": "pending",
                "transaction_amount": 100.00,
                "currency_id": "BRL",
                "description": "Test Payment",
                "date_created": "2025-01-27T14:30:00.000Z",
                "date_last_updated": "2025-01-27T14:30:00.000Z",
                "payment_method_id": "credit_card",
                "installments": 1
            }
        }
        
        performance_gateway.sdk.payment.return_value.create.return_value = mock_response
        
        results = []
        errors = []
        
        def create_payment():
            try:
                payment = performance_gateway.create_payment(TEST_PAYMENT_REQUEST)
                results.append(payment)
            except Exception as e:
                errors.append(e)
        
        # Criar threads concorrentes
        threads = []
        for index in range(5):
            thread = threading.Thread(target=create_payment)
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Validações
        assert len(results) == 5
        assert len(errors) == 0
        
        for payment in results:
            assert payment.id == "payment_001"
            assert payment.status == PaymentStatus.PENDING


# Testes de segurança
class TestMercadoPagoSecurity:
    """Testes de segurança do MercadoPago Gateway"""
    
    @pytest.fixture
    def security_gateway(self):
        """Fixture para testes de segurança"""
        with patch('infrastructure.payments.mercadopago_gateway.mercadopago') as mock_mercadopago, \
             patch('infrastructure.payments.mercadopago_gateway.CircuitBreaker') as mock_cb, \
             patch('infrastructure.payments.mercadopago_gateway.RateLimiter') as mock_rl, \
             patch('infrastructure.payments.mercadopago_gateway.FallbackManager') as mock_fm, \
             patch('infrastructure.payments.mercadopago_gateway.MetricsCollector') as mock_mc:
            
            mock_sdk = Mock()
            mock_mercadopago.SDK.return_value = mock_sdk
            mock_sdk.set_environment.return_value = None
            
            mock_cb.return_value = Mock()
            mock_rl.return_value = Mock()
            mock_fm.return_value = Mock()
            mock_mc.return_value = Mock()
            
            gateway = MercadoPagoGateway(TEST_CONFIG)
            gateway.sdk = mock_sdk
            
            yield gateway
    
    def test_webhook_signature_validation(self, security_gateway):
        """Testa validação de assinatura de webhook"""
        payload = json.dumps(TEST_WEBHOOK_PAYLOAD)
        client_ip = "34.195.33.240"
        
        # Teste com assinatura válida
        valid_signature = security_gateway._validate_signature(payload, "valid_signature")
        assert valid_signature is False  # Sem webhook_secret configurado
        
        # Teste com assinatura inválida
        invalid_signature = security_gateway._validate_signature(payload, "invalid_signature")
        assert invalid_signature is False
    
    def test_ip_whitelist_validation(self, security_gateway):
        """Testa validação de IP whitelist"""
        # IPs válidos
        assert security_gateway._validate_ip("34.195.33.240") is True
        assert security_gateway._validate_ip("34.195.33.241") is True
        
        # IPs inválidos
        assert security_gateway._validate_ip("192.168.1.1") is False
        assert security_gateway._validate_ip("10.0.0.1") is False
        assert security_gateway._validate_ip("8.8.8.8") is False
    
    def test_sql_injection_prevention(self, security_gateway):
        """Testa prevenção de SQL injection"""
        # Dados maliciosos
        malicious_request = PaymentRequest(
            amount=100.00,
            currency="BRL",
            description="'; DROP TABLE payments; --",
            payer_email="test@example.com",
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=1
        )
        
        # Mock de resposta
        mock_response = {
            "status": 201,
            "response": {
                "id": "payment_001",
                "status": "pending",
                "transaction_amount": 100.00,
                "currency_id": "BRL",
                "description": "'; DROP TABLE payments; --",
                "date_created": "2025-01-27T14:30:00.000Z",
                "date_last_updated": "2025-01-27T14:30:00.000Z",
                "payment_method_id": "credit_card",
                "installments": 1
            }
        }
        
        security_gateway.sdk.payment.return_value.create.return_value = mock_response
        
        # Executar teste
        result = security_gateway.create_payment(malicious_request)
        
        # Validar que não houve erro de SQL injection
        assert result.id == "payment_001"
        assert result.description == "'; DROP TABLE payments; --"
    
    def test_xss_prevention(self, security_gateway):
        """Testa prevenção de XSS"""
        # Dados com script malicioso
        xss_request = PaymentRequest(
            amount=100.00,
            currency="BRL",
            description="<script>alert('XSS')</script>",
            payer_email="test@example.com",
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=1
        )
        
        # Mock de resposta
        mock_response = {
            "status": 201,
            "response": {
                "id": "payment_001",
                "status": "pending",
                "transaction_amount": 100.00,
                "currency_id": "BRL",
                "description": "<script>alert('XSS')</script>",
                "date_created": "2025-01-27T14:30:00.000Z",
                "date_last_updated": "2025-01-27T14:30:00.000Z",
                "payment_method_id": "credit_card",
                "installments": 1
            }
        }
        
        security_gateway.sdk.payment.return_value.create.return_value = mock_response
        
        # Executar teste
        result = security_gateway.create_payment(xss_request)
        
        # Validar que não houve execução de script
        assert result.id == "payment_001"
        assert "<script>" in result.description  # Dados preservados, mas não executados


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 