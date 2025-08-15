# 🚨 **Códigos de Erro - Omni Keywords Finder API**

**Tracing ID**: `ERROR_CODES_DOC_20250127_001`  
**Versão**: 1.0.0  
**Data**: 2025-01-27  
**Status**: ✅ **ATIVO**

---

## 📋 **Visão Geral**

Este documento descreve todos os códigos de erro possíveis retornados pela API do Omni Keywords Finder, incluindo causas, soluções e exemplos de implementação.

---

## 🔢 **Códigos de Status HTTP**

### **2xx - Sucesso**
```bash
200 OK                    # Requisição processada com sucesso
201 Created              # Recurso criado com sucesso
202 Accepted             # Requisição aceita para processamento assíncrono
204 No Content           # Requisição processada, sem conteúdo para retornar
```

### **4xx - Erro do Cliente**
```bash
400 Bad Request          # Requisição malformada
401 Unauthorized         # Autenticação necessária
403 Forbidden            # Acesso negado
404 Not Found            # Recurso não encontrado
405 Method Not Allowed   # Método HTTP não permitido
409 Conflict             # Conflito de recursos
422 Unprocessable Entity # Dados inválidos
429 Too Many Requests    # Rate limit excedido
```

### **5xx - Erro do Servidor**
```bash
500 Internal Server Error    # Erro interno do servidor
502 Bad Gateway             # Erro de gateway
503 Service Unavailable      # Serviço temporariamente indisponível
504 Gateway Timeout          # Timeout de gateway
```

---

## 📝 **Estrutura de Resposta de Erro**

### **Formato Padrão**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Descrição legível do erro",
    "details": {
      "field": "campo_specífico",
      "value": "valor_problemático",
      "suggestion": "sugestão_de_correção"
    },
    "trace_id": "trace_1234567890abcdef",
    "timestamp": "2025-01-27T10:30:00Z",
    "documentation_url": "https://docs.omnikeywordsfinder.com/errors/ERROR_CODE"
  }
}
```

### **Headers de Erro**
```bash
X-Error-Code: ERROR_CODE
X-Trace-ID: trace_1234567890abcdef
X-Request-ID: req_1234567890abcdef
```

---

## 🔐 **Erros de Autenticação (4xx)**

### **AUTH_001 - API Key Inválida**
```json
{
  "error": {
    "code": "AUTH_001",
    "message": "API key inválida ou expirada",
    "details": {
      "suggestion": "Verifique se a API key está correta e não expirou"
    },
    "http_status": 401
  }
}
```

**Causas:**
- API key incorreta
- API key expirada
- API key revogada

**Soluções:**
```bash
# Verificar API key
curl -X GET "https://api.omnikeywordsfinder.com/v1/account/verify" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Gerar nova API key
# Acesse: https://app.omnikeywordsfinder.com/settings/api
```

### **AUTH_002 - Permissões Insuficientes**
```json
{
  "error": {
    "code": "AUTH_002",
    "message": "Permissões insuficientes para acessar este recurso",
    "details": {
      "required_permission": "admin",
      "current_permission": "read-only"
    },
    "http_status": 403
  }
}
```

**Causas:**
- API key com permissões limitadas
- Endpoint requer permissões especiais
- Plano não suporta funcionalidade

**Soluções:**
```bash
# Verificar permissões
curl -X GET "https://api.omnikeywordsfinder.com/v1/account/permissions" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Upgrade do plano se necessário
```

### **AUTH_003 - Token JWT Expirado**
```json
{
  "error": {
    "code": "AUTH_003",
    "message": "Token JWT expirado",
    "details": {
      "expired_at": "2025-01-27T09:30:00Z",
      "suggestion": "Use o refresh token para obter um novo access token"
    },
    "http_status": 401
  }
}
```

**Soluções:**
```javascript
// Renovar token
const refreshToken = async (refreshToken) => {
  const response = await fetch('/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  return response.json();
};
```

---

## 🔍 **Erros de Validação (4xx)**

### **VALID_001 - Parâmetros Obrigatórios Ausentes**
```json
{
  "error": {
    "code": "VALID_001",
    "message": "Parâmetros obrigatórios ausentes",
    "details": {
      "missing_fields": ["query", "language"],
      "suggestion": "Inclua todos os parâmetros obrigatórios"
    },
    "http_status": 400
  }
}
```

**Exemplo de Correção:**
```bash
# ❌ Incorreto
curl -X GET "https://api.omnikeywordsfinder.com/v1/keywords/search"

# ✅ Correto
curl -X GET "https://api.omnikeywordsfinder.com/v1/keywords/search?query=digital+marketing&language=pt-BR"
```

### **VALID_002 - Formato de Dados Inválido**
```json
{
  "error": {
    "code": "VALID_002",
    "message": "Formato de dados inválido",
    "details": {
      "field": "email",
      "value": "invalid-email",
      "expected_format": "email@domain.com"
    },
    "http_status": 422
  }
}
```

### **VALID_003 - Valor Fora do Range**
```json
{
  "error": {
    "code": "VALID_003",
    "message": "Valor fora do range permitido",
    "details": {
      "field": "limit",
      "value": 1000,
      "min_value": 1,
      "max_value": 100
    },
    "http_status": 422
  }
}
```

---

## 🚦 **Erros de Rate Limiting (4xx)**

### **RATE_001 - Rate Limit Excedido**
```json
{
  "error": {
    "code": "RATE_001",
    "message": "Rate limit excedido",
    "details": {
      "limit": 1000,
      "reset_time": "2025-01-27T12:00:00Z",
      "retry_after": 3600
    },
    "http_status": 429
  }
}
```

**Implementação de Retry:**
```python
import time
import requests

def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return True
    return False
```

### **RATE_002 - Concurrent Requests Limit**
```json
{
  "error": {
    "code": "RATE_002",
    "message": "Limite de requisições concorrentes excedido",
    "details": {
      "current_requests": 15,
      "max_concurrent": 10,
      "suggestion": "Aguarde algumas requisições terminarem"
    },
    "http_status": 429
  }
}
```

---

## 🔍 **Erros de Recursos (4xx)**

### **RESOURCE_001 - Recurso Não Encontrado**
```json
{
  "error": {
    "code": "RESOURCE_001",
    "message": "Recurso não encontrado",
    "details": {
      "resource_type": "keyword_analysis",
      "resource_id": "analysis_123",
      "suggestion": "Verifique se o ID está correto"
    },
    "http_status": 404
  }
}
```

### **RESOURCE_002 - Recurso Já Existe**
```json
{
  "error": {
    "code": "RESOURCE_002",
    "message": "Recurso já existe",
    "details": {
      "resource_type": "project",
      "resource_name": "My Project",
      "suggestion": "Use um nome único ou atualize o recurso existente"
    },
    "http_status": 409
  }
}
```

---

## ⚙️ **Erros de Processamento (5xx)**

### **PROCESS_001 - Processamento Assíncrono Falhou**
```json
{
  "error": {
    "code": "PROCESS_001",
    "message": "Processamento assíncrono falhou",
    "details": {
      "job_id": "job_1234567890abcdef",
      "failure_reason": "timeout",
      "suggestion": "Tente novamente ou entre em contato com o suporte"
    },
    "http_status": 500
  }
}
```

### **PROCESS_002 - Serviço Temporariamente Indisponível**
```json
{
  "error": {
    "code": "PROCESS_002",
    "message": "Serviço temporariamente indisponível",
    "details": {
      "service": "keyword_analysis",
      "estimated_recovery": "2025-01-27T11:00:00Z",
      "suggestion": "Tente novamente em alguns minutos"
    },
    "http_status": 503
  }
}
```

---

## 🧪 **Implementação de Tratamento de Erros**

### **Python (requests)**
```python
import requests
from typing import Dict, Any

class OmniKeywordsAPIError(Exception):
    def __init__(self, error_data: Dict[str, Any]):
        self.code = error_data.get('code')
        self.message = error_data.get('message')
        self.details = error_data.get('details', {})
        self.http_status = error_data.get('http_status')
        super().__init__(self.message)

class OmniKeywordsAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.omnikeywordsfinder.com/v1'
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            error_data = response.json().get('error', {})
            error_data['http_status'] = response.status_code
            raise OmniKeywordsAPIError(error_data)
        return response.json()
    
    def search_keywords(self, query: str) -> Dict[str, Any]:
        response = requests.get(
            f'{self.base_url}/keywords/search',
            headers={'Authorization': f'Bearer {self.api_key}'},
            params={'q': query}
        )
        return self._handle_response(response)

# Uso com tratamento de erro
try:
    api = OmniKeywordsAPI('your_api_key')
    results = api.search_keywords('digital marketing')
    print(results)
except OmniKeywordsAPIError as e:
    print(f"Erro {e.code}: {e.message}")
    if e.code == 'AUTH_001':
        print("Verifique sua API key")
    elif e.code == 'RATE_001':
        print(f"Aguarde {e.details.get('retry_after')} segundos")
```

### **JavaScript (fetch)**
```javascript
class OmniKeywordsAPIError extends Error {
    constructor(errorData) {
        super(errorData.message);
        this.code = errorData.code;
        this.details = errorData.details;
        this.httpStatus = errorData.http_status;
    }
}

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
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            errorData.error.http_status = response.status;
            throw new OmniKeywordsAPIError(errorData.error);
        }
        
        return response.json();
    }
    
    async searchKeywords(query) {
        return this.request(`/keywords/search?q=${query}`);
    }
}

// Uso com tratamento de erro
const api = new OmniKeywordsAPI('your_api_key');

api.searchKeywords('digital marketing')
    .then(results => console.log(results))
    .catch(error => {
        console.error(`Erro ${error.code}: ${error.message}`);
        
        switch (error.code) {
            case 'AUTH_001':
                console.log('Verifique sua API key');
                break;
            case 'RATE_001':
                console.log(`Aguarde ${error.details.retry_after} segundos`);
                break;
            case 'VALID_001':
                console.log('Parâmetros obrigatórios ausentes:', error.details.missing_fields);
                break;
            default:
                console.log('Erro desconhecido');
        }
    });
```

### **cURL com Tratamento de Erro**
```bash
#!/bin/bash

# Função para fazer requisição com tratamento de erro
api_request() {
    local endpoint="$1"
    local api_key="$2"
    
    response=$(curl -s -w "%{http_code}" -o /tmp/response.json \
        "https://api.omnikeywordsfinder.com/v1${endpoint}" \
        -H "Authorization: Bearer ${api_key}" \
        -H "Content-Type: application/json")
    
    http_code="${response: -3}"
    
    if [ "$http_code" -ge 400 ]; then
        error_data=$(cat /tmp/response.json)
        error_code=$(echo "$error_data" | jq -r '.error.code')
        error_message=$(echo "$error_data" | jq -r '.error.message')
        
        echo "Erro $error_code: $error_message"
        
        case $error_code in
            "AUTH_001")
                echo "Verifique sua API key"
                ;;
            "RATE_001")
                retry_after=$(echo "$error_data" | jq -r '.error.details.retry_after')
                echo "Aguarde $retry_after segundos"
                ;;
            "VALID_001")
                echo "Parâmetros obrigatórios ausentes"
                ;;
            *)
                echo "Erro desconhecido"
                ;;
        esac
        
        return 1
    else
        cat /tmp/response.json
        return 0
    fi
}

# Uso
API_KEY="sk_live_1234567890abcdef"
api_request "/keywords/search?q=digital+marketing" "$API_KEY"
```

---

## 📊 **Monitoramento de Erros**

### **Webhook de Erros**
```json
{
  "event": "api_error",
  "data": {
    "error_code": "RATE_001",
    "user_id": "user_123",
    "endpoint": "/v1/keywords/search",
    "timestamp": "2025-01-27T10:30:00Z",
    "request_id": "req_1234567890abcdef"
  }
}
```

### **Logs de Erro**
```bash
# Formato de log
2025-01-27T10:30:00Z [ERROR] AUTH_001: API key inválida - user_id:user_123 - endpoint:/v1/keywords/search - trace_id:trace_1234567890abcdef
```

---

## 📞 **Suporte**

- **Documentação**: https://docs.omnikeywordsfinder.com/errors
- **Status API**: https://status.omnikeywordsfinder.com
- **Suporte**: support@omnikeywordsfinder.com
- **Discord**: https://discord.gg/omnikeywordsfinder

---

**Última atualização**: 2025-01-27  
**Próxima revisão**: 2025-02-27 