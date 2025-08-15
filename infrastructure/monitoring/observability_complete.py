#!/usr/bin/env python3
"""
Sistema Completo de Observabilidade - Fase 3
Responsável por logging estruturado, métricas customizadas e dashboards.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import time
import threading
import json
import psutil
import requests
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import sqlite3
from collections import defaultdict, deque
import statistics
import structlog
import uuid
from contextvars import ContextVar

# Context variables para rastreabilidade
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class LogLevel(Enum):
    """Níveis de log padronizados."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCategory(Enum):
    """Categorias de log."""
    SYSTEM = "system"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"

class MetricType(Enum):
    """Tipos de métricas."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class HealthStatus(Enum):
    """Status de health check."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class MetricDefinition:
    """Definição de métrica."""
    name: str
    type: MetricType
    description: str
    labels: List[str] = None
    alert_thresholds: Dict[str, float] = None
    unit: str = ""
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        if self.alert_thresholds is None:
            self.alert_thresholds = {}

@dataclass
class MetricValue:
    """Valor de métrica."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}

class StructuredLogger:
    """Sistema de logging estruturado com structlog."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar structlog
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            self._add_correlation_id,
            structlog.processors.JSONRenderer()
        ]
        
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger()
    
    def _add_correlation_id(self, logger, method_name, event_dict):
        """Adicionar correlation ID ao log."""
        if correlation_id.get():
            event_dict['correlation_id'] = correlation_id.get()
        if user_id.get():
            event_dict['user_id'] = user_id.get()
        if request_id.get():
            event_dict['request_id'] = request_id.get()
        return event_dict
    
    def set_correlation_id(self, correlation_id_value: str):
        """Definir correlation ID."""
        correlation_id.set(correlation_id_value)
    
    def set_user_context(self, user_id_value: str, request_id_value: Optional[str] = None):
        """Definir contexto do usuário."""
        user_id.set(user_id_value)
        if request_id_value:
            request_id.set(request_id_value)
    
    def log(self, level: LogLevel, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log estruturado."""
        log_data = {
            'message': message,
            'category': category.value,
            'service': 'omni_keywords_finder',
            'environment': 'production',
            'version': '1.0.0',
            **kwargs
        }
        
        if level == LogLevel.DEBUG:
            self.logger.debug(**log_data)
        elif level == LogLevel.INFO:
            self.logger.info(**log_data)
        elif level == LogLevel.WARNING:
            self.logger.warning(**log_data)
        elif level == LogLevel.ERROR:
            self.logger.error(**log_data)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(**log_data)

class MetricsSystem:
    """Sistema de métricas customizadas."""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self.metrics: Dict[str, MetricDefinition] = {}
        self.current_values: Dict[str, float] = {}
        self.history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        self._init_database()
        self._register_default_metrics()
    
    def _init_database(self):
        """Inicializar banco de dados de métricas."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    labels TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
                ON metrics(name, timestamp)
            """)
    
    def _register_default_metrics(self):
        """Registrar métricas padrão."""
        default_metrics = [
            MetricDefinition(
                name="api_requests_total",
                type=MetricType.COUNTER,
                description="Total de requisições da API",
                labels=["endpoint", "method", "status"],
                alert_thresholds={"warning": 1000, "critical": 5000}
            ),
            MetricDefinition(
                name="api_latency_seconds",
                type=MetricType.HISTOGRAM,
                description="Latência das requisições da API",
                labels=["endpoint"],
                alert_thresholds={"warning": 1.0, "critical": 5.0},
                unit="seconds"
            ),
            MetricDefinition(
                name="cpu_usage_percent",
                type=MetricType.GAUGE,
                description="Uso de CPU em percentual",
                alert_thresholds={"warning": 80.0, "critical": 95.0},
                unit="percent"
            ),
            MetricDefinition(
                name="memory_usage_percent",
                type=MetricType.GAUGE,
                description="Uso de memória em percentual",
                alert_thresholds={"warning": 80.0, "critical": 95.0},
                unit="percent"
            ),
            MetricDefinition(
                name="error_rate_percent",
                type=MetricType.GAUGE,
                description="Taxa de erro em percentual",
                alert_thresholds={"warning": 5.0, "critical": 10.0},
                unit="percent"
            )
        ]
        
        for metric in default_metrics:
            self.register_metric(metric)
    
    def register_metric(self, metric: MetricDefinition):
        """Registrar nova métrica."""
        self.metrics[metric.name] = metric
        self.current_values[metric.name] = 0.0
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Registrar valor de métrica."""
        if name not in self.metrics:
            raise ValueError(f"Métrica '{name}' não registrada")
        
        metric_value = MetricValue(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )
        
        # Atualizar valor atual
        self.current_values[name] = value
        
        # Adicionar ao histórico
        self.history[name].append(metric_value)
        
        # Salvar no banco
        self._save_metric(metric_value)
        
        # Verificar alertas
        self._check_alerts(name, value)
    
    def _save_metric(self, metric_value: MetricValue):
        """Salvar métrica no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metrics (name, value, timestamp, labels)
                VALUES (?, ?, ?, ?)
            """, (
                metric_value.name,
                metric_value.value,
                metric_value.timestamp.isoformat(),
                json.dumps(metric_value.labels)
            ))
    
    def _check_alerts(self, name: str, value: float):
        """Verificar alertas para métrica."""
        if name in self.metrics:
            metric = self.metrics[name]
            thresholds = metric.alert_thresholds
            
            if "critical" in thresholds and value > thresholds["critical"]:
                self._trigger_alert(name, "critical", value, thresholds["critical"])
            elif "warning" in thresholds and value > thresholds["warning"]:
                self._trigger_alert(name, "warning", value, thresholds["warning"])
    
    def _trigger_alert(self, metric_name: str, severity: str, value: float, threshold: float):
        """Disparar alerta."""
        alert = {
            "metric_name": metric_name,
            "severity": severity,
            "value": value,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log do alerta
        logger = StructuredLogger()
        logger.log(
            LogLevel.WARNING if severity == "warning" else LogLevel.ERROR,
            f"Alerta de métrica: {metric_name} = {value} (threshold: {threshold})",
            LogCategory.PERFORMANCE,
            alert=alert
        )
    
    def get_metric_summary(self, name: str, window_minutes: int = 60) -> Optional[Dict[str, Any]]:
        """Obter resumo de métrica."""
        if name not in self.metrics:
            return None
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_values = [
            mv.value for mv in self.history[name]
            if mv.timestamp > cutoff_time
        ]
        
        if not recent_values:
            return None
        
        return {
            "name": name,
            "current_value": self.current_values[name],
            "avg_value": statistics.mean(recent_values),
            "min_value": min(recent_values),
            "max_value": max(recent_values),
            "count": len(recent_values),
            "window_minutes": window_minutes
        }

class HealthChecker:
    """Sistema de health checks."""
    
    def __init__(self):
        self.health_checks = {}
        self.check_results = {}
        self.last_check = {}
        
        # Configurações padrão
        self.default_timeout = 30
        self.default_interval = 60
    
    def register_health_check(
        self,
        name: str,
        check_func: Callable[[], HealthStatus],
        interval: int = 60,
        timeout: int = 30,
        description: str = ""
    ):
        """Registrar health check."""
        self.health_checks[name] = {
            'function': check_func,
            'interval': interval,
            'timeout': timeout,
            'description': description,
            'last_check': None,
            'last_status': HealthStatus.UNKNOWN
        }
    
    def run_health_check(self, name: str) -> HealthStatus:
        """Executar health check específico."""
        if name not in self.health_checks:
            raise ValueError(f"Health check '{name}' não registrado")
        
        check_config = self.health_checks[name]
        
        try:
            status = check_config['function']()
            check_config['last_status'] = status
            check_config['last_check'] = datetime.utcnow()
            
            self.check_results[name] = {
                'status': status,
                'timestamp': check_config['last_check'],
                'description': check_config['description']
            }
            
            return status
            
        except Exception as e:
            logger = StructuredLogger()
            logger.log(
                LogLevel.ERROR,
                f"Erro no health check '{name}': {e}",
                LogCategory.SYSTEM
            )
            
            status = HealthStatus.UNHEALTHY
            check_config['last_status'] = status
            check_config['last_check'] = datetime.utcnow()
            
            self.check_results[name] = {
                'status': status,
                'timestamp': check_config['last_check'],
                'description': check_config['description'],
                'error': str(e)
            }
            
            return status
    
    def run_all_health_checks(self) -> Dict[str, HealthStatus]:
        """Executar todos os health checks."""
        results = {}
        
        for name in self.health_checks:
            results[name] = self.run_health_check(name)
        
        return results
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Obter resumo de saúde do sistema."""
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_checks': len(self.health_checks),
            'healthy': 0,
            'unhealthy': 0,
            'degraded': 0,
            'unknown': 0,
            'checks': {}
        }
        
        for name, result in self.check_results.items():
            status = result['status']
            summary['checks'][name] = result
            
            if status == HealthStatus.HEALTHY:
                summary['healthy'] += 1
            elif status == HealthStatus.UNHEALTHY:
                summary['unhealthy'] += 1
            elif status == HealthStatus.DEGRADED:
                summary['degraded'] += 1
            else:
                summary['unknown'] += 1
        
        return summary

class ObservabilityManager:
    """Gerenciador principal de observabilidade."""
    
    def __init__(self):
        self.logger = StructuredLogger()
        self.metrics = MetricsSystem()
        self.health_checker = HealthChecker()
        
        # Registrar health checks padrão
        self._register_default_health_checks()
        
        # Iniciar thread de coleta de métricas do sistema
        self._start_system_metrics_collection()
    
    def _register_default_health_checks(self):
        """Registrar health checks padrão."""
        
        def check_database():
            try:
                with sqlite3.connect(self.metrics.db_path) as conn:
                    conn.execute("SELECT 1")
                return HealthStatus.HEALTHY
            except Exception:
                return HealthStatus.UNHEALTHY
        
        def check_memory():
            memory_percent = psutil.virtual_memory().percent
            if memory_percent < 80:
                return HealthStatus.HEALTHY
            elif memory_percent < 95:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.UNHEALTHY
        
        def check_cpu():
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 80:
                return HealthStatus.HEALTHY
            elif cpu_percent < 95:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.UNHEALTHY
        
        self.health_checker.register_health_check(
            "database",
            check_database,
            interval=30,
            description="Verificação de conectividade com banco de dados"
        )
        
        self.health_checker.register_health_check(
            "memory",
            check_memory,
            interval=60,
            description="Verificação de uso de memória"
        )
        
        self.health_checker.register_health_check(
            "cpu",
            check_cpu,
            interval=60,
            description="Verificação de uso de CPU"
        )
    
    def _start_system_metrics_collection(self):
        """Iniciar coleta automática de métricas do sistema."""
        def collect_system_metrics():
            while True:
                try:
                    # CPU
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.metrics.record_metric("cpu_usage_percent", cpu_percent)
                    
                    # Memória
                    memory = psutil.virtual_memory()
                    memory_percent = memory.percent
                    self.metrics.record_metric("memory_usage_percent", memory_percent)
                    
                    # Disco
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    self.metrics.record_metric("disk_usage_percent", disk_percent)
                    
                    time.sleep(60)  # Coletar a cada minuto
                    
                except Exception as e:
                    self.logger.log(
                        LogLevel.ERROR,
                        f"Erro na coleta de métricas do sistema: {e}",
                        LogCategory.SYSTEM
                    )
                    time.sleep(60)
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'health': self.health_checker.get_health_summary(),
            'metrics': {
                name: self.metrics.get_metric_summary(name)
                for name in self.metrics.metrics.keys()
            },
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'disk_total_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
            }
        }
    
    def log_business_event(self, event_type: str, user_id: str, **kwargs):
        """Log de evento de negócio."""
        self.logger.set_user_context(user_id)
        self.logger.log(
            LogLevel.INFO,
            f"Evento de negócio: {event_type}",
            LogCategory.BUSINESS,
            event_type=event_type,
            user_id=user_id,
            **kwargs
        )
    
    def log_security_event(self, event_type: str, severity: str, **kwargs):
        """Log de evento de segurança."""
        level = LogLevel.WARNING if severity == "medium" else LogLevel.ERROR
        self.logger.log(
            level,
            f"Evento de segurança: {event_type}",
            LogCategory.SECURITY,
            event_type=event_type,
            severity=severity,
            **kwargs
        )
    
    def log_performance_event(self, operation: str, duration_ms: float, **kwargs):
        """Log de evento de performance."""
        self.metrics.record_metric("api_latency_seconds", duration_ms / 1000, {"operation": operation})
        
        self.logger.log(
            LogLevel.INFO,
            f"Evento de performance: {operation}",
            LogCategory.PERFORMANCE,
            operation=operation,
            duration_ms=duration_ms,
            **kwargs
        )

# Instância global
observability_manager = ObservabilityManager()

# Funções de conveniência
def get_logger() -> StructuredLogger:
    """Obter logger estruturado."""
    return observability_manager.logger

def get_metrics() -> MetricsSystem:
    """Obter sistema de métricas."""
    return observability_manager.metrics

def get_health_checker() -> HealthChecker:
    """Obter health checker."""
    return observability_manager.health_checker

def log_business_event(event_type: str, user_id: str, **kwargs):
    """Log de evento de negócio."""
    observability_manager.log_business_event(event_type, user_id, **kwargs)

def log_security_event(event_type: str, severity: str, **kwargs):
    """Log de evento de segurança."""
    observability_manager.log_security_event(event_type, severity, **kwargs)

def log_performance_event(operation: str, duration_ms: float, **kwargs):
    """Log de evento de performance."""
    observability_manager.log_performance_event(operation, duration_ms, **kwargs)

if __name__ == "__main__":
    # Exemplo de uso
    logger = get_logger()
    metrics = get_metrics()
    health_checker = get_health_checker()
    
    # Log de exemplo
    logger.log(LogLevel.INFO, "Sistema de observabilidade inicializado", LogCategory.SYSTEM)
    
    # Métrica de exemplo
    metrics.record_metric("api_requests_total", 100, {"endpoint": "/api/keywords", "method": "GET", "status": "200"})
    
    # Health check
    health_status = health_checker.run_all_health_checks()
    print(f"Status de saúde: {health_status}")
    
    # Dashboard
    dashboard_data = observability_manager.get_dashboard_data()
    print(f"Dados do dashboard: {json.dumps(dashboard_data, indent=2, default=str)}") 