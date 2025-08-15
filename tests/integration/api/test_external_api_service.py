import pytest
from backend.app.services.external_api_service import fetch_external_data, breaker
from unittest.mock import patch, MagicMock
import requests
from typing import Dict, List, Optional, Any

def setup_function():
    breaker.close()

def test_fetch_external_data_success():
    with patch('requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'ok': True}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = fetch_external_data('http://api.test/sucesso', 'token')
        assert result == {'ok': True}

def test_fetch_external_data_http_error():
    with patch('requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError('Erro HTTP')
        mock_get.return_value = mock_resp
        with pytest.raises(requests.HTTPError):
            fetch_external_data('http://api.test/erro', 'token')

def test_fetch_external_data_timeout():
    with patch('requests.get', side_effect=requests.Timeout):
        with pytest.raises(requests.Timeout):
            fetch_external_data('http://api.test/timeout', 'token')

def test_fetch_external_data_retries(monkeypatch):
    call_count = {'count': 0}
    def fail_then_succeed(*args, **kwargs):
        call_count['count'] += 1
        if call_count['count'] < 3:
            raise requests.RequestException('Falha')
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'ok': True}
        mock_resp.raise_for_status.return_value = None
        return mock_resp
    with patch('requests.get', side_effect=fail_then_succeed):
        result = fetch_external_data('http://api.test/retry', 'token')
        assert result == {'ok': True}
        assert call_count['count'] == 3

def test_fetch_external_data_circuit_breaker():
    breaker.close()
    with patch('requests.get', side_effect=requests.RequestException('Falha')):
        for _ in range(3):
            with pytest.raises(requests.RequestException):
                try:
                    fetch_external_data('http://api.test/break', 'token')
                except Exception:
                    pass
        # Circuit breaker deve abrir
        with pytest.raises(pybreaker.CircuitBreakerError):
            fetch_external_data('http://api.test/break', 'token') 