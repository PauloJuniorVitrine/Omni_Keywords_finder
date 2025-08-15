# 📋 Testes para Multi-Region Database Manager
# Tracing ID: TEST_MULTI_REGION_DB_010_20250127
# Versão: 1.0
# Data: 2025-01-27
# Objetivo: Testes para gerenciamento de database multi-region

"""
Testes para Multi-Region Database Manager

Testa funcionalidades de replicação, failover e balanceamento de carga.
"""

import pytest
import asyncio
import tempfile
import yaml
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import psycopg2
from psycopg2.pool import SimpleConnectionPool

from infrastructure.database.multi_region_db import (
    MultiRegionDatabaseManager,
    DatabaseInstance,
    DatabaseRole,
    DatabaseStatus,
    DatabaseMetrics,
    get_db_manager,
    close_db_manager
)

class TestDatabaseInstance:
    """Testes para a classe DatabaseInstance"""
    
    def test_valid_instance_creation(self):
        """Testa criação de instância válida"""
        instance = DatabaseInstance(
            name="test_primary",
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            role=DatabaseRole.PRIMARY,
            region="us-east-1",
            priority=0
        )
        
        assert instance.name == "test_primary"
        assert instance.host == "localhost"
        assert instance.port == 5432
        assert instance.database == "test_db"
        assert instance.username == "test_user"
        assert instance.password == "test_pass"
        assert instance.role == DatabaseRole.PRIMARY
        assert instance.region == "us-east-1"
        assert instance.priority == 0
    
    def test_invalid_port(self):
        """Testa validação de porta inválida"""
        with pytest.raises(ValueError, match="Porta deve estar entre 1 e 65535"):
            DatabaseInstance(
                name="test",
                host="localhost",
                port=0,
                database="test_db",
                username="test_user",
                password="test_pass",
                role=DatabaseRole.PRIMARY,
                region="us-east-1",
                priority=0
            )
    
    def test_invalid_priority(self):
        """Testa validação de prioridade inválida"""
        with pytest.raises(ValueError, match="Priority deve ser >= 0"):
            DatabaseInstance(
                name="test",
                host="localhost",
                port=5432,
                database="test_db",
                username="test_user",
                password="test_pass",
                role=DatabaseRole.PRIMARY,
                region="us-east-1",
                priority=-1
            )
    
    def test_missing_required_fields(self):
        """Testa validação de campos obrigatórios"""
        with pytest.raises(ValueError, match="Host, database e username são obrigatórios"):
            DatabaseInstance(
                name="test",
                host="",
                port=5432,
                database="",
                username="",
                password="test_pass",
                role=DatabaseRole.PRIMARY,
                region="us-east-1",
                priority=0
            )

class TestDatabaseMetrics:
    """Testes para a classe DatabaseMetrics"""
    
    def test_metrics_creation(self):
        """Testa criação de métricas"""
        now = datetime.now()
        metrics = DatabaseMetrics(
            response_time=0.1,
            connection_count=5,
            active_queries=2,
            replication_lag=0.05,
            last_check=now,
            status=DatabaseStatus.HEALTHY
        )
        
        assert metrics.response_time == 0.1
        assert metrics.connection_count == 5
        assert metrics.active_queries == 2
        assert metrics.replication_lag == 0.05
        assert metrics.last_check == now
        assert metrics.status == DatabaseStatus.HEALTHY

class TestMultiRegionDatabaseManager:
    """Testes para o MultiRegionDatabaseManager"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Cria arquivo de configuração temporário"""
        config = {
            'database': {
                'primary': {
                    'host': 'primary-host',
                    'port': 5432,
                    'database': 'test_db',
                    'username': 'test_user',
                    'password': 'test_pass',
                    'region': 'us-east-1',
                    'connection_timeout': 30,
                    'max_connections': 20,
                    'min_connections': 5
                },
                'replicas': [
                    {
                        'host': 'replica1-host',
                        'port': 5432,
                        'database': 'test_db',
                        'username': 'test_user',
                        'password': 'test_pass',
                        'region': 'us-west-2',
                        'priority': 1,
                        'connection_timeout': 30,
                        'max_connections': 15,
                        'min_connections': 3
                    },
                    {
                        'host': 'replica2-host',
                        'port': 5432,
                        'database': 'test_db',
                        'username': 'test_user',
                        'password': 'test_pass',
                        'region': 'eu-west-1',
                        'priority': 2,
                        'connection_timeout': 30,
                        'max_connections': 15,
                        'min_connections': 3
                    }
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            yield f.name
        
        os.unlink(f.name)
    
    @pytest.fixture
    def mock_pool(self):
        """Mock para SimpleConnectionPool"""
        with patch('infrastructure.database.multi_region_db.SimpleConnectionPool') as mock:
            pool_instance = Mock()
            mock.return_value = pool_instance
            yield mock
    
    @pytest.fixture
    def db_manager(self, temp_config_file, mock_pool):
        """Cria instância do gerenciador de banco de dados"""
        with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
            manager = MultiRegionDatabaseManager(temp_config_file)
            yield manager
            # Cleanup
            for pool in manager.connection_pools.values():
                pool.closeall()
    
    def test_load_configuration_from_file(self, temp_config_file, mock_pool):
        """Testa carregamento de configuração do arquivo"""
        with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
            manager = MultiRegionDatabaseManager(temp_config_file)
            
            assert len(manager.instances) == 3
            assert "primary" in manager.instances
            assert "replica_1" in manager.instances
            assert "replica_2" in manager.instances
            
            # Verifica configuração da primary
            primary = manager.instances["primary"]
            assert primary.host == "primary-host"
            assert primary.role == DatabaseRole.PRIMARY
            assert primary.region == "us-east-1"
            
            # Verifica configuração das réplicas
            replica1 = manager.instances["replica_1"]
            assert replica1.host == "replica1-host"
            assert replica1.role == DatabaseRole.REPLICA
            assert replica1.region == "us-west-2"
            assert replica1.priority == 1
            
            replica2 = manager.instances["replica_2"]
            assert replica2.host == "replica2-host"
            assert replica2.role == DatabaseRole.REPLICA
            assert replica2.region == "eu-west-1"
            assert replica2.priority == 2
    
    def test_load_configuration_from_environment(self, mock_pool):
        """Testa carregamento de configuração do ambiente"""
        env_vars = {
            'DATABASE_PRIMARY_HOST': 'env-primary-host',
            'DATABASE_PRIMARY_PORT': '5432',
            'DATABASE_NAME': 'env_test_db',
            'DATABASE_USERNAME': 'env_test_user',
            'DATABASE_PASSWORD': 'env_test_pass',
            'DATABASE_PRIMARY_REGION': 'us-east-1',
            'DATABASE_REPLICA_HOSTS': 'replica1-host,replica2-host',
            'DATABASE_REPLICA_REGIONS': 'us-west-2,eu-west-1'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
                manager = MultiRegionDatabaseManager("nonexistent.yaml")
                
                assert len(manager.instances) == 3
                assert "primary" in manager.instances
                assert "replica_1" in manager.instances
                assert "replica_2" in manager.instances
                
                primary = manager.instances["primary"]
                assert primary.host == "env-primary-host"
                assert primary.database == "env_test_db"
                assert primary.username == "env_test_user"
    
    def test_initialize_connection_pools(self, db_manager):
        """Testa inicialização dos pools de conexão"""
        assert len(db_manager.connection_pools) == 3
        assert "primary" in db_manager.connection_pools
        assert "replica_1" in db_manager.connection_pools
        assert "replica_2" in db_manager.connection_pools
        
        # Verifica se as métricas foram inicializadas
        assert len(db_manager.metrics) == 3
        for name in ["primary", "replica_1", "replica_2"]:
            assert name in db_manager.metrics
            assert db_manager.metrics[name].status == DatabaseStatus.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_check_instance_health_success(self, db_manager):
        """Testa health check bem-sucedido"""
        # Mock da conexão
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_conn
            
            await db_manager._check_instance_health("primary")
            
            # Verifica se o status foi atualizado
            assert db_manager.metrics["primary"].status == DatabaseStatus.HEALTHY
            assert db_manager.metrics["primary"].response_time > 0
            assert "primary" not in db_manager.failure_counts
    
    @pytest.mark.asyncio
    async def test_check_instance_health_failure(self, db_manager):
        """Testa health check com falha"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_get_conn.side_effect = Exception("Connection failed")
            
            await db_manager._check_instance_health("primary")
            
            # Verifica se o status foi atualizado
            assert db_manager.metrics["primary"].status == DatabaseStatus.UNHEALTHY
            assert db_manager.failure_counts["primary"] == 1
            assert "primary" in db_manager.last_failure_time
    
    @pytest.mark.asyncio
    async def test_trigger_failover(self, db_manager):
        """Testa processo de failover"""
        # Configura falhas na primary
        db_manager.failure_counts["primary"] = 3
        db_manager.metrics["primary"].status = DatabaseStatus.UNHEALTHY
        db_manager.metrics["replica_1"].status = DatabaseStatus.HEALTHY
        
        with patch.object(db_manager, '_promote_replica_to_primary') as mock_promote:
            await db_manager._trigger_failover()
            
            mock_promote.assert_called_once_with("replica_1")
    
    def test_select_best_replica(self, db_manager):
        """Testa seleção da melhor réplica"""
        # Configura métricas das réplicas
        db_manager.metrics["replica_1"].status = DatabaseStatus.HEALTHY
        db_manager.metrics["replica_1"].replication_lag = 0.1
        db_manager.metrics["replica_1"].response_time = 0.05
        
        db_manager.metrics["replica_2"].status = DatabaseStatus.HEALTHY
        db_manager.metrics["replica_2"].replication_lag = 0.2
        db_manager.metrics["replica_2"].response_time = 0.1
        
        best_replica = db_manager._select_best_replica()
        
        # replica_1 deve ser selecionada (menor lag e response time)
        assert best_replica == "replica_1"
    
    def test_select_read_replica_round_robin(self, db_manager):
        """Testa seleção de réplica para leitura com round-robin"""
        # Configura réplicas saudáveis
        db_manager.metrics["replica_1"].status = DatabaseStatus.HEALTHY
        db_manager.metrics["replica_2"].status = DatabaseStatus.HEALTHY
        
        # Primeira seleção
        replica1 = db_manager._select_read_replica()
        assert replica1 == "replica_1"
        
        # Segunda seleção (round-robin)
        replica2 = db_manager._select_read_replica()
        assert replica2 == "replica_2"
        
        # Terceira seleção (volta para primeira)
        replica3 = db_manager._select_read_replica()
        assert replica3 == "replica_1"
    
    def test_select_read_replica_least_connections(self, db_manager):
        """Testa seleção de réplica para leitura com least connections"""
        db_manager.load_balancing_strategy = "least_connections"
        
        # Configura réplicas saudáveis com diferentes números de conexões
        db_manager.metrics["replica_1"].status = DatabaseStatus.HEALTHY
        db_manager.metrics["replica_1"].connection_count = 5
        
        db_manager.metrics["replica_2"].status = DatabaseStatus.HEALTHY
        db_manager.metrics["replica_2"].connection_count = 2
        
        # Deve selecionar replica_2 (menos conexões)
        selected = db_manager._select_read_replica()
        assert selected == "replica_2"
    
    def test_select_read_replica_no_healthy_replicas(self, db_manager):
        """Testa seleção quando não há réplicas saudáveis"""
        # Configura todas as réplicas como não saudáveis
        db_manager.metrics["replica_1"].status = DatabaseStatus.UNHEALTHY
        db_manager.metrics["replica_2"].status = DatabaseStatus.UNHEALTHY
        
        # Deve retornar primary
        selected = db_manager._select_read_replica()
        assert selected == "primary"
    
    def test_is_circuit_breaker_open(self, db_manager):
        """Testa verificação de circuit breaker"""
        # Circuit breaker deve estar fechado inicialmente
        assert not db_manager._is_circuit_breaker_open("primary")
        
        # Configura falhas
        db_manager.failure_counts["primary"] = 3
        db_manager.last_failure_time["primary"] = datetime.now()
        
        # Circuit breaker deve estar aberto
        assert db_manager._is_circuit_breaker_open("primary")
        
        # Após timeout, circuit breaker deve fechar
        db_manager.last_failure_time["primary"] = datetime.now() - timedelta(seconds=400)
        assert not db_manager._is_circuit_breaker_open("primary")
    
    def test_get_metrics(self, db_manager):
        """Testa obtenção de métricas"""
        metrics = db_manager.get_metrics()
        
        assert len(metrics) == 3
        assert "primary" in metrics
        assert "replica_1" in metrics
        assert "replica_2" in metrics
        
        # Verifica estrutura das métricas
        primary_metrics = metrics["primary"]
        assert "status" in primary_metrics
        assert "response_time" in primary_metrics
        assert "connection_count" in primary_metrics
        assert "replication_lag" in primary_metrics
        assert "last_check" in primary_metrics
        assert "role" in primary_metrics
        assert "region" in primary_metrics
        assert "priority" in primary_metrics
    
    def test_get_current_primary(self, db_manager):
        """Testa obtenção da primary atual"""
        current_primary = db_manager.get_current_primary()
        assert current_primary == "primary"
    
    def test_get_healthy_replicas(self, db_manager):
        """Testa obtenção de réplicas saudáveis"""
        # Configura status das réplicas
        db_manager.metrics["replica_1"].status = DatabaseStatus.HEALTHY
        db_manager.metrics["replica_2"].status = DatabaseStatus.UNHEALTHY
        
        healthy_replicas = db_manager.get_healthy_replicas()
        assert len(healthy_replicas) == 1
        assert "replica_1" in healthy_replicas
    
    @pytest.mark.asyncio
    async def test_close(self, db_manager):
        """Testa fechamento do gerenciador"""
        await db_manager.close()
        
        # Verifica se os pools foram fechados
        for pool in db_manager.connection_pools.values():
            pool.closeall.assert_called_once()
        
        assert len(db_manager.connection_pools) == 0

class TestSingletonFunctions:
    """Testes para funções singleton"""
    
    @pytest.mark.asyncio
    async def test_get_db_manager_singleton(self):
        """Testa que get_db_manager retorna sempre a mesma instância"""
        with patch('infrastructure.database.multi_region_db.MultiRegionDatabaseManager') as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance
            
            # Primeira chamada
            manager1 = get_db_manager()
            assert manager1 == mock_instance
            
            # Segunda chamada (deve retornar a mesma instância)
            manager2 = get_db_manager()
            assert manager2 == mock_instance
            
            # Verifica que o construtor foi chamado apenas uma vez
            mock_manager.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_db_manager(self):
        """Testa fechamento do gerenciador singleton"""
        with patch('infrastructure.database.multi_region_db.MultiRegionDatabaseManager') as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance
            
            # Obtém instância
            get_db_manager()
            
            # Fecha
            await close_db_manager()
            
            # Verifica se close foi chamado
            mock_instance.close.assert_called_once()

class TestIntegrationScenarios:
    """Testes de cenários de integração"""
    
    @pytest.mark.asyncio
    async def test_failover_scenario(self, temp_config_file, mock_pool):
        """Testa cenário completo de failover"""
        with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
            manager = MultiRegionDatabaseManager(temp_config_file)
            
            # Configura cenário inicial
            manager.metrics["primary"].status = DatabaseStatus.HEALTHY
            manager.metrics["replica_1"].status = DatabaseStatus.HEALTHY
            manager.metrics["replica_2"].status = DatabaseStatus.HEALTHY
            
            # Simula falhas na primary
            for _ in range(3):
                await manager._check_instance_health("primary")
                manager.metrics["primary"].status = DatabaseStatus.UNHEALTHY
            
            # Verifica se failover foi disparado
            with patch.object(manager, '_promote_replica_to_primary') as mock_promote:
                await manager._trigger_failover()
                mock_promote.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_balancing_scenario(self, temp_config_file, mock_pool):
        """Testa cenário de load balancing"""
        with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
            manager = MultiRegionDatabaseManager(temp_config_file)
            
            # Configura réplicas saudáveis
            manager.metrics["replica_1"].status = DatabaseStatus.HEALTHY
            manager.metrics["replica_2"].status = DatabaseStatus.HEALTHY
            
            # Testa round-robin
            replicas_selected = []
            for _ in range(4):
                replica = manager._select_read_replica()
                replicas_selected.append(replica)
            
            # Verifica distribuição round-robin
            assert replicas_selected == ["replica_1", "replica_2", "replica_1", "replica_2"]
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_scenario(self, temp_config_file, mock_pool):
        """Testa cenário de circuit breaker"""
        with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
            manager = MultiRegionDatabaseManager(temp_config_file)
            
            # Simula falhas
            manager.failure_counts["primary"] = 3
            manager.last_failure_time["primary"] = datetime.now()
            
            # Circuit breaker deve estar aberto
            assert manager._is_circuit_breaker_open("primary")
            
            # Simula timeout
            manager.last_failure_time["primary"] = datetime.now() - timedelta(seconds=400)
            
            # Circuit breaker deve estar fechado
            assert not manager._is_circuit_breaker_open("primary")

# Testes de performance
class TestPerformance:
    """Testes de performance"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_performance(self, temp_config_file, mock_pool):
        """Testa performance do pool de conexões"""
        with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
            manager = MultiRegionDatabaseManager(temp_config_file)
            
            # Simula múltiplas conexões simultâneas
            start_time = datetime.now()
            
            # Simula 100 conexões
            for _ in range(100):
                with manager.get_connection("primary"):
                    pass
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Deve completar em menos de 1 segundo
            assert duration < 1.0
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, temp_config_file, mock_pool):
        """Testa performance dos health checks"""
        with patch('infrastructure.database.multi_region_db.asyncio.create_task'):
            manager = MultiRegionDatabaseManager(temp_config_file)
            
            # Mock de conexão rápida
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            
            with patch.object(manager, 'get_connection') as mock_get_conn:
                mock_get_conn.return_value.__enter__.return_value = mock_conn
                
                start_time = datetime.now()
                
                # Executa health checks para todas as instâncias
                await manager._check_all_instances_health()
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Deve completar em menos de 1 segundo
                assert duration < 1.0 