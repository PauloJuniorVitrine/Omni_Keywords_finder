#!/usr/bin/env python3
"""
Sistema Unificado de Placeholders - Omni Keywords Finder
=======================================================

Tracing ID: PLACEHOLDER_UNIFICATION_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema que unifica todos os padrões de placeholders em um formato padrão:
- Migração automática de formatos antigos
- Validação de consistência
- Detecção de incompatibilidades
- Sistema de fallback inteligente

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.1
Ruleset: enterprise_control_layer.yaml
"""

import re
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import sqlite3
from collections import defaultdict

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


class PlaceholderUnificationSystem:
    """
    Sistema unificado de placeholders.
    
    Responsabilidades:
    - Detecção automática de formatos
    - Migração segura entre formatos
    - Validação de consistência
    - Sistema de fallback
    - Auditoria de mudanças
    """
    
    def __init__(self):
        """Inicializa o sistema de unificação."""
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
        
        # Cache de migrações
        self.migration_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Métricas
        self.metrics = {
            "total_migrations": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "format_detections": defaultdict(int),
            "migration_times": []
        }
        
        logger.info("Sistema de unificação de placeholders inicializado")
    
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
                old_format="[FASE-FUNIL]",
                new_format="{fase_funil}",
                field_name="fase_funil",
                description="Fase do funil de conversão",
                required=False,
                migration_priority=2
            ),
            
            # Placeholders específicos do cluster
            PlaceholderMapping(
                old_format="[CLUSTER-NOME]",
                new_format="{cluster_name}",
                field_name="cluster_name",
                description="Nome do cluster",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[CLUSTER-CATEGORIA]",
                new_format="{cluster_categoria}",
                field_name="cluster_categoria",
                description="Categoria do cluster",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[CLUSTER-SIMILARIDADE]",
                new_format="{cluster_similaridade}",
                field_name="cluster_similaridade",
                description="Similaridade média do cluster",
                required=False,
                migration_priority=3
            ),
            
            # Placeholders de contexto
            PlaceholderMapping(
                old_format="[DATA]",
                new_format="{data}",
                field_name="data",
                description="Data de geração do prompt",
                required=False,
                default_value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                migration_priority=4
            ),
            PlaceholderMapping(
                old_format="[USUARIO]",
                new_format="{usuario}",
                field_name="usuario",
                description="Usuário que gerou o prompt",
                required=False,
                migration_priority=4
            ),
            
            # Placeholders de conteúdo
            PlaceholderMapping(
                old_format="[NICHE]",
                new_format="{niche}",
                field_name="niche",
                description="Nicho do conteúdo",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[PUBLICO-ALVO]",
                new_format="{target_audience}",
                field_name="target_audience",
                description="Público-alvo do conteúdo",
                required=False,
                migration_priority=3
            ),
            PlaceholderMapping(
                old_format="[TIPO-CONTEUDO]",
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
        ]
    
    def detect_format(self, text: str) -> PlaceholderFormat:
        """
        Detecta o formato dos placeholders no texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Formato detectado
        """
        # Padrões de detecção
        patterns = {
            PlaceholderFormat.OLD_BRACKETS: r'\[[A-Z\- ]+\]',
            PlaceholderFormat.NEW_CURLY: r'\{[a-z_]+\}',
            PlaceholderFormat.TEMPLATE_DOLLAR: r'\$[a-z_]+',
            PlaceholderFormat.ANGULAR_BRACKETS: r'<[a-z_]+>',
            PlaceholderFormat.DOUBLE_BRACKETS: r'\[\[[a-z_]+\]\]'
        }
        
        # Contar ocorrências de cada formato
        format_counts = {}
        for format_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            format_counts[format_type] = len(matches)
        
        # Determinar formato dominante
        if format_counts:
            dominant_format = max(format_counts.items(), key=lambda x: x[1])
            if dominant_format[1] > 0:
                self.metrics["format_detections"][dominant_format[0].value] += 1
                return dominant_format[0]
        
        # Padrão: assumir novo formato se não detectar nada
        return PlaceholderFormat.NEW_CURLY
    
    def migrate_to_standard_format(self, text: str, force_migration: bool = False) -> MigrationResult:
        """
        Migra texto para formato padrão unificado.
        
        Args:
            text: Texto para migrar
            force_migration: Forçar migração mesmo se já estiver no formato padrão
            
        Returns:
            Resultado da migração
        """
        import time
        start_time = time.time()
        
        # Gerar hash do texto original
        hash_before = hashlib.md5(text.encode()).hexdigest()
        
        # Verificar cache
        cache_key = f"{hash_before}_{force_migration}"
        if cache_key in self.migration_cache:
            cached_result = self.migration_cache[cache_key]
            if time.time() - cached_result["timestamp"] < self.cache_ttl:
                logger.info("Usando resultado em cache para migração")
                return cached_result["result"]
        
        # Detectar formato atual
        detected_format = self.detect_format(text)
        
        # Se já está no formato padrão e não for forçado, retornar sem mudanças
        if detected_format == PlaceholderFormat.NEW_CURLY and not force_migration:
            result = MigrationResult(
                original_text=text,
                migrated_text=text,
                format_detected=detected_format,
                migrations_applied=[],
                errors=[],
                warnings=["Texto já está no formato padrão"],
                success=True,
                timestamp=datetime.now(),
                hash_before=hash_before,
                hash_after=hash_before
            )
            return result
        
        # Iniciar migração
        migrated_text = text
        migrations_applied = []
        errors = []
        warnings = []
        
        try:
            # Ordenar mapeamentos por prioridade
            sorted_mappings = sorted(
                self.placeholder_mappings,
                key=lambda x: x.migration_priority
            )
            
            # Aplicar migrações por prioridade
            for mapping in sorted_mappings:
                if mapping.old_format in migrated_text:
                    # Contar ocorrências antes da migração
                    occurrences_before = migrated_text.count(mapping.old_format)
                    
                    # Aplicar migração
                    migrated_text = migrated_text.replace(mapping.old_format, mapping.new_format)
                    
                    # Contar ocorrências após a migração
                    occurrences_after = migrated_text.count(mapping.new_format)
                    
                    migrations_applied.append({
                        "old_format": mapping.old_format,
                        "new_format": mapping.new_format,
                        "field_name": mapping.field_name,
                        "occurrences_before": occurrences_before,
                        "occurrences_after": occurrences_after,
                        "priority": mapping.migration_priority
                    })
            
            # Migrar formatos especiais
            if detected_format == PlaceholderFormat.TEMPLATE_DOLLAR:
                migrated_text = re.sub(r'\$([a-z_]+)', r'{\1}', migrated_text)
                migrations_applied.append({
                    "old_format": "template_dollar",
                    "new_format": "new_curly",
                    "field_name": "all_placeholders",
                    "occurrences_before": 0,
                    "occurrences_after": 0,
                    "priority": 1
                })
            
            elif detected_format == PlaceholderFormat.ANGULAR_BRACKETS:
                migrated_text = re.sub(r'<([a-z_]+)>', r'{\1}', migrated_text)
                migrations_applied.append({
                    "old_format": "angular_brackets",
                    "new_format": "new_curly",
                    "field_name": "all_placeholders",
                    "occurrences_before": 0,
                    "occurrences_after": 0,
                    "priority": 1
                })
            
            elif detected_format == PlaceholderFormat.DOUBLE_BRACKETS:
                migrated_text = re.sub(r'\[\[([a-z_]+)\]\]', r'{\1}', migrated_text)
                migrations_applied.append({
                    "old_format": "double_brackets",
                    "new_format": "new_curly",
                    "field_name": "all_placeholders",
                    "occurrences_before": 0,
                    "occurrences_after": 0,
                    "priority": 1
                })
            
            # Validar resultado
            validation_result = self._validate_migrated_text(migrated_text)
            errors.extend(validation_result["errors"])
            warnings.extend(validation_result["warnings"])
            
            # Gerar hash do texto migrado
            hash_after = hashlib.md5(migrated_text.encode()).hexdigest()
            
            # Calcular tempo de execução
            execution_time = time.time() - start_time
            self.metrics["migration_times"].append(execution_time)
            
            # Criar resultado
            result = MigrationResult(
                original_text=text,
                migrated_text=migrated_text,
                format_detected=detected_format,
                migrations_applied=migrations_applied,
                errors=errors,
                warnings=warnings,
                success=len(errors) == 0,
                timestamp=datetime.now(),
                hash_before=hash_before,
                hash_after=hash_after
            )
            
            # Atualizar métricas
            self.metrics["total_migrations"] += 1
            if result.success:
                self.metrics["successful_migrations"] += 1
            else:
                self.metrics["failed_migrations"] += 1
            
            # Armazenar no cache
            self.migration_cache[cache_key] = {
                "result": result,
                "timestamp": time.time()
            }
            
            # Log do resultado
            if result.success:
                logger.info(f"Migração concluída com sucesso: {len(migrations_applied)} mudanças aplicadas")
            else:
                logger.warning(f"Migração concluída com erros: {len(errors)} problemas encontrados")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro durante migração: {str(e)}"
            logger.error(f"Erro na migração: {error_msg}")
            
            return MigrationResult(
                original_text=text,
                migrated_text=text,
                format_detected=detected_format,
                migrations_applied=[],
                errors=[error_msg],
                warnings=[],
                success=False,
                timestamp=datetime.now(),
                hash_before=hash_before,
                hash_after=hash_before
            )
    
    def _validate_migrated_text(self, text: str) -> Dict[str, List[str]]:
        """
        Valida texto migrado.
        
        Args:
            text: Texto para validar
            
        Returns:
            Dicionário com erros e warnings
        """
        errors = []
        warnings = []
        
        # Verificar placeholders obrigatórios
        missing_required = self._check_missing_required_placeholders(text)
        if missing_required:
            errors.append(f"Placeholders obrigatórios ausentes: {missing_required}")
        
        # Verificar placeholders não mapeados
        unmapped = self._detect_unmapped_placeholders(text)
        if unmapped:
            warnings.append(f"Placeholders não mapeados detectados: {unmapped}")
        
        # Verificar sintaxe de placeholders
        syntax_errors = self._check_placeholder_syntax(text)
        if syntax_errors:
            errors.extend(syntax_errors)
        
        # Verificar caracteres especiais problemáticos
        problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07']
        for char in problematic_chars:
            if char in text:
                errors.append(f"Caractere inválido encontrado: {repr(char)}")
        
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
    
    def get_migration_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de migração."""
        return {
            "total_migrations": self.metrics["total_migrations"],
            "successful_migrations": self.metrics["successful_migrations"],
            "failed_migrations": self.metrics["failed_migrations"],
            "success_rate": (
                self.metrics["successful_migrations"] / self.metrics["total_migrations"]
                if self.metrics["total_migrations"] > 0 else 0
            ),
            "format_detections": dict(self.metrics["format_detections"]),
            "avg_migration_time": (
                sum(self.metrics["migration_times"]) / len(self.metrics["migration_times"])
                if self.metrics["migration_times"] else 0
            ),
            "cache_size": len(self.migration_cache)
        }
    
    def clear_cache(self):
        """Limpa cache de migrações."""
        self.migration_cache.clear()
        logger.info("Cache de migrações limpo")


# Instância global
placeholder_unification_system = PlaceholderUnificationSystem()


# Funções de conveniência
def migrate_placeholders(text: str, force: bool = False) -> MigrationResult:
    """Migra placeholders para formato padrão."""
    return placeholder_unification_system.migrate_to_standard_format(text, force)


def detect_placeholder_format(text: str) -> PlaceholderFormat:
    """Detecta formato de placeholders no texto."""
    return placeholder_unification_system.detect_format(text)


def get_migration_stats() -> Dict[str, Any]:
    """Retorna estatísticas de migração."""
    return placeholder_unification_system.get_migration_statistics()


if __name__ == "__main__":
    # Exemplo de uso
    test_texts = [
        "Crie um [TIPO-CONTEUDO] sobre [PALAVRA-CHAVE] para [PUBLICO-ALVO]",
        "Gere {content_type} sobre {primary_keyword} para {target_audience}",
        "Faça $content_type sobre $primary_keyword para $target_audience",
        "Produza <content_type> sobre <primary_keyword> para <target_audience>",
        "Crie [[content_type]] sobre [[primary_keyword]] para [[target_audience]]"
    ]
    
    print("=== Teste de Migração de Placeholders ===\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"Teste {i}:")
        print(f"Texto original: {text}")
        
        # Detectar formato
        detected_format = detect_placeholder_format(text)
        print(f"Formato detectado: {detected_format.value}")
        
        # Migrar
        result = migrate_placeholders(text)
        print(f"Texto migrado: {result.migrated_text}")
        print(f"Sucesso: {result.success}")
        print(f"Mudanças aplicadas: {len(result.migrations_applied)}")
        
        if result.errors:
            print(f"Erros: {result.errors}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
        
        print("-" * 50)
    
    # Estatísticas
    stats = get_migration_stats()
    print("\n=== Estatísticas ===")
    print(json.dumps(stats, indent=2, default=str)) 