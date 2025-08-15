/**
 * useAppState.ts
 * 
 * Hooks customizados para gerenciamento de estado otimizado
 * 
 * Tracing ID: APP_STATE_HOOKS_001_20250127
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 17.2
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Hooks customizados
 * - Seletores otimizados
 * - Cache de dados
 * - Invalidação automática
 * - Memoização inteligente
 */

import React, { useCallback, useMemo, useEffect, useRef } from 'react';
import { useAppStore, useAppSelector } from '../AppStore';

// Tipos para cache e seletores
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  dependencies: any[];
}

interface SelectorOptions {
  equalityFn?: (a: any, b: any) => boolean;
  cacheKey?: string;
  ttl?: number;
  dependencies?: any[];
}

// Hook para seletores com cache automático
export const useAppState = <T>(
  selector: (state: any) => T,
  options: SelectorOptions = {}
) => {
  const { state, actions } = useAppStore();
  const cacheRef = useRef<Map<string, CacheEntry<T>>>(new Map());
  
  const {
    equalityFn,
    cacheKey,
    ttl = 5 * 60 * 1000, // 5 minutos padrão
    dependencies = []
  } = options;

  // Gerar chave de cache
  const key = useMemo(() => {
    if (cacheKey) return cacheKey;
    return `${selector.toString()}-${JSON.stringify(dependencies)}`;
  }, [cacheKey, dependencies]);

  // Verificar cache
  const cachedData = useMemo(() => {
    const cached = cacheRef.current.get(key);
    if (!cached) return null;

    const now = Date.now();
    const isExpired = now - cached.timestamp > cached.ttl;
    
    if (isExpired) {
      cacheRef.current.delete(key);
      return null;
    }

    return cached.data;
  }, [key]);

  // Selecionar dados do estado
  const selectedData = useAppSelector(selector, equalityFn);

  // Cache dos dados selecionados
  useEffect(() => {
    if (selectedData !== undefined) {
      cacheRef.current.set(key, {
        data: selectedData,
        timestamp: Date.now(),
        ttl,
        dependencies
      });
    }
  }, [selectedData, key, ttl, dependencies]);

  // Retornar dados (cached ou fresh)
  return cachedData !== null ? cachedData : selectedData;
};

// Hook para dados com invalidação automática
export const useAppData = <T>(
  selector: (state: any) => T,
  invalidateOn: string[] = [],
  options: SelectorOptions = {}
) => {
  const { state, actions } = useAppStore();
  const [isValid, setIsValid] = React.useState(true);
  const lastInvalidationRef = useRef<number>(0);

  // Monitorar mudanças que invalidam o cache
  useEffect(() => {
    const checkInvalidation = () => {
      const now = Date.now();
      const shouldInvalidate = invalidateOn.some(key => {
        const lastUpdate = state.cache.lastUpdated[key];
        if (!lastUpdate) return false;
        return new Date(lastUpdate).getTime() > lastInvalidationRef.current;
      });

      if (shouldInvalidate) {
        setIsValid(false);
        lastInvalidationRef.current = now;
        
        // Re-validar após um breve delay
        setTimeout(() => setIsValid(true), 100);
      }
    };

    checkInvalidation();
  }, [state.cache.lastUpdated, invalidateOn]);

  const data = useAppState(selector, {
    ...options,
    cacheKey: options.cacheKey ? `${options.cacheKey}-${isValid}` : undefined
  });

  return {
    data,
    isValid,
    invalidate: useCallback(() => setIsValid(false), [])
  };
};

// Hook para listas com paginação e filtros
export const useAppList = <T>(
  selector: (state: any) => T[],
  options: {
    page?: number;
    pageSize?: number;
    filters?: Record<string, any>;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
    cacheKey?: string;
  } = {}
) => {
  const {
    page = 1,
    pageSize = 10,
    filters = {},
    sortBy,
    sortOrder = 'asc',
    cacheKey
  } = options;

  const allData = useAppState(selector, { cacheKey });

  // Aplicar filtros
  const filteredData = useMemo(() => {
    if (!allData || !Array.isArray(allData)) return [];
    
    let filtered = [...allData];
    
    // Aplicar filtros
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        filtered = filtered.filter(item => {
          const itemValue = item[key];
          if (typeof value === 'string') {
            return itemValue?.toLowerCase().includes(value.toLowerCase());
          }
          return itemValue === value;
        });
      }
    });

    // Aplicar ordenação
    if (sortBy) {
      filtered.sort((a, b) => {
        const aValue = a[sortBy];
        const bValue = b[sortBy];
        
        if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [allData, filters, sortBy, sortOrder]);

  // Aplicar paginação
  const paginatedData = useMemo(() => {
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return filteredData.slice(startIndex, endIndex);
  }, [filteredData, page, pageSize]);

  // Calcular metadados
  const metadata = useMemo(() => {
    const total = filteredData.length;
    const totalPages = Math.ceil(total / pageSize);
    const hasNextPage = page < totalPages;
    const hasPrevPage = page > 1;

    return {
      total,
      totalPages,
      currentPage: page,
      pageSize,
      hasNextPage,
      hasPrevPage,
      startIndex: (page - 1) * pageSize + 1,
      endIndex: Math.min(page * pageSize, total)
    };
  }, [filteredData.length, page, pageSize]);

  return {
    data: paginatedData,
    metadata,
    allData: filteredData,
    isLoading: allData === undefined
  };
};

// Hook para dados relacionados
export const useAppRelated = <T>(
  selector: (state: any) => T[],
  relationKey: string,
  relationValue: any,
  options: SelectorOptions = {}
) => {
  const data = useAppState(selector, {
    ...options,
    cacheKey: `${options.cacheKey || 'related'}-${relationKey}-${relationValue}`
  });

  const relatedData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    return data.filter(item => item[relationKey] === relationValue);
  }, [data, relationKey, relationValue]);

  return relatedData;
};

// Hook para estatísticas e métricas
export const useAppStats = <T>(
  selector: (state: any) => T[],
  statsConfig: {
    groupBy?: string;
    countBy?: string;
    sumBy?: string;
    avgBy?: string;
    cacheKey?: string;
  } = {}
) => {
  const data = useAppState(selector, {
    cacheKey: statsConfig.cacheKey || 'stats'
  });

  const stats = useMemo(() => {
    if (!data || !Array.isArray(data)) {
      return {
        total: 0,
        groups: {},
        counts: {},
        sums: {},
        averages: {}
      };
    }

    const result = {
      total: data.length,
      groups: {} as Record<string, T[]>,
      counts: {} as Record<string, number>,
      sums: {} as Record<string, number>,
      averages: {} as Record<string, number>
    };

    // Agrupamento
    if (statsConfig.groupBy) {
      data.forEach(item => {
        const groupValue = item[statsConfig.groupBy!];
        if (!result.groups[groupValue]) {
          result.groups[groupValue] = [];
        }
        result.groups[groupValue].push(item);
      });
    }

    // Contagem
    if (statsConfig.countBy) {
      data.forEach(item => {
        const countValue = item[statsConfig.countBy!];
        result.counts[countValue] = (result.counts[countValue] || 0) + 1;
      });
    }

    // Soma
    if (statsConfig.sumBy) {
      data.forEach(item => {
        const sumValue = item[statsConfig.sumBy!];
        if (typeof sumValue === 'number') {
          result.sums[statsConfig.sumBy!] = (result.sums[statsConfig.sumBy!] || 0) + sumValue;
        }
      });
    }

    // Média
    if (statsConfig.avgBy) {
      const sum = data.reduce((acc, item) => {
        const avgValue = item[statsConfig.avgBy!];
        return acc + (typeof avgValue === 'number' ? avgValue : 0);
      }, 0);
      result.averages[statsConfig.avgBy!] = data.length > 0 ? sum / data.length : 0;
    }

    return result;
  }, [data, statsConfig]);

  return stats;
};

// Hook para cache inteligente
export const useAppCache = <T>(
  key: string,
  fetcher: () => Promise<T>,
  options: {
    ttl?: number;
    dependencies?: any[];
    enabled?: boolean;
  } = {}
) => {
  const { actions } = useAppStore();
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);
  
  const {
    ttl = 5 * 60 * 1000,
    dependencies = [],
    enabled = true
  } = options;

  // Obter dados do cache
  const cachedData = useAppState(
    (state) => state.cache.queries[key],
    { cacheKey: key }
  );

  // Verificar se cache é válido
  const isCacheValid = useMemo(() => {
    if (!cachedData) return false;
    
    const lastUpdated = actions.state.cache.lastUpdated[key];
    if (!lastUpdated) return false;
    
    const now = Date.now();
    const cacheAge = now - new Date(lastUpdated).getTime();
    return cacheAge < ttl;
  }, [cachedData, key, ttl, actions.state.cache.lastUpdated]);

  // Função para buscar dados
  const refetch = useCallback(async () => {
    if (!enabled) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetcher();
      actions.setCache(key, data, ttl);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [key, fetcher, ttl, enabled, actions]);

  // Buscar dados automaticamente se cache não for válido
  useEffect(() => {
    if (!isCacheValid && enabled) {
      refetch();
    }
  }, [isCacheValid, enabled, refetch, ...dependencies]);

  // Limpar cache
  const clearCache = useCallback(() => {
    actions.clearCache(key);
  }, [key, actions]);

  return {
    data: cachedData,
    isLoading,
    error,
    refetch,
    clearCache,
    isCacheValid
  };
};

// Hook para otimização de re-renders
export const useAppMemo = <T>(
  selector: (state: any) => T,
  deps: any[] = [],
  options: SelectorOptions = {}
) => {
  const data = useAppState(selector, options);
  
  return useMemo(() => data, [data, ...deps]);
};

// Hook para debounce de seletores
export const useAppDebounce = <T>(
  selector: (state: any) => T,
  delay: number = 300,
  options: SelectorOptions = {}
) => {
  const [debouncedValue, setDebouncedValue] = React.useState<T | undefined>();
  const data = useAppState(selector, options);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(data);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [data, delay]);

  return debouncedValue;
};

// Hook para throttle de seletores
export const useAppThrottle = <T>(
  selector: (state: any) => T,
  limit: number = 1000,
  options: SelectorOptions = {}
) => {
  const [throttledValue, setThrottledValue] = React.useState<T | undefined>();
  const data = useAppState(selector, options);
  const lastRun = useRef(Date.now());

  useEffect(() => {
    const now = Date.now();
    if (now - lastRun.current >= limit) {
      setThrottledValue(data);
      lastRun.current = now;
    }
  }, [data, limit]);

  return throttledValue;
};

// Hook para comparação de valores anteriores
export const useAppPrevious = <T>(
  selector: (state: any) => T,
  options: SelectorOptions = {}
) => {
  const data = useAppState(selector, options);
  const prevRef = useRef<T>();

  useEffect(() => {
    prevRef.current = data;
  });

  return prevRef.current;
};

// Hook para detecção de mudanças
export const useAppChanged = <T>(
  selector: (state: any) => T,
  options: SelectorOptions = {}
) => {
  const data = useAppState(selector, options);
  const prevData = useAppPrevious(selector, options);

  return useMemo(() => ({
    current: data,
    previous: prevData,
    hasChanged: data !== prevData,
    isFirstRender: prevData === undefined
  }), [data, prevData]);
};

export default {
  useAppState,
  useAppData,
  useAppList,
  useAppRelated,
  useAppStats,
  useAppCache,
  useAppMemo,
  useAppDebounce,
  useAppThrottle,
  useAppPrevious,
  useAppChanged
}; 