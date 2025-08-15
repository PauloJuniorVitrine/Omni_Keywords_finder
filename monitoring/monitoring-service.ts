/**
 * Sistema de Monitoring
 * 
 * Prompt: Implementação de itens de criticidade baixa - 11.4
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { env } from '../config/environment';

// Tipos para métricas
interface Metric {
  name: string;
  value: number;
  timestamp: number;
  tags: Record<string, string>;
  type: 'counter' | 'gauge' | 'histogram';
}

interface Alert {
  id: string;
  name: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: number;
  resolved: boolean;
  metadata: Record<string, any>;
}

interface HealthCheck {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  responseTime: number;
  lastCheck: number;
  error?: string;
}

/**
 * Classe principal de monitoring
 */
export class MonitoringService {
  private metrics: Metric[] = [];
  private alerts: Alert[] = [];
  private healthChecks: Map<string, HealthCheck> = new Map();
  private isEnabled: boolean;

  constructor() {
    this.isEnabled = env.ENABLE_TELEMETRY;
    this.initializeMonitoring();
  }

  /**
   * Inicializa o sistema de monitoring
   */
  private initializeMonitoring(): void {
    if (!this.isEnabled) {
      console.log('[MONITORING] Sistema de monitoring desabilitado');
      return;
    }

    // Configurar coleta automática de métricas
    this.setupAutomaticMetrics();
    
    // Configurar health checks
    this.setupHealthChecks();
    
    // Configurar alertas
    this.setupAlerts();
    
    console.log('[MONITORING] Sistema de monitoring inicializado');
  }

  /**
   * Configura métricas automáticas
   */
  private setupAutomaticMetrics(): void {
    // Métricas de performance
    setInterval(() => {
      this.recordMetric('memory_usage', process.memoryUsage().heapUsed / 1024 / 1024, {
        type: 'gauge',
        tags: { component: 'system' }
      });
      
      this.recordMetric('cpu_usage', process.cpuUsage().user / 1000000, {
        type: 'gauge',
        tags: { component: 'system' }
      });
    }, 30000); // A cada 30 segundos

    // Métricas de uptime
    setInterval(() => {
      this.recordMetric('uptime_seconds', process.uptime(), {
        type: 'gauge',
        tags: { component: 'system' }
      });
    }, 60000); // A cada minuto
  }

  /**
   * Configura health checks
   */
  private setupHealthChecks(): void {
    // Health check da API
    this.addHealthCheck('api_health', async () => {
      try {
        const start = Date.now();
        const response = await fetch(`${env.API_BASE_URL}/health`);
        const responseTime = Date.now() - start;
        
        return {
          status: response.ok ? 'healthy' : 'degraded',
          responseTime,
          error: response.ok ? undefined : `HTTP ${response.status}`
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          responseTime: 0,
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    });

    // Health check do banco de dados
    this.addHealthCheck('database_health', async () => {
      try {
        const start = Date.now();
        // Aqui você implementaria a verificação real do banco
        const responseTime = Date.now() - start;
        
        return {
          status: 'healthy',
          responseTime,
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          responseTime: 0,
          error: error instanceof Error ? error.message : 'Database connection failed'
        };
      }
    });
  }

  /**
   * Configura alertas
   */
  private setupAlerts(): void {
    // Alerta para alta utilização de memória
    this.addAlertRule('high_memory_usage', {
      condition: (metrics) => {
        const memoryMetric = metrics.find(m => m.name === 'memory_usage');
        return memoryMetric && memoryMetric.value > 500; // 500MB
      },
      severity: 'medium',
      message: 'Alta utilização de memória detectada'
    });

    // Alerta para health checks falhando
    this.addAlertRule('health_check_failure', {
      condition: () => {
        const unhealthyChecks = Array.from(this.healthChecks.values())
          .filter(check => check.status === 'unhealthy');
        return unhealthyChecks.length > 0;
      },
      severity: 'high',
      message: 'Health checks falhando'
    });
  }

  /**
   * Registra uma métrica
   */
  public recordMetric(
    name: string, 
    value: number, 
    options: { type: 'counter' | 'gauge' | 'histogram'; tags?: Record<string, string> }
  ): void {
    if (!this.isEnabled) return;

    const metric: Metric = {
      name,
      value,
      timestamp: Date.now(),
      tags: options.tags || {},
      type: options.type
    };

    this.metrics.push(metric);
    
    // Limitar histórico de métricas
    if (this.metrics.length > 10000) {
      this.metrics = this.metrics.slice(-5000);
    }

    // Verificar regras de alerta
    this.checkAlertRules();
  }

  /**
   * Adiciona um health check
   */
  public addHealthCheck(
    name: string, 
    checkFunction: () => Promise<{ status: string; responseTime: number; error?: string }>
  ): void {
    const runCheck = async () => {
      try {
        const result = await checkFunction();
        this.healthChecks.set(name, {
          name,
          status: result.status as 'healthy' | 'degraded' | 'unhealthy',
          responseTime: result.responseTime,
          lastCheck: Date.now(),
          error: result.error
        });
      } catch (error) {
        this.healthChecks.set(name, {
          name,
          status: 'unhealthy',
          responseTime: 0,
          lastCheck: Date.now(),
          error: error instanceof Error ? error.message : 'Check failed'
        });
      }
    };

    // Executar imediatamente
    runCheck();
    
    // Executar periodicamente
    setInterval(runCheck, 60000); // A cada minuto
  }

  /**
   * Adiciona uma regra de alerta
   */
  public addAlertRule(
    name: string, 
    rule: { 
      condition: (metrics: Metric[]) => boolean; 
      severity: Alert['severity']; 
      message: string;
    }
  ): void {
    // Implementação simplificada - em produção você usaria um sistema mais robusto
    const checkRule = () => {
      if (rule.condition(this.metrics)) {
        this.createAlert(name, rule.severity, rule.message);
      }
    };

    setInterval(checkRule, 30000); // Verificar a cada 30 segundos
  }

  /**
   * Cria um alerta
   */
  public createAlert(
    name: string, 
    severity: Alert['severity'], 
    message: string, 
    metadata: Record<string, any> = {}
  ): void {
    const alert: Alert = {
      id: `${name}_${Date.now()}`,
      name,
      severity,
      message,
      timestamp: Date.now(),
      resolved: false,
      metadata
    };

    this.alerts.push(alert);
    
    // Notificar alertas críticos
    if (severity === 'critical') {
      this.notifyCriticalAlert(alert);
    }

    console.log(`[MONITORING] Alerta criado: ${name} - ${severity} - ${message}`);
  }

  /**
   * Verifica regras de alerta
   */
  private checkAlertRules(): void {
    // Implementação seria baseada nas regras configuradas
  }

  /**
   * Notifica alertas críticos
   */
  private notifyCriticalAlert(alert: Alert): void {
    // Em produção, você enviaria para Slack, email, etc.
    console.error(`[MONITORING] ALERTA CRÍTICO: ${alert.name} - ${alert.message}`);
  }

  /**
   * Obtém métricas
   */
  public getMetrics(filter?: { name?: string; tags?: Record<string, string> }): Metric[] {
    let filtered = this.metrics;

    if (filter?.name) {
      filtered = filtered.filter(m => m.name === filter.name);
    }

    if (filter?.tags) {
      filtered = filtered.filter(m => 
        Object.entries(filter.tags!).every(([key, value]) => m.tags[key] === value)
      );
    }

    return filtered;
  }

  /**
   * Obtém alertas
   */
  public getAlerts(filter?: { severity?: Alert['severity']; resolved?: boolean }): Alert[] {
    let filtered = this.alerts;

    if (filter?.severity) {
      filtered = filtered.filter(a => a.severity === filter.severity);
    }

    if (filter?.resolved !== undefined) {
      filtered = filtered.filter(a => a.resolved === filter.resolved);
    }

    return filtered;
  }

  /**
   * Obtém status dos health checks
   */
  public getHealthStatus(): HealthCheck[] {
    return Array.from(this.healthChecks.values());
  }

  /**
   * Resolve um alerta
   */
  public resolveAlert(alertId: string): void {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      console.log(`[MONITORING] Alerta resolvido: ${alertId}`);
    }
  }

  /**
   * Gera relatório de monitoring
   */
  public generateReport(): {
    metrics: { total: number; byType: Record<string, number> };
    alerts: { total: number; bySeverity: Record<string, number> };
    healthChecks: { total: number; healthy: number; degraded: number; unhealthy: number };
    uptime: number;
  } {
    const metricsByType = this.metrics.reduce((acc, metric) => {
      acc[metric.type] = (acc[metric.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const alertsBySeverity = this.alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const healthChecks = Array.from(this.healthChecks.values());
    const healthStatus = healthChecks.reduce((acc, check) => {
      acc[check.status] = (acc[check.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      metrics: {
        total: this.metrics.length,
        byType: metricsByType
      },
      alerts: {
        total: this.alerts.length,
        bySeverity: alertsBySeverity
      },
      healthChecks: {
        total: healthChecks.length,
        healthy: healthStatus.healthy || 0,
        degraded: healthStatus.degraded || 0,
        unhealthy: healthStatus.unhealthy || 0
      },
      uptime: process.uptime()
    };
  }
}

// Instância singleton
export const monitoringService = new MonitoringService();

/**
 * Hook para usar o monitoring service
 */
export function useMonitoring() {
  return {
    recordMetric: monitoringService.recordMetric.bind(monitoringService),
    createAlert: monitoringService.createAlert.bind(monitoringService),
    getMetrics: monitoringService.getMetrics.bind(monitoringService),
    getAlerts: monitoringService.getAlerts.bind(monitoringService),
    getHealthStatus: monitoringService.getHealthStatus.bind(monitoringService),
    generateReport: monitoringService.generateReport.bind(monitoringService),
  };
} 