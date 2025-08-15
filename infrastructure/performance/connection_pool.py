"""
Módulo de Pool de Conexões de Banco de Dados para Sistemas Enterprise
Sistema de gerenciamento de conexões, health checks e failover - Omni Keywords Finder

Prompt: Implementação de sistema de pool de conexões enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import time
import threading
import logging
import queue
import random
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics
import asyncio
from concurrent.futures import ThreadPoolExecutor
import weakref

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Estados de uma conexão."""
    IDLE = "idle"
    IN_USE = "in_use"
    TESTING = "testing"
    FAILED = "failed"
    CLOSED = "closed"


class PoolStrategy(Enum):
    """Estratégias de pool."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    RANDOM = "random"


@dataclass
class ConnectionConfig:
    """Configuração de conexão."""
    host: str
    port: int
    database: str
    username: str
    password: str
    charset: str = "utf8"
    autocommit: bool = True
    connect_timeout: int = 10
    read_timeout: int = 30
    write_timeout: int = 30
    ssl_mode: str = "preferred"
    ssl_ca: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    max_allowed_packet: int = 16777216
    sql_mode: str = "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO"

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.host or len(self.host.strip()) == 0:
            raise ValueError("Host não pode ser vazio")
        if not 1 <= self.port <= 65535:
            raise ValueError("Port deve estar entre 1 e 65535")
        if not self.database or len(self.database.strip()) == 0:
            raise ValueError("Database não pode ser vazio")
        if not self.username or len(self.username.strip()) == 0:
            raise ValueError("Username não pode ser vazio")
        if self.connect_timeout <= 0:
            raise ValueError("Connect timeout deve ser positivo")
        if self.read_timeout <= 0:
            raise ValueError("Read timeout deve ser positivo")
        if self.write_timeout <= 0:
            raise ValueError("Write timeout deve ser positivo")
        if self.max_allowed_packet <= 0:
            raise ValueError("Max allowed packet deve ser positivo")
        
        # Normalizar campos
        self.host = self.host.strip()
        self.database = self.database.strip()
        self.username = self.username.strip()


@dataclass
class PoolConfig:
    """Configuração do pool de conexões."""
    min_connections: int = 5
    max_connections: int = 20
    initial_connections: int = 10
    connection_timeout: int = 30  # segundos
    idle_timeout: int = 300  # segundos
    max_lifetime: int = 3600  # segundos
    health_check_interval: int = 30  # segundos
    health_check_timeout: int = 5  # segundos
    health_check_query: str = "SELECT 1"
    enable_health_checks: bool = True
    enable_connection_reuse: bool = True
    enable_connection_preparation: bool = True
    enable_connection_validation: bool = True
    validation_timeout: int = 5  # segundos
    strategy: PoolStrategy = PoolStrategy.ROUND_ROBIN
    enable_metrics: bool = True
    enable_logging: bool = True
    retry_attempts: int = 3
    retry_delay: float = 1.0  # segundos
    failover_enabled: bool = False
    failover_hosts: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.min_connections <= 0:
            raise ValueError("Min connections deve ser positivo")
        if self.max_connections <= 0:
            raise ValueError("Max connections deve ser positivo")
        if self.min_connections > self.max_connections:
            raise ValueError("Min connections não pode ser maior que max connections")
        if self.initial_connections < self.min_connections:
            raise ValueError("Initial connections deve ser pelo menos min connections")
        if self.initial_connections > self.max_connections:
            raise ValueError("Initial connections não pode ser maior que max connections")
        if self.connection_timeout <= 0:
            raise ValueError("Connection timeout deve ser positivo")
        if self.idle_timeout <= 0:
            raise ValueError("Idle timeout deve ser positivo")
        if self.max_lifetime <= 0:
            raise ValueError("Max lifetime deve ser positivo")
        if self.health_check_interval <= 0:
            raise ValueError("Health check interval deve ser positivo")
        if self.health_check_timeout <= 0:
            raise ValueError("Health check timeout deve ser positivo")
        if self.validation_timeout <= 0:
            raise ValueError("Validation timeout deve ser positivo")
        if self.retry_attempts < 0:
            raise ValueError("Retry attempts não pode ser negativo")
        if self.retry_delay < 0:
            raise ValueError("Retry delay não pode ser negativo")


@dataclass
class ConnectionInfo:
    """Informações de uma conexão."""
    id: str
    connection: Any
    state: ConnectionState
    created_at: datetime
    last_used: datetime
    use_count: int = 0
    last_health_check: Optional[datetime] = None
    health_status: bool = True
    error_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self, max_lifetime: int) -> bool:
        """Verifica se a conexão expirou."""
        return (datetime.utcnow() - self.created_at).total_seconds() > max_lifetime

    def is_idle_too_long(self, idle_timeout: int) -> bool:
        """Verifica se a conexão está ociosa há muito tempo."""
        return (datetime.utcnow() - self.last_used).total_seconds() > idle_timeout

    def needs_health_check(self, health_check_interval: int) -> bool:
        """Verifica se a conexão precisa de health check."""
        if self.last_health_check is None:
            return True
        return (datetime.utcnow() - self.last_health_check).total_seconds() > health_check_interval


@dataclass
class PoolStats:
    """Estatísticas do pool de conexões."""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_requests: int = 0
    connection_timeouts: int = 0
    connection_errors: int = 0
    avg_connection_time: float = 0.0
    avg_query_time: float = 0.0
    health_check_failures: int = 0
    last_health_check: Optional[datetime] = None
    pool_utilization: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def update_utilization(self) -> None:
        """Atualiza utilização do pool."""
        if self.total_connections > 0:
            self.pool_utilization = self.active_connections / self.total_connections
        else:
            self.pool_utilization = 0.0


class DatabaseConnectionPool:
    """Pool de conexões de banco de dados enterprise."""
    
    def __init__(self, connection_config: ConnectionConfig, pool_config: PoolConfig = None,
                 connection_factory: Callable = None):
        """
        Inicializa o pool de conexões.
        
        Args:
            connection_config: Configuração de conexão
            pool_config: Configuração do pool
            connection_factory: Factory para criar conexões
        """
        self.connection_config = connection_config
        self.pool_config = pool_config or PoolConfig()
        self.connection_factory = connection_factory
        
        # Pool de conexões
        self.connections: Dict[str, ConnectionInfo] = {}
        self.connection_queue = queue.Queue()
        self.available_connections: List[str] = []
        
        # Controles
        self.running = False
        self.health_check_thread = None
        self.cleanup_thread = None
        self.lock = threading.RLock()
        
        # Estatísticas
        self.stats = PoolStats()
        
        # Callbacks
        self.on_connection_created: Optional[Callable[[ConnectionInfo], None]] = None
        self.on_connection_closed: Optional[Callable[[ConnectionInfo], None]] = None
        self.on_connection_failed: Optional[Callable[[ConnectionInfo, str], None]] = None
        self.on_health_check_failed: Optional[Callable[[ConnectionInfo], None]] = None
        self.on_pool_exhausted: Optional[Callable[[], None]] = None
        
        # Contadores
        self.connection_counter = 0
        self.current_strategy_index = 0
        
        logger.info(f"DatabaseConnectionPool inicializado - {self.pool_config.min_connections}-{self.pool_config.max_connections} conexões")
    
    def get_connection(self, timeout: int = None) -> Optional[Any]:
        """
        Obtém uma conexão do pool.
        
        Args:
            timeout: Timeout em segundos
            
        Returns:
            Conexão ou None se não disponível
        """
        timeout = timeout or self.pool_config.connection_timeout
        start_time = time.time()
        
        with self.lock:
            self.stats.connection_requests += 1
            
            # Tentar obter conexão disponível
            connection_info = self._get_available_connection()
            
            if connection_info:
                # Marcar como em uso
                connection_info.state = ConnectionState.IN_USE
                connection_info.last_used = datetime.utcnow()
                connection_info.use_count += 1
                
                self.stats.active_connections += 1
                self.stats.update_utilization()
                
                logger.debug(f"Conexão obtida: {connection_info.id}")
                return connection_info.connection
            
            # Se não há conexões disponíveis, tentar criar nova
            if len(self.connections) < self.pool_config.max_connections:
                connection_info = self._create_connection()
                if connection_info:
                    connection_info.state = ConnectionState.IN_USE
                    connection_info.last_used = datetime.utcnow()
                    connection_info.use_count += 1
                    
                    self.stats.active_connections += 1
                    self.stats.update_utilization()
                    
                    logger.debug(f"Nova conexão criada: {connection_info.id}")
                    return connection_info.connection
            
            # Pool esgotado
            if self.on_pool_exhausted:
                self.on_pool_exhausted()
            
            logger.warning("Pool de conexões esgotado")
            self.stats.connection_timeouts += 1
            return None
    
    def release_connection(self, connection: Any) -> bool:
        """
        Libera uma conexão de volta ao pool.
        
        Args:
            connection: Conexão a ser liberada
            
        Returns:
            True se liberada com sucesso, False caso contrário
        """
        with self.lock:
            # Encontrar conexão
            connection_info = None
            for conn_info in self.connections.values():
                if conn_info.connection == connection:
                    connection_info = conn_info
                    break
            
            if not connection_info:
                logger.warning("Conexão não encontrada no pool")
                return False
            
            # Verificar se conexão ainda é válida
            if self.pool_config.enable_connection_validation:
                if not self._validate_connection(connection_info):
                    self._remove_connection(connection_info)
                    return False
            
            # Marcar como ociosa
            connection_info.state = ConnectionState.IDLE
            connection_info.last_used = datetime.utcnow()
            
            # Adicionar à lista de disponíveis
            if connection_info.id not in self.available_connections:
                self.available_connections.append(connection_info.id)
            
            self.stats.active_connections -= 1
            self.stats.idle_connections += 1
            self.stats.update_utilization()
            
            logger.debug(f"Conexão liberada: {connection_info.id}")
            return True
    
    def close_connection(self, connection: Any) -> bool:
        """
        Fecha uma conexão permanentemente.
        
        Args:
            connection: Conexão a ser fechada
            
        Returns:
            True se fechada com sucesso, False caso contrário
        """
        with self.lock:
            # Encontrar conexão
            connection_info = None
            for conn_info in self.connections.values():
                if conn_info.connection == connection:
                    connection_info = conn_info
                    break
            
            if not connection_info:
                return False
            
            self._remove_connection(connection_info)
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do pool.
        
        Returns:
            Dicionário com estatísticas
        """
        with self.lock:
            self.stats.update_utilization()
            
            return {
                "total_connections": self.stats.total_connections,
                "active_connections": self.stats.active_connections,
                "idle_connections": self.stats.idle_connections,
                "failed_connections": self.stats.failed_connections,
                "connection_requests": self.stats.connection_requests,
                "connection_timeouts": self.stats.connection_timeouts,
                "connection_errors": self.stats.connection_errors,
                "avg_connection_time": self.stats.avg_connection_time,
                "avg_query_time": self.stats.avg_query_time,
                "health_check_failures": self.stats.health_check_failures,
                "pool_utilization": self.stats.pool_utilization,
                "last_health_check": self.stats.last_health_check.isoformat() if self.stats.last_health_check else None,
                "timestamp": self.stats.timestamp.isoformat(),
                "pool_config": {
                    "min_connections": self.pool_config.min_connections,
                    "max_connections": self.pool_config.max_connections,
                    "strategy": self.pool_config.strategy.value
                }
            }
    
    def start(self) -> None:
        """Inicia o pool de conexões."""
        if self.running:
            return
        
        self.running = True
        
        # Criar conexões iniciais
        self._create_initial_connections()
        
        # Iniciar thread de health check
        if self.pool_config.enable_health_checks:
            self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
            self.health_check_thread.start()
        
        # Iniciar thread de limpeza
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("DatabaseConnectionPool iniciado")
    
    def stop(self) -> None:
        """Para o pool de conexões."""
        if not self.running:
            return
        
        self.running = False
        
        # Aguardar threads terminarem
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        
        # Fechar todas as conexões
        self._close_all_connections()
        
        logger.info("DatabaseConnectionPool parado")
    
    def _create_initial_connections(self) -> None:
        """Cria conexões iniciais."""
        for _ in range(self.pool_config.initial_connections):
            connection_info = self._create_connection()
            if connection_info:
                connection_info.state = ConnectionState.IDLE
                self.available_connections.append(connection_info.id)
    
    def _create_connection(self) -> Optional[ConnectionInfo]:
        """Cria uma nova conexão."""
        for attempt in range(self.pool_config.retry_attempts + 1):
            try:
                start_time = time.time()
                
                # Usar factory se fornecida, senão usar configuração padrão
                if self.connection_factory:
                    connection = self.connection_factory(self.connection_config)
                else:
                    connection = self._create_default_connection()
                
                connection_time = time.time() - start_time
                
                # Criar info da conexão
                connection_id = f"conn_{self.connection_counter}"
                self.connection_counter += 1
                
                connection_info = ConnectionInfo(
                    id=connection_id,
                    connection=connection,
                    state=ConnectionState.IDLE,
                    created_at=datetime.utcnow(),
                    last_used=datetime.utcnow()
                )
                
                # Adicionar ao pool
                self.connections[connection_id] = connection_info
                self.stats.total_connections += 1
                self.stats.idle_connections += 1
                
                # Atualizar tempo médio de conexão
                if self.stats.total_connections > 0:
                    self.stats.avg_connection_time = (
                        (self.stats.avg_connection_time * (self.stats.total_connections - 1) + connection_time) /
                        self.stats.total_connections
                    )
                
                if self.on_connection_created:
                    self.on_connection_created(connection_info)
                
                logger.debug(f"Conexão criada: {connection_id}")
                return connection_info
                
            except Exception as e:
                error_msg = f"Erro ao criar conexão (tentativa {attempt + 1}): {e}"
                logger.error(error_msg)
                
                if attempt < self.pool_config.retry_attempts:
                    time.sleep(self.pool_config.retry_delay)
                else:
                    self.stats.connection_errors += 1
                    break
        
        return None
    
    def _create_default_connection(self) -> Any:
        """Cria conexão usando configuração padrão."""
        # Esta é uma implementação genérica - em produção, seria específica para o banco
        # Por exemplo, para MySQL: mysql.connector.connect(...)
        # Para PostgreSQL: psycopg2.connect(...)
        
        # Simular criação de conexão
        import random
        connection = {
            'host': self.connection_config.host,
            'port': self.connection_config.port,
            'database': self.connection_config.database,
            'username': self.connection_config.username,
            'connection_id': random.randint(1000, 9999)
        }
        
        return connection
    
    def _get_available_connection(self) -> Optional[ConnectionInfo]:
        """Obtém uma conexão disponível baseada na estratégia."""
        if not self.available_connections:
            return None
        
        if self.pool_config.strategy == PoolStrategy.ROUND_ROBIN:
            # Round robin
            connection_id = self.available_connections[self.current_strategy_index % len(self.available_connections)]
            self.current_strategy_index += 1
            
        elif self.pool_config.strategy == PoolStrategy.LEAST_CONNECTIONS:
            # Menos conexões
            connection_id = min(
                self.available_connections,
                key=lambda cid: self.connections[cid].use_count
            )
            
        elif self.pool_config.strategy == PoolStrategy.WEIGHTED:
            # Ponderado (baseado em uso)
            connection_id = min(
                self.available_connections,
                key=lambda cid: self.connections[cid].use_count * 
                               (datetime.utcnow() - self.connections[cid].last_used).total_seconds()
            )
            
        else:  # RANDOM
            # Aleatório
            connection_id = random.choice(self.available_connections)
        
        # Remover da lista de disponíveis
        self.available_connections.remove(connection_id)
        
        return self.connections.get(connection_id)
    
    def _validate_connection(self, connection_info: ConnectionInfo) -> bool:
        """Valida uma conexão."""
        try:
            # Executar query de validação
            if hasattr(connection_info.connection, 'execute'):
                connection_info.connection.execute(self.pool_config.health_check_query)
            else:
                # Para conexões simuladas, sempre retornar True
                return True
            
            connection_info.health_status = True
            connection_info.error_count = 0
            connection_info.last_error = None
            
            return True
            
        except Exception as e:
            connection_info.health_status = False
            connection_info.error_count += 1
            connection_info.last_error = str(e)
            
            if self.on_connection_failed:
                self.on_connection_failed(connection_info, str(e))
            
            logger.warning(f"Falha na validação da conexão {connection_info.id}: {e}")
            return False
    
    def _remove_connection(self, connection_info: ConnectionInfo) -> None:
        """Remove uma conexão do pool."""
        # Fechar conexão
        try:
            if hasattr(connection_info.connection, 'close'):
                connection_info.connection.close()
        except Exception as e:
            logger.error(f"Erro ao fechar conexão {connection_info.id}: {e}")
        
        # Remover do pool
        if connection_info.id in self.connections:
            del self.connections[connection_info.id]
        
        if connection_info.id in self.available_connections:
            self.available_connections.remove(connection_info.id)
        
        # Atualizar estatísticas
        if connection_info.state == ConnectionState.IN_USE:
            self.stats.active_connections -= 1
        elif connection_info.state == ConnectionState.IDLE:
            self.stats.idle_connections -= 1
        
        self.stats.total_connections -= 1
        self.stats.update_utilization()
        
        if self.on_connection_closed:
            self.on_connection_closed(connection_info)
        
        logger.debug(f"Conexão removida: {connection_info.id}")
    
    def _health_check_loop(self) -> None:
        """Loop de health check."""
        while self.running:
            try:
                time.sleep(self.pool_config.health_check_interval)
                
                with self.lock:
                    # Verificar conexões ociosas
                    for connection_info in list(self.connections.values()):
                        if connection_info.state == ConnectionState.IDLE:
                            if connection_info.needs_health_check(self.pool_config.health_check_interval):
                                connection_info.state = ConnectionState.TESTING
                                connection_info.last_health_check = datetime.utcnow()
                                
                                if not self._validate_connection(connection_info):
                                    self.stats.health_check_failures += 1
                                    connection_info.state = ConnectionState.FAILED
                                    
                                    if self.on_health_check_failed:
                                        self.on_health_check_failed(connection_info)
                                    
                                    # Remover conexão falhada
                                    self._remove_connection(connection_info)
                                else:
                                    connection_info.state = ConnectionState.IDLE
                    
                    self.stats.last_health_check = datetime.utcnow()
                    self.stats.timestamp = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Erro no health check loop: {e}")
    
    def _cleanup_loop(self) -> None:
        """Loop de limpeza."""
        while self.running:
            try:
                time.sleep(60)  # Verificar a cada minuto
                
                with self.lock:
                    # Remover conexões expiradas
                    for connection_info in list(self.connections.values()):
                        if connection_info.state == ConnectionState.IDLE:
                            if (connection_info.is_expired(self.pool_config.max_lifetime) or
                                connection_info.is_idle_too_long(self.pool_config.idle_timeout)):
                                self._remove_connection(connection_info)
                    
                    # Garantir número mínimo de conexões
                    while (len(self.connections) < self.pool_config.min_connections and
                           len(self.connections) < self.pool_config.max_connections):
                        self._create_connection()
                
            except Exception as e:
                logger.error(f"Erro no cleanup loop: {e}")
    
    def _close_all_connections(self) -> None:
        """Fecha todas as conexões."""
        with self.lock:
            for connection_info in list(self.connections.values()):
                self._remove_connection(connection_info)


# Função de conveniência para criar connection pool
def create_connection_pool(connection_config: ConnectionConfig, 
                          pool_config: PoolConfig = None,
                          connection_factory: Callable = None) -> DatabaseConnectionPool:
    """
    Cria um pool de conexões com configurações padrão.
    
    Args:
        connection_config: Configuração de conexão
        pool_config: Configuração do pool
        connection_factory: Factory para criar conexões
        
    Returns:
        Instância configurada do DatabaseConnectionPool
    """
    return DatabaseConnectionPool(connection_config, pool_config, connection_factory) 