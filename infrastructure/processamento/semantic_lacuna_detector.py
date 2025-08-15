#!/usr/bin/env python3
"""
Detector Semântico de Lacunas - Omni Keywords Finder
===================================================

Tracing ID: SEMANTIC_LACUNA_DETECTOR_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema semântico que detecta lacunas usando:
- Análise NLP avançada
- Detecção de sentenças incompletas
- Análise contextual
- Embeddings semânticos
- Cache inteligente de análises

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.2
Ruleset: enterprise_control_layer.yaml
"""

import re
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict, deque
import statistics

# Importar dependências NLP
try:
    import spacy
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("Dependências NLP não disponíveis. Detector semântico será limitado.")

# Importar classes do sistema
from .hybrid_lacuna_detector_imp001 import (
    DetectedGap,
    DetectionMethod,
    ValidationLevel,
    PlaceholderType
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticAnalysisType(Enum):
    """Tipos de análise semântica."""
    INCOMPLETE_SENTENCE = "incomplete_sentence"
    MISSING_CONTEXT = "missing_context"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"
    INCONSISTENT_TONE = "inconsistent_tone"
    MISSING_DETAILS = "missing_details"


@dataclass
class SemanticGap:
    """Lacuna semântica detectada."""
    gap_type: SemanticAnalysisType
    start_pos: int
    end_pos: int
    context: str
    confidence: float
    suggested_placeholder: Optional[PlaceholderType] = None
    suggested_value: Optional[str] = None
    analysis_details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.analysis_details is None:
            self.analysis_details = {}


@dataclass
class SemanticAnalysisResult:
    """Resultado da análise semântica."""
    gaps: List[SemanticGap]
    total_gaps: int
    confidence_avg: float
    analysis_time: float
    success: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SemanticLacunaDetector:
    """Detector de lacunas baseado em análise semântica."""
    
    def __init__(self):
        """Inicializa o detector semântico."""
        self.nlp_model = None
        self.embedding_model = None
        self.sentence_cache = {}
        self.analysis_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Padrões de sentenças incompletas
        self.incomplete_patterns = [
            r'\b(escreva|crie|desenvolva|produza)\s+(um|uma)\s+[^.]*$',  # Verbos de ação sem objeto
            r'\b(sobre|acerca|relacionado)\s+a\s*$',  # Preposições sem complemento
            r'\b(para|com|em|por)\s+[^.]*$',  # Preposições no final
            r'\b(que|qual|quem|onde|quando)\s+[^.]*$',  # Pronomes relativos sem verbo
            r'\b(se|caso|quando)\s+[^.]*$',  # Conjunções condicionais
            r'\b(primeiro|segundo|terceiro)\s+[^.]*$',  # Numerais sem substantivo
            r'\b(importante|essencial|necessário)\s+[^.]*$',  # Adjetivos sem substantivo
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.incomplete_patterns]
        
        # Inicializar modelos NLP se disponíveis
        if NLP_AVAILABLE:
            self._initialize_nlp_models()
        
        # Métricas
        self.metrics = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "avg_analysis_time": 0.0,
            "analysis_times": deque(maxlen=1000),
            "gap_types_detected": defaultdict(int),
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info("SemanticLacunaDetector inicializado")
    
    def _initialize_nlp_models(self):
        """Inicializa modelos NLP."""
        try:
            # Carregar modelo spaCy
            self.nlp_model = spacy.load("pt_core_news_sm")
            logger.info("Modelo spaCy carregado com sucesso")
        except OSError:
            try:
                # Tentar carregar modelo em inglês como fallback
                self.nlp_model = spacy.load("en_core_web_sm")
                logger.warning("Modelo spaCy em português não encontrado. Usando modelo em inglês.")
            except OSError:
                logger.warning("Modelo spaCy não disponível. Funcionalidades semânticas limitadas.")
                self.nlp_model = None
        
        try:
            # Carregar modelo de embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Modelo de embeddings carregado com sucesso")
        except Exception as e:
            logger.warning(f"Modelo de embeddings não disponível: {e}")
            self.embedding_model = None
    
    def detect_semantic_gaps(self, text: str) -> SemanticAnalysisResult:
        """
        Detecta lacunas semânticas no texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Resultado da análise semântica
        """
        start_time = time.time()
        
        # Verificar cache
        text_hash = hash(text)
        if text_hash in self.analysis_cache:
            self.metrics["cache_hits"] += 1
            return self.analysis_cache[text_hash]
        
        self.metrics["cache_misses"] += 1
        
        try:
            gaps = []
            
            # 1. Detectar sentenças incompletas
            incomplete_gaps = self._detect_incomplete_sentences(text)
            gaps.extend(incomplete_gaps)
            
            # 2. Detectar contexto ausente
            context_gaps = self._detect_missing_context(text)
            gaps.extend(context_gaps)
            
            # 3. Detectar referências ambíguas
            ambiguous_gaps = self._detect_ambiguous_references(text)
            gaps.extend(ambiguous_gaps)
            
            # 4. Detectar inconsistências de tom
            tone_gaps = self._detect_inconsistent_tone(text)
            gaps.extend(tone_gaps)
            
            # 5. Detectar detalhes ausentes
            detail_gaps = self._detect_missing_details(text)
            gaps.extend(detail_gaps)
            
            # Calcular métricas
            analysis_time = time.time() - start_time
            confidence_avg = statistics.mean([g.confidence for g in gaps]) if gaps else 0.0
            
            # Atualizar métricas
            self._update_metrics(len(gaps), analysis_time)
            
            # Criar resultado
            result = SemanticAnalysisResult(
                gaps=gaps,
                total_gaps=len(gaps),
                confidence_avg=confidence_avg,
                analysis_time=analysis_time,
                success=True,
                errors=[],
                warnings=[],
                metadata={
                    "nlp_available": self.nlp_model is not None,
                    "embedding_available": self.embedding_model is not None,
                    "gap_types": {gap.gap_type.value: len([g for g in gaps if g.gap_type == gap.gap_type]) for gap in gaps}
                }
            )
            
            # Armazenar no cache
            self.analysis_cache[text_hash] = result
            
            # Limpar cache se necessário
            if len(self.analysis_cache) > 100:
                self.analysis_cache.clear()
            
            logger.info(f"Análise semântica concluída: {len(gaps)} lacunas detectadas")
            return result
            
        except Exception as e:
            error_msg = f"Erro na análise semântica: {str(e)}"
            logger.error(error_msg)
            
            return SemanticAnalysisResult(
                gaps=[],
                total_gaps=0,
                confidence_avg=0.0,
                analysis_time=time.time() - start_time,
                success=False,
                errors=[error_msg],
                warnings=[],
                metadata={"error": str(e)}
            )
    
    def _detect_incomplete_sentences(self, text: str) -> List[SemanticGap]:
        """Detecta sentenças incompletas."""
        gaps = []
        
        # Dividir texto em sentenças
        sentences = self._split_sentences(text)
        
        for i, sentence in enumerate(sentences):
            sentence_start = text.find(sentence)
            sentence_end = sentence_start + len(sentence)
            
            # Verificar padrões de incompletude
            for pattern in self.compiled_patterns:
                if pattern.search(sentence):
                    confidence = self._calculate_incomplete_confidence(sentence, pattern)
                    
                    gap = SemanticGap(
                        gap_type=SemanticAnalysisType.INCOMPLETE_SENTENCE,
                        start_pos=sentence_start,
                        end_pos=sentence_end,
                        context=sentence,
                        confidence=confidence,
                        suggested_placeholder=self._suggest_placeholder_for_incomplete(sentence),
                        analysis_details={
                            "pattern_matched": pattern.pattern,
                            "sentence_index": i,
                            "sentence_length": len(sentence)
                        }
                    )
                    
                    gaps.append(gap)
                    break  # Apenas uma lacuna por sentença
        
        return gaps
    
    def _detect_missing_context(self, text: str) -> List[SemanticGap]:
        """Detecta contexto ausente."""
        gaps = []
        
        if not self.nlp_model:
            return gaps
        
        # Analisar o texto com spaCy
        doc = self.nlp_model(text)
        
        # Procurar por entidades mencionadas sem contexto
        for ent in doc.ents:
            # Verificar se a entidade tem contexto suficiente
            context_window = self._extract_context_window(text, ent.start_char, ent.end_char)
            
            if self._is_lacking_context(ent, context_window):
                confidence = self._calculate_context_confidence(ent, context_window)
                
                gap = SemanticGap(
                    gap_type=SemanticAnalysisType.MISSING_CONTEXT,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    context=context_window,
                    confidence=confidence,
                    suggested_placeholder=self._suggest_placeholder_for_context(ent),
                    analysis_details={
                        "entity_type": ent.label_,
                        "entity_text": ent.text,
                        "context_length": len(context_window)
                    }
                )
                
                gaps.append(gap)
        
        return gaps
    
    def _detect_ambiguous_references(self, text: str) -> List[SemanticGap]:
        """Detecta referências ambíguas."""
        gaps = []
        
        if not self.nlp_model:
            return gaps
        
        doc = self.nlp_model(text)
        
        # Procurar por pronomes e referências
        ambiguous_patterns = [
            r'\b(este|esta|isto|esse|essa|isso)\b',
            r'\b(aqui|ali|lá|onde)\b',
            r'\b(agora|então|depois|antes)\b',
            r'\b(assim|dessa forma|desse modo)\b'
        ]
        
        for pattern in ambiguous_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Verificar se a referência é ambígua
                if self._is_ambiguous_reference(match.group(), text, match.start()):
                    confidence = self._calculate_ambiguity_confidence(match.group(), text, match.start())
                    
                    gap = SemanticGap(
                        gap_type=SemanticAnalysisType.AMBIGUOUS_REFERENCE,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=self._extract_context_window(text, match.start(), match.end()),
                        confidence=confidence,
                        suggested_placeholder=self._suggest_placeholder_for_ambiguous(match.group()),
                        analysis_details={
                            "ambiguous_text": match.group(),
                            "pattern": pattern
                        }
                    )
                    
                    gaps.append(gap)
        
        return gaps
    
    def _detect_inconsistent_tone(self, text: str) -> List[SemanticGap]:
        """Detecta inconsistências de tom."""
        gaps = []
        
        # Padrões de tom
        formal_patterns = [
            r'\b(consequentemente|portanto|assim sendo|dessa forma)\b',
            r'\b(utilizar|obter|realizar|efetuar)\b'
        ]
        
        informal_patterns = [
            r'\b(daí|então|tipo|tipo assim)\b',
            r'\b(usar|pegar|fazer|dar)\b'
        ]
        
        # Contar padrões formais e informais
        formal_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in formal_patterns)
        informal_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in informal_patterns)
        
        # Se há mistura significativa, detectar inconsistência
        if formal_count > 0 and informal_count > 0:
            total_patterns = formal_count + informal_count
            inconsistency_ratio = min(formal_count, informal_count) / total_patterns
            
            if inconsistency_ratio > 0.3:  # Mais de 30% de mistura
                confidence = inconsistency_ratio
                
                gap = SemanticGap(
                    gap_type=SemanticAnalysisType.INCONSISTENT_TONE,
                    start_pos=0,
                    end_pos=len(text),
                    context=text[:200] + "..." if len(text) > 200 else text,
                    confidence=confidence,
                    suggested_placeholder=PlaceholderType.TONE,
                    analysis_details={
                        "formal_patterns": formal_count,
                        "informal_patterns": informal_count,
                        "inconsistency_ratio": inconsistency_ratio
                    }
                )
                
                gaps.append(gap)
        
        return gaps
    
    def _detect_missing_details(self, text: str) -> List[SemanticGap]:
        """Detecta detalhes ausentes."""
        gaps = []
        
        # Padrões que indicam detalhes ausentes
        detail_patterns = [
            (r'\b(especificar|detalhar|explicar)\s+[^.]*$', "detalhes específicos"),
            (r'\b(quantos|quanto|qual)\s+[^.]*$', "quantidade ou especificação"),
            (r'\b(onde|quando|como)\s+[^.]*$', "localização, tempo ou método"),
            (r'\b(por que|para que|como)\s+[^.]*$', "justificativa ou explicação")
        ]
        
        for pattern, detail_type in detail_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                confidence = self._calculate_detail_confidence(match.group(), detail_type)
                
                gap = SemanticGap(
                    gap_type=SemanticAnalysisType.MISSING_DETAILS,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=self._extract_context_window(text, match.start(), match.end()),
                    confidence=confidence,
                    suggested_placeholder=self._suggest_placeholder_for_details(detail_type),
                    analysis_details={
                        "detail_type": detail_type,
                        "pattern_matched": pattern
                    }
                )
                
                gaps.append(gap)
        
        return gaps
    
    def _split_sentences(self, text: str) -> List[str]:
        """Divide texto em sentenças."""
        if self.nlp_model:
            doc = self.nlp_model(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # Fallback simples
            return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _extract_context_window(self, text: str, start: int, end: int, window_size: int = 100) -> str:
        """Extrai janela de contexto."""
        context_start = max(0, start - window_size)
        context_end = min(len(text), end + window_size)
        return text[context_start:context_end].strip()
    
    def _calculate_incomplete_confidence(self, sentence: str, pattern: re.Pattern) -> float:
        """Calcula confiança para sentença incompleta."""
        base_confidence = 0.8
        
        # Ajustar baseado no comprimento da sentença
        if len(sentence) < 20:
            base_confidence *= 0.9
        elif len(sentence) > 100:
            base_confidence *= 1.1
        
        # Ajustar baseado na posição do padrão
        match = pattern.search(sentence)
        if match:
            position_ratio = match.end() / len(sentence)
            if position_ratio > 0.8:  # Padrão no final
                base_confidence *= 1.2
        
        return min(base_confidence, 1.0)
    
    def _calculate_context_confidence(self, entity, context_window: str) -> float:
        """Calcula confiança para contexto ausente."""
        base_confidence = 0.7
        
        # Ajustar baseado no tipo de entidade
        if entity.label_ in ["PERSON", "ORG", "GPE"]:
            base_confidence *= 1.2
        
        # Ajustar baseado no tamanho do contexto
        if len(context_window) < 50:
            base_confidence *= 1.1
        
        return min(base_confidence, 1.0)
    
    def _calculate_ambiguity_confidence(self, ambiguous_text: str, text: str, position: int) -> float:
        """Calcula confiança para referência ambígua."""
        base_confidence = 0.6
        
        # Verificar se há múltiplas ocorrências
        occurrences = len(re.findall(re.escape(ambiguous_text), text, re.IGNORECASE))
        if occurrences > 1:
            base_confidence *= 1.3
        
        # Verificar se está no início do texto
        if position < len(text) * 0.3:
            base_confidence *= 1.2
        
        return min(base_confidence, 1.0)
    
    def _calculate_detail_confidence(self, detail_text: str, detail_type: str) -> float:
        """Calcula confiança para detalhes ausentes."""
        base_confidence = 0.75
        
        # Ajustar baseado no tipo de detalhe
        if "quantidade" in detail_type:
            base_confidence *= 1.1
        elif "justificativa" in detail_type:
            base_confidence *= 1.2
        
        return min(base_confidence, 1.0)
    
    def _is_lacking_context(self, entity, context_window: str) -> bool:
        """Verifica se entidade tem contexto suficiente."""
        # Implementação simplificada
        return len(context_window) < 100
    
    def _is_ambiguous_reference(self, reference: str, text: str, position: int) -> bool:
        """Verifica se referência é ambígua."""
        # Implementação simplificada
        return True  # Para simplificar, considerar todas como ambíguas
    
    def _suggest_placeholder_for_incomplete(self, sentence: str) -> Optional[PlaceholderType]:
        """Sugere placeholder para sentença incompleta."""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ["escreva", "crie", "desenvolva"]):
            return PlaceholderType.CONTENT_TYPE
        elif any(word in sentence_lower for word in ["sobre", "acerca", "relacionado"]):
            return PlaceholderType.PRIMARY_KEYWORD
        elif any(word in sentence_lower for word in ["para", "com", "em"]):
            return PlaceholderType.TARGET_AUDIENCE
        else:
            return PlaceholderType.CUSTOM
    
    def _suggest_placeholder_for_context(self, entity) -> Optional[PlaceholderType]:
        """Sugere placeholder para contexto ausente."""
        if entity.label_ == "PERSON":
            return PlaceholderType.USUARIO
        elif entity.label_ == "ORG":
            return PlaceholderType.CATEGORIA
        elif entity.label_ == "GPE":
            return PlaceholderType.NICHE
        else:
            return PlaceholderType.CUSTOM
    
    def _suggest_placeholder_for_ambiguous(self, reference: str) -> Optional[PlaceholderType]:
        """Sugere placeholder para referência ambígua."""
        reference_lower = reference.lower()
        
        if reference_lower in ["este", "esta", "isto", "esse", "essa", "isso"]:
            return PlaceholderType.PRIMARY_KEYWORD
        elif reference_lower in ["aqui", "ali", "lá", "onde"]:
            return PlaceholderType.NICHE
        elif reference_lower in ["agora", "então", "depois", "antes"]:
            return PlaceholderType.DATA
        else:
            return PlaceholderType.CUSTOM
    
    def _suggest_placeholder_for_details(self, detail_type: str) -> Optional[PlaceholderType]:
        """Sugere placeholder para detalhes ausentes."""
        if "quantidade" in detail_type:
            return PlaceholderType.LENGTH
        elif "localização" in detail_type:
            return PlaceholderType.NICHE
        elif "tempo" in detail_type:
            return PlaceholderType.DATA
        elif "justificativa" in detail_type:
            return PlaceholderType.CUSTOM
        else:
            return PlaceholderType.CUSTOM
    
    def _update_metrics(self, gaps_count: int, analysis_time: float):
        """Atualiza métricas de performance."""
        self.metrics["total_analyses"] += 1
        
        if gaps_count > 0:
            self.metrics["successful_analyses"] += 1
        else:
            self.metrics["failed_analyses"] += 1
        
        self.metrics["analysis_times"].append(analysis_time)
        
        if len(self.metrics["analysis_times"]) > 0:
            self.metrics["avg_analysis_time"] = statistics.mean(self.metrics["analysis_times"])
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de análise."""
        return {
            "total_analyses": self.metrics["total_analyses"],
            "successful_analyses": self.metrics["successful_analyses"],
            "failed_analyses": self.metrics["failed_analyses"],
            "success_rate": self.metrics["successful_analyses"] / self.metrics["total_analyses"] if self.metrics["total_analyses"] > 0 else 0.0,
            "avg_analysis_time": self.metrics["avg_analysis_time"],
            "gap_types_detected": dict(self.metrics["gap_types_detected"]),
            "cache_hit_rate": self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0.0,
            "nlp_available": self.nlp_model is not None,
            "embedding_available": self.embedding_model is not None
        }


# Funções de conveniência
def detect_semantic_gaps(text: str) -> SemanticAnalysisResult:
    """Detecta lacunas semânticas no texto."""
    detector = SemanticLacunaDetector()
    return detector.detect_semantic_gaps(text)


def get_semantic_analysis_stats() -> Dict[str, Any]:
    """Obtém estatísticas de análise semântica."""
    detector = SemanticLacunaDetector()
    return detector.get_analysis_statistics()


# Instância global para uso em outros módulos
semantic_detector = SemanticLacunaDetector() 