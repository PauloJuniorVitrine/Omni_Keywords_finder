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

def test_shadow_canario_comparacao(client: FlaskClient):
    """Teste de comparação canário entre versões de endpoint."""
    response_v1 = client.get('/api/execucoes/v1')
    response_v2 = client.get('/api/execucoes/v2')
    assert response_v1.status_code == response_v2.status_code
    if response_v1.status_code == 200:
        assert response_v1.get_json() == response_v2.get_json() 