/**
 * Hook de Otimização de Queries - Omni Keywords Finder
 * 
 * Este hook implementa otimizações avançadas de performance para queries:
 * - Query deduplication
 * - Background refetching
 * - Optimistic updates
 * - Cache inteligente
 * - Debouncing de requests
 * - Retry logic com backoff
 * 
 * Autor: Sistema Omni Keywords Finder
 * Data: 2024-12-19
 * Versão: 1.0.0
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';

// Tipos para o sistema de otimização
interface QueryConfig<T> {
  key: string;
  fetcher: () => Promise<T>;
  staleTime?: number; // Tempo em ms antes de considerar dados stale
  cacheTime?: number; // Tempo em ms para manter no cache
  retryCount?: number; // Número de tentativas em caso de falha
  retryDelay?: number; // Delay entre tentativas em ms
  backgroundRefetch?: boolean; // Se deve fazer refetch em background
  optimisticUpdate?: boolean; // Se deve usar optimistic updates
  deduplication?: boolean; // Se deve deduplicar queries idênticas
  debounceTime?: number; // Tempo de debounce em ms
}

interface QueryState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  isStale: boolean;
  lastFetched: number | null;
  retryCount: number;
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  staleTime: number;
  cacheTime: number;
  subscribers: Set<(data: T) => void>;
}

// Cache global para queries
const queryCache = new Map<string, CacheEntry<any>>();

// Cache para queries em andamento (deduplication)
const pendingQueries = new Map<string, Promise<any>>();

// Configurações padrão
const DEFAULT_CONFIG = {
  staleTime: 5 * 60 * 1000, // 5 minutos
  cacheTime: 10 * 60 * 1000, // 10 minutos
  retryCount: 3,
  retryDelay: 1000,
  backgroundRefetch: true,
  optimisticUpdate: false,
  deduplication: true,
  debounceTime: 300,
};

// Utilitários
const isStale = (timestamp: number, staleTime: number): boolean => {
  return Date.now() - timestamp > staleTime;
};

const shouldCache = (timestamp: number, cacheTime: number): boolean => {
  return Date.now() - timestamp < cacheTime;
};

const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

const exponentialBackoff = (attempt: number, baseDelay: number): number => {
  return Math.min(baseDelay * Math.pow(2, attempt), 30000); // Max 30s
};

/**
 * Hook principal para otimização de queries
 */
export function useOptimizedQuery<T>(
  config: QueryConfig<T>
): [T | null, boolean, Error | null, () => Promise<void>] {
  const {
    key,
    fetcher,
    staleTime = DEFAULT_CONFIG.staleTime,
    cacheTime = DEFAULT_CONFIG.cacheTime,
    retryCount = DEFAULT_CONFIG.retryCount,
    retryDelay = DEFAULT_CONFIG.retryDelay,
    backgroundRefetch = DEFAULT_CONFIG.backgroundRefetch,
    optimisticUpdate = DEFAULT_CONFIG.optimisticUpdate,
    deduplication = DEFAULT_CONFIG.deduplication,
    debounceTime = DEFAULT_CONFIG.debounceTime,
  } = config;

  // Estado local
  const [state, setState] = useState<QueryState<T>>({
    data: null,
    loading: false,
    error: null,
    isStale: false,
    lastFetched: null,
    retryCount: 0,
  });

  // Refs para controle
  const abortControllerRef = useRef<AbortController | null>(null);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const backgroundRefetchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Função para executar a query com retry logic
  const executeQuery = useCallback(async (): Promise<T> => {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retryCount; attempt++) {
      try {
        // Cancela query anterior se existir
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }

        // Cria novo AbortController
        abortControllerRef.current = new AbortController();

        // Verifica se já existe uma query pendente (deduplication)
        if (deduplication && pendingQueries.has(key)) {
          return await pendingQueries.get(key)!;
        }

        // Executa a query
        const queryPromise = fetcher();
        
        if (deduplication) {
          pendingQueries.set(key, queryPromise);
        }

        const result = await queryPromise;

        // Remove da lista de pendentes
        if (deduplication) {
          pendingQueries.delete(key);
        }

        return result;

      } catch (error) {
        lastError = error as Error;

        // Se foi cancelado, não tenta novamente
        if (error instanceof Error && error.name === 'AbortError') {
          throw error;
        }

        // Se não é a última tentativa, aguarda antes de tentar novamente
        if (attempt < retryCount) {
          const delay = exponentialBackoff(attempt, retryDelay);
          await sleep(delay);
        }
      }
    }

    throw lastError || new Error('Query failed after all retries');
  }, [key, fetcher, retryCount, retryDelay, deduplication]);

  // Função para atualizar o cache
  const updateCache = useCallback((data: T) => {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      staleTime,
      cacheTime,
      subscribers: new Set(),
    };

    queryCache.set(key, entry);

    // Notifica todos os subscribers
    entry.subscribers.forEach(subscriber => subscriber(data));
  }, [key, staleTime, cacheTime]);

  // Função para buscar dados do cache
  const getFromCache = useCallback((): T | null => {
    const entry = queryCache.get(key) as CacheEntry<T> | undefined;
    
    if (!entry) return null;

    // Verifica se ainda está no cache
    if (!shouldCache(entry.timestamp, entry.cacheTime)) {
      queryCache.delete(key);
      return null;
    }

    return entry.data;
  }, [key]);

  // Função principal para refetch
  const refetch = useCallback(async (): Promise<void> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const data = await executeQuery();
      
      setState(prev => ({
        ...prev,
        data,
        loading: false,
        error: null,
        isStale: false,
        lastFetched: Date.now(),
        retryCount: 0,
      }));

      updateCache(data);

    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error as Error,
        retryCount: prev.retryCount + 1,
      }));

      // Mostra erro apenas se não for cancelamento
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error(`Erro ao carregar dados: ${error.message}`);
      }
    }
  }, [executeQuery, updateCache]);

  // Função para refetch em background
  const backgroundRefetchData = useCallback(async () => {
    try {
      const data = await executeQuery();
      
      setState(prev => ({
        ...prev,
        data,
        isStale: false,
        lastFetched: Date.now(),
      }));

      updateCache(data);

    } catch (error) {
      // Em background, apenas loga o erro
      console.warn('Background refetch failed:', error);
    }
  }, [executeQuery, updateCache]);

  // Função para optimistic update
  const optimisticUpdateData = useCallback((updater: (data: T) => T) => {
    if (!optimisticUpdate || !state.data) return;

    const optimisticData = updater(state.data);
    
    setState(prev => ({
      ...prev,
      data: optimisticData,
    }));

    updateCache(optimisticData);
  }, [optimisticUpdate, state.data, updateCache]);

  // Função debounced para refetch
  const debouncedRefetch = useCallback(() => {
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    debounceTimeoutRef.current = setTimeout(() => {
      refetch();
    }, debounceTime);
  }, [refetch, debounceTime]);

  // Inicialização e cache
  useEffect(() => {
    // Busca dados do cache primeiro
    const cachedData = getFromCache();
    
    if (cachedData) {
      setState(prev => ({
        ...prev,
        data: cachedData,
        isStale: isStale(Date.now(), staleTime),
        lastFetched: Date.now(),
      }));

      // Se os dados estão stale e background refetch está habilitado
      if (isStale(Date.now(), staleTime) && backgroundRefetch) {
        backgroundRefetchData();
      }
    } else {
      // Se não há cache, faz fetch inicial
      refetch();
    }

    // Cleanup
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      if (backgroundRefetchTimeoutRef.current) {
        clearTimeout(backgroundRefetchTimeoutRef.current);
      }
    };
  }, [key]); // Executa apenas quando a key muda

  // Background refetch quando dados ficam stale
  useEffect(() => {
    if (!backgroundRefetch || !state.data || !state.lastFetched) return;

    const checkStale = () => {
      if (isStale(state.lastFetched!, staleTime)) {
        setState(prev => ({ ...prev, isStale: true }));
        backgroundRefetchData();
      }
    };

    const interval = setInterval(checkStale, 1000); // Verifica a cada segundo

    return () => clearInterval(interval);
  }, [backgroundRefetch, state.data, state.lastFetched, staleTime, backgroundRefetchData]);

  // Subscribe ao cache
  useEffect(() => {
    const entry = queryCache.get(key) as CacheEntry<T> | undefined;
    
    if (entry) {
      const subscriber = (data: T) => {
        setState(prev => ({ ...prev, data }));
      };
      
      entry.subscribers.add(subscriber);
      
      return () => {
        entry.subscribers.delete(subscriber);
      };
    }
  }, [key]);

  return [state.data, state.loading, state.error, refetch];
}

/**
 * Hook para infinite scrolling otimizado
 */
export function useInfiniteScroll<T>(
  config: QueryConfig<T[]> & {
    pageSize: number;
    hasMore: (data: T[]) => boolean;
  }
) {
  const [page, setPage] = useState(1);
  const [allData, setAllData] = useState<T[]>([]);
  const [hasMore, setHasMore] = useState(true);

  const { key, fetcher, pageSize, hasMore: hasMoreFn, ...queryConfig } = config;

  // Query para dados paginados
  const [data, loading, error, refetch] = useOptimizedQuery<T[]>({
    ...queryConfig,
    key: `${key}_page_${page}`,
    fetcher: () => fetcher(),
  });

  // Atualiza dados quando nova página é carregada
  useEffect(() => {
    if (data) {
      setAllData(prev => {
        const newData = [...prev, ...data];
        setHasMore(hasMoreFn(newData));
        return newData;
      });
    }
  }, [data, hasMoreFn]);

  // Função para carregar próxima página
  const loadMore = useCallback(() => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
    }
  }, [loading, hasMore]);

  // Função para resetar
  const reset = useCallback(() => {
    setPage(1);
    setAllData([]);
    setHasMore(true);
  }, []);

  return {
    data: allData,
    loading,
    error,
    hasMore,
    loadMore,
    reset,
    refetch,
  };
}

/**
 * Hook para lazy loading de componentes
 */
export function useLazyLoad<T>(
  config: QueryConfig<T> & {
    threshold?: number; // Distância do viewport para carregar
  }
) {
  const [isVisible, setIsVisible] = useState(false);
  const [shouldLoad, setShouldLoad] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const { threshold = 100, ...queryConfig } = config;

  // Query otimizada
  const [data, loading, error, refetch] = useOptimizedQuery<T>({
    ...queryConfig,
    key: `${queryConfig.key}_lazy`,
  });

  // Intersection Observer para detectar visibilidade
  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
        
        if (entry.isIntersecting && !shouldLoad) {
          setShouldLoad(true);
        }
      },
      {
        rootMargin: `${threshold}px`,
      }
    );

    observer.observe(element);

    return () => observer.disconnect();
  }, [threshold, shouldLoad]);

  return {
    data: shouldLoad ? data : null,
    loading: shouldLoad ? loading : false,
    error: shouldLoad ? error : null,
    refetch: shouldLoad ? refetch : () => Promise.resolve(),
    elementRef,
    isVisible,
  };
}

/**
 * Hook para debounced queries
 */
export function useDebouncedQuery<T>(
  config: QueryConfig<T> & {
    debounceTime: number;
  }
) {
  const [debouncedKey, setDebouncedKey] = useState(config.key);

  const debouncedConfig = useMemo(() => ({
    ...config,
    key: debouncedKey,
  }), [config, debouncedKey]);

  const [data, loading, error, refetch] = useOptimizedQuery<T>(debouncedConfig);

  const setQueryKey = useCallback((newKey: string) => {
    setDebouncedKey(newKey);
  }, []);

  return {
    data,
    loading,
    error,
    refetch,
    setQueryKey,
  };
}

/**
 * Hook para queries com cache persistente
 */
export function usePersistentQuery<T>(
  config: QueryConfig<T> & {
    storageKey: string;
    storage: 'localStorage' | 'sessionStorage';
  }
) {
  const { storageKey, storage, ...queryConfig } = config;

  // Carrega dados do storage
  const loadFromStorage = useCallback((): T | null => {
    try {
      const stored = window[storage].getItem(storageKey);
      if (stored) {
        const { data, timestamp } = JSON.parse(stored);
        
        // Verifica se ainda é válido
        if (Date.now() - timestamp < (queryConfig.cacheTime || DEFAULT_CONFIG.cacheTime)) {
          return data;
        }
      }
    } catch (error) {
      console.warn('Failed to load from storage:', error);
    }
    return null;
  }, [storageKey, storage, queryConfig.cacheTime]);

  // Salva dados no storage
  const saveToStorage = useCallback((data: T) => {
    try {
      const toStore = {
        data,
        timestamp: Date.now(),
      };
      window[storage].setItem(storageKey, JSON.stringify(toStore));
    } catch (error) {
      console.warn('Failed to save to storage:', error);
    }
  }, [storageKey, storage]);

  // Query otimizada com persistência
  const [data, loading, error, refetch] = useOptimizedQuery<T>({
    ...queryConfig,
    key: `${queryConfig.key}_persistent`,
  });

  // Carrega dados do storage na inicialização
  useEffect(() => {
    const storedData = loadFromStorage();
    if (storedData && !data) {
      // Atualiza o cache com dados do storage
      const entry: CacheEntry<T> = {
        data: storedData,
        timestamp: Date.now(),
        staleTime: queryConfig.staleTime || DEFAULT_CONFIG.staleTime,
        cacheTime: queryConfig.cacheTime || DEFAULT_CONFIG.cacheTime,
        subscribers: new Set(),
      };
      queryCache.set(queryConfig.key, entry);
    }
  }, []);

  // Salva dados no storage quando mudam
  useEffect(() => {
    if (data) {
      saveToStorage(data);
    }
  }, [data, saveToStorage]);

  return [data, loading, error, refetch];
}

/**
 * Hook para queries com prefetch
 */
export function usePrefetchQuery<T>(config: QueryConfig<T>) {
  const prefetch = useCallback(async () => {
    try {
      const data = await config.fetcher();
      const entry: CacheEntry<T> = {
        data,
        timestamp: Date.now(),
        staleTime: config.staleTime || DEFAULT_CONFIG.staleTime,
        cacheTime: config.cacheTime || DEFAULT_CONFIG.cacheTime,
        subscribers: new Set(),
      };
      queryCache.set(config.key, entry);
      return data;
    } catch (error) {
      console.warn('Prefetch failed:', error);
      throw error;
    }
  }, [config]);

  return { prefetch };
}

/**
 * Utilitário para limpar cache
 */
export const clearQueryCache = (key?: string) => {
  if (key) {
    queryCache.delete(key);
    pendingQueries.delete(key);
  } else {
    queryCache.clear();
    pendingQueries.clear();
  }
};

/**
 * Utilitário para obter estatísticas do cache
 */
export const getCacheStats = () => {
  return {
    cacheSize: queryCache.size,
    pendingQueries: pendingQueries.size,
    totalEntries: Array.from(queryCache.values()).reduce(
      (acc, entry) => acc + entry.subscribers.size,
      0
    ),
  };
};

// Exporta tipos para uso externo
export type { QueryConfig, QueryState };

/**
 * Hook para otimização de componentes React
 */
export function useComponentOptimization<T extends Record<string, any>>(
  props: T,
  dependencies: (keyof T)[]
) {
  // Memoiza props baseado nas dependências especificadas
  const memoizedProps = useMemo(() => {
    const memoized: Partial<T> = {};
    dependencies.forEach(key => {
      memoized[key] = props[key];
    });
    return memoized;
  }, dependencies.map(key => props[key]));

  // Verifica se props mudaram
  const hasChanged = useCallback((newProps: T) => {
    return dependencies.some(key => props[key] !== newProps[key]);
  }, [props, dependencies]);

  return {
    memoizedProps,
    hasChanged,
  };
}

/**
 * Hook para lazy loading de imagens
 */
export function useLazyImage(
  src: string,
  placeholder?: string
) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = new Image();
    
    img.onload = () => setIsLoaded(true);
    img.onerror = () => setError(true);
    
    img.src = src;
    
    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [src]);

  return {
    isLoaded,
    error,
    imgRef,
    src: isLoaded ? src : placeholder || src,
  };
}

/**
 * Hook para debounce de valores
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Hook para throttle de funções
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastRun = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  return useCallback((...args: Parameters<T>) => {
    const now = Date.now();

    if (now - lastRun.current >= delay) {
      callback(...args);
      lastRun.current = now;
    } else {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        callback(...args);
        lastRun.current = Date.now();
      }, delay - (now - lastRun.current));
    }
  }, [callback, delay]) as T;
}

/**
 * Hook para virtualização de listas grandes
 */
export function useVirtualization<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) {
  const [scrollTop, setScrollTop] = useState(0);
  
  const totalHeight = items.length * itemHeight;
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );
  
  const visibleItems = items.slice(startIndex, endIndex + 1);
  const offsetY = startIndex * itemHeight;
  
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(event.currentTarget.scrollTop);
  }, []);
  
  return {
    visibleItems,
    offsetY,
    totalHeight,
    handleScroll,
    startIndex,
    endIndex,
  };
} 