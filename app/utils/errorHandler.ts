/**
 * Utilitário Centralizado de Tratamento de Erros
 * 
 * Tracing ID: FIXTYPE-008_ERROR_HANDLER_20250127_001
 * Data: 2025-01-27
 * 
 * Fornece tratamento consistente de erros com:
 * - Tipos específicos de erro
 * - Retry automático
 * - Integração com error-tracking
 * - Fallbacks inteligentes
 */

import { captureError, addBreadcrumb } from './error-tracking';

// Tipos de erro específicos
export enum ErrorType {
  NETWORK = 'NETWORK',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  SERVER = 'SERVER',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN'
}

export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

// Interface para erro padronizado
export interface AppError {
  type: ErrorType;
  severity: ErrorSeverity;
  message: string;
  originalError?: Error;
  context?: Record<string, any>;
  retryable: boolean;
  retryCount?: number;
  maxRetries?: number;
}

// Configuração de retry
export interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
}

// Configuração padrão de retry
const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  backoffMultiplier: 2
};

// Mapeamento de códigos HTTP para tipos de erro
const HTTP_ERROR_MAPPING: Record<number, { type: ErrorType; severity: ErrorSeverity; retryable: boolean }> = {
  400: { type: ErrorType.VALIDATION, severity: ErrorSeverity.MEDIUM, retryable: false },
  401: { type: ErrorType.AUTHENTICATION, severity: ErrorSeverity.HIGH, retryable: false },
  403: { type: ErrorType.AUTHORIZATION, severity: ErrorSeverity.HIGH, retryable: false },
  404: { type: ErrorType.VALIDATION, severity: ErrorSeverity.MEDIUM, retryable: false },
  408: { type: ErrorType.TIMEOUT, severity: ErrorSeverity.MEDIUM, retryable: true },
  429: { type: ErrorType.SERVER, severity: ErrorSeverity.MEDIUM, retryable: true },
  500: { type: ErrorType.SERVER, severity: ErrorSeverity.HIGH, retryable: true },
  502: { type: ErrorType.SERVER, severity: ErrorSeverity.HIGH, retryable: true },
  503: { type: ErrorType.SERVER, severity: ErrorSeverity.HIGH, retryable: true },
  504: { type: ErrorType.TIMEOUT, severity: ErrorSeverity.MEDIUM, retryable: true }
};

/**
 * Classe principal de tratamento de erros
 */
export class ErrorHandler {
  private static instance: ErrorHandler;
  private retryConfig: RetryConfig;

  private constructor(config: RetryConfig = DEFAULT_RETRY_CONFIG) {
    this.retryConfig = config;
  }

  static getInstance(config?: RetryConfig): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler(config);
    }
    return ErrorHandler.instance;
  }

  /**
   * Processa e padroniza erro
   */
  processError(error: unknown, context?: Record<string, any>): AppError {
    // Se já é um AppError, retorna
    if (this.isAppError(error)) {
      return error;
    }

    // Se é um Error padrão
    if (error instanceof Error) {
      return this.createAppError(error, context);
    }

    // Se é uma string
    if (typeof error === 'string') {
      return this.createAppError(new Error(error), context);
    }

    // Erro desconhecido
    return this.createAppError(new Error('Erro desconhecido'), context);
  }

  /**
   * Cria AppError a partir de Error padrão
   */
  private createAppError(error: Error, context?: Record<string, any>): AppError {
    // Detectar tipo baseado na mensagem ou nome
    const type = this.detectErrorType(error);
    const severity = this.getSeverityForType(type);
    const retryable = this.isRetryableError(type);

    return {
      type,
      severity,
      message: error.message || 'Erro desconhecido',
      originalError: error,
      context,
      retryable,
      retryCount: 0,
      maxRetries: retryable ? this.retryConfig.maxRetries : 0
    };
  }

  /**
   * Detecta tipo de erro baseado em padrões
   */
  private detectErrorType(error: Error): ErrorType {
    const message = error.message.toLowerCase();
    const name = error.name.toLowerCase();

    // Network errors
    if (message.includes('network') || message.includes('fetch') || name === 'typeerror') {
      return ErrorType.NETWORK;
    }

    // Authentication errors
    if (message.includes('unauthorized') || message.includes('401')) {
      return ErrorType.AUTHENTICATION;
    }

    // Authorization errors
    if (message.includes('forbidden') || message.includes('403')) {
      return ErrorType.AUTHORIZATION;
    }

    // Validation errors
    if (message.includes('validation') || message.includes('invalid') || message.includes('400')) {
      return ErrorType.VALIDATION;
    }

    // Timeout errors
    if (message.includes('timeout') || message.includes('408') || message.includes('504')) {
      return ErrorType.TIMEOUT;
    }

    // Server errors
    if (message.includes('500') || message.includes('502') || message.includes('503')) {
      return ErrorType.SERVER;
    }

    return ErrorType.UNKNOWN;
  }

  /**
   * Obtém severidade para tipo de erro
   */
  private getSeverityForType(type: ErrorType): ErrorSeverity {
    switch (type) {
      case ErrorType.AUTHENTICATION:
      case ErrorType.AUTHORIZATION:
        return ErrorSeverity.HIGH;
      case ErrorType.SERVER:
        return ErrorSeverity.HIGH;
      case ErrorType.TIMEOUT:
      case ErrorType.VALIDATION:
        return ErrorSeverity.MEDIUM;
      case ErrorType.NETWORK:
        return ErrorSeverity.MEDIUM;
      default:
        return ErrorSeverity.LOW;
    }
  }

  /**
   * Verifica se erro é retryable
   */
  private isRetryableError(type: ErrorType): boolean {
    return [ErrorType.NETWORK, ErrorType.TIMEOUT, ErrorType.SERVER].includes(type);
  }

  /**
   * Verifica se é AppError
   */
  private isAppError(error: unknown): error is AppError {
    return typeof error === 'object' && error !== null && 'type' in error && 'severity' in error;
  }

  /**
   * Executa função com retry automático
   */
  async executeWithRetry<T>(
    fn: () => Promise<T>,
    context?: Record<string, any>
  ): Promise<T> {
    let lastError: AppError;
    let retryCount = 0;

    while (retryCount <= this.retryConfig.maxRetries) {
      try {
        return await fn();
      } catch (error) {
        lastError = this.processError(error, context);
        
        // Se não é retryable, para imediatamente
        if (!lastError.retryable) {
          this.handleError(lastError);
          throw lastError;
        }

        // Se atingiu max retries, para
        if (retryCount >= this.retryConfig.maxRetries) {
          lastError.retryCount = retryCount;
          this.handleError(lastError);
          throw lastError;
        }

        // Log do retry
        addBreadcrumb(
          `Retry ${retryCount + 1}/${this.retryConfig.maxRetries}`,
          'retry',
          { error: lastError.message, retryCount }
        );

        // Aguarda antes do próximo retry
        await this.delay(this.getRetryDelay(retryCount));
        retryCount++;
      }
    }

    throw lastError!;
  }

  /**
   * Calcula delay para retry com backoff exponencial
   */
  private getRetryDelay(retryCount: number): number {
    const delay = this.retryConfig.baseDelay * Math.pow(this.retryConfig.backoffMultiplier, retryCount);
    return Math.min(delay, this.retryConfig.maxDelay);
  }

  /**
   * Delay utilitário
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Trata erro (log, tracking, etc.)
   */
  handleError(error: AppError): void {
    // Adicionar breadcrumb
    addBreadcrumb(
      `Erro ${error.type}: ${error.message}`,
      'error',
      {
        type: error.type,
        severity: error.severity,
        retryable: error.retryable,
        retryCount: error.retryCount
      }
    );

    // Capturar no Sentry se for erro crítico ou alto
    if (error.severity === ErrorSeverity.HIGH || error.severity === ErrorSeverity.CRITICAL) {
      captureError(error.originalError || new Error(error.message), {
        componentName: error.context?.componentName,
        action: error.context?.action,
        metadata: {
          errorType: error.type,
          severity: error.severity,
          retryable: error.retryable,
          retryCount: error.retryCount,
          ...error.context
        }
      });
    }

    // Log no console em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.error('[ErrorHandler]', {
        type: error.type,
        severity: error.severity,
        message: error.message,
        retryable: error.retryable,
        retryCount: error.retryCount,
        context: error.context
      });
    }
  }

  /**
   * Cria mensagem amigável para usuário
   */
  getUserFriendlyMessage(error: AppError): string {
    switch (error.type) {
      case ErrorType.NETWORK:
        return 'Erro de conexão. Verifique sua internet e tente novamente.';
      case ErrorType.AUTHENTICATION:
        return 'Sessão expirada. Faça login novamente.';
      case ErrorType.AUTHORIZATION:
        return 'Você não tem permissão para realizar esta ação.';
      case ErrorType.VALIDATION:
        return 'Dados inválidos. Verifique as informações e tente novamente.';
      case ErrorType.SERVER:
        return 'Erro no servidor. Tente novamente em alguns instantes.';
      case ErrorType.TIMEOUT:
        return 'Tempo limite excedido. Tente novamente.';
      default:
        return 'Ocorreu um erro inesperado. Tente novamente.';
    }
  }

  /**
   * Verifica se deve mostrar erro para usuário
   */
  shouldShowToUser(error: AppError): boolean {
    // Não mostrar erros de rede em retry
    if (error.type === ErrorType.NETWORK && error.retryCount && error.retryCount > 0) {
      return false;
    }

    // Mostrar todos os erros não-retryable
    if (!error.retryable) {
      return true;
    }

    // Mostrar erros retryable apenas após max retries
    return error.retryCount === this.retryConfig.maxRetries;
  }
}

// Instância singleton
export const errorHandler = ErrorHandler.getInstance();

// Funções utilitárias para uso direto
export const processError = (error: unknown, context?: Record<string, any>): AppError => {
  return errorHandler.processError(error, context);
};

export const executeWithRetry = <T>(
  fn: () => Promise<T>,
  context?: Record<string, any>
): Promise<T> => {
  return errorHandler.executeWithRetry(fn, context);
};

export const handleError = (error: AppError): void => {
  errorHandler.handleError(error);
};

export const getUserFriendlyMessage = (error: AppError): string => {
  return errorHandler.getUserFriendlyMessage(error);
};

export const shouldShowToUser = (error: AppError): boolean => {
  return errorHandler.shouldShowToUser(error);
};

// Hook para uso em componentes React
export const useErrorHandler = () => {
  return {
    processError,
    executeWithRetry,
    handleError,
    getUserFriendlyMessage,
    shouldShowToUser,
    ErrorType,
    ErrorSeverity
  };
}; 