#!/usr/bin/env python3
"""
Sistema Completo de APM (Application Performance Monitoring) - Omni Keywords Finder
===============================================================================

Tracing ID: APM_INTEGRATION_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema enterprise de APM que integra:
- Jaeger para distributed tracing
- Sentry para error tracking
- Prometheus para métricas
- Custom dashboards
- Alertas inteligentes
- Performance insights
- Anomaly detection

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 3.2
Ruleset: enterprise_control_layer.yaml
"""

import os
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid

# OpenTelemetry imports
try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.prometheus import PrometheusExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatioSampler
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logging.warning("OpenTelemetry não disponível. APM limitado.")

# Sentry imports
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logging.warning("Sentry não disponível. Error tracking limitado.")

# Prometheus imports
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus não disponível. Métricas limitadas.")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APMServiceType(Enum):
    """Tipos de serviços monitorados"""
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    BACKGROUND_JOB = "background_job"
    FRONTEND = "frontend"


class APMMetricType(Enum):
    """Tipos de métricas APM"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_LATENCY = "network_latency"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_CONNECTIONS = "database_connections"
    QUEUE_SIZE = "queue_size"


@dataclass
class APMMetric:
    """Métrica APM"""
    name: str
    value: float
    type: APMMetricType
    service: APMServiceType
    timestamp: datetime
    labels: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class APMAlert:
    """Alerta APM"""
    id: str
    title: str
    message: str
    severity: str  # info, warning, error, critical
    service: APMServiceType
    metric: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class APMInsight:
    """Insight de performance"""
    id: str
    title: str
    description: str
    impact: str  # low, medium, high, critical
    service: APMServiceType
    metric: str
    current_value: float
    baseline_value: float
    improvement_percentage: float
    recommendations: List[str]
    timestamp: datetime


class APMCollector:
    """Coletor de métricas APM"""
    
    def __init__(self, max_samples: int = 10000):
        self.max_samples = max_samples
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.lock = threading.RLock()
        
        # Métricas Prometheus
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
    
    def _setup_prometheus_metrics(self):
        """Configura métricas Prometheus"""
        self.api_requests = Counter(
            'apm_api_requests_total',
            'Total de requisições da API',
            ['service', 'endpoint', 'method', 'status']
        )
        
        self.api_latency = Histogram(
            'apm_api_latency_seconds',
            'Latência das requisições da API',
            ['service', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.error_rate = Counter(
            'apm_errors_total',
            'Total de erros',
            ['service', 'error_type', 'severity']
        )
        
        self.memory_usage = Gauge(
            'apm_memory_usage_bytes',
            'Uso de memória',
            ['service']
        )
        
        self.cpu_usage = Gauge(
            'apm_cpu_usage_percent',
            'Uso de CPU',
            ['service']
        )
        
        self.cache_hit_rate = Gauge(
            'apm_cache_hit_rate',
            'Taxa de acerto do cache',
            ['service', 'cache_type']
        )
    
    def record_metric(self, metric: APMMetric):
        """Registra uma métrica APM"""
        with self.lock:
            self.metrics[metric.name].append(metric)
            
            # Registrar no Prometheus se disponível
            if PROMETHEUS_AVAILABLE:
                self._record_prometheus_metric(metric)
    
    def _record_prometheus_metric(self, metric: APMMetric):
        """Registra métrica no Prometheus"""
        try:
            if metric.type == APMMetricType.RESPONSE_TIME:
                self.api_latency.labels(
                    service=metric.service.value,
                    endpoint=metric.labels.get('endpoint', 'unknown')
                ).observe(metric.value)
            
            elif metric.type == APMMetricType.ERROR_RATE:
                self.error_rate.labels(
                    service=metric.service.value,
                    error_type=metric.labels.get('error_type', 'unknown'),
                    severity=metric.labels.get('severity', 'unknown')
                ).inc()
            
            elif metric.type == APMMetricType.MEMORY_USAGE:
                self.memory_usage.labels(
                    service=metric.service.value
                ).set(metric.value)
            
            elif metric.type == APMMetricType.CPU_USAGE:
                self.cpu_usage.labels(
                    service=metric.service.value
                ).set(metric.value)
            
            elif metric.type == APMMetricType.CACHE_HIT_RATE:
                self.cache_hit_rate.labels(
                    service=metric.service.value,
                    cache_type=metric.labels.get('cache_type', 'unknown')
                ).set(metric.value)
        
        except Exception as e:
            logger.error(f"Erro ao registrar métrica Prometheus: {e}")


class APMInsightEngine:
    """Motor de insights de performance"""
    
    def __init__(self):
        self.baselines: Dict[str, float] = {}
        self.anomaly_thresholds: Dict[str, float] = {}
        self.insights: List[APMInsight] = []
    
    def calculate_baseline(self, metric_name: str, values: List[float]) -> float:
        """Calcula baseline para uma métrica"""
        if not values:
            return 0.0
        
        # Usar percentil 95 como baseline
        sorted_values = sorted(values)
        percentile_95_index = int(len(sorted_values) * 0.95)
        return sorted_values[percentile_95_index]
    
    def detect_anomaly(self, metric_name: str, current_value: float) -> bool:
        """Detecta anomalia em métrica"""
        baseline = self.baselines.get(metric_name, 0.0)
        threshold = self.anomaly_thresholds.get(metric_name, 2.0)  # 2x o baseline
        
        return current_value > (baseline * threshold)
    
    def generate_insight(self, metric: APMMetric) -> Optional[APMInsight]:
        """Gera insight baseado na métrica"""
        baseline = self.baselines.get(metric.name, 0.0)
        
        if baseline == 0.0:
            return None
        
        improvement = ((baseline - metric.value) / baseline) * 100
        
        if abs(improvement) < 5:  # Menos de 5% de mudança
            return None
        
        impact = self._calculate_impact(improvement)
        recommendations = self._generate_recommendations(metric, improvement)
        
        insight = APMInsight(
            id=str(uuid.uuid4()),
            title=f"Performance {metric.type.value} - {metric.service.value}",
            description=f"Métrica {metric.name} está {improvement:.1f}% {'melhor' if improvement > 0 else 'pior'} que o baseline",
            impact=impact,
            service=metric.service,
            metric=metric.name,
            current_value=metric.value,
            baseline_value=baseline,
            improvement_percentage=improvement,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        
        self.insights.append(insight)
        return insight
    
    def _calculate_impact(self, improvement: float) -> str:
        """Calcula impacto da mudança"""
        abs_improvement = abs(improvement)
        
        if abs_improvement < 10:
            return "low"
        elif abs_improvement < 25:
            return "medium"
        elif abs_improvement < 50:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendations(self, metric: APMMetric, improvement: float) -> List[str]:
        """Gera recomendações baseadas na métrica"""
        recommendations = []
        
        if metric.type == APMMetricType.RESPONSE_TIME:
            if improvement < -20:  # Piorou significativamente
                recommendations.extend([
                    "Investigar gargalos no código",
                    "Verificar configurações de cache",
                    "Analisar queries de banco de dados",
                    "Considerar otimizações de algoritmo"
                ])
            elif improvement > 20:  # Melhorou significativamente
                recommendations.extend([
                    "Documentar otimizações aplicadas",
                    "Monitorar estabilidade das melhorias",
                    "Considerar aplicar em outros serviços"
                ])
        
        elif metric.type == APMMetricType.ERROR_RATE:
            if improvement < -10:  # Taxa de erro aumentou
                recommendations.extend([
                    "Investigar logs de erro",
                    "Verificar dependências externas",
                    "Analisar mudanças recentes no código",
                    "Implementar circuit breakers"
                ])
        
        elif metric.type == APMMetricType.CACHE_HIT_RATE:
            if improvement < -15:  # Cache hit rate diminuiu
                recommendations.extend([
                    "Revisar estratégia de cache",
                    "Verificar expiração de cache",
                    "Analisar padrões de acesso",
                    "Considerar aumentar tamanho do cache"
                ])
        
        return recommendations


class APMAlertManager:
    """Gerenciador de alertas APM"""
    
    def __init__(self):
        self.alerts: Dict[str, APMAlert] = {}
        self.alert_callbacks: List[Callable[[APMAlert], None]] = []
        self.thresholds: Dict[str, Dict[str, float]] = {}
        
        # Configurar thresholds padrão
        self._setup_default_thresholds()
    
    def _setup_default_thresholds(self):
        """Configura thresholds padrão"""
        self.thresholds = {
            APMMetricType.RESPONSE_TIME.value: {
                "warning": 1000,  # 1s
                "error": 3000,    # 3s
                "critical": 5000  # 5s
            },
            APMMetricType.ERROR_RATE.value: {
                "warning": 5,     # 5%
                "error": 10,      # 10%
                "critical": 20    # 20%
            },
            APMMetricType.MEMORY_USAGE.value: {
                "warning": 70,    # 70%
                "error": 85,      # 85%
                "critical": 95    # 95%
            },
            APMMetricType.CPU_USAGE.value: {
                "warning": 80,    # 80%
                "error": 90,      # 90%
                "critical": 95    # 95%
            },
            APMMetricType.CACHE_HIT_RATE.value: {
                "warning": 70,    # 70%
                "error": 50,      # 50%
                "critical": 30    # 30%
            }
        }
    
    def check_alert(self, metric: APMMetric) -> Optional[APMAlert]:
        """Verifica se métrica deve gerar alerta"""
        metric_thresholds = self.thresholds.get(metric.type.value, {})
        
        if not metric_thresholds:
            return None
        
        severity = None
        threshold_value = 0
        
        # Determinar severidade
        if metric.value >= metric_thresholds.get("critical", float('inf')):
            severity = "critical"
            threshold_value = metric_thresholds["critical"]
        elif metric.value >= metric_thresholds.get("error", float('inf')):
            severity = "error"
            threshold_value = metric_thresholds["error"]
        elif metric.value >= metric_thresholds.get("warning", float('inf')):
            severity = "warning"
            threshold_value = metric_thresholds["warning"]
        
        if not severity:
            return None
        
        # Verificar se já existe alerta ativo
        alert_key = f"{metric.name}_{severity}"
        if alert_key in self.alerts and not self.alerts[alert_key].resolved:
            return None
        
        # Criar novo alerta
        alert = APMAlert(
            id=str(uuid.uuid4()),
            title=f"Alerta {severity.upper()}: {metric.type.value}",
            message=f"Métrica {metric.name} está em {metric.value} (threshold: {threshold_value})",
            severity=severity,
            service=metric.service,
            metric=metric.name,
            value=metric.value,
            threshold=threshold_value,
            timestamp=datetime.now()
        )
        
        self.alerts[alert_key] = alert
        
        # Executar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro no callback de alerta: {e}")
        
        return alert
    
    def resolve_alert(self, alert_id: str):
        """Resolve um alerta"""
        for alert in self.alerts.values():
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                break
    
    def add_alert_callback(self, callback: Callable[[APMAlert], None]):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)


class APMManager:
    """
    Gerenciador principal de APM que integra todos os componentes
    """
    
    def __init__(self, service_name: str = "omni-keywords-finder"):
        self.service_name = service_name
        self.collector = APMCollector()
        self.insight_engine = APMInsightEngine()
        self.alert_manager = APMAlertManager()
        
        # Configurações
        self.config = {
            "jaeger_endpoint": os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces"),
            "sentry_dsn": os.getenv("SENTRY_DSN", ""),
            "prometheus_port": int(os.getenv("PROMETHEUS_PORT", "9090")),
            "sampling_rate": float(os.getenv("APM_SAMPLING_RATE", "0.1")),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "enable_insights": os.getenv("APM_ENABLE_INSIGHTS", "true").lower() == "true",
            "enable_alerts": os.getenv("APM_ENABLE_ALERTS", "true").lower() == "true"
        }
        
        # Inicializar componentes
        self._initialize_tracing()
        self._initialize_error_tracking()
        self._initialize_metrics()
        
        # Thread de processamento
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        
        logger.info(f"APM Manager inicializado para serviço: {service_name}")
    
    def _initialize_tracing(self):
        """Inicializa sistema de tracing"""
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry não disponível. Tracing desabilitado.")
            return
        
        try:
            # Criar resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "service.environment": self.config["environment"],
                "deployment.environment": self.config["environment"]
            })
            
            # Configurar provider de tracing
            trace_provider = TracerProvider(
                resource=resource,
                sampler=ParentBasedTraceIdRatioSampler(self.config["sampling_rate"])
            )
            
            # Configurar exportador Jaeger
            jaeger_exporter = JaegerExporter(
                endpoint=self.config["jaeger_endpoint"]
            )
            
            # Adicionar processador
            trace_provider.add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            
            # Configurar tracer global
            trace.set_tracer_provider(trace_provider)
            
            logger.info("Sistema de tracing inicializado com Jaeger")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar tracing: {e}")
    
    def _initialize_error_tracking(self):
        """Inicializa sistema de error tracking"""
        if not SENTRY_AVAILABLE or not self.config["sentry_dsn"]:
            logger.warning("Sentry não disponível ou DSN não configurado.")
            return
        
        try:
            sentry_sdk.init(
                dsn=self.config["sentry_dsn"],
                environment=self.config["environment"],
                traces_sample_rate=self.config["sampling_rate"],
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                    RedisIntegration()
                ],
                before_send=self._filter_sensitive_data
            )
            
            logger.info("Sistema de error tracking inicializado com Sentry")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar Sentry: {e}")
    
    def _initialize_metrics(self):
        """Inicializa sistema de métricas"""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus não disponível. Métricas limitadas.")
            return
        
        try:
            # Iniciar servidor Prometheus
            start_http_server(self.config["prometheus_port"])
            
            logger.info(f"Servidor Prometheus iniciado na porta {self.config['prometheus_port']}")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar Prometheus: {e}")
    
    def _filter_sensitive_data(self, event, hint):
        """Filtra dados sensíveis antes de enviar para Sentry"""
        # Remover dados sensíveis
        if "request" in event:
            if "headers" in event["request"]:
                sensitive_headers = ["authorization", "cookie", "x-api-key"]
                for header in sensitive_headers:
                    if header in event["request"]["headers"]:
                        event["request"]["headers"][header] = "[REDACTED]"
        
        return event
    
    def record_metric(self, name: str, value: float, metric_type: APMMetricType,
                     service: APMServiceType, labels: Optional[Dict[str, str]] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """Registra uma métrica APM"""
        metric = APMMetric(
            name=name,
            value=value,
            type=metric_type,
            service=service,
            timestamp=datetime.now(),
            labels=labels or {},
            metadata=metadata
        )
        
        # Registrar no coletor
        self.collector.record_metric(metric)
        
        # Verificar alertas
        if self.config["enable_alerts"]:
            self.alert_manager.check_alert(metric)
        
        # Gerar insights
        if self.config["enable_insights"]:
            self.insight_engine.generate_insight(metric)
    
    def instrument_fastapi(self, app):
        """Instrumenta aplicação FastAPI"""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentado com OpenTelemetry")
        except Exception as e:
            logger.error(f"Erro ao instrumentar FastAPI: {e}")
    
    def instrument_sqlalchemy(self, engine):
        """Instrumenta SQLAlchemy"""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        try:
            SQLAlchemyInstrumentor.instrument(engine=engine)
            logger.info("SQLAlchemy instrumentado com OpenTelemetry")
        except Exception as e:
            logger.error(f"Erro ao instrumentar SQLAlchemy: {e}")
    
    def instrument_requests(self):
        """Instrumenta biblioteca requests"""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        try:
            RequestsInstrumentor().instrument()
            logger.info("Requests instrumentado com OpenTelemetry")
        except Exception as e:
            logger.error(f"Erro ao instrumentar Requests: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        summary = {
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "metrics_count": sum(len(metrics) for metrics in self.collector.metrics.values()),
            "active_alerts": len([a for a in self.alert_manager.alerts.values() if not a.resolved]),
            "insights_count": len(self.insight_engine.insights),
            "metrics_by_type": {}
        }
        
        # Contar métricas por tipo
        for metric_name, metrics in self.collector.metrics.items():
            if metrics:
                latest_metric = metrics[-1]
                metric_type = latest_metric.type.value
                if metric_type not in summary["metrics_by_type"]:
                    summary["metrics_by_type"][metric_type] = 0
                summary["metrics_by_type"][metric_type] += 1
        
        return summary
    
    def _processing_loop(self):
        """Loop de processamento de métricas"""
        while True:
            try:
                # Atualizar baselines
                for metric_name, metrics in self.collector.metrics.items():
                    if len(metrics) >= 10:  # Mínimo de amostras
                        values = [m.value for m in metrics]
                        self.insight_engine.baselines[metric_name] = \
                            self.insight_engine.calculate_baseline(metric_name, values)
                
                # Limpar insights antigos (mais de 24h)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.insight_engine.insights = [
                    insight for insight in self.insight_engine.insights
                    if insight.timestamp > cutoff_time
                ]
                
                time.sleep(60)  # Processar a cada minuto
            
            except Exception as e:
                logger.error(f"Erro no loop de processamento APM: {e}")
                time.sleep(60)


# Instância global
apm_manager = APMManager()


# Decorators para facilitar uso
def apm_trace(operation_name: str, service: APMServiceType = APMServiceType.API):
    """Decorator para tracing APM"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not OPENTELEMETRY_AVAILABLE:
                return func(*args, **kwargs)
            
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("service.name", service.value)
                span.set_attribute("operation.name", operation_name)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Registrar métrica de sucesso
                    apm_manager.record_metric(
                        name=f"{operation_name}_duration",
                        value=duration * 1000,  # Converter para ms
                        metric_type=APMMetricType.RESPONSE_TIME,
                        service=service,
                        labels={"status": "success"}
                    )
                    
                    return result
                
                except Exception as e:
                    duration = time.time() - start_time
                    
                    # Registrar métrica de erro
                    apm_manager.record_metric(
                        name=f"{operation_name}_duration",
                        value=duration * 1000,
                        metric_type=APMMetricType.RESPONSE_TIME,
                        service=service,
                        labels={"status": "error", "error_type": type(e).__name__}
                    )
                    
                    # Registrar taxa de erro
                    apm_manager.record_metric(
                        name=f"{operation_name}_error_rate",
                        value=1.0,
                        metric_type=APMMetricType.ERROR_RATE,
                        service=service,
                        labels={"error_type": type(e).__name__}
                    )
                    
                    raise
        
        return wrapper
    return decorator


def apm_monitor(metric_name: str, metric_type: APMMetricType, 
                service: APMServiceType = APMServiceType.API):
    """Decorator para monitoramento APM"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Registrar métrica
                apm_manager.record_metric(
                    name=metric_name,
                    value=duration * 1000,
                    metric_type=metric_type,
                    service=service,
                    labels={"status": "success"}
                )
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                
                # Registrar métrica de erro
                apm_manager.record_metric(
                    name=metric_name,
                    value=duration * 1000,
                    metric_type=metric_type,
                    service=service,
                    labels={"status": "error", "error_type": type(e).__name__}
                )
                
                raise
        
        return wrapper
    return decorator


# Funções de conveniência
def record_api_request(endpoint: str, method: str, status: int, duration: float):
    """Registra requisição da API"""
    apm_manager.record_metric(
        name="api_request",
        value=duration * 1000,
        metric_type=APMMetricType.RESPONSE_TIME,
        service=APMServiceType.API,
        labels={
            "endpoint": endpoint,
            "method": method,
            "status": str(status)
        }
    )


def record_database_query(query_type: str, duration: float, success: bool):
    """Registra query de banco de dados"""
    apm_manager.record_metric(
        name="database_query",
        value=duration * 1000,
        metric_type=APMMetricType.RESPONSE_TIME,
        service=APMServiceType.DATABASE,
        labels={
            "query_type": query_type,
            "status": "success" if success else "error"
        }
    )


def record_cache_operation(operation: str, hit: bool, duration: float):
    """Registra operação de cache"""
    apm_manager.record_metric(
        name="cache_operation",
        value=duration * 1000,
        metric_type=APMMetricType.RESPONSE_TIME,
        service=APMServiceType.CACHE,
        labels={
            "operation": operation,
            "hit": str(hit).lower()
        }
    )


def record_external_api_call(api_name: str, endpoint: str, duration: float, success: bool):
    """Registra chamada de API externa"""
    apm_manager.record_metric(
        name="external_api_call",
        value=duration * 1000,
        metric_type=APMMetricType.RESPONSE_TIME,
        service=APMServiceType.EXTERNAL_API,
        labels={
            "api_name": api_name,
            "endpoint": endpoint,
            "status": "success" if success else "error"
        }
    )


if __name__ == "__main__":
    # Exemplo de uso
    print("APM Manager - Omni Keywords Finder")
    print("==================================")
    
    # Inicializar APM
    apm = APMManager("omni-keywords-finder-test")
    
    # Exemplo de métricas
    apm.record_metric(
        name="test_metric",
        value=150.5,
        metric_type=APMMetricType.RESPONSE_TIME,
        service=APMServiceType.API,
        labels={"test": "true"}
    )
    
    # Exemplo com decorator
    @apm_trace("test_operation", APMServiceType.API)
    def test_function():
        time.sleep(0.1)
        return "success"
    
    test_function()
    
    # Mostrar resumo
    summary = apm.get_metrics_summary()
    print(json.dumps(summary, indent=2, default=str)) 