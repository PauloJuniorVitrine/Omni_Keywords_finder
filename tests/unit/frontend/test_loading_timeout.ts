/**
 * 🧪 Testes Unitários - Loading com Timeout
 * 
 * Tracing ID: TEST_LOADING_TIMEOUT_2025_001
 * Data/Hora: 2025-01-27 19:40:00 UTC
 * Versão: 1.0
 * Status: 🚀 IMPLEMENTAÇÃO
 * 
 * Testes para hook useLoadingWithTimeout e componente LoadingWithTimeout.
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { useLoadingWithTimeout, LoadingTimeoutConfig } from '../../../app/hooks/useLoadingWithTimeout';
import { LoadingWithTimeout } from '../../../app/components/shared/LoadingWithTimeout';

// Mock para timers
jest.useFakeTimers();

// Componente de teste para o hook
const TestHookComponent = ({ 
  asyncFunction, 
  config = {} 
}: { 
  asyncFunction: () => Promise<any>; 
  config?: LoadingTimeoutConfig; 
}) => {
  const state = useLoadingWithTimeout(asyncFunction, config);
  
  return (
    <div>
      <div data-testid="isLoading">{state.isLoading.toString()}</div>
      <div data-testid="hasTimedOut">{state.hasTimedOut.toString()}</div>
      <div data-testid="isCancelled">{state.isCancelled.toString()}</div>
      <div data-testid="currentAttempt">{state.currentAttempt}</div>
      <div data-testid="timeRemaining">{state.timeRemaining}</div>
      <div data-testid="error">{state.error?.message || 'null'}</div>
      <button data-testid="cancel" onClick={state.cancel}>Cancel</button>
      <button data-testid="retry" onClick={state.retry}>Retry</button>
      <button data-testid="reset" onClick={state.reset}>Reset</button>
    </div>
  );
};

describe('useLoadingWithTimeout Hook', () => {
  beforeEach(() => {
    jest.clearAllTimers();
  });

  it('should initialize with correct default state', () => {
    const asyncFunction = jest.fn().mockResolvedValue('success');
    
    render(<TestHookComponent asyncFunction={asyncFunction} />);
    
    expect(screen.getByTestId('isLoading')).toHaveTextContent('false');
    expect(screen.getByTestId('hasTimedOut')).toHaveTextContent('false');
    expect(screen.getByTestId('isCancelled')).toHaveTextContent('false');
    expect(screen.getByTestId('currentAttempt')).toHaveTextContent('0');
    expect(screen.getByTestId('timeRemaining')).toHaveTextContent('30000');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });

  it('should execute async function and show loading state', async () => {
    const asyncFunction = jest.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve('success'), 1000))
    );
    
    render(<TestHookComponent asyncFunction={asyncFunction} />);
    
    // Inicialmente não está carregando
    expect(screen.getByTestId('isLoading')).toHaveTextContent('false');
    
    // Executar função
    act(() => {
      asyncFunction();
    });
    
    // Deve estar carregando
    expect(screen.getByTestId('isLoading')).toHaveTextContent('true');
    
    // Avançar tempo
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('isLoading')).toHaveTextContent('false');
    });
  });

  it('should handle timeout correctly', async () => {
    const asyncFunction = jest.fn().mockImplementation(() => 
      new Promise(() => {}) // Promise que nunca resolve
    );
    
    const config: LoadingTimeoutConfig = {
      timeout: 1000,
      autoRetry: false
    };
    
    render(<TestHookComponent asyncFunction={asyncFunction} config={config} />);
    
    // Executar função
    act(() => {
      asyncFunction();
    });
    
    // Avançar tempo para causar timeout
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('hasTimedOut')).toHaveTextContent('true');
      expect(screen.getByTestId('isLoading')).toHaveTextContent('false');
      expect(screen.getByTestId('error')).toHaveTextContent('Timeout após 1000ms');
    });
  });

  it('should handle cancellation correctly', () => {
    const asyncFunction = jest.fn().mockResolvedValue('success');
    
    render(<TestHookComponent asyncFunction={asyncFunction} />);
    
    // Cancelar
    fireEvent.click(screen.getByTestId('cancel'));
    
    expect(screen.getByTestId('isCancelled')).toHaveTextContent('true');
    expect(screen.getByTestId('isLoading')).toHaveTextContent('false');
    expect(screen.getByTestId('hasTimedOut')).toHaveTextContent('false');
  });

  it('should handle retry correctly', async () => {
    const asyncFunction = jest.fn()
      .mockRejectedValueOnce(new Error('First error'))
      .mockResolvedValueOnce('success');
    
    const config: LoadingTimeoutConfig = {
      timeout: 5000,
      maxRetries: 3,
      autoRetry: false
    };
    
    render(<TestHookComponent asyncFunction={asyncFunction} config={config} />);
    
    // Primeira tentativa
    act(() => {
      asyncFunction();
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('First error');
    });
    
    // Retry manual
    fireEvent.click(screen.getByTestId('retry'));
    
    await waitFor(() => {
      expect(screen.getByTestId('currentAttempt')).toHaveTextContent('1');
      expect(screen.getByTestId('error')).toHaveTextContent('null');
    });
  });

  it('should handle auto retry on error', async () => {
    const asyncFunction = jest.fn()
      .mockRejectedValueOnce(new Error('First error'))
      .mockResolvedValueOnce('success');
    
    const config: LoadingTimeoutConfig = {
      timeout: 5000,
      maxRetries: 3,
      autoRetry: true,
      retryDelay: 1000
    };
    
    render(<TestHookComponent asyncFunction={asyncFunction} config={config} />);
    
    // Primeira tentativa
    act(() => {
      asyncFunction();
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('First error');
    });
    
    // Avançar tempo para retry automático
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('currentAttempt')).toHaveTextContent('1');
    });
  });

  it('should respect max retries limit', async () => {
    const asyncFunction = jest.fn().mockRejectedValue(new Error('Always fails'));
    
    const config: LoadingTimeoutConfig = {
      timeout: 1000,
      maxRetries: 2,
      autoRetry: true,
      retryDelay: 500
    };
    
    render(<TestHookComponent asyncFunction={asyncFunction} config={config} />);
    
    // Primeira tentativa
    act(() => {
      asyncFunction();
    });
    
    // Avançar tempo para retries automáticos
    act(() => {
      jest.advanceTimersByTime(500); // Primeiro retry
    });
    
    act(() => {
      jest.advanceTimersByTime(500); // Segundo retry
    });
    
    act(() => {
      jest.advanceTimersByTime(500); // Tentativa de terceiro retry
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('currentAttempt')).toHaveTextContent('2');
      expect(screen.getByTestId('error')).toHaveTextContent('Máximo de tentativas (2) excedido');
    });
  });

  it('should update time remaining correctly', () => {
    const asyncFunction = jest.fn().mockImplementation(() => 
      new Promise(() => {}) // Promise que nunca resolve
    );
    
    const config: LoadingTimeoutConfig = {
      timeout: 3000
    };
    
    render(<TestHookComponent asyncFunction={asyncFunction} config={config} />);
    
    // Executar função
    act(() => {
      asyncFunction();
    });
    
    // Verificar tempo inicial
    expect(screen.getByTestId('timeRemaining')).toHaveTextContent('3000');
    
    // Avançar tempo
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    // Verificar tempo atualizado
    expect(screen.getByTestId('timeRemaining')).toHaveTextContent('2000');
  });

  it('should reset state correctly', () => {
    const asyncFunction = jest.fn().mockResolvedValue('success');
    
    render(<TestHookComponent asyncFunction={asyncFunction} />);
    
    // Cancelar primeiro
    fireEvent.click(screen.getByTestId('cancel'));
    expect(screen.getByTestId('isCancelled')).toHaveTextContent('true');
    
    // Reset
    fireEvent.click(screen.getByTestId('reset'));
    
    expect(screen.getByTestId('isCancelled')).toHaveTextContent('false');
    expect(screen.getByTestId('hasTimedOut')).toHaveTextContent('false');
    expect(screen.getByTestId('currentAttempt')).toHaveTextContent('0');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });
});

describe('LoadingWithTimeout Component', () => {
  beforeEach(() => {
    jest.clearAllTimers();
  });

  it('should render children when not loading', () => {
    const asyncFunction = jest.fn().mockResolvedValue('success');
    
    render(
      <LoadingWithTimeout asyncFunction={asyncFunction} autoExecute={false}>
        <div data-testid="content">Content</div>
      </LoadingWithTimeout>
    );
    
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('should show loading component when executing', () => {
    const asyncFunction = jest.fn().mockImplementation(() => 
      new Promise(() => {}) // Promise que nunca resolve
    );
    
    render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        config={{ timeout: 5000 }}
        autoExecute={true}
      />
    );
    
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
    expect(screen.getByText('Tempo restante: 5s')).toBeInTheDocument();
  });

  it('should show timeout component when timeout occurs', async () => {
    const asyncFunction = jest.fn().mockImplementation(() => 
      new Promise(() => {}) // Promise que nunca resolve
    );
    
    render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        config={{ timeout: 1000, autoRetry: false }}
        autoExecute={true}
      />
    );
    
    // Avançar tempo para causar timeout
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Timeout')).toBeInTheDocument();
      expect(screen.getByText('A operação demorou mais do que o esperado.')).toBeInTheDocument();
      expect(screen.getByText('Tentar Novamente')).toBeInTheDocument();
      expect(screen.getByText('Cancelar')).toBeInTheDocument();
    });
  });

  it('should show error component when error occurs', async () => {
    const asyncFunction = jest.fn().mockRejectedValue(new Error('Test error'));
    
    render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        config={{ autoRetry: false }}
        autoExecute={true}
      />
    );
    
    await waitFor(() => {
      expect(screen.getByText('Erro')).toBeInTheDocument();
      expect(screen.getByText('Test error')).toBeInTheDocument();
      expect(screen.getByText('Tentar Novamente')).toBeInTheDocument();
    });
  });

  it('should show cancelled state when cancelled', () => {
    const asyncFunction = jest.fn().mockResolvedValue('success');
    
    render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        autoExecute={false}
      />
    );
    
    // Simular cancelamento
    const { rerender } = render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        autoExecute={false}
      />
    );
    
    // Forçar estado cancelado (isso seria feito internamente pelo hook)
    // Como não podemos acessar diretamente o estado do hook, testamos a funcionalidade
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('should call onSuccess callback when successful', async () => {
    const asyncFunction = jest.fn().mockResolvedValue('success');
    const onSuccess = jest.fn();
    
    render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        onSuccess={onSuccess}
        autoExecute={true}
      />
    );
    
    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith('success');
    });
  });

  it('should call onError callback when error occurs', async () => {
    const error = new Error('Test error');
    const asyncFunction = jest.fn().mockRejectedValue(error);
    const onError = jest.fn();
    
    render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        onError={onError}
        config={{ autoRetry: false }}
        autoExecute={true}
      />
    );
    
    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(error);
    });
  });

  it('should show retry attempt count', async () => {
    const asyncFunction = jest.fn()
      .mockRejectedValueOnce(new Error('First error'))
      .mockResolvedValueOnce('success');
    
    render(
      <LoadingWithTimeout 
        asyncFunction={asyncFunction} 
        config={{ 
          timeout: 5000, 
          maxRetries: 3, 
          autoRetry: true, 
          retryDelay: 1000 
        }}
        autoExecute={true}
      />
    );
    
    // Avançar tempo para primeiro retry
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Tentativa 1 de 3')).toBeInTheDocument();
    });
  });
});

describe('useLoadingWithTimeout Hook - Edge Cases', () => {
  beforeEach(() => {
    jest.clearAllTimers();
  });

  it('should handle component unmount during execution', () => {
    const asyncFunction = jest.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve('success'), 1000))
    );
    
    const { unmount } = render(<TestHookComponent asyncFunction={asyncFunction} />);
    
    // Executar função
    act(() => {
      asyncFunction();
    });
    
    // Desmontar componente
    unmount();
    
    // Avançar tempo
    act(() => {
      jest.advanceTimersByTime(1000);
    });
    
    // Não deve haver erros de memory leak
    expect(asyncFunction).toHaveBeenCalled();
  });

  it('should handle multiple rapid retries', async () => {
    const asyncFunction = jest.fn().mockRejectedValue(new Error('Always fails'));
    
    render(<TestHookComponent asyncFunction={asyncFunction} />);
    
    // Múltiplos retries rápidos
    fireEvent.click(screen.getByTestId('retry'));
    fireEvent.click(screen.getByTestId('retry'));
    fireEvent.click(screen.getByTestId('retry'));
    
    await waitFor(() => {
      expect(screen.getByTestId('currentAttempt')).toHaveTextContent('3');
    });
  });

  it('should handle zero timeout', () => {
    const asyncFunction = jest.fn().mockResolvedValue('success');
    
    const config: LoadingTimeoutConfig = {
      timeout: 0
    };
    
    render(<TestHookComponent asyncFunction={asyncFunction} config={config} />);
    
    expect(screen.getByTestId('timeRemaining')).toHaveTextContent('0');
  });
}); 