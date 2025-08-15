/**
 * Sistema de Rastreamento de Erros Frontend
 * Tracing ID: FIXTYPE-003
 * 
 * Integra Sentry com sistema de auditoria backend
 * Filtra dados sensíveis e configura por ambiente
 */

import * as Sentry from '@sentry/react';

// Tipos para configuração
interface ErrorTrackingConfig {
  dsn: string;
  environment: string;
  release: string;
  tracesSampleRate: number;
  integrations: any[];
  beforeSend: (event: any) => any | null;
}

interface ErrorContext {
  userId?: string;
  sessionId?: string;
  componentName?: string;
  action?: string;
  metadata?: Record<string, any>;
}

// Configuração por ambiente
const getErrorTrackingConfig = (): ErrorTrackingConfig => {
  const environment = process.env.NODE_ENV || 'development';
  
  return {
    dsn: process.env.REACT_APP_SENTRY_DSN || '',
    environment,
    release: process.env.REACT_APP_VERSION || '1.0.0',
    tracesSampleRate: environment === 'production' ? 0.1 : 1.0,
    integrations: [
      Sentry.browserTracingIntegration({
        tracingOrigins: ['localhost', 'omni-keywords-finder.com'],
      }),
    ],
    beforeSend: (event) => {
      // Filtrar dados sensíveis
      return filterSensitiveData(event);
    },
  };
};

// Filtro de dados sensíveis
const filterSensitiveData = (event: any): any | null => {
  const sensitiveFields = [
    'password',
    'token',
    'secret',
    'key',
    'authorization',
    'cookie',
    'session',
  ];

  const sensitivePatterns = [
    /password/i,
    /token/i,
    /secret/i,
    /key/i,
    /authorization/i,
    /cookie/i,
    /session/i,
  ];

  // Filtrar headers sensíveis
  if (event.request?.headers) {
    Object.keys(event.request.headers).forEach((key) => {
      if (sensitivePatterns.some(pattern => pattern.test(key))) {
        event.request.headers[key] = '[FILTERED]';
      }
    });
  }

  // Filtrar dados de contexto sensíveis
  if (event.contexts?.user) {
    delete event.contexts.user.ip_address;
  }

  // Filtrar breadcrumbs sensíveis
  if (event.breadcrumbs) {
    event.breadcrumbs = event.breadcrumbs.filter((crumb: any) => {
      return !sensitivePatterns.some(pattern => 
        pattern.test(crumb.message || '') || 
        pattern.test(crumb.data?.url || '')
      );
    });
  }

  return event;
};

// Classe principal de rastreamento de erros
class ErrorTracker {
  private static instance: ErrorTracker;
  private isInitialized = false;

  private constructor() {}

  static getInstance(): ErrorTracker {
    if (!ErrorTracker.instance) {
      ErrorTracker.instance = new ErrorTracker();
    }
    return ErrorTracker.instance;
  }

  /**
   * Inicializa o sistema de rastreamento
   */
  initialize(): void {
    if (this.isInitialized) {
      console.warn('[ErrorTracker] Já inicializado');
      return;
    }

    const config = getErrorTrackingConfig();
    
    if (!config.dsn) {
      console.warn('[ErrorTracker] DSN não configurado, rastreamento desabilitado');
      return;
    }

    try {
      Sentry.init(config);
      this.isInitialized = true;
      console.log('[ErrorTracker] Inicializado com sucesso');
    } catch (error) {
      console.error('[ErrorTracker] Erro na inicialização:', error);
    }
  }

  /**
   * Captura erro com contexto
   */
  captureError(error: Error, context?: ErrorContext): void {
    if (!this.isInitialized) {
      console.warn('[ErrorTracker] Não inicializado, erro não capturado:', error);
      return;
    }

    try {
      Sentry.withScope((scope) => {
        // Adicionar contexto
        if (context?.userId) {
          scope.setUser({ id: context.userId });
        }
        
        if (context?.componentName) {
          scope.setTag('component', context.componentName);
        }
        
        if (context?.action) {
          scope.setTag('action', context.action);
        }
        
        if (context?.metadata) {
          scope.setExtras(context.metadata);
        }

        // Capturar erro
        Sentry.captureException(error);
      });
    } catch (trackingError) {
      console.error('[ErrorTracker] Erro ao capturar erro:', trackingError);
    }
  }

  /**
   * Captura mensagem de erro
   */
  captureMessage(message: string, level: Sentry.SeverityLevel = 'error', context?: ErrorContext): void {
    if (!this.isInitialized) {
      console.warn('[ErrorTracker] Não inicializado, mensagem não capturada:', message);
      return;
    }

    try {
      Sentry.withScope((scope) => {
        // Adicionar contexto
        if (context?.userId) {
          scope.setUser({ id: context.userId });
        }
        
        if (context?.componentName) {
          scope.setTag('component', context.componentName);
        }
        
        if (context?.action) {
          scope.setTag('action', context.action);
        }
        
        if (context?.metadata) {
          scope.setExtras(context.metadata);
        }

        // Capturar mensagem
        Sentry.captureMessage(message, level);
      });
    } catch (trackingError) {
      console.error('[ErrorTracker] Erro ao capturar mensagem:', trackingError);
    }
  }

  /**
   * Adiciona breadcrumb para rastreamento
   */
  addBreadcrumb(message: string, category: string, data?: Record<string, any>): void {
    if (!this.isInitialized) {
      return;
    }

    try {
      Sentry.addBreadcrumb({
        message,
        category,
        data,
        level: 'info',
      });
    } catch (error) {
      console.error('[ErrorTracker] Erro ao adicionar breadcrumb:', error);
    }
  }

  /**
   * Define usuário atual
   */
  setUser(userId: string, email?: string, username?: string): void {
    if (!this.isInitialized) {
      return;
    }

    try {
      Sentry.setUser({
        id: userId,
        email,
        username,
      });
    } catch (error) {
      console.error('[ErrorTracker] Erro ao definir usuário:', error);
    }
  }

  /**
   * Limpa dados do usuário
   */
  clearUser(): void {
    if (!this.isInitialized) {
      return;
    }

    try {
      Sentry.setUser(null);
    } catch (error) {
      console.error('[ErrorTracker] Erro ao limpar usuário:', error);
    }
  }

  /**
   * Envia erro para auditoria backend
   */
  async sendToAudit(error: Error, context?: ErrorContext): Promise<void> {
    try {
      const auditData = {
        type: 'frontend_error',
        error: {
          name: error.name,
          message: error.message,
          stack: error.stack,
        },
        context: {
          userId: context?.userId,
          componentName: context?.componentName,
          action: context?.action,
          metadata: context?.metadata,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
        },
      };

      // Enviar para endpoint de auditoria
      await fetch('/api/auditoria/erro-frontend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(auditData),
      });
    } catch (auditError) {
      console.error('[ErrorTracker] Erro ao enviar para auditoria:', auditError);
    }
  }
}

// Instância singleton
export const errorTracker = ErrorTracker.getInstance();

// Hook React para captura automática de erros
export const ErrorBoundary = Sentry.ErrorBoundary;

// Função utilitária para captura rápida
export const captureError = (error: Error, context?: ErrorContext) => {
  errorTracker.captureError(error, context);
  errorTracker.sendToAudit(error, context);
};

// Função utilitária para captura de mensagens
export const captureMessage = (message: string, level?: Sentry.SeverityLevel, context?: ErrorContext) => {
  errorTracker.captureMessage(message, level, context);
};

// Função utilitária para breadcrumbs
export const addBreadcrumb = (message: string, category: string, data?: Record<string, any>) => {
  errorTracker.addBreadcrumb(message, category, data);
};

// Inicialização automática
if (typeof window !== 'undefined') {
  errorTracker.initialize();
}

export default errorTracker; 