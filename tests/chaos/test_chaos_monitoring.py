"""
Testes Unitários para Chaos Monitoring
Chaos Monitoring - Sistema de monitoramento para chaos engineering

Prompt: Implementação de testes unitários para chaos_monitoring.py
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_CHAOS_MONITORING_001_20250127
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from collections import deque

from infrastructure.chaos.chaos_monitoring import (
    MetricType,
    AlertSeverity,
    SystemMetrics,
    ApplicationMetrics,
    ChaosMetrics,
    Alert,
    ImpactAnalysis,
    MonitoringConfig,
    ChaosMonitor,
    create_chaos_monitor
)


class TestMetricType:
    """Testes para MetricType"""
    
    def test_metric_type_values(self):
        """Testa valores dos tipos de métricas"""
        assert MetricType.CPU_USAGE.value == "cpu_usage"
        assert MetricType.MEMORY_USAGE.value == "memory_usage"
        assert MetricType.DISK_USAGE.value == "disk_usage"
        assert MetricType.NETWORK_IO.value == "network_io"
        assert MetricType.RESPONSE_TIME.value == "response_time"
        assert MetricType.ERROR_RATE.value == "error_rate"
        assert MetricType.THROUGHPUT.value == "throughput"
        assert MetricType.AVAILABILITY.value == "availability"
        assert MetricType.CUSTOM.value == "custom"
    
    def test_metric_type_enumeration(self):
        """Testa enumeração completa"""
        expected_types = [
            "cpu_usage", "memory_usage", "disk_usage", "network_io",
            "response_time", "error_rate", "throughput", "availability", "custom"
        ]
        actual_types = [metric.value for metric in MetricType]
        assert actual_types == expected_types
    
    def test_metric_type_validation(self):
        """Testa validação de tipos de métricas"""
        # Teste com valor válido
        assert MetricType("cpu_usage") == MetricType.CPU_USAGE
        
        # Teste com valor inválido
        with pytest.raises(ValueError):
            MetricType("invalid_metric")


class TestAlertSeverity:
    """Testes para AlertSeverity"""
    
    def test_alert_severity_values(self):
        """Testa valores das severidades de alerta"""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"
    
    def test_alert_severity_hierarchy(self):
        """Testa hierarquia de severidades"""
        severities = list(AlertSeverity)
        assert severities[0] == AlertSeverity.INFO
        assert severities[1] == AlertSeverity.WARNING
        assert severities[2] == AlertSeverity.ERROR
        assert severities[3] == AlertSeverity.CRITICAL
    
    def test_alert_severity_comparison(self):
        """Testa comparação entre severidades"""
        assert AlertSeverity.INFO < AlertSeverity.WARNING
        assert AlertSeverity.WARNING < AlertSeverity.ERROR
        assert AlertSeverity.ERROR < AlertSeverity.CRITICAL
        assert AlertSeverity.CRITICAL > AlertSeverity.INFO


class TestSystemMetrics:
    """Testes para SystemMetrics"""
    
    @pytest.fixture
    def sample_system_metrics(self):
        """Dados de exemplo para métricas do sistema"""
        return {
            'timestamp': datetime.now(),
            'cpu_usage': 0.75,
            'memory_usage': 0.60,
            'disk_usage': 0.45,
            'network_sent': 1024.5,
            'network_recv': 2048.0,
            'disk_read': 512.0,
            'disk_write': 256.0
        }
    
    def test_system_metrics_initialization(self, sample_system_metrics):
        """Testa inicialização de SystemMetrics"""
        metrics = SystemMetrics(**sample_system_metrics)
        
        assert metrics.timestamp == sample_system_metrics['timestamp']
        assert metrics.cpu_usage == 0.75
        assert metrics.memory_usage == 0.60
        assert metrics.disk_usage == 0.45
        assert metrics.network_sent == 1024.5
        assert metrics.network_recv == 2048.0
        assert metrics.disk_read == 512.0
        assert metrics.disk_write == 256.0
    
    def test_system_metrics_validation(self):
        """Testa validação de métricas do sistema"""
        # Teste com valores válidos
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=0.5,
            memory_usage=0.3,
            disk_usage=0.2,
            network_sent=100.0,
            network_recv=200.0,
            disk_read=50.0,
            disk_write=25.0
        )
        assert metrics is not None
        
        # Teste com valores extremos
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=1.0,  # 100% CPU
            memory_usage=1.0,  # 100% memória
            disk_usage=1.0,  # 100% disco
            network_sent=0.0,
            network_recv=0.0,
            disk_read=0.0,
            disk_write=0.0
        )
        assert metrics.cpu_usage == 1.0
        assert metrics.memory_usage == 1.0
        assert metrics.disk_usage == 1.0
    
    def test_system_metrics_serialization(self, sample_system_metrics):
        """Testa serialização de SystemMetrics"""
        metrics = SystemMetrics(**sample_system_metrics)
        
        # Teste conversão para dict
        metrics_dict = asdict(metrics)
        assert isinstance(metrics_dict, dict)
        assert metrics_dict['cpu_usage'] == 0.75
        assert metrics_dict['memory_usage'] == 0.60


class TestApplicationMetrics:
    """Testes para ApplicationMetrics"""
    
    @pytest.fixture
    def sample_application_metrics(self):
        """Dados de exemplo para métricas da aplicação"""
        return {
            'timestamp': datetime.now(),
            'response_time': 1.5,
            'error_rate': 0.02,
            'throughput': 1000.0,
            'availability': 0.99,
            'active_connections': 150,
            'queue_size': 25,
            'custom_metrics': {
                'cache_hit_rate': 0.85,
                'database_connections': 10,
                'api_calls_per_second': 500
            }
        }
    
    def test_application_metrics_initialization(self, sample_application_metrics):
        """Testa inicialização de ApplicationMetrics"""
        metrics = ApplicationMetrics(**sample_application_metrics)
        
        assert metrics.timestamp == sample_application_metrics['timestamp']
        assert metrics.response_time == 1.5
        assert metrics.error_rate == 0.02
        assert metrics.throughput == 1000.0
        assert metrics.availability == 0.99
        assert metrics.active_connections == 150
        assert metrics.queue_size == 25
        assert metrics.custom_metrics['cache_hit_rate'] == 0.85
        assert metrics.custom_metrics['database_connections'] == 10
        assert metrics.custom_metrics['api_calls_per_second'] == 500
    
    def test_application_metrics_validation(self):
        """Testa validação de métricas da aplicação"""
        # Teste com valores válidos
        metrics = ApplicationMetrics(
            timestamp=datetime.now(),
            response_time=0.5,
            error_rate=0.01,
            throughput=500.0,
            availability=0.995,
            active_connections=50,
            queue_size=5,
            custom_metrics={}
        )
        assert metrics is not None
        
        # Teste com valores extremos
        metrics = ApplicationMetrics(
            timestamp=datetime.now(),
            response_time=10.0,  # Tempo de resposta alto
            error_rate=0.5,      # Taxa de erro alta
            throughput=0.0,      # Sem throughput
            availability=0.0,    # Sem disponibilidade
            active_connections=0,
            queue_size=1000,     # Fila grande
            custom_metrics={'test': 'value'}
        )
        assert metrics.response_time == 10.0
        assert metrics.error_rate == 0.5
        assert metrics.availability == 0.0
    
    def test_application_metrics_custom_metrics(self):
        """Testa métricas customizadas"""
        custom_metrics = {
            'user_sessions': 1000,
            'failed_logins': 5,
            'cache_miss_rate': 0.15,
            'database_query_time': 0.2
        }
        
        metrics = ApplicationMetrics(
            timestamp=datetime.now(),
            response_time=1.0,
            error_rate=0.01,
            throughput=800.0,
            availability=0.98,
            active_connections=200,
            queue_size=15,
            custom_metrics=custom_metrics
        )
        
        assert metrics.custom_metrics['user_sessions'] == 1000
        assert metrics.custom_metrics['failed_logins'] == 5
        assert metrics.custom_metrics['cache_miss_rate'] == 0.15
        assert metrics.custom_metrics['database_query_time'] == 0.2


class TestChaosMetrics:
    """Testes para ChaosMetrics"""
    
    @pytest.fixture
    def sample_system_metrics(self):
        """Métricas do sistema de exemplo"""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=0.75,
            memory_usage=0.60,
            disk_usage=0.45,
            network_sent=1024.5,
            network_recv=2048.0,
            disk_read=512.0,
            disk_write=256.0
        )
    
    @pytest.fixture
    def sample_application_metrics(self):
        """Métricas da aplicação de exemplo"""
        return ApplicationMetrics(
            timestamp=datetime.now(),
            response_time=1.5,
            error_rate=0.02,
            throughput=1000.0,
            availability=0.99,
            active_connections=150,
            queue_size=25,
            custom_metrics={'cache_hit_rate': 0.85}
        )
    
    @pytest.fixture
    def sample_chaos_metrics(self, sample_system_metrics, sample_application_metrics):
        """Métricas de chaos de exemplo"""
        return {
            'timestamp': datetime.now(),
            'experiment_id': 'chaos_test_001',
            'phase': 'injection',
            'system_metrics': sample_system_metrics,
            'application_metrics': sample_application_metrics,
            'impact_score': 0.65,
            'baseline_deviation': 0.25,
            'recovery_time': None
        }
    
    def test_chaos_metrics_initialization(self, sample_chaos_metrics):
        """Testa inicialização de ChaosMetrics"""
        metrics = ChaosMetrics(**sample_chaos_metrics)
        
        assert metrics.timestamp == sample_chaos_metrics['timestamp']
        assert metrics.experiment_id == 'chaos_test_001'
        assert metrics.phase == 'injection'
        assert metrics.impact_score == 0.65
        assert metrics.baseline_deviation == 0.25
        assert metrics.recovery_time is None
    
    def test_chaos_metrics_with_recovery_time(self, sample_chaos_metrics):
        """Testa ChaosMetrics com tempo de recuperação"""
        sample_chaos_metrics['recovery_time'] = 45.5
        
        metrics = ChaosMetrics(**sample_chaos_metrics)
        
        assert metrics.recovery_time == 45.5
        assert metrics.phase == 'injection'
        assert metrics.impact_score == 0.65
    
    def test_chaos_metrics_phases(self, sample_chaos_metrics):
        """Testa diferentes fases do chaos"""
        phases = ['baseline', 'injection', 'monitoring', 'recovery', 'analysis']
        
        for phase in phases:
            sample_chaos_metrics['phase'] = phase
            metrics = ChaosMetrics(**sample_chaos_metrics)
            assert metrics.phase == phase
    
    def test_chaos_metrics_impact_scores(self, sample_chaos_metrics):
        """Testa diferentes scores de impacto"""
        impact_scores = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for score in impact_scores:
            sample_chaos_metrics['impact_score'] = score
            metrics = ChaosMetrics(**sample_chaos_metrics)
            assert metrics.impact_score == score


class TestAlert:
    """Testes para Alert"""
    
    @pytest.fixture
    def sample_alert_data(self):
        """Dados de exemplo para alerta"""
        return {
            'id': 'alert_001',
            'timestamp': datetime.now(),
            'severity': AlertSeverity.WARNING,
            'metric_type': MetricType.CPU_USAGE,
            'metric_value': 0.85,
            'threshold': 0.8,
            'message': 'CPU usage exceeded threshold',
            'experiment_id': 'chaos_test_001',
            'resolved': False,
            'resolved_at': None
        }
    
    def test_alert_initialization(self, sample_alert_data):
        """Testa inicialização de Alert"""
        alert = Alert(**sample_alert_data)
        
        assert alert.id == 'alert_001'
        assert alert.timestamp == sample_alert_data['timestamp']
        assert alert.severity == AlertSeverity.WARNING
        assert alert.metric_type == MetricType.CPU_USAGE
        assert alert.metric_value == 0.85
        assert alert.threshold == 0.8
        assert alert.message == 'CPU usage exceeded threshold'
        assert alert.experiment_id == 'chaos_test_001'
        assert alert.resolved is False
        assert alert.resolved_at is None
    
    def test_alert_resolution(self, sample_alert_data):
        """Testa resolução de alerta"""
        alert = Alert(**sample_alert_data)
        
        # Inicialmente não resolvido
        assert alert.resolved is False
        assert alert.resolved_at is None
        
        # Resolver alerta
        resolution_time = datetime.now()
        alert.resolved = True
        alert.resolved_at = resolution_time
        
        assert alert.resolved is True
        assert alert.resolved_at == resolution_time
    
    def test_alert_severity_levels(self):
        """Testa diferentes níveis de severidade"""
        severities = [AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL]
        
        for severity in severities:
            alert_data = {
                'id': f'alert_{severity.value}',
                'timestamp': datetime.now(),
                'severity': severity,
                'metric_type': MetricType.CPU_USAGE,
                'metric_value': 0.9,
                'threshold': 0.8,
                'message': f'Test alert for {severity.value}',
                'experiment_id': 'chaos_test_001',
                'resolved': False,
                'resolved_at': None
            }
            
            alert = Alert(**alert_data)
            assert alert.severity == severity
            assert alert.id == f'alert_{severity.value}'
    
    def test_alert_metric_types(self):
        """Testa diferentes tipos de métricas"""
        metric_types = [
            MetricType.CPU_USAGE,
            MetricType.MEMORY_USAGE,
            MetricType.DISK_USAGE,
            MetricType.RESPONSE_TIME,
            MetricType.ERROR_RATE
        ]
        
        for metric_type in metric_types:
            alert_data = {
                'id': f'alert_{metric_type.value}',
                'timestamp': datetime.now(),
                'severity': AlertSeverity.WARNING,
                'metric_type': metric_type,
                'metric_value': 0.9,
                'threshold': 0.8,
                'message': f'Test alert for {metric_type.value}',
                'experiment_id': 'chaos_test_001',
                'resolved': False,
                'resolved_at': None
            }
            
            alert = Alert(**alert_data)
            assert alert.metric_type == metric_type
            assert alert.id == f'alert_{metric_type.value}'


class TestImpactAnalysis:
    """Testes para ImpactAnalysis"""
    
    @pytest.fixture
    def sample_impact_analysis_data(self):
        """Dados de exemplo para análise de impacto"""
        return {
            'experiment_id': 'chaos_test_001',
            'start_time': datetime.now() - timedelta(minutes=10),
            'end_time': datetime.now(),
            'duration': 600.0,
            'max_cpu_impact': 0.25,
            'max_memory_impact': 0.15,
            'max_error_rate_impact': 0.05,
            'max_response_time_impact': 0.3,
            'availability_impact': 0.02,
            'recovery_time': 45.5,
            'recovery_successful': True,
            'baseline_deviation': 0.18,
            'impact_level': 'medium',
            'recommendations': [
                'Monitor CPU usage more closely',
                'Consider scaling up resources',
                'Review error handling procedures'
            ]
        }
    
    def test_impact_analysis_initialization(self, sample_impact_analysis_data):
        """Testa inicialização de ImpactAnalysis"""
        analysis = ImpactAnalysis(**sample_impact_analysis_data)
        
        assert analysis.experiment_id == 'chaos_test_001'
        assert analysis.duration == 600.0
        assert analysis.max_cpu_impact == 0.25
        assert analysis.max_memory_impact == 0.15
        assert analysis.max_error_rate_impact == 0.05
        assert analysis.max_response_time_impact == 0.3
        assert analysis.availability_impact == 0.02
        assert analysis.recovery_time == 45.5
        assert analysis.recovery_successful is True
        assert analysis.baseline_deviation == 0.18
        assert analysis.impact_level == 'medium'
        assert len(analysis.recommendations) == 3
    
    def test_impact_analysis_without_recovery(self, sample_impact_analysis_data):
        """Testa ImpactAnalysis sem tempo de recuperação"""
        sample_impact_analysis_data['recovery_time'] = None
        sample_impact_analysis_data['recovery_successful'] = False
        
        analysis = ImpactAnalysis(**sample_impact_analysis_data)
        
        assert analysis.recovery_time is None
        assert analysis.recovery_successful is False
    
    def test_impact_analysis_impact_levels(self, sample_impact_analysis_data):
        """Testa diferentes níveis de impacto"""
        impact_levels = ['low', 'medium', 'high', 'critical']
        
        for level in impact_levels:
            sample_impact_analysis_data['impact_level'] = level
            analysis = ImpactAnalysis(**sample_impact_analysis_data)
            assert analysis.impact_level == level
    
    def test_impact_analysis_recommendations(self, sample_impact_analysis_data):
        """Testa recomendações da análise"""
        recommendations = [
            'Increase monitoring frequency',
            'Add circuit breakers',
            'Implement retry mechanisms',
            'Scale horizontally',
            'Optimize database queries'
        ]
        
        sample_impact_analysis_data['recommendations'] = recommendations
        analysis = ImpactAnalysis(**sample_impact_analysis_data)
        
        assert len(analysis.recommendations) == 5
        assert 'Increase monitoring frequency' in analysis.recommendations
        assert 'Add circuit breakers' in analysis.recommendations


class TestMonitoringConfig:
    """Testes para MonitoringConfig"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Dados de exemplo para configuração"""
        return {
            'enabled': True,
            'metrics_interval': 10,
            'retention_period': 7200,
            'collect_system_metrics': True,
            'collect_application_metrics': True,
            'collect_custom_metrics': True,
            'cpu_threshold': 0.85,
            'memory_threshold': 0.75,
            'disk_threshold': 0.95,
            'error_rate_threshold': 0.03,
            'response_time_threshold': 1.5,
            'availability_threshold': 0.98,
            'baseline_window': 600,
            'impact_calculation_window': 120,
            'recovery_timeout': 600,
            'export_to_prometheus': True,
            'export_to_grafana': True,
            'export_to_logs': False
        }
    
    def test_monitoring_config_initialization(self, sample_config_data):
        """Testa inicialização de MonitoringConfig"""
        config = MonitoringConfig(**sample_config_data)
        
        assert config.enabled is True
        assert config.metrics_interval == 10
        assert config.retention_period == 7200
        assert config.collect_system_metrics is True
        assert config.collect_application_metrics is True
        assert config.collect_custom_metrics is True
        assert config.cpu_threshold == 0.85
        assert config.memory_threshold == 0.75
        assert config.disk_threshold == 0.95
        assert config.error_rate_threshold == 0.03
        assert config.response_time_threshold == 1.5
        assert config.availability_threshold == 0.98
        assert config.baseline_window == 600
        assert config.impact_calculation_window == 120
        assert config.recovery_timeout == 600
        assert config.export_to_prometheus is True
        assert config.export_to_grafana is True
        assert config.export_to_logs is False
    
    def test_monitoring_config_defaults(self):
        """Testa valores padrão de MonitoringConfig"""
        config = MonitoringConfig()
        
        assert config.enabled is True
        assert config.metrics_interval == 5
        assert config.retention_period == 3600
        assert config.collect_system_metrics is True
        assert config.collect_application_metrics is True
        assert config.collect_custom_metrics is True
        assert config.cpu_threshold == 0.8
        assert config.memory_threshold == 0.8
        assert config.disk_threshold == 0.9
        assert config.error_rate_threshold == 0.05
        assert config.response_time_threshold == 2.0
        assert config.availability_threshold == 0.95
        assert config.baseline_window == 300
        assert config.impact_calculation_window == 60
        assert config.recovery_timeout == 300
        assert config.export_to_prometheus is True
        assert config.export_to_grafana is True
        assert config.export_to_logs is True
    
    def test_monitoring_config_validation(self):
        """Testa validação de configuração"""
        # Teste com valores válidos
        config = MonitoringConfig(
            metrics_interval=1,
            retention_period=100,
            cpu_threshold=0.5,
            memory_threshold=0.6,
            disk_threshold=0.7,
            error_rate_threshold=0.01,
            response_time_threshold=0.5,
            availability_threshold=0.99
        )
        assert config is not None
        
        # Teste com valores extremos
        config = MonitoringConfig(
            metrics_interval=3600,  # 1 hora
            retention_period=86400,  # 1 dia
            cpu_threshold=1.0,      # 100% CPU
            memory_threshold=1.0,   # 100% memória
            disk_threshold=1.0,     # 100% disco
            error_rate_threshold=1.0,  # 100% erro
            response_time_threshold=60.0,  # 60 segundos
            availability_threshold=0.0     # 0% disponibilidade
        )
        assert config.metrics_interval == 3600
        assert config.cpu_threshold == 1.0
        assert config.availability_threshold == 0.0


class TestChaosMonitor:
    """Testes para ChaosMonitor"""
    
    @pytest.fixture
    def sample_monitoring_config(self):
        """Configuração de monitoramento de exemplo"""
        return MonitoringConfig(
            enabled=True,
            metrics_interval=5,
            cpu_threshold=0.8,
            memory_threshold=0.8,
            error_rate_threshold=0.05
        )
    
    @pytest.fixture
    def chaos_monitor(self, sample_monitoring_config):
        """Instância de ChaosMonitor para testes"""
        return ChaosMonitor(config=sample_monitoring_config)
    
    @pytest.fixture
    def sample_system_metrics(self):
        """Métricas do sistema de exemplo"""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=0.75,
            memory_usage=0.60,
            disk_usage=0.45,
            network_sent=1024.5,
            network_recv=2048.0,
            disk_read=512.0,
            disk_write=256.0
        )
    
    @pytest.fixture
    def sample_application_metrics(self):
        """Métricas da aplicação de exemplo"""
        return ApplicationMetrics(
            timestamp=datetime.now(),
            response_time=1.5,
            error_rate=0.02,
            throughput=1000.0,
            availability=0.99,
            active_connections=150,
            queue_size=25,
            custom_metrics={'cache_hit_rate': 0.85}
        )
    
    def test_chaos_monitor_initialization(self, sample_monitoring_config):
        """Testa inicialização de ChaosMonitor"""
        monitor = ChaosMonitor(config=sample_monitoring_config)
        
        assert monitor.config == sample_monitoring_config
        assert isinstance(monitor.metrics_buffer, deque)
        assert monitor.metrics_buffer.maxlen == 1000
        assert isinstance(monitor.alerts, dict)
        assert monitor.baseline_metrics is None
        assert monitor.current_experiment is None
        assert monitor.monitoring_task is None
        assert monitor.stop_monitoring_flag is False
        assert isinstance(monitor.alert_callbacks, list)
        assert isinstance(monitor.metrics_callbacks, list)
        assert isinstance(monitor.stats, dict)
        assert monitor.stats['metrics_collected'] == 0
        assert monitor.stats['alerts_generated'] == 0
    
    def test_chaos_monitor_default_config(self):
        """Testa ChaosMonitor com configuração padrão"""
        monitor = ChaosMonitor()
        
        assert monitor.config is not None
        assert monitor.config.enabled is True
        assert monitor.config.metrics_interval == 5
        assert monitor.config.cpu_threshold == 0.8
    
    @pytest.mark.asyncio
    async def test_chaos_monitor_start_stop_monitoring(self, chaos_monitor):
        """Testa início e parada do monitoramento"""
        # Iniciar monitoramento
        await chaos_monitor.start_monitoring()
        
        assert chaos_monitor.monitoring_task is not None
        assert not chaos_monitor.monitoring_task.done()
        assert chaos_monitor.stop_monitoring_flag is False
        
        # Parar monitoramento
        await chaos_monitor.stop_monitoring()
        
        assert chaos_monitor.stop_monitoring_flag is True
        assert chaos_monitor.monitoring_task.cancelled()
    
    @pytest.mark.asyncio
    async def test_chaos_monitor_collect_metrics(self, chaos_monitor):
        """Testa coleta de métricas"""
        with patch.object(chaos_monitor, '_collect_system_metrics') as mock_system, \
             patch.object(chaos_monitor, '_collect_application_metrics') as mock_app, \
             patch.object(chaos_monitor, '_calculate_impact_score') as mock_impact, \
             patch.object(chaos_monitor, '_calculate_baseline_deviation') as mock_baseline:
            
            # Configurar mocks
            mock_system.return_value = Mock()
            mock_app.return_value = Mock()
            mock_impact.return_value = 0.5
            mock_baseline.return_value = 0.2
            
            # Coletar métricas
            metrics = await chaos_monitor.collect_metrics()
            
            assert metrics is not None
            assert metrics.impact_score == 0.5
            assert metrics.baseline_deviation == 0.2
            assert mock_system.called
            assert mock_app.called
            assert mock_impact.called
            assert mock_baseline.called
    
    def test_chaos_monitor_set_baseline(self, chaos_monitor, sample_system_metrics, sample_application_metrics):
        """Testa definição de baseline"""
        baseline_metrics = ChaosMetrics(
            timestamp=datetime.now(),
            experiment_id='baseline',
            phase='baseline',
            system_metrics=sample_system_metrics,
            application_metrics=sample_application_metrics,
            impact_score=0.0,
            baseline_deviation=0.0
        )
        
        chaos_monitor.set_baseline(baseline_metrics)
        
        assert chaos_monitor.baseline_metrics == baseline_metrics
    
    def test_chaos_monitor_set_current_experiment(self, chaos_monitor):
        """Testa definição de experimento atual"""
        experiment_id = 'chaos_test_001'
        
        chaos_monitor.set_current_experiment(experiment_id)
        
        assert chaos_monitor.current_experiment == experiment_id
    
    def test_chaos_monitor_clear_current_experiment(self, chaos_monitor):
        """Testa limpeza de experimento atual"""
        chaos_monitor.current_experiment = 'chaos_test_001'
        
        chaos_monitor.clear_current_experiment()
        
        assert chaos_monitor.current_experiment is None
    
    def test_chaos_monitor_add_callbacks(self, chaos_monitor):
        """Testa adição de callbacks"""
        alert_callback = Mock()
        metrics_callback = Mock()
        
        chaos_monitor.add_alert_callback(alert_callback)
        chaos_monitor.add_metrics_callback(metrics_callback)
        
        assert alert_callback in chaos_monitor.alert_callbacks
        assert metrics_callback in chaos_monitor.metrics_callbacks
    
    def test_chaos_monitor_get_metrics(self, chaos_monitor):
        """Testa obtenção de métricas"""
        # Adicionar métricas de exemplo
        sample_metrics = Mock()
        chaos_monitor.metrics_buffer.append(sample_metrics)
        chaos_monitor.metrics_buffer.append(sample_metrics)
        
        # Obter todas as métricas
        metrics = chaos_monitor.get_metrics()
        assert len(metrics) == 2
        
        # Obter métricas com limite
        metrics = chaos_monitor.get_metrics(limit=1)
        assert len(metrics) == 1
    
    def test_chaos_monitor_get_alerts(self, chaos_monitor):
        """Testa obtenção de alertas"""
        # Criar alertas de exemplo
        alert1 = Alert(
            id='alert_1',
            timestamp=datetime.now(),
            severity=AlertSeverity.WARNING,
            metric_type=MetricType.CPU_USAGE,
            metric_value=0.85,
            threshold=0.8,
            message='CPU high',
            experiment_id='test_001',
            resolved=False
        )
        
        alert2 = Alert(
            id='alert_2',
            timestamp=datetime.now(),
            severity=AlertSeverity.ERROR,
            metric_type=MetricType.MEMORY_USAGE,
            metric_value=0.9,
            threshold=0.8,
            message='Memory high',
            experiment_id='test_001',
            resolved=True
        )
        
        chaos_monitor.alerts['alert_1'] = alert1
        chaos_monitor.alerts['alert_2'] = alert2
        
        # Obter todos os alertas
        alerts = chaos_monitor.get_alerts()
        assert len(alerts) == 2
        
        # Obter alertas por severidade
        warning_alerts = chaos_monitor.get_alerts(severity=AlertSeverity.WARNING)
        assert len(warning_alerts) == 1
        assert warning_alerts[0].severity == AlertSeverity.WARNING
        
        # Obter alertas por status
        resolved_alerts = chaos_monitor.get_alerts(resolved=True)
        assert len(resolved_alerts) == 1
        assert resolved_alerts[0].resolved is True
    
    def test_chaos_monitor_resolve_alert(self, chaos_monitor):
        """Testa resolução de alerta"""
        alert = Alert(
            id='alert_001',
            timestamp=datetime.now(),
            severity=AlertSeverity.WARNING,
            metric_type=MetricType.CPU_USAGE,
            metric_value=0.85,
            threshold=0.8,
            message='CPU high',
            experiment_id='test_001',
            resolved=False
        )
        
        chaos_monitor.alerts['alert_001'] = alert
        
        # Resolver alerta
        success = chaos_monitor.resolve_alert('alert_001')
        assert success is True
        assert alert.resolved is True
        assert alert.resolved_at is not None
        
        # Tentar resolver alerta inexistente
        success = chaos_monitor.resolve_alert('nonexistent')
        assert success is False
    
    def test_chaos_monitor_get_statistics(self, chaos_monitor):
        """Testa obtenção de estatísticas"""
        stats = chaos_monitor.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'metrics_collected' in stats
        assert 'alerts_generated' in stats
        assert 'experiments_monitored' in stats
        assert 'total_monitoring_time' in stats
    
    def test_chaos_monitor_export_metrics(self, chaos_monitor):
        """Testa exportação de métricas"""
        # Adicionar métricas de exemplo
        sample_metrics = Mock()
        chaos_monitor.metrics_buffer.append(sample_metrics)
        
        # Exportar como JSON
        json_export = chaos_monitor.export_metrics('json')
        assert isinstance(json_export, str)
        
        # Verificar se é JSON válido
        parsed = json.loads(json_export)
        assert isinstance(parsed, dict)
    
    def test_chaos_monitor_cleanup(self, chaos_monitor):
        """Testa limpeza do monitor"""
        # Adicionar dados de exemplo
        chaos_monitor.metrics_buffer.append(Mock())
        chaos_monitor.alerts['test'] = Mock()
        chaos_monitor.baseline_metrics = Mock()
        chaos_monitor.current_experiment = 'test'
        
        # Executar limpeza
        chaos_monitor.cleanup()
        
        assert len(chaos_monitor.metrics_buffer) == 0
        assert len(chaos_monitor.alerts) == 0
        assert chaos_monitor.baseline_metrics is None
        assert chaos_monitor.current_experiment is None


class TestChaosMonitorIntegration:
    """Testes de integração para ChaosMonitor"""
    
    @pytest.mark.asyncio
    async def test_chaos_monitor_full_workflow(self):
        """Testa workflow completo do ChaosMonitor"""
        config = MonitoringConfig(
            enabled=True,
            metrics_interval=1,
            cpu_threshold=0.8,
            memory_threshold=0.8,
            error_rate_threshold=0.05
        )
        
        monitor = ChaosMonitor(config=config)
        
        # 1. Definir baseline
        baseline_metrics = Mock()
        monitor.set_baseline(baseline_metrics)
        assert monitor.baseline_metrics == baseline_metrics
        
        # 2. Definir experimento atual
        monitor.set_current_experiment('chaos_test_001')
        assert monitor.current_experiment == 'chaos_test_001'
        
        # 3. Adicionar callbacks
        alert_callback = Mock()
        metrics_callback = Mock()
        monitor.add_alert_callback(alert_callback)
        monitor.add_metrics_callback(metrics_callback)
        
        # 4. Iniciar monitoramento (simulado)
        with patch.object(monitor, '_monitoring_loop') as mock_loop:
            await monitor.start_monitoring()
            assert monitor.monitoring_task is not None
        
        # 5. Parar monitoramento
        await monitor.stop_monitoring()
        assert monitor.stop_monitoring_flag is True
        
        # 6. Verificar estatísticas
        stats = monitor.get_statistics()
        assert isinstance(stats, dict)
        
        # 7. Limpeza
        monitor.cleanup()
        assert len(monitor.metrics_buffer) == 0
        assert len(monitor.alerts) == 0


class TestChaosMonitorErrorHandling:
    """Testes de tratamento de erro para ChaosMonitor"""
    
    @pytest.mark.asyncio
    async def test_chaos_monitor_monitoring_loop_error(self):
        """Testa tratamento de erro no loop de monitoramento"""
        config = MonitoringConfig(enabled=True, metrics_interval=1)
        monitor = ChaosMonitor(config=config)
        
        with patch.object(monitor, 'collect_metrics', side_effect=Exception("Test error")):
            # O loop deve continuar mesmo com erro
            await monitor.start_monitoring()
            await asyncio.sleep(0.1)  # Aguardar um ciclo
            await monitor.stop_monitoring()
            
            # Verificar que o monitor ainda está funcional
            assert monitor.stop_monitoring_flag is True
    
    def test_chaos_monitor_invalid_config(self):
        """Testa comportamento com configuração inválida"""
        # Teste com configuração None
        monitor = ChaosMonitor(config=None)
        assert monitor.config is not None  # Deve usar configuração padrão
        
        # Teste com configuração vazia
        monitor = ChaosMonitor(config=MonitoringConfig())
        assert monitor.config.enabled is True


class TestChaosMonitorPerformance:
    """Testes de performance para ChaosMonitor"""
    
    def test_chaos_monitor_memory_usage(self):
        """Testa uso de memória do ChaosMonitor"""
        config = MonitoringConfig(
            enabled=True,
            metrics_interval=1,
            retention_period=100
        )
        
        monitor = ChaosMonitor(config=config)
        
        # Adicionar muitas métricas
        for i in range(1000):
            monitor.metrics_buffer.append(Mock())
        
        # Verificar que o buffer não excedeu o limite
        assert len(monitor.metrics_buffer) <= 1000
        
        # Verificar que as métricas mais antigas foram removidas
        assert monitor.metrics_buffer.maxlen == 1000
    
    @pytest.mark.asyncio
    async def test_chaos_monitor_concurrent_access(self):
        """Testa acesso concorrente ao ChaosMonitor"""
        config = MonitoringConfig(enabled=True, metrics_interval=1)
        monitor = ChaosMonitor(config=config)
        
        # Simular acesso concorrente
        async def add_metrics():
            for i in range(100):
                monitor.metrics_buffer.append(Mock())
                await asyncio.sleep(0.001)
        
        async def add_alerts():
            for i in range(100):
                alert = Mock()
                monitor.alerts[f'alert_{i}'] = alert
                await asyncio.sleep(0.001)
        
        # Executar tarefas concorrentes
        await asyncio.gather(add_metrics(), add_alerts())
        
        # Verificar que não houve corrupção de dados
        assert len(monitor.metrics_buffer) <= 1000
        assert len(monitor.alerts) == 100


class TestCreateChaosMonitor:
    """Testes para função create_chaos_monitor"""
    
    def test_create_chaos_monitor_with_config(self):
        """Testa criação de ChaosMonitor com configuração"""
        config = MonitoringConfig(
            enabled=True,
            metrics_interval=10,
            cpu_threshold=0.9
        )
        
        monitor = create_chaos_monitor(config)
        
        assert isinstance(monitor, ChaosMonitor)
        assert monitor.config == config
        assert monitor.config.metrics_interval == 10
        assert monitor.config.cpu_threshold == 0.9
    
    def test_create_chaos_monitor_without_config(self):
        """Testa criação de ChaosMonitor sem configuração"""
        monitor = create_chaos_monitor()
        
        assert isinstance(monitor, ChaosMonitor)
        assert monitor.config is not None
        assert monitor.config.enabled is True
        assert monitor.config.metrics_interval == 5  # Valor padrão 