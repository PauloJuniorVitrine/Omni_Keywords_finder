import pytest
from infrastructure.processamento.normalizador_handler import NormalizadorHandler
from domain.models import Keyword, IntencaoBusca
from typing import Dict, List, Optional, Any

@pytest.fixture
def handler():
    return NormalizadorHandler(remover_acentos=True, case_sensitive=False)

@pytest.mark.parametrize("entrada,esperado", [
    ([Keyword(termo=" Teste ", volume_busca=10, cpc=1.2, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)], [Keyword(termo="teste", volume_busca=10, cpc=1.2, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)]),
    ([Keyword(termo="AÇÃO", volume_busca=5, cpc=0.5, concorrencia=0.2, intencao=IntencaoBusca.INFORMACIONAL)], [Keyword(termo="acao", volume_busca=5, cpc=0.5, concorrencia=0.2, intencao=IntencaoBusca.INFORMACIONAL)]),
    ([Keyword(termo="palavra!", volume_busca=1, cpc=0.1, concorrencia=0.1, intencao=IntencaoBusca.INFORMACIONAL)], [Keyword(termo="palavra!", volume_busca=1, cpc=0.1, concorrencia=0.1, intencao=IntencaoBusca.INFORMACIONAL)]),
    ([], []),
    ([Keyword(termo="duplicado", volume_busca=1, cpc=0.1, concorrencia=0.1, intencao=IntencaoBusca.INFORMACIONAL), Keyword(termo="duplicado", volume_busca=2, cpc=0.2, concorrencia=0.2, intencao=IntencaoBusca.INFORMACIONAL)], [Keyword(termo="duplicado", volume_busca=1, cpc=0.1, concorrencia=0.1, intencao=IntencaoBusca.INFORMACIONAL)]),
    ([Keyword(termo="áéíóú", volume_busca=1, cpc=0.1, concorrencia=0.1, intencao=IntencaoBusca.INFORMACIONAL)], [Keyword(termo="aeiou", volume_busca=1, cpc=0.1, concorrencia=0.1, intencao=IntencaoBusca.INFORMACIONAL)]),
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
])
def test_handle_invalid_inputs(handler, entrada):
    with pytest.raises(Exception):
        handler.handle(entrada, contexto={})

def test_keyword_invalid_instantiation():
    with pytest.raises(ValueError):
        Keyword(termo="", volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)

def test_handle_tipo_errado(handler):
    with pytest.raises(Exception):
        handler.handle(None) 