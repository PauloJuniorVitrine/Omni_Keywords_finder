/**
 * Code Splitting System for Bundle Optimization
 * 
 * Tracing ID: CODE_SPLITTING_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.4
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import React, { Suspense, lazy, useEffect, useState, useRef } from 'react';

// Types for code splitting
export interface CodeSplittingOptions {
  fallback?: React.ReactNode;
  preload?: boolean;
  retry?: number;
  timeout?: number;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

export interface BundleInfo {
  name: string;
  size: number;
  loadTime: number;
  status: 'pending' | 'loading' | 'loaded' | 'error';
  error?: Error;
}

export interface CodeSplittingConfig {
  chunks: {
    [key: string]: () => Promise<{ default: React.ComponentType<any> }>;
  };
  preloadChunks?: string[];
  retryAttempts?: number;
  timeout?: number;
}

// Default fallback component
const DefaultFallback: React.FC = () => (
  <div className="code-splitting-fallback">
    <div className="spinner" />
    <span>Carregando módulo...</span>
  </div>
);

// Bundle loader with retry logic
export class BundleLoader {
  private static instance: BundleLoader;
  private bundles: Map<string, BundleInfo> = new Map();
  private retryAttempts: number;
  private timeout: number;

  constructor(retryAttempts: number = 3, timeout: number = 10000) {
    this.retryAttempts = retryAttempts;
    this.timeout = timeout;
  }

  static getInstance(): BundleLoader {
    if (!BundleLoader.instance) {
      BundleLoader.instance = new BundleLoader();
    }
    return BundleLoader.instance;
  }

  async loadBundle(
    name: string,
    importFn: () => Promise<{ default: React.ComponentType<any> }>,
    options: CodeSplittingOptions = {}
  ): Promise<{ default: React.ComponentType<any> }> {
    const { retry = this.retryAttempts, timeout = this.timeout } = options;
    
    // Check if already loaded
    const existing = this.bundles.get(name);
    if (existing?.status === 'loaded') {
      return importFn();
    }

    // Update status to loading
    this.bundles.set(name, {
      name,
      size: 0,
      loadTime: 0,
      status: 'loading'
    });

    const startTime = performance.now();
    let lastError: Error;

    for (let attempt = 0; attempt <= retry; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const result = await Promise.race([
          importFn(),
          new Promise<never>((_, reject) => {
            controller.signal.addEventListener('abort', () => {
              reject(new Error(`Bundle load timeout: ${name}`));
            });
          })
        ]);

        clearTimeout(timeoutId);
        
        const loadTime = performance.now() - startTime;
        
        this.bundles.set(name, {
          name,
          size: 0, // Would need to get actual bundle size
          loadTime,
          status: 'loaded'
        });

        options.onLoad?.();
        return result;

      } catch (error) {
        lastError = error as Error;
        
        if (attempt < retry) {
          // Wait before retry with exponential backoff
          await new Promise(resolve => 
            setTimeout(resolve, Math.pow(2, attempt) * 1000)
          );
        }
      }
    }

    // All retries failed
    this.bundles.set(name, {
      name,
      size: 0,
      loadTime: performance.now() - startTime,
      status: 'error',
      error: lastError
    });

    options.onError?.(lastError);
    throw lastError;
  }

  getBundleInfo(name: string): BundleInfo | undefined {
    return this.bundles.get(name);
  }

  getAllBundles(): BundleInfo[] {
    return Array.from(this.bundles.values());
  }

  preloadBundle(
    name: string,
    importFn: () => Promise<{ default: React.ComponentType<any> }>
  ): void {
    // Preload in background
    this.loadBundle(name, importFn).catch(() => {
      // Silent fail for preloading
    });
  }
}

// Hook for code splitting with loading state
export const useCodeSplitting = <T extends React.ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  options: CodeSplittingOptions = {}
) => {
  const [Component, setComponent] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const bundleLoader = BundleLoader.getInstance();

  const loadComponent = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await bundleLoader.loadBundle('dynamic', importFn, options);
      setComponent(() => result.default);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComponent();
  }, []);

  return { Component, loading, error, reload: loadComponent };
};

// HOC for code splitting
export const withCodeSplitting = <P extends object>(
  importFn: () => Promise<{ default: React.ComponentType<P> }>,
  options: CodeSplittingOptions = {}
) => {
  const LazyComponent = lazy(importFn);
  
  return (props: P) => (
    <Suspense fallback={options.fallback || <DefaultFallback />}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Route-based code splitting
export const createLazyRoute = (
  importFn: () => Promise<{ default: React.ComponentType<any> }>,
  options: CodeSplittingOptions = {}
) => {
  return withCodeSplitting(importFn, options);
};

// Component-based code splitting
export const createLazyComponent = <P extends object>(
  importFn: () => Promise<{ default: React.ComponentType<P> }>,
  options: CodeSplittingOptions = {}
) => {
  return withCodeSplitting(importFn, options);
};

// Feature-based code splitting
export class FeatureCodeSplitter {
  private features: Map<string, () => Promise<{ default: React.ComponentType<any> }>> = new Map();
  private bundleLoader: BundleLoader;

  constructor() {
    this.bundleLoader = BundleLoader.getInstance();
  }

  registerFeature(
    name: string,
    importFn: () => Promise<{ default: React.ComponentType<any> }>
  ): void {
    this.features.set(name, importFn);
  }

  async loadFeature(
    name: string,
    options: CodeSplittingOptions = {}
  ): Promise<React.ComponentType<any>> {
    const importFn = this.features.get(name);
    if (!importFn) {
      throw new Error(`Feature not registered: ${name}`);
    }

    const result = await this.bundleLoader.loadBundle(name, importFn, options);
    return result.default;
  }

  preloadFeature(name: string): void {
    const importFn = this.features.get(name);
    if (importFn) {
      this.bundleLoader.preloadBundle(name, importFn);
    }
  }

  getRegisteredFeatures(): string[] {
    return Array.from(this.features.keys());
  }
}

// Dynamic import with error boundary
export const DynamicImport: React.FC<{
  importFn: () => Promise<{ default: React.ComponentType<any> }>;
  fallback?: React.ReactNode;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}> = ({ importFn, fallback, onLoad, onError }) => {
  const [Component, setComponent] = useState<React.ComponentType<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadComponent = async () => {
      try {
        const result = await importFn();
        setComponent(() => result.default);
        onLoad?.();
      } catch (err) {
        setError(err as Error);
        onError?.(err as Error);
      } finally {
        setLoading(false);
      }
    };

    loadComponent();
  }, [importFn, onLoad, onError]);

  if (loading) {
    return <>{fallback || <DefaultFallback />}</>;
  }

  if (error) {
    return (
      <div className="code-splitting-error">
        <span>Erro ao carregar módulo: {error.message}</span>
      </div>
    );
  }

  return Component ? <Component /> : null;
};

// Bundle analyzer hook
export const useBundleAnalyzer = () => {
  const [bundles, setBundles] = useState<BundleInfo[]>([]);
  const bundleLoader = BundleLoader.getInstance();

  useEffect(() => {
    const updateBundles = () => {
      setBundles(bundleLoader.getAllBundles());
    };

    // Update immediately
    updateBundles();

    // Set up interval for updates
    const interval = setInterval(updateBundles, 1000);

    return () => clearInterval(interval);
  }, []);

  const getTotalSize = () => {
    return bundles.reduce((total, bundle) => total + bundle.size, 0);
  };

  const getAverageLoadTime = () => {
    const loadedBundles = bundles.filter(b => b.status === 'loaded');
    if (loadedBundles.length === 0) return 0;
    
    return loadedBundles.reduce((total, bundle) => total + bundle.loadTime, 0) / loadedBundles.length;
  };

  const getLoadSuccessRate = () => {
    const total = bundles.length;
    const successful = bundles.filter(b => b.status === 'loaded').length;
    return total > 0 ? (successful / total) * 100 : 0;
  };

  return {
    bundles,
    getTotalSize,
    getAverageLoadTime,
    getLoadSuccessRate
  };
};

// Performance monitoring for code splitting
export const useCodeSplittingMetrics = () => {
  const [metrics, setMetrics] = useState({
    totalBundles: 0,
    loadedBundles: 0,
    failedBundles: 0,
    totalLoadTime: 0,
    averageLoadTime: 0
  });

  const trackBundleLoad = (loadTime: number) => {
    setMetrics(prev => ({
      ...prev,
      loadedBundles: prev.loadedBundles + 1,
      totalLoadTime: prev.totalLoadTime + loadTime,
      averageLoadTime: (prev.totalLoadTime + loadTime) / (prev.loadedBundles + 1)
    }));
  };

  const trackBundleError = () => {
    setMetrics(prev => ({
      ...prev,
      failedBundles: prev.failedBundles + 1
    }));
  };

  const getSuccessRate = () => {
    const total = metrics.loadedBundles + metrics.failedBundles;
    return total > 0 ? (metrics.loadedBundles / total) * 100 : 0;
  };

  return {
    metrics,
    trackBundleLoad,
    trackBundleError,
    getSuccessRate
  };
};

// Utility for clearing bundle cache
export const clearBundleCache = () => {
  // This would clear the bundle cache in a real implementation
  console.log('Bundle cache cleared');
};

// Utility for getting bundle statistics
export const getBundleStats = () => {
  const bundleLoader = BundleLoader.getInstance();
  const bundles = bundleLoader.getAllBundles();
  
  return {
    totalBundles: bundles.length,
    loadedBundles: bundles.filter(b => b.status === 'loaded').length,
    failedBundles: bundles.filter(b => b.status === 'error').length,
    totalSize: bundles.reduce((total, b) => total + b.size, 0),
    averageLoadTime: bundles.length > 0 
      ? bundles.reduce((total, b) => total + b.loadTime, 0) / bundles.length 
      : 0
  };
};

export default {
  BundleLoader,
  useCodeSplitting,
  withCodeSplitting,
  createLazyRoute,
  createLazyComponent,
  FeatureCodeSplitter,
  DynamicImport,
  useBundleAnalyzer,
  useCodeSplittingMetrics,
  clearBundleCache,
  getBundleStats
}; 