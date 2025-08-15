"""
Módulo de Monitoramento de Performance para Sistemas Enterprise
Sistema de métricas, alertas e dashboards - Omni Keywords Finder

Prompt: Implementação de sistema de monitoramento de performance enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import time
import threading
import logging
import json
import psutil
import statistics
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, deque
import weakref

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Severidades de alerta."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Status de alertas."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class MetricConfig:
    """Configuração de métrica."""
    name: str
    type: MetricType
    description: str
    unit: str = ""
    labels: List[str] = field(default_factory=list)
    interval: int = 60  # segundos
    retention_days: int = 30
    aggregation_window: int = 300  # segundos
    enable_alerting: bool = True
    thresholds: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Nome da métrica não pode ser vazio")
        if self.interval <= 0:
            raise ValueError("Interval deve ser positivo")
        if self.retention_days <= 0:
            raise ValueError("Retention days deve ser positivo")
        if self.aggregation_window <= 0:
            raise ValueError("Aggregation window deve ser positivo")


@dataclass
class MetricValue:
    """Valor de uma métrica."""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.metric_name or len(self.metric_name.strip()) == 0:
            raise ValueError("Nome da métrica não pode ser vazio")
        if not isinstance(self.value, (int, float)):
            raise ValueError("Valor deve ser numérico")


@dataclass
class MetricAggregation:
    """Agregação de métricas."""
    metric_name: str
    aggregation_type: str  # min, max, avg, sum, count
    value: float
    timestamp: datetime
    window_start: datetime
    window_end: datetime
    sample_count: int
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Regra de alerta."""
    name: str
    metric_name: str
    condition: str  # >, <, >=, <=, ==, !=
    threshold: float
    severity: AlertSeverity
    description: str
    enabled: bool = True
    cooldown_period: int = 300  # segundos
    last_triggered: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Nome da regra não pode ser vazio")
        if not self.metric_name or len(self.metric_name.strip()) == 0:
            raise ValueError("Nome da métrica não pode ser vazio")
        if self.condition not in [">", "<", ">=", "<=", "==", "!="]:
            raise ValueError("Condição inválida")
        if self.cooldown_period < 0:
            raise ValueError("Cooldown period não pode ser negativo")


@dataclass
class Alert:
    """Alerta."""
    id: str
    rule_name: str
    metric_name: str
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceConfig:
    """Configuração de monitoramento de performance."""
    enable_system_metrics: bool = True
    enable_application_metrics: bool = True
    enable_custom_metrics: bool = True
    collection_interval: int = 60  # segundos
    retention_days: int = 30
    aggregation_interval: int = 300  # segundos
    enable_alerting: bool = True
    enable_dashboard: bool = True
    enable_export: bool = True
    export_format: str = "json"  # json, csv, prometheus
    enable_webhook: bool = False
    webhook_url: Optional[str] = None
    enable_email_alerts: bool = False
    email_recipients: List[str] = field(default_factory=list)
    enable_slack_alerts: bool = False
    slack_webhook_url: Optional[str] = None
    enable_metrics_api: bool = True
    api_port: int = 8080
    enable_health_checks: bool = True
    health_check_interval: int = 30  # segundos

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.collection_interval <= 0:
            raise ValueError("Collection interval deve ser positivo")
        if self.retention_days <= 0:
            raise ValueError("Retention days deve ser positivo")
        if self.aggregation_interval <= 0:
            raise ValueError("Aggregation interval deve ser positivo")
        if self.health_check_interval <= 0:
            raise ValueError("Health check interval deve ser positivo")
        if self.api_port <= 0 or self.api_port > 65535:
            raise ValueError("API port deve estar entre 1 e 65535")


class PerformanceMonitor:
    """Monitor de performance enterprise."""
    
    def __init__(self, config: PerformanceConfig = None):
        """
        Inicializa o monitor de performance.
        
        Args:
            config: Configuração do monitor
        """
        self.config = config or PerformanceConfig()
        
        # Métricas
        self.metrics: Dict[str, MetricConfig] = {}
        self.metric_values: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregations: Dict[str, List[MetricAggregation]] = defaultdict(list)
        
        # Alertas
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Controles
        self.running = False
        self.collection_thread = None
        self.aggregation_thread = None
        self.health_check_thread = None
        self.lock = threading.RLock()
        
        # Callbacks
        self.on_metric_collected: Optional[Callable[[MetricValue], None]] = None
        self.on_alert_triggered: Optional[Callable[[Alert], None]] = None
        self.on_alert_resolved: Optional[Callable[[Alert], None]] = None
        self.on_threshold_exceeded: Optional[Callable[[str, float, float], None]] = None
        
        # Contadores
        self.alert_counter = 0
        
        logger.info("PerformanceMonitor inicializado")
    
    def register_metric(self, config: MetricConfig) -> bool:
        """
        Registra uma nova métrica.
        
        Args:
            config: Configuração da métrica
            
        Returns:
            True se registrada com sucesso, False caso contrário
        """
        with self.lock:
            if config.name in self.metrics:
                logger.warning(f"Métrica já registrada: {config.name}")
                return False
            
            self.metrics[config.name] = config
            logger.info(f"Métrica registrada: {config.name} ({config.type.value})")
            return True
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None,
                     metadata: Dict[str, Any] = None) -> bool:
        """
        Registra um valor de métrica.
        
        Args:
            name: Nome da métrica
            value: Valor da métrica
            labels: Labels da métrica
            metadata: Metadados adicionais
            
        Returns:
            True se registrado com sucesso, False caso contrário
        """
        with self.lock:
            if name not in self.metrics:
                logger.warning(f"Métrica não registrada: {name}")
                return False
            
            metric_value = MetricValue(
                metric_name=name,
                value=value,
                timestamp=datetime.utcnow(),
                labels=labels or {},
                metadata=metadata or {}
            )
            
            self.metric_values[name].append(metric_value)
            
            # Verificar regras de alerta
            if self.config.enable_alerting:
                self._check_alert_rules(metric_value)
            
            if self.on_metric_collected:
                self.on_metric_collected(metric_value)
            
            logger.debug(f"Métrica registrada: {name} = {value}")
            return True
    
    def get_metric_values(self, name: str, limit: int = 100) -> List[MetricValue]:
        """
        Obtém valores de uma métrica.
        
        Args:
            name: Nome da métrica
            limit: Limite de valores
            
        Returns:
            Lista de valores da métrica
        """
        with self.lock:
            if name not in self.metric_values:
                return []
            
            values = list(self.metric_values[name])
            return values[-limit:] if limit > 0 else values
    
    def get_metric_aggregation(self, name: str, aggregation_type: str,
                              window_minutes: int = 5) -> Optional[MetricAggregation]:
        """
        Obtém agregação de uma métrica.
        
        Args:
            name: Nome da métrica
            aggregation_type: Tipo de agregação
            window_minutes: Janela em minutos
            
        Returns:
            Agregação da métrica ou None se não encontrada
        """
        with self.lock:
            if name not in self.aggregations:
                return None
            
            # Calcular janela de tempo
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=window_minutes)
            
            # Filtrar agregações na janela
            window_aggregations = [
                agg for agg in self.aggregations[name]
                if start_time <= agg.timestamp <= end_time and
                agg.aggregation_type == aggregation_type
            ]
            
            if not window_aggregations:
                return None
            
            # Retornar a mais recente
            return max(window_aggregations, key=lambda x: x.timestamp)
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """
        Adiciona uma regra de alerta.
        
        Args:
            rule: Regra de alerta
            
        Returns:
            True se adicionada com sucesso, False caso contrário
        """
        with self.lock:
            if rule.name in self.alert_rules:
                logger.warning(f"Regra de alerta já existe: {rule.name}")
                return False
            
            self.alert_rules[rule.name] = rule
            logger.info(f"Regra de alerta adicionada: {rule.name}")
            return True
    
    def remove_alert_rule(self, name: str) -> bool:
        """
        Remove uma regra de alerta.
        
        Args:
            name: Nome da regra
            
        Returns:
            True se removida com sucesso, False caso contrário
        """
        with self.lock:
            if name not in self.alert_rules:
                return False
            
            del self.alert_rules[name]
            logger.info(f"Regra de alerta removida: {name}")
            return True
    
    def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """
        Obtém alertas ativos.
        
        Args:
            severity: Filtrar por severidade
            
        Returns:
            Lista de alertas ativos
        """
        with self.lock:
            alerts = list(self.active_alerts.values())
            
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            
            return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """
        Reconhece um alerta.
        
        Args:
            alert_id: ID do alerta
            user: Usuário que reconheceu
            
        Returns:
            True se reconhecido com sucesso, False caso contrário
        """
        with self.lock:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user
            alert.acknowledged_at = datetime.utcnow()
            
            logger.info(f"Alerta reconhecido: {alert_id} por {user}")
            return True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve um alerta.
        
        Args:
            alert_id: ID do alerta
            
        Returns:
            True se resolvido com sucesso, False caso contrário
        """
        with self.lock:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            
            # Mover para histórico
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            if self.on_alert_resolved:
                self.on_alert_resolved(alert)
            
            logger.info(f"Alerta resolvido: {alert_id}")
            return True
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de performance.
        
        Returns:
            Dicionário com estatísticas
        """
        with self.lock:
            # Estatísticas do sistema
            system_stats = {}
            if self.config.enable_system_metrics:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    system_stats = {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_mb": memory.used / (1024 * 1024),
                        "memory_total_mb": memory.total / (1024 * 1024),
                        "disk_percent": disk.percent,
                        "disk_used_gb": disk.used / (1024 * 1024 * 1024),
                        "disk_total_gb": disk.total / (1024 * 1024 * 1024)
                    }
                except Exception as e:
                    logger.error(f"Erro ao obter estatísticas do sistema: {e}")
            
            # Estatísticas das métricas
            metrics_stats = {
                "total_metrics": len(self.metrics),
                "total_values": sum(len(values) for values in self.metric_values.values()),
                "total_aggregations": sum(len(aggs) for aggs in self.aggregations.values())
            }
            
            # Estatísticas dos alertas
            alerts_stats = {
                "total_rules": len(self.alert_rules),
                "active_alerts": len(self.active_alerts),
                "alert_history": len(self.alert_history)
            }
            
            return {
                "system": system_stats,
                "metrics": metrics_stats,
                "alerts": alerts_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def export_metrics(self, format: str = None, start_time: datetime = None,
                      end_time: datetime = None) -> str:
        """
        Exporta métricas.
        
        Args:
            format: Formato de exportação
            start_time: Tempo de início
            end_time: Tempo de fim
            
        Returns:
            Dados exportados
        """
        format = format or self.config.export_format
        start_time = start_time or (datetime.utcnow() - timedelta(hours=1))
        end_time = end_time or datetime.utcnow()
        
        with self.lock:
            if format == "json":
                return self._export_json(start_time, end_time)
            elif format == "csv":
                return self._export_csv(start_time, end_time)
            elif format == "prometheus":
                return self._export_prometheus(start_time, end_time)
            else:
                raise ValueError(f"Formato não suportado: {format}")
    
    def start(self) -> None:
        """Inicia o monitor de performance."""
        if self.running:
            return
        
        self.running = True
        
        # Registrar métricas do sistema
        if self.config.enable_system_metrics:
            self._register_system_metrics()
        
        # Iniciar threads
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        self.aggregation_thread = threading.Thread(target=self._aggregation_loop, daemon=True)
        self.aggregation_thread.start()
        
        if self.config.enable_health_checks:
            self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
            self.health_check_thread.start()
        
        logger.info("PerformanceMonitor iniciado")
    
    def stop(self) -> None:
        """Para o monitor de performance."""
        if not self.running:
            return
        
        self.running = False
        
        # Aguardar threads terminarem
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        
        if self.aggregation_thread:
            self.aggregation_thread.join(timeout=5)
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        
        logger.info("PerformanceMonitor parado")
    
    def _register_system_metrics(self) -> None:
        """Registra métricas do sistema."""
        system_metrics = [
            MetricConfig("cpu_usage", MetricType.GAUGE, "CPU usage percentage", "%"),
            MetricConfig("memory_usage", MetricType.GAUGE, "Memory usage percentage", "%"),
            MetricConfig("memory_used", MetricType.GAUGE, "Memory used in MB", "MB"),
            MetricConfig("disk_usage", MetricType.GAUGE, "Disk usage percentage", "%"),
            MetricConfig("disk_used", MetricType.GAUGE, "Disk used in GB", "GB"),
            MetricConfig("network_sent", MetricType.COUNTER, "Network bytes sent", "bytes"),
            MetricConfig("network_recv", MetricType.COUNTER, "Network bytes received", "bytes")
        ]
        
        for metric in system_metrics:
            self.register_metric(metric)
    
    def _check_alert_rules(self, metric_value: MetricValue) -> None:
        """Verifica regras de alerta para uma métrica."""
        for rule in self.alert_rules.values():
            if rule.metric_name != metric_value.metric_name:
                continue
            
            if not rule.enabled:
                continue
            
            # Verificar cooldown
            if (rule.last_triggered and 
                (datetime.utcnow() - rule.last_triggered).total_seconds() < rule.cooldown_period):
                continue
            
            # Verificar condição
            triggered = False
            if rule.condition == ">":
                triggered = metric_value.value > rule.threshold
            elif rule.condition == "<":
                triggered = metric_value.value < rule.threshold
            elif rule.condition == ">=":
                triggered = metric_value.value >= rule.threshold
            elif rule.condition == "<=":
                triggered = metric_value.value <= rule.threshold
            elif rule.condition == "==":
                triggered = metric_value.value == rule.threshold
            elif rule.condition == "!=":
                triggered = metric_value.value != rule.threshold
            
            if triggered:
                self._trigger_alert(rule, metric_value)
    
    def _trigger_alert(self, rule: AlertRule, metric_value: MetricValue) -> None:
        """Dispara um alerta."""
        alert_id = f"alert_{self.alert_counter}"
        self.alert_counter += 1
        
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            metric_name=rule.metric_name,
            severity=rule.severity,
            message=f"{rule.description}: {metric_value.value} {rule.condition} {rule.threshold}",
            value=metric_value.value,
            threshold=rule.threshold,
            timestamp=datetime.utcnow(),
            labels=rule.labels
        )
        
        self.active_alerts[alert_id] = alert
        rule.last_triggered = datetime.utcnow()
        
        if self.on_alert_triggered:
            self.on_alert_triggered(alert)
        
        if self.on_threshold_exceeded:
            self.on_threshold_exceeded(rule.metric_name, metric_value.value, rule.threshold)
        
        logger.warning(f"Alerta disparado: {alert.message}")
    
    def _collection_loop(self) -> None:
        """Loop de coleta de métricas."""
        while self.running:
            try:
                time.sleep(self.config.collection_interval)
                
                if self.config.enable_system_metrics:
                    self._collect_system_metrics()
                
            except Exception as e:
                logger.error(f"Erro no loop de coleta: {e}")
    
    def _collect_system_metrics(self) -> None:
        """Coleta métricas do sistema."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("cpu_usage", cpu_percent)
            
            # Memória
            memory = psutil.virtual_memory()
            self.record_metric("memory_usage", memory.percent)
            self.record_metric("memory_used", memory.used / (1024 * 1024))
            
            # Disco
            disk = psutil.disk_usage('/')
            self.record_metric("disk_usage", disk.percent)
            self.record_metric("disk_used", disk.used / (1024 * 1024 * 1024))
            
            # Rede
            network = psutil.net_io_counters()
            self.record_metric("network_sent", network.bytes_sent)
            self.record_metric("network_recv", network.bytes_recv)
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    def _aggregation_loop(self) -> None:
        """Loop de agregação de métricas."""
        while self.running:
            try:
                time.sleep(self.config.aggregation_interval)
                
                with self.lock:
                    for metric_name, values in self.metric_values.items():
                        if not values:
                            continue
                        
                        # Filtrar valores na janela de agregação
                        window_start = datetime.utcnow() - timedelta(seconds=self.config.aggregation_interval)
                        window_values = [
                            v for v in values
                            if v.timestamp >= window_start
                        ]
                        
                        if not window_values:
                            continue
                        
                        # Calcular agregações
                        values_list = [v.value for v in window_values]
                        
                        aggregations = [
                            MetricAggregation(
                                metric_name=metric_name,
                                aggregation_type="min",
                                value=min(values_list),
                                timestamp=datetime.utcnow(),
                                window_start=window_start,
                                window_end=datetime.utcnow(),
                                sample_count=len(values_list)
                            ),
                            MetricAggregation(
                                metric_name=metric_name,
                                aggregation_type="max",
                                value=max(values_list),
                                timestamp=datetime.utcnow(),
                                window_start=window_start,
                                window_end=datetime.utcnow(),
                                sample_count=len(values_list)
                            ),
                            MetricAggregation(
                                metric_name=metric_name,
                                aggregation_type="avg",
                                value=statistics.mean(values_list),
                                timestamp=datetime.utcnow(),
                                window_start=window_start,
                                window_end=datetime.utcnow(),
                                sample_count=len(values_list)
                            )
                        ]
                        
                        self.aggregations[metric_name].extend(aggregations)
                        
                        # Manter apenas as agregações mais recentes
                        max_aggregations = 1000
                        if len(self.aggregations[metric_name]) > max_aggregations:
                            self.aggregations[metric_name] = self.aggregations[metric_name][-max_aggregations:]
                
            except Exception as e:
                logger.error(f"Erro no loop de agregação: {e}")
    
    def _health_check_loop(self) -> None:
        """Loop de health check."""
        while self.running:
            try:
                time.sleep(self.config.health_check_interval)
                
                # Verificar se o monitor está funcionando
                stats = self.get_performance_stats()
                if not stats:
                    logger.warning("Health check falhou: não foi possível obter estatísticas")
                
            except Exception as e:
                logger.error(f"Erro no health check: {e}")
    
    def _export_json(self, start_time: datetime, end_time: datetime) -> str:
        """Exporta métricas em formato JSON."""
        export_data = {
            "export_time": datetime.utcnow().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "metrics": {}
        }
        
        for metric_name, values in self.metric_values.items():
            filtered_values = [
                {
                    "value": v.value,
                    "timestamp": v.timestamp.isoformat(),
                    "labels": v.labels,
                    "metadata": v.metadata
                }
                for v in values
                if start_time <= v.timestamp <= end_time
            ]
            
            if filtered_values:
                export_data["metrics"][metric_name] = filtered_values
        
        return json.dumps(export_data, indent=2)
    
    def _export_csv(self, start_time: datetime, end_time: datetime) -> str:
        """Exporta métricas em formato CSV."""
        csv_lines = ["metric_name,timestamp,value,labels"]
        
        for metric_name, values in self.metric_values.items():
            for value in values:
                if start_time <= value.timestamp <= end_time:
                    labels_str = json.dumps(value.labels) if value.labels else ""
                    csv_lines.append(f"{metric_name},{value.timestamp.isoformat()},{value.value},{labels_str}")
        
        return "\n".join(csv_lines)
    
    def _export_prometheus(self, start_time: datetime, end_time: datetime) -> str:
        """Exporta métricas em formato Prometheus."""
        prometheus_lines = []
        
        for metric_name, values in self.metric_values.items():
            for value in values:
                if start_time <= value.timestamp <= end_time:
                    # Formato: metric_name{label="value"} value timestamp
                    labels_str = ""
                    if value.labels:
                        labels_parts = [f'{k}="{v}"' for k, v in value.labels.items()]
                        labels_str = "{" + ",".join(labels_parts) + "}"
                    
                    prometheus_lines.append(f"{metric_name}{labels_str} {value.value} {int(value.timestamp.timestamp() * 1000)}")
        
        return "\n".join(prometheus_lines)


# Função de conveniência para criar performance monitor
def create_performance_monitor(config: PerformanceConfig = None) -> PerformanceMonitor:
    """
    Cria um monitor de performance com configurações padrão.
    
    Args:
        config: Configuração customizada
        
    Returns:
        Instância configurada do PerformanceMonitor
    """
    return PerformanceMonitor(config) 