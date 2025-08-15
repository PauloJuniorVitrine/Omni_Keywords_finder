"""
Schemas de Validação para Consumo Externo - Omni Keywords Finder
Validação robusta de dados para APIs externas
Prompt: Validação de consumo externo
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator, HttpUrl
from pydantic.types import IPvAnyAddress

class ExternalEndpointSchema(BaseModel):
    """Schema para validação de endpoints externos"""
    
    endpoint: str = Field(..., min_length=1, max_length=500, description="Endpoint da API externa")
    method: str = Field(default="GET", description="Método HTTP")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, ge=0, le=5, description="Número de tentativas")
    
    @validator('endpoint')
    def validate_endpoint(cls, v):
        """Valida e sanitiza endpoint"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', v.strip())
        
        # Valida formato básico
        if not re.match(r'^[a-zA-Z0-9/._-]+$', sanitized):
            raise ValueError('Endpoint contém caracteres inválidos')
        
        # Previne path traversal
        if '..' in sanitized or '//' in sanitized:
            raise ValueError('Endpoint contém sequências perigosas')
        
        return sanitized
    
    @validator('method')
    def validate_method(cls, v):
        """Valida método HTTP"""
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if v.upper() not in valid_methods:
            raise ValueError(f'Método HTTP inválido. Válidos: {", ".join(valid_methods)}')
        return v.upper()

class ExternalRequestSchema(BaseModel):
    """Schema para requisições externas"""
    
    endpoint: str = Field(..., description="Endpoint da API externa")
    method: str = Field(default="GET", description="Método HTTP")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parâmetros da requisição")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Headers da requisição")
    body: Optional[Dict[str, Any]] = Field(None, description="Corpo da requisição")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="Timeout em segundos")
    
    @validator('params')
    def validate_params(cls, v):
        """Valida e sanitiza parâmetros"""
        if v:
            sanitized = {}
            for key, value in v.items():
                # Sanitiza chave
                clean_key = re.sub(r'[<>"\']', '', str(key))
                if clean_key:
                    # Sanitiza valor
                    if isinstance(value, str):
                        clean_value = re.sub(r'[<>"\']', '', value)
                    else:
                        clean_value = value
                    sanitized[clean_key] = clean_value
            return sanitized
        return v
    
    @validator('headers')
    def validate_headers(cls, v):
        """Valida e sanitiza headers"""
        if v:
            sanitized = {}
            for key, value in v.items():
                # Sanitiza chave
                clean_key = re.sub(r'[<>"\']', '', str(key))
                if clean_key:
                    # Sanitiza valor
                    clean_value = re.sub(r'[<>"\']', '', str(value))
                    sanitized[clean_key] = clean_value
            return sanitized
        return v
    
    @validator('body')
    def validate_body(cls, v):
        """Valida e sanitiza corpo da requisição"""
        if v:
            # Remove caracteres perigosos de strings no corpo
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

class ExternalResponseSchema(BaseModel):
    """Schema para respostas externas"""
    
    status_code: int = Field(..., ge=100, le=599, description="Código de status HTTP")
    data: Optional[Any] = Field(None, description="Dados da resposta")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Headers da resposta")
    response_time: Optional[float] = Field(None, ge=0, description="Tempo de resposta em segundos")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da resposta")
    
    @validator('data')
    def validate_data(cls, v):
        """Valida dados da resposta"""
        if v is not None:
            # Verifica se dados não contêm conteúdo malicioso
            if isinstance(v, str):
                # Remove possíveis scripts
                sanitized = re.sub(r'<script[^>]*>.*?</script>', '', v, flags=re.IGNORECASE)
                return sanitized
        return v

class ExternalConfigSchema(BaseModel):
    """Schema para configuração de APIs externas"""
    
    base_url: HttpUrl = Field(..., description="URL base da API externa")
    api_key: Optional[str] = Field(None, min_length=1, max_length=1000, description="Chave da API")
    timeout: int = Field(default=30, ge=1, le=300, description="Timeout padrão em segundos")
    max_retries: int = Field(default=3, ge=0, le=10, description="Máximo de tentativas")
    rate_limit: Optional[int] = Field(None, ge=1, description="Limite de requisições por minuto")
    allowed_endpoints: Optional[List[str]] = Field(None, description="Endpoints permitidos")
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Valida chave da API"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>"\']', '', v.strip())
            return sanitized
        return v
    
    @validator('allowed_endpoints')
    def validate_allowed_endpoints(cls, v):
        """Valida lista de endpoints permitidos"""
        if v:
            sanitized = []
            for endpoint in v:
                clean_endpoint = re.sub(r'[<>"\']', '', str(endpoint).strip())
                if clean_endpoint and re.match(r'^[a-zA-Z0-9/._-]+$', clean_endpoint):
                    sanitized.append(clean_endpoint)
            return sanitized
        return v

class ExternalFilterSchema(BaseModel):
    """Schema para filtros de consumo externo"""
    
    endpoint: Optional[str] = Field(None, description="Filtrar por endpoint")
    method: Optional[str] = Field(None, description="Filtrar por método HTTP")
    status_code: Optional[int] = Field(None, ge=100, le=599, description="Filtrar por status code")
    min_response_time: Optional[float] = Field(None, ge=0, description="Tempo mínimo de resposta")
    max_response_time: Optional[float] = Field(None, ge=0, description="Tempo máximo de resposta")
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Limite de resultados")
    offset: Optional[int] = Field(None, ge=0, description="Offset para paginação")
    
    @validator('method')
    def validate_method(cls, v):
        """Valida método HTTP"""
        if v:
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
            if v.upper() not in valid_methods:
                raise ValueError(f'Método HTTP inválido. Válidos: {", ".join(valid_methods)}')
        return v.upper() if v else v
    
    @root_validator
    def validate_response_time_range(cls, values):
        """Valida range de tempo de resposta"""
        min_time = values.get('min_response_time')
        max_time = values.get('max_response_time')
        
        if min_time and max_time and min_time > max_time:
            raise ValueError('Tempo mínimo não pode ser maior que tempo máximo')
        
        return values
    
    @root_validator
    def validate_date_range(cls, values):
        """Valida range de datas"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError('Data inicial não pode ser posterior à data final')
        
        return values

class ExternalMetricsSchema(BaseModel):
    """Schema para métricas de consumo externo"""
    
    total_requests: int = Field(..., ge=0, description="Total de requisições")
    successful_requests: int = Field(..., ge=0, description="Requisições bem-sucedidas")
    failed_requests: int = Field(..., ge=0, description="Requisições falhadas")
    avg_response_time: float = Field(..., ge=0, description="Tempo médio de resposta")
    max_response_time: float = Field(..., ge=0, description="Tempo máximo de resposta")
    min_response_time: float = Field(..., ge=0, description="Tempo mínimo de resposta")
    error_rate: float = Field(..., ge=0, le=1, description="Taxa de erro")
    last_request: Optional[datetime] = Field(None, description="Última requisição")
    
    @root_validator
    def validate_metrics_consistency(cls, values):
        """Valida consistência das métricas"""
        total = values.get('total_requests', 0)
        successful = values.get('successful_requests', 0)
        failed = values.get('failed_requests', 0)
        
        if total != successful + failed:
            raise ValueError('Total de requisições deve ser igual à soma de sucessos e falhas')
        
        return values

class ExternalHealthSchema(BaseModel):
    """Schema para health check de APIs externas"""
    
    endpoint: str = Field(..., description="Endpoint testado")
    status: str = Field(..., description="Status da API")
    response_time: float = Field(..., ge=0, description="Tempo de resposta")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Última verificação")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    @validator('status')
    def validate_status(cls, v):
        """Valida status da API"""
        valid_statuses = ['healthy', 'unhealthy', 'degraded', 'unknown']
        if v not in valid_statuses:
            raise ValueError(f'Status inválido. Válidos: {", ".join(valid_statuses)}')
        return v
    
    @validator('error_message')
    def validate_error_message(cls, v):
        """Sanitiza mensagem de erro"""
        if v:
            return re.sub(r'[<>"\']', '', v)
        return v 