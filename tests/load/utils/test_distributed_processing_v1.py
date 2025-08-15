from typing import Dict, List, Optional, Any
"""
Testes de carga para distributed_processing_v1.py
"""
from backend.app.services.distributed_processing_v1 import coletar_keywords_task, processar_keywords_task, exportar_keywords_task
import tempfile

def test_coletar_keywords_task():
    r = coletar_keywords_task.run({"termo": "seo"})
    assert isinstance(r, list)
    assert r[0]["termo"] == "seo"

def test_processar_keywords_task():
    r = processar_keywords_task.run([{"termo": "seo", "volume": 1000}])
    assert r[0]["processado"] is True

def test_exportar_keywords_task():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        r = exportar_keywords_task.run([{"termo": "seo", "volume": 1000}], tmp.name)
        assert r == tmp.name
        with open(tmp.name) as f:
            linhas = f.readlines()
            assert linhas[0].startswith("seo,") 