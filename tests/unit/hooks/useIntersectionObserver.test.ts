/**
 * useIntersectionObserver.test.ts
 * 
 * Testes unitários para o hook useIntersectionObserver
 * 
 * Tracing ID: TEST-USE-INTERSECTION-OBSERVER-001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { renderHook, act } from '@testing-library/react';
import { useRef } from 'react';
import { 
  useIntersectionObserver, 
  useLazyLoad, 
  useInfiniteScroll, 
  useVisibilityTrigger 
} from '../../app/hooks/useIntersectionObserver';

// Mock do IntersectionObserver
const mockIntersectionObserver = jest.fn();
const mockDisconnect = jest.fn();
const mockObserve = jest.fn();
const mockUnobserve = jest.fn();

beforeAll(() => {
  global.IntersectionObserver = mockIntersectionObserver;
  mockIntersectionObserver.mockReturnValue({
    disconnect: mockDisconnect,
    observe: mockObserve,
    unobserve: mockUnobserve,
  });
});

beforeEach(() => {
  jest.clearAllMocks();
});

describe('useIntersectionObserver Hook', () => {
  describe('useIntersectionObserver - Hook Principal', () => {
    it('deve inicializar com estado padrão', () => {
      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useIntersectionObserver(ref);
      });

      expect(result.current).toEqual({
        isIntersecting: false,
        intersectionRatio: 0,
        intersectionRect: null,
        boundingClientRect: null,
        rootBounds: null,
        target: null,
        time: 0,
      });
    });

    it('deve criar IntersectionObserver com configuração padrão', () => {
      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useIntersectionObserver(ref);
      });

      expect(mockIntersectionObserver).toHaveBeenCalledWith(
        expect.any(Function),
        {
          root: null,
          rootMargin: '0px',
          threshold: 0,
        }
      );
    });

    it('deve criar IntersectionObserver com configuração customizada', () => {
      const config = {
        root: document.body,
        rootMargin: '10px',
        threshold: [0, 0.5, 1],
      };

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useIntersectionObserver(ref, config);
      });

      expect(mockIntersectionObserver).toHaveBeenCalledWith(
        expect.any(Function),
        config
      );
    });

    it('deve atualizar estado quando intersection ocorre', () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useIntersectionObserver(ref);
      });

      const mockEntry = {
        isIntersecting: true,
        intersectionRatio: 0.8,
        intersectionRect: { x: 0, y: 0, width: 100, height: 100 } as DOMRectReadOnly,
        boundingClientRect: { x: 0, y: 0, width: 200, height: 200 } as DOMRectReadOnly,
        rootBounds: { x: 0, y: 0, width: 800, height: 600 } as DOMRectReadOnly,
        target: document.createElement('div'),
        time: 1234567890,
      };

      act(() => {
        intersectionCallback([mockEntry], {} as IntersectionObserver);
      });

      expect(result.current).toEqual({
        isIntersecting: true,
        intersectionRatio: 0.8,
        intersectionRect: mockEntry.intersectionRect,
        boundingClientRect: mockEntry.boundingClientRect,
        rootBounds: mockEntry.rootBounds,
        target: mockEntry.target,
        time: 1234567890,
      });
    });

    it('deve desconectar observer ao desmontar', () => {
      const { unmount } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useIntersectionObserver(ref);
      });

      unmount();

      expect(mockDisconnect).toHaveBeenCalled();
    });

    it('deve recriar observer quando configuração muda', () => {
      const { rerender } = renderHook(
        ({ config }) => {
          const ref = useRef<HTMLDivElement>(null);
          return useIntersectionObserver(ref, config);
        },
        { initialProps: { config: { threshold: 0 } } }
      );

      expect(mockIntersectionObserver).toHaveBeenCalledTimes(1);

      rerender({ config: { threshold: 0.5 } });

      expect(mockIntersectionObserver).toHaveBeenCalledTimes(2);
    });
  });

  describe('useLazyLoad - Lazy Loading', () => {
    it('deve inicializar com estado padrão', () => {
      const mockLoadFunction = jest.fn().mockResolvedValue('test-data');

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useLazyLoad(ref, mockLoadFunction);
      });

      expect(result.current).toEqual({
        data: null,
        loading: false,
        error: null,
        trigger: expect.any(Function),
      });
    });

    it('deve carregar dados quando elemento se torna visível', async () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const mockLoadFunction = jest.fn().mockResolvedValue('test-data');

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useLazyLoad(ref, mockLoadFunction);
      });

      const mockEntry = {
        isIntersecting: true,
        intersectionRatio: 0.5,
        intersectionRect: {} as DOMRectReadOnly,
        boundingClientRect: {} as DOMRectReadOnly,
        rootBounds: {} as DOMRectReadOnly,
        target: document.createElement('div'),
        time: 0,
      };

      act(() => {
        intersectionCallback([mockEntry], {} as IntersectionObserver);
      });

      expect(result.current.loading).toBe(true);

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.data).toBe('test-data');
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('deve tratar erros durante carregamento', async () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const mockError = new Error('Load failed');
      const mockLoadFunction = jest.fn().mockRejectedValue(mockError);

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useLazyLoad(ref, mockLoadFunction);
      });

      const mockEntry = {
        isIntersecting: true,
        intersectionRatio: 0.5,
        intersectionRect: {} as DOMRectReadOnly,
        boundingClientRect: {} as DOMRectReadOnly,
        rootBounds: {} as DOMRectReadOnly,
        target: document.createElement('div'),
        time: 0,
      };

      act(() => {
        intersectionCallback([mockEntry], {} as IntersectionObserver);
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.error).toBe(mockError);
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBe(null);
    });

    it('deve permitir trigger manual', async () => {
      const mockLoadFunction = jest.fn().mockResolvedValue('manual-data');

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useLazyLoad(ref, mockLoadFunction);
      });

      act(() => {
        result.current.trigger();
      });

      expect(result.current.loading).toBe(true);

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.data).toBe('manual-data');
    });

    it('não deve carregar novamente se já foi carregado', () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const mockLoadFunction = jest.fn().mockResolvedValue('test-data');

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useLazyLoad(ref, mockLoadFunction);
      });

      // Primeira intersecção
      act(() => {
        intersectionCallback([{ isIntersecting: true } as IntersectionObserverEntry], {} as IntersectionObserver);
      });

      // Segunda intersecção
      act(() => {
        intersectionCallback([{ isIntersecting: true } as IntersectionObserverEntry], {} as IntersectionObserver);
      });

      expect(mockLoadFunction).toHaveBeenCalledTimes(1);
    });
  });

  describe('useInfiniteScroll - Infinite Scroll', () => {
    it('deve inicializar com estado padrão', () => {
      const mockLoadMoreFunction = jest.fn().mockResolvedValue([]);

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useInfiniteScroll(ref, mockLoadMoreFunction);
      });

      expect(result.current).toEqual({
        items: [],
        loading: false,
        error: null,
        hasMore: true,
        loadMore: expect.any(Function),
        reset: expect.any(Function),
      });
    });

    it('deve carregar mais itens quando elemento se torna visível', async () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const mockLoadMoreFunction = jest.fn().mockResolvedValue(['item1', 'item2']);

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useInfiniteScroll(ref, mockLoadMoreFunction);
      });

      const mockEntry = {
        isIntersecting: true,
        intersectionRatio: 0.5,
        intersectionRect: {} as DOMRectReadOnly,
        boundingClientRect: {} as DOMRectReadOnly,
        rootBounds: {} as DOMRectReadOnly,
        target: document.createElement('div'),
        time: 0,
      };

      act(() => {
        intersectionCallback([mockEntry], {} as IntersectionObserver);
      });

      expect(result.current.loading).toBe(true);

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.items).toEqual(['item1', 'item2']);
      expect(result.current.loading).toBe(false);
      expect(result.current.hasMore).toBe(true);
    });

    it('deve parar de carregar quando não há mais itens', async () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const mockLoadMoreFunction = jest.fn().mockResolvedValue([]);

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useInfiniteScroll(ref, mockLoadMoreFunction);
      });

      const mockEntry = {
        isIntersecting: true,
        intersectionRatio: 0.5,
        intersectionRect: {} as DOMRectReadOnly,
        boundingClientRect: {} as DOMRectReadOnly,
        rootBounds: {} as DOMRectReadOnly,
        target: document.createElement('div'),
        time: 0,
      };

      act(() => {
        intersectionCallback([mockEntry], {} as IntersectionObserver);
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.hasMore).toBe(false);
    });

    it('deve permitir reset do estado', () => {
      const mockLoadMoreFunction = jest.fn().mockResolvedValue([]);

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useInfiniteScroll(ref, mockLoadMoreFunction);
      });

      // Simular estado com dados
      act(() => {
        result.current.loadMore();
      });

      act(() => {
        result.current.reset();
      });

      expect(result.current.items).toEqual([]);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(result.current.hasMore).toBe(true);
    });

    it('deve acumular itens em carregamentos sucessivos', async () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const mockLoadMoreFunction = jest.fn()
        .mockResolvedValueOnce(['item1', 'item2'])
        .mockResolvedValueOnce(['item3', 'item4']);

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useInfiniteScroll(ref, mockLoadMoreFunction);
      });

      // Primeiro carregamento
      act(() => {
        intersectionCallback([{ isIntersecting: true } as IntersectionObserverEntry], {} as IntersectionObserver);
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.items).toEqual(['item1', 'item2']);

      // Segundo carregamento
      act(() => {
        intersectionCallback([{ isIntersecting: true } as IntersectionObserverEntry], {} as IntersectionObserver);
      });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.items).toEqual(['item1', 'item2', 'item3', 'item4']);
    });
  });

  describe('useVisibilityTrigger - Trigger de Visibilidade', () => {
    it('deve retornar false quando elemento não está visível', () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useVisibilityTrigger(ref, 0.5);
      });

      const mockEntry = {
        isIntersecting: false,
        intersectionRatio: 0.3,
        intersectionRect: {} as DOMRectReadOnly,
        boundingClientRect: {} as DOMRectReadOnly,
        rootBounds: {} as DOMRectReadOnly,
        target: document.createElement('div'),
        time: 0,
      };

      act(() => {
        intersectionCallback([mockEntry], {} as IntersectionObserver);
      });

      expect(result.current.isVisible).toBe(false);
      expect(result.current.visibilityRatio).toBe(0.3);
    });

    it('deve retornar true quando elemento está visível', () => {
      let intersectionCallback: IntersectionObserverCallback;
      
      mockIntersectionObserver.mockImplementation((callback) => {
        intersectionCallback = callback;
        return {
          disconnect: mockDisconnect,
          observe: mockObserve,
          unobserve: mockUnobserve,
        };
      });

      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useVisibilityTrigger(ref, 0.5);
      });

      const mockEntry = {
        isIntersecting: true,
        intersectionRatio: 0.8,
        intersectionRect: {} as DOMRectReadOnly,
        boundingClientRect: {} as DOMRectReadOnly,
        rootBounds: {} as DOMRectReadOnly,
        target: document.createElement('div'),
        time: 0,
      };

      act(() => {
        intersectionCallback([mockEntry], {} as IntersectionObserver);
      });

      expect(result.current.isVisible).toBe(true);
      expect(result.current.visibilityRatio).toBe(0.8);
    });

    it('deve usar threshold padrão de 0.5', () => {
      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useVisibilityTrigger(ref);
      });

      expect(mockIntersectionObserver).toHaveBeenCalledWith(
        expect.any(Function),
        expect.objectContaining({
          threshold: 0.5,
        })
      );
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com ref null', () => {
      const { result } = renderHook(() => {
        const ref = useRef<HTMLDivElement>(null);
        return useIntersectionObserver(ref);
      });

      expect(result.current.isIntersecting).toBe(false);
    });

    it('deve lidar com erros no IntersectionObserver', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      mockIntersectionObserver.mockImplementation(() => {
        throw new Error('IntersectionObserver not supported');
      });

      expect(() => {
        renderHook(() => {
          const ref = useRef<HTMLDivElement>(null);
          return useIntersectionObserver(ref);
        });
      }).not.toThrow();

      consoleSpy.mockRestore();
    });
  });
}); 