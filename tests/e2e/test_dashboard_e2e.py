import requests
import pytest
from typing import Dict, List, Optional, Any

def test_dashboard_metrics_e2e():
    """
    Teste E2E: Valida o endpoint /api/dashboard/metrics (dashboard).
    - Verifica status 200
    - Verifica estrutura e tipos dos dados retornados
    """
    url = "http://localhost:5000/api/dashboard/metrics"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    data = resp.json()
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