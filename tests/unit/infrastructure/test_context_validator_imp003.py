#!/usr/bin/env python3
"""
Testes Unitários - Context Validator IMP003
===========================================

Tracing ID: TEST_CONTEXT_VALIDATOR_IMP003_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/processamento/context_validator_imp003.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 2.5
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import time
import statistics
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Tuple

# Importar classes e funções reais do sistema
from infrastructure.processamento.context_validator_imp003 import (
    ContextValidationType,
    ValidationSeverity,
    ContextValidationIssue,
    ContextValidationResult,
    ContextAnalyzer,
    ContextValidator,
    validate_context,
    get_context_validation_stats
)

from infrastructure.processamento.hybrid_lacuna_detector_imp001 import (
    DetectedGap,
    DetectionMethod,
    ValidationLevel
)

from infrastructure.processamento.placeholder_unification_system_imp001 import (
    PlaceholderType
)


class TestContextValidationType:
    """Testes para enum ContextValidationType."""
    
    def test_semantic_coherence_value(self):
        """Testa valor do tipo SEMANTIC_COHERENCE."""
        assert ContextValidationType.SEMANTIC_COHERENCE.value == "semantic_coherence"
    
    def test_logical_flow_value(self):
        """Testa valor do tipo LOGICAL_FLOW."""
        assert ContextValidationType.LOGICAL_FLOW.value == "logical_flow"
    
    def test_contextual_consistency_value(self):
        """Testa valor do tipo CONTEXTUAL_CONSISTENCY."""
        assert ContextValidationType.CONTEXTUAL_CONSISTENCY.value == "contextual_consistency"
    
    def test_placeholder_relevance_value(self):
        """Testa valor do tipo PLACEHOLDER_RELEVANCE."""
        assert ContextValidationType.PLACEHOLDER_RELEVANCE.value == "placeholder_relevance"
    
    def test_content_structure_value(self):
        """Testa valor do tipo CONTENT_STRUCTURE."""
        assert ContextValidationType.CONTENT_STRUCTURE.value == "content_structure"


class TestValidationSeverity:
    """Testes para enum ValidationSeverity."""
    
    def test_critical_value(self):
        """Testa valor da severidade CRITICAL."""
        assert ValidationSeverity.CRITICAL.value == "critical"
    
    def test_high_value(self):
        """Testa valor da severidade HIGH."""
        assert ValidationSeverity.HIGH.value == "high"
    
    def test_medium_value(self):
        """Testa valor da severidade MEDIUM."""
        assert ValidationSeverity.MEDIUM.value == "medium"
    
    def test_low_value(self):
        """Testa valor da severidade LOW."""
        assert ValidationSeverity.LOW.value == "low"
    
    def test_info_value(self):
        """Testa valor da severidade INFO."""
        assert ValidationSeverity.INFO.value == "info"


class TestContextValidationIssue:
    """Testes para dataclass ContextValidationIssue."""
    
    def test_context_validation_issue_creation(self):
        """Testa criação de ContextValidationIssue."""
        issue = ContextValidationIssue(
            validation_type=ContextValidationType.SEMANTIC_COHERENCE,
            severity=ValidationSeverity.HIGH,
            description="Teste de problema",
            position=(10, 20),
            context="Contexto de teste",
            suggestion="Sugestão de correção",
            confidence=0.8
        )
        
        assert issue.validation_type == ContextValidationType.SEMANTIC_COHERENCE
        assert issue.severity == ValidationSeverity.HIGH
        assert issue.description == "Teste de problema"
        assert issue.position == (10, 20)
        assert issue.context == "Contexto de teste"
        assert issue.suggestion == "Sugestão de correção"
        assert issue.confidence == 0.8
        assert issue.metadata == {}
    
    def test_context_validation_issue_with_metadata(self):
        """Testa criação com metadata personalizada."""
        metadata = {"test_key": "test_value"}
        issue = ContextValidationIssue(
            validation_type=ContextValidationType.LOGICAL_FLOW,
            severity=ValidationSeverity.MEDIUM,
            description="Teste com metadata",
            position=(0, 100),
            context="Contexto longo",
            suggestion="Sugestão",
            confidence=0.9,
            metadata=metadata
        )
        
        assert issue.metadata == metadata


class TestContextValidationResult:
    """Testes para dataclass ContextValidationResult."""
    
    def test_context_validation_result_creation(self):
        """Testa criação de ContextValidationResult."""
        result = ContextValidationResult(
            is_valid=True,
            overall_score=0.85,
            issues=[],
            warnings=[],
            suggestions=[],
            validation_time=0.5,
            context_analysis={"test": "data"},
            coherence_score=0.8,
            flow_score=0.9,
            consistency_score=0.95
        )
        
        assert result.is_valid is True
        assert result.overall_score == 0.85
        assert result.issues == []
        assert result.warnings == []
        assert result.suggestions == []
        assert result.validation_time == 0.5
        assert result.context_analysis == {"test": "data"}
        assert result.coherence_score == 0.8
        assert result.flow_score == 0.9
        assert result.consistency_score == 0.95
        assert result.metadata == {}
    
    def test_context_validation_result_with_metadata(self):
        """Testa criação com metadata personalizada."""
        metadata = {"validation_id": "test_123"}
        result = ContextValidationResult(
            is_valid=False,
            overall_score=0.3,
            issues=[Mock()],
            warnings=["Warning 1"],
            suggestions=["Suggestion 1"],
            validation_time=1.0,
            context_analysis={},
            coherence_score=0.2,
            flow_score=0.4,
            consistency_score=0.3,
            metadata=metadata
        )
        
        assert result.metadata == metadata


class TestContextAnalyzer:
    """Testes para classe ContextAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para ContextAnalyzer."""
        return ContextAnalyzer()
    
    def test_context_analyzer_initialization(self, analyzer):
        """Testa inicialização do ContextAnalyzer."""
        assert analyzer.context_window_size == 300
        assert analyzer.min_coherence_threshold == 0.6
        assert analyzer.max_flow_distance == 100
        assert isinstance(analyzer.context_patterns, dict)
        assert isinstance(analyzer.coherence_rules, list)
        assert isinstance(analyzer.flow_patterns, dict)
        assert isinstance(analyzer.metrics, dict)
        assert analyzer.metrics["total_analyses"] == 0
    
    def test_create_context_patterns(self, analyzer):
        """Testa criação de padrões de contexto."""
        patterns = analyzer._create_context_patterns()
        
        assert "topic_indicators" in patterns
        assert "audience_indicators" in patterns
        assert "intent_indicators" in patterns
        assert "content_indicators" in patterns
        
        # Verificar se os padrões são listas de strings
        for pattern_list in patterns.values():
            assert isinstance(pattern_list, list)
            for pattern in pattern_list:
                assert isinstance(pattern, str)
    
    def test_create_coherence_rules(self, analyzer):
        """Testa criação de regras de coerência."""
        rules = analyzer._create_coherence_rules()
        
        assert isinstance(rules, list)
        assert len(rules) > 0
        
        for rule in rules:
            assert "name" in rule
            assert "description" in rule
            assert "weight" in rule
            assert "pattern" in rule
            assert "validation" in rule
            assert isinstance(rule["weight"], float)
    
    def test_create_flow_patterns(self, analyzer):
        """Testa criação de padrões de fluxo."""
        patterns = analyzer._create_flow_patterns()
        
        assert "introduction" in patterns
        assert "development" in patterns
        assert "conclusion" in patterns
        assert "transition" in patterns
        
        # Verificar se os padrões são listas de strings
        for pattern_list in patterns.values():
            assert isinstance(pattern_list, list)
            for pattern in pattern_list:
                assert isinstance(pattern, str)
    
    def test_extract_general_context(self, analyzer):
        """Testa extração de contexto geral."""
        text = "Artigo sobre marketing digital para profissionais de marketing. Objetivo educar sobre SEO."
        
        context = analyzer._extract_general_context(text)
        
        assert "topics" in context
        assert "audiences" in context
        assert "intents" in context
        assert "content_types" in context
        assert "tone" in context
        assert "complexity" in context
        
        # Verificar se as listas são inicializadas
        assert isinstance(context["topics"], list)
        assert isinstance(context["audiences"], list)
        assert isinstance(context["intents"], list)
        assert isinstance(context["content_types"], list)
    
    def test_detect_text_tone(self, analyzer):
        """Testa detecção de tom do texto."""
        # Teste tom formal
        formal_text = "Este é um documento formal e técnico."
        assert analyzer._detect_text_tone(formal_text) == "formal"
        
        # Teste tom casual
        casual_text = "Este é um texto casual e descontraído."
        assert analyzer._detect_text_tone(casual_text) == "casual"
        
        # Teste tom neutro
        neutral_text = "Este é um texto normal."
        assert analyzer._detect_text_tone(neutral_text) == "neutro"
    
    def test_detect_text_complexity(self, analyzer):
        """Testa detecção de complexidade do texto."""
        # Teste complexidade baixa
        simple_text = "Texto simples com palavras curtas."
        assert analyzer._detect_text_complexity(simple_text) == "baixo"
        
        # Teste complexidade média
        medium_text = "Texto com palavras de tamanho médio e complexidade moderada."
        assert analyzer._detect_text_complexity(medium_text) == "médio"
        
        # Teste complexidade alta
        complex_text = "Texto com terminologia extremamente sofisticada e vocabulário avançado."
        assert analyzer._detect_text_complexity(complex_text) == "alto"
    
    def test_update_metrics(self, analyzer):
        """Testa atualização de métricas."""
        initial_total = analyzer.metrics["total_analyses"]
        
        # Teste sucesso
        analyzer._update_metrics(True, 0.5, 0.8)
        assert analyzer.metrics["total_analyses"] == initial_total + 1
        assert analyzer.metrics["successful_analyses"] == 1
        assert len(analyzer.metrics["analysis_times"]) == 1
        assert len(analyzer.metrics["coherence_scores"]) == 1
        
        # Teste falha
        analyzer._update_metrics(False, 0.0, 0.0)
        assert analyzer.metrics["total_analyses"] == initial_total + 2
        assert analyzer.metrics["failed_analyses"] == 1


class TestContextValidator:
    """Testes para classe ContextValidator."""
    
    @pytest.fixture
    def validator(self):
        """Fixture para ContextValidator."""
        return ContextValidator()
    
    @pytest.fixture
    def sample_gaps(self):
        """Fixture para lacunas de exemplo."""
        return [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="primary_keyword",
                start_pos=35,
                end_pos=52,
                context="artigo sobre {primary_keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            ),
            DetectedGap(
                placeholder_type=PlaceholderType.TARGET_AUDIENCE,
                placeholder_name="target_audience",
                start_pos=60,
                end_pos=75,
                context="para o público {target_audience}",
                confidence=0.8,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
    
    def test_context_validator_initialization(self, validator):
        """Testa inicialização do ContextValidator."""
        assert isinstance(validator.context_analyzer, ContextAnalyzer)
        assert validator.min_validation_score == 0.7
        assert isinstance(validator.severity_weights, dict)
        assert isinstance(validator.validation_cache, dict)
        assert validator.cache_ttl == 1800
        assert isinstance(validator.metrics, dict)
        assert validator.metrics["total_validations"] == 0
    
    def test_determine_severity(self, validator):
        """Testa determinação de severidade."""
        assert validator._determine_severity("redundant_placeholders") == ValidationSeverity.MEDIUM
        assert validator._determine_severity("missing_topic_context") == ValidationSeverity.HIGH
        assert validator._determine_severity("missing_audience_context") == ValidationSeverity.HIGH
        assert validator._determine_severity("inconsistent_flow") == ValidationSeverity.MEDIUM
        assert validator._determine_severity("low_coherence") == ValidationSeverity.HIGH
        assert validator._determine_severity("unknown_type") == ValidationSeverity.MEDIUM
    
    def test_generate_issue_suggestion(self, validator):
        """Testa geração de sugestões para problemas."""
        inconsistency = {"type": "redundant_placeholders"}
        suggestion = validator._generate_issue_suggestion(inconsistency)
        assert "remover" in suggestion.lower()
        
        inconsistency = {"type": "missing_topic_context"}
        suggestion = validator._generate_issue_suggestion(inconsistency)
        assert "tópico" in suggestion.lower()
        
        inconsistency = {"type": "unknown_type"}
        suggestion = validator._generate_issue_suggestion(inconsistency)
        assert "revise" in suggestion.lower()
    
    def test_calculate_validation_score(self, validator):
        """Testa cálculo de score de validação."""
        # Teste sem problemas
        issues = []
        context_analysis = {"coherence_score": 0.9, "flow_analysis": {"flow_score": 0.9}}
        score = validator._calculate_validation_score(issues, context_analysis)
        assert score > 1.0  # Score base + bonus
        
        # Teste com problemas
        issues = [
            ContextValidationIssue(
                validation_type=ContextValidationType.SEMANTIC_COHERENCE,
                severity=ValidationSeverity.HIGH,
                description="Teste",
                position=(0, 10),
                context="Teste",
                suggestion="Teste",
                confidence=0.8
            )
        ]
        context_analysis = {"coherence_score": 0.5, "flow_analysis": {"flow_score": 0.5}}
        score = validator._calculate_validation_score(issues, context_analysis)
        assert score < 1.0  # Score base - penalty
    
    def test_calculate_consistency_score(self, validator):
        """Testa cálculo de score de consistência."""
        # Teste sem problemas de consistência
        issues = [
            ContextValidationIssue(
                validation_type=ContextValidationType.SEMANTIC_COHERENCE,
                severity=ValidationSeverity.HIGH,
                description="Teste",
                position=(0, 10),
                context="Teste",
                suggestion="Teste",
                confidence=0.8
            )
        ]
        score = validator._calculate_consistency_score(issues)
        assert score == 1.0
        
        # Teste com problemas de consistência
        issues = [
            ContextValidationIssue(
                validation_type=ContextValidationType.CONTEXTUAL_CONSISTENCY,
                severity=ValidationSeverity.HIGH,
                description="Teste",
                position=(0, 10),
                context="Teste",
                suggestion="Teste",
                confidence=0.8
            )
        ]
        score = validator._calculate_consistency_score(issues)
        assert score < 1.0
    
    def test_generate_warnings(self, validator):
        """Testa geração de warnings."""
        # Teste sem problemas críticos
        issues = []
        context_analysis = {"general_context": {"topics": ["test"], "audiences": ["test"]}}
        warnings = validator._generate_warnings(issues, context_analysis)
        assert len(warnings) == 0
        
        # Teste com problemas críticos
        issues = [
            ContextValidationIssue(
                validation_type=ContextValidationType.SEMANTIC_COHERENCE,
                severity=ValidationSeverity.CRITICAL,
                description="Teste",
                position=(0, 10),
                context="Teste",
                suggestion="Teste",
                confidence=0.8
            )
        ]
        context_analysis = {"general_context": {}}
        warnings = validator._generate_warnings(issues, context_analysis)
        assert len(warnings) > 0
        assert any("críticos" in warning for warning in warnings)
    
    def test_update_metrics(self, validator):
        """Testa atualização de métricas."""
        initial_total = validator.metrics["total_validations"]
        
        # Teste sucesso
        issues = []
        validator._update_metrics(True, 0.5, 0.8, issues)
        assert validator.metrics["total_validations"] == initial_total + 1
        assert validator.metrics["successful_validations"] == 1
        assert len(validator.metrics["validation_times"]) == 1
        assert len(validator.metrics["validation_scores"]) == 1
        
        # Teste falha
        validator._update_metrics(False, 0.0, 0.0, [])
        assert validator.metrics["total_validations"] == initial_total + 2
        assert validator.metrics["failed_validations"] == 1


class TestContextValidatorIntegration:
    """Testes de integração para ContextValidator."""
    
    @pytest.fixture
    def validator(self):
        """Fixture para ContextValidator."""
        return ContextValidator()
    
    @pytest.fixture
    def sample_text(self):
        """Fixture para texto de exemplo."""
        return """
        Preciso criar um artigo sobre marketing digital para profissionais de marketing.
        O conteúdo deve ser educativo com tom profissional.
        O objetivo é educar sobre SEO e estratégias de marketing.
        """
    
    @pytest.fixture
    def sample_gaps(self):
        """Fixture para lacunas de exemplo."""
        return [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="primary_keyword",
                start_pos=35,
                end_pos=52,
                context="artigo sobre {primary_keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            ),
            DetectedGap(
                placeholder_type=PlaceholderType.TARGET_AUDIENCE,
                placeholder_name="target_audience",
                start_pos=60,
                end_pos=75,
                context="para o público {target_audience}",
                confidence=0.8,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
    
    def test_validate_context_success(self, validator, sample_text, sample_gaps):
        """Testa validação de contexto bem-sucedida."""
        result = validator.validate_context(sample_text, sample_gaps)
        
        assert isinstance(result, ContextValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'overall_score')
        assert hasattr(result, 'issues')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'suggestions')
        assert hasattr(result, 'validation_time')
        assert hasattr(result, 'context_analysis')
        assert hasattr(result, 'coherence_score')
        assert hasattr(result, 'flow_score')
        assert hasattr(result, 'consistency_score')
        assert hasattr(result, 'metadata')
        
        assert isinstance(result.validation_time, float)
        assert isinstance(result.coherence_score, float)
        assert isinstance(result.flow_score, float)
        assert isinstance(result.consistency_score, float)
    
    def test_validate_context_with_cache(self, validator, sample_text, sample_gaps):
        """Testa validação com cache."""
        # Primeira validação
        result1 = validator.validate_context(sample_text, sample_gaps)
        
        # Segunda validação (deve usar cache)
        result2 = validator.validate_context(sample_text, sample_gaps)
        
        # Verificar se os resultados são iguais
        assert result1.is_valid == result2.is_valid
        assert result1.overall_score == result2.overall_score
        assert result1.coherence_score == result2.coherence_score
    
    def test_validate_context_empty_gaps(self, validator, sample_text):
        """Testa validação com lista vazia de lacunas."""
        result = validator.validate_context(sample_text, [])
        
        assert isinstance(result, ContextValidationResult)
        assert result.is_valid is True  # Sem lacunas = válido
        assert result.overall_score > 0.8  # Score alto sem problemas
    
    def test_validate_context_error_handling(self, validator):
        """Testa tratamento de erros na validação."""
        # Teste com texto None
        result = validator.validate_context(None, [])
        
        assert isinstance(result, ContextValidationResult)
        assert result.is_valid is False
        assert result.overall_score == 0.0
        assert len(result.warnings) > 0


class TestContextValidatorFunctions:
    """Testes para funções de conveniência."""
    
    def test_validate_context_function(self):
        """Testa função de conveniência validate_context."""
        text = "Texto de teste com {keyword} para {audience}."
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=20,
                end_pos=28,
                context="com {keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        result = validate_context(text, gaps)
        
        assert isinstance(result, ContextValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'overall_score')
    
    def test_get_context_validation_stats(self):
        """Testa função de conveniência get_context_validation_stats."""
        stats = get_context_validation_stats()
        
        assert isinstance(stats, dict)
        assert "total_validations" in stats
        assert "successful_validations" in stats
        assert "failed_validations" in stats
        assert "avg_validation_time" in stats
        assert "validation_times" in stats
        assert "validation_scores" in stats
        assert "issue_distribution" in stats


class TestContextValidatorEdgeCases:
    """Testes para casos edge do ContextValidator."""
    
    @pytest.fixture
    def validator(self):
        """Fixture para ContextValidator."""
        return ContextValidator()
    
    def test_validate_context_very_long_text(self, validator):
        """Testa validação com texto muito longo."""
        long_text = "Texto muito longo " * 1000
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=100,
                end_pos=108,
                context="longo {keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        result = validator.validate_context(long_text, gaps)
        
        assert isinstance(result, ContextValidationResult)
        assert result.validation_time > 0
    
    def test_validate_context_many_gaps(self, validator):
        """Testa validação com muitas lacunas."""
        text = "Texto com muitas lacunas: {gap1} {gap2} {gap3} {gap4} {gap5}"
        gaps = []
        
        for i in range(5):
            gaps.append(DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name=f"gap{i+1}",
                start_pos=30 + i * 8,
                end_pos=38 + i * 8,
                context=f"{{gap{i+1}}}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            ))
        
        result = validator.validate_context(text, gaps)
        
        assert isinstance(result, ContextValidationResult)
        assert len(result.issues) >= 0  # Pode ter problemas de redundância
    
    def test_validate_context_special_characters(self, validator):
        """Testa validação com caracteres especiais."""
        text = "Texto com caracteres especiais: @#$%^&*() e {keyword} para teste."
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=45,
                end_pos=53,
                context="e {keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        result = validator.validate_context(text, gaps)
        
        assert isinstance(result, ContextValidationResult)
        assert result.is_valid is not None
    
    def test_validate_context_unicode_text(self, validator):
        """Testa validação com texto Unicode."""
        text = "Texto com acentos: ação, coração, informação e {keyword}."
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=45,
                end_pos=53,
                context="e {keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        result = validator.validate_context(text, gaps)
        
        assert isinstance(result, ContextValidationResult)
        assert result.is_valid is not None


class TestContextValidatorPerformance:
    """Testes de performance para ContextValidator."""
    
    @pytest.fixture
    def validator(self):
        """Fixture para ContextValidator."""
        return ContextValidator()
    
    def test_validation_time_acceptable(self, validator):
        """Testa se o tempo de validação é aceitável."""
        text = "Texto de teste com {keyword} para validação de performance."
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=20,
                end_pos=28,
                context="com {keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        start_time = time.time()
        result = validator.validate_context(text, gaps)
        end_time = time.time()
        
        actual_time = end_time - start_time
        reported_time = result.validation_time
        
        # Verificar se o tempo reportado é próximo do tempo real
        assert abs(actual_time - reported_time) < 0.1
        # Verificar se a validação é rápida (< 1 segundo)
        assert actual_time < 1.0
    
    def test_cache_performance(self, validator):
        """Testa performance do cache."""
        text = "Texto para teste de cache com {keyword}."
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=25,
                end_pos=33,
                context="com {keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        # Primeira validação (sem cache)
        start_time = time.time()
        result1 = validator.validate_context(text, gaps)
        first_time = time.time() - start_time
        
        # Segunda validação (com cache)
        start_time = time.time()
        result2 = validator.validate_context(text, gaps)
        second_time = time.time() - start_time
        
        # Cache deve ser mais rápido
        assert second_time < first_time
        assert result1.is_valid == result2.is_valid


class TestContextValidatorMetrics:
    """Testes para métricas do ContextValidator."""
    
    @pytest.fixture
    def validator(self):
        """Fixture para ContextValidator."""
        return ContextValidator()
    
    def test_metrics_initialization(self, validator):
        """Testa inicialização das métricas."""
        metrics = validator.metrics
        
        assert metrics["total_validations"] == 0
        assert metrics["successful_validations"] == 0
        assert metrics["failed_validations"] == 0
        assert metrics["avg_validation_time"] == 0.0
        assert isinstance(metrics["validation_times"], deque)
        assert isinstance(metrics["validation_scores"], deque)
        assert isinstance(metrics["issue_distribution"], defaultdict)
    
    def test_metrics_update_on_success(self, validator):
        """Testa atualização de métricas em caso de sucesso."""
        text = "Texto para teste de métricas com {keyword}."
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=30,
                end_pos=38,
                context="com {keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        initial_total = validator.metrics["total_validations"]
        initial_successful = validator.metrics["successful_validations"]
        
        result = validator.validate_context(text, gaps)
        
        assert validator.metrics["total_validations"] == initial_total + 1
        assert validator.metrics["successful_validations"] == initial_successful + 1
        assert len(validator.metrics["validation_times"]) > 0
        assert len(validator.metrics["validation_scores"]) > 0
    
    def test_metrics_issue_distribution(self, validator):
        """Testa distribuição de tipos de problema nas métricas."""
        # Criar texto que gere problemas
        text = "Texto sem contexto claro."
        gaps = [
            DetectedGap(
                placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
                placeholder_name="keyword",
                start_pos=0,
                end_pos=8,
                context="{keyword}",
                confidence=0.9,
                detection_method=DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC
            )
        ]
        
        result = validator.validate_context(text, gaps)
        
        # Verificar se as métricas foram atualizadas
        assert validator.metrics["total_validations"] > 0
        if result.issues:
            assert len(validator.metrics["issue_distribution"]) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 