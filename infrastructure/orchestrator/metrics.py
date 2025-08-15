"""
Metrics Module - Omni Keywords Finder

Sistema de métricas e monitoramento para o orquestrador:
- Performance por etapa
- Taxa de sucesso
- Tempo de processamento
- Métricas de negócio

Tracing ID: METRICS_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MetricCategory(Enum):
    """Categorias de métricas."""
    PERFORMANCE = "performance"
    SUCCESS_RATE = "success_rate"
    BUSINESS = "business"
    SYSTEM = "system"


@dataclass
class MetricConfig:
    """Configuração do sistema de métricas."""
    enabled: bool = True
    storage_path: str = "logs/metrics"
    retention_days: int = 30
    flush_interval: float = 10.0  # segundos
    max_histogram_buckets: int = 50
    enable_real_time: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["json", "prometheus"])


@dataclass
class MetricValue:
    """Valor de uma métrica."""
    name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricDefinition:
    """Definição de uma métrica."""
    name: str
    type: MetricType
    category: MetricCategory
    description: str
    unit: Optional[str] = None
    labels: List[str] = field(default_factory=list)


class MetricsCollector:
    """Coletor de métricas."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        """
        Inicializa o coletor de métricas.
        
        Args:
            config: Configuração das métricas
        """
        self.config = config or MetricConfig()
        self.metrics: Dict[str, Any] = defaultdict(dict)
        self.definitions: Dict[str, MetricDefinition] = {}
        self.lock = threading.Lock()
        
        self._setup_storage()
        self._register_default_metrics()
        
        if self.config.enable_real_time:
            self._start_flush_thread()
        
        logger.info("MetricsCollector inicializado")
    
    def _setup_storage(self):
        """Configura armazenamento de métricas."""
        if self.config.enabled:
            self.storage_path = Path(self.config.storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _register_default_metrics(self):
        """Registra métricas padrão do sistema."""
        default_metrics = [
            # Performance
            MetricDefinition(
                name="etapa_duration",
                type=MetricType.HISTOGRAM,
                category=MetricCategory.PERFORMANCE,
                description="Duração de cada etapa",
                unit="seconds",
                labels=["etapa", "nicho"]
            ),
            MetricDefinition(
                name="fluxo_duration",
                type=MetricType.HISTOGRAM,
                category=MetricCategory.PERFORMANCE,
                description="Duração total do fluxo",
                unit="seconds",
                labels=["nicho"]
            ),
            
            # Success Rate
            MetricDefinition(
                name="etapa_success_rate",
                type=MetricType.GAUGE,
                category=MetricCategory.SUCCESS_RATE,
                description="Taxa de sucesso por etapa",
                unit="percentage",
                labels=["etapa", "nicho"]
            ),
            MetricDefinition(
                name="fluxo_success_rate",
                type=MetricType.GAUGE,
                category=MetricCategory.SUCCESS_RATE,
                description="Taxa de sucesso do fluxo completo",
                unit="percentage",
                labels=["nicho"]
            ),
            
            # Business
            MetricDefinition(
                name="keywords_processed",
                type=MetricType.COUNTER,
                category=MetricCategory.BUSINESS,
                description="Número de keywords processadas",
                unit="count",
                labels=["nicho", "etapa"]
            ),
            MetricDefinition(
                name="keywords_validated",
                type=MetricType.COUNTER,
                category=MetricCategory.BUSINESS,
                description="Número de keywords validadas",
                unit="count",
                labels=["nicho"]
            ),
            MetricDefinition(
                name="prompts_generated",
                type=MetricType.COUNTER,
                category=MetricCategory.BUSINESS,
                description="Número de prompts gerados",
                unit="count",
                labels=["nicho"]
            ),
            
            # System
            MetricDefinition(
                name="memory_usage",
                type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Uso de memória",
                unit="bytes",
                labels=["component"]
            ),
            MetricDefinition(
                name="cpu_usage",
                type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Uso de CPU",
                unit="percentage",
                labels=["component"]
            ),
            MetricDefinition(
                name="disk_usage",
                type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="Uso de disco",
                unit="bytes",
                labels=["path"]
            )
        ]
        
        for metric in default_metrics:
            self.register_metric(metric)
    
    def register_metric(self, definition: MetricDefinition):
        """
        Registra uma nova métrica.
        
        Args:
            definition: Definição da métrica
        """
        with self.lock:
            self.definitions[definition.name] = definition
            
            # Inicializar estrutura baseada no tipo
            if definition.type == MetricType.COUNTER:
                self.metrics[definition.name] = defaultdict(int)
            elif definition.type == MetricType.GAUGE:
                self.metrics[definition.name] = defaultdict(float)
            elif definition.type == MetricType.HISTOGRAM:
                self.metrics[definition.name] = defaultdict(lambda: deque(maxlen=self.config.max_histogram_buckets))
            elif definition.type == MetricType.TIMER:
                self.metrics[definition.name] = defaultdict(lambda: deque(maxlen=self.config.max_histogram_buckets))
        
        logger.info(f"Métrica registrada: {definition.name}")
    
    def record_counter(
        self,
        name: str,
        value: int = 1,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Registra um contador.
        
        Args:
            name: Nome da métrica
            value: Valor a incrementar
            labels: Labels da métrica
        """
        if not self.config.enabled:
            return
        
        labels = labels or {}
        label_key = self._make_label_key(labels)
        
        with self.lock:
            if name in self.metrics:
                self.metrics[name][label_key] += value
            else:
                logger.warning(f"Métrica não registrada: {name}")
    
    def record_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Registra um gauge.
        
        Args:
            name: Nome da métrica
            value: Valor atual
            labels: Labels da métrica
        """
        if not self.config.enabled:
            return
        
        labels = labels or {}
        label_key = self._make_label_key(labels)
        
        with self.lock:
            if name in self.metrics:
                self.metrics[name][label_key] = value
            else:
                logger.warning(f"Métrica não registrada: {name}")
    
    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Registra um histograma.
        
        Args:
            name: Nome da métrica
            value: Valor a registrar
            labels: Labels da métrica
        """
        if not self.config.enabled:
            return
        
        labels = labels or {}
        label_key = self._make_label_key(labels)
        
        with self.lock:
            if name in self.metrics:
                self.metrics[name][label_key].append(value)
            else:
                logger.warning(f"Métrica não registrada: {name}")
    
    def start_timer(self, name: str, labels: Optional[Dict[str, str]] = None) -> 'Timer':
        """
        Inicia um timer.
        
        Args:
            name: Nome da métrica
            labels: Labels da métrica
            
        Returns:
            Timer object
        """
        return Timer(self, name, labels)
    
    def _make_label_key(self, labels: Dict[str, str]) -> str:
        """Cria chave única para labels."""
        if not labels:
            return "default"
        
        sorted_items = sorted(labels.items())
        return "|".join(f"{key}={value}" for key, value in sorted_items)
    
    def _start_flush_thread(self):
        """Inicia thread para flush periódico."""
        self.flush_thread = threading.Thread(
            target=self._flush_worker,
            daemon=True
        )
        self.flush_thread.start()
    
    def _flush_worker(self):
        """Worker que faz flush das métricas."""
        while True:
            try:
                time.sleep(self.config.flush_interval)
                self.flush_metrics()
            except Exception as e:
                logger.error(f"Erro no flush worker: {e}")
    
    def flush_metrics(self):
        """Faz flush das métricas para armazenamento."""
        if not self.config.enabled:
            return
        
        try:
            with self.lock:
                metrics_data = self._prepare_metrics_data()
            
            # Salvar em arquivo
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            metrics_file = self.storage_path / f"metrics_{timestamp}.json"
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Métricas salvas em: {metrics_file}")
            
        except Exception as e:
            logger.error(f"Erro ao fazer flush das métricas: {e}")
    
    def _prepare_metrics_data(self) -> Dict[str, Any]:
        """Prepara dados das métricas para exportação."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for name, metric_data in self.metrics.items():
            definition = self.definitions.get(name)
            if not definition:
                continue
            
            metric_info = {
                "type": definition.type.value,
                "category": definition.category.value,
                "description": definition.description,
                "unit": definition.unit,
                "values": {}
            }
            
            for label_key, value in metric_data.items():
                if definition.type in [MetricType.HISTOGRAM, MetricType.TIMER]:
                    # Calcular estatísticas para histogramas
                    if value:
                        metric_info["values"][label_key] = {
                            "count": len(value),
                            "min": min(value),
                            "max": max(value),
                            "mean": statistics.mean(value),
                            "median": statistics.median(value),
                            "values": list(value)
                        }
                    else:
                        metric_info["values"][label_key] = {
                            "count": 0,
                            "min": 0,
                            "max": 0,
                            "mean": 0,
                            "median": 0,
                            "values": []
                        }
                else:
                    metric_info["values"][label_key] = value
            
            data["metrics"][name] = metric_info
        
        return data
    
    def get_metric_summary(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém resumo de uma métrica.
        
        Args:
            name: Nome da métrica
            
        Returns:
            Resumo da métrica ou None
        """
        with self.lock:
            if name not in self.metrics:
                return None
            
            definition = self.definitions.get(name)
            if not definition:
                return None
            
            metric_data = self.metrics[name]
            summary = {
                "name": name,
                "type": definition.type.value,
                "category": definition.category.value,
                "description": definition.description,
                "unit": definition.unit,
                "total_labels": len(metric_data),
                "values": {}
            }
            
            for label_key, value in metric_data.items():
                if definition.type in [MetricType.HISTOGRAM, MetricType.TIMER]:
                    if value:
                        summary["values"][label_key] = {
                            "count": len(value),
                            "min": min(value),
                            "max": max(value),
                            "mean": statistics.mean(value),
                            "median": statistics.median(value)
                        }
                    else:
                        summary["values"][label_key] = {
                            "count": 0,
                            "min": 0,
                            "max": 0,
                            "mean": 0,
                            "median": 0
                        }
                else:
                    summary["values"][label_key] = value
            
            return summary
    
    def get_all_summaries(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém resumo de todas as métricas.
        
        Returns:
            Dicionário com resumos de todas as métricas
        """
        summaries = {}
        
        with self.lock:
            for name in self.metrics.keys():
                summary = self.get_metric_summary(name)
                if summary:
                    summaries[name] = summary
        
        return summaries
    
    def export_prometheus(self) -> str:
        """
        Exporta métricas no formato Prometheus.
        
        Returns:
            String no formato Prometheus
        """
        lines = []
        
        with self.lock:
            for name, metric_data in self.metrics.items():
                definition = self.definitions.get(name)
                if not definition:
                    continue
                
                for label_key, value in metric_data.items():
                    if definition.type in [MetricType.HISTOGRAM, MetricType.TIMER]:
                        if value:
                            # Exportar estatísticas do histograma
                            lines.append(f'# HELP {name} {definition.description}')
                            lines.append(f'# TYPE {name} histogram')
                            
                            labels_str = self._format_prometheus_labels(label_key)
                            lines.append(f'{name}_count{labels_str} {len(value)}')
                            lines.append(f'{name}_sum{labels_str} {sum(value)}')
                            lines.append(f'{name}_min{labels_str} {min(value)}')
                            lines.append(f'{name}_max{labels_str} {max(value)}')
                            lines.append(f'{name}_mean{labels_str} {statistics.mean(value)}')
                    else:
                        # Exportar valor simples
                        lines.append(f'# HELP {name} {definition.description}')
                        lines.append(f'# TYPE {name} {definition.type.value}')
                        
                        labels_str = self._format_prometheus_labels(label_key)
                        lines.append(f'{name}{labels_str} {value}')
        
        return '\n'.join(lines)
    
    def _format_prometheus_labels(self, label_key: str) -> str:
        """Formata labels para formato Prometheus."""
        if label_key == "default":
            return ""
        
        labels = {}
        for item in label_key.split("|"):
            if "=" in item:
                key, value = item.split("=", 1)
                labels[key] = value
        
        if not labels:
            return ""
        
        labels_str = ",".join(f'{key}="{value}"' for key, value in labels.items())
        return f"{{{labels_str}}}"


class Timer:
    """Context manager para timers."""
    
    def __init__(self, collector: MetricsCollector, name: str, labels: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.labels = labels or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.record_histogram(self.name, duration, self.labels)


# Instância global
_metrics_collector: Optional[MetricsCollector] = None


def obter_metrics_collector(config: Optional[MetricConfig] = None) -> MetricsCollector:
    """
    Obtém instância global do coletor de métricas.
    
    Args:
        config: Configuração opcional
        
    Returns:
        Instância do coletor
    """
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(config)
    
    return _metrics_collector


def record_counter(name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
    """Função helper para registrar contador."""
    collector = obter_metrics_collector()
    collector.record_counter(name, value, labels)


def record_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Função helper para registrar gauge."""
    collector = obter_metrics_collector()
    collector.record_gauge(name, value, labels)


def record_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Função helper para registrar histograma."""
    collector = obter_metrics_collector()
    collector.record_histogram(name, value, labels)


def start_timer(name: str, labels: Optional[Dict[str, str]] = None) -> Timer:
    """Função helper para iniciar timer."""
    collector = obter_metrics_collector()
    return collector.start_timer(name, labels)


def get_metric_summary(name: str) -> Optional[Dict[str, Any]]:
    """Função helper para obter resumo de métrica."""
    collector = obter_metrics_collector()
    return collector.get_metric_summary(name)


def get_all_summaries() -> Dict[str, Dict[str, Any]]:
    """Função helper para obter todos os resumos."""
    collector = obter_metrics_collector()
    return collector.get_all_summaries()


def export_prometheus() -> str:
    """Função helper para exportar no formato Prometheus."""
    collector = obter_metrics_collector()
    return collector.export_prometheus() 