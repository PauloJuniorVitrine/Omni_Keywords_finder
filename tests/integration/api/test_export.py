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

def test_exportar_keywords_json(client):
    resp = client.get('/api/exportar_keywords?formato=json')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert all("termo" in kw and "score" in kw for kw in data)

def test_exportar_keywords_csv(client):
    resp = client.get('/api/exportar_keywords?formato=csv')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'text/csv'
    assert "termo,score" in resp.get_data(as_text=True)

def test_exportar_keywords_formato_invalido(client):
    resp = client.get('/api/exportar_keywords?formato=xml')
    assert resp.status_code == 400
    assert "erro" in resp.get_json() 