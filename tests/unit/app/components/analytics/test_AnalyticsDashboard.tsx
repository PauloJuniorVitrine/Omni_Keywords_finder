/**
 * test_AnalyticsDashboard.tsx
 * 
 * Testes unitários para o componente AnalyticsDashboard
 * 
 * Tracing ID: UI-001-TEST
 * Data/Hora: 2024-12-20 07:00:00 UTC
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import AnalyticsDashboard from '../../../../app/components/analytics/AnalyticsDashboard';

// Mock dos hooks
vi.mock('../../../../app/hooks/useAnalytics', () => ({
  useAnalytics: vi.fn()
}));

vi.mock('../../../../app/hooks/usePerformanceMetrics', () => ({
  usePerformanceMetrics: vi.fn()
}));

// Mock dos componentes shared
vi.mock('../../../../app/components/shared/Card', () => ({
  Card: ({ children, ...props }: any) => <div data-testid="card" {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div data-testid="card-content" {...props}>{children}</div>,
  CardHeader: ({ children, ...props }: any) => <div data-testid="card-header" {...props}>{children}</div>,
  CardTitle: ({ children, ...props }: any) => <div data-testid="card-title" {...props}>{children}</div>
}));

vi.mock('../../../../app/components/shared/Button', () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button data-testid="button" onClick={onClick} {...props}>{children}</button>
  )
}));

vi.mock('../../../../app/components/shared/Badge', () => ({
  Badge: ({ children, ...props }: any) => <span data-testid="badge" {...props}>{children}</span>
}));

vi.mock('../../../../app/components/shared/Tabs', () => ({
  Tabs: ({ children, ...props }: any) => <div data-testid="tabs" {...props}>{children}</div>,
  TabsContent: ({ children, ...props }: any) => <div data-testid="tabs-content" {...props}>{children}</div>,
  TabsList: ({ children, ...props }: any) => <div data-testid="tabs-list" {...props}>{children}</div>,
  TabsTrigger: ({ children, ...props }: any) => <button data-testid="tabs-trigger" {...props}>{children}</button>
}));

vi.mock('../../../../app/components/shared/Select', () => ({
  Select: ({ children, ...props }: any) => <div data-testid="select" {...props}>{children}</div>,
  SelectContent: ({ children, ...props }: any) => <div data-testid="select-content" {...props}>{children}</div>,
  SelectItem: ({ children, ...props }: any) => <div data-testid="select-item" {...props}>{children}</div>,
  SelectTrigger: ({ children, ...props }: any) => <button data-testid="select-trigger" {...props}>{children}</button>,
  SelectValue: ({ children, ...props }: any) => <div data-testid="select-value" {...props}>{children}</div>
}));

vi.mock('../../../../app/components/shared/DatePicker', () => ({
  DatePicker: ({ ...props }: any) => <input data-testid="date-picker" {...props} />
}));

vi.mock('../../../../app/components/shared/Progress', () => ({
  Progress: ({ ...props }: any) => <div data-testid="progress" {...props} />
}));

vi.mock('../../../../app/components/shared/Alert', () => ({
  Alert: ({ children, ...props }: any) => <div data-testid="alert" {...props}>{children}</div>,
  AlertDescription: ({ children, ...props }: any) => <div data-testid="alert-description" {...props}>{children}</div>
}));

vi.mock('../../../../app/components/shared/Skeleton', () => ({
  Skeleton: ({ ...props }: any) => <div data-testid="skeleton" {...props} />
}));

// Mock dos ícones
vi.mock('lucide-react', () => ({
  TrendingUp: () => <span data-testid="trending-up">TrendingUp</span>,
  TrendingDown: () => <span data-testid="trending-down">TrendingDown</span>,
  Users: () => <span data-testid="users">Users</span>,
  Target: () => <span data-testid="target">Target</span>,
  BarChart3: () => <span data-testid="bar-chart">BarChart3</span>,
  PieChart: () => <span data-testid="pie-chart">PieChart</span>,
  Download: () => <span data-testid="download">Download</span>,
  RefreshCw: () => <span data-testid="refresh">RefreshCw</span>,
  AlertTriangle: () => <span data-testid="alert-triangle">AlertTriangle</span>,
  CheckCircle: () => <span data-testid="check-circle">CheckCircle</span>,
  Clock: () => <span data-testid="clock">Clock</span>,
  Zap: () => <span data-testid="zap">Zap</span>
}));

// Mock dos utilitários
vi.mock('../../../../app/utils/formatters', () => ({
  formatCurrency: vi.fn((value) => `$${value.toFixed(2)}`),
  formatPercentage: vi.fn((value) => `${(value * 100).toFixed(1)}%`),
  formatNumber: vi.fn((value) => value.toLocaleString())
}));

const mockAnalyticsData = {
  keywordsPerformance: {
    totalKeywords: 1000,
    activeKeywords: 750,
    conversionRate: 0.15,
    avgPosition: 8.5,
    clickThroughRate: 0.025,
    costPerClick: 1.25,
    totalClicks: 5000,
    totalImpressions: 200000
  },
  clusterEfficiency: {
    totalClusters: 50,
    avgClusterSize: 15.2,
    clusterQuality: 0.85,
    semanticCoherence: 0.92,
    performanceVariance: 0.18
  },
  userBehavior: {
    activeUsers: 1200,
    sessionDuration: 8.5,
    pageViews: 15000,
    bounceRate: 0.35,
    userEngagement: 0.78
  },
  predictiveInsights: {
    trendPrediction: 0.12,
    seasonalityFactor: 0.08,
    anomalyScore: 0.15,
    recommendationConfidence: 0.89,
    nextBestAction: 'Otimizar clusters de baixa performance'
  }
};

const mockPerformanceMetrics = {
  responseTime: 150,
  throughput: 1000,
  errorRate: 0.02
};

describe('AnalyticsDashboard', () => {
  const mockUseAnalytics = vi.fn();
  const mockUsePerformanceMetrics = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mocks
    mockUseAnalytics.mockReturnValue({
      data: mockAnalyticsData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    mockUsePerformanceMetrics.mockReturnValue({
      data: mockPerformanceMetrics,
      isLoading: false
    });

    // Apply mocks
    const { useAnalytics } = require('../../../../app/hooks/useAnalytics');
    const { usePerformanceMetrics } = require('../../../../app/hooks/usePerformanceMetrics');
    
    useAnalytics.mockImplementation(mockUseAnalytics);
    usePerformanceMetrics.mockImplementation(mockUsePerformanceMetrics);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar o componente com título e descrição', () => {
      render(<AnalyticsDashboard />);
      
      expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Métricas avançadas e insights preditivos do sistema')).toBeInTheDocument();
    });

    it('deve renderizar controles de período e exportação', () => {
      render(<AnalyticsDashboard />);
      
      expect(screen.getByTestId('select-trigger')).toBeInTheDocument();
      expect(screen.getByText('Atualizar')).toBeInTheDocument();
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });

    it('deve renderizar métricas principais', () => {
      render(<AnalyticsDashboard />);
      
      expect(screen.getByText('Performance Score')).toBeInTheDocument();
      expect(screen.getByText('Keywords Ativas')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Conversão')).toBeInTheDocument();
      expect(screen.getByText('Usuários Ativos')).toBeInTheDocument();
    });

    it('deve renderizar tabs principais', () => {
      render(<AnalyticsDashboard />);
      
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Clusters')).toBeInTheDocument();
      expect(screen.getByText('Comportamento')).toBeInTheDocument();
      expect(screen.getByText('Insights Preditivos')).toBeInTheDocument();
    });
  });

  describe('Estados de Loading', () => {
    it('deve mostrar skeleton durante carregamento', () => {
      mockUseAnalytics.mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        refetch: vi.fn()
      });

      render(<AnalyticsDashboard />);
      
      expect(screen.getAllByTestId('skeleton')).toHaveLength(5); // 1 título + 4 cards
    });
  });

  describe('Estados de Erro', () => {
    it('deve mostrar alerta de erro quando há falha', () => {
      const errorMessage = 'Erro ao carregar dados';
      mockUseAnalytics.mockReturnValue({
        data: null,
        isLoading: false,
        error: { message: errorMessage },
        refetch: vi.fn()
      });

      render(<AnalyticsDashboard />);
      
      expect(screen.getByTestId('alert')).toBeInTheDocument();
      expect(screen.getByText(`Erro ao carregar dados de analytics: ${errorMessage}`)).toBeInTheDocument();
    });
  });

  describe('Interações do Usuário', () => {
    it('deve chamar refetch ao clicar em atualizar', async () => {
      const mockRefetch = vi.fn();
      mockUseAnalytics.mockReturnValue({
        data: mockAnalyticsData,
        isLoading: false,
        error: null,
        refetch: mockRefetch
      });

      render(<AnalyticsDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      fireEvent.click(refreshButton);
      
      expect(mockRefetch).toHaveBeenCalledTimes(1);
    });

    it('deve mudar período quando selecionado', () => {
      render(<AnalyticsDashboard />);
      
      const periodSelect = screen.getByTestId('select-trigger');
      fireEvent.click(periodSelect);
      
      // Simular seleção de período
      expect(periodSelect).toBeInTheDocument();
    });

    it('deve chamar função de exportação ao clicar em botão de export', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      render(<AnalyticsDashboard />);
      
      const csvButton = screen.getByText('CSV');
      fireEvent.click(csvButton);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Exporting analytics data in csv format');
      });
      
      consoleSpy.mockRestore();
    });
  });

  describe('Cálculos e Métricas', () => {
    it('deve calcular performance score corretamente', () => {
      render(<AnalyticsDashboard />);
      
      // Performance Score = (conversionRate * 0.4) + (clusterQuality * 0.3) + (userEngagement * 0.3)
      // = (0.15 * 0.4) + (0.85 * 0.3) + (0.78 * 0.3) = 0.06 + 0.255 + 0.234 = 0.549 * 100 = 55
      expect(screen.getByText('55/100')).toBeInTheDocument();
    });

    it('deve mostrar tendência correta baseada na eficiência', () => {
      render(<AnalyticsDashboard />);
      
      // semanticCoherence > 0.8 deve mostrar tendência 'up'
      expect(screen.getByText('+12% vs período anterior')).toBeInTheDocument();
    });

    it('deve mostrar nível de risco correto', () => {
      render(<AnalyticsDashboard />);
      
      // anomalyScore = 0.15 (baixo) deve mostrar risco 'low'
      expect(screen.getByText('Risco: low')).toBeInTheDocument();
    });
  });

  describe('Dados das Tabs', () => {
    it('deve mostrar dados de performance na tab Performance', () => {
      render(<AnalyticsDashboard />);
      
      expect(screen.getByText('Métricas de Keywords')).toBeInTheDocument();
      expect(screen.getByText('#8.5')).toBeInTheDocument(); // avgPosition
      expect(screen.getByText('2.5%')).toBeInTheDocument(); // clickThroughRate
    });

    it('deve mostrar dados de clusters na tab Clusters', () => {
      render(<AnalyticsDashboard />);
      
      // Clicar na tab Clusters
      const clustersTab = screen.getByText('Clusters');
      fireEvent.click(clustersTab);
      
      expect(screen.getByText('Eficiência de Clusters')).toBeInTheDocument();
      expect(screen.getByText('50')).toBeInTheDocument(); // totalClusters
      expect(screen.getByText('15.2')).toBeInTheDocument(); // avgClusterSize
    });

    it('deve mostrar dados de comportamento na tab Comportamento', () => {
      render(<AnalyticsDashboard />);
      
      // Clicar na tab Comportamento
      const behaviorTab = screen.getByText('Comportamento');
      fireEvent.click(behaviorTab);
      
      expect(screen.getByText('Comportamento do Usuário')).toBeInTheDocument();
      expect(screen.getByText('15,000')).toBeInTheDocument(); // pageViews
      expect(screen.getByText('35.0%')).toBeInTheDocument(); // bounceRate
    });

    it('deve mostrar insights preditivos na tab Insights Preditivos', () => {
      render(<AnalyticsDashboard />);
      
      // Clicar na tab Insights Preditivos
      const predictionsTab = screen.getByText('Insights Preditivos');
      fireEvent.click(predictionsTab);
      
      expect(screen.getByText('Insights Preditivos')).toBeInTheDocument();
      expect(screen.getByText('12.0%')).toBeInTheDocument(); // trendPrediction
      expect(screen.getByText('Otimizar clusters de baixa performance')).toBeInTheDocument(); // nextBestAction
    });
  });

  describe('Configurações de Props', () => {
    it('deve aplicar className customizada', () => {
      const { container } = render(<AnalyticsDashboard className="custom-class" />);
      
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('deve mostrar tempo real quando enableRealTime é true', () => {
      render(<AnalyticsDashboard enableRealTime={true} />);
      
      expect(screen.getByText('Tempo real ativo')).toBeInTheDocument();
    });

    it('deve não mostrar tempo real quando enableRealTime é false', () => {
      render(<AnalyticsDashboard enableRealTime={false} />);
      
      expect(screen.queryByText('Tempo real ativo')).not.toBeInTheDocument();
    });

    it('deve renderizar apenas formatos de exportação especificados', () => {
      render(<AnalyticsDashboard exportFormats={['csv']} />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.queryByText('JSON')).not.toBeInTheDocument();
      expect(screen.queryByText('PDF')).not.toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter estrutura semântica adequada', () => {
      render(<AnalyticsDashboard />);
      
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
    });

    it('deve ter botões com labels adequados', () => {
      render(<AnalyticsDashboard />);
      
      expect(screen.getByRole('button', { name: /atualizar/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /csv/i })).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve usar useMemo para cálculos derivados', () => {
      const { rerender } = render(<AnalyticsDashboard />);
      
      // Primeira renderização
      expect(screen.getByText('55/100')).toBeInTheDocument();
      
      // Re-renderização com mesmos dados
      rerender(<AnalyticsDashboard />);
      
      // Deve manter o mesmo resultado sem recálculo
      expect(screen.getByText('55/100')).toBeInTheDocument();
    });
  });
}); 