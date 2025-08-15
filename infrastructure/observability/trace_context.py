"""
🔍 Trace Context Management System
📅 Generated: 2025-01-27
🎯 Purpose: Trace context propagation and management
📋 Tracing ID: TRACE_CONTEXT_002_20250127
"""

import logging
import threading
import asyncio
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from functools import wraps

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context for categorization"""
    REQUEST = "request"
    BACKGROUND = "background"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    API_CALL = "api_call"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL = "external"


@dataclass
class TraceContext:
    """Trace context information"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    context_type: ContextType = ContextType.REQUEST
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "context_type": self.context_type.value,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "attributes": self.attributes,
            "start_time": self.start_time,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceContext':
        """Create context from dictionary"""
        return cls(
            trace_id=data.get("trace_id", str(uuid.uuid4())),
            span_id=data.get("span_id", str(uuid.uuid4())),
            parent_span_id=data.get("parent_span_id"),
            context_type=ContextType(data.get("context_type", ContextType.REQUEST.value)),
            user_id=data.get("user_id"),
            request_id=data.get("request_id"),
            correlation_id=data.get("correlation_id"),
            attributes=data.get("attributes", {}),
            start_time=data.get("start_time", time.time()),
            metadata=data.get("metadata", {})
        )
    
    def add_attribute(self, key: str, value: Any):
        """Add attribute to context"""
        self.attributes[key] = value
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get attribute from context"""
        return self.attributes.get(key, default)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to context"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from context"""
        return self.metadata.get(key, default)


class TraceContextManager:
    """
    Thread-safe trace context manager
    """
    
    def __init__(self):
        self._contexts = {}
        self._lock = threading.RLock()
        self._async_contexts = {}
        self._async_lock = asyncio.Lock()
    
    def set_context(self, context: TraceContext, thread_id: Optional[str] = None):
        """
        Set trace context for current thread
        
        Args:
            context: Trace context to set
            thread_id: Optional thread ID (defaults to current thread)
        """
        if thread_id is None:
            thread_id = str(threading.get_ident())
        
        with self._lock:
            self._contexts[thread_id] = context
            logger.debug(f"Context set for thread {thread_id}: {context.trace_id}")
    
    def get_context(self, thread_id: Optional[str] = None) -> Optional[TraceContext]:
        """
        Get trace context for current thread
        
        Args:
            thread_id: Optional thread ID (defaults to current thread)
            
        Returns:
            Trace context or None if not found
        """
        if thread_id is None:
            thread_id = str(threading.get_ident())
        
        with self._lock:
            return self._contexts.get(thread_id)
    
    def clear_context(self, thread_id: Optional[str] = None):
        """
        Clear trace context for current thread
        
        Args:
            thread_id: Optional thread ID (defaults to current thread)
        """
        if thread_id is None:
            thread_id = str(threading.get_ident())
        
        with self._lock:
            if thread_id in self._contexts:
                del self._contexts[thread_id]
                logger.debug(f"Context cleared for thread {thread_id}")
    
    async def set_async_context(self, context: TraceContext, task_id: Optional[str] = None):
        """
        Set trace context for current async task
        
        Args:
            context: Trace context to set
            task_id: Optional task ID (defaults to current task)
        """
        if task_id is None:
            task_id = str(id(asyncio.current_task()))
        
        async with self._async_lock:
            self._async_contexts[task_id] = context
            logger.debug(f"Async context set for task {task_id}: {context.trace_id}")
    
    async def get_async_context(self, task_id: Optional[str] = None) -> Optional[TraceContext]:
        """
        Get trace context for current async task
        
        Args:
            task_id: Optional task ID (defaults to current task)
            
        Returns:
            Trace context or None if not found
        """
        if task_id is None:
            task_id = str(id(asyncio.current_task()))
        
        async with self._async_lock:
            return self._async_contexts.get(task_id)
    
    async def clear_async_context(self, task_id: Optional[str] = None):
        """
        Clear trace context for current async task
        
        Args:
            task_id: Optional task ID (defaults to current task)
        """
        if task_id is None:
            task_id = str(id(asyncio.current_task()))
        
        async with self._async_lock:
            if task_id in self._async_contexts:
                del self._async_contexts[task_id]
                logger.debug(f"Async context cleared for task {task_id}")
    
    def create_child_context(
        self,
        context_type: ContextType = ContextType.REQUEST,
        attributes: Optional[Dict[str, Any]] = None,
        thread_id: Optional[str] = None
    ) -> TraceContext:
        """
        Create child context from current context
        
        Args:
            context_type: Type of child context
            attributes: Additional attributes
            thread_id: Optional thread ID (defaults to current thread)
            
        Returns:
            New child trace context
        """
        parent_context = self.get_context(thread_id)
        
        if parent_context:
            child_context = TraceContext(
                trace_id=parent_context.trace_id,
                span_id=str(uuid.uuid4()),
                parent_span_id=parent_context.span_id,
                context_type=context_type,
                user_id=parent_context.user_id,
                request_id=parent_context.request_id,
                correlation_id=parent_context.correlation_id,
                attributes=attributes or {},
                metadata=parent_context.metadata.copy()
            )
        else:
            # Create new root context
            child_context = TraceContext(
                trace_id=str(uuid.uuid4()),
                span_id=str(uuid.uuid4()),
                context_type=context_type,
                attributes=attributes or {}
            )
        
        return child_context
    
    async def create_async_child_context(
        self,
        context_type: ContextType = ContextType.REQUEST,
        attributes: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> TraceContext:
        """
        Create child context from current async context
        
        Args:
            context_type: Type of child context
            attributes: Additional attributes
            task_id: Optional task ID (defaults to current task)
            
        Returns:
            New child trace context
        """
        parent_context = await self.get_async_context(task_id)
        
        if parent_context:
            child_context = TraceContext(
                trace_id=parent_context.trace_id,
                span_id=str(uuid.uuid4()),
                parent_span_id=parent_context.span_id,
                context_type=context_type,
                user_id=parent_context.user_id,
                request_id=parent_context.request_id,
                correlation_id=parent_context.correlation_id,
                attributes=attributes or {},
                metadata=parent_context.metadata.copy()
            )
        else:
            # Create new root context
            child_context = TraceContext(
                trace_id=str(uuid.uuid4()),
                span_id=str(uuid.uuid4()),
                context_type=context_type,
                attributes=attributes or {}
            )
        
        return child_context
    
    def inject_context(self, context: TraceContext, carrier: Dict[str, str]):
        """
        Inject trace context into carrier for propagation
        
        Args:
            context: Trace context to inject
            carrier: Carrier dictionary (e.g., HTTP headers)
        """
        carrier.update({
            "X-Trace-ID": context.trace_id,
            "X-Span-ID": context.span_id,
            "X-Context-Type": context.context_type.value
        })
        
        if context.parent_span_id:
            carrier["X-Parent-Span-ID"] = context.parent_span_id
        
        if context.user_id:
            carrier["X-User-ID"] = context.user_id
        
        if context.request_id:
            carrier["X-Request-ID"] = context.request_id
        
        if context.correlation_id:
            carrier["X-Correlation-ID"] = context.correlation_id
        
        # Add attributes as JSON
        if context.attributes:
            carrier["X-Context-Attributes"] = json.dumps(context.attributes)
    
    def extract_context(self, carrier: Dict[str, str]) -> Optional[TraceContext]:
        """
        Extract trace context from carrier
        
        Args:
            carrier: Carrier dictionary (e.g., HTTP headers)
            
        Returns:
            Extracted trace context or None
        """
        try:
            trace_id = carrier.get("X-Trace-ID")
            span_id = carrier.get("X-Span-ID")
            
            if not trace_id or not span_id:
                return None
            
            context_type = ContextType(carrier.get("X-Context-Type", ContextType.REQUEST.value))
            
            context = TraceContext(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=carrier.get("X-Parent-Span-ID"),
                context_type=context_type,
                user_id=carrier.get("X-User-ID"),
                request_id=carrier.get("X-Request-ID"),
                correlation_id=carrier.get("X-Correlation-ID")
            )
            
            # Extract attributes
            attributes_json = carrier.get("X-Context-Attributes")
            if attributes_json:
                try:
                    context.attributes = json.loads(attributes_json)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse context attributes: {attributes_json}")
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to extract context from carrier: {e}")
            return None
    
    def get_all_contexts(self) -> Dict[str, TraceContext]:
        """Get all active contexts (for debugging)"""
        with self._lock:
            return self._contexts.copy()
    
    async def get_all_async_contexts(self) -> Dict[str, TraceContext]:
        """Get all active async contexts (for debugging)"""
        async with self._async_lock:
            return self._async_contexts.copy()


# Global context manager instance
_context_manager = TraceContextManager()


def get_context_manager() -> TraceContextManager:
    """Get global context manager instance"""
    return _context_manager


def set_context(context: TraceContext):
    """Set trace context for current thread"""
    _context_manager.set_context(context)


def get_context() -> Optional[TraceContext]:
    """Get trace context for current thread"""
    return _context_manager.get_context()


def clear_context():
    """Clear trace context for current thread"""
    _context_manager.clear_context()


async def set_async_context(context: TraceContext):
    """Set trace context for current async task"""
    await _context_manager.set_async_context(context)


async def get_async_context() -> Optional[TraceContext]:
    """Get trace context for current async task"""
    return await _context_manager.get_async_context()


async def clear_async_context():
    """Clear trace context for current async task"""
    await _context_manager.clear_async_context()


def create_child_context(
    context_type: ContextType = ContextType.REQUEST,
    attributes: Optional[Dict[str, Any]] = None
) -> TraceContext:
    """Create child context from current context"""
    return _context_manager.create_child_context(context_type, attributes)


async def create_async_child_context(
    context_type: ContextType = ContextType.REQUEST,
    attributes: Optional[Dict[str, Any]] = None
) -> TraceContext:
    """Create child context from current async context"""
    return await _context_manager.create_async_child_context(context_type, attributes)


def inject_context(context: TraceContext, carrier: Dict[str, str]):
    """Inject trace context into carrier"""
    _context_manager.inject_context(context, carrier)


def extract_context(carrier: Dict[str, str]) -> Optional[TraceContext]:
    """Extract trace context from carrier"""
    return _context_manager.extract_context(carrier)


@contextmanager
def trace_context(
    context_type: ContextType = ContextType.REQUEST,
    attributes: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None
):
    """
    Context manager for trace context creation
    
    Args:
        context_type: Type of context
        attributes: Additional attributes
        user_id: User ID for context
        request_id: Request ID for context
        
    Yields:
        Trace context
    """
    # Create new context
    context = TraceContext(
        trace_id=str(uuid.uuid4()),
        span_id=str(uuid.uuid4()),
        context_type=context_type,
        user_id=user_id,
        request_id=request_id,
        attributes=attributes or {}
    )
    
    # Set context
    set_context(context)
    
    try:
        yield context
    finally:
        # Clear context
        clear_context()


def trace_context_decorator(
    context_type: ContextType = ContextType.REQUEST,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Decorator for automatic trace context creation
    
    Args:
        context_type: Type of context
        attributes: Additional attributes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create context from function info
            func_attributes = {
                "function.name": func.__name__,
                "function.module": func.__module__,
                **(attributes or {})
            }
            
            with trace_context(context_type, func_attributes):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def async_trace_context_decorator(
    context_type: ContextType = ContextType.REQUEST,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Decorator for automatic async trace context creation
    
    Args:
        context_type: Type of context
        attributes: Additional attributes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create context from function info
            func_attributes = {
                "function.name": func.__name__,
                "function.module": func.__module__,
                **(attributes or {})
            }
            
            # Create async context
            context = await create_async_child_context(context_type, func_attributes)
            await set_async_context(context)
            
            try:
                return await func(*args, **kwargs)
            finally:
                await clear_async_context()
        
        return wrapper
    return decorator


class TraceContextMiddleware:
    """
    Middleware for automatic trace context management in web frameworks
    """
    
    def __init__(self, app, context_type: ContextType = ContextType.REQUEST):
        self.app = app
        self.context_type = context_type
    
    def __call__(self, environ, start_response):
        # Extract context from headers
        headers = {k.lower(): v for k, v in environ.items() if k.startswith('HTTP_')}
        carrier = {k.replace('http_', '').replace('_', '-').title(): v for k, v in headers.items()}
        
        # Extract or create context
        context = extract_context(carrier)
        if not context:
            context = TraceContext(
                trace_id=str(uuid.uuid4()),
                span_id=str(uuid.uuid4()),
                context_type=self.context_type,
                request_id=environ.get('HTTP_X_REQUEST_ID')
            )
        
        # Set context
        set_context(context)
        
        # Add trace headers to response
        def custom_start_response(status, headers, exc_info=None):
            trace_headers = [
                ('X-Trace-ID', context.trace_id),
                ('X-Span-ID', context.span_id),
                ('X-Context-Type', context.context_type.value)
            ]
            headers.extend(trace_headers)
            return start_response(status, headers, exc_info)
        
        try:
            return self.app(environ, custom_start_response)
        finally:
            clear_context()


# Utility functions for common context operations
def get_trace_id() -> Optional[str]:
    """Get current trace ID"""
    context = get_context()
    return context.trace_id if context else None


def get_span_id() -> Optional[str]:
    """Get current span ID"""
    context = get_context()
    return context.span_id if context else None


def get_user_id() -> Optional[str]:
    """Get current user ID"""
    context = get_context()
    return context.user_id if context else None


def get_request_id() -> Optional[str]:
    """Get current request ID"""
    context = get_context()
    return context.request_id if context else None


def add_context_attribute(key: str, value: Any):
    """Add attribute to current context"""
    context = get_context()
    if context:
        context.add_attribute(key, value)


def get_context_attribute(key: str, default: Any = None) -> Any:
    """Get attribute from current context"""
    context = get_context()
    return context.get_attribute(key, default) if context else default


def log_with_context(message: str, level: str = "INFO", **kwargs):
    """
    Log message with current trace context
    
    Args:
        message: Log message
        level: Log level
        **kwargs: Additional log fields
    """
    context = get_context()
    if context:
        log_data = {
            "trace_id": context.trace_id,
            "span_id": context.span_id,
            "context_type": context.context_type.value,
            **kwargs
        }
        
        if context.user_id:
            log_data["user_id"] = context.user_id
        
        if context.request_id:
            log_data["request_id"] = context.request_id
        
        log_message = f"[{context.trace_id}] {message}"
        logger.log(getattr(logging, level.upper()), log_message, extra=log_data)
    else:
        logger.log(getattr(logging, level.upper()), message, extra=kwargs) 