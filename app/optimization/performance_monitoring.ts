/**
 * Sistema de Monitoramento de Performance
 * Acompanha métricas de performance em tempo real
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';

// Tipos para monitoramento de performance
interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: Date;
  category: 'loading' | 'rendering' | 'memory' | 'network' | 'user' | 'custom';
}

interface PerformanceThreshold {
  metric: string;
  warning: number;
  critical: number;
  action?: 'alert' | 'log' | 'callback';
}

interface PerformanceAlert {
  id: string;
  metric: string;
  value: number;
  threshold: number;
  severity: 'warning' | 'critical';
  timestamp: Date;
  message: string;
}

interface PerformanceConfig {
  enableRealTimeMonitoring: boolean;
  enableMemoryTracking: boolean;
  enableNetworkTracking: boolean;
  enableUserMetrics: boolean;
  alertThresholds: PerformanceThreshold[];
  samplingInterval: number;
  maxDataPoints: number;
}

// Configuração padrão
const DEFAULT_CONFIG: PerformanceConfig = {
  enableRealTimeMonitoring: true,
  enableMemoryTracking: true,
  enableNetworkTracking: true,
  enableUserMetrics: true,
  alertThresholds: [
    { metric: 'pageLoadTime', warning: 3000, critical: 5000 },
    { metric: 'firstContentfulPaint', warning: 1500, critical: 2500 },
    { metric: 'largestContentfulPaint', warning: 2500, critical: 4000 },
    { metric: 'memoryUsage', warning: 50 * 1024 * 1024, critical: 100 * 1024 * 1024 }
  ],
  samplingInterval: 1000,
  maxDataPoints: 1000
};

/**
 * Monitor de Performance
 */
class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private alerts: PerformanceAlert[] = [];
  private config: PerformanceConfig;
  private observers: Array<(metrics: PerformanceMetric[]) => void> = [];
  private alertObservers: Array<(alert: PerformanceAlert) => void> = [];
  private interval: NodeJS.Timeout | null = null;
  private performanceObserver: PerformanceObserver | null = null;

  constructor(config: PerformanceConfig = DEFAULT_CONFIG) {
    this.config = config;
    this.initializeMonitoring();
  }

  /**
   * Inicializa monitoramento
   */
  private initializeMonitoring() {
    if (this.config.enableRealTimeMonitoring) {
      this.startRealTimeMonitoring();
    }

    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      this.setupPerformanceObserver();
    }
  }

  /**
   * Configura Performance Observer
   */
  private setupPerformanceObserver() {
    try {
      // Monitorar métricas de paint
      this.performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          this.recordMetric({
            name: entry.name,
            value: entry.startTime,
            unit: 'ms',
            timestamp: new Date(),
            category: 'rendering'
          });
        });
      });

      this.performanceObserver.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
    } catch (error) {
      console.warn('PerformanceObserver not supported:', error);
    }
  }

  /**
   * Inicia monitoramento em tempo real
   */
  private startRealTimeMonitoring() {
    this.interval = setInterval(() => {
      this.collectMetrics();
    }, this.config.samplingInterval);
  }

  /**
   * Coleta métricas do sistema
   */
  private collectMetrics() {
    // Métricas de memória
    if (this.config.enableMemoryTracking && 'memory' in performance) {
      const memory = (performance as any).memory;
      this.recordMetric({
        name: 'memoryUsage',
        value: memory.usedJSHeapSize,
        unit: 'bytes',
        timestamp: new Date(),
        category: 'memory'
      });

      this.recordMetric({
        name: 'memoryLimit',
        value: memory.jsHeapSizeLimit,
        unit: 'bytes',
        timestamp: new Date(),
        category: 'memory'
      });
    }

    // Métricas de rede
    if (this.config.enableNetworkTracking) {
      this.collectNetworkMetrics();
    }

    // Métricas de usuário
    if (this.config.enableUserMetrics) {
      this.collectUserMetrics();
    }
  }

  /**
   * Coleta métricas de rede
   */
  private collectNetworkMetrics() {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      
      this.recordMetric({
        name: 'networkSpeed',
        value: connection.downlink || 0,
        unit: 'Mbps',
        timestamp: new Date(),
        category: 'network'
      });

      this.recordMetric({
        name: 'networkLatency',
        value: connection.rtt || 0,
        unit: 'ms',
        timestamp: new Date(),
        category: 'network'
      });
    }
  }

  /**
   * Coleta métricas de usuário
   */
  private collectUserMetrics() {
    // Tempo de interação
    if ('interactionCount' in performance) {
      this.recordMetric({
        name: 'interactionCount',
        value: (performance as any).interactionCount,
        unit: 'count',
        timestamp: new Date(),
        category: 'user'
      });
    }

    // FPS (Frames Per Second)
    this.measureFPS();
  }

  /**
   * Mede FPS
   */
  private measureFPS() {
    let frameCount = 0;
    let lastTime = performance.now();

    const measureFrame = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        
        this.recordMetric({
          name: 'fps',
          value: fps,
          unit: 'fps',
          timestamp: new Date(),
          category: 'user'
        });

        frameCount = 0;
        lastTime = currentTime;
      }

      requestAnimationFrame(measureFrame);
    };

    requestAnimationFrame(measureFrame);
  }

  /**
   * Registra uma métrica
   */
  recordMetric(metric: PerformanceMetric) {
    this.metrics.push(metric);

    // Limitar número de métricas
    if (this.metrics.length > this.config.maxDataPoints) {
      this.metrics.shift();
    }

    // Verificar thresholds
    this.checkThresholds(metric);

    // Notificar observers
    this.notifyObservers();
  }

  /**
   * Verifica thresholds
   */
  private checkThresholds(metric: PerformanceMetric) {
    this.config.alertThresholds.forEach(threshold => {
      if (threshold.metric === metric.name) {
        if (metric.value >= threshold.critical) {
          this.createAlert(metric, threshold.critical, 'critical');
        } else if (metric.value >= threshold.warning) {
          this.createAlert(metric, threshold.warning, 'warning');
        }
      }
    });
  }

  /**
   * Cria alerta
   */
  private createAlert(metric: PerformanceMetric, threshold: number, severity: 'warning' | 'critical') {
    const alert: PerformanceAlert = {
      id: `${metric.name}-${Date.now()}`,
      metric: metric.name,
      value: metric.value,
      threshold,
      severity,
      timestamp: new Date(),
      message: `${metric.name} atingiu ${severity === 'critical' ? 'nível crítico' : 'nível de alerta'}: ${metric.value}${metric.unit}`
    };

    this.alerts.push(alert);
    this.notifyAlertObservers(alert);
  }

  /**
   * Obtém métricas por categoria
   */
  getMetricsByCategory(category: string): PerformanceMetric[] {
    return this.metrics.filter(metric => metric.category === category);
  }

  /**
   * Obtém métricas por nome
   */
  getMetricsByName(name: string): PerformanceMetric[] {
    return this.metrics.filter(metric => metric.name === name);
  }

  /**
   * Obtém métricas recentes
   */
  getRecentMetrics(minutes: number = 5): PerformanceMetric[] {
    const cutoff = new Date(Date.now() - minutes * 60 * 1000);
    return this.metrics.filter(metric => metric.timestamp > cutoff);
  }

  /**
   * Obtém estatísticas de uma métrica
   */
  getMetricStats(name: string) {
    const metrics = this.getMetricsByName(name);
    if (metrics.length === 0) return null;

    const values = metrics.map(m => m.value);
    return {
      name,
      count: metrics.length,
      average: values.reduce((sum, val) => sum + val, 0) / values.length,
      min: Math.min(...values),
      max: Math.max(...values),
      latest: values[values.length - 1]
    };
  }

  /**
   * Obtém alertas
   */
  getAlerts(severity?: 'warning' | 'critical'): PerformanceAlert[] {
    if (severity) {
      return this.alerts.filter(alert => alert.severity === severity);
    }
    return this.alerts;
  }

  /**
   * Adiciona observer
   */
  addObserver(observer: (metrics: PerformanceMetric[]) => void) {
    this.observers.push(observer);
  }

  /**
   * Remove observer
   */
  removeObserver(observer: (metrics: PerformanceMetric[]) => void) {
    const index = this.observers.indexOf(observer);
    if (index > -1) {
      this.observers.splice(index, 1);
    }
  }

  /**
   * Adiciona alert observer
   */
  addAlertObserver(observer: (alert: PerformanceAlert) => void) {
    this.alertObservers.push(observer);
  }

  /**
   * Remove alert observer
   */
  removeAlertObserver(observer: (alert: PerformanceAlert) => void) {
    const index = this.alertObservers.indexOf(observer);
    if (index > -1) {
      this.alertObservers.splice(index, 1);
    }
  }

  /**
   * Notifica observers
   */
  private notifyObservers() {
    this.observers.forEach(observer => {
      try {
        observer([...this.metrics]);
      } catch (error) {
        console.error('Error in performance observer:', error);
      }
    });
  }

  /**
   * Notifica alert observers
   */
  private notifyAlertObservers(alert: PerformanceAlert) {
    this.alertObservers.forEach(observer => {
      try {
        observer(alert);
      } catch (error) {
        console.error('Error in alert observer:', error);
      }
    });
  }

  /**
   * Para monitoramento
   */
  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }

    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
      this.performanceObserver = null;
    }
  }

  /**
   * Limpa dados
   */
  clear() {
    this.metrics = [];
    this.alerts = [];
  }
}

// Instância global do monitor
export const performanceMonitor = new PerformanceMonitor();

/**
 * Hook para monitoramento de performance
 */
export function usePerformanceMonitoring() {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);

  useEffect(() => {
    const metricsObserver = (newMetrics: PerformanceMetric[]) => {
      setMetrics(newMetrics);
    };

    const alertObserver = (alert: PerformanceAlert) => {
      setAlerts(prev => [...prev, alert]);
    };

    performanceMonitor.addObserver(metricsObserver);
    performanceMonitor.addAlertObserver(alertObserver);

    return () => {
      performanceMonitor.removeObserver(metricsObserver);
      performanceMonitor.removeAlertObserver(alertObserver);
    };
  }, []);

  return { metrics, alerts };
}

/**
 * Hook para métricas específicas
 */
export function useMetric(name: string) {
  const [metric, setMetric] = useState<PerformanceMetric | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const observer = (metrics: PerformanceMetric[]) => {
      const latestMetric = metrics
        .filter(m => m.name === name)
        .pop();

      if (latestMetric) {
        setMetric(latestMetric);
        setStats(performanceMonitor.getMetricStats(name));
      }
    };

    performanceMonitor.addObserver(observer);

    return () => {
      performanceMonitor.removeObserver(observer);
    };
  }, [name]);

  return { metric, stats };
}

/**
 * Componente de dashboard de performance
 */
export function PerformanceDashboard() {
  const { metrics, alerts } = usePerformanceMonitoring();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = ['all', 'loading', 'rendering', 'memory', 'network', 'user', 'custom'];
  
  const filteredMetrics = selectedCategory === 'all' 
    ? metrics 
    : metrics.filter(m => m.category === selectedCategory);

  const recentAlerts = alerts.slice(-5);

  return (
    <div className="performance-dashboard">
      <h2>Dashboard de Performance</h2>
      
      {/* Filtros */}
      <div className="filters">
        <select 
          value={selectedCategory} 
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          {categories.map(category => (
            <option key={category} value={category}>
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Métricas em tempo real */}
      <div className="real-time-metrics">
        <h3>Métricas em Tempo Real</h3>
        <div className="metrics-grid">
          {filteredMetrics.slice(-10).map((metric, index) => (
            <div key={index} className="metric-card">
              <h4>{metric.name}</h4>
              <p className="value">{metric.value}{metric.unit}</p>
              <p className="timestamp">{metric.timestamp.toLocaleTimeString()}</p>
              <span className={`category ${metric.category}`}>{metric.category}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Alertas */}
      {recentAlerts.length > 0 && (
        <div className="alerts">
          <h3>Alertas Recentes</h3>
          {recentAlerts.map(alert => (
            <div key={alert.id} className={`alert ${alert.severity}`}>
              <h4>{alert.metric}</h4>
              <p>{alert.message}</p>
              <p className="timestamp">{alert.timestamp.toLocaleTimeString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Componente de gráfico de performance
 */
export function PerformanceChart({ metricName }: { metricName: string }) {
  const { stats } = useMetric(metricName);
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    const observer = (metrics: PerformanceMetric[]) => {
      const metricData = metrics
        .filter(m => m.name === metricName)
        .slice(-50)
        .map(m => ({
          time: m.timestamp.getTime(),
          value: m.value
        }));

      setChartData(metricData);
    };

    performanceMonitor.addObserver(observer);

    return () => {
      performanceMonitor.removeObserver(observer);
    };
  }, [metricName]);

  if (!stats) {
    return <div>Carregando dados...</div>;
  }

  return (
    <div className="performance-chart">
      <h3>{metricName}</h3>
      
      <div className="stats">
        <div className="stat">
          <span>Média:</span>
          <span>{stats.average.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span>Mín:</span>
          <span>{stats.min.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span>Máx:</span>
          <span>{stats.max.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span>Atual:</span>
          <span>{stats.latest.toFixed(2)}</span>
        </div>
      </div>

      {/* Aqui você pode integrar com uma biblioteca de gráficos como Chart.js ou Recharts */}
      <div className="chart-placeholder">
        <p>Gráfico de {metricName}</p>
        <p>{chartData.length} pontos de dados</p>
      </div>
    </div>
  );
}

/**
 * Hook para métricas de carregamento de página
 */
export function usePageLoadMetrics() {
  const [pageLoadTime, setPageLoadTime] = useState<number>(0);
  const [firstContentfulPaint, setFirstContentfulPaint] = useState<number>(0);
  const [largestContentfulPaint, setLargestContentfulPaint] = useState<number>(0);

  useEffect(() => {
    // Tempo de carregamento da página
    if (performance.timing) {
      const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
      setPageLoadTime(loadTime);
      
      performanceMonitor.recordMetric({
        name: 'pageLoadTime',
        value: loadTime,
        unit: 'ms',
        timestamp: new Date(),
        category: 'loading'
      });
    }

    // First Contentful Paint
    if ('PerformanceObserver' in window) {
      const paintObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.name === 'first-contentful-paint') {
            setFirstContentfulPaint(entry.startTime);
            performanceMonitor.recordMetric({
              name: 'firstContentfulPaint',
              value: entry.startTime,
              unit: 'ms',
              timestamp: new Date(),
              category: 'loading'
            });
          }
        });
      });

      paintObserver.observe({ entryTypes: ['paint'] });
    }

    // Largest Contentful Paint
    if ('PerformanceObserver' in window) {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        setLargestContentfulPaint(lastEntry.startTime);
        
        performanceMonitor.recordMetric({
          name: 'largestContentfulPaint',
          value: lastEntry.startTime,
          unit: 'ms',
          timestamp: new Date(),
          category: 'loading'
        });
      });

      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    }
  }, []);

  return { pageLoadTime, firstContentfulPaint, largestContentfulPaint };
}

/**
 * Utilitários para monitoramento de performance
 */
export const PerformanceMonitoringUtils = {
  /**
   * Registra métrica customizada
   */
  recordCustomMetric: (name: string, value: number, unit: string = '') => {
    performanceMonitor.recordMetric({
      name,
      value,
      unit,
      timestamp: new Date(),
      category: 'custom'
    });
  },

  /**
   * Mede tempo de execução de função
   */
  measureExecutionTime: (fn: () => void, name: string) => {
    const start = performance.now();
    fn();
    const end = performance.now();
    
    performanceMonitor.recordMetric({
      name: `${name}ExecutionTime`,
      value: end - start,
      unit: 'ms',
      timestamp: new Date(),
      category: 'custom'
    });
  },

  /**
   * Exporta relatório de performance
   */
  exportReport: () => {
    const metrics = performanceMonitor.getRecentMetrics(60); // Última hora
    const alerts = performanceMonitor.getAlerts();
    
    return {
      metrics,
      alerts,
      summary: {
        totalMetrics: metrics.length,
        totalAlerts: alerts.length,
        criticalAlerts: alerts.filter(a => a.severity === 'critical').length,
        timestamp: new Date().toISOString()
      }
    };
  },

  /**
   * Limpa dados
   */
  clearData: () => {
    performanceMonitor.clear();
  }
};

// Estilos CSS para componentes
export const performanceMonitoringStyles = `
  .performance-dashboard {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .filters {
    margin-bottom: 20px;
  }

  .filters select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
  }

  .metric-card {
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .metric-card h4 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 14px;
  }

  .metric-card .value {
    font-size: 24px;
    font-weight: bold;
    margin: 0 0 5px 0;
    color: #007bff;
  }

  .metric-card .timestamp {
    font-size: 12px;
    color: #666;
    margin: 0 0 5px 0;
  }

  .metric-card .category {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 10px;
    text-transform: uppercase;
    font-weight: bold;
  }

  .category.loading { background: #e3f2fd; color: #1976d2; }
  .category.rendering { background: #f3e5f5; color: #7b1fa2; }
  .category.memory { background: #fff3e0; color: #f57c00; }
  .category.network { background: #e8f5e8; color: #388e3c; }
  .category.user { background: #fce4ec; color: #c2185b; }
  .category.custom { background: #f1f8e9; color: #689f38; }

  .alerts {
    margin-top: 30px;
  }

  .alert {
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    border-left: 4px solid #ddd;
  }

  .alert.warning {
    border-left-color: #ffc107;
    background: #fff8e1;
  }

  .alert.critical {
    border-left-color: #dc3545;
    background: #ffebee;
  }

  .alert h4 {
    margin: 0 0 5px 0;
    color: #333;
  }

  .alert p {
    margin: 0 0 5px 0;
    color: #666;
  }

  .performance-chart {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }

  .stat {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 4px;
  }

  .chart-placeholder {
    height: 200px;
    background: #f8f9fa;
    border: 2px dashed #ddd;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #666;
  }
`; 