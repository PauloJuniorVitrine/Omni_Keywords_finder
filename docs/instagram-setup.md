# 📸 **INSTAGRAM API SETUP GUIDE**

**Tracing ID**: `instagram-setup-2025-01-27-001`  
**Timestamp**: 2025-01-27T10:30:00Z  
**Versão**: 1.0  
**Status**: 🚀 **EM IMPLEMENTAÇÃO**

---

## 📋 **RESUMO EXECUTIVO**

### **Objetivo**
Configurar integração real com Instagram API para coleta de dados de posts, hashtags e métricas de engajamento.

### **APIs Disponíveis**
- **Instagram Basic Display API**: Para dados públicos de posts
- **Instagram Graph API**: Para dados de negócio e métricas avançadas
- **Web Scraping Fallback**: Para casos onde APIs não estão disponíveis

### **Impacto Esperado**
- **15% melhoria** no score geral
- **Cobertura real** de dados do Instagram
- **Métricas de engajamento** precisas
- **Análise de tendências** baseada em dados reais

---

## 🔧 **REQUISITOS E LIMITAÇÕES**

### **📐 CoCoT: Fundamentos Técnicos**
- **Comprovação**: Baseado em documentação oficial da Meta/Facebook
- **Causalidade**: Limitações impostas por políticas de privacidade e rate limiting
- **Contexto**: Necessidade de compliance com GDPR e LGPD
- **Tendência**: Evolução para APIs mais restritivas por questões de privacidade

### **🌲 ToT: Análise de Alternativas**
1. **Instagram Basic Display API**
   - ✅ Dados públicos de posts
   - ✅ Autenticação OAuth 2.0
   - ❌ Limitações de rate limiting
   - ❌ Acesso apenas a dados autorizados

2. **Instagram Graph API**
   - ✅ Métricas de negócio
   - ✅ Dados de engajamento
   - ❌ Requer conta de negócio
   - ❌ Processo de aprovação complexo

3. **Web Scraping Fallback**
   - ✅ Dados públicos disponíveis
   - ✅ Sem limitações de API
   - ❌ Risco de detecção de bot
   - ❌ Mudanças frequentes na estrutura

### **♻️ ReAct: Simulação de Impacto**
- **Rate Limiting**: 200 requests/hour para Basic Display API
- **Processo de Aprovação**: 2-4 semanas para Graph API
- **Compliance**: Necessário implementar consentimento explícito
- **Fallback**: Web scraping deve ser implementado como backup

---

## 📝 **CHECKLIST DE SETUP**

### **Fase 1: Preparação da Conta**

- [ ] **1.1 Criar Conta de Desenvolvedor**
  - [ ] Acessar [developers.facebook.com](https://developers.facebook.com)
  - [ ] Criar conta de desenvolvedor
  - [ ] Verificar email e telefone
  - [ ] **Arquivo**: `docs/instagram-setup.md`

- [ ] **1.2 Configurar Aplicação**
  - [ ] Criar nova aplicação
  - [ ] Selecionar tipo "Consumer" ou "Business"
  - [ ] Configurar domínios permitidos
  - [ ] **Arquivo**: `docs/instagram-setup.md`

- [ ] **1.3 Obter Credenciais**
  - [ ] Copiar App ID
  - [ ] Copiar App Secret
  - [ ] Configurar redirect URIs
  - [ ] **Arquivo**: `docs/instagram-setup.md`

### **Fase 2: Configuração de APIs**

- [ ] **2.1 Instagram Basic Display API**
  - [ ] Adicionar produto Basic Display
  - [ ] Configurar OAuth 2.0
  - [ ] Definir permissões necessárias
  - [ ] **Arquivo**: `infrastructure/coleta/instagram_basic_api.py`

- [ ] **2.2 Instagram Graph API**
  - [ ] Adicionar produto Graph API
  - [ ] Configurar permissões de negócio
  - [ ] Solicitar aprovação de permissões
  - [ ] **Arquivo**: `infrastructure/coleta/instagram_graph_api.py`

- [ ] **2.3 Web Scraping Fallback**
  - [ ] Implementar scraper ético
  - [ ] Configurar rate limiting
  - [ ] Adicionar detecção de captcha
  - [ ] **Arquivo**: `infrastructure/coleta/instagram_scraper.py`

### **Fase 3: Implementação**

- [ ] **3.1 Autenticação OAuth 2.0**
  - [ ] Implementar fluxo de autorização
  - [ ] Gerenciar tokens de acesso
  - [ ] Implementar refresh tokens
  - [ ] **Arquivo**: `infrastructure/coleta/instagram_oauth.py`

- [ ] **3.2 Coleta de Dados**
  - [ ] Implementar coleta de posts
  - [ ] Implementar coleta de hashtags
  - [ ] Implementar métricas de engajamento
  - [ ] **Arquivo**: `infrastructure/coleta/instagram_collector.py`

- [ ] **3.3 Rate Limiting**
  - [ ] Implementar controle de rate limit
  - [ ] Configurar retry com backoff
  - [ ] Implementar cache de respostas
  - [ ] **Arquivo**: `infrastructure/coleta/instagram_rate_limiter.py`

### **Fase 4: Testes e Validação**

- [ ] **4.1 Testes de Integração**
  - [ ] Testar autenticação
  - [ ] Testar coleta de dados
  - [ ] Testar rate limiting
  - [ ] **Arquivo**: `tests/integration/test_instagram_api.py`

- [ ] **4.2 Testes de Fallback**
  - [ ] Testar web scraping
  - [ ] Testar detecção de captcha
  - [ ] Testar recuperação de falhas
  - [ ] **Arquivo**: `tests/integration/test_instagram_fallback.py`

---

## 🔐 **CONFIGURAÇÃO DE SEGURANÇA**

### **OAuth 2.0 Configuration**
```yaml
instagram_oauth:
  client_id: "${INSTAGRAM_CLIENT_ID}"
  client_secret: "${INSTAGRAM_CLIENT_SECRET}"
  redirect_uri: "https://api.omni-keywords.com/auth/instagram/callback"
  scope: "user_profile,user_media"
  state_parameter: true
  pkce_enabled: true
```

### **Rate Limiting Configuration**
```yaml
instagram_rate_limits:
  basic_display_api:
    requests_per_hour: 200
    requests_per_day: 5000
  graph_api:
    requests_per_hour: 100
    requests_per_day: 2000
  web_scraping:
    requests_per_minute: 10
    requests_per_hour: 100
```

### **Fallback Configuration**
```yaml
instagram_fallback:
  enabled: true
  web_scraping:
    enabled: true
    user_agent: "OmniKeywordsBot/1.0"
    delay_between_requests: 2.0
    max_retries: 3
  cache:
    enabled: true
    ttl_hours: 24
```

---

## 📊 **MÉTRICAS E MONITORAMENTO**

### **Métricas a Coletar**
- **Posts por hashtag**
- **Engajamento (likes, comentários)**
- **Reach e impressions**
- **Crescimento de seguidores**
- **Melhor horário de postagem**

### **Alertas Configurados**
- **Rate limit excedido**
- **Token expirado**
- **Falha de autenticação**
- **Web scraping bloqueado**
- **Captcha detectado**

---

## 🚨 **RISCOS E MITIGAÇÕES**

### **Riscos Identificados**
1. **Rate Limiting**: Implementar cache e fallback
2. **Mudanças na API**: Versionamento e abstrações
3. **Detecção de Bot**: Rotação de user agents e delays
4. **Compliance**: Implementar consentimento explícito

### **Estratégias de Mitigação**
1. **Cache Inteligente**: Reduzir chamadas desnecessárias
2. **Fallback Robusto**: Web scraping como backup
3. **Monitoramento**: Alertas em tempo real
4. **Compliance**: Auditoria regular de dados

---

## 📈 **ROADMAP DE IMPLEMENTAÇÃO**

### **Semana 1**
- Setup da conta de desenvolvedor
- Configuração das APIs
- Implementação da autenticação OAuth 2.0

### **Semana 2**
- Implementação da coleta de dados
- Configuração de rate limiting
- Implementação do fallback

### **Semana 3**
- Testes de integração
- Validação de compliance
- Documentação final

---

## 🔗 **LINKS ÚTEIS**

- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [OAuth 2.0 Guide](https://developers.facebook.com/docs/instagram-basic-display-api/getting-started)
- [Rate Limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting)

---

**Documento criado em**: 2025-01-27T10:30:00Z  
**Próxima atualização**: Após conclusão de cada fase  
**Responsável**: Equipe de Backend  
**Versão**: 1.0 