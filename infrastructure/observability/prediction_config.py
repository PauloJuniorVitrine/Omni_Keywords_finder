"""
⚙️ Advanced Predictive Monitoring Configuration System
📅 Generated: 2025-01-27
🎯 Purpose: Comprehensive configuration management for predictive monitoring
📋 Tracing ID: PREDICTION_CONFIG_001_20250127
"""

import logging
import yaml
import json
import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PredictionAlgorithm(Enum):
    """Supported prediction algorithms"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    LSTM = "lstm"
    GRU = "gru"
    CNN = "cnn"
    ENSEMBLE = "ensemble"
    ARIMA = "arima"
    PROPHET = "prophet"
    CUSTOM = "custom"


class PredictionType(Enum):
    """Types of predictions"""
    TREND = "trend"
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"
    THRESHOLD_BREACH = "threshold_breach"
    ANOMALY = "anomaly"
    CAPACITY = "capacity"
    PERFORMANCE = "performance"
    RESOURCE = "resource"


@dataclass
class AlgorithmConfig:
    """Configuration for individual prediction algorithms"""
    name: str
    algorithm_type: PredictionAlgorithm
    enabled: bool = True
    weight: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    training_config: Dict[str, Any] = field(default_factory=dict)
    evaluation_config: Dict[str, Any] = field(default_factory=dict)
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricConfig:
    """Configuration for individual metrics"""
    name: str
    description: str = ""
    unit: str = ""
    enabled: bool = True
    algorithms: List[str] = field(default_factory=list)
    window_size: int = 100
    prediction_horizon: int = 24  # hours
    min_data_points: int = 50
    alert_threshold: float = 2.0
    critical_threshold: float = 3.0
    confidence_threshold: float = 0.7
    cooldown_period: int = 300  # seconds
    custom_config: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    name: str
    description: str = ""
    is_production: bool = False
    alert_channels: List[str] = field(default_factory=lambda: ["console"])
    escalation_rules: Dict[str, Any] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictiveMonitoringConfig:
    """Main configuration for predictive monitoring system"""
    # Global settings
    service_name: str = "omni-keywords-finder"
    environment: str = "development"
    version: str = "1.0.0"
    
    # Algorithm configurations
    algorithms: Dict[str, AlgorithmConfig] = field(default_factory=dict)
    
    # Metric configurations
    metrics: Dict[str, MetricConfig] = field(default_factory=dict)
    
    # Environment configurations
    environments: Dict[str, EnvironmentConfig] = field(default_factory=dict)
    
    # Global thresholds
    global_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Alerting configuration
    alerting: Dict[str, Any] = field(default_factory=dict)
    
    # Performance settings
    performance: Dict[str, Any] = field(default_factory=dict)
    
    # Custom settings
    custom: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "system"
    version_history: List[Dict[str, Any]] = field(default_factory=list)


class ConfigManager:
    """
    Advanced configuration manager for predictive monitoring
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/predictive_monitoring.yaml"
        self.config = self._load_default_config()
        self.lock = threading.RLock()
        self.watchers: List[Callable] = []
        self.last_modified = 0.0
        
        # Load configuration from file if it exists
        if os.path.exists(self.config_path):
            self.load_config()
    
    def _load_default_config(self) -> PredictiveMonitoringConfig:
        """Load default configuration"""
        return PredictiveMonitoringConfig(
            algorithms={
                "linear_regression": AlgorithmConfig(
                    name="linear_regression",
                    algorithm_type=PredictionAlgorithm.LINEAR_REGRESSION,
                    parameters={
                        "fit_intercept": True,
                        "normalize": False
                    },
                    training_config={
                        "test_size": 0.2,
                        "random_state": 42
                    }
                ),
                "random_forest": AlgorithmConfig(
                    name="random_forest",
                    algorithm_type=PredictionAlgorithm.RANDOM_FOREST,
                    parameters={
                        "n_estimators": 100,
                        "max_depth": 10,
                        "random_state": 42
                    },
                    training_config={
                        "test_size": 0.2,
                        "random_state": 42
                    }
                ),
                "lstm": AlgorithmConfig(
                    name="lstm",
                    algorithm_type=PredictionAlgorithm.LSTM,
                    parameters={
                        "sequence_length": 10,
                        "units": 50,
                        "dropout": 0.2
                    },
                    training_config={
                        "epochs": 50,
                        "batch_size": 32,
                        "validation_split": 0.2
                    }
                ),
                "ensemble": AlgorithmConfig(
                    name="ensemble",
                    algorithm_type=PredictionAlgorithm.ENSEMBLE,
                    parameters={
                        "algorithms": ["linear_regression", "random_forest"],
                        "voting_method": "average"
                    },
                    training_config={
                        "test_size": 0.2,
                        "random_state": 42
                    }
                )
            },
            metrics={
                "cpu_usage": MetricConfig(
                    name="cpu_usage",
                    description="CPU usage percentage",
                    unit="%",
                    algorithms=["linear_regression", "random_forest", "lstm"],
                    prediction_horizon=6,
                    alert_threshold=80.0,
                    critical_threshold=95.0,
                    confidence_threshold=0.8
                ),
                "memory_usage": MetricConfig(
                    name="memory_usage",
                    description="Memory usage percentage",
                    unit="%",
                    algorithms=["linear_regression", "random_forest", "lstm"],
                    prediction_horizon=6,
                    alert_threshold=85.0,
                    critical_threshold=95.0,
                    confidence_threshold=0.8
                ),
                "response_time": MetricConfig(
                    name="response_time",
                    description="API response time",
                    unit="ms",
                    algorithms=["linear_regression", "random_forest", "lstm"],
                    prediction_horizon=12,
                    alert_threshold=1000.0,
                    critical_threshold=5000.0,
                    confidence_threshold=0.7
                ),
                "error_rate": MetricConfig(
                    name="error_rate",
                    description="Error rate percentage",
                    unit="%",
                    algorithms=["linear_regression", "random_forest"],
                    prediction_horizon=24,
                    alert_threshold=5.0,
                    critical_threshold=10.0,
                    confidence_threshold=0.9
                ),
                "throughput": MetricConfig(
                    name="throughput",
                    description="Requests per second",
                    unit="req/s",
                    algorithms=["linear_regression", "random_forest", "lstm", "ensemble"],
                    prediction_horizon=24,
                    alert_threshold=100.0,
                    critical_threshold=50.0,
                    confidence_threshold=0.8
                )
            },
            environments={
                "development": EnvironmentConfig(
                    name="development",
                    description="Development environment",
                    is_production=False,
                    alert_channels=["console", "log"]
                ),
                "staging": EnvironmentConfig(
                    name="staging",
                    description="Staging environment",
                    is_production=False,
                    alert_channels=["console", "slack"]
                ),
                "production": EnvironmentConfig(
                    name="production",
                    description="Production environment",
                    is_production=True,
                    alert_channels=["email", "slack", "pagerduty"],
                    escalation_rules={
                        "critical": {"delay": 300, "escalate_to": "oncall"},
                        "emergency": {"delay": 60, "escalate_to": "manager"}
                    }
                )
            },
            global_thresholds={
                "min_confidence": 0.7,
                "max_prediction_error": 0.1,
                "min_data_points": 50,
                "max_window_size": 1000,
                "max_prediction_horizon": 168  # 1 week
            },
            alerting={
                "enabled": True,
                "cooldown_period": 300,
                "max_alerts_per_hour": 10,
                "group_alerts": True,
                "suppression_rules": {}
            },
            performance={
                "max_concurrent_predictions": 100,
                "cache_size": 1000,
                "cleanup_interval": 3600,
                "max_history_size": 10000,
                "model_retraining_interval": 86400  # 24 hours
            }
        )
    
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """Load configuration from file"""
        path = config_path or self.config_path
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            with self.lock:
                self.config = self._deserialize_config(data)
                self.config.updated_at = datetime.now().isoformat()
                self.last_modified = os.path.getmtime(path)
            
            logger.info(f"Predictive monitoring configuration loaded from {path}")
            self._notify_watchers()
            return True
            
        except Exception as e:
            logger.error(f"Failed to load predictive monitoring configuration from {path}: {e}")
            return False
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """Save configuration to file"""
        path = config_path or self.config_path
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with self.lock:
                self.config.updated_at = datetime.now().isoformat()
                data = self._serialize_config(self.config)
            
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Predictive monitoring configuration saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save predictive monitoring configuration to {path}: {e}")
            return False
    
    def _serialize_config(self, config: PredictiveMonitoringConfig) -> Dict[str, Any]:
        """Serialize configuration to dictionary"""
        data = asdict(config)
        
        # Convert enums to strings
        for algorithm in data['algorithms'].values():
            algorithm['algorithm_type'] = algorithm['algorithm_type'].value
        
        return data
    
    def _deserialize_config(self, data: Dict[str, Any]) -> PredictiveMonitoringConfig:
        """Deserialize configuration from dictionary"""
        # Convert string enums back to enum objects
        for algorithm_data in data.get('algorithms', {}).values():
            if 'algorithm_type' in algorithm_data:
                algorithm_data['algorithm_type'] = PredictionAlgorithm(algorithm_data['algorithm_type'])
        
        # Create config object
        return PredictiveMonitoringConfig(**data)
    
    def get_algorithm_config(self, algorithm_name: str) -> Optional[AlgorithmConfig]:
        """Get algorithm configuration"""
        with self.lock:
            return self.config.algorithms.get(algorithm_name)
    
    def set_algorithm_config(self, algorithm_name: str, config: AlgorithmConfig):
        """Set algorithm configuration"""
        with self.lock:
            self.config.algorithms[algorithm_name] = config
            self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def get_metric_config(self, metric_name: str) -> Optional[MetricConfig]:
        """Get metric configuration"""
        with self.lock:
            return self.config.metrics.get(metric_name)
    
    def set_metric_config(self, metric_name: str, config: MetricConfig):
        """Set metric configuration"""
        with self.lock:
            self.config.metrics[metric_name] = config
            self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def get_environment_config(self, env_name: str) -> Optional[EnvironmentConfig]:
        """Get environment configuration"""
        with self.lock:
            return self.config.environments.get(env_name)
    
    def set_environment_config(self, env_name: str, config: EnvironmentConfig):
        """Set environment configuration"""
        with self.lock:
            self.config.environments[env_name] = config
            self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def add_metric(self, metric_config: MetricConfig):
        """Add new metric configuration"""
        with self.lock:
            self.config.metrics[metric_config.name] = metric_config
            self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def remove_metric(self, metric_name: str):
        """Remove metric configuration"""
        with self.lock:
            if metric_name in self.config.metrics:
                del self.config.metrics[metric_name]
                self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def add_algorithm(self, algorithm_config: AlgorithmConfig):
        """Add new algorithm configuration"""
        with self.lock:
            self.config.algorithms[algorithm_config.name] = algorithm_config
            self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def remove_algorithm(self, algorithm_name: str):
        """Remove algorithm configuration"""
        with self.lock:
            if algorithm_name in self.config.algorithms:
                del self.config.algorithms[algorithm_name]
                self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def get_enabled_algorithms(self) -> List[str]:
        """Get list of enabled algorithms"""
        with self.lock:
            return [
                name for name, config in self.config.algorithms.items()
                if config.enabled
            ]
    
    def get_enabled_metrics(self) -> List[str]:
        """Get list of enabled metrics"""
        with self.lock:
            return [
                name for name, config in self.config.metrics.items()
                if config.enabled
            ]
    
    def get_metrics_for_algorithm(self, algorithm_name: str) -> List[str]:
        """Get metrics that use a specific algorithm"""
        with self.lock:
            return [
                name for name, config in self.config.metrics.items()
                if algorithm_name in config.algorithms
            ]
    
    def get_algorithms_for_metric(self, metric_name: str) -> List[str]:
        """Get algorithms used by a specific metric"""
        with self.lock:
            metric_config = self.config.metrics.get(metric_name)
            if metric_config:
                return metric_config.algorithms
            return []
    
    def update_global_threshold(self, threshold_name: str, value: float):
        """Update global threshold"""
        with self.lock:
            self.config.global_thresholds[threshold_name] = value
            self.config.updated_at = datetime.now().isoformat()
        self._notify_watchers()
    
    def get_global_threshold(self, threshold_name: str) -> Optional[float]:
        """Get global threshold value"""
        with self.lock:
            return self.config.global_thresholds.get(threshold_name)
    
    def add_watcher(self, callback: Callable):
        """Add configuration change watcher"""
        with self.lock:
            if callback not in self.watchers:
                self.watchers.append(callback)
    
    def remove_watcher(self, callback: Callable):
        """Remove configuration change watcher"""
        with self.lock:
            if callback in self.watchers:
                self.watchers.remove(callback)
    
    def _notify_watchers(self):
        """Notify all watchers of configuration changes"""
        for callback in self.watchers:
            try:
                callback(self.config)
            except Exception as e:
                logger.error(f"Error in config watcher: {e}")
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return errors"""
        errors = {
            'algorithms': [],
            'metrics': [],
            'environments': [],
            'general': []
        }
        
        with self.lock:
            # Validate algorithms
            for name, config in self.config.algorithms.items():
                if not config.name:
                    errors['algorithms'].append(f"Algorithm {name}: missing name")
                if not config.algorithm_type:
                    errors['algorithms'].append(f"Algorithm {name}: missing algorithm type")
            
            # Validate metrics
            for name, config in self.config.metrics.items():
                if not config.name:
                    errors['metrics'].append(f"Metric {name}: missing name")
                if not config.algorithms:
                    errors['metrics'].append(f"Metric {name}: no algorithms specified")
                
                # Check if referenced algorithms exist
                for algorithm in config.algorithms:
                    if algorithm not in self.config.algorithms:
                        errors['metrics'].append(f"Metric {name}: algorithm '{algorithm}' not found")
                
                # Validate prediction horizon
                if config.prediction_horizon > self.config.global_thresholds.get('max_prediction_horizon', 168):
                    errors['metrics'].append(f"Metric {name}: prediction horizon exceeds maximum")
            
            # Validate environments
            for name, config in self.config.environments.items():
                if not config.name:
                    errors['environments'].append(f"Environment {name}: missing name")
        
        return errors
    
    def export_config(self, format: str = "yaml") -> str:
        """Export configuration in specified format"""
        with self.lock:
            data = self._serialize_config(self.config)
        
        if format.lower() == "json":
            return json.dumps(data, indent=2)
        elif format.lower() == "yaml":
            return yaml.dump(data, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_config(self, config_data: str, format: str = "yaml") -> bool:
        """Import configuration from string"""
        try:
            if format.lower() == "json":
                data = json.loads(config_data)
            elif format.lower() == "yaml":
                data = yaml.safe_load(config_data)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            with self.lock:
                self.config = self._deserialize_config(data)
                self.config.updated_at = datetime.now().isoformat()
            
            self._notify_watchers()
            return True
            
        except Exception as e:
            logger.error(f"Failed to import predictive monitoring configuration: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        with self.lock:
            return {
                'service_name': self.config.service_name,
                'environment': self.config.environment,
                'version': self.config.version,
                'algorithms_count': len(self.config.algorithms),
                'enabled_algorithms_count': len(self.get_enabled_algorithms()),
                'metrics_count': len(self.config.metrics),
                'enabled_metrics_count': len(self.get_enabled_metrics()),
                'environments_count': len(self.config.environments),
                'created_at': self.config.created_at,
                'updated_at': self.config.updated_at
            }
    
    def get_prediction_settings(self, metric_name: str) -> Dict[str, Any]:
        """Get prediction settings for a specific metric"""
        metric_config = self.get_metric_config(metric_name)
        if not metric_config:
            return {}
        
        return {
            'window_size': metric_config.window_size,
            'prediction_horizon': metric_config.prediction_horizon,
            'min_data_points': metric_config.min_data_points,
            'algorithms': metric_config.algorithms,
            'alert_threshold': metric_config.alert_threshold,
            'critical_threshold': metric_config.critical_threshold,
            'confidence_threshold': metric_config.confidence_threshold,
            'cooldown_period': metric_config.cooldown_period
        }
    
    def update_prediction_settings(self, metric_name: str, settings: Dict[str, Any]):
        """Update prediction settings for a specific metric"""
        metric_config = self.get_metric_config(metric_name)
        if not metric_config:
            logger.error(f"Metric {metric_name} not found")
            return
        
        # Update settings
        for key, value in settings.items():
            if hasattr(metric_config, key):
                setattr(metric_config, key, value)
        
        self.set_metric_config(metric_name, metric_config)


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get global predictive monitoring configuration manager instance"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    
    return _config_manager


def get_algorithm_config(algorithm_name: str, config_path: Optional[str] = None) -> Optional[AlgorithmConfig]:
    """Get algorithm configuration"""
    manager = get_config_manager(config_path)
    return manager.get_algorithm_config(algorithm_name)


def get_metric_config(metric_name: str, config_path: Optional[str] = None) -> Optional[MetricConfig]:
    """Get metric configuration"""
    manager = get_config_manager(config_path)
    return manager.get_metric_config(metric_name)


def get_environment_config(env_name: str, config_path: Optional[str] = None) -> Optional[EnvironmentConfig]:
    """Get environment configuration"""
    manager = get_config_manager(config_path)
    return manager.get_environment_config(env_name)


def add_metric(metric_config: MetricConfig, config_path: Optional[str] = None):
    """Add new metric configuration"""
    manager = get_config_manager(config_path)
    manager.add_metric(metric_config)


def add_algorithm(algorithm_config: AlgorithmConfig, config_path: Optional[str] = None):
    """Add new algorithm configuration"""
    manager = get_config_manager(config_path)
    manager.add_algorithm(algorithm_config)


def validate_configuration(config_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Validate configuration"""
    manager = get_config_manager(config_path)
    return manager.validate_config()


def export_configuration(format: str = "yaml", config_path: Optional[str] = None) -> str:
    """Export configuration"""
    manager = get_config_manager(config_path)
    return manager.export_config(format)


def get_prediction_settings(metric_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """Get prediction settings for a specific metric"""
    manager = get_config_manager(config_path)
    return manager.get_prediction_settings(metric_name)


def update_prediction_settings(metric_name: str, settings: Dict[str, Any], config_path: Optional[str] = None):
    """Update prediction settings for a specific metric"""
    manager = get_config_manager(config_path)
    manager.update_prediction_settings(metric_name, settings) 