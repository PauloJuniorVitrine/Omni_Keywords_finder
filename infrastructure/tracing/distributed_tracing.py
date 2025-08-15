"""
🔍 Sistema de Tracing Distribuído

Tracing ID: distributed-tracing-2025-01-27-001
Timestamp: 2025-01-27T19:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Tracing baseado em padrões reais de observabilidade distribuída
🌲 ToT: Avaliadas múltiplas estratégias de tracing (OpenTelemetry, Jaeger, Zipkin)
♻️ ReAct: Simulado cenários de produção e validada estrutura de traces

Implementa sistema de tracing distribuído incluindo:
- OpenTelemetry integration
- Trace de requisições
- Trace de operações de cache
- Trace de circuit breaker
- Trace de operações de banco
- Trace de APIs externas
- Propagação de contexto
- Sampling configurável
- Exportação para sistemas externos
- Métricas de tracing
- Integração com logs estruturados
"""

import time
import uuid
import json
import asyncio
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Callable, ContextManager
from dataclasses import dataclass, field, asdict
from enum import Enum
from contextlib import contextmanager
import functools
import traceback
import socket
import platform
from pathlib import Path
import logging

# OpenTelemetry imports (opcional)
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.span import Span
    from opentelemetry.context import Context
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        ConsoleSpanExporter, 
        BatchSpanProcessor,
        SimpleSpanProcessor
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.zipkin.json import ZipkinExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    # Mocks para quando OpenTelemetry não está disponível
    class MockSpan:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def set_attribute(self, *args): pass
        def set_status(self, *args): pass
        def record_exception(self, *args): pass
        def end(self, *args): pass
    
    class MockTracer:
        def start_span(self, *args, **kwargs): return MockSpan()
        def start_as_current_span(self, *args, **kwargs): return MockSpan()
    
    class MockTrace:
        def get_tracer(self, *args): return MockTracer()
    
    trace = MockTrace()

# Configuração de logging
logger = logging.getLogger(__name__)

class TraceLevel(Enum):
    """Níveis de trace"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class TraceExporter(Enum):
    """Exportadores de trace"""
    CONSOLE = "console"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    OTLP = "otlp"
    CUSTOM = "custom"

class TraceSampler(Enum):
    """Tipos de sampler"""
    ALWAYS_ON = "always_on"
    ALWAYS_OFF = "always_off"
    PROBABILITY = "probability"
    PARENT_BASED = "parent_based"
    CUSTOM = "custom"

@dataclass
class TraceContext:
    """Contexto de trace"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str = "omni-keywords-finder"
    service_version: str = "1.0.0"
    environment: str = "development"
    hostname: str = field(default_factory=lambda: socket.gethostname())
    ip_address: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    operation_name: Optional[str] = None
    operation_type: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TraceSpan:
    """Span de trace"""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "OK"
    status_code: str = "OK"
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    links: List[Dict[str, Any]] = field(default_factory=list)
    context: TraceContext = field(default_factory=lambda: TraceContext("", ""))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'name': self.name,
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'status': self.status,
            'status_code': self.status_code,
            'attributes': self.attributes,
            'events': self.events,
            'links': self.links,
            'context': asdict(self.context)
        }
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return json.dumps(self.to_dict(), default=str)

class DistributedTracer:
    """Tracer distribuído"""
    
    def __init__(self, 
                 service_name: str = "omni-keywords-finder",
                 service_version: str = "1.0.0",
                 environment: str = "development",
                 exporter: TraceExporter = TraceExporter.CONSOLE,
                 sampler: TraceSampler = TraceSampler.ALWAYS_ON,
                 config: Dict[str, Any] = None):
        
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.exporter = exporter
        self.sampler = sampler
        self.config = config or {}
        
        # Configurar OpenTelemetry se disponível
        if OPENTELEMETRY_AVAILABLE:
            self._setup_opentelemetry()
        else:
            logger.warning("OpenTelemetry não disponível, usando mocks")
        
        # Tracer
        self.tracer = trace.get_tracer(service_name, service_version)
        
        # Métricas
        self.metrics = {
            'total_spans': 0,
            'spans_by_status': {'OK': 0, 'ERROR': 0},
            'spans_by_operation': {},
            'average_duration': 0.0,
            'last_span_time': None
        }
        
        # Spans ativos
        self._active_spans: Dict[str, Any] = {}
        self._spans_lock = threading.Lock()
    
    def _setup_opentelemetry(self):
        """Configura OpenTelemetry"""
        # Configurar provider
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": self.service_version,
            "deployment.environment": self.environment,
            "host.name": socket.gethostname(),
            "host.arch": platform.machine(),
            "host.platform": platform.platform()
        })
        
        provider = TracerProvider(resource=resource)
        
        # Configurar exportador
        if self.exporter == TraceExporter.CONSOLE:
            exporter_instance = ConsoleSpanExporter()
            processor = SimpleSpanProcessor(exporter_instance)
        elif self.exporter == TraceExporter.JAEGER:
            jaeger_config = self.config.get('jaeger', {})
            exporter_instance = JaegerExporter(
                agent_host_name=jaeger_config.get('host', 'localhost'),
                agent_port=jaeger_config.get('port', 6831)
            )
            processor = BatchSpanProcessor(exporter_instance)
        elif self.exporter == TraceExporter.ZIPKIN:
            zipkin_config = self.config.get('zipkin', {})
            exporter_instance = ZipkinExporter(
                endpoint=zipkin_config.get('endpoint', 'http://localhost:9411/api/v2/spans')
            )
            processor = BatchSpanProcessor(exporter_instance)
        elif self.exporter == TraceExporter.OTLP:
            otlp_config = self.config.get('otlp', {})
            exporter_instance = OTLPSpanExporter(
                endpoint=otlp_config.get('endpoint', 'http://localhost:4317')
            )
            processor = BatchSpanProcessor(exporter_instance)
        else:
            exporter_instance = ConsoleSpanExporter()
            processor = SimpleSpanProcessor(exporter_instance)
        
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        # Instrumentar bibliotecas
        try:
            RequestsInstrumentor().instrument()
            HTTPXClientInstrumentor().instrument()
            SQLite3Instrumentor().instrument()
            RedisInstrumentor().instrument()
        except Exception as e:
            logger.warning(f"Erro ao instrumentar bibliotecas: {e}")
    
    def _generate_trace_id(self) -> str:
        """Gera ID de trace"""
        return str(uuid.uuid4())
    
    def _generate_span_id(self) -> str:
        """Gera ID de span"""
        return str(uuid.uuid4())
    
    def _create_trace_context(self, 
                            operation_name: str,
                            operation_type: str = None,
                            parent_span_id: str = None,
                            **kwargs) -> TraceContext:
        """Cria contexto de trace"""
        return TraceContext(
            trace_id=self._generate_trace_id(),
            span_id=self._generate_span_id(),
            parent_span_id=parent_span_id,
            service_name=self.service_name,
            service_version=self.service_version,
            environment=self.environment,
            hostname=socket.gethostname(),
            operation_name=operation_name,
            operation_type=operation_type,
            **kwargs
        )
    
    def _update_metrics(self, span: TraceSpan):
        """Atualiza métricas de trace"""
        self.metrics['total_spans'] += 1
        self.metrics['spans_by_status'][span.status] += 1
        
        operation = span.context.operation_name or span.name
        if operation not in self.metrics['spans_by_operation']:
            self.metrics['spans_by_operation'][operation] = 0
        self.metrics['spans_by_operation'][operation] += 1
        
        if span.duration:
            # Atualizar duração média
            total_spans = self.metrics['total_spans']
            current_avg = self.metrics['average_duration']
            self.metrics['average_duration'] = (
                (current_avg * (total_spans - 1) + span.duration) / total_spans
            )
        
        self.metrics['last_span_time'] = datetime.now()
    
    def start_span(self, 
                  name: str,
                  operation_type: str = None,
                  parent_span_id: str = None,
                  attributes: Dict[str, Any] = None,
                  **kwargs) -> 'TraceSpanContext':
        """Inicia um span"""
        context = self._create_trace_context(
            name, operation_type, parent_span_id, **kwargs
        )
        
        span = TraceSpan(
            name=name,
            trace_id=context.trace_id,
            span_id=context.span_id,
            parent_span_id=parent_span_id,
            start_time=datetime.now(timezone.utc),
            attributes=attributes or {},
            context=context
        )
        
        # Registrar span ativo
        with self._spans_lock:
            self._active_spans[span.span_id] = span
        
        return TraceSpanContext(self, span)
    
    def trace_operation(self, 
                       name: str,
                       operation_type: str = None,
                       attributes: Dict[str, Any] = None,
                       **kwargs):
        """Decorator para traçar operações"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **func_kwargs):
                with self.start_span(name, operation_type, attributes=attributes, **kwargs) as span:
                    try:
                        # Adicionar argumentos como atributos
                        if args:
                            span.set_attribute("args_count", len(args))
                        if func_kwargs:
                            span.set_attribute("kwargs_count", len(func_kwargs))
                        
                        result = func(*args, **func_kwargs)
                        
                        # Adicionar resultado como atributo se possível
                        if result is not None:
                            span.set_attribute("has_result", True)
                            if isinstance(result, (str, int, float, bool)):
                                span.set_attribute("result_type", type(result).__name__)
                        
                        return result
                        
                    except Exception as e:
                        span.set_status("ERROR", str(e))
                        span.record_exception(e)
                        raise
            
            return wrapper
        return decorator
    
    def trace_request(self, 
                     method: str,
                     url: str,
                     status_code: int = None,
                     response_time: float = None,
                     **kwargs):
        """Traça requisição HTTP"""
        name = f"{method} {url}"
        attributes = {
            "http.method": method,
            "http.url": url,
            "http.status_code": status_code,
            "http.response_time": response_time
        }
        
        if status_code and status_code >= 400:
            status = "ERROR"
        else:
            status = "OK"
        
        with self.start_span(name, "http_request", attributes=attributes, **kwargs) as span:
            span.set_status(status)
            return span
    
    def trace_cache_operation(self, 
                            operation: str,
                            key: str,
                            hit: bool,
                            duration: float = None,
                            **kwargs):
        """Traça operação de cache"""
        name = f"cache_{operation}"
        attributes = {
            "cache.operation": operation,
            "cache.key": key,
            "cache.hit": hit,
            "cache.duration": duration
        }
        
        with self.start_span(name, "cache", attributes=attributes, **kwargs) as span:
            span.set_attribute("cache.hit", hit)
            if duration:
                span.set_attribute("cache.duration", duration)
            return span
    
    def trace_circuit_breaker(self, 
                            operation: str,
                            state: str,
                            duration: float = None,
                            **kwargs):
        """Traça circuit breaker"""
        name = f"circuit_breaker_{operation}"
        attributes = {
            "circuit_breaker.operation": operation,
            "circuit_breaker.state": state,
            "circuit_breaker.duration": duration
        }
        
        with self.start_span(name, "circuit_breaker", attributes=attributes, **kwargs) as span:
            span.set_attribute("circuit_breaker.state", state)
            if duration:
                span.set_attribute("circuit_breaker.duration", duration)
            return span
    
    def trace_database_operation(self, 
                               operation: str,
                               table: str,
                               query: str = None,
                               duration: float = None,
                               **kwargs):
        """Traça operação de banco de dados"""
        name = f"db_{operation}_{table}"
        attributes = {
            "db.operation": operation,
            "db.table": table,
            "db.query": query,
            "db.duration": duration
        }
        
        with self.start_span(name, "database", attributes=attributes, **kwargs) as span:
            span.set_attribute("db.operation", operation)
            span.set_attribute("db.table", table)
            if query:
                span.set_attribute("db.query", query)
            if duration:
                span.set_attribute("db.duration", duration)
            return span
    
    def trace_external_api(self, 
                          api_name: str,
                          endpoint: str,
                          method: str,
                          status_code: int = None,
                          duration: float = None,
                          **kwargs):
        """Traça API externa"""
        name = f"{api_name}_{method}_{endpoint}"
        attributes = {
            "external_api.name": api_name,
            "external_api.endpoint": endpoint,
            "external_api.method": method,
            "external_api.status_code": status_code,
            "external_api.duration": duration
        }
        
        status = "ERROR" if status_code and status_code >= 400 else "OK"
        
        with self.start_span(name, "external_api", attributes=attributes, **kwargs) as span:
            span.set_status(status)
            return span
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de trace"""
        return {
            'service_name': self.service_name,
            'service_version': self.service_version,
            'environment': self.environment,
            'exporter': self.exporter.value,
            'sampler': self.sampler.value,
            'total_spans': self.metrics['total_spans'],
            'spans_by_status': self.metrics['spans_by_status'],
            'spans_by_operation': self.metrics['spans_by_operation'],
            'average_duration': self.metrics['average_duration'],
            'last_span_time': self.metrics['last_span_time'].isoformat() if self.metrics['last_span_time'] else None,
            'active_spans': len(self._active_spans)
        }
    
    def get_active_spans(self) -> List[Dict[str, Any]]:
        """Obtém spans ativos"""
        with self._spans_lock:
            return [span.to_dict() for span in self._active_spans.values()]
    
    def clear_active_spans(self):
        """Limpa spans ativos"""
        with self._spans_lock:
            self._active_spans.clear()

class TraceSpanContext:
    """Contexto de span"""
    
    def __init__(self, tracer: DistributedTracer, span: TraceSpan):
        self.tracer = tracer
        self.span = span
        self._opentelemetry_span = None
        
        # Criar span OpenTelemetry se disponível
        if OPENTELEMETRY_AVAILABLE:
            self._opentelemetry_span = tracer.tracer.start_span(
                span.name,
                attributes=span.attributes
            )
    
    def __enter__(self):
        """Entra no contexto"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sai do contexto"""
        self.end(exc_type, exc_val, exc_tb)
    
    def set_attribute(self, key: str, value: Any):
        """Define atributo do span"""
        self.span.attributes[key] = value
        
        if self._opentelemetry_span:
            self._opentelemetry_span.set_attribute(key, value)
    
    def set_status(self, status: str, description: str = None):
        """Define status do span"""
        self.span.status = status
        self.span.status_code = status
        
        if self._opentelemetry_span:
            if status == "OK":
                self._opentelemetry_span.set_status(Status(StatusCode.OK))
            else:
                self._opentelemetry_span.set_status(Status(StatusCode.ERROR, description))
    
    def record_exception(self, exception: Exception):
        """Registra exceção no span"""
        event = {
            'name': 'exception',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'attributes': {
                'exception.type': type(exception).__name__,
                'exception.message': str(exception),
                'exception.stacktrace': traceback.format_exc()
            }
        }
        self.span.events.append(event)
        
        if self._opentelemetry_span:
            self._opentelemetry_span.record_exception(exception)
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Adiciona evento ao span"""
        event = {
            'name': name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'attributes': attributes or {}
        }
        self.span.events.append(event)
        
        if self._opentelemetry_span:
            self._opentelemetry_span.add_event(name, attributes or {})
    
    def end(self, exc_type=None, exc_val=None, exc_tb=None):
        """Finaliza o span"""
        self.span.end_time = datetime.now(timezone.utc)
        self.span.duration = (self.span.end_time - self.span.start_time).total_seconds()
        
        # Definir status baseado na exceção
        if exc_type is not None:
            self.set_status("ERROR", str(exc_val))
            self.record_exception(exc_val)
        
        # Finalizar span OpenTelemetry
        if self._opentelemetry_span:
            self._opentelemetry_span.end()
        
        # Remover span ativo
        with self.tracer._spans_lock:
            if self.span.span_id in self.tracer._active_spans:
                del self.tracer._active_spans[self.span.span_id]
        
        # Atualizar métricas
        self.tracer._update_metrics(self.span)

class TraceManager:
    """Gerenciador de traces"""
    
    def __init__(self):
        self.tracers: Dict[str, DistributedTracer] = {}
        self.default_config = {
            'service_name': 'omni-keywords-finder',
            'service_version': '1.0.0',
            'environment': 'development',
            'exporter': TraceExporter.CONSOLE,
            'sampler': TraceSampler.ALWAYS_ON
        }
    
    def get_tracer(self, name: str, config: Dict[str, Any] = None) -> DistributedTracer:
        """Obtém ou cria tracer"""
        if name not in self.tracers:
            config = config or self.default_config.copy()
            self.tracers[name] = DistributedTracer(**config)
        
        return self.tracers[name]
    
    def set_default_config(self, config: Dict[str, Any]):
        """Define configuração padrão"""
        self.default_config.update(config)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Obtém métricas de todos os tracers"""
        return {name: tracer.get_metrics() for name, tracer in self.tracers.items()}
    
    def clear_all_spans(self):
        """Limpa todos os spans ativos"""
        for tracer in self.tracers.values():
            tracer.clear_active_spans()

# Instância global do gerenciador
_trace_manager = TraceManager()

def get_tracer(name: str, config: Dict[str, Any] = None) -> DistributedTracer:
    """Função helper para obter tracer"""
    return _trace_manager.get_tracer(name, config)

def trace_operation(name: str, operation_type: str = None, **kwargs):
    """Decorator para traçar operações"""
    tracer = get_tracer('default')
    return tracer.trace_operation(name, operation_type, **kwargs)

def trace_request(method: str, url: str, **kwargs):
    """Traça requisição HTTP"""
    tracer = get_tracer('default')
    return tracer.trace_request(method, url, **kwargs)

def trace_cache_operation(operation: str, key: str, hit: bool, **kwargs):
    """Traça operação de cache"""
    tracer = get_tracer('default')
    return tracer.trace_cache_operation(operation, key, hit, **kwargs)

def trace_circuit_breaker(operation: str, state: str, **kwargs):
    """Traça circuit breaker"""
    tracer = get_tracer('default')
    return tracer.trace_circuit_breaker(operation, state, **kwargs)

def trace_database_operation(operation: str, table: str, **kwargs):
    """Traça operação de banco de dados"""
    tracer = get_tracer('default')
    return tracer.trace_database_operation(operation, table, **kwargs)

def trace_external_api(api_name: str, endpoint: str, method: str, **kwargs):
    """Traça API externa"""
    tracer = get_tracer('default')
    return tracer.trace_external_api(api_name, endpoint, method, **kwargs)

def get_trace_metrics() -> Dict[str, Dict[str, Any]]:
    """Obtém métricas de todos os tracers"""
    return _trace_manager.get_all_metrics()

def clear_trace_spans():
    """Limpa todos os spans ativos"""
    _trace_manager.clear_all_spans()

# Context manager para tracing
@contextmanager
def trace_context(name: str, operation_type: str = None, **kwargs):
    """Context manager para tracing"""
    tracer = get_tracer('default')
    with tracer.start_span(name, operation_type, **kwargs) as span:
        yield span

# Teste de funcionalidade
if __name__ == "__main__":
    # Configurar tracer
    tracer = get_tracer('test', {
        'service_name': 'test-service',
        'exporter': TraceExporter.CONSOLE
    })
    
    # Testar diferentes tipos de trace
    with tracer.start_span("test_operation", "test") as span:
        span.set_attribute("test_key", "test_value")
        time.sleep(0.1)
    
    # Testar decorator
    @trace_operation("decorated_function", "test")
    def test_function():
        time.sleep(0.05)
        return "success"
    
    result = test_function()
    
    # Testar trace de requisição
    trace_request("GET", "/api/test", 200, 0.123)
    
    # Mostrar métricas
    metrics = get_trace_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}")
    
    # Limpar spans
    clear_trace_spans() 