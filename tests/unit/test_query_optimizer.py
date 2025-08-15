"""
Testes Unitários para Query Optimizer
Sistema de Otimização de Consultas - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de otimização de consultas
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import time
import json
import hashlib
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.performance.query_optimizer import (
    QueryOptimizer, QueryAnalyzer, QueryOptimizationConfig,
    QueryType, OptimizationLevel, IndexType, QueryStats,
    IndexSuggestion, create_query_optimizer
)


class TestQueryOptimizationConfig:
    """Testes para QueryOptimizationConfig"""
    
    def test_query_optimization_config_initialization(self):
        """Testa inicialização de QueryOptimizationConfig"""
        config = QueryOptimizationConfig(
            enable_query_cache=True,
            cache_ttl=7200,
            max_cache_size=2000,
            enable_stats_collection=True,
            stats_retention_days=60,
            enable_auto_optimization=True,
            optimization_threshold=0.2,
            enable_index_suggestions=True,
            max_suggestions_per_query=10,
            enable_query_analysis=True,
            analysis_depth=OptimizationLevel.AGGRESSIVE,
            enable_performance_alerts=True,
            slow_query_threshold=2.0,
            enable_query_logging=True,
            log_slow_queries_only=True
        )
        
        assert config.enable_query_cache is True
        assert config.cache_ttl == 7200
        assert config.max_cache_size == 2000
        assert config.enable_stats_collection is True
        assert config.stats_retention_days == 60
        assert config.enable_auto_optimization is True
        assert config.optimization_threshold == 0.2
        assert config.enable_index_suggestions is True
        assert config.max_suggestions_per_query == 10
        assert config.enable_query_analysis is True
        assert config.analysis_depth == OptimizationLevel.AGGRESSIVE
        assert config.enable_performance_alerts is True
        assert config.slow_query_threshold == 2.0
        assert config.enable_query_logging is True
        assert config.log_slow_queries_only is True
    
    def test_query_optimization_config_validation_cache_ttl_negative(self):
        """Testa validação de cache TTL negativo"""
        with pytest.raises(ValueError, match="Cache TTL deve ser positivo"):
            QueryOptimizationConfig(cache_ttl=0)
    
    def test_query_optimization_config_validation_max_cache_size_negative(self):
        """Testa validação de max cache size negativo"""
        with pytest.raises(ValueError, match="Max cache size deve ser positivo"):
            QueryOptimizationConfig(max_cache_size=0)
    
    def test_query_optimization_config_validation_stats_retention_days_negative(self):
        """Testa validação de stats retention days negativo"""
        with pytest.raises(ValueError, match="Stats retention days deve ser positivo"):
            QueryOptimizationConfig(stats_retention_days=0)
    
    def test_query_optimization_config_validation_optimization_threshold_invalid(self):
        """Testa validação de optimization threshold inválido"""
        with pytest.raises(ValueError, match="Optimization threshold deve estar entre 0 e 1"):
            QueryOptimizationConfig(optimization_threshold=1.5)
    
    def test_query_optimization_config_validation_max_suggestions_negative(self):
        """Testa validação de max suggestions negativo"""
        with pytest.raises(ValueError, match="Max suggestions per query deve ser positivo"):
            QueryOptimizationConfig(max_suggestions_per_query=0)
    
    def test_query_optimization_config_validation_slow_query_threshold_negative(self):
        """Testa validação de slow query threshold negativo"""
        with pytest.raises(ValueError, match="Slow query threshold deve ser positivo"):
            QueryOptimizationConfig(slow_query_threshold=0)


class TestQueryStats:
    """Testes para QueryStats"""
    
    def test_query_stats_initialization(self):
        """Testa inicialização de QueryStats"""
        stats = QueryStats(
            query_hash="abc123",
            query_text="SELECT * FROM users",
            query_type=QueryType.SELECT,
            execution_count=10,
            total_execution_time=5.0,
            avg_execution_time=0.5,
            min_execution_time=0.1,
            max_execution_time=1.0,
            cache_hits=8,
            cache_misses=2,
            optimization_suggestions=["Add WHERE clause"],
            performance_score=85.0,
            complexity_score=30.0
        )
        
        assert stats.query_hash == "abc123"
        assert stats.query_text == "SELECT * FROM users"
        assert stats.query_type == QueryType.SELECT
        assert stats.execution_count == 10
        assert stats.total_execution_time == 5.0
        assert stats.avg_execution_time == 0.5
        assert stats.min_execution_time == 0.1
        assert stats.max_execution_time == 1.0
        assert stats.cache_hits == 8
        assert stats.cache_misses == 2
        assert stats.optimization_suggestions == ["Add WHERE clause"]
        assert stats.performance_score == 85.0
        assert stats.complexity_score == 30.0
    
    def test_update_execution_time(self):
        """Testa atualização de tempo de execução"""
        stats = QueryStats(
            query_hash="test",
            query_text="SELECT * FROM test",
            query_type=QueryType.SELECT
        )
        
        # Primeira execução
        stats.update_execution_time(0.5)
        assert stats.execution_count == 1
        assert stats.total_execution_time == 0.5
        assert stats.avg_execution_time == 0.5
        assert stats.min_execution_time == 0.5
        assert stats.max_execution_time == 0.5
        assert stats.first_execution_time is not None
        assert stats.last_execution_time is not None
        
        # Segunda execução
        stats.update_execution_time(1.0)
        assert stats.execution_count == 2
        assert stats.total_execution_time == 1.5
        assert stats.avg_execution_time == 0.75
        assert stats.min_execution_time == 0.5
        assert stats.max_execution_time == 1.0
    
    def test_update_cache_stats(self):
        """Testa atualização de estatísticas de cache"""
        stats = QueryStats(
            query_hash="test",
            query_text="SELECT * FROM test",
            query_type=QueryType.SELECT
        )
        
        # Hit
        stats.update_cache_stats(True)
        assert stats.cache_hits == 1
        assert stats.cache_misses == 0
        
        # Miss
        stats.update_cache_stats(False)
        assert stats.cache_hits == 1
        assert stats.cache_misses == 1
    
    def test_get_hit_rate(self):
        """Testa cálculo de taxa de hit"""
        stats = QueryStats(
            query_hash="test",
            query_text="SELECT * FROM test",
            query_type=QueryType.SELECT
        )
        
        # Sem requisições
        assert stats.get_hit_rate() == 0.0
        
        # Com hits e misses
        stats.cache_hits = 8
        stats.cache_misses = 2
        assert stats.get_hit_rate() == 0.8
        
        # Apenas hits
        stats.cache_misses = 0
        assert stats.get_hit_rate() == 1.0


class TestIndexSuggestion:
    """Testes para IndexSuggestion"""
    
    def test_index_suggestion_initialization(self):
        """Testa inicialização de IndexSuggestion"""
        suggestion = IndexSuggestion(
            table_name="users",
            column_name="email",
            index_type=IndexType.B_TREE,
            priority=8,
            reason="Coluna usada em WHERE",
            estimated_improvement=25.0,
            sql_statement="CREATE INDEX idx_users_email ON users(email);"
        )
        
        assert suggestion.table_name == "users"
        assert suggestion.column_name == "email"
        assert suggestion.index_type == IndexType.B_TREE
        assert suggestion.priority == 8
        assert suggestion.reason == "Coluna usada em WHERE"
        assert suggestion.estimated_improvement == 25.0
        assert suggestion.sql_statement == "CREATE INDEX idx_users_email ON users(email);"
        assert suggestion.created_at is not None


class TestQueryAnalyzer:
    """Testes para QueryAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Instância de QueryAnalyzer para testes"""
        return QueryAnalyzer()
    
    def test_query_analyzer_initialization(self, analyzer):
        """Testa inicialização do QueryAnalyzer"""
        assert analyzer.patterns is not None
        assert 'select_star' in analyzer.patterns
        assert 'no_where' in analyzer.patterns
        assert 'join' in analyzer.patterns
    
    def test_get_query_type_select(self, analyzer):
        """Testa identificação de tipo SELECT"""
        query = "SELECT * FROM users"
        query_type = analyzer._get_query_type(query.upper())
        assert query_type == QueryType.SELECT
    
    def test_get_query_type_insert(self, analyzer):
        """Testa identificação de tipo INSERT"""
        query = "INSERT INTO users (name) VALUES ('John')"
        query_type = analyzer._get_query_type(query.upper())
        assert query_type == QueryType.INSERT
    
    def test_get_query_type_update(self, analyzer):
        """Testa identificação de tipo UPDATE"""
        query = "UPDATE users SET name = 'John' WHERE id = 1"
        query_type = analyzer._get_query_type(query.upper())
        assert query_type == QueryType.UPDATE
    
    def test_get_query_type_delete(self, analyzer):
        """Testa identificação de tipo DELETE"""
        query = "DELETE FROM users WHERE id = 1"
        query_type = analyzer._get_query_type(query.upper())
        assert query_type == QueryType.DELETE
    
    def test_get_query_type_unknown(self, analyzer):
        """Testa identificação de tipo desconhecido"""
        query = "INVALID QUERY"
        query_type = analyzer._get_query_type(query.upper())
        assert query_type == QueryType.UNKNOWN
    
    def test_extract_tables_simple(self, analyzer):
        """Testa extração de tabelas - consulta simples"""
        query = "SELECT * FROM users"
        tables = analyzer._extract_tables(query.upper())
        assert tables == ["USERS"]
    
    def test_extract_tables_with_joins(self, analyzer):
        """Testa extração de tabelas - com JOINs"""
        query = "SELECT * FROM users JOIN orders ON users.id = orders.user_id"
        tables = analyzer._extract_tables(query.upper())
        assert "USERS" in tables
        assert "ORDERS" in tables
    
    def test_extract_columns_simple(self, analyzer):
        """Testa extração de colunas - consulta simples"""
        query = "SELECT id, name, email FROM users"
        columns = analyzer._extract_columns(query.upper())
        assert "ID" in columns
        assert "NAME" in columns
        assert "EMAIL" in columns
    
    def test_count_joins(self, analyzer):
        """Testa contagem de JOINs"""
        query = "SELECT * FROM users JOIN orders ON users.id = orders.user_id JOIN products ON orders.product_id = products.id"
        count = analyzer._count_joins(query.upper())
        assert count == 2
    
    def test_count_subqueries(self, analyzer):
        """Testa contagem de subconsultas"""
        query = "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)"
        count = analyzer._count_subqueries(query.upper())
        assert count == 1
    
    def test_count_aggregations(self, analyzer):
        """Testa contagem de agregações"""
        query = "SELECT COUNT(*), SUM(amount), AVG(price) FROM orders"
        count = analyzer._count_aggregations(query.upper())
        assert count == 3
    
    def test_analyze_conditions(self, analyzer):
        """Testa análise de condições"""
        query = "SELECT * FROM users WHERE age > 18 AND status = 'active' ORDER BY name GROUP BY department HAVING COUNT(*) > 5 LIMIT 10"
        conditions = analyzer._analyze_conditions(query.upper())
        
        assert conditions['has_where'] is True
        assert conditions['has_order_by'] is True
        assert conditions['has_group_by'] is True
        assert conditions['has_having'] is True
        assert conditions['has_limit'] is True
        assert conditions['condition_count'] == 2  # age > 18 AND status = 'active'
    
    def test_extract_functions(self, analyzer):
        """Testa extração de funções"""
        query = "SELECT COUNT(*), UPPER(name), LOWER(email) FROM users"
        functions = analyzer._extract_functions(query.upper())
        assert "COUNT" in functions
        assert "UPPER" in functions
        assert "LOWER" in functions
    
    def test_calculate_complexity_score(self, analyzer):
        """Testa cálculo de score de complexidade"""
        analysis = {
            'joins': 2,
            'subqueries': 1,
            'aggregations': 2,
            'conditions': {
                'has_where': True,
                'condition_count': 3,
                'has_order_by': True,
                'has_group_by': True,
                'has_having': False,
                'has_limit': True
            },
            'functions': ['COUNT', 'SUM']
        }
        
        score = analyzer._calculate_complexity_score(analysis)
        assert score > 0
        assert score <= 100
    
    def test_get_complexity_level(self, analyzer):
        """Testa determinação de nível de complexidade"""
        assert analyzer._get_complexity_level(20) == 'low'
        assert analyzer._get_complexity_level(50) == 'medium'
        assert analyzer._get_complexity_level(80) == 'high'
    
    def test_identify_performance_issues(self, analyzer):
        """Testa identificação de problemas de performance"""
        query = "SELECT * FROM users WHERE name LIKE '%john%' OR age > 18"
        analysis = {
            'query_type': QueryType.SELECT,
            'conditions': {'has_where': True, 'has_limit': False},
            'joins': 0,
            'subqueries': 0,
            'aggregations': 0,
            'functions': []
        }
        
        issues = analyzer._identify_performance_issues(query.upper(), analysis)
        assert len(issues) > 0
        assert any("SELECT *" in issue for issue in issues)
        assert any("sem LIMIT" in issue for issue in issues)
        assert any("LIKE com %" in issue for issue in issues)
        assert any("OR" in issue for issue in issues)
    
    def test_generate_optimization_suggestions(self, analyzer):
        """Testa geração de sugestões de otimização"""
        analysis = {
            'query_type': QueryType.SELECT,
            'conditions': {
                'has_where': False,
                'has_limit': False
            },
            'joins': 4,
            'subqueries': 1,
            'complexity_score': 70
        }
        
        suggestions = analyzer._generate_optimization_suggestions(analysis)
        assert len(suggestions) > 0
        assert any("WHERE" in suggestion for suggestion in suggestions)
        assert any("LIMIT" in suggestion for suggestion in suggestions)
    
    def test_analyze_query_complete(self, analyzer):
        """Testa análise completa de consulta"""
        query = "SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id = o.user_id WHERE u.status = 'active' GROUP BY u.name ORDER BY COUNT(o.id) DESC LIMIT 10"
        
        analysis = analyzer.analyze_query(query)
        
        assert analysis['query_type'] == QueryType.SELECT
        assert analysis['complexity_score'] > 0
        assert len(analysis['tables']) > 0
        assert len(analysis['columns']) > 0
        assert analysis['joins'] > 0
        assert analysis['aggregations'] > 0
        assert analysis['conditions']['has_where'] is True
        assert analysis['conditions']['has_order_by'] is True
        assert analysis['conditions']['has_group_by'] is True
        assert analysis['conditions']['has_limit'] is True
        assert len(analysis['performance_issues']) >= 0
        assert len(analysis['optimization_suggestions']) >= 0


class TestQueryOptimizer:
    """Testes para QueryOptimizer"""
    
    @pytest.fixture
    def optimizer(self):
        """Instância de QueryOptimizer para testes"""
        config = QueryOptimizationConfig(
            enable_query_cache=True,
            cache_ttl=60,
            max_cache_size=10,
            enable_stats_collection=True,
            slow_query_threshold=0.5
        )
        return QueryOptimizer(config)
    
    def test_query_optimizer_initialization(self):
        """Testa inicialização do QueryOptimizer"""
        optimizer = QueryOptimizer()
        
        assert optimizer.config is not None
        assert optimizer.analyzer is not None
        assert len(optimizer.query_cache) == 0
        assert len(optimizer.query_stats) == 0
        assert len(optimizer.index_suggestions) == 0
        assert optimizer.running is False
    
    def test_generate_query_hash(self, optimizer):
        """Testa geração de hash de consulta"""
        query = "SELECT * FROM users"
        params = {"id": 1}
        
        hash1 = optimizer._generate_query_hash(query, params)
        hash2 = optimizer._generate_query_hash(query, params)
        hash3 = optimizer._generate_query_hash(query, None)
        
        assert hash1 == hash2  # Mesma consulta e parâmetros
        assert hash1 != hash3  # Parâmetros diferentes
    
    def test_optimize_query_simple(self, optimizer):
        """Testa otimização de consulta simples"""
        query = "SELECT * FROM users"
        
        result = optimizer.optimize_query(query)
        
        assert result['original_query'] == query
        assert result['optimized_query'] is not None
        assert result['analysis'] is not None
        assert result['cached'] is False
        assert result['execution_time'] == 0.0
        assert 'index_suggestions' in result
    
    def test_optimize_query_with_params(self, optimizer):
        """Testa otimização de consulta com parâmetros"""
        query = "SELECT * FROM users WHERE id = ?"
        params = {"id": 1}
        
        result = optimizer.optimize_query(query, params)
        
        assert result['original_query'] == query
        assert result['cached'] is False
    
    def test_query_cache_hit(self, optimizer):
        """Testa hit no cache de consultas"""
        query = "SELECT * FROM users"
        
        # Primeira execução
        result1 = optimizer.optimize_query(query)
        assert result1['cached'] is False
        
        # Segunda execução (deve usar cache)
        result2 = optimizer.optimize_query(query)
        assert result2['cached'] is True
    
    def test_execute_query_success(self, optimizer):
        """Testa execução de consulta com sucesso"""
        query = "SELECT * FROM users"
        
        def mock_executor(query, params):
            return [{"id": 1, "name": "John"}]
        
        result = optimizer.execute_query(query, executor_func=mock_executor)
        
        assert result['success'] is True
        assert result['result'] is not None
        assert result['execution_time'] > 0
        assert result['optimization'] is not None
    
    def test_execute_query_failure(self, optimizer):
        """Testa execução de consulta com falha"""
        query = "SELECT * FROM users"
        
        def mock_executor(query, params):
            raise Exception("Database error")
        
        result = optimizer.execute_query(query, executor_func=mock_executor)
        
        assert result['success'] is False
        assert result['result'] is None
        assert 'error' in result
        assert result['execution_time'] > 0
    
    def test_execute_query_no_executor(self, optimizer):
        """Testa execução de consulta sem executor"""
        query = "SELECT * FROM users"
        
        result = optimizer.execute_query(query)
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_get_query_stats_specific(self, optimizer):
        """Testa obtenção de estatísticas de consulta específica"""
        query = "SELECT * FROM users"
        
        # Executar consulta para gerar estatísticas
        optimizer.optimize_query(query)
        
        # Obter hash da consulta
        query_hash = optimizer._generate_query_hash(query)
        
        stats = optimizer.get_query_stats(query_hash)
        assert stats is not None
        assert stats['query_hash'] == query_hash
        assert stats['query_text'] == query
    
    def test_get_query_stats_general(self, optimizer):
        """Testa obtenção de estatísticas gerais"""
        query1 = "SELECT * FROM users"
        query2 = "SELECT * FROM orders"
        
        # Executar consultas
        optimizer.optimize_query(query1)
        optimizer.optimize_query(query2)
        
        stats = optimizer.get_query_stats()
        assert stats['total_queries'] == 2
        assert stats['total_executions'] == 2
        assert stats['cache_size'] == 2
    
    def test_get_slow_queries(self, optimizer):
        """Testa obtenção de consultas lentas"""
        # Configurar threshold baixo
        optimizer.config.slow_query_threshold = 0.1
        
        query = "SELECT * FROM users"
        
        # Simular consulta lenta
        def slow_executor(query, params):
            time.sleep(0.2)  # Mais que o threshold
            return []
        
        optimizer.execute_query(query, executor_func=slow_executor)
        
        slow_queries = optimizer.get_slow_queries()
        assert len(slow_queries) > 0
        assert slow_queries[0]['query_text'] == query
    
    def test_get_index_suggestions(self, optimizer):
        """Testa obtenção de sugestões de índices"""
        query = "SELECT * FROM users WHERE email = 'test@example.com'"
        
        # Otimizar consulta para gerar sugestões
        optimizer.optimize_query(query)
        
        suggestions = optimizer.get_index_suggestions()
        assert len(suggestions) > 0
        assert all(isinstance(s, IndexSuggestion) for s in suggestions)
    
    def test_clear_cache(self, optimizer):
        """Testa limpeza do cache"""
        query = "SELECT * FROM users"
        
        # Executar consulta para popular cache
        optimizer.optimize_query(query)
        assert len(optimizer.query_cache) > 0
        
        # Limpar cache
        removed = optimizer.clear_cache()
        assert removed > 0
        assert len(optimizer.query_cache) == 0
    
    def test_start_stop_optimizer(self, optimizer):
        """Testa início e parada do otimizador"""
        # Iniciar
        optimizer.start()
        assert optimizer.running is True
        
        # Parar
        optimizer.stop()
        assert optimizer.running is False
    
    def test_callback_on_slow_query(self, optimizer):
        """Testa callback de consulta lenta"""
        slow_query_called = False
        slow_query_text = None
        slow_query_time = None
        
        def on_slow_query(query, execution_time):
            nonlocal slow_query_called, slow_query_text, slow_query_time
            slow_query_called = True
            slow_query_text = query
            slow_query_time = execution_time
        
        optimizer.on_slow_query = on_slow_query
        optimizer.config.slow_query_threshold = 0.1
        
        query = "SELECT * FROM users"
        
        def slow_executor(query, params):
            time.sleep(0.2)
            return []
        
        optimizer.execute_query(query, executor_func=slow_executor)
        
        assert slow_query_called is True
        assert slow_query_text == query
        assert slow_query_time > 0.1


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_query_optimizer_default(self):
        """Testa criação de QueryOptimizer com configurações padrão"""
        optimizer = create_query_optimizer()
        
        assert isinstance(optimizer, QueryOptimizer)
        assert optimizer.config is not None
    
    def test_create_query_optimizer_custom(self):
        """Testa criação de QueryOptimizer com configurações customizadas"""
        config = QueryOptimizationConfig(
            enable_query_cache=False,
            slow_query_threshold=5.0
        )
        
        optimizer = create_query_optimizer(config)
        
        assert optimizer.config.enable_query_cache is False
        assert optimizer.config.slow_query_threshold == 5.0


class TestQueryOptimizerIntegration:
    """Testes de integração para Query Optimizer"""
    
    def test_complete_workflow(self):
        """Testa workflow completo do otimizador"""
        config = QueryOptimizationConfig(
            enable_query_cache=True,
            cache_ttl=60,
            max_cache_size=5,
            enable_stats_collection=True,
            slow_query_threshold=0.1
        )
        
        optimizer = QueryOptimizer(config)
        optimizer.start()
        
        try:
            # Consulta simples
            query1 = "SELECT * FROM users WHERE id = 1"
            result1 = optimizer.optimize_query(query1)
            assert result1['cached'] is False
            
            # Segunda execução (cache hit)
            result2 = optimizer.optimize_query(query1)
            assert result2['cached'] is True
            
            # Consulta complexa
            query2 = """
                SELECT u.name, COUNT(o.id) as order_count, SUM(o.amount) as total_amount
                FROM users u
                JOIN orders o ON u.id = o.user_id
                WHERE u.status = 'active' AND o.created_at > '2024-01-01'
                GROUP BY u.name
                HAVING COUNT(o.id) > 5
                ORDER BY total_amount DESC
                LIMIT 10
            """
            
            def mock_executor(query, params):
                time.sleep(0.05)  # Simular execução
                return [{"name": "John", "order_count": 10, "total_amount": 1000}]
            
            result3 = optimizer.execute_query(query2, executor_func=mock_executor)
            assert result3['success'] is True
            assert result3['execution_time'] > 0
            
            # Verificar estatísticas
            stats = optimizer.get_query_stats()
            assert stats['total_queries'] == 2
            assert stats['total_executions'] == 2
            
            # Verificar sugestões de índices
            suggestions = optimizer.get_index_suggestions()
            assert len(suggestions) > 0
            
        finally:
            optimizer.stop()
    
    def test_performance_monitoring(self):
        """Testa monitoramento de performance"""
        config = QueryOptimizationConfig(
            enable_performance_alerts=True,
            slow_query_threshold=0.1,
            enable_query_logging=True
        )
        
        optimizer = QueryOptimizer(config)
        
        slow_queries_detected = []
        
        def on_slow_query(query, execution_time):
            slow_queries_detected.append((query, execution_time))
        
        optimizer.on_slow_query = on_slow_query
        
        # Consulta rápida
        def fast_executor(query, params):
            time.sleep(0.05)
            return []
        
        optimizer.execute_query("SELECT * FROM users", executor_func=fast_executor)
        assert len(slow_queries_detected) == 0
        
        # Consulta lenta
        def slow_executor(query, params):
            time.sleep(0.2)
            return []
        
        optimizer.execute_query("SELECT * FROM orders", executor_func=slow_executor)
        assert len(slow_queries_detected) == 1
        assert slow_queries_detected[0][1] > 0.1
    
    def test_query_analysis_comprehensive(self):
        """Testa análise abrangente de consultas"""
        optimizer = QueryOptimizer()
        
        # Diferentes tipos de consultas
        queries = [
            "SELECT * FROM users",  # Simples
            "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id WHERE u.status = 'active'",  # Com JOIN
            "SELECT COUNT(*), SUM(amount) FROM orders WHERE created_at > '2024-01-01' GROUP BY user_id HAVING COUNT(*) > 5",  # Complexa
            "SELECT * FROM users WHERE name LIKE '%john%' OR email LIKE '%@gmail.com'",  # Com OR
            "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000)"  # Com subconsulta
        ]
        
        for query in queries:
            result = optimizer.optimize_query(query)
            
            assert result['analysis'] is not None
            assert result['analysis']['query_type'] is not None
            assert result['analysis']['complexity_score'] >= 0
            assert result['analysis']['complexity_score'] <= 100
            assert result['analysis']['estimated_complexity'] in ['low', 'medium', 'high']
            assert isinstance(result['analysis']['performance_issues'], list)
            assert isinstance(result['analysis']['optimization_suggestions'], list)


if __name__ == "__main__":
    pytest.main([__file__]) 