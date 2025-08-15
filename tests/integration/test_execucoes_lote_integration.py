import pytest
from backend.app import create_app
from flask.testing import FlaskClient
from typing import Dict, List, Optional, Any

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_execucoes_lote_post_sucesso(client: FlaskClient):
    """Teste de sucesso para execução em lote."""
    payload = [
        {"categoria_id": 1, "palavras_chave": ["kw1"], "cluster": "A"},
        {"categoria_id": 2, "palavras_chave": ["kw2", "kw3"], "cluster": "B"}
    ]
    response = client.post('/api/execucoes/lote', json=payload)
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert isinstance(data, dict) or isinstance(data, list)

def test_execucoes_lote_post_idempotencia(client: FlaskClient):
    """Teste de idempotência para execução em lote."""
    payload = [
        {"categoria_id": 1, "palavras_chave": ["kw1"], "cluster": "A"}
    ]
    response1 = client.post('/api/execucoes/lote', json=payload)
    response2 = client.post('/api/execucoes/lote', json=payload)
    assert response1.status_code == response2.status_code

def test_execucoes_lote_status_get(client: FlaskClient):
    """Teste de consulta de status de lote."""
    # id_lote fictício para simular consulta
    response = client.get('/api/execucoes/lote/status?id_lote=1')
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.get_json()
        assert "id_lote" in data
        assert "total" in data 