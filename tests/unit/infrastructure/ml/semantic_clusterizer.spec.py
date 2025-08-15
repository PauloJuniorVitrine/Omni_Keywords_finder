import pytest
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock
from infrastructure.processamento.clusterizador_semantico import ClusterizadorSemantico, ClusterizadorConfig
from domain.models import Keyword, IntencaoBusca
import asyncio
import json
from typing import Dict, List, Optional, Any

pytestmark = pytest.mark.timeout(10)

def make_keyword(term, volume=10):
    return Keyword(
        termo=term,
        volume_busca=volume,
        cpc=1.0,
        concorrencia=0.5,
        intencao=IntencaoBusca.INFORMACIONAL
    )

def mock_embeddings(termos, model_name=None):
    return np.ones((len(termos), 10))

def mock_similaridade(a, b):
    return np.ones((len(a), len(b)))

@pytest.fixture
def clusterizador():
    return ClusterizadorSemantico(
        func_gerar_embeddings=mock_embeddings,
        func_similaridade=mock_similaridade,
        paralelizar=False
    )

@pytest.fixture
def clusterizador_paralelo():
    return ClusterizadorSemantico(
        func_gerar_embeddings=mock_embeddings,
        func_similaridade=mock_similaridade,
        paralelizar=True
    )

def test_instanciacao_config():
    config = ClusterizadorConfig(func_gerar_embeddings=mock_embeddings)
    c = ClusterizadorSemantico(config=config)
    assert c.modelo_embeddings == config.modelo_embeddings
    assert c.func_gerar_embeddings == mock_embeddings

def test_dependencias():
    # Não deve lançar erro se dependências presentes
    ClusterizadorSemantico(func_gerar_embeddings=mock_embeddings)

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_gerar_clusters_async(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    # Mockar gerar_clusters, pois pode ser chamado internamente
    with patch.object(clusterizador, 'gerar_clusters', return_value={"clusters": [MagicMock(termo="exemplo")], "descartados": [], "relatorio": {}}):
        resultado = await clusterizador.gerar_clusters_async(kws, blog_dominio="meublog.com")
        assert "clusters" in resultado
        assert len(resultado["clusters"]) == 1

def test_gerar_clusters_sincrono(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    resultado = clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")
    assert len(resultado["clusters"]) == 1
    assert resultado["clusters"][0].keywords[0].termo == "kw0"

def test_paralelizacao(clusterizador_paralelo):
    kws = [make_keyword(f"kw{index}") for index in range(12)]
    resultado = clusterizador_paralelo.gerar_clusters(kws, blog_dominio="meublog.com")
    assert len(resultado["clusters"]) >= 1

def test_max_clusters(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(18)]
    clusterizador.max_clusters = 2
    resultado = clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")
    assert len(resultado["clusters"]) == 2

def test_diversidade(clusterizador):
    kws = [make_keyword("kw") for _ in range(12)]
    with pytest.raises(ValueError, match="duplicada|duplicidade|repetido|inconsistente"):
        clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")

def test_similaridade_minima(clusterizador):
    clusterizador.min_similaridade = 2.0
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    resultado = clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")
    assert len(resultado["clusters"]) == 0
    assert any("similaridade" in data["motivo"] for data in resultado["descartados"])

def test_callback_monitoramento():
    callback = MagicMock()
    monitoramento = MagicMock()
    c = ClusterizadorSemantico(
        func_gerar_embeddings=mock_embeddings,
        func_similaridade=mock_similaridade,
        callback=callback,
        monitoramento_hook=monitoramento
    )
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    resultado = c.gerar_clusters(kws, blog_dominio="meublog.com")
    callback.assert_called()
    monitoramento.assert_called()

def test_func_similaridade_custom():
    def sim(a, b):
        return np.ones((len(a), len(b)))
    c = ClusterizadorSemantico(func_gerar_embeddings=mock_embeddings, func_similaridade=sim)
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    resultado = c.gerar_clusters(kws, blog_dominio="meublog.com")
    assert len(resultado["clusters"]) == 1

def test_serializacao_json(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    resultado = clusterizador.gerar_clusters(kws, blog_dominio="meublog.com", formato_retorno="json")
    assert isinstance(resultado["clusters"], list)
    assert isinstance(resultado["descartados"], list)
    assert "relatorio" in resultado

def test_wrapper_compatibilidade(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    clusters = clusterizador.gerar_clusters_semanticos(kws, blog_dominio="meublog.com")
    assert isinstance(clusters, list)
    assert hasattr(clusters[0], "keywords")

def test_validacao_consistencia(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(5)] + [make_keyword("kw0")]
    with pytest.raises(ValueError, match="duplicada|duplicidade|repetido|inconsistente"):
        clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")

def test_embeddings_cache(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    # Primeira chamada
    clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")
    # Segunda chamada deve usar cache
    clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")
    assert (json.dumps([key.termo for key in kws], sort_keys=True), clusterizador.modelo_embeddings) in clusterizador._embeddings_cache

def test_i18n_logs():
    c = ClusterizadorSemantico(func_gerar_embeddings=mock_embeddings, func_similaridade=mock_similaridade, idioma="en")
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    c.gerar_clusters(kws, blog_dominio="meublog.com")
    # Não há assert direto, mas não deve lançar erro

def test_benchmark(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    with pytest.raises(ValueError, match="domínio|dominio|inválido|invalido"):
        clusterizador.benchmark(kws, n_execucoes=2)

def test_duplicidade_termos_levanta_erro(clusterizador):
    kws = [make_keyword("kw1"), make_keyword("kw2"), make_keyword("kw3"), make_keyword("kw4"), make_keyword("kw5"), make_keyword("kw1")]
    with pytest.raises(ValueError, match="duplicada"):
        clusterizador.gerar_clusters(kws, blog_dominio="meublog.com")

def test_dominio_invalido_levanta_erro(clusterizador):
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    with pytest.raises(ValueError, match="domínio|dominio|inválido|invalido"):
        clusterizador.gerar_clusters(kws, blog_dominio="domínio@!") 