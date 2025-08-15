# 🔐 **Guia de Autenticação - Omni Keywords Finder API**

**Tracing ID**: `AUTH_DOC_20250127_001`  
**Versão**: 1.0.0  
**Data**: 2025-01-27  
**Status**: ✅ **ATIVO**

---

## 📋 **Visão Geral**

O Omni Keywords Finder utiliza autenticação baseada em **JWT (JSON Web Tokens)** com suporte a múltiplos métodos de autenticação para diferentes cenários de uso.

---

## 🔑 **Métodos de Autenticação**

### **1. API Key Authentication**
Método recomendado para integrações automatizadas e aplicações de terceiros.

```bash
# Header de autenticação
Authorization: Bearer YOUR_API_KEY

# Exemplo de requisição
curl -X GET "https://api.omnikeywordsfinder.com/v1/keywords/search" \
  -H "Authorization: Bearer sk_live_1234567890abcdef" \
  -H "Content-Type: application/json"
```

#### **Configuração da API Key**
1. Acesse o dashboard em `https://app.omnikeywordsfinder.com/settings/api`
2. Clique em "Generate New API Key"
3. Copie a chave gerada (formato: `sk_live_` + 32 caracteres)
4. Armazene de forma segura (não compartilhe em código público)

#### **Permissões da API Key**
- **Read-only**: Apenas consultas e leitura de dados
- **Read-write**: Consultas + criação/edição de recursos
- **Admin**: Acesso completo (incluindo configurações de conta)

### **2. JWT Token Authentication**
Método para autenticação de usuários via interface web.

```bash
# Login para obter token
curl -X POST "https://api.omnikeywordsfinder.com/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'

# Resposta
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "bearer"
}

# Uso do token
curl -X GET "https://api.omnikeywordsfinder.com/v1/keywords/search" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **3. OAuth 2.0 (Enterprise)**
Para integrações enterprise com provedores de identidade.

```bash
# Fluxo Authorization Code
GET /oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=YOUR_REDIRECT_URI

# Troca do código por token
POST /oauth/token
{
  "grant_type": "authorization_code",
  "code": "AUTHORIZATION_CODE",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "redirect_uri": "YOUR_REDIRECT_URI"
}
```

---

## 🛡️ **Segurança e Boas Práticas**

### **Proteção de Credenciais**
```javascript
// ❌ NUNCA faça isso
const apiKey = "sk_live_1234567890abcdef"; // Hardcoded

// ✅ Faça isso
const apiKey = process.env.OMNI_API_KEY; // Environment variable
```

### **Rotação de Tokens**
- **API Keys**: Rotacione a cada 90 dias
- **JWT Tokens**: Expiração automática em 1 hora
- **Refresh Tokens**: Expiração em 30 dias

### **Rate Limiting**
```bash
# Limites por método de autenticação
API Key (Read-only):    1000 requests/hour
API Key (Read-write):   500 requests/hour
API Key (Admin):        200 requests/hour
JWT Token:              100 requests/hour
OAuth 2.0:             1000 requests/hour
```

### **Headers de Segurança**
```bash
# Headers obrigatórios
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
User-Agent: YourApp/1.0.0
X-Request-ID: unique-request-id

# Headers opcionais de segurança
X-Forwarded-For: client-ip
X-Real-IP: client-ip
```

---

## 🔄 **Refresh Token Flow**

### **Renovação Automática**
```javascript
// Exemplo de renovação automática
const refreshToken = async (refreshToken) => {
  const response = await fetch('/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken
    })
  });
  
  const data = await response.json();
  return data.access_token;
};
```

### **Tratamento de Erros**
```javascript
// Códigos de erro de autenticação
401 Unauthorized: Token inválido ou expirado
403 Forbidden: Permissões insuficientes
429 Too Many Requests: Rate limit excedido
```

---

## 🧪 **Exemplos de Implementação**

### **Python (requests)**
```python
import requests
import os

class OmniKeywordsAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OMNI_API_KEY')
        self.base_url = 'https://api.omnikeywordsfinder.com/v1'
        
    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'OmniKeywordsPython/1.0.0'
        }
    
    def search_keywords(self, query, limit=10):
        response = requests.get(
            f'{self.base_url}/keywords/search',
            headers=self._get_headers(),
            params={'q': query, 'limit': limit}
        )
        return response.json()

# Uso
api = OmniKeywordsAPI()
results = api.search_keywords('digital marketing')
```

### **JavaScript (fetch)**
```javascript
class OmniKeywordsAPI {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.omnikeywordsfinder.com/v1';
    }
    
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json',
                'User-Agent': 'OmniKeywordsJS/1.0.0',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return response.json();
    }
    
    async searchKeywords(query, limit = 10) {
        return this.request(`/keywords/search?q=${query}&limit=${limit}`);
    }
}

// Uso
const api = new OmniKeywordsAPI('sk_live_1234567890abcdef');
api.searchKeywords('digital marketing').then(console.log);
```

### **cURL**
```bash
# Exemplo completo
curl -X GET "https://api.omnikeywordsfinder.com/v1/keywords/search" \
  -H "Authorization: Bearer sk_live_1234567890abcdef" \
  -H "Content-Type: application/json" \
  -H "User-Agent: OmniKeywordsCLI/1.0.0" \
  -G \
  -d "q=digital marketing" \
  -d "limit=10" \
  -d "language=pt-BR"
```

---

## 🚨 **Troubleshooting**

### **Problemas Comuns**

#### **401 Unauthorized**
```bash
# Verifique:
1. Token está correto e não expirou
2. Header Authorization está formatado corretamente
3. Token tem permissões para o endpoint
```

#### **403 Forbidden**
```bash
# Verifique:
1. API Key tem permissões suficientes
2. Endpoint não está bloqueado para seu plano
3. Rate limit não foi excedido
```

#### **429 Too Many Requests**
```bash
# Soluções:
1. Implemente retry com exponential backoff
2. Reduza frequência de requisições
3. Considere upgrade do plano
```

### **Logs de Debug**
```bash
# Ative logs detalhados
curl -X GET "https://api.omnikeywordsfinder.com/v1/keywords/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Debug: true" \
  -v
```

---

## 📞 **Suporte**

- **Documentação**: https://docs.omnikeywordsfinder.com
- **Status API**: https://status.omnikeywordsfinder.com
- **Suporte**: support@omnikeywordsfinder.com
- **Discord**: https://discord.gg/omnikeywordsfinder

---

**Última atualização**: 2025-01-27  
**Próxima revisão**: 2025-02-27 