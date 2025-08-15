from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/rbac/usuarios (POST)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between
import random
import string

class RbacUsuariosPostUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def post_usuario(self):
        username = 'user_' + ''.join(random.choices(string.ascii_lowercase, key=8))
        payload = {"username": username, "password": "Test1234!", "email": f"{username}@test.com"}
        self.client.post("/api/rbac/usuarios", json=payload) 