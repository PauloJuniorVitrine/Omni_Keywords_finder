"""
🔍 Trace Decorators System
📅 Generated: 2025-01-27
🎯 Purpose: Automatic tracing decorators for functions and methods
📋 Tracing ID: TRACE_DECORATOR_003_20250127
"""

import logging
import time
import functools
import inspect
from typing import Any, Callable, Dict, Optional, Union, Type
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from contextlib import contextmanager

from .advanced_tracing import (
    AdvancedTracing, TracingConfig, SpanType, trace_function, trace_async_function,
    start_span, end_span, span_context
)
from .trace_context import (
    TraceContext, ContextType, trace_context_decorator, async_trace_context_decorator,
    get_context, set_context, clear_context
)

logger = logging.getLogger(__name__)


class TraceLevel(Enum):
    """Trace levels for different granularity"""
    NONE = "none"
    BASIC = "basic"
    DETAILED = "detailed"
    FULL = "full"


@dataclass
class TraceDecoratorConfig:
    """Configuration for trace decorators"""
    span_type: SpanType = SpanType.BUSINESS_LOGIC
    context_type: ContextType = ContextType.REQUEST
    trace_level: TraceLevel = TraceLevel.BASIC
    include_args: bool = True
    include_kwargs: bool = True
    include_result: bool = False
    include_duration: bool = True
    include_exceptions: bool = True
    max_arg_length: int = 100
    max_result_length: int = 200
    excluded_args: set = field(default_factory=set)
    excluded_kwargs: set = field(default_factory=set)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    enable_metrics: bool = True
    enable_logs: bool = True


class TraceDecorator:
    """
    Advanced trace decorator with configurable options
    """
    
    def __init__(self, config: Optional[TraceDecoratorConfig] = None):
        self.config = config or TraceDecoratorConfig()
        self.tracing = AdvancedTracing(TracingConfig())
    
    def __call__(self, func: Callable) -> Callable:
        """
        Main decorator implementation
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        if asyncio.iscoroutinefunction(func):
            return self._decorate_async_function(func)
        else:
            return self._decorate_sync_function(func)
    
    def _decorate_sync_function(self, func: Callable) -> Callable:
        """Decorate synchronous function"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create span name
            span_name = self._create_span_name(func)
            
            # Create attributes
            attributes = self._create_attributes(func, args, kwargs)
            
            # Start span
            span = start_span(span_name, self.config.span_type, attributes)
            
            try:
                # Execute function
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Add result if configured
                if self.config.include_result and self.config.trace_level in [TraceLevel.DETAILED, TraceLevel.FULL]:
                    self._add_result_attribute(span, result)
                
                # Add duration if configured
                if self.config.include_duration:
                    span.set_attribute("duration", duration)
                
                # Log success if configured
                if self.config.enable_logs:
                    self._log_success(func, duration, result)
                
                return result
                
            except Exception as e:
                # Add exception if configured
                if self.config.include_exceptions:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                
                # Log error if configured
                if self.config.enable_logs:
                    self._log_error(func, e)
                
                # End span with error
                end_span(span, span.get_status().StatusCode.ERROR, str(e))
                raise
            else:
                # End span successfully
                end_span(span, span.get_status().StatusCode.OK)
        
        return wrapper
    
    def _decorate_async_function(self, func: Callable) -> Callable:
        """Decorate asynchronous function"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create span name
            span_name = self._create_span_name(func)
            
            # Create attributes
            attributes = self._create_attributes(func, args, kwargs)
            
            # Start span
            span = start_span(span_name, self.config.span_type, attributes)
            
            try:
                # Execute function
                start_time = time.time()
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Add result if configured
                if self.config.include_result and self.config.trace_level in [TraceLevel.DETAILED, TraceLevel.FULL]:
                    self._add_result_attribute(span, result)
                
                # Add duration if configured
                if self.config.include_duration:
                    span.set_attribute("duration", duration)
                
                # Log success if configured
                if self.config.enable_logs:
                    self._log_success(func, duration, result)
                
                return result
                
            except Exception as e:
                # Add exception if configured
                if self.config.include_exceptions:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                
                # Log error if configured
                if self.config.enable_logs:
                    self._log_error(func, e)
                
                # End span with error
                end_span(span, span.get_status().StatusCode.ERROR, str(e))
                raise
            else:
                # End span successfully
                end_span(span, span.get_status().StatusCode.OK)
        
        return wrapper
    
    def _create_span_name(self, func: Callable) -> str:
        """Create span name from function"""
        module_name = func.__module__ or "unknown"
        func_name = func.__name__ or "unknown"
        return f"{module_name}.{func_name}"
    
    def _create_attributes(self, func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """Create span attributes from function and arguments"""
        attributes = {
            "function.name": func.__name__,
            "function.module": func.__module__,
            "function.qualname": func.__qualname__,
            **self.config.custom_attributes
        }
        
        # Add arguments if configured
        if self.config.include_args and self.config.trace_level != TraceLevel.NONE:
            self._add_args_attributes(attributes, func, args)
        
        # Add keyword arguments if configured
        if self.config.include_kwargs and self.config.trace_level in [TraceLevel.DETAILED, TraceLevel.FULL]:
            self._add_kwargs_attributes(attributes, kwargs)
        
        return attributes
    
    def _add_args_attributes(self, attributes: Dict[str, Any], func: Callable, args: tuple):
        """Add function arguments as attributes"""
        try:
            # Get function signature
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            
            # Add positional arguments
            for i, arg in enumerate(args):
                if i < len(param_names):
                    param_name = param_names[i]
                    if param_name not in self.config.excluded_args:
                        arg_str = self._format_value(arg)
                        attributes[f"arg.{param_name}"] = arg_str
                else:
                    # Extra positional arguments
                    arg_str = self._format_value(arg)
                    attributes[f"arg.extra_{i}"] = arg_str
                    
        except Exception as e:
            logger.warning(f"Failed to add args attributes: {e}")
    
    def _add_kwargs_attributes(self, attributes: Dict[str, Any], kwargs: dict):
        """Add keyword arguments as attributes"""
        try:
            for key, value in kwargs.items():
                if key not in self.config.excluded_kwargs:
                    value_str = self._format_value(value)
                    attributes[f"kwarg.{key}"] = value_str
        except Exception as e:
            logger.warning(f"Failed to add kwargs attributes: {e}")
    
    def _add_result_attribute(self, span, result):
        """Add function result as attribute"""
        try:
            result_str = self._format_value(result, max_length=self.config.max_result_length)
            span.set_attribute("result", result_str)
        except Exception as e:
            logger.warning(f"Failed to add result attribute: {e}")
    
    def _format_value(self, value: Any, max_length: int = None) -> str:
        """Format value for attribute storage"""
        try:
            if value is None:
                return "None"
            elif isinstance(value, (str, int, float, bool)):
                value_str = str(value)
            elif isinstance(value, (list, tuple)):
                value_str = str(value[:3]) + "..." if len(value) > 3 else str(value)
            elif isinstance(value, dict):
                value_str = str(dict(list(value.items())[:3])) + "..." if len(value) > 3 else str(value)
            else:
                value_str = str(type(value).__name__)
            
            # Truncate if too long
            if max_length and len(value_str) > max_length:
                value_str = value_str[:max_length] + "..."
            
            return value_str
            
        except Exception:
            return str(type(value).__name__)
    
    def _log_success(self, func: Callable, duration: float, result: Any):
        """Log successful function execution"""
        try:
            log_data = {
                "function": f"{func.__module__}.{func.__name__}",
                "duration": f"{duration:.3f}s",
                "status": "success"
            }
            
            if self.config.trace_level == TraceLevel.FULL:
                log_data["result_type"] = type(result).__name__
            
            logger.info(f"Function executed successfully", extra=log_data)
            
        except Exception as e:
            logger.warning(f"Failed to log success: {e}")
    
    def _log_error(self, func: Callable, error: Exception):
        """Log function execution error"""
        try:
            log_data = {
                "function": f"{func.__module__}.{func.__name__}",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "status": "error"
            }
            
            logger.error(f"Function execution failed", extra=log_data)
            
        except Exception as e:
            logger.warning(f"Failed to log error: {e}")


def trace(
    span_type: SpanType = SpanType.BUSINESS_LOGIC,
    context_type: ContextType = ContextType.REQUEST,
    trace_level: TraceLevel = TraceLevel.BASIC,
    include_args: bool = True,
    include_kwargs: bool = True,
    include_result: bool = False,
    include_duration: bool = True,
    include_exceptions: bool = True,
    max_arg_length: int = 100,
    max_result_length: int = 200,
    excluded_args: set = None,
    excluded_kwargs: set = None,
    custom_attributes: Dict[str, Any] = None,
    enable_metrics: bool = True,
    enable_logs: bool = True
):
    """
    Advanced trace decorator with configurable options
    
    Args:
        span_type: Type of span for categorization
        context_type: Type of context for propagation
        trace_level: Level of tracing detail
        include_args: Include function arguments in trace
        include_kwargs: Include keyword arguments in trace
        include_result: Include function result in trace
        include_duration: Include execution duration
        include_exceptions: Include exception information
        max_arg_length: Maximum length for argument values
        max_result_length: Maximum length for result values
        excluded_args: Set of argument names to exclude
        excluded_kwargs: Set of keyword argument names to exclude
        custom_attributes: Additional custom attributes
        enable_metrics: Enable Prometheus metrics
        enable_logs: Enable logging
        
    Returns:
        Decorator function
    """
    config = TraceDecoratorConfig(
        span_type=span_type,
        context_type=context_type,
        trace_level=trace_level,
        include_args=include_args,
        include_kwargs=include_kwargs,
        include_result=include_result,
        include_duration=include_duration,
        include_exceptions=include_exceptions,
        max_arg_length=max_arg_length,
        max_result_length=max_result_length,
        excluded_args=excluded_args or set(),
        excluded_kwargs=excluded_kwargs or set(),
        custom_attributes=custom_attributes or {},
        enable_metrics=enable_metrics,
        enable_logs=enable_logs
    )
    
    return TraceDecorator(config)


def trace_simple(span_type: SpanType = SpanType.BUSINESS_LOGIC):
    """
    Simple trace decorator with basic configuration
    
    Args:
        span_type: Type of span for categorization
        
    Returns:
        Decorator function
    """
    return trace(span_type=span_type, trace_level=TraceLevel.BASIC)


def trace_detailed(span_type: SpanType = SpanType.BUSINESS_LOGIC):
    """
    Detailed trace decorator with comprehensive information
    
    Args:
        span_type: Type of span for categorization
        
    Returns:
        Decorator function
    """
    return trace(
        span_type=span_type,
        trace_level=TraceLevel.DETAILED,
        include_result=True,
        include_kwargs=True
    )


def trace_full(span_type: SpanType = SpanType.BUSINESS_LOGIC):
    """
    Full trace decorator with maximum information
    
    Args:
        span_type: Type of span for categorization
        
    Returns:
        Decorator function
    """
    return trace(
        span_type=span_type,
        trace_level=TraceLevel.FULL,
        include_result=True,
        include_kwargs=True,
        enable_logs=True
    )


def trace_http_request():
    """Trace decorator specifically for HTTP requests"""
    return trace(
        span_type=SpanType.HTTP_REQUEST,
        context_type=ContextType.REQUEST,
        trace_level=TraceLevel.DETAILED,
        include_args=True,
        include_kwargs=True,
        include_result=False,
        custom_attributes={"operation.type": "http_request"}
    )


def trace_database_query():
    """Trace decorator specifically for database queries"""
    return trace(
        span_type=SpanType.DATABASE_QUERY,
        context_type=ContextType.DATABASE,
        trace_level=TraceLevel.DETAILED,
        include_args=True,
        include_kwargs=True,
        include_result=False,
        custom_attributes={"operation.type": "database_query"}
    )


def trace_external_api():
    """Trace decorator specifically for external API calls"""
    return trace(
        span_type=SpanType.EXTERNAL_API,
        context_type=ContextType.EXTERNAL,
        trace_level=TraceLevel.DETAILED,
        include_args=True,
        include_kwargs=True,
        include_result=False,
        custom_attributes={"operation.type": "external_api"}
    )


def trace_background_task():
    """Trace decorator specifically for background tasks"""
    return trace(
        span_type=SpanType.BACKGROUND_TASK,
        context_type=ContextType.BACKGROUND,
        trace_level=TraceLevel.BASIC,
        include_args=True,
        include_kwargs=False,
        include_result=False,
        custom_attributes={"operation.type": "background_task"}
    )


class TraceClass:
    """
    Class decorator for tracing all methods
    """
    
    def __init__(
        self,
        span_type: SpanType = SpanType.BUSINESS_LOGIC,
        trace_level: TraceLevel = TraceLevel.BASIC,
        include_private: bool = False,
        excluded_methods: set = None,
        **kwargs
    ):
        self.span_type = span_type
        self.trace_level = trace_level
        self.include_private = include_private
        self.excluded_methods = excluded_methods or set()
        self.kwargs = kwargs
    
    def __call__(self, cls: Type) -> Type:
        """
        Decorate class with tracing for all methods
        
        Args:
            cls: Class to decorate
            
        Returns:
            Decorated class
        """
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            # Skip private methods unless configured
            if name.startswith('_') and not self.include_private:
                continue
            
            # Skip excluded methods
            if name in self.excluded_methods:
                continue
            
            # Skip special methods
            if name.startswith('__') and name.endswith('__'):
                continue
            
            # Create decorator for this method
            decorator = trace(
                span_type=self.span_type,
                trace_level=self.trace_level,
                custom_attributes={
                    "class.name": cls.__name__,
                    "method.name": name,
                    **self.kwargs
                }
            )
            
            # Apply decorator
            setattr(cls, name, decorator(method))
        
        return cls


def trace_class(
    span_type: SpanType = SpanType.BUSINESS_LOGIC,
    trace_level: TraceLevel = TraceLevel.BASIC,
    include_private: bool = False,
    excluded_methods: set = None,
    **kwargs
):
    """
    Class decorator for tracing all methods
    
    Args:
        span_type: Type of span for categorization
        trace_level: Level of tracing detail
        include_private: Include private methods
        excluded_methods: Set of method names to exclude
        **kwargs: Additional configuration options
        
    Returns:
        Class decorator
    """
    return TraceClass(
        span_type=span_type,
        trace_level=trace_level,
        include_private=include_private,
        excluded_methods=excluded_methods,
        **kwargs
    )


@contextmanager
def trace_context(
    name: str,
    span_type: SpanType = SpanType.BUSINESS_LOGIC,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Context manager for tracing code blocks
    
    Args:
        name: Name of the trace span
        span_type: Type of span for categorization
        attributes: Additional attributes
        
    Yields:
        Span object
    """
    with span_context(name, span_type, attributes) as span:
        yield span


def trace_method(
    span_type: SpanType = SpanType.BUSINESS_LOGIC,
    trace_level: TraceLevel = TraceLevel.BASIC,
    include_self: bool = False,
    **kwargs
):
    """
    Decorator specifically for class methods
    
    Args:
        span_type: Type of span for categorization
        trace_level: Level of tracing detail
        include_self: Include self parameter in trace
        **kwargs: Additional configuration options
        
    Returns:
        Method decorator
    """
    excluded_args = set() if include_self else {'self'}
    
    return trace(
        span_type=span_type,
        trace_level=trace_level,
        excluded_args=excluded_args,
        **kwargs
    )


# Convenience decorators for common use cases
trace_api = trace_http_request
trace_db = trace_database_query
trace_external = trace_external_api
trace_task = trace_background_task
trace_method_simple = lambda: trace_method(trace_level=TraceLevel.BASIC)
trace_method_detailed = lambda: trace_method(trace_level=TraceLevel.DETAILED)
trace_method_full = lambda: trace_method(trace_level=TraceLevel.FULL)


# Example usage decorators
def example_trace_usage():
    """
    Example usage of trace decorators
    """
    
    # Simple tracing
    @trace_simple(SpanType.BUSINESS_LOGIC)
    def simple_function(x, y):
        return x + y
    
    # Detailed tracing
    @trace_detailed(SpanType.DATABASE_QUERY)
    def database_query(query, params):
        return {"result": "data"}
    
    # HTTP request tracing
    @trace_http_request()
    def api_call(url, method="GET"):
        return {"status": 200}
    
    # Class with tracing
    @trace_class(SpanType.BUSINESS_LOGIC, TraceLevel.DETAILED)
    class ExampleService:
        def process_data(self, data):
            return {"processed": data}
        
        def _private_method(self):
            pass  # Won't be traced unless include_private=True
    
    # Method-specific tracing
    class AnotherService:
        @trace_method_detailed()
        def important_method(self, data):
            return {"result": data}
        
        @trace_method_simple()
        def simple_method(self):
            return "ok"
    
    # Context manager usage
    def complex_operation():
        with trace_context("complex_operation", SpanType.BUSINESS_LOGIC):
            # Do something complex
            pass 