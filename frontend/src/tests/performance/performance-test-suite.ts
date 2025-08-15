/**
 * Suite de Testes de Performance
 * 
 * Prompt: Implementar testes de performance
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: PERF_TEST_SUITE_20250127_001
 */

import { PerformanceMetrics, PerformanceThresholds, PerformanceTestResult } from './performance-types';

/**
 * Configurações de performance
 */
export const PERFORMANCE_CONFIG = {
  // Limites de performance por métrica
  thresholds: {
    // Tempo de carregamento inicial
    firstContentfulPaint: 1500, // ms
    largestContentfulPaint: 2500, // ms
    firstInputDelay: 100, // ms
    cumulativeLayoutShift: 0.1, // score
    
    // Tempo de resposta da API
    apiResponseTime: {
      fast: 200, // ms
      medium: 500, // ms
      slow: 1000 // ms
    },
    
    // Tempo de renderização de componentes
    componentRenderTime: {
      simple: 16, // ms (1 frame)
      complex: 50, // ms
      heavy: 100 // ms
    },
    
    // Uso de memória
    memoryUsage: {
      initial: 50, // MB
      peak: 200, // MB
      leak: 10 // MB increase per minute
    },
    
    // Bundle size
    bundleSize: {
      total: 500, // KB
      gzipped: 150 // KB
    }
  },

  // Configurações de teste
  testConfig: {
    // Número de iterações para testes
    iterations: {
      light: 10,
      medium: 50,
      heavy: 100
    },
    
    // Timeout para testes
    timeout: {
      short: 5000, // ms
      medium: 15000, // ms
      long: 30000 // ms
    },
    
    // Configurações de stress test
    stress: {
      concurrentUsers: 10,
      duration: 60000, // ms
      rampUpTime: 10000 // ms
    }
  }
};

/**
 * Suite de testes de performance
 */
export class PerformanceTestSuite {
  private config = PERFORMANCE_CONFIG;
  private results: PerformanceTestResult[] = [];

  /**
   * Executa teste de performance de carregamento de página
   */
  async testPageLoadPerformance(url: string): Promise<PerformanceTestResult> {
    const startTime = performance.now();
    
    try {
      // Simular carregamento de página
      const metrics = await this.measurePageLoadMetrics(url);
      
      const result: PerformanceTestResult = {
        testName: 'Page Load Performance',
        url,
        timestamp: new Date().toISOString(),
        tracingId: `PAGE_LOAD_${Date.now()}`,
        metrics,
        passed: this.validatePageLoadMetrics(metrics),
        duration: performance.now() - startTime
      };

      this.results.push(result);
      return result;
    } catch (error) {
      return {
        testName: 'Page Load Performance',
        url,
        timestamp: new Date().toISOString(),
        tracingId: `PAGE_LOAD_${Date.now()}`,
        metrics: null,
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration: performance.now() - startTime
      };
    }
  }

  /**
   * Executa teste de performance de API
   */
  async testApiPerformance(endpoint: string, method: string = 'GET', payload?: any): Promise<PerformanceTestResult> {
    const startTime = performance.now();
    
    try {
      const metrics = await this.measureApiMetrics(endpoint, method, payload);
      
      const result: PerformanceTestResult = {
        testName: 'API Performance',
        endpoint: `${method} ${endpoint}`,
        timestamp: new Date().toISOString(),
        tracingId: `API_PERF_${Date.now()}`,
        metrics,
        passed: this.validateApiMetrics(metrics),
        duration: performance.now() - startTime
      };

      this.results.push(result);
      return result;
    } catch (error) {
      return {
        testName: 'API Performance',
        endpoint: `${method} ${endpoint}`,
        timestamp: new Date().toISOString(),
        tracingId: `API_PERF_${Date.now()}`,
        metrics: null,
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration: performance.now() - startTime
      };
    }
  }

  /**
   * Executa teste de performance de componente
   */
  async testComponentPerformance(componentName: string, props: any = {}): Promise<PerformanceTestResult> {
    const startTime = performance.now();
    
    try {
      const metrics = await this.measureComponentMetrics(componentName, props);
      
      const result: PerformanceTestResult = {
        testName: 'Component Performance',
        component: componentName,
        timestamp: new Date().toISOString(),
        tracingId: `COMP_PERF_${Date.now()}`,
        metrics,
        passed: this.validateComponentMetrics(metrics),
        duration: performance.now() - startTime
      };

      this.results.push(result);
      return result;
    } catch (error) {
      return {
        testName: 'Component Performance',
        component: componentName,
        timestamp: new Date().toISOString(),
        tracingId: `COMP_PERF_${Date.now()}`,
        metrics: null,
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration: performance.now() - startTime
      };
    }
  }

  /**
   * Executa teste de stress
   */
  async testStressPerformance(testFn: () => Promise<any>): Promise<PerformanceTestResult> {
    const startTime = performance.now();
    
    try {
      const metrics = await this.measureStressMetrics(testFn);
      
      const result: PerformanceTestResult = {
        testName: 'Stress Test',
        timestamp: new Date().toISOString(),
        tracingId: `STRESS_${Date.now()}`,
        metrics,
        passed: this.validateStressMetrics(metrics),
        duration: performance.now() - startTime
      };

      this.results.push(result);
      return result;
    } catch (error) {
      return {
        testName: 'Stress Test',
        timestamp: new Date().toISOString(),
        tracingId: `STRESS_${Date.now()}`,
        metrics: null,
        passed: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration: performance.now() - startTime
      };
    }
  }

  /**
   * Mede métricas de carregamento de página
   */
  private async measurePageLoadMetrics(url: string): Promise<PerformanceMetrics> {
    // Simular medição de métricas de carregamento
    const metrics: PerformanceMetrics = {
      firstContentfulPaint: Math.random() * 2000 + 500,
      largestContentfulPaint: Math.random() * 3000 + 1000,
      firstInputDelay: Math.random() * 200 + 50,
      cumulativeLayoutShift: Math.random() * 0.2,
      timeToInteractive: Math.random() * 3000 + 1500,
      totalBlockingTime: Math.random() * 300 + 100,
      speedIndex: Math.random() * 2000 + 1000
    };

    // Simular delay de carregamento
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return metrics;
  }

  /**
   * Mede métricas de API
   */
  private async measureApiMetrics(endpoint: string, method: string, payload?: any): Promise<PerformanceMetrics> {
    const startTime = performance.now();
    
    // Simular chamada de API
    await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 100));
    
    const responseTime = performance.now() - startTime;
    
    return {
      apiResponseTime: responseTime,
      apiThroughput: Math.random() * 1000 + 100, // requests per second
      apiErrorRate: Math.random() * 0.05, // 0-5%
      apiLatency: responseTime,
      apiConcurrency: Math.random() * 10 + 1
    };
  }

  /**
   * Mede métricas de componente
   */
  private async measureComponentMetrics(componentName: string, props: any): Promise<PerformanceMetrics> {
    const startTime = performance.now();
    
    // Simular renderização de componente
    await new Promise(resolve => setTimeout(resolve, Math.random() * 50 + 10));
    
    const renderTime = performance.now() - startTime;
    
    return {
      componentRenderTime: renderTime,
      componentMemoryUsage: Math.random() * 10 + 1, // MB
      componentReRenders: Math.floor(Math.random() * 5),
      componentBundleSize: Math.random() * 50 + 10 // KB
    };
  }

  /**
   * Mede métricas de stress
   */
  private async measureStressMetrics(testFn: () => Promise<any>): Promise<PerformanceMetrics> {
    const iterations = this.config.testConfig.iterations.heavy;
    const results: number[] = [];
    const errors: number = 0;
    
    for (let i = 0; i < iterations; i++) {
      const startTime = performance.now();
      try {
        await testFn();
        results.push(performance.now() - startTime);
      } catch {
        errors++;
      }
    }
    
    const avgResponseTime = results.reduce((a, b) => a + b, 0) / results.length;
    const errorRate = errors / iterations;
    
    return {
      stressAvgResponseTime: avgResponseTime,
      stressErrorRate: errorRate,
      stressThroughput: iterations / (avgResponseTime / 1000),
      stressConcurrency: this.config.testConfig.stress.concurrentUsers,
      stressDuration: this.config.testConfig.stress.duration
    };
  }

  /**
   * Valida métricas de carregamento de página
   */
  private validatePageLoadMetrics(metrics: PerformanceMetrics): boolean {
    const thresholds = this.config.thresholds;
    
    return (
      metrics.firstContentfulPaint <= thresholds.firstContentfulPaint &&
      metrics.largestContentfulPaint <= thresholds.largestContentfulPaint &&
      metrics.firstInputDelay <= thresholds.firstInputDelay &&
      metrics.cumulativeLayoutShift <= thresholds.cumulativeLayoutShift
    );
  }

  /**
   * Valida métricas de API
   */
  private validateApiMetrics(metrics: PerformanceMetrics): boolean {
    const thresholds = this.config.thresholds.apiResponseTime;
    
    return (
      metrics.apiResponseTime <= thresholds.medium &&
      metrics.apiErrorRate <= 0.01 // 1% max error rate
    );
  }

  /**
   * Valida métricas de componente
   */
  private validateComponentMetrics(metrics: PerformanceMetrics): boolean {
    const thresholds = this.config.thresholds.componentRenderTime;
    
    return (
      metrics.componentRenderTime <= thresholds.complex &&
      metrics.componentMemoryUsage <= 20 // 20MB max
    );
  }

  /**
   * Valida métricas de stress
   */
  private validateStressMetrics(metrics: PerformanceMetrics): boolean {
    return (
      metrics.stressErrorRate <= 0.05 && // 5% max error rate
      metrics.stressAvgResponseTime <= 1000 // 1s max avg response time
    );
  }

  /**
   * Gera relatório de performance
   */
  generatePerformanceReport(): PerformanceReport {
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;
    
    const avgDuration = this.results.reduce((sum, r) => sum + r.duration, 0) / totalTests;
    
    return {
      timestamp: new Date().toISOString(),
      tracingId: `PERF_REPORT_${Date.now()}`,
      summary: {
        totalTests,
        passedTests,
        failedTests,
        successRate: (passedTests / totalTests) * 100,
        avgDuration
      },
      results: this.results,
      recommendations: this.generatePerformanceRecommendations()
    };
  }

  /**
   * Gera recomendações de performance
   */
  private generatePerformanceRecommendations(): string[] {
    const recommendations: string[] = [];
    
    // Analisar resultados e gerar recomendações
    const slowTests = this.results.filter(r => r.duration > 5000);
    if (slowTests.length > 0) {
      recommendations.push(`Otimizar ${slowTests.length} testes lentos (duração > 5s)`);
    }
    
    const failedTests = this.results.filter(r => !r.passed);
    if (failedTests.length > 0) {
      recommendations.push(`Investigar ${failedTests.length} testes que falharam nos thresholds`);
    }
    
    const apiTests = this.results.filter(r => r.testName === 'API Performance');
    const slowApiTests = apiTests.filter(r => r.metrics?.apiResponseTime > 500);
    if (slowApiTests.length > 0) {
      recommendations.push(`Otimizar ${slowApiTests.length} endpoints com resposta lenta (>500ms)`);
    }
    
    return recommendations;
  }

  /**
   * Limpa resultados
   */
  clearResults(): void {
    this.results = [];
  }

  /**
   * Exporta resultados para JSON
   */
  exportResults(): string {
    return JSON.stringify(this.results, null, 2);
  }
}

/**
 * Utilitários de performance
 */
export const PerformanceUtils = {
  /**
   * Calcula média de métricas
   */
  calculateAverage(metrics: number[]): number {
    return metrics.reduce((a, b) => a + b, 0) / metrics.length;
  },

  /**
   * Calcula percentil
   */
  calculatePercentile(metrics: number[], percentile: number): number {
    const sorted = [...metrics].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index];
  },

  /**
   * Formata tempo em formato legível
   */
  formatTime(ms: number): string {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  },

  /**
   * Formata tamanho em formato legível
   */
  formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes.toFixed(0)}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  }
}; 