import pytest
from domain.models import Keyword, Categoria, Blog, Cluster, Execucao, IntencaoBusca
from datetime import datetime
from typing import Dict, List, Optional, Any

# Testes para Keyword

def test_keyword_valid_creation():
    kw = Keyword(
        termo="palavra-chave",
        volume_busca=100,
        cpc=1.5,
        concorrencia=0.7,
        intencao=IntencaoBusca.INFORMACIONAL
    )
    assert kw.termo == "palavra-chave"
    assert kw.volume_busca == 100
    assert kw.cpc == 1.5
    assert kw.concorrencia == 0.7
    assert kw.intencao == IntencaoBusca.INFORMACIONAL
    assert isinstance(kw.data_coleta, datetime)

def test_keyword_invalid_term():
    with pytest.raises(ValueError):
        Keyword(
            termo="",
            volume_busca=10,
            cpc=0.5,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )

def test_keyword_invalid_competition():
    with pytest.raises(ValueError):
        Keyword(
            termo="abc",
            volume_busca=10,
            cpc=0.5,
            concorrencia=1.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )

def test_keyword_score_calculation():
    kw = Keyword(
        termo="compra online",
        volume_busca=200,
        cpc=2.0,
        concorrencia=0.5,
        intencao=IntencaoBusca.COMERCIAL
    )
    score = kw.calcular_score({"volume": 0.4, "cpc": 0.3, "intencao": 0.2, "concorrencia": 0.1})
    assert score > 0

def test_keyword_to_dict_and_from_dict():
    kw = Keyword(
        termo="teste",
        volume_busca=50,
        cpc=1.0,
        concorrencia=0.3,
        intencao=IntencaoBusca.NAVEGACIONAL
    )
    data = kw.to_dict()
    kw2 = Keyword.from_dict(data)
    assert kw2.termo == "teste"
    assert kw2.intencao == IntencaoBusca.NAVEGACIONAL

# Testes para Categoria

def test_categoria_valid_creation():
    cat = Categoria(
        nome="Tecnologia",
        descricao="Categoria de tecnologia",
        palavras_chave=["python", "machine learning"]
    )
    assert cat.nome == "Tecnologia"
    assert "python" in cat.palavras_chave

def test_categoria_invalid_name():
    with pytest.raises(ValueError):
        Categoria(nome="", descricao="desc")

# Testes para Blog

def test_blog_valid_creation():
    cat = Categoria(nome="Negócios", descricao="desc")
    blog = Blog(
        dominio="meublog.com",
        nome="Meu Blog",
        descricao="Blog de negócios",
        publico_alvo="Empreendedores",
        tom_voz="Formal",
        categorias=[cat]
    )
    assert blog.dominio == "meublog.com"
    assert blog.nome == "Meu Blog"
    assert blog.categorias[0].nome == "Negócios"

def test_blog_duplicate_category():
    cat1 = Categoria(nome="A", descricao="desc")
    cat2 = Categoria(nome="A", descricao="desc")
    with pytest.raises(ValueError):
        Blog(
            dominio="dominio.com",
            nome="Blog",
            descricao="desc",
            publico_alvo="Público",
            tom_voz="Neutro",
            categorias=[cat1, cat2]
        )

# Testes para Cluster

def test_cluster_valid_creation():
    kws = [Keyword(termo=f"kw{index}", volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL) for index in range(6)]
    cluster = Cluster(
        id="cluster1",
        keywords=kws,
        similaridade_media=0.8,
        fase_funil="descoberta",
        categoria="Tech",
        blog_dominio="meublog.com"
    )
    assert cluster.id == "cluster1"
    assert len(cluster.keywords) == 6

def test_cluster_invalid_size():
    # Menos de 4 keywords
    kws_few = [Keyword(termo=f"kw{index}", volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL) for index in range(3)]
    with pytest.raises(ValueError):
        Cluster(
            id="c2",
            keywords=kws_few,
            similaridade_media=0.7,
            fase_funil="descoberta",
            categoria="Tech",
            blog_dominio="meublog.com"
        )
    # Mais de 8 keywords
    kws_many = [Keyword(termo=f"kw{index}", volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL) for index in range(9)]
    with pytest.raises(ValueError):
        Cluster(
            id="c3",
            keywords=kws_many,
            similaridade_media=0.7,
            fase_funil="descoberta",
            categoria="Tech",
            blog_dominio="meublog.com"
        )

# Testes para Execucao

def test_execucao_valid_creation():
    execucao = Execucao(
        id="exec1",
        blog_dominio="meublog.com",
        categoria="Tech",
        tipo_execucao="individual",
        modelo_ia="openai"
    )
    assert execucao.id == "exec1"
    assert execucao.status == "iniciada"

def test_execucao_invalid_type():
    with pytest.raises(ValueError):
        Execucao(
            id="e2",
            blog_dominio="meublog.com",
            categoria="Tech",
            tipo_execucao="invalido",
            modelo_ia="openai"
        ) 