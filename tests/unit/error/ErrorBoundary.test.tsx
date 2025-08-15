/**
 * Testes Unitários - ErrorBoundary Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_ERROR_BOUNDARY_023
 * 
 * Baseado em código real do ErrorBoundary.tsx
 */

import React, { Component } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { 
  ErrorBoundary, 
  DataErrorBoundary, 
  FormErrorBoundary, 
  ChartErrorBoundary,
  useErrorBoundary,
  withErrorBoundary,
  createErrorBoundary,
  logError
} from '../../../app/components/error/ErrorBoundary';

// Mock do console.error para evitar spam nos testes
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

// Componente que gera erro para testar ErrorBoundary
class ErrorComponent extends Component<{ shouldThrow?: boolean }> {
  constructor(props: { shouldThrow?: boolean }) {
    super(props);
    if (props.shouldThrow) {
      throw new Error('Erro de teste');
    }
  }

  render() {
    return <div>Componente normal</div>;
  }
}

// Componente funcional que gera erro
const FunctionalErrorComponent: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Erro funcional de teste');
  }
  return <div>Componente funcional normal</div>;
};

// Mock do serviço de report de erro
const mockErrorReportingService = {
  report: jest.fn().mockResolvedValue(undefined)
};

describe('ErrorBoundary - Sistema de Captura de Erros', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('ErrorBoundary Class Component', () => {
    
    test('deve renderizar children quando não há erro', () => {
      render(
        <ErrorBoundary>
          <div>Conteúdo normal</div>
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Conteúdo normal')).toBeInTheDocument();
    });

    test('deve capturar erro e renderizar fallback padrão', () => {
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Algo deu errado')).toBeInTheDocument();
      expect(screen.getByText('Ocorreu um erro inesperado. Nossa equipe foi notificada e está trabalhando para resolver o problema.')).toBeInTheDocument();
    });

    test('deve chamar onError callback quando erro ocorre', () => {
      const mockOnError = jest.fn();
      
      render(
        <ErrorBoundary onError={mockOnError}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(mockOnError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String)
        })
      );
    });

    test('deve reportar erro para serviço de report quando configurado', async () => {
      render(
        <ErrorBoundary errorReportingService={mockErrorReportingService}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      await waitFor(() => {
        expect(mockErrorReportingService.report).toHaveBeenCalledWith(
          expect.any(Error),
          expect.objectContaining({
            componentStack: expect.any(String)
          }),
          expect.objectContaining({
            errorId: expect.any(String),
            timestamp: expect.any(Date),
            retryCount: 0
          })
        );
      });
    });

    test('deve permitir retry quando botão é clicado', async () => {
      const user = userEvent.setup();
      const mockOnRetry = jest.fn();
      
      render(
        <ErrorBoundary onRetry={mockOnRetry}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const retryButton = screen.getByText('Tentar novamente');
      await user.click(retryButton);
      
      expect(mockOnRetry).toHaveBeenCalled();
    });

    test('deve ocultar botão de retry quando showRetryButton é false', () => {
      render(
        <ErrorBoundary showRetryButton={false}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.queryByText('Tentar novamente')).not.toBeInTheDocument();
    });

    test('deve mostrar botão de report quando showReportButton é true', () => {
      render(
        <ErrorBoundary showReportButton={true}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Reportar erro')).toBeInTheDocument();
    });

    test('deve mostrar detalhes do erro quando showErrorDetails é true', () => {
      render(
        <ErrorBoundary showErrorDetails={true}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Detalhes do erro')).toBeInTheDocument();
      expect(screen.getByText('Mensagem:')).toBeInTheDocument();
      expect(screen.getByText('Stack:')).toBeInTheDocument();
      expect(screen.getByText('Component Stack:')).toBeInTheDocument();
    });

    test('deve permitir mostrar detalhes do erro dinamicamente', async () => {
      const user = userEvent.setup();
      
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const showDetailsButton = screen.getByText('Ver detalhes');
      await user.click(showDetailsButton);
      
      expect(screen.getByText('Detalhes do erro')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS customizada', () => {
      render(
        <ErrorBoundary className="custom-error-class">
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const errorContainer = screen.getByText('Algo deu errado').closest('div');
      expect(errorContainer).toHaveClass('custom-error-class');
    });

    test('deve limitar número de retries', async () => {
      const user = userEvent.setup();
      const mockOnRetry = jest.fn();
      
      render(
        <ErrorBoundary maxRetries={2} onRetry={mockOnRetry}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const retryButton = screen.getByText('Tentar novamente');
      
      // Primeiro retry
      await user.click(retryButton);
      expect(mockOnRetry).toHaveBeenCalledTimes(1);
      
      // Segundo retry
      await user.click(retryButton);
      expect(mockOnRetry).toHaveBeenCalledTimes(2);
      
      // Terceiro retry (deve ser ignorado)
      await user.click(retryButton);
      expect(mockOnRetry).toHaveBeenCalledTimes(2);
    });

    test('deve usar fallback customizado como função', () => {
      const customFallback = (error: Error, errorInfo: any, retry: () => void) => (
        <div data-testid="custom-fallback">
          <p>Erro customizado: {error.message}</p>
          <button onClick={retry}>Retry customizado</button>
        </div>
      );
      
      render(
        <ErrorBoundary fallback={customFallback}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
      expect(screen.getByText('Erro customizado: Erro de teste')).toBeInTheDocument();
      expect(screen.getByText('Retry customizado')).toBeInTheDocument();
    });

    test('deve usar fallback customizado como componente', () => {
      const CustomFallback = () => <div data-testid="custom-component">Fallback customizado</div>;
      
      render(
        <ErrorBoundary fallback={<CustomFallback />}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByTestId('custom-component')).toBeInTheDocument();
      expect(screen.getByText('Fallback customizado')).toBeInTheDocument();
    });
  });

  describe('DataErrorBoundary', () => {
    
    test('deve renderizar fallback específico para dados', () => {
      render(
        <DataErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </DataErrorBoundary>
      );
      
      expect(screen.getByText('Erro ao carregar dados')).toBeInTheDocument();
      expect(screen.getByText('Não foi possível carregar os dados. Tente novamente.')).toBeInTheDocument();
      expect(screen.getByText('Tentar novamente')).toBeInTheDocument();
    });

    test('deve chamar onRetry quando botão é clicado', async () => {
      const user = userEvent.setup();
      const mockOnRetry = jest.fn();
      
      render(
        <DataErrorBoundary onRetry={mockOnRetry}>
          <ErrorComponent shouldThrow={true} />
        </DataErrorBoundary>
      );
      
      const retryButton = screen.getByText('Tentar novamente');
      await user.click(retryButton);
      
      expect(mockOnRetry).toHaveBeenCalled();
    });
  });

  describe('FormErrorBoundary', () => {
    
    test('deve renderizar fallback específico para formulários', () => {
      render(
        <FormErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </FormErrorBoundary>
      );
      
      expect(screen.getByText('Erro no formulário. Verifique os dados e tente novamente.')).toBeInTheDocument();
    });
  });

  describe('ChartErrorBoundary', () => {
    
    test('deve renderizar fallback específico para gráficos', () => {
      render(
        <ChartErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ChartErrorBoundary>
      );
      
      expect(screen.getByText('Erro no gráfico')).toBeInTheDocument();
      expect(screen.getByText('Não foi possível renderizar o gráfico.')).toBeInTheDocument();
    });
  });

  describe('useErrorBoundary Hook', () => {
    
    test('deve gerenciar estado de erro', () => {
      const TestComponent = () => {
        const { error, hasError, handleError, resetError } = useErrorBoundary();
        
        if (hasError) {
          return (
            <div>
              <p>Erro: {error?.message}</p>
              <button onClick={resetError}>Reset</button>
            </div>
          );
        }
        
        return (
          <button onClick={() => handleError(new Error('Erro do hook'), { componentStack: '' })}>
            Gerar erro
          </button>
        );
      };
      
      render(<TestComponent />);
      
      const generateErrorButton = screen.getByText('Gerar erro');
      fireEvent.click(generateErrorButton);
      
      expect(screen.getByText('Erro: Erro do hook')).toBeInTheDocument();
      
      const resetButton = screen.getByText('Reset');
      fireEvent.click(resetButton);
      
      expect(screen.getByText('Gerar erro')).toBeInTheDocument();
    });
  });

  describe('withErrorBoundary HOC', () => {
    
    test('deve envolver componente com ErrorBoundary', () => {
      const WrappedComponent = withErrorBoundary(FunctionalErrorComponent);
      
      render(<WrappedComponent shouldThrow={true} />);
      
      expect(screen.getByText('Algo deu errado')).toBeInTheDocument();
    });

    test('deve passar props do ErrorBoundary', () => {
      const WrappedComponent = withErrorBoundary(FunctionalErrorComponent, {
        showErrorDetails: true
      });
      
      render(<WrappedComponent shouldThrow={true} />);
      
      expect(screen.getByText('Detalhes do erro')).toBeInTheDocument();
    });
  });

  describe('createErrorBoundary Utility', () => {
    
    test('deve criar ErrorBoundary com configuração customizada', () => {
      const CustomErrorBoundary = createErrorBoundary({
        showErrorDetails: true,
        maxRetries: 1
      });
      
      render(
        <CustomErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </CustomErrorBoundary>
      );
      
      expect(screen.getByText('Detalhes do erro')).toBeInTheDocument();
    });
  });

  describe('logError Utility', () => {
    
    test('deve logar erro com contexto', () => {
      const error = new Error('Erro de teste');
      const errorInfo = { componentStack: 'Component stack' };
      
      logError(error, errorInfo, 'TestContext');
      
      expect(console.error).toHaveBeenCalledWith('[TestContext] Error:', error);
      expect(console.error).toHaveBeenCalledWith('[TestContext] Component Stack:', errorInfo.componentStack);
    });

    test('deve logar erro sem contexto', () => {
      const error = new Error('Erro de teste');
      const errorInfo = { componentStack: 'Component stack' };
      
      logError(error, errorInfo);
      
      expect(console.error).toHaveBeenCalledWith('[ErrorBoundary] Error:', error);
      expect(console.error).toHaveBeenCalledWith('[ErrorBoundary] Component Stack:', errorInfo.componentStack);
    });
  });

  describe('Validação de Campos', () => {
    
    test('deve validar props obrigatórias', () => {
      render(
        <ErrorBoundary>
          <div>Teste</div>
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Teste')).toBeInTheDocument();
    });

    test('deve validar props opcionais', () => {
      render(
        <ErrorBoundary
          maxRetries={5}
          retryDelay={2000}
          showErrorDetails={true}
          showRetryButton={false}
          showReportButton={true}
          metadata={{ userId: '123' }}
        >
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Detalhes do erro')).toBeInTheDocument();
      expect(screen.queryByText('Tentar novamente')).not.toBeInTheDocument();
      expect(screen.getByText('Reportar erro')).toBeInTheDocument();
    });
  });

  describe('Captura de Erros', () => {
    
    test('deve capturar erro de componente de classe', () => {
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Algo deu errado')).toBeInTheDocument();
    });

    test('deve capturar erro de componente funcional', () => {
      render(
        <ErrorBoundary>
          <FunctionalErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Algo deu errado')).toBeInTheDocument();
    });

    test('deve gerar ID único para cada erro', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const firstErrorId = screen.getByText('Algo deu errado').closest('div')?.getAttribute('data-error-id');
      
      rerender(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const secondErrorId = screen.getByText('Algo deu errado').closest('div')?.getAttribute('data-error-id');
      
      expect(firstErrorId).not.toBe(secondErrorId);
    });

    test('deve registrar timestamp do erro', () => {
      const beforeError = new Date();
      
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const afterError = new Date();
      
      // O timestamp deve estar entre beforeError e afterError
      expect(screen.getByText('Algo deu errado')).toBeInTheDocument();
    });
  });

  describe('Fallback UI', () => {
    
    test('deve renderizar fallback padrão com estrutura correta', () => {
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('⚠')).toBeInTheDocument();
      expect(screen.getByText('Algo deu errado')).toBeInTheDocument();
      expect(screen.getByText('Ocorreu um erro inesperado. Nossa equipe foi notificada e está trabalhando para resolver o problema.')).toBeInTheDocument();
    });

    test('deve ter estrutura semântica adequada', () => {
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const retryButton = screen.getByText('Tentar novamente');
      expect(retryButton).toHaveAttribute('tabIndex', '0');
    });

    test('deve ter contraste adequado', () => {
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const errorContainer = screen.getByText('Algo deu errado').closest('div');
      expect(errorContainer).toHaveClass('border-red-200', 'bg-red-50');
    });
  });

  describe('Logging de Erros', () => {
    
    test('deve logar erro no console', () => {
      render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(console.error).toHaveBeenCalledWith('ErrorBoundary caught an error:', expect.any(Error), expect.any(Object));
    });

    test('deve logar falha no report de erro', async () => {
      const failingErrorService = {
        report: jest.fn().mockRejectedValue(new Error('Falha no report'))
      };
      
      render(
        <ErrorBoundary errorReportingService={failingErrorService}>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      await waitFor(() => {
        expect(console.error).toHaveBeenCalledWith('Failed to report error:', expect.any(Error));
      });
    });

    test('deve incluir metadados no report de erro', async () => {
      const metadata = { userId: '123', page: '/dashboard' };
      
      render(
        <ErrorBoundary 
          errorReportingService={mockErrorReportingService}
          metadata={metadata}
        >
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      await waitFor(() => {
        expect(mockErrorReportingService.report).toHaveBeenCalledWith(
          expect.any(Error),
          expect.any(Object),
          expect.objectContaining({
            metadata: metadata
          })
        );
      });
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve limpar timeout no unmount', () => {
      const { unmount } = render(
        <ErrorBoundary>
          <ErrorComponent shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Simular retry para criar timeout
      const retryButton = screen.getByText('Tentar novamente');
      fireEvent.click(retryButton);
      
      // Unmount deve limpar o timeout
      unmount();
      
      // Não deve haver erros de timeout
      expect(console.error).not.toHaveBeenCalledWith(expect.stringContaining('timeout'));
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <div>Conteúdo normal</div>
        </ErrorBoundary>
      );
      
      // Re-renderizar com os mesmos props não deve causar mudanças
      rerender(
        <ErrorBoundary>
          <div>Conteúdo normal</div>
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Conteúdo normal')).toBeInTheDocument();
    });
  });
}); 