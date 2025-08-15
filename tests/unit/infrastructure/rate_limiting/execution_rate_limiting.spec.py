"""
Testes unitários para rate limiting de execuções
Prompt: Implementação de rate limiting para execuções
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from backend.app.middleware.execucao_rate_limiting import (
    ExecucaoRateLimitConfig, execucao_rate_limited, validate_batch_size,
    get_execucao_rate_limit_stats
)

def test_execucao_rate_limit_config():
    config = ExecucaoRateLimitConfig()
    assert config.individual_requests_per_minute == 10
    assert config.individual_requests_per_hour == 100
    assert config.batch_requests_per_minute == 2
    assert config.max_execucoes_per_batch == 50

@patch('backend.app.middleware.execucao_rate_limiting.RATE_LIMITING_AVAILABLE', True)
@patch('backend.app.middleware.execucao_rate_limiting.get_rate_limiter')
def test_execucao_rate_limited_individual_success(mock_get_rate_limiter):
    # Mock do rate limiter
    mock_limiter = Mock()
    mock_limiter.get_count.return_value = 5  # Dentro do limite
    mock_get_rate_limiter.return_value = mock_limiter
    
    # Mock do Flask
    mock_request = Mock()
    mock_request.endpoint = 'execucoes.executar_prompt'
    mock_g = Mock()
    mock_g.user_id = 'user123'
    
    with patch('backend.app.middleware.execucao_rate_limiting.request', mock_request):
        with patch('backend.app.middleware.execucao_rate_limiting.g', mock_g):
            with patch('backend.app.middleware.execucao_rate_limiting.jsonify') as mock_jsonify:
                # Função de teste
                @execucao_rate_limited()
                def test_func():
                    return "success"
                
                result = test_func()
                assert result == "success"
                assert mock_limiter.increment.call_count == 3  # minuto, hora, dia

@patch('backend.app.middleware.execucao_rate_limiting.RATE_LIMITING_AVAILABLE', True)
@patch('backend.app.middleware.execucao_rate_limiting.get_rate_limiter')
def test_execucao_rate_limited_individual_exceeded(mock_get_rate_limiter):
    # Mock do rate limiter
    mock_limiter = Mock()
    mock_limiter.get_count.return_value = 10  # Limite excedido
    mock_get_rate_limiter.return_value = mock_limiter
    
    # Mock do Flask
    mock_request = Mock()
    mock_request.endpoint = 'execucoes.executar_prompt'
    mock_g = Mock()
    mock_g.user_id = 'user123'
    
    with patch('backend.app.middleware.execucao_rate_limiting.request', mock_request):
        with patch('backend.app.middleware.execucao_rate_limiting.g', mock_g):
            with patch('backend.app.middleware.execucao_rate_limiting.jsonify') as mock_jsonify:
                mock_response = Mock()
                mock_response.status_code = 429
                mock_jsonify.return_value = mock_response
                
                # Função de teste
                @execucao_rate_limited()
                def test_func():
                    return "success"
                
                result = test_func()
                assert result.status_code == 429

@patch('backend.app.middleware.execucao_rate_limiting.RATE_LIMITING_AVAILABLE', True)
@patch('backend.app.middleware.execucao_rate_limiting.get_rate_limiter')
def test_execucao_rate_limited_batch_success(mock_get_rate_limiter):
    # Mock do rate limiter
    mock_limiter = Mock()
    mock_limiter.get_count.return_value = 1  # Dentro do limite
    mock_get_rate_limiter.return_value = mock_limiter
    
    # Mock do Flask
    mock_request = Mock()
    mock_request.endpoint = 'execucoes.executar_lote'
    mock_g = Mock()
    mock_g.user_id = 'user123'
    
    with patch('backend.app.middleware.execucao_rate_limiting.request', mock_request):
        with patch('backend.app.middleware.execucao_rate_limiting.g', mock_g):
            with patch('backend.app.middleware.execucao_rate_limiting.jsonify') as mock_jsonify:
                # Função de teste
                @execucao_rate_limited()
                def test_func():
                    return "success"
                
                result = test_func()
                assert result == "success"

def test_validate_batch_size_success():
    # Mock do Flask
    mock_request = Mock()
    mock_request.get_json.return_value = {
        'execucoes': [{'categoria_id': 1, 'palavras_chave': ['test']}] * 10  # 10 execuções
    }
    
    with patch('backend.app.middleware.execucao_rate_limiting.request', mock_request):
        with patch('backend.app.middleware.execucao_rate_limiting.jsonify') as mock_jsonify:
            # Função de teste
            @validate_batch_size()
            def test_func():
                return "success"
            
            result = test_func()
            assert result == "success"

def test_validate_batch_size_exceeded():
    # Mock do Flask
    mock_request = Mock()
    mock_request.get_json.return_value = {
        'execucoes': [{'categoria_id': 1, 'palavras_chave': ['test']}] * 60  # 60 execuções (excede 50)
    }
    
    with patch('backend.app.middleware.execucao_rate_limiting.request', mock_request):
        with patch('backend.app.middleware.execucao_rate_limiting.jsonify') as mock_jsonify:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_jsonify.return_value = mock_response
            
            # Função de teste
            @validate_batch_size()
            def test_func():
                return "success"
            
            result = test_func()
            assert result.status_code == 400

@patch('backend.app.middleware.execucao_rate_limiting.RATE_LIMITING_AVAILABLE', True)
@patch('backend.app.middleware.execucao_rate_limiting.get_rate_limiter')
def test_get_execucao_rate_limit_stats(mock_get_rate_limiter):
    # Mock do rate limiter
    mock_limiter = Mock()
    mock_limiter.get_count.return_value = 5
    mock_get_rate_limiter.return_value = mock_limiter
    
    stats = get_execucao_rate_limit_stats('user123')
    
    assert 'individual' in stats
    assert 'batch' in stats
    assert 'limits' in stats
    assert stats['individual']['minute'] == 5
    assert stats['limits']['individual']['per_minute'] == 10

@patch('backend.app.middleware.execucao_rate_limiting.RATE_LIMITING_AVAILABLE', False)
def test_get_execucao_rate_limit_stats_unavailable():
    stats = get_execucao_rate_limit_stats('user123')
    assert 'erro' in stats
    assert stats['erro'] == 'Rate limiting não disponível'

def test_execucao_rate_limited_fallback():
    # Mock do Flask
    mock_request = Mock()
    mock_request.endpoint = 'execucoes.executar_prompt'
    mock_g = Mock()
    mock_g.user_id = 'user123'
    
    with patch('backend.app.middleware.execucao_rate_limiting.RATE_LIMITING_AVAILABLE', False):
        with patch('backend.app.middleware.execucao_rate_limiting.request', mock_request):
            with patch('backend.app.middleware.execucao_rate_limiting.g', mock_g):
                # Função de teste
                @execucao_rate_limited()
                def test_func():
                    return "success"
                
                result = test_func()
                assert result == "success" 