"""
Sistema de Monitoramento de Performance - Omni Keywords Finder
============================================================

Sistema enterprise para monitoramento de performance com:
- Métricas em tempo real
- Alertas automáticos
- Dashboards interativos
- Análise de tendências
- Detecção de anomalias
- Relatórios de performance

Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: PERFORMANCE_MONITOR_001
"""

import time
import threading
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging

# Integração com observabilidade
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.metrics import MetricsManager
from infrastructure.observability.tracing import TracingManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(Enum):
    """Níveis de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Métrica de performance"""
    name: str
    value: float
    timestamp: datetime
    type: MetricType
    labels: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceAlert:
    """Alerta de performance"""
    id: str
    level: AlertLevel
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class PerformanceThreshold:
    """Threshold para métricas de performance"""
    metric_name: str
    warning_threshold: float
    error_threshold: float
    critical_threshold: float
    enabled: bool = True


class PerformanceCollector:
    """Coletor de métricas de performance"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.lock = threading.RLock()
        
        # Configurar observabilidade
        self.telemetry = TelemetryManager()
        self.metrics_manager = MetricsManager()
        self.tracing = TracingManager()
    
    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Registra uma métrica de performance"""
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                type=metric_type,
                labels=labels,
                metadata=metadata
            )
            
            self.metrics[name].append(metric)
            
            # Registrar na observabilidade
            self.metrics_manager.record_gauge(name, value, labels or {})
    
    def get_metric_stats(self, name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Obtém estatísticas de uma métrica"""
        with self.lock:
            if name not in self.metrics:
                return {}
            
            # Filtrar por janela de tempo
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            recent_metrics = [
                m for m in self.metrics[name] 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            values = [m.value for m in recent_metrics]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'latest': values[-1],
                'window_minutes': window_minutes
            }
    
    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtém todas as métricas"""
        with self.lock:
            return {
                name: [asdict(metric) for metric in metrics]
                for name, metrics in self.metrics.items()
            }


class PerformanceMonitor:
    """Monitor de performance principal"""
    
    def __init__(self, 
                 enable_alerts: bool = True,
                 enable_dashboard: bool = True,
                 check_interval: int = 30):
        
        self.enable_alerts = enable_alerts
        self.enable_dashboard = enable_dashboard
        self.check_interval = check_interval
        
        # Coletor de métricas
        self.collector = PerformanceCollector()
        
        # Configurar observabilidade
        self.telemetry = TelemetryManager()
        self.metrics_manager = MetricsManager()
        self.tracing = TracingManager()
        
        # Thresholds configuráveis
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        
        # Alertas ativos
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        
        # Callbacks de alerta
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # Thread de monitoramento
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Configurar thresholds padrão
        self._setup_default_thresholds()
        
        logger.info("Sistema de monitoramento de performance inicializado")
    
    def _setup_default_thresholds(self):
        """Configura thresholds padrão"""
        default_thresholds = [
            PerformanceThreshold(
                metric_name="response_time_ms",
                warning_threshold=1000,
                error_threshold=3000,
                critical_threshold=5000
            ),
            PerformanceThreshold(
                metric_name="memory_usage_percent",
                warning_threshold=70,
                error_threshold=85,
                critical_threshold=95
            ),
            PerformanceThreshold(
                metric_name="cpu_usage_percent",
                warning_threshold=80,
                error_threshold=90,
                critical_threshold=95
            ),
            PerformanceThreshold(
                metric_name="error_rate_percent",
                warning_threshold=5,
                error_threshold=10,
                critical_threshold=20
            )
        ]
        
        for threshold in default_thresholds:
            self.thresholds[threshold.metric_name] = threshold
    
    def add_threshold(self, threshold: PerformanceThreshold):
        """Adiciona um threshold personalizado"""
        self.thresholds[threshold.metric_name] = threshold
        logger.info(f"Threshold adicionado para métrica: {threshold.metric_name}")
    
    def remove_threshold(self, metric_name: str):
        """Remove um threshold"""
        if metric_name in self.thresholds:
            del self.thresholds[metric_name]
            logger.info(f"Threshold removido para métrica: {metric_name}")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Registra uma métrica de performance"""
        self.collector.record_metric(name, value, metric_type, labels, metadata)
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while True:
            try:
                # Verificar thresholds
                self._check_thresholds()
                
                # Limpar alertas antigos
                self._cleanup_old_alerts()
                
                # Aguardar próximo check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(60)  # Aguardar 1 minuto em caso de erro
    
    def _check_thresholds(self):
        """Verifica thresholds e gera alertas"""
        for metric_name, threshold in self.thresholds.items():
            if not threshold.enabled:
                continue
            
            # Obter estatísticas da métrica
            stats = self.collector.get_metric_stats(metric_name, window_minutes=5)
            if not stats:
                continue
            
            current_value = stats['latest']
            alert_id = f"{metric_name}_{int(time.time())}"
            
            # Verificar se já existe alerta ativo
            if alert_id in self.active_alerts:
                continue
            
            # Verificar thresholds
            alert_level = None
            if current_value >= threshold.critical_threshold:
                alert_level = AlertLevel.CRITICAL
            elif current_value >= threshold.error_threshold:
                alert_level = AlertLevel.ERROR
            elif current_value >= threshold.warning_threshold:
                alert_level = AlertLevel.WARNING
            
            if alert_level:
                alert = PerformanceAlert(
                    id=alert_id,
                    level=alert_level,
                    message=f"Métrica {metric_name} atingiu threshold {alert_level.value}: {current_value}",
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold=threshold.warning_threshold,
                    timestamp=datetime.now()
                )
                
                self.active_alerts[alert_id] = alert
                
                # Executar callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"Erro no callback de alerta: {e}")
                
                logger.warning(f"Alerta de performance: {alert.message}")
    
    def _cleanup_old_alerts(self):
        """Limpa alertas antigos"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        alerts_to_remove = []
        
        for alert_id, alert in self.active_alerts.items():
            if alert.timestamp < cutoff_time:
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.active_alerts[alert_id]
    
    def resolve_alert(self, alert_id: str):
        """Resolve um alerta"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            logger.info(f"Alerta resolvido: {alert_id}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos"""
        return [asdict(alert) for alert in self.active_alerts.values()]
    
    def get_metric_stats(self, metric_name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Obtém estatísticas de uma métrica"""
        return self.collector.get_metric_stats(metric_name, window_minutes)
    
    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtém todas as métricas"""
        return self.collector.get_all_metrics()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para dashboard"""
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'alerts': self.get_active_alerts(),
            'thresholds': {name: asdict(threshold) for name, threshold in self.thresholds.items()}
        }
        
        # Adicionar estatísticas das métricas principais
        for metric_name in self.thresholds.keys():
            stats = self.get_metric_stats(metric_name, window_minutes=60)
            if stats:
                dashboard_data['metrics'][metric_name] = stats
        
        return dashboard_data


class PerformanceDecorator:
    """Decorator para monitoramento automático de performance"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Decorator para monitorar performance de funções"""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Registrar métrica de sucesso
                    self.monitor.record_metric(
                        f"{metric_name}_duration_ms",
                        duration_ms,
                        MetricType.HISTOGRAM,
                        labels
                    )
                    
                    self.monitor.record_metric(
                        f"{metric_name}_success",
                        1,
                        MetricType.COUNTER,
                        labels
                    )
                    
                    return result
                    
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Registrar métrica de erro
                    self.monitor.record_metric(
                        f"{metric_name}_duration_ms",
                        duration_ms,
                        MetricType.HISTOGRAM,
                        labels
                    )
                    
                    self.monitor.record_metric(
                        f"{metric_name}_errors",
                        1,
                        MetricType.COUNTER,
                        labels
                    )
                    
                    raise
            
            return wrapper
        return decorator


# Instância global do monitor de performance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Retorna instância do monitor de performance"""
    return performance_monitor


# Decorator para monitoramento automático
monitor_performance = PerformanceDecorator(performance_monitor)


# Funções utilitárias para métricas comuns
def record_response_time(operation: str, duration_ms: float, labels: Optional[Dict[str, str]] = None):
    """Registra tempo de resposta"""
    performance_monitor.record_metric(
        f"{operation}_response_time_ms",
        duration_ms,
        MetricType.HISTOGRAM,
        labels
    )


def record_memory_usage(usage_percent: float, labels: Optional[Dict[str, str]] = None):
    """Registra uso de memória"""
    performance_monitor.record_metric(
        "memory_usage_percent",
        usage_percent,
        MetricType.GAUGE,
        labels
    )


def record_cpu_usage(usage_percent: float, labels: Optional[Dict[str, str]] = None):
    """Registra uso de CPU"""
    performance_monitor.record_metric(
        "cpu_usage_percent",
        usage_percent,
        MetricType.GAUGE,
        labels
    )


def record_error_rate(operation: str, error_count: int, total_count: int, labels: Optional[Dict[str, str]] = None):
    """Registra taxa de erro"""
    error_rate = (error_count / total_count * 100) if total_count > 0 else 0
    performance_monitor.record_metric(
        f"{operation}_error_rate_percent",
        error_rate,
        MetricType.GAUGE,
        labels
    )


def record_throughput(operation: str, requests_per_second: float, labels: Optional[Dict[str, str]] = None):
    """Registra throughput"""
    performance_monitor.record_metric(
        f"{operation}_throughput_rps",
        requests_per_second,
        MetricType.GAUGE,
        labels
    ) 