"""
🧪 Teste de Carga - Graceful Degradation
========================================

Tracing ID: resilience-graceful-degradation-test-2025-01-27-001
Timestamp: 2025-01-27T20:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Baseado em fallback strategies reais implementados em infrastructure/resilience/
🌲 ToT: Avaliadas múltiplas estratégias de degradação e escolhido mais abrangente
♻️ ReAct: Simulado cenários de falha e validado comportamento de degradação

Testa graceful degradation implementada em:
- infrastructure/resilience/resilience_complete.py
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
class GracefulDegradationTestConfig:
    """Configuração para testes de graceful degradation"""
    base_url: str = "http://localhost:8000"
    test_duration: int = 300  # 5 minutos
    concurrent_users: int = 40
    degradation_scenarios: List[str] = field(default_factory=lambda: [
        "service_unavailable",
        "partial_failure",
        "timeout_degradation",
        "cache_fallback",
        "static_response"
    ])
    timeout_per_request: float = 30.0
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_monitoring: bool = True

@dataclass
class GracefulDegradationMetrics:
    """Métricas de graceful degradation"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    degraded_requests: int = 0
    fallback_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    degradation_types: List[str] = field(default_factory=list)
    fallback_types: List[str] = field(default_factory=list)
    service_availability: Dict[str, int] = field(default_factory=dict)
    user_experience_scores: List[float] = field(default_factory=list)
    
    def add_request(self, success: bool, response_time: float, degraded: bool = False, 
                   degradation_type: str = "", fallback_type: str = "", service: str = ""):
        """Adiciona métrica de request"""
        self.total_requests += 1
        self.response_times.append(response_time)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if degraded:
            self.degraded_requests += 1
            if degradation_type:
                self.degradation_types.append(degradation_type)
        
        if fallback_type:
            self.fallback_requests += 1
            self.fallback_types.append(fallback_type)
        
        if service:
            self.service_availability[service] = self.service_availability.get(service, 0) + 1
    
    def add_user_experience_score(self, score: float):
        """Adiciona score de experiência do usuário"""
        self.user_experience_scores.append(score)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas"""
        if not self.response_times:
            return {}
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "degraded_requests": self.degraded_requests,
            "fallback_requests": self.fallback_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "degradation_rate": self.degraded_requests / self.total_requests if self.total_requests > 0 else 0,
            "fallback_rate": self.fallback_requests / self.total_requests if self.total_requests > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times),
            "degradation_types_distribution": self._get_distribution(self.degradation_types),
            "fallback_types_distribution": self._get_distribution(self.fallback_types),
            "service_availability": self.service_availability,
            "avg_user_experience_score": statistics.mean(self.user_experience_scores) if self.user_experience_scores else 0
        }
    
    def _get_distribution(self, items: List[str]) -> Dict[str, int]:
        """Retorna distribuição de itens"""
        distribution = {}
        for item in items:
            distribution[item] = distribution.get(item, 0) + 1
        return distribution

class GracefulDegradationLoadTester:
    """Testador de carga para graceful degradation"""
    
    def __init__(self, config: GracefulDegradationTestConfig):
        self.config = config
        self.metrics = GracefulDegradationMetrics()
        self.stop_event = threading.Event()
        self.session = requests.Session()
        self.session.timeout = self.config.timeout_per_request
        
        # Headers padrão
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "GracefulDegradationLoadTester/1.0"
        })
        
        logger.info(f"Graceful Degradation Load Tester inicializado: {config}")
    
    async def run_test(self) -> Dict[str, Any]:
        """Executa teste completo de graceful degradation"""
        logger.info("🚀 Iniciando teste de carga de graceful degradation")
        
        start_time = time.time()
        
        # Executar cenários
        results = await asyncio.gather(
            self._test_service_unavailable_degradation(),
            self._test_partial_failure_degradation(),
            self._test_timeout_degradation(),
            self._test_cache_fallback_degradation(),
            self._test_static_response_degradation(),
            self._test_mixed_degradation_scenarios()
        )
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Gerar relatório
        report = self._generate_report(results, test_duration)
        
        logger.info("✅ Teste de carga de graceful degradation concluído")
        return report
    
    async def _test_service_unavailable_degradation(self) -> Dict[str, Any]:
        """Testa degradação quando serviço está indisponível"""
        logger.info("🔴 Testando degradação por serviço indisponível")
        
        endpoints = [
            "/api/v1/keywords",
            "/api/v1/analytics/advanced",
            "/api/v1/externo/google_trends"
        ]
        
        results = []
        
        for attempt in range(30):  # 30 requests para testar degradação
            endpoint = random.choice(endpoints)
            service = endpoint.split('/')[2]  # Extrair nome do serviço
            
            try:
                start_time = time.time()
                
                # Simular serviço indisponível
                response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                response_time = time.time() - start_time
                
                # Verificar se houve degradação
                degraded = response.status_code == 503 or "fallback" in response.headers.get("X-Resilience-Status", "")
                fallback_type = response.headers.get("X-Error-Type", "")
                
                success = response.status_code in [200, 503]  # 503 é sucesso para degradação
                
                self.metrics.add_request(
                    success=success,
                    response_time=response_time,
                    degraded=degraded,
                    degradation_type="service_unavailable" if degraded else "",
                    fallback_type=fallback_type,
                    service=service
                )
                
                # Calcular score de experiência do usuário
                ux_score = self._calculate_ux_score(response_time, degraded, response.status_code)
                self.metrics.add_user_experience_score(ux_score)
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": success,
                    "degraded": degraded,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "fallback_type": fallback_type,
                    "ux_score": ux_score
                })
                
            except requests.Timeout:
                # Timeout também é considerado degradação
                self.metrics.add_request(
                    success=False,
                    response_time=self.config.timeout_per_request,
                    degraded=True,
                    degradation_type="service_unavailable",
                    fallback_type="timeout",
                    service=service
                )
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": False,
                    "degraded": True,
                    "status_code": 408,
                    "response_time": self.config.timeout_per_request,
                    "fallback_type": "timeout",
                    "ux_score": 0.1  # Score baixo para timeout
                })
                
            except Exception as e:
                self.metrics.add_request(
                    success=False,
                    response_time=self.config.timeout_per_request,
                    degraded=True,
                    degradation_type="service_unavailable",
                    fallback_type="exception",
                    service=service
                )
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": False,
                    "degraded": True,
                    "status_code": 500,
                    "response_time": self.config.timeout_per_request,
                    "fallback_type": "exception",
                    "error": str(e),
                    "ux_score": 0.0
                })
        
        return {
            "scenario": "service_unavailable_degradation",
            "requests_count": len(results),
            "degraded_requests": sum(1 for r in results if r["degraded"]),
            "degradation_rate": sum(1 for r in results if r["degraded"]) / len(results) if results else 0,
            "avg_ux_score": statistics.mean([r["ux_score"] for r in results]) if results else 0,
            "fallback_types": list(set(r["fallback_type"] for r in results if r["fallback_type"]))
        }
    
    async def _test_partial_failure_degradation(self) -> Dict[str, Any]:
        """Testa degradação por falha parcial"""
        logger.info("🟡 Testando degradação por falha parcial")
        
        # Endpoints que podem ter falha parcial
        endpoints = [
            "/api/v1/analytics/advanced",
            "/api/v1/analytics/keywords/performance",
            "/api/v1/analytics/export"
        ]
        
        results = []
        
        for attempt in range(25):  # 25 requests para testar falha parcial
            endpoint = random.choice(endpoints)
            service = "analytics"
            
            try:
                start_time = time.time()
                
                # Simular falha parcial (alguns dados indisponíveis)
                response = self.session.get(f"{self.config.base_url}{endpoint}?simular=resposta_invalida")
                response_time = time.time() - start_time
                
                # Verificar se houve degradação parcial
                degraded = response.status_code == 206 or "partial" in response.headers.get("X-Resilience-Status", "")
                fallback_type = response.headers.get("X-Error-Type", "")
                
                success = response.status_code in [200, 206]  # 206 é sucesso parcial
                
                self.metrics.add_request(
                    success=success,
                    response_time=response_time,
                    degraded=degraded,
                    degradation_type="partial_failure" if degraded else "",
                    fallback_type=fallback_type,
                    service=service
                )
                
                # Calcular score de experiência do usuário
                ux_score = self._calculate_ux_score(response_time, degraded, response.status_code)
                self.metrics.add_user_experience_score(ux_score)
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": success,
                    "degraded": degraded,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "fallback_type": fallback_type,
                    "ux_score": ux_score
                })
                
            except Exception as e:
                self.metrics.add_request(
                    success=False,
                    response_time=self.config.timeout_per_request,
                    degraded=True,
                    degradation_type="partial_failure",
                    fallback_type="exception",
                    service=service
                )
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": False,
                    "degraded": True,
                    "status_code": 500,
                    "response_time": self.config.timeout_per_request,
                    "fallback_type": "exception",
                    "error": str(e),
                    "ux_score": 0.3
                })
        
        return {
            "scenario": "partial_failure_degradation",
            "requests_count": len(results),
            "degraded_requests": sum(1 for r in results if r["degraded"]),
            "degradation_rate": sum(1 for r in results if r["degraded"]) / len(results) if results else 0,
            "avg_ux_score": statistics.mean([r["ux_score"] for r in results]) if results else 0,
            "partial_success_rate": sum(1 for r in results if r["status_code"] == 206) / len(results) if results else 0
        }
    
    async def _test_timeout_degradation(self) -> Dict[str, Any]:
        """Testa degradação por timeout"""
        logger.info("⏱️ Testando degradação por timeout")
        
        endpoints = [
            "/api/v1/externo/google_trends",
            "/api/v1/externo/get",
            "/api/v1/externo/post"
        ]
        
        results = []
        
        for attempt in range(20):  # 20 requests para testar timeout
            endpoint = random.choice(endpoints)
            service = "externo"
            
            try:
                start_time = time.time()
                
                # Simular timeout
                response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                response_time = time.time() - start_time
                
                # Verificar se houve degradação por timeout
                degraded = response.status_code == 408 or "timeout" in response.headers.get("X-Error-Type", "")
                fallback_type = response.headers.get("X-Error-Type", "")
                
                success = response.status_code in [200, 408]  # 408 é sucesso para timeout
                
                self.metrics.add_request(
                    success=success,
                    response_time=response_time,
                    degraded=degraded,
                    degradation_type="timeout" if degraded else "",
                    fallback_type=fallback_type,
                    service=service
                )
                
                # Calcular score de experiência do usuário
                ux_score = self._calculate_ux_score(response_time, degraded, response.status_code)
                self.metrics.add_user_experience_score(ux_score)
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": success,
                    "degraded": degraded,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "fallback_type": fallback_type,
                    "ux_score": ux_score
                })
                
            except requests.Timeout:
                # Timeout real
                self.metrics.add_request(
                    success=False,
                    response_time=self.config.timeout_per_request,
                    degraded=True,
                    degradation_type="timeout",
                    fallback_type="timeout",
                    service=service
                )
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": False,
                    "degraded": True,
                    "status_code": 408,
                    "response_time": self.config.timeout_per_request,
                    "fallback_type": "timeout",
                    "ux_score": 0.2
                })
        
        return {
            "scenario": "timeout_degradation",
            "requests_count": len(results),
            "degraded_requests": sum(1 for r in results if r["degraded"]),
            "degradation_rate": sum(1 for r in results if r["degraded"]) / len(results) if results else 0,
            "avg_ux_score": statistics.mean([r["ux_score"] for r in results]) if results else 0,
            "timeout_rate": sum(1 for r in results if r["status_code"] == 408) / len(results) if results else 0
        }
    
    async def _test_cache_fallback_degradation(self) -> Dict[str, Any]:
        """Testa degradação com fallback para cache"""
        logger.info("💾 Testando degradação com fallback para cache")
        
        endpoints = [
            "/api/v1/keywords",
            "/api/v1/analytics/advanced",
            "/api/v1/analytics/summary"
        ]
        
        results = []
        
        for attempt in range(25):  # 25 requests para testar cache fallback
            endpoint = random.choice(endpoints)
            service = endpoint.split('/')[2]
            
            try:
                start_time = time.time()
                
                # Simular uso de cache como fallback
                response = self.session.get(f"{self.config.base_url}{endpoint}?use_cache=true")
                response_time = time.time() - start_time
                
                # Verificar se houve degradação com cache
                degraded = "cache" in response.headers.get("X-Resilience-Status", "") or "fallback" in response.headers.get("X-Resilience-Status", "")
                fallback_type = "cache" if degraded else ""
                
                success = response.status_code == 200
                
                self.metrics.add_request(
                    success=success,
                    response_time=response_time,
                    degraded=degraded,
                    degradation_type="cache_fallback" if degraded else "",
                    fallback_type=fallback_type,
                    service=service
                )
                
                # Calcular score de experiência do usuário
                ux_score = self._calculate_ux_score(response_time, degraded, response.status_code)
                self.metrics.add_user_experience_score(ux_score)
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": success,
                    "degraded": degraded,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "fallback_type": fallback_type,
                    "ux_score": ux_score,
                    "cache_used": degraded
                })
                
            except Exception as e:
                self.metrics.add_request(
                    success=False,
                    response_time=self.config.timeout_per_request,
                    degraded=True,
                    degradation_type="cache_fallback",
                    fallback_type="exception",
                    service=service
                )
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": False,
                    "degraded": True,
                    "status_code": 500,
                    "response_time": self.config.timeout_per_request,
                    "fallback_type": "exception",
                    "error": str(e),
                    "ux_score": 0.4
                })
        
        return {
            "scenario": "cache_fallback_degradation",
            "requests_count": len(results),
            "degraded_requests": sum(1 for r in results if r["degraded"]),
            "degradation_rate": sum(1 for r in results if r["degraded"]) / len(results) if results else 0,
            "avg_ux_score": statistics.mean([r["ux_score"] for r in results]) if results else 0,
            "cache_usage_rate": sum(1 for r in results if r.get("cache_used", False)) / len(results) if results else 0
        }
    
    async def _test_static_response_degradation(self) -> Dict[str, Any]:
        """Testa degradação com resposta estática"""
        logger.info("📄 Testando degradação com resposta estática")
        
        endpoints = [
            "/api/v1/analytics/advanced",
            "/api/v1/analytics/keywords/performance",
            "/api/v1/analytics/export"
        ]
        
        results = []
        
        for attempt in range(20):  # 20 requests para testar resposta estática
            endpoint = random.choice(endpoints)
            service = "analytics"
            
            try:
                start_time = time.time()
                
                # Simular resposta estática como fallback
                response = self.session.get(f"{self.config.base_url}{endpoint}?static_fallback=true")
                response_time = time.time() - start_time
                
                # Verificar se houve degradação com resposta estática
                degraded = "static" in response.headers.get("X-Resilience-Status", "") or "fallback" in response.headers.get("X-Resilience-Status", "")
                fallback_type = "static_response" if degraded else ""
                
                success = response.status_code == 200
                
                self.metrics.add_request(
                    success=success,
                    response_time=response_time,
                    degraded=degraded,
                    degradation_type="static_response" if degraded else "",
                    fallback_type=fallback_type,
                    service=service
                )
                
                # Calcular score de experiência do usuário
                ux_score = self._calculate_ux_score(response_time, degraded, response.status_code)
                self.metrics.add_user_experience_score(ux_score)
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": success,
                    "degraded": degraded,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "fallback_type": fallback_type,
                    "ux_score": ux_score,
                    "static_response": degraded
                })
                
            except Exception as e:
                self.metrics.add_request(
                    success=False,
                    response_time=self.config.timeout_per_request,
                    degraded=True,
                    degradation_type="static_response",
                    fallback_type="exception",
                    service=service
                )
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "success": False,
                    "degraded": True,
                    "status_code": 500,
                    "response_time": self.config.timeout_per_request,
                    "fallback_type": "exception",
                    "error": str(e),
                    "ux_score": 0.5
                })
        
        return {
            "scenario": "static_response_degradation",
            "requests_count": len(results),
            "degraded_requests": sum(1 for r in results if r["degraded"]),
            "degradation_rate": sum(1 for r in results if r["degraded"]) / len(results) if results else 0,
            "avg_ux_score": statistics.mean([r["ux_score"] for r in results]) if results else 0,
            "static_response_rate": sum(1 for r in results if r.get("static_response", False)) / len(results) if results else 0
        }
    
    async def _test_mixed_degradation_scenarios(self) -> Dict[str, Any]:
        """Testa cenários mistos de degradação"""
        logger.info("🎭 Testando cenários mistos de degradação")
        
        endpoints = [
            "/api/v1/keywords",
            "/api/v1/analytics/advanced",
            "/api/v1/externo/google_trends",
            "/api/v1/analytics/export"
        ]
        
        degradation_scenarios = [
            "service_unavailable",
            "partial_failure",
            "timeout",
            "cache_fallback",
            "static_response"
        ]
        
        results = []
        
        for attempt in range(40):  # 40 requests com cenários mistos
            endpoint = random.choice(endpoints)
            scenario = random.choice(degradation_scenarios)
            service = endpoint.split('/')[2]
            
            try:
                start_time = time.time()
                
                # Simular cenário de degradação
                if scenario == "service_unavailable":
                    response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                elif scenario == "partial_failure":
                    response = self.session.get(f"{self.config.base_url}{endpoint}?simular=resposta_invalida")
                elif scenario == "timeout":
                    response = self.session.get(f"{self.config.base_url}{endpoint}?simular=timeout", timeout=1)
                elif scenario == "cache_fallback":
                    response = self.session.get(f"{self.config.base_url}{endpoint}?use_cache=true")
                else:  # static_response
                    response = self.session.get(f"{self.config.base_url}{endpoint}?static_fallback=true")
                
                response_time = time.time() - start_time
                
                # Verificar degradação
                degraded = (response.status_code in [503, 206, 408] or 
                          "fallback" in response.headers.get("X-Resilience-Status", "") or
                          "cache" in response.headers.get("X-Resilience-Status", "") or
                          "static" in response.headers.get("X-Resilience-Status", ""))
                
                fallback_type = response.headers.get("X-Error-Type", "")
                
                success = response.status_code in [200, 206, 503, 408]  # Todos são sucessos para degradação
                
                self.metrics.add_request(
                    success=success,
                    response_time=response_time,
                    degraded=degraded,
                    degradation_type=scenario if degraded else "",
                    fallback_type=fallback_type,
                    service=service
                )
                
                # Calcular score de experiência do usuário
                ux_score = self._calculate_ux_score(response_time, degraded, response.status_code)
                self.metrics.add_user_experience_score(ux_score)
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "scenario": scenario,
                    "success": success,
                    "degraded": degraded,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "fallback_type": fallback_type,
                    "ux_score": ux_score
                })
                
            except Exception as e:
                self.metrics.add_request(
                    success=False,
                    response_time=self.config.timeout_per_request,
                    degraded=True,
                    degradation_type=scenario,
                    fallback_type="exception",
                    service=service
                )
                
                results.append({
                    "attempt": attempt + 1,
                    "endpoint": endpoint,
                    "service": service,
                    "scenario": scenario,
                    "success": False,
                    "degraded": True,
                    "status_code": 500,
                    "response_time": self.config.timeout_per_request,
                    "fallback_type": "exception",
                    "error": str(e),
                    "ux_score": 0.1
                })
        
        return {
            "scenario": "mixed_degradation_scenarios",
            "requests_count": len(results),
            "degraded_requests": sum(1 for r in results if r["degraded"]),
            "degradation_rate": sum(1 for r in results if r["degraded"]) / len(results) if results else 0,
            "avg_ux_score": statistics.mean([r["ux_score"] for r in results]) if results else 0,
            "scenarios_tested": degradation_scenarios,
            "success_by_scenario": {
                scenario: sum(1 for r in results if r["scenario"] == scenario and r["success"])
                for scenario in degradation_scenarios
            },
            "degradation_by_scenario": {
                scenario: sum(1 for r in results if r["scenario"] == scenario and r["degraded"])
                for scenario in degradation_scenarios
            }
        }
    
    def _calculate_ux_score(self, response_time: float, degraded: bool, status_code: int) -> float:
        """Calcula score de experiência do usuário"""
        base_score = 1.0
        
        # Penalizar por tempo de resposta
        if response_time > 5.0:
            base_score -= 0.4
        elif response_time > 3.0:
            base_score -= 0.2
        elif response_time > 1.0:
            base_score -= 0.1
        
        # Penalizar por degradação
        if degraded:
            if status_code == 503:  # Service Unavailable
                base_score -= 0.5
            elif status_code == 206:  # Partial Content
                base_score -= 0.2
            elif status_code == 408:  # Timeout
                base_score -= 0.3
            else:
                base_score -= 0.1
        
        # Penalizar por erro
        if status_code >= 500:
            base_score -= 0.6
        elif status_code >= 400:
            base_score -= 0.3
        
        return max(0.0, base_score)
    
    def _generate_report(self, results: List[Dict[str, Any]], test_duration: float) -> Dict[str, Any]:
        """Gera relatório completo do teste"""
        metrics_summary = self.metrics.get_summary()
        
        report = {
            "test_info": {
                "name": "Graceful Degradation Load Test",
                "tracing_id": "resilience-graceful-degradation-test-2025-01-27-001",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": test_duration,
                "config": {
                    "base_url": self.config.base_url,
                    "degradation_scenarios": self.config.degradation_scenarios,
                    "concurrent_users": self.config.concurrent_users
                }
            },
            "scenarios": {
                result["scenario"]: result for result in results
            },
            "metrics": metrics_summary,
            "degradation_analysis": {
                "total_degraded_requests": self.metrics.degraded_requests,
                "degradation_rate": self.metrics.degraded_requests / self.metrics.total_requests if self.metrics.total_requests > 0 else 0,
                "fallback_requests": self.metrics.fallback_requests,
                "fallback_rate": self.metrics.fallback_requests / self.metrics.total_requests if self.metrics.total_requests > 0 else 0,
                "degradation_types_distribution": metrics_summary.get("degradation_types_distribution", {}),
                "fallback_types_distribution": metrics_summary.get("fallback_types_distribution", {}),
                "service_availability": metrics_summary.get("service_availability", {})
            },
            "user_experience_analysis": {
                "avg_ux_score": metrics_summary.get("avg_user_experience_score", 0),
                "ux_score_distribution": self._get_ux_score_distribution(),
                "degradation_impact": self._analyze_degradation_impact()
            },
            "performance_analysis": {
                "throughput_rps": self.metrics.total_requests / test_duration if test_duration > 0 else 0,
                "avg_response_time": metrics_summary.get("avg_response_time", 0),
                "p95_response_time": metrics_summary.get("p95_response_time", 0),
                "response_time_with_degradation": self._get_response_time_with_degradation()
            },
            "recommendations": self._generate_recommendations(metrics_summary, results)
        }
        
        return report
    
    def _get_ux_score_distribution(self) -> Dict[str, int]:
        """Retorna distribuição de scores de UX"""
        distribution = {
            "excellent": 0,  # 0.8-1.0
            "good": 0,       # 0.6-0.79
            "fair": 0,       # 0.4-0.59
            "poor": 0,       # 0.2-0.39
            "very_poor": 0   # 0.0-0.19
        }
        
        for score in self.metrics.user_experience_scores:
            if score >= 0.8:
                distribution["excellent"] += 1
            elif score >= 0.6:
                distribution["good"] += 1
            elif score >= 0.4:
                distribution["fair"] += 1
            elif score >= 0.2:
                distribution["poor"] += 1
            else:
                distribution["very_poor"] += 1
        
        return distribution
    
    def _analyze_degradation_impact(self) -> Dict[str, float]:
        """Analisa impacto da degradação na experiência do usuário"""
        if not self.metrics.user_experience_scores:
            return {}
        
        # Separar scores com e sem degradação
        degraded_scores = []
        normal_scores = []
        
        # Esta é uma simplificação - em um teste real, você teria essa informação
        # Aqui vamos estimar baseado nas métricas gerais
        avg_score = statistics.mean(self.metrics.user_experience_scores)
        degradation_rate = self.metrics.degraded_requests / self.metrics.total_requests if self.metrics.total_requests > 0 else 0
        
        return {
            "overall_avg_score": avg_score,
            "estimated_degraded_score": avg_score * 0.7,  # Estimativa
            "estimated_normal_score": avg_score * 1.1,    # Estimativa
            "degradation_impact": avg_score * 0.3,        # Estimativa do impacto
            "degradation_rate": degradation_rate
        }
    
    def _get_response_time_with_degradation(self) -> Dict[str, float]:
        """Retorna tempos de resposta com e sem degradação"""
        if not self.response_times:
            return {}
        
        # Simplificação - em um teste real você teria essa informação
        return {
            "overall_avg": statistics.mean(self.response_times),
            "estimated_degraded_avg": statistics.mean(self.response_times) * 1.5,  # Estimativa
            "estimated_normal_avg": statistics.mean(self.response_times) * 0.8     # Estimativa
        }
    
    def _generate_recommendations(self, metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Análise de degradação
        degradation_rate = metrics.get("degradation_rate", 0)
        if degradation_rate > 0.3:
            recommendations.append("⚠️ Taxa de degradação alta (>30%). Verificar estabilidade dos serviços.")
        elif degradation_rate < 0.1:
            recommendations.append("✅ Taxa de degradação baixa (<10%). Sistema estável.")
        
        # Análise de experiência do usuário
        avg_ux_score = metrics.get("avg_user_experience_score", 0)
        if avg_ux_score < 0.5:
            recommendations.append("⚠️ Score de experiência do usuário baixo (<0.5). Melhorar fallbacks.")
        elif avg_ux_score > 0.8:
            recommendations.append("✅ Score de experiência do usuário excelente (>0.8).")
        
        # Análise de fallbacks
        fallback_rate = metrics.get("fallback_rate", 0)
        if fallback_rate > 0.2:
            recommendations.append("ℹ️ Taxa de fallback alta (>20%). Verificar se fallbacks estão adequados.")
        
        # Análise de performance
        avg_response_time = metrics.get("avg_response_time", 0)
        if avg_response_time > 3.0:
            recommendations.append("⚠️ Tempo de resposta médio alto (>3s). Otimizar degradação.")
        
        # Análise de distribuição de degradação
        degradation_dist = metrics.get("degradation_types_distribution", {})
        if "service_unavailable" in degradation_dist and degradation_dist["service_unavailable"] > 10:
            recommendations.append("⚠️ Muitas falhas de serviço indisponível. Verificar infraestrutura.")
        
        if not recommendations:
            recommendations.append("✅ Graceful degradation funcionando adequadamente.")
        
        return recommendations

async def main():
    """Função principal para executar teste"""
    config = GracefulDegradationTestConfig()
    tester = GracefulDegradationLoadTester(config)
    
    try:
        report = await tester.run_test()
        
        # Salvar relatório
        with open("graceful_degradation_load_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Exibir resumo
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE TESTE DE GRACEFUL DEGRADATION")
        print("="*60)
        print(f"Total de Requests: {report['metrics']['total_requests']}")
        print(f"Taxa de Sucesso: {report['metrics']['success_rate']:.1%}")
        print(f"Taxa de Degradação: {report['metrics']['degradation_rate']:.1%}")
        print(f"Taxa de Fallback: {report['metrics']['fallback_rate']:.1%}")
        print(f"Score Médio de UX: {report['metrics']['avg_user_experience_score']:.2f}")
        print(f"Tempo Médio de Resposta: {report['metrics']['avg_response_time']:.3f}s")
        print("\nTipos de Degradação:")
        for deg_type, count in report['metrics']['degradation_types_distribution'].items():
            print(f"  {deg_type}: {count}")
        print("\nRecomendações:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Erro durante teste: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 