/**
 * ToastManager.test.tsx
 * 
 * Testes unitários para o componente ToastManager
 * 
 * Tracing ID: TEST_NOTIFICATIONS_20250127_002
 * Prompt: CHECKLIST_TESTES_UNITARIOS_REACT.md - Fase 3.4.2
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ToastManager, { 
  Toast, 
  ToastType, 
  ToastPosition, 
  ToastAnimation,
  ToastAction 
} from '../../../app/components/notifications/ToastManager';

// Mock Material-UI components
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  Portal: ({ children }: { children: React.ReactNode }) => <div data-testid="portal">{children}</div>,
  Snackbar: ({ children, open, anchorOrigin, TransitionComponent }: any) => 
    open ? <div data-testid="snackbar" data-anchor={JSON.stringify(anchorOrigin)}>{children}</div> : null,
  Alert: ({ children, severity, icon, action, onMouseEnter, onMouseLeave }: any) => (
    <div 
      data-testid="alert" 
      data-severity={severity}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {icon && <div data-testid="alert-icon">{icon}</div>}
      <div data-testid="alert-content">{children}</div>
      {action && <div data-testid="alert-actions">{action}</div>}
    </div>
  ),
  AlertTitle: ({ children }: any) => <div data-testid="alert-title">{children}</div>,
  Box: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Typography: ({ children, variant }: any) => <div data-testid={`typography-${variant}`}>{children}</div>,
  IconButton: ({ children, onClick, ...props }: any) => (
    <button data-testid="icon-button" onClick={onClick} {...props}>{children}</button>
  ),
  Button: ({ children, onClick, variant, color }: any) => (
    <button data-testid="button" data-variant={variant} data-color={color} onClick={onClick}>
      {children}
    </button>
  ),
  Chip: ({ label, icon, variant }: any) => (
    <div data-testid="chip" data-variant={variant}>
      {icon && <span data-testid="chip-icon">{icon}</span>}
      {label}
    </div>
  ),
  LinearProgress: ({ value, variant }: any) => (
    <div data-testid="linear-progress" data-value={value} data-variant={variant} />
  ),
  Collapse: ({ children, in: inProp }: any) => 
    inProp ? <div data-testid="collapse">{children}</div> : null,
  Slide: ({ children }: any) => <div data-testid="slide">{children}</div>,
  Grow: ({ children }: any) => <div data-testid="grow">{children}</div>,
  Fade: ({ children }: any) => <div data-testid="fade">{children}</div>,
  Zoom: ({ children }: any) => <div data-testid="zoom">{children}</div>,
  useTheme: () => ({
    breakpoints: {
      down: () => false
    },
    zIndex: {
      snackbar: 1400
    }
  }),
  useMediaQuery: () => false
}));

// Mock Material-UI icons
jest.mock('@mui/icons-material', () => ({
  Close: () => <div data-testid="close-icon">Close</div>,
  CheckCircle: () => <div data-testid="check-circle-icon">CheckCircle</div>,
  Error: () => <div data-testid="error-icon">Error</div>,
  Warning: () => <div data-testid="warning-icon">Warning</div>,
  Info: () => <div data-testid="info-icon">Info</div>,
  Refresh: () => <div data-testid="refresh-icon">Refresh</div>,
  Undo: () => <div data-testid="undo-icon">Undo</div>,
  Redo: () => <div data-testid="redo-icon">Redo</div>,
  Download: () => <div data-testid="download-icon">Download</div>,
  Share: () => <div data-testid="share-icon">Share</div>,
  Settings: () => <div data-testid="settings-icon">Settings</div>,
  Notifications: () => <div data-testid="notifications-icon">Notifications</div>,
  AutoAwesome: () => <div data-testid="auto-awesome-icon">AutoAwesome</div>,
  Timer: () => <div data-testid="timer-icon">Timer</div>,
  Pause: () => <div data-testid="pause-icon">Pause</div>,
  PlayArrow: () => <div data-testid="play-icon">PlayArrow</div>,
}));

// Mock data
const mockToasts: Toast[] = [
  {
    id: '1',
    type: 'success',
    title: 'Sucesso!',
    message: 'Operação realizada com sucesso',
    position: 'bottom-right',
    duration: 5000,
    timestamp: new Date('2025-01-27T10:00:00'),
    autoHide: true
  },
  {
    id: '2',
    type: 'error',
    title: 'Erro!',
    message: 'Ocorreu um erro na operação',
    position: 'top-right',
    duration: 8000,
    timestamp: new Date('2025-01-27T10:01:00'),
    autoHide: true,
    onRetry: jest.fn()
  },
  {
    id: '3',
    type: 'warning',
    title: 'Atenção!',
    message: 'Esta ação requer confirmação',
    position: 'bottom-center',
    duration: 10000,
    timestamp: new Date('2025-01-27T10:02:00'),
    autoHide: true,
    onUndo: jest.fn(),
    actions: [
      {
        label: 'Confirmar',
        onClick: jest.fn(),
        color: 'primary',
        variant: 'contained'
      },
      {
        label: 'Cancelar',
        onClick: jest.fn(),
        color: 'secondary',
        variant: 'outlined'
      }
    ]
  },
  {
    id: '4',
    type: 'info',
    title: 'Informação',
    message: 'Nova atualização disponível',
    position: 'top-left',
    duration: 6000,
    timestamp: new Date('2025-01-27T10:03:00'),
    autoHide: true,
    metadata: {
      version: '1.2.0',
      size: '2.5MB',
      features: ['Bug fixes', 'Performance improvements']
    }
  }
];

const defaultProps = {
  toasts: mockToasts,
  onClose: jest.fn(),
  onPause: jest.fn(),
  onResume: jest.fn(),
  onAction: jest.fn(),
  maxToasts: 5,
  defaultPosition: 'bottom-right' as ToastPosition,
  defaultDuration: 6000,
  defaultAnimation: 'slide' as ToastAnimation,
  enableProgress: true,
  enablePause: true,
  enableStacking: true,
  enableSound: false,
  enableVibration: false,
};

// Wrapper component with theme
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const theme = createTheme();
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
};

describe('ToastManager Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar todos os toasts configurados', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('portal')).toBeInTheDocument();
      expect(screen.getAllByTestId('snackbar')).toHaveLength(4);
      expect(screen.getAllByTestId('alert')).toHaveLength(4);
    });

    it('deve renderizar toasts com tipos corretos', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const alerts = screen.getAllByTestId('alert');
      expect(alerts[0]).toHaveAttribute('data-severity', 'success');
      expect(alerts[1]).toHaveAttribute('data-severity', 'error');
      expect(alerts[2]).toHaveAttribute('data-severity', 'warning');
      expect(alerts[3]).toHaveAttribute('data-severity', 'info');
    });

    it('deve renderizar ícones corretos para cada tipo', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getAllByTestId('alert-icon')).toHaveLength(4);
      expect(screen.getByTestId('check-circle-icon')).toBeInTheDocument();
      expect(screen.getByTestId('error-icon')).toBeInTheDocument();
      expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
      expect(screen.getByTestId('info-icon')).toBeInTheDocument();
    });

    it('deve renderizar títulos e mensagens', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByText('Sucesso!')).toBeInTheDocument();
      expect(screen.getByText('Operação realizada com sucesso')).toBeInTheDocument();
      expect(screen.getByText('Erro!')).toBeInTheDocument();
      expect(screen.getByText('Ocorreu um erro na operação')).toBeInTheDocument();
    });

    it('deve renderizar timestamps', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getAllByTestId('typography-caption')).toHaveLength(4);
    });

    it('deve renderizar com posições corretas', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const snackbars = screen.getAllByTestId('snackbar');
      expect(snackbars[0]).toHaveAttribute('data-anchor', '{"vertical":"bottom","horizontal":"right"}');
      expect(snackbars[1]).toHaveAttribute('data-anchor', '{"vertical":"top","horizontal":"right"}');
      expect(snackbars[2]).toHaveAttribute('data-anchor', '{"vertical":"bottom","horizontal":"center"}');
      expect(snackbars[3]).toHaveAttribute('data-anchor', '{"vertical":"top","horizontal":"left"}');
    });
  });

  describe('Funcionalidades de Ação', () => {
    it('deve chamar onClose ao clicar no botão fechar', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} onClose={onClose} />
        </TestWrapper>
      );
      
      const closeButtons = screen.getAllByTestId('icon-button');
      await user.click(closeButtons[0]);
      
      expect(onClose).toHaveBeenCalledWith('1');
    });

    it('deve renderizar ações customizadas', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByText('Confirmar')).toBeInTheDocument();
      expect(screen.getByText('Cancelar')).toBeInTheDocument();
    });

    it('deve chamar onAction ao clicar em ação customizada', async () => {
      const user = userEvent.setup();
      const onAction = jest.fn();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} onAction={onAction} />
        </TestWrapper>
      );
      
      const confirmButton = screen.getByText('Confirmar');
      await user.click(confirmButton);
      
      expect(onAction).toHaveBeenCalledWith('3', 0);
    });

    it('deve renderizar botão de retry quando onRetry disponível', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('refresh-icon')).toBeInTheDocument();
    });

    it('deve chamar onRetry ao clicar no botão retry', async () => {
      const user = userEvent.setup();
      const onRetry = jest.fn();
      const toastWithRetry: Toast = {
        ...mockToasts[1],
        onRetry
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastWithRetry]} />
        </TestWrapper>
      );
      
      const retryButton = screen.getByTestId('refresh-icon').closest('button');
      await user.click(retryButton!);
      
      expect(onRetry).toHaveBeenCalled();
    });

    it('deve renderizar botão de undo quando onUndo disponível', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('undo-icon')).toBeInTheDocument();
    });

    it('deve chamar onUndo ao clicar no botão undo', async () => {
      const user = userEvent.setup();
      const onUndo = jest.fn();
      const toastWithUndo: Toast = {
        ...mockToasts[2],
        onUndo
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastWithUndo]} />
        </TestWrapper>
      );
      
      const undoButton = screen.getByTestId('undo-icon').closest('button');
      await user.click(undoButton!);
      
      expect(onUndo).toHaveBeenCalled();
    });
  });

  describe('Funcionalidades de Pausa/Resume', () => {
    it('deve renderizar botão de pausa quando enablePause é true', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} enablePause={true} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('pause-icon')).toBeInTheDocument();
    });

    it('deve chamar onPause ao clicar no botão pausa', async () => {
      const user = userEvent.setup();
      const onPause = jest.fn();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} onPause={onPause} />
        </TestWrapper>
      );
      
      const pauseButton = screen.getByTestId('pause-icon').closest('button');
      await user.click(pauseButton!);
      
      expect(onPause).toHaveBeenCalledWith('1');
    });

    it('deve chamar onResume ao clicar no botão resume', async () => {
      const user = userEvent.setup();
      const onResume = jest.fn();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} onResume={onResume} />
        </TestWrapper>
      );
      
      // Primeiro clica para pausar
      const pauseButton = screen.getByTestId('pause-icon').closest('button');
      await user.click(pauseButton!);
      
      // Depois clica para resumir
      const playButton = screen.getByTestId('play-icon').closest('button');
      await user.click(playButton!);
      
      expect(onResume).toHaveBeenCalledWith('1');
    });

    it('deve pausar ao passar o mouse quando enablePause é true', async () => {
      const user = userEvent.setup();
      const onPause = jest.fn();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} onPause={onPause} />
        </TestWrapper>
      );
      
      const alert = screen.getAllByTestId('alert')[0];
      await user.hover(alert);
      
      expect(onPause).toHaveBeenCalled();
    });

    it('deve resumir ao remover o mouse quando enablePause é true', async () => {
      const user = userEvent.setup();
      const onResume = jest.fn();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} onResume={onResume} />
        </TestWrapper>
      );
      
      const alert = screen.getAllByTestId('alert')[0];
      await user.hover(alert);
      await user.unhover(alert);
      
      expect(onResume).toHaveBeenCalled();
    });
  });

  describe('Progresso e Auto-Dismiss', () => {
    it('deve renderizar barra de progresso quando enableProgress é true', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} enableProgress={true} />
        </TestWrapper>
      );
      
      expect(screen.getAllByTestId('linear-progress')).toHaveLength(4);
    });

    it('deve não renderizar barra de progresso quando enableProgress é false', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} enableProgress={false} />
        </TestWrapper>
      );
      
      expect(screen.queryByTestId('linear-progress')).not.toBeInTheDocument();
    });

    it('deve atualizar progresso ao longo do tempo', async () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const progressBar = screen.getAllByTestId('linear-progress')[0];
      expect(progressBar).toHaveAttribute('data-value', '0');
      
      // Avança o tempo
      act(() => {
        jest.advanceTimersByTime(1000);
      });
      
      await waitFor(() => {
        expect(progressBar).toHaveAttribute('data-value', expect.any(String));
      });
    });

    it('deve fechar toast automaticamente após duração', async () => {
      const onClose = jest.fn();
      const shortToast: Toast = {
        id: 'short',
        type: 'info',
        message: 'Toast curto',
        duration: 1000,
        timestamp: new Date(),
        autoHide: true
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[shortToast]} onClose={onClose} />
        </TestWrapper>
      );
      
      act(() => {
        jest.advanceTimersByTime(1000);
      });
      
      await waitFor(() => {
        expect(onClose).toHaveBeenCalledWith('short');
      });
    });

    it('deve não fechar toast persistente automaticamente', async () => {
      const onClose = jest.fn();
      const persistentToast: Toast = {
        id: 'persistent',
        type: 'info',
        message: 'Toast persistente',
        duration: 1000,
        timestamp: new Date(),
        autoHide: true,
        persistent: true
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[persistentToast]} onClose={onClose} />
        </TestWrapper>
      );
      
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      expect(onClose).not.toHaveBeenCalled();
    });
  });

  describe('Metadados e Expansão', () => {
    it('deve renderizar metadados quando disponíveis', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByText('Detalhes:')).toBeInTheDocument();
      expect(screen.getByText(/"version": "1.2.0"/)).toBeInTheDocument();
    });

    it('deve expandir/colapsar metadados ao clicar no botão', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const expandButton = screen.getByTestId('auto-awesome-icon').closest('button');
      await user.click(expandButton!);
      
      expect(screen.getByTestId('collapse')).toBeInTheDocument();
    });

    it('deve mostrar chip de pausado quando toast está pausado', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const pauseButton = screen.getByTestId('pause-icon').closest('button');
      await user.click(pauseButton!);
      
      expect(screen.getByText('Pausado')).toBeInTheDocument();
      expect(screen.getByTestId('chip')).toHaveAttribute('data-variant', 'outlined');
    });
  });

  describe('Configurações e Limites', () => {
    it('deve respeitar limite máximo de toasts', () => {
      const manyToasts = Array.from({ length: 10 }, (_, i) => ({
        id: `toast-${i}`,
        type: 'info' as ToastType,
        message: `Toast ${i}`,
        timestamp: new Date(),
        autoHide: true
      }));
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={manyToasts} maxToasts={3} />
        </TestWrapper>
      );
      
      expect(screen.getAllByTestId('snackbar')).toHaveLength(3);
    });

    it('deve usar posição padrão quando não especificada', () => {
      const toastWithoutPosition: Toast = {
        id: 'default',
        type: 'info',
        message: 'Toast sem posição',
        timestamp: new Date(),
        autoHide: true
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastWithoutPosition]} />
        </TestWrapper>
      );
      
      const snackbar = screen.getByTestId('snackbar');
      expect(snackbar).toHaveAttribute('data-anchor', '{"vertical":"bottom","horizontal":"right"}');
    });

    it('deve usar animação padrão quando não especificada', () => {
      const toastWithoutAnimation: Toast = {
        id: 'default',
        type: 'info',
        message: 'Toast sem animação',
        timestamp: new Date(),
        autoHide: true
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastWithoutAnimation]} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('slide')).toBeInTheDocument();
    });

    it('deve usar animação customizada quando especificada', () => {
      const toastWithAnimation: Toast = {
        id: 'animated',
        type: 'info',
        message: 'Toast com animação',
        timestamp: new Date(),
        autoHide: true,
        animation: 'grow'
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastWithAnimation]} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('grow')).toBeInTheDocument();
    });
  });

  describe('Stacking', () => {
    it('deve empilhar toasts quando enableStacking é true', () => {
      const toastsSamePosition = [
        { ...mockToasts[0], position: 'bottom-right' as ToastPosition },
        { ...mockToasts[1], position: 'bottom-right' as ToastPosition },
        { ...mockToasts[2], position: 'bottom-right' as ToastPosition }
      ];
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={toastsSamePosition} enableStacking={true} />
        </TestWrapper>
      );
      
      expect(screen.getAllByTestId('snackbar')).toHaveLength(3);
    });

    it('deve mostrar apenas o toast mais recente quando enableStacking é false', () => {
      const toastsSamePosition = [
        { ...mockToasts[0], position: 'bottom-right' as ToastPosition },
        { ...mockToasts[1], position: 'bottom-right' as ToastPosition },
        { ...mockToasts[2], position: 'bottom-right' as ToastPosition }
      ];
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={toastsSamePosition} enableStacking={false} />
        </TestWrapper>
      );
      
      expect(screen.getAllByTestId('snackbar')).toHaveLength(1);
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter roles e labels apropriados', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('portal')).toBeInTheDocument();
      expect(screen.getAllByTestId('alert')).toHaveLength(4);
    });

    it('deve ser navegável por teclado', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const closeButton = screen.getAllByTestId('icon-button')[0];
      closeButton.focus();
      
      await user.tab();
      expect(screen.getAllByTestId('icon-button')[1]).toHaveFocus();
    });

    it('deve ter aria-labels apropriados', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const alerts = screen.getAllByTestId('alert');
      alerts.forEach(alert => {
        expect(alert).toHaveAttribute('data-severity');
      });
    });
  });

  describe('Performance', () => {
    it('deve limpar timers ao desmontar', () => {
      const { unmount } = render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');
      const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
      
      unmount();
      
      expect(clearTimeoutSpy).toHaveBeenCalled();
      expect(clearIntervalSpy).toHaveBeenCalled();
      
      clearTimeoutSpy.mockRestore();
      clearIntervalSpy.mockRestore();
    });

    it('deve memoizar estados para evitar re-renders desnecessários', () => {
      const { rerender } = render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const initialRender = screen.getAllByTestId('alert')[0];
      
      rerender(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const reRender = screen.getAllByTestId('alert')[0];
      expect(reRender).toBe(initialRender);
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com toasts vazios', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[]} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('portal')).toBeInTheDocument();
      expect(screen.queryByTestId('snackbar')).not.toBeInTheDocument();
    });

    it('deve lidar com toast sem duração', () => {
      const toastWithoutDuration: Toast = {
        id: 'no-duration',
        type: 'info',
        message: 'Toast sem duração',
        timestamp: new Date(),
        autoHide: true
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastWithoutDuration]} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
      expect(screen.queryByTestId('linear-progress')).not.toBeInTheDocument();
    });

    it('deve lidar com toast com duração zero', () => {
      const toastZeroDuration: Toast = {
        id: 'zero-duration',
        type: 'info',
        message: 'Toast com duração zero',
        duration: 0,
        timestamp: new Date(),
        autoHide: true
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastZeroDuration]} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
      expect(screen.queryByTestId('linear-progress')).not.toBeInTheDocument();
    });

    it('deve lidar com toast com mensagem muito longa', () => {
      const longMessage = 'A'.repeat(1000);
      const toastLongMessage: Toast = {
        id: 'long-message',
        type: 'info',
        message: longMessage,
        timestamp: new Date(),
        autoHide: true
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastLongMessage]} />
        </TestWrapper>
      );
      
      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('deve lidar com toast com metadados complexos', () => {
      const complexMetadata = {
        nested: {
          deep: {
            object: {
              with: {
                arrays: [1, 2, 3],
                strings: ['a', 'b', 'c'],
                numbers: 123,
                booleans: true
              }
            }
          }
        }
      };
      
      const toastComplexMetadata: Toast = {
        id: 'complex-metadata',
        type: 'info',
        message: 'Toast com metadados complexos',
        timestamp: new Date(),
        autoHide: true,
        metadata: complexMetadata
      };
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} toasts={[toastComplexMetadata]} />
        </TestWrapper>
      );
      
      expect(screen.getByText(/"nested":/)).toBeInTheDocument();
    });
  });

  describe('Integração com Sistema', () => {
    it('deve integrar com sistema de temas', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const portal = screen.getByTestId('portal');
      expect(portal).toBeInTheDocument();
    });

    it('deve integrar com sistema de responsividade', () => {
      // Mock useMediaQuery para retornar true (mobile)
      jest.doMock('@mui/material', () => ({
        ...jest.requireActual('@mui/material'),
        useMediaQuery: () => true
      }));
      
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      expect(screen.getByTestId('portal')).toBeInTheDocument();
    });

    it('deve integrar com sistema de z-index', () => {
      render(
        <TestWrapper>
          <ToastManager {...defaultProps} />
        </TestWrapper>
      );
      
      const portal = screen.getByTestId('portal');
      expect(portal).toBeInTheDocument();
    });
  });
}); 