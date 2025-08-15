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

def test_listar_categorias(client: FlaskClient):
    """Teste de listagem de categorias de um nicho."""
    # Supondo nicho_id=1
    response = client.get('/api/categorias/1/')
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.get_json()
        assert isinstance(data, list)

def test_listar_nichos(client: FlaskClient):
    """Teste de listagem de nichos."""
    response = client.get('/api/nichos/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_listar_clusters(client: FlaskClient):
    """Teste de sugestão de clusters."""
    response = client.get('/api/clusters/sugerir?categoria_id=1&palavras_chave=kw1,kw2')
    assert response.status_code in (200, 400)
    if response.status_code == 200:
        data = response.get_json()
        assert "sugestoes" in data 