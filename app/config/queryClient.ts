/**
 * Configuração Otimizada do QueryClient
 * 
 * Tracing ID: FIXTYPE-009_QUERY_CLIENT_20250127_001
 * Data: 2025-01-27
 * 
 * Configuração avançada do TanStack Query com:
 * - Cache inteligente com TTL
 * - Invalidação automática
 * - Estratégias de sincronização
 * - Otimizações de performance
 * - Persistência de cache
 */

import { QueryClient } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/react-query-persist-client-core';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

// Configurações de cache por tipo de dados
const CACHE_CONFIGS = {
  // Dados que mudam raramente
  STATIC: {
    staleTime: 30 * 60 * 1000, // 30 minutos
    gcTime: 60 * 60 * 1000, // 1 hora
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  },
  
  // Dados que mudam ocasionalmente
  SEMI_STATIC: {
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 15 * 60 * 1000, // 15 minutos
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  },
  
  // Dados que mudam frequentemente
  DYNAMIC: {
    staleTime: 30 * 1000, // 30 segundos
    gcTime: 5 * 60 * 1000, // 5 minutos
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  },
  
  // Dados em tempo real
  REALTIME: {
    staleTime: 0, // Sempre stale
    gcTime: 2 * 60 * 1000, // 2 minutos
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    refetchInterval: 30 * 1000, // Refetch a cada 30s
  },
  
  // Dados de usuário (sempre atualizados)
  USER: {
    staleTime: 0,
    gcTime: 10 * 60 * 1000, // 10 minutos
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  }
};

// Configuração de retry por tipo de erro
const RETRY_CONFIG = {
  // Erros de rede - retry automático
  network: {
    retry: 3,
    retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
  },
  
  // Erros de servidor - retry limitado
  server: {
    retry: 2,
    retryDelay: (attemptIndex: number) => Math.min(2000 * 2 ** attemptIndex, 10000),
  },
  
  // Erros de validação - sem retry
  validation: {
    retry: false,
  },
  
  // Erros de autenticação - sem retry
  auth: {
    retry: false,
  }
};

// Função para determinar configuração baseada na query key
const getQueryConfig = (queryKey: string[]) => {
  const key = queryKey[0] as string;
  
  // Nichos e categorias - dados semi-estáticos
  if (['nichos', 'categorias'].includes(key)) {
    return CACHE_CONFIGS.SEMI_STATIC;
  }
  
  // Stats e métricas - dados dinâmicos
  if (['stats', 'metrics', 'analytics'].includes(key)) {
    return CACHE_CONFIGS.DYNAMIC;
  }
  
  // Prompts e dados coletados - dados dinâmicos
  if (['prompts-base', 'dados-coletados', 'prompts-preenchidos'].includes(key)) {
    return CACHE_CONFIGS.DYNAMIC;
  }
  
  // Execuções e logs - dados em tempo real
  if (['execucoes', 'logs', 'monitoring'].includes(key)) {
    return CACHE_CONFIGS.REALTIME;
  }
  
  // Usuário e perfil - dados de usuário
  if (['user', 'profile', 'settings'].includes(key)) {
    return CACHE_CONFIGS.USER;
  }
  
  // Padrão - dados dinâmicos
  return CACHE_CONFIGS.DYNAMIC;
};

// Função para determinar retry baseado no erro
const getRetryConfig = (error: any) => {
  if (!error) return RETRY_CONFIG.network;
  
  const message = error.message?.toLowerCase() || '';
  const status = error.status || error.statusCode;
  
  // Erros de autenticação
  if (status === 401 || status === 403 || message.includes('unauthorized') || message.includes('forbidden')) {
    return RETRY_CONFIG.auth;
  }
  
  // Erros de validação
  if (status === 400 || status === 422 || message.includes('validation') || message.includes('invalid')) {
    return RETRY_CONFIG.validation;
  }
  
  // Erros de servidor
  if (status >= 500 || message.includes('server') || message.includes('internal')) {
    return RETRY_CONFIG.server;
  }
  
  // Erros de rede (padrão)
  return RETRY_CONFIG.network;
};

// Persister para cache persistente
const persister = createSyncStoragePersister({
  storage: typeof window !== 'undefined' ? window.localStorage : undefined,
  key: 'omni-keywords-cache',
  serialize: (data) => JSON.stringify(data),
  deserialize: (data) => JSON.parse(data),
});

// Configuração principal do QueryClient
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Configuração padrão
      staleTime: 5 * 60 * 1000, // 5 minutos
      gcTime: 10 * 60 * 1000, // 10 minutos
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
      refetchOnMount: true,
      
      // Configuração dinâmica baseada na query key
      queryFn: async ({ queryKey, signal }) => {
        // Aplica configuração específica baseada na query key
        const config = getQueryConfig(queryKey);
        
        // Aqui você pode adicionar lógica customizada para cada tipo de query
        // Por exemplo, adicionar headers de autenticação, logging, etc.
        
        return config;
      },
      
      // Configuração de retry dinâmica
      retry: (failureCount, error) => {
        const retryConfig = getRetryConfig(error);
        return retryConfig.retry === false ? false : failureCount < retryConfig.retry;
      },
      
      retryDelay: (attemptIndex, error) => {
        const retryConfig = getRetryConfig(error);
        return retryConfig.retryDelay ? retryConfig.retryDelay(attemptIndex) : 1000;
      },
    },
    
    mutations: {
      // Configuração padrão para mutations
      retry: 1,
      retryDelay: 1000,
      
      // Invalidação automática baseada no tipo de mutation
      onSuccess: (data, variables, context) => {
        // Lógica de invalidação será implementada nos hooks específicos
      },
      
      onError: (error, variables, context) => {
        // Log de erro para mutations
        console.error('Mutation error:', error);
      },
    },
  },
});

// Configuração de persistência
if (typeof window !== 'undefined') {
  persistQueryClient({
    queryClient,
    persister,
    maxAge: 1000 * 60 * 60 * 24, // 24 horas
    buster: 'v1', // Versão do cache
  });
}

// Utilitários para gerenciamento de cache
export const cacheUtils = {
  // Invalida queries por padrão
  invalidateQueries: (pattern: string | string[]) => {
    queryClient.invalidateQueries({ queryKey: Array.isArray(pattern) ? pattern : [pattern] });
  },
  
  // Remove queries do cache
  removeQueries: (pattern: string | string[]) => {
    queryClient.removeQueries({ queryKey: Array.isArray(pattern) ? pattern : [pattern] });
  },
  
  // Reseta todo o cache
  resetQueries: () => {
    queryClient.resetQueries();
  },
  
  // Prefetch de queries
  prefetchQuery: async (key: string[], queryFn: () => Promise<any>) => {
    await queryClient.prefetchQuery({
      queryKey: key,
      queryFn,
    });
  },
  
  // Obtém dados do cache
  getQueryData: (key: string[]) => {
    return queryClient.getQueryData({ queryKey: key });
  },
  
  // Define dados no cache
  setQueryData: (key: string[], data: any) => {
    queryClient.setQueryData({ queryKey: key }, data);
  },
  
  // Obtém estatísticas do cache
  getQueryCache: () => {
    return queryClient.getQueryCache();
  },
  
  // Limpa cache antigo
  clearOldCache: () => {
    const cache = queryClient.getQueryCache();
    const now = Date.now();
    
    cache.getAll().forEach(query => {
      const lastUpdated = query.state.dataUpdatedAt;
      const gcTime = query.options.gcTime || 10 * 60 * 1000; // 10 minutos padrão
      
      if (now - lastUpdated > gcTime) {
        cache.remove(query);
      }
    });
  },
  
  // Configuração específica para queries
  getQueryConfig: (queryKey: string[]) => {
    return getQueryConfig(queryKey);
  },
  
  // Configuração de retry para queries
  getRetryConfig: (error: any) => {
    return getRetryConfig(error);
  }
};

// Hooks utilitários para cache
export const useCacheUtils = () => {
  return cacheUtils;
};

// Configuração de desenvolvimento
if (process.env.NODE_ENV === 'development') {
  // Log de queries em desenvolvimento
  queryClient.getQueryCache().subscribe((event) => {
    if (event.type === 'added') {
      console.log('Query added:', event.query.queryKey);
    } else if (event.type === 'removed') {
      console.log('Query removed:', event.query.queryKey);
    }
  });
  
  // Log de mutations em desenvolvimento
  queryClient.getMutationCache().subscribe((event) => {
    if (event.type === 'added') {
      console.log('Mutation added:', event.mutation.options.mutationKey);
    }
  });
}

// Configuração de produção
if (process.env.NODE_ENV === 'production') {
  // Otimizações para produção
  queryClient.setDefaultOptions({
    queries: {
      ...queryClient.getDefaultOptions().queries,
      refetchOnWindowFocus: false, // Desabilita refetch automático em produção
    }
  });
}

export default queryClient; 