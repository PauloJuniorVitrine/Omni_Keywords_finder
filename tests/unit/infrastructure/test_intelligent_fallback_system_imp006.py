# =============================================================================
# Testes Unitários - Intelligent Fallback System IMP006
# =============================================================================
# 
# Testes para o sistema de fallback inteligente avançado
# Baseados completamente na implementação real do código
#
# Arquivo: infrastructure/processamento/intelligent_fallback_system_imp006.py
# Linhas: 748
# Tracing ID: test-intelligent-fallback-system-imp006-2025-01-27-001
# =============================================================================

import pytest
import time
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from typing import List, Dict, Any, Optional

from infrastructure.processamento.intelligent_fallback_system_imp006 import (
    IntelligentFallbackSystem,
    FallbackOption,
    FallbackResult,
    FallbackStrategy,
    FallbackQuality,
    generate_fallbacks,
    get_fallback_system_stats
)

# Mocks para os componentes importados
from infrastructure.processamento.hybrid_lacuna_detector_imp001 import (
    DetectedGap, 
    DetectionMethod, 
    ValidationLevel
)

from infrastructure.processamento.semantic_lacuna_detector_imp002 import (
    SemanticContext
)

from infrastructure.processamento.placeholder_unification_system_imp001 import (
    PlaceholderType
)


class TestIntelligentFallbackSystem:
    """Testes para o IntelligentFallbackSystem"""
    
    @pytest.fixture
    def system(self):
        """Fixture para criar instância do sistema"""
        return IntelligentFallbackSystem()
    
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
            surrounding_text="artigo sobre tecnologia para iniciantes",
            topic="tecnologia",
            intent="informar",
            entities=["tecnologia", "iniciantes"],
            sentiment=0.1,
            keywords=["tecnologia", "artigo", "iniciantes"],
            content_type="artigo",
            target_audience="iniciante",
            tone="neutro",
            complexity_level="baixo"
        )
    
    def test_inicializacao_sistema(self, system):
        """Teste de inicialização do sistema"""
        # Arrange & Act - Sistema já criado no fixture
        
        # Assert - Verificar estratégias de fallback
        assert FallbackStrategy.CONTEXTUAL in system.fallback_strategies
        assert FallbackStrategy.SEMANTIC in system.fallback_strategies
        assert FallbackStrategy.FREQUENCY in system.fallback_strategies
        assert FallbackStrategy.HISTORICAL in system.fallback_strategies
        assert FallbackStrategy.HYBRID in system.fallback_strategies
        
        # Verificar base de conhecimento
        assert "keyword_fallbacks" in system.fallback_knowledge
        assert "audience_fallbacks" in system.fallback_knowledge
        assert "content_type_fallbacks" in system.fallback_knowledge
        assert "tone_fallbacks" in system.fallback_knowledge
        assert "generic_fallbacks" in system.fallback_knowledge
        
        # Verificar histórico e cache
        assert system.usage_history == {}
        assert system.history_max_size == 10000
        assert system.fallback_cache == {}
        assert system.cache_ttl == 3600  # 1 hora
        
        # Verificar estrutura das métricas
        assert "total_fallbacks" in system.metrics
        assert "successful_fallbacks" in system.metrics
        assert "failed_fallbacks" in system.metrics
        assert "avg_fallback_time" in system.metrics
        assert "fallback_times" in system.metrics
        assert "quality_distribution" in system.metrics
        assert "strategy_usage" in system.metrics
        
        assert system.metrics["total_fallbacks"] == 0
        assert system.metrics["successful_fallbacks"] == 0
        assert system.metrics["failed_fallbacks"] == 0
        assert system.metrics["avg_fallback_time"] == 0.0
    
    def test_load_fallback_knowledge(self, system):
        """Teste de carregamento da base de conhecimento"""
        # Arrange & Act - Conhecimento já carregado no __init__
        
        # Assert - Verificar estrutura da base de conhecimento
        knowledge = system.fallback_knowledge
        
        # Verificar keyword_fallbacks
        keyword_fallbacks = knowledge["keyword_fallbacks"]
        assert "tecnologia" in keyword_fallbacks
        assert "saúde" in keyword_fallbacks
        assert "negócios" in keyword_fallbacks
        assert "educação" in keyword_fallbacks
        assert "lazer" in keyword_fallbacks
        
        assert isinstance(keyword_fallbacks["tecnologia"], list)
        assert len(keyword_fallbacks["tecnologia"]) > 0
        
        # Verificar audience_fallbacks
        audience_fallbacks = knowledge["audience_fallbacks"]
        assert "iniciante" in audience_fallbacks
        assert "intermediário" in audience_fallbacks
        assert "avançado" in audience_fallbacks
        assert "empresarial" in audience_fallbacks
        
        # Verificar content_type_fallbacks
        content_type_fallbacks = knowledge["content_type_fallbacks"]
        assert "artigo" in content_type_fallbacks
        assert "tutorial" in content_type_fallbacks
        assert "anúncio" in content_type_fallbacks
        assert "notícia" in content_type_fallbacks
        
        # Verificar tone_fallbacks
        tone_fallbacks = knowledge["tone_fallbacks"]
        assert "formal" in tone_fallbacks
        assert "casual" in tone_fallbacks
        assert "urgente" in tone_fallbacks
        assert "neutro" in tone_fallbacks
        
        # Verificar generic_fallbacks
        generic_fallbacks = knowledge["generic_fallbacks"]
        assert "keyword" in generic_fallbacks
        assert "audience" in generic_fallbacks
        assert "content" in generic_fallbacks
        assert "tone" in generic_fallbacks
    
    def test_generate_fallbacks_sucesso_hybrid(self, system, sample_text, mock_detected_gap, mock_semantic_context):
        """Teste de geração de fallbacks com sucesso usando estratégia híbrida"""
        # Act
        result = system.generate_fallbacks(sample_text, mock_detected_gap, mock_semantic_context, FallbackStrategy.HYBRID)
        
        # Assert
        assert isinstance(result, FallbackResult)
        assert result.success is True
        assert result.strategy_used == FallbackStrategy.HYBRID
        assert result.total_options > 0
        assert result.avg_quality > 0
        assert result.fallback_time > 0
        assert result.best_fallback is not None
        
        # Verificar estrutura das opções
        assert isinstance(result.fallback_options, list)
        assert len(result.fallback_options) > 0
        
        for option in result.fallback_options:
            assert isinstance(option, FallbackOption)
            assert option.value is not None
            assert 0 <= option.quality <= 1
            assert option.strategy in FallbackStrategy
            assert 0 <= option.confidence <= 1
            assert 0 <= option.context_relevance <= 1
            assert option.reasoning is not None
            assert isinstance(option.alternatives, list)
            assert isinstance(option.metadata, dict)
        
        # Verificar insights
        assert isinstance(result.insights, dict)
        assert "strategy_distribution" in result.insights
        assert "avg_quality_by_strategy" in result.insights
        assert "top_fallbacks" in result.insights
        assert "avg_quality" in result.insights
        assert "avg_confidence" in result.insights
    
    def test_generate_fallbacks_cache_functionality(self, system, sample_text, mock_detected_gap):
        """Teste de funcionalidade de cache"""
        # Arrange
        cache_key = f"{hash(sample_text)}:{mock_detected_gap.start_pos}:{mock_detected_gap.end_pos}:hybrid"
        
        # Act - Primeira execução (deve processar)
        result1 = system.generate_fallbacks(sample_text, mock_detected_gap, None, FallbackStrategy.HYBRID)
        
        # Act - Segunda execução (deve vir do cache)
        result2 = system.generate_fallbacks(sample_text, mock_detected_gap, None, FallbackStrategy.HYBRID)
        
        # Assert
        assert cache_key in system.fallback_cache
        assert result1 == result2
    
    def test_generate_fallbacks_diferentes_estrategias(self, system, sample_text, mock_detected_gap):
        """Teste de geração com diferentes estratégias"""
        strategies = [
            FallbackStrategy.CONTEXTUAL,
            FallbackStrategy.SEMANTIC,
            FallbackStrategy.FREQUENCY,
            FallbackStrategy.HISTORICAL,
            FallbackStrategy.HYBRID
        ]
        
        for strategy in strategies:
            # Act
            result = system.generate_fallbacks(sample_text, mock_detected_gap, None, strategy)
            
            # Assert
            assert isinstance(result, FallbackResult)
            assert result.strategy_used == strategy
            assert result.success is True
            assert result.total_options >= 0
            assert result.avg_quality >= 0
    
    def test_contextual_fallback(self, system, sample_text, mock_detected_gap):
        """Teste de fallback contextual"""
        # Act
        options = system._contextual_fallback(sample_text, mock_detected_gap, None)
        
        # Assert
        assert isinstance(options, list)
        
        for option in options:
            assert isinstance(option, FallbackOption)
            assert option.strategy == FallbackStrategy.CONTEXTUAL
            assert option.value is not None
            assert option.quality > 0
            assert option.confidence > 0
            assert option.context_relevance > 0
            assert option.reasoning is not None
            assert "tópico" in option.reasoning or "contexto" in option.reasoning
    
    def test_semantic_fallback(self, system, sample_text, mock_detected_gap, mock_semantic_context):
        """Teste de fallback semântico"""
        # Act
        options = system._semantic_fallback(sample_text, mock_detected_gap, mock_semantic_context)
        
        # Assert
        assert isinstance(options, list)
        
        for option in options:
            assert isinstance(option, FallbackOption)
            assert option.strategy == FallbackStrategy.SEMANTIC
            assert option.value is not None
            assert option.quality > 0
            assert option.confidence > 0
            assert option.context_relevance > 0
            assert option.reasoning is not None
            assert "semântico" in option.reasoning
    
    def test_semantic_fallback_sem_contexto(self, system, sample_text, mock_detected_gap):
        """Teste de fallback semântico sem contexto semântico"""
        # Act
        options = system._semantic_fallback(sample_text, mock_detected_gap, None)
        
        # Assert
        assert isinstance(options, list)
        assert len(options) == 0  # Deve retornar lista vazia sem contexto
    
    def test_frequency_fallback(self, system, sample_text, mock_detected_gap):
        """Teste de fallback por frequência"""
        # Act
        options = system._frequency_fallback(sample_text, mock_detected_gap, None)
        
        # Assert
        assert isinstance(options, list)
        assert len(options) > 0
        
        for i, option in enumerate(options):
            assert isinstance(option, FallbackOption)
            assert option.strategy == FallbackStrategy.FREQUENCY
            assert option.value is not None
            assert option.quality > 0
            assert option.confidence > 0
            assert option.reasoning is not None
            assert "frequência" in option.reasoning
            assert option.metadata["frequency_rank"] == i + 1
    
    def test_historical_fallback(self, system, sample_text, mock_detected_gap):
        """Teste de fallback histórico"""
        # Arrange - Adicionar histórico
        history_key = f"{mock_detected_gap.placeholder_type.value}_{mock_detected_gap.placeholder_name}"
        system.usage_history[history_key]["tecnologia"] = 5
        system.usage_history[history_key]["programação"] = 3
        system.usage_history[history_key]["desenvolvimento"] = 1
        
        # Act
        options = system._historical_fallback(sample_text, mock_detected_gap, None)
        
        # Assert
        assert isinstance(options, list)
        assert len(options) > 0
        
        for option in options:
            assert isinstance(option, FallbackOption)
            assert option.strategy == FallbackStrategy.HISTORICAL
            assert option.value is not None
            assert option.quality > 0
            assert option.confidence > 0
            assert option.reasoning is not None
            assert "histórico" in option.reasoning
            assert "historical_frequency" in option.metadata
            assert "historical_rank" in option.metadata
    
    def test_historical_fallback_sem_historico(self, system, sample_text, mock_detected_gap):
        """Teste de fallback histórico sem histórico"""
        # Act
        options = system._historical_fallback(sample_text, mock_detected_gap, None)
        
        # Assert
        assert isinstance(options, list)
        assert len(options) == 0  # Deve retornar lista vazia sem histórico
    
    def test_hybrid_fallback(self, system, sample_text, mock_detected_gap, mock_semantic_context):
        """Teste de fallback híbrido"""
        # Act
        options = system._hybrid_fallback(sample_text, mock_detected_gap, mock_semantic_context)
        
        # Assert
        assert isinstance(options, list)
        assert len(options) > 0
        
        # Verificar que não há duplicatas
        values = [option.value for option in options]
        assert len(values) == len(set(values))
        
        for option in options:
            assert isinstance(option, FallbackOption)
            assert option.value is not None
            assert option.quality > 0
    
    def test_generate_generic_fallbacks(self, system, mock_detected_gap):
        """Teste de geração de fallbacks genéricos"""
        # Act
        options = system._generate_generic_fallbacks(mock_detected_gap)
        
        # Assert
        assert isinstance(options, list)
        assert len(options) > 0
        
        for option in options:
            assert isinstance(option, FallbackOption)
            assert option.strategy == FallbackStrategy.FREQUENCY
            assert option.value is not None
            assert option.quality == 0.5
            assert option.confidence == 0.5
            assert option.context_relevance == 0.5
            assert option.reasoning == "Fallback genérico devido à falta de opções específicas"
            assert option.metadata["fallback_type"] == "generic"
            assert "category" in option.metadata
    
    def test_extract_context_for_fallback(self, system, sample_text, mock_detected_gap):
        """Teste de extração de contexto para fallback"""
        # Act
        context = system._extract_context_for_fallback(sample_text, mock_detected_gap)
        
        # Assert
        assert isinstance(context, str)
        assert len(context) > 0
        assert "artigo sobre" in context
        assert mock_detected_gap.start_pos - 150 <= len(context) <= mock_detected_gap.end_pos + 150
    
    def test_detect_context_topic(self, system):
        """Teste de detecção de tópico do contexto"""
        # Arrange
        context_tecnologia = "artigo sobre programação e desenvolvimento de software"
        context_saude = "texto sobre medicina e bem-estar"
        context_geral = "texto sem palavras-chave específicas"
        
        # Act & Assert
        topic_tecnologia = system._detect_context_topic(context_tecnologia)
        topic_saude = system._detect_context_topic(context_saude)
        topic_geral = system._detect_context_topic(context_geral)
        
        assert topic_tecnologia == "tecnologia"
        assert topic_saude == "saúde"
        assert topic_geral == "geral"
    
    def test_get_audience_fallbacks_from_context(self, system):
        """Teste de obtenção de fallbacks de audiência do contexto"""
        # Arrange
        context_iniciante = "artigo para iniciantes e novatos"
        context_empresarial = "conteúdo para empresas e negócios"
        
        # Act
        fallbacks_iniciante = system._get_audience_fallbacks_from_context(context_iniciante)
        fallbacks_empresarial = system._get_audience_fallbacks_from_context(context_empresarial)
        
        # Assert
        assert isinstance(fallbacks_iniciante, list)
        assert isinstance(fallbacks_empresarial, list)
        assert len(fallbacks_iniciante) > 0
        assert len(fallbacks_empresarial) > 0
    
    def test_get_intent_based_fallbacks(self, system):
        """Teste de obtenção de fallbacks baseados na intenção"""
        # Act
        tone_fallbacks = system._get_intent_based_fallbacks("informar", "tone")
        keyword_fallbacks = system._get_intent_based_fallbacks("persuadir", "keyword")
        
        # Assert
        assert isinstance(tone_fallbacks, list)
        assert isinstance(keyword_fallbacks, list)
        assert len(tone_fallbacks) > 0
        assert len(keyword_fallbacks) > 0
    
    def test_get_tone_by_intent(self, system):
        """Teste de obtenção de tom baseado na intenção"""
        # Act
        tones_informar = system._get_tone_by_intent("informar")
        tones_persuadir = system._get_tone_by_intent("persuadir")
        tones_instruir = system._get_tone_by_intent("instruir")
        tones_entreter = system._get_tone_by_intent("entreter")
        tones_unknown = system._get_tone_by_intent("unknown")
        
        # Assert
        assert isinstance(tones_informar, list)
        assert isinstance(tones_persuadir, list)
        assert isinstance(tones_instruir, list)
        assert isinstance(tones_entreter, list)
        assert isinstance(tones_unknown, list)
        
        assert len(tones_informar) > 0
        assert len(tones_persuadir) > 0
        assert len(tones_instruir) > 0
        assert len(tones_entreter) > 0
        assert len(tones_unknown) > 0
    
    def test_get_frequent_fallbacks(self, system):
        """Teste de obtenção de fallbacks frequentes"""
        # Act
        keyword_fallbacks = system._get_frequent_fallbacks("keyword")
        audience_fallbacks = system._get_frequent_fallbacks("audience")
        content_fallbacks = system._get_frequent_fallbacks("content")
        tone_fallbacks = system._get_frequent_fallbacks("tone")
        unknown_fallbacks = system._get_frequent_fallbacks("unknown")
        
        # Assert
        assert isinstance(keyword_fallbacks, list)
        assert isinstance(audience_fallbacks, list)
        assert isinstance(content_fallbacks, list)
        assert isinstance(tone_fallbacks, list)
        assert isinstance(unknown_fallbacks, list)
        
        assert len(keyword_fallbacks) > 0
        assert len(audience_fallbacks) > 0
        assert len(content_fallbacks) > 0
        assert len(tone_fallbacks) > 0
        assert len(unknown_fallbacks) > 0
    
    def test_rank_fallback_options(self, system, mock_detected_gap):
        """Teste de ranking de opções de fallback"""
        # Arrange
        options = [
            FallbackOption(
                value="opção1",
                quality=0.8,
                strategy=FallbackStrategy.CONTEXTUAL,
                confidence=0.7,
                context_relevance=0.6,
                reasoning="Teste 1",
                alternatives=[]
            ),
            FallbackOption(
                value="opção2",
                quality=0.6,
                strategy=FallbackStrategy.SEMANTIC,
                confidence=0.8,
                context_relevance=0.9,
                reasoning="Teste 2",
                alternatives=[]
            )
        ]
        
        # Act
        ranked_options = system._rank_fallback_options(options, mock_detected_gap, None)
        
        # Assert
        assert isinstance(ranked_options, list)
        assert len(ranked_options) == 2
        
        # Verificar se está ordenado por qualidade (decrescente)
        assert ranked_options[0].quality >= ranked_options[1].quality
        
        # Verificar se os scores foram recalculados
        for option in ranked_options:
            assert 0 <= option.quality <= 1
    
    def test_rank_fallback_options_vazia(self, system, mock_detected_gap):
        """Teste de ranking com lista vazia"""
        # Act
        ranked_options = system._rank_fallback_options([], mock_detected_gap, None)
        
        # Assert
        assert isinstance(ranked_options, list)
        assert len(ranked_options) == 0
    
    def test_generate_fallback_insights(self, system):
        """Teste de geração de insights de fallback"""
        # Arrange
        options = [
            FallbackOption(
                value="opção1",
                quality=0.8,
                strategy=FallbackStrategy.CONTEXTUAL,
                confidence=0.7,
                context_relevance=0.6,
                reasoning="Teste 1",
                alternatives=[]
            ),
            FallbackOption(
                value="opção2",
                quality=0.6,
                strategy=FallbackStrategy.SEMANTIC,
                confidence=0.8,
                context_relevance=0.9,
                reasoning="Teste 2",
                alternatives=[]
            )
        ]
        
        # Act
        insights = system._generate_fallback_insights(options, FallbackStrategy.HYBRID)
        
        # Assert
        assert isinstance(insights, dict)
        assert "strategy_distribution" in insights
        assert "avg_quality_by_strategy" in insights
        assert "top_fallbacks" in insights
        assert "avg_quality" in insights
        assert "avg_confidence" in insights
        
        # Verificar distribuição de estratégias
        strategy_dist = insights["strategy_distribution"]
        assert strategy_dist["contextual"] == 1
        assert strategy_dist["semantic"] == 1
        
        # Verificar top fallbacks
        assert len(insights["top_fallbacks"]) == 2
        assert "opção1" in insights["top_fallbacks"]
        assert "opção2" in insights["top_fallbacks"]
    
    def test_generate_fallback_insights_vazio(self, system):
        """Teste de geração de insights com lista vazia"""
        # Act
        insights = system._generate_fallback_insights([], FallbackStrategy.HYBRID)
        
        # Assert
        assert isinstance(insights, dict)
        assert insights == {}
    
    def test_update_usage_history(self, system, mock_detected_gap):
        """Teste de atualização do histórico de uso"""
        # Arrange
        history_key = f"{mock_detected_gap.placeholder_type.value}_{mock_detected_gap.placeholder_name}"
        
        # Act
        system._update_usage_history(mock_detected_gap, "tecnologia")
        system._update_usage_history(mock_detected_gap, "tecnologia")  # Incrementar
        system._update_usage_history(mock_detected_gap, "programação")
        
        # Assert
        assert history_key in system.usage_history
        assert system.usage_history[history_key]["tecnologia"] == 2
        assert system.usage_history[history_key]["programação"] == 1
    
    def test_update_metrics_sucesso(self, system):
        """Teste de atualização de métricas com sucesso"""
        # Act
        system._update_metrics(5, 0.5, 0.8, FallbackStrategy.HYBRID)
        
        # Assert
        assert system.metrics["total_fallbacks"] == 1
        assert system.metrics["successful_fallbacks"] == 1
        assert system.metrics["failed_fallbacks"] == 0
        assert system.metrics["avg_fallback_time"] == 0.5
        assert len(system.metrics["fallback_times"]) == 1
        assert system.metrics["quality_distribution"]["bom"] == 1
        assert system.metrics["strategy_usage"]["hybrid"] == 1
    
    def test_update_metrics_falha(self, system):
        """Teste de atualização de métricas com falha"""
        # Act
        system._update_metrics(0, 0.3, 0.0, FallbackStrategy.CONTEXTUAL)
        
        # Assert
        assert system.metrics["total_fallbacks"] == 1
        assert system.metrics["successful_fallbacks"] == 0
        assert system.metrics["failed_fallbacks"] == 1
    
    def test_get_quality_level(self, system):
        """Teste de conversão de qualidade para nível"""
        # Act & Assert
        assert system._get_quality_level(0.95) == "excelente"
        assert system._get_quality_level(0.85) == "bom"
        assert system._get_quality_level(0.75) == "justo"
        assert system._get_quality_level(0.55) == "ruim"
        assert system._get_quality_level(0.25) == "mínimo"
    
    def test_fallback_strategy_enum(self):
        """Teste dos valores do enum FallbackStrategy"""
        # Assert
        assert FallbackStrategy.CONTEXTUAL.value == "contextual"
        assert FallbackStrategy.SEMANTIC.value == "semantic"
        assert FallbackStrategy.FREQUENCY.value == "frequency"
        assert FallbackStrategy.HISTORICAL.value == "historical"
        assert FallbackStrategy.HYBRID.value == "hybrid"
    
    def test_fallback_quality_enum(self):
        """Teste dos valores do enum FallbackQuality"""
        # Assert
        assert FallbackQuality.EXCELLENT.value == 0.95
        assert FallbackQuality.GOOD.value == 0.85
        assert FallbackQuality.FAIR.value == 0.70
        assert FallbackQuality.POOR.value == 0.50
        assert FallbackQuality.MINIMAL.value == 0.30
    
    def test_fallback_option_dataclass(self):
        """Teste da estrutura do dataclass FallbackOption"""
        # Arrange
        option = FallbackOption(
            value="teste",
            quality=0.8,
            strategy=FallbackStrategy.CONTEXTUAL,
            confidence=0.7,
            context_relevance=0.6,
            reasoning="Teste de opção",
            alternatives=["alt1", "alt2"],
            metadata={"key": "value"}
        )
        
        # Assert
        assert option.value == "teste"
        assert option.quality == 0.8
        assert option.strategy == FallbackStrategy.CONTEXTUAL
        assert option.confidence == 0.7
        assert option.context_relevance == 0.6
        assert option.reasoning == "Teste de opção"
        assert option.alternatives == ["alt1", "alt2"]
        assert option.metadata["key"] == "value"
    
    def test_fallback_result_dataclass(self):
        """Teste da estrutura do dataclass FallbackResult"""
        # Arrange
        option = FallbackOption(
            value="teste",
            quality=0.8,
            strategy=FallbackStrategy.CONTEXTUAL,
            confidence=0.7,
            context_relevance=0.6,
            reasoning="Teste",
            alternatives=[]
        )
        
        result = FallbackResult(
            fallback_options=[option],
            best_fallback=option,
            total_options=1,
            avg_quality=0.8,
            fallback_time=0.5,
            strategy_used=FallbackStrategy.CONTEXTUAL,
            success=True,
            errors=[],
            warnings=[],
            insights={"test": "value"}
        )
        
        # Assert
        assert len(result.fallback_options) == 1
        assert result.best_fallback == option
        assert result.total_options == 1
        assert result.avg_quality == 0.8
        assert result.fallback_time == 0.5
        assert result.strategy_used == FallbackStrategy.CONTEXTUAL
        assert result.success is True
        assert result.errors == []
        assert result.warnings == []
        assert result.insights["test"] == "value"
    
    def test_generate_fallbacks_function(self, sample_text, mock_detected_gap):
        """Teste da função de conveniência generate_fallbacks"""
        # Act
        with patch('infrastructure.processamento.intelligent_fallback_system_imp006.IntelligentFallbackSystem') as mock_system_class:
            mock_system = Mock()
            mock_system.generate_fallbacks.return_value = Mock(success=True)
            mock_system_class.return_value = mock_system
            
            result = generate_fallbacks(sample_text, mock_detected_gap)
        
        # Assert
        mock_system.generate_fallbacks.assert_called_once()
        assert result.success is True
    
    def test_get_fallback_system_stats_function(self):
        """Teste da função de conveniência get_fallback_system_stats"""
        # Act
        with patch('infrastructure.processamento.intelligent_fallback_system_imp006.IntelligentFallbackSystem') as mock_system_class:
            mock_system = Mock()
            mock_system.metrics = {"test": "data"}
            mock_system_class.return_value = mock_system
            
            stats = get_fallback_system_stats()
        
        # Assert
        assert stats == {"test": "data"}
    
    def test_generate_fallbacks_erro(self, system, sample_text, mock_detected_gap):
        """Teste de geração de fallbacks com erro"""
        # Arrange - Mock para simular erro
        with patch.object(system, '_contextual_fallback', side_effect=Exception("Erro de teste")):
            # Act
            result = system.generate_fallbacks(sample_text, mock_detected_gap, None, FallbackStrategy.CONTEXTUAL)
            
            # Assert
            assert isinstance(result, FallbackResult)
            assert result.success is False
            assert len(result.errors) > 0
            assert "Erro de teste" in result.errors[0]
            assert result.total_options == 0
            assert result.best_fallback is None
    
    def test_generate_fallbacks_sem_opcoes(self, system, sample_text, mock_detected_gap):
        """Teste de geração de fallbacks sem opções específicas"""
        # Arrange - Mock para retornar lista vazia
        with patch.object(system, '_contextual_fallback', return_value=[]):
            # Act
            result = system.generate_fallbacks(sample_text, mock_detected_gap, None, FallbackStrategy.CONTEXTUAL)
            
            # Assert
            assert isinstance(result, FallbackResult)
            assert result.success is True
            assert result.total_options > 0  # Deve usar fallbacks genéricos
            assert result.best_fallback is not None
            assert len(result.warnings) > 0
            assert "fallback genérico" in result.warnings[0]
    
    def test_limite_historico(self, system, mock_detected_gap):
        """Teste de limite do histórico de uso"""
        # Arrange
        history_key = f"{mock_detected_gap.placeholder_type.value}_{mock_detected_gap.placeholder_name}"
        
        # Adicionar mais itens que o limite
        for i in range(system.history_max_size + 10):
            system.usage_history[history_key][f"item_{i}"] = i
        
        # Act
        system._update_usage_history(mock_detected_gap, "novo_item")
        
        # Assert
        assert len(system.usage_history[history_key]) <= system.history_max_size 