from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/execucoes/agendadas (POST)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random

class ExecucoesAgendadasUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def post_execucoes_agendadas(self):
        payload = {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1", "horario": "2025-01-01T00:00:00Z"}
        self.client.post("/api/execucoes/agendadas", json=payload) 