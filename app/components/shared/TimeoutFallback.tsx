/**
 * TimeoutFallback Component
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - FIXTYPE-002.3
 * Ruleset: enterprise_control_layer.yaml
 * Data/Hora: 2024-12-27 22:55:00 UTC
 * Tracing ID: TIMEOUT_FALLBACK_20241227_001
 */

import React from 'react';

interface TimeoutFallbackProps {
  operation?: string;
  timeoutDuration?: number;
  retryCount?: number;
  maxRetries?: number;
  onRetry?: () => void;
  onCancel?: () => void;
  showAdvancedOptions?: boolean;
}

export const TimeoutFallback: React.FC<TimeoutFallbackProps> = ({
  operation = 'operação',
  timeoutDuration = 30,
  retryCount = 0,
  maxRetries = 3,
  onRetry,
  onCancel,
  showAdvancedOptions = false
}) => {
  const [isRetrying, setIsRetrying] = React.useState(false);
  const [showDetails, setShowDetails] = React.useState(false);

  const handleRetry = async () => {
    if (retryCount >= maxRetries) {
      return;
    }

    setIsRetrying(true);
    
    try {
      if (onRetry) {
        await onRetry();
      }
    } catch (error) {
      console.error('Retry failed:', error);
    } finally {
      setIsRetrying(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  const getTimeoutMessage = () => {
    if (retryCount >= maxRetries) {
      return `A ${operation} falhou após ${maxRetries} tentativas.`;
    }
    
    return `A ${operation} demorou mais de ${timeoutDuration} segundos para responder.`;
  };

  const getRetryMessage = () => {
    if (retryCount >= maxRetries) {
      return 'Número máximo de tentativas atingido.';
    }
    
    return `Tentativa ${retryCount + 1} de ${maxRetries}`;
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 text-center bg-yellow-50 border border-yellow-200 rounded-lg">
      {/* Icon */}
      <div className="text-yellow-600 text-3xl mb-4">⏰</div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Tempo Limite Excedido
      </h3>

      {/* Message */}
      <p className="text-gray-600 mb-4 max-w-md">
        {getTimeoutMessage()}
      </p>

      {/* Retry Info */}
      <div className="mb-6">
        <p className="text-sm text-gray-500 mb-2">
          {getRetryMessage()}
        </p>
        
        {retryCount > 0 && (
          <div className="flex justify-center space-x-1">
            {Array.from({ length: maxRetries }, (_, i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full ${
                  i < retryCount ? 'bg-red-400' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3 w-full max-w-xs">
        {retryCount < maxRetries && (
          <button
            onClick={handleRetry}
            disabled={isRetrying}
            className="flex-1 flex items-center justify-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isRetrying ? (
              <>
                <span className="animate-spin mr-2">🔄</span>
                Tentando...
              </>
            ) : (
              <>
                <span className="mr-2">🔄</span>
                Tentar Novamente
              </>
            )}
          </button>
        )}

        <button
          onClick={handleCancel}
          className="flex-1 flex items-center justify-center bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <span className="mr-2">❌</span>
          Cancelar
        </button>
      </div>

      {/* Advanced Options */}
      {showAdvancedOptions && (
        <div className="mt-6 w-full">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            {showDetails ? 'Ocultar' : 'Mostrar'} opções avançadas
          </button>

          {showDetails && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg text-left">
              <h4 className="font-medium text-gray-900 mb-2">Opções Avançadas:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Verificar conexão com a internet</li>
                <li>• Limpar cache do navegador</li>
                <li>• Tentar em modo incógnito</li>
                <li>• Contatar suporte técnico</li>
              </ul>
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  <strong>Detalhes técnicos:</strong><br />
                  Timeout: {timeoutDuration}s<br />
                  Tentativas: {retryCount}/{maxRetries}<br />
                  Operação: {operation}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 text-xs text-gray-500">
        Se o problema persistir, entre em contato com o suporte.
      </div>
    </div>
  );
};

export default TimeoutFallback; 