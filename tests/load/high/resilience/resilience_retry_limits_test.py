"""
🔄 Teste de Limites de Retry
🎯 Objetivo: Testar limites e configurações de retry
📅 Data: 2025-01-27
🔗 Tracing ID: RESILIENCE_RETRY_LIMITS_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de limites de retry e configurações
🌲 ToT: Avaliadas múltiplas estratégias de limites
♻️ ReAct: Simulado cenários de limite de retry

Testa funcionalidades baseadas em:
- infrastructure/resilience/retry_logic.py
- infrastructure/resilience/retry_limits.py
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
class RetryLimitsMetrics:
    """Métricas de limites de retry"""
    operation_name: str
    max_retries: int
    actual_retries: int
    retry_limit_reached: bool
    total_time: float
    success_rate: float
    retry_strategy: str
    success_count: int
    error_count: int
    timestamp: datetime

class RetryLimitsTest(HttpUser):
    """
    Teste de limites de retry
    Baseado em código real de resiliência
    """
    
    wait_time = between(2, 4)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[RetryLimitsMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'retry_limit_thresholds': {
                'max_total_time': 120.0,
                'min_success_rate': 0.5,
                'max_retry_attempts': 15
            },
            'retry_strategies': ['fixed_limit', 'time_based_limit', 'adaptive_limit'],
            'limit_scenarios': ['low_limit', 'medium_limit', 'high_limit', 'no_limit'],
            'failure_types': ['persistent_failure', 'intermittent_failure', 'cascading_failure']
        }
        
        logger.info(f"Teste de limites de retry iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_retry_limits_report()
    
    @task(3)
    def test_fixed_retry_limit(self):
        """Teste de limite fixo de retry"""
        self._test_retry_limit("fixed_limit", max_retries=5)
    
    @task(2)
    def test_time_based_retry_limit(self):
        """Teste de limite baseado em tempo"""
        self._test_retry_limit("time_based_limit", max_retries=10)
    
    @task(2)
    def test_adaptive_retry_limit(self):
        """Teste de limite adaptativo"""
        self._test_retry_limit("adaptive_limit", max_retries=7)
    
    @task(1)
    def test_no_retry_limit(self):
        """Teste sem limite de retry"""
        self._test_retry_limit("no_limit", max_retries=0)
    
    @task(1)
    def test_retry_limit_with_backoff(self):
        """Teste de limite de retry com backoff"""
        self._test_retry_limit_with_backoff()
    
    def _test_retry_limit(self, retry_strategy: str, max_retries: int):
        """Teste de limite de retry"""
        start_time = time.time()
        
        try:
            # Preparar payload para teste de limite
            payload = {
                "retry_strategy": retry_strategy,
                "max_retries": max_retries,
                "failure_type": random.choice(self.test_config['failure_types']),
                "request_data": {
                    "operation": f"test_operation_{retry_strategy}",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "retry_count": 0,
                        "failure_probability": 0.8,
                        "limit_enforced": True
                    }
                }
            }
            
            # Executar requisição com limite de retry
            with self.client.post(
                "/api/resilience/retry-limits-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Retry-Strategy": retry_strategy,
                    "X-Max-Retries": str(max_retries),
                    "X-Failure-Type": payload["failure_type"]
                },
                catch_response=True,
                timeout=180
            ) as response:
                end_time = time.time()
                total_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações do retry
                    actual_retries = response_data.get('actual_retries', 0)
                    retry_limit_reached = response_data.get('retry_limit_reached', False)
                    strategy_used = response_data.get('retry_strategy', retry_strategy)
                    
                    # Calcular métricas
                    success_count = 1 if not retry_limit_reached or actual_retries < max_retries else 0
                    error_count = 0 if success_count > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = RetryLimitsMetrics(
                        operation_name=f"retry_limit_{retry_strategy}",
                        max_retries=max_retries,
                        actual_retries=actual_retries,
                        retry_limit_reached=retry_limit_reached,
                        total_time=total_time,
                        success_rate=success_rate,
                        retry_strategy=strategy_used,
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_retry_limit_thresholds(metrics, retry_strategy)
                    
                    response.success()
                    logger.info(f"Limite de retry {retry_strategy} testado: {actual_retries}/{max_retries} retries, limite atingido: {retry_limit_reached}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = RetryLimitsMetrics(
                        operation_name=f"retry_limit_{retry_strategy}_error",
                        max_retries=max_retries,
                        actual_retries=0,
                        retry_limit_reached=False,
                        total_time=total_time,
                        success_rate=0.0,
                        retry_strategy=retry_strategy,
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            total_time = end_time - start_time
            
            metrics = RetryLimitsMetrics(
                operation_name=f"retry_limit_{retry_strategy}_exception",
                max_retries=max_retries,
                actual_retries=0,
                retry_limit_reached=False,
                total_time=total_time,
                success_rate=0.0,
                retry_strategy=retry_strategy,
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de limite de retry {retry_strategy}: {str(e)}")
    
    def _test_retry_limit_with_backoff(self):
        """Teste de limite de retry com backoff"""
        start_time = time.time()
        
        try:
            # Preparar payload para teste com backoff
            payload = {
                "retry_strategy": "adaptive_limit",
                "max_retries": 8,
                "failure_type": "intermittent_failure",
                "backoff_enabled": True,
                "base_delay": 2.0,
                "max_delay": 20.0,
                "request_data": {
                    "operation": "test_operation_backoff_limit",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "retry_count": 0,
                        "failure_probability": 0.7,
                        "backoff_factor": 2.0
                    }
                }
            }
            
            # Executar requisição com backoff
            with self.client.post(
                "/api/resilience/retry-limits-backoff-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Retry-Strategy": "adaptive_limit",
                    "X-Max-Retries": "8",
                    "X-Backoff-Enabled": "true",
                    "X-Base-Delay": "2.0"
                },
                catch_response=True,
                timeout=240
            ) as response:
                end_time = time.time()
                total_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações do retry com backoff
                    actual_retries = response_data.get('actual_retries', 0)
                    retry_limit_reached = response_data.get('retry_limit_reached', False)
                    backoff_applied = response_data.get('backoff_applied', False)
                    total_backoff_time = response_data.get('total_backoff_time', 0.0)
                    
                    # Calcular métricas
                    success_count = 1 if not retry_limit_reached or actual_retries < 8 else 0
                    error_count = 0 if success_count > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = RetryLimitsMetrics(
                        operation_name="retry_limit_with_backoff",
                        max_retries=8,
                        actual_retries=actual_retries,
                        retry_limit_reached=retry_limit_reached,
                        total_time=total_time,
                        success_rate=success_rate,
                        retry_strategy="adaptive_limit_with_backoff",
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_retry_limit_thresholds(metrics, "backoff")
                    
                    response.success()
                    logger.info(f"Limite de retry com backoff testado: {actual_retries}/8 retries, backoff aplicado: {backoff_applied}, tempo total: {total_time:.2f}s")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = RetryLimitsMetrics(
                        operation_name="retry_limit_with_backoff_error",
                        max_retries=8,
                        actual_retries=0,
                        retry_limit_reached=False,
                        total_time=total_time,
                        success_rate=0.0,
                        retry_strategy="adaptive_limit_with_backoff",
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            total_time = end_time - start_time
            
            metrics = RetryLimitsMetrics(
                operation_name="retry_limit_with_backoff_exception",
                max_retries=8,
                actual_retries=0,
                retry_limit_reached=False,
                total_time=total_time,
                success_rate=0.0,
                retry_strategy="adaptive_limit_with_backoff",
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de limite de retry com backoff: {str(e)}")
    
    def _validate_retry_limit_thresholds(self, metrics: RetryLimitsMetrics, strategy: str):
        """Validar thresholds de limite de retry"""
        thresholds = self.test_config['retry_limit_thresholds']
        
        # Validar tempo total
        if metrics.total_time > thresholds['max_total_time']:
            logger.warning(f"Tempo total alto para {strategy}: {metrics.total_time:.2f}s > {thresholds['max_total_time']}s")
        
        # Validar taxa de sucesso
        if metrics.success_rate < thresholds['min_success_rate']:
            logger.warning(f"Taxa de sucesso baixa para {strategy}: {metrics.success_rate:.3f} < {thresholds['min_success_rate']}")
        
        # Validar número de tentativas
        if metrics.actual_retries > thresholds['max_retry_attempts']:
            logger.warning(f"Muitas tentativas para {strategy}: {metrics.actual_retries} > {thresholds['max_retry_attempts']}")
        
        # Validar se limite foi respeitado
        if metrics.actual_retries > metrics.max_retries and metrics.max_retries > 0:
            logger.warning(f"Limite de retry excedido para {strategy}: {metrics.actual_retries} > {metrics.max_retries}")
        
        # Validar se limite foi atingido quando esperado
        if not metrics.retry_limit_reached and metrics.actual_retries >= metrics.max_retries:
            logger.warning(f"Limite de retry não foi marcado como atingido para {strategy}")
    
    def _generate_retry_limits_report(self):
        """Gerar relatório de limites de retry"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        total_times = [m.total_time for m in self.metrics]
        success_rates = [m.success_rate for m in self.metrics]
        actual_retries_list = [m.actual_retries for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        # Agrupar por estratégia
        strategy_stats = {}
        for metric in self.metrics:
            strategy = metric.retry_strategy
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'total_times': [],
                    'actual_retries': [],
                    'limit_reached_count': 0
                }
            
            strategy_stats[strategy]['count'] += 1
            strategy_stats[strategy]['success_count'] += metric.success_count
            strategy_stats[strategy]['error_count'] += metric.error_count
            strategy_stats[strategy]['total_times'].append(metric.total_time)
            strategy_stats[strategy]['actual_retries'].append(metric.actual_retries)
            if metric.retry_limit_reached:
                strategy_stats[strategy]['limit_reached_count'] += 1
        
        # Calcular estatísticas por estratégia
        for strategy, stats in strategy_stats.items():
            if stats['total_times']:
                stats['avg_total_time'] = statistics.mean(stats['total_times'])
                stats['avg_actual_retries'] = statistics.mean(stats['actual_retries'])
                stats['success_rate'] = stats['success_count'] / (stats['success_count'] + stats['error_count']) if (stats['success_count'] + stats['error_count']) > 0 else 0
                stats['limit_reached_rate'] = stats['limit_reached_count'] / stats['count'] if stats['count'] > 0 else 0
            else:
                stats['avg_total_time'] = 0
                stats['avg_actual_retries'] = 0
                stats['success_rate'] = 0
                stats['limit_reached_rate'] = 0
        
        report = {
            "test_name": "Retry Limits Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_successful_operations": total_success,
            "total_failed_operations": total_errors,
            "operation_success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "retry_limits_metrics": {
                "total_time": {
                    "mean": statistics.mean(total_times) if total_times else 0,
                    "median": statistics.median(total_times) if total_times else 0,
                    "min": min(total_times) if total_times else 0,
                    "max": max(total_times) if total_times else 0
                },
                "success_rate": {
                    "mean": statistics.mean(success_rates) if success_rates else 0,
                    "min": min(success_rates) if success_rates else 0
                },
                "actual_retries": {
                    "mean": statistics.mean(actual_retries_list) if actual_retries_list else 0,
                    "max": max(actual_retries_list) if actual_retries_list else 0
                }
            },
            "strategy_statistics": strategy_stats,
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/retry_limits_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de limites de retry salvo: retry_limits_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de limites de retry iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de limites de retry finalizado") 