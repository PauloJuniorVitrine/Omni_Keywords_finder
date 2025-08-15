# 🔗 **MercadoPago Gateway Setup**

**Tracing ID**: `mercadopago-setup-2025-01-27-001`  
**Timestamp**: 2025-01-27T14:30:00Z  
**Versão**: 1.0  
**Status**: 📋 **DOCUMENTAÇÃO**

---

## 📋 **RESUMO EXECUTIVO**

### **Objetivo**
Implementar integração completa com MercadoPago Gateway para processamento de pagamentos no sistema Omni Keywords Finder.

### **Métricas Alvo**
- **Taxa de Aprovação**: > 95%
- **Tempo de Processamento**: < 3s
- **Disponibilidade**: 99.9%
- **Cobertura de Testes**: 90%

---

## 🚀 **SETUP INICIAL**

### **1.1 Criar Conta MercadoPago Developer**

#### **Passos**
1. Acessar [MercadoPago Developers](https://www.mercadopago.com.br/developers)
2. Criar conta de desenvolvedor
3. Configurar perfil de negócio
4. Verificar documentação

#### **Requisitos**
- CNPJ válido
- Documentação empresarial
- Conta bancária para recebimentos
- Compliance com regulamentações

### **1.2 Configurar Aplicação**

#### **Credenciais Necessárias**
```bash
# Sandbox (Desenvolvimento)
MERCADOPAGO_ACCESS_TOKEN_SANDBOX=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY_SANDBOX=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Produção
MERCADOPAGO_ACCESS_TOKEN_PROD=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY_PROD=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### **Configurações de Ambiente**
```yaml
# config/mercadopago.yaml
environment: sandbox  # ou production
webhook_url: https://api.omni-keywords.com/webhooks/mercadopago
notification_url: https://api.omni-keywords.com/notifications/mercadopago
auto_return: true
back_urls:
  success: https://omni-keywords.com/payment/success
  failure: https://omni-keywords.com/payment/failure
  pending: https://omni-keywords.com/payment/pending
```

---

## 🔧 **INTEGRAÇÃO TÉCNICA**

### **2.1 SDK MercadoPago Python**

#### **Instalação**
```bash
pip install mercadopago
```

#### **Configuração Básica**
```python
import mercadopago

# Configuração
sdk = mercadopago.SDK("YOUR_ACCESS_TOKEN")

# Ambiente
sdk.set_environment("sandbox")  # ou "production"
```

### **2.2 Endpoints Principais**

#### **Criar Pagamento**
```python
# POST /v1/payments
payment_data = {
    "transaction_amount": 100.00,
    "token": "card_token",
    "description": "Omni Keywords Finder - Premium Plan",
    "installments": 1,
    "payment_method_id": "visa",
    "payer": {
        "email": "user@example.com"
    }
}
```

#### **Webhooks**
```python
# POST /webhooks/mercadopago
webhook_data = {
    "type": "payment",
    "data": {
        "id": "payment_id"
    }
}
```

---

## 🔒 **SEGURANÇA E COMPLIANCE**

### **3.1 Validação HMAC**

#### **Implementação**
```python
import hmac
import hashlib

def validate_webhook_signature(payload, signature, secret):
    """
    Valida assinatura HMAC do webhook MercadoPago
    """
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### **3.2 IP Whitelist**

#### **IPs MercadoPago**
```python
MERCADOPAGO_IPS = [
    "34.195.33.240",
    "34.195.33.241",
    "34.195.33.242",
    "34.195.33.243",
    "34.195.33.244"
]

def validate_mercadopago_ip(client_ip):
    """
    Valida se IP é do MercadoPago
    """
    return client_ip in MERCADOPAGO_IPS
```

### **3.3 Criptografia de Dados**

#### **Tokenização de Cartões**
```python
def tokenize_card(card_data):
    """
    Tokeniza dados do cartão via MercadoPago
    """
    card_token_data = {
        "card_number": card_data["number"],
        "security_code": card_data["cvv"],
        "expiration_month": card_data["exp_month"],
        "expiration_year": card_data["exp_year"],
        "cardholder": {
            "name": card_data["holder_name"],
            "identification": {
                "type": "CPF",
                "number": card_data["cpf"]
            }
        }
    }
    
    return sdk.card_token().create(card_token_data)
```

---

## 🧪 **TESTES E VALIDAÇÃO**

### **4.1 Testes de Sandbox**

#### **Cartões de Teste**
```python
TEST_CARDS = {
    "approved": {
        "number": "4509 9535 6623 3704",
        "cvv": "123",
        "exp_month": "11",
        "exp_year": "2025"
    },
    "rejected": {
        "number": "4000 0000 0000 0002",
        "cvv": "123",
        "exp_month": "11",
        "exp_year": "2025"
    },
    "pending": {
        "number": "4000 0000 0000 0127",
        "cvv": "123",
        "exp_month": "11",
        "exp_year": "2025"
    }
}
```

### **4.2 Cenários de Teste**

#### **Fluxos Principais**
1. **Pagamento Aprovado**
   - Criar pagamento
   - Validar webhook
   - Confirmar status

2. **Pagamento Rejeitado**
   - Simular rejeição
   - Validar fallback
   - Testar retry

3. **Pagamento Pendente**
   - Simular pendência
   - Validar notificação
   - Testar timeout

---

## 📊 **MONITORAMENTO E MÉTRICAS**

### **5.1 Métricas Essenciais**

#### **KPIs de Negócio**
- Taxa de conversão
- Valor médio do ticket
- Tempo de processamento
- Taxa de chargeback

#### **KPIs Técnicos**
- Disponibilidade da API
- Tempo de resposta
- Taxa de erro
- Uso de recursos

### **5.2 Alertas**

#### **Alertas Críticos**
```yaml
alerts:
  - name: "mercadopago_api_down"
    condition: "up{job='mercadopago'} == 0"
    severity: "critical"
    
  - name: "mercadopago_high_error_rate"
    condition: "rate(mercadopago_errors_total[5m]) > 0.05"
    severity: "warning"
    
  - name: "mercadopago_high_latency"
    condition: "histogram_quantile(0.95, rate(mercadopago_request_duration_seconds_bucket[5m])) > 3"
    severity: "warning"
```

---

## 🔄 **FLUXO DE IMPLEMENTAÇÃO**

### **Fase 1: Setup Básico (1-2 dias)**
- [x] Criar conta developer
- [x] Configurar credenciais
- [x] Implementar SDK básico
- [x] Testes de sandbox

### **Fase 2: Integração Completa (3-5 dias)**
- [ ] Implementar gateway
- [ ] Configurar webhooks
- [ ] Implementar validações
- [ ] Testes de integração

### **Fase 3: Produção (1-2 dias)**
- [ ] Configurar produção
- [ ] Validar compliance
- [ ] Monitoramento
- [ ] Go-live

---

## 📝 **CHECKLIST DE IMPLEMENTAÇÃO**

### **Setup**
- [ ] Conta developer criada
- [ ] Credenciais configuradas
- [ ] Ambiente sandbox testado
- [ ] Documentação revisada

### **Desenvolvimento**
- [ ] SDK integrado
- [ ] Gateway implementado
- [ ] Webhooks configurados
- [ ] Validações implementadas

### **Testes**
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes de carga
- [ ] Testes de segurança

### **Produção**
- [ ] Ambiente configurado
- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Rollback plan

---

## 🚨 **RISCOS E MITIGAÇÕES**

### **Riscos Identificados**
1. **Rate Limiting**: MercadoPago tem limites de requisições
2. **Mudanças na API**: Versões podem ser descontinuadas
3. **Compliance**: Regulamentações podem mudar
4. **Disponibilidade**: API pode ter downtime

### **Mitigações**
1. **Cache inteligente** para reduzir requisições
2. **Versioning** da API para compatibilidade
3. **Monitoramento contínuo** de compliance
4. **Fallback** para outros gateways

---

## 📚 **REFERÊNCIAS**

### **Documentação Oficial**
- [MercadoPago Developers](https://www.mercadopago.com.br/developers)
- [API Reference](https://www.mercadopago.com.br/developers/docs)
- [SDK Python](https://github.com/mercadopago/sdk-python)

### **Boas Práticas**
- [PCI DSS Compliance](https://www.pcisecuritystandards.org/)
- [OWASP Payment Security](https://owasp.org/www-project-payment-security-standards/)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)

---

**Documento criado em**: 2025-01-27T14:30:00Z  
**Próxima revisão**: Após implementação  
**Responsável**: Backend Team  
**Versão**: 1.0 