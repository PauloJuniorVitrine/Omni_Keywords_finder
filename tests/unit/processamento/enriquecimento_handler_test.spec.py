import pytest
from infrastructure.processamento.enriquecimento_handler import EnriquecimentoHandler
from domain.models import Keyword, IntencaoBusca
from typing import Dict, List, Optional, Any

@pytest.fixture
def handler():
    return EnriquecimentoHandler()

@pytest.fixture
def keywords_reais():
    """Fixtures com keywords reais do domínio para substituir dados sintéticos."""
    return [
        Keyword(
            termo="marketing digital",
            volume_busca=1200,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.COMERCIAL,
            fonte="google_ads",
            data_coleta=None
        ),
        Keyword(
            termo="como criar blog",
            volume_busca=800,
            cpc=1.8,
            concorrencia=0.4,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_ads",
            data_coleta=None
        ),
        Keyword(
            termo="melhor plataforma wordpress",
            volume_busca=950,
            cpc=3.2,
            concorrencia=0.6,
            intencao=IntencaoBusca.COMPARACAO,
            fonte="google_ads",
            data_coleta=None
        ),
        Keyword(
            termo="wordpress.com login",
            volume_busca=1500,
            cpc=0.5,
            concorrencia=0.3,
            intencao=IntencaoBusca.NAVEGACIONAL,
            fonte="google_ads",
            data_coleta=None
        )
    ]

@pytest.fixture
def keyword_com_erro():
    """Keyword que simula erro de cálculo para testes de exceção."""
    kw = Keyword(
        termo="teste erro",
        volume_busca=100,
        cpc=1.0,
        concorrencia=0.5,
        intencao=IntencaoBusca.INFORMACIONAL,
        fonte="test",
        data_coleta=None
    )
    # Monkey patch para simular erro
    original_calcular = kw.calcular_score
    def calcular_com_erro(weights):
        raise ValueError("Erro de cálculo simulado")
    kw.calcular_score = calcular_com_erro
    return kw

@pytest.mark.parametrize("entrada", [
    [Keyword(termo="palavra valida teste", volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)],
    [],
    [Keyword(termo="palavra", volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL), Keyword(termo="", volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)],
])
def test_handle_edge_cases(handler, entrada):
    result = handler.handle(entrada, contexto={"pesos": {"volume": 0.4, "cpc": 0.2, "intention": 0.2, "competition": 0.2}})
    assert isinstance(result, list)
    for r in result:
        assert hasattr(r, "score")
        assert hasattr(r, "justificativa")

@pytest.mark.parametrize("entrada", [
    None,
    [None],
    [Keyword(termo=None, volume_busca=None, cpc=None, concorrencia=None, intencao=IntencaoBusca.INFORMACIONAL)],
])
def test_handle_invalid_inputs(handler, entrada):
    with pytest.raises(Exception):
        handler.handle(entrada, contexto={})

def test_handle_tipo_errado(handler):
    with pytest.raises(Exception):
        handler.handle(None)

def test_enriquecimento_handler_sucesso(handler, keywords_reais):
    """Teste de sucesso usando keywords reais do domínio."""
    kw = keywords_reais[0]  # "marketing digital"
    result = handler.handle([kw], contexto={"pesos": {"volume": 0.4, "cpc": 0.3, "intencao": 0.2, "concorrencia": 0.1}})
    assert len(result) == 1
    assert result[0].score > 0
    assert "Score calculado" in result[0].justificativa
    assert "marketing digital" in result[0].justificativa

def test_enriquecimento_handler_erro(handler, keyword_com_erro):
    """Teste de erro usando keyword real com erro simulado."""
    result = handler.handle([keyword_com_erro], contexto={"pesos": {"volume": 0.4, "cpc": 0.3, "intencao": 0.2, "concorrencia": 0.1}})
    assert result == []

def test_enriquecimento_handler_vazio(handler):
    result = handler.handle([], contexto={"pesos": {}})
    assert result == []

def test_enriquecimento_handler_multiplas_keywords(handler, keywords_reais):
    """Teste com múltiplas keywords reais do domínio."""
    result = handler.handle(keywords_reais, contexto={"pesos": {"volume": 0.4, "cpc": 0.3, "intencao": 0.2, "concorrencia": 0.1}})
    assert len(result) == 4
    
    # Verifica que cada keyword foi processada
    termos_processados = [kw.termo for kw in result]
    assert "marketing digital" in termos_processados
    assert "como criar blog" in termos_processados
    assert "melhor plataforma wordpress" in termos_processados
    assert "wordpress.com login" in termos_processados
    
    # Verifica que scores foram calculados
    for kw in result:
        assert kw.score > 0
        assert kw.justificativa != ""

def test_enriquecimento_handler_diferentes_intencoes(handler, keywords_reais):
    """Teste verificando diferentes intenções de busca."""
    result = handler.handle(keywords_reais, contexto={"pesos": {"volume": 0.4, "cpc": 0.3, "intencao": 0.2, "concorrencia": 0.1}})
    
    # Verifica que keywords comerciais têm scores diferentes
    comercial_keywords = [kw for kw in result if kw.intencao == IntencaoBusca.COMERCIAL]
    informacional_keywords = [kw for kw in result if kw.intencao == IntencaoBusca.INFORMACIONAL]
    
    assert len(comercial_keywords) > 0
    assert len(informacional_keywords) > 0
    
    # Keywords comerciais devem ter scores diferentes das informacionais
    scores_comerciais = [kw.score for kw in comercial_keywords]
    scores_informacionais = [kw.score for kw in informacional_keywords]
    
    # Verifica que há diferença nos scores (comerciais tendem a ter scores mais altos)
    assert any(sc > si for sc in scores_comerciais for si in scores_informacionais) 