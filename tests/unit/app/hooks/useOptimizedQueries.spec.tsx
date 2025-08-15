/**
 * Testes Unitários - Hook de Otimização de Queries
 * 
 * Este arquivo contém testes abrangentes para o hook useOptimizedQueries,
 * cobrindo todas as funcionalidades de otimização de performance.
 * 
 * Autor: Sistema Omni Keywords Finder
 * Data: 2024-12-19
 * Versão: 1.0.0
 */

import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react';
import { 
  useOptimizedQuery, 
  useInfiniteScroll, 
  useLazyLoad, 
  useDebouncedQuery,
  usePersistentQuery,
  usePrefetchQuery,
  clearQueryCache,
  getCacheStats
} from '../../../../app/hooks/useOptimizedQueries';

// Mock para localStorage e sessionStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Mock para IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

describe('useOptimizedQuery', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should fetch data successfully', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-query',
        fetcher: mockFetcher,
      })
    );

    const [data, loading, error, refetch] = result.current;

    expect(loading).toBe(true);
    expect(data).toBe(null);
    expect(error).toBe(null);

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    expect(result.current[0]).toEqual({ data: 'test' });
    expect(result.current[1]).toBe(false);
    expect(result.current[2]).toBe(null);
  });

  it('should handle fetch errors', async () => {
    const mockError = new Error('Network error');
    const mockFetcher = jest.fn().mockRejectedValue(mockError);

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-query-error',
        fetcher: mockFetcher,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalled();
      });
    });

    expect(result.current[0]).toBe(null);
    expect(result.current[1]).toBe(false);
    expect(result.current[2]).toEqual(mockError);

    consoleSpy.mockRestore();
  });

  it('should deduplicate identical queries', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result: result1 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-dedup',
        fetcher: mockFetcher,
        deduplication: true,
      })
    );

    const { result: result2 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-dedup',
        fetcher: mockFetcher,
        deduplication: true,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1); // Apenas uma chamada
      });
    });

    expect(result1.current[0]).toEqual({ data: 'test' });
    expect(result2.current[0]).toEqual({ data: 'test' });
  });

  it('should retry failed requests', async () => {
    const mockFetcher = jest.fn()
      .mockRejectedValueOnce(new Error('First attempt'))
      .mockRejectedValueOnce(new Error('Second attempt'))
      .mockResolvedValue({ data: 'success' });

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-retry',
        fetcher: mockFetcher,
        retryCount: 2,
        retryDelay: 100,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(3); // 1 inicial + 2 retries
      });
    });

    expect(result.current[0]).toEqual({ data: 'success' });
    expect(result.current[1]).toBe(false);
    expect(result.current[2]).toBe(null);
  });

  it('should cache data and return from cache', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'cached' });

    const { result: result1 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-cache',
        fetcher: mockFetcher,
        cacheTime: 10000,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    // Segunda instância deve usar cache
    const { result: result2 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-cache',
        fetcher: mockFetcher,
        cacheTime: 10000,
      })
    );

    expect(result2.current[0]).toEqual({ data: 'cached' });
    expect(mockFetcher).toHaveBeenCalledTimes(1); // Ainda apenas 1 chamada
  });

  it('should handle background refetch', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'fresh' });

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-background',
        fetcher: mockFetcher,
        staleTime: 1000,
        backgroundRefetch: true,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    // Avança o tempo para tornar os dados stale
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(2); // Background refetch
      });
    });
  });

  it('should handle manual refetch', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'refetched' });

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-manual-refetch',
        fetcher: mockFetcher,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    // Manual refetch
    await act(async () => {
      await result.current[3]();
    });

    expect(mockFetcher).toHaveBeenCalledTimes(2);
  });
});

describe('useInfiniteScroll', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
  });

  it('should load initial data', async () => {
    const mockFetcher = jest.fn().mockResolvedValue(['item1', 'item2']);

    const { result } = renderHook(() =>
      useInfiniteScroll({
        key: 'test-infinite',
        fetcher: mockFetcher,
        pageSize: 2,
        hasMore: (data) => data.length < 10,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    expect(result.current.data).toEqual(['item1', 'item2']);
    expect(result.current.hasMore).toBe(true);
  });

  it('should load more data', async () => {
    const mockFetcher = jest.fn()
      .mockResolvedValueOnce(['item1', 'item2'])
      .mockResolvedValueOnce(['item3', 'item4']);

    const { result } = renderHook(() =>
      useInfiniteScroll({
        key: 'test-infinite-more',
        fetcher: mockFetcher,
        pageSize: 2,
        hasMore: (data) => data.length < 10,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    // Carrega mais dados
    await act(async () => {
      result.current.loadMore();
    });

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(2);
      });
    });

    expect(result.current.data).toEqual(['item1', 'item2', 'item3', 'item4']);
  });

  it('should reset data', async () => {
    const mockFetcher = jest.fn().mockResolvedValue(['item1', 'item2']);

    const { result } = renderHook(() =>
      useInfiniteScroll({
        key: 'test-infinite-reset',
        fetcher: mockFetcher,
        pageSize: 2,
        hasMore: (data) => data.length < 10,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    // Reset
    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toEqual([]);
    expect(result.current.hasMore).toBe(true);
  });
});

describe('useLazyLoad', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
  });

  it('should not load data initially', () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'lazy' });

    const { result } = renderHook(() =>
      useLazyLoad({
        key: 'test-lazy',
        fetcher: mockFetcher,
        threshold: 100,
      })
    );

    expect(result.current.data).toBe(null);
    expect(result.current.loading).toBe(false);
    expect(mockFetcher).not.toHaveBeenCalled();
  });

  it('should load data when element becomes visible', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'lazy' });

    const { result } = renderHook(() =>
      useLazyLoad({
        key: 'test-lazy-visible',
        fetcher: mockFetcher,
        threshold: 100,
      })
    );

    // Simula elemento se tornando visível
    const mockIntersectionObserver = global.IntersectionObserver as jest.Mock;
    const mockObserver = mockIntersectionObserver.mock.results[0].value;

    act(() => {
      // Simula callback do IntersectionObserver
      mockObserver.observe.mock.calls[0][0].dispatchEvent(
        new Event('intersection')
      );
    });

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    expect(result.current.data).toEqual({ data: 'lazy' });
  });
});

describe('useDebouncedQuery', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should debounce query key changes', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'debounced' });

    const { result } = renderHook(() =>
      useDebouncedQuery({
        key: 'test-debounced',
        fetcher: mockFetcher,
        debounceTime: 300,
      })
    );

    // Muda a key rapidamente
    act(() => {
      result.current.setQueryKey('new-key-1');
      result.current.setQueryKey('new-key-2');
      result.current.setQueryKey('new-key-3');
    });

    // Avança o tempo para o debounce
    act(() => {
      jest.advanceTimersByTime(300);
    });

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1); // Apenas uma chamada
      });
    });
  });
});

describe('usePersistentQuery', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
  });

  it('should load data from localStorage', () => {
    const storedData = {
      data: { cached: 'data' },
      timestamp: Date.now(),
    };

    localStorageMock.getItem.mockReturnValue(JSON.stringify(storedData));

    const mockFetcher = jest.fn().mockResolvedValue({ fresh: 'data' });

    const { result } = renderHook(() =>
      usePersistentQuery({
        key: 'test-persistent',
        fetcher: mockFetcher,
        storageKey: 'test-storage',
        storage: 'localStorage',
        cacheTime: 10000,
      })
    );

    expect(result.current[0]).toEqual({ cached: 'data' });
    expect(mockFetcher).not.toHaveBeenCalled(); // Não deve chamar o fetcher
  });

  it('should save data to localStorage', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ fresh: 'data' });

    const { result } = renderHook(() =>
      usePersistentQuery({
        key: 'test-persistent-save',
        fetcher: mockFetcher,
        storageKey: 'test-storage-save',
        storage: 'localStorage',
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'test-storage-save',
      expect.stringContaining('"fresh":"data"')
    );
  });
});

describe('usePrefetchQuery', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
  });

  it('should prefetch data', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ prefetched: 'data' });

    const { result } = renderHook(() =>
      usePrefetchQuery({
        key: 'test-prefetch',
        fetcher: mockFetcher,
      })
    );

    await act(async () => {
      await result.current.prefetch();
    });

    expect(mockFetcher).toHaveBeenCalledTimes(1);

    // Verifica se os dados estão no cache
    const stats = getCacheStats();
    expect(stats.cacheSize).toBe(1);
  });
});

describe('Cache Utilities', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
  });

  it('should clear specific cache entry', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-clear-specific',
        fetcher: mockFetcher,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    expect(result.current[0]).toEqual({ data: 'test' });

    // Limpa cache específico
    clearQueryCache('test-clear-specific');

    const stats = getCacheStats();
    expect(stats.cacheSize).toBe(0);
  });

  it('should clear all cache', async () => {
    const mockFetcher1 = jest.fn().mockResolvedValue({ data: 'test1' });
    const mockFetcher2 = jest.fn().mockResolvedValue({ data: 'test2' });

    const { result: result1 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-clear-all-1',
        fetcher: mockFetcher1,
      })
    );

    const { result: result2 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-clear-all-2',
        fetcher: mockFetcher2,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher1).toHaveBeenCalledTimes(1);
        expect(mockFetcher2).toHaveBeenCalledTimes(1);
      });
    });

    // Limpa todo o cache
    clearQueryCache();

    const stats = getCacheStats();
    expect(stats.cacheSize).toBe(0);
    expect(stats.pendingQueries).toBe(0);
  });

  it('should return cache statistics', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-stats',
        fetcher: mockFetcher,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    const stats = getCacheStats();
    expect(stats.cacheSize).toBe(1);
    expect(stats.pendingQueries).toBe(0);
    expect(stats.totalEntries).toBeGreaterThan(0);
  });
});

describe('Error Handling', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
  });

  it('should handle AbortError gracefully', async () => {
    const abortError = new Error('AbortError');
    abortError.name = 'AbortError';
    
    const mockFetcher = jest.fn().mockRejectedValue(abortError);

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-abort',
        fetcher: mockFetcher,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalled();
      });
    });

    // Não deve mostrar erro no console para AbortError
    expect(consoleSpy).not.toHaveBeenCalled();

    consoleSpy.mockRestore();
  });

  it('should handle network errors with retry', async () => {
    const networkError = new Error('Network error');
    const mockFetcher = jest.fn()
      .mockRejectedValueOnce(networkError)
      .mockResolvedValue({ data: 'success' });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-network-retry',
        fetcher: mockFetcher,
        retryCount: 1,
        retryDelay: 100,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(2); // 1 inicial + 1 retry
      });
    });

    expect(result.current[0]).toEqual({ data: 'success' });
    expect(consoleSpy).toHaveBeenCalled();

    consoleSpy.mockRestore();
  });
});

describe('Performance Optimizations', () => {
  beforeEach(() => {
    clearQueryCache();
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should handle stale time correctly', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'fresh' });

    const { result } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-stale',
        fetcher: mockFetcher,
        staleTime: 1000,
        backgroundRefetch: true,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    // Avança o tempo para tornar stale
    act(() => {
      jest.advanceTimersByTime(1500);
    });

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(2); // Background refetch
      });
    });
  });

  it('should handle cache expiration', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'cached' });

    const { result: result1 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-expiration',
        fetcher: mockFetcher,
        cacheTime: 1000,
      })
    );

    await act(async () => {
      await waitFor(() => {
        expect(mockFetcher).toHaveBeenCalledTimes(1);
      });
    });

    // Avança o tempo para expirar cache
    act(() => {
      jest.advanceTimersByTime(1500);
    });

    // Segunda instância deve fazer nova chamada
    const { result: result2 } = renderHook(() =>
      useOptimizedQuery({
        key: 'test-expiration',
        fetcher: mockFetcher,
        cacheTime: 1000,
      })
    );

    expect(mockFetcher).toHaveBeenCalledTimes(2); // Nova chamada
  });
}); 