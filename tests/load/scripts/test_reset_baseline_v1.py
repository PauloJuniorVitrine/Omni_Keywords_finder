from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/test/reset (POST)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class TestResetUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def post_test_reset(self):
        self.client.post("/api/test/reset") 