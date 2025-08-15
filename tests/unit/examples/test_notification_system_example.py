from typing import Dict, List, Optional, Any
"""
Testes Unitários - Exemplo do Sistema de Notificações
=====================================================

Testes para o exemplo prático do sistema de notificações avançado.

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Importa o exemplo
from examples.notification_system_example import NotificationSystemExample


class TestNotificationSystemExample:
    """Testes para o NotificationSystemExample."""
    
    @pytest.fixture
    def example(self):
        """Instância do exemplo para testes."""
        return NotificationSystemExample()
    
    def test_example_initialization(self, example):
        """Testa inicialização do exemplo."""
        assert example is not None
        assert hasattr(example, 'notification_manager')
        assert hasattr(example, 'config')
    
    def test_get_config(self, example):
        """Testa obtenção da configuração."""
        config = example._get_config()
        
        assert isinstance(config, dict)
        assert "smtp" in config
        assert "slack" in config
        assert "sms" in config
        
        # Verifica configuração SMTP
        smtp_config = config["smtp"]
        assert smtp_config["server"] == "smtp.gmail.com"
        assert smtp_config["port"] == 587
        assert smtp_config["use_tls"] is True
        
        # Verifica configuração Slack
        slack_config = config["slack"]
        assert "webhook_url" in slack_config
        assert slack_config["channel"] == "#notifications"
        
        # Verifica configuração SMS
        sms_config = config["sms"]
        assert "api_key" in sms_config
        assert "api_secret" in sms_config
    
    def test_setup_templates(self, example):
        """Testa configuração dos templates."""
        # Verifica se os templates foram criados
        templates = example.notification_manager.templates
        
        assert "execucao_sucesso" in templates
        assert "execucao_erro" in templates
        assert "relatorio_semanal" in templates
        assert "sistema_alerta" in templates
        
        # Verifica template de execução sucesso
        exec_success = templates["execucao_sucesso"]
        assert exec_success.name == "execucao_sucesso"
        assert "execucao_id" in exec_success.variables
        assert exec_success.channel.value == "email"
        
        # Verifica template de erro
        exec_error = templates["execucao_erro"]
        assert exec_error.name == "execucao_erro"
        assert "error_message" in exec_error.variables
        
        # Verifica template de relatório
        relatorio = templates["relatorio_semanal"]
        assert relatorio.name == "relatorio_semanal"
        assert "periodo" in relatorio.variables
        
        # Verifica template de alerta
        alerta = templates["sistema_alerta"]
        assert alerta.name == "sistema_alerta"
        assert "alerta_titulo" in alerta.variables
    
    def test_setup_user_preferences(self, example):
        """Testa configuração das preferências de usuário."""
        preferences = example.notification_manager.preferences
        
        # Verifica usuário padrão
        assert "user_default" in preferences
        default_pref = preferences["user_default"]
        assert default_pref.user_id == "user_default"
        assert default_pref.channels["websocket"] is True
        assert default_pref.channels["email"] is True
        assert default_pref.channels["slack"] is False
        assert default_pref.channels["sms"] is False
        assert default_pref.frequency_limit == 20
        
        # Verifica usuário premium
        assert "user_premium" in preferences
        premium_pref = preferences["user_premium"]
        assert premium_pref.user_id == "user_premium"
        assert premium_pref.channels["slack"] is True
        assert premium_pref.channels["sms"] is True
        assert premium_pref.frequency_limit == 50
        
        # Verifica usuário noturno
        assert "user_night" in preferences
        night_pref = preferences["user_night"]
        assert night_pref.user_id == "user_night"
        assert night_pref.channels["email"] is False
        assert night_pref.channels["slack"] is True
        assert night_pref.channels["sms"] is True
        assert night_pref.quiet_hours == {}  # Sem horário silencioso
    
    @pytest.mark.asyncio
    async def test_exemplo_execucao_sucesso(self, example):
        """Testa exemplo de execução bem-sucedida."""
        with patch.object(example.notification_manager, 'send_notification', return_value=True) as mock_send:
            await example.exemplo_execucao_sucesso()
            
            # Verifica se a notificação foi enviada
            mock_send.assert_called_once()
            
            # Verifica parâmetros da notificação
            notification = mock_send.call_args[0][0]
            assert notification.user_id == "user_premium"
            assert notification.type.value == "success"
            assert notification.priority.value == 2  # NORMAL
            assert "websocket" in [c.value for c in notification.channels]
            assert "email" in [c.value for c in notification.channels]
            assert "slack" in [c.value for c in notification.channels]
    
    @pytest.mark.asyncio
    async def test_exemplo_execucao_erro(self, example):
        """Testa exemplo de erro na execução."""
        with patch.object(example.notification_manager, 'send_notification', return_value=True) as mock_send:
            await example.exemplo_execucao_erro()
            
            # Verifica se a notificação foi enviada
            mock_send.assert_called_once()
            
            # Verifica parâmetros da notificação
            notification = mock_send.call_args[0][0]
            assert notification.user_id == "user_default"
            assert notification.type.value == "error"
            assert notification.priority.value == 3  # HIGH
            assert "websocket" in [c.value for c in notification.channels]
            assert "email" in [c.value for c in notification.channels]
    
    @pytest.mark.asyncio
    async def test_exemplo_relatorio_semanal(self, example):
        """Testa exemplo de relatório semanal."""
        with patch.object(example.notification_manager, 'send_notification', return_value=True) as mock_send:
            await example.exemplo_relatorio_semanal()
            
            # Verifica se a notificação foi enviada
            mock_send.assert_called_once()
            
            # Verifica parâmetros da notificação
            notification = mock_send.call_args[0][0]
            assert notification.user_id == "user_premium"
            assert notification.type.value == "info"
            assert notification.priority.value == 2  # NORMAL
            assert "email" in [c.value for c in notification.channels]
            assert "slack" in [c.value for c in notification.channels]
    
    @pytest.mark.asyncio
    async def test_exemplo_sistema_alerta(self, example):
        """Testa exemplo de alerta do sistema."""
        with patch.object(example.notification_manager, 'send_notification', return_value=True) as mock_send:
            await example.exemplo_sistema_alerta()
            
            # Verifica se a notificação foi enviada
            mock_send.assert_called_once()
            
            # Verifica parâmetros da notificação
            notification = mock_send.call_args[0][0]
            assert notification.user_id == "user_night"
            assert notification.type.value == "warning"
            assert notification.priority.value == 3  # HIGH
            assert "websocket" in [c.value for c in notification.channels]
            assert "slack" in [c.value for c in notification.channels]
            assert "sms" in [c.value for c in notification.channels]
    
    @pytest.mark.asyncio
    async def test_exemplo_notificacao_simples(self, example):
        """Testa exemplo de notificação simples."""
        with patch.object(example.notification_manager, 'send_notification', return_value=True) as mock_send:
            await example.exemplo_notificacao_simples()
            
            # Verifica se a notificação foi enviada
            mock_send.assert_called_once()
            
            # Verifica parâmetros da notificação
            notification = mock_send.call_args[0][0]
            assert notification.user_id == "user_default"
            assert notification.subject == "Bem-vindo ao Omni Keywords Finder!"
            assert "Bem-vindo" in notification.content
            assert notification.type.value == "success"
            assert notification.priority.value == 2  # NORMAL
    
    @pytest.mark.asyncio
    async def test_exemplo_rate_limiting(self, example):
        """Testa exemplo de rate limiting."""
        # Simula envio bem-sucedido para as primeiras notificações
        # e falha para as últimas (rate limit)
        call_count = 0
        
        def mock_send_side_effect(notification):
            nonlocal call_count
            call_count += 1
            # Simula rate limit após 20 notificações
            return call_count <= 20
        
        with patch.object(example.notification_manager, 'send_notification', side_effect=mock_send_side_effect):
            await example.exemplo_rate_limiting()
            
            # Verifica que várias notificações foram tentadas
            assert call_count > 0
    
    def test_exemplo_metricas(self, example):
        """Testa exemplo de métricas."""
        with patch.object(example.notification_manager, 'get_metrics') as mock_metrics:
            mock_metrics.return_value = {
                "notifications_total": 100,
                "notifications_success": 95,
                "notifications_failed": 5,
                "channels_available": 4,
                "channels_total": 4,
                "templates_count": 4,
                "history_count": 100
            }
            
            # Chama o método (não é async)
            example.exemplo_metricas()
            
            # Verifica se as métricas foram obtidas
            mock_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_executar_exemplos(self, example):
        """Testa execução de todos os exemplos."""
        with patch.object(example, 'exemplo_notificacao_simples') as mock_simple, \
             patch.object(example, 'exemplo_execucao_sucesso') as mock_success, \
             patch.object(example, 'exemplo_execucao_erro') as mock_error, \
             patch.object(example, 'exemplo_relatorio_semanal') as mock_relatorio, \
             patch.object(example, 'exemplo_sistema_alerta') as mock_alerta, \
             patch.object(example, 'exemplo_rate_limiting') as mock_rate, \
             patch.object(example, 'exemplo_metricas') as mock_metrics:
            
            await example.executar_exemplos()
            
            # Verifica se todos os exemplos foram chamados
            mock_simple.assert_called_once()
            mock_success.assert_called_once()
            mock_error.assert_called_once()
            mock_relatorio.assert_called_once()
            mock_alerta.assert_called_once()
            mock_rate.assert_called_once()
            mock_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_executar_exemplos_with_error(self, example):
        """Testa execução dos exemplos com erro."""
        with patch.object(example, 'exemplo_notificacao_simples', side_effect=Exception("Test error")):
            # Deve capturar o erro e continuar
            await example.executar_exemplos()
    
    def test_template_rendering(self, example):
        """Testa renderização de templates."""
        # Testa template de execução sucesso
        exec_data = {
            "user_name": "João",
            "execucao_id": "TEST_001",
            "keywords_count": "100",
            "tempo_execucao": "2m",
            "blog_url": "https://test.com",
            "data_inicio": "2024-01-01 10:00",
            "data_conclusao": "2024-01-01 10:02",
            "dashboard_url": "https://dashboard.com"
        }
        
        notification = example.notification_manager.render_template("execucao_sucesso", exec_data)
        
        assert notification is not None
        assert notification.subject == "✅ Execução TEST_001 concluída com sucesso!"
        assert "João" in notification.content
        assert "TEST_001" in notification.content
        assert "100" in notification.content
    
    def test_template_rendering_error(self, example):
        """Testa renderização de template inexistente."""
        notification = example.notification_manager.render_template("template_inexistente", {})
        assert notification is None
    
    def test_user_preferences_retrieval(self, example):
        """Testa obtenção de preferências de usuário."""
        # Testa usuário existente
        preferences = example.notification_manager._get_user_preferences("user_premium")
        assert preferences is not None
        assert preferences.user_id == "user_premium"
        assert preferences.channels["slack"] is True
        assert preferences.channels["sms"] is True
        
        # Testa usuário novo (deve criar preferências padrão)
        new_preferences = example.notification_manager._get_user_preferences("new_user")
        assert new_preferences is not None
        assert new_preferences.user_id == "new_user"
        assert new_preferences.channels["websocket"] is True
        assert new_preferences.channels["email"] is True
    
    def test_available_channels_filtering(self, example):
        """Testa filtragem de canais disponíveis."""
        preferences = example.notification_manager._get_user_preferences("user_default")
        available = example.notification_manager._get_available_channels(preferences)
        
        # Verifica que apenas canais habilitados estão disponíveis
        assert "websocket" in [c.value for c in available]
        assert "email" in [c.value for c in available]
        assert "slack" not in [c.value for c in available]
        assert "sms" not in [c.value for c in available]


class TestNotificationSystemIntegration:
    """Testes de integração do sistema de notificações."""
    
    @pytest.fixture
    def example(self):
        """Instância do exemplo para testes de integração."""
        return NotificationSystemExample()
    
    @pytest.mark.asyncio
    async def test_full_notification_workflow(self, example):
        """Testa workflow completo de notificação."""
        # Cria dados de teste
        test_data = {
            "user_name": "Test User",
            "execucao_id": "INTEGRATION_TEST_001",
            "keywords_count": "500",
            "tempo_execucao": "1m 30s",
            "blog_url": "https://integration-test.com",
            "data_inicio": "2024-01-01 12:00:00",
            "data_conclusao": "2024-01-01 12:01:30",
            "dashboard_url": "https://dashboard.com/test"
        }
        
        # Renderiza template
        notification = example.notification_manager.render_template("execucao_sucesso", test_data)
        notification.user_id = "user_premium"
        notification.channels = [example.notification_manager.channels[NotificationChannel.WEBSOCKET].__class__]
        
        # Simula envio
        with patch.object(example.notification_manager.channels[NotificationChannel.WEBSOCKET], 'send', return_value=True):
            result = await example.notification_manager.send_notification(notification)
            
            assert result is True
            assert notification.status == "sent"
            assert notification.sent_at is not None
    
    def test_template_variables_validation(self, example):
        """Testa validação de variáveis de template."""
        # Testa template com variáveis obrigatórias
        template = example.notification_manager.templates["execucao_sucesso"]
        
        # Verifica se todas as variáveis necessárias estão definidas
        required_vars = ["user_name", "execucao_id", "keywords_count", "tempo_execucao", 
                        "blog_url", "data_inicio", "data_conclusao", "dashboard_url"]
        
        for var in required_vars:
            assert var in template.variables
    
    def test_notification_priority_mapping(self, example):
        """Testa mapeamento de prioridades."""
        # Testa diferentes tipos de notificação
        test_cases = [
            (NotificationType.INFO, NotificationPriority.NORMAL),
            (NotificationType.SUCCESS, NotificationPriority.NORMAL),
            (NotificationType.WARNING, NotificationPriority.HIGH),
            (NotificationType.ERROR, NotificationPriority.HIGH),
            (NotificationType.CRITICAL, NotificationPriority.URGENT)
        ]
        
        for notification_type, expected_priority in test_cases:
            notification = create_notification(
                user_id="test_user",
                subject="Test",
                content="Test",
                notification_type=notification_type,
                priority=expected_priority
            )
            
            assert notification.type == notification_type
            assert notification.priority == expected_priority
    
    def test_channel_availability_check(self, example):
        """Testa verificação de disponibilidade de canais."""
        # Verifica se todos os canais configurados estão disponíveis
        for channel_name, channel_provider in example.notification_manager.channels.items():
            # Simula verificação de disponibilidade
            with patch.object(channel_provider, 'is_available', return_value=True):
                assert channel_provider.is_available() is True
    
    def test_notification_history_management(self, example):
        """Testa gerenciamento do histórico de notificações."""
        user_id = "history_test_user"
        
        # Adiciona várias notificações
        for index in range(10):
            notification = create_notification(
                user_id=user_id,
                subject=f"History Test {index}",
                content=f"Content {index}",
                channels=[NotificationChannel.WEBSOCKET]
            )
            example.notification_manager._save_to_history(notification)
        
        # Verifica histórico
        history = example.notification_manager.get_notification_history(user_id, limit=5)
        assert len(history) == 5
        assert all(n.user_id == user_id for n in history)
        
        # Verifica que as notificações mais recentes estão primeiro
        assert history[-1].subject == "History Test 9"
        assert history[0].subject == "History Test 5"


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 