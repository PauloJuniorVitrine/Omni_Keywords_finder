from typing import Dict, List, Optional, Any
"""
Testes unitários para RankingExplain (ranking_explain_v1.py)
"""
from backend.app.services.ranking_config_v1 import RankingConfig
from backend.app.services.ranking_explain_v1 import RankingExplain

def test_explicar_ranking_basico():
    config = RankingConfig()
    explain = RankingExplain(config)
    palavras = [
        {'termo': 'a', 'volume': 100, 'concorrencia': 0.5, 'tendencia': 0.8, 'intencao': 0.7, 'ctr': 0.6},
    ]
    resultado = explain.explicar(palavras)
    assert resultado[0]['termo'] == 'a'
    assert 'detalhes' in resultado[0]
    assert 'score' in resultado[0]
    assert resultado[0]['detalhes']['volume']['parcial'] == 100 * config.pesos['volume']

def test_explicar_ranking_pesos_customizados():
    config = RankingConfig(pesos={'volume': 0.1, 'concorrencia': 0.7, 'tendencia': 0.1, 'intencao': 0.05, 'ctr': 0.05})
    explain = RankingExplain(config)
    palavras = [
        {'termo': 'b', 'volume': 200, 'concorrencia': 0.9, 'tendencia': 0.5, 'intencao': 0.6, 'ctr': 0.4},
    ]
    resultado = explain.explicar(palavras)
    assert resultado[0]['termo'] == 'b'
    assert resultado[0]['detalhes']['concorrencia']['valor'] == 0.1

def test_explicar_ranking_lista_vazia():
    config = RankingConfig()
    explain = RankingExplain(config)
    resultado = explain.explicar([])
    assert resultado == [] 