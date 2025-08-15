/**
 * 🎯 Hook para Loading com Timeout
 * 
 * Tracing ID: USE_LOADING_TIMEOUT_2025_001
 * Data/Hora: 2025-01-27 19:30:00 UTC
 * Versão: 1.0
 * Status: 🚀 IMPLEMENTAÇÃO
 * 
 * Hook que gerencia estados de loading com timeout configurável,
 * retry automático e cancelamento manual.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export interface LoadingTimeoutConfig {
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

export interface LoadingTimeoutState {
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

export function useLoadingWithTimeout(
  asyncFunction: () => Promise<any>,
  config: LoadingTimeoutConfig = {}
): LoadingTimeoutState {
  const {
    timeout = 30000,
    maxRetries = 3,
    retryDelay = 2000,
    autoRetry = true,
    onTimeout,
    onRetry,
    onCancel
  } = config;

  // Estados
  const [isLoading, setIsLoading] = useState(false);
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const [isCancelled, setIsCancelled] = useState(false);
  const [currentAttempt, setCurrentAttempt] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(timeout);
  const [error, setError] = useState<Error | null>(null);

  // Refs para controle
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  // Função para cancelar
  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setIsLoading(false);
    setIsCancelled(true);
    setHasTimedOut(false);
    setTimeRemaining(timeout);
    setError(null);

    onCancel?.();
  }, [timeout, onCancel]);

  // Função para resetar
  const reset = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setIsLoading(false);
    setIsCancelled(false);
    setHasTimedOut(false);
    setCurrentAttempt(0);
    setTimeRemaining(timeout);
    setError(null);
  }, [timeout]);

  // Função para retry
  const retry = useCallback(async () => {
    if (currentAttempt >= maxRetries) {
      setError(new Error(`Máximo de tentativas (${maxRetries}) excedido`));
      return;
    }

    reset();
    setCurrentAttempt(prev => prev + 1);
    onRetry?.(currentAttempt + 1);

    await executeAsyncFunction();
  }, [currentAttempt, maxRetries, reset, onRetry]);

  // Função principal de execução
  const executeAsyncFunction = useCallback(async () => {
    if (!isMountedRef.current) return;

    setIsLoading(true);
    setIsCancelled(false);
    setHasTimedOut(false);
    setError(null);
    setTimeRemaining(timeout);

    // Configurar timeout
    timeoutRef.current = setTimeout(() => {
      if (!isMountedRef.current) return;

      setIsLoading(false);
      setHasTimedOut(true);
      setError(new Error(`Timeout após ${timeout}ms`));
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }

      onTimeout?.();

      // Retry automático se configurado
      if (autoRetry && currentAttempt < maxRetries) {
        setTimeout(() => {
          if (isMountedRef.current) {
            retry();
          }
        }, retryDelay);
      }
    }, timeout);

    // Configurar contador regressivo
    intervalRef.current = setInterval(() => {
      if (!isMountedRef.current) return;

      setTimeRemaining(prev => {
        const newTime = prev - 100;
        if (newTime <= 0) {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          return 0;
        }
        return newTime;
      });
    }, 100);

    try {
      await asyncFunction();
      
      if (!isMountedRef.current) return;

      // Sucesso - limpar timeouts
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }

      setIsLoading(false);
      setTimeRemaining(0);
    } catch (err) {
      if (!isMountedRef.current) return;

      setError(err instanceof Error ? err : new Error(String(err)));
      setIsLoading(false);

      // Retry automático se configurado
      if (autoRetry && currentAttempt < maxRetries) {
        setTimeout(() => {
          if (isMountedRef.current) {
            retry();
          }
        }, retryDelay);
      }
    }
  }, [asyncFunction, timeout, autoRetry, currentAttempt, maxRetries, retryDelay, onTimeout, retry]);

  return {
    isLoading,
    hasTimedOut,
    isCancelled,
    currentAttempt,
    timeRemaining,
    error,
    cancel,
    retry,
    reset
  };
}

// Hook para executar função com timeout
export function useExecuteWithTimeout<T>(
  asyncFunction: () => Promise<T>,
  config: LoadingTimeoutConfig = {}
): [LoadingTimeoutState, () => Promise<T | undefined>] {
  const state = useLoadingWithTimeout(asyncFunction, config);
  
  const execute = useCallback(async (): Promise<T | undefined> => {
    try {
      return await asyncFunction();
    } catch (error) {
      throw error;
    }
  }, [asyncFunction]);

  return [state, execute];
}

// Hook para polling com timeout
export function usePollingWithTimeout<T>(
  asyncFunction: () => Promise<T>,
  config: LoadingTimeoutConfig & {
    interval?: number; // Intervalo entre polls
    maxPolls?: number; // Máximo de polls
  } = {}
): LoadingTimeoutState & {
  data: T | null;
  startPolling: () => void;
  stopPolling: () => void;
} {
  const {
    interval = 5000,
    maxPolls = 10,
    ...timeoutConfig
  } = config;

  const [data, setData] = useState<T | null>(null);
  const [pollCount, setPollCount] = useState(0);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const state = useLoadingWithTimeout(asyncFunction, {
    ...timeoutConfig,
    onTimeout: () => {
      stopPolling();
      timeoutConfig.onTimeout?.();
    }
  });

  const startPolling = useCallback(() => {
    if (pollingRef.current) return;

    const poll = async () => {
      if (pollCount >= maxPolls) {
        stopPolling();
        return;
      }

      try {
        const result = await asyncFunction();
        setData(result);
        setPollCount(prev => prev + 1);
      } catch (error) {
        console.error('Erro no polling:', error);
      }

      if (pollingRef.current) {
        pollingRef.current = setTimeout(poll, interval);
      }
    };

    poll();
  }, [asyncFunction, interval, maxPolls, pollCount]);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  // Cleanup
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    ...state,
    data,
    startPolling,
    stopPolling
  };
} 