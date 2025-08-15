import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.resilience import ResilienceMiddleware, CircuitBreaker, RetryLogic

@pytest.fixture
def middleware():
    return ResilienceMiddleware()

@pytest.fixture
def request_data():
    return {'service': 'api', 'timeout': 5000, 'retries': 3}

# 1. Teste de circuit breaker
def test_circuit_breaker(middleware, request_data):
    breaker = CircuitBreaker(failure_threshold=3)
    # Simular falhas
    for _ in range(3):
        breaker.record_failure()
    assert breaker.is_open() is True
    # Teste de fallback
    result = middleware.execute_with_fallback(request_data)
    assert result is not None

# 2. Teste de retry logic
def test_retry_logic(middleware, request_data):
    retry = RetryLogic(max_retries=3)
    attempts = 0
    def failing_operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception("Temporary failure")
        return "success"
    
    result = retry.execute(failing_operation)
    assert result == "success"
    assert attempts == 3

# 3. Teste de timeout
def test_timeout_handling(middleware, request_data):
    def slow_operation():
        import time
        time.sleep(0.1)  # Simular operação lenta
        return "slow_result"
    
    with pytest.raises(Exception):  # Timeout exception
        middleware.execute_with_timeout(slow_operation, timeout=0.05)

# 4. Teste de bulkhead
def test_bulkhead_isolation(middleware, request_data):
    bulkhead = middleware.create_bulkhead(max_concurrent=2)
    # Simular múltiplas requisições
    results = []
    for i in range(5):
        try:
            result = bulkhead.execute(lambda: f"request_{i}")
            results.append(result)
        except Exception:
            results.append("rejected")
    
    assert len([r for r in results if r != "rejected"]) <= 2

# 5. Teste de casos edge (falha total)
def test_edge_case_total_failure(middleware, request_data):
    def always_failing_operation():
        raise Exception("Permanent failure")
    
    with pytest.raises(Exception):
        middleware.execute_with_retry(always_failing_operation, max_retries=3)

# 6. Teste de performance
def test_resilience_performance(middleware, request_data, benchmark):
    def fast_operation():
        return "fast_result"
    
    benchmark(middleware.execute_with_timeout, fast_operation, timeout=1000)

# 7. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware, request_data):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process(request_data) == 'ok'
    next_middleware.assert_called_once()

# 8. Teste de configuração dinâmica
def test_dynamic_configuration():
    mw = ResilienceMiddleware(timeout=1000, max_retries=5)
    assert mw.timeout == 1000
    assert mw.max_retries == 5
    mw.set_timeout(2000)
    assert mw.timeout == 2000

# 9. Teste de logs de resiliência
def test_logging_on_resilience(middleware, request_data, caplog):
    with caplog.at_level('WARNING'):
        try:
            middleware.execute_with_retry(lambda: 1/0, max_retries=1)
        except Exception:
            pass
    assert any('Retry attempt' in m for m in caplog.messages)

# 10. Teste de métricas de resiliência
def test_metrics_collected_on_resilience(middleware, request_data):
    with patch.object(middleware, 'metrics') as mock_metrics:
        try:
            middleware.execute_with_retry(lambda: 1/0, max_retries=1)
        except Exception:
            pass
        mock_metrics.increment.assert_called_with('resilience.retries_exceeded') 