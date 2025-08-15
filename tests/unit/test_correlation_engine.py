"""
Testes Unitários - Engine de Correlação
Omni Keywords Finder

Tracing ID: TEST_CORRELATION_ENGINE_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes de Engine de Correlação

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from infrastructure.aiops.correlation_engine import (
    CorrelationEngine, CorrelationMethod
)
from infrastructure.aiops.intelligent_collector import (
    Event, EventType, EventSeverity
)

# Configuração de teste baseada no código real
CORRELATION_CONFIG = {
    'methods': [CorrelationMethod.TEMPORAL, CorrelationMethod.CAUSAL],
    'window_minutes': 10,
    'min_correlation_events': 2,
    'alert_threshold': 0.8
}

@pytest.fixture
def sample_events():
    """Eventos de exemplo baseados no código real"""
    base_time = datetime.now()
    return [
        Event(
            id="event_1",
            type=EventType.SYSTEM_METRIC,
            source="system_metrics",
            severity=EventSeverity.MEDIUM,
            timestamp=base_time,
            data={'metric_name': 'cpu_usage', 'value': 75.5},
            metadata={},
            correlation_id="corr-123"
        ),
        Event(
            id="event_2",
            type=EventType.APPLICATION_LOG,
            source="application_logs",
            severity=EventSeverity.HIGH,
            timestamp=base_time + timedelta(seconds=30),
            data={'message': 'High CPU detected', 'level': 'WARNING'},
            metadata={},
            correlation_id="corr-123"
        ),
        Event(
            id="event_3",
            type=EventType.ERROR_EVENT,
            source="system_metrics",
            severity=EventSeverity.CRITICAL,
            timestamp=base_time + timedelta(seconds=60),
            data={'error': 'System overload'},
            metadata={},
            correlation_id="corr-123"
        ),
        Event(
            id="event_4",
            type=EventType.DATABASE_QUERY,
            source="database_queries",
            severity=EventSeverity.MEDIUM,
            timestamp=base_time + timedelta(seconds=90),
            data={'query': 'SELECT * FROM users', 'execution_time': 1500},
            metadata={},
            correlation_id="corr-124"
        ),
        Event(
            id="event_5",
            type=EventType.API_REQUEST,
            source="api_gateway",
            severity=EventSeverity.LOW,
            timestamp=base_time + timedelta(seconds=120),
            data={'endpoint': '/api/users', 'response_time': 200},
            metadata={},
            correlation_id="corr-124"
        )
    ]

@pytest.fixture
def correlation_engine():
    """Instância da engine de correlação"""
    return CorrelationEngine(CORRELATION_CONFIG)

class TestCorrelationEngine:
    """Testes para CorrelationEngine"""

    def test_initialization(self, correlation_engine):
        """Testa inicialização da engine"""
        assert correlation_engine.config == CORRELATION_CONFIG
        assert correlation_engine.methods == [CorrelationMethod.TEMPORAL, CorrelationMethod.CAUSAL]
        assert correlation_engine.window_minutes == 10
        assert correlation_engine.min_correlation_events == 2
        assert correlation_engine.alert_threshold == 0.8

    def test_initialization_default_config(self):
        """Testa inicialização com configuração padrão"""
        engine = CorrelationEngine()
        assert engine.methods == [CorrelationMethod.TEMPORAL, CorrelationMethod.CAUSAL]
        assert engine.window_minutes == 10
        assert engine.min_correlation_events == 2
        assert engine.alert_threshold == 0.8

class TestTemporalPatterns:
    """Testes para detecção de padrões temporais"""

    def test_detect_temporal_patterns_success(self, correlation_engine, sample_events):
        """Testa detecção bem-sucedida de padrões temporais"""
        correlations = correlation_engine.detect_temporal_patterns(sample_events)
        
        assert len(correlations) >= 1
        # Verificar se há correlação para corr-123 (3 eventos)
        corr_123 = next((c for c in correlations if c['correlation_id'] == 'corr-123'), None)
        assert corr_123 is not None
        assert len(corr_123['event_ids']) == 3
        assert corr_123['method'] == CorrelationMethod.TEMPORAL.value

    def test_detect_temporal_patterns_empty_events(self, correlation_engine):
        """Testa detecção com lista vazia de eventos"""
        correlations = correlation_engine.detect_temporal_patterns([])
        assert correlations == []

    def test_detect_temporal_patterns_single_event(self, correlation_engine, sample_events):
        """Testa detecção com apenas um evento"""
        correlations = correlation_engine.detect_temporal_patterns([sample_events[0]])
        assert correlations == []

    def test_detect_temporal_patterns_different_correlation_ids(self, correlation_engine, sample_events):
        """Testa detecção com diferentes correlation_ids"""
        correlations = correlation_engine.detect_temporal_patterns(sample_events)
        
        # Deve detectar correlações para ambos os correlation_ids
        corr_123_count = len([c for c in correlations if c['correlation_id'] == 'corr-123'])
        corr_124_count = len([c for c in correlations if c['correlation_id'] == 'corr-124'])
        
        assert corr_123_count >= 1
        assert corr_124_count >= 1

    def test_detect_temporal_patterns_window_limit(self, correlation_engine):
        """Testa limite de janela temporal"""
        base_time = datetime.now()
        events = [
            Event(
                id="event_1",
                type=EventType.SYSTEM_METRIC,
                source="system_metrics",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time,
                data={},
                metadata={},
                correlation_id="corr-test"
            ),
            Event(
                id="event_2",
                type=EventType.APPLICATION_LOG,
                source="application_logs",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time + timedelta(minutes=15),  # Fora da janela
                data={},
                metadata={},
                correlation_id="corr-test"
            )
        ]
        
        correlations = correlation_engine.detect_temporal_patterns(events)
        # Não deve correlacionar eventos fora da janela
        assert len(correlations) == 0

class TestCausalityDetection:
    """Testes para detecção de causalidade"""

    def test_detect_causality_success(self, correlation_engine, sample_events):
        """Testa detecção bem-sucedida de causalidade"""
        correlations = correlation_engine.detect_causality(sample_events)
        
        assert len(correlations) >= 1
        # Verificar estrutura da correlação causal
        causal_corr = correlations[0]
        assert 'cause_event_id' in causal_corr
        assert 'effect_event_id' in causal_corr
        assert 'cause_type' in causal_corr
        assert 'effect_type' in causal_corr
        assert 'delta_seconds' in causal_corr
        assert causal_corr['method'] == CorrelationMethod.CAUSAL.value

    def test_detect_causality_empty_events(self, correlation_engine):
        """Testa detecção com lista vazia de eventos"""
        correlations = correlation_engine.detect_causality([])
        assert correlations == []

    def test_detect_causality_single_event(self, correlation_engine, sample_events):
        """Testa detecção com apenas um evento"""
        correlations = correlation_engine.detect_causality([sample_events[0]])
        assert correlations == []

    def test_detect_causality_different_types(self, correlation_engine):
        """Testa detecção entre tipos diferentes de eventos"""
        base_time = datetime.now()
        events = [
            Event(
                id="cause_event",
                type=EventType.SYSTEM_METRIC,
                source="system_metrics",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time,
                data={},
                metadata={}
            ),
            Event(
                id="effect_event",
                type=EventType.ERROR_EVENT,
                source="application_logs",
                severity=EventSeverity.HIGH,
                timestamp=base_time + timedelta(seconds=30),
                data={},
                metadata={}
            )
        ]
        
        correlations = correlation_engine.detect_causality(events)
        assert len(correlations) == 1
        assert correlations[0]['cause_type'] == 'system_metric'
        assert correlations[0]['effect_type'] == 'error_event'

    def test_detect_causality_same_type(self, correlation_engine):
        """Testa que não detecta causalidade entre eventos do mesmo tipo"""
        base_time = datetime.now()
        events = [
            Event(
                id="event_1",
                type=EventType.SYSTEM_METRIC,
                source="system_metrics",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time,
                data={},
                metadata={}
            ),
            Event(
                id="event_2",
                type=EventType.SYSTEM_METRIC,
                source="system_metrics",
                severity=EventSeverity.HIGH,
                timestamp=base_time + timedelta(seconds=30),
                data={},
                metadata={}
            )
        ]
        
        correlations = correlation_engine.detect_causality(events)
        assert len(correlations) == 0

class TestAlertGeneration:
    """Testes para geração de alertas"""

    def test_generate_alerts_success(self, correlation_engine):
        """Testa geração bem-sucedida de alertas"""
        correlation = {
            'correlation_id': 'corr-123',
            'event_ids': ['event_1', 'event_2', 'event_3'],
            'severities': ['medium', 'high', 'critical'],
            'duration': 120.0,
            'event_types': ['system_metric', 'application_log', 'error_event'],
            'method': CorrelationMethod.TEMPORAL.value
        }
        
        alerts = correlation_engine.generate_alerts([correlation])
        
        assert len(alerts) == 1
        alert = alerts[0]
        assert 'alert_id' in alert
        assert alert['correlation_id'] == 'corr-123'
        assert alert['alert_type'] == 'error_correlation'
        assert alert['severity'] == 'critical'
        assert alert['score'] > 0.8
        assert 'message' in alert

    def test_generate_alerts_empty_correlations(self, correlation_engine):
        """Testa geração com lista vazia de correlações"""
        alerts = correlation_engine.generate_alerts([])
        assert alerts == []

    def test_generate_alerts_low_score(self, correlation_engine):
        """Testa que não gera alerta para score baixo"""
        correlation = {
            'correlation_id': 'corr-123',
            'event_ids': ['event_1'],
            'severities': ['low'],
            'duration': 10.0,
            'event_types': ['api_request'],
            'method': CorrelationMethod.TEMPORAL.value
        }
        
        alerts = correlation_engine.generate_alerts([correlation])
        assert len(alerts) == 0

    def test_calculate_alert_score(self, correlation_engine):
        """Testa cálculo de score de alerta"""
        # Score alto: muitos eventos críticos
        high_score_corr = {
            'event_ids': ['event_1', 'event_2', 'event_3', 'event_4'],
            'severities': ['critical', 'critical', 'high'],
            'duration': 400.0,
            'event_types': ['error_event', 'security_event']
        }
        
        score = correlation_engine._calculate_alert_score(high_score_corr)
        assert score > 0.8
        
        # Score baixo: poucos eventos de baixa severidade
        low_score_corr = {
            'event_ids': ['event_1'],
            'severities': ['low'],
            'duration': 10.0,
            'event_types': ['api_request']
        }
        
        score = correlation_engine._calculate_alert_score(low_score_corr)
        assert score < 0.5

    def test_determine_alert_type(self, correlation_engine):
        """Testa determinação do tipo de alerta"""
        # Error correlation
        error_corr = {
            'event_types': ['error_event', 'system_metric'],
            'method': CorrelationMethod.TEMPORAL.value
        }
        assert correlation_engine._determine_alert_type(error_corr) == 'error_correlation'
        
        # Security correlation
        security_corr = {
            'event_types': ['security_event', 'api_request'],
            'method': CorrelationMethod.TEMPORAL.value
        }
        assert correlation_engine._determine_alert_type(security_corr) == 'security_correlation'
        
        # Causal chain
        causal_corr = {
            'event_types': ['system_metric', 'application_log'],
            'method': CorrelationMethod.CAUSAL.value
        }
        assert correlation_engine._determine_alert_type(causal_corr) == 'causal_chain'

    def test_determine_alert_severity(self, correlation_engine):
        """Testa determinação da severidade do alerta"""
        # Critical
        critical_corr = {
            'severities': ['critical'],
            'event_ids': ['event_1', 'event_2', 'event_3']
        }
        assert correlation_engine._determine_alert_severity(critical_corr) == 'critical'
        
        # High
        high_corr = {
            'severities': ['high'],
            'event_ids': ['event_1', 'event_2']
        }
        assert correlation_engine._determine_alert_severity(high_corr) == 'high'
        
        # Medium
        medium_corr = {
            'severities': ['medium'],
            'event_ids': ['event_1']
        }
        assert correlation_engine._determine_alert_severity(medium_corr) == 'medium'

    def test_generate_alert_message(self, correlation_engine):
        """Testa geração de mensagem de alerta"""
        # Temporal pattern
        temporal_corr = {
            'method': CorrelationMethod.TEMPORAL.value,
            'event_ids': ['event_1', 'event_2', 'event_3'],
            'event_types': ['system_metric', 'application_log'],
            'duration': 60.0
        }
        message = correlation_engine._generate_alert_message(temporal_corr)
        assert 'Padrão temporal detectado' in message
        assert '3 eventos' in message
        
        # Causal relation
        causal_corr = {
            'method': CorrelationMethod.CAUSAL.value,
            'cause_type': 'system_metric',
            'effect_type': 'error_event',
            'delta_seconds': 30.0
        }
        message = correlation_engine._generate_alert_message(causal_corr)
        assert 'Relação causal detectada' in message
        assert 'system_metric -> error_event' in message

class TestCorrelationIntegration:
    """Testes de integração da correlação"""

    def test_correlate_success(self, correlation_engine, sample_events):
        """Testa correlação completa bem-sucedida"""
        correlations = correlation_engine.correlate(sample_events)
        
        assert len(correlations) >= 1
        # Verificar que contém ambos os tipos de correlação
        temporal_corrs = [c for c in correlations if c['method'] == CorrelationMethod.TEMPORAL.value]
        causal_corrs = [c for c in correlations if c['method'] == CorrelationMethod.CAUSAL.value]
        
        assert len(temporal_corrs) >= 1
        assert len(causal_corrs) >= 1

    def test_correlate_empty_events(self, correlation_engine):
        """Testa correlação com lista vazia"""
        correlations = correlation_engine.correlate([])
        assert correlations == []

    def test_correlate_single_method(self):
        """Testa correlação com apenas um método"""
        config = {
            'methods': [CorrelationMethod.TEMPORAL],
            'window_minutes': 10,
            'min_correlation_events': 2
        }
        engine = CorrelationEngine(config)
        
        base_time = datetime.now()
        events = [
            Event(
                id="event_1",
                type=EventType.SYSTEM_METRIC,
                source="system_metrics",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time,
                data={},
                metadata={},
                correlation_id="corr-test"
            ),
            Event(
                id="event_2",
                type=EventType.APPLICATION_LOG,
                source="application_logs",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time + timedelta(seconds=30),
                data={},
                metadata={},
                correlation_id="corr-test"
            )
        ]
        
        correlations = engine.correlate(events)
        assert len(correlations) == 1
        assert correlations[0]['method'] == CorrelationMethod.TEMPORAL.value

    def test_correlate_remove_duplicates(self, correlation_engine):
        """Testa remoção de duplicatas na correlação"""
        # Criar eventos que gerariam duplicatas
        base_time = datetime.now()
        events = [
            Event(
                id="event_1",
                type=EventType.SYSTEM_METRIC,
                source="system_metrics",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time,
                data={},
                metadata={},
                correlation_id="corr-test"
            ),
            Event(
                id="event_2",
                type=EventType.APPLICATION_LOG,
                source="application_logs",
                severity=EventSeverity.MEDIUM,
                timestamp=base_time + timedelta(seconds=30),
                data={},
                metadata={},
                correlation_id="corr-test"
            )
        ]
        
        correlations = correlation_engine.correlate(events)
        # Verificar que não há duplicatas
        correlation_keys = [(c['correlation_id'], c['method']) for c in correlations]
        assert len(correlation_keys) == len(set(correlation_keys))

class TestCorrelationMethod:
    """Testes para CorrelationMethod"""

    def test_correlation_method_values(self):
        """Testa valores dos métodos de correlação"""
        assert CorrelationMethod.TEMPORAL.value == "temporal"
        assert CorrelationMethod.CAUSAL.value == "causal"
        assert CorrelationMethod.FREQUENCY.value == "frequency"
        assert CorrelationMethod.CUSTOM.value == "custom" 