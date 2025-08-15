"""
Testes unitários para verificação de integridade referencial do RBAC.

Este módulo testa as funções de verificação de integridade referencial
antes de operações de exclusão no sistema RBAC.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.app.api.rbac import (
    verificar_integridade_referencial_user,
    verificar_integridade_referencial_role,
    verificar_integridade_referencial_permission
)
from backend.app.models.user import User
from backend.app.models.role import Role
from backend.app.models.permission import Permission


class TestIntegridadeReferencialUser:
    """Testes para verificação de integridade referencial de usuários."""
    
    @patch('backend.app.api.rbac.User')
    @patch('backend.app.api.rbac.Role')
    def test_verificar_integridade_user_sem_dependencias(self, mock_role, mock_user):
        """Testa verificação quando usuário não tem dependências."""
        # Mock do usuário
        mock_user_instance = Mock()
        mock_user_instance.roles = [Mock(nome='usuario')]
        mock_user.query.get.return_value = mock_user_instance
        
        # Mock da query de admin
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.count.return_value = 2
        mock_user.query = mock_query
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.Execucao', create=True) as mock_execucao:
            mock_execucao.query.filter_by.return_value.count.return_value = 0
            
            with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
                mock_audit.query.filter_by.return_value.count.return_value = 0
                
                result = verificar_integridade_referencial_user(1)
                
                assert result['can_delete'] is True
                assert result['erro'] is None
                assert result['execucoes'] == 0
                assert result['audit_logs'] == 0
                assert result['is_last_admin'] is False
    
    @patch('backend.app.api.rbac.User')
    @patch('backend.app.api.rbac.Role')
    def test_verificar_integridade_user_com_execucoes(self, mock_role, mock_user):
        """Testa verificação quando usuário tem execuções associadas."""
        # Mock do usuário
        mock_user_instance = Mock()
        mock_user_instance.roles = [Mock(nome='usuario')]
        mock_user.query.get.return_value = mock_user_instance
        
        # Mock da query de admin
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.count.return_value = 2
        mock_user.query = mock_query
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.Execucao', create=True) as mock_execucao:
            mock_execucao.query.filter_by.return_value.count.return_value = 5
            
            with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
                mock_audit.query.filter_by.return_value.count.return_value = 0
                
                result = verificar_integridade_referencial_user(1)
                
                assert result['can_delete'] is False
                assert result['erro'] == 'Usuário possui execuções associadas'
                assert result['execucoes'] == 5
    
    @patch('backend.app.api.rbac.User')
    @patch('backend.app.api.rbac.Role')
    def test_verificar_integridade_user_ultimo_admin(self, mock_role, mock_user):
        """Testa verificação quando usuário é o último admin."""
        # Mock do usuário
        mock_user_instance = Mock()
        mock_user_instance.roles = [Mock(nome='admin')]
        mock_user.query.get.return_value = mock_user_instance
        
        # Mock da query de admin
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.count.return_value = 1
        mock_user.query = mock_query
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.Execucao', create=True) as mock_execucao:
            mock_execucao.query.filter_by.return_value.count.return_value = 0
            
            with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
                mock_audit.query.filter_by.return_value.count.return_value = 0
                
                result = verificar_integridade_referencial_user(1)
                
                assert result['can_delete'] is False
                assert result['erro'] == 'Último usuário administrador'
                assert result['is_last_admin'] is True


class TestIntegridadeReferencialRole:
    """Testes para verificação de integridade referencial de papéis."""
    
    @patch('backend.app.api.rbac.Role')
    def test_verificar_integridade_role_sem_dependencias(self, mock_role):
        """Testa verificação quando papel não tem dependências."""
        # Mock do papel
        mock_role_instance = Mock()
        mock_role_instance.users = []
        mock_role_instance.nome = 'editor'
        mock_role.query.get.return_value = mock_role_instance
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
            mock_audit.query.filter_by.return_value.count.return_value = 0
            
            result = verificar_integridade_referencial_role(1)
            
            assert result['can_delete'] is True
            assert result['erro'] is None
            assert result['users'] == 0
            assert result['is_critical'] is False
    
    @patch('backend.app.api.rbac.Role')
    def test_verificar_integridade_role_com_usuarios(self, mock_role):
        """Testa verificação quando papel tem usuários associados."""
        # Mock do papel
        mock_role_instance = Mock()
        mock_role_instance.users = [Mock(username='user1'), Mock(username='user2')]
        mock_role_instance.nome = 'editor'
        mock_role.query.get.return_value = mock_role_instance
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
            mock_audit.query.filter_by.return_value.count.return_value = 0
            
            result = verificar_integridade_referencial_role(1)
            
            assert result['can_delete'] is False
            assert result['erro'] == 'Papel possui usuários associados'
            assert result['users'] == 2
    
    @patch('backend.app.api.rbac.Role')
    def test_verificar_integridade_role_critico(self, mock_role):
        """Testa verificação quando papel é crítico do sistema."""
        # Mock do papel
        mock_role_instance = Mock()
        mock_role_instance.users = []
        mock_role_instance.nome = 'admin'
        mock_role.query.get.return_value = mock_role_instance
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
            mock_audit.query.filter_by.return_value.count.return_value = 0
            
            result = verificar_integridade_referencial_role(1)
            
            assert result['can_delete'] is False
            assert result['erro'] == 'Papel crítico do sistema'
            assert result['is_critical'] is True


class TestIntegridadeReferencialPermission:
    """Testes para verificação de integridade referencial de permissões."""
    
    @patch('backend.app.api.rbac.Permission')
    def test_verificar_integridade_permission_sem_dependencias(self, mock_permission):
        """Testa verificação quando permissão não tem dependências."""
        # Mock da permissão
        mock_permission_instance = Mock()
        mock_permission_instance.roles = []
        mock_permission_instance.nome = 'custom_permission'
        mock_permission.query.get.return_value = mock_permission_instance
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
            mock_audit.query.filter_by.return_value.count.return_value = 0
            
            result = verificar_integridade_referencial_permission(1)
            
            assert result['can_delete'] is True
            assert result['erro'] is None
            assert result['roles'] == 0
            assert result['is_critical'] is False
    
    @patch('backend.app.api.rbac.Permission')
    def test_verificar_integridade_permission_com_roles(self, mock_permission):
        """Testa verificação quando permissão tem papéis associados."""
        # Mock da permissão
        mock_permission_instance = Mock()
        mock_permission_instance.roles = [Mock(nome='admin'), Mock(nome='gestor')]
        mock_permission_instance.nome = 'custom_permission'
        mock_permission.query.get.return_value = mock_permission_instance
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
            mock_audit.query.filter_by.return_value.count.return_value = 0
            
            result = verificar_integridade_referencial_permission(1)
            
            assert result['can_delete'] is False
            assert result['erro'] == 'Permissão possui papéis associados'
            assert result['roles'] == 2
    
    @patch('backend.app.api.rbac.Permission')
    def test_verificar_integridade_permission_critica(self, mock_permission):
        """Testa verificação quando permissão é crítica do sistema."""
        # Mock da permissão
        mock_permission_instance = Mock()
        mock_permission_instance.roles = []
        mock_permission_instance.nome = 'read'
        mock_permission.query.get.return_value = mock_permission_instance
        
        # Mock das importações que podem falhar
        with patch('backend.app.api.rbac.AuditLog', create=True) as mock_audit:
            mock_audit.query.filter_by.return_value.count.return_value = 0
            
            result = verificar_integridade_referencial_permission(1)
            
            assert result['can_delete'] is False
            assert result['erro'] == 'Permissão crítica do sistema'
            assert result['is_critical'] is True


class TestIntegridadeReferencialErrorHandling:
    """Testes para tratamento de erros nas verificações de integridade."""
    
    @patch('backend.app.api.rbac.User')
    def test_verificar_integridade_user_erro_import(self, mock_user):
        """Testa tratamento de erro quando importações falham."""
        # Mock do usuário
        mock_user_instance = Mock()
        mock_user_instance.roles = [Mock(nome='usuario')]
        mock_user.query.get.return_value = mock_user_instance
        
        # Mock da query de admin
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.count.return_value = 2
        mock_user.query = mock_query
        
        # Simular erro de importação
        with patch('backend.app.api.rbac.Execucao', side_effect=ImportError):
            with patch('backend.app.api.rbac.AuditLog', side_effect=ImportError):
                result = verificar_integridade_referencial_user(1)
                
                assert result['can_delete'] is True
                assert result['erro'] is None
    
    @patch('backend.app.api.rbac.Role')
    def test_verificar_integridade_role_nao_encontrado(self, mock_role):
        """Testa verificação quando papel não é encontrado."""
        mock_role.query.get.return_value = None
        
        result = verificar_integridade_referencial_role(999)
        
        assert result['can_delete'] is False
        assert result['erro'] == 'Papel não encontrado'
    
    @patch('backend.app.api.rbac.Permission')
    def test_verificar_integridade_permission_nao_encontrada(self, mock_permission):
        """Testa verificação quando permissão não é encontrada."""
        mock_permission.query.get.return_value = None
        
        result = verificar_integridade_referencial_permission(999)
        
        assert result['can_delete'] is False
        assert result['erro'] == 'Permissão não encontrada'


if __name__ == '__main__':
    pytest.main([__file__]) 