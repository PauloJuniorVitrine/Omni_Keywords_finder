import pytest
from infrastructure.monitoramento.observabilidade import log_structured, generate_trace_uuid, REQUEST_COUNT, REQUEST_FAILURES, REQUEST_LATENCY
import logging
from typing import Dict, List, Optional, Any

def test_generate_trace_uuid():
    uuid1 = generate_trace_uuid()
    uuid2 = generate_trace_uuid()
    assert isinstance(uuid1, str)
    assert uuid1 != uuid2

def test_log_structured(caplog):
    with caplog.at_level(logging.INFO):
        log_structured('Teste log', {'foo': 'bar'}, 'info')
    assert any('Teste log' in str(record) and 'foo' in str(record) for record in caplog.records)

def test_prometheus_metrics():
    REQUEST_COUNT.labels(endpoint='/api/test', status='200').inc()
    REQUEST_FAILURES.labels(endpoint='/api/test').inc()
    with REQUEST_LATENCY.labels(endpoint='/api/test').time():
        pass
    # Não há assert direto, mas não deve lançar exceção 