# 📚 **GUIAS DE MIGRAÇÃO**

**Tracing ID:** `MIGRATION_GUIDES_20250127_001`  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ **IMPLEMENTADO**

---

## 🎯 **OBJETIVO**
Guias completos para migração entre versões do sistema de comunicação backend-frontend, garantindo transições seguras e sem quebra de funcionalidades.

---

## 📋 **MIGRAÇÃO v1.0 → v1.1**

### **🔴 Breaking Changes**

#### **1. useApiClient - Mudança na API**
**Antes:**
```typescript
const apiClient = useApiClient();
const response = await apiClient.request('/api/data');
```

**Depois:**
```typescript
const apiClient = useApiClient();
const response = await apiClient.get('/api/data');
```

#### **2. useApiQuery - Mudança nas opções**
**Antes:**
```typescript
const { data } = useApiQuery('/api/users', {
  cacheTime: 300000,
  refetchOnWindowFocus: true
});
```

**Depois:**
```typescript
const { data } = useApiQuery('/api/users', {
  cacheTime: 300000,
  staleTime: 60000, // Nova opção obrigatória
  refetchOnWindowFocus: true
});
```

#### **3. useAuth - Mudança na estrutura de retorno**
**Antes:**
```typescript
const { user, isLoggedIn, login } = useAuth();
```

**Depois:**
```typescript
const { user, isAuthenticated, login } = useAuth();
```

### **🟡 Deprecations**

#### **1. useApiMutation - Opção deprecated**
```typescript
// ❌ Deprecated
const { mutate } = useApiMutation('/api/users', {
  onSuccess: (data) => console.log(data)
});

// ✅ Nova sintaxe
const { mutate } = useApiMutation('/api/users', {
  onSuccess: (data, variables, context) => console.log(data)
});
```

#### **2. Stores - Método deprecated**
```typescript
// ❌ Deprecated
apiStore.setData('/api/users', users);

// ✅ Nova sintaxe
apiStore.setCache('/api/users', users, { ttl: 300000 });
```

### **🟢 Novas Funcionalidades**

#### **1. useWebSocket - Novas opções**
```typescript
const { send, lastMessage, readyState } = useWebSocket('wss://api.example.com', {
  reconnectInterval: 3000, // Nova opção
  heartbeatInterval: 30000, // Nova opção
  maxReconnectAttempts: 5 // Nova opção
});
```

#### **2. useLocalStorage - Nova funcionalidade**
```typescript
const [value, setValue] = useLocalStorage('key', defaultValue, {
  serializer: JSON.stringify, // Nova opção
  deserializer: JSON.parse // Nova opção
});
```

### **📝 Passos de Migração**

1. **Atualizar dependências:**
```bash
npm install @omni-keywords-finder/api-client@1.1.0
```

2. **Executar script de migração:**
```bash
npm run migrate:v1.1
```

3. **Verificar breaking changes:**
```bash
npm run check-breaking-changes
```

4. **Executar testes:**
```bash
npm run test:migration
```

---

## 📋 **MIGRAÇÃO v1.1 → v1.2**

### **🔴 Breaking Changes**

#### **1. useApiQuery - Mudança na estrutura de retorno**
**Antes:**
```typescript
const { data, loading, error } = useApiQuery('/api/users');
```

**Depois:**
```typescript
const { data, isLoading, error, isError } = useApiQuery('/api/users');
```

#### **2. useApiMutation - Mudança nas callbacks**
**Antes:**
```typescript
const { mutate } = useApiMutation('/api/users', {
  onSuccess: (data) => console.log(data),
  onError: (error) => console.error(error)
});
```

**Depois:**
```typescript
const { mutate } = useApiMutation('/api/users', {
  onSuccess: (data, variables, context) => console.log(data),
  onError: (error, variables, context) => console.error(error)
});
```

### **🟡 Deprecations**

#### **1. useAuth - Método deprecated**
```typescript
// ❌ Deprecated
const { refreshToken } = useAuth();
refreshToken();

// ✅ Nova sintaxe
const { refreshSession } = useAuth();
refreshSession();
```

### **🟢 Novas Funcionalidades**

#### **1. useApiQuery - Novas opções**
```typescript
const { data } = useApiQuery('/api/users', {
  select: (data) => data.users, // Nova opção
  enabled: shouldFetch, // Nova opção
  retry: 3, // Nova opção
  retryDelay: 1000 // Nova opção
});
```

#### **2. useWebSocket - Novas funcionalidades**
```typescript
const { send, lastMessage, readyState, events } = useWebSocket('wss://api.example.com', {
  onOpen: () => console.log('Connected'),
  onClose: () => console.log('Disconnected'),
  onError: (error) => console.error(error)
});
```

### **📝 Passos de Migração**

1. **Atualizar dependências:**
```bash
npm install @omni-keywords-finder/api-client@1.2.0
```

2. **Executar migração automática:**
```bash
npm run migrate:v1.2
```

3. **Verificar compatibilidade:**
```bash
npm run check-compatibility
```

---

## 📋 **MIGRAÇÃO v1.2 → v2.0**

### **🔴 Breaking Changes**

#### **1. useApiClient - Nova API**
**Antes:**
```typescript
const apiClient = useApiClient();
const response = await apiClient.get('/api/users');
```

**Depois:**
```typescript
const apiClient = useApiClient();
const response = await apiClient.request({
  url: '/api/users',
  method: 'GET'
});
```

#### **2. Stores - Nova arquitetura**
**Antes:**
```typescript
import { apiStore } from '@/stores/api-store';
apiStore.setCache('/api/users', users);
```

**Depois:**
```typescript
import { useApiStore } from '@/stores/api-store';
const { setCache } = useApiStore();
setCache('/api/users', users);
```

#### **3. useAuth - Nova estrutura**
**Antes:**
```typescript
const { user, isAuthenticated, login } = useAuth();
```

**Depois:**
```typescript
const { user, isAuthenticated, login, session } = useAuth();
```

### **🟡 Deprecations**

#### **1. useApiQuery - Opções deprecated**
```typescript
// ❌ Deprecated
const { data } = useApiQuery('/api/users', {
  cacheTime: 300000,
  staleTime: 60000
});

// ✅ Nova sintaxe
const { data } = useApiQuery('/api/users', {
  gcTime: 300000, // Renomeado de cacheTime
  staleTime: 60000
});
```

### **🟢 Novas Funcionalidades**

#### **1. useApiQuery - Novas funcionalidades**
```typescript
const { data, isFetching, isStale } = useApiQuery('/api/users', {
  placeholderData: [], // Nova opção
  structuralSharing: true, // Nova opção
  networkMode: 'online' // Nova opção
});
```

#### **2. useApiMutation - Novas funcionalidades**
```typescript
const { mutate, isPending, isError, isSuccess } = useApiMutation('/api/users', {
  mutationKey: ['users'], // Nova opção
  onMutate: (variables) => {}, // Nova opção
  onSettled: (data, error, variables, context) => {} // Nova opção
});
```

### **📝 Passos de Migração**

1. **Preparar para migração:**
```bash
npm run prepare-migration:v2.0
```

2. **Atualizar dependências:**
```bash
npm install @omni-keywords-finder/api-client@2.0.0
```

3. **Executar migração:**
```bash
npm run migrate:v2.0
```

4. **Verificar integridade:**
```bash
npm run verify-migration
```

---

## 📋 **MIGRAÇÃO v2.0 → v2.1**

### **🔴 Breaking Changes**

#### **1. useWebSocket - Nova API**
**Antes:**
```typescript
const { send, lastMessage, readyState } = useWebSocket('wss://api.example.com');
```

**Depois:**
```typescript
const { send, lastMessage, readyState, events } = useWebSocket({
  url: 'wss://api.example.com',
  protocols: ['protocol1', 'protocol2']
});
```

### **🟡 Deprecations**

#### **1. useApiQuery - Opção deprecated**
```typescript
// ❌ Deprecated
const { data } = useApiQuery('/api/users', {
  refetchOnWindowFocus: true
});

// ✅ Nova sintaxe
const { data } = useApiQuery('/api/users', {
  refetchOnWindowFocus: 'always'
});
```

### **🟢 Novas Funcionalidades**

#### **1. useApiQuery - Novas funcionalidades**
```typescript
const { data, isRefetching, isRefetchError } = useApiQuery('/api/users', {
  refetchOnMount: 'always', // Nova opção
  refetchOnReconnect: 'always', // Nova opção
  refetchOnWindowFocus: 'always' // Nova opção
});
```

### **📝 Passos de Migração**

1. **Atualizar dependências:**
```bash
npm install @omni-keywords-finder/api-client@2.1.0
```

2. **Executar migração:**
```bash
npm run migrate:v2.1
```

---

## 🛠️ **FERRAMENTAS DE MIGRAÇÃO**

### **1. Script de Migração Automática**
```bash
# Executar migração automática
npm run migrate:auto

# Verificar mudanças necessárias
npm run migrate:check

# Reverter migração
npm run migrate:revert
```

### **2. Validador de Compatibilidade**
```bash
# Verificar compatibilidade
npm run check-compatibility

# Gerar relatório de compatibilidade
npm run compatibility-report
```

### **3. Testes de Migração**
```bash
# Executar testes de migração
npm run test:migration

# Executar testes de regressão
npm run test:regression
```

---

## 📊 **MATRIZ DE COMPATIBILIDADE**

| Versão | React | TypeScript | Node.js | Compatibilidade |
|--------|-------|------------|---------|-----------------|
| v1.0   | 16+   | 4.0+       | 14+     | ⚠️ Deprecated   |
| v1.1   | 16+   | 4.5+       | 16+     | ⚠️ Deprecated   |
| v1.2   | 17+   | 4.5+       | 16+     | ⚠️ Deprecated   |
| v2.0   | 18+   | 4.8+       | 16+     | ✅ Atual        |
| v2.1   | 18+   | 5.0+       | 18+     | ✅ Atual        |

---

## 🚨 **PROBLEMAS COMUNS E SOLUÇÕES**

### **1. Erro de Tipagem**
**Problema:**
```typescript
Type 'boolean' is not assignable to type 'string | boolean'
```

**Solução:**
```typescript
// Atualizar tipo
const { data } = useApiQuery('/api/users', {
  refetchOnWindowFocus: 'always' // Usar string em vez de boolean
});
```

### **2. Erro de Método Não Encontrado**
**Problema:**
```typescript
apiClient.request is not a function
```

**Solução:**
```typescript
// Usar nova API
const response = await apiClient.request({
  url: '/api/users',
  method: 'GET'
});
```

### **3. Erro de Store**
**Problema:**
```typescript
apiStore.setCache is not a function
```

**Solução:**
```typescript
// Usar hook em vez de store direto
const { setCache } = useApiStore();
setCache('/api/users', users);
```

---

## 📞 **SUPORTE**

### **Canais de Suporte**
- 📧 **Email:** support@omni-keywords-finder.com
- 💬 **Slack:** #api-client-support
- 📖 **Documentação:** https://docs.omni-keywords-finder.com
- 🐛 **Issues:** https://github.com/omni-keywords-finder/api-client/issues

### **Recursos Adicionais**
- 📹 **Vídeos tutoriais:** https://youtube.com/omni-keywords-finder
- 📚 **Exemplos:** https://github.com/omni-keywords-finder/examples
- 🧪 **Playground:** https://playground.omni-keywords-finder.com

---

**Status:** ✅ **GUIAS DE MIGRAÇÃO CONCLUÍDOS** 🚀 