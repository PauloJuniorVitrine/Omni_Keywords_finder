# =============================================================================
# Testes Unitários - Quality Validator IMP005
# =============================================================================
# 
# Testes para o validador de qualidade avançado
# Baseados completamente na implementação real do código
#
# Arquivo: infrastructure/processamento/quality_validator_imp005.py
# Linhas: 758
# Tracing ID: test-quality-validator-imp005-2025-01-27-001
# =============================================================================

import pytest
import time
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from infrastructure.processamento.quality_validator_imp005 import (
    QualityValidator,
    QualityIssue,
    QualityReport,
    QualityMetric,
    QualityLevel,
    validate_system_quality,
    get_quality_validation_stats
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

from infrastructure.processamento.placeholder_unification_system_imp001 import (
    PlaceholderType
)


class TestQualityValidator:
    """Testes para o QualityValidator"""
    
    @pytest.fixture
    def validator(self):
        """Fixture para criar instância do validador"""
        return QualityValidator()
    
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
            placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
            placeholder_name="primary_keyword",
            start_pos=35,
            end_pos=52,
            context="artigo sobre {primary_keyword}",
            confidence=0.9,
            detection_method=DetectionMethod.REGEX,
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
            warnings=[],
            detection_time=0.5
        )
    
    @pytest.fixture
    def mock_semantic_result(self):
        """Fixture para criar resultado semântico mock"""
        return SemanticDetectionResult(
            semantic_gaps=[],
            avg_semantic_confidence=0.8,
            success=True,
            errors=[],
            warnings=[],
            semantic_analysis_time=0.3
        )
    
    @pytest.fixture
    def mock_context_result(self):
        """Fixture para criar resultado de contexto mock"""
        return ContextValidationResult(
            is_valid=True,
            overall_score=0.85,
            coherence_score=0.9,
            consistency_score=0.88,
            errors=[],
            warnings=[],
            validation_time=0.2
        )
    
    @pytest.fixture
    def mock_matching_result(self):
        """Fixture para criar resultado de matching mock"""
        return MatchingResult(
            matches=[],
            avg_match_quality=0.8,
            avg_confidence=0.75,
            strategy_used=MatchingStrategy.SEMANTIC,
            success=True,
            errors=[],
            warnings=[],
            matching_time=0.4
        )
    
    def test_inicializacao_validator(self, validator):
        """Teste de inicialização do validador"""
        # Arrange & Act - Validador já criado no fixture
        
        # Assert - Verificar thresholds de qualidade
        assert QualityMetric.PRECISION in validator.quality_thresholds
        assert QualityMetric.RECALL in validator.quality_thresholds
        assert QualityMetric.F1_SCORE in validator.quality_thresholds
        assert QualityMetric.ACCURACY in validator.quality_thresholds
        assert QualityMetric.PERFORMANCE in validator.quality_thresholds
        assert QualityMetric.EFFICIENCY in validator.quality_thresholds
        assert QualityMetric.RELIABILITY in validator.quality_thresholds
        assert QualityMetric.CONSISTENCY in validator.quality_thresholds
        
        # Verificar pesos de qualidade
        assert QualityMetric.PRECISION in validator.quality_weights
        assert QualityMetric.RECALL in validator.quality_weights
        assert QualityMetric.F1_SCORE in validator.quality_weights
        assert QualityMetric.ACCURACY in validator.quality_weights
        assert QualityMetric.PERFORMANCE in validator.quality_weights
        assert QualityMetric.EFFICIENCY in validator.quality_weights
        assert QualityMetric.RELIABILITY in validator.quality_weights
        assert QualityMetric.CONSISTENCY in validator.quality_weights
        
        # Verificar componentes
        assert validator.hybrid_detector is not None
        assert validator.semantic_detector is not None
        assert validator.context_validator is not None
        assert validator.semantic_matcher is not None
        assert validator.unification_system is not None
        
        # Verificar cache e métricas
        assert validator.validation_cache == {}
        assert validator.cache_ttl == 3600  # 1 hora
        
        # Verificar estrutura das métricas
        assert "total_validations" in validator.metrics
        assert "successful_validations" in validator.metrics
        assert "failed_validations" in validator.metrics
        assert "avg_validation_time" in validator.metrics
        assert "validation_times" in validator.metrics
        assert "quality_scores" in validator.metrics
        assert "issue_distribution" in validator.metrics
        
        assert validator.metrics["total_validations"] == 0
        assert validator.metrics["successful_validations"] == 0
        assert validator.metrics["failed_validations"] == 0
        assert validator.metrics["avg_validation_time"] == 0.0
    
    @patch('infrastructure.processamento.quality_validator_imp005.HybridLacunaDetector')
    @patch('infrastructure.processamento.quality_validator_imp005.SemanticGapDetector')
    @patch('infrastructure.processamento.quality_validator_imp005.ContextValidator')
    @patch('infrastructure.processamento.quality_validator_imp005.SemanticMatcher')
    def test_validate_system_quality_sucesso(self, mock_matcher, mock_context, mock_semantic, mock_hybrid,
                                           validator, sample_text, expected_gaps, mock_detection_result,
                                           mock_semantic_result, mock_context_result, mock_matching_result):
        """Teste de validação de qualidade com sucesso"""
        # Arrange - Configurar mocks
        mock_hybrid.return_value.detect_gaps.return_value = mock_detection_result
        mock_semantic.return_value.detect_semantic_gaps.return_value = mock_semantic_result
        mock_context.return_value.validate_context.return_value = mock_context_result
        mock_matcher.return_value.match_semantically.return_value = mock_matching_result
        
        # Act
        report = validator.validate_system_quality(sample_text, expected_gaps)
        
        # Assert
        assert isinstance(report, QualityReport)
        assert report.overall_score > 0
        assert report.quality_level in QualityLevel
        assert isinstance(report.metrics, dict)
        assert isinstance(report.issues, list)
        assert isinstance(report.recommendations, list)
        assert isinstance(report.performance_metrics, dict)
        assert report.validation_time > 0
        assert isinstance(report.timestamp, datetime)
        assert isinstance(report.metadata, dict)
        
        # Verificar métricas
        assert QualityMetric.PRECISION in report.metrics
        assert QualityMetric.RECALL in report.metrics
        assert QualityMetric.F1_SCORE in report.metrics
        assert QualityMetric.ACCURACY in report.metrics
        assert QualityMetric.PERFORMANCE in report.metrics
        assert QualityMetric.EFFICIENCY in report.metrics
        assert QualityMetric.RELIABILITY in report.metrics
        assert QualityMetric.CONSISTENCY in report.metrics
        
        # Verificar performance metrics
        assert "detection_performance" in report.performance_metrics
        assert "semantic_performance" in report.performance_metrics
        assert "context_performance" in report.performance_metrics
        assert "matching_performance" in report.performance_metrics
        assert "overall_performance" in report.performance_metrics
    
    def test_validate_system_quality_cache_functionality(self, validator, sample_text, expected_gaps):
        """Teste de funcionalidade de cache"""
        # Arrange
        cache_key = f"{hash(sample_text)}:{len(expected_gaps)}"
        
        # Mock para simular sucesso
        with patch.object(validator, '_calculate_quality_metrics') as mock_metrics:
            mock_metrics.return_value = {
                QualityMetric.PRECISION: 0.9,
                QualityMetric.RECALL: 0.8,
                QualityMetric.F1_SCORE: 0.85,
                QualityMetric.ACCURACY: 0.9,
                QualityMetric.PERFORMANCE: 0.8,
                QualityMetric.EFFICIENCY: 0.8,
                QualityMetric.RELIABILITY: 0.95,
                QualityMetric.CONSISTENCY: 0.88
            }
            
            with patch.object(validator, '_detect_quality_issues') as mock_issues:
                mock_issues.return_value = []
                
                with patch.object(validator, '_calculate_overall_quality_score') as mock_score:
                    mock_score.return_value = 0.85
                    
                    with patch.object(validator, '_determine_quality_level') as mock_level:
                        mock_level.return_value = QualityLevel.GOOD
                        
                        with patch.object(validator, '_generate_quality_recommendations') as mock_recs:
                            mock_recs.return_value = ["Recomendação teste"]
                            
                            with patch.object(validator, '_collect_performance_metrics') as mock_perf:
                                mock_perf.return_value = {"test": "data"}
                                
                                # Act - Primeira execução (deve processar)
                                report1 = validator.validate_system_quality(sample_text, expected_gaps)
        
        # Act - Segunda execução (deve vir do cache)
        report2 = validator.validate_system_quality(sample_text, expected_gaps)
        
        # Assert
        assert cache_key in validator.validation_cache
        assert report1 == report2
    
    def test_calculate_precision_recall_completo(self, validator, mock_detected_gap):
        """Teste de cálculo de precisão e recall com dados completos"""
        # Arrange
        detected_gaps = [mock_detected_gap]
        expected_gaps = [
            {"start_pos": 35, "end_pos": 52, "type": "primary_keyword"},
            {"start_pos": 65, "end_pos": 82, "type": "target_audience"}
        ]
        
        # Act
        precision, recall, f1_score, accuracy = validator._calculate_precision_recall(detected_gaps, expected_gaps)
        
        # Assert
        assert isinstance(precision, float)
        assert isinstance(recall, float)
        assert isinstance(f1_score, float)
        assert isinstance(accuracy, float)
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1
        assert 0 <= f1_score <= 1
        assert 0 <= accuracy <= 1
    
    def test_calculate_precision_recall_vazio(self, validator):
        """Teste de cálculo de precisão e recall com dados vazios"""
        # Arrange
        detected_gaps = []
        expected_gaps = []
        
        # Act
        precision, recall, f1_score, accuracy = validator._calculate_precision_recall(detected_gaps, expected_gaps)
        
        # Assert
        assert precision == 1.0
        assert recall == 1.0
        assert f1_score == 1.0
        assert accuracy == 1.0
    
    def test_calculate_precision_recall_sem_detectados(self, validator):
        """Teste de cálculo de precisão e recall sem gaps detectados"""
        # Arrange
        detected_gaps = []
        expected_gaps = [{"start_pos": 35, "end_pos": 52, "type": "primary_keyword"}]
        
        # Act
        precision, recall, f1_score, accuracy = validator._calculate_precision_recall(detected_gaps, expected_gaps)
        
        # Assert
        assert precision == 0.0
        assert recall == 0.0
        assert f1_score == 0.0
        assert accuracy == 0.0
    
    def test_calculate_precision_recall_sem_esperados(self, validator, mock_detected_gap):
        """Teste de cálculo de precisão e recall sem gaps esperados"""
        # Arrange
        detected_gaps = [mock_detected_gap]
        expected_gaps = []
        
        # Act
        precision, recall, f1_score, accuracy = validator._calculate_precision_recall(detected_gaps, expected_gaps)
        
        # Assert
        assert precision == 0.0
        assert recall == 1.0
        assert f1_score == 0.0
        assert accuracy == 0.0
    
    def test_positions_overlap(self, validator):
        """Teste de verificação de sobreposição de posições"""
        # Arrange & Act & Assert
        # Sobreposição completa
        assert validator._positions_overlap((10, 20), (10, 20)) is True
        
        # Sobreposição parcial
        assert validator._positions_overlap((10, 20), (15, 25)) is True
        assert validator._positions_overlap((15, 25), (10, 20)) is True
        
        # Sem sobreposição
        assert validator._positions_overlap((10, 20), (25, 35)) is False
        assert validator._positions_overlap((25, 35), (10, 20)) is False
        
        # Bordas tocando
        assert validator._positions_overlap((10, 20), (20, 30)) is False
        assert validator._positions_overlap((20, 30), (10, 20)) is False
    
    def test_calculate_confidence_based_precision(self, validator, mock_detection_result):
        """Teste de cálculo de precisão baseada em confiança"""
        # Act
        precision = validator._calculate_confidence_based_precision(mock_detection_result)
        
        # Assert
        assert isinstance(precision, float)
        assert 0 <= precision <= 1
        assert precision > 0  # Deve ser maior que 0 com confiança de 0.85
    
    def test_calculate_confidence_based_precision_sem_gaps(self, validator):
        """Teste de cálculo de precisão baseada em confiança sem gaps"""
        # Arrange
        empty_result = DetectionResult(
            gaps=[],
            total_gaps=0,
            confidence_avg=0.0,
            precision_score=0.0,
            method_used=DetectionMethod.HYBRID,
            validation_level=ValidationLevel.BASIC,
            success=True,
            errors=[],
            warnings=[],
            detection_time=0.0
        )
        
        # Act
        precision = validator._calculate_confidence_based_precision(empty_result)
        
        # Assert
        assert precision == 0.0
    
    def test_calculate_confidence_based_recall(self, validator, mock_detection_result):
        """Teste de cálculo de recall baseado em confiança"""
        # Act
        recall = validator._calculate_confidence_based_recall(mock_detection_result)
        
        # Assert
        assert isinstance(recall, float)
        assert 0 <= recall <= 1
        assert recall > 0  # Deve ser maior que 0 com 1 gap detectado
    
    def test_calculate_f1_score(self, validator):
        """Teste de cálculo de F1-score"""
        # Act & Assert
        # Caso normal
        f1 = validator._calculate_f1_score(0.8, 0.7)
        assert isinstance(f1, float)
        assert 0 <= f1 <= 1
        
        # Caso com precisão e recall iguais
        f1_equal = validator._calculate_f1_score(0.5, 0.5)
        assert f1_equal == 0.5
        
        # Caso com precisão e recall zero
        f1_zero = validator._calculate_f1_score(0.0, 0.0)
        assert f1_zero == 0.0
    
    def test_calculate_accuracy(self, validator, mock_detection_result):
        """Teste de cálculo de acurácia"""
        # Act
        accuracy = validator._calculate_accuracy(mock_detection_result)
        
        # Assert
        assert isinstance(accuracy, float)
        assert 0 <= accuracy <= 1
        assert accuracy > 0  # Deve ser maior que 0 com sucesso e confiança alta
    
    def test_calculate_performance_metric(self, validator, mock_detection_result, mock_semantic_result,
                                        mock_context_result, mock_matching_result):
        """Teste de cálculo de métrica de performance"""
        # Act
        performance = validator._calculate_performance_metric(
            mock_detection_result, mock_semantic_result, mock_context_result, mock_matching_result
        )
        
        # Assert
        assert isinstance(performance, float)
        assert 0 <= performance <= 1
        assert performance > 0  # Deve ser maior que 0 com tempos baixos
    
    def test_calculate_efficiency_metric(self, validator, mock_detection_result, mock_semantic_result,
                                       mock_context_result, mock_matching_result):
        """Teste de cálculo de métrica de eficiência"""
        # Act
        efficiency = validator._calculate_efficiency_metric(
            mock_detection_result, mock_semantic_result, mock_context_result, mock_matching_result
        )
        
        # Assert
        assert isinstance(efficiency, float)
        assert 0 <= efficiency <= 1
        assert efficiency > 0  # Deve ser maior que 0 com contexto válido
    
    def test_calculate_reliability_metric(self, validator, mock_detection_result, mock_semantic_result,
                                        mock_context_result, mock_matching_result):
        """Teste de cálculo de métrica de confiabilidade"""
        # Act
        reliability = validator._calculate_reliability_metric(
            mock_detection_result, mock_semantic_result, mock_context_result, mock_matching_result
        )
        
        # Assert
        assert isinstance(reliability, float)
        assert 0 <= reliability <= 1
        assert reliability > 0  # Deve ser maior que 0 com todos os componentes com sucesso
    
    def test_calculate_consistency_metric(self, validator, mock_detection_result, mock_semantic_result,
                                        mock_context_result, mock_matching_result):
        """Teste de cálculo de métrica de consistência"""
        # Act
        consistency = validator._calculate_consistency_metric(
            mock_detection_result, mock_semantic_result, mock_context_result, mock_matching_result
        )
        
        # Assert
        assert isinstance(consistency, float)
        assert 0 <= consistency <= 1
        assert consistency > 0  # Deve ser maior que 0 com scores de consistência positivos
    
    def test_detect_quality_issues(self, validator):
        """Teste de detecção de problemas de qualidade"""
        # Arrange
        metrics = {
            QualityMetric.PRECISION: 0.7,  # Abaixo do threshold de 0.85
            QualityMetric.RECALL: 0.9,     # Acima do threshold de 0.80
            QualityMetric.F1_SCORE: 0.75,  # Abaixo do threshold de 0.82
            QualityMetric.ACCURACY: 0.95,  # Acima do threshold de 0.90
            QualityMetric.PERFORMANCE: 0.8, # Acima do threshold de 0.75
            QualityMetric.EFFICIENCY: 0.7,  # Abaixo do threshold de 0.80
            QualityMetric.RELIABILITY: 0.98, # Acima do threshold de 0.95
            QualityMetric.CONSISTENCY: 0.85  # Abaixo do threshold de 0.88
        }
        
        # Act
        issues = validator._detect_quality_issues(metrics)
        
        # Assert
        assert isinstance(issues, list)
        assert len(issues) == 4  # 4 métricas abaixo do threshold
        
        for issue in issues:
            assert isinstance(issue, QualityIssue)
            assert issue.metric in QualityMetric
            assert issue.level in QualityLevel
            assert isinstance(issue.description, str)
            assert isinstance(issue.severity, str)
            assert isinstance(issue.impact, str)
            assert isinstance(issue.recommendation, str)
            assert isinstance(issue.current_value, float)
            assert isinstance(issue.target_value, float)
            assert isinstance(issue.metadata, dict)
    
    def test_determine_issue_level(self, validator):
        """Teste de determinação do nível de problema"""
        # Act & Assert
        assert validator._determine_issue_level(0.95, 1.0) == QualityLevel.EXCELLENT
        assert validator._determine_issue_level(0.85, 1.0) == QualityLevel.GOOD
        assert validator._determine_issue_level(0.70, 1.0) == QualityLevel.FAIR
        assert validator._determine_issue_level(0.50, 1.0) == QualityLevel.POOR
        assert validator._determine_issue_level(0.30, 1.0) == QualityLevel.UNACCEPTABLE
    
    def test_determine_issue_severity(self, validator):
        """Teste de determinação da severidade de problema"""
        # Act & Assert
        assert validator._determine_issue_severity(QualityLevel.EXCELLENT) == "baixa"
        assert validator._determine_issue_severity(QualityLevel.GOOD) == "baixa"
        assert validator._determine_issue_severity(QualityLevel.FAIR) == "média"
        assert validator._determine_issue_severity(QualityLevel.POOR) == "alta"
        assert validator._determine_issue_severity(QualityLevel.UNACCEPTABLE) == "crítica"
    
    def test_determine_issue_impact(self, validator):
        """Teste de determinação do impacto de problema"""
        # Act & Assert
        precision_impact = validator._determine_issue_impact(QualityMetric.PRECISION)
        recall_impact = validator._determine_issue_impact(QualityMetric.RECALL)
        f1_impact = validator._determine_issue_impact(QualityMetric.F1_SCORE)
        
        assert isinstance(precision_impact, str)
        assert isinstance(recall_impact, str)
        assert isinstance(f1_impact, str)
        assert "Falsos positivos" in precision_impact
        assert "Lacunas não detectadas" in recall_impact
        assert "Equilíbrio geral" in f1_impact
    
    def test_generate_issue_recommendation(self, validator):
        """Teste de geração de recomendação para problema"""
        # Act
        rec_critical = validator._generate_issue_recommendation(QualityMetric.PRECISION, 0.3, 0.85)
        rec_important = validator._generate_issue_recommendation(QualityMetric.RECALL, 0.6, 0.80)
        rec_mild = validator._generate_issue_recommendation(QualityMetric.F1_SCORE, 0.8, 0.82)
        
        # Assert
        assert isinstance(rec_critical, str)
        assert isinstance(rec_important, str)
        assert isinstance(rec_mild, str)
        assert "CRÍTICO:" in rec_critical
        assert "IMPORTANTE:" in rec_important
        assert "SUAVE:" in rec_mild
    
    def test_calculate_overall_quality_score(self, validator):
        """Teste de cálculo do score geral de qualidade"""
        # Arrange
        metrics = {
            QualityMetric.PRECISION: 0.9,
            QualityMetric.RECALL: 0.8,
            QualityMetric.F1_SCORE: 0.85,
            QualityMetric.ACCURACY: 0.95,
            QualityMetric.PERFORMANCE: 0.8,
            QualityMetric.EFFICIENCY: 0.8,
            QualityMetric.RELIABILITY: 0.98,
            QualityMetric.CONSISTENCY: 0.88
        }
        
        # Act
        overall_score = validator._calculate_overall_quality_score(metrics)
        
        # Assert
        assert isinstance(overall_score, float)
        assert 0 <= overall_score <= 1
        assert overall_score > 0
    
    def test_calculate_overall_quality_score_vazio(self, validator):
        """Teste de cálculo do score geral com métricas vazias"""
        # Act
        overall_score = validator._calculate_overall_quality_score({})
        
        # Assert
        assert overall_score == 0.0
    
    def test_determine_quality_level(self, validator):
        """Teste de determinação do nível de qualidade"""
        # Act & Assert
        assert validator._determine_quality_level(0.95) == QualityLevel.EXCELLENT
        assert validator._determine_quality_level(0.85) == QualityLevel.GOOD
        assert validator._determine_quality_level(0.75) == QualityLevel.FAIR
        assert validator._determine_quality_level(0.55) == QualityLevel.POOR
        assert validator._determine_quality_level(0.35) == QualityLevel.UNACCEPTABLE
    
    def test_generate_quality_recommendations(self, validator):
        """Teste de geração de recomendações de qualidade"""
        # Arrange
        issues = [
            QualityIssue(
                metric=QualityMetric.PRECISION,
                level=QualityLevel.UNACCEPTABLE,
                description="Teste",
                severity="crítica",
                impact="Teste",
                recommendation="Teste",
                current_value=0.3,
                target_value=0.85
            )
        ]
        
        metrics = {
            QualityMetric.PRECISION: 0.3,
            QualityMetric.RECALL: 0.9
        }
        
        # Act
        recommendations = validator._generate_quality_recommendations(issues, metrics)
        
        # Assert
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0
    
    def test_collect_performance_metrics(self, validator, mock_detection_result, mock_semantic_result,
                                       mock_context_result, mock_matching_result):
        """Teste de coleta de métricas de performance"""
        # Act
        performance_metrics = validator._collect_performance_metrics(
            mock_detection_result, mock_semantic_result, mock_context_result, mock_matching_result
        )
        
        # Assert
        assert isinstance(performance_metrics, dict)
        assert "detection_performance" in performance_metrics
        assert "semantic_performance" in performance_metrics
        assert "context_performance" in performance_metrics
        assert "matching_performance" in performance_metrics
        assert "overall_performance" in performance_metrics
        
        # Verificar estrutura das métricas de detecção
        detection_perf = performance_metrics["detection_performance"]
        assert "total_gaps" in detection_perf
        assert "detection_time" in detection_perf
        assert "avg_confidence" in detection_perf
        assert "success" in detection_perf
    
    def test_update_metrics_sucesso(self, validator):
        """Teste de atualização de métricas com sucesso"""
        # Arrange
        issues = [
            QualityIssue(
                metric=QualityMetric.PRECISION,
                level=QualityLevel.GOOD,
                description="Teste",
                severity="baixa",
                impact="Teste",
                recommendation="Teste",
                current_value=0.8,
                target_value=0.85
            )
        ]
        
        # Act
        validator._update_metrics(True, 0.5, 0.85, issues)
        
        # Assert
        assert validator.metrics["total_validations"] == 1
        assert validator.metrics["successful_validations"] == 1
        assert validator.metrics["failed_validations"] == 0
        assert validator.metrics["avg_validation_time"] == 0.5
        assert len(validator.metrics["validation_times"]) == 1
        assert len(validator.metrics["quality_scores"]) == 1
        assert validator.metrics["issue_distribution"]["precision"] == 1
    
    def test_update_metrics_falha(self, validator):
        """Teste de atualização de métricas com falha"""
        # Act
        validator._update_metrics(False, 0.3, 0.0, [])
        
        # Assert
        assert validator.metrics["total_validations"] == 1
        assert validator.metrics["successful_validations"] == 0
        assert validator.metrics["failed_validations"] == 1
    
    def test_quality_metric_enum(self):
        """Teste dos valores do enum QualityMetric"""
        # Assert
        assert QualityMetric.PRECISION.value == "precision"
        assert QualityMetric.RECALL.value == "recall"
        assert QualityMetric.F1_SCORE.value == "f1_score"
        assert QualityMetric.ACCURACY.value == "accuracy"
        assert QualityMetric.PERFORMANCE.value == "performance"
        assert QualityMetric.EFFICIENCY.value == "efficiency"
        assert QualityMetric.RELIABILITY.value == "reliability"
        assert QualityMetric.CONSISTENCY.value == "consistency"
    
    def test_quality_level_enum(self):
        """Teste dos valores do enum QualityLevel"""
        # Assert
        assert QualityLevel.EXCELLENT.value == "excellent"
        assert QualityLevel.GOOD.value == "good"
        assert QualityLevel.FAIR.value == "fair"
        assert QualityLevel.POOR.value == "poor"
        assert QualityLevel.UNACCEPTABLE.value == "unacceptable"
    
    def test_quality_issue_dataclass(self):
        """Teste da estrutura do dataclass QualityIssue"""
        # Arrange
        issue = QualityIssue(
            metric=QualityMetric.PRECISION,
            level=QualityLevel.GOOD,
            description="Teste de problema",
            severity="baixa",
            impact="Impacto teste",
            recommendation="Recomendação teste",
            current_value=0.8,
            target_value=0.85,
            metadata={"key": "value"}
        )
        
        # Assert
        assert issue.metric == QualityMetric.PRECISION
        assert issue.level == QualityLevel.GOOD
        assert issue.description == "Teste de problema"
        assert issue.severity == "baixa"
        assert issue.impact == "Impacto teste"
        assert issue.recommendation == "Recomendação teste"
        assert issue.current_value == 0.8
        assert issue.target_value == 0.85
        assert issue.metadata["key"] == "value"
    
    def test_quality_report_dataclass(self):
        """Teste da estrutura do dataclass QualityReport"""
        # Arrange
        report = QualityReport(
            overall_score=0.85,
            quality_level=QualityLevel.GOOD,
            metrics={QualityMetric.PRECISION: 0.9},
            issues=[],
            recommendations=["Recomendação teste"],
            performance_metrics={"test": "data"},
            validation_time=0.5,
            timestamp=datetime.now(),
            metadata={"key": "value"}
        )
        
        # Assert
        assert report.overall_score == 0.85
        assert report.quality_level == QualityLevel.GOOD
        assert len(report.metrics) == 1
        assert report.metrics[QualityMetric.PRECISION] == 0.9
        assert report.issues == []
        assert report.recommendations == ["Recomendação teste"]
        assert report.performance_metrics["test"] == "data"
        assert report.validation_time == 0.5
        assert isinstance(report.timestamp, datetime)
        assert report.metadata["key"] == "value"
    
    def test_validate_system_quality_function(self, sample_text, expected_gaps):
        """Teste da função de conveniência validate_system_quality"""
        # Act
        with patch('infrastructure.processamento.quality_validator_imp005.QualityValidator') as mock_validator_class:
            mock_validator = Mock()
            mock_validator.validate_system_quality.return_value = Mock(overall_score=0.85)
            mock_validator_class.return_value = mock_validator
            
            report = validate_system_quality(sample_text, expected_gaps)
        
        # Assert
        mock_validator.validate_system_quality.assert_called_once_with(sample_text, expected_gaps)
        assert report.overall_score == 0.85
    
    def test_get_quality_validation_stats_function(self):
        """Teste da função de conveniência get_quality_validation_stats"""
        # Act
        with patch('infrastructure.processamento.quality_validator_imp005.QualityValidator') as mock_validator_class:
            mock_validator = Mock()
            mock_validator.metrics = {"test": "data"}
            mock_validator_class.return_value = mock_validator
            
            stats = get_quality_validation_stats()
        
        # Assert
        assert stats == {"test": "data"}
    
    def test_validate_system_quality_erro(self, validator, sample_text):
        """Teste de validação de qualidade com erro"""
        # Arrange - Mock para simular erro
        with patch.object(validator, 'hybrid_detector') as mock_detector:
            mock_detector.detect_gaps.side_effect = Exception("Erro de teste")
            
            # Act
            report = validator.validate_system_quality(sample_text)
            
            # Assert
            assert isinstance(report, QualityReport)
            assert report.overall_score == 0.0
            assert report.quality_level == QualityLevel.UNACCEPTABLE
            assert len(report.issues) == 0
            assert len(report.recommendations) == 1
            assert "Erro na validação" in report.recommendations[0]
            assert report.metadata["error"] == "Erro de teste" 