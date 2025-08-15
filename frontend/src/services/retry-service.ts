/**
 * Retry Service para Erros Recuperáveis
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por implementar retry automático para erros recuperáveis
 * Suporta diferentes estratégias de retry e backoff
 */

import { logger } from './logger';

// Tipos de estratégia de retry
export enum RetryStrategy {
  IMMEDIATE = 'IMMEDIATE',
  LINEAR = 'LINEAR',
  EXPONENTIAL = 'EXPONENTIAL',
  FIBONACCI = 'FIBONACCI',
  CUSTOM = 'CUSTOM'
}

// Interface para configuração de retry
export interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  strategy: RetryStrategy;
  jitter: boolean;
  jitterFactor: number;
  retryableErrors: string[];
  nonRetryableErrors: string[];
  onRetry?: (attempt: number, error: Error, delay: number) => void;
  onMaxRetriesReached?: (error: Error, attempts: number) => void;
  onSuccess?: (result: any, attempts: number) => void;
}

// Interface para contexto de retry
export interface RetryContext {
  attempt: number;
  maxRetries: number;
  lastError: Error;
  totalDelay: number;
  startTime: number;
  strategy: RetryStrategy;
}

// Classe principal do Retry Service
export class RetryService {
  private static instance: RetryService;
  private defaultConfig: RetryConfig;
  private activeRetries: Map<string, RetryContext> = new Map();

  private constructor(config: Partial<RetryConfig> = {}) {
    this.defaultConfig = {
      maxRetries: 3,
      baseDelay: 1000,
      maxDelay: 30000,
      strategy: RetryStrategy.EXPONENTIAL,
      jitter: true,
      jitterFactor: 0.1,
      retryableErrors: [
        'network',
        'timeout',
        'server error',
        'service unavailable',
        'gateway timeout'
      ],
      nonRetryableErrors: [
        'unauthorized',
        'forbidden',
        'not found',
        'bad request',
        'validation error'
      ],
      ...config
    };
  }

  public static getInstance(config?: Partial<RetryConfig>): RetryService {
    if (!RetryService.instance) {
      RetryService.instance = new RetryService(config);
    }
    return RetryService.instance;
  }

  // Executar função com retry
  public async executeWithRetry<T>(
    operation: () => Promise<T>,
    config?: Partial<RetryConfig>
  ): Promise<T> {
    const finalConfig = { ...this.defaultConfig, ...config };
    const operationId = this.generateOperationId();
    const startTime = Date.now();

    let lastError: Error;
    let totalDelay = 0;

    for (let attempt = 0; attempt <= finalConfig.maxRetries; attempt++) {
      try {
        const result = await operation();
        
        // Sucesso
        if (finalConfig.onSuccess) {
          finalConfig.onSuccess(result, attempt);
        }

        logger.info('[RETRY_SERVICE] Operation succeeded', {
          operationId,
          attempt,
          totalDelay,
          duration: Date.now() - startTime
        });

        return result;

      } catch (error) {
        lastError = error as Error;
        
        // Verificar se deve fazer retry
        if (!this.shouldRetry(error as Error, attempt, finalConfig)) {
          logger.warn('[RETRY_SERVICE] Non-retryable error', {
            operationId,
            attempt,
            error: error.message,
            errorType: this.getErrorType(error as Error)
          });
          throw error;
        }

        // Se é a última tentativa, não fazer retry
        if (attempt === finalConfig.maxRetries) {
          if (finalConfig.onMaxRetriesReached) {
            finalConfig.onMaxRetriesReached(error as Error, attempt);
          }

          logger.error('[RETRY_SERVICE] Max retries reached', {
            operationId,
            attempt,
            totalDelay,
            duration: Date.now() - startTime,
            error: error.message
          });

          throw error;
        }

        // Calcular delay para próximo retry
        const delay = this.calculateDelay(attempt, finalConfig);
        totalDelay += delay;

        // Callback de retry
        if (finalConfig.onRetry) {
          finalConfig.onRetry(attempt + 1, error as Error, delay);
        }

        // Registrar contexto de retry
        this.activeRetries.set(operationId, {
          attempt: attempt + 1,
          maxRetries: finalConfig.maxRetries,
          lastError: error as Error,
          totalDelay,
          startTime,
          strategy: finalConfig.strategy
        });

        logger.info('[RETRY_SERVICE] Retrying operation', {
          operationId,
          attempt: attempt + 1,
          delay,
          totalDelay,
          error: error.message
        });

        // Aguardar antes do próximo retry
        await this.wait(delay);
      }
    }

    throw lastError!;
  }

  // Verificar se deve fazer retry
  private shouldRetry(error: Error, attempt: number, config: RetryConfig): boolean {
    // Se já atingiu max retries
    if (attempt >= config.maxRetries) {
      return false;
    }

    const errorMessage = error.message.toLowerCase();
    const errorName = error.name.toLowerCase();

    // Verificar erros não retryable
    for (const nonRetryable of config.nonRetryableErrors) {
      if (errorMessage.includes(nonRetryable) || errorName.includes(nonRetryable)) {
        return false;
      }
    }

    // Verificar erros retryable
    for (const retryable of config.retryableErrors) {
      if (errorMessage.includes(retryable) || errorName.includes(retryable)) {
        return true;
      }
    }

    // Se não encontrou padrão específico, retry por padrão
    return true;
  }

  // Calcular delay baseado na estratégia
  private calculateDelay(attempt: number, config: RetryConfig): number {
    let delay: number;

    switch (config.strategy) {
      case RetryStrategy.IMMEDIATE:
        delay = 0;
        break;

      case RetryStrategy.LINEAR:
        delay = config.baseDelay * (attempt + 1);
        break;

      case RetryStrategy.EXPONENTIAL:
        delay = config.baseDelay * Math.pow(2, attempt);
        break;

      case RetryStrategy.FIBONACCI:
        delay = config.baseDelay * this.fibonacci(attempt + 1);
        break;

      case RetryStrategy.CUSTOM:
        delay = config.baseDelay * (attempt + 1) * (attempt + 1); // Quadrático
        break;

      default:
        delay = config.baseDelay * Math.pow(2, attempt);
    }

    // Aplicar jitter se habilitado
    if (config.jitter) {
      const jitter = delay * config.jitterFactor * (Math.random() - 0.5);
      delay += jitter;
    }

    // Limitar ao delay máximo
    return Math.min(delay, config.maxDelay);
  }

  // Calcular número de Fibonacci
  private fibonacci(n: number): number {
    if (n <= 1) return n;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }

  // Aguardar por um tempo
  private wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Gerar ID único para operação
  private generateOperationId(): string {
    return `retry_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Determinar tipo do erro
  private getErrorType(error: Error): string {
    const message = error.message.toLowerCase();
    const name = error.name.toLowerCase();

    if (name.includes('network') || message.includes('fetch') || message.includes('network')) {
      return 'NETWORK';
    }

    if (name.includes('timeout') || message.includes('timeout')) {
      return 'TIMEOUT';
    }

    if (message.includes('server') || message.includes('500')) {
      return 'SERVER';
    }

    if (message.includes('unauthorized') || message.includes('401')) {
      return 'AUTHENTICATION';
    }

    if (message.includes('forbidden') || message.includes('403')) {
      return 'AUTHORIZATION';
    }

    if (message.includes('not found') || message.includes('404')) {
      return 'NOT_FOUND';
    }

    if (message.includes('validation') || message.includes('invalid')) {
      return 'VALIDATION';
    }

    return 'UNKNOWN';
  }

  // Retry para operações HTTP
  public async retryHttpRequest<T>(
    requestFn: () => Promise<Response>,
    config?: Partial<RetryConfig>
  ): Promise<T> {
    return this.executeWithRetry(async () => {
      const response = await requestFn();
      
      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        (error as any).status = response.status;
        (error as any).response = response;
        throw error;
      }

      return response.json();
    }, config);
  }

  // Retry para operações de API
  public async retryApiCall<T>(
    apiCall: () => Promise<T>,
    config?: Partial<RetryConfig>
  ): Promise<T> {
    return this.executeWithRetry(apiCall, {
      retryableErrors: [
        'network',
        'timeout',
        'server error',
        'service unavailable',
        'gateway timeout',
        'connection refused'
      ],
      ...config
    });
  }

  // Retry para operações de WebSocket
  public async retryWebSocketConnection(
    connectFn: () => Promise<WebSocket>,
    config?: Partial<RetryConfig>
  ): Promise<WebSocket> {
    return this.executeWithRetry(connectFn, {
      strategy: RetryStrategy.EXPONENTIAL,
      baseDelay: 2000,
      maxDelay: 60000,
      retryableErrors: [
        'connection refused',
        'timeout',
        'network',
        'websocket error'
      ],
      ...config
    });
  }

  // Retry para operações de upload
  public async retryUpload<T>(
    uploadFn: () => Promise<T>,
    config?: Partial<RetryConfig>
  ): Promise<T> {
    return this.executeWithRetry(uploadFn, {
      strategy: RetryStrategy.LINEAR,
      baseDelay: 2000,
      maxRetries: 5,
      retryableErrors: [
        'network',
        'timeout',
        'server error',
        'connection lost'
      ],
      ...config
    });
  }

  // Cancelar retry ativo
  public cancelRetry(operationId: string): boolean {
    return this.activeRetries.delete(operationId);
  }

  // Obter retries ativos
  public getActiveRetries(): RetryContext[] {
    return Array.from(this.activeRetries.values());
  }

  // Limpar retries ativos
  public clearActiveRetries(): void {
    this.activeRetries.clear();
  }

  // Atualizar configuração padrão
  public updateDefaultConfig(newConfig: Partial<RetryConfig>): void {
    this.defaultConfig = { ...this.defaultConfig, ...newConfig };
  }

  // Obter configuração padrão
  public getDefaultConfig(): RetryConfig {
    return { ...this.defaultConfig };
  }
}

// Instância singleton
export const retryService = RetryService.getInstance();

// Hook para usar retry service
export const useRetryService = () => {
  return retryService;
};

// Hook para retry de operações
export const useRetry = (config?: Partial<RetryConfig>) => {
  const executeWithRetry = async <T>(operation: () => Promise<T>): Promise<T> => {
    return retryService.executeWithRetry(operation, config);
  };

  const retryHttpRequest = async <T>(requestFn: () => Promise<Response>): Promise<T> => {
    return retryService.retryHttpRequest(requestFn, config);
  };

  const retryApiCall = async <T>(apiCall: () => Promise<T>): Promise<T> => {
    return retryService.retryApiCall(apiCall, config);
  };

  return {
    executeWithRetry,
    retryHttpRequest,
    retryApiCall
  };
};

export default retryService; 