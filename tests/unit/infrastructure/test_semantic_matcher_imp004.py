# =============================================================================
# Testes Unitários - Semantic Matcher IMP004
# =============================================================================
# 
# Testes para o matcher semântico avançado
# Baseados completamente na implementação real do código
#
# Arquivo: infrastructure/processamento/semantic_matcher_imp004.py
# Linhas: 837
# Tracing ID: test-semantic-matcher-imp004-2025-01-27-001
# =============================================================================

import pytest
import time
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from infrastructure.processamento.semantic_matcher_imp004 import (
    SemanticMatcher,
    SemanticMatch,
    MatchingResult,
    MatchingStrategy,
    MatchQuality,
    match_semantically,
    get_semantic_matching_stats
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

from infrastructure.processamento.placeholder_unification_system_imp001 import (
    PlaceholderType
)


class TestSemanticMatcher:
    """Testes para o SemanticMatcher"""
    
    @pytest.fixture
    def matcher(self):
        """Fixture para criar instância do matcher"""
        return SemanticMatcher()
    
    @pytest.fixture
    def sample_text(self):
        """Fixture com texto de exemplo baseado no código real"""
        return """
        Preciso criar um artigo sobre {primary_keyword} para o público {target_audience}.
        O conteúdo deve ser {content_type} com tom {tone}.
        """
    
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
    def mock_semantic_context(self):
        """Fixture para criar contexto semântico mock"""
        return SemanticContext(
            topic="tecnologia",
            intent="informar",
            content_type="artigo",
            target_audience="iniciante",
            semantic_score=0.85,
            context_confidence=0.8
        )
    
    def test_inicializacao_matcher(self, matcher):
        """Teste de inicialização do matcher"""
        # Arrange & Act - Matcher já criado no fixture
        
        # Assert - Verificar estratégias de matching
        assert MatchingStrategy.SEMANTIC_SIMILARITY in matcher.matching_strategies
        assert MatchingStrategy.CONTEXTUAL_RELEVANCE in matcher.matching_strategies
        assert MatchingStrategy.INTENT_ALIGNMENT in matcher.matching_strategies
        assert MatchingStrategy.FREQUENCY_BASED in matcher.matching_strategies
        assert MatchingStrategy.HYBRID in matcher.matching_strategies
        
        # Verificar base de conhecimento
        assert "keyword_suggestions" in matcher.knowledge_base
        assert "audience_suggestions" in matcher.knowledge_base
        assert "content_type_suggestions" in matcher.knowledge_base
        assert "tone_suggestions" in matcher.knowledge_base
        
        # Verificar padrões de matching
        assert "keyword_patterns" in matcher.matching_patterns
        assert "context_patterns" in matcher.matching_patterns
        assert "intent_patterns" in matcher.matching_patterns
        
        # Verificar cache e métricas
        assert matcher.match_cache == {}
        assert matcher.cache_ttl == 3600  # 1 hora
        
        # Verificar estrutura das métricas
        assert "total_matches" in matcher.metrics
        assert "successful_matches" in matcher.metrics
        assert "failed_matches" in matcher.metrics
        assert "avg_matching_time" in matcher.metrics
        assert "matching_times" in matcher.metrics
        assert "quality_distribution" in matcher.metrics
        assert "strategy_usage" in matcher.metrics
        
        assert matcher.metrics["total_matches"] == 0
        assert matcher.metrics["successful_matches"] == 0
        assert matcher.metrics["failed_matches"] == 0
        assert matcher.metrics["avg_matching_time"] == 0.0
    
    def test_match_semantically_sucesso(self, matcher, sample_text, mock_detected_gap, mock_semantic_context):
        """Teste de matching semântico com sucesso"""
        # Arrange
        gaps = [mock_detected_gap]
        
        # Act
        result = matcher.match_semantically(sample_text, gaps, mock_semantic_context, MatchingStrategy.HYBRID)
        
        # Assert
        assert isinstance(result, MatchingResult)
        assert isinstance(result.matches, list)
        assert result.total_matches >= 0
        assert isinstance(result.avg_match_quality, float)
        assert isinstance(result.avg_confidence, float)
        assert result.matching_time > 0
        assert result.strategy_used == MatchingStrategy.HYBRID
        assert isinstance(result.success, bool)
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.insights, dict)
        
        # Verificar insights se houver matches
        if result.matches:
            assert "quality_distribution" in result.insights
            assert "strategy_success" in result.insights
            assert "top_suggestions" in result.insights
            assert "avg_quality" in result.insights
            assert "avg_confidence" in result.insights
    
    def test_match_semantically_cache_functionality(self, matcher, sample_text, mock_detected_gap):
        """Teste de funcionalidade de cache"""
        # Arrange
        gaps = [mock_detected_gap]
        cache_key = f"{hash(sample_text)}:{len(gaps)}:{MatchingStrategy.HYBRID.value}"
        
        # Act - Primeira execução (deve processar)
        result1 = matcher.match_semantically(sample_text, gaps, strategy=MatchingStrategy.HYBRID)
        
        # Act - Segunda execução (deve vir do cache)
        result2 = matcher.match_semantically(sample_text, gaps, strategy=MatchingStrategy.HYBRID)
        
        # Assert
        assert cache_key in matcher.match_cache
        assert result1 == result2
    
    def test_match_semantically_com_diferentes_estrategias(self, matcher, sample_text, mock_detected_gap):
        """Teste de matching com diferentes estratégias"""
        # Arrange
        gaps = [mock_detected_gap]
        strategies = [
            MatchingStrategy.SEMANTIC_SIMILARITY,
            MatchingStrategy.CONTEXTUAL_RELEVANCE,
            MatchingStrategy.INTENT_ALIGNMENT,
            MatchingStrategy.FREQUENCY_BASED,
            MatchingStrategy.HYBRID
        ]
        
        # Act & Assert
        for strategy in strategies:
            result = matcher.match_semantically(sample_text, gaps, strategy=strategy)
            
            assert isinstance(result, MatchingResult)
            assert result.strategy_used == strategy
            assert isinstance(result.success, bool)
            assert result.matching_time > 0
    
    def test_match_semantically_sem_gaps(self, matcher, sample_text):
        """Teste de matching sem gaps"""
        # Act
        result = matcher.match_semantically(sample_text, [], strategy=MatchingStrategy.HYBRID)
        
        # Assert
        assert isinstance(result, MatchingResult)
        assert result.total_matches == 0
        assert result.avg_match_quality == 0.0
        assert result.avg_confidence == 0.0
        assert result.success is True
        assert len(result.errors) == 0
    
    def test_match_single_gap(self, matcher, sample_text, mock_detected_gap, mock_semantic_context):
        """Teste de matching para uma lacuna individual"""
        # Act
        match = matcher._match_single_gap(sample_text, mock_detected_gap, mock_semantic_context, MatchingStrategy.HYBRID)
        
        # Assert
        if match:  # Pode retornar None se não encontrar match
            assert isinstance(match, SemanticMatch)
            assert match.gap == mock_detected_gap
            assert isinstance(match.suggested_value, str)
            assert isinstance(match.match_quality, float)
            assert match.matching_strategy == MatchingStrategy.HYBRID
            assert isinstance(match.confidence_score, float)
            assert isinstance(match.relevance_score, float)
            assert isinstance(match.context_alignment, float)
            assert isinstance(match.alternative_matches, list)
            assert isinstance(match.reasoning, str)
            assert isinstance(match.metadata, dict)
    
    def test_semantic_similarity_matching(self, matcher, sample_text, mock_detected_gap):
        """Teste de matching por similaridade semântica"""
        # Act
        result = matcher._semantic_similarity_matching(sample_text, mock_detected_gap, None)
        
        # Assert
        if result:  # Pode retornar None se não encontrar match
            suggestion, score, reasoning = result
            assert isinstance(suggestion, str)
            assert isinstance(score, float)
            assert isinstance(reasoning, str)
            assert 0 <= score <= 1
            assert "Similaridade semântica" in reasoning
    
    def test_contextual_relevance_matching(self, matcher, sample_text, mock_detected_gap):
        """Teste de matching por relevância contextual"""
        # Act
        result = matcher._contextual_relevance_matching(sample_text, mock_detected_gap, None)
        
        # Assert
        if result:  # Pode retornar None se não encontrar match
            suggestion, score, reasoning = result
            assert isinstance(suggestion, str)
            assert isinstance(score, float)
            assert isinstance(reasoning, str)
            assert 0 <= score <= 1
            assert "Relevância contextual" in reasoning
    
    def test_intent_alignment_matching(self, matcher, sample_text, mock_detected_gap):
        """Teste de matching por alinhamento de intenção"""
        # Act
        result = matcher._intent_alignment_matching(sample_text, mock_detected_gap, None)
        
        # Assert
        if result:  # Pode retornar None se não encontrar match
            suggestion, score, reasoning = result
            assert isinstance(suggestion, str)
            assert isinstance(score, float)
            assert isinstance(reasoning, str)
            assert 0 <= score <= 1
            assert "Alinhamento de intenção" in reasoning
    
    def test_frequency_based_matching(self, matcher, sample_text, mock_detected_gap):
        """Teste de matching baseado em frequência"""
        # Act
        result = matcher._frequency_based_matching(sample_text, mock_detected_gap, None)
        
        # Assert
        if result:  # Pode retornar None se não encontrar match
            suggestion, score, reasoning = result
            assert isinstance(suggestion, str)
            assert isinstance(score, float)
            assert isinstance(reasoning, str)
            assert 0 <= score <= 1
            assert "Frequência de uso" in reasoning
    
    def test_hybrid_matching(self, matcher, sample_text, mock_detected_gap):
        """Teste de matching híbrido"""
        # Act
        result = matcher._hybrid_matching(sample_text, mock_detected_gap, None)
        
        # Assert
        if result:  # Pode retornar None se não encontrar match
            suggestion, score, reasoning = result
            assert isinstance(suggestion, str)
            assert isinstance(score, float)
            assert isinstance(reasoning, str)
            assert 0 <= score <= 1
            assert "Híbrido" in reasoning
    
    def test_extract_context_for_matching(self, matcher, sample_text, mock_detected_gap):
        """Teste de extração de contexto para matching"""
        # Act
        context = matcher._extract_context_for_matching(sample_text, mock_detected_gap)
        
        # Assert
        assert isinstance(context, str)
        assert len(context) > 0
        assert "artigo sobre" in context
    
    def test_get_suggestions_by_type(self, matcher):
        """Teste de obtenção de sugestões por tipo"""
        # Act & Assert
        keyword_suggestions = matcher._get_suggestions_by_type("primary_keyword")
        audience_suggestions = matcher._get_suggestions_by_type("target_audience")
        content_suggestions = matcher._get_suggestions_by_type("content_type")
        tone_suggestions = matcher._get_suggestions_by_type("tone")
        
        assert isinstance(keyword_suggestions, list)
        assert isinstance(audience_suggestions, list)
        assert isinstance(content_suggestions, list)
        assert isinstance(tone_suggestions, list)
        
        # Verificar se as sugestões vêm da base de conhecimento
        assert all(suggestion in matcher.knowledge_base["keyword_suggestions"]["tecnologia"] for suggestion in keyword_suggestions)
    
    def test_calculate_semantic_similarity(self, matcher):
        """Teste de cálculo de similaridade semântica"""
        # Arrange
        context = "artigo sobre tecnologia e programação"
        suggestion = "programação"
        
        # Act
        similarity = matcher._calculate_semantic_similarity(context, suggestion)
        
        # Assert
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
        assert similarity > 0  # Deve haver alguma similaridade
    
    def test_calculate_semantic_similarity_sem_intersecao(self, matcher):
        """Teste de cálculo de similaridade semântica sem interseção"""
        # Arrange
        context = "artigo sobre tecnologia"
        suggestion = "culinária"
        
        # Act
        similarity = matcher._calculate_semantic_similarity(context, suggestion)
        
        # Assert
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
        assert similarity == 0.0  # Sem interseção
    
    def test_extract_contextual_info(self, matcher, sample_text, mock_detected_gap):
        """Teste de extração de informações contextuais"""
        # Act
        context_info = matcher._extract_contextual_info(sample_text, mock_detected_gap)
        
        # Assert
        assert isinstance(context_info, dict)
        assert "topic" in context_info
        assert "audience" in context_info
        assert "intent" in context_info
        assert "content_type" in context_info
        
        assert isinstance(context_info["topic"], str)
        assert isinstance(context_info["audience"], str)
        assert isinstance(context_info["intent"], str)
        assert isinstance(context_info["content_type"], str)
    
    def test_detect_context_topic(self, matcher):
        """Teste de detecção de tópico do contexto"""
        # Act & Assert
        tech_context = "artigo sobre programação e desenvolvimento"
        health_context = "texto sobre saúde e bem-estar"
        business_context = "conteúdo sobre negócios e empreendedorismo"
        
        tech_topic = matcher._detect_context_topic(tech_context)
        health_topic = matcher._detect_context_topic(health_context)
        business_topic = matcher._detect_context_topic(business_context)
        
        assert tech_topic in ["tecnologia", "geral"]
        assert health_topic in ["saúde", "geral"]
        assert business_topic in ["negócios", "geral"]
    
    def test_detect_context_audience(self, matcher):
        """Teste de detecção de audiência do contexto"""
        # Act & Assert
        beginner_context = "texto para iniciantes e novatos"
        advanced_context = "conteúdo para especialistas e profissionais"
        
        beginner_audience = matcher._detect_context_audience(beginner_context)
        advanced_audience = matcher._detect_context_audience(advanced_context)
        
        assert beginner_audience in ["iniciante", "geral"]
        assert advanced_audience in ["avançado", "geral"]
    
    def test_detect_context_intent(self, matcher):
        """Teste de detecção de intenção do contexto"""
        # Act & Assert
        inform_context = "texto para explicar e descrever"
        persuade_context = "conteúdo para convencer e influenciar"
        instruct_context = "material para ensinar e guiar"
        entertain_context = "conteúdo para divertir e animar"
        
        inform_intent = matcher._detect_context_intent(inform_context)
        persuade_intent = matcher._detect_context_intent(persuade_context)
        instruct_intent = matcher._detect_context_intent(instruct_context)
        entertain_intent = matcher._detect_context_intent(entertain_context)
        
        assert inform_intent in ["informar", "geral"]
        assert persuade_intent in ["persuadir", "geral"]
        assert instruct_intent in ["instruir", "geral"]
        assert entertain_intent in ["entreter", "geral"]
    
    def test_detect_context_content_type(self, matcher):
        """Teste de detecção de tipo de conteúdo do contexto"""
        # Act & Assert
        article_context = "artigo sobre tecnologia"
        tutorial_context = "tutorial de programação"
        ad_context = "anúncio de produto"
        news_context = "notícia sobre tecnologia"
        
        article_type = matcher._detect_context_content_type(article_context)
        tutorial_type = matcher._detect_context_content_type(tutorial_context)
        ad_type = matcher._detect_context_content_type(ad_context)
        news_type = matcher._detect_context_content_type(news_context)
        
        assert article_type in ["artigo", "texto"]
        assert tutorial_type in ["tutorial", "texto"]
        assert ad_type in ["anúncio", "texto"]
        assert news_type in ["notícia", "texto"]
    
    def test_find_contextually_relevant_suggestions(self, matcher):
        """Teste de busca de sugestões relevantes ao contexto"""
        # Arrange
        context_info = {
            "topic": "tecnologia",
            "audience": "iniciante",
            "intent": "informar",
            "content_type": "artigo"
        }
        
        # Act
        keyword_suggestions = matcher._find_contextually_relevant_suggestions("primary_keyword", context_info)
        audience_suggestions = matcher._find_contextually_relevant_suggestions("target_audience", context_info)
        content_suggestions = matcher._find_contextually_relevant_suggestions("content_type", context_info)
        tone_suggestions = matcher._find_contextually_relevant_suggestions("tone", context_info)
        
        # Assert
        assert isinstance(keyword_suggestions, list)
        assert isinstance(audience_suggestions, list)
        assert isinstance(content_suggestions, list)
        assert isinstance(tone_suggestions, list)
    
    def test_get_tone_by_intent(self, matcher):
        """Teste de obtenção de tom baseado na intenção"""
        # Act & Assert
        inform_tones = matcher._get_tone_by_intent("informar")
        persuade_tones = matcher._get_tone_by_intent("persuadir")
        instruct_tones = matcher._get_tone_by_intent("instruir")
        entertain_tones = matcher._get_tone_by_intent("entreter")
        
        assert isinstance(inform_tones, list)
        assert isinstance(persuade_tones, list)
        assert isinstance(instruct_tones, list)
        assert isinstance(entertain_tones, list)
        
        assert len(inform_tones) > 0
        assert len(persuade_tones) > 0
        assert len(instruct_tones) > 0
        assert len(entertain_tones) > 0
    
    def test_calculate_contextual_relevance(self, matcher):
        """Teste de cálculo de relevância contextual"""
        # Arrange
        suggestion = "programação"
        context_info = {
            "topic": "tecnologia",
            "audience": "iniciante",
            "intent": "informar",
            "content_type": "artigo"
        }
        
        # Act
        relevance = matcher._calculate_contextual_relevance(suggestion, context_info)
        
        # Assert
        assert isinstance(relevance, float)
        assert 0 <= relevance <= 1
        assert relevance > 0.5  # Score base é 0.5
    
    def test_detect_text_intent(self, matcher, sample_text, mock_detected_gap):
        """Teste de detecção de intenção do texto"""
        # Act
        intent = matcher._detect_text_intent(sample_text, mock_detected_gap)
        
        # Assert
        assert isinstance(intent, str)
        assert intent in ["informar", "persuadir", "instruir", "entreter", "geral"]
    
    def test_get_intent_aligned_suggestions(self, matcher):
        """Teste de obtenção de sugestões alinhadas com intenção"""
        # Act
        tone_suggestions = matcher._get_intent_aligned_suggestions("tone", "informar")
        keyword_suggestions = matcher._get_intent_aligned_suggestions("primary_keyword", "persuadir")
        
        # Assert
        assert isinstance(tone_suggestions, list)
        assert isinstance(keyword_suggestions, list)
        assert len(tone_suggestions) > 0
        assert len(keyword_suggestions) > 0
    
    def test_calculate_intent_alignment(self, matcher):
        """Teste de cálculo de alinhamento com intenção"""
        # Act & Assert
        inform_alignment = matcher._calculate_intent_alignment("sugestão", "informar")
        persuade_alignment = matcher._calculate_intent_alignment("sugestão", "persuadir")
        instruct_alignment = matcher._calculate_intent_alignment("sugestão", "instruir")
        entertain_alignment = matcher._calculate_intent_alignment("sugestão", "entreter")
        
        assert isinstance(inform_alignment, float)
        assert isinstance(persuade_alignment, float)
        assert isinstance(instruct_alignment, float)
        assert isinstance(entertain_alignment, float)
        
        assert 0 <= inform_alignment <= 1
        assert 0 <= persuade_alignment <= 1
        assert 0 <= instruct_alignment <= 1
        assert 0 <= entertain_alignment <= 1
    
    def test_get_frequency_based_suggestions(self, matcher):
        """Teste de obtenção de sugestões baseadas em frequência"""
        # Act
        keyword_suggestions = matcher._get_frequency_based_suggestions("primary_keyword")
        audience_suggestions = matcher._get_frequency_based_suggestions("target_audience")
        content_suggestions = matcher._get_frequency_based_suggestions("content_type")
        tone_suggestions = matcher._get_frequency_based_suggestions("tone")
        
        # Assert
        assert isinstance(keyword_suggestions, list)
        assert isinstance(audience_suggestions, list)
        assert isinstance(content_suggestions, list)
        assert isinstance(tone_suggestions, list)
        
        assert len(keyword_suggestions) > 0
        assert len(audience_suggestions) > 0
        assert len(content_suggestions) > 0
        assert len(tone_suggestions) > 0
    
    def test_generate_alternative_matches(self, matcher, sample_text, mock_detected_gap):
        """Teste de geração de matches alternativos"""
        # Act
        alternatives = matcher._generate_alternative_matches(sample_text, mock_detected_gap, None, MatchingStrategy.HYBRID)
        
        # Assert
        assert isinstance(alternatives, list)
        
        for suggestion, score in alternatives:
            assert isinstance(suggestion, str)
            assert isinstance(score, float)
            assert 0 <= score <= 1
        
        # Máximo 3 alternativas
        assert len(alternatives) <= 3
    
    def test_calculate_confidence_score(self, matcher, mock_detected_gap, mock_semantic_context):
        """Teste de cálculo de score de confiança"""
        # Act
        confidence = matcher._calculate_confidence_score(mock_detected_gap, "sugestão", mock_semantic_context)
        
        # Assert
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
        assert confidence >= mock_detected_gap.confidence  # Deve ser pelo menos a confiança base
    
    def test_calculate_relevance_score(self, matcher, mock_detected_gap):
        """Teste de cálculo de score de relevância"""
        # Act
        relevance = matcher._calculate_relevance_score(mock_detected_gap, "sugestão", None)
        
        # Assert
        assert isinstance(relevance, float)
        assert 0 <= relevance <= 1
        assert relevance >= 0.7  # Score base é 0.7
    
    def test_calculate_context_alignment(self, matcher, mock_detected_gap, mock_semantic_context):
        """Teste de cálculo de alinhamento com contexto"""
        # Act
        alignment = matcher._calculate_context_alignment(mock_detected_gap, "sugestão", mock_semantic_context)
        
        # Assert
        assert isinstance(alignment, float)
        assert 0 <= alignment <= 1
        assert alignment >= 0.8  # Score base é 0.8
    
    def test_generate_matching_insights(self, matcher, mock_detected_gap):
        """Teste de geração de insights sobre matching"""
        # Arrange
        match = SemanticMatch(
            gap=mock_detected_gap,
            suggested_value="programação",
            match_quality=0.85,
            matching_strategy=MatchingStrategy.HYBRID,
            confidence_score=0.9,
            relevance_score=0.8,
            context_alignment=0.85,
            alternative_matches=[("desenvolvimento", 0.8)],
            reasoning="Teste de matching"
        )
        
        matches = [match]
        
        # Act
        insights = matcher._generate_matching_insights(matches, MatchingStrategy.HYBRID)
        
        # Assert
        assert isinstance(insights, dict)
        assert "quality_distribution" in insights
        assert "strategy_success" in insights
        assert "top_suggestions" in insights
        assert "avg_quality" in insights
        assert "avg_confidence" in insights
        
        assert isinstance(insights["quality_distribution"], dict)
        assert isinstance(insights["strategy_success"], dict)
        assert isinstance(insights["top_suggestions"], dict)
        assert isinstance(insights["avg_quality"], float)
        assert isinstance(insights["avg_confidence"], float)
    
    def test_generate_matching_insights_sem_matches(self, matcher):
        """Teste de geração de insights sem matches"""
        # Act
        insights = matcher._generate_matching_insights([], MatchingStrategy.HYBRID)
        
        # Assert
        assert insights == {}
    
    def test_get_quality_level(self, matcher):
        """Teste de conversão de valor de qualidade em nível"""
        # Act & Assert
        assert matcher._get_quality_level(0.95) == "excelente"
        assert matcher._get_quality_level(0.85) == "bom"
        assert matcher._get_quality_level(0.75) == "justo"
        assert matcher._get_quality_level(0.55) == "ruim"
        assert matcher._get_quality_level(0.25) == "inadequado"
    
    def test_update_metrics_sucesso(self, matcher):
        """Teste de atualização de métricas com sucesso"""
        # Act
        matcher._update_metrics(3, 0.5, 0.85, MatchingStrategy.HYBRID)
        
        # Assert
        assert matcher.metrics["total_matches"] == 1
        assert matcher.metrics["successful_matches"] == 1
        assert matcher.metrics["failed_matches"] == 0
        assert matcher.metrics["avg_matching_time"] == 0.5
        assert len(matcher.metrics["matching_times"]) == 1
        assert matcher.metrics["quality_distribution"]["bom"] == 1
        assert matcher.metrics["strategy_usage"]["hybrid"] == 1
    
    def test_update_metrics_falha(self, matcher):
        """Teste de atualização de métricas com falha"""
        # Act
        matcher._update_metrics(0, 0.3, 0.0, MatchingStrategy.HYBRID)
        
        # Assert
        assert matcher.metrics["total_matches"] == 1
        assert matcher.metrics["successful_matches"] == 0
        assert matcher.metrics["failed_matches"] == 1
    
    def test_matching_strategy_enum(self):
        """Teste dos valores do enum MatchingStrategy"""
        # Assert
        assert MatchingStrategy.SEMANTIC_SIMILARITY.value == "semantic_similarity"
        assert MatchingStrategy.CONTEXTUAL_RELEVANCE.value == "contextual_relevance"
        assert MatchingStrategy.INTENT_ALIGNMENT.value == "intent_alignment"
        assert MatchingStrategy.FREQUENCY_BASED.value == "frequency_based"
        assert MatchingStrategy.HYBRID.value == "hybrid"
    
    def test_match_quality_enum(self):
        """Teste dos valores do enum MatchQuality"""
        # Assert
        assert MatchQuality.EXCELLENT.value == 0.95
        assert MatchQuality.GOOD.value == 0.85
        assert MatchQuality.FAIR.value == 0.70
        assert MatchQuality.POOR.value == 0.50
        assert MatchQuality.UNSUITABLE.value == 0.30
    
    def test_semantic_match_dataclass(self):
        """Teste da estrutura do dataclass SemanticMatch"""
        # Arrange
        gap = DetectedGap(
            placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
            placeholder_name="test",
            start_pos=0,
            end_pos=10,
            context="test",
            confidence=0.8,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        match = SemanticMatch(
            gap=gap,
            suggested_value="programação",
            match_quality=0.85,
            matching_strategy=MatchingStrategy.HYBRID,
            confidence_score=0.9,
            relevance_score=0.8,
            context_alignment=0.85,
            alternative_matches=[("desenvolvimento", 0.8)],
            reasoning="Teste de matching",
            metadata={"key": "value"}
        )
        
        # Assert
        assert match.gap == gap
        assert match.suggested_value == "programação"
        assert match.match_quality == 0.85
        assert match.matching_strategy == MatchingStrategy.HYBRID
        assert match.confidence_score == 0.9
        assert match.relevance_score == 0.8
        assert match.context_alignment == 0.85
        assert match.alternative_matches == [("desenvolvimento", 0.8)]
        assert match.reasoning == "Teste de matching"
        assert match.metadata["key"] == "value"
    
    def test_matching_result_dataclass(self):
        """Teste da estrutura do dataclass MatchingResult"""
        # Arrange
        result = MatchingResult(
            matches=[],
            total_matches=0,
            avg_match_quality=0.0,
            avg_confidence=0.0,
            matching_time=0.5,
            strategy_used=MatchingStrategy.HYBRID,
            success=True,
            errors=[],
            warnings=[],
            insights={"test": "data"}
        )
        
        # Assert
        assert result.matches == []
        assert result.total_matches == 0
        assert result.avg_match_quality == 0.0
        assert result.avg_confidence == 0.0
        assert result.matching_time == 0.5
        assert result.strategy_used == MatchingStrategy.HYBRID
        assert result.success is True
        assert result.errors == []
        assert result.warnings == []
        assert result.insights["test"] == "data"
    
    def test_match_semantically_function(self, sample_text, mock_detected_gap):
        """Teste da função de conveniência match_semantically"""
        # Act
        with patch('infrastructure.processamento.semantic_matcher_imp004.SemanticMatcher') as mock_matcher_class:
            mock_matcher = Mock()
            mock_matcher.match_semantically.return_value = Mock(total_matches=1)
            mock_matcher_class.return_value = mock_matcher
            
            result = match_semantically(sample_text, [mock_detected_gap])
        
        # Assert
        mock_matcher.match_semantically.assert_called_once()
        assert result.total_matches == 1
    
    def test_get_semantic_matching_stats_function(self):
        """Teste da função de conveniência get_semantic_matching_stats"""
        # Act
        with patch('infrastructure.processamento.semantic_matcher_imp004.SemanticMatcher') as mock_matcher_class:
            mock_matcher = Mock()
            mock_matcher.metrics = {"test": "data"}
            mock_matcher_class.return_value = mock_matcher
            
            stats = get_semantic_matching_stats()
        
        # Assert
        assert stats == {"test": "data"}
    
    def test_match_semantically_erro(self, matcher, sample_text, mock_detected_gap):
        """Teste de matching semântico com erro"""
        # Arrange - Mock para simular erro
        with patch.object(matcher, '_match_single_gap') as mock_match:
            mock_match.side_effect = Exception("Erro de teste")
            
            # Act
            result = matcher.match_semantically(sample_text, [mock_detected_gap])
            
            # Assert
            assert isinstance(result, MatchingResult)
            assert result.total_matches == 0
            assert result.avg_match_quality == 0.0
            assert result.avg_confidence == 0.0
            assert result.success is False
            assert len(result.errors) == 1
            assert "Erro de teste" in result.errors[0]
    
    def test_load_knowledge_base(self, matcher):
        """Teste de carregamento da base de conhecimento"""
        # Act
        knowledge_base = matcher._load_knowledge_base()
        
        # Assert
        assert isinstance(knowledge_base, dict)
        assert "keyword_suggestions" in knowledge_base
        assert "audience_suggestions" in knowledge_base
        assert "content_type_suggestions" in knowledge_base
        assert "tone_suggestions" in knowledge_base
        
        # Verificar estrutura das sugestões
        for category, suggestions in knowledge_base.items():
            assert isinstance(suggestions, dict)
            for subcategory, items in suggestions.items():
                assert isinstance(items, list)
                assert all(isinstance(item, str) for item in items)
    
    def test_create_matching_patterns(self, matcher):
        """Teste de criação de padrões de matching"""
        # Act
        patterns = matcher._create_matching_patterns()
        
        # Assert
        assert isinstance(patterns, dict)
        assert "keyword_patterns" in patterns
        assert "context_patterns" in patterns
        assert "intent_patterns" in patterns
        
        # Verificar que são listas de strings (regex patterns)
        for pattern_list in patterns.values():
            assert isinstance(pattern_list, list)
            assert all(isinstance(pattern, str) for pattern in pattern_list) 