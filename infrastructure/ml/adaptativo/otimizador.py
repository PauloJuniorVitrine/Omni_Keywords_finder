"""
Sistema de Otimização Automática - Omni Keywords Finder
Tracing ID: ML_ADAPTATIVE_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa otimização automática com:
- Múltiplas estratégias de otimização
- Validação cruzada adaptativa
- Early stopping inteligente
- Hiperparâmetros dinâmicos
- Otimização multi-objetivo
- Análise de sensibilidade
"""

import numpy as np
import pandas as pd
import time
import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict
import warnings

try:
    from sklearn.model_selection import (
        cross_val_score, StratifiedKFold, KFold, 
        train_test_split, validation_curve
    )
    from sklearn.metrics import (
        silhouette_score, calinski_harabasz_score, davies_bouldin_score,
        adjusted_rand_score, normalized_mutual_info_score
    )
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn não disponível. Otimização será limitada.")

try:
    import optuna
    from optuna.samplers import TPESampler, RandomSampler, CmaEsSampler
    from optuna.pruners import MedianPruner, PercentilePruner
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


class OptimizationAlgorithm(Enum):
    """Algoritmos de otimização disponíveis."""
    TPE = "tpe"  # Tree-structured Parzen Estimator
    RANDOM = "random"
    CMA_ES = "cma_es"  # Covariance Matrix Adaptation Evolution Strategy
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"


class ObjectiveFunction(Enum):
    """Funções objetivo disponíveis."""
    SILHOUETTE = "silhouette"
    CALINSKI_HARABASZ = "calinski_harabasz"
    DAVIES_BOULDIN = "davies_bouldin"
    COMPOSITE = "composite"
    CUSTOM = "custom"


@dataclass
class OptimizationConfig:
    """Configuração da otimização."""
    algorithm: OptimizationAlgorithm = OptimizationAlgorithm.TPE
    objective_function: ObjectiveFunction = ObjectiveFunction.COMPOSITE
    n_trials: int = 100
    timeout: int = 3600  # segundos
    n_jobs: int = -1
    cv_folds: int = 5
    random_state: int = 42
    early_stopping: bool = True
    patience: int = 10
    min_improvement: float = 0.01
    multi_objective: bool = False
    study_name: str = "omni_keywords_optimization"
    storage: Optional[str] = None  # Para persistência do Optuna


@dataclass
class OptimizationResult:
    """Resultado da otimização."""
    best_params: Dict[str, Any]
    best_score: float
    optimization_time: float
    n_trials: int
    convergence_history: List[float]
    parameter_importance: Dict[str, float]
    sensitivity_analysis: Dict[str, List[float]]
    study_summary: Dict[str, Any]


class AutoOptimizer:
    """
    Otimizador automático com múltiplas estratégias e validação cruzada.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.study = None
        self.best_trial = None
        self.optimization_history = []
        self.parameter_bounds = {}
        self._lock = threading.RLock()
        
        # Configurar telemetria
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry_manager()
        else:
            self.telemetry = None
        
        self.logger = logging.getLogger(__name__)
        
        if not SKLEARN_AVAILABLE:
            self.logger.error("Scikit-learn não disponível. Otimização não funcionará.")
            return
    
    def set_parameter_bounds(self, bounds: Dict[str, Tuple[Any, Any]]) -> None:
        """
        Define limites para os parâmetros de otimização.
        
        Args:
            bounds: Dicionário com limites dos parâmetros
        """
        self.parameter_bounds = bounds
    
    def _create_objective_function(self, X: np.ndarray, model_class: Any) -> Callable:
        """
        Cria função objetivo baseada na configuração.
        
        Args:
            X: Dados de entrada
            model_class: Classe do modelo
            
        Returns:
            Função objetivo
        """
        def objective(trial):
            # Sugerir parâmetros baseado nos limites
            params = {}
            for param_name, (param_type, *param_args) in self.parameter_bounds.items():
                if param_type == 'int':
                    params[param_name] = trial.suggest_int(param_name, *param_args)
                elif param_type == 'float':
                    params[param_name] = trial.suggest_float(param_name, *param_args)
                elif param_type == 'categorical':
                    params[param_name] = trial.suggest_categorical(param_name, param_args[0])
                elif param_type == 'log':
                    params[param_name] = trial.suggest_loguniform(param_name, *param_args)
            
            # Criar modelo com parâmetros sugeridos
            model = model_class(**params)
            
            # Avaliar modelo
            scores = self._evaluate_model(model, X)
            
            # Retornar score baseado na função objetivo
            if self.config.objective_function == ObjectiveFunction.SILHOUETTE:
                return scores['silhouette']
            elif self.config.objective_function == ObjectiveFunction.CALINSKI_HARABASZ:
                return scores['calinski_harabasz'] / 1000  # Normalizar
            elif self.config.objective_function == ObjectiveFunction.DAVIES_BOULDIN:
                return -scores['davies_bouldin']  # Menor é melhor
            elif self.config.objective_function == ObjectiveFunction.COMPOSITE:
                # Score composto (maior é melhor)
                return (scores['silhouette'] + 
                       scores['calinski_harabasz'] / 1000 - 
                       scores['davies_bouldin'] / 10)
            else:
                return scores['silhouette']  # Padrão
        
        return objective
    
    def _evaluate_model(self, model: Any, X: np.ndarray) -> Dict[str, float]:
        """
        Avalia um modelo usando múltiplas métricas.
        
        Args:
            model: Modelo para avaliar
            X: Dados de entrada
            
        Returns:
            Dicionário com métricas
        """
        try:
            # Fazer predições
            if hasattr(model, 'fit_predict'):
                predictions = model.fit_predict(X)
            elif hasattr(model, 'predict'):
                model.fit(X)
                predictions = model.predict(X)
            else:
                return {'silhouette': 0, 'calinski_harabasz': 0, 'davies_bouldin': 0}
            
            # Calcular métricas
            n_clusters = len(np.unique(predictions))
            
            if n_clusters < 2:
                return {'silhouette': 0, 'calinski_harabasz': 0, 'davies_bouldin': 0}
            
            silhouette = silhouette_score(X, predictions)
            calinski = calinski_harabasz_score(X, predictions)
            davies = davies_bouldin_score(X, predictions)
            
            return {
                'silhouette': silhouette,
                'calinski_harabasz': calinski,
                'davies_bouldin': davies,
                'n_clusters': n_clusters
            }
        
        except Exception as e:
            self.logger.warning(f"Erro na avaliação do modelo: {e}")
            return {'silhouette': 0, 'calinski_harabasz': 0, 'davies_bouldin': 0}
    
    def _create_study(self) -> None:
        """Cria estudo de otimização."""
        if not OPTUNA_AVAILABLE:
            raise RuntimeError("Optuna não disponível")
        
        # Configurar sampler baseado no algoritmo
        if self.config.algorithm == OptimizationAlgorithm.TPE:
            sampler = TPESampler(seed=self.config.random_state)
        elif self.config.algorithm == OptimizationAlgorithm.RANDOM:
            sampler = RandomSampler(seed=self.config.random_state)
        elif self.config.algorithm == OptimizationAlgorithm.CMA_ES:
            sampler = CmaEsSampler(seed=self.config.random_state)
        else:
            sampler = TPESampler(seed=self.config.random_state)
        
        # Configurar pruner para early stopping
        pruner = None
        if self.config.early_stopping:
            pruner = MedianPruner(
                n_startup_trials=5,
                n_warmup_steps=10,
                interval_steps=1
            )
        
        # Criar estudo
        self.study = optuna.create_study(
            direction='maximize',
            sampler=sampler,
            pruner=pruner,
            study_name=self.config.study_name,
            storage=self.config.storage,
            load_if_exists=True
        )
    
    def optimize(self, X: np.ndarray, model_class: Any) -> OptimizationResult:
        """
        Otimiza hiperparâmetros do modelo.
        
        Args:
            X: Dados de entrada
            model_class: Classe do modelo
            
        Returns:
            Resultado da otimização
        """
        if not OPTUNA_AVAILABLE:
            raise RuntimeError("Optuna não disponível para otimização")
        
        start_time = time.time()
        
        # Criar estudo
        self._create_study()
        
        # Criar função objetivo
        objective = self._create_objective_function(X, model_class)
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.config.n_trials,
            timeout=self.config.timeout,
            n_jobs=self.config.n_jobs
        )
        
        optimization_time = time.time() - start_time
        
        # Obter melhores resultados
        self.best_trial = self.study.best_trial
        best_params = self.best_trial.params
        best_score = self.best_trial.value
        
        # Análise de importância dos parâmetros
        parameter_importance = optuna.importance.get_param_importances(self.study)
        
        # Análise de sensibilidade
        sensitivity_analysis = self._analyze_sensitivity(X, model_class)
        
        # Histórico de convergência
        convergence_history = [
            trial.value for trial in self.study.trials 
            if trial.value is not None
        ]
        
        # Resumo do estudo
        study_summary = {
            'n_trials': len(self.study.trials),
            'n_completed_trials': len([t for t in self.study.trials if t.state == optuna.trial.TrialState.COMPLETE]),
            'n_pruned_trials': len([t for t in self.study.trials if t.state == optuna.trial.TrialState.PRUNED]),
            'best_trial_number': self.best_trial.number,
            'optimization_direction': self.study.direction.value
        }
        
        # Criar resultado
        result = OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            optimization_time=optimization_time,
            n_trials=self.config.n_trials,
            convergence_history=convergence_history,
            parameter_importance=parameter_importance,
            sensitivity_analysis=sensitivity_analysis,
            study_summary=study_summary
        )
        
        # Armazenar histórico
        self.optimization_history.append(result)
        
        # Registrar métricas
        if self.telemetry:
            self.telemetry.record_metric(
                "optimization_time_seconds",
                optimization_time,
                {"algorithm": self.config.algorithm.value}
            )
            
            self.telemetry.record_metric(
                "optimization_best_score",
                best_score,
                {"algorithm": self.config.algorithm.value}
            )
            
            self.telemetry.record_metric(
                "optimization_n_trials",
                len(self.study.trials),
                {"algorithm": self.config.algorithm.value}
            )
        
        return result
    
    def _analyze_sensitivity(self, X: np.ndarray, model_class: Any) -> Dict[str, List[float]]:
        """
        Analisa sensibilidade dos parâmetros.
        
        Args:
            X: Dados de entrada
            model_class: Classe do modelo
            
        Returns:
            Análise de sensibilidade
        """
        sensitivity = {}
        
        if not self.best_trial:
            return sensitivity
        
        # Para cada parâmetro, variar seu valor e medir impacto
        for param_name, param_value in self.best_trial.params.items():
            if param_name not in self.parameter_bounds:
                continue
            
            param_type, *param_args = self.parameter_bounds[param_name]
            scores = []
            
            # Testar variações do parâmetro
            if param_type == 'int':
                test_values = np.linspace(param_args[0], param_args[1], 10, dtype=int)
            elif param_type == 'float':
                test_values = np.linspace(param_args[0], param_args[1], 10)
            else:
                continue
            
            for test_value in test_values:
                # Criar modelo com valor testado
                params = self.best_trial.params.copy()
                params[param_name] = test_value
                
                try:
                    model = model_class(**params)
                    score = self._evaluate_model(model, X)['silhouette']
                    scores.append(score)
                except:
                    scores.append(0)
            
            sensitivity[param_name] = scores
        
        return sensitivity
    
    def grid_search_optimization(self, X: np.ndarray, model_class: Any, 
                               param_grid: Dict[str, List[Any]]) -> OptimizationResult:
        """
        Otimização por grid search.
        
        Args:
            X: Dados de entrada
            model_class: Classe do modelo
            param_grid: Grade de parâmetros
            
        Returns:
            Resultado da otimização
        """
        from sklearn.model_selection import GridSearchCV
        
        start_time = time.time()
        
        # Criar modelo base
        base_model = model_class()
        
        # Grid search
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=self.config.cv_folds,
            scoring='silhouette_score',
            n_jobs=self.config.n_jobs
        )
        
        grid_search.fit(X)
        
        optimization_time = time.time() - start_time
        
        # Criar resultado
        result = OptimizationResult(
            best_params=grid_search.best_params_,
            best_score=grid_search.best_score_,
            optimization_time=optimization_time,
            n_trials=len(grid_search.cv_results_['params']),
            convergence_history=[grid_search.best_score_],
            parameter_importance={},
            sensitivity_analysis={},
            study_summary={
                'n_trials': len(grid_search.cv_results_['params']),
                'n_completed_trials': len(grid_search.cv_results_['params']),
                'n_pruned_trials': 0,
                'best_trial_number': grid_search.best_index_,
                'optimization_direction': 'maximize'
            }
        )
        
        return result
    
    def random_search_optimization(self, X: np.ndarray, model_class: Any,
                                 param_distributions: Dict[str, List[Any]]) -> OptimizationResult:
        """
        Otimização por random search.
        
        Args:
            X: Dados de entrada
            model_class: Classe do modelo
            param_distributions: Distribuições de parâmetros
            
        Returns:
            Resultado da otimização
        """
        from sklearn.model_selection import RandomizedSearchCV
        
        start_time = time.time()
        
        # Criar modelo base
        base_model = model_class()
        
        # Random search
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
        
        optimization_time = time.time() - start_time
        
        # Criar resultado
        result = OptimizationResult(
            best_params=random_search.best_params_,
            best_score=random_search.best_score_,
            optimization_time=optimization_time,
            n_trials=self.config.n_trials,
            convergence_history=[random_search.best_score_],
            parameter_importance={},
            sensitivity_analysis={},
            study_summary={
                'n_trials': self.config.n_trials,
                'n_completed_trials': self.config.n_trials,
                'n_pruned_trials': 0,
                'best_trial_number': random_search.best_index_,
                'optimization_direction': 'maximize'
            }
        )
        
        return result
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo das otimizações realizadas.
        
        Returns:
            Dicionário com resumo
        """
        if not self.optimization_history:
            return {"error": "Nenhuma otimização realizada"}
        
        latest = self.optimization_history[-1]
        
        return {
            "total_optimizations": len(self.optimization_history),
            "latest_optimization": {
                "algorithm": self.config.algorithm.value,
                "best_score": latest.best_score,
                "optimization_time": latest.optimization_time,
                "n_trials": latest.n_trials
            },
            "parameter_importance": latest.parameter_importance,
            "study_summary": latest.study_summary
        }
    
    def save_optimization_results(self, filepath: str) -> None:
        """
        Salva resultados da otimização.
        
        Args:
            filepath: Caminho para salvar
        """
        if not self.optimization_history:
            raise RuntimeError("Nenhuma otimização realizada")
        
        data = {
            'config': asdict(self.config),
            'optimization_history': [asdict(result) for result in self.optimization_history],
            'parameter_bounds': self.parameter_bounds
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.logger.info(f"Resultados salvos em {filepath}")
    
    def load_optimization_results(self, filepath: str) -> None:
        """
        Carrega resultados de otimização.
        
        Args:
            filepath: Caminho dos resultados
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.config = OptimizationConfig(**data['config'])
        self.parameter_bounds = data['parameter_bounds']
        
        # Recriar objetos OptimizationResult
        self.optimization_history = []
        for result_data in data['optimization_history']:
            result = OptimizationResult(**result_data)
            self.optimization_history.append(result)
        
        self.logger.info(f"Resultados carregados de {filepath}")


# Instância global do otimizador
auto_optimizer = AutoOptimizer()


def get_auto_optimizer() -> AutoOptimizer:
    """Retorna a instância global do otimizador."""
    return auto_optimizer


def initialize_auto_optimizer(config: Optional[OptimizationConfig] = None) -> AutoOptimizer:
    """
    Inicializa e retorna o otimizador automático.
    
    Args:
        config: Configuração do otimizador
        
    Returns:
        Instância configurada do AutoOptimizer
    """
    global auto_optimizer
    auto_optimizer = AutoOptimizer(config)
    return auto_optimizer 