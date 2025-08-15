/**
 * RetryHandler.tsx
 * 
 * Sistema de retry automático e resiliência para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 10.1
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { cn } from '../../utils/cn';

// Types
export interface RetryConfig {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  retryCondition?: (error: any) => boolean;
  onRetry?: (attempt: number, error: any) => void;
  onMaxAttemptsReached?: (error: any) => void;
}

export interface RetryHandlerProps {
  children: React.ReactNode;
  config?: Partial<RetryConfig>;
  className?: string;
  showRetryButton?: boolean;
  showAttempts?: boolean;
  showDelay?: boolean;
  onRetry?: () => Promise<any>;
  fallback?: React.ReactNode;
}

export interface RetryState {
  isRetrying: boolean;
  attempt: number;
  lastError: any;
  nextRetryDelay: number;
  maxAttemptsReached: boolean;
}

// Default configuration
const DEFAULT_CONFIG: RetryConfig = {
  maxAttempts: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffMultiplier: 2,
};

// Hook for retry logic
export const useRetry = (config: Partial<RetryConfig> = {}) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  const [state, setState] = useState<RetryState>({
    isRetrying: false,
    attempt: 0,
    lastError: null,
    nextRetryDelay: finalConfig.initialDelay,
    maxAttemptsReached: false,
  });

  const timeoutRef = useRef<NodeJS.Timeout>();

  const calculateNextDelay = useCallback((currentDelay: number) => {
    return Math.min(
      currentDelay * finalConfig.backoffMultiplier,
      finalConfig.maxDelay
    );
  }, [finalConfig]);

  const shouldRetry = useCallback((error: any) => {
    if (finalConfig.retryCondition) {
      return finalConfig.retryCondition(error);
    }
    
    // Default retry conditions
    if (error?.status >= 500) return true; // Server errors
    if (error?.code === 'NETWORK_ERROR') return true; // Network errors
    if (error?.message?.includes('timeout')) return true; // Timeout errors
    
    return false;
  }, [finalConfig]);

  const retry = useCallback(async (operation: () => Promise<any>) => {
    if (state.maxAttemptsReached) {
      return;
    }

    setState(prev => ({
      ...prev,
      isRetrying: true,
      attempt: prev.attempt + 1,
    }));

    try {
      const result = await operation();
      
      // Success - reset state
      setState({
        isRetrying: false,
        attempt: 0,
        lastError: null,
        nextRetryDelay: finalConfig.initialDelay,
        maxAttemptsReached: false,
      });

      return result;
    } catch (error) {
      const currentAttempt = state.attempt + 1;
      const nextDelay = calculateNextDelay(state.nextRetryDelay);
      
      if (currentAttempt >= finalConfig.maxAttempts || !shouldRetry(error)) {
        // Max attempts reached or shouldn't retry
        setState(prev => ({
          ...prev,
          isRetrying: false,
          lastError: error,
          maxAttemptsReached: true,
        }));
        
        finalConfig.onMaxAttemptsReached?.(error);
        throw error;
      }

      // Schedule next retry
      setState(prev => ({
        ...prev,
        isRetrying: true,
        lastError: error,
        nextRetryDelay: nextDelay,
      }));

      finalConfig.onRetry?.(currentAttempt, error);

      // Wait before next attempt
      await new Promise(resolve => {
        timeoutRef.current = setTimeout(resolve, state.nextRetryDelay);
      });

      // Recursive retry
      return retry(operation);
    }
  }, [state, finalConfig, shouldRetry, calculateNextDelay]);

  const reset = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    setState({
      isRetrying: false,
      attempt: 0,
      lastError: null,
      nextRetryDelay: finalConfig.initialDelay,
      maxAttemptsReached: false,
    });
  }, [finalConfig.initialDelay]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    ...state,
    retry,
    reset,
  };
};

// Retry Button Component
const RetryButton: React.FC<{
  onRetry: () => void;
  attempt: number;
  maxAttempts: number;
  delay?: number;
  disabled?: boolean;
  className?: string;
}> = ({ onRetry, attempt, maxAttempts, delay, disabled, className = '' }) => {
  const [countdown, setCountdown] = useState(delay ? Math.ceil(delay / 1000) : 0);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleClick = () => {
    if (!disabled && countdown === 0) {
      onRetry();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || countdown > 0}
      className={cn(
        'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
        'bg-blue-600 text-white hover:bg-blue-700',
        'disabled:bg-gray-400 disabled:cursor-not-allowed',
        'dark:bg-blue-500 dark:hover:bg-blue-600',
        className
      )}
    >
      {countdown > 0 ? (
        `Tentar novamente em ${countdown}s`
      ) : (
        `Tentar novamente (${attempt}/${maxAttempts})`
      )}
    </button>
  );
};

// Error Display Component
const ErrorDisplay: React.FC<{
  error: any;
  attempt: number;
  maxAttempts: number;
  className?: string;
}> = ({ error, attempt, maxAttempts, className = '' }) => {
  const getErrorMessage = (error: any) => {
    if (error?.message) return error.message;
    if (error?.status) return `Erro ${error.status}: ${error.statusText || 'Erro do servidor'}`;
    if (typeof error === 'string') return error;
    return 'Erro desconhecido';
  };

  const getErrorType = (error: any) => {
    if (error?.status >= 500) return 'Erro do Servidor';
    if (error?.status >= 400) return 'Erro do Cliente';
    if (error?.code === 'NETWORK_ERROR') return 'Erro de Rede';
    if (error?.message?.includes('timeout')) return 'Timeout';
    return 'Erro';
  };

  return (
    <div className={cn('p-4 border border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-700 rounded-lg', className)}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className="w-5 h-5 text-red-500 text-center">✗</div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
            {getErrorType(error)}
          </h3>
          <p className="mt-1 text-sm text-red-700 dark:text-red-300">
            {getErrorMessage(error)}
          </p>
          {attempt > 0 && (
            <p className="mt-2 text-xs text-red-600 dark:text-red-400">
              Tentativa {attempt} de {maxAttempts}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// Main Retry Handler Component
export const RetryHandler: React.FC<RetryHandlerProps> = ({
  children,
  config = {},
  className = '',
  showRetryButton = true,
  showAttempts = true,
  showDelay = true,
  onRetry,
  fallback,
}) => {
  const {
    isRetrying,
    attempt,
    lastError,
    nextRetryDelay,
    maxAttemptsReached,
    retry,
    reset,
  } = useRetry(config);

  const handleRetry = useCallback(async () => {
    if (onRetry) {
      try {
        await retry(onRetry);
      } catch (error) {
        // Error is handled by the retry hook
      }
    }
  }, [retry, onRetry]);

  // If no error, render children normally
  if (!lastError && !isRetrying) {
    return <div className={className}>{children}</div>;
  }

  // If max attempts reached, show fallback or error
  if (maxAttemptsReached) {
    if (fallback) {
      return <div className={className}>{fallback}</div>;
    }
    
    return (
      <div className={cn('space-y-4', className)}>
        <ErrorDisplay
          error={lastError}
          attempt={attempt}
          maxAttempts={config.maxAttempts || DEFAULT_CONFIG.maxAttempts}
        />
        {showRetryButton && (
          <div className="flex items-center space-x-3">
            <RetryButton
              onRetry={handleRetry}
              attempt={attempt}
              maxAttempts={config.maxAttempts || DEFAULT_CONFIG.maxAttempts}
              disabled={isRetrying}
            />
            <button
              onClick={reset}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              Resetar
            </button>
          </div>
        )}
      </div>
    );
  }

  // If retrying, show retry state
  return (
    <div className={cn('space-y-4', className)}>
      <ErrorDisplay
        error={lastError}
        attempt={attempt}
        maxAttempts={config.maxAttempts || DEFAULT_CONFIG.maxAttempts}
      />
      
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 text-blue-500 animate-spin text-center">⟳</div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Tentando novamente...
          </span>
        </div>
        
        {showAttempts && (
          <span className="text-sm text-gray-500 dark:text-gray-500">
            Tentativa {attempt} de {config.maxAttempts || DEFAULT_CONFIG.maxAttempts}
          </span>
        )}
        
        {showDelay && nextRetryDelay > 0 && (
          <span className="text-sm text-gray-500 dark:text-gray-500">
            Próxima tentativa em {Math.ceil(nextRetryDelay / 1000)}s
          </span>
        )}
      </div>
      
      {showRetryButton && (
        <RetryButton
          onRetry={handleRetry}
          attempt={attempt}
          maxAttempts={config.maxAttempts || DEFAULT_CONFIG.maxAttempts}
          delay={nextRetryDelay}
          disabled={isRetrying}
        />
      )}
    </div>
  );
};

// Higher-order component for easy wrapping
export const withRetry = <P extends object>(
  Component: React.ComponentType<P>,
  config?: Partial<RetryConfig>
) => {
  return React.forwardRef<any, P>((props, ref) => (
    <RetryHandler config={config}>
      <Component {...props} ref={ref} />
    </RetryHandler>
  ));
};

// Utility functions
export const createRetryConfig = (overrides: Partial<RetryConfig> = {}): RetryConfig => {
  return { ...DEFAULT_CONFIG, ...overrides };
};

export const isRetryableError = (error: any): boolean => {
  if (error?.status >= 500) return true;
  if (error?.code === 'NETWORK_ERROR') return true;
  if (error?.message?.includes('timeout')) return true;
  return false;
};

export default RetryHandler; 