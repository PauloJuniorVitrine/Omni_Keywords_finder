"""
locustfile_integration_google_keywords_v1.py
Teste de carga para os endpoints de integração Google Keywords

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_INTEGRATION_GOOGLE_KEYWORDS_20250127_001

Endpoints testados:
- POST /api/integrations/google/keywords/search - Busca de keywords
- GET /api/integrations/google/keywords/volume - Análise de volume
- GET /api/integrations/google/keywords/cpc - Análise de CPC
- GET /api/integrations/google/keywords/competition - Análise de concorrência
- POST /api/integrations/google/keywords/analyze - Análise completa

Cenários:
- Busca de keywords via Google Ads API
- Análise de métricas (volume, CPC, concorrência)
- Rate limiting e circuit breaker
- Fallback para web scraping
"""

from locust import HttpUser, TaskSet, task, between, events
import json
import time
import random
from typing import Dict, Any

TRACING_ID = "LOAD_INTEGRATION_GOOGLE_KEYWORDS_20250127_001"

class GoogleKeywordsIntegrationTasks(TaskSet):
    """Tarefas de teste de carga para integração Google Keywords"""
    
    def on_start(self):
        """Inicialização das tarefas"""
        self.tracing_id = TRACING_ID
        self.auth_token = None
        self.test_keywords = [
            "marketing digital",
            "seo optimization", 
            "content marketing",
            "social media",
            "email marketing",
            "influencer marketing",
            "video marketing",
            "affiliate marketing",
            "ppc advertising",
            "conversion optimization"
        ]
        self.test_locations = [
            "Brazil",
            "United States", 
            "United Kingdom",
            "Canada",
            "Australia"
        ]
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "X-Tracing-ID": self.tracing_id,
            "User-Agent": "OmniKeywordsBot/1.0"
        }
    
    @task(5)
    def test_google_keywords_search(self):
        """Testa busca de keywords Google"""
        try:
            keyword = random.choice(self.test_keywords)
            
            search_data = {
                "keyword": keyword,
                "language": "pt",
                "location": random.choice(self.test_locations),
                "max_results": random.randint(10, 100),
                "include_related": True,
                "include_competition": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.post(
                "/api/integrations/google/keywords/search",
                json=search_data,
                headers=self.headers,
                catch_response=True,
                name="Google Keywords Search"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "keywords" in data and isinstance(data["keywords"], list):
                        response.success()
                        # Valida estrutura dos dados
                        for kw in data["keywords"][:5]:  # Valida primeiros 5 keywords
                            if not all(key in kw for key in ["keyword", "search_volume", "cpc"]):
                                response.failure("Estrutura de keyword inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de keywords")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                elif response.status_code == 403:
                    response.success()  # Quota excedida
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="POST",
                name="Google Keywords Search",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(4)
    def test_google_keywords_volume(self):
        """Testa análise de volume Google Keywords"""
        try:
            keyword = random.choice(self.test_keywords)
            
            params = {
                "keyword": keyword,
                "language": "pt",
                "location": random.choice(self.test_locations),
                "time_period": random.choice(["last_30_days", "last_90_days", "last_12_months"]),
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/google/keywords/volume",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="Google Keywords Volume"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "volume_data" in data:
                        response.success()
                        # Valida métricas básicas
                        volume_data = data["volume_data"]
                        if not all(key in volume_data for key in ["keyword", "search_volume", "trend"]):
                            response.failure("Métricas de volume incompletas")
                    else:
                        response.failure("Dados de volume não encontrados")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                elif response.status_code == 403:
                    response.success()  # Quota excedida
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Google Keywords Volume",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(4)
    def test_google_keywords_cpc(self):
        """Testa análise de CPC Google Keywords"""
        try:
            keyword = random.choice(self.test_keywords)
            
            params = {
                "keyword": keyword,
                "language": "pt",
                "location": random.choice(self.test_locations),
                "include_competition": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/google/keywords/cpc",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="Google Keywords CPC"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "cpc_data" in data:
                        response.success()
                        # Valida métricas básicas
                        cpc_data = data["cpc_data"]
                        if not all(key in cpc_data for key in ["keyword", "cpc", "competition"]):
                            response.failure("Métricas de CPC incompletas")
                    else:
                        response.failure("Dados de CPC não encontrados")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                elif response.status_code == 403:
                    response.success()  # Quota excedida
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Google Keywords CPC",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(3)
    def test_google_keywords_competition(self):
        """Testa análise de concorrência Google Keywords"""
        try:
            keyword = random.choice(self.test_keywords)
            
            params = {
                "keyword": keyword,
                "language": "pt",
                "location": random.choice(self.test_locations),
                "include_competitors": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/google/keywords/competition",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="Google Keywords Competition"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "competition_data" in data:
                        response.success()
                        # Valida métricas básicas
                        competition_data = data["competition_data"]
                        if not all(key in competition_data for key in ["keyword", "competition_level", "competitors"]):
                            response.failure("Métricas de concorrência incompletas")
                    else:
                        response.failure("Dados de concorrência não encontrados")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                elif response.status_code == 403:
                    response.success()  # Quota excedida
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Google Keywords Competition",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(2)
    def test_google_keywords_comprehensive_analysis(self):
        """Testa análise completa Google Keywords"""
        try:
            analysis_data = {
                "keywords": random.sample(self.test_keywords, 3),
                "language": "pt",
                "location": random.choice(self.test_locations),
                "analysis_type": "comprehensive",
                "include_volume": True,
                "include_cpc": True,
                "include_competition": True,
                "include_trends": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.post(
                "/api/integrations/google/keywords/analyze",
                json=analysis_data,
                headers=self.headers,
                catch_response=True,
                name="Google Keywords Comprehensive Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "analysis_results" in data:
                        response.success()
                        # Valida estrutura da análise
                        results = data["analysis_results"]
                        if not all(key in results for key in ["keywords", "volume_data", "cpc_data", "competition_data"]):
                            response.failure("Estrutura de análise incompleta")
                    else:
                        response.failure("Resultados de análise não encontrados")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                elif response.status_code == 403:
                    response.success()  # Quota excedida
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="POST",
                name="Google Keywords Comprehensive Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(1)
    def test_google_keywords_quota_management(self):
        """Testa quota management Google Keywords"""
        try:
            # Faz múltiplas requisições para testar quota management
            for i in range(3):
                params = {
                    "keyword": f"test_keyword_{i}",
                    "language": "pt",
                    "location": "Brazil",
                    "tracing_id": self.tracing_id
                }
                
                with self.client.get(
                    "/api/integrations/google/keywords/volume",
                    params=params,
                    headers=self.headers,
                    catch_response=True,
                    name="Google Keywords Quota Management Test"
                ) as response:
                    if response.status_code == 403:
                        response.success()  # Quota excedida funcionando
                        break
                    elif response.status_code == 200:
                        response.success()
                    elif response.status_code == 429:
                        response.success()  # Rate limiting funcionando
                    else:
                        response.failure(f"Status inesperado: {response.status_code}")
                        
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Google Keywords Quota Management Test",
                response_time=0,
                exception=e,
                response_length=0
            )

class GoogleKeywordsIntegrationUser(HttpUser):
    """Usuário de teste para integração Google Keywords"""
    
    tasks = {GoogleKeywordsIntegrationTasks: 1}
    wait_time = between(1, 3)
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = TRACING_ID
        print(f"[{self.tracing_id}] Usuário Google Keywords iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        print(f"[{self.tracing_id}] Usuário Google Keywords finalizado")

# Event listeners para métricas
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Handler para eventos de requisição"""
    if exception:
        print(f"[{TRACING_ID}] Erro na requisição {name}: {exception}")
    elif response and response.status_code >= 400:
        print(f"[{TRACING_ID}] Requisição {name} falhou com status {response.status_code}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    print(f"[{TRACING_ID}] Teste de carga Google Keywords iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"[{TRACING_ID}] Teste de carga Google Keywords finalizado") 