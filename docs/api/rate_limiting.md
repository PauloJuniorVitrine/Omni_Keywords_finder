# 🚦 **Guia de Rate Limiting - Omni Keywords Finder API**

**Tracing ID**: `RATE_LIMIT_DOC_20250127_001`  
**Versão**: 1.0.0  
**Data**: 2025-01-27  
**Status**: ✅ **ATIVO**

---

## 📋 **Visão Geral**

O Omni Keywords Finder implementa um sistema robusto de **Rate Limiting** para garantir performance, estabilidade e uso justo da API entre todos os usuários.

---

## ⚡ **Limites por Plano**

### **Free Tier**
```bash
# Limites diários
Requests por dia:          1,000
Keywords por pesquisa:     10
Searches por hora:         10
Exports por dia:           5

# Limites por minuto
Requests por minuto:       20
Concurrent requests:       2
```

### **Starter Plan ($29/mês)**
```bash
# Limites diários
Requests por dia:          10,000
Keywords por pesquisa:     50
Searches por hora:         100
Exports por dia:           50

# Limites por minuto
Requests por minuto:       100
Concurrent requests:       10
```

### **Professional Plan ($99/mês)**
```bash
# Limites diários
Requests por dia:          100,000
Keywords por pesquisa:     200
Searches por hora:         1,000
Exports por dia:           500

# Limites por minuto
Requests por minuto:       500
Concurrent requests:       50
```

### **Enterprise Plan (Custom)**
```bash
# Limites personalizados
Requests por dia:          Custom
Keywords por pesquisa:     Custom
Searches por hora:         Custom
Exports por dia:           Custom

# Limites por minuto
Requests por minuto:       Custom
Concurrent requests:       Custom
```

---

## 🔍 **Limites por Endpoint**

### **Endpoints de Pesquisa**
```bash
# GET /v1/keywords/search
Free:      10 requests/hour
Starter:   100 requests/hour
Pro:       1,000 requests/hour
Enterprise: Custom

# GET /v1/keywords/related
Free:      5 requests/hour
Starter:   50 requests/hour
Pro:       500 requests/hour
Enterprise: Custom

# GET /v1/keywords/trends
Free:      5 requests/hour
Starter:   25 requests/hour
Pro:       250 requests/hour
Enterprise: Custom
```

### **Endpoints de Análise**
```bash
# POST /v1/analysis/competitor
Free:      2 requests/hour
Starter:   20 requests/hour
Pro:       200 requests/hour
Enterprise: Custom

# POST /v1/analysis/content
Free:      1 request/hour
Starter:   10 requests/hour
Pro:       100 requests/hour
Enterprise: Custom

# POST /v1/analysis/seo
Free:      1 request/hour
Starter:   10 requests/hour
Pro:       100 requests/hour
Enterprise: Custom
```

### **Endpoints de Exportação**
```bash
# GET /v1/export/csv
Free:      5 exports/day
Starter:   50 exports/day
Pro:       500 exports/day
Enterprise: Custom

# GET /v1/export/json
Free:      10 exports/day
Starter:   100 exports/day
Pro:       1,000 exports/day
Enterprise: Custom

# GET /v1/export/pdf
Free:      2 exports/day
Starter:   20 exports/day
Pro:       200 exports/day
Enterprise: Custom
```

---

## 📊 **Headers de Rate Limiting**

### **Headers de Resposta**
```bash
# Headers incluídos em todas as respostas
X-RateLimit-Limit:         1000        # Limite por hora
X-RateLimit-Remaining:     950         # Requisições restantes
X-RateLimit-Reset:         1640995200  # Timestamp de reset (Unix)
X-RateLimit-Reset-Time:    2025-01-27T12:00:00Z  # Reset em formato legível
```

### **Exemplo de Resposta**
```json
{
  "data": [...],
  "meta": {
    "rate_limit": {
      "limit": 1000,
      "remaining": 950,
      "reset": 1640995200,
      "reset_time": "2025-01-27T12:00:00Z"
    }
  }
}
```

---

## 🚨 **Tratamento de Rate Limiting**

### **Código de Status 429**
```bash
# Resposta quando rate limit é excedido
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "details": {
      "limit": 1000,
      "reset": 1640995200,
      "retry_after": 3600
    }
  }
}
```

### **Headers de Retry**
```bash
# Headers incluídos na resposta 429
Retry-After: 3600                    # Segundos até poder tentar novamente
X-RateLimit-Limit: 1000             # Limite atual
X-RateLimit-Reset: 1640995200       # Timestamp de reset
```

---

## 🛠️ **Implementação de Retry**

### **Python (Exponential Backoff)**
```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OmniKeywordsAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.omnikeywordsfinder.com/v1'
        
        # Configurar retry com exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def handle_rate_limit(self, response):
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return True
        return False
    
    def search_keywords(self, query):
        while True:
            response = self.session.get(
                f'{self.base_url}/keywords/search',
                headers={'Authorization': f'Bearer {self.api_key}'},
                params={'q': query}
            )
            
            if not self.handle_rate_limit(response):
                return response.json()
```

### **JavaScript (Async/Await)**
```javascript
class OmniKeywordsAPI {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.omnikeywordsfinder.com/v1';
    }
    
    async requestWithRetry(endpoint, options = {}, maxRetries = 3) {
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const response = await fetch(`${this.baseUrl}${endpoint}`, {
                    ...options,
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                });
                
                if (response.status === 429) {
                    const retryAfter = response.headers.get('Retry-After') || 60;
                    console.log(`Rate limit exceeded. Waiting ${retryAfter} seconds...`);
                    await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
                    continue;
                }
                
                return response.json();
            } catch (error) {
                if (attempt === maxRetries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
            }
        }
    }
    
    async searchKeywords(query) {
        return this.requestWithRetry(`/keywords/search?q=${query}`);
    }
}
```

### **cURL com Retry**
```bash
#!/bin/bash

# Função para fazer requisição com retry
make_request() {
    local url="$1"
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$url" \
            -H "Authorization: Bearer $API_KEY" \
            -H "Content-Type: application/json")
        
        http_code="${response: -3}"
        
        if [ "$http_code" = "200" ]; then
            cat /tmp/response.json
            return 0
        elif [ "$http_code" = "429" ]; then
            retry_after=$(curl -s -I "$url" | grep -i "Retry-After" | cut -d' ' -f2 | tr -d '\r')
            echo "Rate limit exceeded. Waiting ${retry_after}s..."
            sleep "$retry_after"
        else
            echo "HTTP $http_code error"
            return 1
        fi
        
        retry_count=$((retry_count + 1))
    done
    
    echo "Max retries exceeded"
    return 1
}

# Uso
API_KEY="sk_live_1234567890abcdef"
make_request "https://api.omnikeywordsfinder.com/v1/keywords/search?q=digital+marketing"
```

---

## 📈 **Monitoramento de Rate Limiting**

### **Dashboard de Uso**
```bash
# Endpoint para verificar uso atual
GET /v1/account/usage

# Resposta
{
  "usage": {
    "current_period": {
      "requests_used": 450,
      "requests_limit": 1000,
      "percentage_used": 45,
      "reset_date": "2025-01-28T00:00:00Z"
    },
    "endpoints": {
      "/v1/keywords/search": {
        "used": 200,
        "limit": 1000,
        "remaining": 800
      },
      "/v1/analysis/competitor": {
        "used": 10,
        "limit": 200,
        "remaining": 190
      }
    }
  }
}
```

### **Alertas de Rate Limiting**
```javascript
// Webhook para alertas de rate limiting
{
  "event": "rate_limit_warning",
  "data": {
    "user_id": "user_123",
    "endpoint": "/v1/keywords/search",
    "usage_percentage": 85,
    "remaining_requests": 150,
    "reset_time": "2025-01-27T12:00:00Z"
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

---

## 🔧 **Configurações Avançadas**

### **Rate Limiting por IP**
```bash
# Limites adicionais por IP
Free:      100 requests/hour per IP
Starter:   500 requests/hour per IP
Pro:       2,000 requests/hour per IP
Enterprise: Custom
```

### **Rate Limiting por User Agent**
```bash
# Limites por User Agent
Unknown User Agent:    50% dos limites normais
Known User Agent:      100% dos limites normais
Verified Integration:  150% dos limites normais
```

### **Burst Allowance**
```bash
# Permissão de burst (picos de tráfego)
Free:      5 requests em 10 segundos
Starter:   20 requests em 10 segundos
Pro:       100 requests em 10 segundos
Enterprise: Custom
```

---

## 🚨 **Troubleshooting**

### **Problemas Comuns**

#### **Rate Limit Exceeded Frequentemente**
```bash
# Soluções:
1. Implemente cache local para dados estáticos
2. Use webhooks em vez de polling
3. Considere upgrade do plano
4. Otimize requisições (batch quando possível)
```

#### **Retry Loops Infinitos**
```bash
# Prevenção:
1. Sempre verifique Retry-After header
2. Implemente exponential backoff
3. Defina limite máximo de retries
4. Use circuit breaker pattern
```

#### **Concurrent Request Limits**
```bash
# Soluções:
1. Implemente queue de requisições
2. Use connection pooling
3. Limite threads/processos concorrentes
4. Considere async/await patterns
```

---

## 📞 **Suporte**

- **Documentação**: https://docs.omnikeywordsfinder.com/rate-limiting
- **Status API**: https://status.omnikeywordsfinder.com
- **Suporte**: support@omnikeywordsfinder.com
- **Discord**: https://discord.gg/omnikeywordsfinder

---

**Última atualização**: 2025-01-27  
**Próxima revisão**: 2025-02-27 