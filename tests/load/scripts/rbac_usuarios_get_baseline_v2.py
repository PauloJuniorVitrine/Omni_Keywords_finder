from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/rbac/usuarios (GET)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class RbacUsuariosGetUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def get_usuarios(self):
        self.client.get("/api/rbac/usuarios") 