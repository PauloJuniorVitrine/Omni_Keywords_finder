"""
Field Selector - Optional Field Selection for API Responses

Prompt: CHECKLIST_RESOLUCAO_GARGALOS.md - Fase 3.2.2
Ruleset: enterprise_control_layer.yaml
Date: 2025-01-27
Tracing ID: CHECKLIST_RESOLUCAO_GARGALOS_20250127_001
"""

import re
import json
import logging
from typing import Dict, List, Optional, Union, Any, Set
from fastapi import Query, Request
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger(__name__)

class FieldSelectorMode(Enum):
    """Modos de seleção de campos"""
    INCLUDE = "include"  # Incluir apenas campos especificados
    EXCLUDE = "exclude"  # Excluir campos especificados
    AUTO = "auto"        # Automático baseado em contexto

class FieldSelectorConfig:
    """Configuração do seletor de campos"""
    
    def __init__(
        self,
        default_mode: FieldSelectorMode = FieldSelectorMode.AUTO,
        max_fields: int = 50,
        allow_nested: bool = True,
        allow_wildcards: bool = True,
        cache_selections: bool = True,
        default_fields: Optional[List[str]] = None
    ):
        self.default_mode = default_mode
        self.max_fields = max_fields
        self.allow_nested = allow_nested
        self.allow_wildcards = allow_wildcards
        self.cache_selections = cache_selections
        self.default_fields = default_fields or []

class FieldSelector:
    """Seletor de campos para otimização de payloads"""
    
    def __init__(self, config: Optional[FieldSelectorConfig] = None):
        self.config = config or FieldSelectorConfig()
        self.field_cache: Dict[str, Set[str]] = {}
    
    def parse_field_selection(
        self,
        fields_param: Optional[str] = None,
        mode: Optional[FieldSelectorMode] = None
    ) -> Set[str]:
        """Parse do parâmetro de seleção de campos"""
        if not fields_param:
            return set(self.config.default_fields)
        
        # Remove espaços e quebras de linha
        fields_param = re.sub(r'\s+', '', fields_param)
        
        # Divide por vírgula
        field_list = [f.strip() for f in fields_param.split(',') if f.strip()]
        
        # Valida número máximo de campos
        if len(field_list) > self.config.max_fields:
            logger.warning(f"Too many fields requested: {len(field_list)} > {self.config.max_fields}")
            field_list = field_list[:self.config.max_fields]
        
        # Processa wildcards se habilitado
        if self.config.allow_wildcards:
            field_list = self._expand_wildcards(field_list)
        
        return set(field_list)
    
    def _expand_wildcards(self, fields: List[str]) -> List[str]:
        """Expande wildcards em campos"""
        expanded_fields = []
        
        for field in fields:
            if '*' in field:
                # Implementa expansão de wildcards baseada em contexto
                # Por exemplo: user.* -> user.id, user.name, user.email
                expanded_fields.extend(self._expand_wildcard(field))
            else:
                expanded_fields.append(field)
        
        return expanded_fields
    
    def _expand_wildcard(self, wildcard: str) -> List[str]:
        """Expande um wildcard específico"""
        # Mapeamento de wildcards comuns
        wildcard_mappings = {
            'user.*': ['user.id', 'user.name', 'user.email', 'user.created_at'],
            'keyword.*': ['keyword.id', 'keyword.text', 'keyword.score', 'keyword.category'],
            'analysis.*': ['analysis.id', 'analysis.status', 'analysis.created_at', 'analysis.results'],
            '*.id': ['user.id', 'keyword.id', 'analysis.id', 'project.id'],
            '*.name': ['user.name', 'project.name', 'category.name'],
            '*.created_at': ['user.created_at', 'keyword.created_at', 'analysis.created_at']
        }
        
        return wildcard_mappings.get(wildcard, [wildcard])
    
    def select_fields(
        self,
        data: Union[Dict, List, Any],
        fields: Set[str],
        mode: FieldSelectorMode = FieldSelectorMode.INCLUDE
    ) -> Union[Dict, List, Any]:
        """Seleciona campos do objeto de dados"""
        if not fields:
            return data
        
        if isinstance(data, list):
            return [self.select_fields(item, fields, mode) for item in data]
        
        if not isinstance(data, dict):
            return data
        
        if mode == FieldSelectorMode.INCLUDE:
            return self._include_fields(data, fields)
        elif mode == FieldSelectorMode.EXCLUDE:
            return self._exclude_fields(data, fields)
        else:  # AUTO
            return self._auto_select_fields(data, fields)
    
    def _include_fields(self, data: Dict, fields: Set[str]) -> Dict:
        """Inclui apenas os campos especificados"""
        result = {}
        
        for field in fields:
            if '.' in field and self.config.allow_nested:
                # Campo aninhado
                value = self._get_nested_value(data, field)
                if value is not None:
                    self._set_nested_value(result, field, value)
            else:
                # Campo simples
                if field in data:
                    result[field] = data[field]
        
        return result
    
    def _exclude_fields(self, data: Dict, fields: Set[str]) -> Dict:
        """Exclui os campos especificados"""
        result = data.copy()
        
        for field in fields:
            if '.' in field and self.config.allow_nested:
                # Remove campo aninhado
                self._remove_nested_field(result, field)
            else:
                # Remove campo simples
                result.pop(field, None)
        
        return result
    
    def _auto_select_fields(self, data: Dict, fields: Set[str]) -> Dict:
        """Seleção automática baseada em contexto"""
        # Se poucos campos solicitados, usa modo INCLUDE
        if len(fields) <= len(data) // 2:
            return self._include_fields(data, fields)
        else:
            # Se muitos campos solicitados, usa modo EXCLUDE
            return self._exclude_fields(data, fields)
    
    def _get_nested_value(self, data: Dict, field_path: str) -> Any:
        """Obtém valor de campo aninhado"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _set_nested_value(self, data: Dict, field_path: str, value: Any) -> None:
        """Define valor de campo aninhado"""
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _remove_nested_field(self, data: Dict, field_path: str) -> None:
        """Remove campo aninhado"""
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return
        
        if isinstance(current, dict):
            current.pop(keys[-1], None)

class FieldSelectorMiddleware:
    """Middleware para seleção automática de campos"""
    
    def __init__(self, selector: FieldSelector):
        self.selector = selector
    
    async def process_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Processa request para extrair seleção de campos"""
        # Extrai parâmetros de seleção
        fields_param = request.query_params.get('fields')
        mode_param = request.query_params.get('field_mode')
        
        if not fields_param:
            return None
        
        # Parse do modo
        mode = FieldSelectorMode.INCLUDE
        if mode_param:
            try:
                mode = FieldSelectorMode(mode_param.lower())
            except ValueError:
                logger.warning(f"Invalid field mode: {mode_param}")
        
        # Parse dos campos
        fields = self.selector.parse_field_selection(fields_param, mode)
        
        return {
            'fields': fields,
            'mode': mode
        }

class FieldSelectorResponse:
    """Response wrapper com seleção de campos"""
    
    def __init__(self, selector: FieldSelector):
        self.selector = selector
    
    def format_response(
        self,
        data: Any,
        field_selection: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Formata response com seleção de campos"""
        if not field_selection:
            return data
        
        fields = field_selection.get('fields', set())
        mode = field_selection.get('mode', FieldSelectorMode.INCLUDE)
        
        return self.selector.select_fields(data, fields, mode)

# Instância global do seletor
field_selector = FieldSelector()

def get_field_selector() -> FieldSelector:
    """Retorna instância global do seletor de campos"""
    return field_selector

def create_field_query(
    description: str = "Campos a serem incluídos/excluídos na resposta",
    default: Optional[str] = None
) -> str:
    """Cria query parameter para seleção de campos"""
    return Query(
        default=default,
        description=description,
        example="id,name,email,user.profile",
        regex=r"^[a-zA-Z0-9_.,*]+$"
    )

def create_field_mode_query(
    description: str = "Modo de seleção de campos",
    default: FieldSelectorMode = FieldSelectorMode.INCLUDE
) -> FieldSelectorMode:
    """Cria query parameter para modo de seleção"""
    return Query(
        default=default,
        description=description,
        example="include"
    )

# Decorator para endpoints com seleção de campos
def with_field_selection(func):
    """Decorator para aplicar seleção de campos automaticamente"""
    async def wrapper(*args, **kwargs):
        # Extrai seleção de campos dos parâmetros
        fields_param = kwargs.get('fields')
        field_mode = kwargs.get('field_mode', FieldSelectorMode.INCLUDE)
        
        # Remove parâmetros de seleção dos kwargs
        kwargs.pop('fields', None)
        kwargs.pop('field_mode', None)
        
        # Executa função original
        result = await func(*args, **kwargs)
        
        # Aplica seleção de campos se especificada
        if fields_param:
            fields = field_selector.parse_field_selection(fields_param, field_mode)
            result = field_selector.select_fields(result, fields, field_mode)
        
        return result
    
    return wrapper

# Exemplo de uso em endpoint
"""
@router.get("/users/")
async def get_users(
    fields: str = create_field_query(),
    field_mode: FieldSelectorMode = create_field_mode_query()
):
    users = await user_service.get_all_users()
    
    if fields:
        field_set = field_selector.parse_field_selection(fields, field_mode)
        users = field_selector.select_fields(users, field_set, field_mode)
    
    return users
"""

# Configurações predefinidas
FIELD_SELECTOR_CONFIGS = {
    'minimal': FieldSelectorConfig(
        default_fields=['id', 'name'],
        max_fields=10
    ),
    'standard': FieldSelectorConfig(
        default_fields=['id', 'name', 'created_at'],
        max_fields=25
    ),
    'detailed': FieldSelectorConfig(
        default_fields=['id', 'name', 'email', 'created_at', 'updated_at'],
        max_fields=50,
        allow_nested=True
    )
} 