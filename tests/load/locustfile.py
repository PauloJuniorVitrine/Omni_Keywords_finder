from locust import HttpUser, task, between, LoadTestShape, events
import random
import string
import json
import time
from locust.stats import stats_printer, stats_history
from typing import Dict, List, Optional, Any

# Configuração de ramp-up progressivo
class StepLoadShape(LoadTestShape):
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},
        {"duration": 120, "users": 50, "spawn_rate": 5},
        {"duration": 180, "users": 100, "spawn_rate": 10},
        {"duration": 240, "users": 200, "spawn_rate": 20},
        {"duration": 300, "users": 500, "spawn_rate": 50},
    ]
    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None

# Funções utilitárias para geração de payloads

def random_keyword(prefix="test_kw_perf_"):
    return {
        "termo": f"{prefix}{random.randint(0, 99999)}",
        "volume_busca": random.randint(10, 1000),
        "cpc": round(random.uniform(0.1, 10.0), 2),
        "concorrencia": round(random.uniform(0, 1), 2),
        "intencao": random.choice(["informacional", "transacional"])
    }

def keyword_payload(n=10):
    return {
        "keywords": [random_keyword() for _ in range(n)],
        "enriquecer": True,
        "relatorio": True
    }

class OmniUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://127.0.0.1:5000/api"

    @task(5)
    def processar_keywords(self):
        payload = keyword_payload(10)
        with self.client.post("/processar_keywords", json=payload, catch_response=True) as resp:
            if resp.status_code == 200 and "keywords" in resp.json():
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code} | Body: {resp.text}")

    @task(2)
    def exportar_keywords_json(self):
        prefix = "test_kw_"
        with self.client.get(f"/exportar_keywords?formato=json&prefix={prefix}", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(2)
    def exportar_keywords_csv(self):
        prefix = "test_kw_"
        with self.client.get(f"/exportar_keywords?formato=csv&prefix={prefix}", catch_response=True) as resp:
            if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("text/csv"):
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def consultar_logs(self):
        with self.client.get("/governanca/logs", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def upload_regras(self):
        regras = {"score_minimo": 0.7, "blacklist": ["kw_banida"], "whitelist": ["kw_livre"]}
        with self.client.post("/governanca/regras/upload", json=regras, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def editar_regras(self):
        regras = {"score_minimo": 0.8, "blacklist": ["kw_banida2"], "whitelist": ["kw_livre2"]}
        with self.client.post("/governanca/regras/editar", json=regras, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def google_trends(self):
        termo = random_keyword()["termo"]
        with self.client.get(f"/externo/google_trends?termo={termo}", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

    @task(1)
    def reset_ambiente(self):
        with self.client.post("/test/reset", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")

# Logging estruturado dos resultados por requisição
@events.request.add_listener
def log_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    log = {
        "timestamp": time.time(),
        "type": request_type,
        "endpoint": name,
        "status_code": getattr(response, "status_code", None),
        "response_time_ms": response_time,
        "response_length": response_length,
        "exception": str(exception) if exception else None,
        "url": url
    }
    with open("tests/load/locust_results.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")
    # Thresholds automáticos
    if response_time > 800:
        print(f"[ALERTA] Latência alta: {response_time}ms em {name}")
    if getattr(response, "status_code", 200) >= 500:
        print(f"[ALERTA] Erro 5xx em {name}: {getattr(response, 'status_code', None)}")

# Logging de métricas agregadas ao final do teste
@events.quitting.add_listener
def log_summary(environment, **_):
    stats = environment.runner.stats
    summary = {
        "total_requests": stats.total.num_requests,
        "failures": stats.total.num_failures,
        "avg_response_time": stats.total.avg_response_time,
        "rps": stats.total.total_rps,
        "fail_ratio": stats.total.fail_ratio,
        "timestamp": time.time()
    }
    with open("tests/load/locust_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

# Documentação inline
"""
Como executar:

1. Instale o Locust:
   pip install locust

2. Execute:
   locust -f tests/load/locustfile.py

3. Acesse http://localhost:8089 e defina usuários/spawn rate OU use o ramp-up automático.

4. Resultados:
   - Requisições individuais: tests/load/locust_results.jsonl
   - Métricas agregadas: tests/load/locust_summary.json

5. Thresholds automáticos:
   - Latência > 800ms: alerta no console
   - Erro 5xx: alerta no console

6. Versione os arquivos de resultado para análise comparativa.
""" 