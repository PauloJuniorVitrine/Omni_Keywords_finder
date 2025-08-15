import pytest
from infrastructure.processamento.exportador_keywords import ExportadorKeywords
from domain.models import Keyword, IntencaoBusca
from typing import Dict, List, Optional, Any

@pytest.fixture
def exportador():
    return ExportadorKeywords(output_dir="/tmp", idioma="pt")

def test_exportar_keywords_csv_sucesso(tmp_path, exportador):
    dados = [Keyword(termo="exemplo", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL, score=1.0)]
    arquivo = tmp_path / "saida.csv"
    resultado = exportador.exportar_keywords(dados, client="test", niche="test", category="test", filename_prefix="saida", formatos=["csv"])
    assert resultado["status"] in ("success", "warning")

def test_exportar_keywords_csv_entrada_none(exportador):
    resultado = exportador.exportar_keywords(None, client="test", niche="test", category="test", filename_prefix="saida", formatos=["csv"])
    assert resultado["status"] == "empty"

def test_exportar_keywords_csv_erro_io(monkeypatch, exportador):
    def fake_open(*a, **kw): raise IOError("erro de escrita")
    monkeypatch.setattr("builtins.open", fake_open)
    resultado = exportador.exportar_keywords(
        [Keyword(termo="exemplo", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL, score=1.0)],
        client="test", niche="test", category="test", filename_prefix="saida", formatos=["csv"]
    )
    assert resultado["status"] == "error"
    assert any("erro de escrita" in (e.get("erro") or "") for e in resultado.get("erros", [])) 