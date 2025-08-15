import pytest
from backend.app import create_app
from flask.testing import FlaskClient
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_agendar_execucao_sucesso(client: FlaskClient):
    """Teste de sucesso para agendamento de execução."""
    payload = {
        "categoria_id": 1,
        "palavras_chave": ["kw1", "kw2"],
        "cluster": "cluster_nome",
        "data_agendada": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "usuario": "usuario_teste"
    }
    response = client.post('/api/execucoes/agendar', json=payload)
    assert response.status_code in (201, 200)
    data = response.get_json()
    assert "id" in data

def test_agendar_execucao_falha(client: FlaskClient):
    """Teste de falha para payload inválido."""
    # categoria_id ausente
    payload = {
        "palavras_chave": ["kw1"],
        "data_agendada": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "usuario": "usuario_teste"
    }
    response = client.post('/api/execucoes/agendar', json=payload)
    assert response.status_code == 400
    # data_agendada inválida
    payload = {
        "categoria_id": 1,
        "palavras_chave": ["kw1"],
        "data_agendada": "data_invalida",
        "usuario": "usuario_teste"
    }
    response = client.post('/api/execucoes/agendar', json=payload)
    assert response.status_code == 400

def test_listar_execucoes_agendadas(client: FlaskClient):
    """Teste de listagem de execuções agendadas."""
    response = client.get('/api/execucoes/agendadas')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list) 