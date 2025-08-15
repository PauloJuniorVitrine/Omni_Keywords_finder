"""
Testes Unitários - Sistema de Detecção de Anomalias
Omni Keywords Finder

Tracing ID: TEST_ANOMALY_DETECTOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes de Detecção de Anomalias

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from infrastructure.aiops.ml_models.anomaly_detector import (
    AnomalyDetector, FeatureExtractor, AnomalyAlgorithm, 
    AnomalyType, AnomalyResult
)
from infrastructure.aiops.intelligent_collector import (
    Event, EventType, EventSeverity
)

# Configuração de teste baseada no código real
ANOMALY_CONFIG = {
    'algorithms': [AnomalyAlgorithm.ISOLATION_FOREST],
    'contamination': 0.1,
    'min_samples': 5,
    'model_path': 'test_models'
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
        ),
        # Eventos anômalos para teste
        Event(
            id="anomaly_1",
            type=EventType.SYSTEM_METRIC,
            source="system_metrics",
            severity=EventSeverity.CRITICAL,
            timestamp=base_time + timedelta(seconds=150),
            data={'metric_name': 'cpu_usage', 'value': 98.5},  # CPU muito alto
            metadata={},
            correlation_id="corr-125"
        ),
        Event(
            id="anomaly_2",
            type=EventType.DATABASE_QUERY,
            source="database_queries",
            severity=EventSeverity.HIGH,
            timestamp=base_time + timedelta(seconds=180),
            data={'query': 'SELECT * FROM large_table', 'execution_time': 15000},  # Query muito lenta
            metadata={},
            correlation_id="corr-125"
        )
    ]

@pytest.fixture
def feature_extractor():
    """Instância do extrator de features"""
    return FeatureExtractor()

@pytest.fixture
def anomaly_detector():
    """Instância do detector de anomalias"""
    return AnomalyDetector(ANOMALY_CONFIG)

@pytest.fixture
def temp_model_dir():
    """Diretório temporário para modelos"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

class TestFeatureExtractor:
    """Testes para FeatureExtractor"""

    def test_initialization(self, feature_extractor):
        """Testa inicialização do extrator de features"""
        assert feature_extractor.config == {}
        assert feature_extractor.scalers == {}
        assert feature_extractor.feature_names == []

    def test_extract_features_empty_events(self, feature_extractor):
        """Testa extração com lista vazia de eventos"""
        features_df = feature_extractor.extract_features([])
        assert features_df.empty

    def test_extract_features_system_metric(self, feature_extractor):
        """Testa extração de features de métrica do sistema"""
        event = Event(
            id="test_event",
            type=EventType.SYSTEM_METRIC,
            source="system_metrics",
            severity=EventSeverity.HIGH,
            timestamp=datetime.now(),
            data={'metric_name': 'cpu_usage', 'value': 85.5},
            metadata={}
        )
        
        features_df = feature_extractor.extract_features([event])
        
        assert not features_df.empty
        assert 'metric_value' in features_df.columns
        assert 'metric_name_numeric' in features_df.columns
        assert features_df.iloc[0]['metric_value'] == 85.5
        assert features_df.iloc[0]['severity_numeric'] == 3.0  # HIGH

    def test_extract_features_application_log(self, feature_extractor):
        """Testa extração de features de log da aplicação"""
        event = Event(
            id="test_event",
            type=EventType.APPLICATION_LOG,
            source="application_logs",
            severity=EventSeverity.ERROR,
            timestamp=datetime.now(),
            data={'message': 'Database connection failed', 'level': 'ERROR'},
            metadata={}
        )
        
        features_df = feature_extractor.extract_features([event])
        
        assert not features_df.empty
        assert 'log_level_numeric' in features_df.columns
        assert 'message_length' in features_df.columns
        assert features_df.iloc[0]['log_level_numeric'] == 4.0  # ERROR
        assert features_df.iloc[0]['message_length'] == 25

    def test_extract_features_database_query(self, feature_extractor):
        """Testa extração de features de query do banco"""
        event = Event(
            id="test_event",
            type=EventType.DATABASE_QUERY,
            source="database_queries",
            severity=EventSeverity.MEDIUM,
            timestamp=datetime.now(),
            data={'query': 'SELECT * FROM users', 'execution_time': 2500, 'rows_affected': 100},
            metadata={}
        )
        
        features_df = feature_extractor.extract_features([event])
        
        assert not features_df.empty
        assert 'execution_time' in features_df.columns
        assert 'rows_affected' in features_df.columns
        assert features_df.iloc[0]['execution_time'] == 2500.0
        assert features_df.iloc[0]['rows_affected'] == 100.0

    def test_extract_features_api_request(self, feature_extractor):
        """Testa extração de features de requisição API"""
        event = Event(
            id="test_event",
            type=EventType.API_REQUEST,
            source="api_gateway",
            severity=EventSeverity.LOW,
            timestamp=datetime.now(),
            data={'endpoint': '/api/users', 'response_time': 150},
            metadata={}
        )
        
        features_df = feature_extractor.extract_features([event])
        
        assert not features_df.empty
        assert 'response_time' in features_df.columns
        assert 'endpoint_numeric' in features_df.columns
        assert features_df.iloc[0]['response_time'] == 150.0

    def test_extract_features_error_event(self, feature_extractor):
        """Testa extração de features de evento de erro"""
        event = Event(
            id="test_event",
            type=EventType.ERROR_EVENT,
            source="system_metrics",
            severity=EventSeverity.CRITICAL,
            timestamp=datetime.now(),
            data={'error': 'System crash detected'},
            metadata={}
        )
        
        features_df = feature_extractor.extract_features([event])
        
        assert not features_df.empty
        assert 'error_message_length' in features_df.columns
        assert features_df.iloc[0]['error_message_length'] == 20

    def test_extract_features_multiple_events(self, feature_extractor, sample_events):
        """Testa extração de features de múltiplos eventos"""
        features_df = feature_extractor.extract_features(sample_events)
        
        assert len(features_df) == len(sample_events)
        assert len(features_df.columns) > 0
        assert 'timestamp_hour' in features_df.columns
        assert 'severity_numeric' in features_df.columns
        assert 'event_type_numeric' in features_df.columns

    def test_severity_to_numeric(self, feature_extractor):
        """Testa conversão de severidade para numérico"""
        assert feature_extractor._severity_to_numeric(EventSeverity.LOW) == 1.0
        assert feature_extractor._severity_to_numeric(EventSeverity.MEDIUM) == 2.0
        assert feature_extractor._severity_to_numeric(EventSeverity.HIGH) == 3.0
        assert feature_extractor._severity_to_numeric(EventSeverity.CRITICAL) == 4.0

    def test_event_type_to_numeric(self, feature_extractor):
        """Testa conversão de tipo de evento para numérico"""
        assert feature_extractor._event_type_to_numeric(EventType.SYSTEM_METRIC) == 1.0
        assert feature_extractor._event_type_to_numeric(EventType.APPLICATION_LOG) == 2.0
        assert feature_extractor._event_type_to_numeric(EventType.DATABASE_QUERY) == 3.0
        assert feature_extractor._event_type_to_numeric(EventType.API_REQUEST) == 4.0
        assert feature_extractor._event_type_to_numeric(EventType.ERROR_EVENT) == 5.0

    def test_source_to_numeric(self, feature_extractor):
        """Testa conversão de fonte para numérico"""
        assert feature_extractor._source_to_numeric('system_metrics') == 1.0
        assert feature_extractor._source_to_numeric('application_logs') == 2.0
        assert feature_extractor._source_to_numeric('database_queries') == 3.0
        assert feature_extractor._source_to_numeric('api_gateway') == 4.0
        assert feature_extractor._source_to_numeric('unknown_source') == 0.0

    def test_metric_name_to_numeric(self, feature_extractor):
        """Testa conversão de nome de métrica para numérico"""
        assert feature_extractor._metric_name_to_numeric('cpu_usage') == 1.0
        assert feature_extractor._metric_name_to_numeric('memory_usage') == 2.0
        assert feature_extractor._metric_name_to_numeric('disk_usage') == 3.0
        assert feature_extractor._metric_name_to_numeric('unknown_metric') == 0.0

    def test_log_level_to_numeric(self, feature_extractor):
        """Testa conversão de nível de log para numérico"""
        assert feature_extractor._log_level_to_numeric('DEBUG') == 1.0
        assert feature_extractor._log_level_to_numeric('INFO') == 2.0
        assert feature_extractor._log_level_to_numeric('WARNING') == 3.0
        assert feature_extractor._log_level_to_numeric('ERROR') == 4.0
        assert feature_extractor._log_level_to_numeric('CRITICAL') == 5.0
        assert feature_extractor._log_level_to_numeric('unknown') == 0.0

class TestAnomalyDetector:
    """Testes para AnomalyDetector"""

    def test_initialization(self, anomaly_detector):
        """Testa inicialização do detector de anomalias"""
        assert anomaly_detector.config == ANOMALY_CONFIG
        assert anomaly_detector.algorithms == [AnomalyAlgorithm.ISOLATION_FOREST]
        assert anomaly_detector.contamination == 0.1
        assert anomaly_detector.min_samples == 5
        assert anomaly_detector.is_trained is False
        assert anomaly_detector.models == {}
        assert anomaly_detector.scalers == {}

    def test_initialization_default_config(self):
        """Testa inicialização com configuração padrão"""
        detector = AnomalyDetector()
        assert detector.algorithms == [AnomalyAlgorithm.ISOLATION_FOREST]
        assert detector.contamination == 0.1
        assert detector.min_samples == 10

    def test_train_insufficient_data(self, anomaly_detector):
        """Testa treinamento com dados insuficientes"""
        events = [sample_events()[0]] * 3  # Apenas 3 eventos
        result = anomaly_detector.train(events)
        
        assert result['status'] == 'insufficient_data'
        assert 'Dados insuficientes' in result['message']

    def test_train_success(self, anomaly_detector, sample_events):
        """Testa treinamento bem-sucedido"""
        result = anomaly_detector.train(sample_events)
        
        assert result['status'] == 'success'
        assert 'isolation_forest' in result['models_trained']
        assert anomaly_detector.is_trained is True
        assert len(anomaly_detector.models) > 0
        assert len(anomaly_detector.scalers) > 0

    def test_train_empty_events(self, anomaly_detector):
        """Testa treinamento com lista vazia"""
        result = anomaly_detector.train([])
        assert result['status'] == 'insufficient_data'

    def test_detect_anomalies_not_trained(self, anomaly_detector, sample_events):
        """Testa detecção sem treinamento prévio"""
        results = anomaly_detector.detect_anomalies(sample_events)
        assert results == []

    def test_detect_anomalies_empty_events(self, anomaly_detector):
        """Testa detecção com lista vazia de eventos"""
        anomaly_detector.is_trained = True
        results = anomaly_detector.detect_anomalies([])
        assert results == []

    def test_detect_anomalies_success(self, anomaly_detector, sample_events):
        """Testa detecção bem-sucedida de anomalias"""
        # Treinar primeiro
        anomaly_detector.train(sample_events)
        
        # Detectar anomalias
        results = anomaly_detector.detect_anomalies(sample_events)
        
        assert len(results) > 0
        assert all(isinstance(result, AnomalyResult) for result in results)
        
        # Verificar estrutura dos resultados
        for result in results:
            assert hasattr(result, 'event_id')
            assert hasattr(result, 'is_anomaly')
            assert hasattr(result, 'score')
            assert hasattr(result, 'algorithm')
            assert hasattr(result, 'anomaly_type')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'features')
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'metadata')

    def test_determine_anomaly_type(self, anomaly_detector):
        """Testa determinação do tipo de anomalia"""
        # Sistema métrica com valor alto
        event = Event(
            id="test",
            type=EventType.SYSTEM_METRIC,
            source="system_metrics",
            severity=EventSeverity.MEDIUM,
            timestamp=datetime.now(),
            data={'value': 95.0},
            metadata={}
        )
        
        anomaly_type = anomaly_detector._determine_anomaly_type(event, -0.5, 'isolation_forest')
        assert anomaly_type == AnomalyType.POINT
        
        # Query lenta
        event = Event(
            id="test",
            type=EventType.DATABASE_QUERY,
            source="database_queries",
            severity=EventSeverity.MEDIUM,
            timestamp=datetime.now(),
            data={'execution_time': 8000},
            metadata={}
        )
        
        anomaly_type = anomaly_detector._determine_anomaly_type(event, -0.3, 'isolation_forest')
        assert anomaly_type == AnomalyType.TREND

    def test_calculate_confidence(self, anomaly_detector):
        """Testa cálculo de confiança"""
        # Isolation Forest
        confidence = anomaly_detector._calculate_confidence(-0.3, 'isolation_forest')
        assert 0.0 <= confidence <= 1.0
        
        # Score positivo (menos anômalo)
        confidence = anomaly_detector._calculate_confidence(0.2, 'isolation_forest')
        assert confidence < 0.5

    def test_extract_relevant_features(self, anomaly_detector):
        """Testa extração de features relevantes"""
        features = pd.Series({
            'metric_value': 85.5,
            'execution_time': 1500.0,
            'severity_numeric': 3.0,
            'event_type_numeric': 1.0,
            'timestamp_hour': 14.0,
            'unimportant_feature': 0.0
        })
        
        relevant = anomaly_detector._extract_relevant_features(features)
        
        assert 'metric_value' in relevant
        assert 'execution_time' in relevant
        assert 'severity_numeric' in relevant
        assert 'event_type_numeric' in relevant
        assert 'unimportant_feature' not in relevant

    def test_consolidate_results(self, anomaly_detector):
        """Testa consolidação de resultados"""
        base_time = datetime.now()
        
        # Criar resultados múltiplos para o mesmo evento
        results = [
            AnomalyResult(
                event_id="event_1",
                is_anomaly=True,
                score=-0.5,
                algorithm="isolation_forest",
                anomaly_type=AnomalyType.POINT,
                confidence=0.8,
                features={'metric_value': 85.5},
                timestamp=base_time,
                metadata={}
            ),
            AnomalyResult(
                event_id="event_1",
                is_anomaly=False,
                score=-0.2,
                algorithm="local_outlier_factor",
                anomaly_type=AnomalyType.CONTEXTUAL,
                confidence=0.6,
                features={'metric_value': 85.5},
                timestamp=base_time,
                metadata={}
            )
        ]
        
        consolidated = anomaly_detector._consolidate_results(results)
        
        assert len(consolidated) == 1
        consolidated_result = consolidated[0]
        assert consolidated_result.event_id == "event_1"
        assert consolidated_result.is_anomaly is True  # Maioria votou como anomalia
        assert consolidated_result.algorithm == "ensemble_2"
        assert len(consolidated_result.metadata['algorithms_used']) == 2

    def test_save_and_load_models(self, anomaly_detector, sample_events, temp_model_dir):
        """Testa salvamento e carregamento de modelos"""
        # Configurar diretório temporário
        anomaly_detector.model_path = Path(temp_model_dir)
        
        # Treinar modelos
        anomaly_detector.train(sample_events)
        
        # Salvar modelos
        anomaly_detector._save_models()
        
        # Verificar se arquivos foram criados
        assert (Path(temp_model_dir) / "isolation_forest_model.joblib").exists()
        assert (Path(temp_model_dir) / "isolation_forest_scaler.joblib").exists()
        assert (Path(temp_model_dir) / "config.json").exists()
        
        # Criar nova instância e carregar modelos
        new_detector = AnomalyDetector({'model_path': temp_model_dir})
        success = new_detector.load_models()
        
        assert success is True
        assert new_detector.is_trained is True
        assert len(new_detector.models) > 0
        assert len(new_detector.scalers) > 0

    def test_get_performance_metrics(self, anomaly_detector, sample_events):
        """Testa obtenção de métricas de performance"""
        # Antes do treinamento
        metrics = anomaly_detector.get_performance_metrics()
        assert metrics['is_trained'] is False
        assert len(metrics['algorithms']) == 0
        
        # Após treinamento
        anomaly_detector.train(sample_events)
        metrics = anomaly_detector.get_performance_metrics()
        
        assert metrics['is_trained'] is True
        assert len(metrics['algorithms']) > 0
        assert 'performance_metrics' in metrics
        assert metrics['total_models'] > 0

class TestAnomalyAlgorithm:
    """Testes para AnomalyAlgorithm"""

    def test_anomaly_algorithm_values(self):
        """Testa valores dos algoritmos de anomalia"""
        assert AnomalyAlgorithm.ISOLATION_FOREST.value == "isolation_forest"
        assert AnomalyAlgorithm.LOCAL_OUTLIER_FACTOR.value == "local_outlier_factor"
        assert AnomalyAlgorithm.STATISTICAL.value == "statistical"
        assert AnomalyAlgorithm.ENSEMBLE.value == "ensemble"

class TestAnomalyType:
    """Testes para AnomalyType"""

    def test_anomaly_type_values(self):
        """Testa valores dos tipos de anomalia"""
        assert AnomalyType.POINT.value == "point"
        assert AnomalyType.CONTEXTUAL.value == "contextual"
        assert AnomalyType.COLLECTIVE.value == "collective"
        assert AnomalyType.TREND.value == "trend"

class TestAnomalyResult:
    """Testes para AnomalyResult"""

    def test_anomaly_result_creation(self):
        """Testa criação de resultado de anomalia"""
        result = AnomalyResult(
            event_id="test_event",
            is_anomaly=True,
            score=-0.5,
            algorithm="isolation_forest",
            anomaly_type=AnomalyType.POINT,
            confidence=0.8,
            features={'metric_value': 85.5},
            timestamp=datetime.now(),
            metadata={'test': 'data'}
        )
        
        assert result.event_id == "test_event"
        assert result.is_anomaly is True
        assert result.score == -0.5
        assert result.algorithm == "isolation_forest"
        assert result.anomaly_type == AnomalyType.POINT
        assert result.confidence == 0.8
        assert result.features == {'metric_value': 85.5}
        assert 'test' in result.metadata 