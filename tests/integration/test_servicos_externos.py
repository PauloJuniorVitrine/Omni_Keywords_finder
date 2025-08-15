import pytest
import requests
import os
from typing import Dict, List, Optional, Any

# Execute sempre em ambiente de teste isolado (.env.test, banco de teste)
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')
PREFIXO_TESTE = 'test_kw_trends'

@pytest.mark.integration
def test_google_trends_integra():
    termo = PREFIXO_TESTE
    resp = requests.get(f"{API_URL}/externo/google_trends", params={"termo": termo}, timeout=15)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    data = resp.json()
    assert "termo" in data and data["termo"] == termo, "Campo 'termo' ausente ou divergente"
    assert "volume" in data, "Campo 'volume' ausente"
    # (Opcional) Validar fallback e logs
    # (Opcional) Limpeza pós-teste 