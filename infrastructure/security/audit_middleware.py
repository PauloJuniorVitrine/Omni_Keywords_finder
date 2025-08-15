"""
audit_middleware.py

Middleware de Auditoria - Omni Keywords Finder

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 6
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19

Funcionalidades:
- Interceptação automática de requisições
- Logging de ações de usuário
- Captura de metadados de contexto
- Integração com frameworks web
"""

import time
import json
import hashlib
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime
import inspect
import traceback
from dataclasses import dataclass
from enum import Enum

from .advanced_audit import (
    AdvancedAuditSystem, AuditEvent, AuditCategory, AuditLevel,
    audit_system
)

class MiddlewareType(Enum):
    """Tipos de middleware suportados"""
    FLASK = "flask"
    FASTAPI = "fastapi"
    DJANGO = "django"
    GENERIC = "generic"

@dataclass
class RequestContext:
    """Contexto da requisição para auditoria"""
    method: str
    path: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Dict[str, Any]]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None

class AuditMiddleware:
    """
    Middleware de auditoria para interceptação automática
    
    Suporta múltiplos frameworks web e logging automático de ações.
    """
    
    def __init__(self, audit_system: AdvancedAuditSystem = None):
        self.audit_system = audit_system or audit_system
        self.enabled = True
        self.sensitive_paths = [
            "/api/auth/",
            "/api/admin/",
            "/api/users/",
            "/api/config/"
        ]
        self.excluded_paths = [
            "/health",
            "/metrics",
            "/static/",
            "/favicon.ico"
        ]
    
    def should_audit(self, path: str) -> bool:
        """Verificar se o path deve ser auditado"""
        if not self.enabled:
            return False
        
        # Verificar exclusões
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return False
        
        return True
    
    def extract_user_info(self, request) -> Dict[str, Optional[str]]:
        """Extrair informações do usuário da requisição"""
        user_id = None
        session_id = None
        
        # Tentar extrair de diferentes locais
        if hasattr(request, 'user') and request.user:
            if hasattr(request.user, 'id'):
                user_id = str(request.user.id)
            elif hasattr(request.user, 'username'):
                user_id = request.user.username
        
        # Extrair de headers de autenticação
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            # Aqui você pode decodificar o JWT para extrair user_id
            pass
        
        # Extrair session_id
        session_id = request.cookies.get('session_id') or request.headers.get('X-Session-ID')
        
        return {
            'user_id': user_id,
            'session_id': session_id
        }
    
    def extract_request_data(self, request) -> Dict[str, Any]:
        """Extrair dados da requisição"""
        # Headers
        headers = dict(request.headers)
        
        # Remover headers sensíveis
        sensitive_headers = ['authorization', 'cookie', 'value-api-key']
        for header in sensitive_headers:
            if header in headers:
                headers[header] = '[REDACTED]'
        
        # Query parameters
        query_params = dict(request.args) if hasattr(request, 'args') else {}
        
        # Body (apenas para requisições não-GET)
        body = None
        if request.method != 'GET':
            try:
                if hasattr(request, 'json'):
                    body = request.json
                elif hasattr(request, 'form'):
                    body = dict(request.form)
                elif hasattr(request, 'data'):
                    body = request.data.decode('utf-8') if isinstance(request.data, bytes) else request.data
            except Exception:
                body = "[ERROR_PARSING_BODY]"
        
        return {
            'headers': headers,
            'query_params': query_params,
            'body': body
        }
    
    def create_request_context(self, request) -> RequestContext:
        """Criar contexto da requisição"""
        user_info = self.extract_user_info(request)
        request_data = self.extract_request_data(request)
        
        return RequestContext(
            method=request.method,
            path=request.path,
            user_id=user_info['user_id'],
            session_id=user_info['session_id'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            headers=request_data['headers'],
            query_params=request_data['query_params'],
            body=request_data['body'],
            start_time=datetime.now()
        )
    
    def log_request(self, context: RequestContext, response=None, error=None):
        """Log da requisição"""
        if not self.should_audit(context.path):
            return
        
        # Finalizar contexto
        context.end_time = datetime.now()
        context.duration_ms = (context.end_time - context.start_time).total_seconds() * 1000
        
        if response:
            context.status_code = response.status_code if hasattr(response, 'status_code') else 200
        
        if error:
            context.error = str(error)
        
        # Determinar categoria e nível
        category = self._determine_category(context)
        level = self._determine_level(context)
        
        # Criar detalhes
        details = {
            'method': context.method,
            'path': context.path,
            'duration_ms': context.duration_ms,
            'status_code': context.status_code,
            'query_params': context.query_params,
            'headers_count': len(context.headers),
            'body_size': len(json.dumps(context.body)) if context.body else 0
        }
        
        if context.error:
            details['error'] = context.error
        
        # Criar metadados
        metadata = {
            'request_context': {
                'ip_address': context.ip_address,
                'user_agent': context.user_agent,
                'headers': context.headers
            },
            'performance': {
                'duration_ms': context.duration_ms
            }
        }
        
        # Log do evento
        self.audit_system.log_event(
            action=f"{context.method} {context.path}",
            resource=context.path,
            category=category,
            level=level,
            user_id=context.user_id,
            session_id=context.session_id,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            details=details,
            metadata=metadata
        )
    
    def _determine_category(self, context: RequestContext) -> AuditCategory:
        """Determinar categoria do evento"""
        path = context.path.lower()
        
        if '/auth/' in path or '/login' in path or '/logout' in path:
            return AuditCategory.AUTHENTICATION
        
        if '/admin/' in path or '/users/' in path:
            return AuditCategory.AUTHORIZATION
        
        if '/api/' in path:
            return AuditCategory.API_CALL
        
        if '/data/' in path or '/export/' in path:
            return AuditCategory.DATA_ACCESS
        
        if '/config/' in path or '/settings/' in path:
            return AuditCategory.CONFIGURATION_CHANGE
        
        return AuditCategory.USER_ACTION
    
    def _determine_level(self, context: RequestContext) -> AuditLevel:
        """Determinar nível do evento"""
        if context.error:
            return AuditLevel.ERROR
        
        if context.status_code and context.status_code >= 400:
            return AuditLevel.WARNING
        
        # Verificar paths sensíveis
        for sensitive_path in self.sensitive_paths:
            if context.path.startswith(sensitive_path):
                return AuditLevel.SECURITY
        
        return AuditLevel.INFO


class FlaskAuditMiddleware:
    """Middleware específico para Flask"""
    
    def __init__(self, app, audit_system: AdvancedAuditSystem = None):
        self.app = app
        self.audit_middleware = AuditMiddleware(audit_system)
        
        # Registrar middleware
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """Executar antes da requisição"""
        from flask import request, g
        
        if self.audit_middleware.should_audit(request.path):
            context = self.audit_middleware.create_request_context(request)
            g.audit_context = context
    
    def after_request(self, response):
        """Executar após a requisição"""
        from flask import request, g
        
        if hasattr(g, 'audit_context'):
            self.audit_middleware.log_request(g.audit_context, response)
        
        return response
    
    def teardown_request(self, exception):
        """Executar em caso de erro"""
        from flask import g
        
        if exception and hasattr(g, 'audit_context'):
            self.audit_middleware.log_request(g.audit_context, error=exception)


class FastAPIAuditMiddleware:
    """Middleware específico para FastAPI"""
    
    def __init__(self, audit_system: AdvancedAuditSystem = None):
        self.audit_middleware = AuditMiddleware(audit_system)
    
    async def __call__(self, request, call_next):
        """Middleware para FastAPI"""
        if not self.audit_middleware.should_audit(request.url.path):
            return await call_next(request)
        
        # Criar contexto
        context = self.audit_middleware.create_request_context(request)
        
        try:
            # Processar requisição
            response = await call_next(request)
            
            # Log da resposta
            self.audit_middleware.log_request(context, response)
            
            return response
            
        except Exception as e:
            # Log do erro
            self.audit_middleware.log_request(context, error=e)
            raise


def audit_function(
    action: str,
    resource: str,
    category: AuditCategory = AuditCategory.USER_ACTION,
    level: AuditLevel = AuditLevel.INFO
):
    """
    Decorator para auditar funções
    
    Args:
        action: Descrição da ação
        resource: Recurso afetado
        category: Categoria do evento
        level: Nível de severidade
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            error = None
            result = None
            
            try:
                # Executar função
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                error = str(e)
                raise
                
            finally:
                # Calcular duração
                end_time = datetime.now()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                # Extrair informações do contexto
                user_id = None
                session_id = None
                
                # Tentar extrair de argumentos
                for arg in args:
                    if hasattr(arg, 'user_id'):
                        user_id = arg.user_id
                    if hasattr(arg, 'session_id'):
                        session_id = arg.session_id
                
                # Criar detalhes
                details = {
                    'function_name': func.__name__,
                    'module': func.__module__,
                    'duration_ms': duration_ms,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
                
                if error:
                    details['error'] = error
                    level_to_use = AuditLevel.ERROR
                else:
                    level_to_use = level
                
                # Log do evento
                audit_system.log_event(
                    action=action,
                    resource=resource,
                    category=category,
                    level=level_to_use,
                    user_id=user_id,
                    session_id=session_id,
                    details=details,
                    metadata={
                        'function': {
                            'name': func.__name__,
                            'module': func.__module__,
                            'signature': str(inspect.signature(func))
                        },
                        'performance': {
                            'duration_ms': duration_ms
                        }
                    }
                )
        
        return wrapper
    return decorator


def audit_data_access(
    resource: str,
    operation: str = "read",
    sensitive: bool = False
):
    """
    Decorator específico para auditoria de acesso a dados
    
    Args:
        resource: Recurso de dados
        operation: Operação (read, write, delete)
        sensitive: Se os dados são sensíveis
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determinar categoria baseada na operação
            if operation == "write":
                category = AuditCategory.DATA_MODIFICATION
            else:
                category = AuditCategory.DATA_ACCESS
            
            # Determinar nível baseado na sensibilidade
            level = AuditLevel.SECURITY if sensitive else AuditLevel.INFO
            
            # Usar o decorator genérico
            return audit_function(
                action=f"{operation.upper()} {resource}",
                resource=resource,
                category=category,
                level=level
            )(func)(*args, **kwargs)
        
        return wrapper
    return decorator


def audit_configuration_change(resource: str):
    """
    Decorator específico para auditoria de mudanças de configuração
    
    Args:
        resource: Recurso de configuração
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return audit_function(
                action=f"CONFIGURE {resource}",
                resource=resource,
                category=AuditCategory.CONFIGURATION_CHANGE,
                level=AuditLevel.WARNING
            )(func)(*args, **kwargs)
        
        return wrapper
    return decorator


def audit_security_event(
    action: str,
    resource: str,
    critical: bool = False
):
    """
    Decorator específico para auditoria de eventos de segurança
    
    Args:
        action: Ação de segurança
        resource: Recurso afetado
        critical: Se o evento é crítico
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            level = AuditLevel.CRITICAL if critical else AuditLevel.SECURITY
            
            return audit_function(
                action=action,
                resource=resource,
                category=AuditCategory.SECURITY_EVENT,
                level=level
            )(func)(*args, **kwargs)
        
        return wrapper
    return decorator


# Exemplos de uso dos decorators
class ExampleService:
    """Exemplo de serviço com auditoria"""
    
    @audit_function(
        action="CREATE_USER",
        resource="users",
        category=AuditCategory.USER_ACTION,
        level=AuditLevel.INFO
    )
    def create_user(self, user_data):
        # Lógica de criação de usuário
        pass
    
    @audit_data_access(
        resource="user_profiles",
        operation="read",
        sensitive=True
    )
    def get_user_profile(self, user_id):
        # Lógica de leitura de perfil
        pass
    
    @audit_configuration_change("system_settings")
    def update_system_settings(self, settings):
        # Lógica de atualização de configurações
        pass
    
    @audit_security_event(
        action="LOGIN_ATTEMPT",
        resource="authentication",
        critical=False
    )
    def authenticate_user(self, credentials):
        # Lógica de autenticação
        pass


# Função utilitária para configurar middleware
def setup_audit_middleware(app, framework: str = "flask"):
    """
    Configurar middleware de auditoria para diferentes frameworks
    
    Args:
        app: Aplicação web
        framework: Framework utilizado (flask, fastapi, django)
    """
    if framework.lower() == "flask":
        return FlaskAuditMiddleware(app)
    elif framework.lower() == "fastapi":
        return FastAPIAuditMiddleware()
    else:
        raise ValueError(f"Framework não suportado: {framework}")


# Exemplo de configuração para Flask
"""
from flask import Flask
from infrastructure.security.audit_middleware import setup_audit_middleware

app = Flask(__name__)
audit_middleware = setup_audit_middleware(app, "flask")
"""

# Exemplo de configuração para FastAPI
"""
from fastapi import FastAPI
from infrastructure.security.audit_middleware import FastAPIAuditMiddleware

app = FastAPI()
audit_middleware = FastAPIAuditMiddleware()
app.middleware("http")(audit_middleware)
""" 