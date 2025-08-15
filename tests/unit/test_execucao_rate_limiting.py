import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.execucao_rate_limiting import ExecucaoRateLimiting, RateLimitExceeded

@pytest.fixture
def rate_limiter():
    return ExecucaoRateLimiting(max_executions_per_hour=100)

@pytest.fixture
def execucao_data():
    return {'user_id': 'user123', 'execucao_type': 'keyword_search', 'timestamp': '2025-01-27T10:00:00Z'}

# 1. Teste de limitação de execuções
def test_execution_rate_limiting(rate_limiter, execucao_data):
    # Simular 100 execuções
    for i in range(100):
        rate_limiter.check_execution_limit(execucao_data)
    
    # A 101ª execução deve ser bloqueada
    with pytest.raises(RateLimitExceeded):
        rate_limiter.check_execution_limit(execucao_data)

# 2. Teste de configuração
def test_rate_limit_configuration():
    limiter = ExecucaoRateLimiting(max_executions_per_hour=50, window_size=3600)
    assert limiter.max_executions == 50
    assert limiter.window_size == 3600

# 3. Teste de casos edge (limite zero)
def test_edge_case_zero_limit(rate_limiter, execucao_data):
    rate_limiter.set_limit(0)
    with pytest.raises(RateLimitExceeded):
        rate_limiter.check_execution_limit(execucao_data)

# 4. Teste de performance
def test_rate_limiting_performance(rate_limiter, execucao_data, benchmark):
    benchmark(rate_limiter.check_execution_limit, execucao_data)

# 5. Teste de integração com sistema de execuções
def test_integration_with_execution_system(rate_limiter, execucao_data):
    execution_system = MagicMock(return_value='execution_completed')
    rate_limiter.set_execution_system(execution_system)
    
    result = rate_limiter.execute_with_rate_limit(execucao_data)
    assert result == 'execution_completed'
    execution_system.assert_called_once()

# 6. Teste de logs de rate limiting
def test_logging_on_rate_limit(rate_limiter, execucao_data, caplog):
    with caplog.at_level('WARNING'):
        for _ in range(100):
            rate_limiter.check_execution_limit(execucao_data)
        try:
            rate_limiter.check_execution_limit(execucao_data)
        except RateLimitExceeded:
            pass
    assert any('Execution rate limit exceeded' in m for m in caplog.messages)

# 7. Teste de métricas de rate limiting
def test_metrics_collected_on_rate_limit(rate_limiter, execucao_data):
    with patch.object(rate_limiter, 'metrics') as mock_metrics:
        for _ in range(100):
            rate_limiter.check_execution_limit(execucao_data)
        try:
            rate_limiter.check_execution_limit(execucao_data)
        except RateLimitExceeded:
            pass
        mock_metrics.increment.assert_called_with('execution.rate_limit_exceeded')

# 8. Teste de relatórios de rate limiting
def test_rate_limit_report_generation(rate_limiter):
    rate_limiter.metrics = MagicMock()
    rate_limiter.metrics.get_stats.return_value = {
        'executions_allowed': 95,
        'executions_blocked': 5,
        'peak_usage': 100
    }
    report = rate_limiter.generate_rate_limit_report()
    assert 'executions_allowed' in report
    assert 'executions_blocked' in report
    assert 'peak_usage' in report

# 9. Teste de auditoria de rate limiting
def test_audit_logging_on_rate_limit(rate_limiter, execucao_data, caplog):
    with caplog.at_level('AUDIT'):
        rate_limiter.check_execution_limit(execucao_data)
    assert any('Execution rate limit audit' in m for m in caplog.messages)

# 10. Teste de compliance de rate limiting
def test_compliance_checks(rate_limiter, execucao_data):
    compliance_report = rate_limiter.check_compliance()
    assert 'rate_limiting_enabled' in compliance_report
    assert 'limits_configured' in compliance_report
    assert compliance_report['rate_limiting_enabled'] is True 