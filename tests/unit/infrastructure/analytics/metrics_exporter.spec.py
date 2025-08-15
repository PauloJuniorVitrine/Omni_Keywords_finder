import pytest
from flask import Flask
from infrastructure.monitoramento.metrics_exporter import metrics_bp, track_keywords_processadas, track_exportacao, KEYWORDS_PROCESSADAS, EXPORTACOES_REALIZADAS, ERROS_PROCESSAMENTO
from typing import Dict, List, Optional, Any

def test_metrics_endpoint_exposes_prometheus():
    app = Flask(__name__)
    app.register_blueprint(metrics_bp)
    client = app.test_client()
    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert b'keywords_processadas_total' in resp.data
    assert b'exportacoes_realizadas_total' in resp.data

def test_track_keywords_processadas_increments():
    KEYWORDS_PROCESSADAS._value.set(0)
    @track_keywords_processadas
    def dummy():
        return [1, 2, 3]
    dummy()
    assert KEYWORDS_PROCESSADAS._value.get() == 3

def test_track_exportacao_increments():
    EXPORTACOES_REALIZADAS._value.set(0)
    @track_exportacao
    def dummy():
        return True
    dummy()
    assert EXPORTACOES_REALIZADAS._value.get() == 1

def test_track_keywords_processadas_error():
    ERROS_PROCESSAMENTO._value.set(0)
    @track_keywords_processadas
    def fail():
        raise Exception('fail')
    with pytest.raises(Exception):
        fail()
    assert ERROS_PROCESSAMENTO._value.get() == 1 