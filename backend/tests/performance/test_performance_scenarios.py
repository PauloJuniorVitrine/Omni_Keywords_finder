"""
Testes de Performance - Cenários Reais
Baseado em código real do sistema Omni Keywords Finder

Tracing ID: TEST_PERFORMANCE_SCENARIOS_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: CRIADO (NÃO EXECUTADO)
"""

import pytest
import time
import threading
import concurrent.futures
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from backend.app.main import app
from backend.app.models import db, User, Categoria, Execucao, Nicho
from datetime import datetime
import json

class TestPerformanceScenarios:
    """
    Testes de performance baseados em cenários reais do sistema
    """
    
    @pytest.fixture
    def test_app(self):
        """Criar aplicação Flask para testes de performance"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, test_app):
        """Cliente de teste"""
        return test_app.test_client()
    
    @pytest.fixture
    def sample_categoria(self, test_app):
        """Criar categoria de exemplo baseada em dados reais"""
        with test_app.app_context():
            categoria = Categoria(
                nome="Marketing Digital",
                descricao="Categoria para estratégias de marketing digital",
                prompt_template="Analise as palavras-chave: {palavras_chave}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(categoria)
            db.session.commit()
            return categoria
    
    def test_single_execucao_performance(self, client, sample_categoria):
        """
        Teste: Performance de execução única
        Baseado em cenário real: usuário executa uma análise de palavras-chave
        """
        # Arrange - Dados baseados em código real
        execucao_data = {
            "categoria_id": sample_categoria.id,
            "palavras_chave": ["marketing digital", "SEO", "Google Ads"],
            "cluster": "cluster-producao"
        }
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                mock_rate.return_value = lambda f: f
                
                # Mock do processamento
                with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process:
                    mock_process.return_value = {
                        "execucao_id": 1,
                        "prompt_preenchido": "Analise as palavras-chave: marketing digital, SEO, Google Ads",
                        "status": "concluida"
                    }
                    
                    # Act - Medir tempo de resposta
                    start_time = time.time()
                    response = client.post('/api/execucoes/',
                                         data=json.dumps(execucao_data),
                                         content_type='application/json')
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    
                    # Assert
                    assert response.status_code == 200
                    assert response_time < 2.0  # Máximo 2 segundos para execução única
                    
                    # Log de performance
                    print(f"✅ Execução única: {response_time:.3f}s")
    
    def test_batch_execucao_performance(self, client, sample_categoria):
        """
        Teste: Performance de execução em lote
        Baseado em cenário real: usuário processa múltiplas palavras-chave
        """
        # Arrange - Dados baseados em código real (lote de 10 execuções)
        batch_data = {
            "execucoes": [
                {
                    "categoria_id": sample_categoria.id,
                    "palavras_chave": [f"palavra{i}", f"keyword{i}"],
                    "cluster": f"cluster-{i}"
                }
                for i in range(1, 11)  # 10 execuções
            ]
        }
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                mock_rate.return_value = lambda f: f
                
                # Mock da validação de lote
                with patch('backend.app.api.execucoes.validate_batch_size') as mock_validate:
                    mock_validate.return_value = lambda f: f
                    
                    # Mock do processamento de lote
                    with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process:
                        mock_process.return_value = {
                            "lote_id": "lote-123",
                            "total_execucoes": 10,
                            "status": "processando"
                        }
                        
                        # Act - Medir tempo de resposta
                        start_time = time.time()
                        response = client.post('/api/execucoes/lote',
                                             data=json.dumps(batch_data),
                                             content_type='application/json')
                        end_time = time.time()
                        
                        response_time = end_time - start_time
                        
                        # Assert
                        assert response.status_code == 200
                        assert response_time < 5.0  # Máximo 5 segundos para lote de 10
                        
                        # Log de performance
                        print(f"✅ Lote de 10 execuções: {response_time:.3f}s")
    
    def test_concurrent_users_performance(self, client, sample_categoria):
        """
        Teste: Performance com usuários concorrentes
        Baseado em cenário real: múltiplos usuários acessando simultaneamente
        """
        # Arrange - Dados baseados em código real
        execucao_data = {
            "categoria_id": sample_categoria.id,
            "palavras_chave": ["concurrent test"],
            "cluster": "cluster-test"
        }
        
        def make_request():
            """Função para fazer requisição individual"""
            with patch('backend.app.api.execucoes.auth_required') as mock_auth:
                mock_auth.return_value = lambda f: f
                
                with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                    mock_rate.return_value = lambda f: f
                    
                    with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process:
                        mock_process.return_value = {
                            "execucao_id": 1,
                            "status": "concluida"
                        }
                        
                        start_time = time.time()
                        response = client.post('/api/execucoes/',
                                             data=json.dumps(execucao_data),
                                             content_type='application/json')
                        end_time = time.time()
                        
                        return {
                            'status_code': response.status_code,
                            'response_time': end_time - start_time
                        }
        
        # Act - Simular 5 usuários concorrentes
        num_concurrent_users = 5
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent_users)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Assert
        assert len(results) == num_concurrent_users
        assert all(result['status_code'] == 200 for result in results)
        assert total_time < 10.0  # Máximo 10 segundos para 5 usuários concorrentes
        
        # Calcular métricas
        avg_response_time = sum(result['response_time'] for result in results) / len(results)
        max_response_time = max(result['response_time'] for result in results)
        
        # Log de performance
        print(f"✅ {num_concurrent_users} usuários concorrentes:")
        print(f"   Tempo total: {total_time:.3f}s")
        print(f"   Tempo médio por requisição: {avg_response_time:.3f}s")
        print(f"   Tempo máximo: {max_response_time:.3f}s")
    
    def test_database_query_performance(self, client, test_app):
        """
        Teste: Performance de consultas ao banco de dados
        Baseado em cenário real: listagem de execuções com paginação
        """
        # Arrange - Criar dados de teste baseados em código real
        with test_app.app_context():
            # Criar múltiplas execuções para testar paginação
            execucoes = []
            for i in range(100):  # 100 execuções de teste
                execucao = Execucao(
                    categoria_id=1,
                    palavras_chave=[f"palavra{i}"],
                    prompt_preenchido=f"Análise {i}",
                    status="concluida",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                execucoes.append(execucao)
            
            db.session.add_all(execucoes)
            db.session.commit()
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock da consulta paginada
            with patch('backend.app.api.execucoes.Execucao.query') as mock_query:
                mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = execucoes[:10]
                mock_query.filter.return_value.count.return_value = 100
                
                # Act - Medir tempo de consulta
                start_time = time.time()
                response = client.get('/api/execucoes/?pagina=1&por_pagina=10')
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Assert
                assert response.status_code == 200
                assert response_time < 1.0  # Máximo 1 segundo para consulta paginada
                
                # Log de performance
                print(f"✅ Consulta paginada (100 registros): {response_time:.3f}s")
    
    def test_rate_limiting_performance(self, client, sample_categoria):
        """
        Teste: Performance do rate limiting
        Baseado em cenário real: proteção contra abuso
        """
        # Arrange - Dados baseados em código real
        execucao_data = {
            "categoria_id": sample_categoria.id,
            "palavras_chave": ["rate limit test"],
            "cluster": "cluster-test"
        }
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting que permite algumas requisições e depois bloqueia
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                call_count = 0
                
                def rate_limit_wrapper():
                    nonlocal call_count
                    call_count += 1
                    if call_count > 3:  # Bloquear após 3 requisições
                        return lambda f: lambda: ('Rate limit exceeded', 429)
                    return lambda f: f
                
                mock_rate.side_effect = rate_limit_wrapper
                
                # Mock do processamento
                with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process:
                    mock_process.return_value = {
                        "execucao_id": 1,
                        "status": "concluida"
                    }
                    
                    # Act - Fazer múltiplas requisições rapidamente
                    start_time = time.time()
                    responses = []
                    
                    for i in range(5):  # 5 requisições
                        response = client.post('/api/execucoes/',
                                             data=json.dumps(execucao_data),
                                             content_type='application/json')
                        responses.append(response.status_code)
                    
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    # Assert
                    assert total_time < 3.0  # Rate limiting deve ser rápido
                    assert 200 in responses  # Algumas requisições devem passar
                    assert 429 in responses  # Algumas devem ser bloqueadas
                    
                    # Log de performance
                    print(f"✅ Rate limiting (5 requisições): {total_time:.3f}s")
                    print(f"   Status codes: {responses}")
    
    def test_memory_usage_performance(self, client, sample_categoria):
        """
        Teste: Performance de uso de memória
        Baseado em cenário real: processamento de grandes volumes de dados
        """
        import psutil
        import os
        
        # Arrange - Dados baseados em código real (lote grande)
        batch_data = {
            "execucoes": [
                {
                    "categoria_id": sample_categoria.id,
                    "palavras_chave": [f"palavra{i}", f"keyword{i}", f"term{i}"],
                    "cluster": f"cluster-{i}"
                }
                for i in range(1, 51)  # 50 execuções
            ]
        }
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                mock_rate.return_value = lambda f: f
                
                # Mock da validação de lote
                with patch('backend.app.api.execucoes.validate_batch_size') as mock_validate:
                    mock_validate.return_value = lambda f: f
                    
                    # Mock do processamento de lote
                    with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process:
                        mock_process.return_value = {
                            "lote_id": "lote-large",
                            "total_execucoes": 50,
                            "status": "processando"
                        }
                        
                        # Medir memória antes
                        process = psutil.Process(os.getpid())
                        memory_before = process.memory_info().rss / 1024 / 1024  # MB
                        
                        # Act
                        start_time = time.time()
                        response = client.post('/api/execucoes/lote',
                                             data=json.dumps(batch_data),
                                             content_type='application/json')
                        end_time = time.time()
                        
                        # Medir memória depois
                        memory_after = process.memory_info().rss / 1024 / 1024  # MB
                        memory_increase = memory_after - memory_before
                        
                        response_time = end_time - start_time
                        
                        # Assert
                        assert response.status_code == 200
                        assert response_time < 10.0  # Máximo 10 segundos para lote grande
                        assert memory_increase < 100.0  # Máximo 100MB de aumento de memória
                        
                        # Log de performance
                        print(f"✅ Lote grande (50 execuções):")
                        print(f"   Tempo: {response_time:.3f}s")
                        print(f"   Aumento de memória: {memory_increase:.2f}MB")
    
    def test_error_handling_performance(self, client):
        """
        Teste: Performance do tratamento de erros
        Baseado em cenário real: sistema sob carga com erros
        """
        # Arrange - Dados inválidos para gerar erros
        invalid_data = {
            "categoria_id": 999,
            "palavras_chave": []
        }
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                mock_rate.return_value = lambda f: f
                
                # Act - Medir tempo de resposta para erro
                start_time = time.time()
                response = client.post('/api/execucoes/',
                                     data=json.dumps(invalid_data),
                                     content_type='application/json')
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Assert
                assert response.status_code in [400, 404]  # Bad Request ou Not Found
                assert response_time < 1.0  # Tratamento de erro deve ser rápido
                
                # Log de performance
                print(f"✅ Tratamento de erro: {response_time:.3f}s")
    
    def test_authentication_performance(self, client):
        """
        Teste: Performance da autenticação
        Baseado em cenário real: login de usuários
        """
        # Arrange - Dados de login baseados em código real
        login_data = {
            "username": "perfuser",
            "password": "password123"
        }
        
        # Mock do login
        with patch('backend.app.api.auth.check_password_hash') as mock_check:
            mock_check.return_value = True
            
            with patch('backend.app.api.auth.create_access_token') as mock_token:
                mock_token.return_value = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.perf_token"
                
                # Act - Medir tempo de autenticação
                start_time = time.time()
                response = client.post('/api/auth/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Assert
                assert response.status_code == 200
                assert response_time < 0.5  # Autenticação deve ser muito rápida
                
                # Log de performance
                print(f"✅ Autenticação: {response_time:.3f}s") 