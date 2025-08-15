import pytest
from infrastructure.processamento.normalizador_handler import NormalizadorHandler
from domain.models import Keyword
from typing import Dict, List, Optional, Any

@pytest.fixture
def keywords_exemplo():
    return [
        Keyword(termo="Café", volume_busca=100, cpc=1.2, concorrencia=0.5, intencao=0.8, score=0, justificativa=None, fonte="test", data_coleta=None),
        Keyword(termo="café ", volume_busca=50, cpc=0.8, concorrencia=0.3, intencao=0.7, score=0, justificativa=None, fonte="test", data_coleta=None),
        Keyword(termo="CAFÉ", volume_busca=10, cpc=0.5, concorrencia=0.2, intencao=0.6, score=0, justificativa=None, fonte="test", data_coleta=None),
        Keyword(termo="", volume_busca=0, cpc=0, concorrencia=0, intencao=0, score=0, justificativa=None, fonte="test", data_coleta=None),
    ]

def test_normalizador_handler_remover_acentos(keywords_exemplo):
    handler = NormalizadorHandler(remover_acentos=True, case_sensitive=False)
    result = handler.handle(keywords_exemplo, contexto={})
    termos = [kw.termo for kw in result]
    assert "cafe" in termos
    assert len(termos) == 1

def test_normalizador_handler_case_sensitive(keywords_exemplo):
    handler = NormalizadorHandler(remover_acentos=False, case_sensitive=True)
    result = handler.handle(keywords_exemplo, contexto={})
    termos = [kw.termo for kw in result]
    assert "Café" in termos
    assert "CAFÉ" in termos
    assert len(termos) == 2

def test_normalizador_handler_vazio():
    handler = NormalizadorHandler()
    result = handler.handle([], contexto={})
    assert result == []

def test_normalizador_handler_ignora_termo_vazio():
    handler = NormalizadorHandler()
    kw = Keyword(termo="", volume_busca=0, cpc=0, concorrencia=0, intencao=0, score=0, justificativa=None, fonte="test", data_coleta=None)
    result = handler.handle([kw], contexto={})
    assert result == []

@pytest.fixture
def handler():
    return NormalizadorHandler(remover_acentos=True, case_sensitive=False)

@pytest.mark.parametrize("entrada,esperado", [
    ([Keyword(termo=" Teste ", volume_busca=10, cpc=1.2, concorrencia=0.5)], [Keyword(termo="teste", volume_busca=10, cpc=1.2, concorrencia=0.5)]),
    ([Keyword(termo="AÇÃO", volume_busca=5, cpc=0.5, concorrencia=0.2)], [Keyword(termo="acao", volume_busca=5, cpc=0.5, concorrencia=0.2)]),
    ([Keyword(termo="palavra!", volume_busca=1, cpc=0.1, concorrencia=0.1)], [Keyword(termo="palavra!", volume_busca=1, cpc=0.1, concorrencia=0.1)]),
    ([Keyword(termo="   ", volume_busca=1, cpc=0.1, concorrencia=0.1)], []),
    ([], []),
    ([Keyword(termo=None, volume_busca=1, cpc=0.1, concorrencia=0.1)], []),
    ([Keyword(termo="duplicado", volume_busca=1, cpc=0.1, concorrencia=0.1), Keyword(termo="duplicado", volume_busca=2, cpc=0.2, concorrencia=0.2)], [Keyword(termo="duplicado", volume_busca=1, cpc=0.1, concorrencia=0.1)]),
    ([Keyword(termo="áéíóú", volume_busca=1, cpc=0.1, concorrencia=0.1)], [Keyword(termo="aeiou", volume_busca=1, cpc=0.1, concorrencia=0.1)]),
])
def test_handle_edge_cases(handler, entrada, esperado):
    result = handler.handle(entrada, contexto={})
    assert isinstance(result, list)
    assert len(result) == len(esperado)
    for r, e in zip(result, esperado):
        assert r.termo == e.termo

@pytest.mark.parametrize("entrada", [
    None,
    [None],
    [Keyword(termo=None, volume_busca=None, cpc=None, concorrencia=None)],
])
def test_handle_invalid_inputs(handler, entrada):
    with pytest.raises(Exception):
        handler.handle(entrada, contexto={})

def test_handle_tipo_errado(handler):
    with pytest.raises(Exception):
        handler.handle(None) 