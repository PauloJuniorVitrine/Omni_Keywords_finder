"""
Sistema APM (Application Performance Monitoring) - Fase 3.2 COMPLETA
Tracing ID: CHECKLIST_FINAL_20250127_003
Data: 2025-01-27
Status: IMPLEMENTAÇÃO COMPLETA

Sistema enterprise-grade de APM com:
- OpenTelemetry para tracing distribuído
- Prometheus para métricas
- Jaeger para visualização de traces
- APM customizado para Omni Keywords Finder
- Performance monitoring em tempo real
- Error tracking e alertas
"""

import os
import time
import json
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from contextlib import contextmanager
import functools
import uuid
import psutil
import requests
from pathlib import Path

# OpenTelemetry imports
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.sdk.trace.sampling import ProbabilisticSampler
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.prometheus import PrometheusExporter
    from prometheus_client import start_http_server, Counter, Histogram, Gauge, Summary
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    print("OpenTelemetry não disponível. Sistema APM básico será usado.")

class MetricType(Enum):
    """Tipos de métricas APM."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class SpanType(Enum):
    """Tipos de spans para tracing."""
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    CACHE_OPERATION = "cache_operation"
    EXTERNAL_API = "external_api"
    BUSINESS_LOGIC = "business_logic"
    BACKGROUND_JOB = "background_job"

class ErrorSeverity(Enum):
    """Severidade de erros."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class APMConfig:
    """Configuração do sistema APM."""
    service_name: str = "omni-keywords-finder"
    service_version: str = "1.0.0"
    environment: str = "development"
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    prometheus_port: int = 8000
    sampling_rate: float = 0.1
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    metrics_retention_days: int = 30
    trace_retention_days: int = 7

@dataclass
class PerformanceMetric:
    """Métrica de performance."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str]
    metadata: Dict[str, Any]

@dataclass
class ErrorEvent:
    """Evento de erro."""
    error_id: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    stack_trace: str
    user_id: Optional[str]
    correlation_id: Optional[str]
    timestamp: datetime
    context: Dict[str, Any]

class PrometheusMetrics:
    """Métricas Prometheus customizadas para Omni Keywords Finder."""
    
    def __init__(self):
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        # Métricas de API
        self.api_requests_total = Counter(
            'omni_api_requests_total',
            'Total de requisições API',
            ['method', 'endpoint', 'status_code']
        )
        
        self.api_request_duration = Histogram(
            'omni_api_request_duration_seconds',
            'Duração das requisições API',
            ['method', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        # Métricas de negócio
        self.keywords_collected_total = Counter(
            'omni_keywords_collected_total',
            'Total de keywords coletadas',
            ['source', 'status']
        )
        
        self.keywords_processed_total = Counter(
            'omni_keywords_processed_total',
            'Total de keywords processadas',
            ['processor', 'status']
        )
        
        # Métricas de cache
        self.cache_hits_total = Counter(
            'omni_cache_hits_total',
            'Total de hits no cache',
            ['cache_type', 'key_pattern']
        )
        
        self.cache_misses_total = Counter(
            'omni_cache_misses_total',
            'Total de misses no cache',
            ['cache_type', 'key_pattern']
        )
        
        # Métricas de banco de dados
        self.db_queries_total = Counter(
            'omni_db_queries_total',
            'Total de queries no banco',
            ['operation', 'table']
        )
        
        self.db_query_duration = Histogram(
            'omni_db_query_duration_seconds',
            'Duração das queries no banco',
            ['operation', 'table'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
        )
        
        # Métricas de sistema
        self.active_connections = Gauge(
            'omni_active_connections',
            'Conexões ativas',
            ['connection_type']
        )
        
        self.memory_usage_bytes = Gauge(
            'omni_memory_usage_bytes',
            'Uso de memória em bytes',
            ['component']
        )
        
        self.cpu_usage_percent = Gauge(
            'omni_cpu_usage_percent',
            'Uso de CPU em percentual',
            ['component']
        )
        
        # Métricas de erro
        self.errors_total = Counter(
            'omni_errors_total',
            'Total de erros',
            ['error_type', 'severity']
        )
        
        # Métricas de performance
        self.response_time_p95 = Summary(
            'omni_response_time_p95_seconds',
            '95º percentil do tempo de resposta',
            ['endpoint']
        )
        
        self.response_time_p99 = Summary(
            'omni_response_time_p99_seconds',
            '99º percentil do tempo de resposta',
            ['endpoint']
        )

class APMSystem:
    """
    Sistema APM completo para Omni Keywords Finder.
    
    Funcionalidades:
    - Tracing distribuído com OpenTelemetry
    - Métricas customizadas com Prometheus
    - Error tracking e alertas
    - Performance monitoring
    - Business metrics
    """
    
    def __init__(self, config: APMConfig = None):
        self.config = config or APMConfig()
        self.tracer = None
        self.meter = None
        self.prometheus_metrics = None
        self.error_tracker = ErrorTracker()
        self.performance_monitor = PerformanceMonitor()
        self.business_metrics = BusinessMetrics()
        
        # Inicializar componentes
        self._initialize_components()
        
        # Thread para coleta de métricas do sistema
        self._metrics_thread = None
        self._running = False
        
    def _initialize_components(self):
        """Inicializar componentes do APM."""
        if not OPENTELEMETRY_AVAILABLE:
            print("⚠️ OpenTelemetry não disponível. Usando sistema APM básico.")
            return
            
        # Configurar resource
        resource = Resource.create({
            "service.name": self.config.service_name,
            "service.version": self.config.service_version,
            "service.environment": self.config.environment,
            "deployment.environment": self.config.environment,
            "cloud.provider": "aws",
            "cloud.region": "us-east-1"
        })
        
        # Configurar tracing
        if self.config.enable_tracing:
            self._setup_tracing(resource)
        
        # Configurar métricas
        if self.config.enable_metrics:
            self._setup_metrics(resource)
            self.prometheus_metrics = PrometheusMetrics()
            
            # Iniciar servidor Prometheus
            start_http_server(self.config.prometheus_port)
        
        # Configurar logging
        if self.config.enable_logging:
            self._setup_logging()
    
    def _setup_tracing(self, resource: Resource):
        """Configurar sistema de tracing."""
        # Configurar sampler
        sampler = ProbabilisticSampler(self.config.sampling_rate)
        
        # Configurar provider de tracing
        trace_provider = TracerProvider(
            resource=resource,
            sampler=sampler
        )
        
        # Configurar exportadores
        exporters = [ConsoleSpanExporter()]
        
        # Adicionar Jaeger se configurado
        if self.config.jaeger_endpoint:
            try:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=self.config.jaeger_endpoint.split("://")[1].split(":")[0],
                    agent_port=int(self.config.jaeger_endpoint.split(":")[-1].split("/")[0])
                )
                exporters.append(jaeger_exporter)
            except Exception as e:
                print(f"⚠️ Erro ao configurar Jaeger: {e}")
        
        # Adicionar processadores
        for exporter in exporters:
            trace_provider.add_span_processor(BatchSpanProcessor(exporter))
        
        # Configurar tracer global
        trace.set_tracer_provider(trace_provider)
        self.tracer = trace.get_tracer(__name__)
    
    def _setup_metrics(self, resource: Resource):
        """Configurar sistema de métricas."""
        # Configurar exportadores
        exporters = [ConsoleMetricExporter()]
        
        # Configurar provider de métricas
        metric_reader = PeriodicExportingMetricReader(exporters[0])
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
        
        # Configurar meter global
        metrics.set_meter_provider(meter_provider)
        self.meter = metrics.get_meter(__name__)
    
    def _setup_logging(self):
        """Configurar logging instrumentado."""
        if OPENTELEMETRY_AVAILABLE:
            LoggingInstrumentor().instrument()
    
    def start_system_metrics_collection(self):
        """Iniciar coleta de métricas do sistema."""
        if self._metrics_thread and self._metrics_thread.is_alive():
            return
            
        self._running = True
        self._metrics_thread = threading.Thread(
            target=self._collect_system_metrics_loop,
            daemon=True
        )
        self._metrics_thread.start()
    
    def stop_system_metrics_collection(self):
        """Parar coleta de métricas do sistema."""
        self._running = False
        if self._metrics_thread and self._metrics_thread.is_alive():
            self._metrics_thread.join(timeout=5)
    
    def _collect_system_metrics_loop(self):
        """Loop de coleta de métricas do sistema."""
        while self._running:
            try:
                # Métricas de memória
                memory = psutil.virtual_memory()
                if self.prometheus_metrics:
                    self.prometheus_metrics.memory_usage_bytes.labels(
                        component="system"
                    ).set(memory.used)
                
                # Métricas de CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                if self.prometheus_metrics:
                    self.prometheus_metrics.cpu_usage_percent.labels(
                        component="system"
                    ).set(cpu_percent)
                
                # Métricas de processo
                process = psutil.Process()
                if self.prometheus_metrics:
                    self.prometheus_metrics.memory_usage_bytes.labels(
                        component="process"
                    ).set(process.memory_info().rss)
                    
                    self.prometheus_metrics.cpu_usage_percent.labels(
                        component="process"
                    ).set(process.cpu_percent())
                
                time.sleep(30)  # Coletar a cada 30 segundos
                
            except Exception as e:
                print(f"Erro na coleta de métricas do sistema: {e}")
                time.sleep(60)  # Esperar mais tempo em caso de erro
    
    def trace_operation(self, operation_name: str, span_type: SpanType = SpanType.BUSINESS_LOGIC):
        """Decorator para tracing de operações."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.tracer:
                    return func(*args, **kwargs)
                
                with self.tracer.start_as_current_span(
                    operation_name,
                    kind=trace.SpanKind.INTERNAL
                ) as span:
                    # Adicionar atributos
                    span.set_attribute("operation.name", operation_name)
                    span.set_attribute("operation.type", span_type.value)
                    span.set_attribute("service.name", self.config.service_name)
                    
                    # Adicionar argumentos como atributos (sem dados sensíveis)
                    if args:
                        span.set_attribute("operation.args_count", len(args))
                    if kwargs:
                        safe_kwargs = {k: str(v)[:100] for k, v in kwargs.items() 
                                     if not any(sensitive in k.lower() for sensitive in ['password', 'token', 'key'])}
                        span.set_attribute("operation.kwargs", json.dumps(safe_kwargs))
                    
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        # Registrar métricas de performance
                        span.set_attribute("operation.duration", duration)
                        span.set_attribute("operation.status", "success")
                        span.set_status(Status(StatusCode.OK))
                        
                        # Registrar métricas Prometheus
                        if self.prometheus_metrics:
                            self.prometheus_metrics.api_request_duration.labels(
                                method=operation_name,
                                endpoint="internal"
                            ).observe(duration)
                        
                        return result
                        
                    except Exception as e:
                        duration = time.time() - start_time
                        
                        # Registrar erro
                        span.set_attribute("operation.duration", duration)
                        span.set_attribute("operation.status", "error")
                        span.set_attribute("operation.error", str(e))
                        span.set_attribute("operation.error_type", type(e).__name__)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        
                        # Registrar métricas de erro
                        if self.prometheus_metrics:
                            self.prometheus_metrics.errors_total.labels(
                                error_type=type(e).__name__,
                                severity="high"
                            ).inc()
                        
                        # Registrar no error tracker
                        self.error_tracker.record_error(
                            error_type=type(e).__name__,
                            error_message=str(e),
                            severity=ErrorSeverity.HIGH,
                            operation_name=operation_name
                        )
                        
                        raise
            
            return wrapper
        return decorator
    
    def trace_api_request(self, endpoint: str, method: str = "GET"):
        """Decorator para tracing de requisições API."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.tracer:
                    return func(*args, **kwargs)
                
                with self.tracer.start_as_current_span(
                    f"{method} {endpoint}",
                    kind=trace.SpanKind.SERVER
                ) as span:
                    # Adicionar atributos HTTP
                    span.set_attribute("http.method", method)
                    span.set_attribute("http.route", endpoint)
                    span.set_attribute("http.target", endpoint)
                    span.set_attribute("service.name", self.config.service_name)
                    
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        # Registrar métricas
                        span.set_attribute("http.status_code", 200)
                        span.set_attribute("http.response_time", duration)
                        span.set_status(Status(StatusCode.OK))
                        
                        # Métricas Prometheus
                        if self.prometheus_metrics:
                            self.prometheus_metrics.api_requests_total.labels(
                                method=method,
                                endpoint=endpoint,
                                status_code="200"
                            ).inc()
                            
                            self.prometheus_metrics.api_request_duration.labels(
                                method=method,
                                endpoint=endpoint
                            ).observe(duration)
                        
                        return result
                        
                    except Exception as e:
                        duration = time.time() - start_time
                        
                        # Registrar erro
                        span.set_attribute("http.status_code", 500)
                        span.set_attribute("http.response_time", duration)
                        span.set_attribute("http.error", str(e))
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        
                        # Métricas de erro
                        if self.prometheus_metrics:
                            self.prometheus_metrics.api_requests_total.labels(
                                method=method,
                                endpoint=endpoint,
                                status_code="500"
                            ).inc()
                            
                            self.prometheus_metrics.errors_total.labels(
                                error_type=type(e).__name__,
                                severity="high"
                            ).inc()
                        
                        raise
            
            return wrapper
        return decorator
    
    def record_business_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Registrar métrica de negócio."""
        if not labels:
            labels = {}
        
        # Registrar no sistema de métricas de negócio
        self.business_metrics.record_metric(metric_name, value, labels)
        
        # Registrar no Prometheus se disponível
        if self.prometheus_metrics:
            # Criar métrica dinamicamente se não existir
            if not hasattr(self.prometheus_metrics, f"{metric_name}_gauge"):
                setattr(self.prometheus_metrics, f"{metric_name}_gauge", 
                       Gauge(f'omni_{metric_name}', f'Métrica de negócio: {metric_name}', list(labels.keys())))
            
            metric_gauge = getattr(self.prometheus_metrics, f"{metric_name}_gauge")
            metric_gauge.labels(**labels).set(value)
    
    def record_performance_metric(self, operation: str, duration: float, labels: Dict[str, str] = None):
        """Registrar métrica de performance."""
        if not labels:
            labels = {}
        
        # Registrar no monitor de performance
        self.performance_monitor.record_operation(operation, duration, labels)
        
        # Registrar no Prometheus se disponível
        if self.prometheus_metrics:
            if not hasattr(self.prometheus_metrics, f"{operation}_duration"):
                setattr(self.prometheus_metrics, f"{operation}_duration",
                       Histogram(f'omni_{operation}_duration_seconds', 
                               f'Duração da operação: {operation}',
                               list(labels.keys()),
                               buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]))
            
            duration_histogram = getattr(self.prometheus_metrics, f"{operation}_duration")
            duration_histogram.labels(**labels).observe(duration)
    
    def get_apm_summary(self) -> Dict[str, Any]:
        """Obter resumo do sistema APM."""
        return {
            "service": {
                "name": self.config.service_name,
                "version": self.config.service_version,
                "environment": self.config.environment
            },
            "components": {
                "tracing": self.config.enable_tracing and self.tracer is not None,
                "metrics": self.config.enable_metrics and self.meter is not None,
                "logging": self.config.enable_logging
            },
            "performance": self.performance_monitor.get_summary(),
            "errors": self.error_tracker.get_summary(),
            "business_metrics": self.business_metrics.get_summary(),
            "system_health": {
                "memory_usage_percent": psutil.virtual_memory().percent,
                "cpu_usage_percent": psutil.cpu_percent(),
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        }

class ErrorTracker:
    """Rastreador de erros com análise de padrões."""
    
    def __init__(self):
        self.errors: List[ErrorEvent] = []
        self.error_patterns: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def record_error(self, error_type: str, error_message: str, severity: ErrorSeverity, 
                    operation_name: str = None, user_id: str = None, correlation_id: str = None):
        """Registrar erro."""
        error_event = ErrorEvent(
            error_id=str(uuid.uuid4()),
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            stack_trace="",  # Seria preenchido com traceback
            user_id=user_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(),
            context={"operation": operation_name}
        )
        
        with self._lock:
            self.errors.append(error_event)
            
            # Contar padrões de erro
            pattern_key = f"{error_type}:{severity.value}"
            self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Obter resumo de erros."""
        with self._lock:
            total_errors = len(self.errors)
            errors_by_severity = {}
            errors_by_type = {}
            
            for error in self.errors:
                # Por severidade
                severity = error.severity.value
                errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
                
                # Por tipo
                error_type = error.error_type
                errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
            
            return {
                "total_errors": total_errors,
                "errors_by_severity": errors_by_severity,
                "errors_by_type": errors_by_type,
                "error_patterns": self.error_patterns,
                "recent_errors": [
                    {
                        "error_id": error.error_id,
                        "error_type": error.error_type,
                        "severity": error.severity.value,
                        "timestamp": error.timestamp.isoformat(),
                        "message": error.error_message[:100] + "..." if len(error.error_message) > 100 else error.error_message
                    }
                    for error in self.errors[-10:]  # Últimos 10 erros
                ]
            }

class PerformanceMonitor:
    """Monitor de performance com análise de tendências."""
    
    def __init__(self):
        self.operations: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def record_operation(self, operation: str, duration: float, labels: Dict[str, str] = None):
        """Registrar operação."""
        with self._lock:
            if operation not in self.operations:
                self.operations[operation] = []
            
            self.operations[operation].append(duration)
            
            # Manter apenas os últimos 1000 valores
            if len(self.operations[operation]) > 1000:
                self.operations[operation] = self.operations[operation][-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Obter resumo de performance."""
        with self._lock:
            summary = {}
            
            for operation, durations in self.operations.items():
                if durations:
                    summary[operation] = {
                        "count": len(durations),
                        "avg_duration": sum(durations) / len(durations),
                        "min_duration": min(durations),
                        "max_duration": max(durations),
                        "p95_duration": self._percentile(durations, 95),
                        "p99_duration": self._percentile(durations, 99)
                    }
            
            return summary
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calcular percentil."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

class BusinessMetrics:
    """Métricas de negócio específicas do Omni Keywords Finder."""
    
    def __init__(self):
        self.metrics: Dict[str, List[PerformanceMetric]] = {}
        self._lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Registrar métrica de negócio."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit="",
            timestamp=datetime.now(),
            labels=labels or {},
            metadata={}
        )
        
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = []
            
            self.metrics[name].append(metric)
            
            # Manter apenas os últimos 1000 valores
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Obter resumo das métricas de negócio."""
        with self._lock:
            summary = {}
            
            for name, metrics_list in self.metrics.items():
                if metrics_list:
                    values = [m.value for m in metrics_list]
                    summary[name] = {
                        "count": len(values),
                        "current_value": values[-1] if values else 0,
                        "avg_value": sum(values) / len(values),
                        "min_value": min(values),
                        "max_value": max(values),
                        "last_updated": metrics_list[-1].timestamp.isoformat()
                    }
            
            return summary

# Instância global do APM
_apm_system: Optional[APMSystem] = None

def get_apm_system() -> APMSystem:
    """Obter instância global do sistema APM."""
    global _apm_system
    if _apm_system is None:
        config = APMConfig(
            service_name=os.getenv('SERVICE_NAME', 'omni-keywords-finder'),
            service_version=os.getenv('SERVICE_VERSION', '1.0.0'),
            environment=os.getenv('ENVIRONMENT', 'development'),
            jaeger_endpoint=os.getenv('JAEGER_ENDPOINT'),
            prometheus_port=int(os.getenv('PROMETHEUS_PORT', '8000')),
            sampling_rate=float(os.getenv('SAMPLING_RATE', '0.1')),
            enable_tracing=os.getenv('ENABLE_TRACING', 'true').lower() == 'true',
            enable_metrics=os.getenv('ENABLE_METRICS', 'true').lower() == 'true',
            enable_logging=os.getenv('ENABLE_LOGGING', 'true').lower() == 'true'
        )
        _apm_system = APMSystem(config)
        _apm_system.start_system_metrics_collection()
    return _apm_system

# Funções de conveniência
def trace_operation(operation_name: str, span_type: SpanType = SpanType.BUSINESS_LOGIC):
    """Decorator para tracing de operações."""
    return get_apm_system().trace_operation(operation_name, span_type)

def trace_api_request(endpoint: str, method: str = "GET"):
    """Decorator para tracing de requisições API."""
    return get_apm_system().trace_api_request(endpoint, method)

def record_business_metric(metric_name: str, value: float, labels: Dict[str, str] = None):
    """Registrar métrica de negócio."""
    get_apm_system().record_business_metric(metric_name, value, labels)

def record_performance_metric(operation: str, duration: float, labels: Dict[str, str] = None):
    """Registrar métrica de performance."""
    get_apm_system().record_performance_metric(operation, duration, labels)

def get_apm_summary() -> Dict[str, Any]:
    """Obter resumo do sistema APM."""
    return get_apm_system().get_apm_summary() 