"""
Sistema de Coleta de Métricas para Omni Keywords Finder
Coleta e armazena métricas de performance e uso da aplicação
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from collections import defaultdict, deque

from prometheus_client import Counter, Histogram, Gauge, Summary
from redis import Redis
import psutil

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas suportados"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricData:
    """Dados de uma métrica"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Coletor principal de métricas"""
    
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.metrics: Dict[str, Any] = {}
        self.buffer: deque = deque(maxlen=1000)
        self.flush_interval = 60  # segundos
        self.is_running = False
        
        # Métricas Prometheus
        self.request_counter = Counter('http_requests_total', 'Total de requests HTTP', ['method', 'endpoint', 'status'])
        self.request_duration = Histogram('http_request_duration_seconds', 'Duração dos requests HTTP', ['method', 'endpoint'])
        self.active_connections = Gauge('active_connections', 'Conexões ativas')
        self.error_counter = Counter('errors_total', 'Total de erros', ['type', 'component'])
        self.memory_usage = Gauge('memory_usage_bytes', 'Uso de memória em bytes')
        self.cpu_usage = Gauge('cpu_usage_percent', 'Uso de CPU em percentual')
        
    def start_collection(self):
        """Inicia a coleta automática de métricas"""
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self._background_collection())
            logger.info("Coleta de métricas iniciada")
    
    def stop_collection(self):
        """Para a coleta automática de métricas"""
        self.is_running = False
        logger.info("Coleta de métricas parada")
    
    async def _background_collection(self):
        """Coleta métricas em background"""
        while self.is_running:
            try:
                await self.collect_system_metrics()
                await self.flush_metrics()
                await asyncio.sleep(self.flush_interval)
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {str(e)}")
                await asyncio.sleep(10)
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Registra métricas de request HTTP"""
        # Prometheus metrics
        self.request_counter.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Custom metrics
        self._add_metric("http_requests", 1, {
            "method": method,
            "endpoint": endpoint,
            "status": str(status_code)
        })
        
        self._add_metric("http_request_duration", duration, {
            "method": method,
            "endpoint": endpoint
        })
    
    def record_error(self, error_type: str, component: str, error_message: str = ""):
        """Registra métricas de erro"""
        # Prometheus metrics
        self.error_counter.labels(type=error_type, component=component).inc()
        
        # Custom metrics
        self._add_metric("errors", 1, {
            "type": error_type,
            "component": component,
            "message": error_message[:100]  # Limita tamanho da mensagem
        })
    
    def record_database_query(self, query_type: str, duration: float, success: bool):
        """Registra métricas de query do banco de dados"""
        self._add_metric("database_queries", 1, {
            "type": query_type,
            "success": str(success)
        })
        
        self._add_metric("database_query_duration", duration, {
            "type": query_type
        })
        
        if not success:
            self.record_error("database_error", "database", f"Query {query_type} falhou")
    
    def record_cache_operation(self, operation: str, duration: float, success: bool):
        """Registra métricas de operações de cache"""
        self._add_metric("cache_operations", 1, {
            "operation": operation,
            "success": str(success)
        })
        
        self._add_metric("cache_operation_duration", duration, {
            "operation": operation
        })
        
        if not success:
            self.record_error("cache_error", "cache", f"Operação {operation} falhou")
    
    def record_api_call(self, service: str, endpoint: str, duration: float, success: bool):
        """Registra métricas de chamadas de API externas"""
        self._add_metric("api_calls", 1, {
            "service": service,
            "endpoint": endpoint,
            "success": str(success)
        })
        
        self._add_metric("api_call_duration", duration, {
            "service": service,
            "endpoint": endpoint
        })
        
        if not success:
            self.record_error("api_error", service, f"Chamada para {endpoint} falhou")
    
    async def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)
            self._add_metric("system_cpu_usage", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.used)
            self._add_metric("system_memory_usage", memory.used)
            self._add_metric("system_memory_percent", memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self._add_metric("system_disk_usage", disk.used)
            self._add_metric("system_disk_percent", (disk.used / disk.total) * 100)
            
            # Network I/O
            network = psutil.net_io_counters()
            self._add_metric("system_network_bytes_sent", network.bytes_sent)
            self._add_metric("system_network_bytes_recv", network.bytes_recv)
            
            # Active connections
            connections = len(psutil.net_connections())
            self.active_connections.set(connections)
            self._add_metric("system_active_connections", connections)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {str(e)}")
    
    def _add_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Adiciona métrica ao buffer"""
        metric_data = MetricData(
            name=name,
            value=value,
            labels=labels or {},
            timestamp=datetime.now()
        )
        
        self.buffer.append(metric_data)
    
    async def flush_metrics(self):
        """Envia métricas para Redis"""
        if not self.buffer:
            return
        
        try:
            metrics_batch = []
            while self.buffer:
                metric = self.buffer.popleft()
                metrics_batch.append({
                    "name": metric.name,
                    "value": metric.value,
                    "labels": metric.labels,
                    "timestamp": metric.timestamp.isoformat()
                })
            
            # Armazena no Redis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            key = f"metrics:{timestamp}"
            
            await self.redis_client.lpush(key, json.dumps(metrics_batch))
            await self.redis_client.expire(key, 86400)  # Expira em 24 horas
            
            logger.debug(f"Métricas enviadas: {len(metrics_batch)} registros")
            
        except Exception as e:
            logger.error(f"Erro ao enviar métricas: {str(e)}")
            # Recoloca métricas no buffer em caso de erro
            for metric_data in metrics_batch:
                self.buffer.appendleft(MetricData(
                    name=metric_data["name"],
                    value=metric_data["value"],
                    labels=metric_data["labels"],
                    timestamp=datetime.fromisoformat(metric_data["timestamp"])
                ))


class PerformanceMonitor:
    """Monitor de performance específico da aplicação"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str):
        """Inicia timer para uma operação"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str, success: bool = True):
        """Finaliza timer e registra métrica"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.metrics_collector._add_metric(f"{operation}_duration", duration, {"success": str(success)})
            del self.start_times[operation]
    
    def record_keyword_analysis(self, keyword_count: int, duration: float, success: bool):
        """Registra métricas de análise de keywords"""
        self.metrics_collector._add_metric("keyword_analysis_count", keyword_count)
        self.metrics_collector._add_metric("keyword_analysis_duration", duration, {"success": str(success)})
        
        if not success:
            self.metrics_collector.record_error("analysis_error", "keyword_analyzer")
    
    def record_competitor_analysis(self, competitor_count: int, duration: float, success: bool):
        """Registra métricas de análise de competidores"""
        self.metrics_collector._add_metric("competitor_analysis_count", competitor_count)
        self.metrics_collector._add_metric("competitor_analysis_duration", duration, {"success": str(success)})
        
        if not success:
            self.metrics_collector.record_error("analysis_error", "competitor_analyzer")
    
    def record_report_generation(self, report_type: str, duration: float, success: bool):
        """Registra métricas de geração de relatórios"""
        self.metrics_collector._add_metric("report_generation_duration", duration, {
            "type": report_type,
            "success": str(success)
        })
        
        if not success:
            self.metrics_collector.record_error("report_error", "report_generator")


class MetricsAnalyzer:
    """Analisador de métricas coletadas"""
    
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém resumo das métricas das últimas horas"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            metrics_data = []
            
            # Busca métricas do período
            current_time = start_time
            while current_time <= end_time:
                timestamp = current_time.strftime("%Y%m%d_%H%M")
                key = f"metrics:{timestamp}"
                
                data = await self.redis_client.lrange(key, 0, -1)
                for item in data:
                    metrics_data.extend(json.loads(item))
                
                current_time += timedelta(minutes=1)
            
            return self._analyze_metrics(metrics_data)
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de métricas: {str(e)}")
            return {}
    
    def _analyze_metrics(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Analisa dados de métricas"""
        if not metrics_data:
            return {}
        
        analysis = {
            "total_metrics": len(metrics_data),
            "time_range": {
                "start": min(m["timestamp"] for m in metrics_data),
                "end": max(m["timestamp"] for m in metrics_data)
            },
            "metrics_by_type": defaultdict(list),
            "errors": [],
            "performance": {}
        }
        
        # Agrupa métricas por tipo
        for metric in metrics_data:
            analysis["metrics_by_type"][metric["name"]].append(metric)
        
        # Analisa erros
        error_metrics = analysis["metrics_by_type"].get("errors", [])
        if error_metrics:
            analysis["errors"] = self._analyze_errors(error_metrics)
        
        # Analisa performance
        performance_metrics = {
            "http_request_duration": analysis["metrics_by_type"].get("http_request_duration", []),
            "database_query_duration": analysis["metrics_by_type"].get("database_query_duration", []),
            "api_call_duration": analysis["metrics_by_type"].get("api_call_duration", [])
        }
        
        analysis["performance"] = self._analyze_performance(performance_metrics)
        
        return analysis
    
    def _analyze_errors(self, error_metrics: List[Dict]) -> Dict[str, Any]:
        """Analisa métricas de erro"""
        error_counts = defaultdict(int)
        error_by_component = defaultdict(int)
        
        for error in error_metrics:
            error_type = error["labels"].get("type", "unknown")
            component = error["labels"].get("component", "unknown")
            
            error_counts[error_type] += 1
            error_by_component[component] += 1
        
        return {
            "total_errors": len(error_metrics),
            "error_types": dict(error_counts),
            "errors_by_component": dict(error_by_component)
        }
    
    def _analyze_performance(self, performance_metrics: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analisa métricas de performance"""
        analysis = {}
        
        for metric_type, metrics in performance_metrics.items():
            if not metrics:
                continue
            
            values = [m["value"] for m in metrics]
            analysis[metric_type] = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p95": sorted(values)[int(len(values) * 0.95)],
                "p99": sorted(values)[int(len(values) * 0.99)]
            }
        
        return analysis


# Instâncias globais
metrics_collector = None
performance_monitor = None
metrics_analyzer = None


def initialize_metrics(redis_client: Redis):
    """Inicializa o sistema de métricas"""
    global metrics_collector, performance_monitor, metrics_analyzer
    
    metrics_collector = MetricsCollector(redis_client)
    performance_monitor = PerformanceMonitor(metrics_collector)
    metrics_analyzer = MetricsAnalyzer(redis_client)
    
    # Inicia coleta automática
    metrics_collector.start_collection()
    
    logger.info("Sistema de métricas inicializado")


async def get_metrics_summary(hours: int = 24) -> Dict[str, Any]:
    """Obtém resumo das métricas"""
    if metrics_analyzer:
        return await metrics_analyzer.get_metrics_summary(hours)
    return {}


def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """Registra métricas de request"""
    if metrics_collector:
        metrics_collector.record_request(method, endpoint, status_code, duration)


def record_error_metrics(error_type: str, component: str, error_message: str = ""):
    """Registra métricas de erro"""
    if metrics_collector:
        metrics_collector.record_error(error_type, component, error_message) 