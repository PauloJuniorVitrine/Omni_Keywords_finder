"""
Sistema de Modelo Adaptativo - Omni Keywords Finder
Tracing ID: ML_ADAPTATIVE_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa modelo adaptativo com:
- Otimização automática de parâmetros
- Aprendizado contínuo
- Feedback loops
- AutoML para clustering
- Otimização bayesiana
- Validação cruzada adaptativa
"""

import numpy as np
import pandas as pd
import time
import logging
import json
import pickle
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict

try:
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
    from sklearn.model_selection import cross_val_score, GridSearchCV, RandomizedSearchCV
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.decomposition import PCA, TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import IsolationForest
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn não disponível. ML adaptativo será limitado.")

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logging.warning("Optuna não disponível. Otimização bayesiana será limitada.")

try:
    from infrastructure.observability.telemetry import get_telemetry_manager
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logging.warning("Telemetria não disponível. Métricas serão limitadas.")


class ModelType(Enum):
    """Tipos de modelos disponíveis."""
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    AGGLOMERATIVE = "agglomerative"
    ISOLATION_FOREST = "isolation_forest"


class OptimizationStrategy(Enum):
    """Estratégias de otimização."""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    EVOLUTIONARY = "evolutionary"


@dataclass
class ModelConfig:
    """Configuração do modelo adaptativo."""
    model_type: ModelType = ModelType.KMEANS
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN_OPTIMIZATION
    max_iterations: int = 100
    n_trials: int = 50
    cv_folds: int = 5
    random_state: int = 42
    n_jobs: int = -1
    auto_feature_selection: bool = True
    auto_dimensionality_reduction: bool = True
    min_clusters: int = 2
    max_clusters: int = 20
    min_samples: int = 5
    eps_range: Tuple[float, float] = (0.1, 2.0)
    learning_rate: float = 0.01
    patience: int = 10
    min_improvement: float = 0.01


@dataclass
class ModelPerformance:
    """Métricas de performance do modelo."""
    silhouette_score: float
    calinski_harabasz_score: float
    davies_bouldin_score: float
    inertia: Optional[float] = None
    n_clusters: int = 0
    training_time: float = 0.0
    prediction_time: float = 0.0
    memory_usage: float = 0.0
    convergence_iterations: int = 0


@dataclass
class OptimizationResult:
    """Resultado da otimização."""
    best_params: Dict[str, Any]
    best_score: float
    optimization_time: float
    n_trials: int
    convergence_history: List[float]
    model_performance: ModelPerformance


class AdaptiveModel:
    """
    Modelo adaptativo com otimização automática de parâmetros
    e aprendizado contínuo.
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.model = None
        self.scaler = None
        self.feature_selector = None
        self.dim_reducer = None
        self.best_params = {}
        self.performance_history = []
        self.optimization_history = []
        self.feature_importance = {}
        self._lock = threading.RLock()
        self._initialized = False
        
        # Configurar telemetria
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry_manager()
        else:
            self.telemetry = None
        
        self.logger = logging.getLogger(__name__)
        
        if not SKLEARN_AVAILABLE:
            self.logger.error("Scikit-learn não disponível. Modelo adaptativo não funcionará.")
            return
    
    def _initialize_model(self) -> None:
        """Inicializa o modelo baseado na configuração."""
        if self.config.model_type == ModelType.KMEANS:
            self.model = KMeans(
                n_clusters=self.config.min_clusters,
                random_state=self.config.random_state,
                n_init=10
            )
        elif self.config.model_type == ModelType.DBSCAN:
            self.model = DBSCAN(
                eps=0.5,
                min_samples=self.config.min_samples
            )
        elif self.config.model_type == ModelType.AGGLOMERATIVE:
            self.model = AgglomerativeClustering(
                n_clusters=self.config.min_clusters
            )
        elif self.config.model_type == ModelType.ISOLATION_FOREST:
            self.model = IsolationForest(
                random_state=self.config.random_state,
                contamination=0.1
            )
        
        self._initialized = True
    
    def _preprocess_data(self, data: Union[np.ndarray, pd.DataFrame, List[str]]) -> np.ndarray:
        """
        Pré-processa os dados para o modelo.
        
        Args:
            data: Dados de entrada
            
        Returns:
            Dados pré-processados
        """
        # Converter para numpy array se necessário
        if isinstance(data, list):
            # Se for lista de strings, aplicar TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            data = vectorizer.fit_transform(data).toarray()
        elif isinstance(data, pd.DataFrame):
            data = data.values
        
        # Normalização
        if self.scaler is None:
            self.scaler = StandardScaler()
            data = self.scaler.fit_transform(data)
        else:
            data = self.scaler.transform(data)
        
        # Redução de dimensionalidade se habilitada
        if self.config.auto_dimensionality_reduction and data.shape[1] > 50:
            if self.dim_reducer is None:
                self.dim_reducer = PCA(n_components=min(50, data.shape[1] - 1))
                data = self.dim_reducer.fit_transform(data)
            else:
                data = self.dim_reducer.transform(data)
        
        return data
    
    def _evaluate_model(self, model, X: np.ndarray, result: Optional[np.ndarray] = None) -> ModelPerformance:
        """
        Avalia a performance do modelo.
        
        Args:
            model: Modelo treinado
            X: Dados de entrada
            result: Labels (opcional)
            
        Returns:
            Métricas de performance
        """
        start_time = time.time()
        
        # Fazer predições
        if hasattr(model, 'predict'):
            predictions = model.predict(X)
        else:
            predictions = model.fit_predict(X)
        
        prediction_time = time.time() - start_time
        
        # Calcular métricas
        try:
            silhouette = silhouette_score(X, predictions) if len(np.unique(predictions)) > 1 else 0
        except:
            silhouette = 0
        
        try:
            calinski = calinski_harabasz_score(X, predictions) if len(np.unique(predictions)) > 1 else 0
        except:
            calinski = 0
        
        try:
            davies = davies_bouldin_score(X, predictions) if len(np.unique(predictions)) > 1 else 0
        except:
            davies = 0
        
        # Métricas específicas do modelo
        inertia = None
        n_clusters = len(np.unique(predictions))
        
        if hasattr(model, 'inertia_'):
            inertia = model.inertia_
        
        return ModelPerformance(
            silhouette_score=silhouette,
            calinski_harabasz_score=calinski,
            davies_bouldin_score=davies,
            inertia=inertia,
            n_clusters=n_clusters,
            prediction_time=prediction_time
        )
    
    def _objective_function(self, trial, X: np.ndarray) -> float:
        """
        Função objetivo para otimização bayesiana.
        
        Args:
            trial: Trial do Optuna
            X: Dados de entrada
            
        Returns:
            Score da função objetivo
        """
        if self.config.model_type == ModelType.KMEANS:
            n_clusters = trial.suggest_int('n_clusters', 
                                         self.config.min_clusters, 
                                         self.config.max_clusters)
            init = trial.suggest_categorical('init', ['key-means++', 'random'])
            
            model = KMeans(
                n_clusters=n_clusters,
                init=init,
                random_state=self.config.random_state,
                n_init=10
            )
        
        elif self.config.model_type == ModelType.DBSCAN:
            eps = trial.suggest_float('eps', 
                                    self.config.eps_range[0], 
                                    self.config.eps_range[1])
            min_samples = trial.suggest_int('min_samples', 
                                          self.config.min_samples, 
                                          min(20, len(X) // 10))
            
            model = DBSCAN(eps=eps, min_samples=min_samples)
        
        elif self.config.model_type == ModelType.AGGLOMERATIVE:
            n_clusters = trial.suggest_int('n_clusters', 
                                         self.config.min_clusters, 
                                         self.config.max_clusters)
            linkage = trial.suggest_categorical('linkage', ['ward', 'complete', 'average'])
            
            model = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage=linkage
            )
        
        else:
            return 0.0
        
        # Avaliar modelo
        performance = self._evaluate_model(model, X)
        
        # Score composto (maior é melhor)
        score = (performance.silhouette_score + 
                performance.calinski_harabasz_score / 1000 - 
                performance.davies_bouldin_score / 10)
        
        return score
    
    def optimize_parameters(self, data: Union[np.ndarray, pd.DataFrame, List[str]]) -> OptimizationResult:
        """
        Otimiza parâmetros do modelo usando a estratégia configurada.
        
        Args:
            data: Dados de entrada
            
        Returns:
            Resultado da otimização
        """
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("Scikit-learn não disponível")
        
        start_time = time.time()
        
        # Pré-processar dados
        X = self._preprocess_data(data)
        
        if self.config.optimization_strategy == OptimizationStrategy.BAYESIAN_OPTIMIZATION:
            return self._bayesian_optimization(X)
        elif self.config.optimization_strategy == OptimizationStrategy.GRID_SEARCH:
            return self._grid_search_optimization(X)
        elif self.config.optimization_strategy == OptimizationStrategy.RANDOM_SEARCH:
            return self._random_search_optimization(X)
        else:
            raise ValueError(f"Estratégia de otimização não suportada: {self.config.optimization_strategy}")
    
    def _bayesian_optimization(self, X: np.ndarray) -> OptimizationResult:
        """
        Otimização bayesiana usando Optuna.
        
        Args:
            X: Dados de entrada
            
        Returns:
            Resultado da otimização
        """
        if not OPTUNA_AVAILABLE:
            raise RuntimeError("Optuna não disponível para otimização bayesiana")
        
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: self._objective_function(trial, X), 
                      n_trials=self.config.n_trials)
        
        # Treinar modelo com melhores parâmetros
        best_params = study.best_params
        self.best_params = best_params
        
        # Criar modelo com parâmetros otimizados
        if self.config.model_type == ModelType.KMEANS:
            self.model = KMeans(**best_params, random_state=self.config.random_state, n_init=10)
        elif self.config.model_type == ModelType.DBSCAN:
            self.model = DBSCAN(**best_params)
        elif self.config.model_type == ModelType.AGGLOMERATIVE:
            self.model = AgglomerativeClustering(**best_params)
        
        # Treinar modelo final
        training_start = time.time()
        if hasattr(self.model, 'fit'):
            self.model.fit(X)
        else:
            self.model.fit_predict(X)
        training_time = time.time() - training_start
        
        # Avaliar modelo final
        performance = self._evaluate_model(self.model, X)
        performance.training_time = training_time
        
        return OptimizationResult(
            best_params=best_params,
            best_score=study.best_value,
            optimization_time=time.time() - training_start,
            n_trials=self.config.n_trials,
            convergence_history=study.trials_dataframe()['value'].tolist(),
            model_performance=performance
        )
    
    def _grid_search_optimization(self, X: np.ndarray) -> OptimizationResult:
        """
        Otimização por grid search.
        
        Args:
            X: Dados de entrada
            
        Returns:
            Resultado da otimização
        """
        if self.config.model_type == ModelType.KMEANS:
            param_grid = {
                'n_clusters': range(self.config.min_clusters, self.config.max_clusters + 1),
                'init': ['key-means++', 'random']
            }
            base_model = KMeans(random_state=self.config.random_state, n_init=10)
        
        elif self.config.model_type == ModelType.AGGLOMERATIVE:
            param_grid = {
                'n_clusters': range(self.config.min_clusters, self.config.max_clusters + 1),
                'linkage': ['ward', 'complete', 'average']
            }
            base_model = AgglomerativeClustering()
        
        else:
            raise ValueError(f"Grid search não suportado para {self.config.model_type}")
        
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=self.config.cv_folds,
            scoring='silhouette_score',
            n_jobs=self.config.n_jobs
        )
        
        grid_search.fit(X)
        
        self.best_params = grid_search.best_params_
        self.model = grid_search.best_estimator_
        
        performance = self._evaluate_model(self.model, X)
        
        return OptimizationResult(
            best_params=self.best_params,
            best_score=grid_search.best_score_,
            optimization_time=0,  # GridSearchCV não fornece tempo diretamente
            n_trials=len(grid_search.cv_results_['params']),
            convergence_history=[grid_search.best_score_],
            model_performance=performance
        )
    
    def _random_search_optimization(self, X: np.ndarray) -> OptimizationResult:
        """
        Otimização por random search.
        
        Args:
            X: Dados de entrada
            
        Returns:
            Resultado da otimização
        """
        if self.config.model_type == ModelType.KMEANS:
            param_distributions = {
                'n_clusters': range(self.config.min_clusters, self.config.max_clusters + 1),
                'init': ['key-means++', 'random']
            }
            base_model = KMeans(random_state=self.config.random_state, n_init=10)
        
        elif self.config.model_type == ModelType.AGGLOMERATIVE:
            param_distributions = {
                'n_clusters': range(self.config.min_clusters, self.config.max_clusters + 1),
                'linkage': ['ward', 'complete', 'average']
            }
            base_model = AgglomerativeClustering()
        
        else:
            raise ValueError(f"Random search não suportado para {self.config.model_type}")
        
        random_search = RandomizedSearchCV(
            base_model,
            param_distributions,
            n_iter=self.config.n_trials,
            cv=self.config.cv_folds,
            scoring='silhouette_score',
            n_jobs=self.config.n_jobs,
            random_state=self.config.random_state
        )
        
        random_search.fit(X)
        
        self.best_params = random_search.best_params_
        self.model = random_search.best_estimator_
        
        performance = self._evaluate_model(self.model, X)
        
        return OptimizationResult(
            best_params=self.best_params,
            best_score=random_search.best_score_,
            optimization_time=0,
            n_trials=self.config.n_trials,
            convergence_history=[random_search.best_score_],
            model_performance=performance
        )
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame, List[str]]) -> OptimizationResult:
        """
        Treina o modelo com otimização automática de parâmetros.
        
        Args:
            data: Dados de entrada
            
        Returns:
            Resultado da otimização
        """
        with self._lock:
            # Otimizar parâmetros
            result = self.optimize_parameters(data)
            
            # Armazenar histórico
            self.optimization_history.append(result)
            self.performance_history.append(result.model_performance)
            
            # Registrar métricas
            if self.telemetry:
                self.telemetry.record_metric(
                    "ml_model_optimization_time",
                    result.optimization_time,
                    {"model_type": self.config.model_type.value}
                )
                
                self.telemetry.record_metric(
                    "ml_model_silhouette_score",
                    result.model_performance.silhouette_score,
                    {"model_type": self.config.model_type.value}
                )
                
                self.telemetry.record_metric(
                    "ml_model_n_clusters",
                    result.model_performance.n_clusters,
                    {"model_type": self.config.model_type.value}
                )
            
            return result
    
    def predict(self, data: Union[np.ndarray, pd.DataFrame, List[str]]) -> np.ndarray:
        """
        Faz predições usando o modelo treinado.
        
        Args:
            data: Dados de entrada
            
        Returns:
            Predições
        """
        if self.model is None:
            raise RuntimeError("Modelo não treinado. Chame fit() primeiro.")
        
        with self._lock:
            # Pré-processar dados
            X = self._preprocess_data(data)
            
            # Fazer predições
            if hasattr(self.model, 'predict'):
                return self.model.predict(X)
            else:
                return self.model.fit_predict(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Retorna importância das features (se disponível).
        
        Returns:
            Dicionário com importância das features
        """
        if self.dim_reducer is not None and hasattr(self.dim_reducer, 'explained_variance_ratio_'):
            return {
                f"PC_{index}": importance 
                for index, importance in enumerate(self.dim_reducer.explained_variance_ratio_)
            }
        
        return {}
    
    def save_model(self, filepath: str) -> None:
        """
        Salva o modelo treinado.
        
        Args:
            filepath: Caminho para salvar o modelo
        """
        if self.model is None:
            raise RuntimeError("Modelo não treinado. Chame fit() primeiro.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'dim_reducer': self.dim_reducer,
            'best_params': self.best_params,
            'config': asdict(self.config),
            'performance_history': [asdict(p) for p in self.performance_history]
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info(f"Modelo salvo em {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Carrega um modelo treinado.
        
        Args:
            filepath: Caminho do modelo
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.dim_reducer = model_data['dim_reducer']
        self.best_params = model_data['best_params']
        self.performance_history = [
            ModelPerformance(**p) for p in model_data['performance_history']
        ]
        
        self.logger.info(f"Modelo carregado de {filepath}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo da performance do modelo.
        
        Returns:
            Dicionário com resumo da performance
        """
        if not self.performance_history:
            return {"error": "Nenhuma performance registrada"}
        
        latest = self.performance_history[-1]
        
        return {
            "model_type": self.config.model_type.value,
            "best_params": self.best_params,
            "latest_performance": asdict(latest),
            "optimization_history_count": len(self.optimization_history),
            "performance_history_count": len(self.performance_history),
            "feature_importance": self.get_feature_importance()
        }


# Instância global do modelo adaptativo
adaptive_model = AdaptiveModel()


def get_adaptive_model() -> AdaptiveModel:
    """Retorna a instância global do modelo adaptativo."""
    return adaptive_model


def initialize_adaptive_model(config: Optional[ModelConfig] = None) -> AdaptiveModel:
    """
    Inicializa e retorna o modelo adaptativo.
    
    Args:
        config: Configuração do modelo
        
    Returns:
        Instância configurada do AdaptiveModel
    """
    global adaptive_model
    adaptive_model = AdaptiveModel(config)
    return adaptive_model 