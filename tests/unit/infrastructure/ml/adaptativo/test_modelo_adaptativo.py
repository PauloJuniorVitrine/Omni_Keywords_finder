from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de ML Adaptativo
Tracing ID: ML_ADAPTATIVE_20241219_001
Data: 2024-12-19
Versão: 1.0

Testes para o sistema de ML adaptativo com:
- Validação de otimização de parâmetros
- Testes de modelos adaptativos
- Testes de performance
- Validação de configurações
- Testes de integração
"""

import pytest
import numpy as np
import pandas as pd
import time
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

# Importar módulos de ML adaptativo
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../'))

from infrastructure.ml.adaptativo.modelo_adaptativo import (
    AdaptiveModel,
    ModelConfig,
    ModelType,
    ModelPerformance,
    OptimizationResult,
    get_adaptive_model,
    initialize_adaptive_model
)

from infrastructure.ml.adaptativo.otimizador import (
    AutoOptimizer,
    OptimizationConfig,
    OptimizationAlgorithm,
    ObjectiveFunction,
    get_auto_optimizer,
    initialize_auto_optimizer
)

from infrastructure.ml.adaptativo.feedback_loop import (
    FeedbackLoop,
    FeedbackLoopConfig,
    FeedbackData,
    FeedbackType,
    DriftDetection,
    DriftType,
    get_feedback_loop,
    initialize_feedback_loop
)


class TestModelConfig:
    """Testes para configuração do modelo."""
    
    def test_model_config_defaults(self):
        """Testa configurações padrão."""
        # Arrange & Act
        config = ModelConfig()
        
        # Assert
        assert config.model_type == ModelType.KMEANS
        assert config.optimization_strategy.value == "bayesian_optimization"
        assert config.max_iterations == 100
        assert config.n_trials == 50
        assert config.cv_folds == 5
        assert config.random_state == 42
        assert config.auto_feature_selection is True
        assert config.auto_dimensionality_reduction is True
        assert config.min_clusters == 2
        assert config.max_clusters == 20
    
    def test_model_config_custom(self):
        """Testa configuração customizada."""
        # Arrange & Act
        config = ModelConfig(
            model_type=ModelType.DBSCAN,
            max_iterations=200,
            n_trials=100,
            min_clusters=3,
            max_clusters=15
        )
        
        # Assert
        assert config.model_type == ModelType.DBSCAN
        assert config.max_iterations == 200
        assert config.n_trials == 100
        assert config.min_clusters == 3
        assert config.max_clusters == 15


class TestAdaptiveModel:
    """Testes para modelo adaptativo."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.config = ModelConfig(
            model_type=ModelType.KMEANS,
            n_trials=10,  # Poucos trials para testes rápidos
            min_clusters=2,
            max_clusters=5
        )
        self.model = AdaptiveModel(self.config)
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_adaptive_model_initialization(self):
        """Testa inicialização do modelo adaptativo."""
        # Arrange & Act
        model = AdaptiveModel()
        
        # Assert
        assert model.config is not None
        assert model.model is None
        assert model.scaler is None
        assert model.best_params == {}
        assert model.performance_history == []
        assert model.optimization_history == []
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_preprocess_data_numpy_array(self):
        """Testa pré-processamento de array numpy."""
        # Arrange
        data = np.random.rand(100, 10)
        
        # Act
        processed_data = self.model._preprocess_data(data)
        
        # Assert
        assert isinstance(processed_data, np.ndarray)
        assert processed_data.shape[0] == 100
        assert self.model.scaler is not None
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_preprocess_data_list_of_strings(self):
        """Testa pré-processamento de lista de strings."""
        # Arrange
        data = ["keyword one", "keyword two", "keyword three"] * 10
        
        # Act
        processed_data = self.model._preprocess_data(data)
        
        # Assert
        assert isinstance(processed_data, np.ndarray)
        assert processed_data.shape[0] == 30
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_preprocess_data_dataframe(self):
        """Testa pré-processamento de DataFrame."""
        # Arrange
        data = pd.DataFrame(np.random.rand(100, 5), columns=['A', 'B', 'C', 'D', 'E'])
        
        # Act
        processed_data = self.model._preprocess_data(data)
        
        # Assert
        assert isinstance(processed_data, np.ndarray)
        assert processed_data.shape[0] == 100
        assert processed_data.shape[1] == 5
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_evaluate_model_kmeans(self):
        """Testa avaliação de modelo KMeans."""
        # Arrange
        from sklearn.cluster import KMeans
        X = np.random.rand(100, 5)
        model = KMeans(n_clusters=3, random_state=42)
        
        # Act
        performance = self.model._evaluate_model(model, X)
        
        # Assert
        assert isinstance(performance, ModelPerformance)
        assert performance.silhouette_score >= -1 and performance.silhouette_score <= 1
        assert performance.calinski_harabasz_score >= 0
        assert performance.davies_bouldin_score >= 0
        assert performance.n_clusters == 3
        assert performance.prediction_time > 0
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.OPTUNA_AVAILABLE', True)
    def test_bayesian_optimization(self):
        """Testa otimização bayesiana."""
        # Arrange
        X = np.random.rand(50, 3)
        
        # Act
        result = self.model._bayesian_optimization(X)
        
        # Assert
        assert isinstance(result, OptimizationResult)
        assert result.best_params is not None
        assert result.best_score is not None
        assert result.optimization_time > 0
        assert result.n_trials == 10
        assert len(result.convergence_history) > 0
        assert isinstance(result.model_performance, ModelPerformance)
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_grid_search_optimization(self):
        """Testa otimização por grid search."""
        # Arrange
        X = np.random.rand(50, 3)
        
        # Act
        result = self.model._grid_search_optimization(X)
        
        # Assert
        assert isinstance(result, OptimizationResult)
        assert result.best_params is not None
        assert result.best_score is not None
        assert result.n_trials > 0
        assert isinstance(result.model_performance, ModelPerformance)
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_random_search_optimization(self):
        """Testa otimização por random search."""
        # Arrange
        X = np.random.rand(50, 3)
        
        # Act
        result = self.model._random_search_optimization(X)
        
        # Assert
        assert isinstance(result, OptimizationResult)
        assert result.best_params is not None
        assert result.best_score is not None
        assert result.n_trials == 10
        assert isinstance(result.model_performance, ModelPerformance)
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.OPTUNA_AVAILABLE', True)
    def test_fit_with_optimization(self):
        """Testa treinamento com otimização."""
        # Arrange
        X = np.random.rand(50, 3)
        
        # Act
        result = self.model.fit(X)
        
        # Assert
        assert isinstance(result, OptimizationResult)
        assert self.model.model is not None
        assert len(self.model.optimization_history) == 1
        assert len(self.model.performance_history) == 1
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.OPTUNA_AVAILABLE', True)
    def test_predict_after_fit(self):
        """Testa predição após treinamento."""
        # Arrange
        X_train = np.random.rand(50, 3)
        X_test = np.random.rand(20, 3)
        
        # Treinar modelo
        self.model.fit(X_train)
        
        # Act
        predictions = self.model.predict(X_test)
        
        # Assert
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 20
        assert all(isinstance(pred, (int, np.integer)) for pred in predictions)
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    def test_get_feature_importance(self):
        """Testa obtenção de importância das features."""
        # Arrange
        X = np.random.rand(50, 10)
        
        # Configurar modelo com redução de dimensionalidade
        self.model.config.auto_dimensionality_reduction = True
        self.model._preprocess_data(X)
        
        # Act
        importance = self.model.get_feature_importance()
        
        # Assert
        assert isinstance(importance, dict)
        # Pode estar vazio se não houver redução de dimensionalidade
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.OPTUNA_AVAILABLE', True)
    def test_get_performance_summary(self):
        """Testa obtenção de resumo de performance."""
        # Arrange
        X = np.random.rand(50, 3)
        self.model.fit(X)
        
        # Act
        summary = self.model.get_performance_summary()
        
        # Assert
        assert isinstance(summary, dict)
        assert 'model_type' in summary
        assert 'best_params' in summary
        assert 'latest_performance' in summary
        assert 'optimization_history_count' in summary
        assert 'performance_history_count' in summary


class TestAutoOptimizer:
    """Testes para otimizador automático."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.config = OptimizationConfig(
            algorithm=OptimizationAlgorithm.TPE,
            n_trials=10,
            timeout=60
        )
        self.optimizer = AutoOptimizer(self.config)
    
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    def test_auto_optimizer_initialization(self):
        """Testa inicialização do otimizador."""
        # Arrange & Act
        optimizer = AutoOptimizer()
        
        # Assert
        assert optimizer.config is not None
        assert optimizer.study is None
        assert optimizer.best_trial is None
        assert optimizer.optimization_history == []
        assert optimizer.parameter_bounds == {}
    
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    def test_set_parameter_bounds(self):
        """Testa definição de limites de parâmetros."""
        # Arrange
        bounds = {
            'n_clusters': ('int', 2, 10),
            'eps': ('float', 0.1, 2.0),
            'init': ('categorical', ['key-means++', 'random'])
        }
        
        # Act
        self.optimizer.set_parameter_bounds(bounds)
        
        # Assert
        assert self.optimizer.parameter_bounds == bounds
    
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    def test_evaluate_model(self):
        """Testa avaliação de modelo."""
        # Arrange
        from sklearn.cluster import KMeans
        X = np.random.rand(50, 3)
        model = KMeans(n_clusters=3, random_state=42)
        
        # Act
        scores = self.optimizer._evaluate_model(model, X)
        
        # Assert
        assert isinstance(scores, dict)
        assert 'silhouette' in scores
        assert 'calinski_harabasz' in scores
        assert 'davies_bouldin' in scores
        assert 'n_clusters' in scores
        assert scores['n_clusters'] == 3
    
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.otimizador.OPTUNA_AVAILABLE', True)
    def test_optimize_with_kmeans(self):
        """Testa otimização com KMeans."""
        # Arrange
        from sklearn.cluster import KMeans
        X = np.random.rand(50, 3)
        
        bounds = {
            'n_clusters': ('int', 2, 5),
            'init': ('categorical', ['key-means++', 'random'])
        }
        self.optimizer.set_parameter_bounds(bounds)
        
        # Act
        result = self.optimizer.optimize(X, KMeans)
        
        # Assert
        assert isinstance(result, OptimizationResult)
        assert result.best_params is not None
        assert result.best_score is not None
        assert result.optimization_time > 0
        assert result.n_trials == 10
        assert len(result.convergence_history) > 0
        assert isinstance(result.parameter_importance, dict)
        assert isinstance(result.sensitivity_analysis, dict)
        assert isinstance(result.study_summary, dict)
    
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    def test_grid_search_optimization(self):
        """Testa otimização por grid search."""
        # Arrange
        from sklearn.cluster import KMeans
        X = np.random.rand(50, 3)
        
        param_grid = {
            'n_clusters': [2, 3, 4],
            'init': ['key-means++', 'random']
        }
        
        # Act
        result = self.optimizer.grid_search_optimization(X, KMeans, param_grid)
        
        # Assert
        assert isinstance(result, OptimizationResult)
        assert result.best_params is not None
        assert result.best_score is not None
        assert result.n_trials > 0
    
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    def test_random_search_optimization(self):
        """Testa otimização por random search."""
        # Arrange
        from sklearn.cluster import KMeans
        X = np.random.rand(50, 3)
        
        param_distributions = {
            'n_clusters': [2, 3, 4, 5],
            'init': ['key-means++', 'random']
        }
        
        # Act
        result = self.optimizer.random_search_optimization(X, KMeans, param_distributions)
        
        # Assert
        assert isinstance(result, OptimizationResult)
        assert result.best_params is not None
        assert result.best_score is not None
        assert result.n_trials == 10
    
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.otimizador.OPTUNA_AVAILABLE', True)
    def test_get_optimization_summary(self):
        """Testa obtenção de resumo da otimização."""
        # Arrange
        from sklearn.cluster import KMeans
        X = np.random.rand(50, 3)
        
        bounds = {
            'n_clusters': ('int', 2, 5),
            'init': ('categorical', ['key-means++', 'random'])
        }
        self.optimizer.set_parameter_bounds(bounds)
        self.optimizer.optimize(X, KMeans)
        
        # Act
        summary = self.optimizer.get_optimization_summary()
        
        # Assert
        assert isinstance(summary, dict)
        assert 'total_optimizations' in summary
        assert 'latest_optimization' in summary
        assert 'parameter_importance' in summary
        assert 'study_summary' in summary


class TestFeedbackLoop:
    """Testes para sistema de feedback loop."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.config = FeedbackLoopConfig(
            feedback_window_size=100,
            feedback_retention_days=7,
            min_feedback_for_analysis=10
        )
        self.feedback_loop = FeedbackLoop(self.config)
    
    def test_feedback_loop_initialization(self):
        """Testa inicialização do feedback loop."""
        # Arrange & Act
        feedback_loop = FeedbackLoop()
        
        # Assert
        assert feedback_loop.config is not None
        assert len(feedback_loop.feedback_buffer) == 0
        assert len(feedback_loop.performance_history) == 0
        assert len(feedback_loop.drift_detections) == 0
        assert feedback_loop.model_versions == {}
        assert feedback_loop.feedback_weights == defaultdict(float)
    
    def test_add_feedback(self):
        """Testa adição de feedback."""
        # Arrange
        feedback = FeedbackData(
            feedback_type=FeedbackType.USER_RATING,
            value=4.5,
            timestamp=time.time(),
            user_id="test_user"
        )
        
        # Act
        self.feedback_loop.add_feedback(feedback)
        
        # Assert
        assert len(self.feedback_loop.feedback_buffer) == 1
        assert self.feedback_loop.feedback_buffer[0] == feedback
    
    def test_add_multiple_feedback(self):
        """Testa adição de múltiplos feedbacks."""
        # Arrange
        feedbacks = [
            FeedbackData(
                feedback_type=FeedbackType.USER_RATING,
                value=4.0 + index * 0.1,
                timestamp=time.time() + index,
                user_id=f"user_{index}"
            )
            for index in range(5)
        ]
        
        # Act
        for feedback in feedbacks:
            self.feedback_loop.add_feedback(feedback)
        
        # Assert
        assert len(self.feedback_loop.feedback_buffer) == 5
    
    def test_feedback_to_dataframe(self):
        """Testa conversão de feedback para DataFrame."""
        # Arrange
        feedbacks = [
            FeedbackData(
                feedback_type=FeedbackType.USER_RATING,
                value=4.0 + index * 0.1,
                timestamp=time.time() + index,
                user_id=f"user_{index}"
            )
            for index in range(3)
        ]
        
        for feedback in feedbacks:
            self.feedback_loop.add_feedback(feedback)
        
        # Act
        df = self.feedback_loop._feedback_to_dataframe()
        
        # Assert
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'feedback_type' in df.columns
        assert 'value' in df.columns
        assert 'user_id' in df.columns
    
    def test_analyze_performance(self):
        """Testa análise de performance."""
        # Arrange
        feedbacks = [
            FeedbackData(
                feedback_type=FeedbackType.USER_RATING,
                value=4.0 + index * 0.1,
                timestamp=time.time() + index,
                user_id=f"user_{index}"
            )
            for index in range(15)  # Suficiente para análise
        ]
        
        for feedback in feedbacks:
            self.feedback_loop.add_feedback(feedback)
        
        df = self.feedback_loop._feedback_to_dataframe()
        
        # Act
        self.feedback_loop._analyze_performance(df)
        
        # Assert
        assert len(self.feedback_loop.performance_history) > 0
    
    def test_calculate_trend(self):
        """Testa cálculo de tendência."""
        # Arrange
        values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        
        # Act
        trend = self.feedback_loop._calculate_trend(values)
        
        # Assert
        assert isinstance(trend, float)
        assert trend > 0  # Tendência crescente
    
    def test_calculate_trend_decreasing(self):
        """Testa cálculo de tendência decrescente."""
        # Arrange
        values = pd.Series([5.0, 4.0, 3.0, 2.0, 1.0])
        
        # Act
        trend = self.feedback_loop._calculate_trend(values)
        
        # Assert
        assert isinstance(trend, float)
        assert trend < 0  # Tendência decrescente
    
    def test_get_feedback_summary_empty(self):
        """Testa resumo de feedback vazio."""
        # Act
        summary = self.feedback_loop.get_feedback_summary()
        
        # Assert
        assert isinstance(summary, dict)
        assert 'error' in summary
        assert summary['error'] == "Nenhum feedback coletado"
    
    def test_get_feedback_summary_with_data(self):
        """Testa resumo de feedback com dados."""
        # Arrange
        feedbacks = [
            FeedbackData(
                feedback_type=FeedbackType.USER_RATING,
                value=4.0 + index * 0.1,
                timestamp=time.time() + index,
                user_id=f"user_{index}"
            )
            for index in range(5)
        ]
        
        for feedback in feedbacks:
            self.feedback_loop.add_feedback(feedback)
        
        # Act
        summary = self.feedback_loop.get_feedback_summary()
        
        # Assert
        assert isinstance(summary, dict)
        assert 'total_feedback' in summary
        assert 'feedback_types' in summary
        assert 'feedback_window' in summary
        assert summary['total_feedback'] == 5
    
    def test_clear_old_feedback(self):
        """Testa limpeza de feedback antigo."""
        # Arrange
        old_time = time.time() - (10 * 24 * 3600)  # 10 dias atrás
        recent_time = time.time() - (2 * 24 * 3600)  # 2 dias atrás
        
        old_feedback = FeedbackData(
            feedback_type=FeedbackType.USER_RATING,
            value=3.0,
            timestamp=old_time,
            user_id="old_user"
        )
        
        recent_feedback = FeedbackData(
            feedback_type=FeedbackType.USER_RATING,
            value=4.0,
            timestamp=recent_time,
            user_id="recent_user"
        )
        
        self.feedback_loop.add_feedback(old_feedback)
        self.feedback_loop.add_feedback(recent_feedback)
        
        # Act
        self.feedback_loop.clear_old_feedback()
        
        # Assert
        assert len(self.feedback_loop.feedback_buffer) == 1  # Apenas o recente


class TestMLAdaptativeIntegration:
    """Testes de integração para ML adaptativo."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.model_config = ModelConfig(
            model_type=ModelType.KMEANS,
            n_trials=5,
            min_clusters=2,
            max_clusters=4
        )
        self.optimization_config = OptimizationConfig(
            algorithm=OptimizationAlgorithm.TPE,
            n_trials=5
        )
        self.feedback_config = FeedbackLoopConfig(
            feedback_window_size=50,
            min_feedback_for_analysis=5
        )
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.OPTUNA_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.otimizador.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.otimizador.OPTUNA_AVAILABLE', True)
    def test_full_ml_workflow(self):
        """Testa workflow completo de ML adaptativo."""
        # Arrange
        X = np.random.rand(100, 5)
        
        # Inicializar componentes
        model = AdaptiveModel(self.model_config)
        optimizer = AutoOptimizer(self.optimization_config)
        feedback_loop = FeedbackLoop(self.feedback_config)
        
        # Act - Treinar modelo
        optimization_result = model.fit(X)
        
        # Act - Otimizar parâmetros
        bounds = {
            'n_clusters': ('int', 2, 5),
            'init': ('categorical', ['key-means++', 'random'])
        }
        optimizer.set_parameter_bounds(bounds)
        optimization_result = optimizer.optimize(X, model.model.__class__)
        
        # Act - Adicionar feedback
        feedbacks = [
            FeedbackData(
                feedback_type=FeedbackType.USER_RATING,
                value=4.0 + index * 0.1,
                timestamp=time.time() + index,
                user_id=f"user_{index}"
            )
            for index in range(10)
        ]
        
        for feedback in feedbacks:
            feedback_loop.add_feedback(feedback)
        
        # Assert
        assert model.model is not None
        assert len(model.optimization_history) == 1
        assert len(optimizer.optimization_history) == 1
        assert len(feedback_loop.feedback_buffer) == 10
        
        # Verificar performance
        model_summary = model.get_performance_summary()
        optimizer_summary = optimizer.get_optimization_summary()
        feedback_summary = feedback_loop.get_feedback_summary()
        
        assert 'model_type' in model_summary
        assert 'total_optimizations' in optimizer_summary
        assert 'total_feedback' in feedback_summary


class TestMLAdaptativePerformance:
    """Testes de performance para ML adaptativo."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.model_config = ModelConfig(
            model_type=ModelType.KMEANS,
            n_trials=10,
            min_clusters=2,
            max_clusters=5
        )
        self.model = AdaptiveModel(self.model_config)
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.OPTUNA_AVAILABLE', True)
    def test_model_training_performance(self):
        """Testa performance do treinamento."""
        # Arrange
        X = np.random.rand(200, 10)
        start_time = time.time()
        
        # Act
        result = self.model.fit(X)
        end_time = time.time()
        
        # Assert
        training_time = end_time - start_time
        assert training_time < 30  # Deve treinar em menos de 30 segundos
        assert result.optimization_time > 0
        assert result.model_performance.training_time > 0
    
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.SKLEARN_AVAILABLE', True)
    @patch('infrastructure.ml.adaptativo.modelo_adaptativo.OPTUNA_AVAILABLE', True)
    def test_prediction_performance(self):
        """Testa performance da predição."""
        # Arrange
        X_train = np.random.rand(200, 10)
        X_test = np.random.rand(50, 10)
        
        self.model.fit(X_train)
        
        # Act
        start_time = time.time()
        predictions = self.model.predict(X_test)
        end_time = time.time()
        
        # Assert
        prediction_time = end_time - start_time
        assert prediction_time < 1  # Deve prever em menos de 1 segundo
        assert len(predictions) == 50


class TestMLAdaptativeSecurity:
    """Testes de segurança para ML adaptativo."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.model = AdaptiveModel()
        self.feedback_loop = FeedbackLoop()
    
    def test_sensitive_data_not_logged(self):
        """Testa que dados sensíveis não são logados."""
        # Arrange
        sensitive_feedback = FeedbackData(
            feedback_type=FeedbackType.USER_RATING,
            value=4.5,
            timestamp=time.time(),
            user_id="user_123",
            metadata={
                "password": "secret123",
                "api_key": "sk-1234567890abcdef",
                "email": "user@example.com"
            }
        )
        
        # Act
        self.feedback_loop.add_feedback(sensitive_feedback)
        
        # Assert
        summary = self.feedback_loop.get_feedback_summary()
        summary_str = str(summary)
        
        # Verificar que dados sensíveis não estão expostos
        assert "password" not in summary_str
        assert "api_key" not in summary_str
        assert "user@example.com" not in summary_str
    
    def test_model_configuration_validation(self):
        """Testa validação de configurações do modelo."""
        # Arrange & Act
        config = ModelConfig()
        
        # Assert
        assert config.n_trials > 0
        assert config.min_clusters > 0
        assert config.max_clusters >= config.min_clusters
        assert config.cv_folds > 1
        assert config.random_state >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 