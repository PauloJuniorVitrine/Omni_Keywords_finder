"""
Middleware de Tratamento de Erros - Omni Keywords Finder
Aplicação automática de tratamento de erros padronizado
Prompt: Tratamento de Erro - Padronização
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import logging
import traceback
from functools import wraps
from typing import Callable, Any, Dict
from flask import request, jsonify, current_app, g
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError
from backend.app.utils.error_handler import (
    error_handler, ErrorResponse, ErrorCode, ErrorSeverity
)
import time

logger = logging.getLogger(__name__)

def error_middleware(app):
    """
    Middleware para capturar e tratar erros automaticamente
    
    Args:
        app: Instância do Flask app
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Trata erros 400 - Bad Request"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.VALIDATION_ERROR.value,
            message="Requisição inválida",
            details={'original_error': str(error)}
        )
        return error_response.to_json_response(400)
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Trata erros 401 - Unauthorized"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.UNAUTHORIZED.value,
            message="Não autorizado"
        )
        return error_response.to_json_response(401)
    
    @app.errorhandler(403)
    def forbidden(error):
        """Trata erros 403 - Forbidden"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.FORBIDDEN.value,
            message="Acesso negado"
        )
        return error_response.to_json_response(403)
    
    @app.errorhandler(404)
    def not_found(error):
        """Trata erros 404 - Not Found"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.RESOURCE_NOT_FOUND.value,
            message="Recurso não encontrado"
        )
        return error_response.to_json_response(404)
    
    @app.errorhandler(409)
    def conflict(error):
        """Trata erros 409 - Conflict"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.CONFLICT.value,
            message="Conflito de recursos"
        )
        return error_response.to_json_response(409)
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Trata erros 429 - Too Many Requests"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED.value,
            message="Limite de taxa excedido"
        )
        return error_response.to_json_response(429)
    
    @app.errorhandler(500)
    def internal_error(error):
        """Trata erros 500 - Internal Server Error"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.INTERNAL_ERROR.value,
            message="Erro interno do servidor"
        )
        return error_response.to_json_response(500)
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Trata erros 502 - Bad Gateway"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.BAD_GATEWAY.value,
            message="Erro de gateway"
        )
        return error_response.to_json_response(502)
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Trata erros 503 - Service Unavailable"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.SERVICE_UNAVAILABLE.value,
            message="Serviço indisponível"
        )
        return error_response.to_json_response(503)
    
    @app.errorhandler(504)
    def gateway_timeout(error):
        """Trata erros 504 - Gateway Timeout"""
        error_response = error_handler.create_error_response(
            error_code=ErrorCode.GATEWAY_TIMEOUT.value,
            message="Timeout do gateway"
        )
        return error_response.to_json_response(504)
    
    @app.errorhandler(ValidationError)
    def validation_error(error):
        """Trata erros de validação do Pydantic"""
        return error_handler.handle_validation_error(error).to_json_response(400)
    
    @app.errorhandler(HTTPException)
    def http_exception(error):
        """Trata exceções HTTP do Werkzeug"""
        return error_handler.handle_http_exception(error).to_json_response(error.code)
    
    @app.errorhandler(Exception)
    def generic_exception(error):
        """Trata exceções genéricas não capturadas"""
        return error_handler.handle_generic_exception(error).to_json_response(500)

def request_id_middleware():
    """
    Middleware para adicionar ID único a cada requisição
    """
    import uuid
    
    @request.before_request
    def before_request():
        """Adiciona request_id antes de cada requisição"""
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
    
    @request.after_request
    def after_request(response):
        """Adiciona headers de rastreamento após cada requisição"""
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response

def error_logging_middleware():
    """
    Middleware para logging detalhado de erros
    """
    
    @request.before_request
    def before_request():
        """Log de início de requisição"""
        logger.info(f"Requisição iniciada: {request.method} {request.path} - IP: {request.remote_addr}")
    
    @request.after_request
    def after_request(response):
        """Log de fim de requisição"""
        if response.status_code >= 400:
            logger.warning(f"Requisição com erro: {request.method} {request.path} - Status: {response.status_code}")
        else:
            logger.info(f"Requisição concluída: {request.method} {request.path} - Status: {response.status_code}")
        return response

def error_handler_decorator(func: Callable) -> Callable:
    """
    Decorator para tratamento automático de erros em endpoints específicos
    
    Args:
        func: Função do endpoint
        
    Returns:
        Função decorada com tratamento de erros
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            error_response = error_handler.handle_validation_error(e)
            return error_response.to_json_response(400)
        except HTTPException as e:
            error_response = error_handler.handle_http_exception(e)
            return error_response.to_json_response(e.code)
        except Exception as e:
            error_response = error_handler.handle_generic_exception(e)
            return error_response.to_json_response(500)
    
    return wrapper

def safe_json_response(func: Callable) -> Callable:
    """
    Decorator para garantir respostas JSON seguras
    
    Args:
        func: Função do endpoint
        
    Returns:
        Função decorada com tratamento de JSON seguro
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # Se já é uma resposta JSON, retorna como está
            if isinstance(result, tuple) and len(result) == 2:
                response, status_code = result
                if hasattr(response, 'json'):
                    return response, status_code
            
            # Se é um dicionário, converte para JSON
            if isinstance(result, dict):
                return jsonify(result), 200
            
            # Se é uma string, retorna como JSON
            if isinstance(result, str):
                return jsonify({'message': result}), 200
            
            # Para outros tipos, converte para string
            return jsonify({'result': str(result)}), 200
            
        except Exception as e:
            error_response = error_handler.handle_generic_exception(e)
            return error_response.to_json_response(500)
    
    return wrapper

def validate_request_data(schema_class=None):
    """
    Decorator para validação automática de dados de requisição
    
    Args:
        schema_class: Classe do schema Pydantic para validação
        
    Returns:
        Decorator que valida dados de entrada
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Validar dados JSON se schema fornecido
                if schema_class and request.is_json:
                    data = request.get_json()
                    if data is None:
                        error_response = error_handler.create_error_response(
                            error_code=ErrorCode.VALIDATION_ERROR.value,
                            message="Dados JSON obrigatórios"
                        )
                        return error_response.to_json_response(400)
                    
                    # Validar com schema
                    validated_data = schema_class(**data)
                    # Adicionar dados validados ao contexto
                    g.validated_data = validated_data
                
                return func(*args, **kwargs)
                
            except ValidationError as e:
                error_response = error_handler.handle_validation_error(e)
                return error_response.to_json_response(400)
            except Exception as e:
                error_response = error_handler.handle_generic_exception(e)
                return error_response.to_json_response(500)
        
        return wrapper
    return decorator

def require_authentication(func: Callable) -> Callable:
    """
    Decorator para verificar autenticação
    
    Args:
        func: Função do endpoint
        
    Returns:
        Função decorada com verificação de autenticação
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Verificar se usuário está autenticado
            if not hasattr(g, 'user') or g.user is None:
                error_response = error_handler.create_error_response(
                    error_code=ErrorCode.UNAUTHORIZED.value,
                    message="Autenticação necessária"
                )
                return error_response.to_json_response(401)
            
            return func(*args, **kwargs)
            
        except Exception as e:
            error_response = error_handler.handle_generic_exception(e)
            return error_response.to_json_response(500)
    
    return wrapper

def require_permissions(*required_permissions):
    """
    Decorator para verificar permissões específicas
    
    Args:
        *required_permissions: Lista de permissões necessárias
        
    Returns:
        Decorator que verifica permissões
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verificar se usuário tem permissões necessárias
                if not hasattr(g, 'user') or g.user is None:
                    error_response = error_handler.create_error_response(
                        error_code=ErrorCode.UNAUTHORIZED.value,
                        message="Autenticação necessária"
                    )
                    return error_response.to_json_response(401)
                
                # TODO: Implementar verificação de permissões
                # user_permissions = get_user_permissions(g.user.id)
                # if not all(perm in user_permissions for perm in required_permissions):
                #     error_response = error_handler.create_error_response(
                #         error_code=ErrorCode.INSUFFICIENT_PERMISSIONS.value,
                #         message="Permissões insuficientes"
                #     )
                #     return error_response.to_json_response(403)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                error_response = error_handler.handle_generic_exception(e)
                return error_response.to_json_response(500)
        
        return wrapper
    return decorator

# Função para inicializar todos os middlewares
def init_error_middlewares(app):
    """
    Inicializa todos os middlewares de erro
    
    Args:
        app: Instância do Flask app
    """
    # Aplicar middleware de tratamento de erros
    error_middleware(app)
    
    # Aplicar middleware de request_id
    request_id_middleware()
    
    # Aplicar middleware de logging
    error_logging_middleware()
    
    logger.info("Middlewares de erro inicializados com sucesso") 