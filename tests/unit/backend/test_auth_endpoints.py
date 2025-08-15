"""
🧪 Testes Unitários - Endpoints de Autenticação

Tracing ID: TEST_AUTH_20250127_001
Data/Hora: 2025-01-27 15:50:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Testes unitários para os endpoints de autenticação do sistema Omni Keywords Finder.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from backend.app.api.auth import auth_bp, init_jwt, init_oauth
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest


class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""
    
    @pytest.fixture
    def app(self):
        """Fixture para criar aplicação Flask de teste."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test-secret-key-for-testing-only'
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
        
        # Registrar blueprint
        app.register_blueprint(auth_bp)
        
        # Inicializar JWT
        init_jwt(app)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Fixture para cliente de teste."""
        return app.test_client()
    
    @pytest.fixture
    def mock_user(self):
        """Fixture para usuário mock."""
        user = Mock(spec=User)
        user.id = 1
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.ativo = True
        user.senha_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2.'
        return user
    
    def test_login_success(self, client, mock_user):
        """Teste de login bem-sucedido."""
        with patch('backend.app.api.auth.User.query') as mock_query, \
             patch('backend.app.api.auth.check_password_hash') as mock_check, \
             patch('backend.app.api.auth.create_access_token') as mock_token, \
             patch('backend.app.api.auth.security_logger') as mock_logger:
            
            # Configurar mocks
            mock_query.filter_by.return_value.first.return_value = mock_user
            mock_check.return_value = True
            mock_token.return_value = 'test-jwt-token'
            
            # Dados de teste
            login_data = {
                'username': 'testuser',
                'senha': 'testpassword'
            }
            
            # Fazer requisição
            response = client.post('/api/auth/login', 
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'access_token' in data
            assert data['user_id'] == 1
            
            # Verificar se logs foram chamados
            mock_logger.log_event.assert_called()
    
    def test_login_invalid_credentials(self, client):
        """Teste de login com credenciais inválidas."""
        with patch('backend.app.api.auth.User.query') as mock_query, \
             patch('backend.app.api.auth.security_logger') as mock_logger:
            
            # Configurar mock para usuário não encontrado
            mock_query.filter_by.return_value.first.return_value = None
            
            # Dados de teste
            login_data = {
                'username': 'invaliduser',
                'senha': 'wrongpassword'
            }
            
            # Fazer requisição
            response = client.post('/api/auth/login', 
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'erro' in data
            
            # Verificar se logs de segurança foram chamados
            mock_logger.log_event.assert_called()
    
    def test_login_inactive_user(self, client, mock_user):
        """Teste de login com usuário inativo."""
        with patch('backend.app.api.auth.User.query') as mock_query, \
             patch('backend.app.api.auth.check_password_hash') as mock_check, \
             patch('backend.app.api.auth.security_logger') as mock_logger:
            
            # Configurar usuário inativo
            mock_user.ativo = False
            mock_query.filter_by.return_value.first.return_value = mock_user
            mock_check.return_value = True
            
            # Dados de teste
            login_data = {
                'username': 'testuser',
                'senha': 'testpassword'
            }
            
            # Fazer requisição
            response = client.post('/api/auth/login', 
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 403
            data = json.loads(response.data)
            assert 'erro' in data
            
            # Verificar se logs de segurança foram chamados
            mock_logger.log_event.assert_called()
    
    def test_login_missing_data(self, client):
        """Teste de login com dados ausentes."""
        # Dados incompletos
        login_data = {
            'username': 'testuser'
            # senha ausente
        }
        
        # Fazer requisição
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
    
    def test_login_invalid_json(self, client):
        """Teste de login com JSON inválido."""
        # Fazer requisição com JSON inválido
        response = client.post('/api/auth/login', 
                             data='invalid json',
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
    
    @patch('backend.app.api.auth.jwt_required')
    def test_logout_success(self, mock_jwt_required, client):
        """Teste de logout bem-sucedido."""
        with patch('backend.app.api.auth.get_jwt_identity') as mock_identity, \
             patch('backend.app.api.auth.security_logger') as mock_logger:
            
            # Configurar mocks
            mock_identity.return_value = 1
            
            # Fazer requisição
            response = client.post('/api/auth/logout')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'msg' in data
            
            # Verificar se logs foram chamados
            mock_logger.log_event.assert_called()
    
    def test_oauth2_login_google(self, client):
        """Teste de início de login OAuth2 Google."""
        with patch('backend.app.api.auth.oauth') as mock_oauth:
            # Configurar mock
            mock_client = Mock()
            mock_oauth.create_client.return_value = mock_client
            mock_client.authorize_redirect.return_value = Mock()
            
            # Fazer requisição
            response = client.get('/api/auth/oauth2/login/google')
            
            # Verificações
            mock_oauth.create_client.assert_called_with('google')
            mock_client.authorize_redirect.assert_called()
    
    def test_oauth2_login_github(self, client):
        """Teste de início de login OAuth2 GitHub."""
        with patch('backend.app.api.auth.oauth') as mock_oauth:
            # Configurar mock
            mock_client = Mock()
            mock_oauth.create_client.return_value = mock_client
            mock_client.authorize_redirect.return_value = Mock()
            
            # Fazer requisição
            response = client.get('/api/auth/oauth2/login/github')
            
            # Verificações
            mock_oauth.create_client.assert_called_with('github')
            mock_client.authorize_redirect.assert_called()
    
    def test_oauth2_login_invalid_provider(self, client):
        """Teste de login OAuth2 com provedor inválido."""
        with patch('backend.app.api.auth.oauth') as mock_oauth:
            # Configurar mock para erro
            mock_oauth.create_client.side_effect = Exception('Invalid provider')
            
            # Fazer requisição
            response = client.get('/api/auth/oauth2/login/invalid')
            
            # Verificações
            assert response.status_code == 500
    
    def test_oauth2_callback_google(self, client):
        """Teste de callback OAuth2 Google."""
        with patch('backend.app.api.auth.oauth') as mock_oauth, \
             patch('backend.app.api.auth.User.query') as mock_query, \
             patch('backend.app.api.auth.create_access_token') as mock_token:
            
            # Configurar mocks
            mock_client = Mock()
            mock_oauth.create_client.return_value = mock_client
            mock_client.authorize_access_token.return_value = {'access_token': 'test'}
            mock_client.parse_id_token.return_value = {
                'sub': '12345',
                'email': 'test@example.com',
                'name': 'Test User'
            }
            mock_query.filter_by.return_value.first.return_value = None
            mock_token.return_value = 'test-jwt-token'
            
            # Fazer requisição
            response = client.get('/api/auth/oauth2/callback/google')
            
            # Verificações
            mock_oauth.create_client.assert_called_with('google')
            mock_client.authorize_access_token.assert_called()
    
    def test_oauth2_callback_github(self, client):
        """Teste de callback OAuth2 GitHub."""
        with patch('backend.app.api.auth.oauth') as mock_oauth, \
             patch('backend.app.api.auth.User.query') as mock_query, \
             patch('backend.app.api.auth.create_access_token') as mock_token:
            
            # Configurar mocks
            mock_client = Mock()
            mock_oauth.create_client.return_value = mock_client
            mock_client.authorize_access_token.return_value = {'access_token': 'test'}
            mock_client.get.return_value.json.return_value = {
                'id': 12345,
                'email': 'test@example.com',
                'login': 'testuser'
            }
            mock_query.filter_by.return_value.first.return_value = None
            mock_token.return_value = 'test-jwt-token'
            
            # Fazer requisição
            response = client.get('/api/auth/oauth2/callback/github')
            
            # Verificações
            mock_oauth.create_client.assert_called_with('github')
            mock_client.authorize_access_token.assert_called()
    
    def test_oauth2_callback_invalid_provider(self, client):
        """Teste de callback OAuth2 com provedor inválido."""
        with patch('backend.app.api.auth.oauth') as mock_oauth:
            # Configurar mock para erro
            mock_oauth.create_client.side_effect = Exception('Invalid provider')
            
            # Fazer requisição
            response = client.get('/api/auth/oauth2/callback/invalid')
            
            # Verificações
            assert response.status_code == 500


class TestAuthSchemas:
    """Testes para schemas de autenticação."""
    
    def test_login_request_valid(self):
        """Teste de schema de login válido."""
        data = {
            'username': 'testuser',
            'senha': 'testpassword'
        }
        
        login_request = LoginRequest(**data)
        
        assert login_request.username == 'testuser'
        assert login_request.senha == 'testpassword'
    
    def test_login_request_invalid_username(self):
        """Teste de schema de login com username inválido."""
        data = {
            'username': '',  # Username vazio
            'senha': 'testpassword'
        }
        
        with pytest.raises(ValueError):
            LoginRequest(**data)
    
    def test_login_request_invalid_password(self):
        """Teste de schema de login com senha inválida."""
        data = {
            'username': 'testuser',
            'senha': ''  # Senha vazia
        }
        
        with pytest.raises(ValueError):
            LoginRequest(**data)
    
    def test_login_request_missing_fields(self):
        """Teste de schema de login com campos ausentes."""
        data = {
            'username': 'testuser'
            # senha ausente
        }
        
        with pytest.raises(ValueError):
            LoginRequest(**data)


class TestAuthSecurity:
    """Testes de segurança para autenticação."""
    
    def test_jwt_secret_key_validation(self):
        """Teste de validação da chave secreta JWT."""
        with pytest.raises(ValueError):
            # Tentar inicializar JWT sem chave secreta
            app = Flask(__name__)
            app.config['JWT_SECRET_KEY'] = None
            init_jwt(app)
    
    def test_jwt_secret_key_default_value(self):
        """Teste de validação da chave secreta padrão."""
        with pytest.raises(ValueError):
            # Tentar inicializar JWT com chave padrão
            app = Flask(__name__)
            app.config['JWT_SECRET_KEY'] = 'troque-por-uma-chave-segura'
            init_jwt(app)
    
    def test_rate_limiting_auth(self, client):
        """Teste de rate limiting para endpoints de auth."""
        # Fazer múltiplas requisições rapidamente
        for _ in range(10):
            response = client.post('/api/auth/login', 
                                 data=json.dumps({
                                     'username': 'testuser',
                                     'senha': 'testpassword'
                                 }),
                                 content_type='application/json')
        
        # Verificar se rate limiting foi aplicado
        # (implementação depende da configuração específica)


class TestAuthErrorHandling:
    """Testes de tratamento de erros para autenticação."""
    
    def test_database_error_handling(self, client):
        """Teste de tratamento de erro de banco de dados."""
        with patch('backend.app.api.auth.User.query') as mock_query:
            # Configurar mock para simular erro de banco
            mock_query.filter_by.side_effect = Exception('Database error')
            
            # Dados de teste
            login_data = {
                'username': 'testuser',
                'senha': 'testpassword'
            }
            
            # Fazer requisição
            response = client.post('/api/auth/login', 
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500
    
    def test_oauth_error_handling(self, client):
        """Teste de tratamento de erro OAuth."""
        with patch('backend.app.api.auth.oauth') as mock_oauth:
            # Configurar mock para simular erro OAuth
            mock_oauth.create_client.side_effect = Exception('OAuth error')
            
            # Fazer requisição
            response = client.get('/api/auth/oauth2/login/google')
            
            # Verificações
            assert response.status_code == 500


# Configuração do pytest
pytestmark = pytest.mark.unit 