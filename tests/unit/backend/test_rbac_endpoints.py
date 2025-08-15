"""
🧪 Testes Unitários - Endpoints RBAC

Tracing ID: TEST_RBAC_20250127_001
Data/Hora: 2025-01-27 16:35:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Testes unitários para os endpoints de RBAC (Role-Based Access Control) do sistema Omni Keywords Finder.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime
from backend.app.api.rbac import rbac_bp
from backend.app.models import User, Role, Permission
from backend.app.schemas.rbac import (
    UserCreateRequest, RoleCreateRequest, PermissionCreateRequest
)


class TestRBACEndpoints:
    """Testes para endpoints RBAC."""
    
    @pytest.fixture
    def app(self):
        """Fixture para criar aplicação Flask de teste."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Registrar blueprint
        app.register_blueprint(rbac_bp)
        
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
        return user
    
    @pytest.fixture
    def mock_role(self):
        """Fixture para role mock."""
        role = Mock(spec=Role)
        role.id = 1
        role.nome = 'admin'
        role.descricao = 'Administrador do sistema'
        return role
    
    @pytest.fixture
    def mock_permission(self):
        """Fixture para permissão mock."""
        permission = Mock(spec=Permission)
        permission.id = 1
        permission.nome = 'user_create'
        permission.descricao = 'Criar usuários'
        return permission
    
    @patch('backend.app.api.rbac.role_required')
    def test_listar_usuarios_success(self, mock_role_required, client, mock_user):
        """Teste de listagem de usuários bem-sucedida."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.filter.return_value.order_by.return_value.paginate.return_value = Mock(
                items=[mock_user],
                total=1,
                pages=1,
                has_prev=False,
                has_next=False
            )
            
            # Fazer requisição
            response = client.get('/api/rbac/usuarios?page=1&per_page=10')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'usuarios' in data
            assert 'paginacao' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_listar_usuarios_with_filters(self, mock_role_required, client, mock_user):
        """Teste de listagem de usuários com filtros."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.filter.return_value.order_by.return_value.paginate.return_value = Mock(
                items=[mock_user],
                total=1,
                pages=1,
                has_prev=False,
                has_next=False
            )
            
            # Fazer requisição com filtros
            response = client.get('/api/rbac/usuarios?ativo=true&username=test&page=1&per_page=10')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'usuarios' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_criar_usuario_success(self, mock_role_required, client):
        """Teste de criação de usuário bem-sucedida."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query, \
             patch('backend.app.api.rbac.db') as mock_db, \
             patch('backend.app.api.rbac.generate_password_hash') as mock_hash, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.filter_by.return_value.first.return_value = None  # Usuário não existe
            mock_hash.return_value = 'hashed_password'
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            user_data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'senha': 'SecurePass123!',
                'roles': [1, 2]
            }
            
            # Fazer requisição
            response = client.post('/api/rbac/usuarios', 
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'usuario' in data
            assert data['usuario']['username'] == 'newuser'
    
    @patch('backend.app.api.rbac.role_required')
    def test_criar_usuario_duplicate_username(self, mock_role_required, client, mock_user):
        """Teste de criação de usuário com username duplicado."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query:
            # Configurar mock para usuário já existente
            mock_user_query.filter_by.return_value.first.return_value = mock_user
            
            # Dados de teste
            user_data = {
                'username': 'testuser',  # Username já existe
                'email': 'newuser@example.com',
                'senha': 'SecurePass123!',
                'roles': [1]
            }
            
            # Fazer requisição
            response = client.post('/api/rbac/usuarios', 
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 409
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_editar_usuario_success(self, mock_role_required, client, mock_user):
        """Teste de edição de usuário bem-sucedida."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query, \
             patch('backend.app.api.rbac.db') as mock_db, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get_or_404.return_value = mock_user
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            user_data = {
                'email': 'updated@example.com',
                'ativo': True,
                'roles': [1, 2]
            }
            
            # Fazer requisição
            response = client.put('/api/rbac/usuarios/1', 
                                data=json.dumps(user_data),
                                content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'usuario' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_editar_usuario_not_found(self, mock_role_required, client):
        """Teste de edição de usuário não encontrado."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query:
            # Configurar mock para usuário não encontrado
            mock_user_query.get_or_404.side_effect = Exception('Not found')
            
            # Dados de teste
            user_data = {
                'email': 'updated@example.com',
                'ativo': True
            }
            
            # Fazer requisição
            response = client.put('/api/rbac/usuarios/999', 
                                data=json.dumps(user_data),
                                content_type='application/json')
            
            # Verificações
            assert response.status_code == 404
    
    @patch('backend.app.api.rbac.role_required')
    def test_remover_usuario_success(self, mock_role_required, client, mock_user):
        """Teste de remoção de usuário bem-sucedida."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query, \
             patch('backend.app.api.rbac.verificar_integridade_referencial_user') as mock_integrity, \
             patch('backend.app.api.rbac.db') as mock_db, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get_or_404.return_value = mock_user
            mock_integrity.return_value = {'pode_excluir': True, 'dependencias': []}
            mock_db.session.delete.return_value = None
            mock_db.session.commit.return_value = None
            
            # Fazer requisição
            response = client.delete('/api/rbac/usuarios/1')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'mensagem' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_remover_usuario_with_dependencies(self, mock_role_required, client, mock_user):
        """Teste de remoção de usuário com dependências."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query, \
             patch('backend.app.api.rbac.verificar_integridade_referencial_user') as mock_integrity:
            
            # Configurar mocks
            mock_user_query.get_or_404.return_value = mock_user
            mock_integrity.return_value = {
                'pode_excluir': False, 
                'dependencias': ['execucoes', 'pagamentos']
            }
            
            # Fazer requisição
            response = client.delete('/api/rbac/usuarios/1')
            
            # Verificações
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'erro' in data
            assert 'dependencias' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_listar_papeis_success(self, mock_role_required, client, mock_role):
        """Teste de listagem de papéis bem-sucedida."""
        with patch('backend.app.api.rbac.Role.query') as mock_role_query, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_role_query.all.return_value = [mock_role]
            
            # Fazer requisição
            response = client.get('/api/rbac/papeis')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'papeis' in data
            assert len(data['papeis']) == 1
    
    @patch('backend.app.api.rbac.role_required')
    def test_criar_papel_success(self, mock_role_required, client):
        """Teste de criação de papel bem-sucedida."""
        with patch('backend.app.api.rbac.Role.query') as mock_role_query, \
             patch('backend.app.api.rbac.db') as mock_db, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_role_query.filter_by.return_value.first.return_value = None  # Papel não existe
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            role_data = {
                'nome': 'moderator',
                'descricao': 'Moderador do sistema',
                'permissoes': [1, 2, 3]
            }
            
            # Fazer requisição
            response = client.post('/api/rbac/papeis', 
                                 data=json.dumps(role_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'papel' in data
            assert data['papel']['nome'] == 'moderator'
    
    @patch('backend.app.api.rbac.role_required')
    def test_criar_papel_duplicate_name(self, mock_role_required, client, mock_role):
        """Teste de criação de papel com nome duplicado."""
        with patch('backend.app.api.rbac.Role.query') as mock_role_query:
            # Configurar mock para papel já existente
            mock_role_query.filter_by.return_value.first.return_value = mock_role
            
            # Dados de teste
            role_data = {
                'nome': 'admin',  # Nome já existe
                'descricao': 'Novo administrador',
                'permissoes': [1, 2]
            }
            
            # Fazer requisição
            response = client.post('/api/rbac/papeis', 
                                 data=json.dumps(role_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 409
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_editar_papel_success(self, mock_role_required, client, mock_role):
        """Teste de edição de papel bem-sucedida."""
        with patch('backend.app.api.rbac.Role.query') as mock_role_query, \
             patch('backend.app.api.rbac.db') as mock_db, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_role_query.get_or_404.return_value = mock_role
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            role_data = {
                'descricao': 'Administrador atualizado',
                'permissoes': [1, 2, 3, 4]
            }
            
            # Fazer requisição
            response = client.put('/api/rbac/papeis/1', 
                                data=json.dumps(role_data),
                                content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'papel' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_remover_papel_success(self, mock_role_required, client, mock_role):
        """Teste de remoção de papel bem-sucedida."""
        with patch('backend.app.api.rbac.Role.query') as mock_role_query, \
             patch('backend.app.api.rbac.verificar_integridade_referencial_role') as mock_integrity, \
             patch('backend.app.api.rbac.db') as mock_db, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_role_query.get_or_404.return_value = mock_role
            mock_integrity.return_value = {'pode_excluir': True, 'dependencias': []}
            mock_db.session.delete.return_value = None
            mock_db.session.commit.return_value = None
            
            # Fazer requisição
            response = client.delete('/api/rbac/papeis/1')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'mensagem' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_listar_permissoes_success(self, mock_role_required, client, mock_permission):
        """Teste de listagem de permissões bem-sucedida."""
        with patch('backend.app.api.rbac.Permission.query') as mock_permission_query, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_permission_query.all.return_value = [mock_permission]
            
            # Fazer requisição
            response = client.get('/api/rbac/permissoes')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'permissoes' in data
            assert len(data['permissoes']) == 1
    
    @patch('backend.app.api.rbac.role_required')
    def test_criar_permissao_success(self, mock_role_required, client):
        """Teste de criação de permissão bem-sucedida."""
        with patch('backend.app.api.rbac.Permission.query') as mock_permission_query, \
             patch('backend.app.api.rbac.db') as mock_db, \
             patch('backend.app.api.rbac.log_event') as mock_log:
            
            # Configurar mocks
            mock_permission_query.filter_by.return_value.first.return_value = None  # Permissão não existe
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            permission_data = {
                'nome': 'user_delete',
                'descricao': 'Excluir usuários'
            }
            
            # Fazer requisição
            response = client.post('/api/rbac/permissoes', 
                                 data=json.dumps(permission_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'permissao' in data
            assert data['permissao']['nome'] == 'user_delete'


class TestRBACSchemas:
    """Testes para schemas RBAC."""
    
    def test_user_create_request_valid(self):
        """Teste de schema de criação de usuário válido."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'senha': 'SecurePass123!',
            'roles': [1, 2]
        }
        
        request = UserCreateRequest(**data)
        
        assert request.username == 'testuser'
        assert request.email == 'test@example.com'
        assert request.senha == 'SecurePass123!'
        assert request.roles == [1, 2]
    
    def test_user_create_request_invalid_username(self):
        """Teste de schema de criação com username inválido."""
        data = {
            'username': 'a',  # Muito curto
            'email': 'test@example.com',
            'senha': 'SecurePass123!',
            'roles': [1]
        }
        
        with pytest.raises(ValueError):
            UserCreateRequest(**data)
    
    def test_role_create_request_valid(self):
        """Teste de schema de criação de role válido."""
        data = {
            'nome': 'moderator',
            'descricao': 'Moderador do sistema',
            'permissoes': [1, 2, 3]
        }
        
        request = RoleCreateRequest(**data)
        
        assert request.nome == 'moderator'
        assert request.descricao == 'Moderador do sistema'
        assert request.permissoes == [1, 2, 3]
    
    def test_permission_create_request_valid(self):
        """Teste de schema de criação de permissão válido."""
        data = {
            'nome': 'user_delete',
            'descricao': 'Excluir usuários'
        }
        
        request = PermissionCreateRequest(**data)
        
        assert request.nome == 'user_delete'
        assert request.descricao == 'Excluir usuários'


class TestRBACValidation:
    """Testes de validação RBAC."""
    
    def test_sanitizar_username(self):
        """Teste de sanitização de username."""
        from backend.app.api.rbac import sanitizar_username
        
        # Teste de sanitização básica
        result = sanitizar_username('  TestUser123  ')
        assert result == 'TestUser123'
        
        # Teste de caracteres especiais
        result = sanitizar_username('test<script>alert("xss")</script>')
        assert '<script>' not in result
        
        # Teste de comprimento máximo
        long_username = 'a' * 100
        result = sanitizar_username(long_username)
        assert len(result) <= 64
    
    def test_sanitizar_email(self):
        """Teste de sanitização de email."""
        from backend.app.api.rbac import sanitizar_email
        
        # Teste de sanitização básica
        result = sanitizar_email('  TEST@EXAMPLE.COM  ')
        assert result == 'test@example.com'
        
        # Teste de caracteres perigosos
        with pytest.raises(ValueError):
            sanitizar_email('test<script>@example.com')
    
    def test_sanitizar_role_name(self):
        """Teste de sanitização de nome de role."""
        from backend.app.api.rbac import sanitizar_role_name
        
        # Teste de sanitização básica
        result = sanitizar_role_name('  Test-Role_123  ')
        assert result == 'Test-Role_123'
        
        # Teste de caracteres especiais
        result = sanitizar_role_name('test<script>alert("xss")</script>')
        assert '<script>' not in result


class TestRBACErrorHandling:
    """Testes de tratamento de erros RBAC."""
    
    @patch('backend.app.api.rbac.role_required')
    def test_database_error_handling(self, mock_role_required, client):
        """Teste de tratamento de erro de banco de dados."""
        with patch('backend.app.api.rbac.User.query') as mock_user_query:
            # Configurar mock para simular erro de banco
            mock_user_query.filter.side_effect = Exception('Database error')
            
            # Fazer requisição
            response = client.get('/api/rbac/usuarios')
            
            # Verificações
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.api.rbac.role_required')
    def test_validation_error_handling(self, mock_role_required, client):
        """Teste de tratamento de erro de validação."""
        # Dados inválidos
        user_data = {
            'username': '',  # Username vazio
            'email': 'invalid-email',
            'senha': '123'  # Senha muito curta
        }
        
        # Fazer requisição
        response = client.post('/api/rbac/usuarios', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data


class TestRBACSecurity:
    """Testes de segurança RBAC."""
    
    def test_sql_injection_protection(self, client):
        """Teste de proteção contra SQL injection."""
        # Tentativa de SQL injection no username
        malicious_username = "'; DROP TABLE users; --"
        
        user_data = {
            'username': malicious_username,
            'email': 'test@example.com',
            'senha': 'SecurePass123!',
            'roles': [1]
        }
        
        # Fazer requisição
        response = client.post('/api/rbac/usuarios', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_xss_protection(self, client):
        """Teste de proteção contra XSS."""
        # Tentativa de XSS no descrição
        malicious_description = '<script>alert("xss")</script>'
        
        role_data = {
            'nome': 'testrole',
            'descricao': malicious_description,
            'permissoes': [1]
        }
        
        # Fazer requisição
        response = client.post('/api/rbac/papeis', 
                             data=json.dumps(role_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data


# Configuração do pytest
pytestmark = pytest.mark.unit 