/**
 * Testes Unitários para useOptimisticUpdate
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 9.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { renderHook, act } from '@testing-library/react';
import { useOptimisticUpdate, useOptimisticListUpdate, useOptimisticCreate, useOptimisticDelete } from '../../../app/hooks/useOptimisticUpdate';
import { globalCache } from '../../../app/services/cache/intelligent-cache';

// Mock do cache global
jest.mock('../../../app/services/cache/intelligent-cache', () => ({
  globalCache: {
    get: jest.fn(),
    set: jest.fn(),
    delete: jest.fn()
  }
}));

describe('useOptimisticUpdate', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (globalCache.get as jest.Mock).mockReturnValue(null);
  });

  describe('Configuração básica', () => {
    it('deve inicializar com estado correto', () => {
      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, updated: true })
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      expect(result.current.isPending).toBe(false);
      expect(result.current.error).toBe(null);
      expect(typeof result.current.execute).toBe('function');
      expect(typeof result.current.rollback).toBe('function');
    });

    it('deve aceitar configuração com timeout', () => {
      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, updated: true }),
        timeout: 5000
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      expect(result.current.isPending).toBe(false);
      expect(result.current.error).toBe(null);
    });
  });

  describe('Execução de updates otimistas', () => {
    it('deve executar update otimista com sucesso', async () => {
      const originalData = { id: 1, name: 'Test' };
      const updatedData = { id: 1, name: 'Updated Test' };
      
      (globalCache.get as jest.Mock).mockReturnValue(originalData);

      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, name: 'Updated Test' })
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      const mockApiCall = jest.fn().mockResolvedValue(updatedData);

      await act(async () => {
        const response = await result.current.execute(mockApiCall);
        expect(response).toEqual(updatedData);
      });

      expect(result.current.isPending).toBe(false);
      expect(result.current.error).toBe(null);
      expect(globalCache.set).toHaveBeenCalledWith('test:data', updatedData);
    });

    it('deve aplicar update otimista antes da chamada da API', async () => {
      const originalData = { id: 1, name: 'Test' };
      (globalCache.get as jest.Mock).mockReturnValue(originalData);

      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, name: 'Optimistic Update' })
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      const mockApiCall = jest.fn().mockImplementation(() => {
        // Verificar se o cache foi atualizado otimisticamente
        expect(globalCache.set).toHaveBeenCalledWith('test:data', { id: 1, name: 'Optimistic Update' }, 0);
        return Promise.resolve({ id: 1, name: 'Final Update' });
      });

      await act(async () => {
        await result.current.execute(mockApiCall);
      });

      expect(globalCache.set).toHaveBeenCalledTimes(2); // Otimista + final
    });

    it('deve fazer rollback em caso de erro', async () => {
      const originalData = { id: 1, name: 'Test' };
      (globalCache.get as jest.Mock).mockReturnValue(originalData);

      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, name: 'Optimistic Update' })
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      const mockApiCall = jest.fn().mockRejectedValue(new Error('API Error'));

      await act(async () => {
        try {
          await result.current.execute(mockApiCall);
        } catch (error) {
          // Erro esperado
        }
      });

      expect(result.current.isPending).toBe(false);
      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('API Error');
      
      // Verificar se o rollback foi executado
      expect(globalCache.set).toHaveBeenCalledWith('test:data', originalData);
    });

    it('deve executar callback de sucesso', async () => {
      const originalData = { id: 1, name: 'Test' };
      const updatedData = { id: 1, name: 'Updated Test' };
      
      (globalCache.get as jest.Mock).mockReturnValue(originalData);

      const onSuccess = jest.fn();
      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, name: 'Updated Test' }),
        onSuccess
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      const mockApiCall = jest.fn().mockResolvedValue(updatedData);

      await act(async () => {
        await result.current.execute(mockApiCall);
      });

      expect(onSuccess).toHaveBeenCalledWith(updatedData);
    });

    it('deve executar callback de erro', async () => {
      const originalData = { id: 1, name: 'Test' };
      (globalCache.get as jest.Mock).mockReturnValue(originalData);

      const onError = jest.fn();
      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, name: 'Optimistic Update' }),
        onError
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      const apiError = new Error('API Error');
      const mockApiCall = jest.fn().mockRejectedValue(apiError);

      await act(async () => {
        try {
          await result.current.execute(mockApiCall);
        } catch (error) {
          // Erro esperado
        }
      });

      expect(onError).toHaveBeenCalledWith(apiError, originalData);
    });
  });

  describe('Rollback manual', () => {
    it('deve executar rollback manual', () => {
      const originalData = { id: 1, name: 'Test' };
      (globalCache.get as jest.Mock).mockReturnValue(originalData);

      const rollbackFn = jest.fn();
      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, name: 'Updated Test' }),
        rollbackFn
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      act(() => {
        result.current.rollback();
      });

      expect(globalCache.set).toHaveBeenCalledWith('test:data', originalData);
      expect(rollbackFn).toHaveBeenCalledWith(originalData);
    });
  });

  describe('Timeout automático', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('deve executar rollback automático após timeout', async () => {
      const originalData = { id: 1, name: 'Test' };
      (globalCache.get as jest.Mock).mockReturnValue(originalData);

      const config = {
        cacheKey: 'test:data',
        updateFn: (data: any) => ({ ...data, name: 'Optimistic Update' }),
        timeout: 1000
      };

      const { result } = renderHook(() => useOptimisticUpdate(config));

      const mockApiCall = jest.fn().mockImplementation(() => {
        return new Promise((resolve) => {
          setTimeout(() => resolve({ id: 1, name: 'Final Update' }), 2000);
        });
      });

      act(() => {
        result.current.execute(mockApiCall);
      });

      // Avançar o tempo para o timeout
      act(() => {
        jest.advanceTimersByTime(1000);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Timeout: Rollback automático executado');
      expect(globalCache.set).toHaveBeenCalledWith('test:data', originalData);
    });
  });
});

describe('useOptimisticListUpdate', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deve atualizar item específico na lista', async () => {
    const originalList = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' },
      { id: 3, name: 'Item 3' }
    ];

    (globalCache.get as jest.Mock).mockReturnValue(originalList);

    const { result } = renderHook(() => useOptimisticListUpdate('test:list', 2));

    const mockApiCall = jest.fn().mockResolvedValue({ id: 2, name: 'Updated Item 2' });

    await act(async () => {
      await result.current.execute(mockApiCall);
    });

    // Verificar se o item correto foi marcado como otimista
    const optimisticList = (globalCache.set as jest.Mock).mock.calls[0][1];
    expect(optimisticList[1].isOptimistic).toBe(true);
    expect(optimisticList[1].id).toBe(2);
  });

  it('deve fazer rollback removendo flag otimista', () => {
    const originalList = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2', isOptimistic: true },
      { id: 3, name: 'Item 3' }
    ];

    (globalCache.get as jest.Mock).mockReturnValue(originalList);

    const { result } = renderHook(() => useOptimisticListUpdate('test:list', 2));

    act(() => {
      result.current.rollback();
    });

    const rolledBackList = (globalCache.set as jest.Mock).mock.calls[0][1];
    expect(rolledBackList[1].isOptimistic).toBeUndefined();
  });
});

describe('useOptimisticCreate', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deve adicionar item temporário no início da lista', async () => {
    const originalList = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' }
    ];

    (globalCache.get as jest.Mock).mockReturnValue(originalList);

    const { result } = renderHook(() => useOptimisticCreate('test:list'));

    const mockApiCall = jest.fn().mockResolvedValue({ id: 3, name: 'New Item' });

    await act(async () => {
      await result.current.execute(mockApiCall);
    });

    // Verificar se item temporário foi adicionado
    const optimisticList = (globalCache.set as jest.Mock).mock.calls[0][1];
    expect(optimisticList[0].isOptimistic).toBe(true);
    expect(optimisticList[0].id).toMatch(/^temp_\d+$/);
    expect(optimisticList.length).toBe(3);
  });

  it('deve fazer rollback removendo item temporário', () => {
    const originalList = [
      { id: 'temp_123', name: 'Temp Item', isOptimistic: true },
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' }
    ];

    (globalCache.get as jest.Mock).mockReturnValue(originalList);

    const { result } = renderHook(() => useOptimisticCreate('test:list'));

    act(() => {
      result.current.rollback();
    });

    const rolledBackList = (globalCache.set as jest.Mock).mock.calls[0][1];
    expect(rolledBackList.length).toBe(2);
    expect(rolledBackList[0].id).toBe(1);
  });
});

describe('useOptimisticDelete', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('deve remover item da lista imediatamente', async () => {
    const originalList = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' },
      { id: 3, name: 'Item 3' }
    ];

    (globalCache.get as jest.Mock).mockReturnValue(originalList);

    const { result } = renderHook(() => useOptimisticDelete('test:list'));

    const mockApiCall = jest.fn().mockResolvedValue({ success: true });

    await act(async () => {
      await result.current.execute(mockApiCall);
    });

    // Verificar se item foi removido otimisticamente
    const optimisticList = (globalCache.set as jest.Mock).mock.calls[0][1];
    expect(optimisticList.length).toBe(2);
    expect(optimisticList.find((item: any) => item.id === 2)).toBeUndefined();
  });

  it('deve fazer rollback restaurando lista original', () => {
    const originalList = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' },
      { id: 3, name: 'Item 3' }
    ];

    (globalCache.get as jest.Mock).mockReturnValue(originalList);

    const { result } = renderHook(() => useOptimisticDelete('test:list'));

    act(() => {
      result.current.rollback();
    });

    const rolledBackList = (globalCache.set as jest.Mock).mock.calls[0][1];
    expect(rolledBackList).toEqual(originalList);
  });
}); 