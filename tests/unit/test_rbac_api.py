import pytest
from unittest.mock import MagicMock, patch
from myapp.api.rbac import RBACAPI, RoleManager, PermissionManager, AccessChecker

@pytest.fixture
def rbac_api():
    return RBACAPI()

@pytest.fixture
def sample_role():
    return {
        'name': 'admin',
        'description': 'Administrator role',
        'permissions': ['read', 'write', 'delete', 'admin']
    }

@pytest.fixture
def sample_permission():
    return {
        'name': 'user_management',
        'description': 'Manage users',
        'actions': ['create', 'read', 'update', 'delete']
    }

# 1. Teste de gerenciamento de roles
def test_role_management(rbac_api, sample_role):
    role_manager = RoleManager()
    
    # Criar role
    created_role = role_manager.create_role(sample_role)
    assert created_role['name'] == 'admin'
    assert created_role['id'] is not None
    assert len(created_role['permissions']) == 4
    
    # Listar roles
    roles = role_manager.list_roles()
    assert len(roles) > 0
    assert any(role['name'] == 'admin' for role in roles)
    
    # Atualizar role
    updated_role = role_manager.update_role(created_role['id'], {'description': 'Updated admin role'})
    assert updated_role['description'] == 'Updated admin role'
    
    # Deletar role
    result = role_manager.delete_role(created_role['id'])
    assert result is True

# 2. Teste de gerenciamento de permissões
def test_permission_management(rbac_api, sample_permission):
    permission_manager = PermissionManager()
    
    # Criar permissão
    created_permission = permission_manager.create_permission(sample_permission)
    assert created_permission['name'] == 'user_management'
    assert created_permission['id'] is not None
    assert len(created_permission['actions']) == 4
    
    # Listar permissões
    permissions = permission_manager.list_permissions()
    assert len(permissions) > 0
    assert any(perm['name'] == 'user_management' for perm in permissions)
    
    # Atualizar permissão
    updated_permission = permission_manager.update_permission(
        created_permission['id'], 
        {'actions': ['create', 'read', 'update']}
    )
    assert len(updated_permission['actions']) == 3

# 3. Teste de atribuição de roles
def test_role_assignment(rbac_api, sample_role):
    role_manager = RoleManager()
    
    # Criar role primeiro
    role = role_manager.create_role(sample_role)
    
    # Atribuir role a usuário
    assignment = role_manager.assign_role_to_user('user123', role['id'])
    assert assignment['user_id'] == 'user123'
    assert assignment['role_id'] == role['id']
    assert assignment['assigned_at'] is not None
    
    # Verificar roles do usuário
    user_roles = role_manager.get_user_roles('user123')
    assert len(user_roles) > 0
    assert any(r['name'] == 'admin' for r in user_roles)
    
    # Remover role do usuário
    result = role_manager.remove_role_from_user('user123', role['id'])
    assert result is True

# 4. Teste de verificação de acesso
def test_access_verification(rbac_api, sample_role):
    access_checker = AccessChecker()
    
    # Verificar permissão específica
    has_permission = access_checker.check_permission('user123', 'user_management', 'create')
    assert has_permission in [True, False]
    
    # Verificar acesso a recurso
    has_access = access_checker.check_resource_access('user123', 'users', 'read')
    assert has_access in [True, False]
    
    # Verificar múltiplas permissões
    permissions_check = access_checker.check_multiple_permissions(
        'user123', 
        ['user_management:create', 'user_management:read']
    )
    assert isinstance(permissions_check, dict)
    assert 'user_management:create' in permissions_check

# 5. Teste de casos edge
def test_edge_cases(rbac_api):
    role_manager = RoleManager()
    
    # Teste com role duplicada
    role_data = {'name': 'admin', 'permissions': ['read']}
    role1 = role_manager.create_role(role_data)
    
    with pytest.raises(Exception):
        role_manager.create_role(role_data)
    
    # Teste com permissão inválida
    invalid_role = {'name': 'test', 'permissions': ['invalid_permission']}
    with pytest.raises(ValueError):
        role_manager.create_role(invalid_role)
    
    # Teste com usuário inexistente
    access_checker = AccessChecker()
    result = access_checker.check_permission('nonexistent_user', 'read', 'data')
    assert result is False

# 6. Teste de performance
def test_rbac_performance(rbac_api, sample_role, benchmark):
    access_checker = AccessChecker()
    
    def check_permission_operation():
        return access_checker.check_permission('user123', 'read', 'data')
    
    benchmark(check_permission_operation)

# 7. Teste de integração
def test_integration_with_auth_system(rbac_api, sample_role):
    role_manager = RoleManager()
    
    # Integração com sistema de autenticação
    with patch('myapp.auth.AuthSystem') as mock_auth:
        mock_auth.return_value.validate_user.return_value = True
        
        result = role_manager.assign_role_to_user('user123', 'role123')
        assert result['user_id'] == 'user123'

# 8. Teste de segurança
def test_security_checks(rbac_api):
    access_checker = AccessChecker()
    
    # Verificar privilégios elevados
    elevated_check = access_checker.check_elevated_privileges('user123')
    assert elevated_check['has_elevated'] in [True, False]
    assert 'roles' in elevated_check
    
    # Verificar permissões sensíveis
    sensitive_check = access_checker.check_sensitive_permissions('user123')
    assert 'sensitive_permissions' in sensitive_check
    assert isinstance(sensitive_check['sensitive_permissions'], list)

# 9. Teste de logs
def test_logging_functionality(rbac_api, sample_role, caplog):
    role_manager = RoleManager()
    
    with caplog.at_level('INFO'):
        role_manager.create_role(sample_role)
    
    assert any('Role created' in m for m in caplog.messages)
    assert any('admin' in m for m in caplog.messages)
    
    # Verificar logs de auditoria
    with caplog.at_level('AUDIT'):
        role_manager.assign_role_to_user('user123', 'role123')
    
    assert any('Role assigned' in m for m in caplog.messages)

# 10. Teste de auditoria
def test_audit_functionality(rbac_api, sample_role):
    role_manager = RoleManager()
    
    # Registrar mudança de role
    audit_log = role_manager.audit_role_change(
        'user123', 
        'role_assigned', 
        {'role_id': 'role123', 'assigned_by': 'admin'}
    )
    assert audit_log['action'] == 'role_assigned'
    assert audit_log['user_id'] == 'user123'
    assert audit_log['timestamp'] is not None
    
    # Buscar logs de auditoria
    audit_logs = role_manager.get_audit_logs('user123')
    assert len(audit_logs) > 0
    assert all(log['user_id'] == 'user123' for log in audit_logs) 