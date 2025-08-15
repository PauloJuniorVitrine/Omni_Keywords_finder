from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/execucoes/ (POST)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between
import random

class ExecucoesUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def post_execucoes(self):
        payload = {"categoria_id": 1, "palavras_chave": ["python", "locust"], "cluster": "cluster1"}
        self.client.post("/api/execucoes/", json=payload) 