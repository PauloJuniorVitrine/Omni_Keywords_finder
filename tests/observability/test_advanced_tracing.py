"""
🧪 Advanced Distributed Tracing Tests
📅 Generated: 2025-01-27
🎯 Purpose: Comprehensive tests for distributed tracing system
📋 Tracing ID: TEST_ADVANCED_TRACING_001_20250127
"""

import unittest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.observability.advanced_tracing import (
    AdvancedTracing, TracingConfig, TracingBackend, SpanType, StatusCode,
    FallbackSpan, get_tracing, init_tracing, trace_function, trace_async_function,
    start_span, end_span, span_context
)
from infrastructure.observability.trace_context import (
    TraceContext, ContextType, TraceContextManager, get_context_manager,
    set_context, get_context, clear_context, create_child_context
)


class TestAdvancedTracing(unittest.TestCase):
    """Test cases for AdvancedTracing class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="testing",
            backend=TracingBackend.CONSOLE,
            endpoint="http://localhost:14268/api/traces"
        )
        self.tracing = AdvancedTracing(self.config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self.tracing, 'shutdown'):
            self.tracing.shutdown()
    
    def test_init_with_config(self):
        """Test initialization with configuration"""
        self.assertEqual(self.tracing.config.service_name, "test-service")
        self.assertEqual(self.tracing.config.service_version, "1.0.0")
        self.assertEqual(self.tracing.config.environment, "testing")
        self.assertEqual(self.tracing.config.backend, TracingBackend.CONSOLE)
    
    def test_start_span_basic(self):
        """Test basic span creation"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        
        self.assertIsNotNone(span)
        self.assertTrue(hasattr(span, 'name') or hasattr(span, 'get_span_context'))
    
    def test_start_span_with_attributes(self):
        """Test span creation with attributes"""
        attributes = {"test_key": "test_value", "number": 42}
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC, attributes)
        
        self.assertIsNotNone(span)
    
    def test_end_span_success(self):
        """Test successful span ending"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        self.tracing.end_span(span, StatusCode.OK)
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_end_span_error(self):
        """Test span ending with error"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        self.tracing.end_span(span, StatusCode.ERROR, "Test error message")
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_add_event_to_span(self):
        """Test adding events to span"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        self.tracing.add_event(span, "test_event", {"event_key": "event_value"})
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_add_attribute_to_span(self):
        """Test adding attributes to span"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        self.tracing.add_attribute(span, "test_attr", "test_value")
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_span_context_manager(self):
        """Test span context manager"""
        with self.tracing.span_context("test_context", SpanType.BUSINESS_LOGIC) as span:
            self.assertIsNotNone(span)
            # Add some work
            time.sleep(0.001)
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_span_context_manager_with_exception(self):
        """Test span context manager with exception"""
        with self.assertRaises(ValueError):
            with self.tracing.span_context("test_context", SpanType.BUSINESS_LOGIC) as span:
                self.assertIsNotNone(span)
                raise ValueError("Test exception")
    
    def test_get_trace_id(self):
        """Test getting trace ID from span"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        trace_id = self.tracing.get_trace_id(span)
        
        self.assertIsNotNone(trace_id)
        self.assertIsInstance(trace_id, str)
    
    def test_get_span_id(self):
        """Test getting span ID from span"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        span_id = self.tracing.get_span_id(span)
        
        self.assertIsNotNone(span_id)
        self.assertIsInstance(span_id, str)
    
    def test_inject_context(self):
        """Test context injection"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        carrier = {}
        
        self.tracing.inject_context(span, carrier)
        
        # Should add trace headers to carrier
        self.assertIn("X-Trace-ID", carrier)
        self.assertIn("X-Span-ID", carrier)
    
    def test_extract_context(self):
        """Test context extraction"""
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        carrier = {}
        
        self.tracing.inject_context(span, carrier)
        extracted_span = self.tracing.extract_context(carrier)
        
        self.assertIsNotNone(extracted_span)


class TestFallbackSpan(unittest.TestCase):
    """Test cases for FallbackSpan class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.span = FallbackSpan("test_span", SpanType.BUSINESS_LOGIC, {})
    
    def test_fallback_span_creation(self):
        """Test fallback span creation"""
        self.assertEqual(self.span.name, "test_span")
        self.assertEqual(self.span.span_type, SpanType.BUSINESS_LOGIC)
        self.assertIsInstance(self.span.attributes, dict)
        self.assertIsInstance(self.span.trace_id, str)
        self.assertIsInstance(self.span.span_id, str)
    
    def test_set_attribute(self):
        """Test setting span attribute"""
        self.span.set_attribute("test_key", "test_value")
        self.assertEqual(self.span.attributes["test_key"], "test_value")
    
    def test_add_attribute(self):
        """Test adding span attribute"""
        self.span.add_attribute("test_key", "test_value")
        self.assertEqual(self.span.attributes["test_key"], "test_value")
    
    def test_add_event(self):
        """Test adding event to span"""
        self.span.add_event("test_event", {"event_key": "event_value"})
        
        self.assertEqual(len(self.span.events), 1)
        self.assertEqual(self.span.events[0]["name"], "test_event")
        self.assertEqual(self.span.events[0]["attributes"]["event_key"], "event_value")
    
    def test_set_status(self):
        """Test setting span status"""
        self.span.set_status(StatusCode.ERROR, "Test error")
        
        self.assertEqual(self.span.status, StatusCode.ERROR)
        self.assertEqual(self.span.error_message, "Test error")
    
    def test_end_span(self):
        """Test ending span"""
        start_time = self.span.start_time
        self.span.end(StatusCode.OK, "Test completion")
        
        self.assertIsNotNone(self.span.end_time)
        self.assertGreater(self.span.end_time, start_time)
        self.assertEqual(self.span.status, StatusCode.OK)


class TestTraceDecorators(unittest.TestCase):
    """Test cases for trace decorators"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="testing",
            backend=TracingBackend.CONSOLE
        )
        init_tracing(self.config)
    
    def test_trace_function_decorator(self):
        """Test trace function decorator"""
        @trace_function(SpanType.BUSINESS_LOGIC)
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        self.assertEqual(result, 5)
    
    def test_trace_function_with_exception(self):
        """Test trace function decorator with exception"""
        @trace_function(SpanType.BUSINESS_LOGIC)
        def test_function():
            raise ValueError("Test exception")
        
        with self.assertRaises(ValueError):
            test_function()
    
    def test_trace_async_function_decorator(self):
        """Test trace async function decorator"""
        @trace_async_function(SpanType.BUSINESS_LOGIC)
        async def test_async_function(x, y):
            await asyncio.sleep(0.001)
            return x + y
        
        result = asyncio.run(test_async_function(2, 3))
        self.assertEqual(result, 5)
    
    def test_trace_async_function_with_exception(self):
        """Test trace async function decorator with exception"""
        @trace_async_function(SpanType.BUSINESS_LOGIC)
        async def test_async_function():
            await asyncio.sleep(0.001)
            raise ValueError("Test exception")
        
        with self.assertRaises(ValueError):
            asyncio.run(test_async_function())


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global tracing functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = TracingConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="testing",
            backend=TracingBackend.CONSOLE
        )
        init_tracing(self.config)
    
    def test_get_tracing(self):
        """Test getting global tracing instance"""
        tracing = get_tracing()
        self.assertIsInstance(tracing, AdvancedTracing)
    
    def test_start_span_global(self):
        """Test global start_span function"""
        span = start_span("test_span", SpanType.BUSINESS_LOGIC)
        self.assertIsNotNone(span)
    
    def test_end_span_global(self):
        """Test global end_span function"""
        span = start_span("test_span", SpanType.BUSINESS_LOGIC)
        end_span(span, StatusCode.OK)
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_span_context_global(self):
        """Test global span_context function"""
        with span_context("test_context", SpanType.BUSINESS_LOGIC) as span:
            self.assertIsNotNone(span)
            time.sleep(0.001)
        
        # Should not raise any exceptions
        self.assertTrue(True)


class TestTraceContextIntegration(unittest.TestCase):
    """Test cases for trace context integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.context_manager = TraceContextManager()
    
    def test_context_integration(self):
        """Test integration between tracing and context"""
        # Create trace context
        context = TraceContext(
            trace_id="test-trace-123",
            span_id="test-span-456",
            context_type=ContextType.REQUEST
        )
        
        # Set context
        set_context(context)
        
        # Start span (should use context)
        span = start_span("test_span", SpanType.BUSINESS_LOGIC)
        
        # Verify span has context information
        self.assertIsNotNone(span)
        
        # Clean up
        clear_context()
    
    def test_context_propagation(self):
        """Test context propagation through spans"""
        # Create parent context
        parent_context = TraceContext(
            trace_id="parent-trace-123",
            span_id="parent-span-456",
            context_type=ContextType.REQUEST
        )
        
        # Set parent context
        set_context(parent_context)
        
        # Create child context
        child_context = create_child_context(ContextType.BACKGROUND)
        
        # Verify child inherits from parent
        self.assertEqual(child_context.trace_id, parent_context.trace_id)
        self.assertEqual(child_context.parent_span_id, parent_context.span_id)
        self.assertNotEqual(child_context.span_id, parent_context.span_id)
        
        # Clean up
        clear_context()


class TestTracingBackends(unittest.TestCase):
    """Test cases for different tracing backends"""
    
    def test_console_backend(self):
        """Test console backend configuration"""
        config = TracingConfig(
            service_name="test-service",
            backend=TracingBackend.CONSOLE
        )
        tracing = AdvancedTracing(config)
        
        span = tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        tracing.end_span(span, StatusCode.OK)
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    @patch('infrastructure.observability.advanced_tracing.OPENTELEMETRY_AVAILABLE', False)
    def test_fallback_when_opentelemetry_unavailable(self):
        """Test fallback when OpenTelemetry is not available"""
        config = TracingConfig(
            service_name="test-service",
            backend=TracingBackend.JAEGER
        )
        tracing = AdvancedTracing(config)
        
        span = tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        
        # Should create fallback span
        self.assertIsInstance(span, FallbackSpan)
        
        tracing.end_span(span, StatusCode.OK)


class TestTracingPerformance(unittest.TestCase):
    """Test cases for tracing performance"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = TracingConfig(
            service_name="test-service",
            backend=TracingBackend.CONSOLE
        )
        self.tracing = AdvancedTracing(self.config)
    
    def test_span_creation_performance(self):
        """Test span creation performance"""
        start_time = time.time()
        
        for _ in range(100):
            span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
            self.tracing.end_span(span, StatusCode.OK)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 spans in reasonable time (< 1 second)
        self.assertLess(duration, 1.0)
    
    def test_concurrent_span_creation(self):
        """Test concurrent span creation"""
        import threading
        
        def create_spans():
            for _ in range(10):
                span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
                self.tracing.end_span(span, StatusCode.OK)
        
        threads = [threading.Thread(target=create_spans) for _ in range(5)]
        
        start_time = time.time()
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 50 spans in reasonable time (< 2 seconds)
        self.assertLess(duration, 2.0)


class TestTracingErrorHandling(unittest.TestCase):
    """Test cases for tracing error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = TracingConfig(
            service_name="test-service",
            backend=TracingBackend.CONSOLE
        )
        self.tracing = AdvancedTracing(self.config)
    
    def test_invalid_span_type(self):
        """Test handling of invalid span type"""
        # Should not raise exception for invalid span type
        span = self.tracing.start_span("test_span", "invalid_type")
        self.assertIsNotNone(span)
    
    def test_invalid_attributes(self):
        """Test handling of invalid attributes"""
        # Should handle invalid attributes gracefully
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC, {"invalid": object()})
        self.assertIsNotNone(span)
    
    def test_span_without_context(self):
        """Test span creation without context"""
        # Should create span even without context
        span = self.tracing.start_span("test_span", SpanType.BUSINESS_LOGIC)
        self.assertIsNotNone(span)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 