/**
 * usePrevious.test.ts
 * 
 * Testes unitários para o hook usePrevious
 * 
 * Tracing ID: TEST-USE-PREVIOUS-001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { renderHook, act } from '@testing-library/react';
import { 
  usePrevious, 
  usePreviousWithComparison, 
  usePreviousArray 
} from '../../app/hooks/usePrevious';

describe('usePrevious Hook', () => {
  describe('usePrevious - Hook Principal', () => {
    it('deve retornar undefined na primeira renderização', () => {
      const { result } = renderHook(() => usePrevious('initial'));

      expect(result.current).toBeUndefined();
    });

    it('deve retornar valor anterior após mudança', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 'initial' } }
      );

      expect(result.current).toBeUndefined();

      rerender({ value: 'changed' });
      expect(result.current).toBe('initial');

      rerender({ value: 'final' });
      expect(result.current).toBe('changed');
    });

    it('deve funcionar com diferentes tipos de dados', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 0 } }
      );

      rerender({ value: 42 });
      expect(result.current).toBe(0);

      rerender({ value: 100 });
      expect(result.current).toBe(42);
    });

    it('deve funcionar com objetos', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: { count: 0 } } }
      );

      rerender({ value: { count: 1 } });
      expect(result.current).toEqual({ count: 0 });

      rerender({ value: { count: 2 } });
      expect(result.current).toEqual({ count: 1 });
    });

    it('deve funcionar com arrays', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: [1, 2, 3] } }
      );

      rerender({ value: [4, 5, 6] });
      expect(result.current).toEqual([1, 2, 3]);

      rerender({ value: [7, 8, 9] });
      expect(result.current).toEqual([4, 5, 6]);
    });

    it('deve funcionar com valores null e undefined', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: null } }
      );

      rerender({ value: undefined });
      expect(result.current).toBe(null);

      rerender({ value: 'string' });
      expect(result.current).toBeUndefined();
    });
  });

  describe('usePreviousWithComparison - Hook com Comparação', () => {
    it('deve usar função de comparação customizada', () => {
      const compareFn = jest.fn((prev, current) => current > 10);

      const { result, rerender } = renderHook(
        ({ value }) => usePreviousWithComparison(value, compareFn),
        { initialProps: { value: 5 } }
      );

      expect(result.current).toBeUndefined();

      rerender({ value: 15 });
      expect(compareFn).toHaveBeenCalledWith(undefined, 15);
      expect(result.current).toBe(5);

      rerender({ value: 20 });
      expect(result.current).toBe(15);
    });

    it('deve atualizar apenas quando comparação retorna true', () => {
      const compareFn = jest.fn((prev, current) => current % 2 === 0);

      const { result, rerender } = renderHook(
        ({ value }) => usePreviousWithComparison(value, compareFn),
        { initialProps: { value: 1 } }
      );

      rerender({ value: 2 }); // Par - deve atualizar
      expect(result.current).toBe(1);

      rerender({ value: 3 }); // Ímpar - não deve atualizar
      expect(result.current).toBe(1); // Mantém o valor anterior

      rerender({ value: 4 }); // Par - deve atualizar
      expect(result.current).toBe(3);
    });

    it('deve funcionar sem função de comparação', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePreviousWithComparison(value),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'changed' });
      expect(result.current).toBe('initial');
    });

    it('deve comparar objetos profundamente', () => {
      const compareFn = jest.fn((prev, current) => 
        JSON.stringify(prev) !== JSON.stringify(current)
      );

      const { result, rerender } = renderHook(
        ({ value }) => usePreviousWithComparison(value, compareFn),
        { initialProps: { value: { id: 1, name: 'test' } } }
      );

      rerender({ value: { id: 1, name: 'test' } }); // Mesmo objeto
      expect(result.current).toBeUndefined();

      rerender({ value: { id: 2, name: 'test' } }); // Objeto diferente
      expect(result.current).toEqual({ id: 1, name: 'test' });
    });
  });

  describe('usePreviousArray - Hook para Arrays', () => {
    it('deve retornar array vazio na primeira renderização', () => {
      const { result } = renderHook(() => usePreviousArray([1, 2, 3]));

      expect(result.current).toEqual([]);
    });

    it('deve retornar array anterior após mudança', () => {
      const { result, rerender } = renderHook(
        ({ values }) => usePreviousArray(values),
        { initialProps: { values: [1, 2, 3] } }
      );

      expect(result.current).toEqual([]);

      rerender({ values: [4, 5, 6] });
      expect(result.current).toEqual([1, 2, 3]);

      rerender({ values: [7, 8, 9] });
      expect(result.current).toEqual([4, 5, 6]);
    });

    it('deve funcionar com arrays vazios', () => {
      const { result, rerender } = renderHook(
        ({ values }) => usePreviousArray(values),
        { initialProps: { values: [] } }
      );

      expect(result.current).toEqual([]);

      rerender({ values: [1, 2, 3] });
      expect(result.current).toEqual([]);

      rerender({ values: [] });
      expect(result.current).toEqual([1, 2, 3]);
    });

    it('deve funcionar com arrays de objetos', () => {
      const { result, rerender } = renderHook(
        ({ values }) => usePreviousArray(values),
        { initialProps: { values: [{ id: 1 }, { id: 2 }] } }
      );

      rerender({ values: [{ id: 3 }, { id: 4 }] });
      expect(result.current).toEqual([{ id: 1 }, { id: 2 }]);
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com mudanças frequentes', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 0 } }
      );

      // Múltiplas mudanças rápidas
      for (let i = 1; i <= 10; i++) {
        rerender({ value: i });
        expect(result.current).toBe(i - 1);
      }
    });

    it('deve lidar com valores muito grandes', () => {
      const largeValue = Array(10000).fill('test');
      
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: largeValue } }
      );

      const newLargeValue = Array(10000).fill('changed');
      rerender({ value: newLargeValue });
      expect(result.current).toEqual(largeValue);
    });

    it('deve lidar com valores circulares', () => {
      const circularObj: any = { name: 'test' };
      circularObj.self = circularObj;

      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: circularObj } }
      );

      const newCircularObj: any = { name: 'changed' };
      newCircularObj.self = newCircularObj;
      
      rerender({ value: newCircularObj });
      expect(result.current).toBe(circularObj);
    });

    it('deve lidar com valores undefined e null', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: undefined } }
      );

      rerender({ value: null });
      expect(result.current).toBeUndefined();

      rerender({ value: 'string' });
      expect(result.current).toBeNull();
    });
  });

  describe('Integração com React', () => {
    it('deve manter estado entre re-renders', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'changed' });
      expect(result.current).toBe('initial');

      // Re-render sem mudança
      rerender({ value: 'changed' });
      expect(result.current).toBe('initial');
    });

    it('deve limpar referências ao desmontar', () => {
      const { result, unmount } = renderHook(() => usePrevious('test'));

      expect(result.current).toBeUndefined();

      unmount();
      // Não deve causar erros
    });

    it('deve funcionar com múltiplas instâncias', () => {
      const { result: result1, rerender: rerender1 } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 'first' } }
      );

      const { result: result2, rerender: rerender2 } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 'second' } }
      );

      rerender1({ value: 'first-changed' });
      rerender2({ value: 'second-changed' });

      expect(result1.current).toBe('first');
      expect(result2.current).toBe('second');
    });
  });

  describe('Performance', () => {
    it('deve ser eficiente com mudanças frequentes', () => {
      const startTime = performance.now();
      
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 0 } }
      );

      // 1000 mudanças rápidas
      for (let i = 1; i <= 1000; i++) {
        rerender({ value: i });
        expect(result.current).toBe(i - 1);
      }

      const endTime = performance.now();
      const duration = endTime - startTime;
      
      // Deve completar em menos de 100ms
      expect(duration).toBeLessThan(100);
    });

    it('deve usar useRef eficientemente', () => {
      const { result, rerender } = renderHook(
        ({ value }) => usePrevious(value),
        { initialProps: { value: 'test' } }
      );

      // Verificar se não há re-renders desnecessários
      const initialRenderCount = 1;
      let renderCount = initialRenderCount;

      rerender({ value: 'changed' });
      renderCount++;

      rerender({ value: 'changed' }); // Mesmo valor
      renderCount++;

      expect(result.current).toBe('test');
      // Deve ter apenas 2 renders (inicial + mudança)
      expect(renderCount).toBe(2);
    });
  });
}); 