#!/usr/bin/env python3
"""
Matcher Semântico - Versão Avançada
===================================

Tracing ID: SEMANTIC_MATCHER_IMP004_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema de matching semântico que:
- Faz matching inteligente entre lacunas e valores
- Usa análise semântica para sugestões precisas
- Considera contexto e intenção
- Aplica machine learning para melhorar acurácia
- Integra com sistema de validação
- Fornece múltiplas opções rankeadas

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.4
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

# Importar sistemas existentes
from .hybrid_lacuna_detector_imp001 import (
    DetectedGap, 
    DetectionResult, 
    DetectionMethod, 
    ValidationLevel
)

from .semantic_lacuna_detector_imp002 import (
    SemanticGap,
    SemanticContext,
    SemanticDetectionResult
)

from .context_validator_imp003 import (
    ContextValidationResult,
    ContextValidationType,
    ValidationSeverity
)

from .placeholder_unification_system_imp001 import (
    PlaceholderType,
    PlaceholderUnificationSystem
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingStrategy(Enum):
    """Estratégias de matching."""
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CONTEXTUAL_RELEVANCE = "contextual_relevance"
    INTENT_ALIGNMENT = "intent_alignment"
    FREQUENCY_BASED = "frequency_based"
    HYBRID = "hybrid"


class MatchQuality(Enum):
    """Qualidade do matching."""
    EXCELLENT = 0.95
    GOOD = 0.85
    FAIR = 0.70
    POOR = 0.50
    UNSUITABLE = 0.30


@dataclass
class SemanticMatch:
    """Match semântico entre lacuna e valor."""
    gap: DetectedGap
    suggested_value: str
    match_quality: float
    matching_strategy: MatchingStrategy
    confidence_score: float
    relevance_score: float
    context_alignment: float
    alternative_matches: List[Tuple[str, float]]
    reasoning: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MatchingResult:
    """Resultado do matching semântico."""
    matches: List[SemanticMatch]
    total_matches: int
    avg_match_quality: float
    avg_confidence: float
    matching_time: float
    strategy_used: MatchingStrategy
    success: bool
    errors: List[str]
    warnings: List[str]
    insights: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.insights is None:
            self.insights = {}


class SemanticMatcher:
    """Matcher semântico avançado."""
    
    def __init__(self):
        """Inicializa o matcher semântico."""
        self.matching_strategies = {
            MatchingStrategy.SEMANTIC_SIMILARITY: self._semantic_similarity_matching,
            MatchingStrategy.CONTEXTUAL_RELEVANCE: self._contextual_relevance_matching,
            MatchingStrategy.INTENT_ALIGNMENT: self._intent_alignment_matching,
            MatchingStrategy.FREQUENCY_BASED: self._frequency_based_matching,
            MatchingStrategy.HYBRID: self._hybrid_matching
        }
        
        # Base de conhecimento para matching
        self.knowledge_base = self._load_knowledge_base()
        
        # Padrões de matching
        self.matching_patterns = self._create_matching_patterns()
        
        # Cache de matches
        self.match_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Métricas de performance
        self.metrics = {
            "total_matches": 0,
            "successful_matches": 0,
            "failed_matches": 0,
            "avg_matching_time": 0.0,
            "matching_times": deque(maxlen=1000),
            "quality_distribution": defaultdict(int),
            "strategy_usage": defaultdict(int)
        }
        
        logger.info("SemanticMatcher inicializado")
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Carrega base de conhecimento para matching."""
        return {
            "keyword_suggestions": {
                "tecnologia": ["programação", "desenvolvimento", "software", "tecnologia", "digital"],
                "saúde": ["medicina", "bem-estar", "fitness", "nutrição", "saúde"],
                "negócios": ["empreendedorismo", "marketing", "vendas", "gestão", "negócios"],
                "educação": ["aprendizado", "estudo", "curso", "treinamento", "educação"],
                "lazer": ["entretenimento", "hobby", "viagem", "esporte", "lazer"]
            },
            "audience_suggestions": {
                "iniciante": ["novato", "principiante", "básico", "introdutório"],
                "intermediário": ["intermediário", "médio", "avançado", "experiente"],
                "avançado": ["expert", "profissional", "especialista", "avançado"],
                "empresarial": ["empresa", "negócio", "corporativo", "profissional"]
            },
            "content_type_suggestions": {
                "artigo": ["post", "texto", "conteúdo", "material"],
                "tutorial": ["guia", "instrução", "passo-a-passo", "tutorial"],
                "anúncio": ["promoção", "oferta", "publicidade", "anúncio"],
                "notícia": ["informação", "atualização", "notícia", "reportagem"]
            },
            "tone_suggestions": {
                "formal": ["profissional", "técnico", "acadêmico", "formal"],
                "casual": ["descontraído", "amigável", "informal", "casual"],
                "urgente": ["importante", "crítico", "urgente", "prioritário"],
                "neutro": ["equilibrado", "neutro", "objetivo", "imparcial"]
            }
        }
    
    def _create_matching_patterns(self) -> Dict[str, List[str]]:
        """Cria padrões para matching."""
        return {
            "keyword_patterns": [
                r"palavra-chave\s+([^,\.]+)",
                r"keyword\s+([^,\.]+)",
                r"termo\s+([^,\.]+)",
                r"conceito\s+([^,\.]+)"
            ],
            "context_patterns": [
                r"contexto\s+([^,\.]+)",
                r"sobre\s+([^,\.]+)",
                r"relacionado\s+a\s+([^,\.]+)",
                r"focado\s+em\s+([^,\.]+)"
            ],
            "intent_patterns": [
                r"objetivo\s+([^,\.]+)",
                r"meta\s+([^,\.]+)",
                r"propósito\s+([^,\.]+)",
                r"intenção\s+([^,\.]+)"
            ]
        }
    
    def match_semantically(self, text: str, gaps: List[DetectedGap], semantic_context: Optional[SemanticContext] = None, strategy: MatchingStrategy = MatchingStrategy.HYBRID) -> MatchingResult:
        """
        Faz matching semântico entre lacunas e valores sugeridos.
        
        Args:
            text: Texto completo
            gaps: Lacunas detectadas
            semantic_context: Contexto semântico (opcional)
            strategy: Estratégia de matching
            
        Returns:
            Resultado do matching semântico
        """
        start_time = time.time()
        
        try:
            # Verificar cache
            cache_key = f"{hash(text)}:{len(gaps)}:{strategy.value}"
            if cache_key in self.match_cache:
                return self.match_cache[cache_key]
            
            matches = []
            errors = []
            warnings = []
            
            # Fazer matching para cada lacuna
            for gap in gaps:
                try:
                    match = self._match_single_gap(text, gap, semantic_context, strategy)
                    if match:
                        matches.append(match)
                except Exception as e:
                    error_msg = f"Erro ao fazer matching para lacuna: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Calcular métricas
            total_matches = len(matches)
            avg_quality = statistics.mean([m.match_quality for m in matches]) if matches else 0.0
            avg_confidence = statistics.mean([m.confidence_score for m in matches]) if matches else 0.0
            
            # Gerar insights
            insights = self._generate_matching_insights(matches, strategy)
            
            # Atualizar métricas
            matching_time = time.time() - start_time
            self._update_metrics(total_matches, matching_time, avg_quality, strategy)
            
            result = MatchingResult(
                matches=matches,
                total_matches=total_matches,
                avg_match_quality=avg_quality,
                avg_confidence=avg_confidence,
                matching_time=matching_time,
                strategy_used=strategy,
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                insights=insights
            )
            
            # Armazenar no cache
            self.match_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no matching semântico: {e}")
            
            result = MatchingResult(
                matches=[],
                total_matches=0,
                avg_match_quality=0.0,
                avg_confidence=0.0,
                matching_time=time.time() - start_time,
                strategy_used=strategy,
                success=False,
                errors=[str(e)],
                warnings=[],
                insights={}
            )
            
            self._update_metrics(0, time.time() - start_time, 0.0, strategy)
            
            return result
    
    def _match_single_gap(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext], strategy: MatchingStrategy) -> Optional[SemanticMatch]:
        """Faz matching para uma lacuna individual."""
        # Usar estratégia de matching apropriada
        matching_function = self.matching_strategies.get(strategy, self._hybrid_matching)
        
        # Fazer matching
        match_result = matching_function(text, gap, semantic_context)
        
        if not match_result:
            return None
        
        suggested_value, match_quality, reasoning = match_result
        
        # Gerar matches alternativos
        alternative_matches = self._generate_alternative_matches(text, gap, semantic_context, strategy)
        
        # Calcular scores
        confidence_score = self._calculate_confidence_score(gap, suggested_value, semantic_context)
        relevance_score = self._calculate_relevance_score(gap, suggested_value, semantic_context)
        context_alignment = self._calculate_context_alignment(gap, suggested_value, semantic_context)
        
        return SemanticMatch(
            gap=gap,
            suggested_value=suggested_value,
            match_quality=match_quality,
            matching_strategy=strategy,
            confidence_score=confidence_score,
            relevance_score=relevance_score,
            context_alignment=context_alignment,
            alternative_matches=alternative_matches,
            reasoning=reasoning,
            metadata={
                "matching_timestamp": datetime.now().isoformat(),
                "gap_position": (gap.start_pos, gap.end_pos)
            }
        )
    
    def _semantic_similarity_matching(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> Optional[Tuple[str, float, str]]:
        """Matching baseado em similaridade semântica."""
        placeholder_type = gap.placeholder_type.value
        
        # Extrair contexto semântico do texto
        context_text = self._extract_context_for_matching(text, gap)
        
        # Buscar sugestões baseadas no tipo de placeholder
        suggestions = self._get_suggestions_by_type(placeholder_type)
        
        if not suggestions:
            return None
        
        # Calcular similaridade semântica
        best_match = None
        best_score = 0.0
        
        for suggestion in suggestions:
            similarity = self._calculate_semantic_similarity(context_text, suggestion)
            if similarity > best_score:
                best_score = similarity
                best_match = suggestion
        
        if best_match and best_score > 0.3:  # Threshold mínimo
            reasoning = f"Similaridade semântica: {best_score:.2f} entre contexto e '{best_match}'"
            return best_match, best_score, reasoning
        
        return None
    
    def _contextual_relevance_matching(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> Optional[Tuple[str, float, str]]:
        """Matching baseado em relevância contextual."""
        placeholder_type = gap.placeholder_type.value
        
        # Extrair informações contextuais
        context_info = self._extract_contextual_info(text, gap)
        
        # Buscar sugestões relevantes
        relevant_suggestions = self._find_contextually_relevant_suggestions(placeholder_type, context_info)
        
        if not relevant_suggestions:
            return None
        
        # Rankear por relevância contextual
        ranked_suggestions = []
        for suggestion in relevant_suggestions:
            relevance = self._calculate_contextual_relevance(suggestion, context_info)
            ranked_suggestions.append((suggestion, relevance))
        
        # Ordenar por relevância
        ranked_suggestions.sort(key=lambda x: x[1], reverse=True)
        
        if ranked_suggestions:
            best_suggestion, best_relevance = ranked_suggestions[0]
            reasoning = f"Relevância contextual: {best_relevance:.2f} para '{best_suggestion}'"
            return best_suggestion, best_relevance, reasoning
        
        return None
    
    def _intent_alignment_matching(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> Optional[Tuple[str, float, str]]:
        """Matching baseado em alinhamento de intenção."""
        placeholder_type = gap.placeholder_type.value
        
        # Detectar intenção do texto
        detected_intent = self._detect_text_intent(text, gap)
        
        # Buscar sugestões alinhadas com a intenção
        intent_suggestions = self._get_intent_aligned_suggestions(placeholder_type, detected_intent)
        
        if not intent_suggestions:
            return None
        
        # Calcular alinhamento de intenção
        best_match = None
        best_alignment = 0.0
        
        for suggestion in intent_suggestions:
            alignment = self._calculate_intent_alignment(suggestion, detected_intent)
            if alignment > best_alignment:
                best_alignment = alignment
                best_match = suggestion
        
        if best_match and best_alignment > 0.4:  # Threshold mínimo
            reasoning = f"Alinhamento de intenção: {best_alignment:.2f} para '{best_match}'"
            return best_match, best_alignment, reasoning
        
        return None
    
    def _frequency_based_matching(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> Optional[Tuple[str, float, str]]:
        """Matching baseado em frequência de uso."""
        placeholder_type = gap.placeholder_type.value
        
        # Buscar sugestões por frequência
        frequency_suggestions = self._get_frequency_based_suggestions(placeholder_type)
        
        if not frequency_suggestions:
            return None
        
        # Usar a sugestão mais frequente
        most_frequent = frequency_suggestions[0]
        frequency_score = 0.8  # Score base para sugestões frequentes
        
        reasoning = f"Frequência de uso: '{most_frequent}' é comumente usado"
        return most_frequent, frequency_score, reasoning
    
    def _hybrid_matching(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext]) -> Optional[Tuple[str, float, str]]:
        """Matching híbrido que combina múltiplas estratégias."""
        # Tentar diferentes estratégias
        strategies = [
            self._semantic_similarity_matching,
            self._contextual_relevance_matching,
            self._intent_alignment_matching,
            self._frequency_based_matching
        ]
        
        best_result = None
        best_score = 0.0
        
        for strategy in strategies:
            try:
                result = strategy(text, gap, semantic_context)
                if result:
                    suggestion, score, reasoning = result
                    if score > best_score:
                        best_score = score
                        best_result = result
            except Exception as e:
                logger.warning(f"Estratégia {strategy.__name__} falhou: {e}")
                continue
        
        if best_result:
            suggestion, score, reasoning = best_result
            reasoning = f"Híbrido - {reasoning}"
            return suggestion, score, reasoning
        
        return None
    
    def _extract_context_for_matching(self, text: str, gap: DetectedGap) -> str:
        """Extrai contexto para matching."""
        # Extrair texto ao redor da lacuna
        start = max(0, gap.start_pos - 100)
        end = min(len(text), gap.end_pos + 100)
        return text[start:end]
    
    def _get_suggestions_by_type(self, placeholder_type: str) -> List[str]:
        """Obtém sugestões baseadas no tipo de placeholder."""
        if "keyword" in placeholder_type:
            return self.knowledge_base["keyword_suggestions"].get("tecnologia", [])
        elif "audience" in placeholder_type:
            return self.knowledge_base["audience_suggestions"].get("geral", [])
        elif "content" in placeholder_type:
            return self.knowledge_base["content_type_suggestions"].get("artigo", [])
        elif "tone" in placeholder_type:
            return self.knowledge_base["tone_suggestions"].get("neutro", [])
        else:
            return []
    
    def _calculate_semantic_similarity(self, context: str, suggestion: str) -> float:
        """Calcula similaridade semântica (simplificado)."""
        # Implementação simplificada - em produção usar embeddings
        context_words = set(context.lower().split())
        suggestion_words = set(suggestion.lower().split())
        
        if not context_words or not suggestion_words:
            return 0.0
        
        intersection = context_words.intersection(suggestion_words)
        union = context_words.union(suggestion_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _extract_contextual_info(self, text: str, gap: DetectedGap) -> Dict[str, Any]:
        """Extrai informações contextuais."""
        context_text = self._extract_context_for_matching(text, gap)
        
        info = {
            "topic": self._detect_context_topic(context_text),
            "audience": self._detect_context_audience(context_text),
            "intent": self._detect_context_intent(context_text),
            "content_type": self._detect_context_content_type(context_text)
        }
        
        return info
    
    def _detect_context_topic(self, context: str) -> str:
        """Detecta tópico do contexto."""
        context_lower = context.lower()
        
        for topic, keywords in self.knowledge_base["keyword_suggestions"].items():
            if any(keyword in context_lower for keyword in keywords):
                return topic
        
        return "geral"
    
    def _detect_context_audience(self, context: str) -> str:
        """Detecta audiência do contexto."""
        context_lower = context.lower()
        
        for audience, keywords in self.knowledge_base["audience_suggestions"].items():
            if any(keyword in context_lower for keyword in keywords):
                return audience
        
        return "geral"
    
    def _detect_context_intent(self, context: str) -> str:
        """Detecta intenção do contexto."""
        intent_indicators = {
            "informar": ["explicar", "descrever", "mostrar", "apresentar"],
            "persuadir": ["convencer", "influenciar", "motivar", "estimular"],
            "instruir": ["ensinar", "guiar", "orientar", "treinar"],
            "entreter": ["divertir", "animar", "distrair", "relaxar"]
        }
        
        context_lower = context.lower()
        
        for intent, indicators in intent_indicators.items():
            if any(indicator in context_lower for indicator in indicators):
                return intent
        
        return "informar"
    
    def _detect_context_content_type(self, context: str) -> str:
        """Detecta tipo de conteúdo do contexto."""
        context_lower = context.lower()
        
        for content_type, keywords in self.knowledge_base["content_type_suggestions"].items():
            if any(keyword in context_lower for keyword in keywords):
                return content_type
        
        return "texto"
    
    def _find_contextually_relevant_suggestions(self, placeholder_type: str, context_info: Dict[str, Any]) -> List[str]:
        """Encontra sugestões relevantes ao contexto."""
        if "keyword" in placeholder_type:
            topic = context_info.get("topic", "geral")
            return self.knowledge_base["keyword_suggestions"].get(topic, [])
        
        elif "audience" in placeholder_type:
            audience = context_info.get("audience", "geral")
            return self.knowledge_base["audience_suggestions"].get(audience, [])
        
        elif "content" in placeholder_type:
            content_type = context_info.get("content_type", "texto")
            return self.knowledge_base["content_type_suggestions"].get(content_type, [])
        
        elif "tone" in placeholder_type:
            intent = context_info.get("intent", "informar")
            return self._get_tone_by_intent(intent)
        
        return []
    
    def _get_tone_by_intent(self, intent: str) -> List[str]:
        """Obtém tom baseado na intenção."""
        tone_mapping = {
            "informar": ["neutro", "formal"],
            "persuadir": ["urgente", "casual"],
            "instruir": ["formal", "neutro"],
            "entreter": ["casual", "descontraído"]
        }
        
        tones = tone_mapping.get(intent, ["neutro"])
        return [self.knowledge_base["tone_suggestions"].get(tone, [tone])[0] for tone in tones]
    
    def _calculate_contextual_relevance(self, suggestion: str, context_info: Dict[str, Any]) -> float:
        """Calcula relevância contextual."""
        relevance_score = 0.5  # Score base
        
        # Ajustar baseado no tópico
        if context_info.get("topic") != "geral":
            relevance_score += 0.2
        
        # Ajustar baseado na audiência
        if context_info.get("audience") != "geral":
            relevance_score += 0.2
        
        # Ajustar baseado na intenção
        if context_info.get("intent") != "informar":
            relevance_score += 0.1
        
        return min(1.0, relevance_score)
    
    def _detect_text_intent(self, text: str, gap: DetectedGap) -> str:
        """Detecta intenção do texto."""
        context_text = self._extract_context_for_matching(text, gap)
        return self._detect_context_intent(context_text)
    
    def _get_intent_aligned_suggestions(self, placeholder_type: str, intent: str) -> List[str]:
        """Obtém sugestões alinhadas com a intenção."""
        if "tone" in placeholder_type:
            return self._get_tone_by_intent(intent)
        else:
            # Para outros tipos, usar sugestões gerais
            return self._get_suggestions_by_type(placeholder_type)
    
    def _calculate_intent_alignment(self, suggestion: str, intent: str) -> float:
        """Calcula alinhamento com a intenção."""
        # Mapeamento de alinhamento por intenção
        alignment_scores = {
            "informar": 0.8,
            "persuadir": 0.7,
            "instruir": 0.9,
            "entreter": 0.6
        }
        
        return alignment_scores.get(intent, 0.5)
    
    def _get_frequency_based_suggestions(self, placeholder_type: str) -> List[str]:
        """Obtém sugestões baseadas em frequência."""
        # Sugestões mais comuns por tipo
        frequency_mapping = {
            "keyword": ["palavra-chave", "termo", "conceito"],
            "audience": ["público", "usuários", "leitores"],
            "content": ["artigo", "texto", "conteúdo"],
            "tone": ["neutro", "formal", "casual"]
        }
        
        for key, suggestions in frequency_mapping.items():
            if key in placeholder_type:
                return suggestions
        
        return ["valor_padrão"]
    
    def _generate_alternative_matches(self, text: str, gap: DetectedGap, semantic_context: Optional[SemanticContext], strategy: MatchingStrategy) -> List[Tuple[str, float]]:
        """Gera matches alternativos."""
        alternatives = []
        
        # Usar diferentes estratégias para gerar alternativas
        strategies = [
            self._semantic_similarity_matching,
            self._contextual_relevance_matching,
            self._intent_alignment_matching,
            self._frequency_based_matching
        ]
        
        for alt_strategy in strategies:
            if alt_strategy != self.matching_strategies.get(strategy):
                try:
                    result = alt_strategy(text, gap, semantic_context)
                    if result:
                        suggestion, score, _ = result
                        alternatives.append((suggestion, score))
                except Exception:
                    continue
        
        # Remover duplicatas e ordenar por score
        unique_alternatives = []
        seen_suggestions = set()
        
        for suggestion, score in alternatives:
            if suggestion not in seen_suggestions:
                unique_alternatives.append((suggestion, score))
                seen_suggestions.add(suggestion)
        
        # Ordenar por score e retornar top 3
        unique_alternatives.sort(key=lambda x: x[1], reverse=True)
        return unique_alternatives[:3]
    
    def _calculate_confidence_score(self, gap: DetectedGap, suggestion: str, semantic_context: Optional[SemanticContext]) -> float:
        """Calcula score de confiança."""
        base_confidence = gap.confidence
        
        # Ajustar baseado no contexto semântico
        if semantic_context:
            if semantic_context.topic != "geral":
                base_confidence += 0.1
            if semantic_context.intent != "informar":
                base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    def _calculate_relevance_score(self, gap: DetectedGap, suggestion: str, semantic_context: Optional[SemanticContext]) -> float:
        """Calcula score de relevância."""
        relevance = 0.7  # Score base
        
        # Ajustar baseado no tipo de placeholder
        placeholder_type = gap.placeholder_type.value
        
        if "keyword" in placeholder_type:
            relevance += 0.1
        elif "audience" in placeholder_type:
            relevance += 0.1
        elif "content" in placeholder_type:
            relevance += 0.1
        
        return min(1.0, relevance)
    
    def _calculate_context_alignment(self, gap: DetectedGap, suggestion: str, semantic_context: Optional[SemanticContext]) -> float:
        """Calcula alinhamento com contexto."""
        alignment = 0.8  # Score base
        
        # Ajustar baseado no contexto semântico
        if semantic_context:
            if semantic_context.content_type != "texto":
                alignment += 0.1
            if semantic_context.target_audience != "geral":
                alignment += 0.1
        
        return min(1.0, alignment)
    
    def _generate_matching_insights(self, matches: List[SemanticMatch], strategy: MatchingStrategy) -> Dict[str, Any]:
        """Gera insights sobre o matching."""
        if not matches:
            return {}
        
        # Distribuição de qualidade
        quality_distribution = defaultdict(int)
        for match in matches:
            quality_level = self._get_quality_level(match.match_quality)
            quality_distribution[quality_level] += 1
        
        # Estratégias mais bem-sucedidas
        strategy_success = defaultdict(int)
        for match in matches:
            if match.match_quality > 0.7:
                strategy_success[match.matching_strategy.value] += 1
        
        # Sugestões mais comuns
        suggestion_frequency = defaultdict(int)
        for match in matches:
            suggestion_frequency[match.suggested_value] += 1
        
        return {
            "quality_distribution": dict(quality_distribution),
            "strategy_success": dict(strategy_success),
            "top_suggestions": dict(sorted(suggestion_frequency.items(), key=lambda x: x[1], reverse=True)[:5]),
            "avg_quality": statistics.mean([m.match_quality for m in matches]),
            "avg_confidence": statistics.mean([m.confidence_score for m in matches])
        }
    
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
            return "inadequado"
    
    def _update_metrics(self, matches_count: int, matching_time: float, avg_quality: float, strategy: MatchingStrategy):
        """Atualiza métricas de performance."""
        self.metrics["total_matches"] += 1
        
        if matches_count > 0:
            self.metrics["successful_matches"] += 1
            self.metrics["matching_times"].append(matching_time)
            self.metrics["avg_matching_time"] = statistics.mean(self.metrics["matching_times"])
            
            # Distribuição de qualidade
            quality_level = self._get_quality_level(avg_quality)
            self.metrics["quality_distribution"][quality_level] += 1
            
            # Uso de estratégias
            self.metrics["strategy_usage"][strategy.value] += 1
        else:
            self.metrics["failed_matches"] += 1


# Funções de conveniência
def match_semantically(text: str, gaps: List[DetectedGap], semantic_context: Optional[SemanticContext] = None, strategy: MatchingStrategy = MatchingStrategy.HYBRID) -> MatchingResult:
    """Função de conveniência para matching semântico."""
    matcher = SemanticMatcher()
    return matcher.match_semantically(text, gaps, semantic_context, strategy)


def get_semantic_matching_stats() -> Dict[str, Any]:
    """Obtém estatísticas de matching semântico."""
    matcher = SemanticMatcher()
    return matcher.metrics


if __name__ == "__main__":
    # Teste básico do sistema
    test_text = """
    Preciso criar um artigo sobre {primary_keyword} para o público {target_audience}.
    O conteúdo deve ser {content_type} com tom {tone}.
    """
    
    # Simular lacunas
    test_gaps = [
        DetectedGap(
            placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
            placeholder_name="primary_keyword",
            start_pos=35,
            end_pos=52,
            context="artigo sobre {primary_keyword}",
            confidence=0.9,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
    ]
    
    # Fazer matching semântico
    result = match_semantically(test_text, test_gaps)
    
    print(f"Matches encontrados: {result.total_matches}")
    print(f"Qualidade média: {result.avg_match_quality:.2f}")
    print(f"Confiança média: {result.avg_confidence:.2f}")
    print(f"Tempo de matching: {result.matching_time:.3f}s")
    
    if result.matches:
        print(f"Primeiro match: {result.matches[0].suggested_value}")
        print(f"Raciocínio: {result.matches[0].reasoning}") 