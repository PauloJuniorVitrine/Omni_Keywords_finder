from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
🧪 TESTES UNITÁRIOS - GRAPHQL IMPLEMENTATION

Tracing ID: TEST_GRAPHQL_2025_001
Data/Hora: 2025-01-27 18:00:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Testes unitários para a implementação completa do GraphQL.
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Adicionar backend ao path
sys.path.append('backend')

# Importar módulos GraphQL
from app.api.graphql_schema import schema, Query, Mutation
from app.api.graphql_endpoint import graphql_bp, require_auth, log_graphql_request
from app.models import Nicho, Categoria, Execucao, Cliente
from app import db

class TestGraphQLSchema(unittest.TestCase):
    """Testes para o schema GraphQL"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Criar diretórios necessários
        os.makedirs('data/graphql', exist_ok=True)
        os.makedirs('logs/graphql', exist_ok=True)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_schema_creation(self):
        """Testa criação do schema GraphQL"""
        self.assertIsNotNone(schema)
        self.assertIsNotNone(schema.query_type)
        self.assertIsNotNone(schema.mutation_type)
    
    def test_query_type_fields(self):
        """Testa campos do tipo Query"""
        query_type = schema.query_type
        expected_fields = [
            'nichos', 'nicho', 'categorias', 'categoria',
            'execucoes', 'execucao', 'execucoes_agendadas',
            'keywords', 'keyword', 'clusters', 'cluster',
            'business_metrics', 'performance_metrics',
            'logs', 'notificacoes', 'estatisticas_gerais'
        ]
        
        for field in expected_fields:
            self.assertIn(field, query_type.fields)
    
    def test_mutation_type_fields(self):
        """Testa campos do tipo Mutation"""
        mutation_type = schema.mutation_type
        expected_fields = [
            'create_nicho', 'update_nicho', 'create_execucao'
        ]
        
        for field in expected_fields:
            self.assertIn(field, mutation_type.fields)
    
    def test_nicho_type_fields(self):
        """Testa campos do tipo NichoType"""
        nicho_type = schema.get_type('NichoType')
        self.assertIsNotNone(nicho_type)
        
        expected_fields = ['id', 'nome', 'descricao', 'ativo', 'data_criacao']
        for field in expected_fields:
            self.assertIn(field, nicho_type.fields)
    
    def test_categoria_type_fields(self):
        """Testa campos do tipo CategoriaType"""
        categoria_type = schema.get_type('CategoriaType')
        self.assertIsNotNone(categoria_type)
        
        expected_fields = ['id', 'nome', 'descricao', 'nicho_id', 'ativo', 'data_criacao']
        for field in expected_fields:
            self.assertIn(field, categoria_type.fields)
    
    def test_execucao_type_fields(self):
        """Testa campos do tipo ExecucaoType"""
        execucao_type = schema.get_type('ExecucaoType')
        self.assertIsNotNone(execucao_type)
        
        expected_fields = ['id', 'nicho_id', 'categoria_id', 'status', 'parametros', 'data_inicio', 'data_fim']
        for field in expected_fields:
            self.assertIn(field, execucao_type.fields)

class TestGraphQLQueries(unittest.TestCase):
    """Testes para queries GraphQL"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/graphql', exist_ok=True)
        os.makedirs('logs/graphql', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('app.api.graphql_schema.Nicho')
    def test_resolve_nichos(self, mock_nicho):
        """Testa resolver de nichos"""
        # Mock do modelo Nicho
        mock_nicho.query.filter.return_value.all.return_value = [
            MagicMock(id=1, nome='Test Nicho', descricao='Test', ativo=True)
        ]
        
        query = Query()
        result = query.resolve_nichos(None, ativo=True)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].nome, 'Test Nicho')
    
    @patch('app.api.graphql_schema.Categoria')
    def test_resolve_categorias(self, mock_categoria):
        """Testa resolver de categorias"""
        # Mock do modelo Categoria
        mock_categoria.query.filter.return_value.all.return_value = [
            MagicMock(id=1, nome='Test Categoria', descricao='Test', nicho_id=1, ativo=True)
        ]
        
        query = Query()
        result = query.resolve_categorias(None, nicho_id=1)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].nome, 'Test Categoria')
    
    @patch('app.api.graphql_schema.Execucao')
    def test_resolve_execucoes(self, mock_execucao):
        """Testa resolver de execuções"""
        # Mock do modelo Execucao
        mock_execucao.query.filter.return_value.all.return_value = [
            MagicMock(id=1, nicho_id=1, status='completed', data_inicio=datetime.now())
        ]
        
        query = Query()
        result = query.resolve_execucoes(None, nicho_id=1, status='completed')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, 'completed')
    
    @patch('app.api.graphql_schema.APIKeywords')
    def test_resolve_keywords(self, mock_api_keywords):
        """Testa resolver de keywords"""
        # Mock do serviço APIKeywords
        mock_instance = MagicMock()
        mock_instance.get_keywords.return_value = [
            {
                'id': '1',
                'keyword': 'test keyword',
                'volume': 1000,
                'dificuldade': 0.5,
                'cpc': 1.0,
                'categoria': 'test',
                'nicho': 'test',
                'data_coleta': datetime.now(),
                'score': 0.8
            }
        ]
        mock_api_keywords.return_value = mock_instance
        
        query = Query()
        result = query.resolve_keywords(None, filtros={'nicho_id': 1})
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].keyword, 'test keyword')
    
    @patch('app.api.graphql_schema.BusinessMetrics')
    def test_resolve_business_metrics(self, mock_business_metrics):
        """Testa resolver de métricas de negócio"""
        # Mock do serviço BusinessMetrics
        mock_instance = MagicMock()
        mock_instance.get_metrics.return_value = [
            {
                'id': '1',
                'nome': 'Revenue',
                'valor': 10000.0,
                'tipo': 'revenue',
                'periodo': 'monthly',
                'data_calculo': datetime.now(),
                'tendencia': 'up'
            }
        ]
        mock_business_metrics.return_value = mock_instance
        
        query = Query()
        result = query.resolve_business_metrics(None, tipo='revenue')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].nome, 'Revenue')

class TestGraphQLMutations(unittest.TestCase):
    """Testes para mutations GraphQL"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/graphql', exist_ok=True)
        os.makedirs('logs/graphql', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('app.api.graphql_schema.db')
    @patch('app.api.graphql_schema.Nicho')
    def test_create_nicho(self, mock_nicho, mock_db):
        """Testa mutation de criar nicho"""
        # Mock do modelo Nicho
        mock_nicho_instance = MagicMock()
        mock_nicho_instance.id = 1
        mock_nicho_instance.nome = 'Test Nicho'
        mock_nicho.return_value = mock_nicho_instance
        
        # Mock do db
        mock_db.session.add.return_value = None
        mock_db.session.commit.return_value = None
        
        mutation = Mutation()
        result = mutation.create_nicho.mutate(None, input={'nome': 'Test Nicho', 'descricao': 'Test'})
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.nicho.nome, 'Test Nicho')
    
    @patch('app.api.graphql_schema.db')
    @patch('app.api.graphql_schema.Nicho')
    def test_update_nicho(self, mock_nicho, mock_db):
        """Testa mutation de atualizar nicho"""
        # Mock do modelo Nicho
        mock_nicho_instance = MagicMock()
        mock_nicho_instance.id = 1
        mock_nicho_instance.nome = 'Updated Nicho'
        mock_nicho.query.get.return_value = mock_nicho_instance
        
        # Mock do db
        mock_db.session.commit.return_value = None
        
        mutation = Mutation()
        result = mutation.update_nicho.mutate(None, id=1, input={'nome': 'Updated Nicho'})
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.nicho.nome, 'Updated Nicho')
    
    @patch('app.api.graphql_schema.db')
    @patch('app.api.graphql_schema.Execucao')
    def test_create_execucao(self, mock_execucao, mock_db):
        """Testa mutation de criar execução"""
        # Mock do modelo Execucao
        mock_execucao_instance = MagicMock()
        mock_execucao_instance.id = 1
        mock_execucao_instance.nicho_id = 1
        mock_execucao_instance.status = 'pending'
        mock_execucao.return_value = mock_execucao_instance
        
        # Mock do db
        mock_db.session.add.return_value = None
        mock_db.session.commit.return_value = None
        
        mutation = Mutation()
        result = mutation.create_execucao.mutate(None, input={'nicho_id': 1, 'parametros': '{}'})
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.execucao.nicho_id, 1)

class TestGraphQLEndpoint(unittest.TestCase):
    """Testes para endpoint GraphQL"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/graphql', exist_ok=True)
        os.makedirs('logs/graphql', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_require_auth_decorator(self):
        """Testa decorator de autenticação"""
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/test')
        @require_auth
        def test_endpoint():
            return jsonify({'success': True})
        
        with app.test_client() as client:
            # Teste sem token
            response = client.post('/test')
            self.assertEqual(response.status_code, 401)
            
            # Teste com token inválido
            response = client.post('/test', headers={'Authorization': 'Bearer invalid'})
            self.assertEqual(response.status_code, 401)
    
    def test_log_graphql_request_decorator(self):
        """Testa decorator de logging"""
        from flask import Flask, request
        
        app = Flask(__name__)
        
        @app.route('/test')
        @log_graphql_request
        def test_endpoint():
            return {'success': True}
        
        with app.test_client() as client:
            response = client.post('/test', json={'query': 'test'})
            self.assertEqual(response.status_code, 200)
    
    def test_get_context(self):
        """Testa função de contexto"""
        from flask import Flask, request, g
        
        app = Flask(__name__)
        
        with app.test_request_context('/test'):
            context = get_context()
            
            self.assertIn('request', context)
            self.assertIn('headers', context)
            self.assertIn('ip', context)
            self.assertIn('user_agent', context)
    
    def test_format_error(self):
        """Testa formatação de erros"""
        from graphql import GraphQLError
        
        # Teste com GraphQLError
        error = GraphQLError('Test error', locations=[{'line': 1, 'column': 1}])
        formatted = format_error(error)
        
        self.assertIn('message', formatted)
        self.assertIn('locations', formatted)
        self.assertEqual(formatted['message'], 'Test error')
        
        # Teste com erro genérico
        error = Exception('Generic error')
        formatted = format_error(error)
        
        self.assertIn('message', formatted)
        self.assertEqual(formatted['message'], 'Erro interno do servidor')

class TestGraphQLIntegration(unittest.TestCase):
    """Testes de integração GraphQL"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/graphql', exist_ok=True)
        os.makedirs('logs/graphql', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_graphql_workflow(self):
        """Testa workflow completo do GraphQL"""
        # Query de teste
        query = """
        query {
            nichos {
                id
                nome
                descricao
                ativo
            }
        }
        """
        
        # Executar query
        result = schema.execute(query)
        
        # Verificar resultado
        self.assertIsNotNone(result)
        self.assertFalse(result.errors) if result.errors else True
    
    def test_mutation_workflow(self):
        """Testa workflow de mutation"""
        # Mutation de teste
        mutation = """
        mutation CreateNicho($input: NichoInput!) {
            createNicho(input: $input) {
                nicho {
                    id
                    nome
                    descricao
                }
                success
                message
            }
        }
        """
        
        variables = {
            'input': {
                'nome': 'Test Nicho',
                'descricao': 'Test Description',
                'ativo': True
            }
        }
        
        # Executar mutation
        result = schema.execute(mutation, variable_values=variables)
        
        # Verificar resultado
        self.assertIsNotNone(result)
        self.assertFalse(result.errors) if result.errors else True
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        # Query inválida
        query = """
        query {
            invalidField {
                id
            }
        }
        """
        
        # Executar query
        result = schema.execute(query)
        
        # Verificar que há erros
        self.assertIsNotNone(result)
        self.assertTrue(result.errors)

class TestGraphQLPerformance(unittest.TestCase):
    """Testes de performance GraphQL"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/graphql', exist_ok=True)
        os.makedirs('logs/graphql', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_query_performance(self):
        """Testa performance de queries"""
        import time
        
        query = """
        query {
            nichos {
                id
                nome
                categorias {
                    id
                    nome
                }
            }
        }
        """
        
        # Medir tempo de execução
        start_time = time.time()
        result = schema.execute(query)
        execution_time = time.time() - start_time
        
        # Verificar que execução é rápida (< 1 segundo)
        self.assertLess(execution_time, 1.0)
        self.assertIsNotNone(result)
    
    def test_complex_query_performance(self):
        """Testa performance de queries complexas"""
        import time
        
        query = """
        query {
            nichos {
                id
                nome
                categorias {
                    id
                    nome
                    execucoes {
                        id
                        status
                        keywords {
                            id
                            keyword
                            volume
                        }
                    }
                }
            }
        }
        """
        
        # Medir tempo de execução
        start_time = time.time()
        result = schema.execute(query)
        execution_time = time.time() - start_time
        
        # Verificar que execução é aceitável (< 2 segundos)
        self.assertLess(execution_time, 2.0)
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main() 