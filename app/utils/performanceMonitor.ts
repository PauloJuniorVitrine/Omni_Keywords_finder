/**
 * Sistema de Monitoramento de Performance
 * Monitora métricas de performance em tempo real
 * 
 * Tracing ID: PERFORMANCE_MONITOR_001
 * Data: 2025-01-27
 * Versão: 1.0.0
 */

import React from 'react';

// Tipos para métricas de performance
interface PerformanceMetrics {
  // Core Web Vitals
  lcp?: number; // Largest Contentful Paint
  fid?: number; // First Input Delay
  cls?: number; // Cumulative Layout Shift
  ttfb?: number; // Time to First Byte
  fcp?: number; // First Contentful Paint
  
  // Métricas customizadas
  bundleSize?: number;
  loadTime?: number;
  renderTime?: number;
  apiResponseTime?: number;
  memoryUsage?: number;
  
  // Métricas de erro
  errorCount?: number;
  errorRate?: number;
  
  // Timestamp
  timestamp: number;
}

interface PerformanceConfig {
  enableCoreWebVitals?: boolean;
  enableCustomMetrics?: boolean;
  enableErrorTracking?: boolean;
  enableMemoryTracking?: boolean;
  enableAPITracking?: boolean;
  sampleRate?: number;
  maxMetrics?: number;
  endpoint?: string;
}

// Configuração padrão
const DEFAULT_CONFIG: PerformanceConfig = {
  enableCoreWebVitals: true,
  enableCustomMetrics: true,
  enableErrorTracking: true,
  enableMemoryTracking: true,
  enableAPITracking: true,
  sampleRate: 1.0, // 100%
  maxMetrics: 1000,
  endpoint: '/api/performance/metrics'
};

/**
 * Monitor de Performance
 */
class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private config: PerformanceConfig;
  private metrics: PerformanceMetrics[] = [];
  private observers: PerformanceObserver[] = [];
  private isInitialized = false;

  private constructor(config: PerformanceConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  static getInstance(config?: PerformanceConfig): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor(config);
    }
    return PerformanceMonitor.instance;
  }

  /**
   * Inicializa o monitor
   */
  init(): void {
    if (this.isInitialized) return;

    console.log('[PerformanceMonitor] Initializing...');

    if (this.config.enableCoreWebVitals) {
      this.initCoreWebVitals();
    }

    if (this.config.enableCustomMetrics) {
      this.initCustomMetrics();
    }

    if (this.config.enableErrorTracking) {
      this.initErrorTracking();
    }

    if (this.config.enableMemoryTracking) {
      this.initMemoryTracking();
    }

    if (this.config.enableAPITracking) {
      this.initAPITracking();
    }

    this.isInitialized = true;
    console.log('[PerformanceMonitor] Initialized successfully');
  }

  /**
   * Inicializa Core Web Vitals
   */
  private initCoreWebVitals(): void {
    // LCP (Largest Contentful Paint)
    if ('PerformanceObserver' in window) {
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          
          this.addMetric({
            lcp: lastEntry.startTime,
            timestamp: Date.now()
          });
        });
        
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        this.observers.push(lcpObserver);
      } catch (error) {
        console.warn('[PerformanceMonitor] LCP observer failed:', error);
      }

      // FID (First Input Delay)
      try {
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            this.addMetric({
              fid: entry.processingStart - entry.startTime,
              timestamp: Date.now()
            });
          });
        });
        
        fidObserver.observe({ entryTypes: ['first-input'] });
        this.observers.push(fidObserver);
      } catch (error) {
        console.warn('[PerformanceMonitor] FID observer failed:', error);
      }

      // CLS (Cumulative Layout Shift)
      try {
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            if (!entry.hadRecentInput) {
              clsValue += (entry as any).value;
            }
          });
          
          this.addMetric({
            cls: clsValue,
            timestamp: Date.now()
          });
        });
        
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        this.observers.push(clsObserver);
      } catch (error) {
        console.warn('[PerformanceMonitor] CLS observer failed:', error);
      }
    }

    // TTFB e FCP
    if ('performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        this.addMetric({
          ttfb: navigation.responseStart - navigation.requestStart,
          fcp: navigation.domContentLoadedEventEnd - navigation.fetchStart,
          timestamp: Date.now()
        });
      }
    }
  }

  /**
   * Inicializa métricas customizadas
   */
  private initCustomMetrics(): void {
    // Bundle size
    this.measureBundleSize();
    
    // Load time
    this.measureLoadTime();
    
    // Render time
    this.measureRenderTime();
  }

  /**
   * Mede tamanho do bundle
   */
  private measureBundleSize(): void {
    const scripts = document.querySelectorAll('script[src]');
    let totalSize = 0;

    scripts.forEach(script => {
      const src = script.getAttribute('src');
      if (src && src.includes('bundle')) {
        // Em produção, isso seria obtido via Resource Timing API
        totalSize += 500; // Estimativa
      }
    });

    this.addMetric({
      bundleSize: totalSize,
      timestamp: Date.now()
    });
  }

  /**
   * Mede tempo de carregamento
   */
  private measureLoadTime(): void {
    if ('performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        this.addMetric({
          loadTime: navigation.loadEventEnd - navigation.fetchStart,
          timestamp: Date.now()
        });
      }
    }
  }

  /**
   * Mede tempo de renderização
   */
  private measureRenderTime(): void {
    const startTime = performance.now();
    
    // Aguarda próxima frame
    requestAnimationFrame(() => {
      const renderTime = performance.now() - startTime;
      this.addMetric({
        renderTime,
        timestamp: Date.now()
      });
    });
  }

  /**
   * Inicializa tracking de erros
   */
  private initErrorTracking(): void {
    let errorCount = 0;
    const startTime = Date.now();

    // JavaScript errors
    window.addEventListener('error', (event) => {
      errorCount++;
      this.addMetric({
        errorCount,
        errorRate: errorCount / ((Date.now() - startTime) / 1000),
        timestamp: Date.now()
      });
    });

    // Promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      errorCount++;
      this.addMetric({
        errorCount,
        errorRate: errorCount / ((Date.now() - startTime) / 1000),
        timestamp: Date.now()
      });
    });
  }

  /**
   * Inicializa tracking de memória
   */
  private initMemoryTracking(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      
      setInterval(() => {
        this.addMetric({
          memoryUsage: memory.usedJSHeapSize,
          timestamp: Date.now()
        });
      }, 30000); // A cada 30 segundos
    }
  }

  /**
   * Inicializa tracking de API
   */
  private initAPITracking(): void {
    // Intercepta fetch requests
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const startTime = performance.now();
      
      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        
        this.addMetric({
          apiResponseTime: endTime - startTime,
          timestamp: Date.now()
        });
        
        return response;
      } catch (error) {
        const endTime = performance.now();
        
        this.addMetric({
          apiResponseTime: endTime - startTime,
          timestamp: Date.now()
        });
        
        throw error;
      }
    };
  }

  /**
   * Adiciona métrica
   */
  addMetric(metric: Partial<PerformanceMetrics>): void {
    // Aplicar sample rate
    if (Math.random() > this.config.sampleRate!) {
      return;
    }

    const fullMetric: PerformanceMetrics = {
      timestamp: Date.now(),
      ...metric
    };

    this.metrics.push(fullMetric);

    // Limitar número de métricas
    if (this.metrics.length > this.config.maxMetrics!) {
      this.metrics.shift();
    }

    // Enviar para servidor se endpoint configurado
    if (this.config.endpoint) {
      this.sendToServer(fullMetric);
    }
  }

  /**
   * Envia métrica para servidor
   */
  private async sendToServer(metric: PerformanceMetrics): Promise<void> {
    try {
      await fetch(this.config.endpoint!, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metric)
      });
    } catch (error) {
      console.warn('[PerformanceMonitor] Failed to send metric:', error);
    }
  }

  /**
   * Obtém métricas
   */
  getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }

  /**
   * Obtém métricas filtradas
   */
  getMetricsByType(type: keyof PerformanceMetrics): PerformanceMetrics[] {
    return this.metrics.filter(metric => metric[type] !== undefined);
  }

  /**
   * Obtém métricas por período
   */
  getMetricsByPeriod(startTime: number, endTime: number): PerformanceMetrics[] {
    return this.metrics.filter(
      metric => metric.timestamp >= startTime && metric.timestamp <= endTime
    );
  }

  /**
   * Calcula estatísticas
   */
  getStatistics(): Record<string, any> {
    const stats: Record<string, any> = {};

    // Core Web Vitals
    const lcpMetrics = this.getMetricsByType('lcp');
    if (lcpMetrics.length > 0) {
      stats.lcp = {
        avg: lcpMetrics.reduce((sum, m) => sum + m.lcp!, 0) / lcpMetrics.length,
        min: Math.min(...lcpMetrics.map(m => m.lcp!)),
        max: Math.max(...lcpMetrics.map(m => m.lcp!))
      };
    }

    const fidMetrics = this.getMetricsByType('fid');
    if (fidMetrics.length > 0) {
      stats.fid = {
        avg: fidMetrics.reduce((sum, m) => sum + m.fid!, 0) / fidMetrics.length,
        min: Math.min(...fidMetrics.map(m => m.fid!)),
        max: Math.max(...fidMetrics.map(m => m.fid!))
      };
    }

    const clsMetrics = this.getMetricsByType('cls');
    if (clsMetrics.length > 0) {
      stats.cls = {
        avg: clsMetrics.reduce((sum, m) => sum + m.cls!, 0) / clsMetrics.length,
        min: Math.min(...clsMetrics.map(m => m.cls!)),
        max: Math.max(...clsMetrics.map(m => m.cls!))
      };
    }

    return stats;
  }

  /**
   * Limpa métricas
   */
  clearMetrics(): void {
    this.metrics = [];
  }

  /**
   * Destroi monitor
   */
  destroy(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
    this.metrics = [];
    this.isInitialized = false;
  }
}

/**
 * Hook para monitor de performance
 */
export function usePerformanceMonitor(config?: PerformanceConfig) {
  React.useEffect(() => {
    const monitor = PerformanceMonitor.getInstance(config);
    monitor.init();

    return () => {
      // Não destruir aqui, pois pode ser usado por outros componentes
    };
  }, [config]);
}

/**
 * Hook para métricas de performance
 */
export function usePerformanceMetrics() {
  const [metrics, setMetrics] = React.useState<PerformanceMetrics[]>([]);
  const [statistics, setStatistics] = React.useState<Record<string, any>>({});

  React.useEffect(() => {
    const monitor = PerformanceMonitor.getInstance();
    
    const updateMetrics = () => {
      setMetrics(monitor.getMetrics());
      setStatistics(monitor.getStatistics());
    };

    // Atualizar a cada 5 segundos
    const interval = setInterval(updateMetrics, 5000);
    updateMetrics(); // Atualização inicial

    return () => clearInterval(interval);
  }, []);

  return { metrics, statistics };
}

/**
 * Componente para exibir métricas
 */
export function PerformanceMetricsDisplay() {
  const { metrics, statistics } = usePerformanceMetrics();

  return (
    <div className="performance-metrics">
      <h3>Performance Metrics</h3>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>Core Web Vitals</h4>
          <div className="metric">
            <span>LCP:</span>
            <span>{statistics.lcp?.avg?.toFixed(2) || 'N/A'}ms</span>
          </div>
          <div className="metric">
            <span>FID:</span>
            <span>{statistics.fid?.avg?.toFixed(2) || 'N/A'}ms</span>
          </div>
          <div className="metric">
            <span>CLS:</span>
            <span>{statistics.cls?.avg?.toFixed(3) || 'N/A'}</span>
          </div>
        </div>
        
        <div className="metric-card">
          <h4>Recent Metrics</h4>
          <div className="metrics-list">
            {metrics.slice(-5).map((metric, index) => (
              <div key={index} className="metric-item">
                <span>{new Date(metric.timestamp).toLocaleTimeString()}</span>
                <span>{metric.lcp ? `LCP: ${metric.lcp.toFixed(2)}ms` : ''}</span>
                <span>{metric.fid ? `FID: ${metric.fid.toFixed(2)}ms` : ''}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Utilitários para performance
 */
export const PerformanceUtils = {
  /**
   * Obtém instância do monitor
   */
  getMonitor: (config?: PerformanceConfig) => PerformanceMonitor.getInstance(config),

  /**
   * Adiciona métrica customizada
   */
  addMetric: (metric: Partial<PerformanceMetrics>) => {
    const monitor = PerformanceMonitor.getInstance();
    monitor.addMetric(metric);
  },

  /**
   * Obtém estatísticas
   */
  getStatistics: () => {
    const monitor = PerformanceMonitor.getInstance();
    return monitor.getStatistics();
  },

  /**
   * Mede tempo de execução
   */
  measureTime: (fn: () => any) => {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    
    PerformanceUtils.addMetric({
      renderTime: end - start,
      timestamp: Date.now()
    });
    
    return result;
  },

  /**
   * Mede tempo de execução assíncrono
   */
  measureTimeAsync: async (fn: () => Promise<any>) => {
    const start = performance.now();
    const result = await fn();
    const end = performance.now();
    
    PerformanceUtils.addMetric({
      renderTime: end - start,
      timestamp: Date.now()
    });
    
    return result;
  }
};

export default PerformanceMonitor; 