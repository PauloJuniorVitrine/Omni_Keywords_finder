from typing import Dict, List, Optional, Any
"""
Testes unitários para compliance_report_v1.py
"""
import os
import tempfile
from backend.app.services.compliance_report_v1 import gerar_relatorio_conformidade, COMPLIANCE_REPORT_PATH

def test_gerar_relatorio_ok():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'report.json')
        import backend.app.services.compliance_report_v1 as mod
        mod.COMPLIANCE_REPORT_PATH = path
        metricas = {'execucoes': 10}
        cobertura = {'unit': 99}
        falhas = []
        r = gerar_relatorio_conformidade(metricas, cobertura, falhas)
        assert r == path
        with open(path) as f:
            data = f.read()
            assert 'ok' in data

def test_gerar_relatorio_falha():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'report.json')
        import backend.app.services.compliance_report_v1 as mod
        mod.COMPLIANCE_REPORT_PATH = path
        metricas = {'execucoes': 10}
        cobertura = {'unit': 99}
        falhas = ['erro']
        r = gerar_relatorio_conformidade(metricas, cobertura, falhas)
        with open(path) as f:
            data = f.read()
            assert 'falha' in data 