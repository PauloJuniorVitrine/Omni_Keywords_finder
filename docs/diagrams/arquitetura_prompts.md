# 🏗️ **DIAGRAMA DE ARQUITETURA DE PROMPTS**

> **Prompt**: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 1.1  
> **Data**: 2025-01-27  
> **Versão**: 1.0.0  

---

## 📊 **ARQUITETURA GERAL**

```mermaid
graph TB
    subgraph "Frontend"
        A[Dashboard] --> B[Interface de Prompts]
        B --> C[Editor de Templates]
        B --> D[Gerenciador de Credenciais]
    end
    
    subgraph "Backend - Camada de Serviços"
        E[PromptUnifiedService] --> F[ValidadorSemanticoAvancado]
        E --> G[KeywordEnricher]
        E --> H[Cache Layer]
    end
    
    subgraph "Backend - Camada de Dados"
        I[Template Storage] --> J[Prompt Cache]
        I --> K[Enrichment Cache]
        I --> L[Validation Cache]
    end
    
    subgraph "Backend - Camada de Processamento"
        M[Prompt Processor] --> N[Placeholder Filler]
        M --> O[Context Injector]
        M --> P[Quality Validator]
    end
    
    subgraph "External APIs"
        Q[OpenAI API] --> R[Embeddings]
        S[Google Search Console] --> T[Keyword Data]
        U[Analytics APIs] --> V[Trend Data]
    end
    
    A --> E
    E --> I
    E --> M
    M --> Q
    M --> S
    M --> U
```

---

## 🔄 **FLUXO DE PROCESSAMENTO DE PROMPTS**

```mermaid
sequenceDiagram
    participant U as Usuário
    participant D as Dashboard
    participant PUS as PromptUnifiedService
    participant VSA as ValidadorSemanticoAvancado
    participant KE as KeywordEnricher
    participant PP as PromptProcessor
    participant C as Cache
    participant API as External APIs
    
    U->>D: Criar/Editar Template
    D->>PUS: Salvar Template TXT
    PUS->>VSA: Validar Template
    VSA->>PUS: Resultado Validação
    PUS->>C: Armazenar Template
    
    U->>D: Gerar Prompt
    D->>PUS: Solicitar Prompt
    PUS->>C: Verificar Cache
    alt Cache Hit
        C->>PUS: Retornar Prompt Cacheado
    else Cache Miss
        PUS->>KE: Enriquecer Keywords
        KE->>API: Buscar Dados Externos
        API->>KE: Dados Enriquecidos
        KE->>PUS: Resultado Enriquecimento
        PUS->>PP: Processar Prompt
        PP->>PUS: Prompt Final
        PUS->>C: Armazenar no Cache
    end
    PUS->>D: Retornar Prompt
    D->>U: Exibir Prompt
```

---

## 🗂️ **ESTRUTURA DE ARQUIVOS TXT**

```mermaid
graph LR
    subgraph "Templates Directory"
        A[templates/] --> B[marketing/]
        A --> C[seo/]
        A --> D[ads/]
        A --> E[content/]
    end
    
    B --> F[artigo_marketing.txt]
    B --> G[landing_page.txt]
    C --> H[otimizacao_seo.txt]
    C --> I[analise_keywords.txt]
    D --> J[campanha_ads.txt]
    D --> K[anuncio_google.txt]
    E --> L[blog_post.txt]
    E --> M[email_sequence.txt]
    
    subgraph "Template Structure"
        N[# Template: nome] --> O[# Version: 1.0.0]
        O --> P[# Category: categoria]
        P --> Q[# Created: timestamp]
        Q --> R[# Updated: timestamp]
        R --> S[# Metadata: key-value]
        S --> T[Conteúdo do Template]
        T --> U[{placeholders}]
    end
```

---

## 🧠 **ARQUITETURA DE VALIDAÇÃO SEMÂNTICA**

```mermaid
graph TB
    subgraph "ValidadorSemanticoAvancado"
        A[Input: Prompt + Context] --> B[Cache Check]
        B --> C{Cache Hit?}
        
        C -->|Yes| D[Return Cached Result]
        C -->|No| E[Basic Validation]
        
        E --> F[Semantic Validation]
        F --> G[Contextual Validation]
        G --> H[Coherence Validation]
        
        H --> I[Generate Suggestions]
        I --> J[Calculate Score]
        J --> K[Store in Cache]
        K --> L[Return Result]
    end
    
    subgraph "Validation Types"
        M[Basic Validation] --> N[Length Check]
        M --> O[Keyword Density]
        M --> P[Placeholder Check]
        
        Q[Semantic Validation] --> R[Embedding Similarity]
        Q --> S[Context Alignment]
        
        T[Contextual Validation] --> U[Primary Keyword]
        T --> V[Secondary Keywords]
        T --> W[Funnel Stage]
        
        X[Coherence Validation] --> Y[Repetition Check]
        X --> Z[Structure Check]
    end
```

---

## 🔍 **ARQUITETURA DE ENRIQUECIMENTO**

```mermaid
graph TB
    subgraph "KeywordEnricher"
        A[Input: Keyword + Context] --> B[Cache Check]
        B --> C{Cache Hit?}
        
        C -->|Yes| D[Return Cached Result]
        C -->|No| E[Semantic Enrichment]
        
        E --> F[Contextual Enrichment]
        F --> G[Trend Analysis]
        G --> H[Competition Analysis]
        H --> I[Intent Detection]
        
        I --> J[Calculate Total Score]
        J --> K[Store in Cache]
        K --> L[Return Result]
    end
    
    subgraph "Enrichment Types"
        M[Semantic] --> N[Word Analysis]
        M --> O[Brand Detection]
        M --> P[Location Detection]
        M --> Q[Product Detection]
        
        R[Contextual] --> S[Domain Relevance]
        R --> T[Seasonal Relevance]
        R --> U[Trend Alignment]
        R --> V[Audience Match]
        
        W[Trend] --> X[Direction]
        W --> Y[Strength]
        W --> Z[Seasonality]
        W --> AA[Growth Potential]
        
        BB[Competition] --> CC[Level]
        BB --> DD[Difficulty]
        BB --> EE[Opportunity]
        BB --> FF[Saturation]
        
        GG[Intent] --> HH[Commercial]
        GG --> II[Informational]
        GG --> JJ[Navigational]
    end
```

---

## 💾 **ARQUITETURA DE CACHE**

```mermaid
graph TB
    subgraph "Cache Layers"
        A[Prompt Cache] --> B[Template Cache]
        A --> C[Enrichment Cache]
        A --> D[Validation Cache]
    end
    
    subgraph "Cache Structure"
        E[Cache Entry] --> F[Content]
        E --> G[Hash]
        E --> H[Created At]
        E --> I[TTL]
        E --> J[Access Count]
    end
    
    subgraph "Cache Operations"
        K[Get] --> L{Exists?}
        L -->|Yes| M{Expired?}
        L -->|No| N[Return None]
        M -->|No| O[Return + Increment Count]
        M -->|Yes| P[Remove + Return None]
        
        Q[Set] --> R{Max Size?}
        R -->|Yes| S[Remove Oldest]
        R -->|No| T[Add Entry]
        S --> T
    end
```

---

## 🔐 **ARQUITETURA DE SEGURANÇA**

```mermaid
graph TB
    subgraph "Security Layers"
        A[User Input] --> B[Input Validation]
        B --> C[Template Sanitization]
        C --> D[Encryption Layer]
        D --> E[Secure Storage]
    end
    
    subgraph "Credential Management"
        F[Dashboard] --> G[Credential Input]
        G --> H[AES-256 Encryption]
        H --> I[Secure Database]
        I --> J[Audit Logs]
    end
    
    subgraph "Access Control"
        K[User Authentication] --> L[Role-Based Access]
        L --> M[Template Permissions]
        M --> N[API Rate Limiting]
    end
```

---

## 📈 **MÉTRICAS E MONITORAMENTO**

```mermaid
graph TB
    subgraph "Metrics Collection"
        A[Performance Metrics] --> B[Processing Time]
        A --> C[Cache Hit Rate]
        A --> D[Error Rate]
        A --> E[Throughput]
    end
    
    subgraph "Quality Metrics"
        F[Validation Metrics] --> G[Accuracy Score]
        F --> H[False Positive Rate]
        F --> I[Coverage Rate]
    end
    
    subgraph "Business Metrics"
        J[Business Metrics] --> K[Template Usage]
        J --> L[Keyword Processing]
        J --> M[User Satisfaction]
    end
    
    subgraph "Monitoring"
        N[Real-time Monitoring] --> O[Alerting]
        N --> P[Dashboards]
        N --> Q[Logs]
    end
```

---

## 🚀 **DEPLOYMENT ARCHITECTURE**

```mermaid
graph TB
    subgraph "Development"
        A[Local Development] --> B[Unit Tests]
        B --> C[Integration Tests]
        C --> D[Code Review]
    end
    
    subgraph "Staging"
        E[Staging Environment] --> F[Load Testing]
        F --> G[Performance Testing]
        G --> H[Security Testing]
    end
    
    subgraph "Production"
        I[Production Deployment] --> J[Blue-Green Deployment]
        J --> K[Health Checks]
        K --> L[Monitoring]
        L --> M[Rollback if needed]
    end
    
    subgraph "Infrastructure"
        N[Redis Cache] --> O[High Availability]
        P[Database] --> Q[Backup & Recovery]
        R[Load Balancer] --> S[Auto Scaling]
    end
```

---

## 📋 **CHECKLIST DE IMPLEMENTAÇÃO**

### ✅ **Fase 1.1 - Estabilidade Crítica**
- [x] **ValidadorSemanticoAvancado** - Implementado
- [x] **PromptUnifiedService** - Implementado  
- [x] **KeywordEnricher** - Implementado
- [x] **Testes Unitários** - Criados (⚠️ não executados)
- [x] **Diagramas de Arquitetura** - Criados

### 🔄 **Próximas Fases**
- [ ] **Fase 2** - Performance Alta (Semana 3-4)
- [ ] **Fase 3** - Observabilidade (Semana 5-6)
- [ ] **Fase 4** - Resiliência (Semana 7-8)
- [ ] **Fase 5** - Otimizações (Semana 9-10)
- [ ] **Fase 6** - Sistema de Lacunas Preciso (Semana 9-18)

---

> **Status**: ✅ **FASE 1.1 CONCLUÍDA**  
> **Próximo**: Implementar Fase 2 (Performance Alta)  
> **Responsável**: Equipe de Desenvolvimento 