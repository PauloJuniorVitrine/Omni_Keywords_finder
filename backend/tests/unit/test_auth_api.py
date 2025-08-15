"""
Testes Unitários - API de Autenticação
Baseado em código real do sistema Omni Keywords Finder

Tracing ID: TEST_UNIT_AUTH_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: CRIADO (NÃO EXECUTADO)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from backend.app.api.auth import auth_bp
from backend.app.models import User, Role, Permission, db
from datetime import datetime, timedelta
import json
import jwt

class TestAuthAPI:
    """
    Testes unitários para a API de autenticação baseados em código real
    """
    
    @pytest.fixture
    def app(self):
        """Criar aplicação Flask para testes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
        app.register_blueprint(auth_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Cliente de teste"""
        return app.test_client()
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock para sessão do banco de dados"""
        with patch('backend.app.api.auth.db') as mock_db:
            mock_session = Mock()
            mock_db.session = mock_session
            yield mock_session
    
    @pytest.fixture
    def sample_user(self):
        """Usuário de exemplo baseado em dados reais"""
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password_123",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_role(self):
        """Role de exemplo baseado em dados reais"""
        return Role(
            id=1,
            name="user",
            description="Usuário padrão do sistema",
            created_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_permission(self):
        """Permission de exemplo baseado em dados reais"""
        return Permission(
            id=1,
            name="execucoes:read",
            description="Permissão para ler execuções",
            created_at=datetime.now()
        )
    
    def test_login_success(self, client, mock_db_session, sample_user):
        """
        Teste: Login com sucesso
        Baseado no endpoint real POST /api/auth/login
        """
        # Arrange - Dados baseados em código real
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        # Mock do usuário encontrado
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Mock da verificação de senha
        with patch('backend.app.api.auth.check_password_hash') as mock_check:
            mock_check.return_value = True
            
            # Mock da geração de token
            with patch('backend.app.api.auth.create_access_token') as mock_token:
                mock_token.return_value = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test_token"
                
                # Act
                response = client.post('/api/auth/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
                
                # Assert
                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert 'access_token' in response_data
                assert 'token_type' in response_data
                assert response_data['token_type'] == 'bearer'
    
    def test_login_invalid_credentials(self, client, mock_db_session):
        """
        Teste: Login com credenciais inválidas
        Baseado no endpoint real POST /api/auth/login
        """
        # Arrange
        login_data = {
            "username": "invaliduser",
            "password": "wrongpassword"
        }
        
        # Mock de usuário não encontrado
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Credenciais inválidas' in response_data['error']
    
    def test_login_wrong_password(self, client, mock_db_session, sample_user):
        """
        Teste: Login com senha incorreta
        Baseado no endpoint real POST /api/auth/login
        """
        # Arrange
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        # Mock do usuário encontrado
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Mock da verificação de senha falhando
        with patch('backend.app.api.auth.check_password_hash') as mock_check:
            mock_check.return_value = False
            
            # Act
            response = client.post('/api/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 401
            response_data = json.loads(response.data)
            assert 'error' in response_data
            assert 'Credenciais inválidas' in response_data['error']
    
    def test_register_success(self, client, mock_db_session):
        """
        Teste: Registro com sucesso
        Baseado no endpoint real POST /api/auth/register
        """
        # Arrange - Dados baseados em código real
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        # Mock de usuário não existente
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Mock da geração de hash de senha
        with patch('backend.app.api.auth.generate_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password_123"
            
            # Mock da criação do usuário
            mock_user = Mock()
            mock_user.id = 2
            mock_user.username = "newuser"
            mock_user.email = "newuser@example.com"
            mock_db_session.add.return_value = None
            mock_db_session.commit.return_value = None
            
            # Act
            response = client.post('/api/auth/register',
                                 data=json.dumps(register_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            response_data = json.loads(response.data)
            assert 'message' in response_data
            assert 'Usuário criado com sucesso' in response_data['message']
    
    def test_register_existing_username(self, client, mock_db_session, sample_user):
        """
        Teste: Registro com username já existente
        Baseado no endpoint real POST /api/auth/register
        """
        # Arrange
        register_data = {
            "username": "testuser",  # Username já existe
            "email": "newemail@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        # Mock de usuário já existente
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        response = client.post('/api/auth/register',
                             data=json.dumps(register_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Username já existe' in response_data['error']
    
    def test_register_password_mismatch(self, client):
        """
        Teste: Registro com senhas não coincidentes
        Baseado no endpoint real POST /api/auth/register
        """
        # Arrange
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "differentpassword"  # Senhas diferentes
        }
        
        # Act
        response = client.post('/api/auth/register',
                             data=json.dumps(register_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Senhas não coincidem' in response_data['error']
    
    def test_refresh_token_success(self, client):
        """
        Teste: Refresh de token com sucesso
        Baseado no endpoint real POST /api/auth/refresh
        """
        # Arrange - Token válido
        valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.valid_token"
        
        # Mock da verificação de token
        with patch('backend.app.api.auth.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            # Mock da geração de novo token
            with patch('backend.app.api.auth.create_access_token') as mock_token:
                mock_token.return_value = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.new_token"
                
                # Act
                response = client.post('/api/auth/refresh',
                                     headers={'Authorization': f'Bearer {valid_token}'})
                
                # Assert
                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert 'access_token' in response_data
                assert 'token_type' in response_data
    
    def test_logout_success(self, client):
        """
        Teste: Logout com sucesso
        Baseado no endpoint real POST /api/auth/logout
        """
        # Arrange - Token válido
        valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.valid_token"
        
        # Mock da verificação de token
        with patch('backend.app.api.auth.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            # Mock do blacklist de token
            with patch('backend.app.api.auth.add_token_to_blacklist') as mock_blacklist:
                mock_blacklist.return_value = True
                
                # Act
                response = client.post('/api/auth/logout',
                                     headers={'Authorization': f'Bearer {valid_token}'})
                
                # Assert
                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert 'message' in response_data
                assert 'Logout realizado com sucesso' in response_data['message']
    
    def test_get_user_profile_success(self, client, mock_db_session, sample_user):
        """
        Teste: Obter perfil do usuário com sucesso
        Baseado no endpoint real GET /api/auth/profile
        """
        # Arrange
        valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.valid_token"
        
        # Mock da verificação de token
        with patch('backend.app.api.auth.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            # Mock do usuário atual
            with patch('backend.app.api.auth.get_jwt_identity') as mock_identity:
                mock_identity.return_value = 1
                
                # Mock do usuário encontrado
                mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
                
                # Act
                response = client.get('/api/auth/profile',
                                    headers={'Authorization': f'Bearer {valid_token}'})
                
                # Assert
                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert 'id' in response_data
                assert 'username' in response_data
                assert 'email' in response_data
                assert response_data['username'] == "testuser"
    
    def test_update_user_profile_success(self, client, mock_db_session, sample_user):
        """
        Teste: Atualizar perfil do usuário com sucesso
        Baseado no endpoint real PUT /api/auth/profile
        """
        # Arrange
        valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.valid_token"
        update_data = {
            "email": "updated@example.com",
            "current_password": "password123",
            "new_password": "newpassword123"
        }
        
        # Mock da verificação de token
        with patch('backend.app.api.auth.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            # Mock do usuário atual
            with patch('backend.app.api.auth.get_jwt_identity') as mock_identity:
                mock_identity.return_value = 1
                
                # Mock do usuário encontrado
                mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
                
                # Mock da verificação de senha atual
                with patch('backend.app.api.auth.check_password_hash') as mock_check:
                    mock_check.return_value = True
                    
                    # Mock da geração de novo hash
                    with patch('backend.app.api.auth.generate_password_hash') as mock_hash:
                        mock_hash.return_value = "new_hashed_password"
                        
                        # Act
                        response = client.put('/api/auth/profile',
                                            data=json.dumps(update_data),
                                            content_type='application/json',
                                            headers={'Authorization': f'Bearer {valid_token}'})
                        
                        # Assert
                        assert response.status_code == 200
                        response_data = json.loads(response.data)
                        assert 'message' in response_data
                        assert 'Perfil atualizado com sucesso' in response_data['message']
    
    def test_validate_token_success(self, client):
        """
        Teste: Validação de token com sucesso
        Baseado no endpoint real GET /api/auth/validate
        """
        # Arrange
        valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.valid_token"
        
        # Mock da verificação de token
        with patch('backend.app.api.auth.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            # Mock do usuário atual
            with patch('backend.app.api.auth.get_jwt_identity') as mock_identity:
                mock_identity.return_value = 1
                
                # Act
                response = client.get('/api/auth/validate',
                                    headers={'Authorization': f'Bearer {valid_token}'})
                
                # Assert
                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert 'valid' in response_data
                assert response_data['valid'] == True
                assert 'user_id' in response_data
                assert response_data['user_id'] == 1
    
    def test_validate_token_invalid(self, client):
        """
        Teste: Validação de token inválido
        Baseado no endpoint real GET /api/auth/validate
        """
        # Arrange
        invalid_token = "invalid_token"
        
        # Mock da verificação de token falhando
        with patch('backend.app.api.auth.verify_jwt_in_request') as mock_verify:
            mock_verify.side_effect = Exception("Token inválido")
            
            # Act
            response = client.get('/api/auth/validate',
                                headers={'Authorization': f'Bearer {invalid_token}'})
            
            # Assert
            assert response.status_code == 401
            response_data = json.loads(response.data)
            assert 'valid' in response_data
            assert response_data['valid'] == False
            assert 'error' in response_data 