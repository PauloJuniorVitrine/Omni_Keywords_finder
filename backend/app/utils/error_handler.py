"""
Sistema Centralizado de Tratamento de Erros - Omni Keywords Finder
Padronização de respostas de erro, códigos HTTP e mensagens consistentes
Prompt: Tratamento de Erro - Padronização
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from dataclasses import dataclass, asdict
from flask import jsonify, request, current_app
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

# Logger
logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """Códigos de erro padronizados"""
    # Erros de validação (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_VALUE = "INVALID_VALUE"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    
    # Erros de autenticação (401/403)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Erros de recurso (404)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    ENDPOINT_NOT_FOUND = "ENDPOINT_NOT_FOUND"
    
    # Erros de conflito (409)
    CONFLICT = "CONFLICT"
    RESOURCE_EXISTS = "RESOURCE_EXISTS"
    STATE_CONFLICT = "STATE_CONFLICT"
    
    # Erros de rate limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    
    # Erros internos (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    
    # Erros de gateway (502/503/504)
    BAD_GATEWAY = "BAD_GATEWAY"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"

class ErrorSeverity(Enum):
    """Níveis de severidade de erro"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorDetail:
    """Detalhes específicos de um erro"""
    field: Optional[str] = None
    value: Optional[Any] = None
    message: Optional[str] = None
    suggestion: Optional[str] = None

@dataclass
class ErrorResponse:
    """Resposta de erro padronizada"""
    success: bool = False
    error_code: str = ErrorCode.INTERNAL_ERROR.value
    message: str = "Erro interno do servidor"
    details: Optional[Dict[str, Any]] = None
    timestamp: str = None
    request_id: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)
    
    def to_json_response(self, status_code: int = 500) -> tuple:
        """Converte para resposta JSON do Flask"""
        return jsonify(self.to_dict()), status_code

class ErrorHandler:
    """Sistema centralizado de tratamento de erros"""
    
    def __init__(self):
        self.error_mappings = self._setup_error_mappings()
    
    def _setup_error_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Configura mapeamentos de erro"""
        return {
            ErrorCode.VALIDATION_ERROR.value: {
                "status_code": 400,
                "message": "Dados de entrada inválidos",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.MISSING_REQUIRED_FIELD.value: {
                "status_code": 400,
                "message": "Campo obrigatório ausente",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.INVALID_FORMAT.value: {
                "status_code": 400,
                "message": "Formato de dados inválido",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.INVALID_VALUE.value: {
                "status_code": 400,
                "message": "Valor inválido fornecido",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.DUPLICATE_ENTRY.value: {
                "status_code": 409,
                "message": "Registro duplicado",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.UNAUTHORIZED.value: {
                "status_code": 401,
                "message": "Não autorizado",
                "severity": ErrorSeverity.HIGH
            },
            ErrorCode.FORBIDDEN.value: {
                "status_code": 403,
                "message": "Acesso negado",
                "severity": ErrorSeverity.HIGH
            },
            ErrorCode.INVALID_CREDENTIALS.value: {
                "status_code": 401,
                "message": "Credenciais inválidas",
                "severity": ErrorSeverity.HIGH
            },
            ErrorCode.TOKEN_EXPIRED.value: {
                "status_code": 401,
                "message": "Token expirado",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.INSUFFICIENT_PERMISSIONS.value: {
                "status_code": 403,
                "message": "Permissões insuficientes",
                "severity": ErrorSeverity.HIGH
            },
            ErrorCode.RESOURCE_NOT_FOUND.value: {
                "status_code": 404,
                "message": "Recurso não encontrado",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.USER_NOT_FOUND.value: {
                "status_code": 404,
                "message": "Usuário não encontrado",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.FILE_NOT_FOUND.value: {
                "status_code": 404,
                "message": "Arquivo não encontrado",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.ENDPOINT_NOT_FOUND.value: {
                "status_code": 404,
                "message": "Endpoint não encontrado",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.CONFLICT.value: {
                "status_code": 409,
                "message": "Conflito de recursos",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.RESOURCE_EXISTS.value: {
                "status_code": 409,
                "message": "Recurso já existe",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.STATE_CONFLICT.value: {
                "status_code": 409,
                "message": "Conflito de estado",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.RATE_LIMIT_EXCEEDED.value: {
                "status_code": 429,
                "message": "Limite de taxa excedido",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.TOO_MANY_REQUESTS.value: {
                "status_code": 429,
                "message": "Muitas requisições",
                "severity": ErrorSeverity.MEDIUM
            },
            ErrorCode.INTERNAL_ERROR.value: {
                "status_code": 500,
                "message": "Erro interno do servidor",
                "severity": ErrorSeverity.CRITICAL
            },
            ErrorCode.DATABASE_ERROR.value: {
                "status_code": 500,
                "message": "Erro de banco de dados",
                "severity": ErrorSeverity.CRITICAL
            },
            ErrorCode.EXTERNAL_SERVICE_ERROR.value: {
                "status_code": 502,
                "message": "Erro de serviço externo",
                "severity": ErrorSeverity.HIGH
            },
            ErrorCode.CONFIGURATION_ERROR.value: {
                "status_code": 500,
                "message": "Erro de configuração",
                "severity": ErrorSeverity.CRITICAL
            },
            ErrorCode.BAD_GATEWAY.value: {
                "status_code": 502,
                "message": "Gateway inválido",
                "severity": ErrorSeverity.HIGH
            },
            ErrorCode.SERVICE_UNAVAILABLE.value: {
                "status_code": 503,
                "message": "Serviço indisponível",
                "severity": ErrorSeverity.HIGH
            },
            ErrorCode.GATEWAY_TIMEOUT.value: {
                "status_code": 504,
                "message": "Timeout do gateway",
                "severity": ErrorSeverity.HIGH
            }
        }
    
    def create_error_response(
        self,
        error_code: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        custom_status_code: Optional[int] = None
    ) -> ErrorResponse:
        """
        Cria uma resposta de erro padronizada
        
        Args:
            error_code: Código do erro
            message: Mensagem personalizada (opcional)
            details: Detalhes adicionais (opcional)
            request_id: ID da requisição (opcional)
            custom_status_code: Código HTTP personalizado (opcional)
            
        Returns:
            ErrorResponse padronizada
        """
        # Obter configuração do erro
        error_config = self.error_mappings.get(error_code, self.error_mappings[ErrorCode.INTERNAL_ERROR.value])
        
        # Usar mensagem padrão se não fornecida
        if message is None:
            message = error_config["message"]
        
        # Criar resposta
        response = ErrorResponse(
            error_code=error_code,
            message=message,
            details=details,
            request_id=request_id,
            path=request.path if request else None,
            method=request.method if request else None
        )
        
        # Log do erro
        self._log_error(error_code, message, details, error_config["severity"])
        
        return response
    
    def handle_validation_error(self, validation_error: ValidationError) -> ErrorResponse:
        """
        Trata erros de validação do Pydantic
        
        Args:
            validation_error: Erro de validação do Pydantic
            
        Returns:
            ErrorResponse com detalhes de validação
        """
        # Processar erros de validação
        validation_details = []
        for error in validation_error.errors():
            detail = ErrorDetail(
                field='.'.join(str(x) for x in error['loc']),
                value=error.get('input'),
                message=error['msg'],
                suggestion=self._get_validation_suggestion(error['type'])
            )
            validation_details.append(asdict(detail))
        
        return self.create_error_response(
            error_code=ErrorCode.VALIDATION_ERROR.value,
            details={'validation_errors': validation_details}
        )
    
    def handle_http_exception(self, http_exception: HTTPException) -> ErrorResponse:
        """
        Trata exceções HTTP do Werkzeug
        
        Args:
            http_exception: Exceção HTTP
            
        Returns:
            ErrorResponse padronizada
        """
        # Mapear códigos HTTP para códigos de erro
        status_code = http_exception.code
        error_code = self._map_http_status_to_error_code(status_code)
        
        return self.create_error_response(
            error_code=error_code,
            message=str(http_exception.description) if http_exception.description else None
        )
    
    def handle_generic_exception(self, exception: Exception) -> ErrorResponse:
        """
        Trata exceções genéricas
        
        Args:
            exception: Exceção genérica
            
        Returns:
            ErrorResponse padronizada
        """
        # Determinar tipo de erro baseado na exceção
        error_code = self._determine_error_code_from_exception(exception)
        
        # Em produção, não expor detalhes internos
        if current_app.config.get('ENV') == 'production':
            message = "Erro interno do servidor"
            details = None
        else:
            message = str(exception)
            details = {
                'exception_type': type(exception).__name__,
                'traceback': traceback.format_exc()
            }
        
        return self.create_error_response(
            error_code=error_code,
            message=message,
            details=details
        )
    
    def _map_http_status_to_error_code(self, status_code: int) -> str:
        """Mapeia códigos HTTP para códigos de erro"""
        mapping = {
            400: ErrorCode.VALIDATION_ERROR.value,
            401: ErrorCode.UNAUTHORIZED.value,
            403: ErrorCode.FORBIDDEN.value,
            404: ErrorCode.RESOURCE_NOT_FOUND.value,
            409: ErrorCode.CONFLICT.value,
            429: ErrorCode.RATE_LIMIT_EXCEEDED.value,
            500: ErrorCode.INTERNAL_ERROR.value,
            502: ErrorCode.BAD_GATEWAY.value,
            503: ErrorCode.SERVICE_UNAVAILABLE.value,
            504: ErrorCode.GATEWAY_TIMEOUT.value
        }
        return mapping.get(status_code, ErrorCode.INTERNAL_ERROR.value)
    
    def _determine_error_code_from_exception(self, exception: Exception) -> str:
        """Determina código de erro baseado no tipo de exceção"""
        exception_type = type(exception).__name__
        
        # Mapear tipos de exceção para códigos de erro
        mapping = {
            'ValueError': ErrorCode.INVALID_VALUE.value,
            'TypeError': ErrorCode.INVALID_FORMAT.value,
            'KeyError': ErrorCode.MISSING_REQUIRED_FIELD.value,
            'FileNotFoundError': ErrorCode.FILE_NOT_FOUND.value,
            'PermissionError': ErrorCode.INSUFFICIENT_PERMISSIONS.value,
            'ConnectionError': ErrorCode.EXTERNAL_SERVICE_ERROR.value,
            'TimeoutError': ErrorCode.GATEWAY_TIMEOUT.value,
            'IntegrityError': ErrorCode.DUPLICATE_ENTRY.value,
            'OperationalError': ErrorCode.DATABASE_ERROR.value
        }
        
        return mapping.get(exception_type, ErrorCode.INTERNAL_ERROR.value)
    
    def _get_validation_suggestion(self, error_type: str) -> Optional[str]:
        """Obtém sugestão baseada no tipo de erro de validação"""
        suggestions = {
            'missing': 'Campo é obrigatório',
            'value_error': 'Verifique o valor fornecido',
            'type_error': 'Tipo de dado incorreto',
            'value_error.any_str.min_length': 'Valor muito curto',
            'value_error.any_str.max_length': 'Valor muito longo',
            'value_error.number.not_gt': 'Valor deve ser maior',
            'value_error.number.not_lt': 'Valor deve ser menor',
            'value_error.email': 'Formato de email inválido',
            'value_error.url': 'Formato de URL inválido'
        }
        return suggestions.get(error_type)
    
    def _log_error(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]],
        severity: ErrorSeverity
    ):
        """Registra erro no log"""
        log_data = {
            'error_code': error_code,
            'message': message,
            'severity': severity.value,
            'path': request.path if request else None,
            'method': request.method if request else None,
            'ip': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if details:
            log_data['details'] = details
        
        # Log baseado na severidade
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Erro crítico: {json.dumps(log_data)}")
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"Erro alto: {json.dumps(log_data)}")
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Erro médio: {json.dumps(log_data)}")
        else:
            logger.info(f"Erro baixo: {json.dumps(log_data)}")

# Instância global do error handler
error_handler = ErrorHandler()

# Funções utilitárias para uso direto
def create_error_response(
    error_code: str,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Cria resposta de erro usando o handler global"""
    return error_handler.create_error_response(error_code, message, details, request_id)

def handle_validation_error(validation_error: ValidationError) -> ErrorResponse:
    """Trata erro de validação usando o handler global"""
    return error_handler.handle_validation_error(validation_error)

def handle_http_exception(http_exception: HTTPException) -> ErrorResponse:
    """Trata exceção HTTP usando o handler global"""
    return error_handler.handle_http_exception(http_exception)

def handle_generic_exception(exception: Exception) -> ErrorResponse:
    """Trata exceção genérica usando o handler global"""
    return error_handler.handle_generic_exception(exception)

# Decorator para tratamento automático de erros
def handle_errors(func):
    """Decorator para tratamento automático de erros em endpoints"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            error_response = handle_validation_error(e)
            return error_response.to_json_response(400)
        except HTTPException as e:
            error_response = handle_http_exception(e)
            return error_response.to_json_response(e.code)
        except Exception as e:
            error_response = handle_generic_exception(e)
            return error_response.to_json_response(500)
    return wrapper

# Middleware para capturar erros não tratados
def error_middleware(error):
    """Middleware para capturar erros não tratados"""
    if isinstance(error, ValidationError):
        error_response = handle_validation_error(error)
        return error_response.to_json_response(400)
    elif isinstance(error, HTTPException):
        error_response = handle_http_exception(error)
        return error_response.to_json_response(error.code)
    else:
        error_response = handle_generic_exception(error)
        return error_response.to_json_response(500) 