from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/execucoes/lote (POST)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between
import random

class ExecucoesLoteUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def post_execucoes_lote(self):
        payload = {"categoria_id": 1, "lote": [["python", "locust", "threshold"]], "cluster": "cluster1"}
        self.client.post("/api/execucoes/lote", json=payload) 