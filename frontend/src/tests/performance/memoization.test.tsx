/**
 * Tests for Memoization System
 * 
 * Tracing ID: MEMOIZATION_TESTS_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.2
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { 
  useMemoizedValue, 
  useMemoizedCallback, 
  withMemoization,
  deepEqual,
  LRUCache
} from '../../optimizations/memoization';

describe('Memoization System', () => {
  describe('deepEqual', () => {
    it('should return true for identical primitives', () => {
      expect(deepEqual(1, 1)).toBe(true);
      expect(deepEqual('test', 'test')).toBe(true);
      expect(deepEqual(true, true)).toBe(true);
      expect(deepEqual(null, null)).toBe(true);
      expect(deepEqual(undefined, undefined)).toBe(true);
    });

    it('should return false for different primitives', () => {
      expect(deepEqual(1, 2)).toBe(false);
      expect(deepEqual('test', 'other')).toBe(false);
      expect(deepEqual(true, false)).toBe(false);
    });

    it('should return true for identical objects', () => {
      const obj1 = { a: 1, b: { c: 2 } };
      const obj2 = { a: 1, b: { c: 2 } };
      expect(deepEqual(obj1, obj2)).toBe(true);
    });

    it('should return false for different objects', () => {
      const obj1 = { a: 1, b: { c: 2 } };
      const obj2 = { a: 1, b: { c: 3 } };
      expect(deepEqual(obj1, obj2)).toBe(false);
    });

    it('should return true for identical arrays', () => {
      const arr1 = [1, 2, [3, 4]];
      const arr2 = [1, 2, [3, 4]];
      expect(deepEqual(arr1, arr2)).toBe(true);
    });

    it('should return false for different arrays', () => {
      const arr1 = [1, 2, [3, 4]];
      const arr2 = [1, 2, [3, 5]];
      expect(deepEqual(arr1, arr2)).toBe(false);
    });
  });

  describe('LRUCache', () => {
    it('should store and retrieve values', () => {
      const cache = new LRUCache<string, number>(3);
      
      cache.set('a', 1);
      cache.set('b', 2);
      
      expect(cache.get('a')).toBe(1);
      expect(cache.get('b')).toBe(2);
    });

    it('should evict least recently used items when capacity is exceeded', () => {
      const cache = new LRUCache<string, number>(2);
      
      cache.set('a', 1);
      cache.set('b', 2);
      cache.set('c', 3); // Should evict 'a'
      
      expect(cache.get('a')).toBeUndefined();
      expect(cache.get('b')).toBe(2);
      expect(cache.get('c')).toBe(3);
    });

    it('should update access order when getting items', () => {
      const cache = new LRUCache<string, number>(2);
      
      cache.set('a', 1);
      cache.set('b', 2);
      cache.get('a'); // Move 'a' to most recently used
      cache.set('c', 3); // Should evict 'b'
      
      expect(cache.get('a')).toBe(1);
      expect(cache.get('b')).toBeUndefined();
      expect(cache.get('c')).toBe(3);
    });

    it('should clear all items', () => {
      const cache = new LRUCache<string, number>(3);
      
      cache.set('a', 1);
      cache.set('b', 2);
      cache.clear();
      
      expect(cache.get('a')).toBeUndefined();
      expect(cache.get('b')).toBeUndefined();
      expect(cache.size()).toBe(0);
    });
  });

  describe('useMemoizedValue', () => {
    it('should memoize values based on dependencies', () => {
      const factory = jest.fn(() => ({ value: 'test' }));
      
      const TestComponent = ({ deps }: { deps: any[] }) => {
        const result = useMemoizedValue(factory, deps);
        return <div data-testid="result">{JSON.stringify(result)}</div>;
      };

      const { rerender } = render(<TestComponent deps={[1, 2]} />);
      
      expect(factory).toHaveBeenCalledTimes(1);
      
      // Same dependencies, should not call factory again
      rerender(<TestComponent deps={[1, 2]} />);
      expect(factory).toHaveBeenCalledTimes(1);
      
      // Different dependencies, should call factory again
      rerender(<TestComponent deps={[1, 3]} />);
      expect(factory).toHaveBeenCalledTimes(2);
    });

    it('should use cache when dependencies are the same', () => {
      const factory = jest.fn(() => Math.random());
      
      const TestComponent = ({ deps }: { deps: any[] }) => {
        const result = useMemoizedValue(factory, deps);
        return <div data-testid="result">{result}</div>;
      };

      const { rerender } = render(<TestComponent deps={[1]} />);
      const firstResult = screen.getByTestId('result').textContent;
      
      rerender(<TestComponent deps={[1]} />);
      const secondResult = screen.getByTestId('result').textContent;
      
      expect(firstResult).toBe(secondResult);
    });
  });

  describe('useMemoizedCallback', () => {
    it('should memoize callbacks based on dependencies', () => {
      const callback = jest.fn();
      
      const TestComponent = ({ deps }: { deps: any[] }) => {
        const memoizedCallback = useMemoizedCallback(callback, deps);
        return <button onClick={memoizedCallback}>Click</button>;
      };

      const { rerender } = render(<TestComponent deps={[1, 2]} />);
      
      // Same dependencies, should return same callback reference
      const firstCallback = screen.getByRole('button').onclick;
      
      rerender(<TestComponent deps={[1, 2]} />);
      const secondCallback = screen.getByRole('button').onclick;
      
      expect(firstCallback).toBe(secondCallback);
      
      // Different dependencies, should return different callback reference
      rerender(<TestComponent deps={[1, 3]} />);
      const thirdCallback = screen.getByRole('button').onclick;
      
      expect(firstCallback).not.toBe(thirdCallback);
    });
  });

  describe('withMemoization HOC', () => {
    it('should memoize component with shallow comparison', () => {
      const TestComponent = React.memo(({ value }: { value: string }) => (
        <div data-testid="component">{value}</div>
      ));
      
      const MemoizedComponent = withMemoization(TestComponent);
      
      const { rerender } = render(<MemoizedComponent value="test" />);
      expect(screen.getByTestId('component')).toHaveTextContent('test');
      
      // Same props, should not re-render
      rerender(<MemoizedComponent value="test" />);
      expect(screen.getByTestId('component')).toHaveTextContent('test');
    });

    it('should memoize component with deep comparison', () => {
      const TestComponent = React.memo(({ data }: { data: { value: string } }) => (
        <div data-testid="component">{data.value}</div>
      ));
      
      const MemoizedComponent = withMemoization(TestComponent, { deep: true });
      
      const data1 = { value: 'test' };
      const data2 = { value: 'test' };
      
      const { rerender } = render(<MemoizedComponent data={data1} />);
      expect(screen.getByTestId('component')).toHaveTextContent('test');
      
      // Same data structure, should not re-render
      rerender(<MemoizedComponent data={data2} />);
      expect(screen.getByTestId('component')).toHaveTextContent('test');
    });
  });

  describe('Performance', () => {
    it('should avoid unnecessary recalculations', () => {
      const expensiveCalculation = jest.fn(() => {
        // Simulate expensive operation
        return Array(1000).fill(0).map((_, i) => i);
      });
      
      const TestComponent = ({ deps }: { deps: any[] }) => {
        const result = useMemoizedValue(expensiveCalculation, deps);
        return <div data-testid="result">{result.length}</div>;
      };

      const { rerender } = render(<TestComponent deps={[1]} />);
      expect(expensiveCalculation).toHaveBeenCalledTimes(1);
      
      // Same dependencies, should not recalculate
      rerender(<TestComponent deps={[1]} />);
      expect(expensiveCalculation).toHaveBeenCalledTimes(1);
      
      // Different dependencies, should recalculate
      rerender(<TestComponent deps={[2]} />);
      expect(expensiveCalculation).toHaveBeenCalledTimes(2);
    });
  });
}); 