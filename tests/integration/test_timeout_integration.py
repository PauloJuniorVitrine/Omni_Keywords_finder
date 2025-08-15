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

def test_timeout_endpoint(client: FlaskClient):
    """Teste de timeout e fallback do endpoint."""
    response = client.get('/api/test/timeout')
    assert response.status_code in (200, 504)
    # Opcional: checar mensagem de erro ou fallback 