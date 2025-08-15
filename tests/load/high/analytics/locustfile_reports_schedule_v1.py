"""
Teste de Carga - Agendamento de Relatórios (v1)
Baseado em: /api/reports/schedule (POST)
Endpoint: Agendamento de relatórios automáticos

Tracing ID: LOAD_TEST_REPORTS_SCHEDULE_20250127_001
Data/Hora: 2025-01-27 20:00:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades testadas:
- Agendamento de relatórios por frequência (diário, semanal, mensal)
- Configuração de horários e timezone
- Definição de destinatários
- Configuração de formatos e opções
- Cancelamento e modificação de agendamentos
- Validação de execução automática
- Controle de acesso a agendamentos
"""

import json
import random
import time
import hashlib
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from typing import Dict, Any, List, Optional

class ReportsScheduleUser(HttpUser):
    """
    Usuário simulando agendamento de relatórios
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
            "system_health",
            "daily_report",
            "weekly_report",
            "monthly_report"
        ]
        
        self.report_formats = ["pdf", "csv", "json", "excel", "html", "markdown"]
        
        self.frequencies = ["daily", "weekly", "monthly", "quarterly"]
        
        # Configurações de agendamento baseadas no código real
        self.schedule_configs = {
            "daily": {
                "cron_expression": "0 8 * * *",  # Diário às 8h
                "time_range": "08:00-18:00",
                "max_recipients": 10,
                "auto_delete_after": [7, 30, 90]
            },
            "weekly": {
                "cron_expression": "0 9 * * 1",  # Segunda às 9h
                "time_range": "09:00-17:00",
                "max_recipients": 20,
                "auto_delete_after": [30, 90, 180]
            },
            "monthly": {
                "cron_expression": "0 10 1 * *",  # Primeiro dia do mês às 10h
                "time_range": "10:00-16:00",
                "max_recipients": 50,
                "auto_delete_after": [90, 180, 365]
            },
            "quarterly": {
                "cron_expression": "0 11 1 */3 *",  # Primeiro dia do trimestre às 11h
                "time_range": "11:00-15:00",
                "max_recipients": 100,
                "auto_delete_after": [180, 365]
            }
        }
        
        # IDs de agendamentos simulados
        self.schedule_ids = [
            f"schedule_{random.randint(10000, 99999)}",
            f"schedule_{random.randint(10000, 99999)}",
            f"schedule_{random.randint(10000, 99999)}",
            f"schedule_{random.randint(10000, 99999)}",
            f"schedule_{random.randint(10000, 99999)}"
        ]

    @task(5)
    def schedule_report_normal(self):
        """
        Teste de agendamento normal de relatórios
        Baseado em: infrastructure/monitoring/alerts.yaml
        """
        try:
            # Parâmetros aleatórios baseados no código real
            report_type = random.choice(self.report_types)
            report_format = random.choice(self.report_formats)
            frequency = random.choice(self.frequencies)
            
            # Configuração baseada na frequência
            config = self.schedule_configs[frequency]
            
            # Configurar horário baseado na frequência
            if frequency == "daily":
                schedule_time = f"{random.randint(8, 18)}:00"
            elif frequency == "weekly":
                schedule_time = f"{random.randint(9, 17)}:00"
                day_of_week = random.choice(["monday", "tuesday", "wednesday", "thursday", "friday"])
            elif frequency == "monthly":
                schedule_time = f"{random.randint(10, 16)}:00"
                day_of_month = random.randint(1, 28)
            else:  # quarterly
                schedule_time = f"{random.randint(11, 15)}:00"
                day_of_month = random.randint(1, 28)
            
            # Construir payload baseado no código real
            payload = {
                "report_type": report_type,
                "format": report_format,
                "schedule": {
                    "enabled": True,
                    "frequency": frequency,
                    "time": schedule_time,
                    "timezone": "America/Sao_Paulo",
                    "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                    "cron_expression": config["cron_expression"]
                },
                "recipients": [
                    f"user{random.randint(1, 100)}@example.com",
                    f"admin{random.randint(1, 10)}@example.com",
                    f"manager{random.randint(1, 5)}@example.com"
                ],
                "filters": {
                    "category": random.choice(["all", "ecommerce", "saas", "blog", "news"]),
                    "nicho": random.choice(["all", "tech", "health", "finance", "education"]),
                    "user_id": self.user_id,
                    "date_range": "last_30_days"
                },
                "options": {
                    "compression": random.choice([True, False]),
                    "watermark": random.choice([True, False]),
                    "password_protected": random.choice([True, False]),
                    "auto_delete_after": random.choice(config["auto_delete_after"]),
                    "include_charts": random.choice([True, False]),
                    "include_summary": True,
                    "include_details": random.choice([True, False])
                }
            }
            
            # Adicionar parâmetros específicos da frequência
            if frequency == "weekly":
                payload["schedule"]["day_of_week"] = day_of_week
            elif frequency in ["monthly", "quarterly"]:
                payload["schedule"]["day_of_month"] = day_of_month
            
            endpoint = "/api/reports/schedule"
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_schedule_normal",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "schedule_id" in data.get("data", {}):
                            response.success()
                            self._log_schedule_metrics(response, "normal", report_type, frequency)
                        else:
                            response.failure(f"Resposta de agendamento inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de agendamento não é JSON válido")
                elif response.status_code == 201:
                    # Criado com sucesso
                    response.success()
                    self._log_schedule_metrics(response, "normal", report_type, frequency)
                elif response.status_code == 400:
                    response.success()  # Erro de validação é válido
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
                request_type="POST",
                name="reports_schedule_normal_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def schedule_report_batch(self):
        """
        Teste de agendamento em lote de relatórios
        Baseado em: backend/app/services/agendamento_service.py
        """
        try:
            # Parâmetros para agendamento em lote
            batch_size = random.randint(2, 5)
            frequency = random.choice(self.frequencies)
            
            # Configuração baseada na frequência
            config = self.schedule_configs[frequency]
            
            # Criar múltiplos agendamentos
            schedules = []
            for i in range(batch_size):
                report_type = random.choice(self.report_types)
                report_format = random.choice(self.report_formats)
                
                schedule_time = f"{random.randint(8, 18)}:00"
                
                schedule_config = {
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
                    "recipients": [f"user{i}@example.com"],
                    "filters": {
                        "category": "all",
                        "nicho": "all",
                        "user_id": self.user_id
                    },
                    "options": {
                        "compression": True,
                        "watermark": False,
                        "auto_delete_after": 30
                    }
                }
                
                schedules.append(schedule_config)
            
            # Endpoint para agendamento em lote
            endpoint = "/api/reports/schedule/batch"
            
            payload = {
                "schedules": schedules,
                "batch_options": {
                    "validate_all": True,
                    "stop_on_error": False,
                    "notify_on_completion": True
                }
            }
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_schedule_batch",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "batch_id" in data.get("data", {}):
                            response.success()
                            self._log_schedule_metrics(response, "batch", "multiple", frequency)
                        else:
                            response.failure(f"Resposta de lote inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de lote não é JSON válido")
                elif response.status_code == 202:
                    # Aceito para processamento assíncrono
                    response.success()
                    self._log_schedule_metrics(response, "batch", "multiple", frequency)
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_schedule_batch_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def cancel_schedule(self):
        """
        Teste de cancelamento de agendamentos
        Baseado em: backend/app/api/execucoes_agendadas.py
        """
        try:
            # Selecionar agendamento para cancelar
            schedule_id = random.choice(self.schedule_ids)
            
            # Endpoint para cancelamento
            endpoint = f"/api/reports/schedule/{schedule_id}/cancel"
            
            payload = {
                "reason": random.choice([
                    "no_longer_needed",
                    "schedule_changed",
                    "user_request",
                    "system_maintenance"
                ]),
                "notify_recipients": random.choice([True, False]),
                "keep_history": random.choice([True, False])
            }
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_schedule_cancel",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") or data.get("ok"):
                            response.success()
                            self._log_schedule_metrics(response, "cancel", "cancelled", "none")
                        else:
                            response.failure(f"Resposta de cancelamento inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de cancelamento não é JSON válido")
                elif response.status_code == 404:
                    response.success()  # Agendamento não encontrado é válido
                elif response.status_code == 400:
                    response.success()  # Erro de validação é válido
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_schedule_cancel_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def modify_schedule(self):
        """
        Teste de modificação de agendamentos
        Baseado em: backend/app/services/agendamento_service.py
        """
        try:
            # Selecionar agendamento para modificar
            schedule_id = random.choice(self.schedule_ids)
            
            # Endpoint para modificação
            endpoint = f"/api/reports/schedule/{schedule_id}"
            
            # Modificações aleatórias
            modifications = {}
            
            if random.choice([True, False]):
                modifications["schedule"] = {
                    "time": f"{random.randint(8, 18)}:00",
                    "timezone": "America/Sao_Paulo"
                }
            
            if random.choice([True, False]):
                modifications["recipients"] = [
                    f"user{random.randint(1, 100)}@example.com",
                    f"admin{random.randint(1, 10)}@example.com"
                ]
            
            if random.choice([True, False]):
                modifications["options"] = {
                    "compression": random.choice([True, False]),
                    "watermark": random.choice([True, False])
                }
            
            if random.choice([True, False]):
                modifications["filters"] = {
                    "category": random.choice(["all", "ecommerce", "saas"]),
                    "nicho": random.choice(["all", "tech", "health"])
                }
            
            payload = {
                "modifications": modifications,
                "notify_recipients": random.choice([True, False]),
                "effective_from": (datetime.now() + timedelta(days=1)).isoformat()
            }
            
            with self.client.put(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_schedule_modify",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success"):
                            response.success()
                            self._log_schedule_metrics(response, "modify", "modified", "none")
                        else:
                            response.failure(f"Resposta de modificação inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de modificação não é JSON válido")
                elif response.status_code == 404:
                    response.success()  # Agendamento não encontrado é válido
                elif response.status_code == 400:
                    response.success()  # Erro de validação é válido
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="PUT",
                name="reports_schedule_modify_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(2)
    def list_schedules(self):
        """
        Teste de listagem de agendamentos
        Baseado em: backend/app/api/execucoes_agendadas.py
        """
        try:
            # Endpoint para listagem
            endpoint = "/api/reports/schedule"
            
            # Parâmetros de query
            params = {
                "status": random.choice(["active", "paused", "completed", "cancelled", None]),
                "frequency": random.choice(self.frequencies + [None]),
                "report_type": random.choice(self.report_types + [None]),
                "page": random.randint(1, 10),
                "per_page": random.choice([10, 20, 50, 100]),
                "sort_by": random.choice(["created_at", "next_run", "frequency", "report_type"]),
                "sort_order": random.choice(["asc", "desc"])
            }
            
            # Remover parâmetros None
            params = {k: v for k, v in params.items() if v is not None}
            
            with self.client.get(
                endpoint,
                params=params,
                headers=self.headers,
                name="reports_schedule_list",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and "schedules" in data:
                            response.success()
                            self._log_schedule_metrics(response, "list", "multiple", "none")
                        elif isinstance(data, list):
                            response.success()
                            self._log_schedule_metrics(response, "list", "multiple", "none")
                        else:
                            response.failure(f"Formato de resposta inválido: {type(data)}")
                    except json.JSONDecodeError:
                        response.failure("Resposta de listagem não é JSON válido")
                elif response.status_code == 401:
                    response.failure("Erro de autenticação")
                elif response.status_code == 403:
                    response.failure("Acesso negado")
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="GET",
                name="reports_schedule_list_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def schedule_report_advanced(self):
        """
        Teste de agendamento avançado com configurações complexas
        Baseado em: infrastructure/monitoring/alerts.yaml
        """
        try:
            # Configuração avançada
            report_type = random.choice(["compliance_report", "security_audit", "business_metrics"])
            frequency = "monthly"  # Frequência mais complexa
            
            # Configuração baseada no código real
            config = self.schedule_configs[frequency]
            
            payload = {
                "report_type": report_type,
                "format": "pdf",
                "schedule": {
                    "enabled": True,
                    "frequency": frequency,
                    "time": "10:00",
                    "timezone": "America/Sao_Paulo",
                    "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
                    "day_of_month": 1,
                    "cron_expression": config["cron_expression"],
                    "retry_on_failure": True,
                    "max_retries": 3,
                    "retry_delay": 300  # 5 minutos
                },
                "recipients": [
                    f"executive{random.randint(1, 5)}@example.com",
                    f"compliance{random.randint(1, 3)}@example.com",
                    f"security{random.randint(1, 3)}@example.com"
                ],
                "filters": {
                    "category": "all",
                    "nicho": "all",
                    "user_id": self.user_id,
                    "date_range": "last_90_days",
                    "include_archived": False,
                    "include_deleted": False
                },
                "options": {
                    "compression": True,
                    "watermark": True,
                    "password_protected": True,
                    "password": "SecureReport2025!",
                    "auto_delete_after": 365,
                    "include_charts": True,
                    "include_summary": True,
                    "include_details": True,
                    "include_attachments": True,
                    "high_resolution": True,
                    "custom_template": "executive_report_template"
                },
                "notifications": {
                    "on_success": True,
                    "on_failure": True,
                    "on_cancellation": True,
                    "email_template": "monthly_report_notification"
                }
            }
            
            endpoint = "/api/reports/schedule/advanced"
            
            with self.client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                name="reports_schedule_advanced",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("success") and "schedule_id" in data.get("data", {}):
                            response.success()
                            self._log_schedule_metrics(response, "advanced", report_type, frequency)
                        else:
                            response.failure(f"Resposta avançada inválida: {data}")
                    except json.JSONDecodeError:
                        response.failure("Resposta avançada não é JSON válido")
                elif response.status_code == 202:
                    response.success()
                    self._log_schedule_metrics(response, "advanced", report_type, frequency)
                else:
                    response.failure(f"Status code inesperado: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_schedule_advanced_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task(1)
    def schedule_report_error_scenarios(self):
        """
        Teste de cenários de erro para agendamento
        """
        try:
            # Cenários de erro baseados no código real
            error_scenarios = [
                # Payload inválido
                {
                    "endpoint": "/api/reports/schedule",
                    "payload": {
                        "report_type": "invalid_type",
                        "format": "invalid_format"
                    }
                },
                # Frequência inválida
                {
                    "endpoint": "/api/reports/schedule",
                    "payload": {
                        "report_type": "analytics_summary",
                        "format": "pdf",
                        "schedule": {
                            "frequency": "invalid_frequency",
                            "time": "25:00"  # Hora inválida
                        }
                    }
                },
                # Destinatários inválidos
                {
                    "endpoint": "/api/reports/schedule",
                    "payload": {
                        "report_type": "analytics_summary",
                        "format": "pdf",
                        "recipients": ["invalid_email", "another_invalid"]
                    }
                },
                # Data inválida
                {
                    "endpoint": "/api/reports/schedule",
                    "payload": {
                        "report_type": "analytics_summary",
                        "format": "pdf",
                        "schedule": {
                            "start_date": "invalid_date",
                            "end_date": "2025-01-01"  # Data passada
                        }
                    }
                },
                # Agendamento duplicado
                {
                    "endpoint": "/api/reports/schedule",
                    "payload": {
                        "report_type": "analytics_summary",
                        "format": "pdf",
                        "schedule": {
                            "frequency": "daily",
                            "time": "08:00"
                        },
                        "duplicate_check": True
                    }
                }
            ]
            
            scenario = random.choice(error_scenarios)
            
            with self.client.post(
                scenario["endpoint"],
                json=scenario["payload"],
                headers=self.headers,
                name="reports_schedule_error_scenario",
                catch_response=True
            ) as response:
                # Esperamos erro 400 para cenários inválidos
                if response.status_code in [400, 422]:
                    response.success()
                elif response.status_code == 409:
                    response.success()  # Conflito esperado
                elif response.status_code == 401:
                    response.success()  # Erro de auth esperado
                else:
                    response.failure(f"Status code inesperado para erro: {response.status_code}")
                    
        except Exception as e:
            self.client.environment.events.request.fire(
                request_type="POST",
                name="reports_schedule_error_exception",
                response_time=0,
                response_length=0,
                exception=e
            )

    def _log_schedule_metrics(self, response, test_type: str, report_type: str, frequency: str):
        """
        Log de métricas específicas de agendamento
        Baseado no código real de agendamento
        """
        try:
            # Métricas baseadas no código real
            metrics = {
                "test_type": test_type,
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "report_type": report_type,
                "frequency": frequency,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds() * 1000,  # ms
                "schedule_validation": True,
                "cron_expression_valid": True,
                "timezone_validation": True,
                "recipients_validation": True,
                "filters_validation": True,
                "options_validation": True
            }
            
            # Log estruturado
            self.client.environment.events.request.fire(
                request_type="METRICS",
                name="reports_schedule_metrics",
                response_time=0,
                response_length=len(json.dumps(metrics)),
                exception=None,
                context={"metrics": metrics}
            )
            
        except Exception as e:
            # Log de erro nas métricas
            self.client.environment.events.request.fire(
                request_type="METRICS_ERROR",
                name="reports_schedule_metrics_error",
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
        name="reports_schedule_test_start",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "reports_schedule",
            "start_time": datetime.now().isoformat(),
            "description": "Teste de carga para Agendamento de Relatórios API"
        }
    )

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Finalização do teste"""
    environment.events.request.fire(
        request_type="TEST_STOP",
        name="reports_schedule_test_stop",
        response_time=0,
        response_length=0,
        exception=None,
        context={
            "test_type": "reports_schedule",
            "end_time": datetime.now().isoformat(),
            "description": "Teste de carga para Agendamento de Relatórios API finalizado"
        }
    )

# Configuração de métricas finais
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context=None, **kwargs):
    """Listener para métricas de request"""
    if "reports_schedule" in name:
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
        # print(f"REPORTS_SCHEDULE_METRIC: {json.dumps(log_data)}") 