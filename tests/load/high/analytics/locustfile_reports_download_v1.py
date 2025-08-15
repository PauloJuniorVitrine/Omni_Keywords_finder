"""
Teste de Carga - Download de Relatórios (v1)
Baseado em: /api/reports/download (GET)
Endpoint: Download de relatórios gerados

Tracing ID: LOAD_TEST_REPORTS_DOWNLOAD_20250127_001
Data/Hora: 2025-01-27 19:30:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades testadas:
- Download de relatórios em diferentes formatos
- Download de relatórios por ID
- Download de relatórios agendados
- Download de relatórios em lote
- Validação de arquivos baixados
- Controle de acesso a downloads
"""

import json
import random
import time
import hashlib
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from typing import Dict, Any, List, Optional

class ReportsDownloadUser(HttpUser):
    """
    Usuário simulando download de relatórios
    """
    wait_time = between(2, 6)
    
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
        self.report_formats = ["pdf", "csv", "json", "excel", "html", "markdown"]
        
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
        
        # IDs de relatórios simulados baseados no código real
        self.report_ids = [
            f"report_{random.randint(10000, 99999)}",
            f"report_{random.randint(10000, 99999)}",
            f"report_{random.randint(10000, 99999)}",
            f"report_{random.randint(10000, 99999)}",
            f"report_{random.randint(10000, 99999)}"
        ]
        
        # Configurações de download baseadas no código real
        self.download_configs = {
            "pdf": {
                "mime_type": "application/pdf",
                "file_extension": ".pdf",
                "expected_size_range": (50000, 5000000),  # 50KB - 5MB
                "compression": False
            },
            "csv": {
                "mime_type": "text/csv",
                "file_extension": ".csv",
                "expected_size_range": (1000, 100000),  # 1KB - 100KB
                "compression": True
            },
            "json": {
                "mime_type": "application/json",
                "file_extension": ".json",
                "expected_size_range": (2000, 200000),  # 2KB - 200KB
                "compression": True
            },
            "excel": {
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "file_extension": ".xlsx",
                "expected_size_range": (10000, 1000000),  # 10KB - 1MB
                "compression": False
            },
            "html": {
                "mime_type": "text/html",
                "file_extension": ".html",
                "expected_size_range": (5000, 500000),  # 5KB - 500KB
                "compression": True
            },
            "markdown": {
                "mime_type": "text/markdown",
                "file_extension": ".md",
                "expected_size_range": (1000, 100000),  # 1KB - 100KB
                "compression": True
            }
        }

    @task(5)
    def download_report_normal(self):
        """
        Teste de download normal de relatórios
        Baseado em: backend/app/api/auditoria.py
        """
        try:
            # Parâmetros aleatórios baseados no código real
            report_id = random.choice(self.report_ids)
            report_format = random.choice(self.report_formats)
            report_type = random.choice(self.report_types)
            
            # Configuração baseada no formato
            config = self.download_configs[report_format]
            
            # Construir endpoint baseado no código real
            endpoint = f"/api/reports/download/{report_id}"
            
            # Parâmetros de query baseados no código real
            params = {
                "format": report_format,
                "type": report_type,
                "compression": config["compression"],
                "include_metadata": random.choice([True, False]),
                "include_charts": random.choice([True, False]),
                "watermark": random.choice([True, False])
            }
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="reports_download_normal",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Validar resposta baseada no código real
                    content_type = response.headers.get("Content-Type", "")
                    content_length = int(response.headers.get("Content-Length", 0))
                    
                    # Validar tipo MIME
                    if config["mime_type"] in content_type:
                        # Validar tamanho do arquivo
                        min_size, max_size = config["expected_size_range"]
                        if min_size <= content_length <= max_size:
                            response.success()
                            self._log_download_metrics(response, "normal", report_format, content_length)
                        else:
                            response.failure(f"Tamanho do arquivo inválido: {content_length} bytes")
                    else:
                        response.failure(f"Tipo MIME inválido: {content_type}")
                        
                elif response.status_code == 202:
                    # Aceito para processamento assíncrono
                    response.success()
                    self._log_download_metrics(response, "normal", report_format, 0)
                elif response.status_code == 404:
                    response.success()  # Relatório não encontrado é válido
                elif response.status_code == 401:
                    response.failure("Erro de autenticação")
                elif response.status_code == 403:
                    response.failure("Acesso negado")
                elif response.status_code == 429:
                    response.failure("Rate limit excedido")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="reports_download_normal_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def download_report_batch(self):
        """
        Teste de download em lote de relatórios
        Baseado em: backend/app/api/template_management.py
        """
        try:
            # Parâmetros para download em lote
            batch_size = random.randint(2, 5)
            report_format = random.choice(self.report_formats)
            
            # IDs de relatórios para download em lote
            batch_report_ids = random.sample(self.report_ids, min(batch_size, len(self.report_ids)))
            
            # Endpoint para download em lote
            endpoint = "/api/reports/download/batch"
            
            # Payload baseado no código real
            payload = {
                "report_ids": batch_report_ids,
                "format": report_format,
                "options": {
                    "compression": True,
                    "include_metadata": True,
                    "watermark": False,
                    "password_protected": False
                }
            }
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_download_batch",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "download_url" in data.get("data", {}):
                            response.success()
                            self._log_download_metrics(response, "batch", report_format, len(batch_report_ids))
                        else:
                            response.failure(f"Resposta de lote inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de lote não é JSON válido")
                elif response.status_code == 202:
                    # Aceito para processamento assíncrono
                    response.success()
                    self._log_download_metrics(response, "batch", report_format, len(batch_report_ids))
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_download_batch_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def download_report_scheduled(self):
        """
        Teste de download de relatórios agendados
        Baseado em: infrastructure/monitoring/alerts.yaml
        """
        try:
            # Parâmetros para relatórios agendados
            schedule_id = f"schedule_{random.randint(1000, 9999)}"
            report_format = random.choice(self.report_formats)
            
            # Endpoint para download de relatório agendado
            endpoint = f"/api/reports/download/scheduled/{schedule_id}"
            
            # Parâmetros de query
            params = {
                "format": report_format,
                "include_attachments": random.choice([True, False]),
                "include_summary": True,
                "include_details": random.choice([True, False])
            }
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="reports_download_scheduled",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Validar resposta
                    content_type = response.headers.get("Content-Type", "")
                    content_length = int(response.headers.get("Content-Length", 0))
                    
                    config = self.download_configs[report_format]
                    if config["mime_type"] in content_type and content_length > 0:
                        response.success()
                        self._log_download_metrics(response, "scheduled", report_format, content_length)
                    else:
                        response.failure(f"Resposta inválida: {content_type}, {content_length}")
                elif response.status_code == 404:
                    response.success()  # Agendamento não encontrado é válido
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="reports_download_scheduled_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def download_report_by_type(self):
        """
        Teste de download de relatórios por tipo
        Baseado em: backend/app/api/advanced_analytics.py
        """
        try:
            # Parâmetros para download por tipo
            report_type = random.choice(self.report_types)
            report_format = random.choice(self.report_formats)
            time_range = random.choice(["1d", "7d", "30d", "90d", "1y"])
            
            # Endpoint para download por tipo
            endpoint = f"/api/reports/download/type/{report_type}"
            
            # Parâmetros de query baseados no código real
            params = {
                "format": report_format,
                "time_range": time_range,
                "category": random.choice(["all", "ecommerce", "saas", "blog", "news"]),
                "nicho": random.choice(["all", "tech", "health", "finance", "education"]),
                "include_charts": random.choice([True, False]),
                "include_recommendations": random.choice([True, False])
            }
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="reports_download_by_type",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Validar resposta
                    content_type = response.headers.get("Content-Type", "")
                    content_length = int(response.headers.get("Content-Length", 0))
                    
                    config = self.download_configs[report_format]
                    if config["mime_type"] in content_type and content_length > 0:
                        response.success()
                        self._log_download_metrics(response, "by_type", report_format, content_length)
                    else:
                        response.failure(f"Resposta inválida: {content_type}, {content_length}")
                elif response.status_code == 202:
                    response.success()
                    self._log_download_metrics(response, "by_type", report_format, 0)
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="reports_download_by_type_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def download_report_large(self):
        """
        Teste de download de relatórios grandes
        Baseado em: scripts/compliance/generate_compliance_report.py
        """
        try:
            # Parâmetros para relatórios grandes
            report_format = random.choice(["pdf", "excel", "html"])
            report_type = random.choice(["compliance_report", "security_audit", "business_metrics"])
            
            # Endpoint para download de relatório grande
            endpoint = "/api/reports/download/large"
            
            # Parâmetros baseados no código real
            params = {
                "format": report_format,
                "type": report_type,
                "time_range": "1y",  # Período longo
                "include_all_data": True,
                "high_resolution": True,
                "include_attachments": True,
                "include_metadata": True,
                "include_summary": True,
                "include_details": True
            }
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="reports_download_large",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Validar resposta para arquivo grande
                    content_type = response.headers.get("Content-Type", "")
                    content_length = int(response.headers.get("Content-Length", 0))
                    
                    config = self.download_configs[report_format]
                    if config["mime_type"] in content_type and content_length > 100000:  # > 100KB
                        response.success()
                        self._log_download_metrics(response, "large", report_format, content_length)
                    else:
                        response.failure(f"Arquivo não é grande o suficiente: {content_length} bytes")
                elif response.status_code == 202:
                    response.success()
                    self._log_download_metrics(response, "large", report_format, 0)
                elif response.status_code == 413:
                    response.success()  # Payload muito grande é válido
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="reports_download_large_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def download_report_error_scenarios(self):
        """
        Teste de cenários de erro para download
        """
        try:
            # Cenários de erro baseados no código real
            error_scenarios = [
                # ID inválido
                {
                    "endpoint": "/api/reports/download/invalid_id",
                    "params": {"format": "pdf"}
                },
                # Formato inválido
                {
                    "endpoint": "/api/reports/download/report_123",
                    "params": {"format": "invalid_format"}
                },
                # Parâmetros ausentes
                {
                    "endpoint": "/api/reports/download/report_123",
                    "params": {}
                },
                # Relatório não encontrado
                {
                    "endpoint": "/api/reports/download/nonexistent_report",
                    "params": {"format": "pdf"}
                },
                # Acesso negado
                {
                    "endpoint": "/api/reports/download/restricted_report",
                    "params": {"format": "pdf"}
                }
            ]
            
            scenario = random.choice(error_scenarios)
            
            with self.client.get(
                scenario["endpoint"],
                params=scenario["params"],
                headers=self.headers,
                name="reports_download_error_scenario",
                catch_response=True
            ) as response:
                # Esperamos erro 400, 404, 403 para cenários inválidos
                if response.status_code in [400, 404, 403]:
                    response.success()
                elif response.status_code == 401:
                    response.success()  # Erro de auth esperado
                else:
                    response.failure(f"Status code inesperado para erro: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="reports_download_error_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def download_report_stress(self):
        """
        Teste de stress para download de relatórios
        """
        try:
            # Parâmetros de stress
            report_format = "pdf"  # Formato mais pesado
            report_type = random.choice(["compliance_report", "security_audit", "business_metrics"])
            
            # Endpoint para download
            endpoint = "/api/reports/download/stress"
            
            # Parâmetros de stress
            params = {
                "format": report_format,
                "type": report_type,
                "time_range": "1y",
                "include_all_data": True,
                "high_resolution": True,
                "include_attachments": True,
                "include_metadata": True,
                "include_summary": True,
                "include_details": True,
                "include_charts": True,
                "include_recommendations": True,
                "watermark": True,
                "password_protected": True
            }
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="reports_download_stress",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Validar resposta de stress
                    content_type = response.headers.get("Content-Type", "")
                    content_length = int(response.headers.get("Content-Length", 0))
                    
                    config = self.download_configs[report_format]
                    if config["mime_type"] in content_type and content_length > 500000:  # > 500KB
                        response.success()
                        self._log_download_metrics(response, "stress", report_format, content_length)
                    else:
                        response.failure(f"Arquivo de stress não é grande o suficiente: {content_length} bytes")
                elif response.status_code == 202:
                    response.success()
                    self._log_download_metrics(response, "stress", report_format, 0)
                elif response.status_code == 429:
                    response.success()  # Rate limit esperado em stress
                elif response.status_code == 413:
                    response.success()  # Payload muito grande esperado
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="reports_download_stress_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    def _log_download_metrics(self, response, test_type: str, report_format: str, content_length: int):
        """
        Log de métricas específicas de download
        Baseado no código real de download
        """
        try:
            # Métricas baseadas no código real
            metrics = {
                "test_type": test_type,
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "report_format": report_format,
                "content_length": content_length,
                "content_type": response.headers.get("Content-Type", ""),
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds() * 1000,  # ms
                "download_speed": content_length / (response.elapsed.total_seconds() * 1000) if response.elapsed.total_seconds() > 0 else 0,  # bytes/ms
                "compression_enabled": "gzip" in response.headers.get("Content-Encoding", ""),
                "cache_headers": {
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "cache_control": response.headers.get("Cache-Control")
                }
            }
            
            # Log estruturado
            self.client.environment.events.request.fire(
                request_type="METRICS",
                name="reports_download_metrics",
                response_time=0,
                response_length=len(json.dumps(metrics)),
                exception=None,
                context={"metrics": metrics}
            )
            
        except Exception as e:
            # Log de erro nas métricas
            self.client.environment.events.request.fire(
                request_type="METRICS_ERROR",
                name="reports_download_metrics_error",
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
        name="reports_download_test_start",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "reports_download",
            "start_time": datetime.now().isoformat(),
            "description": "Teste de carga para Download de Relatórios API"
        }
    )

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Finalização do teste"""
    environment.events.request.fire(
        request_type="TEST_STOP",
        name="reports_download_test_stop",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "reports_download",
            "end_time": datetime.now().isoformat(),
            "description": "Teste de carga para Download de Relatórios API finalizado"
        }
    )

# Configuração de métricas finais
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context=None, **kwargs):
    """Listener para métricas de request"""
    if "reports_download" in name:
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
        # print(f"REPORTS_DOWNLOAD_METRIC: {json.dumps(log_data)}") 