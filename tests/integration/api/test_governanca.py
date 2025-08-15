import sys
import os
from typing import Dict, List, Optional, Any
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
import pytest
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_governanca_logs_sucesso(client):
    headers = {"Authorization": "Bearer token_teste"}
    resp = client.get('/api/governanca/logs?event=validacao_keywords', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "logs" in data and isinstance(data["logs"], list)

def test_governanca_logs_parametro_invalido(client):
    headers = {"Authorization": "Bearer token_teste"}
    resp = client.get('/api/governanca/logs?event=', headers=headers)
    assert resp.status_code == 400
    assert "erro" in resp.get_json()

def test_governanca_regras_upload_sucesso(client):
    payload = {"score_minimo": 0.7, "blacklist": ["kw1"], "whitelist": ["kw2"]}
    resp = client.post('/api/governanca/regras/upload', json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"

def test_governanca_regras_upload_invalido(client):
    payload = {"score_minimo": "abc", "blacklist": [], "whitelist": []}
    resp = client.post('/api/governanca/regras/upload', json=payload)
    assert resp.status_code == 422
    assert "erro" in resp.get_json()

def test_governanca_regras_editar_sucesso(client):
    payload = {"score_minimo": 0.7, "blacklist": ["kw1"], "whitelist": ["kw2"]}
    resp = client.post('/api/governanca/regras/editar', json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"

def test_governanca_regras_editar_invalido(client):
    payload = {"score_minimo": None, "blacklist": "notalist", "whitelist": 123}
    resp = client.post('/api/governanca/regras/editar', json=payload)
    assert resp.status_code == 422
    assert "erro" in resp.get_json()

def test_governanca_regras_atual(client):
    resp = client.get('/api/governanca/regras/atual')
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data.keys()) == {"score_minimo", "blacklist", "whitelist"} 