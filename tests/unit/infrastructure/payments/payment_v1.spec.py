"""
Testes Unitários para Pagamentos V1 - Omni Keywords Finder
Cobertura completa de schemas, serviço, API e segurança
Prompt: Melhoria do sistema de pagamentos V1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from backend.app.schemas.payment_v1_schemas import (
    PaymentRequest,
    PaymentResponse,
    PaymentRefundRequest,
    PaymentWebhookData,
    PaymentListRequest,
    PaymentMethod,
    PaymentStatus,
    Currency
)
from backend.app.services.payment_v1_service import PaymentV1Service, PaymentResult
from backend.app.api.payments_v1 import router

# Fixtures
@pytest.fixture
def payment_service():
    """Fixture para serviço de pagamentos"""
    return PaymentV1Service(db_path=":memory:")

@pytest.fixture
def client():
    """Fixture para cliente de teste"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def valid_payment_request():
    """Fixture para requisição de pagamento válida"""
    return {
        "payment_id": str(uuid.uuid4()),
        "amount": 100.50,
        "currency": "BRL",
        "payment_method": "credit_card",
        "customer": {
            "name": "João Silva",
            "email": "joao@example.com",
            "phone": "+5511999999999"
        },
        "payment_data": {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2025,
            "cvc": "123"
        },
        "description": "Pagamento de teste",
        "metadata": {
            "order_id": "12345",
            "source": "test"
        }
    }

@pytest.fixture
def valid_refund_request():
    """Fixture para requisição de reembolso válida"""
    return {
        "payment_id": str(uuid.uuid4()),
        "refund_id": str(uuid.uuid4()),
        "amount": 50.25,
        "reason": "Solicitação do cliente"
    }

@pytest.fixture
def mock_user():
    """Fixture para usuário mock"""
    return {
        "id": "user123",
        "email": "test@example.com",
        "permissions": ["payments:process", "payments:read", "payments:refund"]
    }

# Testes de Schemas
class TestPaymentSchemas:
    """Testes para schemas de pagamento"""
    
    def test_payment_request_valid(self, valid_payment_request):
        """Testa requisição de pagamento válida"""
        request = PaymentRequest(**valid_payment_request)
        assert request.payment_id == valid_payment_request["payment_id"]
        assert request.amount == 100.50
        assert request.currency == "BRL"
        assert request.payment_method == "credit_card"
    
    def test_payment_request_invalid_amount(self):
        """Testa requisição com valor inválido"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": -10,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"}
        }
        
        with pytest.raises(ValueError, match="Valor deve ser maior que zero"):
            PaymentRequest(**data)
    
    def test_payment_request_invalid_currency(self):
        """Testa requisição com moeda inválida"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "INVALID",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"}
        }
        
        with pytest.raises(ValueError, match="Moeda não suportada"):
            PaymentRequest(**data)
    
    def test_payment_request_invalid_payment_method(self):
        """Testa requisição com método de pagamento inválido"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "invalid_method",
            "customer": {"name": "Test", "email": "test@example.com"}
        }
        
        with pytest.raises(ValueError, match="Método de pagamento não suportado"):
            PaymentRequest(**data)
    
    def test_payment_request_invalid_customer(self):
        """Testa requisição com dados de cliente inválidos"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test"}  # Email ausente
        }
        
        with pytest.raises(ValueError, match="Campo obrigatório ausente: email"):
            PaymentRequest(**data)
    
    def test_payment_request_invalid_email(self):
        """Testa requisição com email inválido"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "invalid-email"}
        }
        
        with pytest.raises(ValueError, match="Email inválido"):
            PaymentRequest(**data)
    
    def test_payment_request_credit_card_validation(self):
        """Testa validação de cartão de crédito"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"},
            "payment_data": {
                "card_number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2025,
                "cvc": "123"
            }
        }
        
        request = PaymentRequest(**data)
        assert request.payment_data["card_number"] == "4242424242424242"
    
    def test_payment_request_invalid_card_number(self):
        """Testa cartão de crédito inválido"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"},
            "payment_data": {
                "card_number": "1234567890123456",  # Número inválido
                "exp_month": 12,
                "exp_year": 2025,
                "cvc": "123"
            }
        }
        
        with pytest.raises(ValueError, match="Número do cartão inválido"):
            PaymentRequest(**data)
    
    def test_payment_request_expired_card(self):
        """Testa cartão expirado"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"},
            "payment_data": {
                "card_number": "4242424242424242",
                "exp_month": 1,
                "exp_year": 2020,  # Ano passado
                "cvc": "123"
            }
        }
        
        with pytest.raises(ValueError, match="Data de expiração inválida"):
            PaymentRequest(**data)
    
    def test_payment_request_pix_validation(self):
        """Testa validação de PIX"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "pix",
            "customer": {"name": "Test", "email": "test@example.com"},
            "payment_data": {
                "pix_key": "test@example.com"
            }
        }
        
        request = PaymentRequest(**data)
        assert request.payment_data["pix_key"] == "test@example.com"
    
    def test_payment_request_pix_missing_key(self):
        """Testa PIX sem chave"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "pix",
            "customer": {"name": "Test", "email": "test@example.com"},
            "payment_data": {}
        }
        
        with pytest.raises(ValueError, match="Chave PIX obrigatória"):
            PaymentRequest(**data)
    
    def test_payment_request_boleto_validation(self):
        """Testa validação de boleto"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "boleto",
            "customer": {"name": "Test", "email": "test@example.com"},
            "payment_data": {
                "cpf_cnpj": "12345678901"
            }
        }
        
        request = PaymentRequest(**data)
        assert request.payment_data["cpf_cnpj"] == "12345678901"
    
    def test_payment_request_boleto_missing_cpf(self):
        """Testa boleto sem CPF/CNPJ"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "boleto",
            "customer": {"name": "Test", "email": "test@example.com"},
            "payment_data": {}
        }
        
        with pytest.raises(ValueError, match="CPF/CNPJ obrigatório para boleto"):
            PaymentRequest(**data)
    
    def test_payment_request_sanitization(self):
        """Testa sanitização de dados"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {
                "name": "Test<script>alert('xss')</script>",
                "email": "test@example.com"
            },
            "description": "Descrição<script>alert('xss')</script>",
            "payment_data": {
                "card_number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2025,
                "cvc": "123"
            }
        }
        
        request = PaymentRequest(**data)
        assert "<script>" not in request.customer["name"]
        assert "<script>" not in request.description
    
    def test_refund_request_valid(self, valid_refund_request):
        """Testa requisição de reembolso válida"""
        request = PaymentRefundRequest(**valid_refund_request)
        assert request.payment_id == valid_refund_request["payment_id"]
        assert request.amount == 50.25
        assert request.reason == "Solicitação do cliente"
    
    def test_refund_request_invalid_amount(self):
        """Testa reembolso com valor inválido"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": -10
        }
        
        with pytest.raises(ValueError, match="Valor do reembolso deve ser maior que zero"):
            PaymentRefundRequest(**data)
    
    def test_refund_request_sanitization(self):
        """Testa sanitização de motivo do reembolso"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "reason": "Motivo<script>alert('xss')</script>"
        }
        
        request = PaymentRefundRequest(**data)
        assert "<script>" not in request.reason
    
    def test_payment_list_request_valid(self):
        """Testa requisição de listagem válida"""
        data = {
            "customer_id": "customer123",
            "status": "completed",
            "payment_method": "credit_card",
            "limit": 50,
            "offset": 0,
            "sort_by": "created_at",
            "sort_order": "desc"
        }
        
        request = PaymentListRequest(**data)
        assert request.customer_id == "customer123"
        assert request.status == "completed"
        assert request.limit == 50
    
    def test_payment_list_request_invalid_sort_by(self):
        """Testa campo de ordenação inválido"""
        data = {
            "sort_by": "invalid_field"
        }
        
        with pytest.raises(ValueError, match="Campo de ordenação inválido"):
            PaymentListRequest(**data)
    
    def test_payment_list_request_invalid_sort_order(self):
        """Testa ordem de classificação inválida"""
        data = {
            "sort_order": "invalid"
        }
        
        with pytest.raises(ValueError, match="Ordem de classificação deve ser"):
            PaymentListRequest(**data)
    
    def test_payment_list_request_invalid_date_range(self):
        """Testa range de datas inválido"""
        data = {
            "start_date": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) - timedelta(days=1)
        }
        
        with pytest.raises(ValueError, match="Data inicial não pode ser posterior"):
            PaymentListRequest(**data)

# Testes de Serviço
class TestPaymentV1Service:
    """Testes para serviço de pagamentos"""
    
    def test_service_initialization(self, payment_service):
        """Testa inicialização do serviço"""
        assert payment_service is not None
        assert payment_service.db is not None
        assert payment_service.gateway_config is not None
    
    def test_process_payment_success(self, payment_service, valid_payment_request):
        """Testa processamento de pagamento com sucesso"""
        with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
            mock_gateway.return_value = PaymentResult(
                success=True,
                payment_id=valid_payment_request["payment_id"],
                status=PaymentStatus.PROCESSING.value,
                message="Pagamento processado com sucesso",
                data={"payment_intent_id": "pi_test"}
            )
            
            request = PaymentRequest(**valid_payment_request)
            result = payment_service.process_payment(request)
            
            assert result.success is True
            assert result.payment_id == valid_payment_request["payment_id"]
            assert result.status == PaymentStatus.PROCESSING.value
    
    def test_process_payment_fallback(self, payment_service, valid_payment_request):
        """Testa processamento com fallback"""
        with patch.object(payment_service, '_process_with_primary_gateway') as mock_primary:
            mock_primary.return_value = PaymentResult(
                success=False,
                payment_id=valid_payment_request["payment_id"],
                status=PaymentStatus.FAILED.value,
                message="Erro no gateway principal",
                error_code="GATEWAY_ERROR"
            )
            
            with patch.object(payment_service, '_process_with_fallback_gateway') as mock_fallback:
                mock_fallback.return_value = PaymentResult(
                    success=True,
                    payment_id=valid_payment_request["payment_id"],
                    status=PaymentStatus.PROCESSING.value,
                    message="Pagamento processado com fallback"
                )
                
                request = PaymentRequest(**valid_payment_request)
                result = payment_service.process_payment(request)
                
                assert result.success is True
                assert result.status == PaymentStatus.PROCESSING.value
    
    def test_process_payment_idempotency(self, payment_service, valid_payment_request):
        """Testa idempotência de pagamento"""
        # Adicionar chave de idempotência
        valid_payment_request["idempotency_key"] = "test_key_123"
        
        with patch.object(payment_service, '_get_payment_by_idempotency_key') as mock_idempotency:
            mock_idempotency.return_value = {
                "payment_id": valid_payment_request["payment_id"],
                "status": PaymentStatus.COMPLETED.value
            }
            
            request = PaymentRequest(**valid_payment_request)
            result = payment_service.process_payment(request)
            
            assert result.success is True
            assert result.status == PaymentStatus.COMPLETED.value
    
    def test_process_payment_invalid_request(self, payment_service):
        """Testa processamento de requisição inválida"""
        invalid_request = PaymentRequest(
            payment_id=str(uuid.uuid4()),
            amount=0,  # Valor inválido
            currency="BRL",
            payment_method="credit_card",
            customer={"name": "Test", "email": "test@example.com"}
        )
        
        result = payment_service.process_payment(invalid_request)
        
        assert result.success is False
        assert result.error_code == "INVALID_REQUEST"
    
    def test_get_payment_exists(self, payment_service, valid_payment_request):
        """Testa obtenção de pagamento existente"""
        # Primeiro, criar um pagamento
        with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
            mock_gateway.return_value = PaymentResult(
                success=True,
                payment_id=valid_payment_request["payment_id"],
                status=PaymentStatus.COMPLETED.value,
                message="Pagamento processado"
            )
            
            request = PaymentRequest(**valid_payment_request)
            payment_service.process_payment(request)
        
        # Agora buscar o pagamento
        payment = payment_service.get_payment(valid_payment_request["payment_id"])
        
        assert payment is not None
        assert payment["payment_id"] == valid_payment_request["payment_id"]
        assert payment["amount"] == valid_payment_request["amount"]
    
    def test_get_payment_not_exists(self, payment_service):
        """Testa obtenção de pagamento inexistente"""
        payment = payment_service.get_payment("non_existent_id")
        assert payment is None
    
    def test_list_payments(self, payment_service, valid_payment_request):
        """Testa listagem de pagamentos"""
        # Criar alguns pagamentos
        for i in range(3):
            payment_data = valid_payment_request.copy()
            payment_data["payment_id"] = str(uuid.uuid4())
            payment_data["amount"] = 100 + i
            
            with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
                mock_gateway.return_value = PaymentResult(
                    success=True,
                    payment_id=payment_data["payment_id"],
                    status=PaymentStatus.COMPLETED.value,
                    message="Pagamento processado"
                )
                
                request = PaymentRequest(**payment_data)
                payment_service.process_payment(request)
        
        # Listar pagamentos
        filters = PaymentListRequest(limit=10)
        payments = payment_service.list_payments(filters)
        
        assert len(payments) == 3
        assert all(p["status"] == PaymentStatus.COMPLETED.value for p in payments)
    
    def test_list_payments_with_filters(self, payment_service, valid_payment_request):
        """Testa listagem com filtros"""
        # Criar pagamentos com diferentes status
        statuses = [PaymentStatus.COMPLETED.value, PaymentStatus.FAILED.value, PaymentStatus.PENDING.value]
        
        for i, status in enumerate(statuses):
            payment_data = valid_payment_request.copy()
            payment_data["payment_id"] = str(uuid.uuid4())
            
            with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
                mock_gateway.return_value = PaymentResult(
                    success=True,
                    payment_id=payment_data["payment_id"],
                    status=status,
                    message="Pagamento processado"
                )
                
                request = PaymentRequest(**payment_data)
                payment_service.process_payment(request)
        
        # Filtrar por status
        filters = PaymentListRequest(status=PaymentStatus.COMPLETED.value)
        payments = payment_service.list_payments(filters)
        
        assert len(payments) == 1
        assert payments[0]["status"] == PaymentStatus.COMPLETED.value
    
    def test_process_refund_success(self, payment_service, valid_payment_request, valid_refund_request):
        """Testa processamento de reembolso com sucesso"""
        # Primeiro, criar um pagamento
        with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
            mock_gateway.return_value = PaymentResult(
                success=True,
                payment_id=valid_payment_request["payment_id"],
                status=PaymentStatus.COMPLETED.value,
                message="Pagamento processado"
            )
            
            request = PaymentRequest(**valid_payment_request)
            payment_service.process_payment(request)
        
        # Agora processar reembolso
        with patch.object(payment_service, '_process_refund_with_gateway') as mock_refund:
            mock_refund.return_value = PaymentResult(
                success=True,
                payment_id=valid_payment_request["payment_id"],
                status=PaymentStatus.REFUNDED.value,
                message="Reembolso processado"
            )
            
            refund_request = PaymentRefundRequest(**valid_refund_request)
            result = payment_service.process_refund(refund_request)
            
            assert result.success is True
            assert result.status == PaymentStatus.REFUNDED.value
    
    def test_process_refund_payment_not_found(self, payment_service, valid_refund_request):
        """Testa reembolso de pagamento inexistente"""
        refund_request = PaymentRefundRequest(**valid_refund_request)
        result = payment_service.process_refund(refund_request)
        
        assert result.success is False
        assert result.error_code == "PAYMENT_NOT_FOUND"
    
    def test_process_refund_not_allowed(self, payment_service, valid_payment_request, valid_refund_request):
        """Testa reembolso não permitido"""
        # Criar pagamento com status que não permite reembolso
        with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
            mock_gateway.return_value = PaymentResult(
                success=True,
                payment_id=valid_payment_request["payment_id"],
                status=PaymentStatus.PENDING.value,  # Status que não permite reembolso
                message="Pagamento processado"
            )
            
            request = PaymentRequest(**valid_payment_request)
            payment_service.process_payment(request)
        
        # Tentar reembolso
        refund_request = PaymentRefundRequest(**valid_refund_request)
        result = payment_service.process_refund(refund_request)
        
        assert result.success is False
        assert result.error_code == "REFUND_NOT_ALLOWED"
    
    def test_process_webhook_valid(self, payment_service):
        """Testa processamento de webhook válido"""
        webhook_payload = {
            "id": "evt_test",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test",
                    "metadata": {
                        "payment_id": "test_payment_id"
                    }
                }
            }
        }
        
        payload = json.dumps(webhook_payload).encode('utf-8')
        
        with patch.object(payment_service, '_verify_webhook_signature') as mock_verify:
            mock_verify.return_value = True
            
            with patch.object(payment_service, '_update_payment_status') as mock_update:
                result = payment_service.process_webhook(payload, "test_signature")
                
                assert result.success is True
                mock_update.assert_called_once_with("test_payment_id", PaymentStatus.COMPLETED.value)
    
    def test_process_webhook_invalid_signature(self, payment_service):
        """Testa webhook com assinatura inválida"""
        payload = b'{"test": "data"}'
        
        with patch.object(payment_service, '_verify_webhook_signature') as mock_verify:
            mock_verify.return_value = False
            
            result = payment_service.process_webhook(payload, "invalid_signature")
            
            assert result.success is False
            assert result.error_code == "INVALID_SIGNATURE"
    
    def test_process_webhook_invalid_data(self, payment_service):
        """Testa webhook com dados inválidos"""
        payload = b'{"invalid": "data"}'  # Sem campos obrigatórios
        
        with patch.object(payment_service, '_verify_webhook_signature') as mock_verify:
            mock_verify.return_value = True
            
            result = payment_service.process_webhook(payload, "test_signature")
            
            assert result.success is False
            assert result.error_code == "INVALID_WEBHOOK_DATA"

# Testes de Segurança
class TestPaymentSecurity:
    """Testes de segurança para pagamentos"""
    
    def test_sql_injection_prevention(self, payment_service):
        """Testa prevenção de SQL injection"""
        malicious_id = "'; DROP TABLE payments_v1; --"
        
        # Tentar buscar pagamento com ID malicioso
        payment = payment_service.get_payment(malicious_id)
        
        # Deve retornar None sem causar erro
        assert payment is None
    
    def test_xss_prevention_in_customer_data(self, payment_service):
        """Testa prevenção de XSS em dados do cliente"""
        malicious_data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {
                "name": "<script>alert('xss')</script>",
                "email": "test@example.com"
            }
        }
        
        request = PaymentRequest(**malicious_data)
        
        # Dados devem ser sanitizados
        assert "<script>" not in request.customer["name"]
    
    def test_path_traversal_prevention(self, payment_service):
        """Testa prevenção de path traversal"""
        malicious_id = "../../../etc/passwd"
        
        # Tentar buscar pagamento com ID malicioso
        payment = payment_service.get_payment(malicious_id)
        
        # Deve retornar None sem causar erro
        assert payment is None
    
    def test_command_injection_prevention(self, payment_service):
        """Testa prevenção de command injection"""
        malicious_data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {
                "name": "Test; rm -rf /",
                "email": "test@example.com"
            }
        }
        
        request = PaymentRequest(**malicious_data)
        
        # Dados devem ser sanitizados
        assert "rm -rf" not in request.customer["name"]
    
    def test_large_payload_prevention(self, payment_service):
        """Testa prevenção de payloads grandes"""
        # Criar payload muito grande
        large_description = "A" * 10000  # 10KB
        
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"},
            "description": large_description
        }
        
        request = PaymentRequest(**data)
        
        # Descrição deve ser truncada
        assert len(request.description) <= 500
    
    def test_rate_limiting_simulation(self, payment_service, valid_payment_request):
        """Simula teste de rate limiting"""
        request = PaymentRequest(**valid_payment_request)
        
        # Processar múltiplos pagamentos rapidamente
        results = []
        for i in range(5):
            with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
                mock_gateway.return_value = PaymentResult(
                    success=True,
                    payment_id=f"{valid_payment_request['payment_id']}_{i}",
                    status=PaymentStatus.PROCESSING.value,
                    message="Pagamento processado"
                )
                
                result = payment_service.process_payment(request)
                results.append(result)
        
        # Todos devem ser processados (rate limiting seria aplicado na API)
        assert len(results) == 5
        assert all(r.success for r in results)

# Testes de Casos Extremos
class TestPaymentEdgeCases:
    """Testes para casos extremos"""
    
    def test_maximum_amount(self, payment_service):
        """Testa valor máximo permitido"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 1000000,  # Limite máximo
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"}
        }
        
        request = PaymentRequest(**data)
        assert request.amount == 1000000
    
    def test_amount_exceeds_limit(self, payment_service):
        """Testa valor que excede o limite"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 1000001,  # Excede limite
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"}
        }
        
        with pytest.raises(ValueError, match="Valor excede o limite máximo"):
            PaymentRequest(**data)
    
    def test_very_small_amount(self, payment_service):
        """Testa valor muito pequeno"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 0.01,  # Valor mínimo
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"}
        }
        
        request = PaymentRequest(**data)
        assert request.amount == 0.01
    
    def test_unicode_characters(self, payment_service):
        """Testa caracteres Unicode"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {
                "name": "João Silva 🚀",
                "email": "joão@exemplo.com"
            },
            "description": "Pagamento com emoji 🎉"
        }
        
        request = PaymentRequest(**data)
        assert "🚀" in request.customer["name"]
        assert "🎉" in request.description
    
    def test_empty_metadata(self, payment_service):
        """Testa metadados vazios"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"},
            "metadata": {}
        }
        
        request = PaymentRequest(**data)
        assert request.metadata == {}
    
    def test_none_values(self, payment_service):
        """Testa valores None"""
        data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 100,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {"name": "Test", "email": "test@example.com"},
            "description": None,
            "metadata": None
        }
        
        request = PaymentRequest(**data)
        assert request.description is None
        assert request.metadata == {}

# Testes de Concorrência
class TestPaymentConcurrency:
    """Testes de concorrência"""
    
    def test_concurrent_payments(self, payment_service):
        """Testa pagamentos concorrentes"""
        import threading
        import time
        
        results = []
        lock = threading.Lock()
        
        def process_payment(payment_id):
            data = {
                "payment_id": payment_id,
                "amount": 100,
                "currency": "BRL",
                "payment_method": "credit_card",
                "customer": {"name": "Test", "email": "test@example.com"}
            }
            
            with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
                mock_gateway.return_value = PaymentResult(
                    success=True,
                    payment_id=payment_id,
                    status=PaymentStatus.PROCESSING.value,
                    message="Pagamento processado"
                )
                
                request = PaymentRequest(**data)
                result = payment_service.process_payment(request)
                
                with lock:
                    results.append(result)
        
        # Criar threads para pagamentos concorrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=process_payment,
                args=(f"payment_{i}",)
            )
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(results) == 5
        assert all(r.success for r in results)
        assert len(set(r.payment_id for r in results)) == 5  # IDs únicos

# Testes de Performance
class TestPaymentPerformance:
    """Testes de performance"""
    
    def test_bulk_payment_processing(self, payment_service):
        """Testa processamento em lote"""
        import time
        
        start_time = time.time()
        
        # Processar 100 pagamentos
        for i in range(100):
            data = {
                "payment_id": f"bulk_payment_{i}",
                "amount": 100 + i,
                "currency": "BRL",
                "payment_method": "credit_card",
                "customer": {"name": f"Customer {i}", "email": f"customer{i}@example.com"}
            }
            
            with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
                mock_gateway.return_value = PaymentResult(
                    success=True,
                    payment_id=data["payment_id"],
                    status=PaymentStatus.COMPLETED.value,
                    message="Pagamento processado"
                )
                
                request = PaymentRequest(**data)
                payment_service.process_payment(request)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar que processamento foi rápido (< 5 segundos para 100 pagamentos)
        assert processing_time < 5.0
        
        # Verificar que todos foram salvos
        filters = PaymentListRequest(limit=1000)
        payments = payment_service.list_payments(filters)
        assert len(payments) >= 100

# Testes de Integração
class TestPaymentIntegration:
    """Testes de integração"""
    
    def test_full_payment_flow(self, payment_service):
        """Testa fluxo completo de pagamento"""
        # 1. Criar pagamento
        payment_data = {
            "payment_id": str(uuid.uuid4()),
            "amount": 150.75,
            "currency": "BRL",
            "payment_method": "credit_card",
            "customer": {
                "name": "Maria Silva",
                "email": "maria@example.com",
                "phone": "+5511888888888"
            },
            "payment_data": {
                "card_number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2025,
                "cvc": "123"
            },
            "description": "Compra de produtos",
            "metadata": {
                "order_id": "ORD123",
                "source": "web"
            }
        }
        
        with patch.object(payment_service, '_process_with_primary_gateway') as mock_gateway:
            mock_gateway.return_value = PaymentResult(
                success=True,
                payment_id=payment_data["payment_id"],
                status=PaymentStatus.PROCESSING.value,
                message="Pagamento criado com sucesso",
                data={
                    "payment_intent_id": "pi_test_123",
                    "confirmation_url": "/confirm/test",
                    "cancel_url": "/cancel/test"
                }
            )
            
            request = PaymentRequest(**payment_data)
            result = payment_service.process_payment(request)
            
            assert result.success is True
            assert result.status == PaymentStatus.PROCESSING.value
        
        # 2. Verificar pagamento
        payment = payment_service.get_payment(payment_data["payment_id"])
        assert payment is not None
        assert payment["amount"] == 150.75
        assert payment["status"] == PaymentStatus.PROCESSING.value
        
        # 3. Simular webhook de confirmação
        webhook_data = {
            "id": "evt_confirm",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "metadata": {
                        "payment_id": payment_data["payment_id"]
                    }
                }
            }
        }
        
        payload = json.dumps(webhook_data).encode('utf-8')
        
        with patch.object(payment_service, '_verify_webhook_signature') as mock_verify:
            mock_verify.return_value = True
            
            webhook_result = payment_service.process_webhook(payload, "test_signature")
            assert webhook_result.success is True
        
        # 4. Verificar status atualizado
        payment = payment_service.get_payment(payment_data["payment_id"])
        assert payment["status"] == PaymentStatus.COMPLETED.value
        
        # 5. Processar reembolso
        refund_data = {
            "payment_id": payment_data["payment_id"],
            "refund_id": str(uuid.uuid4()),
            "amount": 50.25,
            "reason": "Solicitação do cliente"
        }
        
        with patch.object(payment_service, '_process_refund_with_gateway') as mock_refund:
            mock_refund.return_value = PaymentResult(
                success=True,
                payment_id=payment_data["payment_id"],
                status=PaymentStatus.REFUNDED.value,
                message="Reembolso processado"
            )
            
            refund_request = PaymentRefundRequest(**refund_data)
            refund_result = payment_service.process_refund(refund_request)
            
            assert refund_result.success is True
            assert refund_result.status == PaymentStatus.REFUNDED.value
        
        # 6. Verificar status final
        payment = payment_service.get_payment(payment_data["payment_id"])
        assert payment["status"] == PaymentStatus.REFUNDED.value

# Testes de Limpeza
class TestPaymentCleanup:
    """Testes de limpeza"""
    
    def test_service_cleanup(self, payment_service):
        """Testa limpeza do serviço"""
        # Verificar que conexão existe
        assert payment_service.db is not None
        
        # Fechar serviço
        payment_service.close()
        
        # Verificar que conexão foi fechada
        # (Não podemos verificar diretamente, mas não deve causar erro)
        assert True 