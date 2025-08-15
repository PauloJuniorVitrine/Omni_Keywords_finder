/**
 * Error Handler Centralizado
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por centralizar tratamento de erros da aplicação
 * Fornece categorização, logging e ações corretivas
 */

import { logger } from './logger';

// Tipos de erro
export enum ErrorType {
  NETWORK = 'NETWORK',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  SERVER = 'SERVER',
  CLIENT = 'CLIENT',
  UNKNOWN = 'UNKNOWN'
}

// Severidade do erro
export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

// Interface para erro estruturado
export interface StructuredError {
  id: string;
  type: ErrorType;
  severity: ErrorSeverity;
  message: string;
  originalError?: Error;
  context?: Record<string, any>;
  timestamp: string;
  url: string;
  userAgent: string;
  userId?: string;
  sessionId?: string;
  retryable: boolean;
  retryCount: number;
  maxRetries: number;
}

// Interface para configuração do handler
export interface ErrorHandlerConfig {
  enableRetry: boolean;
  maxRetries: number;
  retryDelay: number;
  enableReporting: boolean;
  enableLogging: boolean;
  enableNotifications: boolean;
  ignoredErrors?: string[];
  customHandlers?: Record<ErrorType, (error: StructuredError) => void>;
}

// Classe principal do Error Handler
export class ErrorHandler {
  private static instance: ErrorHandler;
  private config: ErrorHandlerConfig;
  private errorQueue: StructuredError[] = [];
  private retryQueue: Map<string, NodeJS.Timeout> = new Map();

  private constructor(config: Partial<ErrorHandlerConfig> = {}) {
    this.config = {
      enableRetry: true,
      maxRetries: 3,
      retryDelay: 1000,
      enableReporting: true,
      enableLogging: true,
      enableNotifications: true,
      ignoredErrors: [],
      customHandlers: {},
      ...config
    };

    this.setupGlobalErrorHandlers();
  }

  public static getInstance(config?: Partial<ErrorHandlerConfig>): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler(config);
    }
    return ErrorHandler.instance;
  }

  // Configurar handlers globais
  private setupGlobalErrorHandlers(): void {
    // Handler para erros não capturados
    window.addEventListener('error', (event) => {
      this.handleError(event.error, {
        context: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno
        }
      });
    });

    // Handler para promises rejeitadas
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason, {
        context: {
          type: 'unhandledrejection'
        }
      });
    });

    // Handler para erros de rede
    window.addEventListener('offline', () => {
      this.handleError(new Error('Network connection lost'), {
        type: ErrorType.NETWORK,
        severity: ErrorSeverity.HIGH
      });
    });
  }

  // Método principal para tratar erros
  public handleError(
    error: Error | string,
    options: {
      type?: ErrorType;
      severity?: ErrorSeverity;
      context?: Record<string, any>;
      retryable?: boolean;
      maxRetries?: number;
    } = {}
  ): StructuredError {
    const errorMessage = typeof error === 'string' ? error : error.message;
    const errorId = this.generateErrorId();

    // Verificar se é erro ignorado
    if (this.config.ignoredErrors?.some(ignored => errorMessage.includes(ignored))) {
      logger.debug('[ERROR_HANDLER] Error ignored', { errorMessage, errorId });
      return this.createStructuredError(error, options, errorId);
    }

    const structuredError = this.createStructuredError(error, options, errorId);

    // Log do erro
    if (this.config.enableLogging) {
      this.logError(structuredError);
    }

    // Adicionar à fila para processamento
    this.errorQueue.push(structuredError);

    // Executar handler customizado se existir
    const customHandler = this.config.customHandlers?.[structuredError.type];
    if (customHandler) {
      customHandler(structuredError);
    }

    // Executar ações baseadas no tipo e severidade
    this.executeErrorActions(structuredError);

    // Retry automático se habilitado e retryable
    if (this.config.enableRetry && structuredError.retryable) {
      this.scheduleRetry(structuredError);
    }

    return structuredError;
  }

  // Criar erro estruturado
  private createStructuredError(
    error: Error | string,
    options: {
      type?: ErrorType;
      severity?: ErrorSeverity;
      context?: Record<string, any>;
      retryable?: boolean;
      maxRetries?: number;
    },
    errorId: string
  ): StructuredError {
    const errorMessage = typeof error === 'string' ? error : error.message;
    const originalError = typeof error === 'string' ? new Error(error) : error;

    // Determinar tipo do erro
    const type = options.type || this.determineErrorType(originalError);
    
    // Determinar severidade
    const severity = options.severity || this.determineErrorSeverity(type, originalError);
    
    // Determinar se é retryable
    const retryable = options.retryable ?? this.isRetryable(type, originalError);

    return {
      id: errorId,
      type,
      severity,
      message: errorMessage,
      originalError,
      context: {
        ...options.context,
        userAgent: navigator.userAgent,
        url: window.location.href
      },
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      userId: this.getCurrentUserId(),
      sessionId: this.getSessionId(),
      retryable,
      retryCount: 0,
      maxRetries: options.maxRetries || this.config.maxRetries
    };
  }

  // Determinar tipo do erro
  private determineErrorType(error: Error): ErrorType {
    const message = error.message.toLowerCase();
    const name = error.name.toLowerCase();

    if (name.includes('network') || message.includes('fetch') || message.includes('network')) {
      return ErrorType.NETWORK;
    }

    if (name.includes('auth') || message.includes('unauthorized') || message.includes('forbidden')) {
      return ErrorType.AUTHENTICATION;
    }

    if (message.includes('validation') || message.includes('invalid')) {
      return ErrorType.VALIDATION;
    }

    if (message.includes('server') || message.includes('500')) {
      return ErrorType.SERVER;
    }

    return ErrorType.UNKNOWN;
  }

  // Determinar severidade do erro
  private determineErrorSeverity(type: ErrorType, error: Error): ErrorSeverity {
    switch (type) {
      case ErrorType.AUTHENTICATION:
      case ErrorType.AUTHORIZATION:
        return ErrorSeverity.HIGH;
      case ErrorType.NETWORK:
        return ErrorSeverity.MEDIUM;
      case ErrorType.VALIDATION:
        return ErrorSeverity.LOW;
      case ErrorType.SERVER:
        return ErrorSeverity.CRITICAL;
      default:
        return ErrorSeverity.MEDIUM;
    }
  }

  // Verificar se erro é retryable
  private isRetryable(type: ErrorType, error: Error): boolean {
    switch (type) {
      case ErrorType.NETWORK:
        return true;
      case ErrorType.SERVER:
        return true;
      case ErrorType.VALIDATION:
        return false;
      case ErrorType.AUTHENTICATION:
        return false;
      case ErrorType.AUTHORIZATION:
        return false;
      default:
        return false;
    }
  }

  // Log do erro
  private logError(error: StructuredError): void {
    const logData = {
      errorId: error.id,
      type: error.type,
      severity: error.severity,
      message: error.message,
      context: error.context,
      timestamp: error.timestamp,
      url: error.url,
      retryable: error.retryable,
      retryCount: error.retryCount
    };

    switch (error.severity) {
      case ErrorSeverity.CRITICAL:
        logger.error('[ERROR_HANDLER] Critical error', logData);
        break;
      case ErrorSeverity.HIGH:
        logger.error('[ERROR_HANDLER] High severity error', logData);
        break;
      case ErrorSeverity.MEDIUM:
        logger.warn('[ERROR_HANDLER] Medium severity error', logData);
        break;
      case ErrorSeverity.LOW:
        logger.info('[ERROR_HANDLER] Low severity error', logData);
        break;
    }
  }

  // Executar ações baseadas no erro
  private executeErrorActions(error: StructuredError): void {
    switch (error.severity) {
      case ErrorSeverity.CRITICAL:
        this.handleCriticalError(error);
        break;
      case ErrorSeverity.HIGH:
        this.handleHighSeverityError(error);
        break;
      case ErrorSeverity.MEDIUM:
        this.handleMediumSeverityError(error);
        break;
      case ErrorSeverity.LOW:
        this.handleLowSeverityError(error);
        break;
    }
  }

  // Handler para erros críticos
  private handleCriticalError(error: StructuredError): void {
    // Notificar usuário imediatamente
    if (this.config.enableNotifications) {
      this.showNotification('Erro crítico detectado. A aplicação pode não funcionar corretamente.', 'error');
    }

    // Reportar para analytics
    if (this.config.enableReporting) {
      this.reportError(error);
    }

    // Possível reload da aplicação
    if (error.type === ErrorType.SERVER) {
      setTimeout(() => {
        window.location.reload();
      }, 5000);
    }
  }

  // Handler para erros de alta severidade
  private handleHighSeverityError(error: StructuredError): void {
    if (this.config.enableNotifications) {
      this.showNotification('Erro importante detectado. Verifique sua conexão.', 'warning');
    }

    if (this.config.enableReporting) {
      this.reportError(error);
    }
  }

  // Handler para erros de média severidade
  private handleMediumSeverityError(error: StructuredError): void {
    if (this.config.enableReporting) {
      this.reportError(error);
    }
  }

  // Handler para erros de baixa severidade
  private handleLowSeverityError(error: StructuredError): void {
    // Apenas log, sem ações especiais
  }

  // Agendar retry
  private scheduleRetry(error: StructuredError): void {
    if (error.retryCount >= error.maxRetries) {
      logger.warn('[ERROR_HANDLER] Max retries reached', { errorId: error.id, retryCount: error.retryCount });
      return;
    }

    const delay = this.config.retryDelay * Math.pow(2, error.retryCount); // Exponential backoff

    const timeout = setTimeout(() => {
      this.retryError(error);
    }, delay);

    this.retryQueue.set(error.id, timeout);
  }

  // Retry do erro
  private retryError(error: StructuredError): void {
    error.retryCount++;
    
    logger.info('[ERROR_HANDLER] Retrying error', { 
      errorId: error.id, 
      retryCount: error.retryCount,
      maxRetries: error.maxRetries 
    });

    // Aqui você pode implementar a lógica de retry específica
    // Por exemplo, re-executar a operação que falhou
  }

  // Mostrar notificação
  private showNotification(message: string, type: 'info' | 'warning' | 'error'): void {
    // Integração com sistema de notificações
    if (window.showNotification) {
      window.showNotification(message, type);
    } else {
      // Fallback para alert
      console.warn(`[${type.toUpperCase()}] ${message}`);
    }
  }

  // Reportar erro
  private reportError(error: StructuredError): void {
    // Integração com analytics
    if (window.gtag) {
      window.gtag('event', 'exception', {
        description: error.message,
        fatal: error.severity === ErrorSeverity.CRITICAL,
        error_id: error.id
      });
    }

    // Integração com Sentry
    if (window.Sentry) {
      window.Sentry.captureException(error.originalError, {
        tags: {
          errorId: error.id,
          type: error.type,
          severity: error.severity
        },
        extra: {
          context: error.context,
          retryCount: error.retryCount
        }
      });
    }

    // Enviar para endpoint de report
    fetch('/api/error-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(error)
    }).catch(console.error);
  }

  // Utilitários
  private generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCurrentUserId(): string | undefined {
    // Implementar lógica para obter ID do usuário atual
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

  // Métodos públicos
  public getErrorQueue(): StructuredError[] {
    return [...this.errorQueue];
  }

  public clearErrorQueue(): void {
    this.errorQueue = [];
  }

  public updateConfig(newConfig: Partial<ErrorHandlerConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  public getConfig(): ErrorHandlerConfig {
    return { ...this.config };
  }
}

// Instância singleton
export const errorHandler = ErrorHandler.getInstance();

// Hook para usar error handler
export const useErrorHandler = () => {
  return errorHandler;
};

export default errorHandler; 