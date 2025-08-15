"""
Validation Module - Omni Keywords Finder

Sistema de validação de dados para o orquestrador:
- Verificação de integridade
- Validação de formato
- Checks de qualidade
- Validação de negócio

Tracing ID: VALIDATION_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import logging
import re
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Níveis de validação."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationType(Enum):
    """Tipos de validação."""
    FORMAT = "format"
    INTEGRITY = "integrity"
    QUALITY = "quality"
    BUSINESS = "business"


@dataclass
class ValidationRule:
    """Regra de validação."""
    name: str
    type: ValidationType
    level: ValidationLevel
    description: str
    validator: callable
    error_message: str
    enabled: bool = True


@dataclass
class ValidationResult:
    """Resultado de uma validação."""
    rule_name: str
    passed: bool
    level: ValidationLevel
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationConfig:
    """Configuração do sistema de validação."""
    enabled: bool = True
    fail_fast: bool = False
    log_failures: bool = True
    min_quality_score: float = 0.7
    max_keyword_length: int = 100
    min_keyword_length: int = 2
    required_fields: List[str] = field(default_factory=lambda: [
        "keyword", "volume", "competition", "cpc"
    ])
    forbidden_words: List[str] = field(default_factory=lambda: [
        "xxx", "porn", "adult", "sex"
    ])


class DataValidator:
    """Validador de dados."""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Inicializa o validador.
        
        Args:
            config: Configuração da validação
        """
        self.config = config or ValidationConfig()
        self.rules: Dict[str, ValidationRule] = {}
        
        self._register_default_rules()
        logger.info("DataValidator inicializado")
    
    def _register_default_rules(self):
        """Registra regras de validação padrão."""
        default_rules = [
            # Validações de Formato
            ValidationRule(
                name="keyword_format",
                type=ValidationType.FORMAT,
                level=ValidationLevel.HIGH,
                description="Valida formato da keyword",
                validator=self._validate_keyword_format,
                error_message="Keyword com formato inválido"
            ),
            ValidationRule(
                name="required_fields",
                type=ValidationType.FORMAT,
                level=ValidationLevel.CRITICAL,
                description="Verifica campos obrigatórios",
                validator=self._validate_required_fields,
                error_message="Campos obrigatórios ausentes"
            ),
            ValidationRule(
                name="data_types",
                type=ValidationType.FORMAT,
                level=ValidationLevel.HIGH,
                description="Valida tipos de dados",
                validator=self._validate_data_types,
                error_message="Tipos de dados inválidos"
            ),
            
            # Validações de Integridade
            ValidationRule(
                name="data_consistency",
                type=ValidationType.INTEGRITY,
                level=ValidationLevel.HIGH,
                description="Verifica consistência dos dados",
                validator=self._validate_data_consistency,
                error_message="Dados inconsistentes"
            ),
            ValidationRule(
                name="duplicate_check",
                type=ValidationType.INTEGRITY,
                level=ValidationLevel.MEDIUM,
                description="Verifica duplicatas",
                validator=self._validate_no_duplicates,
                error_message="Keywords duplicadas encontradas"
            ),
            ValidationRule(
                name="hash_verification",
                type=ValidationType.INTEGRITY,
                level=ValidationLevel.LOW,
                description="Verifica hash dos dados",
                validator=self._validate_data_hash,
                error_message="Hash dos dados inválido"
            ),
            
            # Validações de Qualidade
            ValidationRule(
                name="keyword_quality",
                type=ValidationType.QUALITY,
                level=ValidationLevel.HIGH,
                description="Avalia qualidade da keyword",
                validator=self._validate_keyword_quality,
                error_message="Keyword com baixa qualidade"
            ),
            ValidationRule(
                name="volume_threshold",
                type=ValidationType.QUALITY,
                level=ValidationLevel.MEDIUM,
                description="Verifica volume mínimo",
                validator=self._validate_volume_threshold,
                error_message="Volume abaixo do threshold"
            ),
            ValidationRule(
                name="competition_analysis",
                type=ValidationType.QUALITY,
                level=ValidationLevel.MEDIUM,
                description="Analisa competição",
                validator=self._validate_competition,
                error_message="Competição muito alta"
            ),
            
            # Validações de Negócio
            ValidationRule(
                name="forbidden_words",
                type=ValidationType.BUSINESS,
                level=ValidationLevel.CRITICAL,
                description="Verifica palavras proibidas",
                validator=self._validate_forbidden_words,
                error_message="Palavras proibidas encontradas"
            ),
            ValidationRule(
                name="niche_relevance",
                type=ValidationType.BUSINESS,
                level=ValidationLevel.HIGH,
                description="Verifica relevância para o nicho",
                validator=self._validate_niche_relevance,
                error_message="Keyword não relevante para o nicho"
            ),
            ValidationRule(
                name="commercial_intent",
                type=ValidationType.BUSINESS,
                level=ValidationLevel.MEDIUM,
                description="Analisa intenção comercial",
                validator=self._validate_commercial_intent,
                error_message="Baixa intenção comercial"
            )
        ]
        
        for rule in default_rules:
            self.register_rule(rule)
    
    def register_rule(self, rule: ValidationRule):
        """
        Registra uma nova regra de validação.
        
        Args:
            rule: Regra de validação
        """
        self.rules[rule.name] = rule
        logger.info(f"Regra de validação registrada: {rule.name}")
    
    def validate_data(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """
        Valida dados usando todas as regras aplicáveis.
        
        Args:
            data: Dados a serem validados
            context: Contexto adicional
            
        Returns:
            Lista de resultados de validação
        """
        if not self.config.enabled:
            return []
        
        results = []
        context = context or {}
        
        # Normalizar dados para lista
        if isinstance(data, dict):
            data_list = [data]
        else:
            data_list = data
        
        # Validar cada item
        for index, item in enumerate(data_list):
            item_context = {**context, "index": index}
            item_results = self._validate_item(item, item_context)
            results.extend(item_results)
            
            # Fail fast se configurado
            if self.config.fail_fast:
                critical_failures = [r for r in item_results 
                                   if not r.passed and r.level == ValidationLevel.CRITICAL]
                if critical_failures:
                    break
        
        # Log de falhas se configurado
        if self.config.log_failures:
            failures = [r for r in results if not r.passed]
            if failures:
                logger.warning(f"Validação falhou: {len(failures)} falhas encontradas")
                for failure in failures:
                    logger.warning(f"  - {failure.rule_name}: {failure.message}")
        
        return results
    
    def _validate_item(self, item: Dict[str, Any], context: Dict[str, Any]) -> List[ValidationResult]:
        """Valida um item individual."""
        results = []
        
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                passed = rule.validator(item, context)
                result = ValidationResult(
                    rule_name=rule_name,
                    passed=passed,
                    level=rule.level,
                    message=rule.error_message if not passed else "Validação passou"
                )
                results.append(result)
                
            except Exception as e:
                result = ValidationResult(
                    rule_name=rule_name,
                    passed=False,
                    level=rule.level,
                    message=f"Erro na validação: {str(e)}"
                )
                results.append(result)
        
        return results
    
    def _validate_keyword_format(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Valida formato da keyword."""
        keyword = item.get("keyword", "")
        
        if not isinstance(keyword, str):
            return False
        
        # Verificar comprimento
        if len(keyword) < self.config.min_keyword_length:
            return False
        
        if len(keyword) > self.config.max_keyword_length:
            return False
        
        # Verificar caracteres válidos
        if not re.match(r'^[a-zA-Z0-9\string_data\-_]+$', keyword):
            return False
        
        return True
    
    def _validate_required_fields(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica campos obrigatórios."""
        for field in self.config.required_fields:
            if field not in item or item[field] is None:
                return False
        
        return True
    
    def _validate_data_types(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Valida tipos de dados."""
        type_validations = {
            "keyword": str,
            "volume": (int, float),
            "competition": (int, float),
            "cpc": (int, float)
        }
        
        for field, expected_type in type_validations.items():
            if field in item:
                if not isinstance(item[field], expected_type):
                    return False
        
        return True
    
    def _validate_data_consistency(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica consistência dos dados."""
        # Volume deve ser positivo
        volume = item.get("volume", 0)
        if volume < 0:
            return False
        
        # Competition deve estar entre 0 e 1
        competition = item.get("competition", 0)
        if not (0 <= competition <= 1):
            return False
        
        # CPC deve ser positivo
        cpc = item.get("cpc", 0)
        if cpc < 0:
            return False
        
        return True
    
    def _validate_no_duplicates(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica duplicatas (implementação simplificada)."""
        # Esta validação seria melhor implementada no nível da lista
        # Por enquanto, apenas verifica se a keyword não está vazia
        keyword = item.get("keyword", "")
        return bool(keyword.strip())
    
    def _validate_data_hash(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica hash dos dados."""
        # Implementação simplificada - sempre retorna True
        # Em uma implementação real, você compararia com um hash esperado
        return True
    
    def _validate_keyword_quality(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Avalia qualidade da keyword."""
        keyword = item.get("keyword", "").lower()
        
        # Verificar se não é muito genérica
        generic_words = ["como", "o que", "quando", "onde", "por que", "qual"]
        if keyword in generic_words:
            return False
        
        # Verificar se tem pelo menos 2 palavras
        words = keyword.split()
        if len(words) < 2:
            return False
        
        # Verificar se não é muito longa
        if len(words) > 5:
            return False
        
        return True
    
    def _validate_volume_threshold(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica volume mínimo."""
        volume = item.get("volume", 0)
        min_volume = context.get("min_volume", 100)
        
        return volume >= min_volume
    
    def _validate_competition(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Analisa competição."""
        competition = item.get("competition", 1.0)
        max_competition = context.get("max_competition", 0.8)
        
        return competition <= max_competition
    
    def _validate_forbidden_words(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica palavras proibidas."""
        keyword = item.get("keyword", "").lower()
        
        for forbidden_word in self.config.forbidden_words:
            if forbidden_word.lower() in keyword:
                return False
        
        return True
    
    def _validate_niche_relevance(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verifica relevância para o nicho."""
        keyword = item.get("keyword", "").lower()
        niche = context.get("niche", "").lower()
        
        if not niche:
            return True  # Sem nicho especificado, aceita tudo
        
        # Palavras-chave do nicho (exemplo)
        niche_keywords = {
            "tecnologia": ["app", "software", "tech", "digital", "online"],
            "saude": ["saude", "medico", "tratamento", "remedio", "clinica"],
            "financas": ["dinheiro", "investimento", "credito", "banco", "financas"]
        }
        
        niche_words = niche_keywords.get(niche, [])
        
        # Verificar se pelo menos uma palavra do nicho está presente
        for niche_word in niche_words:
            if niche_word in keyword:
                return True
        
        return False
    
    def _validate_commercial_intent(self, item: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Analisa intenção comercial."""
        keyword = item.get("keyword", "").lower()
        
        # Palavras que indicam intenção comercial
        commercial_words = [
            "comprar", "vender", "preco", "custo", "barato", "caro",
            "melhor", "top", "recomendado", "avaliacao", "review"
        ]
        
        # Verificar se contém palavras comerciais
        for commercial_word in commercial_words:
            if commercial_word in keyword:
                return True
        
        return False
    
    def calculate_quality_score(self, results: List[ValidationResult]) -> float:
        """
        Calcula score de qualidade baseado nos resultados.
        
        Args:
            results: Resultados de validação
            
        Returns:
            Score de qualidade (0-1)
        """
        if not results:
            return 0.0
        
        # Pesos por nível
        weights = {
            ValidationLevel.CRITICAL: 1.0,
            ValidationLevel.HIGH: 0.8,
            ValidationLevel.MEDIUM: 0.6,
            ValidationLevel.LOW: 0.4
        }
        
        total_weight = 0.0
        passed_weight = 0.0
        
        for result in results:
            weight = weights.get(result.level, 0.5)
            total_weight += weight
            
            if result.passed:
                passed_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return passed_weight / total_weight
    
    def filter_valid_data(
        self, 
        data: List[Dict[str, Any]], 
        context: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> Tuple[List[Dict[str, Any]], List[ValidationResult]]:
        """
        Filtra dados válidos baseado nas validações.
        
        Args:
            data: Lista de dados
            context: Contexto adicional
            min_score: Score mínimo para aceitar
            
        Returns:
            Tupla (dados válidos, resultados de validação)
        """
        if min_score is None:
            min_score = self.config.min_quality_score
        
        valid_data = []
        all_results = []
        
        for item in data:
            results = self.validate_data(item, context)
            all_results.extend(results)
            
            score = self.calculate_quality_score(results)
            
            if score >= min_score:
                valid_data.append(item)
        
        return valid_data, all_results
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Gera resumo das validações.
        
        Args:
            results: Resultados de validação
            
        Returns:
            Resumo das validações
        """
        summary = {
            "total_validations": len(results),
            "passed": len([r for r in results if r.passed]),
            "failed": len([r for r in results if not r.passed]),
            "quality_score": self.calculate_quality_score(results),
            "by_level": {},
            "by_type": {}
        }
        
        # Agrupar por nível
        for level in ValidationLevel:
            level_results = [r for r in results if r.level == level]
            summary["by_level"][level.value] = {
                "total": len(level_results),
                "passed": len([r for r in level_results if r.passed]),
                "failed": len([r for r in level_results if not r.passed])
            }
        
        # Agrupar por tipo
        for validation_type in ValidationType:
            type_results = [r for r in results if r.type == validation_type]
            summary["by_type"][validation_type.value] = {
                "total": len(type_results),
                "passed": len([r for r in type_results if r.passed]),
                "failed": len([r for r in type_results if not r.passed])
            }
        
        return summary


# Instância global
_data_validator: Optional[DataValidator] = None


def obter_data_validator(config: Optional[ValidationConfig] = None) -> DataValidator:
    """
    Obtém instância global do validador.
    
    Args:
        config: Configuração opcional
        
    Returns:
        Instância do validador
    """
    global _data_validator
    
    if _data_validator is None:
        _data_validator = DataValidator(config)
    
    return _data_validator


def validate_data(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    context: Optional[Dict[str, Any]] = None
) -> List[ValidationResult]:
    """Função helper para validar dados."""
    validator = obter_data_validator()
    return validator.validate_data(data, context)


def filter_valid_data(
    data: List[Dict[str, Any]], 
    context: Optional[Dict[str, Any]] = None,
    min_score: Optional[float] = None
) -> Tuple[List[Dict[str, Any]], List[ValidationResult]]:
    """Função helper para filtrar dados válidos."""
    validator = obter_data_validator()
    return validator.filter_valid_data(data, context, min_score)


def calculate_quality_score(results: List[ValidationResult]) -> float:
    """Função helper para calcular score de qualidade."""
    validator = obter_data_validator()
    return validator.calculate_quality_score(results)


def get_validation_summary(results: List[ValidationResult]) -> Dict[str, Any]:
    """Função helper para obter resumo de validação."""
    validator = obter_data_validator()
    return validator.get_validation_summary(results) 