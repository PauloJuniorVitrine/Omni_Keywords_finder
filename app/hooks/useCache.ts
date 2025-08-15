/**
 * useCache - Hook para gerenciar cache de queries e dados
 * 
 * Prompt: Implementação de cache e memoização para Criticalidade 3.1.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  key: string;
}

interface CacheConfig {
  defaultTTL?: number; // Time to live em milissegundos
  maxSize?: number; // Tamanho máximo do cache
  enableLogging?: boolean;
}

interface CacheStats {
  hits: number;
  misses: number;
  size: number;
  keys: string[];
}

class CacheManager {
  private cache = new Map<string, CacheEntry<any>>();
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    size: 0,
    keys: []
  };
  private config: Required<CacheConfig>;

  constructor(config: CacheConfig = {}) {
    this.config = {
      defaultTTL: config.defaultTTL || 5 * 60 * 1000, // 5 minutos
      maxSize: config.maxSize || 100,
      enableLogging: config.enableLogging || false
    };
  }

  set<T>(key: string, data: T, ttl?: number): void {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.config.defaultTTL,
      key
    };

    // Verificar se excedeu o tamanho máximo
    if (this.cache.size >= this.config.maxSize) {
      this.evictOldest();
    }

    this.cache.set(key, entry);
    this.updateStats();
    
    if (this.config.enableLogging) {
      console.log(`[Cache] Set: ${key}`, { ttl: entry.ttl });
    }
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.stats.misses++;
      if (this.config.enableLogging) {
        console.log(`[Cache] Miss: ${key}`);
      }
      return null;
    }

    // Verificar se expirou
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      this.stats.misses++;
      if (this.config.enableLogging) {
        console.log(`[Cache] Expired: ${key}`);
      }
      return null;
    }

    this.stats.hits++;
    if (this.config.enableLogging) {
      console.log(`[Cache] Hit: ${key}`);
    }
    return entry.data;
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;
    
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return false;
    }
    
    return true;
  }

  delete(key: string): boolean {
    const deleted = this.cache.delete(key);
    if (deleted) {
      this.updateStats();
      if (this.config.enableLogging) {
        console.log(`[Cache] Deleted: ${key}`);
      }
    }
    return deleted;
  }

  clear(): void {
    this.cache.clear();
    this.updateStats();
    if (this.config.enableLogging) {
      console.log('[Cache] Cleared');
    }
  }

  invalidate(pattern: string | RegExp): number {
    let count = 0;
    const keys = Array.from(this.cache.keys());
    
    for (const key of keys) {
      if (typeof pattern === 'string' ? key.includes(pattern) : pattern.test(key)) {
        this.cache.delete(key);
        count++;
      }
    }
    
    this.updateStats();
    if (this.config.enableLogging) {
      console.log(`[Cache] Invalidated ${count} entries with pattern: ${pattern}`);
    }
    
    return count;
  }

  getStats(): CacheStats {
    return { ...this.stats };
  }

  private evictOldest(): void {
    let oldestKey: string | null = null;
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTime) {
        oldestTime = entry.timestamp;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
      if (this.config.enableLogging) {
        console.log(`[Cache] Evicted oldest: ${oldestKey}`);
      }
    }
  }

  private updateStats(): void {
    this.stats.size = this.cache.size;
    this.stats.keys = Array.from(this.cache.keys());
  }
}

// Instância global do cache
const globalCache = new CacheManager();

export const useCache = <T>(
  key: string,
  fetcher: () => Promise<T>,
  options: {
    ttl?: number;
    enabled?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
  } = {}
) => {
  const {
    ttl,
    enabled = true,
    onSuccess,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(async () => {
    if (!enabled) return;

    // Verificar cache primeiro
    const cachedData = globalCache.get<T>(key);
    if (cachedData) {
      setData(cachedData);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Cancelar requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    try {
      const result = await fetcher();
      
      // Armazenar no cache
      globalCache.set(key, result, ttl);
      
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setError(err);
        onError?.(err);
      }
    } finally {
      setIsLoading(false);
    }
  }, [key, fetcher, ttl, enabled, onSuccess, onError]);

  const invalidate = useCallback(() => {
    globalCache.delete(key);
    setData(null);
  }, [key]);

  const refetch = useCallback(() => {
    invalidate();
    fetchData();
  }, [invalidate, fetchData]);

  useEffect(() => {
    fetchData();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    refetch,
    invalidate,
    cacheStats: globalCache.getStats()
  };
};

// Hook para cache de queries específicas
export const useQueryCache = <T>(
  queryKey: string,
  queryFn: () => Promise<T>,
  options: {
    ttl?: number;
    enabled?: boolean;
    staleTime?: number; // Tempo antes de considerar dados stale
  } = {}
) => {
  const { staleTime = 0 } = options;
  
  return useCache(queryKey, queryFn, {
    ...options,
    onSuccess: (data) => {
      // Marcar como fresh
      setTimeout(() => {
        globalCache.invalidate(queryKey);
      }, staleTime);
    }
  });
};

// Hook para cache de dados estáticos
export const useStaticCache = <T>(
  key: string,
  data: T,
  ttl?: number
) => {
  useEffect(() => {
    globalCache.set(key, data, ttl);
  }, [key, data, ttl]);

  return {
    get: () => globalCache.get<T>(key),
    set: (newData: T) => globalCache.set(key, newData, ttl),
    delete: () => globalCache.delete(key),
    has: () => globalCache.has(key)
  };
};

export { globalCache, CacheManager };
export type { CacheConfig, CacheStats }; 