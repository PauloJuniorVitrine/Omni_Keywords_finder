"""
Teste de Carga - Geração de Relatórios (v1)
Baseado em: /api/reports/generate (POST)
Endpoint: Geração de relatórios em diferentes formatos

Tracing ID: LOAD_TEST_REPORTS_GENERATE_20250127_001
Data/Hora: 2025-01-27 19:00:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades testadas:
- Geração de relatórios de analytics
- Geração de relatórios de execução
- Geração de relatórios de compliance
- Geração de relatórios de performance
- Exportação em múltiplos formatos
- Agendamento de relatórios
"""

import json
import random
import time
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from typing import Dict, Any, List

class ReportsGenerateUser(HttpUser):
    """
    Usuário simulando geração de relatórios
    """
    wait_time = between(3, 8)
    
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
        self.report_types = [
            "analytics_summary",
            "execution_report", 
            "compliance_report",
            "performance_report",
            "business_metrics",
            "security_audit",
            "user_activity",
            "system_health"
        ]
        
        self.report_formats = ["pdf", "csv", "json", "excel", "html", "markdown"]
        
        self.time_ranges = ["1d", "7d", "30d", "90d", "1y"]
        
        # Dados de teste baseados no código real
        self.report_configs = {
            "analytics_summary": {
                "sections": ["keywords_performance", "clusters_efficiency", "user_behavior", "predictive_insights"],
                "include_charts": True,
                "include_recommendations": True,
                "max_data_points": 1000
            },
            "execution_report": {
                "sections": ["execution_summary", "performance_metrics", "error_analysis", "resource_usage"],
                "include_logs": True,
                "include_timeline": True,
                "max_executions": 500
            },
            "compliance_report": {
                "sections": ["security_checks", "data_protection", "access_controls", "audit_trail"],
                "include_violations": True,
                "include_recommendations": True,
                "compliance_frameworks": ["PCI-DSS", "LGPD", "ISO-27001"]
            },
            "performance_report": {
                "sections": ["response_times", "throughput", "error_rates", "resource_utilization"],
                "include_trends": True,
                "include_alerts": True,
                "time_granularity": "hourly"
            },
            "business_metrics": {
                "sections": ["revenue", "conversions", "user_engagement", "roi_analysis"],
                "include_forecasts": True,
                "include_benchmarks": True,
                "currency": "BRL"
            },
            "security_audit": {
                "sections": ["vulnerability_scan", "access_review", "incident_analysis", "threat_assessment"],
                "include_risk_scores": True,
                "include_remediation": True,
                "severity_levels": ["low", "medium", "high", "critical"]
            },
            "user_activity": {
                "sections": ["login_patterns", "feature_usage", "session_analysis", "engagement_metrics"],
                "include_heatmaps": True,
                "include_segments": True,
                "privacy_compliant": True
            },
            "system_health": {
                "sections": ["infrastructure_status", "service_health", "capacity_analysis", "maintenance_schedule"],
                "include_alerts": True,
                "include_metrics": True,
                "monitoring_interval": "5m"
            }
        }

    @task(4)
    def generate_report_normal(self):
        """
        Teste de carga normal para geração de relatórios
        Baseado em: backend/app/api/template_export.py
        """
        try:
            # Parâmetros aleatórios baseados no código real
            report_type = random.choice(self.report_types)
            report_format = random.choice(self.report_formats)
            time_range = random.choice(self.time_ranges)
            
            # Configuração baseada no tipo de relatório
            config = self.report_configs[report_type].copy()
            
            # Construir payload baseado no código real
            payload = {
                "report_type": report_type,
                "format": report_format,
                "time_range": time_range,
                "sections": config["sections"],
                "include_charts": config.get("include_charts", False),
                "include_recommendations": config.get("include_recommendations", False),
                "filters": {
                    "category": random.choice(["all", "ecommerce", "saas", "blog", "news"]),
                    "nicho": random.choice(["all", "tech", "health", "finance", "education"]),
                    "user_id": self.user_id
                },
                "options": {
                    "compression": random.choice([True, False]),
                    "watermark": random.choice([True, False]),
                    "password_protected": False,
                    "expires_in": random.choice([None, 3600, 86400, 604800])  # 1h, 1d, 1w
                }
            }
            
            # Endpoint baseado no padrão do sistema
            endpoint = "/api/reports/generate"
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_generate_normal",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "report_id" in data.get("data", {}):
                            response.success()
                            self._log_report_metrics(data, "normal", report_type, report_format)
                        else:
                            response.failure(f"Resposta inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta não é JSON válido")
                elif response.status_code == 202:
                    # Aceito para processamento assíncrono
                    response.success()
                    self._log_report_metrics({"status": "accepted"}, "normal", report_type, report_format)
                elif response.status_code == 401:
                    response.failure("Erro de autenticação")
                elif response.status_code == 429:
                    response.failure("Rate limit excedido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_generate_normal_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def generate_report_complex(self):
        """
        Teste de geração de relatórios complexos
        Baseado em: scripts/compliance/generate_compliance_report.py
        """
        try:
            # Parâmetros para relatório complexo
            report_type = random.choice(["compliance_report", "security_audit", "business_metrics"])
            report_format = random.choice(["pdf", "excel", "html"])
            
            # Configuração complexa
            config = self.report_configs[report_type].copy()
            
            # Payload complexo
            payload = {
                "report_type": report_type,
                "format": report_format,
                "time_range": random.choice(["30d", "90d", "1y"]),
                "sections": config["sections"],
                "include_charts": True,
                "include_recommendations": True,
                "include_trends": True,
                "include_forecasts": True,
                "filters": {
                    "category": "all",
                    "nicho": "all",
                    "user_id": self.user_id,
                    "include_historical": True,
                    "include_comparison": True
                },
                "options": {
                    "compression": True,
                    "watermark": True,
                    "password_protected": random.choice([True, False]),
                    "expires_in": 604800,  # 1 semana
                    "include_metadata": True,
                    "include_summary": True,
                    "include_details": True
                },
                "customizations": {
                    "theme": random.choice(["default", "dark", "light", "corporate"]),
                    "language": random.choice(["pt-BR", "en-US", "es-ES"]),
                    "timezone": random.choice(["America/Sao_Paulo", "UTC", "Europe/London"]),
                    "currency": random.choice(["BRL", "USD", "EUR"])
                }
            }
            
            endpoint = "/api/reports/generate"
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_generate_complex",
                catch_response=True
            ) as response:
                if response.status_code in [200, 202]:
                    try:
                        data = response.json()
                        if data.get("success") or data.get("status") == "accepted":
                            response.success()
                            self._log_report_metrics(data, "complex", report_type, report_format)
                        else:
                            response.failure(f"Resposta complexa inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta complexa não é JSON válido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_generate_complex_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def generate_report_batch(self):
        """
        Teste de geração de relatórios em lote
        Baseado em: backend/app/api/execucoes.py
        """
        try:
            # Gerar múltiplos relatórios
            batch_size = random.randint(2, 5)
            reports = []
            
            for i in range(batch_size):
                report_type = random.choice(self.report_types)
                report_format = random.choice(self.report_formats)
                
                reports.append({
                    "report_type": report_type,
                    "format": report_format,
                    "time_range": random.choice(self.time_ranges),
                    "sections": self.report_configs[report_type]["sections"][:2],  # Apenas 2 seções
                    "filters": {
                        "category": "all",
                        "nicho": "all",
                        "user_id": self.user_id
                    },
                    "options": {
                        "compression": False,
                        "watermark": False,
                        "password_protected": False
                    }
                })
            
            payload = {
                "batch_id": f"batch_{int(time.time())}_{random.randint(1000, 9999)}",
                "reports": reports,
                "options": {
                    "parallel_processing": random.choice([True, False]),
                    "notify_completion": True,
                    "compress_batch": True
                }
            }
            
            endpoint = "/api/reports/generate/batch"
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_generate_batch",
                catch_response=True
            ) as response:
                if response.status_code in [200, 202]:
                    try:
                        data = response.json()
                        if data.get("success") or data.get("status") == "accepted":
                            response.success()
                            self._log_report_metrics(data, "batch", f"{batch_size}_reports", "batch")
                        else:
                            response.failure(f"Resposta de lote inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de lote não é JSON válido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_generate_batch_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def generate_report_scheduled(self):
        """
        Teste de agendamento de relatórios
        Baseado em: infrastructure/monitoring/alerts.yaml
        """
        try:
            # Parâmetros para agendamento
            report_type = random.choice(self.report_types)
            report_format = random.choice(self.report_formats)
            frequency = random.choice(["daily", "weekly", "monthly"])
            
            # Configurar horário baseado na frequência
            if frequency == "daily":
                schedule_time = f"{random.randint(8, 18)}:00"
            elif frequency == "weekly":
                schedule_time = f"{random.randint(9, 17)}:00"
                day_of_week = random.choice(["monday", "tuesday", "wednesday", "thursday", "friday"])
            else:  # monthly
                schedule_time = f"{random.randint(10, 16)}:00"
                day_of_month = random.randint(1, 28)
            
            payload = {
                "report_type": report_type,
                "format": report_format,
                "schedule": {
                    "enabled": True,
                    "frequency": frequency,
                    "time": schedule_time,
                    "timezone": "America/Sao_Paulo",
                    "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    "end_date": (datetime.now() + timedelta(days=30)).isoformat()
                },
                "recipients": [
                    f"user{random.randint(1, 100)}@example.com",
                    f"admin{random.randint(1, 10)}@example.com"
                ],
                "sections": self.report_configs[report_type]["sections"],
                "filters": {
                    "category": "all",
                    "nicho": "all",
                    "user_id": self.user_id
                },
                "options": {
                    "compression": True,
                    "watermark": False,
                    "password_protected": False,
                    "auto_delete_after": random.choice([7, 30, 90])  # dias
                }
            }
            
            # Adicionar parâmetros específicos da frequência
            if frequency == "weekly":
                payload["schedule"]["day_of_week"] = day_of_week
            elif frequency == "monthly":
                payload["schedule"]["day_of_month"] = day_of_month
            
            endpoint = "/api/reports/schedule"
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_schedule",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "schedule_id" in data.get("data", {}):
                            response.success()
                            self._log_report_metrics(data, "scheduled", report_type, frequency)
                        else:
                            response.failure(f"Resposta de agendamento inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de agendamento não é JSON válido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_schedule_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def generate_report_error_scenarios(self):
        """
        Teste de cenários de erro para geração de relatórios
        """
        try:
            # Cenários de erro baseados no código real
            error_scenarios = [
                # Payload inválido
                {
                    "report_type": "invalid_type",
                    "format": "invalid_format",
                    "time_range": "invalid_range"
                },
                # Parâmetros obrigatórios ausentes
                {
                    "format": "pdf"
                },
                # Configuração inválida
                {
                    "report_type": "analytics_summary",
                    "format": "pdf",
                    "sections": ["invalid_section"],
                    "filters": {
                        "invalid_filter": "value"
                    }
                },
                # Time range muito longo
                {
                    "report_type": "analytics_summary",
                    "format": "pdf",
                    "time_range": "10y",
                    "sections": ["keywords_performance"]
                },
                # Payload vazio
                {}
            ]
            
            scenario = random.choice(error_scenarios)
            endpoint = "/api/reports/generate"
            
            with self.client.post(
                endpoint,
                json=scenario,
                headers=self.headers,
                name="reports_generate_error_scenario",
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
                request_type="POST",
                name="reports_generate_error_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def generate_report_stress(self):
        """
        Teste de stress para geração de relatórios
        """
        try:
            # Parâmetros de stress
            report_type = random.choice(["compliance_report", "security_audit", "business_metrics"])
            report_format = "pdf"  # Formato mais pesado
            
            payload = {
                "report_type": report_type,
                "format": report_format,
                "time_range": "1y",  # Período longo
                "sections": self.report_configs[report_type]["sections"],
                "include_charts": True,
                "include_recommendations": True,
                "include_trends": True,
                "include_forecasts": True,
                "include_historical": True,
                "filters": {
                    "category": "all",
                    "nicho": "all",
                    "user_id": self.user_id,
                    "include_all_data": True,
                    "high_resolution": True
                },
                "options": {
                    "compression": False,  # Sem compressão para stress
                    "watermark": True,
                    "password_protected": True,
                    "expires_in": None,  # Sem expiração
                    "include_metadata": True,
                    "include_summary": True,
                    "include_details": True,
                    "include_attachments": True,
                    "high_quality": True
                },
                "customizations": {
                    "theme": "corporate",
                    "language": "pt-BR",
                    "timezone": "America/Sao_Paulo",
                    "currency": "BRL",
                    "include_logos": True,
                    "include_branding": True
                }
            }
            
            endpoint = "/api/reports/generate"
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_generate_stress",
                catch_response=True
            ) as response:
                if response.status_code in [200, 202]:
                    try:
                        data = response.json()
                        if data.get("success") or data.get("status") == "accepted":
                            response.success()
                            self._log_report_metrics(data, "stress", report_type, report_format)
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
                request_type="POST",
                name="reports_generate_stress_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    def _log_report_metrics(self, data: Dict[str, Any], test_type: str, report_type: str, format_type: str):
        """
        Log de métricas específicas de geração de relatórios
        Baseado no código real de relatórios
        """
        try:
            report_data = data.get("data", {})
            
            # Métricas baseadas no código real
            metrics = {
                "test_type": test_type,
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "report_type": report_type,
                "format": format_type,
                "report_id": report_data.get("report_id"),
                "schedule_id": report_data.get("schedule_id"),
                "status": report_data.get("status", "unknown"),
                "estimated_size": report_data.get("estimated_size"),
                "processing_time": report_data.get("processing_time"),
                "sections_count": len(self.report_configs.get(report_type, {}).get("sections", [])),
                "has_charts": report_data.get("include_charts", False),
                "has_recommendations": report_data.get("include_recommendations", False),
                "compression_enabled": report_data.get("compression", False),
                "watermark_enabled": report_data.get("watermark", False)
            }
            
            # Log estruturado
            self.client.environment.events.request.fire(
                request_type="METRICS",
                name="reports_generate_metrics",
                response_time=0,
                response_length=len(json.dumps(metrics)),
                exception=None,
                context={"metrics": metrics}
            )
            
        except Exception as e:
            # Log de erro nas métricas
            self.client.environment.events.request.fire(
                request_type="METRICS_ERROR",
                name="reports_generate_metrics_error",
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
        name="reports_generate_test_start",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "reports_generate",
            "start_time": datetime.now().isoformat(),
            "description": "Teste de carga para Geração de Relatórios API"
        }
    )

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Finalização do teste"""
    environment.events.request.fire(
        request_type="TEST_STOP",
        name="reports_generate_test_stop",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "reports_generate",
            "end_time": datetime.now().isoformat(),
            "description": "Teste de carga para Geração de Relatórios API finalizado"
        }
    )

# Configuração de métricas finais
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context=None, **kwargs):
    """Listener para métricas de request"""
    if "reports_generate" in name:
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
        # print(f"REPORTS_GENERATE_METRIC: {json.dumps(log_data)}") 