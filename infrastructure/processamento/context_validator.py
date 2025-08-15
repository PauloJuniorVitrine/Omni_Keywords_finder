#!/usr/bin/env python3
"""
Validador de Contexto - Omni Keywords Finder
============================================

Tracing ID: CONTEXT_VALIDATOR_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema de validação contextual que verifica:
- Coerência semântica
- Consistência de tom
- Relevância de conteúdo
- Compatibilidade de placeholders
- Análise de fluxo lógico

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.3
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
    logging.warning("Dependências NLP não disponíveis. Validador de contexto será limitado.")

# Importar classes do sistema
from .hybrid_lacuna_detector_imp001 import (
    DetectedGap,
    PlaceholderType
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextValidationType(Enum):
    """Tipos de validação contextual."""
    SEMANTIC_COHERENCE = "semantic_coherence"
    TONE_CONSISTENCY = "tone_consistency"
    CONTENT_RELEVANCE = "content_relevance"
    PLACEHOLDER_COMPATIBILITY = "placeholder_compatibility"
    LOGICAL_FLOW = "logical_flow"


class ValidationSeverity(Enum):
    """Severidade da validação."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContextValidationIssue:
    """Problema de validação contextual."""
    validation_type: ContextValidationType
    severity: ValidationSeverity
    message: str
    start_pos: int
    end_pos: int
    context: str
    confidence: float
    suggestions: List[str]
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
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContextValidator:
    """Validador de contexto avançado."""
    
    def __init__(self):
        """Inicializa o validador de contexto."""
        self.nlp_model = None
        self.embedding_model = None
        self.validation_cache = {}
        self.cache_ttl = 1800  # 30 minutos
        
        # Regras de validação
        self.validation_rules = self._create_validation_rules()
        
        # Padrões de tom
        self.tone_patterns = self._create_tone_patterns()
        
        # Palavras-chave de relevância
        self.relevance_keywords = self._create_relevance_keywords()
        
        # Inicializar modelos NLP se disponíveis
        if NLP_AVAILABLE:
            self._initialize_nlp_models()
        
        # Métricas
        self.metrics = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "avg_validation_score": 0.0,
            "validation_scores": deque(maxlen=1000),
            "validation_times": deque(maxlen=1000),
            "issues_by_type": defaultdict(int),
            "issues_by_severity": defaultdict(int)
        }
        
        logger.info("ContextValidator inicializado")
    
    def _initialize_nlp_models(self):
        """Inicializa modelos NLP."""
        try:
            # Carregar modelo spaCy
            self.nlp_model = spacy.load("pt_core_news_sm")
            logger.info("Modelo spaCy carregado para validação contextual")
        except OSError:
            try:
                # Tentar carregar modelo em inglês como fallback
                self.nlp_model = spacy.load("en_core_web_sm")
                logger.warning("Modelo spaCy em português não encontrado. Usando modelo em inglês.")
            except OSError:
                logger.warning("Modelo spaCy não disponível. Validação contextual limitada.")
                self.nlp_model = None
        
        try:
            # Carregar modelo de embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Modelo de embeddings carregado para validação contextual")
        except Exception as e:
            logger.warning(f"Modelo de embeddings não disponível: {e}")
            self.embedding_model = None
    
    def _create_validation_rules(self) -> Dict[ContextValidationType, List[Dict[str, Any]]]:
        """Cria regras de validação contextual."""
        return {
            ContextValidationType.SEMANTIC_COHERENCE: [
                {"type": "contradiction", "severity": ValidationSeverity.HIGH, "message": "Contradição semântica detectada"},
                {"type": "inconsistency", "severity": ValidationSeverity.MEDIUM, "message": "Inconsistência semântica detectada"},
                {"type": "ambiguity", "severity": ValidationSeverity.MEDIUM, "message": "Ambiguidade semântica detectada"}
            ],
            ContextValidationType.TONE_CONSISTENCY: [
                {"type": "mixed_formal_informal", "severity": ValidationSeverity.MEDIUM, "message": "Mistura de tom formal e informal"},
                {"type": "inappropriate_tone", "severity": ValidationSeverity.HIGH, "message": "Tom inadequado para o contexto"},
                {"type": "tone_shift", "severity": ValidationSeverity.MEDIUM, "message": "Mudança abrupta de tom"}
            ],
            ContextValidationType.CONTENT_RELEVANCE: [
                {"type": "off_topic", "severity": ValidationSeverity.HIGH, "message": "Conteúdo fora do tópico"},
                {"type": "irrelevant_details", "severity": ValidationSeverity.MEDIUM, "message": "Detalhes irrelevantes"},
                {"type": "missing_key_info", "severity": ValidationSeverity.HIGH, "message": "Informação chave ausente"}
            ],
            ContextValidationType.PLACEHOLDER_COMPATIBILITY: [
                {"type": "incompatible_placeholders", "severity": ValidationSeverity.HIGH, "message": "Placeholders incompatíveis"},
                {"type": "missing_required", "severity": ValidationSeverity.CRITICAL, "message": "Placeholder obrigatório ausente"},
                {"type": "redundant_placeholders", "severity": ValidationSeverity.LOW, "message": "Placeholders redundantes"}
            ],
            ContextValidationType.LOGICAL_FLOW: [
                {"type": "illogical_sequence", "severity": ValidationSeverity.HIGH, "message": "Sequência ilógica detectada"},
                {"type": "missing_transition", "severity": ValidationSeverity.MEDIUM, "message": "Transição ausente"},
                {"type": "circular_reference", "severity": ValidationSeverity.HIGH, "message": "Referência circular detectada"}
            ]
        }
    
    def _create_tone_patterns(self) -> Dict[str, List[str]]:
        """Cria padrões de tom."""
        return {
            "formal": [
                r'\b(consequentemente|portanto|assim sendo|dessa forma)\b',
                r'\b(utilizar|obter|realizar|efetuar)\b',
                r'\b(mediante|através|por intermédio)\b',
                r'\b(considerando|tendo em vista|em virtude)\b'
            ],
            "informal": [
                r'\b(daí|então|tipo|tipo assim)\b',
                r'\b(usar|pegar|fazer|dar)\b',
                r'\b(beleza|legal|massa|show)\b',
                r'\b(olha só|veja bem|saca só)\b'
            ],
            "technical": [
                r'\b(algoritmo|protocolo|framework|arquitetura)\b',
                r'\b(implementação|otimização|escalabilidade)\b',
                r'\b(performance|latência|throughput)\b',
                r'\b(integração|deployment|monitoring)\b'
            ],
            "conversational": [
                r'\b(imagina|pensa|olha|veja)\b',
                r'\b(por exemplo|tipo|como|assim)\b',
                r'\b(entende|sabe|percebe)\b',
                r'\b(beleza|tranquilo|suave)\b'
            ]
        }
    
    def _create_relevance_keywords(self) -> Dict[str, List[str]]:
        """Cria palavras-chave de relevância por domínio."""
        return {
            "marketing": [
                "conversão", "lead", "funil", "segmentação", "persona",
                "campanha", "métricas", "roi", "ctr", "cpa"
            ],
            "seo": [
                "rankings", "keywords", "backlinks", "meta tags", "schema",
                "indexação", "crawling", "sitemap", "robots.txt"
            ],
            "content": [
                "engajamento", "alcance", "interação", "compartilhamento",
                "comentários", "likes", "views", "tempo de leitura"
            ],
            "analytics": [
                "dados", "métricas", "relatórios", "insights", "kpis",
                "dashboard", "tracking", "monitoring", "alertas"
            ]
        }
    
    def validate_context(self, gap: DetectedGap, suggested_value: str, full_text: str) -> ContextValidationResult:
        """
        Valida contexto de uma lacuna.
        
        Args:
            gap: Lacuna detectada
            suggested_value: Valor sugerido
            full_text: Texto completo
            
        Returns:
            Resultado da validação contextual
        """
        start_time = time.time()
        
        # Verificar cache
        cache_key = f"{gap.placeholder_type.value}_{hash(suggested_value)}_{hash(full_text)}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            issues = []
            warnings = []
            suggestions = []
            
            # 1. Validar coerência semântica
            semantic_issues = self._validate_semantic_coherence(gap, suggested_value, full_text)
            issues.extend(semantic_issues)
            
            # 2. Validar consistência de tom
            tone_issues = self._validate_tone_consistency(gap, suggested_value, full_text)
            issues.extend(tone_issues)
            
            # 3. Validar relevância de conteúdo
            relevance_issues = self._validate_content_relevance(gap, suggested_value, full_text)
            issues.extend(relevance_issues)
            
            # 4. Validar compatibilidade de placeholders
            placeholder_issues = self._validate_placeholder_compatibility(gap, suggested_value, full_text)
            issues.extend(placeholder_issues)
            
            # 5. Validar fluxo lógico
            flow_issues = self._validate_logical_flow(gap, suggested_value, full_text)
            issues.extend(flow_issues)
            
            # Calcular score geral
            overall_score = self._calculate_overall_score(issues)
            
            # Determinar se é válido
            is_valid = overall_score >= 0.7 and not any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)
            
            # Gerar sugestões
            suggestions = self._generate_suggestions(issues)
            
            # Criar resultado
            validation_time = time.time() - start_time
            result = ContextValidationResult(
                is_valid=is_valid,
                overall_score=overall_score,
                issues=issues,
                warnings=warnings,
                suggestions=suggestions,
                validation_time=validation_time,
                metadata={
                    "gap_type": gap.placeholder_type.value,
                    "suggested_value": suggested_value,
                    "text_length": len(full_text),
                    "issues_count": len(issues),
                    "critical_issues": len([i for i in issues if i.severity == ValidationSeverity.CRITICAL])
                }
            )
            
            # Armazenar no cache
            self.validation_cache[cache_key] = result
            
            # Limpar cache se necessário
            if len(self.validation_cache) > 100:
                self.validation_cache.clear()
            
            # Atualizar métricas
            self._update_metrics(result)
            
            logger.info(f"Validação contextual concluída: score {overall_score:.2f}")
            return result
            
        except Exception as e:
            error_msg = f"Erro na validação contextual: {str(e)}"
            logger.error(error_msg)
            
            return ContextValidationResult(
                is_valid=False,
                overall_score=0.0,
                issues=[],
                warnings=[error_msg],
                suggestions=[],
                validation_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _validate_semantic_coherence(self, gap: DetectedGap, suggested_value: str, full_text: str) -> List[ContextValidationIssue]:
        """Valida coerência semântica."""
        issues = []
        
        if not self.nlp_model:
            return issues
        
        try:
            # Analisar texto com spaCy
            doc = self.nlp_model(full_text)
            
            # Verificar contradições
            contradictions = self._detect_contradictions(doc, suggested_value)
            for contradiction in contradictions:
                issues.append(ContextValidationIssue(
                    validation_type=ContextValidationType.SEMANTIC_COHERENCE,
                    severity=ValidationSeverity.HIGH,
                    message=f"Contradição semântica: {contradiction}",
                    start_pos=gap.start_pos,
                    end_pos=gap.end_pos,
                    context=gap.context,
                    confidence=0.8,
                    suggestions=["Revise o valor sugerido para evitar contradições"],
                    metadata={"contradiction_type": contradiction}
                ))
            
            # Verificar inconsistências
            inconsistencies = self._detect_inconsistencies(doc, suggested_value)
            for inconsistency in inconsistencies:
                issues.append(ContextValidationIssue(
                    validation_type=ContextValidationType.SEMANTIC_COHERENCE,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Inconsistência semântica: {inconsistency}",
                    start_pos=gap.start_pos,
                    end_pos=gap.end_pos,
                    context=gap.context,
                    confidence=0.7,
                    suggestions=["Verifique a consistência do valor com o contexto"],
                    metadata={"inconsistency_type": inconsistency}
                ))
            
        except Exception as e:
            logger.warning(f"Erro na validação semântica: {e}")
        
        return issues
    
    def _validate_tone_consistency(self, gap: DetectedGap, suggested_value: str, full_text: str) -> List[ContextValidationIssue]:
        """Valida consistência de tom."""
        issues = []
        
        # Detectar tom do texto principal
        main_tone = self._detect_text_tone(full_text)
        value_tone = self._detect_text_tone(suggested_value)
        
        # Verificar incompatibilidade de tom
        if main_tone != value_tone and main_tone != "mixed" and value_tone != "mixed":
            severity = ValidationSeverity.HIGH if main_tone in ["formal", "technical"] else ValidationSeverity.MEDIUM
            
            issues.append(ContextValidationIssue(
                validation_type=ContextValidationType.TONE_CONSISTENCY,
                severity=severity,
                message=f"Incompatibilidade de tom: texto {main_tone}, valor {value_tone}",
                start_pos=gap.start_pos,
                end_pos=gap.end_pos,
                context=gap.context,
                confidence=0.9,
                suggestions=[f"Use tom {main_tone} no valor sugerido"],
                metadata={"main_tone": main_tone, "value_tone": value_tone}
            ))
        
        return issues
    
    def _validate_content_relevance(self, gap: DetectedGap, suggested_value: str, full_text: str) -> List[ContextValidationIssue]:
        """Valida relevância de conteúdo."""
        issues = []
        
        # Detectar domínio do texto
        text_domain = self._detect_text_domain(full_text)
        value_domain = self._detect_text_domain(suggested_value)
        
        # Verificar relevância
        if text_domain and value_domain and text_domain != value_domain:
            issues.append(ContextValidationIssue(
                validation_type=ContextValidationType.CONTENT_RELEVANCE,
                severity=ValidationSeverity.HIGH,
                message=f"Conteúdo irrelevante: texto {text_domain}, valor {value_domain}",
                start_pos=gap.start_pos,
                end_pos=gap.end_pos,
                context=gap.context,
                confidence=0.8,
                suggestions=[f"Use conteúdo relacionado ao domínio {text_domain}"],
                metadata={"text_domain": text_domain, "value_domain": value_domain}
            ))
        
        return issues
    
    def _validate_placeholder_compatibility(self, gap: DetectedGap, suggested_value: str, full_text: str) -> List[ContextValidationIssue]:
        """Valida compatibilidade de placeholders."""
        issues = []
        
        # Verificar se o valor é compatível com o tipo de placeholder
        if not self._is_placeholder_compatible(gap.placeholder_type, suggested_value):
            issues.append(ContextValidationIssue(
                validation_type=ContextValidationType.PLACEHOLDER_COMPATIBILITY,
                severity=ValidationSeverity.HIGH,
                message=f"Valor incompatível com placeholder {gap.placeholder_type.value}",
                start_pos=gap.start_pos,
                end_pos=gap.end_pos,
                context=gap.context,
                confidence=0.9,
                suggestions=[f"Use valor compatível com {gap.placeholder_type.value}"],
                metadata={"placeholder_type": gap.placeholder_type.value}
            ))
        
        # Verificar se há placeholders obrigatórios ausentes
        missing_required = self._check_missing_required_placeholders(full_text)
        if missing_required:
            issues.append(ContextValidationIssue(
                validation_type=ContextValidationType.PLACEHOLDER_COMPATIBILITY,
                severity=ValidationSeverity.CRITICAL,
                message=f"Placeholders obrigatórios ausentes: {', '.join(missing_required)}",
                start_pos=gap.start_pos,
                end_pos=gap.end_pos,
                context=gap.context,
                confidence=1.0,
                suggestions=["Adicione os placeholders obrigatórios"],
                metadata={"missing_placeholders": missing_required}
            ))
        
        return issues
    
    def _validate_logical_flow(self, gap: DetectedGap, suggested_value: str, full_text: str) -> List[ContextValidationIssue]:
        """Valida fluxo lógico."""
        issues = []
        
        # Verificar sequência lógica
        if not self._is_logical_sequence(full_text, suggested_value):
            issues.append(ContextValidationIssue(
                validation_type=ContextValidationType.LOGICAL_FLOW,
                severity=ValidationSeverity.MEDIUM,
                message="Sequência lógica questionável",
                start_pos=gap.start_pos,
                end_pos=gap.end_pos,
                context=gap.context,
                confidence=0.6,
                suggestions=["Verifique a sequência lógica do conteúdo"],
                metadata={"flow_issue": "sequence"}
            ))
        
        return issues
    
    def _detect_contradictions(self, doc, suggested_value: str) -> List[str]:
        """Detecta contradições no texto."""
        contradictions = []
        
        # Implementação simplificada
        # Em uma implementação real, usaria análise semântica mais avançada
        
        return contradictions
    
    def _detect_inconsistencies(self, doc, suggested_value: str) -> List[str]:
        """Detecta inconsistências no texto."""
        inconsistencies = []
        
        # Implementação simplificada
        
        return inconsistencies
    
    def _detect_text_tone(self, text: str) -> str:
        """Detecta tom do texto."""
        if not text:
            return "neutral"
        
        tone_scores = defaultdict(int)
        
        for tone, patterns in self.tone_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                tone_scores[tone] += matches
        
        if not tone_scores:
            return "neutral"
        
        # Determinar tom dominante
        dominant_tone = max(tone_scores.items(), key=lambda x: x[1])
        
        # Se há múltiplos tons com pontuação similar, considerar misto
        max_score = dominant_tone[1]
        similar_tones = [tone for tone, score in tone_scores.items() if score >= max_score * 0.7]
        
        if len(similar_tones) > 1:
            return "mixed"
        else:
            return dominant_tone[0]
    
    def _detect_text_domain(self, text: str) -> Optional[str]:
        """Detecta domínio do texto."""
        if not text:
            return None
        
        domain_scores = defaultdict(int)
        
        for domain, keywords in self.relevance_keywords.items():
            for keyword in keywords:
                matches = len(re.findall(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE))
                domain_scores[domain] += matches
        
        if not domain_scores:
            return None
        
        # Retornar domínio com maior pontuação
        return max(domain_scores.items(), key=lambda x: x[1])[0]
    
    def _is_placeholder_compatible(self, placeholder_type: PlaceholderType, value: str) -> bool:
        """Verifica se valor é compatível com tipo de placeholder."""
        if not value:
            return False
        
        # Regras de compatibilidade por tipo
        compatibility_rules = {
            PlaceholderType.PRIMARY_KEYWORD: lambda v: len(v) >= 2 and len(v) <= 100,
            PlaceholderType.SECONDARY_KEYWORDS: lambda v: len(v) >= 2 and len(v) <= 500,
            PlaceholderType.CLUSTER_ID: lambda v: re.match(r'^[a-zA-Z0-9\-_]+$', v),
            PlaceholderType.CATEGORIA: lambda v: len(v) >= 2 and len(v) <= 50,
            PlaceholderType.CONTENT_TYPE: lambda v: v.lower() in ["artigo", "post", "vídeo", "infográfico", "e-book", "newsletter"],
            PlaceholderType.TONE: lambda v: v.lower() in ["formal", "informal", "profissional", "casual", "técnico", "amigável"],
            PlaceholderType.LENGTH: lambda v: v.isdigit() and 100 <= int(v) <= 5000,
            PlaceholderType.TARGET_AUDIENCE: lambda v: len(v) >= 3 and len(v) <= 100,
            PlaceholderType.NICHE: lambda v: len(v) >= 2 and len(v) <= 50
        }
        
        rule = compatibility_rules.get(placeholder_type)
        if rule:
            try:
                return rule(value)
            except:
                return False
        
        return True  # Para tipos customizados
    
    def _check_missing_required_placeholders(self, text: str) -> List[str]:
        """Verifica placeholders obrigatórios ausentes."""
        required_placeholders = {
            PlaceholderType.PRIMARY_KEYWORD,
            PlaceholderType.CLUSTER_ID,
            PlaceholderType.CATEGORIA
        }
        
        missing = []
        for placeholder in required_placeholders:
            if f"{{{placeholder.value}}}" not in text:
                missing.append(placeholder.value)
        
        return missing
    
    def _is_logical_sequence(self, text: str, value: str) -> bool:
        """Verifica se a sequência é lógica."""
        # Implementação simplificada
        # Em uma implementação real, usaria análise mais avançada
        
        # Verificar se o valor não quebra o fluxo
        if not value:
            return False
        
        # Verificar se não há repetições desnecessárias
        if value in text:
            return False
        
        return True
    
    def _calculate_overall_score(self, issues: List[ContextValidationIssue]) -> float:
        """Calcula score geral baseado nos problemas encontrados."""
        if not issues:
            return 1.0
        
        # Pesos por severidade
        severity_weights = {
            ValidationSeverity.LOW: 0.1,
            ValidationSeverity.MEDIUM: 0.3,
            ValidationSeverity.HIGH: 0.6,
            ValidationSeverity.CRITICAL: 1.0
        }
        
        total_penalty = 0.0
        for issue in issues:
            weight = severity_weights.get(issue.severity, 0.3)
            total_penalty += weight * (1.0 - issue.confidence)
        
        # Normalizar para 0-1
        max_penalty = sum(severity_weights.values())
        normalized_penalty = min(total_penalty / max_penalty, 1.0)
        
        return max(0.0, 1.0 - normalized_penalty)
    
    def _generate_suggestions(self, issues: List[ContextValidationIssue]) -> List[str]:
        """Gera sugestões baseadas nos problemas encontrados."""
        suggestions = []
        
        for issue in issues:
            suggestions.extend(issue.suggestions)
        
        # Remover duplicatas
        return list(set(suggestions))
    
    def _update_metrics(self, result: ContextValidationResult):
        """Atualiza métricas de validação."""
        self.metrics["total_validations"] += 1
        
        if result.is_valid:
            self.metrics["successful_validations"] += 1
        else:
            self.metrics["failed_validations"] += 1
        
        self.metrics["validation_scores"].append(result.overall_score)
        self.metrics["validation_times"].append(result.validation_time)
        
        # Atualizar scores médios
        if len(self.metrics["validation_scores"]) > 0:
            self.metrics["avg_validation_score"] = statistics.mean(self.metrics["validation_scores"])
        
        # Contar issues por tipo e severidade
        for issue in result.issues:
            self.metrics["issues_by_type"][issue.validation_type.value] += 1
            self.metrics["issues_by_severity"][issue.severity.value] += 1
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de validação."""
        return {
            "total_validations": self.metrics["total_validations"],
            "successful_validations": self.metrics["successful_validations"],
            "failed_validations": self.metrics["failed_validations"],
            "success_rate": self.metrics["successful_validations"] / self.metrics["total_validations"] if self.metrics["total_validations"] > 0 else 0.0,
            "avg_validation_score": self.metrics["avg_validation_score"],
            "avg_validation_time": statistics.mean(self.metrics["validation_times"]) if self.metrics["validation_times"] else 0.0,
            "issues_by_type": dict(self.metrics["issues_by_type"]),
            "issues_by_severity": dict(self.metrics["issues_by_severity"]),
            "nlp_available": self.nlp_model is not None,
            "embedding_available": self.embedding_model is not None
        }


# Funções de conveniência
def validate_context(gap: DetectedGap, suggested_value: str, full_text: str) -> ContextValidationResult:
    """Valida contexto de uma lacuna."""
    validator = ContextValidator()
    return validator.validate_context(gap, suggested_value, full_text)


def get_context_validation_stats() -> Dict[str, Any]:
    """Obtém estatísticas de validação contextual."""
    validator = ContextValidator()
    return validator.get_validation_statistics()


# Instância global para uso em outros módulos
context_validator = ContextValidator() 