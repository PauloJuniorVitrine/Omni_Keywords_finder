/**
 * Error Capture and Monitoring System
 * 
 * Tracing ID: ERROR_CAPTURE_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.6
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import React, { Component, ErrorInfo, ReactNode, useEffect, useState, useCallback } from 'react';

// Types for error monitoring
export interface ErrorEvent {
  id: string;
  type: 'javascript' | 'react' | 'network' | 'resource' | 'promise' | 'custom';
  message: string;
  stack?: string;
  componentStack?: string;
  timestamp: number;
  url: string;
  userAgent: string;
  userId?: string;
  sessionId?: string;
  metadata?: Record<string, any>;
  severity: 'low' | 'medium' | 'high' | 'critical';
  handled: boolean;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export interface ErrorReportingOptions {
  endpoint?: string;
  includeStack?: boolean;
  includeUserInfo?: boolean;
  includeMetadata?: boolean;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  retryAttempts?: number;
  retryDelay?: number;
}

// Error severity levels
export const ERROR_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
} as const;

// Error types
export const ERROR_TYPES = {
  JAVASCRIPT: 'javascript',
  REACT: 'react',
  NETWORK: 'network',
  RESOURCE: 'resource',
  PROMISE: 'promise',
  CUSTOM: 'custom'
} as const;

// Global error store
class ErrorStore {
  private static instance: ErrorStore;
  private errors: ErrorEvent[] = [];
  private maxErrors: number = 1000;
  private listeners: Set<(error: ErrorEvent) => void> = new Set();

  static getInstance(): ErrorStore {
    if (!ErrorStore.instance) {
      ErrorStore.instance = new ErrorStore();
    }
    return ErrorStore.instance;
  }

  addError(error: ErrorEvent): void {
    this.errors.push(error);
    
    // Keep only the latest errors
    if (this.errors.length > this.maxErrors) {
      this.errors = this.errors.slice(-this.maxErrors);
    }

    // Notify listeners
    this.listeners.forEach(listener => listener(error));
  }

  getErrors(): ErrorEvent[] {
    return [...this.errors];
  }

  getErrorsByType(type: string): ErrorEvent[] {
    return this.errors.filter(error => error.type === type);
  }

  getErrorsBySeverity(severity: string): ErrorEvent[] {
    return this.errors.filter(error => error.severity === severity);
  }

  getRecentErrors(limit: number = 10): ErrorEvent[] {
    return this.errors.slice(-limit);
  }

  clearErrors(): void {
    this.errors = [];
  }

  addListener(listener: (error: ErrorEvent) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  getErrorStats(): {
    total: number;
    byType: Record<string, number>;
    bySeverity: Record<string, number>;
    unhandled: number;
  } {
    const byType: Record<string, number> = {};
    const bySeverity: Record<string, number> = {};
    let unhandled = 0;

    this.errors.forEach(error => {
      byType[error.type] = (byType[error.type] || 0) + 1;
      bySeverity[error.severity] = (bySeverity[error.severity] || 0) + 1;
      if (!error.handled) unhandled++;
    });

    return {
      total: this.errors.length,
      byType,
      bySeverity,
      unhandled
    };
  }
}

// Error reporter
class ErrorReporter {
  private endpoint?: string;
  private retryAttempts: number;
  private retryDelay: number;
  private queue: ErrorEvent[] = [];
  private isProcessing = false;

  constructor(options: ErrorReportingOptions = {}) {
    this.endpoint = options.endpoint;
    this.retryAttempts = options.retryAttempts || 3;
    this.retryDelay = options.retryDelay || 1000;
  }

  async reportError(error: ErrorEvent): Promise<void> {
    if (!this.endpoint) {
      console.warn('No error reporting endpoint configured');
      return;
    }

    this.queue.push(error);
    await this.processQueue();
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) return;

    this.isProcessing = true;

    while (this.queue.length > 0) {
      const error = this.queue.shift()!;
      await this.sendError(error);
    }

    this.isProcessing = false;
  }

  private async sendError(error: ErrorEvent, attempt: number = 0): Promise<void> {
    try {
      const response = await fetch(this.endpoint!, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(error)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      if (attempt < this.retryAttempts) {
        await new Promise(resolve => setTimeout(resolve, this.retryDelay * Math.pow(2, attempt)));
        await this.sendError(error, attempt + 1);
      } else {
        console.error('Failed to report error after retries:', error, err);
      }
    }
  }
}

// Global instances
const errorStore = ErrorStore.getInstance();
let errorReporter: ErrorReporter | null = null;

// Error boundary component
export class ErrorBoundary extends Component<
  { 
    children: ReactNode;
    fallback?: ReactNode | ((error: Error, errorInfo: ErrorInfo) => ReactNode);
    onError?: (error: Error, errorInfo: ErrorInfo) => void;
    reportErrors?: boolean;
  },
  ErrorBoundaryState
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ error, errorInfo });

    // Report error
    if (this.props.reportErrors !== false) {
      const errorEvent: ErrorEvent = {
        id: generateErrorId(),
        type: ERROR_TYPES.REACT,
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: Date.now(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        severity: ERROR_SEVERITY.HIGH,
        handled: false
      };

      errorStore.addError(errorEvent);
      errorReporter?.reportError(errorEvent);
    }

    // Call custom error handler
    this.props.onError?.(error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (typeof this.props.fallback === 'function') {
        return this.props.fallback(this.state.error!, this.state.errorInfo!);
      }
      
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="error-boundary-fallback">
          <h2>Algo deu errado</h2>
          <p>Ocorreu um erro inesperado. Tente recarregar a página.</p>
          <button onClick={() => window.location.reload()}>
            Recarregar Página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook for error monitoring
export const useErrorMonitoring = () => {
  const [errors, setErrors] = useState<ErrorEvent[]>([]);
  const [stats, setStats] = useState(errorStore.getErrorStats());

  useEffect(() => {
    const unsubscribe = errorStore.addListener((error) => {
      setErrors(prev => [...prev, error]);
      setStats(errorStore.getErrorStats());
    });

    return unsubscribe;
  }, []);

  const reportError = useCallback((
    error: Error | string,
    metadata?: Record<string, any>,
    severity: 'low' | 'medium' | 'high' | 'critical' = ERROR_SEVERITY.MEDIUM
  ) => {
    const errorEvent: ErrorEvent = {
      id: generateErrorId(),
      type: ERROR_TYPES.CUSTOM,
      message: typeof error === 'string' ? error : error.message,
      stack: error instanceof Error ? error.stack : undefined,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      severity,
      handled: true,
      metadata
    };

    errorStore.addError(errorEvent);
    errorReporter?.reportError(errorEvent);
  }, []);

  const clearErrors = useCallback(() => {
    errorStore.clearErrors();
    setErrors([]);
    setStats(errorStore.getErrorStats());
  }, []);

  return {
    errors,
    stats,
    reportError,
    clearErrors
  };
};

// Hook for component error handling
export const useComponentError = (componentName: string) => {
  const { reportError } = useErrorMonitoring();

  const handleError = useCallback((
    error: Error | string,
    metadata?: Record<string, any>
  ) => {
    reportError(error, { component: componentName, ...metadata });
  }, [componentName, reportError]);

  return { handleError };
};

// Global error handlers
export const setupGlobalErrorHandlers = (options: ErrorReportingOptions = {}) => {
  // Initialize error reporter
  errorReporter = new ErrorReporter(options);

  // JavaScript errors
  window.addEventListener('error', (event) => {
    const errorEvent: ErrorEvent = {
      id: generateErrorId(),
      type: ERROR_TYPES.JAVASCRIPT,
      message: event.message,
      stack: event.error?.stack,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      severity: ERROR_SEVERITY.MEDIUM,
      handled: false,
      metadata: {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }
    };

    errorStore.addError(errorEvent);
    errorReporter?.reportError(errorEvent);
  });

  // Unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    const errorEvent: ErrorEvent = {
      id: generateErrorId(),
      type: ERROR_TYPES.PROMISE,
      message: event.reason?.message || 'Unhandled Promise Rejection',
      stack: event.reason?.stack,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      severity: ERROR_SEVERITY.HIGH,
      handled: false,
      metadata: {
        reason: event.reason
      }
    };

    errorStore.addError(errorEvent);
    errorReporter?.reportError(errorEvent);
  });

  // Network errors
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    try {
      const response = await originalFetch(...args);
      
      if (!response.ok) {
        const errorEvent: ErrorEvent = {
          id: generateErrorId(),
          type: ERROR_TYPES.NETWORK,
          message: `HTTP ${response.status}: ${response.statusText}`,
          timestamp: Date.now(),
          url: window.location.href,
          userAgent: navigator.userAgent,
          severity: ERROR_SEVERITY.MEDIUM,
          handled: true,
          metadata: {
            url: args[0],
            status: response.status,
            statusText: response.statusText
          }
        };

        errorStore.addError(errorEvent);
        errorReporter?.reportError(errorEvent);
      }
      
      return response;
    } catch (error) {
      const errorEvent: ErrorEvent = {
        id: generateErrorId(),
        type: ERROR_TYPES.NETWORK,
        message: error instanceof Error ? error.message : 'Network Error',
        stack: error instanceof Error ? error.stack : undefined,
        timestamp: Date.now(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        severity: ERROR_SEVERITY.MEDIUM,
        handled: true,
        metadata: {
          url: args[0],
          error
        }
      };

      errorStore.addError(errorEvent);
      errorReporter?.reportError(errorEvent);
      throw error;
    }
  };
};

// Utility functions
export const generateErrorId = (): string => {
  return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const getErrorStore = (): ErrorStore => {
  return errorStore;
};

export const getErrorReporter = (): ErrorReporter | null => {
  return errorReporter;
};

export const setErrorReporter = (reporter: ErrorReporter): void => {
  errorReporter = reporter;
};

// Error severity calculator
export const calculateErrorSeverity = (
  error: Error | string,
  context?: Record<string, any>
): 'low' | 'medium' | 'high' | 'critical' => {
  const message = typeof error === 'string' ? error : error.message;
  
  // Critical errors
  if (message.includes('Out of memory') || message.includes('Maximum call stack size exceeded')) {
    return ERROR_SEVERITY.CRITICAL;
  }
  
  // High severity errors
  if (message.includes('NetworkError') || message.includes('Failed to fetch')) {
    return ERROR_SEVERITY.HIGH;
  }
  
  // Medium severity errors
  if (message.includes('TypeError') || message.includes('ReferenceError')) {
    return ERROR_SEVERITY.MEDIUM;
  }
  
  // Low severity errors
  return ERROR_SEVERITY.LOW;
};

// Error grouping utility
export const groupErrors = (errors: ErrorEvent[]): Record<string, ErrorEvent[]> => {
  const groups: Record<string, ErrorEvent[]> = {};
  
  errors.forEach(error => {
    const key = `${error.type}_${error.message}`;
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(error);
  });
  
  return groups;
};

export default {
  ErrorBoundary,
  useErrorMonitoring,
  useComponentError,
  setupGlobalErrorHandlers,
  generateErrorId,
  getErrorStore,
  getErrorReporter,
  setErrorReporter,
  calculateErrorSeverity,
  groupErrors,
  ERROR_SEVERITY,
  ERROR_TYPES
}; 