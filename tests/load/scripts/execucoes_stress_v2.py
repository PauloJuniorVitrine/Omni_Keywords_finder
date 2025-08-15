from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/execucoes/ (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random

class ExecucoesUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_execucoes(self):
        payload = {"categoria_id": 1, "palavras_chave": ["python", "locust", "stress"], "cluster": "cluster1"}
        self.client.post("/api/execucoes/", json=payload) 