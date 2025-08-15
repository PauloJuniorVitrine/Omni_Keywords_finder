"""
Testes Unitários para Payment V1 Service
Serviço de Pagamentos V1 - Omni Keywords Finder

Prompt: Implementação de testes unitários para serviço de pagamentos V1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any

from backend.app.services.payment_v1_service import (
    PaymentV1Service,
    PaymentGatewayConfig,
    PaymentResult
)
from backend.app.schemas.payment_v1_schemas import (
    PaymentRequest,
    PaymentRefundRequest,
    PaymentListRequest,
    PaymentMethod,
    PaymentStatus,
    Currency
)


class TestPaymentGatewayConfig:
    """Testes para PaymentGatewayConfig"""
    
    def test_payment_gateway_config_creation(self):
        """Testa criação de configuração do gateway"""
        config = PaymentGatewayConfig(
            provider="stripe",
            api_key="test_api_key",
            secret_key="test_secret_key",
            webhook_secret="test_webhook_secret",
            environment="test",
            timeout=30,
            max_retries=3
        )
        
        assert config.provider == "stripe"
        assert config.api_key == "test_api_key"
        assert config.secret_key == "test_secret_key"
        assert config.webhook_secret == "test_webhook_secret"
        assert config.environment == "test"
        assert config.timeout == 30
        assert config.max_retries == 3


class TestPaymentResult:
    """Testes para PaymentResult"""
    
    def test_payment_result_success(self):
        """Testa criação de resultado de pagamento com sucesso"""
        result = PaymentResult(
            success=True,
            payment_id="test_payment_123",
            status=PaymentStatus.PROCESSING.value,
            message="Pagamento processado com sucesso",
            data={"payment_intent_id": "pi_123", "confirmation_url": "/confirm"}
        )
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.PROCESSING.value
        assert result.message == "Pagamento processado com sucesso"
        assert result.data["payment_intent_id"] == "pi_123"
        assert result.error_code is None
        assert result.error_details is None
    
    def test_payment_result_failure(self):
        """Testa criação de resultado de pagamento com falha"""
        result = PaymentResult(
            success=False,
            payment_id="test_payment_123",
            status=PaymentStatus.FAILED.value,
            message="Pagamento falhou",
            error_code="CARD_DECLINED",
            error_details="Cartão recusado pelo banco"
        )
        
        assert result.success is False
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.FAILED.value
        assert result.message == "Pagamento falhou"
        assert result.error_code == "CARD_DECLINED"
        assert result.error_details == "Cartão recusado pelo banco"


class TestPaymentV1Service:
    """Testes para PaymentV1Service"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def payment_service(self, temp_db_path):
        """Instância do PaymentV1Service para testes"""
        with patch.dict(os.environ, {
            'PAYMENT_PROVIDER': 'stripe',
            'PAYMENT_API_KEY': 'test_api_key',
            'PAYMENT_SECRET_KEY': 'test_secret_key',
            'PAYMENT_WEBHOOK_SECRET': 'test_webhook_secret',
            'PAYMENT_ENVIRONMENT': 'test'
        }):
            service = PaymentV1Service(db_path=temp_db_path)
            yield service
            service.close()
    
    @pytest.fixture
    def valid_payment_request(self):
        """Requisição de pagamento válida para testes"""
        return PaymentRequest(
            payment_id="test_payment_123",
            amount=100.00,
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={
                "name": "João Silva",
                "email": "joao@example.com",
                "id": "customer_123"
            },
            payment_data={
                "card_number": "4242424242424242",
                "exp_month": "12",
                "exp_year": "2025",
                "cvc": "123",
                "token": "tok_visa"
            },
            reference_id="order_123",
            metadata={"order_id": "order_123"},
            idempotency_key="idemp_123"
        )
    
    def test_payment_service_initialization(self, temp_db_path):
        """Testa inicialização do PaymentV1Service"""
        with patch.dict(os.environ, {
            'PAYMENT_PROVIDER': 'stripe',
            'PAYMENT_API_KEY': 'test_api_key',
            'PAYMENT_SECRET_KEY': 'test_secret_key',
            'PAYMENT_WEBHOOK_SECRET': 'test_webhook_secret',
            'PAYMENT_ENVIRONMENT': 'test'
        }):
            service = PaymentV1Service(db_path=temp_db_path)
            
            assert service.db_path == temp_db_path
            assert service.gateway_config.provider == "stripe"
            assert service.gateway_config.api_key == "test_api_key"
            assert service.gateway_config.secret_key == "test_secret_key"
            assert service.gateway_config.webhook_secret == "test_webhook_secret"
            assert service.gateway_config.environment == "test"
            assert service.gateway_config.timeout == 30
            assert service.gateway_config.max_retries == 3
            
            service.close()
    
    def test_validate_payment_request_valid(self, payment_service, valid_payment_request):
        """Testa validação de requisição de pagamento válida"""
        is_valid = payment_service._validate_payment_request(valid_payment_request)
        assert is_valid is True
    
    def test_validate_payment_request_invalid_amount(self, payment_service):
        """Testa validação de requisição com valor inválido"""
        invalid_request = PaymentRequest(
            payment_id="test_payment_123",
            amount=0,  # Valor inválido
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={"name": "João", "email": "joao@example.com"},
            payment_data={"card_number": "4242424242424242", "exp_month": "12", "exp_year": "2025", "cvc": "123"}
        )
        
        is_valid = payment_service._validate_payment_request(invalid_request)
        assert is_valid is False
    
    def test_validate_payment_request_missing_customer_data(self, payment_service):
        """Testa validação de requisição sem dados do cliente"""
        invalid_request = PaymentRequest(
            payment_id="test_payment_123",
            amount=100.00,
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={},  # Dados do cliente vazios
            payment_data={"card_number": "4242424242424242", "exp_month": "12", "exp_year": "2025", "cvc": "123"}
        )
        
        is_valid = payment_service._validate_payment_request(invalid_request)
        assert is_valid is False
    
    def test_validate_payment_request_missing_card_data(self, payment_service):
        """Testa validação de requisição sem dados do cartão"""
        invalid_request = PaymentRequest(
            payment_id="test_payment_123",
            amount=100.00,
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={"name": "João", "email": "joao@example.com"},
            payment_data={}  # Dados do cartão vazios
        )
        
        is_valid = payment_service._validate_payment_request(invalid_request)
        assert is_valid is False
    
    @patch('requests.post')
    def test_process_with_stripe_success(self, mock_post, payment_service, valid_payment_request):
        """Testa processamento com Stripe com sucesso"""
        # Mock da resposta do Stripe
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "pi_test_123",
            "client_secret": "pi_test_secret_123",
            "next_action": {
                "redirect_to_url": {
                    "url": "https://stripe.com/confirm"
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = payment_service._process_with_stripe(valid_payment_request)
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.PROCESSING.value
        assert result.data["payment_intent_id"] == "pi_test_123"
        assert result.data["client_secret"] == "pi_test_secret_123"
        assert result.data["confirmation_url"] == "https://stripe.com/confirm"
    
    @patch('requests.post')
    def test_process_with_stripe_failure(self, mock_post, payment_service, valid_payment_request):
        """Testa processamento com Stripe com falha"""
        # Mock da resposta de erro do Stripe
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "code": "card_declined",
                "message": "Your card was declined."
            }
        }
        mock_post.return_value = mock_response
        
        result = payment_service._process_with_stripe(valid_payment_request)
        
        assert result.success is False
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.FAILED.value
        assert result.error_code == "card_declined"
        assert "Your card was declined" in result.message
    
    def test_process_with_paypal_success(self, payment_service, valid_payment_request):
        """Testa processamento com PayPal com sucesso"""
        result = payment_service._process_with_paypal(valid_payment_request)
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.PROCESSING.value
        assert result.data["payment_intent_id"] == f"paypal_{valid_payment_request.payment_id}"
        assert "paypal/confirm" in result.data["confirmation_url"]
    
    def test_process_with_generic_gateway_success(self, payment_service, valid_payment_request):
        """Testa processamento com gateway genérico com sucesso"""
        result = payment_service._process_with_generic_gateway(valid_payment_request)
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.PROCESSING.value
        assert result.data["payment_intent_id"] == f"generic_{valid_payment_request.payment_id}"
        assert "confirm" in result.data["confirmation_url"]
    
    def test_process_with_fallback_gateway_success(self, payment_service, valid_payment_request):
        """Testa processamento com gateway de fallback com sucesso"""
        result = payment_service._process_with_fallback_gateway(valid_payment_request)
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.PROCESSING.value
        assert result.data["payment_intent_id"] == f"pi_fallback_{valid_payment_request.payment_id}"
        assert "fallback" in result.message
    
    @patch('requests.post')
    def test_process_payment_success(self, mock_post, payment_service, valid_payment_request):
        """Testa processamento de pagamento com sucesso"""
        # Mock da resposta do Stripe
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "pi_test_123",
            "client_secret": "pi_test_secret_123"
        }
        mock_post.return_value = mock_response
        
        result = payment_service.process_payment(valid_payment_request)
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.PROCESSING.value
    
    def test_process_payment_invalid_request(self, payment_service):
        """Testa processamento de pagamento com requisição inválida"""
        invalid_request = PaymentRequest(
            payment_id="test_payment_123",
            amount=0,  # Valor inválido
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={"name": "João", "email": "joao@example.com"},
            payment_data={"card_number": "4242424242424242", "exp_month": "12", "exp_year": "2025", "cvc": "123"}
        )
        
        result = payment_service.process_payment(invalid_request)
        
        assert result.success is False
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.FAILED.value
        assert result.error_code == "INVALID_REQUEST"
    
    def test_get_payment_by_idempotency_key_not_found(self, payment_service):
        """Testa busca de pagamento por chave de idempotência não encontrado"""
        result = payment_service._get_payment_by_idempotency_key("nonexistent_key")
        assert result is None
    
    def test_get_payment_not_found(self, payment_service):
        """Testa busca de pagamento não encontrado"""
        result = payment_service.get_payment("nonexistent_payment")
        assert result is None
    
    def test_list_payments_empty(self, payment_service):
        """Testa listagem de pagamentos vazia"""
        filters = PaymentListRequest()
        payments = payment_service.list_payments(filters)
        assert payments == []
    
    def test_process_refund_payment_not_found(self, payment_service):
        """Testa processamento de reembolso com pagamento não encontrado"""
        refund_request = PaymentRefundRequest(
            refund_id="refund_123",
            payment_id="nonexistent_payment",
            amount=50.00,
            reason="Customer request"
        )
        
        result = payment_service.process_refund(refund_request)
        
        assert result.success is False
        assert result.payment_id == "nonexistent_payment"
        assert result.error_code == "PAYMENT_NOT_FOUND"
    
    def test_process_refund_not_allowed(self, payment_service, valid_payment_request):
        """Testa processamento de reembolso não permitido"""
        # Primeiro, salvar um pagamento com status que não permite reembolso
        result = PaymentResult(
            success=True,
            payment_id=valid_payment_request.payment_id,
            status=PaymentStatus.FAILED.value,
            message="Pagamento processado"
        )
        payment_service._save_payment(valid_payment_request, result)
        
        # Tentar reembolso
        refund_request = PaymentRefundRequest(
            refund_id="refund_123",
            payment_id=valid_payment_request.payment_id,
            amount=50.00,
            reason="Customer request"
        )
        
        result = payment_service.process_refund(refund_request)
        
        assert result.success is False
        assert result.error_code == "REFUND_NOT_ALLOWED"
    
    def test_verify_webhook_signature_stripe_valid(self, payment_service):
        """Testa verificação de assinatura do webhook Stripe válida"""
        payload = b'{"test": "data"}'
        signature = "whsec_test_signature"
        
        # Mock da verificação HMAC
        with patch('hmac.new') as mock_hmac:
            mock_hmac.return_value.hexdigest.return_value = "test_signature"
            with patch('hmac.compare_digest', return_value=True):
                is_valid = payment_service._verify_webhook_signature(payload, signature)
                assert is_valid is True
    
    def test_verify_webhook_signature_stripe_invalid(self, payment_service):
        """Testa verificação de assinatura do webhook Stripe inválida"""
        payload = b'{"test": "data"}'
        signature = "whsec_invalid_signature"
        
        # Mock da verificação HMAC
        with patch('hmac.new') as mock_hmac:
            mock_hmac.return_value.hexdigest.return_value = "test_signature"
            with patch('hmac.compare_digest', return_value=False):
                is_valid = payment_service._verify_webhook_signature(payload, signature)
                assert is_valid is False
    
    def test_validate_webhook_data_valid(self, payment_service):
        """Testa validação de dados do webhook válidos"""
        webhook_data = {
            "id": "evt_test_123",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "metadata": {
                        "payment_id": "test_payment_123"
                    }
                }
            }
        }
        
        is_valid = payment_service._validate_webhook_data(webhook_data)
        assert is_valid is True
    
    def test_validate_webhook_data_invalid(self, payment_service):
        """Testa validação de dados do webhook inválidos"""
        webhook_data = {
            "id": "evt_test_123"
            # Faltando campos obrigatórios
        }
        
        is_valid = payment_service._validate_webhook_data(webhook_data)
        assert is_valid is False
    
    def test_process_webhook_event_success(self, payment_service):
        """Testa processamento de evento do webhook com sucesso"""
        webhook_data = {
            "id": "evt_test_123",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "metadata": {
                        "payment_id": "test_payment_123"
                    }
                }
            }
        }
        
        result = payment_service._process_webhook_event(webhook_data)
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        assert result.status == PaymentStatus.COMPLETED.value
        assert result.data["event_id"] == "evt_test_123"
        assert result.data["event_type"] == "payment_intent.succeeded"
    
    def test_process_webhook_event_missing_payment_id(self, payment_service):
        """Testa processamento de evento do webhook sem payment_id"""
        webhook_data = {
            "id": "evt_test_123",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "metadata": {}
                }
            }
        }
        
        result = payment_service._process_webhook_event(webhook_data)
        
        assert result.success is False
        assert result.error_code == "MISSING_PAYMENT_ID"
    
    def test_process_webhook_success(self, payment_service):
        """Testa processamento de webhook com sucesso"""
        payload = json.dumps({
            "id": "evt_test_123",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "metadata": {
                        "payment_id": "test_payment_123"
                    }
                }
            }
        }).encode('utf-8')
        
        # Mock da verificação de assinatura
        with patch.object(payment_service, '_verify_webhook_signature', return_value=True):
            result = payment_service.process_webhook(payload, "test_signature")
            
            assert result.success is True
            assert result.payment_id == "test_payment_123"
            assert result.status == PaymentStatus.COMPLETED.value
    
    def test_process_webhook_invalid_signature(self, payment_service):
        """Testa processamento de webhook com assinatura inválida"""
        payload = b'{"test": "data"}'
        
        # Mock da verificação de assinatura
        with patch.object(payment_service, '_verify_webhook_signature', return_value=False):
            result = payment_service.process_webhook(payload, "invalid_signature")
            
            assert result.success is False
            assert result.error_code == "INVALID_SIGNATURE"
    
    def test_process_webhook_invalid_data(self, payment_service):
        """Testa processamento de webhook com dados inválidos"""
        payload = b'{"invalid": "data"}'
        
        # Mock da verificação de assinatura
        with patch.object(payment_service, '_verify_webhook_signature', return_value=True):
            result = payment_service.process_webhook(payload, "test_signature")
            
            assert result.success is False
            assert result.error_code == "INVALID_WEBHOOK_DATA"


class TestPaymentV1ServiceIntegration:
    """Testes de integração para PaymentV1Service"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def payment_service(self, temp_db_path):
        """Instância do PaymentV1Service para testes"""
        with patch.dict(os.environ, {
            'PAYMENT_PROVIDER': 'stripe',
            'PAYMENT_API_KEY': 'test_api_key',
            'PAYMENT_SECRET_KEY': 'test_secret_key',
            'PAYMENT_WEBHOOK_SECRET': 'test_webhook_secret',
            'PAYMENT_ENVIRONMENT': 'test'
        }):
            service = PaymentV1Service(db_path=temp_db_path)
            yield service
            service.close()
    
    @pytest.fixture
    def valid_payment_request(self):
        """Requisição de pagamento válida para testes"""
        return PaymentRequest(
            payment_id="test_payment_123",
            amount=100.00,
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={
                "name": "João Silva",
                "email": "joao@example.com",
                "id": "customer_123"
            },
            payment_data={
                "card_number": "4242424242424242",
                "exp_month": "12",
                "exp_year": "2025",
                "cvc": "123",
                "token": "tok_visa"
            },
            reference_id="order_123",
            metadata={"order_id": "order_123"},
            idempotency_key="idemp_123"
        )
    
    @patch('requests.post')
    def test_full_payment_flow(self, mock_post, payment_service, valid_payment_request):
        """Testa fluxo completo de pagamento"""
        # Mock da resposta do Stripe
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "pi_test_123",
            "client_secret": "pi_test_secret_123"
        }
        mock_post.return_value = mock_response
        
        # Processar pagamento
        result = payment_service.process_payment(valid_payment_request)
        
        assert result.success is True
        assert result.payment_id == "test_payment_123"
        
        # Verificar se foi salvo no banco
        saved_payment = payment_service.get_payment("test_payment_123")
        assert saved_payment is not None
        assert saved_payment["payment_id"] == "test_payment_123"
        assert saved_payment["amount"] == 100.00
        assert saved_payment["currency"] == Currency.BRL.value
        assert saved_payment["status"] == PaymentStatus.PROCESSING.value
    
    def test_payment_with_idempotency(self, payment_service, valid_payment_request):
        """Testa pagamento com idempotência"""
        # Primeiro pagamento
        result1 = payment_service.process_payment(valid_payment_request)
        assert result1.success is True
        
        # Segundo pagamento com mesma chave de idempotência
        result2 = payment_service.process_payment(valid_payment_request)
        assert result2.success is True
        assert result2.message == "Pagamento já processado"
    
    def test_refund_flow(self, payment_service, valid_payment_request):
        """Testa fluxo de reembolso"""
        # Primeiro, criar um pagamento completado
        result = PaymentResult(
            success=True,
            payment_id=valid_payment_request.payment_id,
            status=PaymentStatus.COMPLETED.value,
            message="Pagamento processado"
        )
        payment_service._save_payment(valid_payment_request, result)
        
        # Processar reembolso
        refund_request = PaymentRefundRequest(
            refund_id="refund_123",
            payment_id=valid_payment_request.payment_id,
            amount=50.00,
            reason="Customer request"
        )
        
        refund_result = payment_service.process_refund(refund_request)
        
        assert refund_result.success is True
        assert refund_result.payment_id == valid_payment_request.payment_id
        assert refund_result.status == PaymentStatus.REFUNDED.value


class TestPaymentV1ServiceErrorHandling:
    """Testes de tratamento de erros para PaymentV1Service"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def payment_service(self, temp_db_path):
        """Instância do PaymentV1Service para testes"""
        with patch.dict(os.environ, {
            'PAYMENT_PROVIDER': 'stripe',
            'PAYMENT_API_KEY': 'test_api_key',
            'PAYMENT_SECRET_KEY': 'test_secret_key',
            'PAYMENT_WEBHOOK_SECRET': 'test_webhook_secret',
            'PAYMENT_ENVIRONMENT': 'test'
        }):
            service = PaymentV1Service(db_path=temp_db_path)
            yield service
            service.close()
    
    @patch('requests.post')
    def test_gateway_connection_error(self, mock_post, payment_service):
        """Testa erro de conexão com gateway"""
        mock_post.side_effect = Exception("Connection error")
        
        payment_request = PaymentRequest(
            payment_id="test_payment_123",
            amount=100.00,
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={"name": "João", "email": "joao@example.com"},
            payment_data={"card_number": "4242424242424242", "exp_month": "12", "exp_year": "2025", "cvc": "123"}
        )
        
        result = payment_service.process_payment(payment_request)
        
        assert result.success is False
        assert result.error_code == "INTERNAL_ERROR"
        assert "Connection error" in result.error_details
    
    def test_database_error_handling(self, payment_service):
        """Testa tratamento de erro de banco de dados"""
        # Fechar conexão para simular erro
        payment_service.db.close()
        
        payment_request = PaymentRequest(
            payment_id="test_payment_123",
            amount=100.00,
            currency=Currency.BRL.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            customer={"name": "João", "email": "joao@example.com"},
            payment_data={"card_number": "4242424242424242", "exp_month": "12", "exp_year": "2025", "cvc": "123"}
        )
        
        result = PaymentResult(
            success=True,
            payment_id=payment_request.payment_id,
            status=PaymentStatus.PROCESSING.value,
            message="Pagamento processado"
        )
        
        # Deve levantar exceção ao tentar salvar
        with pytest.raises(Exception):
            payment_service._save_payment(payment_request, result)


class TestPaymentV1ServicePerformance:
    """Testes de performance para PaymentV1Service"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria caminho temporário para banco de dados"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Limpar após teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def payment_service(self, temp_db_path):
        """Instância do PaymentV1Service para testes"""
        with patch.dict(os.environ, {
            'PAYMENT_PROVIDER': 'stripe',
            'PAYMENT_API_KEY': 'test_api_key',
            'PAYMENT_SECRET_KEY': 'test_secret_key',
            'PAYMENT_WEBHOOK_SECRET': 'test_webhook_secret',
            'PAYMENT_ENVIRONMENT': 'test'
        }):
            service = PaymentV1Service(db_path=temp_db_path)
            yield service
            service.close()
    
    def test_multiple_payments_performance(self, payment_service):
        """Testa performance de múltiplos pagamentos"""
        import time
        
        start_time = time.time()
        
        # Processar múltiplos pagamentos
        for i in range(10):
            payment_request = PaymentRequest(
                payment_id=f"test_payment_{i}",
                amount=100.00,
                currency=Currency.BRL.value,
                payment_method=PaymentMethod.CREDIT_CARD.value,
                customer={"name": f"Cliente {i}", "email": f"cliente{i}@example.com"},
                payment_data={"card_number": "4242424242424242", "exp_month": "12", "exp_year": "2025", "cvc": "123"}
            )
            
            result = PaymentResult(
                success=True,
                payment_id=payment_request.payment_id,
                status=PaymentStatus.PROCESSING.value,
                message="Pagamento processado"
            )
            
            payment_service._save_payment(payment_request, result)
        
        end_time = time.time()
        
        # Verificar se todos foram salvos
        for i in range(10):
            payment = payment_service.get_payment(f"test_payment_{i}")
            assert payment is not None
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 10 pagamentos


if __name__ == "__main__":
    pytest.main([__file__]) 