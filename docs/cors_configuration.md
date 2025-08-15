# 🔒 Configuração CORS - Omni Keywords Finder

**Tracing ID:** `CORS_CONFIG_DOCS_2025_001`  
**Data/Hora:** 2025-01-27 19:15:00 UTC  
**Versão:** 1.0  
**Status:** 📚 DOCUMENTAÇÃO COMPLETA  

---

## 🎯 **OBJETIVO**

Este documento descreve a configuração CORS (Cross-Origin Resource Sharing) implementada no sistema Omni Keywords Finder, incluindo configurações por ambiente e headers de segurança.

---

## 🏗️ **ARQUITETURA**

### **Componentes Principais**

1. **`backend/app/main.py`** - Configuração CORS básica com Flask-CORS
2. **`backend/app/middleware/cors_middleware.py`** - Middleware CORS avançado
3. **`backend/app/middleware/security_headers.py`** - Headers de segurança
4. **`tests/unit/backend/test_cors_config.py`** - Testes unitários

### **Fluxo de Execução**

```
Request → CORS Middleware → Security Headers → Application → Response
    ↓           ↓                ↓              ↓           ↓
Origin    Validation      Security Headers   Business    CORS Headers
Check     & Logging       Addition           Logic       Addition
```

---

## 🌍 **CONFIGURAÇÕES POR AMBIENTE**

### **🛠️ Desenvolvimento (`FLASK_ENV=development`)**

**Origins Permitidas:**
```javascript
[
  'http://localhost:3000',      // React dev server
  'http://localhost:3001',      // React dev server (alternativo)
  'http://127.0.0.1:3000',     // IP local
  'http://127.0.0.1:3001',     // IP local (alternativo)
  'http://localhost:5173',      // Vite dev server
  'http://127.0.0.1:5173'      // Vite dev server (IP)
]
```

**Configurações:**
- ✅ **Validação de Origem:** Flexível (permite localhost com qualquer porta)
- ✅ **Log de Violações:** Desabilitado
- ✅ **Headers de Segurança:** Básicos
- ✅ **HSTS:** Desabilitado
- ✅ **CSP:** Permissivo para desenvolvimento

**Headers de Segurança:**
```http
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer-when-downgrade
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' http: https: ws: wss:;
```

### **🧪 Staging (`FLASK_ENV=staging`)**

**Origins Permitidas:**
```javascript
[
  'https://staging.omni-keywords-finder.com',
  'https://test.omni-keywords-finder.com',
  'http://localhost:3000',      // Para testes locais
  'http://127.0.0.1:3000'      // Para testes locais
]
```

**Configurações:**
- ✅ **Validação de Origem:** Estrita
- ✅ **Log de Violações:** Habilitado
- ✅ **Headers de Segurança:** Intermediários
- ✅ **HSTS:** Habilitado (86400 segundos)
- ✅ **CSP:** Moderado

**Headers de Segurança:**
```http
Strict-Transport-Security: max-age=86400; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
```

### **🚀 Produção (`FLASK_ENV=production`)**

**Origins Permitidas:**
```javascript
[
  'https://omni-keywords-finder.com',
  'https://www.omni-keywords-finder.com',
  'https://app.omni-keywords-finder.com'
]
```

**Configurações:**
- ✅ **Validação de Origem:** Máxima segurança
- ✅ **Log de Violações:** Habilitado
- ✅ **Headers de Segurança:** Máximos
- ✅ **HSTS:** Habilitado (31536000 segundos + preload)
- ✅ **CSP:** Restritivo

**Headers de Segurança:**
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 🔧 **IMPLEMENTAÇÃO**

### **1. Configuração Básica (main.py)**

```python
# Configuração CORS segura por ambiente
def get_cors_origins():
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ['https://omni-keywords-finder.com', ...]
    elif env == 'staging':
        return ['https://staging.omni-keywords-finder.com', ...]
    else:
        return ['http://localhost:3000', ...]

# Aplicar CORS com configuração segura
CORS(app, 
     origins=get_cors_origins(),
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=[
         'Content-Type', 
         'Authorization', 
         'X-Requested-With',
         'X-API-Key',
         'X-Client-Version',
         'X-Request-ID'
     ],
     expose_headers=[
         'X-Request-ID',
         'X-Rate-Limit-Remaining',
         'X-Rate-Limit-Reset'
     ],
     supports_credentials=True,
     max_age=3600)
```

### **2. Middleware CORS Avançado**

```python
# Validação de origem
def is_valid_origin(origin, config):
    if origin in config['origins']:
        return True
    
    # Verificação por padrão (desenvolvimento)
    if not config['strict_origin_validation']:
        if re.match(r'^http://localhost:\d+$', origin):
            return True
    
    return False

# Decorator para endpoints específicos
@cors_protected
def protected_endpoint():
    return {'data': 'protected'}
```

### **3. Headers de Segurança**

```python
def add_security_headers(response):
    config = get_security_config()
    
    # Headers básicos
    response.headers['X-Content-Type-Options'] = config['x_content_type_options']
    response.headers['X-Frame-Options'] = config['x_frame_options']
    response.headers['X-XSS-Protection'] = config['x_xss_protection']
    response.headers['Referrer-Policy'] = config['referrer_policy']
    
    # Content Security Policy
    if config['content_security_policy']:
        response.headers['Content-Security-Policy'] = config['content_security_policy']
    
    # Strict Transport Security
    if config['strict_transport_security']:
        response.headers['Strict-Transport-Security'] = config['strict_transport_security']
    
    return response
```

---

## 🧪 **TESTES**

### **Executar Testes CORS**

```bash
# Executar todos os testes CORS
python -m pytest tests/unit/backend/test_cors_config.py -v

# Executar testes específicos
python -m pytest tests/unit/backend/test_cors_config.py::TestCORSConfig -v
python -m pytest tests/unit/backend/test_cors_config.py::TestCORSMiddleware -v
python -m pytest tests/unit/backend/test_cors_config.py::TestSecurityHeaders -v
```

### **Testes Disponíveis**

1. **TestCORSConfig** - Configurações por ambiente
2. **TestCORSMiddleware** - Middleware CORS
3. **TestSecurityHeaders** - Headers de segurança
4. **TestCORSIntegration** - Testes de integração

---

## 🚨 **TROUBLESHOOTING**

### **Erro: CORS Policy Violation**

**Sintomas:**
```
Access to fetch at 'http://localhost:5000/api/test' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Soluções:**

1. **Verificar Ambiente:**
   ```bash
   echo $FLASK_ENV
   # Deve ser 'development' para localhost
   ```

2. **Verificar Origins Configuradas:**
   ```python
   from app.middleware.cors_middleware import get_cors_config
   config = get_cors_config()
   print(config['origins'])
   ```

3. **Verificar Headers da Requisição:**
   ```javascript
   // Frontend
   fetch('/api/test', {
     headers: {
       'Origin': 'http://localhost:3000',
       'Content-Type': 'application/json'
     }
   })
   ```

### **Erro: Security Headers Missing**

**Sintomas:**
```
Security headers not present in response
```

**Soluções:**

1. **Verificar Middleware:**
   ```python
   from app.middleware.security_headers import init_security_headers
   app = init_security_headers(app)
   ```

2. **Verificar Configuração:**
   ```python
   from app.middleware.security_headers import get_security_config
   config = get_security_config()
   print(config)
   ```

---

## 📊 **MONITORAMENTO**

### **Logs de Violações CORS**

As violações CORS são logadas automaticamente:

```python
# Exemplo de log
{
  "nivel": "WARNING",
  "modulo": "cors_middleware",
  "mensagem": "CORS policy violation: http://malicious.com from 192.168.1.100",
  "dados": {
    "origin": "http://malicious.com",
    "ip": "192.168.1.100",
    "timestamp": "2025-01-27T19:15:00Z"
  }
}
```

### **Headers Suspeitos**

Headers suspeitos são detectados e logados:

```python
# Exemplo de log
{
  "nivel": "WARNING",
  "modulo": "security_headers",
  "mensagem": "Suspicious header detected: X-Forwarded-For",
  "dados": {
    "header": "X-Forwarded-For",
    "value": "192.168.1.1",
    "ip": "10.0.0.1",
    "timestamp": "2025-01-27T19:15:00Z"
  }
}
```

---

## 🔄 **DEPLOYMENT**

### **Desenvolvimento**

```bash
export FLASK_ENV=development
python backend/app/main.py
```

### **Staging**

```bash
export FLASK_ENV=staging
python backend/app/main.py
```

### **Produção**

```bash
export FLASK_ENV=production
python backend/app/main.py
```

---

## 📚 **REFERÊNCIAS**

- [MDN Web Docs - CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)

---

**🔄 Documento atualizado em:** 2025-01-27 19:15:00 UTC  
**📝 Próxima revisão:** 2025-02-27 19:15:00 UTC 