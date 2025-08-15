from typing import Dict, List, Optional, Any
"""
Testes unitários para auditoria_v1.py
"""
import os
import tempfile
from backend.app.services.auditoria_v1 import registrar_log, consultar_logs, AUDIT_LOG_PATH

def test_registrar_e_consultar_log():
    with tempfile.TemporaryDirectory() as tmp:
        log_path = os.path.join(tmp, 'audit.log')
        # Monkeypatch path
        import backend.app.services.auditoria_v1 as mod
        mod.AUDIT_LOG_PATH = log_path
        registrar_log('criação', 'Categoria', 'admin', 'Criou categoria', '123')
        logs = consultar_logs(tipo_operacao='criação', entidade='Categoria', usuario='admin')
        assert logs[0]['entidade'] == 'Categoria'
        assert logs[0]['usuario'] == 'admin'
        assert logs[0]['tipo_operacao'] == 'criação'

def test_consultar_logs_vazio():
    with tempfile.TemporaryDirectory() as tmp:
        log_path = os.path.join(tmp, 'audit.log')
        import backend.app.services.auditoria_v1 as mod
        mod.AUDIT_LOG_PATH = log_path
        logs = consultar_logs()
        assert logs == [] 