/**
 * Sistema de Telemetria
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por coletar dados de telemetria da aplicação
 * Inclui métricas de performance, uso e comportamento do usuário
 */

import { logger } from './logger';

// Tipos de telemetria
export enum TelemetryType {
  PERFORMANCE = 'PERFORMANCE',
  USAGE = 'USAGE',
  ERROR = 'ERROR',
  NAVIGATION = 'NAVIGATION',
  INTERACTION = 'INTERACTION',
  SYSTEM = 'SYSTEM',
  CUSTOM = 'CUSTOM'
}

// Interface para evento de telemetria
export interface TelemetryEvent {
  id: string;
  type: TelemetryType;
  name: string;
  timestamp: string;
  data: Record<string, any>;
  context: {
    userId?: string;
    sessionId: string;
    pageUrl: string;
    userAgent: string;
    viewport: {
      width: number;
      height: number;
    };
    referrer?: string;
  };
  metadata: {
    version: string;
    environment: string;
    tags: Record<string, string>;
  };
}

// Interface para configuração da telemetria
export interface TelemetryConfig {
  enabled: boolean;
  endpoint: string;
  batchSize: number;
  batchTimeout: number;
  enablePerformanceTracking: boolean;
  enableUsageTracking: boolean;
  enableErrorTracking: boolean;
  enableNavigationTracking: boolean;
  enableInteractionTracking: boolean;
  enableSystemTracking: boolean;
  samplingRate: number;
  enableUserTracking: boolean;
  enableSessionTracking: boolean;
  maxEventsInMemory: number;
  flushOnPageUnload: boolean;
}

// Interface para métricas de performance
export interface PerformanceMetrics {
  loadTime: number;
  domContentLoaded: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  firstInputDelay: number;
  cumulativeLayoutShift: number;
  timeToInteractive: number;
  totalBlockingTime: number;
}

// Interface para métricas de sistema
export interface SystemMetrics {
  memory: {
    used: number;
    total: number;
    available: number;
  };
  cpu: {
    cores: number;
    usage?: number;
  };
  network: {
    type: string;
    downlink?: number;
    effectiveType?: string;
  };
  battery?: {
    level: number;
    charging: boolean;
  };
}

// Classe principal da Telemetria
export class TelemetryService {
  private static instance: TelemetryService;
  private config: TelemetryConfig;
  private eventQueue: TelemetryEvent[] = [];
  private batchTimeout: NodeJS.Timeout | null = null;
  private isProcessing = false;
  private sessionId: string;
  private performanceObserver: PerformanceObserver | null = null;
  private navigationObserver: PerformanceObserver | null = null;

  private constructor(config: Partial<TelemetryConfig> = {}) {
    this.config = {
      enabled: true,
      endpoint: '/api/telemetry',
      batchSize: 20,
      batchTimeout: 10000,
      enablePerformanceTracking: true,
      enableUsageTracking: true,
      enableErrorTracking: true,
      enableNavigationTracking: true,
      enableInteractionTracking: true,
      enableSystemTracking: true,
      samplingRate: 1.0,
      enableUserTracking: true,
      enableSessionTracking: true,
      maxEventsInMemory: 1000,
      flushOnPageUnload: true,
      ...config
    };

    this.sessionId = this.generateSessionId();
    this.initialize();
  }

  public static getInstance(config?: Partial<TelemetryConfig>): TelemetryService {
    if (!TelemetryService.instance) {
      TelemetryService.instance = new TelemetryService(config);
    }
    return TelemetryService.instance;
  }

  // Inicializar telemetria
  private initialize(): void {
    if (!this.config.enabled) {
      return;
    }

    // Configurar observers de performance
    if (this.config.enablePerformanceTracking) {
      this.setupPerformanceObservers();
    }

    // Configurar tracking de navegação
    if (this.config.enableNavigationTracking) {
      this.setupNavigationTracking();
    }

    // Configurar tracking de interações
    if (this.config.enableInteractionTracking) {
      this.setupInteractionTracking();
    }

    // Configurar tracking de sistema
    if (this.config.enableSystemTracking) {
      this.setupSystemTracking();
    }

    // Configurar flush no unload da página
    if (this.config.flushOnPageUnload) {
      this.setupPageUnloadHandler();
    }

    logger.info('[TELEMETRY] Service initialized', {
      sessionId: this.sessionId,
      config: this.config
    });
  }

  // Configurar observers de performance
  private setupPerformanceObservers(): void {
    if (!window.PerformanceObserver) {
      logger.warn('[TELEMETRY] PerformanceObserver not supported');
      return;
    }

    // Observer para métricas de performance
    try {
      this.performanceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.trackPerformanceMetric(entry);
        }
      });

      this.performanceObserver.observe({ entryTypes: ['navigation', 'paint', 'largest-contentful-paint', 'first-input', 'layout-shift'] });
    } catch (error) {
      logger.warn('[TELEMETRY] Failed to setup performance observer', { error });
    }
  }

  // Configurar tracking de navegação
  private setupNavigationTracking(): void {
    // Track mudanças de rota
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    history.pushState = (...args) => {
      originalPushState.apply(history, args);
      this.trackNavigation('pushState', window.location.pathname);
    };

    history.replaceState = (...args) => {
      originalReplaceState.apply(history, args);
      this.trackNavigation('replaceState', window.location.pathname);
    };

    // Track popstate
    window.addEventListener('popstate', () => {
      this.trackNavigation('popstate', window.location.pathname);
    });
  }

  // Configurar tracking de interações
  private setupInteractionTracking(): void {
    // Track cliques
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      this.trackInteraction('click', {
        element: target.tagName.toLowerCase(),
        id: target.id,
        className: target.className,
        text: target.textContent?.substring(0, 100)
      });
    });

    // Track inputs
    document.addEventListener('input', (event) => {
      const target = event.target as HTMLInputElement;
      this.trackInteraction('input', {
        element: target.tagName.toLowerCase(),
        type: target.type,
        id: target.id,
        name: target.name
      });
    });

    // Track scroll
    let scrollTimeout: NodeJS.Timeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        this.trackInteraction('scroll', {
          scrollY: window.scrollY,
          scrollX: window.scrollX,
          documentHeight: document.documentElement.scrollHeight
        });
      }, 100);
    });
  }

  // Configurar tracking de sistema
  private setupSystemTracking(): void {
    // Track mudanças de conectividade
    window.addEventListener('online', () => {
      this.trackSystemEvent('network_online');
    });

    window.addEventListener('offline', () => {
      this.trackSystemEvent('network_offline');
    });

    // Track mudanças de visibilidade
    document.addEventListener('visibilitychange', () => {
      this.trackSystemEvent('visibility_change', {
        hidden: document.hidden
      });
    });

    // Track mudanças de foco
    window.addEventListener('focus', () => {
      this.trackSystemEvent('window_focus');
    });

    window.addEventListener('blur', () => {
      this.trackSystemEvent('window_blur');
    });

    // Coletar métricas de sistema periodicamente
    setInterval(() => {
      this.collectSystemMetrics();
    }, 30000); // A cada 30 segundos
  }

  // Configurar handler de unload da página
  private setupPageUnloadHandler(): void {
    window.addEventListener('beforeunload', () => {
      this.flush();
    });

    window.addEventListener('pagehide', () => {
      this.flush();
    });
  }

  // Track evento de telemetria
  public track(
    type: TelemetryType,
    name: string,
    data: Record<string, any> = {},
    tags: Record<string, string> = {}
  ): void {
    if (!this.config.enabled) {
      return;
    }

    // Verificar sampling
    if (Math.random() > this.config.samplingRate) {
      return;
    }

    const event: TelemetryEvent = {
      id: this.generateEventId(),
      type,
      name,
      timestamp: new Date().toISOString(),
      data,
      context: {
        userId: this.config.enableUserTracking ? this.getCurrentUserId() : undefined,
        sessionId: this.config.enableSessionTracking ? this.sessionId : undefined,
        pageUrl: window.location.href,
        userAgent: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        },
        referrer: document.referrer
      },
      metadata: {
        version: process.env.REACT_APP_VERSION || 'unknown',
        environment: process.env.NODE_ENV || 'development',
        tags
      }
    };

    this.eventQueue.push(event);

    // Processar se atingiu batch size
    if (this.eventQueue.length >= this.config.batchSize) {
      this.processBatch();
    } else if (!this.batchTimeout) {
      // Agendar processamento
      this.batchTimeout = setTimeout(() => {
        this.processBatch();
      }, this.config.batchTimeout);
    }

    // Limitar eventos em memória
    if (this.eventQueue.length > this.config.maxEventsInMemory) {
      this.eventQueue.splice(0, this.eventQueue.length - this.config.maxEventsInMemory);
    }
  }

  // Track métrica de performance
  private trackPerformanceMetric(entry: PerformanceEntry): void {
    if (!this.config.enablePerformanceTracking) {
      return;
    }

    const data: Record<string, any> = {
      entryType: entry.entryType,
      name: entry.name,
      startTime: entry.startTime,
      duration: entry.duration
    };

    // Adicionar dados específicos por tipo
    if (entry.entryType === 'navigation') {
      const navEntry = entry as PerformanceNavigationTiming;
      data.loadEventEnd = navEntry.loadEventEnd;
      data.domContentLoadedEventEnd = navEntry.domContentLoadedEventEnd;
      data.domInteractive = navEntry.domInteractive;
    } else if (entry.entryType === 'paint') {
      const paintEntry = entry as PerformancePaintTiming;
      data.paintTime = paintEntry.startTime;
    } else if (entry.entryType === 'largest-contentful-paint') {
      const lcpEntry = entry as PerformanceEntry;
      data.lcpValue = lcpEntry.startTime;
    } else if (entry.entryType === 'first-input') {
      const fidEntry = entry as PerformanceEntry;
      data.fidValue = fidEntry.processingStart - fidEntry.startTime;
    } else if (entry.entryType === 'layout-shift') {
      const lsEntry = entry as PerformanceEntry;
      data.clsValue = (lsEntry as any).value;
    }

    this.track(TelemetryType.PERFORMANCE, `performance_${entry.entryType}`, data, {
      metric: entry.entryType
    });
  }

  // Track navegação
  private trackNavigation(action: string, path: string): void {
    if (!this.config.enableNavigationTracking) {
      return;
    }

    this.track(TelemetryType.NAVIGATION, 'page_navigation', {
      action,
      path,
      timestamp: Date.now()
    }, {
      action,
      path
    });
  }

  // Track interação
  private trackInteraction(type: string, data: Record<string, any>): void {
    if (!this.config.enableInteractionTracking) {
      return;
    }

    this.track(TelemetryType.INTERACTION, `user_${type}`, {
      ...data,
      timestamp: Date.now()
    }, {
      interaction: type
    });
  }

  // Track evento de sistema
  private trackSystemEvent(event: string, data: Record<string, any> = {}): void {
    if (!this.config.enableSystemTracking) {
      return;
    }

    this.track(TelemetryType.SYSTEM, event, {
      ...data,
      timestamp: Date.now()
    }, {
      systemEvent: event
    });
  }

  // Coletar métricas de sistema
  private collectSystemMetrics(): void {
    if (!this.config.enableSystemTracking) {
      return;
    }

    const metrics: SystemMetrics = {
      memory: {
        used: 0,
        total: 0,
        available: 0
      },
      cpu: {
        cores: navigator.hardwareConcurrency || 0
      },
      network: {
        type: navigator.connection?.effectiveType || 'unknown'
      }
    };

    // Coletar métricas de memória se disponível
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      metrics.memory = {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        available: memory.jsHeapSizeLimit
      };
    }

    // Coletar métricas de rede se disponível
    if (navigator.connection) {
      metrics.network = {
        type: navigator.connection.effectiveType || 'unknown',
        downlink: navigator.connection.downlink,
        effectiveType: navigator.connection.effectiveType
      };
    }

    // Coletar métricas de bateria se disponível
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        metrics.battery = {
          level: battery.level,
          charging: battery.charging
        };
      });
    }

    this.track(TelemetryType.SYSTEM, 'system_metrics', metrics, {
      type: 'system_metrics'
    });
  }

  // Track erro
  public trackError(error: Error, context: Record<string, any> = {}): void {
    if (!this.config.enableErrorTracking) {
      return;
    }

    this.track(TelemetryType.ERROR, 'application_error', {
      message: error.message,
      stack: error.stack,
      name: error.name,
      ...context
    }, {
      errorType: error.name,
      severity: 'error'
    });
  }

  // Track uso
  public trackUsage(action: string, data: Record<string, any> = {}): void {
    if (!this.config.enableUsageTracking) {
      return;
    }

    this.track(TelemetryType.USAGE, `usage_${action}`, {
      ...data,
      timestamp: Date.now()
    }, {
      usage: action
    });
  }

  // Processar lote de eventos
  private async processBatch(): Promise<void> {
    if (this.isProcessing || this.eventQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    // Limpar timeout
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    const batch = this.eventQueue.splice(0, this.config.batchSize);

    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          events: batch,
          timestamp: new Date().toISOString(),
          batchId: this.generateBatchId()
        })
      });

      if (!response.ok) {
        throw new Error(`Telemetry failed: ${response.status}`);
      }

      logger.info('[TELEMETRY] Batch sent successfully', {
        batchSize: batch.length,
        remainingInQueue: this.eventQueue.length
      });

    } catch (error) {
      logger.error('[TELEMETRY] Failed to send batch', { error });
      
      // Recolocar eventos na fila para retry
      this.eventQueue.unshift(...batch);
    } finally {
      this.isProcessing = false;

      // Processar próximo lote se houver
      if (this.eventQueue.length > 0) {
        setTimeout(() => this.processBatch(), 1000);
      }
    }
  }

  // Utilitários
  private generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateBatchId(): string {
    return `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateSessionId(): string {
    let sessionId = sessionStorage.getItem('telemetry_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('telemetry_session_id', sessionId);
    }
    return sessionId;
  }

  private getCurrentUserId(): string | undefined {
    return localStorage.getItem('userId') || undefined;
  }

  private getAuthToken(): string {
    return localStorage.getItem('authToken') || '';
  }

  // Métodos públicos
  public flush(): Promise<void> {
    return this.processBatch();
  }

  public updateConfig(newConfig: Partial<TelemetryConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  public getConfig(): TelemetryConfig {
    return { ...this.config };
  }

  public getQueueSize(): number {
    return this.eventQueue.length;
  }

  public clearQueue(): void {
    this.eventQueue = [];
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }
  }

  public destroy(): void {
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }
    if (this.navigationObserver) {
      this.navigationObserver.disconnect();
    }
    this.clearQueue();
  }
}

// Instância singleton
export const telemetry = TelemetryService.getInstance();

// Hook para usar telemetria
export const useTelemetry = () => {
  return telemetry;
};

// Hook para track de eventos
export const useTelemetryTrack = () => {
  const track = (type: TelemetryType, name: string, data?: Record<string, any>, tags?: Record<string, string>) => {
    telemetry.track(type, name, data, tags);
  };

  const trackError = (error: Error, context?: Record<string, any>) => {
    telemetry.trackError(error, context);
  };

  const trackUsage = (action: string, data?: Record<string, any>) => {
    telemetry.trackUsage(action, data);
  };

  return { track, trackError, trackUsage };
};

export default telemetry; 