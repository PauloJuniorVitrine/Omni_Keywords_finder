/**
 * useTimeout.ts
 * 
 * Hook para timeout customizado
 * 
 * Tracing ID: HOOK-006
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { useRef, useCallback, useEffect } from 'react';
import { useState } from 'react';

export function useTimeout(callback: () => void, delay: number | null) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  const set = useCallback(() => {
    if (delay !== null) {
      timeoutRef.current = setTimeout(() => savedCallback.current(), delay);
    }
  }, [delay]);

  const clear = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    clear();
    set();
  }, [clear, set]);

  useEffect(() => {
    if (delay !== null) {
      set();
      return clear;
    }
  }, [delay, set, clear]);

  return { set, clear, reset };
}

export function useTimeoutWithState(callback: () => void, delay: number | null) {
  const [isActive, setIsActive] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  const set = useCallback(() => {
    if (delay !== null) {
      setIsActive(true);
      timeoutRef.current = setTimeout(() => {
        savedCallback.current();
        setIsActive(false);
      }, delay);
    }
  }, [delay]);

  const clear = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
      setIsActive(false);
    }
  }, []);

  const reset = useCallback(() => {
    clear();
    set();
  }, [clear, set]);

  useEffect(() => {
    if (delay !== null) {
      set();
      return clear;
    }
  }, [delay, set, clear]);

  return { isActive, set, clear, reset };
}

export function useTimeoutWithDependencies(
  callback: () => void,
  delay: number | null,
  dependencies: any[] = []
) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  const set = useCallback(() => {
    if (delay !== null) {
      timeoutRef.current = setTimeout(() => savedCallback.current(), delay);
    }
  }, [delay]);

  const clear = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    clear();
    set();
  }, [clear, set]);

  useEffect(() => {
    if (delay !== null) {
      set();
      return clear;
    }
  }, [delay, set, clear, ...dependencies]);

  return { set, clear, reset };
}

export default useTimeout; 