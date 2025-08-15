/**
 * Teste do Sistema de Cache Inteligente
 * 
 * Tracing ID: FIXTYPE-009_TEST_CACHE_20250127_001
 * Data: 2025-01-27
 * 
 * Testa todas as funcionalidades do sistema de cache:
 * - Configuração de cache
 * - Invalidação inteligente
 * - Estratégias de sincronização
 * - Otimizações de performance
 * - Monitoramento de cache
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { QueryClient } from '@tanstack/react-query';
import {
  CacheManager,
  CACHE_STRATEGIES,
  INVALIDATION_STRATEGIES,
  getCacheManager,
  useCacheUtils,
  invalidateQueries,
  autoCacheConfig
} from '../../../app/utils/cacheUtils';

// Mock do QueryClient
const mockQueryClient = {
  invalidateQueries: vi.fn(),
  removeQueries: vi.fn(),
  resetQueries: vi.fn(),
  clear: vi.fn(),
  prefetchQuery: vi.fn(),
  getQueryData: vi.fn(),
  setQueryData: vi.fn(),
  getQueryCache: vi.fn(() => ({
    getAll: vi.fn(() => []),
    remove: vi.fn(),
    subscribe: vi.fn(() => vi.fn())
  })),
  getMutationCache: vi.fn(() => ({
    subscribe: vi.fn(() => vi.fn())
  }))
} as any;

describe('CacheManager', () => {
  let cacheManager: CacheManager;

  beforeEach(() => {
    vi.clearAllMocks();
    cacheManager = new CacheManager(mockQueryClient);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getCacheConfig', () => {
    it('deve retornar configuração correta para nichos', () => {
      const config = cacheManager.getCacheConfig(['nichos']);
      expect(config).toEqual(CACHE_STRATEGIES.SEMI_STATIC);
    });

    it('deve retornar configuração correta para categorias', () => {
      const config = cacheManager.getCacheConfig(['categorias']);
      expect(config).toEqual(CACHE_STRATEGIES.SEMI_STATIC);
    });

    it('deve retornar configuração correta para stats', () => {
      const config = cacheManager.getCacheConfig(['stats']);
      expect(config).toEqual(CACHE_STRATEGIES.DYNAMIC);
    });

    it('deve retornar configuração correta para prompts-base', () => {
      const config = cacheManager.getCacheConfig(['prompts-base']);
      expect(config).toEqual(CACHE_STRATEGIES.DYNAMIC);
    });

    it('deve retornar configuração correta para execucoes', () => {
      const config = cacheManager.getCacheConfig(['execucoes']);
      expect(config).toEqual(CACHE_STRATEGIES.REALTIME);
    });

    it('deve retornar configuração padrão para queries desconhecidas', () => {
      const config = cacheManager.getCacheConfig(['unknown']);
      expect(config).toEqual(CACHE_STRATEGIES.DYNAMIC);
    });
  });

  describe('invalidateByStrategy', () => {
    it('deve invalidar queries imediatas', () => {
      cacheManager.invalidateByStrategy('CREATE_NICHO');
      
      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['nichos']
      });
      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['stats']
      });
    });

    it('deve invalidar queries condicionais com dados', () => {
      const data = { id: '123' };
      cacheManager.invalidateByStrategy('UPDATE_NICHO', data);
      
      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['nichos']
      });
      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['nichos-123']
      });
    });

    it('deve invalidar queries com delay', () => {
      vi.useFakeTimers();
      
      cacheManager.invalidateByStrategy('PROCESSAR_LOTE');
      
      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['prompts-preenchidos']
      });
      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['stats']
      });
      
      vi.advanceTimersByTime(1000);
      
      expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
        queryKey: ['execucoes']
      });
      
      vi.useRealTimers();
    });
  });

  describe('prefetchRelated', () => {
    it('deve fazer prefetch de categorias para nichos', async () => {
      const data = { id: '123' };
      await cacheManager.prefetchRelated(['nichos'], data);
      
      expect(mockQueryClient.prefetchQuery).toHaveBeenCalledWith({
        queryKey: ['categorias', '123'],
        queryFn: expect.any(Function)
      });
    });

    it('deve fazer prefetch de prompts para categorias', async () => {
      const data = { id: '456' };
      await cacheManager.prefetchRelated(['categorias'], data);
      
      expect(mockQueryClient.prefetchQuery).toHaveBeenCalledWith({
        queryKey: ['prompts-base', '456'],
        queryFn: expect.any(Function)
      });
    });

    it('deve fazer prefetch de dados coletados para prompts', async () => {
      const data = { categoria_id: '789' };
      await cacheManager.prefetchRelated(['prompts-base'], data);
      
      expect(mockQueryClient.prefetchQuery).toHaveBeenCalledWith({
        queryKey: ['dados-coletados', '789'],
        queryFn: expect.any(Function)
      });
    });
  });

  describe('optimizeCache', () => {
    it('deve remover queries antigas', () => {
      const mockQueries = [
        {
          state: { dataUpdatedAt: Date.now() - 20000000 }, // 20 minutos atrás
          options: { gcTime: 10000000 } // 10 minutos
        },
        {
          state: { dataUpdatedAt: Date.now() - 5000000 }, // 5 minutos atrás
          options: { gcTime: 10000000 } // 10 minutos
        }
      ];
      
      mockQueryClient.getQueryCache.mockReturnValue({
        getAll: vi.fn(() => mockQueries),
        remove: vi.fn()
      });
      
      cacheManager.optimizeCache();
      
      const cache = mockQueryClient.getQueryCache();
      expect(cache.remove).toHaveBeenCalledWith(mockQueries[0]);
      expect(cache.remove).not.toHaveBeenCalledWith(mockQueries[1]);
    });
  });

  describe('getStats', () => {
    it('deve retornar estatísticas corretas', () => {
      const mockQueries = [
        { state: { status: 'success', dataUpdatedAt: Date.now() } },
        { state: { status: 'error', dataUpdatedAt: Date.now() - 10000000 } },
        { state: { status: 'success', dataUpdatedAt: Date.now() - 10000000 } }
      ];
      
      mockQueryClient.getQueryCache.mockReturnValue({
        getAll: vi.fn(() => mockQueries)
      });
      
      const stats = cacheManager.getStats();
      
      expect(stats.totalQueries).toBe(3);
      expect(stats.activeQueries).toBe(2);
      expect(stats.staleQueries).toBe(2);
      expect(stats.hitRate).toBe(66.67);
    });
  });

  describe('clearCache', () => {
    it('deve limpar cache específico', () => {
      cacheManager.clearCache(['nichos']);
      
      expect(mockQueryClient.removeQueries).toHaveBeenCalledWith({
        queryKey: ['nichos']
      });
    });

    it('deve limpar todo o cache', () => {
      cacheManager.clearCache();
      
      expect(mockQueryClient.clear).toHaveBeenCalled();
    });
  });

  describe('resetCache', () => {
    it('deve resetar cache', () => {
      cacheManager.resetCache();
      
      expect(mockQueryClient.resetQueries).toHaveBeenCalled();
    });
  });

  describe('getCacheData', () => {
    it('deve obter dados do cache', () => {
      const mockData = { id: '123', name: 'Test' };
      mockQueryClient.getQueryData.mockReturnValue(mockData);
      
      const data = cacheManager.getCacheData(['nichos']);
      
      expect(mockQueryClient.getQueryData).toHaveBeenCalledWith({
        queryKey: ['nichos']
      });
      expect(data).toEqual(mockData);
    });
  });

  describe('setCacheData', () => {
    it('deve definir dados no cache', () => {
      const mockData = { id: '123', name: 'Test' };
      
      cacheManager.setCacheData(['nichos'], mockData);
      
      expect(mockQueryClient.setQueryData).toHaveBeenCalledWith({
        queryKey: ['nichos']
      }, mockData);
    });
  });
});

describe('getCacheManager', () => {
  it('deve criar instância única', () => {
    const manager1 = getCacheManager(mockQueryClient);
    const manager2 = getCacheManager(mockQueryClient);
    
    expect(manager1).toBe(manager2);
  });

  it('deve lançar erro se não inicializado', () => {
    // Reset da instância global
    (getCacheManager as any).instance = null;
    
    expect(() => getCacheManager()).toThrow('CacheManager não inicializado');
  });
});

describe('useCacheUtils', () => {
  it('deve retornar todas as funções necessárias', () => {
    const utils = useCacheUtils();
    
    expect(utils.getCacheConfig).toBeDefined();
    expect(utils.invalidateByStrategy).toBeDefined();
    expect(utils.prefetchRelated).toBeDefined();
    expect(utils.optimizeCache).toBeDefined();
    expect(utils.getStats).toBeDefined();
    expect(utils.clearCache).toBeDefined();
    expect(utils.resetCache).toBeDefined();
    expect(utils.getCacheData).toBeDefined();
    expect(utils.setCacheData).toBeDefined();
    expect(utils.subscribeToChanges).toBeDefined();
  });
});

describe('invalidateQueries', () => {
  beforeEach(() => {
    // Inicializar CacheManager
    getCacheManager(mockQueryClient);
  });

  it('deve invalidar nichos corretamente', () => {
    invalidateQueries.nichos('123');
    
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['nichos']
    });
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['nichos-123']
    });
  });

  it('deve invalidar categorias corretamente', () => {
    invalidateQueries.categorias('456', '123');
    
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['categorias']
    });
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['categorias-nicho-123']
    });
  });

  it('deve invalidar prompts corretamente', () => {
    invalidateQueries.prompts('789');
    
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['prompts-base']
    });
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['prompts-base-789']
    });
  });

  it('deve invalidar dados coletados corretamente', () => {
    invalidateQueries.dadosColetados('101');
    
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['dados-coletados']
    });
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['dados-coletados-categoria-101']
    });
  });

  it('deve invalidar preenchimentos corretamente', () => {
    invalidateQueries.preenchimentos();
    
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['prompts-preenchidos']
    });
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['stats']
    });
  });

  it('deve invalidar lotes corretamente', () => {
    invalidateQueries.lotes();
    
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['prompts-preenchidos']
    });
    expect(mockQueryClient.invalidateQueries).toHaveBeenCalledWith({
      queryKey: ['stats']
    });
  });
});

describe('autoCacheConfig', () => {
  it('deve ter configuração para nichos', () => {
    expect(autoCacheConfig.nichos).toBeDefined();
    expect(autoCacheConfig.nichos.staleTime).toBe(CACHE_STRATEGIES.SEMI_STATIC.staleTime);
    expect(autoCacheConfig.nichos.refetchOnMount).toBe(true);
  });

  it('deve ter configuração para categorias', () => {
    expect(autoCacheConfig.categorias).toBeDefined();
    expect(autoCacheConfig.categorias.staleTime).toBe(CACHE_STRATEGIES.SEMI_STATIC.staleTime);
    expect(autoCacheConfig.categorias.refetchOnMount).toBe(true);
  });

  it('deve ter configuração para prompts', () => {
    expect(autoCacheConfig.prompts).toBeDefined();
    expect(autoCacheConfig.prompts.staleTime).toBe(CACHE_STRATEGIES.DYNAMIC.staleTime);
    expect(autoCacheConfig.prompts.refetchOnMount).toBe(true);
  });

  it('deve ter configuração para dados coletados', () => {
    expect(autoCacheConfig.dadosColetados).toBeDefined();
    expect(autoCacheConfig.dadosColetados.staleTime).toBe(CACHE_STRATEGIES.DYNAMIC.staleTime);
    expect(autoCacheConfig.dadosColetados.refetchOnMount).toBe(true);
  });

  it('deve ter configuração para stats', () => {
    expect(autoCacheConfig.stats).toBeDefined();
    expect(autoCacheConfig.stats.staleTime).toBe(CACHE_STRATEGIES.DYNAMIC.staleTime);
    expect(autoCacheConfig.stats.refetchInterval).toBe(60 * 1000);
  });

  it('deve ter configuração para execuções', () => {
    expect(autoCacheConfig.execucoes).toBeDefined();
    expect(autoCacheConfig.execucoes.staleTime).toBe(CACHE_STRATEGIES.REALTIME.staleTime);
    expect(autoCacheConfig.execucoes.refetchInterval).toBe(10 * 1000);
  });
});

describe('CACHE_STRATEGIES', () => {
  it('deve ter estratégia STATIC', () => {
    expect(CACHE_STRATEGIES.STATIC).toBeDefined();
    expect(CACHE_STRATEGIES.STATIC.staleTime).toBe(30 * 60 * 1000);
    expect(CACHE_STRATEGIES.STATIC.gcTime).toBe(60 * 60 * 1000);
    expect(CACHE_STRATEGIES.STATIC.refetchOnWindowFocus).toBe(false);
  });

  it('deve ter estratégia SEMI_STATIC', () => {
    expect(CACHE_STRATEGIES.SEMI_STATIC).toBeDefined();
    expect(CACHE_STRATEGIES.SEMI_STATIC.staleTime).toBe(5 * 60 * 1000);
    expect(CACHE_STRATEGIES.SEMI_STATIC.gcTime).toBe(15 * 60 * 1000);
    expect(CACHE_STRATEGIES.SEMI_STATIC.refetchOnWindowFocus).toBe(true);
  });

  it('deve ter estratégia DYNAMIC', () => {
    expect(CACHE_STRATEGIES.DYNAMIC).toBeDefined();
    expect(CACHE_STRATEGIES.DYNAMIC.staleTime).toBe(30 * 1000);
    expect(CACHE_STRATEGIES.DYNAMIC.gcTime).toBe(5 * 60 * 1000);
    expect(CACHE_STRATEGIES.DYNAMIC.refetchOnWindowFocus).toBe(true);
  });

  it('deve ter estratégia REALTIME', () => {
    expect(CACHE_STRATEGIES.REALTIME).toBeDefined();
    expect(CACHE_STRATEGIES.REALTIME.staleTime).toBe(0);
    expect(CACHE_STRATEGIES.REALTIME.gcTime).toBe(2 * 60 * 1000);
    expect(CACHE_STRATEGIES.REALTIME.refetchInterval).toBe(30 * 1000);
  });
});

describe('INVALIDATION_STRATEGIES', () => {
  it('deve ter estratégia CREATE_NICHO', () => {
    expect(INVALIDATION_STRATEGIES.CREATE_NICHO).toBeDefined();
    expect(INVALIDATION_STRATEGIES.CREATE_NICHO.immediate).toContain('nichos');
    expect(INVALIDATION_STRATEGIES.CREATE_NICHO.immediate).toContain('stats');
  });

  it('deve ter estratégia UPDATE_NICHO', () => {
    expect(INVALIDATION_STRATEGIES.UPDATE_NICHO).toBeDefined();
    expect(INVALIDATION_STRATEGIES.UPDATE_NICHO.immediate).toContain('nichos');
    expect(INVALIDATION_STRATEGIES.UPDATE_NICHO.conditional).toBeDefined();
  });

  it('deve ter estratégia DELETE_NICHO', () => {
    expect(INVALIDATION_STRATEGIES.DELETE_NICHO).toBeDefined();
    expect(INVALIDATION_STRATEGIES.DELETE_NICHO.immediate).toContain('nichos');
    expect(INVALIDATION_STRATEGIES.DELETE_NICHO.immediate).toContain('categorias');
    expect(INVALIDATION_STRATEGIES.DELETE_NICHO.immediate).toContain('stats');
  });

  it('deve ter estratégia CREATE_CATEGORIA', () => {
    expect(INVALIDATION_STRATEGIES.CREATE_CATEGORIA).toBeDefined();
    expect(INVALIDATION_STRATEGIES.CREATE_CATEGORIA.immediate).toContain('categorias');
    expect(INVALIDATION_STRATEGIES.CREATE_CATEGORIA.immediate).toContain('stats');
  });

  it('deve ter estratégia PROCESSAR_LOTE', () => {
    expect(INVALIDATION_STRATEGIES.PROCESSAR_LOTE).toBeDefined();
    expect(INVALIDATION_STRATEGIES.PROCESSAR_LOTE.immediate).toContain('prompts-preenchidos');
    expect(INVALIDATION_STRATEGIES.PROCESSAR_LOTE.immediate).toContain('stats');
    expect(INVALIDATION_STRATEGIES.PROCESSAR_LOTE.delayed).toContain('execucoes');
  });
}); 