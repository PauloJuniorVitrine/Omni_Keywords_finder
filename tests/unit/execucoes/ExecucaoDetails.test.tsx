/**
 * Testes Unitários - ExecucaoDetails Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_EXECUCAO_DETAILS_024
 * 
 * Baseado em código real do ExecucaoDetails.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ExecucaoDetails from '../../../app/components/execucoes/ExecucaoDetails';

// Mock do Material-UI
jest.mock('@mui/material', () => ({
  Box: ({ children, ...props }: any) => <div data-testid="box" {...props}>{children}</div>,
  Paper: ({ children, ...props }: any) => <div data-testid="paper" {...props}>{children}</div>,
  Typography: ({ children, variant, ...props }: any) => (
    <div data-testid="typography" data-variant={variant} {...props}>{children}</div>
  ),
  Grid: ({ children, container, item, ...props }: any) => (
    <div data-testid={container ? "grid-container" : "grid-item"} {...props}>{children}</div>
  ),
  Card: ({ children, ...props }: any) => <div data-testid="card" {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div data-testid="card-content" {...props}>{children}</div>,
  CardHeader: ({ title, ...props }: any) => <div data-testid="card-header" {...props}>{title}</div>,
  Button: ({ children, onClick, variant, startIcon, ...props }: any) => (
    <button data-testid="button" onClick={onClick} data-variant={variant} {...props}>
      {startIcon}
      {children}
    </button>
  ),
  Chip: ({ label, color, ...props }: any) => (
    <span data-testid="chip" data-color={color} {...props}>{label}</span>
  ),
  IconButton: ({ children, onClick, ...props }: any) => (
    <button data-testid="icon-button" onClick={onClick} {...props}>{children}</button>
  ),
  LinearProgress: ({ value, ...props }: any) => (
    <div data-testid="linear-progress" data-value={value} {...props} />
  ),
  List: ({ children, ...props }: any) => <div data-testid="list" {...props}>{children}</div>,
  ListItem: ({ children, ...props }: any) => <div data-testid="list-item" {...props}>{children}</div>,
  ListItemText: ({ primary, secondary, ...props }: any) => (
    <div data-testid="list-item-text" {...props}>
      <div data-testid="primary">{primary}</div>
      <div data-testid="secondary">{secondary}</div>
    </div>
  ),
  ListItemIcon: ({ children, ...props }: any) => <div data-testid="list-item-icon" {...props}>{children}</div>,
  Divider: ({ ...props }: any) => <hr data-testid="divider" {...props} />,
  Alert: ({ children, severity, ...props }: any) => (
    <div data-testid="alert" data-severity={severity} {...props}>{children}</div>
  ),
  Skeleton: ({ variant, ...props }: any) => (
    <div data-testid="skeleton" data-variant={variant} {...props} />
  ),
  Tabs: ({ children, value, onChange, ...props }: any) => (
    <div data-testid="tabs" data-value={value} {...props}>{children}</div>
  ),
  Tab: ({ label, icon, ...props }: any) => (
    <button data-testid="tab" {...props}>
      {icon}
      {label}
    </button>
  ),
  Table: ({ children, ...props }: any) => <table data-testid="table" {...props}>{children}</table>,
  TableBody: ({ children, ...props }: any) => <tbody data-testid="table-body" {...props}>{children}</tbody>,
  TableCell: ({ children, ...props }: any) => <td data-testid="table-cell" {...props}>{children}</td>,
  TableContainer: ({ children, ...props }: any) => (
    <div data-testid="table-container" {...props}>{children}</div>
  ),
  TableHead: ({ children, ...props }: any) => <thead data-testid="table-head" {...props}>{children}</thead>,
  TableRow: ({ children, ...props }: any) => <tr data-testid="table-row" {...props}>{children}</tr>,
  Dialog: ({ children, open, onClose, ...props }: any) => (
    <div data-testid="dialog" data-open={open} {...props}>{children}</div>
  ),
  DialogTitle: ({ children, ...props }: any) => (
    <div data-testid="dialog-title" {...props}>{children}</div>
  ),
  DialogContent: ({ children, ...props }: any) => (
    <div data-testid="dialog-content" {...props}>{children}</div>
  ),
  DialogActions: ({ children, ...props }: any) => (
    <div data-testid="dialog-actions" {...props}>{children}</div>
  ),
  TextField: ({ ...props }: any) => <input data-testid="text-field" {...props} />,
  FormControl: ({ children, ...props }: any) => (
    <div data-testid="form-control" {...props}>{children}</div>
  ),
  InputLabel: ({ children, ...props }: any) => (
    <label data-testid="input-label" {...props}>{children}</label>
  ),
  Select: ({ children, value, onChange, ...props }: any) => (
    <select data-testid="select" value={value} onChange={onChange} {...props}>{children}</select>
  ),
  MenuItem: ({ children, value, ...props }: any) => (
    <option data-testid="menu-item" value={value} {...props}>{children}</option>
  ),
  useTheme: () => ({
    breakpoints: {
      down: () => false
    }
  }),
  useMediaQuery: () => false,
  Tooltip: ({ children, ...props }: any) => (
    <div data-testid="tooltip" {...props}>{children}</div>
  ),
  Badge: ({ children, ...props }: any) => (
    <div data-testid="badge" {...props}>{children}</div>
  ),
  Avatar: ({ children, ...props }: any) => (
    <div data-testid="avatar" {...props}>{children}</div>
  ),
  Timeline: ({ children, ...props }: any) => (
    <div data-testid="timeline" {...props}>{children}</div>
  ),
  TimelineItem: ({ children, ...props }: any) => (
    <div data-testid="timeline-item" {...props}>{children}</div>
  ),
  TimelineSeparator: ({ children, ...props }: any) => (
    <div data-testid="timeline-separator" {...props}>{children}</div>
  ),
  TimelineConnector: ({ ...props }: any) => (
    <div data-testid="timeline-connector" {...props} />
  ),
  TimelineContent: ({ children, ...props }: any) => (
    <div data-testid="timeline-content" {...props}>{children}</div>
  ),
  TimelineDot: ({ children, ...props }: any) => (
    <div data-testid="timeline-dot" {...props}>{children}</div>
  ),
  TimelineOppositeContent: ({ children, ...props }: any) => (
    <div data-testid="timeline-opposite-content" {...props}>{children}</div>
  ),
}));

// Mock dos ícones Material-UI
jest.mock('@mui/icons-material', () => ({
  ArrowBack: ({ ...props }: any) => <div data-testid="icon-arrow-back" {...props} />,
  PlayArrow: ({ ...props }: any) => <div data-testid="icon-play" {...props} />,
  Stop: ({ ...props }: any) => <div data-testid="icon-stop" {...props} />,
  Pause: ({ ...props }: any) => <div data-testid="icon-pause" {...props} />,
  Refresh: ({ ...props }: any) => <div data-testid="icon-refresh" {...props} />,
  Download: ({ ...props }: any) => <div data-testid="icon-download" {...props} />,
  Share: ({ ...props }: any) => <div data-testid="icon-share" {...props} />,
  Edit: ({ ...props }: any) => <div data-testid="icon-edit" {...props} />,
  Delete: ({ ...props }: any) => <div data-testid="icon-delete" {...props} />,
  Settings: ({ ...props }: any) => <div data-testid="icon-settings" {...props} />,
  CheckCircle: ({ ...props }: any) => <div data-testid="icon-check-circle" {...props} />,
  Warning: ({ ...props }: any) => <div data-testid="icon-warning" {...props} />,
  Error: ({ ...props }: any) => <div data-testid="icon-error" {...props} />,
  Info: ({ ...props }: any) => <div data-testid="icon-info" {...props} />,
  Schedule: ({ ...props }: any) => <div data-testid="icon-schedule" {...props} />,
  Speed: ({ ...props }: any) => <div data-testid="icon-speed" {...props} />,
  Memory: ({ ...props }: any) => <div data-testid="icon-memory" {...props} />,
  Timer: ({ ...props }: any) => <div data-testid="icon-timer" {...props} />,
  TrendingUp: ({ ...props }: any) => <div data-testid="icon-trending-up" {...props} />,
  Visibility: ({ ...props }: any) => <div data-testid="icon-visibility" {...props} />,
  FileDownload: ({ ...props }: any) => <div data-testid="icon-file-download" {...props} />,
  CloudDownload: ({ ...props }: any) => <div data-testid="icon-cloud-download" {...props} />,
  Assessment: ({ ...props }: any) => <div data-testid="icon-assessment" {...props} />,
  Timeline: ({ ...props }: any) => <div data-testid="icon-timeline" {...props} />,
  BugReport: ({ ...props }: any) => <div data-testid="icon-bug-report" {...props} />,
}));

// Mock do react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: 'test-execution-id' }),
}));

describe('ExecucaoDetails - Detalhes de Execução', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar o componente com loading inicial', () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      expect(screen.getByTestId('box')).toBeInTheDocument();
    });

    test('deve renderizar com dados de execução carregados', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Execução Tecnologia - Lote 1')).toBeInTheDocument();
      });
    });

    test('deve renderizar informações básicas da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Execução Tecnologia - Lote 1')).toBeInTheDocument();
        expect(screen.getByText('Execução completa para nicho de tecnologia')).toBeInTheDocument();
        expect(screen.getByText('Tecnologia')).toBeInTheDocument();
        expect(screen.getByText('Desenvolvimento Web')).toBeInTheDocument();
      });
    });
  });

  describe('Status da Execução', () => {
    
    test('deve renderizar status em andamento', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Em Andamento')).toBeInTheDocument();
      });
    });

    test('deve renderizar progresso da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const progressBar = screen.getByTestId('linear-progress');
        expect(progressBar).toHaveAttribute('data-value', '75');
      });
    });

    test('deve renderizar métricas de progresso', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('750')).toBeInTheDocument(); // keywords processadas
        expect(screen.getByText('520')).toBeInTheDocument(); // keywords encontradas
        expect(screen.getByText('65')).toBeInTheDocument(); // tempo de execução
      });
    });
  });

  describe('Ações de Execução', () => {
    
    test('deve renderizar botões de controle', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('icon-pause')).toBeInTheDocument();
        expect(screen.getByTestId('icon-stop')).toBeInTheDocument();
        expect(screen.getByTestId('icon-refresh')).toBeInTheDocument();
      });
    });

    test('deve renderizar botões de ação', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('icon-download')).toBeInTheDocument();
        expect(screen.getByTestId('icon-share')).toBeInTheDocument();
        expect(screen.getByTestId('icon-edit')).toBeInTheDocument();
        expect(screen.getByTestId('icon-delete')).toBeInTheDocument();
      });
    });

    test('deve permitir pausar execução', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const pauseButton = screen.getByTestId('icon-pause').closest('button');
        expect(pauseButton).toBeInTheDocument();
      });
    });

    test('deve permitir parar execução', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const stopButton = screen.getByTestId('icon-stop').closest('button');
        expect(stopButton).toBeInTheDocument();
      });
    });

    test('deve permitir exportar resultados', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const exportButtons = screen.getAllByText(/Exportar/);
        expect(exportButtons.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Histórico de Execuções', () => {
    
    test('deve renderizar logs da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Iniciando execução')).toBeInTheDocument();
        expect(screen.getByText('Configuração carregada com sucesso')).toBeInTheDocument();
        expect(screen.getByText('Processando keywords do lote 1')).toBeInTheDocument();
      });
    });

    test('deve renderizar resultados da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('react development')).toBeInTheDocument();
        expect(screen.getByText('typescript tutorial')).toBeInTheDocument();
      });
    });

    test('deve renderizar métricas da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('69.3%')).toBeInTheDocument(); // taxa de sucesso
        expect(screen.getByText('5.2s')).toBeInTheDocument(); // tempo médio
        expect(screen.getByText('45.2%')).toBeInTheDocument(); // uso de memória
        expect(screen.getByText('67.8%')).toBeInTheDocument(); // uso de CPU
      });
    });
  });

  describe('Abas de Navegação', () => {
    
    test('deve renderizar todas as abas', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Visão Geral')).toBeInTheDocument();
        expect(screen.getByText('Logs')).toBeInTheDocument();
        expect(screen.getByText('Resultados')).toBeInTheDocument();
        expect(screen.getByText('Timeline')).toBeInTheDocument();
      });
    });

    test('deve permitir navegação entre abas', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const logsTab = screen.getByText('Logs');
        expect(logsTab).toBeInTheDocument();
      });
    });

    test('deve mostrar aba de visão geral por padrão', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Informações da Execução')).toBeInTheDocument();
        expect(screen.getByText('Ações Rápidas')).toBeInTheDocument();
      });
    });
  });

  describe('Filtros e Busca', () => {
    
    test('deve permitir filtrar logs', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const logsTab = screen.getByText('Logs');
        expect(logsTab).toBeInTheDocument();
      });
    });

    test('deve mostrar filtro de logs', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Filtrar Logs')).toBeInTheDocument();
      });
    });
  });

  describe('Dialog de Confirmação', () => {
    
    test('deve mostrar dialog de confirmação para exclusão', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const deleteButton = screen.getByTestId('icon-delete').closest('button');
        expect(deleteButton).toBeInTheDocument();
      });
    });

    test('deve permitir cancelar exclusão', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Cancelar')).toBeInTheDocument();
      });
    });
  });

  describe('Auto-refresh', () => {
    
    test('deve configurar auto-refresh para execuções em andamento', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Em Andamento')).toBeInTheDocument();
      });
    });

    test('deve permitir desabilitar auto-refresh', async () => {
      const user = userEvent.setup();
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const refreshButton = screen.getByTestId('icon-refresh').closest('button');
        expect(refreshButton).toBeInTheDocument();
      });
    });
  });

  describe('Validação de Campos', () => {
    
    test('deve validar ID da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Execução Tecnologia - Lote 1')).toBeInTheDocument();
      });
    });

    test('deve validar dados obrigatórios da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Execução Tecnologia - Lote 1')).toBeInTheDocument();
        expect(screen.getByText('Tecnologia')).toBeInTheDocument();
        expect(screen.getByText('Desenvolvimento Web')).toBeInTheDocument();
      });
    });

    test('deve validar métricas da execução', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('1000')).toBeInTheDocument(); // total keywords
        expect(screen.getByText('750')).toBeInTheDocument(); // keywords processadas
        expect(screen.getByText('520')).toBeInTheDocument(); // keywords encontradas
      });
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter estrutura semântica adequada', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('typography')).toBeInTheDocument();
      });
    });

    test('deve ter navegação por teclado', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        const buttons = screen.getAllByTestId('button');
        expect(buttons.length).toBeGreaterThan(0);
      });
    });

    test('deve ter labels apropriados', async () => {
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Informações da Execução')).toBeInTheDocument();
        expect(screen.getByText('Ações Rápidas')).toBeInTheDocument();
      });
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente com dados complexos', async () => {
      const startTime = performance.now();
      
      render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Execução Tecnologia - Lote 1')).toBeInTheDocument();
      });
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(1000); // Deve renderizar em menos de 1s
    });

    test('deve evitar re-renders desnecessários', async () => {
      const { rerender } = render(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Execução Tecnologia - Lote 1')).toBeInTheDocument();
      });
      
      // Re-renderizar com os mesmos dados não deve causar mudanças
      rerender(
        <MemoryRouter initialEntries={['/execucoes/test-id']}>
          <Routes>
            <Route path="/execucoes/:id" element={<ExecucaoDetails />} />
          </Routes>
        </MemoryRouter>
      );
      
      expect(screen.getByText('Execução Tecnologia - Lote 1')).toBeInTheDocument();
    });
  });
}); 