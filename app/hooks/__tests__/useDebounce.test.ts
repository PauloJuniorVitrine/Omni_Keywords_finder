/**
 * Testes para useDebounce Hook
 * 
 * Prompt: Implementação de testes para hooks críticos
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USE_DEBOUNCE_001
 * 
 * Testes baseados APENAS no código real do useDebounce.ts
 */

import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '../useDebounce';

describe('useDebounce Hook', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Funcionalidade Básica', () => {
    it('deve retornar valor inicial imediatamente', () => {
      const initialValue = 'initial value';
      
      const { result } = renderHook(() => useDebounce(initialValue, 500));

      expect(result.current).toBe(initialValue);
    });

    it('deve debounce mudanças de valor', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      // Mudança 1
      rerender({ value: 'changed 1', delay: 500 });
      expect(result.current).toBe('initial');

      // Avançar tempo parcialmente
      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe('initial');

      // Mudança 2 (deve resetar o timer)
      rerender({ value: 'changed 2', delay: 500 });
      expect(result.current).toBe('initial');

      // Avançar tempo completo
      act(() => {
        jest.advanceTimersByTime(500);
      });
      expect(result.current).toBe('changed 2');
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
  });

  describe('Diferentes Tipos de Valores', () => {
    it('deve debounce strings', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'hello', delay: 300 } }
      );

      rerender({ value: 'world', delay: 300 });
      expect(result.current).toBe('hello');

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe('world');
    });

    it('deve debounce números', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 0, delay: 300 } }
      );

      rerender({ value: 42, delay: 300 });
      expect(result.current).toBe(0);

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe(42);
    });

    it('deve debounce objetos', () => {
      const initialObj = { name: 'John', age: 30 };
      const changedObj = { name: 'Jane', age: 25 };

      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: initialObj, delay: 300 } }
      );

      rerender({ value: changedObj, delay: 300 });
      expect(result.current).toEqual(initialObj);

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toEqual(changedObj);
    });

    it('deve debounce arrays', () => {
      const initialArray = [1, 2, 3];
      const changedArray = [4, 5, 6];

      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: initialArray, delay: 300 } }
      );

      rerender({ value: changedArray, delay: 300 });
      expect(result.current).toEqual(initialArray);

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toEqual(changedArray);
    });

    it('deve debounce valores booleanos', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: false, delay: 300 } }
      );

      rerender({ value: true, delay: 300 });
      expect(result.current).toBe(false);

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe(true);
    });
  });

  describe('Múltiplas Mudanças', () => {
    it('deve debounce múltiplas mudanças consecutivas', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      // Múltiplas mudanças rápidas
      rerender({ value: 'change 1', delay: 500 });
      rerender({ value: 'change 2', delay: 500 });
      rerender({ value: 'change 3', delay: 500 });
      rerender({ value: 'final', delay: 500 });

      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe('final');
    });

    it('deve resetar timer a cada mudança', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 1000 } }
      );

      // Primeira mudança
      rerender({ value: 'change 1', delay: 1000 });
      
      // Avançar 800ms (antes do timeout)
      act(() => {
        jest.advanceTimersByTime(800);
      });
      expect(result.current).toBe('initial');

      // Segunda mudança (deve resetar timer)
      rerender({ value: 'change 2', delay: 1000 });
      
      // Avançar 800ms novamente (ainda antes do timeout)
      act(() => {
        jest.advanceTimersByTime(800);
      });
      expect(result.current).toBe('initial');

      // Avançar 200ms restantes
      act(() => {
        jest.advanceTimersByTime(200);
      });
      expect(result.current).toBe('change 2');
    });
  });

  describe('Diferentes Delays', () => {
    it('deve respeitar delay de 100ms', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 100 } }
      );

      rerender({ value: 'changed', delay: 100 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(100);
      });
      expect(result.current).toBe('changed');
    });

    it('deve respeitar delay de 1000ms', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 1000 } }
      );

      rerender({ value: 'changed', delay: 1000 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(1000);
      });
      expect(result.current).toBe('changed');
    });

    it('deve funcionar com delay de 0ms', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 0 } }
      );

      rerender({ value: 'changed', delay: 0 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(0);
      });
      expect(result.current).toBe('changed');
    });
  });

  describe('Limpeza de Timer', () => {
    it('deve limpar timer quando componente é desmontado', () => {
      const clearTimeoutSpy = jest.spyOn(window, 'clearTimeout');

      const { unmount, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      rerender({ value: 'changed', delay: 500 });
      
      unmount();

      expect(clearTimeoutSpy).toHaveBeenCalled();
    });

    it('deve limpar timer anterior ao criar novo', () => {
      const clearTimeoutSpy = jest.spyOn(window, 'clearTimeout');

      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      rerender({ value: 'change 1', delay: 500 });
      rerender({ value: 'change 2', delay: 500 });

      expect(clearTimeoutSpy).toHaveBeenCalled();

      act(() => {
        jest.advanceTimersByTime(500);
      });
      expect(result.current).toBe('change 2');
    });
  });

  describe('Valores Especiais', () => {
    it('deve debounce valores null', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: null, delay: 300 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe(null);
    });

    it('deve debounce valores undefined', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: undefined, delay: 300 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe(undefined);
    });

    it('deve debounce valores vazios', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: '', delay: 300 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe('');
    });
  });

  describe('Integração useDebounce', () => {
    it('deve manter consistência durante mudanças complexas', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: { count: 0 }, delay: 500 } }
      );

      // Sequência de mudanças
      rerender({ value: { count: 1 }, delay: 500 });
      rerender({ value: { count: 2 }, delay: 500 });
      rerender({ value: { count: 3 }, delay: 500 });

      expect(result.current).toEqual({ count: 0 });

      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toEqual({ count: 3 });
    });

    it('deve lidar com mudanças de delay', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      rerender({ value: 'changed', delay: 300 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(result.current).toBe('changed');
    });
  });

  describe('Performance useDebounce', () => {
    it('deve evitar re-renders desnecessários', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      const initialValue = result.current;

      // Múltiplas mudanças sem avançar o tempo
      rerender({ value: 'change 1', delay: 500 });
      rerender({ value: 'change 2', delay: 500 });
      rerender({ value: 'change 3', delay: 500 });

      expect(result.current).toBe(initialValue);

      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe('change 3');
    });

    it('deve limpar timers eficientemente', () => {
      const clearTimeoutSpy = jest.spyOn(window, 'clearTimeout');

      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      // Múltiplas mudanças rápidas
      for (let i = 0; i < 10; i++) {
        rerender({ value: `change ${i}`, delay: 500 });
      }

      expect(clearTimeoutSpy).toHaveBeenCalledTimes(9); // Uma chamada para cada mudança exceto a primeira

      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(result.current).toBe('change 9');
    });
  });

  describe('Casos de Borda', () => {
    it('deve lidar com delay negativo', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: -100 } }
      );

      rerender({ value: 'changed', delay: -100 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(0);
      });
      expect(result.current).toBe('changed');
    });

    it('deve lidar com delay muito grande', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 10000 } }
      );

      rerender({ value: 'changed', delay: 10000 });
      expect(result.current).toBe('initial');

      act(() => {
        jest.advanceTimersByTime(10000);
      });
      expect(result.current).toBe('changed');
    });

    it('deve manter referência de objeto quando valor não muda', () => {
      const sameObject = { id: 1, name: 'John' };

      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: sameObject, delay: 500 } }
      );

      rerender({ value: sameObject, delay: 500 });
      expect(result.current).toBe(sameObject);

      act(() => {
        jest.advanceTimersByTime(500);
      });
      expect(result.current).toBe(sameObject);
    });
  });
}); 