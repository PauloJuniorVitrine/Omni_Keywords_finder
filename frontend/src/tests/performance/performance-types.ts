/**
 * Tipos para Testes de Performance
 * 
 * Prompt: Implementar testes de performance
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: PERF_TYPES_20250127_001
 */

/**
 * Métricas de performance
 */
export interface PerformanceMetrics {
  // Métricas de carregamento de página
  firstContentfulPaint?: number; // ms
  largestContentfulPaint?: number; // ms
  firstInputDelay?: number; // ms
  cumulativeLayoutShift?: number; // score
  timeToInteractive?: number; // ms
  totalBlockingTime?: number; // ms
  speedIndex?: number; // ms

  // Métricas de API
  apiResponseTime?: number; // ms
  apiThroughput?: number; // requests per second
  apiErrorRate?: number; // percentage
  apiLatency?: number; // ms
  apiConcurrency?: number; // concurrent requests

  // Métricas de componente
  componentRenderTime?: number; // ms
  componentMemoryUsage?: number; // MB
  componentReRenders?: number; // count
  componentBundleSize?: number; // KB

  // Métricas de stress
  stressAvgResponseTime?: number; // ms
  stressErrorRate?: number; // percentage
  stressThroughput?: number; // requests per second
  stressConcurrency?: number; // concurrent users
  stressDuration?: number; // ms

  // Métricas de memória
  memoryUsage?: number; // MB
  memoryLeak?: number; // MB per minute
  heapSize?: number; // MB
  heapUsed?: number; // MB

  // Métricas de bundle
  bundleSize?: number; // KB
  bundleSizeGzipped?: number; // KB
  bundleChunks?: number; // count
  bundleLoadTime?: number; // ms
}

/**
 * Thresholds de performance
 */
export interface PerformanceThresholds {
  // Carregamento de página
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  firstInputDelay: number;
  cumulativeLayoutShift: number;

  // API
  apiResponseTime: {
    fast: number;
    medium: number;
    slow: number;
  };

  // Componentes
  componentRenderTime: {
    simple: number;
    complex: number;
    heavy: number;
  };

  // Memória
  memoryUsage: {
    initial: number;
    peak: number;
    leak: number;
  };

  // Bundle
  bundleSize: {
    total: number;
    gzipped: number;
  };
}

/**
 * Resultado de teste de performance
 */
export interface PerformanceTestResult {
  testName: string;
  url?: string;
  endpoint?: string;
  component?: string;
  timestamp: string;
  tracingId: string;
  metrics: PerformanceMetrics | null;
  passed: boolean;
  error?: string;
  duration: number; // ms
  metadata?: Record<string, any>;
}

/**
 * Relatório de performance
 */
export interface PerformanceReport {
  timestamp: string;
  tracingId: string;
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    successRate: number; // percentage
    avgDuration: number; // ms
  };
  results: PerformanceTestResult[];
  recommendations: string[];
  metadata?: Record<string, any>;
}

/**
 * Configuração de teste de performance
 */
export interface PerformanceTestConfig {
  name: string;
  description: string;
  type: 'page-load' | 'api' | 'component' | 'stress' | 'memory' | 'bundle';
  thresholds: Partial<PerformanceThresholds>;
  iterations?: number;
  timeout?: number;
  concurrent?: number;
  metadata?: Record<string, any>;
}

/**
 * Suite de testes de performance
 */
export interface PerformanceTestSuite {
  name: string;
  description: string;
  tests: PerformanceTestConfig[];
  globalThresholds?: PerformanceThresholds;
  metadata?: Record<string, any>;
}

/**
 * Resultado de suite de testes
 */
export interface PerformanceSuiteResult {
  suiteName: string;
  timestamp: string;
  tracingId: string;
  results: PerformanceTestResult[];
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    successRate: number;
    avgDuration: number;
  };
  recommendations: string[];
}

/**
 * Métricas de baseline para comparação
 */
export interface PerformanceBaseline {
  name: string;
  version: string;
  timestamp: string;
  metrics: PerformanceMetrics;
  thresholds: PerformanceThresholds;
  metadata?: Record<string, any>;
}

/**
 * Comparação de performance
 */
export interface PerformanceComparison {
  baseline: PerformanceBaseline;
  current: PerformanceTestResult;
  regression: boolean;
  improvements: string[];
  regressions: string[];
  percentageChange: Record<string, number>;
}

/**
 * Alertas de performance
 */
export interface PerformanceAlert {
  id: string;
  type: 'regression' | 'threshold-exceeded' | 'anomaly';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  metric: string;
  currentValue: number;
  thresholdValue: number;
  timestamp: string;
  tracingId: string;
  recommendations: string[];
}

/**
 * Configuração de monitoramento de performance
 */
export interface PerformanceMonitoringConfig {
  enabled: boolean;
  interval: number; // ms
  thresholds: PerformanceThresholds;
  alerting: {
    enabled: boolean;
    channels: string[];
    severity: 'low' | 'medium' | 'high' | 'critical';
  };
  retention: {
    days: number;
    maxSize: number; // MB
  };
}

/**
 * Dados de telemetria de performance
 */
export interface PerformanceTelemetry {
  timestamp: string;
  tracingId: string;
  sessionId: string;
  userId?: string;
  page: string;
  metrics: PerformanceMetrics;
  userAgent: string;
  connectionType?: string;
  deviceType?: string;
  metadata?: Record<string, any>;
}

/**
 * Agregação de métricas de performance
 */
export interface PerformanceAggregation {
  period: 'hour' | 'day' | 'week' | 'month';
  startTime: string;
  endTime: string;
  metrics: {
    avg: PerformanceMetrics;
    min: PerformanceMetrics;
    max: PerformanceMetrics;
    p95: PerformanceMetrics;
    p99: PerformanceMetrics;
  };
  count: number;
  errors: number;
  errorRate: number;
}

/**
 * Configuração de relatório de performance
 */
export interface PerformanceReportConfig {
  format: 'json' | 'html' | 'csv' | 'pdf';
  include: string[];
  exclude: string[];
  groupBy?: string[];
  sortBy?: string[];
  limit?: number;
  metadata?: Record<string, any>;
}

/**
 * Resultado de análise de performance
 */
export interface PerformanceAnalysis {
  timestamp: string;
  tracingId: string;
  insights: string[];
  bottlenecks: string[];
  opportunities: string[];
  risks: string[];
  recommendations: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
  effort: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
} 