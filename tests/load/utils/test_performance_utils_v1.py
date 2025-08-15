from typing import Dict, List, Optional, Any
"""
Testes de performance para performance_utils_v1.py
"""
from backend.app.services.performance_utils_v1 import medir_tempo_execucao
import time

def test_medir_tempo_execucao():
    @medir_tempo_execucao
    def soma(a, b):
        time.sleep(0.01)
        return a + b
    resultado, duracao = soma(2, 3)
    assert resultado == 5
    assert duracao >= 0.01

def test_medir_tempo_execucao_zero():
    @medir_tempo_execucao
    def ident(value):
        return value
    resultado, duracao = ident('ok')
    assert resultado == 'ok'
    assert duracao >= 0 