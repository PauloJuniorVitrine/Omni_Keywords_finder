import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.security_headers import SecurityHeadersMiddleware, SecurityConfig

@pytest.fixture
def middleware():
    return SecurityHeadersMiddleware()

@pytest.fixture
def request_data():
    return {'headers': {}, 'method': 'GET'}

# 1. Teste de headers de segurança
def test_security_headers_present(middleware, request_data):
    headers = middleware.add_security_headers(request_data)
    assert 'X-Content-Type-Options' in headers
    assert 'X-Frame-Options' in headers
    assert 'X-XSS-Protection' in headers

# 2. Teste de configuração
def test_security_configuration():
    config = SecurityConfig(csp_enabled=True, hsts_enabled=True)
    mw = SecurityHeadersMiddleware(config)
    assert mw.config.csp_enabled is True
    assert mw.config.hsts_enabled is True

# 3. Teste de casos edge (headers vazios)
def test_edge_case_empty_headers(middleware):
    request_data = {'headers': None, 'method': 'GET'}
    headers = middleware.add_security_headers(request_data)
    assert headers is not None
    assert 'X-Content-Type-Options' in headers

# 4. Teste de performance
def test_security_headers_performance(middleware, request_data, benchmark):
    benchmark(middleware.add_security_headers, request_data)

# 5. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware, request_data):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process(request_data) == 'ok'
    next_middleware.assert_called_once()

# 6. Teste de logs de segurança
def test_logging_on_security_headers(middleware, request_data, caplog):
    with caplog.at_level('INFO'):
        middleware.add_security_headers(request_data)
    assert any('Security headers added' in m for m in caplog.messages)

# 7. Teste de métricas de segurança
def test_metrics_collected_on_security(middleware, request_data):
    with patch.object(middleware, 'metrics') as mock_metrics:
        middleware.add_security_headers(request_data)
        mock_metrics.increment.assert_called_with('security.headers_added')

# 8. Teste de compliance
def test_compliance_headers_present(middleware, request_data):
    headers = middleware.add_security_headers(request_data)
    assert 'Strict-Transport-Security' in headers
    assert 'Content-Security-Policy' in headers

# 9. Teste de relatórios de segurança
def test_security_report_generation(middleware):
    middleware.metrics = MagicMock()
    middleware.metrics.get_stats.return_value = {'headers_added': 100, 'violations': 0}
    report = middleware.generate_security_report()
    assert 'headers_added' in report
    assert 'violations' in report

# 10. Teste de auditoria de segurança
def test_security_audit_logging(middleware, request_data, caplog):
    with caplog.at_level('AUDIT'):
        middleware.add_security_headers(request_data)
    assert any('Security audit' in m for m in caplog.messages) 