from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Notificações Avançado

Testes abrangentes para validar todas as funcionalidades do sistema
de notificações avançado.

Autor: Sistema de Testes
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from infrastructure.notifications.advanced_notification_system import (
    AdvancedNotificationSystem,
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationTemplate,
    UserPreferences,
    EmailNotifier,
    SlackNotifier,
    DiscordNotifier,
    PushNotifier,
    WebhookNotifier,
    TemplateManager,
    create_notification_system,
    DEFAULT_CONFIG
)

class TestNotificationTypes:
    """Testes para tipos de notificação"""
    
    def test_notification_type_enum(self):
        """Testa enum de tipos de notificação"""
        assert NotificationType.INFO.value == "info"
        assert NotificationType.WARNING.value == "warning"
        assert NotificationType.ERROR.value == "error"
        assert NotificationType.SUCCESS.value == "success"
        assert NotificationType.CRITICAL.value == "critical"
    
    def test_notification_channel_enum(self):
        """Testa enum de canais de notificação"""
        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.SLACK.value == "slack"
        assert NotificationChannel.DISCORD.value == "discord"
        assert NotificationChannel.PUSH.value == "push"
        assert NotificationChannel.IN_APP.value == "in_app"
        assert NotificationChannel.WEBHOOK.value == "webhook"

class TestNotificationDataStructures:
    """Testes para estruturas de dados"""
    
    def test_notification_creation(self):
        """Testa criação de notificação"""
        notification = Notification(
            id="test-123",
            title="Teste",
            message="Mensagem de teste",
            notification_type=NotificationType.INFO,
            user_id="user-123",
            channels=[NotificationChannel.EMAIL],
            priority=1,
            created_at=datetime.utcnow()
        )
        
        assert notification.id == "test-123"
        assert notification.title == "Teste"
        assert notification.message == "Mensagem de teste"
        assert notification.notification_type == NotificationType.INFO
        assert notification.user_id == "user-123"
        assert notification.priority == 1
    
    def test_user_preferences_creation(self):
        """Testa criação de preferências de usuário"""
        prefs = UserPreferences(
            user_id="user-123",
            email_enabled=True,
            slack_enabled=False,
            discord_enabled=True,
            push_enabled=True,
            in_app_enabled=True,
            webhook_enabled=False,
            email_address="test@example.com",
            notification_types=[NotificationType.INFO, NotificationType.ERROR]
        )
        
        assert prefs.user_id == "user-123"
        assert prefs.email_enabled is True
        assert prefs.slack_enabled is False
        assert prefs.email_address == "test@example.com"
        assert len(prefs.notification_types) == 2
    
    def test_notification_template_creation(self):
        """Testa criação de template de notificação"""
        template = NotificationTemplate(
            id="template-123",
            name="Template de Teste",
            subject="Assunto: {nome}",
            body="Olá {nome}, {mensagem}",
            variables=["nome", "mensagem"],
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        assert template.id == "template-123"
        assert template.name == "Template de Teste"
        assert "nome" in template.variables
        assert "mensagem" in template.variables
        assert len(template.channels) == 2

class TestEmailNotifier:
    """Testes para notificador de email"""
    
    @pytest.fixture
    def email_config(self):
        return {
            'smtp_host': 'localhost',
            'smtp_port': 587,
            'smtp_user': 'test@example.com',
            'smtp_password': 'password',
            'from_email': 'noreply@test.com',
            'use_tls': True
        }
    
    @pytest.fixture
    def email_notifier(self, email_config):
        return EmailNotifier(email_config)
    
    @pytest.fixture
    def sample_notification(self):
        return Notification(
            id="test-123",
            title="Teste Email",
            message="Mensagem de teste",
            notification_type=NotificationType.INFO,
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_user_prefs(self):
        return UserPreferences(
            user_id="user-123",
            email_enabled=True,
            email_address="recipient@example.com"
        )
    
    def test_email_notifier_initialization(self, email_config):
        """Testa inicialização do notificador de email"""
        notifier = EmailNotifier(email_config)
        assert notifier.smtp_host == 'localhost'
        assert notifier.smtp_port == 587
        assert notifier.smtp_user == 'test@example.com'
        assert notifier.from_email == 'noreply@test.com'
    
    @patch('smtplib.SMTP')
    def test_send_notification_success(self, mock_smtp, email_notifier, sample_notification, sample_user_prefs):
        """Testa envio bem-sucedido de email"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = email_notifier.send_notification(sample_notification, sample_user_prefs)
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'password')
        mock_server.send_message.assert_called_once()
    
    def test_send_notification_disabled(self, email_notifier, sample_notification):
        """Testa envio com email desabilitado"""
        user_prefs = UserPreferences(user_id="user-123", email_enabled=False)
        result = email_notifier.send_notification(sample_notification, user_prefs)
        assert result is False
    
    def test_send_notification_no_email(self, email_notifier, sample_notification):
        """Testa envio sem endereço de email"""
        user_prefs = UserPreferences(user_id="user-123", email_enabled=True, email_address=None)
        result = email_notifier.send_notification(sample_notification, user_prefs)
        assert result is False
    
    def test_get_color_by_type(self, email_notifier):
        """Testa obtenção de cor por tipo de notificação"""
        colors = {
            NotificationType.INFO: "#4f8cff",
            NotificationType.WARNING: "#eab308",
            NotificationType.ERROR: "#ef4444",
            NotificationType.SUCCESS: "#10b981",
            NotificationType.CRITICAL: "#dc2626"
        }
        
        for notification_type, expected_color in colors.items():
            color = email_notifier._get_color(notification_type)
            assert color == expected_color

class TestSlackNotifier:
    """Testes para notificador do Slack"""
    
    @pytest.fixture
    def slack_config(self):
        return {
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'slack_default_channel': '#general'
        }
    
    @pytest.fixture
    def slack_notifier(self, slack_config):
        return SlackNotifier(slack_config)
    
    @pytest.fixture
    def sample_notification(self):
        return Notification(
            id="test-123",
            title="Teste Slack",
            message="Mensagem de teste",
            notification_type=NotificationType.WARNING,
            priority=2,
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_user_prefs(self):
        return UserPreferences(
            user_id="user-123",
            slack_enabled=True,
            slack_channel="#test-channel"
        )
    
    def test_slack_notifier_initialization(self, slack_config):
        """Testa inicialização do notificador do Slack"""
        notifier = SlackNotifier(slack_config)
        assert notifier.webhook_url == 'https://hooks.slack.com/test'
        assert notifier.default_channel == '#general'
    
    @patch('requests.post')
    def test_send_notification_success(self, mock_post, slack_notifier, sample_notification, sample_user_prefs):
        """Testa envio bem-sucedido para Slack"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = slack_notifier.send_notification(sample_notification, sample_user_prefs)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verificar payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['channel'] == '#test-channel'
        assert payload['text'] == 'Teste Slack'
        assert len(payload['attachments']) == 1
    
    def test_send_notification_disabled(self, slack_notifier, sample_notification):
        """Testa envio com Slack desabilitado"""
        user_prefs = UserPreferences(user_id="user-123", slack_enabled=False)
        result = slack_notifier.send_notification(sample_notification, user_prefs)
        assert result is False
    
    def test_send_notification_no_webhook(self, slack_notifier, sample_notification, sample_user_prefs):
        """Testa envio sem webhook configurado"""
        slack_notifier.webhook_url = None
        result = slack_notifier.send_notification(sample_notification, sample_user_prefs)
        assert result is False

class TestDiscordNotifier:
    """Testes para notificador do Discord"""
    
    @pytest.fixture
    def discord_config(self):
        return {
            'discord_webhook_url': 'https://discord.com/api/webhooks/test'
        }
    
    @pytest.fixture
    def discord_notifier(self, discord_config):
        return DiscordNotifier(discord_config)
    
    @pytest.fixture
    def sample_notification(self):
        return Notification(
            id="test-123",
            title="Teste Discord",
            message="Mensagem de teste",
            notification_type=NotificationType.ERROR,
            priority=3,
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_user_prefs(self):
        return UserPreferences(
            user_id="user-123",
            discord_enabled=True,
            discord_webhook="https://discord.com/api/webhooks/user-test"
        )
    
    def test_discord_notifier_initialization(self, discord_config):
        """Testa inicialização do notificador do Discord"""
        notifier = DiscordNotifier(discord_config)
        assert notifier.webhook_url == 'https://discord.com/api/webhooks/test'
    
    @patch('requests.post')
    def test_send_notification_success(self, mock_post, discord_notifier, sample_notification, sample_user_prefs):
        """Testa envio bem-sucedido para Discord"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = discord_notifier.send_notification(sample_notification, sample_user_prefs)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verificar payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'embeds' in payload
        assert len(payload['embeds']) == 1
        
        embed = payload['embeds'][0]
        assert embed['title'] == 'Teste Discord'
        assert embed['description'] == 'Mensagem de teste'
    
    def test_send_notification_disabled(self, discord_notifier, sample_notification):
        """Testa envio com Discord desabilitado"""
        user_prefs = UserPreferences(user_id="user-123", discord_enabled=False)
        result = discord_notifier.send_notification(sample_notification, user_prefs)
        assert result is False
    
    def test_get_color_int(self, discord_notifier):
        """Testa obtenção de cor como inteiro para Discord"""
        colors = {
            NotificationType.INFO: 0x4f8cff,
            NotificationType.WARNING: 0xeab308,
            NotificationType.ERROR: 0xef4444,
            NotificationType.SUCCESS: 0x10b981,
            NotificationType.CRITICAL: 0xdc2626
        }
        
        for notification_type, expected_color in colors.items():
            color = discord_notifier._get_color_int(notification_type)
            assert color == expected_color

class TestTemplateManager:
    """Testes para gerenciador de templates"""
    
    @pytest.fixture
    def temp_templates_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def template_manager(self, temp_templates_dir):
        return TemplateManager(temp_templates_dir)
    
    @pytest.fixture
    def sample_template(self):
        return NotificationTemplate(
            id="test-template",
            name="Template de Teste",
            subject="Olá {nome}",
            body="Bem-vindo {nome}! {mensagem}",
            variables=["nome", "mensagem"],
            channels=[NotificationChannel.EMAIL],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def test_template_manager_initialization(self, temp_templates_dir):
        """Testa inicialização do gerenciador de templates"""
        manager = TemplateManager(temp_templates_dir)
        assert manager.templates_dir == Path(temp_templates_dir)
        assert len(manager.templates) == 0
    
    def test_create_template(self, template_manager, sample_template):
        """Testa criação de template"""
        result = template_manager.create_template(sample_template)
        assert result is True
        
        # Verificar se arquivo foi criado
        template_file = Path(template_manager.templates_dir) / f"{sample_template.id}.json"
        assert template_file.exists()
        
        # Verificar se template foi carregado
        assert sample_template.id in template_manager.templates
    
    def test_get_template(self, template_manager, sample_template):
        """Testa obtenção de template"""
        template_manager.create_template(sample_template)
        
        retrieved_template = template_manager.get_template(sample_template.id)
        assert retrieved_template is not None
        assert retrieved_template.id == sample_template.id
        assert retrieved_template.name == sample_template.name
    
    def test_apply_template(self, template_manager, sample_template):
        """Testa aplicação de template com variáveis"""
        template_manager.create_template(sample_template)
        
        variables = {
            "nome": "João",
            "mensagem": "Seja bem-vindo ao sistema!"
        }
        
        result = template_manager.apply_template(sample_template.id, variables)
        assert result is not None
        assert result["subject"] == "Olá João"
        assert result["body"] == "Bem-vindo João! Seja bem-vindo ao sistema!"
    
    def test_apply_template_missing_variables(self, template_manager, sample_template):
        """Testa aplicação de template com variáveis faltando"""
        template_manager.create_template(sample_template)
        
        variables = {"nome": "João"}  # mensagem faltando
        
        result = template_manager.apply_template(sample_template.id, variables)
        assert result is not None
        assert result["subject"] == "Olá João"
        assert result["body"] == "Bem-vindo João! {mensagem}"
    
    def test_list_templates(self, template_manager, sample_template):
        """Testa listagem de templates"""
        template_manager.create_template(sample_template)
        
        templates = template_manager.list_templates()
        assert len(templates) == 1
        assert templates[0].id == sample_template.id

class TestAdvancedNotificationSystem:
    """Testes para sistema principal de notificações"""
    
    @pytest.fixture
    def notification_config(self):
        return {
            'smtp_host': 'localhost',
            'smtp_port': 587,
            'smtp_user': 'test@example.com',
            'smtp_password': 'password',
            'from_email': 'noreply@test.com',
            'slack_webhook_url': 'https://hooks.slack.com/test',
            'discord_webhook_url': 'https://discord.com/api/webhooks/test'
        }
    
    @pytest.fixture
    def notification_system(self, notification_config):
        return AdvancedNotificationSystem(notification_config)
    
    @pytest.fixture
    def sample_notification(self):
        return Notification(
            id="test-123",
            title="Teste Sistema",
            message="Mensagem de teste do sistema",
            notification_type=NotificationType.INFO,
            user_id="user-123",
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            priority=1,
            created_at=datetime.utcnow()
        )
    
    def test_notification_system_initialization(self, notification_config):
        """Testa inicialização do sistema de notificações"""
        system = AdvancedNotificationSystem(notification_config)
        assert system.config == notification_config
        assert len(system.notifiers) == 5  # email, slack, discord, push, webhook
        assert NotificationChannel.EMAIL in system.notifiers
        assert NotificationChannel.SLACK in system.notifiers
    
    def test_get_user_preferences_default(self, notification_system):
        """Testa obtenção de preferências padrão do usuário"""
        prefs = notification_system.get_user_preferences("user-123")
        assert prefs.user_id == "user-123"
        assert prefs.email_enabled is True
        assert prefs.slack_enabled is False
        assert prefs.in_app_enabled is True
    
    def test_is_in_quiet_hours(self, notification_system):
        """Testa verificação de quiet hours"""
        prefs = UserPreferences(
            user_id="user-123",
            quiet_hours_start="22:00",
            quiet_hours_end="08:00"
        )
        
        # Teste durante quiet hours
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 23, 0)  # 23:00
            result = notification_system._is_in_quiet_hours(prefs)
            assert result is True
        
        # Teste fora de quiet hours
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 14, 0)  # 14:00
            result = notification_system._is_in_quiet_hours(prefs)
            assert result is False
    
    def test_create_notification_system_factory(self):
        """Testa factory para criar sistema de notificações"""
        system = create_notification_system()
        assert isinstance(system, AdvancedNotificationSystem)
        assert system.config == DEFAULT_CONFIG
    
    def test_create_notification_system_custom_config(self, notification_config):
        """Testa factory com configuração customizada"""
        system = create_notification_system(notification_config)
        assert isinstance(system, AdvancedNotificationSystem)
        assert system.config == notification_config

class TestWebhookNotifier:
    """Testes para notificador de webhook"""
    
    @pytest.fixture
    def webhook_notifier(self):
        return WebhookNotifier()
    
    @pytest.fixture
    def sample_notification(self):
        return Notification(
            id="test-123",
            title="Teste Webhook",
            message="Mensagem de teste",
            notification_type=NotificationType.INFO,
            user_id="user-123",
            priority=1,
            created_at=datetime.utcnow(),
            metadata={"source": "test"}
        )
    
    @pytest.fixture
    def sample_user_prefs(self):
        return UserPreferences(
            user_id="user-123",
            webhook_enabled=True,
            webhook_url="https://api.example.com/webhook"
        )
    
    @patch('requests.post')
    def test_send_webhook_notification_success(self, mock_post, webhook_notifier, sample_notification, sample_user_prefs):
        """Testa envio bem-sucedido de webhook"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = webhook_notifier.send_notification(sample_notification, sample_user_prefs)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verificar payload
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.example.com/webhook"
        
        payload = call_args[1]['json']
        assert payload['notification_id'] == "test-123"
        assert payload['title'] == "Teste Webhook"
        assert payload['type'] == "info"
        assert payload['user_id'] == "user-123"
    
    def test_send_webhook_notification_disabled(self, webhook_notifier, sample_notification):
        """Testa envio com webhook desabilitado"""
        user_prefs = UserPreferences(user_id="user-123", webhook_enabled=False)
        result = webhook_notifier.send_notification(sample_notification, user_prefs)
        assert result is False
    
    def test_send_webhook_notification_no_url(self, webhook_notifier, sample_notification):
        """Testa envio sem URL de webhook"""
        user_prefs = UserPreferences(user_id="user-123", webhook_enabled=True, webhook_url=None)
        result = webhook_notifier.send_notification(sample_notification, user_prefs)
        assert result is False

class TestPushNotifier:
    """Testes para notificador push"""
    
    @pytest.fixture
    def push_config(self):
        return {
            'fcm_api_key': 'test-api-key'
        }
    
    @pytest.fixture
    def push_notifier(self, push_config):
        return PushNotifier(push_config)
    
    @pytest.fixture
    def sample_notification(self):
        return Notification(
            id="test-123",
            title="Teste Push",
            message="Mensagem de teste",
            notification_type=NotificationType.INFO,
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_user_prefs(self):
        return UserPreferences(
            user_id="user-123",
            push_enabled=True
        )
    
    def test_push_notifier_initialization(self, push_config):
        """Testa inicialização do notificador push"""
        notifier = PushNotifier(push_config)
        assert notifier.fcm_api_key == 'test-api-key'
        assert notifier.fcm_url == "https://fcm.googleapis.com/fcm/send"
    
    def test_send_push_notification_disabled(self, push_notifier, sample_notification):
        """Testa envio com push desabilitado"""
        user_prefs = UserPreferences(user_id="user-123", push_enabled=False)
        result = push_notifier.send_notification(sample_notification, user_prefs)
        assert result is False
    
    def test_send_push_notification_no_api_key(self, push_notifier, sample_notification, sample_user_prefs):
        """Testa envio sem API key"""
        push_notifier.fcm_api_key = None
        result = push_notifier.send_notification(sample_notification, sample_user_prefs)
        assert result is False

if __name__ == '__main__':
    pytest.main([__file__, '-value']) 