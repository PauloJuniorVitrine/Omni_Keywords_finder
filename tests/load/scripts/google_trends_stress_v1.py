from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/externo/google_trends (GET)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class GoogleTrendsUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def get_google_trends(self):
        params = {"termo": "python carga"}
        self.client.get("/api/externo/google_trends", params=params) 