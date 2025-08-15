import pytest
from domain.models import Keyword, IntencaoBusca, Categoria, Blog, Cluster, Execucao
from datetime import datetime, timedelta
from unittest.mock import patch
from typing import Dict, List, Optional, Any

# --- Keyword ---
def test_keyword_criacao_valida():
    key = Keyword(
        termo="palavra-chave",
        volume_busca=100,
        cpc=1.5,
        concorrencia=0.7,
        intencao=IntencaoBusca.INFORMACIONAL
    )
    assert key.termo == "palavra-chave"
    assert key.volume_busca == 100
    assert key.cpc == 1.5
    assert key.concorrencia == 0.7
    assert key.intencao == IntencaoBusca.INFORMACIONAL

@pytest.mark.parametrize("campo,valor", [
    ("termo", ""),
    ("volume_busca", -1),
    ("cpc", -0.1),
    ("concorrencia", 1.1),
    ("concorrencia", -0.1),
    ("termo", "@!#"),
    ("termo", "t"*101),
])
def test_keyword_invalida(campo, valor):
    kwargs = dict(
        termo="palavra-chave",
        volume_busca=100,
        cpc=1.5,
        concorrencia=0.7,
        intencao=IntencaoBusca.INFORMACIONAL
    )
    kwargs[campo] = valor
    with pytest.raises(ValueError):
        Keyword(**kwargs)

def test_keyword_eq_hash():
    k1 = Keyword("abc", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL)
    k2 = Keyword("ABC", 20, 2, 0.7, IntencaoBusca.COMERCIAL)
    assert k1 == k2
    assert hash(k1) == hash(k2)

def test_keyword_score():
    key = Keyword("abc", 100, 2, 1, IntencaoBusca.COMERCIAL)
    score = key.calcular_score({})
    assert score > 0
    assert "Score =" in key.justificativa

def test_keyword_to_dict_from_dict():
    key = Keyword("abc", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL)
    data = key.to_dict()
    k2 = Keyword.from_dict(data)
    assert key == k2

def test_keyword_normalizar_termo():
    assert Keyword.normalizar_termo(" AbC ") == "abc"

def make_kw(termo, volume=10, cpc=1.0, concorrencia=0.2, intencao=IntencaoBusca.INFORMACIONAL):
    return Keyword(termo=termo, volume_busca=volume, cpc=cpc, concorrencia=concorrencia, intencao=intencao)

def test_keyword_termo_vazio_ou_espacos():
    # Termo vazio
    with pytest.raises(ValueError, match="Termo não pode ser vazio"):
        make_kw("")
    # Termo só espaços
    with pytest.raises(ValueError, match="Termo não pode ser vazio"):
        make_kw("   ")
    # Termo None
    with pytest.raises(ValueError, match="Termo não pode ser vazio"):
        make_kw(None)
    # Termo válido
    kw = make_kw("palavra chave teste")
    assert kw.termo == "palavra chave teste"

# --- EDGE CASES E SERIALIZAÇÃO COMPLEXA ---
def test_keyword_serializacao_complexa_com_campos_opcionais():
    """Testa serialização complexa com todos os campos opcionais."""
    key = Keyword(
        termo="marketing digital",
        volume_busca=1200,
        cpc=2.5,
        concorrencia=0.7,
        intencao=IntencaoBusca.COMERCIAL,
        score=0.85,
        justificativa="Score calculado",
        fonte="google_ads",
        data_coleta=datetime(2024, 1, 15, 10, 30),
        ordem_no_cluster=2,
        fase_funil="consideração",
        nome_artigo="Artigo3"
    )
    
    data = key.to_dict()
    
    # Verificar todos os campos
    assert data["termo"] == "marketing digital"
    assert data["volume_busca"] == 1200
    assert data["cpc"] == 2.5
    assert data["concorrencia"] == 0.7
    assert data["intencao"] == "comercial"
    assert data["score"] == 0.85
    assert data["justificativa"] == "Score calculado"
    assert data["fonte"] == "google_ads"
    assert data["data_coleta"] == "2024-01-15T10:30:00"
    assert data["ordem_no_cluster"] == 2
    assert data["fase_funil"] == "consideração"
    assert data["nome_artigo"] == "Artigo3"
    
    # Testar deserialização
    key2 = Keyword.from_dict(data)
    assert key2.termo == key.termo
    assert key2.ordem_no_cluster == key.ordem_no_cluster
    assert key2.fase_funil == key.fase_funil
    assert key2.nome_artigo == key.nome_artigo

def test_keyword_calculo_score_com_pesos_personalizados():
    """Testa cálculo de score com pesos personalizados."""
    key = Keyword("teste", 1000, 3.0, 0.8, IntencaoBusca.TRANSACIONAL)
    
    # Pesos personalizados
    weights = {
        "volume": 0.5,
        "cpc": 0.2,
        "intencao": 0.2,
        "concorrencia": 0.1
    }
    
    score = key.calcular_score(weights)
    
    # Verificar que o score foi calculado corretamente
    assert score > 0
    assert "volume(1000)" in key.justificativa
    assert "cpc(3.0)" in key.justificativa
    assert "intencao(1.0)" in key.justificativa  # TRANSACIONAL = 1.0
    assert "concorrencia(0.8)" in key.justificativa

def test_keyword_diferentes_intencoes_busca():
    """Testa diferentes intenções de busca."""
    intencoes = [
        IntencaoBusca.INFORMACIONAL,
        IntencaoBusca.COMERCIAL,
        IntencaoBusca.NAVEGACIONAL,
        IntencaoBusca.TRANSACIONAL,
        IntencaoBusca.COMPARACAO
    ]
    
    for intencao in intencoes:
        key = Keyword("teste", 100, 1.0, 0.5, intencao)
        assert key.intencao == intencao
        assert str(key.intencao) == intencao.value
        assert key.intencao.lower() == intencao.value.lower()

def test_keyword_caracteres_especiais_permitidos():
    """Testa caracteres especiais permitidos no termo."""
    termos_validos = [
        "palavra-chave",
        "palavra chave",
        "palavra, chave",
        "palavra? chave",
        "palavra! chave",
        "palavra.chave",
        "palavra_chave"
    ]
    
    for termo in termos_validos:
        key = Keyword(termo, 100, 1.0, 0.5, IntencaoBusca.INFORMACIONAL)
        assert key.termo == termo

def test_keyword_caracteres_especiais_proibidos():
    """Testa caracteres especiais proibidos no termo."""
    termos_invalidos = [
        "palavra@chave",
        "palavra#chave",
        "palavra$chave",
        "palavra%chave",
        "palavra^chave",
        "palavra&chave",
        "palavra*chave",
        "palavra(chave",
        "palavra)chave",
        "palavra+chave",
        "palavra=chave",
        "palavra[chave",
        "palavra]chave",
        "palavra{chave",
        "palavra}chave",
        "palavra|chave",
        "palavra\\chave",
        "palavra/chave",
        "palavra<chave",
        "palavra>chave"
    ]
    
    for termo in termos_invalidos:
        with pytest.raises(ValueError, match="caracteres especiais não permitidos"):
            Keyword(termo, 100, 1.0, 0.5, IntencaoBusca.INFORMACIONAL)

def test_keyword_serializacao_com_data_coleta_none():
    """Testa serialização quando data_coleta é None."""
    key = Keyword("teste", 100, 1.0, 0.5, IntencaoBusca.INFORMACIONAL)
    key.data_coleta = None
    
    data = key.to_dict()
    assert data["data_coleta"] is None

def test_keyword_deserializacao_com_intencao_invalida():
    """Testa deserialização com intenção inválida."""
    data = {
        "termo": "teste",
        "volume_busca": 100,
        "cpc": 1.0,
        "concorrencia": 0.5,
        "intencao": "intencao_invalida",
        "data_coleta": "2024-01-15T10:30:00"
    }
    
    key = Keyword.from_dict(data)
    # Deve usar INFORMACIONAL como padrão
    assert key.intencao == IntencaoBusca.INFORMACIONAL

# --- Categoria ---
def test_categoria_criacao_valida():
    c = Categoria(
        nome="Categoria",
        descricao="Descrição",
        palavras_chave=["abc", "def"],
    )
    assert c.nome == "Categoria"
    assert c.descricao == "Descrição"
    assert set(c.palavras_chave) == {"abc", "def"}

def test_categoria_invalida():
    with pytest.raises(ValueError):
        Categoria(nome="", descricao="desc")
    with pytest.raises(ValueError):
        Categoria(nome="t"*51, descricao="desc")
    with pytest.raises(ValueError):
        Categoria(nome="Nome", descricao="data"*201)
    with pytest.raises(ValueError):
        Categoria(nome="Nome@", descricao="desc")
    with pytest.raises(ValueError):
        Categoria(nome="Nome", descricao="desc", palavras_chave=["t"*101])
    with pytest.raises(ValueError):
        Categoria(nome="Nome", descricao="desc", palavras_chave=["abc@!"])

def test_categoria_to_dict_from_dict():
    c = Categoria(nome="Nome", descricao="desc", palavras_chave=["abc"])
    data = c.to_dict()
    c2 = Categoria.from_dict(data)
    assert c.nome == c2.nome

def test_categoria_atualizar_status_log():
    c = Categoria(nome="cat", descricao="desc")
    with patch("domain.models.logger") as logger_mock:
        c.atualizar_status("executando")
        logger_mock.info.assert_called()
        assert c.status_execucao == "executando"
        assert c.ultima_execucao is not None

def test_categoria_adicionar_cluster_log():
    from domain.models import Cluster, Keyword
    keywords = [Keyword(f"abc{index}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for index in range(6)]
    c = Categoria(nome="cat", descricao="desc")
    clu = Cluster(id="clu1", keywords=keywords, similaridade_media=0.8, fase_funil="descoberta", categoria="cat", blog_dominio="meublog.com")
    with patch("domain.models.logger") as logger_mock:
        c.adicionar_cluster(clu)
        logger_mock.info.assert_called()
        assert c.clusters_gerados[0] == clu
    # Testa erro de categoria diferente
    keywords2 = [Keyword(f"xyz{index}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for index in range(6)]
    with pytest.raises(ValueError):
        c.adicionar_cluster(Cluster(id="clu2", keywords=keywords2, similaridade_media=0.8, fase_funil="descoberta", categoria="outra", blog_dominio="meublog.com"))

# --- EDGE CASES CATEGORIA ---
def test_categoria_palavras_chave_duplicadas():
    """Testa remoção de palavras-chave duplicadas."""
    c = Categoria(
        nome="Teste",
        descricao="Descrição",
        palavras_chave=["abc", "ABC", "abc", "def", "DEF"]
    )
    # Deve normalizar e remover duplicatas
    assert set(c.palavras_chave) == {"abc", "def"}

def test_categoria_palavras_chave_vazias():
    """Testa palavras-chave vazias ou só espaços."""
    c = Categoria(
        nome="Teste",
        descricao="Descrição",
        palavras_chave=["abc", "", "   ", "def", "  xyz  "]
    )
    # Deve remover vazias e normalizar
    assert set(c.palavras_chave) == {"abc", "def", "xyz"}

def test_categoria_serializacao_completa():
    """Testa serialização completa com clusters."""
    from domain.models import Cluster, Keyword
    keywords = [Keyword(f"kw{i}", 100, 1.0, 0.5, IntencaoBusca.INFORMACIONAL) for i in range(6)]
    cluster = Cluster(id="clu1", keywords=keywords, similaridade_media=0.8, fase_funil="descoberta", categoria="Teste", blog_dominio="test.com")
    
    c = Categoria(nome="Teste", descricao="Descrição", palavras_chave=["abc"])
    c.clusters_gerados = [cluster]
    c.status_execucao = "concluida"
    c.ultima_execucao = datetime(2024, 1, 15, 10, 30)
    
    data = c.to_dict()
    
    assert data["nome"] == "Teste"
    assert data["descricao"] == "Descrição"
    assert data["palavras_chave"] == ["abc"]
    assert data["status_execucao"] == "concluida"
    assert data["ultima_execucao"] == "2024-01-15T10:30:00"
    assert data["total_clusters"] == 1

# --- Blog ---
def test_blog_criacao_valida():
    c = Categoria(nome="cat", descricao="desc")
    b = Blog(
        dominio="meublog.com",
        nome="Meu Blog",
        descricao="desc",
        publico_alvo="público",
        tom_voz="formal",
        categorias=[c]
    )
    assert b.dominio == "meublog.com"
    assert b.nome == "Meu Blog"
    assert b.categorias[0].nome == "cat"

def test_blog_invalido():
    with pytest.raises(ValueError):
        Blog(dominio="", nome="n", descricao="data", publico_alvo="p", tom_voz="t")
    with pytest.raises(ValueError):
        Blog(dominio="dominio.com", nome="t"*101, descricao="data", publico_alvo="p", tom_voz="t")
    with pytest.raises(ValueError):
        Blog(dominio="dominio.com", nome="n", descricao="data"*501, publico_alvo="p", tom_voz="t")
    with pytest.raises(ValueError):
        Blog(dominio="dominio.com", nome="n", descricao="data", publico_alvo="p"*201, tom_voz="t")
    with pytest.raises(ValueError):
        Blog(dominio="dominio.com", nome="n", descricao="data", publico_alvo="p", tom_voz="t"*51)
    with pytest.raises(ValueError):
        Blog(dominio="dominio.com", nome="n", descricao="data", publico_alvo="p", tom_voz="t", categorias=[Categoria(nome="cat", descricao="desc"), Categoria(nome="cat", descricao="desc")])

def test_blog_to_dict_from_dict():
    c = Categoria(nome="cat", descricao="desc")
    b = Blog(dominio="meublog.com", nome="Meu Blog", descricao="desc", publico_alvo="p", tom_voz="t", categorias=[c])
    data = b.to_dict()
    b2 = Blog.from_dict(data)
    assert b.dominio == b2.dominio

def test_blog_adicionar_remover_categoria_log():
    c = Categoria(nome="cat", descricao="desc")
    b = Blog(dominio="meublog.com", nome="Meu Blog", descricao="desc", publico_alvo="p", tom_voz="t", categorias=[])
    with patch("domain.models.logger") as logger_mock:
        b.adicionar_categoria(c)
        logger_mock.info.assert_called()
        assert b.categorias[0].nome == "cat"
    with patch("domain.models.logger") as logger_mock:
        b.remover_categoria("cat")
        logger_mock.info.assert_called()
        assert len(b.categorias) == 0
    with pytest.raises(ValueError):
        b.remover_categoria("inexistente")
    with pytest.raises(ValueError):
        b.adicionar_categoria(c)
        b.adicionar_categoria(c)

# --- EDGE CASES BLOG ---
def test_blog_dominio_normalizacao():
    """Testa normalização de domínio."""
    b = Blog(
        dominio="MEUBLOG.COM",
        nome="Meu Blog",
        descricao="desc",
        publico_alvo="público",
        tom_voz="formal"
    )
    assert b.dominio == "meublog.com"

def test_blog_dominio_invalido():
    """Testa domínios inválidos."""
    dominios_invalidos = [
        "dominio",
        ".dominio.com",
        "dominio.",
        "dominio..com",
        "dominio-.com",
        "-dominio.com",
        "dominio@.com",
        "dominio#.com"
    ]
    
    for dominio in dominios_invalidos:
        with pytest.raises(ValueError, match="Domínio inválido"):
            Blog(
                dominio=dominio,
                nome="Meu Blog",
                descricao="desc",
                publico_alvo="público",
                tom_voz="formal"
            )

def test_blog_serializacao_completa():
    """Testa serialização completa do blog."""
    c1 = Categoria(nome="cat1", descricao="desc1")
    c2 = Categoria(nome="cat2", descricao="desc2")
    
    b = Blog(
        dominio="meublog.com",
        nome="Meu Blog",
        descricao="Descrição completa",
        publico_alvo="Público-alvo específico",
        tom_voz="Formal",
        categorias=[c1, c2],
        prompt_base="Prompt base do blog"
    )
    
    data = b.to_dict()
    
    assert data["dominio"] == "meublog.com"
    assert data["nome"] == "Meu Blog"
    assert data["descricao"] == "Descrição completa"
    assert data["publico_alvo"] == "Público-alvo específico"
    assert data["tom_voz"] == "Formal"
    assert data["total_categorias"] == 2
    assert data["prompt_base"] == "Prompt base do blog"
    assert len(data["categorias"]) == 2

# --- Cluster ---
def test_cluster_criacao_valida():
    keywords = [Keyword(f"abc{index}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for index in range(6)]
    c = Cluster(
        id="clu1",
        keywords=keywords,
        similaridade_media=0.8,
        fase_funil="descoberta",
        categoria="cat",
        blog_dominio="meublog.com"
    )
    assert c.id == "clu1"
    assert len(c.keywords) == 6

# --- EDGE CASES CLUSTER ---
def test_cluster_keywords_duplicadas():
    """Testa validação de keywords duplicadas no cluster."""
    keywords = [
        Keyword("abc", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL),
        Keyword("ABC", 20, 2, 0.7, IntencaoBusca.COMERCIAL),  # Duplicada (case insensitive)
        Keyword("def", 30, 3, 0.8, IntencaoBusca.TRANSACIONAL)
    ]
    
    with pytest.raises(ValueError, match="Keyword duplicada no cluster"):
        Cluster(
            id="clu1",
            keywords=keywords,
            similaridade_media=0.8,
            fase_funil="descoberta",
            categoria="cat",
            blog_dominio="meublog.com"
        )

def test_cluster_tamanho_invalido():
    """Testa validação de tamanho do cluster."""
    # Cluster muito pequeno
    keywords_pequeno = [Keyword(f"kw{i}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for i in range(3)]
    with pytest.raises(ValueError, match="Cluster deve conter entre 4 e 8 keywords"):
        Cluster(
            id="clu1",
            keywords=keywords_pequeno,
            similaridade_media=0.8,
            fase_funil="descoberta",
            categoria="cat",
            blog_dominio="meublog.com"
        )
    
    # Cluster muito grande
    keywords_grande = [Keyword(f"kw{i}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for i in range(9)]
    with pytest.raises(ValueError, match="Cluster deve conter entre 4 e 8 keywords"):
        Cluster(
            id="clu1",
            keywords=keywords_grande,
            similaridade_media=0.8,
            fase_funil="descoberta",
            categoria="cat",
            blog_dominio="meublog.com"
        )

def test_cluster_fase_funil_invalida():
    """Testa validação de fase do funil."""
    keywords = [Keyword(f"kw{i}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for i in range(6)]
    
    with pytest.raises(ValueError, match="Fase do funil inválida"):
        Cluster(
            id="clu1",
            keywords=keywords,
            similaridade_media=0.8,
            fase_funil="fase_invalida",
            categoria="cat",
            blog_dominio="meublog.com"
        )

def test_cluster_similaridade_invalida():
    """Testa validação de similaridade média."""
    keywords = [Keyword(f"kw{i}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for i in range(6)]
    
    # Similaridade negativa
    with pytest.raises(ValueError, match="Similaridade média deve estar entre 0 e 1"):
        Cluster(
            id="clu1",
            keywords=keywords,
            similaridade_media=-0.1,
            fase_funil="descoberta",
            categoria="cat",
            blog_dominio="meublog.com"
        )
    
    # Similaridade maior que 1
    with pytest.raises(ValueError, match="Similaridade média deve estar entre 0 e 1"):
        Cluster(
            id="clu1",
            keywords=keywords,
            similaridade_media=1.1,
            fase_funil="descoberta",
            categoria="cat",
            blog_dominio="meublog.com"
        )

def test_cluster_id_invalido():
    """Testa validação de ID do cluster."""
    keywords = [Keyword(f"kw{i}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for i in range(6)]
    
    # ID vazio
    with pytest.raises(ValueError, match="ID do cluster não pode ser vazio"):
        Cluster(
            id="",
            keywords=keywords,
            similaridade_media=0.8,
            fase_funil="descoberta",
            categoria="cat",
            blog_dominio="meublog.com"
        )
    
    # ID com caracteres inválidos
    with pytest.raises(ValueError, match="ID do cluster contém caracteres inválidos"):
        Cluster(
            id="cluster@123",
            keywords=keywords,
            similaridade_media=0.8,
            fase_funil="descoberta",
            categoria="cat",
            blog_dominio="meublog.com"
        )

def test_cluster_serializacao_completa():
    """Testa serialização completa do cluster."""
    keywords = [Keyword(f"kw{i}", 100, 1.0, 0.5, IntencaoBusca.INFORMACIONAL) for i in range(6)]
    
    c = Cluster(
        id="cluster-123",
        keywords=keywords,
        similaridade_media=0.85,
        fase_funil="consideração",
        categoria="Marketing",
        blog_dominio="meublog.com",
        data_criacao=datetime(2024, 1, 15, 10, 30),
        status_geracao="concluida",
        prompt_gerado="Prompt gerado para o cluster"
    )
    
    data = c.to_dict()
    
    assert data["id"] == "cluster-123"
    assert len(data["keywords"]) == 6
    assert data["similaridade_media"] == 0.85
    assert data["fase_funil"] == "consideração"
    assert data["categoria"] == "Marketing"
    assert data["blog_dominio"] == "meublog.com"
    assert data["data_criacao"] == "2024-01-15T10:30:00"
    assert data["status_geracao"] == "concluida"
    assert data["tem_prompt"] is True

def test_cluster_to_dict_from_dict():
    keywords = [Keyword(f"abc{index}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for index in range(6)]
    c = Cluster(
        id="clu1",
        keywords=keywords,
        similaridade_media=0.8,
        fase_funil="descoberta",
        categoria="cat",
        blog_dominio="meublog.com"
    )
    data = c.to_dict()
    c2 = Cluster.from_dict(data)
    assert c.id == c2.id

def test_cluster_atualizar_status_log():
    keywords = [Keyword(f"abc{index}", 10, 1, 0.5, IntencaoBusca.INFORMACIONAL) for index in range(6)]
    c = Cluster(
        id="clu1",
        keywords=keywords,
        similaridade_media=0.8,
        fase_funil="descoberta",
        categoria="cat",
        blog_dominio="meublog.com"
    )
    with patch("domain.models.logger") as logger_mock:
        c.atualizar_status("processando")
        logger_mock.info.assert_called()
        assert c.status_geracao == "processando"

def test_execucao_criacao_valida():
    e = Execucao(
        id="exec1",
        blog_dominio="meublog.com",
        categoria="cat",
        tipo_execucao="individual",
        modelo_ia="gpt-4"
    )
    assert e.id == "exec1"
    assert e.status == "iniciada"

def test_execucao_invalida():
    with pytest.raises(ValueError):
        Execucao(id="", blog_dominio="d", categoria="c", tipo_execucao="individual", modelo_ia="m")
    with pytest.raises(ValueError):
        Execucao(id="exec1", blog_dominio="d", categoria="c", tipo_execucao="invalido", modelo_ia="m")
    with pytest.raises(ValueError):
        Execucao(id="exec1", blog_dominio="d", categoria="c", tipo_execucao="individual", modelo_ia="")

def test_execucao_to_dict_from_dict():
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    data = e.to_dict()
    e2 = Execucao.from_dict(data)
    assert e.id == e2.id

def test_execucao_adicionar_erro_log():
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    with patch("domain.models.logger") as logger_mock:
        e.adicionar_erro("Erro teste")
        logger_mock.error.assert_called()
        assert len(e.erros) == 1

def test_execucao_adicionar_cluster_log():
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    with patch("domain.models.logger") as logger_mock:
        e.adicionar_cluster("cluster1")
        logger_mock.info.assert_called()
        assert e.clusters_gerados[0] == "cluster1"

def test_execucao_atualizar_status_log():
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    with patch("domain.models.logger") as logger_mock:
        e.atualizar_status("processando")
        logger_mock.info.assert_called()
        assert e.status == "processando"

def test_execucao_finalizar_log():
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    e.adicionar_cluster("cluster1")
    with patch("domain.models.logger") as logger_mock:
        e.finalizar(sucesso=True)
        logger_mock.info.assert_called()
        assert e.status == "concluida"
        assert e.fim_execucao is not None

# --- EDGE CASES EXECUÇÃO ---
def test_execucao_limite_erros():
    """Testa limite de erros na execução."""
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    
    # Adicionar erros até o limite
    for i in range(3):
        e.adicionar_erro(f"Erro {i}")
    
    # O 4º erro deve finalizar a execução automaticamente
    e.adicionar_erro("Erro final")
    
    assert e.status == "erro"
    assert e.fim_execucao is not None
    assert len(e.erros) == 4

def test_execucao_metricas_calculo():
    """Testa cálculo de métricas na finalização."""
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    
    # Adicionar clusters
    e.adicionar_cluster("cluster1")
    e.adicionar_cluster("cluster2")
    e.adicionar_cluster("cluster3")
    
    # Finalizar
    e.finalizar(sucesso=True)
    
    assert e.metricas["total_clusters"] == 3
    assert e.metricas["total_erros"] == 0
    assert e.metricas["duracao_segundos"] > 0
    assert e.metricas["media_tempo_cluster"] > 0

def test_execucao_status_invalido():
    """Testa validação de status inválido."""
    e = Execucao(id="exec1", blog_dominio="meublog.com", categoria="cat", tipo_execucao="individual", modelo_ia="gpt-4")
    
    with pytest.raises(ValueError, match="Status inválido"):
        e.atualizar_status("status_invalido")

def test_execucao_serializacao_completa():
    """Testa serialização completa da execução."""
    e = Execucao(
        id="exec-123",
        blog_dominio="meublog.com",
        categoria="Marketing",
        tipo_execucao="lote",
        modelo_ia="gpt-4",
        inicio_execucao=datetime(2024, 1, 15, 10, 30),
        fim_execucao=datetime(2024, 1, 15, 11, 30),
        status="concluida",
        clusters_gerados=["cluster1", "cluster2"],
        erros=["erro1"],
        metricas={"duracao_segundos": 3600}
    )
    
    data = e.to_dict()
    
    assert data["id"] == "exec-123"
    assert data["blog_dominio"] == "meublog.com"
    assert data["categoria"] == "Marketing"
    assert data["tipo_execucao"] == "lote"
    assert data["modelo_ia"] == "gpt-4"
    assert data["inicio_execucao"] == "2024-01-15T10:30:00"
    assert data["fim_execucao"] == "2024-01-15T11:30:00"
    assert data["status"] == "concluida"
    assert data["clusters_gerados"] == ["cluster1", "cluster2"]
    assert data["total_clusters"] == 2
    assert data["erros"] == ["erro1"]
    assert data["total_erros"] == 1
    assert data["metricas"]["duracao_segundos"] == 3600 