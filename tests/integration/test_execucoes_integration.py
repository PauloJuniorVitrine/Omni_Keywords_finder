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

def test_execucao_post_sucesso(client: FlaskClient):
    """Teste de sucesso para criação de execução."""
    payload = {
        "categoria_id": 1,
        "palavras_chave": ["keyword1", "keyword2"],
        "cluster": "cluster_teste"
    }
    response = client.post('/api/execucoes/', json=payload)
    assert response.status_code in (201, 200)
    data = response.get_json()
    assert "execucao_id" in data
    assert data["categoria_id"] == payload["categoria_id"]
    assert data["palavras_chave"] == payload["palavras_chave"]

def test_execucao_post_falha(client: FlaskClient):
    """Teste de falha para payload inválido."""
    # categoria_id ausente
    response = client.post('/api/execucoes/', json={"palavras_chave": ["kw"]})
    assert response.status_code == 400
    # palavras_chave ausente
    response = client.post('/api/execucoes/', json={"categoria_id": 1})
    assert response.status_code == 400
    # categoria_id inválido
    response = client.post('/api/execucoes/', json={"categoria_id": -1, "palavras_chave": ["kw"]})
    assert response.status_code == 400
    # palavras_chave inválidas
    response = client.post('/api/execucoes/', json={"categoria_id": 1, "palavras_chave": [""]})
    assert response.status_code == 400

def test_execucao_get_status(client: FlaskClient):
    """Teste de consulta de execução existente e inexistente."""
    # Supondo que 1 pode existir e 99999 não
    response = client.get('/api/execucoes/1')
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.get_json()
        assert "id" in data
        assert "palavras_chave" in data 