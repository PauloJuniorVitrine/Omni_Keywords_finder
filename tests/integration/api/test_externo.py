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

def test_google_trends_sucesso(client):
    resp = client.get('/api/externo/google_trends?termo=python')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["termo"] == "python"
    assert "volume" in data and isinstance(data["volume"], int) 