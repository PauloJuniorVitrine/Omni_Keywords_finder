# 📚 Documentação da API - Omni Keywords Finder

## 📋 Visão Geral

Esta documentação descreve a API completa do Omni Keywords Finder, incluindo todos os endpoints, schemas, códigos de erro e exemplos de uso.

## 🗂️ Estrutura da Documentação

### Arquivos Principais

- **`swagger.yaml`** - Especificação OpenAPI 3.0.3 completa
- **`swagger_generated.yaml`** - Documentação gerada automaticamente
- **`postman_collection.json`** - Coleção Postman para testes
- **`redoc.html`** - Interface visual da documentação

### Documentação por Tópico

- **`authentication.md`** - Guia de autenticação e autorização
- **`endpoints.md`** - Lista completa de endpoints
- **`error_codes.md`** - Códigos de erro padronizados
- **`rate_limiting.md`** - Políticas de rate limiting

## 🚀 Como Usar

### 1. Autenticação

```bash
# Login para obter token JWT
curl -X POST https://api.omnikeywordsfinder.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seu_usuario",
    "senha": "sua_senha"
  }'
```

### 2. Usar Token

```bash
# Fazer requisição autenticada
curl -X GET https://api.omnikeywordsfinder.com/v1/execucoes \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

## 🛡️ Sistema de Tratamento de Erros

### Resposta de Erro Padronizada

Todos os endpoints retornam erros no formato padronizado:

```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Dados de entrada inválidos",
  "details": {
    "validation_errors": [
      {
        "field": "username",
        "value": "",
        "message": "Campo obrigatório",
        "suggestion": "Campo é obrigatório"
      }
    ]
  },
  "timestamp": "2025-01-27T10:30:00Z",
  "request_id": "req_123456789",
  "path": "/api/auth/login",
  "method": "POST"
}
```

### Códigos de Erro Principais

| Código | Descrição | HTTP Status |
|--------|-----------|-------------|
| `VALIDATION_ERROR` | Dados de entrada inválidos | 400 |
| `UNAUTHORIZED` | Não autorizado | 401 |
| `FORBIDDEN` | Acesso negado | 403 |
| `RESOURCE_NOT_FOUND` | Recurso não encontrado | 404 |
| `RATE_LIMIT_EXCEEDED` | Limite de taxa excedido | 429 |
| `INTERNAL_ERROR` | Erro interno do servidor | 500 |

## 📊 Rate Limiting

### Limites por Tipo de Usuário

| Tipo | Requests/Hora | Requests/Minuto |
|------|---------------|-----------------|
| Free | 100 | 10 |
| Basic | 1.000 | 100 |
| Premium | 10.000 | 1.000 |
| Enterprise | 100.000 | 10.000 |

### Headers de Rate Limiting

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643270400
Retry-After: 60
```

## 🔧 Geração Automática de Documentação

### Gerador de Documentação

A documentação é gerada automaticamente usando o `APIDocsGenerator`:

```python
from backend.app.utils.api_docs_generator import generate_api_documentation

# Gerar documentação
generate_api_documentation()
```

### Atualizar Documentação

```bash
# Executar gerador
python -m backend.app.utils.api_docs_generator

# Ou usar script dedicado
python scripts/generate_docs.py
```

## 📝 Endpoints Principais

### Autenticação

- `POST /auth/login` - Login de usuário
- `POST /auth/register` - Registro de usuário
- `POST /auth/logout` - Logout
- `GET /auth/oauth2/login/{provider}` - Login OAuth2
- `GET /auth/oauth2/callback/{provider}` - Callback OAuth2

### Execuções

- `POST /execucoes/` - Executar prompt
- `GET /execucoes/` - Listar execuções
- `GET /execucoes/{id}` - Detalhes da execução
- `POST /execucoes/lote` - Execução em lote
- `GET /execucoes/lote/status` - Status do lote

### Pagamentos

- `POST /payments/create-payment-intent` - Criar PaymentIntent
- `POST /payments/confirm-payment` - Confirmar pagamento
- `POST /payments/refund` - Reembolso
- `GET /payments/history` - Histórico de pagamentos
- `POST /webhooks/stripe` - Webhook Stripe

### RBAC

- `GET /rbac/roles` - Listar roles
- `POST /rbac/roles` - Criar role
- `PUT /rbac/roles/{id}` - Atualizar role
- `DELETE /rbac/roles/{id}` - Excluir role
- `GET /rbac/permissions` - Listar permissões

### Auditoria

- `GET /auditoria/logs` - Consultar logs
- `GET /auditoria/estatisticas` - Estatísticas
- `GET /auditoria/relatorios` - Relatórios
- `POST /auditoria/exportar` - Exportar logs
- `GET /auditoria/download/{filename}` - Download de arquivo

### Métricas de Negócio

- `POST /business_metrics/coletar` - Coletar métricas
- `GET /business_metrics/analise` - Análise de métricas
- `GET /business_metrics/kpis` - KPIs
- `GET /business_metrics/dashboards` - Dashboards

### Consumo Externo

- `POST /consumo_externo/processar` - Processar dados externos
- `GET /consumo_externo/status` - Status do processamento
- `POST /consumo_externo/validar` - Validar dados

## 🧪 Testes

### Coleção Postman

Use a coleção Postman incluída (`postman_collection.json`) para testar todos os endpoints.

### Exemplos de Teste

```bash
# Teste de autenticação
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "senha": "test123"}'

# Teste de execução
curl -X POST http://localhost:8000/v1/execucoes \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "categoria_id": 1,
    "palavras_chave": ["marketing digital", "seo"]
  }'
```

## 🔍 Monitoramento

### Logs de Segurança

Todos os endpoints geram logs de segurança estruturados:

```json
{
  "timestamp": "2025-01-27T10:30:00Z",
  "event_type": "LOGIN_SUCCESS",
  "user_id": "123",
  "username": "usuario",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "details": {
    "endpoint": "/auth/login",
    "provider": "local"
  }
}
```

### Métricas de Performance

- Tempo de resposta médio
- Taxa de erro
- Throughput
- Uptime

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro 401 - Não autorizado**
   - Verificar se o token JWT é válido
   - Verificar se o token não expirou

2. **Erro 429 - Rate limit excedido**
   - Aguardar o tempo especificado em `Retry-After`
   - Verificar limites do seu plano

3. **Erro 422 - Validação falhou**
   - Verificar formato dos dados enviados
   - Consultar detalhes no campo `validation_errors`

### Suporte

- **Email**: support@omnikeywordsfinder.com
- **Documentação**: https://docs.omnikeywordsfinder.com
- **Status**: https://status.omnikeywordsfinder.com

## 📈 Changelog

### v2.0.0 (2025-01-27)
- ✅ Sistema de tratamento de erros padronizado
- ✅ Documentação OpenAPI completa
- ✅ Schemas Pydantic para todos os endpoints
- ✅ Middleware de segurança aprimorado
- ✅ Logs estruturados e auditoria
- ✅ Rate limiting inteligente
- ✅ Validação robusta de entrada

### v1.0.0 (2024-12-01)
- 🎉 Lançamento inicial da API
- 🔐 Autenticação JWT
- 📊 Endpoints de execução
- 💳 Sistema de pagamentos básico

---

**Última Atualização**: 2025-01-27
**Versão da API**: 2.0.0
**Status**: ✅ Ativa 