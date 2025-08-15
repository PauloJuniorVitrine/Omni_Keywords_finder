from typing import Dict, List, Optional, Any
"""
Testes Unitários - Database Optimization v2.0

Tracing ID: IMP002_DATABASE_OPTIMIZATION_TEST_001
Data: 2025-01-27
Versão: 1.0
Status: Em Implementação

Testa funcionalidades de otimização de database:
- Connection pooling
- Query caching
- Backup system
- Performance monitoring
- Index recommendations
"""

import unittest
import tempfile
import os
import sqlite3
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Importa classes do script de otimização
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

try:
    from database_optimization_v2 import (
        AdvancedConnectionPool,
        QueryCache,
        DatabaseBackup,
        DatabaseOptimizer,
        DatabaseMonitor,
        QueryType,
        QueryMetrics,
        IndexRecommendation,
        ConnectionPoolStats
    )
except ImportError:
    # Fallback para importação local
    pass


class TestAdvancedConnectionPool(unittest.TestCase):
    """Testa o pool de conexões avançado"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Cria database de teste
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES ('test1'), ('test2')")
    
    def tearDown(self):
        """Limpeza após testes"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_connection_pool_initialization(self):
        """Testa inicialização do pool"""
        pool = AdvancedConnectionPool(self.db_path, max_connections=5, min_connections=2)
        
        self.assertEqual(pool.max_connections, 5)
        self.assertEqual(pool.min_connections, 2)
        self.assertGreaterEqual(pool.connection_pool.qsize(), 2)
    
    def test_get_connection(self):
        """Testa obtenção de conexão"""
        pool = AdvancedConnectionPool(self.db_path, max_connections=3)
        
        conn = pool.get_connection()
        self.assertIsNotNone(conn)
        self.assertEqual(pool.active_connections, 1)
        
        # Testa query
        cursor = conn.execute("SELECT COUNT(*) FROM test")
        result = cursor.fetchone()
        self.assertEqual(result[0], 2)
        
        pool.return_connection(conn)
        self.assertEqual(pool.active_connections, 0)
    
    def test_connection_validation(self):
        """Testa validação de conexões"""
        pool = AdvancedConnectionPool(self.db_path)
        
        conn = pool.get_connection()
        self.assertTrue(pool._is_connection_valid(conn))
        
        # Fecha conexão manualmente
        conn.close()
        self.assertFalse(pool._is_connection_valid(conn))
        
        pool.return_connection(conn)
    
    def test_connection_pool_stats(self):
        """Testa estatísticas do pool"""
        pool = AdvancedConnectionPool(self.db_path, max_connections=5)
        
        # Usa algumas conexões
        conn1 = pool.get_connection()
        conn2 = pool.get_connection()
        
        stats = pool.get_stats()
        
        self.assertEqual(stats.total_connections, 5)
        self.assertEqual(stats.active_connections, 2)
        self.assertGreaterEqual(stats.idle_connections, 0)
        
        pool.return_connection(conn1)
        pool.return_connection(conn2)


class TestQueryCache(unittest.TestCase):
    """Testa o sistema de cache de queries"""
    
    def setUp(self):
        """Configuração inicial"""
        self.cache = QueryCache(max_size=10, ttl=60)
    
    def test_cache_set_get(self):
        """Testa armazenamento e recuperação do cache"""
        query = "SELECT * FROM users WHERE id = ?"
        params = (1,)
        result = [{"id": 1, "name": "John"}]
        
        # Armazena no cache
        self.cache.set(query, params, result)
        
        # Recupera do cache
        cached_result = self.cache.get(query, params)
        self.assertEqual(cached_result, result)
    
    def test_cache_key_generation(self):
        """Testa geração de chaves únicas"""
        query1 = "SELECT * FROM users WHERE id = ?"
        params1 = (1,)
        
        query2 = "SELECT * FROM users WHERE id = ?"
        params2 = (2,)
        
        key1 = self.cache._generate_key(query1, params1)
        key2 = self.cache._generate_key(query2, params2)
        
        self.assertNotEqual(key1, key2)
    
    def test_cache_ttl_expiration(self):
        """Testa expiração por TTL"""
        cache = QueryCache(max_size=10, ttl=1)  # 1 segundo
        
        query = "SELECT * FROM users"
        result = [{"id": 1}]
        
        cache.set(query, None, result)
        
        # Resultado deve estar disponível
        cached_result = cache.get(query, None)
        self.assertEqual(cached_result, result)
        
        # Aguarda expiração
        time.sleep(1.1)
        
        # Resultado deve ter expirado
        cached_result = cache.get(query, None)
        self.assertIsNone(cached_result)
    
    def test_cache_eviction(self):
        """Testa remoção de itens menos usados"""
        cache = QueryCache(max_size=3, ttl=3600)
        
        # Adiciona 4 itens (mais que o máximo)
        for index in range(4):
            query = f"SELECT * FROM table{index}"
            result = [{"id": index}]
            cache.set(query, None, result)
        
        # Verifica que apenas 3 itens permanecem
        stats = cache.get_stats()
        self.assertEqual(stats['size'], 3)
    
    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        cache = QueryCache(max_size=10, ttl=3600)
        
        # Adiciona alguns itens
        for index in range(3):
            query = f"SELECT * FROM table{index}"
            result = [{"id": index}]
            cache.set(query, None, result)
        
        # Acessa alguns itens
        cache.get("SELECT * FROM table0", None)
        cache.get("SELECT * FROM table1", None)
        
        stats = cache.get_stats()
        
        self.assertEqual(stats['size'], 3)
        self.assertEqual(stats['max_size'], 10)
        self.assertGreater(stats['hit_ratio'], 0)


class TestDatabaseBackup(unittest.TestCase):
    """Testa o sistema de backup"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        # Cria database de teste
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES ('backup_test')")
        
        self.backup = DatabaseBackup(self.db_path, backup_dir=os.path.join(self.temp_dir, "backups"))
    
    def tearDown(self):
        """Limpeza após testes"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_backup_creation(self):
        """Testa criação de backup"""
        backup_path = self.backup.create_backup()
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.endswith('.sqlite3'))
        
        # Verifica que backup contém dados
        with sqlite3.connect(backup_path) as conn:
            cursor = conn.execute("SELECT name FROM test")
            result = cursor.fetchone()
            self.assertEqual(result[0], 'backup_test')
    
    def test_backup_restore(self):
        """Testa restauração de backup"""
        # Cria backup
        backup_path = self.backup.create_backup()
        
        # Modifica database original
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM test")
            conn.execute("INSERT INTO test (name) VALUES ('modified')")
        
        # Restaura backup
        success = self.backup.restore_backup(backup_path)
        self.assertTrue(success)
        
        # Verifica que dados foram restaurados
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name FROM test")
            result = cursor.fetchone()
            self.assertEqual(result[0], 'backup_test')
    
    def test_backup_cleanup(self):
        """Testa limpeza de backups antigos"""
        # Cria alguns backups
        for index in range(3):
            backup_path = self.backup.create_backup()
            # Simula backup antigo
            old_time = datetime.now() - timedelta(days=31)
            os.utime(backup_path, (old_time.timestamp(), old_time.timestamp()))
        
        # Cria backup recente
        recent_backup = self.backup.create_backup()
        
        # Executa limpeza
        self.backup.cleanup_old_backups()
        
        # Verifica que backups antigos foram removidos
        backup_files = os.listdir(self.backup.backup_dir)
        self.assertEqual(len(backup_files), 1)  # Apenas o recente


class TestDatabaseOptimizer(unittest.TestCase):
    """Testa o otimizador principal"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Cria database de teste com dados
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
            conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL)")
            
            # Insere dados de teste
            for index in range(100):
                conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                           (f"user{index}", f"user{index}@example.com"))
                conn.execute("INSERT INTO orders (user_id, amount) VALUES (?, ?)", 
                           (index+1, index*10.5))
    
    def tearDown(self):
        """Limpeza após testes"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_optimizer_initialization(self):
        """Testa inicialização do otimizador"""
        optimizer = DatabaseOptimizer(self.db_path)
        
        self.assertIsNotNone(optimizer.connection_pool)
        self.assertIsNotNone(optimizer.query_cache)
        self.assertIsNotNone(optimizer.backup_system)
    
    def test_query_execution_with_cache(self):
        """Testa execução de query com cache"""
        optimizer = DatabaseOptimizer(self.db_path)
        
        query = "SELECT COUNT(*) FROM users"
        
        # Primeira execução (sem cache)
        result1, time1 = optimizer.execute_query(query)
        self.assertEqual(result1[0][0], 100)
        
        # Segunda execução (com cache)
        result2, time2 = optimizer.execute_query(query)
        self.assertEqual(result2[0][0], 100)
        
        # Segunda execução deve ser mais rápida
        self.assertLess(time2, time1)
    
    def test_slow_query_detection(self):
        """Testa detecção de queries lentas"""
        optimizer = DatabaseOptimizer(self.db_path)
        optimizer.slow_query_threshold = 0.001  # 1ms para teste
        
        # Query que deve ser considerada lenta
        query = "SELECT * FROM users CROSS JOIN orders"  # Query complexa
        
        result, execution_time = optimizer.execute_query(query)
        
        # Verifica que query foi registrada como lenta
        slow_queries = optimizer.get_slow_queries()
        self.assertGreater(len(slow_queries), 0)
    
    def test_index_recommendations(self):
        """Testa geração de recomendações de índice"""
        optimizer = DatabaseOptimizer(self.db_path)
        
        # Executa query que pode se beneficiar de índice
        query = "SELECT * FROM users WHERE name = 'user50'"
        optimizer.execute_query(query)
        
        # Verifica se há recomendações
        recommendations = optimizer.get_index_recommendations()
        # Pode ou não ter recomendações dependendo da análise
        self.assertIsInstance(recommendations, list)
    
    def test_performance_stats(self):
        """Testa coleta de estatísticas de performance"""
        optimizer = DatabaseOptimizer(self.db_path)
        
        # Executa algumas queries
        optimizer.execute_query("SELECT COUNT(*) FROM users")
        optimizer.execute_query("SELECT COUNT(*) FROM orders")
        
        stats = optimizer.get_performance_stats()
        
        self.assertIn('query_stats', stats)
        self.assertIn('cache_stats', stats)
        self.assertIn('pool_stats', stats)
        self.assertIn('index_stats', stats)
        
        # Verifica que há queries registradas
        self.assertGreater(stats['query_stats']['total_queries'], 0)


class TestDatabaseMonitor(unittest.TestCase):
    """Testa o monitor de database"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Cria database de teste
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        
        self.optimizer = DatabaseOptimizer(self.db_path)
        self.monitor = DatabaseMonitor(self.optimizer)
    
    def tearDown(self):
        """Limpeza após testes"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_monitor_initialization(self):
        """Testa inicialização do monitor"""
        self.assertFalse(self.monitor.monitoring_active)
        self.assertIsNone(self.monitor.monitor_thread)
    
    def test_monitor_start_stop(self):
        """Testa início e parada do monitoramento"""
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring_active)
        self.assertIsNotNone(self.monitor.monitor_thread)
        
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)
    
    def test_alert_thresholds(self):
        """Testa configuração de alertas"""
        self.assertEqual(self.monitor.alert_thresholds['slow_query_threshold'], 2.0)
        self.assertEqual(self.monitor.alert_thresholds['cache_hit_ratio_threshold'], 0.5)
        self.assertEqual(self.monitor.alert_thresholds['pool_hit_ratio_threshold'], 0.8)


class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Cria database de teste complexo
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    category TEXT,
                    price REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE sales (
                    id INTEGER PRIMARY KEY,
                    product_id INTEGER,
                    quantity INTEGER,
                    total REAL,
                    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            # Insere dados de teste
            for index in range(1000):
                conn.execute("""
                    INSERT INTO products (name, category, price) 
                    VALUES (?, ?, ?)
                """, (f"Product {index}", f"Category {index % 10}", index * 1.5))
                
                conn.execute("""
                    INSERT INTO sales (product_id, quantity, total)
                    VALUES (?, ?, ?)
                """, (index+1, index % 10 + 1, (index % 10 + 1) * (index * 1.5)))
    
    def tearDown(self):
        """Limpeza após testes"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_full_optimization_workflow(self):
        """Testa workflow completo de otimização"""
        optimizer = DatabaseOptimizer(self.db_path)
        
        # 1. Executa queries que podem ser otimizadas
        queries = [
            "SELECT COUNT(*) FROM products WHERE category = 'Category 1'",
            "SELECT p.name, string_data.quantity FROM products p JOIN sales string_data ON p.id = string_data.product_id WHERE p.price > 100",
            "SELECT category, AVG(price) FROM products GROUP BY category",
            "SELECT * FROM sales WHERE sale_date > '2024-01-01' ORDER BY total DESC"
        ]
        
        for query in queries:
            optimizer.execute_query(query)
        
        # 2. Executa otimização
        results = optimizer.optimize_database()
        
        # 3. Verifica resultados
        self.assertIn('timestamp', results)
        self.assertIn('slow_queries_analyzed', results)
        self.assertIn('indexes_created', results)
        self.assertIn('cache_optimized', results)
        self.assertIn('backup_created', results)
        
        # 4. Verifica estatísticas
        stats = optimizer.get_performance_stats()
        self.assertGreater(stats['query_stats']['total_queries'], 0)
    
    def test_concurrent_access(self):
        """Testa acesso concorrente ao database"""
        optimizer = DatabaseOptimizer(self.db_path, max_connections=10)
        
        def worker(worker_id):
            """Worker para teste concorrente"""
            for index in range(10):
                query = f"SELECT * FROM products WHERE id = {worker_id * 10 + index}"
                try:
                    result, time_taken = optimizer.execute_query(query)
                    return f"Worker {worker_id}: {len(result)} results in {time_taken:.4f}string_data"
                except Exception as e:
                    return f"Worker {worker_id}: Error - {e}"
        
        # Executa workers concorrentes
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, index) for index in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verifica que todos os workers completaram
        self.assertEqual(len(results), 5)
        
        # Verifica estatísticas do pool
        pool_stats = optimizer.connection_pool.get_stats()
        self.assertGreater(pool_stats.pool_hit_ratio, 0)


if __name__ == '__main__':
    # Executa testes
    unittest.main(verbosity=2) 