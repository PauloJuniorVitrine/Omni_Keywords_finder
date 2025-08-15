"""
locustfile_integration_youtube_v1.py
Teste de carga para os endpoints de integração YouTube

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Alto
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_INTEGRATION_YOUTUBE_20250127_001

Endpoints testados:
- POST /api/integrations/youtube/auth - Autenticação OAuth 2.0
- GET /api/integrations/youtube/videos - Busca de vídeos
- GET /api/integrations/youtube/comments - Análise de comentários
- GET /api/integrations/youtube/trends - Análise de tendências
- POST /api/integrations/youtube/analyze - Análise completa

Cenários:
- Autenticação OAuth 2.0 com Google Cloud
- Busca de vídeos com diferentes queries
- Análise de comentários e transcrições
- Quota management e rate limiting
- Circuit breaker e fallback
"""

from locust import HttpUser, TaskSet, task, between, events
import json
import time
import random
from typing import Dict, Any

TRACING_ID = "LOAD_INTEGRATION_YOUTUBE_20250127_001"

class YouTubeIntegrationTasks(TaskSet):
    """Tarefas de teste de carga para integração YouTube"""
    
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
            "trending videos",
            "tutorial",
            "review"
        ]
        self.test_video_ids = [
            "dQw4w9WgXcQ",  # Rick Roll (exemplo)
            "9bZkp7q19f0",  # PSY - GANGNAM STYLE
            "kJQP7kiw5Fk",  # Luis Fonsi - Despacito
            "ZZ5LpwO-An4",  # Ed Sheeran - Shape of You
            "JGwWNGJdvx8"   # Ed Sheeran - Perfect
        ]
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "X-Tracing-ID": self.tracing_id,
            "User-Agent": "OmniKeywordsBot/1.0"
        }
    
    @task(3)
    def test_youtube_auth(self):
        """Testa autenticação OAuth 2.0 YouTube"""
        try:
            # Simula fluxo de autenticação OAuth 2.0
            auth_data = {
                "client_id": "test_client_id",
                "scope": "https://www.googleapis.com/auth/youtube.readonly",
                "redirect_uri": "https://api.omni-keywords.com/auth/youtube/callback",
                "state": f"state_{int(time.time())}",
                "access_type": "offline",
                "prompt": "consent"
            }
            
            with self.client.post(
                "/api/integrations/youtube/auth",
                json=auth_data,
                headers=self.headers,
                catch_response=True,
                name="YouTube OAuth Auth"
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
                name="YouTube OAuth Auth",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(5)
    def test_youtube_video_search(self):
        """Testa busca de vídeos YouTube"""
        try:
            query = random.choice(self.test_queries)
            
            params = {
                "query": query,
                "max_results": random.randint(10, 50),
                "order": random.choice(["relevance", "date", "rating", "viewCount"]),
                "type": "video",
                "part": "snippet",
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/youtube/videos",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="YouTube Video Search"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "videos" in data and isinstance(data["videos"], list):
                        response.success()
                        # Valida estrutura dos dados
                        for video in data["videos"][:5]:  # Valida primeiros 5 vídeos
                            if not all(key in video for key in ["id", "title", "snippet"]):
                                response.failure("Estrutura de vídeo inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de vídeos")
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
                name="YouTube Video Search",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(4)
    def test_youtube_video_details(self):
        """Testa detalhes de vídeo YouTube"""
        try:
            video_id = random.choice(self.test_video_ids)
            
            params = {
                "video_id": video_id,
                "part": "snippet,statistics,contentDetails",
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/youtube/video",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="YouTube Video Details"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "video" in data:
                        response.success()
                        # Valida métricas básicas
                        video = data["video"]
                        if not all(key in video for key in ["id", "title", "statistics"]):
                            response.failure("Métricas de vídeo incompletas")
                    else:
                        response.failure("Detalhes de vídeo não encontrados")
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
                name="YouTube Video Details",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(3)
    def test_youtube_comments_analysis(self):
        """Testa análise de comentários YouTube"""
        try:
            video_id = random.choice(self.test_video_ids)
            
            params = {
                "video_id": video_id,
                "max_results": random.randint(10, 100),
                "part": "snippet",
                "order": random.choice(["relevance", "time"]),
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/youtube/comments",
                params=params,
                headers=self.headers,
                catch_response=True,
                name="YouTube Comments Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "comments" in data and isinstance(data["comments"], list):
                        response.success()
                        # Valida estrutura dos comentários
                        for comment in data["comments"][:3]:  # Valida primeiros 3 comentários
                            if not all(key in comment for key in ["id", "snippet"]):
                                response.failure("Estrutura de comentário inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de comentários")
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
                name="YouTube Comments Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(3)
    def test_youtube_trends_analysis(self):
        """Testa análise de tendências YouTube"""
        try:
            trends_data = {
                "region_code": random.choice(["BR", "US", "CA", "GB"]),
                "video_category_id": random.choice(["1", "10", "15", "17", "20"]),
                "max_results": random.randint(10, 50),
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "tracing_id": self.tracing_id
            }
            
            with self.client.get(
                "/api/integrations/youtube/trends",
                params=trends_data,
                headers=self.headers,
                catch_response=True,
                name="YouTube Trends Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "trending_videos" in data and isinstance(data["trending_videos"], list):
                        response.success()
                        # Valida estrutura das tendências
                        for video in data["trending_videos"][:3]:  # Valida primeiros 3 vídeos
                            if not all(key in video for key in ["id", "snippet", "statistics"]):
                                response.failure("Estrutura de vídeo em tendência inválida")
                                break
                    else:
                        response.failure("Resposta não contém lista de vídeos em tendência")
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
                name="YouTube Trends Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(2)
    def test_youtube_comprehensive_analysis(self):
        """Testa análise completa YouTube"""
        try:
            analysis_data = {
                "keywords": random.sample(self.test_queries, 3),
                "video_ids": random.sample(self.test_video_ids, 2),
                "analysis_type": "comprehensive",
                "include_comments": True,
                "include_transcripts": True,
                "include_trends": True,
                "tracing_id": self.tracing_id
            }
            
            with self.client.post(
                "/api/integrations/youtube/analyze",
                json=analysis_data,
                headers=self.headers,
                catch_response=True,
                name="YouTube Comprehensive Analysis"
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    if "analysis_results" in data:
                        response.success()
                        # Valida estrutura da análise
                        results = data["analysis_results"]
                        if not all(key in results for key in ["videos", "comments", "trends"]):
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
                name="YouTube Comprehensive Analysis",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    @task(1)
    def test_youtube_quota_management(self):
        """Testa quota management YouTube"""
        try:
            # Faz múltiplas requisições para testar quota management
            for i in range(3):
                params = {
                    "query": f"test_query_{i}",
                    "max_results": 10,
                    "tracing_id": self.tracing_id
                }
                
                with self.client.get(
                    "/api/integrations/youtube/videos",
                    params=params,
                    headers=self.headers,
                    catch_response=True,
                    name="YouTube Quota Management Test"
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
                name="YouTube Quota Management Test",
                response_time=0,
                exception=e,
                response_length=0
            )

class YouTubeIntegrationUser(HttpUser):
    """Usuário de teste para integração YouTube"""
    
    tasks = {YouTubeIntegrationTasks: 1}
    wait_time = between(1, 3)
    
    def on_start(self):
        """Inicialização do usuário"""
        self.tracing_id = TRACING_ID
        print(f"[{self.tracing_id}] Usuário YouTube iniciado")
    
    def on_stop(self):
        """Finalização do usuário"""
        print(f"[{self.tracing_id}] Usuário YouTube finalizado")

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
    print(f"[{TRACING_ID}] Teste de carga YouTube iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    print(f"[{TRACING_ID}] Teste de carga YouTube finalizado") 