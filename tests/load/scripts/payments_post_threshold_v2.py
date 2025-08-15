from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/payments/ (POST)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between
import random
import string

class PaymentsPostUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def post_payment(self):
        payload = {"amount": random.randint(10, 100), "currency": "BRL", "user_id": random.randint(1, 1000)}
        self.client.post("/api/payments/", json=payload) 