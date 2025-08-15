# 🔐 **DOCUMENTAÇÃO DA API DE CREDENCIAIS**

## 📋 **INFORMAÇÕES GERAIS**

- **Versão da API**: 1.0
- **Base URL**: `/api/credentials`
- **Autenticação**: Bearer Token (JWT)
- **Formato de Resposta**: JSON
- **Encoding**: UTF-8
- **Rate Limiting**: 5 requisições/minuto por provider
- **Criptografia**: AES-256 para dados sensíveis

---

## 🔑 **AUTENTICAÇÃO**

### **Bearer Token**
Todas as requisições devem incluir um token JWT válido no header:

```http
Authorization: Bearer <seu_token_jwt>
```

### **Exemplo de Requisição Autenticada**
```bash
curl -X GET "http://localhost:8000/api/credentials/config" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 📊 **ENDPOINTS PRINCIPAIS**

### **1. VALIDAÇÃO DE CREDENCIAIS**

#### **POST** `/api/credentials/validate`

Valida uma credencial de API específica.

**Request Body:**
```json
{
  "provider": "openai",
  "credential_type": "api_key",
  "credential_value": "sk-...",
  "context": "optional_context"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "provider": "openai",
  "credential_type": "api_key",
  "validation_time": 0.125,
  "message": "Credencial válida",
  "details": {
    "model_access": ["gpt-4", "gpt-3.5-turbo"],
    "rate_limits": {
      "requests_per_minute": 60,
      "tokens_per_minute": 150000
    }
  },
  "rate_limit_info": {
    "remaining_requests": 4,
    "reset_time_seconds": 45
  }
}
```

**Response (429 Too Many Requests):**
```json
{
  "message": "Rate limit excedido",
  "retry_after": 60,
  "reason": "Too many validation attempts"
}
```

**Códigos de Erro:**
- `400` - Dados inválidos
- `401` - Não autenticado
- `429` - Rate limit excedido
- `500` - Erro interno

---

### **2. CONFIGURAÇÃO DE CREDENCIAIS**

#### **GET** `/api/credentials/config`

Obtém a configuração atual de credenciais.

**Response (200 OK):**
```json
{
  "config": {
    "ai": {
      "openai": {
        "apiKey": "encrypted_key_here",
        "enabled": true,
        "model": "gpt-4",
        "maxTokens": 4096,
        "temperature": 0.7
      },
      "deepseek": {
        "apiKey": "encrypted_key_here",
        "enabled": false,
        "model": "deepseek-chat",
        "maxTokens": 4096,
        "temperature": 0.7
      }
    },
    "social": {
      "instagram": {
        "username": "user123",
        "password": "encrypted_password",
        "sessionId": "session_123",
        "enabled": true
      }
    },
    "analytics": {
      "google_analytics": {
        "clientId": "client_id_here",
        "clientSecret": "encrypted_secret",
        "enabled": true
      }
    },
    "payments": {
      "stripe": {
        "apiKey": "encrypted_key_here",
        "webhookSecret": "encrypted_secret",
        "enabled": false
      }
    },
    "notifications": {
      "slack": {
        "webhookUrl": "https://hooks.slack.com/...",
        "enabled": true
      }
    }
  },
  "lastUpdated": "2025-01-27T10:30:00Z",
  "isValid": true,
  "validationErrors": []
}
```

#### **PUT** `/api/credentials/config`

Atualiza a configuração de credenciais.

**Request Body:**
```json
{
  "config": {
    "ai": {
      "openai": {
        "apiKey": "sk-...",
        "enabled": true,
        "model": "gpt-4",
        "maxTokens": 4096,
        "temperature": 0.7
      }
    }
  },
  "validateOnUpdate": true
}
```

**Response (200 OK):**
```json
{
  "config": {
    "ai": {
      "openai": {
        "apiKey": "encrypted_key_here",
        "enabled": true,
        "model": "gpt-4",
        "maxTokens": 4096,
        "temperature": 0.7
      }
    }
  },
  "lastUpdated": "2025-01-27T10:35:00Z",
  "isValid": true,
  "validationErrors": []
}
```

---

### **3. STATUS E MONITORAMENTO**

#### **GET** `/api/credentials/status`

Obtém o status geral das credenciais.

**Query Parameters:**
- `include_details` (boolean, opcional): Incluir detalhes completos
- `provider` (string, opcional): Filtrar por provedor específico

**Response (200 OK):**
```json
{
  "timestamp": "2025-01-27T10:30:00Z",
  "user_id": "user_123",
  "system_health": {
    "overall_score": 95.5,
    "status": "healthy",
    "last_check": "2025-01-27T10:29:00Z"
  },
  "credentials_status": {
    "openai": {
      "status": "active",
      "last_validation": "2025-01-27T10:25:00Z",
      "success_rate": 99.8,
      "error_count": 2
    },
    "instagram": {
      "status": "warning",
      "last_validation": "2025-01-27T09:15:00Z",
      "success_rate": 85.2,
      "error_count": 15
    }
  },
  "rate_limiting": {
    "total_requests": 1250,
    "blocked_requests": 23,
    "active_providers": 8
  },
  "audit_statistics": {
    "total_events": 15420,
    "security_events": 45,
    "validation_events": 12340
  }
}
```

#### **GET** `/api/credentials/status/{provider}`

Obtém o status de um provedor específico.

**Response (200 OK):**
```json
{
  "provider": "openai",
  "timestamp": "2025-01-27T10:30:00Z",
  "user_id": "user_123",
  "status": {
    "is_active": true,
    "last_validation": "2025-01-27T10:25:00Z",
    "success_rate": 99.8,
    "error_count": 2,
    "rate_limit_remaining": 45,
    "rate_limit_reset": "2025-01-27T10:35:00Z"
  },
  "recent_events": [
    {
      "timestamp": "2025-01-27T10:25:00Z",
      "event_type": "validation_success",
      "severity": "info",
      "details": {
        "response_time": 125,
        "model_access": ["gpt-4", "gpt-3.5-turbo"]
      }
    }
  ],
  "health_score": 95.5
}
```

#### **GET** `/api/credentials/health`

Obtém a saúde geral do sistema.

**Response (200 OK):**
```json
{
  "overall_score": 95.5,
  "status": "healthy",
  "last_check": "2025-01-27T10:29:00Z",
  "components": {
    "encryption": {
      "status": "healthy",
      "score": 100.0
    },
    "rate_limiting": {
      "status": "healthy",
      "score": 98.5
    },
    "audit": {
      "status": "healthy",
      "score": 95.2
    }
  },
  "alerts": []
}
```

---

### **4. ALERTAS E NOTIFICAÇÕES**

#### **GET** `/api/credentials/alerts`

Obtém alertas ativos do sistema.

**Query Parameters:**
- `severity` (string, opcional): Filtrar por severidade (info, warning, error, critical)

**Response (200 OK):**
```json
[
  {
    "id": "alert_001",
    "severity": "warning",
    "message": "Instagram credentials showing high error rate",
    "provider": "instagram",
    "timestamp": "2025-01-27T10:15:00Z",
    "details": {
      "error_rate": 15.2,
      "threshold": 10.0
    }
  }
]
```

---

### **5. OPERAÇÕES DE MANUTENÇÃO**

#### **POST** `/api/credentials/config/validate`

Valida todas as credenciais configuradas.

**Response (200 OK):**
```json
{
  "total_credentials": 12,
  "valid_credentials": 10,
  "invalid_credentials": 2,
  "validation_time": 2.45,
  "results": {
    "openai": {
      "valid": true,
      "message": "Credencial válida"
    },
    "instagram": {
      "valid": false,
      "message": "Sessão expirada"
    }
  }
}
```

#### **GET** `/api/credentials/config/backup`

Obtém backup da configuração atual.

**Response (200 OK):**
```json
{
  "backup_timestamp": "2025-01-27T10:30:00Z",
  "config_hash": "sha256:abc123...",
  "config_data": {
    "ai": { ... },
    "social": { ... },
    "analytics": { ... }
  }
}
```

#### **POST** `/api/credentials/reset/{provider}`

Reseta o rate limit de um provedor específico.

**Response (200 OK):**
```json
{
  "provider": "openai",
  "reset_successful": true,
  "reset_time": "2025-01-27T10:30:00Z",
  "new_rate_limit": {
    "remaining_requests": 5,
    "reset_time_seconds": 60
  }
}
```

---

## 🔧 **PROVIDERS SUPORTADOS**

### **IAs Generativas**
- **OpenAI**: `openai`
- **DeepSeek**: `deepseek`
- **Claude (Anthropic)**: `claude`
- **Gemini (Google)**: `gemini`

### **Redes Sociais**
- **Instagram**: `instagram`
- **TikTok**: `tiktok`
- **YouTube**: `youtube`
- **Pinterest**: `pinterest`
- **Reddit**: `reddit`

### **Analytics**
- **Google Analytics**: `google_analytics`
- **SEMrush**: `semrush`
- **Ahrefs**: `ahrefs`
- **Google Search Console**: `google_search_console`

### **Pagamentos**
- **Stripe**: `stripe`
- **PayPal**: `paypal`
- **Mercado Pago**: `mercadopago`

### **Notificações**
- **Slack**: `slack`
- **Discord**: `discord`
- **Telegram**: `telegram`

---

## 🛡️ **SEGURANÇA**

### **Criptografia**
- Todas as credenciais sensíveis são criptografadas usando AES-256
- A chave mestra é armazenada em variável de ambiente
- Rotação automática de chaves a cada 90 dias

### **Rate Limiting**
- 5 validações por minuto por provider
- Bloqueio temporário após 10 tentativas falhadas
- Reset automático após 1 hora

### **Auditoria**
- Todos os acessos são logados
- Eventos de segurança são monitorados
- Alertas automáticos para atividades suspeitas

### **Validação**
- Validação em tempo real de credenciais
- Verificação de formato antes da criptografia
- Teste de conectividade antes de salvar

---

## 📝 **EXEMPLOS DE USO**

### **Exemplo 1: Configurar OpenAI**
```bash
curl -X PUT "http://localhost:8000/api/credentials/config" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "ai": {
        "openai": {
          "apiKey": "sk-...",
          "enabled": true,
          "model": "gpt-4",
          "maxTokens": 4096,
          "temperature": 0.7
        }
      }
    },
    "validateOnUpdate": true
  }'
```

### **Exemplo 2: Validar Credencial**
```bash
curl -X POST "http://localhost:8000/api/credentials/validate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "credential_type": "api_key",
    "credential_value": "sk-..."
  }'
```

### **Exemplo 3: Verificar Status**
```bash
curl -X GET "http://localhost:8000/api/credentials/status?include_details=true" \
  -H "Authorization: Bearer <token>"
```

---

## ⚠️ **LIMITAÇÕES E CONSIDERAÇÕES**

### **Rate Limiting**
- Máximo 5 validações por minuto por provider
- Bloqueio temporário após múltiplas falhas
- Reset automático após período de cooldown

### **Tamanho de Dados**
- Máximo 1MB por requisição
- Máximo 100 providers por configuração
- Máximo 1000 caracteres por credencial

### **Performance**
- Validação: <200ms por credencial
- Configuração: <500ms para salvar
- Status: <100ms para consultar

### **Disponibilidade**
- Uptime: 99.9%
- Backup automático a cada alteração
- Recuperação automática de falhas

---

## 🔍 **TROUBLESHOOTING**

### **Erro 401 - Não Autenticado**
```json
{
  "detail": "Falha na autenticação"
}
```
**Solução**: Verificar se o token JWT é válido e não expirou.

### **Erro 429 - Rate Limit Excedido**
```json
{
  "message": "Rate limit excedido",
  "retry_after": 60
}
```
**Solução**: Aguardar o tempo especificado em `retry_after`.

### **Erro 400 - Dados Inválidos**
```json
{
  "detail": "API Key é obrigatória para openai quando habilitado"
}
```
**Solução**: Verificar se todos os campos obrigatórios estão preenchidos.

### **Erro 500 - Erro Interno**
```json
{
  "detail": "Erro ao salvar configuração"
}
```
**Solução**: Verificar logs do servidor e contatar suporte.

---

## 📞 **SUPORTE**

Para suporte técnico ou dúvidas sobre a API:

- **Email**: suporte@omnikeywordsfinder.com
- **Documentação**: https://docs.omnikeywordsfinder.com
- **Status**: https://status.omnikeywordsfinder.com
- **GitHub**: https://github.com/omnikeywordsfinder/api-issues

---

**Última atualização**: 2025-01-27
**Versão da documentação**: 1.0
**Autor**: Paulo Júnior 