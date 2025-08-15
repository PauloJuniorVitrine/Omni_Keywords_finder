#!/usr/bin/env python3
"""
Validador de Qualidade - Versão Avançada
========================================

Tracing ID: QUALITY_VALIDATOR_IMP005_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema de validação de qualidade que:
- Valida qualidade geral do sistema de lacunas
- Verifica precisão e recall
- Analisa performance e eficiência
- Detecta problemas de qualidade
- Fornece métricas detalhadas
- Integra todos os componentes

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.5
Ruleset: enterprise_control_layer.yaml
"""

import re
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict, deque
import statistics
import numpy as np
from pathlib import Path

# Importar todos os sistemas existentes
from .hybrid_lacuna_detector_imp001 import (
    DetectedGap, 
    DetectionResult, 
    DetectionMethod, 
    ValidationLevel,
    HybridLacunaDetector
)

from .semantic_lacuna_detector_imp002 import (
    SemanticGap,
    SemanticContext,
    SemanticDetectionResult,
    SemanticGapDetector
)

from .context_validator_imp003 import (
    ContextValidationResult,
    ContextValidationType,
    ValidationSeverity,
    ContextValidator
)

from .semantic_matcher_imp004 import (
    SemanticMatch,
    MatchingResult,
    MatchingStrategy,
    SemanticMatcher
)

from .placeholder_unification_system_imp001 import (
    PlaceholderType,
    PlaceholderUnificationSystem
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Métricas de qualidade."""
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    RELIABILITY = "reliability"
    CONSISTENCY = "consistency"


class QualityLevel(Enum):
    """Níveis de qualidade."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class QualityIssue:
    """Problema de qualidade identificado."""
    metric: QualityMetric
    level: QualityLevel
    description: str
    severity: str
    impact: str
    recommendation: str
    current_value: float
    target_value: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QualityReport:
    """Relatório de qualidade completo."""
    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[QualityMetric, float]
    issues: List[QualityIssue]
    recommendations: List[str]
    performance_metrics: Dict[str, Any]
    validation_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class QualityValidator:
    """Validador de qualidade avançado."""
    
    def __init__(self):
        """Inicializa o validador de qualidade."""
        self.quality_thresholds = {
            QualityMetric.PRECISION: 0.85,
            QualityMetric.RECALL: 0.80,
            QualityMetric.F1_SCORE: 0.82,
            QualityMetric.ACCURACY: 0.90,
            QualityMetric.PERFORMANCE: 0.75,
            QualityMetric.EFFICIENCY: 0.80,
            QualityMetric.RELIABILITY: 0.95,
            QualityMetric.CONSISTENCY: 0.88
        }
        
        self.quality_weights = {
            QualityMetric.PRECISION: 0.25,
            QualityMetric.RECALL: 0.25,
            QualityMetric.F1_SCORE: 0.20,
            QualityMetric.ACCURACY: 0.15,
            QualityMetric.PERFORMANCE: 0.05,
            QualityMetric.EFFICIENCY: 0.05,
            QualityMetric.RELIABILITY: 0.03,
            QualityMetric.CONSISTENCY: 0.02
        }
        
        # Componentes do sistema
        self.hybrid_detector = HybridLacunaDetector()
        self.semantic_detector = SemanticGapDetector()
        self.context_validator = ContextValidator()
        self.semantic_matcher = SemanticMatcher()
        self.unification_system = PlaceholderUnificationSystem()
        
        # Cache de validações
        self.validation_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Métricas de performance
        self.metrics = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "avg_validation_time": 0.0,
            "validation_times": deque(maxlen=1000),
            "quality_scores": deque(maxlen=1000),
            "issue_distribution": defaultdict(int)
        }
        
        logger.info("QualityValidator inicializado")
    
    def validate_system_quality(self, text: str, expected_gaps: Optional[List[Dict[str, Any]]] = None) -> QualityReport:
        """
        Valida a qualidade geral do sistema de lacunas.
        
        Args:
            text: Texto para validação
            expected_gaps: Lacunas esperadas (para cálculo de precisão/recall)
            
        Returns:
            Relatório de qualidade completo
        """
        start_time = time.time()
        
        try:
            # Verificar cache
            cache_key = f"{hash(text)}:{len(expected_gaps) if expected_gaps else 0}"
            if cache_key in self.validation_cache:
                return self.validation_cache[cache_key]
            
            # Executar todos os componentes do sistema
            hybrid_result = self.hybrid_detector.detect_gaps(text)
            semantic_result = self.semantic_detector.detect_semantic_gaps(text, hybrid_result.gaps)
            context_result = self.context_validator.validate_context(text, hybrid_result.gaps)
            matching_result = self.semantic_matcher.match_semantically(text, hybrid_result.gaps)
            
            # Calcular métricas de qualidade
            metrics = self._calculate_quality_metrics(
                hybrid_result, semantic_result, context_result, matching_result, expected_gaps
            )
            
            # Detectar problemas de qualidade
            issues = self._detect_quality_issues(metrics)
            
            # Calcular score geral
            overall_score = self._calculate_overall_quality_score(metrics)
            quality_level = self._determine_quality_level(overall_score)
            
            # Gerar recomendações
            recommendations = self._generate_quality_recommendations(issues, metrics)
            
            # Coletar métricas de performance
            performance_metrics = self._collect_performance_metrics(
                hybrid_result, semantic_result, context_result, matching_result
            )
            
            report = QualityReport(
                overall_score=overall_score,
                quality_level=quality_level,
                metrics=metrics,
                issues=issues,
                recommendations=recommendations,
                performance_metrics=performance_metrics,
                validation_time=time.time() - start_time,
                timestamp=datetime.now(),
                metadata={
                    "cache_key": cache_key,
                    "text_length": len(text),
                    "gaps_detected": len(hybrid_result.gaps),
                    "semantic_gaps": len(semantic_result.semantic_gaps),
                    "context_valid": context_result.is_valid,
                    "matches_generated": len(matching_result.matches)
                }
            )
            
            # Armazenar no cache
            self.validation_cache[cache_key] = report
            
            # Atualizar métricas
            self._update_metrics(True, time.time() - start_time, overall_score, issues)
            
            return report
            
        except Exception as e:
            logger.error(f"Erro na validação de qualidade: {e}")
            
            report = QualityReport(
                overall_score=0.0,
                quality_level=QualityLevel.UNACCEPTABLE,
                metrics={},
                issues=[],
                recommendations=[f"Erro na validação: {e}"],
                performance_metrics={},
                validation_time=time.time() - start_time,
                timestamp=datetime.now(),
                metadata={"error": str(e)}
            )
            
            self._update_metrics(False, time.time() - start_time, 0.0, [])
            
            return report
    
    def _calculate_quality_metrics(self, hybrid_result: DetectionResult, semantic_result: SemanticDetectionResult, 
                                 context_result: ContextValidationResult, matching_result: MatchingResult,
                                 expected_gaps: Optional[List[Dict[str, Any]]]) -> Dict[QualityMetric, float]:
        """Calcula todas as métricas de qualidade."""
        metrics = {}
        
        # Precisão e Recall (se expected_gaps for fornecido)
        if expected_gaps:
            precision, recall, f1_score, accuracy = self._calculate_precision_recall(hybrid_result.gaps, expected_gaps)
            metrics[QualityMetric.PRECISION] = precision
            metrics[QualityMetric.RECALL] = recall
            metrics[QualityMetric.F1_SCORE] = f1_score
            metrics[QualityMetric.ACCURACY] = accuracy
        else:
            # Usar métricas baseadas em confiança
            metrics[QualityMetric.PRECISION] = self._calculate_confidence_based_precision(hybrid_result)
            metrics[QualityMetric.RECALL] = self._calculate_confidence_based_recall(hybrid_result)
            metrics[QualityMetric.F1_SCORE] = self._calculate_f1_score(metrics[QualityMetric.PRECISION], metrics[QualityMetric.RECALL])
            metrics[QualityMetric.ACCURACY] = self._calculate_accuracy(hybrid_result)
        
        # Performance
        metrics[QualityMetric.PERFORMANCE] = self._calculate_performance_metric(hybrid_result, semantic_result, context_result, matching_result)
        
        # Eficiência
        metrics[QualityMetric.EFFICIENCY] = self._calculate_efficiency_metric(hybrid_result, semantic_result, context_result, matching_result)
        
        # Confiabilidade
        metrics[QualityMetric.RELIABILITY] = self._calculate_reliability_metric(hybrid_result, semantic_result, context_result, matching_result)
        
        # Consistência
        metrics[QualityMetric.CONSISTENCY] = self._calculate_consistency_metric(hybrid_result, semantic_result, context_result, matching_result)
        
        return metrics
    
    def _calculate_precision_recall(self, detected_gaps: List[DetectedGap], expected_gaps: List[Dict[str, Any]]) -> Tuple[float, float, float, float]:
        """Calcula precisão, recall, F1-score e acurácia."""
        if not detected_gaps and not expected_gaps:
            return 1.0, 1.0, 1.0, 1.0
        
        if not detected_gaps:
            return 0.0, 0.0, 0.0, 0.0
        
        if not expected_gaps:
            return 0.0, 1.0, 0.0, 0.0
        
        # Converter expected_gaps para formato comparável
        expected_positions = []
        for expected in expected_gaps:
            start = expected.get("start_pos", 0)
            end = expected.get("end_pos", start + 10)
            expected_positions.append((start, end))
        
        # Contar true positives, false positives, false negatives
        true_positives = 0
        false_positives = 0
        
        for detected in detected_gaps:
            detected_pos = (detected.start_pos, detected.end_pos)
            is_true_positive = False
            
            for expected_pos in expected_positions:
                # Verificar sobreposição
                if self._positions_overlap(detected_pos, expected_pos):
                    true_positives += 1
                    is_true_positive = True
                    break
            
            if not is_true_positive:
                false_positives += 1
        
        false_negatives = len(expected_gaps) - true_positives
        
        # Calcular métricas
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = true_positives / (true_positives + false_positives + false_negatives) if (true_positives + false_positives + false_negatives) > 0 else 0.0
        
        return precision, recall, f1_score, accuracy
    
    def _positions_overlap(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Verifica se duas posições se sobrepõem."""
        start1, end1 = pos1
        start2, end2 = pos2
        
        return max(start1, start2) < min(end1, end2)
    
    def _calculate_confidence_based_precision(self, hybrid_result: DetectionResult) -> float:
        """Calcula precisão baseada em confiança."""
        if not hybrid_result.gaps:
            return 0.0
        
        # Usar confiança média como proxy para precisão
        avg_confidence = hybrid_result.confidence_avg
        return min(1.0, avg_confidence * 1.1)  # Ajuste para compensar viés
    
    def _calculate_confidence_based_recall(self, hybrid_result: DetectionResult) -> float:
        """Calcula recall baseado em confiança."""
        if not hybrid_result.gaps:
            return 0.0
        
        # Usar número de detecções como proxy para recall
        detection_count = len(hybrid_result.gaps)
        # Assumir que mais detecções = melhor recall (com limite)
        recall = min(1.0, detection_count / 10.0)  # Normalizar
        return recall
    
    def _calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calcula F1-score."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def _calculate_accuracy(self, hybrid_result: DetectionResult) -> float:
        """Calcula acurácia baseada em confiança e sucesso."""
        if not hybrid_result.gaps:
            return 0.0
        
        # Combinar confiança e sucesso
        confidence_factor = hybrid_result.confidence_avg
        success_factor = 1.0 if hybrid_result.success else 0.5
        
        accuracy = (confidence_factor + success_factor) / 2
        return min(1.0, accuracy)
    
    def _calculate_performance_metric(self, hybrid_result: DetectionResult, semantic_result: SemanticDetectionResult,
                                    context_result: ContextValidationResult, matching_result: MatchingResult) -> float:
        """Calcula métrica de performance."""
        # Combinar tempos de execução
        total_time = (
            hybrid_result.detection_time +
            semantic_result.semantic_analysis_time +
            context_result.validation_time +
            matching_result.matching_time
        )
        
        # Normalizar tempo (assumir que < 1 segundo é excelente)
        if total_time < 1.0:
            performance = 1.0
        elif total_time < 2.0:
            performance = 0.9
        elif total_time < 5.0:
            performance = 0.8
        elif total_time < 10.0:
            performance = 0.6
        else:
            performance = 0.4
        
        return performance
    
    def _calculate_efficiency_metric(self, hybrid_result: DetectionResult, semantic_result: SemanticDetectionResult,
                                   context_result: ContextValidationResult, matching_result: MatchingResult) -> float:
        """Calcula métrica de eficiência."""
        # Eficiência baseada na relação entre resultados e recursos
        total_gaps = len(hybrid_result.gaps)
        semantic_gaps = len(semantic_result.semantic_gaps)
        context_valid = context_result.is_valid
        matches_generated = len(matching_result.matches)
        
        if total_gaps == 0:
            return 0.0
        
        # Calcular eficiência como relação entre outputs e inputs
        efficiency_factors = []
        
        # Eficiência de detecção semântica
        if total_gaps > 0:
            semantic_efficiency = semantic_gaps / total_gaps
            efficiency_factors.append(semantic_efficiency)
        
        # Eficiência de validação contextual
        efficiency_factors.append(1.0 if context_valid else 0.5)
        
        # Eficiência de matching
        if total_gaps > 0:
            matching_efficiency = matches_generated / total_gaps
            efficiency_factors.append(matching_efficiency)
        
        # Média dos fatores de eficiência
        efficiency = statistics.mean(efficiency_factors) if efficiency_factors else 0.0
        return min(1.0, efficiency)
    
    def _calculate_reliability_metric(self, hybrid_result: DetectionResult, semantic_result: SemanticDetectionResult,
                                    context_result: ContextValidationResult, matching_result: MatchingResult) -> float:
        """Calcula métrica de confiabilidade."""
        reliability_factors = []
        
        # Confiabilidade baseada no sucesso das operações
        reliability_factors.append(1.0 if hybrid_result.success else 0.5)
        reliability_factors.append(1.0 if semantic_result.success else 0.5)
        reliability_factors.append(1.0 if context_result.is_valid else 0.7)
        reliability_factors.append(1.0 if matching_result.success else 0.5)
        
        # Confiabilidade baseada na ausência de erros
        error_penalty = 0.1
        if hybrid_result.errors:
            reliability_factors.append(1.0 - (len(hybrid_result.errors) * error_penalty))
        if semantic_result.errors:
            reliability_factors.append(1.0 - (len(semantic_result.errors) * error_penalty))
        if context_result.errors:
            reliability_factors.append(1.0 - (len(context_result.errors) * error_penalty))
        if matching_result.errors:
            reliability_factors.append(1.0 - (len(matching_result.errors) * error_penalty))
        
        reliability = statistics.mean(reliability_factors) if reliability_factors else 0.0
        return min(1.0, max(0.0, reliability))
    
    def _calculate_consistency_metric(self, hybrid_result: DetectionResult, semantic_result: SemanticDetectionResult,
                                    context_result: ContextValidationResult, matching_result: MatchingResult) -> float:
        """Calcula métrica de consistência."""
        consistency_factors = []
        
        # Consistência entre diferentes métodos de detecção
        if hybrid_result.gaps and semantic_result.semantic_gaps:
            detection_consistency = len(semantic_result.semantic_gaps) / len(hybrid_result.gaps)
            consistency_factors.append(detection_consistency)
        
        # Consistência de validação contextual
        consistency_factors.append(context_result.consistency_score)
        
        # Consistência de matching
        if matching_result.matches:
            match_qualities = [match.match_quality for match in matching_result.matches]
            consistency_factors.append(statistics.mean(match_qualities))
        
        # Consistência de confiança
        if hybrid_result.gaps:
            confidences = [gap.confidence for gap in hybrid_result.gaps]
            confidence_std = statistics.stdev(confidences) if len(confidences) > 1 else 0.0
            confidence_consistency = max(0.0, 1.0 - confidence_std)
            consistency_factors.append(confidence_consistency)
        
        consistency = statistics.mean(consistency_factors) if consistency_factors else 0.0
        return min(1.0, consistency)
    
    def _detect_quality_issues(self, metrics: Dict[QualityMetric, float]) -> List[QualityIssue]:
        """Detecta problemas de qualidade."""
        issues = []
        
        for metric, value in metrics.items():
            threshold = self.quality_thresholds[metric]
            
            if value < threshold:
                level = self._determine_issue_level(value, threshold)
                severity = self._determine_issue_severity(level)
                
                issue = QualityIssue(
                    metric=metric,
                    level=level,
                    description=f"{metric.value} está abaixo do threshold ({value:.2f} < {threshold:.2f})",
                    severity=severity,
                    impact=self._determine_issue_impact(metric),
                    recommendation=self._generate_issue_recommendation(metric, value, threshold),
                    current_value=value,
                    target_value=threshold
                )
                issues.append(issue)
        
        return issues
    
    def _determine_issue_level(self, current_value: float, target_value: float) -> QualityLevel:
        """Determina o nível de um problema."""
        ratio = current_value / target_value
        
        if ratio >= 0.95:
            return QualityLevel.EXCELLENT
        elif ratio >= 0.85:
            return QualityLevel.GOOD
        elif ratio >= 0.70:
            return QualityLevel.FAIR
        elif ratio >= 0.50:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _determine_issue_severity(self, level: QualityLevel) -> str:
        """Determina a severidade de um problema."""
        severity_mapping = {
            QualityLevel.EXCELLENT: "baixa",
            QualityLevel.GOOD: "baixa",
            QualityLevel.FAIR: "média",
            QualityLevel.POOR: "alta",
            QualityLevel.UNACCEPTABLE: "crítica"
        }
        return severity_mapping.get(level, "média")
    
    def _determine_issue_impact(self, metric: QualityMetric) -> str:
        """Determina o impacto de um problema."""
        impact_mapping = {
            QualityMetric.PRECISION: "Falsos positivos podem afetar a qualidade das sugestões",
            QualityMetric.RECALL: "Lacunas não detectadas podem comprometer a completude",
            QualityMetric.F1_SCORE: "Equilíbrio geral entre precisão e recall comprometido",
            QualityMetric.ACCURACY: "Acurácia geral do sistema comprometida",
            QualityMetric.PERFORMANCE: "Performance pode afetar a experiência do usuário",
            QualityMetric.EFFICIENCY: "Ineficiência pode aumentar custos computacionais",
            QualityMetric.RELIABILITY: "Confiabilidade do sistema comprometida",
            QualityMetric.CONSISTENCY: "Inconsistências podem confundir o usuário"
        }
        return impact_mapping.get(metric, "Impacto não especificado")
    
    def _generate_issue_recommendation(self, metric: QualityMetric, current_value: float, target_value: float) -> str:
        """Gera recomendação para um problema específico."""
        recommendations = {
            QualityMetric.PRECISION: "Ajuste os thresholds de detecção ou melhore a validação semântica",
            QualityMetric.RECALL: "Expanda os padrões de detecção ou adicione mais métodos",
            QualityMetric.F1_SCORE: "Balanceie precisão e recall ajustando parâmetros",
            QualityMetric.ACCURACY: "Revise a lógica de detecção e validação",
            QualityMetric.PERFORMANCE: "Otimize algoritmos ou implemente cache",
            QualityMetric.EFFICIENCY: "Reduza processamento desnecessário ou paralelize operações",
            QualityMetric.RELIABILITY: "Implemente tratamento de erros mais robusto",
            QualityMetric.CONSISTENCY: "Padronize métodos e validações"
        }
        
        base_recommendation = recommendations.get(metric, "Revise e ajuste o sistema")
        
        if current_value < target_value * 0.5:
            return f"CRÍTICO: {base_recommendation}"
        elif current_value < target_value * 0.8:
            return f"IMPORTANTE: {base_recommendation}"
        else:
            return f"SUAVE: {base_recommendation}"
    
    def _calculate_overall_quality_score(self, metrics: Dict[QualityMetric, float]) -> float:
        """Calcula o score geral de qualidade."""
        if not metrics:
            return 0.0
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric, value in metrics.items():
            weight = self.quality_weights.get(metric, 0.0)
            weighted_score += value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_score / total_weight
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determina o nível de qualidade geral."""
        if overall_score >= 0.9:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.8:
            return QualityLevel.GOOD
        elif overall_score >= 0.7:
            return QualityLevel.FAIR
        elif overall_score >= 0.5:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _generate_quality_recommendations(self, issues: List[QualityIssue], metrics: Dict[QualityMetric, float]) -> List[str]:
        """Gera recomendações gerais de qualidade."""
        recommendations = []
        
        # Recomendações baseadas em problemas críticos
        critical_issues = [i for i in issues if i.severity == "crítica"]
        if critical_issues:
            recommendations.append(f"Corrija {len(critical_issues)} problemas críticos prioritariamente")
        
        # Recomendações baseadas em métricas baixas
        low_metrics = [metric for metric, value in metrics.items() if value < 0.6]
        if low_metrics:
            recommendations.append(f"Foque na melhoria das métricas: {', '.join([m.value for m in low_metrics])}")
        
        # Recomendações gerais
        if not recommendations:
            recommendations.append("Sistema está funcionando bem. Mantenha monitoramento contínuo")
        
        return recommendations
    
    def _collect_performance_metrics(self, hybrid_result: DetectionResult, semantic_result: SemanticDetectionResult,
                                   context_result: ContextValidationResult, matching_result: MatchingResult) -> Dict[str, Any]:
        """Coleta métricas de performance detalhadas."""
        return {
            "detection_performance": {
                "total_gaps": len(hybrid_result.gaps),
                "detection_time": hybrid_result.detection_time,
                "avg_confidence": hybrid_result.confidence_avg,
                "success": hybrid_result.success
            },
            "semantic_performance": {
                "semantic_gaps": len(semantic_result.semantic_gaps),
                "analysis_time": semantic_result.semantic_analysis_time,
                "avg_semantic_confidence": semantic_result.avg_semantic_confidence,
                "success": semantic_result.success
            },
            "context_performance": {
                "is_valid": context_result.is_valid,
                "validation_time": context_result.validation_time,
                "coherence_score": context_result.coherence_score,
                "consistency_score": context_result.consistency_score
            },
            "matching_performance": {
                "matches_generated": len(matching_result.matches),
                "matching_time": matching_result.matching_time,
                "avg_match_quality": matching_result.avg_match_quality,
                "avg_confidence": matching_result.avg_confidence,
                "success": matching_result.success
            },
            "overall_performance": {
                "total_time": (
                    hybrid_result.detection_time +
                    semantic_result.semantic_analysis_time +
                    context_result.validation_time +
                    matching_result.matching_time
                ),
                "total_operations": 4,
                "success_rate": sum([
                    hybrid_result.success,
                    semantic_result.success,
                    context_result.is_valid,
                    matching_result.success
                ]) / 4
            }
        }
    
    def _update_metrics(self, success: bool, validation_time: float, overall_score: float, issues: List[QualityIssue]):
        """Atualiza métricas de performance."""
        self.metrics["total_validations"] += 1
        
        if success:
            self.metrics["successful_validations"] += 1
            self.metrics["validation_times"].append(validation_time)
            self.metrics["avg_validation_time"] = statistics.mean(self.metrics["validation_times"])
            self.metrics["quality_scores"].append(overall_score)
            
            # Distribuição de problemas
            for issue in issues:
                self.metrics["issue_distribution"][issue.metric.value] += 1
        else:
            self.metrics["failed_validations"] += 1


# Funções de conveniência
def validate_system_quality(text: str, expected_gaps: Optional[List[Dict[str, Any]]] = None) -> QualityReport:
    """Função de conveniência para validação de qualidade."""
    validator = QualityValidator()
    return validator.validate_system_quality(text, expected_gaps)


def get_quality_validation_stats() -> Dict[str, Any]:
    """Obtém estatísticas de validação de qualidade."""
    validator = QualityValidator()
    return validator.metrics


if __name__ == "__main__":
    # Teste básico do sistema
    test_text = """
    Preciso criar um artigo sobre {primary_keyword} para o público {target_audience}.
    O conteúdo deve ser {content_type} com tom {tone}.
    """
    
    # Simular lacunas esperadas
    expected_gaps = [
        {"start_pos": 35, "end_pos": 52, "type": "primary_keyword"},
        {"start_pos": 65, "end_pos": 82, "type": "target_audience"},
        {"start_pos": 105, "end_pos": 118, "type": "content_type"},
        {"start_pos": 127, "end_pos": 132, "type": "tone"}
    ]
    
    # Validar qualidade do sistema
    report = validate_system_quality(test_text, expected_gaps)
    
    print(f"Score geral: {report.overall_score:.2f}")
    print(f"Nível de qualidade: {report.quality_level.value}")
    print(f"Problemas encontrados: {len(report.issues)}")
    print(f"Recomendações: {len(report.recommendations)}")
    print(f"Tempo de validação: {report.validation_time:.3f}s")
    
    # Mostrar métricas detalhadas
    print("\nMétricas detalhadas:")
    for metric, value in report.metrics.items():
        print(f"  {metric.value}: {value:.2f}")
    
    # Mostrar problemas críticos
    critical_issues = [i for i in report.issues if i.severity == "crítica"]
    if critical_issues:
        print(f"\nProblemas críticos ({len(critical_issues)}):")
        for issue in critical_issues:
            print(f"  - {issue.description}")
            print(f"    Recomendação: {issue.recommendation}") 