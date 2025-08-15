"""
🔄 Teste de Backoff Exponencial
🎯 Objetivo: Testar lógica de backoff exponencial em retries
📅 Data: 2025-01-27
🔗 Tracing ID: RESILIENCE_EXPONENTIAL_BACKOFF_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de backoff exponencial e retry logic
🌲 ToT: Avaliadas múltiplas estratégias de backoff
♻️ ReAct: Simulado cenários de falha e retry com backoff

Testa funcionalidades baseadas em:
- infrastructure/resilience/retry_logic.py
- infrastructure/resilience/backoff_strategies.py
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
class ExponentialBackoffMetrics:
    """Métricas de backoff exponencial"""
    operation_name: str
    total_retries: int
    total_wait_time: float
    success_on_retry: int
    backoff_strategy: str
    max_retry_delay: float
    success_rate: float
    success_count: int
    error_count: int
    timestamp: datetime

class ExponentialBackoffTest(HttpUser):
    """
    Teste de backoff exponencial
    Baseado em código real de resiliência
    """
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[ExponentialBackoffMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'backoff_thresholds': {
                'max_total_wait_time': 60.0,
                'min_success_rate': 0.6,
                'max_retry_delay': 30.0
            },
            'backoff_strategies': ['exponential', 'exponential_with_jitter', 'fibonacci'],
            'retry_scenarios': ['transient_failure', 'rate_limit', 'timeout', 'server_error'],
            'max_retries': [3, 5, 7, 10]
        }
        
        logger.info(f"Teste de backoff exponencial iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_backoff_report()
    
    @task(3)
    def test_exponential_backoff_transient(self):
        """Teste de backoff exponencial para falhas transitórias"""
        self._test_exponential_backoff("transient_failure", max_retries=5)
    
    @task(2)
    def test_exponential_backoff_rate_limit(self):
        """Teste de backoff exponencial para rate limit"""
        self._test_exponential_backoff("rate_limit", max_retries=7)
    
    @task(2)
    def test_exponential_backoff_timeout(self):
        """Teste de backoff exponencial para timeout"""
        self._test_exponential_backoff("timeout", max_retries=3)
    
    @task(1)
    def test_exponential_backoff_server_error(self):
        """Teste de backoff exponencial para erro do servidor"""
        self._test_exponential_backoff("server_error", max_retries=10)
    
    @task(1)
    def test_exponential_backoff_with_jitter(self):
        """Teste de backoff exponencial com jitter"""
        self._test_exponential_backoff_with_jitter()
    
    def _test_exponential_backoff(self, failure_type: str, max_retries: int):
        """Teste de backoff exponencial"""
        start_time = time.time()
        
        try:
            # Preparar payload para simular falhas
            payload = {
                "failure_type": failure_type,
                "max_retries": max_retries,
                "backoff_strategy": "exponential",
                "base_delay": 1.0,
                "max_delay": 30.0,
                "request_data": {
                    "operation": f"test_operation_{failure_type}",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "retry_count": 0,
                        "failure_probability": 0.7
                    }
                }
            }
            
            # Executar requisição com retry
            with self.client.post(
                "/api/resilience/exponential-backoff-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Failure-Type": failure_type,
                    "X-Max-Retries": str(max_retries),
                    "X-Backoff-Strategy": "exponential"
                },
                catch_response=True,
                timeout=120
            ) as response:
                end_time = time.time()
                total_wait_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações do retry
                    total_retries = response_data.get('total_retries', 0)
                    success_on_retry = response_data.get('success_on_retry', 0)
                    backoff_strategy = response_data.get('backoff_strategy', 'exponential')
                    max_retry_delay = response_data.get('max_retry_delay', 0.0)
                    
                    # Calcular métricas
                    success_count = 1 if success_on_retry > 0 else 0
                    error_count = 0 if success_on_retry > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = ExponentialBackoffMetrics(
                        operation_name=f"exponential_backoff_{failure_type}",
                        total_retries=total_retries,
                        total_wait_time=total_wait_time,
                        success_on_retry=success_on_retry,
                        backoff_strategy=backoff_strategy,
                        max_retry_delay=max_retry_delay,
                        success_rate=success_rate,
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_backoff_thresholds(metrics, failure_type)
                    
                    response.success()
                    logger.info(f"Backoff exponencial {failure_type} bem-sucedido: {total_retries} retries, sucesso no retry {success_on_retry}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = ExponentialBackoffMetrics(
                        operation_name=f"exponential_backoff_{failure_type}_error",
                        total_retries=max_retries,
                        total_wait_time=total_wait_time,
                        success_on_retry=0,
                        backoff_strategy="exponential",
                        max_retry_delay=0.0,
                        success_rate=0.0,
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            total_wait_time = end_time - start_time
            
            metrics = ExponentialBackoffMetrics(
                operation_name=f"exponential_backoff_{failure_type}_exception",
                total_retries=0,
                total_wait_time=total_wait_time,
                success_on_retry=0,
                backoff_strategy="exponential",
                max_retry_delay=0.0,
                success_rate=0.0,
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de backoff exponencial {failure_type}: {str(e)}")
    
    def _test_exponential_backoff_with_jitter(self):
        """Teste de backoff exponencial com jitter"""
        start_time = time.time()
        
        try:
            # Preparar payload para teste com jitter
            payload = {
                "failure_type": "transient_failure",
                "max_retries": 5,
                "backoff_strategy": "exponential_with_jitter",
                "base_delay": 1.0,
                "max_delay": 30.0,
                "jitter_factor": 0.1,
                "request_data": {
                    "operation": "test_operation_jitter",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "retry_count": 0,
                        "failure_probability": 0.8,
                        "jitter_enabled": True
                    }
                }
            }
            
            # Executar requisição com jitter
            with self.client.post(
                "/api/resilience/exponential-backoff-jitter-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Failure-Type": "transient_failure",
                    "X-Max-Retries": "5",
                    "X-Backoff-Strategy": "exponential_with_jitter",
                    "X-Jitter-Factor": "0.1"
                },
                catch_response=True,
                timeout=90
            ) as response:
                end_time = time.time()
                total_wait_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações do retry com jitter
                    total_retries = response_data.get('total_retries', 0)
                    success_on_retry = response_data.get('success_on_retry', 0)
                    backoff_strategy = response_data.get('backoff_strategy', 'exponential_with_jitter')
                    max_retry_delay = response_data.get('max_retry_delay', 0.0)
                    jitter_applied = response_data.get('jitter_applied', False)
                    
                    # Calcular métricas
                    success_count = 1 if success_on_retry > 0 else 0
                    error_count = 0 if success_on_retry > 0 else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = ExponentialBackoffMetrics(
                        operation_name="exponential_backoff_with_jitter",
                        total_retries=total_retries,
                        total_wait_time=total_wait_time,
                        success_on_retry=success_on_retry,
                        backoff_strategy=backoff_strategy,
                        max_retry_delay=max_retry_delay,
                        success_rate=success_rate,
                        success_count=success_count,
                        error_count=error_count,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
                    # Validar thresholds
                    self._validate_backoff_thresholds(metrics, "jitter")
                    
                    response.success()
                    logger.info(f"Backoff exponencial com jitter bem-sucedido: {total_retries} retries, jitter aplicado: {jitter_applied}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = ExponentialBackoffMetrics(
                        operation_name="exponential_backoff_with_jitter_error",
                        total_retries=5,
                        total_wait_time=total_wait_time,
                        success_on_retry=0,
                        backoff_strategy="exponential_with_jitter",
                        max_retry_delay=0.0,
                        success_rate=0.0,
                        success_count=0,
                        error_count=1,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metrics)
                    
        except Exception as e:
            end_time = time.time()
            total_wait_time = end_time - start_time
            
            metrics = ExponentialBackoffMetrics(
                operation_name="exponential_backoff_with_jitter_exception",
                total_retries=0,
                total_wait_time=total_wait_time,
                success_on_retry=0,
                backoff_strategy="exponential_with_jitter",
                max_retry_delay=0.0,
                success_rate=0.0,
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de backoff exponencial com jitter: {str(e)}")
    
    def _validate_backoff_thresholds(self, metrics: ExponentialBackoffMetrics, failure_type: str):
        """Validar thresholds de backoff"""
        thresholds = self.test_config['backoff_thresholds']
        
        # Validar tempo total de espera
        if metrics.total_wait_time > thresholds['max_total_wait_time']:
            logger.warning(f"Tempo total de espera alto para {failure_type}: {metrics.total_wait_time:.2f}s > {thresholds['max_total_wait_time']}s")
        
        # Validar taxa de sucesso
        if metrics.success_rate < thresholds['min_success_rate']:
            logger.warning(f"Taxa de sucesso baixa para {failure_type}: {metrics.success_rate:.3f} < {thresholds['min_success_rate']}")
        
        # Validar delay máximo de retry
        if metrics.max_retry_delay > thresholds['max_retry_delay']:
            logger.warning(f"Delay máximo de retry alto para {failure_type}: {metrics.max_retry_delay:.2f}s > {thresholds['max_retry_delay']}s")
        
        # Validar se retry foi bem-sucedido
        if metrics.success_on_retry == 0 and metrics.total_retries > 0:
            logger.warning(f"Retry não foi bem-sucedido para {failure_type} após {metrics.total_retries} tentativas")
    
    def _generate_backoff_report(self):
        """Gerar relatório de backoff"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        total_wait_times = [m.total_wait_time for m in self.metrics]
        success_rates = [m.success_rate for m in self.metrics]
        max_retry_delays = [m.max_retry_delay for m in self.metrics]
        total_retries_list = [m.total_retries for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        # Agrupar por estratégia
        strategy_stats = {}
        for metric in self.metrics:
            strategy = metric.backoff_strategy
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'total_wait_times': [],
                    'max_retry_delays': [],
                    'total_retries': []
                }
            
            strategy_stats[strategy]['count'] += 1
            strategy_stats[strategy]['success_count'] += metric.success_count
            strategy_stats[strategy]['error_count'] += metric.error_count
            strategy_stats[strategy]['total_wait_times'].append(metric.total_wait_time)
            strategy_stats[strategy]['max_retry_delays'].append(metric.max_retry_delay)
            strategy_stats[strategy]['total_retries'].append(metric.total_retries)
        
        # Calcular estatísticas por estratégia
        for strategy, stats in strategy_stats.items():
            if stats['total_wait_times']:
                stats['avg_wait_time'] = statistics.mean(stats['total_wait_times'])
                stats['avg_max_retry_delay'] = statistics.mean(stats['max_retry_delays'])
                stats['avg_total_retries'] = statistics.mean(stats['total_retries'])
                stats['success_rate'] = stats['success_count'] / (stats['success_count'] + stats['error_count']) if (stats['success_count'] + stats['error_count']) > 0 else 0
            else:
                stats['avg_wait_time'] = 0
                stats['avg_max_retry_delay'] = 0
                stats['avg_total_retries'] = 0
                stats['success_rate'] = 0
        
        report = {
            "test_name": "Exponential Backoff Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_successful_retries": total_success,
            "total_failed_retries": total_errors,
            "retry_success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "backoff_metrics": {
                "total_wait_time": {
                    "mean": statistics.mean(total_wait_times) if total_wait_times else 0,
                    "median": statistics.median(total_wait_times) if total_wait_times else 0,
                    "min": min(total_wait_times) if total_wait_times else 0,
                    "max": max(total_wait_times) if total_wait_times else 0
                },
                "success_rate": {
                    "mean": statistics.mean(success_rates) if success_rates else 0,
                    "min": min(success_rates) if success_rates else 0
                },
                "max_retry_delay": {
                    "mean": statistics.mean(max_retry_delays) if max_retry_delays else 0,
                    "max": max(max_retry_delays) if max_retry_delays else 0
                },
                "total_retries": {
                    "mean": statistics.mean(total_retries_list) if total_retries_list else 0,
                    "max": max(total_retries_list) if total_retries_list else 0
                }
            },
            "strategy_statistics": strategy_stats,
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/exponential_backoff_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de backoff exponencial salvo: exponential_backoff_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de backoff exponencial iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de backoff exponencial finalizado") 