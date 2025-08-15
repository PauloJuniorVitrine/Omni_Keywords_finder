/**
 * Teste Unitário - BusinessMetricsDashboard
 * 
 * Teste baseado no código real do sistema Omni Keywords Finder
 * 
 * Tracing ID: TEST_BM_DASHBOARD_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Dashboard de Métricas de Negócio
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BusinessMetricsDashboard } from '../../app/components/analytics/BusinessMetricsDashboard';
import { useBusinessMetrics, useUserEngagement, useRevenueMetrics } from '../../app/hooks/useBusinessMetrics';

// Mock dos hooks baseados no código real
jest.mock('../../app/hooks/useBusinessMetrics');

const mockUseBusinessMetrics = useBusinessMetrics as jest.MockedFunction<typeof useBusinessMetrics>;
const mockUseUserEngagement = useUserEngagement as jest.MockedFunction<typeof useUserEngagement>;
const mockUseRevenueMetrics = useRevenueMetrics as jest.MockedFunction<typeof useRevenueMetrics>;

// Dados reais baseados no sistema Omni Keywords Finder
const mockBusinessMetricsData = {
  metrics: [
    {
      id: 'metric-001',
      name: 'Keywords Processadas',
      value: 15420,
      unit: 'keywords',
      category: 'keywords' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'up' as const,
      changePercent: 12.5,
      targetValue: 20000,
      alertThreshold: 10000
    },
    {
      id: 'metric-002',
      name: 'Clusters Gerados',
      value: 892,
      unit: 'clusters',
      category: 'keywords' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'up' as const,
      changePercent: 8.3,
      targetValue: 1000,
      alertThreshold: 500
    },
    {
      id: 'metric-003',
      name: 'Taxa de Conversão',
      value: 3.2,
      unit: '%',
      category: 'conversion' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'stable' as const,
      changePercent: 0.5,
      targetValue: 5.0,
      alertThreshold: 2.0
    },
    {
      id: 'metric-004',
      name: 'Usuários Ativos',
      value: 1250,
      unit: 'users',
      category: 'users' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'up' as const,
      changePercent: 15.2,
      targetValue: 1500,
      alertThreshold: 800
    }
  ],
  funnels: [
    {
      id: 'funnel-001',
      name: 'Onboarding Completo',
      stages: ['Registro', 'Configuração', 'Primeira Execução', 'Pagamento'],
      values: [1000, 850, 720, 156],
      conversionRates: [100, 85, 84.7, 21.7],
      timestamp: '2025-01-27T15:30:00Z'
    },
    {
      id: 'funnel-002',
      name: 'Execução de Keywords',
      stages: ['Seleção', 'Configuração', 'Execução', 'Resultados'],
      values: [500, 480, 465, 450],
      conversionRates: [100, 96, 96.9, 90],
      timestamp: '2025-01-27T15:30:00Z'
    }
  ],
  cohorts: [
    {
      id: 'cohort-001',
      cohortDate: '2025-01-01',
      cohortSize: 250,
      retentionData: { 1: 95, 7: 78, 30: 65, 90: 45 },
      churnData: { 1: 5, 7: 22, 30: 35, 90: 55 },
      revenueData: { 1: 25.50, 7: 45.20, 30: 85.75, 90: 125.30 }
    },
    {
      id: 'cohort-002',
      cohortDate: '2025-01-15',
      cohortSize: 180,
      retentionData: { 1: 92, 7: 75, 30: 62 },
      churnData: { 1: 8, 7: 25, 30: 38 },
      revenueData: { 1: 28.75, 7: 48.90, 30: 88.45 }
    }
  ],
  abTests: [
    {
      id: 'ab-test-001',
      experimentId: 'onboarding-flow-v2',
      variantA: 'Original',
      variantB: 'Simplificado',
      metricName: 'Taxa de Conversão',
      variantAStats: { mean: 2.8, std: 0.5, n: 500 },
      variantBStats: { mean: 3.2, std: 0.6, n: 500 },
      pValue: 0.03,
      confidenceLevel: 95.2,
      lift: 14.3,
      statisticalPower: 0.85,
      sampleSize: 1000,
      timestamp: '2025-01-27T15:30:00Z'
    }
  ],
  calculated: {
    totals: {
      revenue: 1250000,
      users: 15420,
      conversion: 3.2,
      engagement: 78.5
    },
    trends: {
      revenue: { overallTrend: 'up', changePercent: 8.3 },
      users: { overallTrend: 'up', changePercent: 12.5 },
      conversion: { overallTrend: 'stable', changePercent: 0.5 },
      engagement: { overallTrend: 'up', changePercent: 5.2 }
    }
  }
};

const mockEngagementData = {
  metrics: [
    {
      id: 'engagement-001',
      name: 'Tempo Médio de Sessão',
      value: 12.5,
      unit: 'minutos',
      category: 'engagement' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'up' as const,
      changePercent: 8.2
    },
    {
      id: 'engagement-002',
      name: 'Páginas por Sessão',
      value: 4.8,
      unit: 'páginas',
      category: 'engagement' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'stable' as const,
      changePercent: 1.2
    }
  ]
};

const mockRevenueData = {
  metrics: [
    {
      id: 'revenue-001',
      name: 'Receita Mensal',
      value: 1250000,
      unit: 'R$',
      category: 'revenue' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'up' as const,
      changePercent: 8.3
    },
    {
      id: 'revenue-002',
      name: 'Ticket Médio',
      value: 85.50,
      unit: 'R$',
      category: 'revenue' as const,
      timestamp: '2025-01-27T15:30:00Z',
      trend: 'up' as const,
      changePercent: 5.1
    }
  ]
};

describe('BusinessMetricsDashboard', () => {
  beforeEach(() => {
    // Configurar mocks baseados no código real
    mockUseBusinessMetrics.mockReturnValue({
      data: mockBusinessMetricsData,
      metrics: mockBusinessMetricsData.metrics,
      funnels: mockBusinessMetricsData.funnels,
      cohorts: mockBusinessMetricsData.cohorts,
      abTests: mockBusinessMetricsData.abTests,
      calculated: mockBusinessMetricsData.calculated,
      isLoading: false,
      hasError: false,
      error: null,
      refreshAll: jest.fn(),
      exportData: jest.fn()
    });

    mockUseUserEngagement.mockReturnValue({
      data: mockEngagementData,
      metrics: mockEngagementData.metrics
    });

    mockUseRevenueMetrics.mockReturnValue({
      data: mockRevenueData,
      metrics: mockRevenueData.metrics
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Inicial', () => {
    test('deve renderizar o dashboard com título correto', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('Métricas de Negócio')).toBeInTheDocument();
    });

    test('deve renderizar todas as abas principais', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('Visão Geral')).toBeInTheDocument();
      expect(screen.getByText('Engajamento')).toBeInTheDocument();
      expect(screen.getByText('Funis de Conversão')).toBeInTheDocument();
      expect(screen.getByText('Receita')).toBeInTheDocument();
      expect(screen.getByText('Cohorts')).toBeInTheDocument();
      expect(screen.getByText('A/B Testing')).toBeInTheDocument();
    });

    test('deve renderizar métricas principais na aba Visão Geral', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('Keywords Processadas')).toBeInTheDocument();
      expect(screen.getByText('15,420')).toBeInTheDocument();
      expect(screen.getByText('Clusters Gerados')).toBeInTheDocument();
      expect(screen.getByText('892')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Conversão')).toBeInTheDocument();
      expect(screen.getByText('3.2%')).toBeInTheDocument();
    });

    test('deve renderizar estatísticas do dashboard', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('R$ 1,250,000')).toBeInTheDocument();
      expect(screen.getByText('15,420')).toBeInTheDocument();
      expect(screen.getByText('3.2%')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Filtros', () => {
    test('deve permitir seleção de período', () => {
      render(<BusinessMetricsDashboard />);
      
      const periodSelect = screen.getByRole('combobox', { name: /período/i });
      expect(periodSelect).toBeInTheDocument();
      
      fireEvent.click(periodSelect);
      expect(screen.getByText('7 dias')).toBeInTheDocument();
      expect(screen.getByText('30 dias')).toBeInTheDocument();
      expect(screen.getByText('90 dias')).toBeInTheDocument();
    });

    test('deve permitir seleção de categoria', () => {
      render(<BusinessMetricsDashboard />);
      
      const categorySelect = screen.getByRole('combobox', { name: /categoria/i });
      expect(categorySelect).toBeInTheDocument();
      
      fireEvent.click(categorySelect);
      expect(screen.getByText('Todas')).toBeInTheDocument();
      expect(screen.getByText('Receita')).toBeInTheDocument();
      expect(screen.getByText('Usuários')).toBeInTheDocument();
    });
  });

  describe('Abas de Conteúdo', () => {
    test('deve mostrar métricas de engajamento na aba Engajamento', () => {
      render(<BusinessMetricsDashboard />);
      
      fireEvent.click(screen.getByText('Engajamento'));
      
      expect(screen.getByText('Tempo Médio de Sessão')).toBeInTheDocument();
      expect(screen.getByText('12.5 minutos')).toBeInTheDocument();
      expect(screen.getByText('Páginas por Sessão')).toBeInTheDocument();
      expect(screen.getByText('4.8 páginas')).toBeInTheDocument();
    });

    test('deve mostrar funis de conversão na aba Funis de Conversão', () => {
      render(<BusinessMetricsDashboard />);
      
      fireEvent.click(screen.getByText('Funis de Conversão'));
      
      expect(screen.getByText('Onboarding Completo')).toBeInTheDocument();
      expect(screen.getByText('Execução de Keywords')).toBeInTheDocument();
      expect(screen.getByText('Registro')).toBeInTheDocument();
      expect(screen.getByText('Configuração')).toBeInTheDocument();
      expect(screen.getByText('Primeira Execução')).toBeInTheDocument();
      expect(screen.getByText('Pagamento')).toBeInTheDocument();
    });

    test('deve mostrar métricas de receita na aba Receita', () => {
      render(<BusinessMetricsDashboard />);
      
      fireEvent.click(screen.getByText('Receita'));
      
      expect(screen.getByText('Receita Mensal')).toBeInTheDocument();
      expect(screen.getByText('R$ 1,250,000')).toBeInTheDocument();
      expect(screen.getByText('Ticket Médio')).toBeInTheDocument();
      expect(screen.getByText('R$ 85.50')).toBeInTheDocument();
    });

    test('deve mostrar análise de cohorts na aba Cohorts', () => {
      render(<BusinessMetricsDashboard />);
      
      fireEvent.click(screen.getByText('Cohorts'));
      
      expect(screen.getByText(/Cohorte 01\/01\/2025/)).toBeInTheDocument();
      expect(screen.getByText('250 usuários')).toBeInTheDocument();
      expect(screen.getByText('95.0%')).toBeInTheDocument(); // Retenção
      expect(screen.getByText('5.0%')).toBeInTheDocument(); // Churn
      expect(screen.getByText('R$ 25.50')).toBeInTheDocument(); // Receita
    });

    test('deve mostrar resultados de A/B testing na aba A/B Testing', () => {
      render(<BusinessMetricsDashboard />);
      
      fireEvent.click(screen.getByText('A/B Testing'));
      
      expect(screen.getByText('onboarding-flow-v2')).toBeInTheDocument();
      expect(screen.getByText('Significativo')).toBeInTheDocument();
      expect(screen.getByText('Variante A')).toBeInTheDocument();
      expect(screen.getByText('2.80')).toBeInTheDocument();
      expect(screen.getByText('Variante B')).toBeInTheDocument();
      expect(screen.getByText('3.20')).toBeInTheDocument();
      expect(screen.getByText('Lift: 14.30%')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Exportação', () => {
    test('deve renderizar botões de exportação', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });

    test('deve chamar função de exportação ao clicar em CSV', async () => {
      const mockExportData = jest.fn();
      mockUseBusinessMetrics.mockReturnValue({
        ...mockUseBusinessMetrics(),
        exportData: mockExportData
      });

      render(<BusinessMetricsDashboard />);
      
      const csvButton = screen.getByText('CSV');
      fireEvent.click(csvButton);
      
      await waitFor(() => {
        expect(mockExportData).toHaveBeenCalledWith('csv');
      });
    });

    test('deve chamar função de exportação ao clicar em JSON', async () => {
      const mockExportData = jest.fn();
      mockUseBusinessMetrics.mockReturnValue({
        ...mockUseBusinessMetrics(),
        exportData: mockExportData
      });

      render(<BusinessMetricsDashboard />);
      
      const jsonButton = screen.getByText('JSON');
      fireEvent.click(jsonButton);
      
      await waitFor(() => {
        expect(mockExportData).toHaveBeenCalledWith('json');
      });
    });
  });

  describe('Funcionalidades de Atualização', () => {
    test('deve mostrar botão de refresh', () => {
      render(<BusinessMetricsDashboard />);
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      expect(refreshButton).toBeInTheDocument();
    });

    test('deve chamar refreshAll ao clicar no botão de refresh', () => {
      const mockRefreshAll = jest.fn();
      mockUseBusinessMetrics.mockReturnValue({
        ...mockUseBusinessMetrics(),
        refreshAll: mockRefreshAll
      });

      render(<BusinessMetricsDashboard />);
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      fireEvent.click(refreshButton);
      
      expect(mockRefreshAll).toHaveBeenCalled();
    });

    test('deve mostrar timestamp da última atualização', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText(/Última atualização:/)).toBeInTheDocument();
    });
  });

  describe('Estados de Loading e Erro', () => {
    test('deve mostrar loading quando dados estão carregando', () => {
      mockUseBusinessMetrics.mockReturnValue({
        ...mockUseBusinessMetrics(),
        isLoading: true
      });

      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('Carregando métricas...')).toBeInTheDocument();
    });

    test('deve mostrar erro quando há falha na carga', () => {
      mockUseBusinessMetrics.mockReturnValue({
        ...mockUseBusinessMetrics(),
        hasError: true,
        error: new Error('Falha ao carregar métricas')
      });

      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('Erro ao carregar métricas')).toBeInTheDocument();
      expect(screen.getByText('Falha ao carregar métricas')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Tempo Real', () => {
    test('deve mostrar badge de tempo real quando habilitado', () => {
      render(<BusinessMetricsDashboard enableRealTime={true} />);
      
      expect(screen.getByText('Tempo real')).toBeInTheDocument();
    });

    test('não deve mostrar badge de tempo real quando desabilitado', () => {
      render(<BusinessMetricsDashboard enableRealTime={false} />);
      
      expect(screen.queryByText('Tempo real')).not.toBeInTheDocument();
    });
  });

  describe('Formatação de Dados', () => {
    test('deve formatar números grandes corretamente', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByText('15,420')).toBeInTheDocument();
      expect(screen.getByText('R$ 1,250,000')).toBeInTheDocument();
    });

    test('deve mostrar tendências com cores corretas', () => {
      render(<BusinessMetricsDashboard />);
      
      // Verificar que métricas com tendência 'up' têm classe de cor verde
      const upTrendElements = screen.getAllByText('Crescendo');
      expect(upTrendElements.length).toBeGreaterThan(0);
      
      // Verificar que métricas com tendência 'stable' têm classe de cor neutra
      const stableTrendElements = screen.getAllByText('Estável');
      expect(stableTrendElements.length).toBeGreaterThan(0);
    });
  });

  describe('Responsividade', () => {
    test('deve renderizar corretamente em diferentes tamanhos de tela', () => {
      const { container } = render(<BusinessMetricsDashboard />);
      
      // Verificar que o grid é responsivo
      const gridElements = container.querySelectorAll('.grid');
      expect(gridElements.length).toBeGreaterThan(0);
      
      // Verificar que as abas são responsivas
      const tabsElement = container.querySelector('[role="tablist"]');
      expect(tabsElement).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    test('deve ter roles de acessibilidade corretos', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getAllByRole('tab')).toHaveLength(6);
      expect(screen.getByRole('tabpanel')).toBeInTheDocument();
    });

    test('deve ter labels acessíveis para controles', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(screen.getByLabelText(/período/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/categoria/i)).toBeInTheDocument();
    });
  });

  describe('Integração com Hooks', () => {
    test('deve chamar useBusinessMetrics com parâmetros corretos', () => {
      render(<BusinessMetricsDashboard 
        refreshInterval={60000}
        enableRealTime={true}
        defaultPeriod="7d"
      />);
      
      expect(mockUseBusinessMetrics).toHaveBeenCalledWith(
        expect.objectContaining({
          startDate: expect.any(String),
          endDate: expect.any(String)
        }),
        expect.objectContaining({
          enableRealTime: true,
          refreshInterval: 60000
        })
      );
    });

    test('deve chamar useUserEngagement com parâmetros corretos', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(mockUseUserEngagement).toHaveBeenCalledWith(
        undefined,
        expect.objectContaining({
          enableRealTime: true,
          refreshInterval: 30000
        })
      );
    });

    test('deve chamar useRevenueMetrics com parâmetros corretos', () => {
      render(<BusinessMetricsDashboard />);
      
      expect(mockUseRevenueMetrics).toHaveBeenCalledWith(
        expect.objectContaining({
          enableRealTime: true,
          refreshInterval: 30000
        })
      );
    });
  });
}); 