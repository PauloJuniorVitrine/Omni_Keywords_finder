import pytest
from infrastructure.processamento.utils_keywords import Auditoria, VersionadorRegras
from typing import Dict, List, Optional, Any

def test_auditoria_registrar_log(monkeypatch):
    logs = []
    monkeypatch.setattr("shared.logger.logger.info", lambda value: logs.append(value))
    Auditoria.registrar("evento_teste", {"foo": "bar"})
    assert logs
    assert logs[0]["event"] == "evento_teste"

def test_versionador_registrar_e_historico():
    VersionadorRegras._historico.clear()
    v1 = VersionadorRegras.registrar_versao({"regra": 1})
    v2 = VersionadorRegras.registrar_versao({"regra": 2})
    hist = VersionadorRegras.historico()
    assert len(hist) == 2
    assert hist[0]["versao"] == v1
    assert hist[1]["versao"] == v2 