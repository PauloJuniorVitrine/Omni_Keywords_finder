/**
 * useDebounce.ts
 * 
 * Hook para debounce de valores
 * 
 * Tracing ID: HOOK-002
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export interface DebounceConfig {
  delay: number;
  leading?: boolean;
  trailing?: boolean;
  maxWait?: number;
}

export function useDebounce<T>(
  value: T,
  delay: number = 500,
  config?: Partial<DebounceConfig>
): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastCallRef = useRef<number>(0);
  const lastValueRef = useRef<T>(value);

  const {
    leading = false,
    trailing = true,
    maxWait,
  } = config || {};

  useEffect(() => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCallRef.current;

    // Se é a primeira chamada e leading é true, atualizar imediatamente
    if (leading && lastCallRef.current === 0) {
      setDebouncedValue(value);
      lastValueRef.current = value;
    }

    // Limpar timeout anterior
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Verificar se maxWait foi excedido
    if (maxWait && timeSinceLastCall >= maxWait) {
      setDebouncedValue(value);
      lastValueRef.current = value;
      lastCallRef.current = now;
      return;
    }

    // Configurar novo timeout
    timeoutRef.current = setTimeout(() => {
      if (trailing) {
        setDebouncedValue(value);
        lastValueRef.current = value;
      }
      lastCallRef.current = Date.now();
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, delay, leading, trailing, maxWait]);

  return debouncedValue;
}

export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 500,
  config?: Partial<DebounceConfig>
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastCallRef = useRef<number>(0);
  const lastArgsRef = useRef<Parameters<T>>();

  const {
    leading = false,
    trailing = true,
    maxWait,
  } = config || {};

  const debouncedCallback = useCallback((...args: Parameters<T>) => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCallRef.current;

    // Se é a primeira chamada e leading é true, executar imediatamente
    if (leading && lastCallRef.current === 0) {
      callback(...args);
    }

    // Salvar argumentos
    lastArgsRef.current = args;

    // Limpar timeout anterior
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Verificar se maxWait foi excedido
    if (maxWait && timeSinceLastCall >= maxWait) {
      callback(...args);
      lastCallRef.current = now;
      return;
    }

    // Configurar novo timeout
    timeoutRef.current = setTimeout(() => {
      if (trailing && lastArgsRef.current) {
        callback(...lastArgsRef.current);
      }
      lastCallRef.current = Date.now();
    }, delay);
  }, [callback, delay, leading, trailing, maxWait]) as T;

  return debouncedCallback;
}

export function useDebouncedState<T>(
  initialValue: T,
  delay: number = 500,
  config?: Partial<DebounceConfig>
): [T, T, (value: T) => void] {
  const [value, setValue] = useState<T>(initialValue);
  const debouncedValue = useDebounce(value, delay, config);

  return [value, debouncedValue, setValue];
}

export default useDebounce; 