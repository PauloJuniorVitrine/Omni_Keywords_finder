from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/test/reset (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class TestResetUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_test_reset(self):
        self.client.post("/api/test/reset") 