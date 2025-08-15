from typing import Dict, List, Optional, Any
"""
Testes unitários para client_api_externa_v1.py
"""
import pytest
from infrastructure.consumo_externo.client_api_externa_v1 import APIExternaClientV1
from tenacity import RetryError

class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.elapsed = type('obj', (object,), {'total_seconds': lambda self: 0.1})()
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception('Erro')

def test_get_sucesso(monkeypatch):
    client = APIExternaClientV1('http://api', 'token')
    def fake_get(*a, **kw):
        return FakeResponse(200, {'ok': True})
    monkeypatch.setattr('requests.get', fake_get)
    resultado = client.get('endpoint')
    assert resultado['ok'] is True

def test_get_falha(monkeypatch):
    client = APIExternaClientV1('http://api', 'token')
    def fake_get(*a, **kw):
        raise Exception('Falha')
    monkeypatch.setattr('requests.get', fake_get)
    with pytest.raises(Exception):
        client.get('endpoint')

def test_get_com_fallback(monkeypatch):
    client = APIExternaClientV1('http://api', 'token')
    def erro(*a, **kw):
        raise RetryError('Falha')
    monkeypatch.setattr(client, 'get', erro)
    resultado = client.get_com_fallback('endpoint')
    assert 'fallback' in str(resultado['erro']) 