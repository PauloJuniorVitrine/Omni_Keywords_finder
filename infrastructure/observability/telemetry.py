#!/usr/bin/env python3
"""
Sistema de Telemetria Centralizado com Payload/Headers Logging - Omni Keywords Finder
Tracing ID: OBSERVABILITY_20241219_002
Data: 2024-12-19
Versão: 2.0

Implementa observabilidade distribuída usando OpenTelemetry com:
- Tracing distribuído
- Métricas customizadas
- Logs estruturados
- Payload/Headers logging completo
- Anonimização de dados sensíveis
- Integração com ELK Stack
- Sampling adaptativo
- Integração com Jaeger e Grafana
"""

import logging
import os
import time
import json
import re
import hashlib
from contextlib import contextmanager
from typing import Any, Dict, Optional, Union, List
from uuid import uuid4
from datetime import datetime

from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatioSampler
from prometheus_client import start_http_server

class PayloadLogger:
    """
    Sistema de logging de payloads e headers com anonimização de dados sensíveis.
    """
    
    def __init__(self):
        # Padrões de dados sensíveis para anonimização
        self.sensitive_patterns = {
            'password': r'password["\']?\string_data*[:=]\string_data*["\']?[^"\string_data,}]+["\']?',
            'token': r'token["\']?\string_data*[:=]\string_data*["\']?[^"\string_data,}]+["\']?',
            'api_key': r'api_key["\']?\string_data*[:=]\string_data*["\']?[^"\string_data,}]+["\']?',
            'secret': r'secret["\']?\string_data*[:=]\string_data*["\']?[^"\string_data,}]+["\']?',
            'authorization': r'authorization["\']?\string_data*[:=]\string_data*["\']?[^"\string_data,}]+["\']?',
            'bearer': r'bearer\string_data+[a-zA-Z0-9._-]+',
            'cpf': r'\data{3}\.\data{3}\.\data{3}-\data{2}',
            'cnpj': r'\data{2}\.\data{3}\.\data{3}/\data{4}-\data{2}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\(\data{2}\)\string_data*\data{4,5}-\data{4}',
            'credit_card': r'\data{4}[\string_data-]?\data{4}[\string_data-]?\data{4}[\string_data-]?\data{4}'
        }
        
        # Headers sensíveis que devem ser anonimizados
        self.sensitive_headers = {
            'authorization', 'value-api-key', 'value-auth-token', 'cookie',
            'value-csrf-token', 'value-session-id', 'value-user-token'
        }
        
        # Configurações de logging
        self.config = {
            'log_payloads': True,
            'log_headers': True,
            'anonymize_sensitive': True,
            'max_payload_size': 10240,  # 10KB
            'max_header_size': 2048,    # 2KB
            'log_level': 'INFO',
            'elk_integration': False,
            'elk_endpoint': os.getenv('ELK_ENDPOINT', 'http://localhost:9200'),
            'elk_index': 'omni-keywords-finder-logs'
        }
    
    def anonymize_sensitive_data(self, data: str) -> str:
        """
        Anonimiza dados sensíveis em strings.
        
        Args:
            data: String contendo dados potencialmente sensíveis
            
        Returns:
            String com dados sensíveis anonimizados
        """
        if not self.config['anonymize_sensitive']:
            return data
        
        anonymized_data = data
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            if pattern_name in ['password', 'token', 'api_key', 'secret', 'authorization']:
                # Para credenciais, substituir por [REDACTED]
                anonymized_data = re.sub(
                    pattern, 
                    f'{pattern_name}="[REDACTED]"', 
                    anonymized_data, 
                    flags=re.IGNORECASE
                )
            elif pattern_name == 'bearer':
                # Para bearer tokens, manter apenas "Bearer [REDACTED]"
                anonymized_data = re.sub(
                    pattern,
                    'Bearer [REDACTED]',
                    anonymized_data,
                    flags=re.IGNORECASE
                )
            elif pattern_name in ['cpf', 'cnpj']:
                # Para documentos, substituir por [DOCUMENT_REDACTED]
                anonymized_data = re.sub(
                    pattern,
                    '[DOCUMENT_REDACTED]',
                    anonymized_data
                )
            elif pattern_name == 'email':
                # Para emails, manter apenas domínio
                anonymized_data = re.sub(
                    pattern,
                    lambda m: f'[REDACTED]@{m.group(0).split("@")[1]}',
                    anonymized_data
                )
            elif pattern_name == 'phone':
                # Para telefones, substituir por [PHONE_REDACTED]
                anonymized_data = re.sub(
                    pattern,
                    '[PHONE_REDACTED]',
                    anonymized_data
                )
            elif pattern_name == 'credit_card':
                # Para cartões, manter apenas últimos 4 dígitos
                anonymized_data = re.sub(
                    pattern,
                    lambda m: f'****-****-****-{m.group(0).replace(" ", "").replace("-", "")[-4:]}',
                    anonymized_data
                )
        
        return anonymized_data
    
    def anonymize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Anonimiza headers sensíveis.
        
        Args:
            headers: Dicionário de headers
            
        Returns:
            Dicionário com headers sensíveis anonimizados
        """
        if not self.config['anonymize_sensitive']:
            return headers
        
        anonymized_headers = {}
        
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                anonymized_headers[key] = '[REDACTED]'
            else:
                anonymized_headers[key] = value
        
        return anonymized_headers
    
    def truncate_data(self, data: str, max_size: int) -> str:
        """
        Trunca dados que excedem o tamanho máximo.
        
        Args:
            data: Dados a serem truncados
            max_size: Tamanho máximo em bytes
            
        Returns:
            Dados truncados se necessário
        """
        if len(data.encode('utf-8')) <= max_size:
            return data
        
        # Truncar e adicionar indicador
        truncated = data[:max_size//2] + "...[TRUNCATED]..." + data[-max_size//2:]
        return truncated
    
    def log_payload(self, payload: Union[str, Dict, bytes], 
                   context: Optional[Dict[str, Any]] = None) -> None:
        """
        Loga payload com anonimização e truncamento.
        
        Args:
            payload: Payload a ser logado
            context: Contexto adicional para o log
        """
        if not self.config['log_payloads']:
            return
        
        try:
            # Converter payload para string
            if isinstance(payload, bytes):
                payload_str = payload.decode('utf-8', errors='ignore')
            elif isinstance(payload, dict):
                payload_str = json.dumps(payload, ensure_ascii=False, default=str)
            else:
                payload_str = str(payload)
            
            # Anonimizar dados sensíveis
            anonymized_payload = self.anonymize_sensitive_data(payload_str)
            
            # Truncar se necessário
            truncated_payload = self.truncate_data(
                anonymized_payload, 
                self.config['max_payload_size']
            )
            
            # Preparar contexto do log
            log_context = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'payload_log',
                'size_bytes': len(payload_str.encode('utf-8')),
                'truncated': len(anonymized_payload) > self.config['max_payload_size'],
                'anonymized': self.config['anonymize_sensitive']
            }
            
            if context:
                log_context.update(context)
            
            # Log estruturado
            logging.info(
                f"Payload logged: {truncated_payload}",
                extra={
                    'payload_data': truncated_payload,
                    'log_context': log_context
                }
            )
            
        except Exception as e:
            logging.error(f"Erro ao logar payload: {e}")
    
    def log_headers(self, headers: Dict[str, str], 
                   context: Optional[Dict[str, Any]] = None) -> None:
        """
        Loga headers com anonimização.
        
        Args:
            headers: Headers a serem logados
            context: Contexto adicional para o log
        """
        if not self.config['log_headers']:
            return
        
        try:
            # Anonimizar headers sensíveis
            anonymized_headers = self.anonymize_headers(headers)
            
            # Converter para string JSON
            headers_str = json.dumps(anonymized_headers, ensure_ascii=False)
            
            # Truncar se necessário
            truncated_headers = self.truncate_data(
                headers_str, 
                self.config['max_header_size']
            )
            
            # Preparar contexto do log
            log_context = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'headers_log',
                'header_count': len(headers),
                'sensitive_headers_count': len([
                    h for h in headers.keys() 
                    if h.lower() in self.sensitive_headers
                ]),
                'truncated': len(headers_str) > self.config['max_header_size'],
                'anonymized': self.config['anonymize_sensitive']
            }
            
            if context:
                log_context.update(context)
            
            # Log estruturado
            logging.info(
                f"Headers logged: {truncated_headers}",
                extra={
                    'headers_data': truncated_headers,
                    'log_context': log_context
                }
            )
            
        except Exception as e:
            logging.error(f"Erro ao logar headers: {e}")
    
    def log_http_request(self, method: str, url: str, 
                        headers: Optional[Dict[str, str]] = None,
                        payload: Optional[Union[str, Dict, bytes]] = None,
                        context: Optional[Dict[str, Any]] = None) -> None:
        """
        Loga requisição HTTP completa com payload e headers.
        
        Args:
            method: Método HTTP
            url: URL da requisição
            headers: Headers da requisição
            payload: Payload da requisição
            context: Contexto adicional
        """
        request_context = {
            'method': method,
            'url': url,
            'request_type': 'http_request'
        }
        
        if context:
            request_context.update(context)
        
        # Logar headers
        if headers:
            self.log_headers(headers, request_context)
        
        # Logar payload
        if payload:
            self.log_payload(payload, request_context)
    
    def log_http_response(self, status_code: int, 
                         headers: Optional[Dict[str, str]] = None,
                         payload: Optional[Union[str, Dict, bytes]] = None,
                         context: Optional[Dict[str, Any]] = None) -> None:
        """
        Loga resposta HTTP completa com payload e headers.
        
        Args:
            status_code: Código de status HTTP
            headers: Headers da resposta
            payload: Payload da resposta
            context: Contexto adicional
        """
        response_context = {
            'status_code': status_code,
            'response_type': 'http_response'
        }
        
        if context:
            response_context.update(context)
        
        # Logar headers
        if headers:
            self.log_headers(headers, response_context)
        
        # Logar payload
        if payload:
            self.log_payload(payload, response_context)

class TelemetryManager:
    """
    Gerenciador centralizado de telemetria com configuração automática
    e integração com múltiplos backends de observabilidade.
    """
    
    def __init__(self, service_name: str = "omni-keywords-finder"):
        self.service_name = service_name
        self.tracer = None
        self.meter = None
        self.logger = None
        self.payload_logger = PayloadLogger()
        self._initialized = False
        
        # Configurações padrão
        self.config = {
            "jaeger_endpoint": os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces"),
            "prometheus_port": int(os.getenv("PROMETHEUS_PORT", "9090")),
            "sampling_rate": float(os.getenv("SAMPLING_RATE", "0.1")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    
    def initialize(self) -> None:
        """Inicializa o sistema de telemetria com todas as configurações."""
        if self._initialized:
            return
            
        try:
            # Configurar resource com metadados do serviço
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": self.config["environment"],
                "tracing.id": f"OBSERVABILITY_{int(time.time())}_{uuid4().hex[:8]}"
            })
            
            # Configurar tracing
            self._setup_tracing(resource)
            
            # Configurar métricas
            self._setup_metrics(resource)
            
            # Configurar logs
            self._setup_logging()
            
            # Configurar instrumentação automática
            self._setup_auto_instrumentation()
            
            self._initialized = True
            self.logger.info(f"Telemetria com payload/headers logging inicializada para {self.service_name}")
            
        except Exception as e:
            logging.error(f"Erro ao inicializar telemetria: {e}")
            raise
    
    def _setup_tracing(self, resource: Resource) -> None:
        """Configura o sistema de tracing distribuído."""
        # Configurar sampler adaptativo
        sampler = ParentBasedTraceIdRatioSampler(self.config["sampling_rate"])
        
        # Configurar provider de tracing
        trace_provider = TracerProvider(
            resource=resource,
            sampler=sampler
        )
        
        # Configurar exportador Jaeger
        jaeger_exporter = JaegerExporter(
            endpoint=self.config["jaeger_endpoint"]
        )
        
        # Adicionar processador de spans
        trace_provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        
        # Configurar tracer global
        trace.set_tracer_provider(trace_provider)
        self.tracer = trace.get_tracer(__name__)
    
    def _setup_metrics(self, resource: Resource) -> None:
        """Configura o sistema de métricas."""
        # Configurar exportador Prometheus
        prometheus_exporter = PrometheusExporter()
        
        # Configurar provider de métricas
        metric_reader = PeriodicExportingMetricReader(prometheus_exporter)
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
        
        # Configurar meter global
        metrics.set_meter_provider(meter_provider)
        self.meter = metrics.get_meter(__name__)
        
        # Iniciar servidor Prometheus
        start_http_server(self.config["prometheus_port"])
    
    def _setup_logging(self) -> None:
        """Configura logs estruturados."""
        logging.basicConfig(
            level=getattr(logging, self.config["log_level"]),
            format='%(asctime)string_data [%(levelname)string_data] [%(name)string_data] %(message)string_data - %(trace_id)string_data:%(span_id)string_data',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"logs/telemetry_{int(time.time())}.log")
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_auto_instrumentation(self) -> None:
        """Configura instrumentação automática para frameworks."""
        try:
            # Instrumentar Flask (se disponível)
            FlaskInstrumentor().instrument()
            
            # Instrumentar requests
            RequestsInstrumentor().instrument()
            
            # Instrumentar SQLAlchemy
            SQLAlchemyInstrumentor().instrument()
            
        except ImportError as e:
            self.logger.warning(f"Framework não disponível para instrumentação: {e}")
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager para tracing de operações com atributos customizados.
        
        Args:
            operation_name: Nome da operação sendo executada
            attributes: Atributos adicionais para o span
        """
        if not self._initialized:
            yield
            return
            
        span = self.tracer.start_span(operation_name, attributes=attributes or {})
        
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
        finally:
            span.end()
    
    def record_metric(self, metric_name: str, value: Union[int, float], 
                     labels: Optional[Dict[str, str]] = None) -> None:
        """
        Registra uma métrica customizada.
        
        Args:
            metric_name: Nome da métrica
            value: Valor da métrica
            labels: Labels adicionais
        """
        if not self._initialized:
            return
            
        try:
            counter = self.meter.create_counter(metric_name)
            counter.add(value, labels or {})
        except Exception as e:
            self.logger.error(f"Erro ao registrar métrica {metric_name}: {e}")
    
    def log_event(self, event_type: str, message: str, 
                  extra_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Registra um evento estruturado com metadados.
        
        Args:
            event_type: Tipo do evento
            message: Mensagem do evento
            extra_data: Dados adicionais
        """
        if not self._initialized:
            return
            
        log_data = {
            "event_type": event_type,
            "message": message,
            "timestamp": time.time(),
            "service": self.service_name,
            "environment": self.config["environment"]
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        self.logger.info(f"EVENT: {event_type} - {message}", extra=log_data)


# Instância global do gerenciador de telemetria
telemetry_manager = TelemetryManager()


def get_telemetry_manager() -> TelemetryManager:
    """Retorna a instância global do gerenciador de telemetria."""
    return telemetry_manager


def initialize_telemetry(service_name: str = "omni-keywords-finder") -> TelemetryManager:
    """
    Inicializa e retorna o sistema de telemetria.
    
    Args:
        service_name: Nome do serviço para identificação
        
    Returns:
        Instância configurada do TelemetryManager
    """
    global telemetry_manager
    telemetry_manager = TelemetryManager(service_name)
    telemetry_manager.initialize()
    return telemetry_manager


# Decoradores para facilitar o uso
def traced_operation(operation_name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Decorador para tracing automático de operações.
    
    Args:
        operation_name: Nome da operação
        attributes: Atributos adicionais
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with telemetry_manager.trace_operation(operation_name, attributes):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def monitored_metric(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """
    Decorador para monitoramento automático de métricas.
    
    Args:
        metric_name: Nome da métrica
        labels: Labels adicionais
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                telemetry_manager.record_metric(
                    f"{metric_name}_success", 1, labels
                )
                return result
            except Exception as e:
                telemetry_manager.record_metric(
                    f"{metric_name}_error", 1, labels
                )
                raise
            finally:
                duration = time.time() - start_time
                telemetry_manager.record_metric(
                    f"{metric_name}_duration", duration, labels
                )
        return wrapper
    return decorator 