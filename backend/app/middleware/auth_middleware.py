"""
Auth Middleware
Middleware para validação de autenticação JWT em endpoints sensíveis.

Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - FIXTYPE-003.3
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-27 23:15:00 UTC
Tracing ID: AUTH_MIDDLEWARE_20241227_001
"""

from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend.app.models.user import User
from backend.app.models import db
import logging
from typing import List, Optional, Callable, Any
import os

# Configuração de endpoints que não precisam de autenticação
PUBLIC_ENDPOINTS = [
    '/api/auth/login',
    '/api/auth/oauth2/login/<provider>',
    '/api/auth/oauth2/callback/<provider>',
    '/api/public/health',
    '/api/public/metrics',
    '/api/docs',
    '/api/docs/openapi.json',
    '/api/docs/swagger',
    '/api/docs/redoc'
]

# Configuração de endpoints que precisam de autenticação mas podem ser acessados por API tokens
API_TOKEN_ENDPOINTS = [
    '/api/public/execucoes',
    '/api/public/exportacoes',
    '/api/public/metricas'
]

# Configuração de endpoints que precisam de autenticação JWT completa
PROTECTED_ENDPOINTS = [
    '/api/nichos',
    '/api/categorias',
    '/api/execucoes',
    '/api/execucoes_agendadas',
    '/api/logs',
    '/api/notificacoes',
    '/api/payments',
    '/api/webhooks',
    '/api/analytics',
    '/api/ab_testing',
    '/api/templates',
    '/api/credentials',
    '/api/ai_integration',
    '/api/prompt_system'
]

def get_api_token() -> Optional[str]:
    """Obtém o token da API das variáveis de ambiente."""
    return os.getenv('API_TOKEN')

def validate_api_token(token: str) -> bool:
    """Valida se o token da API é válido."""
    expected_token = get_api_token()
    return bool(expected_token and token == expected_token)

def get_user_from_token() -> Optional[User]:
    """Obtém o usuário a partir do token JWT."""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except Exception as e:
        logging.warning(f"Erro ao obter usuário do token: {e}")
        return None

def check_user_permissions(user: User, endpoint: str, method: str) -> bool:
    """
    Verifica se o usuário tem permissão para acessar o endpoint.
    
    Args:
        user: Usuário autenticado
        endpoint: Endpoint sendo acessado
        method: Método HTTP (GET, POST, PUT, DELETE)
    
    Returns:
        bool: True se o usuário tem permissão
    """
    if not user or not user.ativo:
        return False
    
    # Admin tem acesso total
    if user.role == 'admin':
        return True
    
    # Usuário comum tem acesso limitado
    if user.role == 'user':
        # Usuários podem ler dados, mas não podem modificar configurações críticas
        if method in ['GET']:
            return True
        elif method in ['POST', 'PUT', 'DELETE']:
            # Usuários podem criar/editar execuções e nichos básicos
            if '/api/execucoes' in endpoint:
                return True
            if '/api/nichos' in endpoint and method in ['POST', 'PUT']:
                return True
            if '/api/categorias' in endpoint and method in ['POST', 'PUT']:
                return True
            # Não podem acessar configurações de sistema
            if any(restricted in endpoint for restricted in [
                '/api/credentials',
                '/api/ai_integration',
                '/api/analytics',
                '/api/ab_testing',
                '/api/templates'
            ]):
                return False
    
    return False

def log_auth_attempt(user_id: Optional[int], endpoint: str, method: str, success: bool, ip: str):
    """Registra tentativa de autenticação."""
    status = "SUCCESS" if success else "FAILED"
    logging.info(f"AUTH_ATTEMPT: user_id={user_id}, endpoint={endpoint}, method={method}, status={status}, ip={ip}")

def auth_required(require_admin: bool = False, require_api_token: bool = False):
    """
    Decorator para endpoints que requerem autenticação.
    
    Args:
        require_admin: Se True, apenas admins podem acessar
        require_api_token: Se True, aceita API token como alternativa ao JWT
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obter informações da requisição
            endpoint = request.endpoint
            method = request.method
            ip = request.remote_addr
            
            # Verificar se é endpoint público
            if any(public_endpoint.replace('<provider>', 'google') in request.path 
                   for public_endpoint in PUBLIC_ENDPOINTS):
                return f(*args, **kwargs)
            
            # Verificar API token se permitido
            if require_api_token:
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    if validate_api_token(token):
                        logging.info(f"API_TOKEN_ACCESS: endpoint={endpoint}, method={method}, ip={ip}")
                        return f(*args, **kwargs)
            
            # Verificar JWT
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                
                if not user:
                    log_auth_attempt(None, endpoint, method, False, ip)
                    return jsonify({'erro': 'Usuário não encontrado'}), 401
                
                if not user.ativo:
                    log_auth_attempt(user_id, endpoint, method, False, ip)
                    return jsonify({'erro': 'Usuário inativo'}), 403
                
                # Verificar permissões
                if not check_user_permissions(user, request.path, method):
                    log_auth_attempt(user_id, endpoint, method, False, ip)
                    return jsonify({'erro': 'Permissão negada'}), 403
                
                # Verificar se requer admin
                if require_admin and user.role != 'admin':
                    log_auth_attempt(user_id, endpoint, method, False, ip)
                    return jsonify({'erro': 'Acesso restrito a administradores'}), 403
                
                log_auth_attempt(user_id, endpoint, method, True, ip)
                return f(*args, **kwargs)
                
            except Exception as e:
                log_auth_attempt(None, endpoint, method, False, ip)
                logging.warning(f"Auth error: {e}")
                return jsonify({'erro': 'Token inválido ou expirado'}), 401
        
        return decorated_function
    return decorator

def admin_required(f: Callable) -> Callable:
    """Decorator para endpoints que requerem privilégios de administrador."""
    return auth_required(require_admin=True)(f)

def api_token_or_jwt_required(f: Callable) -> Callable:
    """Decorator para endpoints que aceitam API token ou JWT."""
    return auth_required(require_api_token=True)(f)

def get_current_user() -> Optional[User]:
    """Obtém o usuário atual da requisição."""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None

def get_user_role() -> Optional[str]:
    """Obtém o role do usuário atual."""
    user = get_current_user()
    return user.role if user else None

def is_admin() -> bool:
    """Verifica se o usuário atual é administrador."""
    return get_user_role() == 'admin'

def is_authenticated() -> bool:
    """Verifica se o usuário está autenticado."""
    return get_current_user() is not None

# Middleware para registrar todas as requisições
def auth_middleware():
    """Middleware para registrar e validar autenticação em todas as requisições."""
    def before_request():
        # Log da requisição
        logging.info(f"REQUEST: {request.method} {request.path} from {request.remote_addr}")
        
        # Verificar se é endpoint protegido
        if any(protected in request.path for protected in PROTECTED_ENDPOINTS):
            # Verificar se tem token
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                logging.warning(f"NO_AUTH_HEADER: {request.method} {request.path} from {request.remote_addr}")
                return jsonify({'erro': 'Token de autenticação necessário'}), 401
    
    def after_request(response):
        # Log da resposta
        logging.info(f"RESPONSE: {request.method} {request.path} -> {response.status_code}")
        return response
    
    return before_request, after_request

# Função para configurar o middleware na aplicação
def init_auth_middleware(app):
    """Inicializa o middleware de autenticação na aplicação Flask."""
    before_request, after_request = auth_middleware()
    
    app.before_request(before_request)
    app.after_request(after_request)
    
    logging.info("Auth middleware initialized") 