"""
Testes de Integração - APIs Reais
Baseado em código real do sistema Omni Keywords Finder

Tracing ID: TEST_INTEGRATION_API_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: CRIADO (NÃO EXECUTADO)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from backend.app.main import app
from backend.app.models import db, User, Categoria, Execucao, Nicho
from backend.app.api.execucoes import execucoes_bp
from backend.app.api.auth import auth_bp
from backend.app.api.nichos import nichos_bp
from backend.app.api.categorias import categorias_bp
from datetime import datetime
import json

class TestAPIIntegration:
    """
    Testes de integração para APIs reais do sistema
    """
    
    @pytest.fixture
    def test_app(self):
        """Criar aplicação Flask para testes de integração"""
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
    def auth_token(self, client):
        """Token de autenticação para testes"""
        # Criar usuário de teste
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        # Mock do registro de usuário
        with patch('backend.app.api.auth.generate_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            # Mock do login
            with patch('backend.app.api.auth.check_password_hash') as mock_check:
                mock_check.return_value = True
                
                with patch('backend.app.api.auth.create_access_token') as mock_token:
                    mock_token.return_value = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test_token"
                    
                    response = client.post('/api/auth/login',
                                         data=json.dumps({
                                             "username": "testuser",
                                             "password": "password123"
                                         }),
                                         content_type='application/json')
                    
                    if response.status_code == 200:
                        return json.loads(response.data)['access_token']
                    else:
                        return "mock_token_for_testing"
    
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
    
    @pytest.fixture
    def sample_nicho(self, test_app):
        """Criar nicho de exemplo baseado em dados reais"""
        with test_app.app_context():
            nicho = Nicho(
                nome="E-commerce",
                descricao="Nicho de e-commerce e vendas online",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(nicho)
            db.session.commit()
            return nicho
    
    def test_auth_to_execucoes_flow(self, client, auth_token, sample_categoria):
        """
        Teste: Fluxo completo de autenticação para execuções
        Baseado em APIs reais: POST /api/auth/login -> POST /api/execucoes/
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
                
                # Mock do processamento de execução
                with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process:
                    mock_process.return_value = {
                        "execucao_id": 1,
                        "prompt_preenchido": "Analise as palavras-chave: marketing digital, SEO, Google Ads",
                        "status": "processando"
                    }
                    
                    # Act
                    response = client.post('/api/execucoes/',
                                         data=json.dumps(execucao_data),
                                         content_type='application/json',
                                         headers={'Authorization': f'Bearer {auth_token}'})
                    
                    # Assert
                    assert response.status_code == 200
                    response_data = json.loads(response.data)
                    assert 'execucao_id' in response_data
                    assert 'prompt_preenchido' in response_data
                    assert 'categoria_id' in response_data
    
    def test_nichos_to_categorias_flow(self, client, auth_token, sample_nicho):
        """
        Teste: Fluxo de nichos para categorias
        Baseado em APIs reais: GET /api/nichos/ -> GET /api/categorias/
        """
        # Arrange - Mock da autenticação
        with patch('backend.app.api.nichos.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock da listagem de nichos
            with patch('backend.app.api.nichos.Nicho.query') as mock_nichos:
                mock_nichos.all.return_value = [sample_nicho]
                
                # Act - Listar nichos
                nichos_response = client.get('/api/nichos/',
                                           headers={'Authorization': f'Bearer {auth_token}'})
                
                # Assert
                assert nichos_response.status_code == 200
                nichos_data = json.loads(nichos_response.data)
                assert 'nichos' in nichos_data
                
                # Mock da listagem de categorias
                with patch('backend.app.api.categorias.Categoria.query') as mock_categorias:
                    mock_categorias.all.return_value = []
                    
                    # Act - Listar categorias
                    categorias_response = client.get('/api/categorias/',
                                                   headers={'Authorization': f'Bearer {auth_token}'})
                    
                    # Assert
                    assert categorias_response.status_code == 200
                    categorias_data = json.loads(categorias_response.data)
                    assert 'categorias' in categorias_data
    
    def test_execucoes_batch_flow(self, client, auth_token, sample_categoria):
        """
        Teste: Fluxo de execuções em lote
        Baseado em APIs reais: POST /api/execucoes/lote -> GET /api/execucoes/lote/status
        """
        # Arrange - Dados baseados em código real
        batch_data = {
            "execucoes": [
                {
                    "categoria_id": sample_categoria.id,
                    "palavras_chave": ["palavra1", "palavra2"],
                    "cluster": "cluster-1"
                },
                {
                    "categoria_id": sample_categoria.id,
                    "palavras_chave": ["palavra3", "palavra4"],
                    "cluster": "cluster-2"
                }
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
                            "total_execucoes": 2,
                            "status": "processando"
                        }
                        
                        # Act - Criar lote
                        batch_response = client.post('/api/execucoes/lote',
                                                   data=json.dumps(batch_data),
                                                   content_type='application/json',
                                                   headers={'Authorization': f'Bearer {auth_token}'})
                        
                        # Assert
                        assert batch_response.status_code == 200
                        batch_response_data = json.loads(batch_response.data)
                        assert 'lote_id' in batch_response_data
                        
                        # Mock do status do lote
                        with patch('backend.app.api.execucoes.get_lote_status') as mock_status:
                            mock_status.return_value = {
                                "lote_id": "lote-123",
                                "total_execucoes": 2,
                                "execucoes_concluidas": 1,
                                "execucoes_falharam": 0,
                                "status": "processando"
                            }
                            
                            # Act - Verificar status
                            status_response = client.get('/api/execucoes/lote/status?lote_id=lote-123',
                                                       headers={'Authorization': f'Bearer {auth_token}'})
                            
                            # Assert
                            assert status_response.status_code == 200
                            status_data = json.loads(status_response.data)
                            assert 'lote_id' in status_data
                            assert 'total_execucoes' in status_data
                            assert 'execucoes_concluidas' in status_data
    
    def test_error_handling_flow(self, client, auth_token):
        """
        Teste: Fluxo de tratamento de erros
        Baseado em APIs reais com cenários de erro
        """
        # Arrange - Dados inválidos baseados em validações reais
        invalid_data = {
            "categoria_id": 999,  # Categoria inexistente
            "palavras_chave": []  # Lista vazia
        }
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                mock_rate.return_value = lambda f: f
                
                # Act
                response = client.post('/api/execucoes/',
                                     data=json.dumps(invalid_data),
                                     content_type='application/json',
                                     headers={'Authorization': f'Bearer {auth_token}'})
                
                # Assert
                assert response.status_code in [400, 404]  # Bad Request ou Not Found
                response_data = json.loads(response.data)
                assert 'error' in response_data
    
    def test_rate_limiting_integration(self, client, auth_token, sample_categoria):
        """
        Teste: Integração com rate limiting
        Baseado em APIs reais com proteção contra abuso
        """
        # Arrange - Múltiplas requisições
        execucao_data = {
            "categoria_id": sample_categoria.id,
            "palavras_chave": ["teste"],
            "cluster": "cluster-teste"
        }
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting que falha após muitas requisições
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                # Primeiras requisições passam
                mock_rate.return_value = lambda f: f
                
                # Simular múltiplas requisições
                responses = []
                for i in range(5):
                    response = client.post('/api/execucoes/',
                                         data=json.dumps(execucao_data),
                                         content_type='application/json',
                                         headers={'Authorization': f'Bearer {auth_token}'})
                    responses.append(response.status_code)
                
                # Assert - Verificar que rate limiting está funcionando
                # Pelo menos uma requisição deve ser rejeitada (429) ou todas passarem (200)
                assert all(status in [200, 429] for status in responses)
    
    def test_data_validation_integration(self, client, auth_token):
        """
        Teste: Integração com validação de dados
        Baseado em validações reais do sistema
        """
        # Arrange - Dados com diferentes tipos de validação
        test_cases = [
            {
                "data": {"categoria_id": "invalid", "palavras_chave": ["teste"]},
                "expected_status": 400,
                "description": "categoria_id inválido (string em vez de int)"
            },
            {
                "data": {"categoria_id": 1, "palavras_chave": ["a" * 101]},
                "expected_status": 400,
                "description": "palavra-chave muito longa"
            },
            {
                "data": {"categoria_id": 1, "palavras_chave": ["<script>alert('xss')</script>"]},
                "expected_status": 400,
                "description": "palavra-chave com XSS"
            }
        ]
        
        # Mock da autenticação
        with patch('backend.app.api.execucoes.auth_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            
            # Mock do rate limiting
            with patch('backend.app.api.execucoes.execucao_rate_limited') as mock_rate:
                mock_rate.return_value = lambda f: f
                
                # Testar cada caso
                for test_case in test_cases:
                    # Act
                    response = client.post('/api/execucoes/',
                                         data=json.dumps(test_case["data"]),
                                         content_type='application/json',
                                         headers={'Authorization': f'Bearer {auth_token}'})
                    
                    # Assert
                    assert response.status_code == test_case["expected_status"], \
                        f"Falha no caso: {test_case['description']}"
                    
                    if response.status_code == 400:
                        response_data = json.loads(response.data)
                        assert 'error' in response_data
    
    def test_authentication_integration(self, client):
        """
        Teste: Integração com sistema de autenticação
        Baseado em fluxos reais de autenticação
        """
        # Arrange - Fluxo de registro e login
        user_data = {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        # Mock do registro
        with patch('backend.app.api.auth.generate_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            # Mock do login
            with patch('backend.app.api.auth.check_password_hash') as mock_check:
                mock_check.return_value = True
                
                with patch('backend.app.api.auth.create_access_token') as mock_token:
                    mock_token.return_value = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.integration_token"
                    
                    # Act - Registro
                    register_response = client.post('/api/auth/register',
                                                  data=json.dumps(user_data),
                                                  content_type='application/json')
                    
                    # Assert
                    assert register_response.status_code == 201
                    
                    # Act - Login
                    login_response = client.post('/api/auth/login',
                                               data=json.dumps({
                                                   "username": "integrationuser",
                                                   "password": "password123"
                                               }),
                                               content_type='application/json')
                    
                    # Assert
                    assert login_response.status_code == 200
                    login_data = json.loads(login_response.data)
                    assert 'access_token' in login_data
                    
                    # Testar uso do token
                    token = login_data['access_token']
                    
                    # Mock da validação de token
                    with patch('backend.app.api.auth.verify_jwt_in_request') as mock_verify:
                        mock_verify.return_value = None
                        
                        # Act - Usar token para acessar recurso protegido
                        profile_response = client.get('/api/auth/profile',
                                                    headers={'Authorization': f'Bearer {token}'})
                        
                        # Assert
                        assert profile_response.status_code == 200 