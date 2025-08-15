# Práticas de Segurança

Este documento detalha as práticas de segurança do Omni Keywords Finder.

## Autenticação

### 1. OAuth2

```python
# api/auth/oauth2.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
```

### 2. 2FA

```python
# api/auth/2fa.py
import pyotp
import qrcode
from io import BytesIO
from base64 import b64encode

def generate_2fa_secret():
    """Gera segredo para 2FA."""
    return pyotp.random_base32()

def generate_2fa_qr(secret: str, username: str):
    """Gera QR code para 2FA."""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        username,
        issuer_name="Omni Keywords Finder"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return b64encode(buffered.getvalue()).decode()

def verify_2fa_code(secret: str, code: str) -> bool:
    """Verifica código 2FA."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
```

## Autorização

### 1. RBAC

```python
# api/auth/rbac.py
from enum import Enum
from typing import List, Set
from dataclasses import dataclass

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

@dataclass
class Permission:
    resource: str
    action: str

class RBAC:
    def __init__(self):
        self._role_permissions: dict[Role, Set[Permission]] = {
            Role.ADMIN: {
                Permission("keywords", "create"),
                Permission("keywords", "read"),
                Permission("keywords", "update"),
                Permission("keywords", "delete"),
                Permission("clusters", "create"),
                Permission("clusters", "read"),
                Permission("clusters", "update"),
                Permission("clusters", "delete")
            },
            Role.USER: {
                Permission("keywords", "create"),
                Permission("keywords", "read"),
                Permission("clusters", "read")
            },
            Role.READONLY: {
                Permission("keywords", "read"),
                Permission("clusters", "read")
            }
        }
    
    def has_permission(self, role: Role, permission: Permission) -> bool:
        """Verifica se role tem permissão."""
        return permission in self._role_permissions.get(role, set())
```

### 2. ACL

```python
# api/auth/acl.py
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class Resource:
    id: str
    owner: str
    permissions: Dict[str, Set[str]]

class ACL:
    def __init__(self):
        self._resources: Dict[str, Resource] = {}
    
    def add_resource(self, resource: Resource):
        """Adiciona recurso."""
        self._resources[resource.id] = resource
    
    def grant_permission(
        self,
        resource_id: str,
        user: str,
        permission: str
    ):
        """Concede permissão."""
        if resource_id in self._resources:
            resource = self._resources[resource_id]
            if user not in resource.permissions:
                resource.permissions[user] = set()
            resource.permissions[user].add(permission)
    
    def check_permission(
        self,
        resource_id: str,
        user: str,
        permission: str
    ) -> bool:
        """Verifica permissão."""
        if resource_id in self._resources:
            resource = self._resources[resource_id]
            if user == resource.owner:
                return True
            return (
                user in resource.permissions and
                permission in resource.permissions[user]
            )
        return False
```

## Proteção de Dados

### 1. Criptografia

```python
# api/security/encryption.py
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
from config.settings import settings

class Encryption:
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY)
    
    def encrypt(self, data: str) -> str:
        """Criptografa dados."""
        return b64encode(
            self.fernet.encrypt(data.encode())
        ).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografa dados."""
        return self.fernet.decrypt(
            b64decode(encrypted_data)
        ).decode()
```

### 2. Sanitização

```python
# api/security/sanitization.py
import re
from html import escape
from typing import Any, Dict, List

class Sanitizer:
    @staticmethod
    def sanitize_input(data: Any) -> Any:
        """Sanitiza entrada."""
        if isinstance(data, str):
            return escape(data.strip())
        elif isinstance(data, dict):
            return {
                k: Sanitizer.sanitize_input(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [
                Sanitizer.sanitize_input(item)
                for item in data
            ]
        return data
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Valida senha."""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
```

## Segurança de Rede

### 1. WAF

```python
# api/security/waf.py
from fastapi import Request, HTTPException
from typing import List, Set
import re

class WAF:
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, int] = {}
        self.sql_patterns: List[str] = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)',
            r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\b\s+\'\w+\'\s*=\s*\'\w+\')'
        ]
        self.xss_patterns: List[str] = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*='
        ]
    
    async def check_request(self, request: Request):
        """Verifica requisição."""
        # Verificar IP bloqueado
        client_ip = request.client.host
        if client_ip in self.blocked_ips:
            raise HTTPException(
                status_code=403,
                detail="IP bloqueado"
            )
        
        # Verificar rate limit
        if not self._check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Muitas requisições"
            )
        
        # Verificar SQL injection
        if self._check_sql_injection(request):
            raise HTTPException(
                status_code=400,
                detail="Entrada inválida"
            )
        
        # Verificar XSS
        if self._check_xss(request):
            raise HTTPException(
                status_code=400,
                detail="Entrada inválida"
            )
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Verifica rate limit."""
        if ip not in self.rate_limits:
            self.rate_limits[ip] = 1
            return True
        self.rate_limits[ip] += 1
        return self.rate_limits[ip] <= 100
    
    def _check_sql_injection(self, request: Request) -> bool:
        """Verifica SQL injection."""
        query_params = str(request.query_params)
        for pattern in self.sql_patterns:
            if re.search(pattern, query_params, re.I):
                return True
        return False
    
    def _check_xss(self, request: Request) -> bool:
        """Verifica XSS."""
        query_params = str(request.query_params)
        for pattern in self.xss_patterns:
            if re.search(pattern, query_params, re.I):
                return True
        return False
```

### 2. Rate Limiting

```python
# api/security/rate_limit.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}
        self.window = timedelta(minutes=1)
        self.max_requests = 100
    
    async def check_rate_limit(self, request: Request):
        """Verifica rate limit."""
        client_ip = request.client.host
        now = datetime.utcnow()
        
        # Limpar requisições antigas
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < self.window
            ]
        
        # Verificar limite
        if client_ip in self.requests:
            if len(self.requests[client_ip]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Muitas requisições"
                )
            self.requests[client_ip].append(now)
        else:
            self.requests[client_ip] = [now]
```

## Observações

- Manter segredos seguros
- Atualizar dependências
- Monitorar logs
- Revisar código
- Testar segurança
- Documentar práticas
- Treinar equipe
- Manter histórico
- Revisar periodicamente
- Garantir conformidade 