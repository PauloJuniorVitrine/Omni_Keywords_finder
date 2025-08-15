from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify, g, request
from backend.app.models.user import User
from backend.app.utils.log_event import log_event
from typing import Callable
import datetime

def role_required(*roles: str) -> Callable:
    """
    Decorator para exigir que o usuário autenticado possua pelo menos um dos papéis especificados.
    Exemplo: @role_required('admin', 'gestor')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.ativo:
                log_event('acesso_negado', 'User', usuario=user.username if user else None, detalhes=f'Acesso negado: usuário inexistente ou inativo')
                return jsonify({'erro': 'Acesso negado'}), 403
            user_roles = {r.nome for r in user.roles}
            if not any(r in user_roles for r in roles):
                log_event('acesso_negado', 'User', usuario=user.username, detalhes=f'Acesso negado: requer papel {roles}')
                return jsonify({'erro': 'Permissão insuficiente'}), 403
            g.current_user = user.username
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def permission_required(*permissions: str) -> Callable:
    """
    Decorator para exigir que o usuário autenticado possua pelo menos uma das permissões especificadas.
    Exemplo: @permission_required('gerenciar_usuarios')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.ativo:
                log_event('acesso_negado', 'User', usuario=user.username if user else None, detalhes=f'Acesso negado: usuário inexistente ou inativo')
                return jsonify({'erro': 'Acesso negado'}), 403
            user_permissions = {p.nome for r in user.roles for p in r.permissions}
            if not any(p in user_permissions for p in permissions):
                log_event('acesso_negado', 'User', usuario=user.username, detalhes=f'Acesso negado: requer permissão {permissions}')
                return jsonify({'erro': 'Permissão insuficiente'}), 403
            g.current_user = user.username
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Exemplo de uso:
# @role_required('admin')
# def endpoint_admin(): ...
# @permission_required('gerenciar_usuarios')
# def endpoint_usuarios(): ... 