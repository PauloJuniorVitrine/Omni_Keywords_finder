"""
Schemas de Validação para Pagamentos V1 - Omni Keywords Finder
Validação robusta e estrutura de dados para sistema de pagamentos V1
Prompt: Melhoria do sistema de pagamentos V1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
import uuid

class PaymentMethod(Enum):
    """Métodos de pagamento suportados"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BOLETO = "boleto"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"

class PaymentStatus(Enum):
    """Status de pagamento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class Currency(Enum):
    """Moedas suportadas"""
    BRL = "BRL"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class PaymentRequest(BaseModel):
    """Schema para requisição de pagamento"""
    
    # Identificação
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único do pagamento")
    reference_id: Optional[str] = Field(None, description="ID de referência externa")
    
    # Valores
    amount: float = Field(..., gt=0, description="Valor do pagamento")
    currency: str = Field(default="BRL", description="Moeda do pagamento")
    
    # Método de pagamento
    payment_method: str = Field(..., description="Método de pagamento")
    
    # Dados do cliente
    customer: Dict[str, Any] = Field(..., description="Dados do cliente")
    
    # Dados específicos do método
    payment_data: Optional[Dict[str, Any]] = Field(None, description="Dados específicos do método de pagamento")
    
    # Metadados
    description: Optional[str] = Field(None, description="Descrição do pagamento")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados adicionais")
    
    # Configurações
    capture_method: str = Field(default="automatic", description="Método de captura")
    confirmation_method: str = Field(default="automatic", description="Método de confirmação")
    setup_future_usage: Optional[str] = Field(None, description="Configuração para uso futuro")
    
    # Validação e segurança
    idempotency_key: Optional[str] = Field(None, description="Chave de idempotência")
    application_fee_amount: Optional[int] = Field(None, description="Taxa da aplicação")
    
    @validator('currency')
    def validate_currency(cls, v):
        """Valida moeda"""
        valid_currencies = [currency.value for currency in Currency]
        if v not in valid_currencies:
            raise ValueError(f'Moeda não suportada. Válidas: {", ".join(valid_currencies)}')
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        """Valida método de pagamento"""
        valid_methods = [method.value for method in PaymentMethod]
        if v not in valid_methods:
            raise ValueError(f'Método de pagamento não suportado. Válidos: {", ".join(valid_methods)}')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        """Valida valor do pagamento"""
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        if v > 1000000:  # Limite de 1 milhão
            raise ValueError('Valor excede o limite máximo permitido')
        return round(v, 2)
    
    @validator('description')
    def validate_description(cls, v):
        """Sanitiza descrição"""
        if v:
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            return sanitized[:500]  # Limite de 500 caracteres
        return v
    
    @validator('customer')
    def validate_customer(cls, v):
        """Valida dados do cliente"""
        if not isinstance(v, dict):
            raise ValueError('Dados do cliente devem ser um objeto')
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Campo obrigatório ausente: {field}')
        
        # Validar email
        email = v.get('email', '')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Email inválido')
        
        # Sanitizar dados
        sanitized_customer = {}
        for key, value in v.items():
            if isinstance(value, str):
                sanitized_customer[key] = re.sub(r'[<>"\']', '', value.strip())
            else:
                sanitized_customer[key] = value
        
        return sanitized_customer
    
    @validator('payment_data')
    def validate_payment_data(cls, v, values):
        """Valida dados específicos do método de pagamento"""
        if v is None:
            return v
        
        payment_method = values.get('payment_method')
        
        if payment_method == PaymentMethod.CREDIT_CARD.value:
            required_fields = ['card_number', 'exp_month', 'exp_year', 'cvc']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Campo obrigatório para cartão: {field}')
            
            # Validar número do cartão (Luhn algorithm)
            card_number = str(v.get('card_number', '')).replace(' ', '')
            if not cls._validate_luhn(card_number):
                raise ValueError('Número do cartão inválido')
            
            # Validar data de expiração
            exp_month = v.get('exp_month')
            exp_year = v.get('exp_year')
            if not cls._validate_expiry(exp_month, exp_year):
                raise ValueError('Data de expiração inválida')
            
            # Validar CVC
            cvc = str(v.get('cvc', ''))
            if not re.match(r'^\d{3,4}$', cvc):
                raise ValueError('CVC inválido')
        
        elif payment_method == PaymentMethod.PIX.value:
            if 'pix_key' not in v:
                raise ValueError('Chave PIX obrigatória')
        
        elif payment_method == PaymentMethod.BOLETO.value:
            if 'cpf_cnpj' not in v:
                raise ValueError('CPF/CNPJ obrigatório para boleto')
        
        return v
    
    @staticmethod
    def _validate_luhn(card_number: str) -> bool:
        """Valida número do cartão usando algoritmo de Luhn"""
        if not card_number.isdigit():
            return False
        
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        
        return checksum % 10 == 0
    
    @staticmethod
    def _validate_expiry(exp_month: int, exp_year: int) -> bool:
        """Valida data de expiração"""
        try:
            exp_month = int(exp_month)
            exp_year = int(exp_year)
            
            if not (1 <= exp_month <= 12):
                return False
            
            current_year = datetime.now().year
            if exp_year < current_year:
                return False
            
            return True
        except (ValueError, TypeError):
            return False

class PaymentResponse(BaseModel):
    """Schema para resposta de pagamento"""
    
    # Identificação
    payment_id: str = Field(..., description="ID do pagamento")
    reference_id: Optional[str] = Field(None, description="ID de referência")
    
    # Status
    status: str = Field(..., description="Status do pagamento")
    status_code: str = Field(..., description="Código de status")
    
    # Valores
    amount: float = Field(..., description="Valor do pagamento")
    currency: str = Field(..., description="Moeda")
    amount_received: float = Field(..., description="Valor recebido")
    
    # Método
    payment_method: str = Field(..., description="Método de pagamento")
    
    # Dados do cliente
    customer: Dict[str, Any] = Field(..., description="Dados do cliente")
    
    # Timestamps
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Dados específicos
    payment_intent_id: Optional[str] = Field(None, description="ID do PaymentIntent")
    charge_id: Optional[str] = Field(None, description="ID da cobrança")
    
    # URLs e dados adicionais
    confirmation_url: Optional[str] = Field(None, description="URL de confirmação")
    cancel_url: Optional[str] = Field(None, description="URL de cancelamento")
    
    # Metadados
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    # Erros
    error_code: Optional[str] = Field(None, description="Código de erro")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    @validator('status')
    def validate_status(cls, v):
        """Valida status"""
        valid_statuses = [status.value for status in PaymentStatus]
        if v not in valid_statuses:
            raise ValueError(f'Status inválido. Válidos: {", ".join(valid_statuses)}')
        return v

class PaymentRefundRequest(BaseModel):
    """Schema para requisição de reembolso"""
    
    # Identificação
    payment_id: str = Field(..., description="ID do pagamento a reembolsar")
    refund_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID do reembolso")
    
    # Valores
    amount: Optional[float] = Field(None, description="Valor do reembolso (total se não especificado)")
    reason: Optional[str] = Field(None, description="Motivo do reembolso")
    
    # Metadados
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Valida valor do reembolso"""
        if v is not None and v <= 0:
            raise ValueError('Valor do reembolso deve ser maior que zero')
        return v
    
    @validator('reason')
    def validate_reason(cls, v):
        """Sanitiza motivo"""
        if v:
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            return sanitized[:200]  # Limite de 200 caracteres
        return v

class PaymentWebhookData(BaseModel):
    """Schema para dados de webhook de pagamento"""
    
    # Identificação
    event_id: str = Field(..., description="ID do evento")
    event_type: str = Field(..., description="Tipo do evento")
    
    # Dados do pagamento
    payment_id: str = Field(..., description="ID do pagamento")
    payment_intent_id: Optional[str] = Field(None, description="ID do PaymentIntent")
    
    # Status
    status: str = Field(..., description="Status do pagamento")
    
    # Valores
    amount: float = Field(..., description="Valor do pagamento")
    currency: str = Field(..., description="Moeda")
    
    # Timestamps
    created_at: datetime = Field(..., description="Data de criação")
    processed_at: datetime = Field(..., description="Data de processamento")
    
    # Dados adicionais
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        """Valida tipo de evento"""
        valid_types = [
            'payment_intent.succeeded',
            'payment_intent.payment_failed',
            'payment_intent.canceled',
            'charge.succeeded',
            'charge.failed',
            'charge.refunded'
        ]
        if v not in valid_types:
            raise ValueError(f'Tipo de evento não suportado. Válidos: {", ".join(valid_types)}')
        return v

class PaymentListRequest(BaseModel):
    """Schema para listagem de pagamentos"""
    
    # Filtros
    customer_id: Optional[str] = Field(None, description="ID do cliente")
    status: Optional[str] = Field(None, description="Status do pagamento")
    payment_method: Optional[str] = Field(None, description="Método de pagamento")
    
    # Paginação
    limit: Optional[int] = Field(None, ge=1, le=100, description="Limite de resultados")
    offset: Optional[int] = Field(None, ge=0, description="Offset para paginação")
    
    # Ordenação
    sort_by: Optional[str] = Field(default="created_at", description="Campo para ordenação")
    sort_order: Optional[str] = Field(default="desc", description="Ordem de classificação")
    
    # Filtros de tempo
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    
    @validator('status')
    def validate_status(cls, v):
        """Valida status"""
        if v:
            valid_statuses = [status.value for status in PaymentStatus]
            if v not in valid_statuses:
                raise ValueError(f'Status inválido. Válidos: {", ".join(valid_statuses)}')
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        """Valida método de pagamento"""
        if v:
            valid_methods = [method.value for method in PaymentMethod]
            if v not in valid_methods:
                raise ValueError(f'Método de pagamento não suportado. Válidos: {", ".join(valid_methods)}')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Valida campo de ordenação"""
        valid_fields = [
            'created_at', 'updated_at', 'amount', 'status', 
            'payment_method', 'customer_id'
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