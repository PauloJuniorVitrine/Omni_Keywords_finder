"""
🧪 Testes Unitários - Admin API
🎯 Objetivo: Testar endpoints administrativos
📅 Data: 2025-01-27
🔗 Tracing ID: TEST_ADMIN_API_001
📋 Ruleset: enterprise_control_layer.yaml

Testes:
- Gestão de usuários
- Configuração do sistema
- Monitoramento administrativo
- Relatórios administrativos
- Permissões e autenticação
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.api.admin_api import admin_api_bp, AdminAction, UserManagementData, SystemConfigData
from app.models.user import User
from app.models.execution import Execution
from app.models.payment import Payment

# Configuração do teste
@pytest.fixture
def app():
    """Cria aplicação Flask para testes"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Registrar blueprint
    app.register_blueprint(admin_api_bp)
    
    return app

@pytest.fixture
def client(app):
    """Cliente de teste"""
    return app.test_client()

@pytest.fixture
def mock_auth():
    """Mock de autenticação"""
    with patch('app.api.admin_api.get_user_id_from_token') as mock_get_user:
        with patch('app.api.admin_api.has_admin_permission') as mock_permission:
            mock_get_user.return_value = 'admin_user_001'
            mock_permission.return_value = True
            yield {
                'get_user': mock_get_user,
                'permission': mock_permission
            }

@pytest.fixture
def mock_audit_logger():
    """Mock do audit logger"""
    with patch('app.api.admin_api.audit_logger') as mock_logger:
        mock_logger.log_admin_action = Mock()
        yield mock_logger

@pytest.fixture
def sample_user_data():
    """Dados de exemplo de usuário"""
    return {
        'id': 'user_001',
        'username': 'testuser',
        'email': 'test@example.com',
        'full_name': 'Test User',
        'role': 'user',
        'status': 'active',
        'created_at': datetime.utcnow(),
        'last_login': datetime.utcnow(),
        'is_active': True,
        'email_verified': True
    }

@pytest.fixture
def sample_execution_data():
    """Dados de exemplo de execução"""
    return {
        'id': 'exec_001',
        'user_id': 'user_001',
        'status': 'completed',
        'created_at': datetime.utcnow(),
        'completed_at': datetime.utcnow(),
        'keywords_count': 100,
        'clusters_count': 10
    }

@pytest.fixture
def sample_payment_data():
    """Dados de exemplo de pagamento"""
    return {
        'id': 'payment_001',
        'user_id': 'user_001',
        'amount': 99.99,
        'status': 'completed',
        'created_at': datetime.utcnow(),
        'payment_method': 'credit_card'
    }

# ============================================================================
# TESTES DE GESTÃO DE USUÁRIOS
# ============================================================================

class TestUserManagement:
    """Testes para gestão de usuários"""
    
    def test_get_users_success(self, client, mock_auth, mock_audit_logger):
        """Testa listagem de usuários com sucesso"""
        # Mock da query de usuários
        with patch('app.api.admin_api.User') as mock_user:
            mock_user.query.count.return_value = 1
            mock_user.query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
                Mock(
                    id='user_001',
                    username='testuser',
                    email='test@example.com',
                    full_name='Test User',
                    role='user',
                    status='active',
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                    is_active=True,
                    email_verified=True
                )
            ]
            
            response = client.get('/admin/api/v1/users')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'users' in data['data']
            assert 'pagination' in data['data']
            assert len(data['data']['users']) == 1
    
    def test_get_users_invalid_page(self, client, mock_auth):
        """Testa listagem com página inválida"""
        response = client.get('/admin/api/v1/users?page=0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Página deve ser maior que 0' in data['error']
    
    def test_get_users_invalid_per_page(self, client, mock_auth):
        """Testa listagem com itens por página inválidos"""
        response = client.get('/admin/api/v1/users?per_page=0')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Itens por página deve estar entre 1 e 100' in data['error']
    
    def test_get_user_details_success(self, client, mock_auth, mock_audit_logger):
        """Testa obtenção de detalhes de usuário com sucesso"""
        with patch('app.api.admin_api.User') as mock_user:
            with patch('app.api.admin_api.Execution') as mock_execution:
                with patch('app.api.admin_api.Payment') as mock_payment:
                    # Mock do usuário
                    mock_user.query.get.return_value = Mock(
                        id='user_001',
                        username='testuser',
                        email='test@example.com',
                        full_name='Test User',
                        role='user',
                        status='active',
                        created_at=datetime.utcnow(),
                        last_login=datetime.utcnow(),
                        is_active=True,
                        email_verified=True
                    )
                    
                    # Mock das contagens
                    mock_execution.query.filter_by.count.return_value = 10
                    mock_payment.query.filter_by.count.return_value = 5
                    
                    response = client.get('/admin/api/v1/users/user_001')
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert data['data']['id'] == 'user_001'
                    assert 'statistics' in data['data']
                    assert data['data']['statistics']['executions_count'] == 10
                    assert data['data']['statistics']['payments_count'] == 5
    
    def test_get_user_details_not_found(self, client, mock_auth):
        """Testa obtenção de usuário inexistente"""
        with patch('app.api.admin_api.User') as mock_user:
            mock_user.query.get.return_value = None
            
            response = client.get('/admin/api/v1/users/nonexistent')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Usuário não encontrado' in data['error']
    
    def test_update_user_status_success(self, client, mock_auth, mock_audit_logger):
        """Testa atualização de status de usuário com sucesso"""
        with patch('app.api.admin_api.User') as mock_user:
            with patch('app.api.admin_api.db') as mock_db:
                # Mock do usuário
                mock_user_instance = Mock(
                    id='user_001',
                    status='active',
                    updated_at=None
                )
                mock_user.query.get.return_value = mock_user_instance
                
                response = client.put(
                    '/admin/api/v1/users/user_001/status',
                    json={'status': 'suspended', 'reason': 'Test suspension'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'Status do usuário atualizado' in data['message']
                assert data['data']['old_status'] == 'active'
                assert data['data']['new_status'] == 'suspended'
                
                # Verificar se o mock foi chamado corretamente
                assert mock_user_instance.status == 'suspended'
                assert mock_user_instance.updated_at is not None
                mock_db.session.commit.assert_called_once()
    
    def test_update_user_status_invalid_status(self, client, mock_auth):
        """Testa atualização com status inválido"""
        response = client.put(
            '/admin/api/v1/users/user_001/status',
            json={'status': 'invalid_status'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Status inválido' in data['error']
    
    def test_update_user_status_missing_data(self, client, mock_auth):
        """Testa atualização sem dados"""
        response = client.put('/admin/api/v1/users/user_001/status')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Dados necessários' in data['error']

# ============================================================================
# TESTES DE CONFIGURAÇÃO DO SISTEMA
# ============================================================================

class TestSystemConfig:
    """Testes para configuração do sistema"""
    
    def test_get_system_config_success(self, client, mock_auth):
        """Testa obtenção de configurações do sistema"""
        response = client.get('/admin/api/v1/system/config')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'app_name' in data['data']
        assert 'version' in data['data']
        assert 'environment' in data['data']
        assert data['data']['app_name'] == 'Omni Keywords Finder'
    
    def test_update_system_config_success(self, client, mock_auth, mock_audit_logger):
        """Testa atualização de configurações do sistema"""
        config_data = {
            'maintenance_mode': True,
            'rate_limit_requests': 200,
            'session_timeout': 7200
        }
        
        response = client.put(
            '/admin/api/v1/system/config',
            json=config_data
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Configurações atualizadas' in data['message']
        assert data['data'] == config_data
    
    def test_update_system_config_invalid_configs(self, client, mock_auth):
        """Testa atualização com configurações inválidas"""
        config_data = {
            'invalid_config': 'value'
        }
        
        response = client.put(
            '/admin/api/v1/system/config',
            json=config_data
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Nenhuma configuração válida' in data['error']
    
    def test_update_system_config_missing_data(self, client, mock_auth):
        """Testa atualização sem dados"""
        response = client.put('/admin/api/v1/system/config')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Dados necessários' in data['error']

# ============================================================================
# TESTES DE MONITORAMENTO ADMINISTRATIVO
# ============================================================================

class TestMonitoring:
    """Testes para monitoramento administrativo"""
    
    def test_get_monitoring_overview_success(self, client, mock_auth):
        """Testa obtenção de visão geral do monitoramento"""
        with patch('app.api.admin_api.User') as mock_user:
            with patch('app.api.admin_api.Execution') as mock_execution:
                with patch('app.api.admin_api.Payment') as mock_payment:
                    # Mock das contagens
                    mock_user.query.count.return_value = 100
                    mock_user.query.filter_by.count.return_value = 80
                    mock_execution.query.count.return_value = 1000
                    mock_payment.query.count.return_value = 500
                    
                    # Mock de execuções recentes
                    mock_execution.query.filter.return_value.count.return_value = 50
                    mock_payment.query.filter.return_value.count.return_value = 25
                    mock_user.query.filter.return_value.count.return_value = 10
                    
                    response = client.get('/admin/api/v1/monitoring/overview')
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert 'users' in data['data']
                    assert 'executions' in data['data']
                    assert 'payments' in data['data']
                    assert 'system' in data['data']
                    assert data['data']['users']['total'] == 100
                    assert data['data']['users']['active'] == 80
    
    def test_get_system_alerts_success(self, client, mock_auth):
        """Testa obtenção de alertas do sistema"""
        response = client.get('/admin/api/v1/monitoring/alerts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'alerts' in data['data']
        assert 'total' in data['data']
        assert 'unacknowledged' in data['data']
        assert isinstance(data['data']['alerts'], list)

# ============================================================================
# TESTES DE RELATÓRIOS ADMINISTRATIVOS
# ============================================================================

class TestReports:
    """Testes para relatórios administrativos"""
    
    def test_get_users_report_success(self, client, mock_auth):
        """Testa geração de relatório de usuários"""
        with patch('app.api.admin_api.User') as mock_user:
            # Mock de usuários
            mock_users = [
                Mock(
                    id='user_001',
                    username='user1',
                    email='user1@example.com',
                    role='user',
                    status='active',
                    created_at=datetime.utcnow()
                ),
                Mock(
                    id='user_002',
                    username='user2',
                    email='user2@example.com',
                    role='admin',
                    status='active',
                    created_at=datetime.utcnow()
                )
            ]
            mock_user.query.all.return_value = mock_users
            mock_user.query.filter.return_value.all.return_value = mock_users
            
            response = client.get('/admin/api/v1/reports/users')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'summary' in data['data']
            assert 'by_role' in data['data']
            assert 'by_month' in data['data']
            assert data['data']['summary']['total_users'] == 2
            assert data['data']['summary']['active_users'] == 2
    
    def test_get_executions_report_success(self, client, mock_auth):
        """Testa geração de relatório de execuções"""
        with patch('app.api.admin_api.Execution') as mock_execution:
            # Mock de execuções
            mock_executions = [
                Mock(
                    id='exec_001',
                    status='completed',
                    created_at=datetime.utcnow()
                ),
                Mock(
                    id='exec_002',
                    status='failed',
                    created_at=datetime.utcnow()
                )
            ]
            mock_execution.query.all.return_value = mock_executions
            mock_execution.query.filter.return_value.all.return_value = mock_executions
            
            response = client.get('/admin/api/v1/reports/executions')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'summary' in data['data']
            assert 'by_status' in data['data']
            assert 'by_day' in data['data']
            assert data['data']['summary']['total_executions'] == 2
            assert data['data']['summary']['successful_executions'] == 1
            assert data['data']['summary']['failed_executions'] == 1

# ============================================================================
# TESTES DE AUTENTICAÇÃO E PERMISSÕES
# ============================================================================

class TestAuthentication:
    """Testes para autenticação e permissões"""
    
    def test_missing_auth_header(self, client):
        """Testa acesso sem header de autenticação"""
        response = client.get('/admin/api/v1/users')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Token de autenticação necessário' in data['error']
    
    def test_invalid_auth_header(self, client):
        """Testa acesso com header de autenticação inválido"""
        response = client.get(
            '/admin/api/v1/users',
            headers={'Authorization': 'Invalid token'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Token inválido' in data['error']
    
    def test_insufficient_permissions(self, client):
        """Testa acesso com permissões insuficientes"""
        with patch('app.api.admin_api.get_user_id_from_token') as mock_get_user:
            with patch('app.api.admin_api.has_admin_permission') as mock_permission:
                mock_get_user.return_value = 'user_001'
                mock_permission.return_value = False
                
                response = client.get(
                    '/admin/api/v1/users',
                    headers={'Authorization': 'Bearer valid_token'}
                )
                
                assert response.status_code == 403
                data = json.loads(response.data)
                assert data['success'] is False
                assert 'Permissão administrativa necessária' in data['error']

# ============================================================================
# TESTES DE HEALTH CHECK
# ============================================================================

class TestHealthCheck:
    """Testes para health check"""
    
    def test_admin_health_check_success(self, client):
        """Testa health check da API administrativa"""
        response = client.get('/admin/api/v1/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'admin_api'
        assert 'version' in data
        assert 'timestamp' in data
        assert 'endpoints' in data
        assert isinstance(data['endpoints'], list)

# ============================================================================
# TESTES DE SCHEMAS E VALIDAÇÃO
# ============================================================================

class TestSchemas:
    """Testes para schemas de dados"""
    
    def test_user_management_data(self):
        """Testa criação de UserManagementData"""
        data = UserManagementData(
            user_id='user_001',
            action=AdminAction.USER_SUSPEND,
            data={'status': 'suspended'},
            reason='Test suspension',
            admin_id='admin_001'
        )
        
        assert data.user_id == 'user_001'
        assert data.action == AdminAction.USER_SUSPEND
        assert data.data['status'] == 'suspended'
        assert data.reason == 'Test suspension'
        assert data.admin_id == 'admin_001'
    
    def test_system_config_data(self):
        """Testa criação de SystemConfigData"""
        data = SystemConfigData(
            config_key='maintenance_mode',
            config_value=True,
            config_type='boolean',
            description='Enable maintenance mode',
            admin_id='admin_001'
        )
        
        assert data.config_key == 'maintenance_mode'
        assert data.config_value is True
        assert data.config_type == 'boolean'
        assert data.description == 'Enable maintenance mode'
        assert data.admin_id == 'admin_001'

# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

class TestIntegration:
    """Testes de integração"""
    
    def test_full_user_management_flow(self, client, mock_auth, mock_audit_logger):
        """Testa fluxo completo de gestão de usuários"""
        with patch('app.api.admin_api.User') as mock_user:
            with patch('app.api.admin_api.db') as mock_db:
                # Mock para listagem
                mock_user.query.count.return_value = 1
                mock_user.query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
                    Mock(
                        id='user_001',
                        username='testuser',
                        email='test@example.com',
                        full_name='Test User',
                        role='user',
                        status='active',
                        created_at=datetime.utcnow(),
                        last_login=datetime.utcnow(),
                        is_active=True,
                        email_verified=True
                    )
                ]
                
                # Listar usuários
                response = client.get('/admin/api/v1/users')
                assert response.status_code == 200
                
                # Mock para detalhes
                mock_user.query.get.return_value = Mock(
                    id='user_001',
                    username='testuser',
                    email='test@example.com',
                    full_name='Test User',
                    role='user',
                    status='active',
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                    is_active=True,
                    email_verified=True
                )
                
                with patch('app.api.admin_api.Execution') as mock_execution:
                    with patch('app.api.admin_api.Payment') as mock_payment:
                        mock_execution.query.filter_by.count.return_value = 10
                        mock_payment.query.filter_by.count.return_value = 5
                        
                        # Obter detalhes
                        response = client.get('/admin/api/v1/users/user_001')
                        assert response.status_code == 200
                
                # Mock para atualização
                mock_user_instance = Mock(
                    id='user_001',
                    status='active',
                    updated_at=None
                )
                mock_user.query.get.return_value = mock_user_instance
                
                # Atualizar status
                response = client.put(
                    '/admin/api/v1/users/user_001/status',
                    json={'status': 'suspended', 'reason': 'Test'}
                )
                assert response.status_code == 200
                
                # Verificar se audit logger foi chamado
                assert mock_audit_logger.log_admin_action.call_count >= 3 