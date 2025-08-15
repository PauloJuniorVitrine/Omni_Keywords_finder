"""
Schemas de Validação para Pagamentos - Omni Keywords Finder
Validação robusta de dados de pagamento com Pydantic
Prompt: Validação robusta de pagamentos
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import PaymentCardNumber, EmailStr

class PaymentCardSchema(BaseModel):
    """Schema para validação de cartão de crédito"""
    
    number: PaymentCardNumber = Field(..., description="Número do cartão")
    exp_month: int = Field(..., ge=1, le=12, description="Mês de expiração (1-12)")
    exp_year: int = Field(..., ge=2025, le=2035, description="Ano de expiração")
    cvc: str = Field(..., min_length=3, max_length=4, description="Código de segurança")
    name: str = Field(..., min_length=2, max_length=100, description="Nome no cartão")
    
    @validator('cvc')
    def validate_cvc(cls, v):
        """Valida se CVC contém apenas números"""
        if not v.isdigit():
            raise ValueError('CVC deve conter apenas números')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Sanitiza e valida nome no cartão"""
        # Remove caracteres especiais perigosos
        sanitized = re.sub(r'[<>"\']', '', v.strip())
        if len(sanitized) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return sanitized.title()
    
    @root_validator
    def validate_expiration(cls, values):
        """Valida se cartão não está expirado"""
        exp_month = values.get('exp_month')
        exp_year = values.get('exp_year')
        
        if exp_month and exp_year:
            current_date = datetime.now()
            if exp_year < current_date.year or (exp_year == current_date.year and exp_month < current_date.month):
                raise ValueError('Cartão expirado')
        
        return values

class PixSchema(BaseModel):
    """Schema para validação de PIX"""
    
    key_type: str = Field(..., description="Tipo da chave PIX")
    key_value: str = Field(..., description="Valor da chave PIX")
    
    @validator('key_type')
    def validate_key_type(cls, v):
        """Valida tipo de chave PIX"""
        valid_types = ['cpf', 'cnpj', 'email', 'phone', 'random']
        if v not in valid_types:
            raise ValueError(f'Tipo de chave PIX inválido. Válidos: {", ".join(valid_types)}')
        return v
    
    @validator('key_value')
    def validate_key_value(cls, v, values):
        """Valida valor da chave PIX baseado no tipo"""
        key_type = values.get('key_type')
        
        if key_type == 'cpf':
            if not re.match(r'^\d{11}$', v):
                raise ValueError('CPF deve ter 11 dígitos')
        elif key_type == 'cnpj':
            if not re.match(r'^\d{14}$', v):
                raise ValueError('CNPJ deve ter 14 dígitos')
        elif key_type == 'email':
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError('Email inválido')
        elif key_type == 'phone':
            if not re.match(r'^\+55\d{10,11}$', v):
                raise ValueError('Telefone deve estar no formato +55XXXXXXXXXXX')
        elif key_type == 'random':
            if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', v):
                raise ValueError('Chave aleatória deve ser um UUID válido')
        
        return v

class BoletoSchema(BaseModel):
    """Schema para validação de boleto"""
    
    customer_name: str = Field(..., min_length=2, max_length=100, description="Nome do cliente")
    customer_document: str = Field(..., description="CPF/CNPJ do cliente")
    customer_email: EmailStr = Field(..., description="Email do cliente")
    due_date: datetime = Field(..., description="Data de vencimento")
    
    @validator('customer_name')
    def validate_customer_name(cls, v):
        """Sanitiza e valida nome do cliente"""
        sanitized = re.sub(r'[<>"\']', '', v.strip())
        if len(sanitized) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return sanitized.title()
    
    @validator('customer_document')
    def validate_customer_document(cls, v):
        """Valida CPF ou CNPJ"""
        # Remove caracteres não numéricos
        clean_doc = re.sub(r'\D', '', v)
        
        if len(clean_doc) == 11:
            # Validação básica de CPF
            if not re.match(r'^\d{11}$', clean_doc):
                raise ValueError('CPF inválido')
        elif len(clean_doc) == 14:
            # Validação básica de CNPJ
            if not re.match(r'^\d{14}$', clean_doc):
                raise ValueError('CNPJ inválido')
        else:
            raise ValueError('Documento deve ser CPF (11 dígitos) ou CNPJ (14 dígitos)')
        
        return clean_doc
    
    @validator('due_date')
    def validate_due_date(cls, v):
        """Valida se data de vencimento é futura"""
        if v <= datetime.now():
            raise ValueError('Data de vencimento deve ser futura')
        return v

class PaymentMethodSchema(BaseModel):
    """Schema para método de pagamento"""
    
    type: str = Field(..., description="Tipo de método de pagamento")
    card: Optional[PaymentCardSchema] = Field(None, description="Dados do cartão")
    pix: Optional[PixSchema] = Field(None, description="Dados do PIX")
    boleto: Optional[BoletoSchema] = Field(None, description="Dados do boleto")
    
    @validator('type')
    def validate_type(cls, v):
        """Valida tipo de método de pagamento"""
        valid_types = ['card', 'pix', 'boleto']
        if v not in valid_types:
            raise ValueError(f'Tipo de pagamento inválido. Válidos: {", ".join(valid_types)}')
        return v
    
    @root_validator
    def validate_method_data(cls, values):
        """Valida se dados específicos do método estão presentes"""
        payment_type = values.get('type')
        
        if payment_type == 'card' and not values.get('card'):
            raise ValueError('Dados do cartão são obrigatórios para pagamento com cartão')
        elif payment_type == 'pix' and not values.get('pix'):
            raise ValueError('Dados do PIX são obrigatórios para pagamento PIX')
        elif payment_type == 'boleto' and not values.get('boleto'):
            raise ValueError('Dados do boleto são obrigatórios para pagamento com boleto')
        
        return values

class PaymentCreateSchema(BaseModel):
    """Schema para criação de pagamento"""
    
    amount: int = Field(..., ge=100, le=99999999, description="Valor em centavos")
    currency: str = Field(default="brl", description="Moeda")
    payment_method: PaymentMethodSchema = Field(..., description="Método de pagamento")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do pagamento")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados")
    
    @validator('currency')
    def validate_currency(cls, v):
        """Valida moeda suportada"""
        supported_currencies = ['brl', 'usd', 'eur']
        if v not in supported_currencies:
            raise ValueError(f'Moeda não suportada. Suportadas: {", ".join(supported_currencies)}')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Sanitiza descrição"""
        if v:
            # Remove caracteres perigosos
            sanitized = re.sub(r'[<>"\']', '', v.strip())
            return sanitized
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Valida metadados"""
        if v:
            # Remove chaves com caracteres perigosos
            sanitized = {}
            for key, value in v.items():
                clean_key = re.sub(r'[<>"\']', '', str(key))
                if clean_key:
                    sanitized[clean_key] = value
            return sanitized
        return v

class PaymentUpdateSchema(BaseModel):
    """Schema para atualização de pagamento"""
    
    description: Optional[str] = Field(None, max_length=500, description="Descrição do pagamento")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados")
    
    @validator('description')
    def validate_description(cls, v):
        """Sanitiza descrição"""
        if v:
            sanitized = re.sub(r'[<>"\']', '', v.strip())
            return sanitized
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Valida metadados"""
        if v:
            sanitized = {}
            for key, value in v.items():
                clean_key = re.sub(r'[<>"\']', '', str(key))
                if clean_key:
                    sanitized[clean_key] = value
            return sanitized
        return v

class PaymentFilterSchema(BaseModel):
    """Schema para filtros de pagamento"""
    
    status: Optional[str] = Field(None, description="Status do pagamento")
    payment_method: Optional[str] = Field(None, description="Método de pagamento")
    min_amount: Optional[int] = Field(None, ge=0, description="Valor mínimo")
    max_amount: Optional[int] = Field(None, ge=0, description="Valor máximo")
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    limit: Optional[int] = Field(None, ge=1, le=100, description="Limite de resultados")
    offset: Optional[int] = Field(None, ge=0, description="Offset para paginação")
    
    @validator('status')
    def validate_status(cls, v):
        """Valida status do pagamento"""
        if v:
            valid_statuses = ['pending', 'processing', 'succeeded', 'failed', 'canceled']
            if v not in valid_statuses:
                raise ValueError(f'Status inválido. Válidos: {", ".join(valid_statuses)}')
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        """Valida método de pagamento"""
        if v:
            valid_methods = ['card', 'pix', 'boleto']
            if v not in valid_methods:
                raise ValueError(f'Método inválido. Válidos: {", ".join(valid_methods)}')
        return v
    
    @root_validator
    def validate_amount_range(cls, values):
        """Valida range de valores"""
        min_amount = values.get('min_amount')
        max_amount = values.get('max_amount')
        
        if min_amount and max_amount and min_amount > max_amount:
            raise ValueError('Valor mínimo não pode ser maior que valor máximo')
        
        return values
    
    @root_validator
    def validate_date_range(cls, values):
        """Valida range de datas"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError('Data inicial não pode ser posterior à data final')
        
        return values

class PaymentResponseSchema(BaseModel):
    """Schema para resposta de pagamento"""
    
    id: str = Field(..., description="ID do pagamento")
    amount: int = Field(..., description="Valor em centavos")
    currency: str = Field(..., description="Moeda")
    status: str = Field(..., description="Status do pagamento")
    payment_method: str = Field(..., description="Método de pagamento")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    description: Optional[str] = Field(None, description="Descrição")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 