/**
 * Lazy Loading System for Components
 * 
 * Tracing ID: LAZY_LOADING_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.1
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import React, { Suspense, lazy, useEffect, useRef, useState } from 'react';

// Types for lazy loading
export interface LazyLoadingOptions {
  threshold?: number;
  rootMargin?: string;
  fallback?: React.ReactNode;
  preload?: boolean;
}

export interface LazyComponentProps {
  children: React.ReactNode;
  options?: LazyLoadingOptions;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

// Default fallback component
const DefaultFallback: React.FC = () => (
  <div className="lazy-loading-fallback">
    <div className="spinner" />
    <span>Carregando...</span>
  </div>
);

// Intersection Observer hook for lazy loading
export const useLazyLoad = (options: LazyLoadingOptions = {}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const {
    threshold = 0.1,
    rootMargin = '50px',
    preload = false
  } = options;

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    // If preload is enabled, load immediately
    if (preload) {
      setIsVisible(true);
      setHasLoaded(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          setHasLoaded(true);
          observer.disconnect();
        }
      },
      {
        threshold,
        rootMargin
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [threshold, rootMargin, preload]);

  return {
    elementRef,
    isVisible,
    hasLoaded
  };
};

// Lazy loading wrapper component
export const LazyLoad: React.FC<LazyComponentProps> = ({
  children,
  options = {},
  onLoad,
  onError
}) => {
  const { elementRef, isVisible, hasLoaded } = useLazyLoad(options);
  const { fallback = <DefaultFallback /> } = options;

  useEffect(() => {
    if (hasLoaded && onLoad) {
      onLoad();
    }
  }, [hasLoaded, onLoad]);

  if (!isVisible) {
    return (
      <div ref={elementRef} className="lazy-loading-container">
        {fallback}
      </div>
    );
  }

  return (
    <div ref={elementRef} className="lazy-loaded-content">
      {children}
    </div>
  );
};

// Lazy loading for images
export const LazyImage: React.FC<{
  src: string;
  alt: string;
  className?: string;
  fallback?: string;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}> = ({ src, alt, className, fallback, onLoad, onError }) => {
  const [imageSrc, setImageSrc] = useState(fallback || '');
  const [isLoaded, setIsLoaded] = useState(false);
  const { elementRef, isVisible } = useLazyLoad();

  useEffect(() => {
    if (isVisible && src) {
      const img = new Image();
      img.src = src;
      
      img.onload = () => {
        setImageSrc(src);
        setIsLoaded(true);
        onLoad?.();
      };
      
      img.onerror = (error) => {
        onError?.(new Error(`Failed to load image: ${src}`));
      };
    }
  }, [isVisible, src, onLoad, onError]);

  return (
    <img
      ref={elementRef}
      src={imageSrc}
      alt={alt}
      className={`lazy-image ${isLoaded ? 'loaded' : 'loading'} ${className || ''}`}
    />
  );
};

// Lazy loading for components with React.lazy
export const createLazyComponent = <T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ReactNode
) => {
  const LazyComponent = lazy(importFunc);
  
  return (props: React.ComponentProps<T>) => (
    <Suspense fallback={fallback || <DefaultFallback />}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Preload utility for critical components
export const preloadComponent = <T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
) => {
  return () => {
    importFunc();
  };
};

// Lazy loading for routes
export const createLazyRoute = (
  importFunc: () => Promise<{ default: React.ComponentType<any> }>,
  fallback?: React.ReactNode
) => {
  return createLazyComponent(importFunc, fallback);
};

// Performance monitoring for lazy loading
export const useLazyLoadingMetrics = () => {
  const [metrics, setMetrics] = useState({
    totalComponents: 0,
    loadedComponents: 0,
    loadTimes: [] as number[],
    errors: [] as Error[]
  });

  const trackLoad = (loadTime: number) => {
    setMetrics(prev => ({
      ...prev,
      loadedComponents: prev.loadedComponents + 1,
      loadTimes: [...prev.loadTimes, loadTime]
    }));
  };

  const trackError = (error: Error) => {
    setMetrics(prev => ({
      ...prev,
      errors: [...prev.errors, error]
    }));
  };

  const getAverageLoadTime = () => {
    if (metrics.loadTimes.length === 0) return 0;
    return metrics.loadTimes.reduce((a, b) => a + b, 0) / metrics.loadTimes.length;
  };

  return {
    metrics,
    trackLoad,
    trackError,
    getAverageLoadTime
  };
};

export default {
  useLazyLoad,
  LazyLoad,
  LazyImage,
  createLazyComponent,
  preloadComponent,
  createLazyRoute,
  useLazyLoadingMetrics
}; 