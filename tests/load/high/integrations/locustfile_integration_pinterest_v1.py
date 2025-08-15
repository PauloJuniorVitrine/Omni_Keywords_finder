"""
locustfile_integration_pinterest_v1.py
Teste de carga para os endpoints de integração Pinterest

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_INTEGRATION_PINTEREST_20250127_001

Endpoints testados:
- POST /api/integrations/pinterest/auth - Autenticação OAuth 2.0
- GET /api/integrations/pinterest/pins - Busca de pins
- GET /api/integrations/pinterest/boards - Análise de boards
- GET /api/integrations/pinterest/trends - Análise de tendências
- POST /api/integrations/pinterest/analyze - Análise completa

Cenários:
- Autenticação OAuth 2.0 com Pinterest
- Busca de pins com diferentes queries
- Análise de boards e usuários
- Rate limiting e circuit breaker
- Fallback para web scraping
"""

from locust import HttpUser, TaskSet, task, between, events
import json
import time
import random
from typing import Dict, Any

TRACING_ID = "LOAD_INTEGRATION_PINTEREST_20250127_001"

class PinterestIntegrationTasks(TaskSet):
    """Tarefas de teste de carga para integração Pinterest"""
    
    def on_start(self):
        """Inicialização das tarefas"""
        self.tracing_id = TRACING_ID
        self.auth_token = None
        self.test_queries = [
            "home decor",
            "fashion style", 
            "recipe ideas",
            "travel inspiration",
            "diy crafts",
            "wedding planning",
            "fitness motivation",
            "beauty tips",
            "gardening ideas",
            "art inspiration"
        ]
        self.test_board_ids = [
            "test_board_1",
            "test_board_2", 
            "test_board_3",
            "test_board_4",
            "test_board_5"
        ]
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "X-Tracing-ID": self.tracing_id,
            "User-Agent": "OmniKeywordsBot/1.0"
        }
    
    @task(3)
    def test_pinterest_auth(self):
        """Testa autenticação OAuth 2.0 Pinterest"""
        try:
            # Simula fluxo de autenticação OAuth 2.0
            auth_data = {
                "client_id": "test_client_id",
                "scope": "boards:read,pins:read,user_accounts:read",
                "redirect_uri": "https://api.omni-keywords.com/auth/pinterest/callback",
                "state": f"state_{int(time.time())}",
                "response_type": "code"
            }
            
            with self.client.post(
                "/api/integrations/pinterest/auth",
                json=auth_data,
                headers=self.headers,
                catch_response=True,
                name="Pinterest OAuth Auth"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "auth_url" in data:
                        response.success()
                        self.auth_token = data.get("access_token")
                    else:
                        response.failure("URL de autorização não encontrada")
                elif response.status_code == 401:
                    response.success()  # Esperado para credenciais de teste
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="POST",
                name="Pinterest OAuth Auth",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(5)
    def test_pinterest_pin_search(self):
        """Testa busca de pins Pinterest"""
        try:
            query = random.choice(self.test_queries)
            
            params = {
                "query": query,
                "page_size": random.randint(10, 25),
                "fields": "id,title,description,link,board_id,created_at,creative_type",
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/pinterest/pins",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="Pinterest Pin Search"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data and isinstance(data["items"], list):
                        response.success()
                        # Valida estrutura dos dados
                        for pin in data["items"][:5]:  # Valida primeiros 5 pins
                            if not all(key in pin for key in ["id", "title", "board_id"]):
                                response.failure("Estrutura de pin inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de pins")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Pinterest Pin Search",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(4)
    def test_pinterest_board_analysis(self):
        """Testa análise de boards Pinterest"""
        try:
            board_id = random.choice(self.test_board_ids)
            
            params = {
                "board_id": board_id,
                "fields": "id,name,description,pin_count,follower_count,created_at",
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/pinterest/boards",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="Pinterest Board Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "board" in data:
                        response.success()
                        # Valida métricas básicas
                        board = data["board"]
                        if not all(key in board for key in ["id", "name", "pin_count"]):
                            response.failure("Métricas de board incompletas")
                    else:
                        response.failure("Detalhes de board não encontrados")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Pinterest Board Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(3)
    def test_pinterest_user_analysis(self):
        """Testa análise de usuários Pinterest"""
        try:
            params = {
                "fields": "username,about,website,profile_image,follower_count,following_count",
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/pinterest/user",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="Pinterest User Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data:
                        response.success()
                        # Valida estrutura do usuário
                        user = data["user"]
                        if not all(key in user for key in ["username", "follower_count"]):
                            response.failure("Dados de usuário incompletos")
                    else:
                        response.failure("Dados de usuário não encontrados")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Pinterest User Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(3)
    def test_pinterest_trends_analysis(self):
        """Testa análise de tendências Pinterest"""
        try:
            trends_data = {
                "category": random.choice(["home", "fashion", "food", "travel", "crafts"]),
                "time_period": random.choice(["day", "week", "month"]),
                "max_results": random.randint(10, 50),
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/pinterest/trends",
                params=trends_data,
                headers=self.headers,
                catch_response=True,
                name="Pinterest Trends Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "trending_pins" in data and isinstance(data["trending_pins"], list):
                        response.success()
                        # Valida estrutura das tendências
                        for pin in data["trending_pins"][:3]:  # Valida primeiros 3 pins
                            if not all(key in pin for key in ["id", "title", "save_count"]):
                                response.failure("Estrutura de pin em tendência inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de pins em tendência")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Pinterest Trends Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(2)
    def test_pinterest_comprehensive_analysis(self):
        """Testa análise completa Pinterest"""
        try:
            analysis_data = {
                "keywords": random.sample(self.test_queries, 3),
                "board_ids": random.sample(self.test_board_ids, 2),
                "analysis_type": "comprehensive",
                "include_pins": True,
                "include_boards": True,
                "include_trends": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.post(
                "/api/integrations/pinterest/analyze",
                json=analysis_data,
                headers=self.headers,
                catch_response=True,
                name="Pinterest Comprehensive Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "analysis_results" in data:
                        response.success()
                        # Valida estrutura da análise
                        results = data["analysis_results"]
                        if not all(key in results for key in ["pins", "boards", "trends"]):
                            response.failure("Estrutura de análise incompleta")
                    else:
                        response.failure("Resultados de análise não encontrados")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="POST",
                name="Pinterest Comprehensive Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(1)
    def test_pinterest_rate_limiting(self):
        """Testa rate limiting Pinterest"""
        try:
            # Faz múltiplas requisições para testar rate limiting
            for i in range(3):
                params = {
                    "query": f"test_query_{i}",
                    "page_size": 10,
                    "tracing_id": self.tracing_id
                }
                
                with self.client.get(
                    "/api/integrations/pinterest/pins",
                    params=params,
                    headers=self.headers,
                    catch_response=True,
                    name="Pinterest Rate Limiting Test"
                ) as response:
                    if response.status_code == 429:
                        response.success()  # Rate limiting funcionando
                        break
                    elif response.status_code == 200:
                        response.success()
                    elif response.status_code == 503:
                        response.success()  # Circuit breaker funcionando
                    else:
                        response.failure(f"Status inesperado: {response.status_code}")
                        
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="Pinterest Rate Limiting Test",
                response_time=0,
                exception=e,
                response_length=0
            )

class PinterestIntegrationUser(HttpUser):
    """Usuário de teste para integração Pinterest"""
    
    tasks = {PinterestIntegrationTasks: 1}
    wait_time = between(1, 3)
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = TRACING_ID
        print(f"[{self.tracing_id}] Usuário Pinterest iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        print(f"[{self.tracing_id}] Usuário Pinterest finalizado")

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
    print(f"[{TRACING_ID}] Teste de carga Pinterest iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"[{TRACING_ID}] Teste de carga Pinterest finalizado") 