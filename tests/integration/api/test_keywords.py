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

def test_processar_keywords_sucesso(client):
    payload = {"keywords": [{"termo": "python", "volume_busca": 100, "cpc": 1.0, "concorrencia": 0.5}]}
    resp = client.post('/api/processar_keywords', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "keywords" in data and "relatorio" in data
    assert isinstance(data["keywords"], list)
    assert data["relatorio"]["status"] == "ok"

def test_processar_keywords_lista_vazia(client):
    resp = client.post('/api/processar_keywords', json={"keywords": []})
    assert resp.status_code == 400
    assert "erro" in resp.get_json()

def test_processar_keywords_tipo_errado(client):
    resp = client.post('/api/processar_keywords', json={"keywords": "nao_lista"})
    assert resp.status_code == 400
    assert "erro" in resp.get_json()

def test_processar_keywords_campo_obrigatorio_ausente(client):
    resp = client.post('/api/processar_keywords', json={})
    assert resp.status_code == 400
    assert "erro" in resp.get_json()

def test_processar_keywords_valores_invalidos(client):
    payload = {"keywords": [{"termo": "", "volume_busca": -1, "cpc": -1, "concorrencia": 2}]}
    resp = client.post('/api/processar_keywords', json=payload)
    assert resp.status_code == 422
    assert "erro" in resp.get_json() 