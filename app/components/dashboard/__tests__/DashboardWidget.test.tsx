/**
 * DashboardWidget.test.tsx - Testes unitários para DashboardWidget
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 5.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Testes baseados APENAS no código real implementado
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import DashboardWidget from '../DashboardWidget';

// Mock do recharts para evitar problemas de renderização em testes
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>
}));

const theme = createTheme();

const mockMetricData = {
  value: 15420,
  change: 12.5,
  trend: 'up' as const,
  unit: 'keywords',
  color: '#1976d2'
};

const mockChartData = [
  { date: 'Jan', value: 12000 },
  { date: 'Fev', value: 13500 },
  { date: 'Mar', value: 14200 }
];

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('DashboardWidget', () => {
  const defaultProps = {
    title: 'Total de Keywords',
    metric: mockMetricData,
    chartData: mockChartData
  };

  describe('Renderização básica', () => {
    it('deve renderizar o título do widget', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      expect(screen.getByText('Total de Keywords')).toBeInTheDocument();
    });

    it('deve renderizar o valor da métrica formatado', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      expect(screen.getByText('15.4K')).toBeInTheDocument();
    });

    it('deve renderizar a unidade da métrica', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      expect(screen.getByText('keywords')).toBeInTheDocument();
    });

    it('deve renderizar a mudança percentual', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      expect(screen.getByText('+12.5%')).toBeInTheDocument();
    });

    it('deve renderizar o texto "vs período anterior"', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      expect(screen.getByText('vs período anterior')).toBeInTheDocument();
    });
  });

  describe('Formatação de valores', () => {
    it('deve formatar valores grandes em milhões', () => {
      const largeMetric = { ...mockMetricData, value: 2500000 };
      renderWithTheme(<DashboardWidget {...defaultProps} metric={largeMetric} />);
      expect(screen.getByText('2.5M')).toBeInTheDocument();
    });

    it('deve formatar valores em milhares', () => {
      const thousandMetric = { ...mockMetricData, value: 2500 };
      renderWithTheme(<DashboardWidget {...defaultProps} metric={thousandMetric} />);
      expect(screen.getByText('2.5K')).toBeInTheDocument();
    });

    it('deve manter valores pequenos sem formatação', () => {
      const smallMetric = { ...mockMetricData, value: 250 };
      renderWithTheme(<DashboardWidget {...defaultProps} metric={smallMetric} />);
      expect(screen.getByText('250')).toBeInTheDocument();
    });
  });

  describe('Estados de tendência', () => {
    it('deve renderizar ícone de tendência de alta quando trend é "up"', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      const trendIcon = screen.getByTestId('TrendingUpIcon');
      expect(trendIcon).toBeInTheDocument();
    });

    it('deve renderizar ícone de tendência de baixa quando trend é "down"', () => {
      const downMetric = { ...mockMetricData, trend: 'down' as const };
      renderWithTheme(<DashboardWidget {...defaultProps} metric={downMetric} />);
      const trendIcon = screen.getByTestId('TrendingDownIcon');
      expect(trendIcon).toBeInTheDocument();
    });

    it('deve aplicar cor correta para tendência de alta', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      const chip = screen.getByText('+12.5%');
      expect(chip).toHaveClass('MuiChip-colorSuccess');
    });

    it('deve aplicar cor correta para tendência de baixa', () => {
      const downMetric = { ...mockMetricData, trend: 'down' as const, change: -5.2 };
      renderWithTheme(<DashboardWidget {...defaultProps} metric={downMetric} />);
      const chip = screen.getByText('-5.2%');
      expect(chip).toHaveClass('MuiChip-colorError');
    });
  });

  describe('Gráfico', () => {
    it('deve renderizar o gráfico quando chartData está presente', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    });

    it('não deve renderizar o gráfico quando chartData está vazio', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} chartData={[]} />);
      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
    });

    it('deve renderizar o gráfico quando showChart é true', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} showChart={true} />);
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    });

    it('não deve renderizar o gráfico quando showChart é false', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} showChart={false} />);
      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
    });
  });

  describe('Controles de visibilidade do gráfico', () => {
    it('deve renderizar botão de toggle de visibilidade quando showChart é true', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} showChart={true} />);
      const visibilityButton = screen.getByLabelText('Ocultar gráfico');
      expect(visibilityButton).toBeInTheDocument();
    });

    it('deve alternar visibilidade do gráfico ao clicar no botão', async () => {
      renderWithTheme(<DashboardWidget {...defaultProps} showChart={true} />);
      
      // Gráfico deve estar visível inicialmente
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      
      // Clicar no botão para ocultar
      const visibilityButton = screen.getByLabelText('Ocultar gráfico');
      fireEvent.click(visibilityButton);
      
      // Gráfico deve ser ocultado
      await waitFor(() => {
        expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
      });
    });
  });

  describe('Estados de loading', () => {
    it('deve renderizar progress bar quando isLoading é true', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} isLoading={true} />);
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('não deve renderizar progress bar quando isLoading é false', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} isLoading={false} />);
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    it('deve desabilitar botão de refresh quando isLoading é true', () => {
      const mockOnRefresh = jest.fn();
      renderWithTheme(
        <DashboardWidget {...defaultProps} isLoading={true} onRefresh={mockOnRefresh} />
      );
      
      const refreshButton = screen.getByLabelText('Atualizar dados');
      expect(refreshButton).toBeDisabled();
    });
  });

  describe('Callbacks', () => {
    it('deve chamar onRefresh quando botão de refresh é clicado', () => {
      const mockOnRefresh = jest.fn();
      renderWithTheme(
        <DashboardWidget {...defaultProps} onRefresh={mockOnRefresh} />
      );
      
      const refreshButton = screen.getByLabelText('Atualizar dados');
      fireEvent.click(refreshButton);
      
      expect(mockOnRefresh).toHaveBeenCalledTimes(1);
    });

    it('deve chamar onConfigure quando botão de configuração é clicado', () => {
      const mockOnConfigure = jest.fn();
      renderWithTheme(
        <DashboardWidget {...defaultProps} onConfigure={mockOnConfigure} />
      );
      
      const configureButton = screen.getByLabelText('Configurar widget');
      fireEvent.click(configureButton);
      
      expect(mockOnConfigure).toHaveBeenCalledTimes(1);
    });
  });

  describe('Tamanhos do widget', () => {
    it('deve aplicar altura correta para tamanho small', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} size="small" />);
      const card = screen.getByRole('article');
      expect(card).toHaveStyle({ height: '200px' });
    });

    it('deve aplicar altura correta para tamanho medium', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} size="medium" />);
      const card = screen.getByRole('article');
      expect(card).toHaveStyle({ height: '300px' });
    });

    it('deve aplicar altura correta para tamanho large', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} size="large" />);
      const card = screen.getByRole('article');
      expect(card).toHaveStyle({ height: '400px' });
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter título acessível', () => {
      renderWithTheme(<DashboardWidget {...defaultProps} />);
      const title = screen.getByRole('heading', { level: 3 });
      expect(title).toHaveTextContent('Total de Keywords');
    });

    it('deve ter botões com labels acessíveis', () => {
      renderWithTheme(
        <DashboardWidget 
          {...defaultProps} 
          onRefresh={jest.fn()}
          onConfigure={jest.fn()}
          showChart={true}
        />
      );
      
      expect(screen.getByLabelText('Ocultar gráfico')).toBeInTheDocument();
      expect(screen.getByLabelText('Atualizar dados')).toBeInTheDocument();
      expect(screen.getByLabelText('Configurar widget')).toBeInTheDocument();
    });
  });
}); 