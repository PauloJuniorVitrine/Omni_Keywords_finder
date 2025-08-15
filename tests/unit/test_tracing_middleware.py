import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.tracing import TracingMiddleware, TraceContext

@pytest.fixture
def middleware():
    return TracingMiddleware()

@pytest.fixture
def request_data():
    return {'trace_id': '123', 'span_id': '456', 'method': 'GET'}

# 1. Teste de geração de traces
def test_trace_generation(middleware, request_data):
    trace = middleware.generate_trace(request_data)
    assert trace.trace_id is not None
    assert trace.span_id is not None
    assert trace.start_time is not None

# 2. Teste de propagação de context
def test_context_propagation(middleware, request_data):
    context = TraceContext(trace_id='123', span_id='456')
    propagated = middleware.propagate_context(context, request_data)
    assert propagated['trace_id'] == '123'
    assert propagated['span_id'] == '456'

# 3. Teste de sampling
def test_trace_sampling(middleware, request_data):
    middleware.set_sampling_rate(0.5)
    traces = []
    for _ in range(100):
        if middleware.should_sample(request_data):
            traces.append(middleware.generate_trace(request_data))
    assert 40 <= len(traces) <= 60  # ~50% sampling rate

# 4. Teste de exportação
def test_trace_export(middleware, request_data):
    trace = middleware.generate_trace(request_data)
    with patch.object(middleware, 'exporter') as mock_exporter:
        middleware.export_trace(trace)
        mock_exporter.export.assert_called_once_with(trace)

# 5. Teste de casos edge (context vazio)
def test_edge_case_empty_context(middleware):
    request_data = {}
    trace = middleware.generate_trace(request_data)
    assert trace.trace_id is not None
    assert trace.span_id is not None

# 6. Teste de performance
def test_tracing_performance(middleware, request_data, benchmark):
    benchmark(middleware.generate_trace, request_data)

# 7. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware, request_data):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process(request_data) == 'ok'
    next_middleware.assert_called_once()

# 8. Teste de configuração dinâmica
def test_dynamic_configuration():
    mw = TracingMiddleware(sampling_rate=0.1)
    assert mw.sampling_rate == 0.1
    mw.set_sampling_rate(0.8)
    assert mw.sampling_rate == 0.8

# 9. Teste de logs de tracing
def test_logging_on_trace(middleware, request_data, caplog):
    with caplog.at_level('DEBUG'):
        middleware.generate_trace(request_data)
    assert any('Trace generated' in m for m in caplog.messages)

# 10. Teste de métricas de tracing
def test_metrics_collected_on_trace(middleware, request_data):
    with patch.object(middleware, 'metrics') as mock_metrics:
        middleware.generate_trace(request_data)
        mock_metrics.increment.assert_called_with('tracing.traces_generated') 