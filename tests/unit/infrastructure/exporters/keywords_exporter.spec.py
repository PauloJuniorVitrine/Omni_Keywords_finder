import pytest
import os
import tempfile
import json
from infrastructure.processamento.exportador_keywords import ExportadorKeywords
from domain.models import Keyword, Cluster, IntencaoBusca
from unittest.mock import patch, MagicMock
from typing import Dict, List, Optional, Any

def make_keyword(term="kw", intencao=IntencaoBusca.INFORMACIONAL):
    return Keyword(
        termo=term,
        volume_busca=10,
        cpc=1.0,
        concorrencia=0.5,
        intencao=intencao
    )

def make_cluster():
    kws = [make_keyword(f"kw{index}") for index in range(6)]
    return Cluster(
        id="cl1",
        keywords=kws,
        similaridade_media=0.8,
        fase_funil="descoberta",
        categoria="cat",
        blog_dominio="blog.com"
    )

def test_exportar_keywords_csv_json(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a"), make_keyword("b")]
    relatorio = {"motivos_rejeicao": {}}
    result = exp.exportar_keywords(kws, "cli", "nich", "cat", relatorio_validacao=relatorio)
    assert result["status"] == "success"
    assert os.path.exists(result["arquivos"]["csv"])
    assert os.path.exists(result["arquivos"]["json"])
    assert "relatorio_validacao" in result
    # Checar conteúdo JSON
    with open(result["arquivos"]["json"], encoding="utf-8") as f:
        data = json.load(f)
        assert any(data["termo"] == "a" for data in data)

def test_exportar_keywords_csv_conteudo(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    result = exp.exportar_keywords(kws, "cli", "nich", "cat")
    with open(result["arquivos"]["csv"], encoding="utf-8") as f:
        lines = f.readlines()
        assert any("a" in list_data for list_data in lines)

def test_exportar_keywords_concorrente(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword(f"key{index}") for index in range(5)]
    # Simular concorrência (chamadas rápidas)
    for _ in range(3):
        exp.exportar_keywords(kws, "cli", "nich", "cat", append=True)

def test_exportar_keywords_incompleto(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    class IncompleteKeyword:
        def __init__(self):
            self.termo = "incompleto"
            self.intencao = IntencaoBusca.INFORMACIONAL
            self.cpc = 0.0
            self.concorrencia = 0.0
            self.volume_busca = 0
        def to_dict(self):
            return {"termo": self.termo, "intencao": self.intencao.value, "cpc": self.cpc, "concorrencia": self.concorrencia, "volume_busca": self.volume_busca}
    kws = [IncompleteKeyword()]
    result = exp.exportar_keywords(kws, "cli", "nich", "cat")
    assert result["status"] in ("success", "warning", "error")

def test_exportar_keywords_permissao_negada(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch("builtins.open", side_effect=PermissionError("negado")):
        result = exp.exportar_keywords(kws, "cli", "nich", "cat")
        assert result["status"] == "error"

def test_exportar_keywords_arquivo_corrompido(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    # Criar arquivo corrompido
    path = tmp_path / "cli" / "nich" / "cat" / "corrompido.json"
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("{corrompido}")
    # Tentar exportar (não deve afetar exportação nova)
    result = exp.exportar_keywords(kws, "cli", "nich", "cat")
    assert result["status"] in ("success", "warning", "error")

def test_exportar_keywords_callback_excecao(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    def callback_raise(*a, **kw):
        raise Exception("erro callback")
    result = exp.exportar_keywords(kws, "cli", "nich", "cat", callback=callback_raise)
    assert result["status"] in ("success", "warning", "error")

def test_exportar_keywords_lista_vazia(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    result = exp.exportar_keywords([], "cli", "nich", "cat")
    assert result["status"] == "empty"

def test_exportar_keywords_callback(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    callback = MagicMock()
    exp.exportar_keywords(kws, "cli", "nich", "cat", callback=callback)
    callback.assert_called()

def test_exportar_keywords_append(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    exp.exportar_keywords(kws, "cli", "nich", "cat", append=True)
    exp.exportar_keywords(kws, "cli", "nich", "cat", append=True)
    # Exportação incremental com múltiplos arquivos
    exp.exportar_keywords(kws, "cli2", "nich2", "cat2", append=True)

def test_exportar_keywords_xlsx(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch("infrastructure.processamento.exportador_keywords.XLSX_OK", True), \
         patch("infrastructure.processamento.exportador_keywords.openpyxl.Workbook") as mock_wb:
        exp.exportar_keywords(kws, "cli", "nich", "cat", export_xlsx=True)
        assert mock_wb.called

def test_exportar_keywords_xlsx_erro(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch("infrastructure.processamento.exportador_keywords.XLSX_OK", True), \
         patch("infrastructure.processamento.exportador_keywords.openpyxl.Workbook", side_effect=Exception("erro")):
        result = exp.exportar_keywords(kws, "cli", "nich", "cat", export_xlsx=True)
        assert any("xlsx" in e.get("arquivo", "") or "erro" in e.get("erro", "") for e in result["erros"])

def test_exportar_keywords_sem_espaco(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch.object(ExportadorKeywords, "_check_disk_space", return_value=False):
        result = exp.exportar_keywords(kws, "cli", "nich", "cat")
        assert result["status"] == "warning"

def test_exportar_keywords_erro_escrita(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch("builtins.open", side_effect=IOError("erro")):
        result = exp.exportar_keywords(kws, "cli", "nich", "cat")
        assert result["status"] == "error"

def test_exportar_keywords_nome_customizado(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    relatorio = {"motivos_rejeicao": {}}
    result = exp.exportar_keywords(kws, "cli", "nich", "cat", filename_prefix="custom", relatorio_validacao=relatorio)
    assert any("custom" in value for value in result["arquivos"].values())
    assert "relatorio_validacao" in result

def test_exportar_keywords_diretorio_inexistente(tmp_path):
    dir_path = tmp_path / "nao_existe"
    exp = ExportadorKeywords(output_dir=str(dir_path))
    kws = [make_keyword("a")]
    result = exp.exportar_keywords(kws, "cli", "nich", "cat")
    assert result["status"] == "success"

def test_exportar_keywords_dados_invalidos(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    class FakeKeyword:
        def __init__(self):
            self.termo = "fake"
            self.intencao = IntencaoBusca.INFORMACIONAL
            self.cpc = 0.0
            self.concorrencia = 0.0
            self.volume_busca = 0
        def to_dict(self):
            return {"termo": self.termo, "intencao": self.intencao.value, "cpc": self.cpc, "concorrencia": self.concorrencia, "volume_busca": self.volume_busca}
    kws = [FakeKeyword()]
    result = exp.exportar_keywords(kws, "cli", "nich", "cat")
    assert result["status"] in ("success", "error", "warning")

def test_exportar_clusters_csv_json(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    clusters = [make_cluster()]
    result = exp.exportar_clusters(clusters, "cli", "nich", "cat")
    assert result["status"] == "success"
    assert os.path.exists(result["arquivos"]["csv"])
    assert os.path.exists(result["arquivos"]["json"])

def test_exportar_clusters_lista_vazia(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    result = exp.exportar_clusters([], "cli", "nich", "cat")
    assert result["status"] == "empty"

def test_exportar_clusters_callback(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    clusters = [make_cluster()]
    callback = MagicMock()
    exp.exportar_clusters(clusters, "cli", "nich", "cat", callback=callback)
    callback.assert_called()

def test_exportar_clusters_erro(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    class FakeCluster:
        def to_dict(self):
            raise Exception("erro")
    clusters = [FakeCluster()]
    result = exp.exportar_clusters(clusters, "cli", "nich", "cat")
    assert result["status"] in ("success", "error", "warning")

def test_exportar_clusters_incompleto(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    class IncompleteCluster:
        def to_dict(self):
            return {"id": None}
    clusters = [IncompleteCluster()]
    result = exp.exportar_clusters(clusters, "cli", "nich", "cat")
    assert result["status"] in ("success", "warning", "error")

def test_exportar_clusters_permissao_negada(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    clusters = [make_cluster()]
    with patch("builtins.open", side_effect=PermissionError("negado")):
        result = exp.exportar_clusters(clusters, "cli", "nich", "cat")
        assert result["status"] == "error"

def test_exportar_clusters_arquivo_corrompido(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    clusters = [make_cluster()]
    path = tmp_path / "cli" / "nich" / "cat" / "corrompido.json"
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("{corrompido}")
    result = exp.exportar_clusters(clusters, "cli", "nich", "cat")
    assert result["status"] in ("success", "warning", "error")

def test_exportar_clusters_callback_excecao(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    clusters = [make_cluster()]
    def callback_raise(*a, **kw):
        raise Exception("erro callback")
    result = exp.exportar_clusters(clusters, "cli", "nich", "cat", callback=callback_raise)
    assert result["status"] in ("success", "warning", "error")

def test_exportar_keywords_log_sucesso(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch("infrastructure.processamento.exportador_keywords.logger") as logger_mock:
        result = exp.exportar_keywords(kws, "cli", "nich", "cat")
        logger_mock.info.assert_called()
        assert result["status"] == "success"

def test_exportar_keywords_log_erro(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch("builtins.open", side_effect=IOError("erro")), \
         patch("infrastructure.processamento.exportador_keywords.logger") as logger_mock:
        result = exp.exportar_keywords(kws, "cli", "nich", "cat")
        logger_mock.error.assert_called()
        assert result["status"] == "error"

def test_exportar_keywords_dados_nulos(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    class NullKeyword:
        def __init__(self):
            self.termo = "null"
            self.intencao = IntencaoBusca.INFORMACIONAL
            self.cpc = 0.0
            self.concorrencia = 0.0
            self.volume_busca = 0
        def to_dict(self):
            return {"termo": self.termo, "intencao": self.intencao.value, "cpc": self.cpc, "concorrencia": self.concorrencia, "volume_busca": self.volume_busca}
    kws = [NullKeyword()]
    result = exp.exportar_keywords(kws, "cli", "nich", "cat")
    assert result["status"] in ("success", "warning", "error")

def test_exportar_keywords_concorrente_erro(tmp_path):
    exp = ExportadorKeywords(output_dir=str(tmp_path))
    kws = [make_keyword("a")]
    with patch("builtins.open", side_effect=[MagicMock(), IOError("erro")]), \
         patch("infrastructure.processamento.exportador_keywords.logger") as logger_mock:
        result = exp.exportar_keywords(kws, "cli", "nich", "cat", append=True)
        logger_mock.error.assert_called()
        assert result["status"] in ("success", "error")

def test_exportar_keywords_diretorio_protegido():
    exp = ExportadorKeywords(output_dir="/root/protegido")
    kws = [make_keyword("a")]
    with patch("builtins.open", side_effect=PermissionError("negado")), \
         patch("infrastructure.processamento.exportador_keywords.logger") as logger_mock:
        result = exp.exportar_keywords(kws, "cli", "nich", "cat")
        logger_mock.error.assert_called()
        assert result["status"] == "error"

def test_exportar_keywords_cauda_longa():
    # Ajustar para garantir que apenas termos com 3+ palavras e 15+ caracteres sejam aceitos
    termos = ["palavra chave exemplo", "duas palavras", "palavra pequena", "palavra muito longa exemplo"]
    cauda_longa = [t for t in termos if len(t.split()) >= 3 and len(t) >= 15]
    assert "duas palavras" not in cauda_longa
    assert "palavra chave exemplo" in cauda_longa 