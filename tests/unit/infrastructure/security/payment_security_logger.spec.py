"""
Testes unitários para logger de segurança de pagamentos
Prompt: Logs de segurança para pagamentos
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""
import pytest
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from backend.app.utils.payment_logger import PaymentSecurityLogger

@pytest.fixture
def payment_logger():
    """Fixture para logger de pagamentos"""
    with patch('backend.app.utils.payment_logger.logging.FileHandler') as mock_handler:
        logger = PaymentSecurityLogger()
        yield logger

@pytest.fixture
def sample_payment_data():
    """Dados de pagamento de exemplo"""
    return {
        'id': 'pi_test_123',
        'amount': 1000,
        'currency': 'brl',
        'payment_method': 'card',
        'status': 'requires_payment_method'
    }

class TestPaymentSecurityLogger:
    """Testes para logger de segurança de pagamentos"""
    
    def test_logger_initialization(self, payment_logger):
        """Testa inicialização do logger"""
        assert payment_logger.logger is not None
        assert payment_logger.logger.name == 'payment_security'
    
    def test_log_payment_creation(self, payment_logger, sample_payment_data):
        """Testa log de criação de pagamento"""
        with patch.object(payment_logger.logger, 'info') as mock_info:
            payment_logger.log_payment_creation(
                payment_data=sample_payment_data,
                user_id='user_123',
                ip_address='192.168.1.1',
                user_agent='Mozilla/5.0'
            )
            
            mock_info.assert_called_once()
            log_message = mock_info.call_args[0][0]
            assert 'PAYMENT_CREATION:' in log_message
            
            # Verificar se JSON é válido
            json_part = log_message.split('PAYMENT_CREATION: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'payment_creation'
            assert log_data['user_id'] == 'user_123'
            assert log_data['payment_id'] == 'pi_test_123'
            assert log_data['amount'] == 1000
            assert log_data['currency'] == 'brl'
            assert log_data['ip_address'] == '192.168.1.1'
            assert 'user_agent_hash' in log_data
            assert 'risk_score' in log_data
    
    def test_log_payment_success(self, payment_logger):
        """Testa log de pagamento bem-sucedido"""
        with patch.object(payment_logger.logger, 'info') as mock_info:
            payment_logger.log_payment_success(
                payment_id='pi_test_123',
                user_id='user_123',
                amount=1000,
                currency='brl',
                payment_method='card'
            )
            
            mock_info.assert_called_once()
            log_message = mock_info.call_args[0][0]
            assert 'PAYMENT_SUCCESS:' in log_message
            
            json_part = log_message.split('PAYMENT_SUCCESS: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'payment_success'
            assert log_data['payment_id'] == 'pi_test_123'
            assert log_data['amount'] == 1000
            assert log_data['status'] == 'succeeded'
    
    def test_log_payment_failure(self, payment_logger):
        """Testa log de falha de pagamento"""
        with patch.object(payment_logger.logger, 'warning') as mock_warning:
            payment_logger.log_payment_failure(
                payment_id='pi_test_123',
                user_id='user_123',
                error_code='card_declined',
                error_message='Cartão recusado',
                payment_method='card'
            )
            
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            assert 'PAYMENT_FAILURE:' in log_message
            
            json_part = log_message.split('PAYMENT_FAILURE: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'payment_failure'
            assert log_data['error_code'] == 'card_declined'
            assert log_data['error_message'] == 'Cartão recusado'
            assert log_data['status'] == 'failed'
    
    def test_log_payment_dispute(self, payment_logger):
        """Testa log de disputa de pagamento"""
        with patch.object(payment_logger.logger, 'warning') as mock_warning:
            payment_logger.log_payment_dispute(
                payment_id='pi_test_123',
                user_id='user_123',
                dispute_reason='fraudulent',
                dispute_amount=1000
            )
            
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            assert 'PAYMENT_DISPUTE:' in log_message
            
            json_part = log_message.split('PAYMENT_DISPUTE: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'payment_dispute'
            assert log_data['dispute_reason'] == 'fraudulent'
            assert log_data['dispute_amount'] == 1000
            assert log_data['status'] == 'disputed'
    
    def test_log_suspicious_activity(self, payment_logger):
        """Testa log de atividade suspeita"""
        with patch.object(payment_logger.logger, 'warning') as mock_warning:
            details = {
                'multiple_failed_attempts': True,
                'unusual_amount': 50000
            }
            
            payment_logger.log_suspicious_activity(
                user_id='user_123',
                activity_type='multiple_failures',
                details=details,
                risk_score=75
            )
            
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            assert 'SUSPICIOUS_ACTIVITY:' in log_message
            
            json_part = log_message.split('SUSPICIOUS_ACTIVITY: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'suspicious_activity'
            assert log_data['activity_type'] == 'multiple_failures'
            assert log_data['risk_score'] == 75
            assert log_data['status'] == 'suspicious'
    
    def test_log_webhook_event(self, payment_logger):
        """Testa log de evento de webhook"""
        with patch.object(payment_logger.logger, 'info') as mock_info:
            payment_logger.log_webhook_event(
                event_type='payment_intent.succeeded',
                event_id='evt_test_123',
                payment_id='pi_test_123',
                ip_address='3.18.12.63',
                signature_valid=True
            )
            
            mock_info.assert_called_once()
            log_message = mock_info.call_args[0][0]
            assert 'WEBHOOK_EVENT:' in log_message
            
            json_part = log_message.split('WEBHOOK_EVENT: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'webhook_event'
            assert log_data['webhook_event_type'] == 'payment_intent.succeeded'
            assert log_data['webhook_event_id'] == 'evt_test_123'
            assert log_data['signature_valid'] is True
    
    def test_log_validation_error(self, payment_logger):
        """Testa log de erro de validação"""
        with patch.object(payment_logger.logger, 'warning') as mock_warning:
            payment_logger.log_validation_error(
                user_id='user_123',
                error_type='invalid_card_number',
                field_name='card.number',
                error_message='Número de cartão inválido',
                ip_address='192.168.1.1'
            )
            
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            assert 'VALIDATION_ERROR:' in log_message
            
            json_part = log_message.split('VALIDATION_ERROR: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'validation_error'
            assert log_data['error_type'] == 'invalid_card_number'
            assert log_data['field_name'] == 'card.number'
            assert log_data['status'] == 'validation_failed'
    
    def test_log_rate_limit_exceeded(self, payment_logger):
        """Testa log de exceder limite de taxa"""
        with patch.object(payment_logger.logger, 'warning') as mock_warning:
            payment_logger.log_rate_limit_exceeded(
                user_id='user_123',
                ip_address='192.168.1.1',
                endpoint='/api/payments/create',
                limit=10
            )
            
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            assert 'RATE_LIMIT_EXCEEDED:' in log_message
            
            json_part = log_message.split('RATE_LIMIT_EXCEEDED: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'rate_limit_exceeded'
            assert log_data['endpoint'] == '/api/payments/create'
            assert log_data['limit'] == 10
            assert log_data['status'] == 'rate_limited'
    
    def test_log_unauthorized_access(self, payment_logger):
        """Testa log de acesso não autorizado"""
        with patch.object(payment_logger.logger, 'warning') as mock_warning:
            payment_logger.log_unauthorized_access(
                ip_address='192.168.1.1',
                endpoint='/api/payments/webhook',
                user_agent='Mozilla/5.0',
                reason='IP não autorizado'
            )
            
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            assert 'UNAUTHORIZED_ACCESS:' in log_message
            
            json_part = log_message.split('UNAUTHORIZED_ACCESS: ')[1]
            log_data = json.loads(json_part)
            
            assert log_data['event_type'] == 'unauthorized_access'
            assert log_data['endpoint'] == '/api/payments/webhook'
            assert log_data['reason'] == 'IP não autorizado'
            assert log_data['status'] == 'denied'
            assert 'user_agent_hash' in log_data
    
    def test_calculate_risk_score_low_amount(self, payment_logger):
        """Testa cálculo de risco para valor baixo"""
        payment_data = {
            'amount': 1000,  # R$ 10
            'payment_method': 'pix'
        }
        
        risk_score = payment_logger._calculate_risk_score(payment_data, '192.168.1.1')
        assert risk_score == 2  # Apenas risco do método PIX
    
    def test_calculate_risk_score_high_amount(self, payment_logger):
        """Testa cálculo de risco para valor alto"""
        payment_data = {
            'amount': 150000,  # R$ 1500
            'payment_method': 'card'
        }
        
        risk_score = payment_logger._calculate_risk_score(payment_data, '192.168.1.1')
        assert risk_score == 25  # 20 (valor alto) + 5 (cartão)
    
    def test_calculate_risk_score_risky_ip(self, payment_logger):
        """Testa cálculo de risco para IP suspeito"""
        payment_data = {
            'amount': 1000,
            'payment_method': 'pix'
        }
        
        risk_score = payment_logger._calculate_risk_score(payment_data, '192.168.1.1')
        assert risk_score == 32  # 2 (PIX) + 30 (IP suspeito)
    
    def test_calculate_risk_score_maximum(self, payment_logger):
        """Testa que score de risco não excede 100"""
        payment_data = {
            'amount': 200000,  # R$ 2000
            'payment_method': 'card'
        }
        
        risk_score = payment_logger._calculate_risk_score(payment_data, '192.168.1.1')
        assert risk_score <= 100
    
    def test_get_payment_audit_trail(self, payment_logger):
        """Testa obtenção de trilha de auditoria"""
        audit_trail = payment_logger.get_payment_audit_trail('pi_test_123')
        
        assert isinstance(audit_trail, list)
        assert len(audit_trail) > 0
        
        event = audit_trail[0]
        assert 'timestamp' in event
        assert 'event_type' in event
        assert 'payment_id' in event
        assert event['payment_id'] == 'pi_test_123'
    
    def test_export_security_logs(self, payment_logger):
        """Testa exportação de logs de segurança"""
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            start_date = datetime(2025, 1, 1)
            end_date = datetime(2025, 1, 31)
            
            result = payment_logger.export_security_logs(start_date, end_date)
            
            assert 'payment_security_logs_20250101_20250131.json' in result
            mock_file.write.assert_called()
            
            # Verificar se JSON é válido
            write_call = mock_file.write.call_args[0][0]
            export_data = json.loads(write_call)
            
            assert 'export_info' in export_data
            assert 'events' in export_data
            assert export_data['export_info']['start_date'] == start_date.isoformat()
            assert export_data['export_info']['end_date'] == end_date.isoformat()
    
    def test_user_agent_hashing(self, payment_logger):
        """Testa que user agent é hasheado corretamente"""
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        with patch.object(payment_logger.logger, 'info') as mock_info:
            payment_logger.log_payment_creation(
                payment_data={'id': 'test'},
                user_id='user_123',
                ip_address='192.168.1.1',
                user_agent=user_agent
            )
            
            log_message = mock_info.call_args[0][0]
            json_part = log_message.split('PAYMENT_CREATION: ')[1]
            log_data = json.loads(json_part)
            
            assert 'user_agent_hash' in log_data
            assert len(log_data['user_agent_hash']) == 16
            assert log_data['user_agent_hash'] != user_agent  # Deve ser diferente do original
    
    def test_timestamp_format(self, payment_logger):
        """Testa formato de timestamp nos logs"""
        with patch.object(payment_logger.logger, 'info') as mock_info:
            payment_logger.log_payment_success(
                payment_id='pi_test_123',
                user_id='user_123',
                amount=1000,
                currency='brl',
                payment_method='card'
            )
            
            log_message = mock_info.call_args[0][0]
            json_part = log_message.split('PAYMENT_SUCCESS: ')[1]
            log_data = json.loads(json_part)
            
            # Verificar se timestamp é ISO format
            timestamp = log_data['timestamp']
            datetime.fromisoformat(timestamp)  # Deve ser válido 