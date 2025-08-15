from typing import Dict, List, Optional, Any
"""
Teste de carga para os endpoints /governanca/regras/upload e /governanca/regras/editar.
Cenários positivos e negativos, logging estruturado, parametrização de host e versionamento de logs.
"""
import os
from locust import HttpUser, task, between, events
import random, json, time
from tests.load.utils.logging import log_request

def regras_payload():
    return {
        "score_minimo": round(random.uniform(0.5, 0.9), 2),
        "blacklist": [f"kw_banida_{random.randint(0,99)}" for _ in range(random.randint(1,3))],
        "whitelist": [f"kw_livre_{random.randint(0,99)}" for _ in range(random.randint(1,3))]
    }

class GovernancaRegrasUser(HttpUser):
    wait_time = between(1, 2)
    host = os.environ.get("LOCUST_HOST", "http://127.0.0.1:5000/api")

    @task(2)
    def upload_regras(self):
        with self.client.post("/governanca/regras/upload", json=regras_payload(), catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def editar_regras(self):
        with self.client.post("/governanca/regras/editar", json=regras_payload(), catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def regras_invalido(self):
        # Payload inválido: score_minimo fora do range
        payload = {"score_minimo": 2, "blacklist": [], "whitelist": []}
        with self.client.post("/governanca/regras/upload", json=payload, catch_response=True) as resp:
            if resp.status_code in (400, 422):
                resp.success()
            else:
                resp.failure(f"Esperado 400/422, obtido {resp.status_code}")

@events.request.add_listener
def _log_request(**kwargs):
    log_request(log_prefix="governanca_regras", **kwargs) 