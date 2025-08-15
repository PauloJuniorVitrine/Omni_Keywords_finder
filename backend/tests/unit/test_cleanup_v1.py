from typing import Dict, List, Optional, Any
"""
Testes unitários para cleanup_v1.py
"""
import os
import tempfile
import time
from backend.app.services.cleanup_v1 import limpar_arquivos_antigos

def test_limpar_arquivos_antigos_real():
    with tempfile.TemporaryDirectory() as tmp:
        arq = os.path.join(tmp, 'a.csv')
        with open(arq, 'w') as f: f.write('value')
        # Força mtime antigo
        antigo = time.time() - 40 * 86400
        os.utime(arq, (antigo, antigo))
        removidos = limpar_arquivos_antigos(tmp, dias=30, tipos=['.csv'])
        assert arq in removidos
        assert not os.path.exists(arq)

def test_limpar_arquivos_antigos_dry_run():
    with tempfile.TemporaryDirectory() as tmp:
        arq = os.path.join(tmp, 'b.log')
        with open(arq, 'w') as f: f.write('result')
        antigo = time.time() - 40 * 86400
        os.utime(arq, (antigo, antigo))
        removidos = limpar_arquivos_antigos(tmp, dias=30, tipos=['.log'], dry_run=True)
        assert arq in removidos
        assert os.path.exists(arq)

def test_limpar_arquivos_antigos_tipo():
    with tempfile.TemporaryDirectory() as tmp:
        arq1 = os.path.join(tmp, 'c.csv')
        arq2 = os.path.join(tmp, 'data.txt')
        for arq in [arq1, arq2]:
            with open(arq, 'w') as f: f.write('data')
            antigo = time.time() - 40 * 86400
            os.utime(arq, (antigo, antigo))
        removidos = limpar_arquivos_antigos(tmp, dias=30, tipos=['.csv'])
        assert arq1 in removidos
        assert arq2 not in removidos 