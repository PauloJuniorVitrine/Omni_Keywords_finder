"""
Testes Unitários para AnomalyModels
AnomalyModels - Modelos de Machine Learning para detecção de anomalias

Prompt: Implementação de testes unitários para AnomalyModels
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_ANOMALY_MODELS_001_20250127
"""

import pytest
import numpy as np
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union

from infrastructure.observability.anomaly_models import (
    ModelType,
    ModelStatus,
    ModelConfig,
    ModelMetrics,
    ModelResult,
    BaseAnomalyModel,
    IsolationForestModel,
    OneClassSVMModel,
    LocalOutlierFactorModel,
    EnsembleAnomalyModel,
    AnomalyModelFactory
)


class TestModelType:
    """Testes para ModelType"""
    
    def test_model_type_values(self):
        """Testa valores do enum ModelType"""
        assert ModelType.ISOLATION_FOREST.value == "isolation_forest"
        assert ModelType.ONE_CLASS_SVM.value == "one_class_svm"
        assert ModelType.LOCAL_OUTLIER_FACTOR.value == "local_outlier_factor"
        assert ModelType.ELLIPTIC_ENVELOPE.value == "elliptic_envelope"
        assert ModelType.AUTOENCODER.value == "autoencoder"
        assert ModelType.LSTM.value == "lstm"
        assert ModelType.ENSEMBLE.value == "ensemble"
        assert ModelType.CUSTOM.value == "custom"
    
    def test_model_type_membership(self):
        """Testa membership do enum ModelType"""
        assert ModelType.ISOLATION_FOREST in ModelType
        assert ModelType.ONE_CLASS_SVM in ModelType
        assert ModelType.LOCAL_OUTLIER_FACTOR in ModelType
        assert ModelType.ENSEMBLE in ModelType


class TestModelStatus:
    """Testes para ModelStatus"""
    
    def test_model_status_values(self):
        """Testa valores do enum ModelStatus"""
        assert ModelStatus.NOT_TRAINED.value == "not_trained"
        assert ModelStatus.TRAINING.value == "training"
        assert ModelStatus.TRAINED.value == "trained"
        assert ModelStatus.EVALUATING.value == "evaluating"
        assert ModelStatus.EVALUATED.value == "evaluated"
        assert ModelStatus.ERROR.value == "error"
    
    def test_model_status_membership(self):
        """Testa membership do enum ModelStatus"""
        assert ModelStatus.NOT_TRAINED in ModelStatus
        assert ModelStatus.TRAINING in ModelStatus
        assert ModelStatus.TRAINED in ModelStatus
        assert ModelStatus.ERROR in ModelStatus


class TestModelConfig:
    """Testes para ModelConfig"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return {
            "model_type": ModelType.ISOLATION_FOREST,
            "name": "test_anomaly_model",
            "description": "Test anomaly detection model",
            "parameters": {"contamination": 0.1, "random_state": 42},
            "threshold": 0.5,
            "max_training_samples": 1000,
            "min_training_samples": 10,
            "retrain_interval": 3600,
            "evaluation_metrics": ["precision", "recall", "f1"]
        }
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        config = ModelConfig(**sample_config)
        
        assert config.model_type == ModelType.ISOLATION_FOREST
        assert config.name == "test_anomaly_model"
        assert config.description == "Test anomaly detection model"
        assert config.parameters == {"contamination": 0.1, "random_state": 42}
        assert config.threshold == 0.5
        assert config.max_training_samples == 1000
        assert config.min_training_samples == 10
        assert config.retrain_interval == 3600
        assert config.evaluation_metrics == ["precision", "recall", "f1"]
    
    def test_default_values(self):
        """Testa valores padrão"""
        config = ModelConfig(model_type=ModelType.ISOLATION_FOREST)
        
        assert config.model_type == ModelType.ISOLATION_FOREST
        assert config.name == ""
        assert config.description == ""
        assert config.parameters == {}
        assert config.threshold == 0.5
        assert config.max_training_samples == 10000
        assert config.min_training_samples == 50
        assert config.retrain_interval == 86400
        assert config.evaluation_metrics == ["precision", "recall"]
    
    def test_validation(self, sample_config):
        """Testa validações"""
        # Teste com threshold inválido
        with pytest.raises(ValueError):
            ModelConfig(model_type=ModelType.ISOLATION_FOREST, threshold=-0.1)
        
        with pytest.raises(ValueError):
            ModelConfig(model_type=ModelType.ISOLATION_FOREST, threshold=1.5)
        
        # Teste com max_training_samples menor que min_training_samples
        with pytest.raises(ValueError):
            ModelConfig(
                model_type=ModelType.ISOLATION_FOREST,
                max_training_samples=10,
                min_training_samples=100
            )
        
        # Teste com retrain_interval negativo
        with pytest.raises(ValueError):
            ModelConfig(model_type=ModelType.ISOLATION_FOREST, retrain_interval=-1)
    
    def test_serialization(self, sample_config):
        """Testa serialização"""
        config = ModelConfig(**sample_config)
        
        config_dict = config.to_dict()
        assert config_dict["model_type"] == "isolation_forest"
        assert config_dict["name"] == "test_anomaly_model"
        assert config_dict["threshold"] == 0.5
        assert config_dict["parameters"] == {"contamination": 0.1, "random_state": 42}
    
    def test_from_dict(self, sample_config):
        """Testa criação a partir de dicionário"""
        config = ModelConfig.from_dict(sample_config)
        
        assert config.model_type == ModelType.ISOLATION_FOREST
        assert config.name == "test_anomaly_model"
        assert config.threshold == 0.5


class TestModelMetrics:
    """Testes para ModelMetrics"""
    
    @pytest.fixture
    def sample_metrics(self):
        """Métricas de exemplo para testes"""
        return {
            "precision": 0.85,
            "recall": 0.78,
            "f1_score": 0.81,
            "accuracy": 0.92,
            "true_positives": 85,
            "false_positives": 15,
            "true_negatives": 920,
            "false_negatives": 22,
            "total_samples": 1042,
            "anomaly_rate": 0.102,
            "last_updated": time.time()
        }
    
    def test_initialization(self, sample_metrics):
        """Testa inicialização básica"""
        metrics = ModelMetrics(**sample_metrics)
        
        assert metrics.precision == 0.85
        assert metrics.recall == 0.78
        assert metrics.f1_score == 0.81
        assert metrics.accuracy == 0.92
        assert metrics.true_positives == 85
        assert metrics.false_positives == 15
        assert metrics.true_negatives == 920
        assert metrics.false_negatives == 22
        assert metrics.total_samples == 1042
        assert metrics.anomaly_rate == 0.102
    
    def test_default_values(self):
        """Testa valores padrão"""
        metrics = ModelMetrics()
        
        assert metrics.precision == 0.0
        assert metrics.recall == 0.0
        assert metrics.f1_score == 0.0
        assert metrics.accuracy == 0.0
        assert metrics.true_positives == 0
        assert metrics.false_positives == 0
        assert metrics.true_negatives == 0
        assert metrics.false_negatives == 0
        assert metrics.total_samples == 0
        assert metrics.anomaly_rate == 0.0
        assert metrics.last_updated > 0
    
    def test_validation(self, sample_metrics):
        """Testa validações"""
        # Teste com valores negativos
        with pytest.raises(ValueError):
            ModelMetrics(precision=-0.1)
        
        with pytest.raises(ValueError):
            ModelMetrics(recall=1.5)
        
        with pytest.raises(ValueError):
            ModelMetrics(true_positives=-1)
        
        # Teste com valores maiores que 1
        with pytest.raises(ValueError):
            ModelMetrics(precision=1.1)
        
        with pytest.raises(ValueError):
            ModelMetrics(recall=2.0)
    
    def test_calculate_metrics(self, sample_metrics):
        """Testa cálculo de métricas"""
        metrics = ModelMetrics(**sample_metrics)
        
        # Verificar que métricas calculadas estão corretas
        expected_f1 = 2 * (0.85 * 0.78) / (0.85 + 0.78)
        assert abs(metrics.f1_score - expected_f1) < 0.01
        
        expected_accuracy = (85 + 920) / 1042
        assert abs(metrics.accuracy - expected_accuracy) < 0.01
        
        expected_anomaly_rate = (85 + 22) / 1042
        assert abs(metrics.anomaly_rate - expected_anomaly_rate) < 0.01
    
    def test_serialization(self, sample_metrics):
        """Testa serialização"""
        metrics = ModelMetrics(**sample_metrics)
        
        metrics_dict = metrics.to_dict()
        assert metrics_dict["precision"] == 0.85
        assert metrics_dict["recall"] == 0.78
        assert metrics_dict["f1_score"] == 0.81
        assert metrics_dict["accuracy"] == 0.92


class TestModelResult:
    """Testes para ModelResult"""
    
    @pytest.fixture
    def sample_result(self):
        """Resultado de exemplo para testes"""
        return {
            "is_anomaly": True,
            "confidence": 0.85,
            "score": -0.75,
            "model_name": "test_model",
            "timestamp": time.time(),
            "features": [1.2, 3.4, 5.6],
            "metadata": {"threshold": 0.5, "method": "isolation_forest"}
        }
    
    def test_initialization(self, sample_result):
        """Testa inicialização básica"""
        result = ModelResult(**sample_result)
        
        assert result.is_anomaly == True
        assert result.confidence == 0.85
        assert result.score == -0.75
        assert result.model_name == "test_model"
        assert result.features == [1.2, 3.4, 5.6]
        assert result.metadata == {"threshold": 0.5, "method": "isolation_forest"}
    
    def test_default_values(self):
        """Testa valores padrão"""
        result = ModelResult(is_anomaly=False)
        
        assert result.is_anomaly == False
        assert result.confidence == 0.0
        assert result.score == 0.0
        assert result.model_name == ""
        assert result.timestamp > 0
        assert result.features == []
        assert result.metadata == {}
    
    def test_validation(self, sample_result):
        """Testa validações"""
        # Teste com confidence inválido
        with pytest.raises(ValueError):
            ModelResult(is_anomaly=True, confidence=-0.1)
        
        with pytest.raises(ValueError):
            ModelResult(is_anomaly=True, confidence=1.5)
    
    def test_serialization(self, sample_result):
        """Testa serialização"""
        result = ModelResult(**sample_result)
        
        result_dict = result.to_dict()
        assert result_dict["is_anomaly"] == True
        assert result_dict["confidence"] == 0.85
        assert result_dict["score"] == -0.75
        assert result_dict["model_name"] == "test_model"
        assert result_dict["features"] == [1.2, 3.4, 5.6]


class TestBaseAnomalyModel:
    """Testes para BaseAnomalyModel (classe abstrata)"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.ISOLATION_FOREST,
            name="test_model",
            threshold=0.5
        )
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        # Criar uma classe concreta para testar
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                self.model = Mock()
                return True
            
            def _predict_model(self, features):
                return ModelResult(
                    is_anomaly=features[0] > 0.5,
                    confidence=0.8,
                    score=features[0]
                )
        
        model = ConcreteAnomalyModel(sample_config)
        
        assert model.config == sample_config
        assert model.model is None
        assert model.status == ModelStatus.NOT_TRAINED
        assert model.metrics is not None
        assert len(model.training_data) == 0
        assert model.last_training_time == 0
    
    def test_add_training_data(self, sample_config):
        """Testa adição de dados de treinamento"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                return True
            
            def _predict_model(self, features):
                return ModelResult(is_anomaly=False, confidence=0.5, score=0.0)
        
        model = ConcreteAnomalyModel(sample_config)
        
        # Adicionar dados de treinamento
        model.add_training_data(1.5, is_anomaly=True)
        model.add_training_data(0.3, is_anomaly=False)
        
        assert len(model.training_data) == 2
        assert model.training_data[0]['data'] == 1.5
        assert model.training_data[0]['is_anomaly'] == True
        assert model.training_data[1]['data'] == 0.3
        assert model.training_data[1]['is_anomaly'] == False
    
    def test_extract_features(self, sample_config):
        """Testa extração de features"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                return True
            
            def _predict_model(self, features):
                return ModelResult(is_anomaly=False, confidence=0.5, score=0.0)
        
        model = ConcreteAnomalyModel(sample_config)
        
        # Teste com valor único
        features = model.extract_features(1.5)
        assert features == [1.5]
        
        # Teste com lista
        features = model.extract_features([1.0, 2.0, 3.0])
        assert features == [1.0, 2.0, 3.0]
        
        # Teste com tipo inválido
        with pytest.raises(ValueError):
            model.extract_features("invalid")
    
    def test_prepare_training_data(self, sample_config):
        """Testa preparação de dados de treinamento"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                return True
            
            def _predict_model(self, features):
                return ModelResult(is_anomaly=False, confidence=0.5, score=0.0)
        
        model = ConcreteAnomalyModel(sample_config)
        
        # Adicionar dados
        model.add_training_data(1.5, is_anomaly=True)
        model.add_training_data(0.3, is_anomaly=False)
        model.add_training_data(2.1, is_anomaly=True)
        
        X, y = model.prepare_training_data()
        
        assert len(X) == 3
        assert len(y) == 3
        assert X[0] == [1.5]
        assert X[1] == [0.3]
        assert X[2] == [2.1]
        assert y[0] == 1
        assert y[1] == 0
        assert y[2] == 1
    
    def test_train(self, sample_config):
        """Testa treinamento do modelo"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                self.model = Mock()
                return True
            
            def _predict_model(self, features):
                return ModelResult(is_anomaly=False, confidence=0.5, score=0.0)
        
        model = ConcreteAnomalyModel(sample_config)
        
        # Adicionar dados suficientes
        for i in range(20):
            model.add_training_data(i * 0.1, is_anomaly=(i > 15))
        
        success = model.train()
        assert success == True
        assert model.status == ModelStatus.TRAINED
        assert model.model is not None
        assert model.last_training_time > 0
    
    def test_train_insufficient_data(self, sample_config):
        """Testa treinamento com dados insuficientes"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                return True
            
            def _predict_model(self, features):
                return ModelResult(is_anomaly=False, confidence=0.5, score=0.0)
        
        model = ConcreteAnomalyModel(sample_config)
        
        # Adicionar poucos dados
        for i in range(5):
            model.add_training_data(i * 0.1, is_anomaly=False)
        
        success = model.train()
        assert success == False
        assert model.status == ModelStatus.NOT_TRAINED
    
    def test_predict(self, sample_config):
        """Testa predição"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                self.model = Mock()
                return True
            
            def _predict_model(self, features):
                return ModelResult(
                    is_anomaly=features[0] > 0.5,
                    confidence=0.8,
                    score=features[0]
                )
        
        model = ConcreteAnomalyModel(sample_config)
        
        # Treinar modelo
        for i in range(20):
            model.add_training_data(i * 0.1, is_anomaly=(i > 15))
        model.train()
        
        # Fazer predições
        result1 = model.predict(0.3)
        result2 = model.predict(0.8)
        
        assert result1.is_anomaly == False
        assert result2.is_anomaly == True
        assert result1.confidence == 0.8
        assert result2.confidence == 0.8
    
    def test_predict_without_training(self, sample_config):
        """Testa predição sem treinamento"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                return True
            
            def _predict_model(self, features):
                return ModelResult(is_anomaly=False, confidence=0.5, score=0.0)
        
        model = ConcreteAnomalyModel(sample_config)
        
        with pytest.raises(ValueError, match="Model not trained"):
            model.predict(1.0)
    
    def test_evaluate(self, sample_config):
        """Testa avaliação do modelo"""
        class ConcreteAnomalyModel(BaseAnomalyModel):
            def _train_model(self, X, y):
                self.model = Mock()
                return True
            
            def _predict_model(self, features):
                return ModelResult(
                    is_anomaly=features[0] > 0.5,
                    confidence=0.8,
                    score=features[0]
                )
        
        model = ConcreteAnomalyModel(sample_config)
        
        # Adicionar dados com anomalias conhecidas
        for i in range(50):
            model.add_training_data(i * 0.1, is_anomaly=(i > 40))
        
        # Treinar e avaliar
        model.train()
        metrics = model.evaluate()
        
        assert metrics is not None
        assert metrics.total_samples > 0
        assert model.status == ModelStatus.EVALUATED
    
    def test_abstract_methods(self, sample_config):
        """Testa que métodos abstratos não podem ser chamados"""
        model = BaseAnomalyModel(sample_config)
        
        X = np.array([[1.0], [2.0]])
        y = np.array([0, 1])
        
        with pytest.raises(NotImplementedError):
            model._train_model(X, y)
        
        with pytest.raises(NotImplementedError):
            model._predict_model([1.0])


class TestIsolationForestModel:
    """Testes para IsolationForestModel"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.ISOLATION_FOREST,
            name="isolation_forest_test",
            parameters={"contamination": 0.1, "random_state": 42}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo"""
        # Dados normais
        normal_data = np.random.normal(0, 1, 90)
        # Dados anômalos
        anomaly_data = np.random.normal(5, 1, 10)
        return np.concatenate([normal_data, anomaly_data])
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = IsolationForestModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is not None
            assert model.status == ModelStatus.NOT_TRAINED
    
    def test_initialization_without_sklearn(self, sample_config):
        """Testa inicialização sem sklearn"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', False):
            model = IsolationForestModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is None
    
    def test_train(self, sample_config, sample_data):
        """Testa treinamento do modelo"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = IsolationForestModel(sample_config)
            
            # Adicionar dados
            for i, data_point in enumerate(sample_data):
                model.add_training_data(data_point, is_anomaly=(i >= 90))
            
            success = model.train()
            assert success == True
            assert model.status == ModelStatus.TRAINED
    
    def test_predict(self, sample_config, sample_data):
        """Testa predição"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = IsolationForestModel(sample_config)
            
            # Treinar modelo
            for i, data_point in enumerate(sample_data):
                model.add_training_data(data_point, is_anomaly=(i >= 90))
            model.train()
            
            # Fazer predições
            result_normal = model.predict(0.0)
            result_anomaly = model.predict(6.0)
            
            assert isinstance(result_normal, ModelResult)
            assert isinstance(result_anomaly, ModelResult)
            assert result_normal.confidence >= 0
            assert result_anomaly.confidence >= 0


class TestOneClassSVMModel:
    """Testes para OneClassSVMModel"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.ONE_CLASS_SVM,
            name="one_class_svm_test",
            parameters={"nu": 0.1, "kernel": "rbf"}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo"""
        return np.random.normal(0, 1, 100)
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = OneClassSVMModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is not None
            assert model.status == ModelStatus.NOT_TRAINED
    
    def test_train(self, sample_config, sample_data):
        """Testa treinamento do modelo"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = OneClassSVMModel(sample_config)
            
            # Adicionar dados normais
            for data_point in sample_data:
                model.add_training_data(data_point, is_anomaly=False)
            
            success = model.train()
            assert success == True
            assert model.status == ModelStatus.TRAINED
    
    def test_predict(self, sample_config, sample_data):
        """Testa predição"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = OneClassSVMModel(sample_config)
            
            # Treinar modelo
            for data_point in sample_data:
                model.add_training_data(data_point, is_anomaly=False)
            model.train()
            
            # Fazer predições
            result_normal = model.predict(0.0)
            result_anomaly = model.predict(10.0)
            
            assert isinstance(result_normal, ModelResult)
            assert isinstance(result_anomaly, ModelResult)


class TestLocalOutlierFactorModel:
    """Testes para LocalOutlierFactorModel"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.LOCAL_OUTLIER_FACTOR,
            name="lof_test",
            parameters={"n_neighbors": 20, "contamination": 0.1}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo"""
        normal_data = np.random.normal(0, 1, 90)
        anomaly_data = np.random.normal(5, 1, 10)
        return np.concatenate([normal_data, anomaly_data])
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = LocalOutlierFactorModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is not None
            assert model.status == ModelStatus.NOT_TRAINED
    
    def test_train(self, sample_config, sample_data):
        """Testa treinamento do modelo"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = LocalOutlierFactorModel(sample_config)
            
            # Adicionar dados
            for i, data_point in enumerate(sample_data):
                model.add_training_data(data_point, is_anomaly=(i >= 90))
            
            success = model.train()
            assert success == True
            assert model.status == ModelStatus.TRAINED
    
    def test_predict(self, sample_config, sample_data):
        """Testa predição"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = LocalOutlierFactorModel(sample_config)
            
            # Treinar modelo
            for i, data_point in enumerate(sample_data):
                model.add_training_data(data_point, is_anomaly=(i >= 90))
            model.train()
            
            # Fazer predições
            result_normal = model.predict(0.0)
            result_anomaly = model.predict(6.0)
            
            assert isinstance(result_normal, ModelResult)
            assert isinstance(result_anomaly, ModelResult)


class TestEnsembleAnomalyModel:
    """Testes para EnsembleAnomalyModel"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.ENSEMBLE,
            name="ensemble_test",
            parameters={"voting_method": "majority", "weights": [0.4, 0.3, 0.3]}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo"""
        normal_data = np.random.normal(0, 1, 80)
        anomaly_data = np.random.normal(5, 1, 20)
        return np.concatenate([normal_data, anomaly_data])
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = EnsembleAnomalyModel(sample_config)
            
            assert model.config == sample_config
            assert len(model.models) > 0
            assert model.status == ModelStatus.NOT_TRAINED
    
    def test_train(self, sample_config, sample_data):
        """Testa treinamento do modelo"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = EnsembleAnomalyModel(sample_config)
            
            # Adicionar dados
            for i, data_point in enumerate(sample_data):
                model.add_training_data(data_point, is_anomaly=(i >= 80))
            
            success = model.train()
            assert success == True
            assert model.status == ModelStatus.TRAINED
    
    def test_predict(self, sample_config, sample_data):
        """Testa predição"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = EnsembleAnomalyModel(sample_config)
            
            # Treinar modelo
            for i, data_point in enumerate(sample_data):
                model.add_training_data(data_point, is_anomaly=(i >= 80))
            model.train()
            
            # Fazer predições
            result_normal = model.predict(0.0)
            result_anomaly = model.predict(6.0)
            
            assert isinstance(result_normal, ModelResult)
            assert isinstance(result_anomaly, ModelResult)
            assert result_normal.confidence >= 0
            assert result_anomaly.confidence >= 0


class TestAnomalyModelFactory:
    """Testes para AnomalyModelFactory"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.ISOLATION_FOREST,
            name="factory_test",
            threshold=0.5
        )
    
    def test_create_isolation_forest(self, sample_config):
        """Testa criação de IsolationForest"""
        model = AnomalyModelFactory.create_model(ModelType.ISOLATION_FOREST, sample_config)
        
        assert isinstance(model, IsolationForestModel)
        assert model.config == sample_config
    
    def test_create_one_class_svm(self, sample_config):
        """Testa criação de OneClassSVM"""
        config = ModelConfig(
            model_type=ModelType.ONE_CLASS_SVM,
            name="svm_test",
            threshold=0.5
        )
        model = AnomalyModelFactory.create_model(ModelType.ONE_CLASS_SVM, config)
        
        assert isinstance(model, OneClassSVMModel)
        assert model.config == config
    
    def test_create_local_outlier_factor(self, sample_config):
        """Testa criação de LocalOutlierFactor"""
        config = ModelConfig(
            model_type=ModelType.LOCAL_OUTLIER_FACTOR,
            name="lof_test",
            threshold=0.5
        )
        model = AnomalyModelFactory.create_model(ModelType.LOCAL_OUTLIER_FACTOR, config)
        
        assert isinstance(model, LocalOutlierFactorModel)
        assert model.config == config
    
    def test_create_ensemble(self, sample_config):
        """Testa criação de Ensemble"""
        config = ModelConfig(
            model_type=ModelType.ENSEMBLE,
            name="ensemble_test",
            threshold=0.5
        )
        model = AnomalyModelFactory.create_model(ModelType.ENSEMBLE, config)
        
        assert isinstance(model, EnsembleAnomalyModel)
        assert model.config == config
    
    def test_create_unknown_model(self, sample_config):
        """Testa criação de modelo desconhecido"""
        with pytest.raises(ValueError, match="Unsupported model type"):
            AnomalyModelFactory.create_model("unknown_type", sample_config)
    
    def test_create_with_default_config(self):
        """Testa criação com configuração padrão"""
        model = AnomalyModelFactory.create_model(ModelType.ISOLATION_FOREST)
        
        assert isinstance(model, IsolationForestModel)
        assert model.config.model_type == ModelType.ISOLATION_FOREST


class TestAnomalyModelsIntegration:
    """Testes de integração para AnomalyModels"""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para integração"""
        np.random.seed(42)
        # Dados normais
        normal_data = np.random.normal(0, 1, 200)
        # Dados anômalos
        anomaly_data = np.random.normal(4, 1, 50)
        return np.concatenate([normal_data, anomaly_data])
    
    def test_full_anomaly_detection_cycle(self, sample_data):
        """Testa ciclo completo de detecção de anomalias"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            # Criar diferentes tipos de modelos
            models = []
            
            # Isolation Forest
            config_if = ModelConfig(
                model_type=ModelType.ISOLATION_FOREST,
                name="if_test",
                parameters={"contamination": 0.2}
            )
            model_if = IsolationForestModel(config_if)
            models.append(model_if)
            
            # One Class SVM
            config_svm = ModelConfig(
                model_type=ModelType.ONE_CLASS_SVM,
                name="svm_test",
                parameters={"nu": 0.1}
            )
            model_svm = OneClassSVMModel(config_svm)
            models.append(model_svm)
            
            # Ensemble
            config_ensemble = ModelConfig(
                model_type=ModelType.ENSEMBLE,
                name="ensemble_test"
            )
            model_ensemble = EnsembleAnomalyModel(config_ensemble)
            models.append(model_ensemble)
            
            # Treinar todos os modelos
            for model in models:
                # Adicionar dados (últimos 50 são anômalos)
                for i, data_point in enumerate(sample_data):
                    model.add_training_data(data_point, is_anomaly=(i >= 200))
                
                success = model.train()
                assert success == True
                assert model.status == ModelStatus.TRAINED
            
            # Fazer predições com todos os modelos
            test_points = [0.0, 5.0, -1.0, 6.0]
            
            for model in models:
                for point in test_points:
                    result = model.predict(point)
                    assert isinstance(result, ModelResult)
                    assert result.confidence >= 0
                    assert result.confidence <= 1
            
            # Avaliar todos os modelos
            for model in models:
                metrics = model.evaluate()
                assert metrics is not None
                assert metrics.total_samples > 0
                assert model.status == ModelStatus.EVALUATED


class TestAnomalyModelsErrorHandling:
    """Testes de tratamento de erro para AnomalyModels"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.ISOLATION_FOREST,
            name="error_test",
            threshold=0.5
        )
    
    def test_training_with_invalid_data(self, sample_config):
        """Testa treinamento com dados inválidos"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = IsolationForestModel(sample_config)
            
            # Adicionar dados inválidos
            for i in range(10):
                model.add_training_data("invalid_data", is_anomaly=False)
            
            success = model.train()
            assert success == False
            assert model.status == ModelStatus.ERROR
    
    def test_missing_dependencies(self, sample_config):
        """Testa dependências ausentes"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', False):
            model = IsolationForestModel(sample_config)
            
            # Adicionar dados
            for i in range(20):
                model.add_training_data(i * 0.1, is_anomaly=(i > 15))
            
            success = model.train()
            assert success == False
            assert model.status == ModelStatus.ERROR
    
    def test_prediction_without_training(self, sample_config):
        """Testa predição sem treinamento"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = IsolationForestModel(sample_config)
            
            with pytest.raises(ValueError, match="Model not trained"):
                model.predict(1.0)
    
    def test_invalid_config_parameters(self, sample_config):
        """Testa parâmetros de configuração inválidos"""
        # Configuração com threshold inválido
        with pytest.raises(ValueError):
            ModelConfig(
                model_type=ModelType.ISOLATION_FOREST,
                name="invalid_test",
                threshold=1.5
            )
        
        # Configuração com parâmetros inválidos
        with pytest.raises(ValueError):
            ModelConfig(
                model_type=ModelType.ISOLATION_FOREST,
                name="invalid_test",
                max_training_samples=5,
                min_training_samples=10
            )


class TestAnomalyModelsPerformance:
    """Testes de performance para AnomalyModels"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            model_type=ModelType.ISOLATION_FOREST,
            name="performance_test",
            threshold=0.5
        )
    
    def test_training_performance(self, sample_config):
        """Testa performance do treinamento"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = IsolationForestModel(sample_config)
            
            # Dados maiores
            for i in range(1000):
                model.add_training_data(i * 0.01, is_anomaly=(i > 900))
            
            start_time = time.time()
            success = model.train()
            end_time = time.time()
            
            assert success == True
            training_time = end_time - start_time
            assert training_time < 10.0  # Deve ser razoavelmente rápido
    
    def test_prediction_performance(self, sample_config):
        """Testa performance da predição"""
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            model = IsolationForestModel(sample_config)
            
            # Treinar modelo
            for i in range(100):
                model.add_training_data(i * 0.1, is_anomaly=(i > 80))
            model.train()
            
            # Testar performance de predição
            test_points = np.random.random(1000)
            
            start_time = time.time()
            for point in test_points:
                result = model.predict(point)
                assert isinstance(result, ModelResult)
            end_time = time.time()
            
            prediction_time = end_time - start_time
            assert prediction_time < 5.0  # Deve ser rápido
    
    def test_memory_usage(self, sample_config):
        """Testa uso de memória"""
        import gc
        import sys
        
        with patch('infrastructure.observability.anomaly_models.SKLEARN_AVAILABLE', True):
            # Forçar garbage collection
            gc.collect()
            
            # Criar múltiplos modelos
            models = []
            for i in range(5):
                config = ModelConfig(
                    model_type=ModelType.ISOLATION_FOREST,
                    name=f"model_{i}",
                    threshold=0.5
                )
                model = IsolationForestModel(config)
                
                # Treinar modelo
                for j in range(100):
                    model.add_training_data(j * 0.1, is_anomaly=(j > 80))
                model.train()
                
                models.append(model)
            
            # Verificar que não há vazamento significativo
            gc.collect()
            
            # Limpar modelos
            models.clear()
            gc.collect() 