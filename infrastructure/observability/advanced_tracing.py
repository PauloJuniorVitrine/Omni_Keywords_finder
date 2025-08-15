"""
🔍 Advanced Distributed Tracing System
📅 Generated: 2025-01-27
🎯 Purpose: Distributed tracing with OpenTelemetry integration
📋 Tracing ID: ADVANCED_TRACING_001_20250127
"""

import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
from functools import wraps

# OpenTelemetry imports
try:
    from opentelemetry import trace, context
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.span import Span
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        OTLPSpanExporter
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.zipkin.json import ZipkinExporter
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logging.warning("OpenTelemetry not available. Using fallback tracing.")

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus not available. Metrics disabled.")

logger = logging.getLogger(__name__)


class TracingBackend(Enum):
    """Supported tracing backends"""
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    OTLP = "otlp"
    CONSOLE = "console"
    CUSTOM = "custom"


class SpanType(Enum):
    """Types of spans for categorization"""
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    EXTERNAL_API = "external_api"
    BUSINESS_LOGIC = "business_logic"
    BACKGROUND_TASK = "background_task"
    CACHE_OPERATION = "cache_operation"
    FILE_OPERATION = "file_operation"
    MESSAGE_QUEUE = "message_queue"


@dataclass
class TracingConfig:
    """Configuration for distributed tracing"""
    service_name: str = "omni-keywords-finder"
    service_version: str = "1.0.0"
    environment: str = "production"
    backend: TracingBackend = TracingBackend.JAEGER
    endpoint: str = "http://localhost:14268/api/traces"
    sample_rate: float = 1.0
    max_attributes: int = 32
    max_events: int = 128
    max_links: int = 32
    enable_metrics: bool = True
    enable_logs: bool = True
    custom_attributes: Dict[str, str] = field(default_factory=dict)
    excluded_paths: List[str] = field(default_factory=list)
    included_paths: List[str] = field(default_factory=list)


@dataclass
class SpanContext:
    """Context information for spans"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    span_type: SpanType = SpanType.BUSINESS_LOGIC
    attributes: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: StatusCode = StatusCode.OK
    error_message: Optional[str] = None


class AdvancedTracing:
    """
    Advanced distributed tracing system with OpenTelemetry integration
    """
    
    def __init__(self, config: TracingConfig):
        self.config = config
        self.tracer_provider = None
        self.tracer = None
        self.metrics = {}
        self._setup_tracing()
        self._setup_metrics()
        
    def _setup_tracing(self):
        """Initialize OpenTelemetry tracing"""
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available. Using fallback tracing.")
            return
            
        try:
            # Create resource
            resource = Resource.create({
                "service.name": self.config.service_name,
                "service.version": self.config.service_version,
                "service.environment": self.config.environment,
                **self.config.custom_attributes
            })
            
            # Create tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            
            # Configure exporter based on backend
            if self.config.backend == TracingBackend.JAEGER:
                exporter = JaegerExporter(
                    agent_host_name="localhost",
                    agent_port=6831,
                    endpoint=self.config.endpoint
                )
            elif self.config.backend == TracingBackend.ZIPKIN:
                exporter = ZipkinExporter(
                    endpoint=self.config.endpoint
                )
            elif self.config.backend == TracingBackend.OTLP:
                exporter = OTLPSpanExporter(
                    endpoint=self.config.endpoint
                )
            else:  # CONSOLE
                exporter = ConsoleSpanExporter()
                
            # Add span processor
            span_processor = BatchSpanProcessor(exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            # Create tracer
            self.tracer = trace.get_tracer(
                self.config.service_name,
                self.config.service_version
            )
            
            logger.info(f"Tracing initialized with backend: {self.config.backend.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            self.tracer = None
    
    def _setup_metrics(self):
        """Initialize Prometheus metrics for tracing"""
        if not PROMETHEUS_AVAILABLE or not self.config.enable_metrics:
            return
            
        try:
            self.metrics = {
                "spans_total": Counter(
                    "tracing_spans_total",
                    "Total number of spans created",
                    ["service", "span_type", "status"]
                ),
                "span_duration": Histogram(
                    "tracing_span_duration_seconds",
                    "Span duration in seconds",
                    ["service", "span_type"],
                    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
                ),
                "active_spans": Gauge(
                    "tracing_active_spans",
                    "Number of active spans",
                    ["service", "span_type"]
                ),
                "trace_errors": Counter(
                    "tracing_errors_total",
                    "Total number of tracing errors",
                    ["service", "error_type"]
                )
            }
            logger.info("Tracing metrics initialized")
        except Exception as e:
            logger.error(f"Failed to initialize tracing metrics: {e}")
    
    def start_span(
        self,
        name: str,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        attributes: Optional[Dict[str, Any]] = None,
        parent_span: Optional[Span] = None
    ) -> Span:
        """
        Start a new span
        
        Args:
            name: Span name
            span_type: Type of span for categorization
            attributes: Additional attributes
            parent_span: Parent span for context
            
        Returns:
            OpenTelemetry span
        """
        if not self.tracer:
            return self._create_fallback_span(name, span_type, attributes)
            
        try:
            # Create span context
            span_context = None
            if parent_span:
                span_context = trace.set_span_in_context(parent_span)
            
            # Start span
            span = self.tracer.start_span(
                name=name,
                context=span_context
            )
            
            # Add attributes
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            # Add span type attribute
            span.set_attribute("span.type", span_type.value)
            span.set_attribute("service.name", self.config.service_name)
            span.set_attribute("service.version", self.config.service_version)
            
            # Update metrics
            self._update_metrics("spans_total", {"span_type": span_type.value, "status": "started"})
            self._update_metrics("active_spans", {"span_type": span_type.value}, increment=True)
            
            return span
            
        except Exception as e:
            logger.error(f"Failed to start span: {e}")
            self._update_metrics("trace_errors", {"error_type": "span_start"})
            return self._create_fallback_span(name, span_type, attributes)
    
    def _create_fallback_span(self, name: str, span_type: SpanType, attributes: Optional[Dict[str, Any]]) -> 'FallbackSpan':
        """Create fallback span when OpenTelemetry is not available"""
        return FallbackSpan(name, span_type, attributes or {})
    
    def end_span(self, span: Span, status: StatusCode = StatusCode.OK, error_message: Optional[str] = None):
        """
        End a span
        
        Args:
            span: Span to end
            status: Span status
            error_message: Error message if status is error
        """
        try:
            if hasattr(span, 'set_status'):
                # OpenTelemetry span
                span.set_status(status, error_message)
                span.end()
                
                # Update metrics
                span_type = span.get_attributes().get("span.type", "unknown")
                duration = time.time() - span.start_time / 1e9  # Convert nanoseconds to seconds
                
                self._update_metrics("spans_total", {"span_type": span_type, "status": status.name})
                self._update_metrics("span_duration", {"span_type": span_type}, duration)
                self._update_metrics("active_spans", {"span_type": span_type}, increment=False)
                
            else:
                # Fallback span
                span.end(status, error_message)
                
        except Exception as e:
            logger.error(f"Failed to end span: {e}")
            self._update_metrics("trace_errors", {"error_type": "span_end"})
    
    def add_event(self, span: Span, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to span"""
        try:
            if hasattr(span, 'add_event'):
                span.add_event(name, attributes or {})
            else:
                # Fallback span
                span.add_event(name, attributes or {})
        except Exception as e:
            logger.error(f"Failed to add event to span: {e}")
    
    def add_attribute(self, span: Span, key: str, value: Any):
        """Add attribute to span"""
        try:
            if hasattr(span, 'set_attribute'):
                span.set_attribute(key, value)
            else:
                # Fallback span
                span.add_attribute(key, value)
        except Exception as e:
            logger.error(f"Failed to add attribute to span: {e}")
    
    def _update_metrics(self, metric_name: str, labels: Dict[str, str], value: float = 1.0, increment: bool = True):
        """Update Prometheus metrics"""
        if metric_name not in self.metrics:
            return
            
        try:
            metric = self.metrics[metric_name]
            label_values = [labels.get(label, "") for label in metric._labelnames]
            
            if hasattr(metric, 'inc'):
                metric.labels(*label_values).inc(value)
            elif hasattr(metric, 'observe'):
                metric.labels(*label_values).observe(value)
            elif hasattr(metric, 'set'):
                if increment:
                    metric.labels(*label_values).inc(value)
                else:
                    metric.labels(*label_values).dec(value)
                    
        except Exception as e:
            logger.error(f"Failed to update metric {metric_name}: {e}")
    
    @contextmanager
    def span_context(
        self,
        name: str,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for span creation
        
        Args:
            name: Span name
            span_type: Type of span
            attributes: Additional attributes
            
        Yields:
            Span context
        """
        span = self.start_span(name, span_type, attributes)
        try:
            yield span
        except Exception as e:
            self.end_span(span, StatusCode.ERROR, str(e))
            raise
        else:
            self.end_span(span, StatusCode.OK)
    
    def trace_function(
        self,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Decorator for tracing functions
        
        Args:
            span_type: Type of span
            attributes: Additional attributes
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = f"{func.__module__}.{func.__name__}"
                func_attributes = {
                    "function.name": func.__name__,
                    "function.module": func.__module__,
                    **(attributes or {})
                }
                
                with self.span_context(func_name, span_type, func_attributes):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def trace_async_function(
        self,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Decorator for tracing async functions
        
        Args:
            span_type: Type of span
            attributes: Additional attributes
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                func_name = f"{func.__module__}.{func.__name__}"
                func_attributes = {
                    "function.name": func.__name__,
                    "function.module": func.__module__,
                    **(attributes or {})
                }
                
                with self.span_context(func_name, span_type, func_attributes):
                    return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_trace_id(self, span: Span) -> str:
        """Get trace ID from span"""
        try:
            if hasattr(span, 'get_span_context'):
                return span.get_span_context().trace_id
            else:
                return span.trace_id
        except Exception:
            return str(uuid.uuid4())
    
    def get_span_id(self, span: Span) -> str:
        """Get span ID from span"""
        try:
            if hasattr(span, 'get_span_context'):
                return span.get_span_context().span_id
            else:
                return span.span_id
        except Exception:
            return str(uuid.uuid4())
    
    def inject_context(self, span: Span, carrier: Dict[str, str]):
        """Inject trace context into carrier for propagation"""
        try:
            if hasattr(span, 'get_span_context'):
                trace_id = span.get_span_context().trace_id
                span_id = span.get_span_context().span_id
                carrier["X-Trace-ID"] = trace_id
                carrier["X-Span-ID"] = span_id
        except Exception as e:
            logger.error(f"Failed to inject context: {e}")
    
    def extract_context(self, carrier: Dict[str, str]) -> Optional[Span]:
        """Extract trace context from carrier"""
        try:
            trace_id = carrier.get("X-Trace-ID")
            span_id = carrier.get("X-Span-ID")
            if trace_id and span_id:
                # Create span context from extracted IDs
                # This is a simplified implementation
                return self.start_span("extracted_span")
        except Exception as e:
            logger.error(f"Failed to extract context: {e}")
        return None
    
    def shutdown(self):
        """Shutdown tracing system"""
        try:
            if self.tracer_provider:
                self.tracer_provider.shutdown()
            logger.info("Tracing system shutdown")
        except Exception as e:
            logger.error(f"Failed to shutdown tracing: {e}")


class FallbackSpan:
    """Fallback span implementation when OpenTelemetry is not available"""
    
    def __init__(self, name: str, span_type: SpanType, attributes: Dict[str, Any]):
        self.name = name
        self.span_type = span_type
        self.attributes = attributes.copy()
        self.events = []
        self.start_time = time.time()
        self.end_time = None
        self.status = StatusCode.OK
        self.error_message = None
        self.trace_id = str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        
        # Add default attributes
        self.attributes.update({
            "span.type": span_type.value,
            "span.name": name,
            "trace.id": self.trace_id,
            "span.id": self.span_id
        })
    
    def set_attribute(self, key: str, value: Any):
        """Set span attribute"""
        self.attributes[key] = value
    
    def add_attribute(self, key: str, value: Any):
        """Add span attribute"""
        self.attributes[key] = value
    
    def add_event(self, name: str, attributes: Dict[str, Any]):
        """Add event to span"""
        self.events.append({
            "name": name,
            "attributes": attributes,
            "timestamp": time.time()
        })
    
    def set_status(self, status: StatusCode, description: Optional[str] = None):
        """Set span status"""
        self.status = status
        if description:
            self.error_message = description
    
    def end(self, status: StatusCode = StatusCode.OK, error_message: Optional[str] = None):
        """End span"""
        self.end_time = time.time()
        self.status = status
        if error_message:
            self.error_message = error_message
        
        # Log span information
        duration = self.end_time - self.start_time
        logger.info(f"Span ended: {self.name} (duration: {duration:.3f}s, status: {status.name})")


# Global tracing instance
_tracing_instance: Optional[AdvancedTracing] = None


def get_tracing() -> AdvancedTracing:
    """Get global tracing instance"""
    global _tracing_instance
    if _tracing_instance is None:
        config = TracingConfig()
        _tracing_instance = AdvancedTracing(config)
    return _tracing_instance


def init_tracing(config: TracingConfig):
    """Initialize global tracing with custom config"""
    global _tracing_instance
    _tracing_instance = AdvancedTracing(config)


def trace_function(span_type: SpanType = SpanType.BUSINESS_LOGIC, attributes: Optional[Dict[str, Any]] = None):
    """Global decorator for tracing functions"""
    return get_tracing().trace_function(span_type, attributes)


def trace_async_function(span_type: SpanType = SpanType.BUSINESS_LOGIC, attributes: Optional[Dict[str, Any]] = None):
    """Global decorator for tracing async functions"""
    return get_tracing().trace_async_function(span_type, attributes)


def start_span(name: str, span_type: SpanType = SpanType.BUSINESS_LOGIC, attributes: Optional[Dict[str, Any]] = None) -> Span:
    """Global function to start span"""
    return get_tracing().start_span(name, span_type, attributes)


def end_span(span: Span, status: StatusCode = StatusCode.OK, error_message: Optional[str] = None):
    """Global function to end span"""
    get_tracing().end_span(span, status, error_message)


@contextmanager
def span_context(name: str, span_type: SpanType = SpanType.BUSINESS_LOGIC, attributes: Optional[Dict[str, Any]] = None):
    """Global context manager for span creation"""
    with get_tracing().span_context(name, span_type, attributes) as span:
        yield span 