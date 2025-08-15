import pytest
import requests
import os
import yaml
from typing import Dict, List, Optional, Any

# Execute sempre em ambiente de teste isolado (.env.test, banco de teste)
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')
PREFIXO_TESTE = 'test_'

@pytest.mark.integration
def test_upload_regras_yaml():
    regras = {
        'score_minimo': 0.7,
        'blacklist': [f'{PREFIXO_TESTE}banido'],
        'whitelist': [f'{PREFIXO_TESTE}livre']
    }
    yaml_regras = yaml.dump(regras, allow_unicode=True)
    files = {'file': ('regras.yaml', yaml_regras, 'application/value-yaml')}
    headers = {"Authorization": "Bearer token_teste"}
    resp = requests.post(f"{API_URL}/governanca/regras/upload", files=files, headers=headers, timeout=15)
    print("DEBUG-RESPONSE:", resp.text)
    print("DEBUG-STATUS:", resp.status_code)
    # assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    # data = resp.json()
    # assert data.get('status') == 'ok', f"Resposta inesperada: {data}"
    # Validar persistência: buscar regras atuais
    # resp2 = requests.get(f"{API_URL}/governanca/regras/atual", timeout=10)
    # assert resp2.status_code == 200
    # regras_atual = resp2.json()
    # assert regras_atual.get('score_minimo') == 0.7
    # assert f'{PREFIXO_TESTE}banido' in regras_atual.get('blacklist', [])
    # (Opcional) Limpeza pós-teste

@pytest.mark.integration
def test_edicao_regras_inline():
    novas_regras = {
        'score_minimo': 0.9,
        'blacklist': [f'{PREFIXO_TESTE}banido2'],
        'whitelist': [f'{PREFIXO_TESTE}livre2']
    }
    resp = requests.post(f"{API_URL}/governanca/regras/editar", json=novas_regras, timeout=10)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    data = resp.json()
    assert data.get('status') == 'ok', f"Resposta inesperada: {data}"
    # (Opcional) Validar efeito no processamento
    # (Opcional) Limpeza pós-teste 