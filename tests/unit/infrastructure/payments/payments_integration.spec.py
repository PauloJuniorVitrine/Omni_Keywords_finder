"""
Testes unitários para integração de pagamentos
Prompt: Implementação real de pagamentos
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from backend.app.api.payments import PaymentService, payment_service

@pytest.fixture
def mock_stripe():
    """Mock do Stripe para testes"""
    with patch('backend.app.api.payments.stripe') as mock_stripe:
        yield mock_stripe

@pytest.fixture
def mock_env_vars():
    """Mock das variáveis de ambiente"""
    with patch.dict('os.environ', {
        'STRIPE_SECRET_KEY': 'sk_test_123',
        'STRIPE_WEBHOOK_SECRET': 'whsec_test_123',
        'STRIPE_PUBLISHABLE_KEY': 'pk_test_123'
    }):
        yield

def test_payment_service_initialization(mock_stripe, mock_env_vars):
    """Testa inicialização do PaymentService"""
    service = PaymentService()
    assert service.stripe_available == True

def test_payment_service_stripe_unavailable():
    """Testa PaymentService quando Stripe não está disponível"""
    with patch('backend.app.api.payments.STRIPE_AVAILABLE', False):
        service = PaymentService()
        assert service.stripe_available == False

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_create_payment_intent_success(mock_stripe, mock_env_vars):
    """Testa criação bem-sucedida de PaymentIntent"""
    # Mock do PaymentIntent
    mock_payment_intent = Mock()
    mock_payment_intent.id = 'pi_test_123'
    mock_payment_intent.client_secret = 'pi_test_123_secret'
    mock_payment_intent.amount = 1000
    mock_payment_intent.currency = 'brl'
    mock_payment_intent.status = 'requires_payment_method'
    
    mock_stripe.PaymentIntent.create.return_value = mock_payment_intent
    
    service = PaymentService()
    result = service.create_payment_intent(amount=1000, currency='brl')
    
    assert result['id'] == 'pi_test_123'
    assert result['amount'] == 1000
    assert result['currency'] == 'brl'
    assert result['status'] == 'requires_payment_method'
    
    # Verificar se Stripe foi chamado corretamente
    mock_stripe.PaymentIntent.create.assert_called_once_with(
        amount=1000,
        currency='brl',
        metadata={},
        automatic_payment_methods={'enabled': True}
    )

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_create_payment_intent_stripe_error(mock_stripe, mock_env_vars):
    """Testa erro do Stripe na criação de PaymentIntent"""
    mock_stripe.PaymentIntent.create.side_effect = Exception("Stripe error")
    
    service = PaymentService()
    
    with pytest.raises(Exception) as exc_info:
        service.create_payment_intent(amount=1000)
    
    assert "Erro no processamento de pagamento" in str(exc_info.value)

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_retrieve_payment_intent_success(mock_stripe, mock_env_vars):
    """Testa recuperação bem-sucedida de PaymentIntent"""
    # Mock do PaymentIntent
    mock_payment_intent = Mock()
    mock_payment_intent.id = 'pi_test_123'
    mock_payment_intent.amount = 1000
    mock_payment_intent.currency = 'brl'
    mock_payment_intent.status = 'succeeded'
    mock_payment_intent.payment_method = 'pm_test_123'
    mock_payment_intent.created = 1234567890
    mock_payment_intent.metadata = {'user_id': '123'}
    
    mock_stripe.PaymentIntent.retrieve.return_value = mock_payment_intent
    
    service = PaymentService()
    result = service.retrieve_payment_intent('pi_test_123')
    
    assert result['id'] == 'pi_test_123'
    assert result['status'] == 'succeeded'
    assert result['metadata'] == {'user_id': '123'}
    
    mock_stripe.PaymentIntent.retrieve.assert_called_once_with('pi_test_123')

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_validate_webhook_signature_success(mock_stripe, mock_env_vars):
    """Testa validação bem-sucedida de assinatura de webhook"""
    payload = b'{"type": "payment_intent.succeeded"}'
    signature = 't=1234567890,v1=test_signature'
    
    mock_stripe.Webhook.construct_event.return_value = {
        'type': 'payment_intent.succeeded',
        'id': 'evt_test_123'
    }
    
    service = PaymentService()
    result = service.validate_webhook_signature(payload, signature)
    
    assert result == True
    mock_stripe.Webhook.construct_event.assert_called_once_with(
        payload, signature, 'whsec_test_123'
    )

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_validate_webhook_signature_invalid(mock_stripe, mock_env_vars):
    """Testa validação falhada de assinatura de webhook"""
    payload = b'{"type": "payment_intent.succeeded"}'
    signature = 'invalid_signature'
    
    mock_stripe.Webhook.construct_event.side_effect = Exception("Invalid signature")
    
    service = PaymentService()
    result = service.validate_webhook_signature(payload, signature)
    
    assert result == False

def test_validate_webhook_signature_no_secret():
    """Testa validação sem webhook secret configurado"""
    with patch.dict('os.environ', {}, clear=True):
        service = PaymentService()
        result = service.validate_webhook_signature(b'payload', 'signature')
        assert result == False

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_create_payment_endpoint_success(mock_stripe, mock_env_vars, client):
    """Testa endpoint de criação de pagamento"""
    # Mock do PaymentIntent
    mock_payment_intent = Mock()
    mock_payment_intent.id = 'pi_test_123'
    mock_payment_intent.client_secret = 'pi_test_123_secret'
    mock_payment_intent.amount = 1000
    mock_payment_intent.currency = 'brl'
    mock_payment_intent.status = 'requires_payment_method'
    
    mock_stripe.PaymentIntent.create.return_value = mock_payment_intent
    
    # Mock de autenticação
    with patch('backend.app.middleware.auth_middleware.auth_required') as mock_auth:
        mock_auth.return_value = lambda f: f
        
        response = client.post('/api/payments/create', 
                             json={'amount': 1000, 'currency': 'brl'})
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['payment_intent']['id'] == 'pi_test_123'

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_create_payment_endpoint_invalid_amount(mock_stripe, mock_env_vars, client):
    """Testa endpoint com valor inválido"""
    with patch('backend.app.middleware.auth_middleware.auth_required') as mock_auth:
        mock_auth.return_value = lambda f: f
        
        response = client.post('/api/payments/create', 
                             json={'amount': 50})  # Valor muito baixo
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Valor deve ser inteiro >= 100 centavos' in data['erro']

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_payment_webhook_success(mock_stripe, mock_env_vars, client):
    """Testa webhook de pagamento"""
    payload = {
        'type': 'payment_intent.succeeded',
        'id': 'evt_test_123',
        'data': {
            'object': {
                'id': 'pi_test_123',
                'amount': 1000
            }
        }
    }
    
    mock_stripe.Webhook.construct_event.return_value = payload
    
    response = client.post('/api/payments/webhook',
                          data=json.dumps(payload),
                          headers={'Stripe-Signature': 't=1234567890,v1=test_signature'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'

@patch('backend.app.api.payments.STRIPE_AVAILABLE', True)
def test_payment_webhook_invalid_signature(mock_stripe, mock_env_vars, client):
    """Testa webhook com assinatura inválida"""
    payload = {'type': 'payment_intent.succeeded'}
    
    mock_stripe.Webhook.construct_event.side_effect = Exception("Invalid signature")
    
    response = client.post('/api/payments/webhook',
                          data=json.dumps(payload),
                          headers={'Stripe-Signature': 'invalid_signature'})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['erro'] == 'Assinatura inválida'

def test_payment_config_endpoint(client):
    """Testa endpoint de configuração de pagamento"""
    with patch.dict('os.environ', {'STRIPE_PUBLISHABLE_KEY': 'pk_test_123'}):
        response = client.get('/api/payments/config')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['stripe_publishable_key'] == 'pk_test_123'
        assert data['currency'] == 'brl'
        assert 'card' in data['supported_methods'] 