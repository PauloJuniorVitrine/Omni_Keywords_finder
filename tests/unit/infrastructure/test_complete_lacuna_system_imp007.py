# =============================================================================
# Testes Unitários - Complete Lacuna System IMP007
# =============================================================================
# 
# Testes para o sistema completo de lacunas que integra todos os componentes
# Baseados completamente na implementação real do código
#
# Arquivo: infrastructure/processamento/complete_lacuna_system_imp007.py
# Linhas: 898
# Tracing ID: test-complete-lacuna-system-imp007-2025-01-27-001
# =============================================================================

import pytest
import time
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from typing import List, Dict, Any, Optional

from infrastructure.processamento.complete_lacuna_system_imp007 import (
    CompleteLacunaSystem,
    CompleteLacunaResult,
    ProcessingResult,
    ProcessingStage,
    SystemComponent,
    process_text_complete,
    get_complete_system_stats
)

# Mocks para os componentes importados
from infrastructure.processamento.hybrid_lacuna_detector_imp001 import (
    DetectedGap, 
    DetectionResult, 
    DetectionMethod, 
    ValidationLevel
)

from infrastructure.processamento.semantic_lacuna_detector_imp002 import (
    SemanticGap,
    SemanticContext,
    SemanticDetectionResult
)

from infrastructure.processamento.context_validator_imp003 import (
    ContextValidationResult,
    ContextValidationType,
    ValidationSeverity
)

from infrastructure.processamento.semantic_matcher_imp004 import (
    SemanticMatch,
    MatchingResult,
    MatchingStrategy
)

from infrastructure.processamento.quality_validator_imp005 import (
    QualityReport,
    QualityLevel
)

from infrastructure.processamento.intelligent_fallback_system_imp006 import (
    FallbackOption,
    FallbackResult,
    FallbackStrategy
)

from infrastructure.processamento.placeholder_unification_system_imp001 import (
    PlaceholderType
)


class TestCompleteLacunaSystem:
    """Testes para o CompleteLacunaSystem"""
    
    @pytest.fixture
    def system(self):
        """Fixture para criar instância do sistema"""
        return CompleteLacunaSystem()
    
    @pytest.fixture
    def sample_text(self):
        """Fixture com texto de exemplo baseado no código real"""
        return """
        Preciso criar um artigo sobre {primary_keyword} para o público {target_audience}.
        O conteúdo deve ser {content_type} com tom {tone}.
        """
    
    @pytest.fixture
    def expected_gaps(self):
        """Fixture com lacunas esperadas baseadas no código real"""
        return [
            {"start_pos": 35, "end_pos": 52, "type": "primary_keyword"},
            {"start_pos": 65, "end_pos": 82, "type": "target_audience"},
            {"start_pos": 105, "end_pos": 118, "type": "content_type"},
            {"start_pos": 127, "end_pos": 132, "type": "tone"}
        ]
    
    @pytest.fixture
    def mock_detected_gap(self):
        """Fixture para criar gap detectado mock"""
        return DetectedGap(
            start_pos=35,
            end_pos=52,
            gap_type="primary_keyword",
            confidence=0.85,
            method_used=DetectionMethod.HYBRID,
            validation_level=ValidationLevel.BASIC
        )
    
    @pytest.fixture
    def mock_detection_result(self, mock_detected_gap):
        """Fixture para criar resultado de detecção mock"""
        return DetectionResult(
            gaps=[mock_detected_gap],
            total_gaps=1,
            confidence_avg=0.85,
            precision_score=0.90,
            method_used=DetectionMethod.HYBRID,
            validation_level=ValidationLevel.BASIC,
            success=True,
            errors=[],
            warnings=[]
        )
    
    def test_inicializacao_sistema(self, system):
        """Teste de inicialização do sistema"""
        # Arrange & Act - Sistema já criado no fixture
        
        # Assert - Verificar componentes inicializados
        assert system.hybrid_detector is not None
        assert system.semantic_detector is not None
        assert system.context_validator is not None
        assert system.semantic_matcher is not None
        assert system.quality_validator is not None
        assert system.fallback_system is not None
        assert system.unification_system is not None
        
        # Verificar configurações
        assert system.enable_semantic_analysis is True
        assert system.enable_context_validation is True
        assert system.enable_semantic_matching is True
        assert system.enable_quality_validation is True
        assert system.enable_fallback_generation is True
        
        # Verificar cache e métricas
        assert system.system_cache == {}
        assert system.cache_ttl == 3600  # 1 hora
        
        # Verificar estrutura das métricas
        assert "total_processing" in system.metrics
        assert "successful_processing" in system.metrics
        assert "failed_processing" in system.metrics
        assert "avg_processing_time" in system.metrics
        assert "processing_times" in system.metrics
        assert "component_usage" in system.metrics
        assert "stage_success_rates" in system.metrics
        
        assert system.metrics["total_processing"] == 0
        assert system.metrics["successful_processing"] == 0
        assert system.metrics["failed_processing"] == 0
        assert system.metrics["avg_processing_time"] == 0.0
    
    @patch('infrastructure.processamento.complete_lacuna_system_imp007.PlaceholderUnificationSystem')
    @patch('infrastructure.processamento.complete_lacuna_system_imp007.HybridLacunaDetector')
    @patch('infrastructure.processamento.complete_lacuna_system_imp007.SemanticGapDetector')
    @patch('infrastructure.processamento.complete_lacuna_system_imp007.ContextValidator')
    @patch('infrastructure.processamento.complete_lacuna_system_imp007.SemanticMatcher')
    @patch('infrastructure.processamento.complete_lacuna_system_imp007.QualityValidator')
    @patch('infrastructure.processamento.complete_lacuna_system_imp007.IntelligentFallbackSystem')
    def test_process_text_sucesso_completo(self, mock_fallback, mock_quality, mock_matcher, 
                                          mock_context, mock_semantic, mock_hybrid, mock_unification,
                                          system, sample_text, expected_gaps, mock_detection_result):
        """Teste de processamento completo com sucesso"""
        # Arrange - Configurar mocks
        mock_unification.return_value.migrate_to_standard_format.return_value = Mock(
            success=True,
            migrated_text=sample_text,
            errors=[],
            warnings=[],
            migrations_applied=[]
        )
        
        mock_hybrid.return_value.detect_gaps.return_value = mock_detection_result
        
        mock_semantic.return_value.detect_semantic_gaps.return_value = Mock(
            success=True,
            semantic_gaps=[],
            avg_semantic_confidence=0.8,
            errors=[],
            warnings=[]
        )
        
        mock_context.return_value.validate_context.return_value = Mock(
            is_valid=True,
            overall_score=0.85,
            coherence_score=0.9,
            errors=[],
            warnings=[]
        )
        
        mock_matcher.return_value.match_semantically.return_value = Mock(
            success=True,
            matches=[],
            avg_match_quality=0.8,
            strategy_used=MatchingStrategy.SEMANTIC,
            errors=[],
            warnings=[]
        )
        
        mock_quality.return_value.validate_system_quality.return_value = Mock(
            overall_score=0.85,
            quality_level=QualityLevel.GOOD,
            issues=[],
            recommendations=[]
        )
        
        mock_fallback.return_value.generate_fallbacks.return_value = Mock(
            success=True,
            fallback_options=[],
            best_fallback=None,
            errors=[],
            warnings=[]
        )
        
        # Act
        result = system.process_text(sample_text, expected_gaps)
        
        # Assert
        assert isinstance(result, CompleteLacunaResult)
        assert result.success is True
        assert result.system_health in ["excellent", "good", "fair", "poor", "critical"]
        assert result.overall_quality_score > 0
        assert result.total_processing_time > 0
        assert result.unified_text == sample_text
        
        # Verificar estrutura dos resultados
        assert result.hybrid_result is not None
        assert result.semantic_result is not None
        assert result.context_result is not None
        assert result.matching_result is not None
        assert result.quality_result is not None
        assert isinstance(result.fallback_results, list)
        
        # Verificar dados integrados
        assert isinstance(result.all_gaps, list)
        assert isinstance(result.semantic_gaps, list)
        assert isinstance(result.validated_gaps, list)
        assert isinstance(result.matched_gaps, list)
        assert isinstance(result.fallback_options, list)
        
        # Verificar processamento detalhado
        assert isinstance(result.processing_stages, list)
        assert len(result.processing_stages) > 0
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        
        # Verificar insights e recomendações
        assert isinstance(result.insights, dict)
        assert isinstance(result.recommendations, list)
        
        # Verificar metadados
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.metadata, dict)
    
    def test_process_text_cache_functionality(self, system, sample_text):
        """Teste de funcionalidade de cache"""
        # Arrange
        cache_key = f"{hash(sample_text)}:0"
        
        # Act - Primeira execução (deve processar)
        with patch.object(system, '_process_unification_stage') as mock_unification:
            mock_unification.return_value = ProcessingResult(
                stage=ProcessingStage.UNIFICATION,
                success=True,
                data=sample_text,
                execution_time=0.1,
                errors=[],
                warnings=[]
            )
            
            with patch.object(system, '_process_detection_stage') as mock_detection:
                mock_detection.return_value = ProcessingResult(
                    stage=ProcessingStage.DETECTION,
                    success=True,
                    data=Mock(gaps=[]),
                    execution_time=0.1,
                    errors=[],
                    warnings=[]
                )
                
                # Mock outros estágios para sucesso
                with patch.object(system, '_process_semantic_stage'), \
                     patch.object(system, '_process_context_stage'), \
                     patch.object(system, '_process_matching_stage'), \
                     patch.object(system, '_process_quality_stage'), \
                     patch.object(system, '_process_fallback_stage'), \
                     patch.object(system, '_process_integration_stage'), \
                     patch.object(system, '_create_complete_result'):
                    
                    result1 = system.process_text(sample_text)
        
        # Act - Segunda execução (deve vir do cache)
        result2 = system.process_text(sample_text)
        
        # Assert
        assert cache_key in system.system_cache
        assert result1 == result2
    
    def test_process_unification_stage_sucesso(self, system, sample_text):
        """Teste do estágio de unificação com sucesso"""
        # Arrange
        mock_migration_result = Mock(
            success=True,
            migrated_text="texto unificado",
            errors=[],
            warnings=[],
            migrations_applied=["migration1", "migration2"]
        )
        
        system.unification_system.migrate_to_standard_format = Mock(return_value=mock_migration_result)
        
        # Act
        result = system._process_unification_stage(sample_text)
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.UNIFICATION
        assert result.success is True
        assert result.data == "texto unificado"
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["migrations_applied"] == 2
    
    def test_process_unification_stage_falha(self, system, sample_text):
        """Teste do estágio de unificação com falha"""
        # Arrange
        mock_migration_result = Mock(
            success=False,
            migrated_text=sample_text,
            errors=["Erro de migração"],
            warnings=["Aviso de migração"],
            migrations_applied=[]
        )
        
        system.unification_system.migrate_to_standard_format = Mock(return_value=mock_migration_result)
        
        # Act
        result = system._process_unification_stage(sample_text)
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.UNIFICATION
        assert result.success is False
        assert result.data == sample_text  # Deve usar texto original
        assert result.execution_time > 0
        assert result.errors == ["Erro de migração"]
        assert result.warnings == ["Aviso de migração"]
        assert result.metadata["fallback_to_original"] is True
    
    def test_process_detection_stage_sucesso(self, system, sample_text, mock_detection_result):
        """Teste do estágio de detecção com sucesso"""
        # Arrange
        system.hybrid_detector.detect_gaps = Mock(return_value=mock_detection_result)
        
        # Act
        result = system._process_detection_stage(sample_text)
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.DETECTION
        assert result.success is True
        assert result.data == mock_detection_result
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["gaps_detected"] == 1
        assert result.metadata["avg_confidence"] == 0.85
    
    def test_process_semantic_stage_sucesso(self, system, sample_text, mock_detected_gap):
        """Teste do estágio semântico com sucesso"""
        # Arrange
        mock_semantic_result = Mock(
            success=True,
            semantic_gaps=[],
            avg_semantic_confidence=0.8,
            errors=[],
            warnings=[]
        )
        
        system.semantic_detector.detect_semantic_gaps = Mock(return_value=mock_semantic_result)
        
        # Act
        result = system._process_semantic_stage(sample_text, [mock_detected_gap])
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.SEMANTIC_ANALYSIS
        assert result.success is True
        assert result.data == mock_semantic_result
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["semantic_gaps"] == 0
        assert result.metadata["avg_semantic_confidence"] == 0.8
    
    def test_process_context_stage_sucesso(self, system, sample_text, mock_detected_gap):
        """Teste do estágio de contexto com sucesso"""
        # Arrange
        mock_context_result = Mock(
            is_valid=True,
            overall_score=0.85,
            coherence_score=0.9,
            errors=[],
            warnings=[]
        )
        
        system.context_validator.validate_context = Mock(return_value=mock_context_result)
        
        # Act
        result = system._process_context_stage(sample_text, [mock_detected_gap])
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.CONTEXT_VALIDATION
        assert result.success is True
        assert result.data == mock_context_result
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["overall_score"] == 0.85
        assert result.metadata["coherence_score"] == 0.9
    
    def test_process_matching_stage_sucesso(self, system, sample_text, mock_detected_gap):
        """Teste do estágio de matching com sucesso"""
        # Arrange
        mock_matching_result = Mock(
            success=True,
            matches=[],
            avg_match_quality=0.8,
            strategy_used=MatchingStrategy.SEMANTIC,
            errors=[],
            warnings=[]
        )
        
        system.semantic_matcher.match_semantically = Mock(return_value=mock_matching_result)
        
        # Act
        result = system._process_matching_stage(sample_text, [mock_detected_gap], None)
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.SEMANTIC_MATCHING
        assert result.success is True
        assert result.data == mock_matching_result
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["matches_generated"] == 0
        assert result.metadata["avg_match_quality"] == 0.8
    
    def test_process_quality_stage_sucesso(self, system, sample_text, mock_detected_gap, expected_gaps):
        """Teste do estágio de qualidade com sucesso"""
        # Arrange
        mock_quality_result = Mock(
            overall_score=0.85,
            quality_level=QualityLevel.GOOD,
            issues=[],
            recommendations=[]
        )
        
        system.quality_validator.validate_system_quality = Mock(return_value=mock_quality_result)
        
        # Act
        result = system._process_quality_stage(sample_text, [mock_detected_gap], expected_gaps)
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.QUALITY_VALIDATION
        assert result.success is True  # Score >= 0.7
        assert result.data == mock_quality_result
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["overall_score"] == 0.85
        assert result.metadata["quality_level"] == QualityLevel.GOOD.value
    
    def test_process_quality_stage_falha_threshold(self, system, sample_text, mock_detected_gap):
        """Teste do estágio de qualidade com falha por threshold"""
        # Arrange
        mock_quality_result = Mock(
            overall_score=0.6,  # Abaixo do threshold de 0.7
            quality_level=QualityLevel.POOR,
            issues=["Problema de qualidade"],
            recommendations=["Melhorar qualidade"]
        )
        
        system.quality_validator.validate_system_quality = Mock(return_value=mock_quality_result)
        
        # Act
        result = system._process_quality_stage(sample_text, [mock_detected_gap], None)
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.QUALITY_VALIDATION
        assert result.success is False  # Score < 0.7
        assert result.data == mock_quality_result
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == ["Problema de qualidade", "Melhorar qualidade"]
    
    def test_process_fallback_stage_sucesso(self, system, sample_text, mock_detected_gap):
        """Teste do estágio de fallback com sucesso"""
        # Arrange
        mock_fallback_result = Mock(
            success=True,
            fallback_options=[],
            best_fallback=Mock(),
            errors=[],
            warnings=[]
        )
        
        system.fallback_system.generate_fallbacks = Mock(return_value=mock_fallback_result)
        
        # Act
        results = system._process_fallback_stage(sample_text, [mock_detected_gap], None)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 1
        
        result = results[0]
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.FALLBACK_GENERATION
        assert result.success is True
        assert result.data == mock_fallback_result
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["gap_id"] == "35_52"
        assert result.metadata["fallback_options"] == 0
    
    def test_process_integration_stage_sucesso(self, system, sample_text, mock_detection_result):
        """Teste do estágio de integração com sucesso"""
        # Arrange
        mock_semantic_result = ProcessingResult(
            stage=ProcessingStage.SEMANTIC_ANALYSIS,
            success=True,
            data=Mock(semantic_gaps=[]),
            execution_time=0.1,
            errors=[],
            warnings=[]
        )
        
        mock_context_result = ProcessingResult(
            stage=ProcessingStage.CONTEXT_VALIDATION,
            success=True,
            data=Mock(),
            execution_time=0.1,
            errors=[],
            warnings=[]
        )
        
        mock_matching_result = ProcessingResult(
            stage=ProcessingStage.SEMANTIC_MATCHING,
            success=True,
            data=Mock(),
            execution_time=0.1,
            errors=[],
            warnings=[]
        )
        
        mock_quality_result = ProcessingResult(
            stage=ProcessingStage.QUALITY_VALIDATION,
            success=True,
            data=Mock(),
            execution_time=0.1,
            errors=[],
            warnings=[]
        )
        
        # Act
        result = system._process_integration_stage(
            sample_text, mock_detection_result, mock_semantic_result,
            mock_context_result, mock_matching_result, mock_quality_result, []
        )
        
        # Assert
        assert isinstance(result, ProcessingResult)
        assert result.stage == ProcessingStage.INTEGRATION
        assert result.success is True
        assert result.data is not None
        assert result.execution_time > 0
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["integration_success"] is True
    
    def test_create_complete_result(self, system, sample_text, mock_detection_result):
        """Teste de criação de resultado completo"""
        # Arrange
        processing_stages = [
            ProcessingResult(
                stage=ProcessingStage.UNIFICATION,
                success=True,
                data=sample_text,
                execution_time=0.1,
                errors=[],
                warnings=[]
            )
        ]
        
        # Act
        result = system._create_complete_result(
            sample_text, mock_detection_result, None, None, None, None, [],
            processing_stages, [], [], 0.5
        )
        
        # Assert
        assert isinstance(result, CompleteLacunaResult)
        assert result.hybrid_result == mock_detection_result
        assert result.unified_text == sample_text
        assert result.total_processing_time == 0.5
        assert result.success is True
        assert len(result.processing_stages) == 1
        assert isinstance(result.insights, dict)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.timestamp, datetime)
    
    def test_create_error_result(self, system):
        """Teste de criação de resultado de erro"""
        # Arrange
        errors = ["Erro 1", "Erro 2"]
        warnings = ["Aviso 1"]
        total_time = 0.3
        
        # Act
        result = system._create_error_result(errors, warnings, total_time)
        
        # Assert
        assert isinstance(result, CompleteLacunaResult)
        assert result.success is False
        assert result.system_health == "error"
        assert result.overall_quality_score == 0.0
        assert result.total_processing_time == total_time
        assert result.errors == errors
        assert result.warnings == warnings
        assert result.recommendations == ["Corrija os erros antes de reprocessar"]
        assert result.metadata["error"] is True
    
    def test_determine_system_health_excellent(self, system):
        """Teste de determinação de saúde do sistema - excellent"""
        # Arrange
        processing_stages = [
            ProcessingResult(ProcessingStage.UNIFICATION, True, None, 0.1, [], []),
            ProcessingResult(ProcessingStage.DETECTION, True, None, 0.1, [], []),
            ProcessingResult(ProcessingStage.SEMANTIC_ANALYSIS, True, None, 0.1, [], [])
        ]
        quality_score = 0.85
        
        # Act
        health = system._determine_system_health(processing_stages, quality_score)
        
        # Assert
        assert health == "excellent"
    
    def test_determine_system_health_good(self, system):
        """Teste de determinação de saúde do sistema - good"""
        # Arrange
        processing_stages = [
            ProcessingResult(ProcessingStage.UNIFICATION, True, None, 0.1, [], []),
            ProcessingResult(ProcessingStage.DETECTION, True, None, 0.1, [], []),
            ProcessingResult(ProcessingStage.SEMANTIC_ANALYSIS, False, None, 0.1, [], [])
        ]
        quality_score = 0.75
        
        # Act
        health = system._determine_system_health(processing_stages, quality_score)
        
        # Assert
        assert health == "good"
    
    def test_determine_system_health_critical(self, system):
        """Teste de determinação de saúde do sistema - critical"""
        # Arrange
        processing_stages = [
            ProcessingResult(ProcessingStage.UNIFICATION, False, None, 0.1, [], []),
            ProcessingResult(ProcessingStage.DETECTION, False, None, 0.1, [], [])
        ]
        quality_score = 0.3
        
        # Act
        health = system._determine_system_health(processing_stages, quality_score)
        
        # Assert
        assert health == "critical"
    
    def test_generate_system_insights(self, system, mock_detection_result):
        """Teste de geração de insights do sistema"""
        # Arrange
        mock_semantic_result = Mock(
            semantic_gaps=[],
            avg_semantic_confidence=0.8
        )
        
        mock_context_result = Mock(
            is_valid=True,
            overall_score=0.85,
            coherence_score=0.9
        )
        
        mock_matching_result = Mock(
            matches=[],
            avg_match_quality=0.8,
            strategy_used=MatchingStrategy.SEMANTIC
        )
        
        mock_quality_result = Mock(
            overall_score=0.85,
            quality_level=QualityLevel.GOOD,
            issues=[]
        )
        
        # Act
        insights = system._generate_system_insights(
            mock_detection_result, mock_semantic_result, mock_context_result,
            mock_matching_result, mock_quality_result, []
        )
        
        # Assert
        assert isinstance(insights, dict)
        assert "detection_insights" in insights
        assert "semantic_insights" in insights
        assert "context_insights" in insights
        assert "matching_insights" in insights
        assert "quality_insights" in insights
        assert "fallback_insights" in insights
        
        # Verificar insights de detecção
        detection_insights = insights["detection_insights"]
        assert detection_insights["total_gaps"] == 1
        assert detection_insights["avg_confidence"] == 0.85
        assert detection_insights["detection_method"] == DetectionMethod.HYBRID.value
    
    def test_generate_system_recommendations(self, system):
        """Teste de geração de recomendações do sistema"""
        # Arrange
        processing_stages = [
            ProcessingResult(ProcessingStage.UNIFICATION, True, None, 0.1, [], []),
            ProcessingResult(ProcessingStage.DETECTION, False, None, 0.1, ["Erro"], [])
        ]
        errors = ["Erro geral"]
        warnings = ["Aviso geral"]
        quality_score = 0.6
        
        # Act
        recommendations = system._generate_system_recommendations(
            processing_stages, errors, warnings, quality_score
        )
        
        # Assert
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert "Corrija 1 erro(s) identificado(s)" in recommendations
        assert "Revise 1 aviso(s) para melhorar o sistema" in recommendations
        assert "Melhore a qualidade geral do sistema" in recommendations
        assert "Corrija 1 estágio(s) que falharam" in recommendations
    
    def test_update_metrics_sucesso(self, system):
        """Teste de atualização de métricas com sucesso"""
        # Arrange
        processing_stages = [
            ProcessingResult(ProcessingStage.UNIFICATION, True, None, 0.1, [], []),
            ProcessingResult(ProcessingStage.DETECTION, True, None, 0.1, [], [])
        ]
        
        # Act
        system._update_metrics(True, 0.5, 0.85, processing_stages)
        
        # Assert
        assert system.metrics["total_processing"] == 1
        assert system.metrics["successful_processing"] == 1
        assert system.metrics["failed_processing"] == 0
        assert system.metrics["avg_processing_time"] == 0.5
        
        # Verificar uso de componentes
        assert system.metrics["component_usage"]["unification"] == 1
        assert system.metrics["component_usage"]["detection"] == 1
        
        # Verificar taxa de sucesso por estágio
        assert system.metrics["stage_success_rates"]["unification"]["total"] == 1
        assert system.metrics["stage_success_rates"]["unification"]["success"] == 1
        assert system.metrics["stage_success_rates"]["detection"]["total"] == 1
        assert system.metrics["stage_success_rates"]["detection"]["success"] == 1
    
    def test_update_metrics_falha(self, system):
        """Teste de atualização de métricas com falha"""
        # Arrange
        processing_stages = [
            ProcessingResult(ProcessingStage.UNIFICATION, False, None, 0.1, [], [])
        ]
        
        # Act
        system._update_metrics(False, 0.3, 0.0, processing_stages)
        
        # Assert
        assert system.metrics["total_processing"] == 1
        assert system.metrics["successful_processing"] == 0
        assert system.metrics["failed_processing"] == 1
        
        # Verificar uso de componentes
        assert system.metrics["component_usage"]["unification"] == 1
        
        # Verificar taxa de sucesso por estágio
        assert system.metrics["stage_success_rates"]["unification"]["total"] == 1
        assert system.metrics["stage_success_rates"]["unification"]["success"] == 0
    
    def test_process_text_complete_function(self, sample_text, expected_gaps):
        """Teste da função de conveniência process_text_complete"""
        # Arrange & Act
        with patch('infrastructure.processamento.complete_lacuna_system_imp007.CompleteLacunaSystem') as mock_system_class:
            mock_system = Mock()
            mock_system.process_text.return_value = Mock(success=True)
            mock_system_class.return_value = mock_system
            
            result = process_text_complete(sample_text, expected_gaps)
        
        # Assert
        mock_system.process_text.assert_called_once_with(sample_text, expected_gaps)
        assert result.success is True
    
    def test_get_complete_system_stats_function(self):
        """Teste da função de conveniência get_complete_system_stats"""
        # Arrange & Act
        with patch('infrastructure.processamento.complete_lacuna_system_imp007.CompleteLacunaSystem') as mock_system_class:
            mock_system = Mock()
            mock_system.metrics = {"test": "data"}
            mock_system_class.return_value = mock_system
            
            stats = get_complete_system_stats()
        
        # Assert
        assert stats == {"test": "data"}
    
    def test_system_component_enum(self):
        """Teste dos valores do enum SystemComponent"""
        # Assert
        assert SystemComponent.HYBRID_DETECTOR.value == "hybrid_detector"
        assert SystemComponent.SEMANTIC_DETECTOR.value == "semantic_detector"
        assert SystemComponent.CONTEXT_VALIDATOR.value == "context_validator"
        assert SystemComponent.SEMANTIC_MATCHER.value == "semantic_matcher"
        assert SystemComponent.QUALITY_VALIDATOR.value == "quality_validator"
        assert SystemComponent.FALLBACK_SYSTEM.value == "fallback_system"
        assert SystemComponent.UNIFICATION_SYSTEM.value == "unification_system"
    
    def test_processing_stage_enum(self):
        """Teste dos valores do enum ProcessingStage"""
        # Assert
        assert ProcessingStage.UNIFICATION.value == "unification"
        assert ProcessingStage.DETECTION.value == "detection"
        assert ProcessingStage.SEMANTIC_ANALYSIS.value == "semantic_analysis"
        assert ProcessingStage.CONTEXT_VALIDATION.value == "context_validation"
        assert ProcessingStage.SEMANTIC_MATCHING.value == "semantic_matching"
        assert ProcessingStage.QUALITY_VALIDATION.value == "quality_validation"
        assert ProcessingStage.FALLBACK_GENERATION.value == "fallback_generation"
        assert ProcessingStage.INTEGRATION.value == "integration"
    
    def test_processing_result_dataclass(self):
        """Teste da estrutura do dataclass ProcessingResult"""
        # Arrange
        result = ProcessingResult(
            stage=ProcessingStage.UNIFICATION,
            success=True,
            data="test data",
            execution_time=0.5,
            errors=[],
            warnings=[],
            metadata={"key": "value"}
        )
        
        # Assert
        assert result.stage == ProcessingStage.UNIFICATION
        assert result.success is True
        assert result.data == "test data"
        assert result.execution_time == 0.5
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata["key"] == "value"
    
    def test_complete_lacuna_result_dataclass(self, mock_detection_result):
        """Teste da estrutura do dataclass CompleteLacunaResult"""
        # Arrange
        result = CompleteLacunaResult(
            hybrid_result=mock_detection_result,
            semantic_result=None,
            context_result=None,
            matching_result=None,
            quality_result=None,
            fallback_results=[],
            unified_text="test text",
            all_gaps=[],
            semantic_gaps=[],
            validated_gaps=[],
            matched_gaps=[],
            fallback_options=[],
            total_processing_time=1.0,
            overall_quality_score=0.8,
            system_health="good",
            success=True,
            processing_stages=[],
            errors=[],
            warnings=[],
            insights={},
            recommendations=[],
            timestamp=datetime.now(),
            metadata={"test": "value"}
        )
        
        # Assert
        assert result.hybrid_result == mock_detection_result
        assert result.unified_text == "test text"
        assert result.total_processing_time == 1.0
        assert result.overall_quality_score == 0.8
        assert result.system_health == "good"
        assert result.success is True
        assert result.metadata["test"] == "value" 