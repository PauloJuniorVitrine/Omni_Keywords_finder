"""
Sistema de Pool de Conexões
Otimiza gerenciamento de conexões com banco de dados
"""

import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager, contextmanager
import weakref

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError

logger = logging.getLogger(__name__)


class PoolType(Enum):
    QUEUE = "queue"
    STATIC = "static"
    NULL = "null"


class ConnectionState(Enum):
    IDLE = "idle"
    IN_USE = "in_use"
    CHECKING_OUT = "checking_out"
    CHECKING_IN = "checking_in"
    INVALID = "invalid"


@dataclass
class ConnectionInfo:
    id: str
    state: ConnectionState
    created_at: datetime
    last_used: datetime
    checkouts: int
    checkins: int
    errors: int
    is_valid: bool = True


@dataclass
class PoolMetrics:
    total_connections: int
    active_connections: int
    idle_connections: int
    max_connections: int
    min_connections: int
    checkouts: int
    checkins: int
    errors: int
    wait_time: float
    avg_checkout_time: float
    avg_checkin_time: float
    connection_creation_time: float
    connection_cleanup_time: float


@dataclass
class PoolConfig:
    pool_type: PoolType = PoolType.QUEUE
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo: bool = False
    echo_pool: bool = False
    reset_on_return: str = 'rollback'
    enable_metrics: bool = True
    health_check_interval: int = 300  # 5 minutos
    connection_timeout: int = 10
    max_lifetime: int = 7200  # 2 horas


class ConnectionPool:
    """
    Pool de conexões com monitoramento e métricas
    """
    
    def __init__(self, database_url: str, config: Optional[PoolConfig] = None):
        self.database_url = database_url
        self.config = config or PoolConfig()
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        
        # Métricas e monitoramento
        self.metrics = PoolMetrics(
            total_connections=0,
            active_connections=0,
            idle_connections=0,
            max_connections=self.config.pool_size + self.config.max_overflow,
            min_connections=0,
            checkouts=0,
            checkins=0,
            errors=0,
            wait_time=0.0,
            avg_checkout_time=0.0,
            avg_checkin_time=0.0,
            connection_creation_time=0.0,
            connection_cleanup_time=0.0
        )
        
        # Rastreamento de conexões
        self.connections: Dict[str, ConnectionInfo] = {}
        self.connection_lock = threading.Lock()
        
        # Health check
        self.health_check_task = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa pool de conexões"""
        try:
            # Configurar pool baseado no tipo
            pool_kwargs = self._get_pool_kwargs()
            
            # Engine síncrono
            self.engine = create_engine(
                self.database_url,
                **pool_kwargs,
                echo=self.config.echo,
                echo_pool=self.config.echo_pool
            )
            
            # Engine assíncrono (se suportado)
            if self.database_url.startswith(('postgresql+asyncpg', 'mysql+asyncmy')):
                self.async_engine = create_async_engine(
                    self.database_url,
                    **pool_kwargs,
                    echo=self.config.echo,
                    echo_pool=self.config.echo_pool
                )
            
            # Session factories
            self.session_factory = sessionmaker(bind=self.engine)
            if self.async_engine:
                self.async_session_factory = sessionmaker(
                    bind=self.async_engine,
                    class_=AsyncSession
                )
            
            # Configurar eventos
            self._setup_engine_events()
            
            # Iniciar health check
            if self.config.enable_metrics:
                self._start_health_check()
            
            logger.info(f"Pool de conexões inicializado: {self.config.pool_type.value}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar pool: {e}")
            raise
    
    def _get_pool_kwargs(self) -> Dict[str, Any]:
        """Obtém argumentos do pool baseado no tipo"""
        if self.config.pool_type == PoolType.QUEUE:
            return {
                'poolclass': QueuePool,
                'pool_size': self.config.pool_size,
                'max_overflow': self.config.max_overflow,
                'pool_timeout': self.config.pool_timeout,
                'pool_recycle': self.config.pool_recycle,
                'pool_pre_ping': self.config.pool_pre_ping,
                'reset_on_return': self.config.reset_on_return
            }
        elif self.config.pool_type == PoolType.STATIC:
            return {
                'poolclass': StaticPool,
                'pool_size': self.config.pool_size
            }
        elif self.config.pool_type == PoolType.NULL:
            return {
                'poolclass': NullPool
            }
        else:
            return {
                'poolclass': QueuePool,
                'pool_size': self.config.pool_size,
                'max_overflow': self.config.max_overflow
            }
    
    def _setup_engine_events(self):
        """Configura eventos do engine para monitoramento"""
        if not self.engine:
            return
        
        @event.listens_for(self.engine, 'checkout')
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            self._on_connection_checkout(connection_record)
        
        @event.listens_for(self.engine, 'checkin')
        def receive_checkin(dbapi_connection, connection_record):
            self._on_connection_checkin(connection_record)
        
        @event.listens_for(self.engine, 'connect')
        def receive_connect(dbapi_connection, connection_record):
            self._on_connection_created(connection_record)
        
        @event.listens_for(self.engine, 'close')
        def receive_close(dbapi_connection):
            self._on_connection_closed()
        
        @event.listens_for(self.engine, 'reset')
        def receive_reset(dbapi_connection, connection_record):
            self._on_connection_reset(connection_record)
    
    def _on_connection_checkout(self, connection_record):
        """Evento de checkout de conexão"""
        start_time = time.time()
        connection_id = str(id(connection_record))
        
        with self.connection_lock:
            if connection_id not in self.connections:
                self.connections[connection_id] = ConnectionInfo(
                    id=connection_id,
                    state=ConnectionState.CHECKING_OUT,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                    checkouts=0,
                    checkins=0,
                    errors=0
                )
            
            conn_info = self.connections[connection_id]
            conn_info.state = ConnectionState.IN_USE
            conn_info.last_used = datetime.now()
            conn_info.checkouts += 1
            
            self.metrics.checkouts += 1
            self.metrics.active_connections += 1
            self.metrics.idle_connections = max(0, self.metrics.idle_connections - 1)
        
        # Calcular tempo de checkout
        checkout_time = time.time() - start_time
        self.metrics.avg_checkout_time = (
            (self.metrics.avg_checkout_time * (self.metrics.checkouts - 1) + checkout_time) 
            / self.metrics.checkouts
        )
        
        logger.debug(f"Connection checkout: {connection_id}")
    
    def _on_connection_checkin(self, connection_record):
        """Evento de checkin de conexão"""
        start_time = time.time()
        connection_id = str(id(connection_record))
        
        with self.connection_lock:
            if connection_id in self.connections:
                conn_info = self.connections[connection_id]
                conn_info.state = ConnectionState.IDLE
                conn_info.checkins += 1
                
                self.metrics.checkins += 1
                self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
                self.metrics.idle_connections += 1
        
        # Calcular tempo de checkin
        checkin_time = time.time() - start_time
        self.metrics.avg_checkin_time = (
            (self.metrics.avg_checkin_time * (self.metrics.checkins - 1) + checkin_time) 
            / self.metrics.checkins
        )
        
        logger.debug(f"Connection checkin: {connection_id}")
    
    def _on_connection_created(self, connection_record):
        """Evento de criação de conexão"""
        connection_id = str(id(connection_record))
        start_time = time.time()
        
        with self.connection_lock:
            self.connections[connection_id] = ConnectionInfo(
                id=connection_id,
                state=ConnectionState.IDLE,
                created_at=datetime.now(),
                last_used=datetime.now(),
                checkouts=0,
                checkins=0,
                errors=0
            )
            
            self.metrics.total_connections += 1
            self.metrics.idle_connections += 1
        
        creation_time = time.time() - start_time
        self.metrics.connection_creation_time = (
            (self.metrics.connection_creation_time * (self.metrics.total_connections - 1) + creation_time) 
            / self.metrics.total_connections
        )
        
        logger.debug(f"Connection created: {connection_id}")
    
    def _on_connection_closed(self):
        """Evento de fechamento de conexão"""
        with self.connection_lock:
            self.metrics.total_connections = max(0, self.metrics.total_connections - 1)
            self.metrics.idle_connections = max(0, self.metrics.idle_connections - 1)
        
        logger.debug("Connection closed")
    
    def _on_connection_reset(self, connection_record):
        """Evento de reset de conexão"""
        connection_id = str(id(connection_record))
        
        with self.connection_lock:
            if connection_id in self.connections:
                conn_info = self.connections[connection_id]
                conn_info.state = ConnectionState.IDLE
                conn_info.last_used = datetime.now()
        
        logger.debug(f"Connection reset: {connection_id}")
    
    def _start_health_check(self):
        """Inicia verificação de saúde do pool"""
        if self.health_check_task:
            return
        
        async def health_check_loop():
            while True:
                try:
                    await self._perform_health_check()
                    await asyncio.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Erro no health check: {e}")
                    await asyncio.sleep(60)  # Esperar 1 minuto antes de tentar novamente
        
        self.health_check_task = asyncio.create_task(health_check_loop())
    
    async def _perform_health_check(self):
        """Executa verificação de saúde do pool"""
        try:
            # Verificar conexões inativas
            current_time = datetime.now()
            max_lifetime = timedelta(seconds=self.config.max_lifetime)
            
            with self.connection_lock:
                for conn_id, conn_info in list(self.connections.items()):
                    # Verificar se conexão expirou
                    if current_time - conn_info.created_at > max_lifetime:
                        conn_info.is_valid = False
                        logger.warning(f"Connection {conn_id} expired")
                    
                    # Verificar conexões com muitos erros
                    if conn_info.errors > 5:
                        conn_info.is_valid = False
                        logger.warning(f"Connection {conn_id} has too many errors")
            
            # Limpar conexões inválidas
            await self._cleanup_invalid_connections()
            
            # Verificar pool status
            await self._check_pool_status()
            
        except Exception as e:
            logger.error(f"Erro no health check: {e}")
    
    async def _cleanup_invalid_connections(self):
        """Remove conexões inválidas"""
        start_time = time.time()
        
        with self.connection_lock:
            invalid_connections = [
                conn_id for conn_id, conn_info in self.connections.items()
                if not conn_info.is_valid
            ]
            
            for conn_id in invalid_connections:
                del self.connections[conn_id]
        
        cleanup_time = time.time() - start_time
        self.metrics.connection_cleanup_time = (
            (self.metrics.connection_cleanup_time + cleanup_time) / 2
        )
        
        if invalid_connections:
            logger.info(f"Cleaned up {len(invalid_connections)} invalid connections")
    
    async def _check_pool_status(self):
        """Verifica status do pool"""
        pool_status = self.get_pool_status()
        
        # Alertas
        if pool_status['active_connections'] > pool_status['max_connections'] * 0.8:
            logger.warning("Pool approaching capacity")
        
        if pool_status['errors'] > 10:
            logger.error("High error rate in connection pool")
    
    @contextmanager
    def get_connection(self):
        """Context manager para obter conexão síncrona"""
        session = None
        start_time = time.time()
        
        try:
            session = self.session_factory()
            yield session
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Error in connection: {e}")
            raise
        finally:
            if session:
                session.close()
            
            # Calcular tempo de espera
            wait_time = time.time() - start_time
            self.metrics.wait_time = (
                (self.metrics.wait_time + wait_time) / 2
            )
    
    @asynccontextmanager
    async def get_async_connection(self):
        """Context manager para obter conexão assíncrona"""
        session = None
        start_time = time.time()
        
        try:
            if self.async_session_factory:
                session = self.async_session_factory()
                yield session
            else:
                raise RuntimeError("Async engine not available")
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Error in async connection: {e}")
            raise
        finally:
            if session:
                await session.close()
            
            # Calcular tempo de espera
            wait_time = time.time() - start_time
            self.metrics.wait_time = (
                (self.metrics.wait_time + wait_time) / 2
            )
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Obtém status do pool"""
        with self.connection_lock:
            return {
                'total_connections': self.metrics.total_connections,
                'active_connections': self.metrics.active_connections,
                'idle_connections': self.metrics.idle_connections,
                'max_connections': self.metrics.max_connections,
                'min_connections': self.metrics.min_connections,
                'checkouts': self.metrics.checkouts,
                'checkins': self.metrics.checkins,
                'errors': self.metrics.errors,
                'wait_time': self.metrics.wait_time,
                'avg_checkout_time': self.metrics.avg_checkout_time,
                'avg_checkin_time': self.metrics.avg_checkin_time,
                'connection_creation_time': self.metrics.connection_creation_time,
                'connection_cleanup_time': self.metrics.connection_cleanup_time,
                'utilization_rate': (
                    self.metrics.active_connections / self.metrics.max_connections * 100
                    if self.metrics.max_connections > 0 else 0
                )
            }
    
    def get_connection_details(self) -> List[Dict[str, Any]]:
        """Obtém detalhes das conexões"""
        with self.connection_lock:
            return [
                {
                    'id': conn_info.id,
                    'state': conn_info.state.value,
                    'created_at': conn_info.created_at.isoformat(),
                    'last_used': conn_info.last_used.isoformat(),
                    'checkouts': conn_info.checkouts,
                    'checkins': conn_info.checkins,
                    'errors': conn_info.errors,
                    'is_valid': conn_info.is_valid
                }
                for conn_info in self.connections.values()
            ]
    
    async def test_connection(self) -> bool:
        """Testa conexão com o banco"""
        try:
            if self.async_engine:
                async with self.async_engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
            else:
                with self.engine.begin() as conn:
                    conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def close(self):
        """Fecha o pool de conexões"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.async_engine:
            await self.async_engine.dispose()
        
        if self.engine:
            self.engine.dispose()
        
        logger.info("Connection pool closed")


class PoolManager:
    """
    Gerenciador de múltiplos pools
    """
    
    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self.default_pool: Optional[ConnectionPool] = None
    
    def add_pool(self, name: str, database_url: str, config: Optional[PoolConfig] = None) -> ConnectionPool:
        """Adiciona um pool"""
        pool = ConnectionPool(database_url, config)
        self.pools[name] = pool
        
        if not self.default_pool:
            self.default_pool = pool
        
        return pool
    
    def get_pool(self, name: str = None) -> Optional[ConnectionPool]:
        """Obtém um pool"""
        if name:
            return self.pools.get(name)
        return self.default_pool
    
    def remove_pool(self, name: str) -> bool:
        """Remove um pool"""
        if name in self.pools:
            pool = self.pools[name]
            asyncio.create_task(pool.close())
            del self.pools[name]
            
            if self.default_pool == pool:
                self.default_pool = next(iter(self.pools.values()), None)
            
            return True
        return False
    
    def get_all_pools_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtém status de todos os pools"""
        return {
            name: pool.get_pool_status()
            for name, pool in self.pools.items()
        }
    
    async def close_all(self):
        """Fecha todos os pools"""
        for pool in self.pools.values():
            await pool.close()
        self.pools.clear()
        self.default_pool = None


# Instância global do gerenciador de pools
pool_manager = PoolManager()


# Decorators para facilitar uso
def with_connection(pool_name: str = None):
    """Decorator para usar conexão do pool"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pool = pool_manager.get_pool(pool_name)
            if not pool:
                raise RuntimeError(f"Pool {pool_name} not found")
            
            with pool.get_connection() as session:
                return func(session, *args, **kwargs)
        return wrapper
    return decorator


def with_async_connection(pool_name: str = None):
    """Decorator para usar conexão assíncrona do pool"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            pool = pool_manager.get_pool(pool_name)
            if not pool:
                raise RuntimeError(f"Pool {pool_name} not found")
            
            async with pool.get_async_connection() as session:
                return await func(session, *args, **kwargs)
        return wrapper
    return decorator


# Funções utilitárias
def create_pool(database_url: str, config: Optional[PoolConfig] = None) -> ConnectionPool:
    """Cria um pool de conexões"""
    return ConnectionPool(database_url, config)


def get_pool_status(pool_name: str = None) -> Dict[str, Any]:
    """Obtém status do pool"""
    pool = pool_manager.get_pool(pool_name)
    if pool:
        return pool.get_pool_status()
    return {}


async def test_pool_connection(pool_name: str = None) -> bool:
    """Testa conexão do pool"""
    pool = pool_manager.get_pool(pool_name)
    if pool:
        return await pool.test_connection()
    return False 