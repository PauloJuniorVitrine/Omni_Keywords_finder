from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/execucoes/ (POST)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random

class ExecucoesUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def post_execucoes(self):
        payload = {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1"}
        self.client.post("/api/execucoes/", json=payload) 