from typing import Dict, List, Optional, Any
"""
Teste de carga baseline para /api/dashboard/metrics (GET)
Usuários: 10 | Taxa: 1/string_data | Duração: 30s
"""
from locust import HttpUser, task, between

class DashboardMetricsUser(HttpUser):
    wait_time = between(1, 2)
    @task
    def get_dashboard_metrics(self):
        self.client.get("/api/dashboard/metrics") 