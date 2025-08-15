import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.rate_limiting import RateLimitingMiddleware, RateLimitExceeded

@pytest.fixture
def middleware():
    return RateLimitingMiddleware(requests_per_minute=10)

@pytest.fixture
def request_data():
    return {'ip': '192.168.1.1', 'user_id': 'user123', 'endpoint': '/api/test'}

# 1. Teste de limitação por IP
def test_rate_limit_by_ip(middleware, request_data):
    for _ in range(10):
        middleware.check_rate_limit(request_data)
    with pytest.raises(RateLimitExceeded):
        middleware.check_rate_limit(request_data)

# 2. Teste de limitação por usuário
def test_rate_limit_by_user(middleware, request_data):
    middleware.set_limit_by('user', 5)
    for _ in range(5):
        middleware.check_rate_limit(request_data)
    with pytest.raises(RateLimitExceeded):
        middleware.check_rate_limit(request_data)

# 3. Teste de limitação por endpoint
def test_rate_limit_by_endpoint(middleware, request_data):
    middleware.set_limit_by('endpoint', 3)
    for _ in range(3):
        middleware.check_rate_limit(request_data)
    with pytest.raises(RateLimitExceeded):
        middleware.check_rate_limit(request_data)

# 4. Teste de configuração de limites
def test_limit_configuration():
    mw = RateLimitingMiddleware(requests_per_minute=20)
    assert mw.limit == 20
    mw.set_limit(30)
    assert mw.limit == 30

# 5. Teste de casos edge (limite zero)
def test_edge_case_zero_limit(middleware, request_data):
    middleware.set_limit(0)
    with pytest.raises(RateLimitExceeded):
        middleware.check_rate_limit(request_data)

# 6. Teste de performance
def test_rate_limiting_performance(middleware, request_data, benchmark):
    benchmark(middleware.check_rate_limit, request_data)

# 7. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware, request_data):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process(request_data) == 'ok'
    next_middleware.assert_called_once()

# 8. Teste de configuração dinâmica
def test_dynamic_configuration():
    mw = RateLimitingMiddleware()
    mw.set_window_size(60)
    assert mw.window_size == 60
    mw.set_cleanup_interval(300)
    assert mw.cleanup_interval == 300

# 9. Teste de logs de rate limiting
def test_logging_on_rate_limit(middleware, request_data, caplog):
    with caplog.at_level('WARNING'):
        for _ in range(10):
            middleware.check_rate_limit(request_data)
        try:
            middleware.check_rate_limit(request_data)
        except RateLimitExceeded:
            pass
    assert any('Rate limit exceeded' in m for m in caplog.messages)

# 10. Teste de métricas de rate limiting
def test_metrics_collected_on_rate_limit(middleware, request_data):
    with patch.object(middleware, 'metrics') as mock_metrics:
        for _ in range(10):
            middleware.check_rate_limit(request_data)
        try:
            middleware.check_rate_limit(request_data)
        except RateLimitExceeded:
            pass
        mock_metrics.increment.assert_called_with('rate_limit.exceeded') 