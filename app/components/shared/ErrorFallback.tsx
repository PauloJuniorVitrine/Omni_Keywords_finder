/**
 * ErrorFallback Component
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - FIXTYPE-002.1
 * Ruleset: enterprise_control_layer.yaml
 * Data/Hora: 2024-12-27 22:45:00 UTC
 * Tracing ID: ERROR_FALLBACK_20241227_001
 */

import React from 'react';

interface ErrorFallbackProps {
  error?: Error;
  errorInfo?: React.ErrorInfo;
  resetErrorBoundary?: () => void;
  fallbackType?: 'page' | 'component' | 'modal';
  showDetails?: boolean;
  customMessage?: string;
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorInfo,
  resetErrorBoundary,
  fallbackType = 'component',
  showDetails = false,
  customMessage
}) => {
  const [showErrorDetails, setShowErrorDetails] = React.useState(showDetails);

  const handleRetry = () => {
    if (resetErrorBoundary) {
      resetErrorBoundary();
    } else {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleContactSupport = () => {
    // Implementar integração com sistema de suporte
    console.error('Error details for support:', { error, errorInfo });
    // TODO: Integrar com sistema de tickets ou chat
  };

  const getErrorMessage = () => {
    if (customMessage) return customMessage;
    
    if (error?.message) {
      // Mapear mensagens de erro comuns para mensagens amigáveis
      const errorMap: Record<string, string> = {
        'Network Error': 'Problema de conexão. Verifique sua internet.',
        'Failed to fetch': 'Erro ao carregar dados. Tente novamente.',
        'Unauthorized': 'Sessão expirada. Faça login novamente.',
        'Forbidden': 'Acesso negado. Verifique suas permissões.',
        'Not Found': 'Recurso não encontrado.',
        'Internal Server Error': 'Erro interno do servidor. Tente novamente.',
        'Bad Request': 'Dados inválidos. Verifique as informações.',
        'Timeout': 'Tempo limite excedido. Tente novamente.',
      };

      return errorMap[error.message] || 'Ocorreu um erro inesperado.';
    }

    return 'Algo deu errado. Tente novamente.';
  };

  const containerClasses = {
    page: 'min-h-screen flex items-center justify-center bg-gray-50 p-4',
    component: 'p-6 bg-white rounded-lg border border-red-200 shadow-sm',
    modal: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50'
  };

  const contentClasses = {
    page: 'max-w-md w-full bg-white rounded-lg shadow-lg p-6',
    component: 'w-full',
    modal: 'bg-white rounded-lg shadow-xl p-6 max-w-md w-full'
  };

  return (
    <div className={containerClasses[fallbackType]}>
      <div className={contentClasses[fallbackType]}>
        {/* Header */}
        <div className="flex items-center justify-center mb-4">
          <div className="bg-red-100 p-3 rounded-full">
            <span className="text-2xl text-red-600">⚠️</span>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-xl font-semibold text-gray-900 text-center mb-2">
          Ops! Algo deu errado
        </h2>

        {/* Message */}
        <p className="text-gray-600 text-center mb-6">
          {getErrorMessage()}
        </p>

        {/* Error Details (Collapsible) */}
        {error && (
          <div className="mb-6">
            <button
              onClick={() => setShowErrorDetails(!showErrorDetails)}
              className="flex items-center justify-center w-full text-sm text-gray-500 hover:text-gray-700 mb-2"
            >
              <span className="mr-1">❓</span>
              {showErrorDetails ? 'Ocultar detalhes' : 'Ver detalhes técnicos'}
            </button>
            
            {showErrorDetails && (
              <div className="bg-gray-50 p-3 rounded text-xs font-mono text-gray-700 overflow-auto max-h-32">
                <div className="mb-2">
                  <strong>Erro:</strong> {error.message}
                </div>
                {error.stack && (
                  <div>
                    <strong>Stack:</strong>
                    <pre className="whitespace-pre-wrap">{error.stack}</pre>
                  </div>
                )}
                {errorInfo?.componentStack && (
                  <div>
                    <strong>Component Stack:</strong>
                    <pre className="whitespace-pre-wrap">{errorInfo.componentStack}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col gap-3">
          <button
            onClick={handleRetry}
            className="flex items-center justify-center w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <span className="mr-2">🔄</span>
            Tentar Novamente
          </button>

          <div className="flex gap-2">
            <button
              onClick={handleGoHome}
              className="flex-1 flex items-center justify-center bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <span className="mr-2">🏠</span>
              Início
            </button>
            
            <button
              onClick={handleContactSupport}
              className="flex-1 flex items-center justify-center bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <span className="mr-2">❓</span>
              Suporte
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-4 text-center text-xs text-gray-500">
          ID: {error?.name || 'UNKNOWN'}-{Date.now()}
        </div>
      </div>
    </div>
  );
};

export default ErrorFallback; 