"""
🧪 Trace Context Management Tests
📅 Generated: 2025-01-27
🎯 Purpose: Comprehensive tests for trace context management system
📋 Tracing ID: TEST_TRACE_CONTEXT_002_20250127
"""

import unittest
import asyncio
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.observability.trace_context import (
    TraceContext, ContextType, TraceContextManager, get_context_manager,
    set_context, get_context, clear_context, create_child_context,
    set_async_context, get_async_context, clear_async_context,
    create_async_child_context, inject_context, extract_context,
    trace_context, trace_context_decorator, async_trace_context_decorator,
    TraceContextMiddleware, get_trace_id, get_span_id, get_user_id,
    get_request_id, add_context_attribute, get_context_attribute,
    log_with_context
)


class TestTraceContext(unittest.TestCase):
    """Test cases for TraceContext class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.context = TraceContext(
            trace_id="test-trace-123",
            span_id="test-span-456",
            parent_span_id="parent-span-789",
            context_type=ContextType.REQUEST,
            user_id="user-123",
            request_id="request-456",
            correlation_id="correlation-789"
        )
    
    def test_context_creation(self):
        """Test trace context creation"""
        self.assertEqual(self.context.trace_id, "test-trace-123")
        self.assertEqual(self.context.span_id, "test-span-456")
        self.assertEqual(self.context.parent_span_id, "parent-span-789")
        self.assertEqual(self.context.context_type, ContextType.REQUEST)
        self.assertEqual(self.context.user_id, "user-123")
        self.assertEqual(self.context.request_id, "request-456")
        self.assertEqual(self.context.correlation_id, "correlation-789")
        self.assertIsInstance(self.context.attributes, dict)
        self.assertIsInstance(self.context.metadata, dict)
        self.assertIsInstance(self.context.start_time, float)
    
    def test_to_dict(self):
        """Test converting context to dictionary"""
        context_dict = self.context.to_dict()
        
        self.assertEqual(context_dict["trace_id"], "test-trace-123")
        self.assertEqual(context_dict["span_id"], "test-span-456")
        self.assertEqual(context_dict["parent_span_id"], "parent-span-789")
        self.assertEqual(context_dict["context_type"], "request")
        self.assertEqual(context_dict["user_id"], "user-123")
        self.assertEqual(context_dict["request_id"], "request-456")
        self.assertEqual(context_dict["correlation_id"], "correlation-789")
        self.assertIsInstance(context_dict["attributes"], dict)
        self.assertIsInstance(context_dict["metadata"], dict)
        self.assertIsInstance(context_dict["start_time"], float)
    
    def test_from_dict(self):
        """Test creating context from dictionary"""
        context_dict = {
            "trace_id": "new-trace-123",
            "span_id": "new-span-456",
            "parent_span_id": "new-parent-789",
            "context_type": "background",
            "user_id": "new-user-123",
            "request_id": "new-request-456",
            "correlation_id": "new-correlation-789",
            "attributes": {"key1": "value1"},
            "metadata": {"meta1": "meta_value1"},
            "start_time": 1234567890.0
        }
        
        new_context = TraceContext.from_dict(context_dict)
        
        self.assertEqual(new_context.trace_id, "new-trace-123")
        self.assertEqual(new_context.span_id, "new-span-456")
        self.assertEqual(new_context.parent_span_id, "new-parent-789")
        self.assertEqual(new_context.context_type, ContextType.BACKGROUND)
        self.assertEqual(new_context.user_id, "new-user-123")
        self.assertEqual(new_context.request_id, "new-request-456")
        self.assertEqual(new_context.correlation_id, "new-correlation-789")
        self.assertEqual(new_context.attributes["key1"], "value1")
        self.assertEqual(new_context.metadata["meta1"], "meta_value1")
        self.assertEqual(new_context.start_time, 1234567890.0)
    
    def test_add_attribute(self):
        """Test adding attribute to context"""
        self.context.add_attribute("test_key", "test_value")
        self.assertEqual(self.context.attributes["test_key"], "test_value")
    
    def test_get_attribute(self):
        """Test getting attribute from context"""
        self.context.add_attribute("test_key", "test_value")
        value = self.context.get_attribute("test_key")
        self.assertEqual(value, "test_value")
    
    def test_get_attribute_default(self):
        """Test getting attribute with default value"""
        value = self.context.get_attribute("non_existent_key", "default_value")
        self.assertEqual(value, "default_value")
    
    def test_add_metadata(self):
        """Test adding metadata to context"""
        self.context.add_metadata("test_meta", "test_meta_value")
        self.assertEqual(self.context.metadata["test_meta"], "test_meta_value")
    
    def test_get_metadata(self):
        """Test getting metadata from context"""
        self.context.add_metadata("test_meta", "test_meta_value")
        value = self.context.get_metadata("test_meta")
        self.assertEqual(value, "test_meta_value")
    
    def test_get_metadata_default(self):
        """Test getting metadata with default value"""
        value = self.context.get_metadata("non_existent_meta", "default_meta")
        self.assertEqual(value, "default_meta")


class TestTraceContextManager(unittest.TestCase):
    """Test cases for TraceContextManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = TraceContextManager()
        self.context = TraceContext(
            trace_id="test-trace-123",
            span_id="test-span-456",
            context_type=ContextType.REQUEST
        )
    
    def test_set_context(self):
        """Test setting context for current thread"""
        self.manager.set_context(self.context)
        retrieved_context = self.manager.get_context()
        
        self.assertIsNotNone(retrieved_context)
        self.assertEqual(retrieved_context.trace_id, "test-trace-123")
        self.assertEqual(retrieved_context.span_id, "test-span-456")
    
    def test_get_context_none(self):
        """Test getting context when none is set"""
        context = self.manager.get_context()
        self.assertIsNone(context)
    
    def test_clear_context(self):
        """Test clearing context"""
        self.manager.set_context(self.context)
        self.manager.clear_context()
        
        context = self.manager.get_context()
        self.assertIsNone(context)
    
    def test_create_child_context(self):
        """Test creating child context"""
        self.manager.set_context(self.context)
        child_context = self.manager.create_child_context(ContextType.BACKGROUND)
        
        self.assertEqual(child_context.trace_id, self.context.trace_id)
        self.assertEqual(child_context.parent_span_id, self.context.span_id)
        self.assertEqual(child_context.context_type, ContextType.BACKGROUND)
        self.assertNotEqual(child_context.span_id, self.context.span_id)
    
    def test_create_child_context_no_parent(self):
        """Test creating child context without parent"""
        child_context = self.manager.create_child_context(ContextType.BACKGROUND)
        
        self.assertIsNotNone(child_context.trace_id)
        self.assertIsNotNone(child_context.span_id)
        self.assertEqual(child_context.context_type, ContextType.BACKGROUND)
        self.assertIsNone(child_context.parent_span_id)
    
    def test_inject_context(self):
        """Test injecting context into carrier"""
        carrier = {}
        self.manager.inject_context(self.context, carrier)
        
        self.assertIn("X-Trace-ID", carrier)
        self.assertIn("X-Span-ID", carrier)
        self.assertIn("X-Context-Type", carrier)
        self.assertEqual(carrier["X-Trace-ID"], "test-trace-123")
        self.assertEqual(carrier["X-Span-ID"], "test-span-456")
        self.assertEqual(carrier["X-Context-Type"], "request")
    
    def test_inject_context_with_optional_fields(self):
        """Test injecting context with optional fields"""
        context_with_optional = TraceContext(
            trace_id="test-trace-123",
            span_id="test-span-456",
            parent_span_id="parent-span-789",
            context_type=ContextType.REQUEST,
            user_id="user-123",
            request_id="request-456",
            correlation_id="correlation-789",
            attributes={"attr1": "value1"}
        )
        
        carrier = {}
        self.manager.inject_context(context_with_optional, carrier)
        
        self.assertIn("X-Parent-Span-ID", carrier)
        self.assertIn("X-User-ID", carrier)
        self.assertIn("X-Request-ID", carrier)
        self.assertIn("X-Correlation-ID", carrier)
        self.assertIn("X-Context-Attributes", carrier)
    
    def test_extract_context(self):
        """Test extracting context from carrier"""
        carrier = {
            "X-Trace-ID": "extracted-trace-123",
            "X-Span-ID": "extracted-span-456",
            "X-Context-Type": "background",
            "X-Parent-Span-ID": "extracted-parent-789",
            "X-User-ID": "extracted-user-123",
            "X-Request-ID": "extracted-request-456",
            "X-Correlation-ID": "extracted-correlation-789",
            "X-Context-Attributes": '{"attr1": "value1"}'
        }
        
        extracted_context = self.manager.extract_context(carrier)
        
        self.assertIsNotNone(extracted_context)
        self.assertEqual(extracted_context.trace_id, "extracted-trace-123")
        self.assertEqual(extracted_context.span_id, "extracted-span-456")
        self.assertEqual(extracted_context.context_type, ContextType.BACKGROUND)
        self.assertEqual(extracted_context.parent_span_id, "extracted-parent-789")
        self.assertEqual(extracted_context.user_id, "extracted-user-123")
        self.assertEqual(extracted_context.request_id, "extracted-request-456")
        self.assertEqual(extracted_context.correlation_id, "extracted-correlation-789")
        self.assertEqual(extracted_context.attributes["attr1"], "value1")
    
    def test_extract_context_invalid(self):
        """Test extracting context from invalid carrier"""
        # Missing required fields
        carrier = {"X-Trace-ID": "trace-123"}
        extracted_context = self.manager.extract_context(carrier)
        self.assertIsNone(extracted_context)
        
        # Invalid JSON in attributes
        carrier = {
            "X-Trace-ID": "trace-123",
            "X-Span-ID": "span-456",
            "X-Context-Attributes": "invalid json"
        }
        extracted_context = self.manager.extract_context(carrier)
        self.assertIsNotNone(extracted_context)  # Should still extract basic info
    
    def test_get_all_contexts(self):
        """Test getting all active contexts"""
        self.manager.set_context(self.context)
        all_contexts = self.manager.get_all_contexts()
        
        self.assertIsInstance(all_contexts, dict)
        self.assertGreater(len(all_contexts), 0)


class TestAsyncTraceContextManager(unittest.TestCase):
    """Test cases for async trace context management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = TraceContextManager()
        self.context = TraceContext(
            trace_id="async-trace-123",
            span_id="async-span-456",
            context_type=ContextType.REQUEST
        )
    
    def test_set_async_context(self):
        """Test setting async context"""
        async def test_async_context():
            await self.manager.set_async_context(self.context)
            retrieved_context = await self.manager.get_async_context()
            
            self.assertIsNotNone(retrieved_context)
            self.assertEqual(retrieved_context.trace_id, "async-trace-123")
            self.assertEqual(retrieved_context.span_id, "async-span-456")
        
        asyncio.run(test_async_context())
    
    def test_get_async_context_none(self):
        """Test getting async context when none is set"""
        async def test_no_context():
            context = await self.manager.get_async_context()
            self.assertIsNone(context)
        
        asyncio.run(test_no_context())
    
    def test_clear_async_context(self):
        """Test clearing async context"""
        async def test_clear_context():
            await self.manager.set_async_context(self.context)
            await self.manager.clear_async_context()
            
            context = await self.manager.get_async_context()
            self.assertIsNone(context)
        
        asyncio.run(test_clear_context())
    
    def test_create_async_child_context(self):
        """Test creating async child context"""
        async def test_child_context():
            await self.manager.set_async_context(self.context)
            child_context = await self.manager.create_async_child_context(ContextType.BACKGROUND)
            
            self.assertEqual(child_context.trace_id, self.context.trace_id)
            self.assertEqual(child_context.parent_span_id, self.context.span_id)
            self.assertEqual(child_context.context_type, ContextType.BACKGROUND)
            self.assertNotEqual(child_context.span_id, self.context.span_id)
        
        asyncio.run(test_child_context())
    
    def test_create_async_child_context_no_parent(self):
        """Test creating async child context without parent"""
        async def test_no_parent():
            child_context = await self.manager.create_async_child_context(ContextType.BACKGROUND)
            
            self.assertIsNotNone(child_context.trace_id)
            self.assertIsNotNone(child_context.span_id)
            self.assertEqual(child_context.context_type, ContextType.BACKGROUND)
            self.assertIsNone(child_context.parent_span_id)
        
        asyncio.run(test_no_parent())
    
    def test_get_all_async_contexts(self):
        """Test getting all active async contexts"""
        async def test_all_contexts():
            await self.manager.set_async_context(self.context)
            all_contexts = await self.manager.get_all_async_contexts()
            
            self.assertIsInstance(all_contexts, dict)
            self.assertGreater(len(all_contexts), 0)
        
        asyncio.run(test_all_contexts())


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global context functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.context = TraceContext(
            trace_id="global-trace-123",
            span_id="global-span-456",
            context_type=ContextType.REQUEST
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        clear_context()
    
    def test_set_get_clear_context(self):
        """Test global context set/get/clear operations"""
        set_context(self.context)
        retrieved_context = get_context()
        
        self.assertIsNotNone(retrieved_context)
        self.assertEqual(retrieved_context.trace_id, "global-trace-123")
        
        clear_context()
        context_after_clear = get_context()
        self.assertIsNone(context_after_clear)
    
    def test_create_child_context(self):
        """Test global child context creation"""
        set_context(self.context)
        child_context = create_child_context(ContextType.BACKGROUND)
        
        self.assertEqual(child_context.trace_id, self.context.trace_id)
        self.assertEqual(child_context.parent_span_id, self.context.span_id)
        self.assertEqual(child_context.context_type, ContextType.BACKGROUND)
    
    def test_inject_extract_context(self):
        """Test global context injection and extraction"""
        carrier = {}
        inject_context(self.context, carrier)
        
        self.assertIn("X-Trace-ID", carrier)
        self.assertIn("X-Span-ID", carrier)
        
        extracted_context = extract_context(carrier)
        self.assertIsNotNone(extracted_context)
        self.assertEqual(extracted_context.trace_id, "global-trace-123")
    
    def test_async_context_functions(self):
        """Test global async context functions"""
        async def test_async_functions():
            await set_async_context(self.context)
            retrieved_context = await get_async_context()
            
            self.assertIsNotNone(retrieved_context)
            self.assertEqual(retrieved_context.trace_id, "global-trace-123")
            
            await clear_async_context()
            context_after_clear = await get_async_context()
            self.assertIsNone(context_after_clear)
        
        asyncio.run(test_async_functions())
    
    def test_create_async_child_context(self):
        """Test global async child context creation"""
        async def test_async_child():
            await set_async_context(self.context)
            child_context = await create_async_child_context(ContextType.BACKGROUND)
            
            self.assertEqual(child_context.trace_id, self.context.trace_id)
            self.assertEqual(child_context.parent_span_id, self.context.span_id)
            self.assertEqual(child_context.context_type, ContextType.BACKGROUND)
        
        asyncio.run(test_async_child())


class TestContextManagers(unittest.TestCase):
    """Test cases for context managers"""
    
    def test_trace_context_manager(self):
        """Test trace context manager"""
        with trace_context(ContextType.REQUEST, {"test_key": "test_value"}) as context:
            self.assertIsNotNone(context)
            self.assertEqual(context.context_type, ContextType.REQUEST)
            self.assertEqual(context.attributes["test_key"], "test_value")
            
            # Context should be available globally
            global_context = get_context()
            self.assertIsNotNone(global_context)
            self.assertEqual(global_context.trace_id, context.trace_id)
        
        # Context should be cleared after exit
        context_after_exit = get_context()
        self.assertIsNone(context_after_exit)
    
    def test_trace_context_manager_with_exception(self):
        """Test trace context manager with exception"""
        with self.assertRaises(ValueError):
            with trace_context(ContextType.REQUEST) as context:
                self.assertIsNotNone(context)
                raise ValueError("Test exception")
        
        # Context should still be cleared after exception
        context_after_exception = get_context()
        self.assertIsNone(context_after_exception)


class TestDecorators(unittest.TestCase):
    """Test cases for context decorators"""
    
    def test_trace_context_decorator(self):
        """Test trace context decorator"""
        @trace_context_decorator(ContextType.REQUEST, {"decorator_key": "decorator_value"})
        def test_function():
            context = get_context()
            self.assertIsNotNone(context)
            self.assertEqual(context.context_type, ContextType.REQUEST)
            self.assertEqual(context.attributes["decorator_key"], "decorator_value")
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        
        # Context should be cleared after function execution
        context_after_function = get_context()
        self.assertIsNone(context_after_function)
    
    def test_async_trace_context_decorator(self):
        """Test async trace context decorator"""
        @async_trace_context_decorator(ContextType.BACKGROUND, {"async_key": "async_value"})
        async def test_async_function():
            context = await get_async_context()
            self.assertIsNotNone(context)
            self.assertEqual(context.context_type, ContextType.BACKGROUND)
            self.assertEqual(context.attributes["async_key"], "async_value")
            return "async_success"
        
        async def run_test():
            result = await test_async_function()
            self.assertEqual(result, "async_success")
            
            # Context should be cleared after function execution
            context_after_function = await get_async_context()
            self.assertIsNone(context_after_function)
        
        asyncio.run(run_test())


class TestMiddleware(unittest.TestCase):
    """Test cases for TraceContextMiddleware"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = Mock()
        self.middleware = TraceContextMiddleware(self.app, ContextType.REQUEST)
    
    def test_middleware_with_trace_headers(self):
        """Test middleware with trace headers"""
        environ = {
            'HTTP_X_TRACE_ID': 'middleware-trace-123',
            'HTTP_X_SPAN_ID': 'middleware-span-456',
            'HTTP_X_CONTEXT_TYPE': 'request'
        }
        
        start_response = Mock()
        
        self.app.return_value = ['response']
        
        # Mock the middleware call
        with patch('infrastructure.observability.trace_context.set_context') as mock_set:
            with patch('infrastructure.observability.trace_context.clear_context') as mock_clear:
                result = self.middleware(environ, start_response)
                
                # Verify context was set and cleared
                mock_set.assert_called_once()
                mock_clear.assert_called_once()
                
                # Verify response headers were added
                start_response.assert_called_once()
                call_args = start_response.call_args[0]
                headers = call_args[1]
                
                # Find trace headers in response
                trace_headers = [h for h in headers if h[0].startswith('X-')]
                self.assertGreater(len(trace_headers), 0)
    
    def test_middleware_without_trace_headers(self):
        """Test middleware without trace headers"""
        environ = {}
        start_response = Mock()
        
        self.app.return_value = ['response']
        
        with patch('infrastructure.observability.trace_context.set_context') as mock_set:
            with patch('infrastructure.observability.trace_context.clear_context') as mock_clear:
                result = self.middleware(environ, start_response)
                
                # Verify context was still set and cleared
                mock_set.assert_called_once()
                mock_clear.assert_called_once()


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.context = TraceContext(
            trace_id="utility-trace-123",
            span_id="utility-span-456",
            context_type=ContextType.REQUEST,
            user_id="utility-user-123",
            request_id="utility-request-456"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        clear_context()
    
    def test_get_trace_id(self):
        """Test getting trace ID"""
        set_context(self.context)
        trace_id = get_trace_id()
        self.assertEqual(trace_id, "utility-trace-123")
    
    def test_get_span_id(self):
        """Test getting span ID"""
        set_context(self.context)
        span_id = get_span_id()
        self.assertEqual(span_id, "utility-span-456")
    
    def test_get_user_id(self):
        """Test getting user ID"""
        set_context(self.context)
        user_id = get_user_id()
        self.assertEqual(user_id, "utility-user-123")
    
    def test_get_request_id(self):
        """Test getting request ID"""
        set_context(self.context)
        request_id = get_request_id()
        self.assertEqual(request_id, "utility-request-456")
    
    def test_add_context_attribute(self):
        """Test adding context attribute"""
        set_context(self.context)
        add_context_attribute("test_attr", "test_value")
        
        value = get_context_attribute("test_attr")
        self.assertEqual(value, "test_value")
    
    def test_get_context_attribute_default(self):
        """Test getting context attribute with default"""
        set_context(self.context)
        value = get_context_attribute("non_existent", "default_value")
        self.assertEqual(value, "default_value")
    
    def test_log_with_context(self):
        """Test logging with context"""
        set_context(self.context)
        
        # Should not raise any exceptions
        log_with_context("Test log message", "INFO", extra_key="extra_value")
        self.assertTrue(True)
    
    def test_log_without_context(self):
        """Test logging without context"""
        # Should not raise any exceptions even without context
        log_with_context("Test log message without context", "INFO")
        self.assertTrue(True)


class TestThreadSafety(unittest.TestCase):
    """Test cases for thread safety"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = TraceContextManager()
        self.results = []
        self.lock = threading.Lock()
    
    def test_thread_safety(self):
        """Test thread safety of context manager"""
        def worker(thread_id):
            context = TraceContext(
                trace_id=f"thread-{thread_id}-trace",
                span_id=f"thread-{thread_id}-span",
                context_type=ContextType.REQUEST
            )
            
            self.manager.set_context(context)
            retrieved_context = self.manager.get_context()
            
            with self.lock:
                self.results.append({
                    'thread_id': thread_id,
                    'trace_id': retrieved_context.trace_id if retrieved_context else None
                })
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify each thread got its own context
        self.assertEqual(len(self.results), 5)
        for result in self.results:
            self.assertIsNotNone(result['trace_id'])
            self.assertIn(f"thread-{result['thread_id']}-trace", result['trace_id'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 