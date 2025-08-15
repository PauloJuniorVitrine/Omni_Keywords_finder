from typing import Dict, List, Optional, Any
"""
Middleware de Headers de Segurança - Omni Keywords Finder

Este módulo implementa headers de segurança adicionais
para proteção contra ataques comuns.

Autor: Sistema Omni Keywords Finder
Data: 2024-12-27
Versão: 1.0.0
"""

import os
from flask import request, g

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

def get_security_config():
    """Retorna configuração de segurança baseada no ambiente"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return {
            'strict_transport_security': 'max-age=31536000; includeSubDomains; preload',
            'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';",
            'x_content_type_options': 'nosniff',
            'x_frame_options': 'DENY',
            'x_xss_protection': '1; mode=block',
            'referrer_policy': 'strict-origin-when-cross-origin',
            'permissions_policy': 'geolocation=(), microphone=(), camera=()',
            'cross_origin_embedder_policy': 'require-corp',
            'cross_origin_opener_policy': 'same-origin',
            'cross_origin_resource_policy': 'same-origin'
        }
    elif env == 'staging':
        return {
            'strict_transport_security': 'max-age=86400; includeSubDomains',
            'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;",
            'x_content_type_options': 'nosniff',
            'x_frame_options': 'DENY',
            'x_xss_protection': '1; mode=block',
            'referrer_policy': 'strict-origin-when-cross-origin',
            'permissions_policy': 'geolocation=(), microphone=(), camera=()',
            'cross_origin_embedder_policy': 'require-corp',
            'cross_origin_opener_policy': 'same-origin',
            'cross_origin_resource_policy': 'same-origin'
        }
    else:  # development
        return {
            'strict_transport_security': None,  # Não usar HSTS em desenvolvimento
            'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' http: https: ws: wss:;",
            'x_content_type_options': 'nosniff',
            'x_frame_options': 'SAMEORIGIN',  # Mais permissivo em desenvolvimento
            'x_xss_protection': '1; mode=block',
            'referrer_policy': 'no-referrer-when-downgrade',
            'permissions_policy': 'geolocation=(), microphone=(), camera=()',
            'cross_origin_embedder_policy': None,  # Desabilitado em desenvolvimento
            'cross_origin_opener_policy': None,  # Desabilitado em desenvolvimento
            'cross_origin_resource_policy': None  # Desabilitado em desenvolvimento
        }

# =============================================================================
# MIDDLEWARE DE HEADERS DE SEGURANÇA
# =============================================================================

def add_security_headers(response):
    """Adiciona headers de segurança à resposta"""
    config = get_security_config()
    
    # Headers básicos de segurança
    response.headers['X-Content-Type-Options'] = config['x_content_type_options']
    response.headers['X-Frame-Options'] = config['x_frame_options']
    response.headers['X-XSS-Protection'] = config['x_xss_protection']
    response.headers['Referrer-Policy'] = config['referrer_policy']
    
    # Content Security Policy
    if config['content_security_policy']:
        response.headers['Content-Security-Policy'] = config['content_security_policy']
    
    # Strict Transport Security (apenas em produção/staging)
    if config['strict_transport_security']:
        response.headers['Strict-Transport-Security'] = config['strict_transport_security']
    
    # Permissions Policy
    if config['permissions_policy']:
        response.headers['Permissions-Policy'] = config['permissions_policy']
    
    # Cross-Origin Policies (apenas em produção/staging)
    if config['cross_origin_embedder_policy']:
        response.headers['Cross-Origin-Embedder-Policy'] = config['cross_origin_embedder_policy']
    
    if config['cross_origin_opener_policy']:
        response.headers['Cross-Origin-Opener-Policy'] = config['cross_origin_opener_policy']
    
    if config['cross_origin_resource_policy']:
        response.headers['Cross-Origin-Resource-Policy'] = config['cross_origin_resource_policy']
    
    # Headers customizados
    response.headers['X-Powered-By'] = 'Omni Keywords Finder'  # Remove "Flask"
    response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
    
    return response

# =============================================================================
# VALIDAÇÃO DE HEADERS DE ENTRADA
# =============================================================================

def validate_request_headers():
    """Valida headers de entrada para detectar ataques"""
    suspicious_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Forwarded-Host',
        'X-Forwarded-Proto'
    ]
    
    for header in suspicious_headers:
        if header in request.headers:
            # Log de header suspeito
            log_suspicious_header(header, request.headers[header])
    
    # Validação de User-Agent
    user_agent = request.headers.get('User-Agent', '')
    if not user_agent or len(user_agent) > 500:
        log_suspicious_header('User-Agent', user_agent)

def log_suspicious_header(header_name, header_value):
    """Loga headers suspeitos"""
    try:
        from ..models import Log
        from .. import db
        from datetime import datetime
        
        log_entry = Log(
            nivel='WARNING',
            modulo='security_headers',
            mensagem=f'Suspicious header detected: {header_name}',
            dados=f'{{"header": "{header_name}", "value": "{header_value[:100]}", "ip": "{request.remote_addr}", "timestamp": "{datetime.now().isoformat()}"}}',
            timestamp=datetime.now()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        print(f"Erro ao logar header suspeito: {e}")

# =============================================================================
# FUNÇÃO DE INICIALIZAÇÃO
# =============================================================================

def init_security_headers(app):
    """Inicializa o middleware de headers de segurança"""
    
    @app.before_request
    def before_request():
        """Executa antes de cada requisição"""
        validate_request_headers()
    
    @app.after_request
    def after_request(response):
        """Executa após cada requisição"""
        return add_security_headers(response)
    
    return app 