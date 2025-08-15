# 🔒 Integração com Stripe - Guia de Configuração

## 📋 Visão Geral

Este guia descreve como configurar a integração real com Stripe para processamento seguro de pagamentos no Omni Keywords Finder.

## 🚀 Configuração Inicial

### 1. Instalação da Dependência

```bash
pip install stripe
```

### 2. Variáveis de Ambiente

Adicione as seguintes variáveis ao seu arquivo `.env`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...  # Chave secreta do Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Chave pública do Stripe
STRIPE_WEBHOOK_SECRET=whsec_...  # Secret do webhook
STRIPE_WEBHOOK_IPS=3.18.12.63,3.130.192.231  # IPs do Stripe (opcional)
```

### 3. Obtenção das Chaves

1. **Acesse o Dashboard do Stripe**: https://dashboard.stripe.com/
2. **Vá para Developers > API Keys**
3. **Copie as chaves de teste** (test keys) para desenvolvimento
4. **Para produção, use as chaves live**

## 🔗 Configuração de Webhooks

### 1. Criar Webhook no Stripe

1. **Dashboard > Developers > Webhooks**
2. **Add endpoint**: `https://seu-dominio.com/api/payments/webhook`
3. **Selecionar eventos**:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.dispute.created`
4. **Copiar o webhook secret**

### 2. Configurar IPs Permitidos (Opcional)

Para maior segurança, configure os IPs do Stripe:

```bash
STRIPE_WEBHOOK_IPS=3.18.12.63,3.130.192.231,13.235.14.237
```

## 🧪 Testes

### 1. Executar Testes Unitários

```bash
pytest tests/unit/test_payments_integration.py -v
```

### 2. Testar Endpoints

#### Criar Pagamento
```bash
curl -X POST http://localhost:8000/api/payments/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "amount": 1000,
    "currency": "brl",
    "metadata": {
      "user_id": "123",
      "plan": "premium"
    }
  }'
```

#### Consultar Status
```bash
curl -X GET http://localhost:8000/api/payments/status/pi_test_123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Configuração
```bash
curl -X GET http://localhost:8000/api/payments/config
```

## 🔒 Segurança

### 1. Validação de Assinatura

Todos os webhooks são validados usando HMAC SHA256:

```python
# Validação automática no código
if not payment_service.validate_webhook_signature(payload, signature):
    return jsonify({'erro': 'Assinatura inválida'}), 400
```

### 2. Validação de IP

Webhooks só são aceitos de IPs autorizados:

```python
allowed_ips = os.getenv('STRIPE_WEBHOOK_IPS', '').split(',')
if allowed_ips and remote_ip not in allowed_ips:
    return jsonify({'erro': 'IP não autorizado'}), 403
```

### 3. Logs de Segurança

Todos os eventos são logados:

```python
log_event('info', 'Payment', detalhes=f'Pagamento criado: {payment_id}')
```

## 📊 Monitoramento

### 1. Logs Importantes

- **Criação de pagamento**: `[INFO] Payment - Pagamento criado`
- **Webhook recebido**: `[INFO] Payment - Webhook processado`
- **Erros**: `[ERRO] Payment - Erro no processamento`

### 2. Métricas

- Taxa de sucesso de pagamentos
- Tempo de resposta do Stripe
- Erros de webhook
- Disputas de pagamento

## 🚨 Troubleshooting

### Problema: "Stripe não configurado"

**Solução**: Verificar se `STRIPE_SECRET_KEY` está configurada

### Problema: "Assinatura inválida"

**Solução**: Verificar se `STRIPE_WEBHOOK_SECRET` está correto

### Problema: "IP não autorizado"

**Solução**: Verificar se IP do Stripe está na lista `STRIPE_WEBHOOK_IPS`

## 🔄 Migração de Simulado para Real

### 1. Backup

```bash
# Backup da implementação atual
cp backend/app/api/payments.py backend/app/api/payments_simulated.py
```

### 2. Configuração Gradual

1. **Desenvolvimento**: Usar chaves de teste
2. **Staging**: Usar chaves de teste com dados reais
3. **Produção**: Usar chaves live

### 3. Rollback

Se necessário, volte para implementação simulada:

```bash
cp backend/app/api/payments_simulated.py backend/app/api/payments.py
```

## 📞 Suporte

- **Stripe Support**: https://support.stripe.com/
- **Documentação Stripe**: https://stripe.com/docs
- **Equipe de Segurança**: security@omni-keywords.com

---

**Última Atualização**: 2025-01-27
**Versão**: 1.0 