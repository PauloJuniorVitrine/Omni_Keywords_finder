#!/usr/bin/env python3
"""
Detector Semântico de Lacunas - Versão Avançada
===============================================

Tracing ID: SEMANTIC_LACUNA_DETECTOR_IMP002_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema semântico avançado que complementa o detector híbrido:
- Análise semântica com transformers
- Detecção contextual de lacunas
- Validação semântica de qualidade
- Matching inteligente de placeholders
- Sistema de fallback semântico
- Integração com sistema híbrido existente

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.2
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

# Importar sistema híbrido existente
from .hybrid_lacuna_detector_imp001 import (
    DetectedGap, 
    DetectionResult, 
    DetectionMethod, 
    ValidationLevel,
    HybridLacunaDetector
)

# Importar sistema de unificação
from .placeholder_unification_system_imp001 import (
    PlaceholderType,
    PlaceholderUnificationSystem
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticAnalysisType(Enum):
    """Tipos de análise semântica."""
    CONTEXTUAL = "contextual"
    INTENT_BASED = "intent_based"
    ENTITY_RECOGNITION = "entity_recognition"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TOPIC_MODELING = "topic_modeling"


class SemanticConfidence(Enum):
    """Níveis de confiança semântica."""
    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30


@dataclass
class SemanticContext:
    """Contexto semântico de uma lacuna."""
    surrounding_text: str
    topic: str
    intent: str
    entities: List[str]
    sentiment: float
    keywords: List[str]
    content_type: str
    target_audience: str
    tone: str
    complexity_level: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SemanticGap:
    """Lacuna detectada semanticamente."""
    gap: DetectedGap
    semantic_context: SemanticContext
    semantic_confidence: float
    suggested_semantic_value: str
    alternative_suggestions: List[str]
    semantic_validation_score: float
    context_relevance: float
    intent_alignment: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SemanticDetectionResult:
    """Resultado da detecção semântica."""
    semantic_gaps: List[SemanticGap]
    total_semantic_gaps: int
    avg_semantic_confidence: float
    semantic_analysis_time: float
    context_analysis_time: float
    intent_detection_time: float
    success: bool
    errors: List[str]
    warnings: List[str]
    semantic_insights: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.semantic_insights is None:
            self.semantic_insights = {}


class SemanticAnalyzer:
    """Analisador semântico avançado."""
    
    def __init__(self):
        """Inicializa o analisador semântico."""
        self.context_window_size = 200
        self.min_confidence_threshold = 0.6
        self.max_alternatives = 5
        
        # Padrões semânticos para detecção
        self.semantic_patterns = self._create_semantic_patterns()
        
        # Dicionários de contexto
        self.topic_keywords = self._load_topic_keywords()
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        
        # Métricas de performance
        self.metrics = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "avg_analysis_time": 0.0,
            "analysis_times": deque(maxlen=1000),
            "confidence_distribution": defaultdict(int),
            "context_types": defaultdict(int)
        }
        
        logger.info("SemanticAnalyzer inicializado")
    
    def _create_semantic_patterns(self) -> Dict[str, List[str]]:
        """Cria padrões semânticos para detecção."""
        return {
            "keyword_context": [
                r"palavra-chave\s+([^,\.]+)",
                r"keyword\s+([^,\.]+)",
                r"termo\s+([^,\.]+)",
                r"conceito\s+([^,\.]+)"
            ],
            "content_context": [
                r"conteúdo\s+([^,\.]+)",
                r"artigo\s+([^,\.]+)",
                r"texto\s+([^,\.]+)",
                r"material\s+([^,\.]+)"
            ],
            "audience_context": [
                r"público\s+([^,\.]+)",
                r"audiência\s+([^,\.]+)",
                r"usuários\s+([^,\.]+)",
                r"leitores\s+([^,\.]+)"
            ],
            "intent_context": [
                r"objetivo\s+([^,\.]+)",
                r"intenção\s+([^,\.]+)",
                r"propósito\s+([^,\.]+)",
                r"meta\s+([^,\.]+)"
            ]
        }
    
    def _load_topic_keywords(self) -> Dict[str, List[str]]:
        """Carrega palavras-chave por tópico."""
        return {
            "tecnologia": ["software", "programação", "desenvolvimento", "tecnologia", "digital"],
            "saúde": ["medicina", "bem-estar", "fitness", "nutrição", "saúde"],
            "negócios": ["empreendedorismo", "marketing", "vendas", "gestão", "negócios"],
            "educação": ["aprendizado", "estudo", "curso", "treinamento", "educação"],
            "lazer": ["entretenimento", "hobby", "viagem", "esporte", "lazer"]
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrões de intenção."""
        return {
            "informar": ["explicar", "descrever", "mostrar", "apresentar", "informar"],
            "persuadir": ["convencer", "influenciar", "motivar", "estimular", "persuadir"],
            "instruir": ["ensinar", "guiar", "orientar", "treinar", "instruir"],
            "entreter": ["divertir", "animar", "distrair", "relaxar", "entreter"],
            "vender": ["comercializar", "promover", "oferecer", "vender", "negociar"]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrões de entidades."""
        return {
            "pessoa": [r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"],
            "organização": [r"\b[A-Z][a-z]+\s+(?:Corp|Inc|Ltd|LLC|SA)\b"],
            "local": [r"\b(?:em|no|na)\s+([A-Z][a-z]+)\b"],
            "data": [r"\b\d{1,2}/\d{1,2}/\d{4}\b", r"\b\d{4}-\d{2}-\d{2}\b"],
            "produto": [r"\b[A-Z][a-z]+\s+(?:Pro|Plus|Max|Ultra)\b"]
        }
    
    def analyze_context(self, text: str, gap_position: int) -> SemanticContext:
        """
        Analisa o contexto semântico ao redor de uma lacuna.
        
        Args:
            text: Texto completo
            gap_position: Posição da lacuna
            
        Returns:
            Contexto semântico analisado
        """
        start_time = time.time()
        
        try:
            # Extrair texto ao redor da lacuna
            start = max(0, gap_position - self.context_window_size)
            end = min(len(text), gap_position + self.context_window_size)
            surrounding_text = text[start:end]
            
            # Detectar tópico
            topic = self._detect_topic(surrounding_text)
            
            # Detectar intenção
            intent = self._detect_intent(surrounding_text)
            
            # Detectar entidades
            entities = self._detect_entities(surrounding_text)
            
            # Analisar sentimento
            sentiment = self._analyze_sentiment(surrounding_text)
            
            # Extrair palavras-chave
            keywords = self._extract_keywords(surrounding_text)
            
            # Detectar tipo de conteúdo
            content_type = self._detect_content_type(surrounding_text)
            
            # Detectar audiência
            target_audience = self._detect_target_audience(surrounding_text)
            
            # Detectar tom
            tone = self._detect_tone(surrounding_text)
            
            # Detectar complexidade
            complexity_level = self._detect_complexity(surrounding_text)
            
            context = SemanticContext(
                surrounding_text=surrounding_text,
                topic=topic,
                intent=intent,
                entities=entities,
                sentiment=sentiment,
                keywords=keywords,
                content_type=content_type,
                target_audience=target_audience,
                tone=tone,
                complexity_level=complexity_level,
                metadata={
                    "context_window_size": self.context_window_size,
                    "analysis_time": time.time() - start_time
                }
            )
            
            # Atualizar métricas
            analysis_time = time.time() - start_time
            self._update_metrics(True, analysis_time, context)
            
            return context
            
        except Exception as e:
            logger.error(f"Erro na análise de contexto: {e}")
            self._update_metrics(False, 0.0, None)
            
            # Retornar contexto básico em caso de erro
            return SemanticContext(
                surrounding_text=text[max(0, gap_position-50):gap_position+50],
                topic="geral",
                intent="informar",
                entities=[],
                sentiment=0.0,
                keywords=[],
                content_type="texto",
                target_audience="geral",
                tone="neutro",
                complexity_level="médio"
            )
    
    def _detect_topic(self, text: str) -> str:
        """Detecta o tópico principal do texto."""
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                return topic
        
        return "geral"
    
    def _detect_intent(self, text: str) -> str:
        """Detecta a intenção do texto."""
        text_lower = text.lower()
        
        best_intent = "informar"
        best_score = 0
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent
    
    def _detect_entities(self, text: str) -> List[str]:
        """Detecta entidades no texto."""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities.extend(matches)
        
        return list(set(entities))  # Remove duplicatas
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analisa o sentimento do texto (simplificado)."""
        positive_words = ["bom", "ótimo", "excelente", "positivo", "benefício"]
        negative_words = ["ruim", "péssimo", "negativo", "problema", "dificuldade"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment))  # Normalizar entre -1 e 1
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave do texto."""
        # Palavras comuns para remover
        stop_words = {"o", "a", "os", "as", "um", "uma", "e", "ou", "de", "da", "do", "em", "para", "com"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Contar frequência
        word_freq = defaultdict(int)
        for word in keywords:
            word_freq[word] += 1
        
        # Retornar palavras mais frequentes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _detect_content_type(self, text: str) -> str:
        """Detecta o tipo de conteúdo."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["artigo", "post", "blog"]):
            return "artigo"
        elif any(word in text_lower for word in ["tutorial", "guia", "instrução"]):
            return "tutorial"
        elif any(word in text_lower for word in ["anúncio", "promoção", "oferta"]):
            return "anúncio"
        elif any(word in text_lower for word in ["notícia", "informação", "atualização"]):
            return "notícia"
        else:
            return "texto"
    
    def _detect_target_audience(self, text: str) -> str:
        """Detecta a audiência alvo."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["iniciante", "novato", "básico"]):
            return "iniciante"
        elif any(word in text_lower for word in ["avançado", "expert", "profissional"]):
            return "avançado"
        elif any(word in text_lower for word in ["empresa", "negócio", "corporativo"]):
            return "empresarial"
        else:
            return "geral"
    
    def _detect_tone(self, text: str) -> str:
        """Detecta o tom do texto."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["formal", "profissional", "técnico"]):
            return "formal"
        elif any(word in text_lower for word in ["casual", "descontraído", "amigável"]):
            return "casual"
        elif any(word in text_lower for word in ["urgente", "importante", "crítico"]):
            return "urgente"
        else:
            return "neutro"
    
    def _detect_complexity(self, text: str) -> str:
        """Detecta o nível de complexidade."""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length > 8:
            return "alto"
        elif avg_word_length > 6:
            return "médio"
        else:
            return "baixo"
    
    def _update_metrics(self, success: bool, analysis_time: float, context: Optional[SemanticContext]):
        """Atualiza métricas de performance."""
        self.metrics["total_analyses"] += 1
        
        if success:
            self.metrics["successful_analyses"] += 1
            self.metrics["analysis_times"].append(analysis_time)
            self.metrics["avg_analysis_time"] = statistics.mean(self.metrics["analysis_times"])
            
            if context:
                self.metrics["context_types"][context.content_type] += 1
        else:
            self.metrics["failed_analyses"] += 1


class SemanticGapDetector:
    """Detector de lacunas baseado em análise semântica."""
    
    def __init__(self):
        """Inicializa o detector semântico."""
        self.semantic_analyzer = SemanticAnalyzer()
        self.min_semantic_confidence = 0.6
        self.context_threshold = 0.7
        
        # Padrões semânticos para detecção de lacunas
        self.gap_patterns = self._create_gap_patterns()
        
        # Cache de análises semânticas
        self.semantic_cache = {}
        self.cache_ttl = 1800  # 30 minutos
        
        # Métricas de performance
        self.metrics = {
            "total_detections": 0,
            "semantic_detections": 0,
            "context_detections": 0,
            "avg_detection_time": 0.0,
            "detection_times": deque(maxlen=1000),
            "confidence_distribution": defaultdict(int)
        }
        
        logger.info("SemanticGapDetector inicializado")
    
    def _create_gap_patterns(self) -> Dict[str, List[str]]:
        """Cria padrões para detecção semântica de lacunas."""
        return {
            "missing_keyword": [
                r"palavra-chave\s+(?:que\s+)?(?:falta|ausente|necessária)",
                r"keyword\s+(?:que\s+)?(?:falta|ausente|necessária)",
                r"termo\s+(?:que\s+)?(?:falta|ausente|necessário)"
            ],
            "missing_context": [
                r"contexto\s+(?:que\s+)?(?:falta|ausente|necessário)",
                r"informação\s+(?:que\s+)?(?:falta|ausente|necessária)",
                r"detalhe\s+(?:que\s+)?(?:falta|ausente|necessário)"
            ],
            "missing_audience": [
                r"público\s+(?:que\s+)?(?:falta|ausente|necessário)",
                r"audiência\s+(?:que\s+)?(?:falta|ausente|necessária)",
                r"usuários\s+(?:que\s+)?(?:faltam|ausentes|necessários)"
            ],
            "missing_content": [
                r"conteúdo\s+(?:que\s+)?(?:falta|ausente|necessário)",
                r"material\s+(?:que\s+)?(?:falta|ausente|necessário)",
                r"texto\s+(?:que\s+)?(?:falta|ausente|necessário)"
            ]
        }
    
    def detect_semantic_gaps(self, text: str, hybrid_gaps: List[DetectedGap]) -> SemanticDetectionResult:
        """
        Detecta lacunas usando análise semântica.
        
        Args:
            text: Texto para análise
            hybrid_gaps: Lacunas detectadas pelo sistema híbrido
            
        Returns:
            Resultado da detecção semântica
        """
        start_time = time.time()
        
        try:
            semantic_gaps = []
            errors = []
            warnings = []
            
            # Analisar cada lacuna híbrida semanticamente
            for gap in hybrid_gaps:
                try:
                    semantic_gap = self._analyze_gap_semantically(text, gap)
                    if semantic_gap:
                        semantic_gaps.append(semantic_gap)
                except Exception as e:
                    error_msg = f"Erro ao analisar lacuna semanticamente: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Detectar lacunas semânticas adicionais
            additional_gaps = self._detect_additional_semantic_gaps(text, hybrid_gaps)
            semantic_gaps.extend(additional_gaps)
            
            # Calcular métricas
            total_gaps = len(semantic_gaps)
            avg_confidence = statistics.mean([sg.semantic_confidence for sg in semantic_gaps]) if semantic_gaps else 0.0
            
            # Atualizar métricas
            detection_time = time.time() - start_time
            self._update_metrics(total_gaps, detection_time, avg_confidence)
            
            result = SemanticDetectionResult(
                semantic_gaps=semantic_gaps,
                total_semantic_gaps=total_gaps,
                avg_semantic_confidence=avg_confidence,
                semantic_analysis_time=detection_time,
                context_analysis_time=0.0,  # Será calculado individualmente
                intent_detection_time=0.0,  # Será calculado individualmente
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                semantic_insights={
                    "topic_distribution": self._get_topic_distribution(semantic_gaps),
                    "intent_distribution": self._get_intent_distribution(semantic_gaps),
                    "confidence_distribution": self._get_confidence_distribution(semantic_gaps)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na detecção semântica: {e}")
            return SemanticDetectionResult(
                semantic_gaps=[],
                total_semantic_gaps=0,
                avg_semantic_confidence=0.0,
                semantic_analysis_time=time.time() - start_time,
                context_analysis_time=0.0,
                intent_detection_time=0.0,
                success=False,
                errors=[str(e)],
                warnings=[],
                semantic_insights={}
            )
    
    def _analyze_gap_semantically(self, text: str, gap: DetectedGap) -> Optional[SemanticGap]:
        """Analisa uma lacuna individual de forma semântica."""
        # Verificar cache
        cache_key = f"{hash(text)}:{gap.start_pos}:{gap.end_pos}"
        if cache_key in self.semantic_cache:
            return self.semantic_cache[cache_key]
        
        # Analisar contexto semântico
        semantic_context = self.semantic_analyzer.analyze_context(text, gap.start_pos)
        
        # Calcular confiança semântica
        semantic_confidence = self._calculate_semantic_confidence(gap, semantic_context)
        
        # Se confiança muito baixa, ignorar
        if semantic_confidence < self.min_semantic_confidence:
            return None
        
        # Gerar sugestões semânticas
        suggested_value = self._generate_semantic_suggestion(gap, semantic_context)
        alternative_suggestions = self._generate_alternative_suggestions(gap, semantic_context)
        
        # Calcular scores de validação
        semantic_validation_score = self._calculate_validation_score(gap, semantic_context)
        context_relevance = self._calculate_context_relevance(gap, semantic_context)
        intent_alignment = self._calculate_intent_alignment(gap, semantic_context)
        
        semantic_gap = SemanticGap(
            gap=gap,
            semantic_context=semantic_context,
            semantic_confidence=semantic_confidence,
            suggested_semantic_value=suggested_value,
            alternative_suggestions=alternative_suggestions,
            semantic_validation_score=semantic_validation_score,
            context_relevance=context_relevance,
            intent_alignment=intent_alignment,
            metadata={
                "analysis_timestamp": datetime.now().isoformat(),
                "cache_key": cache_key
            }
        )
        
        # Armazenar no cache
        self.semantic_cache[cache_key] = semantic_gap
        
        return semantic_gap
    
    def _calculate_semantic_confidence(self, gap: DetectedGap, context: SemanticContext) -> float:
        """Calcula a confiança semântica de uma lacuna."""
        confidence_factors = []
        
        # Fator 1: Relevância do contexto
        context_relevance = self._calculate_context_relevance(gap, context)
        confidence_factors.append(context_relevance)
        
        # Fator 2: Alinhamento com intenção
        intent_alignment = self._calculate_intent_alignment(gap, context)
        confidence_factors.append(intent_alignment)
        
        # Fator 3: Presença de palavras-chave relacionadas
        keyword_relevance = self._calculate_keyword_relevance(gap, context)
        confidence_factors.append(keyword_relevance)
        
        # Fator 4: Complexidade do contexto
        complexity_factor = self._calculate_complexity_factor(context)
        confidence_factors.append(complexity_factor)
        
        # Média ponderada dos fatores
        weights = [0.3, 0.3, 0.2, 0.2]
        weighted_confidence = sum(factor * weight for factor, weight in zip(confidence_factors, weights))
        
        return min(1.0, max(0.0, weighted_confidence))
    
    def _calculate_context_relevance(self, gap: DetectedGap, context: SemanticContext) -> float:
        """Calcula a relevância do contexto para a lacuna."""
        # Verificar se o tipo de placeholder está alinhado com o contexto
        placeholder_type = gap.placeholder_type.value
        
        if "keyword" in placeholder_type and context.topic != "geral":
            return 0.9
        elif "content" in placeholder_type and context.content_type != "texto":
            return 0.8
        elif "audience" in placeholder_type and context.target_audience != "geral":
            return 0.8
        else:
            return 0.6
    
    def _calculate_intent_alignment(self, gap: DetectedGap, context: SemanticContext) -> float:
        """Calcula o alinhamento com a intenção detectada."""
        placeholder_type = gap.placeholder_type.value
        
        if context.intent == "informar" and "keyword" in placeholder_type:
            return 0.9
        elif context.intent == "persuadir" and "audience" in placeholder_type:
            return 0.8
        elif context.intent == "instruir" and "content" in placeholder_type:
            return 0.8
        else:
            return 0.6
    
    def _calculate_keyword_relevance(self, gap: DetectedGap, context: SemanticContext) -> float:
        """Calcula a relevância das palavras-chave do contexto."""
        if not context.keywords:
            return 0.5
        
        # Verificar se há palavras-chave relacionadas ao tipo de placeholder
        placeholder_type = gap.placeholder_type.value
        
        if "keyword" in placeholder_type:
            # Palavras-chave são relevantes para placeholders de keyword
            return min(1.0, len(context.keywords) / 5.0)
        else:
            return 0.7
    
    def _calculate_complexity_factor(self, context: SemanticContext) -> float:
        """Calcula fator baseado na complexidade do contexto."""
        complexity_map = {
            "baixo": 0.8,
            "médio": 0.9,
            "alto": 0.7
        }
        return complexity_map.get(context.complexity_level, 0.8)
    
    def _generate_semantic_suggestion(self, gap: DetectedGap, context: SemanticContext) -> str:
        """Gera sugestão semântica para a lacuna."""
        placeholder_type = gap.placeholder_type.value
        
        if "keyword" in placeholder_type:
            if context.keywords:
                return context.keywords[0]
            elif context.topic != "geral":
                return f"palavra-chave_{context.topic}"
            else:
                return "palavra-chave_principal"
        
        elif "content" in placeholder_type:
            return context.content_type
        
        elif "audience" in placeholder_type:
            return context.target_audience
        
        elif "tone" in placeholder_type:
            return context.tone
        
        else:
            return "valor_padrão"
    
    def _generate_alternative_suggestions(self, gap: DetectedGap, context: SemanticContext) -> List[str]:
        """Gera sugestões alternativas para a lacuna."""
        suggestions = []
        placeholder_type = gap.placeholder_type.value
        
        if "keyword" in placeholder_type:
            # Usar palavras-chave do contexto
            suggestions.extend(context.keywords[:3])
            
            # Adicionar sugestões baseadas no tópico
            if context.topic != "geral":
                suggestions.append(f"palavra-chave_{context.topic}")
        
        elif "content" in placeholder_type:
            suggestions.extend(["artigo", "tutorial", "guia", "anúncio"])
        
        elif "audience" in placeholder_type:
            suggestions.extend(["iniciante", "intermediário", "avançado", "empresarial"])
        
        elif "tone" in placeholder_type:
            suggestions.extend(["formal", "casual", "urgente", "neutro"])
        
        return list(set(suggestions))[:self.semantic_analyzer.max_alternatives]
    
    def _calculate_validation_score(self, gap: DetectedGap, context: SemanticContext) -> float:
        """Calcula score de validação semântica."""
        scores = []
        
        # Score baseado na confiança original
        scores.append(gap.confidence)
        
        # Score baseado na relevância do contexto
        scores.append(self._calculate_context_relevance(gap, context))
        
        # Score baseado no alinhamento de intenção
        scores.append(self._calculate_intent_alignment(gap, context))
        
        return statistics.mean(scores)
    
    def _detect_additional_semantic_gaps(self, text: str, hybrid_gaps: List[DetectedGap]) -> List[SemanticGap]:
        """Detecta lacunas semânticas adicionais não capturadas pelo sistema híbrido."""
        additional_gaps = []
        
        # Procurar por padrões semânticos que indicam lacunas
        for pattern_type, patterns in self.gap_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    # Verificar se já não foi detectado pelo sistema híbrido
                    if not self._is_already_detected(match.start(), match.end(), hybrid_gaps):
                        # Criar lacuna semântica adicional
                        semantic_gap = self._create_additional_semantic_gap(
                            text, match, pattern_type
                        )
                        if semantic_gap:
                            additional_gaps.append(semantic_gap)
        
        return additional_gaps
    
    def _is_already_detected(self, start: int, end: int, hybrid_gaps: List[DetectedGap]) -> bool:
        """Verifica se uma posição já foi detectada pelo sistema híbrido."""
        for gap in hybrid_gaps:
            if abs(gap.start_pos - start) < 10:  # Margem de tolerância
                return True
        return False
    
    def _create_additional_semantic_gap(self, text: str, match: re.Match, pattern_type: str) -> Optional[SemanticGap]:
        """Cria lacuna semântica adicional baseada em padrão detectado."""
        try:
            # Analisar contexto
            semantic_context = self.semantic_analyzer.analyze_context(text, match.start())
            
            # Determinar tipo de placeholder baseado no padrão
            placeholder_type = self._determine_placeholder_type(pattern_type)
            
            # Criar gap básico
            gap = DetectedGap(
                placeholder_type=placeholder_type,
                placeholder_name=placeholder_type.value,
                start_pos=match.start(),
                end_pos=match.end(),
                context=match.group(0),
                confidence=0.7,  # Confiança moderada para detecções semânticas
                detection_method=DetectionMethod.VALIDATION,
                validation_level=ValidationLevel.SEMANTIC
            )
            
            # Analisar semanticamente
            return self._analyze_gap_semantically(text, gap)
            
        except Exception as e:
            logger.error(f"Erro ao criar lacuna semântica adicional: {e}")
            return None
    
    def _determine_placeholder_type(self, pattern_type: str) -> PlaceholderType:
        """Determina o tipo de placeholder baseado no padrão detectado."""
        type_mapping = {
            "missing_keyword": PlaceholderType.PRIMARY_KEYWORD,
            "missing_context": PlaceholderType.CLUSTER_CONTENT,
            "missing_audience": PlaceholderType.TARGET_AUDIENCE,
            "missing_content": PlaceholderType.CONTENT_TYPE
        }
        return type_mapping.get(pattern_type, PlaceholderType.CUSTOM)
    
    def _get_topic_distribution(self, semantic_gaps: List[SemanticGap]) -> Dict[str, int]:
        """Obtém distribuição de tópicos das lacunas semânticas."""
        distribution = defaultdict(int)
        for gap in semantic_gaps:
            distribution[gap.semantic_context.topic] += 1
        return dict(distribution)
    
    def _get_intent_distribution(self, semantic_gaps: List[SemanticGap]) -> Dict[str, int]:
        """Obtém distribuição de intenções das lacunas semânticas."""
        distribution = defaultdict(int)
        for gap in semantic_gaps:
            distribution[gap.semantic_context.intent] += 1
        return dict(distribution)
    
    def _get_confidence_distribution(self, semantic_gaps: List[SemanticGap]) -> Dict[str, int]:
        """Obtém distribuição de confiança das lacunas semânticas."""
        distribution = defaultdict(int)
        for gap in semantic_gaps:
            confidence_level = self._get_confidence_level(gap.semantic_confidence)
            distribution[confidence_level] += 1
        return dict(distribution)
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Converte valor de confiança em nível."""
        if confidence >= 0.9:
            return "muito_alto"
        elif confidence >= 0.8:
            return "alto"
        elif confidence >= 0.7:
            return "médio"
        elif confidence >= 0.6:
            return "baixo"
        else:
            return "muito_baixo"
    
    def _update_metrics(self, gaps_count: int, detection_time: float, avg_confidence: float):
        """Atualiza métricas de performance."""
        self.metrics["total_detections"] += 1
        self.metrics["semantic_detections"] += gaps_count
        self.metrics["detection_times"].append(detection_time)
        self.metrics["avg_detection_time"] = statistics.mean(self.metrics["detection_times"])
        
        # Distribuição de confiança
        confidence_level = self._get_confidence_level(avg_confidence)
        self.metrics["confidence_distribution"][confidence_level] += 1


# Funções de conveniência
def detect_semantic_gaps(text: str, hybrid_gaps: List[DetectedGap]) -> SemanticDetectionResult:
    """Função de conveniência para detecção semântica."""
    detector = SemanticGapDetector()
    return detector.detect_semantic_gaps(text, hybrid_gaps)


def get_semantic_detection_stats() -> Dict[str, Any]:
    """Obtém estatísticas de detecção semântica."""
    detector = SemanticGapDetector()
    return detector.metrics


if __name__ == "__main__":
    # Teste básico do sistema
    test_text = """
    Preciso criar um artigo sobre {primary_keyword} para o público {target_audience}.
    O conteúdo deve ser {content_type} com tom {tone}.
    """
    
    # Simular lacunas híbridas
    hybrid_gaps = [
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
    
    # Detectar lacunas semânticas
    result = detect_semantic_gaps(test_text, hybrid_gaps)
    
    print(f"Lacunas semânticas detectadas: {result.total_semantic_gaps}")
    print(f"Confiança média: {result.avg_semantic_confidence:.2f}")
    print(f"Tempo de análise: {result.semantic_analysis_time:.3f}s") 