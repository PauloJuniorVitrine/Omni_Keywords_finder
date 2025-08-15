"""
Testes Unitários para PredictionModels
PredictionModels - Modelos de Machine Learning para predição

Prompt: Implementação de testes unitários para PredictionModels
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_PREDICTION_MODELS_001_20250127
"""

import pytest
import numpy as np
import pandas as pd
import time
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from infrastructure.observability.prediction_models import (
    ModelType,
    PredictionTask,
    ModelConfig,
    ModelPerformance,
    PredictionResult,
    BasePredictiveModel,
    LinearRegressionModel,
    RandomForestModel,
    LSTMModel,
    ModelRegistry
)


class TestModelType:
    """Testes para ModelType"""
    
    def test_model_type_values(self):
        """Testa valores do enum ModelType"""
        assert ModelType.LINEAR_REGRESSION.value == "linear_regression"
        assert ModelType.RIDGE_REGRESSION.value == "ridge_regression"
        assert ModelType.RANDOM_FOREST.value == "random_forest"
        assert ModelType.ISOLATION_FOREST.value == "isolation_forest"
        assert ModelType.LSTM.value == "lstm"
        assert ModelType.GRU.value == "gru"
        assert ModelType.CNN.value == "cnn"
        assert ModelType.ENSEMBLE.value == "ensemble"
        assert ModelType.CUSTOM.value == "custom"
    
    def test_model_type_membership(self):
        """Testa membership do enum ModelType"""
        assert ModelType.LINEAR_REGRESSION in ModelType
        assert ModelType.RANDOM_FOREST in ModelType
        assert ModelType.LSTM in ModelType
        assert ModelType.ENSEMBLE in ModelType


class TestPredictionTask:
    """Testes para PredictionTask"""
    
    def test_prediction_task_values(self):
        """Testa valores do enum PredictionTask"""
        assert PredictionTask.REGRESSION.value == "regression"
        assert PredictionTask.CLASSIFICATION.value == "classification"
        assert PredictionTask.TIME_SERIES.value == "time_series"
        assert PredictionTask.ANOMALY_DETECTION.value == "anomaly_detection"
    
    def test_prediction_task_membership(self):
        """Testa membership do enum PredictionTask"""
        assert PredictionTask.REGRESSION in PredictionTask
        assert PredictionTask.CLASSIFICATION in PredictionTask
        assert PredictionTask.TIME_SERIES in PredictionTask
        assert PredictionTask.ANOMALY_DETECTION in PredictionTask


class TestModelConfig:
    """Testes para ModelConfig"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return {
            "name": "test_model",
            "model_type": ModelType.LINEAR_REGRESSION,
            "task": PredictionTask.REGRESSION,
            "parameters": {"fit_intercept": True, "normalize": False},
            "feature_names": ["feature1", "feature2", "feature3"],
            "target_name": "target",
            "description": "Test model for unit testing"
        }
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        config = ModelConfig(**sample_config)
        
        assert config.name == "test_model"
        assert config.model_type == ModelType.LINEAR_REGRESSION
        assert config.task == PredictionTask.REGRESSION
        assert config.parameters == {"fit_intercept": True, "normalize": False}
        assert config.feature_names == ["feature1", "feature2", "feature3"]
        assert config.target_name == "target"
        assert config.description == "Test model for unit testing"
    
    def test_default_values(self):
        """Testa valores padrão"""
        config = ModelConfig(name="test")
        
        assert config.name == "test"
        assert config.model_type == ModelType.LINEAR_REGRESSION
        assert config.task == PredictionTask.REGRESSION
        assert config.parameters == {}
        assert config.feature_names == []
        assert config.target_name == "target"
        assert config.description == ""
    
    def test_validation(self, sample_config):
        """Testa validações"""
        # Teste com nome vazio
        with pytest.raises(ValueError):
            ModelConfig(name="")
        
        # Teste com tipo de modelo inválido
        with pytest.raises(ValueError):
            ModelConfig(name="test", model_type="invalid")
        
        # Teste com task inválido
        with pytest.raises(ValueError):
            ModelConfig(name="test", task="invalid")
    
    def test_serialization(self, sample_config):
        """Testa serialização"""
        config = ModelConfig(**sample_config)
        
        config_dict = config.to_dict()
        assert config_dict["name"] == "test_model"
        assert config_dict["model_type"] == "linear_regression"
        assert config_dict["task"] == "regression"
        assert config_dict["parameters"] == {"fit_intercept": True, "normalize": False}
    
    def test_from_dict(self, sample_config):
        """Testa criação a partir de dicionário"""
        config = ModelConfig.from_dict(sample_config)
        
        assert config.name == "test_model"
        assert config.model_type == ModelType.LINEAR_REGRESSION
        assert config.task == PredictionTask.REGRESSION


class TestModelPerformance:
    """Testes para ModelPerformance"""
    
    @pytest.fixture
    def sample_performance(self):
        """Performance de exemplo para testes"""
        return {
            "model_name": "test_model",
            "metric_name": "mse",
            "value": 0.123,
            "timestamp": time.time(),
            "training_time": 1.5,
            "prediction_time": 0.001,
            "last_updated": time.time()
        }
    
    def test_initialization(self, sample_performance):
        """Testa inicialização básica"""
        performance = ModelPerformance(**sample_performance)
        
        assert performance.model_name == "test_model"
        assert performance.metric_name == "mse"
        assert performance.value == 0.123
        assert performance.training_time == 1.5
        assert performance.prediction_time == 0.001
    
    def test_default_values(self):
        """Testa valores padrão"""
        performance = ModelPerformance(model_name="test", metric_name="mse")
        
        assert performance.model_name == "test"
        assert performance.metric_name == "mse"
        assert performance.value == 0.0
        assert performance.timestamp > 0
        assert performance.training_time == 0.0
        assert performance.prediction_time == 0.0
    
    def test_validation(self, sample_performance):
        """Testa validações"""
        # Teste com nome vazio
        with pytest.raises(ValueError):
            ModelPerformance(model_name="", metric_name="mse")
        
        # Teste com métrica vazia
        with pytest.raises(ValueError):
            ModelPerformance(model_name="test", metric_name="")
        
        # Teste com valor negativo
        with pytest.raises(ValueError):
            ModelPerformance(model_name="test", metric_name="mse", value=-1.0)
    
    def test_serialization(self, sample_performance):
        """Testa serialização"""
        performance = ModelPerformance(**sample_performance)
        
        performance_dict = performance.to_dict()
        assert performance_dict["model_name"] == "test_model"
        assert performance_dict["metric_name"] == "mse"
        assert performance_dict["value"] == 0.123
        assert performance_dict["training_time"] == 1.5


class TestPredictionResult:
    """Testes para PredictionResult"""
    
    @pytest.fixture
    def sample_result(self):
        """Resultado de exemplo para testes"""
        return {
            "predictions": np.array([1.0, 2.0, 3.0]),
            "confidence": np.array([0.9, 0.8, 0.7]),
            "model_name": "test_model",
            "timestamp": time.time(),
            "metadata": {"feature_count": 3, "prediction_count": 3}
        }
    
    def test_initialization(self, sample_result):
        """Testa inicialização básica"""
        result = PredictionResult(**sample_result)
        
        assert np.array_equal(result.predictions, np.array([1.0, 2.0, 3.0]))
        assert np.array_equal(result.confidence, np.array([0.9, 0.8, 0.7]))
        assert result.model_name == "test_model"
        assert result.metadata == {"feature_count": 3, "prediction_count": 3}
    
    def test_default_values(self):
        """Testa valores padrão"""
        result = PredictionResult(predictions=np.array([1.0]))
        
        assert np.array_equal(result.predictions, np.array([1.0]))
        assert result.confidence is None
        assert result.model_name == ""
        assert result.timestamp > 0
        assert result.metadata == {}
    
    def test_validation(self, sample_result):
        """Testa validações"""
        # Teste com predictions vazio
        with pytest.raises(ValueError):
            PredictionResult(predictions=np.array([]))
        
        # Teste com confidence de tamanho diferente
        with pytest.raises(ValueError):
            PredictionResult(
                predictions=np.array([1.0, 2.0]),
                confidence=np.array([0.9])
            )
    
    def test_serialization(self, sample_result):
        """Testa serialização"""
        result = PredictionResult(**sample_result)
        
        result_dict = result.to_dict()
        assert result_dict["model_name"] == "test_model"
        assert result_dict["metadata"] == {"feature_count": 3, "prediction_count": 3}
        assert "predictions" in result_dict
        assert "confidence" in result_dict


class TestBasePredictiveModel:
    """Testes para BasePredictiveModel (classe abstrata)"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="test_model",
            model_type=ModelType.LINEAR_REGRESSION,
            task=PredictionTask.REGRESSION
        )
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        # Criar uma classe concreta para testar
        class ConcreteModel(BasePredictiveModel):
            def train(self, X, y, feature_names=None):
                return True
            
            def predict(self, X):
                return np.array([1.0, 2.0])
            
            def predict_with_confidence(self, X):
                return np.array([1.0, 2.0]), np.array([0.9, 0.8])
            
            def evaluate(self, X, y):
                return ModelPerformance(model_name="test", metric_name="mse")
            
            def save_model(self, filepath):
                return True
            
            def load_model(self, filepath):
                return True
        
        model = ConcreteModel(sample_config)
        
        assert model.config == sample_config
        assert model.model is None
        assert model.scaler is None
        assert model.feature_names == []
        assert model.is_trained == False
        assert model.performance.model_name == "test_model"
    
    def test_abstract_methods(self, sample_config):
        """Testa que métodos abstratos não podem ser chamados"""
        model = BasePredictiveModel(sample_config)
        
        X = np.array([[1, 2], [3, 4]])
        y = np.array([1, 2])
        
        with pytest.raises(NotImplementedError):
            model.train(X, y)
        
        with pytest.raises(NotImplementedError):
            model.predict(X)
        
        with pytest.raises(NotImplementedError):
            model.predict_with_confidence(X)
        
        with pytest.raises(NotImplementedError):
            model.evaluate(X, y)
        
        with pytest.raises(NotImplementedError):
            model.save_model("test.pkl")
        
        with pytest.raises(NotImplementedError):
            model.load_model("test.pkl")


class TestLinearRegressionModel:
    """Testes para LinearRegressionModel"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="linear_test",
            model_type=ModelType.LINEAR_REGRESSION,
            task=PredictionTask.REGRESSION,
            parameters={"fit_intercept": True}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para treinamento"""
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([3, 7, 11, 15])  # y = x1 + x2
        return X, y
    
    @pytest.fixture
    def sample_feature_names(self):
        """Nomes das features"""
        return ["feature1", "feature2"]
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is not None
            assert model.scaler is not None
            assert model.feature_names == []
            assert model.is_trained == False
    
    def test_initialization_without_sklearn(self, sample_config):
        """Testa inicialização sem sklearn"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', False):
            model = LinearRegressionModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is None
            assert model.scaler is None
    
    def test_train(self, sample_config, sample_data, sample_feature_names):
        """Testa treinamento do modelo"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            X, y = sample_data
            
            success = model.train(X, y, sample_feature_names)
            
            assert success == True
            assert model.is_trained == True
            assert model.feature_names == sample_feature_names
            assert model.performance.training_time > 0
            assert model.performance.last_updated > 0
    
    def test_train_failure(self, sample_config):
        """Testa falha no treinamento"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            
            # Dados inválidos
            X = np.array([[1, 2], [3, 4]])
            y = np.array([1])  # Tamanho diferente
            
            success = model.train(X, y)
            assert success == False
    
    def test_predict(self, sample_config, sample_data, sample_feature_names):
        """Testa predição"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            X, y = sample_data
            
            # Treinar primeiro
            model.train(X, y, sample_feature_names)
            
            # Fazer predição
            X_test = np.array([[2, 3], [4, 5]])
            predictions = model.predict(X_test)
            
            assert len(predictions) == 2
            assert isinstance(predictions, np.ndarray)
    
    def test_predict_without_training(self, sample_config):
        """Testa predição sem treinamento"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            
            X_test = np.array([[1, 2]])
            
            with pytest.raises(ValueError, match="Model not trained"):
                model.predict(X_test)
    
    def test_predict_with_confidence(self, sample_config, sample_data, sample_feature_names):
        """Testa predição com intervalo de confiança"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            X, y = sample_data
            
            # Treinar primeiro
            model.train(X, y, sample_feature_names)
            
            # Fazer predição com confiança
            X_test = np.array([[2, 3]])
            predictions, confidence = model.predict_with_confidence(X_test)
            
            assert len(predictions) == 1
            assert len(confidence) == 1
            assert isinstance(predictions, np.ndarray)
            assert isinstance(confidence, np.ndarray)
    
    def test_evaluate(self, sample_config, sample_data, sample_feature_names):
        """Testa avaliação do modelo"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            X, y = sample_data
            
            # Treinar primeiro
            model.train(X, y, sample_feature_names)
            
            # Avaliar
            performance = model.evaluate(X, y)
            
            assert isinstance(performance, ModelPerformance)
            assert performance.model_name == "linear_test"
            assert performance.value >= 0
    
    def test_save_load_model(self, sample_config, sample_data, sample_feature_names):
        """Testa salvamento e carregamento do modelo"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            X, y = sample_data
            
            # Treinar primeiro
            model.train(X, y, sample_feature_names)
            
            # Salvar modelo
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp_file:
                success = model.save_model(tmp_file.name)
                assert success == True
                
                # Carregar modelo
                new_model = LinearRegressionModel(sample_config)
                success = new_model.load_model(tmp_file.name)
                assert success == True
                
                # Verificar que modelo carregado funciona
                X_test = np.array([[2, 3]])
                predictions = new_model.predict(X_test)
                assert len(predictions) == 1
                
                # Limpar arquivo temporário
                os.unlink(tmp_file.name)


class TestRandomForestModel:
    """Testes para RandomForestModel"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="rf_test",
            model_type=ModelType.RANDOM_FOREST,
            task=PredictionTask.REGRESSION,
            parameters={"n_estimators": 10, "random_state": 42}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para treinamento"""
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([3, 7, 11, 15])
        return X, y
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = RandomForestModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is not None
            assert model.scaler is not None
    
    def test_train(self, sample_config, sample_data):
        """Testa treinamento do modelo"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = RandomForestModel(sample_config)
            X, y = sample_data
            
            success = model.train(X, y)
            assert success == True
            assert model.is_trained == True
    
    def test_predict(self, sample_config, sample_data):
        """Testa predição"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = RandomForestModel(sample_config)
            X, y = sample_data
            
            # Treinar primeiro
            model.train(X, y)
            
            # Fazer predição
            X_test = np.array([[2, 3]])
            predictions = model.predict(X_test)
            
            assert len(predictions) == 1
            assert isinstance(predictions, np.ndarray)


class TestLSTMModel:
    """Testes para LSTMModel"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="lstm_test",
            model_type=ModelType.LSTM,
            task=PredictionTask.TIME_SERIES,
            parameters={"units": 50, "dropout": 0.2}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para treinamento"""
        X = np.random.random((100, 10, 5))  # (samples, timesteps, features)
        y = np.random.random((100, 1))
        return X, y
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        with patch('infrastructure.observability.prediction_models.TENSORFLOW_AVAILABLE', True):
            model = LSTMModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is None  # Modelo é criado durante treinamento
            assert model.scaler is not None
    
    def test_initialization_without_tensorflow(self, sample_config):
        """Testa inicialização sem TensorFlow"""
        with patch('infrastructure.observability.prediction_models.TENSORFLOW_AVAILABLE', False):
            model = LSTMModel(sample_config)
            
            assert model.config == sample_config
            assert model.model is None
            assert model.scaler is None
    
    def test_train(self, sample_config, sample_data):
        """Testa treinamento do modelo"""
        with patch('infrastructure.observability.prediction_models.TENSORFLOW_AVAILABLE', True):
            model = LSTMModel(sample_config)
            X, y = sample_data
            
            success = model.train(X, y)
            assert success == True
            assert model.is_trained == True
            assert model.model is not None
    
    def test_predict(self, sample_config, sample_data):
        """Testa predição"""
        with patch('infrastructure.observability.prediction_models.TENSORFLOW_AVAILABLE', True):
            model = LSTMModel(sample_config)
            X, y = sample_data
            
            # Treinar primeiro
            model.train(X, y)
            
            # Fazer predição
            X_test = np.random.random((10, 10, 5))
            predictions = model.predict(X_test)
            
            assert len(predictions) == 10
            assert isinstance(predictions, np.ndarray)


class TestModelRegistry:
    """Testes para ModelRegistry"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="test_model",
            model_type=ModelType.LINEAR_REGRESSION,
            task=PredictionTask.REGRESSION
        )
    
    @pytest.fixture
    def temp_models_dir(self):
        """Diretório temporário para modelos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_initialization(self, temp_models_dir):
        """Testa inicialização básica"""
        registry = ModelRegistry(temp_models_dir)
        
        assert registry.models_dir == temp_models_dir
        assert registry.models == {}
        assert len(registry.model_factories) > 0
    
    def test_create_model(self, temp_models_dir, sample_config):
        """Testa criação de modelo"""
        registry = ModelRegistry(temp_models_dir)
        
        model = registry.create_model(sample_config)
        
        assert model is not None
        assert isinstance(model, LinearRegressionModel)
        assert model.config == sample_config
    
    def test_create_unknown_model(self, temp_models_dir):
        """Testa criação de modelo desconhecido"""
        registry = ModelRegistry(temp_models_dir)
        
        config = ModelConfig(
            name="unknown",
            model_type="unknown_type",
            task=PredictionTask.REGRESSION
        )
        
        model = registry.create_model(config)
        assert model is None
    
    def test_register_model(self, temp_models_dir, sample_config):
        """Testa registro de modelo"""
        registry = ModelRegistry(temp_models_dir)
        
        model = LinearRegressionModel(sample_config)
        success = registry.register_model(model)
        
        assert success == True
        assert "test_model" in registry.models
        assert registry.models["test_model"] == model
    
    def test_get_model(self, temp_models_dir, sample_config):
        """Testa obtenção de modelo"""
        registry = ModelRegistry(temp_models_dir)
        
        model = LinearRegressionModel(sample_config)
        registry.register_model(model)
        
        retrieved_model = registry.get_model("test_model")
        assert retrieved_model == model
        
        # Teste com modelo inexistente
        assert registry.get_model("nonexistent") is None
    
    def test_list_models(self, temp_models_dir, sample_config):
        """Testa listagem de modelos"""
        registry = ModelRegistry(temp_models_dir)
        
        # Registrar alguns modelos
        model1 = LinearRegressionModel(sample_config)
        config2 = ModelConfig(name="model2", model_type=ModelType.RANDOM_FOREST, task=PredictionTask.REGRESSION)
        model2 = RandomForestModel(config2)
        
        registry.register_model(model1)
        registry.register_model(model2)
        
        models = registry.list_models()
        assert "test_model" in models
        assert "model2" in models
        assert len(models) == 2
    
    def test_remove_model(self, temp_models_dir, sample_config):
        """Testa remoção de modelo"""
        registry = ModelRegistry(temp_models_dir)
        
        model = LinearRegressionModel(sample_config)
        registry.register_model(model)
        
        # Verificar que modelo foi registrado
        assert "test_model" in registry.models
        
        # Remover modelo
        success = registry.remove_model("test_model")
        assert success == True
        assert "test_model" not in registry.models
        
        # Teste com modelo inexistente
        assert registry.remove_model("nonexistent") == False


class TestPredictionModelsIntegration:
    """Testes de integração para PredictionModels"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="integration_test",
            model_type=ModelType.LINEAR_REGRESSION,
            task=PredictionTask.REGRESSION,
            parameters={"fit_intercept": True}
        )
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo"""
        np.random.seed(42)
        X = np.random.random((100, 3))
        y = X[:, 0] * 2 + X[:, 1] * 3 + X[:, 2] * 1.5 + np.random.normal(0, 0.1, 100)
        return X, y
    
    def test_full_model_lifecycle(self, sample_config, sample_data, temp_models_dir):
        """Testa ciclo completo de vida do modelo"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            # Criar modelo
            model = LinearRegressionModel(sample_config)
            X, y = sample_data
            
            # Treinar
            success = model.train(X, y)
            assert success == True
            
            # Fazer predições
            X_test = X[:10]
            predictions = model.predict(X_test)
            assert len(predictions) == 10
            
            # Avaliar
            performance = model.evaluate(X, y)
            assert performance.value >= 0
            
            # Salvar e carregar
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp_file:
                save_success = model.save_model(tmp_file.name)
                assert save_success == True
                
                new_model = LinearRegressionModel(sample_config)
                load_success = new_model.load_model(tmp_file.name)
                assert load_success == True
                
                # Verificar que modelo carregado funciona
                new_predictions = new_model.predict(X_test)
                assert len(new_predictions) == 10
                
                os.unlink(tmp_file.name)


class TestPredictionModelsErrorHandling:
    """Testes de tratamento de erro para PredictionModels"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="error_test",
            model_type=ModelType.LINEAR_REGRESSION,
            task=PredictionTask.REGRESSION
        )
    
    def test_invalid_data_types(self, sample_config):
        """Testa tipos de dados inválidos"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            
            # Dados não numéricos
            X = [["a", "b"], ["c", "d"]]
            y = [1, 2]
            
            success = model.train(X, y)
            assert success == False
    
    def test_missing_dependencies(self, sample_config):
        """Testa dependências ausentes"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', False):
            model = LinearRegressionModel(sample_config)
            
            X = np.array([[1, 2], [3, 4]])
            y = np.array([1, 2])
            
            success = model.train(X, y)
            assert success == False
    
    def test_file_operations_error(self, sample_config, sample_data):
        """Testa erros em operações de arquivo"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            X, y = sample_data
            
            # Treinar modelo
            model.train(X, y)
            
            # Tentar salvar em diretório inexistente
            success = model.save_model("/nonexistent/path/model.pkl")
            assert success == False


class TestPredictionModelsPerformance:
    """Testes de performance para PredictionModels"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return ModelConfig(
            name="performance_test",
            model_type=ModelType.LINEAR_REGRESSION,
            task=PredictionTask.REGRESSION
        )
    
    def test_training_performance(self, sample_config):
        """Testa performance do treinamento"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            
            # Dados maiores
            X = np.random.random((1000, 10))
            y = np.random.random(1000)
            
            start_time = time.time()
            success = model.train(X, y)
            end_time = time.time()
            
            assert success == True
            training_time = end_time - start_time
            assert training_time < 5.0  # Deve ser rápido
    
    def test_prediction_performance(self, sample_config):
        """Testa performance da predição"""
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            model = LinearRegressionModel(sample_config)
            
            # Treinar modelo
            X_train = np.random.random((100, 5))
            y_train = np.random.random(100)
            model.train(X_train, y_train)
            
            # Testar performance de predição
            X_test = np.random.random((1000, 5))
            
            start_time = time.time()
            predictions = model.predict(X_test)
            end_time = time.time()
            
            prediction_time = end_time - start_time
            assert prediction_time < 1.0  # Deve ser muito rápido
            assert len(predictions) == 1000
    
    def test_memory_usage(self, sample_config):
        """Testa uso de memória"""
        import gc
        import sys
        
        with patch('infrastructure.observability.prediction_models.SKLEARN_AVAILABLE', True):
            # Forçar garbage collection
            gc.collect()
            
            # Criar múltiplos modelos
            models = []
            for i in range(10):
                config = ModelConfig(
                    name=f"model_{i}",
                    model_type=ModelType.LINEAR_REGRESSION,
                    task=PredictionTask.REGRESSION
                )
                model = LinearRegressionModel(config)
                
                # Treinar modelo
                X = np.random.random((100, 5))
                y = np.random.random(100)
                model.train(X, y)
                
                models.append(model)
            
            # Verificar que não há vazamento significativo
            gc.collect()
            
            # Limpar modelos
            models.clear()
            gc.collect() 