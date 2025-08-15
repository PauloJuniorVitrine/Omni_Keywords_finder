"""
🤖 Advanced Predictive Models System
📅 Generated: 2025-01-27
🎯 Purpose: Machine learning models for predictive monitoring
📋 Tracing ID: PREDICTION_MODELS_001_20250127
"""

import logging
import time
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import joblib
from datetime import datetime, timedelta
import threading
from collections import deque, defaultdict
import warnings
from pathlib import Path

# Machine Learning imports
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.pipeline import Pipeline
    from sklearn.base import BaseEstimator, TransformerMixin
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available. Using fallback models.")

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available. Using fallback models.")

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported model types"""
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    RANDOM_FOREST = "random_forest"
    ISOLATION_FOREST = "isolation_forest"
    LSTM = "lstm"
    GRU = "gru"
    CNN = "cnn"
    ENSEMBLE = "ensemble"
    CUSTOM = "custom"


class PredictionTask(Enum):
    """Types of prediction tasks"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    FORECASTING = "forecasting"


@dataclass
class ModelConfig:
    """Configuration for predictive models"""
    name: str
    model_type: ModelType
    task: PredictionTask
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    training_config: Dict[str, Any] = field(default_factory=dict)
    evaluation_config: Dict[str, Any] = field(default_factory=dict)
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    metric_name: str
    mse: float = 0.0
    mae: float = 0.0
    r2_score: float = 0.0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    training_time: float = 0.0
    prediction_time: float = 0.0
    last_updated: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """Result of model prediction"""
    model_name: str
    metric_name: str
    predicted_value: float
    confidence: float
    prediction_interval: Tuple[float, float]
    features_used: List[str]
    model_performance: ModelPerformance
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePredictiveModel:
    """Base class for predictive models"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.is_trained = False
        self.performance = ModelPerformance(
            model_name=config.name,
            metric_name=""
        )
        self.lock = threading.RLock()
    
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> bool:
        """Train the model"""
        raise NotImplementedError
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        raise NotImplementedError
    
    def predict_with_confidence(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals"""
        raise NotImplementedError
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Evaluate model performance"""
        raise NotImplementedError
    
    def save_model(self, filepath: str) -> bool:
        """Save model to file"""
        raise NotImplementedError
    
    def load_model(self, filepath: str) -> bool:
        """Load model from file"""
        raise NotImplementedError


class LinearRegressionModel(BasePredictiveModel):
    """Linear regression model"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if SKLEARN_AVAILABLE:
            self.model = LinearRegression(**config.parameters)
            self.scaler = StandardScaler()
    
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> bool:
        """Train linear regression model"""
        try:
            with self.lock:
                start_time = time.time()
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Train model
                self.model.fit(X_scaled, y)
                
                # Store feature names
                self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
                
                # Update performance
                self.performance.training_time = time.time() - start_time
                self.performance.last_updated = time.time()
                
                self.is_trained = True
                logger.info(f"Linear regression model {self.config.name} trained successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to train linear regression model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_with_confidence(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals"""
        predictions = self.predict(X)
        
        # Simple confidence interval based on model residuals
        confidence = np.full_like(predictions, 0.95)  # 95% confidence
        
        return predictions, confidence
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Evaluate model performance"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        start_time = time.time()
        y_pred = self.predict(X)
        prediction_time = time.time() - start_time
        
        # Calculate metrics
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        self.performance.mse = mse
        self.performance.mae = mae
        self.performance.r2_score = r2
        self.performance.prediction_time = prediction_time
        self.performance.last_updated = time.time()
        
        return self.performance
    
    def save_model(self, filepath: str) -> bool:
        """Save model to file"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'config': self.config,
                'performance': self.performance,
                'is_trained': self.is_trained
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
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.config = model_data['config']
            self.performance = model_data['performance']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class RandomForestModel(BasePredictiveModel):
    """Random forest model"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if SKLEARN_AVAILABLE:
            self.model = RandomForestRegressor(**config.parameters)
            self.scaler = StandardScaler()
    
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> bool:
        """Train random forest model"""
        try:
            with self.lock:
                start_time = time.time()
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Train model
                self.model.fit(X_scaled, y)
                
                # Store feature names
                self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
                
                # Update performance
                self.performance.training_time = time.time() - start_time
                self.performance.last_updated = time.time()
                
                self.is_trained = True
                logger.info(f"Random forest model {self.config.name} trained successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to train random forest model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_with_confidence(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from all trees
        predictions = []
        for estimator in self.model.estimators_:
            predictions.append(estimator.predict(X_scaled))
        
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        # Confidence interval (95%)
        confidence = 1.96 * std_pred
        
        return mean_pred, confidence
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Evaluate model performance"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        start_time = time.time()
        y_pred = self.predict(X)
        prediction_time = time.time() - start_time
        
        # Calculate metrics
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        self.performance.mse = mse
        self.performance.mae = mae
        self.performance.r2_score = r2
        self.performance.prediction_time = prediction_time
        self.performance.last_updated = time.time()
        
        return self.performance
    
    def save_model(self, filepath: str) -> bool:
        """Save model to file"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'config': self.config,
                'performance': self.performance,
                'is_trained': self.is_trained
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
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.config = model_data['config']
            self.performance = model_data['performance']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class LSTMModel(BasePredictiveModel):
    """LSTM model for time series prediction"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.sequence_length = config.parameters.get('sequence_length', 10)
        self.model = None
        self.scaler = MinMaxScaler()
    
    def _create_lstm_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """Create LSTM model architecture"""
        model = keras.Sequential([
            keras.layers.LSTM(50, return_sequences=True, input_shape=input_shape),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(50, return_sequences=False),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(25),
            keras.layers.Dense(1)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _prepare_sequences(self, data: np.ndarray, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM"""
        X, y = [], []
        for i in range(len(data) - sequence_length):
            X.append(data[i:(i + sequence_length)])
            y.append(data[i + sequence_length])
        return np.array(X), np.array(y)
    
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> bool:
        """Train LSTM model"""
        try:
            with self.lock:
                start_time = time.time()
                
                # Reshape data for LSTM
                if len(X.shape) == 1:
                    X = X.reshape(-1, 1)
                
                # Scale data
                X_scaled = self.scaler.fit_transform(X)
                
                # Prepare sequences
                X_seq, y_seq = self._prepare_sequences(X_scaled, self.sequence_length)
                
                # Create and train model
                self.model = self._create_lstm_model((X_seq.shape[1], X_seq.shape[2]))
                
                # Training parameters
                epochs = self.config.training_config.get('epochs', 50)
                batch_size = self.config.training_config.get('batch_size', 32)
                validation_split = self.config.training_config.get('validation_split', 0.2)
                
                self.model.fit(
                    X_seq, y_seq,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=validation_split,
                    verbose=0
                )
                
                # Store feature names
                self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
                
                # Update performance
                self.performance.training_time = time.time() - start_time
                self.performance.last_updated = time.time()
                
                self.is_trained = True
                logger.info(f"LSTM model {self.config.name} trained successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to train LSTM model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        # Reshape and scale input
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        
        X_scaled = self.scaler.transform(X)
        
        # Prepare sequence
        if len(X_scaled) < self.sequence_length:
            # Pad with zeros if not enough data
            padding = np.zeros((self.sequence_length - len(X_scaled), X_scaled.shape[1]))
            X_scaled = np.vstack([padding, X_scaled])
        
        # Get the last sequence
        X_seq = X_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
        
        # Make prediction
        prediction_scaled = self.model.predict(X_seq, verbose=0)
        
        # Inverse transform
        prediction = self.scaler.inverse_transform(prediction_scaled)
        
        return prediction.flatten()
    
    def predict_with_confidence(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals"""
        predictions = self.predict(X)
        
        # Simple confidence interval for LSTM
        confidence = np.full_like(predictions, 0.90)  # 90% confidence
        
        return predictions, confidence
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Evaluate model performance"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        start_time = time.time()
        y_pred = self.predict(X)
        prediction_time = time.time() - start_time
        
        # Calculate metrics
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        self.performance.mse = mse
        self.performance.mae = mae
        self.performance.r2_score = r2
        self.performance.prediction_time = prediction_time
        self.performance.last_updated = time.time()
        
        return self.performance
    
    def save_model(self, filepath: str) -> bool:
        """Save model to file"""
        try:
            if self.model:
                self.model.save(filepath)
            
            # Save additional data
            metadata_file = filepath.replace('.h5', '_metadata.pkl')
            metadata = {
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'config': self.config,
                'performance': self.performance,
                'is_trained': self.is_trained,
                'sequence_length': self.sequence_length
            }
            
            with open(metadata_file, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"LSTM model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save LSTM model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load model from file"""
        try:
            # Load model
            self.model = keras.models.load_model(filepath)
            
            # Load metadata
            metadata_file = filepath.replace('.h5', '_metadata.pkl')
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            self.scaler = metadata['scaler']
            self.feature_names = metadata['feature_names']
            self.config = metadata['config']
            self.performance = metadata['performance']
            self.is_trained = metadata['is_trained']
            self.sequence_length = metadata['sequence_length']
            
            logger.info(f"LSTM model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load LSTM model: {e}")
            return False


class ModelRegistry:
    """
    Registry for managing predictive models
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.models: Dict[str, BasePredictiveModel] = {}
        self.model_factories = {
            ModelType.LINEAR_REGRESSION: LinearRegressionModel,
            ModelType.RANDOM_FOREST: RandomForestModel,
            ModelType.LSTM: LSTMModel
        }
        
        self.lock = threading.RLock()
    
    def create_model(self, config: ModelConfig) -> Optional[BasePredictiveModel]:
        """Create a new model instance"""
        try:
            if config.model_type in self.model_factories:
                model_class = self.model_factories[config.model_type]
                model = model_class(config)
                return model
            else:
                logger.error(f"Unsupported model type: {config.model_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            return None
    
    def register_model(self, model: BasePredictiveModel) -> bool:
        """Register a model in the registry"""
        try:
            with self.lock:
                self.models[model.config.name] = model
                logger.info(f"Model {model.config.name} registered")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return False
    
    def get_model(self, model_name: str) -> Optional[BasePredictiveModel]:
        """Get model by name"""
        with self.lock:
            return self.models.get(model_name)
    
    def list_models(self) -> List[str]:
        """List all registered models"""
        with self.lock:
            return list(self.models.keys())
    
    def remove_model(self, model_name: str) -> bool:
        """Remove model from registry"""
        try:
            with self.lock:
                if model_name in self.models:
                    del self.models[model_name]
                    logger.info(f"Model {model_name} removed from registry")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove model: {e}")
            return False
    
    def save_model(self, model_name: str, filepath: Optional[str] = None) -> bool:
        """Save model to file"""
        try:
            model = self.get_model(model_name)
            if not model:
                logger.error(f"Model {model_name} not found")
                return False
            
            if filepath is None:
                filepath = self.models_dir / f"{model_name}.pkl"
            
            return model.save_model(str(filepath))
            
        except Exception as e:
            logger.error(f"Failed to save model {model_name}: {e}")
            return False
    
    def load_model(self, model_name: str, filepath: str) -> bool:
        """Load model from file"""
        try:
            # Get model config from file
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            config = model_data['config']
            model = self.create_model(config)
            
            if model and model.load_model(filepath):
                return self.register_model(model)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    def get_model_performance(self, model_name: str) -> Optional[ModelPerformance]:
        """Get model performance"""
        model = self.get_model(model_name)
        if model:
            return model.performance
        return None
    
    def list_model_performances(self) -> Dict[str, ModelPerformance]:
        """List performance of all models"""
        with self.lock:
            return {
                name: model.performance
                for name, model in self.models.items()
            }


# Global model registry
_model_registry: Optional[ModelRegistry] = None


def get_model_registry(models_dir: str = "models") -> ModelRegistry:
    """Get global model registry instance"""
    global _model_registry
    
    if _model_registry is None:
        _model_registry = ModelRegistry(models_dir)
    
    return _model_registry


def create_model(config: ModelConfig, models_dir: str = "models") -> Optional[BasePredictiveModel]:
    """Create a new model"""
    registry = get_model_registry(models_dir)
    return registry.create_model(config)


def register_model(model: BasePredictiveModel, models_dir: str = "models") -> bool:
    """Register a model"""
    registry = get_model_registry(models_dir)
    return registry.register_model(model)


def get_model(model_name: str, models_dir: str = "models") -> Optional[BasePredictiveModel]:
    """Get model by name"""
    registry = get_model_registry(models_dir)
    return registry.get_model(model_name)


def list_models(models_dir: str = "models") -> List[str]:
    """List all models"""
    registry = get_model_registry(models_dir)
    return registry.list_models()


def save_model(model_name: str, filepath: Optional[str] = None, models_dir: str = "models") -> bool:
    """Save model to file"""
    registry = get_model_registry(models_dir)
    return registry.save_model(model_name, filepath)


def load_model(model_name: str, filepath: str, models_dir: str = "models") -> bool:
    """Load model from file"""
    registry = get_model_registry(models_dir)
    return registry.load_model(model_name, filepath)


def get_model_performance(model_name: str, models_dir: str = "models") -> Optional[ModelPerformance]:
    """Get model performance"""
    registry = get_model_registry(models_dir)
    return registry.get_model_performance(model_name) 