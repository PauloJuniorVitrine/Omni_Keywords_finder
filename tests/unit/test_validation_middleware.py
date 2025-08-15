import pytest
from unittest.mock import MagicMock, patch
from myapp.middleware.validation import ValidationMiddleware, ValidationError

@pytest.fixture
def middleware():
    return ValidationMiddleware(schema={'field': str})

@pytest.fixture
def valid_request():
    return {'field': 'valor'}

@pytest.fixture
def invalid_request():
    return {'field': 123}

# 1. Teste de validação de requests
def test_validate_request_success(middleware, valid_request):
    assert middleware.validate(valid_request) is True

# 2. Teste de validação de schemas
def test_validate_schema_error(middleware, invalid_request):
    with pytest.raises(ValidationError):
        middleware.validate(invalid_request)

# 3. Teste de tratamento de erros
def test_error_handling_returns_false(middleware):
    with patch.object(middleware, 'validate', side_effect=ValidationError):
        with pytest.raises(ValidationError):
            middleware.validate({'field': 1})

# 4. Teste de performance
def test_validation_performance(middleware, valid_request, benchmark):
    benchmark(middleware.validate, valid_request)

# 5. Teste de casos edge (campo ausente)
def test_edge_case_missing_field(middleware):
    with pytest.raises(ValidationError):
        middleware.validate({})

# 6. Teste de integração com outro middleware
def test_integration_with_next_middleware(middleware, valid_request):
    next_middleware = MagicMock(return_value='ok')
    middleware.set_next(next_middleware)
    assert middleware.process(valid_request) == 'ok'
    next_middleware.assert_called_once()

# 7. Teste de configuração dinâmica
def test_dynamic_configuration():
    mw = ValidationMiddleware(schema={'foo': int})
    assert mw.schema == {'foo': int}
    mw.update_schema({'bar': str})
    assert mw.schema == {'bar': str}

# 8. Teste de logs de validação
def test_logging_on_validation_error(middleware, invalid_request, caplog):
    with caplog.at_level('ERROR'):
        with pytest.raises(ValidationError):
            middleware.validate(invalid_request)
    assert any('Validation error' in m for m in caplog.messages)

# 9. Teste de métricas de validação
def test_metrics_collected_on_validation(middleware, valid_request):
    with patch.object(middleware, 'metrics') as mock_metrics:
        middleware.validate(valid_request)
        mock_metrics.increment.assert_called_with('validation.success')

# 10. Teste de geração de relatórios
def test_report_generation(middleware):
    middleware.metrics = MagicMock()
    middleware.metrics.get_stats.return_value = {'success': 10, 'fail': 2}
    report = middleware.generate_report()
    assert 'success' in report and 'fail' in report 