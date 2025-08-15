import pytest
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from domain.models import Keyword, IntencaoBusca
from typing import Dict, List, Optional, Any

def make_keyword(termo: str, score: float = 0.0) -> Keyword:
    return Keyword(
        termo=termo,
        volume_busca=10,
        cpc=1.0,
        concorrencia=0.5,
        intencao=IntencaoBusca.INFORMACIONAL,
        score=score
    )

def test_callback_pos_excecao():
    def cb(a, r): raise Exception("erro")
    val = ValidadorKeywords(callback_pos=cb)
    kws = [make_keyword("termo valido teste")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 0

def test_blacklist_dinamica():
    val = ValidadorKeywords()
    val.adicionar_blacklist("proibido exemplo teste")
    kws = [make_keyword("proibido exemplo teste"), make_keyword("permitido exemplo teste")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 1 