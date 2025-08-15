from typing import Dict, List, Optional, Any
"""
GraphQL Endpoint - Omni Keywords Finder

Este módulo implementa o endpoint GraphQL principal com autenticação,
middleware de segurança e integração com Flask.

Autor: Sistema Omni Keywords Finder
Data: 2024-12-19
Versão: 1.0.0
"""

from flask import Blueprint, request, jsonify, g
from flask_graphql import GraphQLView
from graphql import GraphQLError
import json
import time
from datetime import datetime
from functools import wraps

# Importa schema
from .graphql_schema import schema

# Importa utilitários de autenticação
from ..security.security_utils_v1 import verificar_token_jwt, obter_usuario_do_token

# Blueprint para GraphQL
graphql_bp = Blueprint('graphql', __name__, url_prefix='/graphql')

# =============================================================================
# MIDDLEWARE DE AUTENTICAÇÃO
# =============================================================================

def require_auth(f):
    """Decorator para requerer autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica token no header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'errors': [{
                    'message': 'Token de autenticação requerido',
                    'extensions': {'code': 'UNAUTHENTICATED'}
                }]
            }), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verifica token
            payload = verificar_token_jwt(token)
            if not payload:
                return jsonify({
                    'errors': [{
                        'message': 'Token inválido',
                        'extensions': {'code': 'UNAUTHENTICATED'}
                    }]
                }), 401
            
            # Obtém usuário
            usuario = obter_usuario_do_token(payload)
            if not usuario:
                return jsonify({
                    'errors': [{
                        'message': 'Usuário não encontrado',
                        'extensions': {'code': 'UNAUTHENTICATED'}
                    }]
                }), 401
            
            # Adiciona usuário ao contexto
            g.current_user = usuario
            
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'errors': [{
                    'message': f'Erro de autenticação: {str(e)}',
                    'extensions': {'code': 'UNAUTHENTICATED'}
                }]
            }), 401
    
    return decorated_function

# =============================================================================
# MIDDLEWARE DE LOGGING
# =============================================================================

def log_graphql_request(f):
    """Decorator para logar requisições GraphQL"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Log da requisição
        request_data = {
            'timestamp': datetime.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'user_agent': request.headers.get('User-Agent'),
            'ip': request.remote_addr,
            'user_id': getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
        }
        
        # Log do body se for POST
        if request.method == 'POST':
            try:
                body = request.get_json()
                if body:
                    request_data['query'] = body.get('query', '')
                    request_data['variables'] = body.get('variables', {})
                    request_data['operation_name'] = body.get('operationName', '')
            except Exception:
                pass
        
        # Executa a função
        response = f(*args, **kwargs)
        
        # Calcula tempo de execução
        execution_time = time.time() - start_time
        request_data['execution_time'] = execution_time
        request_data['status_code'] = response.status_code if hasattr(response, 'status_code') else 200
        
        # Log do resultado
        try:
            from ..models import Log
            from .. import db
            
            log_entry = Log(
                nivel='INFO',
                modulo='graphql',
                mensagem=f"GraphQL Request: {request_data['operation_name'] or 'anonymous'}",
                dados=json.dumps(request_data),
                timestamp=datetime.now()
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            print(f"Erro ao salvar log GraphQL: {e}")
        
        return response
    
    return decorated_function

# =============================================================================
# MIDDLEWARE DE RATE LIMITING
# =============================================================================

def rate_limit_graphql(f):
    """Decorator para rate limiting de GraphQL"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implementação básica de rate limiting
        # Em produção, usar Redis ou similar
        user_id = getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else 'anonymous'
        
        # Aqui você implementaria a lógica de rate limiting
        # Por enquanto, apenas permite todas as requisições
        
        return f(*args, **kwargs)
    
    return decorated_function

# =============================================================================
# CONTEXT PROVIDER
# =============================================================================

def get_context():
    """Fornece contexto para o GraphQL"""
    return {
        'request': request,
        'user': getattr(g, 'current_user', None),
        'headers': dict(request.headers),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
    }

# =============================================================================
# ERROR HANDLER
# =============================================================================

def format_error(error):
    """Formata erros do GraphQL"""
    if isinstance(error, GraphQLError):
        return {
            'message': str(error),
            'locations': [{'line': loc.line, 'column': loc.column} for loc in error.locations] if error.locations else None,
            'path': error.path,
            'extensions': error.extensions
        }
    else:
        return {
            'message': 'Erro interno do servidor',
            'extensions': {'code': 'INTERNAL_SERVER_ERROR'}
        }

# =============================================================================
# ENDPOINTS
# =============================================================================

@graphql_bp.route('/query', methods=['POST'])
@require_auth
@log_graphql_request
@rate_limit_graphql
def graphql_query():
    """Endpoint principal para queries GraphQL"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'errors': [{
                    'message': 'Dados JSON requeridos',
                    'extensions': {'code': 'BAD_REQUEST'}
                }]
            }), 400
        
        query = data.get('query')
        variables = data.get('variables', {})
        operation_name = data.get('operationName')
        
        if not query:
            return jsonify({
                'errors': [{
                    'message': 'Query GraphQL requerida',
                    'extensions': {'code': 'BAD_REQUEST'}
                }]
            }), 400
        
        # Executa query
        result = schema.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            context_value=get_context()
        )
        
        # Prepara resposta
        response_data = {}
        
        if result.data:
            response_data['data'] = result.data
        
        if result.errors:
            response_data['errors'] = [format_error(error) for error in result.errors]
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'errors': [{
                'message': f'Erro interno: {str(e)}',
                'extensions': {'code': 'INTERNAL_SERVER_ERROR'}
            }]
        }), 500

@graphql_bp.route('/schema', methods=['GET'])
def graphql_schema():
    """Endpoint para obter o schema GraphQL"""
    try:
        # Retorna o schema em formato SDL (Schema Definition Language)
        schema_sdl = schema.introspect()
        
        return jsonify({
            'data': {
                '__schema': schema_sdl
            }
        })
        
    except Exception as e:
        return jsonify({
            'errors': [{
                'message': f'Erro ao obter schema: {str(e)}',
                'extensions': {'code': 'INTERNAL_SERVER_ERROR'}
            }]
        }), 500

@graphql_bp.route('/health', methods=['GET'])
def graphql_health():
    """Endpoint de health check para GraphQL"""
    return jsonify({
        'status': 'healthy',
        'service': 'graphql',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# =============================================================================
# VIEW ALTERNATIVA COM GRAPHQL PLAYGROUND
# =============================================================================

class CustomGraphQLView(GraphQLView):
    """View customizada do GraphQL com autenticação"""
    
    def dispatch_request(self, *args, **kwargs):
        # Verifica autenticação
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'errors': [{
                    'message': 'Token de autenticação requerido',
                    'extensions': {'code': 'UNAUTHENTICATED'}
                }]
            }), 401
        
        # Chama método original
        return super().dispatch_request(*args, **kwargs)

# Adiciona view do GraphQL Playground (opcional)
graphql_bp.add_url_rule(
    '/playground',
    view_func=CustomGraphQLView.as_view(
        'graphql_playground',
        schema=schema,
        graphiql=True,  # Habilita GraphQL Playground
        context_value=get_context
    )
)

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def register_graphql_routes(app):
    """Registra as rotas GraphQL na aplicação Flask"""
    app.register_blueprint(graphql_bp)
    
    # Adiciona middleware global para GraphQL
    @app.before_request
    def before_request():
        if request.path.startswith('/graphql'):
            # Middleware específico para GraphQL
            pass
    
    return app 