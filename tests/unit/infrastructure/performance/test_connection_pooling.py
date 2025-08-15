"""
🔧 Testes Avançados - Connection Pooling Optimization - Omni Keywords Finder

Tracing ID: TEST_INT_008_CONNECTION_POOLING_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Testes avançados para o sistema de connection pooling com cobertura de:
- Integração com diferentes tipos de banco
- Concorrência e race conditions
- Falhas e recuperação
- Observabilidade e métricas
- Edge cases e cenários extremos
"""

import pytest
import time
import threading
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional, Any
import queue
import weakref

from infrastructure.performance.connection_pooling import (
    ConnectionPool, ConnectionFactory, ConnectionConfig, PoolConfig,
    ConnectionState, PoolStrategy, ConnectionInfo, PoolMetrics,
    MockConnection, get_connection, create_connection_pool,
    get_global_pool, set_global_pool
)


class TestConnectionFactory:
    """Testes para ConnectionFactory."""
    
    @pytest.fixture
    def connection_config(self):
        """Configuração de conexão para testes."""
        return ConnectionConfig(
            host="test-host",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10
        )
    
    @pytest.fixture
    def factory(self, connection_config):
        """Factory de conexões para testes."""
        return ConnectionFactory(connection_config)
    
    def test_create_connection_success(self, factory):
        """Testa criação bem-sucedida de conexão."""
        connection_id, connection = factory.create_connection()
        
        assert connection_id.startswith("conn_")
        assert connection is not None
        assert hasattr(connection, 'close')
        assert hasattr(connection, 'execute')
    
    def test_create_connection_thread_safe(self, factory):
        """Testa thread safety na criação de conexões."""
        results = []
        errors = []
        
        def create_conn():
            try:
                conn_id, conn = factory.create_connection()
                results.append((conn_id, conn))
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=create_conn) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 10
        assert len(errors) == 0
        # Verifica se IDs são únicos
        connection_ids = [r[0] for r in results]
        assert len(set(connection_ids)) == 10
    
    @patch('infrastructure.performance.connection_pooling.psycopg2')
    def test_create_real_connection_postgresql(self, mock_psycopg2, factory):
        """Testa criação de conexão PostgreSQL real."""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        # Simula criação real
        connection = factory._create_real_connection()
        
        assert connection == mock_connection
        mock_psycopg2.connect.assert_called_once()
    
    def test_validate_connection_success(self, factory):
        """Testa validação bem-sucedida de conexão."""
        connection = MockConnection(factory.config)
        assert factory.validate_connection(connection) is True
    
    def test_validate_connection_failure(self, factory):
        """Testa falha na validação de conexão."""
        connection = Mock()
        connection.execute.side_effect = Exception("Connection broken")
        
        assert factory.validate_connection(connection) is False
    
    def test_close_connection_success(self, factory):
        """Testa fechamento bem-sucedido de conexão."""
        connection = MockConnection(factory.config)
        factory.close_connection(connection)
        # Verifica se close foi chamado
        assert connection.closed is True


class TestConnectionPool:
    """Testes para ConnectionPool."""
    
    @pytest.fixture
    def connection_config(self):
        """Configuração de conexão para testes."""
        return ConnectionConfig(
            host="test-host",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
    
    @pytest.fixture
    def pool_config(self):
        """Configuração de pool para testes."""
        return PoolConfig(
            min_size=2,
            max_size=5,
            initial_size=3,
            acquire_timeout=5,
            health_check_interval=10,
            max_lifetime=60,
            max_idle_time=30
        )
    
    @pytest.fixture
    def pool(self, connection_config, pool_config):
        """Pool de conexões para testes."""
        return ConnectionPool(connection_config, pool_config)
    
    def test_pool_initialization(self, pool):
        """Testa inicialização correta do pool."""
        status = pool.get_pool_status()
        
        assert status["total_connections"] == 3  # initial_size
        assert status["active_connections"] == 0
        assert status["idle_connections"] == 3
        assert status["broken_connections"] == 0
        assert status["pool_size"] == 3
        assert status["max_size"] == 5
        assert status["min_size"] == 2
    
    def test_acquire_connection_success(self, pool):
        """Testa aquisição bem-sucedida de conexão."""
        connection = pool.acquire()
        
        assert connection is not None
        assert hasattr(connection, 'close')
        assert hasattr(connection, 'execute')
        
        status = pool.get_pool_status()
        assert status["active_connections"] == 1
        assert status["idle_connections"] == 2
    
    def test_acquire_connection_timeout(self, pool):
        """Testa timeout na aquisição de conexão."""
        # Adquire todas as conexões disponíveis
        connections = []
        for _ in range(3):
            conn = pool.acquire()
            connections.append(conn)
        
        # Tenta adquirir mais uma (deve falhar com timeout)
        start_time = time.time()
        connection = pool.acquire(timeout=1)
        end_time = time.time()
        
        assert connection is None
        assert end_time - start_time >= 1.0
        
        # Libera conexões
        for conn in connections:
            pool.release(conn)
    
    def test_release_connection_success(self, pool):
        """Testa liberação bem-sucedida de conexão."""
        connection = pool.acquire()
        pool.release(connection)
        
        status = pool.get_pool_status()
        assert status["active_connections"] == 0
        assert status["idle_connections"] == 3
    
    def test_concurrent_acquire_release(self, pool):
        """Testa concorrência na aquisição e liberação de conexões."""
        results = []
        errors = []
        
        def worker():
            try:
                for _ in range(5):
                    conn = pool.acquire(timeout=2)
                    if conn:
                        time.sleep(0.1)  # Simula uso
                        pool.release(conn)
                        results.append("success")
                    else:
                        results.append("timeout")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 15  # 3 threads * 5 operações
        
        status = pool.get_pool_status()
        assert status["active_connections"] == 0
        assert status["idle_connections"] == 3
    
    def test_connection_recycling(self, pool):
        """Testa reciclagem de conexões expiradas."""
        # Adquire e libera uma conexão
        connection = pool.acquire()
        conn_info = pool._connections[connection]
        conn_info.created_at = time.time() - 70  # Mais que max_lifetime
        pool.release(connection)
        
        # Força reciclagem
        pool._recycle_expired_connections()
        
        status = pool.get_pool_status()
        assert status["broken_connections"] == 1
    
    def test_health_check_failure(self, pool):
        """Testa falha no health check."""
        # Adquire uma conexão
        connection = pool.acquire()
        conn_info = pool._connections[connection]
        
        # Simula falha no health check
        conn_info.connection.execute.side_effect = Exception("Health check failed")
        
        # Executa health check
        pool._perform_health_checks()
        
        # Verifica se conexão foi marcada como broken
        assert conn_info.state == ConnectionState.BROKEN
        
        pool.release(connection)
    
    def test_pool_resize(self, pool):
        """Testa redimensionamento do pool."""
        # Redimensiona para tamanho menor
        pool.resize_pool(min_size=1, max_size=3)
        
        status = pool.get_pool_status()
        assert status["min_size"] == 1
        assert status["max_size"] == 3
        
        # Redimensiona para tamanho maior
        pool.resize_pool(min_size=5, max_size=10)
        
        status = pool.get_pool_status()
        assert status["min_size"] == 5
        assert status["max_size"] == 10
        assert status["total_connections"] >= 5  # Deve criar conexões adicionais
    
    def test_pool_metrics(self, pool):
        """Testa coleta de métricas do pool."""
        # Executa algumas operações
        conn1 = pool.acquire()
        conn2 = pool.acquire()
        pool.release(conn1)
        conn3 = pool.acquire()
        pool.release(conn2)
        pool.release(conn3)
        
        metrics = pool.get_detailed_metrics()
        
        assert metrics.total_connections == 3
        assert metrics.total_acquires == 3
        assert metrics.total_releases == 3
        assert metrics.active_connections == 0
        assert metrics.idle_connections == 3
        assert metrics.pool_utilization == 0.0
    
    def test_pool_close(self, pool):
        """Testa fechamento do pool."""
        # Adquire algumas conexões
        conn1 = pool.acquire()
        conn2 = pool.acquire()
        
        # Fecha o pool
        pool.close()
        
        # Verifica se conexões foram fechadas
        assert conn1.closed is True
        assert conn2.closed is True
        
        # Verifica se pool está fechado
        status = pool.get_pool_status()
        assert status["total_connections"] == 0
        assert status["active_connections"] == 0
        assert status["idle_connections"] == 0


class TestConnectionPoolContextManager:
    """Testes para context manager de conexões."""
    
    @pytest.fixture
    def pool(self):
        """Pool para testes do context manager."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(min_size=2, max_size=5, initial_size=2)
        return ConnectionPool(connection_config, pool_config)
    
    def test_get_connection_context_manager(self, pool):
        """Testa uso do context manager para conexões."""
        with get_connection(pool) as connection:
            assert connection is not None
            assert hasattr(connection, 'close')
            assert hasattr(connection, 'execute')
            
            status = pool.get_pool_status()
            assert status["active_connections"] == 1
        
        # Verifica se conexão foi liberada automaticamente
        status = pool.get_pool_status()
        assert status["active_connections"] == 0
        assert status["idle_connections"] == 2
    
    def test_get_connection_timeout(self, pool):
        """Testa timeout no context manager."""
        # Adquire todas as conexões
        connections = []
        for _ in range(2):
            conn = pool.acquire()
            connections.append(conn)
        
        # Tenta usar context manager com timeout
        start_time = time.time()
        with get_connection(pool, timeout=1) as connection:
            assert connection is None
        end_time = time.time()
        
        assert end_time - start_time >= 1.0
        
        # Libera conexões
        for conn in connections:
            pool.release(conn)


class TestConnectionPoolFactory:
    """Testes para factory de pools."""
    
    def test_create_connection_pool(self):
        """Testa criação de pool via factory."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(min_size=2, max_size=5, initial_size=2)
        
        pool = create_connection_pool(connection_config, pool_config)
        
        assert isinstance(pool, ConnectionPool)
        assert pool.config == pool_config
        assert pool.connection_config == connection_config
    
    def test_global_pool_management(self):
        """Testa gerenciamento do pool global."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(min_size=1, max_size=3, initial_size=1)
        
        pool = create_connection_pool(connection_config, pool_config)
        set_global_pool(pool)
        
        global_pool = get_global_pool()
        assert global_pool == pool
        
        # Testa uso do pool global
        with get_connection(global_pool) as connection:
            assert connection is not None


class TestConnectionPoolEdgeCases:
    """Testes para edge cases e cenários extremos."""
    
    @pytest.fixture
    def pool(self):
        """Pool para testes de edge cases."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(
            min_size=1,
            max_size=2,
            initial_size=1,
            acquire_timeout=1,
            health_check_interval=5,
            max_lifetime=30,
            max_idle_time=15
        )
        return ConnectionPool(connection_config, pool_config)
    
    def test_pool_exhaustion_recovery(self, pool):
        """Testa recuperação após esgotamento do pool."""
        # Esgota o pool
        conn1 = pool.acquire()
        conn2 = pool.acquire()
        
        # Tenta adquirir mais uma (deve falhar)
        conn3 = pool.acquire(timeout=1)
        assert conn3 is None
        
        # Libera uma conexão
        pool.release(conn1)
        
        # Agora deve conseguir adquirir
        conn3 = pool.acquire()
        assert conn3 is not None
        
        pool.release(conn2)
        pool.release(conn3)
    
    def test_connection_failure_handling(self, pool):
        """Testa tratamento de falhas de conexão."""
        # Simula falha na criação de conexão
        with patch.object(pool.factory, 'create_connection') as mock_create:
            mock_create.side_effect = Exception("Connection failed")
            
            # Tenta criar conexão adicional
            pool._create_connection()
            
            # Verifica se erro foi tratado
            status = pool.get_pool_status()
            assert status["total_connections"] == 1  # Mantém conexões existentes
    
    def test_rapid_acquire_release_cycle(self, pool):
        """Testa ciclo rápido de aquisição/liberação."""
        for _ in range(100):
            connection = pool.acquire()
            assert connection is not None
            pool.release(connection)
        
        status = pool.get_pool_status()
        assert status["active_connections"] == 0
        assert status["idle_connections"] == 1
    
    def test_pool_with_zero_connections(self):
        """Testa pool com zero conexões iniciais."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(min_size=0, max_size=2, initial_size=0)
        
        pool = ConnectionPool(connection_config, pool_config)
        
        status = pool.get_pool_status()
        assert status["total_connections"] == 0
        assert status["idle_connections"] == 0
        
        # Deve conseguir criar conexão sob demanda
        connection = pool.acquire()
        assert connection is not None
        
        pool.release(connection)
    
    def test_pool_with_single_connection(self):
        """Testa pool com apenas uma conexão."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(min_size=1, max_size=1, initial_size=1)
        
        pool = ConnectionPool(connection_config, pool_config)
        
        # Adquire a única conexão
        conn1 = pool.acquire()
        assert conn1 is not None
        
        # Tenta adquirir mais uma (deve falhar)
        conn2 = pool.acquire(timeout=1)
        assert conn2 is None
        
        # Libera e tenta novamente
        pool.release(conn1)
        conn2 = pool.acquire()
        assert conn2 is not None
        
        pool.release(conn2)


class TestConnectionPoolObservability:
    """Testes para observabilidade e métricas."""
    
    @pytest.fixture
    def pool_with_metrics(self):
        """Pool com métricas habilitadas."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(
            min_size=2,
            max_size=5,
            initial_size=2,
            enable_metrics=True,
            enable_logging=True
        )
        return ConnectionPool(connection_config, pool_config)
    
    def test_metrics_collection(self, pool_with_metrics):
        """Testa coleta de métricas detalhadas."""
        # Executa operações para gerar métricas
        conn1 = pool_with_metrics.acquire()
        time.sleep(0.1)
        pool_with_metrics.release(conn1)
        
        conn2 = pool_with_metrics.acquire()
        time.sleep(0.1)
        pool_with_metrics.release(conn2)
        
        metrics = pool_with_metrics.get_detailed_metrics()
        
        assert metrics.total_acquires == 2
        assert metrics.total_releases == 2
        assert metrics.avg_acquire_time > 0
        assert metrics.avg_release_time > 0
        assert metrics.pool_utilization >= 0
        assert metrics.connection_efficiency >= 0
    
    def test_health_check_metrics(self, pool_with_metrics):
        """Testa métricas de health check."""
        # Executa health check
        pool_with_metrics._perform_health_checks()
        
        metrics = pool_with_metrics.get_detailed_metrics()
        assert metrics.avg_health_check_time >= 0
    
    def test_error_metrics(self, pool_with_metrics):
        """Testa métricas de erro."""
        # Simula erro na aquisição
        with patch.object(pool_with_metrics, '_get_idle_connection') as mock_get:
            mock_get.return_value = None
            
            # Tenta adquirir com timeout
            connection = pool_with_metrics.acquire(timeout=1)
            assert connection is None
        
        metrics = pool_with_metrics.get_detailed_metrics()
        assert metrics.acquire_timeouts >= 1


class TestConnectionPoolIntegration:
    """Testes de integração para connection pooling."""
    
    def test_pool_with_real_database_simulation(self):
        """Testa pool com simulação de banco real."""
        connection_config = ConnectionConfig(
            host="localhost",
            port=5432,
            database="test_db"
        )
        pool_config = PoolConfig(
            min_size=3,
            max_size=10,
            initial_size=3,
            health_check_interval=30,
            max_lifetime=300
        )
        
        pool = create_connection_pool(connection_config, pool_config)
        
        # Simula operações de banco
        operations = []
        for i in range(5):
            with get_connection(pool) as conn:
                # Simula query
                result = conn.execute(f"SELECT {i}")
                operations.append(result)
        
        assert len(operations) == 5
        
        # Verifica métricas finais
        metrics = pool.get_detailed_metrics()
        assert metrics.total_acquires == 5
        assert metrics.total_releases == 5
        assert metrics.active_connections == 0
        
        pool.close()
    
    def test_pool_under_load(self):
        """Testa pool sob carga."""
        connection_config = ConnectionConfig()
        pool_config = PoolConfig(
            min_size=5,
            max_size=20,
            initial_size=5,
            acquire_timeout=5
        )
        
        pool = create_connection_pool(connection_config, pool_config)
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(10):
                    with get_connection(pool) as conn:
                        # Simula operação
                        time.sleep(0.01)
                        result = f"worker_{worker_id}_op_{i}"
                        results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Inicia múltiplos workers
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 50  # 5 workers * 10 operações
        
        # Verifica se pool se comportou adequadamente
        metrics = pool.get_detailed_metrics()
        assert metrics.total_acquires == 50
        assert metrics.total_releases == 50
        assert metrics.active_connections == 0
        
        pool.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 