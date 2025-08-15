"""
Sistema de Pipeline de ML Automatizado
Tracing ID: LONGTAIL-039
Data: 2024-12-20
Descrição: Pipeline automatizado end-to-end para treinamento e deployment de modelos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import pickle
import joblib
from datetime import datetime, timedelta
from pathlib import Path
import os
import shutil
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    """Estágios do pipeline de ML"""
    DATA_COLLECTION = "data_collection"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_SELECTION = "model_selection"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    MODEL_DEPLOYMENT = "model_deployment"
    MONITORING = "monitoring"

class ModelType(Enum):
    """Tipos de modelos suportados"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"

@dataclass
class PipelineConfig:
    """Configuração do pipeline"""
    model_type: ModelType
    target_column: str
    feature_columns: List[str]
    test_size: float = 0.2
    random_state: int = 42
    max_iterations: int = 100
    cv_folds: int = 5
    scoring_metric: str = "accuracy"
    auto_feature_selection: bool = True
    hyperparameter_tuning: bool = True
    model_persistence: bool = True
    monitoring_enabled: bool = True

@dataclass
class PipelineResult:
    """Resultado do pipeline"""
    model: Any
    metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    training_time: float
    model_path: str
    config: PipelineConfig
    timestamp: datetime
    version: str

class DataCollector(ABC):
    """Classe abstrata para coleta de dados"""
    
    @abstractmethod
    def collect(self) -> pd.DataFrame:
        """Coleta dados da fonte"""
        pass
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Valida qualidade dos dados"""
        pass

class KeywordDataCollector(DataCollector):
    """Coletor específico para dados de keywords"""
    
    def __init__(self, data_sources: List[str]):
        self.data_sources = data_sources
        self.required_columns = [
            'keyword', 'search_volume', 'cpc', 'competition',
            'density', 'complexity', 'intent_score'
        ]
    
    def collect(self) -> pd.DataFrame:
        """Coleta dados de keywords de múltiplas fontes"""
        logger.info("Iniciando coleta de dados de keywords...")
        
        all_data = []
        
        for source in self.data_sources:
            try:
                # Simula coleta de dados (em produção, seria API real)
                source_data = self._collect_from_source(source)
                all_data.append(source_data)
                logger.info(f"Dados coletados de {source}: {len(source_data)} registros")
            except Exception as e:
                logger.error(f"Erro ao coletar de {source}: {e}")
        
        if not all_data:
            raise ValueError("Nenhum dado foi coletado com sucesso")
        
        # Combina dados de todas as fontes
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Remove duplicatas
        combined_data = combined_data.drop_duplicates(subset=['keyword'])
        
        logger.info(f"Coleta concluída: {len(combined_data)} registros únicos")
        return combined_data
    
    def _collect_from_source(self, source: str) -> pd.DataFrame:
        """Coleta dados de uma fonte específica"""
        # Simulação de dados de keywords
        np.random.seed(42)
        n_samples = np.random.randint(1000, 5000)
        
        data = {
            'keyword': [f"keyword_{index}" for index in range(n_samples)],
            'search_volume': np.random.randint(100, 10000, n_samples),
            'cpc': np.random.uniform(0.1, 5.0, n_samples),
            'competition': np.random.uniform(0.1, 1.0, n_samples),
            'density': np.random.uniform(0.1, 0.9, n_samples),
            'complexity': np.random.uniform(0.1, 0.9, n_samples),
            'intent_score': np.random.uniform(0.1, 1.0, n_samples),
            'source': source
        }
        
        return pd.DataFrame(data)
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Valida qualidade dos dados coletados"""
        logger.info("Validando qualidade dos dados...")
        
        # Verifica colunas obrigatórias
        missing_columns = set(self.required_columns) - set(data.columns)
        if missing_columns:
            logger.error(f"Colunas obrigatórias ausentes: {missing_columns}")
            return False
        
        # Verifica valores nulos
        null_counts = data[self.required_columns].isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"Valores nulos encontrados: {null_counts.to_dict()}")
        
        # Verifica tipos de dados
        numeric_columns = ['search_volume', 'cpc', 'competition', 'density', 'complexity', 'intent_score']
        for col in numeric_columns:
            if not pd.api.types.is_numeric_dtype(data[col]):
                logger.error(f"Coluna {col} não é numérica")
                return False
        
        # Verifica ranges válidos
        if (data['search_volume'] < 0).any():
            logger.error("Search volume não pode ser negativo")
            return False
        
        if (data['cpc'] < 0).any():
            logger.error("CPC não pode ser negativo")
            return False
        
        if ((data['competition'] < 0) | (data['competition'] > 1)).any():
            logger.error("Competition deve estar entre 0 e 1")
            return False
        
        logger.info("Validação de dados concluída com sucesso")
        return True

class DataPreprocessor:
    """Preprocessador de dados"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.scalers = {}
        self.encoders = {}
    
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocessa dados para treinamento"""
        logger.info("Iniciando preprocessamento de dados...")
        
        # Cria cópia para não modificar original
        processed_data = data.copy()
        
        # Remove outliers
        processed_data = self._remove_outliers(processed_data)
        
        # Normaliza features numéricas
        processed_data = self._normalize_features(processed_data)
        
        # Engenharia de features
        processed_data = self._engineer_features(processed_data)
        
        # Seleção de features
        if self.config.auto_feature_selection:
            processed_data = self._select_features(processed_data)
        
        logger.info(f"Preprocessamento concluído: {processed_data.shape}")
        return processed_data
    
    def _remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers usando IQR"""
        numeric_columns = ['search_volume', 'cpc', 'competition', 'density', 'complexity', 'intent_score']
        
        for col in numeric_columns:
            if col in data.columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Remove outliers
                data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]
        
        return data
    
    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Normaliza features numéricas"""
        from sklearn.preprocessing import StandardScaler
        
        numeric_columns = ['search_volume', 'cpc', 'competition', 'density', 'complexity', 'intent_score']
        
        for col in numeric_columns:
            if col in data.columns:
                scaler = StandardScaler()
                data[col] = scaler.fit_transform(data[col].values.reshape(-1, 1))
                self.scalers[col] = scaler
        
        return data
    
    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Cria features derivadas"""
        # Feature de volume por complexidade
        if 'search_volume' in data.columns and 'complexity' in data.columns:
            data['volume_complexity_ratio'] = data['search_volume'] / (data['complexity'] + 1e-6)
        
        # Feature de competição por CPC
        if 'competition' in data.columns and 'cpc' in data.columns:
            data['competition_cpc_ratio'] = data['competition'] / (data['cpc'] + 1e-6)
        
        # Feature de densidade por intenção
        if 'density' in data.columns and 'intent_score' in data.columns:
            data['density_intent_ratio'] = data['density'] / (data['intent_score'] + 1e-6)
        
        # Feature composta de qualidade
        if all(col in data.columns for col in ['search_volume', 'cpc', 'competition']):
            data['quality_score'] = (
                data['search_volume'] * 0.4 +
                (1 - data['competition']) * 0.4 +
                (1 / (data['cpc'] + 1e-6)) * 0.2
            )
        
        return data
    
    def _select_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Seleciona features mais importantes"""
        from sklearn.feature_selection import SelectKBest, f_regression
        
        # Remove colunas não numéricas
        numeric_data = data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) <= 5:  # Se poucas features, mantém todas
            return data
        
        # Seleciona as 5 melhores features
        selector = SelectKBest(score_func=f_regression, key=5)
        selected_features = selector.fit_transform(numeric_data, numeric_data['quality_score'])
        
        # Obtém nomes das features selecionadas
        selected_indices = selector.get_support(indices=True)
        selected_columns = numeric_data.columns[selected_indices].tolist()
        
        # Adiciona coluna de keyword se existir
        if 'keyword' in data.columns:
            selected_columns.append('keyword')
        
        return data[selected_columns]

class ModelTrainer:
    """Treinador de modelos"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.models = {}
        self.best_model = None
        self.best_score = 0.0
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Treina múltiplos modelos e seleciona o melhor"""
        logger.info("Iniciando treinamento de modelos...")
        
        # Define modelos para testar
        models_to_test = self._get_models_to_test()
        
        results = {}
        
        for name, model in models_to_test.items():
            logger.info(f"Treinando modelo: {name}")
            
            try:
                # Treina modelo
                start_time = datetime.now()
                model.fit(X_train, y_train)
                training_time = (datetime.now() - start_time).total_seconds()
                
                # Avalia modelo
                train_score = model.score(X_train, y_train)
                val_score = model.score(X_val, y_val)
                
                # Predições
                y_pred = model.predict(X_val)
                
                # Métricas adicionais
                metrics = self._calculate_metrics(y_val, y_pred)
                metrics.update({
                    'train_score': train_score,
                    'val_score': val_score,
                    'training_time': training_time
                })
                
                results[name] = {
                    'model': model,
                    'metrics': metrics,
                    'training_time': training_time
                }
                
                # Atualiza melhor modelo
                if val_score > self.best_score:
                    self.best_score = val_score
                    self.best_model = model
                
                logger.info(f"{name}: Val Score = {val_score:.4f}, Time = {training_time:.2f}string_data")
                
            except Exception as e:
                logger.error(f"Erro ao treinar {name}: {e}")
                continue
        
        if not results:
            raise ValueError("Nenhum modelo foi treinado com sucesso")
        
        logger.info(f"Treinamento concluído. Melhor modelo: {self.best_score:.4f}")
        return results
    
    def _get_models_to_test(self) -> Dict[str, Any]:
        """Retorna modelos para testar baseado no tipo de problema"""
        from sklearn.linear_model import LinearRegression, LogisticRegression
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.svm import SVR, SVC
        from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
        from xgboost import XGBRegressor, XGBClassifier
        
        if self.config.model_type == ModelType.REGRESSION:
            return {
                'LinearRegression': LinearRegression(),
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=self.config.random_state),
                'SVR': SVR(),
                'KNN': KNeighborsRegressor(n_neighbors=5),
                'XGBoost': XGBRegressor(n_estimators=100, random_state=self.config.random_state)
            }
        elif self.config.model_type == ModelType.CLASSIFICATION:
            return {
                'LogisticRegression': LogisticRegression(random_state=self.config.random_state),
                'RandomForest': RandomForestClassifier(n_estimators=100, random_state=self.config.random_state),
                'SVC': SVC(random_state=self.config.random_state),
                'KNN': KNeighborsClassifier(n_neighbors=5),
                'XGBoost': XGBClassifier(n_estimators=100, random_state=self.config.random_state)
            }
        else:
            raise ValueError(f"Tipo de modelo não suportado: {self.config.model_type}")
    
    def _calculate_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de avaliação"""
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        if self.config.model_type == ModelType.REGRESSION:
            return {
                'mse': mean_squared_error(y_true, y_pred),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2': r2_score(y_true, y_pred)
            }
        elif self.config.model_type == ModelType.CLASSIFICATION:
            return {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted'),
                'recall': recall_score(y_true, y_pred, average='weighted'),
                'f1': f1_score(y_true, y_pred, average='weighted')
            }
        else:
            return {}

class ModelEvaluator:
    """Avaliador de modelos"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
    
    def evaluate(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """Avalia modelo em dados de teste"""
        logger.info("Avaliando modelo em dados de teste...")
        
        # Predições
        y_pred = model.predict(X_test)
        
        # Métricas
        metrics = self._calculate_test_metrics(y_test, y_pred)
        
        # Feature importance (se disponível)
        feature_importance = self._get_feature_importance(model, X_test.columns)
        
        logger.info(f"Avaliação concluída: {metrics}")
        
        return {
            'metrics': metrics,
            'feature_importance': feature_importance
        }
    
    def _calculate_test_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de teste"""
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        if self.config.model_type == ModelType.REGRESSION:
            return {
                'test_mse': mean_squared_error(y_true, y_pred),
                'test_mae': mean_absolute_error(y_true, y_pred),
                'test_r2': r2_score(y_true, y_pred)
            }
        elif self.config.model_type == ModelType.CLASSIFICATION:
            return {
                'test_accuracy': accuracy_score(y_true, y_pred),
                'test_precision': precision_score(y_true, y_pred, average='weighted'),
                'test_recall': recall_score(y_true, y_pred, average='weighted'),
                'test_f1': f1_score(y_true, y_pred, average='weighted')
            }
        else:
            return {}
    
    def _get_feature_importance(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
        """Extrai importância das features"""
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
            else:
                return {}
            
            # Normaliza importância
            importance = importance / np.sum(importance)
            
            return dict(zip(feature_names, importance))
        except:
            return {}

class ModelDeployer:
    """Deployer de modelos"""
    
    def __init__(self, model_path: str = "models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
    
    def deploy(self, model: Any, config: PipelineConfig, 
               metrics: Dict[str, float], feature_importance: Dict[str, float],
               training_time: float) -> str:
        """Deploya modelo treinado"""
        logger.info("Iniciando deployment do modelo...")
        
        # Gera versão do modelo
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = self.model_path / version
        model_dir.mkdir(exist_ok=True)
        
        # Salva modelo
        model_file = model_dir / "model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        
        # Salva metadados
        metadata = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'config': {
                'model_type': config.model_type.value,
                'target_column': config.target_column,
                'feature_columns': config.feature_columns,
                'test_size': config.test_size,
                'random_state': config.random_state,
                'scoring_metric': config.scoring_metric
            },
            'metrics': metrics,
            'feature_importance': feature_importance,
            'training_time': training_time
        }
        
        metadata_file = model_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Cria link simbólico para versão atual
        current_link = self.model_path / "current"
        if current_link.exists():
            current_link.unlink()
        current_link.symlink_to(version)
        
        logger.info(f"Modelo deployado: {model_file}")
        return str(model_file)

class ModelMonitor:
    """Monitor de modelos em produção"""
    
    def __init__(self, model_path: str = "models"):
        self.model_path = Path(model_path)
        self.metrics_history = []
    
    def monitor_performance(self, model: Any, X_new: pd.DataFrame, y_new: pd.Series) -> Dict[str, Any]:
        """Monitora performance do modelo em novos dados"""
        logger.info("Monitorando performance do modelo...")
        
        # Predições
        y_pred = model.predict(X_new)
        
        # Calcula métricas atuais
        current_metrics = self._calculate_current_metrics(y_new, y_pred)
        
        # Compara com baseline
        drift_analysis = self._analyze_drift(current_metrics)
        
        # Salva histórico
        self.metrics_history.append({
            'timestamp': datetime.now().isoformat(),
            'metrics': current_metrics,
            'drift_analysis': drift_analysis
        })
        
        return {
            'current_metrics': current_metrics,
            'drift_analysis': drift_analysis,
            'alerts': self._generate_alerts(current_metrics, drift_analysis)
        }
    
    def _calculate_current_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas atuais"""
        from sklearn.metrics import mean_squared_error, accuracy_score
        
        if len(y_true) == 0:
            return {}
        
        if isinstance(y_pred[0], (int, float)) and not isinstance(y_pred[0], bool):
            # Regressão
            return {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred))
            }
        else:
            # Classificação
            return {
                'accuracy': accuracy_score(y_true, y_pred)
            }
    
    def _analyze_drift(self, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analisa drift de performance"""
        if len(self.metrics_history) < 2:
            return {'drift_detected': False, 'drift_score': 0.0}
        
        # Compara com métricas anteriores
        baseline_metrics = self.metrics_history[-2]['metrics']
        
        drift_scores = {}
        for metric in current_metrics:
            if metric in baseline_metrics:
                baseline = baseline_metrics[metric]
                current = current_metrics[metric]
                drift = abs(current - baseline) / (baseline + 1e-6)
                drift_scores[metric] = drift
        
        avg_drift = np.mean(list(drift_scores.values())) if drift_scores else 0.0
        
        return {
            'drift_detected': avg_drift > 0.1,  # 10% de drift
            'drift_score': avg_drift,
            'drift_scores': drift_scores
        }
    
    def _generate_alerts(self, current_metrics: Dict[str, float], 
                        drift_analysis: Dict[str, Any]) -> List[str]:
        """Gera alertas baseados na performance"""
        alerts = []
        
        # Alerta de drift
        if drift_analysis.get('drift_detected', False):
            alerts.append(f"DRIFT_DETECTED: Score de drift = {drift_analysis['drift_score']:.3f}")
        
        # Alerta de performance baixa
        for metric, value in current_metrics.items():
            if metric == 'accuracy' and value < 0.7:
                alerts.append(f"LOW_ACCURACY: {value:.3f}")
            elif metric == 'mse' and value > 1.0:
                alerts.append(f"HIGH_MSE: {value:.3f}")
        
        return alerts

class AutomatedMLPipeline:
    """Pipeline automatizado de ML"""
    
    def __init__(self, config: PipelineConfig, data_collector: DataCollector):
        self.config = config
        self.data_collector = data_collector
        self.preprocessor = DataPreprocessor(config)
        self.trainer = ModelTrainer(config)
        self.evaluator = ModelEvaluator(config)
        self.deployer = ModelDeployer()
        self.monitor = ModelMonitor()
        
        self.results = None
    
    def run(self) -> PipelineResult:
        """Executa pipeline completo"""
        logger.info("Iniciando pipeline automatizado de ML...")
        
        start_time = datetime.now()
        
        try:
            # 1. Coleta de dados
            logger.info(f"Estágio: {PipelineStage.DATA_COLLECTION.value}")
            data = self.data_collector.collect()
            
            if not self.data_collector.validate_data(data):
                raise ValueError("Dados não passaram na validação")
            
            # 2. Preprocessamento
            logger.info(f"Estágio: {PipelineStage.DATA_PREPROCESSING.value}")
            processed_data = self.preprocessor.preprocess(data)
            
            # 3. Preparação para treinamento
            logger.info(f"Estágio: {PipelineStage.FEATURE_ENGINEERING.value}")
            X, result = self._prepare_training_data(processed_data)
            
            # Split dos dados
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, result, test_size=self.config.test_size, random_state=self.config.random_state
            )
            
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=self.config.random_state
            )
            
            # 4. Treinamento
            logger.info(f"Estágio: {PipelineStage.MODEL_TRAINING.value}")
            training_results = self.trainer.train(X_train, y_train, X_val, y_val)
            
            # 5. Avaliação
            logger.info(f"Estágio: {PipelineStage.MODEL_EVALUATION.value}")
            best_model = self.trainer.best_model
            evaluation_results = self.evaluator.evaluate(best_model, X_test, y_test)
            
            # 6. Deployment
            logger.info(f"Estágio: {PipelineStage.MODEL_DEPLOYMENT.value}")
            model_path = self.deployer.deploy(
                best_model, self.config, 
                evaluation_results['metrics'],
                evaluation_results['feature_importance'],
                training_results[list(training_results.keys())[0]]['training_time']
            )
            
            # 7. Monitoramento (se habilitado)
            if self.config.monitoring_enabled:
                logger.info(f"Estágio: {PipelineStage.MONITORING.value}")
                monitoring_results = self.monitor.monitor_performance(best_model, X_test, y_test)
                logger.info(f"Monitoramento: {monitoring_results['alerts']}")
            
            # Resultado final
            training_time = (datetime.now() - start_time).total_seconds()
            
            self.results = PipelineResult(
                model=best_model,
                metrics=evaluation_results['metrics'],
                feature_importance=evaluation_results['feature_importance'],
                training_time=training_time,
                model_path=model_path,
                config=self.config,
                timestamp=datetime.now(),
                version=datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            
            logger.info("Pipeline executado com sucesso!")
            return self.results
            
        except Exception as e:
            logger.error(f"Erro no pipeline: {e}")
            raise
    
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepara dados para treinamento"""
        # Remove colunas não numéricas
        feature_data = data.select_dtypes(include=[np.number])
        
        # Remove target se existir
        if self.config.target_column in feature_data.columns:
            result = feature_data[self.config.target_column]
            X = feature_data.drop(columns=[self.config.target_column])
        else:
            # Se não há target, usa qualidade como proxy
            if 'quality_score' in feature_data.columns:
                result = feature_data['quality_score']
                X = feature_data.drop(columns=['quality_score'])
            else:
                raise ValueError("Nenhuma coluna target encontrada")
        
        # Remove colunas com muitos valores únicos (como IDs)
        for col in X.columns:
            if X[col].nunique() > len(X) * 0.9:
                X = X.drop(columns=[col])
        
        return X, result
    
    def get_results(self) -> Optional[PipelineResult]:
        """Retorna resultados do pipeline"""
        return self.results
    
    def save_pipeline_state(self, filepath: str):
        """Salva estado do pipeline"""
        state = {
            'config': {
                'model_type': self.config.model_type.value,
                'target_column': self.config.target_column,
                'feature_columns': self.config.feature_columns,
                'test_size': self.config.test_size,
                'random_state': self.config.random_state,
                'scoring_metric': self.config.scoring_metric
            },
            'results': {
                'metrics': self.results.metrics if self.results else {},
                'feature_importance': self.results.feature_importance if self.results else {},
                'training_time': self.results.training_time if self.results else 0,
                'model_path': self.results.model_path if self.results else "",
                'version': self.results.version if self.results else ""
            },
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

# Função de conveniência para uso rápido
def run_automated_ml_pipeline(data_sources: List[str], 
                             target_column: str = "quality_score",
                             model_type: ModelType = ModelType.REGRESSION) -> PipelineResult:
    """
    Função de conveniência para executar pipeline automatizado
    
    Args:
        data_sources: Lista de fontes de dados
        target_column: Coluna target
        model_type: Tipo de modelo
    
    Returns:
        Resultado do pipeline
    """
    # Configuração padrão
    config = PipelineConfig(
        model_type=model_type,
        target_column=target_column,
        feature_columns=[],  # Será preenchido automaticamente
        test_size=0.2,
        random_state=42,
        scoring_metric="r2" if model_type == ModelType.REGRESSION else "accuracy"
    )
    
    # Coletor de dados
    data_collector = KeywordDataCollector(data_sources)
    
    # Pipeline
    pipeline = AutomatedMLPipeline(config, data_collector)
    
    # Executa pipeline
    return pipeline.run()

if __name__ == "__main__":
    # Exemplo de uso
    data_sources = ["google_keywords", "amazon_keywords", "bing_keywords"]
    
    try:
        result = run_automated_ml_pipeline(
            data_sources=data_sources,
            target_column="quality_score",
            model_type=ModelType.REGRESSION
        )
        
        print("Pipeline executado com sucesso!")
        print(f"Modelo salvo em: {result.model_path}")
        print(f"Métricas: {result.metrics}")
        print(f"Tempo de treinamento: {result.training_time:.2f}string_data")
        
    except Exception as e:
        print(f"Erro no pipeline: {e}") 