/**
 * Memoization System for Components
 * 
 * Tracing ID: MEMOIZATION_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.2
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import React, { useMemo, useCallback, useRef, useEffect, useState } from 'react';

// Types for memoization
export interface MemoizationOptions {
  deep?: boolean;
  maxSize?: number;
  ttl?: number; // Time to live in milliseconds
  key?: string;
}

export interface MemoizedValue<T> {
  value: T;
  timestamp: number;
  key: string;
}

// Deep comparison utility
export const deepEqual = (a: any, b: any): boolean => {
  if (a === b) return true;
  
  if (a == null || b == null) return false;
  
  if (typeof a !== typeof b) return false;
  
  if (typeof a !== 'object') return false;
  
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  
  if (Array.isArray(a)) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (!deepEqual(a[i], b[i])) return false;
    }
    return true;
  }
  
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  
  if (keysA.length !== keysB.length) return false;
  
  for (const key of keysA) {
    if (!keysB.includes(key)) return false;
    if (!deepEqual(a[key], b[key])) return false;
  }
  
  return true;
};

// LRU Cache for memoization
export class LRUCache<K, V> {
  private capacity: number;
  private cache: Map<K, V>;
  
  constructor(capacity: number = 100) {
    this.capacity = capacity;
    this.cache = new Map();
  }
  
  get(key: K): V | undefined {
    if (!this.cache.has(key)) return undefined;
    
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }
  
  set(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.capacity) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, value);
  }
  
  clear(): void {
    this.cache.clear();
  }
  
  size(): number {
    return this.cache.size;
  }
}

// Global cache instance
const globalCache = new LRUCache<string, MemoizedValue<any>>(1000);

// Custom hook for memoization with cache
export const useMemoizedValue = <T>(
  factory: () => T,
  deps: React.DependencyList,
  options: MemoizationOptions = {}
): T => {
  const { deep = false, maxSize = 100, ttl, key } = options;
  const cacheKey = key || JSON.stringify(deps);
  const cacheRef = useRef(new LRUCache<string, MemoizedValue<T>>(maxSize));
  
  return useMemo(() => {
    const cached = cacheRef.current.get(cacheKey);
    const now = Date.now();
    
    // Check if cached value is still valid
    if (cached && (!ttl || now - cached.timestamp < ttl)) {
      return cached.value;
    }
    
    // Generate new value
    const newValue = factory();
    cacheRef.current.set(cacheKey, {
      value: newValue,
      timestamp: now,
      key: cacheKey
    });
    
    return newValue;
  }, deps);
};

// Custom hook for memoized callbacks
export const useMemoizedCallback = <T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList,
  options: MemoizationOptions = {}
): T => {
  const { deep = false } = options;
  
  return useCallback((...args: Parameters<T>) => {
    return callback(...args);
  }, deps) as T;
};

// HOC for component memoization
export const withMemoization = <P extends object>(
  Component: React.ComponentType<P>,
  options: MemoizationOptions = {}
) => {
  const { deep = false } = options;
  
  const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
    if (deep) {
      return deepEqual(prevProps, nextProps);
    }
    return true; // Default shallow comparison
  });
  
  MemoizedComponent.displayName = `withMemoization(${Component.displayName || Component.name})`;
  
  return MemoizedComponent;
};

// Hook for expensive computations
export const useExpensiveComputation = <T>(
  computation: () => T,
  deps: React.DependencyList,
  options: MemoizationOptions = {}
): T => {
  const [result, setResult] = useState<T | null>(null);
  const [isComputing, setIsComputing] = useState(false);
  const { ttl, key } = options;
  const cacheKey = key || JSON.stringify(deps);
  
  useEffect(() => {
    const cached = globalCache.get(cacheKey);
    const now = Date.now();
    
    if (cached && (!ttl || now - cached.timestamp < ttl)) {
      setResult(cached.value);
      return;
    }
    
    setIsComputing(true);
    
    // Use requestIdleCallback for non-blocking computation
    const compute = () => {
      try {
        const newResult = computation();
        globalCache.set(cacheKey, {
          value: newResult,
          timestamp: now,
          key: cacheKey
        });
        setResult(newResult);
      } catch (error) {
        console.error('Computation error:', error);
      } finally {
        setIsComputing(false);
      }
    };
    
    if ('requestIdleCallback' in window) {
      (window as any).requestIdleCallback(compute);
    } else {
      setTimeout(compute, 0);
    }
  }, deps);
  
  return result as T;
};

// Hook for memoized selectors (Redux-like)
export const useMemoizedSelector = <TState, TResult>(
  selector: (state: TState) => TResult,
  state: TState,
  options: MemoizationOptions = {}
): TResult => {
  return useMemoizedValue(() => selector(state), [state], options);
};

// Hook for memoized API calls
export const useMemoizedQuery = <T>(
  queryFn: () => Promise<T>,
  deps: React.DependencyList,
  options: MemoizationOptions = {}
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const { ttl, key } = options;
  const cacheKey = key || JSON.stringify(deps);
  
  const executeQuery = useCallback(async () => {
    const cached = globalCache.get(cacheKey);
    const now = Date.now();
    
    if (cached && (!ttl || now - cached.timestamp < ttl)) {
      setData(cached.value);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await queryFn();
      globalCache.set(cacheKey, {
        value: result,
        timestamp: now,
        key: cacheKey
      });
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [queryFn, cacheKey, ttl]);
  
  useEffect(() => {
    executeQuery();
  }, deps);
  
  return { data, loading, error, refetch: executeQuery };
};

// Performance monitoring for memoization
export const useMemoizationMetrics = () => {
  const [metrics, setMetrics] = useState({
    cacheHits: 0,
    cacheMisses: 0,
    totalComputations: 0,
    averageComputationTime: 0,
    cacheSize: 0
  });
  
  const trackCacheHit = () => {
    setMetrics(prev => ({
      ...prev,
      cacheHits: prev.cacheHits + 1
    }));
  };
  
  const trackCacheMiss = (computationTime: number) => {
    setMetrics(prev => ({
      ...prev,
      cacheMisses: prev.cacheMisses + 1,
      totalComputations: prev.totalComputations + 1,
      averageComputationTime: 
        (prev.averageComputationTime * prev.totalComputations + computationTime) / 
        (prev.totalComputations + 1)
    }));
  };
  
  const getCacheHitRate = () => {
    const total = metrics.cacheHits + metrics.cacheMisses;
    return total > 0 ? (metrics.cacheHits / total) * 100 : 0;
  };
  
  return {
    metrics,
    trackCacheHit,
    trackCacheMiss,
    getCacheHitRate
  };
};

// Utility for clearing cache
export const clearMemoizationCache = () => {
  globalCache.clear();
};

// Utility for getting cache statistics
export const getMemoizationStats = () => {
  return {
    cacheSize: globalCache.size(),
    totalEntries: globalCache.size()
  };
};

export default {
  deepEqual,
  LRUCache,
  useMemoizedValue,
  useMemoizedCallback,
  withMemoization,
  useExpensiveComputation,
  useMemoizedSelector,
  useMemoizedQuery,
  useMemoizationMetrics,
  clearMemoizationCache,
  getMemoizationStats
}; 