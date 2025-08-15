import time
import pytest
import numpy as np
from unittest.mock import patch
from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.clusterizador_semantico import ClusterizadorSemantico
from infrastructure.processamento.exportador_keywords import ExportadorKeywords
from typing import Dict, List, Optional, Any

@pytest.mark.performance
def test_benchmark_clusterizacao_exportacao_mock(tmp_path):
    # Gera 1.000 keywords sintéticas (reduzido para evitar timeout)
    keywords = [
        Keyword(
            termo=f"palavra_bench_{index}",
            volume_busca=1000-index%100,
            cpc=1.0+(index%10)*0.1,
            concorrencia=(index%10)/10.0,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        for index in range(1000)
    ]
    clusterizador = ClusterizadorSemantico(tamanho_cluster=6, paralelizar=True)

    # Mocka o método _gerar_embeddings para retornar arrays aleatórios
    with patch.object(clusterizador, '_gerar_embeddings', return_value=np.random.rand(len(keywords), 384)):
        t0 = time.time()
        resultado = clusterizador.gerar_clusters(keywords, categoria="BenchCat", blog_dominio="bench.com", formato_retorno="objeto")
        t1 = time.time()
        # Exporta clusters
        exportador = ExportadorKeywords(output_dir=tmp_path)
        for cluster in resultado['clusters']:
            exportador.exportar_keywords(cluster.keywords, "ClienteA", "NichoX", "CategoriaY")
        tempo_total = t1 - t0
        print(f"Tempo total pipeline (mock embeddings): {tempo_total:.2f}string_data, clusters gerados: {len(resultado['clusters'])}")
        assert tempo_total < 30  # Esperado: pipeline rápido com mock
        assert len(resultado['clusters']) > 0 