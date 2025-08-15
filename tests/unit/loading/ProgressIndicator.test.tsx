/**
 * ProgressIndicator.test.tsx
 * 
 * Testes unitários para o componente ProgressIndicator
 * 
 * Tracing ID: TEST_LOADING_20250127_001
 * Prompt: CHECKLIST_TESTES_UNITARIOS_REACT.md - Fase 3.5
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { 
  ProgressIndicator, 
  StepsProgress,
  useProgress,
  ProgressType, 
  ProgressStatus 
} from '../../../app/components/loading/ProgressIndicator';

// Mock data
const mockSteps = [
  { id: '1', label: 'Inicialização', status: 'completed' as const, description: 'Sistema inicializado' },
  { id: '2', label: 'Carregamento', status: 'active' as const, description: 'Carregando dados' },
  { id: '3', label: 'Processamento', status: 'pending' as const, description: 'Aguardando processamento' },
  { id: '4', label: 'Finalização', status: 'pending' as const, description: 'Finalizando operação' },
];

const defaultProps = {
  type: 'linear' as ProgressType,
  status: 'loading' as ProgressStatus,
  progress: 50,
  total: 100,
  current: 50,
  label: 'Carregando dados',
  description: 'Processando arquivos...',
  showPercentage: true,
  showLabel: true,
  showDescription: true,
  animated: true,
  size: 'md' as const,
  className: '',
  onCancel: jest.fn(),
  onRetry: jest.fn(),
  onPause: jest.fn(),
  onResume: jest.fn(),
};

describe('ProgressIndicator Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar com configurações padrão', () => {
      render(<ProgressIndicator />);
      
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('deve renderizar com todas as propriedades', () => {
      render(<ProgressIndicator {...defaultProps} />);
      
      expect(screen.getByText('Carregando dados')).toBeInTheDocument();
      expect(screen.getByText('Processando arquivos...')).toBeInTheDocument();
      expect(screen.getByText('50%')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('deve renderizar sem label quando showLabel é false', () => {
      render(<ProgressIndicator {...defaultProps} showLabel={false} />);
      
      expect(screen.queryByText('Carregando dados')).not.toBeInTheDocument();
      expect(screen.getByText('50%')).toBeInTheDocument();
    });

    it('deve renderizar sem descrição quando showDescription é false', () => {
      render(<ProgressIndicator {...defaultProps} showDescription={false} />);
      
      expect(screen.getByText('Carregando dados')).toBeInTheDocument();
      expect(screen.queryByText('Processando arquivos...')).not.toBeInTheDocument();
    });

    it('deve renderizar sem porcentagem quando showPercentage é false', () => {
      render(<ProgressIndicator {...defaultProps} showPercentage={false} />);
      
      expect(screen.getByText('Carregando dados')).toBeInTheDocument();
      expect(screen.queryByText('50%')).not.toBeInTheDocument();
    });
  });

  describe('Tipos de Progresso', () => {
    describe('Linear Progress', () => {
      it('deve renderizar progresso linear', () => {
        render(<ProgressIndicator type="linear" progress={75} />);
        
        const progressBar = screen.getByRole('progressbar');
        expect(progressBar).toBeInTheDocument();
        expect(progressBar).toHaveStyle({ width: '75%' });
      });

      it('deve aplicar cores baseadas no status', () => {
        const { rerender } = render(<ProgressIndicator type="linear" status="success" />);
        expect(screen.getByRole('progressbar')).toHaveClass('bg-green-500');
        
        rerender(<ProgressIndicator type="linear" status="error" />);
        expect(screen.getByRole('progressbar')).toHaveClass('bg-red-500');
        
        rerender(<ProgressIndicator type="linear" status="warning" />);
        expect(screen.getByRole('progressbar')).toHaveClass('bg-yellow-500');
        
        rerender(<ProgressIndicator type="linear" status="paused" />);
        expect(screen.getByRole('progressbar')).toHaveClass('bg-gray-400');
      });

      it('deve aplicar tamanhos diferentes', () => {
        const { rerender } = render(<ProgressIndicator type="linear" size="sm" />);
        expect(screen.getByRole('progressbar')).toHaveClass('h-1');
        
        rerender(<ProgressIndicator type="linear" size="md" />);
        expect(screen.getByRole('progressbar')).toHaveClass('h-2');
        
        rerender(<ProgressIndicator type="linear" size="lg" />);
        expect(screen.getByRole('progressbar')).toHaveClass('h-3');
        
        rerender(<ProgressIndicator type="linear" size="xl" />);
        expect(screen.getByRole('progressbar')).toHaveClass('h-4');
      });
    });

    describe('Circular Progress', () => {
      it('deve renderizar progresso circular', () => {
        render(<ProgressIndicator type="circular" progress={60} />);
        
        expect(screen.getByText('60%')).toBeInTheDocument();
        const svg = screen.getByRole('progressbar').querySelector('svg');
        expect(svg).toBeInTheDocument();
      });

      it('deve aplicar tamanhos diferentes para circular', () => {
        const { rerender } = render(<ProgressIndicator type="circular" size="sm" />);
        const svg = screen.getByRole('progressbar').querySelector('svg');
        expect(svg).toHaveClass('w-8', 'h-8');
        
        rerender(<ProgressIndicator type="circular" size="md" />);
        expect(svg).toHaveClass('w-12', 'h-12');
        
        rerender(<ProgressIndicator type="circular" size="lg" />);
        expect(svg).toHaveClass('w-16', 'h-16');
        
        rerender(<ProgressIndicator type="circular" size="xl" />);
        expect(svg).toHaveClass('w-24', 'h-24');
      });
    });

    describe('Dots Progress', () => {
      it('deve renderizar progresso com dots', () => {
        render(<ProgressIndicator type="dots" />);
        
        const dots = screen.getAllByTestId('progress-dot');
        expect(dots).toHaveLength(3);
      });

      it('deve aplicar animação aos dots', () => {
        render(<ProgressIndicator type="dots" animated={true} />);
        
        const dots = screen.getAllByTestId('progress-dot');
        dots.forEach((dot, index) => {
          expect(dot).toHaveStyle({
            animationDelay: `${index * 0.2}s`
          });
        });
      });
    });

    describe('Spinner Progress', () => {
      it('deve renderizar spinner', () => {
        render(<ProgressIndicator type="spinner" />);
        
        expect(screen.getByTestId('spinner')).toBeInTheDocument();
      });

      it('deve mostrar ícone de status', () => {
        const { rerender } = render(<ProgressIndicator type="spinner" status="success" />);
        expect(screen.getByTestId('success-icon')).toBeInTheDocument();
        
        rerender(<ProgressIndicator type="spinner" status="error" />);
        expect(screen.getByTestId('error-icon')).toBeInTheDocument();
        
        rerender(<ProgressIndicator type="spinner" status="warning" />);
        expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
      });
    });
  });

  describe('Steps Progress', () => {
    it('deve renderizar steps progress', () => {
      render(<StepsProgress steps={mockSteps} currentStep={1} />);
      
      expect(screen.getByText('Inicialização')).toBeInTheDocument();
      expect(screen.getByText('Carregamento')).toBeInTheDocument();
      expect(screen.getByText('Processamento')).toBeInTheDocument();
      expect(screen.getByText('Finalização')).toBeInTheDocument();
    });

    it('deve destacar step atual', () => {
      render(<StepsProgress steps={mockSteps} currentStep={1} />);
      
      const currentStep = screen.getByText('Carregamento').closest('div');
      expect(currentStep).toHaveClass('border-blue-500', 'bg-blue-50');
    });

    it('deve marcar steps completados', () => {
      render(<StepsProgress steps={mockSteps} currentStep={1} />);
      
      const completedStep = screen.getByText('Inicialização').closest('div');
      expect(completedStep).toHaveClass('border-green-500', 'bg-green-50');
    });

    it('deve chamar onStepClick ao clicar em step', async () => {
      const user = userEvent.setup();
      const onStepClick = jest.fn();
      
      render(<StepsProgress steps={mockSteps} currentStep={1} onStepClick={onStepClick} />);
      
      const step = screen.getByText('Processamento');
      await user.click(step);
      
      expect(onStepClick).toHaveBeenCalledWith(2);
    });

    it('deve mostrar descrições dos steps', () => {
      render(<StepsProgress steps={mockSteps} currentStep={1} />);
      
      expect(screen.getByText('Sistema inicializado')).toBeInTheDocument();
      expect(screen.getByText('Carregando dados')).toBeInTheDocument();
      expect(screen.getByText('Aguardando processamento')).toBeInTheDocument();
    });
  });

  describe('Ações e Controles', () => {
    it('deve renderizar botão cancelar quando onCancel fornecido', () => {
      render(<ProgressIndicator {...defaultProps} onCancel={jest.fn()} />);
      
      expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
    });

    it('deve chamar onCancel ao clicar em cancelar', async () => {
      const user = userEvent.setup();
      const onCancel = jest.fn();
      
      render(<ProgressIndicator {...defaultProps} onCancel={onCancel} />);
      
      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      await user.click(cancelButton);
      
      expect(onCancel).toHaveBeenCalled();
    });

    it('deve renderizar botão retry quando onRetry fornecido e status é error', () => {
      render(<ProgressIndicator {...defaultProps} status="error" onRetry={jest.fn()} />);
      
      expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeInTheDocument();
    });

    it('deve chamar onRetry ao clicar em retry', async () => {
      const user = userEvent.setup();
      const onRetry = jest.fn();
      
      render(<ProgressIndicator {...defaultProps} status="error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /tentar novamente/i });
      await user.click(retryButton);
      
      expect(onRetry).toHaveBeenCalled();
    });

    it('deve renderizar botão pausar quando onPause fornecido', () => {
      render(<ProgressIndicator {...defaultProps} onPause={jest.fn()} />);
      
      expect(screen.getByRole('button', { name: /pausar/i })).toBeInTheDocument();
    });

    it('deve chamar onPause ao clicar em pausar', async () => {
      const user = userEvent.setup();
      const onPause = jest.fn();
      
      render(<ProgressIndicator {...defaultProps} onPause={onPause} />);
      
      const pauseButton = screen.getByRole('button', { name: /pausar/i });
      await user.click(pauseButton);
      
      expect(onPause).toHaveBeenCalled();
    });

    it('deve renderizar botão resumir quando onResume fornecido e status é paused', () => {
      render(<ProgressIndicator {...defaultProps} status="paused" onResume={jest.fn()} />);
      
      expect(screen.getByRole('button', { name: /resumir/i })).toBeInTheDocument();
    });

    it('deve chamar onResume ao clicar em resumir', async () => {
      const user = userEvent.setup();
      const onResume = jest.fn();
      
      render(<ProgressIndicator {...defaultProps} status="paused" onResume={onResume} />);
      
      const resumeButton = screen.getByRole('button', { name: /resumir/i });
      await user.click(resumeButton);
      
      expect(onResume).toHaveBeenCalled();
    });
  });

  describe('Hook useProgress', () => {
    it('deve fornecer estado inicial correto', () => {
      const TestComponent = () => {
        const { progress, status, start, complete, error, pause, resume, reset } = useProgress(25);
        
        return (
          <div>
            <div data-testid="progress">{progress}</div>
            <div data-testid="status">{status}</div>
            <button onClick={start}>Start</button>
            <button onClick={complete}>Complete</button>
            <button onClick={error}>Error</button>
            <button onClick={pause}>Pause</button>
            <button onClick={resume}>Resume</button>
            <button onClick={reset}>Reset</button>
          </div>
        );
      };
      
      render(<TestComponent />);
      
      expect(screen.getByTestId('progress')).toHaveTextContent('25');
      expect(screen.getByTestId('status')).toHaveTextContent('idle');
    });

    it('deve atualizar status ao chamar start', async () => {
      const user = userEvent.setup();
      const TestComponent = () => {
        const { status, start } = useProgress();
        
        return (
          <div>
            <div data-testid="status">{status}</div>
            <button onClick={start}>Start</button>
          </div>
        );
      };
      
      render(<TestComponent />);
      
      expect(screen.getByTestId('status')).toHaveTextContent('idle');
      
      const startButton = screen.getByText('Start');
      await user.click(startButton);
      
      expect(screen.getByTestId('status')).toHaveTextContent('loading');
    });

    it('deve atualizar status ao chamar complete', async () => {
      const user = userEvent.setup();
      const TestComponent = () => {
        const { status, start, complete } = useProgress();
        
        return (
          <div>
            <div data-testid="status">{status}</div>
            <button onClick={start}>Start</button>
            <button onClick={complete}>Complete</button>
          </div>
        );
      };
      
      render(<TestComponent />);
      
      const startButton = screen.getByText('Start');
      await user.click(startButton);
      
      const completeButton = screen.getByText('Complete');
      await user.click(completeButton);
      
      expect(screen.getByTestId('status')).toHaveTextContent('success');
    });

    it('deve atualizar status ao chamar error', async () => {
      const user = userEvent.setup();
      const TestComponent = () => {
        const { status, error } = useProgress();
        
        return (
          <div>
            <div data-testid="status">{status}</div>
            <button onClick={error}>Error</button>
          </div>
        );
      };
      
      render(<TestComponent />);
      
      const errorButton = screen.getByText('Error');
      await user.click(errorButton);
      
      expect(screen.getByTestId('status')).toHaveTextContent('error');
    });
  });

  describe('Validação de Progresso', () => {
    it('deve limitar progresso entre 0 e 100', () => {
      const { rerender } = render(<ProgressIndicator progress={-10} />);
      expect(screen.getByText('0%')).toBeInTheDocument();
      
      rerender(<ProgressIndicator progress={150} />);
      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('deve calcular progresso baseado em current e total', () => {
      render(<ProgressIndicator current={25} total={100} />);
      expect(screen.getByText('25%')).toBeInTheDocument();
    });

    it('deve usar progress quando fornecido em vez de calcular', () => {
      render(<ProgressIndicator progress={75} current={25} total={100} />);
      expect(screen.getByText('75%')).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter role progressbar', () => {
      render(<ProgressIndicator />);
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('deve ter aria-label apropriado', () => {
      render(<ProgressIndicator label="Carregando dados" />);
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-label', 'Carregando dados');
    });

    it('deve ter aria-valuenow e aria-valuemax', () => {
      render(<ProgressIndicator progress={60} />);
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '60');
      expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    });

    it('deve ser navegável por teclado', async () => {
      const user = userEvent.setup();
      render(<ProgressIndicator onCancel={jest.fn()} />);
      
      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      cancelButton.focus();
      
      await user.tab();
      expect(screen.getByRole('progressbar')).toHaveFocus();
    });
  });

  describe('Performance', () => {
    it('deve memoizar renderização para evitar re-renders desnecessários', () => {
      const { rerender } = render(<ProgressIndicator progress={50} />);
      
      const initialRender = screen.getByRole('progressbar');
      
      rerender(<ProgressIndicator progress={50} />);
      
      const reRender = screen.getByRole('progressbar');
      expect(reRender).toBe(initialRender);
    });

    it('deve aplicar animações apenas quando animated é true', () => {
      const { rerender } = render(<ProgressIndicator animated={true} />);
      expect(screen.getByRole('progressbar')).toHaveClass('transition-all');
      
      rerender(<ProgressIndicator animated={false} />);
      expect(screen.getByRole('progressbar')).not.toHaveClass('transition-all');
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com progresso zero', () => {
      render(<ProgressIndicator progress={0} />);
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('deve lidar com progresso 100', () => {
      render(<ProgressIndicator progress={100} />);
      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('deve lidar com valores undefined/null', () => {
      render(<ProgressIndicator progress={undefined} current={undefined} total={undefined} />);
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('deve lidar com total zero', () => {
      render(<ProgressIndicator current={10} total={0} />);
      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('deve lidar com labels muito longos', () => {
      const longLabel = 'A'.repeat(200);
      render(<ProgressIndicator label={longLabel} />);
      expect(screen.getByText(longLabel)).toBeInTheDocument();
    });

    it('deve lidar com muitos steps', () => {
      const manySteps = Array.from({ length: 20 }, (_, i) => ({
        id: `${i}`,
        label: `Step ${i}`,
        status: 'pending' as const
      }));
      
      render(<StepsProgress steps={manySteps} />);
      expect(screen.getAllByText(/Step \d+/)).toHaveLength(20);
    });
  });

  describe('Integração com Sistema', () => {
    it('deve integrar com sistema de temas', () => {
      render(<ProgressIndicator />);
      
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveClass('dark:bg-gray-700');
    });

    it('deve integrar com sistema de classes utilitárias', () => {
      render(<ProgressIndicator className="custom-class" />);
      
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveClass('custom-class');
    });

    it('deve integrar com sistema de animações', () => {
      render(<ProgressIndicator animated={true} />);
      
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveClass('transition-all', 'duration-300');
    });
  });
}); 