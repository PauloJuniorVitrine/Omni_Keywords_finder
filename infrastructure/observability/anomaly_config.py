"""
⚙️ Advanced Anomaly Detection Configuration System
📅 Generated: 2025-01-27
🎯 Purpose: Comprehensive configuration management for anomaly detection
📋 Tracing ID: ANOMALY_CONFIG_001_20250127
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


class AlgorithmType(Enum):
    """Supported anomaly detection algorithms"""
    STATISTICAL = "statistical"
    ZSCORE = "zscore"
    IQR = "iqr"
    MAD = "mad"
    EXPONENTIAL = "exponential"
    SEASONAL = "seasonal"
    TREND = "trend"
    PATTERN = "pattern"
    THRESHOLD = "threshold"
    ENSEMBLE = "ensemble"
    MACHINE_LEARNING = "machine_learning"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    CUSTOM = "custom"


@dataclass
class AlgorithmConfig:
    """Configuration for individual algorithms"""
    name: str
    algorithm_type: AlgorithmType
    enabled: bool = True
    weight: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    custom_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricConfig:
    """Configuration for individual metrics"""
    name: str
    metric_type: MetricType
    description: str = ""
    unit: str = ""
    enabled: bool = True
    algorithms: List[str] = field(default_factory=list)
    window_size: int = 100
    min_data_points: int = 10
    alert_threshold: float = 2.0
    critical_threshold: float = 3.0
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
class AnomalyDetectionConfig:
    """Main configuration for anomaly detection system"""
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
    Advanced configuration manager for anomaly detection
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/anomaly_detection.yaml"
        self.config = self._load_default_config()
        self.lock = threading.RLock()
        self.watchers: List[Callable] = []
        self.last_modified = 0.0
        
        # Load configuration from file if it exists
        if os.path.exists(self.config_path):
            self.load_config()
    
    def _load_default_config(self) -> AnomalyDetectionConfig:
        """Load default configuration"""
        return AnomalyDetectionConfig(
            algorithms={
                "statistical": AlgorithmConfig(
                    name="statistical",
                    algorithm_type=AlgorithmType.STATISTICAL,
                    parameters={
                        "window_size": 100,
                        "threshold_multiplier": 2.0,
                        "confidence_level": 0.95
                    }
                ),
                "zscore": AlgorithmConfig(
                    name="zscore",
                    algorithm_type=AlgorithmType.ZSCORE,
                    parameters={
                        "window_size": 100,
                        "threshold": 2.0
                    }
                ),
                "iqr": AlgorithmConfig(
                    name="iqr",
                    algorithm_type=AlgorithmType.IQR,
                    parameters={
                        "window_size": 100,
                        "multiplier": 1.5
                    }
                ),
                "exponential": AlgorithmConfig(
                    name="exponential",
                    algorithm_type=AlgorithmType.EXPONENTIAL,
                    parameters={
                        "alpha": 0.1,
                        "threshold": 2.0
                    }
                ),
                "seasonal": AlgorithmConfig(
                    name="seasonal",
                    algorithm_type=AlgorithmType.SEASONAL,
                    parameters={
                        "seasonal_period": 24,
                        "threshold": 2.0
                    }
                ),
                "trend": AlgorithmConfig(
                    name="trend",
                    algorithm_type=AlgorithmType.TREND,
                    parameters={
                        "window_size": 50,
                        "threshold": 2.0
                    }
                ),
                "pattern": AlgorithmConfig(
                    name="pattern",
                    algorithm_type=AlgorithmType.PATTERN,
                    parameters={
                        "pattern_length": 10,
                        "similarity_threshold": 0.8
                    }
                ),
                "threshold": AlgorithmConfig(
                    name="threshold",
                    algorithm_type=AlgorithmType.THRESHOLD,
                    parameters={
                        "upper_threshold": None,
                        "lower_threshold": None
                    }
                ),
                "ensemble": AlgorithmConfig(
                    name="ensemble",
                    algorithm_type=AlgorithmType.ENSEMBLE,
                    parameters={
                        "algorithms": ["statistical", "zscore", "iqr"],
                        "voting_threshold": 0.5
                    }
                )
            },
            metrics={
                "cpu_usage": MetricConfig(
                    name="cpu_usage",
                    metric_type=MetricType.GAUGE,
                    description="CPU usage percentage",
                    unit="%",
                    algorithms=["statistical", "zscore", "threshold"],
                    alert_threshold=80.0,
                    critical_threshold=95.0
                ),
                "memory_usage": MetricConfig(
                    name="memory_usage",
                    metric_type=MetricType.GAUGE,
                    description="Memory usage percentage",
                    unit="%",
                    algorithms=["statistical", "zscore", "threshold"],
                    alert_threshold=85.0,
                    critical_threshold=95.0
                ),
                "response_time": MetricConfig(
                    name="response_time",
                    metric_type=MetricType.HISTOGRAM,
                    description="API response time",
                    unit="ms",
                    algorithms=["statistical", "zscore", "exponential"],
                    alert_threshold=1000.0,
                    critical_threshold=5000.0
                ),
                "error_rate": MetricConfig(
                    name="error_rate",
                    metric_type=MetricType.COUNTER,
                    description="Error rate percentage",
                    unit="%",
                    algorithms=["statistical", "threshold"],
                    alert_threshold=5.0,
                    critical_threshold=10.0
                ),
                "throughput": MetricConfig(
                    name="throughput",
                    metric_type=MetricType.COUNTER,
                    description="Requests per second",
                    unit="req/s",
                    algorithms=["statistical", "trend", "seasonal"],
                    alert_threshold=100.0,
                    critical_threshold=50.0
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
                "max_false_positive_rate": 0.05,
                "min_data_points": 10,
                "max_window_size": 1000
            },
            alerting={
                "enabled": True,
                "cooldown_period": 300,
                "max_alerts_per_hour": 10,
                "group_alerts": True,
                "suppression_rules": {}
            },
            performance={
                "max_concurrent_detections": 100,
                "cache_size": 1000,
                "cleanup_interval": 3600,
                "max_history_size": 10000
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
            
            logger.info(f"Configuration loaded from {path}")
            self._notify_watchers()
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {path}: {e}")
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
            
            logger.info(f"Configuration saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {path}: {e}")
            return False
    
    def _serialize_config(self, config: AnomalyDetectionConfig) -> Dict[str, Any]:
        """Serialize configuration to dictionary"""
        data = asdict(config)
        
        # Convert enums to strings
        for algorithm in data['algorithms'].values():
            algorithm['algorithm_type'] = algorithm['algorithm_type'].value
        
        for metric in data['metrics'].values():
            metric['metric_type'] = metric['metric_type'].value
        
        return data
    
    def _deserialize_config(self, data: Dict[str, Any]) -> AnomalyDetectionConfig:
        """Deserialize configuration from dictionary"""
        # Convert string enums back to enum objects
        for algorithm_data in data.get('algorithms', {}).values():
            if 'algorithm_type' in algorithm_data:
                algorithm_data['algorithm_type'] = AlgorithmType(algorithm_data['algorithm_type'])
        
        for metric_data in data.get('metrics', {}).values():
            if 'metric_type' in metric_data:
                metric_data['metric_type'] = MetricType(metric_data['metric_type'])
        
        # Create config object
        return AnomalyDetectionConfig(**data)
    
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
            logger.error(f"Failed to import configuration: {e}")
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


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get global configuration manager instance"""
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