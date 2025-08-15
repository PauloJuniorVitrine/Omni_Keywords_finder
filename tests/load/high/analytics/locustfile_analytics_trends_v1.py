"""
Teste de Carga - Analytics Trends (v1)
Baseado em: /api/v1/analytics/trends (GET)
Endpoint: Análise de tendências de performance e comportamento

Tracing ID: LOAD_TEST_ANALYTICS_TRENDS_20250127_001
Data/Hora: 2025-01-27 18:30:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades testadas:
- Análise de tendências de keywords
- Tendências de performance de clusters
- Tendências de comportamento do usuário
- Insights preditivos de tendências
- Análise sazonal e cíclica
- Detecção de breakpoints em tendências
"""

import json
import random
import time
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from typing import Dict, Any, List

class AnalyticsTrendsUser(HttpUser):
    """
    Usuário simulando análise de tendências de analytics
    """
    wait_time = between(2, 5)
    
    def on_start(self):
        """Inicialização do usuário"""
        self.user_id = f"user_{random.randint(1000, 9999)}"
        self.auth_token = f"Bearer test_token_{self.user_id}"
        self.headers = {
            "Authorization": self.auth_token,
            "Content-Type": "application/json",
            "X-User-ID": self.user_id,
            "X-Request-ID": f"req_{int(time.time())}_{random.randint(1000, 9999)}"
        }
        
        # Parâmetros de teste baseados no código real
        self.time_ranges = ["1d", "7d", "30d", "90d"]
        self.categories = ["all", "ecommerce", "saas", "blog", "news"]
        self.nichos = ["all", "tech", "health", "finance", "education"]
        self.trend_types = ["keywords", "clusters", "users", "revenue", "performance"]
        
        # Dados de teste baseados no código real
        self.trend_filters = {
            "keywords": {
                "metrics": ["search_volume", "ranking", "ctr", "cpc"],
                "granularity": ["hourly", "daily", "weekly"]
            },
            "clusters": {
                "metrics": ["quality", "diversity", "coherence", "performance"],
                "granularity": ["daily", "weekly", "monthly"]
            },
            "users": {
                "metrics": ["engagement", "session_duration", "bounce_rate", "conversion"],
                "granularity": ["hourly", "daily", "weekly"]
            },
            "revenue": {
                "metrics": ["total_revenue", "conversion_rate", "arpu", "ltv"],
                "granularity": ["daily", "weekly", "monthly"]
            },
            "performance": {
                "metrics": ["response_time", "error_rate", "throughput", "availability"],
                "granularity": ["minute", "hourly", "daily"]
            }
        }

    @task(3)
    def get_trends_normal(self):
        """
        Teste de carga normal para análise de tendências
        Baseado em: infrastructure/analytics/advanced_analytics_system.py
        """
        try:
            # Parâmetros aleatórios baseados no código real
            time_range = random.choice(self.time_ranges)
            category = random.choice(self.categories)
            nicho = random.choice(self.nichos)
            trend_type = random.choice(self.trend_types)
            
            # Construir query baseada no código real
            params = {
                "timeRange": time_range,
                "category": category,
                "nicho": nicho,
                "trendType": trend_type,
                "granularity": random.choice(self.trend_filters[trend_type]["granularity"]),
                "metrics": ",".join(random.sample(self.trend_filters[trend_type]["metrics"], 2)),
                "includeSeasonal": random.choice([True, False]),
                "includeCyclical": random.choice([True, False]),
                "detectBreakpoints": random.choice([True, False]),
                "forecastPeriods": random.randint(7, 30)
            }
            
            # Endpoint baseado no padrão do sistema
            endpoint = "/api/v1/analytics/trends"
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="analytics_trends_normal",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "trends" in data.get("data", {}):
                            response.success()
                            self._log_trends_metrics(data, "normal")
                        else:
                            response.failure(f"Resposta inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta não é JSON válido")
                elif response.status_code == 401:
                    response.failure("Erro de autenticação")
                elif response.status_code == 429:
                    response.failure("Rate limit excedido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="analytics_trends_normal_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def get_trends_detailed(self):
        """
        Teste de análise detalhada de tendências
        Baseado em: ml/predictive/trend_forecasting.py
        """
        try:
            # Parâmetros para análise detalhada
            params = {
                "timeRange": random.choice(["30d", "90d"]),
                "category": random.choice(self.categories),
                "nicho": random.choice(self.nichos),
                "trendType": random.choice(self.trend_types),
                "granularity": "daily",
                "metrics": ",".join(self.trend_filters[random.choice(self.trend_types)]["metrics"]),
                "includeSeasonal": True,
                "includeCyclical": True,
                "detectBreakpoints": True,
                "forecastPeriods": 30,
                "confidenceLevel": random.choice([0.8, 0.9, 0.95]),
                "smoothingFactor": random.uniform(0.1, 0.9),
                "minDataPoints": random.randint(10, 50)
            }
            
            endpoint = "/api/v1/analytics/trends/detailed"
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="analytics_trends_detailed",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "detailed_trends" in data.get("data", {}):
                            response.success()
                            self._log_trends_metrics(data, "detailed")
                        else:
                            response.failure(f"Resposta detalhada inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta detalhada não é JSON válido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="analytics_trends_detailed_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def get_trends_forecast(self):
        """
        Teste de previsão de tendências
        Baseado em: ml/predictive/traffic_forecasting.py
        """
        try:
            # Parâmetros para previsão
            params = {
                "timeRange": random.choice(["7d", "30d"]),
                "category": random.choice(self.categories),
                "nicho": random.choice(self.nichos),
                "trendType": random.choice(self.trend_types),
                "forecastPeriods": random.randint(7, 90),
                "forecastMethod": random.choice(["linear", "exponential", "seasonal", "arima"]),
                "confidenceLevel": random.choice([0.8, 0.9, 0.95]),
                "includeUncertainty": True,
                "scenarios": random.choice([1, 3, 5])
            }
            
            endpoint = "/api/v1/analytics/trends/forecast"
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="analytics_trends_forecast",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "forecast" in data.get("data", {}):
                            response.success()
                            self._log_trends_metrics(data, "forecast")
                        else:
                            response.failure(f"Resposta de previsão inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de previsão não é JSON válido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="analytics_trends_forecast_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def get_trends_anomaly(self):
        """
        Teste de detecção de anomalias em tendências
        Baseado em: ml/anomaly/market_changes.py
        """
        try:
            # Parâmetros para detecção de anomalias
            params = {
                "timeRange": random.choice(["7d", "30d"]),
                "category": random.choice(self.categories),
                "nicho": random.choice(self.nichos),
                "trendType": random.choice(self.trend_types),
                "anomalyThreshold": random.uniform(0.05, 0.2),
                "detectionMethod": random.choice(["statistical", "ml", "hybrid"]),
                "sensitivity": random.choice(["low", "medium", "high"]),
                "includeContext": True
            }
            
            endpoint = "/api/v1/analytics/trends/anomaly"
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="analytics_trends_anomaly",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "anomalies" in data.get("data", {}):
                            response.success()
                            self._log_trends_metrics(data, "anomaly")
                        else:
                            response.failure(f"Resposta de anomalia inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de anomalia não é JSON válido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="analytics_trends_anomaly_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def get_trends_error_scenarios(self):
        """
        Teste de cenários de erro para tendências
        """
        try:
            # Cenários de erro baseados no código real
            error_scenarios = [
                # Parâmetros inválidos
                {"timeRange": "invalid", "category": "test"},
                # Range de tempo muito longo
                {"timeRange": "365d", "category": "test"},
                # Métricas inexistentes
                {"timeRange": "7d", "metrics": "invalid_metric"},
                # Granularidade inválida
                {"timeRange": "7d", "granularity": "invalid"},
                # Parâmetros vazios
                {"timeRange": "", "category": ""}
            ]
            
            scenario = random.choice(error_scenarios)
            endpoint = "/api/v1/analytics/trends"
            
            with self.client.get(
                endpoint,
                params=scenario,
                headers=self.headers,
                name="analytics_trends_error_scenario",
                catch_response=True
            ) as response:
                # Esperamos erro 400 para cenários inválidos
                if response.status_code in [400, 422]:
                    response.success()
                elif response.status_code == 401:
                    response.success()  # Erro de auth esperado
                else:
                    response.failure(f"Status code inesperado para erro: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="analytics_trends_error_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def get_trends_stress(self):
        """
        Teste de stress para análise de tendências
        """
        try:
            # Parâmetros de stress
            params = {
                "timeRange": "90d",
                "category": "all",
                "nicho": "all",
                "trendType": "all",
                "granularity": "hourly",
                "metrics": ",".join([
                    "search_volume", "ranking", "ctr", "cpc", "quality", 
                    "diversity", "coherence", "performance", "engagement", 
                    "session_duration", "bounce_rate", "conversion"
                ]),
                "includeSeasonal": True,
                "includeCyclical": True,
                "detectBreakpoints": True,
                "forecastPeriods": 90,
                "confidenceLevel": 0.99,
                "smoothingFactor": 0.1,
                "minDataPoints": 100
            }
            
            endpoint = "/api/v1/analytics/trends"
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="analytics_trends_stress",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success"):
                            response.success()
                            self._log_trends_metrics(data, "stress")
                        else:
                            response.failure(f"Resposta de stress inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de stress não é JSON válido")
                elif response.status_code == 429:
                    response.success()  # Rate limit esperado em stress
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="analytics_trends_stress_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    def _log_trends_metrics(self, data: Dict[str, Any], test_type: str):
        """
        Log de métricas específicas de tendências
        Baseado no código real de analytics
        """
        try:
            trends_data = data.get("data", {}).get("trends", {})
            
            # Métricas baseadas no código real
            metrics = {
                "test_type": test_type,
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "trends_count": len(trends_data.get("trends", [])),
                "has_seasonal": bool(trends_data.get("seasonal_patterns")),
                "has_cyclical": bool(trends_data.get("cyclical_patterns")),
                "has_breakpoints": bool(trends_data.get("breakpoints")),
                "forecast_periods": len(trends_data.get("forecast", [])),
                "confidence_level": trends_data.get("confidence_level", 0),
                "data_points": trends_data.get("data_points_count", 0)
            }
            
            # Log estruturado
            self.client.environment.events.request.fire(
                request_type="METRICS",
                name="analytics_trends_metrics",
                response_time=0,
                response_length=len(json.dumps(metrics)),
                exception=None,
                context={"metrics": metrics}
            )
            
        except Exception as e:
            # Log de erro nas métricas
            self.client.environment.events.request.fire(
                request_type="METRICS_ERROR",
                name="analytics_trends_metrics_error",
                response_time=0,
                response_length=0,
                exception=e
            )

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Inicialização do teste"""
    environment.events.request.fire(
        request_type="TEST_START",
        name="analytics_trends_test_start",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "analytics_trends",
            "start_time": datetime.now().isoformat(),
            "description": "Teste de carga para Analytics Trends API"
        }
    )

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Finalização do teste"""
    environment.events.request.fire(
        request_type="TEST_STOP",
        name="analytics_trends_test_stop",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "analytics_trends",
            "end_time": datetime.now().isoformat(),
            "description": "Teste de carga para Analytics Trends API finalizado"
        }
    )

# Configuração de métricas finais
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context=None, **kwargs):
    """Listener para métricas de request"""
    if "analytics_trends" in name:
        # Log estruturado para análise
        log_data = {
            "request_type": request_type,
            "name": name,
            "response_time": response_time,
            "response_length": response_length,
            "exception": str(exception) if exception else None,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # Aqui você pode enviar para sistema de monitoramento
        # print(f"ANALYTICS_TRENDS_METRIC: {json.dumps(log_data)}") 