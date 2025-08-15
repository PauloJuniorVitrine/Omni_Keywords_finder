"""
Schemas de Validação para Webhooks - Omni Keywords Finder
Validação robusta e sanitização de dados para webhooks
Prompt: Revisão de segurança de webhooks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import re
import hmac
import hashlib
import base64
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from urllib.parse import urlparse
from pydantic import BaseModel, Field, validator, root_validator, HttpUrl
from pydantic.types import IPvAnyAddress

class WebhookEndpointSchema(BaseModel):
    """Schema para validação de endpoints de webhook"""
    
    name: str = Field(..., min_length=1, max_length=100, description="Nome do webhook")
    url: HttpUrl = Field(..., description="URL do endpoint do webhook")
    events: List[str] = Field(..., min_items=1, max_items=50, description="Lista de eventos")
    secret: Optional[str] = Field(None, min_length=16, max_length=256, description="Secret para assinatura HMAC")
    api_key: Optional[str] = Field(None, min_length=1, max_length=256, description="API key para autenticação")
    security_level: str = Field(default="hmac", description="Nível de segurança")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Headers customizados")
    timeout: int = Field(default=30, ge=5, le=300, description="Timeout em segundos")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Número de tentativas")
    retry_delay: int = Field(default=5, ge=1, le=3600, description="Delay entre tentativas em segundos")
    rate_limit: int = Field(default=100, ge=1, le=10000, description="Limite de requisições por hora")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados customizados")
    
    @validator('name')
    def validate_name(cls, v):
        """Valida e sanitiza nome do webhook"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', v.strip())
        
        # Valida formato básico
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', sanitized):
            raise ValueError('Nome contém caracteres inválidos')
        
        return sanitized
    
    @validator('url')
    def validate_url(cls, v):
        """Valida URL do webhook"""
        url_str = str(v)
        
        # Verificar se é HTTPS (recomendado para webhooks)
        if not url_str.startswith('https://'):
            raise ValueError('URL deve usar HTTPS para segurança')
        
        # Verificar se não é localhost em produção
        parsed = urlparse(url_str)
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            raise ValueError('URL não pode apontar para localhost')
        
        return v
    
    @validator('events')
    def validate_events(cls, v):
        """Valida lista de eventos"""
        valid_events = [
            'user.created', 'user.updated', 'user.deleted',
            'payment.created', 'payment.succeeded', 'payment.failed',
            'subscription.created', 'subscription.updated', 'subscription.cancelled',
            'execution.started', 'execution.completed', 'execution.failed',
            'keyword.found', 'keyword.analyzed', 'keyword.exported'
        ]
        
        sanitized_events = []
        for event in v:
            # Sanitiza evento
            clean_event = re.sub(r'[<>"\']', '', str(event).strip())
            
            # Valida formato
            if not re.match(r'^[a-z]+\.[a-z_]+$', clean_event):
                raise ValueError(f'Formato de evento inválido: {event}')
            
            # Verifica se é válido
            if clean_event not in valid_events:
                raise ValueError(f'Evento não suportado: {event}')
            
            sanitized_events.append(clean_event)
        
        return sanitized_events
    
    @validator('secret')
    def validate_secret(cls, v):
        """Valida secret para HMAC"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>"\']', '', v.strip())
            
            # Verifica se tem comprimento mínimo
            if len(sanitized) < 16:
                raise ValueError('Secret deve ter pelo menos 16 caracteres')
            
            return sanitized
        return v
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Valida API key"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>"\']', '', v.strip())
            return sanitized
        return v
    
    @validator('security_level')
    def validate_security_level(cls, v):
        """Valida nível de segurança"""
        valid_levels = ['none', 'hmac', 'api_key', 'both']
        if v not in valid_levels:
            raise ValueError(f'Nível de segurança inválido. Válidos: {", ".join(valid_levels)}')
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
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Valida metadados"""
        if v:
            # Remove caracteres perigosos de strings nos metadados
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

class WebhookPayloadSchema(BaseModel):
    """Schema para validação de payloads de webhook"""
    
    event: str = Field(..., description="Tipo do evento")
    data: Dict[str, Any] = Field(..., description="Dados do evento")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do evento")
    id: str = Field(..., description="ID único do evento")
    source: Optional[str] = Field(None, description="Origem do evento")
    version: str = Field(default="1.0", description="Versão do payload")
    
    @validator('event')
    def validate_event(cls, v):
        """Valida tipo do evento"""
        valid_events = [
            'user.created', 'user.updated', 'user.deleted',
            'payment.created', 'payment.succeeded', 'payment.failed',
            'subscription.created', 'subscription.updated', 'subscription.cancelled',
            'execution.started', 'execution.completed', 'execution.failed',
            'keyword.found', 'keyword.analyzed', 'keyword.exported'
        ]
        
        clean_event = re.sub(r'[<>"\']', '', str(v).strip())
        if clean_event not in valid_events:
            raise ValueError(f'Evento não suportado: {v}')
        
        return clean_event
    
    @validator('data')
    def validate_data(cls, v):
        """Valida dados do evento"""
        if v:
            # Remove caracteres perigosos de strings nos dados
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
    
    @validator('id')
    def validate_id(cls, v):
        """Valida ID do evento"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        
        # Valida formato UUID
        if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', sanitized):
            raise ValueError('ID deve ser um UUID válido')
        
        return sanitized
    
    @validator('source')
    def validate_source(cls, v):
        """Valida origem do evento"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            return sanitized
        return v

class WebhookSignatureSchema(BaseModel):
    """Schema para validação de assinaturas HMAC"""
    
    signature: str = Field(..., description="Assinatura HMAC")
    timestamp: str = Field(..., description="Timestamp da requisição")
    payload: str = Field(..., description="Payload original")
    secret: str = Field(..., description="Secret para validação")
    
    @validator('signature')
    def validate_signature(cls, v):
        """Valida formato da assinatura"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        
        # Verifica se é base64 válido
        try:
            base64.b64decode(sanitized)
        except Exception:
            raise ValueError('Assinatura deve ser base64 válido')
        
        return sanitized
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Valida timestamp"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        
        # Verifica se é número
        try:
            int(sanitized)
        except ValueError:
            raise ValueError('Timestamp deve ser um número válido')
        
        return sanitized
    
    @validator('payload')
    def validate_payload(cls, v):
        """Valida payload"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        return sanitized
    
    @validator('secret')
    def validate_secret(cls, v):
        """Valida secret"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        
        # Verifica comprimento mínimo
        if len(sanitized) < 16:
            raise ValueError('Secret deve ter pelo menos 16 caracteres')
        
        return sanitized

class WebhookDeliverySchema(BaseModel):
    """Schema para validação de entregas de webhook"""
    
    endpoint_id: str = Field(..., description="ID do endpoint")
    event_id: str = Field(..., description="ID do evento")
    payload: Dict[str, Any] = Field(..., description="Payload enviado")
    response_status: int = Field(..., ge=100, le=599, description="Status da resposta")
    response_time: float = Field(..., ge=0, description="Tempo de resposta em segundos")
    attempt_count: int = Field(..., ge=0, le=10, description="Número de tentativas")
    max_attempts: int = Field(..., ge=1, le=10, description="Máximo de tentativas")
    status: str = Field(..., description="Status da entrega")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação")
    
    @validator('endpoint_id')
    def validate_endpoint_id(cls, v):
        """Valida ID do endpoint"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        
        # Valida formato UUID
        if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', sanitized):
            raise ValueError('Endpoint ID deve ser um UUID válido')
        
        return sanitized
    
    @validator('event_id')
    def validate_event_id(cls, v):
        """Valida ID do evento"""
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        
        # Valida formato UUID
        if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', sanitized):
            raise ValueError('Event ID deve ser um UUID válido')
        
        return sanitized
    
    @validator('payload')
    def validate_payload(cls, v):
        """Valida payload"""
        if v:
            # Remove caracteres perigosos de strings no payload
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
    
    @validator('status')
    def validate_status(cls, v):
        """Valida status da entrega"""
        valid_statuses = ['pending', 'delivered', 'failed', 'retrying']
        if v not in valid_statuses:
            raise ValueError(f'Status inválido. Válidos: {", ".join(valid_statuses)}')
        return v
    
    @validator('error_message')
    def validate_error_message(cls, v):
        """Sanitiza mensagem de erro"""
        if v:
            return re.sub(r'[<>"\']', '', v)
        return v

class WebhookFilterSchema(BaseModel):
    """Schema para filtros de webhook"""
    
    endpoint_id: Optional[str] = Field(None, description="Filtrar por endpoint")
    event_type: Optional[str] = Field(None, description="Filtrar por tipo de evento")
    status: Optional[str] = Field(None, description="Filtrar por status")
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Limite de resultados")
    offset: Optional[int] = Field(None, ge=0, description="Offset para paginação")
    
    @validator('endpoint_id')
    def validate_endpoint_id(cls, v):
        """Valida ID do endpoint"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            
            # Valida formato UUID
            if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', sanitized):
                raise ValueError('Endpoint ID deve ser um UUID válido')
            
            return sanitized
        return v
    
    @validator('event_type')
    def validate_event_type(cls, v):
        """Valida tipo de evento"""
        if v:
            valid_events = [
                'user.created', 'user.updated', 'user.deleted',
                'payment.created', 'payment.succeeded', 'payment.failed',
                'subscription.created', 'subscription.updated', 'subscription.cancelled',
                'execution.started', 'execution.completed', 'execution.failed',
                'keyword.found', 'keyword.analyzed', 'keyword.exported'
            ]
            
            clean_event = re.sub(r'[<>"\']', '', str(v).strip())
            if clean_event not in valid_events:
                raise ValueError(f'Evento não suportado: {v}')
            
            return clean_event
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Valida status"""
        if v:
            valid_statuses = ['pending', 'delivered', 'failed', 'retrying']
            if v not in valid_statuses:
                raise ValueError(f'Status inválido. Válidos: {", ".join(valid_statuses)}')
        return v
    
    @root_validator
    def validate_date_range(cls, values):
        """Valida range de datas"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError('Data inicial não pode ser posterior à data final')
        
        return values

class WebhookHMACValidator:
    """Classe para validação de assinaturas HMAC"""
    
    @staticmethod
    def generate_signature(payload: str, secret: str, timestamp: str = None) -> str:
        """
        Gera assinatura HMAC para payload
        
        Args:
            payload: Payload em string
            secret: Secret para assinatura
            timestamp: Timestamp (opcional)
            
        Returns:
            Assinatura HMAC em base64
        """
        if timestamp is None:
            timestamp = str(int(datetime.utcnow().timestamp()))
        
        # Criar mensagem para assinatura
        message = f"{timestamp}.{payload}"
        
        # Gerar assinatura HMAC-SHA256
        signature = hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Retornar em base64
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def validate_signature(payload: str, signature: str, secret: str, timestamp: str, tolerance: int = 300) -> bool:
        """
        Valida assinatura HMAC
        
        Args:
            payload: Payload recebido
            signature: Assinatura recebida
            secret: Secret para validação
            timestamp: Timestamp da requisição
            tolerance: Tolerância em segundos para timestamp
            
        Returns:
            True se assinatura for válida
        """
        try:
            # Validar timestamp
            request_time = int(timestamp)
            current_time = int(datetime.utcnow().timestamp())
            
            if abs(current_time - request_time) > tolerance:
                return False
            
            # Gerar assinatura esperada
            expected_signature = WebhookHMACValidator.generate_signature(payload, secret, timestamp)
            
            # Comparar assinaturas (timing-safe)
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False 