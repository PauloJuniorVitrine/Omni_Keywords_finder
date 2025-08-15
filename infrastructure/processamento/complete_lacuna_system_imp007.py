#!/usr/bin/env python3
"""
Sistema Completo de Lacunas - Versão Final
==========================================

Tracing ID: COMPLETE_LACUNA_SYSTEM_IMP007_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema completo que integra todos os componentes:
- Detector Híbrido (IMP001)
- Detector Semântico (IMP002)
- Validador de Contexto (IMP003)
- Matcher Semântico (IMP004)
- Validador de Qualidade (IMP005)
- Sistema de Fallback Inteligente (IMP006)

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.2-6.5
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

# Importar todos os componentes do sistema
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

from .quality_validator_imp005 import (
    QualityReport,
    QualityLevel,
    QualityValidator
)

from .intelligent_fallback_system_imp006 import (
    FallbackOption,
    FallbackResult,
    FallbackStrategy,
    IntelligentFallbackSystem
)

from .placeholder_unification_system_imp001 import (
    PlaceholderType,
    PlaceholderUnificationSystem
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemComponent(Enum):
    """Componentes do sistema."""
    HYBRID_DETECTOR = "hybrid_detector"
    SEMANTIC_DETECTOR = "semantic_detector"
    CONTEXT_VALIDATOR = "context_validator"
    SEMANTIC_MATCHER = "semantic_matcher"
    QUALITY_VALIDATOR = "quality_validator"
    FALLBACK_SYSTEM = "fallback_system"
    UNIFICATION_SYSTEM = "unification_system"


class ProcessingStage(Enum):
    """Estágios de processamento."""
    UNIFICATION = "unification"
    DETECTION = "detection"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    CONTEXT_VALIDATION = "context_validation"
    SEMANTIC_MATCHING = "semantic_matching"
    QUALITY_VALIDATION = "quality_validation"
    FALLBACK_GENERATION = "fallback_generation"
    INTEGRATION = "integration"


@dataclass
class ProcessingResult:
    """Resultado de um estágio de processamento."""
    stage: ProcessingStage
    success: bool
    data: Any
    execution_time: float
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CompleteLacunaResult:
    """Resultado completo do sistema de lacunas."""
    # Resultados dos componentes
    hybrid_result: DetectionResult
    semantic_result: SemanticDetectionResult
    context_result: ContextValidationResult
    matching_result: MatchingResult
    quality_result: QualityReport
    fallback_results: List[FallbackResult]
    
    # Dados integrados
    unified_text: str
    all_gaps: List[DetectedGap]
    semantic_gaps: List[SemanticGap]
    validated_gaps: List[DetectedGap]
    matched_gaps: List[SemanticMatch]
    fallback_options: List[FallbackOption]
    
    # Métricas gerais
    total_processing_time: float
    overall_quality_score: float
    system_health: str
    success: bool
    
    # Processamento detalhado
    processing_stages: List[ProcessingResult]
    errors: List[str]
    warnings: List[str]
    
    # Insights e recomendações
    insights: Dict[str, Any]
    recommendations: List[str]
    
    # Metadados
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CompleteLacunaSystem:
    """Sistema completo de lacunas que integra todos os componentes."""
    
    def __init__(self):
        """Inicializa o sistema completo."""
        # Inicializar todos os componentes
        self.hybrid_detector = HybridLacunaDetector()
        self.semantic_detector = SemanticGapDetector()
        self.context_validator = ContextValidator()
        self.semantic_matcher = SemanticMatcher()
        self.quality_validator = QualityValidator()
        self.fallback_system = IntelligentFallbackSystem()
        self.unification_system = PlaceholderUnificationSystem()
        
        # Configurações do sistema
        self.enable_semantic_analysis = True
        self.enable_context_validation = True
        self.enable_semantic_matching = True
        self.enable_quality_validation = True
        self.enable_fallback_generation = True
        
        # Cache do sistema
        self.system_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Métricas do sistema
        self.metrics = {
            "total_processing": 0,
            "successful_processing": 0,
            "failed_processing": 0,
            "avg_processing_time": 0.0,
            "processing_times": deque(maxlen=1000),
            "component_usage": defaultdict(int),
            "stage_success_rates": defaultdict(lambda: {"success": 0, "total": 0})
        }
        
        logger.info("CompleteLacunaSystem inicializado")
    
    def process_text(self, text: str, expected_gaps: Optional[List[Dict[str, Any]]] = None) -> CompleteLacunaResult:
        """
        Processa texto completo através de todos os componentes do sistema.
        
        Args:
            text: Texto para processamento
            expected_gaps: Lacunas esperadas (opcional)
            
        Returns:
            Resultado completo do processamento
        """
        start_time = time.time()
        
        try:
            # Verificar cache
            cache_key = f"{hash(text)}:{len(expected_gaps) if expected_gaps else 0}"
            if cache_key in self.system_cache:
                return self.system_cache[cache_key]
            
            # Inicializar resultados
            processing_stages = []
            all_errors = []
            all_warnings = []
            
            # Estágio 1: Unificação de Placeholders
            unification_result = self._process_unification_stage(text)
            processing_stages.append(unification_result)
            all_errors.extend(unification_result.errors)
            all_warnings.extend(unification_result.warnings)
            
            if not unification_result.success:
                return self._create_error_result(all_errors, all_warnings, time.time() - start_time)
            
            unified_text = unification_result.data
            
            # Estágio 2: Detecção Híbrida
            detection_result = self._process_detection_stage(unified_text)
            processing_stages.append(detection_result)
            all_errors.extend(detection_result.errors)
            all_warnings.extend(detection_result.warnings)
            
            if not detection_result.success:
                return self._create_error_result(all_errors, all_warnings, time.time() - start_time)
            
            hybrid_result = detection_result.data
            
            # Estágio 3: Análise Semântica
            semantic_result = None
            if self.enable_semantic_analysis:
                semantic_result = self._process_semantic_stage(unified_text, hybrid_result.gaps)
                processing_stages.append(semantic_result)
                all_errors.extend(semantic_result.errors)
                all_warnings.extend(semantic_result.warnings)
            
            # Estágio 4: Validação de Contexto
            context_result = None
            if self.enable_context_validation:
                context_result = self._process_context_stage(unified_text, hybrid_result.gaps)
                processing_stages.append(context_result)
                all_errors.extend(context_result.errors)
                all_warnings.extend(context_result.warnings)
            
            # Estágio 5: Matching Semântico
            matching_result = None
            if self.enable_semantic_matching:
                semantic_context = semantic_result.data.semantic_gaps[0].semantic_context if semantic_result and semantic_result.data.semantic_gaps else None
                matching_result = self._process_matching_stage(unified_text, hybrid_result.gaps, semantic_context)
                processing_stages.append(matching_result)
                all_errors.extend(matching_result.errors)
                all_warnings.extend(matching_result.warnings)
            
            # Estágio 6: Validação de Qualidade
            quality_result = None
            if self.enable_quality_validation:
                quality_result = self._process_quality_stage(unified_text, hybrid_result.gaps, expected_gaps)
                processing_stages.append(quality_result)
                all_errors.extend(quality_result.errors)
                all_warnings.extend(quality_result.warnings)
            
            # Estágio 7: Geração de Fallbacks
            fallback_results = []
            if self.enable_fallback_generation:
                fallback_results = self._process_fallback_stage(unified_text, hybrid_result.gaps, semantic_context)
                processing_stages.extend(fallback_results)
                for fallback_result in fallback_results:
                    all_errors.extend(fallback_result.errors)
                    all_warnings.extend(fallback_result.warnings)
            
            # Estágio 8: Integração Final
            integration_result = self._process_integration_stage(
                unified_text, hybrid_result, semantic_result, context_result, 
                matching_result, quality_result, fallback_results
            )
            processing_stages.append(integration_result)
            
            # Criar resultado final
            complete_result = self._create_complete_result(
                unified_text, hybrid_result, semantic_result, context_result,
                matching_result, quality_result, fallback_results,
                processing_stages, all_errors, all_warnings, time.time() - start_time
            )
            
            # Armazenar no cache
            self.system_cache[cache_key] = complete_result
            
            # Atualizar métricas
            self._update_metrics(True, time.time() - start_time, complete_result.overall_quality_score, processing_stages)
            
            return complete_result
            
        except Exception as e:
            logger.error(f"Erro no processamento completo: {e}")
            error_result = self._create_error_result([str(e)], [], time.time() - start_time)
            self._update_metrics(False, time.time() - start_time, 0.0, [])
            return error_result
    
    def _process_unification_stage(self, text: str) -> ProcessingResult:
        """Processa estágio de unificação de placeholders."""
        start_time = time.time()
        
        try:
            # Migrar para formato padrão
            migration_result = self.unification_system.migrate_to_standard_format(text)
            
            if migration_result.success:
                return ProcessingResult(
                    stage=ProcessingStage.UNIFICATION,
                    success=True,
                    data=migration_result.migrated_text,
                    execution_time=time.time() - start_time,
                    errors=migration_result.errors,
                    warnings=migration_result.warnings,
                    metadata={"migrations_applied": len(migration_result.migrations_applied)}
                )
            else:
                return ProcessingResult(
                    stage=ProcessingStage.UNIFICATION,
                    success=False,
                    data=text,  # Usar texto original em caso de falha
                    execution_time=time.time() - start_time,
                    errors=migration_result.errors,
                    warnings=migration_result.warnings,
                    metadata={"fallback_to_original": True}
                )
                
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.UNIFICATION,
                success=False,
                data=text,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _process_detection_stage(self, text: str) -> ProcessingResult:
        """Processa estágio de detecção híbrida."""
        start_time = time.time()
        
        try:
            detection_result = self.hybrid_detector.detect_gaps(text)
            
            return ProcessingResult(
                stage=ProcessingStage.DETECTION,
                success=detection_result.success,
                data=detection_result,
                execution_time=time.time() - start_time,
                errors=detection_result.errors,
                warnings=detection_result.warnings,
                metadata={
                    "gaps_detected": len(detection_result.gaps),
                    "avg_confidence": detection_result.confidence_avg
                }
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.DETECTION,
                success=False,
                data=None,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _process_semantic_stage(self, text: str, gaps: List[DetectedGap]) -> ProcessingResult:
        """Processa estágio de análise semântica."""
        start_time = time.time()
        
        try:
            semantic_result = self.semantic_detector.detect_semantic_gaps(text, gaps)
            
            return ProcessingResult(
                stage=ProcessingStage.SEMANTIC_ANALYSIS,
                success=semantic_result.success,
                data=semantic_result,
                execution_time=time.time() - start_time,
                errors=semantic_result.errors,
                warnings=semantic_result.warnings,
                metadata={
                    "semantic_gaps": len(semantic_result.semantic_gaps),
                    "avg_semantic_confidence": semantic_result.avg_semantic_confidence
                }
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.SEMANTIC_ANALYSIS,
                success=False,
                data=None,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _process_context_stage(self, text: str, gaps: List[DetectedGap]) -> ProcessingResult:
        """Processa estágio de validação de contexto."""
        start_time = time.time()
        
        try:
            context_result = self.context_validator.validate_context(text, gaps)
            
            return ProcessingResult(
                stage=ProcessingStage.CONTEXT_VALIDATION,
                success=context_result.is_valid,
                data=context_result,
                execution_time=time.time() - start_time,
                errors=context_result.errors,
                warnings=context_result.warnings,
                metadata={
                    "overall_score": context_result.overall_score,
                    "coherence_score": context_result.coherence_score
                }
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.CONTEXT_VALIDATION,
                success=False,
                data=None,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _process_matching_stage(self, text: str, gaps: List[DetectedGap], semantic_context: Optional[SemanticContext]) -> ProcessingResult:
        """Processa estágio de matching semântico."""
        start_time = time.time()
        
        try:
            matching_result = self.semantic_matcher.match_semantically(text, gaps, semantic_context)
            
            return ProcessingResult(
                stage=ProcessingStage.SEMANTIC_MATCHING,
                success=matching_result.success,
                data=matching_result,
                execution_time=time.time() - start_time,
                errors=matching_result.errors,
                warnings=matching_result.warnings,
                metadata={
                    "matches_generated": len(matching_result.matches),
                    "avg_match_quality": matching_result.avg_match_quality
                }
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.SEMANTIC_MATCHING,
                success=False,
                data=None,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _process_quality_stage(self, text: str, gaps: List[DetectedGap], expected_gaps: Optional[List[Dict[str, Any]]]) -> ProcessingResult:
        """Processa estágio de validação de qualidade."""
        start_time = time.time()
        
        try:
            quality_result = self.quality_validator.validate_system_quality(text, expected_gaps)
            
            return ProcessingResult(
                stage=ProcessingStage.QUALITY_VALIDATION,
                success=quality_result.overall_score >= 0.7,  # Threshold de qualidade
                data=quality_result,
                execution_time=time.time() - start_time,
                errors=[],
                warnings=quality_result.recommendations,
                metadata={
                    "overall_score": quality_result.overall_score,
                    "quality_level": quality_result.quality_level.value
                }
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.QUALITY_VALIDATION,
                success=False,
                data=None,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _process_fallback_stage(self, text: str, gaps: List[DetectedGap], semantic_context: Optional[SemanticContext]) -> List[ProcessingResult]:
        """Processa estágio de geração de fallbacks."""
        fallback_results = []
        
        for gap in gaps:
            start_time = time.time()
            
            try:
                fallback_result = self.fallback_system.generate_fallbacks(text, gap, semantic_context)
                
                processing_result = ProcessingResult(
                    stage=ProcessingStage.FALLBACK_GENERATION,
                    success=fallback_result.success,
                    data=fallback_result,
                    execution_time=time.time() - start_time,
                    errors=fallback_result.errors,
                    warnings=fallback_result.warnings,
                    metadata={
                        "gap_id": f"{gap.start_pos}_{gap.end_pos}",
                        "fallback_options": len(fallback_result.fallback_options)
                    }
                )
                
                fallback_results.append(processing_result)
                
            except Exception as e:
                processing_result = ProcessingResult(
                    stage=ProcessingStage.FALLBACK_GENERATION,
                    success=False,
                    data=None,
                    execution_time=time.time() - start_time,
                    errors=[str(e)],
                    warnings=[],
                    metadata={"error": str(e)}
                )
                
                fallback_results.append(processing_result)
        
        return fallback_results
    
    def _process_integration_stage(self, unified_text: str, hybrid_result: DetectionResult, 
                                 semantic_result: Optional[ProcessingResult], context_result: Optional[ProcessingResult],
                                 matching_result: Optional[ProcessingResult], quality_result: Optional[ProcessingResult],
                                 fallback_results: List[ProcessingResult]) -> ProcessingResult:
        """Processa estágio de integração final."""
        start_time = time.time()
        
        try:
            # Integrar todos os resultados
            integration_data = {
                "unified_text": unified_text,
                "hybrid_result": hybrid_result,
                "semantic_result": semantic_result.data if semantic_result and semantic_result.success else None,
                "context_result": context_result.data if context_result and context_result.success else None,
                "matching_result": matching_result.data if matching_result and matching_result.success else None,
                "quality_result": quality_result.data if quality_result and quality_result.success else None,
                "fallback_results": [fr.data for fr in fallback_results if fr.success]
            }
            
            return ProcessingResult(
                stage=ProcessingStage.INTEGRATION,
                success=True,
                data=integration_data,
                execution_time=time.time() - start_time,
                errors=[],
                warnings=[],
                metadata={"integration_success": True}
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.INTEGRATION,
                success=False,
                data=None,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _create_complete_result(self, unified_text: str, hybrid_result: DetectionResult,
                              semantic_result: Optional[ProcessingResult], context_result: Optional[ProcessingResult],
                              matching_result: Optional[ProcessingResult], quality_result: Optional[ProcessingResult],
                              fallback_results: List[ProcessingResult], processing_stages: List[ProcessingResult],
                              errors: List[str], warnings: List[str], total_time: float) -> CompleteLacunaResult:
        """Cria resultado completo integrando todos os componentes."""
        
        # Extrair dados dos resultados
        semantic_data = semantic_result.data if semantic_result and semantic_result.success else None
        context_data = context_result.data if context_result and context_result.success else None
        matching_data = matching_result.data if matching_result and matching_result.success else None
        quality_data = quality_result.data if quality_result and quality_result.success else None
        
        # Preparar dados integrados
        all_gaps = hybrid_result.gaps
        semantic_gaps = semantic_data.semantic_gaps if semantic_data else []
        validated_gaps = all_gaps if context_data and context_data.is_valid else []
        matched_gaps = matching_data.matches if matching_data else []
        fallback_options = []
        
        for fallback_result in fallback_results:
            if fallback_result.success and fallback_result.data.best_fallback:
                fallback_options.append(fallback_result.data.best_fallback)
        
        # Calcular score geral de qualidade
        overall_quality_score = quality_data.overall_score if quality_data else 0.0
        
        # Determinar saúde do sistema
        system_health = self._determine_system_health(processing_stages, overall_quality_score)
        
        # Gerar insights
        insights = self._generate_system_insights(
            hybrid_result, semantic_data, context_data, matching_data, quality_data, fallback_results
        )
        
        # Gerar recomendações
        recommendations = self._generate_system_recommendations(
            processing_stages, errors, warnings, overall_quality_score
        )
        
        return CompleteLacunaResult(
            # Resultados dos componentes
            hybrid_result=hybrid_result,
            semantic_result=semantic_data,
            context_result=context_data,
            matching_result=matching_data,
            quality_result=quality_data,
            fallback_results=[fr.data for fr in fallback_results if fr.success],
            
            # Dados integrados
            unified_text=unified_text,
            all_gaps=all_gaps,
            semantic_gaps=semantic_gaps,
            validated_gaps=validated_gaps,
            matched_gaps=matched_gaps,
            fallback_options=fallback_options,
            
            # Métricas gerais
            total_processing_time=total_time,
            overall_quality_score=overall_quality_score,
            system_health=system_health,
            success=len(errors) == 0,
            
            # Processamento detalhado
            processing_stages=processing_stages,
            errors=errors,
            warnings=warnings,
            
            # Insights e recomendações
            insights=insights,
            recommendations=recommendations,
            
            # Metadados
            timestamp=datetime.now(),
            metadata={
                "components_used": len([s for s in processing_stages if s.success]),
                "total_stages": len(processing_stages)
            }
        )
    
    def _create_error_result(self, errors: List[str], warnings: List[str], total_time: float) -> CompleteLacunaResult:
        """Cria resultado de erro quando o processamento falha."""
        return CompleteLacunaResult(
            # Resultados dos componentes (vazios)
            hybrid_result=DetectionResult([], 0, 0.0, 0.0, DetectionMethod.HYBRID, ValidationLevel.BASIC, False, [], []),
            semantic_result=None,
            context_result=None,
            matching_result=None,
            quality_result=None,
            fallback_results=[],
            
            # Dados integrados (vazios)
            unified_text="",
            all_gaps=[],
            semantic_gaps=[],
            validated_gaps=[],
            matched_gaps=[],
            fallback_options=[],
            
            # Métricas gerais
            total_processing_time=total_time,
            overall_quality_score=0.0,
            system_health="error",
            success=False,
            
            # Processamento detalhado
            processing_stages=[],
            errors=errors,
            warnings=warnings,
            
            # Insights e recomendações
            insights={},
            recommendations=["Corrija os erros antes de reprocessar"],
            
            # Metadados
            timestamp=datetime.now(),
            metadata={"error": True}
        )
    
    def _determine_system_health(self, processing_stages: List[ProcessingResult], quality_score: float) -> str:
        """Determina a saúde geral do sistema."""
        successful_stages = len([s for s in processing_stages if s.success])
        total_stages = len(processing_stages)
        
        if total_stages == 0:
            return "unknown"
        
        success_rate = successful_stages / total_stages
        
        if success_rate >= 0.9 and quality_score >= 0.8:
            return "excellent"
        elif success_rate >= 0.8 and quality_score >= 0.7:
            return "good"
        elif success_rate >= 0.7 and quality_score >= 0.6:
            return "fair"
        elif success_rate >= 0.5:
            return "poor"
        else:
            return "critical"
    
    def _generate_system_insights(self, hybrid_result: DetectionResult, semantic_result: Optional[SemanticDetectionResult],
                                context_result: Optional[ContextValidationResult], matching_result: Optional[MatchingResult],
                                quality_result: Optional[QualityReport], fallback_results: List[ProcessingResult]) -> Dict[str, Any]:
        """Gera insights sobre o sistema."""
        insights = {
            "detection_insights": {
                "total_gaps": len(hybrid_result.gaps),
                "avg_confidence": hybrid_result.confidence_avg,
                "detection_method": hybrid_result.method_used.value
            },
            "semantic_insights": {},
            "context_insights": {},
            "matching_insights": {},
            "quality_insights": {},
            "fallback_insights": {}
        }
        
        if semantic_result:
            insights["semantic_insights"] = {
                "semantic_gaps": len(semantic_result.semantic_gaps),
                "avg_semantic_confidence": semantic_result.avg_semantic_confidence
            }
        
        if context_result:
            insights["context_insights"] = {
                "is_valid": context_result.is_valid,
                "overall_score": context_result.overall_score,
                "coherence_score": context_result.coherence_score
            }
        
        if matching_result:
            insights["matching_insights"] = {
                "matches_generated": len(matching_result.matches),
                "avg_match_quality": matching_result.avg_match_quality,
                "strategy_used": matching_result.strategy_used.value
            }
        
        if quality_result:
            insights["quality_insights"] = {
                "overall_score": quality_result.overall_score,
                "quality_level": quality_result.quality_level.value,
                "issues_count": len(quality_result.issues)
            }
        
        if fallback_results:
            insights["fallback_insights"] = {
                "fallback_results": len(fallback_results),
                "successful_fallbacks": len([fr for fr in fallback_results if fr.success])
            }
        
        return insights
    
    def _generate_system_recommendations(self, processing_stages: List[ProcessingResult], errors: List[str],
                                       warnings: List[str], quality_score: float) -> List[str]:
        """Gera recomendações para o sistema."""
        recommendations = []
        
        # Recomendações baseadas em erros
        if errors:
            recommendations.append(f"Corrija {len(errors)} erro(s) identificado(s)")
        
        # Recomendações baseadas em warnings
        if warnings:
            recommendations.append(f"Revise {len(warnings)} aviso(s) para melhorar o sistema")
        
        # Recomendações baseadas na qualidade
        if quality_score < 0.7:
            recommendations.append("Melhore a qualidade geral do sistema")
        
        # Recomendações baseadas nos estágios
        failed_stages = [s for s in processing_stages if not s.success]
        if failed_stages:
            recommendations.append(f"Corrija {len(failed_stages)} estágio(s) que falharam")
        
        if not recommendations:
            recommendations.append("Sistema funcionando adequadamente")
        
        return recommendations
    
    def _update_metrics(self, success: bool, processing_time: float, quality_score: float, processing_stages: List[ProcessingResult]):
        """Atualiza métricas do sistema."""
        self.metrics["total_processing"] += 1
        
        if success:
            self.metrics["successful_processing"] += 1
            self.metrics["processing_times"].append(processing_time)
            self.metrics["avg_processing_time"] = statistics.mean(self.metrics["processing_times"])
        else:
            self.metrics["failed_processing"] += 1
        
        # Atualizar uso de componentes
        for stage in processing_stages:
            component_name = stage.stage.value
            self.metrics["component_usage"][component_name] += 1
            
            # Atualizar taxa de sucesso por estágio
            stage_stats = self.metrics["stage_success_rates"][component_name]
            stage_stats["total"] += 1
            if stage.success:
                stage_stats["success"] += 1


# Funções de conveniência
def process_text_complete(text: str, expected_gaps: Optional[List[Dict[str, Any]]] = None) -> CompleteLacunaResult:
    """Função de conveniência para processamento completo."""
    system = CompleteLacunaSystem()
    return system.process_text(text, expected_gaps)


def get_complete_system_stats() -> Dict[str, Any]:
    """Obtém estatísticas do sistema completo."""
    system = CompleteLacunaSystem()
    return system.metrics


if __name__ == "__main__":
    # Teste completo do sistema
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
    
    # Processar texto completo
    result = process_text_complete(test_text, expected_gaps)
    
    print(f"Processamento completo concluído!")
    print(f"Sucesso: {result.success}")
    print(f"Saúde do sistema: {result.system_health}")
    print(f"Score de qualidade: {result.overall_quality_score:.2f}")
    print(f"Tempo total: {result.total_processing_time:.3f}s")
    print(f"Lacunas detectadas: {len(result.all_gaps)}")
    print(f"Lacunas semânticas: {len(result.semantic_gaps)}")
    print(f"Matches gerados: {len(result.matched_gaps)}")
    print(f"Opções de fallback: {len(result.fallback_options)}")
    
    print(f"\nEstágios processados: {len(result.processing_stages)}")
    for stage in result.processing_stages:
        print(f"  - {stage.stage.value}: {'✅' if stage.success else '❌'} ({stage.execution_time:.3f}s)")
    
    if result.errors:
        print(f"\nErros encontrados ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.recommendations:
        print(f"\nRecomendações ({len(result.recommendations)}):")
        for rec in result.recommendations:
            print(f"  - {rec}")
    
    print(f"\nInsights do sistema:")
    for category, insights in result.insights.items():
        print(f"  {category}: {insights}") 