"""
Módulo de Padronização de Placeholders para Prompts
Responsável por unificar formatos de placeholders em todo o sistema.

Prompt: CHECKLIST_PRIMEIRA_REVISAO_PROMT_FUNCTION.md - C1.1
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from shared.logger import logger
from domain.models import Keyword, Cluster

class PlaceholderFormat(Enum):
    """Formatos de placeholders suportados."""
    OLD_BRACKETS = "old_brackets"  # [PALAVRA-CHAVE], [CLUSTER]
    NEW_CURLY = "new_curly"        # {primary_keyword}, {cluster_id}
    TEMPLATE_DOLLAR = "template_dollar"  # $primary_keyword, $cluster_id

@dataclass
class PlaceholderMapping:
    """Mapeamento de placeholders antigos para novos."""
    old_format: str
    new_format: str
    field_name: str
    description: str
    required: bool = True
    default_value: Optional[str] = None

class PromptStandardizer:
    """
    Padronizador de placeholders para prompts.
    
    Responsabilidades:
    - Migração de formatos antigos para novos
    - Validação de placeholders obrigatórios
    - Detecção automática de formato
    - Conversão segura entre formatos
    """
    
    def __init__(self):
        """Inicializa o padronizador de prompts."""
        self.placeholder_mappings = self._create_placeholder_mappings()
        self.required_placeholders = {
            'primary_keyword', 'cluster_id', 'categoria'
        }
        self.optional_placeholders = {
            'secondary_keywords', 'fase_funil', 'data', 'usuario'
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "prompt_standardizer_initialized",
            "status": "success",
            "source": "prompt_standardizer.__init__",
            "details": {
                "total_mappings": len(self.placeholder_mappings),
                "required_placeholders": len(self.required_placeholders),
                "optional_placeholders": len(self.optional_placeholders)
            }
        })
    
    def _create_placeholder_mappings(self) -> List[PlaceholderMapping]:
        """Cria mapeamentos de placeholders antigos para novos."""
        return [
            # Placeholders principais
            PlaceholderMapping(
                old_format="[PALAVRA-CHAVE]",
                new_format="{primary_keyword}",
                field_name="primary_keyword",
                description="Palavra-chave principal do prompt",
                required=True
            ),
            PlaceholderMapping(
                old_format="[CLUSTER]",
                new_format="{cluster_id}",
                field_name="cluster_id",
                description="ID do cluster relacionado",
                required=True
            ),
            PlaceholderMapping(
                old_format="[CATEGORIA]",
                new_format="{categoria}",
                field_name="categoria",
                description="Categoria do conteúdo",
                required=True
            ),
            
            # Placeholders secundários
            PlaceholderMapping(
                old_format="[PALAVRAS-SECUNDARIAS]",
                new_format="{secondary_keywords}",
                field_name="secondary_keywords",
                description="Lista de palavras-chave secundárias",
                required=False
            ),
            PlaceholderMapping(
                old_format="[FASE-FUNIL]",
                new_format="{fase_funil}",
                field_name="fase_funil",
                description="Fase do funil de conversão",
                required=False
            ),
            PlaceholderMapping(
                old_format="[DATA]",
                new_format="{data}",
                field_name="data",
                description="Data de geração do prompt",
                required=False,
                default_value=datetime.utcnow().strftime('%Y-%m-%data %H:%M:%S')
            ),
            PlaceholderMapping(
                old_format="[USUARIO]",
                new_format="{usuario}",
                field_name="usuario",
                description="Usuário que gerou o prompt",
                required=False
            ),
            
            # Placeholders específicos do cluster
            PlaceholderMapping(
                old_format="[CLUSTER-NOME]",
                new_format="{cluster_name}",
                field_name="cluster_name",
                description="Nome do cluster",
                required=False
            ),
            PlaceholderMapping(
                old_format="[CLUSTER-CATEGORIA]",
                new_format="{cluster_categoria}",
                field_name="cluster_categoria",
                description="Categoria do cluster",
                required=False
            ),
            PlaceholderMapping(
                old_format="[CLUSTER-SIMILARIDADE]",
                new_format="{cluster_similaridade}",
                field_name="cluster_similaridade",
                description="Similaridade média do cluster",
                required=False
            ),
        ]
    
    def detect_format(self, prompt: str) -> PlaceholderFormat:
        """
        Detecta o formato dos placeholders no prompt.
        
        Args:
            prompt: Conteúdo do prompt
            
        Returns:
            Formato detectado
        """
        if re.search(r'\[[A-Z\-]+\]', prompt):
            return PlaceholderFormat.OLD_BRACKETS
        elif re.search(r'\{[a-z_]+\}', prompt):
            return PlaceholderFormat.NEW_CURLY
        elif re.search(r'\$[a-z_]+', prompt):
            return PlaceholderFormat.TEMPLATE_DOLLAR
        else:
            # Padrão: assumir novo formato se não detectar nada
            return PlaceholderFormat.NEW_CURLY
    
    def migrate_to_standard_format(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Migra prompt para formato padrão (new_curly).
        
        Args:
            prompt: Prompt original
            
        Returns:
            Tupla (prompt_migrado, relatorio_migracao)
        """
        original_prompt = prompt
        detected_format = self.detect_format(prompt)
        migrations_applied = []
        errors = []
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "migracao_prompt_iniciada",
            "status": "info",
            "source": "prompt_standardizer.migrate_to_standard_format",
            "details": {
                "formato_detectado": detected_format.value,
                "tamanho_prompt": len(prompt)
            }
        })
        
        try:
            # Migrar de formato antigo para novo
            if detected_format == PlaceholderFormat.OLD_BRACKETS:
                for mapping in self.placeholder_mappings:
                    if mapping.old_format in prompt:
                        prompt = prompt.replace(mapping.old_format, mapping.new_format)
                        migrations_applied.append({
                            "old": mapping.old_format,
                            "new": mapping.new_format,
                            "field": mapping.field_name
                        })
            
            # Migrar de template_dollar para new_curly
            elif detected_format == PlaceholderFormat.TEMPLATE_DOLLAR:
                prompt = re.sub(r'\$([a-z_]+)', r'{\1}', prompt)
                migrations_applied.append({
                    "old": "template_dollar",
                    "new": "new_curly",
                    "field": "all_placeholders"
                })
            
            # Validar placeholders obrigatórios
            missing_required = self._validate_required_placeholders(prompt)
            if missing_required:
                errors.append(f"Placeholders obrigatórios ausentes: {missing_required}")
            
            # Detectar placeholders não mapeados
            unmapped_placeholders = self._detect_unmapped_placeholders(prompt)
            if unmapped_placeholders:
                errors.append(f"Placeholders não mapeados: {unmapped_placeholders}")
            
            relatorio = {
                "formato_original": detected_format.value,
                "formato_final": PlaceholderFormat.NEW_CURLY.value,
                "migrations_aplicadas": migrations_applied,
                "placeholders_obrigatorios_ausentes": missing_required,
                "placeholders_nao_mapeados": unmapped_placeholders,
                "erros": errors,
                "sucesso": len(errors) == 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if relatorio["sucesso"]:
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "migracao_prompt_concluida",
                    "status": "success",
                    "source": "prompt_standardizer.migrate_to_standard_format",
                    "details": relatorio
                })
            else:
                logger.warning({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "migracao_prompt_com_erros",
                    "status": "warning",
                    "source": "prompt_standardizer.migrate_to_standard_format",
                    "details": relatorio
                })
            
            return prompt, relatorio
            
        except Exception as e:
            error_msg = f"Erro durante migração: {str(e)}"
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_migracao_prompt",
                "status": "error",
                "source": "prompt_standardizer.migrate_to_standard_format",
                "details": {"erro": error_msg, "prompt_original": original_prompt[:200]}
            })
            
            return original_prompt, {
                "erro": error_msg,
                "sucesso": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _validate_required_placeholders(self, prompt: str) -> List[str]:
        """
        Valida se placeholders obrigatórios estão presentes.
        
        Args:
            prompt: Prompt para validar
            
        Returns:
            Lista de placeholders obrigatórios ausentes
        """
        missing = []
        for placeholder in self.required_placeholders:
            if f"{{{placeholder}}}" not in prompt:
                missing.append(placeholder)
        return missing
    
    def _detect_unmapped_placeholders(self, prompt: str) -> List[str]:
        """
        Detecta placeholders não mapeados no prompt.
        
        Args:
            prompt: Prompt para analisar
            
        Returns:
            Lista de placeholders não mapeados
        """
        all_placeholders = re.findall(r'\{([^}]+)\}', prompt)
        mapped_placeholders = {mapping.field_name for mapping in self.placeholder_mappings}
        return [p for p in all_placeholders if p not in mapped_placeholders]
    
    def validate_prompt_structure(self, prompt: str) -> Tuple[bool, List[str]]:
        """
        Valida estrutura completa do prompt.
        
        Args:
            prompt: Prompt para validar
            
        Returns:
            Tupla (valido, erros)
        """
        errors = []
        
        # Verificar se está vazio
        if not prompt or not prompt.strip():
            errors.append("Prompt está vazio")
        
        # Verificar tamanho mínimo
        if len(prompt.strip()) < 10:
            errors.append("Prompt muito curto (mínimo 10 caracteres)")
        
        # Verificar tamanho máximo
        if len(prompt) > 10000:
            errors.append("Prompt muito longo (máximo 10.000 caracteres)")
        
        # Verificar placeholders obrigatórios
        missing_required = self._validate_required_placeholders(prompt)
        if missing_required:
            errors.append(f"Placeholders obrigatórios ausentes: {missing_required}")
        
        # Verificar placeholders não mapeados
        unmapped = self._detect_unmapped_placeholders(prompt)
        if unmapped:
            errors.append(f"Placeholders não mapeados: {unmapped}")
        
        # Verificar caracteres especiais problemáticos
        problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07']
        for char in problematic_chars:
            if char in prompt:
                errors.append(f"Caractere inválido encontrado: {repr(char)}")
        
        return len(errors) == 0, errors
    
    def generate_standard_template(self, 
                                 primary_keyword: str,
                                 cluster_id: str,
                                 categoria: str,
                                 **kwargs) -> str:
        """
        Gera template padrão com placeholders.
        
        Args:
            primary_keyword: Palavra-chave principal
            cluster_id: ID do cluster
            categoria: Categoria do conteúdo
            **kwargs: Outros parâmetros opcionais
            
        Returns:
            Template padrão
        """
        template = f"""Você deve gerar 6 artigos distintos com base nas palavras-chave a seguir.

Cada artigo deve estar numerado de 1 a 6, em ordem crescente, respeitando a sequência abaixo, pois serão publicados com 4 horas de intervalo. Cada artigo pertence a uma fase da jornada de conteúdo:

1. Artigo 1 — Fase: Descoberta — Palavra-chave principal: {{{primary_keyword}}}
2. Artigo 2 — Fase: Curiosidade — Palavra-chave principal: {{{primary_keyword}}}
3. Artigo 3 — Fase: Consideração — Palavra-chave principal: {{{primary_keyword}}}
4. Artigo 4 — Fase: Comparação — Palavra-chave principal: {{{primary_keyword}}}
5. Artigo 5 — Fase: Decisão — Palavra-chave principal: {{{primary_keyword}}}
6. Artigo 6 — Fase: Autoridade — Palavra-chave principal: {{{primary_keyword}}}

Cluster: {{{cluster_id}}}
Categoria: {{{categoria}}}

Palavras-chave secundárias: {{{kwargs.get('secondary_keywords', '')}}}

Todos os artigos devem seguir o estilo definido no arquivo `prompt_base.txt` deste blog.

Data de geração: {{{kwargs.get('data', '{data}')}}}
Usuário: {{{kwargs.get('usuario', '{usuario}')}}}"""
        
        return template
    
    def get_placeholder_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre placeholders suportados.
        
        Returns:
            Dicionário com informações dos placeholders
        """
        return {
            "formatos_suportados": [fmt.value for fmt in PlaceholderFormat],
            "placeholders_obrigatorios": list(self.required_placeholders),
            "placeholders_opcionais": list(self.optional_placeholders),
            "mapeamentos": [
                {
                    "old_format": m.old_format,
                    "new_format": m.new_format,
                    "field_name": m.field_name,
                    "description": m.description,
                    "required": m.required,
                    "default_value": m.default_value
                }
                for m in self.placeholder_mappings
            ],
            "total_mapeamentos": len(self.placeholder_mappings)
        } 