"""
Testes Unitários para Connection Pool
Sistema de Pool de Conexões de Banco de Dados - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de pool de conexões
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.performance.connection_pool import (
    DatabaseConnectionPool, ConnectionConfig, PoolConfig,
    ConnectionState, PoolStrategy, ConnectionInfo, PoolStats,
    create_connection_pool
)


class TestConnectionConfig:
    """Testes para ConnectionConfig"""
    
    def test_connection_config_initialization(self):
        """Testa inicialização de ConnectionConfig"""
        config = ConnectionConfig(
            host="localhost",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass",
            charset="utf8mb4",
            autocommit=False,
            connect_timeout=15,
            read_timeout=45,
            write_timeout=45,
            ssl_mode="required",
            ssl_ca="/path/to/ca.pem",
            ssl_cert="/path/to/cert.pem",
            ssl_key="/path/to/key.pem",
            max_allowed_packet=33554432,
            sql_mode="STRICT_TRANS_TABLES"
        )
        
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.database == "testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.charset == "utf8mb4"
        assert config.autocommit is False
        assert config.connect_timeout == 15
        assert config.read_timeout == 45
        assert config.write_timeout == 45
        assert config.ssl_mode == "required"
        assert config.ssl_ca == "/path/to/ca.pem"
        assert config.ssl_cert == "/path/to/cert.pem"
        assert config.ssl_key == "/path/to/key.pem"
        assert config.max_allowed_packet == 33554432
        assert config.sql_mode == "STRICT_TRANS_TABLES"
    
    def test_connection_config_validation_host_empty(self):
        """Testa validação de host vazio"""
        with pytest.raises(ValueError, match="Host não pode ser vazio"):
            ConnectionConfig(
                host="",
                port=3306,
                database="testdb",
                username="testuser",
                password="testpass"
            )
    
    def test_connection_config_validation_port_invalid(self):
        """Testa validação de port inválido"""
        with pytest.raises(ValueError, match="Port deve estar entre 1 e 65535"):
            ConnectionConfig(
                host="localhost",
                port=0,
                database="testdb",
                username="testuser",
                password="testpass"
            )
    
    def test_connection_config_validation_database_empty(self):
        """Testa validação de database vazio"""
        with pytest.raises(ValueError, match="Database não pode ser vazio"):
            ConnectionConfig(
                host="localhost",
                port=3306,
                database="",
                username="testuser",
                password="testpass"
            )
    
    def test_connection_config_validation_username_empty(self):
        """Testa validação de username vazio"""
        with pytest.raises(ValueError, match="Username não pode ser vazio"):
            ConnectionConfig(
                host="localhost",
                port=3306,
                database="testdb",
                username="",
                password="testpass"
            )
    
    def test_connection_config_validation_connect_timeout_negative(self):
        """Testa validação de connect timeout negativo"""
        with pytest.raises(ValueError, match="Connect timeout deve ser positivo"):
            ConnectionConfig(
                host="localhost",
                port=3306,
                database="testdb",
                username="testuser",
                password="testpass",
                connect_timeout=0
            )
    
    def test_connection_config_validation_read_timeout_negative(self):
        """Testa validação de read timeout negativo"""
        with pytest.raises(ValueError, match="Read timeout deve ser positivo"):
            ConnectionConfig(
                host="localhost",
                port=3306,
                database="testdb",
                username="testuser",
                password="testpass",
                read_timeout=0
            )
    
    def test_connection_config_validation_write_timeout_negative(self):
        """Testa validação de write timeout negativo"""
        with pytest.raises(ValueError, match="Write timeout deve ser positivo"):
            ConnectionConfig(
                host="localhost",
                port=3306,
                database="testdb",
                username="testuser",
                password="testpass",
                write_timeout=0
            )
    
    def test_connection_config_validation_max_allowed_packet_negative(self):
        """Testa validação de max allowed packet negativo"""
        with pytest.raises(ValueError, match="Max allowed packet deve ser positivo"):
            ConnectionConfig(
                host="localhost",
                port=3306,
                database="testdb",
                username="testuser",
                password="testpass",
                max_allowed_packet=0
            )
    
    def test_connection_config_normalization(self):
        """Testa normalização de campos"""
        config = ConnectionConfig(
            host="  localhost  ",
            port=3306,
            database="  testdb  ",
            username="  testuser  ",
            password="testpass"
        )
        
        assert config.host == "localhost"
        assert config.database == "testdb"
        assert config.username == "testuser"


class TestPoolConfig:
    """Testes para PoolConfig"""
    
    def test_pool_config_initialization(self):
        """Testa inicialização de PoolConfig"""
        config = PoolConfig(
            min_connections=10,
            max_connections=50,
            initial_connections=20,
            connection_timeout=60,
            idle_timeout=600,
            max_lifetime=7200,
            health_check_interval=60,
            health_check_timeout=10,
            health_check_query="SELECT 1 FROM dual",
            enable_health_checks=False,
            enable_connection_reuse=False,
            enable_connection_preparation=False,
            enable_connection_validation=False,
            validation_timeout=10,
            strategy=PoolStrategy.LEAST_CONNECTIONS,
            enable_metrics=False,
            enable_logging=False,
            retry_attempts=5,
            retry_delay=2.0,
            failover_enabled=True,
            failover_hosts=["host2", "host3"]
        )
        
        assert config.min_connections == 10
        assert config.max_connections == 50
        assert config.initial_connections == 20
        assert config.connection_timeout == 60
        assert config.idle_timeout == 600
        assert config.max_lifetime == 7200
        assert config.health_check_interval == 60
        assert config.health_check_timeout == 10
        assert config.health_check_query == "SELECT 1 FROM dual"
        assert config.enable_health_checks is False
        assert config.enable_connection_reuse is False
        assert config.enable_connection_preparation is False
        assert config.enable_connection_validation is False
        assert config.validation_timeout == 10
        assert config.strategy == PoolStrategy.LEAST_CONNECTIONS
        assert config.enable_metrics is False
        assert config.enable_logging is False
        assert config.retry_attempts == 5
        assert config.retry_delay == 2.0
        assert config.failover_enabled is True
        assert config.failover_hosts == ["host2", "host3"]
    
    def test_pool_config_validation_min_connections_negative(self):
        """Testa validação de min connections negativo"""
        with pytest.raises(ValueError, match="Min connections deve ser positivo"):
            PoolConfig(min_connections=0)
    
    def test_pool_config_validation_max_connections_negative(self):
        """Testa validação de max connections negativo"""
        with pytest.raises(ValueError, match="Max connections deve ser positivo"):
            PoolConfig(max_connections=0)
    
    def test_pool_config_validation_min_greater_than_max(self):
        """Testa validação de min maior que max"""
        with pytest.raises(ValueError, match="Min connections não pode ser maior que max connections"):
            PoolConfig(min_connections=20, max_connections=10)
    
    def test_pool_config_validation_initial_less_than_min(self):
        """Testa validação de initial menor que min"""
        with pytest.raises(ValueError, match="Initial connections deve ser pelo menos min connections"):
            PoolConfig(min_connections=10, initial_connections=5)
    
    def test_pool_config_validation_initial_greater_than_max(self):
        """Testa validação de initial maior que max"""
        with pytest.raises(ValueError, match="Initial connections não pode ser maior que max connections"):
            PoolConfig(max_connections=10, initial_connections=15)
    
    def test_pool_config_validation_connection_timeout_negative(self):
        """Testa validação de connection timeout negativo"""
        with pytest.raises(ValueError, match="Connection timeout deve ser positivo"):
            PoolConfig(connection_timeout=0)
    
    def test_pool_config_validation_idle_timeout_negative(self):
        """Testa validação de idle timeout negativo"""
        with pytest.raises(ValueError, match="Idle timeout deve ser positivo"):
            PoolConfig(idle_timeout=0)
    
    def test_pool_config_validation_max_lifetime_negative(self):
        """Testa validação de max lifetime negativo"""
        with pytest.raises(ValueError, match="Max lifetime deve ser positivo"):
            PoolConfig(max_lifetime=0)
    
    def test_pool_config_validation_health_check_interval_negative(self):
        """Testa validação de health check interval negativo"""
        with pytest.raises(ValueError, match="Health check interval deve ser positivo"):
            PoolConfig(health_check_interval=0)
    
    def test_pool_config_validation_health_check_timeout_negative(self):
        """Testa validação de health check timeout negativo"""
        with pytest.raises(ValueError, match="Health check timeout deve ser positivo"):
            PoolConfig(health_check_timeout=0)
    
    def test_pool_config_validation_validation_timeout_negative(self):
        """Testa validação de validation timeout negativo"""
        with pytest.raises(ValueError, match="Validation timeout deve ser positivo"):
            PoolConfig(validation_timeout=0)
    
    def test_pool_config_validation_retry_attempts_negative(self):
        """Testa validação de retry attempts negativo"""
        with pytest.raises(ValueError, match="Retry attempts não pode ser negativo"):
            PoolConfig(retry_attempts=-1)
    
    def test_pool_config_validation_retry_delay_negative(self):
        """Testa validação de retry delay negativo"""
        with pytest.raises(ValueError, match="Retry delay não pode ser negativo"):
            PoolConfig(retry_delay=-1.0)


class TestConnectionInfo:
    """Testes para ConnectionInfo"""
    
    def test_connection_info_initialization(self):
        """Testa inicialização de ConnectionInfo"""
        connection = {"host": "localhost", "port": 3306}
        created_at = datetime.utcnow()
        
        info = ConnectionInfo(
            id="conn_1",
            connection=connection,
            state=ConnectionState.IDLE,
            created_at=created_at,
            last_used=created_at,
            use_count=5,
            last_health_check=created_at,
            health_status=True,
            error_count=0,
            last_error=None,
            metadata={"pool": "main"}
        )
        
        assert info.id == "conn_1"
        assert info.connection == connection
        assert info.state == ConnectionState.IDLE
        assert info.created_at == created_at
        assert info.last_used == created_at
        assert info.use_count == 5
        assert info.last_health_check == created_at
        assert info.health_status is True
        assert info.error_count == 0
        assert info.last_error is None
        assert info.metadata == {"pool": "main"}
    
    def test_is_expired_false(self):
        """Testa verificação de expiração - não expirado"""
        info = ConnectionInfo(
            id="test",
            connection={},
            state=ConnectionState.IDLE,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow()
        )
        
        assert info.is_expired(3600) is False
    
    def test_is_expired_true(self):
        """Testa verificação de expiração - expirado"""
        info = ConnectionInfo(
            id="test",
            connection={},
            state=ConnectionState.IDLE,
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_used=datetime.utcnow()
        )
        
        assert info.is_expired(3600) is True
    
    def test_is_idle_too_long_false(self):
        """Testa verificação de ociosidade - não ocioso demais"""
        info = ConnectionInfo(
            id="test",
            connection={},
            state=ConnectionState.IDLE,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow()
        )
        
        assert info.is_idle_too_long(300) is False
    
    def test_is_idle_too_long_true(self):
        """Testa verificação de ociosidade - ocioso demais"""
        info = ConnectionInfo(
            id="test",
            connection={},
            state=ConnectionState.IDLE,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow() - timedelta(minutes=10)
        )
        
        assert info.is_idle_too_long(300) is True
    
    def test_needs_health_check_no_last_check(self):
        """Testa necessidade de health check - sem último check"""
        info = ConnectionInfo(
            id="test",
            connection={},
            state=ConnectionState.IDLE,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow(),
            last_health_check=None
        )
        
        assert info.needs_health_check(30) is True
    
    def test_needs_health_check_recent_check(self):
        """Testa necessidade de health check - check recente"""
        info = ConnectionInfo(
            id="test",
            connection={},
            state=ConnectionState.IDLE,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow(),
            last_health_check=datetime.utcnow()
        )
        
        assert info.needs_health_check(30) is False
    
    def test_needs_health_check_old_check(self):
        """Testa necessidade de health check - check antigo"""
        info = ConnectionInfo(
            id="test",
            connection={},
            state=ConnectionState.IDLE,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow(),
            last_health_check=datetime.utcnow() - timedelta(minutes=1)
        )
        
        assert info.needs_health_check(30) is True


class TestPoolStats:
    """Testes para PoolStats"""
    
    def test_pool_stats_initialization(self):
        """Testa inicialização de PoolStats"""
        stats = PoolStats(
            total_connections=20,
            active_connections=10,
            idle_connections=8,
            failed_connections=2,
            connection_requests=100,
            connection_timeouts=5,
            connection_errors=3,
            avg_connection_time=0.5,
            avg_query_time=0.1,
            health_check_failures=1,
            last_health_check=datetime.utcnow(),
            pool_utilization=0.5
        )
        
        assert stats.total_connections == 20
        assert stats.active_connections == 10
        assert stats.idle_connections == 8
        assert stats.failed_connections == 2
        assert stats.connection_requests == 100
        assert stats.connection_timeouts == 5
        assert stats.connection_errors == 3
        assert stats.avg_connection_time == 0.5
        assert stats.avg_query_time == 0.1
        assert stats.health_check_failures == 1
        assert stats.pool_utilization == 0.5
    
    def test_update_utilization_with_connections(self):
        """Testa atualização de utilização com conexões"""
        stats = PoolStats(total_connections=10, active_connections=5)
        
        stats.update_utilization()
        assert stats.pool_utilization == 0.5
    
    def test_update_utilization_no_connections(self):
        """Testa atualização de utilização sem conexões"""
        stats = PoolStats(total_connections=0, active_connections=0)
        
        stats.update_utilization()
        assert stats.pool_utilization == 0.0


class TestDatabaseConnectionPool:
    """Testes para DatabaseConnectionPool"""
    
    @pytest.fixture
    def connection_config(self):
        """Configuração de conexão para testes"""
        return ConnectionConfig(
            host="localhost",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass"
        )
    
    @pytest.fixture
    def pool_config(self):
        """Configuração de pool para testes"""
        return PoolConfig(
            min_connections=2,
            max_connections=5,
            initial_connections=3,
            enable_health_checks=False
        )
    
    @pytest.fixture
    def pool(self, connection_config, pool_config):
        """Instância de DatabaseConnectionPool para testes"""
        return DatabaseConnectionPool(connection_config, pool_config)
    
    def test_database_connection_pool_initialization(self, connection_config):
        """Testa inicialização do DatabaseConnectionPool"""
        pool = DatabaseConnectionPool(connection_config)
        
        assert pool.connection_config == connection_config
        assert pool.pool_config is not None
        assert len(pool.connections) == 0
        assert len(pool.available_connections) == 0
        assert pool.running is False
        assert pool.stats is not None
    
    def test_get_connection_success(self, pool):
        """Testa obtenção de conexão com sucesso"""
        pool.start()
        
        try:
            connection = pool.get_connection()
            assert connection is not None
            
            # Verificar que conexão foi marcada como em uso
            connection_info = None
            for conn_info in pool.connections.values():
                if conn_info.connection == connection:
                    connection_info = conn_info
                    break
            
            assert connection_info is not None
            assert connection_info.state == ConnectionState.IN_USE
            assert connection_info.use_count == 1
            
        finally:
            pool.stop()
    
    def test_get_connection_pool_exhausted(self, pool):
        """Testa obtenção de conexão com pool esgotado"""
        pool.pool_config.max_connections = 1
        pool.start()
        
        try:
            # Obter primeira conexão
            connection1 = pool.get_connection()
            assert connection1 is not None
            
            # Tentar obter segunda conexão (deve falhar)
            connection2 = pool.get_connection()
            assert connection2 is None
            
            # Verificar estatísticas
            stats = pool.get_stats()
            assert stats['connection_timeouts'] > 0
            
        finally:
            pool.stop()
    
    def test_release_connection_success(self, pool):
        """Testa liberação de conexão com sucesso"""
        pool.start()
        
        try:
            # Obter conexão
            connection = pool.get_connection()
            assert connection is not None
            
            # Liberar conexão
            success = pool.release_connection(connection)
            assert success is True
            
            # Verificar que conexão foi marcada como ociosa
            connection_info = None
            for conn_info in pool.connections.values():
                if conn_info.connection == connection:
                    connection_info = conn_info
                    break
            
            assert connection_info is not None
            assert connection_info.state == ConnectionState.IDLE
            
        finally:
            pool.stop()
    
    def test_release_connection_not_found(self, pool):
        """Testa liberação de conexão não encontrada"""
        pool.start()
        
        try:
            # Tentar liberar conexão inexistente
            fake_connection = {"fake": "connection"}
            success = pool.release_connection(fake_connection)
            assert success is False
            
        finally:
            pool.stop()
    
    def test_close_connection_success(self, pool):
        """Testa fechamento de conexão com sucesso"""
        pool.start()
        
        try:
            # Obter conexão
            connection = pool.get_connection()
            assert connection is not None
            
            initial_count = len(pool.connections)
            
            # Fechar conexão
            success = pool.close_connection(connection)
            assert success is True
            
            # Verificar que conexão foi removida
            assert len(pool.connections) == initial_count - 1
            
        finally:
            pool.stop()
    
    def test_close_connection_not_found(self, pool):
        """Testa fechamento de conexão não encontrada"""
        pool.start()
        
        try:
            # Tentar fechar conexão inexistente
            fake_connection = {"fake": "connection"}
            success = pool.close_connection(fake_connection)
            assert success is False
            
        finally:
            pool.stop()
    
    def test_get_stats(self, pool):
        """Testa obtenção de estatísticas"""
        pool.start()
        
        try:
            # Obter algumas conexões
            connection1 = pool.get_connection()
            connection2 = pool.get_connection()
            
            stats = pool.get_stats()
            
            assert stats['total_connections'] > 0
            assert stats['active_connections'] > 0
            assert stats['connection_requests'] > 0
            assert 'pool_utilization' in stats
            assert 'pool_config' in stats
            
        finally:
            pool.stop()
    
    def test_start_stop_pool(self, pool):
        """Testa início e parada do pool"""
        # Iniciar
        pool.start()
        assert pool.running is True
        assert len(pool.connections) >= pool.pool_config.initial_connections
        
        # Parar
        pool.stop()
        assert pool.running is False
        assert len(pool.connections) == 0
    
    def test_connection_strategies(self, connection_config, pool_config):
        """Testa diferentes estratégias de conexão"""
        strategies = [
            PoolStrategy.ROUND_ROBIN,
            PoolStrategy.LEAST_CONNECTIONS,
            PoolStrategy.WEIGHTED,
            PoolStrategy.RANDOM
        ]
        
        for strategy in strategies:
            pool_config.strategy = strategy
            pool = DatabaseConnectionPool(connection_config, pool_config)
            pool.start()
            
            try:
                # Obter algumas conexões
                connections = []
                for _ in range(3):
                    conn = pool.get_connection()
                    if conn:
                        connections.append(conn)
                
                # Verificar que conexões foram obtidas
                assert len(connections) > 0
                
            finally:
                pool.stop()
    
    def test_connection_validation(self, pool):
        """Testa validação de conexões"""
        pool.pool_config.enable_connection_validation = True
        pool.start()
        
        try:
            # Obter conexão
            connection = pool.get_connection()
            assert connection is not None
            
            # Liberar conexão (deve passar pela validação)
            success = pool.release_connection(connection)
            assert success is True
            
        finally:
            pool.stop()
    
    def test_callback_on_connection_created(self, connection_config, pool_config):
        """Testa callback de conexão criada"""
        created_connections = []
        
        def on_connection_created(connection_info):
            created_connections.append(connection_info)
        
        pool = DatabaseConnectionPool(connection_config, pool_config)
        pool.on_connection_created = on_connection_created
        pool.start()
        
        try:
            # Aguardar conexões serem criadas
            time.sleep(0.1)
            
            assert len(created_connections) >= pool_config.initial_connections
            
        finally:
            pool.stop()
    
    def test_callback_on_connection_closed(self, connection_config, pool_config):
        """Testa callback de conexão fechada"""
        closed_connections = []
        
        def on_connection_closed(connection_info):
            closed_connections.append(connection_info)
        
        pool = DatabaseConnectionPool(connection_config, pool_config)
        pool.on_connection_closed = on_connection_closed
        pool.start()
        
        try:
            # Obter e fechar conexão
            connection = pool.get_connection()
            pool.close_connection(connection)
            
            assert len(closed_connections) == 1
            
        finally:
            pool.stop()
    
    def test_callback_on_pool_exhausted(self, connection_config, pool_config):
        """Testa callback de pool esgotado"""
        pool_exhausted_called = False
        
        def on_pool_exhausted():
            nonlocal pool_exhausted_called
            pool_exhausted_called = True
        
        pool_config.max_connections = 1
        pool = DatabaseConnectionPool(connection_config, pool_config)
        pool.on_pool_exhausted = on_pool_exhausted
        pool.start()
        
        try:
            # Obter primeira conexão
            connection1 = pool.get_connection()
            
            # Tentar obter segunda conexão (deve chamar callback)
            connection2 = pool.get_connection()
            
            assert pool_exhausted_called is True
            
        finally:
            pool.stop()


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_connection_pool_default(self):
        """Testa criação de DatabaseConnectionPool com configurações padrão"""
        connection_config = ConnectionConfig(
            host="localhost",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        pool = create_connection_pool(connection_config)
        
        assert isinstance(pool, DatabaseConnectionPool)
        assert pool.connection_config == connection_config
        assert pool.pool_config is not None
    
    def test_create_connection_pool_custom(self):
        """Testa criação de DatabaseConnectionPool com configurações customizadas"""
        connection_config = ConnectionConfig(
            host="localhost",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        pool_config = PoolConfig(
            min_connections=10,
            max_connections=50,
            strategy=PoolStrategy.LEAST_CONNECTIONS
        )
        
        def mock_factory(config):
            return {"host": config.host, "port": config.port}
        
        pool = create_connection_pool(connection_config, pool_config, mock_factory)
        
        assert pool.pool_config.min_connections == 10
        assert pool.pool_config.max_connections == 50
        assert pool.pool_config.strategy == PoolStrategy.LEAST_CONNECTIONS
        assert pool.connection_factory == mock_factory


class TestDatabaseConnectionPoolIntegration:
    """Testes de integração para Database Connection Pool"""
    
    def test_complete_workflow(self):
        """Testa workflow completo do pool"""
        connection_config = ConnectionConfig(
            host="localhost",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        pool_config = PoolConfig(
            min_connections=2,
            max_connections=5,
            initial_connections=3,
            enable_health_checks=False
        )
        
        pool = DatabaseConnectionPool(connection_config, pool_config)
        pool.start()
        
        try:
            # Obter múltiplas conexões
            connections = []
            for _ in range(3):
                conn = pool.get_connection()
                assert conn is not None
                connections.append(conn)
            
            # Verificar estatísticas
            stats = pool.get_stats()
            assert stats['total_connections'] >= 3
            assert stats['active_connections'] == 3
            assert stats['connection_requests'] == 3
            
            # Liberar conexões
            for conn in connections:
                success = pool.release_connection(conn)
                assert success is True
            
            # Verificar estatísticas após liberação
            stats = pool.get_stats()
            assert stats['active_connections'] == 0
            assert stats['idle_connections'] >= 3
            
        finally:
            pool.stop()
    
    def test_concurrent_access(self):
        """Testa acesso concorrente ao pool"""
        connection_config = ConnectionConfig(
            host="localhost",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        pool_config = PoolConfig(
            min_connections=5,
            max_connections=10,
            initial_connections=5,
            enable_health_checks=False
        )
        
        pool = DatabaseConnectionPool(connection_config, pool_config)
        pool.start()
        
        try:
            connections_obtained = []
            errors = []
            
            def worker(worker_id):
                try:
                    conn = pool.get_connection(timeout=5)
                    if conn:
                        connections_obtained.append(conn)
                        time.sleep(0.1)  # Simular uso
                        pool.release_connection(conn)
                except Exception as e:
                    errors.append(e)
            
            # Criar threads
            threads = []
            for i in range(10):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Aguardar threads terminarem
            for thread in threads:
                thread.join()
            
            # Verificar resultados
            assert len(errors) == 0
            assert len(connections_obtained) > 0
            
        finally:
            pool.stop()
    
    def test_connection_reuse(self):
        """Testa reutilização de conexões"""
        connection_config = ConnectionConfig(
            host="localhost",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        pool_config = PoolConfig(
            min_connections=1,
            max_connections=2,
            initial_connections=1,
            enable_health_checks=False
        )
        
        pool = DatabaseConnectionPool(connection_config, pool_config)
        pool.start()
        
        try:
            # Obter primeira conexão
            conn1 = pool.get_connection()
            assert conn1 is not None
            
            # Liberar conexão
            pool.release_connection(conn1)
            
            # Obter segunda conexão (deve reutilizar a primeira)
            conn2 = pool.get_connection()
            assert conn2 is not None
            
            # Verificar que é a mesma conexão
            assert conn1 == conn2
            
            # Verificar contador de uso
            for conn_info in pool.connections.values():
                if conn_info.connection == conn1:
                    assert conn_info.use_count == 2
                    break
            
        finally:
            pool.stop()


if __name__ == "__main__":
    pytest.main([__file__]) 