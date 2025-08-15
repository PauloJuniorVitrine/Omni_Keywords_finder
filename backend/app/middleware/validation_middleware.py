"""
Middleware de Validação Global - Omni Keywords Finder
Implementa validação centralizada, sanitização e rate limiting

Prompt: Implementação de middleware de validação global
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import time
import json
import re
import hashlib
from typing import Dict, Any, Optional, Callable
from functools import wraps
from flask import request, jsonify, g, current_app
from werkzeug.exceptions import RequestEntityTooLarge, BadRequest
import redis
from datetime import datetime, timedelta

class ValidationMiddleware:
    """Middleware de validação global para validação de entrada"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.rate_limits = {
            'auth': {'requests': 5, 'window': 300},  # 5 requests por 5 min
            'execucao': {'requests': 10, 'window': 60},  # 10 requests por min
            'payment': {'requests': 3, 'window': 300},  # 3 requests por 5 min
            'default': {'requests': 100, 'window': 60}  # 100 requests por min
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o middleware com a aplicação Flask"""
        self.app = app
        
        # Configurar Redis para rate limiting
        try:
            self.redis_client = redis.Redis(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                db=app.config.get('REDIS_DB', 0),
                decode_responses=True
            )
        except Exception as e:
            app.logger.warning(f"Redis não disponível para rate limiting: {e}")
            self.redis_client = None
        
        # Registrar middleware
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Registrar handlers de erro
        app.register_error_handler(RequestEntityTooLarge, self.handle_payload_too_large)
        app.register_error_handler(BadRequest, self.handle_bad_request)
    
    def before_request(self):
        """Executa antes de cada requisição"""
        # Validar tamanho do payload
        self.validate_payload_size()
        
        # Validar headers obrigatórios
        self.validate_headers()
        
        # Aplicar rate limiting
        self.apply_rate_limiting()
        
        # Sanitizar entrada
        self.sanitize_input()
        
        # Registrar início da requisição
        g.request_start_time = time.time()
        g.request_id = self.generate_request_id()
    
    def after_request(self, response):
        """Executa após cada requisição"""
        # Adicionar headers de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Adicionar headers de rate limiting
        if hasattr(g, 'rate_limit_info'):
            response.headers['X-RateLimit-Limit'] = str(g.rate_limit_info['limit'])
            response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_info['remaining'])
            response.headers['X-RateLimit-Reset'] = str(g.rate_limit_info['reset'])
        
        # Log da requisição
        self.log_request(response)
        
        return response
    
    def validate_payload_size(self):
        """Valida o tamanho do payload da requisição"""
        content_length = request.content_length
        
        if content_length is None:
            return
        
        # Limites por tipo de endpoint
        limits = {
            'auth': 1024,  # 1KB para autenticação
            'execucao': 10240,  # 10KB para execuções
            'payment': 5120,  # 5KB para pagamentos
            'upload': 10485760,  # 10MB para uploads
            'default': 102400  # 100KB padrão
        }
        
        # Determinar limite baseado no endpoint
        endpoint = request.endpoint or 'default'
        limit = limits.get(endpoint.split('.')[0], limits['default'])
        
        if content_length > limit:
            raise RequestEntityTooLarge(f"Payload muito grande. Máximo: {limit} bytes")
    
    def validate_headers(self):
        """Valida headers obrigatórios"""
        required_headers = {
            'User-Agent': r'.+',  # Qualquer User-Agent
            'Accept': r'application/json',  # Aceitar JSON
        }
        
        # Headers condicionais baseados no método
        if request.method in ['POST', 'PUT', 'PATCH']:
            required_headers['Content-Type'] = r'application/json'
        
        for header, pattern in required_headers.items():
            value = request.headers.get(header)
            if not value:
                raise BadRequest(f"Header obrigatório ausente: {header}")
            
            if not re.match(pattern, value, re.IGNORECASE):
                raise BadRequest(f"Header inválido: {header}")
    
    def apply_rate_limiting(self):
        """Aplica rate limiting baseado no endpoint e usuário/IP"""
        if not self.redis_client:
            return
        
        # Identificar cliente (IP ou usuário autenticado)
        client_id = self.get_client_id()
        
        # Determinar limite baseado no endpoint
        endpoint = request.endpoint or 'default'
        endpoint_key = endpoint.split('.')[0]
        limit_config = self.rate_limits.get(endpoint_key, self.rate_limits['default'])
        
        # Chave para Redis
        redis_key = f"rate_limit:{client_id}:{endpoint_key}"
        current_time = int(time.time())
        window_start = current_time - limit_config['window']
        
        # Verificar requisições na janela
        try:
            # Adicionar requisição atual
            self.redis_client.zadd(redis_key, {str(current_time): current_time})
            
            # Remover requisições antigas
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)
            
            # Contar requisições na janela
            request_count = self.redis_client.zcard(redis_key)
            
            # Definir expiração
            self.redis_client.expire(redis_key, limit_config['window'])
            
            # Verificar limite
            if request_count > limit_config['requests']:
                reset_time = current_time + limit_config['window']
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Máximo de {limit_config["requests"]} requisições por {limit_config["window"]} segundos',
                    'reset_time': reset_time
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(limit_config['requests'])
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(reset_time)
                return response
            
            # Armazenar informações de rate limit
            g.rate_limit_info = {
                'limit': limit_config['requests'],
                'remaining': limit_config['requests'] - request_count,
                'reset': current_time + limit_config['window']
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro no rate limiting: {e}")
    
    def sanitize_input(self):
        """Sanitiza entrada para prevenir XSS e injeção"""
        if request.is_json:
            data = request.get_json()
            if data:
                sanitized_data = self.sanitize_dict(data)
                request._cached_json = sanitized_data
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza dicionário recursivamente"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [self.sanitize_item(item) for item in value]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def sanitize_string(self, value: str) -> str:
        """Sanitiza string removendo caracteres perigosos"""
        # Remover caracteres de controle
        value = ''.join(char for char in value if ord(char) >= 32)
        
        # Escapar caracteres HTML
        html_escapes = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        }
        
        for char, escape in html_escapes.items():
            value = value.replace(char, escape)
        
        # Remover scripts suspeitos
        script_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'vbscript:',
            r'data:',
        ]
        
        for pattern in script_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value.strip()
    
    def sanitize_item(self, item: Any) -> Any:
        """Sanitiza item individual"""
        if isinstance(item, str):
            return self.sanitize_string(item)
        elif isinstance(item, dict):
            return self.sanitize_dict(item)
        elif isinstance(item, list):
            return [self.sanitize_item(subitem) for subitem in item]
        else:
            return item
    
    def get_client_id(self) -> str:
        """Obtém ID do cliente para rate limiting"""
        # Priorizar usuário autenticado
        if hasattr(g, 'user') and g.user:
            return f"user:{g.user.id}"
        
        # Fallback para IP
        return f"ip:{request.remote_addr}"
    
    def generate_request_id(self) -> str:
        """Gera ID único para a requisição"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(f"{request.remote_addr}{timestamp}".encode()).hexdigest()[:8]
        return f"{timestamp}-{random_part}"
    
    def log_request(self, response):
        """Registra log da requisição"""
        duration = time.time() - g.request_start_time
        
        log_data = {
            'request_id': g.request_id,
            'method': request.method,
            'endpoint': request.endpoint,
            'path': request.path,
            'status_code': response.status_code,
            'duration': round(duration, 3),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_length': request.content_length,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Adicionar informações de rate limit se disponível
        if hasattr(g, 'rate_limit_info'):
            log_data['rate_limit'] = g.rate_limit_info
        
        # Log baseado no status code
        if response.status_code >= 400:
            current_app.logger.warning(f"Request failed: {json.dumps(log_data)}")
        else:
            current_app.logger.info(f"Request completed: {json.dumps(log_data)}")
    
    def handle_payload_too_large(self, error):
        """Handler para payload muito grande"""
        return jsonify({
            'error': 'Payload too large',
            'message': 'O tamanho da requisição excede o limite permitido',
            'max_size': '100KB para requisições padrão'
        }), 413
    
    def handle_bad_request(self, error):
        """Handler para requisição malformada"""
        return jsonify({
            'error': 'Bad request',
            'message': str(error),
            'details': 'Verifique os headers e formato da requisição'
        }), 400

# Decorator para aplicar validação específica
def validate_input(schema_class):
    """Decorator para validar entrada com schema Pydantic"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validar entrada com schema
                if request.is_json:
                    data = request.get_json()
                    validated_data = schema_class(**data)
                    g.validated_data = validated_data
                else:
                    # Para dados de formulário
                    data = dict(request.form)
                    validated_data = schema_class(**data)
                    g.validated_data = validated_data
                
                return f(*args, **kwargs)
            
            except Exception as e:
                return jsonify({
                    'error': 'Validation error',
                    'message': str(e),
                    'details': 'Os dados fornecidos não atendem aos requisitos de validação'
                }), 422
        
        return decorated_function
    return decorator

# Instância global do middleware
validation_middleware = ValidationMiddleware() 