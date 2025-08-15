"""
locustfile_integration_tiktok_v1.py
Teste de carga para os endpoints de integração TikTok

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_INTEGRATION_TIKTOK_20250127_001

Endpoints testados:
- POST /api/integrations/tiktok/auth - Autenticação OAuth 2.0
- GET /api/integrations/tiktok/videos - Busca de vídeos
- GET /api/integrations/tiktok/hashtags - Análise de hashtags
- GET /api/integrations/tiktok/trends - Análise de tendências
- POST /api/integrations/tiktok/analyze - Análise completa

Cenários:
- Autenticação OAuth 2.0 com PKCE
- Busca de vídeos com diferentes queries
- Análise de hashtags trending
- Rate limiting e circuit breaker
- Fallback para web scraping
"""

from locust import HttpUser, TaskSet, task, between, events
import json
import time
import random
from typing import Dict, Any

TRACING_ID = "LOAD_INTEGRATION_TIKTOK_20250127_001"

class TikTokIntegrationTasks(TaskSet):
    """Tarefas de teste de carga para integração TikTok"""
    
    def on_start(self):
        """Inicialização das tarefas"""
        self.tracing_id = TRACING_ID
        self.auth_token = None
        self.test_queries = [
            "marketing digital",
            "seo optimization", 
            "content creation",
            "social media",
            "brand awareness",
            "influencer marketing",
            "video marketing",
            "trending hashtags"
        ]
        self.test_hashtags = [
            "marketing",
            "digital",
            "seo",
            "content",
            "socialmedia",
            "branding",
            "influencer",
            "viral"
        ]
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "X-Tracing-ID": self.tracing_id,
            "User-Agent": "OmniKeywordsBot/1.0"
        }
    
    @task(3)
    def test_tiktok_auth(self):
        """Testa autenticação OAuth 2.0 TikTok"""
        try:
            # Simula fluxo de autenticação OAuth 2.0
            auth_data = {
                "client_key": "test_client_key",
                "scope": "user.info.basic,video.list,hashtag.search",
                "redirect_uri": "https://api.omni-keywords.com/auth/tiktok/callback",
                "state": f"state_{int(time.time())}",
                "code_challenge": "test_challenge",
                "code_challenge_method": "S256"
            }
            
            with self.client.post(
                "/api/integrations/tiktok/auth",
                json=auth_data,
                headers=self.headers,
                catch_response=True,
                name="TikTok OAuth Auth"
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
                name="TikTok OAuth Auth",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(5)
    def test_tiktok_video_search(self):
        """Testa busca de vídeos TikTok"""
        try:
            query = random.choice(self.test_queries)
            
            params = {
                "query": query,
                "max_count": random.randint(10, 50),
                "fields": ["id", "title", "description", "duration", "statistics"],
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/tiktok/videos",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="TikTok Video Search"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "videos" in data and isinstance(data["videos"], list):
                        response.success()
                        # Valida estrutura dos dados
                        for video in data["videos"][:5]:  # Valida primeiros 5 vídeos
                            if not all(key in video for key in ["id", "title", "statistics"]):
                                response.failure("Estrutura de vídeo inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de vídeos")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="TikTok Video Search",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(4)
    def test_tiktok_hashtag_analysis(self):
        """Testa análise de hashtags TikTok"""
        try:
            hashtag = random.choice(self.test_hashtags)
            
            params = {
                "hashtag": hashtag,
                "include_related": True,
                "include_metrics": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/tiktok/hashtags",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="TikTok Hashtag Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "hashtag_info" in data:
                        response.success()
                        # Valida métricas básicas
                        hashtag_info = data["hashtag_info"]
                        if not all(key in hashtag_info for key in ["name", "video_count"]):
                            response.failure("Métricas de hashtag incompletas")
                    else:
                        response.failure("Informações de hashtag não encontradas")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="TikTok Hashtag Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(3)
    def test_tiktok_trends_analysis(self):
        """Testa análise de tendências TikTok"""
        try:
            trends_data = {
                "period": random.choice(["1d", "7d", "30d"]),
                "category": random.choice(["videos", "hashtags", "sounds"]),
                "limit": random.randint(10, 50),
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/tiktok/trends",
                params=trends_data,
                headers=self.headers,
                catch_response=True,
                name="TikTok Trends Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "trends" in data and isinstance(data["trends"], list):
                        response.success()
                        # Valida estrutura das tendências
                        for trend in data["trends"][:3]:  # Valida primeiras 3 tendências
                            if not all(key in trend for key in ["name", "growth_rate"]):
                                response.failure("Estrutura de tendência inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de tendências")
                elif response.status_code == 429:
                    response.success()  # Rate limiting esperado
                elif response.status_code == 503:
                    response.success()  # Circuit breaker ativo
                else:
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="TikTok Trends Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(2)
    def test_tiktok_comprehensive_analysis(self):
        """Testa análise completa TikTok"""
        try:
            analysis_data = {
                "keywords": random.sample(self.test_queries, 3),
                "hashtags": random.sample(self.test_hashtags, 2),
                "analysis_type": "comprehensive",
                "include_metrics": True,
                "include_trends": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.post(
                "/api/integrations/tiktok/analyze",
                json=analysis_data,
                headers=self.headers,
                catch_response=True,
                name="TikTok Comprehensive Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "analysis_results" in data:
                        response.success()
                        # Valida estrutura da análise
                        results = data["analysis_results"]
                        if not all(key in results for key in ["keywords", "hashtags", "trends"]):
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
                name="TikTok Comprehensive Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(1)
    def test_tiktok_rate_limiting(self):
        """Testa rate limiting TikTok"""
        try:
            # Faz múltiplas requisições rápidas para testar rate limiting
            for i in range(5):
                params = {
                    "query": f"test_query_{i}",
                    "max_count": 10,
                    "tracing_id": self.tracing_id
                }
                
                with self.client.get(
                    "/api/integrations/tiktok/videos",
                    params=params,
                    headers=self.headers,
                    catch_response=True,
                    name="TikTok Rate Limiting Test"
                ) as response:
                    if response.status_code == 429:
                        response.success()  # Rate limiting funcionando
                        break
                    elif response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Status inesperado: {response.status_code}")
                        
        except Exception as e:
            self.client.environment.events.request_failure.fire(
                request_type="GET",
                name="TikTok Rate Limiting Test",
                response_time=0,
                exception=e,
                response_length=0
            )

class TikTokIntegrationUser(HttpUser):
    """Usuário de teste para integração TikTok"""
    
    tasks = {TikTokIntegrationTasks: 1}
    wait_time = between(1, 3)
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = TRACING_ID
        print(f"[{self.tracing_id}] Usuário TikTok iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        print(f"[{self.tracing_id}] Usuário TikTok finalizado")

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
    print(f"[{TRACING_ID}] Teste de carga TikTok iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"[{TRACING_ID}] Teste de carga TikTok finalizado") 