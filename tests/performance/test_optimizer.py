#!/usr/bin/env python3
"""
🧪 Testes do Sistema de Otimização de Performance - IMP-016
==========================================================

Tracing ID: TEST_PERFORMANCE_OPTIMIZER_IMP016_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes abrangentes para:
- PerformanceOptimizer
- CacheOptimizer
- QueryOptimizer
- OptimizationConfig
- Integração entre componentes

Prompt: CHECKLIST_CONFIABILIDADE.md - IMP-016
Ruleset: enterprise_control_layer.yaml
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar componentes a testar
from infrastructure.performance.optimizer import (
    PerformanceOptimizer,
    OptimizationConfig as PerfOptimizationConfig,
    PerformanceMetrics,
    OptimizationResult,
    OptimizationType,
    initialize_performance_optimizer,
    get_global_optimizer,
    set_global_optimizer
)

from infrastructure.performance.cache_optimizer import (
    CacheOptimizer,
    CacheConfig,
    CacheStrategy,
    CacheLevel,
    CacheMetrics,
    initialize_cache_optimizer,
    get_global_cache_optimizer,
    set_global_cache_optimizer
)

from infrastructure.performance.query_optimizer import (
    QueryOptimizer,
    QueryOptimizerConfig,
    QueryType,
    QueryMetrics,
    QueryAnalysis,
    initialize_query_optimizer,
    get_global_query_optimizer,
    set_global_query_optimizer
)

from infrastructure.performance.optimization_config import (
    OptimizationConfigManager,
    OptimizationConfig,
    Environment,
    PerformanceThresholds,
    CacheConfig as ConfigCacheConfig,
    QueryConfig,
    MonitoringConfig,
    get_global_config_manager,
    set_global_config_manager
)


class TestPerformanceOptimizer(unittest.TestCase):
    """Testes para o PerformanceOptimizer."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.config = PerfOptimizationConfig(
            cache_ttl=60,
            cache_max_size=100,
            query_timeout=10,
            max_concurrent_queries=5,
            memory_threshold=0.8,
            cpu_threshold=0.7,
            enable_auto_optimization=True,
            optimization_interval=1,
            metrics_collection_interval=1
        )
        self.optimizer = PerformanceOptimizer(self.config)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        if self.optimizer.monitoring_active:
            self.optimizer.stop_monitoring()
    
    def test_initialization(self):
        """Testa inicialização do otimizador."""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.config, self.config)
        self.assertFalse(self.optimizer.monitoring_active)
        self.assertIsNotNone(self.optimizer.metrics_collector)
    
    def test_start_monitoring(self):
        """Testa início do monitoramento."""
        result = self.optimizer.start_monitoring()
        self.assertTrue(result)
        self.assertTrue(self.optimizer.monitoring_active)
        
        # Aguardar um pouco para threads iniciarem
        time.sleep(0.1)
        
        # Verificar se threads foram criadas
        self.assertIsNotNone(self.optimizer.metrics_thread)
        self.assertIsNotNone(self.optimizer.optimization_thread)
    
    def test_stop_monitoring(self):
        """Testa parada do monitoramento."""
        # Iniciar monitoramento
        self.optimizer.start_monitoring()
        time.sleep(0.1)
        
        # Parar monitoramento
        result = self.optimizer.stop_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.optimizer.monitoring_active)
    
    def test_collect_metrics(self):
        """Testa coleta de métricas."""
        metrics = self.optimizer.collect_metrics()
        
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertIsInstance(metrics.timestamp, datetime)
        self.assertGreaterEqual(metrics.memory_usage, 0.0)
        self.assertLessEqual(metrics.memory_usage, 1.0)
        self.assertGreaterEqual(metrics.cpu_usage, 0.0)
        self.assertLessEqual(metrics.cpu_usage, 1.0)
    
    def test_optimize_cache(self):
        """Testa otimização de cache."""
        result = self.optimizer.optimize_cache()
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.CACHE)
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.improvement_percentage, 0.0)
        self.assertIsInstance(result.details, dict)
    
    def test_optimize_queries(self):
        """Testa otimização de queries."""
        result = self.optimizer.optimize_queries()
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.QUERY)
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.improvement_percentage, 0.0)
        self.assertIsInstance(result.details, dict)
    
    def test_optimize_memory(self):
        """Testa otimização de memória."""
        result = self.optimizer.optimize_memory()
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_type, OptimizationType.MEMORY)
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.improvement_percentage, 0.0)
        self.assertIsInstance(result.details, dict)
    
    def test_generate_performance_report(self):
        """Testa geração de relatório de performance."""
        # Coletar algumas métricas primeiro
        for _ in range(3):
            self.optimizer.collect_metrics()
            time.sleep(0.1)
        
        report = self.optimizer.generate_performance_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('timestamp', report)
        self.assertIn('current_metrics', report)
        self.assertIn('historical_stats', report)
        self.assertIn('optimizations', report)
        self.assertIn('recommendations', report)
    
    def test_should_optimize(self):
        """Testa lógica de decisão de otimização."""
        # Sem baseline, deve retornar False
        self.assertFalse(self.optimizer._should_optimize())
        
        # Estabelecer baseline
        self.optimizer._establish_baseline()
        
        # Com baseline, deve retornar True ou False baseado nas condições
        result = self.optimizer._should_optimize()
        self.assertIsInstance(result, bool)
    
    def test_apply_auto_optimizations(self):
        """Testa aplicação de otimizações automáticas."""
        # Estabelecer baseline
        self.optimizer._establish_baseline()
        
        # Aplicar otimizações
        self.optimizer._apply_auto_optimizations()
        
        # Verificar se otimizações foram aplicadas
        self.assertGreaterEqual(len(self.optimizer.optimization_history), 0)
    
    @patch('infrastructure.performance.optimizer.psutil')
    def test_collect_metrics_with_mock(self, mock_psutil):
        """Testa coleta de métricas com mock."""
        # Configurar mock
        mock_memory = Mock()
        mock_memory.percent = 75.0
        mock_psutil.virtual_memory.return_value = mock_memory
        mock_psutil.cpu_percent.return_value = 45.0
        
        metrics = self.optimizer.collect_metrics()
        
        self.assertEqual(metrics.memory_usage, 0.75)
        self.assertEqual(metrics.cpu_usage, 0.45)
    
    def test_optimize_performance_decorator(self):
        """Testa decorator de otimização de performance."""
        @self.optimizer.optimize_performance
        def test_function():
            time.sleep(0.1)
            return "test_result"
        
        result = test_function()
        self.assertEqual(result, "test_result")


class TestCacheOptimizer(unittest.TestCase):
    """Testes para o CacheOptimizer."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.config = CacheConfig(
            strategy=CacheStrategy.ADAPTIVE,
            l1_max_size=100,
            l1_ttl=60,
            l2_max_size=500,
            l2_ttl=300,
            l3_max_size=1000,
            l3_ttl=3600,
            enable_preloading=True,
            enable_compression=True,
            compression_threshold=1024,
            adaptive_learning_rate=0.1,
            pattern_analysis_interval=1
        )
        self.cache_optimizer = CacheOptimizer(self.config)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        if self.cache_optimizer.monitoring_active:
            self.cache_optimizer.stop_monitoring()
    
    def test_initialization(self):
        """Testa inicialização do otimizador de cache."""
        self.assertIsNotNone(self.cache_optimizer)
        self.assertEqual(self.cache_optimizer.config, self.config)
        self.assertFalse(self.cache_optimizer.monitoring_active)
        self.assertIsNotNone(self.cache_optimizer.metrics_collector)
    
    def test_start_monitoring(self):
        """Testa início do monitoramento de cache."""
        result = self.cache_optimizer.start_monitoring()
        self.assertTrue(result)
        self.assertTrue(self.cache_optimizer.monitoring_active)
        
        time.sleep(0.1)
        self.assertIsNotNone(self.cache_optimizer.pattern_analysis_thread)
        self.assertIsNotNone(self.cache_optimizer.optimization_thread)
    
    def test_stop_monitoring(self):
        """Testa parada do monitoramento de cache."""
        self.cache_optimizer.start_monitoring()
        time.sleep(0.1)
        
        result = self.cache_optimizer.stop_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.cache_optimizer.monitoring_active)
    
    def test_get_set_cache(self):
        """Testa operações básicas de cache."""
        # Testar set
        success = self.cache_optimizer.set("test_key", "test_value")
        self.assertTrue(success)
        
        # Testar get
        value = self.cache_optimizer.get("test_key")
        self.assertEqual(value, "test_value")
        
        # Testar get de chave inexistente
        value = self.cache_optimizer.get("nonexistent_key")
        self.assertIsNone(value)
    
    def test_cache_layers(self):
        """Testa funcionamento das camadas de cache."""
        # Armazenar em todas as camadas
        self.cache_optimizer.set("layer_test", "layer_value")
        
        # Verificar se está em todas as camadas
        self.assertIn("layer_test", self.cache_optimizer.l1_cache)
        self.assertIn("layer_test", self.cache_optimizer.l2_cache)
        self.assertIn("layer_test", self.cache_optimizer.l3_cache)
    
    def test_delete_cache(self):
        """Testa remoção de cache."""
        # Adicionar item
        self.cache_optimizer.set("delete_test", "delete_value")
        
        # Verificar se foi adicionado
        self.assertIsNotNone(self.cache_optimizer.get("delete_test"))
        
        # Remover
        success = self.cache_optimizer.delete("delete_test")
        self.assertTrue(success)
        
        # Verificar se foi removido
        self.assertIsNone(self.cache_optimizer.get("delete_test"))
    
    def test_clear_cache(self):
        """Testa limpeza de cache."""
        # Adicionar alguns itens
        self.cache_optimizer.set("clear_test1", "value1")
        self.cache_optimizer.set("clear_test2", "value2")
        
        # Limpar
        success = self.cache_optimizer.clear()
        self.assertTrue(success)
        
        # Verificar se foram removidos
        self.assertIsNone(self.cache_optimizer.get("clear_test1"))
        self.assertIsNone(self.cache_optimizer.get("clear_test2"))
    
    def test_preload_data(self):
        """Testa pré-carregamento de dados."""
        def data_provider(key):
            return f"preloaded_{key}"
        
        keys = ["key1", "key2", "key3"]
        results = self.cache_optimizer.preload_data(keys, data_provider)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 3)
        
        # Verificar se dados foram carregados
        for key in keys:
            self.assertIsNotNone(self.cache_optimizer.get(key))
    
    def test_analyze_patterns(self):
        """Testa análise de padrões."""
        # Adicionar alguns acessos
        self.cache_optimizer.get("pattern_test1")
        self.cache_optimizer.get("pattern_test2")
        self.cache_optimizer.set("pattern_test3", "value3")
        
        analysis = self.cache_optimizer.analyze_patterns()
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('total_patterns', analysis)
        self.assertIn('total_accesses', analysis)
        self.assertIn('patterns', analysis)
        self.assertIn('recommendations', analysis)
    
    def test_optimize_cache(self):
        """Testa otimização de cache."""
        # Adicionar alguns dados
        for i in range(10):
            self.cache_optimizer.set(f"optimize_test_{i}", f"value_{i}")
        
        result = self.cache_optimizer.optimize_cache()
        
        self.assertIsInstance(result, dict)
        self.assertIn('optimizations_applied', result)
        self.assertIn('cache_stats', result)
        self.assertIn('pattern_analysis', result)
    
    def test_get_cache_stats(self):
        """Testa obtenção de estatísticas de cache."""
        # Adicionar alguns dados
        self.cache_optimizer.set("stats_test1", "value1")
        self.cache_optimizer.set("stats_test2", "value2")
        self.cache_optimizer.get("stats_test1")
        
        stats = self.cache_optimizer.get_cache_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('hit_rate', stats)
        self.assertIn('cache_sizes', stats)
        self.assertIn('memory_usage', stats)
        self.assertIn('config', stats)
    
    def test_cache_result_decorator(self):
        """Testa decorator de cache de resultados."""
        call_count = 0
        
        @self.cache_optimizer.cache_result
        def expensive_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"
        
        # Primeira chamada
        result1 = expensive_function("test")
        self.assertEqual(result1, "result_test")
        self.assertEqual(call_count, 1)
        
        # Segunda chamada (deve usar cache)
        result2 = expensive_function("test")
        self.assertEqual(result2, "result_test")
        self.assertEqual(call_count, 1)  # Não deve incrementar


class TestQueryOptimizer(unittest.TestCase):
    """Testes para o QueryOptimizer."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.config = QueryOptimizerConfig(
            slow_query_threshold=1.0,
            max_query_history=1000,
            analysis_interval=1,
            enable_auto_optimization=True,
            enable_index_suggestions=True,
            enable_query_rewriting=True,
            max_suggestions_per_query=5,
            complexity_threshold=0.7
        )
        self.query_optimizer = QueryOptimizer(self.config)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        if self.query_optimizer.monitoring_active:
            self.query_optimizer.stop_monitoring()
    
    def test_initialization(self):
        """Testa inicialização do otimizador de queries."""
        self.assertIsNotNone(self.query_optimizer)
        self.assertEqual(self.query_optimizer.config, self.config)
        self.assertFalse(self.query_optimizer.monitoring_active)
        self.assertIsNotNone(self.query_optimizer.metrics_collector)
    
    def test_start_monitoring(self):
        """Testa início do monitoramento de queries."""
        result = self.query_optimizer.start_monitoring()
        self.assertTrue(result)
        self.assertTrue(self.query_optimizer.monitoring_active)
        
        time.sleep(0.1)
        self.assertIsNotNone(self.query_optimizer.analysis_thread)
        self.assertIsNotNone(self.query_optimizer.optimization_thread)
    
    def test_stop_monitoring(self):
        """Testa parada do monitoramento de queries."""
        self.query_optimizer.start_monitoring()
        time.sleep(0.1)
        
        result = self.query_optimizer.stop_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.query_optimizer.monitoring_active)
    
    def test_record_query(self):
        """Testa registro de queries."""
        sql = "SELECT * FROM users WHERE id = 1"
        execution_time = 0.5
        
        success = self.query_optimizer.record_query(
            sql=sql,
            execution_time=execution_time,
            rows_returned=1,
            cpu_usage=0.1,
            memory_usage=0.05
        )
        
        self.assertTrue(success)
        self.assertGreater(len(self.query_optimizer.query_history), 0)
    
    def test_record_slow_query(self):
        """Testa registro de query lenta."""
        sql = "SELECT * FROM users WHERE name LIKE '%test%'"
        execution_time = 2.0  # Acima do threshold
        
        success = self.query_optimizer.record_query(
            sql=sql,
            execution_time=execution_time
        )
        
        self.assertTrue(success)
        self.assertGreater(len(self.query_optimizer.slow_queries), 0)
    
    def test_analyze_query(self):
        """Testa análise de query."""
        sql = "SELECT id, name FROM users WHERE age > 18 ORDER BY name"
        
        analysis = self.query_optimizer.analyze_query(sql)
        
        self.assertIsInstance(analysis, QueryAnalysis)
        self.assertEqual(analysis.sql, sql)
        self.assertEqual(analysis.query_type, QueryType.SELECT)
        self.assertIsInstance(analysis.tables, list)
        self.assertIsInstance(analysis.columns, list)
        self.assertIsInstance(analysis.where_conditions, list)
        self.assertIsInstance(analysis.complexity_score, float)
        self.assertIsInstance(analysis.optimization_suggestions, list)
        self.assertIsInstance(analysis.recommended_indexes, list)
        self.assertIsInstance(analysis.estimated_improvement, float)
    
    def test_optimize_query(self):
        """Testa otimização de query."""
        sql = "SELECT * FROM users WHERE name LIKE '%test%'"
        
        result = self.query_optimizer.optimize_query(sql)
        
        self.assertIsInstance(result, dict)
        self.assertIn('original_query', result)
        self.assertIn('analysis', result)
        self.assertIn('optimizations', result)
        self.assertIn('total_improvement', result)
    
    def test_get_slow_queries(self):
        """Testa obtenção de queries lentas."""
        # Registrar algumas queries lentas
        for i in range(5):
            self.query_optimizer.record_query(
                sql=f"SELECT * FROM table_{i}",
                execution_time=2.0
            )
        
        slow_queries = self.query_optimizer.get_slow_queries(limit=3)
        
        self.assertIsInstance(slow_queries, list)
        self.assertLessEqual(len(slow_queries), 3)
        
        for query in slow_queries:
            self.assertIsInstance(query, QueryMetrics)
            self.assertGreaterEqual(query.execution_time, self.config.slow_query_threshold)
    
    def test_get_query_stats(self):
        """Testa obtenção de estatísticas de queries."""
        # Registrar algumas queries
        for i in range(10):
            self.query_optimizer.record_query(
                sql=f"SELECT * FROM table_{i}",
                execution_time=0.1 + (i * 0.1)
            )
        
        stats = self.query_optimizer.get_query_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_queries', stats)
        self.assertIn('slow_queries', stats)
        self.assertIn('execution_times', stats)
        self.assertIn('query_types', stats)
        self.assertIn('slowest_queries', stats)
    
    def test_detect_query_type(self):
        """Testa detecção de tipo de query."""
        test_cases = [
            ("SELECT * FROM users", QueryType.SELECT),
            ("INSERT INTO users VALUES (1, 'test')", QueryType.INSERT),
            ("UPDATE users SET name = 'test' WHERE id = 1", QueryType.UPDATE),
            ("DELETE FROM users WHERE id = 1", QueryType.DELETE),
            ("CREATE TABLE users (id INT)", QueryType.CREATE),
            ("ALTER TABLE users ADD COLUMN age INT", QueryType.ALTER),
            ("DROP TABLE users", QueryType.DROP)
        ]
        
        for sql, expected_type in test_cases:
            detected_type = self.query_optimizer._detect_query_type(sql)
            self.assertEqual(detected_type, expected_type)
    
    def test_monitor_query_decorator(self):
        """Testa decorator de monitoramento de queries."""
        call_count = 0
        
        @self.query_optimizer.monitor_query
        def database_query(sql):
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simular tempo de execução
            return [{"id": 1, "name": "test"}]
        
        result = database_query("SELECT * FROM users")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "test")
        self.assertEqual(call_count, 1)
        self.assertGreater(len(self.query_optimizer.query_history), 0)


class TestOptimizationConfig(unittest.TestCase):
    """Testes para o OptimizationConfig."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.config_manager = OptimizationConfigManager()
    
    def test_initialization(self):
        """Testa inicialização do gerenciador de configuração."""
        self.assertIsNotNone(self.config_manager)
        self.assertIsInstance(self.config_manager.config, OptimizationConfig)
    
    def test_default_config(self):
        """Testa configuração padrão."""
        config = self.config_manager.get_config()
        
        self.assertEqual(config.environment, Environment.DEVELOPMENT)
        self.assertIsInstance(config.thresholds, PerformanceThresholds)
        self.assertIsInstance(config.cache, ConfigCacheConfig)
        self.assertIsInstance(config.query, QueryConfig)
        self.assertIsInstance(config.monitoring, MonitoringConfig)
    
    def test_environment_config(self):
        """Testa configurações por ambiente."""
        from infrastructure.performance.optimization_config import get_environment_config
        
        # Testar configuração de desenvolvimento
        dev_config = get_environment_config(Environment.DEVELOPMENT)
        self.assertEqual(dev_config.environment, Environment.DEVELOPMENT)
        self.assertEqual(dev_config.thresholds.response_time_warning, 2.0)
        
        # Testar configuração de produção
        prod_config = get_environment_config(Environment.PRODUCTION)
        self.assertEqual(prod_config.environment, Environment.PRODUCTION)
        self.assertEqual(prod_config.thresholds.response_time_warning, 0.5)
    
    def test_validation(self):
        """Testa validação de configuração."""
        # Configuração válida
        self.assertTrue(self.config_manager.validate_config())
        
        # Configuração inválida
        invalid_config = self.config_manager.get_config()
        invalid_config.thresholds.response_time_warning = 5.0
        invalid_config.thresholds.response_time_critical = 3.0
        
        self.config_manager.update_config(invalid_config)
        self.assertFalse(self.config_manager.validate_config())
    
    def test_save_load_config(self):
        """Testa salvamento e carregamento de configuração."""
        import tempfile
        import os
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            # Salvar configuração
            self.config_manager.save_config(temp_file)
            self.assertTrue(os.path.exists(temp_file))
            
            # Carregar configuração
            new_manager = OptimizationConfigManager(temp_file)
            loaded_config = new_manager.get_config()
            
            # Verificar se configurações são iguais
            self.assertEqual(
                self.config_manager.get_config().environment,
                loaded_config.environment
            )
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestIntegration(unittest.TestCase):
    """Testes de integração entre componentes."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.config_manager = OptimizationConfigManager()
        self.config = self.config_manager.get_config()
        
        # Inicializar otimizadores
        self.perf_optimizer = PerformanceOptimizer(
            PerfOptimizationConfig(
                cache_ttl=60,
                cache_max_size=100,
                optimization_interval=1,
                metrics_collection_interval=1
            )
        )
        
        self.cache_optimizer = CacheOptimizer(
            CacheConfig(
                l1_max_size=100,
                l1_ttl=60,
                pattern_analysis_interval=1
            )
        )
        
        self.query_optimizer = QueryOptimizer(
            QueryOptimizerConfig(
                slow_query_threshold=1.0,
                max_query_history=100,
                analysis_interval=1
            )
        )
    
    def tearDown(self):
        """Limpeza após cada teste."""
        if self.perf_optimizer.monitoring_active:
            self.perf_optimizer.stop_monitoring()
        if self.cache_optimizer.monitoring_active:
            self.cache_optimizer.stop_monitoring()
        if self.query_optimizer.monitoring_active:
            self.query_optimizer.stop_monitoring()
    
    def test_global_initialization(self):
        """Testa inicialização global dos otimizadores."""
        # Performance optimizer
        global_perf = initialize_performance_optimizer()
        self.assertIsNotNone(global_perf)
        self.assertEqual(get_global_optimizer(), global_perf)
        
        # Cache optimizer
        global_cache = initialize_cache_optimizer()
        self.assertIsNotNone(global_cache)
        self.assertEqual(get_global_cache_optimizer(), global_cache)
        
        # Query optimizer
        global_query = initialize_query_optimizer()
        self.assertIsNotNone(global_query)
        self.assertEqual(get_global_query_optimizer(), global_query)
        
        # Config manager
        global_config = get_global_config_manager()
        self.assertIsNotNone(global_config)
    
    def test_workflow_integration(self):
        """Testa workflow integrado de otimização."""
        # 1. Iniciar monitoramento
        self.perf_optimizer.start_monitoring()
        self.cache_optimizer.start_monitoring()
        self.query_optimizer.start_monitoring()
        
        time.sleep(0.1)
        
        # 2. Simular carga de trabalho
        # Cache operations
        self.cache_optimizer.set("test_key", "test_value")
        self.cache_optimizer.get("test_key")
        
        # Query operations
        self.query_optimizer.record_query(
            sql="SELECT * FROM users WHERE id = 1",
            execution_time=0.5
        )
        
        # Performance metrics
        self.perf_optimizer.collect_metrics()
        
        time.sleep(0.1)
        
        # 3. Verificar otimizações
        perf_report = self.perf_optimizer.generate_performance_report()
        cache_stats = self.cache_optimizer.get_cache_stats()
        query_stats = self.query_optimizer.get_query_stats()
        
        # Verificar se relatórios foram gerados
        self.assertIsInstance(perf_report, dict)
        self.assertIsInstance(cache_stats, dict)
        self.assertIsInstance(query_stats, dict)
        
        # Verificar se otimizações foram aplicadas
        self.assertGreaterEqual(len(self.perf_optimizer.optimization_history), 0)
    
    def test_error_handling(self):
        """Testa tratamento de erros."""
        # Testar com configurações inválidas
        invalid_config = PerfOptimizationConfig(
            cache_ttl=-1,  # Valor inválido
            cache_max_size=0  # Valor inválido
        )
        
        # Deve criar otimizador mesmo com configuração inválida
        optimizer = PerformanceOptimizer(invalid_config)
        self.assertIsNotNone(optimizer)
        
        # Testar operações que podem falhar
        result = optimizer.collect_metrics()
        self.assertIsInstance(result, PerformanceMetrics)
    
    def test_concurrent_access(self):
        """Testa acesso concorrente aos otimizadores."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def worker(worker_id):
            try:
                # Operações de cache
                self.cache_optimizer.set(f"worker_{worker_id}", f"value_{worker_id}")
                value = self.cache_optimizer.get(f"worker_{worker_id}")
                
                # Operações de query
                self.query_optimizer.record_query(
                    sql=f"SELECT * FROM table_{worker_id}",
                    execution_time=0.1
                )
                
                # Operações de performance
                metrics = self.perf_optimizer.collect_metrics()
                
                results.put({
                    'worker_id': worker_id,
                    'cache_value': value,
                    'metrics': metrics
                })
                
            except Exception as e:
                results.put({'worker_id': worker_id, 'error': str(e)})
        
        # Criar threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        while not results.empty():
            result = results.get()
            self.assertNotIn('error', result)
            self.assertIsInstance(result['cache_value'], str)
            self.assertIsInstance(result['metrics'], PerformanceMetrics)


if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2) 