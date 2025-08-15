"""
🧪 Testes de Tracing Distribuído

Tracing ID: distributed-tracing-tests-2025-01-27-001
Timestamp: 2025-01-27T19:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de tracing distribuído
🌲 ToT: Avaliadas múltiplas estratégias de teste
♻️ ReAct: Simulado cenários de produção e validada funcionalidade

Testa sistema de tracing distribuído incluindo:
- Testes de diferentes exportadores (Console, Jaeger, Zipkin, OTLP)
- Testes de diferentes tipos de trace
- Testes de context managers
- Testes de decorators
- Testes de métricas de trace
- Testes de performance
- Testes de integração
- Testes de propagação de contexto
"""

import pytest
import json
import time
import uuid
import tempfile
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import threading
import asyncio

from infrastructure.tracing.distributed_tracing import (
    DistributedTracer, TraceLevel, TraceExporter, TraceSampler, TraceContext, TraceSpan,
    TraceSpanContext, TraceManager, get_tracer, trace_operation, trace_request,
    trace_cache_operation, trace_circuit_breaker, trace_database_operation,
    trace_external_api, get_trace_metrics, clear_trace_spans, trace_context
)

class TestTraceLevel:
    """Testes de níveis de trace"""
    
    def test_trace_level_values(self):
        """Testa valores dos níveis de trace"""
        assert TraceLevel.DEBUG.value == "DEBUG"
        assert TraceLevel.INFO.value == "INFO"
        assert TraceLevel.WARNING.value == "WARNING"
        assert TraceLevel.ERROR.value == "ERROR"

class TestTraceExporter:
    """Testes de exportadores de trace"""
    
    def test_trace_exporter_values(self):
        """Testa valores dos exportadores"""
        assert TraceExporter.CONSOLE.value == "console"
        assert TraceExporter.JAEGER.value == "jaeger"
        assert TraceExporter.ZIPKIN.value == "zipkin"
        assert TraceExporter.OTLP.value == "otlp"
        assert TraceExporter.CUSTOM.value == "custom"

class TestTraceSampler:
    """Testes de samplers de trace"""
    
    def test_trace_sampler_values(self):
        """Testa valores dos samplers"""
        assert TraceSampler.ALWAYS_ON.value == "always_on"
        assert TraceSampler.ALWAYS_OFF.value == "always_off"
        assert TraceSampler.PROBABILITY.value == "probability"
        assert TraceSampler.PARENT_BASED.value == "parent_based"
        assert TraceSampler.CUSTOM.value == "custom"

class TestTraceContext:
    """Testes de contexto de trace"""
    
    def test_trace_context_creation(self):
        """Testa criação de contexto de trace"""
        context = TraceContext(
            trace_id="trace123",
            span_id="span456",
            parent_span_id="parent789",
            user_id="user123",
            request_id="req456"
        )
        
        assert context.trace_id == "trace123"
        assert context.span_id == "span456"
        assert context.parent_span_id == "parent789"
        assert context.user_id == "user123"
        assert context.request_id == "req456"
        assert context.service_name == "omni-keywords-finder"
        assert context.service_version == "1.0.0"
        assert context.environment == "development"
    
    def test_trace_context_defaults(self):
        """Testa valores padrão do contexto"""
        context = TraceContext(trace_id="trace123", span_id="span456")
        
        assert context.trace_id == "trace123"
        assert context.span_id == "span456"
        assert context.parent_span_id is None
        assert context.user_id is None
        assert context.request_id is None
        assert context.service_name == "omni-keywords-finder"
        assert context.service_version == "1.0.0"
        assert context.environment == "development"
        assert context.hostname is not None
        assert isinstance(context.additional_data, dict)
    
    def test_trace_context_asdict(self):
        """Testa conversão para dicionário"""
        context = TraceContext(
            trace_id="trace123",
            span_id="span456",
            additional_data={"key": "value"}
        )
        
        context_dict = context.__dict__
        
        assert context_dict["trace_id"] == "trace123"
        assert context_dict["span_id"] == "span456"
        assert context_dict["additional_data"]["key"] == "value"

class TestTraceSpan:
    """Testes de span de trace"""
    
    def test_trace_span_creation(self):
        """Testa criação de span de trace"""
        context = TraceContext(trace_id="trace123", span_id="span456")
        start_time = datetime.now(timezone.utc)
        
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            parent_span_id="parent789",
            start_time=start_time,
            status="OK",
            status_code="OK",
            attributes={"key": "value"},
            context=context
        )
        
        assert span.name == "test_span"
        assert span.trace_id == "trace123"
        assert span.span_id == "span456"
        assert span.parent_span_id == "parent789"
        assert span.start_time == start_time
        assert span.status == "OK"
        assert span.status_code == "OK"
        assert span.attributes["key"] == "value"
        assert span.context.trace_id == "trace123"
    
    def test_trace_span_to_dict(self):
        """Testa conversão para dicionário"""
        context = TraceContext(trace_id="trace123", span_id="span456")
        start_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2023, 1, 1, 12, 0, 1, tzinfo=timezone.utc)
        
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=start_time,
            end_time=end_time,
            duration=1.0,
            status="OK",
            status_code="OK",
            attributes={"key": "value"},
            context=context
        )
        
        span_dict = span.to_dict()
        
        assert span_dict["name"] == "test_span"
        assert span_dict["trace_id"] == "trace123"
        assert span_dict["span_id"] == "span456"
        assert span_dict["start_time"] == start_time.isoformat()
        assert span_dict["end_time"] == end_time.isoformat()
        assert span_dict["duration"] == 1.0
        assert span_dict["status"] == "OK"
        assert span_dict["status_code"] == "OK"
        assert span_dict["attributes"]["key"] == "value"
        assert span_dict["context"]["trace_id"] == "trace123"
    
    def test_trace_span_to_json(self):
        """Testa conversão para JSON"""
        context = TraceContext(trace_id="trace123", span_id="span456")
        start_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=start_time,
            status="OK",
            status_code="OK",
            context=context
        )
        
        json_str = span.to_json()
        span_dict = json.loads(json_str)
        
        assert span_dict["name"] == "test_span"
        assert span_dict["trace_id"] == "trace123"
        assert span_dict["span_id"] == "span456"
        assert span_dict["status"] == "OK"

class TestDistributedTracer:
    """Testes do tracer distribuído"""
    
    def test_tracer_creation(self):
        """Testa criação do tracer"""
        tracer = DistributedTracer(
            service_name="test_service",
            service_version="1.0.0",
            environment="test",
            exporter=TraceExporter.CONSOLE,
            sampler=TraceSampler.ALWAYS_ON
        )
        
        assert tracer.service_name == "test_service"
        assert tracer.service_version == "1.0.0"
        assert tracer.environment == "test"
        assert tracer.exporter == TraceExporter.CONSOLE
        assert tracer.sampler == TraceSampler.ALWAYS_ON
    
    def test_tracer_default_config(self):
        """Testa configuração padrão do tracer"""
        tracer = DistributedTracer()
        
        assert tracer.service_name == "omni-keywords-finder"
        assert tracer.service_version == "1.0.0"
        assert tracer.environment == "development"
        assert tracer.exporter == TraceExporter.CONSOLE
        assert tracer.sampler == TraceSampler.ALWAYS_ON
    
    def test_tracer_generate_ids(self):
        """Testa geração de IDs"""
        tracer = DistributedTracer()
        
        trace_id = tracer._generate_trace_id()
        span_id = tracer._generate_span_id()
        
        assert isinstance(trace_id, str)
        assert isinstance(span_id, str)
        assert len(trace_id) > 0
        assert len(span_id) > 0
    
    def test_tracer_create_context(self):
        """Testa criação de contexto"""
        tracer = DistributedTracer()
        
        context = tracer._create_trace_context(
            "test_operation",
            "test_type",
            "parent123",
            user_id="user456"
        )
        
        assert context.operation_name == "test_operation"
        assert context.operation_type == "test_type"
        assert context.parent_span_id == "parent123"
        assert context.user_id == "user456"
        assert context.trace_id is not None
        assert context.span_id is not None
    
    def test_tracer_start_span(self):
        """Testa início de span"""
        tracer = DistributedTracer()
        
        with tracer.start_span("test_span", "test_type") as span:
            assert span.span.name == "test_span"
            assert span.span.trace_id is not None
            assert span.span.span_id is not None
            assert span.span.start_time is not None
            assert span.span.end_time is None  # Ainda não finalizado
        
        # Após sair do contexto, span deve estar finalizado
        assert span.span.end_time is not None
        assert span.span.duration is not None
    
    def test_tracer_start_span_with_attributes(self):
        """Testa início de span com atributos"""
        tracer = DistributedTracer()
        
        attributes = {"key": "value", "number": 42}
        
        with tracer.start_span("test_span", attributes=attributes) as span:
            assert span.span.attributes["key"] == "value"
            assert span.span.attributes["number"] == 42
    
    def test_tracer_trace_operation_decorator(self):
        """Testa decorator de trace de operação"""
        tracer = DistributedTracer()
        
        @tracer.trace_operation("test_function", "test")
        def test_function():
            return "success"
        
        # Executar função
        result = test_function()
        
        assert result == "success"
        
        # Verificar métricas
        metrics = tracer.get_metrics()
        assert metrics["total_spans"] == 1
        assert "test_function" in metrics["spans_by_operation"]
    
    def test_tracer_trace_operation_decorator_with_error(self):
        """Testa decorator de trace de operação com erro"""
        tracer = DistributedTracer()
        
        @tracer.trace_operation("test_function_error", "test")
        def test_function_error():
            raise ValueError("Test error")
        
        # Executar função e capturar erro
        with pytest.raises(ValueError):
            test_function_error()
        
        # Verificar métricas
        metrics = tracer.get_metrics()
        assert metrics["total_spans"] == 1
        assert metrics["spans_by_status"]["ERROR"] == 1
    
    def test_tracer_trace_request(self):
        """Testa trace de requisição"""
        tracer = DistributedTracer()
        
        # Trace de requisição bem-sucedida
        with tracer.trace_request("GET", "/api/users", 200, 0.123) as span:
            assert span.span.name == "GET /api/users"
            assert span.span.attributes["http.method"] == "GET"
            assert span.span.attributes["http.url"] == "/api/users"
            assert span.span.attributes["http.status_code"] == 200
            assert span.span.attributes["http.response_time"] == 0.123
            assert span.span.status == "OK"
        
        # Trace de requisição com erro
        with tracer.trace_request("POST", "/api/users", 500, 0.456) as span:
            assert span.span.status == "ERROR"
    
    def test_tracer_trace_cache_operation(self):
        """Testa trace de operação de cache"""
        tracer = DistributedTracer()
        
        # Trace de cache hit
        with tracer.trace_cache_operation("get", "user:123", True, 0.001) as span:
            assert span.span.name == "cache_get"
            assert span.span.attributes["cache.operation"] == "get"
            assert span.span.attributes["cache.key"] == "user:123"
            assert span.span.attributes["cache.hit"] is True
            assert span.span.attributes["cache.duration"] == 0.001
        
        # Trace de cache miss
        with tracer.trace_cache_operation("get", "user:456", False) as span:
            assert span.span.attributes["cache.hit"] is False
    
    def test_tracer_trace_circuit_breaker(self):
        """Testa trace de circuit breaker"""
        tracer = DistributedTracer()
        
        # Trace de circuit breaker fechado
        with tracer.trace_circuit_breaker("api_call", "closed", 0.1) as span:
            assert span.span.name == "circuit_breaker_api_call"
            assert span.span.attributes["circuit_breaker.operation"] == "api_call"
            assert span.span.attributes["circuit_breaker.state"] == "closed"
            assert span.span.attributes["circuit_breaker.duration"] == 0.1
        
        # Trace de circuit breaker aberto
        with tracer.trace_circuit_breaker("api_call", "open") as span:
            assert span.span.attributes["circuit_breaker.state"] == "open"
    
    def test_tracer_trace_database_operation(self):
        """Testa trace de operação de banco"""
        tracer = DistributedTracer()
        
        # Trace de operação de banco
        with tracer.trace_database_operation("select", "users", "SELECT * FROM users", 0.05) as span:
            assert span.span.name == "db_select_users"
            assert span.span.attributes["db.operation"] == "select"
            assert span.span.attributes["db.table"] == "users"
            assert span.span.attributes["db.query"] == "SELECT * FROM users"
            assert span.span.attributes["db.duration"] == 0.05
    
    def test_tracer_trace_external_api(self):
        """Testa trace de API externa"""
        tracer = DistributedTracer()
        
        # Trace de API externa bem-sucedida
        with tracer.trace_external_api("instagram", "/users/me", "GET", 200, 0.2) as span:
            assert span.span.name == "instagram_GET_/users/me"
            assert span.span.attributes["external_api.name"] == "instagram"
            assert span.span.attributes["external_api.endpoint"] == "/users/me"
            assert span.span.attributes["external_api.method"] == "GET"
            assert span.span.attributes["external_api.status_code"] == 200
            assert span.span.attributes["external_api.duration"] == 0.2
            assert span.span.status == "OK"
        
        # Trace de API externa com erro
        with tracer.trace_external_api("instagram", "/users/me", "GET", 500, 0.1) as span:
            assert span.span.status == "ERROR"
    
    def test_tracer_metrics(self):
        """Testa métricas do tracer"""
        tracer = DistributedTracer()
        
        # Fazer alguns traces
        with tracer.start_span("span1", "test"):
            pass
        
        with tracer.start_span("span2", "test"):
            pass
        
        # Obter métricas
        metrics = tracer.get_metrics()
        
        assert metrics["service_name"] == "omni-keywords-finder"
        assert metrics["service_version"] == "1.0.0"
        assert metrics["environment"] == "development"
        assert metrics["exporter"] == "console"
        assert metrics["sampler"] == "always_on"
        assert metrics["total_spans"] == 2
        assert metrics["spans_by_status"]["OK"] == 2
        assert metrics["spans_by_operation"]["span1"] == 1
        assert metrics["spans_by_operation"]["span2"] == 1
        assert metrics["average_duration"] > 0
        assert metrics["last_span_time"] is not None
        assert metrics["active_spans"] == 0  # Todos finalizados
    
    def test_tracer_active_spans(self):
        """Testa spans ativos"""
        tracer = DistributedTracer()
        
        # Iniciar span sem finalizar
        span_context = tracer.start_span("active_span", "test")
        
        # Verificar spans ativos
        active_spans = tracer.get_active_spans()
        assert len(active_spans) == 1
        assert active_spans[0]["name"] == "active_span"
        
        # Finalizar span
        span_context.end()
        
        # Verificar que não há mais spans ativos
        active_spans = tracer.get_active_spans()
        assert len(active_spans) == 0
    
    def test_tracer_clear_active_spans(self):
        """Testa limpeza de spans ativos"""
        tracer = DistributedTracer()
        
        # Iniciar alguns spans sem finalizar
        span1 = tracer.start_span("span1", "test")
        span2 = tracer.start_span("span2", "test")
        
        # Verificar spans ativos
        active_spans = tracer.get_active_spans()
        assert len(active_spans) == 2
        
        # Limpar spans ativos
        tracer.clear_active_spans()
        
        # Verificar que não há mais spans ativos
        active_spans = tracer.get_active_spans()
        assert len(active_spans) == 0

class TestTraceSpanContext:
    """Testes de contexto de span"""
    
    def test_span_context_creation(self):
        """Testa criação de contexto de span"""
        tracer = DistributedTracer()
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=datetime.now(timezone.utc)
        )
        
        span_context = TraceSpanContext(tracer, span)
        
        assert span_context.tracer == tracer
        assert span_context.span == span
    
    def test_span_context_set_attribute(self):
        """Testa definição de atributo"""
        tracer = DistributedTracer()
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=datetime.now(timezone.utc)
        )
        
        span_context = TraceSpanContext(tracer, span)
        span_context.set_attribute("test_key", "test_value")
        
        assert span.attributes["test_key"] == "test_value"
    
    def test_span_context_set_status(self):
        """Testa definição de status"""
        tracer = DistributedTracer()
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=datetime.now(timezone.utc)
        )
        
        span_context = TraceSpanContext(tracer, span)
        span_context.set_status("ERROR", "Test error")
        
        assert span.status == "ERROR"
        assert span.status_code == "ERROR"
    
    def test_span_context_record_exception(self):
        """Testa registro de exceção"""
        tracer = DistributedTracer()
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=datetime.now(timezone.utc)
        )
        
        span_context = TraceSpanContext(tracer, span)
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            span_context.record_exception(e)
        
        assert len(span.events) == 1
        assert span.events[0]["name"] == "exception"
        assert span.events[0]["attributes"]["exception.type"] == "ValueError"
        assert span.events[0]["attributes"]["exception.message"] == "Test exception"
    
    def test_span_context_add_event(self):
        """Testa adição de evento"""
        tracer = DistributedTracer()
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=datetime.now(timezone.utc)
        )
        
        span_context = TraceSpanContext(tracer, span)
        span_context.add_event("test_event", {"key": "value"})
        
        assert len(span.events) == 1
        assert span.events[0]["name"] == "test_event"
        assert span.events[0]["attributes"]["key"] == "value"
    
    def test_span_context_end(self):
        """Testa finalização de span"""
        tracer = DistributedTracer()
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=datetime.now(timezone.utc)
        )
        
        span_context = TraceSpanContext(tracer, span)
        
        # Verificar que span não está finalizado
        assert span.end_time is None
        assert span.duration is None
        
        # Finalizar span
        span_context.end()
        
        # Verificar que span está finalizado
        assert span.end_time is not None
        assert span.duration is not None
    
    def test_span_context_end_with_exception(self):
        """Testa finalização de span com exceção"""
        tracer = DistributedTracer()
        span = TraceSpan(
            name="test_span",
            trace_id="trace123",
            span_id="span456",
            start_time=datetime.now(timezone.utc)
        )
        
        span_context = TraceSpanContext(tracer, span)
        
        # Finalizar span com exceção
        exception = ValueError("Test error")
        span_context.end(ValueError, exception, None)
        
        # Verificar que status foi definido como erro
        assert span.status == "ERROR"
        assert span.status_code == "ERROR"
        
        # Verificar que exceção foi registrada
        assert len(span.events) == 1
        assert span.events[0]["name"] == "exception"

class TestTraceManager:
    """Testes do gerenciador de traces"""
    
    def test_trace_manager_creation(self):
        """Testa criação do gerenciador"""
        manager = TraceManager()
        
        assert len(manager.tracers) == 0
        assert manager.default_config["service_name"] == "omni-keywords-finder"
        assert manager.default_config["service_version"] == "1.0.0"
    
    def test_trace_manager_get_tracer(self):
        """Testa obtenção de tracer"""
        manager = TraceManager()
        
        # Obter tracer pela primeira vez
        tracer1 = manager.get_tracer("test_tracer")
        assert "test_tracer" in manager.tracers
        assert tracer1.service_name == "omni-keywords-finder"
        
        # Obter o mesmo tracer novamente
        tracer2 = manager.get_tracer("test_tracer")
        assert tracer1 is tracer2
    
    def test_trace_manager_custom_config(self):
        """Testa configuração customizada"""
        manager = TraceManager()
        
        config = {
            "service_name": "custom_service",
            "service_version": "2.0.0",
            "environment": "production",
            "exporter": TraceExporter.JAEGER
        }
        
        tracer = manager.get_tracer("test_tracer", config)
        
        assert tracer.service_name == "custom_service"
        assert tracer.service_version == "2.0.0"
        assert tracer.environment == "production"
        assert tracer.exporter == TraceExporter.JAEGER
    
    def test_trace_manager_set_default_config(self):
        """Testa configuração padrão"""
        manager = TraceManager()
        
        new_config = {
            "service_name": "new_service",
            "environment": "staging"
        }
        
        manager.set_default_config(new_config)
        
        assert manager.default_config["service_name"] == "new_service"
        assert manager.default_config["environment"] == "staging"
    
    def test_trace_manager_get_all_metrics(self):
        """Testa obtenção de todas as métricas"""
        manager = TraceManager()
        
        # Criar alguns tracers
        tracer1 = manager.get_tracer("tracer1")
        tracer2 = manager.get_tracer("tracer2")
        
        # Fazer alguns traces
        with tracer1.start_span("span1", "test"):
            pass
        
        with tracer2.start_span("span2", "test"):
            pass
        
        # Obter métricas
        all_metrics = manager.get_all_metrics()
        
        assert "tracer1" in all_metrics
        assert "tracer2" in all_metrics
        assert all_metrics["tracer1"]["total_spans"] == 1
        assert all_metrics["tracer2"]["total_spans"] == 1
    
    def test_trace_manager_clear_all_spans(self):
        """Testa limpeza de todos os spans"""
        manager = TraceManager()
        
        # Criar alguns tracers
        tracer1 = manager.get_tracer("tracer1")
        tracer2 = manager.get_tracer("tracer2")
        
        # Iniciar spans sem finalizar
        span1 = tracer1.start_span("span1", "test")
        span2 = tracer2.start_span("span2", "test")
        
        # Verificar spans ativos
        assert len(tracer1.get_active_spans()) == 1
        assert len(tracer2.get_active_spans()) == 1
        
        # Limpar todos os spans
        manager.clear_all_spans()
        
        # Verificar que não há mais spans ativos
        assert len(tracer1.get_active_spans()) == 0
        assert len(tracer2.get_active_spans()) == 0

class TestHelperFunctions:
    """Testes das funções helper"""
    
    def test_get_tracer(self):
        """Testa função get_tracer"""
        tracer = get_tracer("test_tracer")
        
        assert isinstance(tracer, DistributedTracer)
        assert tracer.service_name == "omni-keywords-finder"
    
    def test_trace_operation(self):
        """Testa função trace_operation"""
        @trace_operation("test_function", "test")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
        
        # Verificar se trace foi criado
        metrics = get_trace_metrics()
        assert any("test_function" in op for op in metrics.get("default", {}).get("spans_by_operation", {}))
    
    def test_trace_request(self):
        """Testa função trace_request"""
        with trace_request("GET", "/api/test", 200, 0.123) as span:
            assert span.span.name == "GET /api/test"
            assert span.span.attributes["http.method"] == "GET"
    
    def test_trace_cache_operation(self):
        """Testa função trace_cache_operation"""
        with trace_cache_operation("get", "user:123", True) as span:
            assert span.span.name == "cache_get"
            assert span.span.attributes["cache.hit"] is True
    
    def test_trace_circuit_breaker(self):
        """Testa função trace_circuit_breaker"""
        with trace_circuit_breaker("api_call", "open") as span:
            assert span.span.name == "circuit_breaker_api_call"
            assert span.span.attributes["circuit_breaker.state"] == "open"
    
    def test_trace_database_operation(self):
        """Testa função trace_database_operation"""
        with trace_database_operation("select", "users") as span:
            assert span.span.name == "db_select_users"
            assert span.span.attributes["db.operation"] == "select"
    
    def test_trace_external_api(self):
        """Testa função trace_external_api"""
        with trace_external_api("instagram", "/users/me", "GET") as span:
            assert span.span.name == "instagram_GET_/users/me"
            assert span.span.attributes["external_api.name"] == "instagram"
    
    def test_get_trace_metrics(self):
        """Testa função get_trace_metrics"""
        # Fazer alguns traces
        with trace_request("GET", "/api/test", 200, 0.123):
            pass
        
        # Obter métricas
        metrics = get_trace_metrics()
        
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
    
    def test_clear_trace_spans(self):
        """Testa função clear_trace_spans"""
        # Criar alguns tracers
        get_tracer("test_tracer1")
        get_tracer("test_tracer2")
        
        # Limpar spans
        clear_trace_spans()
        
        # Verificar se foram limpos
        metrics = get_trace_metrics()
        for tracer_metrics in metrics.values():
            assert tracer_metrics["active_spans"] == 0

class TestContextManagers:
    """Testes de context managers"""
    
    def test_trace_context_success(self):
        """Testa trace_context com sucesso"""
        with trace_context("test_operation", "test") as span:
            assert span.span.name == "test_operation"
            assert span.span.start_time is not None
            assert span.span.end_time is None  # Ainda não finalizado
        
        # Após sair do contexto, span deve estar finalizado
        assert span.span.end_time is not None
        assert span.span.duration is not None
    
    def test_trace_context_error(self):
        """Testa trace_context com erro"""
        with pytest.raises(ValueError):
            with trace_context("test_operation_error", "test") as span:
                raise ValueError("Test error")
        
        # Span deve estar finalizado com status de erro
        assert span.span.end_time is not None
        assert span.span.status == "ERROR"

class TestPerformance:
    """Testes de performance"""
    
    def test_tracer_performance(self):
        """Testa performance do tracer"""
        tracer = DistributedTracer()
        
        start_time = time.time()
        
        # Fazer muitos traces
        for i in range(1000):
            with tracer.start_span(f"span_{i}", "test"):
                pass
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar métricas
        metrics = tracer.get_metrics()
        assert metrics["total_spans"] == 1000
        
        # Performance deve ser boa (menos de 1 segundo para 1000 traces)
        assert duration < 1.0
    
    def test_concurrent_tracing(self):
        """Testa tracing concorrente"""
        tracer = DistributedTracer()
        
        def trace_worker(worker_id):
            for i in range(100):
                with tracer.start_span(f"worker_{worker_id}_span_{i}", "test"):
                    pass
        
        # Executar múltiplos workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=trace_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar todos terminarem
        for thread in threads:
            thread.join()
        
        # Verificar métricas
        metrics = tracer.get_metrics()
        assert metrics["total_spans"] == 500  # 5 workers * 100 traces cada

class TestIntegration:
    """Testes de integração"""
    
    def test_full_tracing_workflow(self):
        """Testa workflow completo de tracing"""
        # Configurar tracer
        tracer = get_tracer("integration_test", {
            "service_name": "integration_service",
            "environment": "test"
        })
        
        # Fazer diferentes tipos de traces
        with tracer.trace_request("POST", "/api/users", 201, 0.234) as request_span:
            request_span.set_attribute("user_id", "user123")
            
            with tracer.trace_database_operation("insert", "users", "INSERT INTO users...", 0.045) as db_span:
                db_span.set_attribute("rows_affected", 1)
            
            with tracer.trace_cache_operation("set", "user:123", False, 0.002) as cache_span:
                cache_span.set_attribute("cache_size", 1024)
            
            with tracer.trace_external_api("email_service", "/send", "POST", 200, 0.156) as api_span:
                api_span.set_attribute("email_type", "welcome")
        
        # Obter métricas
        metrics = get_trace_metrics()
        
        # Verificar se todos os tipos de trace foram criados
        integration_metrics = metrics.get("integration_test", {})
        assert integration_metrics["total_spans"] == 4
        assert integration_metrics["spans_by_status"]["OK"] == 4
    
    def test_trace_propagation(self):
        """Testa propagação de contexto entre spans"""
        tracer = DistributedTracer()
        
        # Span pai
        with tracer.start_span("parent_span", "parent") as parent_span:
            parent_span.set_attribute("parent_key", "parent_value")
            
            # Span filho
            with tracer.start_span("child_span", "child", parent_span_id=parent_span.span.span_id) as child_span:
                child_span.set_attribute("child_key", "child_value")
                
                # Span neto
                with tracer.start_span("grandchild_span", "child", parent_span_id=child_span.span.span_id) as grandchild_span:
                    grandchild_span.set_attribute("grandchild_key", "grandchild_value")
        
        # Verificar hierarquia
        assert parent_span.span.parent_span_id is None
        assert child_span.span.parent_span_id == parent_span.span.span_id
        assert grandchild_span.span.parent_span_id == child_span.span.span_id

# Teste de funcionalidade
if __name__ == "__main__":
    # Teste básico
    tracer = get_tracer("test")
    
    with tracer.start_span("test_span", "test") as span:
        span.set_attribute("test_key", "test_value")
        time.sleep(0.1)
    
    # Teste de diferentes tipos de trace
    trace_request("GET", "/api/test", 200, 0.123)
    trace_cache_operation("get", "user:123", True)
    trace_circuit_breaker("api_call", "closed")
    
    # Mostrar métricas
    metrics = get_trace_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}")
    
    # Limpar spans
    clear_trace_spans() 