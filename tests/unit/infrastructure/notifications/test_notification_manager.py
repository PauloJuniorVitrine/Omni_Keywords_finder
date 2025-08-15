"""
Testes Unitários - Sistema de Notificações Avançado
===================================================

Testes abrangentes para o NotificationManager e componentes relacionados.

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Importa classes do sistema de notificações
from infrastructure.notifications.avancado.notification_manager import (
    NotificationManager,
    Notification,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    NotificationTemplate,
    NotificationPreferences,
    create_notification
)
from infrastructure.notifications.avancado.channels.websocket_channel import WebSocketChannel
from infrastructure.notifications.avancado.channels.email_channel import EmailChannel
from infrastructure.notifications.avancado.channels.slack_channel import SlackChannel
from infrastructure.notifications.avancado.channels.sms_channel import SMSChannel


class TestNotificationManager:
    """Testes para o NotificationManager."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis para testes."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.publish.return_value = 1
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = "0"
        mock_redis.incr.return_value = 1
        mock_redis.pipeline.return_value.__enter__.return_value = mock_redis
        return mock_redis
    
    @pytest.fixture
    def config(self):
        """Configuração de teste."""
        return {
            "smtp": {
                "server": "smtp.test.com",
                "port": 587,
                "username": "test@test.com",
                "password": "password",
                "use_tls": True,
                "from_email": "noreply@test.com"
            },
            "slack": {
                "webhook_url": "https://hooks.slack.com/services/test",
                "channel": "#test"
            },
            "sms": {
                "api_key": "test_key",
                "api_secret": "test_secret"
            }
        }
    
    @pytest.fixture
    def notification_manager(self, mock_redis, config):
        """Instância do NotificationManager para testes."""
        return NotificationManager(mock_redis, config)
    
    @pytest.fixture
    def sample_notification(self):
        """Notificação de exemplo para testes."""
        return Notification(
            user_id="test_user",
            type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            subject="Test Subject",
            content="Test Content",
            channels=[NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL]
        )
    
    def test_notification_manager_initialization(self, notification_manager):
        """Testa inicialização do NotificationManager."""
        assert notification_manager is not None
        assert hasattr(notification_manager, 'channels')
        assert hasattr(notification_manager, 'templates')
        assert hasattr(notification_manager, 'preferences')
    
    def test_channel_initialization(self, notification_manager):
        """Testa inicialização dos canais."""
        # Verifica se os canais foram inicializados
        assert NotificationChannel.WEBSOCKET in notification_manager.channels
        assert NotificationChannel.EMAIL in notification_manager.channels
        assert NotificationChannel.SLACK in notification_manager.channels
        assert NotificationChannel.SMS in notification_manager.channels
    
    def test_validate_notification_success(self, notification_manager, sample_notification):
        """Testa validação de notificação válida."""
        result = notification_manager._validate_notification(sample_notification)
        assert result is True
    
    def test_validate_notification_missing_user_id(self, notification_manager):
        """Testa validação de notificação sem user_id."""
        notification = Notification(
            user_id="",
            subject="Test",
            content="Test",
            channels=[NotificationChannel.WEBSOCKET]
        )
        result = notification_manager._validate_notification(notification)
        assert result is False
    
    def test_validate_notification_missing_content(self, notification_manager):
        """Testa validação de notificação sem conteúdo."""
        notification = Notification(
            user_id="test_user",
            subject="",
            content="",
            channels=[NotificationChannel.WEBSOCKET]
        )
        result = notification_manager._validate_notification(notification)
        assert result is False
    
    def test_validate_notification_missing_channels(self, notification_manager):
        """Testa validação de notificação sem canais."""
        notification = Notification(
            user_id="test_user",
            subject="Test",
            content="Test",
            channels=[]
        )
        result = notification_manager._validate_notification(notification)
        assert result is False
    
    def test_rate_limit_check(self, notification_manager):
        """Testa verificação de rate limiting."""
        user_id = "test_user"
        
        # Primeira verificação deve passar
        result = notification_manager._check_rate_limit(user_id)
        assert result is True
        
        # Simula múltiplas notificações
        for _ in range(15):  # Mais que o limite padrão (10)
            notification_manager._check_rate_limit(user_id)
        
        # Última verificação deve falhar
        result = notification_manager._check_rate_limit(user_id)
        assert result is False
    
    def test_quiet_hours_check(self, notification_manager):
        """Testa verificação de horário silencioso."""
        user_id = "test_user"
        
        # Configura horário silencioso
        preferences = NotificationPreferences(
            user_id=user_id,
            quiet_hours={"start": "22:00", "end": "08:00"}
        )
        notification_manager.preferences[user_id] = preferences
        
        # Testa fora do horário silencioso (simulado)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 14, 0)  # 14:00
            result = notification_manager._is_in_quiet_hours(user_id)
            assert result is False
    
    def test_get_user_preferences(self, notification_manager):
        """Testa obtenção de preferências do usuário."""
        user_id = "test_user"
        preferences = notification_manager._get_user_preferences(user_id)
        
        assert preferences is not None
        assert preferences.user_id == user_id
        assert NotificationChannel.WEBSOCKET in preferences.channels
        assert NotificationChannel.EMAIL in preferences.channels
    
    def test_get_available_channels(self, notification_manager):
        """Testa obtenção de canais disponíveis."""
        preferences = NotificationPreferences(
            user_id="test_user",
            channels={
                NotificationChannel.WEBSOCKET: True,
                NotificationChannel.EMAIL: True,
                NotificationChannel.SLACK: False,
                NotificationChannel.SMS: False
            }
        )
        
        available = notification_manager._get_available_channels(preferences)
        assert NotificationChannel.WEBSOCKET in available
        assert NotificationChannel.EMAIL in available
        assert NotificationChannel.SLACK not in available
        assert NotificationChannel.SMS not in available
    
    def test_create_template(self, notification_manager):
        """Testa criação de template."""
        template = NotificationTemplate(
            name="test_template",
            subject="Test {{variable}}",
            content="Content {{variable}}",
            variables=["variable"],
            channel=NotificationChannel.EMAIL
        )
        
        result = notification_manager.create_template(template)
        assert result is True
        assert "test_template" in notification_manager.templates
    
    def test_get_template(self, notification_manager):
        """Testa obtenção de template."""
        template = NotificationTemplate(
            name="test_template",
            subject="Test",
            content="Content",
            channel=NotificationChannel.EMAIL
        )
        notification_manager.templates["test_template"] = template
        
        retrieved = notification_manager.get_template("test_template")
        assert retrieved == template
    
    def test_render_template(self, notification_manager):
        """Testa renderização de template."""
        template = NotificationTemplate(
            name="test_template",
            subject="Hello {{name}}",
            content="Welcome {{name}}!",
            variables=["name"],
            channel=NotificationChannel.EMAIL
        )
        notification_manager.templates["test_template"] = template
        
        variables = {"name": "John"}
        notification = notification_manager.render_template("test_template", variables)
        
        assert notification is not None
        assert notification.subject == "Hello John"
        assert notification.content == "Welcome John!"
    
    def test_save_to_history(self, notification_manager, sample_notification):
        """Testa salvamento no histórico."""
        initial_count = len(notification_manager.notification_history)
        notification_manager._save_to_history(sample_notification)
        
        assert len(notification_manager.notification_history) == initial_count + 1
        assert notification_manager.notification_history[-1] == sample_notification
    
    def test_get_notification_history(self, notification_manager):
        """Testa obtenção do histórico de notificações."""
        user_id = "test_user"
        
        # Adiciona algumas notificações
        for index in range(5):
            notification = Notification(
                user_id=user_id,
                subject=f"Test {index}",
                content=f"Content {index}",
                channels=[NotificationChannel.WEBSOCKET]
            )
            notification_manager._save_to_history(notification)
        
        # Adiciona notificação de outro usuário
        other_notification = Notification(
            user_id="other_user",
            subject="Other",
            content="Other",
            channels=[NotificationChannel.WEBSOCKET]
        )
        notification_manager._save_to_history(other_notification)
        
        # Obtém histórico do usuário
        history = notification_manager.get_notification_history(user_id, limit=3)
        assert len(history) == 3
        assert all(n.user_id == user_id for n in history)
    
    def test_get_metrics(self, notification_manager, mock_redis):
        """Testa obtenção de métricas."""
        metrics = notification_manager.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "channels_available" in metrics
        assert "channels_total" in metrics
        assert "templates_count" in metrics
        assert "history_count" in metrics


class TestWebSocketChannel:
    """Testes para o canal WebSocket."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis para testes."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.publish.return_value = 1
        return mock_redis
    
    @pytest.fixture
    def websocket_channel(self, mock_redis):
        """Instância do WebSocketChannel para testes."""
        return WebSocketChannel(mock_redis)
    
    @pytest.fixture
    def sample_notification(self):
        """Notificação de exemplo para testes."""
        return Notification(
            user_id="test_user",
            type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            subject="Test Subject",
            content="Test Content",
            channels=[NotificationChannel.WEBSOCKET]
        )
    
    def test_websocket_channel_initialization(self, websocket_channel):
        """Testa inicialização do WebSocketChannel."""
        assert websocket_channel is not None
        assert websocket_channel.channel_name == "notifications"
        assert hasattr(websocket_channel, 'connection_pool')
    
    @pytest.mark.asyncio
    async def test_send_notification(self, websocket_channel, sample_notification, mock_redis):
        """Testa envio de notificação via WebSocket."""
        result = await websocket_channel.send(sample_notification)
        
        assert result is True
        mock_redis.publish.assert_called()
    
    def test_is_available(self, websocket_channel, mock_redis):
        """Testa verificação de disponibilidade."""
        result = websocket_channel.is_available()
        assert result is True
    
    def test_is_available_failure(self, websocket_channel, mock_redis):
        """Testa verificação de disponibilidade com falha."""
        mock_redis.ping.side_effect = Exception("Connection failed")
        result = websocket_channel.is_available()
        assert result is False
    
    def test_get_name(self, websocket_channel):
        """Testa obtenção do nome do canal."""
        name = websocket_channel.get_name()
        assert name == "websocket"
    
    def test_subscribe_user(self, websocket_channel, mock_redis):
        """Testa inscrição de usuário."""
        user_id = "test_user"
        callback = Mock()
        
        result = websocket_channel.subscribe_user(user_id, callback)
        
        assert result is True
        assert user_id in websocket_channel.connection_pool
    
    def test_unsubscribe_user(self, websocket_channel, mock_redis):
        """Testa remoção de inscrição de usuário."""
        user_id = "test_user"
        callback = Mock()
        
        # Primeiro inscreve
        websocket_channel.subscribe_user(user_id, callback)
        assert user_id in websocket_channel.connection_pool
        
        # Depois remove
        result = websocket_channel.unsubscribe_user(user_id)
        assert result is True
        assert user_id not in websocket_channel.connection_pool
    
    def test_get_active_connections(self, websocket_channel):
        """Testa contagem de conexões ativas."""
        # Adiciona algumas conexões
        for index in range(3):
            user_id = f"user_{index}"
            callback = Mock()
            websocket_channel.subscribe_user(user_id, callback)
        
        count = websocket_channel.get_active_connections()
        assert count == 3


class TestEmailChannel:
    """Testes para o canal Email."""
    
    @pytest.fixture
    def smtp_config(self):
        """Configuração SMTP para testes."""
        return {
            "server": "smtp.test.com",
            "port": 587,
            "username": "test@test.com",
            "password": "password",
            "use_tls": True,
            "from_email": "noreply@test.com"
        }
    
    @pytest.fixture
    def email_channel(self, smtp_config):
        """Instância do EmailChannel para testes."""
        return EmailChannel(smtp_config)
    
    @pytest.fixture
    def sample_notification(self):
        """Notificação de exemplo para testes."""
        return Notification(
            user_id="test_user",
            type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            subject="Test Subject",
            content="Test Content",
            channels=[NotificationChannel.EMAIL]
        )
    
    def test_email_channel_initialization(self, email_channel):
        """Testa inicialização do EmailChannel."""
        assert email_channel is not None
        assert email_channel.smtp_config.server == "smtp.test.com"
        assert email_channel.smtp_config.port == 587
        assert hasattr(email_channel, 'templates')
    
    def test_get_user_email(self, email_channel):
        """Testa obtenção de email do usuário."""
        user_id = "test_user"
        email = email_channel._get_user_email(user_id)
        
        assert email == f"{user_id}@example.com"
        assert user_id in email_channel.user_emails
    
    def test_html_to_text(self, email_channel):
        """Testa conversão de HTML para texto."""
        html = "<h1>Title</h1><p>Content with <strong>bold</strong> text.</p>"
        text = email_channel._html_to_text(html)
        
        assert "Title" in text
        assert "Content with bold text" in text
        assert "<h1>" not in text
        assert "<strong>" not in text
    
    def test_render_template(self, email_channel):
        """Testa renderização de template de email."""
        template_name = "execucao_concluida"
        variables = {
            "user_name": "John",
            "execucao_id": "123",
            "keywords_count": "50",
            "tempo_execucao": "2m 30s",
            "blog_url": "https://example.com",
            "data_inicio": "2024-01-01 10:00",
            "data_conclusao": "2024-01-01 10:02",
            "dashboard_url": "https://dashboard.com"
        }
        
        result = email_channel._render_template(template_name, variables)
        
        assert result is not None
        assert "subject" in result
        assert "html" in result
        assert "text" in result
        assert "John" in result["subject"]
        assert "123" in result["html"]
    
    def test_add_template(self, email_channel):
        """Testa adição de template."""
        from infrastructure.notifications.avancado.channels.email_channel import EmailTemplate
        
        template = EmailTemplate(
            name="custom_template",
            subject="Custom {{name}}",
            html_content="<h1>Hello {{name}}</h1>",
            text_content="Hello {{name}}",
            variables=["name"]
        )
        
        email_channel.add_template(template)
        assert "custom_template" in email_channel.templates
    
    def test_get_templates(self, email_channel):
        """Testa obtenção de templates."""
        templates = email_channel.get_templates()
        assert isinstance(templates, list)
        assert "execucao_concluida" in templates
        assert "execucao_erro" in templates
        assert "relatorio_semanal" in templates


class TestSlackChannel:
    """Testes para o canal Slack."""
    
    @pytest.fixture
    def slack_config(self):
        """Configuração Slack para testes."""
        return {
            "webhook_url": "https://hooks.slack.com/services/test",
            "channel": "#test"
        }
    
    @pytest.fixture
    def slack_channel(self, slack_config):
        """Instância do SlackChannel para testes."""
        return SlackChannel(
            webhook_url=slack_config["webhook_url"],
            channel=slack_config["channel"]
        )
    
    @pytest.fixture
    def sample_notification(self):
        """Notificação de exemplo para testes."""
        return Notification(
            user_id="test_user",
            type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            subject="Test Subject",
            content="Test Content",
            channels=[NotificationChannel.SLACK]
        )
    
    def test_slack_channel_initialization(self, slack_channel):
        """Testa inicialização do SlackChannel."""
        assert slack_channel is not None
        assert slack_channel.config.webhook_url == "https://hooks.slack.com/services/test"
        assert slack_channel.config.channel == "#test"
        assert hasattr(slack_channel, 'message_templates')
    
    def test_get_channel_for_notification(self, slack_channel, sample_notification):
        """Testa determinação de canal para notificação."""
        # Testa com template específico
        sample_notification.template_name = "execucao_success"
        channel = slack_channel._get_channel_for_notification(sample_notification)
        assert channel == "#execucoes"
        
        # Testa com tipo específico
        sample_notification.template_name = None
        sample_notification.type = NotificationType.ERROR
        channel = slack_channel._get_channel_for_notification(sample_notification)
        assert channel == "#errors"
        
        # Testa canal padrão
        sample_notification.type = NotificationType.INFO
        channel = slack_channel._get_channel_for_notification(sample_notification)
        assert channel == "#test"
    
    def test_render_template_variables(self, slack_channel):
        """Testa renderização de variáveis no template."""
        payload = {
            "text": "Hello {{name}}!",
            "attachments": [{
                "title": "Welcome {{name}}",
                "fields": [
                    {"title": "User", "value": "{{name}}", "short": True}
                ]
            }]
        }
        
        variables = {"name": "John"}
        result = slack_channel._render_template_variables(payload, variables)
        
        assert result["text"] == "Hello John!"
        assert result["attachments"][0]["title"] == "Welcome John"
        assert result["attachments"][0]["fields"][0]["value"] == "John"
    
    def test_add_template(self, slack_channel):
        """Testa adição de template."""
        template = {
            "text": "Custom template {{variable}}",
            "attachments": [{
                "color": "#36a64f",
                "title": "{{title}}"
            }]
        }
        
        slack_channel.add_template("custom_template", template)
        assert "custom_template" in slack_channel.message_templates
    
    def test_set_channel_mapping(self, slack_channel):
        """Testa definição de mapeamento de canal."""
        slack_channel.set_channel_mapping("custom_type", "#custom_channel")
        assert slack_channel.channel_mappings["custom_type"] == "#custom_channel"
    
    def test_get_templates(self, slack_channel):
        """Testa obtenção de templates."""
        templates = slack_channel.get_templates()
        assert isinstance(templates, list)
        assert "execucao_success" in templates
        assert "execucao_error" in templates
    
    def test_get_channels(self, slack_channel):
        """Testa obtenção de canais."""
        channels = slack_channel.get_channels()
        assert isinstance(channels, list)
        assert "#test" in channels  # Canal padrão


class TestSMSChannel:
    """Testes para o canal SMS."""
    
    @pytest.fixture
    def sms_config(self):
        """Configuração SMS para testes."""
        return {
            "api_key": "test_key",
            "api_secret": "test_secret"
        }
    
    @pytest.fixture
    def sms_channel(self, sms_config):
        """Instância do SMSChannel para testes."""
        return SMSChannel(
            api_key=sms_config["api_key"],
            api_secret=sms_config["api_secret"]
        )
    
    @pytest.fixture
    def sample_notification(self):
        """Notificação de exemplo para testes."""
        return Notification(
            user_id="test_user",
            type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            subject="Test Subject",
            content="Test Content",
            channels=[NotificationChannel.SMS]
        )
    
    def test_sms_channel_initialization(self, sms_channel):
        """Testa inicialização do SMSChannel."""
        assert sms_channel is not None
        assert sms_channel.config.api_key == "test_key"
        assert sms_channel.config.api_secret == "test_secret"
        assert hasattr(sms_channel, 'providers')
    
    def test_get_user_phone(self, sms_channel):
        """Testa obtenção de telefone do usuário."""
        user_id = "test_user"
        phone = sms_channel._get_user_phone(user_id)
        
        assert phone == "+5511999999999"
        assert user_id in sms_channel.user_phones
    
    def test_prepare_sms_content(self, sms_channel, sample_notification):
        """Testa preparação de conteúdo SMS."""
        content = sms_channel._prepare_sms_content(sample_notification)
        
        assert "Test Subject" in content
        assert "Test Content" in content
        assert len(content) <= sms_channel.config.max_length
    
    def test_prepare_sms_content_with_template(self, sms_channel):
        """Testa preparação de conteúdo SMS com template."""
        notification = Notification(
            user_id="test_user",
            template_name="execucao_concluida",
            variables={
                "execucao_id": "123",
                "keywords_count": "50",
                "tempo_execucao": "2m 30s"
            },
            channels=[NotificationChannel.SMS]
        )
        
        content = sms_channel._prepare_sms_content(notification)
        
        assert "123" in content
        assert "50" in content
        assert "2m 30s" in content
    
    def test_rate_limit_check(self, sms_channel):
        """Testa verificação de rate limiting."""
        user_id = "test_user"
        
        # Primeira verificação deve passar
        result = sms_channel._check_rate_limit(user_id)
        assert result is True
        
        # Simula múltiplas notificações
        for _ in range(15):  # Mais que o limite padrão
            sms_channel._check_rate_limit(user_id)
        
        # Última verificação deve falhar
        result = sms_channel._check_rate_limit(user_id)
        assert result is False
    
    def test_add_provider(self, sms_channel):
        """Testa adição de provedor."""
        mock_provider = Mock()
        sms_channel.add_provider("test_provider", mock_provider)
        
        assert "test_provider" in sms_channel.providers
        assert sms_channel.providers["test_provider"] == mock_provider
    
    def test_get_providers(self, sms_channel):
        """Testa obtenção de provedores."""
        providers = sms_channel.get_providers()
        assert isinstance(providers, list)
        assert "simulated" in providers


class TestCreateNotification:
    """Testes para função de conveniência create_notification."""
    
    def test_create_notification_defaults(self):
        """Testa criação de notificação com valores padrão."""
        notification = create_notification(
            user_id="test_user",
            subject="Test Subject",
            content="Test Content"
        )
        
        assert notification.user_id == "test_user"
        assert notification.subject == "Test Subject"
        assert notification.content == "Test Content"
        assert notification.type == NotificationType.INFO
        assert notification.priority == NotificationPriority.NORMAL
        assert NotificationChannel.WEBSOCKET in notification.channels
        assert NotificationChannel.EMAIL in notification.channels
    
    def test_create_notification_custom(self):
        """Testa criação de notificação com valores customizados."""
        notification = create_notification(
            user_id="test_user",
            subject="Test Subject",
            content="Test Content",
            notification_type=NotificationType.ERROR,
            priority=NotificationPriority.HIGH,
            channels=[NotificationChannel.SLACK],
            template_name="test_template",
            variables={"key": "value"}
        )
        
        assert notification.type == NotificationType.ERROR
        assert notification.priority == NotificationPriority.HIGH
        assert notification.channels == [NotificationChannel.SLACK]
        assert notification.template_name == "test_template"
        assert notification.variables == {"key": "value"}


# Testes de integração
class TestNotificationIntegration:
    """Testes de integração do sistema de notificações."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis para testes de integração."""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.publish.return_value = 1
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = "0"
        mock_redis.incr.return_value = 1
        mock_redis.pipeline.return_value.__enter__.return_value = mock_redis
        return mock_redis
    
    @pytest.fixture
    def config(self):
        """Configuração completa para testes de integração."""
        return {
            "smtp": {
                "server": "smtp.test.com",
                "port": 587,
                "username": "test@test.com",
                "password": "password",
                "use_tls": True,
                "from_email": "noreply@test.com"
            },
            "slack": {
                "webhook_url": "https://hooks.slack.com/services/test",
                "channel": "#test"
            },
            "sms": {
                "api_key": "test_key",
                "api_secret": "test_secret"
            }
        }
    
    @pytest.fixture
    def notification_manager(self, mock_redis, config):
        """NotificationManager para testes de integração."""
        return NotificationManager(mock_redis, config)
    
    @pytest.mark.asyncio
    async def test_full_notification_flow(self, notification_manager):
        """Testa fluxo completo de notificação."""
        # Cria template
        template = NotificationTemplate(
            name="test_template",
            subject="Hello {{name}}",
            content="Welcome {{name}}!",
            variables=["name"],
            channel=NotificationChannel.EMAIL
        )
        notification_manager.create_template(template)
        
        # Cria notificação usando template
        notification = notification_manager.render_template("test_template", {"name": "John"})
        notification.user_id = "test_user"
        notification.channels = [NotificationChannel.WEBSOCKET, NotificationChannel.EMAIL]
        
        # Envia notificação
        result = await notification_manager.send_notification(notification)
        
        # Verifica resultado
        assert result is True
        assert notification.status == "sent"
        assert notification.sent_at is not None
    
    @pytest.mark.asyncio
    async def test_notification_with_fallback(self, notification_manager):
        """Testa notificação com fallback de canal."""
        # Cria notificação
        notification = create_notification(
            user_id="test_user",
            subject="Test Subject",
            content="Test Content",
            channels=[NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET]
        )
        
        # Simula falha do email
        with patch.object(notification_manager.channels[NotificationChannel.EMAIL], 'send', return_value=False):
            result = await notification_manager.send_notification(notification)
            
            # Deve tentar WebSocket como fallback
            assert result is True
    
    def test_notification_history_persistence(self, notification_manager):
        """Testa persistência do histórico de notificações."""
        user_id = "test_user"
        
        # Cria múltiplas notificações
        for index in range(10):
            notification = create_notification(
                user_id=user_id,
                subject=f"Test {index}",
                content=f"Content {index}"
            )
            notification_manager._save_to_history(notification)
        
        # Verifica histórico
        history = notification_manager.get_notification_history(user_id, limit=5)
        assert len(history) == 5
        assert all(n.user_id == user_id for n in history)
    
    def test_metrics_collection(self, notification_manager, mock_redis):
        """Testa coleta de métricas."""
        # Simula algumas notificações
        for index in range(5):
            notification = create_notification(
                user_id=f"user_{index}",
                subject=f"Test {index}",
                content=f"Content {index}"
            )
            notification_manager._save_to_history(notification)
            notification_manager._record_metrics(notification, 1)
        
        # Obtém métricas
        metrics = notification_manager.get_metrics()
        
        assert "notifications_total" in metrics
        assert "channels_available" in metrics
        assert "templates_count" in metrics
        assert "history_count" in metrics
        assert metrics["history_count"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 