#!/usr/bin/env python3
"""
Matcher Semântico - Omni Keywords Finder
========================================

Tracing ID: SEMANTIC_MATCHER_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema de matching semântico que:
- Encontra melhor correspondência entre lacunas e candidatos
- Usa embeddings semânticos
- Calcula similaridade contextual
- Aplica filtros inteligentes
- Cache de resultados

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.4
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
    logging.warning("Dependências NLP não disponíveis. Matcher semântico será limitado.")

# Importar classes do sistema
from .hybrid_lacuna_detector_imp001 import (
    DetectedGap,
    PlaceholderType
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingStrategy(Enum):
    """Estratégias de matching."""
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CONTEXTUAL_MATCHING = "contextual_matching"
    KEYWORD_MATCHING = "keyword_matching"
    HYBRID_MATCHING = "hybrid_matching"
    FALLBACK_MATCHING = "fallback_matching"


@dataclass
class MatchResult:
    """Resultado de um match."""
    candidate: str
    similarity_score: float
    confidence: float
    strategy_used: MatchingStrategy
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MatchingResult:
    """Resultado completo do matching."""
    best_match: Optional[MatchResult]
    all_matches: List[MatchResult]
    total_candidates: int
    matching_time: float
    success: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SemanticMatcher:
    """Matcher semântico avançado."""
    
    def __init__(self):
        """Inicializa o matcher semântico."""
        self.nlp_model = None
        self.embedding_model = None
        self.matching_cache = {}
        self.cache_ttl = 1800  # 30 minutos
        
        # Configurações de matching
        self.similarity_threshold = 0.7
        self.max_candidates = 10
        self.context_window_size = 200
        
        # Filtros de matching
        self.matching_filters = self._create_matching_filters()
        
        # Inicializar modelos NLP se disponíveis
        if NLP_AVAILABLE:
            self._initialize_nlp_models()
        
        # Métricas
        self.metrics = {
            "total_matches": 0,
            "successful_matches": 0,
            "failed_matches": 0,
            "avg_matching_time": 0.0,
            "matching_times": deque(maxlen=1000),
            "strategy_usage": defaultdict(int),
            "avg_similarity_score": 0.0,
            "similarity_scores": deque(maxlen=1000),
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info("SemanticMatcher inicializado")
    
    def _initialize_nlp_models(self):
        """Inicializa modelos NLP."""
        try:
            # Carregar modelo spaCy
            self.nlp_model = spacy.load("pt_core_news_sm")
            logger.info("Modelo spaCy carregado para matching semântico")
        except OSError:
            try:
                # Tentar carregar modelo em inglês como fallback
                self.nlp_model = spacy.load("en_core_web_sm")
                logger.warning("Modelo spaCy em português não encontrado. Usando modelo em inglês.")
            except OSError:
                logger.warning("Modelo spaCy não disponível. Matching semântico limitado.")
                self.nlp_model = None
        
        try:
            # Carregar modelo de embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Modelo de embeddings carregado para matching semântico")
        except Exception as e:
            logger.warning(f"Modelo de embeddings não disponível: {e}")
            self.embedding_model = None
    
    def _create_matching_filters(self) -> Dict[str, Any]:
        """Cria filtros de matching."""
        return {
            "length_filter": {
                "enabled": True,
                "min_ratio": 0.3,
                "max_ratio": 3.0
            },
            "keyword_filter": {
                "enabled": True,
                "min_keyword_match": 0.2
            },
            "domain_filter": {
                "enabled": True,
                "strict_domain": False
            },
            "quality_filter": {
                "enabled": True,
                "min_quality_score": 0.5
            }
        }
    
    def find_best_match(self, gap: DetectedGap, candidates: List[str]) -> MatchingResult:
        """
        Encontra a melhor correspondência para uma lacuna.
        
        Args:
            gap: Lacuna detectada
            candidates: Lista de candidatos
            
        Returns:
            Resultado do matching
        """
        start_time = time.time()
        
        # Verificar cache
        cache_key = f"{gap.placeholder_type.value}_{hash(tuple(candidates))}_{hash(gap.context)}"
        if cache_key in self.matching_cache:
            self.metrics["cache_hits"] += 1
            return self.matching_cache[cache_key]
        
        self.metrics["cache_misses"] += 1
        
        try:
            if not candidates:
                return MatchingResult(
                    best_match=None,
                    all_matches=[],
                    total_candidates=0,
                    matching_time=time.time() - start_time,
                    success=False,
                    errors=["Nenhum candidato fornecido"],
                    warnings=[]
                )
            
            # 1. Aplicar filtros iniciais
            filtered_candidates = self._apply_initial_filters(gap, candidates)
            
            if not filtered_candidates:
                return MatchingResult(
                    best_match=None,
                    all_matches=[],
                    total_candidates=len(candidates),
                    matching_time=time.time() - start_time,
                    success=False,
                    errors=["Nenhum candidato passou pelos filtros iniciais"],
                    warnings=[]
                )
            
            # 2. Calcular scores de similaridade
            matches = []
            
            for candidate in filtered_candidates:
                # Matching semântico
                semantic_score = self._calculate_semantic_similarity(gap, candidate)
                
                # Matching contextual
                contextual_score = self._calculate_contextual_similarity(gap, candidate)
                
                # Matching por keywords
                keyword_score = self._calculate_keyword_similarity(gap, candidate)
                
                # Score híbrido
                hybrid_score = self._calculate_hybrid_score(semantic_score, contextual_score, keyword_score)
                
                # Determinar estratégia usada
                strategy = self._determine_strategy(semantic_score, contextual_score, keyword_score)
                
                # Calcular confiança
                confidence = self._calculate_confidence(hybrid_score, strategy)
                
                match = MatchResult(
                    candidate=candidate,
                    similarity_score=hybrid_score,
                    confidence=confidence,
                    strategy_used=strategy,
                    metadata={
                        "semantic_score": semantic_score,
                        "contextual_score": contextual_score,
                        "keyword_score": keyword_score,
                        "passed_filters": True
                    }
                )
                
                matches.append(match)
            
            # 3. Ordenar por score
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # 4. Selecionar melhor match
            best_match = matches[0] if matches and matches[0].similarity_score >= self.similarity_threshold else None
            
            # 5. Criar resultado
            matching_time = time.time() - start_time
            result = MatchingResult(
                best_match=best_match,
                all_matches=matches,
                total_candidates=len(candidates),
                matching_time=matching_time,
                success=best_match is not None,
                errors=[],
                warnings=[],
                metadata={
                    "gap_type": gap.placeholder_type.value,
                    "candidates_analyzed": len(matches),
                    "similarity_threshold": self.similarity_threshold,
                    "best_score": best_match.similarity_score if best_match else 0.0
                }
            )
            
            # Armazenar no cache
            self.matching_cache[cache_key] = result
            
            # Limpar cache se necessário
            if len(self.matching_cache) > 100:
                self.matching_cache.clear()
            
            # Atualizar métricas
            self._update_metrics(result)
            
            logger.info(f"Matching concluído: {len(matches)} candidatos analisados, melhor score: {best_match.similarity_score if best_match else 0.0:.3f}")
            return result
            
        except Exception as e:
            error_msg = f"Erro no matching semântico: {str(e)}"
            logger.error(error_msg)
            
            return MatchingResult(
                best_match=None,
                all_matches=[],
                total_candidates=len(candidates),
                matching_time=time.time() - start_time,
                success=False,
                errors=[error_msg],
                warnings=[]
            )
    
    def _apply_initial_filters(self, gap: DetectedGap, candidates: List[str]) -> List[str]:
        """Aplica filtros iniciais aos candidatos."""
        filtered_candidates = []
        
        for candidate in candidates:
            if not candidate or not candidate.strip():
                continue
            
            # Filtro de comprimento
            if self.matching_filters["length_filter"]["enabled"]:
                if not self._passes_length_filter(gap, candidate):
                    continue
            
            # Filtro de keywords
            if self.matching_filters["keyword_filter"]["enabled"]:
                if not self._passes_keyword_filter(gap, candidate):
                    continue
            
            # Filtro de domínio
            if self.matching_filters["domain_filter"]["enabled"]:
                if not self._passes_domain_filter(gap, candidate):
                    continue
            
            # Filtro de qualidade
            if self.matching_filters["quality_filter"]["enabled"]:
                if not self._passes_quality_filter(candidate):
                    continue
            
            filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def _passes_length_filter(self, gap: DetectedGap, candidate: str) -> bool:
        """Verifica se candidato passa no filtro de comprimento."""
        if not gap.context:
            return True
        
        context_length = len(gap.context)
        candidate_length = len(candidate)
        
        min_ratio = self.matching_filters["length_filter"]["min_ratio"]
        max_ratio = self.matching_filters["length_filter"]["max_ratio"]
        
        if context_length == 0:
            return True
        
        ratio = candidate_length / context_length
        return min_ratio <= ratio <= max_ratio
    
    def _passes_keyword_filter(self, gap: DetectedGap, candidate: str) -> bool:
        """Verifica se candidato passa no filtro de keywords."""
        if not gap.context or not candidate:
            return True
        
        # Extrair keywords do contexto
        context_keywords = self._extract_keywords(gap.context)
        candidate_keywords = self._extract_keywords(candidate)
        
        if not context_keywords or not candidate_keywords:
            return True
        
        # Calcular sobreposição
        intersection = set(context_keywords) & set(candidate_keywords)
        union = set(context_keywords) | set(candidate_keywords)
        
        if not union:
            return True
        
        overlap_ratio = len(intersection) / len(union)
        min_overlap = self.matching_filters["keyword_filter"]["min_keyword_match"]
        
        return overlap_ratio >= min_overlap
    
    def _passes_domain_filter(self, gap: DetectedGap, candidate: str) -> bool:
        """Verifica se candidato passa no filtro de domínio."""
        # Implementação simplificada
        # Em uma implementação real, usaria análise de domínio mais avançada
        return True
    
    def _passes_quality_filter(self, candidate: str) -> bool:
        """Verifica se candidato passa no filtro de qualidade."""
        if not candidate:
            return False
        
        # Verificar se não é muito curto
        if len(candidate.strip()) < 2:
            return False
        
        # Verificar se não é muito longo
        if len(candidate) > 500:
            return False
        
        # Verificar se não contém apenas caracteres especiais
        if not re.search(r'[a-zA-Z0-9]', candidate):
            return False
        
        return True
    
    def _calculate_semantic_similarity(self, gap: DetectedGap, candidate: str) -> float:
        """Calcula similaridade semântica."""
        if not self.embedding_model or not gap.context or not candidate:
            return 0.5  # Score neutro
        
        try:
            # Calcular embeddings
            context_embedding = self.embedding_model.encode([gap.context])
            candidate_embedding = self.embedding_model.encode([candidate])
            
            # Calcular similaridade cosseno
            similarity = cosine_similarity(context_embedding, candidate_embedding)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"Erro no cálculo de similaridade semântica: {e}")
            return 0.5
    
    def _calculate_contextual_similarity(self, gap: DetectedGap, candidate: str) -> float:
        """Calcula similaridade contextual."""
        if not gap.context or not candidate:
            return 0.5
        
        try:
            # Extrair contexto expandido
            expanded_context = self._extract_expanded_context(gap.context)
            
            # Calcular similaridade baseada em palavras-chave
            context_keywords = self._extract_keywords(expanded_context)
            candidate_keywords = self._extract_keywords(candidate)
            
            if not context_keywords or not candidate_keywords:
                return 0.5
            
            # Calcular Jaccard similarity
            intersection = set(context_keywords) & set(candidate_keywords)
            union = set(context_keywords) | set(candidate_keywords)
            
            if not union:
                return 0.5
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.warning(f"Erro no cálculo de similaridade contextual: {e}")
            return 0.5
    
    def _calculate_keyword_similarity(self, gap: DetectedGap, candidate: str) -> float:
        """Calcula similaridade por keywords."""
        if not gap.context or not candidate:
            return 0.5
        
        try:
            # Extrair keywords importantes
            context_keywords = self._extract_important_keywords(gap.context)
            candidate_keywords = self._extract_important_keywords(candidate)
            
            if not context_keywords or not candidate_keywords:
                return 0.5
            
            # Calcular similaridade ponderada
            total_score = 0.0
            total_weight = 0.0
            
            for context_kw, context_weight in context_keywords.items():
                for candidate_kw, candidate_weight in candidate_keywords.items():
                    # Calcular similaridade entre keywords
                    kw_similarity = self._calculate_keyword_similarity_score(context_kw, candidate_kw)
                    weight = context_weight * candidate_weight
                    
                    total_score += kw_similarity * weight
                    total_weight += weight
            
            if total_weight == 0:
                return 0.5
            
            return total_score / total_weight
            
        except Exception as e:
            logger.warning(f"Erro no cálculo de similaridade por keywords: {e}")
            return 0.5
    
    def _calculate_hybrid_score(self, semantic_score: float, contextual_score: float, keyword_score: float) -> float:
        """Calcula score híbrido."""
        # Pesos para cada tipo de score
        weights = {
            "semantic": 0.4,
            "contextual": 0.35,
            "keyword": 0.25
        }
        
        hybrid_score = (
            semantic_score * weights["semantic"] +
            contextual_score * weights["contextual"] +
            keyword_score * weights["keyword"]
        )
        
        return min(max(hybrid_score, 0.0), 1.0)
    
    def _determine_strategy(self, semantic_score: float, contextual_score: float, keyword_score: float) -> MatchingStrategy:
        """Determina estratégia usada baseada nos scores."""
        if semantic_score > 0.8:
            return MatchingStrategy.SEMANTIC_SIMILARITY
        elif contextual_score > 0.7:
            return MatchingStrategy.CONTEXTUAL_MATCHING
        elif keyword_score > 0.6:
            return MatchingStrategy.KEYWORD_MATCHING
        elif max(semantic_score, contextual_score, keyword_score) > 0.5:
            return MatchingStrategy.HYBRID_MATCHING
        else:
            return MatchingStrategy.FALLBACK_MATCHING
    
    def _calculate_confidence(self, hybrid_score: float, strategy: MatchingStrategy) -> float:
        """Calcula confiança do match."""
        base_confidence = hybrid_score
        
        # Ajustar baseado na estratégia
        strategy_confidence_boost = {
            MatchingStrategy.SEMANTIC_SIMILARITY: 1.1,
            MatchingStrategy.CONTEXTUAL_MATCHING: 1.05,
            MatchingStrategy.KEYWORD_MATCHING: 1.0,
            MatchingStrategy.HYBRID_MATCHING: 0.95,
            MatchingStrategy.FALLBACK_MATCHING: 0.8
        }
        
        boost = strategy_confidence_boost.get(strategy, 1.0)
        confidence = base_confidence * boost
        
        return min(max(confidence, 0.0), 1.0)
    
    def _extract_expanded_context(self, context: str) -> str:
        """Extrai contexto expandido."""
        # Implementação simplificada
        # Em uma implementação real, usaria análise mais avançada
        return context
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai keywords do texto."""
        if not text:
            return []
        
        # Remover pontuação e converter para minúsculas
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Dividir em palavras
        words = text_clean.split()
        
        # Filtrar palavras muito curtas ou muito longas
        keywords = [word for word in words if 3 <= len(word) <= 20]
        
        # Remover palavras comuns (stop words)
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
            'e', 'ou', 'mas', 'porém', 'contudo', 'entretanto',
            'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos',
            'para', 'com', 'sem', 'sob', 'sobre', 'entre', 'contra',
            'que', 'qual', 'quais', 'quem', 'onde', 'quando', 'como',
            'por', 'que', 'porque', 'pois', 'já', 'ainda', 'sempre', 'nunca'
        }
        
        keywords = [word for word in keywords if word not in stop_words]
        
        return keywords
    
    def _extract_important_keywords(self, text: str) -> Dict[str, float]:
        """Extrai keywords importantes com pesos."""
        keywords = self._extract_keywords(text)
        
        if not keywords:
            return {}
        
        # Contar frequência
        keyword_counts = defaultdict(int)
        for keyword in keywords:
            keyword_counts[keyword] += 1
        
        # Calcular pesos baseados na frequência e comprimento
        total_keywords = len(keywords)
        keyword_weights = {}
        
        for keyword, count in keyword_counts.items():
            # Peso baseado na frequência
            frequency_weight = count / total_keywords
            
            # Peso baseado no comprimento (palavras mais longas são mais importantes)
            length_weight = min(len(keyword) / 10.0, 1.0)
            
            # Peso combinado
            combined_weight = (frequency_weight + length_weight) / 2.0
            
            keyword_weights[keyword] = combined_weight
        
        return keyword_weights
    
    def _calculate_keyword_similarity_score(self, kw1: str, kw2: str) -> float:
        """Calcula similaridade entre duas keywords."""
        if kw1 == kw2:
            return 1.0
        
        # Similaridade por prefixo/sufixo
        if kw1.startswith(kw2) or kw2.startswith(kw1):
            return 0.8
        
        # Similaridade por comprimento
        length_diff = abs(len(kw1) - len(kw2))
        max_length = max(len(kw1), len(kw2))
        
        if max_length == 0:
            return 0.0
        
        length_similarity = 1.0 - (length_diff / max_length)
        
        # Similaridade por caracteres comuns
        common_chars = set(kw1) & set(kw2)
        total_chars = set(kw1) | set(kw2)
        
        if not total_chars:
            return 0.0
        
        char_similarity = len(common_chars) / len(total_chars)
        
        # Score combinado
        combined_score = (length_similarity + char_similarity) / 2.0
        
        return min(max(combined_score, 0.0), 1.0)
    
    def _update_metrics(self, result: MatchingResult):
        """Atualiza métricas de matching."""
        self.metrics["total_matches"] += 1
        
        if result.success:
            self.metrics["successful_matches"] += 1
        else:
            self.metrics["failed_matches"] += 1
        
        self.metrics["matching_times"].append(result.matching_time)
        
        if result.best_match:
            self.metrics["similarity_scores"].append(result.best_match.similarity_score)
            self.metrics["strategy_usage"][result.best_match.strategy_used.value] += 1
        
        # Atualizar médias
        if len(self.metrics["matching_times"]) > 0:
            self.metrics["avg_matching_time"] = statistics.mean(self.metrics["matching_times"])
        
        if len(self.metrics["similarity_scores"]) > 0:
            self.metrics["avg_similarity_score"] = statistics.mean(self.metrics["similarity_scores"])
    
    def get_matching_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de matching."""
        return {
            "total_matches": self.metrics["total_matches"],
            "successful_matches": self.metrics["successful_matches"],
            "failed_matches": self.metrics["failed_matches"],
            "success_rate": self.metrics["successful_matches"] / self.metrics["total_matches"] if self.metrics["total_matches"] > 0 else 0.0,
            "avg_matching_time": self.metrics["avg_matching_time"],
            "avg_similarity_score": self.metrics["avg_similarity_score"],
            "strategy_usage": dict(self.metrics["strategy_usage"]),
            "cache_hit_rate": self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0.0,
            "nlp_available": self.nlp_model is not None,
            "embedding_available": self.embedding_model is not None
        }


# Funções de conveniência
def find_best_match(gap: DetectedGap, candidates: List[str]) -> MatchingResult:
    """Encontra a melhor correspondência para uma lacuna."""
    matcher = SemanticMatcher()
    return matcher.find_best_match(gap, candidates)


def get_semantic_matching_stats() -> Dict[str, Any]:
    """Obtém estatísticas de matching semântico."""
    matcher = SemanticMatcher()
    return matcher.get_matching_statistics()


# Instância global para uso em outros módulos
semantic_matcher = SemanticMatcher() 