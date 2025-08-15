"""
🔄 Canary Endpoints System - Omni Keywords Finder

Sistema de endpoints canário para shadow testing e detecção de regressões.

Tracing ID: canary-endpoints-system-2025-01-27-001
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urlparse

import aiohttp
import pytest
from dataclasses_json import dataclass_json

from tests.utils.risk_calculator import calculate_risk_score
from tests.utils.semantic_validator import SemanticValidator
from tests.decorators.critical_decorators import (
    critical_risk, 
    semantic_validation, 
    real_data_validation,
    production_scenario,
    side_effects_monitoring,
    performance_monitoring
)

# Configuração de logging estruturado
logger = logging.getLogger(__name__)

@dataclass_json
@dataclass
class CanaryEndpoint:
    """Representa um endpoint canário"""
    path: str
    method: str
    production_url: str
    canary_url: str
    traffic_percentage: float = 0.1  # 10% do tráfego vai para canário
    health_check_path: Optional[str] = None
    rollback_threshold: float = 0.05  # 5% de erro para rollback
    enabled: bool = True
    created_at: float = field(default_factory=time.time)

@dataclass_json
@dataclass
class CanaryHealth:
    """Status de saúde do endpoint canário"""
    endpoint_path: str
    is_healthy: bool
    response_time: float
    error_rate: float
    success_count: int
    error_count: int
    last_check: float = field(default_factory=time.time)
    risk_score: int = 0

@dataclass_json
@dataclass
class CanaryTrafficSplit:
    """Configuração de divisão de tráfego"""
    endpoint_path: str
    production_weight: float
    canary_weight: float
    total_requests: int
    canary_requests: int
    production_requests: int
    last_updated: float = field(default_factory=time.time)

class CanaryEndpointsManager:
    """
    Gerenciador de endpoints canário
    
    Características:
    - Configuração de endpoints canário
    - Health checks automáticos
    - Divisão de tráfego inteligente
    - Rollback automático
    - Métricas de performance
    """
    
    def __init__(self, 
                 base_production_url: str,
                 base_canary_url: str,
                 health_check_interval: int = 30):
        """
        Inicializa o gerenciador de endpoints canário
        
        Args:
            base_production_url: URL base da produção
            base_canary_url: URL base do canário
            health_check_interval: Intervalo de health checks em segundos
        """
        self.base_production_url = base_production_url.rstrip('/')
        self.base_canary_url = base_canary_url.rstrip('/')
        self.health_check_interval = health_check_interval
        
        self.endpoints: Dict[str, CanaryEndpoint] = {}
        self.health_status: Dict[str, CanaryHealth] = {}
        self.traffic_splits: Dict[str, CanaryTrafficSplit] = {}
        
        self.semantic_validator = SemanticValidator()
        self.logger = logging.getLogger(f"{__name__}.CanaryManager")
        
        # Métricas de performance
        self.performance_metrics = {
            'total_endpoints': 0,
            'healthy_endpoints': 0,
            'unhealthy_endpoints': 0,
            'total_requests': 0,
            'canary_requests': 0,
            'production_requests': 0,
            'rollbacks_triggered': 0
        }
    
    def register_endpoint(self, endpoint: CanaryEndpoint) -> None:
        """
        Registra um novo endpoint canário
        
        Args:
            endpoint: Configuração do endpoint
        """
        endpoint_key = f"{endpoint.method}:{endpoint.path}"
        
        if endpoint_key in self.endpoints:
            self.logger.warning(f"Endpoint {endpoint_key} já registrado, atualizando...")
        
        self.endpoints[endpoint_key] = endpoint
        
        # Inicializa health status
        self.health_status[endpoint_key] = CanaryHealth(
            endpoint_path=endpoint.path,
            is_healthy=True,
            response_time=0.0,
            error_rate=0.0,
            success_count=0,
            error_count=0
        )
        
        # Inicializa traffic split
        self.traffic_splits[endpoint_key] = CanaryTrafficSplit(
            endpoint_path=endpoint.path,
            production_weight=1.0 - endpoint.traffic_percentage,
            canary_weight=endpoint.traffic_percentage,
            total_requests=0,
            canary_requests=0,
            production_requests=0
        )
        
        self.performance_metrics['total_endpoints'] += 1
        self.logger.info(f"Endpoint canário registrado: {endpoint_key}")
    
    async def route_request(self, 
                          method: str, 
                          path: str, 
                          headers: Dict[str, str], 
                          body: Optional[str] = None) -> Dict[str, Any]:
        """
        Roteia uma requisição para produção ou canário
        
        Args:
            method: Método HTTP
            path: Caminho da requisição
            headers: Headers da requisição
            body: Corpo da requisição
            
        Returns:
            Resposta da requisição
        """
        endpoint_key = f"{method}:{path}"
        
        if endpoint_key not in self.endpoints:
            # Se não é um endpoint canário, vai direto para produção
            return await self._make_production_request(method, path, headers, body)
        
        endpoint = self.endpoints[endpoint_key]
        if not endpoint.enabled:
            return await self._make_production_request(method, path, headers, body)
        
        # Verifica saúde do canário
        health = self.health_status[endpoint_key]
        if not health.is_healthy:
            self.logger.warning(f"Canário não saudável para {endpoint_key}, usando produção")
            return await self._make_production_request(method, path, headers, body)
        
        # Decide roteamento baseado em peso do tráfego
        traffic_split = self.traffic_splits[endpoint_key]
        import random
        rand_val = random.random()
        
        if rand_val < traffic_split.canary_weight:
            # Rota para canário
            traffic_split.canary_requests += 1
            self.performance_metrics['canary_requests'] += 1
            response = await self._make_canary_request(method, path, headers, body)
        else:
            # Rota para produção
            traffic_split.production_requests += 1
            self.performance_metrics['production_requests'] += 1
            response = await self._make_production_request(method, path, headers, body)
        
        traffic_split.total_requests += 1
        self.performance_metrics['total_requests'] += 1
        traffic_split.last_updated = time.time()
        
        return response
    
    async def _make_production_request(self, 
                                     method: str, 
                                     path: str, 
                                     headers: Dict[str, str], 
                                     body: Optional[str] = None) -> Dict[str, Any]:
        """Faz requisição para produção"""
        url = f"{self.base_production_url}{path}"
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=body,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_body = await response.text()
                    response_time = time.time() - start_time
                    
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": response_body,
                        "response_time": response_time,
                        "source": "production"
                    }
            except Exception as e:
                response_time = time.time() - start_time
                self.logger.error(f"Erro na requisição de produção: {e}")
                
                return {
                    "status_code": 500,
                    "headers": {},
                    "body": str(e),
                    "response_time": response_time,
                    "source": "production"
                }
    
    async def _make_canary_request(self, 
                                 method: str, 
                                 path: str, 
                                 headers: Dict[str, str], 
                                 body: Optional[str] = None) -> Dict[str, Any]:
        """Faz requisição para canário"""
        url = f"{self.base_canary_url}{path}"
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=body,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_body = await response.text()
                    response_time = time.time() - start_time
                    
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": response_body,
                        "response_time": response_time,
                        "source": "canary"
                    }
            except Exception as e:
                response_time = time.time() - start_time
                self.logger.error(f"Erro na requisição de canário: {e}")
                
                return {
                    "status_code": 500,
                    "headers": {},
                    "body": str(e),
                    "response_time": response_time,
                    "source": "canary"
                }
    
    async def perform_health_check(self, endpoint_key: str) -> CanaryHealth:
        """
        Executa health check em um endpoint canário
        
        Args:
            endpoint_key: Chave do endpoint
            
        Returns:
            Status de saúde atualizado
        """
        if endpoint_key not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint_key} não encontrado")
        
        endpoint = self.endpoints[endpoint_key]
        health = self.health_status[endpoint_key]
        
        # Faz health check
        health_check_path = endpoint.health_check_path or f"{endpoint.path}/health"
        
        try:
            response = await self._make_canary_request(
                "GET", health_check_path, {"Content-Type": "application/json"}
            )
            
            # Atualiza métricas de saúde
            is_healthy = response["status_code"] == 200
            response_time = response["response_time"]
            
            if is_healthy:
                health.success_count += 1
            else:
                health.error_count += 1
            
            total_requests = health.success_count + health.error_count
            error_rate = health.error_count / max(total_requests, 1)
            
            # Atualiza health status
            health.is_healthy = is_healthy and error_rate < endpoint.rollback_threshold
            health.response_time = response_time
            health.error_rate = error_rate
            health.last_check = time.time()
            
            # Calcula RISK_SCORE
            health.risk_score = calculate_risk_score(
                component="canary_health_check",
                operation=f"health_check_{endpoint.path}",
                data_sensitivity="low",
                external_dependencies=1,
                error_rate=error_rate
            )
            
            # Atualiza métricas globais
            if health.is_healthy:
                self.performance_metrics['healthy_endpoints'] = sum(
                    1 for h in self.health_status.values() if h.is_healthy
                )
                self.performance_metrics['unhealthy_endpoints'] = (
                    self.performance_metrics['total_endpoints'] - 
                    self.performance_metrics['healthy_endpoints']
                )
            
            # Log estruturado
            health_log = {
                "event": "canary_health_check",
                "endpoint": endpoint_key,
                "is_healthy": health.is_healthy,
                "error_rate": error_rate,
                "response_time": response_time,
                "risk_score": health.risk_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if health.is_healthy:
                self.logger.info(f"HEALTH_CHECK_LOG: {json.dumps(health_log)}")
            else:
                self.logger.error(f"HEALTH_CHECK_LOG: {json.dumps(health_log)}")
            
            return health
            
        except Exception as e:
            self.logger.error(f"Erro no health check de {endpoint_key}: {e}")
            
            # Marca como não saudável
            health.is_healthy = False
            health.error_count += 1
            health.last_check = time.time()
            health.risk_score = calculate_risk_score(
                component="canary_health_check",
                operation=f"health_check_{endpoint.path}",
                data_sensitivity="low",
                external_dependencies=1,
                error_rate=1.0
            )
            
            return health
    
    async def trigger_rollback(self, endpoint_key: str) -> bool:
        """
        Dispara rollback de um endpoint canário
        
        Args:
            endpoint_key: Chave do endpoint
            
        Returns:
            True se rollback foi executado com sucesso
        """
        if endpoint_key not in self.endpoints:
            return False
        
        endpoint = self.endpoints[endpoint_key]
        endpoint.enabled = False
        
        self.performance_metrics['rollbacks_triggered'] += 1
        
        # Log estruturado
        rollback_log = {
            "event": "canary_rollback",
            "endpoint": endpoint_key,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "health_check_failed",
            "risk_score": self.health_status[endpoint_key].risk_score
        }
        
        self.logger.error(f"ROLLBACK_LOG: {json.dumps(rollback_log)}")
        
        return True
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance dos endpoints canário"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_endpoints": self.performance_metrics['total_endpoints'],
            "healthy_endpoints": self.performance_metrics['healthy_endpoints'],
            "unhealthy_endpoints": self.performance_metrics['unhealthy_endpoints'],
            "total_requests": self.performance_metrics['total_requests'],
            "canary_requests": self.performance_metrics['canary_requests'],
            "production_requests": self.performance_metrics['production_requests'],
            "rollbacks_triggered": self.performance_metrics['rollbacks_triggered'],
            "canary_traffic_percentage": (
                self.performance_metrics['canary_requests'] / 
                max(self.performance_metrics['total_requests'], 1) * 100
            ),
            "endpoints_health": [
                {
                    "endpoint": key,
                    "is_healthy": health.is_healthy,
                    "error_rate": health.error_rate,
                    "response_time": health.response_time,
                    "risk_score": health.risk_score,
                    "last_check": datetime.fromtimestamp(health.last_check).isoformat()
                }
                for key, health in self.health_status.items()
            ],
            "traffic_splits": [
                {
                    "endpoint": key,
                    "canary_weight": split.canary_weight,
                    "production_weight": split.production_weight,
                    "total_requests": split.total_requests,
                    "canary_requests": split.canary_requests,
                    "production_requests": split.production_requests
                }
                for key, split in self.traffic_splits.items()
            ]
        }

# Decorators para testes de endpoints canário
@critical_risk
@semantic_validation
@real_data_validation
@production_scenario
@side_effects_monitoring
@performance_monitoring
class TestCanaryEndpoints:
    """Testes de integração para endpoints canário"""
    
    @pytest.fixture
    def canary_manager(self):
        """Fixture para o gerenciador de endpoints canário"""
        return CanaryEndpointsManager(
            base_production_url="https://api.omni-keywords-finder.com",
            base_canary_url="https://canary.omni-keywords-finder.com",
            health_check_interval=30
        )
    
    def test_canary_endpoint_registration(self, canary_manager):
        """
        Testa o registro de endpoints canário
        
        RISK_SCORE: 70 (Alto - Configuração de produção)
        """
        # Registra endpoint canário
        endpoint = CanaryEndpoint(
            path="/api/v1/keywords/instagram/search",
            method="GET",
            production_url="https://api.omni-keywords-finder.com/api/v1/keywords/instagram/search",
            canary_url="https://canary.omni-keywords-finder.com/api/v1/keywords/instagram/search",
            traffic_percentage=0.1,
            health_check_path="/api/v1/keywords/instagram/search/health",
            rollback_threshold=0.05
        )
        
        canary_manager.register_endpoint(endpoint)
        
        # Validações
        endpoint_key = f"{endpoint.method}:{endpoint.path}"
        assert endpoint_key in canary_manager.endpoints
        assert endpoint_key in canary_manager.health_status
        assert endpoint_key in canary_manager.traffic_splits
        
        # Valida configurações
        registered_endpoint = canary_manager.endpoints[endpoint_key]
        assert registered_endpoint.path == endpoint.path
        assert registered_endpoint.method == endpoint.method
        assert registered_endpoint.traffic_percentage == 0.1
        assert registered_endpoint.rollback_threshold == 0.05
        
        # Log estruturado
        logger.info(f"Canary endpoint registration test completed: {endpoint_key}")
        logger.info(f"Total endpoints: {canary_manager.performance_metrics['total_endpoints']}")
    
    @pytest.mark.asyncio
    async def test_canary_health_check(self, canary_manager):
        """
        Testa health check de endpoints canário
        
        RISK_SCORE: 80 (Alto - Validação de saúde)
        """
        # Registra endpoint para teste
        endpoint = CanaryEndpoint(
            path="/api/v1/keywords/facebook/analyze",
            method="POST",
            production_url="https://api.omni-keywords-finder.com/api/v1/keywords/facebook/analyze",
            canary_url="https://canary.omni-keywords-finder.com/api/v1/keywords/facebook/analyze",
            traffic_percentage=0.05,
            health_check_path="/api/v1/keywords/facebook/analyze/health"
        )
        
        canary_manager.register_endpoint(endpoint)
        endpoint_key = f"{endpoint.method}:{endpoint.path}"
        
        # Executa health check
        health = await canary_manager.perform_health_check(endpoint_key)
        
        # Validações
        assert health is not None
        assert health.endpoint_path == endpoint.path
        assert isinstance(health.is_healthy, bool)
        assert isinstance(health.response_time, float)
        assert isinstance(health.error_rate, float)
        assert health.risk_score >= 70  # Teste crítico
        
        # Log estruturado
        logger.info(f"Canary health check test completed: {endpoint_key}")
        logger.info(f"Health status: {health.is_healthy}")
        logger.info(f"Error rate: {health.error_rate}")
        logger.info(f"Risk score: {health.risk_score}")
    
    @pytest.mark.asyncio
    async def test_canary_request_routing(self, canary_manager):
        """
        Testa o roteamento de requisições para canário
        
        RISK_SCORE: 85 (Alto - Roteamento de produção)
        """
        # Registra endpoint para teste
        endpoint = CanaryEndpoint(
            path="/api/v1/keywords/youtube/search",
            method="GET",
            production_url="https://api.omni-keywords-finder.com/api/v1/keywords/youtube/search",
            canary_url="https://canary.omni-keywords-finder.com/api/v1/keywords/youtube/search",
            traffic_percentage=0.2
        )
        
        canary_manager.register_endpoint(endpoint)
        
        # Faz requisição
        response = await canary_manager.route_request(
            method="GET",
            path="/api/v1/keywords/youtube/search",
            headers={"Authorization": "Bearer test_token"},
            body=None
        )
        
        # Validações
        assert response is not None
        assert "status_code" in response
        assert "source" in response
        assert "response_time" in response
        assert response["source"] in ["production", "canary"]
        
        # Log estruturado
        logger.info(f"Canary request routing test completed")
        logger.info(f"Response source: {response['source']}")
        logger.info(f"Response time: {response['response_time']}")
        logger.info(f"Status code: {response['status_code']}")
    
    def test_canary_performance_metrics(self, canary_manager):
        """
        Testa as métricas de performance dos endpoints canário
        
        RISK_SCORE: 75 (Alto - Validação de métricas)
        """
        # Registra alguns endpoints para teste
        endpoints = [
            CanaryEndpoint(
                path="/api/v1/keywords/tiktok/search",
                method="GET",
                production_url="https://api.omni-keywords-finder.com/api/v1/keywords/tiktok/search",
                canary_url="https://canary.omni-keywords-finder.com/api/v1/keywords/tiktok/search",
                traffic_percentage=0.15
            ),
            CanaryEndpoint(
                path="/api/v1/keywords/pinterest/analyze",
                method="POST",
                production_url="https://api.omni-keywords-finder.com/api/v1/keywords/pinterest/analyze",
                canary_url="https://canary.omni-keywords-finder.com/api/v1/keywords/pinterest/analyze",
                traffic_percentage=0.1
            )
        ]
        
        for endpoint in endpoints:
            canary_manager.register_endpoint(endpoint)
        
        # Gera relatório de performance
        report = canary_manager.get_performance_report()
        
        # Validações
        assert "timestamp" in report
        assert "total_endpoints" in report
        assert "healthy_endpoints" in report
        assert "unhealthy_endpoints" in report
        assert "total_requests" in report
        assert "canary_requests" in report
        assert "production_requests" in report
        assert "rollbacks_triggered" in report
        assert "canary_traffic_percentage" in report
        assert "endpoints_health" in report
        assert "traffic_splits" in report
        
        # Valida tipos de dados
        assert isinstance(report["total_endpoints"], int)
        assert isinstance(report["canary_traffic_percentage"], float)
        assert isinstance(report["endpoints_health"], list)
        assert isinstance(report["traffic_splits"], list)
        
        # Log estruturado
        logger.info(f"Canary performance metrics test completed")
        logger.info(f"Total endpoints: {report['total_endpoints']}")
        logger.info(f"Canary traffic percentage: {report['canary_traffic_percentage']}%")
        logger.info(f"Healthy endpoints: {report['healthy_endpoints']}")

if __name__ == "__main__":
    # Execução direta para testes
    pytest.main([__file__, "-v", "--tb=short"]) 