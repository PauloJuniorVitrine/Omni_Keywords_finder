# 🔐 **DOCUMENTAÇÃO DA API DE CREDENCIAIS - OMNİ KEYWORDS FINDER**

**Tracing ID**: `API_CREDENTIALS_DOC_001`  
**Data/Hora**: 2024-12-27 18:30:00 UTC  
**Versão**: 1.0.0  
**Status**: ✅ **CONCLUÍDO**

---

## 🎯 **VISÃO GERAL**

A API de Credenciais do Omni Keywords Finder fornece endpoints seguros para gerenciamento, validação e monitoramento de credenciais de API de diversos provedores (IAs Generativas, Redes Sociais, Analytics, Pagamentos, Notificações).

### **Características Principais**
- 🔒 **Criptografia AES-256** para todas as credenciais sensíveis
- 🛡️ **Rate Limiting** inteligente por provedor
- 📊 **Auditoria completa** de todas as operações
- 🔍 **Validação em tempo real** de credenciais
- 📈 **Monitoramento** e métricas detalhadas
- 🔄 **Fallback automático** entre provedores

### **Informações da API**
- **Base URL**: `/api/credentials`
- **Versão**: 1.0.0
- **Autenticação**: JWT Bearer Token
- **Formato**: JSON
- **Criptografia**: AES-256

---

## 🔐 **AUTENTICAÇÃO**

### **Header de Autenticação**
```http
Authorization: Bearer <seu_token_jwt>
```

### **Exemplo de Token**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

---

## 📋 **ENDPOINTS PRINCIPAIS**

### **1. VALIDAÇÃO DE CREDENCIAIS**

#### **Validar Credencial**
```http
POST /api/credentials/validate
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**
```json
{
    "provider": "openai",
    "credential_type": "api_key",
    "credential_value": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
    "context": "test_validation"
}
```

**Resposta de Sucesso (200)**
```json
{
    "valid": true,
    "provider": "openai",
    "credential_type": "api_key",
    "validation_time": 0.045,
    "message": "Credencial válida",
    "details": {
        "encrypted": true,
        "context": "test_validation"
    },
    "rate_limit_info": {
        "remaining": 4,
        "reset_time": 1703692800
    }
}
```

**Resposta de Erro (400)**
```json
{
    "valid": false,
    "provider": "openai",
    "credential_type": "api_key",
    "validation_time": 0.023,
    "message": "Credencial inválida",
    "details": {
        "encrypted": false,
        "context": "test_validation",
        "error": "Formato de chave inválido"
    },
    "rate_limit_info": {
        "remaining": 4,
        "reset_time": 1703692800
    }
}
```

**Códigos de Erro**
- `400`: Dados inválidos
- `401`: Token inválido
- `429`: Rate limit excedido
- `500`: Erro interno do servidor

---

### **2. CONFIGURAÇÃO DE CREDENCIAIS**

#### **Obter Configuração**
```http
GET /api/credentials/config
Authorization: Bearer <token>
```

**Resposta de Sucesso (200)**
```json
{
    "config": {
        "ai": {
            "openai": {
                "apiKey": "encrypted:abc123...",
                "enabled": true,
                "model": "gpt-4",
                "maxTokens": 4096,
                "temperature": 0.7
            },
            "deepseek": {
                "apiKey": "encrypted:def456...",
                "enabled": true,
                "model": "deepseek-chat",
                "maxTokens": 4096,
                "temperature": 0.7
            },
            "claude": {
                "apiKey": "encrypted:ghi789...",
                "enabled": false,
                "model": "claude-3-sonnet",
                "maxTokens": 4096,
                "temperature": 0.7
            },
            "gemini": {
                "apiKey": "encrypted:jkl012...",
                "enabled": false,
                "model": "gemini-pro",
                "maxTokens": 4096,
                "temperature": 0.7
            }
        },
        "social": {
            "instagram": {
                "username": "user123",
                "password": "encrypted:pass123...",
                "sessionId": "session123",
                "enabled": false
            },
            "tiktok": {
                "apiKey": "encrypted:tiktok123...",
                "apiSecret": "encrypted:secret123...",
                "enabled": false
            },
            "youtube": {
                "apiKey": "encrypted:youtube123...",
                "clientId": "client123",
                "clientSecret": "encrypted:clientsecret123...",
                "enabled": false
            },
            "pinterest": {
                "accessToken": "encrypted:pinterest123...",
                "enabled": false
            },
            "reddit": {
                "clientId": "reddit123",
                "clientSecret": "encrypted:redditsecret123...",
                "enabled": false
            }
        },
        "analytics": {
            "google_analytics": {
                "clientId": "ga123",
                "clientSecret": "encrypted:gasecret123...",
                "enabled": false
            },
            "semrush": {
                "apiKey": "encrypted:semrush123...",
                "enabled": false
            },
            "ahrefs": {
                "apiKey": "encrypted:ahrefs123...",
                "enabled": false
            },
            "google_search_console": {
                "clientId": "gsc123",
                "clientSecret": "encrypted:gscsecret123...",
                "refreshToken": "encrypted:refresh123...",
                "enabled": false
            }
        },
        "payments": {
            "stripe": {
                "apiKey": "encrypted:stripe123...",
                "webhookSecret": "encrypted:webhook123...",
                "enabled": false
            },
            "paypal": {
                "clientId": "paypal123",
                "clientSecret": "encrypted:paypalsecret123...",
                "enabled": false
            },
            "mercado_pago": {
                "accessToken": "encrypted:mp123...",
                "enabled": false
            }
        },
        "notifications": {
            "slack": {
                "webhookUrl": "https://hooks.slack.com/services/...",
                "enabled": false
            },
            "discord": {
                "botToken": "encrypted:discord123...",
                "enabled": false
            },
            "telegram": {
                "botToken": "encrypted:telegram123...",
                "enabled": false
            }
        }
    },
    "lastUpdated": "2024-12-27T18:30:00Z",
    "isValid": true,
    "validationErrors": []
}
```

#### **Atualizar Configuração**
```http
PUT /api/credentials/config
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**
```json
{
    "config": {
        "ai": {
            "openai": {
                "apiKey": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
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

**Resposta de Sucesso (200)**
```json
{
    "config": {
        "ai": {
            "openai": {
                "apiKey": "encrypted:abc123...",
                "enabled": true,
                "model": "gpt-4",
                "maxTokens": 4096,
                "temperature": 0.7
            }
        }
    },
    "lastUpdated": "2024-12-27T18:30:00Z",
    "isValid": true,
    "validationErrors": []
}
```

#### **Validar Configuração**
```http
POST /api/credentials/config/validate
Authorization: Bearer <token>
```

**Resposta de Sucesso (200)**
```json
{
    "isValid": true,
    "errors": [],
    "validatedAt": "2024-12-27T18:30:00Z"
}
```

---

### **3. STATUS E MONITORAMENTO**

#### **Status Geral**
```http
GET /api/credentials/status
Authorization: Bearer <token>
```

**Query Parameters**
- `include_details` (boolean, opcional): Incluir detalhes completos
- `provider` (string, opcional): Filtrar por provedor específico

**Resposta de Sucesso (200)**
```json
{
    "timestamp": "2024-12-27T18:30:00Z",
    "user_id": "user_123",
    "system_health": {
        "overall_health": "healthy",
        "encryption_status": "operational",
        "rate_limiting_status": "normal",
        "last_check": "2024-12-27T18:30:00Z"
    },
    "credentials_status": {
        "openai": {
            "status": "healthy",
            "last_validation": "2024-12-27T18:25:00Z",
            "success_rate": 99.8,
            "response_time_avg": 45.2
        },
        "deepseek": {
            "status": "healthy",
            "last_validation": "2024-12-27T18:28:00Z",
            "success_rate": 99.9,
            "response_time_avg": 38.7
        }
    },
    "rate_limiting": {
        "total_requests": 1250,
        "blocked_requests": 12,
        "active_providers": 8,
        "blocked_providers": 0
    },
    "audit_statistics": {
        "total_events": 15420,
        "successful_events": 15380,
        "failed_events": 40,
        "last_24h_events": 1250
    },
    "last_updated": "2024-12-27T18:30:00Z"
}
```

#### **Status por Provedor**
```http
GET /api/credentials/status/{provider}
Authorization: Bearer <token>
```

**Resposta de Sucesso (200)**
```json
{
    "provider": "openai",
    "timestamp": "2024-12-27T18:30:00Z",
    "user_id": "user_123",
    "status": {
        "status": "healthy",
        "last_validation": "2024-12-27T18:25:00Z",
        "success_rate": 99.8,
        "response_time_avg": 45.2,
        "total_requests": 850,
        "failed_requests": 2
    },
    "recent_events": [
        {
            "timestamp": "2024-12-27T18:25:00Z",
            "event_type": "credential_validated",
            "severity": "info",
            "details": {
                "valid": true,
                "validation_time": 0.045
            }
        }
    ],
    "health_score": 98.5
}
```

#### **Saúde do Sistema**
```http
GET /api/credentials/health
Authorization: Bearer <token>
```

**Resposta de Sucesso (200)**
```json
{
    "overall_health": "healthy",
    "encryption_status": "operational",
    "rate_limiting_status": "normal",
    "audit_status": "operational",
    "last_check": "2024-12-27T18:30:00Z",
    "uptime": "99.98%",
    "response_time_avg": 42.3
}
```

---

### **4. MÉTRICAS E ESTATÍSTICAS**

#### **Métricas Detalhadas**
```http
GET /api/credentials/metrics
Authorization: Bearer <token>
```

**Resposta de Sucesso (200)**
```json
{
    "total_requests": 15420,
    "blocked_requests": 12,
    "anomaly_detections": 5,
    "active_providers": 8,
    "blocked_providers": 0,
    "encryption_metrics": {
        "encryption_operations": 12500,
        "decryption_operations": 12500,
        "errors": 0,
        "avg_operation_time": 2.3
    },
    "rate_limit_metrics": {
        "total_checks": 15420,
        "rate_limited": 12,
        "avg_response_time": 1.2,
        "peak_requests_per_minute": 45
    },
    "validation_metrics": {
        "total_validations": 12500,
        "successful_validations": 12480,
        "failed_validations": 20,
        "avg_validation_time": 45.2
    },
    "audit_metrics": {
        "total_events": 15420,
        "events_last_24h": 1250,
        "events_last_7d": 8500,
        "storage_used_mb": 45.2
    }
}
```

---

## 🔧 **PROVEDORES SUPORTADOS**

### **IAs Generativas**

#### **OpenAI**
- **Tipo**: `openai`
- **Formato da Chave**: `sk-proj-` + 48 caracteres
- **Endpoint**: `/api/credentials/validate`
- **Configuração**: `ai.openai`

#### **DeepSeek**
- **Tipo**: `deepseek`
- **Formato da Chave**: `sk-` + 48 caracteres
- **Endpoint**: `/api/credentials/validate`
- **Configuração**: `ai.deepseek`

#### **Claude (Anthropic)**
- **Tipo**: `claude`
- **Formato da Chave**: `sk-ant-api03-` + 48 caracteres
- **Endpoint**: `/api/credentials/validate`
- **Configuração**: `ai.claude`

#### **Gemini (Google)**
- **Tipo**: `gemini`
- **Formato da Chave**: `AIzaSy` + 35 caracteres
- **Endpoint**: `/api/credentials/validate`
- **Configuração**: `ai.gemini`

### **Redes Sociais**

#### **Instagram**
- **Tipo**: `instagram`
- **Campos**: `username`, `password`, `sessionId`
- **Configuração**: `social.instagram`

#### **TikTok**
- **Tipo**: `tiktok`
- **Campos**: `apiKey`, `apiSecret`
- **Configuração**: `social.tiktok`

#### **YouTube**
- **Tipo**: `youtube`
- **Campos**: `apiKey`, `clientId`, `clientSecret`
- **Configuração**: `social.youtube`

#### **Pinterest**
- **Tipo**: `pinterest`
- **Campos**: `accessToken`
- **Configuração**: `social.pinterest`

#### **Reddit**
- **Tipo**: `reddit`
- **Campos**: `clientId`, `clientSecret`
- **Configuração**: `social.reddit`

### **Analytics**

#### **Google Analytics**
- **Tipo**: `google_analytics`
- **Campos**: `clientId`, `clientSecret`
- **Configuração**: `analytics.google_analytics`

#### **SEMrush**
- **Tipo**: `semrush`
- **Campos**: `apiKey`
- **Configuração**: `analytics.semrush`

#### **Ahrefs**
- **Tipo**: `ahrefs`
- **Campos**: `apiKey`
- **Configuração**: `analytics.ahrefs`

#### **Google Search Console**
- **Tipo**: `google_search_console`
- **Campos**: `clientId`, `clientSecret`, `refreshToken`
- **Configuração**: `analytics.google_search_console`

### **Pagamentos**

#### **Stripe**
- **Tipo**: `stripe`
- **Campos**: `apiKey`, `webhookSecret`
- **Configuração**: `payments.stripe`

#### **PayPal**
- **Tipo**: `paypal`
- **Campos**: `clientId`, `clientSecret`
- **Configuração**: `payments.paypal`

#### **Mercado Pago**
- **Tipo**: `mercado_pago`
- **Campos**: `accessToken`
- **Configuração**: `payments.mercado_pago`

### **Notificações**

#### **Slack**
- **Tipo**: `slack`
- **Campos**: `webhookUrl`
- **Configuração**: `notifications.slack`

#### **Discord**
- **Tipo**: `discord`
- **Campos**: `botToken`
- **Configuração**: `notifications.discord`

#### **Telegram**
- **Tipo**: `telegram`
- **Campos**: `botToken`
- **Configuração**: `notifications.telegram`

---

## 🛡️ **SEGURANÇA**

### **Criptografia**
- **Algoritmo**: AES-256-GCM
- **Chave Mestra**: Armazenada em variável de ambiente
- **Prefix**: `encrypted:` para credenciais criptografadas
- **Rotação**: Suporte a rotação automática de chaves

### **Rate Limiting**
- **Limite**: 5 requisições por minuto por provedor
- **Janela**: 60 segundos
- **Estratégia**: Token Bucket
- **Headers**: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### **Auditoria**
- **Logs**: JSONL estruturados
- **Eventos**: Todas as operações registradas
- **Retenção**: 90 dias
- **Compliance**: GDPR, SOC 2, ISO 27001

---

## 📊 **CÓDIGOS DE ERRO**

### **HTTP Status Codes**
- `200`: Sucesso
- `201`: Criado
- `400`: Dados inválidos
- `401`: Não autorizado
- `403`: Proibido
- `404`: Não encontrado
- `429`: Rate limit excedido
- `500`: Erro interno do servidor

### **Códigos de Erro Específicos**
```json
{
    "error_codes": {
        "CREDENTIAL_INVALID": "Credencial inválida",
        "PROVIDER_NOT_SUPPORTED": "Provedor não suportado",
        "RATE_LIMIT_EXCEEDED": "Rate limit excedido",
        "ENCRYPTION_ERROR": "Erro de criptografia",
        "VALIDATION_ERROR": "Erro de validação",
        "AUDIT_ERROR": "Erro de auditoria",
        "CONFIG_ERROR": "Erro de configuração"
    }
}
```

---

## 🔄 **EXEMPLOS DE USO**

### **Exemplo 1: Validar Credencial OpenAI**
```bash
curl -X POST "http://localhost:5000/api/credentials/validate" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "credential_type": "api_key",
    "credential_value": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
    "context": "production"
  }'
```

### **Exemplo 2: Obter Configuração**
```bash
curl -X GET "http://localhost:5000/api/credentials/config" \
  -H "Authorization: Bearer your_token"
```

### **Exemplo 3: Atualizar Configuração**
```bash
curl -X PUT "http://localhost:5000/api/credentials/config" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "ai": {
        "openai": {
          "apiKey": "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz",
          "enabled": true,
          "model": "gpt-4"
        }
      }
    },
    "validateOnUpdate": true
  }'
```

### **Exemplo 4: Verificar Status**
```bash
curl -X GET "http://localhost:5000/api/credentials/status?include_details=true" \
  -H "Authorization: Bearer your_token"
```

---

## 📚 **REFERÊNCIAS**

### **Documentação Relacionada**
- [Guia de Autenticação](../guides/auth.md)
- [Guia de Segurança](../guides/security.md)
- [Guia de Monitoramento](../guides/monitoring.md)
- [OpenAPI Specification](../openapi.yaml)

### **Links Úteis**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT.io](https://jwt.io/)
- [AES Encryption](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

---

## 🤝 **SUPORTE**

### **Contato**
- **Email**: api-support@omni-keywords-finder.com
- **Documentação**: https://docs.omni-keywords-finder.com
- **Status**: https://status.omni-keywords-finder.com

### **Comunidade**
- **GitHub**: https://github.com/omni-keywords-finder
- **Discord**: https://discord.gg/omni-keywords-finder
- **Stack Overflow**: Tag: `omni-keywords-finder`

---

**Última Atualização**: 2024-12-27 18:30:00 UTC  
**Versão da Documentação**: 1.0.0  
**Próxima Revisão**: 2025-01-27 