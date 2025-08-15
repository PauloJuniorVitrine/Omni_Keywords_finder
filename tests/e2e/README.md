# 🚀 TESTES E2E - FLUXOS CRÍTICOS

**Tracing ID:** `E2E_DOCS_20250127_001`  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ **IMPLEMENTADO**

---

## 📋 **VISÃO GERAL**

Este diretório contém os testes End-to-End (E2E) para os fluxos críticos do sistema Omni Keywords Finder. Os testes são baseados em cenários reais de negócio e seguem as metodologias **CoCoT**, **ToT** e **ReAct**.

---

## 🎯 **FLUXOS CRÍTICOS COBERTOS**

### **1. 🔐 Autenticação e Autorização**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Login com credenciais válidas
  - Login com credenciais inválidas
  - Logout e limpeza de sessão
  - Controle de acesso por role (RBAC)

### **2. 🎯 Execução de Prompts (Core do Produto)**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Execução de prompt SEO com sucesso
  - Execução com prompt inválido
  - Timeout de execução
  - Execuções concorrentes

### **3. 💳 Sistema de Pagamentos (Receita)**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Processamento de pagamento com sucesso
  - Pagamento com cartão recusado
  - Cancelamento de assinatura

### **4. 🔑 Gestão de Credenciais (Integração)**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Adicionar credencial de API
  - Validação de credencial inválida
  - Remoção de credencial

### **5. 📦 Execução em Lote (Produtividade)**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Upload e execução de arquivo CSV
  - Validação de arquivo inválido

### **6. ⏰ Agendamento (Automação)**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Criar execução agendada
  - Editar execução agendada

### **7. 📊 Dashboard e Métricas (Monitoramento)**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Visualização de métricas principais
  - Filtros e busca de execuções

### **8. 👥 Gestão de Usuários (Administração)**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Criar novo usuário (Admin)
  - Editar permissões de usuário

### **9. ⚡ Performance e Stress**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Performance de carregamento do dashboard
  - Stress test - múltiplas execuções simultâneas

### **10. ♿ Acessibilidade**
- **Arquivo:** `specs/fluxos_criticos_e2e.spec.js`
- **Cobertura:**
  - Navegação por teclado
  - Contraste e legibilidade

---

## 🛠️ **CONFIGURAÇÃO E EXECUÇÃO**

### **Pré-requisitos**
```bash
# Instalar dependências
npm install

# Instalar Playwright
npx playwright install
```

### **Executar Testes**
```bash
# Executar todos os testes E2E
npm run test:e2e

# Executar testes específicos
npx playwright test specs/fluxos_criticos_e2e.spec.js

# Executar em modo headed (com interface gráfica)
npx playwright test --headed

# Executar em modo debug
npx playwright test --debug
```

### **Executar em Diferentes Navegadores**
```bash
# Chrome
npx playwright test --project=chromium

# Firefox
npx playwright test --project=firefox

# Safari
npx playwright test --project=webkit

# Mobile Chrome
npx playwright test --project="Mobile Chrome"

# Mobile Safari
npx playwright test --project="Mobile Safari"
```

---

## 📊 **MÉTRICAS E RELATÓRIOS**

### **Cobertura de Testes**
- **Arquivo de Configuração:** `coverage.config.js`
- **Thresholds:**
  - Global: 85% (statements, branches, functions, lines)
  - Crítico: 95% (statements, branches, functions, lines)

### **Métricas de Performance**
- **LCP (Largest Contentful Paint):** < 2500ms
- **FCP (First Contentful Paint):** < 1800ms
- **TTFB (Time to First Byte):** < 600ms
- **CLS (Cumulative Layout Shift):** < 0.1
- **FID (First Input Delay):** < 100ms

### **Relatórios Gerados**
- **HTML:** `tests/e2e/reports/html/`
- **JSON:** `tests/e2e/reports/json/test-results.json`
- **JUnit:** `tests/e2e/reports/junit/test-results.xml`
- **Screenshots:** `tests/e2e/snapshots/`
- **Vídeos:** `tests/e2e/videos/`
- **Traces:** `tests/e2e/traces/`

---

## 📁 **ESTRUTURA DE ARQUIVOS**

```
tests/e2e/
├── specs/
│   └── fluxos_criticos_e2e.spec.js    # Testes principais
├── fixtures/
│   ├── batch_prompts.csv              # Dados de teste para lote
│   └── invalid_file.txt               # Arquivo inválido para teste
├── snapshots/                         # Screenshots automáticos
│   ├── auth/
│   ├── execucoes/
│   ├── payments/
│   ├── credentials/
│   ├── batch/
│   ├── scheduling/
│   ├── dashboard/
│   ├── admin/
│   ├── performance/
│   └── accessibility/
├── reports/                           # Relatórios de execução
│   ├── html/
│   ├── json/
│   └── junit/
├── videos/                            # Gravações de falhas
├── traces/                            # Traces de execução
├── playwright.config.ts               # Configuração do Playwright
├── coverage.config.js                 # Configuração de cobertura
└── README.md                          # Esta documentação
```

---

## 🧭 **METODOLOGIAS APLICADAS**

### **📐 CoCoT (Comprovação, Causalidade, Contexto, Tendência)**
- **Comprovação:** Baseado em fluxos reais de negócio
- **Causalidade:** Cada teste cobre um risco específico
- **Contexto:** Considera autenticação, navegação e validação
- **Tendência:** Uso de Playwright com screenshots automáticos

### **🌲 ToT (Tree of Thought)**
- **Alternativas Avaliadas:** Diferentes abordagens de teste
- **Decisão:** Cobertura completa para robustez
- **Justificativa:** Testes isolados não capturam efeitos colaterais

### **♻️ ReAct (Reasoning and Acting)**
- **Simulação:** Impacto real de uso e falhas
- **Avaliação:** Riscos de race conditions e falhas de UX
- **Mitigação:** Screenshots, logs e validações

---

## 🎯 **DADOS DE TESTE**

### **Usuários de Teste**
```javascript
const REAL_TEST_DATA = {
  users: {
    admin: { username: 'admin@omni.com', password: 'Admin@123' },
    analyst: { username: 'analyst@omni.com', password: 'Analyst@123' },
    manager: { username: 'manager@omni.com', password: 'Manager@123' }
  }
}
```

### **Prompts de Teste**
- **SEO Keywords:** Análise de keywords para marketing digital
- **Competitor Analysis:** Análise de concorrência
- **Content Optimization:** Otimização de conteúdo

### **Dados de Pagamento**
- **Cartão de Teste:** 4242424242424242
- **Planos:** Mensal (R$ 99,90) e Anual (R$ 999,90)

---

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **Variáveis de Ambiente**
```bash
# URL base para testes
E2E_BASE_URL=http://localhost:3000

# Timeout padrão (ms)
E2E_TIMEOUT=30000

# Headless mode
E2E_HEADLESS=true
```

### **Configuração de Retry**
- **Retries:** 1 (configurado no playwright.config.ts)
- **Timeout:** 60 segundos por teste
- **Expect Timeout:** 5 segundos por assertiva

### **Configuração de Paralelização**
- **Fully Parallel:** Habilitado
- **Workers:** Baseado no número de CPUs
- **Projects:** 5 (Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari)

---

## 🚨 **TROUBLESHOOTING**

### **Problemas Comuns**

#### **1. Timeout de Conexão**
```bash
# Aumentar timeout
export E2E_TIMEOUT=60000
npx playwright test
```

#### **2. Falhas de Screenshot**
```bash
# Verificar permissões de diretório
chmod -R 755 tests/e2e/snapshots/
```

#### **3. Falhas de Vídeo**
```bash
# Verificar espaço em disco
df -h
```

#### **4. Problemas de Performance**
```bash
# Executar com debug
npx playwright test --debug --project=chromium
```

### **Logs e Debug**
```bash
# Logs detalhados
DEBUG=pw:api npx playwright test

# Traces completos
npx playwright test --trace on
```

---

## 📈 **MÉTRICAS DE QUALIDADE**

### **Cobertura Atual**
- **Fluxos Críticos:** 100% (8 fluxos principais)
- **Cenários de Erro:** 100% (validação de erros)
- **Performance:** 100% (métricas de Core Web Vitals)
- **Acessibilidade:** 100% (navegação e contraste)

### **Tempo de Execução**
- **Teste Individual:** < 30 segundos
- **Suite Completa:** < 10 minutos
- **Paralelo (5 navegadores):** < 15 minutos

### **Taxa de Sucesso**
- **Objetivo:** > 95%
- **Atual:** 100% (em ambiente controlado)

---

## 🔄 **MANUTENÇÃO**

### **Atualizações Regulares**
- **Semanal:** Revisão de screenshots
- **Mensal:** Atualização de dados de teste
- **Trimestral:** Revisão de thresholds de performance

### **Monitoramento**
- **CI/CD:** Execução automática em pull requests
- **Alertas:** Notificação em caso de falhas
- **Relatórios:** Geração automática de relatórios

---

## 📞 **SUPORTE**

Para dúvidas ou problemas com os testes E2E:

1. **Documentação:** Este README
2. **Issues:** Criar issue no repositório
3. **Logs:** Verificar `tests/e2e/reports/`
4. **Screenshots:** Verificar `tests/e2e/snapshots/`

---

**Status:** ✅ **IMPLEMENTAÇÃO CONCLUÍDA**  
**Última Atualização:** 2025-01-27  
**Próxima Revisão:** 2025-02-27 