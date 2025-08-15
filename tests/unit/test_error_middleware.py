import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.error import ErrorMiddleware, ErrorNotification, ErrorFormatter

@pytest.fixture
def middleware():
    return ErrorMiddleware()

@pytest.fixture
def error_request():
    return {'raise_error': True}

# 1. Teste de captura de erros
def test_error_capture(middleware, error_request):
    with pytest.raises(Exception):
        middleware.process(error_request)

# 2. Teste de formatação de erros
def test_error_formatting(middleware):
    formatter = ErrorFormatter()
    error = Exception('fail')
    formatted = formatter.format(error)
    assert 'fail' in formatted

# 3. Teste de logging de erros
def test_error_logging(middleware, caplog):
    with caplog.at_level('ERROR'):
        try:
            middleware.process({'raise_error': True})
        except Exception:
            pass
    assert any('Error captured' in m for m in caplog.messages)

# 4. Teste de notificação de erros
def test_error_notification(middleware):
    notifier = MagicMock(spec=ErrorNotification)
    middleware.set_notifier(notifier)
    with patch.object(middleware, 'process', side_effect=Exception('fail')):
        try:
            middleware.process({'raise_error': True})
        except Exception:
            pass
    notifier.notify.assert_called()

# 5. Teste de casos edge (erro desconhecido)
def test_edge_case_unknown_error(middleware):
    class UnknownError(Exception): pass
    with pytest.raises(UnknownError):
        middleware.process({'raise_error': UnknownError()})

# 6. Teste de performance
def test_error_handling_performance(middleware, error_request, benchmark):
    def run():
        try:
            middleware.process(error_request)
        except Exception:
            pass
    benchmark(run)

# 7. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process({'raise_error': False}) == 'ok'
    next_middleware.assert_called_once()

# 8. Teste de configuração dinâmica
def test_dynamic_configuration():
    mw = ErrorMiddleware(log_level='WARNING')
    assert mw.log_level == 'WARNING'
    mw.set_log_level('ERROR')
    assert mw.log_level == 'ERROR'

# 9. Teste de logs detalhados
def test_detailed_logging(middleware, caplog):
    with caplog.at_level('DEBUG'):
        try:
            middleware.process({'raise_error': True})
        except Exception:
            pass
    assert any('Traceback' in m or 'DEBUG' in m for m in caplog.messages)

# 10. Teste de métricas de erros
def test_metrics_collected_on_error(middleware):
    with patch.object(middleware, 'metrics') as mock_metrics:
        try:
            middleware.process({'raise_error': True})
        except Exception:
            pass
        mock_metrics.increment.assert_called_with('error.captured') 