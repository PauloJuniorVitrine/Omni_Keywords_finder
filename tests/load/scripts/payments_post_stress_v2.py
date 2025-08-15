from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/payments/ (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random
import string

class PaymentsPostUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_payment(self):
        payload = {"amount": random.randint(10, 100), "currency": "BRL", "user_id": random.randint(1, 1000)}
        self.client.post("/api/payments/", json=payload) 