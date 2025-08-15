"""
🔄 Teste de Mecanismos de Fallback de Circuit Breaker
🎯 Objetivo: Testar mecanismos de fallback quando circuit breakers estão abertos
📅 Data: 2025-01-27
🔗 Tracing ID: RESILIENCE_CIRCUIT_BREAKER_FALLBACK_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de fallbacks e circuit breakers
🌲 ToT: Avaliadas múltiplas estratégias de fallback
♻️ ReAct: Simulado cenários de falha e fallback

Testa funcionalidades baseadas em:
- infrastructure/resilience/circuit_breaker.py
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
class FallbackMetrics:
    """Métricas de fallback"""
    operation_name: str
    fallback_triggered: bool
    fallback_strategy: str
    response_time: float
    success_rate: float
    data_quality: float
    circuit_state: str
    success_count: int
    error_count: int
    timestamp: datetime

class CircuitBreakerFallbackTest(HttpUser):
    """
    Teste de mecanismos de fallback de circuit breakers
    Baseado em código real de resiliência
    """
    
    wait_time = between(3, 6)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[FallbackMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'fallback_thresholds': {
                'max_response_time': 5.0,
                'min_success_rate': 0.7,
                'min_data_quality': 0.6
            },
            'fallback_strategies': ['cache', 'default_values', 'degraded_service', 'alternative_endpoint'],
            'circuit_states': ['CLOSED', 'OPEN', 'HALF_OPEN'],
            'service_types': ['database', 'external_api', 'cache', 'file_system']
        }
        
        logger.info(f"Teste de fallback de circuit breaker iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_fallback_report()
    
    @task(3)
    def test_cache_fallback(self):
        """Teste de fallback para cache"""
        self._test_fallback_strategy("cache", service_type="database")
    
    @task(2)
    def test_default_values_fallback(self):
        """Teste de fallback para valores padrão"""
        self._test_fallback_strategy("default_values", service_type="external_api")
    
    @task(2)
    def test_degraded_service_fallback(self):
        """Teste de fallback para serviço degradado"""
        self._test_fallback_strategy("degraded_service", service_type="cache")
    
    @task(1)
    def test_alternative_endpoint_fallback(self):
        """Teste de fallback para endpoint alternativo"""
        self._test_fallback_strategy("alternative_endpoint", service_type="file_system")
    
    @task(1)
    def test_multi_strategy_fallback(self):
        """Teste de fallback com múltiplas estratégias"""
        self._test_multi_strategy_fallback()
    
    def _test_fallback_strategy(self, fallback_strategy: str, service_type: str):
        """Teste de estratégia de fallback específica"""
        start_time = time.time()
        
        try:
            # Preparar payload para forçar circuit breaker aberto
            payload = {
                "service_type": service_type,
                "force_circuit_open": True,
                "fallback_strategy": fallback_strategy,
                "request_data": {
                    "operation": "read",
                    "resource": f"test_resource_{random.randint(1, 1000)}",
                    "parameters": {
                        "limit": 10,
                        "offset": 0,
                        "filters": {"status": "active"}
                    }
                }
            }
            
            # Executar requisição que deve ativar fallback
            with self.client.post(
                "/api/resilience/fallback-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Fallback-Strategy": fallback_strategy,
                    "X-Service-Type": service_type,
                    "X-Force-Circuit-Open": "true"
                },
                catch_response=True,
                timeout=30
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações do fallback
                    fallback_triggered = response_data.get('fallback_triggered', False)
                    actual_strategy = response_data.get('fallback_strategy', 'none')
                    circuit_state = response_data.get('circuit_state', 'UNKNOWN')
                    data_quality = response_data.get('data_quality', 0.0)
                    
                    # Calcular taxa de sucesso
                    success_count = 1 if fallback_triggered else 0
                    error_count = 0 if fallback_triggered else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = FallbackMetrics(
                        operation_name=f"fallback_{fallback_strategy}_{service_type}",
                        fallback_triggered=fallback_triggered,
                        fallback_strategy=actual_strategy,
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
                    self._validate_fallback_thresholds(metrics, fallback_strategy)
                    
                    response.success()
                    logger.info(f"Fallback {fallback_strategy} para {service_type} bem-sucedido: {response_time:.2f}s, qualidade: {data_quality:.3f}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = FallbackMetrics(
                        operation_name=f"fallback_{fallback_strategy}_{service_type}_error",
                        fallback_triggered=False,
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
            
            metrics = FallbackMetrics(
                operation_name=f"fallback_{fallback_strategy}_{service_type}_exception",
                fallback_triggered=False,
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
            
            logger.error(f"Erro no teste de fallback {fallback_strategy} para {service_type}: {str(e)}")
    
    def _test_multi_strategy_fallback(self):
        """Teste de fallback com múltiplas estratégias"""
        start_time = time.time()
        
        try:
            # Preparar payload para teste de múltiplas estratégias
            payload = {
                "multi_strategy_fallback": True,
                "strategies": [
                    {"strategy": "cache", "priority": 1},
                    {"strategy": "default_values", "priority": 2},
                    {"strategy": "degraded_service", "priority": 3},
                    {"strategy": "alternative_endpoint", "priority": 4}
                ],
                "service_type": "database",
                "request_data": {
                    "operation": "complex_query",
                    "resource": "analytics_data",
                    "parameters": {
                        "date_range": "last_30_days",
                        "metrics": ["views", "clicks", "conversions"],
                        "group_by": ["date", "campaign"]
                    }
                }
            }
            
            # Executar requisição com múltiplas estratégias
            with self.client.post(
                "/api/resilience/multi-fallback-test",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Multi-Strategy": "true",
                    "X-Service-Type": "database"
                },
                catch_response=True,
                timeout=45
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extrair informações do fallback múltiplo
                    fallback_triggered = response_data.get('fallback_triggered', False)
                    strategies_used = response_data.get('strategies_used', [])
                    primary_strategy = strategies_used[0] if strategies_used else "none"
                    circuit_state = response_data.get('circuit_state', 'UNKNOWN')
                    data_quality = response_data.get('data_quality', 0.0)
                    
                    # Calcular métricas
                    success_count = 1 if fallback_triggered else 0
                    error_count = 0 if fallback_triggered else 1
                    success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
                    
                    # Registrar métricas
                    metrics = FallbackMetrics(
                        operation_name="multi_strategy_fallback",
                        fallback_triggered=fallback_triggered,
                        fallback_strategy=primary_strategy,
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
                    self._validate_fallback_thresholds(metrics, "multi_strategy")
                    
                    response.success()
                    logger.info(f"Fallback múltiplo bem-sucedido: {response_time:.2f}s, estratégias: {strategies_used}, qualidade: {data_quality:.3f}")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
                    # Registrar métricas de falha
                    metrics = FallbackMetrics(
                        operation_name="multi_strategy_fallback_error",
                        fallback_triggered=False,
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
            
            metrics = FallbackMetrics(
                operation_name="multi_strategy_fallback_exception",
                fallback_triggered=False,
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
            
            logger.error(f"Erro no teste de fallback múltiplo: {str(e)}")
    
    def _validate_fallback_thresholds(self, metrics: FallbackMetrics, strategy: str):
        """Validar thresholds de fallback"""
        thresholds = self.test_config['fallback_thresholds']
        
        # Validar tempo de resposta
        if metrics.response_time > thresholds['max_response_time']:
            logger.warning(f"Tempo de resposta alto para fallback {strategy}: {metrics.response_time:.2f}s > {thresholds['max_response_time']}s")
        
        # Validar taxa de sucesso
        if metrics.success_rate < thresholds['min_success_rate']:
            logger.warning(f"Taxa de sucesso baixa para fallback {strategy}: {metrics.success_rate:.3f} < {thresholds['min_success_rate']}")
        
        # Validar qualidade dos dados
        if metrics.data_quality < thresholds['min_data_quality']:
            logger.warning(f"Qualidade de dados baixa para fallback {strategy}: {metrics.data_quality:.3f} < {thresholds['min_data_quality']}")
        
        # Validar se fallback foi acionado quando necessário
        if not metrics.fallback_triggered and metrics.circuit_state == "OPEN":
            logger.warning(f"Fallback não foi acionado para {strategy} com circuit breaker aberto")
    
    def _generate_fallback_report(self):
        """Gerar relatório de fallback"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        response_times = [m.response_time for m in self.metrics]
        success_rates = [m.success_rate for m in self.metrics]
        data_qualities = [m.data_quality for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        # Agrupar por estratégia
        strategy_stats = {}
        for metric in self.metrics:
            strategy = metric.fallback_strategy
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'response_times': [],
                    'data_qualities': []
                }
            
            strategy_stats[strategy]['count'] += 1
            strategy_stats[strategy]['success_count'] += metric.success_count
            strategy_stats[strategy]['error_count'] += metric.error_count
            strategy_stats[strategy]['response_times'].append(metric.response_time)
            strategy_stats[strategy]['data_qualities'].append(metric.data_quality)
        
        # Calcular estatísticas por estratégia
        for strategy, stats in strategy_stats.items():
            if stats['response_times']:
                stats['avg_response_time'] = statistics.mean(stats['response_times'])
                stats['avg_data_quality'] = statistics.mean(stats['data_qualities'])
                stats['success_rate'] = stats['success_count'] / (stats['success_count'] + stats['error_count']) if (stats['success_count'] + stats['error_count']) > 0 else 0
            else:
                stats['avg_response_time'] = 0
                stats['avg_data_quality'] = 0
                stats['success_rate'] = 0
        
        report = {
            "test_name": "Circuit Breaker Fallback Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_successful_fallbacks": total_success,
            "total_failed_fallbacks": total_errors,
            "fallback_success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "fallback_metrics": {
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
                }
            },
            "strategy_statistics": strategy_stats,
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/circuit_breaker_fallback_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de fallback de circuit breaker salvo: circuit_breaker_fallback_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de fallback de circuit breaker iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de fallback de circuit breaker finalizado") 