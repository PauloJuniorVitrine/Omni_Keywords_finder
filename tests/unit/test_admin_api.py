import pytest
from unittest.mock import MagicMock, patch
from myapp.api.admin import AdminAPI, UserManager, SystemConfig

@pytest.fixture
def admin_api():
    return AdminAPI()

@pytest.fixture
def user_data():
    return {'username': 'admin_user', 'email': 'admin@example.com', 'role': 'admin'}

# 1. Teste de gerenciamento de usuários
def test_user_management(admin_api, user_data):
    user_manager = UserManager()
    
    # Criar usuário
    user = user_manager.create_user(user_data)
    assert user['username'] == 'admin_user'
    assert user['role'] == 'admin'
    
    # Listar usuários
    users = user_manager.list_users()
    assert len(users) > 0
    assert any(u['username'] == 'admin_user' for u in users)
    
    # Atualizar usuário
    updated_user = user_manager.update_user(user['id'], {'role': 'super_admin'})
    assert updated_user['role'] == 'super_admin'
    
    # Deletar usuário
    result = user_manager.delete_user(user['id'])
    assert result is True

# 2. Teste de configuração do sistema
def test_system_configuration(admin_api):
    config = SystemConfig()
    
    # Obter configuração atual
    current_config = config.get_config()
    assert 'database' in current_config
    assert 'security' in current_config
    
    # Atualizar configuração
    new_config = {'max_connections': 100, 'timeout': 30}
    updated_config = config.update_config(new_config)
    assert updated_config['max_connections'] == 100
    assert updated_config['timeout'] == 30

# 3. Teste de monitoramento
def test_system_monitoring(admin_api):
    # Obter métricas do sistema
    metrics = admin_api.get_system_metrics()
    assert 'cpu_usage' in metrics
    assert 'memory_usage' in metrics
    assert 'disk_usage' in metrics
    
    # Obter status dos serviços
    services_status = admin_api.get_services_status()
    assert 'database' in services_status
    assert 'api' in services_status
    assert all(status in ['healthy', 'warning', 'critical'] for status in services_status.values())

# 4. Teste de relatórios
def test_report_generation(admin_api):
    # Gerar relatório de usuários
    user_report = admin_api.generate_user_report()
    assert 'total_users' in user_report
    assert 'active_users' in user_report
    assert 'new_users_this_month' in user_report
    
    # Gerar relatório de sistema
    system_report = admin_api.generate_system_report()
    assert 'uptime' in system_report
    assert 'performance_metrics' in system_report
    assert 'error_logs' in system_report

# 5. Teste de auditoria
def test_audit_logging(admin_api, user_data):
    # Registrar ação administrativa
    audit_log = admin_api.log_admin_action(
        user_id='admin123',
        action='user_created',
        details=user_data
    )
    assert audit_log['action'] == 'user_created'
    assert audit_log['timestamp'] is not None
    
    # Buscar logs de auditoria
    audit_logs = admin_api.get_audit_logs(filters={'action': 'user_created'})
    assert len(audit_logs) > 0
    assert all(log['action'] == 'user_created' for log in audit_logs)

# 6. Teste de casos edge (usuário duplicado)
def test_edge_case_duplicate_user(admin_api, user_data):
    user_manager = UserManager()
    
    # Criar primeiro usuário
    user1 = user_manager.create_user(user_data)
    
    # Tentar criar usuário duplicado
    with pytest.raises(Exception):
        user_manager.create_user(user_data)

# 7. Teste de performance
def test_admin_api_performance(admin_api, user_data, benchmark):
    def create_user_operation():
        user_manager = UserManager()
        return user_manager.create_user(user_data)
    
    benchmark(create_user_operation)

# 8. Teste de integração
def test_integration_with_other_apis(admin_api):
    # Integração com API de autenticação
    with patch('myapp.api.auth.AuthAPI') as mock_auth:
        mock_auth.return_value.validate_admin_token.return_value = True
        result = admin_api.validate_admin_access('admin_token')
        assert result is True

# 9. Teste de segurança
def test_security_checks(admin_api):
    # Verificar permissões de administrador
    has_permission = admin_api.check_admin_permissions('user123', 'delete_user')
    assert has_permission in [True, False]
    
    # Validar token de administrador
    with pytest.raises(Exception):
        admin_api.validate_admin_access('invalid_token')

# 10. Teste de logs
def test_logging_functionality(admin_api, user_data, caplog):
    with caplog.at_level('INFO'):
        admin_api.create_user(user_data)
    
    assert any('User created' in m for m in caplog.messages)
    assert any('admin_user' in m for m in caplog.messages) 