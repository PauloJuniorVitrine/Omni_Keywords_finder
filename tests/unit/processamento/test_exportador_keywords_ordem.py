import os
import tempfile
import json
import pytest
from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.exportador_keywords import ExportadorKeywords
from typing import Dict, List, Optional, Any

@pytest.fixture
def keywords_cluster():
    # Simula 3 keywords já com ordem e fase_funil
    return [
        Keyword(termo=f"palavra{index+1}", volume_busca=100-index*10, cpc=1.0+index, concorrencia=0.2*index, intencao=IntencaoBusca.INFORMACIONAL, ordem_no_cluster=index, fase_funil=f"FASE{index+1}", nome_artigo=f"Artigo{index+1}")
        for index in range(3)
    ]

def test_exporta_ordem_nome_artigo(tmp_path, keywords_cluster):
    exportador = ExportadorKeywords(output_dir=tmp_path)
    client, niche, category = "ClienteA", "NichoX", "CategoriaY"
    result = exportador.exportar_keywords(keywords_cluster, client, niche, category, formatos=["json"])
    assert result["status"] == "success"
    # Busca arquivo gerado
    arquivos = result["arquivos"]
    assert "json" in arquivos
    with open(arquivos["json"], encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 3
    for index, item in enumerate(data):
        assert item["ordem_no_cluster"] == index
        assert item["nome_artigo"] == f"Artigo{index+1}"
        assert item["fase_funil"] == f"FASE{index+1}" 