"""
Sistema de Tracing Distribuído com UUID Único por Integração - Omni Keywords Finder
Tracing ID: OBSERVABILITY_20241219_001
Data: 2024-12-19
Versão: 2.0

Implementa tracing distribuído com:
- UUID único por integração
- Propagação cross-service
- Integração com OpenTelemetry
- Logging estruturado com UUID
- Dashboard de rastreabilidade
- Análise de performance avançada
"""

import logging
import time
import json
import hashlib
from contextlib import contextmanager
from typing import Any, Dict, Optional, Union, List
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatioSampler
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.trace import SpanKind, Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    from opentelemetry.trace.propagation.b3 import B3MultiFormat
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logging.warning("OpenTelemetry não disponível. Tracing será limitado.")

class IntegrationType(Enum):
    """Tipos de integração suportados"""
    WEBHOOK = "webhook"
    API_CALL = "api_call"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL_SERVICE = "internal_service"
    BACKGROUND_JOB = "background_job"
    SCHEDULED_TASK = "scheduled_task"

@dataclass
class IntegrationTrace:
    """Informações de trace de integração"""
    integration_uuid: str
    integration_type: IntegrationType
    service_name: str
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "pending"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    parent_trace_id: Optional[str] = None
    child_traces: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.child_traces is None:
            self.child_traces = []

class DistributedTracing:
    """
    Sistema de tracing distribuído com UUID único por integração
    e propagação cross-service avançada.
    """
    
    def __init__(self, service_name: str = "omni-keywords-finder"):
        self.service_name = service_name
        self.tracer = None
        self.propagator = TraceContextTextMapPropagator()
        self.b3_propagator = B3MultiFormat() if OPENTELEMETRY_AVAILABLE else None
        self._initialized = False
        
        # Rastreamento de integrações
        self.active_integrations: Dict[str, IntegrationTrace] = {}
        self.integration_history: List[IntegrationTrace] = []
        
        # Configurações
        self.config = {
            "sampling_rate": 0.1,  # 10% dos traces
            "jaeger_endpoint": "http://localhost:14268/api/traces",
            "max_span_duration": 30.0,  # segundos
            "batch_size": 512,
            "export_timeout": 30.0,
            "environment": "development",
            "enable_uuid_propagation": True,
            "enable_cross_service_tracing": True,
            "max_integration_history": 10000,
            "uuid_header_name": "X-Integration-UUID",
            "trace_header_name": "X-Trace-ID"
        }
        
        if OPENTELEMETRY_AVAILABLE:
            self._setup_tracing()
    
    def _setup_tracing(self) -> None:
        """Configura o sistema de tracing distribuído."""
        try:
            # Configurar resource com metadados
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": self.config["environment"],
                "tracing.id": f"TRACING_{int(time.time())}_{uuid4().hex[:8]}",
                "tracing.features": "uuid_propagation,cross_service,opentelemetry"
            })
            
            # Configurar sampler adaptativo
            sampler = ParentBasedTraceIdRatioSampler(self.config["sampling_rate"])
            
            # Configurar provider
            provider = TracerProvider(
                resource=resource,
                sampler=sampler
            )
            
            # Configurar exportadores
            self._setup_exporters(provider)
            
            # Configurar tracer global
            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer(self.service_name)
            
            self._initialized = True
            logging.info(f"Tracing distribuído com UUID inicializado para {self.service_name}")
            
        except Exception as e:
            logging.error(f"Erro ao configurar tracing: {e}")
            raise
    
    def _setup_exporters(self, provider: TracerProvider) -> None:
        """Configura os exportadores de spans."""
        # Exportador Jaeger para produção
        jaeger_exporter = JaegerExporter(
            endpoint=self.config["jaeger_endpoint"]
        )
        
        provider.add_span_processor(
            BatchSpanProcessor(
                jaeger_exporter,
                max_queue_size=self.config["batch_size"],
                export_timeout=self.config["export_timeout"]
            )
        )
        
        # Exportador console para desenvolvimento
        if self.config["environment"] == "development":
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
    
    def generate_integration_uuid(self, integration_type: IntegrationType, 
                                 operation_name: str) -> str:
        """
        Gera UUID único para integração com metadados.
        
        Args:
            integration_type: Tipo da integração
            operation_name: Nome da operação
            
        Returns:
            UUID único para a integração
        """
        # Gerar UUID base
        base_uuid = str(uuid4())
        
        # Criar hash com metadados para rastreabilidade
        metadata = {
            "service": self.service_name,
            "type": integration_type.value,
            "operation": operation_name,
            "timestamp": int(time.time())
        }
        
        metadata_hash = hashlib.sha256(
            json.dumps(metadata, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        # Combinar UUID base com hash de metadados
        integration_uuid = f"{base_uuid[:8]}-{metadata_hash}-{base_uuid[9:]}"
        
        return integration_uuid
    
    def start_integration_trace(self, integration_type: IntegrationType,
                               operation_name: str,
                               parent_trace_id: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Inicia trace de integração com UUID único.
        
        Args:
            integration_type: Tipo da integração
            operation_name: Nome da operação
            parent_trace_id: ID do trace pai (se houver)
            metadata: Metadados adicionais
            
        Returns:
            UUID da integração
        """
        integration_uuid = self.generate_integration_uuid(integration_type, operation_name)
        
        # Criar trace de integração
        integration_trace = IntegrationTrace(
            integration_uuid=integration_uuid,
            integration_type=integration_type,
            service_name=self.service_name,
            operation_name=operation_name,
            start_time=datetime.now(),
            parent_trace_id=parent_trace_id,
            metadata=metadata or {}
        )
        
        # Armazenar trace ativo
        self.active_integrations[integration_uuid] = integration_trace
        
        # Log estruturado com UUID
        log_data = {
            "integration_uuid": integration_uuid,
            "integration_type": integration_type.value,
            "operation_name": operation_name,
            "service_name": self.service_name,
            "timestamp": integration_trace.start_time.isoformat(),
            "parent_trace_id": parent_trace_id
        }
        
        logging.info(f"Integration trace started: {json.dumps(log_data)}")
        
        return integration_uuid
    
    def end_integration_trace(self, integration_uuid: str, 
                             status: str = "success",
                             error_message: Optional[str] = None,
                             additional_metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Finaliza trace de integração.
        
        Args:
            integration_uuid: UUID da integração
            status: Status da integração (success, error, timeout)
            error_message: Mensagem de erro (se houver)
            additional_metadata: Metadados adicionais
        """
        if integration_uuid not in self.active_integrations:
            logging.warning(f"Integration UUID não encontrado: {integration_uuid}")
            return
        
        integration_trace = self.active_integrations[integration_uuid]
        integration_trace.end_time = datetime.now()
        integration_trace.duration = (integration_trace.end_time - integration_trace.start_time).total_seconds()
        integration_trace.status = status
        integration_trace.error_message = error_message
        
        if additional_metadata:
            integration_trace.metadata.update(additional_metadata)
        
        # Mover para histórico
        self.integration_history.append(integration_trace)
        del self.active_integrations[integration_uuid]
        
        # Limitar histórico
        if len(self.integration_history) > self.config["max_integration_history"]:
            self.integration_history = self.integration_history[-self.config["max_integration_history"]:]
        
        # Log estruturado com resultado
        log_data = {
            "integration_uuid": integration_uuid,
            "status": status,
            "duration": integration_trace.duration,
            "error_message": error_message,
            "timestamp": integration_trace.end_time.isoformat()
        }
        
        if status == "success":
            logging.info(f"Integration trace completed: {json.dumps(log_data)}")
        else:
            logging.error(f"Integration trace failed: {json.dumps(log_data)}")
    
    @contextmanager
    def integration_span(self, integration_type: IntegrationType,
                        operation_name: str,
                        parent_trace_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager para spans de integração com UUID único.
        
        Args:
            integration_type: Tipo da integração
            operation_name: Nome da operação
            parent_trace_id: ID do trace pai
            metadata: Metadados adicionais
        """
        integration_uuid = self.start_integration_trace(
            integration_type, operation_name, parent_trace_id, metadata
        )
        
        try:
            # Criar span OpenTelemetry se disponível
            if self._initialized and self.tracer:
                span_attributes = {
                    "integration.uuid": integration_uuid,
                    "integration.type": integration_type.value,
                    "integration.operation": operation_name,
                    "service.name": self.service_name
                }
                
                if metadata:
                    for key, value in metadata.items():
                        span_attributes[f"integration.metadata.{key}"] = str(value)
                
                with self.trace_span(
                    f"Integration: {operation_name}",
                    SpanKind.CLIENT,
                    span_attributes
                ) as span:
                    if span:
                        span.set_attribute("integration.uuid", integration_uuid)
                    yield integration_uuid
            else:
                yield integration_uuid
                
        except Exception as e:
            self.end_integration_trace(
                integration_uuid, 
                status="error", 
                error_message=str(e)
            )
            raise
        else:
            self.end_integration_trace(integration_uuid, status="success")
    
    def inject_integration_context(self, headers: Dict[str, str], 
                                  integration_uuid: str) -> Dict[str, str]:
        """
        Injeta contexto de integração em headers HTTP.
        
        Args:
            headers: Headers HTTP existentes
            integration_uuid: UUID da integração
            
        Returns:
            Headers com contexto de integração injetado
        """
        if not self.config["enable_uuid_propagation"]:
            return headers
        
        # Adicionar UUID da integração
        headers[self.config["uuid_header_name"]] = integration_uuid
        
        # Adicionar trace ID se disponível
        if self._initialized:
            trace_id = self.get_trace_id()
            if trace_id:
                headers[self.config["trace_header_name"]] = trace_id
            
            # Injeta contexto OpenTelemetry
            self.propagator.inject(headers)
        
        return headers
    
    def extract_integration_context(self, headers: Dict[str, str]) -> Optional[str]:
        """
        Extrai contexto de integração de headers HTTP.
        
        Args:
            headers: Headers HTTP
            
        Returns:
            UUID da integração ou None
        """
        if not self.config["enable_uuid_propagation"]:
            return None
        
        # Extrair UUID da integração
        integration_uuid = headers.get(self.config["uuid_header_name"])
        
        # Extrair contexto OpenTelemetry se disponível
        if self._initialized:
            self.propagator.extract(headers)
        
        return integration_uuid
    
    def get_integration_trace(self, integration_uuid: str) -> Optional[IntegrationTrace]:
        """
        Obtém trace de integração por UUID.
        
        Args:
            integration_uuid: UUID da integração
            
        Returns:
            Trace de integração ou None
        """
        # Buscar em traces ativos
        if integration_uuid in self.active_integrations:
            return self.active_integrations[integration_uuid]
        
        # Buscar em histórico
        for trace in self.integration_history:
            if trace.integration_uuid == integration_uuid:
                return trace
        
        return None
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas das integrações.
        
        Returns:
            Estatísticas das integrações
        """
        active_count = len(self.active_integrations)
        history_count = len(self.integration_history)
        
        # Estatísticas por tipo
        type_stats = {}
        for trace in self.integration_history:
            trace_type = trace.integration_type.value
            if trace_type not in type_stats:
                type_stats[trace_type] = {
                    "total": 0,
                    "success": 0,
                    "error": 0,
                    "avg_duration": 0.0
                }
            
            type_stats[trace_type]["total"] += 1
            if trace.status == "success":
                type_stats[trace_type]["success"] += 1
            else:
                type_stats[trace_type]["error"] += 1
            
            if trace.duration:
                type_stats[trace_type]["avg_duration"] += trace.duration
        
        # Calcular médias
        for trace_type, stats in type_stats.items():
            if stats["total"] > 0:
                stats["avg_duration"] /= stats["total"]
                stats["success_rate"] = (stats["success"] / stats["total"]) * 100
        
        return {
            "active_integrations": active_count,
            "total_integrations": history_count,
            "type_statistics": type_stats,
            "service_name": self.service_name,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_integration_traces(self, format: str = "json") -> str:
        """
        Exporta traces de integração.
        
        Args:
            format: Formato de exportação (json, csv)
            
        Returns:
            Dados exportados
        """
        if format == "json":
            data = {
                "service_name": self.service_name,
                "export_timestamp": datetime.now().isoformat(),
                "active_integrations": [
                    asdict(trace) for trace in self.active_integrations.values()
                ],
                "integration_history": [
                    asdict(trace) for trace in self.integration_history[-100:]  # Últimos 100
                ],
                "statistics": self.get_integration_statistics()
            }
            return json.dumps(data, indent=2, default=str)
        else:
            # Implementar CSV se necessário
            return "CSV format not implemented yet"
    
    @contextmanager
    def trace_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL, 
                   attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager para criar spans com configuração avançada.
        
        Args:
            name: Nome do span
            kind: Tipo do span (INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER)
            attributes: Atributos customizados
        """
        if not self._initialized or not self.tracer:
            yield None
            return
        
        start_time = time.time()
        span = self.tracer.start_span(
            name=name,
            kind=kind,
            attributes=attributes or {}
        )
        
        try:
            # Adicionar atributos padrão
            span.set_attribute("span.start_time", start_time)
            span.set_attribute("service.name", self.service_name)
            
            yield span
            
            # Marcar como sucesso
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            # Marcar como erro
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
        finally:
            # Adicionar duração
            duration = time.time() - start_time
            span.set_attribute("span.duration", duration)
            
            # Verificar duração máxima
            if duration > self.config["max_span_duration"]:
                span.set_attribute("span.slow_operation", True)
                logging.warning(f"Span lento detectado: {name} ({duration:.2f}string_data)")
            
            span.end()
    
    def trace_function(self, func_name: Optional[str] = None, 
                      attributes: Optional[Dict[str, Any]] = None):
        """
        Decorador para tracing automático de funções.
        
        Args:
            func_name: Nome customizado para o span
            attributes: Atributos adicionais
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                name = func_name or f"{func.__module__}.{func.__name__}"
                
                with self.trace_span(name, attributes=attributes) as span:
                    if span:
                        # Adicionar informações da função
                        span.set_attribute("function.name", func.__name__)
                        span.set_attribute("function.module", func.__module__)
                        span.set_attribute("function.args_count", len(args))
                        span.set_attribute("function.kwargs_count", len(kwargs))
                    
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def trace_http_request(self, method: str, url: str, 
                          status_code: Optional[int] = None,
                          duration: Optional[float] = None):
        """
        Registra trace de requisição HTTP.
        
        Args:
            method: Método HTTP
            url: URL da requisição
            status_code: Código de status
            duration: Duração da requisição
        """
        if not self._initialized or not self.tracer:
            return
        
        span = self.tracer.start_span(
            name=f"HTTP {method}",
            kind=SpanKind.CLIENT
        )
        
        try:
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", url)
            
            if status_code:
                span.set_attribute("http.status_code", status_code)
                span.set_status(Status(StatusCode.OK if status_code < 400 else StatusCode.ERROR))
            
            if duration:
                span.set_attribute("http.duration", duration)
            
        finally:
            span.end()
    
    def trace_database_query(self, query: str, table: str, 
                            duration: Optional[float] = None,
                            rows_affected: Optional[int] = None):
        """
        Registra trace de query de banco de dados.
        
        Args:
            query: Query SQL
            table: Tabela afetada
            duration: Duração da query
            rows_affected: Linhas afetadas
        """
        if not self._initialized or not self.tracer:
            return
        
        span = self.tracer.start_span(
            name=f"DB Query - {table}",
            kind=SpanKind.CLIENT
        )
        
        try:
            span.set_attribute("db.system", "sqlite")
            span.set_attribute("db.table", table)
            span.set_attribute("db.query", query[:100] + "..." if len(query) > 100 else query)
            
            if duration:
                span.set_attribute("db.duration", duration)
            
            if rows_affected is not None:
                span.set_attribute("db.rows_affected", rows_affected)
            
        finally:
            span.end()
    
    def trace_external_api_call(self, service: str, endpoint: str,
                               method: str = "GET",
                               duration: Optional[float] = None,
                               status_code: Optional[int] = None):
        """
        Registra trace de chamada para API externa.
        
        Args:
            service: Nome do serviço externo
            endpoint: Endpoint chamado
            method: Método HTTP
            duration: Duração da chamada
            status_code: Código de status
        """
        if not self._initialized or not self.tracer:
            return
        
        span = self.tracer.start_span(
            name=f"External API - {service}",
            kind=SpanKind.CLIENT
        )
        
        try:
            span.set_attribute("external.service", service)
            span.set_attribute("external.endpoint", endpoint)
            span.set_attribute("external.method", method)
            
            if duration:
                span.set_attribute("external.duration", duration)
            
            if status_code:
                span.set_attribute("external.status_code", status_code)
                span.set_status(Status(StatusCode.OK if status_code < 400 else StatusCode.ERROR))
            
        finally:
            span.end()
    
    def inject_context(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Injeta contexto de tracing em headers HTTP.
        
        Args:
            headers: Headers HTTP existentes
            
        Returns:
            Headers com contexto de tracing injetado
        """
        if not self._initialized:
            return headers
        
        self.propagator.inject(headers)
        return headers
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[Any]:
        """
        Extrai contexto de tracing de headers HTTP.
        
        Args:
            headers: Headers HTTP
            
        Returns:
            Contexto extraído ou None
        """
        if not self._initialized:
            return None
        
        return self.propagator.extract(headers)
    
    def get_trace_id(self) -> Optional[str]:
        """
        Retorna o ID do trace atual.
        
        Returns:
            ID do trace ou None se não houver trace ativo
        """
        if not self._initialized or not self.tracer:
            return None
        
        current_span = trace.get_current_span()
        if current_span:
            return format(current_span.get_span_context().trace_id, "032x")
        return None
    
    def get_span_id(self) -> Optional[str]:
        """
        Retorna o ID do span atual.
        
        Returns:
            ID do span ou None se não houver span ativo
        """
        if not self._initialized or not self.tracer:
            return None
        
        current_span = trace.get_current_span()
        if current_span:
            return format(current_span.get_span_context().span_id, "016x")
        return None
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        Adiciona evento ao span atual.
        
        Args:
            name: Nome do evento
            attributes: Atributos do evento
        """
        if not self._initialized or not self.tracer:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Define atributo no span atual.
        
        Args:
            key: Chave do atributo
            value: Valor do atributo
        """
        if not self._initialized or not self.tracer:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, value)


# Instância global do sistema de tracing
distributed_tracing = DistributedTracing()


def get_tracing() -> DistributedTracing:
    """Retorna a instância global do sistema de tracing."""
    return distributed_tracing


def initialize_tracing(service_name: str = "omni-keywords-finder") -> DistributedTracing:
    """
    Inicializa e retorna o sistema de tracing.
    
    Args:
        service_name: Nome do serviço
        
    Returns:
        Instância configurada do DistributedTracing
    """
    global distributed_tracing
    distributed_tracing = DistributedTracing(service_name)
    return distributed_tracing


# Decoradores para facilitar o uso
def traced_function(func_name: Optional[str] = None, 
                   attributes: Optional[Dict[str, Any]] = None):
    """Decorador para tracing automático de funções."""
    return distributed_tracing.trace_function(func_name, attributes)


def traced_span(name: str, kind: SpanKind = SpanKind.INTERNAL, 
               attributes: Optional[Dict[str, Any]] = None):
    """Context manager para spans."""
    return distributed_tracing.trace_span(name, kind, attributes)


def traced_integration(integration_type: IntegrationType,
                      operation_name: str,
                      parent_trace_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None):
    """Context manager para integrações com UUID único."""
    return distributed_tracing.integration_span(
        integration_type, operation_name, parent_trace_id, metadata
    ) 