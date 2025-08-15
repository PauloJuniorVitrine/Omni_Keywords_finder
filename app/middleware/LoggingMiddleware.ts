/**
 * LoggingMiddleware.ts
 * 
 * Middleware de logging para o store
 * 
 * Tracing ID: LOGGING_MIDDLEWARE_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.3
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Logging de ações do store
 * - Performance monitoring
 * - Error tracking
 * - Analytics
 */

import { AppAction } from '../store/AppStore';

export interface LogEntry {
  timestamp: string;
  action: string;
  payload?: any;
  userId?: string;
  sessionId: string;
  performance?: {
    duration: number;
    memory?: number;
  };
  error?: {
    message: string;
    stack?: string;
  };
}

export interface LoggingConfig {
  enabled: boolean;
  level: 'debug' | 'info' | 'warn' | 'error';
  persist: boolean;
  maxEntries: number;
  includePerformance: boolean;
  includeMemory: boolean;
}

class LoggingMiddleware {
  private config: LoggingConfig;
  private logs: LogEntry[] = [];
  private sessionId: string;
  private startTime: number;

  constructor(config: Partial<LoggingConfig> = {}) {
    this.config = {
      enabled: true,
      level: 'info',
      persist: true,
      maxEntries: 1000,
      includePerformance: true,
      includeMemory: false,
      ...config,
    };

    this.sessionId = this.generateSessionId();
    this.startTime = Date.now();

    // Carregar logs persistidos
    if (this.config.persist) {
      this.loadLogs();
    }
  }

  // Middleware principal
  middleware = (action: AppAction, getState: () => any, dispatch: (action: AppAction) => void) => {
    if (!this.config.enabled) {
      return dispatch(action);
    }

    const startTime = performance.now();
    const startMemory = this.config.includeMemory ? performance.memory?.usedJSHeapSize : undefined;

    try {
      // Executar ação
      const result = dispatch(action);

      // Calcular performance
      const endTime = performance.now();
      const duration = endTime - startTime;
      const endMemory = this.config.includeMemory ? performance.memory?.usedJSHeapSize : undefined;

      // Criar entrada de log
      const logEntry: LogEntry = {
        timestamp: new Date().toISOString(),
        action: action.type,
        payload: action,
        sessionId: this.sessionId,
        performance: this.config.includePerformance ? {
          duration,
          memory: endMemory && startMemory ? endMemory - startMemory : undefined,
        } : undefined,
      };

      // Adicionar log
      this.addLog(logEntry);

      return result;
    } catch (error) {
      // Log de erro
      const logEntry: LogEntry = {
        timestamp: new Date().toISOString(),
        action: action.type,
        payload: action,
        sessionId: this.sessionId,
        error: {
          message: error instanceof Error ? error.message : 'Unknown error',
          stack: error instanceof Error ? error.stack : undefined,
        },
      };

      this.addLog(logEntry);
      throw error;
    }
  };

  // Adicionar log
  private addLog(entry: LogEntry): void {
    this.logs.push(entry);

    // Limitar número de logs
    if (this.logs.length > this.config.maxEntries) {
      this.logs = this.logs.slice(-this.config.maxEntries);
    }

    // Persistir logs
    if (this.config.persist) {
      this.persistLogs();
    }

    // Console log baseado no nível
    this.consoleLog(entry);
  }

  // Log no console
  private consoleLog(entry: LogEntry): void {
    const { level, action, payload, performance, error } = entry;

    if (error) {
      console.error(`[Store] ${action}:`, error.message, payload);
      return;
    }

    const message = `[Store] ${action}`;
    const data = { payload, performance };

    switch (this.config.level) {
      case 'debug':
        console.debug(message, data);
        break;
      case 'info':
        console.info(message, data);
        break;
      case 'warn':
        console.warn(message, data);
        break;
      case 'error':
        console.error(message, data);
        break;
    }
  }

  // Persistir logs
  private persistLogs(): void {
    try {
      localStorage.setItem('store_logs', JSON.stringify(this.logs));
    } catch (error) {
      console.warn('[LoggingMiddleware] Failed to persist logs:', error);
    }
  }

  // Carregar logs persistidos
  private loadLogs(): void {
    try {
      const persisted = localStorage.getItem('store_logs');
      if (persisted) {
        this.logs = JSON.parse(persisted);
      }
    } catch (error) {
      console.warn('[LoggingMiddleware] Failed to load persisted logs:', error);
    }
  }

  // Gerar ID de sessão
  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Obter logs
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  // Obter logs por ação
  getLogsByAction(actionType: string): LogEntry[] {
    return this.logs.filter(log => log.action === actionType);
  }

  // Obter logs por período
  getLogsByPeriod(startDate: Date, endDate: Date): LogEntry[] {
    return this.logs.filter(log => {
      const timestamp = new Date(log.timestamp);
      return timestamp >= startDate && timestamp <= endDate;
    });
  }

  // Obter logs com erro
  getErrorLogs(): LogEntry[] {
    return this.logs.filter(log => log.error);
  }

  // Limpar logs
  clearLogs(): void {
    this.logs = [];
    if (this.config.persist) {
      localStorage.removeItem('store_logs');
    }
  }

  // Exportar logs
  exportLogs(): string {
    return JSON.stringify({
      sessionId: this.sessionId,
      startTime: this.startTime,
      endTime: Date.now(),
      logs: this.logs,
      config: this.config,
    }, null, 2);
  }

  // Obter estatísticas
  getStats() {
    const total = this.logs.length;
    const errors = this.logs.filter(log => log.error).length;
    const actions = this.logs.reduce((acc, log) => {
      acc[log.action] = (acc[log.action] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const avgDuration = this.logs
      .filter(log => log.performance?.duration)
      .reduce((sum, log) => sum + (log.performance?.duration || 0), 0) / 
      this.logs.filter(log => log.performance?.duration).length;

    return {
      total,
      errors,
      errorRate: total > 0 ? (errors / total) * 100 : 0,
      actions,
      avgDuration: avgDuration || 0,
      sessionDuration: Date.now() - this.startTime,
    };
  }

  // Configurar middleware
  configure(config: Partial<LoggingConfig>): void {
    this.config = { ...this.config, ...config };
  }

  // Habilitar/desabilitar
  setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
  }

  // Definir nível de log
  setLevel(level: LoggingConfig['level']): void {
    this.config.level = level;
  }
}

// Instância global
export const loggingMiddleware = new LoggingMiddleware({
  enabled: process.env.NODE_ENV === 'development',
  level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
  persist: true,
  maxEntries: 1000,
  includePerformance: true,
  includeMemory: false,
});

export default loggingMiddleware; 