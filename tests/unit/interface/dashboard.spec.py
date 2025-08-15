import pytest
from flask import Flask
from app.pages.dashboard.index import dashboard_bp
from typing import Dict, List, Optional, Any

def test_dashboard_endpoint_renders_metrics(monkeypatch):
    app = Flask(__name__)
    app.register_blueprint(dashboard_bp)
    client = app.test_client()
    # Mock get_metric_value para valores previsíveis
    monkeypatch.setattr('app.pages.dashboard.index.get_metric_value', lambda name: 42)
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'Keywords processadas' in html
    assert 'Exportações realizadas' in html
    assert 'Clusters gerados' in html
    assert 'Rejeições/Erros' in html
    assert 'Ver métricas Prometheus' in html 