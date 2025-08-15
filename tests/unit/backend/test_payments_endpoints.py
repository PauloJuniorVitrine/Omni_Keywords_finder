"""
🧪 Testes Unitários - Endpoints de Pagamentos

Tracing ID: TEST_PAYMENTS_20250127_001
Data/Hora: 2025-01-27 16:00:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Testes unitários para os endpoints de pagamentos do sistema Omni Keywords Finder.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime
from backend.app.api.payments import payments_bp
from backend.app.api.payments_v1 import payments_v1_bp
from backend.app.models import Payment, User
from backend.app.schemas.payment_schemas import PaymentCreateRequest, PaymentRefundRequest


class TestPaymentsEndpoints:
    """Testes para endpoints de pagamentos."""
    
    @pytest.fixture
    def app(self):
        """Fixture para criar aplicação Flask de teste."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Registrar blueprints
        app.register_blueprint(payments_bp)
        app.register_blueprint(payments_v1_bp)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Fixture para cliente de teste."""
        return app.test_client()
    
    @pytest.fixture
    def mock_payment(self):
        """Fixture para pagamento mock."""
        payment = Mock(spec=Payment)
        payment.id = 1
        payment.user_id = 1
        payment.amount = 1000  # $10.00
        payment.currency = 'usd'
        payment.status = 'succeeded'
        payment.stripe_payment_intent_id = 'pi_test_123'
        payment.created_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        payment.metadata = {'plan': 'premium', 'months': 1}
        return payment
    
    @pytest.fixture
    def mock_user(self):
        """Fixture para usuário mock."""
        user = Mock(spec=User)
        user.id = 1
        user.email = 'test@example.com'
        user.stripe_customer_id = 'cus_test_123'
        return user
    
    @patch('backend.app.api.payments.auth_required')
    def test_create_payment_success(self, mock_auth, client, mock_user, mock_payment):
        """Teste de criação de pagamento bem-sucedida."""
        with patch('backend.app.api.payments.User.query') as mock_user_query, \
             patch('backend.app.api.payments.stripe.PaymentIntent.create') as mock_stripe_create, \
             patch('backend.app.api.payments.db') as mock_db, \
             patch('backend.app.api.payments.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_stripe_create.return_value = Mock(
                id='pi_test_123',
                client_secret='pi_test_123_secret'
            )
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            payment_data = {
                'amount': 1000,
                'currency': 'usd',
                'payment_method_id': 'pm_test_123',
                'metadata': {
                    'plan': 'premium',
                    'months': 1
                }
            }
            
            # Fazer requisição
            response = client.post('/api/payments/', 
                                 data=json.dumps(payment_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'payment_intent_id' in data
            assert 'client_secret' in data
            
            # Verificar se logs foram chamados
            mock_log.assert_called()
    
    @patch('backend.app.api.payments.auth_required')
    def test_create_payment_invalid_data(self, mock_auth, client):
        """Teste de criação de pagamento com dados inválidos."""
        # Dados inválidos
        payment_data = {
            'amount': -100,  # Valor negativo
            'currency': 'usd'
        }
        
        # Fazer requisição
        response = client.post('/api/payments/', 
                             data=json.dumps(payment_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    @patch('backend.app.api.payments.auth_required')
    def test_create_payment_stripe_error(self, mock_auth, client, mock_user):
        """Teste de criação de pagamento com erro do Stripe."""
        with patch('backend.app.api.payments.User.query') as mock_user_query, \
             patch('backend.app.api.payments.stripe.PaymentIntent.create') as mock_stripe_create:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_stripe_create.side_effect = Exception('Stripe error')
            
            # Dados de teste
            payment_data = {
                'amount': 1000,
                'currency': 'usd',
                'payment_method_id': 'pm_test_123'
            }
            
            # Fazer requisição
            response = client.post('/api/payments/', 
                                 data=json.dumps(payment_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.api.payments.auth_required')
    def test_get_payment_success(self, mock_auth, client, mock_payment):
        """Teste de obtenção de pagamento bem-sucedida."""
        with patch('backend.app.api.payments.Payment.query') as mock_payment_query, \
             patch('backend.app.api.payments.log_event') as mock_log:
            
            # Configurar mocks
            mock_payment_query.get_or_404.return_value = mock_payment
            
            # Fazer requisição
            response = client.get('/api/payments/1')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'payment' in data
            assert data['payment']['id'] == 1
    
    @patch('backend.app.api.payments.auth_required')
    def test_get_payment_not_found(self, mock_auth, client):
        """Teste de obtenção de pagamento não encontrado."""
        with patch('backend.app.api.payments.Payment.query') as mock_payment_query:
            # Configurar mock para pagamento não encontrado
            mock_payment_query.get_or_404.side_effect = Exception('Not found')
            
            # Fazer requisição
            response = client.get('/api/payments/999')
            
            # Verificações
            assert response.status_code == 404
    
    @patch('backend.app.api.payments.auth_required')
    def test_refund_payment_success(self, mock_auth, client, mock_payment):
        """Teste de reembolso de pagamento bem-sucedido."""
        with patch('backend.app.api.payments.Payment.query') as mock_payment_query, \
             patch('backend.app.api.payments.stripe.Refund.create') as mock_stripe_refund, \
             patch('backend.app.api.payments.db') as mock_db, \
             patch('backend.app.api.payments.log_event') as mock_log:
            
            # Configurar mocks
            mock_payment_query.get_or_404.return_value = mock_payment
            mock_stripe_refund.return_value = Mock(
                id='re_test_123',
                status='succeeded'
            )
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            refund_data = {
                'amount': 1000,
                'reason': 'requested_by_customer'
            }
            
            # Fazer requisição
            response = client.post('/api/payments/1/refund', 
                                 data=json.dumps(refund_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'refund_id' in data
            assert 'status' in data
            
            # Verificar se logs foram chamados
            mock_log.assert_called()
    
    @patch('backend.app.api.payments.auth_required')
    def test_refund_payment_already_refunded(self, mock_auth, client, mock_payment):
        """Teste de reembolso de pagamento já reembolsado."""
        # Configurar pagamento já reembolsado
        mock_payment.status = 'refunded'
        
        with patch('backend.app.api.payments.Payment.query') as mock_payment_query:
            # Configurar mocks
            mock_payment_query.get_or_404.return_value = mock_payment
            
            # Dados de teste
            refund_data = {
                'amount': 1000,
                'reason': 'requested_by_customer'
            }
            
            # Fazer requisição
            response = client.post('/api/payments/1/refund', 
                                 data=json.dumps(refund_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.api.payments.auth_required')
    def test_get_payment_history_success(self, mock_auth, client, mock_payment):
        """Teste de obtenção de histórico de pagamentos bem-sucedida."""
        with patch('backend.app.api.payments.Payment.query') as mock_payment_query, \
             patch('backend.app.api.payments.log_event') as mock_log:
            
            # Configurar mocks
            mock_payment_query.filter.return_value.order_by.return_value.paginate.return_value = Mock(
                items=[mock_payment],
                total=1,
                pages=1,
                has_prev=False,
                has_next=False
            )
            
            # Fazer requisição
            response = client.get('/api/payments/history?page=1&per_page=10')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'payments' in data
            assert 'paginacao' in data
    
    @patch('backend.app.api.payments.auth_required')
    def test_get_payment_history_with_filters(self, mock_auth, client, mock_payment):
        """Teste de obtenção de histórico com filtros."""
        with patch('backend.app.api.payments.Payment.query') as mock_payment_query, \
             patch('backend.app.api.payments.log_event') as mock_log:
            
            # Configurar mocks
            mock_payment_query.filter.return_value.order_by.return_value.paginate.return_value = Mock(
                items=[mock_payment],
                total=1,
                pages=1,
                has_prev=False,
                has_next=False
            )
            
            # Fazer requisição com filtros
            response = client.get('/api/payments/history?status=succeeded&currency=usd&page=1&per_page=10')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'payments' in data


class TestPaymentsV1Endpoints:
    """Testes para endpoints de pagamentos v1."""
    
    @patch('backend.app.api.payments_v1.auth_required')
    def test_create_subscription_success(self, mock_auth, client, mock_user):
        """Teste de criação de assinatura bem-sucedida."""
        with patch('backend.app.api.payments_v1.User.query') as mock_user_query, \
             patch('backend.app.api.payments_v1.stripe.Subscription.create') as mock_stripe_sub, \
             patch('backend.app.api.payments_v1.db') as mock_db, \
             patch('backend.app.api.payments_v1.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_stripe_sub.return_value = Mock(
                id='sub_test_123',
                status='active',
                current_period_end=1234567890
            )
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            subscription_data = {
                'price_id': 'price_test_123',
                'payment_method_id': 'pm_test_123',
                'metadata': {
                    'plan': 'premium',
                    'months': 1
                }
            }
            
            # Fazer requisição
            response = client.post('/api/v1/payments/subscriptions', 
                                 data=json.dumps(subscription_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'subscription_id' in data
            assert 'status' in data
    
    @patch('backend.app.api.payments_v1.auth_required')
    def test_cancel_subscription_success(self, mock_auth, client):
        """Teste de cancelamento de assinatura bem-sucedido."""
        with patch('backend.app.api.payments_v1.stripe.Subscription.modify') as mock_stripe_modify, \
             patch('backend.app.api.payments_v1.log_event') as mock_log:
            
            # Configurar mocks
            mock_stripe_modify.return_value = Mock(
                id='sub_test_123',
                status='canceled'
            )
            
            # Fazer requisição
            response = client.post('/api/v1/payments/subscriptions/sub_test_123/cancel')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'subscription_id' in data
            assert data['status'] == 'canceled'
    
    @patch('backend.app.api.payments_v1.auth_required')
    def test_get_invoice_success(self, mock_auth, client):
        """Teste de obtenção de fatura bem-sucedida."""
        with patch('backend.app.api.payments_v1.stripe.Invoice.retrieve') as mock_stripe_invoice, \
             patch('backend.app.api.payments_v1.log_event') as mock_log:
            
            # Configurar mocks
            mock_stripe_invoice.return_value = Mock(
                id='in_test_123',
                amount_paid=1000,
                status='paid',
                hosted_invoice_url='https://invoice.stripe.com/test'
            )
            
            # Fazer requisição
            response = client.get('/api/v1/payments/invoices/in_test_123')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'invoice_id' in data
            assert 'amount_paid' in data


class TestPaymentsSchemas:
    """Testes para schemas de pagamentos."""
    
    def test_payment_create_request_valid(self):
        """Teste de schema de criação de pagamento válido."""
        data = {
            'amount': 1000,
            'currency': 'usd',
            'payment_method_id': 'pm_test_123',
            'metadata': {
                'plan': 'premium',
                'months': 1
            }
        }
        
        request = PaymentCreateRequest(**data)
        
        assert request.amount == 1000
        assert request.currency == 'usd'
        assert request.payment_method_id == 'pm_test_123'
        assert request.metadata['plan'] == 'premium'
    
    def test_payment_create_request_invalid_amount(self):
        """Teste de schema de criação com valor inválido."""
        data = {
            'amount': -100,  # Valor negativo
            'currency': 'usd',
            'payment_method_id': 'pm_test_123'
        }
        
        with pytest.raises(ValueError):
            PaymentCreateRequest(**data)
    
    def test_payment_create_request_invalid_currency(self):
        """Teste de schema de criação com moeda inválida."""
        data = {
            'amount': 1000,
            'currency': 'invalid',  # Moeda inválida
            'payment_method_id': 'pm_test_123'
        }
        
        with pytest.raises(ValueError):
            PaymentCreateRequest(**data)
    
    def test_payment_refund_request_valid(self):
        """Teste de schema de reembolso válido."""
        data = {
            'amount': 1000,
            'reason': 'requested_by_customer'
        }
        
        request = PaymentRefundRequest(**data)
        
        assert request.amount == 1000
        assert request.reason == 'requested_by_customer'
    
    def test_payment_refund_request_invalid_reason(self):
        """Teste de schema de reembolso com motivo inválido."""
        data = {
            'amount': 1000,
            'reason': 'invalid_reason'  # Motivo inválido
        }
        
        with pytest.raises(ValueError):
            PaymentRefundRequest(**data)


class TestPaymentsWebhooks:
    """Testes para webhooks de pagamentos."""
    
    def test_stripe_webhook_success(self, client):
        """Teste de webhook do Stripe bem-sucedido."""
        with patch('backend.app.api.payments.stripe.Webhook.construct_event') as mock_webhook, \
             patch('backend.app.api.payments.handle_payment_intent_succeeded') as mock_handler, \
             patch('backend.app.api.payments.log_event') as mock_log:
            
            # Configurar mocks
            mock_webhook.return_value = {
                'type': 'payment_intent.succeeded',
                'data': {
                    'object': {
                        'id': 'pi_test_123',
                        'amount': 1000,
                        'status': 'succeeded'
                    }
                }
            }
            
            # Fazer requisição
            response = client.post('/api/payments/webhooks/stripe',
                                 data='test_payload',
                                 headers={'Stripe-Signature': 'test_signature'})
            
            # Verificações
            assert response.status_code == 200
            
            # Verificar se handler foi chamado
            mock_handler.assert_called()
    
    def test_stripe_webhook_invalid_signature(self, client):
        """Teste de webhook do Stripe com assinatura inválida."""
        with patch('backend.app.api.payments.stripe.Webhook.construct_event') as mock_webhook:
            # Configurar mock para assinatura inválida
            mock_webhook.side_effect = Exception('Invalid signature')
            
            # Fazer requisição
            response = client.post('/api/payments/webhooks/stripe',
                                 data='test_payload',
                                 headers={'Stripe-Signature': 'invalid_signature'})
            
            # Verificações
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'erro' in data


class TestPaymentsErrorHandling:
    """Testes de tratamento de erros para pagamentos."""
    
    @patch('backend.app.api.payments.auth_required')
    def test_stripe_api_error_handling(self, mock_auth, client, mock_user):
        """Teste de tratamento de erro da API do Stripe."""
        with patch('backend.app.api.payments.User.query') as mock_user_query, \
             patch('backend.app.api.payments.stripe.PaymentIntent.create') as mock_stripe_create:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_stripe_create.side_effect = Exception('Stripe API error')
            
            # Dados de teste
            payment_data = {
                'amount': 1000,
                'currency': 'usd',
                'payment_method_id': 'pm_test_123'
            }
            
            # Fazer requisição
            response = client.post('/api/payments/', 
                                 data=json.dumps(payment_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.api.payments.auth_required')
    def test_database_error_handling(self, mock_auth, client, mock_user):
        """Teste de tratamento de erro de banco de dados."""
        with patch('backend.app.api.payments.User.query') as mock_user_query, \
             patch('backend.app.api.payments.stripe.PaymentIntent.create') as mock_stripe_create, \
             patch('backend.app.api.payments.db') as mock_db:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_stripe_create.return_value = Mock(
                id='pi_test_123',
                client_secret='pi_test_123_secret'
            )
            mock_db.session.commit.side_effect = Exception('Database error')
            
            # Dados de teste
            payment_data = {
                'amount': 1000,
                'currency': 'usd',
                'payment_method_id': 'pm_test_123'
            }
            
            # Fazer requisição
            response = client.post('/api/payments/', 
                                 data=json.dumps(payment_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'erro' in data


class TestPaymentsSecurity:
    """Testes de segurança para pagamentos."""
    
    def test_webhook_signature_validation(self, client):
        """Teste de validação de assinatura de webhook."""
        with patch('backend.app.api.payments.stripe.Webhook.construct_event') as mock_webhook:
            # Configurar mock para assinatura inválida
            mock_webhook.side_effect = Exception('Invalid signature')
            
            # Fazer requisição sem assinatura
            response = client.post('/api/payments/webhooks/stripe',
                                 data='test_payload')
            
            # Verificações
            assert response.status_code == 400
    
    def test_payment_amount_validation(self, client):
        """Teste de validação de valor de pagamento."""
        # Teste com valor muito alto
        payment_data = {
            'amount': 10000000,  # $100,000
            'currency': 'usd',
            'payment_method_id': 'pm_test_123'
        }
        
        # Fazer requisição
        response = client.post('/api/payments/', 
                             data=json.dumps(payment_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data


# Configuração do pytest
pytestmark = pytest.mark.unit 