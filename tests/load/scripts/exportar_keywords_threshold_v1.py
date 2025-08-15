from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/exportar_keywords (GET)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between

class ExportarKeywordsUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def get_exportar_keywords(self):
        params = {"formato": "json", "prefix": "python_"}
        self.client.get("/api/exportar_keywords", params=params) 