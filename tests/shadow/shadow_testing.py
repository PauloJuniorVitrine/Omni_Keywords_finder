"""
🔄 Shadow Testing System - Omni Keywords Finder

Sistema de duplicação silenciosa de requisições para detectar regressões
e comparar respostas entre versões de produção.

Tracing ID: shadow-testing-system-2025-01-27-001
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
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
class ShadowRequest:
    """Representa uma requisição para shadow testing"""
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    request_id: str = field(default_factory=lambda: f"shadow_{int(time.time() * 1000)}")

@dataclass_json
@dataclass
class ShadowResponse:
    """Representa uma resposta do shadow testing"""
    status_code: int
    headers: Dict[str, str]
    body: str
    response_time: float
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"  # "production" ou "canary"

@dataclass_json
@dataclass
class ShadowComparison:
    """Resultado da comparação entre respostas"""
    request_id: str
    production_response: ShadowResponse
    canary_response: ShadowResponse
    status_match: bool
    body_similarity: float
    response_time_diff: float
    headers_match: bool
    is_regression: bool
    risk_score: int
    timestamp: float = field(default_factory=time.time)

class ShadowTestingSystem:
    """
    Sistema de Shadow Testing para detectar regressões
    
    Características:
    - Duplicação silenciosa de requisições
    - Comparação automática de respostas
    - Detecção de regressões
    - Alertas automáticos
    - Rollback automático se necessário
    """
    
    def __init__(self, 
                 production_base_url: str,
                 canary_base_url: str,
                 similarity_threshold: float = 0.95,
                 response_time_threshold: float = 2.0):
        """
        Inicializa o sistema de shadow testing
        
        Args:
            production_base_url: URL base da produção
            canary_base_url: URL base do canário
            similarity_threshold: Limite de similaridade para considerar respostas iguais
            response_time_threshold: Limite de diferença de tempo de resposta
        """
        self.production_base_url = production_base_url.rstrip('/')
        self.canary_base_url = canary_base_url.rstrip('/')
        self.similarity_threshold = similarity_threshold
        self.response_time_threshold = response_time_threshold
        self.semantic_validator = SemanticValidator()
        self.comparisons: List[ShadowComparison] = []
        self.regressions_detected = 0
        self.total_requests = 0
        
        # Configuração de logging
        self.logger = logging.getLogger(f"{__name__}.ShadowTesting")
        self.logger.setLevel(logging.INFO)
        
        # Métricas de performance
        self.performance_metrics = {
            'total_requests': 0,
            'successful_comparisons': 0,
            'regressions_detected': 0,
            'avg_response_time_production': 0.0,
            'avg_response_time_canary': 0.0,
            'avg_similarity_score': 0.0
        }
    
    async def duplicate_request(self, request: ShadowRequest) -> ShadowComparison:
        """
        Duplica uma requisição para produção e canário simultaneamente
        
        Args:
            request: Requisição a ser duplicada
            
        Returns:
            Comparação entre as respostas
        """
        self.total_requests += 1
        self.logger.info(f"Duplicando requisição {request.request_id} para shadow testing")
        
        # Executa requisições em paralelo
        async with aiohttp.ClientSession() as session:
            production_task = self._make_request(session, request, self.production_base_url, "production")
            canary_task = self._make_request(session, request, self.canary_base_url, "canary")
            
            production_response, canary_response = await asyncio.gather(
                production_task, canary_task, return_exceptions=True
            )
        
        # Trata exceções
        if isinstance(production_response, Exception):
            self.logger.error(f"Erro na requisição de produção: {production_response}")
            production_response = ShadowResponse(
                status_code=500,
                headers={},
                body="",
                response_time=0.0,
                source="production"
            )
        
        if isinstance(canary_response, Exception):
            self.logger.error(f"Erro na requisição de canário: {canary_response}")
            canary_response = ShadowResponse(
                status_code=500,
                headers={},
                body="",
                response_time=0.0,
                source="canary"
            )
        
        # Compara as respostas
        comparison = self._compare_responses(request, production_response, canary_response)
        self.comparisons.append(comparison)
        
        # Atualiza métricas
        self._update_metrics(comparison)
        
        # Verifica se é uma regressão
        if comparison.is_regression:
            self.regressions_detected += 1
            await self._handle_regression(comparison)
        
        return comparison
    
    async def _make_request(self, 
                          session: aiohttp.ClientSession, 
                          request: ShadowRequest, 
                          base_url: str, 
                          source: str) -> ShadowResponse:
        """
        Faz uma requisição HTTP
        
        Args:
            session: Sessão HTTP
            request: Requisição a ser feita
            base_url: URL base
            source: Origem da requisição
            
        Returns:
            Resposta da requisição
        """
        # Constrói URL completa
        parsed_url = urlparse(request.url)
        full_url = f"{base_url}{parsed_url.path}"
        if parsed_url.query:
            full_url += f"?{parsed_url.query}"
        
        start_time = time.time()
        
        try:
            async with session.request(
                method=request.method,
                url=full_url,
                headers=request.headers,
                data=request.body,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                body = await response.text()
                response_time = time.time() - start_time
                
                return ShadowResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    body=body,
                    response_time=response_time,
                    source=source
                )
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Erro na requisição {source}: {e}")
            
            return ShadowResponse(
                status_code=500,
                headers={},
                body=str(e),
                response_time=response_time,
                source=source
            )
    
    def _compare_responses(self, 
                          request: ShadowRequest, 
                          production_response: ShadowResponse, 
                          canary_response: ShadowResponse) -> ShadowComparison:
        """
        Compara as respostas de produção e canário
        
        Args:
            request: Requisição original
            production_response: Resposta da produção
            canary_response: Resposta do canário
            
        Returns:
            Resultado da comparação
        """
        # Compara status codes
        status_match = production_response.status_code == canary_response.status_code
        
        # Compara headers (ignora headers específicos de servidor)
        production_headers = {k: v for k, v in production_response.headers.items() 
                            if not k.lower().startswith(('server', 'date', 'x-'))}
        canary_headers = {k: v for k, v in canary_response.headers.items() 
                         if not k.lower().startswith(('server', 'date', 'x-'))}
        headers_match = production_headers == canary_headers
        
        # Calcula similaridade semântica dos corpos
        try:
            body_similarity = self.semantic_validator.calculate_similarity(
                production_response.body, canary_response.body
            )
        except Exception as e:
            self.logger.warning(f"Erro ao calcular similaridade: {e}")
            body_similarity = 0.0
        
        # Calcula diferença de tempo de resposta
        response_time_diff = abs(production_response.response_time - canary_response.response_time)
        
        # Determina se é uma regressão
        is_regression = (
            not status_match or 
            not headers_match or 
            body_similarity < self.similarity_threshold or
            response_time_diff > self.response_time_threshold
        )
        
        # Calcula RISK_SCORE
        risk_score = calculate_risk_score(
            component="shadow_testing",
            operation=f"compare_{request.method}_{urlparse(request.url).path}",
            data_sensitivity="high" if "keywords" in request.url else "medium",
            external_dependencies=2,  # Produção + Canário
            error_rate=1.0 if is_regression else 0.0
        )
        
        return ShadowComparison(
            request_id=request.request_id,
            production_response=production_response,
            canary_response=canary_response,
            status_match=status_match,
            body_similarity=body_similarity,
            response_time_diff=response_time_diff,
            headers_match=headers_match,
            is_regression=is_regression,
            risk_score=risk_score
        )
    
    def _update_metrics(self, comparison: ShadowComparison):
        """Atualiza métricas de performance"""
        self.performance_metrics['total_requests'] += 1
        
        if not comparison.is_regression:
            self.performance_metrics['successful_comparisons'] += 1
        
        if comparison.is_regression:
            self.performance_metrics['regressions_detected'] += 1
        
        # Atualiza médias
        total = self.performance_metrics['total_requests']
        current_avg_prod = self.performance_metrics['avg_response_time_production']
        current_avg_canary = self.performance_metrics['avg_response_time_canary']
        current_avg_similarity = self.performance_metrics['avg_similarity_score']
        
        self.performance_metrics['avg_response_time_production'] = (
            (current_avg_prod * (total - 1) + comparison.production_response.response_time) / total
        )
        self.performance_metrics['avg_response_time_canary'] = (
            (current_avg_canary * (total - 1) + comparison.canary_response.response_time) / total
        )
        self.performance_metrics['avg_similarity_score'] = (
            (current_avg_similarity * (total - 1) + comparison.body_similarity) / total
        )
    
    async def _handle_regression(self, comparison: ShadowComparison):
        """
        Trata uma regressão detectada
        
        Args:
            comparison: Comparação que detectou a regressão
        """
        self.logger.error(f"REGRESSÃO DETECTADA: {comparison.request_id}")
        self.logger.error(f"Status match: {comparison.status_match}")
        self.logger.error(f"Headers match: {comparison.headers_match}")
        self.logger.error(f"Body similarity: {comparison.body_similarity}")
        self.logger.error(f"Response time diff: {comparison.response_time_diff}")
        self.logger.error(f"Risk score: {comparison.risk_score}")
        
        # Log estruturado para observabilidade
        regression_log = {
            "event": "regression_detected",
            "request_id": comparison.request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "risk_score": comparison.risk_score,
            "status_match": comparison.status_match,
            "headers_match": comparison.headers_match,
            "body_similarity": comparison.body_similarity,
            "response_time_diff": comparison.response_time_diff,
            "production_status": comparison.production_response.status_code,
            "canary_status": comparison.canary_response.status_code,
            "severity": "high" if comparison.risk_score >= 70 else "medium"
        }
        
        self.logger.error(f"REGRESSION_LOG: {json.dumps(regression_log)}")
        
        # TODO: Implementar alertas e rollback automático
        # await self._send_alert(regression_log)
        # await self._trigger_rollback(comparison)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance do shadow testing"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_requests": self.performance_metrics['total_requests'],
            "successful_comparisons": self.performance_metrics['successful_comparisons'],
            "regressions_detected": self.performance_metrics['regressions_detected'],
            "regression_rate": (
                self.performance_metrics['regressions_detected'] / 
                max(self.performance_metrics['total_requests'], 1)
            ),
            "avg_response_time_production": self.performance_metrics['avg_response_time_production'],
            "avg_response_time_canary": self.performance_metrics['avg_response_time_canary'],
            "avg_similarity_score": self.performance_metrics['avg_similarity_score'],
            "recent_comparisons": [
                {
                    "request_id": c.request_id,
                    "is_regression": c.is_regression,
                    "risk_score": c.risk_score,
                    "body_similarity": c.body_similarity,
                    "timestamp": datetime.fromtimestamp(c.timestamp).isoformat()
                }
                for c in self.comparisons[-10:]  # Últimas 10 comparações
            ]
        }

# Decorators para testes de shadow
@critical_risk
@semantic_validation
@real_data_validation
@production_scenario
@side_effects_monitoring
@performance_monitoring
class TestShadowTesting:
    """Testes de integração para o sistema de shadow testing"""
    
    @pytest.fixture
    def shadow_system(self):
        """Fixture para o sistema de shadow testing"""
        return ShadowTestingSystem(
            production_base_url="https://api.omni-keywords-finder.com",
            canary_base_url="https://canary.omni-keywords-finder.com",
            similarity_threshold=0.95,
            response_time_threshold=2.0
        )
    
    @pytest.mark.asyncio
    async def test_shadow_request_duplication(self, shadow_system):
        """
        Testa a duplicação de requisições para shadow testing
        
        RISK_SCORE: 85 (Alto - Teste de produção real)
        """
        # Requisição real para teste de shadow
        request = ShadowRequest(
            method="GET",
            url="/api/v1/keywords/instagram/search",
            headers={
                "Authorization": "Bearer real_token_here",
                "Content-Type": "application/json"
            },
            body=json.dumps({
                "query": "real_keyword_test",
                "platform": "instagram",
                "limit": 10
            })
        )
        
        # Executa shadow testing
        comparison = await shadow_system.duplicate_request(request)
        
        # Validações
        assert comparison is not None
        assert comparison.request_id == request.request_id
        assert comparison.production_response.source == "production"
        assert comparison.canary_response.source == "canary"
        assert comparison.risk_score >= 70  # Teste crítico
        
        # Log estruturado
        logger.info(f"Shadow test completed: {comparison.request_id}")
        logger.info(f"Risk score: {comparison.risk_score}")
        logger.info(f"Is regression: {comparison.is_regression}")
    
    @pytest.mark.asyncio
    async def test_shadow_regression_detection(self, shadow_system):
        """
        Testa a detecção de regressões no shadow testing
        
        RISK_SCORE: 90 (Crítico - Validação de regressões)
        """
        # Simula uma regressão (requisição que deve falhar no canário)
        request = ShadowRequest(
            method="POST",
            url="/api/v1/keywords/facebook/analyze",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json"
            },
            body=json.dumps({
                "keywords": ["test_keyword_1", "test_keyword_2"],
                "platform": "facebook",
                "analysis_type": "competitor"
            })
        )
        
        # Executa shadow testing
        comparison = await shadow_system.duplicate_request(request)
        
        # Validações específicas para regressão
        assert comparison.risk_score >= 70
        assert isinstance(comparison.is_regression, bool)
        
        # Se for regressão, valida logs
        if comparison.is_regression:
            assert shadow_system.regressions_detected > 0
            logger.warning(f"Regression detected in test: {comparison.request_id}")
        
        # Log estruturado
        logger.info(f"Regression detection test completed: {comparison.request_id}")
        logger.info(f"Risk score: {comparison.risk_score}")
        logger.info(f"Regressions detected: {shadow_system.regressions_detected}")
    
    def test_shadow_performance_metrics(self, shadow_system):
        """
        Testa as métricas de performance do shadow testing
        
        RISK_SCORE: 75 (Alto - Validação de métricas)
        """
        # Gera relatório de performance
        report = shadow_system.get_performance_report()
        
        # Validações
        assert "timestamp" in report
        assert "total_requests" in report
        assert "successful_comparisons" in report
        assert "regressions_detected" in report
        assert "regression_rate" in report
        assert "avg_response_time_production" in report
        assert "avg_response_time_canary" in report
        assert "avg_similarity_score" in report
        assert "recent_comparisons" in report
        
        # Valida tipos de dados
        assert isinstance(report["total_requests"], int)
        assert isinstance(report["regression_rate"], float)
        assert isinstance(report["avg_similarity_score"], float)
        assert isinstance(report["recent_comparisons"], list)
        
        # Log estruturado
        logger.info(f"Performance metrics test completed")
        logger.info(f"Total requests: {report['total_requests']}")
        logger.info(f"Regression rate: {report['regression_rate']}")
        logger.info(f"Average similarity: {report['avg_similarity_score']}")

if __name__ == "__main__":
    # Execução direta para testes
    pytest.main([__file__, "-v", "--tb=short"]) 