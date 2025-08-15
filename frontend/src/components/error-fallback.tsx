/**
 * Error Fallback Components
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por fornecer componentes de fallback para diferentes cenários de erro
 * Inclui fallbacks para network, auth, server e erros genéricos
 */

import React from 'react';

// Interface para props dos componentes de fallback
export interface ErrorFallbackProps {
  error?: Error;
  errorId?: string;
  onRetry?: () => void;
  onReport?: () => void;
  onGoHome?: () => void;
  onGoBack?: () => void;
  customMessage?: string;
  showDetails?: boolean;
}

// Componente base para fallbacks
const BaseFallback: React.FC<ErrorFallbackProps & { 
  title: string; 
  message: string; 
  icon: string;
  actions?: React.ReactNode;
}> = ({ 
  title, 
  message, 
  icon, 
  actions, 
  errorId, 
  error, 
  showDetails = false 
}) => {
  return (
    <div className="error-fallback">
      <div className="error-fallback-content">
        <div className="error-fallback-icon">
          <span role="img" aria-label="error">{icon}</span>
        </div>
        
        <h2 className="error-fallback-title">{title}</h2>
        <p className="error-fallback-message">{message}</p>
        
        {errorId && (
          <div className="error-fallback-id">
            ID do Erro: {errorId}
          </div>
        )}
        
        {actions && (
          <div className="error-fallback-actions">
            {actions}
          </div>
        )}
        
        {showDetails && error && process.env.NODE_ENV === 'development' && (
          <details className="error-fallback-details">
            <summary>Detalhes do Erro (Desenvolvimento)</summary>
            <pre className="error-fallback-stack">
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};

// Fallback para erros de rede
export const NetworkErrorFallback: React.FC<ErrorFallbackProps> = ({
  onRetry,
  onGoBack,
  errorId
}) => {
  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  };

  const handleGoBack = () => {
    if (onGoBack) {
      onGoBack();
    } else {
      window.history.back();
    }
  };

  return (
    <BaseFallback
      title="Problema de Conexão"
      message="Não foi possível conectar ao servidor. Verifique sua conexão com a internet e tente novamente."
      icon="📡"
      errorId={errorId}
      actions={
        <div className="error-fallback-buttons">
          <button 
            onClick={handleRetry}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            Tentar Novamente
          </button>
          <button 
            onClick={handleGoBack}
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            Voltar
          </button>
        </div>
      }
    />
  );
};

// Fallback para erros de autenticação
export const AuthErrorFallback: React.FC<ErrorFallbackProps> = ({
  onRetry,
  onGoHome,
  errorId
}) => {
  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      // Tentar refresh do token
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      window.location.href = '/';
    }
  };

  return (
    <BaseFallback
      title="Sessão Expirada"
      message="Sua sessão expirou. Faça login novamente para continuar."
      icon="🔐"
      errorId={errorId}
      actions={
        <div className="error-fallback-buttons">
          <button 
            onClick={handleRetry}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            Fazer Login
          </button>
          <button 
            onClick={handleGoHome}
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            Ir para Home
          </button>
        </div>
      }
    />
  );
};

// Fallback para erros de autorização
export const AuthorizationErrorFallback: React.FC<ErrorFallbackProps> = ({
  onGoHome,
  onGoBack,
  errorId
}) => {
  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      window.location.href = '/';
    }
  };

  const handleGoBack = () => {
    if (onGoBack) {
      onGoBack();
    } else {
      window.history.back();
    }
  };

  return (
    <BaseFallback
      title="Acesso Negado"
      message="Você não tem permissão para acessar este recurso. Entre em contato com o administrador se acredita que isso é um erro."
      icon="🚫"
      errorId={errorId}
      actions={
        <div className="error-fallback-buttons">
          <button 
            onClick={handleGoHome}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            Ir para Home
          </button>
          <button 
            onClick={handleGoBack}
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            Voltar
          </button>
        </div>
      }
    />
  );
};

// Fallback para erros do servidor
export const ServerErrorFallback: React.FC<ErrorFallbackProps> = ({
  onRetry,
  onReport,
  errorId,
  error
}) => {
  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  };

  const handleReport = () => {
    if (onReport) {
      onReport();
    } else {
      // Abrir modal de report ou enviar para suporte
      window.open('mailto:support@example.com?subject=Erro do Servidor', '_blank');
    }
  };

  return (
    <BaseFallback
      title="Erro do Servidor"
      message="Ocorreu um erro interno no servidor. Nossa equipe foi notificada e está trabalhando para resolver o problema."
      icon="🛠️"
      errorId={errorId}
      error={error}
      showDetails={true}
      actions={
        <div className="error-fallback-buttons">
          <button 
            onClick={handleRetry}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            Tentar Novamente
          </button>
          <button 
            onClick={handleReport}
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            Reportar Erro
          </button>
        </div>
      }
    />
  );
};

// Fallback para erros de validação
export const ValidationErrorFallback: React.FC<ErrorFallbackProps> = ({
  onRetry,
  onGoBack,
  errorId,
  customMessage
}) => {
  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.history.back();
    }
  };

  const handleGoBack = () => {
    if (onGoBack) {
      onGoBack();
    } else {
      window.history.back();
    }
  };

  return (
    <BaseFallback
      title="Dados Inválidos"
      message={customMessage || "Os dados fornecidos são inválidos. Verifique as informações e tente novamente."}
      icon="⚠️"
      errorId={errorId}
      actions={
        <div className="error-fallback-buttons">
          <button 
            onClick={handleRetry}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            Corrigir Dados
          </button>
          <button 
            onClick={handleGoBack}
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            Voltar
          </button>
        </div>
      }
    />
  );
};

// Fallback genérico para erros desconhecidos
export const GenericErrorFallback: React.FC<ErrorFallbackProps> = ({
  onRetry,
  onReport,
  onGoHome,
  errorId,
  error,
  customMessage
}) => {
  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  };

  const handleReport = () => {
    if (onReport) {
      onReport();
    } else {
      // Abrir modal de report
      window.open('mailto:support@example.com?subject=Erro Genérico', '_blank');
    }
  };

  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      window.location.href = '/';
    }
  };

  return (
    <BaseFallback
      title="Algo deu errado"
      message={customMessage || "Ocorreu um erro inesperado. Nossa equipe foi notificada."}
      icon="❌"
      errorId={errorId}
      error={error}
      showDetails={true}
      actions={
        <div className="error-fallback-buttons">
          <button 
            onClick={handleRetry}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            Tentar Novamente
          </button>
          <button 
            onClick={handleReport}
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            Reportar Erro
          </button>
          <button 
            onClick={handleGoHome}
            className="error-fallback-btn error-fallback-btn-tertiary"
          >
            Ir para Home
          </button>
        </div>
      }
    />
  );
};

// Fallback para erros de carregamento
export const LoadingErrorFallback: React.FC<ErrorFallbackProps> = ({
  onRetry,
  onGoBack,
  errorId
}) => {
  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  };

  const handleGoBack = () => {
    if (onGoBack) {
      onGoBack();
    } else {
      window.history.back();
    }
  };

  return (
    <BaseFallback
      title="Falha no Carregamento"
      message="Não foi possível carregar o conteúdo. Tente novamente ou volte para a página anterior."
      icon="📂"
      errorId={errorId}
      actions={
        <div className="error-fallback-buttons">
          <button 
            onClick={handleRetry}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            Tentar Novamente
          </button>
          <button 
            onClick={handleGoBack}
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            Voltar
          </button>
        </div>
      }
    />
  );
};

// Hook para selecionar fallback baseado no tipo de erro
export const useErrorFallback = (error?: Error) => {
  const getFallbackComponent = (): React.ComponentType<ErrorFallbackProps> => {
    if (!error) {
      return GenericErrorFallback;
    }

    const message = error.message.toLowerCase();
    const name = error.name.toLowerCase();

    if (name.includes('network') || message.includes('fetch') || message.includes('network')) {
      return NetworkErrorFallback;
    }

    if (name.includes('auth') || message.includes('unauthorized') || message.includes('401')) {
      return AuthErrorFallback;
    }

    if (message.includes('forbidden') || message.includes('403')) {
      return AuthorizationErrorFallback;
    }

    if (message.includes('validation') || message.includes('invalid')) {
      return ValidationErrorFallback;
    }

    if (message.includes('server') || message.includes('500')) {
      return ServerErrorFallback;
    }

    if (message.includes('loading') || message.includes('load')) {
      return LoadingErrorFallback;
    }

    return GenericErrorFallback;
  };

  return {
    FallbackComponent: getFallbackComponent(),
    errorType: error ? getErrorType(error) : 'UNKNOWN'
  };
};

// Utilitário para determinar tipo de erro
const getErrorType = (error: Error): string => {
  const message = error.message.toLowerCase();
  const name = error.name.toLowerCase();

  if (name.includes('network') || message.includes('fetch') || message.includes('network')) {
    return 'NETWORK';
  }

  if (name.includes('auth') || message.includes('unauthorized') || message.includes('401')) {
    return 'AUTHENTICATION';
  }

  if (message.includes('forbidden') || message.includes('403')) {
    return 'AUTHORIZATION';
  }

  if (message.includes('validation') || message.includes('invalid')) {
    return 'VALIDATION';
  }

  if (message.includes('server') || message.includes('500')) {
    return 'SERVER';
  }

  if (message.includes('loading') || message.includes('load')) {
    return 'LOADING';
  }

  return 'UNKNOWN';
};

// Componente principal que seleciona o fallback apropriado
export const ErrorFallback: React.FC<ErrorFallbackProps> = (props) => {
  const { FallbackComponent } = useErrorFallback(props.error);
  return <FallbackComponent {...props} />;
};

export default ErrorFallback; 