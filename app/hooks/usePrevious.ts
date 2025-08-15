/**
 * usePrevious.ts
 * 
 * Hook para acessar o valor anterior de uma variável
 * 
 * Tracing ID: HOOK-004
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { useRef, useEffect } from 'react';

export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}

export function usePreviousWithComparison<T>(
  value: T,
  compareFn?: (prev: T | undefined, current: T) => boolean
): T | undefined {
  const ref = useRef<T>();
  const prevRef = useRef<T | undefined>();

  useEffect(() => {
    const shouldUpdate = compareFn ? compareFn(prevRef.current, value) : true;
    
    if (shouldUpdate) {
      prevRef.current = ref.current;
      ref.current = value;
    }
  }, [value, compareFn]);

  return prevRef.current;
}

export function usePreviousArray<T>(values: T[]): T[] {
  const ref = useRef<T[]>([]);

  useEffect(() => {
    ref.current = values;
  }, [values]);

  return ref.current;
}

export default usePrevious; 