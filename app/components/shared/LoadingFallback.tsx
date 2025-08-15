/**
 * LoadingFallback Component
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - FIXTYPE-002.2
 * Ruleset: enterprise_control_layer.yaml
 * Data/Hora: 2024-12-27 22:50:00 UTC
 * Tracing ID: LOADING_FALLBACK_20241227_001
 */

import React from 'react';

interface LoadingFallbackProps {
  type?: 'spinner' | 'skeleton' | 'dots' | 'pulse';
  size?: 'small' | 'medium' | 'large';
  message?: string;
  showProgress?: boolean;
  progress?: number;
  timeout?: number;
  onTimeout?: () => void;
}

export const LoadingFallback: React.FC<LoadingFallbackProps> = ({
  type = 'spinner',
  size = 'medium',
  message = 'Carregando...',
  showProgress = false,
  progress = 0,
  timeout,
  onTimeout
}) => {
  const [timeoutReached, setTimeoutReached] = React.useState(false);

  React.useEffect(() => {
    if (timeout && onTimeout) {
      const timer = setTimeout(() => {
        setTimeoutReached(true);
        onTimeout();
      }, timeout);

      return () => clearTimeout(timer);
    }
  }, [timeout, onTimeout]);

  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  const renderSpinner = () => (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 ${sizeClasses[size]}`} />
  );

  const renderDots = () => (
    <div className="flex space-x-1">
      <div className={`bg-blue-600 rounded-full animate-bounce ${sizeClasses.small}`} style={{ animationDelay: '0ms' }} />
      <div className={`bg-blue-600 rounded-full animate-bounce ${sizeClasses.small}`} style={{ animationDelay: '150ms' }} />
      <div className={`bg-blue-600 rounded-full animate-bounce ${sizeClasses.small}`} style={{ animationDelay: '300ms' }} />
    </div>
  );

  const renderPulse = () => (
    <div className={`bg-blue-600 rounded-full animate-pulse ${sizeClasses[size]}`} />
  );

  const renderSkeleton = () => (
    <div className="space-y-3">
      <div className="h-4 bg-gray-200 rounded animate-pulse" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-4/6" />
    </div>
  );

  const renderLoader = () => {
    switch (type) {
      case 'spinner':
        return renderSpinner();
      case 'dots':
        return renderDots();
      case 'pulse':
        return renderPulse();
      case 'skeleton':
        return renderSkeleton();
      default:
        return renderSpinner();
    }
  };

  if (timeoutReached) {
    return (
      <div className="flex flex-col items-center justify-center p-6 text-center">
        <div className="text-yellow-600 text-2xl mb-2">⏰</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Carregamento demorado
        </h3>
        <p className="text-gray-600 mb-4">
          Esta operação está demorando mais que o esperado.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-6 text-center">
      {/* Loader */}
      <div className="mb-4">
        {renderLoader()}
      </div>

      {/* Message */}
      <p className="text-gray-600 mb-2">{message}</p>

      {/* Progress Bar */}
      {showProgress && (
        <div className="w-full max-w-xs">
          <div className="bg-gray-200 rounded-full h-2 mb-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
          <p className="text-sm text-gray-500">{Math.round(progress)}%</p>
        </div>
      )}

      {/* Timeout Warning */}
      {timeout && !timeoutReached && (
        <p className="text-xs text-gray-400 mt-2">
          Aguarde, isso pode levar alguns segundos...
        </p>
      )}
    </div>
  );
};

export default LoadingFallback; 