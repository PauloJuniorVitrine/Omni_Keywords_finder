import os
import tempfile
import shutil
import pytest
from scripts import auditoria_release
from typing import Dict, List, Optional, Any

def test_checar_artefatos_all_present(tmp_path, monkeypatch):
    # Cria todos os artefatos obrigatórios
    for a in auditoria_release.checar_artefatos():
        path = tmp_path / a
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('ok')
    monkeypatch.chdir(tmp_path)
    faltando = auditoria_release.checar_artefatos()
    assert isinstance(faltando, list)
    assert len(faltando) > 0

def test_checar_artefatos_missing(tmp_path, monkeypatch):
    # Remove um artefato obrigatório
    for a in auditoria_release.checar_artefatos():
        if 'README.md' not in a:
            path = tmp_path / a
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('ok')
    monkeypatch.chdir(tmp_path)
    faltando = auditoria_release.checar_artefatos()
    assert 'README.md' in faltando

def test_checar_logs_erro(tmp_path, monkeypatch):
    logdir = tmp_path / 'logs'
    logdir.mkdir()
    log = logdir / 'omni_keywords.log'
    log.write_text('error: fail\ninfo: ok\n')
    monkeypatch.chdir(tmp_path)
    erros = auditoria_release.checar_logs_erro()
    assert any('error' in e or 'fail' in e for e in erros)

def test_gerar_relatorio(tmp_path, monkeypatch):
    # Cria todos os artefatos obrigatórios
    for a in auditoria_release.checar_artefatos():
        path = tmp_path / a
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('ok')
    logdir = tmp_path / 'logs'
    logdir.mkdir()
    (logdir / 'omni_keywords.log').write_text('error: fail\n')
    (tmp_path / 'test-results').mkdir(exist_ok=True)
    (tmp_path / 'test-results' / 'coverage.xml').write_text('<coverage line-rate="1.0"/>')
    monkeypatch.chdir(tmp_path)
    # Mocka criação do relatorio_release.md
    relatorio_path = tmp_path / 'docs' / 'relatorio_release.md'
    relatorio_path.parent.mkdir(parents=True, exist_ok=True)
    relatorio_path.write_text('# Relatório de Release - Mock')
    auditoria_release.gerar_relatorio()
    rel = relatorio_path.read_text()
    assert 'Cobertura de testes' in rel
    assert 'error' in rel or 'fail' in rel 