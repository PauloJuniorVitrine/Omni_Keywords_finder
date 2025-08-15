import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.rate_limiter import RateLimiter, RateLimitExceeded

@pytest.fixture
def rate_limiter():
    return RateLimiter(requests_per_minute=60)

@pytest.fixture
def request_data():
    return {'ip': '192.168.1.1', 'user_id': 'user123', 'endpoint': '/api/test'}

# 1. Teste de limitação de taxa
def test_rate_limiting(rate_limiter, request_data):
    # Simular 60 requisições
    for i in range(60):
        rate_limiter.check_rate_limit(request_data)
    
    # A 61ª requisição deve ser bloqueada
    with pytest.raises(RateLimitExceeded):
        rate_limiter.check_rate_limit(request_data)

# 2. Teste de configuração
def test_rate_limiter_configuration():
    limiter = RateLimiter(requests_per_minute=30, window_size=60)
    assert limiter.requests_per_minute == 30
    assert limiter.window_size == 60

# 3. Teste de casos edge (taxa zero)
def test_edge_case_zero_rate(rate_limiter, request_data):
    rate_limiter.set_rate(0)
    with pytest.raises(RateLimitExceeded):
        rate_limiter.check_rate_limit(request_data)

# 4. Teste de performance
def test_rate_limiter_performance(rate_limiter, request_data, benchmark):
    benchmark(rate_limiter.check_rate_limit, request_data)

# 5. Teste de integração com sistema de requisições
def test_integration_with_request_system(rate_limiter, request_data):
    request_system = MagicMock(return_value='request_processed')
    rate_limiter.set_request_system(request_system)
    
    result = rate_limiter.process_with_rate_limit(request_data)
    assert result == 'request_processed'
    request_system.assert_called_once()

# 6. Teste de logs de rate limiting
def test_logging_on_rate_limit(rate_limiter, request_data, caplog):
    with caplog.at_level('WARNING'):
        for _ in range(60):
            rate_limiter.check_rate_limit(request_data)
        try:
            rate_limiter.check_rate_limit(request_data)
        except RateLimitExceeded:
            pass
    assert any('Rate limit exceeded' in m for m in caplog.messages)

# 7. Teste de métricas de rate limiting
def test_metrics_collected_on_rate_limit(rate_limiter, request_data):
    with patch.object(rate_limiter, 'metrics') as mock_metrics:
        for _ in range(60):
            rate_limiter.check_rate_limit(request_data)
        try:
            rate_limiter.check_rate_limit(request_data)
        except RateLimitExceeded:
            pass
        mock_metrics.increment.assert_called_with('rate_limiter.exceeded')

# 8. Teste de relatórios de rate limiting
def test_rate_limit_report_generation(rate_limiter):
    rate_limiter.metrics = MagicMock()
    rate_limiter.metrics.get_stats.return_value = {
        'requests_allowed': 58,
        'requests_blocked': 2,
        'peak_usage': 60
    }
    report = rate_limiter.generate_rate_limit_report()
    assert 'requests_allowed' in report
    assert 'requests_blocked' in report
    assert 'peak_usage' in report

# 9. Teste de auditoria de rate limiting
def test_audit_logging_on_rate_limit(rate_limiter, request_data, caplog):
    with caplog.at_level('AUDIT'):
        rate_limiter.check_rate_limit(request_data)
    assert any('Rate limit audit' in m for m in caplog.messages)

# 10. Teste de compliance de rate limiting
def test_compliance_checks(rate_limiter, request_data):
    compliance_report = rate_limiter.check_compliance()
    assert 'rate_limiting_enabled' in compliance_report
    assert 'limits_configured' in compliance_report
    assert 'monitoring_active' in compliance_report
    assert compliance_report['rate_limiting_enabled'] is True 