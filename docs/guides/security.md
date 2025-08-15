# Guia de Segurança

Este documento detalha as estratégias de otimização de segurança do Omni Keywords Finder.

## Autenticação

### 1. JWT

```python
# src/security/jwt.py
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JWTHandler:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.security = HTTPBearer()
        
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Cria token JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
        
    def verify_token(
        self,
        credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> Dict[str, Any]:
        """Verifica token JWT"""
        try:
            token = credentials.credentials
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token expirado"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )
```

### 2. OAuth2

```python
# src/security/oauth2.py
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from src.models.user import User
from src.services.user_service import UserService

class OAuth2Handler:
    def __init__(
        self,
        user_service: UserService,
        token_url: str = "/token",
        access_token_expire_minutes: int = 30
    ):
        self.user_service = user_service
        self.oauth2_scheme = OAuth2PasswordBearer(token_url=token_url)
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )
        self.access_token_expire_minutes = access_token_expire_minutes
        
    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verifica senha"""
        return self.pwd_context.verify(
            plain_password,
            hashed_password
        )
        
    def get_password_hash(self, password: str) -> str:
        """Gera hash da senha"""
        return self.pwd_context.hash(password)
        
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Autentica usuário"""
        user = await self.user_service.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
        
    async def get_current_user(
        self,
        token: str = Security(OAuth2PasswordBearer(token_url="/token"))
    ) -> User:
        """Obtém usuário atual"""
        credentials_exception = HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except jwt.JWTError:
            raise credentials_exception
            
        user = await self.user_service.get_by_email(email)
        if user is None:
            raise credentials_exception
            
        return user
```

## Autorização

### 1. RBAC

```python
# src/security/rbac.py
from typing import Dict, Any, List, Optional
from enum import Enum
from fastapi import HTTPException, Security
from src.models.user import User
from src.security.oauth2 import OAuth2Handler

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Permission(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

class RBACHandler:
    def __init__(self, oauth2_handler: OAuth2Handler):
        self.oauth2_handler = oauth2_handler
        self.role_permissions = {
            Role.ADMIN: [
                Permission.CREATE,
                Permission.READ,
                Permission.UPDATE,
                Permission.DELETE
            ],
            Role.USER: [
                Permission.CREATE,
                Permission.READ,
                Permission.UPDATE
            ],
            Role.GUEST: [
                Permission.READ
            ]
        }
        
    async def check_permission(
        self,
        user: User,
        permission: Permission
    ) -> bool:
        """Verifica permissão"""
        if user.role not in self.role_permissions:
            return False
            
        return permission in self.role_permissions[user.role]
        
    async def require_permission(
        self,
        permission: Permission,
        current_user: User = Security(OAuth2Handler.get_current_user)
    ) -> User:
        """Exige permissão"""
        if not await self.check_permission(current_user, permission):
            raise HTTPException(
                status_code=403,
                detail="Permissão negada"
            )
        return current_user
```

### 2. ACL

```python
# src/security/acl.py
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, Security
from src.models.user import User
from src.models.keyword import Keyword
from src.security.oauth2 import OAuth2Handler

class ACLHandler:
    def __init__(self, oauth2_handler: OAuth2Handler):
        self.oauth2_handler = oauth2_handler
        
    async def check_ownership(
        self,
        user: User,
        resource: Any
    ) -> bool:
        """Verifica propriedade"""
        if isinstance(resource, Keyword):
            return resource.user_id == user.id
        return False
        
    async def require_ownership(
        self,
        resource: Any,
        current_user: User = Security(OAuth2Handler.get_current_user)
    ) -> User:
        """Exige propriedade"""
        if not await self.check_ownership(current_user, resource):
            raise HTTPException(
                status_code=403,
                detail="Acesso negado"
            )
        return current_user
```

## Criptografia

### 1. Dados

```python
# src/security/encryption.py
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64
import os

class EncryptionHandler:
    def __init__(self, key: Optional[str] = None):
        if key:
            self.key = base64.urlsafe_b64encode(key.encode())
        else:
            self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        
    def encrypt(self, data: str) -> str:
        """Criptografa dados"""
        return self.cipher_suite.encrypt(
            data.encode()
        ).decode()
        
    def decrypt(self, data: str) -> str:
        """Descriptografa dados"""
        return self.cipher_suite.decrypt(
            data.encode()
        ).decode()
        
    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Criptografa dicionário"""
        return {
            k: self.encrypt(str(v))
            for k, v in data.items()
        }
        
    def decrypt_dict(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Descriptografa dicionário"""
        return {
            k: self.decrypt(v)
            for k, v in data.items()
        }
```

### 2. Senhas

```python
# src/security/password.py
from typing import Optional
from passlib.context import CryptContext
import secrets
import string

class PasswordHandler:
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )
        
    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verifica senha"""
        return self.pwd_context.verify(
            plain_password,
            hashed_password
        )
        
    def get_password_hash(self, password: str) -> str:
        """Gera hash da senha"""
        return self.pwd_context.hash(password)
        
    def generate_password(
        self,
        length: int = 12,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True
    ) -> str:
        """Gera senha forte"""
        chars = ""
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_lowercase:
            chars += string.ascii_lowercase
        if use_digits:
            chars += string.digits
        if use_special:
            chars += string.punctuation
            
        if not chars:
            raise ValueError("Nenhum tipo de caractere selecionado")
            
        return "".join(
            secrets.choice(chars)
            for _ in range(length)
        )
```

## Validação

### 1. Entrada

```python
# src/security/validation.py
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr, constr
import re

class InputValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida email"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
        
    @staticmethod
    def validate_password(password: str) -> bool:
        """Valida senha"""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True
        
    @staticmethod
    def sanitize_input(data: str) -> str:
        """Sanitiza entrada"""
        return re.sub(r"[<>]", "", data)
```

### 2. Saída

```python
# src/security/output.py
from typing import Dict, Any, Optional
from fastapi import Response
import json

class OutputHandler:
    @staticmethod
    def sanitize_output(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza saída"""
        if isinstance(data, dict):
            return {
                k: OutputHandler.sanitize_output(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [
                OutputHandler.sanitize_output(item)
                for item in data
            ]
        elif isinstance(data, str):
            return data.replace("<", "&lt;").replace(">", "&gt;")
        return data
        
    @staticmethod
    def secure_response(
        data: Dict[str, Any],
        response: Response
    ) -> Response:
        """Configura resposta segura"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        sanitized = OutputHandler.sanitize_output(data)
        response.body = json.dumps(sanitized).encode()
        
        return response
```

## Observações

- Autenticar usuários
- Autorizar ações
- Criptografar dados
- Validar entradas
- Sanitizar saídas
- Proteger rotas
- Monitorar acessos
- Registrar logs
- Atualizar dependências
- Manter documentação 