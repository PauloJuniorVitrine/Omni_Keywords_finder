# Arquitetura de Segurança

Este documento detalha a arquitetura de segurança do Omni Keywords Finder.

## Autenticação

### OAuth2
```python
# security/oauth2.py
class OAuth2Handler:
    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user(email)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 2FA
```python
# security/2fa.py
class TwoFactorAuth:
    def __init__(self):
        self.totp = pyotp.TOTP(SECRET_KEY)

    def generate_secret(self):
        return pyotp.random_base32()

    def verify_code(self, secret: str, code: str):
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    def generate_qr_code(self, secret: str, email: str):
        return pyotp.totp.TOTP(secret).provisioning_uri(
            email, issuer_name="Omni Keywords Finder"
        )
```

## Autorização

### RBAC
```python
# security/rbac.py
class RoleBasedAccess:
    def __init__(self):
        self.roles = {
            "admin": ["*"],
            "user": ["read:keywords", "write:keywords"],
            "viewer": ["read:keywords"]
        }

    def check_permission(self, user: User, permission: str):
        user_role = user.role
        if user_role not in self.roles:
            return False
        return (
            permission in self.roles[user_role] or
            "*" in self.roles[user_role]
        )

    def get_user_permissions(self, user: User):
        return self.roles.get(user.role, [])
```

### ACL
```python
# security/acl.py
class AccessControlList:
    def __init__(self):
        self.acls = {}

    def add_permission(self, resource: str, user: str, permission: str):
        if resource not in self.acls:
            self.acls[resource] = {}
        if user not in self.acls[resource]:
            self.acls[resource][user] = set()
        self.acls[resource][user].add(permission)

    def check_permission(self, resource: str, user: str, permission: str):
        return (
            resource in self.acls and
            user in self.acls[resource] and
            permission in self.acls[resource][user]
        )
```

## Proteção de Dados

### Criptografia
```python
# security/encryption.py
class DataEncryption:
    def __init__(self):
        self.cipher_suite = Fernet(SECRET_KEY)

    def encrypt_data(self, data: str):
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes):
        return self.cipher_suite.decrypt(encrypted_data).decode()

    def rotate_key(self):
        new_key = Fernet.generate_key()
        # Implementar rotação de chaves
```

### Sanitização
```python
# security/sanitization.py
class InputSanitizer:
    def sanitize_input(self, data: str):
        # Remover caracteres especiais
        data = re.sub(r'[<>]', '', data)
        # Escapar caracteres HTML
        data = html.escape(data)
        return data

    def validate_email(self, email: str):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

    def validate_password(self, password: str):
        return bool(re.match(
            r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
            password
        ))
```

## Segurança de Rede

### WAF
```python
# security/waf.py
class WebApplicationFirewall:
    def __init__(self):
        self.rules = {
            "sql_injection": r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\b)",
            "xss": r"(<script|javascript:|on\w+\s*=)",
            "path_traversal": r"(\.\.\/|\.\.\\)"
        }

    def check_request(self, request: Request):
        for rule_name, pattern in self.rules.items():
            if re.search(pattern, str(request)):
                return False
        return True

    def log_violation(self, request: Request, rule: str):
        logger.warning(f"WAF violation: {rule} in request {request}")
```

### Rate Limiting
```python
# security/rate_limit.py
class RateLimiter:
    def __init__(self):
        self.redis = Redis()
        self.limits = {
            "default": {"requests": 100, "period": 3600},
            "api": {"requests": 1000, "period": 3600}
        }

    async def check_rate_limit(self, key: str, limit_type: str = "default"):
        limit = self.limits[limit_type]
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, limit["period"])
        return current <= limit["requests"]
```

## Observações

1. Autenticação forte
2. Autorização granular
3. Criptografia de dados
4. Sanitização de inputs
5. Proteção contra ataques
6. Rate limiting
7. Logs de segurança
8. Monitoramento
9. Atualizações regulares
10. Documentação atualizada 