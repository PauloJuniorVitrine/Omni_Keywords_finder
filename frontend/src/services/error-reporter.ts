/**
 * Error Reporter para Analytics
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por reportar erros para sistemas de analytics e monitoramento
 * Integra com Google Analytics, Sentry, DataDog e sistemas internos
 */

import { logger } from './logger';

// Tipos de analytics suportados
export enum AnalyticsProvider {
  GOOGLE_ANALYTICS = 'GOOGLE_ANALYTICS',
  SENTRY = 'SENTRY',
  DATADOG = 'DATADOG',
  INTERNAL = 'INTERNAL',
  CUSTOM = 'CUSTOM'
}

// Interface para configuração do reporter
export interface ErrorReporterConfig {
  enabled: boolean;
  providers: AnalyticsProvider[];
  batchSize: number;
  batchTimeout: number;
  maxRetries: number;
  retryDelay: number;
  enableSampling: boolean;
  samplingRate: number;
  enableUserTracking: boolean;
  enableSessionTracking: boolean;
  customEndpoints?: Record<AnalyticsProvider, string>;
  apiKeys?: Record<AnalyticsProvider, string>;
}

// Interface para erro reportado
export interface ErrorReport {
  id: string;
  timestamp: string;
  error: {
    name: string;
    message: string;
    stack?: string;
    type: string;
    severity: string;
  };
  context: {
    url: string;
    userAgent: string;
    userId?: string;
    sessionId?: string;
    pageTitle?: string;
    referrer?: string;
    viewport?: {
      width: number;
      height: number;
    };
    performance?: {
      loadTime: number;
      domContentLoaded: number;
    };
  };
  metadata: {
    retryCount: number;
    tags: Record<string, string>;
    customData?: Record<string, any>;
  };
}

// Classe principal do Error Reporter
export class ErrorReporter {
  private static instance: ErrorReporter;
  private config: ErrorReporterConfig;
  private reportQueue: ErrorReport[] = [];
  private batchTimeout: NodeJS.Timeout | null = null;
  private isProcessing = false;

  private constructor(config: Partial<ErrorReporterConfig> = {}) {
    this.config = {
      enabled: true,
      providers: [AnalyticsProvider.GOOGLE_ANALYTICS, AnalyticsProvider.INTERNAL],
      batchSize: 10,
      batchTimeout: 5000,
      maxRetries: 3,
      retryDelay: 1000,
      enableSampling: false,
      samplingRate: 0.1,
      enableUserTracking: true,
      enableSessionTracking: true,
      ...config
    };

    this.initializeProviders();
  }

  public static getInstance(config?: Partial<ErrorReporterConfig>): ErrorReporter {
    if (!ErrorReporter.instance) {
      ErrorReporter.instance = new ErrorReporter(config);
    }
    return ErrorReporter.instance;
  }

  // Inicializar providers
  private initializeProviders(): void {
    if (!this.config.enabled) {
      logger.info('[ERROR_REPORTER] Error reporting disabled');
      return;
    }

    // Verificar disponibilidade dos providers
    this.config.providers.forEach(provider => {
      switch (provider) {
        case AnalyticsProvider.GOOGLE_ANALYTICS:
          this.initializeGoogleAnalytics();
          break;
        case AnalyticsProvider.SENTRY:
          this.initializeSentry();
          break;
        case AnalyticsProvider.DATADOG:
          this.initializeDataDog();
          break;
        case AnalyticsProvider.INTERNAL:
          this.initializeInternal();
          break;
      }
    });

    logger.info('[ERROR_REPORTER] Initialized providers', { providers: this.config.providers });
  }

  // Inicializar Google Analytics
  private initializeGoogleAnalytics(): void {
    if (typeof window !== 'undefined' && window.gtag) {
      logger.info('[ERROR_REPORTER] Google Analytics initialized');
    } else {
      logger.warn('[ERROR_REPORTER] Google Analytics not available');
    }
  }

  // Inicializar Sentry
  private initializeSentry(): void {
    if (typeof window !== 'undefined' && window.Sentry) {
      logger.info('[ERROR_REPORTER] Sentry initialized');
    } else {
      logger.warn('[ERROR_REPORTER] Sentry not available');
    }
  }

  // Inicializar DataDog
  private initializeDataDog(): void {
    if (typeof window !== 'undefined' && window.DD_LOGS) {
      logger.info('[ERROR_REPORTER] DataDog initialized');
    } else {
      logger.warn('[ERROR_REPORTER] DataDog not available');
    }
  }

  // Inicializar sistema interno
  private initializeInternal(): void {
    logger.info('[ERROR_REPORTER] Internal reporting system initialized');
  }

  // Reportar erro
  public reportError(
    error: Error | string,
    options: {
      type?: string;
      severity?: string;
      tags?: Record<string, string>;
      customData?: Record<string, any>;
      retryCount?: number;
    } = {}
  ): void {
    if (!this.config.enabled) {
      return;
    }

    // Verificar sampling
    if (this.config.enableSampling && Math.random() > this.config.samplingRate) {
      logger.debug('[ERROR_REPORTER] Error skipped due to sampling');
      return;
    }

    const errorReport = this.createErrorReport(error, options);
    
    // Adicionar à fila
    this.reportQueue.push(errorReport);

    // Processar se atingiu batch size
    if (this.reportQueue.length >= this.config.batchSize) {
      this.processBatch();
    } else if (!this.batchTimeout) {
      // Agendar processamento
      this.batchTimeout = setTimeout(() => {
        this.processBatch();
      }, this.config.batchTimeout);
    }
  }

  // Criar relatório de erro
  private createErrorReport(
    error: Error | string,
    options: {
      type?: string;
      severity?: string;
      tags?: Record<string, string>;
      customData?: Record<string, any>;
      retryCount?: number;
    }
  ): ErrorReport {
    const errorMessage = typeof error === 'string' ? error : error.message;
    const errorName = typeof error === 'string' ? 'StringError' : error.name;

    return {
      id: this.generateReportId(),
      timestamp: new Date().toISOString(),
      error: {
        name: errorName,
        message: errorMessage,
        stack: typeof error === 'string' ? undefined : error.stack,
        type: options.type || 'UNKNOWN',
        severity: options.severity || 'MEDIUM'
      },
      context: {
        url: window.location.href,
        userAgent: navigator.userAgent,
        userId: this.config.enableUserTracking ? this.getCurrentUserId() : undefined,
        sessionId: this.config.enableSessionTracking ? this.getSessionId() : undefined,
        pageTitle: document.title,
        referrer: document.referrer,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        },
        performance: this.getPerformanceMetrics()
      },
      metadata: {
        retryCount: options.retryCount || 0,
        tags: {
          environment: process.env.NODE_ENV || 'development',
          version: process.env.REACT_APP_VERSION || 'unknown',
          ...options.tags
        },
        customData: options.customData
      }
    };
  }

  // Processar lote de relatórios
  private async processBatch(): Promise<void> {
    if (this.isProcessing || this.reportQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    // Limpar timeout
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    const batch = this.reportQueue.splice(0, this.config.batchSize);

    try {
      // Reportar para todos os providers
      const promises = this.config.providers.map(provider => 
        this.reportToProvider(provider, batch)
      );

      await Promise.allSettled(promises);

      logger.info('[ERROR_REPORTER] Batch processed successfully', {
        batchSize: batch.length,
        remainingInQueue: this.reportQueue.length
      });

    } catch (error) {
      logger.error('[ERROR_REPORTER] Failed to process batch', { error });
      
      // Recolocar na fila para retry
      this.reportQueue.unshift(...batch);
    } finally {
      this.isProcessing = false;

      // Processar próximo lote se houver
      if (this.reportQueue.length > 0) {
        setTimeout(() => this.processBatch(), 100);
      }
    }
  }

  // Reportar para provider específico
  private async reportToProvider(provider: AnalyticsProvider, reports: ErrorReport[]): Promise<void> {
    try {
      switch (provider) {
        case AnalyticsProvider.GOOGLE_ANALYTICS:
          await this.reportToGoogleAnalytics(reports);
          break;
        case AnalyticsProvider.SENTRY:
          await this.reportToSentry(reports);
          break;
        case AnalyticsProvider.DATADOG:
          await this.reportToDataDog(reports);
          break;
        case AnalyticsProvider.INTERNAL:
          await this.reportToInternal(reports);
          break;
        case AnalyticsProvider.CUSTOM:
          await this.reportToCustom(reports);
          break;
      }
    } catch (error) {
      logger.error(`[ERROR_REPORTER] Failed to report to ${provider}`, { error });
      throw error;
    }
  }

  // Reportar para Google Analytics
  private async reportToGoogleAnalytics(reports: ErrorReport[]): Promise<void> {
    if (!window.gtag) {
      throw new Error('Google Analytics not available');
    }

    reports.forEach(report => {
      window.gtag('event', 'exception', {
        description: report.error.message,
        fatal: report.error.severity === 'CRITICAL',
        error_id: report.id,
        error_type: report.error.type,
        error_name: report.error.name,
        custom_map: {
          error_id: 'error_id',
          error_type: 'error_type',
          error_name: 'error_name',
          user_id: 'user_id',
          session_id: 'session_id'
        },
        user_id: report.context.userId,
        session_id: report.context.sessionId
      });
    });
  }

  // Reportar para Sentry
  private async reportToSentry(reports: ErrorReport[]): Promise<void> {
    if (!window.Sentry) {
      throw new Error('Sentry not available');
    }

    reports.forEach(report => {
      const error = new Error(report.error.message);
      error.name = report.error.name;
      error.stack = report.error.stack;

      window.Sentry.captureException(error, {
        tags: {
          error_id: report.id,
          error_type: report.error.type,
          error_severity: report.error.severity,
          ...report.metadata.tags
        },
        extra: {
          context: report.context,
          metadata: report.metadata
        },
        user: report.context.userId ? {
          id: report.context.userId
        } : undefined
      });
    });
  }

  // Reportar para DataDog
  private async reportToDataDog(reports: ErrorReport[]): Promise<void> {
    if (!window.DD_LOGS) {
      throw new Error('DataDog not available');
    }

    reports.forEach(report => {
      window.DD_LOGS.logger.error(report.error.message, {
        error_id: report.id,
        error_type: report.error.type,
        error_severity: report.error.severity,
        error_name: report.error.name,
        error_stack: report.error.stack,
        context: report.context,
        metadata: report.metadata
      });
    });
  }

  // Reportar para sistema interno
  private async reportToInternal(reports: ErrorReport[]): Promise<void> {
    const endpoint = this.config.customEndpoints?.[AnalyticsProvider.INTERNAL] || '/api/error-reports';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKeys?.[AnalyticsProvider.INTERNAL]}`
      },
      body: JSON.stringify({
        reports,
        timestamp: new Date().toISOString(),
        batch_id: this.generateReportId()
      })
    });

    if (!response.ok) {
      throw new Error(`Internal reporting failed: ${response.status}`);
    }
  }

  // Reportar para sistema customizado
  private async reportToCustom(reports: ErrorReport[]): Promise<void> {
    const endpoint = this.config.customEndpoints?.[AnalyticsProvider.CUSTOM];
    
    if (!endpoint) {
      throw new Error('Custom endpoint not configured');
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKeys?.[AnalyticsProvider.CUSTOM]}`
      },
      body: JSON.stringify({
        reports,
        timestamp: new Date().toISOString(),
        batch_id: this.generateReportId()
      })
    });

    if (!response.ok) {
      throw new Error(`Custom reporting failed: ${response.status}`);
    }
  }

  // Utilitários
  private generateReportId(): string {
    return `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCurrentUserId(): string | undefined {
    return localStorage.getItem('userId') || undefined;
  }

  private getSessionId(): string {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
  }

  private getPerformanceMetrics(): { loadTime: number; domContentLoaded: number } {
    if (typeof window !== 'undefined' && window.performance) {
      const perf = window.performance;
      const navigation = perf.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      
      return {
        loadTime: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0,
        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : 0
      };
    }
    
    return { loadTime: 0, domContentLoaded: 0 };
  }

  // Métodos públicos
  public updateConfig(newConfig: Partial<ErrorReporterConfig>): void {
    this.config = { ...this.config, ...newConfig };
    this.initializeProviders();
  }

  public getConfig(): ErrorReporterConfig {
    return { ...this.config };
  }

  public getQueueSize(): number {
    return this.reportQueue.length;
  }

  public clearQueue(): void {
    this.reportQueue = [];
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }
  }

  public flush(): Promise<void> {
    return this.processBatch();
  }
}

// Instância singleton
export const errorReporter = ErrorReporter.getInstance();

// Hook para usar error reporter
export const useErrorReporter = () => {
  return errorReporter;
};

export default errorReporter; 