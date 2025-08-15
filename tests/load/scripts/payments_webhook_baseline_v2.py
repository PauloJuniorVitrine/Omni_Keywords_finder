from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/payments/webhook (POST)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between
import random
import string

class PaymentsWebhookUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def post_webhook(self):
        payload = {"event": "payment_received", "payment_id": random.randint(1, 10000), "status": "success"}
        self.client.post("/api/payments/webhook", json=payload) 