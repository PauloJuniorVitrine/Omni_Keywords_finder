"""
🔧 INT-008: Connection Pooling Optimization - Omni Keywords Finder

Tracing ID: INT_008_CONNECTION_POOLING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Implementar sistema de connection pooling otimizado com health checks,
pool sizing inteligente e connection recycling para o sistema Omni Keywords Finder.
"""

import os
import time
import threading
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import queue
import weakref
from contextlib import contextmanager
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Estados de uma conexão."""
    IDLE = "idle"
    IN_USE = "in_use"
    BROKEN = "broken"
    CREATING = "creating"
    CLOSING = "closing"

class PoolStrategy(Enum):
    """Estratégias de pool."""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"
    LAZY = "lazy"

@dataclass
class ConnectionConfig:
    """Configuração de conexão."""
    # Configurações básicas
    host: str = "localhost"
    port: int = 5432
    database: str = "omni_keywords"
    username: str = "postgres"
    password: str = ""
    
    # Configurações de timeout
    connect_timeout: int = 10
    read_timeout: int = 30
    write_timeout: int = 30
    
    # Configurações de SSL
    ssl_enabled: bool = False
    ssl_verify: bool = True
    
    # Configurações de charset
    charset: str = "utf8"
    collation: str = "utf8_general_ci"

@dataclass
class PoolConfig:
    """Configuração do pool de conexões."""
    # Configurações de tamanho
    min_size: int = 5
    max_size: int = 20
    initial_size: int = 10
    
    # Configurações de timeout
    acquire_timeout: int = 30
    release_timeout: int = 10
    
    # Configurações de health check
    health_check_interval: int = 60  # segundos
    health_check_timeout: int = 5
    health_check_query: str = "SELECT 1"
    
    # Configurações de recycling
    max_lifetime: int = 3600  # segundos
    max_idle_time: int = 1800  # segundos
    
    # Configurações de retry
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Configurações de monitoramento
    enable_metrics: bool = True
    enable_logging: bool = True
    
    # Configurações de estratégia
    strategy: PoolStrategy = PoolStrategy.ADAPTIVE
    
    # Configurações adaptativas
    adaptive_enabled: bool = True
    adaptive_learning_period: int = 300  # segundos
    adaptive_threshold: float = 0.8  # 80% de utilização

@dataclass
class ConnectionInfo:
    """Informações de uma conexão."""
    id: str
    state: ConnectionState
    created_at: float
    last_used: float
    last_health_check: float
    usage_count: int
    error_count: int
    connection: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PoolMetrics:
    """Métricas do pool."""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    broken_connections: int = 0
    
    total_acquires: int = 0
    total_releases: int = 0
    total_creates: int = 0
    total_destroys: int = 0
    
    acquire_timeouts: int = 0
    health_check_failures: int = 0
    connection_errors: int = 0
    
    avg_acquire_time: float = 0.0
    avg_release_time: float = 0.0
    avg_health_check_time: float = 0.0
    
    pool_utilization: float = 0.0
    connection_efficiency: float = 0.0

class ConnectionFactory:
    """Factory para criação de conexões."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.connection_counter = 0
        self.lock = threading.Lock()
    
    def create_connection(self) -> Tuple[str, Any]:
        """Cria uma nova conexão."""
        with self.lock:
            self.connection_counter += 1
            connection_id = f"conn_{self.connection_counter}_{int(time.time())}"
        
        try:
            # Simula criação de conexão (substituir pela implementação real)
            connection = self._create_real_connection()
            
            logger.info({
                "event": "connection_created",
                "status": "success",
                "source": "ConnectionFactory.create_connection",
                "details": {
                    "connection_id": connection_id,
                    "host": self.config.host,
                    "port": self.config.port,
                    "database": self.config.database
                }
            })
            
            return connection_id, connection
            
        except Exception as e:
            logger.error({
                "event": "connection_creation_failed",
                "status": "error",
                "source": "ConnectionFactory.create_connection",
                "details": {
                    "connection_id": connection_id,
                    "error": str(e),
                    "host": self.config.host,
                    "port": self.config.port
                }
            })
            raise
    
    def _create_real_connection(self) -> Any:
        """Cria conexão real (implementação específica do banco)."""
        # TODO: Implementar criação real de conexão baseada no tipo de banco
        # Exemplo para PostgreSQL:
        # import psycopg2
        # return psycopg2.connect(
        #     host=self.config.host,
        #     port=self.config.port,
        #     database=self.config.database,
        #     user=self.config.username,
        #     password=self.config.password,
        #     connect_timeout=self.config.connect_timeout
        # )
        
        # Por enquanto, retorna um mock
        return MockConnection(self.config)
    
    def validate_connection(self, connection: Any) -> bool:
        """Valida se uma conexão está funcionando."""
        try:
            # TODO: Implementar validação real
            # Exemplo para PostgreSQL:
            # cursor = connection.cursor()
            # cursor.execute("SELECT 1")
            # cursor.fetchone()
            # cursor.close()
            # return True
            
            # Por enquanto, simula validação
            return hasattr(connection, 'is_valid') and connection.is_valid
        except Exception as e:
            logger.warning({
                "event": "connection_validation_failed",
                "status": "warning",
                "source": "ConnectionFactory.validate_connection",
                "details": {"error": str(e)}
            })
            return False
    
    def close_connection(self, connection: Any):
        """Fecha uma conexão."""
        try:
            # TODO: Implementar fechamento real
            # connection.close()
            
            # Por enquanto, simula fechamento
            if hasattr(connection, 'close'):
                connection.close()
                
            logger.info({
                "event": "connection_closed",
                "status": "success",
                "source": "ConnectionFactory.close_connection"
            })
            
        except Exception as e:
            logger.error({
                "event": "connection_close_failed",
                "status": "error",
                "source": "ConnectionFactory.close_connection",
                "details": {"error": str(e)}
            })

class MockConnection:
    """Conexão mock para testes."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.is_valid = True
        self.created_at = time.time()
        self.last_used = time.time()
    
    def close(self):
        """Fecha a conexão."""
        self.is_valid = False
    
    def execute(self, query: str):
        """Executa uma query."""
        self.last_used = time.time()
        return f"Mock result for: {query}"

class ConnectionPool:
    """
    Pool de conexões otimizado com funcionalidades enterprise-grade.
    
    Implementa:
    - Connection pooling inteligente
    - Health checks automáticos
    - Connection recycling
    - Pool sizing adaptativo
    - Métricas detalhadas
    """
    
    def __init__(self, connection_config: ConnectionConfig, pool_config: PoolConfig):
        """
        Inicializar pool de conexões.
        
        Args:
            connection_config: Configuração das conexões
            pool_config: Configuração do pool
        """
        self.connection_config = connection_config
        self.pool_config = pool_config
        self.factory = ConnectionFactory(connection_config)
        
        # Pool de conexões
        self.connections: Dict[str, ConnectionInfo] = {}
        self.idle_queue = queue.Queue()
        self.active_connections: set = set()
        
        # Threading
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        
        # Métricas
        self.metrics = PoolMetrics()
        self.acquire_times: deque = deque(maxlen=100)
        self.release_times: deque = deque(maxlen=100)
        self.health_check_times: deque = deque(maxlen=100)
        
        # Background tasks
        self.running = True
        self.health_check_thread = None
        self.metrics_thread = None
        self.recycling_thread = None
        
        # Inicializar pool
        self._initialize_pool()
        self._start_background_tasks()
        
        logger.info({
            "event": "connection_pool_initialized",
            "status": "success",
            "source": "ConnectionPool.__init__",
            "details": {
                "min_size": pool_config.min_size,
                "max_size": pool_config.max_size,
                "initial_size": pool_config.initial_size,
                "strategy": pool_config.strategy.value
            }
        })
    
    def _initialize_pool(self):
        """Inicializa o pool com conexões iniciais."""
        for _ in range(self.pool_config.initial_size):
            try:
                self._create_connection()
            except Exception as e:
                logger.warning({
                    "event": "initial_connection_failed",
                    "status": "warning",
                    "source": "ConnectionPool._initialize_pool",
                    "details": {"error": str(e)}
                })
    
    def _create_connection(self) -> Optional[str]:
        """Cria uma nova conexão no pool."""
        if len(self.connections) >= self.pool_config.max_size:
            return None
        
        try:
            connection_id, connection = self.factory.create_connection()
            
            conn_info = ConnectionInfo(
                id=connection_id,
                state=ConnectionState.IDLE,
                created_at=time.time(),
                last_used=time.time(),
                last_health_check=time.time(),
                usage_count=0,
                error_count=0,
                connection=connection
            )
            
            self.connections[connection_id] = conn_info
            self.idle_queue.put(connection_id)
            self.metrics.total_connections += 1
            self.metrics.total_creates += 1
            self.metrics.idle_connections += 1
            
            logger.debug({
                "event": "connection_added_to_pool",
                "status": "info",
                "source": "ConnectionPool._create_connection",
                "details": {
                    "connection_id": connection_id,
                    "pool_size": len(self.connections)
                }
            })
            
            return connection_id
            
        except Exception as e:
            self.metrics.connection_errors += 1
            logger.error({
                "event": "connection_creation_failed",
                "status": "error",
                "source": "ConnectionPool._create_connection",
                "details": {"error": str(e)}
            })
            return None
    
    def acquire(self, timeout: Optional[int] = None) -> Optional[Any]:
        """
        Adquire uma conexão do pool.
        
        Args:
            timeout: Timeout em segundos
            
        Returns:
            Conexão ou None se timeout
        """
        start_time = time.time()
        timeout = timeout or self.pool_config.acquire_timeout
        
        with self.condition:
            # Tenta obter conexão idle
            connection_id = self._get_idle_connection()
            
            if connection_id:
                connection = self._activate_connection(connection_id)
                self._record_acquire_time(time.time() - start_time)
                return connection
            
            # Se não há conexões idle e pode criar mais
            if len(self.connections) < self.pool_config.max_size:
                connection_id = self._create_connection()
                if connection_id:
                    connection = self._activate_connection(connection_id)
                    self._record_acquire_time(time.time() - start_time)
                    return connection
            
            # Aguarda conexão disponível
            if self.condition.wait(timeout):
                connection_id = self._get_idle_connection()
                if connection_id:
                    connection = self._activate_connection(connection_id)
                    self._record_acquire_time(time.time() - start_time)
                    return connection
        
        # Timeout
        self.metrics.acquire_timeouts += 1
        logger.warning({
            "event": "connection_acquire_timeout",
            "status": "warning",
            "source": "ConnectionPool.acquire",
            "details": {
                "timeout": timeout,
                "pool_size": len(self.connections),
                "active_connections": len(self.active_connections)
            }
        })
        
        return None
    
    def _get_idle_connection(self) -> Optional[str]:
        """Obtém uma conexão idle."""
        try:
            return self.idle_queue.get_nowait()
        except queue.Empty:
            return None
    
    def _activate_connection(self, connection_id: str) -> Any:
        """Ativa uma conexão."""
        conn_info = self.connections[connection_id]
        conn_info.state = ConnectionState.IN_USE
        conn_info.last_used = time.time()
        conn_info.usage_count += 1
        
        self.active_connections.add(connection_id)
        self.metrics.active_connections += 1
        self.metrics.idle_connections -= 1
        self.metrics.total_acquires += 1
        
        return conn_info.connection
    
    def release(self, connection: Any):
        """
        Libera uma conexão de volta ao pool.
        
        Args:
            connection: Conexão a ser liberada
        """
        start_time = time.time()
        
        with self.lock:
            # Encontra a conexão
            connection_id = None
            for conn_id, conn_info in self.connections.items():
                if conn_info.connection == connection:
                    connection_id = conn_id
                    break
            
            if not connection_id:
                logger.warning({
                    "event": "connection_not_found",
                    "status": "warning",
                    "source": "ConnectionPool.release"
                })
                return
            
            conn_info = self.connections[connection_id]
            
            # Verifica se precisa reciclar
            if self._should_recycle_connection(conn_info):
                self._destroy_connection(connection_id)
            else:
                # Retorna ao pool
                conn_info.state = ConnectionState.IDLE
                self.active_connections.discard(connection_id)
                self.idle_queue.put(connection_id)
                self.metrics.active_connections -= 1
                self.metrics.idle_connections += 1
                self.metrics.total_releases += 1
        
        self._record_release_time(time.time() - start_time)
        
        # Notifica threads aguardando
        with self.condition:
            self.condition.notify()
    
    def _should_recycle_connection(self, conn_info: ConnectionInfo) -> bool:
        """Verifica se uma conexão deve ser reciclada."""
        now = time.time()
        
        # Verifica tempo de vida
        if now - conn_info.created_at > self.pool_config.max_lifetime:
            return True
        
        # Verifica tempo idle
        if now - conn_info.last_used > self.pool_config.max_idle_time:
            return True
        
        # Verifica número de erros
        if conn_info.error_count > 3:
            return True
        
        # Verifica se está quebrada
        if conn_info.state == ConnectionState.BROKEN:
            return True
        
        return False
    
    def _destroy_connection(self, connection_id: str):
        """Destrói uma conexão."""
        conn_info = self.connections[connection_id]
        
        try:
            self.factory.close_connection(conn_info.connection)
        except Exception as e:
            logger.error({
                "event": "connection_close_failed",
                "status": "error",
                "source": "ConnectionPool._destroy_connection",
                "details": {
                    "connection_id": connection_id,
                    "error": str(e)
                }
            })
        
        # Remove do pool
        self.connections.pop(connection_id, None)
        self.active_connections.discard(connection_id)
        
        self.metrics.total_connections -= 1
        self.metrics.total_destroys += 1
        
        if conn_info.state == ConnectionState.IN_USE:
            self.metrics.active_connections -= 1
        else:
            self.metrics.idle_connections -= 1
    
    def _start_background_tasks(self):
        """Inicia tarefas em background."""
        self.health_check_thread = threading.Thread(
            target=self._health_check_worker,
            daemon=True
        )
        self.health_check_thread.start()
        
        self.metrics_thread = threading.Thread(
            target=self._metrics_worker,
            daemon=True
        )
        self.metrics_thread.start()
        
        self.recycling_thread = threading.Thread(
            target=self._recycling_worker,
            daemon=True
        )
        self.recycling_thread.start()
    
    def _health_check_worker(self):
        """Worker para health checks."""
        while self.running:
            try:
                time.sleep(self.pool_config.health_check_interval)
                self._perform_health_checks()
            except Exception as e:
                logger.error({
                    "event": "health_check_worker_error",
                    "status": "error",
                    "source": "ConnectionPool._health_check_worker",
                    "details": {"error": str(e)}
                })
    
    def _perform_health_checks(self):
        """Executa health checks em todas as conexões."""
        start_time = time.time()
        
        with self.lock:
            for connection_id, conn_info in list(self.connections.items()):
                if conn_info.state == ConnectionState.IDLE:
                    try:
                        is_healthy = self.factory.validate_connection(conn_info.connection)
                        if not is_healthy:
                            conn_info.state = ConnectionState.BROKEN
                            self.metrics.health_check_failures += 1
                            logger.warning({
                                "event": "connection_health_check_failed",
                                "status": "warning",
                                "source": "ConnectionPool._perform_health_checks",
                                "details": {"connection_id": connection_id}
                            })
                        else:
                            conn_info.last_health_check = time.time()
                    except Exception as e:
                        conn_info.state = ConnectionState.BROKEN
                        self.metrics.health_check_failures += 1
                        logger.error({
                            "event": "health_check_exception",
                            "status": "error",
                            "source": "ConnectionPool._perform_health_checks",
                            "details": {
                                "connection_id": connection_id,
                                "error": str(e)
                            }
                        })
        
        health_check_time = time.time() - start_time
        self.health_check_times.append(health_check_time)
    
    def _metrics_worker(self):
        """Worker para atualização de métricas."""
        while self.running:
            try:
                time.sleep(10)  # Atualiza a cada 10 segundos
                self._update_metrics()
            except Exception as e:
                logger.error({
                    "event": "metrics_worker_error",
                    "status": "error",
                    "source": "ConnectionPool._metrics_worker",
                    "details": {"error": str(e)}
                })
    
    def _update_metrics(self):
        """Atualiza métricas do pool."""
        total = len(self.connections)
        active = len(self.active_connections)
        
        if total > 0:
            self.metrics.pool_utilization = active / total
            self.metrics.connection_efficiency = self.metrics.total_acquires / max(total, 1)
        
        if self.acquire_times:
            self.metrics.avg_acquire_time = statistics.mean(self.acquire_times)
        
        if self.release_times:
            self.metrics.avg_release_time = statistics.mean(self.release_times)
        
        if self.health_check_times:
            self.metrics.avg_health_check_time = statistics.mean(self.health_check_times)
    
    def _recycling_worker(self):
        """Worker para recycling de conexões."""
        while self.running:
            try:
                time.sleep(30)  # Verifica a cada 30 segundos
                self._recycle_expired_connections()
            except Exception as e:
                logger.error({
                    "event": "recycling_worker_error",
                    "status": "error",
                    "source": "ConnectionPool._recycling_worker",
                    "details": {"error": str(e)}
                })
    
    def _recycle_expired_connections(self):
        """Recicla conexões expiradas."""
        with self.lock:
            for connection_id, conn_info in list(self.connections.items()):
                if self._should_recycle_connection(conn_info):
                    self._destroy_connection(connection_id)
    
    def _record_acquire_time(self, duration: float):
        """Registra tempo de aquisição."""
        self.acquire_times.append(duration)
    
    def _record_release_time(self, duration: float):
        """Registra tempo de liberação."""
        self.release_times.append(duration)
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Obtém status do pool."""
        return {
            "total_connections": len(self.connections),
            "active_connections": len(self.active_connections),
            "idle_connections": self.metrics.idle_connections,
            "broken_connections": self.metrics.broken_connections,
            "pool_utilization": self.metrics.pool_utilization,
            "connection_efficiency": self.metrics.connection_efficiency,
            "avg_acquire_time": self.metrics.avg_acquire_time,
            "avg_release_time": self.metrics.avg_release_time,
            "health_check_failures": self.metrics.health_check_failures,
            "acquire_timeouts": self.metrics.acquire_timeouts
        }
    
    def get_detailed_metrics(self) -> PoolMetrics:
        """Obtém métricas detalhadas."""
        return self.metrics
    
    def resize_pool(self, min_size: int, max_size: int):
        """Redimensiona o pool."""
        with self.lock:
            old_min = self.pool_config.min_size
            old_max = self.pool_config.max_size
            
            self.pool_config.min_size = min_size
            self.pool_config.max_size = max_size
            
            # Ajusta pool se necessário
            while len(self.connections) < min_size:
                self._create_connection()
            
            logger.info({
                "event": "pool_resized",
                "status": "info",
                "source": "ConnectionPool.resize_pool",
                "details": {
                    "old_min": old_min,
                    "old_max": old_max,
                    "new_min": min_size,
                    "new_max": max_size,
                    "current_size": len(self.connections)
                }
            })
    
    def health_check(self) -> Dict[str, Any]:
        """Health check do pool."""
        return {
            "status": "healthy" if self.running else "unhealthy",
            "pool_size": len(self.connections),
            "active_connections": len(self.active_connections),
            "utilization": self.metrics.pool_utilization,
            "last_health_check": time.time(),
            "background_threads": {
                "health_check": self.health_check_thread.is_alive() if self.health_check_thread else False,
                "metrics": self.metrics_thread.is_alive() if self.metrics_thread else False,
                "recycling": self.recycling_thread.is_alive() if self.recycling_thread else False
            }
        }
    
    def close(self):
        """Fecha o pool e todas as conexões."""
        self.running = False
        
        with self.lock:
            # Fecha todas as conexões
            for connection_id in list(self.connections.keys()):
                self._destroy_connection(connection_id)
        
        logger.info({
            "event": "connection_pool_closed",
            "status": "info",
            "source": "ConnectionPool.close",
            "details": {
                "total_connections_closed": self.metrics.total_connections
            }
        })

@contextmanager
def get_connection(pool: ConnectionPool, timeout: Optional[int] = None):
    """
    Context manager para obter conexão do pool.
    
    Args:
        pool: Pool de conexões
        timeout: Timeout para aquisição
        
    Yields:
        Conexão do pool
    """
    connection = None
    try:
        connection = pool.acquire(timeout)
        if connection is None:
            raise Exception("Failed to acquire connection from pool")
        yield connection
    finally:
        if connection:
            pool.release(connection)

def create_connection_pool(
    connection_config: ConnectionConfig,
    pool_config: PoolConfig
) -> ConnectionPool:
    """
    Cria e retorna um pool de conexões.
    
    Args:
        connection_config: Configuração das conexões
        pool_config: Configuração do pool
        
    Returns:
        Pool de conexões configurado
    """
    return ConnectionPool(connection_config, pool_config)

# Configurações padrão
DEFAULT_CONNECTION_CONFIG = ConnectionConfig()
DEFAULT_POOL_CONFIG = PoolConfig()

# Pool global (singleton)
_global_pool: Optional[ConnectionPool] = None

def get_global_pool() -> ConnectionPool:
    """Obtém o pool global."""
    global _global_pool
    if _global_pool is None:
        _global_pool = create_connection_pool(DEFAULT_CONNECTION_CONFIG, DEFAULT_POOL_CONFIG)
    return _global_pool

def set_global_pool(pool: ConnectionPool):
    """Define o pool global."""
    global _global_pool
    _global_pool = pool 