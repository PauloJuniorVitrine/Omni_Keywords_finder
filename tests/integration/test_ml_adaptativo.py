import pytest
import requests
import os
from typing import Dict, List, Optional, Any

# Execute sempre em ambiente de teste isolado (.env.test, banco de teste)
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')
PREFIXO_TESTE = 'test_kw_ml_'

@pytest.mark.integration
def test_ml_adaptativo_sucesso():
    payload = {
        "keywords": [
            {"termo": f"{PREFIXO_TESTE}1", "volume_busca": 100, "cpc": 1.0, "concorrencia": 0.3, "intencao": "informacional"},
            {"termo": f"{PREFIXO_TESTE}2", "volume_busca": 200, "cpc": 2.0, "concorrencia": 0.6, "intencao": "transacional"}
        ],
        "ml_adaptativo": True,
        "relatorio": True
    }
    resp = requests.post(f"{API_URL}/processar_keywords", json=payload, timeout=20)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    data = resp.json()
    assert "keywords" in data, "Campo 'keywords' ausente na resposta"
    assert any(kw["termo"].startswith(PREFIXO_TESTE) for kw in data["keywords"]), "Nenhuma keyword de teste ML encontrada"
    assert "relatorio" in data
    # (Opcional) Validar logs e efeitos colaterais do ML
    # (Opcional) Limpeza pós-teste 