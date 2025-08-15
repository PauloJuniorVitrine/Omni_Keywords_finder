"""
🧪 Teste de Carga - Circuit Breakers
====================================

Tracing ID: resilience-circuit-breaker-test-2025-01-27-001
Timestamp: 2025-01-27T19:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Baseado em circuit breakers reais implementados em infrastructure/resilience/
🌲 ToT: Avaliadas múltiplas estratégias de teste e escolhido mais abrangente
♻️ ReAct: Simulado cenários de falha e validado comportamento do circuit breaker

Testa circuit breakers implementados em:
- infrastructure/resilience/circuit_breakers.py
- infrastructure/resilience/advanced_circuit_breaker.py
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
class CircuitBreakerTestConfig:
    """Configuração para testes de circuit breaker"""
    base_url: str = "http://localhost:8000"
    test_duration: int = 300  # 5 minutos
    concurrent_users: int = 50
    failure_rate_target: float = 0.3  # 30% de falhas para abrir circuit
    recovery_timeout: int = 60  # 60 segundos para recuperação
    success_threshold: int = 2  # 2 sucessos para fechar
    max_requests_per_user: int = 100
    timeout_per_request: float = 30.0
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_monitoring: bool = True

@dataclass
class CircuitBreakerMetrics:
    """Métricas de circuit breaker"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_open_requests: int = 0
    circuit_half_open_requests: int = 0
    circuit_closed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    failure_times: List[datetime] = field(default_factory=list)
    recovery_times: List[datetime] = field(default_factory=list)
    state_transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_request(self, success: bool, response_time: float, circuit_state: str):
        """Adiciona métrica de request"""
        self.total_requests += 1
        self.response_times.append(response_time)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            self.failure_times.append(datetime.now())
        
        if circuit_state == "open":
            self.circuit_open_requests += 1
        elif circuit_state == "half_open":
            self.circuit_half_open_requests += 1
        else:
            self.circuit_closed_requests += 1
    
    def add_state_transition(self, from_state: str, to_state: str, reason: str):
        """Adiciona transição de estado"""
        self.state_transitions.append({
            "from_state": from_state,
            "to_state": to_state,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
    
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
            "circuit_open_requests": self.circuit_open_requests,
            "circuit_half_open_requests": self.circuit_half_open_requests,
            "circuit_closed_requests": self.circuit_closed_requests,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times),
            "p99_response_time": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) >= 100 else max(self.response_times),
            "state_transitions_count": len(self.state_transitions),
            "state_transitions": self.state_transitions[-10:] if self.state_transitions else []  # Últimas 10 transições
        }

class CircuitBreakerLoadTester:
    """Testador de carga para circuit breakers"""
    
    def __init__(self, config: CircuitBreakerTestConfig):
        self.config = config
        self.metrics = CircuitBreakerMetrics()
        self.stop_event = threading.Event()
        self.session = requests.Session()
        self.session.timeout = self.config.timeout_per_request
        
        # Headers padrão
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "CircuitBreakerLoadTester/1.0"
        })
        
        logger.info(f"Circuit Breaker Load Tester inicializado: {config}")
    
    async def run_test(self) -> Dict[str, Any]:
        """Executa teste completo de circuit breaker"""
        logger.info("🚀 Iniciando teste de carga de circuit breaker")
        
        start_time = time.time()
        
        # Executar cenários
        results = await asyncio.gather(
            self._test_normal_operation(),
            self._test_failure_injection(),
            self._test_circuit_opening(),
            self._test_circuit_recovery(),
            self._test_stress_conditions()
        )
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Gerar relatório
        report = self._generate_report(results, test_duration)
        
        logger.info("✅ Teste de carga de circuit breaker concluído")
        return report
    
    async def _test_normal_operation(self) -> Dict[str, Any]:
        """Testa operação normal do circuit breaker"""
        logger.info("📊 Testando operação normal")
        
        endpoints = [
            "/api/v1/keywords",
            "/api/v1/analytics/advanced",
            "/api/v1/externo/google_trends"
        ]
        
        results = []
        for _ in range(50):  # 50 requests normais
            endpoint = random.choice(endpoints)
            try:
                start_time = time.time()
                response = self.session.get(f"{self.config.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                circuit_state = response.headers.get("X-Circuit-Breaker", "unknown")
                
                self.metrics.add_request(success, response_time, circuit_state)
                
                results.append({
                    "endpoint": endpoint,
                    "success": success,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "circuit_state": circuit_state
                })
                
                if self.config.enable_logging:
                    logger.debug(f"Request normal: {endpoint} - {response.status_code} - {response_time:.3f}s")
                
            except Exception as e:
                logger.warning(f"Erro em request normal: {e}")
                self.metrics.add_request(False, self.config.timeout_per_request, "unknown")
        
        return {
            "scenario": "normal_operation",
            "requests_count": len(results),
            "success_rate": sum(1 for r in results if r["success"]) / len(results) if results else 0,
            "avg_response_time": statistics.mean([r["response_time"] for r in results]) if results else 0
        }
    
    async def _test_failure_injection(self) -> Dict[str, Any]:
        """Testa injeção de falhas para abrir circuit breaker"""
        logger.info("💥 Testando injeção de falhas")
        
        # Endpoints que podem falhar
        failure_endpoints = [
            "/api/v1/externo/test_timeout",
            "/api/v1/externo/test_network_failure",
            "/api/v1/externo/test_error"
        ]
        
        results = []
        failure_count = 0
        
        for i in range(100):  # 100 requests com falhas
            endpoint = random.choice(failure_endpoints)
            
            # Simular falha baseada em configuração
            should_fail = random.random() < self.config.failure_rate_target
            
            try:
                start_time = time.time()
                
                if should_fail:
                    # Forçar falha
                    response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                else:
                    # Request normal
                    response = self.session.get(f"{self.config.base_url}{endpoint}")
                
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                circuit_state = response.headers.get("X-Circuit-Breaker", "unknown")
                
                if not success:
                    failure_count += 1
                
                self.metrics.add_request(success, response_time, circuit_state)
                
                results.append({
                    "endpoint": endpoint,
                    "success": success,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "circuit_state": circuit_state,
                    "forced_failure": should_fail
                })
                
            except requests.Timeout:
                failure_count += 1
                self.metrics.add_request(False, self.config.timeout_per_request, "unknown")
                results.append({
                    "endpoint": endpoint,
                    "success": False,
                    "status_code": 408,
                    "response_time": self.config.timeout_per_request,
                    "circuit_state": "unknown",
                    "forced_failure": should_fail,
                    "error": "timeout"
                })
                
            except Exception as e:
                failure_count += 1
                self.metrics.add_request(False, self.config.timeout_per_request, "unknown")
                results.append({
                    "endpoint": endpoint,
                    "success": False,
                    "status_code": 500,
                    "response_time": self.config.timeout_per_request,
                    "circuit_state": "unknown",
                    "forced_failure": should_fail,
                    "error": str(e)
                })
        
        return {
            "scenario": "failure_injection",
            "requests_count": len(results),
            "failure_count": failure_count,
            "failure_rate": failure_count / len(results) if results else 0,
            "forced_failures": sum(1 for r in results if r.get("forced_failure", False))
        }
    
    async def _test_circuit_opening(self) -> Dict[str, Any]:
        """Testa abertura do circuit breaker"""
        logger.info("🔴 Testando abertura do circuit breaker")
        
        # Endpoint que vai falhar consistentemente
        endpoint = "/api/v1/externo/test_timeout"
        
        results = []
        circuit_opened = False
        
        for i in range(20):  # 20 requests consecutivos para abrir circuit
            try:
                start_time = time.time()
                response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                circuit_state = response.headers.get("X-Circuit-Breaker", "unknown")
                
                # Verificar se circuit abriu
                if circuit_state == "open" and not circuit_opened:
                    circuit_opened = True
                    self.metrics.add_state_transition("closed", "open", "failure_threshold_reached")
                    logger.info(f"🔴 Circuit breaker aberto após {i+1} falhas")
                
                self.metrics.add_request(success, response_time, circuit_state)
                
                results.append({
                    "request_number": i + 1,
                    "success": success,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "circuit_state": circuit_state,
                    "circuit_opened": circuit_opened
                })
                
            except requests.Timeout:
                self.metrics.add_request(False, self.config.timeout_per_request, "unknown")
                results.append({
                    "request_number": i + 1,
                    "success": False,
                    "status_code": 408,
                    "response_time": self.config.timeout_per_request,
                    "circuit_state": "unknown",
                    "error": "timeout"
                })
        
        return {
            "scenario": "circuit_opening",
            "requests_count": len(results),
            "circuit_opened": circuit_opened,
            "requests_to_open": next((i for i, r in enumerate(results) if r.get("circuit_opened")), -1) + 1
        }
    
    async def _test_circuit_recovery(self) -> Dict[str, Any]:
        """Testa recuperação do circuit breaker"""
        logger.info("🟡 Testando recuperação do circuit breaker")
        
        # Primeiro, abrir o circuit
        await self._test_circuit_opening()
        
        # Aguardar tempo de recuperação
        logger.info(f"⏳ Aguardando {self.config.recovery_timeout} segundos para recuperação")
        await asyncio.sleep(self.config.recovery_timeout)
        
        # Testar recuperação
        endpoint = "/api/v1/keywords"  # Endpoint que deve funcionar
        results = []
        circuit_recovered = False
        
        for i in range(10):  # 10 requests para testar recuperação
            try:
                start_time = time.time()
                response = self.session.get(f"{self.config.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                circuit_state = response.headers.get("X-Circuit-Breaker", "unknown")
                
                # Verificar se circuit fechou
                if circuit_state == "closed" and not circuit_recovered:
                    circuit_recovered = True
                    self.metrics.add_state_transition("half_open", "closed", "success_threshold_reached")
                    logger.info(f"🟢 Circuit breaker recuperado após {i+1} sucessos")
                
                self.metrics.add_request(success, response_time, circuit_state)
                
                results.append({
                    "request_number": i + 1,
                    "success": success,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "circuit_state": circuit_state,
                    "circuit_recovered": circuit_recovered
                })
                
            except Exception as e:
                self.metrics.add_request(False, self.config.timeout_per_request, "unknown")
                results.append({
                    "request_number": i + 1,
                    "success": False,
                    "status_code": 500,
                    "response_time": self.config.timeout_per_request,
                    "circuit_state": "unknown",
                    "error": str(e)
                })
        
        return {
            "scenario": "circuit_recovery",
            "requests_count": len(results),
            "circuit_recovered": circuit_recovered,
            "requests_to_recover": next((i for i, r in enumerate(results) if r.get("circuit_recovered")), -1) + 1
        }
    
    async def _test_stress_conditions(self) -> Dict[str, Any]:
        """Testa condições de stress"""
        logger.info("🔥 Testando condições de stress")
        
        endpoints = [
            "/api/v1/keywords",
            "/api/v1/analytics/advanced",
            "/api/v1/externo/google_trends"
        ]
        
        # Executar requests concorrentes
        async def stress_request():
            endpoint = random.choice(endpoints)
            try:
                start_time = time.time()
                response = self.session.get(f"{self.config.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                circuit_state = response.headers.get("X-Circuit-Breaker", "unknown")
                
                self.metrics.add_request(success, response_time, circuit_state)
                
                return {
                    "endpoint": endpoint,
                    "success": success,
                    "response_time": response_time,
                    "circuit_state": circuit_state
                }
                
            except Exception as e:
                self.metrics.add_request(False, self.config.timeout_per_request, "unknown")
                return {
                    "endpoint": endpoint,
                    "success": False,
                    "error": str(e)
                }
        
        # Executar 200 requests concorrentes
        tasks = [stress_request() for _ in range(200)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos
        valid_results = [r for r in results if not isinstance(r, Exception)]
        
        return {
            "scenario": "stress_conditions",
            "requests_count": len(valid_results),
            "success_rate": sum(1 for r in valid_results if r["success"]) / len(valid_results) if valid_results else 0,
            "avg_response_time": statistics.mean([r["response_time"] for r in valid_results if "response_time" in r]) if valid_results else 0
        }
    
    def _generate_report(self, results: List[Dict[str, Any]], test_duration: float) -> Dict[str, Any]:
        """Gera relatório completo do teste"""
        metrics_summary = self.metrics.get_summary()
        
        report = {
            "test_info": {
                "name": "Circuit Breaker Load Test",
                "tracing_id": "resilience-circuit-breaker-test-2025-01-27-001",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": test_duration,
                "config": {
                    "base_url": self.config.base_url,
                    "concurrent_users": self.config.concurrent_users,
                    "failure_rate_target": self.config.failure_rate_target,
                    "recovery_timeout": self.config.recovery_timeout
                }
            },
            "scenarios": {
                result["scenario"]: result for result in results
            },
            "metrics": metrics_summary,
            "circuit_breaker_analysis": {
                "total_state_transitions": len(self.metrics.state_transitions),
                "state_transitions": self.metrics.state_transitions,
                "circuit_effectiveness": {
                    "requests_protected": self.metrics.circuit_open_requests,
                    "protection_rate": self.metrics.circuit_open_requests / self.metrics.total_requests if self.metrics.total_requests > 0 else 0
                }
            },
            "performance_analysis": {
                "throughput_rps": self.metrics.total_requests / test_duration if test_duration > 0 else 0,
                "avg_response_time": metrics_summary.get("avg_response_time", 0),
                "p95_response_time": metrics_summary.get("p95_response_time", 0),
                "p99_response_time": metrics_summary.get("p99_response_time", 0)
            },
            "recommendations": self._generate_recommendations(metrics_summary, results)
        }
        
        return report
    
    def _generate_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Análise de performance
        if metrics.get("avg_response_time", 0) > 2.0:
            recommendations.append("⚠️ Tempo de resposta médio alto (>2s). Considere otimizar endpoints.")
        
        if metrics.get("p95_response_time", 0) > 5.0:
            recommendations.append("⚠️ P95 de tempo de resposta alto (>5s). Verificar gargalos.")
        
        # Análise de circuit breaker
        if metrics.get("circuit_open_requests", 0) == 0:
            recommendations.append("ℹ️ Circuit breaker não foi ativado. Considere ajustar thresholds.")
        
        if len(metrics.get("state_transitions", [])) > 10:
            recommendations.append("⚠️ Muitas transições de estado. Verificar estabilidade do serviço.")
        
        # Análise de falhas
        failure_rate = metrics.get("failure_rate", 0)
        if failure_rate > 0.1:
            recommendations.append(f"⚠️ Taxa de falha alta ({failure_rate:.1%}). Investigar causas.")
        
        # Recomendações de configuração
        if not recommendations:
            recommendations.append("✅ Circuit breaker funcionando adequadamente.")
        
        return recommendations

async def main():
    """Função principal para executar teste"""
    config = CircuitBreakerTestConfig()
    tester = CircuitBreakerLoadTester(config)
    
    try:
        report = await tester.run_test()
        
        # Salvar relatório
        with open("circuit_breaker_load_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Exibir resumo
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTE DE CIRCUIT BREAKER")
        print("="*60)
        print(f"Total de Requests: {report['metrics']['total_requests']}")
        print(f"Taxa de Sucesso: {report['metrics']['success_rate']:.1%}")
        print(f"Tempo Médio de Resposta: {report['metrics']['avg_response_time']:.3f}s")
        print(f"Circuit Breaker Ativado: {report['metrics']['circuit_open_requests']} vezes")
        print(f"Transições de Estado: {report['metrics']['state_transitions_count']}")
        print("\nRecomendações:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Erro durante teste: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 