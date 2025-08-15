from typing import Dict, List, Optional, Any
"""
Testes unitários para RankingConfig (ranking_config_v1.py)
"""
import pytest
from backend.app.services.ranking_config_v1 import RankingConfig

def test_ranqueamento_padrao():
    ranking = RankingConfig()
    palavras = [
        {'termo': 'a', 'volume': 100, 'concorrencia': 0.5, 'tendencia': 0.8, 'intencao': 0.7, 'ctr': 0.6},
        {'termo': 'b', 'volume': 200, 'concorrencia': 0.2, 'tendencia': 0.5, 'intencao': 0.6, 'ctr': 0.4},
    ]
    resultado = ranking.ranquear(palavras)
    assert resultado[0]['termo'] == 'b'

def test_ranqueamento_pesos_customizados():
    ranking = RankingConfig(pesos={'volume': 0.1, 'concorrencia': 0.7, 'tendencia': 0.1, 'intencao': 0.05, 'ctr': 0.05})
    palavras = [
        {'termo': 'a', 'volume': 100, 'concorrencia': 0.1, 'tendencia': 0.8, 'intencao': 0.7, 'ctr': 0.6},
        {'termo': 'b', 'volume': 200, 'concorrencia': 0.9, 'tendencia': 0.5, 'intencao': 0.6, 'ctr': 0.4},
    ]
    resultado = ranking.ranquear(palavras)
    assert resultado[0]['termo'] == 'a'

def test_ranqueamento_lista_vazia():
    ranking = RankingConfig()
    resultado = ranking.ranquear([])
    assert resultado == [] 