from typing import Dict, List, Optional, Any
"""
Teste de carga threshold para /api/payments/webhook (POST)
Usuários: 100 | Taxa: 10/string_data | Duração: 1min
"""
from locust import HttpUser, task, between
import random
import string

class PaymentsWebhookUser(HttpUser):
    wait_time = between(0.1, 0.2)
    @task
    def post_webhook(self):
        payload = {"event": "payment_received", "payment_id": random.randint(1, 10000), "status": "success"}
        self.client.post("/api/payments/webhook", json=payload) 