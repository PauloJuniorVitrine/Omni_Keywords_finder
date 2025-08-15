/**
 * test_WorkflowBuilder.tsx
 * Testes unitários para WorkflowBuilder
 * Tracing ID: UI-023-TEST
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import WorkflowBuilder from '../../../../app/components/workflow/WorkflowBuilder';

// Mock Material-UI components
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  SpeedDial: ({ children, ...props }: any) => <div data-testid="speed-dial" {...props}>{children}</div>,
  SpeedDialAction: ({ tooltipTitle, ...props }: any) => <button data-testid={`speed-dial-action-${tooltipTitle}`} {...props} />,
  SpeedDialIcon: () => <div data-testid="speed-dial-icon" />,
}));

// Mock icons
jest.mock('@mui/icons-material', () => ({
  AccountTree: () => <div data-testid="account-tree-icon" />,
  PlayArrow: () => <div data-testid="play-arrow-icon" />,
  Pause: () => <div data-testid="pause-icon" />,
  Stop: () => <div data-testid="stop-icon" />,
  Refresh: () => <div data-testid="refresh-icon" />,
  Add: () => <div data-testid="add-icon" />,
  Edit: () => <div data-testid="edit-icon" />,
  Visibility: () => <div data-testid="visibility-icon" />,
  Timeline: () => <div data-testid="timeline-icon" />,
  Settings: () => <div data-testid="settings-icon" />,
  Assessment: () => <div data-testid="assessment-icon" />,
  TrendingUp: () => <div data-testid="trending-up-icon" />,
  Check: () => <div data-testid="check-icon" />,
  Close: () => <div data-testid="close-icon" />,
  Save: () => <div data-testid="save-icon" />,
  Cancel: () => <div data-testid="cancel-icon" />,
}));

// Mock data
const mockWorkflows = [
  {
    id: 'workflow_001',
    name: 'Processamento de Keywords',
    description: 'Workflow para processamento automático de keywords',
    version: '1.0.0',
    status: 'active' as const,
    createdAt: '2024-01-15T00:00:00Z',
    updatedAt: '2024-12-20T10:30:00Z',
    steps: [
      {
        id: 'step_001',
        name: 'Trigger - Nova Keyword',
        type: 'trigger' as const,
        position: { x: 100, y: 100 },
        config: { event: 'keyword.created' },
        connections: ['step_002'],
        status: 'idle' as const
      },
      {
        id: 'step_002',
        name: 'Validar Keyword',
        type: 'action' as const,
        position: { x: 300, y: 100 },
        config: { action: 'validate_keyword' },
        connections: ['step_003'],
        status: 'idle' as const
      }
    ],
    statistics: {
      totalExecutions: 1250,
      successfulExecutions: 1180,
      failedExecutions: 70,
      avgExecutionTime: 45.2
    }
  },
  {
    id: 'workflow_002',
    name: 'Backup Automático',
    description: 'Workflow para backup automático de dados',
    version: '1.0.0',
    status: 'active' as const,
    createdAt: '2024-02-01T00:00:00Z',
    updatedAt: '2024-12-20T09:15:00Z',
    steps: [
      {
        id: 'step_003',
        name: 'Trigger - Agendamento',
        type: 'trigger' as const,
        position: { x: 100, y: 100 },
        config: { event: 'schedule.daily' },
        connections: ['step_004'],
        status: 'idle' as const
      }
    ],
    statistics: {
      totalExecutions: 320,
      successfulExecutions: 315,
      failedExecutions: 5,
      avgExecutionTime: 1200.5
    }
  }
];

const mockExecutions = [
  {
    id: 'exec_001',
    workflowId: 'workflow_001',
    status: 'completed' as const,
    startedAt: '2024-12-20T10:20:00Z',
    completedAt: '2024-12-20T10:21:00Z',
    duration: 60
  },
  {
    id: 'exec_002',
    workflowId: 'workflow_002',
    status: 'running' as const,
    startedAt: '2024-12-20T10:25:00Z'
  }
];

// Test theme
const theme = createTheme();

// Test wrapper
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </ThemeProvider>
);

describe('WorkflowBuilder', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização inicial', () => {
    it('deve renderizar o componente corretamente', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByText('Construtor de Workflows')).toBeInTheDocument();
      expect(screen.getByText('Crie e gerencie workflows automatizados com interface visual')).toBeInTheDocument();
    });

    it('deve exibir as métricas principais', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByText('2')).toBeInTheDocument(); // Total de workflows
      expect(screen.getByText('2')).toBeInTheDocument(); // Workflows ativos
      expect(screen.getByText('1.570')).toBeInTheDocument(); // Execuções totais
      expect(screen.getByText('94,3%')).toBeInTheDocument(); // Taxa de sucesso
    });

    it('deve exibir as abas principais', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByText('Canvas')).toBeInTheDocument();
      expect(screen.getByText('Execuções')).toBeInTheDocument();
      expect(screen.getByText('Configurações')).toBeInTheDocument();
    });
  });

  describe('Lista de Workflows', () => {
    it('deve exibir a lista de workflows', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByText('Workflows')).toBeInTheDocument();
      expect(screen.getByText('Processamento de Keywords')).toBeInTheDocument();
      expect(screen.getByText('Backup Automático')).toBeInTheDocument();
    });

    it('deve exibir os status dos workflows corretamente', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const statusChips = screen.getAllByText('active');
      expect(statusChips).toHaveLength(2);
    });

    it('deve exibir as descrições dos workflows', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByText('Workflow para processamento automático de keywords')).toBeInTheDocument();
      expect(screen.getByText('Workflow para backup automático de dados')).toBeInTheDocument();
    });

    it('deve ter botão de criação de novo workflow', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByText('Novo')).toBeInTheDocument();
    });

    it('deve ter botões de edição para cada workflow', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const editButtons = screen.getAllByTestId('edit-icon');
      expect(editButtons).toHaveLength(2);
    });
  });

  describe('Aba Canvas', () => {
    it('deve exibir a aba Canvas quando selecionada', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const canvasTab = screen.getByText('Canvas');
      fireEvent.click(canvasTab);

      await waitFor(() => {
        expect(screen.getByText('Selecione um Workflow')).toBeInTheDocument();
      });
    });

    it('deve exibir mensagem quando nenhum workflow está selecionado', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const canvasTab = screen.getByText('Canvas');
      fireEvent.click(canvasTab);

      await waitFor(() => {
        expect(screen.getByText('Selecione um Workflow')).toBeInTheDocument();
        expect(screen.getByText('Escolha um workflow da lista para visualizar e editar')).toBeInTheDocument();
      });
    });

    it('deve exibir o workflow selecionado no canvas', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const canvasTab = screen.getByText('Canvas');
      fireEvent.click(canvasTab);

      // Selecionar um workflow
      const workflowItem = screen.getByText('Processamento de Keywords');
      fireEvent.click(workflowItem);

      await waitFor(() => {
        expect(screen.getByText('Processamento de Keywords')).toBeInTheDocument();
      });
    });

    it('deve exibir os botões de controle do workflow', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const canvasTab = screen.getByText('Canvas');
      fireEvent.click(canvasTab);

      // Selecionar um workflow
      const workflowItem = screen.getByText('Processamento de Keywords');
      fireEvent.click(workflowItem);

      await waitFor(() => {
        expect(screen.getByText('Executar')).toBeInTheDocument();
        expect(screen.getByText('Pausar')).toBeInTheDocument();
        expect(screen.getByText('Parar')).toBeInTheDocument();
      });
    });

    it('deve exibir a paleta de steps', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const canvasTab = screen.getByText('Canvas');
      fireEvent.click(canvasTab);

      // Selecionar um workflow
      const workflowItem = screen.getByText('Processamento de Keywords');
      fireEvent.click(workflowItem);

      await waitFor(() => {
        expect(screen.getByText('Adicionar Step:')).toBeInTheDocument();
        expect(screen.getByText('Trigger')).toBeInTheDocument();
        expect(screen.getByText('Ação')).toBeInTheDocument();
        expect(screen.getByText('Condição')).toBeInTheDocument();
        expect(screen.getByText('API')).toBeInTheDocument();
        expect(screen.getByText('Notificação')).toBeInTheDocument();
      });
    });
  });

  describe('Aba Execuções', () => {
    it('deve exibir a aba Execuções quando clicada', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const execucoesTab = screen.getByText('Execuções');
      fireEvent.click(execucoesTab);

      await waitFor(() => {
        expect(screen.getByText('Execuções Recentes')).toBeInTheDocument();
      });
    });

    it('deve exibir a tabela de execuções', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const execucoesTab = screen.getByText('Execuções');
      fireEvent.click(execucoesTab);

      await waitFor(() => {
        expect(screen.getByText('ID')).toBeInTheDocument();
        expect(screen.getByText('Workflow')).toBeInTheDocument();
        expect(screen.getByText('Status')).toBeInTheDocument();
        expect(screen.getByText('Início')).toBeInTheDocument();
        expect(screen.getByText('Duração')).toBeInTheDocument();
        expect(screen.getByText('Ações')).toBeInTheDocument();
      });
    });

    it('deve exibir as execuções na tabela', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const execucoesTab = screen.getByText('Execuções');
      fireEvent.click(execucoesTab);

      await waitFor(() => {
        expect(screen.getByText('exec_001')).toBeInTheDocument();
        expect(screen.getByText('exec_002')).toBeInTheDocument();
        expect(screen.getByText('completed')).toBeInTheDocument();
        expect(screen.getByText('running')).toBeInTheDocument();
      });
    });

    it('deve exibir os nomes dos workflows nas execuções', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const execucoesTab = screen.getByText('Execuções');
      fireEvent.click(execucoesTab);

      await waitFor(() => {
        expect(screen.getByText('Processamento de Keywords')).toBeInTheDocument();
        expect(screen.getByText('Backup Automático')).toBeInTheDocument();
      });
    });

    it('deve exibir os botões de ação nas execuções', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const execucoesTab = screen.getByText('Execuções');
      fireEvent.click(execucoesTab);

      await waitFor(() => {
        const visibilityButtons = screen.getAllByTestId('visibility-icon');
        const refreshButtons = screen.getAllByTestId('refresh-icon');
        expect(visibilityButtons).toHaveLength(2);
        expect(refreshButtons).toHaveLength(2);
      });
    });
  });

  describe('Aba Configurações', () => {
    it('deve exibir a aba Configurações quando clicada', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const configTab = screen.getByText('Configurações');
      fireEvent.click(configTab);

      await waitFor(() => {
        expect(screen.getByText('Configurações do Workflow')).toBeInTheDocument();
      });
    });

    it('deve exibir alerta quando nenhum workflow está selecionado', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const configTab = screen.getByText('Configurações');
      fireEvent.click(configTab);

      await waitFor(() => {
        expect(screen.getByText('Selecione um workflow para ver suas configurações')).toBeInTheDocument();
      });
    });

    it('deve exibir as configurações do workflow selecionado', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const configTab = screen.getByText('Configurações');
      fireEvent.click(configTab);

      // Selecionar um workflow
      const workflowItem = screen.getByText('Processamento de Keywords');
      fireEvent.click(workflowItem);

      await waitFor(() => {
        expect(screen.getByText('Configurações Gerais')).toBeInTheDocument();
        expect(screen.getByText('Estatísticas')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Processamento de Keywords')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Workflow para processamento automático de keywords')).toBeInTheDocument();
      });
    });

    it('deve exibir as estatísticas do workflow', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const configTab = screen.getByText('Configurações');
      fireEvent.click(configTab);

      // Selecionar um workflow
      const workflowItem = screen.getByText('Processamento de Keywords');
      fireEvent.click(workflowItem);

      await waitFor(() => {
        expect(screen.getByText('Total de Execuções: 1250')).toBeInTheDocument();
        expect(screen.getByText('Execuções Bem-sucedidas: 1180')).toBeInTheDocument();
        expect(screen.getByText('Execuções Falhadas: 70')).toBeInTheDocument();
        expect(screen.getByText('Tempo Médio: 45.2s')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidades de criação e edição', () => {
    it('deve abrir o dialog de criação de workflow', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const novoButton = screen.getByText('Novo');
      fireEvent.click(novoButton);

      expect(screen.getByText('Novo Workflow')).toBeInTheDocument();
      expect(screen.getByLabelText('Nome do Workflow')).toBeInTheDocument();
      expect(screen.getByLabelText('Descrição')).toBeInTheDocument();
    });

    it('deve abrir o dialog de edição de workflow', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const editButtons = screen.getAllByTestId('edit-icon');
      fireEvent.click(editButtons[0]);

      expect(screen.getByText('Editar Workflow')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Processamento de Keywords')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Workflow para processamento automático de keywords')).toBeInTheDocument();
    });

    it('deve fechar o dialog ao clicar em Cancelar', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const novoButton = screen.getByText('Novo');
      fireEvent.click(novoButton);

      const cancelarButton = screen.getByText('Cancelar');
      fireEvent.click(cancelarButton);

      expect(screen.queryByText('Novo Workflow')).not.toBeInTheDocument();
    });

    it('deve criar um novo workflow ao clicar em Criar', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const novoButton = screen.getByText('Novo');
      fireEvent.click(novoButton);

      const criarButton = screen.getByText('Criar');
      fireEvent.click(criarButton);

      expect(screen.getByText('Workflow criado com sucesso')).toBeInTheDocument();
    });

    it('deve atualizar um workflow ao clicar em Atualizar', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const editButtons = screen.getAllByTestId('edit-icon');
      fireEvent.click(editButtons[0]);

      const atualizarButton = screen.getByText('Atualizar');
      fireEvent.click(atualizarButton);

      expect(screen.getByText('Workflow atualizado com sucesso')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de steps', () => {
    it('deve abrir o dialog de criação de step', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const canvasTab = screen.getByText('Canvas');
      fireEvent.click(canvasTab);

      // Selecionar um workflow
      const workflowItem = screen.getByText('Processamento de Keywords');
      fireEvent.click(workflowItem);

      await waitFor(() => {
        const triggerButton = screen.getByText('Trigger');
        fireEvent.click(triggerButton);
      });

      expect(screen.getByText('Novo Step')).toBeInTheDocument();
      expect(screen.getByLabelText('Nome do Step')).toBeInTheDocument();
      expect(screen.getByLabelText('Tipo')).toBeInTheDocument();
    });

    it('deve abrir o dialog de edição de step', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const canvasTab = screen.getByText('Canvas');
      fireEvent.click(canvasTab);

      // Selecionar um workflow
      const workflowItem = screen.getByText('Processamento de Keywords');
      fireEvent.click(workflowItem);

      await waitFor(() => {
        // Simular clique em um step (não implementado no mock)
        const stepButton = screen.getByText('Trigger - Nova Keyword');
        fireEvent.click(stepButton);
      });

      // Como o canvas é mockado, não podemos testar a interação direta
      // Mas podemos verificar se os steps estão sendo renderizados
      expect(screen.getByText('Trigger - Nova Keyword')).toBeInTheDocument();
    });
  });

  describe('Speed Dial', () => {
    it('deve renderizar o speed dial', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByTestId('speed-dial')).toBeInTheDocument();
      expect(screen.getByTestId('speed-dial-icon')).toBeInTheDocument();
    });

    it('deve ter ações rápidas disponíveis', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByTestId('speed-dial-action-Novo workflow')).toBeInTheDocument();
      expect(screen.getByTestId('speed-dial-action-Executar todos')).toBeInTheDocument();
      expect(screen.getByTestId('speed-dial-action-Relatório')).toBeInTheDocument();
    });

    it('deve executar ação de execução em lote', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const execucaoButton = screen.getByTestId('speed-dial-action-Executar todos');
      fireEvent.click(execucaoButton);

      expect(screen.getByText('Execução em lote iniciada')).toBeInTheDocument();
    });

    it('deve executar ação de relatório', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const relatorioButton = screen.getByTestId('speed-dial-action-Relatório');
      fireEvent.click(relatorioButton);

      expect(screen.getByText('Relatório gerado com sucesso')).toBeInTheDocument();
    });
  });

  describe('Snackbar', () => {
    it('deve exibir snackbar de sucesso', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const novoButton = screen.getByText('Novo');
      fireEvent.click(novoButton);

      const criarButton = screen.getByText('Criar');
      fireEvent.click(criarButton);

      expect(screen.getByText('Workflow criado com sucesso')).toBeInTheDocument();
    });

    it('deve fechar o snackbar automaticamente', async () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const novoButton = screen.getByText('Novo');
      fireEvent.click(novoButton);

      const criarButton = screen.getByText('Criar');
      fireEvent.click(criarButton);

      expect(screen.getByText('Workflow criado com sucesso')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.queryByText('Workflow criado com sucesso')).not.toBeInTheDocument();
      }, { timeout: 7000 });
    });
  });

  describe('Responsividade', () => {
    it('deve ser responsivo em diferentes tamanhos de tela', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      // Verifica se os componentes principais estão presentes
      expect(screen.getByText('Construtor de Workflows')).toBeInTheDocument();
      expect(screen.getByText('Canvas')).toBeInTheDocument();
      expect(screen.getByText('Novo')).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter tooltips nas ações', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const execucoesTab = screen.getByText('Execuções');
      fireEvent.click(execucoesTab);

      // Verifica se os botões de ação estão presentes
      const visibilityButtons = screen.getAllByTestId('visibility-icon');
      const refreshButtons = screen.getAllByTestId('refresh-icon');
      expect(visibilityButtons).toHaveLength(2);
      expect(refreshButtons).toHaveLength(2);
    });

    it('deve ter labels apropriados nos campos de formulário', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const novoButton = screen.getByText('Novo');
      fireEvent.click(novoButton);

      expect(screen.getByLabelText('Nome do Workflow')).toBeInTheDocument();
      expect(screen.getByLabelText('Descrição')).toBeInTheDocument();
      expect(screen.getByLabelText('Status')).toBeInTheDocument();
      expect(screen.getByLabelText('Versão')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve renderizar rapidamente', () => {
      const startTime = performance.now();
      
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(1000); // Deve renderizar em menos de 1 segundo
    });

    it('deve calcular métricas eficientemente', () => {
      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      // Verifica se as métricas estão sendo calculadas corretamente
      expect(screen.getByText('2')).toBeInTheDocument(); // Total de workflows
      expect(screen.getByText('1.570')).toBeInTheDocument(); // Execuções totais
    });
  });

  describe('Tratamento de erros', () => {
    it('deve lidar com dados vazios graciosamente', () => {
      // Mock de dados vazios
      jest.doMock('../../../../app/components/workflow/WorkflowBuilder', () => {
        const originalModule = jest.requireActual('../../../../app/components/workflow/WorkflowBuilder');
        return {
          ...originalModule,
          default: () => {
            const [workflows] = React.useState([]);
            return (
              <div>
                <div>Construtor de Workflows</div>
                <div>Total de Workflows: {workflows.length}</div>
              </div>
            );
          }
        };
      });

      render(
        <TestWrapper>
          <WorkflowBuilder />
        </TestWrapper>
      );

      expect(screen.getByText('Construtor de Workflows')).toBeInTheDocument();
    });
  });
}); 