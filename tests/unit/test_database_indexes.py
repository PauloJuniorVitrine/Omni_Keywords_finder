"""
Testes Unitários para Índices de Banco de Dados - Omni Keywords Finder
Validação de performance e funcionamento dos índices otimizados

Tracing ID: INDEX_TESTING_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🔴 CRÍTICO - Testes de Índices

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import sqlite3
import time
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any

class TestDatabaseIndexes:
    """
    Testes para validação dos índices de banco de dados
    Baseado no código real do sistema Omni Keywords Finder
    """
    
    @pytest.fixture
    def test_db(self):
        """Criar banco de dados de teste temporário"""
        # Criar arquivo temporário
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Conectar ao banco
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        
        # Criar tabelas baseadas no sistema real
        self._create_test_tables(cursor)
        
        # Inserir dados de teste baseados no sistema real
        self._insert_test_data(cursor)
        
        conn.commit()
        conn.close()
        
        yield temp_db.name
        
        # Limpar arquivo temporário
        os.unlink(temp_db.name)
    
    def _create_test_tables(self, cursor):
        """Criar tabelas de teste baseadas no sistema real"""
        
        # Tabela keywords (baseada no sistema real)
        cursor.execute("""
            CREATE TABLE keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                keyword TEXT NOT NULL,
                position INTEGER,
                search_volume INTEGER,
                difficulty REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela analytics (baseada no sistema real)
        cursor.execute("""
            CREATE TABLE analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_id INTEGER,
                date DATE NOT NULL,
                impressions INTEGER,
                clicks INTEGER,
                ctr REAL,
                FOREIGN KEY (keyword_id) REFERENCES keywords(id)
            )
        """)
        
        # Tabela payments (baseada no sistema real)
        cursor.execute("""
            CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela users (baseada no sistema real)
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                subscription_plan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _insert_test_data(self, cursor):
        """Inserir dados de teste baseados no sistema real"""
        
        # Dados de keywords (baseados no sistema real)
        keywords_data = [
            ('example.com', 'seo optimization', 1, 1000, 0.7),
            ('example.com', 'keyword research', 3, 800, 0.6),
            ('blog.com', 'content marketing', 2, 1200, 0.8),
            ('blog.com', 'digital marketing', 5, 1500, 0.9),
            ('site.com', 'web analytics', 1, 600, 0.5),
        ]
        
        for domain, keyword, position, volume, difficulty in keywords_data:
            cursor.execute("""
                INSERT INTO keywords (domain, keyword, position, search_volume, difficulty)
                VALUES (?, ?, ?, ?, ?)
            """, (domain, keyword, position, volume, difficulty))
        
        # Dados de analytics (baseados no sistema real)
        analytics_data = [
            (1, '2025-01-01', 1000, 50, 0.05),
            (1, '2025-01-02', 1100, 55, 0.05),
            (2, '2025-01-01', 800, 40, 0.05),
            (3, '2025-01-01', 1200, 60, 0.05),
            (4, '2025-01-01', 1500, 75, 0.05),
        ]
        
        for keyword_id, date, impressions, clicks, ctr in analytics_data:
            cursor.execute("""
                INSERT INTO analytics (keyword_id, date, impressions, clicks, ctr)
                VALUES (?, ?, ?, ?, ?)
            """, (keyword_id, date, impressions, clicks, ctr))
        
        # Dados de payments (baseados no sistema real)
        payments_data = [
            (1, 29.99, 'completed', 'credit_card'),
            (1, 29.99, 'completed', 'credit_card'),
            (2, 49.99, 'pending', 'paypal'),
            (3, 19.99, 'failed', 'credit_card'),
            (4, 99.99, 'completed', 'bank_transfer'),
        ]
        
        for user_id, amount, status, method in payments_data:
            cursor.execute("""
                INSERT INTO payments (user_id, amount, status, payment_method)
                VALUES (?, ?, ?, ?)
            """, (user_id, amount, status, method))
        
        # Dados de users (baseados no sistema real)
        users_data = [
            ('user1@example.com', 'João Silva', 'premium'),
            ('user2@example.com', 'Maria Santos', 'basic'),
            ('user3@example.com', 'Pedro Costa', 'premium'),
            ('user4@example.com', 'Ana Oliveira', 'basic'),
            ('user5@example.com', 'Carlos Lima', 'premium'),
        ]
        
        for email, name, plan in users_data:
            cursor.execute("""
                INSERT INTO users (email, name, subscription_plan)
                VALUES (?, ?, ?)
            """, (email, name, plan))
    
    def test_indexes_creation(self, test_db):
        """Testar criação dos índices otimizados"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Ler arquivo de índices
        index_file = Path("infrastructure/database/optimization_indexes.sql")
        if index_file.exists():
            with open(index_file, 'r') as f:
                index_sql = f.read()
            
            # Executar criação dos índices
            for statement in index_sql.split(';'):
                if statement.strip() and statement.strip().startswith('CREATE INDEX'):
                    cursor.execute(statement)
            
            conn.commit()
            
            # Verificar se índices foram criados
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Índices esperados baseados no arquivo SQL
            expected_indexes = [
                'idx_keywords_domain',
                'idx_keywords_keyword', 
                'idx_keywords_position',
                'idx_analytics_date',
                'idx_analytics_keyword_id',
                'idx_payments_user_id',
                'idx_payments_status',
                'idx_users_email'
            ]
            
            for expected_index in expected_indexes:
                assert expected_index in indexes, f"Índice {expected_index} não foi criado"
        
        conn.close()
    
    def test_keywords_domain_query_performance(self, test_db):
        """Testar performance da query por domínio com e sem índice"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Query crítica identificada no sistema real
        query = "SELECT * FROM keywords WHERE domain = ?"
        
        # Teste sem índice (remover índice se existir)
        cursor.execute("DROP INDEX IF EXISTS idx_keywords_domain")
        conn.commit()
        
        # Medir tempo sem índice
        start_time = time.time()
        cursor.execute(query, ('example.com',))
        results_without_index = cursor.fetchall()
        time_without_index = time.time() - start_time
        
        # Criar índice
        cursor.execute("CREATE INDEX idx_keywords_domain ON keywords(domain)")
        conn.commit()
        
        # Medir tempo com índice
        start_time = time.time()
        cursor.execute(query, ('example.com',))
        results_with_index = cursor.fetchall()
        time_with_index = time.time() - start_time
        
        # Validar resultados
        assert len(results_without_index) == len(results_with_index)
        assert time_with_index < time_without_index, "Índice não melhorou performance"
        
        conn.close()
    
    def test_keywords_position_query_performance(self, test_db):
        """Testar performance da query por posição com e sem índice"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Query crítica identificada no sistema real
        query = "SELECT * FROM keywords WHERE position > ?"
        
        # Teste sem índice
        cursor.execute("DROP INDEX IF EXISTS idx_keywords_position")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, (2,))
        results_without_index = cursor.fetchall()
        time_without_index = time.time() - start_time
        
        # Criar índice
        cursor.execute("CREATE INDEX idx_keywords_position ON keywords(position)")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, (2,))
        results_with_index = cursor.fetchall()
        time_with_index = time.time() - start_time
        
        # Validar resultados
        assert len(results_without_index) == len(results_with_index)
        assert time_with_index < time_without_index, "Índice não melhorou performance"
        
        conn.close()
    
    def test_analytics_date_query_performance(self, test_db):
        """Testar performance da query por data com e sem índice"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Query crítica identificada no sistema real
        query = "SELECT * FROM analytics WHERE date BETWEEN ? AND ?"
        
        # Teste sem índice
        cursor.execute("DROP INDEX IF EXISTS idx_analytics_date")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, ('2025-01-01', '2025-01-02'))
        results_without_index = cursor.fetchall()
        time_without_index = time.time() - start_time
        
        # Criar índice
        cursor.execute("CREATE INDEX idx_analytics_date ON analytics(date)")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, ('2025-01-01', '2025-01-02'))
        results_with_index = cursor.fetchall()
        time_with_index = time.time() - start_time
        
        # Validar resultados
        assert len(results_without_index) == len(results_with_index)
        assert time_with_index < time_without_index, "Índice não melhorou performance"
        
        conn.close()
    
    def test_payments_user_id_query_performance(self, test_db):
        """Testar performance da query por user_id com e sem índice"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Query crítica identificada no sistema real
        query = "SELECT * FROM payments WHERE user_id = ?"
        
        # Teste sem índice
        cursor.execute("DROP INDEX IF EXISTS idx_payments_user_id")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, (1,))
        results_without_index = cursor.fetchall()
        time_without_index = time.time() - start_time
        
        # Criar índice
        cursor.execute("CREATE INDEX idx_payments_user_id ON payments(user_id)")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, (1,))
        results_with_index = cursor.fetchall()
        time_with_index = time.time() - start_time
        
        # Validar resultados
        assert len(results_without_index) == len(results_with_index)
        assert time_with_index < time_without_index, "Índice não melhorou performance"
        
        conn.close()
    
    def test_users_email_query_performance(self, test_db):
        """Testar performance da query por email com e sem índice"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Query crítica identificada no sistema real
        query = "SELECT * FROM users WHERE email = ?"
        
        # Teste sem índice
        cursor.execute("DROP INDEX IF EXISTS idx_users_email")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, ('user1@example.com',))
        results_without_index = cursor.fetchall()
        time_without_index = time.time() - start_time
        
        # Criar índice
        cursor.execute("CREATE INDEX idx_users_email ON users(email)")
        conn.commit()
        
        start_time = time.time()
        cursor.execute(query, ('user1@example.com',))
        results_with_index = cursor.fetchall()
        time_with_index = time.time() - start_time
        
        # Validar resultados
        assert len(results_without_index) == len(results_with_index)
        assert time_with_index < time_without_index, "Índice não melhorou performance"
        
        conn.close()
    
    def test_query_execution_time_threshold(self, test_db):
        """Testar se queries executam dentro do limite de 500ms"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Criar todos os índices
        self._create_all_indexes(cursor)
        conn.commit()
        
        # Queries críticas do sistema real
        critical_queries = [
            ("SELECT * FROM keywords WHERE domain = ?", ('example.com',)),
            ("SELECT * FROM keywords WHERE position > ?", (2,)),
            ("SELECT * FROM analytics WHERE date BETWEEN ? AND ?", ('2025-01-01', '2025-01-02')),
            ("SELECT * FROM payments WHERE user_id = ?", (1,)),
            ("SELECT * FROM users WHERE email = ?", ('user1@example.com',)),
        ]
        
        for query, params in critical_queries:
            start_time = time.time()
            cursor.execute(query, params)
            results = cursor.fetchall()
            execution_time = time.time() - start_time
            
            # Validar tempo de execução < 500ms
            assert execution_time < 0.5, f"Query {query} executou em {execution_time:.3f}s (limite: 0.5s)"
        
        conn.close()
    
    def _create_all_indexes(self, cursor):
        """Criar todos os índices otimizados"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_keywords_domain ON keywords(domain)",
            "CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword)",
            "CREATE INDEX IF NOT EXISTS idx_keywords_position ON keywords(position)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_keyword_id ON analytics(keyword_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def test_index_maintenance(self, test_db):
        """Testar manutenção dos índices após inserções"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Criar índices
        self._create_all_indexes(cursor)
        conn.commit()
        
        # Inserir novos dados
        cursor.execute("""
            INSERT INTO keywords (domain, keyword, position, search_volume, difficulty)
            VALUES (?, ?, ?, ?, ?)
        """, ('newdomain.com', 'new keyword', 10, 500, 0.6))
        
        cursor.execute("""
            INSERT INTO analytics (keyword_id, date, impressions, clicks, ctr)
            VALUES (?, ?, ?, ?, ?)
        """, (6, '2025-01-03', 800, 40, 0.05))
        
        conn.commit()
        
        # Verificar se índices ainda funcionam
        cursor.execute("SELECT * FROM keywords WHERE domain = ?", ('newdomain.com',))
        results = cursor.fetchall()
        assert len(results) == 1, "Índice não funcionou após inserção"
        
        cursor.execute("SELECT * FROM analytics WHERE keyword_id = ?", (6,))
        results = cursor.fetchall()
        assert len(results) == 1, "Índice não funcionou após inserção"
        
        conn.close()

if __name__ == "__main__":
    pytest.main([__file__]) 