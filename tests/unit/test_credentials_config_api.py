import pytest
from unittest.mock import MagicMock, patch
from myapp.api.credentials_config import CredentialsConfigAPI, ProviderManager, CredentialValidator, RotationManager

@pytest.fixture
def credentials_api():
    return CredentialsConfigAPI()

@pytest.fixture
def sample_provider():
    return {
        'name': 'google_analytics',
        'type': 'analytics',
        'credentials': {
            'client_id': 'client123',
            'client_secret': 'secret456',
            'refresh_token': 'refresh789'
        },
        'config': {
            'scopes': ['read', 'write'],
            'redirect_uri': 'https://app.example.com/callback'
        }
    }

# 1. Teste de configuração de providers
def test_provider_configuration(credentials_api, sample_provider):
    provider_manager = ProviderManager()
    
    # Configurar provider
    configured_provider = provider_manager.configure_provider(sample_provider)
    assert configured_provider['name'] == 'google_analytics'
    assert configured_provider['id'] is not None
    assert configured_provider['status'] == 'active'
    assert 'credentials' in configured_provider
    
    # Listar providers
    providers = provider_manager.list_providers()
    assert len(providers) > 0
    assert any(p['name'] == 'google_analytics' for p in providers)
    
    # Atualizar configuração
    updated_config = provider_manager.update_provider_config(
        configured_provider['id'], 
        {'scopes': ['read', 'write', 'admin']}
    )
    assert 'admin' in updated_config['config']['scopes']

# 2. Teste de validação de credenciais
def test_credential_validation(credentials_api, sample_provider):
    validator = CredentialValidator()
    
    # Validar credenciais
    validation_result = validator.validate_credentials(sample_provider['credentials'])
    assert validation_result['valid'] is True
    assert validation_result['expires_at'] is not None
    assert 'scopes' in validation_result
    
    # Testar credenciais inválidas
    invalid_credentials = {
        'client_id': 'invalid',
        'client_secret': 'invalid',
        'refresh_token': 'invalid'
    }
    invalid_validation = validator.validate_credentials(invalid_credentials)
    assert invalid_validation['valid'] is False
    assert 'error' in invalid_validation

# 3. Teste de rotação de credenciais
def test_credential_rotation(credentials_api, sample_provider):
    rotation_manager = RotationManager()
    provider_manager = ProviderManager()
    
    # Configurar provider primeiro
    provider = provider_manager.configure_provider(sample_provider)
    
    # Rotacionar credenciais
    rotation_result = rotation_manager.rotate_credentials(provider['id'])
    assert rotation_result['rotated'] is True
    assert rotation_result['new_credentials'] is not None
    assert rotation_result['rotation_date'] is not None
    
    # Verificar histórico de rotação
    rotation_history = rotation_manager.get_rotation_history(provider['id'])
    assert len(rotation_history) > 0
    assert all('rotation_date' in entry for entry in rotation_history)

# 4. Teste de casos edge
def test_edge_cases(credentials_api):
    provider_manager = ProviderManager()
    
    # Teste com provider vazio
    empty_provider = {}
    with pytest.raises(ValueError):
        provider_manager.configure_provider(empty_provider)
    
    # Teste com credenciais ausentes
    no_credentials_provider = {
        'name': 'test_provider',
        'type': 'test',
        'config': {}
    }
    with pytest.raises(ValueError):
        provider_manager.configure_provider(no_credentials_provider)
    
    # Teste com provider duplicado
    duplicate_provider = {
        'name': 'google_analytics',
        'type': 'analytics',
        'credentials': {'test': 'value'}
    }
    provider_manager.configure_provider(duplicate_provider)
    with pytest.raises(Exception):
        provider_manager.configure_provider(duplicate_provider)

# 5. Teste de performance
def test_credentials_performance(credentials_api, sample_provider, benchmark):
    provider_manager = ProviderManager()
    
    def configure_provider_operation():
        return provider_manager.configure_provider(sample_provider)
    
    benchmark(configure_provider_operation)

# 6. Teste de integração
def test_integration_with_external_services(credentials_api, sample_provider):
    provider_manager = ProviderManager()
    
    # Integração com serviço de autenticação
    with patch('myapp.auth.AuthService') as mock_auth:
        mock_auth.return_value.validate_oauth_credentials.return_value = {'valid': True}
        
        result = provider_manager.validate_with_external_service(sample_provider)
        assert result['valid'] is True

# 7. Teste de segurança
def test_security_checks(credentials_api, sample_provider):
    validator = CredentialValidator()
    
    # Verificar criptografia de credenciais
    encrypted_credentials = validator.encrypt_credentials(sample_provider['credentials'])
    assert 'encrypted' in encrypted_credentials
    assert 'client_secret' not in encrypted_credentials
    assert 'refresh_token' not in encrypted_credentials
    
    # Verificar força das credenciais
    strength_check = validator.check_credential_strength(sample_provider['credentials'])
    assert 'strength_score' in strength_check
    assert 'recommendations' in strength_check
    
    # Verificar expiração
    expiration_check = validator.check_credential_expiration(sample_provider['credentials'])
    assert 'expires_in_days' in expiration_check
    assert 'needs_rotation' in expiration_check

# 8. Teste de logs
def test_logging_functionality(credentials_api, sample_provider, caplog):
    provider_manager = ProviderManager()
    
    with caplog.at_level('INFO'):
        provider_manager.configure_provider(sample_provider)
    
    assert any('Provider configured' in m for m in caplog.messages)
    assert any('google_analytics' in m for m in caplog.messages)
    
    # Verificar logs de segurança
    with caplog.at_level('SECURITY'):
        validator = CredentialValidator()
        validator.validate_credentials(sample_provider['credentials'])
    
    assert any('Credentials validated' in m for m in caplog.messages)

# 9. Teste de auditoria
def test_audit_functionality(credentials_api, sample_provider):
    provider_manager = ProviderManager()
    
    # Registrar mudança de configuração
    audit_log = provider_manager.audit_configuration_change(
        'user123',
        'provider_configured',
        {'provider_name': 'google_analytics', 'action': 'created'}
    )
    assert audit_log['action'] == 'provider_configured'
    assert audit_log['user_id'] == 'user123'
    assert audit_log['timestamp'] is not None
    
    # Buscar logs de auditoria
    audit_logs = provider_manager.get_audit_logs('google_analytics')
    assert len(audit_logs) > 0
    assert all(log['provider_name'] == 'google_analytics' for log in audit_logs)

# 10. Teste de compliance
def test_compliance_checks(credentials_api, sample_provider):
    validator = CredentialValidator()
    
    # Verificar compliance GDPR
    gdpr_compliance = validator.check_gdpr_compliance(sample_provider)
    assert gdpr_compliance['compliant'] in [True, False]
    assert 'data_retention' in gdpr_compliance
    assert 'access_controls' in gdpr_compliance
    
    # Verificar compliance SOC2
    soc2_compliance = validator.check_soc2_compliance(sample_provider)
    assert soc2_compliance['compliant'] in [True, False]
    assert 'access_management' in soc2_compliance
    assert 'encryption' in soc2_compliance 