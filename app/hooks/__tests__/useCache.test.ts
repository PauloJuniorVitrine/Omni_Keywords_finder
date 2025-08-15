/**
 * Testes unitários para useCache
 * 
 * Prompt: Implementação de testes para Criticalidade 3.1.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useCache, useQueryCache, useStaticCache, globalCache, CacheManager } from '../useCache';

// Mock de dados para teste
const mockData = {
  keywords: [
    { id: '1', keyword: 'seo tools', volume: 1000 },
    { id: '2', keyword: 'keyword research', volume: 800 }
  ],
  niches: [
    { id: '1', name: 'Marketing Digital', keywords: 150 },
    { id: '2', name: 'E-commerce', keywords: 200 }
  ]
};

const mockFetcher = jest.fn();

describe('useCache', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    globalCache.clear();
    mockFetcher.mockReset();
  });

  describe('Funcionalidade básica', () => {
    it('deve buscar dados e armazenar no cache', async () => {
      mockFetcher.mockResolvedValue(mockData.keywords);

      const { result } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 60000 })
      );

      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBe(null);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data).toEqual(mockData.keywords);
      expect(mockFetcher).toHaveBeenCalledTimes(1);
    });

    it('deve retornar dados do cache quando disponível', async () => {
      mockFetcher.mockResolvedValue(mockData.keywords);

      // Primeira chamada
      const { result: result1 } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 60000 })
      );

      await waitFor(() => {
        expect(result1.current.isLoading).toBe(false);
      });

      // Segunda chamada - deve usar cache
      const { result: result2 } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 60000 })
      );

      expect(result2.current.data).toEqual(mockData.keywords);
      expect(mockFetcher).toHaveBeenCalledTimes(1); // Apenas uma vez
    });

    it('deve lidar com erros de fetch', async () => {
      const error = new Error('API Error');
      mockFetcher.mockRejectedValue(error);

      const { result } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 60000 })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toEqual(error);
      expect(result.current.data).toBe(null);
    });
  });

  describe('Invalidação de cache', () => {
    it('deve invalidar cache específico', async () => {
      mockFetcher.mockResolvedValue(mockData.keywords);

      const { result } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 60000 })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.invalidate();
      });

      expect(result.current.data).toBe(null);
    });

    it('deve refazer fetch após invalidação', async () => {
      mockFetcher.mockResolvedValue(mockData.keywords);

      const { result } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 60000 })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.refetch();
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockFetcher).toHaveBeenCalledTimes(2);
    });
  });

  describe('TTL (Time to Live)', () => {
    it('deve expirar cache após TTL', async () => {
      jest.useFakeTimers();

      mockFetcher.mockResolvedValue(mockData.keywords);

      const { result } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 1000 })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Avançar tempo além do TTL
      act(() => {
        jest.advanceTimersByTime(2000);
      });

      // Nova chamada deve refazer fetch
      const { result: result2 } = renderHook(() =>
        useCache('keywords', mockFetcher, { ttl: 1000 })
      );

      expect(mockFetcher).toHaveBeenCalledTimes(2);

      jest.useRealTimers();
    });
  });

  describe('useQueryCache', () => {
    it('deve funcionar como useCache com stale time', async () => {
      mockFetcher.mockResolvedValue(mockData.keywords);

      const { result } = renderHook(() =>
        useQueryCache('keywords', mockFetcher, { 
          ttl: 60000, 
          staleTime: 5000 
        })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data).toEqual(mockData.keywords);
    });
  });

  describe('useStaticCache', () => {
    it('deve armazenar dados estáticos no cache', () => {
      const { result } = renderHook(() =>
        useStaticCache('static-data', mockData.keywords, 60000)
      );

      expect(result.current.has()).toBe(true);
      expect(result.current.get()).toEqual(mockData.keywords);
    });

    it('deve permitir atualizar dados estáticos', () => {
      const { result } = renderHook(() =>
        useStaticCache('static-data', mockData.keywords, 60000)
      );

      const newData = [...mockData.keywords, { id: '3', keyword: 'new keyword', volume: 500 }];

      act(() => {
        result.current.set(newData);
      });

      expect(result.current.get()).toEqual(newData);
    });

    it('deve permitir deletar dados estáticos', () => {
      const { result } = renderHook(() =>
        useStaticCache('static-data', mockData.keywords, 60000)
      );

      expect(result.current.has()).toBe(true);

      act(() => {
        result.current.delete();
      });

      expect(result.current.has()).toBe(false);
      expect(result.current.get()).toBe(null);
    });
  });

  describe('CacheManager', () => {
    it('deve gerenciar estatísticas de cache', () => {
      const cacheManager = new CacheManager({ enableLogging: true });

      cacheManager.set('test-key', 'test-value');
      expect(cacheManager.get('test-key')).toBe('test-value');

      const stats = cacheManager.getStats();
      expect(stats.hits).toBe(1);
      expect(stats.size).toBe(1);
    });

    it('deve invalidar cache por padrão', () => {
      const cacheManager = new CacheManager();

      cacheManager.set('keywords', mockData.keywords);
      cacheManager.set('niches', mockData.niches);

      const invalidatedCount = cacheManager.invalidate('keywords');
      expect(invalidatedCount).toBe(1);

      expect(cacheManager.get('keywords')).toBe(null);
      expect(cacheManager.get('niches')).toEqual(mockData.niches);
    });

    it('deve limpar todo o cache', () => {
      const cacheManager = new CacheManager();

      cacheManager.set('key1', 'value1');
      cacheManager.set('key2', 'value2');

      cacheManager.clear();

      expect(cacheManager.get('key1')).toBe(null);
      expect(cacheManager.get('key2')).toBe(null);
      expect(cacheManager.getStats().size).toBe(0);
    });
  });

  describe('Callbacks', () => {
    it('deve chamar onSuccess callback', async () => {
      const onSuccess = jest.fn();
      mockFetcher.mockResolvedValue(mockData.keywords);

      const { result } = renderHook(() =>
        useCache('keywords', mockFetcher, { 
          ttl: 60000,
          onSuccess 
        })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(onSuccess).toHaveBeenCalledWith(mockData.keywords);
    });

    it('deve chamar onError callback', async () => {
      const onError = jest.fn();
      const error = new Error('API Error');
      mockFetcher.mockRejectedValue(error);

      const { result } = renderHook(() =>
        useCache('keywords', mockFetcher, { 
          ttl: 60000,
          onError 
        })
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(onError).toHaveBeenCalledWith(error);
    });
  });

  describe('AbortController', () => {
    it('deve cancelar requisições anteriores', async () => {
      mockFetcher.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(mockData.keywords), 1000))
      );

      const { result, rerender } = renderHook(
        ({ key }) => useCache(key, mockFetcher, { ttl: 60000 }),
        { initialProps: { key: 'keywords' } }
      );

      // Mudar key rapidamente para testar cancelamento
      rerender({ key: 'keywords2' });
      rerender({ key: 'keywords3' });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Apenas a última requisição deve completar
      expect(mockFetcher).toHaveBeenCalledTimes(3);
    });
  });
}); 