/**
 * useIntersectionObserver.ts
 * 
 * Hook para Intersection Observer API
 * 
 * Tracing ID: HOOK-003
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { useState, useEffect, useRef, useCallback, RefObject } from 'react';

export interface IntersectionObserverConfig {
  root?: Element | null;
  rootMargin?: string;
  threshold?: number | number[];
}

export interface IntersectionObserverState {
  isIntersecting: boolean;
  intersectionRatio: number;
  intersectionRect: DOMRectReadOnly | null;
  boundingClientRect: DOMRectReadOnly | null;
  rootBounds: DOMRectReadOnly | null;
  target: Element | null;
  time: number;
}

export function useIntersectionObserver(
  targetRef: RefObject<Element>,
  config?: IntersectionObserverConfig
): IntersectionObserverState {
  const [state, setState] = useState<IntersectionObserverState>({
    isIntersecting: false,
    intersectionRatio: 0,
    intersectionRect: null,
    boundingClientRect: null,
    rootBounds: null,
    target: null,
    time: 0,
  });

  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const target = targetRef.current;
    if (!target) return;

    const handleIntersection = (entries: IntersectionObserverEntry[]) => {
      const entry = entries[0];
      if (entry) {
        setState({
          isIntersecting: entry.isIntersecting,
          intersectionRatio: entry.intersectionRatio,
          intersectionRect: entry.intersectionRect,
          boundingClientRect: entry.boundingClientRect,
          rootBounds: entry.rootBounds,
          target: entry.target,
          time: entry.time,
        });
      }
    };

    const observer = new IntersectionObserver(handleIntersection, {
      root: config?.root || null,
      rootMargin: config?.rootMargin || '0px',
      threshold: config?.threshold || 0,
    });

    observer.observe(target);
    observerRef.current = observer;

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [targetRef, config?.root, config?.rootMargin, config?.threshold]);

  return state;
}

export function useLazyLoad<T>(
  targetRef: RefObject<Element>,
  loadFunction: () => Promise<T>,
  config?: IntersectionObserverConfig
): { data: T | null; loading: boolean; error: Error | null; trigger: () => void } {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [hasTriggered, setHasTriggered] = useState(false);

  const { isIntersecting } = useIntersectionObserver(targetRef, config);

  const trigger = useCallback(async () => {
    if (loading || hasTriggered) return;

    setLoading(true);
    setError(null);
    setHasTriggered(true);

    try {
      const result = await loadFunction();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [loadFunction, loading, hasTriggered]);

  useEffect(() => {
    if (isIntersecting && !hasTriggered) {
      trigger();
    }
  }, [isIntersecting, trigger, hasTriggered]);

  return { data, loading, error, trigger };
}

export function useInfiniteScroll<T>(
  targetRef: RefObject<Element>,
  loadMoreFunction: () => Promise<T[]>,
  config?: IntersectionObserverConfig
): { 
  items: T[]; 
  loading: boolean; 
  error: Error | null; 
  hasMore: boolean;
  loadMore: () => void;
  reset: () => void;
} {
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);

  const { isIntersecting } = useIntersectionObserver(targetRef, config);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    setError(null);

    try {
      const newItems = await loadMoreFunction();
      
      if (newItems.length === 0) {
        setHasMore(false);
      } else {
        setItems(prev => [...prev, ...newItems]);
        setPage(prev => prev + 1);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [loadMoreFunction, loading, hasMore]);

  const reset = useCallback(() => {
    setItems([]);
    setLoading(false);
    setError(null);
    setHasMore(true);
    setPage(1);
  }, []);

  useEffect(() => {
    if (isIntersecting && hasMore && !loading) {
      loadMore();
    }
  }, [isIntersecting, hasMore, loading, loadMore]);

  return { items, loading, error, hasMore, loadMore, reset };
}

export function useVisibilityTrigger(
  targetRef: RefObject<Element>,
  threshold: number = 0.5,
  config?: Omit<IntersectionObserverConfig, 'threshold'>
): { isVisible: boolean; visibilityRatio: number } {
  const { isIntersecting, intersectionRatio } = useIntersectionObserver(targetRef, {
    ...config,
    threshold,
  });

  return {
    isVisible: isIntersecting && intersectionRatio >= threshold,
    visibilityRatio: intersectionRatio,
  };
}

export default useIntersectionObserver; 