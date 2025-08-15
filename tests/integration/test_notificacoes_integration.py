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

def test_criar_notificacao_sucesso(client: FlaskClient):
    """Teste de sucesso para criação de notificação."""
    payload = {
        "titulo": "Título Teste",
        "mensagem": "Mensagem de teste",
        "tipo": "info",
        "usuario": "usuario_teste"
    }
    response = client.post('/api/notificacoes', json=payload)
    assert response.status_code in (201, 200)
    data = response.get_json()
    assert "id" in data

def test_criar_notificacao_falha(client: FlaskClient):
    """Teste de falha para payload inválido."""
    response = client.post('/api/notificacoes', json={"titulo": "Só título"})
    assert response.status_code == 400
    response = client.post('/api/notificacoes', json={"mensagem": "Só mensagem"})
    assert response.status_code == 400

def test_listar_notificacoes(client: FlaskClient):
    """Teste de listagem de notificações."""
    response = client.get('/api/notificacoes')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list) 