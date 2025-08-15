"""
Testes Unitários para Alert Manager
Sistema de Alertas - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de alertas
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json
from typing import Dict, Any

from backend.app.monitoring.alerting_system import (
    AlertManager,
    AlertRule,
    Alert,
    AlertSeverity,
    AlertStatus,
    EmailNotifier,
    SlackNotifier,
    TelegramNotifier,
    AlertRules,
    initialize_alerting_system,
    get_active_alerts,
    acknowledge_alert,
    resolve_alert
)


class TestAlertSeverity:
    """Testes para enum AlertSeverity"""
    
    def test_alert_severity_values(self):
        """Testa valores do enum AlertSeverity"""
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"
    
    def test_alert_severity_comparison(self):
        """Testa comparação entre severidades"""
        assert AlertSeverity.LOW < AlertSeverity.MEDIUM
        assert AlertSeverity.MEDIUM < AlertSeverity.HIGH
        assert AlertSeverity.HIGH < AlertSeverity.CRITICAL


class TestAlertStatus:
    """Testes para enum AlertStatus"""
    
    def test_alert_status_values(self):
        """Testa valores do enum AlertStatus"""
        assert AlertStatus.ACTIVE.value == "active"
        assert AlertStatus.ACKNOWLEDGED.value == "acknowledged"
        assert AlertStatus.RESOLVED.value == "resolved"
        assert AlertStatus.SUPPRESSED.value == "suppressed"


class TestAlertRule:
    """Testes para classe AlertRule"""
    
    def test_alert_rule_creation(self):
        """Testa criação de regra de alerta"""
        async def test_condition():
            return True
        
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=test_condition,
            severity=AlertSeverity.HIGH,
            threshold=80.0,
            cooldown_minutes=5,
            enabled=True,
            notification_channels=["email", "slack"]
        )
        
        assert rule.name == "test_rule"
        assert rule.description == "Test rule"
        assert rule.severity == AlertSeverity.HIGH
        assert rule.threshold == 80.0
        assert rule.cooldown_minutes == 5
        assert rule.enabled is True
        assert rule.notification_channels == ["email", "slack"]
    
    def test_alert_rule_defaults(self):
        """Testa valores padrão da regra de alerta"""
        async def test_condition():
            return True
        
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=test_condition,
            severity=AlertSeverity.MEDIUM,
            threshold=50.0
        )
        
        assert rule.cooldown_minutes == 5
        assert rule.enabled is True
        assert rule.notification_channels == []


class TestAlert:
    """Testes para classe Alert"""
    
    def test_alert_creation(self):
        """Testa criação de alerta"""
        alert = Alert(
            id="test_alert_001",
            rule_name="test_rule",
            severity=AlertSeverity.HIGH,
            message="Test alert message",
            details={"threshold": 80.0},
            timestamp=datetime.now()
        )
        
        assert alert.id == "test_alert_001"
        assert alert.rule_name == "test_rule"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.message == "Test alert message"
        assert alert.details == {"threshold": 80.0}
        assert alert.status == AlertStatus.ACTIVE
        assert alert.acknowledged_by is None
        assert alert.acknowledged_at is None
        assert alert.resolved_at is None
    
    def test_alert_with_acknowledgment(self):
        """Testa alerta com reconhecimento"""
        timestamp = datetime.now()
        alert = Alert(
            id="test_alert_002",
            rule_name="test_rule",
            severity=AlertSeverity.CRITICAL,
            message="Critical alert",
            details={},
            timestamp=timestamp
        )
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = "admin"
        alert.acknowledged_at = timestamp
        
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "admin"
        assert alert.acknowledged_at == timestamp


class TestAlertManager:
    """Testes para classe AlertManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.hset = AsyncMock()
        redis_mock.expire = AsyncMock()
        return redis_mock
    
    @pytest.fixture
    def alert_manager(self, mock_redis):
        """Instância do AlertManager para testes"""
        return AlertManager(mock_redis)
    
    def test_alert_manager_initialization(self, mock_redis):
        """Testa inicialização do AlertManager"""
        manager = AlertManager(mock_redis)
        
        assert manager.redis_client == mock_redis
        assert manager.rules == {}
        assert manager.active_alerts == {}
        assert manager.notification_handlers == {}
        assert manager.is_running is False
        assert manager.check_interval == 30
    
    def test_register_rule(self, alert_manager):
        """Testa registro de regra de alerta"""
        async def test_condition():
            return True
        
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=test_condition,
            severity=AlertSeverity.HIGH,
            threshold=80.0
        )
        
        alert_manager.register_rule(rule)
        
        assert "test_rule" in alert_manager.rules
        assert alert_manager.rules["test_rule"] == rule
    
    def test_register_notification_handler(self, alert_manager):
        """Testa registro de handler de notificação"""
        async def test_handler(alert, rule):
            pass
        
        alert_manager.register_notification_handler("email", test_handler)
        
        assert "email" in alert_manager.notification_handlers
        assert alert_manager.notification_handlers["email"] == test_handler
    
    def test_start_monitoring(self, alert_manager):
        """Testa início do monitoramento"""
        alert_manager.start_monitoring()
        
        assert alert_manager.is_running is True
    
    def test_stop_monitoring(self, alert_manager):
        """Testa parada do monitoramento"""
        alert_manager.is_running = True
        alert_manager.stop_monitoring()
        
        assert alert_manager.is_running is False
    
    @pytest.mark.asyncio
    async def test_trigger_alert(self, alert_manager):
        """Testa disparo de alerta"""
        async def test_condition():
            return True
        
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=test_condition,
            severity=AlertSeverity.HIGH,
            threshold=80.0,
            notification_channels=["email"]
        )
        
        # Mock do handler de notificação
        mock_handler = AsyncMock()
        alert_manager.notification_handlers["email"] = mock_handler
        
        await alert_manager._trigger_alert(rule)
        
        # Verifica se o alerta foi criado
        assert len(alert_manager.active_alerts) == 1
        
        alert_id = list(alert_manager.active_alerts.keys())[0]
        alert = alert_manager.active_alerts[alert_id]
        
        assert alert.rule_name == "test_rule"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.status == AlertStatus.ACTIVE
        
        # Verifica se a notificação foi enviada
        mock_handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_trigger_alert_with_cooldown(self, alert_manager):
        """Testa disparo de alerta com cooldown"""
        async def test_condition():
            return True
        
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=test_condition,
            severity=AlertSeverity.HIGH,
            threshold=80.0,
            cooldown_minutes=5
        )
        
        # Primeiro alerta
        await alert_manager._trigger_alert(rule)
        initial_count = len(alert_manager.active_alerts)
        
        # Segundo alerta (deve ser ignorado por cooldown)
        await alert_manager._trigger_alert(rule)
        
        # Verifica se não foi criado novo alerta
        assert len(alert_manager.active_alerts) == initial_count
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, alert_manager):
        """Testa resolução de alerta"""
        # Cria alerta ativo
        alert = Alert(
            id="test_alert",
            rule_name="test_rule",
            severity=AlertSeverity.HIGH,
            message="Test alert",
            details={},
            timestamp=datetime.now()
        )
        alert_manager.active_alerts["test_alert"] = alert
        
        await alert_manager._resolve_alert("test_rule")
        
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
    
    def test_get_active_alert(self, alert_manager):
        """Testa obtenção de alerta ativo"""
        # Cria alerta ativo
        alert = Alert(
            id="test_alert",
            rule_name="test_rule",
            severity=AlertSeverity.HIGH,
            message="Test alert",
            details={},
            timestamp=datetime.now()
        )
        alert_manager.active_alerts["test_alert"] = alert
        
        # Cria alerta resolvido
        resolved_alert = Alert(
            id="resolved_alert",
            rule_name="test_rule",
            severity=AlertSeverity.MEDIUM,
            message="Resolved alert",
            details={},
            timestamp=datetime.now()
        )
        resolved_alert.status = AlertStatus.RESOLVED
        alert_manager.active_alerts["resolved_alert"] = resolved_alert
        
        active_alert = alert_manager._get_active_alert("test_rule")
        
        assert active_alert is not None
        assert active_alert.id == "test_alert"
        assert active_alert.status == AlertStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_save_alert(self, alert_manager):
        """Testa salvamento de alerta no Redis"""
        alert = Alert(
            id="test_alert",
            rule_name="test_rule",
            severity=AlertSeverity.HIGH,
            message="Test alert",
            details={"threshold": 80.0},
            timestamp=datetime.now()
        )
        
        await alert_manager._save_alert(alert)
        
        # Verifica se o Redis foi chamado
        alert_manager.redis_client.hset.assert_called_once()
        alert_manager.redis_client.expire.assert_called_once_with(
            f"alert:{alert.id}", 86400 * 7
        )


class TestEmailNotifier:
    """Testes para EmailNotifier"""
    
    @pytest.fixture
    def email_config(self):
        """Configuração de email para testes"""
        return {
            "smtp_server": "smtp.test.com",
            "smtp_port": 587,
            "username": "test@test.com",
            "password": "password123",
            "from_email": "alerts@test.com",
            "to_email": "admin@test.com"
        }
    
    @pytest.fixture
    def email_notifier(self, email_config):
        """Instância do EmailNotifier para testes"""
        return EmailNotifier(email_config)
    
    @pytest.mark.asyncio
    async def test_send_alert_email(self, email_notifier):
        """Testa envio de alerta por email"""
        rule = AlertRule(
            name="test_rule",
            description="Test rule description",
            condition=lambda: True,
            severity=AlertSeverity.HIGH,
            threshold=80.0
        )
        
        alert = Alert(
            id="test_alert",
            rule_name="test_rule",
            severity=AlertSeverity.HIGH,
            message="Test alert message",
            details={"threshold": 80.0},
            timestamp=datetime.now()
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            await email_notifier.send_alert(alert, rule)
            
            # Verifica se o SMTP foi configurado corretamente
            mock_smtp.assert_called_once_with("smtp.test.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@test.com", "password123")
            mock_server.send_message.assert_called_once()


class TestSlackNotifier:
    """Testes para SlackNotifier"""
    
    @pytest.fixture
    def slack_config(self):
        """Configuração do Slack para testes"""
        return {
            "webhook_url": "https://hooks.slack.com/test",
            "channel": "#alerts"
        }
    
    @pytest.fixture
    def slack_notifier(self, slack_config):
        """Instância do SlackNotifier para testes"""
        return SlackNotifier(slack_config)
    
    @pytest.mark.asyncio
    async def test_send_alert_slack(self, slack_notifier):
        """Testa envio de alerta para Slack"""
        rule = AlertRule(
            name="test_rule",
            description="Test rule description",
            condition=lambda: True,
            severity=AlertSeverity.CRITICAL,
            threshold=90.0
        )
        
        alert = Alert(
            id="test_alert",
            rule_name="test_rule",
            severity=AlertSeverity.CRITICAL,
            message="Critical alert message",
            details={"threshold": 90.0},
            timestamp=datetime.now()
        )
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            await slack_notifier.send_alert(alert, rule)
            
            # Verifica se a requisição foi feita
            mock_post.assert_called_once()
            
            # Verifica o payload
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://hooks.slack.com/test"
            
            payload = call_args[1]['json']
            assert payload['channel'] == "#alerts"
            assert len(payload['attachments']) == 1
            
            attachment = payload['attachments'][0]
            assert "🚨 Alerta CRITICAL" in attachment['title']
            assert attachment['color'] == "#ff0000"


class TestTelegramNotifier:
    """Testes para TelegramNotifier"""
    
    @pytest.fixture
    def telegram_config(self):
        """Configuração do Telegram para testes"""
        return {
            "bot_token": "test_bot_token",
            "chat_id": "test_chat_id"
        }
    
    @pytest.fixture
    def telegram_notifier(self, telegram_config):
        """Instância do TelegramNotifier para testes"""
        return TelegramNotifier(telegram_config)
    
    @pytest.mark.asyncio
    async def test_send_alert_telegram(self, telegram_notifier):
        """Testa envio de alerta para Telegram"""
        rule = AlertRule(
            name="test_rule",
            description="Test rule description",
            condition=lambda: True,
            severity=AlertSeverity.MEDIUM,
            threshold=60.0
        )
        
        alert = Alert(
            id="test_alert",
            rule_name="test_rule",
            severity=AlertSeverity.MEDIUM,
            message="Medium alert message",
            details={"threshold": 60.0},
            timestamp=datetime.now()
        )
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            await telegram_notifier.send_alert(alert, rule)
            
            # Verifica se a requisição foi feita
            mock_post.assert_called_once()
            
            # Verifica o payload
            call_args = mock_post.call_args
            expected_url = f"https://api.telegram.org/bot{telegram_config['bot_token']}/sendMessage"
            assert call_args[0][0] == expected_url
            
            payload = call_args[1]['json']
            assert payload['chat_id'] == "test_chat_id"
            assert payload['parse_mode'] == "Markdown"
            assert "🟡 *ALERTA MEDIUM*" in payload['text']


class TestAlertRules:
    """Testes para AlertRules"""
    
    @pytest.mark.asyncio
    async def test_high_cpu_usage(self):
        """Testa regra de uso alto de CPU"""
        with patch('psutil.cpu_percent') as mock_cpu:
            # Simula CPU alto
            mock_cpu.return_value = 85.0
            result = await AlertRules.high_cpu_usage(80.0)
            assert result is True
            
            # Simula CPU normal
            mock_cpu.return_value = 70.0
            result = await AlertRules.high_cpu_usage(80.0)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_high_memory_usage(self):
        """Testa regra de uso alto de memória"""
        with patch('psutil.virtual_memory') as mock_memory:
            # Simula memória alta
            mock_memory.return_value.percent = 90.0
            result = await AlertRules.high_memory_usage(85.0)
            assert result is True
            
            # Simula memória normal
            mock_memory.return_value.percent = 70.0
            result = await AlertRules.high_memory_usage(85.0)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_low_disk_space(self):
        """Testa regra de espaço em disco baixo"""
        with patch('psutil.disk_usage') as mock_disk:
            # Simula disco cheio
            mock_disk.return_value.used = 95
            mock_disk.return_value.total = 100
            result = await AlertRules.low_disk_space(90.0)
            assert result is True
            
            # Simula disco com espaço
            mock_disk.return_value.used = 80
            mock_disk.return_value.total = 100
            result = await AlertRules.low_disk_space(90.0)
            assert result is False
    
    @pytest.mark.asyncio
    async def test_high_error_rate(self):
        """Testa regra de taxa alta de erros"""
        # Esta regra retorna False por padrão (não implementada)
        result = await AlertRules.high_error_rate(10.0)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_slow_response_time(self):
        """Testa regra de tempo de resposta lento"""
        # Esta regra retorna False por padrão (não implementada)
        result = await AlertRules.slow_response_time(5.0)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_database_connection_issues(self):
        """Testa regra de problemas de conexão com banco"""
        # Esta regra retorna False por padrão (não implementada)
        result = await AlertRules.database_connection_issues()
        assert result is False


class TestAlertManagerIntegration:
    """Testes de integração para AlertManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.hset = AsyncMock()
        redis_mock.expire = AsyncMock()
        return redis_mock
    
    @pytest.mark.asyncio
    async def test_initialize_alerting_system(self, mock_redis):
        """Testa inicialização do sistema de alertas"""
        config = {
            "email": {
                "smtp_server": "smtp.test.com",
                "smtp_port": 587,
                "username": "test@test.com",
                "password": "password123",
                "from_email": "alerts@test.com"
            },
            "slack": {
                "webhook_url": "https://hooks.slack.com/test",
                "channel": "#alerts"
            }
        }
        
        with patch('backend.app.monitoring.alerting_system.AlertManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            
            initialize_alerting_system(mock_redis, config)
            
            # Verifica se o manager foi criado
            mock_manager_class.assert_called_once_with(mock_redis)
            
            # Verifica se os handlers foram registrados
            assert mock_manager.register_notification_handler.call_count >= 2
            
            # Verifica se as regras foram registradas
            assert mock_manager.register_rule.call_count >= 3
            
            # Verifica se o monitoramento foi iniciado
            mock_manager.start_monitoring.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_alerts(self, mock_redis):
        """Testa obtenção de alertas ativos"""
        # Mock do alert manager global
        with patch('backend.app.monitoring.alerting_system.alert_manager') as mock_alert_manager:
            mock_alert_manager.active_alerts = {
                "alert1": Alert(
                    id="alert1",
                    rule_name="test_rule",
                    severity=AlertSeverity.HIGH,
                    message="Active alert",
                    details={},
                    timestamp=datetime.now(),
                    status=AlertStatus.ACTIVE
                ),
                "alert2": Alert(
                    id="alert2",
                    rule_name="test_rule",
                    severity=AlertSeverity.MEDIUM,
                    message="Resolved alert",
                    details={},
                    timestamp=datetime.now(),
                    status=AlertStatus.RESOLVED
                )
            }
            
            active_alerts = await get_active_alerts()
            
            assert len(active_alerts) == 1
            assert active_alerts[0]["id"] == "alert1"
            assert active_alerts[0]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, mock_redis):
        """Testa reconhecimento de alerta"""
        with patch('backend.app.monitoring.alerting_system.alert_manager') as mock_alert_manager:
            alert = Alert(
                id="test_alert",
                rule_name="test_rule",
                severity=AlertSeverity.HIGH,
                message="Test alert",
                details={},
                timestamp=datetime.now(),
                status=AlertStatus.ACTIVE
            )
            
            mock_alert_manager.active_alerts = {"test_alert": alert}
            mock_alert_manager._save_alert = AsyncMock()
            
            result = await acknowledge_alert("test_alert", "admin")
            
            assert result is True
            assert alert.status == AlertStatus.ACKNOWLEDGED
            assert alert.acknowledged_by == "admin"
            assert alert.acknowledged_at is not None
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, mock_redis):
        """Testa resolução de alerta"""
        with patch('backend.app.monitoring.alerting_system.alert_manager') as mock_alert_manager:
            alert = Alert(
                id="test_alert",
                rule_name="test_rule",
                severity=AlertSeverity.HIGH,
                message="Test alert",
                details={},
                timestamp=datetime.now(),
                status=AlertStatus.ACTIVE
            )
            
            mock_alert_manager.active_alerts = {"test_alert": alert}
            mock_alert_manager._save_alert = AsyncMock()
            
            result = await resolve_alert("test_alert")
            
            assert result is True
            assert alert.status == AlertStatus.RESOLVED
            assert alert.resolved_at is not None


class TestAlertManagerErrorHandling:
    """Testes de tratamento de erros para AlertManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.hset = AsyncMock()
        redis_mock.expire = AsyncMock()
        return redis_mock
    
    @pytest.mark.asyncio
    async def test_redis_error_handling(self, mock_redis):
        """Testa tratamento de erro do Redis"""
        mock_redis.hset.side_effect = Exception("Redis connection error")
        
        alert_manager = AlertManager(mock_redis)
        
        alert = Alert(
            id="test_alert",
            rule_name="test_rule",
            severity=AlertSeverity.HIGH,
            message="Test alert",
            details={},
            timestamp=datetime.now()
        )
        
        # Não deve levantar exceção
        await alert_manager._save_alert(alert)
    
    @pytest.mark.asyncio
    async def test_notification_error_handling(self, mock_redis):
        """Testa tratamento de erro de notificação"""
        alert_manager = AlertManager(mock_redis)
        
        async def failing_handler(alert, rule):
            raise Exception("Notification failed")
        
        alert_manager.notification_handlers["email"] = failing_handler
        
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=lambda: True,
            severity=AlertSeverity.HIGH,
            threshold=80.0,
            notification_channels=["email"]
        )
        
        # Não deve levantar exceção
        await alert_manager._send_notifications(Mock(), rule)
    
    @pytest.mark.asyncio
    async def test_rule_check_error_handling(self, mock_redis):
        """Testa tratamento de erro na verificação de regras"""
        alert_manager = AlertManager(mock_redis)
        
        async def failing_condition():
            raise Exception("Rule check failed")
        
        rule = AlertRule(
            name="failing_rule",
            description="Failing rule",
            condition=failing_condition,
            severity=AlertSeverity.HIGH,
            threshold=80.0
        )
        
        alert_manager.rules["failing_rule"] = rule
        
        # Não deve levantar exceção
        await alert_manager._check_all_rules()


class TestAlertManagerPerformance:
    """Testes de performance para AlertManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.hset = AsyncMock()
        redis_mock.expire = AsyncMock()
        return redis_mock
    
    @pytest.mark.asyncio
    async def test_multiple_alerts_performance(self, mock_redis):
        """Testa performance com múltiplos alertas"""
        alert_manager = AlertManager(mock_redis)
        
        # Cria múltiplas regras
        for i in range(10):
            async def test_condition():
                return True
            
            rule = AlertRule(
                name=f"rule_{i}",
                description=f"Rule {i}",
                condition=test_condition,
                severity=AlertSeverity.HIGH,
                threshold=80.0
            )
            alert_manager.register_rule(rule)
        
        # Verifica se todas as regras foram registradas
        assert len(alert_manager.rules) == 10
    
    @pytest.mark.asyncio
    async def test_alert_cooldown_performance(self, mock_redis):
        """Testa performance do sistema de cooldown"""
        alert_manager = AlertManager(mock_redis)
        
        async def test_condition():
            return True
        
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=test_condition,
            severity=AlertSeverity.HIGH,
            threshold=80.0,
            cooldown_minutes=1
        )
        
        # Dispara múltiplos alertas rapidamente
        for _ in range(5):
            await alert_manager._trigger_alert(rule)
        
        # Deve ter apenas um alerta ativo devido ao cooldown
        active_alerts = [a for a in alert_manager.active_alerts.values() 
                        if a.status == AlertStatus.ACTIVE]
        assert len(active_alerts) == 1


if __name__ == "__main__":
    pytest.main([__file__]) 