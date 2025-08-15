/**
 * Sistema de Análise de Bundle
 * Monitora e otimiza tamanho dos bundles para melhorar performance
 */

import React, { useState, useEffect, useCallback } from 'react';

// Tipos para análise de bundle
interface BundleInfo {
  name: string;
  size: number;
  gzippedSize: number;
  dependencies: string[];
  modules: ModuleInfo[];
  loadTime: number;
  lastModified: Date;
}

interface ModuleInfo {
  name: string;
  size: number;
  type: 'js' | 'css' | 'asset';
  dependencies: string[];
  exports: string[];
}

interface BundleAnalysis {
  totalSize: number;
  totalGzippedSize: number;
  averageSize: number;
  largestBundle: BundleInfo;
  duplicateModules: string[];
  unusedModules: string[];
  optimizationSuggestions: OptimizationSuggestion[];
}

interface OptimizationSuggestion {
  type: 'split' | 'remove' | 'optimize' | 'merge';
  bundle: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  estimatedSavings: number;
}

interface BundleAnalyzerConfig {
  maxBundleSize: number;
  maxModuleSize: number;
  enableGzipAnalysis: boolean;
  enableDependencyAnalysis: boolean;
  enablePerformanceTracking: boolean;
}

// Configuração padrão
const DEFAULT_CONFIG: BundleAnalyzerConfig = {
  maxBundleSize: 500 * 1024, // 500KB
  maxModuleSize: 100 * 1024, // 100KB
  enableGzipAnalysis: true,
  enableDependencyAnalysis: true,
  enablePerformanceTracking: true
};

/**
 * Analisador de bundles
 */
class BundleAnalyzer {
  private bundles = new Map<string, BundleInfo>();
  private config: BundleAnalyzerConfig;
  private performanceMetrics = new Map<string, number[]>();

  constructor(config: BundleAnalyzerConfig = DEFAULT_CONFIG) {
    this.config = config;
  }

  /**
   * Registra informações de um bundle
   */
  registerBundle(bundleInfo: BundleInfo) {
    this.bundles.set(bundleInfo.name, bundleInfo);
  }

  /**
   * Analisa todos os bundles
   */
  analyzeBundles(): BundleAnalysis {
    const bundles = Array.from(this.bundles.values());
    
    if (bundles.length === 0) {
      return {
        totalSize: 0,
        totalGzippedSize: 0,
        averageSize: 0,
        largestBundle: {} as BundleInfo,
        duplicateModules: [],
        unusedModules: [],
        optimizationSuggestions: []
      };
    }

    const totalSize = bundles.reduce((sum, bundle) => sum + bundle.size, 0);
    const totalGzippedSize = bundles.reduce((sum, bundle) => sum + bundle.gzippedSize, 0);
    const averageSize = totalSize / bundles.length;
    const largestBundle = bundles.reduce((max, bundle) => 
      bundle.size > max.size ? bundle : max
    );

    const duplicateModules = this.findDuplicateModules(bundles);
    const unusedModules = this.findUnusedModules(bundles);
    const optimizationSuggestions = this.generateOptimizationSuggestions(bundles);

    return {
      totalSize,
      totalGzippedSize,
      averageSize,
      largestBundle,
      duplicateModules,
      unusedModules,
      optimizationSuggestions
    };
  }

  /**
   * Encontra módulos duplicados
   */
  private findDuplicateModules(bundles: BundleInfo[]): string[] {
    const moduleCounts = new Map<string, number>();
    const duplicates: string[] = [];

    bundles.forEach(bundle => {
      bundle.modules.forEach(module => {
        const count = moduleCounts.get(module.name) || 0;
        moduleCounts.set(module.name, count + 1);
      });
    });

    moduleCounts.forEach((count, moduleName) => {
      if (count > 1) {
        duplicates.push(moduleName);
      }
    });

    return duplicates;
  }

  /**
   * Encontra módulos não utilizados
   */
  private findUnusedModules(bundles: BundleInfo[]): string[] {
    const usedModules = new Set<string>();
    const allModules = new Set<string>();

    bundles.forEach(bundle => {
      bundle.modules.forEach(module => {
        allModules.add(module.name);
        module.exports.forEach(exportName => {
          usedModules.add(`${module.name}:${exportName}`);
        });
      });
    });

    return Array.from(allModules).filter(moduleName => {
      const hasUsedExports = bundle.modules.some(module => 
        module.name === moduleName && 
        module.exports.some(exportName => 
          usedModules.has(`${moduleName}:${exportName}`)
        )
      );
      return !hasUsedExports;
    });
  }

  /**
   * Gera sugestões de otimização
   */
  private generateOptimizationSuggestions(bundles: BundleInfo[]): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];

    bundles.forEach(bundle => {
      // Bundle muito grande
      if (bundle.size > this.config.maxBundleSize) {
        suggestions.push({
          type: 'split',
          bundle: bundle.name,
          description: `Bundle muito grande (${this.formatSize(bundle.size)}), considere dividir em chunks menores`,
          impact: 'high',
          estimatedSavings: bundle.size * 0.3
        });
      }

      // Módulos muito grandes
      const largeModules = bundle.modules.filter(module => 
        module.size > this.config.maxModuleSize
      );

      largeModules.forEach(module => {
        suggestions.push({
          type: 'optimize',
          bundle: bundle.name,
          description: `Módulo ${module.name} muito grande (${this.formatSize(module.size)})`,
          impact: 'medium',
          estimatedSavings: module.size * 0.2
        });
      });
    });

    // Módulos duplicados
    const duplicateModules = this.findDuplicateModules(bundles);
    if (duplicateModules.length > 0) {
      suggestions.push({
        type: 'remove',
        bundle: 'all',
        description: `${duplicateModules.length} módulos duplicados encontrados`,
        impact: 'high',
        estimatedSavings: duplicateModules.length * 50 * 1024 // Estimativa de 50KB por módulo
      });
    }

    // Módulos não utilizados
    const unusedModules = this.findUnusedModules(bundles);
    if (unusedModules.length > 0) {
      suggestions.push({
        type: 'remove',
        bundle: 'all',
        description: `${unusedModules.length} módulos não utilizados encontrados`,
        impact: 'medium',
        estimatedSavings: unusedModules.length * 30 * 1024 // Estimativa de 30KB por módulo
      });
    }

    return suggestions.sort((a, b) => {
      const impactOrder = { high: 3, medium: 2, low: 1 };
      return impactOrder[b.impact] - impactOrder[a.impact];
    });
  }

  /**
   * Registra métrica de performance
   */
  recordPerformanceMetric(bundleName: string, loadTime: number) {
    if (!this.config.enablePerformanceTracking) return;

    const metrics = this.performanceMetrics.get(bundleName) || [];
    metrics.push(loadTime);
    
    // Manter apenas as últimas 100 métricas
    if (metrics.length > 100) {
      metrics.shift();
    }
    
    this.performanceMetrics.set(bundleName, metrics);
  }

  /**
   * Obtém métricas de performance
   */
  getPerformanceMetrics() {
    const metrics: Record<string, {
      average: number;
      min: number;
      max: number;
      count: number;
    }> = {};

    this.performanceMetrics.forEach((times, bundleName) => {
      const average = times.reduce((sum, time) => sum + time, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);

      metrics[bundleName] = {
        average,
        min,
        max,
        count: times.length
      };
    });

    return metrics;
  }

  /**
   * Formata tamanho em bytes
   */
  formatSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Exporta relatório completo
   */
  exportReport(): string {
    const analysis = this.analyzeBundles();
    const performanceMetrics = this.getPerformanceMetrics();

    return JSON.stringify({
      analysis,
      performanceMetrics,
      config: this.config,
      timestamp: new Date().toISOString()
    }, null, 2);
  }

  /**
   * Limpa dados
   */
  clear() {
    this.bundles.clear();
    this.performanceMetrics.clear();
  }
}

// Instância global do analisador
export const bundleAnalyzer = new BundleAnalyzer();

/**
 * Hook para análise de bundle
 */
export function useBundleAnalysis() {
  const [analysis, setAnalysis] = useState<BundleAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  const analyze = useCallback(() => {
    setLoading(true);
    const result = bundleAnalyzer.analyzeBundles();
    setAnalysis(result);
    setLoading(false);
  }, []);

  useEffect(() => {
    analyze();
  }, [analyze]);

  return { analysis, loading, refresh: analyze };
}

/**
 * Componente de visualização de análise de bundle
 */
export function BundleAnalysisView() {
  const { analysis, loading, refresh } = useBundleAnalysis();

  if (loading) {
    return <div>Analisando bundles...</div>;
  }

  if (!analysis) {
    return <div>Nenhum bundle encontrado</div>;
  }

  return (
    <div className="bundle-analysis">
      <h2>Análise de Bundles</h2>
      
      {/* Resumo */}
      <div className="summary">
        <div className="metric">
          <h3>Tamanho Total</h3>
          <p>{bundleAnalyzer.formatSize(analysis.totalSize)}</p>
        </div>
        <div className="metric">
          <h3>Tamanho Gzipped</h3>
          <p>{bundleAnalyzer.formatSize(analysis.totalGzippedSize)}</p>
        </div>
        <div className="metric">
          <h3>Tamanho Médio</h3>
          <p>{bundleAnalyzer.formatSize(analysis.averageSize)}</p>
        </div>
      </div>

      {/* Maior Bundle */}
      <div className="largest-bundle">
        <h3>Maior Bundle</h3>
        <p>{analysis.largestBundle.name}: {bundleAnalyzer.formatSize(analysis.largestBundle.size)}</p>
      </div>

      {/* Problemas */}
      {analysis.duplicateModules.length > 0 && (
        <div className="issues">
          <h3>Módulos Duplicados</h3>
          <ul>
            {analysis.duplicateModules.map(module => (
              <li key={module}>{module}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.unusedModules.length > 0 && (
        <div className="issues">
          <h3>Módulos Não Utilizados</h3>
          <ul>
            {analysis.unusedModules.map(module => (
              <li key={module}>{module}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Sugestões */}
      {analysis.optimizationSuggestions.length > 0 && (
        <div className="suggestions">
          <h3>Sugestões de Otimização</h3>
          {analysis.optimizationSuggestions.map((suggestion, index) => (
            <div key={index} className={`suggestion ${suggestion.impact}`}>
              <h4>{suggestion.type.toUpperCase()}</h4>
              <p>{suggestion.description}</p>
              <p>Impacto: {suggestion.impact}</p>
              <p>Economia estimada: {bundleAnalyzer.formatSize(suggestion.estimatedSavings)}</p>
            </div>
          ))}
        </div>
      )}

      <button onClick={refresh}>Atualizar Análise</button>
    </div>
  );
}

/**
 * Hook para métricas de performance
 */
export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<Record<string, any>>({});

  const updateMetrics = useCallback(() => {
    const performanceMetrics = bundleAnalyzer.getPerformanceMetrics();
    setMetrics(performanceMetrics);
  }, []);

  useEffect(() => {
    updateMetrics();
  }, [updateMetrics]);

  return { metrics, updateMetrics };
}

/**
 * Componente de visualização de métricas de performance
 */
export function PerformanceMetricsView() {
  const { metrics, updateMetrics } = usePerformanceMetrics();

  return (
    <div className="performance-metrics">
      <h2>Métricas de Performance</h2>
      
      {Object.entries(metrics).map(([bundleName, bundleMetrics]) => (
        <div key={bundleName} className="bundle-metrics">
          <h3>{bundleName}</h3>
          <div className="metrics-grid">
            <div className="metric">
              <span>Tempo Médio:</span>
              <span>{bundleMetrics.average.toFixed(2)}ms</span>
            </div>
            <div className="metric">
              <span>Mínimo:</span>
              <span>{bundleMetrics.min.toFixed(2)}ms</span>
            </div>
            <div className="metric">
              <span>Máximo:</span>
              <span>{bundleMetrics.max.toFixed(2)}ms</span>
            </div>
            <div className="metric">
              <span>Total:</span>
              <span>{bundleMetrics.count} carregamentos</span>
            </div>
          </div>
        </div>
      ))}

      <button onClick={updateMetrics}>Atualizar Métricas</button>
    </div>
  );
}

/**
 * Sistema de monitoramento de bundles
 */
class BundleMonitor {
  private observers: Array<(analysis: BundleAnalysis) => void> = [];
  private interval: NodeJS.Timeout | null = null;

  /**
   * Inicia monitoramento
   */
  startMonitoring(intervalMs: number = 30000) {
    if (this.interval) return;

    this.interval = setInterval(() => {
      const analysis = bundleAnalyzer.analyzeBundles();
      this.notifyObservers(analysis);
    }, intervalMs);
  }

  /**
   * Para monitoramento
   */
  stopMonitoring() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }

  /**
   * Adiciona observer
   */
  addObserver(observer: (analysis: BundleAnalysis) => void) {
    this.observers.push(observer);
  }

  /**
   * Remove observer
   */
  removeObserver(observer: (analysis: BundleAnalysis) => void) {
    const index = this.observers.indexOf(observer);
    if (index > -1) {
      this.observers.splice(index, 1);
    }
  }

  /**
   * Notifica observers
   */
  private notifyObservers(analysis: BundleAnalysis) {
    this.observers.forEach(observer => {
      try {
        observer(analysis);
      } catch (error) {
        console.error('Error in bundle monitor observer:', error);
      }
    });
  }
}

// Instância global do monitor
export const bundleMonitor = new BundleMonitor();

/**
 * Hook para monitoramento de bundles
 */
export function useBundleMonitoring() {
  const [analysis, setAnalysis] = useState<BundleAnalysis | null>(null);

  useEffect(() => {
    const observer = (newAnalysis: BundleAnalysis) => {
      setAnalysis(newAnalysis);
    };

    bundleMonitor.addObserver(observer);
    bundleMonitor.startMonitoring();

    return () => {
      bundleMonitor.removeObserver(observer);
    };
  }, []);

  return analysis;
}

/**
 * Utilitários para análise de bundle
 */
export const BundleAnalysisUtils = {
  /**
   * Registra bundle automaticamente
   */
  registerBundleFromWebpack: (webpackStats: any) => {
    if (webpackStats && webpackStats.assets) {
      webpackStats.assets.forEach((asset: any) => {
        const bundleInfo: BundleInfo = {
          name: asset.name,
          size: asset.size,
          gzippedSize: asset.gzippedSize || asset.size * 0.3,
          dependencies: asset.chunks || [],
          modules: asset.modules || [],
          loadTime: 0,
          lastModified: new Date()
        };
        
        bundleAnalyzer.registerBundle(bundleInfo);
      });
    }
  },

  /**
   * Exporta relatório
   */
  exportReport: () => {
    return bundleAnalyzer.exportReport();
  },

  /**
   * Limpa dados
   */
  clearData: () => {
    bundleAnalyzer.clear();
  },

  /**
   * Obtém estatísticas
   */
  getStats: () => {
    const analysis = bundleAnalyzer.analyzeBundles();
    const performanceMetrics = bundleAnalyzer.getPerformanceMetrics();
    
    return {
      bundles: analysis,
      performance: performanceMetrics,
      suggestions: analysis.optimizationSuggestions.length
    };
  }
};

// Estilos CSS para componentes
export const bundleAnalysisStyles = `
  .bundle-analysis {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }

  .metric {
    background: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .metric h3 {
    margin: 0 0 10px 0;
    color: #666;
    font-size: 14px;
  }

  .metric p {
    margin: 0;
    font-size: 24px;
    font-weight: bold;
    color: #333;
  }

  .largest-bundle,
  .issues,
  .suggestions {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .suggestion {
    border-left: 4px solid #ddd;
    padding-left: 15px;
    margin-bottom: 15px;
  }

  .suggestion.high {
    border-left-color: #dc3545;
  }

  .suggestion.medium {
    border-left-color: #ffc107;
  }

  .suggestion.low {
    border-left-color: #28a745;
  }

  .performance-metrics {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .bundle-metrics {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-top: 15px;
  }

  .metrics-grid .metric {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 4px;
  }

  button {
    background: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 20px;
  }

  button:hover {
    background: #0056b3;
  }
`; 