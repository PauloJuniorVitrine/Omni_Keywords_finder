"""
Schemas de Validação para Auditoria - Omni Keywords Finder
Validação robusta e estrutura de dados para auditoria
Prompt: Implementação de sistema de auditoria
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator

class AuditEventType(Enum):
    """Tipos de eventos de auditoria"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    PAYMENT_CREATED = "payment_created"
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"
    WEBHOOK_CREATED = "webhook_created"
    WEBHOOK_UPDATED = "webhook_updated"
    WEBHOOK_DELETED = "webhook_deleted"
    WEBHOOK_TRIGGERED = "webhook_triggered"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    CONFIGURATION_CHANGED = "configuration_changed"
    SECURITY_EVENT = "security_event"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class AuditSeverity(Enum):
    """Níveis de severidade de auditoria"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditCategory(Enum):
    """Categorias de auditoria"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"

class AuditLogEntry(BaseModel):
    """Schema para entrada de log de auditoria"""
    
    # Identificação
    log_id: str = Field(..., description="ID único do log")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp do evento")
    event_type: str = Field(..., description="Tipo do evento")
    severity: str = Field(default="info", description="Nível de severidade")
    category: str = Field(default="system", description="Categoria do evento")
    
    # Contexto
    user_id: Optional[str] = Field(None, description="ID do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User-Agent")
    request_id: Optional[str] = Field(None, description="ID da requisição")
    
    # Dados do evento
    message: str = Field(..., description="Mensagem do evento")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Detalhes do evento")
    resource_type: Optional[str] = Field(None, description="Tipo do recurso")
    resource_id: Optional[str] = Field(None, description="ID do recurso")
    
    # Metadados
    source: str = Field(default="api", description="Origem do evento")
    version: str = Field(default="1.0", description="Versão do schema")
    environment: str = Field(default="production", description="Ambiente")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        """Valida tipo do evento"""
        valid_events = [event.value for event in AuditEventType]
        if v not in valid_events:
            raise ValueError(f'Evento não suportado. Válidos: {", ".join(valid_events)}')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        """Valida nível de severidade"""
        valid_severities = [severity.value for severity in AuditSeverity]
        if v not in valid_severities:
            raise ValueError(f'Severidade inválida. Válidas: {", ".join(valid_severities)}')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        """Valida categoria"""
        valid_categories = [category.value for category in AuditCategory]
        if v not in valid_categories:
            raise ValueError(f'Categoria inválida. Válidas: {", ".join(valid_categories)}')
        return v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Valida ID do usuário"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            return sanitized
        return v
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        """Valida endereço IP"""
        if v:
            # Validação básica de IP
            ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ip_pattern, v):
                raise ValueError('Endereço IP inválido')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Sanitiza mensagem"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        return sanitized
    
    @validator('details')
    def validate_details(cls, v):
        """Sanitiza detalhes"""
        if v:
            sanitized = {}
            for key, value in v.items():
                clean_key = re.sub(r'[<>"\']', '', str(key))
                if clean_key:
                    if isinstance(value, str):
                        clean_value = re.sub(r'[<>"\']', '', value)
                    else:
                        clean_value = value
                    sanitized[clean_key] = clean_value
            return sanitized
        return v

class AuditFilterSchema(BaseModel):
    """Schema para filtros de auditoria"""
    
    # Filtros de tempo
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    
    # Filtros de evento
    event_types: Optional[List[str]] = Field(None, description="Tipos de evento")
    severities: Optional[List[str]] = Field(None, description="Níveis de severidade")
    categories: Optional[List[str]] = Field(None, description="Categorias")
    
    # Filtros de usuário
    user_id: Optional[str] = Field(None, description="ID do usuário")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    
    # Filtros de recurso
    resource_type: Optional[str] = Field(None, description="Tipo do recurso")
    resource_id: Optional[str] = Field(None, description="ID do recurso")
    
    # Paginação
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Limite de resultados")
    offset: Optional[int] = Field(None, ge=0, description="Offset para paginação")
    
    # Ordenação
    sort_by: Optional[str] = Field(default="timestamp", description="Campo para ordenação")
    sort_order: Optional[str] = Field(default="desc", description="Ordem de classificação")
    
    @validator('event_types')
    def validate_event_types(cls, v):
        """Valida tipos de evento"""
        if v:
            valid_events = [event.value for event in AuditEventType]
            for event_type in v:
                if event_type not in valid_events:
                    raise ValueError(f'Evento não suportado: {event_type}')
        return v
    
    @validator('severities')
    def validate_severities(cls, v):
        """Valida níveis de severidade"""
        if v:
            valid_severities = [severity.value for severity in AuditSeverity]
            for severity in v:
                if severity not in valid_severities:
                    raise ValueError(f'Severidade inválida: {severity}')
        return v
    
    @validator('categories')
    def validate_categories(cls, v):
        """Valida categorias"""
        if v:
            valid_categories = [category.value for category in AuditCategory]
            for category in v:
                if category not in valid_categories:
                    raise ValueError(f'Categoria inválida: {category}')
        return v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Valida ID do usuário"""
        if v:
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            return sanitized
        return v
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        """Valida endereço IP"""
        if v:
            ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ip_pattern, v):
                raise ValueError('Endereço IP inválido')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Valida campo de ordenação"""
        valid_fields = [
            'timestamp', 'event_type', 'severity', 'category', 
            'user_id', 'ip_address', 'resource_type', 'resource_id'
        ]
        if v not in valid_fields:
            raise ValueError(f'Campo de ordenação inválido. Válidos: {", ".join(valid_fields)}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Valida ordem de classificação"""
        if v not in ['asc', 'desc']:
            raise ValueError('Ordem de classificação deve ser "asc" ou "desc"')
        return v
    
    @root_validator
    def validate_date_range(cls, values):
        """Valida range de datas"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError('Data inicial não pode ser posterior à data final')
        
        return values

class AuditReportSchema(BaseModel):
    """Schema para relatórios de auditoria"""
    
    # Metadados do relatório
    report_id: str = Field(..., description="ID único do relatório")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Data de geração")
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    # Filtros aplicados
    filters: AuditFilterSchema = Field(..., description="Filtros aplicados")
    
    # Estatísticas
    total_events: int = Field(..., description="Total de eventos")
    events_by_type: Dict[str, int] = Field(default_factory=dict, description="Eventos por tipo")
    events_by_severity: Dict[str, int] = Field(default_factory=dict, description="Eventos por severidade")
    events_by_category: Dict[str, int] = Field(default_factory=dict, description="Eventos por categoria")
    events_by_user: Dict[str, int] = Field(default_factory=dict, description="Eventos por usuário")
    
    # Análise de segurança
    security_events: int = Field(..., description="Eventos de segurança")
    unauthorized_access: int = Field(..., description="Tentativas de acesso não autorizado")
    suspicious_activity: int = Field(..., description="Atividades suspeitas")
    rate_limit_violations: int = Field(..., description="Violações de rate limiting")
    
    # Performance
    average_events_per_hour: float = Field(..., description="Média de eventos por hora")
    peak_hour: str = Field(..., description="Hora de pico")
    peak_events: int = Field(..., description="Eventos no pico")
    
    # Recomendações
    recommendations: List[str] = Field(default_factory=list, description="Recomendações de segurança")

class AuditExportSchema(BaseModel):
    """Schema para exportação de auditoria"""
    
    # Configuração de exportação
    format: str = Field(default="json", description="Formato de exportação")
    include_details: bool = Field(default=True, description="Incluir detalhes")
    include_metadata: bool = Field(default=True, description="Incluir metadados")
    
    # Filtros
    filters: AuditFilterSchema = Field(..., description="Filtros para exportação")
    
    # Configurações de arquivo
    filename: Optional[str] = Field(None, description="Nome do arquivo")
    compression: bool = Field(default=False, description="Comprimir arquivo")
    
    @validator('format')
    def validate_format(cls, v):
        """Valida formato de exportação"""
        valid_formats = ['json', 'csv', 'xml', 'pdf']
        if v not in valid_formats:
            raise ValueError(f'Formato inválido. Válidos: {", ".join(valid_formats)}')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        """Valida nome do arquivo"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>:"/\\|?*]', '', str(v).strip())
            return sanitized
        return v 