import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.auth import AuthMiddleware, TokenValidator, PermissionChecker

@pytest.fixture
def middleware():
    return AuthMiddleware()

@pytest.fixture
def request_data():
    return {'token': 'valid_token_123', 'user_id': 'user123', 'permissions': ['read', 'write']}

# 1. Teste de validação de tokens
def test_token_validation(middleware, request_data):
    validator = TokenValidator()
    is_valid = validator.validate(request_data['token'])
    assert is_valid is True

# 2. Teste de verificação de permissões
def test_permission_checking(middleware, request_data):
    checker = PermissionChecker()
    has_permission = checker.check_permission(request_data['user_id'], 'read')
    assert has_permission is True

# 3. Teste de refresh de tokens
def test_token_refresh(middleware, request_data):
    new_token = middleware.refresh_token(request_data['token'])
    assert new_token is not None
    assert new_token != request_data['token']

# 4. Teste de casos edge (token inválido)
def test_edge_case_invalid_token(middleware):
    request_data = {'token': 'invalid_token', 'user_id': 'user123'}
    with pytest.raises(Exception):
        middleware.validate_token(request_data['token'])

# 5. Teste de performance
def test_auth_performance(middleware, request_data, benchmark):
    benchmark(middleware.validate_token, request_data['token'])

# 6. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware, request_data):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process(request_data) == 'ok'
    next_middleware.assert_called_once()

# 7. Teste de configuração dinâmica
def test_dynamic_configuration():
    mw = AuthMiddleware(token_expiry=3600)
    assert mw.token_expiry == 3600
    mw.set_token_expiry(7200)
    assert mw.token_expiry == 7200

# 8. Teste de logs de autenticação
def test_logging_on_auth(middleware, request_data, caplog):
    with caplog.at_level('INFO'):
        middleware.validate_token(request_data['token'])
    assert any('Token validated' in m for m in caplog.messages)

# 9. Teste de métricas de autenticação
def test_metrics_collected_on_auth(middleware, request_data):
    with patch.object(middleware, 'metrics') as mock_metrics:
        middleware.validate_token(request_data['token'])
        mock_metrics.increment.assert_called_with('auth.tokens_validated')

# 10. Teste de segurança
def test_security_token_validation(middleware):
    # Teste com token malicioso
    malicious_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.evil_payload'
    with pytest.raises(Exception):
        middleware.validate_token(malicious_token) 