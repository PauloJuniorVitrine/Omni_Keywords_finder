"""
Teste de Carga - Integração Google Trends (v1)
Baseado em: /api/externo/google_trends (GET)
Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - 5.2 APIs de Google
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_TEST_GOOGLE_TRENDS_20250127_001

Funcionalidades testadas:
- Consulta de tendências do Google Trends
- Simulação de cenários de erro (timeout, autenticação, resposta inválida)
- Rate limiting e validação de parâmetros
- Performance sob carga de múltiplos usuários
- Fallback e tratamento de erros
"""

from locust import HttpUser, task, between, events
import random
import time
from typing import Dict, List, Optional, Any

class GoogleTrendsIntegrationUser(HttpUser):
    """
    Usuário simulando integração com Google Trends API
    """
    wait_time = between(1, 3)  # Intervalo entre requisições
    
    def on_start(self):
        """Setup inicial do usuário"""
        self.keywords = [
            "marketing digital", "seo", "python", "javascript", "react",
            "machine learning", "data science", "blockchain", "cloud computing",
            "artificial intelligence", "cybersecurity", "devops", "docker",
            "kubernetes", "microservices", "api", "rest", "graphql"
        ]
        
        self.error_scenarios = [
            "timeout", "erro_autenticacao", "resposta_invalida"
        ]
        
        # Contadores para métricas
        self.success_count = 0
        self.error_count = 0
        self.timeout_count = 0
    
    @task(7)  # 70% das requisições - cenário normal
    def get_google_trends_normal(self):
        """
        Teste de carga normal para Google Trends
        """
        keyword = random.choice(self.keywords)
        params = {
            "termo": f"{keyword}_{int(time.time())}",  # Evita cache
            "regiao": "BR",
            "periodo": random.choice(["1d", "7d", "30d"])
        }
        
        start_time = time.time()
        
        try:
            with self.client.get(
                "/api/externo/google_trends",
                params=params,
                catch_response=True,
                timeout=10
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validações de resposta
                    if "termo" in data and "volume" in data:
                        self.success_count += 1
                        response.success()
                        
                        # Log de sucesso
                        events.request.fire(
                            request_type="GET",
                            name="google_trends_success",
                            response_time=response_time * 1000,
                            response_length=len(response.content),
                            exception=None,
                            context={
                                "keyword": keyword,
                                "params": params,
                                "response_data": data
                            }
                        )
                    else:
                        self.error_count += 1
                        response.failure(f"Resposta inválida: {data}")
                        
                elif response.status_code == 429:
                    self.error_count += 1
                    response.failure("Rate limit exceeded")
                    
                elif response.status_code >= 500:
                    self.error_count += 1
                    response.failure(f"Erro do servidor: {response.status_code}")
                    
                else:
                    self.error_count += 1
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.error_count += 1
            events.request.fire(
                request_type="GET",
                name="google_trends_exception",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "keyword": keyword,
                    "params": params,
                    "error": str(e)
                }
            )
    
    @task(2)  # 20% das requisições - cenários de erro
    def get_google_trends_error_scenarios(self):
        """
        Teste de cenários de erro do Google Trends
        """
        scenario = random.choice(self.error_scenarios)
        keyword = random.choice(self.keywords)
        
        params = {
            "termo": keyword,
            "simular": scenario
        }
        
        start_time = time.time()
        
        try:
            with self.client.get(
                "/api/externo/google_trends",
                params=params,
                catch_response=True,
                timeout=15  # Timeout maior para cenários de erro
            ) as response:
                response_time = time.time() - start_time
                
                if scenario == "timeout":
                    if response.status_code == 503:
                        response.success()
                        self.timeout_count += 1
                    else:
                        response.failure(f"Timeout não simulado corretamente: {response.status_code}")
                        
                elif scenario == "erro_autenticacao":
                    if response.status_code == 401:
                        response.success()
                        self.error_count += 1
                    else:
                        response.failure(f"Erro de autenticação não simulado: {response.status_code}")
                        
                elif scenario == "resposta_invalida":
                    if response.status_code == 502:
                        response.success()
                        self.error_count += 1
                    else:
                        response.failure(f"Resposta inválida não simulado: {response.status_code}")
                        
        except Exception as e:
            self.error_count += 1
            events.request.fire(
                request_type="GET",
                name="google_trends_error_scenario",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "scenario": scenario,
                    "keyword": keyword,
                    "error": str(e)
                }
            )
    
    @task(1)  # 10% das requisições - stress test
    def get_google_trends_stress(self):
        """
        Teste de stress com múltiplas keywords simultâneas
        """
        keywords = random.sample(self.keywords, 3)  # 3 keywords simultâneas
        
        for keyword in keywords:
            params = {
                "termo": f"{keyword}_stress_{int(time.time())}",
                "regiao": random.choice(["BR", "US", "ES"]),
                "periodo": random.choice(["1d", "7d", "30d", "90d"])
            }
            
            start_time = time.time()
            
            try:
                with self.client.get(
                    "/api/externo/google_trends",
                    params=params,
                    catch_response=True,
                    timeout=5
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        self.success_count += 1
                        response.success()
                    else:
                        self.error_count += 1
                        response.failure(f"Stress test falhou: {response.status_code}")
                        
            except Exception as e:
                self.error_count += 1
                events.request.fire(
                    request_type="GET",
                    name="google_trends_stress_exception",
                    response_time=(time.time() - start_time) * 1000,
                    response_length=0,
                    exception=e,
                    context={
                        "keyword": keyword,
                        "params": params,
                        "error": str(e)
                    }
                )
    
    def on_stop(self):
        """Cleanup ao final do teste"""
        # Log de métricas finais
        total_requests = self.success_count + self.error_count + self.timeout_count
        
        if total_requests > 0:
            success_rate = (self.success_count / total_requests) * 100
            error_rate = (self.error_count / total_requests) * 100
            timeout_rate = (self.timeout_count / total_requests) * 100
            
            events.request.fire(
                request_type="METRICS",
                name="google_trends_final_metrics",
                response_time=0,
                response_length=0,
                exception=None,
                context={
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "error_rate": error_rate,
                    "timeout_rate": timeout_rate,
                    "success_count": self.success_count,
                    "error_count": self.error_count,
                    "timeout_count": self.timeout_count
                }
            ) 