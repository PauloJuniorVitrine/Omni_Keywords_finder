#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTES UNITÁRIOS - ALERT MANAGER
📋 Sistema: Omni Keywords Finder
📅 Data: 2025-01-27
👤 Autor: Paulo Júnior
🔗 Tracing ID: TEST_ALERT_MANAGER_20250127_001

Testes unitários para o sistema de gerenciamento de alertas
baseados COMPLETAMENTE no código real do AlertManager.
"""

import pytest
import json
import time
import yaml
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Importações do código real
from scripts.alert_manager import AlertManager, Alert, NotificationConfig


class TestAlertManager:
    """Testes para o AlertManager baseados no código real"""
    
    @pytest.fixture
    def alert_manager(self):
        """Fixture para criar instância do AlertManager"""
        with patch('scripts.alert_manager.open', create=True), \
             patch('yaml.safe_load', return_value={
                 'global': {
                     'slack_api_url': 'https://hooks.slack.com/test',
                     'pagerduty_url': 'https://events.pagerduty.com/test',
                     'smtp_smarthost': 'smtp.gmail.com:587',
                     'smtp_auth_username': 'test@test.com',
                     'smtp_auth_password': 'password',
                     'smtp_from': 'alerts@test.com'
                 },
                 'silence_rules': []
             }), \
             patch('redis.Redis'), \
             patch('scripts.alert_manager.start_http_server'):
            
            manager = AlertManager("test_config.yaml")
            manager.redis_client = Mock()
            manager.redis_client.ping.return_value = True
            return manager
    
    @pytest.fixture
    def sample_alert_data(self):
        """Dados de exemplo para alerta baseados no código real"""
        return {
            "id": "test_alert_001",
            "name": "API Response Time High",
            "severity": "critical",
            "team": "backend",
            "component": "api",
            "description": "API response time is above threshold",
            "instance": "api-server-1"
        }
    
    def test_alert_manager_initialization(self, alert_manager):
        """Testa inicialização do AlertManager"""
        assert alert_manager.config_path == "test_config.yaml"
        assert isinstance(alert_manager.alerts, dict)
        assert isinstance(alert_manager.notification_configs, dict)
        assert isinstance(alert_manager.escalation_policies, dict)
        assert isinstance(alert_manager.silence_rules, list)
        assert len(alert_manager.notification_configs) == 3  # slack, pagerduty, email
    
    def test_load_config_success(self):
        """Testa carregamento bem-sucedido de configuração"""
        config_data = {
            'global': {
                'slack_api_url': 'https://hooks.slack.com/test'
            },
            'silence_rules': []
        }
        
        with patch('builtins.open', create=True) as mock_open, \
             patch('yaml.safe_load', return_value=config_data):
            
            mock_open.return_value.__enter__.return_value.read.return_value = "test"
            
            manager = AlertManager("test_config.yaml")
            assert manager.config == config_data
    
    def test_load_config_failure(self):
        """Testa falha no carregamento de configuração"""
        with patch('builtins.open', side_effect=FileNotFoundError()), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            manager = AlertManager("nonexistent.yaml")
            assert manager.config == {}
            mock_logger.error.assert_called()
    
    def test_setup_redis_success(self):
        """Testa configuração bem-sucedida do Redis"""
        with patch('redis.Redis') as mock_redis, \
             patch('os.getenv', side_effect=['localhost', '6379', '0']):
            
            mock_redis_instance = Mock()
            mock_redis_instance.ping.return_value = True
            mock_redis.return_value = mock_redis_instance
            
            manager = AlertManager("test_config.yaml")
            assert manager.redis_client is not None
            mock_redis_instance.ping.assert_called_once()
    
    def test_setup_redis_failure(self):
        """Testa falha na configuração do Redis"""
        with patch('redis.Redis', side_effect=Exception("Connection failed")), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            manager = AlertManager("test_config.yaml")
            assert manager.redis_client is None
            mock_logger.warning.assert_called()
    
    def test_setup_notifications_slack(self, alert_manager):
        """Testa configuração de notificações Slack"""
        slack_config = alert_manager.notification_configs.get('slack')
        assert slack_config is not None
        assert slack_config.type == 'slack'
        assert slack_config.config['webhook_url'] == 'https://hooks.slack.com/test'
        assert slack_config.config['default_channel'] == '#alerts'
        assert slack_config.enabled is True
        assert slack_config.retry_count == 3
        assert slack_config.retry_delay == 30
    
    def test_setup_notifications_pagerduty(self, alert_manager):
        """Testa configuração de notificações PagerDuty"""
        pagerduty_config = alert_manager.notification_configs.get('pagerduty')
        assert pagerduty_config is not None
        assert pagerduty_config.type == 'pagerduty'
        assert pagerduty_config.config['url'] == 'https://events.pagerduty.com/test'
        assert 'routing_key' in pagerduty_config.config
    
    def test_setup_notifications_email(self, alert_manager):
        """Testa configuração de notificações Email"""
        email_config = alert_manager.notification_configs.get('email')
        assert email_config is not None
        assert email_config.type == 'email'
        assert email_config.config['smtp_host'] == 'smtp.gmail.com'
        assert email_config.config['smtp_port'] == 587
        assert email_config.config['username'] == 'test@test.com'
        assert email_config.config['password'] == 'password'
        assert email_config.config['from_email'] == 'alerts@test.com'
    
    def test_setup_escalation_policies(self, alert_manager):
        """Testa configuração de políticas de escalação"""
        policies = alert_manager.escalation_policies
        
        # Política para alertas críticos
        critical_policy = policies.get('critical')
        assert len(critical_policy) == 3
        assert critical_policy[0]['delay'] == 5
        assert critical_policy[0]['receiver'] == 'pagerduty-critical'
        assert critical_policy[1]['delay'] == 15
        assert critical_policy[1]['receiver'] == 'email-critical'
        assert critical_policy[2]['delay'] == 30
        assert critical_policy[2]['receiver'] == 'slack-notifications'
        
        # Política para alertas de warning
        warning_policy = policies.get('warning')
        assert len(warning_policy) == 2
        assert warning_policy[0]['delay'] == 10
        assert warning_policy[0]['receiver'] == 'slack-warnings'
        assert warning_policy[1]['delay'] == 30
        assert warning_policy[1]['receiver'] == 'email-critical'
    
    def test_start_metrics_server(self, alert_manager):
        """Testa inicialização do servidor de métricas"""
        with patch('scripts.alert_manager.start_http_server') as mock_start_server, \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            alert_manager.start_metrics_server(9093)
            mock_start_server.assert_called_once_with(9093, registry=alert_manager.registry)
            mock_logger.info.assert_called_with("Servidor de métricas iniciado na porta 9093")
    
    def test_start_metrics_server_failure(self, alert_manager):
        """Testa falha na inicialização do servidor de métricas"""
        with patch('scripts.alert_manager.start_http_server', side_effect=Exception("Port in use")), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            alert_manager.start_metrics_server(9093)
            mock_logger.error.assert_called()
    
    def test_process_alert_success(self, alert_manager, sample_alert_data):
        """Testa processamento bem-sucedido de alerta"""
        with patch.object(alert_manager, '_should_silence', return_value=False), \
             patch('scripts.alert_manager.alert_counter') as mock_counter, \
             patch('scripts.alert_manager.active_alerts') as mock_active_alerts:
            
            alert = alert_manager.process_alert(sample_alert_data)
            
            assert alert is not None
            assert alert.id == "test_alert_001"
            assert alert.name == "API Response Time High"
            assert alert.severity == "critical"
            assert alert.team == "backend"
            assert alert.component == "api"
            assert alert.description == "API response time is above threshold"
            assert alert.instance == "api-server-1"
            assert alert.status == "firing"
            assert isinstance(alert.created_at, datetime)
            assert alert.escalation_level == 0
            assert alert.notification_count == 0
            
            # Verifica se foi armazenado
            assert alert.id in alert_manager.alerts
            assert alert_manager.alerts[alert.id] == alert
            
            # Verifica métricas
            mock_counter.labels.assert_called_with(
                severity="critical",
                team="backend",
                component="api"
            )
            mock_active_alerts.labels.assert_called_with(severity="critical")
    
    def test_process_alert_silenced(self, alert_manager, sample_alert_data):
        """Testa processamento de alerta silenciado"""
        with patch.object(alert_manager, '_should_silence', return_value=True), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            alert = alert_manager.process_alert(sample_alert_data)
            
            assert alert is None
            mock_logger.info.assert_called_with("Alerta test_alert_001 silenciado")
    
    def test_process_alert_with_redis_cache(self, alert_manager, sample_alert_data):
        """Testa processamento de alerta com cache Redis"""
        with patch.object(alert_manager, '_should_silence', return_value=False), \
             patch('scripts.alert_manager.alert_counter'), \
             patch('scripts.alert_manager.active_alerts'), \
             patch('scripts.alert_manager.json.dumps') as mock_dumps:
            
            mock_dumps.return_value = '{"id": "test_alert_001"}'
            
            alert = alert_manager.process_alert(sample_alert_data)
            
            # Verifica cache Redis
            alert_manager.redis_client.setex.assert_called_with(
                "alert:test_alert_001",
                3600,  # 1 hora
                '{"id": "test_alert_001"}'
            )
    
    def test_should_silence_no_rules(self, alert_manager, sample_alert_data):
        """Testa verificação de silêncio sem regras"""
        alert_manager.silence_rules = []
        result = alert_manager._should_silence(sample_alert_data)
        assert result is False
    
    def test_should_silence_with_rules(self, alert_manager, sample_alert_data):
        """Testa verificação de silêncio com regras"""
        alert_manager.silence_rules = [{"matcher": "test"}]
        
        with patch.object(alert_manager, '_matches_silence_rule', return_value=True):
            result = alert_manager._should_silence(sample_alert_data)
            assert result is True
    
    def test_matches_silence_rule(self, alert_manager, sample_alert_data):
        """Testa correspondência de regra de silêncio"""
        rule = {"matcher": "test"}
        current_time = datetime.now()
        
        result = alert_manager._matches_silence_rule(sample_alert_data, rule, current_time)
        assert result is False  # Implementação simplificada sempre retorna False
    
    def test_send_notification_slack(self, alert_manager):
        """Testa envio de notificação Slack"""
        alert = Alert(
            id="test_alert_002",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        with patch.object(alert_manager, '_send_slack_notification', return_value=True):
            result = alert_manager.send_notification(alert, 'slack-notifications')
            assert result is True
    
    def test_send_notification_pagerduty(self, alert_manager):
        """Testa envio de notificação PagerDuty"""
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
        
        with patch.object(alert_manager, '_send_pagerduty_notification', return_value=True):
            result = alert_manager.send_notification(alert, 'pagerduty-critical')
            assert result is True
    
    def test_send_notification_email(self, alert_manager):
        """Testa envio de notificação Email"""
        alert = Alert(
            id="test_alert_004",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        with patch.object(alert_manager, '_send_email_notification', return_value=True):
            result = alert_manager.send_notification(alert, 'email-critical')
            assert result is True
    
    def test_send_notification_unknown_receiver(self, alert_manager):
        """Testa envio para receiver desconhecido"""
        alert = Alert(
            id="test_alert_005",
            name="Test Alert",
            severity="info",
            team="unknown",
            component="unknown",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        with patch('scripts.alert_manager.logger') as mock_logger:
            result = alert_manager.send_notification(alert, "unknown-receiver")
            assert result is False
            mock_logger.warning.assert_called_with("Receiver desconhecido: unknown-receiver")
    
    def test_send_slack_notification_success(self, alert_manager):
        """Testa envio bem-sucedido para Slack"""
        alert = Alert(
            id="test_alert_006",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        with patch('requests.post') as mock_post, \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = alert_manager._send_slack_notification(alert, '#alerts')
            
            assert result is True
            mock_post.assert_called_once()
            mock_logger.info.assert_called_with("Notificação Slack enviada para #alerts")
    
    def test_send_slack_notification_failure(self, alert_manager):
        """Testa falha no envio para Slack"""
        alert = Alert(
            id="test_alert_007",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        with patch('requests.post', side_effect=Exception("Network error")), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            result = alert_manager._send_slack_notification(alert, '#alerts')
            
            assert result is False
            mock_logger.error.assert_called()
    
    def test_send_pagerduty_notification_success(self, alert_manager):
        """Testa envio bem-sucedido para PagerDuty"""
        alert = Alert(
            id="test_alert_008",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        with patch('requests.post') as mock_post, \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = alert_manager._send_pagerduty_notification(alert)
            
            assert result is True
            mock_post.assert_called_once()
            mock_logger.info.assert_called_with("Notificação PagerDuty enviada")
    
    def test_send_email_notification_success(self, alert_manager):
        """Testa envio bem-sucedido por email"""
        alert = Alert(
            id="test_alert_009",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        with patch('smtplib.SMTP') as mock_smtp, \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            mock_server = Mock()
            mock_smtp.return_value = mock_server
            
            result = alert_manager._send_email_notification(alert, 'test@test.com')
            
            assert result is True
            mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with('test@test.com', 'password')
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
            mock_logger.info.assert_called_with("Email enviado para test@test.com")
    
    def test_resolve_alert_success(self, alert_manager):
        """Testa resolução bem-sucedida de alerta"""
        alert = Alert(
            id="test_alert_010",
            name="Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Test description",
            instance="test-instance",
            status="firing",
            created_at=datetime.now()
        )
        
        alert_manager.alerts["test_alert_010"] = alert
        
        with patch('scripts.alert_manager.active_alerts') as mock_active_alerts, \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            result = alert_manager.resolve_alert("test_alert_010", "test_user")
            
            assert result is True
            assert alert.status == "resolved"
            assert alert.resolved_at is not None
            assert alert.acknowledged_by == "test_user"
            
            mock_active_alerts.labels.assert_called_with(severity="critical")
            alert_manager.redis_client.delete.assert_called_with("alert:test_alert_010")
            mock_logger.info.assert_called_with("Alerta test_alert_010 resolvido por test_user")
    
    def test_resolve_alert_not_found(self, alert_manager):
        """Testa resolução de alerta inexistente"""
        with patch('scripts.alert_manager.logger') as mock_logger:
            result = alert_manager.resolve_alert("nonexistent_alert", "test_user")
            
            assert result is False
            mock_logger.warning.assert_called_with("Alerta nonexistent_alert não encontrado")
    
    def test_check_escalation(self, alert_manager):
        """Testa verificação de escalação"""
        # Cria alerta crítico
        alert = Alert(
            id="test_alert_011",
            name="Critical Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Critical issue",
            instance="api-server-1",
            status="firing",
            created_at=datetime.now() - timedelta(minutes=10)  # 10 minutos atrás
        )
        
        alert_manager.alerts["test_alert_011"] = alert
        
        with patch.object(alert_manager, 'send_notification', return_value=True), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            alert_manager.check_escalation()
            
            # Verifica se escalação foi executada
            assert alert.escalation_level > 0
            assert alert.last_notification is not None
            mock_logger.info.assert_called()
    
    def test_cleanup_old_alerts(self, alert_manager):
        """Testa limpeza de alertas antigos"""
        # Cria alerta antigo (25 horas atrás)
        old_alert = Alert(
            id="old_alert_001",
            name="Old Alert",
            severity="info",
            team="backend",
            component="api",
            description="Old alert",
            instance="api-server-1",
            status="firing",
            created_at=datetime.now() - timedelta(hours=25)
        )
        
        # Cria alerta recente (1 hora atrás)
        recent_alert = Alert(
            id="recent_alert_001",
            name="Recent Alert",
            severity="info",
            team="backend",
            component="api",
            description="Recent alert",
            instance="api-server-1",
            status="firing",
            created_at=datetime.now() - timedelta(hours=1)
        )
        
        alert_manager.alerts["old_alert_001"] = old_alert
        alert_manager.alerts["recent_alert_001"] = recent_alert
        
        with patch('scripts.alert_manager.logger') as mock_logger:
            alert_manager.cleanup_old_alerts(max_age_hours=24)
            
            # Verifica se alerta antigo foi removido
            assert "old_alert_001" not in alert_manager.alerts
            assert "recent_alert_001" in alert_manager.alerts
            
            alert_manager.redis_client.delete.assert_called_with("alert:old_alert_001")
            mock_logger.info.assert_called_with("Removidos 1 alertas antigos")
    
    def test_get_alert_statistics(self, alert_manager):
        """Testa obtenção de estatísticas de alertas"""
        # Cria alertas de teste
        alert1 = Alert(
            id="alert_001",
            name="Critical Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Critical issue",
            instance="api-server-1",
            status="firing",
            created_at=datetime.now()
        )
        
        alert2 = Alert(
            id="alert_002",
            name="Warning Alert",
            severity="warning",
            team="frontend",
            component="ui",
            description="Warning issue",
            instance="ui-server-1",
            status="resolved",
            created_at=datetime.now(),
            resolved_at=datetime.now()
        )
        
        alert_manager.alerts["alert_001"] = alert1
        alert_manager.alerts["alert_002"] = alert2
        
        stats = alert_manager.get_alert_statistics()
        
        assert stats['total_alerts'] == 2
        assert stats['active_alerts'] == 1
        assert stats['resolved_alerts'] == 1
        assert stats['by_severity']['critical'] == 1
        assert stats['by_severity']['warning'] == 1
        assert stats['by_team']['backend'] == 1
        assert stats['by_team']['frontend'] == 1
        assert stats['by_component']['api'] == 1
        assert stats['by_component']['ui'] == 1
    
    def test_run_scheduled_tasks(self, alert_manager):
        """Testa execução de tarefas agendadas"""
        with patch.object(alert_manager, 'check_escalation') as mock_check, \
             patch.object(alert_manager, 'cleanup_old_alerts') as mock_cleanup, \
             patch.object(alert_manager, 'get_alert_statistics', return_value={'total': 0}), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            alert_manager.run_scheduled_tasks()
            
            mock_check.assert_called_once()
            mock_cleanup.assert_called_once()
            mock_logger.info.assert_called()
    
    def test_run_scheduled_tasks_exception(self, alert_manager):
        """Testa tratamento de exceção em tarefas agendadas"""
        with patch.object(alert_manager, 'check_escalation', side_effect=Exception("Test error")), \
             patch('scripts.alert_manager.logger') as mock_logger:
            
            alert_manager.run_scheduled_tasks()
            
            mock_logger.error.assert_called_with("Erro nas tarefas agendadas: Test error")
    
    def test_notification_config_structure(self, alert_manager):
        """Testa estrutura das configurações de notificação"""
        for config_type, config in alert_manager.notification_configs.items():
            assert hasattr(config, 'type')
            assert hasattr(config, 'config')
            assert hasattr(config, 'enabled')
            assert hasattr(config, 'retry_count')
            assert hasattr(config, 'retry_delay')
            assert isinstance(config.type, str)
            assert isinstance(config.config, dict)
            assert isinstance(config.enabled, bool)
            assert isinstance(config.retry_count, int)
            assert isinstance(config.retry_delay, int)
    
    def test_alert_dataclass_structure(self):
        """Testa estrutura da dataclass Alert"""
        alert = Alert(
            id="test_alert_012",
            name="Test Alert",
            severity="info",
            team="test",
            component="test",
            description="Test",
            instance="test",
            status="firing",
            created_at=datetime.now()
        )
        
        assert hasattr(alert, 'id')
        assert hasattr(alert, 'name')
        assert hasattr(alert, 'severity')
        assert hasattr(alert, 'team')
        assert hasattr(alert, 'component')
        assert hasattr(alert, 'description')
        assert hasattr(alert, 'instance')
        assert hasattr(alert, 'status')
        assert hasattr(alert, 'created_at')
        assert hasattr(alert, 'resolved_at')
        assert hasattr(alert, 'acknowledged_by')
        assert hasattr(alert, 'acknowledged_at')
        assert hasattr(alert, 'escalation_level')
        assert hasattr(alert, 'notification_count')
        assert hasattr(alert, 'last_notification')
    
    def test_alert_manager_without_redis(self):
        """Testa AlertManager sem Redis disponível"""
        with patch('scripts.alert_manager.open', create=True), \
             patch('yaml.safe_load', return_value={'global': {}, 'silence_rules': []}), \
             patch('redis.Redis', side_effect=Exception("Redis unavailable")), \
             patch('scripts.alert_manager.start_http_server'):
            
            manager = AlertManager("test_config.yaml")
            assert manager.redis_client is None
    
    def test_alert_manager_metrics_integration(self, alert_manager):
        """Testa integração com métricas Prometheus"""
        # Verifica se as métricas estão definidas
        assert hasattr(alert_manager, 'alert_counter')
        assert hasattr(alert_manager, 'alert_duration')
        assert hasattr(alert_manager, 'active_alerts')
        
        # Testa incremento de métricas
        with patch('scripts.alert_manager.alert_counter') as mock_counter, \
             patch('scripts.alert_manager.active_alerts') as mock_active_alerts:
            
            alert_data = {
                "id": "test_alert_013",
                "name": "Test Alert",
                "severity": "critical",
                "team": "backend",
                "component": "api",
                "description": "Test",
                "instance": "test"
            }
            
            with patch.object(alert_manager, '_should_silence', return_value=False):
                alert_manager.process_alert(alert_data)
                
                mock_counter.labels.assert_called_with(
                    severity="critical",
                    team="backend",
                    component="api"
                )
                mock_active_alerts.labels.assert_called_with(severity="critical")


class TestAlertManagerIntegration:
    """Testes de integração para o AlertManager"""
    
    @pytest.fixture
    def integration_alert_manager(self):
        """Fixture para testes de integração"""
        with patch('scripts.alert_manager.open', create=True), \
             patch('yaml.safe_load', return_value={
                 'global': {
                     'slack_api_url': 'https://hooks.slack.com/test',
                     'pagerduty_url': 'https://events.pagerduty.com/test',
                     'smtp_smarthost': 'smtp.gmail.com:587',
                     'smtp_auth_username': 'test@test.com',
                     'smtp_auth_password': 'password',
                     'smtp_from': 'alerts@test.com'
                 },
                 'silence_rules': []
             }), \
             patch('redis.Redis'), \
             patch('scripts.alert_manager.start_http_server'):
            
            manager = AlertManager("test_config.yaml")
            manager.redis_client = Mock()
            manager.redis_client.ping.return_value = True
            return manager
    
    def test_full_alert_lifecycle(self, integration_alert_manager):
        """Testa ciclo completo de vida de um alerta"""
        # 1. Processa alerta
        alert_data = {
            "id": "lifecycle_alert_001",
            "name": "Lifecycle Test Alert",
            "severity": "critical",
            "team": "backend",
            "component": "api",
            "description": "Lifecycle test",
            "instance": "api-server-1"
        }
        
        with patch.object(integration_alert_manager, '_should_silence', return_value=False), \
             patch('scripts.alert_manager.alert_counter'), \
             patch('scripts.alert_manager.active_alerts'):
            
            alert = integration_alert_manager.process_alert(alert_data)
            assert alert is not None
            assert alert.status == "firing"
            
            # 2. Verifica escalação
            alert.created_at = datetime.now() - timedelta(minutes=10)
            
            with patch.object(integration_alert_manager, 'send_notification', return_value=True):
                integration_alert_manager.check_escalation()
                assert alert.escalation_level > 0
            
            # 3. Resolve alerta
            with patch('scripts.alert_manager.active_alerts'):
                result = integration_alert_manager.resolve_alert(alert.id, "test_user")
                assert result is True
                assert alert.status == "resolved"
                assert alert.resolved_at is not None
                assert alert.acknowledged_by == "test_user"
    
    def test_multiple_alerts_processing(self, integration_alert_manager):
        """Testa processamento de múltiplos alertas"""
        alert_data_list = [
            {
                "id": f"multi_alert_{i:03d}",
                "name": f"Multi Alert {i}",
                "severity": "critical" if i % 2 == 0 else "warning",
                "team": "backend" if i % 3 == 0 else "frontend",
                "component": "api" if i % 2 == 0 else "ui",
                "description": f"Multi alert {i}",
                "instance": f"server-{i}"
            }
            for i in range(1, 6)
        ]
        
        with patch.object(integration_alert_manager, '_should_silence', return_value=False), \
             patch('scripts.alert_manager.alert_counter'), \
             patch('scripts.alert_manager.active_alerts'):
            
            alerts = []
            for alert_data in alert_data_list:
                alert = integration_alert_manager.process_alert(alert_data)
                alerts.append(alert)
            
            assert len(alerts) == 5
            assert len(integration_alert_manager.alerts) == 5
            
            # Verifica estatísticas
            stats = integration_alert_manager.get_alert_statistics()
            assert stats['total_alerts'] == 5
            assert stats['active_alerts'] == 5
            assert stats['by_severity']['critical'] == 3
            assert stats['by_severity']['warning'] == 2
            assert stats['by_team']['backend'] == 2
            assert stats['by_team']['frontend'] == 3
            assert stats['by_component']['api'] == 3
            assert stats['by_component']['ui'] == 2
    
    def test_escalation_policy_execution(self, integration_alert_manager):
        """Testa execução completa de política de escalação"""
        # Cria alerta crítico
        alert = Alert(
            id="escalation_test_001",
            name="Escalation Test Alert",
            severity="critical",
            team="backend",
            component="api",
            description="Escalation test",
            instance="api-server-1",
            status="firing",
            created_at=datetime.now() - timedelta(minutes=20)  # 20 minutos atrás
        )
        
        integration_alert_manager.alerts[alert.id] = alert
        
        # Simula envio de notificações
        with patch.object(integration_alert_manager, 'send_notification') as mock_send:
            mock_send.return_value = True
            
            integration_alert_manager.check_escalation()
            
            # Verifica se todas as escalações foram executadas
            assert alert.escalation_level == 3  # Todas as 3 escalações
            assert mock_send.call_count == 3
            
            # Verifica ordem das escalações
            calls = mock_send.call_args_list
            assert calls[0][0][1] == 'pagerduty-critical'  # Primeira escalação
            assert calls[1][0][1] == 'email-critical'      # Segunda escalação
            assert calls[2][0][1] == 'slack-notifications' # Terceira escalação


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 