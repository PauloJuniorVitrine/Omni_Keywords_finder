"""
🔄 Teste de Serviços Indisponíveis
🎯 Objetivo: Testar comportamento quando serviços estão indisponíveis
📅 Data: 2025-01-27
🔗 Tracing ID: RESILIENCE_SERVICE_UNAVAILABLE_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de serviços indisponíveis e fallbacks
🌲 ToT: Avaliadas múltiplas estratégias de fallback
♻️ ReAct: Simulado cenários de indisponibilidade

Testa funcionalidades baseadas em:
- infrastructure/resilience/service_unavailable_handler.py
- infrastructure/resilience/fallback_strategies.py
- backend/app/services/resilient_service.py
"""

import time
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

from locust import HttpUser, task, between, events
from locust.exception import StopUser

# Configuração de logging
import logging
logger = logging.getLogger(__name__)

@dataclass
class ServiceUnavailableMetrics:
    """Métricas de serviço indisponível"""
    operation_name: str
    service_name: str
    unavailable_duration: float
    fallback_used: bool
    fallback_strategy: str
    response_time: float
    success_rate: float
    data_quality: float
    circuit_state: str
    success_count: int
    error_count: int
    timestamp: datetime

class ServiceUnavailableTest(HttpUser):
    """
    Teste de serviços indisponíveis
    Baseado em código real de resiliência
    """
    
    wait_time = between(4, 8)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[ServiceUnavailableMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'service_unavailable_thresholds': {
                'max_response_time': 20.0,
                'min_success_rate': 0.5,
                'min_data_quality': 0.4
            },
            'services': ['database', 'cache', 'external_api', 'file_system', 'queue', 'search_engine'],
            'unavailable_scenarios': ['temporary', 'prolonged', 'intermittent', 'cascading'],
            'fallback_strategies': ['cache_only', 'default_data', 'degraded_service', 'alternative_service']
        }
        
        logger.info(f"Teste de serviços indisponíveis iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_service_unavailable_report()
    
    @task(3)
    def test_temporary_unavailable(self):
        """Teste de indisponibilidade temporária"""
        self._test_service_unavailable("temporary", duration=30)
    
    @task(2)
    def test_prolonged_unavailable(self):
        """Teste de indisponibilidade prolongada"""
        self._test_service_unavailable("prolonged", duration=120)
    
    @task(2)
    def test_intermittent_unavailable(self):
        """Teste de indisponibilidade intermitente"""
        self._test_service_unavailable("intermittent", duration=60)
    
    @task(1)
    def test_cascading_unavailable(self):
        """Teste de indisponibilidade em cascata"""
        self._test_service_unavailable("cascading", duration=90)
    
    @task(1)
    def test_service_unavailable_with_fallback(self):
        """Teste de serviço indisponível com fallback"""
        self._test_service_unavailable_with_fallback()
    
    def _test_service_unavailable(self, scenario: str, duration: int):
        """Teste de serviço indisponível"""
        start_time = time.time()
        
        try:
            # Selecionar serviço para tornar indisponível
            unavailable_service = random.choice(self.test_config['services'])
            
            # Preparar payload para simular indisponibilidade
            payload = {
                "unavailable_scenario": scenario,
                "unavailable_service": unavailable_service,
                "unavailable_duration": duration,
                "request_data": {
                    "operation": f"test_operation_{scenario}",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "service_dependency": unavailable_service,
                        "fallback_enabled": True
                    }
                }
            }
            
            # Executar requisição com serviço indisponível
            with self.client.post(
                "/api/resilience/service-unavailable-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Unavailable-Scenario": scenario,
                    "X-Unavailable-Service": unavailable_service,
                    "X-Unavailable-Duration": str(duration)
                },
                catch_response=True,
                timeout=180
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações da indisponibilidade
                    actual_duration = response_data.get('unavailable_duration', 0.0)
                    fallback_used = response_data.get('fallback_used', False)
                    fallback_strategy = response_data.get('fallback_strategy', 'none')
                    data_quality = response_data.get('data_quality', 0.0)
                    circuit_state = response_data.get('circuit_state', 'UNKNOWN')
                    
                    # Calcular métricas
                    success_count = 1 if fallback_used or data_quality > 0.2 else 0
                    error_count = 0 if success_count > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = ServiceUnavailableMetrics(
                        operation_name=f"service_unavailable_{scenario}",
                        service_name=unavailable_service,
                        unavailable_duration=actual_duration,
                        fallback_used=fallback_used,
                        fallback_strategy=fallback_strategy,
                        response_time=response_time,
                        success_rate=success_rate,
                        data_quality=data_quality,
                        circuit_state=circuit_state,
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_service_unavailable_thresholds(metrics, scenario)
                    
                    response.success()
                    logger.info(f"Serviço indisponível {scenario} testado: {unavailable_service}, fallback: {fallback_used}, duração: {actual_duration:.2f}s")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = ServiceUnavailableMetrics(
                        operation_name=f"service_unavailable_{scenario}_error",
                        service_name=unavailable_service,
                        unavailable_duration=duration,
                        fallback_used=False,
                        fallback_strategy="none",
                        response_time=response_time,
                        success_rate=0.0,
                        data_quality=0.0,
                        circuit_state="UNKNOWN",
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics = ServiceUnavailableMetrics(
                operation_name=f"service_unavailable_{scenario}_exception",
                service_name=unavailable_service if 'unavailable_service' in locals() else "unknown",
                unavailable_duration=duration,
                fallback_used=False,
                fallback_strategy="none",
                response_time=response_time,
                success_rate=0.0,
                data_quality=0.0,
                circuit_state="UNKNOWN",
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de serviço indisponível {scenario}: {str(e)}")
    
    def _test_service_unavailable_with_fallback(self):
        """Teste de serviço indisponível com fallback"""
        start_time = time.time()
        
        try:
            # Preparar payload para teste com fallback
            payload = {
                "service_unavailable_with_fallback": True,
                "unavailable_service": "database",
                "fallback_strategy": random.choice(self.test_config['fallback_strategies']),
                "request_data": {
                    "operation": "test_operation_fallback",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "primary_service": "database",
                        "fallback_services": ["cache", "file_system"],
                        "data_consistency": "eventual"
                    }
                }
            }
            
            # Executar requisição com fallback
            with self.client.post(
                "/api/resilience/service-unavailable-fallback-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Service-Unavailable-With-Fallback": "true",
                    "X-Fallback-Strategy": payload["fallback_strategy"]
                },
                catch_response=True,
                timeout=120
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações do fallback
                    fallback_used = response_data.get('fallback_used', False)
                    fallback_strategy = response_data.get('fallback_strategy', 'none')
                    fallback_service = response_data.get('fallback_service', 'none')
                    data_quality = response_data.get('data_quality', 0.0)
                    response_time_with_fallback = response_data.get('response_time_with_fallback', 0.0)
                    
                    # Calcular métricas
                    success_count = 1 if fallback_used and data_quality > 0.3 else 0
                    error_count = 0 if success_count > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = ServiceUnavailableMetrics(
                        operation_name="service_unavailable_with_fallback",
                        service_name="database",
                        unavailable_duration=response_time_with_fallback,
                        fallback_used=fallback_used,
                        fallback_strategy=fallback_strategy,
                        response_time=response_time,
                        success_rate=success_rate,
                        data_quality=data_quality,
                        circuit_state="FALLBACK" if fallback_used else "UNKNOWN",
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_service_unavailable_thresholds(metrics, "fallback")
                    
                    response.success()
                    logger.info(f"Serviço indisponível com fallback testado: estratégia {fallback_strategy}, serviço: {fallback_service}, qualidade: {data_quality:.3f}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = ServiceUnavailableMetrics(
                        operation_name="service_unavailable_with_fallback_error",
                        service_name="database",
                        unavailable_duration=0.0,
                        fallback_used=False,
                        fallback_strategy="none",
                        response_time=response_time,
                        success_rate=0.0,
                        data_quality=0.0,
                        circuit_state="UNKNOWN",
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics = ServiceUnavailableMetrics(
                operation_name="service_unavailable_with_fallback_exception",
                service_name="database",
                unavailable_duration=0.0,
                fallback_used=False,
                fallback_strategy="none",
                response_time=response_time,
                success_rate=0.0,
                data_quality=0.0,
                circuit_state="UNKNOWN",
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de serviço indisponível com fallback: {str(e)}")
    
    def _validate_service_unavailable_thresholds(self, metrics: ServiceUnavailableMetrics, scenario: str):
        """Validar thresholds de serviço indisponível"""
        thresholds = self.test_config['service_unavailable_thresholds']
        
        # Validar tempo de resposta
        if metrics.response_time > thresholds['max_response_time']:
            logger.warning(f"Tempo de resposta alto para {scenario}: {metrics.response_time:.2f}s > {thresholds['max_response_time']}s")
        
        # Validar taxa de sucesso
        if metrics.success_rate < thresholds['min_success_rate']:
            logger.warning(f"Taxa de sucesso baixa para {scenario}: {metrics.success_rate:.3f} < {thresholds['min_success_rate']}")
        
        # Validar qualidade dos dados
        if metrics.data_quality < thresholds['min_data_quality']:
            logger.warning(f"Qualidade de dados baixa para {scenario}: {metrics.data_quality:.3f} < {thresholds['min_data_quality']}")
        
        # Validar uso de fallback
        if not metrics.fallback_used and metrics.circuit_state != "CLOSED":
            logger.warning(f"Fallback não foi usado para {scenario} com serviço indisponível")
        
        # Validar duração da indisponibilidade
        if metrics.unavailable_duration > 300:  # 5 minutos
            logger.warning(f"Duração de indisponibilidade muito longa para {scenario}: {metrics.unavailable_duration:.2f}s")
    
    def _generate_service_unavailable_report(self):
        """Gerar relatório de serviços indisponíveis"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        response_times = [m.response_time for m in self.metrics]
        success_rates = [m.success_rate for m in self.metrics]
        data_qualities = [m.data_quality for m in self.metrics]
        unavailable_durations = [m.unavailable_duration for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        # Agrupar por serviço
        service_stats = {}
        for metric in self.metrics:
            service = metric.service_name
            if service not in service_stats:
                service_stats[service] = {
                    'count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'response_times': [],
                    'data_qualities': [],
                    'fallback_used_count': 0
                }
            
            service_stats[service]['count'] += 1
            service_stats[service]['success_count'] += metric.success_count
            service_stats[service]['error_count'] += metric.error_count
            service_stats[service]['response_times'].append(metric.response_time)
            service_stats[service]['data_qualities'].append(metric.data_quality)
            if metric.fallback_used:
                service_stats[service]['fallback_used_count'] += 1
        
        # Calcular estatísticas por serviço
        for service, stats in service_stats.items():
            if stats['response_times']:
                stats['avg_response_time'] = statistics.mean(stats['response_times'])
                stats['avg_data_quality'] = statistics.mean(stats['data_qualities'])
                stats['success_rate'] = stats['success_count'] / (stats['success_count'] + stats['error_count']) if (stats['success_count'] + stats['error_count']) > 0 else 0
                stats['fallback_usage_rate'] = stats['fallback_used_count'] / stats['count'] if stats['count'] > 0 else 0
            else:
                stats['avg_response_time'] = 0
                stats['avg_data_quality'] = 0
                stats['success_rate'] = 0
                stats['fallback_usage_rate'] = 0
        
        report = {
            "test_name": "Service Unavailable Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_successful_operations": total_success,
            "total_failed_operations": total_errors,
            "operation_success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "service_unavailable_metrics": {
                "response_time": {
                    "mean": statistics.mean(response_times) if response_times else 0,
                    "median": statistics.median(response_times) if response_times else 0,
                    "min": min(response_times) if response_times else 0,
                    "max": max(response_times) if response_times else 0
                },
                "success_rate": {
                    "mean": statistics.mean(success_rates) if success_rates else 0,
                    "min": min(success_rates) if success_rates else 0
                },
                "data_quality": {
                    "mean": statistics.mean(data_qualities) if data_qualities else 0,
                    "min": min(data_qualities) if data_qualities else 0
                },
                "unavailable_duration": {
                    "mean": statistics.mean(unavailable_durations) if unavailable_durations else 0,
                    "max": max(unavailable_durations) if unavailable_durations else 0
                }
            },
            "service_statistics": service_stats,
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/service_unavailable_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de serviços indisponíveis salvo: service_unavailable_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de serviços indisponíveis iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de serviços indisponíveis finalizado") 