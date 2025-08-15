"""
🔄 Teste de Falhas Parciais
🎯 Objetivo: Testar degradação graciosa em falhas parciais
📅 Data: 2025-01-27
🔗 Tracing ID: RESILIENCE_PARTIAL_FAILURE_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de falhas parciais e degradação
🌲 ToT: Avaliadas múltiplas estratégias de degradação
♻️ ReAct: Simulado cenários de falha parcial

Testa funcionalidades baseadas em:
- infrastructure/resilience/graceful_degradation.py
- infrastructure/resilience/partial_failure_handler.py
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
class PartialFailureMetrics:
    """Métricas de falha parcial"""
    operation_name: str
    components_failed: int
    components_total: int
    degradation_level: str
    response_time: float
    success_rate: float
    data_completeness: float
    fallback_used: bool
    success_count: int
    error_count: int
    timestamp: datetime

class PartialFailureTest(HttpUser):
    """
    Teste de falhas parciais
    Baseado em código real de resiliência
    """
    
    wait_time = between(3, 6)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[PartialFailureMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'partial_failure_thresholds': {
                'max_response_time': 15.0,
                'min_success_rate': 0.6,
                'min_data_completeness': 0.5
            },
            'degradation_levels': ['none', 'low', 'medium', 'high', 'critical'],
            'component_types': ['database', 'cache', 'external_api', 'file_system', 'queue'],
            'failure_scenarios': ['single_component', 'multiple_components', 'cascading_failure']
        }
        
        logger.info(f"Teste de falhas parciais iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_partial_failure_report()
    
    @task(3)
    def test_single_component_failure(self):
        """Teste de falha de componente único"""
        self._test_partial_failure("single_component", components_to_fail=1)
    
    @task(2)
    def test_multiple_components_failure(self):
        """Teste de falha de múltiplos componentes"""
        self._test_partial_failure("multiple_components", components_to_fail=2)
    
    @task(2)
    def test_cascading_failure(self):
        """Teste de falha em cascata"""
        self._test_partial_failure("cascading_failure", components_to_fail=3)
    
    @task(1)
    def test_graceful_degradation(self):
        """Teste de degradação graciosa"""
        self._test_graceful_degradation()
    
    @task(1)
    def test_partial_failure_recovery(self):
        """Teste de recuperação de falha parcial"""
        self._test_partial_failure_recovery()
    
    def _test_partial_failure(self, failure_scenario: str, components_to_fail: int):
        """Teste de falha parcial"""
        start_time = time.time()
        
        try:
            # Selecionar componentes para falhar
            failed_components = random.sample(self.test_config['component_types'], components_to_fail)
            
            # Preparar payload para simular falha parcial
            payload = {
                "failure_scenario": failure_scenario,
                "failed_components": failed_components,
                "degradation_enabled": True,
                "request_data": {
                    "operation": f"test_operation_{failure_scenario}",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "components_required": self.test_config['component_types'],
                        "fallback_strategy": "graceful_degradation"
                    }
                }
            }
            
            # Executar requisição com falha parcial
            with self.client.post(
                "/api/resilience/partial-failure-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Failure-Scenario": failure_scenario,
                    "X-Failed-Components": ",".join(failed_components),
                    "X-Degradation-Enabled": "true"
                },
                catch_response=True,
                timeout=60
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações da falha parcial
                    components_failed = response_data.get('components_failed', 0)
                    components_total = response_data.get('components_total', len(self.test_config['component_types']))
                    degradation_level = response_data.get('degradation_level', 'none')
                    data_completeness = response_data.get('data_completeness', 0.0)
                    fallback_used = response_data.get('fallback_used', False)
                    
                    # Calcular métricas
                    success_count = 1 if data_completeness > 0.3 else 0
                    error_count = 0 if success_count > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = PartialFailureMetrics(
                        operation_name=f"partial_failure_{failure_scenario}",
                        components_failed=components_failed,
                        components_total=components_total,
                        degradation_level=degradation_level,
                        response_time=response_time,
                        success_rate=success_rate,
                        data_completeness=data_completeness,
                        fallback_used=fallback_used,
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_partial_failure_thresholds(metrics, failure_scenario)
                    
                    response.success()
                    logger.info(f"Falha parcial {failure_scenario} testada: {components_failed}/{components_total} componentes falharam, degradação: {degradation_level}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = PartialFailureMetrics(
                        operation_name=f"partial_failure_{failure_scenario}_error",
                        components_failed=components_to_fail,
                        components_total=len(self.test_config['component_types']),
                        degradation_level="unknown",
                        response_time=response_time,
                        success_rate=0.0,
                        data_completeness=0.0,
                        fallback_used=False,
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics = PartialFailureMetrics(
                operation_name=f"partial_failure_{failure_scenario}_exception",
                components_failed=components_to_fail,
                components_total=len(self.test_config['component_types']),
                degradation_level="unknown",
                response_time=response_time,
                success_rate=0.0,
                data_completeness=0.0,
                fallback_used=False,
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de falha parcial {failure_scenario}: {str(e)}")
    
    def _test_graceful_degradation(self):
        """Teste de degradação graciosa"""
        start_time = time.time()
        
        try:
            # Preparar payload para teste de degradação graciosa
            payload = {
                "graceful_degradation": True,
                "degradation_strategy": "progressive",
                "components_priority": ["database", "cache", "external_api", "file_system", "queue"],
                "request_data": {
                    "operation": "test_operation_graceful_degradation",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "degradation_levels": self.test_config['degradation_levels'],
                        "fallback_enabled": True
                    }
                }
            }
            
            # Executar requisição com degradação graciosa
            with self.client.post(
                "/api/resilience/graceful-degradation-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Graceful-Degradation": "true",
                    "X-Degradation-Strategy": "progressive"
                },
                catch_response=True,
                timeout=90
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações da degradação graciosa
                    degradation_level = response_data.get('degradation_level', 'none')
                    components_available = response_data.get('components_available', [])
                    data_completeness = response_data.get('data_completeness', 0.0)
                    fallback_used = response_data.get('fallback_used', False)
                    degradation_progression = response_data.get('degradation_progression', [])
                    
                    # Calcular métricas
                    components_failed = len(self.test_config['component_types']) - len(components_available)
                    success_count = 1 if data_completeness > 0.2 else 0
                    error_count = 0 if success_count > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = PartialFailureMetrics(
                        operation_name="graceful_degradation",
                        components_failed=components_failed,
                        components_total=len(self.test_config['component_types']),
                        degradation_level=degradation_level,
                        response_time=response_time,
                        success_rate=success_rate,
                        data_completeness=data_completeness,
                        fallback_used=fallback_used,
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_partial_failure_thresholds(metrics, "graceful_degradation")
                    
                    response.success()
                    logger.info(f"Degradação graciosa testada: nível {degradation_level}, componentes disponíveis: {len(components_available)}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = PartialFailureMetrics(
                        operation_name="graceful_degradation_error",
                        components_failed=len(self.test_config['component_types']),
                        components_total=len(self.test_config['component_types']),
                        degradation_level="unknown",
                        response_time=response_time,
                        success_rate=0.0,
                        data_completeness=0.0,
                        fallback_used=False,
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics = PartialFailureMetrics(
                operation_name="graceful_degradation_exception",
                components_failed=len(self.test_config['component_types']),
                components_total=len(self.test_config['component_types']),
                degradation_level="unknown",
                response_time=response_time,
                success_rate=0.0,
                data_completeness=0.0,
                fallback_used=False,
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de degradação graciosa: {str(e)}")
    
    def _test_partial_failure_recovery(self):
        """Teste de recuperação de falha parcial"""
        start_time = time.time()
        
        try:
            # Preparar payload para teste de recuperação
            payload = {
                "partial_failure_recovery": True,
                "recovery_strategy": "automatic",
                "components_to_recover": ["cache", "external_api"],
                "request_data": {
                    "operation": "test_operation_recovery",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "recovery_timeout": 30,
                        "health_check_interval": 5
                    }
                }
            }
            
            # Executar requisição com recuperação
            with self.client.post(
                "/api/resilience/partial-failure-recovery-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Partial-Failure-Recovery": "true",
                    "X-Recovery-Strategy": "automatic"
                },
                catch_response=True,
                timeout=120
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações da recuperação
                    components_recovered = response_data.get('components_recovered', [])
                    recovery_time = response_data.get('recovery_time', 0.0)
                    final_degradation_level = response_data.get('final_degradation_level', 'none')
                    data_completeness = response_data.get('data_completeness', 0.0)
                    
                    # Calcular métricas
                    components_failed = 2 - len(components_recovered)  # Assumindo 2 componentes para recuperar
                    success_count = 1 if len(components_recovered) > 0 else 0
                    error_count = 0 if success_count > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = PartialFailureMetrics(
                        operation_name="partial_failure_recovery",
                        components_failed=components_failed,
                        components_total=2,
                        degradation_level=final_degradation_level,
                        response_time=response_time,
                        success_rate=success_rate,
                        data_completeness=data_completeness,
                        fallback_used=False,
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_partial_failure_thresholds(metrics, "recovery")
                    
                    response.success()
                    logger.info(f"Recuperação de falha parcial testada: {len(components_recovered)} componentes recuperados em {recovery_time:.2f}s")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = PartialFailureMetrics(
                        operation_name="partial_failure_recovery_error",
                        components_failed=2,
                        components_total=2,
                        degradation_level="unknown",
                        response_time=response_time,
                        success_rate=0.0,
                        data_completeness=0.0,
                        fallback_used=False,
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics = PartialFailureMetrics(
                operation_name="partial_failure_recovery_exception",
                components_failed=2,
                components_total=2,
                degradation_level="unknown",
                response_time=response_time,
                success_rate=0.0,
                data_completeness=0.0,
                fallback_used=False,
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de recuperação de falha parcial: {str(e)}")
    
    def _validate_partial_failure_thresholds(self, metrics: PartialFailureMetrics, scenario: str):
        """Validar thresholds de falha parcial"""
        thresholds = self.test_config['partial_failure_thresholds']
        
        # Validar tempo de resposta
        if metrics.response_time > thresholds['max_response_time']:
            logger.warning(f"Tempo de resposta alto para {scenario}: {metrics.response_time:.2f}s > {thresholds['max_response_time']}s")
        
        # Validar taxa de sucesso
        if metrics.success_rate < thresholds['min_success_rate']:
            logger.warning(f"Taxa de sucesso baixa para {scenario}: {metrics.success_rate:.3f} < {thresholds['min_success_rate']}")
        
        # Validar completude dos dados
        if metrics.data_completeness < thresholds['min_data_completeness']:
            logger.warning(f"Completude de dados baixa para {scenario}: {metrics.data_completeness:.3f} < {thresholds['min_data_completeness']}")
        
        # Validar nível de degradação
        if metrics.degradation_level in ['high', 'critical'] and metrics.data_completeness < 0.3:
            logger.warning(f"Degradação crítica para {scenario} com completude baixa: {metrics.data_completeness:.3f}")
    
    def _generate_partial_failure_report(self):
        """Gerar relatório de falhas parciais"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        response_times = [m.response_time for m in self.metrics]
        success_rates = [m.success_rate for m in self.metrics]
        data_completeness_list = [m.data_completeness for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        # Agrupar por nível de degradação
        degradation_stats = {}
        for metric in self.metrics:
            level = metric.degradation_level
            if level not in degradation_stats:
                degradation_stats[level] = {
                    'count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'response_times': [],
                    'data_completeness': []
                }
            
            degradation_stats[level]['count'] += 1
            degradation_stats[level]['success_count'] += metric.success_count
            degradation_stats[level]['error_count'] += metric.error_count
            degradation_stats[level]['response_times'].append(metric.response_time)
            degradation_stats[level]['data_completeness'].append(metric.data_completeness)
        
        # Calcular estatísticas por nível de degradação
        for level, stats in degradation_stats.items():
            if stats['response_times']:
                stats['avg_response_time'] = statistics.mean(stats['response_times'])
                stats['avg_data_completeness'] = statistics.mean(stats['data_completeness'])
                stats['success_rate'] = stats['success_count'] / (stats['success_count'] + stats['error_count']) if (stats['success_count'] + stats['error_count']) > 0 else 0
            else:
                stats['avg_response_time'] = 0
                stats['avg_data_completeness'] = 0
                stats['success_rate'] = 0
        
        report = {
            "test_name": "Partial Failure Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_successful_operations": total_success,
            "total_failed_operations": total_errors,
            "operation_success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "partial_failure_metrics": {
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
                "data_completeness": {
                    "mean": statistics.mean(data_completeness_list) if data_completeness_list else 0,
                    "min": min(data_completeness_list) if data_completeness_list else 0
                }
            },
            "degradation_statistics": degradation_stats,
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/partial_failure_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de falhas parciais salvo: partial_failure_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de falhas parciais iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de falhas parciais finalizado") 