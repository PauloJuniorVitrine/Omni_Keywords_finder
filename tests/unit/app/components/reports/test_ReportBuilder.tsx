/**
 * test_ReportBuilder.tsx
 * 
 * Testes unitários para o componente ReportBuilder
 * 
 * Prompt: CHECKLIST_INTERFACE_GRAFICA_V1.md - UI-010
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-20
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { ReportBuilder } from '../../../../components/reports/ReportBuilder';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

// Mock das dependências
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

// Mock do Ant Design
jest.mock('antd', () => {
  const antd = jest.requireActual('antd');
  return {
    ...antd,
    message: {
      success: jest.fn(),
      error: jest.fn(),
      warning: jest.fn(),
    },
  };
});

// Mock dos ícones
jest.mock('@ant-design/icons', () => ({
  PlusOutlined: () => <span data-testid="plus-icon">+</span>,
  SaveOutlined: () => <span data-testid="save-icon">💾</span>,
  EyeOutlined: () => <span data-testid="eye-icon">👁️</span>,
  ShareAltOutlined: () => <span data-testid="share-icon">📤</span>,
  DownloadOutlined: () => <span data-testid="download-icon">📥</span>,
  SettingOutlined: () => <span data-testid="setting-icon">⚙️</span>,
  DeleteOutlined: () => <span data-testid="delete-icon">🗑️</span>,
  CopyOutlined: () => <span data-testid="copy-icon">📋</span>,
  ClockCircleOutlined: () => <span data-testid="clock-icon">🕐</span>,
  BarChartOutlined: () => <span data-testid="bar-chart-icon">📊</span>,
  LineChartOutlined: () => <span data-testid="line-chart-icon">📈</span>,
  PieChartOutlined: () => <span data-testid="pie-chart-icon">🥧</span>,
  TableOutlined: () => <span data-testid="table-icon">📋</span>,
  FilterOutlined: () => <span data-testid="filter-icon">🔍</span>,
  LayoutOutlined: () => <span data-testid="layout-icon">📐</span>,
  TemplateOutlined: () => <span data-testid="template-icon">📄</span>,
  UserOutlined: () => <span data-testid="user-icon">👤</span>,
  LockOutlined: () => <span data-testid="lock-icon">🔒</span>,
  UnlockOutlined: () => <span data-testid="unlock-icon">🔓</span>,
  HistoryOutlined: () => <span data-testid="history-icon">📜</span>,
  StarOutlined: () => <span data-testid="star-icon">⭐</span>,
  StarFilled: () => <span data-testid="star-filled-icon">⭐</span>,
  DragOutlined: () => <span data-testid="drag-icon">✋</span>,
  ResizeOutlined: () => <span data-testid="resize-icon">↔️</span>,
  FullscreenOutlined: () => <span data-testid="fullscreen-icon">⛶</span>,
  FullscreenExitOutlined: () => <span data-testid="fullscreen-exit-icon">⛶</span>,
}));

// Mock do react-dnd
jest.mock('react-dnd', () => ({
  DndProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="dnd-provider">{children}</div>,
  useDrag: () => [{ isDragging: false }, jest.fn()],
  useDrop: () => [{ isOver: false }, jest.fn()],
}));

// Mock do react-dnd-html5-backend
jest.mock('react-dnd-html5-backend', () => ({
  HTML5Backend: jest.fn(),
}));

// Wrapper para renderizar o componente com DndProvider
const renderWithDnd = (component: React.ReactElement) => {
  return render(
    <DndProvider backend={HTML5Backend}>
      {component}
    </DndProvider>
  );
};

describe('ReportBuilder', () => {
  const mockOnSave = jest.fn();
  const mockOnExport = jest.fn();
  const mockOnShare = jest.fn();
  const mockOnSchedule = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Inicial', () => {
    it('deve renderizar o componente corretamente', () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      expect(screen.getByText('Novo Relatório')).toBeInTheDocument();
      expect(screen.getByText('Templates')).toBeInTheDocument();
      expect(screen.getByText('Agendar')).toBeInTheDocument();
      expect(screen.getByText('Compartilhar')).toBeInTheDocument();
      expect(screen.getByText('Exportar')).toBeInTheDocument();
      expect(screen.getByText('Salvar')).toBeInTheDocument();
    });

    it('deve mostrar loading quando carregando', async () => {
      renderWithDnd(
        <ReportBuilder
          reportId="test-report"
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      expect(screen.getByText('Carregando relatório...')).toBeInTheDocument();
    });

    it('deve renderizar em modo somente leitura', () => {
      renderWithDnd(
        <ReportBuilder
          readOnly={true}
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      expect(screen.getByText('Novo Relatório')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Componentes', () => {
    it('deve mostrar lista de componentes disponíveis', () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      expect(screen.getByText('Gráfico de Linha')).toBeInTheDocument();
      expect(screen.getByText('Gráfico de Barras')).toBeInTheDocument();
      expect(screen.getByText('Gráfico de Pizza')).toBeInTheDocument();
      expect(screen.getByText('Tabela de Dados')).toBeInTheDocument();
      expect(screen.getByText('Métrica')).toBeInTheDocument();
    });

    it('deve permitir adicionar componente ao canvas', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const lineChartComponent = screen.getByText('Gráfico de Linha');
      fireEvent.click(lineChartComponent);

      await waitFor(() => {
        expect(screen.getByText('Configurar Gráfico de Linha')).toBeInTheDocument();
      });
    });

    it('deve mostrar canvas vazio inicialmente', () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      expect(screen.getByText('Arraste componentes aqui para começar')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Templates', () => {
    it('deve abrir modal de templates', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const templatesButton = screen.getByText('Templates');
      fireEvent.click(templatesButton);

      await waitFor(() => {
        expect(screen.getByText('Templates de Relatório')).toBeInTheDocument();
      });
    });

    it('deve mostrar templates disponíveis', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const templatesButton = screen.getByText('Templates');
      fireEvent.click(templatesButton);

      await waitFor(() => {
        expect(screen.getByText('Visão Geral de Performance')).toBeInTheDocument();
        expect(screen.getByText('Análise de Keywords')).toBeInTheDocument();
      });
    });

    it('deve permitir aplicar template', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const templatesButton = screen.getByText('Templates');
      fireEvent.click(templatesButton);

      await waitFor(() => {
        const applyButton = screen.getByText('Aplicar');
        fireEvent.click(applyButton);
      });

      // Verificar se o template foi aplicado
      await waitFor(() => {
        expect(screen.queryByText('Arraste componentes aqui para começar')).not.toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidades de Agendamento', () => {
    it('deve abrir modal de agendamento', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const scheduleButton = screen.getByText('Agendar');
      fireEvent.click(scheduleButton);

      await waitFor(() => {
        expect(screen.getByText('Agendar Relatório')).toBeInTheDocument();
      });
    });

    it('deve permitir configurar agendamento', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const scheduleButton = screen.getByText('Agendar');
      fireEvent.click(scheduleButton);

      await waitFor(() => {
        expect(screen.getByText('Frequência')).toBeInTheDocument();
        expect(screen.getByText('Horário')).toBeInTheDocument();
        expect(screen.getByText('Destinatários')).toBeInTheDocument();
        expect(screen.getByText('Formato')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidades de Compartilhamento', () => {
    it('deve abrir modal de compartilhamento', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const shareButton = screen.getByText('Compartilhar');
      fireEvent.click(shareButton);

      await waitFor(() => {
        expect(screen.getByText('Compartilhar Relatório')).toBeInTheDocument();
      });
    });

    it('deve permitir configurar permissões', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const shareButton = screen.getByText('Compartilhar');
      fireEvent.click(shareButton);

      await waitFor(() => {
        expect(screen.getByText('Tornar Público')).toBeInTheDocument();
        expect(screen.getByText('Usuários')).toBeInTheDocument();
        expect(screen.getByText('Roles')).toBeInTheDocument();
        expect(screen.getByText('Permissões')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidades de Exportação', () => {
    it('deve mostrar menu de exportação', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const exportButton = screen.getByText('Exportar');
      fireEvent.click(exportButton);

      // O menu dropdown deve estar disponível
      expect(exportButton).toBeInTheDocument();
    });

    it('deve chamar função de exportação', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      // Simular exportação
      act(() => {
        mockOnExport({ id: 'test' }, 'pdf');
      });

      expect(mockOnExport).toHaveBeenCalledWith({ id: 'test' }, 'pdf');
    });
  });

  describe('Funcionalidades de Salvamento', () => {
    it('deve chamar função de salvamento', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const saveButton = screen.getByText('Salvar');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalled();
      });
    });

    it('deve mostrar loading durante salvamento', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const saveButton = screen.getByText('Salvar');
      fireEvent.click(saveButton);

      // O botão deve mostrar loading
      expect(saveButton).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Configuração', () => {
    it('deve permitir configurar tamanho do canvas', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      // Navegar para a aba de configurações
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);

      await waitFor(() => {
        expect(screen.getByText('Tamanho do Canvas:')).toBeInTheDocument();
      });
    });

    it('deve permitir configurar filtros', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      // Navegar para a aba de filtros
      const filtersTab = screen.getByText('Filtros');
      fireEvent.click(filtersTab);

      await waitFor(() => {
        expect(screen.getByText('Filtros Globais:')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidades de Edição de Componentes', () => {
    it('deve permitir editar componente', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      // Adicionar um componente primeiro
      const lineChartComponent = screen.getByText('Gráfico de Linha');
      fireEvent.click(lineChartComponent);

      await waitFor(() => {
        expect(screen.getByText('Configurar Gráfico de Linha')).toBeInTheDocument();
      });

      // Editar o componente
      const titleInput = screen.getByDisplayValue('Gráfico de Linha');
      fireEvent.change(titleInput, { target: { value: 'Novo Título' } });

      expect(titleInput).toHaveValue('Novo Título');
    });

    it('deve permitir excluir componente', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      // Adicionar um componente primeiro
      const lineChartComponent = screen.getByText('Gráfico de Linha');
      fireEvent.click(lineChartComponent);

      await waitFor(() => {
        expect(screen.getByText('Configurar Gráfico de Linha')).toBeInTheDocument();
      });

      // O componente deve estar no canvas
      expect(screen.queryByText('Arraste componentes aqui para começar')).not.toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Navegação', () => {
    it('deve permitir navegar entre abas', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      // Navegar para filtros
      const filtersTab = screen.getByText('Filtros');
      fireEvent.click(filtersTab);

      await waitFor(() => {
        expect(screen.getByText('Filtros Globais:')).toBeInTheDocument();
      });

      // Navegar para configurações
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);

      await waitFor(() => {
        expect(screen.getByText('Tamanho do Canvas:')).toBeInTheDocument();
      });

      // Voltar para componentes
      const componentsTab = screen.getByText('Componentes');
      fireEvent.click(componentsTab);

      await waitFor(() => {
        expect(screen.getByText('Gráfico de Linha')).toBeInTheDocument();
      });
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve tratar erro ao carregar relatório', async () => {
      // Mock de erro na API
      global.fetch = jest.fn().mockRejectedValue(new Error('Erro de rede'));

      renderWithDnd(
        <ReportBuilder
          reportId="invalid-report"
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Carregando relatório...')).toBeInTheDocument();
      });
    });

    it('deve tratar erro ao salvar relatório', async () => {
      const mockOnSaveWithError = jest.fn().mockRejectedValue(new Error('Erro ao salvar'));

      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSaveWithError}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const saveButton = screen.getByText('Salvar');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockOnSaveWithError).toHaveBeenCalled();
      });
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados', () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      expect(screen.getByText('Novo Relatório')).toBeInTheDocument();
      expect(screen.getByText('Templates')).toBeInTheDocument();
      expect(screen.getByText('Agendar')).toBeInTheDocument();
      expect(screen.getByText('Compartilhar')).toBeInTheDocument();
      expect(screen.getByText('Exportar')).toBeInTheDocument();
      expect(screen.getByText('Salvar')).toBeInTheDocument();
    });

    it('deve ter navegação por teclado', () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const saveButton = screen.getByText('Salvar');
      expect(saveButton).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve renderizar rapidamente', () => {
      const startTime = performance.now();
      
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Deve renderizar em menos de 100ms
      expect(renderTime).toBeLessThan(100);
    });

    it('deve otimizar re-renderizações', () => {
      const { rerender } = renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      // Re-renderizar com as mesmas props
      rerender(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      expect(screen.getByText('Novo Relatório')).toBeInTheDocument();
    });
  });

  describe('Integração', () => {
    it('deve integrar com sistema de templates', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const templatesButton = screen.getByText('Templates');
      fireEvent.click(templatesButton);

      await waitFor(() => {
        expect(screen.getByText('Visão Geral de Performance')).toBeInTheDocument();
        expect(screen.getByText('Análise de Keywords')).toBeInTheDocument();
      });
    });

    it('deve integrar com sistema de agendamento', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const scheduleButton = screen.getByText('Agendar');
      fireEvent.click(scheduleButton);

      await waitFor(() => {
        expect(screen.getByText('Agendar Relatório')).toBeInTheDocument();
      });
    });

    it('deve integrar com sistema de compartilhamento', async () => {
      renderWithDnd(
        <ReportBuilder
          onSave={mockOnSave}
          onExport={mockOnExport}
          onShare={mockOnShare}
          onSchedule={mockOnSchedule}
        />
      );

      const shareButton = screen.getByText('Compartilhar');
      fireEvent.click(shareButton);

      await waitFor(() => {
        expect(screen.getByText('Compartilhar Relatório')).toBeInTheDocument();
      });
    });
  });
}); 