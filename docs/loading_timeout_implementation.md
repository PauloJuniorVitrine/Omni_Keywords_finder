# 🎯 Sistema de Loading com Timeout - Omni Keywords Finder

**Tracing ID:** `LOADING_TIMEOUT_DOCS_2025_001`  
**Data/Hora:** 2025-01-27 19:45:00 UTC  
**Versão:** 1.0  
**Status:** 📚 DOCUMENTAÇÃO COMPLETA  

---

## 🎯 **OBJETIVO**

Este documento descreve a implementação do sistema de loading com timeout no Omni Keywords Finder, incluindo o hook `useLoadingWithTimeout` e o componente `LoadingWithTimeout`.

---

## 🏗️ **ARQUITETURA**

### **Componentes Principais**

1. **`app/hooks/useLoadingWithTimeout.ts`** - Hook principal para gerenciar loading com timeout
2. **`app/components/shared/LoadingWithTimeout.tsx`** - Componente React que utiliza o hook
3. **`tests/unit/frontend/test_loading_timeout.ts`** - Testes unitários completos

### **Fluxo de Execução**

```
Início → Loading → [Timeout/Erro/Sucesso] → [Retry/Cancel] → Final
  ↓         ↓              ↓                    ↓           ↓
Estado   Execução      Tratamento           Ações       Resultado
Inicial  Assíncrona    de Resultado        do Usuário   Final
```

---

## 🎣 **HOOK: useLoadingWithTimeout**

### **Interface de Configuração**

```typescript
interface LoadingTimeoutConfig {
  /** Timeout em milissegundos (padrão: 30000ms = 30s) */
  timeout?: number;
  /** Número máximo de tentativas (padrão: 3) */
  maxRetries?: number;
  /** Delay entre tentativas em ms (padrão: 2000ms = 2s) */
  retryDelay?: number;
  /** Se deve fazer retry automático (padrão: true) */
  autoRetry?: boolean;
  /** Callback executado no timeout */
  onTimeout?: () => void;
  /** Callback executado no retry */
  onRetry?: (attempt: number) => void;
  /** Callback executado no cancelamento */
  onCancel?: () => void;
}
```

### **Estado Retornado**

```typescript
interface LoadingTimeoutState {
  /** Se está carregando */
  isLoading: boolean;
  /** Se houve timeout */
  hasTimedOut: boolean;
  /** Se foi cancelado */
  isCancelled: boolean;
  /** Número da tentativa atual */
  currentAttempt: number;
  /** Tempo restante em ms */
  timeRemaining: number;
  /** Erro atual */
  error: Error | null;
  /** Função para cancelar */
  cancel: () => void;
  /** Função para retry manual */
  retry: () => void;
  /** Função para resetar estado */
  reset: () => void;
}
```

### **Uso Básico**

```typescript
import { useLoadingWithTimeout } from '../hooks/useLoadingWithTimeout';

const MyComponent = () => {
  const asyncFunction = async () => {
    // Sua função assíncrona aqui
    const response = await fetch('/api/data');
    return response.json();
  };

  const {
    isLoading,
    hasTimedOut,
    error,
    cancel,
    retry,
    timeRemaining
  } = useLoadingWithTimeout(asyncFunction, {
    timeout: 15000, // 15 segundos
    maxRetries: 3,
    autoRetry: true
  });

  return (
    <div>
      {isLoading && <p>Carregando... {Math.ceil(timeRemaining / 1000)}s</p>}
      {hasTimedOut && <p>Timeout! <button onClick={retry}>Tentar Novamente</button></p>}
      {error && <p>Erro: {error.message}</p>}
      <button onClick={cancel}>Cancelar</button>
    </div>
  );
};
```

### **Configurações Avançadas**

```typescript
// Configuração para operações críticas
const criticalConfig: LoadingTimeoutConfig = {
  timeout: 60000,        // 1 minuto
  maxRetries: 5,         // 5 tentativas
  retryDelay: 5000,      // 5 segundos entre tentativas
  autoRetry: true,
  onTimeout: () => {
    console.log('Operação crítica falhou por timeout');
    // Notificar usuário ou sistema
  },
  onRetry: (attempt) => {
    console.log(`Tentativa ${attempt} iniciada`);
  },
  onCancel: () => {
    console.log('Operação cancelada pelo usuário');
  }
};

// Configuração para operações rápidas
const quickConfig: LoadingTimeoutConfig = {
  timeout: 5000,         // 5 segundos
  maxRetries: 1,         // Apenas 1 retry
  retryDelay: 1000,      // 1 segundo entre tentativas
  autoRetry: false       // Sem retry automático
};
```

---

## 🧩 **COMPONENTE: LoadingWithTimeout**

### **Props**

```typescript
interface LoadingWithTimeoutProps {
  /** Função assíncrona a ser executada */
  asyncFunction: () => Promise<any>;
  /** Configuração do timeout */
  config?: LoadingTimeoutConfig;
  /** Conteúdo a ser exibido durante loading */
  children?: React.ReactNode;
  /** Componente de loading customizado */
  loadingComponent?: React.ComponentType<{ progress: number; timeRemaining: number }>;
  /** Componente de timeout customizado */
  timeoutComponent?: React.ComponentType<{ onRetry: () => void; onCancel: () => void }>;
  /** Componente de erro customizado */
  errorComponent?: React.ComponentType<{ error: Error; onRetry: () => void }>;
  /** Se deve executar automaticamente */
  autoExecute?: boolean;
  /** Callback executado no sucesso */
  onSuccess?: (data: any) => void;
  /** Callback executado no erro */
  onError?: (error: Error) => void;
  /** Classes CSS customizadas */
  className?: string;
}
```

### **Uso Básico**

```typescript
import { LoadingWithTimeout } from '../components/shared/LoadingWithTimeout';

const MyComponent = () => {
  const fetchData = async () => {
    const response = await fetch('/api/data');
    return response.json();
  };

  return (
    <LoadingWithTimeout
      asyncFunction={fetchData}
      config={{ timeout: 10000 }}
      onSuccess={(data) => console.log('Dados carregados:', data)}
      onError={(error) => console.error('Erro:', error)}
    >
      <div>Conteúdo após carregamento</div>
    </LoadingWithTimeout>
  );
};
```

### **Componentes Customizados**

```typescript
// Componente de loading customizado
const CustomLoading = ({ progress, timeRemaining }: { progress: number; timeRemaining: number }) => (
  <div className="custom-loading">
    <div className="spinner"></div>
    <div className="progress-bar">
      <div className="progress-fill" style={{ width: `${progress}%` }}></div>
    </div>
    <p>Tempo restante: {Math.ceil(timeRemaining / 1000)}s</p>
  </div>
);

// Componente de timeout customizado
const CustomTimeout = ({ onRetry, onCancel }: { onRetry: () => void; onCancel: () => void }) => (
  <div className="custom-timeout">
    <h3>⏰ Tempo Esgotado</h3>
    <p>A operação demorou mais do que o esperado.</p>
    <div className="actions">
      <button onClick={onRetry} className="btn-primary">🔄 Tentar Novamente</button>
      <button onClick={onCancel} className="btn-secondary">❌ Cancelar</button>
    </div>
  </div>
);

// Uso com componentes customizados
<LoadingWithTimeout
  asyncFunction={fetchData}
  loadingComponent={CustomLoading}
  timeoutComponent={CustomTimeout}
  config={{ timeout: 15000 }}
>
  <div>Conteúdo carregado</div>
</LoadingWithTimeout>
```

---

## 🔧 **HOOKS AUXILIARES**

### **useExecuteWithTimeout**

Hook para executar função com timeout controlado:

```typescript
import { useExecuteWithTimeout } from '../hooks/useLoadingWithTimeout';

const MyComponent = () => {
  const [state, execute] = useExecuteWithTimeout(
    async () => {
      const response = await fetch('/api/data');
      return response.json();
    },
    { timeout: 10000 }
  );

  const handleClick = async () => {
    const result = await execute();
    if (result) {
      console.log('Resultado:', result);
    }
  };

  return (
    <div>
      <button onClick={handleClick} disabled={state.isLoading}>
        {state.isLoading ? 'Carregando...' : 'Executar'}
      </button>
      {state.error && <p>Erro: {state.error.message}</p>}
    </div>
  );
};
```

### **usePollingWithTimeout**

Hook para polling com timeout:

```typescript
import { usePollingWithTimeout } from '../hooks/useLoadingWithTimeout';

const MyComponent = () => {
  const {
    isLoading,
    data,
    startPolling,
    stopPolling,
    error
  } = usePollingWithTimeout(
    async () => {
      const response = await fetch('/api/status');
      return response.json();
    },
    {
      timeout: 30000,
      interval: 5000,  // Poll a cada 5 segundos
      maxPolls: 10     // Máximo 10 polls
    }
  );

  return (
    <div>
      <button onClick={startPolling}>Iniciar Polling</button>
      <button onClick={stopPolling}>Parar Polling</button>
      {isLoading && <p>Monitorando...</p>}
      {data && <p>Status: {data.status}</p>}
      {error && <p>Erro: {error.message}</p>}
    </div>
  );
};
```

---

## 🎨 **COMPONENTES DE EXEMPLO**

### **QuickLoadingWithTimeout**

Componente para uso rápido com Promise:

```typescript
import { QuickLoadingWithTimeout } from '../components/shared/LoadingWithTimeout';

const MyComponent = () => {
  const [promise, setPromise] = useState<Promise<any> | null>(null);

  const handleClick = () => {
    setPromise(fetch('/api/data').then(r => r.json()));
  };

  return (
    <div>
      <button onClick={handleClick}>Carregar Dados</button>
      {promise && (
        <QuickLoadingWithTimeout promise={promise} timeout={10000}>
          <div>Dados carregados com sucesso!</div>
        </QuickLoadingWithTimeout>
      )}
    </div>
  );
};
```

### **useLoadingWithTimeoutComponent**

Hook wrapper para facilitar uso:

```typescript
import { useLoadingWithTimeoutComponent } from '../components/shared/LoadingWithTimeout';

const MyComponent = () => {
  const { execute, Component } = useLoadingWithTimeoutComponent(
    async () => {
      const response = await fetch('/api/data');
      return response.json();
    },
    { timeout: 15000 }
  );

  return (
    <div>
      <button onClick={execute}>Executar</button>
      <Component>
        <div>Conteúdo após execução</div>
      </Component>
    </div>
  );
};
```

---

## 🧪 **TESTES**

### **Executar Testes**

```bash
# Executar todos os testes de loading timeout
npm test -- test_loading_timeout.ts

# Executar com coverage
npm test -- test_loading_timeout.ts --coverage

# Executar testes específicos
npm test -- -t "should handle timeout correctly"
```

### **Cobertura de Testes**

Os testes cobrem:

- ✅ **Estados iniciais** - Verificação de valores padrão
- ✅ **Execução assíncrona** - Loading state durante execução
- ✅ **Timeout** - Detecção e tratamento de timeout
- ✅ **Cancelamento** - Cancelamento manual de operações
- ✅ **Retry manual** - Retry controlado pelo usuário
- ✅ **Retry automático** - Retry automático em caso de erro
- ✅ **Limite de tentativas** - Respeito ao máximo de retries
- ✅ **Contador regressivo** - Atualização do tempo restante
- ✅ **Reset de estado** - Reset completo do estado
- ✅ **Edge cases** - Casos extremos e memory leaks

---

## 📊 **MÉTRICAS E MONITORAMENTO**

### **Métricas Coletadas**

```typescript
// Exemplo de métricas que podem ser coletadas
interface LoadingMetrics {
  operationName: string;
  duration: number;
  attempts: number;
  timeoutOccurred: boolean;
  cancelled: boolean;
  success: boolean;
  errorType?: string;
}
```

### **Integração com Analytics**

```typescript
const configWithAnalytics: LoadingTimeoutConfig = {
  timeout: 30000,
  onTimeout: () => {
    analytics.track('loading_timeout', {
      operation: 'fetch_data',
      timeout: 30000
    });
  },
  onRetry: (attempt) => {
    analytics.track('loading_retry', {
      operation: 'fetch_data',
      attempt: attempt
    });
  },
  onCancel: () => {
    analytics.track('loading_cancelled', {
      operation: 'fetch_data'
    });
  }
};
```

---

## 🔧 **CONFIGURAÇÃO POR AMBIENTE**

### **Desenvolvimento**

```typescript
const devConfig: LoadingTimeoutConfig = {
  timeout: 60000,        // Timeout mais longo para debug
  maxRetries: 5,         // Mais tentativas
  retryDelay: 1000,      // Retry mais rápido
  autoRetry: true
};
```

### **Produção**

```typescript
const prodConfig: LoadingTimeoutConfig = {
  timeout: 15000,        // Timeout mais restritivo
  maxRetries: 2,         // Menos tentativas
  retryDelay: 3000,      // Retry mais lento
  autoRetry: true
};
```

### **Testes**

```typescript
const testConfig: LoadingTimeoutConfig = {
  timeout: 1000,         // Timeout muito curto
  maxRetries: 1,         // Apenas 1 retry
  retryDelay: 100,       // Retry muito rápido
  autoRetry: false       // Sem retry automático
};
```

---

## 🚀 **MELHORIAS FUTURAS**

### **Planejadas**

1. **Cache inteligente** - Cache de resultados para evitar re-execução
2. **Priorização** - Sistema de prioridade para operações
3. **Batch operations** - Agrupamento de operações similares
4. **Progress tracking** - Rastreamento de progresso para operações longas
5. **WebSocket integration** - Integração com WebSocket para atualizações em tempo real

### **Otimizações**

1. **Debounce** - Evitar múltiplas execuções simultâneas
2. **Throttle** - Limitar frequência de execuções
3. **Memory optimization** - Otimização de uso de memória
4. **Performance monitoring** - Monitoramento de performance

---

## 📝 **EXEMPLOS DE USO REAL**

### **Carregamento de Dados de Nichos**

```typescript
const NichosList = () => {
  const { isLoading, hasTimedOut, error, retry } = useLoadingWithTimeout(
    async () => {
      const response = await fetch('/api/nichos');
      if (!response.ok) throw new Error('Falha ao carregar nichos');
      return response.json();
    },
    {
      timeout: 20000,
      maxRetries: 3,
      onTimeout: () => {
        toast.error('Timeout ao carregar nichos. Verifique sua conexão.');
      }
    }
  );

  if (isLoading) return <LoadingSpinner />;
  if (hasTimedOut) return <TimeoutMessage onRetry={retry} />;
  if (error) return <ErrorMessage error={error} onRetry={retry} />;

  return <NichosData />;
};
```

### **Upload de Arquivo com Progresso**

```typescript
const FileUpload = () => {
  return (
    <LoadingWithTimeout
      asyncFunction={async () => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        });
        return response.json();
      }}
      config={{
        timeout: 60000, // 1 minuto para upload
        maxRetries: 2,
        onTimeout: () => {
          toast.error('Upload demorou muito. Tente novamente.');
        }
      }}
      onSuccess={(result) => {
        toast.success('Arquivo enviado com sucesso!');
        onUploadComplete(result);
      }}
      onError={(error) => {
        toast.error(`Erro no upload: ${error.message}`);
      }}
    >
      <div>Arquivo enviado com sucesso!</div>
    </LoadingWithTimeout>
  );
};
```

---

**🔄 Documento será atualizado conforme novas funcionalidades são implementadas** 