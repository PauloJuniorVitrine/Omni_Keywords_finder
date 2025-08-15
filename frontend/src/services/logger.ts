/**
 * Sistema de Logs Estruturado
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por fornecer sistema de logs estruturado e centralizado
 * Suporta diferentes níveis, formatação e destinos de log
 */

// Níveis de log
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  CRITICAL = 4
}

// Interface para entrada de log
export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  context?: Record<string, any>;
  error?: Error;
  userId?: string;
  sessionId?: string;
  requestId?: string;
  component?: string;
  action?: string;
  duration?: number;
  tags?: Record<string, string>;
}

// Interface para configuração do logger
export interface LoggerConfig {
  level: LogLevel;
  enableConsole: boolean;
  enableRemote: boolean;
  enableLocalStorage: boolean;
  maxLocalStorageLogs: number;
  remoteEndpoint?: string;
  batchSize: number;
  batchTimeout: number;
  enableSampling: boolean;
  samplingRate: number;
  enableUserTracking: boolean;
  enableSessionTracking: boolean;
  enablePerformanceTracking: boolean;
  customFormatters?: Record<LogLevel, (entry: LogEntry) => string>;
}

// Interface para transport de log
export interface LogTransport {
  name: string;
  enabled: boolean;
  log(entry: LogEntry): Promise<void>;
  flush?(): Promise<void>;
}

// Transport para console
class ConsoleTransport implements LogTransport {
  name = 'console';
  enabled = true;

  async log(entry: LogEntry): Promise<void> {
    const formattedMessage = this.formatMessage(entry);
    
    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(formattedMessage);
        break;
      case LogLevel.INFO:
        console.info(formattedMessage);
        break;
      case LogLevel.WARN:
        console.warn(formattedMessage);
        break;
      case LogLevel.ERROR:
      case LogLevel.CRITICAL:
        console.error(formattedMessage);
        break;
    }
  }

  private formatMessage(entry: LogEntry): string {
    const levelName = LogLevel[entry.level];
    const timestamp = new Date(entry.timestamp).toISOString();
    
    let message = `[${timestamp}] [${levelName}] ${entry.message}`;
    
    if (entry.component) {
      message += ` [${entry.component}]`;
    }
    
    if (entry.action) {
      message += ` [${entry.action}]`;
    }
    
    if (entry.duration !== undefined) {
      message += ` (${entry.duration}ms)`;
    }
    
    if (entry.context && Object.keys(entry.context).length > 0) {
      message += ` | Context: ${JSON.stringify(entry.context)}`;
    }
    
    if (entry.error) {
      message += ` | Error: ${entry.error.message}`;
      if (entry.error.stack) {
        message += ` | Stack: ${entry.error.stack}`;
      }
    }
    
    return message;
  }
}

// Transport para localStorage
class LocalStorageTransport implements LogTransport {
  name = 'localStorage';
  enabled = true;
  private maxLogs: number;
  private storageKey = 'app_logs';

  constructor(maxLogs: number = 1000) {
    this.maxLogs = maxLogs;
  }

  async log(entry: LogEntry): Promise<void> {
    try {
      const logs = this.getLogs();
      logs.push(entry);
      
      // Manter apenas os logs mais recentes
      if (logs.length > this.maxLogs) {
        logs.splice(0, logs.length - this.maxLogs);
      }
      
      localStorage.setItem(this.storageKey, JSON.stringify(logs));
    } catch (error) {
      console.warn('Failed to store log in localStorage:', error);
    }
  }

  private getLogs(): LogEntry[] {
    try {
      const logs = localStorage.getItem(this.storageKey);
      return logs ? JSON.parse(logs) : [];
    } catch {
      return [];
    }
  }

  async flush(): Promise<void> {
    // Limpar logs antigos
    const logs = this.getLogs();
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentLogs = logs.filter(log => new Date(log.timestamp) > oneDayAgo);
    localStorage.setItem(this.storageKey, JSON.stringify(recentLogs));
  }
}

// Transport para servidor remoto
class RemoteTransport implements LogTransport {
  name = 'remote';
  enabled = true;
  private endpoint: string;
  private batchSize: number;
  private batchTimeout: number;
  private logQueue: LogEntry[] = [];
  private batchTimeoutId: NodeJS.Timeout | null = null;

  constructor(endpoint: string, batchSize: number = 10, batchTimeout: number = 5000) {
    this.endpoint = endpoint;
    this.batchSize = batchSize;
    this.batchTimeout = batchTimeout;
  }

  async log(entry: LogEntry): Promise<void> {
    this.logQueue.push(entry);
    
    if (this.logQueue.length >= this.batchSize) {
      await this.flush();
    } else if (!this.batchTimeoutId) {
      this.batchTimeoutId = setTimeout(() => {
        this.flush();
      }, this.batchTimeout);
    }
  }

  async flush(): Promise<void> {
    if (this.batchTimeoutId) {
      clearTimeout(this.batchTimeoutId);
      this.batchTimeoutId = null;
    }

    if (this.logQueue.length === 0) {
      return;
    }

    const batch = this.logQueue.splice(0, this.batchSize);

    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          logs: batch,
          timestamp: new Date().toISOString(),
          batchId: this.generateBatchId()
        })
      });

      if (!response.ok) {
        throw new Error(`Remote logging failed: ${response.status}`);
      }
    } catch (error) {
      console.warn('Failed to send logs to remote server:', error);
      // Recolocar logs na fila para retry
      this.logQueue.unshift(...batch);
    }
  }

  private getAuthToken(): string {
    return localStorage.getItem('authToken') || '';
  }

  private generateBatchId(): string {
    return `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Classe principal do Logger
export class Logger {
  private static instance: Logger;
  private config: LoggerConfig;
  private transports: LogTransport[] = [];
  private sessionId: string;

  private constructor(config: Partial<LoggerConfig> = {}) {
    this.config = {
      level: LogLevel.INFO,
      enableConsole: true,
      enableRemote: false,
      enableLocalStorage: true,
      maxLocalStorageLogs: 1000,
      batchSize: 10,
      batchTimeout: 5000,
      enableSampling: false,
      samplingRate: 0.1,
      enableUserTracking: true,
      enableSessionTracking: true,
      enablePerformanceTracking: true,
      ...config
    };

    this.sessionId = this.generateSessionId();
    this.initializeTransports();
  }

  public static getInstance(config?: Partial<LoggerConfig>): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger(config);
    }
    return Logger.instance;
  }

  // Inicializar transports
  private initializeTransports(): void {
    if (this.config.enableConsole) {
      this.transports.push(new ConsoleTransport());
    }

    if (this.config.enableLocalStorage) {
      this.transports.push(new LocalStorageTransport(this.config.maxLocalStorageLogs));
    }

    if (this.config.enableRemote && this.config.remoteEndpoint) {
      this.transports.push(
        new RemoteTransport(
          this.config.remoteEndpoint,
          this.config.batchSize,
          this.config.batchTimeout
        )
      );
    }
  }

  // Log principal
  private log(
    level: LogLevel,
    message: string,
    context?: Record<string, any>,
    error?: Error,
    options?: {
      component?: string;
      action?: string;
      duration?: number;
      tags?: Record<string, string>;
    }
  ): void {
    // Verificar nível de log
    if (level < this.config.level) {
      return;
    }

    // Verificar sampling
    if (this.config.enableSampling && Math.random() > this.config.samplingRate) {
      return;
    }

    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      context,
      error,
      userId: this.config.enableUserTracking ? this.getCurrentUserId() : undefined,
      sessionId: this.config.enableSessionTracking ? this.sessionId : undefined,
      requestId: this.getRequestId(),
      component: options?.component,
      action: options?.action,
      duration: options?.duration,
      tags: {
        environment: process.env.NODE_ENV || 'development',
        version: process.env.REACT_APP_VERSION || 'unknown',
        ...options?.tags
      }
    };

    // Enviar para todos os transports
    this.transports.forEach(transport => {
      if (transport.enabled) {
        transport.log(entry).catch(console.warn);
      }
    });
  }

  // Métodos de log por nível
  public debug(message: string, context?: Record<string, any>, options?: any): void {
    this.log(LogLevel.DEBUG, message, context, undefined, options);
  }

  public info(message: string, context?: Record<string, any>, options?: any): void {
    this.log(LogLevel.INFO, message, context, undefined, options);
  }

  public warn(message: string, context?: Record<string, any>, options?: any): void {
    this.log(LogLevel.WARN, message, context, undefined, options);
  }

  public error(message: string, error?: Error, context?: Record<string, any>, options?: any): void {
    this.log(LogLevel.ERROR, message, context, error, options);
  }

  public critical(message: string, error?: Error, context?: Record<string, any>, options?: any): void {
    this.log(LogLevel.CRITICAL, message, context, error, options);
  }

  // Log de performance
  public performance(operation: string, duration: number, context?: Record<string, any>): void {
    if (this.config.enablePerformanceTracking) {
      this.info(`Performance: ${operation}`, context, {
        action: 'performance',
        duration,
        tags: { type: 'performance' }
      });
    }
  }

  // Log de métricas
  public metric(name: string, value: number, unit?: string, context?: Record<string, any>): void {
    this.info(`Metric: ${name} = ${value}${unit ? ` ${unit}` : ''}`, context, {
      action: 'metric',
      tags: { type: 'metric', metricName: name }
    });
  }

  // Log de eventos
  public event(eventName: string, data?: Record<string, any>, context?: Record<string, any>): void {
    this.info(`Event: ${eventName}`, { ...data, ...context }, {
      action: 'event',
      tags: { type: 'event', eventName }
    });
  }

  // Log de navegação
  public navigation(from: string, to: string, duration?: number): void {
    this.info(`Navigation: ${from} → ${to}`, undefined, {
      action: 'navigation',
      duration,
      tags: { type: 'navigation', from, to }
    });
  }

  // Log de API
  public api(method: string, url: string, status: number, duration: number, context?: Record<string, any>): void {
    const level = status >= 400 ? LogLevel.ERROR : LogLevel.INFO;
    this.log(level, `API: ${method} ${url} - ${status}`, context, undefined, {
      action: 'api',
      duration,
      tags: { type: 'api', method, url, status: status.toString() }
    });
  }

  // Log de erro de API
  public apiError(method: string, url: string, error: Error, context?: Record<string, any>): void {
    this.error(`API Error: ${method} ${url}`, error, context, {
      action: 'api_error',
      tags: { type: 'api_error', method, url }
    });
  }

  // Log de autenticação
  public auth(action: string, success: boolean, context?: Record<string, any>): void {
    const level = success ? LogLevel.INFO : LogLevel.WARN;
    this.log(level, `Auth: ${action} - ${success ? 'SUCCESS' : 'FAILED'}`, context, undefined, {
      action: 'auth',
      tags: { type: 'auth', authAction: action, success: success.toString() }
    });
  }

  // Log de segurança
  public security(event: string, context?: Record<string, any>): void {
    this.warn(`Security: ${event}`, context, {
      action: 'security',
      tags: { type: 'security', securityEvent: event }
    });
  }

  // Utilitários
  private generateSessionId(): string {
    let sessionId = sessionStorage.getItem('logger_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('logger_session_id', sessionId);
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

  // Métodos públicos
  public updateConfig(newConfig: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...newConfig };
    this.initializeTransports();
  }

  public getConfig(): LoggerConfig {
    return { ...this.config };
  }

  public async flush(): Promise<void> {
    const promises = this.transports.map(transport => 
      transport.flush ? transport.flush() : Promise.resolve()
    );
    await Promise.allSettled(promises);
  }

  public getLogs(): LogEntry[] {
    try {
      const logs = localStorage.getItem('app_logs');
      return logs ? JSON.parse(logs) : [];
    } catch {
      return [];
    }
  }

  public clearLogs(): void {
    localStorage.removeItem('app_logs');
  }
}

// Instância singleton
export const logger = Logger.getInstance();

// Hook para usar logger
export const useLogger = () => {
  return logger;
};

// Hook para log de performance
export const usePerformanceLogger = () => {
  const logPerformance = (operation: string, duration: number, context?: Record<string, any>) => {
    logger.performance(operation, duration, context);
  };

  const logMetric = (name: string, value: number, unit?: string, context?: Record<string, any>) => {
    logger.metric(name, value, unit, context);
  };

  return { logPerformance, logMetric };
};

// Hook para log de eventos
export const useEventLogger = () => {
  const logEvent = (eventName: string, data?: Record<string, any>, context?: Record<string, any>) => {
    logger.event(eventName, data, context);
  };

  const logNavigation = (from: string, to: string, duration?: number) => {
    logger.navigation(from, to, duration);
  };

  return { logEvent, logNavigation };
};

// Hook para log de API
export const useApiLogger = () => {
  const logApiCall = (method: string, url: string, status: number, duration: number, context?: Record<string, any>) => {
    logger.api(method, url, status, duration, context);
  };

  const logApiError = (method: string, url: string, error: Error, context?: Record<string, any>) => {
    logger.apiError(method, url, error, context);
  };

  return { logApiCall, logApiError };
};

export default logger; 