from typing import Dict, List, Optional, Any
"""
Teste de carga stress para /api/payments/webhook (POST)
Usuários: 400 | Taxa: 40/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random
import string

class PaymentsWebhookUser(HttpUser):
    wait_time = between(0.01, 0.05)
    @task
    def post_webhook(self):
        payload = {"event": "payment_received", "payment_id": random.randint(1, 10000), "status": "success"}
        self.client.post("/api/payments/webhook", json=payload) 