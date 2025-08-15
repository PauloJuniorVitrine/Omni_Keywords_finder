#!/usr/bin/env python3
"""
Detector Híbrido de Lacunas - Versão Aprimorada
===============================================

Tracing ID: HYBRID_LACUNA_DETECTOR_IMP001_20250127_001
Data: 2025-01-27
Versão: 2.0.0

Sistema híbrido aprimorado que combina:
- Detecção por regex (alta velocidade)
- Validação básica (alta precisão)
- Sistema de fallback inteligente
- Métricas de performance avançadas
- Padrão único de placeholders
- Auditoria completa

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.1
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

# Importar sistema de unificação aprimorado
from .placeholder_unification_system_imp001 import (
    PlaceholderUnificationSystem, 
    PlaceholderType,
    ValidationResult
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DetectionMethod(Enum):
    """Métodos de detecção."""
    REGEX = "regex"
    VALIDATION = "validation"
    HYBRID = "hybrid"
    FALLBACK = "fallback"


class ValidationLevel(Enum):
    """Níveis de validação."""
    BASIC = "basic"
    SEMANTIC = "semantic"
    ADVANCED = "advanced"


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
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DetectionResult:
    """Resultado da detecção."""
    gaps: List[DetectedGap]
    total_gaps: int
    confidence_avg: float
    detection_time: float
    method_used: DetectionMethod
    validation_level: ValidationLevel
    success: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RegexLacunaDetector:
    """Detector de lacunas baseado em regex - Versão Aprimorada."""
    
    def __init__(self):
        """Inicializa o detector regex aprimorado."""
        self.placeholder_patterns = self._create_patterns()
        self.compiled_patterns = self._compile_patterns()
        self.context_window_size = 150  # Tamanho da janela de contexto
        
        # Métricas de performance
        self.metrics = {
            "total_detections": 0,
            "successful_detections": 0,
            "failed_detections": 0,
            "avg_detection_time": 0.0,
            "detection_times": deque(maxlen=1000),
            "pattern_usage": defaultdict(int)
        }
        
        logger.info("RegexLacunaDetector aprimorado inicializado")
    
    def _create_patterns(self) -> Dict[PlaceholderType, str]:
        """Cria padrões regex otimizados para cada tipo de placeholder."""
        return {
            PlaceholderType.PRIMARY_KEYWORD: r'\{primary_keyword\}',
            PlaceholderType.SECONDARY_KEYWORDS: r'\{secondary_keywords\}',
            PlaceholderType.CLUSTER_CONTENT: r'\{cluster_content\}',
            PlaceholderType.CLUSTER_ID: r'\{cluster_id\}',
            PlaceholderType.CLUSTER_NAME: r'\{cluster_name\}',
            PlaceholderType.CATEGORIA: r'\{categoria\}',
            PlaceholderType.FASE_FUNIL: r'\{fase_funil\}',
            PlaceholderType.DATA: r'\{data\}',
            PlaceholderType.USUARIO: r'\{usuario\}',
            PlaceholderType.NICHE: r'\{niche\}',
            PlaceholderType.TARGET_AUDIENCE: r'\{target_audience\}',
            PlaceholderType.CONTENT_TYPE: r'\{content_type\}',
            PlaceholderType.TONE: r'\{tone\}',
            PlaceholderType.LENGTH: r'\{length\}',
            PlaceholderType.CUSTOM: r'\{([^}]+)\}'
        }
    
    def _compile_patterns(self) -> Dict[PlaceholderType, re.Pattern]:
        """Compila padrões regex com flags otimizadas."""
        return {
            placeholder_type: re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for placeholder_type, pattern in self.placeholder_patterns.items()
        }
    
    def detect_gaps(self, text: str) -> List[DetectedGap]:
        """
        Detecta lacunas usando regex otimizado.
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de lacunas detectadas
        """
        start_time = time.time()
        
        try:
            detected_gaps = []
            
            for placeholder_type, pattern in self.compiled_patterns.items():
                matches = pattern.finditer(text)
                
                for match in matches:
                    # Extrair nome do placeholder
                    if placeholder_type == PlaceholderType.CUSTOM:
                        placeholder_name = match.group(1)
                    else:
                        placeholder_name = placeholder_type.value
                    
                    # Extrair contexto otimizado
                    context = self._extract_context_optimized(text, match.start(), match.end())
                    
                    # Calcular confiança baseada no contexto
                    confidence = self._calculate_regex_confidence_advanced(context, placeholder_type, match)
                    
                    gap = DetectedGap(
                        placeholder_type=placeholder_type,
                        placeholder_name=placeholder_name,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=context,
                        confidence=confidence,
                        detection_method=DetectionMethod.REGEX,
                        validation_level=ValidationLevel.BASIC,
                        metadata={
                            "pattern_used": self.placeholder_patterns[placeholder_type],
                            "match_length": match.end() - match.start(),
                            "match_text": match.group(0),
                            "line_number": self._get_line_number(text, match.start()),
                            "column_number": self._get_column_number(text, match.start())
                        }
                    )
                    
                    detected_gaps.append(gap)
                    self.metrics["pattern_usage"][placeholder_type.value] += 1
            
            # Atualizar métricas
            detection_time = time.time() - start_time
            self._update_metrics(len(detected_gaps), detection_time)
            
            return detected_gaps
            
        except Exception as e:
            error_msg = f"Erro na detecção regex: {str(e)}"
            logger.error(error_msg)
            self.metrics["failed_detections"] += 1
            return []
    
    def _extract_context_optimized(self, text: str, start: int, end: int) -> str:
        """Extrai contexto otimizado ao redor da lacuna."""
        context_start = max(0, start - self.context_window_size)
        context_end = min(len(text), end + self.context_window_size)
        
        context = text[context_start:context_end].strip()
        
        # Limpar contexto para melhor legibilidade
        context = re.sub(r'\s+', ' ', context)  # Normalizar espaços
        context = context[:200] + "..." if len(context) > 200 else context  # Truncar se muito longo
        
        return context
    
    def _calculate_regex_confidence_advanced(self, context: str, placeholder_type: PlaceholderType, match: re.Match) -> float:
        """Calcula confiança avançada baseada no contexto."""
        base_confidence = 0.95  # Alta confiança para regex
        
        # Ajustar confiança baseado no tipo
        if placeholder_type in [PlaceholderType.PRIMARY_KEYWORD, PlaceholderType.CLUSTER_ID]:
            base_confidence = 0.98
        elif placeholder_type == PlaceholderType.CUSTOM:
            base_confidence = 0.90
        elif placeholder_type in [PlaceholderType.CONTENT_TYPE, PlaceholderType.TONE]:
            base_confidence = 0.92
        
        # Ajustar baseado no contexto
        if len(context) < 10:
            base_confidence *= 0.9  # Contexto muito pequeno
        elif len(context) > 100:
            base_confidence *= 1.05  # Contexto rico
        
        # Ajustar baseado na posição no texto
        if match.start() < 50:
            base_confidence *= 0.95  # No início do texto
        elif match.start() > len(context) - 50:
            base_confidence *= 0.95  # No final do texto
        
        # Verificar se há outros placeholders próximos
        nearby_placeholders = self._count_nearby_placeholders(context)
        if nearby_placeholders > 1:
            base_confidence *= 1.02  # Contexto rico em placeholders
        
        return min(base_confidence, 1.0)
    
    def _count_nearby_placeholders(self, context: str) -> int:
        """Conta placeholders próximos no contexto."""
        placeholder_pattern = r'\{[^}]+\}'
        return len(re.findall(placeholder_pattern, context))
    
    def _get_line_number(self, text: str, position: int) -> int:
        """Obtém número da linha para uma posição."""
        return text[:position].count('\n') + 1
    
    def _get_column_number(self, text: str, position: int) -> int:
        """Obtém número da coluna para uma posição."""
        last_newline = text.rfind('\n', 0, position)
        return position - last_newline if last_newline != -1 else position + 1
    
    def _update_metrics(self, gaps_count: int, detection_time: float):
        """Atualiza métricas de performance."""
        self.metrics["total_detections"] += 1
        
        if gaps_count > 0:
            self.metrics["successful_detections"] += 1
        else:
            self.metrics["failed_detections"] += 1
        
        self.metrics["detection_times"].append(detection_time)
        
        if len(self.metrics["detection_times"]) > 0:
            self.metrics["avg_detection_time"] = statistics.mean(self.metrics["detection_times"])


class BasicValidator:
    """Validador básico de lacunas - Versão Aprimorada."""
    
    def __init__(self):
        """Inicializa o validador básico aprimorado."""
        self.validation_rules = self._create_validation_rules()
        self.required_fields = {
            PlaceholderType.PRIMARY_KEYWORD,
            PlaceholderType.CLUSTER_ID,
            PlaceholderType.CATEGORIA
        }
        
        # Métricas de validação
        self.metrics = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "avg_validation_score": 0.0,
            "validation_scores": deque(maxlen=1000),
            "errors_by_type": defaultdict(int)
        }
        
        logger.info("BasicValidator aprimorado inicializado")
    
    def _create_validation_rules(self) -> Dict[PlaceholderType, List[Dict[str, Any]]]:
        """Cria regras de validação avançadas para cada tipo."""
        return {
            PlaceholderType.PRIMARY_KEYWORD: [
                {"type": "required", "message": "Palavra-chave principal é obrigatória"},
                {"type": "length", "min": 2, "max": 100, "message": "Palavra-chave deve ter entre 2 e 100 caracteres"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\s\-_]+$', "message": "Palavra-chave deve conter apenas letras, números, espaços, hífens e underscores"},
                {"type": "no_special_chars", "message": "Evite caracteres especiais na palavra-chave principal"}
            ],
            PlaceholderType.SECONDARY_KEYWORDS: [
                {"type": "length", "min": 2, "max": 500, "message": "Palavras-chave secundárias devem ter entre 2 e 500 caracteres"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\s\-_,]+$', "message": "Palavras-chave devem conter apenas letras, números, espaços, hífens, underscores e vírgulas"},
                {"type": "comma_separated", "message": "Palavras-chave devem ser separadas por vírgulas"}
            ],
            PlaceholderType.CLUSTER_ID: [
                {"type": "required", "message": "ID do cluster é obrigatório"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\-_]+$', "message": "ID do cluster deve conter apenas letras, números, hífens e underscores"},
                {"type": "length", "min": 3, "max": 50, "message": "ID do cluster deve ter entre 3 e 50 caracteres"}
            ],
            PlaceholderType.CATEGORIA: [
                {"type": "required", "message": "Categoria é obrigatória"},
                {"type": "length", "min": 2, "max": 50, "message": "Categoria deve ter entre 2 e 50 caracteres"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\s\-_]+$', "message": "Categoria deve conter apenas letras, números, espaços, hífens e underscores"}
            ],
            PlaceholderType.CONTENT_TYPE: [
                {"type": "enum", "values": ["artigo", "post", "vídeo", "infográfico", "e-book", "newsletter", "case", "tutorial"], "message": "Tipo de conteúdo deve ser um dos valores válidos"}
            ],
            PlaceholderType.TONE: [
                {"type": "enum", "values": ["formal", "informal", "profissional", "casual", "técnico", "amigável", "autoridade", "conversacional"], "message": "Tom deve ser um dos valores válidos"}
            ],
            PlaceholderType.LENGTH: [
                {"type": "format", "pattern": r'^\d+$', "message": "Comprimento deve ser um número"},
                {"type": "range", "min": 100, "max": 5000, "message": "Comprimento deve estar entre 100 e 5000"},
                {"type": "reasonable", "message": "Comprimento deve ser razoável para o tipo de conteúdo"}
            ],
            PlaceholderType.TARGET_AUDIENCE: [
                {"type": "length", "min": 3, "max": 100, "message": "Público-alvo deve ter entre 3 e 100 caracteres"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\s\-_,]+$', "message": "Público-alvo deve conter apenas letras, números, espaços, hífens, underscores e vírgulas"}
            ],
            PlaceholderType.NICHE: [
                {"type": "length", "min": 2, "max": 50, "message": "Nicho deve ter entre 2 e 50 caracteres"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\s\-_]+$', "message": "Nicho deve conter apenas letras, números, espaços, hífens e underscores"}
            ]
        }
    
    def validate_gap(self, gap: DetectedGap, suggested_value: str) -> Dict[str, Any]:
        """
        Valida uma lacuna com valor sugerido.
        
        Args:
            gap: Lacuna detectada
            suggested_value: Valor sugerido
            
        Returns:
            Resultado da validação
        """
        start_time = time.time()
        
        try:
            validation_result = {
                "is_valid": True,
                "confidence": 1.0,
                "issues": [],
                "suggestions": [],
                "validation_score": 1.0,
                "warnings": [],
                "metadata": {
                    "validation_time": 0.0,
                    "rules_applied": 0,
                    "field_type": gap.placeholder_type.value
                }
            }
            
            # Obter regras para o tipo de placeholder
            rules = self.validation_rules.get(gap.placeholder_type, [])
            validation_result["metadata"]["rules_applied"] = len(rules)
            
            for rule in rules:
                rule_type = rule["type"]
                
                if rule_type == "required":
                    if not suggested_value or not suggested_value.strip():
                        validation_result["is_valid"] = False
                        validation_result["issues"].append(rule["message"])
                        validation_result["confidence"] *= 0.8
                
                elif rule_type == "length":
                    min_len = rule.get("min", 0)
                    max_len = rule.get("max", float('inf'))
                    
                    if len(suggested_value) < min_len or len(suggested_value) > max_len:
                        validation_result["is_valid"] = False
                        validation_result["issues"].append(rule["message"])
                        validation_result["confidence"] *= 0.9
                
                elif rule_type == "format":
                    pattern = rule["pattern"]
                    if not re.match(pattern, suggested_value):
                        validation_result["is_valid"] = False
                        validation_result["issues"].append(rule["message"])
                        validation_result["confidence"] *= 0.7
                
                elif rule_type == "enum":
                    valid_values = rule["values"]
                    if suggested_value.lower() not in [v.lower() for v in valid_values]:
                        validation_result["is_valid"] = False
                        validation_result["issues"].append(rule["message"])
                        validation_result["suggestions"].append(f"Valores válidos: {', '.join(valid_values)}")
                        validation_result["confidence"] *= 0.6
                
                elif rule_type == "range":
                    try:
                        value = int(suggested_value)
                        min_val = rule.get("min", 0)
                        max_val = rule.get("max", float('inf'))
                        
                        if value < min_val or value > max_val:
                            validation_result["is_valid"] = False
                            validation_result["issues"].append(rule["message"])
                            validation_result["confidence"] *= 0.8
                    except ValueError:
                        validation_result["is_valid"] = False
                        validation_result["issues"].append("Valor deve ser numérico")
                        validation_result["confidence"] *= 0.5
                
                elif rule_type == "comma_separated":
                    if "," not in suggested_value and len(suggested_value.split()) > 1:
                        validation_result["warnings"].append(rule["message"])
                        validation_result["confidence"] *= 0.95
                
                elif rule_type == "no_special_chars":
                    if re.search(r'[^\w\s\-_]', suggested_value):
                        validation_result["warnings"].append(rule["message"])
                        validation_result["confidence"] *= 0.9
                
                elif rule_type == "reasonable":
                    try:
                        value = int(suggested_value)
                        if value < 50 or value > 10000:
                            validation_result["warnings"].append(rule["message"])
                            validation_result["confidence"] *= 0.95
                    except ValueError:
                        pass
            
            # Calcular score final
            validation_result["validation_score"] = validation_result["confidence"]
            validation_result["metadata"]["validation_time"] = time.time() - start_time
            
            # Atualizar métricas
            self._update_metrics(validation_result)
            
            return validation_result
            
        except Exception as e:
            error_msg = f"Erro na validação: {str(e)}"
            logger.error(error_msg)
            
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": [error_msg],
                "suggestions": [],
                "validation_score": 0.0,
                "warnings": [],
                "metadata": {
                    "validation_time": time.time() - start_time,
                    "error": str(e)
                }
            }
    
    def _update_metrics(self, validation_result: Dict[str, Any]):
        """Atualiza métricas de validação."""
        self.metrics["total_validations"] += 1
        
        if validation_result["is_valid"]:
            self.metrics["successful_validations"] += 1
        else:
            self.metrics["failed_validations"] += 1
        
        score = validation_result["validation_score"]
        self.metrics["validation_scores"].append(score)
        
        if len(self.metrics["validation_scores"]) > 0:
            self.metrics["avg_validation_score"] = statistics.mean(self.metrics["validation_scores"])
        
        # Contar erros por tipo
        for issue in validation_result["issues"]:
            error_type = "general"
            if "obrigatória" in issue.lower() or "obrigatório" in issue.lower():
                error_type = "required"
            elif "comprimento" in issue.lower() or "length" in issue.lower():
                error_type = "length"
            elif "formato" in issue.lower() or "format" in issue.lower():
                error_type = "format"
            elif "enum" in issue.lower() or "valores válidos" in issue.lower():
                error_type = "enum"
            
            self.metrics["errors_by_type"][error_type] += 1


class FallbackSystem:
    """Sistema de fallback inteligente - Versão Aprimorada."""
    
    def __init__(self):
        """Inicializa o sistema de fallback aprimorado."""
        self.fallback_values = self._create_fallback_values()
        self.context_patterns = self._create_context_patterns()
        
        # Cache de fallbacks
        self.fallback_cache = {}
        self.cache_ttl = 1800  # 30 minutos
        
        # Métricas
        self.metrics = {
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info("FallbackSystem aprimorado inicializado")
    
    def _create_fallback_values(self) -> Dict[PlaceholderType, List[str]]:
        """Cria valores de fallback inteligentes."""
        return {
            PlaceholderType.PRIMARY_KEYWORD: [
                "marketing digital",
                "SEO",
                "content marketing",
                "social media",
                "email marketing",
                "analytics",
                "automation"
            ],
            PlaceholderType.SECONDARY_KEYWORDS: [
                "estratégia, otimização, conversão",
                "tráfego, leads, vendas",
                "engajamento, alcance, interação",
                "segmentação, personalização, automação"
            ],
            PlaceholderType.CLUSTER_ID: [
                "cluster_001",
                "cluster_marketing",
                "cluster_seo",
                "cluster_content",
                "cluster_social"
            ],
            PlaceholderType.CATEGORIA: [
                "Marketing",
                "SEO",
                "Conteúdo",
                "Social Media",
                "Analytics",
                "Automação"
            ],
            PlaceholderType.CONTENT_TYPE: [
                "artigo",
                "post",
                "vídeo",
                "infográfico",
                "e-book",
                "newsletter"
            ],
            PlaceholderType.TONE: [
                "profissional",
                "amigável",
                "técnico",
                "casual",
                "formal",
                "conversacional"
            ],
            PlaceholderType.LENGTH: [
                "800",
                "1200",
                "1500",
                "2000",
                "2500"
            ],
            PlaceholderType.TARGET_AUDIENCE: [
                "profissionais de marketing",
                "empreendedores",
                "agências",
                "startups",
                "empresas estabelecidas"
            ],
            PlaceholderType.NICHE: [
                "SaaS",
                "E-commerce",
                "Educação",
                "Saúde",
                "Finanças",
                "Tecnologia"
            ]
        }
    
    def _create_context_patterns(self) -> Dict[str, List[str]]:
        """Cria padrões de contexto para fallback inteligente."""
        return {
            "marketing": ["marketing", "promoção", "vendas", "conversão"],
            "seo": ["seo", "otimização", "google", "rankings"],
            "content": ["conteúdo", "artigo", "blog", "escrita"],
            "social": ["social", "redes", "facebook", "instagram"],
            "analytics": ["analytics", "dados", "métricas", "relatórios"],
            "automation": ["automação", "workflow", "processo", "eficiente"]
        }
    
    def get_fallback_value(self, gap: DetectedGap, context: str) -> str:
        """
        Obtém valor de fallback inteligente baseado no contexto.
        
        Args:
            gap: Lacuna detectada
            context: Contexto da lacuna
            
        Returns:
            Valor de fallback
        """
        # Verificar cache
        cache_key = f"{gap.placeholder_type.value}_{hashlib.md5(context.encode()).hexdigest()[:8]}"
        
        if cache_key in self.fallback_cache:
            self.metrics["cache_hits"] += 1
            return self.fallback_cache[cache_key]
        
        self.metrics["cache_misses"] += 1
        
        try:
            # Obter valores de fallback para o tipo
            fallback_options = self.fallback_values.get(gap.placeholder_type, [])
            
            if not fallback_options:
                # Fallback genérico
                if gap.placeholder_type == PlaceholderType.CUSTOM:
                    return "valor_padrão"
                else:
                    return gap.placeholder_name
            
            # Selecionar melhor valor baseado no contexto
            best_value = self._select_best_fallback_value(fallback_options, context, gap.placeholder_type)
            
            # Armazenar no cache
            self.fallback_cache[cache_key] = best_value
            
            # Limpar cache se necessário
            if len(self.fallback_cache) > 1000:
                self.fallback_cache.clear()
            
            self.metrics["successful_fallbacks"] += 1
            return best_value
            
        except Exception as e:
            error_msg = f"Erro no fallback: {str(e)}"
            logger.error(error_msg)
            self.metrics["failed_fallbacks"] += 1
            
            # Fallback de emergência
            return "valor_padrão"
    
    def _select_best_fallback_value(self, options: List[str], context: str, placeholder_type: PlaceholderType) -> str:
        """Seleciona o melhor valor de fallback baseado no contexto."""
        if not options:
            return "valor_padrão"
        
        # Se há apenas uma opção, retornar
        if len(options) == 1:
            return options[0]
        
        # Analisar contexto para encontrar melhor match
        context_lower = context.lower()
        
        # Para tipos específicos, usar lógica especializada
        if placeholder_type == PlaceholderType.PRIMARY_KEYWORD:
            return self._select_keyword_fallback(options, context_lower)
        elif placeholder_type == PlaceholderType.CONTENT_TYPE:
            return self._select_content_type_fallback(options, context_lower)
        elif placeholder_type == PlaceholderType.TONE:
            return self._select_tone_fallback(options, context_lower)
        else:
            # Lógica genérica baseada em palavras-chave no contexto
            return self._select_generic_fallback(options, context_lower)
    
    def _select_keyword_fallback(self, options: List[str], context: str) -> str:
        """Seleciona palavra-chave baseada no contexto."""
        # Verificar padrões de contexto
        for pattern_key, keywords in self.context_patterns.items():
            if any(keyword in context for keyword in keywords):
                # Encontrar opção que melhor se alinha com o padrão
                for option in options:
                    if pattern_key in option.lower() or any(keyword in option.lower() for keyword in keywords):
                        return option
        
        # Retornar primeira opção se não encontrar match
        return options[0]
    
    def _select_content_type_fallback(self, options: List[str], context: str) -> str:
        """Seleciona tipo de conteúdo baseado no contexto."""
        if "artigo" in context or "blog" in context or "texto" in context:
            return "artigo"
        elif "vídeo" in context or "visual" in context:
            return "vídeo"
        elif "infográfico" in context or "imagem" in context:
            return "infográfico"
        elif "e-book" in context or "guia" in context:
            return "e-book"
        elif "newsletter" in context or "email" in context:
            return "newsletter"
        else:
            return "artigo"  # Padrão
    
    def _select_tone_fallback(self, options: List[str], context: str) -> str:
        """Seleciona tom baseado no contexto."""
        if "formal" in context or "profissional" in context or "empresarial" in context:
            return "profissional"
        elif "casual" in context or "descontraído" in context:
            return "casual"
        elif "técnico" in context or "especializado" in context:
            return "técnico"
        elif "amigável" in context or "acessível" in context:
            return "amigável"
        else:
            return "profissional"  # Padrão
    
    def _select_generic_fallback(self, options: List[str], context: str) -> str:
        """Seleciona fallback genérico."""
        # Tentar encontrar match baseado em palavras no contexto
        for option in options:
            if option.lower() in context:
                return option
        
        # Retornar primeira opção
        return options[0]


class HybridLacunaDetector:
    """
    Detector híbrido de lacunas - Versão Aprimorada.
    
    Combina detecção por regex com validação básica para máxima precisão.
    """
    
    def __init__(self):
        """Inicializa o detector híbrido aprimorado."""
        self.regex_detector = RegexLacunaDetector()
        self.validator = BasicValidator()
        self.fallback_system = FallbackSystem()
        self.unification_system = PlaceholderUnificationSystem()
        
        # Métricas avançadas
        self.metrics = {
            "total_detections": 0,
            "successful_detections": 0,
            "failed_detections": 0,
            "avg_confidence": 0.0,
            "detection_times": deque(maxlen=1000),
            "method_usage": defaultdict(int),
            "validation_scores": deque(maxlen=1000),
            "fallback_usage": defaultdict(int)
        }
        
        logger.info("HybridLacunaDetector aprimorado inicializado")
    
    def detect_gaps(self, text: str, enable_validation: bool = True) -> DetectionResult:
        """
        Detecta lacunas usando método híbrido aprimorado.
        
        Args:
            text: Texto para análise
            enable_validation: Habilitar validação básica
            
        Returns:
            Resultado da detecção
        """
        start_time = time.time()
        
        try:
            # 1. Unificar placeholders primeiro
            migration_result = self.unification_system.migrate_to_standard_format(text)
            if not migration_result.success:
                return DetectionResult(
                    gaps=[],
                    total_gaps=0,
                    confidence_avg=0.0,
                    detection_time=time.time() - start_time,
                    method_used=DetectionMethod.FALLBACK,
                    validation_level=ValidationLevel.BASIC,
                    success=False,
                    errors=migration_result.errors,
                    warnings=migration_result.warnings,
                    metadata={
                        "migration_failed": True,
                        "migration_errors": migration_result.errors
                    }
                )
            
            unified_text = migration_result.migrated_text
            
            # 2. Detecção por regex
            regex_gaps = self.regex_detector.detect_gaps(unified_text)
            self.metrics["method_usage"]["regex"] += 1
            
            # 3. Validação básica (se habilitada)
            validated_gaps = []
            if enable_validation:
                for gap in regex_gaps:
                    # Obter valor de fallback
                    fallback_value = self.fallback_system.get_fallback_value(gap, gap.context)
                    self.metrics["fallback_usage"][gap.placeholder_type.value] += 1
                    
                    # Validar valor
                    validation_result = self.validator.validate_gap(gap, fallback_value)
                    
                    # Atualizar gap com informações de validação
                    gap.suggested_value = fallback_value
                    gap.validation_score = validation_result["validation_score"]
                    gap.confidence = min(gap.confidence, validation_result["confidence"])
                    gap.metadata["validation_result"] = validation_result
                    
                    # Ajustar método de detecção
                    if validation_result["is_valid"]:
                        gap.detection_method = DetectionMethod.HYBRID
                        gap.validation_level = ValidationLevel.BASIC
                    else:
                        gap.detection_method = DetectionMethod.FALLBACK
                        gap.validation_level = ValidationLevel.BASIC
                    
                    validated_gaps.append(gap)
                    self.metrics["validation_scores"].append(validation_result["validation_score"])
            else:
                validated_gaps = regex_gaps
            
            # 4. Calcular métricas
            detection_time = time.time() - start_time
            confidence_avg = statistics.mean([g.confidence for g in validated_gaps]) if validated_gaps else 0.0
            
            # 5. Atualizar métricas globais
            self._update_metrics(len(validated_gaps), detection_time, confidence_avg)
            
            # 6. Criar resultado
            result = DetectionResult(
                gaps=validated_gaps,
                total_gaps=len(validated_gaps),
                confidence_avg=confidence_avg,
                detection_time=detection_time,
                method_used=DetectionMethod.HYBRID if enable_validation else DetectionMethod.REGEX,
                validation_level=ValidationLevel.BASIC if enable_validation else ValidationLevel.BASIC,
                success=True,
                errors=[],
                warnings=migration_result.warnings,
                metadata={
                    "migration_applied": len(migration_result.migrations_applied) > 0,
                    "migration_details": migration_result.migrations_applied,
                    "unified_text": unified_text,
                    "validation_enabled": enable_validation,
                    "avg_validation_score": statistics.mean(self.metrics["validation_scores"]) if self.metrics["validation_scores"] else 0.0
                }
            )
            
            logger.info(f"Detecção híbrida aprimorada concluída: {len(validated_gaps)} lacunas detectadas")
            return result
            
        except Exception as e:
            error_msg = f"Erro na detecção híbrida aprimorada: {str(e)}"
            logger.error(error_msg)
            
            return DetectionResult(
                gaps=[],
                total_gaps=0,
                confidence_avg=0.0,
                detection_time=time.time() - start_time,
                method_used=DetectionMethod.FALLBACK,
                validation_level=ValidationLevel.BASIC,
                success=False,
                errors=[error_msg],
                warnings=[],
                metadata={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
    
    def _update_metrics(self, gaps_count: int, detection_time: float, confidence_avg: float):
        """Atualiza métricas avançadas."""
        self.metrics["total_detections"] += 1
        
        if gaps_count > 0:
            self.metrics["successful_detections"] += 1
        else:
            self.metrics["failed_detections"] += 1
        
        self.metrics["detection_times"].append(detection_time)
        self.metrics["avg_confidence"] = confidence_avg
        
        # Calcular tempo médio
        if len(self.metrics["detection_times"]) > 0:
            avg_time = statistics.mean(self.metrics["detection_times"])
            self.metrics["avg_detection_time"] = avg_time
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de detecção."""
        return {
            "total_detections": self.metrics["total_detections"],
            "successful_detections": self.metrics["successful_detections"],
            "failed_detections": self.metrics["failed_detections"],
            "success_rate": self.metrics["successful_detections"] / self.metrics["total_detections"] if self.metrics["total_detections"] > 0 else 0.0,
            "avg_confidence": self.metrics["avg_confidence"],
            "avg_detection_time": statistics.mean(self.metrics["detection_times"]) if self.metrics["detection_times"] else 0.0,
            "method_usage": dict(self.metrics["method_usage"]),
            "fallback_usage": dict(self.metrics["fallback_usage"]),
            "avg_validation_score": statistics.mean(self.metrics["validation_scores"]) if self.metrics["validation_scores"] else 0.0
        }


# Funções de conveniência
def detect_gaps_hybrid(text: str, enable_validation: bool = True) -> DetectionResult:
    """Detecta lacunas usando método híbrido."""
    detector = HybridLacunaDetector()
    return detector.detect_gaps(text, enable_validation)


def get_detection_stats() -> Dict[str, Any]:
    """Obtém estatísticas de detecção."""
    detector = HybridLacunaDetector()
    return detector.get_detection_statistics()


# Instância global para uso em outros módulos
hybrid_detector = HybridLacunaDetector() 