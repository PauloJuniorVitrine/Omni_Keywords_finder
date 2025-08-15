#!/usr/bin/env python3
"""
Sistema Unificado de Placeholders - Versão Aprimorada
====================================================

Tracing ID: PLACEHOLDER_UNIFICATION_IMP001_20250127_001
Data: 2025-01-27
Versão: 2.0.0

Sistema aprimorado que unifica todos os padrões de placeholders em um formato padrão:
- Padrão único: {placeholder_name}
- Migração automática de formatos antigos
- Validação de consistência avançada
- Detecção de incompatibilidades
- Sistema de fallback inteligente
- Auditoria completa de mudanças

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.1
Ruleset: enterprise_control_layer.yaml
"""

import re
import json
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import sqlite3
from collections import defaultdict, deque
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaceholderFormat(Enum):
    """Formatos de placeholders suportados."""
    OLD_BRACKETS = "old_brackets"           # [PALAVRA-CHAVE], [CLUSTER]
    NEW_CURLY = "new_curly"                 # {primary_keyword}, {cluster_id}
    TEMPLATE_DOLLAR = "template_dollar"     # $primary_keyword, $cluster_id
    ANGULAR_BRACKETS = "angular_brackets"   # <primary_keyword>, <cluster_id>
    DOUBLE_BRACKETS = "double_brackets"     # [[primary_keyword]], [[cluster_id]]
    MIXED = "mixed"                         # Formato misto


class PlaceholderType(Enum):
    """Tipos de placeholders padronizados."""
    PRIMARY_KEYWORD = "primary_keyword"
    SECONDARY_KEYWORDS = "secondary_keywords"
    CLUSTER_CONTENT = "cluster_content"
    CLUSTER_ID = "cluster_id"
    CLUSTER_NAME = "cluster_name"
    CATEGORIA = "categoria"
    FASE_FUNIL = "fase_funil"
    DATA = "data"
    USUARIO = "usuario"
    NICHE = "niche"
    TARGET_AUDIENCE = "target_audience"
    CONTENT_TYPE = "content_type"
    TONE = "tone"
    LENGTH = "length"
    CUSTOM = "custom"


@dataclass
class PlaceholderMapping:
    """Mapeamento de placeholders antigos para novos."""
    old_format: str
    new_format: str
    field_name: str
    description: str
    required: bool = True
    default_value: Optional[str] = None
    validation_rules: List[str] = None
    migration_priority: int = 1
    deprecated: bool = False
    replacement: Optional[str] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []


@dataclass
class MigrationResult:
    """Resultado de uma migração de placeholder."""
    original_text: str
    migrated_text: str
    format_detected: PlaceholderFormat
    migrations_applied: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    success: bool
    timestamp: datetime
    hash_before: str
    hash_after: str
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}


@dataclass
class ValidationResult:
    """Resultado de validação de placeholders."""
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    consistency_score: float
    completeness_score: float
    placeholder_count: int
    required_missing: List[str]
    deprecated_used: List[str]


class PlaceholderUnificationSystem:
    """
    Sistema unificado de placeholders - Versão Aprimorada.
    
    Responsabilidades:
    - Padrão único: {placeholder_name}
    - Migração automática de formatos antigos
    - Validação de consistência avançada
    - Detecção de incompatibilidades
    - Sistema de fallback inteligente
    - Auditoria completa de mudanças
    - Performance monitoring
    """
    
    # Padrão único definido
    STANDARD_FORMAT = "curly_braces"  # {placeholder_name}
    
    def __init__(self):
        """Inicializa o sistema de unificação aprimorado."""
        self.placeholder_mappings = self._create_comprehensive_mappings()
        self.required_placeholders = {
            PlaceholderType.PRIMARY_KEYWORD,
            PlaceholderType.CLUSTER_ID,
            PlaceholderType.CATEGORIA
        }
        self.optional_placeholders = {
            PlaceholderType.SECONDARY_KEYWORDS,
            PlaceholderType.FASE_FUNIL,
            PlaceholderType.DATA,
            PlaceholderType.USUARIO,
            PlaceholderType.CLUSTER_NAME,
            PlaceholderType.NICHE,
            PlaceholderType.TARGET_AUDIENCE,
            PlaceholderType.CONTENT_TYPE,
            PlaceholderType.TONE,
            PlaceholderType.LENGTH
        }
        
        # Cache de migrações com TTL
        self.migration_cache = {}
        self.cache_ttl = 3600  # 1 hora
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Métricas de performance
        self.metrics = {
            "total_migrations": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "format_detections": defaultdict(int),
            "migration_times": deque(maxlen=1000),
            "cache_hit_rate": 0.0,
            "avg_migration_time": 0.0,
            "errors_by_type": defaultdict(int)
        }
        
        # Padrões de detecção otimizados
        self.format_patterns = self._create_format_patterns()
        
        logger.info("Sistema de unificação de placeholders aprimorado inicializado")
    
    def _create_comprehensive_mappings(self) -> List[PlaceholderMapping]:
        """Cria mapeamentos abrangentes de placeholders."""
        return [
            # Placeholders principais (alta prioridade)
            PlaceholderMapping(
                old_format="[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]",
                new_format="{primary_keyword}",
                field_name="primary_keyword",
                description="Palavra-chave principal do prompt",
                required=True,
                migration_priority=1
            ),
            PlaceholderMapping(
                old_format="[PALAVRA-CHAVE]",
                new_format="{primary_keyword}",
                field_name="primary_keyword",
                description="Palavra-chave principal (formato antigo)",
                required=True,
                migration_priority=1
            ),
            PlaceholderMapping(
                old_format="[CLUSTER]",
                new_format="{cluster_id}",
                field_name="cluster_id",
                description="ID do cluster relacionado",
                required=True,
                migration_priority=1
            ),
            PlaceholderMapping(
                old_format="[CATEGORIA]",
                new_format="{categoria}",
                field_name="categoria",
                description="Categoria do conteúdo",
                required=True,
                migration_priority=1
            ),
            
            # Placeholders secundários (média prioridade)
            PlaceholderMapping(
                old_format="[PALAVRAS-CHAVE SECUNDÁRIAS]",
                new_format="{secondary_keywords}",
                field_name="secondary_keywords",
                description="Lista de palavras-chave secundárias",
                required=False,
                migration_priority=2
            ),
            PlaceholderMapping(
                old_format="[PALAVRAS-SECUNDARIAS]",
                new_format="{secondary_keywords}",
                field_name="secondary_keywords",
                description="Palavras-chave secundárias (formato antigo)",
                required=False,
                migration_priority=2
            ),
            PlaceholderMapping(
                old_format="[CLUSTER DE CONTEÚDO]",
                new_format="{cluster_content}",
                field_name="cluster_content",
                description="Conteúdo do cluster",
                required=False,
                migration_priority=2
            ),
            PlaceholderMapping(
                old_format="[NOME DO CLUSTER]",
                new_format="{cluster_name}",
                field_name="cluster_name",
                description="Nome do cluster",
                required=False,
                migration_priority=2
            ),
            
            # Placeholders de contexto (baixa prioridade)
            PlaceholderMapping(
                old_format="[FASE DO FUNIL]",
                new_format="{fase_funil}",
                field_name="fase_funil",
                description="Fase do funil de vendas",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[DATA]",
                new_format="{data}",
                field_name="data",
                description="Data de criação",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[USUÁRIO]",
                new_format="{usuario}",
                field_name="usuario",
                description="Nome do usuário",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[NICHE]",
                new_format="{niche}",
                field_name="niche",
                description="Nicho de mercado",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[PÚBLICO-ALVO]",
                new_format="{target_audience}",
                field_name="target_audience",
                description="Público-alvo",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[TIPO DE CONTEÚDO]",
                new_format="{content_type}",
                field_name="content_type",
                description="Tipo de conteúdo",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[TOM]",
                new_format="{tone}",
                field_name="tone",
                description="Tom do conteúdo",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[COMPRIMENTO]",
                new_format="{length}",
                field_name="length",
                description="Comprimento do conteúdo",
                required=False,
                migration_priority=3
            ),
            
            # Mapeamentos para outros formatos
            PlaceholderMapping(
                old_format="$primary_keyword",
                new_format="{primary_keyword}",
                field_name="primary_keyword",
                description="Palavra-chave principal (formato $)",
                required=True,
                migration_priority=1
            ),
            PlaceholderMapping(
                old_format="$cluster_id",
                new_format="{cluster_id}",
                field_name="cluster_id",
                description="ID do cluster (formato $)",
                required=True,
                migration_priority=1
            ),
            PlaceholderMapping(
                old_format="<primary_keyword>",
                new_format="{primary_keyword}",
                field_name="primary_keyword",
                description="Palavra-chave principal (formato <>)",
                required=True,
                migration_priority=1
            ),
            PlaceholderMapping(
                old_format="[[primary_keyword]]",
                new_format="{primary_keyword}",
                field_name="primary_keyword",
                description="Palavra-chave principal (formato [[]])",
                required=True,
                migration_priority=1
            ),
            
            # Placeholders deprecated (para compatibilidade)
            PlaceholderMapping(
                old_format="[PALAVRA-CHAVE ANTIGA]",
                new_format="{primary_keyword}",
                field_name="primary_keyword",
                description="Palavra-chave antiga (deprecated)",
                required=False,
                migration_priority=4,
                deprecated=True,
                replacement="primary_keyword"
            )
        ]
    
    def _create_format_patterns(self) -> Dict[PlaceholderFormat, List[re.Pattern]]:
        """Cria padrões de detecção para cada formato."""
        return {
            PlaceholderFormat.OLD_BRACKETS: [
                re.compile(r'\[[A-Z\s\-_]+\]', re.IGNORECASE)
            ],
            PlaceholderFormat.NEW_CURLY: [
                re.compile(r'\{[a-z_][a-z0-9_]*\}', re.IGNORECASE)
            ],
            PlaceholderFormat.TEMPLATE_DOLLAR: [
                re.compile(r'\$[a-z_][a-z0-9_]*', re.IGNORECASE)
            ],
            PlaceholderFormat.ANGULAR_BRACKETS: [
                re.compile(r'<[a-z_][a-z0-9_]*>', re.IGNORECASE)
            ],
            PlaceholderFormat.DOUBLE_BRACKETS: [
                re.compile(r'\[\[[a-z_][a-z0-9_]*\]\]', re.IGNORECASE)
            ]
        }
    
    def detect_format(self, text: str) -> PlaceholderFormat:
        """
        Detecta o formato dos placeholders no texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Formato detectado
        """
        if not text:
            return PlaceholderFormat.NEW_CURLY
        
        format_counts = defaultdict(int)
        
        for format_type, patterns in self.format_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                format_counts[format_type] += len(matches)
        
        # Determinar formato dominante
        if not format_counts:
            return PlaceholderFormat.NEW_CURLY
        
        dominant_format = max(format_counts.items(), key=lambda x: x[1])[0]
        
        # Verificar se é formato misto
        active_formats = [f for f, count in format_counts.items() if count > 0]
        if len(active_formats) > 1:
            return PlaceholderFormat.MIXED
        
        self.metrics["format_detections"][dominant_format.value] += 1
        return dominant_format
    
    def migrate_to_standard_format(self, text: str, force_migration: bool = False) -> MigrationResult:
        """
        Migra texto para o formato padrão único.
        
        Args:
            text: Texto para migração
            force_migration: Forçar migração mesmo se já estiver no formato padrão
            
        Returns:
            Resultado da migração
        """
        start_time = time.time()
        
        # Verificar cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"{text_hash}_{force_migration}"
        
        if cache_key in self.migration_cache:
            self.cache_hits += 1
            cached_result = self.migration_cache[cache_key]
            cached_result.performance_metrics["cache_hit"] = True
            return cached_result
        
        self.cache_misses += 1
        
        try:
            # Detectar formato atual
            format_detected = self.detect_format(text)
            
            # Se já está no formato padrão e não for forçado, retornar sem mudanças
            if format_detected == PlaceholderFormat.NEW_CURLY and not force_migration:
                result = MigrationResult(
                    original_text=text,
                    migrated_text=text,
                    format_detected=format_detected,
                    migrations_applied=[],
                    errors=[],
                    warnings=["Texto já está no formato padrão"],
                    success=True,
                    timestamp=datetime.now(),
                    hash_before=text_hash,
                    hash_after=text_hash,
                    performance_metrics={
                        "migration_time": time.time() - start_time,
                        "cache_hit": False,
                        "format_already_standard": True
                    }
                )
                
                # Atualizar cache
                self.migration_cache[cache_key] = result
                self._update_metrics(result)
                return result
            
            # Aplicar migrações
            migrated_text = text
            migrations_applied = []
            errors = []
            warnings = []
            
            # Ordenar mapeamentos por prioridade
            sorted_mappings = sorted(self.placeholder_mappings, key=lambda x: x.migration_priority)
            
            for mapping in sorted_mappings:
                try:
                    # Escapar caracteres especiais no padrão antigo
                    escaped_old = re.escape(mapping.old_format)
                    pattern = re.compile(escaped_old, re.IGNORECASE)
                    
                    if pattern.search(migrated_text):
                        # Aplicar substituição
                        old_migrated_text = migrated_text
                        migrated_text = pattern.sub(mapping.new_format, migrated_text)
                        
                        if migrated_text != old_migrated_text:
                            migrations_applied.append({
                                "old_format": mapping.old_format,
                                "new_format": mapping.new_format,
                                "field_name": mapping.field_name,
                                "description": mapping.description,
                                "deprecated": mapping.deprecated,
                                "replacement": mapping.replacement
                            })
                            
                            if mapping.deprecated:
                                warnings.append(f"Placeholder deprecated usado: {mapping.old_format} -> {mapping.new_format}")
                
                except Exception as e:
                    error_msg = f"Erro ao migrar {mapping.old_format}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Validar resultado
            validation_result = self._validate_migrated_text(migrated_text)
            errors.extend(validation_result["errors"])
            warnings.extend(validation_result["warnings"])
            
            # Calcular hash do resultado
            hash_after = hashlib.md5(migrated_text.encode()).hexdigest()
            
            # Determinar sucesso
            success = len(errors) == 0 and len(migrations_applied) > 0
            
            # Criar resultado
            migration_time = time.time() - start_time
            result = MigrationResult(
                original_text=text,
                migrated_text=migrated_text,
                format_detected=format_detected,
                migrations_applied=migrations_applied,
                errors=errors,
                warnings=warnings,
                success=success,
                timestamp=datetime.now(),
                hash_before=text_hash,
                hash_after=hash_after,
                performance_metrics={
                    "migration_time": migration_time,
                    "cache_hit": False,
                    "migrations_count": len(migrations_applied),
                    "errors_count": len(errors),
                    "warnings_count": len(warnings)
                }
            )
            
            # Atualizar cache
            self.migration_cache[cache_key] = result
            
            # Atualizar métricas
            self._update_metrics(result)
            
            logger.info(f"Migração concluída: {len(migrations_applied)} placeholders migrados")
            return result
            
        except Exception as e:
            error_msg = f"Erro geral na migração: {str(e)}"
            logger.error(error_msg)
            
            result = MigrationResult(
                original_text=text,
                migrated_text=text,
                format_detected=PlaceholderFormat.NEW_CURLY,
                migrations_applied=[],
                errors=[error_msg],
                warnings=[],
                success=False,
                timestamp=datetime.now(),
                hash_before=text_hash,
                hash_after=text_hash,
                performance_metrics={
                    "migration_time": time.time() - start_time,
                    "cache_hit": False,
                    "error": str(e)
                }
            )
            
            self._update_metrics(result)
            return result
    
    def _validate_migrated_text(self, text: str) -> Dict[str, List[str]]:
        """
        Valida texto migrado.
        
        Args:
            text: Texto migrado
            
        Returns:
            Resultado da validação
        """
        errors = []
        warnings = []
        
        # Verificar placeholders obrigatórios ausentes
        missing_required = self._check_missing_required_placeholders(text)
        if missing_required:
            warnings.append(f"Placeholders obrigatórios ausentes: {', '.join(missing_required)}")
        
        # Detectar placeholders não mapeados
        unmapped = self._detect_unmapped_placeholders(text)
        if unmapped:
            warnings.append(f"Placeholders não mapeados encontrados: {', '.join(unmapped)}")
        
        # Verificar sintaxe dos placeholders
        syntax_errors = self._check_placeholder_syntax(text)
        errors.extend(syntax_errors)
        
        return {
            "errors": errors,
            "warnings": warnings
        }
    
    def _check_missing_required_placeholders(self, text: str) -> List[str]:
        """Verifica placeholders obrigatórios ausentes."""
        missing = []
        for placeholder in self.required_placeholders:
            if f"{{{placeholder.value}}}" not in text:
                missing.append(placeholder.value)
        return missing
    
    def _detect_unmapped_placeholders(self, text: str) -> List[str]:
        """Detecta placeholders não mapeados."""
        all_placeholders = re.findall(r'\{([^}]+)\}', text)
        mapped_placeholders = {mapping.field_name for mapping in self.placeholder_mappings}
        return [p for p in all_placeholders if p not in mapped_placeholders]
    
    def _check_placeholder_syntax(self, text: str) -> List[str]:
        """Verifica sintaxe dos placeholders."""
        errors = []
        
        # Verificar placeholders malformados
        malformed_patterns = [
            r'\{[^}]*$',  # Placeholder não fechado
            r'^[^}]*\}',  # Placeholder não aberto
            r'\{\s*\}',   # Placeholder vazio
            r'\{\s*[^}]*\s+\}',  # Placeholder com espaços
        ]
        
        for pattern in malformed_patterns:
            matches = re.findall(pattern, text)
            if matches:
                errors.append(f"Placeholders malformados encontrados: {matches}")
        
        return errors
    
    def validate_placeholders(self, text: str) -> ValidationResult:
        """
        Valida placeholders no texto.
        
        Args:
            text: Texto para validação
            
        Returns:
            Resultado da validação
        """
        # Detectar todos os placeholders
        all_placeholders = re.findall(r'\{([^}]+)\}', text)
        placeholder_count = len(all_placeholders)
        
        # Verificar placeholders obrigatórios
        found_placeholders = set(all_placeholders)
        required_missing = []
        for placeholder in self.required_placeholders:
            if placeholder.value not in found_placeholders:
                required_missing.append(placeholder.value)
        
        # Verificar placeholders deprecated
        deprecated_used = []
        for mapping in self.placeholder_mappings:
            if mapping.deprecated and mapping.field_name in found_placeholders:
                deprecated_used.append(mapping.field_name)
        
        # Calcular scores
        completeness_score = 1.0 - (len(required_missing) / len(self.required_placeholders)) if self.required_placeholders else 1.0
        consistency_score = 1.0 - (len(deprecated_used) / placeholder_count) if placeholder_count > 0 else 1.0
        
        # Determinar se é válido
        is_valid = len(required_missing) == 0 and len(deprecated_used) == 0
        
        # Gerar issues e warnings
        issues = []
        warnings = []
        suggestions = []
        
        if required_missing:
            issues.append(f"Placeholders obrigatórios ausentes: {', '.join(required_missing)}")
            suggestions.append("Adicione os placeholders obrigatórios ao texto")
        
        if deprecated_used:
            warnings.append(f"Placeholders deprecated usados: {', '.join(deprecated_used)}")
            suggestions.append("Substitua placeholders deprecated pelos novos")
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions,
            consistency_score=consistency_score,
            completeness_score=completeness_score,
            placeholder_count=placeholder_count,
            required_missing=required_missing,
            deprecated_used=deprecated_used
        )
    
    def _update_metrics(self, result: MigrationResult):
        """Atualiza métricas do sistema."""
        self.metrics["total_migrations"] += 1
        
        if result.success:
            self.metrics["successful_migrations"] += 1
        else:
            self.metrics["failed_migrations"] += 1
        
        # Atualizar tempo médio
        if result.performance_metrics and "migration_time" in result.performance_metrics:
            migration_time = result.performance_metrics["migration_time"]
            self.metrics["migration_times"].append(migration_time)
            
            if len(self.metrics["migration_times"]) > 0:
                self.metrics["avg_migration_time"] = statistics.mean(self.metrics["migration_times"])
        
        # Atualizar cache hit rate
        total_cache_requests = self.cache_hits + self.cache_misses
        if total_cache_requests > 0:
            self.metrics["cache_hit_rate"] = self.cache_hits / total_cache_requests
        
        # Atualizar erros por tipo
        if result.errors:
            for error in result.errors:
                error_type = "general"
                if "deprecated" in error.lower():
                    error_type = "deprecated"
                elif "syntax" in error.lower():
                    error_type = "syntax"
                elif "missing" in error.lower():
                    error_type = "missing"
                
                self.metrics["errors_by_type"][error_type] += 1
    
    def get_migration_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de migração."""
        return {
            "total_migrations": self.metrics["total_migrations"],
            "successful_migrations": self.metrics["successful_migrations"],
            "failed_migrations": self.metrics["failed_migrations"],
            "success_rate": self.metrics["successful_migrations"] / self.metrics["total_migrations"] if self.metrics["total_migrations"] > 0 else 0.0,
            "format_detections": dict(self.metrics["format_detections"]),
            "avg_migration_time": self.metrics["avg_migration_time"],
            "cache_hit_rate": self.metrics["cache_hit_rate"],
            "errors_by_type": dict(self.metrics["errors_by_type"]),
            "cache_size": len(self.migration_cache)
        }
    
    def clear_cache(self):
        """Limpa cache de migrações."""
        self.migration_cache.clear()
        logger.info("Cache de migrações limpo")


# Funções de conveniência
def migrate_placeholders(text: str, force: bool = False) -> MigrationResult:
    """Migra placeholders para formato padrão."""
    system = PlaceholderUnificationSystem()
    return system.migrate_to_standard_format(text, force)


def detect_placeholder_format(text: str) -> PlaceholderFormat:
    """Detecta formato dos placeholders."""
    system = PlaceholderUnificationSystem()
    return system.detect_format(text)


def validate_placeholders(text: str) -> ValidationResult:
    """Valida placeholders no texto."""
    system = PlaceholderUnificationSystem()
    return system.validate_placeholders(text)


def get_migration_stats() -> Dict[str, Any]:
    """Obtém estatísticas de migração."""
    system = PlaceholderUnificationSystem()
    return system.get_migration_statistics()


# Instância global para uso em outros módulos
unification_system = PlaceholderUnificationSystem() 