#!/usr/bin/env python3
"""
Validador de Contexto - Versão Avançada
=======================================

Tracing ID: CONTEXT_VALIDATOR_IMP003_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema de validação contextual que:
- Valida se lacunas fazem sentido no contexto
- Verifica coerência semântica
- Analisa fluxo lógico do texto
- Detecta inconsistências contextuais
- Fornece sugestões de melhoria
- Integra com sistema semântico

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.3
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

from .placeholder_unification_system_imp001 import (
    PlaceholderType,
    PlaceholderUnificationSystem
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextValidationType(Enum):
    """Tipos de validação contextual."""
    SEMANTIC_COHERENCE = "semantic_coherence"
    LOGICAL_FLOW = "logical_flow"
    CONTEXTUAL_CONSISTENCY = "contextual_consistency"
    PLACEHOLDER_RELEVANCE = "placeholder_relevance"
    CONTENT_STRUCTURE = "content_structure"


class ValidationSeverity(Enum):
    """Níveis de severidade da validação."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ContextValidationIssue:
    """Problema de validação contextual."""
    validation_type: ContextValidationType
    severity: ValidationSeverity
    description: str
    position: Tuple[int, int]
    context: str
    suggestion: str
    confidence: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ContextValidationResult:
    """Resultado da validação contextual."""
    is_valid: bool
    overall_score: float
    issues: List[ContextValidationIssue]
    warnings: List[str]
    suggestions: List[str]
    validation_time: float
    context_analysis: Dict[str, Any]
    coherence_score: float
    flow_score: float
    consistency_score: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContextAnalyzer:
    """Analisador de contexto avançado."""
    
    def __init__(self):
        """Inicializa o analisador de contexto."""
        self.context_window_size = 300
        self.min_coherence_threshold = 0.6
        self.max_flow_distance = 100
        
        # Padrões de análise contextual
        self.context_patterns = self._create_context_patterns()
        
        # Regras de coerência
        self.coherence_rules = self._create_coherence_rules()
        
        # Padrões de fluxo lógico
        self.flow_patterns = self._create_flow_patterns()
        
        # Métricas de performance
        self.metrics = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "avg_analysis_time": 0.0,
            "analysis_times": deque(maxlen=1000),
            "coherence_scores": deque(maxlen=1000),
            "flow_scores": deque(maxlen=1000)
        }
        
        logger.info("ContextAnalyzer inicializado")
    
    def _create_context_patterns(self) -> Dict[str, List[str]]:
        """Cria padrões para análise contextual."""
        return {
            "topic_indicators": [
                r"sobre\s+([^,\.]+)",
                r"relacionado\s+a\s+([^,\.]+)",
                r"focado\s+em\s+([^,\.]+)",
                r"especializado\s+em\s+([^,\.]+)"
            ],
            "audience_indicators": [
                r"para\s+([^,\.]+)",
                r"direcionado\s+a\s+([^,\.]+)",
                r"voltado\s+para\s+([^,\.]+)",
                r"focado\s+em\s+([^,\.]+)"
            ],
            "intent_indicators": [
                r"objetivo\s+([^,\.]+)",
                r"meta\s+([^,\.]+)",
                r"propósito\s+([^,\.]+)",
                r"intenção\s+([^,\.]+)"
            ],
            "content_indicators": [
                r"tipo\s+de\s+conteúdo\s+([^,\.]+)",
                r"formato\s+([^,\.]+)",
                r"estilo\s+([^,\.]+)",
                r"abordagem\s+([^,\.]+)"
            ]
        }
    
    def _create_coherence_rules(self) -> List[Dict[str, Any]]:
        """Cria regras de coerência contextual."""
        return [
            {
                "name": "topic_consistency",
                "description": "Verifica se o tópico é consistente",
                "weight": 0.3,
                "pattern": r"tópico\s+([^,\.]+)",
                "validation": "same_topic"
            },
            {
                "name": "audience_alignment",
                "description": "Verifica se a audiência está alinhada",
                "weight": 0.25,
                "pattern": r"audiência\s+([^,\.]+)",
                "validation": "audience_match"
            },
            {
                "name": "intent_consistency",
                "description": "Verifica se a intenção é consistente",
                "weight": 0.25,
                "pattern": r"intenção\s+([^,\.]+)",
                "validation": "intent_match"
            },
            {
                "name": "content_type_alignment",
                "description": "Verifica se o tipo de conteúdo está alinhado",
                "weight": 0.2,
                "pattern": r"tipo\s+([^,\.]+)",
                "validation": "content_type_match"
            }
        ]
    
    def _create_flow_patterns(self) -> Dict[str, List[str]]:
        """Cria padrões de fluxo lógico."""
        return {
            "introduction": [
                r"introdução",
                r"apresentação",
                r"contexto",
                r"background"
            ],
            "development": [
                r"desenvolvimento",
                r"análise",
                r"discussão",
                r"exploração"
            ],
            "conclusion": [
                r"conclusão",
                r"resumo",
                r"finalização",
                r"encerramento"
            ],
            "transition": [
                r"além\s+disso",
                r"por\s+outro\s+lado",
                r"entretanto",
                r"portanto"
            ]
        }
    
    def analyze_context_coherence(self, text: str, gaps: List[DetectedGap]) -> Dict[str, Any]:
        """
        Analisa a coerência contextual do texto com as lacunas.
        
        Args:
            text: Texto completo
            gaps: Lacunas detectadas
            
        Returns:
            Análise de coerência contextual
        """
        start_time = time.time()
        
        try:
            # Extrair contexto geral
            general_context = self._extract_general_context(text)
            
            # Analisar cada lacuna no contexto
            gap_analyses = []
            for gap in gaps:
                gap_analysis = self._analyze_gap_context(text, gap, general_context)
                gap_analyses.append(gap_analysis)
            
            # Calcular coerência geral
            coherence_score = self._calculate_overall_coherence(gap_analyses, general_context)
            
            # Detectar inconsistências
            inconsistencies = self._detect_contextual_inconsistencies(gap_analyses, general_context)
            
            # Analisar fluxo lógico
            flow_analysis = self._analyze_logical_flow(text, gaps)
            
            analysis_result = {
                "general_context": general_context,
                "gap_analyses": gap_analyses,
                "coherence_score": coherence_score,
                "inconsistencies": inconsistencies,
                "flow_analysis": flow_analysis,
                "analysis_time": time.time() - start_time
            }
            
            # Atualizar métricas
            self._update_metrics(True, time.time() - start_time, coherence_score)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erro na análise de coerência contextual: {e}")
            self._update_metrics(False, 0.0, 0.0)
            
            return {
                "general_context": {},
                "gap_analyses": [],
                "coherence_score": 0.0,
                "inconsistencies": [],
                "flow_analysis": {},
                "analysis_time": 0.0,
                "error": str(e)
            }
    
    def _extract_general_context(self, text: str) -> Dict[str, Any]:
        """Extrai contexto geral do texto."""
        context = {
            "topics": [],
            "audiences": [],
            "intents": [],
            "content_types": [],
            "tone": "neutro",
            "complexity": "médio"
        }
        
        # Extrair tópicos
        for pattern in self.context_patterns["topic_indicators"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            context["topics"].extend(matches)
        
        # Extrair audiências
        for pattern in self.context_patterns["audience_indicators"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            context["audiences"].extend(matches)
        
        # Extrair intenções
        for pattern in self.context_patterns["intent_indicators"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            context["intents"].extend(matches)
        
        # Extrair tipos de conteúdo
        for pattern in self.context_patterns["content_indicators"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            context["content_types"].extend(matches)
        
        # Detectar tom
        context["tone"] = self._detect_text_tone(text)
        
        # Detectar complexidade
        context["complexity"] = self._detect_text_complexity(text)
        
        # Remover duplicatas
        for key in ["topics", "audiences", "intents", "content_types"]:
            context[key] = list(set(context[key]))
        
        return context
    
    def _analyze_gap_context(self, text: str, gap: DetectedGap, general_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o contexto de uma lacuna específica."""
        # Extrair contexto local
        start = max(0, gap.start_pos - self.context_window_size)
        end = min(len(text), gap.end_pos + self.context_window_size)
        local_context = text[start:end]
        
        # Analisar relevância do placeholder
        placeholder_relevance = self._analyze_placeholder_relevance(gap, local_context, general_context)
        
        # Verificar coerência com contexto geral
        coherence_with_general = self._check_coherence_with_general(gap, general_context)
        
        # Analisar posição no fluxo
        position_in_flow = self._analyze_position_in_flow(gap, text)
        
        return {
            "gap": gap,
            "local_context": local_context,
            "placeholder_relevance": placeholder_relevance,
            "coherence_with_general": coherence_with_general,
            "position_in_flow": position_in_flow,
            "context_score": (placeholder_relevance + coherence_with_general) / 2
        }
    
    def _analyze_placeholder_relevance(self, gap: DetectedGap, local_context: str, general_context: Dict[str, Any]) -> float:
        """Analisa a relevância do placeholder no contexto local."""
        placeholder_type = gap.placeholder_type.value
        
        # Verificar se o tipo de placeholder faz sentido no contexto
        if "keyword" in placeholder_type:
            # Verificar se há indicações de palavras-chave no contexto
            keyword_indicators = ["palavra-chave", "keyword", "termo", "conceito"]
            relevance = sum(1 for indicator in keyword_indicators if indicator in local_context.lower()) / len(keyword_indicators)
            return min(1.0, relevance)
        
        elif "audience" in placeholder_type:
            # Verificar se há indicações de audiência no contexto
            audience_indicators = ["público", "audiência", "usuários", "leitores"]
            relevance = sum(1 for indicator in audience_indicators if indicator in local_context.lower()) / len(audience_indicators)
            return min(1.0, relevance)
        
        elif "content" in placeholder_type:
            # Verificar se há indicações de conteúdo no contexto
            content_indicators = ["conteúdo", "artigo", "texto", "material"]
            relevance = sum(1 for indicator in content_indicators if indicator in local_context.lower()) / len(content_indicators)
            return min(1.0, relevance)
        
        else:
            return 0.7  # Relevância padrão para outros tipos
    
    def _check_coherence_with_general(self, gap: DetectedGap, general_context: Dict[str, Any]) -> float:
        """Verifica coerência com o contexto geral."""
        placeholder_type = gap.placeholder_type.value
        coherence_score = 0.8  # Score base
        
        # Verificar se há tópicos definidos para placeholders de keyword
        if "keyword" in placeholder_type and general_context["topics"]:
            coherence_score += 0.1
        
        # Verificar se há audiências definidas para placeholders de audience
        if "audience" in placeholder_type and general_context["audiences"]:
            coherence_score += 0.1
        
        # Verificar se há intenções definidas para placeholders de content
        if "content" in placeholder_type and general_context["intents"]:
            coherence_score += 0.1
        
        return min(1.0, coherence_score)
    
    def _analyze_position_in_flow(self, gap: DetectedGap, text: str) -> Dict[str, Any]:
        """Analisa a posição da lacuna no fluxo do texto."""
        # Determinar se está no início, meio ou fim
        text_length = len(text)
        position_ratio = gap.start_pos / text_length
        
        if position_ratio < 0.3:
            flow_position = "início"
        elif position_ratio < 0.7:
            flow_position = "meio"
        else:
            flow_position = "fim"
        
        # Verificar se há transições próximas
        nearby_transitions = self._find_nearby_transitions(text, gap.start_pos)
        
        return {
            "position": flow_position,
            "position_ratio": position_ratio,
            "nearby_transitions": nearby_transitions,
            "flow_appropriate": self._is_flow_appropriate(gap, flow_position)
        }
    
    def _find_nearby_transitions(self, text: str, position: int) -> List[str]:
        """Encontra transições próximas à posição."""
        transitions = []
        search_start = max(0, position - 100)
        search_end = min(len(text), position + 100)
        search_text = text[search_start:search_end]
        
        for flow_type, patterns in self.flow_patterns.items():
            for pattern in patterns:
                if re.search(pattern, search_text, re.IGNORECASE):
                    transitions.append(flow_type)
        
        return list(set(transitions))
    
    def _is_flow_appropriate(self, gap: DetectedGap, flow_position: str) -> bool:
        """Verifica se a lacuna é apropriada para a posição no fluxo."""
        placeholder_type = gap.placeholder_type.value
        
        # Regras de apropriação por posição
        if flow_position == "início":
            # No início, placeholders de contexto são apropriados
            return any(keyword in placeholder_type for keyword in ["keyword", "topic", "audience"])
        
        elif flow_position == "meio":
            # No meio, placeholders de desenvolvimento são apropriados
            return any(keyword in placeholder_type for keyword in ["content", "detail", "example"])
        
        elif flow_position == "fim":
            # No fim, placeholders de conclusão são apropriados
            return any(keyword in placeholder_type for keyword in ["summary", "conclusion", "call_to_action"])
        
        return True
    
    def _calculate_overall_coherence(self, gap_analyses: List[Dict[str, Any]], general_context: Dict[str, Any]) -> float:
        """Calcula a coerência geral do texto."""
        if not gap_analyses:
            return 1.0  # Texto sem lacunas é considerado coerente
        
        # Média dos scores de contexto das lacunas
        context_scores = [analysis["context_score"] for analysis in gap_analyses]
        avg_context_score = statistics.mean(context_scores)
        
        # Fator de coerência baseado no contexto geral
        general_coherence = 0.8  # Score base
        
        # Ajustar baseado na presença de elementos contextuais
        if general_context["topics"]:
            general_coherence += 0.1
        if general_context["audiences"]:
            general_coherence += 0.1
        
        # Combinar scores
        overall_coherence = (avg_context_score + general_coherence) / 2
        
        return min(1.0, max(0.0, overall_coherence))
    
    def _detect_contextual_inconsistencies(self, gap_analyses: List[Dict[str, Any]], general_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta inconsistências contextuais."""
        inconsistencies = []
        
        # Verificar inconsistências entre lacunas
        for i, analysis1 in enumerate(gap_analyses):
            for j, analysis2 in enumerate(gap_analyses[i+1:], i+1):
                inconsistency = self._check_gap_inconsistency(analysis1, analysis2)
                if inconsistency:
                    inconsistencies.append(inconsistency)
        
        # Verificar inconsistências com contexto geral
        for analysis in gap_analyses:
            inconsistency = self._check_general_inconsistency(analysis, general_context)
            if inconsistency:
                inconsistencies.append(inconsistency)
        
        return inconsistencies
    
    def _check_gap_inconsistency(self, analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verifica inconsistência entre duas lacunas."""
        gap1 = analysis1["gap"]
        gap2 = analysis2["gap"]
        
        # Verificar se há placeholders conflitantes
        if gap1.placeholder_type == gap2.placeholder_type:
            # Mesmo tipo de placeholder pode indicar redundância
            if abs(gap1.start_pos - gap2.start_pos) < 50:  # Muito próximos
                return {
                    "type": "redundant_placeholders",
                    "description": f"Placeholders redundantes do tipo {gap1.placeholder_type.value}",
                    "severity": "medium",
                    "position": (gap1.start_pos, gap2.end_pos)
                }
        
        return None
    
    def _check_general_inconsistency(self, analysis: Dict[str, Any], general_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verifica inconsistência com contexto geral."""
        gap = analysis["gap"]
        placeholder_type = gap.placeholder_type.value
        
        # Verificar se placeholder de keyword está presente mas não há tópicos definidos
        if "keyword" in placeholder_type and not general_context["topics"]:
            return {
                "type": "missing_topic_context",
                "description": "Placeholder de keyword sem contexto de tópico",
                "severity": "high",
                "position": (gap.start_pos, gap.end_pos)
            }
        
        # Verificar se placeholder de audience está presente mas não há audiências definidas
        if "audience" in placeholder_type and not general_context["audiences"]:
            return {
                "type": "missing_audience_context",
                "description": "Placeholder de audiência sem contexto de público",
                "severity": "high",
                "position": (gap.start_pos, gap.end_pos)
            }
        
        return None
    
    def _analyze_logical_flow(self, text: str, gaps: List[DetectedGap]) -> Dict[str, Any]:
        """Analisa o fluxo lógico do texto."""
        # Detectar seções do texto
        sections = self._detect_text_sections(text)
        
        # Analisar distribuição das lacunas por seção
        gap_distribution = self._analyze_gap_distribution(gaps, sections)
        
        # Verificar se o fluxo faz sentido
        flow_coherence = self._check_flow_coherence(gap_distribution)
        
        return {
            "sections": sections,
            "gap_distribution": gap_distribution,
            "flow_coherence": flow_coherence,
            "flow_score": self._calculate_flow_score(gap_distribution, flow_coherence)
        }
    
    def _detect_text_sections(self, text: str) -> List[Dict[str, Any]]:
        """Detecta seções do texto."""
        sections = []
        
        # Padrões de início de seção
        section_patterns = [
            (r"introdução", "introdução"),
            (r"desenvolvimento", "desenvolvimento"),
            (r"conclusão", "conclusão"),
            (r"resumo", "resumo"),
            (r"considerações finais", "conclusão")
        ]
        
        for pattern, section_type in section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                sections.append({
                    "type": section_type,
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(0)
                })
        
        # Ordenar por posição
        sections.sort(key=lambda x: x["start"])
        
        return sections
    
    def _analyze_gap_distribution(self, gaps: List[DetectedGap], sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa a distribuição das lacunas por seção."""
        distribution = {
            "introdução": [],
            "desenvolvimento": [],
            "conclusão": [],
            "outros": []
        }
        
        for gap in gaps:
            gap_section = "outros"
            
            for section in sections:
                if section["start"] <= gap.start_pos <= section["end"]:
                    gap_section = section["type"]
                    break
            
            distribution[gap_section].append(gap)
        
        return distribution
    
    def _check_flow_coherence(self, gap_distribution: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica a coerência do fluxo."""
        coherence_issues = []
        
        # Verificar se há lacunas de contexto no início
        if not gap_distribution["introdução"]:
            coherence_issues.append("Falta contexto no início")
        
        # Verificar se há lacunas de desenvolvimento no meio
        if not gap_distribution["desenvolvimento"]:
            coherence_issues.append("Falta desenvolvimento no meio")
        
        # Verificar se há lacunas de conclusão no fim
        if not gap_distribution["conclusão"]:
            coherence_issues.append("Falta conclusão no fim")
        
        return {
            "is_coherent": len(coherence_issues) == 0,
            "issues": coherence_issues
        }
    
    def _calculate_flow_score(self, gap_distribution: Dict[str, Any], flow_coherence: Dict[str, Any]) -> float:
        """Calcula score do fluxo."""
        base_score = 0.8
        
        # Penalizar por problemas de coerência
        penalty = len(flow_coherence["issues"]) * 0.1
        
        # Bonus por distribuição equilibrada
        if gap_distribution["introdução"] and gap_distribution["desenvolvimento"]:
            base_score += 0.1
        
        if gap_distribution["conclusão"]:
            base_score += 0.1
        
        return max(0.0, min(1.0, base_score - penalty))
    
    def _detect_text_tone(self, text: str) -> str:
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
    
    def _detect_text_complexity(self, text: str) -> str:
        """Detecta a complexidade do texto."""
        words = text.split()
        if not words:
            return "médio"
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        if avg_word_length > 8:
            return "alto"
        elif avg_word_length > 6:
            return "médio"
        else:
            return "baixo"
    
    def _update_metrics(self, success: bool, analysis_time: float, coherence_score: float):
        """Atualiza métricas de performance."""
        self.metrics["total_analyses"] += 1
        
        if success:
            self.metrics["successful_analyses"] += 1
            self.metrics["analysis_times"].append(analysis_time)
            self.metrics["avg_analysis_time"] = statistics.mean(self.metrics["analysis_times"])
            self.metrics["coherence_scores"].append(coherence_score)
        else:
            self.metrics["failed_analyses"] += 1


class ContextValidator:
    """Validador de contexto avançado."""
    
    def __init__(self):
        """Inicializa o validador de contexto."""
        self.context_analyzer = ContextAnalyzer()
        self.min_validation_score = 0.7
        self.severity_weights = {
            ValidationSeverity.CRITICAL: 1.0,
            ValidationSeverity.HIGH: 0.8,
            ValidationSeverity.MEDIUM: 0.6,
            ValidationSeverity.LOW: 0.4,
            ValidationSeverity.INFO: 0.2
        }
        
        # Cache de validações
        self.validation_cache = {}
        self.cache_ttl = 1800  # 30 minutos
        
        # Métricas de performance
        self.metrics = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "avg_validation_time": 0.0,
            "validation_times": deque(maxlen=1000),
            "validation_scores": deque(maxlen=1000),
            "issue_distribution": defaultdict(int)
        }
        
        logger.info("ContextValidator inicializado")
    
    def validate_context(self, text: str, gaps: List[DetectedGap]) -> ContextValidationResult:
        """
        Valida o contexto das lacunas detectadas.
        
        Args:
            text: Texto completo
            gaps: Lacunas detectadas
            
        Returns:
            Resultado da validação contextual
        """
        start_time = time.time()
        
        try:
            # Verificar cache
            cache_key = f"{hash(text)}:{len(gaps)}"
            if cache_key in self.validation_cache:
                return self.validation_cache[cache_key]
            
            # Analisar coerência contextual
            context_analysis = self.context_analyzer.analyze_context_coherence(text, gaps)
            
            # Detectar problemas de validação
            issues = self._detect_validation_issues(text, gaps, context_analysis)
            
            # Gerar sugestões
            suggestions = self._generate_validation_suggestions(issues, context_analysis)
            
            # Calcular scores
            overall_score = self._calculate_validation_score(issues, context_analysis)
            coherence_score = context_analysis["coherence_score"]
            flow_score = context_analysis["flow_analysis"]["flow_score"]
            consistency_score = self._calculate_consistency_score(issues)
            
            # Determinar se é válido
            is_valid = overall_score >= self.min_validation_score and len([i for i in issues if i.severity == ValidationSeverity.CRITICAL]) == 0
            
            # Gerar warnings
            warnings = self._generate_warnings(issues, context_analysis)
            
            result = ContextValidationResult(
                is_valid=is_valid,
                overall_score=overall_score,
                issues=issues,
                warnings=warnings,
                suggestions=suggestions,
                validation_time=time.time() - start_time,
                context_analysis=context_analysis,
                coherence_score=coherence_score,
                flow_score=flow_score,
                consistency_score=consistency_score,
                metadata={
                    "cache_key": cache_key,
                    "validation_timestamp": datetime.now().isoformat()
                }
            )
            
            # Armazenar no cache
            self.validation_cache[cache_key] = result
            
            # Atualizar métricas
            self._update_metrics(True, time.time() - start_time, overall_score, issues)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação contextual: {e}")
            
            result = ContextValidationResult(
                is_valid=False,
                overall_score=0.0,
                issues=[],
                warnings=[f"Erro na validação: {e}"],
                suggestions=[],
                validation_time=time.time() - start_time,
                context_analysis={},
                coherence_score=0.0,
                flow_score=0.0,
                consistency_score=0.0,
                metadata={"error": str(e)}
            )
            
            self._update_metrics(False, time.time() - start_time, 0.0, [])
            
            return result
    
    def _detect_validation_issues(self, text: str, gaps: List[DetectedGap], context_analysis: Dict[str, Any]) -> List[ContextValidationIssue]:
        """Detecta problemas de validação."""
        issues = []
        
        # Verificar inconsistências contextuais
        for inconsistency in context_analysis.get("inconsistencies", []):
            issue = ContextValidationIssue(
                validation_type=ContextValidationType.CONTEXTUAL_CONSISTENCY,
                severity=self._determine_severity(inconsistency["type"]),
                description=inconsistency["description"],
                position=inconsistency["position"],
                context=text[max(0, inconsistency["position"][0]-50):inconsistency["position"][1]+50],
                suggestion=self._generate_issue_suggestion(inconsistency),
                confidence=0.8
            )
            issues.append(issue)
        
        # Verificar problemas de fluxo
        flow_analysis = context_analysis.get("flow_analysis", {})
        flow_coherence = flow_analysis.get("flow_coherence", {})
        
        for flow_issue in flow_coherence.get("issues", []):
            issue = ContextValidationIssue(
                validation_type=ContextValidationType.LOGICAL_FLOW,
                severity=ValidationSeverity.MEDIUM,
                description=flow_issue,
                position=(0, len(text)),
                context=text[:200] + "..." if len(text) > 200 else text,
                suggestion="Reorganize o texto para incluir seções apropriadas",
                confidence=0.7
            )
            issues.append(issue)
        
        # Verificar problemas de coerência semântica
        coherence_score = context_analysis.get("coherence_score", 0.0)
        if coherence_score < 0.6:
            issue = ContextValidationIssue(
                validation_type=ContextValidationType.SEMANTIC_COHERENCE,
                severity=ValidationSeverity.HIGH,
                description=f"Baixa coerência semântica (score: {coherence_score:.2f})",
                position=(0, len(text)),
                context=text[:200] + "..." if len(text) > 200 else text,
                suggestion="Melhore a coerência entre as lacunas e o contexto",
                confidence=0.9
            )
            issues.append(issue)
        
        return issues
    
    def _determine_severity(self, issue_type: str) -> ValidationSeverity:
        """Determina a severidade baseada no tipo de problema."""
        severity_mapping = {
            "redundant_placeholders": ValidationSeverity.MEDIUM,
            "missing_topic_context": ValidationSeverity.HIGH,
            "missing_audience_context": ValidationSeverity.HIGH,
            "inconsistent_flow": ValidationSeverity.MEDIUM,
            "low_coherence": ValidationSeverity.HIGH
        }
        return severity_mapping.get(issue_type, ValidationSeverity.MEDIUM)
    
    def _generate_issue_suggestion(self, inconsistency: Dict[str, Any]) -> str:
        """Gera sugestão para um problema específico."""
        issue_type = inconsistency["type"]
        
        suggestions = {
            "redundant_placeholders": "Considere remover um dos placeholders redundantes",
            "missing_topic_context": "Defina o tópico principal antes de usar placeholders de keyword",
            "missing_audience_context": "Especifique a audiência alvo antes de usar placeholders de audience",
            "inconsistent_flow": "Reorganize o texto para melhorar o fluxo lógico",
            "low_coherence": "Melhore a coerência entre as lacunas e o contexto geral"
        }
        
        return suggestions.get(issue_type, "Revise o contexto e ajuste conforme necessário")
    
    def _generate_validation_suggestions(self, issues: List[ContextValidationIssue], context_analysis: Dict[str, Any]) -> List[str]:
        """Gera sugestões gerais de validação."""
        suggestions = []
        
        # Sugestões baseadas no score de coerência
        coherence_score = context_analysis.get("coherence_score", 0.0)
        if coherence_score < 0.7:
            suggestions.append("Melhore a coerência contextual entre as lacunas")
        
        # Sugestões baseadas no fluxo
        flow_score = context_analysis.get("flow_analysis", {}).get("flow_score", 0.0)
        if flow_score < 0.7:
            suggestions.append("Reorganize o texto para melhorar o fluxo lógico")
        
        # Sugestões baseadas no contexto geral
        general_context = context_analysis.get("general_context", {})
        if not general_context.get("topics"):
            suggestions.append("Defina claramente o tópico principal do texto")
        
        if not general_context.get("audiences"):
            suggestions.append("Especifique a audiência alvo do conteúdo")
        
        return suggestions
    
    def _calculate_validation_score(self, issues: List[ContextValidationIssue], context_analysis: Dict[str, Any]) -> float:
        """Calcula o score geral de validação."""
        base_score = 1.0
        
        # Penalizar por problemas
        for issue in issues:
            penalty = self.severity_weights[issue.severity] * 0.1
            base_score -= penalty
        
        # Bonus por boa coerência
        coherence_score = context_analysis.get("coherence_score", 0.0)
        if coherence_score > 0.8:
            base_score += 0.1
        
        # Bonus por bom fluxo
        flow_score = context_analysis.get("flow_analysis", {}).get("flow_score", 0.0)
        if flow_score > 0.8:
            base_score += 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _calculate_consistency_score(self, issues: List[ContextValidationIssue]) -> float:
        """Calcula o score de consistência."""
        consistency_issues = [i for i in issues if i.validation_type == ContextValidationType.CONTEXTUAL_CONSISTENCY]
        
        if not consistency_issues:
            return 1.0
        
        # Penalizar por problemas de consistência
        penalty = len(consistency_issues) * 0.2
        return max(0.0, 1.0 - penalty)
    
    def _generate_warnings(self, issues: List[ContextValidationIssue], context_analysis: Dict[str, Any]) -> List[str]:
        """Gera warnings baseados na análise."""
        warnings = []
        
        # Warnings baseados na severidade dos problemas
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            warnings.append(f"Encontrados {len(critical_issues)} problemas críticos que devem ser corrigidos")
        
        high_issues = [i for i in issues if i.severity == ValidationSeverity.HIGH]
        if high_issues:
            warnings.append(f"Encontrados {len(high_issues)} problemas de alta severidade")
        
        # Warnings baseados no contexto
        general_context = context_analysis.get("general_context", {})
        if not general_context.get("topics"):
            warnings.append("Tópico principal não definido claramente")
        
        if not general_context.get("audiences"):
            warnings.append("Audiência alvo não especificada")
        
        return warnings
    
    def _update_metrics(self, success: bool, validation_time: float, validation_score: float, issues: List[ContextValidationIssue]):
        """Atualiza métricas de performance."""
        self.metrics["total_validations"] += 1
        
        if success:
            self.metrics["successful_validations"] += 1
            self.metrics["validation_times"].append(validation_time)
            self.metrics["avg_validation_time"] = statistics.mean(self.metrics["validation_times"])
            self.metrics["validation_scores"].append(validation_score)
            
            # Distribuição de tipos de problema
            for issue in issues:
                self.metrics["issue_distribution"][issue.validation_type.value] += 1
        else:
            self.metrics["failed_validations"] += 1


# Funções de conveniência
def validate_context(text: str, gaps: List[DetectedGap]) -> ContextValidationResult:
    """Função de conveniência para validação contextual."""
    validator = ContextValidator()
    return validator.validate_context(text, gaps)


def get_context_validation_stats() -> Dict[str, Any]:
    """Obtém estatísticas de validação contextual."""
    validator = ContextValidator()
    return validator.metrics


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
    
    # Validar contexto
    result = validate_context(test_text, test_gaps)
    
    print(f"Validação bem-sucedida: {result.is_valid}")
    print(f"Score geral: {result.overall_score:.2f}")
    print(f"Score de coerência: {result.coherence_score:.2f}")
    print(f"Problemas encontrados: {len(result.issues)}")
    print(f"Tempo de validação: {result.validation_time:.3f}s") 