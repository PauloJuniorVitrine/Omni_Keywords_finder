"""
🔍 Anomaly Detection Models
📅 Generated: 2025-01-27
🎯 Purpose: Machine learning models for advanced anomaly detection
📋 Tracing ID: ANOMALY_MODELS_002_20250127
"""

import logging
import time
import numpy as np
import statistics
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from collections import deque, defaultdict
import threading
from datetime import datetime, timedelta
import warnings

# Suppress warnings for optional ML libraries
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of anomaly detection models"""
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    ELLIPTIC_ENVELOPE = "elliptic_envelope"
    AUTOENCODER = "autoencoder"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"
    CUSTOM = "custom"


class ModelStatus(Enum):
    """Model training and evaluation status"""
    NOT_TRAINED = "not_trained"
    TRAINING = "training"
    TRAINED = "trained"
    EVALUATING = "evaluating"
    EVALUATED = "evaluated"
    ERROR = "error"


@dataclass
class ModelConfig:
    """Configuration for anomaly detection models"""
    model_type: ModelType = ModelType.ISOLATION_FOREST
    window_size: int = 100
    feature_count: int = 5
    contamination: float = 0.1
    random_state: int = 42
    n_estimators: int = 100
    max_samples: Union[int, float] = "auto"
    bootstrap: bool = True
    n_jobs: int = -1
    verbose: int = 0
    auto_retrain: bool = True
    retrain_interval: int = 3600  # seconds
    min_training_samples: int = 50
    max_training_samples: int = 10000
    evaluation_threshold: float = 0.8
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    auc: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    training_time: float = 0.0
    prediction_time: float = 0.0
    last_evaluation: float = field(default_factory=time.time)


@dataclass
class ModelResult:
    """Result of model prediction"""
    is_anomaly: bool
    confidence: float = 0.0
    score: float = 0.0
    threshold: float = 0.0
    features: List[float] = field(default_factory=list)
    model_name: str = ""
    prediction_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAnomalyModel:
    """Base class for anomaly detection models"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.status = ModelStatus.NOT_TRAINED
        self.metrics = ModelMetrics()
        self.training_data = deque(maxlen=config.max_training_samples)
        self.last_training_time = 0
        self.lock = threading.RLock()
        
    def add_training_data(self, data_point: Union[float, List[float]], 
                         is_anomaly: bool = False):
        """Add data point for training"""
        with self.lock:
            self.training_data.append({
                'data': data_point,
                'is_anomaly': is_anomaly,
                'timestamp': time.time()
            })
    
    def extract_features(self, data: Union[float, List[float]]) -> List[float]:
        """Extract features from data point"""
        if isinstance(data, (int, float)):
            # Single value - create basic features
            return [float(data)]
        elif isinstance(data, list):
            # List of values - use as features
            return [float(x) for x in data]
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for model"""
        if len(self.training_data) < self.config.min_training_samples:
            raise ValueError(f"Insufficient training data: {len(self.training_data)} < {self.config.min_training_samples}")
        
        features = []
        labels = []
        
        for item in self.training_data:
            feature_vector = self.extract_features(item['data'])
            if len(feature_vector) == self.config.feature_count:
                features.append(feature_vector)
                labels.append(1 if item['is_anomaly'] else 0)
        
        if len(features) < self.config.min_training_samples:
            raise ValueError(f"Insufficient valid training samples: {len(features)}")
        
        return np.array(features), np.array(labels)
    
    def train(self) -> bool:
        """Train the model"""
        try:
            with self.lock:
                self.status = ModelStatus.TRAINING
                
                # Prepare training data
                X, y = self.prepare_training_data()
                
                # Train model
                start_time = time.time()
                self._train_model(X, y)
                training_time = time.time() - start_time
                
                # Update metrics
                self.metrics.training_time = training_time
                self.metrics.last_evaluation = time.time()
                self.last_training_time = time.time()
                
                self.status = ModelStatus.TRAINED
                logger.info(f"Model trained successfully in {training_time:.2f}s")
                return True
                
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            self.status = ModelStatus.ERROR
            return False
    
    def predict(self, data: Union[float, List[float]]) -> ModelResult:
        """Predict anomaly for data point"""
        if self.model is None or self.status != ModelStatus.TRAINED:
            return ModelResult(
                is_anomaly=False,
                confidence=0.0,
                message="Model not trained"
            )
        
        try:
            start_time = time.time()
            
            # Extract features
            features = self.extract_features(data)
            
            # Ensure feature count matches
            if len(features) != self.config.feature_count:
                # Pad or truncate features
                if len(features) < self.config.feature_count:
                    features.extend([0.0] * (self.config.feature_count - len(features)))
                else:
                    features = features[:self.config.feature_count]
            
            # Make prediction
            prediction = self._predict_model(features)
            prediction_time = time.time() - start_time
            
            # Update metrics
            self.metrics.prediction_time = prediction_time
            
            return prediction
            
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            return ModelResult(
                is_anomaly=False,
                confidence=0.0,
                message=f"Prediction error: {str(e)}"
            )
    
    def evaluate(self) -> ModelMetrics:
        """Evaluate model performance"""
        if self.model is None or self.status != ModelStatus.TRAINED:
            return self.metrics
        
        try:
            with self.lock:
                self.status = ModelStatus.EVALUATING
                
                # Prepare evaluation data
                X, y = self.prepare_training_data()
                
                # Make predictions
                predictions = []
                for i in range(len(X)):
                    result = self._predict_model(X[i])
                    predictions.append(1 if result.is_anomaly else 0)
                
                # Calculate metrics
                self._calculate_metrics(y, predictions)
                self.status = ModelStatus.EVALUATED
                
                return self.metrics
                
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            self.status = ModelStatus.ERROR
            return self.metrics
    
    def _train_model(self, X: np.ndarray, y: np.ndarray):
        """Train the specific model implementation"""
        raise NotImplementedError("Subclasses must implement _train_model")
    
    def _predict_model(self, features: List[float]) -> ModelResult:
        """Make prediction using the specific model implementation"""
        raise NotImplementedError("Subclasses must implement _predict_model")
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: List[int]):
        """Calculate performance metrics"""
        if len(y_true) == 0 or len(y_pred) == 0:
            return
        
        # Calculate basic metrics
        tp = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and y_pred[i] == 1)
        tn = sum(1 for i in range(len(y_true)) if y_true[i] == 0 and y_pred[i] == 0)
        fp = sum(1 for i in range(len(y_true)) if y_true[i] == 0 and y_pred[i] == 1)
        fn = sum(1 for i in range(len(y_true)) if y_true[i] == 1 and y_pred[i] == 0)
        
        # Calculate derived metrics
        total = len(y_true)
        if total > 0:
            self.metrics.accuracy = (tp + tn) / total
        
        if (tp + fp) > 0:
            self.metrics.precision = tp / (tp + fp)
        
        if (tp + fn) > 0:
            self.metrics.recall = tp / (tp + fn)
        
        if (self.metrics.precision + self.metrics.recall) > 0:
            self.metrics.f1_score = 2 * (self.metrics.precision * self.metrics.recall) / (self.metrics.precision + self.metrics.recall)
        
        if (fp + tn) > 0:
            self.metrics.false_positive_rate = fp / (fp + tn)
        
        if (fn + tp) > 0:
            self.metrics.false_negative_rate = fn / (fn + tp)
    
    def save_model(self, filepath: str) -> bool:
        """Save model to file"""
        try:
            with self.lock:
                model_data = {
                    'config': self.config,
                    'status': self.status,
                    'metrics': self.metrics,
                    'last_training_time': self.last_training_time,
                    'model': self.model
                }
                
                with open(filepath, 'wb') as f:
                    pickle.dump(model_data, f)
                
                logger.info(f"Model saved to {filepath}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load model from file"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            with self.lock:
                self.config = model_data['config']
                self.status = model_data['status']
                self.metrics = model_data['metrics']
                self.last_training_time = model_data['last_training_time']
                self.model = model_data['model']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def should_retrain(self) -> bool:
        """Check if model should be retrained"""
        if not self.config.auto_retrain:
            return False
        
        current_time = time.time()
        time_since_training = current_time - self.last_training_time
        
        return time_since_training > self.config.retrain_interval


class IsolationForestModel(BaseAnomalyModel):
    """Isolation Forest anomaly detection model"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._setup_model()
    
    def _setup_model(self):
        """Setup Isolation Forest model"""
        try:
            from sklearn.ensemble import IsolationForest
            
            self.model = IsolationForest(
                contamination=self.config.contamination,
                random_state=self.config.random_state,
                n_estimators=self.config.n_estimators,
                max_samples=self.config.max_samples,
                bootstrap=self.config.bootstrap,
                n_jobs=self.config.n_jobs,
                verbose=self.config.verbose,
                **self.config.custom_parameters
            )
            
        except ImportError:
            logger.warning("scikit-learn not available. Using fallback model.")
            self.model = None
    
    def _train_model(self, X: np.ndarray, y: np.ndarray):
        """Train Isolation Forest model"""
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        # Isolation Forest doesn't use labels, so we ignore y
        self.model.fit(X)
    
    def _predict_model(self, features: List[float]) -> ModelResult:
        """Make prediction using Isolation Forest"""
        if self.model is None:
            raise RuntimeError("Model not trained")
        
        X = np.array([features])
        
        # Predict anomaly (-1 for anomaly, 1 for normal)
        prediction = self.model.predict(X)[0]
        is_anomaly = prediction == -1
        
        # Get anomaly score
        score = self.model.score_samples(X)[0]
        
        # Convert score to confidence (lower score = higher confidence for anomaly)
        confidence = 1.0 - (score + 0.5)  # Normalize to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        return ModelResult(
            is_anomaly=is_anomaly,
            confidence=confidence,
            score=score,
            threshold=self.config.contamination,
            features=features,
            model_name="IsolationForest",
            prediction_time=self.metrics.prediction_time
        )


class OneClassSVMModel(BaseAnomalyModel):
    """One-Class SVM anomaly detection model"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._setup_model()
    
    def _setup_model(self):
        """Setup One-Class SVM model"""
        try:
            from sklearn.svm import OneClassSVM
            
            self.model = OneClassSVM(
                kernel='rbf',
                nu=self.config.contamination,
                random_state=self.config.random_state,
                verbose=self.config.verbose,
                **self.config.custom_parameters
            )
            
        except ImportError:
            logger.warning("scikit-learn not available. Using fallback model.")
            self.model = None
    
    def _train_model(self, X: np.ndarray, y: np.ndarray):
        """Train One-Class SVM model"""
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        # One-Class SVM doesn't use labels
        self.model.fit(X)
    
    def _predict_model(self, features: List[float]) -> ModelResult:
        """Make prediction using One-Class SVM"""
        if self.model is None:
            raise RuntimeError("Model not trained")
        
        X = np.array([features])
        
        # Predict anomaly (-1 for anomaly, 1 for normal)
        prediction = self.model.predict(X)[0]
        is_anomaly = prediction == -1
        
        # Get decision function score
        score = self.model.decision_function(X)[0]
        
        # Convert score to confidence
        confidence = 1.0 - (score + 1.0)  # Normalize to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        return ModelResult(
            is_anomaly=is_anomaly,
            confidence=confidence,
            score=score,
            threshold=0.0,
            features=features,
            model_name="OneClassSVM",
            prediction_time=self.metrics.prediction_time
        )


class LocalOutlierFactorModel(BaseAnomalyModel):
    """Local Outlier Factor anomaly detection model"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._setup_model()
    
    def _setup_model(self):
        """Setup Local Outlier Factor model"""
        try:
            from sklearn.neighbors import LocalOutlierFactor
            
            self.model = LocalOutlierFactor(
                contamination=self.config.contamination,
                n_neighbors=20,
                algorithm='auto',
                leaf_size=30,
                metric='minkowski',
                p=2,
                metric_params=None,
                novelty=True,
                n_jobs=self.config.n_jobs,
                **self.config.custom_parameters
            )
            
        except ImportError:
            logger.warning("scikit-learn not available. Using fallback model.")
            self.model = None
    
    def _train_model(self, X: np.ndarray, y: np.ndarray):
        """Train Local Outlier Factor model"""
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        # LOF doesn't use labels
        self.model.fit(X)
    
    def _predict_model(self, features: List[float]) -> ModelResult:
        """Make prediction using Local Outlier Factor"""
        if self.model is None:
            raise RuntimeError("Model not trained")
        
        X = np.array([features])
        
        # Predict anomaly (-1 for anomaly, 1 for normal)
        prediction = self.model.predict(X)[0]
        is_anomaly = prediction == -1
        
        # Get decision function score
        score = self.model.decision_function(X)[0]
        
        # Convert score to confidence
        confidence = 1.0 - (score + 1.0)  # Normalize to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        return ModelResult(
            is_anomaly=is_anomaly,
            confidence=confidence,
            score=score,
            threshold=0.0,
            features=features,
            model_name="LocalOutlierFactor",
            prediction_time=self.metrics.prediction_time
        )


class EnsembleAnomalyModel(BaseAnomalyModel):
    """Ensemble anomaly detection model combining multiple algorithms"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.models = {}
        self._setup_models()
    
    def _setup_models(self):
        """Setup ensemble models"""
        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.svm import OneClassSVM
            from sklearn.neighbors import LocalOutlierFactor
            
            self.models = {
                'isolation_forest': IsolationForest(
                    contamination=self.config.contamination,
                    random_state=self.config.random_state,
                    n_estimators=self.config.n_estimators
                ),
                'one_class_svm': OneClassSVM(
                    kernel='rbf',
                    nu=self.config.contamination,
                    random_state=self.config.random_state
                ),
                'local_outlier_factor': LocalOutlierFactor(
                    contamination=self.config.contamination,
                    novelty=True,
                    n_neighbors=20
                )
            }
            
        except ImportError:
            logger.warning("scikit-learn not available. Using fallback models.")
            self.models = {}
    
    def _train_model(self, X: np.ndarray, y: np.ndarray):
        """Train ensemble models"""
        if not self.models:
            raise RuntimeError("No models available")
        
        for name, model in self.models.items():
            try:
                model.fit(X)
                logger.info(f"Trained {name} model")
            except Exception as e:
                logger.error(f"Failed to train {name} model: {e}")
    
    def _predict_model(self, features: List[float]) -> ModelResult:
        """Make ensemble prediction"""
        if not self.models:
            raise RuntimeError("No models available")
        
        X = np.array([features])
        predictions = []
        scores = []
        
        for name, model in self.models.items():
            try:
                # Get prediction
                pred = model.predict(X)[0]
                predictions.append(1 if pred == -1 else 0)  # Convert to binary
                
                # Get score
                if hasattr(model, 'score_samples'):
                    score = model.score_samples(X)[0]
                elif hasattr(model, 'decision_function'):
                    score = model.decision_function(X)[0]
                else:
                    score = 0.0
                
                scores.append(score)
                
            except Exception as e:
                logger.warning(f"Error in {name} prediction: {e}")
                predictions.append(0)
                scores.append(0.0)
        
        if not predictions:
            return ModelResult(
                is_anomaly=False,
                confidence=0.0,
                message="No valid predictions"
            )
        
        # Calculate ensemble prediction
        anomaly_votes = sum(predictions)
        total_votes = len(predictions)
        ensemble_score = anomaly_votes / total_votes
        
        # Determine if anomaly (majority vote)
        is_anomaly = ensemble_score > 0.5
        
        # Calculate confidence based on agreement
        if is_anomaly:
            confidence = ensemble_score
        else:
            confidence = 1.0 - ensemble_score
        
        # Average score
        avg_score = statistics.mean(scores) if scores else 0.0
        
        return ModelResult(
            is_anomaly=is_anomaly,
            confidence=confidence,
            score=avg_score,
            threshold=0.5,
            features=features,
            model_name="Ensemble",
            prediction_time=self.metrics.prediction_time,
            metadata={
                'individual_predictions': predictions,
                'individual_scores': scores,
                'ensemble_score': ensemble_score
            }
        )


class AnomalyModelFactory:
    """Factory for creating anomaly detection models"""
    
    @staticmethod
    def create_model(model_type: ModelType, config: Optional[ModelConfig] = None) -> BaseAnomalyModel:
        """Create anomaly detection model"""
        if config is None:
            config = ModelConfig(model_type=model_type)
        
        if model_type == ModelType.ISOLATION_FOREST:
            return IsolationForestModel(config)
        elif model_type == ModelType.ONE_CLASS_SVM:
            return OneClassSVMModel(config)
        elif model_type == ModelType.LOCAL_OUTLIER_FACTOR:
            return LocalOutlierFactorModel(config)
        elif model_type == ModelType.ENSEMBLE:
            return EnsembleAnomalyModel(config)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")


# Global model manager
_model_manager: Optional[Dict[str, BaseAnomalyModel]] = None


def get_model_manager() -> Dict[str, BaseAnomalyModel]:
    """Get global model manager"""
    global _model_manager
    if _model_manager is None:
        _model_manager = {}
    return _model_manager


def create_model(model_name: str, model_type: ModelType, 
                config: Optional[ModelConfig] = None) -> BaseAnomalyModel:
    """Create and register a new model"""
    manager = get_model_manager()
    
    if model_name in manager:
        logger.warning(f"Model {model_name} already exists. Overwriting.")
    
    model = AnomalyModelFactory.create_model(model_type, config)
    manager[model_name] = model
    
    return model


def get_model(model_name: str) -> Optional[BaseAnomalyModel]:
    """Get model by name"""
    manager = get_model_manager()
    return manager.get(model_name)


def train_model(model_name: str, data: List[Tuple[Union[float, List[float]], bool]]) -> bool:
    """Train model with labeled data"""
    model = get_model(model_name)
    if model is None:
        logger.error(f"Model {model_name} not found")
        return False
    
    # Add training data
    for data_point, is_anomaly in data:
        model.add_training_data(data_point, is_anomaly)
    
    # Train model
    return model.train()


def predict_anomaly(model_name: str, data: Union[float, List[float]]) -> ModelResult:
    """Predict anomaly using model"""
    model = get_model(model_name)
    if model is None:
        return ModelResult(
            is_anomaly=False,
            confidence=0.0,
            message=f"Model {model_name} not found"
        )
    
    return model.predict(data)


def evaluate_model(model_name: str) -> ModelMetrics:
    """Evaluate model performance"""
    model = get_model(model_name)
    if model is None:
        return ModelMetrics()
    
    return model.evaluate()


def save_model(model_name: str, filepath: str) -> bool:
    """Save model to file"""
    model = get_model(model_name)
    if model is None:
        return False
    
    return model.save_model(filepath)


def load_model(model_name: str, filepath: str) -> bool:
    """Load model from file"""
    model = get_model(model_name)
    if model is None:
        return False
    
    return model.load_model(filepath) 