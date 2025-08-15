/**
 * Teste do Sistema de Tratamento de Erros
 * 
 * Tracing ID: FIXTYPE-008_TEST_ERROR_HANDLER_20250127_001
 * Data: 2025-01-27
 * 
 * Testa todas as funcionalidades do errorHandler:
 * - Processamento de erros
 * - Retry automático
 * - Tipos de erro
 * - Mensagens amigáveis
 * - Integração com error-tracking
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  ErrorHandler,
  ErrorType,
  ErrorSeverity,
  AppError,
  processError,
  executeWithRetry,
  handleError,
  getUserFriendlyMessage,
  shouldShowToUser,
  useErrorHandler
} from '../../../app/utils/errorHandler';

// Mock do error-tracking
vi.mock('../../../app/utils/error-tracking', () => ({
  captureError: vi.fn(),
  addBreadcrumb: vi.fn()
}));

describe('ErrorHandler', () => {
  let errorHandler: ErrorHandler;

  beforeEach(() => {
    // Reset singleton para cada teste
    (ErrorHandler as any).instance = undefined;
    errorHandler = ErrorHandler.getInstance();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('processError', () => {
    it('deve processar Error padrão', () => {
      const error = new Error('Erro de rede');
      const result = errorHandler.processError(error);

      expect(result).toEqual({
        type: ErrorType.NETWORK,
        severity: ErrorSeverity.MEDIUM,
        message: 'Erro de rede',
        originalError: error,
        context: undefined,
        retryable: true,
        retryCount: 0,
        maxRetries: 3
      });
    });

    it('deve processar string como erro', () => {
      const result = errorHandler.processError('Erro de validação');

      expect(result.type).toBe(ErrorType.VALIDATION);
      expect(result.message).toBe('Erro de validação');
      expect(result.retryable).toBe(false);
    });

    it('deve processar AppError existente', () => {
      const appError: AppError = {
        type: ErrorType.AUTHENTICATION,
        severity: ErrorSeverity.HIGH,
        message: 'Sessão expirada',
        retryable: false
      };

      const result = errorHandler.processError(appError);
      expect(result).toBe(appError);
    });

    it('deve detectar tipos de erro corretamente', () => {
      const testCases = [
        { error: new Error('Network error'), expected: ErrorType.NETWORK },
        { error: new Error('Unauthorized'), expected: ErrorType.AUTHENTICATION },
        { error: new Error('Forbidden'), expected: ErrorType.AUTHORIZATION },
        { error: new Error('Validation failed'), expected: ErrorType.VALIDATION },
        { error: new Error('Timeout'), expected: ErrorType.TIMEOUT },
        { error: new Error('500 Internal Server Error'), expected: ErrorType.SERVER },
        { error: new Error('Erro desconhecido'), expected: ErrorType.UNKNOWN }
      ];

      testCases.forEach(({ error, expected }) => {
        const result = errorHandler.processError(error);
        expect(result.type).toBe(expected);
      });
    });

    it('deve incluir contexto no processamento', () => {
      const error = new Error('Erro de teste');
      const context = { userId: '123', action: 'test' };

      const result = errorHandler.processError(error, context);

      expect(result.context).toEqual(context);
    });
  });

  describe('executeWithRetry', () => {
    it('deve executar função com sucesso na primeira tentativa', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');
      const context = { action: 'test' };

      const result = await errorHandler.executeWithRetry(mockFn, context);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('deve fazer retry em caso de erro retryable', async () => {
      const mockFn = vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue('success');

      const result = await errorHandler.executeWithRetry(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(3);
    });

    it('deve parar retry em erro não-retryable', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('Validation error'));

      await expect(errorHandler.executeWithRetry(mockFn)).rejects.toThrow();

      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('deve parar após max retries', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(errorHandler.executeWithRetry(mockFn)).rejects.toThrow();

      expect(mockFn).toHaveBeenCalledTimes(4); // 1 tentativa + 3 retries
    });

    it('deve usar backoff exponencial', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('Network error'));
      const startTime = Date.now();

      await expect(errorHandler.executeWithRetry(mockFn)).rejects.toThrow();

      const endTime = Date.now();
      const totalTime = endTime - startTime;

      // Deve ter pelo menos 1s + 2s + 4s = 7s de delay
      expect(totalTime).toBeGreaterThan(6000);
    });
  });

  describe('handleError', () => {
    it('deve capturar erro no Sentry para severidade alta', () => {
      const { captureError } = require('../../../app/utils/error-tracking');
      const error: AppError = {
        type: ErrorType.AUTHENTICATION,
        severity: ErrorSeverity.HIGH,
        message: 'Sessão expirada',
        retryable: false,
        context: { userId: '123' }
      };

      errorHandler.handleError(error);

      expect(captureError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          metadata: expect.objectContaining({
            errorType: ErrorType.AUTHENTICATION,
            severity: ErrorSeverity.HIGH,
            userId: '123'
          })
        })
      );
    });

    it('não deve capturar erro no Sentry para severidade baixa', () => {
      const { captureError } = require('../../../app/utils/error-tracking');
      const error: AppError = {
        type: ErrorType.VALIDATION,
        severity: ErrorSeverity.LOW,
        message: 'Campo inválido',
        retryable: false
      };

      errorHandler.handleError(error);

      expect(captureError).not.toHaveBeenCalled();
    });
  });

  describe('getUserFriendlyMessage', () => {
    it('deve retornar mensagens amigáveis para cada tipo', () => {
      const testCases = [
        { type: ErrorType.NETWORK, expected: 'Erro de conexão' },
        { type: ErrorType.AUTHENTICATION, expected: 'Sessão expirada' },
        { type: ErrorType.AUTHORIZATION, expected: 'Você não tem permissão' },
        { type: ErrorType.VALIDATION, expected: 'Dados inválidos' },
        { type: ErrorType.SERVER, expected: 'Erro no servidor' },
        { type: ErrorType.TIMEOUT, expected: 'Tempo limite excedido' },
        { type: ErrorType.UNKNOWN, expected: 'Ocorreu um erro inesperado' }
      ];

      testCases.forEach(({ type, expected }) => {
        const error: AppError = {
          type,
          severity: ErrorSeverity.MEDIUM,
          message: 'Test',
          retryable: false
        };

        const message = errorHandler.getUserFriendlyMessage(error);
        expect(message).toContain(expected);
      });
    });
  });

  describe('shouldShowToUser', () => {
    it('deve mostrar erro não-retryable', () => {
      const error: AppError = {
        type: ErrorType.VALIDATION,
        severity: ErrorSeverity.MEDIUM,
        message: 'Dados inválidos',
        retryable: false
      };

      expect(errorHandler.shouldShowToUser(error)).toBe(true);
    });

    it('não deve mostrar erro de rede em retry', () => {
      const error: AppError = {
        type: ErrorType.NETWORK,
        severity: ErrorSeverity.MEDIUM,
        message: 'Erro de rede',
        retryable: true,
        retryCount: 1
      };

      expect(errorHandler.shouldShowToUser(error)).toBe(false);
    });

    it('deve mostrar erro retryable após max retries', () => {
      const error: AppError = {
        type: ErrorType.NETWORK,
        severity: ErrorSeverity.MEDIUM,
        message: 'Erro de rede',
        retryable: true,
        retryCount: 3
      };

      expect(errorHandler.shouldShowToUser(error)).toBe(true);
    });
  });
});

describe('Funções utilitárias', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('processError deve funcionar como função standalone', () => {
    const error = new Error('Test error');
    const result = processError(error, { test: true });

    expect(result.type).toBe(ErrorType.UNKNOWN);
    expect(result.context).toEqual({ test: true });
  });

  it('executeWithRetry deve funcionar como função standalone', async () => {
    const mockFn = vi.fn().mockResolvedValue('success');
    const result = await executeWithRetry(mockFn);

    expect(result).toBe('success');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('handleError deve funcionar como função standalone', () => {
    const { captureError } = require('../../../app/utils/error-tracking');
    const error: AppError = {
      type: ErrorType.AUTHENTICATION,
      severity: ErrorSeverity.HIGH,
      message: 'Test',
      retryable: false
    };

    handleError(error);

    expect(captureError).toHaveBeenCalled();
  });

  it('getUserFriendlyMessage deve funcionar como função standalone', () => {
    const error: AppError = {
      type: ErrorType.NETWORK,
      severity: ErrorSeverity.MEDIUM,
      message: 'Test',
      retryable: true
    };

    const message = getUserFriendlyMessage(error);
    expect(message).toContain('Erro de conexão');
  });

  it('shouldShowToUser deve funcionar como função standalone', () => {
    const error: AppError = {
      type: ErrorType.VALIDATION,
      severity: ErrorSeverity.MEDIUM,
      message: 'Test',
      retryable: false
    };

    expect(shouldShowToUser(error)).toBe(true);
  });
});

describe('useErrorHandler hook', () => {
  it('deve retornar todas as funções necessárias', () => {
    const hook = useErrorHandler();

    expect(hook.processError).toBeDefined();
    expect(hook.executeWithRetry).toBeDefined();
    expect(hook.handleError).toBeDefined();
    expect(hook.getUserFriendlyMessage).toBeDefined();
    expect(hook.shouldShowToUser).toBeDefined();
    expect(hook.ErrorType).toBeDefined();
    expect(hook.ErrorSeverity).toBeDefined();
  });

  it('deve ter tipos de erro corretos', () => {
    const { ErrorType } = useErrorHandler();

    expect(ErrorType.NETWORK).toBe('NETWORK');
    expect(ErrorType.AUTHENTICATION).toBe('AUTHENTICATION');
    expect(ErrorType.AUTHORIZATION).toBe('AUTHORIZATION');
    expect(ErrorType.VALIDATION).toBe('VALIDATION');
    expect(ErrorType.SERVER).toBe('SERVER');
    expect(ErrorType.TIMEOUT).toBe('TIMEOUT');
    expect(ErrorType.UNKNOWN).toBe('UNKNOWN');
  });

  it('deve ter severidades corretas', () => {
    const { ErrorSeverity } = useErrorHandler();

    expect(ErrorSeverity.LOW).toBe('LOW');
    expect(ErrorSeverity.MEDIUM).toBe('MEDIUM');
    expect(ErrorSeverity.HIGH).toBe('HIGH');
    expect(ErrorSeverity.CRITICAL).toBe('CRITICAL');
  });
});

describe('Configuração de retry', () => {
  it('deve permitir configuração customizada', () => {
    const customConfig = {
      maxRetries: 5,
      baseDelay: 500,
      maxDelay: 5000,
      backoffMultiplier: 1.5
    };

    const customHandler = ErrorHandler.getInstance(customConfig);
    const error = new Error('Network error');
    const result = customHandler.processError(error);

    expect(result.maxRetries).toBe(5);
  });

  it('deve usar configuração padrão se não especificada', () => {
    const handler = ErrorHandler.getInstance();
    const error = new Error('Network error');
    const result = handler.processError(error);

    expect(result.maxRetries).toBe(3);
  });
});

describe('Integração com error-tracking', () => {
  it('deve adicionar breadcrumbs corretamente', () => {
    const { addBreadcrumb } = require('../../../app/utils/error-tracking');
    const error: AppError = {
      type: ErrorType.NETWORK,
      severity: ErrorSeverity.MEDIUM,
      message: 'Test error',
      retryable: true,
      retryCount: 1
    };

    handleError(error);

    expect(addBreadcrumb).toHaveBeenCalledWith(
      'Erro NETWORK: Test error',
      'error',
      expect.objectContaining({
        type: ErrorType.NETWORK,
        severity: ErrorSeverity.MEDIUM,
        retryable: true,
        retryCount: 1
      })
    );
  });

  it('deve adicionar breadcrumbs de retry', async () => {
    const { addBreadcrumb } = require('../../../app/utils/error-tracking');
    const mockFn = vi.fn()
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValue('success');

    await executeWithRetry(mockFn);

    expect(addBreadcrumb).toHaveBeenCalledWith(
      'Retry 1/3',
      'retry',
      expect.objectContaining({
        error: 'Network error',
        retryCount: 0
      })
    );
  });
}); 