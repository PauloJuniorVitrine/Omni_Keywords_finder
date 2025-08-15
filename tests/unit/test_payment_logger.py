"""
Testes Unitários para Payment Logger
Utilitário de Logs de Segurança para Pagamentos - Omni Keywords Finder

Prompt: Implementação de testes unitários para logger de pagamentos
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

from backend.app.utils.payment_logger import PaymentSecurityLogger, payment_security_logger


class TestPaymentSecurityLogger:
    """Testes para PaymentSecurityLogger"""
    
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
    def payment_logger(self, temp_log_file):
        """Instância do PaymentSecurityLogger para testes"""
        with patch('backend.app.utils.payment_logger.logging.FileHandler') as mock_handler:
            mock_handler.return_value = Mock()
            
            logger = PaymentSecurityLogger()
            logger.logger = Mock()
            
            return logger
    
    def test_payment_logger_initialization(self, payment_logger):
        """Testa inicialização do PaymentSecurityLogger"""
        assert payment_logger.logger is not None
        assert isinstance(payment_logger.logger, Mock)
    
    def test_setup_logger(self, payment_logger):
        """Testa configuração do logger"""
        with patch('backend.app.utils.payment_logger.logging.FileHandler') as mock_handler:
            with patch('backend.app.utils.payment_logger.logging.Formatter') as mock_formatter:
                mock_handler.return_value = Mock()
                mock_formatter.return_value = Mock()
                
                payment_logger.setup_logger()
                
                # Verificar se o handler foi adicionado
                payment_logger.logger.addHandler.assert_called_once()
                payment_logger.logger.setLevel.assert_called_once_with(logging.INFO)
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_payment_creation(self, mock_log_event, payment_logger):
        """Testa log de criação de pagamento"""
        payment_data = {
            'id': 'pay_123456',
            'amount': 5000,  # R$ 50,00
            'currency': 'brl',
            'payment_method': 'card'
        }
        
        payment_logger.log_payment_creation(
            payment_data=payment_data,
            user_id='user_123',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.info.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'info', 'PaymentSecurity',
            detalhes='Pagamento criado: pay_123456 - Usuário: user_123'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.info.call_args[0][0]
        assert 'PAYMENT_CREATION:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('PAYMENT_CREATION: ')[1])
        assert log_data['event_type'] == 'payment_creation'
        assert log_data['user_id'] == 'user_123'
        assert log_data['payment_id'] == 'pay_123456'
        assert log_data['amount'] == 5000
        assert log_data['currency'] == 'brl'
        assert log_data['payment_method'] == 'card'
        assert log_data['ip_address'] == '192.168.1.1'
        assert log_data['status'] == 'initiated'
        assert 'risk_score' in log_data
        assert 'user_agent_hash' in log_data
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_payment_success(self, mock_log_event, payment_logger):
        """Testa log de pagamento bem-sucedido"""
        payment_logger.log_payment_success(
            payment_id='pay_123456',
            user_id='user_123',
            amount=5000,
            currency='brl',
            payment_method='card'
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.info.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'success', 'PaymentSecurity',
            detalhes='Pagamento confirmado: pay_123456 - Valor: 50.0 BRL'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.info.call_args[0][0]
        assert 'PAYMENT_SUCCESS:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('PAYMENT_SUCCESS: ')[1])
        assert log_data['event_type'] == 'payment_success'
        assert log_data['user_id'] == 'user_123'
        assert log_data['payment_id'] == 'pay_123456'
        assert log_data['amount'] == 5000
        assert log_data['currency'] == 'brl'
        assert log_data['payment_method'] == 'card'
        assert log_data['status'] == 'succeeded'
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_payment_failure(self, mock_log_event, payment_logger):
        """Testa log de falha de pagamento"""
        payment_logger.log_payment_failure(
            payment_id='pay_123456',
            user_id='user_123',
            error_code='card_declined',
            error_message='Cartão recusado',
            payment_method='card'
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.warning.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'warning', 'PaymentSecurity',
            detalhes='Pagamento falhou: pay_123456 - Erro: card_declined'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.warning.call_args[0][0]
        assert 'PAYMENT_FAILURE:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('PAYMENT_FAILURE: ')[1])
        assert log_data['event_type'] == 'payment_failure'
        assert log_data['user_id'] == 'user_123'
        assert log_data['payment_id'] == 'pay_123456'
        assert log_data['error_code'] == 'card_declined'
        assert log_data['error_message'] == 'Cartão recusado'
        assert log_data['payment_method'] == 'card'
        assert log_data['status'] == 'failed'
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_payment_dispute(self, mock_log_event, payment_logger):
        """Testa log de disputa de pagamento"""
        payment_logger.log_payment_dispute(
            payment_id='pay_123456',
            user_id='user_123',
            dispute_reason='fraudulent_charge',
            dispute_amount=5000
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.warning.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'warning', 'PaymentSecurity',
            detalhes='Disputa criada: pay_123456 - Motivo: fraudulent_charge'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.warning.call_args[0][0]
        assert 'PAYMENT_DISPUTE:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('PAYMENT_DISPUTE: ')[1])
        assert log_data['event_type'] == 'payment_dispute'
        assert log_data['user_id'] == 'user_123'
        assert log_data['payment_id'] == 'pay_123456'
        assert log_data['dispute_reason'] == 'fraudulent_charge'
        assert log_data['dispute_amount'] == 5000
        assert log_data['status'] == 'disputed'
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_suspicious_activity(self, mock_log_event, payment_logger):
        """Testa log de atividade suspeita"""
        details = {
            'multiple_failed_attempts': 5,
            'unusual_amount': 100000
        }
        
        payment_logger.log_suspicious_activity(
            user_id='user_123',
            activity_type='multiple_failed_payments',
            details=details,
            risk_score=75
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.warning.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'warning', 'PaymentSecurity',
            detalhes='Atividade suspeita: multiple_failed_payments - Usuário: user_123'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.warning.call_args[0][0]
        assert 'SUSPICIOUS_ACTIVITY:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('SUSPICIOUS_ACTIVITY: ')[1])
        assert log_data['event_type'] == 'suspicious_activity'
        assert log_data['user_id'] == 'user_123'
        assert log_data['activity_type'] == 'multiple_failed_payments'
        assert log_data['details'] == details
        assert log_data['risk_score'] == 75
        assert log_data['status'] == 'suspicious'
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_webhook_event(self, mock_log_event, payment_logger):
        """Testa log de evento de webhook"""
        payment_logger.log_webhook_event(
            event_type='payment.succeeded',
            event_id='evt_123456',
            payment_id='pay_123456',
            ip_address='192.168.1.1',
            signature_valid=True
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.info.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'info', 'PaymentSecurity',
            detalhes='Webhook recebido: payment.succeeded - Pagamento: pay_123456'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.info.call_args[0][0]
        assert 'WEBHOOK_EVENT:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('WEBHOOK_EVENT: ')[1])
        assert log_data['event_type'] == 'webhook_event'
        assert log_data['webhook_event_type'] == 'payment.succeeded'
        assert log_data['webhook_event_id'] == 'evt_123456'
        assert log_data['payment_id'] == 'pay_123456'
        assert log_data['ip_address'] == '192.168.1.1'
        assert log_data['signature_valid'] is True
        assert log_data['status'] == 'received'
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_validation_error(self, mock_log_event, payment_logger):
        """Testa log de erro de validação"""
        payment_logger.log_validation_error(
            user_id='user_123',
            error_type='invalid_card_number',
            field_name='card_number',
            error_message='Número de cartão inválido',
            ip_address='192.168.1.1'
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.warning.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'warning', 'PaymentSecurity',
            detalhes='Erro de validação: invalid_card_number - Campo: card_number'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.warning.call_args[0][0]
        assert 'VALIDATION_ERROR:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('VALIDATION_ERROR: ')[1])
        assert log_data['event_type'] == 'validation_error'
        assert log_data['user_id'] == 'user_123'
        assert log_data['error_type'] == 'invalid_card_number'
        assert log_data['field_name'] == 'card_number'
        assert log_data['error_message'] == 'Número de cartão inválido'
        assert log_data['ip_address'] == '192.168.1.1'
        assert log_data['status'] == 'validation_failed'
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_rate_limit_exceeded(self, mock_log_event, payment_logger):
        """Testa log de exceder limite de taxa"""
        payment_logger.log_rate_limit_exceeded(
            user_id='user_123',
            ip_address='192.168.1.1',
            endpoint='/api/payments',
            limit=100
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.warning.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'warning', 'PaymentSecurity',
            detalhes='Rate limit excedido: /api/payments - Usuário: user_123'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.warning.call_args[0][0]
        assert 'RATE_LIMIT_EXCEEDED:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('RATE_LIMIT_EXCEEDED: ')[1])
        assert log_data['event_type'] == 'rate_limit_exceeded'
        assert log_data['user_id'] == 'user_123'
        assert log_data['ip_address'] == '192.168.1.1'
        assert log_data['endpoint'] == '/api/payments'
        assert log_data['limit'] == 100
        assert log_data['status'] == 'rate_limited'
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_log_unauthorized_access(self, mock_log_event, payment_logger):
        """Testa log de acesso não autorizado"""
        payment_logger.log_unauthorized_access(
            ip_address='192.168.1.1',
            endpoint='/api/payments',
            user_agent='curl/7.68.0',
            reason='Invalid API key'
        )
        
        # Verificar se o logger foi chamado
        payment_logger.logger.warning.assert_called_once()
        
        # Verificar se log_event foi chamado
        mock_log_event.assert_called_once_with(
            'warning', 'PaymentSecurity',
            detalhes='Acesso não autorizado: /api/payments - IP: 192.168.1.1'
        )
        
        # Verificar conteúdo do log
        log_call = payment_logger.logger.warning.call_args[0][0]
        assert 'UNAUTHORIZED_ACCESS:' in log_call
        
        # Verificar se os dados estão no log
        log_data = json.loads(log_call.split('UNAUTHORIZED_ACCESS: ')[1])
        assert log_data['event_type'] == 'unauthorized_access'
        assert log_data['ip_address'] == '192.168.1.1'
        assert log_data['endpoint'] == '/api/payments'
        assert 'user_agent_hash' in log_data
        assert log_data['reason'] == 'Invalid API key'
        assert log_data['status'] == 'denied'
    
    def test_calculate_risk_score_low_amount(self, payment_logger):
        """Testa cálculo de score de risco para valor baixo"""
        payment_data = {
            'amount': 1000,  # R$ 10,00
            'payment_method': 'pix'
        }
        
        score = payment_logger._calculate_risk_score(payment_data, '192.168.1.2')
        
        assert score == 2  # Apenas score do método PIX
    
    def test_calculate_risk_score_medium_amount(self, payment_logger):
        """Testa cálculo de score de risco para valor médio"""
        payment_data = {
            'amount': 50000,  # R$ 500,00
            'payment_method': 'card'
        }
        
        score = payment_logger._calculate_risk_score(payment_data, '192.168.1.2')
        
        assert score == 15  # 10 (valor médio) + 5 (cartão)
    
    def test_calculate_risk_score_high_amount(self, payment_logger):
        """Testa cálculo de score de risco para valor alto"""
        payment_data = {
            'amount': 150000,  # R$ 1500,00
            'payment_method': 'card'
        }
        
        score = payment_logger._calculate_risk_score(payment_data, '192.168.1.2')
        
        assert score == 25  # 20 (valor alto) + 5 (cartão)
    
    def test_calculate_risk_score_risky_ip(self, payment_logger):
        """Testa cálculo de score de risco com IP suspeito"""
        payment_data = {
            'amount': 1000,
            'payment_method': 'pix'
        }
        
        score = payment_logger._calculate_risk_score(payment_data, '192.168.1.1')
        
        assert score == 32  # 2 (PIX) + 30 (IP suspeito)
    
    def test_calculate_risk_score_maximum(self, payment_logger):
        """Testa que o score de risco não excede o máximo"""
        payment_data = {
            'amount': 200000,  # R$ 2000,00
            'payment_method': 'card'
        }
        
        score = payment_logger._calculate_risk_score(payment_data, '192.168.1.1')
        
        assert score == 100  # Máximo definido no código
    
    def test_get_payment_audit_trail(self, payment_logger):
        """Testa obtenção de trilha de auditoria"""
        audit_trail = payment_logger.get_payment_audit_trail('pay_123456')
        
        assert isinstance(audit_trail, list)
        assert len(audit_trail) == 1
        
        event = audit_trail[0]
        assert event['event_type'] == 'payment_creation'
        assert event['payment_id'] == 'pay_123456'
        assert event['status'] == 'initiated'
        assert 'timestamp' in event
    
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_export_security_logs(self, mock_json_dump, mock_open, payment_logger):
        """Testa exportação de logs de segurança"""
        start_date = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = payment_logger.export_security_logs(start_date, end_date)
        
        # Verificar se o arquivo foi criado
        expected_filename = 'payment_security_logs_20250101_20250131.json'
        assert result == f'logs/exports/{expected_filename}'
        
        # Verificar se json.dump foi chamado
        mock_json_dump.assert_called_once()
        
        # Verificar estrutura dos dados exportados
        export_data = mock_json_dump.call_args[0][0]
        assert 'export_info' in export_data
        assert 'events' in export_data
        assert export_data['export_info']['start_date'] == start_date.isoformat()
        assert export_data['export_info']['end_date'] == end_date.isoformat()
        assert 'exported_at' in export_data['export_info']
        assert export_data['export_info']['total_events'] == 0


class TestPaymentSecurityLoggerIntegration:
    """Testes de integração para PaymentSecurityLogger"""
    
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
    def payment_logger(self, temp_log_file):
        """Instância do PaymentSecurityLogger para testes"""
        with patch('backend.app.utils.payment_logger.logging.FileHandler') as mock_handler:
            mock_handler.return_value = Mock()
            
            logger = PaymentSecurityLogger()
            logger.logger = Mock()
            
            return logger
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_complete_payment_lifecycle_logging(self, mock_log_event, payment_logger):
        """Testa logging completo do ciclo de vida de um pagamento"""
        payment_data = {
            'id': 'pay_123456',
            'amount': 5000,
            'currency': 'brl',
            'payment_method': 'card'
        }
        
        # Criar pagamento
        payment_logger.log_payment_creation(
            payment_data=payment_data,
            user_id='user_123',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        
        # Pagamento bem-sucedido
        payment_logger.log_payment_success(
            payment_id='pay_123456',
            user_id='user_123',
            amount=5000,
            currency='brl',
            payment_method='card'
        )
        
        # Webhook de confirmação
        payment_logger.log_webhook_event(
            event_type='payment.succeeded',
            event_id='evt_123456',
            payment_id='pay_123456',
            ip_address='192.168.1.1',
            signature_valid=True
        )
        
        # Verificar se todos os logs foram registrados
        assert payment_logger.logger.info.call_count == 2  # creation + success
        assert payment_logger.logger.info.call_count == 2  # webhook
        
        # Verificar se log_event foi chamado 3 vezes
        assert mock_log_event.call_count == 3
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_security_incident_logging(self, mock_log_event, payment_logger):
        """Testa logging de incidentes de segurança"""
        # Múltiplas tentativas falhadas
        for i in range(3):
            payment_logger.log_payment_failure(
                payment_id=f'pay_123456_{i}',
                user_id='user_123',
                error_code='card_declined',
                error_message='Cartão recusado',
                payment_method='card'
            )
        
        # Atividade suspeita
        payment_logger.log_suspicious_activity(
            user_id='user_123',
            activity_type='multiple_failed_payments',
            details={'attempts': 3},
            risk_score=75
        )
        
        # Rate limit excedido
        payment_logger.log_rate_limit_exceeded(
            user_id='user_123',
            ip_address='192.168.1.1',
            endpoint='/api/payments',
            limit=100
        )
        
        # Verificar se todos os logs de segurança foram registrados
        assert payment_logger.logger.warning.call_count == 5  # 3 failures + suspicious + rate limit
        
        # Verificar se log_event foi chamado 5 vezes
        assert mock_log_event.call_count == 5


class TestPaymentSecurityLoggerErrorHandling:
    """Testes de tratamento de erros para PaymentSecurityLogger"""
    
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
    def payment_logger(self, temp_log_file):
        """Instância do PaymentSecurityLogger para testes"""
        with patch('backend.app.utils.payment_logger.logging.FileHandler') as mock_handler:
            mock_handler.return_value = Mock()
            
            logger = PaymentSecurityLogger()
            logger.logger = Mock()
            
            return logger
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_logging_with_invalid_data(self, mock_log_event, payment_logger):
        """Testa logging com dados inválidos"""
        # Testar com dados None
        payment_logger.log_payment_creation(
            payment_data={},
            user_id=None,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        
        # Deve funcionar sem erro
        payment_logger.logger.info.assert_called_once()
        mock_log_event.assert_called_once()


class TestPaymentSecurityLoggerPerformance:
    """Testes de performance para PaymentSecurityLogger"""
    
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
    def payment_logger(self, temp_log_file):
        """Instância do PaymentSecurityLogger para testes"""
        with patch('backend.app.utils.payment_logger.logging.FileHandler') as mock_handler:
            mock_handler.return_value = Mock()
            
            logger = PaymentSecurityLogger()
            logger.logger = Mock()
            
            return logger
    
    @patch('backend.app.utils.payment_logger.log_event')
    def test_multiple_payment_logs_performance(self, mock_log_event, payment_logger):
        """Testa performance de múltiplos logs de pagamento"""
        import time
        
        start_time = time.time()
        
        # Criar múltiplos logs de pagamento
        for i in range(1000):
            payment_data = {
                'id': f'pay_{i}',
                'amount': 1000 + i,
                'currency': 'brl',
                'payment_method': 'card'
            }
            
            payment_logger.log_payment_creation(
                payment_data=payment_data,
                user_id=f'user_{i}',
                ip_address=f'192.168.1.{i % 256}',
                user_agent='Mozilla/5.0'
            )
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 10.0  # Menos de 10 segundos para 1000 logs
        
        # Verificar se todos os logs foram registrados
        assert payment_logger.logger.info.call_count == 1000
        assert mock_log_event.call_count == 1000


class TestGlobalPaymentSecurityLogger:
    """Testes para instância global do PaymentSecurityLogger"""
    
    def test_global_payment_security_logger(self):
        """Testa instância global do PaymentSecurityLogger"""
        assert payment_security_logger is not None
        assert isinstance(payment_security_logger, PaymentSecurityLogger)


if __name__ == "__main__":
    pytest.main([__file__]) 