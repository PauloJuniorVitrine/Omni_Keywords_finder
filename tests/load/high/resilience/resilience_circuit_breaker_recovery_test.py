"""
🔄 Teste de Recuperação de Circuit Breaker
🎯 Objetivo: Testar recuperação automática de circuit breakers
📅 Data: 2025-01-27
🔗 Tracing ID: RESILIENCE_CIRCUIT_BREAKER_RECOVERY_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de circuit breakers e recuperação
🌲 ToT: Avaliadas múltiplas estratégias de recuperação
♻️ ReAct: Simulado cenários de falha e recuperação

Testa funcionalidades baseadas em:
- infrastructure/resilience/circuit_breaker.py
- backend/app/middleware/resilience.py
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
class CircuitBreakerRecoveryMetrics:
    """Métricas de recuperação de circuit breaker"""
    operation_name: str
    failure_count: int
    recovery_time: float
    success_rate: float
    circuit_state: str
    attempts_before_recovery: int
    success_count: int
    error_count: int
    timestamp: datetime

class CircuitBreakerRecoveryTest(HttpUser):
    """
    Teste de recuperação de circuit breakers
    Baseado em código real de resiliência
    """
    
    wait_time = between(2, 4)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[CircuitBreakerRecoveryMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'recovery_thresholds': {
                'max_recovery_time': 30.0,
                'min_success_rate': 0.8,
                'max_attempts_before_recovery': 10
            },
            'circuit_states': ['CLOSED', 'OPEN', 'HALF_OPEN'],
            'failure_scenarios': ['timeout', 'connection_error', 'server_error', 'rate_limit'],
            'recovery_strategies': ['immediate', 'exponential_backoff', 'linear_backoff']
        }
        
        logger.info(f"Teste de recuperação de circuit breaker iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_recovery_report()
    
    @task(3)
    def test_circuit_breaker_timeout_recovery(self):
        """Teste de recuperação após timeout"""
        self._test_circuit_breaker_recovery("timeout", failure_count=5)
    
    @task(2)
    def test_circuit_breaker_connection_recovery(self):
        """Teste de recuperação após erro de conexão"""
        self._test_circuit_breaker_recovery("connection_error", failure_count=3)
    
    @task(2)
    def test_circuit_breaker_server_error_recovery(self):
        """Teste de recuperação após erro do servidor"""
        self._test_circuit_breaker_recovery("server_error", failure_count=4)
    
    @task(1)
    def test_circuit_breaker_rate_limit_recovery(self):
        """Teste de recuperação após rate limit"""
        self._test_circuit_breaker_recovery("rate_limit", failure_count=6)
    
    @task(1)
    def test_circuit_breaker_automatic_recovery(self):
        """Teste de recuperação automática"""
        self._test_automatic_recovery()
    
    def _test_circuit_breaker_recovery(self, failure_type: str, failure_count: int):
        """Teste de recuperação de circuit breaker"""
        start_time = time.time()
        recovery_start_time = None
        attempts_before_recovery = 0
        success_count = 0
        error_count = 0
        circuit_state = "CLOSED"
        
        try:
            # Fase 1: Induzir falhas para abrir o circuit breaker
            logger.info(f"Induzindo falhas do tipo {failure_type} para abrir circuit breaker")
            
            for i in range(failure_count):
                try:
                    # Simular falha baseada no tipo
                    if failure_type == "timeout":
                        response = self.client.get(
                            "/api/resilience/timeout-test",
                            timeout=1,  # Timeout muito baixo para forçar falha
                            catch_response=True
                        )
                    elif failure_type == "connection_error":
                        response = self.client.get(
                            "/api/resilience/connection-test",
                            headers={"X-Force-Connection-Error": "true"},
                            catch_response=True
                        )
                    elif failure_type == "server_error":
                        response = self.client.get(
                            "/api/resilience/server-error-test",
                            headers={"X-Force-Server-Error": "500"},
                            catch_response=True
                        )
                    elif failure_type == "rate_limit":
                        response = self.client.get(
                            "/api/resilience/rate-limit-test",
                            headers={"X-Force-Rate-Limit": "true"},
                            catch_response=True
                        )
                    
                    if response.status_code >= 500 or response.status_code == 429:
                        error_count += 1
                        circuit_state = "OPEN" if error_count >= 3 else "HALF_OPEN"
                    else:
                        success_count += 1
                        
                except Exception as e:
                    error_count += 1
                    circuit_state = "OPEN" if error_count >= 3 else "HALF_OPEN"
                    logger.debug(f"Falha {i+1}: {str(e)}")
            
            # Fase 2: Aguardar e testar recuperação
            logger.info(f"Circuit breaker aberto. Aguardando recuperação...")
            recovery_start_time = time.time()
            
            # Tentar recuperação com diferentes estratégias
            recovery_strategy = random.choice(self.test_config['recovery_strategies'])
            
            while attempts_before_recovery < self.test_config['recovery_thresholds']['max_attempts_before_recovery']:
                try:
                    # Aguardar baseado na estratégia de recuperação
                    if recovery_strategy == "exponential_backoff":
                        wait_time = min(2 ** attempts_before_recovery, 30)
                    elif recovery_strategy == "linear_backoff":
                        wait_time = attempts_before_recovery * 2
                    else:  # immediate
                        wait_time = 1
                    
                    time.sleep(wait_time)
                    
                    # Testar se o serviço recuperou
                    response = self.client.get(
                        "/api/resilience/health-check",
                        headers={
                            "X-Recovery-Strategy": recovery_strategy,
                            "X-Attempt": str(attempts_before_recovery + 1)
                        },
                        catch_response=True,
                        timeout=10
                    )
                    
                    attempts_before_recovery += 1
                    
                    if response.status_code == 200:
                        # Serviço recuperou
                        circuit_state = "CLOSED"
                        success_count += 1
                        logger.info(f"Recuperação bem-sucedida após {attempts_before_recovery} tentativas")
                        break
                    else:
                        error_count += 1
                        circuit_state = "HALF_OPEN"
                        
                except Exception as e:
                    error_count += 1
                    circuit_state = "HALF_OPEN"
                    attempts_before_recovery += 1
                    logger.debug(f"Tentativa de recuperação {attempts_before_recovery} falhou: {str(e)}")
            
            # Calcular métricas
            end_time = time.time()
            recovery_time = end_time - (recovery_start_time or start_time)
            success_rate = success_count / (success_count + error_count) if (success_count + error_count) > 0 else 0
            
            # Registrar métricas
            metrics = CircuitBreakerRecoveryMetrics(
                operation_name=f"circuit_breaker_{failure_type}_recovery",
                failure_count=failure_count,
                recovery_time=recovery_time,
                success_rate=success_rate,
                circuit_state=circuit_state,
                attempts_before_recovery=attempts_before_recovery,
                success_count=success_count,
                error_count=error_count,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            # Validar thresholds
            self._validate_recovery_thresholds(metrics, failure_type)
            
            logger.info(f"Teste de recuperação {failure_type} concluído: {recovery_time:.2f}s, taxa de sucesso: {success_rate:.2f}")
            
        except Exception as e:
            end_time = time.time()
            recovery_time = end_time - start_time
            
            metrics = CircuitBreakerRecoveryMetrics(
                operation_name=f"circuit_breaker_{failure_type}_recovery_error",
                failure_count=failure_count,
                recovery_time=recovery_time,
                success_rate=0.0,
                circuit_state="UNKNOWN",
                attempts_before_recovery=attempts_before_recovery,
                success_count=success_count,
                error_count=error_count + 1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de recuperação {failure_type}: {str(e)}")
    
    def _test_automatic_recovery(self):
        """Teste de recuperação automática"""
        start_time = time.time()
        
        try:
            # Simular cenário de recuperação automática
            logger.info("Testando recuperação automática de circuit breaker")
            
            # Fase 1: Induzir falhas para abrir circuit breaker
            failure_count = 0
            for i in range(5):
                try:
                    response = self.client.get(
                        "/api/resilience/auto-recovery-test",
                        headers={"X-Failure-Count": str(i)},
                        timeout=2,
                        catch_response=True
                    )
                    
                    if response.status_code >= 500:
                        failure_count += 1
                        
                except Exception:
                    failure_count += 1
            
            # Fase 2: Aguardar recuperação automática
            logger.info(f"Circuit breaker aberto após {failure_count} falhas. Aguardando recuperação automática...")
            
            recovery_start_time = time.time()
            max_wait_time = 60  # Máximo 60 segundos para recuperação automática
            check_interval = 5  # Verificar a cada 5 segundos
            
            recovered = False
            attempts = 0
            
            while time.time() - recovery_start_time < max_wait_time:
                try:
                    response = self.client.get(
                        "/api/resilience/auto-recovery-status",
                        headers={"X-Check-Attempt": str(attempts + 1)},
                        catch_response=True,
                        timeout=10
                    )
                    
                    attempts += 1
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data.get('circuit_state') == 'CLOSED':
                            recovered = True
                            break
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    attempts += 1
                    logger.debug(f"Verificação de recuperação {attempts} falhou: {str(e)}")
                    time.sleep(check_interval)
            
            # Calcular métricas
            end_time = time.time()
            recovery_time = end_time - recovery_start_time
            success_rate = 1.0 if recovered else 0.0
            
            metrics = CircuitBreakerRecoveryMetrics(
                operation_name="circuit_breaker_automatic_recovery",
                failure_count=failure_count,
                recovery_time=recovery_time,
                success_rate=success_rate,
                circuit_state="CLOSED" if recovered else "OPEN",
                attempts_before_recovery=attempts,
                success_count=1 if recovered else 0,
                error_count=0 if recovered else 1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            # Validar thresholds
            self._validate_recovery_thresholds(metrics, "automatic")
            
            if recovered:
                logger.info(f"Recuperação automática bem-sucedida em {recovery_time:.2f}s")
            else:
                logger.warning(f"Recuperação automática falhou após {recovery_time:.2f}s")
            
        except Exception as e:
            end_time = time.time()
            recovery_time = end_time - start_time
            
            metrics = CircuitBreakerRecoveryMetrics(
                operation_name="circuit_breaker_automatic_recovery_error",
                failure_count=0,
                recovery_time=recovery_time,
                success_rate=0.0,
                circuit_state="UNKNOWN",
                attempts_before_recovery=0,
                success_count=0,
                error_count=1,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no teste de recuperação automática: {str(e)}")
    
    def _validate_recovery_thresholds(self, metrics: CircuitBreakerRecoveryMetrics, failure_type: str):
        """Validar thresholds de recuperação"""
        thresholds = self.test_config['recovery_thresholds']
        
        # Validar tempo de recuperação
        if metrics.recovery_time > thresholds['max_recovery_time']:
            logger.warning(f"Tempo de recuperação alto para {failure_type}: {metrics.recovery_time:.2f}s > {thresholds['max_recovery_time']}s")
        
        # Validar taxa de sucesso
        if metrics.success_rate < thresholds['min_success_rate']:
            logger.warning(f"Taxa de sucesso baixa para {failure_type}: {metrics.success_rate:.3f} < {thresholds['min_success_rate']}")
        
        # Validar tentativas antes da recuperação
        if metrics.attempts_before_recovery > thresholds['max_attempts_before_recovery']:
            logger.warning(f"Muitas tentativas para recuperação {failure_type}: {metrics.attempts_before_recovery} > {thresholds['max_attempts_before_recovery']}")
    
    def _generate_recovery_report(self):
        """Gerar relatório de recuperação"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        recovery_times = [m.recovery_time for m in self.metrics]
        success_rates = [m.success_rate for m in self.metrics]
        attempts_counts = [m.attempts_before_recovery for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        report = {
            "test_name": "Circuit Breaker Recovery Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_successful_recoveries": total_success,
            "total_failed_recoveries": total_errors,
            "recovery_success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "recovery_metrics": {
                "recovery_time": {
                    "mean": statistics.mean(recovery_times) if recovery_times else 0,
                    "median": statistics.median(recovery_times) if recovery_times else 0,
                    "min": min(recovery_times) if recovery_times else 0,
                    "max": max(recovery_times) if recovery_times else 0
                },
                "success_rate": {
                    "mean": statistics.mean(success_rates) if success_rates else 0,
                    "min": min(success_rates) if success_rates else 0
                },
                "attempts_before_recovery": {
                    "mean": statistics.mean(attempts_counts) if attempts_counts else 0,
                    "max": max(attempts_counts) if attempts_counts else 0
                }
            },
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/circuit_breaker_recovery_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de recuperação de circuit breaker salvo: circuit_breaker_recovery_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de recuperação de circuit breaker iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de recuperação de circuit breaker finalizado") 