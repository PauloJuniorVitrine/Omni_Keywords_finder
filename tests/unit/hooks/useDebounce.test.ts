/**
 * useDebounce.test.ts
 * 
 * Testes unitários para o hook useDebounce
 * 
 * Tracing ID: TEST-USE-DEBOUNCE-001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { renderHook, act } from '@testing-library/react';
import { useDebounce, useDebouncedCallback, useDebouncedState } from '../../app/hooks/useDebounce';

// Mock do setTimeout e clearTimeout
jest.useFakeTimers();

describe('useDebounce Hook', () => {
  beforeEach(() => {
    jest.clearAllTimers();
  });

  describe('useDebounce - Debounce de Valores', () => {
    it('deve retornar o valor inicial imediatamente', () => {
      const { result } = renderHook(() => useDebounce('initial', 500));

      expect(result.current).toBe('initial');
    });

    it('deve debounce mudanças de valor', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 500),
        { initialProps: { value: 'initial' } }
      );

      expect(result.current).toBe('initial');

      // Mudar valor rapidamente
      rerender({ value: 'changed1' });
      rerender({ value: 'changed2' });
      rerender({ value: 'final' });

      // Valor ainda deve ser o inicial
      expect(result.current).toBe('initial');

      // Avançar tempo
      act(() => {
        jest.advanceTimersByTime(500);
      });

      // Agora deve ser o valor final
      expect(result.current).toBe('final');
    });

    it('deve usar delay padrão de 500ms', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'changed' });

      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe('changed');
    });

    it('deve limpar timeout anterior ao mudar valor', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 1000),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'changed1' });

      // Avançar apenas 500ms (antes do timeout)
      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe('initial');

      // Mudar valor novamente
      rerender({ value: 'changed2' });

      // Avançar mais 500ms (total 1000ms)
      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe('changed2');
    });

    it('deve funcionar com configuração leading', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 500, { leading: true }),
        { initialProps: { value: 'initial' } }
      );

      // Com leading, deve atualizar imediatamente na primeira mudança
      rerender({ value: 'changed' });
      expect(result.current).toBe('changed');

      // Segunda mudança deve ser debounced
      rerender({ value: 'changed2' });
      expect(result.current).toBe('changed');

      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe('changed2');
    });

    it('deve funcionar com configuração trailing', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 500, { trailing: false }),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'changed' });

      act(() => {
        jest.advanceTimersByTime(500);
      });

      // Com trailing: false, não deve atualizar
      expect(result.current).toBe('initial');
    });

    it('deve funcionar com maxWait', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 1000, { maxWait: 2000 }),
        { initialProps: { value: 'initial' } }
      );

      // Mudar valor várias vezes
      rerender({ value: 'changed1' });
      rerender({ value: 'changed2' });
      rerender({ value: 'changed3' });

      // Avançar tempo além do maxWait
      act(() => {
        jest.advanceTimersByTime(2500);
      });

      expect(result.current).toBe('changed3');
    });

    it('deve funcionar com diferentes tipos de dados', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 100),
        { initialProps: { value: 0 } }
      );

      rerender({ value: 42 });

      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(result.current).toBe(42);

      // Testar com objeto
      rerender({ value: { count: 1 } });

      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(result.current).toEqual({ count: 1 });
    });
  });

  describe('useDebouncedCallback - Debounce de Funções', () => {
    it('deve debounce chamadas de função', () => {
      const mockFn = jest.fn();
      const { result } = renderHook(() => useDebouncedCallback(mockFn, 500));

      // Chamar função várias vezes rapidamente
      act(() => {
        result.current('arg1');
        result.current('arg2');
        result.current('arg3');
      });

      // Função não deve ter sido chamada ainda
      expect(mockFn).not.toHaveBeenCalled();

      // Avançar tempo
      act(() => {
        jest.advanceTimersByTime(500);
      });

      // Função deve ter sido chamada apenas uma vez com o último argumento
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('arg3');
    });

    it('deve funcionar com configuração leading', () => {
      const mockFn = jest.fn();
      const { result } = renderHook(() => 
        useDebouncedCallback(mockFn, 500, { leading: true })
      );

      // Primeira chamada deve executar imediatamente
      act(() => {
        result.current('first');
      });

      expect(mockFn).toHaveBeenCalledWith('first');

      // Segunda chamada deve ser debounced
      act(() => {
        result.current('second');
      });

      expect(mockFn).toHaveBeenCalledTimes(1);

      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(mockFn).toHaveBeenCalledTimes(2);
      expect(mockFn).toHaveBeenCalledWith('second');
    });

    it('deve funcionar com configuração trailing', () => {
      const mockFn = jest.fn();
      const { result } = renderHook(() => 
        useDebouncedCallback(mockFn, 500, { trailing: false })
      );

      act(() => {
        result.current('test');
      });

      act(() => {
        jest.advanceTimersByTime(500);
      });

      // Com trailing: false, função não deve ser chamada
      expect(mockFn).not.toHaveBeenCalled();
    });

    it('deve funcionar com maxWait', () => {
      const mockFn = jest.fn();
      const { result } = renderHook(() => 
        useDebouncedCallback(mockFn, 1000, { maxWait: 2000 })
      );

      // Chamar várias vezes
      act(() => {
        result.current('call1');
        result.current('call2');
        result.current('call3');
      });

      // Avançar tempo além do maxWait
      act(() => {
        jest.advanceTimersByTime(2500);
      });

      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('call3');
    });

    it('deve preservar contexto da função', () => {
      const mockFn = jest.fn(function(this: any) {
        return this.value;
      });
      
      const context = { value: 'test-context' };
      const boundFn = mockFn.bind(context);

      const { result } = renderHook(() => useDebouncedCallback(boundFn, 100));

      act(() => {
        result.current();
      });

      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(mockFn).toHaveBeenCalled();
    });
  });

  describe('useDebouncedState - Estado com Debounce', () => {
    it('deve retornar estado atual e debounced', () => {
      const { result } = renderHook(() => useDebouncedState('initial', 500));

      const [currentValue, debouncedValue, setValue] = result.current;

      expect(currentValue).toBe('initial');
      expect(debouncedValue).toBe('initial');
      expect(typeof setValue).toBe('function');
    });

    it('deve atualizar estado imediatamente mas debounce o valor debounced', () => {
      const { result } = renderHook(() => useDebouncedState('initial', 500));

      act(() => {
        result.current[2]('changed');
      });

      const [currentValue, debouncedValue] = result.current;

      expect(currentValue).toBe('changed');
      expect(debouncedValue).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(500);
      });

      const [currentValue2, debouncedValue2] = result.current;

      expect(currentValue2).toBe('changed');
      expect(debouncedValue2).toBe('changed');
    });

    it('deve funcionar com função de atualização', () => {
      const { result } = renderHook(() => useDebouncedState(0, 100));

      act(() => {
        result.current[2](prev => prev + 1);
      });

      expect(result.current[0]).toBe(1);
      expect(result.current[1]).toBe(0);

      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(result.current[0]).toBe(1);
      expect(result.current[1]).toBe(1);
    });

    it('deve funcionar com configuração customizada', () => {
      const { result } = renderHook(() => 
        useDebouncedState('initial', 500, { leading: true })
      );

      act(() => {
        result.current[2]('changed');
      });

      // Com leading, debounced value deve atualizar imediatamente
      expect(result.current[0]).toBe('changed');
      expect(result.current[1]).toBe('changed');
    });
  });

  describe('Limpeza de Timeouts', () => {
    it('deve limpar timeouts ao desmontar', () => {
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
      
      const { unmount } = renderHook(() => useDebounce('test', 1000));

      unmount();

      expect(clearTimeoutSpy).toHaveBeenCalled();
      
      clearTimeoutSpy.mockRestore();
    });

    it('deve limpar timeouts ao mudar dependências', () => {
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
      
      const { rerender } = renderHook(
        ({ delay }) => useDebounce('test', delay),
        { initialProps: { delay: 1000 } }
      );

      rerender({ delay: 2000 });

      expect(clearTimeoutSpy).toHaveBeenCalled();
      
      clearTimeoutSpy.mockRestore();
    });
  });

  describe('Casos Extremos', () => {
    it('deve funcionar com delay zero', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 0),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'changed' });

      // Com delay zero, deve atualizar imediatamente
      expect(result.current).toBe('changed');
    });

    it('deve funcionar com delay muito grande', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 10000),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'changed' });

      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(10000);
      });

      expect(result.current).toBe('changed');
    });

    it('deve funcionar com valores undefined e null', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value, 100),
        { initialProps: { value: undefined } }
      );

      rerender({ value: null });

      act(() => {
        jest.advanceTimersByTime(100);
      });

      expect(result.current).toBe(null);
    });
  });
}); 