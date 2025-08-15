import pytest
from infrastructure.processamento.limpeza_handler import LimpezaHandler
from domain.models import Keyword
from typing import Dict, List, Optional, Any

@pytest.fixture
def keywords_limpeza():
    return [
        Keyword(termo="abc", volume_busca=1, cpc=1, concorrencia=0.1, intencao=0.5, score=0, justificativa=None, fonte="test", data_coleta=None),
        Keyword(termo="", volume_busca=1, cpc=1, concorrencia=0.1, intencao=0.5, score=0, justificativa=None, fonte="test", data_coleta=None),
        Keyword(termo=None, volume_busca=1, cpc=1, concorrencia=0.1, intencao=0.5, score=0, justificativa=None, fonte="test", data_coleta=None),
    ]

def test_limpeza_handler_remove_invalidos(keywords_limpeza):
    handler = LimpezaHandler()
    result = handler.handle(keywords_limpeza, contexto={})
    assert all(kw.termo for kw in result)
    assert len(result) == 1

def test_limpeza_handler_vazio():
    handler = LimpezaHandler()
    result = handler.handle([], contexto={})
    assert result == []

@pytest.fixture
def handler():
    return LimpezaHandler()

@pytest.mark.parametrize("entrada,esperado", [
    ([Keyword(termo="palavra valida teste", volume_busca=10, cpc=1.0, concorrencia=0.5)], [Keyword(termo="palavra valida teste", volume_busca=10, cpc=1.0, concorrencia=0.5)]),
    ([Keyword(termo="a", volume_busca=-1, cpc=1.0, concorrencia=0.5)], []),
    ([Keyword(termo="", volume_busca=10, cpc=1.0, concorrencia=0.5)], []),
    ([], []),
    ([Keyword(termo="palavra", volume_busca=-10, cpc=1.0, concorrencia=0.5)], []),
    ([Keyword(termo="palavra", volume_busca=10, cpc=-1.0, concorrencia=0.5)], []),
    ([Keyword(termo="palavra", volume_busca=10, cpc=1.0, concorrencia=1.5)], []),
    ([Keyword(termo="palavra", volume_busca=10, cpc=1.0, concorrencia=-0.1)], []),
    ([Keyword(termo="palavra", volume_busca=10, cpc=1.0, concorrencia=0.5), Keyword(termo="", volume_busca=10, cpc=1.0, concorrencia=0.5)], [Keyword(termo="palavra", volume_busca=10, cpc=1.0, concorrencia=0.5)]),
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