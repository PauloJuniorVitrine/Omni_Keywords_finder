/**
 * Monitor de Performance
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por monitorar métricas de performance da aplicação
 * Inclui Core Web Vitals, métricas customizadas e alertas de performance
 */

import { logger } from './logger';
import { telemetry } from './telemetry';

// Tipos de métricas de performance
export enum PerformanceMetricType {
  // Core Web Vitals
  LARGEST_CONTENTFUL_PAINT = 'LCP',
  FIRST_INPUT_DELAY = 'FID',
  CUMULATIVE_LAYOUT_SHIFT = 'CLS',
  
  // Métricas adicionais
  FIRST_CONTENTFUL_PAINT = 'FCP',
  TIME_TO_INTERACTIVE = 'TTI',
  TOTAL_BLOCKING_TIME = 'TBT',
  SPEED_INDEX = 'SI',
  
  // Métricas customizadas
  CUSTOM = 'CUSTOM'
}

// Interface para métrica de performance
export interface PerformanceMetric {
  name: string;
  type: PerformanceMetricType;
  value: number;
  unit: string;
  timestamp: string;
  url: string;
  userAgent: string;
  threshold?: {
    good: number;
    needsImprovement: number;
    poor: number;
  };
  status: 'good' | 'needs-improvement' | 'poor';
  context?: Record<string, any>;
}

// Interface para configuração do monitor
export interface PerformanceMonitorConfig {
  enabled: boolean;
  enableCoreWebVitals: boolean;
  enableCustomMetrics: boolean;
  enableRealUserMonitoring: boolean;
  enableSyntheticMonitoring: boolean;
  samplingRate: number;
  reportingInterval: number;
  thresholds: Record<PerformanceMetricType, {
    good: number;
    needsImprovement: number;
    poor: number;
  }>;
  enableAlerts: boolean;
  alertThreshold: number;
  enableReporting: boolean;
  endpoint?: string;
}

// Interface para alerta de performance
export interface PerformanceAlert {
  id: string;
  metric: PerformanceMetric;
  severity: 'warning' | 'error' | 'critical';
  message: string;
  timestamp: string;
  context?: Record<string, any>;
}

// Classe principal do Monitor de Performance
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private config: PerformanceMonitorConfig;
  private metrics: PerformanceMetric[] = [];
  private alerts: PerformanceAlert[] = [];
  private observers: Map<string, PerformanceObserver> = new Map();
  private reportingInterval: NodeJS.Timeout | null = null;
  private sessionId: string;

  private constructor(config: Partial<PerformanceMonitorConfig> = {}) {
    this.config = {
      enabled: true,
      enableCoreWebVitals: true,
      enableCustomMetrics: true,
      enableRealUserMonitoring: true,
      enableSyntheticMonitoring: false,
      samplingRate: 1.0,
      reportingInterval: 60000, // 1 minuto
      thresholds: {
        [PerformanceMetricType.LARGEST_CONTENTFUL_PAINT]: { good: 2500, needsImprovement: 4000, poor: 4000 },
        [PerformanceMetricType.FIRST_INPUT_DELAY]: { good: 100, needsImprovement: 300, poor: 300 },
        [PerformanceMetricType.CUMULATIVE_LAYOUT_SHIFT]: { good: 0.1, needsImprovement: 0.25, poor: 0.25 },
        [PerformanceMetricType.FIRST_CONTENTFUL_PAINT]: { good: 1800, needsImprovement: 3000, poor: 3000 },
        [PerformanceMetricType.TIME_TO_INTERACTIVE]: { good: 3800, needsImprovement: 7300, poor: 7300 },
        [PerformanceMetricType.TOTAL_BLOCKING_TIME]: { good: 200, needsImprovement: 600, poor: 600 },
        [PerformanceMetricType.SPEED_INDEX]: { good: 3400, needsImprovement: 5800, poor: 5800 },
        [PerformanceMetricType.CUSTOM]: { good: 0, needsImprovement: 0, poor: 0 }
      },
      enableAlerts: true,
      alertThreshold: 0.1, // 10% das métricas ruins
      enableReporting: true,
      ...config
    };

    this.sessionId = this.generateSessionId();
    this.initialize();
  }

  public static getInstance(config?: Partial<PerformanceMonitorConfig>): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor(config);
    }
    return PerformanceMonitor.instance;
  }

  // Inicializar monitor
  private initialize(): void {
    if (!this.config.enabled) {
      return;
    }

    // Configurar observers para Core Web Vitals
    if (this.config.enableCoreWebVitals) {
      this.setupCoreWebVitalsObservers();
    }

    // Configurar observers para métricas adicionais
    this.setupAdditionalMetricsObservers();

    // Iniciar reporting periódico
    if (this.config.enableReporting) {
      this.startPeriodicReporting();
    }

    // Configurar handlers de página
    this.setupPageHandlers();

    logger.info('[PERFORMANCE_MONITOR] Initialized', {
      sessionId: this.sessionId,
      config: this.config
    });
  }

  // Configurar observers para Core Web Vitals
  private setupCoreWebVitalsObservers(): void {
    if (!window.PerformanceObserver) {
      logger.warn('[PERFORMANCE_MONITOR] PerformanceObserver not supported');
      return;
    }

    // Observer para Largest Contentful Paint (LCP)
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.recordMetric(PerformanceMetricType.LARGEST_CONTENTFUL_PAINT, lastEntry.startTime, 'ms');
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.set('lcp', lcpObserver);
    } catch (error) {
      logger.warn('[PERFORMANCE_MONITOR] Failed to setup LCP observer', { error });
    }

    // Observer para First Input Delay (FID)
    try {
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        for (const entry of entries) {
          const fid = (entry as any).processingStart - entry.startTime;
          this.recordMetric(PerformanceMetricType.FIRST_INPUT_DELAY, fid, 'ms');
        }
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.set('fid', fidObserver);
    } catch (error) {
      logger.warn('[PERFORMANCE_MONITOR] Failed to setup FID observer', { error });
    }

    // Observer para Cumulative Layout Shift (CLS)
    try {
      const clsObserver = new PerformanceObserver((list) => {
        let clsValue = 0;
        const entries = list.getEntries();
        for (const entry of entries) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
        this.recordMetric(PerformanceMetricType.CUMULATIVE_LAYOUT_SHIFT, clsValue, 'score');
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.set('cls', clsObserver);
    } catch (error) {
      logger.warn('[PERFORMANCE_MONITOR] Failed to setup CLS observer', { error });
    }
  }

  // Configurar observers para métricas adicionais
  private setupAdditionalMetricsObservers(): void {
    if (!window.PerformanceObserver) {
      return;
    }

    // Observer para First Contentful Paint (FCP)
    try {
      const fcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
        if (fcpEntry) {
          this.recordMetric(PerformanceMetricType.FIRST_CONTENTFUL_PAINT, fcpEntry.startTime, 'ms');
        }
      });
      fcpObserver.observe({ entryTypes: ['paint'] });
      this.observers.set('fcp', fcpObserver);
    } catch (error) {
      logger.warn('[PERFORMANCE_MONITOR] Failed to setup FCP observer', { error });
    }

    // Observer para Total Blocking Time (TBT)
    try {
      const tbtObserver = new PerformanceObserver((list) => {
        let totalBlockingTime = 0;
        const entries = list.getEntries();
        for (const entry of entries) {
          if (entry.duration > 50) {
            totalBlockingTime += entry.duration - 50;
          }
        }
        this.recordMetric(PerformanceMetricType.TOTAL_BLOCKING_TIME, totalBlockingTime, 'ms');
      });
      tbtObserver.observe({ entryTypes: ['longtask'] });
      this.observers.set('tbt', tbtObserver);
    } catch (error) {
      logger.warn('[PERFORMANCE_MONITOR] Failed to setup TBT observer', { error });
    }
  }

  // Configurar handlers de página
  private setupPageHandlers(): void {
    // Medir métricas quando a página carregar
    window.addEventListener('load', () => {
      setTimeout(() => {
        this.measurePageLoadMetrics();
      }, 0);
    });

    // Medir métricas quando a página ficar visível
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        this.measureVisibilityMetrics();
      }
    });
  }

  // Medir métricas de carregamento da página
  private measurePageLoadMetrics(): void {
    if (!window.performance) {
      return;
    }

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigation) {
      // Time to Interactive (TTI) - aproximação
      const tti = navigation.domInteractive + 5000; // Aproximação simples
      this.recordMetric(PerformanceMetricType.TIME_TO_INTERACTIVE, tti, 'ms');

      // Speed Index (SI) - aproximação baseada em FCP
      const fcp = navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;
      const si = fcp * 1.5; // Aproximação simples
      this.recordMetric(PerformanceMetricType.SPEED_INDEX, si, 'ms');
    }
  }

  // Medir métricas de visibilidade
  private measureVisibilityMetrics(): void {
    // Medir tempo de resposta após a página ficar visível
    const startTime = performance.now();
    
    // Simular interação para medir responsividade
    setTimeout(() => {
      const responseTime = performance.now() - startTime;
      this.recordMetric(PerformanceMetricType.CUSTOM, responseTime, 'ms', {
        name: 'visibility_response_time',
        context: { type: 'visibility_change' }
      });
    }, 100);
  }

  // Registrar métrica
  private recordMetric(
    type: PerformanceMetricType,
    value: number,
    unit: string,
    context?: Record<string, any>
  ): void {
    // Verificar sampling
    if (Math.random() > this.config.samplingRate) {
      return;
    }

    const threshold = this.config.thresholds[type];
    const status = this.getMetricStatus(value, threshold);

    const metric: PerformanceMetric = {
      name: type,
      type,
      value,
      unit,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      threshold,
      status,
      context
    };

    this.metrics.push(metric);

    // Verificar se deve gerar alerta
    if (this.config.enableAlerts && status === 'poor') {
      this.generateAlert(metric);
    }

    // Log da métrica
    logger.info('[PERFORMANCE_MONITOR] Metric recorded', {
      type,
      value,
      unit,
      status,
      url: window.location.href
    });

    // Enviar para telemetria
    if (this.config.enableReporting) {
      telemetry.track('PERFORMANCE', `metric_${type.toLowerCase()}`, {
        value,
        unit,
        status,
        threshold
      }, {
        metric: type,
        status
      });
    }
  }

  // Determinar status da métrica
  private getMetricStatus(value: number, threshold: { good: number; needsImprovement: number; poor: number }): 'good' | 'needs-improvement' | 'poor' {
    if (value <= threshold.good) {
      return 'good';
    } else if (value <= threshold.needsImprovement) {
      return 'needs-improvement';
    } else {
      return 'poor';
    }
  }

  // Gerar alerta de performance
  private generateAlert(metric: PerformanceMetric): void {
    const alert: PerformanceAlert = {
      id: this.generateAlertId(),
      metric,
      severity: this.getAlertSeverity(metric),
      message: `Performance alert: ${metric.name} = ${metric.value}${metric.unit} (${metric.status})`,
      timestamp: new Date().toISOString(),
      context: {
        url: window.location.href,
        userAgent: navigator.userAgent
      }
    };

    this.alerts.push(alert);

    // Log do alerta
    logger.warn('[PERFORMANCE_MONITOR] Alert generated', {
      alertId: alert.id,
      metric: metric.name,
      value: metric.value,
      status: metric.status,
      severity: alert.severity
    });

    // Enviar para telemetria
    telemetry.track('ERROR', 'performance_alert', {
      metric: metric.name,
      value: metric.value,
      status: metric.status,
      severity: alert.severity
    }, {
      type: 'performance_alert',
      severity: alert.severity
    });
  }

  // Determinar severidade do alerta
  private getAlertSeverity(metric: PerformanceMetric): 'warning' | 'error' | 'critical' {
    switch (metric.type) {
      case PerformanceMetricType.LARGEST_CONTENTFUL_PAINT:
      case PerformanceMetricType.FIRST_INPUT_DELAY:
        return 'critical';
      case PerformanceMetricType.CUMULATIVE_LAYOUT_SHIFT:
        return 'error';
      default:
        return 'warning';
    }
  }

  // Registrar métrica customizada
  public recordCustomMetric(
    name: string,
    value: number,
    unit: string,
    context?: Record<string, any>
  ): void {
    this.recordMetric(PerformanceMetricType.CUSTOM, value, unit, {
      name,
      ...context
    });
  }

  // Medir tempo de execução de função
  public measureFunction<T>(
    name: string,
    fn: () => T,
    context?: Record<string, any>
  ): T {
    const startTime = performance.now();
    try {
      const result = fn();
      const duration = performance.now() - startTime;
      
      this.recordCustomMetric(`function_${name}`, duration, 'ms', {
        type: 'function_execution',
        ...context
      });
      
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      
      this.recordCustomMetric(`function_${name}_error`, duration, 'ms', {
        type: 'function_execution_error',
        error: error.message,
        ...context
      });
      
      throw error;
    }
  }

  // Medir tempo de execução de função assíncrona
  public async measureAsyncFunction<T>(
    name: string,
    fn: () => Promise<T>,
    context?: Record<string, any>
  ): Promise<T> {
    const startTime = performance.now();
    try {
      const result = await fn();
      const duration = performance.now() - startTime;
      
      this.recordCustomMetric(`async_function_${name}`, duration, 'ms', {
        type: 'async_function_execution',
        ...context
      });
      
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      
      this.recordCustomMetric(`async_function_${name}_error`, duration, 'ms', {
        type: 'async_function_execution_error',
        error: error.message,
        ...context
      });
      
      throw error;
    }
  }

  // Iniciar reporting periódico
  private startPeriodicReporting(): void {
    this.reportingInterval = setInterval(() => {
      this.reportMetrics();
    }, this.config.reportingInterval);
  }

  // Reportar métricas
  private async reportMetrics(): Promise<void> {
    if (this.metrics.length === 0) {
      return;
    }

    const metricsToReport = this.metrics.splice(0, this.metrics.length);

    try {
      if (this.config.endpoint) {
        const response = await fetch(this.config.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`
          },
          body: JSON.stringify({
            metrics: metricsToReport,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
          })
        });

        if (!response.ok) {
          throw new Error(`Performance reporting failed: ${response.status}`);
        }
      }

      logger.info('[PERFORMANCE_MONITOR] Metrics reported', {
        count: metricsToReport.length,
        sessionId: this.sessionId
      });

    } catch (error) {
      logger.error('[PERFORMANCE_MONITOR] Failed to report metrics', { error });
      
      // Recolocar métricas na fila
      this.metrics.unshift(...metricsToReport);
    }
  }

  // Utilitários
  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateSessionId(): string {
    let sessionId = sessionStorage.getItem('performance_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('performance_session_id', sessionId);
    }
    return sessionId;
  }

  private getAuthToken(): string {
    return localStorage.getItem('authToken') || '';
  }

  // Métodos públicos
  public getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  public getAlerts(): PerformanceAlert[] {
    return [...this.alerts];
  }

  public getMetricsByType(type: PerformanceMetricType): PerformanceMetric[] {
    return this.metrics.filter(metric => metric.type === type);
  }

  public getLatestMetric(type: PerformanceMetricType): PerformanceMetric | undefined {
    const metrics = this.getMetricsByType(type);
    return metrics[metrics.length - 1];
  }

  public getAverageMetric(type: PerformanceMetricType): number | undefined {
    const metrics = this.getMetricsByType(type);
    if (metrics.length === 0) {
      return undefined;
    }
    
    const sum = metrics.reduce((acc, metric) => acc + metric.value, 0);
    return sum / metrics.length;
  }

  public updateConfig(newConfig: Partial<PerformanceMonitorConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  public getConfig(): PerformanceMonitorConfig {
    return { ...this.config };
  }

  public destroy(): void {
    // Desconectar observers
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();

    // Limpar interval
    if (this.reportingInterval) {
      clearInterval(this.reportingInterval);
      this.reportingInterval = null;
    }

    // Limpar dados
    this.metrics = [];
    this.alerts = [];
  }
}

// Instância singleton
export const performanceMonitor = PerformanceMonitor.getInstance();

// Hook para usar performance monitor
export const usePerformanceMonitor = () => {
  return performanceMonitor;
};

// Hook para medir performance
export const usePerformanceMeasurement = () => {
  const measureFunction = <T>(name: string, fn: () => T, context?: Record<string, any>): T => {
    return performanceMonitor.measureFunction(name, fn, context);
  };

  const measureAsyncFunction = async <T>(name: string, fn: () => Promise<T>, context?: Record<string, any>): Promise<T> => {
    return performanceMonitor.measureAsyncFunction(name, fn, context);
  };

  const recordCustomMetric = (name: string, value: number, unit: string, context?: Record<string, any>): void => {
    performanceMonitor.recordCustomMetric(name, value, unit, context);
  };

  return { measureFunction, measureAsyncFunction, recordCustomMetric };
};

export default performanceMonitor; 