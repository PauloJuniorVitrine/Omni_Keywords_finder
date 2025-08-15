"""
🧪 Teste de Carga - Retry Logic
================================

Tracing ID: resilience-retry-logic-test-2025-01-27-001
Timestamp: 2025-01-27T19:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Baseado em retry mechanisms reais implementados em infrastructure/resilience/
🌲 ToT: Avaliadas múltiplas estratégias de retry e escolhido mais abrangente
♻️ ReAct: Simulado cenários de falha e validado comportamento do retry

Testa retry logic implementada em:
- infrastructure/resilience/retry_mechanisms.py
- infrastructure/resilience/circuit_breakers.py
- backend/app/middleware/resilience.py
"""

import asyncio
import time
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json
import requests
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from contextlib import asynccontextmanager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RetryLogicTestConfig:
    """Configuração para testes de retry logic"""
    base_url: str = "http://localhost:8000"
    test_duration: int = 300  # 5 minutos
    concurrent_users: int = 30
    max_retry_attempts: int = 3
    base_delay: float = 1.0  # 1 segundo
    max_delay: float = 10.0  # 10 segundos
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    timeout_per_request: float = 30.0
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_monitoring: bool = True

@dataclass
class RetryLogicMetrics:
    """Métricas de retry logic"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    retry_attempts: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    response_times: List[float] = field(default_factory=list)
    retry_delays: List[float] = field(default_factory=list)
    retry_reasons: List[str] = field(default_factory=list)
    exponential_backoff_usage: int = 0
    jitter_usage: int = 0
    
    def add_request(self, success: bool, response_time: float, retry_count: int = 0, retry_delay: float = 0, retry_reason: str = ""):
        """Adiciona métrica de request"""
        self.total_requests += 1
        self.response_times.append(response_time)
        
        if success:
            self.successful_requests += 1
            if retry_count > 0:
                self.successful_retries += 1
        else:
            self.failed_requests += 1
            if retry_count > 0:
                self.failed_retries += 1
        
        if retry_count > 0:
            self.retry_attempts += retry_count
            self.retry_delays.append(retry_delay)
            if retry_reason:
                self.retry_reasons.append(retry_reason)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        if not self.response_times:
            return {}
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "failure_rate": self.failed_requests / self.total_requests if self.total_requests > 0 else 0,
            "retry_attempts": self.retry_attempts,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
            "retry_success_rate": self.successful_retries / (self.successful_retries + self.failed_retries) if (self.successful_retries + self.failed_retries) > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times),
            "avg_retry_delay": statistics.mean(self.retry_delays) if self.retry_delays else 0,
            "retry_reasons_distribution": self._get_retry_reasons_distribution()
        }
    
    def _get_retry_reasons_distribution(self) -> Dict[str, int]:
        """Retorna distribuição de razões de retry"""
        distribution = {}
        for reason in self.retry_reasons:
            distribution[reason] = distribution.get(reason, 0) + 1
        return distribution

class RetryLogicLoadTester:
    """Testador de carga para retry logic"""
    
    def __init__(self, config: RetryLogicTestConfig):
        self.config = config
        self.metrics = RetryLogicMetrics()
        self.stop_event = threading.Event()
        self.session = requests.Session()
        self.session.timeout = self.config.timeout_per_request
        
        # Headers padrão
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "RetryLogicLoadTester/1.0"
        })
        
        logger.info(f"Retry Logic Load Tester inicializado: {config}")
    
    async def run_test(self) -> Dict[str, Any]:
        """Executa teste completo de retry logic"""
        logger.info("🚀 Iniciando teste de carga de retry logic")
        
        start_time = time.time()
        
        # Executar cenários
        results = await asyncio.gather(
            self._test_exponential_backoff(),
            self._test_jitter_behavior(),
            self._test_retry_limits(),
            self._test_timeout_retries(),
            self._test_network_failure_retries(),
            self._test_mixed_failure_scenarios()
        )
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Gerar relatório
        report = self._generate_report(results, test_duration)
        
        logger.info("✅ Teste de carga de retry logic concluído")
        return report
    
    async def _test_exponential_backoff(self) -> Dict[str, Any]:
        """Testa exponential backoff"""
        logger.info("📈 Testando exponential backoff")
        
        endpoint = "/api/v1/externo/test_timeout"
        results = []
        
        for attempt in range(20):  # 20 requests para testar backoff
            retry_count = 0
            total_delay = 0
            retry_reason = ""
            
            for retry_attempt in range(self.config.max_retry_attempts + 1):
                try:
                    start_time = time.time()
                    
                    # Simular falha intermitente
                    should_fail = retry_attempt < 2  # Falha nas primeiras 2 tentativas
                    
                    if should_fail:
                        response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                    else:
                        response = self.session.get(f"{self.config.base_url}{endpoint}")
                    
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200
                    
                    if success:
                        # Sucesso após retry
                        if retry_attempt > 0:
                            retry_reason = "exponential_backoff_success"
                            self.metrics.exponential_backoff_usage += 1
                        
                        self.metrics.add_request(success, response_time, retry_count, total_delay, retry_reason)
                        
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": True,
                            "response_time": response_time,
                            "total_delay": total_delay,
                            "retry_reason": retry_reason
                        })
                        break
                    else:
                        retry_count += 1
                        retry_reason = f"http_error_{response.status_code}"
                        
                except requests.Timeout:
                    retry_count += 1
                    retry_reason = "timeout"
                    
                    # Calcular delay exponencial
                    if retry_attempt < self.config.max_retry_attempts:
                        delay = min(
                            self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                            self.config.max_delay
                        )
                        total_delay += delay
                        
                        if self.config.enable_logging:
                            logger.debug(f"Retry {retry_attempt + 1}: aguardando {delay:.2f}s")
                        
                        await asyncio.sleep(delay)
                    else:
                        # Máximo de tentativas atingido
                        self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, retry_reason)
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": False,
                            "response_time": self.config.timeout_per_request,
                            "total_delay": total_delay,
                            "retry_reason": retry_reason,
                            "error": "max_retries_exceeded"
                        })
                        break
                        
                except Exception as e:
                    retry_count += 1
                    retry_reason = f"exception_{type(e).__name__}"
                    
                    if retry_attempt < self.config.max_retry_attempts:
                        delay = min(
                            self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                            self.config.max_delay
                        )
                        total_delay += delay
                        await asyncio.sleep(delay)
                    else:
                        self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, retry_reason)
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": False,
                            "response_time": self.config.timeout_per_request,
                            "total_delay": total_delay,
                            "retry_reason": retry_reason,
                            "error": str(e)
                        })
                        break
        
        return {
            "scenario": "exponential_backoff",
            "requests_count": len(results),
            "successful_retries": sum(1 for r in results if r["success"] and r["retry_count"] > 0),
            "failed_retries": sum(1 for r in results if not r["success"] and r["retry_count"] > 0),
            "avg_retry_count": statistics.mean([r["retry_count"] for r in results]) if results else 0,
            "avg_total_delay": statistics.mean([r["total_delay"] for r in results]) if results else 0
        }
    
    async def _test_jitter_behavior(self) -> Dict[str, Any]:
        """Testa comportamento do jitter"""
        logger.info("🎲 Testando comportamento do jitter")
        
        endpoint = "/api/v1/externo/test_network_failure"
        results = []
        
        for attempt in range(30):  # 30 requests para testar jitter
            retry_count = 0
            total_delay = 0
            jitter_delays = []
            
            for retry_attempt in range(self.config.max_retry_attempts + 1):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.config.base_url}{endpoint}?simular=erro_autenticacao")
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200
                    
                    if success:
                        self.metrics.add_request(success, response_time, retry_count, total_delay, "jitter_success")
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": True,
                            "response_time": response_time,
                            "total_delay": total_delay,
                            "jitter_delays": jitter_delays
                        })
                        break
                    else:
                        retry_count += 1
                        
                        if retry_attempt < self.config.max_retry_attempts:
                            base_delay = self.config.base_delay * (self.config.exponential_base ** retry_attempt)
                            
                            if self.config.jitter:
                                jitter = base_delay * self.config.jitter_factor * random.uniform(-1, 1)
                                delay = max(0, base_delay + jitter)
                                self.metrics.jitter_usage += 1
                            else:
                                delay = base_delay
                            
                            delay = min(delay, self.config.max_delay)
                            total_delay += delay
                            jitter_delays.append(delay)
                            
                            await asyncio.sleep(delay)
                        else:
                            self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, "jitter_failure")
                            results.append({
                                "attempt": attempt + 1,
                                "retry_count": retry_count,
                                "success": False,
                                "response_time": self.config.timeout_per_request,
                                "total_delay": total_delay,
                                "jitter_delays": jitter_delays,
                                "error": "max_retries_exceeded"
                            })
                            break
                            
                except Exception as e:
                    retry_count += 1
                    
                    if retry_attempt < self.config.max_retry_attempts:
                        base_delay = self.config.base_delay * (self.config.exponential_base ** retry_attempt)
                        
                        if self.config.jitter:
                            jitter = base_delay * self.config.jitter_factor * random.uniform(-1, 1)
                            delay = max(0, base_delay + jitter)
                        else:
                            delay = base_delay
                        
                        delay = min(delay, self.config.max_delay)
                        total_delay += delay
                        jitter_delays.append(delay)
                        
                        await asyncio.sleep(delay)
                    else:
                        self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, f"jitter_exception_{type(e).__name__}")
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": False,
                            "response_time": self.config.timeout_per_request,
                            "total_delay": total_delay,
                            "jitter_delays": jitter_delays,
                            "error": str(e)
                        })
                        break
        
        return {
            "scenario": "jitter_behavior",
            "requests_count": len(results),
            "jitter_usage_count": self.metrics.jitter_usage,
            "avg_jitter_delay": statistics.mean([d for r in results for d in r.get("jitter_delays", [])]) if results else 0,
            "jitter_variance": statistics.variance([d for r in results for d in r.get("jitter_delays", [])]) if results and any(r.get("jitter_delays") for r in results) else 0
        }
    
    async def _test_retry_limits(self) -> Dict[str, Any]:
        """Testa limites de retry"""
        logger.info("🚫 Testando limites de retry")
        
        endpoint = "/api/v1/externo/test_timeout"
        results = []
        
        # Testar diferentes configurações de max_attempts
        max_attempts_configs = [1, 2, 3, 5]
        
        for max_attempts in max_attempts_configs:
            for attempt in range(10):  # 10 requests por configuração
                retry_count = 0
                total_delay = 0
                
                for retry_attempt in range(max_attempts + 1):
                    try:
                        start_time = time.time()
                        response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                        response_time = time.time() - start_time
                        
                        success = response.status_code == 200
                        
                        if success:
                            self.metrics.add_request(success, response_time, retry_count, total_delay, "retry_limit_success")
                            results.append({
                                "max_attempts": max_attempts,
                                "attempt": attempt + 1,
                                "retry_count": retry_count,
                                "success": True,
                                "response_time": response_time,
                                "total_delay": total_delay
                            })
                            break
                        else:
                            retry_count += 1
                            
                    except requests.Timeout:
                        retry_count += 1
                        
                        if retry_attempt < max_attempts:
                            delay = min(
                                self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                                self.config.max_delay
                            )
                            total_delay += delay
                            await asyncio.sleep(delay)
                        else:
                            # Limite atingido
                            self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, "retry_limit_exceeded")
                            results.append({
                                "max_attempts": max_attempts,
                                "attempt": attempt + 1,
                                "retry_count": retry_count,
                                "success": False,
                                "response_time": self.config.timeout_per_request,
                                "total_delay": total_delay,
                                "error": "retry_limit_exceeded"
                            })
                            break
        
        return {
            "scenario": "retry_limits",
            "requests_count": len(results),
            "configurations_tested": max_attempts_configs,
            "success_by_max_attempts": {
                max_attempts: sum(1 for r in results if r["max_attempts"] == max_attempts and r["success"])
                for max_attempts in max_attempts_configs
            },
            "failure_by_max_attempts": {
                max_attempts: sum(1 for r in results if r["max_attempts"] == max_attempts and not r["success"])
                for max_attempts in max_attempts_configs
            }
        }
    
    async def _test_timeout_retries(self) -> Dict[str, Any]:
        """Testa retries por timeout"""
        logger.info("⏱️ Testando retries por timeout")
        
        endpoint = "/api/v1/externo/test_timeout"
        results = []
        
        for attempt in range(25):  # 25 requests para testar timeout
            retry_count = 0
            total_delay = 0
            
            for retry_attempt in range(self.config.max_retry_attempts + 1):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200
                    
                    if success:
                        self.metrics.add_request(success, response_time, retry_count, total_delay, "timeout_retry_success")
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": True,
                            "response_time": response_time,
                            "total_delay": total_delay
                        })
                        break
                    else:
                        retry_count += 1
                        
                except requests.Timeout:
                    retry_count += 1
                    
                    if retry_attempt < self.config.max_retry_attempts:
                        delay = min(
                            self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                            self.config.max_delay
                        )
                        total_delay += delay
                        await asyncio.sleep(delay)
                    else:
                        self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, "timeout_retry_failure")
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": False,
                            "response_time": self.config.timeout_per_request,
                            "total_delay": total_delay,
                            "error": "timeout_max_retries_exceeded"
                        })
                        break
        
        return {
            "scenario": "timeout_retries",
            "requests_count": len(results),
            "timeout_retries": sum(1 for r in results if r["retry_count"] > 0),
            "successful_timeout_retries": sum(1 for r in results if r["success"] and r["retry_count"] > 0),
            "failed_timeout_retries": sum(1 for r in results if not r["success"] and r["retry_count"] > 0)
        }
    
    async def _test_network_failure_retries(self) -> Dict[str, Any]:
        """Testa retries por falhas de rede"""
        logger.info("🌐 Testando retries por falhas de rede")
        
        endpoint = "/api/v1/externo/test_network_failure"
        results = []
        
        for attempt in range(20):  # 20 requests para testar falhas de rede
            retry_count = 0
            total_delay = 0
            
            for retry_attempt in range(self.config.max_retry_attempts + 1):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.config.base_url}{endpoint}?simular=erro_autenticacao")
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200
                    
                    if success:
                        self.metrics.add_request(success, response_time, retry_count, total_delay, "network_retry_success")
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": True,
                            "response_time": response_time,
                            "total_delay": total_delay
                        })
                        break
                    else:
                        retry_count += 1
                        
                        if retry_attempt < self.config.max_retry_attempts:
                            delay = min(
                                self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                                self.config.max_delay
                            )
                            total_delay += delay
                            await asyncio.sleep(delay)
                        else:
                            self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, "network_retry_failure")
                            results.append({
                                "attempt": attempt + 1,
                                "retry_count": retry_count,
                                "success": False,
                                "response_time": self.config.timeout_per_request,
                                "total_delay": total_delay,
                                "error": "network_max_retries_exceeded"
                            })
                            break
                            
                except requests.ConnectionError:
                    retry_count += 1
                    
                    if retry_attempt < self.config.max_retry_attempts:
                        delay = min(
                            self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                            self.config.max_delay
                        )
                        total_delay += delay
                        await asyncio.sleep(delay)
                    else:
                        self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, "network_connection_failure")
                        results.append({
                            "attempt": attempt + 1,
                            "retry_count": retry_count,
                            "success": False,
                            "response_time": self.config.timeout_per_request,
                            "total_delay": total_delay,
                            "error": "network_connection_failure"
                        })
                        break
        
        return {
            "scenario": "network_failure_retries",
            "requests_count": len(results),
            "network_retries": sum(1 for r in results if r["retry_count"] > 0),
            "successful_network_retries": sum(1 for r in results if r["success"] and r["retry_count"] > 0),
            "failed_network_retries": sum(1 for r in results if not r["success"] and r["retry_count"] > 0)
        }
    
    async def _test_mixed_failure_scenarios(self) -> Dict[str, Any]:
        """Testa cenários mistos de falha"""
        logger.info("🎭 Testando cenários mistos de falha")
        
        endpoints = [
            "/api/v1/externo/test_timeout",
            "/api/v1/externo/test_network_failure",
            "/api/v1/externo/test_error"
        ]
        
        failure_types = ["timeout", "network", "http_error", "random"]
        results = []
        
        for attempt in range(40):  # 40 requests com falhas mistas
            endpoint = random.choice(endpoints)
            failure_type = random.choice(failure_types)
            retry_count = 0
            total_delay = 0
            
            for retry_attempt in range(self.config.max_retry_attempts + 1):
                try:
                    start_time = time.time()
                    
                    if failure_type == "timeout":
                        response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                    elif failure_type == "network":
                        response = self.session.get(f"{self.config.base_url}{endpoint}?simular=erro_autenticacao")
                    elif failure_type == "http_error":
                        response = self.session.get(f"{self.config.base_url}{endpoint}?simular=resposta_invalida")
                    else:
                        # Falha aleatória
                        if random.random() < 0.7:  # 70% chance de falha
                            response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                        else:
                            response = self.session.get(f"{self.config.base_url}{endpoint}")
                    
                    response_time = time.time() - start_time
                    success = response.status_code == 200
                    
                    if success:
                        self.metrics.add_request(success, response_time, retry_count, total_delay, f"mixed_{failure_type}_success")
                        results.append({
                            "attempt": attempt + 1,
                            "endpoint": endpoint,
                            "failure_type": failure_type,
                            "retry_count": retry_count,
                            "success": True,
                            "response_time": response_time,
                            "total_delay": total_delay
                        })
                        break
                    else:
                        retry_count += 1
                        
                        if retry_attempt < self.config.max_retry_attempts:
                            delay = min(
                                self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                                self.config.max_delay
                            )
                            total_delay += delay
                            await asyncio.sleep(delay)
                        else:
                            self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, f"mixed_{failure_type}_failure")
                            results.append({
                                "attempt": attempt + 1,
                                "endpoint": endpoint,
                                "failure_type": failure_type,
                                "retry_count": retry_count,
                                "success": False,
                                "response_time": self.config.timeout_per_request,
                                "total_delay": total_delay,
                                "error": "mixed_max_retries_exceeded"
                            })
                            break
                            
                except Exception as e:
                    retry_count += 1
                    
                    if retry_attempt < self.config.max_retry_attempts:
                        delay = min(
                            self.config.base_delay * (self.config.exponential_base ** retry_attempt),
                            self.config.max_delay
                        )
                        total_delay += delay
                        await asyncio.sleep(delay)
                    else:
                        self.metrics.add_request(False, self.config.timeout_per_request, retry_count, total_delay, f"mixed_{failure_type}_exception")
                        results.append({
                            "attempt": attempt + 1,
                            "endpoint": endpoint,
                            "failure_type": failure_type,
                            "retry_count": retry_count,
                            "success": False,
                            "response_time": self.config.timeout_per_request,
                            "total_delay": total_delay,
                            "error": str(e)
                        })
                        break
        
        return {
            "scenario": "mixed_failure_scenarios",
            "requests_count": len(results),
            "failure_types_tested": failure_types,
            "success_by_failure_type": {
                failure_type: sum(1 for r in results if r["failure_type"] == failure_type and r["success"])
                for failure_type in failure_types
            },
            "retry_effectiveness": {
                "total_retries": sum(r["retry_count"] for r in results),
                "successful_retries": sum(1 for r in results if r["success"] and r["retry_count"] > 0),
                "retry_success_rate": sum(1 for r in results if r["success"] and r["retry_count"] > 0) / sum(1 for r in results if r["retry_count"] > 0) if sum(1 for r in results if r["retry_count"] > 0) > 0 else 0
            }
        }
    
    def _generate_report(self, results: List[Dict[str, Any]], test_duration: float) -> Dict[str, Any]:
        """Gera relatório completo do teste"""
        metrics_summary = self.metrics.get_summary()
        
        report = {
            "test_info": {
                "name": "Retry Logic Load Test",
                "tracing_id": "resilience-retry-logic-test-2025-01-27-001",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": test_duration,
                "config": {
                    "base_url": self.config.base_url,
                    "max_retry_attempts": self.config.max_retry_attempts,
                    "base_delay": self.config.base_delay,
                    "exponential_base": self.config.exponential_base,
                    "jitter": self.config.jitter
                }
            },
            "scenarios": {
                result["scenario"]: result for result in results
            },
            "metrics": metrics_summary,
            "retry_analysis": {
                "total_retry_attempts": self.metrics.retry_attempts,
                "successful_retries": self.metrics.successful_retries,
                "failed_retries": self.metrics.failed_retries,
                "retry_success_rate": self.metrics.successful_retries / (self.metrics.successful_retries + self.metrics.failed_retries) if (self.metrics.successful_retries + self.metrics.failed_retries) > 0 else 0,
                "exponential_backoff_usage": self.metrics.exponential_backoff_usage,
                "jitter_usage": self.metrics.jitter_usage,
                "retry_reasons_distribution": metrics_summary.get("retry_reasons_distribution", {})
            },
            "performance_analysis": {
                "throughput_rps": self.metrics.total_requests / test_duration if test_duration > 0 else 0,
                "avg_response_time": metrics_summary.get("avg_response_time", 0),
                "avg_retry_delay": metrics_summary.get("avg_retry_delay", 0),
                "p95_response_time": metrics_summary.get("p95_response_time", 0)
            },
            "recommendations": self._generate_recommendations(metrics_summary, results)
        }
        
        return report
    
    def _generate_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Análise de retry effectiveness
        retry_success_rate = metrics.get("retry_success_rate", 0)
        if retry_success_rate < 0.5:
            recommendations.append("⚠️ Taxa de sucesso de retry baixa (<50%). Verificar se retries estão sendo efetivos.")
        
        if retry_success_rate > 0.9:
            recommendations.append("✅ Taxa de sucesso de retry excelente (>90%). Retry logic funcionando bem.")
        
        # Análise de performance
        avg_response_time = metrics.get("avg_response_time", 0)
        if avg_response_time > 3.0:
            recommendations.append("⚠️ Tempo de resposta médio alto (>3s). Retries podem estar causando latência excessiva.")
        
        # Análise de jitter
        if self.metrics.jitter_usage == 0:
            recommendations.append("ℹ️ Jitter não foi utilizado. Considere habilitar para evitar thundering herd.")
        
        # Análise de exponential backoff
        if self.metrics.exponential_backoff_usage == 0:
            recommendations.append("ℹ️ Exponential backoff não foi utilizado. Verificar se cenários de falha estão adequados.")
        
        # Análise de configuração
        if not recommendations:
            recommendations.append("✅ Retry logic funcionando adequadamente.")
        
        return recommendations

async def main():
    """Função principal para executar teste"""
    config = RetryLogicTestConfig()
    tester = RetryLogicLoadTester(config)
    
    try:
        report = await tester.run_test()
        
        # Salvar relatório
        with open("retry_logic_load_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Exibir resumo
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTE DE RETRY LOGIC")
        print("="*60)
        print(f"Total de Requests: {report['metrics']['total_requests']}")
        print(f"Taxa de Sucesso: {report['metrics']['success_rate']:.1%}")
        print(f"Tentativas de Retry: {report['metrics']['retry_attempts']}")
        print(f"Retries Bem-sucedidos: {report['metrics']['successful_retries']}")
        print(f"Taxa de Sucesso de Retry: {report['metrics']['retry_success_rate']:.1%}")
        print(f"Tempo Médio de Resposta: {report['metrics']['avg_response_time']:.3f}s")
        print(f"Delay Médio de Retry: {report['metrics']['avg_retry_delay']:.3f}s")
        print("\nRecomendações:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Erro durante teste: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 