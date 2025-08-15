"""
Sistema de Métricas e Monitoramento
Responsável por métricas customizadas, health checks e dashboards Grafana.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 3.2
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

class MetricType(Enum):
    """Tipos de métricas."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class HealthStatus(Enum):
    """Status de health check."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class Metric:
    """Métrica customizada."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = None
    description: str = ""
    unit: str = ""
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['metric_type'] = self.metric_type.value
        return data

@dataclass
class HealthCheck:
    """Health check."""
    name: str
    status: HealthStatus
    timestamp: datetime
    response_time: Optional[float] = None
    details: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class MetricsCollector:
    """
    Coletor de métricas customizadas.
    
    Funcionalidades:
    - Coleta de métricas de negócio
    - Métricas de sistema
    - Agregação de dados
    - Armazenamento persistente
    """
    
    def __init__(self, db_path: str = "logs/metrics.db"):
        """
        Inicializar coletor de métricas.
        
        Args:
            db_path: Caminho do banco de dados
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
        
        # Métricas em memória
        self.metrics_buffer = deque(maxlen=10000)
        self.metrics_by_name = defaultdict(list)
        
        # Thread para persistência
        self.running = True
        self.persist_thread = threading.Thread(target=self._persist_loop, daemon=True)
        self.persist_thread.start()
        
        # Estatísticas
        self.stats = {
            'total_metrics': 0,
            'metrics_by_type': defaultdict(int),
            'last_persist': None
        }
    
    def _init_database(self):
        """Inicializar banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    labels TEXT,
                    description TEXT,
                    unit TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Índices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metric_name ON metrics(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metric_timestamp ON metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metric_type ON metrics(metric_type)")
            
            conn.commit()
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
        description: str = "",
        unit: str = ""
    ):
        """
        Registrar métrica.
        
        Args:
            name: Nome da métrica
            value: Valor da métrica
            metric_type: Tipo da métrica
            labels: Labels da métrica
            description: Descrição da métrica
            unit: Unidade da métrica
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            description=description,
            unit=unit
        )
        
        # Adicionar ao buffer
        self.metrics_buffer.append(metric)
        self.metrics_by_name[name].append(metric)
        
        # Manter apenas as últimas 1000 métricas por nome
        if len(self.metrics_by_name[name]) > 1000:
            self.metrics_by_name[name] = self.metrics_by_name[name][-1000:]
        
        # Atualizar estatísticas
        self.stats['total_metrics'] += 1
        self.stats['metrics_by_type'][metric_type.value] += 1
    
    def record_counter(self, name: str, value: float = 1.0, **kwargs):
        """Registrar métrica do tipo counter."""
        self.record_metric(name, value, MetricType.COUNTER, **kwargs)
    
    def record_gauge(self, name: str, value: float, **kwargs):
        """Registrar métrica do tipo gauge."""
        self.record_metric(name, value, MetricType.GAUGE, **kwargs)
    
    def record_histogram(self, name: str, value: float, **kwargs):
        """Registrar métrica do tipo histogram."""
        self.record_metric(name, value, MetricType.HISTOGRAM, **kwargs)
    
    def get_metric_stats(self, name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """
        Obter estatísticas de uma métrica.
        
        Args:
            name: Nome da métrica
            window_minutes: Janela de tempo em minutos
            
        Returns:
            Estatísticas da métrica
        """
        if name not in self.metrics_by_name:
            return {}
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in self.metrics_by_name[name]
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        values = [m.value for m in recent_metrics]
        
        return {
            'name': name,
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'window_minutes': window_minutes,
            'last_value': recent_metrics[-1].value,
            'last_timestamp': recent_metrics[-1].timestamp.isoformat()
        }
    
    def _persist_loop(self):
        """Loop de persistência de métricas."""
        while self.running:
            try:
                self._persist_metrics()
                time.sleep(60)  # Persistir a cada minuto
            except Exception as e:
                logging.error(f"Erro no loop de persistência: {e}")
                time.sleep(10)
    
    def _persist_metrics(self):
        """Persistir métricas no banco de dados."""
        if not self.metrics_buffer:
            return
        
        metrics_to_persist = list(self.metrics_buffer)
        self.metrics_buffer.clear()
        
        with sqlite3.connect(self.db_path) as conn:
            for metric in metrics_to_persist:
                conn.execute("""
                    INSERT INTO metrics (
                        name, value, metric_type, timestamp, labels,
                        description, unit, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.name,
                    metric.value,
                    metric.metric_type.value,
                    metric.timestamp.isoformat(),
                    json.dumps(metric.labels),
                    metric.description,
                    metric.unit,
                    datetime.utcnow().isoformat()
                ))
            conn.commit()
        
        self.stats['last_persist'] = datetime.utcnow().isoformat()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do coletor."""
        return self.stats.copy()

class HealthChecker:
    """
    Sistema de health checks.
    
    Funcionalidades:
    - Health checks customizados
    - Verificação de dependências
    - Monitoramento de endpoints
    - Alertas de degradação
    """
    
    def __init__(self):
        """Inicializar health checker."""
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
        """
        Registrar health check.
        
        Args:
            name: Nome do health check
            check_func: Função de verificação
            interval: Intervalo em segundos
            timeout: Timeout em segundos
            description: Descrição do health check
        """
        self.health_checks[name] = {
            'function': check_func,
            'interval': interval,
            'timeout': timeout,
            'description': description,
            'last_check': None,
            'last_status': HealthStatus.UNKNOWN
        }
    
    def check_health(self, name: str) -> HealthCheck:
        """
        Executar health check específico.
        
        Args:
            name: Nome do health check
            
        Returns:
            Resultado do health check
        """
        if name not in self.health_checks:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNKNOWN,
                timestamp=datetime.utcnow(),
                error_message="Health check não encontrado"
            )
        
        check_config = self.health_checks[name]
        start_time = time.time()
        
        try:
            # Executar health check com timeout
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Health check timeout")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(check_config['timeout'])
            
            try:
                status = check_config['function']()
                signal.alarm(0)  # Cancelar alarme
            except TimeoutError:
                status = HealthStatus.UNHEALTHY
                error_message = "Timeout"
            except Exception as e:
                status = HealthStatus.UNHEALTHY
                error_message = str(e)
            else:
                error_message = None
            
            response_time = time.time() - start_time
            
            health_check = HealthCheck(
                name=name,
                status=status,
                timestamp=datetime.utcnow(),
                response_time=response_time,
                error_message=error_message
            )
            
            # Atualizar estado
            check_config['last_check'] = health_check.timestamp
            check_config['last_status'] = status
            self.check_results[name] = health_check
            
            return health_check
            
        except Exception as e:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
    
    def check_all_health(self) -> Dict[str, HealthCheck]:
        """Executar todos os health checks."""
        results = {}
        
        for name in self.health_checks:
            # Verificar se é hora de executar
            check_config = self.health_checks[name]
            if check_config['last_check']:
                time_since_last = (datetime.utcnow() - check_config['last_check']).total_seconds()
                if time_since_last < check_config['interval']:
                    # Usar resultado anterior
                    if name in self.check_results:
                        results[name] = self.check_results[name]
                    continue
            
            results[name] = self.check_health(name)
        
        return results
    
    def get_overall_health(self) -> HealthStatus:
        """Obter status geral de saúde."""
        results = self.check_all_health()
        
        if not results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

class SystemMetricsCollector:
    """
    Coletor de métricas do sistema.
    
    Funcionalidades:
    - Métricas de CPU
    - Métricas de memória
    - Métricas de disco
    - Métricas de rede
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        """
        Inicializar coletor de métricas do sistema.
        
        Args:
            metrics_collector: Coletor de métricas
        """
        self.metrics_collector = metrics_collector
        self.running = True
        
        # Thread para coleta contínua
        self.collector_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.collector_thread.start()
    
    def _collect_loop(self):
        """Loop de coleta de métricas do sistema."""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(60)  # Coletar a cada minuto
            except Exception as e:
                logging.error(f"Erro na coleta de métricas do sistema: {e}")
                time.sleep(10)
    
    def _collect_system_metrics(self):
        """Coletar métricas do sistema."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_collector.record_gauge(
            'system_cpu_usage',
            cpu_percent,
            description="Uso de CPU do sistema",
            unit="percent"
        )
        
        # Memória
        memory = psutil.virtual_memory()
        self.metrics_collector.record_gauge(
            'system_memory_usage',
            memory.percent,
            description="Uso de memória do sistema",
            unit="percent"
        )
        self.metrics_collector.record_gauge(
            'system_memory_available',
            memory.available / (1024**3),  # GB
            description="Memória disponível",
            unit="GB"
        )
        
        # Disco
        disk = psutil.disk_usage('/')
        self.metrics_collector.record_gauge(
            'system_disk_usage',
            disk.percent,
            description="Uso de disco do sistema",
            unit="percent"
        )
        self.metrics_collector.record_gauge(
            'system_disk_free',
            disk.free / (1024**3),  # GB
            description="Espaço livre em disco",
            unit="GB"
        )
        
        # Rede
        network = psutil.net_io_counters()
        self.metrics_collector.record_counter(
            'system_network_bytes_sent',
            network.bytes_sent,
            description="Bytes enviados pela rede"
        )
        self.metrics_collector.record_counter(
            'system_network_bytes_recv',
            network.bytes_recv,
            description="Bytes recebidos pela rede"
        )
        
        # Processos
        process_count = len(psutil.pids())
        self.metrics_collector.record_gauge(
            'system_process_count',
            process_count,
            description="Número de processos ativos"
        )

class BusinessMetricsCollector:
    """
    Coletor de métricas de negócio.
    
    Funcionalidades:
    - Métricas de usuários ativos
    - Métricas de processamento
    - Métricas de performance
    - Métricas de qualidade
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        """
        Inicializar coletor de métricas de negócio.
        
        Args:
            metrics_collector: Coletor de métricas
        """
        self.metrics_collector = metrics_collector
        self.business_stats = {
            'active_users': 0,
            'keywords_processed': 0,
            'success_rate': 0.0,
            'avg_processing_time': 0.0
        }
    
    def record_user_activity(self, user_id: str, action: str, success: bool = True):
        """Registrar atividade do usuário."""
        self.metrics_collector.record_counter(
            f'user_activity_{action}',
            1,
            labels={'user_id': user_id, 'success': str(success).lower()}
        )
    
    def record_keyword_processing(self, keyword: str, processing_time: float, success: bool = True):
        """Registrar processamento de keyword."""
        self.metrics_collector.record_counter(
            'keywords_processed_total',
            1,
            labels={'success': str(success).lower()}
        )
        
        self.metrics_collector.record_histogram(
            'keyword_processing_time',
            processing_time,
            labels={'success': str(success).lower()},
            unit="seconds"
        )
        
        # Atualizar estatísticas de negócio
        self.business_stats['keywords_processed'] += 1
        
        # Calcular taxa de sucesso
        if hasattr(self, '_processing_results'):
            self._processing_results.append(success)
            if len(self._processing_results) > 1000:
                self._processing_results = self._processing_results[-1000:]
        else:
            self._processing_results = [success]
        
        success_rate = sum(self._processing_results) / len(self._processing_results)
        self.business_stats['success_rate'] = success_rate
        
        # Atualizar tempo médio de processamento
        if hasattr(self, '_processing_times'):
            self._processing_times.append(processing_time)
            if len(self._processing_times) > 1000:
                self._processing_times = self._processing_times[-1000:]
        else:
            self._processing_times = [processing_time]
        
        avg_time = statistics.mean(self._processing_times)
        self.business_stats['avg_processing_time'] = avg_time
        
        # Registrar métricas de negócio
        self.metrics_collector.record_gauge(
            'business_success_rate',
            success_rate,
            description="Taxa de sucesso do processamento",
            unit="percent"
        )
        
        self.metrics_collector.record_gauge(
            'business_avg_processing_time',
            avg_time,
            description="Tempo médio de processamento",
            unit="seconds"
        )
    
    def record_api_call(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Registrar chamada de API."""
        self.metrics_collector.record_counter(
            'api_calls_total',
            1,
            labels={'endpoint': endpoint, 'method': method, 'status_code': str(status_code)}
        )
        
        self.metrics_collector.record_histogram(
            'api_response_time',
            response_time,
            labels={'endpoint': endpoint, 'method': method},
            unit="seconds"
        )
    
    def get_business_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de negócio."""
        return self.business_stats.copy()

# Instâncias globais
_metrics_collector: Optional[MetricsCollector] = None
_health_checker: Optional[HealthChecker] = None
_system_metrics: Optional[SystemMetricsCollector] = None
_business_metrics: Optional[BusinessMetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Obter instância global do coletor de métricas."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_health_checker() -> HealthChecker:
    """Obter instância global do health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

def get_system_metrics() -> SystemMetricsCollector:
    """Obter instância global do coletor de métricas do sistema."""
    global _system_metrics
    if _system_metrics is None:
        _system_metrics = SystemMetricsCollector(get_metrics_collector())
    return _system_metrics

def get_business_metrics() -> BusinessMetricsCollector:
    """Obter instância global do coletor de métricas de negócio."""
    global _business_metrics
    if _business_metrics is None:
        _business_metrics = BusinessMetricsCollector(get_metrics_collector())
    return _business_metrics

def record_metric(name: str, value: float, **kwargs):
    """Registrar métrica."""
    collector = get_metrics_collector()
    collector.record_metric(name, value, **kwargs)

def check_health(name: str) -> HealthCheck:
    """Executar health check."""
    checker = get_health_checker()
    return checker.check_health(name)

def record_business_metric(keyword: str, processing_time: float, success: bool = True):
    """Registrar métrica de negócio."""
    business_metrics = get_business_metrics()
    business_metrics.record_keyword_processing(keyword, processing_time, success) 