from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.models.user import User
from backend.app.models.role import Role
from backend.app.models.permission import Permission
from backend.app.models import db
from werkzeug.security import generate_password_hash
from backend.app.utils.log_event import log_event
from backend.app.utils.auth_utils import role_required
from backend.app.schemas.rbac import (
    UserCreateRequest, UserUpdateRequest, RoleCreateRequest, RoleUpdateRequest,
    PermissionCreateRequest, PermissionUpdateRequest, UserIDRequest, RoleIDRequest, PermissionIDRequest
)
from pydantic import ValidationError
from typing import Dict, List, Optional, Any
import re
import html
import unicodedata

rbac_bp = Blueprint('rbac', __name__, url_prefix='/api/rbac')

def sanitizar_string(texto: str, max_length: int = 255, allow_html: bool = False) -> str:
    """
    Sanitiza string removendo caracteres perigosos e normalizando.
    
    Args:
        texto: String a ser sanitizada
        max_length: Comprimento máximo permitido
        allow_html: Se permite HTML (não recomendado)
        
    Returns:
        String sanitizada
    """
    if not texto:
        return ""
    
    # Converter para string se não for
    texto = str(texto)
    
    # Normalizar unicode
    texto = unicodedata.normalize('NFKC', texto)
    
    # Remover caracteres de controle exceto tab, newline, carriage return
    texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texto)
    
    # Remover HTML se não permitido
    if not allow_html:
        texto = html.escape(texto)
    
    # Remover espaços extras
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    # Limitar comprimento
    if len(texto) > max_length:
        texto = texto[:max_length]
    
    return texto

def sanitizar_email(email: str) -> str:
    """
    Sanitiza email removendo caracteres perigosos.
    
    Args:
        email: Email a ser sanitizado
        
    Returns:
        Email sanitizado
    """
    if not email:
        return ""
    
    email = str(email).lower().strip()
    
    # Remover caracteres perigosos
    email = re.sub(r'[^\w@.-]', '', email)
    
    # Validar formato básico
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Formato de email inválido")
    
    return email

def sanitizar_username(username: str) -> str:
    """
    Sanitiza username removendo caracteres perigosos.
    
    Args:
        username: Username a ser sanitizado
        
    Returns:
        Username sanitizado
    """
    if not username:
        return ""
    
    username = str(username).strip()
    
    # Remover caracteres especiais, manter apenas alfanuméricos e underscore
    username = re.sub(r'[^\w]', '', username)
    
    # Limitar comprimento
    if len(username) > 64:
        username = username[:64]
    
    # Validar formato
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,63}$', username):
        raise ValueError("Username deve começar com letra e conter apenas letras, números e underscore")
    
    return username

def sanitizar_role_name(role_name: str) -> str:
    """
    Sanitiza nome de papel removendo caracteres perigosos.
    
    Args:
        role_name: Nome do papel a ser sanitizado
        
    Returns:
        Nome sanitizado
    """
    if not role_name:
        return ""
    
    role_name = str(role_name).strip()
    
    # Remover caracteres especiais, manter apenas alfanuméricos e hífen
    role_name = re.sub(r'[^\w-]', '', role_name)
    
    # Limitar comprimento
    if len(role_name) > 64:
        role_name = role_name[:64]
    
    # Validar formato
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]{1,63}$', role_name):
        raise ValueError("Nome do papel deve começar com letra e conter apenas letras, números, underscore e hífen")
    
    return role_name

def sanitizar_permission_name(permission_name: str) -> str:
    """
    Sanitiza nome de permissão removendo caracteres perigosos.
    
    Args:
        permission_name: Nome da permissão a ser sanitizada
        
    Returns:
        Nome sanitizado
    """
    if not permission_name:
        return ""
    
    permission_name = str(permission_name).strip()
    
    # Remover caracteres especiais, manter apenas alfanuméricos e underscore
    permission_name = re.sub(r'[^\w]', '', permission_name)
    
    # Limitar comprimento
    if len(permission_name) > 64:
        permission_name = permission_name[:64]
    
    # Validar formato
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{1,63}$', permission_name):
        raise ValueError("Nome da permissão deve começar com letra e conter apenas letras, números e underscore")
    
    return permission_name

def sanitizar_lista_strings(lista: List[str], sanitizer_func, **kwargs) -> List[str]:
    """
    Sanitiza lista de strings usando função específica.
    
    Args:
        lista: Lista de strings a ser sanitizada
        sanitizer_func: Função de sanitização a ser aplicada
        **kwargs: Argumentos adicionais para a função de sanitização
        
    Returns:
        Lista sanitizada
    """
    if not lista:
        return []
    
    resultado = []
    for item in lista:
        try:
            item_sanitizado = sanitizer_func(item, **kwargs)
            if item_sanitizado:
                resultado.append(item_sanitizado)
        except ValueError as e:
            # Log do erro mas continua processando outros itens
            print(f"Erro ao sanitizar item '{item}': {e}")
            continue
    
    return resultado

def verificar_integridade_referencial_user(user_id: int) -> Dict[str, Any]:
    """
    Verifica integridade referencial antes de excluir usuário.
    
    Args:
        user_id: ID do usuário a ser verificado
        
    Returns:
        Dict com informações sobre dependências encontradas
    """
    dependencias = {
        'execucoes': 0,
        'audit_logs': 0,
        'is_last_admin': False,
        'can_delete': True,
        'erro': None
    }
    
    try:
        # Verificar execuções
        try:
            from backend.app.models.execucao import Execucao
            dependencias['execucoes'] = Execucao.query.filter_by(usuario_id=user_id).count()
        except ImportError:
            pass
        
        # Verificar logs de auditoria
        try:
            from backend.app.models.audit_log import AuditLog
            dependencias['audit_logs'] = AuditLog.query.filter_by(usuario_id=user_id).count()
        except ImportError:
            pass
        
        # Verificar se é último admin
        user = User.query.get(user_id)
        if user and 'admin' in [r.nome for r in user.roles]:
            admin_users_count = User.query.join(User.roles).filter(Role.nome == 'admin').count()
            dependencias['is_last_admin'] = admin_users_count <= 1
        
        # Determinar se pode excluir
        if dependencias['execucoes'] > 0:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Usuário possui execuções associadas'
        elif dependencias['audit_logs'] > 0:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Usuário possui logs de auditoria'
        elif dependencias['is_last_admin']:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Último usuário administrador'
            
    except Exception as e:
        dependencias['can_delete'] = False
        dependencias['erro'] = f'Erro na verificação: {str(e)}'
    
    return dependencias

def verificar_integridade_referencial_role(role_id: int) -> Dict[str, Any]:
    """
    Verifica integridade referencial antes de excluir papel.
    
    Args:
        role_id: ID do papel a ser verificado
        
    Returns:
        Dict com informações sobre dependências encontradas
    """
    dependencias = {
        'users': 0,
        'audit_logs': 0,
        'is_critical': False,
        'can_delete': True,
        'erro': None
    }
    
    try:
        role = Role.query.get(role_id)
        if not role:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Papel não encontrado'
            return dependencias
        
        # Verificar usuários associados
        dependencias['users'] = len(role.users)
        
        # Verificar se é papel crítico
        roles_criticos = ['admin', 'gestor', 'usuario']
        dependencias['is_critical'] = role.nome in roles_criticos
        
        # Verificar logs de auditoria
        try:
            from backend.app.models.audit_log import AuditLog
            dependencias['audit_logs'] = AuditLog.query.filter_by(entidade='Role', entidade_id=role_id).count()
        except ImportError:
            pass
        
        # Determinar se pode excluir
        if dependencias['users'] > 0:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Papel possui usuários associados'
        elif dependencias['is_critical']:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Papel crítico do sistema'
        elif dependencias['audit_logs'] > 0:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Papel possui logs de auditoria'
            
    except Exception as e:
        dependencias['can_delete'] = False
        dependencias['erro'] = f'Erro na verificação: {str(e)}'
    
    return dependencias

def verificar_integridade_referencial_permission(permission_id: int) -> Dict[str, Any]:
    """
    Verifica integridade referencial antes de excluir permissão.
    
    Args:
        permission_id: ID da permissão a ser verificada
        
    Returns:
        Dict com informações sobre dependências encontradas
    """
    dependencias = {
        'roles': 0,
        'audit_logs': 0,
        'is_critical': False,
        'can_delete': True,
        'erro': None
    }
    
    try:
        permission = Permission.query.get(permission_id)
        if not permission:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Permissão não encontrada'
            return dependencias
        
        # Verificar roles associados
        dependencias['roles'] = len(permission.roles)
        
        # Verificar se é permissão crítica
        permissoes_criticas = ['read', 'write', 'delete', 'admin']
        dependencias['is_critical'] = permission.nome in permissoes_criticas
        
        # Verificar logs de auditoria
        try:
            from backend.app.models.audit_log import AuditLog
            dependencias['audit_logs'] = AuditLog.query.filter_by(entidade='Permission', entidade_id=permission_id).count()
        except ImportError:
            pass
        
        # Determinar se pode excluir
        if dependencias['roles'] > 0:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Permissão possui papéis associados'
        elif dependencias['is_critical']:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Permissão crítica do sistema'
        elif dependencias['audit_logs'] > 0:
            dependencias['can_delete'] = False
            dependencias['erro'] = 'Permissão possui logs de auditoria'
            
    except Exception as e:
        dependencias['can_delete'] = False
        dependencias['erro'] = f'Erro na verificação: {str(e)}'
    
    return dependencias

# Usuários
@rbac_bp.route('/usuarios', methods=['GET'])
@role_required('admin', 'gestor')
def listar_usuarios():
    usuarios = User.query.all()
    return jsonify([
        {
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'ativo': u.ativo,
            'roles': [r.nome for r in u.roles]
        } for u in usuarios
    ])

@rbac_bp.route('/usuarios', methods=['POST'])
@role_required('admin')
def criar_usuario():
    try:
        # Validar entrada com Pydantic
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        # Sanitizar dados de entrada
        try:
            if 'username' in data:
                data['username'] = sanitizar_username(data['username'])
            if 'email' in data:
                data['email'] = sanitizar_email(data['email'])
            if 'roles' in data and isinstance(data['roles'], list):
                data['roles'] = sanitizar_lista_strings(data['roles'], sanitizar_role_name)
        except ValueError as e:
            return jsonify({'erro': 'Dados inválidos após sanitização', 'detalhes': str(e)}), 400
        
        user_data = UserCreateRequest(**data)
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=user_data.username).first():
            return jsonify({'erro': 'Usuário já existe'}), 409
        
        if User.query.filter_by(email=user_data.email).first():
            return jsonify({'erro': 'Email já está em uso'}), 409
        
        # Criar usuário
        user = User(
            username=user_data.username,
            email=user_data.email,
            senha_hash=generate_password_hash(user_data.senha),
            ativo=user_data.ativo
        )
        
        # Adicionar roles
        for role_name in user_data.roles:
            role = Role.query.filter_by(nome=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        
        log_event('criação', 'User', id_referencia=user.id, usuario=user_data.username, 
                 detalhes='Usuário criado com validação robusta e sanitização')
        
        return jsonify({
            'id': user.id, 
            'username': user.username,
            'email': user.email,
            'ativo': user.ativo,
            'roles': [r.nome for r in user.roles]
        }), 201
        
    except ValidationError as e:
        return jsonify({'erro': 'Dados inválidos', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'User', detalhes=f'Erro ao criar usuário: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@rbac_bp.route('/usuarios/<int:user_id>', methods=['PUT'])
@role_required('admin')
def editar_usuario(user_id):
    try:
        # Validar ID do usuário
        user_id_data = UserIDRequest(user_id=user_id)
        
        # Buscar usuário
        user = User.query.get_or_404(user_id_data.user_id)
        
        # Validar dados de entrada
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        # Sanitizar dados de entrada
        try:
            if 'email' in data:
                data['email'] = sanitizar_email(data['email'])
            if 'roles' in data and isinstance(data['roles'], list):
                data['roles'] = sanitizar_lista_strings(data['roles'], sanitizar_role_name)
        except ValueError as e:
            return jsonify({'erro': 'Dados inválidos após sanitização', 'detalhes': str(e)}), 400
        
        user_data = UserUpdateRequest(**data)
        
        # Atualizar campos se fornecidos
        if user_data.email is not None:
            # Verificar se email já está em uso por outro usuário
            existing_user = User.query.filter_by(email=user_data.email).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'erro': 'Email já está em uso'}), 409
            user.email = user_data.email
        
        if user_data.senha is not None:
            user.senha_hash = generate_password_hash(user_data.senha)
        
        if user_data.ativo is not None:
            user.ativo = user_data.ativo
        
        if user_data.roles is not None:
            user.roles.clear()
            for role_name in user_data.roles:
                role = Role.query.filter_by(nome=role_name).first()
                if role:
                    user.roles.append(role)
        
        db.session.commit()
        
        log_event('alteração', 'User', id_referencia=user.id, usuario=user.username, 
                 detalhes='Usuário editado com validação robusta e sanitização')
        
        return jsonify({
            'id': user.id, 
            'username': user.username,
            'email': user.email,
            'ativo': user.ativo,
            'roles': [r.nome for r in user.roles]
        })
        
    except ValidationError as e:
        return jsonify({'erro': 'Dados inválidos', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'User', id_referencia=user_id, detalhes=f'Erro ao editar usuário: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@rbac_bp.route('/usuarios/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def remover_usuario(user_id):
    try:
        # Validar ID do usuário
        user_id_data = UserIDRequest(user_id=user_id)
        
        # Buscar usuário
        user = User.query.get_or_404(user_id_data.user_id)
        
        # Verificar integridade referencial
        dependencias = verificar_integridade_referencial_user(user.id)
        
        if not dependencias['can_delete']:
            return jsonify({
                'erro': 'Não é possível excluir usuário',
                'detalhes': dependencias['erro'],
                'dependencias': {
                    'execucoes': dependencias['execucoes'],
                    'audit_logs': dependencias['audit_logs'],
                    'is_last_admin': dependencias['is_last_admin']
                },
                'sugestao': 'Verifique as dependências antes da exclusão'
            }), 409
        
        # Remover associações com roles
        user.roles.clear()
        
        # Excluir usuário
        db.session.delete(user)
        db.session.commit()
        
        log_event('deleção', 'User', id_referencia=user.id, usuario=user.username, 
                 detalhes='Usuário removido com verificação de integridade referencial')
        
        return jsonify({
            'mensagem': 'Usuário removido com sucesso',
            'id': user_id,
            'username': user.username
        }), 200
        
    except ValidationError as e:
        return jsonify({'erro': 'ID de usuário inválido', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'User', id_referencia=user_id, 
                 detalhes=f'Erro ao remover usuário: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# Papéis
@rbac_bp.route('/papeis', methods=['GET'])
@role_required('admin', 'gestor')
def listar_papeis():
    papeis = Role.query.all()
    return jsonify([
        {
            'id': r.id,
            'nome': r.nome,
            'descricao': r.descricao,
            'permissoes': [p.nome for p in r.permissions]
        } for r in papeis
    ])

@rbac_bp.route('/papeis', methods=['POST'])
@role_required('admin')
def criar_papel():
    try:
        # Validar entrada com Pydantic
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        # Sanitizar dados de entrada
        try:
            if 'nome' in data:
                data['nome'] = sanitizar_role_name(data['nome'])
            if 'descricao' in data:
                data['descricao'] = sanitizar_string(data['descricao'], max_length=255)
            if 'permissoes' in data and isinstance(data['permissoes'], list):
                data['permissoes'] = sanitizar_lista_strings(data['permissoes'], sanitizar_permission_name)
        except ValueError as e:
            return jsonify({'erro': 'Dados inválidos após sanitização', 'detalhes': str(e)}), 400
        
        role_data = RoleCreateRequest(**data)
        
        # Verificar se role já existe
        if Role.query.filter_by(nome=role_data.nome).first():
            return jsonify({'erro': 'Papel já existe'}), 409
        
        # Criar role
        papel = Role(nome=role_data.nome, descricao=role_data.descricao)
        
        # Adicionar permissões
        for perm_name in role_data.permissoes:
            perm = Permission.query.filter_by(nome=perm_name).first()
            if perm:
                papel.permissions.append(perm)
        
        db.session.add(papel)
        db.session.commit()
        
        log_event('criação', 'Role', id_referencia=papel.id, 
                 detalhes='Papel criado com validação robusta e sanitização')
        
        return jsonify({
            'id': papel.id, 
            'nome': papel.nome,
            'descricao': papel.descricao,
            'permissoes': [p.nome for p in papel.permissions]
        }), 201
        
    except ValidationError as e:
        return jsonify({'erro': 'Dados inválidos', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'Role', detalhes=f'Erro ao criar papel: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@rbac_bp.route('/papeis/<int:role_id>', methods=['PUT'])
@role_required('admin')
def editar_papel(role_id):
    try:
        # Validar ID do papel
        role_id_data = RoleIDRequest(role_id=role_id)
        
        # Buscar papel
        papel = Role.query.get_or_404(role_id_data.role_id)
        
        # Validar dados de entrada
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        # Sanitizar dados de entrada
        try:
            if 'descricao' in data:
                data['descricao'] = sanitizar_string(data['descricao'], max_length=255)
            if 'permissoes' in data and isinstance(data['permissoes'], list):
                data['permissoes'] = sanitizar_lista_strings(data['permissoes'], sanitizar_permission_name)
        except ValueError as e:
            return jsonify({'erro': 'Dados inválidos após sanitização', 'detalhes': str(e)}), 400
        
        # Atualizar campos se fornecidos
        if 'descricao' in data:
            papel.descricao = data['descricao']
        
        if 'permissoes' in data:
            papel.permissions.clear()
            for perm_name in data['permissoes']:
                perm = Permission.query.filter_by(nome=perm_name).first()
                if perm:
                    papel.permissions.append(perm)
        
        db.session.commit()
        
        log_event('alteração', 'Role', id_referencia=papel.id, 
                 detalhes='Papel editado com validação robusta e sanitização')
        
        return jsonify({
            'id': papel.id, 
            'nome': papel.nome,
            'descricao': papel.descricao,
            'permissoes': [p.nome for p in papel.permissions]
        })
        
    except ValidationError as e:
        return jsonify({'erro': 'ID de papel inválido', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'Role', id_referencia=role_id, detalhes=f'Erro ao editar papel: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@rbac_bp.route('/papeis/<int:role_id>', methods=['DELETE'])
@role_required('admin')
def remover_papel(role_id):
    try:
        # Validar ID do papel
        role_id_data = RoleIDRequest(role_id=role_id)
        
        # Buscar papel
        papel = Role.query.get_or_404(role_id_data.role_id)
        
        # Verificar integridade referencial
        dependencias = verificar_integridade_referencial_role(papel.id)
        
        if not dependencias['can_delete']:
            return jsonify({
                'erro': 'Não é possível excluir papel',
                'detalhes': dependencias['erro'],
                'dependencias': {
                    'users': dependencias['users'],
                    'audit_logs': dependencias['audit_logs'],
                    'is_critical': dependencias['is_critical']
                },
                'sugestao': 'Verifique as dependências antes da exclusão'
            }), 409
        
        # Remover associações com permissões
        papel.permissions.clear()
        
        # Excluir papel
        db.session.delete(papel)
        db.session.commit()
        
        log_event('deleção', 'Role', id_referencia=papel.id, 
                 detalhes='Papel removido com verificação de integridade referencial')
        
        return jsonify({
            'mensagem': 'Papel removido com sucesso',
            'id': role_id,
            'nome': papel.nome
        }), 200
        
    except ValidationError as e:
        return jsonify({'erro': 'ID de papel inválido', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'Role', id_referencia=role_id, 
                 detalhes=f'Erro ao remover papel: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# Permissões
@rbac_bp.route('/permissoes', methods=['GET'])
@role_required('admin', 'gestor')
def listar_permissoes():
    permissoes = Permission.query.all()
    return jsonify([
        {
            'id': p.id,
            'nome': p.nome,
            'descricao': p.descricao
        } for p in permissoes
    ])

@rbac_bp.route('/permissoes', methods=['POST'])
@role_required('admin')
def criar_permissao():
    try:
        # Validar entrada
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        # Sanitizar dados de entrada
        try:
            if 'nome' in data:
                data['nome'] = sanitizar_permission_name(data['nome'])
            if 'descricao' in data:
                data['descricao'] = sanitizar_string(data['descricao'], max_length=255)
        except ValueError as e:
            return jsonify({'erro': 'Dados inválidos após sanitização', 'detalhes': str(e)}), 400
        
        nome = data.get('nome')
        descricao = data.get('descricao')
        
        if not nome:
            return jsonify({'erro': 'nome é obrigatório'}), 400
        
        if Permission.query.filter_by(nome=nome).first():
            return jsonify({'erro': 'Permissão já existe'}), 409
        
        perm = Permission(nome=nome, descricao=descricao)
        db.session.add(perm)
        db.session.commit()
        
        log_event('criação', 'Permission', id_referencia=perm.id, 
                 detalhes='Permissão criada com validação robusta e sanitização')
        
        return jsonify({
            'id': perm.id, 
            'nome': perm.nome,
            'descricao': perm.descricao
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'Permission', detalhes=f'Erro ao criar permissão: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@rbac_bp.route('/permissoes/<int:perm_id>', methods=['PUT'])
@role_required('admin')
def editar_permissao(perm_id):
    try:
        # Validar ID da permissão
        perm_id_data = PermissionIDRequest(permission_id=perm_id)
        
        # Buscar permissão
        perm = Permission.query.get_or_404(perm_id_data.permission_id)
        
        # Validar dados de entrada
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        # Sanitizar dados de entrada
        try:
            if 'descricao' in data:
                data['descricao'] = sanitizar_string(data['descricao'], max_length=255)
        except ValueError as e:
            return jsonify({'erro': 'Dados inválidos após sanitização', 'detalhes': str(e)}), 400
        
        # Atualizar campos se fornecidos
        if 'descricao' in data:
            perm.descricao = data['descricao']
        
        db.session.commit()
        
        log_event('alteração', 'Permission', id_referencia=perm.id, 
                 detalhes='Permissão editada com validação robusta e sanitização')
        
        return jsonify({
            'id': perm.id, 
            'nome': perm.nome,
            'descricao': perm.descricao
        })
        
    except ValidationError as e:
        return jsonify({'erro': 'ID de permissão inválido', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'Permission', id_referencia=perm_id, detalhes=f'Erro ao editar permissão: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@rbac_bp.route('/permissoes/<int:perm_id>', methods=['DELETE'])
@role_required('admin')
def remover_permissao(perm_id):
    try:
        # Validar ID da permissão
        perm_id_data = PermissionIDRequest(permission_id=perm_id)
        
        # Buscar permissão
        permissao = Permission.query.get_or_404(perm_id_data.permission_id)
        
        # Verificar integridade referencial
        dependencias = verificar_integridade_referencial_permission(permissao.id)
        
        if not dependencias['can_delete']:
            return jsonify({
                'erro': 'Não é possível excluir permissão',
                'detalhes': dependencias['erro'],
                'dependencias': {
                    'roles': dependencias['roles'],
                    'audit_logs': dependencias['audit_logs'],
                    'is_critical': dependencias['is_critical']
                },
                'sugestao': 'Verifique as dependências antes da exclusão'
            }), 409
        
        # Excluir permissão
        db.session.delete(permissao)
        db.session.commit()
        
        log_event('deleção', 'Permission', id_referencia=permissao.id, 
                 detalhes='Permissão removida com verificação de integridade referencial')
        
        return jsonify({
            'mensagem': 'Permissão removida com sucesso',
            'id': perm_id,
            'nome': permissao.nome
        }), 200
        
    except ValidationError as e:
        return jsonify({'erro': 'ID de permissão inválido', 'detalhes': e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        log_event('erro', 'Permission', id_referencia=perm_id, 
                 detalhes=f'Erro ao remover permissão: {str(e)}')
        return jsonify({'erro': 'Erro interno do servidor'}), 500 