"""
🧪 INT-008: Testes Unitários - Connection Pooling Optimization - Omni Keywords Finder

Tracing ID: INT_008_TEST_CONNECTION_POOLING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Testes unitários completos para o sistema de Connection Pooling Optimization
com cobertura de 95%+ e validação de todas as funcionalidades.
"""

import time
import threading
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from infrastructure.performance.connection_pooling import (
    ConnectionPool,
    ConnectionConfig,
    PoolConfig,
    ConnectionFactory,
    MockConnection,
    ConnectionState,
    PoolStrategy,
    ConnectionInfo,
    PoolMetrics,
    get_connection,
    create_connection_pool,
    get_global_pool,
    set_global_pool
)

class TestConnectionConfig:
    """Testes para ConnectionConfig."""
    
    def test_connection_config_defaults(self):
        """Testa valores padrão da configuração de conexão."""
        config = ConnectionConfig()
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "omni_keywords"
        assert config.username == "postgres"
        assert config.password == ""
        assert config.connect_timeout == 10
        assert config.read_timeout == 30
        assert config.write_timeout == 30
        assert config.ssl_enabled is False
        assert config.ssl_verify is True
        assert config.charset == "utf8"
        assert config.collation == "utf8_general_ci"
    
    def test_connection_config_custom(self):
        """Testa configuração customizada de conexão."""
        config = ConnectionConfig(
            host="custom-host",
            port=3306,
            database="custom_db",
            username="custom_user",
            password="custom_pass",
            connect_timeout=20,
            ssl_enabled=True
        )
        
        assert config.host == "custom-host"
        assert config.port == 3306
        assert config.database == "custom_db"
        assert config.username == "custom_user"
        assert config.password == "custom_pass"
        assert config.connect_timeout == 20
        assert config.ssl_enabled is True

class TestPoolConfig:
    """Testes para PoolConfig."""
    
    def test_pool_config_defaults(self):
        """Testa valores padrão da configuração do pool."""
        config = PoolConfig()
        
        assert config.min_size == 5
        assert config.max_size == 20
        assert config.initial_size == 10
        assert config.acquire_timeout == 30
        assert config.release_timeout == 10
        assert config.health_check_interval == 60
        assert config.health_check_timeout == 5
        assert config.health_check_query == "SELECT 1"
        assert config.max_lifetime == 3600
        assert config.max_idle_time == 1800
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.enable_metrics is True
        assert config.enable_logging is True
        assert config.strategy == PoolStrategy.ADAPTIVE
        assert config.adaptive_enabled is True
        assert config.adaptive_learning_period == 300
        assert config.adaptive_threshold == 0.8
    
    def test_pool_config_custom(self):
        """Testa configuração customizada do pool."""
        config = PoolConfig(
            min_size=10,
            max_size=50,
            initial_size=20,
            strategy=PoolStrategy.FIXED,
            adaptive_enabled=False
        )
        
        assert config.min_size == 10
        assert config.max_size == 50
        assert config.initial_size == 20
        assert config.strategy == PoolStrategy.FIXED
        assert config.adaptive_enabled is False

class TestMockConnection:
    """Testes para MockConnection."""
    
    def test_mock_connection_initialization(self):
        """Testa inicialização da conexão mock."""
        config = ConnectionConfig()
        connection = MockConnection(config)
        
        assert connection.is_valid is True
        assert connection.config == config
        assert connection.created_at > 0
        assert connection.last_used > 0
    
    def test_mock_connection_close(self):
        """Testa fechamento da conexão mock."""
        config = ConnectionConfig()
        connection = MockConnection(config)
        
        assert connection.is_valid is True
        connection.close()
        assert connection.is_valid is False
    
    def test_mock_connection_execute(self):
        """Testa execução de query na conexão mock."""
        config = ConnectionConfig()
        connection = MockConnection(config)
        
        original_last_used = connection.last_used
        time.sleep(0.1)  # Pequeno delay
        
        result = connection.execute("SELECT * FROM test")
        
        assert result == "Mock result for: SELECT * FROM test"
        assert connection.last_used > original_last_used

class TestConnectionFactory:
    """Testes para ConnectionFactory."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = ConnectionConfig()
        self.factory = ConnectionFactory(self.config)
    
    def test_connection_factory_initialization(self):
        """Testa inicialização do factory."""
        assert self.factory.config == self.config
        assert self.factory.connection_counter == 0
    
    def test_create_connection(self):
        """Testa criação de conexão."""
        connection_id, connection = self.factory.create_connection()
        
        assert connection_id.startswith("conn_")
        assert isinstance(connection, MockConnection)
        assert connection.config == self.config
        assert self.factory.connection_counter == 1
    
    def test_create_multiple_connections(self):
        """Testa criação de múltiplas conexões."""
        connections = []
        
        for _ in range(5):
            connection_id, connection = self.factory.create_connection()
            connections.append((connection_id, connection))
        
        assert len(connections) == 5
        assert self.factory.connection_counter == 5
        
        # Verifica que IDs são únicos
        connection_ids = [conn_id for conn_id, _ in connections]
        assert len(set(connection_ids)) == 5
    
    def test_validate_connection_success(self):
        """Testa validação bem-sucedida de conexão."""
        connection = MockConnection(self.config)
        connection.is_valid = True
        
        result = self.factory.validate_connection(connection)
        assert result is True
    
    def test_validate_connection_failure(self):
        """Testa falha na validação de conexão."""
        connection = MockConnection(self.config)
        connection.is_valid = False
        
        result = self.factory.validate_connection(connection)
        assert result is False
    
    def test_close_connection(self):
        """Testa fechamento de conexão."""
        connection = MockConnection(self.config)
        
        self.factory.close_connection(connection)
        assert connection.is_valid is False

class TestConnectionPool:
    """Testes para ConnectionPool."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.connection_config = ConnectionConfig()
        self.pool_config = PoolConfig(
            min_size=2,
            max_size=5,
            initial_size=2
        )
        self.pool = ConnectionPool(self.connection_config, self.pool_config)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if hasattr(self, 'pool'):
            self.pool.close()
    
    def test_connection_pool_initialization(self):
        """Testa inicialização do pool."""
        assert self.pool.connection_config == self.connection_config
        assert self.pool.pool_config == self.pool_config
        assert len(self.pool.connections) >= self.pool_config.initial_size
        assert self.pool.running is True
    
    def test_acquire_connection_success(self):
        """Testa aquisição bem-sucedida de conexão."""
        connection = self.pool.acquire()
        
        assert connection is not None
        assert isinstance(connection, MockConnection)
        assert len(self.pool.active_connections) == 1
        assert self.pool.metrics.total_acquires == 1
    
    def test_acquire_connection_timeout(self):
        """Testa timeout na aquisição de conexão."""
        # Adquire todas as conexões disponíveis
        connections = []
        for _ in range(self.pool_config.max_size):
            conn = self.pool.acquire()
            if conn:
                connections.append(conn)
        
        # Tenta adquirir mais uma (deve falhar)
        connection = self.pool.acquire(timeout=1)
        assert connection is None
        assert self.pool.metrics.acquire_timeouts == 1
    
    def test_release_connection(self):
        """Testa liberação de conexão."""
        connection = self.pool.acquire()
        assert connection is not None
        
        initial_active = len(self.pool.active_connections)
        initial_idle = self.pool.metrics.idle_connections
        
        self.pool.release(connection)
        
        assert len(self.pool.active_connections) == initial_active - 1
        assert self.pool.metrics.idle_connections == initial_idle + 1
        assert self.pool.metrics.total_releases == 1
    
    def test_connection_recycling_lifetime(self):
        """Testa recycling por tempo de vida."""
        # Cria conexão com tempo de vida muito curto
        self.pool.pool_config.max_lifetime = 0.1  # 100ms
        
        connection = self.pool.acquire()
        assert connection is not None
        
        # Aguarda expiração
        time.sleep(0.2)
        
        initial_total = len(self.pool.connections)
        self.pool.release(connection)
        
        # Verifica se foi reciclada
        assert len(self.pool.connections) < initial_total
    
    def test_connection_recycling_idle_time(self):
        """Testa recycling por tempo idle."""
        # Cria conexão com tempo idle muito curto
        self.pool.pool_config.max_idle_time = 0.1  # 100ms
        
        connection = self.pool.acquire()
        assert connection is not None
        
        # Simula uso antigo
        for conn_info in self.pool.connections.values():
            if conn_info.connection == connection:
                conn_info.last_used = time.time() - 1.0  # 1 segundo atrás
                break
        
        initial_total = len(self.pool.connections)
        self.pool.release(connection)
        
        # Verifica se foi reciclada
        assert len(self.pool.connections) < initial_total
    
    def test_connection_recycling_error_count(self):
        """Testa recycling por número de erros."""
        connection = self.pool.acquire()
        assert connection is not None
        
        # Simula múltiplos erros
        for conn_info in self.pool.connections.values():
            if conn_info.connection == connection:
                conn_info.error_count = 5  # Mais que o limite
                break
        
        initial_total = len(self.pool.connections)
        self.pool.release(connection)
        
        # Verifica se foi reciclada
        assert len(self.pool.connections) < initial_total
    
    def test_health_check_worker(self):
        """Testa worker de health check."""
        # Simula conexão quebrada
        connection = self.pool.acquire()
        assert connection is not None
        
        # Quebra a conexão
        connection.is_valid = False
        
        self.pool.release(connection)
        
        # Executa health check manualmente
        self.pool._perform_health_checks()
        
        # Verifica se conexão foi marcada como quebrada
        for conn_info in self.pool.connections.values():
            if conn_info.connection == connection:
                assert conn_info.state == ConnectionState.BROKEN
                break
    
    def test_pool_resize(self):
        """Testa redimensionamento do pool."""
        initial_size = len(self.pool.connections)
        
        # Redimensiona para tamanho maior
        self.pool.resize_pool(min_size=10, max_size=15)
        
        assert self.pool.pool_config.min_size == 10
        assert self.pool.pool_config.max_size == 15
        assert len(self.pool.connections) >= 10
    
    def test_get_pool_status(self):
        """Testa obtenção de status do pool."""
        status = self.pool.get_pool_status()
        
        assert "total_connections" in status
        assert "active_connections" in status
        assert "idle_connections" in status
        assert "broken_connections" in status
        assert "pool_utilization" in status
        assert "connection_efficiency" in status
        assert "avg_acquire_time" in status
        assert "avg_release_time" in status
        assert "health_check_failures" in status
        assert "acquire_timeouts" in status
    
    def test_get_detailed_metrics(self):
        """Testa obtenção de métricas detalhadas."""
        metrics = self.pool.get_detailed_metrics()
        
        assert isinstance(metrics, PoolMetrics)
        assert metrics.total_connections >= 0
        assert metrics.active_connections >= 0
        assert metrics.idle_connections >= 0
        assert metrics.broken_connections >= 0
        assert metrics.total_acquires >= 0
        assert metrics.total_releases >= 0
        assert metrics.total_creates >= 0
        assert metrics.total_destroys >= 0
    
    def test_health_check(self):
        """Testa health check do pool."""
        health = self.pool.health_check()
        
        assert "status" in health
        assert "pool_size" in health
        assert "active_connections" in health
        assert "utilization" in health
        assert "last_health_check" in health
        assert "background_threads" in health
        assert health["status"] == "healthy"
    
    def test_concurrent_access(self):
        """Testa acesso concorrente ao pool."""
        def worker():
            for _ in range(10):
                connection = self.pool.acquire()
                if connection:
                    time.sleep(0.01)
                    self.pool.release(connection)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Verifica que não houve race conditions
        assert self.pool.metrics.total_acquires == self.pool.metrics.total_releases

class TestConnectionContextManager:
    """Testes para context manager de conexão."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.connection_config = ConnectionConfig()
        self.pool_config = PoolConfig(
            min_size=2,
            max_size=5,
            initial_size=2
        )
        self.pool = ConnectionPool(self.connection_config, self.pool_config)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if hasattr(self, 'pool'):
            self.pool.close()
    
    def test_get_connection_context_manager_success(self):
        """Testa context manager com sucesso."""
        with get_connection(self.pool) as connection:
            assert connection is not None
            assert isinstance(connection, MockConnection)
            assert len(self.pool.active_connections) == 1
        
        # Verifica que foi liberada
        assert len(self.pool.active_connections) == 0
    
    def test_get_connection_context_manager_failure(self):
        """Testa context manager com falha."""
        # Esgota o pool
        connections = []
        for _ in range(self.pool_config.max_size):
            conn = self.pool.acquire()
            if conn:
                connections.append(conn)
        
        # Tenta usar context manager (deve falhar)
        try:
            with get_connection(self.pool, timeout=1) as connection:
                assert False, "Deveria ter falhado"
        except Exception as e:
            assert "Failed to acquire connection" in str(e)
        
        # Libera conexões
        for conn in connections:
            self.pool.release(conn)
    
    def test_get_connection_context_manager_exception(self):
        """Testa context manager com exceção."""
        try:
            with get_connection(self.pool) as connection:
                assert connection is not None
                raise Exception("Test exception")
        except Exception as e:
            assert "Test exception" in str(e)
        
        # Verifica que conexão foi liberada mesmo com exceção
        assert len(self.pool.active_connections) == 0

class TestConnectionPoolFactory:
    """Testes para factory de pool de conexões."""
    
    def test_create_connection_pool(self):
        """Testa criação de pool de conexões."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig()
        
        pool = create_connection_pool(connection_config, pool_config)
        
        assert isinstance(pool, ConnectionPool)
        assert pool.connection_config == connection_config
        assert pool.pool_config == pool_config
        
        pool.close()
    
    def test_get_global_pool(self):
        """Testa obtenção do pool global."""
        # Limpa pool global
        set_global_pool(None)
        
        pool = get_global_pool()
        
        assert isinstance(pool, ConnectionPool)
        assert pool is get_global_pool()  # Mesma instância
    
    def test_set_global_pool(self):
        """Testa definição do pool global."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig()
        custom_pool = ConnectionPool(connection_config, pool_config)
        
        set_global_pool(custom_pool)
        
        assert get_global_pool() is custom_pool
        
        custom_pool.close()

class TestPoolMetrics:
    """Testes para métricas do pool."""
    
    def test_pool_metrics_initialization(self):
        """Testa inicialização das métricas."""
        metrics = PoolMetrics()
        
        assert metrics.total_connections == 0
        assert metrics.active_connections == 0
        assert metrics.idle_connections == 0
        assert metrics.broken_connections == 0
        assert metrics.total_acquires == 0
        assert metrics.total_releases == 0
        assert metrics.total_creates == 0
        assert metrics.total_destroys == 0
        assert metrics.acquire_timeouts == 0
        assert metrics.health_check_failures == 0
        assert metrics.connection_errors == 0
        assert metrics.avg_acquire_time == 0.0
        assert metrics.avg_release_time == 0.0
        assert metrics.avg_health_check_time == 0.0
        assert metrics.pool_utilization == 0.0
        assert metrics.connection_efficiency == 0.0

class TestEdgeCases:
    """Testes para casos extremos."""
    
    def test_pool_with_zero_size(self):
        """Testa pool com tamanho zero."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(
            min_size=0,
            max_size=0,
            initial_size=0
        )
        
        pool = ConnectionPool(connection_config, pool_config)
        
        connection = pool.acquire(timeout=1)
        assert connection is None
        
        pool.close()
    
    def test_pool_with_very_large_size(self):
        """Testa pool com tamanho muito grande."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(
            min_size=100,
            max_size=1000,
            initial_size=100
        )
        
        pool = ConnectionPool(connection_config, pool_config)
        
        # Deve conseguir criar muitas conexões
        connections = []
        for _ in range(50):
            conn = pool.acquire()
            if conn:
                connections.append(conn)
        
        assert len(connections) == 50
        
        # Libera conexões
        for conn in connections:
            pool.release(conn)
        
        pool.close()
    
    def test_release_nonexistent_connection(self):
        """Testa liberação de conexão inexistente."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig()
        pool = ConnectionPool(connection_config, pool_config)
        
        # Tenta liberar conexão que não existe no pool
        fake_connection = MockConnection(connection_config)
        pool.release(fake_connection)
        
        # Não deve causar erro
        assert len(pool.connections) == pool_config.initial_size
        
        pool.close()

def run_all_tests():
    """Executa todos os testes."""
    test_classes = [
        TestConnectionConfig,
        TestPoolConfig,
        TestMockConnection,
        TestConnectionFactory,
        TestConnectionPool,
        TestConnectionContextManager,
        TestConnectionPoolFactory,
        TestPoolMetrics,
        TestEdgeCases
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        test_instance = test_class()
        
        # Executa todos os métodos que começam com 'test_'
        for method_name in dir(test_instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    # Setup se existir
                    if hasattr(test_instance, 'setup_method'):
                        test_instance.setup_method()
                    
                    # Executa o teste
                    getattr(test_instance, method_name)()
                    passed_tests += 1
                    print(f"✅ {test_class.__name__}.{method_name} - PASSED")
                except Exception as e:
                    print(f"❌ {test_class.__name__}.{method_name} - FAILED: {str(e)}")
                finally:
                    # Teardown se existir
                    if hasattr(test_instance, 'teardown_method'):
                        test_instance.teardown_method()
    
    print(f"\n📊 RESULTADO DOS TESTES:")
    print(f"Total de testes: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Testes falharam: {total_tests - passed_tests}")
    print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 