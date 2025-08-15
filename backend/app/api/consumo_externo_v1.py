"""
API de Consumo Externo (v1) - Omni Keywords Finder
Validação robusta e sanitização de dados para APIs externas
Prompt: Validação de consumo externo
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import os
import re
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden

from infrastructure.consumo_externo.client_api_externa_v1 import APIExternaClientV1
from app.schemas.external_consumption_schemas import (
    ExternalEndpointSchema,
    ExternalRequestSchema,
    ExternalResponseSchema,
    ExternalFilterSchema,
    ExternalHealthSchema
)
from app.utils.security_logger import SecurityLogger
from app.utils.external_rate_limiter import ExternalRateLimiter, external_get_rate_limit, external_post_rate_limit
from app.utils.sanitizer import DataSanitizer

# Configuração de logging
logger = logging.getLogger(__name__)
security_logger = SecurityLogger()

bp = Blueprint('consumo_externo_v1', __name__, url_prefix='/api/v1/externo')

# Cliente da API externa
client = APIExternaClientV1(
    base_url=os.getenv('EXTERNAL_API_URL', 'https://api.exemplo.com'),
    token=os.getenv('EXTERNAL_API_TOKEN', 'demo')
)

# Rate limiter para consumo externo
rate_limiter = ExternalRateLimiter(
    redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379')
)

# Sanitizador de dados
sanitizer = DataSanitizer()

def validate_and_sanitize_endpoint(endpoint: str) -> str:
    """
    Valida e sanitiza endpoint de forma robusta
    
    Args:
        endpoint: Endpoint a ser validado
        
    Returns:
        Endpoint sanitizado
        
    Raises:
        BadRequest: Se endpoint for inválido
    """
    try:
        # Validação com schema
        endpoint_schema = ExternalEndpointSchema(endpoint=endpoint)
        return endpoint_schema.endpoint
    except ValidationError as e:
        security_logger.log_security_event(
            event_type="validation_error",
            severity="warning",
            details={
                "component": "external_consumption",
                "field": "endpoint",
                "value": endpoint,
                "errors": e.errors()
            }
        )
        raise BadRequest(f"Endpoint inválido: {e.errors()}")

def validate_and_sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida e sanitiza dados da requisição
    
    Args:
        data: Dados da requisição
        
    Returns:
        Dados sanitizados
        
    Raises:
        BadRequest: Se dados forem inválidos
    """
    try:
        # Validação com schema
        request_schema = ExternalRequestSchema(**data)
        return request_schema.dict()
    except ValidationError as e:
        security_logger.log_security_event(
            event_type="validation_error",
            severity="warning",
            details={
                "component": "external_consumption",
                "field": "request_data",
                "value": str(data),
                "errors": e.errors()
            }
        )
        raise BadRequest(f"Dados de requisição inválidos: {e.errors()}")

def log_external_request(endpoint: str, method: str, params: Optional[Dict] = None, 
                        response_time: Optional[float] = None, status_code: Optional[int] = None,
                        error: Optional[str] = None):
    """
    Registra logs estruturados de requisições externas
    
    Args:
        endpoint: Endpoint chamado
        method: Método HTTP
        params: Parâmetros da requisição
        response_time: Tempo de resposta
        status_code: Código de status
        error: Erro ocorrido
    """
    log_data = {
        "component": "external_consumption",
        "endpoint": endpoint,
        "method": method,
        "params": params,
        "response_time": response_time,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": getattr(request, 'user_id', None),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent')
    }
    
    if error:
        log_data["error"] = error
        security_logger.log_security_event(
            event_type="external_api_error",
            severity="error",
            details=log_data
        )
    else:
        logger.info("Requisição externa executada", extra=log_data)

@bp.route('/get', methods=['GET'])
def get_externo():
    """
    Endpoint GET para consumo externo com validação robusta
    """
    start_time = time.time()
    
    try:
        # Rate limiting
        client_id = rate_limiter.get_client_identifier(request)
        client_type = rate_limiter.get_client_type(request)
        allowed, rate_info = rate_limiter.check_rate_limit(client_id, "get", client_type)
        
        if not allowed:
            security_logger.log_security_event(
                event_type="rate_limit_exceeded",
                severity="warning",
                details={
                    "component": "external_consumption",
                    "endpoint": "/get",
                    "ip_address": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent'),
                    "client_type": client_type,
                    "rate_info": rate_info
                }
            )
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Too many requests. Try again later."
            }), 429
        
        # Validação de parâmetros
        endpoint = request.args.get('endpoint', '')
        if not endpoint:
            raise BadRequest("Parâmetro 'endpoint' é obrigatório")
        
        # Sanitização e validação do endpoint
        sanitized_endpoint = validate_and_sanitize_endpoint(endpoint)
        
        # Validação de parâmetros adicionais
        params = {}
        for key, value in request.args.items():
            if key != 'endpoint':
                # Sanitiza chave e valor
                clean_key = sanitizer.sanitize_string(key)
                clean_value = sanitizer.sanitize_string(value)
                if clean_key and clean_value:
                    params[clean_key] = clean_value
        
        # Execução da requisição
        resultado = client.get_com_fallback(sanitized_endpoint)
        
        # Cálculo do tempo de resposta
        response_time = time.time() - start_time
        
        # Log de sucesso
        log_external_request(
            endpoint=sanitized_endpoint,
            method="GET",
            params=params,
            response_time=response_time,
            status_code=200
        )
        
        return jsonify({
            "success": True,
            "data": resultado,
            "response_time": response_time,
            "endpoint": sanitized_endpoint
        }), 200
        
    except BadRequest as e:
        response_time = time.time() - start_time
        log_external_request(
            endpoint=endpoint if 'endpoint' in locals() else "unknown",
            method="GET",
            response_time=response_time,
            status_code=400,
            error=str(e)
        )
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        response_time = time.time() - start_time
        log_external_request(
            endpoint=endpoint if 'endpoint' in locals() else "unknown",
            method="GET",
            response_time=response_time,
            status_code=500,
            error=str(e)
        )
        return jsonify({"error": "Erro interno do servidor"}), 500

@bp.route('/post', methods=['POST'])
def post_externo():
    """
    Endpoint POST para consumo externo com validação robusta
    """
    start_time = time.time()
    
    try:
        # Rate limiting
        client_id = rate_limiter.get_client_identifier(request)
        client_type = rate_limiter.get_client_type(request)
        allowed, rate_info = rate_limiter.check_rate_limit(client_id, "post", client_type)
        
        if not allowed:
            security_logger.log_security_event(
                event_type="rate_limit_exceeded",
                severity="warning",
                details={
                    "component": "external_consumption",
                    "endpoint": "/post",
                    "ip_address": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent'),
                    "client_type": client_type,
                    "rate_info": rate_info
                }
            )
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Too many requests. Try again later."
            }), 429
        
        # Validação de dados da requisição
        request_data = request.get_json()
        if not request_data:
            raise BadRequest("Dados JSON são obrigatórios")
        
        # Validação e sanitização dos dados
        validated_data = validate_and_sanitize_request_data(request_data)
        
        # Execução da requisição
        resultado = client.post_com_fallback(
            endpoint=validated_data.get('endpoint'),
            data=validated_data.get('body'),
            headers=validated_data.get('headers')
        )
        
        # Cálculo do tempo de resposta
        response_time = time.time() - start_time
        
        # Log de sucesso
        log_external_request(
            endpoint=validated_data.get('endpoint', 'unknown'),
            method="POST",
            params=validated_data.get('params'),
            response_time=response_time,
            status_code=200
        )
        
        return jsonify({
            "success": True,
            "data": resultado,
            "response_time": response_time,
            "endpoint": validated_data.get('endpoint')
        }), 200
        
    except BadRequest as e:
        response_time = time.time() - start_time
        log_external_request(
            endpoint="unknown",
            method="POST",
            response_time=response_time,
            status_code=400,
            error=str(e)
        )
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        response_time = time.time() - start_time
        log_external_request(
            endpoint="unknown",
            method="POST",
            response_time=response_time,
            status_code=500,
            error=str(e)
        )
        return jsonify({"error": "Erro interno do servidor"}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check para APIs externas
    """
    try:
        # Validação de parâmetros
        endpoint = request.args.get('endpoint', '')
        if not endpoint:
            raise BadRequest("Parâmetro 'endpoint' é obrigatório")
        
        # Sanitização do endpoint
        sanitized_endpoint = validate_and_sanitize_endpoint(endpoint)
        
        # Teste de conectividade
        start_time = time.time()
        try:
            client.get_com_fallback(sanitized_endpoint)
            response_time = time.time() - start_time
            status = "healthy"
            error_message = None
        except Exception as e:
            response_time = time.time() - start_time
            status = "unhealthy"
            error_message = str(e)
        
        # Validação com schema
        health_data = ExternalHealthSchema(
            endpoint=sanitized_endpoint,
            status=status,
            response_time=response_time,
            error_message=error_message
        )
        
        return jsonify(health_data.dict()), 200
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Métricas de consumo externo
    """
    try:
        # Validação de filtros
        filters = {}
        for key, value in request.args.items():
            if key in ['start_date', 'end_date', 'limit', 'offset']:
                filters[key] = value
        
        # Validação com schema
        filter_schema = ExternalFilterSchema(**filters)
        
        # Implementar lógica de métricas aqui
        # Por enquanto, retorna dados simulados
        metrics = {
            "total_requests": 100,
            "successful_requests": 95,
            "failed_requests": 5,
            "avg_response_time": 0.5,
            "max_response_time": 2.0,
            "min_response_time": 0.1,
            "error_rate": 0.05,
            "last_request": datetime.utcnow().isoformat()
        }
        
        return jsonify(metrics), 200
        
    except ValidationError as e:
        return jsonify({"error": f"Filtros inválidos: {e.errors()}"}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500

@bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """
    Handler para erros de validação
    """
    security_logger.log_security_event(
        event_type="validation_error",
        severity="warning",
        details={
            "component": "external_consumption",
            "errors": error.errors()
        }
    )
    return jsonify({"error": "Dados inválidos", "details": error.errors()}), 400

@bp.errorhandler(Exception)
def handle_generic_error(error):
    """
    Handler para erros genéricos
    """
    security_logger.log_security_event(
        event_type="unexpected_error",
        severity="error",
        details={
            "component": "external_consumption",
            "error": str(error),
            "error_type": type(error).__name__
        }
    )
    return jsonify({"error": "Erro interno do servidor"}), 500 