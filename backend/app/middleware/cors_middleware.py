from typing import Dict, List, Optional, Any
"""
Middleware CORS Avançado - Omni Keywords Finder

Este módulo implementa validação de origem CORS por ambiente
com headers de segurança adicionais.

Autor: Sistema Omni Keywords Finder
Data: 2024-12-27
Versão: 1.0.0
"""

import os
import re
from flask import request, jsonify, g
from functools import wraps
from datetime import datetime

# =============================================================================
# CONFIGURAÇÕES POR AMBIENTE
# =============================================================================

def get_cors_config():
    """Retorna configuração CORS baseada no ambiente"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return {
            'origins': [
                'https://omni-keywords-finder.com',
                'https://www.omni-keywords-finder.com',
                'https://app.omni-keywords-finder.com'
            ],
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': [
                'Content-Type', 
                'Authorization', 
                'X-Requested-With',
                'X-API-Key',
                'X-Client-Version',
                'X-Request-ID'
            ],
            'expose_headers': [
                'X-Request-ID',
                'X-Rate-Limit-Remaining',
                'X-Rate-Limit-Reset'
            ],
            'max_age': 3600,
            'strict_origin_validation': True,
            'log_violations': True
        }
    elif env == 'staging':
        return {
            'origins': [
                'https://staging.omni-keywords-finder.com',
                'https://test.omni-keywords-finder.com',
                'http://localhost:3000',  # Para testes locais
                'http://127.0.0.1:3000'
            ],
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': [
                'Content-Type', 
                'Authorization', 
                'X-Requested-With',
                'X-API-Key',
                'X-Client-Version',
                'X-Request-ID'
            ],
            'expose_headers': [
                'X-Request-ID',
                'X-Rate-Limit-Remaining',
                'X-Rate-Limit-Reset'
            ],
            'max_age': 3600,
            'strict_origin_validation': True,
            'log_violations': True
        }
    else:  # development
        return {
            'origins': [
                'http://localhost:3000',
                'http://localhost:3001',
                'http://127.0.0.1:3000',
                'http://127.0.0.1:3001',
                'http://localhost:5173',  # Vite dev server
                'http://127.0.0.1:5173'
            ],
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': [
                'Content-Type', 
                'Authorization', 
                'X-Requested-With',
                'X-API-Key',
                'X-Client-Version',
                'X-Request-ID'
            ],
            'expose_headers': [
                'X-Request-ID',
                'X-Rate-Limit-Remaining',
                'X-Rate-Limit-Reset'
            ],
            'max_age': 3600,
            'strict_origin_validation': False,
            'log_violations': False
        }

# =============================================================================
# VALIDAÇÃO DE ORIGEM
# =============================================================================

def is_valid_origin(origin, config):
    """Valida se a origem é permitida"""
    if not origin:
        return False
    
    # Verificação exata
    if origin in config['origins']:
        return True
    
    # Verificação por padrão (para desenvolvimento)
    if not config['strict_origin_validation']:
        # Permite localhost com qualquer porta em desenvolvimento
        if re.match(r'^http://localhost:\data+$', origin):
            return True
        if re.match(r'^http://127\.0\.0\.1:\data+$', origin):
            return True
    
    return False

def validate_origin_middleware():
    """Middleware para validação de origem CORS"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            config = get_cors_config()
            origin = request.headers.get('Origin')
            
            # Se não há origem, permite (pode ser uma requisição direta)
            if not origin:
                return f(*args, **kwargs)
            
            # Valida origem
            if not is_valid_origin(origin, config):
                if config['log_violations']:
                    log_cors_violation(origin, request.remote_addr)
                return jsonify({
                    'error': 'CORS policy violation',
                    'message': 'Origin not allowed',
                    'origin': origin
                }), 403
            
            # Adiciona headers CORS
            response = f(*args, **kwargs)
            
            # Se é uma resposta Flask, adiciona headers
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = ', '.join(config['methods'])
                response.headers['Access-Control-Allow-Headers'] = ', '.join(config['allow_headers'])
                response.headers['Access-Control-Expose-Headers'] = ', '.join(config['expose_headers'])
                response.headers['Access-Control-Max-Age'] = str(config['max_age'])
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                
                # Headers de segurança adicionais
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['X-Frame-Options'] = 'DENY'
                response.headers['X-XSS-Protection'] = '1; mode=block'
                response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
                
                # Adiciona Request ID se não existir
                if 'X-Request-ID' not in response.headers:
                    request_id = request.headers.get('X-Request-ID') or generate_request_id()
                    response.headers['X-Request-ID'] = request_id
            
            return response
        
        return decorated_function
    return decorator

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def generate_request_id():
    """Gera um ID único para a requisição"""
    import uuid
    return str(uuid.uuid4())

def log_cors_violation(origin, ip):
    """Loga violações de CORS"""
    try:
        from ..models import Log
        from .. import db
        
        log_entry = Log(
            nivel='WARNING',
            modulo='cors_middleware',
            mensagem=f'CORS policy violation: {origin} from {ip}',
            dados=f'{{"origin": "{origin}", "ip": "{ip}", "timestamp": "{datetime.now().isoformat()}"}}',
            timestamp=datetime.now()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        print(f"Erro ao logar violação CORS: {e}")

# =============================================================================
# DECORATOR PARA ENDPOINTS ESPECÍFICOS
# =============================================================================

def cors_protected(f):
    """Decorator para endpoints que precisam de proteção CORS específica"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        config = get_cors_config()
        origin = request.headers.get('Origin')
        
        # Para OPTIONS (preflight), sempre permite
        if request.method == 'OPTIONS':
            response = jsonify({})
            if origin and is_valid_origin(origin, config):
                response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = ', '.join(config['methods'])
            response.headers['Access-Control-Allow-Headers'] = ', '.join(config['allow_headers'])
            response.headers['Access-Control-Max-Age'] = str(config['max_age'])
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
        
        # Para outras requisições, valida origem
        if origin and not is_valid_origin(origin, config):
            if config['log_violations']:
                log_cors_violation(origin, request.remote_addr)
            return jsonify({
                'error': 'CORS policy violation',
                'message': 'Origin not allowed'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# =============================================================================
# FUNÇÃO DE INICIALIZAÇÃO
# =============================================================================

def init_cors_middleware(app):
    """Inicializa o middleware CORS no app Flask"""
    
    @app.before_request
    def before_request():
        """Executa antes de cada requisição"""
        # Adiciona Request ID se não existir
        if 'X-Request-ID' not in request.headers:
            request.headers['X-Request-ID'] = generate_request_id()
        
        # Log da requisição para auditoria
        g.request_id = request.headers.get('X-Request-ID')
        g.origin = request.headers.get('Origin')
        g.user_agent = request.headers.get('User-Agent')
    
    @app.after_request
    def after_request(response):
        """Executa após cada requisição"""
        config = get_cors_config()
        origin = request.headers.get('Origin')
        
        # Adiciona headers CORS se a origem for válida
        if origin and is_valid_origin(origin, config):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = ', '.join(config['methods'])
            response.headers['Access-Control-Allow-Headers'] = ', '.join(config['allow_headers'])
            response.headers['Access-Control-Expose-Headers'] = ', '.join(config['expose_headers'])
            response.headers['Access-Control-Max-Age'] = str(config['max_age'])
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        # Headers de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Adiciona Request ID se não existir
        if 'X-Request-ID' not in response.headers:
            response.headers['X-Request-ID'] = getattr(g, 'request_id', generate_request_id())
        
        return response
    
    return app 