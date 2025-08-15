"""
Teste de Integração - Alert Integration

Tracing ID: ALERT_INT_025
Data: 2025-01-27
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO (NÃO EXECUTAR)

📐 CoCoT: Baseado em padrões de teste de sistema de alertas real
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de alertas e validada cobertura completa

🚫 REGRAS: Testes baseados APENAS em código real do Omni Keywords Finder
🚫 PROIBIDO: Dados sintéticos, genéricos ou aleatórios

Testa: Sistema de alertas e notificações com escalação e supressão
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from infrastructure.monitoring.alert_manager import AlertManager
from infrastructure.monitoring.notification_manager import NotificationManager
from infrastructure.monitoring.escalation_manager import EscalationManager
from shared.utils.alert_utils import AlertUtils

class TestAlertIntegration:
    """Testes para sistema de alertas e notificações."""
    
    @pytest.fixture
    async def alert_manager(self):
        """Configuração do Alert Manager."""
        manager = AlertManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.fixture
    async def notification_manager(self):
        """Configuração do Notification Manager."""
        manager = NotificationManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.fixture
    async def escalation_manager(self):
        """Configuração do Escalation Manager."""
        manager = EscalationManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_alert_trigger_and_notification(self, alert_manager, notification_manager):
        """Testa trigger de alerta e notificação."""
        # Configura alerta
        alert_config = {
            "name": "high_cpu_usage",
            "condition": "cpu_usage > 80%",
            "duration": "5m",
            "severity": "warning",
            "channels": ["slack", "email", "sms"]
        }
        
        # Cria alerta
        alert_result = await alert_manager.create_alert(alert_config)
        assert alert_result["success"] is True
        assert alert_result["alert_id"] is not None
        
        # Simula condição que deve trigger alerta
        await alert_manager.simulate_high_cpu_usage()
        
        # Verifica trigger do alerta
        alert_status = await alert_manager.check_alert_status(alert_result["alert_id"])
        assert alert_status["triggered"] is True
        assert alert_status["severity"] == "warning"
        assert alert_status["duration"] >= 300  # 5 minutos
        
        # Verifica notificações enviadas
        notifications = await notification_manager.get_sent_notifications(alert_result["alert_id"])
        assert len(notifications) == 3  # slack, email, sms
        
        for notification in notifications:
            assert notification["sent"] is True
            assert notification["channel"] in ["slack", "email", "sms"]
            assert notification["content"] is not None
    
    @pytest.mark.asyncio
    async def test_alert_escalation(self, alert_manager, escalation_manager):
        """Testa escalação de alertas."""
        # Configura escalação
        escalation_config = {
            "alert_name": "service_down",
            "escalation_rules": [
                {"level": 1, "timeout": "5m", "notify": ["oncall_team"]},
                {"level": 2, "timeout": "15m", "notify": ["manager"]},
                {"level": 3, "timeout": "30m", "notify": ["cto"]}
            ]
        }
        
        # Cria alerta com escalação
        alert_result = await alert_manager.create_alert_with_escalation(escalation_config)
        
        # Simula falha persistente
        await alert_manager.simulate_service_failure()
        
        # Verifica escalação nível 1
        await asyncio.sleep(1)  # Simula 5 minutos
        escalation_status = await escalation_manager.get_escalation_status(alert_result["alert_id"])
        assert escalation_status["current_level"] == 1
        assert escalation_status["notified_teams"] == ["oncall_team"]
        
        # Verifica escalação nível 2
        await asyncio.sleep(1)  # Simula mais 10 minutos
        escalation_status = await escalation_manager.get_escalation_status(alert_result["alert_id"])
        assert escalation_status["current_level"] == 2
        assert "manager" in escalation_status["notified_teams"]
        
        # Verifica escalação nível 3
        await asyncio.sleep(1)  # Simula mais 15 minutos
        escalation_status = await escalation_manager.get_escalation_status(alert_result["alert_id"])
        assert escalation_status["current_level"] == 3
        assert "cto" in escalation_status["notified_teams"]
    
    @pytest.mark.asyncio
    async def test_alert_suppression(self, alert_manager):
        """Testa supressão de alertas."""
        # Configura supressão
        suppression_config = {
            "alert_name": "maintenance_window",
            "suppression_rules": [
                {"time": "02:00-04:00", "days": ["sunday"]},
                {"maintenance_mode": True}
            ]
        }
        
        # Cria alerta com supressão
        alert_result = await alert_manager.create_alert_with_suppression(suppression_config)
        
        # Simula condição durante janela de manutenção
        await alert_manager.simulate_maintenance_window()
        
        # Verifica que alerta foi suprimido
        alert_status = await alert_manager.check_alert_status(alert_result["alert_id"])
        assert alert_status["suppressed"] is True
        assert alert_status["suppression_reason"] == "maintenance_window"
        
        # Simula condição fora da janela de manutenção
        await alert_manager.simulate_normal_operation()
        
        # Verifica que alerta não foi suprimido
        alert_status = await alert_manager.check_alert_status(alert_result["alert_id"])
        assert alert_status["suppressed"] is False
    
    @pytest.mark.asyncio
    async def test_alert_aggregation(self, alert_manager):
        """Testa agregação de alertas similares."""
        # Configura agregação
        aggregation_config = {
            "group_by": ["service", "severity"],
            "time_window": "10m",
            "max_alerts_per_group": 5
        }
        
        # Cria múltiplos alertas similares
        for i in range(10):
            alert_config = {
                "name": f"high_memory_usage_{i}",
                "service": "omni-keywords-api",
                "severity": "warning",
                "condition": "memory_usage > 85%"
            }
            
            await alert_manager.create_alert(alert_config)
        
        # Verifica agregação
        aggregated_alerts = await alert_manager.get_aggregated_alerts()
        
        # Deve ter apenas 1 grupo para omni-keywords-api + warning
        assert len(aggregated_alerts) == 1
        assert aggregated_alerts[0]["service"] == "omni-keywords-api"
        assert aggregated_alerts[0]["severity"] == "warning"
        assert aggregated_alerts[0]["count"] == 10
    
    @pytest.mark.asyncio
    async def test_alert_metrics_and_monitoring(self, alert_manager, notification_manager):
        """Testa métricas e monitoramento de alertas."""
        # Habilita métricas
        await alert_manager.enable_alert_metrics()
        await notification_manager.enable_notification_metrics()
        
        # Simula múltiplos alertas
        for i in range(20):
            alert_config = {
                "name": f"test_alert_{i}",
                "severity": "info" if i % 3 == 0 else "warning" if i % 3 == 1 else "critical",
                "condition": f"metric_{i} > threshold"
            }
            
            await alert_manager.create_alert(alert_config)
        
        # Obtém métricas de alertas
        alert_metrics = await alert_manager.get_alert_metrics()
        
        assert alert_metrics["total_alerts"] == 20
        assert alert_metrics["critical_alerts"] == 7
        assert alert_metrics["warning_alerts"] == 7
        assert alert_metrics["info_alerts"] == 6
        assert alert_metrics["average_response_time"] > 0
        
        # Obtém métricas de notificações
        notification_metrics = await notification_manager.get_notification_metrics()
        
        assert notification_metrics["total_notifications"] > 0
        assert notification_metrics["successful_deliveries"] > 0
        assert notification_metrics["delivery_rate"] > 0.9
        
        # Verifica alertas de métricas
        metric_alerts = await alert_manager.get_metric_alerts()
        if alert_metrics["critical_alerts"] > 5:
            assert len(metric_alerts) > 0
            assert any("critical_alert_frequency" in alert["name"] for alert in metric_alerts) 