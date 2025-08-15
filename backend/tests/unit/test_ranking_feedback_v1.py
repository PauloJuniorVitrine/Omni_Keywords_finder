from typing import Dict, List, Optional, Any
"""
Testes unitários para RankingFeedback (ranking_feedback_v1.py)
"""
import os
import tempfile
from backend.app.services.ranking_feedback_v1 import RankingFeedback

def test_registrar_e_consultar_feedback():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        fb = RankingFeedback(storage_path=tmp.name)
        fb.registrar('termo1', 'preferida')
        assert fb.consultar('termo1') == 'preferida'
        fb.registrar('termo2', 'irrelevante')
        assert fb.consultar('termo2') == 'irrelevante'
    os.remove(tmp.name)

def test_influenciar_score():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        fb = RankingFeedback(storage_path=tmp.name)
        fb.registrar('termo1', 'preferida')
        fb.registrar('termo2', 'irrelevante')
        palavras = [
            {'termo': 'termo1', 'score': 5},
            {'termo': 'termo2', 'score': 5},
            {'termo': 'termo3', 'score': 5},
        ]
        resultado = fb.influenciar(palavras)
        assert next(p for p in resultado if p['termo'] == 'termo1')['score'] == 15
        assert next(p for p in resultado if p['termo'] == 'termo2')['score'] == -5
        assert next(p for p in resultado if p['termo'] == 'termo3')['score'] == 5
    os.remove(tmp.name)

def test_feedback_edge_cases():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        fb = RankingFeedback(storage_path=tmp.name)
        palavras = [{'termo': 'nao_registrado', 'score': 0}]
        resultado = fb.influenciar(palavras)
        assert resultado[0]['score'] == 0
    os.remove(tmp.name) 