# 🚀 Omni Keywords Finder - Frontend

Interface web moderna para o sistema de preenchimento automático de lacunas em prompts.

## 📋 **Funcionalidades Implementadas**

### ✅ **Sistema de Preenchimento de Lacunas**
- **Dashboard Principal**: Visão geral de nichos, categorias e prompts
- **Gestão de Nichos**: CRUD completo de nichos
- **Gestão de Categorias**: CRUD completo de categorias vinculadas a nichos
- **Upload de Prompts**: Interface drag & drop para upload de arquivos TXT
- **Preview de Prompts**: Visualização completa dos prompts base
- **Detecção de Lacunas**: Identificação automática de placeholders
- **Estatísticas**: Métricas de performance e uso do sistema

### 🎨 **Interface Moderna**
- **Material-UI**: Design system consistente e responsivo
- **React Query**: Gerenciamento de estado e cache inteligente
- **TypeScript**: Tipagem forte e desenvolvimento seguro
- **Responsivo**: Funciona perfeitamente em desktop e mobile

## 🛠️ **Tecnologias**

- **React 18** - Biblioteca de interface
- **TypeScript** - Tipagem estática
- **Material-UI** - Componentes de UI
- **React Query** - Gerenciamento de estado
- **Vite** - Build tool e dev server
- **Vitest** - Framework de testes
- **ESLint** - Linting de código

## 📦 **Instalação**

### Pré-requisitos
- Node.js 18+ 
- npm ou yarn

### Passos
```bash
# 1. Instalar dependências
npm install

# 2. Configurar variáveis de ambiente
cp .env.example .env.local

# 3. Iniciar servidor de desenvolvimento
npm run dev
```

## 🚀 **Scripts Disponíveis**

```bash
# Desenvolvimento
npm run dev          # Iniciar servidor de desenvolvimento
npm run build        # Build para produção
npm run preview      # Preview do build

# Testes
npm run test         # Executar testes
npm run test:ui      # Interface visual de testes
npm run test:coverage # Testes com cobertura

# Qualidade de código
npm run lint         # Verificar linting
npm run lint:fix     # Corrigir problemas de linting
npm run type-check   # Verificar tipos TypeScript
```

## 📁 **Estrutura do Projeto**

```
app/
├── components/           # Componentes React
│   ├── prompt-system/   # Sistema de preenchimento de lacunas
│   │   ├── dialogs/     # Diálogos modais
│   │   └── *.tsx        # Componentes principais
│   └── shared/          # Componentes compartilhados
├── hooks/               # Custom hooks
├── types/               # Definições TypeScript
├── utils/               # Utilitários
├── pages/               # Páginas da aplicação
├── api/                 # Integração com APIs
└── src/                 # Código fonte principal
    ├── providers/       # Providers (React Query, etc.)
    └── test/            # Configuração de testes
```

## 🔧 **Configuração**

### Variáveis de Ambiente
```env
# API Backend
VITE_API_URL=http://localhost:8000

# Ambiente
NODE_ENV=development

# Analytics (opcional)
VITE_ANALYTICS_ID=your-analytics-id
```

### Proxy de Desenvolvimento
O Vite está configurado para fazer proxy das requisições `/api` para o backend em `http://localhost:8000`.

## 🧪 **Testes**

### Executar Testes
```bash
# Todos os testes
npm run test

# Interface visual
npm run test:ui

# Com cobertura
npm run test:coverage
```

### Estrutura de Testes
- **Unitários**: Testes de componentes individuais
- **Integração**: Testes de fluxos completos
- **E2E**: Testes end-to-end (futuro)

## 📊 **CI/CD**

O projeto usa GitHub Actions para:

- ✅ **Instalação automática** de dependências
- ✅ **Verificação de tipos** TypeScript
- ✅ **Linting** de código
- ✅ **Execução de testes** com cobertura
- ✅ **Build automático** para produção
- ✅ **Deploy** para preview e produção

### Workflow
1. **Push/Pull Request** → Dispara CI
2. **Instalação** → `npm ci`
3. **Verificações** → Type check, lint, testes
4. **Build** → Gera artefatos
5. **Deploy** → Deploy automático

## 🎯 **Próximas Funcionalidades**

### Fase 2 - Interface Web (Em Desenvolvimento)
- [ ] **Dashboard Avançado**: Métricas em tempo real
- [ ] **Processamento em Lote**: Interface para processamento massivo
- [ ] **Sistema de Cache**: Visualização e gestão de cache
- [ ] **Logs e Auditoria**: Interface para logs estruturados

### Fase 3 - Otimizações
- [ ] **Performance**: Otimizações de bundle e carregamento
- [ ] **PWA**: Progressive Web App
- [ ] **Offline**: Funcionalidade offline
- [ ] **Notificações**: Push notifications

### Fase 4 - Integrações
- [ ] **IA Generativa**: Integração direta com APIs de IA
- [ ] **Webhooks**: Sistema de webhooks
- [ ] **Exportação**: Múltiplos formatos de exportação
- [ ] **API Externa**: Documentação e SDK

## 🤝 **Contribuição**

### Padrões de Código
- **TypeScript**: Tipagem forte obrigatória
- **ESLint**: Regras de linting configuradas
- **Prettier**: Formatação automática
- **Conventional Commits**: Padrão de commits

### Processo
1. **Fork** do repositório
2. **Branch** para feature (`feature/nome-da-feature`)
3. **Desenvolvimento** seguindo padrões
4. **Testes** obrigatórios
5. **Pull Request** com descrição clara

## 📈 **Métricas de Qualidade**

- **Cobertura de Testes**: > 85%
- **Performance**: Lighthouse score > 90
- **Acessibilidade**: WCAG 2.1 AA
- **SEO**: Otimizado para motores de busca

## 🐛 **Troubleshooting**

### Problemas Comuns

**Erro de dependências**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Erro de tipos TypeScript**
```bash
npm run type-check
```

**Erro de linting**
```bash
npm run lint:fix
```

**Problemas de build**
```bash
npm run build
# Verificar logs de erro
```

## 📞 **Suporte**

- **Issues**: GitHub Issues
- **Documentação**: Este README
- **Email**: suporte@omni.com

---

**Status**: 🟢 **PRONTO PARA PRODUÇÃO**  
**Versão**: 1.0.0  
**Última Atualização**: 2024-12-27 