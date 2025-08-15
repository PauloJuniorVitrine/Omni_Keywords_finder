/**
 * Utilitários de Cache Inteligente
 * 
 * Tracing ID: FIXTYPE-009_CACHE_UTILS_20250127_001
 * Data: 2025-01-27
 * 
 * Utilitários para gerenciamento avançado de cache:
 * - Invalidação inteligente
 * - Estratégias de sincronização
 * - Otimizações de performance
 * - Monitoramento de cache
 */

import { QueryClient } from '@tanstack/react-query';

// Tipos para configuração de cache
export interface CacheConfig {
  key: string;
  staleTime: number;
  gcTime: number;
  refetchOnWindowFocus: boolean;
  refetchOnReconnect: boolean;
  refetchInterval?: number;
}

export interface InvalidationStrategy {
  immediate: string[];
  delayed: string[];
  conditional: (data: any) => string[];
}

export interface CacheStats {
  totalQueries: number;
  activeQueries: number;
  staleQueries: number;
  cacheSize: number;
  hitRate: number;
}

// Configurações de cache por tipo de dados
export const CACHE_STRATEGIES = {
  // Dados estáticos (nichos, configurações)
  STATIC: {
    staleTime: 30 * 60 * 1000, // 30 minutos
    gcTime: 60 * 60 * 1000, // 1 hora
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  },
  
  // Dados semi-estáticos (categorias, prompts-base)
  SEMI_STATIC: {
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 15 * 60 * 1000, // 15 minutos
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  },
  
  // Dados dinâmicos (stats, dados-coletados)
  DYNAMIC: {
    staleTime: 30 * 1000, // 30 segundos
    gcTime: 5 * 60 * 1000, // 5 minutos
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  },
  
  // Dados em tempo real (execuções, logs)
  REALTIME: {
    staleTime: 0, // Sempre stale
    gcTime: 2 * 60 * 1000, // 2 minutos
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    refetchInterval: 30 * 1000, // Refetch a cada 30s
  }
};

// Estratégias de invalidação por tipo de mutation
export const INVALIDATION_STRATEGIES = {
  // Criar nicho
  CREATE_NICHO: {
    immediate: ['nichos', 'stats'],
    delayed: [],
    conditional: () => []
  },
  
  // Atualizar nicho
  UPDATE_NICHO: {
    immediate: ['nichos'],
    delayed: [],
    conditional: (data: any) => [`nichos-${data.id}`]
  },
  
  // Deletar nicho
  DELETE_NICHO: {
    immediate: ['nichos', 'categorias', 'stats'],
    delayed: [],
    conditional: (data: any) => [`nichos-${data.id}`, `categorias-nicho-${data.id}`]
  },
  
  // Criar categoria
  CREATE_CATEGORIA: {
    immediate: ['categorias', 'stats'],
    delayed: [],
    conditional: (data: any) => [`categorias-nicho-${data.nicho_id}`]
  },
  
  // Atualizar categoria
  UPDATE_CATEGORIA: {
    immediate: ['categorias'],
    delayed: [],
    conditional: (data: any) => [`categorias-${data.id}`, `prompts-base-${data.id}`]
  },
  
  // Deletar categoria
  DELETE_CATEGORIA: {
    immediate: ['categorias', 'prompts-base', 'dados-coletados', 'stats'],
    delayed: [],
    conditional: (data: any) => [
      `categorias-${data.id}`,
      `prompts-base-${data.id}`,
      `dados-coletados-categoria-${data.id}`
    ]
  },
  
  // Upload prompt base
  UPLOAD_PROMPT_BASE: {
    immediate: ['prompts-base', 'stats'],
    delayed: [],
    conditional: (data: any) => [`prompts-base-${data.categoria_id}`]
  },
  
  // Criar dados coletados
  CREATE_DADOS_COLETADOS: {
    immediate: ['dados-coletados', 'stats'],
    delayed: [],
    conditional: (data: any) => [`dados-coletados-categoria-${data.categoria_id}`]
  },
  
  // Processar preenchimento
  PROCESSAR_PREENCHIMENTO: {
    immediate: ['prompts-preenchidos', 'stats'],
    delayed: [],
    conditional: () => []
  },
  
  // Processar lote
  PROCESSAR_LOTE: {
    immediate: ['prompts-preenchidos', 'stats'],
    delayed: ['execucoes'],
    conditional: () => []
  }
};

/**
 * Classe principal para gerenciamento de cache
 */
export class CacheManager {
  private queryClient: QueryClient;
  private stats: CacheStats = {
    totalQueries: 0,
    activeQueries: 0,
    staleQueries: 0,
    cacheSize: 0,
    hitRate: 0
  };

  constructor(queryClient: QueryClient) {
    this.queryClient = queryClient;
    this.updateStats();
  }

  /**
   * Obtém configuração de cache baseada na query key
   */
  getCacheConfig(queryKey: string[]): CacheConfig {
    const key = queryKey[0] as string;
    
    // Nichos e categorias - dados semi-estáticos
    if (['nichos', 'categorias'].includes(key)) {
      return CACHE_STRATEGIES.SEMI_STATIC;
    }
    
    // Stats e métricas - dados dinâmicos
    if (['stats', 'metrics', 'analytics'].includes(key)) {
      return CACHE_STRATEGIES.DYNAMIC;
    }
    
    // Prompts e dados coletados - dados dinâmicos
    if (['prompts-base', 'dados-coletados', 'prompts-preenchidos'].includes(key)) {
      return CACHE_STRATEGIES.DYNAMIC;
    }
    
    // Execuções e logs - dados em tempo real
    if (['execucoes', 'logs', 'monitoring'].includes(key)) {
      return CACHE_STRATEGIES.REALTIME;
    }
    
    // Padrão - dados dinâmicos
    return CACHE_STRATEGIES.DYNAMIC;
  }

  /**
   * Invalida queries baseado em estratégia
   */
  invalidateByStrategy(strategyKey: keyof typeof INVALIDATION_STRATEGIES, data?: any): void {
    const strategy = INVALIDATION_STRATEGIES[strategyKey];
    
    // Invalidação imediata
    strategy.immediate.forEach(key => {
      this.queryClient.invalidateQueries({ queryKey: [key] });
    });
    
    // Invalidação condicional
    if (data) {
      const conditionalKeys = strategy.conditional(data);
      conditionalKeys.forEach(key => {
        this.queryClient.invalidateQueries({ queryKey: [key] });
      });
    }
    
    // Invalidação com delay (para queries que dependem de processamento)
    if (strategy.delayed.length > 0) {
      setTimeout(() => {
        strategy.delayed.forEach(key => {
          this.queryClient.invalidateQueries({ queryKey: [key] });
        });
      }, 1000);
    }
  }

  /**
   * Prefetch inteligente baseado em padrões de uso
   */
  async prefetchRelated(primaryKey: string[], data?: any): Promise<void> {
    const key = primaryKey[0];
    
    // Prefetch baseado no tipo de dados
    switch (key) {
      case 'nichos':
        // Prefetch das categorias do nicho
        if (data?.id) {
          await this.queryClient.prefetchQuery({
            queryKey: ['categorias', data.id],
            queryFn: () => Promise.resolve([]), // Será substituído pela função real
          });
        }
        break;
        
      case 'categorias':
        // Prefetch dos prompts-base da categoria
        if (data?.id) {
          await this.queryClient.prefetchQuery({
            queryKey: ['prompts-base', data.id],
            queryFn: () => Promise.resolve(null),
          });
        }
        break;
        
      case 'prompts-base':
        // Prefetch dos dados coletados da categoria
        if (data?.categoria_id) {
          await this.queryClient.prefetchQuery({
            queryKey: ['dados-coletados', data.categoria_id],
            queryFn: () => Promise.resolve([]),
          });
        }
        break;
    }
  }

  /**
   * Otimiza cache removendo dados antigos
   */
  optimizeCache(): void {
    const cache = this.queryClient.getQueryCache();
    const now = Date.now();
    
    cache.getAll().forEach(query => {
      const lastUpdated = query.state.dataUpdatedAt;
      const gcTime = query.options.gcTime || 10 * 60 * 1000; // 10 minutos padrão
      
      // Remove queries muito antigas
      if (now - lastUpdated > gcTime * 2) {
        cache.remove(query);
      }
    });
    
    this.updateStats();
  }

  /**
   * Atualiza estatísticas do cache
   */
  updateStats(): void {
    const cache = this.queryClient.getQueryCache();
    const queries = cache.getAll();
    const now = Date.now();
    
    this.stats = {
      totalQueries: queries.length,
      activeQueries: queries.filter(q => q.state.status === 'success').length,
      staleQueries: queries.filter(q => {
        const staleTime = q.options.staleTime || 5 * 60 * 1000;
        return now - q.state.dataUpdatedAt > staleTime;
      }).length,
      cacheSize: queries.reduce((size, q) => size + JSON.stringify(q.state.data).length, 0),
      hitRate: this.calculateHitRate()
    };
  }

  /**
   * Calcula taxa de hit do cache
   */
  private calculateHitRate(): number {
    const cache = this.queryClient.getQueryCache();
    const queries = cache.getAll();
    
    if (queries.length === 0) return 0;
    
    const successfulQueries = queries.filter(q => q.state.status === 'success').length;
    return (successfulQueries / queries.length) * 100;
  }

  /**
   * Obtém estatísticas do cache
   */
  getStats(): CacheStats {
    this.updateStats();
    return { ...this.stats };
  }

  /**
   * Limpa cache por padrão
   */
  clearCache(pattern?: string | string[]): void {
    if (pattern) {
      this.queryClient.removeQueries({ 
        queryKey: Array.isArray(pattern) ? pattern : [pattern] 
      });
    } else {
      this.queryClient.clear();
    }
    
    this.updateStats();
  }

  /**
   * Reseta cache mantendo queries ativas
   */
  resetCache(): void {
    this.queryClient.resetQueries();
    this.updateStats();
  }

  /**
   * Obtém dados do cache
   */
  getCacheData(key: string[]): any {
    return this.queryClient.getQueryData({ queryKey: key });
  }

  /**
   * Define dados no cache
   */
  setCacheData(key: string[], data: any): void {
    this.queryClient.setQueryData({ queryKey: key }, data);
  }

  /**
   * Monitora mudanças no cache
   */
  subscribeToChanges(callback: (event: any) => void): () => void {
    const unsubscribe = this.queryClient.getQueryCache().subscribe(callback);
    return unsubscribe;
  }
}

// Instância global do CacheManager
let cacheManagerInstance: CacheManager | null = null;

/**
 * Obtém instância do CacheManager
 */
export const getCacheManager = (queryClient?: QueryClient): CacheManager => {
  if (!cacheManagerInstance && queryClient) {
    cacheManagerInstance = new CacheManager(queryClient);
  }
  
  if (!cacheManagerInstance) {
    throw new Error('CacheManager não inicializado. Forneça um QueryClient.');
  }
  
  return cacheManagerInstance;
};

/**
 * Hook para usar utilitários de cache
 */
export const useCacheUtils = () => {
  return {
    getCacheConfig: (queryKey: string[]) => getCacheManager().getCacheConfig(queryKey),
    invalidateByStrategy: (strategy: keyof typeof INVALIDATION_STRATEGIES, data?: any) => 
      getCacheManager().invalidateByStrategy(strategy, data),
    prefetchRelated: (primaryKey: string[], data?: any) => 
      getCacheManager().prefetchRelated(primaryKey, data),
    optimizeCache: () => getCacheManager().optimizeCache(),
    getStats: () => getCacheManager().getStats(),
    clearCache: (pattern?: string | string[]) => getCacheManager().clearCache(pattern),
    resetCache: () => getCacheManager().resetCache(),
    getCacheData: (key: string[]) => getCacheManager().getCacheData(key),
    setCacheData: (key: string[], data: any) => getCacheManager().setCacheData(key, data),
    subscribeToChanges: (callback: (event: any) => void) => 
      getCacheManager().subscribeToChanges(callback)
  };
};

/**
 * Utilitários para invalidação inteligente
 */
export const invalidateQueries = {
  // Invalida queries relacionadas a nichos
  nichos: (nichoId?: string) => {
    const manager = getCacheManager();
    if (nichoId) {
      manager.invalidateByStrategy('UPDATE_NICHO', { id: nichoId });
    } else {
      manager.invalidateByStrategy('CREATE_NICHO');
    }
  },
  
  // Invalida queries relacionadas a categorias
  categorias: (categoriaId?: string, nichoId?: string) => {
    const manager = getCacheManager();
    if (categoriaId) {
      manager.invalidateByStrategy('UPDATE_CATEGORIA', { id: categoriaId });
    } else if (nichoId) {
      manager.invalidateByStrategy('CREATE_CATEGORIA', { nicho_id: nichoId });
    } else {
      manager.invalidateByStrategy('CREATE_CATEGORIA');
    }
  },
  
  // Invalida queries relacionadas a prompts
  prompts: (categoriaId?: string) => {
    const manager = getCacheManager();
    if (categoriaId) {
      manager.invalidateByStrategy('UPLOAD_PROMPT_BASE', { categoria_id: categoriaId });
    } else {
      manager.invalidateByStrategy('UPLOAD_PROMPT_BASE');
    }
  },
  
  // Invalida queries relacionadas a dados coletados
  dadosColetados: (categoriaId?: string) => {
    const manager = getCacheManager();
    if (categoriaId) {
      manager.invalidateByStrategy('CREATE_DADOS_COLETADOS', { categoria_id: categoriaId });
    } else {
      manager.invalidateByStrategy('CREATE_DADOS_COLETADOS');
    }
  },
  
  // Invalida queries relacionadas a preenchimentos
  preenchimentos: () => {
    const manager = getCacheManager();
    manager.invalidateByStrategy('PROCESSAR_PREENCHIMENTO');
  },
  
  // Invalida queries relacionadas a lotes
  lotes: () => {
    const manager = getCacheManager();
    manager.invalidateByStrategy('PROCESSAR_LOTE');
  }
};

/**
 * Configuração automática de cache
 */
export const autoCacheConfig = {
  // Configuração para queries de nichos
  nichos: {
    ...CACHE_STRATEGIES.SEMI_STATIC,
    refetchOnMount: true,
  },
  
  // Configuração para queries de categorias
  categorias: {
    ...CACHE_STRATEGIES.SEMI_STATIC,
    refetchOnMount: true,
  },
  
  // Configuração para queries de prompts
  prompts: {
    ...CACHE_STRATEGIES.DYNAMIC,
    refetchOnMount: true,
  },
  
  // Configuração para queries de dados coletados
  dadosColetados: {
    ...CACHE_STRATEGIES.DYNAMIC,
    refetchOnMount: true,
  },
  
  // Configuração para queries de stats
  stats: {
    ...CACHE_STRATEGIES.DYNAMIC,
    refetchInterval: 60 * 1000, // Refetch a cada minuto
  },
  
  // Configuração para queries de execuções
  execucoes: {
    ...CACHE_STRATEGIES.REALTIME,
    refetchInterval: 10 * 1000, // Refetch a cada 10 segundos
  }
}; 