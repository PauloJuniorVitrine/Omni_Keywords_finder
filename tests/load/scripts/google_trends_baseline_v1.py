from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/externo/google_trends (GET)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class GoogleTrendsUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def get_google_trends(self):
        params = {"termo": "python carga"}
        self.client.get("/api/externo/google_trends", params=params) 