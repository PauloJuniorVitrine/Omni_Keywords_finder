/**
 * useToggle.ts
 * 
 * Hook para toggle de estado
 * 
 * Tracing ID: HOOK-005
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { useState, useCallback } from 'react';

export function useToggle(initialValue: boolean = false): [boolean, () => void, (value: boolean) => void] {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);

  return [value, toggle, setValue];
}

export function useToggleWithValues<T>(values: [T, T], initialIndex: number = 0): [T, () => void, (value: T) => void] {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  const toggle = useCallback(() => {
    setCurrentIndex(prev => (prev === 0 ? 1 : 0));
  }, []);

  const setValue = useCallback((value: T) => {
    const index = values.indexOf(value);
    if (index !== -1) {
      setCurrentIndex(index);
    }
  }, [values]);

  return [values[currentIndex], toggle, setValue];
}

export function useToggleArray<T>(values: T[], initialIndex: number = 0): [T, () => void, (index: number) => void] {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  const toggle = useCallback(() => {
    setCurrentIndex(prev => (prev + 1) % values.length);
  }, [values.length]);

  const setIndex = useCallback((index: number) => {
    if (index >= 0 && index < values.length) {
      setCurrentIndex(index);
    }
  }, [values.length]);

  return [values[currentIndex], toggle, setIndex];
}

export function useToggleWithReset<T>(initialValue: T, alternateValue: T): [T, () => void, () => void] {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue(prev => prev === initialValue ? alternateValue : initialValue);
  }, [initialValue, alternateValue]);

  const reset = useCallback(() => {
    setValue(initialValue);
  }, [initialValue]);

  return [value, toggle, reset];
}

export default useToggle; 