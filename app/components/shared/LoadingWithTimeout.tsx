/**
 * 🎯 Componente Loading com Timeout
 * 
 * Tracing ID: LOADING_TIMEOUT_COMPONENT_2025_001
 * Data/Hora: 2025-01-27 19:35:00 UTC
 * Versão: 1.0
 * Status: 🚀 IMPLEMENTAÇÃO
 * 
 * Componente que exibe loading com timeout configurável,
 * barra de progresso, contador regressivo e ações de retry/cancel.
 */

import React from 'react';
import { useLoadingWithTimeout, LoadingTimeoutConfig } from '../../hooks/useLoadingWithTimeout';

export interface LoadingWithTimeoutProps {
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

// Componente de loading padrão
const DefaultLoadingComponent: React.FC<{ progress: number; timeRemaining: number }> = ({ 
  progress, 
  timeRemaining 
}) => (
  <div className="flex flex-col items-center justify-center p-6 space-y-4">
    <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
    <div className="text-center">
      <p className="text-gray-600 mb-2">Carregando...</p>
      <div className="w-64 bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-sm text-gray-500 mt-2">
        Tempo restante: {Math.ceil(timeRemaining / 1000)}s
      </p>
    </div>
  </div>
);

// Componente de timeout padrão
const DefaultTimeoutComponent: React.FC<{ onRetry: () => void; onCancel: () => void }> = ({ 
  onRetry, 
  onCancel 
}) => (
  <div className="flex flex-col items-center justify-center p-6 space-y-4">
    <div className="w-16 h-16 border-4 border-red-200 border-t-red-600 rounded-full animate-spin"></div>
    <div className="text-center">
      <h3 className="text-lg font-semibold text-red-600 mb-2">Timeout</h3>
      <p className="text-gray-600 mb-4">
        A operação demorou mais do que o esperado.
      </p>
      <div className="flex space-x-3">
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Tentar Novamente
        </button>
        <button
          onClick={onCancel}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
        >
          Cancelar
        </button>
      </div>
    </div>
  </div>
);

// Componente de erro padrão
const DefaultErrorComponent: React.FC<{ error: Error; onRetry: () => void }> = ({ 
  error, 
  onRetry 
}) => (
  <div className="flex flex-col items-center justify-center p-6 space-y-4">
    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
      <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
    </div>
    <div className="text-center">
      <h3 className="text-lg font-semibold text-red-600 mb-2">Erro</h3>
      <p className="text-gray-600 mb-2">{error.message}</p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >
        Tentar Novamente
      </button>
    </div>
  </div>
);

export const LoadingWithTimeout: React.FC<LoadingWithTimeoutProps> = ({
  asyncFunction,
  config = {},
  children,
  loadingComponent: LoadingComponent = DefaultLoadingComponent,
  timeoutComponent: TimeoutComponent = DefaultTimeoutComponent,
  errorComponent: ErrorComponent = DefaultErrorComponent,
  autoExecute = true,
  onSuccess,
  onError,
  className = ''
}) => {
  const {
    isLoading,
    hasTimedOut,
    isCancelled,
    currentAttempt,
    timeRemaining,
    error,
    cancel,
    retry,
    reset
  } = useLoadingWithTimeout(asyncFunction, {
    ...config,
    onTimeout: () => {
      config.onTimeout?.();
    },
    onRetry: (attempt) => {
      config.onRetry?.(attempt);
    },
    onCancel: () => {
      config.onCancel?.();
    }
  });

  // Executar automaticamente se configurado
  React.useEffect(() => {
    if (autoExecute && !isLoading && !hasTimedOut && !error) {
      // Executar a função assíncrona
      const execute = async () => {
        try {
          const result = await asyncFunction();
          onSuccess?.(result);
        } catch (err) {
          onError?.(err instanceof Error ? err : new Error(String(err)));
        }
      };
      execute();
    }
  }, [autoExecute, isLoading, hasTimedOut, error, asyncFunction, onSuccess, onError]);

  // Calcular progresso
  const progress = React.useMemo(() => {
    const totalTime = config.timeout || 30000;
    return Math.max(0, Math.min(100, ((totalTime - timeRemaining) / totalTime) * 100));
  }, [timeRemaining, config.timeout]);

  // Renderizar baseado no estado
  if (isCancelled) {
    return (
      <div className={`text-center p-4 ${className}`}>
        <p className="text-gray-500">Operação cancelada</p>
        <button
          onClick={reset}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Reiniciar
        </button>
      </div>
    );
  }

  if (error && !hasTimedOut) {
    return (
      <div className={className}>
        <ErrorComponent error={error} onRetry={retry} />
      </div>
    );
  }

  if (hasTimedOut) {
    return (
      <div className={className}>
        <TimeoutComponent onRetry={retry} onCancel={cancel} />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className={className}>
        <LoadingComponent progress={progress} timeRemaining={timeRemaining} />
        {currentAttempt > 0 && (
          <div className="text-center mt-2">
            <p className="text-sm text-gray-500">
              Tentativa {currentAttempt} de {config.maxRetries || 3}
            </p>
          </div>
        )}
      </div>
    );
  }

  // Estado inicial ou após sucesso
  return <div className={className}>{children}</div>;
};

// Hook wrapper para facilitar uso
export const useLoadingWithTimeoutComponent = (
  asyncFunction: () => Promise<any>,
  config?: LoadingTimeoutConfig
) => {
  const [shouldExecute, setShouldExecute] = React.useState(false);
  
  const execute = React.useCallback(() => {
    setShouldExecute(true);
  }, []);

  const reset = React.useCallback(() => {
    setShouldExecute(false);
  }, []);

  return {
    execute,
    reset,
    Component: React.useMemo(() => {
      return (props: Omit<LoadingWithTimeoutProps, 'asyncFunction' | 'config'>) => (
        <LoadingWithTimeout
          asyncFunction={asyncFunction}
          config={config}
          autoExecute={shouldExecute}
          {...props}
        />
      );
    }, [asyncFunction, config, shouldExecute])
  };
};

// Componente de exemplo para uso rápido
export const QuickLoadingWithTimeout: React.FC<{
  promise: Promise<any>;
  timeout?: number;
  children?: React.ReactNode;
}> = ({ promise, timeout = 30000, children }) => {
  const asyncFunction = React.useCallback(() => promise, [promise]);
  
  return (
    <LoadingWithTimeout
      asyncFunction={asyncFunction}
      config={{ timeout }}
      autoExecute={true}
    >
      {children}
    </LoadingWithTimeout>
  );
}; 