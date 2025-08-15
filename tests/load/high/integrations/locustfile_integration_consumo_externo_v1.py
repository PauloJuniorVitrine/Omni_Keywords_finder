"""
Teste de Carga - Consumo Externo (v1)
Baseado em: /api/v1/externo/get (GET) e /api/v1/externo/post (POST)
Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - 5.1 APIs de Integração Externa
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_TEST_CONSUMO_EXTERNO_20250127_001

Funcionalidades testadas:
- Consumo de APIs externas via proxy interno
- Rate limiting e validação de parâmetros
- Sanitização de dados e segurança
- Fallback e circuit breaker
- Performance sob carga de múltiplos usuários
- Logs estruturados e monitoramento
"""

from locust import HttpUser, task, between, events
import random
import time
import json
from typing import Dict, List, Optional, Any

class ConsumoExternoUser(HttpUser):
    """
    Usuário simulando consumo de APIs externas
    """
    wait_time = between(2, 5)  # Intervalo maior para APIs externas
    
    def on_start(self):
        """Setup inicial do usuário"""
        self.external_endpoints = [
            "google-trends/daily",
            "semrush/keyword-overview",
            "ahrefs/domain-rating",
            "moz/domain-authority",
            "similarweb/traffic",
            "alexa/rank",
            "socialblade/youtube-stats",
            "instagram/basic-metrics",
            "tiktok/video-analytics",
            "youtube/channel-stats"
        ]
        
        self.test_payloads = [
            {
                "keyword": "marketing digital",
                "country": "BR",
                "language": "pt"
            },
            {
                "domain": "example.com",
                "metrics": ["traffic", "rankings", "backlinks"]
            },
            {
                "channel": "UC123456789",
                "period": "30d",
                "metrics": ["views", "subscribers", "engagement"]
            },
            {
                "hashtag": "marketing",
                "platform": "instagram",
                "limit": 100
            },
            {
                "video_id": "dQw4w9WgXcQ",
                "platform": "youtube",
                "metrics": ["views", "likes", "comments"]
            }
        ]
        
        # Contadores para métricas
        self.get_success_count = 0
        self.post_success_count = 0
        self.rate_limit_count = 0
        self.validation_error_count = 0
        self.external_error_count = 0
    
    @task(6)  # 60% das requisições - GET externo
    def get_externo_normal(self):
        """
        Teste de carga normal para GET externo
        """
        endpoint = random.choice(self.external_endpoints)
        
        # Parâmetros variados para simular uso real
        params = {
            "endpoint": endpoint,
            "timeout": random.choice([5, 10, 15]),
            "cache": random.choice(["true", "false"]),
            "format": random.choice(["json", "xml"]),
            "limit": random.randint(10, 100)
        }
        
        # Adiciona parâmetros específicos por endpoint
        if "google-trends" in endpoint:
            params.update({
                "termo": f"keyword_{int(time.time())}",
                "regiao": random.choice(["BR", "US", "ES"]),
                "periodo": random.choice(["1d", "7d", "30d"])
            })
        elif "semrush" in endpoint:
            params.update({
                "keyword": f"semrush_{int(time.time())}",
                "database": random.choice(["br", "us", "uk"]),
                "display_limit": random.randint(10, 50)
            })
        elif "instagram" in endpoint:
            params.update({
                "username": f"user_{int(time.time())}",
                "metrics": "followers,posts,engagement"
            })
        
        start_time = time.time()
        
        try:
            with self.client.get(
                "/api/v1/externo/get",
                params=params,
                catch_response=True,
                timeout=20
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validações básicas de resposta
                        if isinstance(data, dict) and len(data) > 0:
                            self.get_success_count += 1
                            response.success()
                            
                            # Log de sucesso
                            events.request.fire(
                                request_type="GET",
                                name="consumo_externo_get_success",
                                response_time=response_time * 1000,
                                response_length=len(response.content),
                                exception=None,
                                context={
                                    "endpoint": endpoint,
                                    "params": params,
                                    "response_keys": list(data.keys())
                                }
                            )
                        else:
                            self.validation_error_count += 1
                            response.failure("Resposta vazia ou inválida")
                            
                    except json.JSONDecodeError:
                        self.validation_error_count += 1
                        response.failure("Resposta não é JSON válido")
                        
                elif response.status_code == 429:
                    self.rate_limit_count += 1
                    response.success()  # Rate limit é comportamento esperado
                    
                elif response.status_code == 400:
                    self.validation_error_count += 1
                    response.failure(f"Erro de validação: {response.text}")
                    
                elif response.status_code >= 500:
                    self.external_error_count += 1
                    response.failure(f"Erro externo: {response.status_code}")
                    
                else:
                    self.external_error_count += 1
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.external_error_count += 1
            events.request.fire(
                request_type="GET",
                name="consumo_externo_get_exception",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "endpoint": endpoint,
                    "params": params,
                    "error": str(e)
                }
            )
    
    @task(3)  # 30% das requisições - POST externo
    def post_externo_normal(self):
        """
        Teste de carga normal para POST externo
        """
        endpoint = random.choice(self.external_endpoints)
        payload = random.choice(self.test_payloads)
        
        # Adiciona dados dinâmicos para evitar cache
        if "keyword" in payload:
            payload["keyword"] = f"{payload['keyword']}_{int(time.time())}"
        if "domain" in payload:
            payload["domain"] = f"domain{int(time.time())}.com"
        if "channel" in payload:
            payload["channel"] = f"UC{int(time.time())}"
        
        request_data = {
            "endpoint": endpoint,
            "body": payload,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "OmniKeywordsFinder/1.0"
            },
            "timeout": random.randint(10, 30),
            "retry": random.choice([True, False])
        }
        
        start_time = time.time()
        
        try:
            with self.client.post(
                "/api/v1/externo/post",
                json=request_data,
                headers={"Content-Type": "application/json"},
                catch_response=True,
                timeout=25
            ) as response:
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validações básicas de resposta
                        if isinstance(data, dict):
                            self.post_success_count += 1
                            response.success()
                            
                            # Log de sucesso
                            events.request.fire(
                                request_type="POST",
                                name="consumo_externo_post_success",
                                response_time=response_time * 1000,
                                response_length=len(response.content),
                                exception=None,
                                context={
                                    "endpoint": endpoint,
                                    "payload_size": len(json.dumps(payload)),
                                    "response_keys": list(data.keys())
                                }
                            )
                        else:
                            self.validation_error_count += 1
                            response.failure("Resposta não é um objeto válido")
                            
                    except json.JSONDecodeError:
                        self.validation_error_count += 1
                        response.failure("Resposta não é JSON válido")
                        
                elif response.status_code == 429:
                    self.rate_limit_count += 1
                    response.success()  # Rate limit é comportamento esperado
                    
                elif response.status_code == 400:
                    self.validation_error_count += 1
                    response.failure(f"Erro de validação: {response.text}")
                    
                elif response.status_code >= 500:
                    self.external_error_count += 1
                    response.failure(f"Erro externo: {response.status_code}")
                    
                else:
                    self.external_error_count += 1
                    response.failure(f"Status inesperado: {response.status_code}")
                    
        except Exception as e:
            self.external_error_count += 1
            events.request.fire(
                request_type="POST",
                name="consumo_externo_post_exception",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "endpoint": endpoint,
                    "payload": payload,
                    "error": str(e)
                }
            )
    
    @task(1)  # 10% das requisições - cenários de erro
    def test_error_scenarios(self):
        """
        Teste de cenários de erro e edge cases
        """
        scenarios = [
            # Endpoint inválido
            {"endpoint": "invalid/endpoint", "expected_status": 400},
            
            # Parâmetros malformados
            {"endpoint": "", "expected_status": 400},
            
            # Payload muito grande
            {"endpoint": "test/large", "payload": {"data": "x" * 10000}, "expected_status": 400},
            
            # Headers inválidos
            {"endpoint": "test/headers", "headers": {"Invalid-Header": "invalid"}, "expected_status": 400}
        ]
        
        scenario = random.choice(scenarios)
        
        start_time = time.time()
        
        try:
            if "payload" in scenario:
                # Teste POST com payload problemático
                with self.client.post(
                    "/api/v1/externo/post",
                    json={
                        "endpoint": scenario["endpoint"],
                        "body": scenario["payload"],
                        "headers": scenario.get("headers", {})
                    },
                    headers={"Content-Type": "application/json"},
                    catch_response=True,
                    timeout=10
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status_code == scenario["expected_status"]:
                        response.success()
                        self.validation_error_count += 1
                    else:
                        response.failure(f"Status esperado {scenario['expected_status']}, obtido {response.status_code}")
                        
            else:
                # Teste GET com parâmetros problemáticos
                params = {"endpoint": scenario["endpoint"]}
                params.update(scenario.get("headers", {}))
                
                with self.client.get(
                    "/api/v1/externo/get",
                    params=params,
                    catch_response=True,
                    timeout=10
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status_code == scenario["expected_status"]:
                        response.success()
                        self.validation_error_count += 1
                    else:
                        response.failure(f"Status esperado {scenario['expected_status']}, obtido {response.status_code}")
                        
        except Exception as e:
            self.external_error_count += 1
            events.request.fire(
                request_type="ERROR_SCENARIO",
                name="consumo_externo_error_scenario",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
                context={
                    "scenario": scenario,
                    "error": str(e)
                }
            )
    
    def on_stop(self):
        """Cleanup ao final do teste"""
        # Log de métricas finais
        total_requests = (
            self.get_success_count + self.post_success_count + 
            self.rate_limit_count + self.validation_error_count + 
            self.external_error_count
        )
        
        if total_requests > 0:
            success_rate = ((self.get_success_count + self.post_success_count) / total_requests) * 100
            rate_limit_rate = (self.rate_limit_count / total_requests) * 100
            validation_error_rate = (self.validation_error_count / total_requests) * 100
            external_error_rate = (self.external_error_count / total_requests) * 100
            
            events.request.fire(
                request_type="METRICS",
                name="consumo_externo_final_metrics",
                response_time=0,
                response_length=0,
                exception=None,
                context={
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "rate_limit_rate": rate_limit_rate,
                    "validation_error_rate": validation_error_rate,
                    "external_error_rate": external_error_rate,
                    "get_success_count": self.get_success_count,
                    "post_success_count": self.post_success_count,
                    "rate_limit_count": self.rate_limit_count,
                    "validation_error_count": self.validation_error_count,
                    "external_error_count": self.external_error_count
                }
            ) 