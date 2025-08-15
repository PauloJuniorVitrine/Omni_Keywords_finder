"""
Tracing Middleware for Flask Application
Tracing ID: FINE_TUNING_IMPLEMENTATION_20250127_001
Created: 2025-01-27
Version: 1.0

This module provides automatic tracing middleware for Flask applications,
including correlation ID injection, span creation, and request/response tracking.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional
from functools import wraps

from flask import request, g, current_app
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.trace.span import Span

from infrastructure.observability.opentelemetry_config import get_ot_config

logger = logging.getLogger(__name__)

class TracingMiddleware:
    """
    Middleware for automatic tracing of Flask requests.
    
    Features:
    - Automatic correlation ID generation and propagation
    - Request/response span creation
    - Performance metrics collection
    - Error tracking and logging
    - Integration with OpenTelemetry
    """
    
    def __init__(self, app=None):
        self.app = app
        self.ot_config = get_ot_config()
        self.tracer = trace.get_tracer(__name__)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
        
        # Add custom headers to response
        app.after_request(self.add_tracing_headers)
        
        logger.info("Tracing middleware initialized")
    
    def before_request(self):
        """Handle before request processing."""
        start_time = time.time()
        
        # Generate or extract correlation ID
        correlation_id = self._get_correlation_id()
        
        # Create request span
        span = self.tracer.start_span(
            f"{request.method} {request.endpoint or request.path}",
            kind=SpanKind.SERVER,
            attributes={
                "http.method": request.method,
                "http.url": request.url,
                "http.target": request.path,
                "http.host": request.host,
                "http.user_agent": request.headers.get("User-Agent", ""),
                "http.request_id": correlation_id,
                "http.scheme": request.scheme,
                "http.flavor": request.environ.get("SERVER_PROTOCOL", ""),
                "net.peer.ip": request.remote_addr,
                "net.peer.port": request.environ.get("REMOTE_PORT"),
            }
        )
        
        # Store in Flask g object
        g.tracing_span = span
        g.tracing_start_time = start_time
        g.correlation_id = correlation_id
        
        # Add correlation ID to request context
        request.correlation_id = correlation_id
        
        # Log request start
        logger.info(
            f"Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.path,
                "user_agent": request.headers.get("User-Agent", ""),
                "remote_addr": request.remote_addr
            }
        )
    
    def after_request(self, response):
        """Handle after request processing."""
        span = getattr(g, 'tracing_span', None)
        start_time = getattr(g, 'tracing_start_time', None)
        
        if span and start_time:
            # Calculate duration
            duration = time.time() - start_time
            
            # Add response attributes
            span.set_attributes({
                "http.status_code": response.status_code,
                "http.status_text": response.status_text,
                "http.response_size": len(response.get_data()),
                "http.duration": duration
            })
            
            # Set span status based on response
            if response.status_code < 400:
                span.set_status(Status(StatusCode.OK))
            elif response.status_code < 500:
                span.set_status(Status(StatusCode.ERROR, f"Client error: {response.status_code}"))
            else:
                span.set_status(Status(StatusCode.ERROR, f"Server error: {response.status_code}"))
            
            # Record metrics
            self.ot_config.record_api_request(
                endpoint=request.endpoint or request.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration
            )
            
            # Log request completion
            logger.info(
                f"Request completed",
                extra={
                    "correlation_id": getattr(g, 'correlation_id', ''),
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration": duration
                }
            )
        
        return response
    
    def teardown_request(self, exception=None):
        """Handle request teardown."""
        span = getattr(g, 'tracing_span', None)
        
        if span:
            # Handle exceptions
            if exception:
                span.set_status(Status(StatusCode.ERROR, str(exception)))
                span.record_exception(exception)
                
                logger.error(
                    f"Request failed with exception",
                    extra={
                        "correlation_id": getattr(g, 'correlation_id', ''),
                        "method": request.method,
                        "path": request.path,
                        "exception": str(exception),
                        "exception_type": type(exception).__name__
                    },
                    exc_info=True
                )
            
            # End span
            span.end()
            
            # Clean up
            if hasattr(g, 'tracing_span'):
                delattr(g, 'tracing_span')
            if hasattr(g, 'tracing_start_time'):
                delattr(g, 'tracing_start_time')
            if hasattr(g, 'correlation_id'):
                delattr(g, 'correlation_id')
    
    def add_tracing_headers(self, response):
        """Add tracing headers to response."""
        correlation_id = getattr(g, 'correlation_id', None)
        
        if correlation_id:
            response.headers['X-Correlation-ID'] = correlation_id
            response.headers['X-Request-ID'] = correlation_id
        
        # Add OpenTelemetry trace context headers
        span = getattr(g, 'tracing_span', None)
        if span:
            # Add trace and span IDs for debugging
            response.headers['X-Trace-ID'] = format(span.get_span_context().trace_id, '032x')
            response.headers['X-Span-ID'] = format(span.get_span_context().span_id, '016x')
        
        return response
    
    def _get_correlation_id(self) -> str:
        """Get or generate correlation ID."""
        # Try to get from headers first
        correlation_id = request.headers.get('X-Correlation-ID') or \
                        request.headers.get('X-Request-ID') or \
                        request.headers.get('Correlation-ID')
        
        # Generate new if not present
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        return correlation_id


def trace_operation(operation_name: str = None, attributes: Dict[str, Any] = None):
    """
    Decorator for tracing operations with correlation IDs.
    
    Args:
        operation_name: Name of the operation (defaults to function name)
        attributes: Additional attributes to add to the span
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get operation name
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Get correlation ID from request context
            correlation_id = getattr(g, 'correlation_id', None)
            
            # Create span attributes
            span_attributes = {
                "operation.name": op_name,
                "operation.module": func.__module__,
                "operation.function": func.__name__,
            }
            
            if correlation_id:
                span_attributes["correlation_id"] = correlation_id
            
            if attributes:
                span_attributes.update(attributes)
            
            # Create span
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(
                op_name,
                kind=SpanKind.INTERNAL,
                attributes=span_attributes
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator


def trace_database_operation(operation: str, table: str = None, query: str = None):
    """
    Decorator for tracing database operations.
    
    Args:
        operation: Type of database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        query: SQL query (optional, for debugging)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get correlation ID
            correlation_id = getattr(g, 'correlation_id', None)
            
            # Create span attributes
            span_attributes = {
                "db.operation": operation,
                "db.system": "sqlite",  # Default, can be overridden
                "span.kind": "client"
            }
            
            if table:
                span_attributes["db.table"] = table
            
            if query:
                span_attributes["db.statement"] = query
            
            if correlation_id:
                span_attributes["correlation_id"] = correlation_id
            
            # Create span
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(
                f"db.{operation.lower()}",
                kind=SpanKind.CLIENT,
                attributes=span_attributes
            ) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    span.set_attributes({
                        "db.duration": duration,
                        "db.rows_affected": getattr(result, 'rowcount', None)
                    })
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    span.set_attributes({"db.duration": duration})
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator


def trace_external_api_call(service: str, endpoint: str, method: str = "GET"):
    """
    Decorator for tracing external API calls.
    
    Args:
        service: Name of the external service
        endpoint: API endpoint
        method: HTTP method
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get correlation ID
            correlation_id = getattr(g, 'correlation_id', None)
            
            # Create span attributes
            span_attributes = {
                "http.method": method,
                "http.url": endpoint,
                "http.target": endpoint,
                "peer.service": service,
                "span.kind": "client"
            }
            
            if correlation_id:
                span_attributes["correlation_id"] = correlation_id
            
            # Create span
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(
                f"{service}.{method.lower()}",
                kind=SpanKind.CLIENT,
                attributes=span_attributes
            ) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    span.set_attributes({
                        "http.duration": duration,
                        "http.status_code": getattr(result, 'status_code', None)
                    })
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    span.set_attributes({"http.duration": duration})
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator


def get_current_correlation_id() -> Optional[str]:
    """Get current correlation ID from Flask context."""
    return getattr(g, 'correlation_id', None)


def get_current_span() -> Optional[Span]:
    """Get current span from Flask context."""
    return getattr(g, 'tracing_span', None)


def add_span_attribute(key: str, value: Any):
    """Add attribute to current span."""
    span = get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Dict[str, Any] = None):
    """Add event to current span."""
    span = get_current_span()
    if span:
        span.add_event(name, attributes or {})


# Global middleware instance
tracing_middleware = TracingMiddleware() 