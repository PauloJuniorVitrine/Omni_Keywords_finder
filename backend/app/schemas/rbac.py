"""
Schemas Pydantic para validação robusta do RBAC
Implementa validação de entrada seguindo OWASP Top 10 e NIST RBAC Framework
"""

from pydantic import BaseModel, validator, EmailStr, Field
from typing import List, Optional, Dict, Any
import re

class UserCreateRequest(BaseModel):
    """Schema para criação de usuário"""
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=8, max_length=128, description="Senha do usuário")
    roles: List[str] = Field(default=[], description="Lista de roles")
    ativo: bool = Field(default=True, description="Status do usuário")
    
    @validator('username')
    def validate_username(cls, v):
        """Valida username"""
        if not v:
            raise ValueError('Username é obrigatório')
        
        # Verificar comprimento
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username deve ter entre 3 e 50 caracteres')
        
        # Verificar caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username deve conter apenas letras, números, underscore e hífen')
        
        # Verificar se não é apenas números
        if v.isdigit():
            raise ValueError('Username não pode ser apenas números')
        
        # Verificar palavras reservadas
        reserved_words = ['admin', 'root', 'system', 'guest', 'test', 'null', 'undefined']
        if v.lower() in reserved_words:
            raise ValueError('Username não pode ser uma palavra reservada')
        
        return v.strip()
    
    @validator('senha')
    def validate_senha(cls, v):
        """Valida senha"""
        if not v:
            raise ValueError('Senha é obrigatória')
        
        # Verificar comprimento mínimo
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        # Verificar comprimento máximo
        if len(v) > 128:
            raise ValueError('Senha deve ter no máximo 128 caracteres')
        
        # Verificar complexidade
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        
        # Verificar caracteres suspeitos
        suspicious_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        for char in suspicious_chars:
            if char in v.lower():
                raise ValueError('Senha contém caracteres não permitidos')
        
        return v
    
    @validator('roles')
    def validate_roles(cls, v):
        """Valida roles"""
        if not isinstance(v, list):
            raise ValueError('Roles deve ser uma lista')
        
        # Verificar se não há roles duplicadas
        if len(v) != len(set(v)):
            raise ValueError('Roles duplicadas não são permitidas')
        
        # Verificar se roles são válidas
        valid_roles = ['admin', 'gestor', 'usuario', 'analista', 'viewer']
        for role in v:
            if role not in valid_roles:
                raise ValueError(f'Role inválida: {role}. Roles válidas: {valid_roles}')
        
        return v

class UserUpdateRequest(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    senha: Optional[str] = Field(None, min_length=8, max_length=128, description="Nova senha")
    roles: Optional[List[str]] = Field(None, description="Lista de roles")
    ativo: Optional[bool] = Field(None, description="Status do usuário")
    
    @validator('senha')
    def validate_senha(cls, v):
        """Valida senha se fornecida"""
        if v is None:
            return v
        
        # Verificar comprimento mínimo
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        # Verificar comprimento máximo
        if len(v) > 128:
            raise ValueError('Senha deve ter no máximo 128 caracteres')
        
        # Verificar complexidade
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        
        return v
    
    @validator('roles')
    def validate_roles(cls, v):
        """Valida roles se fornecidas"""
        if v is None:
            return v
        
        if not isinstance(v, list):
            raise ValueError('Roles deve ser uma lista')
        
        # Verificar se não há roles duplicadas
        if len(v) != len(set(v)):
            raise ValueError('Roles duplicadas não são permitidas')
        
        # Verificar se roles são válidas
        valid_roles = ['admin', 'gestor', 'usuario', 'analista', 'viewer']
        for role in v:
            if role not in valid_roles:
                raise ValueError(f'Role inválida: {role}. Roles válidas: {valid_roles}')
        
        return v

class RoleCreateRequest(BaseModel):
    """Schema para criação de role"""
    nome: str = Field(..., min_length=2, max_length=50, description="Nome da role")
    descricao: Optional[str] = Field(None, max_length=200, description="Descrição da role")
    permissoes: List[str] = Field(default=[], description="Lista de permissões")
    
    @validator('nome')
    def validate_nome(cls, v):
        """Valida nome da role"""
        if not v:
            raise ValueError('Nome da role é obrigatório')
        
        # Verificar comprimento
        if len(v) < 2 or len(v) > 50:
            raise ValueError('Nome da role deve ter entre 2 e 50 caracteres')
        
        # Verificar caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Nome da role deve conter apenas letras, números, underscore e hífen')
        
        # Verificar palavras reservadas
        reserved_words = ['admin', 'root', 'system', 'guest', 'test', 'null', 'undefined']
        if v.lower() in reserved_words:
            raise ValueError('Nome da role não pode ser uma palavra reservada')
        
        return v.strip()
    
    @validator('permissoes')
    def validate_permissoes(cls, v):
        """Valida permissões"""
        if not isinstance(v, list):
            raise ValueError('Permissões deve ser uma lista')
        
        # Verificar se não há permissões duplicadas
        if len(v) != len(set(v)):
            raise ValueError('Permissões duplicadas não são permitidas')
        
        # Verificar se permissões são válidas
        valid_permissions = [
            'user:read', 'user:write', 'user:delete',
            'role:read', 'role:write', 'role:delete',
            'permission:read', 'permission:write', 'permission:delete',
            'execucao:read', 'execucao:write', 'execucao:delete',
            'keyword:read', 'keyword:write', 'keyword:delete',
            'report:read', 'report:write', 'report:delete',
            'admin:all'
        ]
        
        for perm in v:
            if perm not in valid_permissions:
                raise ValueError(f'Permissão inválida: {perm}. Permissões válidas: {valid_permissions}')
        
        return v

class RoleUpdateRequest(BaseModel):
    """Schema para atualização de role"""
    descricao: Optional[str] = Field(None, max_length=200, description="Descrição da role")
    permissoes: Optional[List[str]] = Field(None, description="Lista de permissões")
    
    @validator('permissoes')
    def validate_permissoes(cls, v):
        """Valida permissões se fornecidas"""
        if v is None:
            return v
        
        if not isinstance(v, list):
            raise ValueError('Permissões deve ser uma lista')
        
        # Verificar se não há permissões duplicadas
        if len(v) != len(set(v)):
            raise ValueError('Permissões duplicadas não são permitidas')
        
        # Verificar se permissões são válidas
        valid_permissions = [
            'user:read', 'user:write', 'user:delete',
            'role:read', 'role:write', 'role:delete',
            'permission:read', 'permission:write', 'permission:delete',
            'execucao:read', 'execucao:write', 'execucao:delete',
            'keyword:read', 'keyword:write', 'keyword:delete',
            'report:read', 'report:write', 'report:delete',
            'admin:all'
        ]
        
        for perm in v:
            if perm not in valid_permissions:
                raise ValueError(f'Permissão inválida: {perm}. Permissões válidas: {valid_permissions}')
        
        return v

class PermissionCreateRequest(BaseModel):
    """Schema para criação de permissão"""
    nome: str = Field(..., min_length=3, max_length=50, description="Nome da permissão")
    descricao: Optional[str] = Field(None, max_length=200, description="Descrição da permissão")
    
    @validator('nome')
    def validate_nome(cls, v):
        """Valida nome da permissão"""
        if not v:
            raise ValueError('Nome da permissão é obrigatório')
        
        # Verificar comprimento
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Nome da permissão deve ter entre 3 e 50 caracteres')
        
        # Verificar formato (resource:action)
        if ':' not in v:
            raise ValueError('Nome da permissão deve seguir o formato: resource:action')
        
        resource, action = v.split(':', 1)
        
        # Verificar resource
        valid_resources = ['user', 'role', 'permission', 'execucao', 'keyword', 'report', 'admin']
        if resource not in valid_resources:
            raise ValueError(f'Resource inválido: {resource}. Resources válidos: {valid_resources}')
        
        # Verificar action
        valid_actions = ['read', 'write', 'delete', 'all']
        if action not in valid_actions:
            raise ValueError(f'Action inválida: {action}. Actions válidas: {valid_actions}')
        
        return v.strip()

class PermissionUpdateRequest(BaseModel):
    """Schema para atualização de permissão"""
    descricao: Optional[str] = Field(None, max_length=200, description="Descrição da permissão")

class UserIDRequest(BaseModel):
    """Schema para validação de ID de usuário"""
    user_id: int = Field(..., gt=0, description="ID do usuário")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Valida ID do usuário"""
        if v <= 0:
            raise ValueError('ID do usuário deve ser maior que zero')
        return v

class RoleIDRequest(BaseModel):
    """Schema para validação de ID de role"""
    role_id: int = Field(..., gt=0, description="ID da role")
    
    @validator('role_id')
    def validate_role_id(cls, v):
        """Valida ID da role"""
        if v <= 0:
            raise ValueError('ID da role deve ser maior que zero')
        return v

class PermissionIDRequest(BaseModel):
    """Schema para validação de ID de permissão"""
    perm_id: int = Field(..., gt=0, description="ID da permissão")
    
    @validator('perm_id')
    def validate_perm_id(cls, v):
        """Valida ID da permissão"""
        if v <= 0:
            raise ValueError('ID da permissão deve ser maior que zero')
        return v 