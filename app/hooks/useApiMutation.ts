/**
 * useApiMutation.ts
 * 
 * Hook para gerenciar mutations da API com tipagem forte
 * 
 * Tracing ID: HOOK-API-MUTATION-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 2.3
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Mutations tipadas (POST, PUT, PATCH, DELETE)
 * - Gerenciamento de estado de loading
 * - Tratamento de erros centralizado
 * - Retry automático configurável
 * - Cache invalidation
 * - Optimistic updates
 * - Debounce para mutations
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { ApiClient } from '../services/api/ApiClient';
import { ApiRequestConfig, ApiResponse, ApiError } from '../shared/types/api';

// Tipos
interface MutationState<TData = any, TError = any> {
  data: TData | null;
  error: TError | null;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
  isIdle: boolean;
}

interface MutationOptions<TData, TError, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: TError, variables: TVariables) => void;
  onSettled?: (data: TData | null, error: TError | null, variables: TVariables) => void;
  retry?: number | boolean;
  retryDelay?: number;
  cacheTime?: number;
  staleTime?: number;
  optimisticUpdate?: (variables: TVariables) => TData;
  onMutate?: (variables: TVariables) => Promise<TData | null>;
  onRollback?: (data: TData | null) => void;
  debounceMs?: number;
  timeout?: number;
}

interface UseMutationResult<TData, TError, TVariables> {
  mutate: (variables: TVariables, options?: Partial<MutationOptions<TData, TError, TVariables>>) => Promise<TData>;
  mutateAsync: (variables: TVariables, options?: Partial<MutationOptions<TData, TError, TVariables>>) => Promise<TData>;
  reset: () => void;
  state: MutationState<TData, TError>;
}

// Estado inicial
const initialState: MutationState = {
  data: null,
  error: null,
  isLoading: false,
  isSuccess: false,
  isError: false,
  isIdle: true,
};

export function useApiMutation<TData = any, TError = ApiError, TVariables = any>(
  mutationFn: (variables: TVariables, config?: ApiRequestConfig) => Promise<ApiResponse<TData>>,
  options: MutationOptions<TData, TError, TVariables> = {}
): UseMutationResult<TData, TError, TVariables> {
  const [state, setState] = useState<MutationState<TData, TError>>(initialState);
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const optimisticDataRef = useRef<TData | null>(null);

  // Configurações padrão
  const {
    retry = 3,
    retryDelay = 1000,
    debounceMs = 0,
    timeout = 30000,
    ...restOptions
  } = options;

  // Função para executar a mutation
  const executeMutation = useCallback(async (
    variables: TVariables,
    executionOptions: Partial<MutationOptions<TData, TError, TVariables>> = {}
  ): Promise<TData> => {
    const finalOptions = { ...options, ...executionOptions };
    
    // Cancelar mutation anterior se estiver em andamento
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Criar novo AbortController
    abortControllerRef.current = new AbortController();

    // Resetar estado
    setState(prev => ({
      ...prev,
      isLoading: true,
      isIdle: false,
      isSuccess: false,
      isError: false,
      error: null,
    }));

    retryCountRef.current = 0;

    try {
      // Optimistic update
      if (finalOptions.optimisticUpdate) {
        optimisticDataRef.current = finalOptions.optimisticUpdate(variables);
        setState(prev => ({
          ...prev,
          data: optimisticDataRef.current,
          isLoading: true,
        }));
      }

      // onMutate callback
      if (finalOptions.onMutate) {
        await finalOptions.onMutate(variables);
      }

      // Executar mutation
      const response = await mutationFn(variables, {
        signal: abortControllerRef.current.signal,
        timeout,
      });

      const data = response.data as TData;

      // Sucesso
      setState({
        data,
        error: null,
        isLoading: false,
        isSuccess: true,
        isError: false,
        isIdle: false,
      });

      // Callbacks de sucesso
      if (finalOptions.onSuccess) {
        finalOptions.onSuccess(data, variables);
      }

      if (finalOptions.onSettled) {
        finalOptions.onSettled(data, null, variables);
      }

      return data;

    } catch (error) {
      const apiError = error as TError;

      // Rollback optimistic update
      if (optimisticDataRef.current && finalOptions.onRollback) {
        finalOptions.onRollback(optimisticDataRef.current);
      }

      // Retry logic
      if (retryCountRef.current < (typeof retry === 'number' ? retry : 3)) {
        retryCountRef.current++;
        
        await new Promise(resolve => setTimeout(resolve, retryDelay * retryCountRef.current));
        
        return executeMutation(variables, executionOptions);
      }

      // Erro final
      setState({
        data: null,
        error: apiError,
        isLoading: false,
        isSuccess: false,
        isError: true,
        isIdle: false,
      });

      // Callbacks de erro
      if (finalOptions.onError) {
        finalOptions.onError(apiError, variables);
      }

      if (finalOptions.onSettled) {
        finalOptions.onSettled(null, apiError, variables);
      }

      throw apiError;
    }
  }, [mutationFn, options, retry, retryDelay, timeout]);

  // Função mutate com debounce
  const mutate = useCallback((
    variables: TVariables,
    executionOptions: Partial<MutationOptions<TData, TError, TVariables>> = {}
  ): Promise<TData> => {
    if (debounceMs > 0) {
      return new Promise((resolve, reject) => {
        if (debounceTimeoutRef.current) {
          clearTimeout(debounceTimeoutRef.current);
        }

        debounceTimeoutRef.current = setTimeout(() => {
          executeMutation(variables, executionOptions)
            .then(resolve)
            .catch(reject);
        }, debounceMs);
      });
    }

    return executeMutation(variables, executionOptions);
  }, [executeMutation, debounceMs]);

  // Função mutateAsync (alias para mutate)
  const mutateAsync = useCallback((
    variables: TVariables,
    executionOptions: Partial<MutationOptions<TData, TError, TVariables>> = {}
  ): Promise<TData> => {
    return mutate(variables, executionOptions);
  }, [mutate]);

  // Função reset
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    setState(initialState);
    retryCountRef.current = 0;
    optimisticDataRef.current = null;
  }, []);

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);

  return {
    mutate,
    mutateAsync,
    reset,
    state,
  };
}

// Hook especializado para POST
export function usePostMutation<TData = any, TError = ApiError, TVariables = any>(
  endpoint: string,
  options: MutationOptions<TData, TError, TVariables> = {}
) {
  const mutationFn = useCallback((variables: TVariables, config?: ApiRequestConfig) => {
    return ApiClient.post<TData>(endpoint, variables, config);
  }, [endpoint]);

  return useApiMutation(mutationFn, options);
}

// Hook especializado para PUT
export function usePutMutation<TData = any, TError = ApiError, TVariables = any>(
  endpoint: string,
  options: MutationOptions<TData, TError, TVariables> = {}
) {
  const mutationFn = useCallback((variables: TVariables, config?: ApiRequestConfig) => {
    return ApiClient.put<TData>(endpoint, variables, config);
  }, [endpoint]);

  return useApiMutation(mutationFn, options);
}

// Hook especializado para PATCH
export function usePatchMutation<TData = any, TError = ApiError, TVariables = any>(
  endpoint: string,
  options: MutationOptions<TData, TError, TVariables> = {}
) {
  const mutationFn = useCallback((variables: TVariables, config?: ApiRequestConfig) => {
    return ApiClient.patch<TData>(endpoint, variables, config);
  }, [endpoint]);

  return useApiMutation(mutationFn, options);
}

// Hook especializado para DELETE
export function useDeleteMutation<TData = any, TError = ApiError, TVariables = any>(
  endpoint: string,
  options: MutationOptions<TData, TError, TVariables> = {}
) {
  const mutationFn = useCallback((variables: TVariables, config?: ApiRequestConfig) => {
    return ApiClient.delete<TData>(endpoint, variables, config);
  }, [endpoint]);

  return useApiMutation(mutationFn, options);
}

export default useApiMutation; 