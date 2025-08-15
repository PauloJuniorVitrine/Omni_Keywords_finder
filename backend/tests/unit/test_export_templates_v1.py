from typing import Dict, List, Optional, Any
"""
Testes unitários para ExportTemplate e ExportadorIncremental (export_templates_v1.py)
"""
import os
import tempfile
from backend.app.services.export_templates_v1 import ExportTemplate, ExportadorIncremental

def test_exportar_csv_e_txt():
    dados = [
        {'a': 1, 'b': 2},
        {'a': 3, 'b': 4},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, 'teste.csv')
        txt_path = os.path.join(tmp, 'teste.txt')
        tpl_csv = ExportTemplate(['a', 'b'], formato='csv')
        tpl_txt = ExportTemplate(['a', 'b'], formato='txt', delimitador='|')
        tpl_csv.exportar(dados, csv_path)
        tpl_txt.exportar(dados, txt_path)
        with open(csv_path) as f:
            linhas = f.readlines()
            assert linhas[0].strip() == 'a,b'
        with open(txt_path) as f:
            linhas = f.readlines()
            assert linhas[0].strip() == '1|2'

def test_exportar_incremental():
    dados = [{'a': 1, 'b': 2}]
    with tempfile.TemporaryDirectory() as tmp:
        tpl = ExportTemplate(['a', 'b'])
        exp = ExportadorIncremental(tmp, tpl)
        arq = exp.exportar_incremental('arq.csv', dados)
        assert arq is not None
        # Segunda chamada sem alteração não exporta
        arq2 = exp.exportar_incremental('arq.csv', dados)
        assert arq2 is None
        # Mudando os dados, exporta novamente
        dados2 = [{'a': 2, 'b': 3}]
        arq3 = exp.exportar_incremental('arq.csv', dados2)
        assert arq3 is not None

def test_exportar_edge_cases():
    dados = []
    with tempfile.TemporaryDirectory() as tmp:
        tpl = ExportTemplate(['a', 'b'])
        exp = ExportadorIncremental(tmp, tpl)
        arq = exp.exportar_incremental('vazio.csv', dados)
        assert arq is not None 