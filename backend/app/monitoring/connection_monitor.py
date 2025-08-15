"""
Connection Monitor - Omni Keywords Finder
Tracing ID: CONNECTION_MONITOR_20250127_001

Sistema de monitoramento de conexões com métricas em tempo real
e integração com Prometheus para observabilidade.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import psutil

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError

# Configuração de logging
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Estados das conexões"""
    IDLE = "idle"
    ACTIVE = "active"
    WAITING = "waiting"
    ERROR = "error"
    CLOSED = "closed"

@dataclass
class ConnectionMetrics:
    """Métricas de uma conexão individual"""
    connection_id: str
    state: ConnectionState
    created_at: float
    last_used: float
    total_queries: int
    total_errors: int
    avg_response_time: float
    last_query: Optional[str] = None
    last_error: Optional[str] = None

@dataclass
class PoolMetrics:
    """Métricas agregadas do pool"""
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_connections: int
    error_connections: int
    avg_response_time: float
    total_queries: int
    total_errors: int
    error_rate: float
    utilization_rate: float
    timestamp: float

class ConnectionMonitor:
    """
    Monitor de conexões com métricas em tempo real e alertas
    """
    
    def __init__(
        self,
        database_url: str,
        monitoring_interval: int = 10,
        metrics_retention: int = 3600,  # 1 hora
        enable_prometheus: bool = True,
        alert_thresholds: Optional[Dict[str, float]] = None
    ):
        self.database_url = database_url
        self.monitoring_interval = monitoring_interval
        self.metrics_retention = metrics_retention
        self.enable_prometheus = enable_prometheus
        
        # Configurações de alerta
        self.alert_thresholds = alert_thresholds or {
            'error_rate': 0.05,  # 5%
            'utilization_rate': 0.9,  # 90%
            'avg_response_time': 1.0,  # 1 segundo
            'waiting_connections': 10
        }
        
        # Estado do monitoramento
        self.is_running = False
        self.connection_metrics: Dict[str, ConnectionMetrics] = {}
        self.pool_metrics_history: deque = deque(maxlen=metrics_retention)
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._stop_event = threading.Event()
        
        # Callbacks e alertas
        self._alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self._metrics_callbacks: List[Callable[[PoolMetrics], None]] = []
        
        # Prometheus metrics (se habilitado)
        if self.enable_prometheus:
            self._setup_prometheus_metrics()
        
        logger.info(f"Connection monitor initialized: interval={monitoring_interval}s")
    
    def _setup_prometheus_metrics(self):
        """Configura métricas do Prometheus"""
        try:
            from prometheus_client import Counter, Gauge, Histogram
            
            # Métricas do Prometheus
            self.prometheus_metrics = {
                'connections_total': Gauge('db_connections_total', 'Total number of connections'),
                'connections_active': Gauge('db_connections_active', 'Number of active connections'),
                'connections_idle': Gauge('db_connections_idle', 'Number of idle connections'),
                'connections_waiting': Gauge('db_connections_waiting', 'Number of waiting connections'),
                'connections_errors': Gauge('db_connections_errors', 'Number of connections with errors'),
                'queries_total': Counter('db_queries_total', 'Total number of queries'),
                'queries_errors': Counter('db_queries_errors', 'Total number of query errors'),
                'response_time': Histogram('db_response_time_seconds', 'Database response time'),
                'error_rate': Gauge('db_error_rate', 'Database error rate'),
                'utilization_rate': Gauge('db_utilization_rate', 'Connection pool utilization rate')
            }
            
            logger.info("Prometheus metrics configured")
            
        except ImportError:
            logger.warning("Prometheus client not available, metrics disabled")
            self.enable_prometheus = False
            self.prometheus_metrics = {}
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Adiciona callback para alertas"""
        self._alert_callbacks.append(callback)
    
    def add_metrics_callback(self, callback: Callable[[PoolMetrics], None]):
        """Adiciona callback para métricas"""
        self._metrics_callbacks.append(callback)
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        if self.is_running:
            logger.warning("Connection monitor already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ConnectionMonitor"
        )
        self._monitoring_thread.start()
        
        logger.info("Connection monitoring started")
    
    def stop_monitoring(self):
        """Para monitoramento contínuo"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        
        logger.info("Connection monitoring stopped")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while not self._stop_event.is_set():
            try:
                # Coletar métricas
                pool_metrics = self._collect_pool_metrics()
                
                # Armazenar métricas
                with self._lock:
                    self.pool_metrics_history.append(pool_metrics)
                
                # Atualizar métricas do Prometheus
                if self.enable_prometheus:
                    self._update_prometheus_metrics(pool_metrics)
                
                # Verificar alertas
                self._check_alerts(pool_metrics)
                
                # Notificar callbacks
                self._notify_metrics_callbacks(pool_metrics)
                
                # Aguardar próximo ciclo
                self._stop_event.wait(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self._stop_event.wait(5)  # Aguardar 5 segundos em caso de erro
    
    def _collect_pool_metrics(self) -> PoolMetrics:
        """Coleta métricas do pool de conexões"""
        try:
            # Criar engine temporário para coleta
            engine = create_engine(self.database_url, pool_pre_ping=True)
            pool = engine.pool
            
            # Métricas básicas do pool
            total_connections = pool.size()
            active_connections = pool.checkedout()
            idle_connections = pool.checkedin()
            waiting_connections = pool.overflow()
            
            # Calcular métricas agregadas
            total_queries = sum(conn.total_queries for conn in self.connection_metrics.values())
            total_errors = sum(conn.total_errors for conn in self.connection_metrics.values())
            
            # Calcular taxas
            error_rate = total_errors / total_queries if total_queries > 0 else 0.0
            utilization_rate = active_connections / total_connections if total_connections > 0 else 0.0
            
            # Calcular tempo médio de resposta
            response_times = [conn.avg_response_time for conn in self.connection_metrics.values() if conn.avg_response_time > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            
            # Contar conexões com erro
            error_connections = sum(1 for conn in self.connection_metrics.values() if conn.state == ConnectionState.ERROR)
            
            metrics = PoolMetrics(
                total_connections=total_connections,
                active_connections=active_connections,
                idle_connections=idle_connections,
                waiting_connections=waiting_connections,
                error_connections=error_connections,
                avg_response_time=avg_response_time,
                total_queries=total_queries,
                total_errors=total_errors,
                error_rate=error_rate,
                utilization_rate=utilization_rate,
                timestamp=time.time()
            )
            
            logger.debug(f"Pool metrics collected: active={active_connections}/{total_connections}, error_rate={error_rate:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting pool metrics: {e}")
            return PoolMetrics(
                total_connections=0,
                active_connections=0,
                idle_connections=0,
                waiting_connections=0,
                error_connections=0,
                avg_response_time=0.0,
                total_queries=0,
                total_errors=0,
                error_rate=1.0,
                utilization_rate=0.0,
                timestamp=time.time()
            )
    
    def _update_prometheus_metrics(self, metrics: PoolMetrics):
        """Atualiza métricas do Prometheus"""
        try:
            self.prometheus_metrics['connections_total'].set(metrics.total_connections)
            self.prometheus_metrics['connections_active'].set(metrics.active_connections)
            self.prometheus_metrics['connections_idle'].set(metrics.idle_connections)
            self.prometheus_metrics['connections_waiting'].set(metrics.waiting_connections)
            self.prometheus_metrics['connections_errors'].set(metrics.error_connections)
            self.prometheus_metrics['error_rate'].set(metrics.error_rate)
            self.prometheus_metrics['utilization_rate'].set(metrics.utilization_rate)
            
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    def _check_alerts(self, metrics: PoolMetrics):
        """Verifica se há alertas baseados nas métricas"""
        alerts = []
        
        # Verificar taxa de erro
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'message': f'High error rate: {metrics.error_rate:.3f}',
                'value': metrics.error_rate,
                'threshold': self.alert_thresholds['error_rate']
            })
        
        # Verificar taxa de utilização
        if metrics.utilization_rate > self.alert_thresholds['utilization_rate']:
            alerts.append({
                'type': 'high_utilization',
                'message': f'High utilization rate: {metrics.utilization_rate:.3f}',
                'value': metrics.utilization_rate,
                'threshold': self.alert_thresholds['utilization_rate']
            })
        
        # Verificar tempo de resposta
        if metrics.avg_response_time > self.alert_thresholds['avg_response_time']:
            alerts.append({
                'type': 'slow_response',
                'message': f'Slow response time: {metrics.avg_response_time:.3f}s',
                'value': metrics.avg_response_time,
                'threshold': self.alert_thresholds['avg_response_time']
            })
        
        # Verificar conexões em espera
        if metrics.waiting_connections > self.alert_thresholds['waiting_connections']:
            alerts.append({
                'type': 'high_waiting',
                'message': f'High number of waiting connections: {metrics.waiting_connections}',
                'value': metrics.waiting_connections,
                'threshold': self.alert_thresholds['waiting_connections']
            })
        
        # Notificar alertas
        for alert in alerts:
            self._notify_alert_callbacks(alert)
    
    def _notify_alert_callbacks(self, alert: Dict[str, Any]):
        """Notifica callbacks de alerta"""
        for callback in self._alert_callbacks:
            try:
                callback(alert['type'], alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _notify_metrics_callbacks(self, metrics: PoolMetrics):
        """Notifica callbacks de métricas"""
        for callback in self._metrics_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"Error in metrics callback: {e}")
    
    def track_connection(self, connection_id: str, session: Session):
        """Rastreia uma conexão específica"""
        try:
            with self._lock:
                if connection_id not in self.connection_metrics:
                    self.connection_metrics[connection_id] = ConnectionMetrics(
                        connection_id=connection_id,
                        state=ConnectionState.ACTIVE,
                        created_at=time.time(),
                        last_used=time.time(),
                        total_queries=0,
                        total_errors=0,
                        avg_response_time=0.0
                    )
                
                # Atualizar estado
                conn_metrics = self.connection_metrics[connection_id]
                conn_metrics.last_used = time.time()
                conn_metrics.state = ConnectionState.ACTIVE
                
                # Configurar eventos para rastreamento
                self._setup_connection_events(connection_id, session)
                
        except Exception as e:
            logger.error(f"Error tracking connection {connection_id}: {e}")
    
    def _setup_connection_events(self, connection_id: str, session: Session):
        """Configura eventos para rastrear uma conexão"""
        try:
            @event.listens_for(session, 'after_cursor_execute')
            def after_cursor_execute(session, cursor, statement, parameters, context, executemany):
                self._record_query(connection_id, statement, time.time())
            
            @event.listens_for(session, 'after_cursor_execute')
            def after_cursor_execute_error(session, cursor, statement, parameters, context, executemany):
                if hasattr(cursor, 'error'):
                    self._record_error(connection_id, str(cursor.error))
                    
        except Exception as e:
            logger.error(f"Error setting up connection events: {e}")
    
    def _record_query(self, connection_id: str, query: str, timestamp: float):
        """Registra uma query executada"""
        try:
            with self._lock:
                if connection_id in self.connection_metrics:
                    conn_metrics = self.connection_metrics[connection_id]
                    conn_metrics.total_queries += 1
                    conn_metrics.last_query = query
                    conn_metrics.last_used = timestamp
                    
                    # Atualizar tempo médio de resposta (simplificado)
                    if conn_metrics.avg_response_time == 0:
                        conn_metrics.avg_response_time = 0.1  # Estimativa
                    else:
                        conn_metrics.avg_response_time = (
                            conn_metrics.avg_response_time * 0.9 + 0.1 * 0.9
                        )
                        
        except Exception as e:
            logger.error(f"Error recording query: {e}")
    
    def _record_error(self, connection_id: str, error: str):
        """Registra um erro de conexão"""
        try:
            with self._lock:
                if connection_id in self.connection_metrics:
                    conn_metrics = self.connection_metrics[connection_id]
                    conn_metrics.total_errors += 1
                    conn_metrics.last_error = error
                    conn_metrics.state = ConnectionState.ERROR
                    
        except Exception as e:
            logger.error(f"Error recording error: {e}")
    
    def get_current_metrics(self) -> Optional[PoolMetrics]:
        """Obtém métricas atuais"""
        with self._lock:
            if self.pool_metrics_history:
                return self.pool_metrics_history[-1]
            return None
    
    def get_metrics_history(self, limit: int = 100) -> List[PoolMetrics]:
        """Obtém histórico de métricas"""
        with self._lock:
            return list(self.pool_metrics_history)[-limit:] if self.pool_metrics_history else []
    
    def get_connection_details(self, connection_id: str) -> Optional[ConnectionMetrics]:
        """Obtém detalhes de uma conexão específica"""
        with self._lock:
            return self.connection_metrics.get(connection_id)
    
    def get_all_connections(self) -> Dict[str, ConnectionMetrics]:
        """Obtém todas as conexões rastreadas"""
        with self._lock:
            return self.connection_metrics.copy()
    
    def export_metrics(self) -> Dict[str, Any]:
        """Exporta métricas para formato JSON"""
        try:
            current_metrics = self.get_current_metrics()
            metrics_history = self.get_metrics_history(10)  # Últimas 10 medições
            
            return {
                'current_metrics': current_metrics.__dict__ if current_metrics else None,
                'metrics_history': [m.__dict__ for m in metrics_history],
                'connections': {
                    conn_id: conn.__dict__ for conn_id, conn in self.connection_metrics.items()
                },
                'alert_thresholds': self.alert_thresholds,
                'is_running': self.is_running,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return {'error': str(e)}

# Instância global do monitor
_connection_monitor: Optional[ConnectionMonitor] = None

def get_connection_monitor() -> ConnectionMonitor:
    """Obtém instância global do monitor de conexões"""
    global _connection_monitor
    if _connection_monitor is None:
        raise RuntimeError("Connection monitor not initialized")
    return _connection_monitor

def initialize_connection_monitor(database_url: str, **kwargs) -> ConnectionMonitor:
    """Inicializa monitor de conexões global"""
    global _connection_monitor
    if _connection_monitor is None:
        _connection_monitor = ConnectionMonitor(database_url, **kwargs)
    return _connection_monitor

def shutdown_connection_monitor():
    """Desliga monitor de conexões global"""
    global _connection_monitor
    if _connection_monitor:
        _connection_monitor.stop_monitoring()
        _connection_monitor = None 