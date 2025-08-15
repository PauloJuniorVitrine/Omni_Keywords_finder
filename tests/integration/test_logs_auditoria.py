import pytest
import requests
import os
import time
from typing import Dict, List, Optional, Any

# Execute sempre em ambiente de teste isolado (.env.test, banco de teste)
API_URL = os.getenv('API_URL', 'http://localhost:5000/api')

@pytest.mark.integration
def test_consulta_logs_sucesso():
    params = {"page": 1, "page_size": 10, "event": "validacao_keywords"}
    headers = {"Authorization": "Bearer token_teste"}
    resp = requests.get(f"{API_URL}/governanca/logs", params=params, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    data = resp.json()
    assert "logs" in data, "Campo 'logs' ausente na resposta"
    assert isinstance(data["logs"], list), "Logs não é uma lista"
    for log in data["logs"]:
        assert isinstance(log, dict), "Log não é um dicionário"
        assert "timestamp" in log
        assert "event" in log
        assert "status" in log
        assert "details" in log
    # Validação de logs estruturados: buscar logs recentes e validar evento
    time.sleep(0.5)
    logs_audit = requests.get(f"{API_URL}/governanca/logs", params={"page": 1, "page_size": 5, "event": "validacao_keywords"}, headers=headers, timeout=5).json()["logs"]
    eventos = [log["event"] for log in logs_audit]
    assert any(ev in eventos for ev in ["validacao_keywords", "limpeza_keywords", "erro_enriquecimento"]), "Evento esperado não encontrado nos logs recentes"
    print(f"[LOGS AUDIT] Eventos recentes: {eventos}")
    # (Opcional) Limpeza pós-teste

@pytest.mark.integration
def test_consulta_logs_filtro_negativo():
    params = {"page": 1, "page_size": 10, "event": "evento_inexistente"}
    headers = {"Authorization": "Bearer token_teste"}
    resp = requests.get(f"{API_URL}/governanca/logs", params=params, headers=headers, timeout=10)
    assert resp.status_code == 200, f"Status inesperado: {resp.status_code}"
    data = resp.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)
    assert len(data["logs"]) == 0
    # (Opcional) Limpeza pós-teste 