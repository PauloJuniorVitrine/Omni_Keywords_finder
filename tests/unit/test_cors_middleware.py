import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.cors import CORSMiddleware, CORSConfig

@pytest.fixture
def middleware():
    return CORSMiddleware()

@pytest.fixture
def request_data():
    return {'origin': 'https://example.com', 'method': 'GET'}

# 1. Teste de configuração de CORS
def test_cors_configuration():
    config = CORSConfig(allowed_origins=['https://example.com'])
    mw = CORSMiddleware(config)
    assert 'https://example.com' in mw.config.allowed_origins

# 2. Teste de headers CORS
def test_cors_headers(middleware, request_data):
    headers = middleware.add_cors_headers(request_data)
    assert 'Access-Control-Allow-Origin' in headers
    assert 'Access-Control-Allow-Methods' in headers

# 3. Teste de preflight requests
def test_preflight_requests(middleware, request_data):
    request_data['method'] = 'OPTIONS'
    response = middleware.handle_preflight(request_data)
    assert response.status_code == 200
    assert 'Access-Control-Allow-Headers' in response.headers

# 4. Teste de casos edge (origem não permitida)
def test_edge_case_disallowed_origin(middleware):
    request_data = {'origin': 'https://malicious.com'}
    headers = middleware.add_cors_headers(request_data)
    assert headers.get('Access-Control-Allow-Origin') != 'https://malicious.com'

# 5. Teste de performance
def test_cors_performance(middleware, request_data, benchmark):
    benchmark(middleware.add_cors_headers, request_data)

# 6. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware, request_data):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process(request_data) == 'ok'
    next_middleware.assert_called_once()

# 7. Teste de configuração dinâmica
def test_dynamic_configuration():
    mw = CORSMiddleware()
    mw.add_allowed_origin('https://newdomain.com')
    assert 'https://newdomain.com' in mw.config.allowed_origins

# 8. Teste de logs de CORS
def test_logging_on_cors_request(middleware, request_data, caplog):
    with caplog.at_level('INFO'):
        middleware.add_cors_headers(request_data)
    assert any('CORS headers added' in m for m in caplog.messages)

# 9. Teste de métricas de CORS
def test_metrics_collected_on_cors(middleware, request_data):
    with patch.object(middleware, 'metrics') as mock_metrics:
        middleware.add_cors_headers(request_data)
        mock_metrics.increment.assert_called_with('cors.requests')

# 10. Teste de segurança
def test_security_headers_present(middleware, request_data):
    headers = middleware.add_cors_headers(request_data)
    assert 'X-Content-Type-Options' in headers
    assert 'X-Frame-Options' in headers 