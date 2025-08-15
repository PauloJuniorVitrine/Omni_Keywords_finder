/**
 * api-store.ts
 * 
 * Store para gerenciamento de estado da API
 * 
 * Tracing ID: STORE-API-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 4.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Cache inteligente com TTL
 * - Loading states por endpoint
 * - Otimistic updates
 * - Background sync
 * - Cache invalidation
 * - Memory management
 * - Persistência seletiva
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { ApiResponse, ApiError } from '../shared/types/api';

// Tipos
interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  etag?: string;
  lastModified?: string;
}

interface LoadingState {
  isLoading: boolean;
  isRefetching: boolean;
  isMutating: boolean;
  error: ApiError | null;
  retryCount: number;
  lastAttempt: number;
}

interface ApiState {
  // Cache
  cache: Map<string, CacheEntry>;
  
  // Loading states
  loadingStates: Map<string, LoadingState>;
  
  // Background sync
  backgroundSync: Set<string>;
  
  // Cache metadata
  cacheStats: {
    hits: number;
    misses: number;
    size: number;
    lastCleanup: number;
  };
  
  // Actions
  setCache: <T>(key: string, data: T, ttl?: number, etag?: string) => void;
  getCache: <T>(key: string) => T | null;
  invalidateCache: (pattern?: string) => void;
  clearCache: () => void;
  
  setLoadingState: (key: string, state: Partial<LoadingState>) => void;
  getLoadingState: (key: string) => LoadingState;
  clearLoadingState: (key: string) => void;
  
  addBackgroundSync: (key: string) => void;
  removeBackgroundSync: (key: string) => void;
  getBackgroundSync: () => string[];
  
  updateCacheStats: (hit: boolean) => void;
  cleanupCache: () => void;
  
  // Computed
  isCached: (key: string) => boolean;
  isExpired: (key: string) => boolean;
  getCacheSize: () => number;
  getCacheHitRate: () => number;
}

// Configurações
const CACHE_CONFIG = {
  DEFAULT_TTL: 5 * 60 * 1000, // 5 minutos
  MAX_CACHE_SIZE: 100,
  CLEANUP_INTERVAL: 10 * 60 * 1000, // 10 minutos
  BACKGROUND_SYNC_INTERVAL: 30 * 1000, // 30 segundos
};

// Estado inicial
const initialState = {
  cache: new Map<string, CacheEntry>(),
  loadingStates: new Map<string, LoadingState>(),
  backgroundSync: new Set<string>(),
  cacheStats: {
    hits: 0,
    misses: 0,
    size: 0,
    lastCleanup: Date.now(),
  },
};

// Função para gerar chave de cache
const generateCacheKey = (endpoint: string, params?: Record<string, any>): string => {
  if (!params) return endpoint;
  return `${endpoint}?${JSON.stringify(params)}`;
};

// Função para verificar se cache expirou
const isCacheExpired = (entry: CacheEntry): boolean => {
  return Date.now() - entry.timestamp > entry.ttl;
};

// Função para limpar cache expirado
const cleanupExpiredCache = (cache: Map<string, CacheEntry>): void => {
  const now = Date.now();
  for (const [key, entry] of cache.entries()) {
    if (now - entry.timestamp > entry.ttl) {
      cache.delete(key);
    }
  }
};

// Função para limitar tamanho do cache
const limitCacheSize = (cache: Map<string, CacheEntry>, maxSize: number): void => {
  if (cache.size <= maxSize) return;

  const entries = Array.from(cache.entries());
  entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
  
  const toDelete = entries.slice(0, cache.size - maxSize);
  toDelete.forEach(([key]) => cache.delete(key));
};

export const useApiStore = create<ApiState>()(
  devtools(
    subscribeWithSelector(
      persist(
        (set, get) => ({
          ...initialState,

          // Cache actions
          setCache: <T>(key: string, data: T, ttl = CACHE_CONFIG.DEFAULT_TTL, etag?: string) => {
            set((state) => {
              const newCache = new Map(state.cache);
              newCache.set(key, {
                data,
                timestamp: Date.now(),
                ttl,
                etag,
                lastModified: new Date().toISOString(),
              });

              // Limitar tamanho do cache
              limitCacheSize(newCache, CACHE_CONFIG.MAX_CACHE_SIZE);

              return {
                cache: newCache,
                cacheStats: {
                  ...state.cacheStats,
                  size: newCache.size,
                },
              };
            });
          },

          getCache: <T>(key: string): T | null => {
            const state = get();
            const entry = state.cache.get(key);

            if (!entry) {
              state.updateCacheStats(false);
              return null;
            }

            if (isCacheExpired(entry)) {
              state.cache.delete(key);
              state.updateCacheStats(false);
              return null;
            }

            state.updateCacheStats(true);
            return entry.data as T;
          },

          invalidateCache: (pattern?: string) => {
            set((state) => {
              const newCache = new Map(state.cache);

              if (pattern) {
                // Invalidar por padrão (regex ou wildcard)
                const regex = new RegExp(pattern.replace(/\*/g, '.*'));
                for (const [key] of newCache.entries()) {
                  if (regex.test(key)) {
                    newCache.delete(key);
                  }
                }
              } else {
                // Limpar todo o cache
                newCache.clear();
              }

              return {
                cache: newCache,
                cacheStats: {
                  ...state.cacheStats,
                  size: newCache.size,
                },
              };
            });
          },

          clearCache: () => {
            set((state) => ({
              cache: new Map(),
              cacheStats: {
                ...state.cacheStats,
                size: 0,
              },
            }));
          },

          // Loading states actions
          setLoadingState: (key: string, state: Partial<LoadingState>) => {
            set((currentState) => {
              const newLoadingStates = new Map(currentState.loadingStates);
              const currentLoadingState = newLoadingStates.get(key) || {
                isLoading: false,
                isRefetching: false,
                isMutating: false,
                error: null,
                retryCount: 0,
                lastAttempt: 0,
              };

              newLoadingStates.set(key, {
                ...currentLoadingState,
                ...state,
                lastAttempt: state.isLoading || state.isRefetching || state.isMutating 
                  ? Date.now() 
                  : currentLoadingState.lastAttempt,
              });

              return { loadingStates: newLoadingStates };
            });
          },

          getLoadingState: (key: string): LoadingState => {
            const state = get();
            return state.loadingStates.get(key) || {
              isLoading: false,
              isRefetching: false,
              isMutating: false,
              error: null,
              retryCount: 0,
              lastAttempt: 0,
            };
          },

          clearLoadingState: (key: string) => {
            set((state) => {
              const newLoadingStates = new Map(state.loadingStates);
              newLoadingStates.delete(key);
              return { loadingStates: newLoadingStates };
            });
          },

          // Background sync actions
          addBackgroundSync: (key: string) => {
            set((state) => {
              const newBackgroundSync = new Set(state.backgroundSync);
              newBackgroundSync.add(key);
              return { backgroundSync: newBackgroundSync };
            });
          },

          removeBackgroundSync: (key: string) => {
            set((state) => {
              const newBackgroundSync = new Set(state.backgroundSync);
              newBackgroundSync.delete(key);
              return { backgroundSync: newBackgroundSync };
            });
          },

          getBackgroundSync: (): string[] => {
            const state = get();
            return Array.from(state.backgroundSync);
          },

          // Cache stats actions
          updateCacheStats: (hit: boolean) => {
            set((state) => ({
              cacheStats: {
                ...state.cacheStats,
                hits: state.cacheStats.hits + (hit ? 1 : 0),
                misses: state.cacheStats.misses + (hit ? 0 : 1),
              },
            }));
          },

          cleanupCache: () => {
            set((state) => {
              const newCache = new Map(state.cache);
              cleanupExpiredCache(newCache);
              limitCacheSize(newCache, CACHE_CONFIG.MAX_CACHE_SIZE);

              return {
                cache: newCache,
                cacheStats: {
                  ...state.cacheStats,
                  size: newCache.size,
                  lastCleanup: Date.now(),
                },
              };
            });
          },

          // Computed getters
          isCached: (key: string): boolean => {
            const state = get();
            const entry = state.cache.get(key);
            return entry ? !isCacheExpired(entry) : false;
          },

          isExpired: (key: string): boolean => {
            const state = get();
            const entry = state.cache.get(key);
            return entry ? isCacheExpired(entry) : true;
          },

          getCacheSize: (): number => {
            const state = get();
            return state.cache.size;
          },

          getCacheHitRate: (): number => {
            const state = get();
            const total = state.cacheStats.hits + state.cacheStats.misses;
            return total > 0 ? state.cacheStats.hits / total : 0;
          },
        }),
        {
          name: 'api-store',
          storage: createJSONStorage(() => localStorage),
          partialize: (state) => ({
            cache: Array.from(state.cache.entries()),
            cacheStats: state.cacheStats,
          }),
          onRehydrateStorage: () => (state) => {
            if (state) {
              // Converter array de volta para Map
              state.cache = new Map(state.cache as any);
              state.loadingStates = new Map();
              state.backgroundSync = new Set();
              
              // Limpar cache expirado na rehydratação
              state.cleanupCache();
            }
          },
        }
      )
    ),
    {
      name: 'api-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Hooks utilitários
export const useCache = () => {
  const store = useApiStore();
  
  return {
    setCache: store.setCache,
    getCache: store.getCache,
    invalidateCache: store.invalidateCache,
    clearCache: store.clearCache,
    isCached: store.isCached,
    isExpired: store.isExpired,
    getCacheSize: store.getCacheSize,
    getCacheHitRate: store.getCacheHitRate,
  };
};

export const useLoadingState = (key: string) => {
  const store = useApiStore();
  
  return {
    loadingState: store.getLoadingState(key),
    setLoadingState: (state: Partial<LoadingState>) => store.setLoadingState(key, state),
    clearLoadingState: () => store.clearLoadingState(key),
  };
};

export const useBackgroundSync = () => {
  const store = useApiStore();
  
  return {
    backgroundSync: store.getBackgroundSync(),
    addBackgroundSync: store.addBackgroundSync,
    removeBackgroundSync: store.removeBackgroundSync,
  };
};

export const useCacheStats = () => {
  const store = useApiStore();
  
  return {
    hits: store.cacheStats.hits,
    misses: store.cacheStats.misses,
    size: store.cacheStats.size,
    hitRate: store.getCacheHitRate(),
    lastCleanup: store.cacheStats.lastCleanup,
  };
};

// Auto-cleanup
if (typeof window !== 'undefined') {
  setInterval(() => {
    useApiStore.getState().cleanupCache();
  }, CACHE_CONFIG.CLEANUP_INTERVAL);
}

export default useApiStore; 