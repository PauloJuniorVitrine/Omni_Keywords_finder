# Segurança e Gestão de Segredos

## Objetivo
Garantir que nenhum segredo sensível (senhas, tokens, chaves de API) seja exposto em código, logs ou arquivos de configuração versionados.

## Integração Recomendada
- Utilize HashiCorp Vault, AWS Secrets Manager ou equivalente para armazenar segredos.
- Configure as variáveis de ambiente:
  - `VAULT_ADDR`: URL do Vault
  - `VAULT_TOKEN`: Token de acesso (NUNCA versionar)

## Exemplo de Uso
```python
from infrastructure.security.vault_client import VaultClient
vault = VaultClient()
senha_db = vault.get_secret('secret/data/db', 'password')
```

## Boas Práticas
- Nunca exponha segredos reais em `.env`, `.env.example`, código ou logs.
- Faça rotação periódica de tokens e senhas.
- Restrinja acesso ao Vault apenas a serviços/automações autorizadas.
- Audite acessos e alterações de segredos.

## Observações
- Para ambientes de produção, utilize autenticação forte (AppRole, JWT, etc).
- Em desenvolvimento, use apenas segredos mock ou tokens temporários.

# Guia de Segurança

Este documento detalha as práticas de segurança do Omni Keywords Finder.

## Autenticação

### 1. OAuth2

```python
# infrastructure/security/oauth2.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class OAuth2Handler:
    def __init__(self, settings: Settings):
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
    
    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> User:
        user = await self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user
    
    async def create_access_token(
        self,
        data: dict
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            seconds=settings.jwt_expiration
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            self.secret,
            algorithm=self.algorithm
        )
```

### 2. 2FA

```python
# infrastructure/security/2fa.py
import pyotp
import qrcode
from config.settings import Settings

class TwoFactorAuth:
    def __init__(self, settings: Settings):
        self.secret = pyotp.random_base32()
    
    def generate_secret(self) -> str:
        return self.secret
    
    def verify_code(self, code: str) -> bool:
        totp = pyotp.TOTP(self.secret)
        return totp.verify(code)
    
    def generate_qr_code(self, username: str) -> bytes:
        totp = pyotp.TOTP(self.secret)
        provisioning_uri = totp.provisioning_uri(
            username,
            issuer_name="Omni Keywords Finder"
        )
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img.getvalue()
```

## Autorização

### 1. RBAC

```python
# infrastructure/security/rbac.py
from enum import Enum
from typing import List, Set

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class Permission(str, Enum):
    CREATE_KEYWORD = "create:keyword"
    READ_KEYWORD = "read:keyword"
    UPDATE_KEYWORD = "update:keyword"
    DELETE_KEYWORD = "delete:keyword"
    MANAGE_USERS = "manage:users"

class RoleBasedAccess:
    def __init__(self):
        self.role_permissions = {
            Role.ADMIN: {
                Permission.CREATE_KEYWORD,
                Permission.READ_KEYWORD,
                Permission.UPDATE_KEYWORD,
                Permission.DELETE_KEYWORD,
                Permission.MANAGE_USERS
            },
            Role.USER: {
                Permission.CREATE_KEYWORD,
                Permission.READ_KEYWORD,
                Permission.UPDATE_KEYWORD
            },
            Role.READONLY: {
                Permission.READ_KEYWORD
            }
        }
    
    def has_permission(
        self,
        role: Role,
        permission: Permission
    ) -> bool:
        return permission in self.role_permissions.get(role, set())
```

### 2. ACL

```python
# infrastructure/security/acl.py
from typing import Dict, Set

class AccessControlList:
    def __init__(self):
        self.resource_permissions: Dict[str, Set[str]] = {}
    
    def grant_permission(
        self,
        resource: str,
        user: str,
        permission: str
    ):
        if resource not in self.resource_permissions:
            self.resource_permissions[resource] = set()
        self.resource_permissions[resource].add(
            f"{user}:{permission}"
        )
    
    def check_permission(
        self,
        resource: str,
        user: str,
        permission: str
    ) -> bool:
        if resource not in self.resource_permissions:
            return False
        return f"{user}:{permission}" in self.resource_permissions[resource]
```

## Proteção de Dados

### 1. Criptografia

```python
# infrastructure/security/encryption.py
from cryptography.fernet import Fernet
from config.settings import Settings

class DataEncryption:
    def __init__(self, settings: Settings):
        self.key = settings.encryption_key
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(
            encrypted_data.encode()
        ).decode()
```

### 2. Sanitização

```python
# infrastructure/security/sanitization.py
import re
from typing import Optional

class InputSanitizer:
    def __init__(self):
        self.email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        self.password_pattern = re.compile(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$"
        )
    
    def sanitize_input(self, text: str) -> str:
        # Remover caracteres especiais
        return re.sub(r"[^\w\s-]", "", text)
    
    def validate_email(self, email: str) -> bool:
        return bool(self.email_pattern.match(email))
    
    def validate_password(self, password: str) -> bool:
        return bool(self.password_pattern.match(password))
```

## Segurança de Rede

### 1. WAF

```python
# infrastructure/security/waf.py
from fastapi import Request, HTTPException
from typing import List, Set

class WebApplicationFirewall:
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.blocked_paths: Set[str] = set()
        self.blocked_headers: Set[str] = set()
    
    async def check_request(self, request: Request):
        # Verificar IP
        if request.client.host in self.blocked_ips:
            raise HTTPException(
                status_code=403,
                detail="IP bloqueado"
            )
        
        # Verificar path
        if request.url.path in self.blocked_paths:
            raise HTTPException(
                status_code=403,
                detail="Path bloqueado"
            )
        
        # Verificar headers
        for header in request.headers:
            if header in self.blocked_headers:
                raise HTTPException(
                    status_code=403,
                    detail="Header bloqueado"
                )
```

### 2. Rate Limiting

```python
# infrastructure/security/rate_limit.py
from fastapi import Request, HTTPException
from redis import Redis
from config.settings import Settings

class RateLimiter:
    def __init__(self, settings: Settings):
        self.redis = Redis.from_url(settings.redis_uri)
        self.rate_limit = 100  # requisições por minuto
    
    async def check_rate_limit(self, request: Request):
        key = f"rate_limit:{request.client.host}"
        current = self.redis.get(key)
        
        if current and int(current) >= self.rate_limit:
            raise HTTPException(
                status_code=429,
                detail="Limite de requisições excedido"
            )
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        pipe.execute()
```

## Observações

- Manter segredos seguros
- Atualizar dependências
- Monitorar logs
- Validar entradas
- Criptografar dados
- Limitar acesso
- Proteger APIs
- Testar segurança
- Documentar práticas
- Revisar periodicamente 