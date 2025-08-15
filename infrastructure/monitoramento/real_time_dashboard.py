"""
Dashboard de Performance em Tempo Real - Omni Keywords Finder

Funcionalidades:
- Dashboard de métricas em tempo real
- Gráficos interativos
- Alertas de performance
- Métricas de negócio
- Drill-down de dados
- Exportação de relatórios

Autor: Sistema de Dashboard em Tempo Real
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import sqlite3
from collections import deque, defaultdict
import logging
from pathlib import Path

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest
except ImportError:
    # Fallback se Prometheus não estiver disponível
    class MockMetric:
        def __init__(self, name, description, **kwargs):
            self.name = name
            self.description = description
            self._value = 0
        
        def inc(self, amount=1):
            self._value += amount
        
        def set(self, value):
            self._value = value
        
        def observe(self, value):
            self._value = value
    
    Counter = Histogram = Gauge = Summary = MockMetric

class MetricType(Enum):
    """Tipos de métricas suportados"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Severidades de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """Estrutura de métrica de performance"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = None
    metadata: Dict[str, Any] = None

@dataclass
class BusinessMetric:
    """Estrutura de métrica de negócio"""
    name: str
    value: float
    category: str
    timestamp: datetime
    trend: str = "stable"  # up, down, stable
    change_percent: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class SystemMetric:
    """Estrutura de métrica do sistema"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    threshold_warning: float = None
    threshold_critical: float = None
    status: str = "normal"  # normal, warning, critical

@dataclass
class Alert:
    """Estrutura de alerta"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = None

class PerformanceCollector:
    """Coletor de métricas de performance"""
    
    def __init__(self):
        # Métricas Prometheus
        self.api_requests = Counter(
            'api_requests_total',
            'Total de requisições da API',
            ['endpoint', 'method', 'status']
        )
        
        self.api_latency = Histogram(
            'api_latency_seconds',
            'Latência das requisições da API',
            ['endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.processing_time = Histogram(
            'processing_time_seconds',
            'Tempo de processamento',
            ['operation'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.active_connections = Gauge(
            'active_connections',
            'Conexões ativas'
        )
        
        self.queue_size = Gauge(
            'queue_size',
            'Tamanho da fila de processamento'
        )
        
        # Histórico de métricas
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        
    def track_request(self, endpoint: str, method: str, status: int, duration: float):
        """Registra requisição da API"""
        self.api_requests.labels(
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
        
        self.api_latency.labels(endpoint=endpoint).observe(duration)
        
        # Adicionar ao histórico
        metric = PerformanceMetric(
            name=f"api_latency_{endpoint}",
            value=duration,
            unit="seconds",
            timestamp=datetime.utcnow(),
            labels={"endpoint": endpoint, "method": method, "status": status}
        )
        self.metrics_history[metric.name].append(metric)
    
    def track_processing(self, operation: str, duration: float):
        """Registra tempo de processamento"""
        self.processing_time.labels(operation=operation).observe(duration)
        
        metric = PerformanceMetric(
            name=f"processing_time_{operation}",
            value=duration,
            unit="seconds",
            timestamp=datetime.utcnow(),
            labels={"operation": operation}
        )
        self.metrics_history[metric.name].append(metric)
    
    def update_connections(self, count: int):
        """Atualiza contador de conexões"""
        self.active_connections.set(count)
        
        metric = PerformanceMetric(
            name="active_connections",
            value=count,
            unit="connections",
            timestamp=datetime.utcnow()
        )
        self.metrics_history[metric.name].append(metric)
    
    def update_queue_size(self, size: int):
        """Atualiza tamanho da fila"""
        self.queue_size.set(size)
        
        metric = PerformanceMetric(
            name="queue_size",
            value=size,
            unit="items",
            timestamp=datetime.utcnow()
        )
        self.metrics_history[metric.name].append(metric)
    
    def get_metrics_history(self, metric_name: str, minutes: int = 60) -> List[PerformanceMetric]:
        """Obtém histórico de métricas"""
        if metric_name not in self.metrics_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            metric for metric in self.metrics_history[metric_name]
            if metric.timestamp >= cutoff_time
        ]

class BusinessMetricsCollector:
    """Coletor de métricas de negócio"""
    
    def __init__(self):
        # Métricas de negócio
        self.keywords_processed = Counter(
            'keywords_processed_total',
            'Total de keywords processadas',
            ['language', 'status']
        )
        
        self.clusters_created = Counter(
            'clusters_created_total',
            'Total de clusters criados',
            ['size', 'score_range']
        )
        
        self.user_actions = Counter(
            'user_actions_total',
            'Total de ações do usuário',
            ['action_type', 'user_type']
        )
        
        self.export_count = Counter(
            'exports_total',
            'Total de exportações',
            ['format', 'status']
        )
        
        # Histórico de métricas de negócio
        self.business_history = defaultdict(lambda: deque(maxlen=1000))
        
    def track_keyword_processing(self, language: str, status: str, count: int = 1):
        """Registra processamento de keywords"""
        self.keywords_processed.labels(
            language=language,
            status=status
        ).inc(count)
        
        metric = BusinessMetric(
            name="keywords_processed",
            value=count,
            category="processing",
            timestamp=datetime.utcnow(),
            metadata={"language": language, "status": status}
        )
        self.business_history[metric.name].append(metric)
    
    def track_cluster_creation(self, size: str, score_range: str):
        """Registra criação de clusters"""
        self.clusters_created.labels(
            size=size,
            score_range=score_range
        ).inc()
        
        metric = BusinessMetric(
            name="clusters_created",
            value=1,
            category="clustering",
            timestamp=datetime.utcnow(),
            metadata={"size": size, "score_range": score_range}
        )
        self.business_history[metric.name].append(metric)
    
    def track_user_action(self, action_type: str, user_type: str):
        """Registra ação do usuário"""
        self.user_actions.labels(
            action_type=action_type,
            user_type=user_type
        ).inc()
        
        metric = BusinessMetric(
            name="user_actions",
            value=1,
            category="engagement",
            timestamp=datetime.utcnow(),
            metadata={"action_type": action_type, "user_type": user_type}
        )
        self.business_history[metric.name].append(metric)
    
    def track_export(self, format_type: str, status: str):
        """Registra exportação"""
        self.export_count.labels(
            format=format_type,
            status=status
        ).inc()
        
        metric = BusinessMetric(
            name="exports",
            value=1,
            category="export",
            timestamp=datetime.utcnow(),
            metadata={"format": format_type, "status": status}
        )
        self.business_history[metric.name].append(metric)
    
    def get_business_metrics(self, minutes: int = 60) -> Dict[str, List[BusinessMetric]]:
        """Obtém métricas de negócio do período"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        result = {}
        
        for metric_name, history in self.business_history.items():
            filtered_metrics = [
                metric for metric in history
                if metric.timestamp >= cutoff_time
            ]
            if filtered_metrics:
                result[metric_name] = filtered_metrics
        
        return result

class SystemMonitor:
    """Monitor do sistema"""
    
    def __init__(self):
        # Métricas do sistema
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'Uso de CPU em percentual'
        )
        
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Uso de memória em bytes'
        )
        
        self.disk_usage = Gauge(
            'disk_usage_percent',
            'Uso de disco em percentual',
            ['mount']
        )
        
        self.network_io = Counter(
            'network_bytes_total',
            'Bytes de rede',
            ['direction']
        )
        
        # Histórico de métricas do sistema
        self.system_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Thresholds
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 80.0,
            'disk_critical': 95.0
        }
    
    def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.set(cpu_percent)
        
        cpu_metric = SystemMetric(
            name="cpu_usage",
            value=cpu_percent,
            unit="percent",
            timestamp=datetime.utcnow(),
            threshold_warning=self.thresholds['cpu_warning'],
            threshold_critical=self.thresholds['cpu_critical'],
            status=self._get_status(cpu_percent, self.thresholds['cpu_warning'], self.thresholds['cpu_critical'])
        )
        self.system_history['cpu_usage'].append(cpu_metric)
        
        # Memória
        memory = psutil.virtual_memory()
        memory_bytes = memory.used
        memory_percent = memory.percent
        self.memory_usage.set(memory_bytes)
        
        memory_metric = SystemMetric(
            name="memory_usage",
            value=memory_percent,
            unit="percent",
            timestamp=datetime.utcnow(),
            threshold_warning=self.thresholds['memory_warning'],
            threshold_critical=self.thresholds['memory_critical'],
            status=self._get_status(memory_percent, self.thresholds['memory_warning'], self.thresholds['memory_critical'])
        )
        self.system_history['memory_usage'].append(memory_metric)
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.disk_usage.labels(mount='/').set(disk_percent)
        
        disk_metric = SystemMetric(
            name="disk_usage",
            value=disk_percent,
            unit="percent",
            timestamp=datetime.utcnow(),
            threshold_warning=self.thresholds['disk_warning'],
            threshold_critical=self.thresholds['disk_critical'],
            status=self._get_status(disk_percent, self.thresholds['disk_warning'], self.thresholds['disk_critical'])
        )
        self.system_history['disk_usage'].append(disk_metric)
        
        # Rede
        network = psutil.net_io_counters()
        self.network_io.labels(direction='bytes_sent').inc(network.bytes_sent)
        self.network_io.labels(direction='bytes_recv').inc(network.bytes_recv)
        
        return {
            'cpu': cpu_metric,
            'memory': memory_metric,
            'disk': disk_metric,
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
        }
    
    def _get_status(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Determina status baseado em thresholds"""
        if value >= critical_threshold:
            return "critical"
        elif value >= warning_threshold:
            return "warning"
        else:
            return "normal"
    
    def get_system_metrics_history(self, minutes: int = 60) -> Dict[str, List[SystemMetric]]:
        """Obtém histórico de métricas do sistema"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        result = {}
        
        for metric_name, history in self.system_history.items():
            filtered_metrics = [
                metric for metric in history
                if metric.timestamp >= cutoff_time
            ]
            if filtered_metrics:
                result[metric_name] = filtered_metrics
        
        return result

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_rules = {
            'cpu_critical': {
                'metric': 'cpu_usage',
                'threshold': 90.0,
                'severity': AlertSeverity.CRITICAL,
                'title': 'CPU Usage Critical',
                'message': 'CPU usage is above critical threshold'
            },
            'memory_critical': {
                'metric': 'memory_usage',
                'threshold': 95.0,
                'severity': AlertSeverity.CRITICAL,
                'title': 'Memory Usage Critical',
                'message': 'Memory usage is above critical threshold'
            },
            'disk_critical': {
                'metric': 'disk_usage',
                'threshold': 95.0,
                'severity': AlertSeverity.CRITICAL,
                'title': 'Disk Usage Critical',
                'message': 'Disk usage is above critical threshold'
            },
            'api_latency_high': {
                'metric': 'api_latency',
                'threshold': 2.0,
                'severity': AlertSeverity.WARNING,
                'title': 'High API Latency',
                'message': 'API latency is above normal threshold'
            }
        }
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Verifica e gera alertas baseado nas métricas"""
        new_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            metric_name = rule['metric']
            threshold = rule['threshold']
            
            if metric_name in metrics:
                current_value = metrics[metric_name]
                
                if current_value >= threshold:
                    # Verificar se já existe alerta ativo
                    alert_id = f"{rule_name}_{metric_name}"
                    
                    if alert_id not in self.alerts:
                        alert = Alert(
                            id=alert_id,
                            title=rule['title'],
                            message=rule['message'],
                            severity=rule['severity'],
                            metric_name=metric_name,
                            current_value=current_value,
                            threshold=threshold,
                            timestamp=datetime.utcnow(),
                            metadata={"rule": rule_name}
                        )
                        
                        self.alerts[alert_id] = alert
                        self.alert_history.append(alert)
                        new_alerts.append(alert)
                        
                        logging.warning(f"Alert triggered: {alert.title} - {current_value} >= {threshold}")
                else:
                    # Resolver alerta se existir
                    alert_id = f"{rule_name}_{metric_name}"
                    if alert_id in self.alerts:
                        self.alerts[alert_id].resolved = True
                        logging.info(f"Alert resolved: {rule['title']}")
        
        return new_alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Reconhece um alerta"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtém alertas ativos"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Obtém histórico de alertas"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]

class RealTimeDashboard:
    """Dashboard de performance em tempo real"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.performance_collector = PerformanceCollector()
        self.business_collector = BusinessMetricsCollector()
        self.system_monitor = SystemMonitor()
        self.alert_manager = AlertManager()
        
        # Configurações
        self.update_interval = self.config.get('update_interval', 5)  # segundos
        self.history_retention = self.config.get('history_retention', 24)  # horas
        
        # Estado do dashboard
        self.is_running = False
        self.update_thread = None
        
        # WebSocket connections (para atualizações em tempo real)
        self.websocket_connections = []
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Inicia o dashboard"""
        if self.is_running:
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        self.logger.info("Dashboard de performance iniciado")
    
    def stop(self):
        """Para o dashboard"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
        
        self.logger.info("Dashboard de performance parado")
    
    def _update_loop(self):
        """Loop principal de atualização"""
        while self.is_running:
            try:
                # Coletar métricas do sistema
                system_metrics = self.system_monitor.collect_system_metrics()
                
                # Verificar alertas
                alerts = self.alert_manager.check_alerts({
                    'cpu_usage': system_metrics['cpu'].value,
                    'memory_usage': system_metrics['memory'].value,
                    'disk_usage': system_metrics['disk'].value
                })
                
                # Notificar clientes WebSocket se houver alertas
                if alerts:
                    self._notify_websocket_clients({
                        'type': 'alerts',
                        'alerts': [asdict(alert) for alert in alerts]
                    })
                
                # Aguardar próximo ciclo
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de atualização: {str(e)}")
                time.sleep(self.update_interval)
    
    def get_dashboard_data(self, include_history: bool = True) -> Dict[str, Any]:
        """Obtém dados completos do dashboard"""
        try:
            # Métricas atuais do sistema
            system_metrics = self.system_monitor.collect_system_metrics()
            
            # Métricas de negócio
            business_metrics = self.business_collector.get_business_metrics(minutes=60)
            
            # Alertas ativos
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Histórico (se solicitado)
            history = {}
            if include_history:
                history = {
                    'system': self.system_monitor.get_system_metrics_history(minutes=60),
                    'business': business_metrics,
                    'alerts': self.alert_manager.get_alert_history(hours=1)
                }
            
            return {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'system': {
                    'cpu': asdict(system_metrics['cpu']),
                    'memory': asdict(system_metrics['memory']),
                    'disk': asdict(system_metrics['disk']),
                    'network': system_metrics['network']
                },
                'business': {
                    name: [asdict(metric) for metric in metrics]
                    for name, metrics in business_metrics.items()
                },
                'alerts': {
                    'active': [asdict(alert) for alert in active_alerts],
                    'count': len(active_alerts)
                },
                'history': history
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do dashboard: {str(e)}")
            return {
                'error': 'Erro ao obter dados do dashboard',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
    
    def get_performance_metrics(self, metric_name: str = None, minutes: int = 60) -> Dict[str, Any]:
        """Obtém métricas de performance"""
        try:
            if metric_name:
                metrics = self.performance_collector.get_metrics_history(metric_name, minutes)
                return {
                    'metric': metric_name,
                    'data': [asdict(metric) for metric in metrics]
                }
            else:
                # Retornar todas as métricas de performance
                all_metrics = {}
                for name in self.performance_collector.metrics_history.keys():
                    metrics = self.performance_collector.get_metrics_history(name, minutes)
                    all_metrics[name] = [asdict(metric) for metric in metrics]
                
                return all_metrics
                
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas de performance: {str(e)}")
            return {'error': 'Erro ao obter métricas de performance'}
    
    def export_report(self, report_type: str = 'performance', format: str = 'json', hours: int = 24) -> Dict[str, Any]:
        """Exporta relatório"""
        try:
            if report_type == 'performance':
                data = self.get_performance_metrics(minutes=hours * 60)
            elif report_type == 'system':
                data = self.system_monitor.get_system_metrics_history(minutes=hours * 60)
            elif report_type == 'business':
                data = self.business_collector.get_business_metrics(minutes=hours * 60)
            elif report_type == 'alerts':
                data = self.alert_manager.get_alert_history(hours=hours)
            else:
                return {'error': 'Tipo de relatório inválido'}
            
            report = {
                'type': report_type,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'period_hours': hours,
                'data': data
            }
            
            if format == 'json':
                return report
            elif format == 'csv':
                # Implementar conversão para CSV
                return {'error': 'Formato CSV não implementado ainda'}
            else:
                return {'error': 'Formato não suportado'}
                
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório: {str(e)}")
            return {'error': 'Erro ao exportar relatório'}
    
    def add_websocket_connection(self, websocket):
        """Adiciona conexão WebSocket"""
        self.websocket_connections.append(websocket)
    
    def remove_websocket_connection(self, websocket):
        """Remove conexão WebSocket"""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
    
    def _notify_websocket_clients(self, data: Dict[str, Any]):
        """Notifica clientes WebSocket"""
        message = json.dumps(data)
        for websocket in self.websocket_connections[:]:  # Copiar lista para evitar modificação durante iteração
            try:
                # Implementar envio via WebSocket
                pass
            except Exception as e:
                self.logger.error(f"Erro ao enviar para WebSocket: {str(e)}")
                self.remove_websocket_connection(websocket)
    
    def get_prometheus_metrics(self) -> str:
        """Retorna métricas no formato Prometheus"""
        try:
            return generate_latest().decode('utf-8')
        except Exception as e:
            self.logger.error(f"Erro ao gerar métricas Prometheus: {str(e)}")
            return ""

# Factory function
def create_real_time_dashboard(config: Optional[Dict[str, Any]] = None) -> RealTimeDashboard:
    """Factory para criar dashboard de performance em tempo real"""
    return RealTimeDashboard(config) 