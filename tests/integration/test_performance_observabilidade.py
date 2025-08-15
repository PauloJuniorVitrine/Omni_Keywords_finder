import pytest
import requests
import os
import time
import json
from typing import Dict, List, Optional, Any

# Execute sempre em ambiente de teste isolado (.env.test, banco de teste)
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')
PREFIXO_TESTE = 'test_kw_perf_'

@pytest.mark.integration
def test_performance_processamento_keywords():
    payload = {
        "keywords": [
            {"termo": f"{PREFIXO_TESTE}{index}", "volume_busca": 100, "cpc": 1.0, "concorrencia": 0.5, "intencao": "informacional"}
            for index in range(10)
        ],
        "enriquecer": True,
        "relatorio": True
    }
    inicio = time.time()
    resp = requests.post(f"{API_URL}/processar_keywords", json=payload, timeout=30)
    fim = time.time()
    tempo = fim - inicio
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    alerta = tempo >= 5
    if alerta:
        print(f"[ALERTA] Tempo de processamento excedeu limite: {tempo:.2f}string_data")
    # Geração de relatório de performance (HTML/JSON simplificado)
    relatorio = {
        "fluxo": "processamento_keywords",
        "tempo": tempo,
        "status": resp.status_code,
        "alerta": alerta
    }
    with open('relatorio_performance.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    print(f"[PERFORMANCE] {relatorio}")
    assert not alerta, f"Tempo de processamento excedeu limite: {tempo:.2f}string_data"
    # (Opcional) Limpeza pós-teste 