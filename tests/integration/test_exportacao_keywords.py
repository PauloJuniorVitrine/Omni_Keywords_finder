import pytest
import requests
import os
from typing import Dict, List, Optional, Any

# Execute sempre em ambiente de teste isolado (.env.test, banco de teste)
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')
PREFIXO_TESTE = 'test_kw_'

@pytest.mark.integration
def test_exportacao_keywords_csv():
    # Pré-condição: keywords de teste já processadas (use prefixo exclusivo)
    params = {"formato": "csv", "prefix": PREFIXO_TESTE}
    resp = requests.get(f"{API_URL}/exportar_keywords", params=params, timeout=15)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    assert resp.headers['Content-Type'].startswith('text/csv')
    content = resp.text
    assert PREFIXO_TESTE in content, "Prefixo de teste não encontrado no CSV"
    assert 'termo' in content, "Campo 'termo' ausente no CSV"
    # (Opcional) Limpeza pós-teste: remover arquivos/dados criados

@pytest.mark.integration
def test_exportacao_keywords_json():
    params = {"formato": "json", "prefix": PREFIXO_TESTE}
    resp = requests.get(f"{API_URL}/exportar_keywords", params=params, timeout=15)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    assert resp.headers['Content-Type'].startswith('application/json')
    data = resp.json()
    assert isinstance(data, list), "Resposta JSON não é uma lista"
    assert any(kw['termo'].startswith(PREFIXO_TESTE) for kw in data), "Nenhuma keyword de teste encontrada"
    # (Opcional) Limpeza pós-teste 