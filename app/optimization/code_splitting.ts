/**
 * Sistema de Code Splitting
 * Otimiza carregamento de bundles e melhora performance da aplicação
 */

import React, { Suspense, lazy, ComponentType, ReactNode } from 'react';

// Tipos para configuração de code splitting
interface CodeSplittingConfig {
  fallback?: ReactNode;
  timeout?: number;
  retryAttempts?: number;
  chunkSize?: 'small' | 'medium' | 'large';
  preloadStrategy?: 'aggressive' | 'conservative' | 'on-demand';
}

interface BundleConfig {
  name: string;
  components: string[];
  priority: 'critical' | 'high' | 'medium' | 'low';
  preload?: boolean;
  dependencies?: string[];
}

// Configuração padrão
const DEFAULT_CONFIG: CodeSplittingConfig = {
  fallback: <div className="loading-spinner">Carregando módulo...</div>,
  timeout: 10000,
  retryAttempts: 3,
  chunkSize: 'medium',
  preloadStrategy: 'on-demand'
};

/**
 * Gerenciador de bundles
 */
class BundleManager {
  private bundles = new Map<string, BundleConfig>();
  private loadedBundles = new Set<string>();
  private loadingBundles = new Set<string>();
  private bundleCache = new Map<string, any>();

  /**
   * Registra um bundle
   */
  registerBundle(config: BundleConfig) {
    this.bundles.set(config.name, config);
  }

  /**
   * Carrega um bundle
   */
  async loadBundle(bundleName: string): Promise<any> {
    if (this.loadedBundles.has(bundleName)) {
      return this.bundleCache.get(bundleName);
    }

    if (this.loadingBundles.has(bundleName)) {
      // Aguarda o carregamento em andamento
      return new Promise((resolve, reject) => {
        const checkLoaded = () => {
          if (this.loadedBundles.has(bundleName)) {
            resolve(this.bundleCache.get(bundleName));
          } else if (!this.loadingBundles.has(bundleName)) {
            reject(new Error(`Failed to load bundle: ${bundleName}`));
          } else {
            setTimeout(checkLoaded, 100);
          }
        };
        checkLoaded();
      });
    }

    const bundle = this.bundles.get(bundleName);
    if (!bundle) {
      throw new Error(`Bundle not found: ${bundleName}`);
    }

    this.loadingBundles.add(bundleName);

    try {
      // Carregar dependências primeiro
      if (bundle.dependencies) {
        await Promise.all(
          bundle.dependencies.map(dep => this.loadBundle(dep))
        );
      }

      // Simular carregamento do bundle (em produção seria um import dinâmico)
      const bundleModule = await this.importBundle(bundleName);
      
      this.bundleCache.set(bundleName, bundleModule);
      this.loadedBundles.add(bundleName);
      this.loadingBundles.delete(bundleName);

      return bundleModule;
    } catch (error) {
      this.loadingBundles.delete(bundleName);
      throw error;
    }
  }

  /**
   * Importa um bundle dinamicamente
   */
  private async importBundle(bundleName: string): Promise<any> {
    // Em produção, isso seria um import dinâmico real
    // Por exemplo: return import(`../bundles/${bundleName}`);
    
    // Simulação para demonstração
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          name: bundleName,
          components: {},
          loadedAt: new Date()
        });
      }, Math.random() * 1000 + 500);
    });
  }

  /**
   * Preload de bundles
   */
  async preloadBundles(bundleNames: string[]) {
    const preloadPromises = bundleNames.map(name => 
      this.loadBundle(name).catch(error => {
        console.warn(`Failed to preload bundle ${name}:`, error);
      })
    );

    await Promise.all(preloadPromises);
  }

  /**
   * Obtém status dos bundles
   */
  getBundleStatus() {
    return {
      total: this.bundles.size,
      loaded: this.loadedBundles.size,
      loading: this.loadingBundles.size,
      loadedBundles: Array.from(this.loadedBundles),
      loadingBundles: Array.from(this.loadingBundles)
    };
  }

  /**
   * Limpa cache de bundles
   */
  clearCache() {
    this.bundleCache.clear();
    this.loadedBundles.clear();
    this.loadingBundles.clear();
  }
}

// Instância global do gerenciador de bundles
export const bundleManager = new BundleManager();

/**
 * Hook para carregamento de bundle
 */
export function useBundle(
  bundleName: string,
  config: CodeSplittingConfig = {}
) {
  const [bundle, setBundle] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  React.useEffect(() => {
    let mounted = true;

    const loadBundle = async () => {
      try {
        setLoading(true);
        setError(null);

        const bundleModule = await bundleManager.loadBundle(bundleName);
        
        if (mounted) {
          setBundle(bundleModule);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };

    loadBundle();

    return () => {
      mounted = false;
    };
  }, [bundleName, finalConfig]);

  return { bundle, loading, error };
}

/**
 * Componente com carregamento de bundle
 */
export function BundleComponent({
  bundleName,
  componentName,
  fallback,
  ...props
}: {
  bundleName: string;
  componentName: string;
  fallback?: ReactNode;
} & Record<string, any>) {
  const { bundle, loading, error } = useBundle(bundleName);
  const [Component, setComponent] = React.useState<ComponentType<any> | null>(null);

  React.useEffect(() => {
    if (bundle && bundle.components && bundle.components[componentName]) {
      setComponent(() => bundle.components[componentName]);
    }
  }, [bundle, componentName]);

  if (error) {
    return <div className="error">Erro ao carregar componente</div>;
  }

  if (loading || !Component) {
    return <>{fallback || DEFAULT_CONFIG.fallback}</>;
  }

  return <Component {...props} />;
}

/**
 * Sistema de route-based code splitting
 */
export function createRouteComponent(
  importFn: () => Promise<{ default: ComponentType<any> }>,
  config: CodeSplittingConfig = {}
) {
  const LazyComponent = lazy(importFn);
  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  return function RouteComponent(props: any) {
    return (
      <Suspense fallback={finalConfig.fallback}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };
}

/**
 * Sistema de feature-based code splitting
 */
export class FeatureSplitter {
  private features = new Map<string, () => Promise<{ default: ComponentType<any> }>>();
  private loadedFeatures = new Set<string>();

  /**
   * Registra uma feature
   */
  registerFeature(
    name: string,
    importFn: () => Promise<{ default: ComponentType<any> }>
  ) {
    this.features.set(name, importFn);
  }

  /**
   * Carrega uma feature
   */
  async loadFeature(name: string): Promise<ComponentType<any>> {
    if (this.loadedFeatures.has(name)) {
      const importFn = this.features.get(name);
      if (importFn) {
        const result = await importFn();
        return result.default;
      }
    }

    const importFn = this.features.get(name);
    if (!importFn) {
      throw new Error(`Feature not found: ${name}`);
    }

    const result = await importFn();
    this.loadedFeatures.add(name);
    return result.default;
  }

  /**
   * Cria um componente lazy para uma feature
   */
  createFeatureComponent(name: string) {
    return lazy(async () => {
      const Component = await this.loadFeature(name);
      return { default: Component };
    });
  }

  /**
   * Preload de features
   */
  async preloadFeatures(featureNames: string[]) {
    const preloadPromises = featureNames.map(name =>
      this.loadFeature(name).catch(error => {
        console.warn(`Failed to preload feature ${name}:`, error);
      })
    );

    await Promise.all(preloadPromises);
  }
}

// Instância global do feature splitter
export const featureSplitter = new FeatureSplitter();

/**
 * Hook para feature-based code splitting
 */
export function useFeature(
  featureName: string,
  config: CodeSplittingConfig = {}
) {
  const [Component, setComponent] = React.useState<ComponentType<any> | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  React.useEffect(() => {
    let mounted = true;

    const loadFeature = async () => {
      try {
        setLoading(true);
        setError(null);

        const FeatureComponent = await featureSplitter.loadFeature(featureName);
        
        if (mounted) {
          setComponent(() => FeatureComponent);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };

    loadFeature();

    return () => {
      mounted = false;
    };
  }, [featureName, finalConfig]);

  return { Component, loading, error };
}

/**
 * Sistema de dynamic imports com cache
 */
class DynamicImportCache {
  private cache = new Map<string, Promise<any>>();
  private maxSize = 100;

  async import(modulePath: string): Promise<any> {
    if (this.cache.has(modulePath)) {
      return this.cache.get(modulePath);
    }

    if (this.cache.size >= this.maxSize) {
      this.clearOldest();
    }

    const importPromise = this.dynamicImport(modulePath);
    this.cache.set(modulePath, importPromise);

    return importPromise;
  }

  private async dynamicImport(modulePath: string): Promise<any> {
    // Em produção, isso seria um import dinâmico real
    // Por exemplo: return import(modulePath);
    
    // Simulação para demonstração
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          default: () => <div>Componente carregado dinamicamente: {modulePath}</div>
        });
      }, Math.random() * 500 + 200);
    });
  }

  private clearOldest() {
    const firstKey = this.cache.keys().next().value;
    if (firstKey) {
      this.cache.delete(firstKey);
    }
  }

  clear() {
    this.cache.clear();
  }
}

// Instância global do cache de imports dinâmicos
export const dynamicImportCache = new DynamicImportCache();

/**
 * Hook para import dinâmico com cache
 */
export function useDynamicImport(modulePath: string) {
  const [module, setModule] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    let mounted = true;

    const loadModule = async () => {
      try {
        setLoading(true);
        setError(null);

        const moduleData = await dynamicImportCache.import(modulePath);
        
        if (mounted) {
          setModule(moduleData);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };

    loadModule();

    return () => {
      mounted = false;
    };
  }, [modulePath]);

  return { module, loading, error };
}

/**
 * Sistema de análise de chunks
 */
export class ChunkAnalyzer {
  private chunks = new Map<string, {
    size: number;
    dependencies: string[];
    components: string[];
    loadTime: number;
  }>();

  /**
   * Registra informações de um chunk
   */
  registerChunk(
    name: string,
    size: number,
    dependencies: string[] = [],
    components: string[] = []
  ) {
    this.chunks.set(name, {
      size,
      dependencies,
      components,
      loadTime: 0
    });
  }

  /**
   * Registra tempo de carregamento
   */
  recordLoadTime(chunkName: string, loadTime: number) {
    const chunk = this.chunks.get(chunkName);
    if (chunk) {
      chunk.loadTime = loadTime;
    }
  }

  /**
   * Obtém análise dos chunks
   */
  getAnalysis() {
    const chunks = Array.from(this.chunks.entries());
    
    return {
      totalChunks: chunks.length,
      totalSize: chunks.reduce((sum, [_, chunk]) => sum + chunk.size, 0),
      averageSize: chunks.reduce((sum, [_, chunk]) => sum + chunk.size, 0) / chunks.length,
      averageLoadTime: chunks.reduce((sum, [_, chunk]) => sum + chunk.loadTime, 0) / chunks.length,
      largestChunk: chunks.reduce((max, [name, chunk]) => 
        chunk.size > max.size ? { name, ...chunk } : max, 
        { name: '', size: 0, dependencies: [], components: [], loadTime: 0 }
      ),
      chunksBySize: chunks
        .map(([name, chunk]) => ({ name, ...chunk }))
        .sort((a, b) => b.size - a.size)
    };
  }

  /**
   * Sugere otimizações
   */
  getOptimizationSuggestions() {
    const analysis = this.getAnalysis();
    const suggestions = [];

    if (analysis.largestChunk.size > 500000) { // 500KB
      suggestions.push({
        type: 'split_large_chunk',
        chunk: analysis.largestChunk.name,
        reason: 'Chunk muito grande, considere dividir em chunks menores'
      });
    }

    if (analysis.averageLoadTime > 2000) { // 2s
      suggestions.push({
        type: 'optimize_load_time',
        reason: 'Tempo de carregamento médio alto, considere preload de chunks críticos'
      });
    }

    const chunksWithManyDeps = Array.from(this.chunks.entries())
      .filter(([_, chunk]) => chunk.dependencies.length > 5);

    if (chunksWithManyDeps.length > 0) {
      suggestions.push({
        type: 'reduce_dependencies',
        chunks: chunksWithManyDeps.map(([name, _]) => name),
        reason: 'Chunks com muitas dependências, considere otimizar imports'
      });
    }

    return suggestions;
  }
}

// Instância global do analisador de chunks
export const chunkAnalyzer = new ChunkAnalyzer();

/**
 * Utilitários para code splitting
 */
export const CodeSplittingUtils = {
  /**
   * Cria um componente com code splitting
   */
  createSplitComponent: (importFn: () => Promise<{ default: ComponentType<any> }>) => {
    return createRouteComponent(importFn);
  },

  /**
   * Preload de múltiplos módulos
   */
  preloadModules: async (modules: Array<() => Promise<any>>) => {
    try {
      await Promise.all(modules.map(module => module()));
    } catch (error) {
      console.warn('Failed to preload some modules:', error);
    }
  },

  /**
   * Limpa todos os caches
   */
  clearAllCaches: () => {
    bundleManager.clearCache();
    dynamicImportCache.clear();
  },

  /**
   * Obtém estatísticas de performance
   */
  getPerformanceStats: () => {
    return {
      bundles: bundleManager.getBundleStatus(),
      chunks: chunkAnalyzer.getAnalysis(),
      suggestions: chunkAnalyzer.getOptimizationSuggestions()
    };
  }
};

// Configuração de bundles padrão
export const DefaultBundles = {
  core: {
    name: 'core',
    components: ['App', 'Router', 'Layout'],
    priority: 'critical' as const,
    preload: true
  },
  dashboard: {
    name: 'dashboard',
    components: ['Dashboard', 'Analytics', 'Reports'],
    priority: 'high' as const,
    dependencies: ['core']
  },
  admin: {
    name: 'admin',
    components: ['AdminPanel', 'UserManagement', 'Settings'],
    priority: 'medium' as const,
    dependencies: ['core']
  },
  features: {
    name: 'features',
    components: ['AdvancedFeatures', 'Integrations', 'API'],
    priority: 'low' as const,
    dependencies: ['core']
  }
};

// Registrar bundles padrão
Object.values(DefaultBundles).forEach(bundle => {
  bundleManager.registerBundle(bundle);
}); 