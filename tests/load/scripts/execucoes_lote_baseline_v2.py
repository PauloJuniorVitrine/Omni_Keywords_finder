from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/execucoes/lote (POST)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random

class ExecucoesLoteUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def post_execucoes_lote(self):
        payload = {"categoria_id": 1, "lote": [["python", "locust"]], "cluster": "cluster1"}
        self.client.post("/api/execucoes/lote", json=payload) 