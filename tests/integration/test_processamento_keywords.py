import pytest
import requests
import os
import time
from typing import Dict, List, Optional, Any

API_URL = os.getenv('API_URL', 'http://localhost:5000/api')

@pytest.fixture(scope='function', autouse=True)
def limpar_dados():
    # Recomendado: execute sempre em ambiente de teste isolado (.env.test, banco de teste)
    # Se houver endpoint de limpeza/reset, utilize aqui para remover dados criados
    yield
    # Limpeza pós-teste (opcional): buscar e remover keywords criadas com prefixo 'test_kw_'
    # Exemplo:
    # requests.post(f"{API_URL}/test/reset_keywords", json={"prefix": "test_kw_"})

@pytest.mark.integration
def test_processamento_keywords_sucesso():
    payload = {
        "keywords": [
            {"termo": "test_kw_python", "volume_busca": 1000, "cpc": 2.5, "concorrencia": 0.7, "intencao": "informacional"},
            {"termo": "test_kw_pytest", "volume_busca": 500, "cpc": 1.2, "concorrencia": 0.5, "intencao": "transacional"}
        ],
        "enriquecer": True,
        "relatorio": True
    }
    resp = requests.post(f"{API_URL}/processar_keywords", json=payload, timeout=15)
    assert resp.status_code == 200
    data = resp.json()
    assert "keywords" in data
    assert len(data["keywords"]) == 2
    for kw in data["keywords"]:
        assert kw["termo"].startswith("test_kw_")
        assert "score" in kw
    assert "relatorio" in data
    # (Opcional) Após o teste, buscar e remover keywords criadas, se a API permitir

@pytest.mark.integration
def test_processamento_keywords_invalido():
    payload = {
        "keywords": [
            {"termo": "", "volume_busca": -1, "cpc": -2, "concorrencia": 2, "intencao": ""}
        ],
        "enriquecer": True,
        "relatorio": True
    }
    resp = requests.post(f"{API_URL}/processar_keywords", json=payload, timeout=15)
    assert resp.status_code == 400 or resp.status_code == 422
    data = resp.json()
    assert "erro" in data or "detail" in data 