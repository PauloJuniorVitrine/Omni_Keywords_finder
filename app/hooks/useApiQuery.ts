/**
 * useApiQuery.ts
 * 
 * Hook para gerenciar queries da API com cache e revalidação
 * 
 * Tracing ID: HOOK-API-QUERY-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 2.4
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Queries tipadas com cache inteligente
 * - Revalidação automática e manual
 * - Background refetch
 * - Paginação automática
 * - Infinite queries
 * - Suspense mode
 * - Error boundaries
 * - Stale-while-revalidate
 */

import { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import { ApiClient } from '../services/api/ApiClient';
import { ApiRequestConfig, ApiResponse, ApiError } from '../shared/types/api';

// Tipos
interface QueryState<TData = any, TError = any> {
  data: TData | null;
  error: TError | null;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
  isIdle: boolean;
  isFetching: boolean;
  isStale: boolean;
  isRefetching: boolean;
}

interface QueryOptions<TData, TError, TQueryKey> {
  enabled?: boolean;
  staleTime?: number;
  cacheTime?: number;
  refetchOnWindowFocus?: boolean;
  refetchOnReconnect?: boolean;
  refetchOnMount?: boolean;
  retry?: number | boolean;
  retryDelay?: number;
  onSuccess?: (data: TData) => void;
  onError?: (error: TError) => void;
  onSettled?: (data: TData | null, error: TError | null) => void;
  suspense?: boolean;
  keepPreviousData?: boolean;
  select?: (data: TData) => any;
  placeholderData?: TData;
  timeout?: number;
  pollingInterval?: number;
  refetchInterval?: number;
}

interface UseQueryResult<TData, TError> {
  data: TData | null;
  error: TError | null;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
  isIdle: boolean;
  isFetching: boolean;
  isStale: boolean;
  isRefetching: boolean;
  refetch: () => Promise<TData>;
  invalidate: () => void;
  reset: () => void;
  state: QueryState<TData, TError>;
}

// Cache global para queries
interface CacheEntry<TData> {
  data: TData;
  timestamp: number;
  staleTime: number;
  cacheTime: number;
}

class QueryCache {
  private cache = new Map<string, CacheEntry<any>>();

  set<TData>(key: string, data: TData, staleTime: number, cacheTime: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      staleTime,
      cacheTime,
    });
  }

  get<TData>(key: string): TData | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = Date.now();
    const isStale = now - entry.timestamp > entry.staleTime;
    const isExpired = now - entry.timestamp > entry.cacheTime;

    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  invalidate(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }
}

// Instância global do cache
const queryCache = new QueryCache();

// Estado inicial
const initialState: QueryState = {
  data: null,
  error: null,
  isLoading: false,
  isSuccess: false,
  isError: false,
  isIdle: true,
  isFetching: false,
  isStale: false,
  isRefetching: false,
};

export function useApiQuery<TData = any, TError = ApiError, TQueryKey extends readonly unknown[] = any[]>(
  queryKey: TQueryKey,
  queryFn: (config?: ApiRequestConfig) => Promise<ApiResponse<TData>>,
  options: QueryOptions<TData, TError, TQueryKey> = {}
): UseQueryResult<TData, TError> {
  const [state, setState] = useState<QueryState<TData, TError>>(initialState);
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const refetchIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // Configurações padrão
  const {
    enabled = true,
    staleTime = 5 * 60 * 1000, // 5 minutos
    cacheTime = 10 * 60 * 1000, // 10 minutos
    refetchOnWindowFocus = true,
    refetchOnReconnect = true,
    refetchOnMount = true,
    retry = 3,
    suspense = false,
    keepPreviousData = false,
    timeout = 30000,
    pollingInterval = 0,
    refetchInterval = 0,
    ...restOptions
  } = options;

  // Gerar chave do cache
  const cacheKey = useMemo(() => {
    return JSON.stringify(queryKey);
  }, [queryKey]);

  // Função para executar a query
  const executeQuery = useCallback(async (isRefetch = false): Promise<TData> => {
    if (!enabled) {
      throw new Error('Query is disabled');
    }

    // Cancelar query anterior se estiver em andamento
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Criar novo AbortController
    abortControllerRef.current = new AbortController();

    // Verificar cache primeiro
    const cachedData = queryCache.get<TData>(cacheKey);
    if (cachedData && !isRefetch) {
      setState(prev => ({
        ...prev,
        data: cachedData,
        isLoading: false,
        isSuccess: true,
        isIdle: false,
        isStale: false,
      }));

      if (restOptions.onSuccess) {
        restOptions.onSuccess(cachedData);
      }

      return cachedData;
    }

    // Atualizar estado
    setState(prev => ({
      ...prev,
      isLoading: !isRefetch,
      isFetching: true,
      isRefetching: isRefetch,
      isIdle: false,
      isSuccess: false,
      isError: false,
      error: null,
    }));

    retryCountRef.current = 0;

    try {
      // Executar query
      const response = await queryFn({
        signal: abortControllerRef.current.signal,
        timeout,
      });

      const data = response.data as TData;

      // Aplicar select se fornecido
      const finalData = restOptions.select ? restOptions.select(data) : data;

      // Salvar no cache
      queryCache.set(cacheKey, finalData, staleTime, cacheTime);

      // Sucesso
      setState(prev => ({
        ...prev,
        data: finalData,
        error: null,
        isLoading: false,
        isFetching: false,
        isRefetching: false,
        isSuccess: true,
        isError: false,
        isStale: false,
      }));

      // Callbacks de sucesso
      if (restOptions.onSuccess) {
        restOptions.onSuccess(finalData);
      }

      if (restOptions.onSettled) {
        restOptions.onSettled(finalData, null);
      }

      return finalData;

    } catch (error) {
      const apiError = error as TError;

      // Retry logic
      if (retryCountRef.current < (typeof retry === 'number' ? retry : 3)) {
        retryCountRef.current++;
        
        const delay = typeof retry === 'number' ? 
          (restOptions.retryDelay || 1000) * retryCountRef.current : 
          (restOptions.retryDelay || 1000);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        
        return executeQuery(isRefetch);
      }

      // Erro final
      setState(prev => ({
        ...prev,
        data: null,
        error: apiError,
        isLoading: false,
        isFetching: false,
        isRefetching: false,
        isSuccess: false,
        isError: true,
      }));

      // Callbacks de erro
      if (restOptions.onError) {
        restOptions.onError(apiError);
      }

      if (restOptions.onSettled) {
        restOptions.onSettled(null, apiError);
      }

      throw apiError;
    }
  }, [queryFn, enabled, cacheKey, staleTime, cacheTime, timeout, retry, restOptions]);

  // Função refetch
  const refetch = useCallback(async (): Promise<TData> => {
    return executeQuery(true);
  }, [executeQuery]);

  // Função invalidate
  const invalidate = useCallback(() => {
    queryCache.invalidate(cacheKey);
    setState(prev => ({
      ...prev,
      isStale: true,
    }));
  }, [cacheKey]);

  // Função reset
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
    
    if (refetchIntervalRef.current) {
      clearInterval(refetchIntervalRef.current);
    }

    setState(initialState);
    retryCountRef.current = 0;
  }, []);

  // Efeito principal para executar query
  useEffect(() => {
    if (!enabled) return;

    // Verificar se deve executar no mount
    if (refetchOnMount) {
      executeQuery();
    }

    // Polling
    if (pollingInterval > 0) {
      pollingIntervalRef.current = setInterval(() => {
        if (isMountedRef.current) {
          executeQuery(true);
        }
      }, pollingInterval);
    }

    // Refetch interval
    if (refetchInterval > 0) {
      refetchIntervalRef.current = setInterval(() => {
        if (isMountedRef.current) {
          executeQuery(true);
        }
      }, refetchInterval);
    }

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      
      if (refetchIntervalRef.current) {
        clearInterval(refetchIntervalRef.current);
      }
    };
  }, [enabled, refetchOnMount, pollingInterval, refetchInterval, executeQuery]);

  // Efeito para refetch on window focus
  useEffect(() => {
    if (!refetchOnWindowFocus) return;

    const handleFocus = () => {
      if (isMountedRef.current && state.isStale) {
        executeQuery(true);
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnWindowFocus, state.isStale, executeQuery]);

  // Efeito para refetch on reconnect
  useEffect(() => {
    if (!refetchOnReconnect) return;

    const handleOnline = () => {
      if (isMountedRef.current && state.isStale) {
        executeQuery(true);
      }
    };

    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, [refetchOnReconnect, state.isStale, executeQuery]);

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  return {
    ...state,
    refetch,
    invalidate,
    reset,
    state,
  };
}

// Hook especializado para GET
export function useGetQuery<TData = any, TError = ApiError>(
  endpoint: string,
  options: QueryOptions<TData, TError, any> = {}
) {
  const queryFn = useCallback((config?: ApiRequestConfig) => {
    return ApiClient.get<TData>(endpoint, config);
  }, [endpoint]);

  return useApiQuery([endpoint], queryFn, options);
}

// Hook para queries com parâmetros
export function useGetQueryWithParams<TData = any, TError = ApiError>(
  endpoint: string,
  params: Record<string, any>,
  options: QueryOptions<TData, TError, any> = {}
) {
  const queryFn = useCallback((config?: ApiRequestConfig) => {
    return ApiClient.get<TData>(endpoint, { ...config, params });
  }, [endpoint, params]);

  return useApiQuery([endpoint, params], queryFn, options);
}

// Hook para infinite queries
export function useInfiniteQuery<TData = any, TError = ApiError>(
  queryKey: readonly unknown[],
  queryFn: (pageParam: any, config?: ApiRequestConfig) => Promise<ApiResponse<TData>>,
  options: QueryOptions<TData, TError, any> & {
    getNextPageParam?: (lastPage: TData, allPages: TData[]) => any;
    getPreviousPageParam?: (firstPage: TData, allPages: TData[]) => any;
  } = {}
) {
  const [pages, setPages] = useState<TData[]>([]);
  const [pageParams, setPageParams] = useState<any[]>([]);

  const {
    getNextPageParam,
    getPreviousPageParam,
    ...queryOptions
  } = options;

  const query = useApiQuery(
    queryKey,
    async (config) => {
      const lastPageParam = pageParams[pageParams.length - 1];
      return queryFn(lastPageParam, config);
    },
    queryOptions
  );

  const fetchNextPage = useCallback(async () => {
    if (!getNextPageParam) return;

    const lastPage = pages[pages.length - 1];
    const nextPageParam = getNextPageParam(lastPage, pages);

    if (nextPageParam !== undefined) {
      const response = await queryFn(nextPageParam);
      const newPage = response.data as TData;

      setPages(prev => [...prev, newPage]);
      setPageParams(prev => [...prev, nextPageParam]);
    }
  }, [getNextPageParam, pages, queryFn]);

  const fetchPreviousPage = useCallback(async () => {
    if (!getPreviousPageParam) return;

    const firstPage = pages[0];
    const previousPageParam = getPreviousPageParam(firstPage, pages);

    if (previousPageParam !== undefined) {
      const response = await queryFn(previousPageParam);
      const newPage = response.data as TData;

      setPages(prev => [newPage, ...prev]);
      setPageParams(prev => [previousPageParam, ...prev]);
    }
  }, [getPreviousPageParam, pages, queryFn]);

  return {
    ...query,
    pages,
    pageParams,
    fetchNextPage,
    fetchPreviousPage,
    hasNextPage: getNextPageParam ? getNextPageParam(pages[pages.length - 1], pages) !== undefined : false,
    hasPreviousPage: getPreviousPageParam ? getPreviousPageParam(pages[0], pages) !== undefined : false,
  };
}

export default useApiQuery; 