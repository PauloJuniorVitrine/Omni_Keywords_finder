#!/usr/bin/env python3
"""
Sistema de Lacunas Preciso - Fase 6
Responsável por detecção híbrida (Regex + NLP) e validação semântica.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 6
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import re
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import sqlite3
from collections import defaultdict, deque
import statistics
import threading
from datetime import datetime, timedelta

# Dependências opcionais
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaceholderType(Enum):
    """Tipos de placeholders."""
    PRIMARY_KEYWORD = "primary_keyword"
    SECONDARY_KEYWORDS = "secondary_keywords"
    CLUSTER_CONTENT = "cluster_content"
    NICHE = "niche"
    TARGET_AUDIENCE = "target_audience"
    CONTENT_TYPE = "content_type"
    TONE = "tone"
    LENGTH = "length"
    CUSTOM = "custom"

class DetectionMethod(Enum):
    """Métodos de detecção."""
    REGEX = "regex"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

class ValidationLevel(Enum):
    """Níveis de validação."""
    BASIC = "basic"
    SEMANTIC = "semantic"
    CONTEXTUAL = "contextual"
    FULL = "full"

@dataclass
class Placeholder:
    """Representação de placeholder."""
    type: PlaceholderType
    name: str
    pattern: str
    required: bool = True
    default_value: Optional[str] = None
    validation_rules: List[str] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []

@dataclass
class DetectedGap:
    """Lacuna detectada."""
    placeholder_type: PlaceholderType
    placeholder_name: str
    start_pos: int
    end_pos: int
    context: str
    confidence: float
    detection_method: DetectionMethod
    validation_level: ValidationLevel
    suggested_value: Optional[str] = None
    validation_score: Optional[float] = None

@dataclass
class GapValidation:
    """Resultado de validação de lacuna."""
    is_valid: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    semantic_score: Optional[float] = None
    contextual_score: Optional[float] = None

class RegexLacunaDetector:
    """Detector de lacunas baseado em regex."""
    
    def __init__(self):
        self.placeholder_patterns = {
            PlaceholderType.PRIMARY_KEYWORD: r'\{primary_keyword\}',
            PlaceholderType.SECONDARY_KEYWORDS: r'\{secondary_keywords\}',
            PlaceholderType.CLUSTER_CONTENT: r'\{cluster_content\}',
            PlaceholderType.NICHE: r'\{niche\}',
            PlaceholderType.TARGET_AUDIENCE: r'\{target_audience\}',
            PlaceholderType.CONTENT_TYPE: r'\{content_type\}',
            PlaceholderType.TONE: r'\{tone\}',
            PlaceholderType.LENGTH: r'\{length\}',
            PlaceholderType.CUSTOM: r'\{([^}]+)\}'
        }
        
        self.compiled_patterns = {
            placeholder_type: re.compile(pattern, re.IGNORECASE)
            for placeholder_type, pattern in self.placeholder_patterns.items()
        }
    
    def detect_gaps(self, text: str) -> List[DetectedGap]:
        """Detecta lacunas usando regex."""
        detected_gaps = []
        
        for placeholder_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                gap = DetectedGap(
                    placeholder_type=placeholder_type,
                    placeholder_name=match.group(1) if placeholder_type == PlaceholderType.CUSTOM else placeholder_type.value,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=self._extract_context(text, match.start(), match.end()),
                    confidence=0.95,  # Alta confiança para regex
                    detection_method=DetectionMethod.REGEX,
                    validation_level=ValidationLevel.BASIC
                )
                
                detected_gaps.append(gap)
        
        return detected_gaps
    
    def _extract_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Extrai contexto ao redor da lacuna."""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        
        return text[context_start:context_end].strip()

class SemanticLacunaDetector:
    """Detector de lacunas baseado em semântica."""
    
    def __init__(self):
        self.model = None
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Modelo semântico carregado com sucesso")
            except Exception as e:
                logger.warning(f"Não foi possível carregar modelo semântico: {e}")
    
    def detect_gaps(self, text: str) -> List[DetectedGap]:
        """Detecta lacunas usando análise semântica."""
        if not self.model:
            return []
        
        detected_gaps = []
        
        # Dividir texto em sentenças
        sentences = self._split_sentences(text)
        
        for index, sentence in enumerate(sentences):
            # Verificar se a sentença parece incompleta
            if self._is_incomplete_sentence(sentence):
                # Calcular posição da lacuna
                start_pos = text.find(sentence)
                end_pos = start_pos + len(sentence)
                
                gap = DetectedGap(
                    placeholder_type=PlaceholderType.CUSTOM,
                    placeholder_name="semantic_gap",
                    start_pos=start_pos,
                    end_pos=end_pos,
                    context=sentence,
                    confidence=self._calculate_semantic_confidence(sentence),
                    detection_method=DetectionMethod.SEMANTIC,
                    validation_level=ValidationLevel.SEMANTIC
                )
                
                detected_gaps.append(gap)
        
        return detected_gaps
    
    def _split_sentences(self, text: str) -> List[str]:
        """Divide texto em sentenças."""
        # Implementação simples - pode ser melhorada com spaCy
        sentences = re.split(r'[.!?]+', text)
        return [string_data.strip() for string_data in sentences if string_data.strip()]
    
    def _is_incomplete_sentence(self, sentence: str) -> bool:
        """Verifica se sentença parece incompleta."""
        # Heurísticas para detectar sentenças incompletas
        incomplete_indicators = [
            r'\b(para|com|em|de|que|qual|quem|onde|quando|como|por que)\string_data*$',
            r'\b(é|são|está|estão|tem|têm|pode|podem|deve|devem)\string_data*$',
            r'\b(um|uma|o|a|os|as|este|esta|estes|estas)\string_data*$',
            r'\b(se|mas|e|ou|nem|tanto|quanto)\string_data*$'
        ]
        
        for pattern in incomplete_indicators:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_semantic_confidence(self, sentence: str) -> float:
        """Calcula confiança semântica."""
        # Implementação básica - pode ser melhorada
        words = sentence.split()
        if len(words) < 3:
            return 0.8
        elif len(words) < 5:
            return 0.6
        else:
            return 0.4

class ContextValidator:
    """Validador de contexto."""
    
    def __init__(self):
        self.nlp = None
        
        if SPACY_AVAILABLE:
            try:
                # Tentar carregar modelo português, fallback para inglês
                try:
                    self.nlp = spacy.load("pt_core_news_sm")
                except:
                    self.nlp = spacy.load("en_core_web_sm")
                logger.info("Modelo de linguagem carregado para validação contextual")
            except Exception as e:
                logger.warning(f"Não foi possível carregar modelo de linguagem: {e}")
    
    def validate_context(self, gap: DetectedGap, suggested_value: str, full_text: str) -> GapValidation:
        """Valida contexto da lacuna."""
        issues = []
        suggestions = []
        semantic_score = None
        contextual_score = None
        
        # Validação básica
        if not suggested_value.strip():
            issues.append("Valor sugerido está vazio")
            return GapValidation(False, 0.0, issues, suggestions)
        
        # Validação de coerência
        if self._check_coherence(gap, suggested_value, full_text):
            contextual_score = 0.8
        else:
            issues.append("Valor não é coerente com o contexto")
            contextual_score = 0.3
        
        # Validação semântica
        if self.nlp:
            semantic_score = self._calculate_semantic_similarity(gap.context, suggested_value)
            if semantic_score < 0.5:
                issues.append("Baixa similaridade semântica")
                suggestions.append("Considere um valor mais relacionado ao contexto")
        
        # Validação de formato
        if not self._validate_format(gap.placeholder_type, suggested_value):
            issues.append("Formato não adequado para o tipo de placeholder")
            suggestions.append(f"Use formato apropriado para {gap.placeholder_type.value}")
        
        # Calcular confiança geral
        confidence = self._calculate_overall_confidence(semantic_score, contextual_score, len(issues))
        
        return GapValidation(
            is_valid=len(issues) == 0,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            semantic_score=semantic_score,
            contextual_score=contextual_score
        )
    
    def _check_coherence(self, gap: DetectedGap, suggested_value: str, full_text: str) -> bool:
        """Verifica coerência do valor sugerido."""
        # Implementação básica - pode ser melhorada
        context_words = set(gap.context.lower().split())
        value_words = set(suggested_value.lower().split())
        
        # Verificar se há palavras em comum
        common_words = context_words.intersection(value_words)
        return len(common_words) > 0
    
    def _calculate_semantic_similarity(self, context: str, value: str) -> float:
        """Calcula similaridade semântica."""
        if not self.nlp:
            return 0.5
        
        try:
            doc1 = self.nlp(context)
            doc2 = self.nlp(value)
            return doc1.similarity(doc2)
        except Exception:
            return 0.5
    
    def _validate_format(self, placeholder_type: PlaceholderType, value: str) -> bool:
        """Valida formato do valor."""
        if placeholder_type == PlaceholderType.LENGTH:
            return value.isdigit()
        elif placeholder_type == PlaceholderType.TONE:
            valid_tones = ["formal", "informal", "profissional", "casual", "técnico"]
            return value.lower() in valid_tones
        elif placeholder_type == PlaceholderType.CONTENT_TYPE:
            valid_types = ["artigo", "post", "vídeo", "infográfico", "e-book"]
            return value.lower() in valid_types
        
        return True
    
    def _calculate_overall_confidence(self, semantic_score: Optional[float], 
                                    contextual_score: Optional[float], 
                                    issue_count: int) -> float:
        """Calcula confiança geral."""
        base_confidence = 0.7
        
        if semantic_score is not None:
            base_confidence = (base_confidence + semantic_score) / 2
        
        if contextual_score is not None:
            base_confidence = (base_confidence + contextual_score) / 2
        
        # Penalizar por issues
        penalty = issue_count * 0.1
        base_confidence = max(0.0, base_confidence - penalty)
        
        return base_confidence

class SemanticMatcher:
    """Matcher semântico para preenchimento de lacunas."""
    
    def __init__(self):
        self.model = None
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Modelo de matching semântico carregado")
            except Exception as e:
                logger.warning(f"Não foi possível carregar modelo de matching: {e}")
    
    def find_best_match(self, gap: DetectedGap, candidates: List[str]) -> Tuple[str, float]:
        """Encontra melhor match para a lacuna."""
        if not self.model or not candidates:
            return candidates[0] if candidates else "", 0.0
        
        try:
            # Calcular embeddings
            gap_embedding = self.model.encode(gap.context)
            candidate_embeddings = self.model.encode(candidates)
            
            # Calcular similaridades
            similarities = []
            for candidate_embedding in candidate_embeddings:
                similarity = self._cosine_similarity(gap_embedding, candidate_embedding)
                similarities.append(similarity)
            
            # Encontrar melhor match
            best_idx = similarities.index(max(similarities))
            best_candidate = candidates[best_idx]
            best_similarity = similarities[best_idx]
            
            return best_candidate, best_similarity
            
        except Exception as e:
            logger.error(f"Erro no matching semântico: {e}")
            return candidates[0] if candidates else "", 0.0
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calcula similaridade de cosseno."""
        import numpy as np
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

class QualityValidator:
    """Validador de qualidade."""
    
    def __init__(self):
        self.quality_thresholds = {
            "min_length": 3,
            "max_length": 1000,
            "min_semantic_score": 0.6,
            "min_contextual_score": 0.7,
            "min_overall_confidence": 0.8
        }
    
    def validate_quality(self, gap: DetectedGap, suggested_value: str, 
                        validation: GapValidation) -> bool:
        """Valida qualidade do preenchimento."""
        issues = []
        
        # Validação de comprimento
        if len(suggested_value) < self.quality_thresholds["min_length"]:
            issues.append(f"Valor muito curto (mínimo: {self.quality_thresholds['min_length']})")
        
        if len(suggested_value) > self.quality_thresholds["max_length"]:
            issues.append(f"Valor muito longo (máximo: {self.quality_thresholds['max_length']})")
        
        # Validação de scores
        if validation.semantic_score and validation.semantic_score < self.quality_thresholds["min_semantic_score"]:
            issues.append(f"Score semântico baixo (mínimo: {self.quality_thresholds['min_semantic_score']})")
        
        if validation.contextual_score and validation.contextual_score < self.quality_thresholds["min_contextual_score"]:
            issues.append(f"Score contextual baixo (mínimo: {self.quality_thresholds['min_contextual_score']})")
        
        if validation.confidence < self.quality_thresholds["min_overall_confidence"]:
            issues.append(f"Confiança geral baixa (mínimo: {self.quality_thresholds['min_overall_confidence']})")
        
        # Validação de conteúdo
        if self._has_inappropriate_content(suggested_value):
            issues.append("Conteúdo inapropriado detectado")
        
        return len(issues) == 0
    
    def _has_inappropriate_content(self, value: str) -> bool:
        """Verifica se há conteúdo inapropriado."""
        inappropriate_patterns = [
            r'\b(spam|scam|fraude|mentira|falso)\b',
            r'\b(sexo|pornografia|violência)\b',
            r'\b(droga|álcool|tabaco)\b'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False

class FallbackSystem:
    """Sistema de fallback inteligente."""
    
    def __init__(self):
        self.fallback_strategies = {
            PlaceholderType.PRIMARY_KEYWORD: self._fallback_primary_keyword,
            PlaceholderType.SECONDARY_KEYWORDS: self._fallback_secondary_keywords,
            PlaceholderType.CLUSTER_CONTENT: self._fallback_cluster_content,
            PlaceholderType.NICHE: self._fallback_niche,
            PlaceholderType.TARGET_AUDIENCE: self._fallback_target_audience,
            PlaceholderType.CONTENT_TYPE: self._fallback_content_type,
            PlaceholderType.TONE: self._fallback_tone,
            PlaceholderType.LENGTH: self._fallback_length
        }
    
    def get_fallback_value(self, gap: DetectedGap, context: str) -> str:
        """Obtém valor de fallback para a lacuna."""
        strategy = self.fallback_strategies.get(gap.placeholder_type)
        
        if strategy:
            return strategy(context)
        else:
            return self._fallback_generic(context)
    
    def _fallback_primary_keyword(self, context: str) -> str:
        """Fallback para keyword primária."""
        # Extrair palavras-chave do contexto
        words = re.findall(r'\b\w{4,}\b', context.lower())
        if words:
            return words[0].title()
        return "palavra-chave"
    
    def _fallback_secondary_keywords(self, context: str) -> str:
        """Fallback para keywords secundárias."""
        words = re.findall(r'\b\w{4,}\b', context.lower())
        if len(words) >= 2:
            return ", ".join(words[1:3])
        return "palavra-chave secundária"
    
    def _fallback_cluster_content(self, context: str) -> str:
        """Fallback para conteúdo do cluster."""
        return "conteúdo relacionado ao tópico"
    
    def _fallback_niche(self, context: str) -> str:
        """Fallback para nicho."""
        niches = ["tecnologia", "marketing", "saúde", "educação", "negócios"]
        return niches[0]
    
    def _fallback_target_audience(self, context: str) -> str:
        """Fallback para público-alvo."""
        audiences = ["profissionais", "estudantes", "empresários", "consumidores"]
        return audiences[0]
    
    def _fallback_content_type(self, context: str) -> str:
        """Fallback para tipo de conteúdo."""
        types = ["artigo", "post", "vídeo", "infográfico"]
        return types[0]
    
    def _fallback_tone(self, context: str) -> str:
        """Fallback para tom."""
        tones = ["profissional", "casual", "formal", "técnico"]
        return tones[0]
    
    def _fallback_length(self, context: str) -> str:
        """Fallback para comprimento."""
        return "500"
    
    def _fallback_generic(self, context: str) -> str:
        """Fallback genérico."""
        return "valor padrão"

class SistemaLacunasPreciso:
    """Sistema principal de lacunas preciso."""
    
    def __init__(self):
        self.regex_detector = RegexLacunaDetector()
        self.semantic_detector = SemanticLacunaDetector()
        self.context_validator = ContextValidator()
        self.semantic_matcher = SemanticMatcher()
        self.quality_validator = QualityValidator()
        self.fallback_system = FallbackSystem()
        
        # Cache e métricas
        self.detection_cache = {}
        self.metrics = {
            "total_detections": 0,
            "successful_detections": 0,
            "failed_detections": 0,
            "avg_confidence": 0.0,
            "detection_times": deque(maxlen=1000)
        }
    
    def detect_and_fill_gaps(self, text: str, candidates: Dict[PlaceholderType, List[str]] = None) -> Dict[str, Any]:
        """Detecta e preenche lacunas no texto."""
        start_time = time.time()
        
        try:
            # 1. Detecção híbrida
            regex_gaps = self.regex_detector.detect_gaps(text)
            semantic_gaps = self.semantic_detector.detect_gaps(text)
            
            # Combinar detecções
            all_gaps = self._merge_detections(regex_gaps, semantic_gaps)
            
            # 2. Preenchimento e validação
            filled_gaps = []
            validation_results = []
            
            for gap in all_gaps:
                # Encontrar melhor valor
                if candidates and gap.placeholder_type in candidates:
                    best_value, similarity = self.semantic_matcher.find_best_match(
                        gap, candidates[gap.placeholder_type]
                    )
                else:
                    best_value = self.fallback_system.get_fallback_value(gap, gap.context)
                    similarity = 0.5
                
                # Validar contexto
                validation = self.context_validator.validate_context(gap, best_value, text)
                
                # Validar qualidade
                quality_ok = self.quality_validator.validate_quality(gap, best_value, validation)
                
                # Atualizar gap
                gap.suggested_value = best_value
                gap.validation_score = validation.confidence
                
                filled_gaps.append(gap)
                validation_results.append({
                    "gap": asdict(gap),
                    "validation": asdict(validation),
                    "quality_ok": quality_ok
                })
            
            # 3. Calcular métricas
            execution_time = time.time() - start_time
            self._update_metrics(len(all_gaps), len(filled_gaps), execution_time)
            
            # 4. Resultado
            result = {
                "success": True,
                "detected_gaps": len(all_gaps),
                "filled_gaps": len(filled_gaps),
                "execution_time": execution_time,
                "avg_confidence": statistics.mean([g.confidence for g in filled_gaps]) if filled_gaps else 0.0,
                "gaps": [asdict(gap) for gap in filled_gaps],
                "validation_results": validation_results,
                "metrics": dict(self.metrics)
            }
            
            logger.info(f"Detecção e preenchimento concluídos: {len(filled_gaps)} lacunas processadas")
            return result
            
        except Exception as e:
            logger.error(f"Erro na detecção e preenchimento: {e}")
            return {
                "success": False,
                "error": str(e),
                "detected_gaps": 0,
                "filled_gaps": 0,
                "execution_time": time.time() - start_time
            }
    
    def _merge_detections(self, regex_gaps: List[DetectedGap], 
                         semantic_gaps: List[DetectedGap]) -> List[DetectedGap]:
        """Combina detecções de diferentes métodos."""
        merged_gaps = regex_gaps.copy()
        
        # Adicionar gaps semânticos que não se sobrepõem
        for semantic_gap in semantic_gaps:
            overlaps = False
            
            for regex_gap in regex_gaps:
                if self._gaps_overlap(semantic_gap, regex_gap):
                    overlaps = True
                    break
            
            if not overlaps:
                merged_gaps.append(semantic_gap)
        
        return merged_gaps
    
    def _gaps_overlap(self, gap1: DetectedGap, gap2: DetectedGap) -> bool:
        """Verifica se duas lacunas se sobrepõem."""
        return not (gap1.end_pos <= gap2.start_pos or gap2.end_pos <= gap1.start_pos)
    
    def _update_metrics(self, detected_count: int, successful_count: int, execution_time: float):
        """Atualiza métricas do sistema."""
        self.metrics["total_detections"] += detected_count
        self.metrics["successful_detections"] += successful_count
        self.metrics["failed_detections"] += (detected_count - successful_count)
        self.metrics["detection_times"].append(execution_time)
        
        if self.metrics["total_detections"] > 0:
            self.metrics["avg_confidence"] = (
                self.metrics["successful_detections"] / self.metrics["total_detections"]
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance."""
        if not self.metrics["detection_times"]:
            return {"avg_execution_time": 0.0}
        
        return {
            "avg_execution_time": statistics.mean(self.metrics["detection_times"]),
            "min_execution_time": min(self.metrics["detection_times"]),
            "max_execution_time": max(self.metrics["detection_times"]),
            "total_operations": len(self.metrics["detection_times"]),
            "success_rate": self.metrics["avg_confidence"]
        }
    
    def validate_placeholder_consistency(self, text: str) -> Dict[str, Any]:
        """Valida consistência de placeholders no texto."""
        gaps = self.regex_detector.detect_gaps(text)
        
        # Verificar placeholders obrigatórios
        required_placeholders = {
            PlaceholderType.PRIMARY_KEYWORD,
            PlaceholderType.SECONDARY_KEYWORDS
        }
        
        found_placeholders = {gap.placeholder_type for gap in gaps}
        missing_placeholders = required_placeholders - found_placeholders
        
        return {
            "total_placeholders": len(gaps),
            "missing_required": list(missing_placeholders),
            "consistency_score": 1.0 - (len(missing_placeholders) / len(required_placeholders)),
            "placeholders_found": [gap.placeholder_type.value for gap in gaps]
        }

# Instância global
sistema_lacunas = SistemaLacunasPreciso()

# Funções de conveniência
def detect_and_fill_gaps(text: str, candidates: Dict[str, List[str]] = None) -> Dict[str, Any]:
    """Detecta e preenche lacunas no texto."""
    if candidates:
        # Converter strings para PlaceholderType
        typed_candidates = {}
        for key, values in candidates.items():
            try:
                placeholder_type = PlaceholderType(key)
                typed_candidates[placeholder_type] = values
            except ValueError:
                logger.warning(f"Tipo de placeholder inválido: {key}")
        
        return sistema_lacunas.detect_and_fill_gaps(text, typed_candidates)
    else:
        return sistema_lacunas.detect_and_fill_gaps(text)

def validate_placeholder_consistency(text: str) -> Dict[str, Any]:
    """Valida consistência de placeholders."""
    return sistema_lacunas.validate_placeholder_consistency(text)

def get_performance_metrics() -> Dict[str, Any]:
    """Obtém métricas de performance."""
    return sistema_lacunas.get_performance_metrics()

if __name__ == "__main__":
    # Exemplo de uso
    sample_text = """
    Crie um {content_type} sobre {primary_keyword} para {target_audience}.
    O conteúdo deve ter {length} palavras e usar um tom {tone}.
    Inclua {secondary_keywords} e {cluster_content}.
    """
    
    candidates = {
        "primary_keyword": ["SEO", "marketing digital", "otimização"],
        "secondary_keywords": ["palavras-chave", "tráfego orgânico", "rankings"],
        "content_type": ["artigo", "post", "vídeo"],
        "target_audience": ["profissionais", "empresários", "estudantes"],
        "tone": ["profissional", "casual", "técnico"],
        "length": ["500", "1000", "1500"]
    }
    
    # Detectar e preencher lacunas
    result = detect_and_fill_gaps(sample_text, candidates)
    
    print("Resultado da detecção e preenchimento:")
    print(json.dumps(result, indent=2, default=str))
    
    # Validar consistência
    consistency = validate_placeholder_consistency(sample_text)
    print("\nValidação de consistência:")
    print(json.dumps(consistency, indent=2))
    
    # Métricas de performance
    metrics = get_performance_metrics()
    print("\nMétricas de performance:")
    print(json.dumps(metrics, indent=2)) 