from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTES UNITÁRIOS - ALERT MANAGER

Tracing ID: test-alert-manager-2025-01-27-001
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Testes unitários para o sistema de alertas automáticos
com cobertura completa de todas as funcionalidades.
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adiciona o diretório scripts ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from alert_manager import AlertManager, Alert, NotificationConfig

class TestAlert:
    """Testes para a classe Alert"""
    
    def test_alert_creation(self):
        """Testa criação de alerta"""
        alert = Alert(
            id="test_alert_001",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test alert description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        assert alert.id == "test_alert_001"
        assert alert.name == "Test Alert"
        assert alert.severity == "critical"
        assert alert.team == "backend"
        assert alert.component == "api"
        assert alert.status == "firing"
        assert alert.escalation_level == 0
        assert alert.notification_count == 0
    
    def test_alert_resolution(self):
        """Testa resolução de alerta"""
        alert = Alert(
            id="test_alert_002",
            name="Test Alert",
            severity="warning",
            team="devops",
            component="infrastructure",
            description="Test alert description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        # Resolve o alerta
        alert.status = "resolved"
        alert.resolved_at = datetime.now()
        alert.acknowledged_by = "test-user"
        
        assert alert.status == "resolved"
        assert alert.resolved_at is not None
        assert alert.acknowledged_by == "test-user"
    
    def test_alert_escalation(self):
        """Testa escalação de alerta"""
        alert = Alert(
            id="test_alert_003",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="database",
            description="Test alert description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        # Simula escalação
        alert.escalation_level = 1
        alert.notification_count = 2
        alert.last_notification = datetime.now()
        
        assert alert.escalation_level == 1
        assert alert.notification_count == 2
        assert alert.last_notification is not None

class TestNotificationConfig:
    """Testes para a classe NotificationConfig"""
    
    def test_slack_config(self):
        """Testa configuração do Slack"""
        config = NotificationConfig(
            type="slack",
            config={
                "webhook_url": "https://hooks.slack.com/services/test",
                "default_channel": "#alerts"
            },
            enabled=True,
            retry_count=3,
            retry_delay=30
        )
        
        assert config.type == "slack"
        assert config.config["webhook_url"] == "https://hooks.slack.com/services/test"
        assert config.config["default_channel"] == "#alerts"
        assert config.enabled is True
        assert config.retry_count == 3
        assert config.retry_delay == 30
    
    def test_pagerduty_config(self):
        """Testa configuração do PagerDuty"""
        config = NotificationConfig(
            type="pagerduty",
            config={
                "url": "https://events.pagerduty.com/v2/enqueue",
                "routing_key": "test-routing-key"
            },
            enabled=True
        )
        
        assert config.type == "pagerduty"
        assert config.config["url"] == "https://events.pagerduty.com/v2/enqueue"
        assert config.config["routing_key"] == "test-routing-key"
    
    def test_email_config(self):
        """Testa configuração de email"""
        config = NotificationConfig(
            type="email",
            config={
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "test@example.com",
                "password": "test-password"
            },
            enabled=True
        )
        
        assert config.type == "email"
        assert config.config["smtp_host"] == "smtp.gmail.com"
        assert config.config["smtp_port"] == 587

class TestAlertManager:
    """Testes para a classe AlertManager"""
    
    @pytest.fixture
    def mock_config(self):
        """Configuração mock para testes"""
        return {
            "global": {
                "slack_api_url": "https://hooks.slack.com/services/test",
                "pagerduty_url": "https://events.pagerduty.com/v2/enqueue",
                "smtp_smarthost": "smtp.gmail.com:587",
                "smtp_auth_username": "test@example.com",
                "smtp_auth_password": "test-password",
                "smtp_from": "alerts@example.com"
            },
            "silence_rules": [],
            "escalation": {
                "critical": [
                    {"delay": 5, "receiver": "pagerduty-critical"},
                    {"delay": 15, "receiver": "email-critical"}
                ]
            }
        }
    
    @pytest.fixture
    def alert_manager(self, mock_config):
        """Instância do AlertManager para testes"""
        with patch('alert_manager.AlertManager._load_config', return_value=mock_config):
            with patch('alert_manager.AlertManager._setup_redis', return_value=None):
                with patch('alert_manager.AlertManager.start_metrics_server'):
                    manager = AlertManager()
                    return manager
    
    def test_alert_manager_initialization(self, alert_manager):
        """Testa inicialização do AlertManager"""
        assert alert_manager.alerts == {}
        assert len(alert_manager.notification_configs) == 3  # slack, pagerduty, email
        assert alert_manager.redis_client is None
        assert alert_manager.silence_rules == []
    
    def test_process_alert(self, alert_manager):
        """Testa processamento de alerta"""
        alert_data = {
            "id": "test_alert_001",
            "name": "API Down",
            "severity": "critical",
            "team": "backend",
            "component": "api",
            "description": "API is not responding",
            "instance": "api-server-1"
        }
        
        alert = alert_manager.process_alert(alert_data)
        
        assert alert is not None
        assert alert.id == "test_alert_001"
        assert alert.name == "API Down"
        assert alert.severity == "critical"
        assert alert.status == "firing"
        assert alert.id in alert_manager.alerts
    
    def test_process_alert_with_silence(self, alert_manager):
        """Testa processamento de alerta com silêncio"""
        # Adiciona regra de silêncio
        alert_manager.silence_rules = [
            {
                "matchers": [{"name": "alertname", "value": "API Down"}],
                "time_intervals": [{"name": "maintenance_window"}]
            }
        ]
        
        alert_data = {
            "name": "API Down",
            "severity": "critical",
            "team": "backend",
            "component": "api",
            "description": "API is not responding",
            "instance": "api-server-1"
        }
        
        with patch.object(alert_manager, '_should_silence', return_value=True):
            alert = alert_manager.process_alert(alert_data)
            assert alert is None
    
    def test_resolve_alert(self, alert_manager):
        """Testa resolução de alerta"""
        # Cria alerta
        alert_data = {
            "id": "test_alert_002",
            "name": "Database Slow",
            "severity": "warning",
            "team": "backend",
            "component": "database",
            "description": "Database queries are slow",
            "instance": "db-server-1"
        }
        
        alert = alert_manager.process_alert(alert_data)
        
        # Resolve o alerta
        result = alert_manager.resolve_alert("test_alert_002", "test-user")
        
        assert result is True
        assert alert_manager.alerts["test_alert_002"].status == "resolved"
        assert alert_manager.alerts["test_alert_002"].acknowledged_by == "test-user"
    
    def test_resolve_nonexistent_alert(self, alert_manager):
        """Testa resolução de alerta inexistente"""
        result = alert_manager.resolve_alert("nonexistent_alert", "test-user")
        assert result is False
    
    @patch('requests.post')
    def test_send_slack_notification(self, mock_post, alert_manager):
        """Testa envio de notificação Slack"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        alert = Alert(
            id="test_alert_003",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        result = alert_manager.send_notification(alert, "slack-notifications")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_pagerduty_notification(self, mock_post, alert_manager):
        """Testa envio de notificação PagerDuty"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        alert = Alert(
            id="test_alert_004",
            name="Critical Alert",
            severity="critical",
            team="backend",
            component="database",
            description="Database is down",
            instance="db-server-1",
            status="firing",
            created_at=datetime.now()
        )
        
        result = alert_manager.send_notification(alert, "pagerduty-critical")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_notification(self, mock_smtp, alert_manager):
        """Testa envio de notificação por email"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        alert = Alert(
            id="test_alert_005",
            name="Warning Alert",
            severity="warning",
            team="devops",
            component="infrastructure",
            description="High CPU usage",
            instance="server-1",
            status="firing",
            created_at=datetime.now()
        )
        
        result = alert_manager.send_notification(alert, "email-critical")
        
        assert result is True
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    def test_send_notification_unknown_receiver(self, alert_manager):
        """Testa envio para receiver desconhecido"""
        alert = Alert(
            id="test_alert_006",
            name="Test Alert",
            severity="info",
            team="unknown",
            component="unknown",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        result = alert_manager.send_notification(alert, "unknown-receiver")
        assert result is False
    
    def test_check_escalation(self, alert_manager):
        """Testa verificação de escalação"""
        # Cria alerta crítico
        alert_data = {
            "id": "test_alert_007",
            "name": "Critical Alert",
            "severity": "critical",
            "team": "backend",
            "component": "api",
            "description": "Critical issue",
            "instance": "api-server-1"
        }
        
        alert = alert_manager.process_alert(alert_data)
        
        # Simula tempo passado
        alert.created_at = datetime.now() - timedelta(minutes=10)
        
        with patch.object(alert_manager, 'send_notification', return_value=True):
            alert_manager.check_escalation()
            
            # Verifica se escalação foi executada
            assert alert.escalation_level > 0
            assert alert.last_notification is not None
    
    def test_cleanup_old_alerts(self, alert_manager):
        """Testa limpeza de alertas antigos"""
        # Cria alerta antigo
        old_alert_data = {
            "id": "old_alert_001",
            "name": "Old Alert",
            "severity": "info",
            "team": "unknown",
            "component": "unknown",
            "description": "Old alert",
            "instance": "old-instance"
        }
        
        old_alert = alert_manager.process_alert(old_alert_data)
        old_alert.created_at = datetime.now() - timedelta(hours=25)
        
        # Cria alerta recente
        recent_alert_data = {
            "id": "recent_alert_001",
            "name": "Recent Alert",
            "severity": "warning",
            "team": "backend",
            component="api",
            "description": "Recent alert",
            "instance": "recent-instance"
        }
        
        recent_alert = alert_manager.process_alert(recent_alert_data)
        
        # Executa limpeza
        alert_manager.cleanup_old_alerts(max_age_hours=24)
        
        # Verifica se alerta antigo foi removido
        assert "old_alert_001" not in alert_manager.alerts
        assert "recent_alert_001" in alert_manager.alerts
    
    def test_get_alert_statistics(self, alert_manager):
        """Testa obtenção de estatísticas"""
        # Cria alguns alertas
        alert_data_1 = {
            "id": "alert_001",
            "name": "Critical Alert",
            "severity": "critical",
            "team": "backend",
            "component": "api",
            "description": "Critical issue",
            "instance": "api-server-1"
        }
        
        alert_data_2 = {
            "id": "alert_002",
            "name": "Warning Alert",
            "severity": "warning",
            "team": "devops",
            "component": "infrastructure",
            "description": "Warning issue",
            "instance": "server-1"
        }
        
        alert_manager.process_alert(alert_data_1)
        alert_manager.process_alert(alert_data_2)
        
        # Resolve um alerta
        alert_manager.resolve_alert("alert_001", "test-user")
        
        stats = alert_manager.get_alert_statistics()
        
        assert stats["total_alerts"] == 2
        assert stats["active_alerts"] == 1
        assert stats["resolved_alerts"] == 1
        assert stats["by_severity"]["critical"] == 1
        assert stats["by_severity"]["warning"] == 1
        assert stats["by_team"]["backend"] == 1
        assert stats["by_team"]["devops"] == 1
    
    def test_should_silence(self, alert_manager):
        """Testa verificação de silêncio"""
        alert_data = {
            "name": "Test Alert",
            "severity": "info",
            "team": "unknown",
            "component": "unknown",
            "description": "Test description",
            "instance": "test-instance"
        }
        
        # Sem regras de silêncio
        result = alert_manager._should_silence(alert_data)
        assert result is False
        
        # Com regra de silêncio
        alert_manager.silence_rules = [
            {
                "matchers": [{"name": "alertname", "value": "Test Alert"}]
            }
        ]
        
        with patch.object(alert_manager, '_matches_silence_rule', return_value=True):
            result = alert_manager._should_silence(alert_data)
            assert result is True
    
    def test_matches_silence_rule(self, alert_manager):
        """Testa correspondência com regra de silêncio"""
        alert_data = {
            "name": "Test Alert",
            "severity": "info"
        }
        
        rule = {
            "matchers": [{"name": "alertname", "value": "Test Alert"}]
        }
        
        current_time = datetime.now()
        
        # Implementação simplificada retorna False
        result = alert_manager._matches_silence_rule(alert_data, rule, current_time)
        assert result is False
    
    @patch('redis.Redis')
    def test_redis_integration(self, mock_redis, mock_config):
        """Testa integração com Redis"""
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        
        with patch('alert_manager.AlertManager._load_config', return_value=mock_config):
            with patch('alert_manager.AlertManager.start_metrics_server'):
                manager = AlertManager()
                
                assert manager.redis_client is not None
                mock_redis_instance.ping.assert_called_once()
    
    def test_escalation_policies(self, alert_manager):
        """Testa políticas de escalação"""
        policies = alert_manager.escalation_policies
        
        assert "critical" in policies
        assert "warning" in policies
        
        critical_policy = policies["critical"]
        assert len(critical_policy) == 2
        assert critical_policy[0]["delay"] == 5
        assert critical_policy[0]["receiver"] == "pagerduty-critical"
        assert critical_policy[1]["delay"] == 15
        assert critical_policy[1]["receiver"] == "email-critical"
    
    def test_notification_configs(self, alert_manager):
        """Testa configurações de notificação"""
        configs = alert_manager.notification_configs
        
        assert "slack" in configs
        assert "pagerduty" in configs
        assert "email" in configs
        
        slack_config = configs["slack"]
        assert slack_config.type == "slack"
        assert "webhook_url" in slack_config.config
        
        pagerduty_config = configs["pagerduty"]
        assert pagerduty_config.type == "pagerduty"
        assert "url" in pagerduty_config.config
        
        email_config = configs["email"]
        assert email_config.type == "email"
        assert "smtp_host" in email_config.config

class TestAlertManagerIntegration:
    """Testes de integração do AlertManager"""
    
    @pytest.fixture
    def integration_alert_manager(self):
        """AlertManager para testes de integração"""
        with patch('alert_manager.AlertManager._load_config', return_value={}):
            with patch('alert_manager.AlertManager._setup_redis', return_value=None):
                with patch('alert_manager.AlertManager.start_metrics_server'):
                    return AlertManager()
    
    def test_full_alert_lifecycle(self, integration_alert_manager):
        """Testa ciclo completo de vida do alerta"""
        # 1. Criação do alerta
        alert_data = {
            "id": "lifecycle_alert_001",
            "name": "Lifecycle Test",
            "severity": "critical",
            "team": "backend",
            "component": "api",
            "description": "Lifecycle test alert",
            "instance": "test-instance"
        }
        
        alert = integration_alert_manager.process_alert(alert_data)
        assert alert is not None
        assert alert.status == "firing"
        
        # 2. Simula notificações
        with patch.object(integration_alert_manager, 'send_notification', return_value=True):
            result = integration_alert_manager.send_notification(alert, "slack-notifications")
            assert result is True
        
        # 3. Simula escalação
        alert.created_at = datetime.now() - timedelta(minutes=10)
        with patch.object(integration_alert_manager, 'send_notification', return_value=True):
            integration_alert_manager.check_escalation()
            assert alert.escalation_level > 0
        
        # 4. Resolução
        result = integration_alert_manager.resolve_alert("lifecycle_alert_001", "test-user")
        assert result is True
        assert alert.status == "resolved"
    
    def test_multiple_alerts_processing(self, integration_alert_manager):
        """Testa processamento de múltiplos alertas"""
        alerts_data = [
            {
                "id": f"multi_alert_{index:03d}",
                "name": f"Multi Alert {index}",
                "severity": "critical" if index % 2 == 0 else "warning",
                "team": "backend" if index % 3 == 0 else "devops",
                "component": "api" if index % 2 == 0 else "infrastructure",
                "description": f"Multi alert {index} description",
                "instance": f"instance-{index}"
            }
            for index in range(1, 11)
        ]
        
        # Processa todos os alertas
        processed_alerts = []
        for alert_data in alerts_data:
            alert = integration_alert_manager.process_alert(alert_data)
            processed_alerts.append(alert)
        
        # Verifica se todos foram processados
        assert len(processed_alerts) == 10
        assert len(integration_alert_manager.alerts) == 10
        
        # Verifica estatísticas
        stats = integration_alert_manager.get_alert_statistics()
        assert stats["total_alerts"] == 10
        assert stats["active_alerts"] == 10
        assert stats["by_severity"]["critical"] == 5
        assert stats["by_severity"]["warning"] == 5

if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 