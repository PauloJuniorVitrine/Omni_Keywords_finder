# 📋 Multi-Region Database Manager
# Tracing ID: MULTI_REGION_DB_009_20250127
# Versão: 1.0
# Data: 2025-01-27
# Objetivo: Gerenciamento de database multi-region com replicação

"""
Multi-Region Database Manager

Este módulo gerencia conexões de banco de dados em múltiplas regiões,
fornecendo replicação automática, failover e balanceamento de carga.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncpg
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import asynccontextmanager, contextmanager
import yaml
import os
from datetime import datetime, timedelta

# Configuração de logging
logger = logging.getLogger(__name__)

class DatabaseRole(Enum):
    """Roles possíveis para instâncias de banco de dados"""
    PRIMARY = "primary"
    REPLICA = "replica"
    STANDBY = "standby"

class DatabaseStatus(Enum):
    """Status possíveis para instâncias de banco de dados"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    FAILING_OVER = "failing_over"

@dataclass
class DatabaseInstance:
    """Configuração de uma instância de banco de dados"""
    name: str
    host: str
    port: int
    database: str
    username: str
    password: str
    role: DatabaseRole
    region: str
    priority: int
    ssl_mode: str = "require"
    connection_timeout: int = 30
    max_connections: int = 20
    min_connections: int = 5
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.host or not self.database or not self.username:
            raise ValueError("Host, database e username são obrigatórios")
        if self.port < 1 or self.port > 65535:
            raise ValueError("Porta deve estar entre 1 e 65535")
        if self.priority < 0:
            raise ValueError("Priority deve ser >= 0")

@dataclass
class DatabaseMetrics:
    """Métricas de performance do banco de dados"""
    response_time: float
    connection_count: int
    active_queries: int
    replication_lag: Optional[float]
    last_check: datetime
    status: DatabaseStatus

class MultiRegionDatabaseManager:
    """
    Gerenciador de banco de dados multi-region
    
    Gerencia conexões, replicação e failover entre múltiplas regiões.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de banco de dados multi-region
        
        Args:
            config_path: Caminho para arquivo de configuração YAML
        """
        self.config_path = config_path or "config/database_config.yaml"
        self.instances: Dict[str, DatabaseInstance] = {}
        self.connection_pools: Dict[str, SimpleConnectionPool] = {}
        self.metrics: Dict[str, DatabaseMetrics] = {}
        self.current_primary: Optional[str] = None
        self.health_check_interval = 30  # segundos
        self.failover_threshold = 3  # tentativas
        self.replication_check_interval = 60  # segundos
        
        # Configuração de circuit breaker
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.circuit_breaker_timeout = 300  # segundos
        
        # Configuração de load balancing
        self.load_balancing_strategy = "round_robin"  # ou "least_connections"
        self.current_replica_index = 0
        
        # Inicialização
        self._load_configuration()
        self._initialize_connection_pools()
        self._start_health_monitoring()
        
        logger.info("MultiRegionDatabaseManager inicializado com sucesso")
    
    def _load_configuration(self) -> None:
        """Carrega configuração do arquivo YAML"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    config = yaml.safe_load(file)
                
                # Configuração de database
                db_config = config.get('database', {})
                
                # Instância primária
                primary_config = db_config.get('primary', {})
                primary_instance = DatabaseInstance(
                    name="primary",
                    host=primary_config.get('host'),
                    port=primary_config.get('port', 5432),
                    database=primary_config.get('database'),
                    username=primary_config.get('username'),
                    password=primary_config.get('password'),
                    role=DatabaseRole.PRIMARY,
                    region=primary_config.get('region', 'us-east-1'),
                    priority=0,
                    ssl_mode=primary_config.get('ssl_mode', 'require'),
                    connection_timeout=primary_config.get('connection_timeout', 30),
                    max_connections=primary_config.get('max_connections', 20),
                    min_connections=primary_config.get('min_connections', 5)
                )
                self.instances["primary"] = primary_instance
                self.current_primary = "primary"
                
                # Instâncias réplicas
                replicas_config = db_config.get('replicas', [])
                for i, replica_config in enumerate(replicas_config):
                    replica_instance = DatabaseInstance(
                        name=f"replica_{i+1}",
                        host=replica_config.get('host'),
                        port=replica_config.get('port', 5432),
                        database=replica_config.get('database'),
                        username=replica_config.get('username'),
                        password=replica_config.get('password'),
                        role=DatabaseRole.REPLICA,
                        region=replica_config.get('region', 'us-west-2'),
                        priority=replica_config.get('priority', i+1),
                        ssl_mode=replica_config.get('ssl_mode', 'require'),
                        connection_timeout=replica_config.get('connection_timeout', 30),
                        max_connections=replica_config.get('max_connections', 15),
                        min_connections=replica_config.get('min_connections', 3)
                    )
                    self.instances[f"replica_{i+1}"] = replica_instance
                
                logger.info(f"Configuração carregada: {len(self.instances)} instâncias")
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                self._load_from_environment()
                
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Carrega configuração das variáveis de ambiente"""
        try:
            # Configuração primária
            primary_instance = DatabaseInstance(
                name="primary",
                host=os.getenv('DATABASE_PRIMARY_HOST', 'localhost'),
                port=int(os.getenv('DATABASE_PRIMARY_PORT', '5432')),
                database=os.getenv('DATABASE_NAME', 'omni_keywords'),
                username=os.getenv('DATABASE_USERNAME', 'omni_user'),
                password=os.getenv('DATABASE_PASSWORD', ''),
                role=DatabaseRole.PRIMARY,
                region=os.getenv('DATABASE_PRIMARY_REGION', 'us-east-1'),
                priority=0
            )
            self.instances["primary"] = primary_instance
            self.current_primary = "primary"
            
            # Configuração de réplicas
            replica_hosts = os.getenv('DATABASE_REPLICA_HOSTS', '').split(',')
            replica_regions = os.getenv('DATABASE_REPLICA_REGIONS', '').split(',')
            
            for i, (host, region) in enumerate(zip(replica_hosts, replica_regions)):
                if host and region:
                    replica_instance = DatabaseInstance(
                        name=f"replica_{i+1}",
                        host=host.strip(),
                        port=int(os.getenv('DATABASE_REPLICA_PORT', '5432')),
                        database=os.getenv('DATABASE_NAME', 'omni_keywords'),
                        username=os.getenv('DATABASE_USERNAME', 'omni_user'),
                        password=os.getenv('DATABASE_PASSWORD', ''),
                        role=DatabaseRole.REPLICA,
                        region=region.strip(),
                        priority=i+1
                    )
                    self.instances[f"replica_{i+1}"] = replica_instance
            
            logger.info(f"Configuração carregada do ambiente: {len(self.instances)} instâncias")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração do ambiente: {e}")
            raise
    
    def _initialize_connection_pools(self) -> None:
        """Inicializa pools de conexão para todas as instâncias"""
        for name, instance in self.instances.items():
            try:
                pool = SimpleConnectionPool(
                    minconn=instance.min_connections,
                    maxconn=instance.max_connections,
                    host=instance.host,
                    port=instance.port,
                    database=instance.database,
                    user=instance.username,
                    password=instance.password,
                    sslmode=instance.ssl_mode,
                    connect_timeout=instance.connection_timeout
                )
                self.connection_pools[name] = pool
                
                # Inicializa métricas
                self.metrics[name] = DatabaseMetrics(
                    response_time=0.0,
                    connection_count=0,
                    active_queries=0,
                    replication_lag=None,
                    last_check=datetime.now(),
                    status=DatabaseStatus.UNKNOWN
                )
                
                logger.info(f"Pool de conexão inicializado para {name}")
                
            except Exception as e:
                logger.error(f"Erro ao inicializar pool para {name}: {e}")
                self.metrics[name] = DatabaseMetrics(
                    response_time=0.0,
                    connection_count=0,
                    active_queries=0,
                    replication_lag=None,
                    last_check=datetime.now(),
                    status=DatabaseStatus.UNHEALTHY
                )
    
    def _start_health_monitoring(self) -> None:
        """Inicia monitoramento de saúde das instâncias"""
        asyncio.create_task(self._health_monitor_loop())
        asyncio.create_task(self._replication_monitor_loop())
    
    async def _health_monitor_loop(self) -> None:
        """Loop de monitoramento de saúde"""
        while True:
            try:
                await self._check_all_instances_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Erro no monitoramento de saúde: {e}")
                await asyncio.sleep(10)
    
    async def _replication_monitor_loop(self) -> None:
        """Loop de monitoramento de replicação"""
        while True:
            try:
                await self._check_replication_status()
                await asyncio.sleep(self.replication_check_interval)
            except Exception as e:
                logger.error(f"Erro no monitoramento de replicação: {e}")
                await asyncio.sleep(30)
    
    async def _check_all_instances_health(self) -> None:
        """Verifica saúde de todas as instâncias"""
        tasks = []
        for name in self.instances.keys():
            task = asyncio.create_task(self._check_instance_health(name))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_instance_health(self, instance_name: str) -> None:
        """Verifica saúde de uma instância específica"""
        try:
            start_time = time.time()
            
            # Testa conexão
            with self.get_connection(instance_name) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            
            response_time = time.time() - start_time
            
            # Atualiza métricas
            self.metrics[instance_name].response_time = response_time
            self.metrics[instance_name].last_check = datetime.now()
            self.metrics[instance_name].status = DatabaseStatus.HEALTHY
            
            # Reseta contador de falhas se estava saudável
            if instance_name in self.failure_counts:
                del self.failure_counts[instance_name]
            
            logger.debug(f"Health check {instance_name}: OK ({response_time:.3f}s)")
            
        except Exception as e:
            logger.warning(f"Health check {instance_name} falhou: {e}")
            
            # Incrementa contador de falhas
            self.failure_counts[instance_name] = self.failure_counts.get(instance_name, 0) + 1
            self.last_failure_time[instance_name] = datetime.now()
            
            # Atualiza status
            self.metrics[instance_name].status = DatabaseStatus.UNHEALTHY
            self.metrics[instance_name].last_check = datetime.now()
            
            # Verifica se precisa fazer failover
            if (self.failure_counts[instance_name] >= self.failover_threshold and 
                instance_name == self.current_primary):
                await self._trigger_failover()
    
    async def _check_replication_status(self) -> None:
        """Verifica status da replicação"""
        if not self.current_primary:
            return
        
        try:
            # Verifica lag de replicação em todas as réplicas
            for name, instance in self.instances.items():
                if instance.role == DatabaseRole.REPLICA:
                    await self._check_replication_lag(name)
                    
        except Exception as e:
            logger.error(f"Erro ao verificar replicação: {e}")
    
    async def _check_replication_lag(self, replica_name: str) -> None:
        """Verifica lag de replicação de uma réplica específica"""
        try:
            with self.get_connection(replica_name) as conn:
                with conn.cursor() as cursor:
                    # Verifica se a réplica está recebendo logs
                    cursor.execute("""
                        SELECT 
                            CASE 
                                WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn()
                                THEN 0
                                ELSE EXTRACT (EPOCH FROM now() - pg_last_xact_replay_timestamp()) * 1000
                            END AS replication_lag_ms
                    """)
                    result = cursor.fetchone()
                    
                    if result:
                        lag_ms = result[0] or 0
                        self.metrics[replica_name].replication_lag = lag_ms / 1000.0  # converte para segundos
                        
                        if lag_ms > 5000:  # mais de 5 segundos
                            logger.warning(f"Replicação lag alta em {replica_name}: {lag_ms}ms")
                    
        except Exception as e:
            logger.error(f"Erro ao verificar lag de replicação em {replica_name}: {e}")
    
    async def _trigger_failover(self) -> None:
        """Dispara processo de failover"""
        logger.warning(f"Iniciando failover - primary {self.current_primary} não está saudável")
        
        try:
            # Marca status de failover
            self.metrics[self.current_primary].status = DatabaseStatus.FAILING_OVER
            
            # Encontra a melhor réplica para promover
            best_replica = self._select_best_replica()
            
            if best_replica:
                # Promove réplica para primary
                await self._promote_replica_to_primary(best_replica)
                logger.info(f"Failover concluído: {best_replica} promovido para primary")
            else:
                logger.error("Nenhuma réplica adequada encontrada para failover")
                
        except Exception as e:
            logger.error(f"Erro durante failover: {e}")
            self.metrics[self.current_primary].status = DatabaseStatus.UNHEALTHY
    
    def _select_best_replica(self) -> Optional[str]:
        """Seleciona a melhor réplica para promover"""
        candidates = []
        
        for name, instance in self.instances.items():
            if (instance.role == DatabaseRole.REPLICA and 
                self.metrics[name].status == DatabaseStatus.HEALTHY):
                
                # Calcula score baseado em prioridade, lag e response time
                lag_penalty = self.metrics[name].replication_lag or 0
                response_penalty = self.metrics[name].response_time or 0
                score = instance.priority - lag_penalty - response_penalty
                
                candidates.append((name, score))
        
        if candidates:
            # Retorna a réplica com maior score
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    async def _promote_replica_to_primary(self, replica_name: str) -> None:
        """Promove uma réplica para primary"""
        try:
            # Atualiza configuração da réplica
            self.instances[replica_name].role = DatabaseRole.PRIMARY
            self.instances[replica_name].priority = 0
            
            # Atualiza primary anterior
            old_primary = self.current_primary
            self.instances[old_primary].role = DatabaseRole.STANDBY
            self.instances[old_primary].priority = 999
            
            # Atualiza referência atual
            self.current_primary = replica_name
            
            # Reseta contadores de falha
            if replica_name in self.failure_counts:
                del self.failure_counts[replica_name]
            
            logger.info(f"Réplica {replica_name} promovida para primary")
            
        except Exception as e:
            logger.error(f"Erro ao promover réplica {replica_name}: {e}")
            raise
    
    @contextmanager
    def get_connection(self, instance_name: Optional[str] = None, read_only: bool = False):
        """
        Obtém uma conexão do pool
        
        Args:
            instance_name: Nome da instância específica (None para auto-seleção)
            read_only: Se True, usa réplica para leitura
            
        Yields:
            Connection: Conexão PostgreSQL
        """
        if instance_name:
            target_instance = instance_name
        elif read_only:
            target_instance = self._select_read_replica()
        else:
            target_instance = self.current_primary
        
        if not target_instance or target_instance not in self.connection_pools:
            raise ValueError(f"Instância {target_instance} não disponível")
        
        # Verifica circuit breaker
        if self._is_circuit_breaker_open(target_instance):
            raise Exception(f"Circuit breaker aberto para {target_instance}")
        
        pool = self.connection_pools[target_instance]
        conn = None
        
        try:
            conn = pool.getconn()
            self.metrics[target_instance].connection_count += 1
            yield conn
        except Exception as e:
            # Incrementa contador de falhas
            self.failure_counts[target_instance] = self.failure_counts.get(target_instance, 0) + 1
            self.last_failure_time[target_instance] = datetime.now()
            raise
        finally:
            if conn:
                pool.putconn(conn)
                self.metrics[target_instance].connection_count -= 1
    
    def _select_read_replica(self) -> Optional[str]:
        """Seleciona uma réplica para leitura baseado na estratégia de load balancing"""
        healthy_replicas = [
            name for name, instance in self.instances.items()
            if (instance.role == DatabaseRole.REPLICA and 
                self.metrics[name].status == DatabaseStatus.HEALTHY)
        ]
        
        if not healthy_replicas:
            # Se não há réplicas saudáveis, usa primary
            return self.current_primary
        
        if self.load_balancing_strategy == "round_robin":
            # Round-robin entre réplicas
            replica = healthy_replicas[self.current_replica_index % len(healthy_replicas)]
            self.current_replica_index += 1
            return replica
        
        elif self.load_balancing_strategy == "least_connections":
            # Seleciona réplica com menos conexões
            return min(healthy_replicas, 
                      key=lambda x: self.metrics[x].connection_count)
        
        else:
            # Fallback para primeira réplica
            return healthy_replicas[0]
    
    def _is_circuit_breaker_open(self, instance_name: str) -> bool:
        """Verifica se o circuit breaker está aberto para uma instância"""
        if instance_name not in self.failure_counts:
            return False
        
        failure_count = self.failure_counts[instance_name]
        last_failure = self.last_failure_time.get(instance_name)
        
        if failure_count >= self.failover_threshold:
            if last_failure:
                time_since_failure = datetime.now() - last_failure
                if time_since_failure.total_seconds() < self.circuit_breaker_timeout:
                    return True
        
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de todas as instâncias"""
        return {
            name: {
                "status": metric.status.value,
                "response_time": metric.response_time,
                "connection_count": metric.connection_count,
                "replication_lag": metric.replication_lag,
                "last_check": metric.last_check.isoformat(),
                "role": self.instances[name].role.value,
                "region": self.instances[name].region,
                "priority": self.instances[name].priority
            }
            for name, metric in self.metrics.items()
        }
    
    def get_current_primary(self) -> Optional[str]:
        """Retorna o nome da instância primary atual"""
        return self.current_primary
    
    def get_healthy_replicas(self) -> List[str]:
        """Retorna lista de réplicas saudáveis"""
        return [
            name for name, instance in self.instances.items()
            if (instance.role == DatabaseRole.REPLICA and 
                self.metrics[name].status == DatabaseStatus.HEALTHY)
        ]
    
    async def close(self) -> None:
        """Fecha todas as conexões e pools"""
        for name, pool in self.connection_pools.items():
            try:
                pool.closeall()
                logger.info(f"Pool de conexão {name} fechado")
            except Exception as e:
                logger.error(f"Erro ao fechar pool {name}: {e}")
        
        self.connection_pools.clear()
        logger.info("MultiRegionDatabaseManager fechado")

# Singleton instance
_db_manager: Optional[MultiRegionDatabaseManager] = None

def get_db_manager() -> MultiRegionDatabaseManager:
    """Retorna instância singleton do gerenciador de banco de dados"""
    global _db_manager
    if _db_manager is None:
        _db_manager = MultiRegionDatabaseManager()
    return _db_manager

async def close_db_manager() -> None:
    """Fecha o gerenciador de banco de dados"""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None 