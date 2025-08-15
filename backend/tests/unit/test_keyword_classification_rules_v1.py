from typing import Dict, List, Optional, Any
"""
Testes unitários para KeywordClassifier (keyword_classification_rules_v1.py)
"""
from backend.app.services.keyword_classification_rules_v1 import KeywordClassifier, regra_por_volume, regra_por_intencao

def test_classificar_por_volume():
    palavras = [
        {'termo': 'a', 'volume': 1500},
        {'termo': 'b', 'volume': 800},
    ]
    clf = KeywordClassifier(lambda p: regra_por_volume(p, limiar=1000))
    resultado = clf.classificar(palavras)
    assert len(resultado['primarias']) == 1
    assert resultado['primarias'][0]['termo'] == 'a'
    assert len(resultado['secundarias']) == 1
    assert resultado['secundarias'][0]['termo'] == 'b'

def test_classificar_por_intencao():
    palavras = [
        {'termo': 'value', 'intencao': 0.8},
        {'termo': 'result', 'intencao': 0.5},
    ]
    clf = KeywordClassifier(lambda p: regra_por_intencao(p, limiar=0.7))
    resultado = clf.classificar(palavras)
    assert resultado['primarias'][0]['termo'] == 'value'
    assert resultado['secundarias'][0]['termo'] == 'result'

def test_classificar_edge_cases():
    palavras = [
        {'termo': 'data'},  # sem volume/intencao
    ]
    clf = KeywordClassifier(lambda p: regra_por_volume(p, limiar=1000))
    resultado = clf.classificar(palavras)
    assert resultado['secundarias'][0]['termo'] == 'data'

def test_classificar_regra_invalida():
    palavras = [{'termo': 'a'}]
    clf = KeywordClassifier(lambda p: None)
    resultado = clf.classificar(palavras)
    assert resultado['primarias'] == []
    assert resultado['secundarias'] == [] 