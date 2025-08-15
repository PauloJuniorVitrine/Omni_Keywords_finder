/**
 * Sistema de Lazy Loading de Componentes
 * Otimiza performance do frontend carregando componentes sob demanda
 */

import React, { Suspense, lazy, ComponentType, ReactNode } from 'react';

// Tipos para configuração de lazy loading
interface LazyLoadingConfig {
  fallback?: ReactNode;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
}

interface ComponentConfig {
  component: ComponentType<any>;
  preload?: boolean;
  priority?: 'high' | 'medium' | 'low';
  dependencies?: string[];
}

// Configuração padrão
const DEFAULT_CONFIG: LazyLoadingConfig = {
  fallback: <div className="loading-spinner">Carregando...</div>,
  timeout: 5000,
  retryAttempts: 3,
  retryDelay: 1000
};

/**
 * Hook para lazy loading com retry automático
 */
export function useLazyComponent(
  importFn: () => Promise<{ default: ComponentType<any> }>,
  config: LazyLoadingConfig = {}
) {
  const [Component, setComponent] = React.useState<ComponentType<any> | null>(null);
  const [error, setError] = React.useState<Error | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [retryCount, setRetryCount] = React.useState(0);

  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  const loadComponent = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Timeout para evitar carregamento infinito
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error('Timeout')), finalConfig.timeout);
      });

      const componentPromise = importFn();
      const result = await Promise.race([componentPromise, timeoutPromise]);
      
      setComponent(() => result.default);
      setLoading(false);
    } catch (err) {
      setError(err as Error);
      
      // Retry logic
      if (retryCount < finalConfig.retryAttempts!) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          loadComponent();
        }, finalConfig.retryDelay);
      } else {
        setLoading(false);
      }
    }
  }, [importFn, finalConfig, retryCount]);

  React.useEffect(() => {
    loadComponent();
  }, [loadComponent]);

  return { Component, loading, error, retry: loadComponent };
}

/**
 * Componente de lazy loading com Suspense
 */
export function LazyComponent({
  importFn,
  fallback,
  ...props
}: {
  importFn: () => Promise<{ default: ComponentType<any> }>;
  fallback?: ReactNode;
} & Record<string, any>) {
  const LazyComponent = lazy(importFn);
  
  return (
    <Suspense fallback={fallback || DEFAULT_CONFIG.fallback}>
      <LazyComponent {...props} />
    </Suspense>
  );
}

/**
 * Sistema de preload de componentes
 */
class ComponentPreloader {
  private preloadedComponents = new Map<string, ComponentType<any>>();
  private preloadQueue: Array<() => Promise<void>> = [];
  private isProcessing = false;

  /**
   * Adiciona componente à fila de preload
   */
  addToPreloadQueue(
    key: string,
    importFn: () => Promise<{ default: ComponentType<any> }>,
    priority: 'high' | 'medium' | 'low' = 'medium'
  ) {
    const preloadTask = async () => {
      try {
        const result = await importFn();
        this.preloadedComponents.set(key, result.default);
      } catch (error) {
        console.warn(`Failed to preload component ${key}:`, error);
      }
    };

    if (priority === 'high') {
      this.preloadQueue.unshift(preloadTask);
    } else {
      this.preloadQueue.push(preloadTask);
    }

    this.processQueue();
  }

  /**
   * Processa a fila de preload
   */
  private async processQueue() {
    if (this.isProcessing || this.preloadQueue.length === 0) return;

    this.isProcessing = true;

    while (this.preloadQueue.length > 0) {
      const task = this.preloadQueue.shift();
      if (task) {
        await task();
        // Pequena pausa para não bloquear a UI
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    }

    this.isProcessing = false;
  }

  /**
   * Verifica se componente foi preloadado
   */
  isPreloaded(key: string): boolean {
    return this.preloadedComponents.has(key);
  }

  /**
   * Obtém componente preloadado
   */
  getPreloadedComponent(key: string): ComponentType<any> | undefined {
    return this.preloadedComponents.get(key);
  }

  /**
   * Remove componente do cache
   */
  removeFromCache(key: string) {
    this.preloadedComponents.delete(key);
  }

  /**
   * Limpa todo o cache
   */
  clearCache() {
    this.preloadedComponents.clear();
  }
}

// Instância global do preloader
export const componentPreloader = new ComponentPreloader();

/**
 * Hook para preload de componentes
 */
export function useComponentPreload(
  key: string,
  importFn: () => Promise<{ default: ComponentType<any> }>,
  priority: 'high' | 'medium' | 'low' = 'medium'
) {
  React.useEffect(() => {
    if (!componentPreloader.isPreloaded(key)) {
      componentPreloader.addToPreloadQueue(key, importFn, priority);
    }
  }, [key, importFn, priority]);

  return {
    isPreloaded: componentPreloader.isPreloaded(key),
    getComponent: () => componentPreloader.getPreloadedComponent(key)
  };
}

/**
 * Componente com preload automático
 */
export function PreloadedComponent({
  key,
  importFn,
  fallback,
  priority = 'medium',
  ...props
}: {
  key: string;
  importFn: () => Promise<{ default: ComponentType<any> }>;
  fallback?: ReactNode;
  priority?: 'high' | 'medium' | 'low';
} & Record<string, any>) {
  const { isPreloaded, getComponent } = useComponentPreload(key, importFn, priority);
  const [Component, setComponent] = React.useState<ComponentType<any> | null>(null);

  React.useEffect(() => {
    if (isPreloaded) {
      const preloadedComponent = getComponent();
      if (preloadedComponent) {
        setComponent(() => preloadedComponent);
      }
    } else {
      // Fallback para lazy loading se não estiver preloadado
      importFn().then(result => {
        setComponent(() => result.default);
      });
    }
  }, [isPreloaded, getComponent, importFn]);

  if (!Component) {
    return <>{fallback || DEFAULT_CONFIG.fallback}</>;
  }

  return <Component {...props} />;
}

/**
 * Sistema de lazy loading com intersection observer
 */
export function useIntersectionLazyLoad(
  importFn: () => Promise<{ default: ComponentType<any> }>,
  options: IntersectionObserverInit = {}
) {
  const [Component, setComponent] = React.useState<ComponentType<any> | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);
  const ref = React.useRef<HTMLDivElement>(null);

  const loadComponent = React.useCallback(async () => {
    if (Component || loading) return;

    try {
      setLoading(true);
      setError(null);
      const result = await importFn();
      setComponent(() => result.default);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [Component, loading, importFn]);

  React.useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            loadComponent();
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
        ...options
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [loadComponent, options]);

  return { ref, Component, loading, error };
}

/**
 * Componente com lazy loading baseado em intersection observer
 */
export function IntersectionLazyComponent({
  importFn,
  fallback,
  observerOptions,
  ...props
}: {
  importFn: () => Promise<{ default: ComponentType<any> }>;
  fallback?: ReactNode;
  observerOptions?: IntersectionObserverInit;
} & Record<string, any>) {
  const { ref, Component, loading, error } = useIntersectionLazyLoad(importFn, observerOptions);

  if (error) {
    return <div className="error">Erro ao carregar componente</div>;
  }

  return (
    <div ref={ref}>
      {Component ? (
        <Component {...props} />
      ) : (
        fallback || DEFAULT_CONFIG.fallback
      )}
    </div>
  );
}

/**
 * Sistema de cache de componentes
 */
class ComponentCache {
  private cache = new Map<string, { component: ComponentType<any>; timestamp: number }>();
  private maxSize = 50;
  private maxAge = 5 * 60 * 1000; // 5 minutos

  set(key: string, component: ComponentType<any>) {
    // Limpar cache se estiver cheio
    if (this.cache.size >= this.maxSize) {
      this.cleanup();
    }

    this.cache.set(key, {
      component,
      timestamp: Date.now()
    });
  }

  get(key: string): ComponentType<any> | null {
    const item = this.cache.get(key);
    if (!item) return null;

    // Verificar se expirou
    if (Date.now() - item.timestamp > this.maxAge) {
      this.cache.delete(key);
      return null;
    }

    return item.component;
  }

  has(key: string): boolean {
    return this.cache.has(key);
  }

  delete(key: string) {
    this.cache.delete(key);
  }

  clear() {
    this.cache.clear();
  }

  private cleanup() {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > this.maxAge) {
        this.cache.delete(key);
      }
    }
  }
}

// Instância global do cache
export const componentCache = new ComponentCache();

/**
 * Hook para cache de componentes
 */
export function useCachedComponent(
  key: string,
  importFn: () => Promise<{ default: ComponentType<any> }>
) {
  const [Component, setComponent] = React.useState<ComponentType<any> | null>(() => {
    return componentCache.get(key);
  });

  React.useEffect(() => {
    if (!Component) {
      importFn().then(result => {
        const component = result.default;
        componentCache.set(key, component);
        setComponent(() => component);
      });
    }
  }, [key, Component, importFn]);

  return Component;
}

/**
 * Utilitários para otimização
 */
export const LazyLoadingUtils = {
  /**
   * Cria um componente lazy com configuração padrão
   */
  createLazyComponent: (importFn: () => Promise<{ default: ComponentType<any> }>) => {
    return lazy(importFn);
  },

  /**
   * Cria múltiplos componentes lazy
   */
  createLazyComponents: (components: Record<string, () => Promise<{ default: ComponentType<any> }>>) => {
    const lazyComponents: Record<string, ComponentType<any>> = {};
    
    for (const [key, importFn] of Object.entries(components)) {
      lazyComponents[key] = lazy(importFn);
    }
    
    return lazyComponents;
  },

  /**
   * Preload de componentes em paralelo
   */
  preloadComponents: async (components: Array<() => Promise<{ default: ComponentType<any> }>>) => {
    try {
      await Promise.all(components.map(importFn => importFn()));
    } catch (error) {
      console.warn('Failed to preload some components:', error);
    }
  },

  /**
   * Limpa todos os caches
   */
  clearAllCaches: () => {
    componentPreloader.clearCache();
    componentCache.clear();
  }
};

// Exemplo de uso
export const LazyComponents = {
  Dashboard: () => import('../components/dashboard/Dashboard'),
  Analytics: () => import('../components/analytics/Analytics'),
  Reports: () => import('../components/reports/Reports'),
  Settings: () => import('../components/settings/Settings'),
  Profile: () => import('../components/profile/Profile')
};

// Componentes lazy pré-configurados
export const LazyDashboard = lazy(LazyComponents.Dashboard);
export const LazyAnalytics = lazy(LazyComponents.Analytics);
export const LazyReports = lazy(LazyComponents.Reports);
export const LazySettings = lazy(LazyComponents.Settings);
export const LazyProfile = lazy(LazyComponents.Profile); 