# 📚 **DOCUMENTAÇÃO MANUAL DE ENDPOINTS - OMNİ KEYWORDS FINDER API**

## 🎯 **VISÃO GERAL**

Esta documentação fornece informações detalhadas sobre todos os endpoints da API do Omni Keywords Finder, incluindo exemplos de uso, códigos de resposta e casos de uso específicos.

---

## 🔐 **AUTENTICAÇÃO**

### **Base URL**
- **Produção**: `https://api.omnikeywordsfinder.com/v1`
- **Staging**: `https://staging-api.omnikeywordsfinder.com/v1`
- **Desenvolvimento**: `http://localhost:8000/v1`

### **Autenticação JWT**
Todos os endpoints protegidos requerem um token JWT Bearer no header `Authorization`:

```http
Authorization: Bearer <seu_token_jwt>
```

---

## 📋 **ENDPOINTS DE AUTENTICAÇÃO**

### **POST /auth/login**
**Descrição**: Autentica o usuário e retorna token JWT

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Resposta de Sucesso (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123456789",
    "email": "user@example.com",
    "name": "João Silva",
    "company": "Minha Empresa LTDA",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z"
  }
}
```

**Resposta de Erro (401)**:
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Credenciais inválidas",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

**Casos de Uso**:
- Login inicial do usuário
- Renovação de sessão
- Validação de credenciais

---

### **POST /auth/register**
**Descrição**: Cria uma nova conta de usuário

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "João Silva",
  "company": "Minha Empresa LTDA"
}
```

**Resposta de Sucesso (201)**:
```json
{
  "id": "user_123456789",
  "email": "newuser@example.com",
  "name": "João Silva",
  "company": "Minha Empresa LTDA",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Resposta de Erro (409)**:
```json
{
  "error": "EMAIL_ALREADY_EXISTS",
  "message": "Email já cadastrado",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

**Casos de Uso**:
- Registro de novos usuários
- Criação de contas corporativas
- Onboarding de clientes

---

## 🔍 **ENDPOINTS DE PALAVRAS-CHAVE**

### **POST /keywords/search**
**Descrição**: Realiza busca avançada de palavras-chave com filtros e análise semântica

**Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>
```

**Body**:
```json
{
  "query": "marketing digital",
  "filters": {
    "language": "pt-BR",
    "region": "BR",
    "difficulty": "medium",
    "volume_range": {
      "min": 1000,
      "max": 10000
    }
  },
  "semantic_analysis": true,
  "include_related": true,
  "limit": 20
}
```

**Parâmetros de Filtro**:
- `language`: `pt-BR`, `en-US`, `es-ES`
- `difficulty`: `easy`, `medium`, `hard`
- `volume_range.min`: Volume mínimo de busca
- `volume_range.max`: Volume máximo de busca

**Resposta de Sucesso (200)**:
```json
{
  "keywords": [
    {
      "id": "kw_123456789",
      "keyword": "marketing digital",
      "search_volume": 5400,
      "difficulty": "medium",
      "cpc": 2.45,
      "competition": 0.75,
      "trend": "rising",
      "related_keywords": ["digital marketing", "marketing online"],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1,
  "search_metadata": {
    "query": "marketing digital",
    "filters_applied": {
      "language": "pt-BR",
      "region": "BR",
      "difficulty": "medium"
    },
    "processing_time": 0.85,
    "sources_used": ["google_ads", "google_trends", "semrush"]
  }
}
```

**Casos de Uso**:
- Pesquisa de palavras-chave para SEO
- Análise de mercado
- Descoberta de oportunidades
- Planejamento de campanhas

---

### **POST /keywords/analyze**
**Descrição**: Realiza análise completa de uma palavra-chave específica

**Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>
```

**Body**:
```json
{
  "keyword": "marketing digital",
  "include_competition": true,
  "include_trends": true,
  "include_suggestions": true
}
```

**Resposta de Sucesso (200)**:
```json
{
  "keyword": {
    "id": "kw_123456789",
    "keyword": "marketing digital",
    "search_volume": 5400,
    "difficulty": "medium",
    "cpc": 2.45,
    "competition": 0.75,
    "trend": "rising",
    "related_keywords": ["digital marketing", "marketing online"],
    "created_at": "2024-01-15T10:30:00Z"
  },
  "competition_analysis": {
    "top_competitors": [
      {
        "domain": "example.com",
        "authority": 85,
        "backlinks": 15000
      }
    ],
    "difficulty_score": 0.75
  },
  "trend_analysis": {
    "historical_data": [
      {
        "date": "2024-01-01",
        "volume": 5000
      }
    ],
    "forecast": {
      "next_month": 5800,
      "next_quarter": 6200
    }
  },
  "suggestions": [
    {
      "id": "kw_987654321",
      "keyword": "digital marketing",
      "search_volume": 4800,
      "difficulty": "medium",
      "cpc": 2.10,
      "competition": 0.70,
      "trend": "stable"
    }
  ],
  "seo_insights": {
    "content_gaps": ["Como fazer marketing digital", "Marketing digital para iniciantes"],
    "content_opportunities": ["Guia completo de marketing digital", "Estratégias de marketing digital"]
  }
}
```

**Casos de Uso**:
- Análise detalhada de palavras-chave
- Planejamento de conteúdo
- Análise de competição
- Previsão de tendências

---

## 📁 **ENDPOINTS DE COLEÇÕES**

### **GET /collections**
**Descrição**: Retorna todas as coleções de palavras-chave do usuário

**Headers**:
```http
Authorization: Bearer <token>
```

**Query Parameters**:
- `page`: Número da página (padrão: 1)
- `limit`: Limite de resultados por página (padrão: 20, máximo: 100)

**Exemplo de Requisição**:
```http
GET /collections?page=1&limit=20
```

**Resposta de Sucesso (200)**:
```json
{
  "collections": [
    {
      "id": "col_123456789",
      "name": "Marketing Digital 2024",
      "description": "Palavras-chave para campanhas de marketing digital",
      "tags": ["marketing", "digital", "2024"],
      "is_public": false,
      "keyword_count": 150,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z",
      "owner": {
        "id": "user_123456789",
        "email": "user@example.com",
        "name": "João Silva"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

**Casos de Uso**:
- Listagem de coleções do usuário
- Organização de palavras-chave
- Compartilhamento de pesquisas

---

### **POST /collections**
**Descrição**: Cria uma nova coleção de palavras-chave

**Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>
```

**Body**:
```json
{
  "name": "Marketing Digital 2024",
  "description": "Palavras-chave para campanhas de marketing digital",
  "tags": ["marketing", "digital", "2024"],
  "is_public": false
}
```

**Resposta de Sucesso (201)**:
```json
{
  "id": "col_123456789",
  "name": "Marketing Digital 2024",
  "description": "Palavras-chave para campanhas de marketing digital",
  "tags": ["marketing", "digital", "2024"],
  "is_public": false,
  "keyword_count": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "owner": {
    "id": "user_123456789",
    "email": "user@example.com",
    "name": "João Silva"
  }
}
```

**Casos de Uso**:
- Criação de coleções personalizadas
- Organização de pesquisas
- Compartilhamento de dados

---

## 📊 **ENDPOINTS DE ANALYTICS**

### **GET /analytics/overview**
**Descrição**: Retorna métricas gerais de uso e performance

**Headers**:
```http
Authorization: Bearer <token>
```

**Query Parameters**:
- `period`: Período de análise (`day`, `week`, `month`, `quarter`, `year`)
- `start_date`: Data de início (YYYY-MM-DD)
- `end_date`: Data de fim (YYYY-MM-DD)

**Exemplo de Requisição**:
```http
GET /analytics/overview?period=month
```

**Resposta de Sucesso (200)**:
```json
{
  "period": "month",
  "searches_performed": 1250,
  "keywords_analyzed": 3400,
  "collections_created": 25,
  "api_calls": 8900,
  "top_searched_keywords": [
    {
      "keyword": "marketing digital",
      "count": 45
    }
  ],
  "usage_trends": {
    "daily": [
      {
        "date": "2024-01-15",
        "searches": 42
      }
    ]
  }
}
```

**Casos de Uso**:
- Dashboard de analytics
- Relatórios de uso
- Monitoramento de performance
- Análise de tendências

---

## 💬 **ENDPOINTS DE FEEDBACK**

### **POST /feedback**
**Descrição**: Envia feedback do usuário sobre o sistema

**Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>
```

**Body**:
```json
{
  "type": "feature",
  "message": "Gostaria de ver mais opções de filtros na busca de palavras-chave",
  "rating": 4,
  "category": "search",
  "contact_email": "user@example.com"
}
```

**Tipos de Feedback**:
- `bug`: Report de bug
- `feature`: Solicitação de feature
- `general`: Feedback geral
- `praise`: Elogio

**Resposta de Sucesso (201)**:
```json
{
  "id": "fb_123456789",
  "message": "Feedback recebido com sucesso"
}
```

**Casos de Uso**:
- Report de bugs
- Solicitação de features
- Avaliação do sistema
- Melhoria contínua

---

## ⚠️ **CÓDIGOS DE ERRO COMUNS**

### **400 Bad Request**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Dados de entrada inválidos",
  "details": [
    {
      "field": "email",
      "message": "Email inválido",
      "code": "INVALID_EMAIL"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### **401 Unauthorized**
```json
{
  "error": "UNAUTHORIZED",
  "message": "Token de autenticação inválido ou expirado",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### **403 Forbidden**
```json
{
  "error": "FORBIDDEN",
  "message": "Acesso negado para este recurso",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### **404 Not Found**
```json
{
  "error": "NOT_FOUND",
  "message": "Recurso não encontrado",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### **429 Too Many Requests**
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Limite de requisições excedido",
  "retry_after": 60,
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### **500 Internal Server Error**
```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "Erro interno do servidor",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

---

## 🔧 **RATE LIMITING**

### **Limites por Plano**
- **Free**: 100 requests/hora
- **Basic**: 1.000 requests/hora
- **Pro**: 10.000 requests/hora
- **Enterprise**: 100.000 requests/hora

### **Headers de Rate Limiting**
```http
X-Rate-Limit-Limit: 1000
X-Rate-Limit-Remaining: 999
X-Rate-Limit-Reset: 1642233600
```

---

## 📝 **EXEMPLOS DE USO**

### **Fluxo Completo de Busca**
1. **Login** → POST /auth/login
2. **Buscar Palavras-chave** → POST /keywords/search
3. **Analisar Palavra-chave** → POST /keywords/analyze
4. **Criar Coleção** → POST /collections
5. **Ver Analytics** → GET /analytics/overview

### **Exemplo com cURL**
```bash
# Login
curl -X POST https://api.omnikeywordsfinder.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Buscar palavras-chave
curl -X POST https://api.omnikeywordsfinder.com/v1/keywords/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "marketing digital", "limit": 10}'
```

### **Exemplo com JavaScript**
```javascript
// Login
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { access_token } = await loginResponse.json();

// Buscar palavras-chave
const searchResponse = await fetch('/keywords/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    query: 'marketing digital',
    limit: 10
  })
});

const keywords = await searchResponse.json();
```

---

## 🔗 **LINKS ÚTEIS**

- **Documentação Interativa**: https://api.omnikeywordsfinder.com/v1/api/docs
- **Status da API**: https://status.omnikeywordsfinder.com
- **Suporte**: support@omnikeywordsfinder.com
- **Changelog**: https://docs.omnikeywordsfinder.com/changelog

---

## 📞 **SUPORTE**

Para dúvidas sobre a API, entre em contato:
- **Email**: support@omnikeywordsfinder.com
- **Documentação**: https://docs.omnikeywordsfinder.com
- **Status**: https://status.omnikeywordsfinder.com 