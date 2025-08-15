"""
📊 Risk Analyzer System - Omni Keywords Finder

Sistema de análise de risco por fluxo com métricas detalhadas.

Tracing ID: risk-analyzer-system-2025-01-27-001
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict, Counter
import statistics

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
class FlowRisk:
    """Risco de um fluxo específico"""
    flow_name: str
    flow_type: str  # "api", "batch", "real-time", "scheduled"
    total_tests: int
    avg_risk_score: float
    max_risk_score: int
    min_risk_score: int
    high_risk_tests: int  # RISK_SCORE >= 70
    medium_risk_tests: int  # RISK_SCORE 40-69
    low_risk_tests: int  # RISK_SCORE < 40
    risk_distribution: Dict[str, int] = field(default_factory=dict)
    critical_components: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

@dataclass_json
@dataclass
class ComponentRisk:
    """Risco de um componente específico"""
    component_name: str
    component_type: str  # "function", "class", "module", "service"
    risk_score: int
    complexity: int
    dependencies_count: int
    error_rate: float
    last_error: Optional[float] = None
    test_coverage: float = 0.0
    mutation_score: float = 0.0
    semantic_validation_score: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass_json
@dataclass
class RiskTrend:
    """Tendência de risco ao longo do tempo"""
    flow_name: str
    date: str
    avg_risk_score: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_tests: int
    risk_change: float  # Mudança percentual
    timestamp: float = field(default_factory=time.time)

@dataclass_json
@dataclass
class RiskAlert:
    """Alerta de risco"""
    alert_id: str
    flow_name: str
    alert_type: str  # "high_risk", "risk_increase", "threshold_exceeded"
    severity: str  # "low", "medium", "high", "critical"
    message: str
    current_risk_score: float
    threshold: float
    recommendations: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    acknowledged: bool = False
    resolved: bool = False

class RiskAnalyzer:
    """
    Analisador de risco por fluxo
    
    Características:
    - Análise de risco por fluxo (≤ 60 de risco médio)
    - Identificação de componentes críticos
    - Tendências de risco ao longo do tempo
    - Alertas automáticos
    - Recomendações de mitigação
    """
    
    def __init__(self, 
                 risk_threshold: float = 60.0,
                 high_risk_threshold: int = 70,
                 medium_risk_threshold: int = 40):
        """
        Inicializa o analisador de risco
        
        Args:
            risk_threshold: Threshold de risco médio aceitável
            high_risk_threshold: Threshold para risco alto
            medium_risk_threshold: Threshold para risco médio
        """
        self.risk_threshold = risk_threshold
        self.high_risk_threshold = high_risk_threshold
        self.medium_risk_threshold = medium_risk_threshold
        
        self.semantic_validator = SemanticValidator()
        self.logger = logging.getLogger(f"{__name__}.RiskAnalyzer")
        
        # Armazenamento de métricas
        self.flow_risks: List[FlowRisk] = []
        self.component_risks: List[ComponentRisk] = []
        self.risk_trends: List[RiskTrend] = []
        self.risk_alerts: List[RiskAlert] = []
        
        # Cache de análise
        self.flow_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.component_cache: Dict[str, ComponentRisk] = {}
        
        # Mapeamento de fluxos críticos
        self.critical_flows = {
            "instagram_search": ["Instagram Graph API", "Keyword Analysis Service"],
            "facebook_analyze": ["Facebook Marketing API", "Competitor Analysis"],
            "youtube_search": ["YouTube Data API", "Video Analysis"],
            "tiktok_search": ["TikTok Business API", "Trend Analysis"],
            "pinterest_analyze": ["Pinterest API", "Visual Analysis"]
        }
    
    def analyze_flow_risk(self, 
                         flow_name: str,
                         flow_type: str,
                         test_metrics: List[Dict[str, Any]]) -> FlowRisk:
        """
        Analisa risco de um fluxo específico
        
        Args:
            flow_name: Nome do fluxo
            flow_type: Tipo do fluxo
            test_metrics: Métricas de teste do fluxo
            
        Returns:
            Análise de risco do fluxo
        """
        self.logger.info(f"Analisando risco do fluxo: {flow_name}")
        
        if not test_metrics:
            return FlowRisk(
                flow_name=flow_name,
                flow_type=flow_type,
                total_tests=0,
                avg_risk_score=0.0,
                max_risk_score=0,
                min_risk_score=0,
                high_risk_tests=0,
                medium_risk_tests=0,
                low_risk_tests=0
            )
        
        # Extrai RISK_SCOREs
        risk_scores = [t.get("risk_score", 0) for t in test_metrics]
        
        # Calcula estatísticas
        avg_risk_score = statistics.mean(risk_scores)
        max_risk_score = max(risk_scores)
        min_risk_score = min(risk_scores)
        
        # Categoriza por nível de risco
        high_risk_tests = len([r for r in risk_scores if r >= self.high_risk_threshold])
        medium_risk_tests = len([r for r in risk_scores if self.medium_risk_threshold <= r < self.high_risk_threshold])
        low_risk_tests = len([r for r in risk_scores if r < self.medium_risk_threshold])
        
        # Distribuição de risco
        risk_distribution = {
            "high": high_risk_tests,
            "medium": medium_risk_tests,
            "low": low_risk_tests
        }
        
        # Identifica componentes críticos
        critical_components = self._identify_critical_components(flow_name, test_metrics)
        
        # Identifica dependências
        dependencies = self._identify_dependencies(flow_name, test_metrics)
        
        # Cria análise de risco
        flow_risk = FlowRisk(
            flow_name=flow_name,
            flow_type=flow_type,
            total_tests=len(test_metrics),
            avg_risk_score=avg_risk_score,
            max_risk_score=max_risk_score,
            min_risk_score=min_risk_score,
            high_risk_tests=high_risk_tests,
            medium_risk_tests=medium_risk_tests,
            low_risk_tests=low_risk_tests,
            risk_distribution=risk_distribution,
            critical_components=critical_components,
            dependencies=dependencies
        )
        
        self.flow_risks.append(flow_risk)
        
        # Verifica se precisa criar alerta
        if avg_risk_score > self.risk_threshold:
            self._create_risk_alert(flow_risk, "threshold_exceeded")
        
        # Log estruturado
        risk_log = {
            "event": "flow_risk_analysis_completed",
            "flow_name": flow_name,
            "avg_risk_score": avg_risk_score,
            "high_risk_tests": high_risk_tests,
            "total_tests": len(test_metrics),
            "threshold_exceeded": avg_risk_score > self.risk_threshold,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"FLOW_RISK_LOG: {json.dumps(risk_log)}")
        
        return flow_risk
    
    def analyze_component_risk(self, 
                             component_name: str,
                             component_type: str,
                             complexity: int,
                             dependencies_count: int,
                             error_rate: float,
                             test_coverage: float = 0.0,
                             mutation_score: float = 0.0,
                             semantic_validation_score: float = 0.0) -> ComponentRisk:
        """
        Analisa risco de um componente específico
        
        Args:
            component_name: Nome do componente
            component_type: Tipo do componente
            complexity: Complexidade do componente
            dependencies_count: Número de dependências
            error_rate: Taxa de erro
            test_coverage: Cobertura de teste
            mutation_score: Score de mutation testing
            semantic_validation_score: Score de validação semântica
            
        Returns:
            Análise de risco do componente
        """
        # Calcula RISK_SCORE baseado em múltiplos fatores
        risk_score = self._calculate_component_risk_score(
            complexity, dependencies_count, error_rate, 
            test_coverage, mutation_score, semantic_validation_score
        )
        
        component_risk = ComponentRisk(
            component_name=component_name,
            component_type=component_type,
            risk_score=risk_score,
            complexity=complexity,
            dependencies_count=dependencies_count,
            error_rate=error_rate,
            test_coverage=test_coverage,
            mutation_score=mutation_score,
            semantic_validation_score=semantic_validation_score
        )
        
        self.component_risks.append(component_risk)
        self.component_cache[component_name] = component_risk
        
        # Log estruturado
        component_log = {
            "event": "component_risk_analysis_completed",
            "component_name": component_name,
            "component_type": component_type,
            "risk_score": risk_score,
            "complexity": complexity,
            "error_rate": error_rate,
            "test_coverage": test_coverage,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"COMPONENT_RISK_LOG: {json.dumps(component_log)}")
        
        return component_risk
    
    def _calculate_component_risk_score(self,
                                      complexity: int,
                                      dependencies_count: int,
                                      error_rate: float,
                                      test_coverage: float,
                                      mutation_score: float,
                                      semantic_validation_score: float) -> int:
        """
        Calcula RISK_SCORE de um componente
        
        Args:
            complexity: Complexidade
            dependencies_count: Número de dependências
            error_rate: Taxa de erro
            test_coverage: Cobertura de teste
            mutation_score: Score de mutation testing
            semantic_validation_score: Score de validação semântica
            
        Returns:
            RISK_SCORE do componente
        """
        risk_score = 30  # Base
        
        # Aumenta risco baseado em complexidade
        risk_score += complexity * 3
        
        # Aumenta risco baseado em dependências
        risk_score += dependencies_count * 2
        
        # Aumenta risco baseado em taxa de erro
        risk_score += int(error_rate * 50)
        
        # Diminui risco baseado em cobertura de teste
        risk_score -= int(test_coverage * 0.3)
        
        # Diminui risco baseado em mutation score
        risk_score -= int(mutation_score * 0.2)
        
        # Diminui risco baseado em validação semântica
        risk_score -= int(semantic_validation_score * 0.1)
        
        return max(0, min(risk_score, 100))
    
    def _identify_critical_components(self, 
                                    flow_name: str, 
                                    test_metrics: List[Dict[str, Any]]) -> List[str]:
        """
        Identifica componentes críticos de um fluxo
        
        Args:
            flow_name: Nome do fluxo
            test_metrics: Métricas de teste
            
        Returns:
            Lista de componentes críticos
        """
        critical_components = []
        
        # Adiciona componentes críticos conhecidos
        if flow_name in self.critical_flows:
            critical_components.extend(self.critical_flows[flow_name])
        
        # Identifica componentes com alto risco
        high_risk_tests = [t for t in test_metrics if t.get("risk_score", 0) >= self.high_risk_threshold]
        for test in high_risk_tests:
            component = test.get("component", "")
            if component and component not in critical_components:
                critical_components.append(component)
        
        return critical_components
    
    def _identify_dependencies(self, 
                             flow_name: str, 
                             test_metrics: List[Dict[str, Any]]) -> List[str]:
        """
        Identifica dependências de um fluxo
        
        Args:
            flow_name: Nome do fluxo
            test_metrics: Métricas de teste
            
        Returns:
            Lista de dependências
        """
        dependencies = set()
        
        # Extrai dependências dos testes
        for test in test_metrics:
            test_deps = test.get("dependencies", [])
            if isinstance(test_deps, list):
                dependencies.update(test_deps)
            elif isinstance(test_deps, str):
                dependencies.add(test_deps)
        
        # Adiciona dependências conhecidas por fluxo
        if flow_name == "instagram_search":
            dependencies.update(["Instagram Graph API", "Database", "Cache"])
        elif flow_name == "facebook_analyze":
            dependencies.update(["Facebook Marketing API", "Competitor Service", "Analytics"])
        elif flow_name == "youtube_search":
            dependencies.update(["YouTube Data API", "Video Processing", "Storage"])
        elif flow_name == "tiktok_search":
            dependencies.update(["TikTok Business API", "Trend Analysis", "ML Service"])
        elif flow_name == "pinterest_analyze":
            dependencies.update(["Pinterest API", "Image Analysis", "Recommendation Engine"])
        
        return list(dependencies)
    
    def _create_risk_alert(self, flow_risk: FlowRisk, alert_type: str):
        """
        Cria alerta de risco
        
        Args:
            flow_risk: Análise de risco do fluxo
            alert_type: Tipo do alerta
        """
        # Determina severidade
        severity = "low"
        if flow_risk.avg_risk_score >= 80:
            severity = "critical"
        elif flow_risk.avg_risk_score >= 70:
            severity = "high"
        elif flow_risk.avg_risk_score >= 60:
            severity = "medium"
        
        # Cria mensagem
        if alert_type == "threshold_exceeded":
            message = f"Risco médio do fluxo {flow_risk.flow_name} ({flow_risk.avg_risk_score:.1f}) excede o threshold ({self.risk_threshold})"
        elif alert_type == "risk_increase":
            message = f"Aumento significativo no risco do fluxo {flow_risk.flow_name}"
        else:
            message = f"Alerta de risco para o fluxo {flow_risk.flow_name}"
        
        # Gera recomendações
        recommendations = self._generate_risk_recommendations(flow_risk)
        
        # Cria alerta
        alert = RiskAlert(
            alert_id=f"risk_alert_{flow_risk.flow_name}_{int(time.time())}",
            flow_name=flow_risk.flow_name,
            alert_type=alert_type,
            severity=severity,
            message=message,
            current_risk_score=flow_risk.avg_risk_score,
            threshold=self.risk_threshold,
            recommendations=recommendations
        )
        
        self.risk_alerts.append(alert)
        
        # Log estruturado
        alert_log = {
            "event": "risk_alert_created",
            "alert_id": alert.alert_id,
            "flow_name": flow_risk.flow_name,
            "alert_type": alert_type,
            "severity": severity,
            "current_risk_score": flow_risk.avg_risk_score,
            "threshold": self.risk_threshold,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.error(f"RISK_ALERT_LOG: {json.dumps(alert_log)}")
    
    def _generate_risk_recommendations(self, flow_risk: FlowRisk) -> List[str]:
        """
        Gera recomendações para mitigação de risco
        
        Args:
            flow_risk: Análise de risco do fluxo
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        # Recomendações baseadas no risco médio
        if flow_risk.avg_risk_score >= 80:
            recommendations.extend([
                "Revisar arquitetura do fluxo",
                "Implementar circuit breakers",
                "Adicionar mais testes de integração",
                "Revisar dependências externas"
            ])
        elif flow_risk.avg_risk_score >= 70:
            recommendations.extend([
                "Adicionar testes de edge cases",
                "Implementar retry logic",
                "Melhorar logging e monitoramento",
                "Revisar validações de entrada"
            ])
        elif flow_risk.avg_risk_score >= 60:
            recommendations.extend([
                "Adicionar testes unitários",
                "Implementar validação semântica",
                "Melhorar tratamento de erros",
                "Revisar configurações"
            ])
        
        # Recomendações baseadas em componentes críticos
        if flow_risk.critical_components:
            recommendations.append(f"Focar testes nos componentes críticos: {', '.join(flow_risk.critical_components)}")
        
        # Recomendações baseadas em dependências
        if len(flow_risk.dependencies) > 5:
            recommendations.append("Considerar reduzir dependências externas")
        
        return recommendations
    
    def track_risk_trend(self, 
                        flow_name: str,
                        date: str,
                        test_metrics: List[Dict[str, Any]]) -> RiskTrend:
        """
        Rastreia tendência de risco ao longo do tempo
        
        Args:
            flow_name: Nome do fluxo
            date: Data da medição
            test_metrics: Métricas de teste
            
        Returns:
            Tendência de risco
        """
        if not test_metrics:
            return RiskTrend(
                flow_name=flow_name,
                date=date,
                avg_risk_score=0.0,
                high_risk_count=0,
                medium_risk_count=0,
                low_risk_count=0,
                total_tests=0,
                risk_change=0.0
            )
        
        # Calcula métricas atuais
        risk_scores = [t.get("risk_score", 0) for t in test_metrics]
        avg_risk_score = statistics.mean(risk_scores)
        high_risk_count = len([r for r in risk_scores if r >= self.high_risk_threshold])
        medium_risk_count = len([r for r in risk_scores if self.medium_risk_threshold <= r < self.high_risk_threshold])
        low_risk_count = len([r for r in risk_scores if r < self.medium_risk_threshold])
        
        # Calcula mudança em relação ao dia anterior
        previous_trend = next((t for t in self.risk_trends if t.flow_name == flow_name), None)
        risk_change = 0.0
        if previous_trend:
            risk_change = ((avg_risk_score - previous_trend.avg_risk_score) / max(previous_trend.avg_risk_score, 1)) * 100
        
        # Cria tendência
        trend = RiskTrend(
            flow_name=flow_name,
            date=date,
            avg_risk_score=avg_risk_score,
            high_risk_count=high_risk_count,
            medium_risk_count=medium_risk_count,
            low_risk_count=low_risk_count,
            total_tests=len(test_metrics),
            risk_change=risk_change
        )
        
        self.risk_trends.append(trend)
        
        # Cria alerta se houver aumento significativo
        if risk_change > 20:  # Aumento de mais de 20%
            flow_risk = FlowRisk(
                flow_name=flow_name,
                flow_type="unknown",
                total_tests=len(test_metrics),
                avg_risk_score=avg_risk_score,
                max_risk_score=max(risk_scores),
                min_risk_score=min(risk_scores),
                high_risk_tests=high_risk_count,
                medium_risk_tests=medium_risk_count,
                low_risk_tests=low_risk_count
            )
            self._create_risk_alert(flow_risk, "risk_increase")
        
        return trend
    
    def get_comprehensive_risk_report(self) -> Dict[str, Any]:
        """Gera relatório abrangente de risco"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_flows": len(self.flow_risks),
                "avg_risk_score": statistics.mean([f.avg_risk_score for f in self.flow_risks]) if self.flow_risks else 0.0,
                "high_risk_flows": len([f for f in self.flow_risks if f.avg_risk_score >= self.high_risk_threshold]),
                "threshold_exceeded_flows": len([f for f in self.flow_risks if f.avg_risk_score > self.risk_threshold]),
                "total_alerts": len(self.risk_alerts),
                "active_alerts": len([a for a in self.risk_alerts if not a.resolved])
            },
            "flow_risks": [
                {
                    "flow_name": f.flow_name,
                    "flow_type": f.flow_type,
                    "avg_risk_score": f.avg_risk_score,
                    "high_risk_tests": f.high_risk_tests,
                    "total_tests": f.total_tests,
                    "threshold_exceeded": f.avg_risk_score > self.risk_threshold,
                    "critical_components": f.critical_components,
                    "dependencies": f.dependencies,
                    "last_updated": datetime.fromtimestamp(f.last_updated).isoformat()
                }
                for f in self.flow_risks
            ],
            "component_risks": [
                {
                    "component_name": c.component_name,
                    "component_type": c.component_type,
                    "risk_score": c.risk_score,
                    "complexity": c.complexity,
                    "error_rate": c.error_rate,
                    "test_coverage": c.test_coverage,
                    "mutation_score": c.mutation_score,
                    "semantic_validation_score": c.semantic_validation_score,
                    "timestamp": datetime.fromtimestamp(c.timestamp).isoformat()
                }
                for c in self.component_risks
            ],
            "risk_trends": [
                {
                    "flow_name": t.flow_name,
                    "date": t.date,
                    "avg_risk_score": t.avg_risk_score,
                    "risk_change": t.risk_change,
                    "high_risk_count": t.high_risk_count,
                    "total_tests": t.total_tests,
                    "timestamp": datetime.fromtimestamp(t.timestamp).isoformat()
                }
                for t in self.risk_trends[-30:]  # Últimos 30 dias
            ],
            "risk_alerts": [
                {
                    "alert_id": a.alert_id,
                    "flow_name": a.flow_name,
                    "alert_type": a.alert_type,
                    "severity": a.severity,
                    "message": a.message,
                    "current_risk_score": a.current_risk_score,
                    "threshold": a.threshold,
                    "recommendations": a.recommendations,
                    "acknowledged": a.acknowledged,
                    "resolved": a.resolved,
                    "created_at": datetime.fromtimestamp(a.created_at).isoformat()
                }
                for a in self.risk_alerts[-10:]  # Últimos 10 alertas
            ]
        }

# Decorators para testes de análise de risco
@critical_risk
@semantic_validation
@real_data_validation
@production_scenario
@side_effects_monitoring
@performance_monitoring
class TestRiskAnalyzer:
    """Testes de integração para o analisador de risco"""
    
    @pytest.fixture
    def risk_analyzer(self):
        """Fixture para o analisador de risco"""
        return RiskAnalyzer(
            risk_threshold=60.0,
            high_risk_threshold=70,
            medium_risk_threshold=40
        )
    
    def test_flow_risk_analysis(self, risk_analyzer):
        """
        Testa análise de risco de fluxo
        
        RISK_SCORE: 80 (Alto - Análise de risco)
        """
        # Métricas de teste simuladas
        test_metrics = [
            {"risk_score": 85, "component": "Instagram API"},
            {"risk_score": 75, "component": "Keyword Analysis"},
            {"risk_score": 65, "component": "Database"},
            {"risk_score": 45, "component": "Cache"}
        ]
        
        # Analisa risco do fluxo
        flow_risk = risk_analyzer.analyze_flow_risk(
            flow_name="instagram_search",
            flow_type="api",
            test_metrics=test_metrics
        )
        
        # Validações
        assert flow_risk is not None
        assert flow_risk.flow_name == "instagram_search"
        assert flow_risk.total_tests == 4
        assert flow_risk.avg_risk_score == 67.5
        assert flow_risk.high_risk_tests == 2
        assert flow_risk.medium_risk_tests == 1
        assert flow_risk.low_risk_tests == 1
        
        # Verifica se alerta foi criado (threshold excedido)
        assert len(risk_analyzer.risk_alerts) > 0
        alert = risk_analyzer.risk_alerts[-1]
        assert alert.flow_name == "instagram_search"
        assert alert.alert_type == "threshold_exceeded"
        
        # Log estruturado
        logger.info(f"Flow risk analysis test completed: {flow_risk.flow_name}")
        logger.info(f"Average risk score: {flow_risk.avg_risk_score}")
        logger.info(f"High risk tests: {flow_risk.high_risk_tests}")
        logger.info(f"Alert created: {alert.alert_id}")
    
    def test_component_risk_analysis(self, risk_analyzer):
        """
        Testa análise de risco de componente
        
        RISK_SCORE: 75 (Alto - Análise de componente)
        """
        # Analisa risco de componente
        component_risk = risk_analyzer.analyze_component_risk(
            component_name="InstagramGraphAPI",
            component_type="service",
            complexity=8,
            dependencies_count=3,
            error_rate=0.05,
            test_coverage=85.0,
            mutation_score=90.0,
            semantic_validation_score=95.0
        )
        
        # Validações
        assert component_risk is not None
        assert component_risk.component_name == "InstagramGraphAPI"
        assert component_risk.component_type == "service"
        assert component_risk.complexity == 8
        assert component_risk.dependencies_count == 3
        assert component_risk.error_rate == 0.05
        assert component_risk.test_coverage == 85.0
        assert component_risk.mutation_score == 90.0
        assert component_risk.semantic_validation_score == 95.0
        assert 0 <= component_risk.risk_score <= 100
        
        # Log estruturado
        logger.info(f"Component risk analysis test completed: {component_risk.component_name}")
        logger.info(f"Risk score: {component_risk.risk_score}")
        logger.info(f"Complexity: {component_risk.complexity}")
        logger.info(f"Test coverage: {component_risk.test_coverage}%")
    
    def test_risk_trend_tracking(self, risk_analyzer):
        """
        Testa rastreamento de tendência de risco
        
        RISK_SCORE: 70 (Alto - Tendências)
        """
        # Primeira medição
        test_metrics_1 = [
            {"risk_score": 60},
            {"risk_score": 65},
            {"risk_score": 70}
        ]
        
        trend_1 = risk_analyzer.track_risk_trend(
            flow_name="facebook_analyze",
            date="2025-01-26",
            test_metrics=test_metrics_1
        )
        
        # Segunda medição (aumento de risco)
        test_metrics_2 = [
            {"risk_score": 80},
            {"risk_score": 85},
            {"risk_score": 90}
        ]
        
        trend_2 = risk_analyzer.track_risk_trend(
            flow_name="facebook_analyze",
            date="2025-01-27",
            test_metrics=test_metrics_2
        )
        
        # Validações
        assert trend_1.avg_risk_score == 65.0
        assert trend_2.avg_risk_score == 85.0
        assert trend_2.risk_change > 0  # Aumento de risco
        
        # Verifica se alerta foi criado para aumento de risco
        alerts = [a for a in risk_analyzer.risk_alerts if a.flow_name == "facebook_analyze"]
        assert len(alerts) > 0
        
        # Log estruturado
        logger.info(f"Risk trend tracking test completed")
        logger.info(f"Day 1 average: {trend_1.avg_risk_score}")
        logger.info(f"Day 2 average: {trend_2.avg_risk_score}")
        logger.info(f"Risk change: {trend_2.risk_change}%")
    
    def test_comprehensive_risk_report(self, risk_analyzer):
        """
        Testa geração de relatório abrangente de risco
        
        RISK_SCORE: 70 (Alto - Relatórios)
        """
        # Adiciona alguns dados para teste
        test_metrics = [
            {"risk_score": 75, "component": "API Gateway"},
            {"risk_score": 65, "component": "Database"}
        ]
        
        risk_analyzer.analyze_flow_risk("test_flow", "api", test_metrics)
        risk_analyzer.analyze_component_risk("TestComponent", "service", 5, 2, 0.02, 80.0, 85.0, 90.0)
        
        # Gera relatório
        report = risk_analyzer.get_comprehensive_risk_report()
        
        # Validações
        assert "timestamp" in report
        assert "summary" in report
        assert "flow_risks" in report
        assert "component_risks" in report
        assert "risk_trends" in report
        assert "risk_alerts" in report
        
        # Valida summary
        summary = report["summary"]
        assert "total_flows" in summary
        assert "avg_risk_score" in summary
        assert "high_risk_flows" in summary
        assert "total_alerts" in summary
        
        # Log estruturado
        logger.info(f"Comprehensive risk report test completed")
        logger.info(f"Total flows: {summary['total_flows']}")
        logger.info(f"Average risk score: {summary['avg_risk_score']}")
        logger.info(f"Total alerts: {summary['total_alerts']}")

if __name__ == "__main__":
    # Execução direta para testes
    pytest.main([__file__, "-v", "--tb=short"]) 