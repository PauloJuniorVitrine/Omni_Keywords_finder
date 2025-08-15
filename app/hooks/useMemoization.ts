/**
 * useMemoization - Hook para gerenciar memoização otimizada
 * 
 * Prompt: Implementação de cache e memoização para Criticalidade 3.1.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useMemo, useCallback, useRef, useEffect } from 'react';

interface MemoizationConfig {
  enableProfiling?: boolean;
  maxCacheSize?: number;
  enableLogging?: boolean;
}

interface MemoizationStats {
  memoHits: number;
  memoMisses: number;
  callbackHits: number;
  callbackMisses: number;
  cacheSize: number;
}

class MemoizationManager {
  private cache = new Map<string, { value: any; timestamp: number; deps: any[] }>();
  private stats: MemoizationStats = {
    memoHits: 0,
    memoMisses: 0,
    callbackHits: 0,
    callbackMisses: 0,
    cacheSize: 0
  };
  private config: Required<MemoizationConfig>;

  constructor(config: MemoizationConfig = {}) {
    this.config = {
      enableProfiling: config.enableProfiling || false,
      maxCacheSize: config.maxCacheSize || 1000,
      enableLogging: config.enableLogging || false
    };
  }

  private generateKey(fn: Function, deps: any[]): string {
    return `${fn.name || 'anonymous'}_${JSON.stringify(deps)}`;
  }

  private isEqual(a: any[], b: any[]): boolean {
    if (a.length !== b.length) return false;
    return a.every((val, index) => {
      if (typeof val === 'object' && val !== null) {
        return JSON.stringify(val) === JSON.stringify(b[index]);
      }
      return val === b[index];
    });
  }

  memoize<T>(fn: () => T, deps: any[], key?: string): T {
    const cacheKey = key || this.generateKey(fn, deps);
    const cached = this.cache.get(cacheKey);

    if (cached && this.isEqual(cached.deps, deps)) {
      this.stats.memoHits++;
      if (this.config.enableLogging) {
        console.log(`[Memo] Hit: ${cacheKey}`);
      }
      return cached.value;
    }

    this.stats.memoMisses++;
    if (this.config.enableLogging) {
      console.log(`[Memo] Miss: ${cacheKey}`);
    }

    const result = fn();
    
    // Gerenciar tamanho do cache
    if (this.cache.size >= this.config.maxCacheSize) {
      this.evictOldest();
    }

    this.cache.set(cacheKey, {
      value: result,
      timestamp: Date.now(),
      deps: [...deps]
    });

    this.updateStats();
    return result;
  }

  memoizeCallback<T extends (...args: any[]) => any>(
    fn: T,
    deps: any[],
    key?: string
  ): T {
    const cacheKey = key || this.generateKey(fn, deps);
    const cached = this.cache.get(cacheKey);

    if (cached && this.isEqual(cached.deps, deps)) {
      this.stats.callbackHits++;
      if (this.config.enableLogging) {
        console.log(`[Callback] Hit: ${cacheKey}`);
      }
      return cached.value;
    }

    this.stats.callbackMisses++;
    if (this.config.enableLogging) {
      console.log(`[Callback] Miss: ${cacheKey}`);
    }

    // Gerenciar tamanho do cache
    if (this.cache.size >= this.config.maxCacheSize) {
      this.evictOldest();
    }

    this.cache.set(cacheKey, {
      value: fn,
      timestamp: Date.now(),
      deps: [...deps]
    });

    this.updateStats();
    return fn;
  }

  clear(): void {
    this.cache.clear();
    this.updateStats();
    if (this.config.enableLogging) {
      console.log('[Memoization] Cache cleared');
    }
  }

  getStats(): MemoizationStats {
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
        console.log(`[Memoization] Evicted: ${oldestKey}`);
      }
    }
  }

  private updateStats(): void {
    this.stats.cacheSize = this.cache.size;
  }
}

// Instância global do gerenciador de memoização
const memoizationManager = new MemoizationManager();

// Hook para memoização otimizada
export const useOptimizedMemo = <T>(
  factory: () => T,
  deps: React.DependencyList,
  key?: string
): T => {
  return useMemo(() => {
    return memoizationManager.memoize(factory, deps, key);
  }, deps);
};

// Hook para callback otimizado
export const useOptimizedCallback = <T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList,
  key?: string
): T => {
  return useCallback((...args: Parameters<T>) => {
    const memoizedCallback = memoizationManager.memoizeCallback(callback, deps, key);
    return memoizedCallback(...args);
  }, deps) as T;
};

// Hook para memoização de objetos complexos
export const useObjectMemo = <T extends object>(
  obj: T,
  deps: React.DependencyList
): T => {
  return useOptimizedMemo(() => obj, deps, 'object_memo');
};

// Hook para memoização de arrays
export const useArrayMemo = <T>(
  arr: T[],
  deps: React.DependencyList
): T[] => {
  return useOptimizedMemo(() => arr, deps, 'array_memo');
};

// Hook para memoização de funções de cálculo custoso
export const useExpensiveCalculation = <T>(
  calculation: () => T,
  deps: React.DependencyList,
  key?: string
): T => {
  return useOptimizedMemo(() => {
    if (memoizationManager.config.enableProfiling) {
      const start = performance.now();
      const result = calculation();
      const end = performance.now();
      console.log(`[ExpensiveCalc] ${key || 'anonymous'}: ${end - start}ms`);
      return result;
    }
    return calculation();
  }, deps, key);
};

// Hook para memoização de filtros e ordenação
export const useFilteredData = <T>(
  data: T[],
  filterFn: (item: T) => boolean,
  sortFn?: (a: T, b: T) => number,
  deps: React.DependencyList = []
): T[] => {
  return useOptimizedMemo(() => {
    let filtered = data.filter(filterFn);
    if (sortFn) {
      filtered = filtered.sort(sortFn);
    }
    return filtered;
  }, [data, filterFn, sortFn, ...deps], 'filtered_data');
};

// Hook para memoização de agregações
export const useAggregatedData = <T, R>(
  data: T[],
  aggregator: (items: T[]) => R,
  deps: React.DependencyList = []
): R => {
  return useOptimizedMemo(() => {
    return aggregator(data);
  }, [data, aggregator, ...deps], 'aggregated_data');
};

// Hook para memoização de transformações
export const useTransformedData = <T, R>(
  data: T,
  transformer: (item: T) => R,
  deps: React.DependencyList = []
): R => {
  return useOptimizedMemo(() => {
    return transformer(data);
  }, [data, transformer, ...deps], 'transformed_data');
};

// Hook para profiling de performance
export const usePerformanceProfiler = (componentName: string) => {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(performance.now());

  useEffect(() => {
    renderCount.current++;
    const currentTime = performance.now();
    const timeSinceLastRender = currentTime - lastRenderTime.current;
    
    console.log(`[Profiler] ${componentName}:`, {
      renderCount: renderCount.current,
      timeSinceLastRender: `${timeSinceLastRender.toFixed(2)}ms`
    });
    
    lastRenderTime.current = currentTime;
  });

  return {
    renderCount: renderCount.current,
    resetCount: () => { renderCount.current = 0; }
  };
};

// HOC para memoização automática de componentes
export const withMemoization = <P extends object>(
  Component: React.ComponentType<P>,
  propsAreEqual?: (prevProps: P, nextProps: P) => boolean
) => {
  const MemoizedComponent = React.memo(Component, propsAreEqual);
  
  // Adicionar display name para debugging
  MemoizedComponent.displayName = `withMemoization(${Component.displayName || Component.name})`;
  
  return MemoizedComponent;
};

// Hook para limpeza automática do cache
export const useCacheCleanup = (intervalMs: number = 5 * 60 * 1000) => {
  useEffect(() => {
    const interval = setInterval(() => {
      memoizationManager.clear();
    }, intervalMs);

    return () => clearInterval(interval);
  }, [intervalMs]);
};

export { memoizationManager, MemoizationManager };
export type { MemoizationConfig, MemoizationStats }; 