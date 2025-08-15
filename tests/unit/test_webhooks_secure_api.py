import pytest
from unittest.mock import MagicMock, patch
from myapp.api.webhooks_secure import WebhooksSecureAPI, WebhookReceiver, SignatureValidator, RetryManager

@pytest.fixture
def webhooks_api():
    return WebhooksSecureAPI()

@pytest.fixture
def sample_webhook():
    return {
        'event_type': 'payment.completed',
        'data': {'payment_id': 'pay_123', 'amount': 100.00},
        'timestamp': '2024-01-01T10:00:00Z',
        'signature': 'sha256=abc123'
    }

# 1. Teste de recebimento de webhooks
def test_webhook_reception(webhooks_api, sample_webhook):
    receiver = WebhookReceiver()
    
    # Receber webhook
    reception_result = receiver.receive_webhook(sample_webhook)
    assert reception_result['received'] is True
    assert reception_result['webhook_id'] is not None
    assert reception_result['timestamp'] is not None
    
    # Verificar webhook recebido
    received_webhook = receiver.get_webhook(reception_result['webhook_id'])
    assert received_webhook['event_type'] == 'payment.completed'
    assert received_webhook['data']['payment_id'] == 'pay_123'

# 2. Teste de validação de assinatura
def test_signature_validation(webhooks_api, sample_webhook):
    validator = SignatureValidator()
    
    # Validar assinatura válida
    valid_signature = validator.validate_signature(sample_webhook, 'secret_key')
    assert valid_signature['valid'] is True
    assert valid_signature['algorithm'] == 'sha256'
    
    # Testar assinatura inválida
    invalid_webhook = sample_webhook.copy()
    invalid_webhook['signature'] = 'sha256=invalid'
    invalid_signature = validator.validate_signature(invalid_webhook, 'secret_key')
    assert invalid_signature['valid'] is False

# 3. Teste de processamento
def test_webhook_processing(webhooks_api, sample_webhook):
    receiver = WebhookReceiver()
    
    # Processar webhook
    processing_result = receiver.process_webhook(sample_webhook)
    assert processing_result['processed'] is True
    assert processing_result['status'] == 'success'
    assert processing_result['processing_time'] > 0
    
    # Verificar processamento por tipo de evento
    event_processing = receiver.process_by_event_type('payment.completed', sample_webhook['data'])
    assert event_processing['handled'] is True

# 4. Teste de retry
def test_retry_mechanism(webhooks_api, sample_webhook):
    retry_manager = RetryManager()
    
    # Configurar retry
    retry_config = retry_manager.configure_retry({
        'max_attempts': 3,
        'delay_seconds': 5,
        'backoff_multiplier': 2
    })
    assert retry_config['max_attempts'] == 3
    
    # Simular falha e retry
    failed_webhook = sample_webhook.copy()
    failed_webhook['event_type'] = 'payment.failed'
    
    retry_result = retry_manager.retry_webhook(failed_webhook)
    assert retry_result['retry_count'] > 0
    assert retry_result['next_retry'] is not None

# 5. Teste de casos edge
def test_edge_cases(webhooks_api):
    receiver = WebhookReceiver()
    
    # Teste com webhook vazio
    empty_webhook = {}
    with pytest.raises(ValueError):
        receiver.receive_webhook(empty_webhook)
    
    # Teste com assinatura ausente
    no_signature_webhook = {
        'event_type': 'payment.completed',
        'data': {'payment_id': 'pay_123'}
    }
    with pytest.raises(ValueError):
        receiver.receive_webhook(no_signature_webhook)
    
    # Teste com evento desconhecido
    unknown_event_webhook = {
        'event_type': 'unknown.event',
        'data': {},
        'signature': 'sha256=abc123'
    }
    processing_result = receiver.process_webhook(unknown_event_webhook)
    assert processing_result['status'] == 'ignored'

# 6. Teste de performance
def test_webhook_performance(webhooks_api, sample_webhook, benchmark):
    receiver = WebhookReceiver()
    
    def receive_webhook_operation():
        return receiver.receive_webhook(sample_webhook)
    
    benchmark(receive_webhook_operation)

# 7. Teste de integração
def test_integration_with_external_services(webhooks_api, sample_webhook):
    receiver = WebhookReceiver()
    
    # Integração com serviço de notificação
    with patch('myapp.services.notification.NotificationService') as mock_notification:
        mock_notification.return_value.send.return_value = {'sent': True}
        
        result = receiver.process_webhook_with_notification(sample_webhook)
        assert result['notification_sent'] is True

# 8. Teste de segurança
def test_security_checks(webhooks_api, sample_webhook):
    receiver = WebhookReceiver()
    
    # Verificar rate limiting
    rate_limit_check = receiver.check_rate_limit('192.168.1.1')
    assert rate_limit_check['allowed'] in [True, False]
    assert 'remaining_requests' in rate_limit_check
    
    # Verificar IP whitelist
    ip_check = receiver.check_ip_whitelist('192.168.1.1')
    assert ip_check['allowed'] in [True, False]
    
    # Verificar tamanho do payload
    size_check = receiver.validate_payload_size(sample_webhook)
    assert size_check['valid'] is True
    assert 'size_bytes' in size_check

# 9. Teste de logs
def test_logging_functionality(webhooks_api, sample_webhook, caplog):
    receiver = WebhookReceiver()
    
    with caplog.at_level('INFO'):
        receiver.receive_webhook(sample_webhook)
    
    assert any('Webhook received' in m for m in caplog.messages)
    assert any('payment.completed' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            receiver.receive_webhook({})
        except:
            pass
    
    assert any('Invalid webhook data' in m for m in caplog.messages)

# 10. Teste de métricas
def test_metrics_monitoring(webhooks_api, sample_webhook):
    receiver = WebhookReceiver()
    
    # Monitorar volume de webhooks
    volume_metrics = receiver.monitor_webhook_volume('2024-01-01', '2024-01-31')
    assert 'total_webhooks' in volume_metrics
    assert 'webhooks_per_hour' in volume_metrics
    assert 'event_type_distribution' in volume_metrics
    
    # Monitorar performance do processamento
    performance_metrics = receiver.monitor_processing_performance()
    assert 'avg_processing_time' in performance_metrics
    assert 'success_rate' in performance_metrics
    assert 'error_rate' in performance_metrics 