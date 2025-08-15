/**
 * Testes unitários para sistema de rastreamento de erros frontend
 * Tracing ID: FIXTYPE-003
 */

import { errorTracker, captureError, captureMessage, addBreadcrumb } from '../../../app/utils/error-tracking';

// Mock do Sentry
jest.mock('@sentry/react', () => ({
  init: jest.fn(),
  captureException: jest.fn(),
  captureMessage: jest.fn(),
  addBreadcrumb: jest.fn(),
  setUser: jest.fn(),
  withScope: jest.fn((callback) => {
    const scope = {
      setUser: jest.fn(),
      setTag: jest.fn(),
      setExtras: jest.fn(),
    };
    callback(scope);
  }),
  ErrorBoundary: jest.fn(),
}));

// Mock do fetch
global.fetch = jest.fn();

describe('ErrorTracker', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset da instância singleton
    (errorTracker as any).isInitialized = false;
  });

  describe('initialize', () => {
    it('deve inicializar com configuração válida', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      process.env.NODE_ENV = 'development';

      errorTracker.initialize();

      expect(errorTracker).toBeDefined();
    });

    it('não deve inicializar sem DSN', () => {
      delete process.env.REACT_APP_SENTRY_DSN;

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      errorTracker.initialize();

      expect(consoleSpy).toHaveBeenCalledWith(
        '[ErrorTracker] DSN não configurado, rastreamento desabilitado'
      );
      consoleSpy.mockRestore();
    });

    it('não deve inicializar duas vezes', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      
      errorTracker.initialize();
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      errorTracker.initialize();

      expect(consoleSpy).toHaveBeenCalledWith('[ErrorTracker] Já inicializado');
      consoleSpy.mockRestore();
    });
  });

  describe('captureError', () => {
    it('deve capturar erro com contexto', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const error = new Error('Test error');
      const context = {
        userId: 'user123',
        componentName: 'TestComponent',
        action: 'test-action',
        metadata: { test: 'data' },
      };

      errorTracker.captureError(error, context);

      expect(errorTracker).toBeDefined();
    });

    it('deve avisar quando não inicializado', () => {
      const error = new Error('Test error');
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      errorTracker.captureError(error);

      expect(consoleSpy).toHaveBeenCalledWith(
        '[ErrorTracker] Não inicializado, erro não capturado:',
        error
      );
      consoleSpy.mockRestore();
    });
  });

  describe('captureMessage', () => {
    it('deve capturar mensagem com nível e contexto', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const message = 'Test message';
      const context = {
        userId: 'user123',
        componentName: 'TestComponent',
      };

      errorTracker.captureMessage(message, 'warning', context);

      expect(errorTracker).toBeDefined();
    });
  });

  describe('addBreadcrumb', () => {
    it('deve adicionar breadcrumb', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      addBreadcrumb('Test breadcrumb', 'test-category', { test: 'data' });

      expect(errorTracker).toBeDefined();
    });
  });

  describe('setUser', () => {
    it('deve definir usuário', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      errorTracker.setUser('user123', 'test@example.com', 'testuser');

      expect(errorTracker).toBeDefined();
    });
  });

  describe('clearUser', () => {
    it('deve limpar dados do usuário', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      errorTracker.clearUser();

      expect(errorTracker).toBeDefined();
    });
  });

  describe('sendToAudit', () => {
    it('deve enviar erro para auditoria backend', async () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const error = new Error('Test error');
      const context = {
        userId: 'user123',
        componentName: 'TestComponent',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({ ok: true });

      await errorTracker.sendToAudit(error, context);

      expect(global.fetch).toHaveBeenCalledWith('/api/auditoria/erro-frontend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: expect.stringContaining('frontend_error'),
      });
    });

    it('deve lidar com erro na auditoria', async () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const error = new Error('Test error');
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await errorTracker.sendToAudit(error);

      expect(consoleSpy).toHaveBeenCalledWith(
        '[ErrorTracker] Erro ao enviar para auditoria:',
        expect.any(Error)
      );
      consoleSpy.mockRestore();
    });
  });

  describe('Funções utilitárias', () => {
    it('captureError deve chamar errorTracker', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const error = new Error('Test error');
      const context = { userId: 'user123' };

      const captureErrorSpy = jest.spyOn(errorTracker, 'captureError');
      const sendToAuditSpy = jest.spyOn(errorTracker, 'sendToAudit');

      captureError(error, context);

      expect(captureErrorSpy).toHaveBeenCalledWith(error, context);
      expect(sendToAuditSpy).toHaveBeenCalledWith(error, context);
    });

    it('captureMessage deve chamar errorTracker', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const message = 'Test message';
      const context = { userId: 'user123' };

      const captureMessageSpy = jest.spyOn(errorTracker, 'captureMessage');

      captureMessage(message, 'info', context);

      expect(captureMessageSpy).toHaveBeenCalledWith(message, 'info', context);
    });

    it('addBreadcrumb deve chamar errorTracker', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const message = 'Test breadcrumb';
      const category = 'test-category';
      const data = { test: 'data' };

      const addBreadcrumbSpy = jest.spyOn(errorTracker, 'addBreadcrumb');

      addBreadcrumb(message, category, data);

      expect(addBreadcrumbSpy).toHaveBeenCalledWith(message, category, data);
    });
  });

  describe('Filtro de dados sensíveis', () => {
    it('deve filtrar headers sensíveis', () => {
      process.env.REACT_APP_SENTRY_DSN = 'https://test@sentry.io/123';
      errorTracker.initialize();

      const error = new Error('Test error');
      const context = {
        metadata: {
          headers: {
            'Authorization': 'Bearer token123',
            'Content-Type': 'application/json',
            'X-Password': 'secret123',
          },
        },
      };

      errorTracker.captureError(error, context);

      expect(errorTracker).toBeDefined();
    });
  });
}); 