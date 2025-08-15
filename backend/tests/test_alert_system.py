"""
Testes Unitários - Sistema de Alertas
Testa sistema de alertas em tempo real

Prompt: Implementação de testes para sistema de alertas
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

# Importar sistema de alertas
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.utils.alert_system import (
    AlertSystem, AlertRule, AlertEvent, AlertSeverity, AlertType,
    EmailChannel, SlackChannel, NotificationChannel
)

class TestAlertSystem:
    """Testes para o sistema de alertas"""
    
    @pytest.fixture
    def config(self):
        """Configuração de teste"""
        return {
            'enabled': True,
            'email': {
                'enabled': True,
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'username': 'test@example.com',
                'password': 'password',
                'from_email': 'alerts@example.com',
                'to_emails': ['admin@example.com'],
                'use_tls': True
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/test',
                'channel': '#alerts',
                'username': 'Test Bot'
            }
        }
    
    @pytest.fixture
    def alert_system(self, config):
        """Cria instância do sistema de alertas"""
        with patch('smtplib.SMTP'), patch('requests.post'):
            system = AlertSystem(config)
            yield system
            # Cleanup
            system.alert_history.clear()
            system.cooldowns.clear()
    
    def test_alert_system_initialization(self, config):
        """Testa inicialização do sistema de alertas"""
        with patch('smtplib.SMTP'), patch('requests.post'):
            system = AlertSystem(config)
            
            assert system.enabled == True
            assert len(system.rules) > 0
            assert 'email' in system.channels
            assert 'slack' in system.channels
    
    def test_load_default_rules(self, alert_system):
        """Testa carregamento das regras padrão"""
        rule_ids = [rule.id for rule in alert_system.rules]
        
        expected_rules = [
            'security_unauthorized_access',
            'security_suspicious_activity',
            'performance_high_error_rate',
            'business_payment_failure',
            'system_database_error'
        ]
        
        for expected_rule in expected_rules:
            assert expected_rule in rule_ids
    
    def test_rule_matching_unauthorized_access(self, alert_system):
        """Testa matching de regra de acesso não autorizado"""
        event_data = {
            'event_type': 'unauthorized_access',
            'user_id': 'test_user',
            'ip_address': '192.168.1.1',
            'source': 'api'
        }
        
        # Primeira tentativa - não deve gerar alerta (threshold = 3)
        alert = alert_system.check_event(event_data)
        assert alert is None
        
        # Segunda tentativa - não deve gerar alerta
        alert = alert_system.check_event(event_data)
        assert alert is None
        
        # Terceira tentativa - deve gerar alerta
        alert = alert_system.check_event(event_data)
        assert alert is not None
        assert alert.rule_id == 'security_unauthorized_access'
        assert alert.severity == AlertSeverity.HIGH
        assert alert.alert_type == AlertType.SECURITY
    
    def test_rule_matching_suspicious_activity(self, alert_system):
        """Testa matching de regra de atividade suspeita"""
        event_data = {
            'event_type': 'suspicious_activity',
            'user_id': 'test_user',
            'ip_address': '192.168.1.1',
            'source': 'api'
        }
        
        # Deve gerar alerta imediatamente (threshold = 1)
        alert = alert_system.check_event(event_data)
        assert alert is not None
        assert alert.rule_id == 'security_suspicious_activity'
        assert alert.severity == AlertSeverity.MEDIUM
    
    def test_rule_matching_payment_failure(self, alert_system):
        """Testa matching de regra de falha de pagamento"""
        event_data = {
            'event_type': 'payment_failed',
            'user_id': 'test_user',
            'amount': 100.00,
            'source': 'payment_gateway'
        }
        
        # Deve gerar alerta imediatamente
        alert = alert_system.check_event(event_data)
        assert alert is not None
        assert alert.rule_id == 'business_payment_failure'
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.alert_type == AlertType.BUSINESS
    
    def test_cooldown_mechanism(self, alert_system):
        """Testa mecanismo de cooldown"""
        event_data = {
            'event_type': 'suspicious_activity',
            'user_id': 'test_user',
            'source': 'api'
        }
        
        # Primeiro alerta
        alert1 = alert_system.check_event(event_data)
        assert alert1 is not None
        
        # Segundo alerta imediatamente - deve estar em cooldown
        alert2 = alert_system.check_event(event_data)
        assert alert2 is None
        
        # Verificar que cooldown foi registrado
        assert 'security_suspicious_activity' in alert_system.cooldowns
    
    def test_alert_message_creation(self, alert_system):
        """Testa criação de mensagens de alerta"""
        rule = alert_system._get_rule('security_unauthorized_access')
        event_data = {
            'event_type': 'unauthorized_access',
            'user_id': 'test_user',
            'ip_address': '192.168.1.1'
        }
        
        message = alert_system._create_alert_message(rule, event_data)
        assert 'tentativas de acesso não autorizado' in message
    
    def test_alert_statistics(self, alert_system):
        """Testa estatísticas de alertas"""
        # Gerar alguns alertas
        event_data = {
            'event_type': 'suspicious_activity',
            'user_id': 'test_user',
            'source': 'api'
        }
        
        for _ in range(3):
            alert_system.check_event(event_data)
        
        # Aguardar processamento
        time.sleep(0.1)
        
        stats = alert_system.get_alert_statistics()
        
        assert stats['total_alerts'] >= 3
        assert stats['alerts_24h'] >= 3
        assert 'medium' in stats['by_severity']
        assert 'security' in stats['by_type']
        assert 'security_suspicious_activity' in stats['by_rule']
    
    def test_rule_management(self, alert_system):
        """Testa gerenciamento de regras"""
        # Desabilitar regra
        alert_system.disable_rule('security_suspicious_activity')
        rule = alert_system._get_rule('security_suspicious_activity')
        assert not rule.enabled
        
        # Habilitar regra
        alert_system.enable_rule('security_suspicious_activity')
        rule = alert_system._get_rule('security_suspicious_activity')
        assert rule.enabled
        
        # Adicionar nova regra
        new_rule = AlertRule(
            id='test_rule',
            name='Test Rule',
            description='Test rule for testing',
            alert_type=AlertType.SYSTEM,
            severity=AlertSeverity.LOW,
            conditions={'event_type': 'test_event'}
        )
        
        alert_system.add_rule(new_rule)
        assert alert_system._get_rule('test_rule') is not None
        
        # Remover regra
        alert_system.remove_rule('test_rule')
        assert alert_system._get_rule('test_rule') is None
    
    def test_alert_history_management(self, alert_system):
        """Testa gerenciamento do histórico de alertas"""
        # Gerar muitos alertas
        event_data = {
            'event_type': 'suspicious_activity',
            'user_id': 'test_user',
            'source': 'api'
        }
        
        for _ in range(1100):  # Mais que o limite de 1000
            alert_system.check_event(event_data)
        
        # Aguardar processamento
        time.sleep(0.1)
        
        # Verificar que histórico foi limitado
        assert len(alert_system.alert_history) <= 1000
        
        # Testar obtenção de histórico limitado
        history = alert_system.get_alert_history(limit=50)
        assert len(history) <= 50

class TestEmailChannel:
    """Testes para canal de email"""
    
    @pytest.fixture
    def email_config(self):
        """Configuração de email"""
        return {
            'name': 'email',
            'smtp_server': 'localhost',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'password',
            'from_email': 'alerts@example.com',
            'to_emails': ['admin@example.com'],
            'use_tls': True
        }
    
    @pytest.fixture
    def email_channel(self, email_config):
        """Cria instância do canal de email"""
        return EmailChannel(email_config)
    
    @pytest.fixture
    def test_alert(self):
        """Cria alerta de teste"""
        return AlertEvent(
            id='test-alert-123',
            rule_id='security_unauthorized_access',
            timestamp=datetime.now(timezone.utc),
            severity=AlertSeverity.HIGH,
            alert_type=AlertType.SECURITY,
            message='Test alert message',
            details={'test': 'data'},
            source='test',
            user_id='test_user',
            ip_address='192.168.1.1'
        )
    
    def test_email_channel_initialization(self, email_config):
        """Testa inicialização do canal de email"""
        channel = EmailChannel(email_config)
        
        assert channel.name == 'email'
        assert channel.smtp_server == 'localhost'
        assert channel.smtp_port == 587
        assert channel.username == 'test@example.com'
        assert channel.from_email == 'alerts@example.com'
        assert 'admin@example.com' in channel.to_emails
    
    @patch('smtplib.SMTP')
    def test_email_send_success(self, mock_smtp, email_channel, test_alert):
        """Testa envio de email com sucesso"""
        # Configurar mock
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Enviar alerta
        result = email_channel.send(test_alert)
        
        assert result == True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_email_send_failure(self, mock_smtp, email_channel, test_alert):
        """Testa falha no envio de email"""
        # Configurar mock para falhar
        mock_smtp.side_effect = Exception("SMTP error")
        
        # Enviar alerta
        result = email_channel.send(test_alert)
        
        assert result == False
    
    def test_email_body_creation(self, email_channel, test_alert):
        """Testa criação do corpo do email"""
        body = email_channel._create_email_body(test_alert)
        
        # Verificar elementos HTML
        assert '<html>' in body
        assert '<h2>🚨 Alerta de Segurança</h2>' in body
        assert 'Test alert message' in body
        assert 'test_user' in body
        assert '192.168.1.1' in body
        assert 'security' in body.lower()
        assert 'high' in body.lower()

class TestSlackChannel:
    """Testes para canal do Slack"""
    
    @pytest.fixture
    def slack_config(self):
        """Configuração do Slack"""
        return {
            'name': 'slack',
            'webhook_url': 'https://hooks.slack.com/test',
            'channel': '#alerts',
            'username': 'Test Bot'
        }
    
    @pytest.fixture
    def slack_channel(self, slack_config):
        """Cria instância do canal do Slack"""
        return SlackChannel(slack_config)
    
    @pytest.fixture
    def test_alert(self):
        """Cria alerta de teste"""
        return AlertEvent(
            id='test-alert-123',
            rule_id='security_unauthorized_access',
            timestamp=datetime.now(timezone.utc),
            severity=AlertSeverity.HIGH,
            alert_type=AlertType.SECURITY,
            message='Test alert message',
            details={'test': 'data'},
            source='test',
            user_id='test_user',
            ip_address='192.168.1.1'
        )
    
    def test_slack_channel_initialization(self, slack_config):
        """Testa inicialização do canal do Slack"""
        channel = SlackChannel(slack_config)
        
        assert channel.name == 'slack'
        assert channel.webhook_url == 'https://hooks.slack.com/test'
        assert channel.channel == '#alerts'
        assert channel.username == 'Test Bot'
    
    @patch('requests.post')
    def test_slack_send_success(self, mock_post, slack_channel, test_alert):
        """Testa envio para Slack com sucesso"""
        # Configurar mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Enviar alerta
        result = slack_channel.send(test_alert)
        
        assert result == True
        mock_post.assert_called_once()
        
        # Verificar payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['channel'] == '#alerts'
        assert payload['username'] == 'Test Bot'
        assert len(payload['attachments']) == 1
        assert '🚨 Alerta de Segurança' in payload['attachments'][0]['title']
    
    @patch('requests.post')
    def test_slack_send_failure(self, mock_post, slack_channel, test_alert):
        """Testa falha no envio para Slack"""
        # Configurar mock para falhar
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        # Enviar alerta
        result = slack_channel.send(test_alert)
        
        assert result == False
    
    @patch('requests.post')
    def test_slack_send_exception(self, mock_post, slack_channel, test_alert):
        """Testa exceção no envio para Slack"""
        # Configurar mock para gerar exceção
        mock_post.side_effect = Exception("Network error")
        
        # Enviar alerta
        result = slack_channel.send(test_alert)
        
        assert result == False
    
    def test_slack_payload_creation(self, slack_channel, test_alert):
        """Testa criação do payload do Slack"""
        payload = slack_channel._create_slack_payload(test_alert)
        
        assert payload['channel'] == '#alerts'
        assert payload['username'] == 'Test Bot'
        assert len(payload['attachments']) == 1
        
        attachment = payload['attachments'][0]
        assert '🚨 Alerta de Segurança' in attachment['title']
        assert 'Test alert message' in attachment['text']
        assert attachment['color'] == '#dc3545'  # Vermelho para HIGH
        assert len(attachment['fields']) >= 3  # Tipo, Severidade, Fonte

class TestAlertRule:
    """Testes para regras de alerta"""
    
    def test_alert_rule_creation(self):
        """Testa criação de regra de alerta"""
        rule = AlertRule(
            id='test_rule',
            name='Test Rule',
            description='Test rule description',
            alert_type=AlertType.SECURITY,
            severity=AlertSeverity.HIGH,
            conditions={'event_type': 'test_event'},
            enabled=True,
            cooldown_minutes=10,
            channels=['email', 'slack']
        )
        
        assert rule.id == 'test_rule'
        assert rule.name == 'Test Rule'
        assert rule.alert_type == AlertType.SECURITY
        assert rule.severity == AlertSeverity.HIGH
        assert rule.enabled == True
        assert rule.cooldown_minutes == 10
        assert 'email' in rule.channels
        assert 'slack' in rule.channels
    
    def test_alert_rule_defaults(self):
        """Testa valores padrão da regra de alerta"""
        rule = AlertRule(
            id='test_rule',
            name='Test Rule',
            description='Test rule description',
            alert_type=AlertType.SECURITY,
            severity=AlertSeverity.HIGH,
            conditions={'event_type': 'test_event'}
        )
        
        assert rule.enabled == True
        assert rule.cooldown_minutes == 5
        assert rule.channels == ['email']

class TestAlertEvent:
    """Testes para eventos de alerta"""
    
    def test_alert_event_creation(self):
        """Testa criação de evento de alerta"""
        event = AlertEvent(
            id='test-event-123',
            rule_id='test_rule',
            timestamp=datetime.now(timezone.utc),
            severity=AlertSeverity.HIGH,
            alert_type=AlertType.SECURITY,
            message='Test message',
            details={'test': 'data'},
            source='test',
            user_id='test_user',
            ip_address='192.168.1.1',
            request_id='req-123'
        )
        
        assert event.id == 'test-event-123'
        assert event.rule_id == 'test_rule'
        assert event.severity == AlertSeverity.HIGH
        assert event.alert_type == AlertType.SECURITY
        assert event.message == 'Test message'
        assert event.user_id == 'test_user'
        assert event.ip_address == '192.168.1.1'
        assert event.request_id == 'req-123'

if __name__ == '__main__':
    pytest.main([__file__]) 