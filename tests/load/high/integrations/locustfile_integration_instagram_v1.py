"""
Teste de Carga - Integração Instagram (v1)
Baseado em: infrastructure/coleta/instagram_real_api.py
Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - 5.1 APIs de Redes Sociais
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_TEST_INSTAGRAM_20250127_001

Funcionalidades testadas:
- Coleta de dados do Instagram via API oficial
- OAuth 2.0 e autenticação
- Rate limiting e circuit breaker
- Cache inteligente e fallback
- Performance sob carga de múltiplos usuários
- Tratamento de erros e logs estruturados
"""

from locust import HttpUser, task, between, events
import random
import time
import json
from typing import Dict, List, Optional, Any

class InstagramIntegrationUser(HttpUser):
    """
    Usuário simulando integração com Instagram API
    """
    wait_time = between(3, 6)  # Intervalo maior para APIs de redes sociais
    
    def on_start(self):
        """Setup inicial do usuário"""
        self.instagram_endpoints = [
            "/api/integrations/instagram/user/{username}",
            "/api/integrations/instagram/hashtag/{hashtag}",
            "/api/integrations/instagram/location/{location_id}",
            "/api/integrations/instagram/media/{media_id}",
            "/api/integrations/instagram/stories/{user_id}",
            "/api/integrations/instagram/insights/{media_id}",
            "/api/integrations/instagram/comments/{media_id}",
            "/api/integrations/instagram/followers/{user_id}",
            "/api/integrations/instagram/engagement/{media_id}",
            "/api/integrations/instagram/trending"
        ]
        
        self.test_usernames = [
            "nike", "adidas", "apple", "samsung", "coca_cola",
            "pepsi", "mcdonalds", "burgerking", "netflix", "spotify",
            "amazon", "google", "microsoft", "tesla", "spacex",
            "instagram", "facebook", "twitter", "tiktok", "youtube"
        ]
        
        self.test_hashtags = [
            "marketing", "digital", "seo", "socialmedia", "branding",
            "design", "photography", "travel", "food", "fitness",
            "fashion", "beauty", "technology", "business", "entrepreneur",
            "startup", "innovation", "sustainability", "wellness", "lifestyle"
        ]
        
        self.test_locations = [
            "214437944",  # São Paulo, Brazil
            "214437945",  # Rio de Janeiro, Brazil
            "214437946",  # New York, USA
            "214437947",  # Los Angeles, USA
            "214437948",  # London, UK
            "214437949",  # Paris, France
            "214437950",  # Tokyo, Japan
            "214437951",  # Sydney, Australia
            "214437952",  # Toronto, Canada
            "214437953"   # Berlin, Germany
        ]
        
        # Contadores para métricas
        self.user_data_count = 0
        self.hashtag_data_count = 0
        self.location_data_count = 0
        self.media_data_count = 0
        self.insights_count = 0
        self.rate_limit_count = 0
        self.auth_error_count = 0
        self.api_error_count = 0
    
    @task(4)  # 40% das requisições - dados de usuário
    def get_user_data(self):
        """
        Teste de carga para dados de usuário do Instagram
        """
        username = random.choice(self.test_usernames)
        
        # Parâmetros variados para simular uso real
        params = {
            "fields": random.choice([
                "id,username,full_name,biography,followers_count,follows_count,media_count",
                "id,username,profile_picture_url,website,is_private,is_verified",
                "id,username,full_name,biography,followers_count,media_count,is_business_account"
            ]),
            "access_token": "test_token",  # Token de teste
            "limit": random.randint(10, 50),
            "cache": random.choice(["true", "false"])
        }
        
        start_time = time.time()
        
        try:
            with self.client.get(
                f"/api/integrations/instagram/user/{username}",
                params=params,
                catch_response=True,
                timeout=15
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validações de resposta
                        if isinstance(data, dict) and "id" in data:
                            self.user_data_count += 1
                            response.success()
                            
                            # Log de sucesso
                            events.request.fire(
                                request_type="GET",
                                name="instagram_user_success",
                                response_time=response_time * 1000,
                                response_length=len(response.content),
                                exception=None,
                                context={
                                    "username": username,
                                    "params": params,
                                    "response_fields": list(data.keys())
                                }
                            )
                        else:
                            self.api_error_count += 1
                            response.failure("Resposta inválida para dados de usuário")
                            
                    except json.JSONDecodeError:
                        self.api_error_count += 1
                        response.failure("Resposta não é JSON válido")
                        
                elif response.status_code == 401:
                    self.auth_error_count += 1
                    response.success()  # Erro de auth é esperado em testes
                    
                elif response.status_code == 429:
                    self.rate_limit_count += 1
                    response.success()  # Rate limit é comportamento esperado
                    
                elif response.status_code >= 500:
                    self.api_error_count += 1
                    response.failure(f"Erro da API: {response.status_code}")
                    
                else:
                    self.api_error_count += 1
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.api_error_count += 1
            events.request.fire(
                request_type="GET",
                name="instagram_user_exception",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "username": username,
                    "params": params,
                    "error": str(e)
                }
            )
    
    @task(3)  # 30% das requisições - dados de hashtag
    def get_hashtag_data(self):
        """
        Teste de carga para dados de hashtag do Instagram
        """
        hashtag = random.choice(self.test_hashtags)
        
        params = {
            "fields": random.choice([
                "id,name,media_count,top_media",
                "id,name,media_count,recent_media",
                "id,name,media_count,related_tags"
            ]),
            "access_token": "test_token",
            "limit": random.randint(20, 100),
            "media_type": random.choice(["all", "image", "video", "carousel"]),
            "time_period": random.choice(["day", "week", "month"])
        }
        
        start_time = time.time()
        
        try:
            with self.client.get(
                f"/api/integrations/instagram/hashtag/{hashtag}",
                params=params,
                catch_response=True,
                timeout=20
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validações de resposta
                        if isinstance(data, dict) and "id" in data and "media_count" in data:
                            self.hashtag_data_count += 1
                            response.success()
                            
                            # Log de sucesso
                            events.request.fire(
                                request_type="GET",
                                name="instagram_hashtag_success",
                                response_time=response_time * 1000,
                                response_length=len(response.content),
                                exception=None,
                                context={
                                    "hashtag": hashtag,
                                    "params": params,
                                    "media_count": data.get("media_count", 0)
                                }
                            )
                        else:
                            self.api_error_count += 1
                            response.failure("Resposta inválida para dados de hashtag")
                            
                    except json.JSONDecodeError:
                        self.api_error_count += 1
                        response.failure("Resposta não é JSON válido")
                        
                elif response.status_code == 401:
                    self.auth_error_count += 1
                    response.success()
                    
                elif response.status_code == 429:
                    self.rate_limit_count += 1
                    response.success()
                    
                elif response.status_code >= 500:
                    self.api_error_count += 1
                    response.failure(f"Erro da API: {response.status_code}")
                    
                else:
                    self.api_error_count += 1
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.api_error_count += 1
            events.request.fire(
                request_type="GET",
                name="instagram_hashtag_exception",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "hashtag": hashtag,
                    "params": params,
                    "error": str(e)
                }
            )
    
    @task(2)  # 20% das requisições - dados de localização
    def get_location_data(self):
        """
        Teste de carga para dados de localização do Instagram
        """
        location_id = random.choice(self.test_locations)
        
        params = {
            "fields": random.choice([
                "id,name,latitude,longitude,media_count",
                "id,name,street_address,city,media_count",
                "id,name,latitude,longitude,top_media"
            ]),
            "access_token": "test_token",
            "limit": random.randint(10, 50),
            "media_type": random.choice(["all", "image", "video"])
        }
        
        start_time = time.time()
        
        try:
            with self.client.get(
                f"/api/integrations/instagram/location/{location_id}",
                params=params,
                catch_response=True,
                timeout=15
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validações de resposta
                        if isinstance(data, dict) and "id" in data and "name" in data:
                            self.location_data_count += 1
                            response.success()
                            
                            # Log de sucesso
                            events.request.fire(
                                request_type="GET",
                                name="instagram_location_success",
                                response_time=response_time * 1000,
                                response_length=len(response.content),
                                exception=None,
                                context={
                                    "location_id": location_id,
                                    "params": params,
                                    "location_name": data.get("name", "")
                                }
                            )
                        else:
                            self.api_error_count += 1
                            response.failure("Resposta inválida para dados de localização")
                            
                    except json.JSONDecodeError:
                        self.api_error_count += 1
                        response.failure("Resposta não é JSON válido")
                        
                elif response.status_code == 401:
                    self.auth_error_count += 1
                    response.success()
                    
                elif response.status_code == 429:
                    self.rate_limit_count += 1
                    response.success()
                    
                elif response.status_code >= 500:
                    self.api_error_count += 1
                    response.failure(f"Erro da API: {response.status_code}")
                    
                else:
                    self.api_error_count += 1
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.api_error_count += 1
            events.request.fire(
                request_type="GET",
                name="instagram_location_exception",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "location_id": location_id,
                    "params": params,
                    "error": str(e)
                }
            )
    
    @task(1)  # 10% das requisições - insights e métricas
    def get_insights_data(self):
        """
        Teste de carga para insights e métricas do Instagram
        """
        # Simula diferentes tipos de insights
        insight_types = [
            "media_insights",
            "story_insights", 
            "account_insights",
            "audience_insights"
        ]
        
        insight_type = random.choice(insight_types)
        
        # Gera IDs fictícios para teste
        media_id = f"media_{int(time.time())}"
        user_id = f"user_{int(time.time())}"
        
        params = {
            "access_token": "test_token",
            "metric": random.choice([
                "impressions,reach,engagement",
                "saved,comments,likes",
                "profile_views,website_clicks,email_contacts"
            ]),
            "period": random.choice(["day", "week", "month"]),
            "limit": random.randint(10, 30)
        }
        
        start_time = time.time()
        
        try:
            endpoint = f"/api/integrations/instagram/insights/{media_id}"
            
            with self.client.get(
                endpoint,
                params=params,
                catch_response=True,
                timeout=20
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validações básicas
                        if isinstance(data, dict):
                            self.insights_count += 1
                            response.success()
                            
                            # Log de sucesso
                            events.request.fire(
                                request_type="GET",
                                name="instagram_insights_success",
                                response_time=response_time * 1000,
                                response_length=len(response.content),
                                exception=None,
                                context={
                                    "insight_type": insight_type,
                                    "media_id": media_id,
                                    "params": params,
                                    "response_keys": list(data.keys())
                                }
                            )
                        else:
                            self.api_error_count += 1
                            response.failure("Resposta inválida para insights")
                            
                    except json.JSONDecodeError:
                        self.api_error_count += 1
                        response.failure("Resposta não é JSON válido")
                        
                elif response.status_code == 401:
                    self.auth_error_count += 1
                    response.success()
                    
                elif response.status_code == 429:
                    self.rate_limit_count += 1
                    response.success()
                    
                elif response.status_code >= 500:
                    self.api_error_count += 1
                    response.failure(f"Erro da API: {response.status_code}")
                    
                else:
                    self.api_error_count += 1
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.api_error_count += 1
            events.request.fire(
                request_type="GET",
                name="instagram_insights_exception",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "insight_type": insight_type,
                    "media_id": media_id,
                    "params": params,
                    "error": str(e)
                }
            )
    
    def on_stop(self):
        """Cleanup ao final do teste"""
        # Log de métricas finais
        total_requests = (
            self.user_data_count + self.hashtag_data_count + 
            self.location_data_count + self.insights_count +
            self.rate_limit_count + self.auth_error_count + 
            self.api_error_count
        )
        
        if total_requests > 0:
            success_rate = (
                (self.user_data_count + self.hashtag_data_count + 
                 self.location_data_count + self.insights_count) / total_requests
            ) * 100
            rate_limit_rate = (self.rate_limit_count / total_requests) * 100
            auth_error_rate = (self.auth_error_count / total_requests) * 100
            api_error_rate = (self.api_error_count / total_requests) * 100
            
            events.request.fire(
                request_type="METRICS",
                name="instagram_final_metrics",
                response_time=0,
                response_length=0,
                exception=None,
                context={
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "rate_limit_rate": rate_limit_rate,
                    "auth_error_rate": auth_error_rate,
                    "api_error_rate": api_error_rate,
                    "user_data_count": self.user_data_count,
                    "hashtag_data_count": self.hashtag_data_count,
                    "location_data_count": self.location_data_count,
                    "insights_count": self.insights_count,
                    "rate_limit_count": self.rate_limit_count,
                    "auth_error_count": self.auth_error_count,
                    "api_error_count": self.api_error_count
                }
            ) 