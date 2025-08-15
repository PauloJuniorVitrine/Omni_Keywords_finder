"""
🔄 Shadow Comparison System - Omni Keywords Finder

Sistema de comparação de respostas para shadow testing e detecção de divergências.

Tracing ID: shadow-comparison-system-2025-01-27-001
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from difflib import SequenceMatcher

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
class ComparisonResult:
    """Resultado de uma comparação entre respostas"""
    request_id: str
    endpoint: str
    method: str
    production_response: Dict[str, Any]
    canary_response: Dict[str, Any]
    status_code_match: bool
    headers_match: bool
    body_similarity: float
    response_time_diff: float
    is_divergent: bool
    divergence_type: Optional[str] = None
    divergence_details: Dict[str, Any] = field(default_factory=dict)
    risk_score: int = 0
    timestamp: float = field(default_factory=time.time)

@dataclass_json
@dataclass
class DivergenceAlert:
    """Alerta de divergência detectada"""
    alert_id: str
    comparison_result: ComparisonResult
    severity: str  # "low", "medium", "high", "critical"
    message: str
    recommendations: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    acknowledged: bool = False
    resolved: bool = False

class ShadowComparisonSystem:
    """
    Sistema de comparação para shadow testing
    
    Características:
    - Comparação detalhada de respostas
    - Detecção de divergências
    - Alertas automáticos
    - Análise semântica
    - Métricas de performance
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.95,
                 response_time_threshold: float = 2.0,
                 max_divergence_rate: float = 0.05):
        """
        Inicializa o sistema de comparação
        
        Args:
            similarity_threshold: Limite de similaridade para considerar respostas iguais
            response_time_threshold: Limite de diferença de tempo de resposta
            max_divergence_rate: Taxa máxima de divergência aceitável
        """
        self.similarity_threshold = similarity_threshold
        self.response_time_threshold = response_time_threshold
        self.max_divergence_rate = max_divergence_rate
        
        self.semantic_validator = SemanticValidator()
        self.logger = logging.getLogger(f"{__name__}.ComparisonSystem")
        
        # Armazenamento de resultados
        self.comparison_results: List[ComparisonResult] = []
        self.divergence_alerts: List[DivergenceAlert] = []
        
        # Métricas de performance
        self.performance_metrics = {
            'total_comparisons': 0,
            'successful_comparisons': 0,
            'divergent_comparisons': 0,
            'avg_similarity_score': 0.0,
            'avg_response_time_diff': 0.0,
            'divergence_rate': 0.0
        }
    
    async def compare_responses(self, 
                              request_id: str,
                              endpoint: str,
                              method: str,
                              production_response: Dict[str, Any],
                              canary_response: Dict[str, Any]) -> ComparisonResult:
        """
        Compara respostas de produção e canário
        
        Args:
            request_id: ID da requisição
            endpoint: Endpoint testado
            method: Método HTTP
            production_response: Resposta da produção
            canary_response: Resposta do canário
            
        Returns:
            Resultado da comparação
        """
        self.logger.info(f"Comparando respostas para {request_id}")
        
        # Compara status codes
        status_code_match = (
            production_response.get("status_code") == canary_response.get("status_code")
        )
        
        # Compara headers (ignora headers específicos de servidor)
        headers_match = self._compare_headers(
            production_response.get("headers", {}),
            canary_response.get("headers", {})
        )
        
        # Calcula similaridade semântica dos corpos
        body_similarity = await self._calculate_body_similarity(
            production_response.get("body", ""),
            canary_response.get("body", "")
        )
        
        # Calcula diferença de tempo de resposta
        response_time_diff = abs(
            production_response.get("response_time", 0) - 
            canary_response.get("response_time", 0)
        )
        
        # Determina se há divergência
        is_divergent = (
            not status_code_match or 
            not headers_match or 
            body_similarity < self.similarity_threshold or
            response_time_diff > self.response_time_threshold
        )
        
        # Identifica tipo de divergência
        divergence_type = None
        divergence_details = {}
        
        if is_divergent:
            divergence_type, divergence_details = self._identify_divergence_type(
                status_code_match, headers_match, body_similarity, response_time_diff
            )
        
        # Calcula RISK_SCORE
        risk_score = calculate_risk_score(
            component="shadow_comparison",
            operation=f"compare_{method}_{endpoint}",
            data_sensitivity="high" if "keywords" in endpoint else "medium",
            external_dependencies=2,  # Produção + Canário
            error_rate=1.0 if is_divergent else 0.0
        )
        
        # Cria resultado da comparação
        comparison_result = ComparisonResult(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            production_response=production_response,
            canary_response=canary_response,
            status_code_match=status_code_match,
            headers_match=headers_match,
            body_similarity=body_similarity,
            response_time_diff=response_time_diff,
            is_divergent=is_divergent,
            divergence_type=divergence_type,
            divergence_details=divergence_details,
            risk_score=risk_score
        )
        
        # Armazena resultado
        self.comparison_results.append(comparison_result)
        
        # Atualiza métricas
        self._update_metrics(comparison_result)
        
        # Cria alerta se necessário
        if is_divergent:
            await self._create_divergence_alert(comparison_result)
        
        return comparison_result
    
    def _compare_headers(self, 
                        production_headers: Dict[str, str], 
                        canary_headers: Dict[str, str]) -> bool:
        """
        Compara headers ignorando headers específicos de servidor
        
        Args:
            production_headers: Headers da produção
            canary_headers: Headers do canário
            
        Returns:
            True se headers são compatíveis
        """
        # Headers a ignorar na comparação
        ignore_headers = {
            'server', 'date', 'x-powered-by', 'x-request-id', 
            'x-runtime', 'x-version', 'cf-ray', 'cf-cache-status'
        }
        
        # Filtra headers
        prod_filtered = {
            k.lower(): v for k, v in production_headers.items() 
            if k.lower() not in ignore_headers
        }
        canary_filtered = {
            k.lower(): v for k, v in canary_headers.items() 
            if k.lower() not in ignore_headers
        }
        
        return prod_filtered == canary_filtered
    
    async def _calculate_body_similarity(self, 
                                       production_body: str, 
                                       canary_body: str) -> float:
        """
        Calcula similaridade semântica entre corpos de resposta
        
        Args:
            production_body: Corpo da resposta de produção
            canary_body: Corpo da resposta do canário
            
        Returns:
            Score de similaridade (0.0 a 1.0)
        """
        try:
            # Tenta usar validação semântica
            similarity = self.semantic_validator.calculate_similarity(
                production_body, canary_body
            )
        except Exception as e:
            self.logger.warning(f"Erro na validação semântica: {e}")
            
            # Fallback para comparação de string
            try:
                # Tenta parsear como JSON
                prod_json = json.loads(production_body) if production_body else {}
                canary_json = json.loads(canary_body) if canary_body else {}
                
                # Compara estruturas JSON
                similarity = self._compare_json_structures(prod_json, canary_json)
            except json.JSONDecodeError:
                # Fallback para comparação de string simples
                similarity = SequenceMatcher(None, production_body, canary_body).ratio()
        
        return similarity
    
    def _compare_json_structures(self, 
                                prod_json: Any, 
                                canary_json: Any) -> float:
        """
        Compara estruturas JSON para calcular similaridade
        
        Args:
            prod_json: JSON da produção
            canary_json: JSON do canário
            
        Returns:
            Score de similaridade (0.0 a 1.0)
        """
        if type(prod_json) != type(canary_json):
            return 0.0
        
        if isinstance(prod_json, dict):
            prod_keys = set(prod_json.keys())
            canary_keys = set(canary_json.keys())
            
            # Calcula similaridade de chaves
            key_similarity = len(prod_keys & canary_keys) / max(len(prod_keys | canary_keys), 1)
            
            # Calcula similaridade de valores para chaves comuns
            common_keys = prod_keys & canary_keys
            if not common_keys:
                return key_similarity
            
            value_similarities = []
            for key in common_keys:
                value_sim = self._compare_json_structures(prod_json[key], canary_json[key])
                value_similarities.append(value_sim)
            
            avg_value_similarity = sum(value_similarities) / len(value_similarities)
            
            # Combina similaridade de chaves e valores
            return (key_similarity + avg_value_similarity) / 2
        
        elif isinstance(prod_json, list):
            if len(prod_json) != len(canary_json):
                return 0.0
            
            if not prod_json:
                return 1.0
            
            # Compara elementos da lista
            similarities = []
            for i in range(len(prod_json)):
                sim = self._compare_json_structures(prod_json[i], canary_json[i])
                similarities.append(sim)
            
            return sum(similarities) / len(similarities)
        
        else:
            # Valores primitivos
            return 1.0 if prod_json == canary_json else 0.0
    
    def _identify_divergence_type(self, 
                                 status_code_match: bool,
                                 headers_match: bool,
                                 body_similarity: float,
                                 response_time_diff: float) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Identifica o tipo de divergência
        
        Args:
            status_code_match: Se status codes são iguais
            headers_match: Se headers são compatíveis
            body_similarity: Similaridade dos corpos
            response_time_diff: Diferença de tempo de resposta
            
        Returns:
            Tipo de divergência e detalhes
        """
        divergence_type = None
        details = {}
        
        if not status_code_match:
            divergence_type = "status_code_mismatch"
            details = {
                "production_status": "unknown",
                "canary_status": "unknown",
                "severity": "high"
            }
        elif not headers_match:
            divergence_type = "headers_mismatch"
            details = {
                "severity": "medium"
            }
        elif body_similarity < self.similarity_threshold:
            divergence_type = "body_similarity_low"
            details = {
                "similarity_score": body_similarity,
                "threshold": self.similarity_threshold,
                "severity": "high" if body_similarity < 0.8 else "medium"
            }
        elif response_time_diff > self.response_time_threshold:
            divergence_type = "response_time_divergence"
            details = {
                "time_diff": response_time_diff,
                "threshold": self.response_time_threshold,
                "severity": "medium"
            }
        
        return divergence_type, details
    
    def _update_metrics(self, comparison_result: ComparisonResult):
        """Atualiza métricas de performance"""
        self.performance_metrics['total_comparisons'] += 1
        
        if not comparison_result.is_divergent:
            self.performance_metrics['successful_comparisons'] += 1
        
        if comparison_result.is_divergent:
            self.performance_metrics['divergent_comparisons'] += 1
        
        # Atualiza médias
        total = self.performance_metrics['total_comparisons']
        current_avg_similarity = self.performance_metrics['avg_similarity_score']
        current_avg_time_diff = self.performance_metrics['avg_response_time_diff']
        
        self.performance_metrics['avg_similarity_score'] = (
            (current_avg_similarity * (total - 1) + comparison_result.body_similarity) / total
        )
        self.performance_metrics['avg_response_time_diff'] = (
            (current_avg_time_diff * (total - 1) + comparison_result.response_time_diff) / total
        )
        
        # Calcula taxa de divergência
        self.performance_metrics['divergence_rate'] = (
            self.performance_metrics['divergent_comparisons'] / 
            max(self.performance_metrics['total_comparisons'], 1)
        )
    
    async def _create_divergence_alert(self, comparison_result: ComparisonResult):
        """
        Cria alerta de divergência
        
        Args:
            comparison_result: Resultado da comparação com divergência
        """
        # Determina severidade
        severity = "low"
        if comparison_result.divergence_type == "status_code_mismatch":
            severity = "critical"
        elif comparison_result.divergence_type == "body_similarity_low":
            severity = "high" if comparison_result.body_similarity < 0.8 else "medium"
        elif comparison_result.divergence_type == "headers_mismatch":
            severity = "medium"
        elif comparison_result.divergence_type == "response_time_divergence":
            severity = "low"
        
        # Cria mensagem
        message = f"Divergência detectada em {comparison_result.endpoint}: {comparison_result.divergence_type}"
        
        # Gera recomendações
        recommendations = self._generate_recommendations(comparison_result)
        
        # Cria alerta
        alert = DivergenceAlert(
            alert_id=f"alert_{comparison_result.request_id}_{int(time.time())}",
            comparison_result=comparison_result,
            severity=severity,
            message=message,
            recommendations=recommendations
        )
        
        self.divergence_alerts.append(alert)
        
        # Log estruturado
        alert_log = {
            "event": "divergence_alert_created",
            "alert_id": alert.alert_id,
            "request_id": comparison_result.request_id,
            "endpoint": comparison_result.endpoint,
            "divergence_type": comparison_result.divergence_type,
            "severity": severity,
            "risk_score": comparison_result.risk_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.error(f"DIVERGENCE_ALERT_LOG: {json.dumps(alert_log)}")
    
    def _generate_recommendations(self, comparison_result: ComparisonResult) -> List[str]:
        """
        Gera recomendações baseadas no tipo de divergência
        
        Args:
            comparison_result: Resultado da comparação
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        if comparison_result.divergence_type == "status_code_mismatch":
            recommendations.extend([
                "Verificar logs de erro no canário",
                "Comparar configurações entre produção e canário",
                "Verificar se há diferenças na versão do código"
            ])
        elif comparison_result.divergence_type == "body_similarity_low":
            recommendations.extend([
                "Analisar diferenças no processamento de dados",
                "Verificar se há mudanças na lógica de negócio",
                "Comparar dados de entrada entre produção e canário"
            ])
        elif comparison_result.divergence_type == "headers_mismatch":
            recommendations.extend([
                "Verificar configurações de headers no canário",
                "Comparar middlewares entre produção e canário"
            ])
        elif comparison_result.divergence_type == "response_time_divergence":
            recommendations.extend([
                "Analisar performance do canário",
                "Verificar recursos disponíveis no canário",
                "Comparar configurações de cache"
            ])
        
        return recommendations
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance do sistema de comparação"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_comparisons": self.performance_metrics['total_comparisons'],
            "successful_comparisons": self.performance_metrics['successful_comparisons'],
            "divergent_comparisons": self.performance_metrics['divergent_comparisons'],
            "divergence_rate": self.performance_metrics['divergence_rate'],
            "avg_similarity_score": self.performance_metrics['avg_similarity_score'],
            "avg_response_time_diff": self.performance_metrics['avg_response_time_diff'],
            "active_alerts": len([a for a in self.divergence_alerts if not a.resolved]),
            "recent_comparisons": [
                {
                    "request_id": c.request_id,
                    "endpoint": c.endpoint,
                    "is_divergent": c.is_divergent,
                    "divergence_type": c.divergence_type,
                    "body_similarity": c.body_similarity,
                    "risk_score": c.risk_score,
                    "timestamp": datetime.fromtimestamp(c.timestamp).isoformat()
                }
                for c in self.comparison_results[-10:]  # Últimas 10 comparações
            ],
            "recent_alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity,
                    "divergence_type": a.comparison_result.divergence_type,
                    "acknowledged": a.acknowledged,
                    "resolved": a.resolved,
                    "created_at": datetime.fromtimestamp(a.created_at).isoformat()
                }
                for a in self.divergence_alerts[-5:]  # Últimos 5 alertas
            ]
        }

# Decorators para testes de comparação
@critical_risk
@semantic_validation
@real_data_validation
@production_scenario
@side_effects_monitoring
@performance_monitoring
class TestShadowComparison:
    """Testes de integração para o sistema de comparação"""
    
    @pytest.fixture
    def comparison_system(self):
        """Fixture para o sistema de comparação"""
        return ShadowComparisonSystem(
            similarity_threshold=0.95,
            response_time_threshold=2.0,
            max_divergence_rate=0.05
        )
    
    @pytest.mark.asyncio
    async def test_response_comparison(self, comparison_system):
        """
        Testa comparação de respostas
        
        RISK_SCORE: 85 (Alto - Validação de produção)
        """
        # Respostas de teste
        production_response = {
            "status_code": 200,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"keywords": ["test1", "test2"], "count": 2}),
            "response_time": 1.5,
            "source": "production"
        }
        
        canary_response = {
            "status_code": 200,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"keywords": ["test1", "test2"], "count": 2}),
            "response_time": 1.6,
            "source": "canary"
        }
        
        # Executa comparação
        result = await comparison_system.compare_responses(
            request_id="test_request_001",
            endpoint="/api/v1/keywords/instagram/search",
            method="GET",
            production_response=production_response,
            canary_response=canary_response
        )
        
        # Validações
        assert result is not None
        assert result.request_id == "test_request_001"
        assert result.status_code_match is True
        assert result.headers_match is True
        assert result.body_similarity >= 0.95
        assert result.is_divergent is False
        assert result.risk_score >= 70  # Teste crítico
        
        # Log estruturado
        logger.info(f"Response comparison test completed: {result.request_id}")
        logger.info(f"Body similarity: {result.body_similarity}")
        logger.info(f"Is divergent: {result.is_divergent}")
        logger.info(f"Risk score: {result.risk_score}")
    
    @pytest.mark.asyncio
    async def test_divergence_detection(self, comparison_system):
        """
        Testa detecção de divergências
        
        RISK_SCORE: 90 (Crítico - Detecção de problemas)
        """
        # Respostas com divergência
        production_response = {
            "status_code": 200,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"keywords": ["test1", "test2"], "count": 2}),
            "response_time": 1.5,
            "source": "production"
        }
        
        canary_response = {
            "status_code": 500,  # Divergência de status
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
            "response_time": 1.6,
            "source": "canary"
        }
        
        # Executa comparação
        result = await comparison_system.compare_responses(
            request_id="test_request_002",
            endpoint="/api/v1/keywords/facebook/analyze",
            method="POST",
            production_response=production_response,
            canary_response=canary_response
        )
        
        # Validações
        assert result.is_divergent is True
        assert result.status_code_match is False
        assert result.divergence_type == "status_code_mismatch"
        assert result.risk_score >= 70
        
        # Verifica se alerta foi criado
        assert len(comparison_system.divergence_alerts) > 0
        alert = comparison_system.divergence_alerts[-1]
        assert alert.comparison_result.request_id == "test_request_002"
        assert alert.severity == "critical"
        
        # Log estruturado
        logger.warning(f"Divergence detection test completed: {result.request_id}")
        logger.warning(f"Divergence type: {result.divergence_type}")
        logger.warning(f"Alert severity: {alert.severity}")
        logger.warning(f"Risk score: {result.risk_score}")
    
    def test_comparison_performance_metrics(self, comparison_system):
        """
        Testa métricas de performance do sistema de comparação
        
        RISK_SCORE: 75 (Alto - Validação de métricas)
        """
        # Gera relatório de performance
        report = comparison_system.get_performance_report()
        
        # Validações
        assert "timestamp" in report
        assert "total_comparisons" in report
        assert "successful_comparisons" in report
        assert "divergent_comparisons" in report
        assert "divergence_rate" in report
        assert "avg_similarity_score" in report
        assert "avg_response_time_diff" in report
        assert "active_alerts" in report
        assert "recent_comparisons" in report
        assert "recent_alerts" in report
        
        # Valida tipos de dados
        assert isinstance(report["total_comparisons"], int)
        assert isinstance(report["divergence_rate"], float)
        assert isinstance(report["avg_similarity_score"], float)
        assert isinstance(report["recent_comparisons"], list)
        assert isinstance(report["recent_alerts"], list)
        
        # Log estruturado
        logger.info(f"Comparison performance metrics test completed")
        logger.info(f"Total comparisons: {report['total_comparisons']}")
        logger.info(f"Divergence rate: {report['divergence_rate']}")
        logger.info(f"Average similarity: {report['avg_similarity_score']}")

if __name__ == "__main__":
    # Execução direta para testes
    pytest.main([__file__, "-v", "--tb=short"]) 