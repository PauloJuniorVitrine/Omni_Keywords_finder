"""
Testes Unitários - Sistema de Coleta Inteligente
Omni Keywords Finder

Tracing ID: TEST_INTELLIGENT_COLLECTOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes de Sistema de Coleta Inteligente

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any

from infrastructure.aiops.intelligent_collector import (
    IntelligentCollector, DataSource, SystemMetricsSource, 
    ApplicationLogSource, DatabaseQuerySource, Event, 
    EventType, EventSeverity
)

# Dados de teste baseados no código real
SYSTEM_METRICS_CONFIG = {
    'collection_interval': 60,
    'metrics': ['cpu_usage', 'memory_usage', 'disk_usage'],
    'thresholds': {
        'cpu_usage': {
            'critical': 90,
            'high': 80,
            'medium': 70
        },
        'memory_usage': {
            'critical': 95,
            'high': 85,
            'medium': 75
        }
    }
}

APPLICATION_LOGS_CONFIG = {
    'log_file_path': '/var/log/omni_keywords_finder/app.log',
    'log_levels': ['ERROR', 'WARNING', 'INFO'],
    'batch_size': 100
}

DATABASE_QUERIES_CONFIG = {
    'slow_query_threshold': 1000,
    'query_patterns': ['SELECT', 'UPDATE', 'INSERT'],
    'collection_interval': 30
}

COLLECTOR_CONFIG = {
    'collection_interval': 60,
    'batch_size': 1000,
    'enable_anomaly_detection': True,
    'enable_correlation': True,
    'max_recent_events': 10000,
    'sources': {
        'system_metrics': {
            'enabled': True,
            **SYSTEM_METRICS_CONFIG
        },
        'application_logs': {
            'enabled': True,
            **APPLICATION_LOGS_CONFIG
        },
        'database_queries': {
            'enabled': True,
            **DATABASE_QUERIES_CONFIG
        }
    }
}

@pytest.fixture
def mock_redis_manager():
    """Mock do Redis Manager"""
    redis_mock = Mock()
    redis_mock.connect = AsyncMock()
    redis_mock.disconnect = AsyncMock()
    redis_mock.set = AsyncMock()
    redis_mock.lpush = AsyncMock()
    redis_mock.expire = AsyncMock()
    return redis_mock

@pytest.fixture
def mock_anomaly_detector():
    """Mock do Anomaly Detector"""
    detector_mock = Mock()
    detector_mock.detect_anomalies = AsyncMock(return_value=[])
    return detector_mock

@pytest.fixture
def mock_structured_logger():
    """Mock do Structured Logger"""
    logger_mock = Mock()
    logger_mock.log_event = AsyncMock()
    return logger_mock

@pytest.fixture
def mock_metrics_collector():
    """Mock do Metrics Collector"""
    collector_mock = Mock()
    collector_mock.initialize = AsyncMock()
    collector_mock.collect_system_metrics = AsyncMock(return_value={
        'cpu_usage': 75.5,
        'memory_usage': 82.3,
        'disk_usage': 45.7
    })
    return collector_mock

@pytest.fixture
def sample_event():
    """Evento de exemplo"""
    return Event(
        id="test_event_1",
        type=EventType.SYSTEM_METRIC,
        source="system_metrics",
        severity=EventSeverity.MEDIUM,
        timestamp=datetime.now(),
        data={
            'metric_name': 'cpu_usage',
            'value': 75.5,
            'unit': '%'
        },
        metadata={
            'collection_interval': 60,
            'thresholds': SYSTEM_METRICS_CONFIG['thresholds']
        },
        correlation_id="corr-123",
        user_id="user-456"
    )

class TestDataSource:
    """Testes para a classe base DataSource"""

    def test_data_source_initialization(self):
        """Testa inicialização da fonte de dados"""
        config = {'test': 'config'}
        source = DataSource("test_source", config)
        
        assert source.name == "test_source"
        assert source.config == config
        assert source.is_active is False
        assert source.last_collection is None
        assert source.error_count == 0
        assert source.success_count == 0

    def test_get_health_status(self):
        """Testa obtenção do status de saúde"""
        source = DataSource("test_source", {})
        source.is_active = True
        source.last_collection = datetime.now()
        source.error_count = 2
        source.success_count = 8
        
        status = source.get_health_status()
        
        assert status['name'] == "test_source"
        assert status['is_active'] is True
        assert status['last_collection'] is not None
        assert status['error_count'] == 2
        assert status['success_count'] == 8
        assert status['error_rate'] == 0.2  # 2/(2+8)

    def test_get_health_status_zero_events(self):
        """Testa status de saúde com zero eventos"""
        source = DataSource("test_source", {})
        
        status = source.get_health_status()
        
        assert status['error_rate'] == 0

class TestSystemMetricsSource:
    """Testes para SystemMetricsSource"""

    @pytest.mark.asyncio
    async def test_connect_success(self, mock_metrics_collector):
        """Testa conexão bem-sucedida"""
        with patch('infrastructure.aiops.intelligent_collector.MetricsCollector', return_value=mock_metrics_collector):
            source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
            
            result = await source.connect()
            
            assert result is True
            assert source.is_active is True
            mock_metrics_collector.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, mock_metrics_collector):
        """Testa falha na conexão"""
        mock_metrics_collector.initialize.side_effect = Exception("Connection failed")
        
        with patch('infrastructure.aiops.intelligent_collector.MetricsCollector', return_value=mock_metrics_collector):
            source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
            
            result = await source.connect()
            
            assert result is False
            assert source.is_active is False
            assert source.error_count == 1

    @pytest.mark.asyncio
    async def test_collect_metrics_success(self, mock_metrics_collector):
        """Testa coleta bem-sucedida de métricas"""
        with patch('infrastructure.aiops.intelligent_collector.MetricsCollector', return_value=mock_metrics_collector):
            source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
            source.is_active = True
            
            events = await source.collect()
            
            assert len(events) == 3  # cpu, memory, disk
            assert all(event.type == EventType.SYSTEM_METRIC for event in events)
            assert all(event.source == "system_metrics" for event in events)
            assert source.last_collection is not None
            assert source.success_count == 1

    @pytest.mark.asyncio
    async def test_collect_metrics_failure(self, mock_metrics_collector):
        """Testa falha na coleta de métricas"""
        mock_metrics_collector.collect_system_metrics.side_effect = Exception("Collection failed")
        
        with patch('infrastructure.aiops.intelligent_collector.MetricsCollector', return_value=mock_metrics_collector):
            source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
            source.is_active = True
            
            events = await source.collect()
            
            assert len(events) == 0
            assert source.error_count == 1

    def test_determine_severity_cpu_critical(self):
        """Testa determinação de severidade crítica para CPU"""
        source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
        
        severity = source._determine_severity('cpu_usage', 95.0)
        
        assert severity == EventSeverity.CRITICAL

    def test_determine_severity_cpu_high(self):
        """Testa determinação de severidade alta para CPU"""
        source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
        
        severity = source._determine_severity('cpu_usage', 85.0)
        
        assert severity == EventSeverity.HIGH

    def test_determine_severity_cpu_medium(self):
        """Testa determinação de severidade média para CPU"""
        source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
        
        severity = source._determine_severity('cpu_usage', 75.0)
        
        assert severity == EventSeverity.MEDIUM

    def test_determine_severity_cpu_low(self):
        """Testa determinação de severidade baixa para CPU"""
        source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
        
        severity = source._determine_severity('cpu_usage', 50.0)
        
        assert severity == EventSeverity.LOW

    def test_determine_severity_memory_critical(self):
        """Testa determinação de severidade crítica para memória"""
        source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
        
        severity = source._determine_severity('memory_usage', 98.0)
        
        assert severity == EventSeverity.CRITICAL

    def test_get_metric_unit(self):
        """Testa obtenção de unidades de métricas"""
        source = SystemMetricsSource(SYSTEM_METRICS_CONFIG)
        
        assert source._get_metric_unit('cpu_usage') == '%'
        assert source._get_metric_unit('memory_usage') == '%'
        assert source._get_metric_unit('disk_usage') == '%'
        assert source._get_metric_unit('network_io') == 'MB/s'
        assert source._get_metric_unit('response_time') == 'ms'
        assert source._get_metric_unit('unknown_metric') == ''

class TestApplicationLogSource:
    """Testes para ApplicationLogSource"""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Testa conexão bem-sucedida"""
        source = ApplicationLogSource(APPLICATION_LOGS_CONFIG)
        
        result = await source.connect()
        
        assert result is True
        assert source.is_active is True

    @pytest.mark.asyncio
    async def test_collect_logs_success(self):
        """Testa coleta bem-sucedida de logs"""
        source = ApplicationLogSource(APPLICATION_LOGS_CONFIG)
        source.is_active = True
        
        events = await source.collect()
        
        assert len(events) == 3  # 3 entradas simuladas
        assert all(event.type == EventType.APPLICATION_LOG for event in events)
        assert all(event.source == "application_logs" for event in events)
        assert source.last_collection is not None
        assert source.success_count == 1

    def test_map_log_level_to_severity(self):
        """Testa mapeamento de nível de log para severidade"""
        source = ApplicationLogSource(APPLICATION_LOGS_CONFIG)
        
        assert source._map_log_level_to_severity('ERROR') == EventSeverity.HIGH
        assert source._map_log_level_to_severity('WARNING') == EventSeverity.MEDIUM
        assert source._map_log_level_to_severity('INFO') == EventSeverity.LOW
        assert source._map_log_level_to_severity('DEBUG') == EventSeverity.LOW
        assert source._map_log_level_to_severity('UNKNOWN') == EventSeverity.LOW

class TestDatabaseQuerySource:
    """Testes para DatabaseQuerySource"""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Testa conexão bem-sucedida"""
        source = DatabaseQuerySource(DATABASE_QUERIES_CONFIG)
        
        result = await source.connect()
        
        assert result is True
        assert source.is_active is True

    @pytest.mark.asyncio
    async def test_collect_queries_success(self):
        """Testa coleta bem-sucedida de queries"""
        source = DatabaseQuerySource(DATABASE_QUERIES_CONFIG)
        source.is_active = True
        
        events = await source.collect()
        
        assert len(events) == 2  # 2 queries simuladas (ambas lentas)
        assert all(event.type == EventType.DATABASE_QUERY for event in events)
        assert all(event.source == "database_queries" for event in events)
        assert source.last_collection is not None
        assert source.success_count == 1

    def test_determine_query_severity_critical(self):
        """Testa determinação de severidade crítica para query"""
        source = DatabaseQuerySource(DATABASE_QUERIES_CONFIG)
        
        severity = source._determine_query_severity(6000)  # 6s
        
        assert severity == EventSeverity.CRITICAL

    def test_determine_query_severity_high(self):
        """Testa determinação de severidade alta para query"""
        source = DatabaseQuerySource(DATABASE_QUERIES_CONFIG)
        
        severity = source._determine_query_severity(3000)  # 3s
        
        assert severity == EventSeverity.HIGH

    def test_determine_query_severity_medium(self):
        """Testa determinação de severidade média para query"""
        source = DatabaseQuerySource(DATABASE_QUERIES_CONFIG)
        
        severity = source._determine_query_severity(1500)  # 1.5s
        
        assert severity == EventSeverity.MEDIUM

    def test_determine_query_severity_low(self):
        """Testa determinação de severidade baixa para query"""
        source = DatabaseQuerySource(DATABASE_QUERIES_CONFIG)
        
        severity = source._determine_query_severity(500)  # 0.5s
        
        assert severity == EventSeverity.LOW

class TestIntelligentCollector:
    """Testes para IntelligentCollector"""

    @pytest.fixture
    def collector(self, mock_redis_manager, mock_anomaly_detector, mock_structured_logger):
        """Instância do coletor inteligente"""
        with patch('infrastructure.aiops.intelligent_collector.RedisManager', return_value=mock_redis_manager), \
             patch('infrastructure.aiops.intelligent_collector.AnomalyDetector', return_value=mock_anomaly_detector), \
             patch('infrastructure.aiops.intelligent_collector.StructuredLogger', return_value=mock_structured_logger):
            return IntelligentCollector(COLLECTOR_CONFIG)

    def test_initialization(self, collector):
        """Testa inicialização do coletor"""
        assert collector.is_running is False
        assert len(collector.sources) == 3  # system_metrics, application_logs, database_queries
        assert collector.collection_interval == 60
        assert collector.batch_size == 1000
        assert collector.enable_anomaly_detection is True
        assert collector.enable_correlation is True
        assert collector.max_recent_events == 10000

    @pytest.mark.asyncio
    async def test_start_success(self, collector, mock_redis_manager):
        """Testa início bem-sucedido do coletor"""
        # Mock das fontes de dados
        for source in collector.sources:
            source.connect = AsyncMock(return_value=True)
            source.disconnect = AsyncMock()
        
        # Mock do loop de coleta
        with patch.object(collector, '_collection_loop', new_callable=AsyncMock) as mock_loop:
            await collector.start()
            
            mock_redis_manager.connect.assert_called_once()
            for source in collector.sources:
                source.connect.assert_called_once()
            assert collector.is_running is True

    @pytest.mark.asyncio
    async def test_start_failure(self, collector, mock_redis_manager):
        """Testa falha no início do coletor"""
        mock_redis_manager.connect.side_effect = Exception("Redis connection failed")
        
        await collector.start()
        
        assert collector.is_running is False

    @pytest.mark.asyncio
    async def test_stop(self, collector, mock_redis_manager):
        """Testa parada do coletor"""
        collector.is_running = True
        
        # Mock das fontes de dados
        for source in collector.sources:
            source.disconnect = AsyncMock()
        
        await collector.stop()
        
        assert collector.is_running is False
        mock_redis_manager.disconnect.assert_called_once()
        for source in collector.sources:
            source.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_collect_from_source_success(self, collector):
        """Testa coleta bem-sucedida de uma fonte"""
        source = Mock()
        source.name = "test_source"
        source.collect = AsyncMock(return_value=[sample_event()])
        
        events = await collector._collect_from_source(source)
        
        assert len(events) == 1
        assert events[0].id == "test_event_1"
        source.collect.assert_called_once()

    @pytest.mark.asyncio
    async def test_collect_from_source_failure(self, collector):
        """Testa falha na coleta de uma fonte"""
        source = Mock()
        source.name = "test_source"
        source.collect = AsyncMock(side_effect=Exception("Collection failed"))
        
        events = await collector._collect_from_source(source)
        
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_process_events_success(self, collector, mock_anomaly_detector, mock_redis_manager, mock_structured_logger):
        """Testa processamento bem-sucedido de eventos"""
        events = [sample_event()]
        
        await collector._process_events(events)
        
        assert len(collector.recent_events) == 1
        mock_anomaly_detector.detect_anomalies.assert_called_once()
        mock_redis_manager.set.assert_called()
        mock_structured_logger.log_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_anomalies_success(self, collector, mock_anomaly_detector):
        """Testa detecção bem-sucedida de anomalias"""
        events = [sample_event()]
        mock_anomaly_detector.detect_anomalies.return_value = [{
            'event_id': 'test_event_1',
            'is_anomaly': True,
            'score': 0.95,
            'type': 'outlier'
        }]
        
        anomalies = await collector._detect_anomalies(events)
        
        assert len(anomalies) == 1
        assert anomalies[0].metadata['anomaly_score'] == 0.95
        assert anomalies[0].metadata['anomaly_type'] == 'outlier'

    @pytest.mark.asyncio
    async def test_detect_anomalies_no_anomalies(self, collector, mock_anomaly_detector):
        """Testa detecção sem anomalias"""
        events = [sample_event()]
        mock_anomaly_detector.detect_anomalies.return_value = []
        
        anomalies = await collector._detect_anomalies(events)
        
        assert len(anomalies) == 0

    @pytest.mark.asyncio
    async def test_correlate_events_success(self, collector):
        """Testa correlação bem-sucedida de eventos"""
        event1 = sample_event()
        event1.correlation_id = "corr-123"
        event1.timestamp = datetime.now()
        
        event2 = sample_event()
        event2.id = "test_event_2"
        event2.correlation_id = "corr-123"
        event2.timestamp = datetime.now() + timedelta(seconds=10)
        
        events = [event1, event2]
        
        correlations = await collector._correlate_events(events)
        
        assert len(correlations) == 1
        assert correlations[0]['correlation_id'] == "corr-123"
        assert len(correlations[0]['events']) == 2

    @pytest.mark.asyncio
    async def test_correlate_events_no_correlation(self, collector):
        """Testa correlação sem eventos correlacionados"""
        event1 = sample_event()
        event1.correlation_id = None
        
        event2 = sample_event()
        event2.id = "test_event_2"
        event2.correlation_id = None
        
        events = [event1, event2]
        
        correlations = await collector._correlate_events(events)
        
        assert len(correlations) == 0

    @pytest.mark.asyncio
    async def test_handle_anomalies(self, collector, mock_redis_manager):
        """Testa processamento de anomalias"""
        anomaly_event = sample_event()
        anomaly_event.metadata['anomaly_score'] = 0.95
        anomaly_event.metadata['anomaly_type'] = 'outlier'
        
        anomalies = [anomaly_event]
        
        await collector._handle_anomalies(anomalies)
        
        mock_redis_manager.set.assert_called_once()
        call_args = mock_redis_manager.set.call_args
        assert 'alert:anomaly:test_event_1' in call_args[0]

    @pytest.mark.asyncio
    async def test_handle_correlations(self, collector, mock_redis_manager):
        """Testa processamento de correlações"""
        correlation = {
            'correlation_id': 'corr-123',
            'events': [sample_event()],
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(seconds=10),
            'duration': 10.0,
            'event_types': ['system_metric'],
            'severities': ['medium']
        }
        
        correlations = [correlation]
        
        await collector._handle_correlations(correlations)
        
        mock_redis_manager.set.assert_called_once()
        call_args = mock_redis_manager.set.call_args
        assert 'correlation:corr-123' in call_args[0]

    @pytest.mark.asyncio
    async def test_store_events(self, collector, mock_redis_manager):
        """Testa armazenamento de eventos"""
        events = [sample_event()]
        
        await collector._store_events(events)
        
        # Verificar se foram feitas as chamadas para armazenar
        assert mock_redis_manager.set.call_count >= 1
        assert mock_redis_manager.lpush.call_count >= 2  # type e severity
        assert mock_redis_manager.expire.call_count >= 2

    @pytest.mark.asyncio
    async def test_log_events(self, collector, mock_structured_logger):
        """Testa registro de eventos"""
        events = [sample_event()]
        
        await collector._log_events(events)
        
        mock_structured_logger.log_event.assert_called_once()

    def test_get_health_status(self, collector):
        """Testa obtenção do status de saúde"""
        collector.is_running = True
        
        status = asyncio.run(collector.get_health_status())
        
        assert status['is_running'] is True
        assert status['active_sources'] == 0  # Fontes não conectadas
        assert status['total_sources'] == 3
        assert status['recent_events_count'] == 0
        assert status['collection_interval'] == 60
        assert len(status['sources_health']) == 3

    def test_get_events_summary(self, collector):
        """Testa obtenção do resumo de eventos"""
        # Adicionar eventos recentes
        collector.recent_events = [
            sample_event(),
            sample_event()  # Mesmo evento, mas será tratado como diferente
        ]
        collector.recent_events[1].id = "test_event_2"
        
        summary = asyncio.run(collector.get_events_summary(24))
        
        assert summary['period_hours'] == 24
        assert summary['total_events'] == 2
        assert 'system_metric' in summary['events_by_type']
        assert 'medium' in summary['events_by_severity']
        assert 'system_metrics' in summary['events_by_source']

    def test_get_events_summary_empty(self, collector):
        """Testa resumo de eventos vazio"""
        summary = asyncio.run(collector.get_events_summary(24))
        
        assert summary['total_events'] == 0
        assert summary['events_by_type'] == {}
        assert summary['events_by_severity'] == {}
        assert summary['events_by_source'] == {}

    def test_get_events_summary_error(self, collector):
        """Testa resumo de eventos com erro"""
        # Simular erro
        with patch.object(collector, 'recent_events', side_effect=Exception("Test error")):
            summary = asyncio.run(collector.get_events_summary(24))
            
            assert 'error' in summary
            assert summary['total_events'] == 0

def sample_event():
    """Cria um evento de exemplo para testes"""
    return Event(
        id="test_event_1",
        type=EventType.SYSTEM_METRIC,
        source="system_metrics",
        severity=EventSeverity.MEDIUM,
        timestamp=datetime.now(),
        data={
            'metric_name': 'cpu_usage',
            'value': 75.5,
            'unit': '%'
        },
        metadata={
            'collection_interval': 60,
            'thresholds': SYSTEM_METRICS_CONFIG['thresholds']
        },
        correlation_id="corr-123",
        user_id="user-456"
    )

class TestEvent:
    """Testes para a classe Event"""

    def test_event_creation(self):
        """Testa criação de evento"""
        event = Event(
            id="test_event",
            type=EventType.SYSTEM_METRIC,
            source="test_source",
            severity=EventSeverity.HIGH,
            timestamp=datetime.now(),
            data={'test': 'data'},
            metadata={'meta': 'info'},
            correlation_id="corr-123",
            user_id="user-456",
            session_id="session-789"
        )
        
        assert event.id == "test_event"
        assert event.type == EventType.SYSTEM_METRIC
        assert event.source == "test_source"
        assert event.severity == EventSeverity.HIGH
        assert event.data == {'test': 'data'}
        assert event.metadata == {'meta': 'info'}
        assert event.correlation_id == "corr-123"
        assert event.user_id == "user-456"
        assert event.session_id == "session-789"

    def test_event_optional_fields(self):
        """Testa criação de evento com campos opcionais"""
        event = Event(
            id="test_event",
            type=EventType.APPLICATION_LOG,
            source="test_source",
            severity=EventSeverity.LOW,
            timestamp=datetime.now(),
            data={},
            metadata={}
        )
        
        assert event.correlation_id is None
        assert event.user_id is None
        assert event.session_id is None

class TestEventType:
    """Testes para EventType"""

    def test_event_type_values(self):
        """Testa valores dos tipos de evento"""
        assert EventType.SYSTEM_METRIC.value == "system_metric"
        assert EventType.APPLICATION_LOG.value == "application_log"
        assert EventType.DATABASE_QUERY.value == "database_query"
        assert EventType.API_REQUEST.value == "api_request"
        assert EventType.ERROR_EVENT.value == "error_event"
        assert EventType.PERFORMANCE_METRIC.value == "performance_metric"
        assert EventType.SECURITY_EVENT.value == "security_event"
        assert EventType.USER_ACTION.value == "user_action"
        assert EventType.BUSINESS_METRIC.value == "business_metric"
        assert EventType.INFRASTRUCTURE_ALERT.value == "infrastructure_alert"

class TestEventSeverity:
    """Testes para EventSeverity"""

    def test_event_severity_values(self):
        """Testa valores das severidades de evento"""
        assert EventSeverity.LOW.value == "low"
        assert EventSeverity.MEDIUM.value == "medium"
        assert EventSeverity.HIGH.value == "high"
        assert EventSeverity.CRITICAL.value == "critical"

    def test_severity_comparison(self):
        """Testa comparação de severidades"""
        assert EventSeverity.CRITICAL.value > EventSeverity.HIGH.value
        assert EventSeverity.HIGH.value > EventSeverity.MEDIUM.value
        assert EventSeverity.MEDIUM.value > EventSeverity.LOW.value 