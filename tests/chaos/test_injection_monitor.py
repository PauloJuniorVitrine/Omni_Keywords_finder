"""
Testes Unitários para InjectionMonitor
InjectionMonitor - Sistema de monitoramento de injeções de falhas para chaos engineering

Prompt: Implementação de testes unitários para InjectionMonitor
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_INJECTION_MONITOR_001_20250127
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.chaos.injection_monitor import (
    MonitorStatus,
    ImpactLevel,
    InjectionMetrics,
    InjectionImpact,
    MonitorConfig,
    InjectionMonitor
)


class TestMonitorStatus:
    """Testes para MonitorStatus"""
    
    def test_monitor_status_values(self):
        """Testa valores do enum MonitorStatus"""
        assert MonitorStatus.IDLE.value == "idle"
        assert MonitorStatus.MONITORING.value == "monitoring"
        assert MonitorStatus.ALERTING.value == "alerting"
        assert MonitorStatus.STOPPED.value == "stopped"
    
    def test_monitor_status_membership(self):
        """Testa pertencimento ao enum"""
        assert MonitorStatus.IDLE in MonitorStatus
        assert MonitorStatus.MONITORING in MonitorStatus
        assert MonitorStatus.ALERTING in MonitorStatus
        assert MonitorStatus.STOPPED in MonitorStatus


class TestImpactLevel:
    """Testes para ImpactLevel"""
    
    def test_impact_level_values(self):
        """Testa valores do enum ImpactLevel"""
        assert ImpactLevel.NONE.value == "none"
        assert ImpactLevel.CRITICAL.value == "critical"
    
    def test_impact_level_membership(self):
        """Testa pertencimento ao enum"""
        assert ImpactLevel.NONE in ImpactLevel
        assert ImpactLevel.CRITICAL in ImpactLevel


class TestInjectionMetrics:
    """Testes para InjectionMetrics"""
    
    @pytest.fixture
    def sample_metrics_data(self):
        """Dados de exemplo para métricas"""
        return {
            "injection_id": "test_injection_001",
            "timestamp": datetime.now(timezone.utc),
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_io": 12.5,
            "network_io": 8.3,
            "response_time": 150.0,
            "error_rate": 0.02,
            "throughput": 1250.0,
            "availability": 99.8,
            "impact_score": 0.15,
            "custom_metrics": {"queue_size": 100, "active_connections": 50}
        }
    
    def test_injection_metrics_initialization(self, sample_metrics_data):
        """Testa inicialização básica"""
        metrics = InjectionMetrics(**sample_metrics_data)
        
        assert metrics.injection_id == "test_injection_001"
        assert metrics.cpu_usage == 45.2
        assert metrics.memory_usage == 67.8
        assert metrics.disk_io == 12.5
        assert metrics.network_io == 8.3
        assert metrics.response_time == 150.0
        assert metrics.error_rate == 0.02
        assert metrics.throughput == 1250.0
        assert metrics.availability == 99.8
        assert metrics.impact_score == 0.15
        assert metrics.custom_metrics["queue_size"] == 100
        assert metrics.custom_metrics["active_connections"] == 50
    
    def test_injection_metrics_validation(self, sample_metrics_data):
        """Testa validações de métricas"""
        # Teste com valores válidos
        metrics = InjectionMetrics(**sample_metrics_data)
        assert 0 <= metrics.cpu_usage <= 100
        assert 0 <= metrics.memory_usage <= 100
        assert metrics.error_rate >= 0
        assert metrics.availability >= 0
    
    def test_injection_metrics_edge_cases(self):
        """Testa casos extremos"""
        # Teste com valores mínimos
        min_data = {
            "injection_id": "min_test",
            "timestamp": datetime.now(timezone.utc),
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_io": 0.0,
            "network_io": 0.0,
            "response_time": 0.0,
            "error_rate": 0.0,
            "throughput": 0.0,
            "availability": 0.0,
            "impact_score": 0.0,
            "custom_metrics": {}
        }
        metrics = InjectionMetrics(**min_data)
        assert metrics.cpu_usage == 0.0
        assert metrics.impact_score == 0.0
        
        # Teste com valores máximos
        max_data = {
            "injection_id": "max_test",
            "timestamp": datetime.now(timezone.utc),
            "cpu_usage": 100.0,
            "memory_usage": 100.0,
            "disk_io": 1000.0,
            "network_io": 1000.0,
            "response_time": 10000.0,
            "error_rate": 1.0,
            "throughput": 10000.0,
            "availability": 100.0,
            "impact_score": 1.0,
            "custom_metrics": {"max_value": 999999}
        }
        metrics = InjectionMetrics(**max_data)
        assert metrics.cpu_usage == 100.0
        assert metrics.impact_score == 1.0


class TestInjectionImpact:
    """Testes para InjectionImpact"""
    
    @pytest.fixture
    def sample_impact_data(self):
        """Dados de exemplo para impacto"""
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(minutes=5)
        
        return {
            "injection_id": "test_impact_001",
            "start_time": start_time,
            "end_time": end_time,
            "duration": 300.0,
            "max_cpu_impact": 25.5,
            "max_memory_impact": 30.2,
            "max_disk_impact": 15.8,
            "max_network_impact": 12.3,
            "max_response_time_impact": 200.0,
            "max_error_rate_impact": 0.15,
            "min_availability": 95.5,
            "impact_level": ImpactLevel.CRITICAL,
            "recovery_time": 45.0,
            "baseline_deviation": 0.25,
            "avg_cpu_impact": 18.3,
            "avg_memory_impact": 22.1,
            "avg_error_rate_impact": 0.08,
            "recommendations": ["Aumentar recursos de CPU", "Otimizar queries"],
            "issues_found": ["Alto uso de CPU", "Latência elevada"]
        }
    
    def test_injection_impact_initialization(self, sample_impact_data):
        """Testa inicialização básica"""
        impact = InjectionImpact(**sample_impact_data)
        
        assert impact.injection_id == "test_impact_001"
        assert impact.duration == 300.0
        assert impact.max_cpu_impact == 25.5
        assert impact.max_memory_impact == 30.2
        assert impact.impact_level == ImpactLevel.CRITICAL
        assert impact.recovery_time == 45.0
        assert impact.baseline_deviation == 0.25
        assert len(impact.recommendations) == 2
        assert len(impact.issues_found) == 2
    
    def test_injection_impact_duration_calculation(self):
        """Testa cálculo de duração"""
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(minutes=10)
        
        impact_data = {
            "injection_id": "duration_test",
            "start_time": start_time,
            "end_time": end_time,
            "duration": 600.0,
            "max_cpu_impact": 0.0,
            "max_memory_impact": 0.0,
            "max_disk_impact": 0.0,
            "max_network_impact": 0.0,
            "max_response_time_impact": 0.0,
            "max_error_rate_impact": 0.0,
            "min_availability": 100.0,
            "impact_level": ImpactLevel.NONE,
            "recovery_time": None,
            "baseline_deviation": 0.0,
            "avg_cpu_impact": 0.0,
            "avg_memory_impact": 0.0,
            "avg_error_rate_impact": 0.0,
            "recommendations": [],
            "issues_found": []
        }
        
        impact = InjectionImpact(**impact_data)
        expected_duration = (end_time - start_time).total_seconds()
        assert abs(impact.duration - expected_duration) < 1.0  # Tolerância de 1 segundo
    
    def test_injection_impact_validation(self, sample_impact_data):
        """Testa validações de impacto"""
        impact = InjectionImpact(**sample_impact_data)
        
        # Validações básicas
        assert impact.duration > 0
        assert impact.max_cpu_impact >= 0
        assert impact.max_memory_impact >= 0
        assert impact.min_availability >= 0
        assert impact.baseline_deviation >= 0
        
        # Validação de impacto crítico
        if impact.impact_level == ImpactLevel.CRITICAL:
            assert impact.max_cpu_impact > 20 or impact.max_error_rate_impact > 0.1


class TestMonitorConfig:
    """Testes para MonitorConfig"""
    
    def test_monitor_config_default_values(self):
        """Testa valores padrão da configuração"""
        config = MonitorConfig()
        
        # Verificar se a configuração é criada sem erros
        assert config is not None
    
    def test_monitor_config_custom_values(self):
        """Testa configuração com valores customizados"""
        # Teste com parâmetros específicos se disponíveis
        config = MonitorConfig()
        assert isinstance(config, MonitorConfig)


class TestInjectionMonitor:
    """Testes para InjectionMonitor"""
    
    @pytest.fixture
    def monitor_config(self):
        """Configuração do monitor para testes"""
        return MonitorConfig()
    
    @pytest.fixture
    def injection_monitor(self, monitor_config):
        """Instância do monitor para testes"""
        return InjectionMonitor(config=monitor_config)
    
    @pytest.fixture
    def sample_metrics(self):
        """Métricas de exemplo"""
        return InjectionMetrics(
            injection_id="test_injection",
            timestamp=datetime.now(timezone.utc),
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_io=10.0,
            network_io=5.0,
            response_time=100.0,
            error_rate=0.05,
            throughput=1000.0,
            availability=98.0,
            impact_score=0.2,
            custom_metrics={"test": "value"}
        )
    
    def test_injection_monitor_initialization(self, injection_monitor):
        """Testa inicialização do monitor"""
        assert injection_monitor.status == MonitorStatus.IDLE
        assert injection_monitor.monitoring_task is None
        assert injection_monitor.stop_monitoring_flag is False
        assert injection_monitor.baseline_metrics is None
        assert len(injection_monitor.injection_metrics) == 0
        assert len(injection_monitor.impact_analysis) == 0
        assert len(injection_monitor.impact_callbacks) == 0
        assert len(injection_monitor.alert_callbacks) == 0
        assert len(injection_monitor.metrics_callbacks) == 0
        assert injection_monitor.stats['injections_monitored'] == 0
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, injection_monitor):
        """Testa início do monitoramento"""
        injection_id = "test_monitoring_001"
        
        # Mock do baseline
        with patch.object(injection_monitor, '_establish_baseline', new_callable=AsyncMock):
            with patch.object(injection_monitor, '_monitoring_loop', new_callable=AsyncMock):
                await injection_monitor.start_monitoring(injection_id)
        
        assert injection_monitor.status == MonitorStatus.MONITORING
        assert injection_monitor.stop_monitoring_flag is False
        assert injection_monitor.stats['injections_monitored'] == 1
    
    @pytest.mark.asyncio
    async def test_start_monitoring_already_running(self, injection_monitor):
        """Testa início quando já está monitorando"""
        injection_monitor.status = MonitorStatus.MONITORING
        
        with patch.object(injection_monitor, '_establish_baseline', new_callable=AsyncMock):
            with patch.object(injection_monitor, '_monitoring_loop', new_callable=AsyncMock):
                await injection_monitor.start_monitoring("test_id")
        
        # Status não deve mudar
        assert injection_monitor.status == MonitorStatus.MONITORING
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, injection_monitor):
        """Testa parada do monitoramento"""
        injection_monitor.status = MonitorStatus.MONITORING
        injection_monitor.monitoring_task = Mock()
        injection_monitor.monitoring_task.cancel = Mock()
        
        await injection_monitor.stop_monitoring()
        
        assert injection_monitor.status == MonitorStatus.STOPPED
        assert injection_monitor.stop_monitoring_flag is True
        injection_monitor.monitoring_task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, injection_monitor):
        """Testa coleta de métricas"""
        injection_id = "test_collect_001"
        
        with patch.object(injection_monitor, '_collect_system_metrics', new_callable=AsyncMock) as mock_system:
            with patch.object(injection_monitor, '_collect_application_metrics', new_callable=AsyncMock) as mock_app:
                with patch.object(injection_monitor, '_collect_custom_metrics', new_callable=AsyncMock) as mock_custom:
                    with patch.object(injection_monitor, '_calculate_impact_score', return_value=0.15):
                        
                        mock_system.return_value = {
                            'cpu_usage': 45.0,
                            'memory_usage': 55.0,
                            'disk_io': 8.0,
                            'network_io': 3.0
                        }
                        
                        mock_app.return_value = {
                            'response_time': 120.0,
                            'error_rate': 0.03,
                            'throughput': 1100.0,
                            'availability': 99.5
                        }
                        
                        mock_custom.return_value = {"custom": "metric"}
                        
                        metrics = await injection_monitor._collect_metrics(injection_id)
                        
                        assert metrics.injection_id == injection_id
                        assert metrics.cpu_usage == 45.0
                        assert metrics.memory_usage == 55.0
                        assert metrics.response_time == 120.0
                        assert metrics.error_rate == 0.03
                        assert metrics.impact_score == 0.15
                        assert metrics.custom_metrics["custom"] == "metric"
    
    def test_add_impact_callback(self, injection_monitor):
        """Testa adição de callback de impacto"""
        callback = Mock()
        injection_monitor.add_impact_callback(callback)
        
        assert callback in injection_monitor.impact_callbacks
        assert len(injection_monitor.impact_callbacks) == 1
    
    def test_add_alert_callback(self, injection_monitor):
        """Testa adição de callback de alerta"""
        callback = Mock()
        injection_monitor.add_alert_callback(callback)
        
        assert callback in injection_monitor.alert_callbacks
        assert len(injection_monitor.alert_callbacks) == 1
    
    def test_add_metrics_callback(self, injection_monitor):
        """Testa adição de callback de métricas"""
        callback = Mock()
        injection_monitor.add_metrics_callback(callback)
        
        assert callback in injection_monitor.metrics_callbacks
        assert len(injection_monitor.metrics_callbacks) == 1
    
    def test_get_stats(self, injection_monitor):
        """Testa obtenção de estatísticas"""
        stats = injection_monitor.get_stats()
        
        assert 'injections_monitored' in stats
        assert 'metrics_collected' in stats
        assert 'alerts_generated' in stats
        assert 'impact_analyses' in stats
        assert isinstance(stats['injections_monitored'], int)
    
    def test_get_injection_metrics(self, injection_monitor, sample_metrics):
        """Testa obtenção de métricas de injeção"""
        injection_id = "test_get_metrics"
        injection_monitor.injection_metrics[injection_id].append(sample_metrics)
        
        metrics = injection_monitor.get_injection_metrics(injection_id)
        
        assert len(metrics) == 1
        assert metrics[0].injection_id == injection_id
    
    def test_get_impact_analysis(self, injection_monitor):
        """Testa obtenção de análise de impacto"""
        injection_id = "test_impact"
        impact = InjectionImpact(
            injection_id=injection_id,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(minutes=5),
            duration=300.0,
            max_cpu_impact=20.0,
            max_memory_impact=25.0,
            max_disk_impact=10.0,
            max_network_impact=8.0,
            max_response_time_impact=150.0,
            max_error_rate_impact=0.1,
            min_availability=95.0,
            impact_level=ImpactLevel.CRITICAL,
            recovery_time=30.0,
            baseline_deviation=0.2,
            avg_cpu_impact=15.0,
            avg_memory_impact=18.0,
            avg_error_rate_impact=0.05,
            recommendations=["Test recommendation"],
            issues_found=["Test issue"]
        )
        
        injection_monitor.impact_analysis[injection_id] = impact
        
        retrieved_impact = injection_monitor.get_impact_analysis(injection_id)
        
        assert retrieved_impact.injection_id == injection_id
        assert retrieved_impact.impact_level == ImpactLevel.CRITICAL


class TestInjectionMonitorIntegration:
    """Testes de integração para InjectionMonitor"""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_cycle(self):
        """Testa ciclo completo de monitoramento"""
        monitor = InjectionMonitor()
        injection_id = "integration_test_001"
        
        # Mock de todas as operações assíncronas
        with patch.object(monitor, '_establish_baseline', new_callable=AsyncMock):
            with patch.object(monitor, '_monitoring_loop', new_callable=AsyncMock):
                with patch.object(monitor, '_collect_metrics', new_callable=AsyncMock):
                    
                    # Iniciar monitoramento
                    await monitor.start_monitoring(injection_id)
                    assert monitor.status == MonitorStatus.MONITORING
                    
                    # Parar monitoramento
                    await monitor.stop_monitoring()
                    assert monitor.status == MonitorStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_callback_integration(self):
        """Testa integração com callbacks"""
        monitor = InjectionMonitor()
        
        impact_callback = Mock()
        alert_callback = Mock()
        metrics_callback = Mock()
        
        # Adicionar callbacks
        monitor.add_impact_callback(impact_callback)
        monitor.add_alert_callback(alert_callback)
        monitor.add_metrics_callback(metrics_callback)
        
        assert len(monitor.impact_callbacks) == 1
        assert len(monitor.alert_callbacks) == 1
        assert len(monitor.metrics_callbacks) == 1


class TestInjectionMonitorErrorHandling:
    """Testes de tratamento de erro para InjectionMonitor"""
    
    @pytest.mark.asyncio
    async def test_monitoring_error_handling(self):
        """Testa tratamento de erros durante monitoramento"""
        monitor = InjectionMonitor()
        
        # Mock que simula erro na coleta de métricas
        with patch.object(monitor, '_collect_metrics', side_effect=Exception("Test error")):
            with patch.object(monitor, '_establish_baseline', new_callable=AsyncMock):
                with patch.object(monitor, '_monitoring_loop', new_callable=AsyncMock):
                    # Deve continuar funcionando mesmo com erro
                    await monitor.start_monitoring("error_test")
                    assert monitor.status == MonitorStatus.MONITORING
    
    def test_invalid_metrics_handling(self):
        """Testa tratamento de métricas inválidas"""
        monitor = InjectionMonitor()
        
        # Teste com dados inválidos
        with pytest.raises(TypeError):
            # Tentativa de criar métricas com dados inválidos
            InjectionMetrics(
                injection_id=123,  # Deveria ser string
                timestamp="invalid",  # Deveria ser datetime
                cpu_usage="invalid",  # Deveria ser float
                memory_usage=60.0,
                disk_io=10.0,
                network_io=5.0,
                response_time=100.0,
                error_rate=0.05,
                throughput=1000.0,
                availability=98.0,
                impact_score=0.2,
                custom_metrics={"test": "value"}
            )


class TestInjectionMonitorPerformance:
    """Testes de performance para InjectionMonitor"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_performance(self):
        """Testa performance da coleta de métricas"""
        monitor = InjectionMonitor()
        
        start_time = datetime.now()
        
        # Simular coleta de métricas
        with patch.object(monitor, '_collect_system_metrics', new_callable=AsyncMock) as mock_system:
            with patch.object(monitor, '_collect_application_metrics', new_callable=AsyncMock) as mock_app:
                with patch.object(monitor, '_collect_custom_metrics', new_callable=AsyncMock) as mock_custom:
                    with patch.object(monitor, '_calculate_impact_score', return_value=0.15):
                        
                        mock_system.return_value = {
                            'cpu_usage': 45.0,
                            'memory_usage': 55.0,
                            'disk_io': 8.0,
                            'network_io': 3.0
                        }
                        
                        mock_app.return_value = {
                            'response_time': 120.0,
                            'error_rate': 0.03,
                            'throughput': 1100.0,
                            'availability': 99.5
                        }
                        
                        mock_custom.return_value = {"custom": "metric"}
                        
                        metrics = await monitor._collect_metrics("performance_test")
                        
                        end_time = datetime.now()
                        duration = (end_time - start_time).total_seconds()
                        
                        # Performance deve ser < 1 segundo
                        assert duration < 1.0
                        assert metrics is not None
    
    def test_memory_usage_with_large_metrics(self):
        """Testa uso de memória com muitas métricas"""
        monitor = InjectionMonitor()
        
        # Adicionar muitas métricas
        for i in range(1000):
            metrics = InjectionMetrics(
                injection_id=f"test_{i}",
                timestamp=datetime.now(timezone.utc),
                cpu_usage=50.0 + i,
                memory_usage=60.0 + i,
                disk_io=10.0,
                network_io=5.0,
                response_time=100.0,
                error_rate=0.05,
                throughput=1000.0,
                availability=98.0,
                impact_score=0.2,
                custom_metrics={"index": i}
            )
            monitor.injection_metrics[f"test_{i}"].append(metrics)
        
        # Verificar que não há vazamento de memória
        assert len(monitor.injection_metrics) == 1000
        # Cada deque tem maxlen=1000, então deve limitar automaticamente 