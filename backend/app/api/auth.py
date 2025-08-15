from flask import Blueprint, request, jsonify, url_for, redirect, session
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from typing import Dict, List, Optional, Any
from backend.app.models.user import User
from backend.app.models import db
from werkzeug.security import check_password_hash
import os
from authlib.integrations.flask_client import OAuth
import logging
from backend.app.middleware.rate_limiter import auth_rate_limit, oauth_rate_limit, init_redis
from backend.app.schemas.auth import LoginRequest
from pydantic import ValidationError
from backend.app.security.audit_logger import (
    security_logger, SecurityEventType, SecurityLevel
)
from backend.app.utils.error_handler import (
    create_error_response, handle_validation_error, handle_generic_exception,
    ErrorCode
)
from backend.app.middleware.error_middleware import (
    error_handler_decorator, safe_json_response, validate_request_data
)

# Blueprint de autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Inicialização do JWTManager (deve ser chamada no app principal)
jwt = JWTManager()

# Inicialização do OAuth
oauth = OAuth()

def init_jwt(app):
    # Validação crítica: JWT_SECRET_KEY deve estar definida
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret or jwt_secret == 'troque-por-uma-chave-segura':
        raise ValueError(
            "JWT_SECRET_KEY deve ser definida como variável de ambiente. "
            "Use uma chave segura de pelo menos 32 caracteres."
        )
    
    app.config['JWT_SECRET_KEY'] = jwt_secret
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Log de segurança (sem expor a chave)
    logging.info(f"JWT inicializado com sucesso. Expiração: {app.config['JWT_ACCESS_TOKEN_EXPIRES']}s")
    
    jwt.init_app(app)

def init_oauth(app):
    oauth.init_app(app)
    # Google
    oauth.register(
        name='google',
        client_id=os.getenv('OAUTH2_GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('OAUTH2_GOOGLE_CLIENT_SECRET'),
        access_token_url='https://oauth2.googleapis.com/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
    )
    # GitHub
    oauth.register(
        name='github',
        client_id=os.getenv('OAUTH2_GITHUB_CLIENT_ID'),
        client_secret=os.getenv('OAUTH2_GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        userinfo_endpoint='https://api.github.com/user',
        client_kwargs={'scope': 'user:email'},
    )

@auth_bp.route('/login', methods=['POST'])
@auth_rate_limit
@error_handler_decorator
@safe_json_response
@validate_request_data(LoginRequest)
def login():
    """Endpoint de login com tratamento de erros padronizado"""
    # Dados já validados pelo decorator
    login_data = g.validated_data
    
    # Buscar usuário
    user = User.query.filter_by(username=login_data.username).first()
    
    if not user or not check_password_hash(user.senha_hash, login_data.senha):
        # Log de tentativa de login falhada com detalhes de segurança
        security_logger.log_event(
            event_type=SecurityEventType.LOGIN_FAILED,
            username=login_data.username,
            details={
                'reason': 'invalid_credentials',
                'failed_attempts': 1,  # TODO: Implementar contador
                'endpoint': 'login'
            },
            security_level=SecurityLevel.WARNING
        )
        raise create_error_response(
            error_code=ErrorCode.INVALID_CREDENTIALS.value,
            message="Credenciais inválidas"
        )
    
    if not user.ativo:
        # Log de tentativa de login para usuário inativo
        security_logger.log_event(
            event_type=SecurityEventType.LOGIN_FAILED,
            username=login_data.username,
            user_id=str(user.id),
            details={
                'reason': 'inactive_account',
                'endpoint': 'login'
            },
            security_level=SecurityLevel.WARNING
        )
        raise create_error_response(
            error_code=ErrorCode.FORBIDDEN.value,
            message="Usuário inativo"
        )
    
    # Log de login bem-sucedido
    security_logger.log_event(
        event_type=SecurityEventType.LOGIN_SUCCESS,
        username=login_data.username,
        user_id=str(user.id),
        details={
            'endpoint': 'login',
            'provider': 'local'
        },
        security_level=SecurityLevel.INFO
    )
    
    access_token = create_access_token(identity=user.id)
    return {
        'success': True,
        'access_token': access_token,
        'user_id': user.id,
        'message': 'Login realizado com sucesso'
    }

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Obter informações do usuário
    user_id = get_jwt_identity()
    
    # Log de logout
    security_logger.log_event(
        event_type=SecurityEventType.LOGOUT,
        user_id=str(user_id),
        details={
            'endpoint': 'logout',
            'session_terminated': True
        },
        security_level=SecurityLevel.INFO
    )
    
    # Para JWT stateless, logout é feito no frontend (remover token)
    return jsonify({'msg': 'Logout efetuado.'}), 200

@auth_bp.route('/oauth2/login/<provider>')
@oauth_rate_limit
def oauth2_login(provider):
    """Inicia o fluxo OAuth2 para o provedor especificado."""
    # Log de início de fluxo OAuth
    logging.info(f"Início de fluxo OAuth2: provider={provider}, IP: {request.remote_addr}")
    redirect_uri = url_for('auth.oauth2_callback', provider=provider, _external=True)
    return oauth.create_client(provider).authorize_redirect(redirect_uri)

@auth_bp.route('/oauth2/callback/<provider>')
@oauth_rate_limit
def oauth2_callback(provider):
    """Callback do provedor OAuth2. Cria/atualiza usuário e retorna JWT."""
    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    if provider == 'google':
        userinfo = client.parse_id_token(token)
        provider_id = userinfo.get('sub')
        email = userinfo.get('email')
        username = userinfo.get('name')
    elif provider == 'github':
        resp = client.get('user')
        userinfo = resp.json()
        provider_id = str(userinfo.get('id'))
        email = userinfo.get('email') or userinfo.get('login')
        username = userinfo.get('login')
    else:
        return jsonify({'erro': 'Provedor não suportado.'}), 400
    # Buscar ou criar usuário
    user = User.query.filter_by(provider=provider, provider_id=provider_id).first()
    if not user:
        # Verifica se já existe usuário local com o mesmo email
        user = User.query.filter_by(email=email).first()
        if user:
            user.provider = provider
            user.provider_id = provider_id
        else:
            user = User(username=username, email=email, senha_hash='', ativo=True, provider=provider, provider_id=provider_id)
            db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=user.id)
    
    # Log de login OAuth bem-sucedido
    security_logger.log_event(
        event_type=SecurityEventType.OAUTH_LOGIN,
        user_id=str(user.id),
        username=username,
        details={
            'provider': provider,
            'email': email,
            'endpoint': 'oauth2_callback',
            'user_created': user.provider_id is not None
        },
        security_level=SecurityLevel.INFO
    )
    
    return jsonify({'access_token': access_token, 'user_id': user.id, 'provider': provider}), 200 