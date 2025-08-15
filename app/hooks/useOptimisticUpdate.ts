/**
 * Hook para Optimistic Updates
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 7.3
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { useState, useCallback, useRef } from 'react';
import { globalCache } from '../services/cache/intelligent-cache';

export interface OptimisticUpdateConfig<T> {
  cacheKey: string;
  updateFn: (data: T) => T;
  rollbackFn?: (originalData: T) => void;
  onSuccess?: (data: T) => void;
  onError?: (error: Error, originalData: T) => void;
  timeout?: number; // Timeout para rollback automático
}

export interface OptimisticUpdateResult<T> {
  isPending: boolean;
  error: Error | null;
  execute: (apiCall: () => Promise<T>) => Promise<T>;
  rollback: () => void;
}

export function useOptimisticUpdate<T>(config: OptimisticUpdateConfig<T>): OptimisticUpdateResult<T> {
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const originalDataRef = useRef<T | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Executa update otimista
   */
  const execute = useCallback(async (apiCall: () => Promise<T>): Promise<T> => {
    try {
      setIsPending(true);
      setError(null);

      // 1. Salvar dados originais
      const originalData = globalCache.get<T>(config.cacheKey);
      originalDataRef.current = originalData;

      // 2. Aplicar update otimista
      if (originalData) {
        const optimisticData = config.updateFn(originalData);
        globalCache.set(config.cacheKey, optimisticData, 0); // Sem TTL para dados otimistas
      }

      // 3. Configurar timeout para rollback automático
      if (config.timeout) {
        timeoutRef.current = setTimeout(() => {
          if (isPending) {
            rollback();
            setError(new Error('Timeout: Rollback automático executado'));
          }
        }, config.timeout);
      }

      // 4. Executar chamada real da API
      const result = await apiCall();

      // 5. Limpar timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      // 6. Atualizar cache com dados reais
      globalCache.set(config.cacheKey, result);

      // 7. Notificar sucesso
      if (config.onSuccess) {
        config.onSuccess(result);
      }

      setIsPending(false);
      return result;

    } catch (err) {
      // 8. Em caso de erro, fazer rollback
      rollback();
      
      const error = err instanceof Error ? err : new Error('Erro desconhecido');
      setError(error);

      if (config.onError && originalDataRef.current) {
        config.onError(error, originalDataRef.current);
      }

      setIsPending(false);
      throw error;
    }
  }, [config]);

  /**
   * Faz rollback para dados originais
   */
  const rollback = useCallback(() => {
    if (originalDataRef.current !== null) {
      globalCache.set(config.cacheKey, originalDataRef.current);
      
      if (config.rollbackFn) {
        config.rollbackFn(originalDataRef.current);
      }
      
      originalDataRef.current = null;
    }

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, [config]);

  return {
    isPending,
    error,
    execute,
    rollback
  };
}

/**
 * Hook especializado para updates de lista
 */
export function useOptimisticListUpdate<T>(
  cacheKey: string,
  itemId: string | number
) {
  return useOptimisticUpdate<T[]>({
    cacheKey,
    updateFn: (list) => {
      // Implementação específica para listas
      return list.map(item => 
        (item as any).id === itemId 
          ? { ...item, isOptimistic: true }
          : item
      );
    },
    rollbackFn: (originalList) => {
      // Remove flag otimista
      return originalList.map(item => {
        const { isOptimistic, ...cleanItem } = item as any;
        return cleanItem;
      });
    }
  });
}

/**
 * Hook especializado para criação otimista
 */
export function useOptimisticCreate<T>(cacheKey: string) {
  return useOptimisticUpdate<T[]>({
    cacheKey,
    updateFn: (list) => {
      // Adiciona item temporário no início da lista
      const tempItem = {
        id: `temp_${Date.now()}`,
        isOptimistic: true,
        createdAt: new Date().toISOString()
      } as T;
      
      return [tempItem, ...list];
    },
    rollbackFn: (originalList) => {
      // Remove item temporário
      return originalList.filter((item: any) => !item.isOptimistic);
    }
  });
}

/**
 * Hook especializado para deleção otimista
 */
export function useOptimisticDelete<T>(cacheKey: string) {
  return useOptimisticUpdate<T[]>({
    cacheKey,
    updateFn: (list) => {
      // Remove item da lista imediatamente
      return list.filter((item: any) => !item.isOptimistic);
    },
    rollbackFn: (originalList) => {
      // Restaura lista original
      return originalList;
    }
  });
} 