from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/rbac/usuarios (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random
import string

class RbacUsuariosPostUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_usuario(self):
        username = 'user_' + ''.join(random.choices(string.ascii_lowercase, key=10))
        payload = {"username": username, "password": "Test1234!", "email": f"{username}@test.com"}
        self.client.post("/api/rbac/usuarios", json=payload) 