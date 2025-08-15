# API Documentation - Omni Keywords Finder

## Base URL
```
https://api.omni-keywords.com/v1
```

## Autenticação
Todas as requisições devem incluir o header de autorização:
```
Authorization: Bearer <your_token>
```

## Endpoints

### Keywords

#### GET /keywords
Lista todas as keywords.

**Query Parameters:**
- `page` (int): Número da página (default: 1)
- `limit` (int): Itens por página (default: 20)
- `search` (string): Termo de busca
- `category` (string): Categoria da keyword

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "keyword": "seo optimization",
      "volume": 1000,
      "difficulty": "medium",
      "category": "marketing",
      "created_at": "2025-01-27T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### POST /keywords
Cria nova keyword.

**Request Body:**
```json
{
  "keyword": "digital marketing",
  "category": "marketing",
  "volume": 800,
  "difficulty": "low"
}
```

#### GET /keywords/{id}
Obtém keyword específica.

#### PUT /keywords/{id}
Atualiza keyword.

#### DELETE /keywords/{id}
Remove keyword.

### Analysis

#### POST /analysis/analyze
Analisa keywords.

**Request Body:**
```json
{
  "keywords": ["seo", "marketing", "digital"],
  "analysis_type": "comprehensive"
}
```

#### GET /analysis/reports
Lista relatórios de análise.

### Monitoring

#### GET /health
Health check do sistema.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T10:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api": "healthy"
  }
}
```

#### GET /metrics
Métricas do sistema (formato Prometheus).

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |

## Rate Limiting

- **Limite**: 1000 requisições por hora
- **Header**: `X-RateLimit-Remaining`
- **Reset**: `X-RateLimit-Reset`

## Exemplos

### Python
```python
import requests

headers = {
    'Authorization': 'Bearer your_token',
    'Content-Type': 'application/json'
}

# Listar keywords
response = requests.get('https://api.omni-keywords.com/v1/keywords', headers=headers)
keywords = response.json()

# Criar keyword
data = {
    'keyword': 'seo optimization',
    'category': 'marketing'
}
response = requests.post('https://api.omni-keywords.com/v1/keywords', 
                        headers=headers, json=data)
```

### JavaScript
```javascript
const headers = {
    'Authorization': 'Bearer your_token',
    'Content-Type': 'application/json'
};

// Listar keywords
const response = await fetch('https://api.omni-keywords.com/v1/keywords', {
    headers
});
const keywords = await response.json();
```

## Webhooks

### Configuração
```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["keyword.created", "analysis.completed"],
  "secret": "your_webhook_secret"
}
```

### Payload
```json
{
  "event": "keyword.created",
  "timestamp": "2025-01-27T10:00:00Z",
  "data": {
    "keyword_id": 123,
    "keyword": "seo optimization"
  }
}
```
