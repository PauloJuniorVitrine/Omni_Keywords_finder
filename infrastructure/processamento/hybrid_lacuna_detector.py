#!/usr/bin/env python3
"""
Detector Híbrido de Lacunas - Omni Keywords Finder
==================================================

Tracing ID: HYBRID_LACUNA_DETECTOR_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema híbrido que combina:
- Detecção por regex (alta velocidade)
- Validação básica (alta precisão)
- Sistema de fallback inteligente
- Métricas de performance

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

# Importar sistema de unificação
from .placeholder_unification_system import PlaceholderUnificationSystem, PlaceholderType

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
    CONTEXTUAL = "contextual"
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
    """Detector de lacunas baseado em regex."""
    
    def __init__(self):
        """Inicializa o detector regex."""
        self.placeholder_patterns = self._create_patterns()
        self.compiled_patterns = self._compile_patterns()
        
        logger.info("RegexLacunaDetector inicializado")
    
    def _create_patterns(self) -> Dict[PlaceholderType, str]:
        """Cria padrões regex para cada tipo de placeholder."""
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
        """Compila padrões regex."""
        return {
            placeholder_type: re.compile(pattern, re.IGNORECASE)
            for placeholder_type, pattern in self.placeholder_patterns.items()
        }
    
    def detect_gaps(self, text: str) -> List[DetectedGap]:
        """
        Detecta lacunas usando regex.
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de lacunas detectadas
        """
        detected_gaps = []
        
        for placeholder_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                # Extrair nome do placeholder
                if placeholder_type == PlaceholderType.CUSTOM:
                    placeholder_name = match.group(1)
                else:
                    placeholder_name = placeholder_type.value
                
                # Extrair contexto
                context = self._extract_context(text, match.start(), match.end())
                
                # Calcular confiança baseada no contexto
                confidence = self._calculate_regex_confidence(context, placeholder_type)
                
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
                        "match_length": match.end() - match.start()
                    }
                )
                
                detected_gaps.append(gap)
        
        return detected_gaps
    
    def _extract_context(self, text: str, start: int, end: int, context_size: int = 100) -> str:
        """Extrai contexto ao redor da lacuna."""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        
        return text[context_start:context_end].strip()
    
    def _calculate_regex_confidence(self, context: str, placeholder_type: PlaceholderType) -> float:
        """Calcula confiança baseada no contexto."""
        base_confidence = 0.95  # Alta confiança para regex
        
        # Ajustar confiança baseado no tipo
        if placeholder_type in [PlaceholderType.PRIMARY_KEYWORD, PlaceholderType.CLUSTER_ID]:
            base_confidence = 0.98
        elif placeholder_type == PlaceholderType.CUSTOM:
            base_confidence = 0.90
        
        # Ajustar baseado no contexto
        if len(context) < 10:
            base_confidence *= 0.9  # Contexto muito pequeno
        
        return min(base_confidence, 1.0)


class BasicValidator:
    """Validador básico de lacunas."""
    
    def __init__(self):
        """Inicializa o validador básico."""
        self.validation_rules = self._create_validation_rules()
        
        logger.info("BasicValidator inicializado")
    
    def _create_validation_rules(self) -> Dict[PlaceholderType, List[Dict[str, Any]]]:
        """Cria regras de validação para cada tipo."""
        return {
            PlaceholderType.PRIMARY_KEYWORD: [
                {"type": "required", "message": "Palavra-chave principal é obrigatória"},
                {"type": "length", "min": 2, "max": 100, "message": "Palavra-chave deve ter entre 2 e 100 caracteres"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\s\-_]+$', "message": "Palavra-chave deve conter apenas letras, números, espaços, hífens e underscores"}
            ],
            PlaceholderType.SECONDARY_KEYWORDS: [
                {"type": "length", "min": 2, "max": 500, "message": "Palavras-chave secundárias devem ter entre 2 e 500 caracteres"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\s\-_,]+$', "message": "Palavras-chave devem conter apenas letras, números, espaços, hífens, underscores e vírgulas"}
            ],
            PlaceholderType.CLUSTER_ID: [
                {"type": "required", "message": "ID do cluster é obrigatório"},
                {"type": "format", "pattern": r'^[a-zA-Z0-9\-_]+$', "message": "ID do cluster deve conter apenas letras, números, hífens e underscores"}
            ],
            PlaceholderType.CATEGORIA: [
                {"type": "required", "message": "Categoria é obrigatória"},
                {"type": "length", "min": 2, "max": 50, "message": "Categoria deve ter entre 2 e 50 caracteres"}
            ],
            PlaceholderType.CONTENT_TYPE: [
                {"type": "enum", "values": ["artigo", "post", "vídeo", "infográfico", "e-book", "newsletter"], "message": "Tipo de conteúdo deve ser um dos valores válidos"}
            ],
            PlaceholderType.TONE: [
                {"type": "enum", "values": ["formal", "informal", "profissional", "casual", "técnico", "amigável"], "message": "Tom deve ser um dos valores válidos"}
            ],
            PlaceholderType.LENGTH: [
                {"type": "format", "pattern": r'^\d+$', "message": "Comprimento deve ser um número"},
                {"type": "range", "min": 100, "max": 5000, "message": "Comprimento deve estar entre 100 e 5000"}
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
        validation_result = {
            "is_valid": True,
            "confidence": 1.0,
            "issues": [],
            "suggestions": [],
            "validation_score": 1.0
        }
        
        # Obter regras para o tipo de placeholder
        rules = self.validation_rules.get(gap.placeholder_type, [])
        
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
                    min_val = rule.get("min", float('-inf'))
                    max_val = rule.get("max", float('inf'))
                    
                    if value < min_val or value > max_val:
                        validation_result["is_valid"] = False
                        validation_result["issues"].append(rule["message"])
                        validation_result["confidence"] *= 0.8
                except ValueError:
                    validation_result["is_valid"] = False
                    validation_result["issues"].append("Valor deve ser um número")
                    validation_result["confidence"] *= 0.5
        
        # Calcular score final
        validation_result["validation_score"] = validation_result["confidence"]
        
        return validation_result


class FallbackSystem:
    """Sistema de fallback inteligente."""
    
    def __init__(self):
        """Inicializa o sistema de fallback."""
        self.fallback_strategies = self._create_fallback_strategies()
        
        logger.info("FallbackSystem inicializado")
    
    def _create_fallback_strategies(self) -> Dict[PlaceholderType, callable]:
        """Cria estratégias de fallback para cada tipo."""
        return {
            PlaceholderType.PRIMARY_KEYWORD: self._fallback_primary_keyword,
            PlaceholderType.SECONDARY_KEYWORDS: self._fallback_secondary_keywords,
            PlaceholderType.CLUSTER_CONTENT: self._fallback_cluster_content,
            PlaceholderType.CLUSTER_ID: self._fallback_cluster_id,
            PlaceholderType.CATEGORIA: self._fallback_categoria,
            PlaceholderType.CONTENT_TYPE: self._fallback_content_type,
            PlaceholderType.TONE: self._fallback_tone,
            PlaceholderType.LENGTH: self._fallback_length,
            PlaceholderType.TARGET_AUDIENCE: self._fallback_target_audience,
            PlaceholderType.NICHE: self._fallback_niche
        }
    
    def get_fallback_value(self, gap: DetectedGap, context: str) -> str:
        """
        Obtém valor de fallback para a lacuna.
        
        Args:
            gap: Lacuna detectada
            context: Contexto da lacuna
            
        Returns:
            Valor de fallback
        """
        strategy = self.fallback_strategies.get(gap.placeholder_type)
        
        if strategy:
            return strategy(context)
        else:
            return self._fallback_generic(context)
    
    def _fallback_primary_keyword(self, context: str) -> str:
        """Fallback para palavra-chave principal."""
        # Extrair palavras-chave do contexto
        words = re.findall(r'\b\w{4,}\b', context.lower())
        if words:
            return words[0].title()
        return "palavra-chave"
    
    def _fallback_secondary_keywords(self, context: str) -> str:
        """Fallback para palavras-chave secundárias."""
        words = re.findall(r'\b\w{4,}\b', context.lower())
        if len(words) >= 2:
            return ", ".join(words[1:3])
        return "palavra-chave secundária"
    
    def _fallback_cluster_content(self, context: str) -> str:
        """Fallback para conteúdo do cluster."""
        return "conteúdo relacionado ao tópico"
    
    def _fallback_cluster_id(self, context: str) -> str:
        """Fallback para ID do cluster."""
        return "cluster_001"
    
    def _fallback_categoria(self, context: str) -> str:
        """Fallback para categoria."""
        return "geral"
    
    def _fallback_content_type(self, context: str) -> str:
        """Fallback para tipo de conteúdo."""
        return "artigo"
    
    def _fallback_tone(self, context: str) -> str:
        """Fallback para tom."""
        return "profissional"
    
    def _fallback_length(self, context: str) -> str:
        """Fallback para comprimento."""
        return "500"
    
    def _fallback_target_audience(self, context: str) -> str:
        """Fallback para público-alvo."""
        return "profissionais"
    
    def _fallback_niche(self, context: str) -> str:
        """Fallback para nicho."""
        return "tecnologia"
    
    def _fallback_generic(self, context: str) -> str:
        """Fallback genérico."""
        return "valor_padrão"


class HybridLacunaDetector:
    """
    Detector híbrido de lacunas.
    
    Combina detecção por regex com validação básica para máxima precisão.
    """
    
    def __init__(self):
        """Inicializa o detector híbrido."""
        self.regex_detector = RegexLacunaDetector()
        self.validator = BasicValidator()
        self.fallback_system = FallbackSystem()
        self.unification_system = PlaceholderUnificationSystem()
        
        # Métricas
        self.metrics = {
            "total_detections": 0,
            "successful_detections": 0,
            "failed_detections": 0,
            "avg_confidence": 0.0,
            "detection_times": deque(maxlen=1000),
            "method_usage": defaultdict(int)
        }
        
        logger.info("HybridLacunaDetector inicializado")
    
    def detect_gaps(self, text: str, enable_validation: bool = True) -> DetectionResult:
        """
        Detecta lacunas usando método híbrido.
        
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
                    warnings=migration_result.warnings
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
                    "unified_text": unified_text
                }
            )
            
            logger.info(f"Detecção híbrida concluída: {len(validated_gaps)} lacunas detectadas")
            return result
            
        except Exception as e:
            error_msg = f"Erro na detecção híbrida: {str(e)}"
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
                warnings=[]
            )
    
    def _update_metrics(self, gaps_count: int, detection_time: float, confidence_avg: float):
        """Atualiza métricas de performance."""
        self.metrics["total_detections"] += 1
        self.metrics["successful_detections"] += 1
        self.metrics["detection_times"].append(detection_time)
        
        # Atualizar média de confiança
        if self.metrics["detection_times"]:
            self.metrics["avg_confidence"] = (
                (self.metrics["avg_confidence"] * (self.metrics["total_detections"] - 1) + confidence_avg) /
                self.metrics["total_detections"]
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance."""
        return {
            "total_detections": self.metrics["total_detections"],
            "successful_detections": self.metrics["successful_detections"],
            "failed_detections": self.metrics["failed_detections"],
            "success_rate": (
                self.metrics["successful_detections"] / self.metrics["total_detections"]
                if self.metrics["total_detections"] > 0 else 0
            ),
            "avg_confidence": self.metrics["avg_confidence"],
            "avg_detection_time": (
                statistics.mean(self.metrics["detection_times"])
                if self.metrics["detection_times"] else 0
            ),
            "method_usage": dict(self.metrics["method_usage"])
        }


# Instância global
hybrid_detector = HybridLacunaDetector()


# Funções de conveniência
def detect_gaps_hybrid(text: str, enable_validation: bool = True) -> DetectionResult:
    """Detecta lacunas usando método híbrido."""
    return hybrid_detector.detect_gaps(text, enable_validation)


def get_hybrid_detector_metrics() -> Dict[str, Any]:
    """Retorna métricas do detector híbrido."""
    return hybrid_detector.get_performance_metrics()


if __name__ == "__main__":
    # Exemplo de uso
    test_texts = [
        "Crie um {content_type} sobre {primary_keyword} para {target_audience}",
        "Gere artigo sobre SEO para profissionais",
        "Faça {content_type} sobre {primary_keyword} com {length} palavras",
        "Produza conteúdo sobre {niche} usando tom {tone}"
    ]
    
    print("=== Teste do Detector Híbrido de Lacunas ===\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"Teste {i}:")
        print(f"Texto: {text}")
        
        # Detectar lacunas
        result = detect_gaps_hybrid(text, enable_validation=True)
        
        print(f"Lacunas detectadas: {result.total_gaps}")
        print(f"Confiança média: {result.confidence_avg:.2f}")
        print(f"Tempo de detecção: {result.detection_time:.4f}s")
        print(f"Método usado: {result.method_used.value}")
        
        for j, gap in enumerate(result.gaps, 1):
            print(f"  Lacuna {j}:")
            print(f"    Tipo: {gap.placeholder_type.value}")
            print(f"    Nome: {gap.placeholder_name}")
            print(f"    Confiança: {gap.confidence:.2f}")
            print(f"    Valor sugerido: {gap.suggested_value}")
            print(f"    Score de validação: {gap.validation_score:.2f}")
        
        print("-" * 50)
    
    # Métricas
    metrics = get_hybrid_detector_metrics()
    print("\n=== Métricas de Performance ===")
    print(json.dumps(metrics, indent=2, default=str)) 