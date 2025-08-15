from typing import Dict, List, Optional, Any
"""
Testes unitários para o validador de keywords.
"""
import pytest
from datetime import datetime
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from domain.models import Keyword, IntencaoBusca
import re
from infrastructure.processamento.validacao_handler import ValidacaoHandler

def make_keyword(termo: str, score: float = 0.0) -> Keyword:
    """Helper para criar keywords de teste."""
    return Keyword(
        termo=termo,
        volume_busca=10,
        cpc=1.0,
        concorrencia=0.5,
        intencao=IntencaoBusca.INFORMACIONAL,
        score=score
    )

def test_validar_lista_vazia():
    """Testa validação de lista vazia."""
    val = ValidadorKeywords()
    aprovadas, rejeitadas, _ = val.validar_lista([])
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 0

def test_validar_lista_termo_valido():
    """Testa validação de termo válido."""
    val = ValidadorKeywords()
    kws = [make_keyword("termo valido teste")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 0

def test_validar_lista_termo_invalido():
    """Testa validação de termo inválido."""
    val = ValidadorKeywords()
    with pytest.raises(ValueError, match="Termo não pode ser vazio"):
        make_keyword("")

def test_validar_lista_espacos():
    """Testa validação de termo com apenas espaços."""
    val = ValidadorKeywords()
    with pytest.raises(ValueError, match="Termo não pode ser vazio"):
        make_keyword("   ")

def test_validar_lista_caracteres_especiais():
    """Testa validação de termo com caracteres especiais."""
    val = ValidadorKeywords()
    with pytest.raises(ValueError, match="Termo contém caracteres especiais não permitidos"):
        make_keyword("termo@invalido")

def test_validar_lista_blacklist():
    """Testa validação de termo na blacklist."""
    val = ValidadorKeywords(blacklist=["termo"])
    kws = [make_keyword("termo")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_whitelist():
    """Testa validação de termo na whitelist."""
    val = ValidadorKeywords(whitelist=["termo valido teste"])
    kws = [make_keyword("termo valido teste"), make_keyword("banido exemplo teste")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 1

def test_validar_lista_tamanho():
    """Testa validação de tamanho do termo."""
    val = ValidadorKeywords(tamanho_max=5)
    kws = [make_keyword("termo longo")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_palavras_obrigatorias():
    """Testa validação de palavras obrigatórias."""
    val = ValidadorKeywords(palavras_obrigatorias=["obrigatoria"])
    kws = [make_keyword("termo sem palavra")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_score():
    """Testa validação de score mínimo."""
    val = ValidadorKeywords(score_minimo=1.0)
    kws = [make_keyword("termo")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_volume():
    """Testa validação de volume mínimo."""
    val = ValidadorKeywords(volume_min=100)
    kws = [make_keyword("termo")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_cpc():
    """Testa validação de CPC mínimo."""
    val = ValidadorKeywords(cpc_min=2.0)
    kws = [make_keyword("termo")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_concorrencia():
    """Testa validação de concorrência máxima."""
    val = ValidadorKeywords(concorrencia_max=0.3)
    kws = [make_keyword("termo")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_duplicados():
    """Testa validação de termos duplicados."""
    val = ValidadorKeywords()
    kws = [make_keyword("termo valido teste"), make_keyword("termo valido teste")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 1

def test_validar_lista_callback():
    """Testa callback pós-validação."""
    chamado = False
    def callback(aprovadas, rejeitadas):
        nonlocal chamado
        chamado = True
        assert len(aprovadas) == 1
        assert len(rejeitadas) == 0
    
    val = ValidadorKeywords(callback_pos=callback)
    kws = [make_keyword("ok")]
    val.validar_lista(kws)
    assert chamado

def test_validar_lista_callback_excecao():
    """Testa erro no callback pós-validação."""
    def cb(a, r):
        raise Exception("erro")
    val = ValidadorKeywords(callback_pos=cb)
    kws = [make_keyword("termo valido teste")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 0

def test_validar_lista_score_minimo():
    """Testa validação de score mínimo."""
    val = ValidadorKeywords(score_minimo=2.0)
    kws = [make_keyword("termo", score=1.0)]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_score_none():
    """Testa validação de score None."""
    val = ValidadorKeywords(score_minimo=1.0)
    kws = [make_keyword("termo", score=0.0)]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_score_negativo():
    """Testa validação de score negativo."""
    val = ValidadorKeywords(score_minimo=0.0)
    kws = [make_keyword("termo", score=-1.0)]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 0
    assert len(rejeitadas) == 1

def test_validar_lista_regex():
    """Testa validação com regex personalizada (exemplo: rejeita números)."""
    val = ValidadorKeywords(regex_termo=r"^[A-Za-data\string_data]+$")  # Aceita apenas letras e espaços
    kws = [
        make_keyword("apenas letras validas"),
        make_keyword("com123 letras validas"),
        make_keyword("outro exemplo valido")
    ]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 2
    assert len(rejeitadas) == 1

def test_validar_lista_regex_invalida():
    """Testa validação com regex inválida."""
    with pytest.raises(re.error):
        ValidadorKeywords(regex_termo="[")

def test_validar_lista_atualizar_blacklist_whitelist():
    """Testa atualização de blacklist e whitelist."""
    val = ValidadorKeywords()
    val.adicionar_blacklist("banido exemplo teste")
    val.adicionar_whitelist("ok exemplo teste")
    kws = [make_keyword("ok exemplo teste"), make_keyword("banido exemplo teste")]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 1

def test_validar_lista_relatorio():
    """Testa geração de relatório."""
    val = ValidadorKeywords(blacklist=["banido exemplo teste"], tamanho_min=2)
    kws = [make_keyword("ok exemplo teste"), make_keyword("banido exemplo teste")]
    aprovadas, rejeitadas, relatorio = val.validar_lista(kws, relatorio=True)
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 1
    assert aprovadas[0].termo == "ok exemplo teste"
    assert rejeitadas[0].termo == "banido exemplo teste"
    assert relatorio["total_aprovado"] == 1
    assert relatorio["total_rejeitado"] == 1
    assert "blacklist" in relatorio["motivos_rejeicao"]

def test_debug_regex_matching():
    """Teste temporário para debug do comportamento do regex."""
    val = ValidadorKeywords(regex_termo=r"^[A-Za-data\string_data]+$")  # Aceita apenas letras e espaços
    kws = [
        make_keyword("apenas letras validas"),
        make_keyword("com123 letras validas"),
        make_keyword("outro exemplo valido")
    ]
    aprovadas, rejeitadas, _ = val.validar_lista(kws)
    assert len(aprovadas) == 2
    assert len(rejeitadas) == 1

def make_kw(termo, volume=100, cpc=1.0, concorrencia=0.4, intencao=IntencaoBusca.INFORMACIONAL):
    return Keyword(
        termo=termo,
        volume_busca=volume,
        cpc=cpc,
        concorrencia=concorrencia,
        intencao=intencao,
        score=0.0,
        justificativa="",
        fonte="teste",
        data_coleta=None
    )

def test_validador_aprova_cauda_longa():
    handler = ValidacaoHandler(validador=None)
    kws = [make_kw("palavra chave cauda longa exemplo", concorrencia=0.4)]
    aprovadas = handler.handle(kws, contexto={})
    assert len(aprovadas) == 1
    assert aprovadas[0].termo == "palavra chave cauda longa exemplo"

def test_validador_rejeita_curto_ou_concorrente():
    handler = ValidacaoHandler(validador=None)
    # Termo curto
    kws = [make_kw("curta", concorrencia=0.4)]
    aprovadas = handler.handle(kws, contexto={})
    assert len(aprovadas) == 0
    # Concorrência alta
    kws = [make_kw("palavra chave cauda longa exemplo", concorrencia=0.8)]
    aprovadas = handler.handle(kws, contexto={})
    assert len(aprovadas) == 0
    # Menos de 3 palavras
    kws = [make_kw("duas palavras", concorrencia=0.4)]
    aprovadas = handler.handle(kws, contexto={})
    assert len(aprovadas) == 0
    # Exatamente 3 palavras e 15 caracteres
    kws = [make_kw("abc def ghijklmno", concorrencia=0.5)]
    aprovadas = handler.handle(kws, contexto={})
    assert len(aprovadas) == 1
    assert aprovadas[0].termo == "abc def ghijklmno" 