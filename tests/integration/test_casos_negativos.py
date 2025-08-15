import pytest
import requests
import os
from typing import Dict, List, Optional, Any

# Execute sempre em ambiente de teste isolado (.env.test, banco de teste)
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')

@pytest.mark.integration
def test_autenticacao_invalida():
    # Simula token inválido (ajuste conforme autenticação real)
    headers = {"Authorization": "Bearer token_invalido"}
    resp = requests.get(f"{API_URL}/governanca/logs?event=validacao_keywords", headers=headers, timeout=10)
    assert resp.status_code == 401, f"Status inesperado: {resp.status_code}"
    # (Opcional) Limpeza pós-teste

@pytest.mark.integration
def test_dados_invalidos():
    payload = {"keywords": "string_ao_inves_de_lista"}
    resp = requests.post(f"{API_URL}/processar_keywords", json=payload, timeout=10)
    assert resp.status_code in (400, 422), f"Status inesperado: {resp.status_code}"
    data = resp.json()
    assert "erro" in data or "detail" in data, "Mensagem de erro não encontrada"
    # (Opcional) Limpeza pós-teste

@pytest.mark.integration
def test_timeout():
    # Simula timeout reduzindo drasticamente o tempo limite
    try:
        requests.get(f"{API_URL}/test/timeout", timeout=0.01)
        assert False, "Deveria lançar timeout"
    except requests.exceptions.Timeout:
        assert True
    # (Opcional) Limpeza pós-teste 