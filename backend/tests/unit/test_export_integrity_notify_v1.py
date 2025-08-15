from typing import Dict, List, Optional, Any
"""
Testes unitários para ExportIntegrity e ExportNotifier (export_integrity_notify_v1.py)
"""
import os
import tempfile
from backend.app.services.export_integrity_notify_v1 import ExportIntegrity, ExportNotifier

def test_gerar_e_verificar_hash():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b'abc123')
        tmp.flush()
        h = ExportIntegrity.gerar_hash(tmp.name)
        assert isinstance(h, str)
        assert ExportIntegrity.verificar_hash(tmp.name, h)
        # Modifica arquivo
        with open(tmp.name, 'wb') as f:
            f.write(b'outro')
        assert not ExportIntegrity.verificar_hash(tmp.name, h)
    os.remove(tmp.name)

def test_salvar_hash():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b'data')
        tmp.flush()
        h = ExportIntegrity.gerar_hash(tmp.name)
        hash_path = ExportIntegrity.salvar_hash(tmp.name, h)
        with open(hash_path) as f:
            assert f.read() == h
    os.remove(tmp.name)
    os.remove(hash_path)

def test_enviar_email_webhook():
    assert ExportNotifier.enviar_email('a@b.com', 'Teste', 'Corpo')
    assert ExportNotifier.enviar_webhook('http://localhost', {'ok': True}) 