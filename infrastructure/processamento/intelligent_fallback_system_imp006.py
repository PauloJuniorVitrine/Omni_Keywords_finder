#!/usr/bin/env python3
"""
Sistema de Fallback Inteligente - Versão Avançada
=================================================

Tracing ID: INTELLIGENT_FALLBACK_IMP006_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema de fallback inteligente que:
- Fornece valores de fallback contextuais
- Aplica lógica semântica para seleção
- Considera histórico de uso
- Adapta-se ao contexto do texto
- Integra com todos os componentes
- Fornece múltiplas opções rankeadas

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

from .quality_validator_imp005 import (
    QualityReport,
    QualityLevel,
    QualityValidator
)

from .placeholder_unification_system_imp001 import (
    PlaceholderType,
    PlaceholderUnificationSystem
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FallbackStrategy(Enum):
    """Estratégias de fallback."""
    CONTEXTUAL = "contextual"
    SEMANTIC = "semantic"
    FREQUENCY = "frequency"
    HISTORICAL = "historical"
    HYBRID = "hybrid"


class FallbackQuality(Enum):
    """Qualidade do fallback."""
    EXCELLENT = 0.95
    GOOD = 0.85
    FAIR = 0.70
    POOR = 0.50
    MINIMAL = 0.30


@dataclass
class FallbackOption:
    """Opção de fallback."""
    value: str
    quality: float
    strategy: FallbackStrategy
    confidence: float
    context_relevance: float
    reasoning: str
    alternatives: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FallbackResult:
    """Resultado do sistema de fallback."""
    fallback_options: List[FallbackOption]
    best_fallback: Optional[FallbackOption]
    total_options: int
    avg_quality: float
    fallback_time: float
    strategy_used: FallbackStrategy
    success: bool
    errors: List[str]
    warnings: List[str]
    insights: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.insights is None:
            self.insights = {}


class IntelligentFallbackSystem:
    """Sistema de fallback inteligente avançado."""
    
    def __init__(self):
        """Inicializa o sistema de fallback inteligente."""
        self.fallback_strategies = {
            FallbackStrategy.CONTEXTUAL: self._contextual_fallback,
            FallbackStrategy.SEMANTIC: self._semantic_fallback,
            FallbackStrategy.FREQUENCY: self._frequency_fallback,
            FallbackStrategy.HISTORICAL: self._historical_fallback,
            FallbackStrategy.HYBRID: self._hybrid_fallback
        }
        
        # Base de conhecimento de fallbacks
        self.fallback_knowledge = self._load_fallback_knowledge()
        
        # Histórico de uso
        self.usage_history = defaultdict(lambda: defaultdict(int))
        self.history_max_size = 10000
        
        # Cache de fallbacks
        self.fallback_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Métricas de performance
        self.metrics = {
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "avg_fallback_time": 0.0,
            "fallback_times": deque(maxlen=1000),
            "quality_distribution": defaultdict(int),
            "strategy_usage": defaultdict(int)
        }
        
        logger.info("IntelligentFallbackSystem inicializado")
    
    def _load_fallback_knowledge(self) -> Dict[str, Any]:
        """Carrega base de conhecimento de fallbacks."""
        return {
            "keyword_fallbacks": {
                "tecnologia": ["programação", "desenvolvimento", "software", "tecnologia", "digital", "inovação"],
                "saúde": ["medicina", "bem-estar", "fitness", "nutrição", "saúde", "vida"],
                "negócios": ["empreendedorismo", "marketing", "vendas", "gestão", "negócios", "lucro"],
                "educação": ["aprendizado", "estudo", "curso", "treinamento", "educação", "conhecimento"],
                "lazer": ["entretenimento", "hobby", "viagem", "esporte", "lazer", "diversão"]
            },
            "audience_fallbacks": {
                "iniciante": ["novato", "principiante", "básico", "introdutório", "iniciante"],
                "intermediário": ["intermediário", "médio", "experiente", "avançado"],
                "avançado": ["expert", "profissional", "especialista", "avançado"],
                "empresarial": ["empresa", "negócio", "corporativo", "profissional", "comercial"]
            },
            "content_type_fallbacks": {
                "artigo": ["post", "texto", "conteúdo", "material", "artigo"],
                "tutorial": ["guia", "instrução", "passo-a-passo", "tutorial", "manual"],
                "anúncio": ["promoção", "oferta", "publicidade", "anúncio", "propaganda"],
                "notícia": ["informação", "atualização", "notícia", "reportagem", "informe"]
            },
            "tone_fallbacks": {
                "formal": ["profissional", "técnico", "acadêmico", "formal", "sério"],
                "casual": ["descontraído", "amigável", "informal", "casual", "leve"],
                "urgente": ["importante", "crítico", "urgente", "prioritário", "essencial"],
                "neutro": ["equilibrado", "neutro", "objetivo", "imparcial", "balanceado"]
            },
            "generic_fallbacks": {
                "keyword": ["palavra-chave", "termo", "conceito", "expressão"],
                "audience": ["público", "usuários", "leitores", "audiência"],
                "content": ["conteúdo", "material", "texto", "informação"],
                "tone": ["tom", "estilo", "abordagem", "linguagem"]
            }
        }
    
    def generate_fallbacks(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext] = None, 
                          strategy: FallbackStrategy = FallbackStrategy.HYBRID) -> FallbackResult:
        """
        Gera opções de fallback para uma lacuna.
        
        Args:
            text: Texto completo
            gap: Lacuna detectada
            semantic_context: Contexto semântico (opcional)
            strategy: Estratégia de fallback
            
        Returns:
            Resultado com opções de fallback
        """
        start_time = time.time()
        
        try:
            # Verificar cache
            cache_key = f"{hash(text)}:{gap.start_pos}:{gap.end_pos}:{strategy.value}"
            if cache_key in self.fallback_cache:
                return self.fallback_cache[cache_key]
            
            # Gerar opções de fallback
            fallback_options = []
            errors = []
            warnings = []
            
            # Usar estratégia de fallback apropriada
            fallback_function = self.fallback_strategies.get(strategy, self._hybrid_fallback)
            
            try:
                options = fallback_function(text, gap, semantic_context)
                fallback_options.extend(options)
            except Exception as e:
                error_msg = f"Erro na estratégia {strategy.value}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
            
            # Se não há opções, usar fallback genérico
            if not fallback_options:
                warnings.append("Usando fallback genérico devido à falta de opções específicas")
                fallback_options = self._generate_generic_fallbacks(gap)
            
            # Rankear opções por qualidade
            ranked_options = self._rank_fallback_options(fallback_options, gap, semantic_context)
            
            # Selecionar melhor opção
            best_fallback = ranked_options[0] if ranked_options else None
            
            # Calcular métricas
            total_options = len(ranked_options)
            avg_quality = statistics.mean([opt.quality for opt in ranked_options]) if ranked_options else 0.0
            
            # Gerar insights
            insights = self._generate_fallback_insights(ranked_options, strategy)
            
            # Atualizar histórico
            if best_fallback:
                self._update_usage_history(gap, best_fallback.value)
            
            result = FallbackResult(
                fallback_options=ranked_options,
                best_fallback=best_fallback,
                total_options=total_options,
                avg_quality=avg_quality,
                fallback_time=time.time() - start_time,
                strategy_used=strategy,
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                insights=insights
            )
            
            # Armazenar no cache
            self.fallback_cache[cache_key] = result
            
            # Atualizar métricas
            self._update_metrics(total_options, time.time() - start_time, avg_quality, strategy)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no sistema de fallback: {e}")
            
            result = FallbackResult(
                fallback_options=[],
                best_fallback=None,
                total_options=0,
                avg_quality=0.0,
                fallback_time=time.time() - start_time,
                strategy_used=strategy,
                success=False,
                errors=[str(e)],
                warnings=[],
                insights={}
            )
            
            self._update_metrics(0, time.time() - start_time, 0.0, strategy)
            
            return result
    
    def _contextual_fallback(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> List[FallbackOption]:
        """Gera fallbacks baseados no contexto."""
        options = []
        placeholder_type = gap.placeholder_type.value
        
        # Extrair contexto local
        context_text = self._extract_context_for_fallback(text, gap)
        
        # Detectar tópico do contexto
        detected_topic = self._detect_context_topic(context_text)
        
        # Buscar fallbacks baseados no tópico
        if "keyword" in placeholder_type:
            topic_fallbacks = self.fallback_knowledge["keyword_fallbacks"].get(detected_topic, [])
            for fallback in topic_fallbacks:
                option = FallbackOption(
                    value=fallback,
                    quality=0.8,
                    strategy=FallbackStrategy.CONTEXTUAL,
                    confidence=0.7,
                    context_relevance=0.8,
                    reasoning=f"Fallback baseado no tópico '{detected_topic}' detectado no contexto",
                    alternatives=topic_fallbacks[:3],
                    metadata={"topic": detected_topic, "context_text": context_text[:100]}
                )
                options.append(option)
        
        # Buscar fallbacks baseados em outros aspectos do contexto
        if "audience" in placeholder_type:
            audience_fallbacks = self._get_audience_fallbacks_from_context(context_text)
            for fallback in audience_fallbacks:
                option = FallbackOption(
                    value=fallback,
                    quality=0.7,
                    strategy=FallbackStrategy.CONTEXTUAL,
                    confidence=0.6,
                    context_relevance=0.7,
                    reasoning="Fallback baseado na audiência detectada no contexto",
                    alternatives=audience_fallbacks[:3],
                    metadata={"context_text": context_text[:100]}
                )
                options.append(option)
        
        return options
    
    def _semantic_fallback(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> List[FallbackOption]:
        """Gera fallbacks baseados em análise semântica."""
        options = []
        placeholder_type = gap.placeholder_type.value
        
        if not semantic_context:
            return options
        
        # Usar informações semânticas para gerar fallbacks
        if "keyword" in placeholder_type and semantic_context.keywords:
            for keyword in semantic_context.keywords[:3]:
                option = FallbackOption(
                    value=keyword,
                    quality=0.9,
                    strategy=FallbackStrategy.SEMANTIC,
                    confidence=0.8,
                    context_relevance=0.9,
                    reasoning=f"Fallback semântico baseado na palavra-chave '{keyword}' extraída do contexto",
                    alternatives=semantic_context.keywords[:3],
                    metadata={"semantic_keywords": semantic_context.keywords}
                )
                options.append(option)
        
        # Usar tópico semântico
        if semantic_context.topic != "geral":
            topic_fallbacks = self.fallback_knowledge["keyword_fallbacks"].get(semantic_context.topic, [])
            for fallback in topic_fallbacks[:2]:
                option = FallbackOption(
                    value=fallback,
                    quality=0.8,
                    strategy=FallbackStrategy.SEMANTIC,
                    confidence=0.7,
                    context_relevance=0.8,
                    reasoning=f"Fallback semântico baseado no tópico '{semantic_context.topic}'",
                    alternatives=topic_fallbacks[:3],
                    metadata={"semantic_topic": semantic_context.topic}
                )
                options.append(option)
        
        # Usar intenção semântica
        if semantic_context.intent != "informar":
            intent_fallbacks = self._get_intent_based_fallbacks(semantic_context.intent, placeholder_type)
            for fallback in intent_fallbacks:
                option = FallbackOption(
                    value=fallback,
                    quality=0.7,
                    strategy=FallbackStrategy.SEMANTIC,
                    confidence=0.6,
                    context_relevance=0.7,
                    reasoning=f"Fallback semântico baseado na intenção '{semantic_context.intent}'",
                    alternatives=intent_fallbacks[:3],
                    metadata={"semantic_intent": semantic_context.intent}
                )
                options.append(option)
        
        return options
    
    def _frequency_fallback(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> List[FallbackOption]:
        """Gera fallbacks baseados em frequência de uso."""
        options = []
        placeholder_type = gap.placeholder_type.value
        
        # Usar fallbacks mais frequentes
        frequent_fallbacks = self._get_frequent_fallbacks(placeholder_type)
        
        for i, fallback in enumerate(frequent_fallbacks):
            # Score baseado na posição (mais frequente = melhor)
            quality = 0.9 - (i * 0.1)
            
            option = FallbackOption(
                value=fallback,
                quality=max(0.5, quality),
                strategy=FallbackStrategy.FREQUENCY,
                confidence=0.8 - (i * 0.1),
                context_relevance=0.6,
                reasoning=f"Fallback baseado em frequência de uso (posição {i+1})",
                alternatives=frequent_fallbacks[:3],
                metadata={"frequency_rank": i + 1}
            )
            options.append(option)
        
        return options
    
    def _historical_fallback(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> List[FallbackOption]:
        """Gera fallbacks baseados no histórico de uso."""
        options = []
        placeholder_type = gap.placeholder_type.value
        
        # Buscar histórico de uso para este tipo de placeholder
        history_key = f"{placeholder_type}_{gap.placeholder_name}"
        usage_history = self.usage_history[history_key]
        
        if usage_history:
            # Ordenar por frequência de uso
            sorted_history = sorted(usage_history.items(), key=lambda x: x[1], reverse=True)
            
            for i, (value, frequency) in enumerate(sorted_history[:5]):
                # Score baseado na frequência histórica
                quality = min(0.9, 0.5 + (frequency / 10.0))
                
                option = FallbackOption(
                    value=value,
                    quality=quality,
                    strategy=FallbackStrategy.HISTORICAL,
                    confidence=0.7 + (frequency / 20.0),
                    context_relevance=0.6,
                    reasoning=f"Fallback histórico baseado em uso anterior (frequência: {frequency})",
                    alternatives=[item[0] for item in sorted_history[:3]],
                    metadata={"historical_frequency": frequency, "historical_rank": i + 1}
                )
                options.append(option)
        
        return options
    
    def _hybrid_fallback(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> List[FallbackOption]:
        """Gera fallbacks usando estratégia híbrida."""
        all_options = []
        
        # Combinar todas as estratégias
        strategies = [
            self._contextual_fallback,
            self._semantic_fallback,
            self._frequency_fallback,
            self._historical_fallback
        ]
        
        for strategy in strategies:
            try:
                options = strategy(text, gap, semantic_context)
                all_options.extend(options)
            except Exception as e:
                logger.warning(f"Estratégia {strategy.__name__} falhou: {e}")
                continue
        
        # Remover duplicatas mantendo a melhor qualidade
        unique_options = {}
        for option in all_options:
            if option.value not in unique_options or option.quality > unique_options[option.value].quality:
                unique_options[option.value] = option
        
        return list(unique_options.values())
    
    def _generate_generic_fallbacks(self, gap: DetectedGap) -> List[FallbackOption]:
        """Gera fallbacks genéricos quando não há opções específicas."""
        options = []
        placeholder_type = gap.placeholder_type.value
        
        # Determinar categoria genérica
        if "keyword" in placeholder_type:
            category = "keyword"
        elif "audience" in placeholder_type:
            category = "audience"
        elif "content" in placeholder_type:
            category = "content"
        elif "tone" in placeholder_type:
            category = "tone"
        else:
            category = "keyword"
        
        # Usar fallbacks genéricos
        generic_fallbacks = self.fallback_knowledge["generic_fallbacks"].get(category, ["valor_padrão"])
        
        for fallback in generic_fallbacks:
            option = FallbackOption(
                value=fallback,
                quality=0.5,
                strategy=FallbackStrategy.FREQUENCY,
                confidence=0.5,
                context_relevance=0.5,
                reasoning="Fallback genérico devido à falta de opções específicas",
                alternatives=generic_fallbacks[:3],
                metadata={"fallback_type": "generic", "category": category}
            )
            options.append(option)
        
        return options
    
    def _extract_context_for_fallback(self, text: str, gap: DetectedGap) -> str:
        """Extrai contexto para fallback."""
        # Extrair texto ao redor da lacuna
        start = max(0, gap.start_pos - 150)
        end = min(len(text), gap.end_pos + 150)
        return text[start:end]
    
    def _detect_context_topic(self, context_text: str) -> str:
        """Detecta tópico do contexto."""
        context_lower = context_text.lower()
        
        for topic, keywords in self.fallback_knowledge["keyword_fallbacks"].items():
            if any(keyword in context_lower for keyword in keywords):
                return topic
        
        return "geral"
    
    def _get_audience_fallbacks_from_context(self, context_text: str) -> List[str]:
        """Obtém fallbacks de audiência do contexto."""
        context_lower = context_text.lower()
        
        for audience, keywords in self.fallback_knowledge["audience_fallbacks"].items():
            if any(keyword in context_lower for keyword in keywords):
                return keywords[:3]
        
        return self.fallback_knowledge["audience_fallbacks"].get("geral", ["público"])
    
    def _get_intent_based_fallbacks(self, intent: str, placeholder_type: str) -> List[str]:
        """Obtém fallbacks baseados na intenção."""
        if "tone" in placeholder_type:
            return self._get_tone_by_intent(intent)
        else:
            return self.fallback_knowledge["generic_fallbacks"].get("keyword", ["palavra-chave"])
    
    def _get_tone_by_intent(self, intent: str) -> List[str]:
        """Obtém tom baseado na intenção."""
        tone_mapping = {
            "informar": ["neutro", "formal"],
            "persuadir": ["urgente", "casual"],
            "instruir": ["formal", "neutro"],
            "entreter": ["casual", "descontraído"]
        }
        
        tones = tone_mapping.get(intent, ["neutro"])
        return [self.fallback_knowledge["tone_fallbacks"].get(tone, [tone])[0] for tone in tones]
    
    def _get_frequent_fallbacks(self, placeholder_type: str) -> List[str]:
        """Obtém fallbacks mais frequentes."""
        if "keyword" in placeholder_type:
            return ["palavra-chave", "termo", "conceito", "expressão"]
        elif "audience" in placeholder_type:
            return ["público", "usuários", "leitores", "audiência"]
        elif "content" in placeholder_type:
            return ["conteúdo", "material", "texto", "informação"]
        elif "tone" in placeholder_type:
            return ["tom", "estilo", "abordagem", "linguagem"]
        else:
            return ["valor_padrão"]
    
    def _rank_fallback_options(self, options: List[FallbackOption], gap: DetectedGap, 
                              semantic_context: Optional[SemanticContext]) -> List[FallbackOption]:
        """Rankeia opções de fallback por qualidade."""
        if not options:
            return []
        
        # Calcular score composto para cada opção
        for option in options:
            composite_score = (
                option.quality * 0.4 +
                option.confidence * 0.3 +
                option.context_relevance * 0.3
            )
            option.quality = min(1.0, composite_score)
        
        # Ordenar por qualidade
        ranked_options = sorted(options, key=lambda x: x.quality, reverse=True)
        
        return ranked_options
    
    def _generate_fallback_insights(self, options: List[FallbackOption], strategy: FallbackStrategy) -> Dict[str, Any]:
        """Gera insights sobre os fallbacks."""
        if not options:
            return {}
        
        # Distribuição de estratégias
        strategy_distribution = defaultdict(int)
        for option in options:
            strategy_distribution[option.strategy.value] += 1
        
        # Qualidade média por estratégia
        quality_by_strategy = defaultdict(list)
        for option in options:
            quality_by_strategy[option.strategy.value].append(option.quality)
        
        avg_quality_by_strategy = {}
        for strategy_name, qualities in quality_by_strategy.items():
            avg_quality_by_strategy[strategy_name] = statistics.mean(qualities)
        
        # Top fallbacks
        top_fallbacks = [opt.value for opt in options[:5]]
        
        return {
            "strategy_distribution": dict(strategy_distribution),
            "avg_quality_by_strategy": avg_quality_by_strategy,
            "top_fallbacks": top_fallbacks,
            "avg_quality": statistics.mean([opt.quality for opt in options]),
            "avg_confidence": statistics.mean([opt.confidence for opt in options])
        }
    
    def _update_usage_history(self, gap: DetectedGap, value: str):
        """Atualiza histórico de uso."""
        history_key = f"{gap.placeholder_type.value}_{gap.placeholder_name}"
        self.usage_history[history_key][value] += 1
        
        # Limitar tamanho do histórico
        if len(self.usage_history[history_key]) > self.history_max_size:
            # Remover itens menos frequentes
            sorted_items = sorted(self.usage_history[history_key].items(), key=lambda x: x[1])
            items_to_remove = len(sorted_items) - self.history_max_size
            for i in range(items_to_remove):
                del self.usage_history[history_key][sorted_items[i][0]]
    
    def _update_metrics(self, options_count: int, fallback_time: float, avg_quality: float, strategy: FallbackStrategy):
        """Atualiza métricas de performance."""
        self.metrics["total_fallbacks"] += 1
        
        if options_count > 0:
            self.metrics["successful_fallbacks"] += 1
            self.metrics["fallback_times"].append(fallback_time)
            self.metrics["avg_fallback_time"] = statistics.mean(self.metrics["fallback_times"])
            
            # Distribuição de qualidade
            quality_level = self._get_quality_level(avg_quality)
            self.metrics["quality_distribution"][quality_level] += 1
            
            # Uso de estratégias
            self.metrics["strategy_usage"][strategy.value] += 1
        else:
            self.metrics["failed_fallbacks"] += 1
    
    def _get_quality_level(self, quality: float) -> str:
        """Converte valor de qualidade em nível."""
        if quality >= 0.9:
            return "excelente"
        elif quality >= 0.8:
            return "bom"
        elif quality >= 0.7:
            return "justo"
        elif quality >= 0.5:
            return "ruim"
        else:
            return "mínimo"


# Funções de conveniência
def generate_fallbacks(text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext] = None, 
                      strategy: FallbackStrategy = FallbackStrategy.HYBRID) -> FallbackResult:
    """Função de conveniência para geração de fallbacks."""
    fallback_system = IntelligentFallbackSystem()
    return fallback_system.generate_fallbacks(text, gap, semantic_context, strategy)


def get_fallback_system_stats() -> Dict[str, Any]:
    """Obtém estatísticas do sistema de fallback."""
    fallback_system = IntelligentFallbackSystem()
    return fallback_system.metrics


if __name__ == "__main__":
    # Teste básico do sistema
    test_text = """
    Preciso criar um artigo sobre {primary_keyword} para o público {target_audience}.
    O conteúdo deve ser {content_type} com tom {tone}.
    """
    
    # Simular lacuna
    test_gap = DetectedGap(
        placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
        placeholder_name="primary_keyword",
        start_pos=35,
        end_pos=52,
        context="artigo sobre {primary_keyword}",
        confidence=0.9,
        detection_method=DetectionMethod.REGEX,
        validation_level=ValidationLevel.BASIC
    )
    
    # Simular contexto semântico
    test_semantic_context = SemanticContext(
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
    
    # Gerar fallbacks
    result = generate_fallbacks(test_text, test_gap, test_semantic_context)
    
    print(f"Opções de fallback geradas: {result.total_options}")
    print(f"Qualidade média: {result.avg_quality:.2f}")
    print(f"Tempo de geração: {result.fallback_time:.3f}s")
    
    if result.best_fallback:
        print(f"Melhor fallback: {result.best_fallback.value}")
        print(f"Qualidade: {result.best_fallback.quality:.2f}")
        print(f"Raciocínio: {result.best_fallback.reasoning}")
        print(f"Alternativas: {result.best_fallback.alternatives}")
    
    # Mostrar insights
    print("\nInsights:")
    for key, value in result.insights.items():
        print(f"  {key}: {value}") 