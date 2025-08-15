"""
OpenTelemetry Configuration for Omni Keywords Finder
Tracing ID: FINE_TUNING_IMPLEMENTATION_20250127_001
Created: 2025-01-27
Version: 1.0

This module provides comprehensive OpenTelemetry configuration for distributed tracing,
custom metrics, and integration with Jaeger/Zipkin for observability.
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    OTLPSpanExporter
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    OTLPMetricExporter,
    PeriodicExportingMetricReader
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Custom imports
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.metrics import Counter, Histogram, UpDownCounter

logger = logging.getLogger(__name__)

class OpenTelemetryConfig:
    """
    Comprehensive OpenTelemetry configuration for the Omni Keywords Finder system.
    
    Provides:
    - Distributed tracing with correlation IDs
    - Custom metrics for APIs and business operations
    - Integration with Jaeger/Zipkin
    - Automatic instrumentation for Flask, SQLAlchemy, Redis
    - Sampling strategies for different environments
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.service_name = "omni-keywords-finder"
        self.service_version = os.getenv("APP_VERSION", "1.0.0")
        
        # Initialize providers
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        
        # Custom metrics
        self.api_request_counter: Optional[Counter] = None
        self.api_duration_histogram: Optional[Histogram] = None
        self.business_operation_counter: Optional[Counter] = None
        self.cache_hit_counter: Optional[Counter] = None
        self.cache_miss_counter: Optional[Counter] = None
        self.active_connections_counter: Optional[UpDownCounter] = None
        
        # Configuration
        self.sampling_rate = self._get_sampling_rate()
        self.exporters = self._configure_exporters()
        
    def _get_sampling_rate(self) -> float:
        """Get sampling rate based on environment."""
        rates = {
            "development": 1.0,  # 100% sampling for development
            "staging": 0.5,      # 50% sampling for staging
            "production": 0.1    # 10% sampling for production
        }
        return rates.get(self.environment, 0.1)
    
    def _configure_exporters(self) -> Dict[str, Any]:
        """Configure exporters based on environment."""
        exporters = {
            "console": ConsoleSpanExporter(),
            "console_metrics": ConsoleMetricExporter()
        }
        
        # Add OTLP exporters if configured
        otlp_endpoint = os.getenv("OTLP_ENDPOINT")
        if otlp_endpoint:
            exporters["otlp"] = OTLPSpanExporter(endpoint=otlp_endpoint)
            exporters["otlp_metrics"] = OTLPMetricExporter(endpoint=otlp_endpoint)
        
        # Add Jaeger exporter if configured
        jaeger_endpoint = os.getenv("JAEGER_ENDPOINT")
        if jaeger_endpoint:
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            exporters["jaeger"] = JaegerExporter(
                agent_host_name=jaeger_endpoint.split(":")[0],
                agent_port=int(jaeger_endpoint.split(":")[1])
            )
        
        return exporters
    
    def setup_tracing(self) -> None:
        """Setup distributed tracing with correlation IDs."""
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": self.service_version,
                "service.environment": self.environment,
                "deployment.environment": self.environment
            })
            
            # Create tracer provider
            self.tracer_provider = TracerProvider(
                resource=resource,
                sampler=self._create_sampler()
            )
            
            # Add span processors
            for name, exporter in self.exporters.items():
                if "jaeger" in name or "otlp" in name or "console" in name:
                    self.tracer_provider.add_span_processor(
                        BatchSpanProcessor(exporter)
                    )
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            # Create tracer
            self.tracer = trace.get_tracer(__name__)
            
            logger.info(f"OpenTelemetry tracing configured for {self.environment}")
            
        except Exception as e:
            logger.error(f"Failed to setup tracing: {e}")
            raise
    
    def setup_metrics(self) -> None:
        """Setup custom metrics for APIs and business operations."""
        try:
            # Create meter provider
            metric_readers = []
            
            # Add periodic metric reader for OTLP
            if "otlp_metrics" in self.exporters:
                metric_readers.append(
                    PeriodicExportingMetricReader(
                        self.exporters["otlp_metrics"],
                        export_interval_millis=5000
                    )
                )
            
            # Add console metric reader
            metric_readers.append(
                PeriodicExportingMetricReader(
                    self.exporters["console_metrics"],
                    export_interval_millis=10000
                )
            )
            
            self.meter_provider = MeterProvider(metric_readers=metric_readers)
            metrics.set_meter_provider(self.meter_provider)
            
            # Create meter
            self.meter = metrics.get_meter(__name__)
            
            # Create custom metrics
            self._create_custom_metrics()
            
            logger.info("OpenTelemetry metrics configured")
            
        except Exception as e:
            logger.error(f"Failed to setup metrics: {e}")
            raise
    
    def _create_custom_metrics(self) -> None:
        """Create custom metrics for monitoring."""
        # API request counter
        self.api_request_counter = self.meter.create_counter(
            name="api_requests_total",
            description="Total number of API requests",
            unit="1"
        )
        
        # API duration histogram
        self.api_duration_histogram = self.meter.create_histogram(
            name="api_request_duration_seconds",
            description="API request duration in seconds",
            unit="string_data"
        )
        
        # Business operation counter
        self.business_operation_counter = self.meter.create_counter(
            name="business_operations_total",
            description="Total number of business operations",
            unit="1"
        )
        
        # Cache metrics
        self.cache_hit_counter = self.meter.create_counter(
            name="cache_hits_total",
            description="Total number of cache hits",
            unit="1"
        )
        
        self.cache_miss_counter = self.meter.create_counter(
            name="cache_misses_total",
            description="Total number of cache misses",
            unit="1"
        )
        
        # Active connections counter
        self.active_connections_counter = self.meter.create_up_down_counter(
            name="active_connections",
            description="Number of active connections",
            unit="1"
        )
    
    def _create_sampler(self):
        """Create sampling strategy based on environment."""
        from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
        
        return TraceIdRatioBased(self.sampling_rate)
    
    def instrument_flask(self, app) -> None:
        """Instrument Flask application with OpenTelemetry."""
        try:
            FlaskInstrumentor().instrument_app(app)
            logger.info("Flask application instrumented")
        except Exception as e:
            logger.error(f"Failed to instrument Flask: {e}")
    
    def instrument_sqlalchemy(self, engine) -> None:
        """Instrument SQLAlchemy with OpenTelemetry."""
        try:
            SQLAlchemyInstrumentor().instrument(engine=engine)
            logger.info("SQLAlchemy instrumented")
        except Exception as e:
            logger.error(f"Failed to instrument SQLAlchemy: {e}")
    
    def instrument_redis(self) -> None:
        """Instrument Redis with OpenTelemetry."""
        try:
            RedisInstrumentor().instrument()
            logger.info("Redis instrumented")
        except Exception as e:
            logger.error(f"Failed to instrument Redis: {e}")
    
    def instrument_logging(self) -> None:
        """Instrument logging with OpenTelemetry."""
        try:
            LoggingInstrumentor().instrument(
                set_logging_format=True,
                log_level=logging.INFO
            )
            logger.info("Logging instrumented")
        except Exception as e:
            logger.error(f"Failed to instrument logging: {e}")
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: Dict[str, Any] = None):
        """
        Context manager for tracing operations with correlation IDs.
        
        Args:
            operation_name: Name of the operation being traced
            attributes: Additional attributes to add to the span
        """
        span = self.tracer.start_span(
            operation_name,
            kind=SpanKind.INTERNAL,
            attributes=attributes or {}
        )
        
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
        finally:
            span.end()
    
    def record_api_request(self, endpoint: str, method: str, status_code: int, duration: float) -> None:
        """Record API request metrics."""
        if self.api_request_counter:
            self.api_request_counter.add(1, {
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code)
            })
        
        if self.api_duration_histogram:
            self.api_duration_histogram.record(duration, {
                "endpoint": endpoint,
                "method": method
            })
    
    def record_business_operation(self, operation: str, status: str) -> None:
        """Record business operation metrics."""
        if self.business_operation_counter:
            self.business_operation_counter.add(1, {
                "operation": operation,
                "status": status
            })
    
    def record_cache_operation(self, operation: str, hit: bool) -> None:
        """Record cache operation metrics."""
        if hit and self.cache_hit_counter:
            self.cache_hit_counter.add(1, {"operation": operation})
        elif not hit and self.cache_miss_counter:
            self.cache_miss_counter.add(1, {"operation": operation})
    
    def update_active_connections(self, count: int) -> None:
        """Update active connections counter."""
        if self.active_connections_counter:
            self.active_connections_counter.add(count)
    
    def shutdown(self) -> None:
        """Shutdown OpenTelemetry gracefully."""
        try:
            if self.tracer_provider:
                self.tracer_provider.shutdown()
            if self.meter_provider:
                self.meter_provider.shutdown()
            logger.info("OpenTelemetry shutdown completed")
        except Exception as e:
            logger.error(f"Failed to shutdown OpenTelemetry: {e}")


# Global instance
_ot_config: Optional[OpenTelemetryConfig] = None

def get_ot_config(environment: str = None) -> OpenTelemetryConfig:
    """Get or create OpenTelemetry configuration instance."""
    global _ot_config
    
    if _ot_config is None:
        env = environment or os.getenv("ENVIRONMENT", "development")
        _ot_config = OpenTelemetryConfig(env)
    
    return _ot_config

def initialize_observability(environment: str = None) -> OpenTelemetryConfig:
    """Initialize complete observability setup."""
    config = get_ot_config(environment)
    
    # Setup tracing and metrics
    config.setup_tracing()
    config.setup_metrics()
    
    return config

def instrument_application(app, engine=None):
    """Instrument application with OpenTelemetry."""
    config = get_ot_config()
    
    # Instrument Flask
    config.instrument_flask(app)
    
    # Instrument SQLAlchemy if engine provided
    if engine:
        config.instrument_sqlalchemy(engine)
    
    # Instrument Redis
    config.instrument_redis()
    
    # Instrument logging
    config.instrument_logging()
    
    return config 