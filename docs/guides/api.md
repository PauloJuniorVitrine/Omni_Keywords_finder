# Guia da API

## Visão Geral

A API do Omni Keywords Finder segue o padrão REST e utiliza OpenAPI 3.0 para documentação.

## Autenticação

```http
Authorization: Bearer <token>
```

## Endpoints

### 1. Keywords

#### Extrair Keywords
```http
POST /api/v1/keywords/extract
Content-Type: application/json

{
    "text": "string",
    "language": "string",
    "max_keywords": integer
}
```

**Resposta**
```json
{
    "keywords": [
        {
            "text": "string",
            "score": float,
            "language": "string"
        }
    ]
}
```

#### Listar Keywords
```http
GET /api/v1/keywords
Query Parameters:
- page: integer
- limit: integer
- language: string
- sort: string
```

**Resposta**
```json
{
    "items": [
        {
            "id": "string",
            "text": "string",
            "score": float,
            "language": "string",
            "created_at": "datetime"
        }
    ],
    "total": integer,
    "page": integer,
    "limit": integer
}
```

### 2. Usuários

#### Registrar
```http
POST /api/v1/users/register
Content-Type: application/json

{
    "email": "string",
    "password": "string",
    "name": "string"
}
```

#### Login
```http
POST /api/v1/users/login
Content-Type: application/json

{
    "email": "string",
    "password": "string"
}
```

**Resposta**
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": integer
}
```

### 3. Modelos

#### Listar Modelos
```http
GET /api/v1/models
```

**Resposta**
```json
{
    "models": [
        {
            "id": "string",
            "name": "string",
            "version": "string",
            "language": "string",
            "accuracy": float
        }
    ]
}
```

#### Treinar Modelo
```http
POST /api/v1/models/train
Content-Type: application/json

{
    "name": "string",
    "language": "string",
    "data": [
        {
            "text": "string",
            "keywords": ["string"]
        }
    ]
}
```

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Token inválido |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Erro interno |

## Rate Limiting

- 100 requisições por minuto por IP
- 1000 requisições por hora por usuário
- Headers de resposta:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining
  - X-RateLimit-Reset

## Exemplos

### Python
```python
import requests

# Configuração
API_URL = "http://localhost:8000/api/v1"
TOKEN = "your-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Extrair keywords
response = requests.post(
    f"{API_URL}/keywords/extract",
    headers=headers,
    json={
        "text": "Python é uma linguagem de programação",
        "language": "pt",
        "max_keywords": 5
    }
)

print(response.json())
```

### JavaScript
```javascript
const API_URL = "http://localhost:8000/api/v1";
const TOKEN = "your-token";

// Extrair keywords
async function extractKeywords(text) {
    const response = await fetch(`${API_URL}/keywords/extract`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${TOKEN}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            text,
            language: "pt",
            max_keywords: 5
        })
    });
    
    return response.json();
}
```

## Webhooks

### Configurar Webhook
```http
POST /api/v1/webhooks
Content-Type: application/json

{
    "url": "string",
    "events": ["keyword.created", "model.trained"],
    "secret": "string"
}
```

### Eventos Disponíveis
- keyword.created
- keyword.updated
- keyword.deleted
- model.trained
- model.updated
- user.registered
- user.updated

## Paginação

Todos os endpoints de listagem suportam paginação:

- page: Número da página (default: 1)
- limit: Itens por página (default: 20, max: 100)
- sort: Campo para ordenação (ex: -created_at)
- filter: Filtros específicos por endpoint

## Compressão

A API suporta compressão gzip:

```http
Accept-Encoding: gzip
```

## Cache

Respostas são cacheadas por 5 minutos por padrão. Headers de cache:

- Cache-Control: max-age=300
- ETag: "hash"
- Last-Modified: timestamp 