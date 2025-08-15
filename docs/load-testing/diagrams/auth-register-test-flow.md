# 📝 DIAGRAMA DE FLUXO - TESTE DE CARGA AUTH REGISTER

## 📊 Visão Geral

Este documento descreve o fluxo de teste de carga para o endpoint `/api/auth/register`, incluindo cenários, métricas e representações visuais.

---

## 🎯 Objetivo do Teste

Validar a performance, segurança e confiabilidade do endpoint de registro de usuários sob carga, garantindo que as validações funcionem corretamente e que o sistema seja resistente a ataques.

---

## 🔄 Fluxo Principal do Teste

```mermaid
graph TD
    A[Início do Teste] --> B[Validação do Ambiente]
    B --> C{Ambiente OK?}
    C -->|Não| D[Falha - Ambiente Inválido]
    C -->|Sim| E[Preparação do Ambiente]
    E --> F[Limpeza de Dados de Teste]
    F --> G[Execução dos Cenários]
    G --> H[Análise de Resultados]
    H --> I[Geração de Relatórios]
    I --> J[Fim do Teste]
    
    style A fill:#e1f5fe
    style J fill:#e8f5e8
    style D fill:#ffebee
```

---

## 🧪 Cenários de Teste

### 1. Registro Válido (50% das requisições)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Locust
    participant S as Servidor
    participant V as Validador
    participant D as Database
    
    U->>L: Inicia teste
    L->>L: Gera dados válidos
    L->>S: POST /api/auth/register
    Note over L,S: {username, email, senha, confirmar_senha}
    S->>V: Valida dados
    V-->>S: Dados válidos
    S->>D: Verifica duplicação
    D-->>S: Sem duplicação
    S->>D: Cria usuário
    D-->>S: Usuário criado
    S-->>L: 201 Created + user_id
    L->>L: Valida resposta
    L-->>U: Sucesso
```

### 2. Dados Duplicados (15% das requisições)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Locust
    participant S as Servidor
    participant V as Validador
    participant D as Database
    
    U->>L: Inicia teste
    L->>L: Gera dados duplicados
    L->>S: POST /api/auth/register
    Note over L,S: {username, email} já existentes
    S->>V: Valida dados
    V-->>S: Dados válidos
    S->>D: Verifica duplicação
    D-->>S: Dados duplicados
    S-->>L: 409 Conflict
    L->>L: Valida erro esperado
    L-->>U: Sucesso (erro esperado)
```

### 3. Username Inválido (15% das requisições)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Locust
    participant S as Servidor
    participant V as Validador
    
    U->>L: Inicia teste
    L->>L: Gera username inválido
    L->>S: POST /api/auth/register
    Note over L,S: {username: "ab", email, senha}
    S->>V: Valida dados
    V-->>S: Username inválido
    S-->>L: 400/422 Bad Request
    L->>L: Valida erro esperado
    L-->>U: Sucesso (erro esperado)
```

### 4. Email Inválido (10% das requisições)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Locust
    participant S as Servidor
    participant V as Validador
    
    U->>L: Inicia teste
    L->>L: Gera email inválido
    L->>S: POST /api/auth/register
    Note over L,S: {username, email: "invalid", senha}
    S->>V: Valida dados
    V-->>S: Email inválido
    S-->>L: 400/422 Bad Request
    L->>L: Valida erro esperado
    L-->>U: Sucesso (erro esperado)
```

### 5. Senha Inválida (5% das requisições)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Locust
    participant S as Servidor
    participant V as Validador
    
    U->>L: Inicia teste
    L->>L: Gera senha inválida
    L->>S: POST /api/auth/register
    Note over L,S: {username, email, senha: "weak"}
    S->>V: Valida dados
    V-->>S: Senha inválida
    S-->>L: 400/422 Bad Request
    L->>L: Valida erro esperado
    L-->>U: Sucesso (erro esperado)
```

### 6. Senhas Não Coincidem (3% das requisições)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Locust
    participant S as Servidor
    participant V as Validador
    
    U->>L: Inicia teste
    L->>L: Gera senhas diferentes
    L->>S: POST /api/auth/register
    Note over L,S: {senha: "pass123", confirmar_senha: "pass456"}
    S->>V: Valida dados
    V-->>S: Senhas não coincidem
    S-->>L: 400/422 Bad Request
    L->>L: Valida erro esperado
    L-->>U: Sucesso (erro esperado)
```

### 7. Payload Malformado (2% das requisições)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant L as Locust
    participant S as Servidor
    
    U->>L: Inicia teste
    L->>L: Gera payload malformado
    L->>S: POST /api/auth/register
    Note over L,S: Payload inválido
    S->>S: Valida payload
    S-->>L: 400/422 Bad Request
    L->>L: Valida erro esperado
    L-->>U: Sucesso (erro esperado)
```

---

## 📊 Métricas Coletadas

### Métricas de Performance
```mermaid
graph LR
    A[Métricas] --> B[Tempo de Resposta]
    A --> C[Throughput]
    A --> D[Taxa de Falha]
    A --> E[Concorrência]
    
    B --> B1[Médio]
    B --> B2[Máximo]
    B --> B3[Mínimo]
    
    C --> C1[Req/s]
    C --> C2[Usuários/s]
    
    D --> D1[% Falhas]
    D --> D2[Tipos de Erro]
    
    E --> E1[Usuários Ativos]
    E --> E2[Taxa de Spawn]
```

### Métricas de Validação
```mermaid
graph TD
    A[Métricas de Validação] --> B[Registros Válidos]
    A --> C[Erros de Validação]
    A --> D[Dados Duplicados]
    A --> E[Rate Limiting]
    A --> F[Segurança]
    
    B --> B1[Sucessos]
    B --> B2[Tempo de Processamento]
    
    C --> C1[Username Inválido]
    C --> C2[Email Inválido]
    C --> C3[Senha Inválida]
    C --> C4[Senhas Não Coincidem]
    
    D --> D1[Conflitos Detectados]
    D --> D2[Tempo de Verificação]
    
    E --> E1[Limites Atingidos]
    E --> E2[Comportamento]
    
    F --> F1[Ataques Bloqueados]
    F --> F2[Vulnerabilidades]
```

---

## 🎯 Critérios de Sucesso

### Performance
- **Tempo de Resposta**: < 3000ms (médio)
- **Throughput**: > 20 req/s
- **Taxa de Falha**: < 10%

### Segurança
- **Dados Inválidos**: 100% rejeitados
- **Dados Duplicados**: 100% detectados
- **Rate Limiting**: Funcionando corretamente
- **Validação de Senha**: Regras aplicadas

### Confiabilidade
- **Disponibilidade**: > 99%
- **Consistência**: Respostas consistentes
- **Integridade**: Dados salvos corretamente

---

## 📈 Análise de Riscos

### Riscos Identificados
```mermaid
graph TD
    A[Riscos] --> B[Performance]
    A --> C[Segurança]
    A --> D[Confiabilidade]
    
    B --> B1[Timeout]
    B --> B2[Memory Leak]
    B --> B3[Database Overload]
    
    C --> C1[Enumeration Attack]
    C --> C2[Data Validation Bypass]
    C --> C3[SQL Injection]
    C --> C4[XSS Attack]
    
    D --> D1[Data Corruption]
    D --> D2[Duplicate Users]
    D --> D3[Inconsistent State]
```

### Mitigações
- **Validação Robusta**: Múltiplas camadas de validação
- **Rate Limiting**: Proteção contra spam
- **Logs Detalhados**: Auditoria completa
- **Sanitização**: Limpeza de dados de entrada
- **Transações**: Atomicidade das operações

---

## 🔧 Configuração do Teste

### Parâmetros
```yaml
test_config:
  base_url: "http://localhost:8000"
  endpoint: "/api/auth/register"
  users: 30
  spawn_rate: 5
  run_time: "5m"
  scenarios:
    valid_registration: 50%
    duplicate_data: 15%
    invalid_username: 15%
    invalid_email: 10%
    invalid_password: 5%
    password_mismatch: 3%
    malformed_payload: 2%
```

### Ambiente
```yaml
environment:
  server: "FastAPI/Flask"
  database: "PostgreSQL"
  validation: "Pydantic"
  security: "OWASP Guidelines"
  rate_limiting: "Redis-based"
```

---

## 📋 Checklist de Execução

### Pré-Teste
- [ ] Servidor rodando
- [ ] Database conectado
- [ ] Validações configuradas
- [ ] Rate limiting ativo
- [ ] Logs configurados
- [ ] Monitoramento ativo
- [ ] Backup dos dados

### Durante o Teste
- [ ] Métricas coletadas
- [ ] Logs monitorados
- [ ] Performance observada
- [ ] Erros registrados
- [ ] Alertas configurados
- [ ] Dados de teste isolados

### Pós-Teste
- [ ] Relatórios gerados
- [ ] Análise realizada
- [ ] Recomendações criadas
- [ ] Documentação atualizada
- [ ] Limpeza de dados
- [ ] Próximos passos definidos

---

## 🎨 Representações Visuais

### Dashboard de Métricas
```
┌─────────────────────────────────────────────────────────────┐
│                    AUTH REGISTER LOAD TEST                  │
├─────────────────────────────────────────────────────────────┤
│  📊 Performance Metrics                                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Avg Response│ Max Response│ Min Response│ Throughput  │  │
│  │   2,100ms   │   5,200ms   │    200ms    │   15 req/s  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
│                                                             │
│  📈 Success Rate: 92.5%                                     │
│  ⚠️  Failure Rate: 7.5%                                     │
│                                                             │
│  🔒 Validation Metrics                                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Valid Reg   │ Invalid Usr │ Invalid Pwd │ Duplicates  │  │
│  │    750      │     120     │      80     │     45      │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Validação
```
┌─────────────────┐
│   Register Data │
└─────────┬───────┘
          │
    ┌─────▼─────┐
    │  Validate │
    │  Username │
    └─────┬─────┘
          │
    ┌─────▼─────┐
    │  Validate │
    │   Email   │
    └─────┬─────┘
          │
    ┌─────▼─────┐
    │  Validate │
    │ Password  │
    └─────┬─────┘
          │
    ┌─────▼─────┐
    │  Validate │
    │  Confirm  │
    └─────┬─────┘
          │
    ┌─────▼─────┐
    │ Check DB  │
    │ Duplicate │
    └─────┬─────┘
          │
    ┌─────▼─────┐     ┌─────────────┐
    │  Success  │────▶│ Return 201  │
    └───────────┘     └─────────────┘
```

---

## 📝 Conclusões

O teste de carga para o endpoint `/api/auth/register` é essencial para garantir:

1. **Performance adequada** sob carga
2. **Segurança robusta** contra ataques
3. **Validação confiável** de dados
4. **Integridade** dos dados salvos
5. **Resistência** a ataques de enumeração

A implementação segue as melhores práticas de segurança OWASP e validação de dados, com monitoramento abrangente e análise detalhada de resultados. 