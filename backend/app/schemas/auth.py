"""
Schemas Pydantic para validação de entrada de autenticação
Implementa validação robusta seguindo OWASP Top 10
"""

from pydantic import BaseModel, validator, EmailStr
from typing import Optional
import re

class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    username: str
    senha: str
    
    @validator('username')
    def validate_username(cls, v):
        """Valida username"""
        if not v:
            raise ValueError('Username é obrigatório')
        
        # Verificar comprimento
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username deve ter entre 3 e 50 caracteres')
        
        # Verificar caracteres permitidos (apenas alfanuméricos, underscore e hífen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username deve conter apenas letras, números, underscore e hífen')
        
        # Verificar se não é apenas números
        if v.isdigit():
            raise ValueError('Username não pode ser apenas números')
        
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
        
        # Verificar caracteres especiais suspeitos
        suspicious_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        for char in suspicious_chars:
            if char in v.lower():
                raise ValueError('Senha contém caracteres não permitidos')
        
        return v

class RegisterRequest(BaseModel):
    """Schema para requisição de registro"""
    username: str
    email: EmailStr
    senha: str
    confirmar_senha: str
    
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
    
    @validator('confirmar_senha')
    def validate_confirmar_senha(cls, v, values):
        """Valida confirmação de senha"""
        if 'senha' in values and v != values['senha']:
            raise ValueError('Senhas não coincidem')
        return v

class OAuthCallbackRequest(BaseModel):
    """Schema para callback OAuth"""
    code: str
    state: Optional[str] = None
    
    @validator('code')
    def validate_code(cls, v):
        """Valida código OAuth"""
        if not v:
            raise ValueError('Código OAuth é obrigatório')
        
        # Verificar comprimento
        if len(v) < 10 or len(v) > 1000:
            raise ValueError('Código OAuth inválido')
        
        # Verificar caracteres permitidos
        if not re.match(r'^[A-Za-z0-9\-._~+/]+=*$', v):
            raise ValueError('Código OAuth contém caracteres inválidos')
        
        return v

class PasswordResetRequest(BaseModel):
    """Schema para reset de senha"""
    email: EmailStr
    
    @validator('email')
    def validate_email(cls, v):
        """Valida email"""
        if not v:
            raise ValueError('Email é obrigatório')
        
        # Validação adicional de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Email inválido')
        
        return v.lower().strip()

class PasswordChangeRequest(BaseModel):
    """Schema para mudança de senha"""
    senha_atual: str
    nova_senha: str
    confirmar_nova_senha: str
    
    @validator('senha_atual')
    def validate_senha_atual(cls, v):
        """Valida senha atual"""
        if not v:
            raise ValueError('Senha atual é obrigatória')
        
        if len(v) < 8 or len(v) > 128:
            raise ValueError('Senha atual inválida')
        
        return v
    
    @validator('nova_senha')
    def validate_nova_senha(cls, v):
        """Valida nova senha"""
        if not v:
            raise ValueError('Nova senha é obrigatória')
        
        # Verificar comprimento mínimo
        if len(v) < 8:
            raise ValueError('Nova senha deve ter pelo menos 8 caracteres')
        
        # Verificar comprimento máximo
        if len(v) > 128:
            raise ValueError('Nova senha deve ter no máximo 128 caracteres')
        
        # Verificar complexidade
        if not re.search(r'[A-Z]', v):
            raise ValueError('Nova senha deve conter pelo menos uma letra maiúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Nova senha deve conter pelo menos uma letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('Nova senha deve conter pelo menos um número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Nova senha deve conter pelo menos um caractere especial')
        
        return v
    
    @validator('confirmar_nova_senha')
    def validate_confirmar_nova_senha(cls, v, values):
        """Valida confirmação da nova senha"""
        if 'nova_senha' in values and v != values['nova_senha']:
            raise ValueError('Senhas não coincidem')
        return v 