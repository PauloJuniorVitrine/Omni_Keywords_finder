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

def test_dashboard_metrics_ok(client):
    resp = client.get('/api/dashboard/metrics')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert set(data.keys()) == {'keywords', 'exportacoes', 'clusters', 'erros', 'tendencias'}
    assert isinstance(data['keywords'], int)
    assert isinstance(data['exportacoes'], int)
    assert isinstance(data['clusters'], int)
    assert isinstance(data['erros'], int)
    assert isinstance(data['tendencias'], list)
    for t in data['tendencias']:
        assert set(t.keys()) == {'nome', 'volume'}
        assert isinstance(t['nome'], str)
        assert isinstance(t['volume'], int) 