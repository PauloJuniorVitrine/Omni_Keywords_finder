from typing import Dict, List, Optional, Any
"""
Testes unitários para KeywordGapSuggester (keyword_gap_suggestion_v1.py)
"""
from backend.app.services.keyword_gap_suggestion_v1 import KeywordGapSuggester

def test_detectar_lacunas():
    sugg = KeywordGapSuggester()
    assert sugg.detectar_lacunas([], [{'termo': 'b'}])['falta_primaria']
    assert sugg.detectar_lacunas([{'termo': 'a'}], [])['falta_secundaria']
    assert not sugg.detectar_lacunas([{'termo': 'a'}], [{'termo': 'b'}])['falta_primaria']
    assert not sugg.detectar_lacunas([{'termo': 'a'}], [{'termo': 'b'}])['falta_secundaria']

def test_sugerir_secundarias():
    sugg = KeywordGapSuggester(threshold=0.5)
    primarias = [{'termo': 'marketing digital'}]
    candidatos = [
        {'termo': 'marketing de conteudo'},
        {'termo': 'financas pessoais'},
        {'termo': 'marketing digital avancado'},
    ]
    sugestoes = sugg.sugerir_secundarias(primarias, candidatos)
    assert any('conteudo' in string_data['termo'] or 'avancado' in string_data['termo'] for string_data in sugestoes)

def test_validar_complementaridade():
    sugg = KeywordGapSuggester(threshold=0.5)
    primaria = {'termo': 'gestao de projetos'}
    secundaria = {'termo': 'gestao de projetos avancada'}
    assert sugg.validar_complementaridade(primaria, secundaria)
    secundaria2 = {'termo': 'culinaria vegana'}
    assert not sugg.validar_complementaridade(primaria, secundaria2)

def test_similaridade_edge_case():
    sugg = KeywordGapSuggester()
    assert sugg.similaridade('', '') == 1.0
    assert sugg.similaridade('a', '') == 0.0 