"""
🔍 Trace Configuration System
📅 Generated: 2025-01-27
🎯 Purpose: Configuration management for distributed tracing
📋 Tracing ID: TRACE_CONFIG_004_20250127
"""

import logging
import os
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path

from .advanced_tracing import TracingConfig, TracingBackend, SpanType
from .trace_context import ContextType

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class SamplingStrategy(Enum):
    """Sampling strategies for traces"""
    ALWAYS = "always"
    PROBABILISTIC = "probabilistic"
    RATE_LIMITING = "rate_limiting"
    ADAPTIVE = "adaptive"


@dataclass
class BackendConfig:
    """Configuration for tracing backend"""
    type: TracingBackend
    endpoint: str
    host: str = "localhost"
    port: int = 14268
    timeout: int = 30
    retries: int = 3
    batch_size: int = 100
    batch_timeout: int = 5
    credentials: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    ssl_verify: bool = True
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None


@dataclass
class SamplingConfig:
    """Configuration for trace sampling"""
    strategy: SamplingStrategy = SamplingStrategy.ALWAYS
    rate: float = 1.0
    max_traces_per_second: int = 1000
    adaptive_threshold: float = 0.1
    adaptive_window: int = 60
    rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FilterConfig:
    """Configuration for trace filtering"""
    include_paths: List[str] = field(default_factory=list)
    exclude_paths: List[str] = field(default_factory=list)
    include_services: List[str] = field(default_factory=list)
    exclude_services: List[str] = field(default_factory=list)
    include_methods: List[str] = field(default_factory=list)
    exclude_methods: List[str] = field(default_factory=list)
    min_duration: float = 0.0
    max_duration: float = float('inf')
    error_only: bool = False


@dataclass
class MetricsConfig:
    """Configuration for trace metrics"""
    enabled: bool = True
    prometheus_endpoint: str = "/metrics"
    custom_metrics: List[Dict[str, Any]] = field(default_factory=list)
    histogram_buckets: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
    enable_span_metrics: bool = True
    enable_error_metrics: bool = True
    enable_duration_metrics: bool = True


@dataclass
class LoggingConfig:
    """Configuration for trace logging"""
    enabled: bool = True
    level: str = "INFO"
    format: str = "json"
    include_trace_id: bool = True
    include_span_id: bool = True
    include_context: bool = True
    log_errors: bool = True
    log_slow_queries: bool = True
    slow_query_threshold: float = 1.0


@dataclass
class AdvancedTraceConfig:
    """Advanced configuration for distributed tracing"""
    # Basic configuration
    service_name: str = "omni-keywords-finder"
    service_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    
    # Backend configuration
    backend: BackendConfig = field(default_factory=lambda: BackendConfig(
        type=TracingBackend.JAEGER,
        endpoint="http://localhost:14268/api/traces"
    ))
    
    # Sampling configuration
    sampling: SamplingConfig = field(default_factory=SamplingConfig)
    
    # Filtering configuration
    filtering: FilterConfig = field(default_factory=FilterConfig)
    
    # Metrics configuration
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    
    # Logging configuration
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Advanced settings
    max_attributes: int = 32
    max_events: int = 128
    max_links: int = 32
    max_span_duration: float = 300.0
    enable_async_propagation: bool = True
    enable_context_propagation: bool = True
    enable_baggage: bool = False
    custom_attributes: Dict[str, str] = field(default_factory=dict)
    
    # Performance settings
    buffer_size: int = 1000
    flush_interval: int = 5
    max_queue_size: int = 10000
    worker_threads: int = 4
    
    # Security settings
    enable_encryption: bool = False
    encryption_key: Optional[str] = None
    enable_authentication: bool = False
    auth_token: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "service_name": self.service_name,
            "service_version": self.service_version,
            "environment": self.environment.value,
            "backend": {
                "type": self.backend.type.value,
                "endpoint": self.backend.endpoint,
                "host": self.backend.host,
                "port": self.backend.port,
                "timeout": self.backend.timeout,
                "retries": self.backend.retries,
                "batch_size": self.backend.batch_size,
                "batch_timeout": self.backend.batch_timeout,
                "credentials": self.backend.credentials,
                "headers": self.backend.headers,
                "ssl_verify": self.backend.ssl_verify,
                "ssl_cert": self.backend.ssl_cert,
                "ssl_key": self.backend.ssl_key
            },
            "sampling": {
                "strategy": self.sampling.strategy.value,
                "rate": self.sampling.rate,
                "max_traces_per_second": self.sampling.max_traces_per_second,
                "adaptive_threshold": self.sampling.adaptive_threshold,
                "adaptive_window": self.sampling.adaptive_window,
                "rules": self.sampling.rules
            },
            "filtering": {
                "include_paths": self.filtering.include_paths,
                "exclude_paths": self.filtering.exclude_paths,
                "include_services": self.filtering.include_services,
                "exclude_services": self.filtering.exclude_services,
                "include_methods": self.filtering.include_methods,
                "exclude_methods": self.filtering.exclude_methods,
                "min_duration": self.filtering.min_duration,
                "max_duration": self.filtering.max_duration,
                "error_only": self.filtering.error_only
            },
            "metrics": {
                "enabled": self.metrics.enabled,
                "prometheus_endpoint": self.metrics.prometheus_endpoint,
                "custom_metrics": self.metrics.custom_metrics,
                "histogram_buckets": self.metrics.histogram_buckets,
                "enable_span_metrics": self.metrics.enable_span_metrics,
                "enable_error_metrics": self.metrics.enable_error_metrics,
                "enable_duration_metrics": self.metrics.enable_duration_metrics
            },
            "logging": {
                "enabled": self.logging.enabled,
                "level": self.logging.level,
                "format": self.logging.format,
                "include_trace_id": self.logging.include_trace_id,
                "include_span_id": self.logging.include_span_id,
                "include_context": self.logging.include_context,
                "log_errors": self.logging.log_errors,
                "log_slow_queries": self.logging.log_slow_queries,
                "slow_query_threshold": self.logging.slow_query_threshold
            },
            "advanced": {
                "max_attributes": self.max_attributes,
                "max_events": self.max_events,
                "max_links": self.max_links,
                "max_span_duration": self.max_span_duration,
                "enable_async_propagation": self.enable_async_propagation,
                "enable_context_propagation": self.enable_context_propagation,
                "enable_baggage": self.enable_baggage,
                "custom_attributes": self.custom_attributes
            },
            "performance": {
                "buffer_size": self.buffer_size,
                "flush_interval": self.flush_interval,
                "max_queue_size": self.max_queue_size,
                "worker_threads": self.worker_threads
            },
            "security": {
                "enable_encryption": self.enable_encryption,
                "encryption_key": self.encryption_key,
                "enable_authentication": self.enable_authentication,
                "auth_token": self.auth_token
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedTraceConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Basic configuration
        config.service_name = data.get("service_name", config.service_name)
        config.service_version = data.get("service_version", config.service_version)
        config.environment = Environment(data.get("environment", config.environment.value))
        
        # Backend configuration
        backend_data = data.get("backend", {})
        config.backend = BackendConfig(
            type=TracingBackend(backend_data.get("type", config.backend.type.value)),
            endpoint=backend_data.get("endpoint", config.backend.endpoint),
            host=backend_data.get("host", config.backend.host),
            port=backend_data.get("port", config.backend.port),
            timeout=backend_data.get("timeout", config.backend.timeout),
            retries=backend_data.get("retries", config.backend.retries),
            batch_size=backend_data.get("batch_size", config.backend.batch_size),
            batch_timeout=backend_data.get("batch_timeout", config.backend.batch_timeout),
            credentials=backend_data.get("credentials"),
            headers=backend_data.get("headers"),
            ssl_verify=backend_data.get("ssl_verify", config.backend.ssl_verify),
            ssl_cert=backend_data.get("ssl_cert"),
            ssl_key=backend_data.get("ssl_key")
        )
        
        # Sampling configuration
        sampling_data = data.get("sampling", {})
        config.sampling = SamplingConfig(
            strategy=SamplingStrategy(sampling_data.get("strategy", config.sampling.strategy.value)),
            rate=sampling_data.get("rate", config.sampling.rate),
            max_traces_per_second=sampling_data.get("max_traces_per_second", config.sampling.max_traces_per_second),
            adaptive_threshold=sampling_data.get("adaptive_threshold", config.sampling.adaptive_threshold),
            adaptive_window=sampling_data.get("adaptive_window", config.sampling.adaptive_window),
            rules=sampling_data.get("rules", config.sampling.rules)
        )
        
        # Filtering configuration
        filtering_data = data.get("filtering", {})
        config.filtering = FilterConfig(
            include_paths=filtering_data.get("include_paths", config.filtering.include_paths),
            exclude_paths=filtering_data.get("exclude_paths", config.filtering.exclude_paths),
            include_services=filtering_data.get("include_services", config.filtering.include_services),
            exclude_services=filtering_data.get("exclude_services", config.filtering.exclude_services),
            include_methods=filtering_data.get("include_methods", config.filtering.include_methods),
            exclude_methods=filtering_data.get("exclude_methods", config.filtering.exclude_methods),
            min_duration=filtering_data.get("min_duration", config.filtering.min_duration),
            max_duration=filtering_data.get("max_duration", config.filtering.max_duration),
            error_only=filtering_data.get("error_only", config.filtering.error_only)
        )
        
        # Metrics configuration
        metrics_data = data.get("metrics", {})
        config.metrics = MetricsConfig(
            enabled=metrics_data.get("enabled", config.metrics.enabled),
            prometheus_endpoint=metrics_data.get("prometheus_endpoint", config.metrics.prometheus_endpoint),
            custom_metrics=metrics_data.get("custom_metrics", config.metrics.custom_metrics),
            histogram_buckets=metrics_data.get("histogram_buckets", config.metrics.histogram_buckets),
            enable_span_metrics=metrics_data.get("enable_span_metrics", config.metrics.enable_span_metrics),
            enable_error_metrics=metrics_data.get("enable_error_metrics", config.metrics.enable_error_metrics),
            enable_duration_metrics=metrics_data.get("enable_duration_metrics", config.metrics.enable_duration_metrics)
        )
        
        # Logging configuration
        logging_data = data.get("logging", {})
        config.logging = LoggingConfig(
            enabled=logging_data.get("enabled", config.logging.enabled),
            level=logging_data.get("level", config.logging.level),
            format=logging_data.get("format", config.logging.format),
            include_trace_id=logging_data.get("include_trace_id", config.logging.include_trace_id),
            include_span_id=logging_data.get("include_span_id", config.logging.include_span_id),
            include_context=logging_data.get("include_context", config.logging.include_context),
            log_errors=logging_data.get("log_errors", config.logging.log_errors),
            log_slow_queries=logging_data.get("log_slow_queries", config.logging.log_slow_queries),
            slow_query_threshold=logging_data.get("slow_query_threshold", config.logging.slow_query_threshold)
        )
        
        # Advanced settings
        advanced_data = data.get("advanced", {})
        config.max_attributes = advanced_data.get("max_attributes", config.max_attributes)
        config.max_events = advanced_data.get("max_events", config.max_events)
        config.max_links = advanced_data.get("max_links", config.max_links)
        config.max_span_duration = advanced_data.get("max_span_duration", config.max_span_duration)
        config.enable_async_propagation = advanced_data.get("enable_async_propagation", config.enable_async_propagation)
        config.enable_context_propagation = advanced_data.get("enable_context_propagation", config.enable_context_propagation)
        config.enable_baggage = advanced_data.get("enable_baggage", config.enable_baggage)
        config.custom_attributes = advanced_data.get("custom_attributes", config.custom_attributes)
        
        # Performance settings
        performance_data = data.get("performance", {})
        config.buffer_size = performance_data.get("buffer_size", config.buffer_size)
        config.flush_interval = performance_data.get("flush_interval", config.flush_interval)
        config.max_queue_size = performance_data.get("max_queue_size", config.max_queue_size)
        config.worker_threads = performance_data.get("worker_threads", config.worker_threads)
        
        # Security settings
        security_data = data.get("security", {})
        config.enable_encryption = security_data.get("enable_encryption", config.enable_encryption)
        config.encryption_key = security_data.get("encryption_key")
        config.enable_authentication = security_data.get("enable_authentication", config.enable_authentication)
        config.auth_token = security_data.get("auth_token")
        
        return config


class TraceConfigManager:
    """
    Configuration manager for distributed tracing
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> AdvancedTraceConfig:
        """Load configuration from file or environment"""
        # Try to load from file first
        if self.config_path and Path(self.config_path).exists():
            return self._load_from_file(self.config_path)
        
        # Try to load from environment
        return self._load_from_environment()
    
    def _load_from_file(self, config_path: str) -> AdvancedTraceConfig:
        """Load configuration from file"""
        try:
            file_path = Path(config_path)
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {file_path.suffix}")
            
            config = AdvancedTraceConfig.from_dict(data)
            logger.info(f"Configuration loaded from file: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration from file {config_path}: {e}")
            return self._load_from_environment()
    
    def _load_from_environment(self) -> AdvancedTraceConfig:
        """Load configuration from environment variables"""
        config = AdvancedTraceConfig()
        
        # Basic configuration
        config.service_name = os.getenv("TRACE_SERVICE_NAME", config.service_name)
        config.service_version = os.getenv("TRACE_SERVICE_VERSION", config.service_version)
        config.environment = Environment(os.getenv("TRACE_ENVIRONMENT", config.environment.value))
        
        # Backend configuration
        config.backend.type = TracingBackend(os.getenv("TRACE_BACKEND_TYPE", config.backend.type.value))
        config.backend.endpoint = os.getenv("TRACE_BACKEND_ENDPOINT", config.backend.endpoint)
        config.backend.host = os.getenv("TRACE_BACKEND_HOST", config.backend.host)
        config.backend.port = int(os.getenv("TRACE_BACKEND_PORT", str(config.backend.port)))
        config.backend.timeout = int(os.getenv("TRACE_BACKEND_TIMEOUT", str(config.backend.timeout)))
        config.backend.retries = int(os.getenv("TRACE_BACKEND_RETRIES", str(config.backend.retries)))
        config.backend.batch_size = int(os.getenv("TRACE_BACKEND_BATCH_SIZE", str(config.backend.batch_size)))
        config.backend.batch_timeout = int(os.getenv("TRACE_BACKEND_BATCH_TIMEOUT", str(config.backend.batch_timeout)))
        config.backend.ssl_verify = os.getenv("TRACE_BACKEND_SSL_VERIFY", "true").lower() == "true"
        
        # Sampling configuration
        config.sampling.strategy = SamplingStrategy(os.getenv("TRACE_SAMPLING_STRATEGY", config.sampling.strategy.value))
        config.sampling.rate = float(os.getenv("TRACE_SAMPLING_RATE", str(config.sampling.rate)))
        config.sampling.max_traces_per_second = int(os.getenv("TRACE_SAMPLING_MAX_TRACES_PER_SECOND", str(config.sampling.max_traces_per_second)))
        
        # Metrics configuration
        config.metrics.enabled = os.getenv("TRACE_METRICS_ENABLED", "true").lower() == "true"
        config.metrics.prometheus_endpoint = os.getenv("TRACE_METRICS_ENDPOINT", config.metrics.prometheus_endpoint)
        
        # Logging configuration
        config.logging.enabled = os.getenv("TRACE_LOGGING_ENABLED", "true").lower() == "true"
        config.logging.level = os.getenv("TRACE_LOGGING_LEVEL", config.logging.level)
        config.logging.format = os.getenv("TRACE_LOGGING_FORMAT", config.logging.format)
        
        # Advanced settings
        config.max_attributes = int(os.getenv("TRACE_MAX_ATTRIBUTES", str(config.max_attributes)))
        config.max_events = int(os.getenv("TRACE_MAX_EVENTS", str(config.max_events)))
        config.max_links = int(os.getenv("TRACE_MAX_LINKS", str(config.max_links)))
        config.enable_async_propagation = os.getenv("TRACE_ENABLE_ASYNC_PROPAGATION", "true").lower() == "true"
        config.enable_context_propagation = os.getenv("TRACE_ENABLE_CONTEXT_PROPAGATION", "true").lower() == "true"
        
        # Performance settings
        config.buffer_size = int(os.getenv("TRACE_BUFFER_SIZE", str(config.buffer_size)))
        config.flush_interval = int(os.getenv("TRACE_FLUSH_INTERVAL", str(config.flush_interval)))
        config.max_queue_size = int(os.getenv("TRACE_MAX_QUEUE_SIZE", str(config.max_queue_size)))
        config.worker_threads = int(os.getenv("TRACE_WORKER_THREADS", str(config.worker_threads)))
        
        # Security settings
        config.enable_encryption = os.getenv("TRACE_ENABLE_ENCRYPTION", "false").lower() == "true"
        config.encryption_key = os.getenv("TRACE_ENCRYPTION_KEY")
        config.enable_authentication = os.getenv("TRACE_ENABLE_AUTHENTICATION", "false").lower() == "true"
        config.auth_token = os.getenv("TRACE_AUTH_TOKEN")
        
        logger.info("Configuration loaded from environment variables")
        return config
    
    def get_tracing_config(self) -> TracingConfig:
        """Convert to OpenTelemetry TracingConfig"""
        return TracingConfig(
            service_name=self.config.service_name,
            service_version=self.config.service_version,
            environment=self.config.environment.value,
            backend=self.config.backend.type,
            endpoint=self.config.backend.endpoint,
            sample_rate=self.config.sampling.rate,
            max_attributes=self.config.max_attributes,
            max_events=self.config.max_events,
            max_links=self.config.max_links,
            enable_metrics=self.config.metrics.enabled,
            enable_logs=self.config.logging.enabled,
            custom_attributes=self.config.custom_attributes
        )
    
    def save_config(self, config_path: Optional[str] = None):
        """Save configuration to file"""
        save_path = config_path or self.config_path
        if not save_path:
            raise ValueError("No config path specified")
        
        try:
            file_path = Path(save_path)
            data = self.config.to_dict()
            
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {file_path.suffix}")
            
            logger.info(f"Configuration saved to file: {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to file {save_path}: {e}")
            raise
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        try:
            # Convert current config to dict
            current_data = self.config.to_dict()
            
            # Apply updates recursively
            self._update_dict_recursive(current_data, updates)
            
            # Create new config from updated data
            self.config = AdvancedTraceConfig.from_dict(current_data)
            
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise
    
    def _update_dict_recursive(self, target: Dict[str, Any], updates: Dict[str, Any]):
        """Recursively update dictionary"""
        for key, value in updates.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict_recursive(target[key], value)
            else:
                target[key] = value
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate basic configuration
        if not self.config.service_name:
            errors.append("Service name is required")
        
        if not self.config.service_version:
            errors.append("Service version is required")
        
        # Validate backend configuration
        if not self.config.backend.endpoint:
            errors.append("Backend endpoint is required")
        
        if self.config.backend.port < 1 or self.config.backend.port > 65535:
            errors.append("Backend port must be between 1 and 65535")
        
        # Validate sampling configuration
        if self.config.sampling.rate < 0.0 or self.config.sampling.rate > 1.0:
            errors.append("Sampling rate must be between 0.0 and 1.0")
        
        if self.config.sampling.max_traces_per_second < 1:
            errors.append("Max traces per second must be at least 1")
        
        # Validate performance settings
        if self.config.buffer_size < 1:
            errors.append("Buffer size must be at least 1")
        
        if self.config.flush_interval < 1:
            errors.append("Flush interval must be at least 1")
        
        if self.config.max_queue_size < 1:
            errors.append("Max queue size must be at least 1")
        
        if self.config.worker_threads < 1:
            errors.append("Worker threads must be at least 1")
        
        return errors


# Global configuration manager instance
_config_manager: Optional[TraceConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> TraceConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = TraceConfigManager(config_path)
    return _config_manager


def get_config() -> AdvancedTraceConfig:
    """Get current configuration"""
    return get_config_manager().config


def get_tracing_config() -> TracingConfig:
    """Get OpenTelemetry tracing configuration"""
    return get_config_manager().get_tracing_config()


def update_config(updates: Dict[str, Any]):
    """Update global configuration"""
    get_config_manager().update_config(updates)


def save_config(config_path: Optional[str] = None):
    """Save current configuration to file"""
    get_config_manager().save_config(config_path)


def validate_config() -> List[str]:
    """Validate current configuration"""
    return get_config_manager().validate_config()


# Predefined configurations for common environments
def get_development_config() -> AdvancedTraceConfig:
    """Get development environment configuration"""
    config = AdvancedTraceConfig()
    config.environment = Environment.DEVELOPMENT
    config.backend.type = TracingBackend.CONSOLE
    config.sampling.rate = 1.0
    config.logging.level = "DEBUG"
    config.metrics.enabled = False
    return config


def get_staging_config() -> AdvancedTraceConfig:
    """Get staging environment configuration"""
    config = AdvancedTraceConfig()
    config.environment = Environment.STAGING
    config.backend.type = TracingBackend.JAEGER
    config.sampling.rate = 0.5
    config.logging.level = "INFO"
    config.metrics.enabled = True
    return config


def get_production_config() -> AdvancedTraceConfig:
    """Get production environment configuration"""
    config = AdvancedTraceConfig()
    config.environment = Environment.PRODUCTION
    config.backend.type = TracingBackend.JAEGER
    config.sampling.rate = 0.1
    config.logging.level = "WARNING"
    config.metrics.enabled = True
    config.enable_encryption = True
    config.enable_authentication = True
    return config


def get_testing_config() -> AdvancedTraceConfig:
    """Get testing environment configuration"""
    config = AdvancedTraceConfig()
    config.environment = Environment.TESTING
    config.backend.type = TracingBackend.CONSOLE
    config.sampling.rate = 1.0
    config.logging.level = "ERROR"
    config.metrics.enabled = False
    config.enable_async_propagation = False
    config.enable_context_propagation = False
    return config 