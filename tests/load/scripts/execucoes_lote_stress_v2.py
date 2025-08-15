from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/execucoes/lote (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random

class ExecucoesLoteUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_execucoes_lote(self):
        payload = {"categoria_id": 1, "lote": [["python", "locust", "stress"]], "cluster": "cluster1"}
        self.client.post("/api/execucoes/lote", json=payload) 