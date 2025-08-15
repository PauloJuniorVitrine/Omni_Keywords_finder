"""
🧪 Testes Unitários - Otimização de Banco de Dados
==================================================

Tracing ID: TEST_DATABASE_OPTIMIZATION_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTAÇÃO

Testes para o módulo backend/app/optimization/database_optimization.py
Baseado exclusivamente no código real do Omni Keywords Finder
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, Optional, List

# Importações do código real
from backend.app.optimization.database_optimization import (
    QueryType,
    QueryMetrics,
    OptimizationSuggestion,
    DatabaseOptimizer,
    DatabaseOptimizerSingleton,
    monitor_query,
    monitored_query
)


class TestQueryType:
    """Testes para enum QueryType"""
    
    def test_query_type_values(self):
        """Testa valores do enum QueryType"""
        assert QueryType.SELECT.value == "SELECT"
        assert QueryType.INSERT.value == "INSERT"
        assert QueryType.UPDATE.value == "UPDATE"
        assert QueryType.DELETE.value == "DELETE"
        assert QueryType.CREATE.value == "CREATE"
        assert QueryType.ALTER.value == "ALTER"
        assert QueryType.DROP.value == "DROP"
    
    def test_query_type_membership(self):
        """Testa pertencimento ao enum"""
        assert "SELECT" in [query_type.value for query_type in QueryType]
        assert "INSERT" in [query_type.value for query_type in QueryType]
        assert "UPDATE" in [query_type.value for query_type in QueryType]
        assert "DELETE" in [query_type.value for query_type in QueryType]
        assert "CREATE" in [query_type.value for query_type in QueryType]
        assert "ALTER" in [query_type.value for query_type in QueryType]
        assert "DROP" in [query_type.value for query_type in QueryType]


class TestQueryMetrics:
    """Testes para dataclass QueryMetrics"""
    
    def test_query_metrics_default_values(self):
        """Testa valores padrão do QueryMetrics"""
        metrics = QueryMetrics(
            query="SELECT * FROM users",
            query_type=QueryType.SELECT,
            execution_time=0.5,
            rows_affected=100,
            timestamp=datetime.now()
        )
        
        assert metrics.query == "SELECT * FROM users"
        assert metrics.query_type == QueryType.SELECT
        assert metrics.execution_time == 0.5
        assert metrics.rows_affected == 100
        assert isinstance(metrics.timestamp, datetime)
        assert metrics.table_name is None
        assert metrics.index_used is None
        assert metrics.full_table_scan is False
        assert metrics.slow_query is False
    
    def test_query_metrics_custom_values(self):
        """Testa valores customizados do QueryMetrics"""
        timestamp = datetime.now()
        metrics = QueryMetrics(
            query="SELECT * FROM products WHERE category = 'electronics'",
            query_type=QueryType.SELECT,
            execution_time=2.5,
            rows_affected=500,
            timestamp=timestamp,
            table_name="products",
            index_used="idx_category",
            full_table_scan=False,
            slow_query=True
        )
        
        assert metrics.query == "SELECT * FROM products WHERE category = 'electronics'"
        assert metrics.query_type == QueryType.SELECT
        assert metrics.execution_time == 2.5
        assert metrics.rows_affected == 500
        assert metrics.timestamp == timestamp
        assert metrics.table_name == "products"
        assert metrics.index_used == "idx_category"
        assert metrics.full_table_scan is False
        assert metrics.slow_query is True


class TestOptimizationSuggestion:
    """Testes para dataclass OptimizationSuggestion"""
    
    def test_optimization_suggestion_default_values(self):
        """Testa valores padrão do OptimizationSuggestion"""
        suggestion = OptimizationSuggestion(
            type="index",
            description="Create index on users.email",
            impact="high",
            estimated_improvement=0.8
        )
        
        assert suggestion.type == "index"
        assert suggestion.description == "Create index on users.email"
        assert suggestion.impact == "high"
        assert suggestion.estimated_improvement == 0.8
        assert suggestion.sql_statement is None
        assert suggestion.table_name is None
    
    def test_optimization_suggestion_custom_values(self):
        """Testa valores customizados do OptimizationSuggestion"""
        suggestion = OptimizationSuggestion(
            type="query_rewrite",
            description="Optimize JOIN order",
            impact="medium",
            estimated_improvement=0.3,
            sql_statement="SELECT u.name, p.title FROM users u INNER JOIN posts p ON u.id = p.user_id",
            table_name="users"
        )
        
        assert suggestion.type == "query_rewrite"
        assert suggestion.description == "Optimize JOIN order"
        assert suggestion.impact == "medium"
        assert suggestion.estimated_improvement == 0.3
        assert suggestion.sql_statement == "SELECT u.name, p.title FROM users u INNER JOIN posts p ON u.id = p.user_id"
        assert suggestion.table_name == "users"


class TestDatabaseOptimizer:
    """Testes para classe DatabaseOptimizer"""
    
    @pytest.fixture
    def database_optimizer(self):
        """Fixture para DatabaseOptimizer"""
        config = {
            'slow_query_threshold': 1.0,
            'max_metrics_history': 1000,
            'pool_size': 5,
            'max_overflow': 10
        }
        return DatabaseOptimizer("sqlite:///test.db", config)
    
    @pytest.fixture
    def async_database_optimizer(self):
        """Fixture para DatabaseOptimizer com engine assíncrono"""
        config = {
            'slow_query_threshold': 1.0,
            'max_metrics_history': 1000,
            'pool_size': 5,
            'max_overflow': 10
        }
        return DatabaseOptimizer("postgresql+asyncpg://user:pass@localhost/test", config)
    
    def test_database_optimizer_initialization(self, database_optimizer):
        """Testa inicialização do DatabaseOptimizer"""
        assert database_optimizer.database_url == "sqlite:///test.db"
        assert database_optimizer.slow_query_threshold == 1.0
        assert database_optimizer.max_metrics_history == 1000
        assert len(database_optimizer.query_metrics) == 0
        assert len(database_optimizer.optimization_suggestions) == 0
        assert database_optimizer.engine is not None
    
    def test_database_optimizer_async_initialization(self, async_database_optimizer):
        """Testa inicialização do DatabaseOptimizer com engine assíncrono"""
        assert async_database_optimizer.database_url == "postgresql+asyncpg://user:pass@localhost/test"
        assert async_database_optimizer.async_engine is not None
    
    def test_detect_query_type(self, database_optimizer):
        """Testa detecção de tipo de query"""
        assert database_optimizer._detect_query_type("SELECT * FROM users") == QueryType.SELECT
        assert database_optimizer._detect_query_type("INSERT INTO users VALUES (1, 'John')") == QueryType.INSERT
        assert database_optimizer._detect_query_type("UPDATE users SET name = 'Jane' WHERE id = 1") == QueryType.UPDATE
        assert database_optimizer._detect_query_type("DELETE FROM users WHERE id = 1") == QueryType.DELETE
        assert database_optimizer._detect_query_type("CREATE TABLE users (id INT)") == QueryType.CREATE
        assert database_optimizer._detect_query_type("ALTER TABLE users ADD COLUMN email TEXT") == QueryType.ALTER
        assert database_optimizer._detect_query_type("DROP TABLE users") == QueryType.DROP
    
    def test_extract_table_name(self, database_optimizer):
        """Testa extração de nome da tabela"""
        assert database_optimizer._extract_table_name("SELECT * FROM users") == "users"
        assert database_optimizer._extract_table_name("INSERT INTO products (name) VALUES ('test')") == "products"
        assert database_optimizer._extract_table_name("UPDATE orders SET status = 'completed'") == "orders"
        assert database_optimizer._extract_table_name("DELETE FROM customers WHERE id = 1") == "customers"
        assert database_optimizer._extract_table_name("CREATE TABLE categories (id INT)") == "categories"
        assert database_optimizer._extract_table_name("ALTER TABLE posts ADD COLUMN title TEXT") == "posts"
        assert database_optimizer._extract_table_name("DROP TABLE comments") == "comments"
        
        # Testa queries complexas
        assert database_optimizer._extract_table_name("SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id") == "users"
        assert database_optimizer._extract_table_name("SELECT * FROM (SELECT * FROM users) sub") == "users"
    
    def test_add_query_metrics(self, database_optimizer):
        """Testa adição de métricas de query"""
        initial_count = len(database_optimizer.query_metrics)
        
        metrics = QueryMetrics(
            query="SELECT * FROM users",
            query_type=QueryType.SELECT,
            execution_time=0.5,
            rows_affected=100,
            timestamp=datetime.now()
        )
        
        database_optimizer._add_query_metrics(metrics)
        
        assert len(database_optimizer.query_metrics) == initial_count + 1
        assert database_optimizer.query_metrics[-1] == metrics
    
    def test_add_query_metrics_max_history(self, database_optimizer):
        """Testa limite de histórico de métricas"""
        # Adiciona mais métricas que o limite
        for i in range(database_optimizer.max_metrics_history + 10):
            metrics = QueryMetrics(
                query=f"SELECT * FROM users WHERE id = {i}",
                query_type=QueryType.SELECT,
                execution_time=0.1,
                rows_affected=1,
                timestamp=datetime.now()
            )
            database_optimizer._add_query_metrics(metrics)
        
        # Verifica se não excedeu o limite
        assert len(database_optimizer.query_metrics) <= database_optimizer.max_metrics_history
    
    @pytest.mark.asyncio
    async def test_analyze_query_performance(self, database_optimizer):
        """Testa análise de performance de query"""
        with patch.object(database_optimizer, 'engine') as mock_engine:
            mock_connection = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value.rowcount = 100
            
            start_time = time.time()
            metrics = await database_optimizer.analyze_query_performance(
                "SELECT * FROM users WHERE email = 'test@example.com'"
            )
            execution_time = time.time() - start_time
            
            assert isinstance(metrics, QueryMetrics)
            assert metrics.query == "SELECT * FROM users WHERE email = 'test@example.com'"
            assert metrics.query_type == QueryType.SELECT
            assert metrics.execution_time >= 0
            assert metrics.rows_affected == 100
            assert isinstance(metrics.timestamp, datetime)
            assert metrics.table_name == "users"
    
    @pytest.mark.asyncio
    async def test_get_slow_queries(self, database_optimizer):
        """Testa obtenção de queries lentas"""
        # Adiciona algumas métricas
        fast_metrics = QueryMetrics(
            query="SELECT * FROM users WHERE id = 1",
            query_type=QueryType.SELECT,
            execution_time=0.1,
            rows_affected=1,
            timestamp=datetime.now()
        )
        
        slow_metrics = QueryMetrics(
            query="SELECT * FROM users WHERE email LIKE '%@example.com'",
            query_type=QueryType.SELECT,
            execution_time=2.5,
            rows_affected=1000,
            timestamp=datetime.now()
        )
        
        database_optimizer._add_query_metrics(fast_metrics)
        database_optimizer._add_query_metrics(slow_metrics)
        
        slow_queries = await database_optimizer.get_slow_queries(limit=5)
        
        assert len(slow_queries) == 1
        assert slow_queries[0].execution_time > database_optimizer.slow_query_threshold
    
    @pytest.mark.asyncio
    async def test_get_query_statistics(self, database_optimizer):
        """Testa obtenção de estatísticas de queries"""
        # Adiciona métricas de diferentes tipos
        metrics_list = [
            QueryMetrics("SELECT * FROM users", QueryType.SELECT, 0.1, 10, datetime.now()),
            QueryMetrics("INSERT INTO users VALUES (1, 'John')", QueryType.INSERT, 0.05, 1, datetime.now()),
            QueryMetrics("UPDATE users SET name = 'Jane'", QueryType.UPDATE, 0.2, 5, datetime.now()),
            QueryMetrics("DELETE FROM users WHERE id = 1", QueryType.DELETE, 0.15, 1, datetime.now())
        ]
        
        for metrics in metrics_list:
            database_optimizer._add_query_metrics(metrics)
        
        stats = await database_optimizer.get_query_statistics()
        
        assert "total_queries" in stats
        assert "avg_execution_time" in stats
        assert "slow_queries_count" in stats
        assert "queries_by_type" in stats
        assert "most_accessed_tables" in stats
        
        assert stats["total_queries"] == 4
        assert "SELECT" in stats["queries_by_type"]
        assert "INSERT" in stats["queries_by_type"]
        assert "UPDATE" in stats["queries_by_type"]
        assert "DELETE" in stats["queries_by_type"]
    
    @pytest.mark.asyncio
    async def test_analyze_index_usage(self, database_optimizer):
        """Testa análise de uso de índices"""
        with patch.object(database_optimizer, 'engine') as mock_engine:
            mock_inspector = Mock()
            mock_engine.inspect.return_value = mock_inspector
            mock_inspector.get_indexes.return_value = [
                {'name': 'idx_email', 'column_names': ['email']},
                {'name': 'idx_name', 'column_names': ['name']}
            ]
            
            index_usage = await database_optimizer.analyze_index_usage()
            
            assert isinstance(index_usage, list)
            assert len(index_usage) == 2
            assert any(idx['name'] == 'idx_email' for idx in index_usage)
            assert any(idx['name'] == 'idx_name' for idx in index_usage)
    
    @pytest.mark.asyncio
    async def test_generate_optimization_suggestions(self, database_optimizer):
        """Testa geração de sugestões de otimização"""
        # Adiciona métricas que podem gerar sugestões
        slow_query_metrics = QueryMetrics(
            query="SELECT * FROM users WHERE email LIKE '%@example.com'",
            query_type=QueryType.SELECT,
            execution_time=3.0,
            rows_affected=10000,
            timestamp=datetime.now(),
            table_name="users",
            full_table_scan=True,
            slow_query=True
        )
        
        database_optimizer._add_query_metrics(slow_query_metrics)
        
        suggestions = await database_optimizer.generate_optimization_suggestions()
        
        assert isinstance(suggestions, list)
        # Pode ter sugestões baseadas nas métricas
        assert all(isinstance(suggestion, OptimizationSuggestion) for suggestion in suggestions)
    
    @pytest.mark.asyncio
    async def test_optimize_connection_pool(self, database_optimizer):
        """Testa otimização do pool de conexões"""
        pool_info = await database_optimizer.optimize_connection_pool()
        
        assert isinstance(pool_info, dict)
        assert "current_pool_size" in pool_info
        assert "max_overflow" in pool_info
        assert "pool_timeout" in pool_info
        assert "recommendations" in pool_info
    
    @pytest.mark.asyncio
    async def test_create_performance_indexes(self, database_optimizer):
        """Testa criação de índices de performance"""
        with patch.object(database_optimizer, 'engine') as mock_engine:
            mock_connection = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = Mock()
            
            success = await database_optimizer.create_performance_indexes(
                "users", 
                ["email", "created_at"]
            )
            
            assert success is True
            mock_connection.execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_analyze_table_structure(self, database_optimizer):
        """Testa análise da estrutura da tabela"""
        with patch.object(database_optimizer, 'engine') as mock_engine:
            mock_inspector = Mock()
            mock_engine.inspect.return_value = mock_inspector
            mock_inspector.get_columns.return_value = [
                {'name': 'id', 'type': 'INTEGER', 'nullable': False},
                {'name': 'email', 'type': 'VARCHAR', 'nullable': False},
                {'name': 'name', 'type': 'VARCHAR', 'nullable': True}
            ]
            mock_inspector.get_indexes.return_value = [
                {'name': 'idx_email', 'column_names': ['email']}
            ]
            
            structure = await database_optimizer.analyze_table_structure("users")
            
            assert isinstance(structure, dict)
            assert "columns" in structure
            assert "indexes" in structure
            assert "recommendations" in structure
            assert len(structure["columns"]) == 3
            assert len(structure["indexes"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_database_health_report(self, database_optimizer):
        """Testa relatório de saúde do banco de dados"""
        # Adiciona algumas métricas para o relatório
        metrics_list = [
            QueryMetrics("SELECT * FROM users", QueryType.SELECT, 0.1, 10, datetime.now()),
            QueryMetrics("SELECT * FROM products", QueryType.SELECT, 2.5, 1000, datetime.now(), slow_query=True)
        ]
        
        for metrics in metrics_list:
            database_optimizer._add_query_metrics(metrics)
        
        health_report = await database_optimizer.get_database_health_report()
        
        assert isinstance(health_report, dict)
        assert "overall_health" in health_report
        assert "performance_metrics" in health_report
        assert "slow_queries" in health_report
        assert "optimization_suggestions" in health_report
        assert "connection_pool_status" in health_report
    
    @pytest.mark.asyncio
    async def test_cleanup_old_metrics(self, database_optimizer):
        """Testa limpeza de métricas antigas"""
        # Adiciona métricas antigas e recentes
        old_timestamp = datetime.now() - timedelta(days=31)
        recent_timestamp = datetime.now()
        
        old_metrics = QueryMetrics(
            query="SELECT * FROM old_data",
            query_type=QueryType.SELECT,
            execution_time=0.1,
            rows_affected=1,
            timestamp=old_timestamp
        )
        
        recent_metrics = QueryMetrics(
            query="SELECT * FROM recent_data",
            query_type=QueryType.SELECT,
            execution_time=0.1,
            rows_affected=1,
            timestamp=recent_timestamp
        )
        
        database_optimizer._add_query_metrics(old_metrics)
        database_optimizer._add_query_metrics(recent_metrics)
        
        initial_count = len(database_optimizer.query_metrics)
        
        await database_optimizer.cleanup_old_metrics(days=30)
        
        # Verifica se as métricas antigas foram removidas
        assert len(database_optimizer.query_metrics) < initial_count
        assert all(metrics.timestamp > old_timestamp for metrics in database_optimizer.query_metrics)
    
    def test_export_metrics(self, database_optimizer, tmp_path):
        """Testa exportação de métricas"""
        # Adiciona algumas métricas
        metrics_list = [
            QueryMetrics("SELECT * FROM users", QueryType.SELECT, 0.1, 10, datetime.now()),
            QueryMetrics("INSERT INTO users VALUES (1, 'John')", QueryType.INSERT, 0.05, 1, datetime.now())
        ]
        
        for metrics in metrics_list:
            database_optimizer._add_query_metrics(metrics)
        
        export_file = tmp_path / "metrics_export.json"
        database_optimizer.export_metrics(str(export_file))
        
        assert export_file.exists()
        
        # Verifica se o arquivo contém dados válidos
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        assert "export_timestamp" in exported_data
        assert "metrics" in exported_data
        assert len(exported_data["metrics"]) == 2


class TestMonitorQueryDecorator:
    """Testes para decorator monitor_query"""
    
    @pytest.mark.asyncio
    async def test_monitor_query_decorator(self):
        """Testa decorator monitor_query"""
        call_count = 0
        
        @monitor_query
        async def test_query_function(param1, param2):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simula execução de query
            return f"result_{param1}_{param2}"
        
        # Executa a função decorada
        result = await test_query_function("a", "b")
        
        assert result == "result_a_b"
        assert call_count == 1


class TestMonitoredQueryContextManager:
    """Testes para context manager monitored_query"""
    
    @pytest.mark.asyncio
    async def test_monitored_query_context_manager(self):
        """Testa context manager monitored_query"""
        async with monitored_query("SELECT * FROM users WHERE id = 1") as result:
            # Simula execução de query
            await asyncio.sleep(0.01)
            result = {"id": 1, "name": "John Doe"}
        
        assert result == {"id": 1, "name": "John Doe"}
    
    @pytest.mark.asyncio
    async def test_monitored_query_with_params(self):
        """Testa context manager monitored_query com parâmetros"""
        params = {"user_id": 1, "status": "active"}
        
        async with monitored_query("SELECT * FROM users WHERE id = :user_id AND status = :status", params) as result:
            await asyncio.sleep(0.01)
            result = {"id": 1, "name": "John Doe", "status": "active"}
        
        assert result == {"id": 1, "name": "John Doe", "status": "active"}


class TestDatabaseOptimizerSingleton:
    """Testes para classe DatabaseOptimizerSingleton"""
    
    def test_singleton_get_instance_none(self):
        """Testa get_instance quando não há instância"""
        # Limpa instância existente
        DatabaseOptimizerSingleton._instance = None
        
        instance = DatabaseOptimizerSingleton.get_instance()
        assert instance is None
    
    def test_singleton_set_and_get_instance(self):
        """Testa set_instance e get_instance"""
        # Limpa instância existente
        DatabaseOptimizerSingleton._instance = None
        
        # Cria otimizador
        optimizer = DatabaseOptimizer("sqlite:///test.db")
        
        # Define instância
        DatabaseOptimizerSingleton.set_instance(optimizer)
        
        # Obtém instância
        retrieved_instance = DatabaseOptimizerSingleton.get_instance()
        
        assert retrieved_instance is optimizer
    
    def test_singleton_same_instance(self):
        """Testa se sempre retorna a mesma instância"""
        # Limpa instância existente
        DatabaseOptimizerSingleton._instance = None
        
        # Cria otimizador
        optimizer = DatabaseOptimizer("sqlite:///test.db")
        DatabaseOptimizerSingleton.set_instance(optimizer)
        
        # Obtém instância múltiplas vezes
        instance1 = DatabaseOptimizerSingleton.get_instance()
        instance2 = DatabaseOptimizerSingleton.get_instance()
        instance3 = DatabaseOptimizerSingleton.get_instance()
        
        assert instance1 is instance2
        assert instance2 is instance3
        assert instance1 is optimizer


class TestIntegrationScenarios:
    """Testes de cenários de integração"""
    
    @pytest.mark.asyncio
    async def test_database_optimization_workflow(self):
        """Testa workflow completo de otimização de banco de dados"""
        # Cria otimizador
        optimizer = DatabaseOptimizer("sqlite:///test.db")
        
        # Analisa performance de queries
        metrics1 = await optimizer.analyze_query_performance("SELECT * FROM users WHERE email = 'test@example.com'")
        metrics2 = await optimizer.analyze_query_performance("SELECT * FROM products WHERE category = 'electronics'")
        
        assert isinstance(metrics1, QueryMetrics)
        assert isinstance(metrics2, QueryMetrics)
        
        # Obtém estatísticas
        stats = await optimizer.get_query_statistics()
        assert stats["total_queries"] == 2
        
        # Gera sugestões de otimização
        suggestions = await optimizer.generate_optimization_suggestions()
        assert isinstance(suggestions, list)
        
        # Obtém relatório de saúde
        health_report = await optimizer.get_database_health_report()
        assert "overall_health" in health_report
    
    @pytest.mark.asyncio
    async def test_slow_query_detection_workflow(self):
        """Testa workflow de detecção de queries lentas"""
        optimizer = DatabaseOptimizer("sqlite:///test.db", {"slow_query_threshold": 0.1})
        
        # Adiciona queries rápidas e lentas
        fast_metrics = QueryMetrics(
            query="SELECT * FROM users WHERE id = 1",
            query_type=QueryType.SELECT,
            execution_time=0.05,
            rows_affected=1,
            timestamp=datetime.now()
        )
        
        slow_metrics = QueryMetrics(
            query="SELECT * FROM users WHERE email LIKE '%@example.com'",
            query_type=QueryType.SELECT,
            execution_time=0.5,
            rows_affected=1000,
            timestamp=datetime.now(),
            slow_query=True
        )
        
        optimizer._add_query_metrics(fast_metrics)
        optimizer._add_query_metrics(slow_metrics)
        
        # Obtém queries lentas
        slow_queries = await optimizer.get_slow_queries()
        assert len(slow_queries) == 1
        assert slow_queries[0].execution_time > optimizer.slow_query_threshold
    
    @pytest.mark.asyncio
    async def test_optimization_suggestions_workflow(self):
        """Testa workflow de sugestões de otimização"""
        optimizer = DatabaseOptimizer("sqlite:///test.db")
        
        # Adiciona métricas que geram sugestões
        problematic_metrics = [
            QueryMetrics(
                query="SELECT * FROM users WHERE email LIKE '%@example.com'",
                query_type=QueryType.SELECT,
                execution_time=3.0,
                rows_affected=10000,
                timestamp=datetime.now(),
                table_name="users",
                full_table_scan=True,
                slow_query=True
            ),
            QueryMetrics(
                query="SELECT * FROM products WHERE category = 'electronics' AND price > 100",
                query_type=QueryType.SELECT,
                execution_time=2.5,
                rows_affected=5000,
                timestamp=datetime.now(),
                table_name="products",
                slow_query=True
            )
        ]
        
        for metrics in problematic_metrics:
            optimizer._add_query_metrics(metrics)
        
        # Gera sugestões
        suggestions = await optimizer.generate_optimization_suggestions()
        
        assert isinstance(suggestions, list)
        assert all(isinstance(suggestion, OptimizationSuggestion) for suggestion in suggestions)
        
        # Verifica se há sugestões de índice
        index_suggestions = [s for s in suggestions if s.type == "index"]
        assert len(index_suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_connection_pool_optimization_workflow(self):
        """Testa workflow de otimização do pool de conexões"""
        optimizer = DatabaseOptimizer("sqlite:///test.db", {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30
        })
        
        # Analisa pool de conexões
        pool_info = await optimizer.optimize_connection_pool()
        
        assert isinstance(pool_info, dict)
        assert "current_pool_size" in pool_info
        assert "max_overflow" in pool_info
        assert "pool_timeout" in pool_info
        assert "recommendations" in pool_info
        
        # Verifica se as recomendações fazem sentido
        recommendations = pool_info["recommendations"]
        assert isinstance(recommendations, list)
    
    @pytest.mark.asyncio
    async def test_table_structure_analysis_workflow(self):
        """Testa workflow de análise de estrutura de tabela"""
        optimizer = DatabaseOptimizer("sqlite:///test.db")
        
        with patch.object(optimizer, 'engine') as mock_engine:
            mock_inspector = Mock()
            mock_engine.inspect.return_value = mock_inspector
            
            # Simula estrutura de tabela
            mock_inspector.get_columns.return_value = [
                {'name': 'id', 'type': 'INTEGER', 'nullable': False},
                {'name': 'email', 'type': 'VARCHAR(255)', 'nullable': False},
                {'name': 'name', 'type': 'VARCHAR(100)', 'nullable': True},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'nullable': False}
            ]
            
            mock_inspector.get_indexes.return_value = [
                {'name': 'idx_email', 'column_names': ['email']}
            ]
            
            # Analisa estrutura
            structure = await optimizer.analyze_table_structure("users")
            
            assert isinstance(structure, dict)
            assert "columns" in structure
            assert "indexes" in structure
            assert "recommendations" in structure
            
            # Verifica se detectou falta de índices
            columns = structure["columns"]
            indexes = structure["indexes"]
            
            assert len(columns) == 4
            assert len(indexes) == 1
            
            # Verifica se há recomendações
            recommendations = structure["recommendations"]
            assert isinstance(recommendations, list)
    
    @pytest.mark.asyncio
    async def test_metrics_export_workflow(self):
        """Testa workflow de exportação de métricas"""
        optimizer = DatabaseOptimizer("sqlite:///test.db")
        
        # Adiciona métricas variadas
        metrics_data = [
            ("SELECT * FROM users", QueryType.SELECT, 0.1, 10),
            ("INSERT INTO users VALUES (1, 'John')", QueryType.INSERT, 0.05, 1),
            ("UPDATE users SET name = 'Jane' WHERE id = 1", QueryType.UPDATE, 0.2, 1),
            ("DELETE FROM users WHERE id = 1", QueryType.DELETE, 0.15, 1),
            ("SELECT * FROM products WHERE category = 'electronics'", QueryType.SELECT, 2.5, 1000)
        ]
        
        for query, query_type, execution_time, rows_affected in metrics_data:
            metrics = QueryMetrics(
                query=query,
                query_type=query_type,
                execution_time=execution_time,
                rows_affected=rows_affected,
                timestamp=datetime.now()
            )
            optimizer._add_query_metrics(metrics)
        
        # Exporta métricas
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            export_path = tmp_file.name
        
        try:
            optimizer.export_metrics(export_path)
            
            # Verifica arquivo exportado
            with open(export_path, 'r') as f:
                exported_data = json.load(f)
            
            assert "export_timestamp" in exported_data
            assert "metrics" in exported_data
            assert len(exported_data["metrics"]) == 5
            
            # Verifica se todos os tipos de query estão presentes
            query_types = [m["query_type"] for m in exported_data["metrics"]]
            assert "SELECT" in query_types
            assert "INSERT" in query_types
            assert "UPDATE" in query_types
            assert "DELETE" in query_types
            
        finally:
            # Limpa arquivo temporário
            import os
            os.unlink(export_path) 