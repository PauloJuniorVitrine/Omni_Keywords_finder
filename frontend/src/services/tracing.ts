/**
 * Sistema de Tracing Distribuído
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por implementar tracing distribuído para rastreamento de requisições
 * Suporta OpenTelemetry, Jaeger, Zipkin e sistemas internos
 */

import { logger } from './logger';

// Tipos de span
export enum SpanType {
  HTTP_REQUEST = 'HTTP_REQUEST',
  HTTP_RESPONSE = 'HTTP_RESPONSE',
  DATABASE_QUERY = 'DATABASE_QUERY',
  CACHE_OPERATION = 'CACHE_OPERATION',
  EXTERNAL_API = 'EXTERNAL_API',
  FUNCTION_CALL = 'FUNCTION_CALL',
  CUSTOM = 'CUSTOM'
}

// Status do span
export enum SpanStatus {
  OK = 'OK',
  ERROR = 'ERROR',
  UNKNOWN = 'UNKNOWN'
}

// Interface para span
export interface Span {
  id: string;
  traceId: string;
  parentId?: string;
  name: string;
  type: SpanType;
  startTime: number;
  endTime?: number;
  duration?: number;
  status: SpanStatus;
  attributes: Record<string, any>;
  events: SpanEvent[];
  context: {
    userId?: string;
    sessionId: string;
    requestId?: string;
    url: string;
    userAgent: string;
  };
  metadata: {
    version: string;
    environment: string;
    service: string;
  };
}

// Interface para evento do span
export interface SpanEvent {
  id: string;
  name: string;
  timestamp: number;
  attributes: Record<string, any>;
}

// Interface para configuração do tracing
export interface TracingConfig {
  enabled: boolean;
  serviceName: string;
  serviceVersion: string;
  enableSampling: boolean;
  samplingRate: number;
  enableBatching: boolean;
  batchSize: number;
  batchTimeout: number;
  enableExport: boolean;
  endpoint?: string;
  enableConsoleExport: boolean;
  enableLocalStorage: boolean;
  maxSpansInMemory: number;
  enableAutoInstrumentation: boolean;
  enablePerformanceTracing: boolean;
  enableErrorTracing: boolean;
  enableUserTracking: boolean;
  enableSessionTracking: boolean;
}

// Interface para contexto de trace
export interface TraceContext {
  traceId: string;
  spanId: string;
  parentId?: string;
  userId?: string;
  sessionId: string;
  requestId?: string;
}

// Classe principal do Tracing
export class TracingService {
  private static instance: TracingService;
  private config: TracingConfig;
  private spans: Span[] = [];
  private activeSpans: Map<string, Span> = new Map();
  private batchTimeout: NodeJS.Timeout | null = null;
  private isProcessing = false;
  private sessionId: string;
  private currentTraceId?: string;
  private currentSpanId?: string;

  private constructor(config: Partial<TracingConfig> = {}) {
    this.config = {
      enabled: true,
      serviceName: 'omni-keywords-finder-frontend',
      serviceVersion: process.env.REACT_APP_VERSION || '1.0.0',
      enableSampling: true,
      samplingRate: 0.1,
      enableBatching: true,
      batchSize: 50,
      batchTimeout: 10000,
      enableExport: true,
      enableConsoleExport: true,
      enableLocalStorage: true,
      maxSpansInMemory: 1000,
      enableAutoInstrumentation: true,
      enablePerformanceTracing: true,
      enableErrorTracing: true,
      enableUserTracking: true,
      enableSessionTracking: true,
      ...config
    };

    this.sessionId = this.generateSessionId();
    this.initialize();
  }

  public static getInstance(config?: Partial<TracingConfig>): TracingService {
    if (!TracingService.instance) {
      TracingService.instance = new TracingService(config);
    }
    return TracingService.instance;
  }

  // Inicializar tracing
  private initialize(): void {
    if (!this.config.enabled) {
      return;
    }

    // Configurar auto-instrumentação
    if (this.config.enableAutoInstrumentation) {
      this.setupAutoInstrumentation();
    }

    // Configurar performance tracing
    if (this.config.enablePerformanceTracing) {
      this.setupPerformanceTracing();
    }

    // Configurar error tracing
    if (this.config.enableErrorTracing) {
      this.setupErrorTracing();
    }

    logger.info('[TRACING] Service initialized', {
      serviceName: this.config.serviceName,
      serviceVersion: this.config.serviceVersion,
      sessionId: this.sessionId
    });
  }

  // Configurar auto-instrumentação
  private setupAutoInstrumentation(): void {
    // Interceptar fetch requests
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const [url, options] = args;
      const span = this.startSpan('fetch_request', SpanType.HTTP_REQUEST, {
        url: typeof url === 'string' ? url : url.toString(),
        method: options?.method || 'GET',
        headers: options?.headers
      });

      try {
        const response = await originalFetch(...args);
        
        this.addSpanEvent(span.id, 'response_received', {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries())
        });

        this.endSpan(span.id, SpanStatus.OK, {
          statusCode: response.status,
          responseSize: response.headers.get('content-length')
        });

        return response;
      } catch (error) {
        this.addSpanEvent(span.id, 'error_occurred', {
          error: error.message,
          stack: error.stack
        });

        this.endSpan(span.id, SpanStatus.ERROR, {
          error: error.message
        });

        throw error;
      }
    };

    // Interceptar XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url, ...args) {
      this._tracingSpan = tracingService.startSpan('xhr_request', SpanType.HTTP_REQUEST, {
        url: url.toString(),
        method: method.toUpperCase()
      });
      return originalXHROpen.call(this, method, url, ...args);
    };

    XMLHttpRequest.prototype.send = function(data) {
      const span = this._tracingSpan;
      if (span) {
        this.addEventListener('load', () => {
          tracingService.addSpanEvent(span.id, 'response_received', {
            status: this.status,
            statusText: this.statusText
          });
          tracingService.endSpan(span.id, SpanStatus.OK, {
            statusCode: this.status,
            responseSize: this.responseText?.length
          });
        });

        this.addEventListener('error', () => {
          tracingService.addSpanEvent(span.id, 'error_occurred', {
            status: this.status,
            statusText: this.statusText
          });
          tracingService.endSpan(span.id, SpanStatus.ERROR, {
            error: 'XHR request failed'
          });
        });
      }
      return originalXHRSend.call(this, data);
    };
  }

  // Configurar performance tracing
  private setupPerformanceTracing(): void {
    if (!window.PerformanceObserver) {
      return;
    }

    // Observer para navigation timing
    try {
      const navigationObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        for (const entry of entries) {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming;
            this.traceNavigationPerformance(navEntry);
          }
        }
      });
      navigationObserver.observe({ entryTypes: ['navigation'] });
    } catch (error) {
      logger.warn('[TRACING] Failed to setup navigation observer', { error });
    }

    // Observer para resource timing
    try {
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        for (const entry of entries) {
          if (entry.entryType === 'resource') {
            const resourceEntry = entry as PerformanceResourceTiming;
            this.traceResourcePerformance(resourceEntry);
          }
        }
      });
      resourceObserver.observe({ entryTypes: ['resource'] });
    } catch (error) {
      logger.warn('[TRACING] Failed to setup resource observer', { error });
    }
  }

  // Configurar error tracing
  private setupErrorTracing(): void {
    // Interceptar erros globais
    window.addEventListener('error', (event) => {
      this.traceError('global_error', event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      });
    });

    // Interceptar promises rejeitadas
    window.addEventListener('unhandledrejection', (event) => {
      this.traceError('unhandled_rejection', event.reason, {
        type: 'unhandledrejection'
      });
    });
  }

  // Iniciar span
  public startSpan(
    name: string,
    type: SpanType,
    attributes: Record<string, any> = {}
  ): Span {
    if (!this.config.enabled) {
      return this.createDummySpan();
    }

    // Verificar sampling
    if (this.config.enableSampling && Math.random() > this.config.samplingRate) {
      return this.createDummySpan();
    }

    const spanId = this.generateSpanId();
    const traceId = this.currentTraceId || this.generateTraceId();
    const parentId = this.currentSpanId;

    const span: Span = {
      id: spanId,
      traceId,
      parentId,
      name,
      type,
      startTime: performance.now(),
      status: SpanStatus.UNKNOWN,
      attributes: {
        ...attributes,
        service: this.config.serviceName,
        version: this.config.serviceVersion
      },
      events: [],
      context: {
        userId: this.config.enableUserTracking ? this.getCurrentUserId() : undefined,
        sessionId: this.config.enableSessionTracking ? this.sessionId : undefined,
        requestId: this.getRequestId(),
        url: window.location.href,
        userAgent: navigator.userAgent
      },
      metadata: {
        version: this.config.serviceVersion,
        environment: process.env.NODE_ENV || 'development',
        service: this.config.serviceName
      }
    };

    this.spans.push(span);
    this.activeSpans.set(spanId, span);

    // Atualizar contexto atual
    this.currentTraceId = traceId;
    this.currentSpanId = spanId;

    // Log do span iniciado
    if (this.config.enableConsoleExport) {
      logger.debug('[TRACING] Span started', {
        spanId,
        traceId,
        name,
        type
      });
    }

    return span;
  }

  // Finalizar span
  public endSpan(
    spanId: string,
    status: SpanStatus = SpanStatus.OK,
    attributes: Record<string, any> = {}
  ): void {
    if (!this.config.enabled) {
      return;
    }

    const span = this.activeSpans.get(spanId);
    if (!span) {
      return;
    }

    span.endTime = performance.now();
    span.duration = span.endTime - span.startTime;
    span.status = status;
    span.attributes = {
      ...span.attributes,
      ...attributes
    };

    this.activeSpans.delete(spanId);

    // Restaurar contexto pai
    this.currentSpanId = span.parentId;

    // Log do span finalizado
    if (this.config.enableConsoleExport) {
      logger.debug('[TRACING] Span ended', {
        spanId,
        traceId: span.traceId,
        name: span.name,
        status,
        duration: span.duration
      });
    }

    // Processar se atingiu batch size
    if (this.config.enableBatching && this.spans.length >= this.config.batchSize) {
      this.processBatch();
    } else if (!this.batchTimeout && this.config.enableBatching) {
      // Agendar processamento
      this.batchTimeout = setTimeout(() => {
        this.processBatch();
      }, this.config.batchTimeout);
    }

    // Limitar spans em memória
    if (this.spans.length > this.config.maxSpansInMemory) {
      this.spans.splice(0, this.spans.length - this.config.maxSpansInMemory);
    }
  }

  // Adicionar evento ao span
  public addSpanEvent(
    spanId: string,
    name: string,
    attributes: Record<string, any> = {}
  ): void {
    if (!this.config.enabled) {
      return;
    }

    const span = this.activeSpans.get(spanId);
    if (!span) {
      return;
    }

    const event: SpanEvent = {
      id: this.generateEventId(),
      name,
      timestamp: performance.now(),
      attributes
    };

    span.events.push(event);
  }

  // Trace performance de navegação
  private traceNavigationPerformance(navEntry: PerformanceNavigationTiming): void {
    const span = this.startSpan('page_load', SpanType.CUSTOM, {
      entryType: 'navigation',
      url: window.location.href
    });

    this.addSpanEvent(span.id, 'dom_content_loaded', {
      timestamp: navEntry.domContentLoadedEventEnd
    });

    this.addSpanEvent(span.id, 'load_complete', {
      timestamp: navEntry.loadEventEnd
    });

    this.endSpan(span.id, SpanStatus.OK, {
      domContentLoaded: navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart,
      loadTime: navEntry.loadEventEnd - navEntry.loadEventStart,
      totalTime: navEntry.loadEventEnd - navEntry.fetchStart
    });
  }

  // Trace performance de recursos
  private traceResourcePerformance(resourceEntry: PerformanceResourceTiming): void {
    const span = this.startSpan('resource_load', SpanType.CUSTOM, {
      entryType: 'resource',
      name: resourceEntry.name,
      initiatorType: resourceEntry.initiatorType
    });

    this.endSpan(span.id, SpanStatus.OK, {
      duration: resourceEntry.duration,
      transferSize: resourceEntry.transferSize,
      encodedBodySize: resourceEntry.encodedBodySize,
      decodedBodySize: resourceEntry.decodedBodySize
    });
  }

  // Trace erro
  public traceError(
    name: string,
    error: Error,
    attributes: Record<string, any> = {}
  ): void {
    const span = this.startSpan(name, SpanType.CUSTOM, {
      errorType: error.name,
      errorMessage: error.message,
      ...attributes
    });

    this.addSpanEvent(span.id, 'error_details', {
      stack: error.stack,
      name: error.name,
      message: error.message
    });

    this.endSpan(span.id, SpanStatus.ERROR, {
      error: error.message
    });
  }

  // Trace função
  public traceFunction<T>(
    name: string,
    fn: () => T,
    attributes: Record<string, any> = {}
  ): T {
    const span = this.startSpan(name, SpanType.FUNCTION_CALL, attributes);

    try {
      const result = fn();
      this.endSpan(span.id, SpanStatus.OK);
      return result;
    } catch (error) {
      this.addSpanEvent(span.id, 'function_error', {
        error: error.message,
        stack: error.stack
      });
      this.endSpan(span.id, SpanStatus.ERROR, {
        error: error.message
      });
      throw error;
    }
  }

  // Trace função assíncrona
  public async traceAsyncFunction<T>(
    name: string,
    fn: () => Promise<T>,
    attributes: Record<string, any> = {}
  ): Promise<T> {
    const span = this.startSpan(name, SpanType.FUNCTION_CALL, attributes);

    try {
      const result = await fn();
      this.endSpan(span.id, SpanStatus.OK);
      return result;
    } catch (error) {
      this.addSpanEvent(span.id, 'async_function_error', {
        error: error.message,
        stack: error.stack
      });
      this.endSpan(span.id, SpanStatus.ERROR, {
        error: error.message
      });
      throw error;
    }
  }

  // Processar lote de spans
  private async processBatch(): Promise<void> {
    if (this.isProcessing || this.spans.length === 0) {
      return;
    }

    this.isProcessing = true;

    // Limpar timeout
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    const batch = this.spans.splice(0, this.config.batchSize);

    try {
      // Exportar spans
      if (this.config.enableExport) {
        await this.exportSpans(batch);
      }

      // Salvar no localStorage
      if (this.config.enableLocalStorage) {
        this.saveToLocalStorage(batch);
      }

      logger.info('[TRACING] Batch processed successfully', {
        batchSize: batch.length,
        remainingInQueue: this.spans.length
      });

    } catch (error) {
      logger.error('[TRACING] Failed to process batch', { error });
      
      // Recolocar spans na fila para retry
      this.spans.unshift(...batch);
    } finally {
      this.isProcessing = false;

      // Processar próximo lote se houver
      if (this.spans.length > 0) {
        setTimeout(() => this.processBatch(), 1000);
      }
    }
  }

  // Exportar spans
  private async exportSpans(spans: Span[]): Promise<void> {
    if (!this.config.endpoint) {
      return;
    }

    const response = await fetch(this.config.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify({
        spans,
        serviceName: this.config.serviceName,
        serviceVersion: this.config.serviceVersion,
        timestamp: new Date().toISOString()
      })
    });

    if (!response.ok) {
      throw new Error(`Tracing export failed: ${response.status}`);
    }
  }

  // Salvar no localStorage
  private saveToLocalStorage(spans: Span[]): void {
    try {
      const existingSpans = this.getSpansFromLocalStorage();
      const allSpans = [...existingSpans, ...spans];
      
      // Manter apenas os spans mais recentes
      if (allSpans.length > this.config.maxSpansInMemory) {
        allSpans.splice(0, allSpans.length - this.config.maxSpansInMemory);
      }
      
      localStorage.setItem('tracing_spans', JSON.stringify(allSpans));
    } catch (error) {
      logger.warn('[TRACING] Failed to save to localStorage', { error });
    }
  }

  // Obter spans do localStorage
  private getSpansFromLocalStorage(): Span[] {
    try {
      const spans = localStorage.getItem('tracing_spans');
      return spans ? JSON.parse(spans) : [];
    } catch {
      return [];
    }
  }

  // Utilitários
  private generateSpanId(): string {
    return `span_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateTraceId(): string {
    return `trace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateSessionId(): string {
    let sessionId = sessionStorage.getItem('tracing_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('tracing_session_id', sessionId);
    }
    return sessionId;
  }

  private getCurrentUserId(): string | undefined {
    return localStorage.getItem('userId') || undefined;
  }

  private getRequestId(): string | undefined {
    // Implementar lógica para obter request ID se disponível
    return undefined;
  }

  private getAuthToken(): string {
    return localStorage.getItem('authToken') || '';
  }

  private createDummySpan(): Span {
    return {
      id: 'dummy',
      traceId: 'dummy',
      name: 'dummy',
      type: SpanType.CUSTOM,
      startTime: 0,
      status: SpanStatus.UNKNOWN,
      attributes: {},
      events: [],
      context: {
        sessionId: this.sessionId,
        url: window.location.href,
        userAgent: navigator.userAgent
      },
      metadata: {
        version: this.config.serviceVersion,
        environment: process.env.NODE_ENV || 'development',
        service: this.config.serviceName
      }
    };
  }

  // Métodos públicos
  public getSpans(): Span[] {
    return [...this.spans];
  }

  public getActiveSpans(): Span[] {
    return Array.from(this.activeSpans.values());
  }

  public getSpansByTraceId(traceId: string): Span[] {
    return this.spans.filter(span => span.traceId === traceId);
  }

  public getSpansByType(type: SpanType): Span[] {
    return this.spans.filter(span => span.type === type);
  }

  public getCurrentTraceContext(): TraceContext | undefined {
    if (!this.currentTraceId) {
      return undefined;
    }

    return {
      traceId: this.currentTraceId,
      spanId: this.currentSpanId || '',
      parentId: undefined,
      userId: this.getCurrentUserId(),
      sessionId: this.sessionId,
      requestId: this.getRequestId()
    };
  }

  public updateConfig(newConfig: Partial<TracingConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  public getConfig(): TracingConfig {
    return { ...this.config };
  }

  public flush(): Promise<void> {
    return this.processBatch();
  }

  public clearSpans(): void {
    this.spans = [];
    this.activeSpans.clear();
  }
}

// Instância singleton
export const tracingService = TracingService.getInstance();

// Hook para usar tracing
export const useTracing = () => {
  return tracingService;
};

// Hook para tracing de funções
export const useTracingFunctions = () => {
  const traceFunction = <T>(name: string, fn: () => T, attributes?: Record<string, any>): T => {
    return tracingService.traceFunction(name, fn, attributes);
  };

  const traceAsyncFunction = async <T>(name: string, fn: () => Promise<T>, attributes?: Record<string, any>): Promise<T> => {
    return tracingService.traceAsyncFunction(name, fn, attributes);
  };

  return { traceFunction, traceAsyncFunction };
};

export default tracingService; 