from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/execucoes/agendadas (GET)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between

class ExecucoesAgendadasGetUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def get_execucoes_agendadas(self):
        self.client.get("/api/execucoes/agendadas") 