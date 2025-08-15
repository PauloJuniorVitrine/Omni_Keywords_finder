from typing import Dict, List, Optional, Any
"""
Teste de carga para o endpoint /processar_keywords.
Cenários positivos e negativos, logging estruturado, parametrização de host e versionamento de logs.
"""
import os
from locust import HttpUser, task, between, events
import random, json, time
from tests.load.utils.logging import log_request

def random_keyword(prefix="test_kw_perf_"):
    return {
        "termo": f"{prefix}{random.randint(0, 99999)}",
        "volume_busca": random.randint(10, 1000),
        "cpc": round(random.uniform(0.1, 10.0), 2),
        "concorrencia": round(random.uniform(0, 1), 2),
        "intencao": random.choice(["informacional", "transacional"])
    }

def keyword_payload(n=10):
    return {
        "keywords": [random_keyword() for _ in range(n)],
        "enriquecer": True,
        "relatorio": True
    }

class ProcessarKeywordsUser(HttpUser):
    wait_time = between(1, 2)
    host = os.environ.get("LOCUST_HOST", "http://127.0.0.1:5000/api")

    @task(3)
    def processar_keywords(self):
        payload = keyword_payload(10)
        with self.client.post("/processar_keywords", json=payload, catch_response=True) as resp:
            if resp.status_code == 200 and "keywords" in resp.json():
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code} | Body: {resp.text}")

    @task(1)
    def processar_keywords_invalido(self):
        # Payload inválido: campo faltando
        payload = {"keywords": []}
        with self.client.post("/processar_keywords", json=payload, catch_response=True) as resp:
            if resp.status_code == 400:
                resp.success()
            else:
                resp.failure(f"Esperado 400, obtido {resp.status_code}")

@events.request.add_listener
def _log_request(**kwargs):
    log_request(log_prefix="processar_keywords", **kwargs) 