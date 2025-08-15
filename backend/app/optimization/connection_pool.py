"""
Connection Pool Optimization - Omni Keywords Finder
Tracing ID: CONNECTION_POOL_20250127_001

Sistema de pool de conexões escalável com configuração adaptativa
baseada em carga e monitoramento em tempo real.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError

# Configuração de logging
logger = logging.getLogger(__name__)

class PoolStatus(Enum):
    """Status do pool de conexões"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OVERLOADED = "overloaded"

@dataclass
class PoolMetrics:
    """Métricas do pool de conexões"""
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    avg_wait_time: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    status: PoolStatus
    timestamp: float

class AdaptiveConnectionPool:
    """
    Pool de conexões adaptativo com configuração dinâmica
    baseada em métricas de performance e carga do sistema
    """
    
    def __init__(
        self,
        database_url: str,
        initial_pool_size: int = 20,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        max_overflow: int = 20,
        pre_ping: bool = True
    ):
        self.database_url = database_url
        self.initial_pool_size = initial_pool_size
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.max_overflow = max_overflow
        self.pre_ping = pre_ping
        
        # Métricas e monitoramento
        self.metrics_history: List[PoolMetrics] = []
        self.max_history_size = 1000
        self.adaptation_interval = 60  # segundos
        self.last_adaptation = time.time()
        
        # Configurações adaptativas
        self.adaptation_enabled = True
        self.auto_scaling = True
        self.health_check_interval = 30  # segundos
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        # Inicializar pool
        self._initialize_pool()
        self._start_monitoring()
    
    def _initialize_pool(self):
        """Inicializa o pool de conexões com configurações otimizadas"""
        try:
            # Configurações do engine
            engine_config = {
                'poolclass': QueuePool,
                'pool_size': self.initial_pool_size,
                'max_overflow': self.max_overflow,
                'pool_timeout': self.pool_timeout,
                'pool_recycle': self.pool_recycle,
                'pool_pre_ping': self.pre_ping,
                'echo': False,
                'echo_pool': False,
                'pool_reset_on_return': 'commit',
                'isolation_level': 'READ_COMMITTED'
            }
            
            # Criar engine
            self.engine = create_engine(self.database_url, **engine_config)
            
            # Configurar eventos para monitoramento
            self._setup_engine_events()
            
            # Criar session factory
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            logger.info(f"Connection pool initialized: size={self.initial_pool_size}, max={self.max_pool_size}")
            
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def _setup_engine_events(self):
        """Configura eventos do engine para monitoramento"""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            logger.debug("New database connection established")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug("Database connection checked out")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            logger.debug("Database connection checked in")
        
        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_connection):
            logger.debug("Database connection closed")
    
    def _start_monitoring(self):
        """Inicia thread de monitoramento"""
        if self._monitoring_thread is None:
            self._stop_monitoring.clear()
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="ConnectionPoolMonitor"
            )
            self._monitoring_thread.start()
            logger.info("Connection pool monitoring started")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while not self._stop_monitoring.is_set():
            try:
                # Coletar métricas
                metrics = self._collect_metrics()
                
                # Armazenar métricas
                with self._lock:
                    self.metrics_history.append(metrics)
                    if len(self.metrics_history) > self.max_history_size:
                        self.metrics_history.pop(0)
                
                # Adaptar pool se necessário
                if self.adaptation_enabled and self._should_adapt():
                    self._adapt_pool()
                
                # Log de status
                if metrics.status in [PoolStatus.WARNING, PoolStatus.CRITICAL]:
                    logger.warning(f"Pool status: {metrics.status.value}, active: {metrics.active_connections}/{self.engine.pool.size()}")
                
                # Aguardar próximo ciclo
                self._stop_monitoring.wait(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self._stop_monitoring.wait(5)  # Aguardar 5 segundos em caso de erro
    
    def _collect_metrics(self) -> PoolMetrics:
        """Coleta métricas atuais do pool"""
        try:
            pool = self.engine.pool
            
            # Métricas do pool
            total_connections = pool.size()
            active_connections = pool.checkedin() + pool.checkedout()
            idle_connections = pool.checkedin()
            waiting_requests = pool.overflow()
            
            # Calcular tempo médio de espera (simplificado)
            avg_wait_time = self._calculate_avg_wait_time()
            
            # Calcular taxa de erro
            error_rate = self._calculate_error_rate()
            
            # Métricas do sistema
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            # Determinar status
            status = self._determine_pool_status(
                active_connections, total_connections, 
                waiting_requests, error_rate, cpu_usage
            )
            
            return PoolMetrics(
                total_connections=total_connections,
                active_connections=active_connections,
                idle_connections=idle_connections,
                waiting_requests=waiting_requests,
                avg_wait_time=avg_wait_time,
                error_rate=error_rate,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                status=status,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return PoolMetrics(
                total_connections=0,
                active_connections=0,
                idle_connections=0,
                waiting_requests=0,
                avg_wait_time=0.0,
                error_rate=1.0,
                cpu_usage=0.0,
                memory_usage=0.0,
                status=PoolStatus.CRITICAL,
                timestamp=time.time()
            )
    
    def _calculate_avg_wait_time(self) -> float:
        """Calcula tempo médio de espera (implementação simplificada)"""
        # Em produção, isso seria calculado com métricas reais
        return 0.1  # 100ms como exemplo
    
    def _calculate_error_rate(self) -> float:
        """Calcula taxa de erro (implementação simplificada)"""
        # Em produção, isso seria calculado com métricas reais
        return 0.01  # 1% como exemplo
    
    def _determine_pool_status(
        self, 
        active_connections: int, 
        total_connections: int,
        waiting_requests: int,
        error_rate: float,
        cpu_usage: float
    ) -> PoolStatus:
        """Determina status do pool baseado em métricas"""
        
        utilization_rate = active_connections / total_connections if total_connections > 0 else 0
        
        # Critérios para status
        if error_rate > 0.1 or cpu_usage > 90:
            return PoolStatus.CRITICAL
        elif utilization_rate > 0.9 or waiting_requests > 10:
            return PoolStatus.OVERLOADED
        elif utilization_rate > 0.7 or waiting_requests > 5:
            return PoolStatus.WARNING
        else:
            return PoolStatus.HEALTHY
    
    def _should_adapt(self) -> bool:
        """Verifica se deve adaptar o pool"""
        now = time.time()
        return (now - self.last_adaptation) >= self.adaptation_interval
    
    def _adapt_pool(self):
        """Adapta configuração do pool baseado em métricas"""
        try:
            with self._lock:
                if not self.metrics_history:
                    return
                
                # Obter métricas recentes
                recent_metrics = self.metrics_history[-10:]  # Últimas 10 medições
                avg_utilization = sum(m.active_connections / m.total_connections for m in recent_metrics) / len(recent_metrics)
                avg_waiting = sum(m.waiting_requests for m in recent_metrics) / len(recent_metrics)
                avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
                
                current_pool_size = self.engine.pool.size()
                new_pool_size = current_pool_size
                
                # Lógica de adaptação
                if avg_utilization > 0.8 and avg_waiting > 5:
                    # Aumentar pool se alta utilização e fila de espera
                    new_pool_size = min(current_pool_size + 10, self.max_pool_size)
                    logger.info(f"Scaling up pool: {current_pool_size} -> {new_pool_size}")
                    
                elif avg_utilization < 0.3 and avg_waiting < 2:
                    # Diminuir pool se baixa utilização
                    new_pool_size = max(current_pool_size - 5, self.min_pool_size)
                    logger.info(f"Scaling down pool: {current_pool_size} -> {new_pool_size}")
                
                # Aplicar mudança se necessário
                if new_pool_size != current_pool_size:
                    self._resize_pool(new_pool_size)
                
                self.last_adaptation = time.time()
                
        except Exception as e:
            logger.error(f"Error adapting pool: {e}")
    
    def _resize_pool(self, new_size: int):
        """Redimensiona o pool de conexões"""
        try:
            # Em SQLAlchemy, o redimensionamento é automático
            # mas podemos ajustar configurações
            self.engine.pool.resize(new_size)
            logger.info(f"Pool resized to {new_size} connections")
            
        except Exception as e:
            logger.error(f"Error resizing pool: {e}")
    
    @asynccontextmanager
    async def get_connection(self):
        """Obtém conexão do pool com gerenciamento automático"""
        session = None
        try:
            session = self.SessionLocal()
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            if session:
                session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if session:
                session.rollback()
            raise
        finally:
            if session:
                session.close()
    
    def get_session(self) -> Session:
        """Obtém sessão do pool"""
        return self.SessionLocal()
    
    def get_metrics(self) -> PoolMetrics:
        """Obtém métricas atuais do pool"""
        with self._lock:
            if self.metrics_history:
                return self.metrics_history[-1]
            return None
    
    def get_metrics_history(self, limit: int = 100) -> List[PoolMetrics]:
        """Obtém histórico de métricas"""
        with self._lock:
            return self.metrics_history[-limit:] if self.metrics_history else []
    
    def health_check(self) -> bool:
        """Verifica saúde do pool"""
        try:
            with self.get_connection() as session:
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def shutdown(self):
        """Desliga o pool de conexões"""
        try:
            self._stop_monitoring.set()
            if self._monitoring_thread:
                self._monitoring_thread.join(timeout=5)
            
            if hasattr(self, 'engine'):
                self.engine.dispose()
            
            logger.info("Connection pool shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Instância global do pool
_connection_pool: Optional[AdaptiveConnectionPool] = None

def get_connection_pool() -> AdaptiveConnectionPool:
    """Obtém instância global do pool de conexões"""
    global _connection_pool
    if _connection_pool is None:
        raise RuntimeError("Connection pool not initialized")
    return _connection_pool

def initialize_connection_pool(database_url: str, **kwargs) -> AdaptiveConnectionPool:
    """Inicializa pool de conexões global"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = AdaptiveConnectionPool(database_url, **kwargs)
    return _connection_pool

def shutdown_connection_pool():
    """Desliga pool de conexões global"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.shutdown()
        _connection_pool = None 