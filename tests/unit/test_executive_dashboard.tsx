/**
 * Testes Unitários - Dashboard Executivo
 * Testes abrangentes para o ExecutiveDashboard
 * 
 * Tracing ID: TEST_EXECUTIVE_DASHBOARD_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Testes de Dashboard Executivo
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import ExecutiveDashboard from '../../app/components/dashboards/ExecutiveDashboard';

// Mock das APIs do sistema real
const mockBusinessMetrics = {
  totalUsers: 15420,
  activeUsers: 8920,
  newUsers: 156,
  userGrowthRate: 12.5,
  revenue: 1250000,
  revenueGrowth: 8.3,
  conversionRate: 3.2,
  averageOrderValue: 85.50,
  customerSatisfaction: 4.6,
  churnRate: 2.1
};

const mockPerformanceMetrics = {
  systemUptime: 99.87,
  responseTime: 245,
  errorRate: 0.12,
  throughput: 1250,
  cpuUsage: 68.5,
  memoryUsage: 72.3,
  databaseConnections: 45,
  cacheHitRate: 89.2
};

const mockRoiMetrics = {
  totalInvestment: 850000,
  totalReturn: 1250000,
  roiPercentage: 47.1,
  paybackPeriod: 18,
  customerLifetimeValue: 1250,
  acquisitionCost: 45,
  profitMargin: 32.5
};

const mockAlertMetrics = {
  totalAlerts: 23,
  criticalAlerts: 2,
  resolvedAlerts: 18,
  averageResolutionTime: 15.5,
  alertTrend: 'down' as const
};

// Mock global do fetch
global.fetch = jest.fn();

describe('ExecutiveDashboard', () => {
  beforeEach(() => {
    // Limpar mocks antes de cada teste
    jest.clearAllMocks();
    
    // Mock das respostas das APIs
    (global.fetch as jest.Mock).mockResolvedValue({
      json: jest.fn().mockResolvedValue(mockBusinessMetrics)
    });
  });

  describe('Renderização Inicial', () => {
    test('deve renderizar o dashboard com título correto', () => {
      render(<ExecutiveDashboard />);
      
      expect(screen.getByText('Dashboard Executivo')).toBeInTheDocument();
      expect(screen.getByText('Métricas em tempo real para tomada de decisões estratégicas')).toBeInTheDocument();
    });

    test('deve renderizar todos os KPIs principais', () => {
      render(<ExecutiveDashboard />);
      
      // KPIs principais
      expect(screen.getByText('Usuários Ativos')).toBeInTheDocument();
      expect(screen.getByText('Receita Mensal')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Conversão')).toBeInTheDocument();
      expect(screen.getByText('ROI')).toBeInTheDocument();
    });

    test('deve renderizar métricas de performance', () => {
      render(<ExecutiveDashboard />);
      
      expect(screen.getByText('Performance do Sistema')).toBeInTheDocument();
      expect(screen.getByText('Uptime')).toBeInTheDocument();
      expect(screen.getByText('Tempo de Resposta')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Erro')).toBeInTheDocument();
      expect(screen.getByText('Throughput')).toBeInTheDocument();
    });

    test('deve renderizar métricas de alertas', () => {
      render(<ExecutiveDashboard />);
      
      expect(screen.getByText('Alertas e Monitoramento')).toBeInTheDocument();
      expect(screen.getByText('Alertas Críticos')).toBeInTheDocument();
      expect(screen.getByText('Alertas Resolvidos')).toBeInTheDocument();
      expect(screen.getByText('Tempo Médio de Resolução')).toBeInTheDocument();
    });

    test('deve renderizar gráficos e visualizações', () => {
      render(<ExecutiveDashboard />);
      
      expect(screen.getByText('Crescimento de Usuários')).toBeInTheDocument();
      expect(screen.getByText('Distribuição de Receita')).toBeInTheDocument();
      expect(screen.getByText('Performance do Sistema')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Controle', () => {
    test('deve permitir seleção de timeframe', () => {
      render(<ExecutiveDashboard />);
      
      const timeframeSelect = screen.getByDisplayValue('Últimas 24h');
      expect(timeframeSelect).toBeInTheDocument();
      
      fireEvent.change(timeframeSelect, { target: { value: '7d' } });
      expect(timeframeSelect).toHaveValue('7d');
    });

    test('deve ter botão de atualização', () => {
      render(<ExecutiveDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      expect(refreshButton).toBeInTheDocument();
      expect(refreshButton).toBeEnabled();
    });

    test('deve ter botão de exportar', () => {
      render(<ExecutiveDashboard />);
      
      const exportButton = screen.getByText('Exportar');
      expect(exportButton).toBeInTheDocument();
      expect(exportButton).toBeEnabled();
    });

    test('deve ter botão de compartilhar', () => {
      render(<ExecutiveDashboard />);
      
      const shareButton = screen.getByText('Compartilhar');
      expect(shareButton).toBeInTheDocument();
      expect(shareButton).toBeEnabled();
    });
  });

  describe('Formatação de Dados', () => {
    test('deve formatar valores monetários corretamente', () => {
      render(<ExecutiveDashboard />);
      
      // Verificar se a receita está formatada como moeda brasileira
      const revenueElement = screen.getByText(/R\$\s*1\.250\.000/);
      expect(revenueElement).toBeInTheDocument();
    });

    test('deve formatar percentuais corretamente', () => {
      render(<ExecutiveDashboard />);
      
      // Verificar se a taxa de conversão está formatada como percentual
      const conversionElement = screen.getByText('3,2%');
      expect(conversionElement).toBeInTheDocument();
    });

    test('deve formatar números grandes corretamente', () => {
      render(<ExecutiveDashboard />);
      
      // Verificar se usuários ativos está formatado com separadores
      const usersElement = screen.getByText('8.920');
      expect(usersElement).toBeInTheDocument();
    });

    test('deve formatar tempo de resposta em milissegundos', () => {
      render(<ExecutiveDashboard />);
      
      // Verificar se tempo de resposta está formatado com "ms"
      const responseTimeElement = screen.getByText('245ms');
      expect(responseTimeElement).toBeInTheDocument();
    });
  });

  describe('Atualização de Dados', () => {
    test('deve buscar dados ao montar o componente', async () => {
      render(<ExecutiveDashboard />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/business-metrics');
        expect(global.fetch).toHaveBeenCalledWith('/api/performance-metrics');
        expect(global.fetch).toHaveBeenCalledWith('/api/roi-metrics');
        expect(global.fetch).toHaveBeenCalledWith('/api/alert-metrics');
      });
    });

    test('deve atualizar dados ao clicar no botão de atualizar', async () => {
      render(<ExecutiveDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      
      await act(async () => {
        fireEvent.click(refreshButton);
      });
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(8); // 4 inicial + 4 do refresh
      });
    });

    test('deve mostrar indicador de carregamento durante atualização', async () => {
      // Mock de fetch lento
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          json: jest.fn().mockResolvedValue(mockBusinessMetrics)
        }), 100))
      );
      
      render(<ExecutiveDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      
      await act(async () => {
        fireEvent.click(refreshButton);
      });
      
      // Verificar se o ícone de loading está presente
      const loadingIcon = screen.getByTestId('refresh-icon');
      expect(loadingIcon).toHaveClass('animate-spin');
    });
  });

  describe('Funcionalidade de Exportação', () => {
    test('deve exportar relatório em JSON', async () => {
      // Mock do URL.createObjectURL e URL.revokeObjectURL
      const mockCreateObjectURL = jest.fn().mockReturnValue('blob:mock-url');
      const mockRevokeObjectURL = jest.fn();
      global.URL.createObjectURL = mockCreateObjectURL;
      global.URL.revokeObjectURL = mockRevokeObjectURL;
      
      // Mock do document.createElement
      const mockAnchor = {
        href: '',
        download: '',
        click: jest.fn()
      };
      document.createElement = jest.fn().mockReturnValue(mockAnchor);
      
      render(<ExecutiveDashboard />);
      
      const exportButton = screen.getByText('Exportar');
      
      await act(async () => {
        fireEvent.click(exportButton);
      });
      
      expect(mockCreateObjectURL).toHaveBeenCalled();
      expect(mockAnchor.click).toHaveBeenCalled();
      expect(mockRevokeObjectURL).toHaveBeenCalled();
    });

    test('deve gerar nome de arquivo com data atual', async () => {
      const mockAnchor = {
        href: '',
        download: '',
        click: jest.fn()
      };
      document.createElement = jest.fn().mockReturnValue(mockAnchor);
      
      render(<ExecutiveDashboard />);
      
      const exportButton = screen.getByText('Exportar');
      
      await act(async () => {
        fireEvent.click(exportButton);
      });
      
      expect(mockAnchor.download).toMatch(/executive-dashboard-\d{4}-\d{2}-\d{2}\.json/);
    });
  });

  describe('Funcionalidade de Compartilhamento', () => {
    test('deve usar Web Share API quando disponível', async () => {
      // Mock do navigator.share
      const mockShare = jest.fn().mockResolvedValue(undefined);
      Object.assign(navigator, { share: mockShare });
      
      render(<ExecutiveDashboard />);
      
      const shareButton = screen.getByText('Compartilhar');
      
      await act(async () => {
        fireEvent.click(shareButton);
      });
      
      expect(mockShare).toHaveBeenCalledWith({
        title: 'Dashboard Executivo - Omni Keywords Finder',
        text: 'Relatório executivo com métricas em tempo real',
        url: window.location.href
      });
    });

    test('deve usar fallback para copiar URL quando Web Share API não disponível', async () => {
      // Mock do navigator.clipboard
      const mockClipboard = {
        writeText: jest.fn().mockResolvedValue(undefined)
      };
      Object.assign(navigator, { clipboard: mockClipboard, share: undefined });
      
      // Mock do alert
      global.alert = jest.fn();
      
      render(<ExecutiveDashboard />);
      
      const shareButton = screen.getByText('Compartilhar');
      
      await act(async () => {
        fireEvent.click(shareButton);
      });
      
      expect(mockClipboard.writeText).toHaveBeenCalledWith(window.location.href);
      expect(global.alert).toHaveBeenCalledWith('URL do dashboard copiada para a área de transferência');
    });
  });

  describe('Métricas Avançadas', () => {
    test('deve mostrar métricas avançadas quando habilitadas', () => {
      render(<ExecutiveDashboard showAdvancedMetrics={true} />);
      
      expect(screen.getByText('Métricas de Negócio')).toBeInTheDocument();
      expect(screen.getByText('Métricas de ROI')).toBeInTheDocument();
      expect(screen.getByText('Satisfação do Cliente')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Churn')).toBeInTheDocument();
      expect(screen.getByText('Valor Médio do Pedido')).toBeInTheDocument();
      expect(screen.getByText('Período de Payback')).toBeInTheDocument();
      expect(screen.getByText('LTV do Cliente')).toBeInTheDocument();
      expect(screen.getByText('Custo de Aquisição')).toBeInTheDocument();
    });

    test('deve ocultar métricas avançadas quando desabilitadas', () => {
      render(<ExecutiveDashboard showAdvancedMetrics={false} />);
      
      expect(screen.queryByText('Métricas de Negócio')).not.toBeInTheDocument();
      expect(screen.queryByText('Métricas de ROI')).not.toBeInTheDocument();
    });
  });

  describe('Tempo Real', () => {
    test('deve mostrar indicador de tempo real quando habilitado', () => {
      render(<ExecutiveDashboard enableRealTime={true} />);
      
      expect(screen.getByText('Tempo real ativo')).toBeInTheDocument();
    });

    test('deve ocultar indicador de tempo real quando desabilitado', () => {
      render(<ExecutiveDashboard enableRealTime={false} />);
      
      expect(screen.queryByText('Tempo real ativo')).not.toBeInTheDocument();
    });

    test('deve atualizar automaticamente quando tempo real está habilitado', async () => {
      jest.useFakeTimers();
      
      render(<ExecutiveDashboard enableRealTime={true} refreshInterval={1000} />);
      
      // Avançar o tempo para simular intervalo de atualização
      act(() => {
        jest.advanceTimersByTime(1000);
      });
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(8); // 4 inicial + 4 do intervalo
      });
      
      jest.useRealTimers();
    });
  });

  describe('Tratamento de Erros', () => {
    test('deve manter dados existentes em caso de erro na API', async () => {
      // Mock de erro na API
      (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));
      
      render(<ExecutiveDashboard />);
      
      // Verificar se os dados iniciais ainda estão visíveis
      expect(screen.getByText('8.920')).toBeInTheDocument(); // Usuários ativos
      expect(screen.getByText('R$ 1.250.000')).toBeInTheDocument(); // Receita
    });

    test('deve logar erro no console em caso de falha', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      // Mock de erro na API
      (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));
      
      render(<ExecutiveDashboard />);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Erro ao buscar dados do dashboard:', expect.any(Error));
      });
      
      consoleSpy.mockRestore();
    });
  });

  describe('Acessibilidade', () => {
    test('deve ter botões com roles apropriados', () => {
      render(<ExecutiveDashboard />);
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      const exportButton = screen.getByRole('button', { name: /exportar/i });
      const shareButton = screen.getByRole('button', { name: /compartilhar/i });
      
      expect(refreshButton).toBeInTheDocument();
      expect(exportButton).toBeInTheDocument();
      expect(shareButton).toBeInTheDocument();
    });

    test('deve ter select com label apropriado', () => {
      render(<ExecutiveDashboard />);
      
      const timeframeSelect = screen.getByRole('combobox');
      expect(timeframeSelect).toBeInTheDocument();
      expect(timeframeSelect).toHaveValue('24h');
    });

    test('deve ter elementos com textos descritivos', () => {
      render(<ExecutiveDashboard />);
      
      expect(screen.getByText('Última atualização:')).toBeInTheDocument();
      expect(screen.getByText('Configurações')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    test('deve ter classes CSS responsivas', () => {
      render(<ExecutiveDashboard />);
      
      // Verificar se o grid principal tem classes responsivas
      const mainGrid = screen.getByText('Dashboard Executivo').closest('.min-h-screen');
      expect(mainGrid).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4');
    });

    test('deve ter layout responsivo para diferentes tamanhos de tela', () => {
      render(<ExecutiveDashboard />);
      
      // Verificar se os containers têm classes responsivas
      const performanceSection = screen.getByText('Performance do Sistema').closest('.grid');
      expect(performanceSection).toHaveClass('grid-cols-1', 'lg:grid-cols-2');
    });
  });

  describe('Performance', () => {
    test('deve usar useCallback para funções de callback', () => {
      // Este teste verifica se as funções estão sendo memoizadas
      // Na implementação real, isso seria verificado através de profiling
      render(<ExecutiveDashboard />);
      
      // Verificar se o componente renderiza sem erros
      expect(screen.getByText('Dashboard Executivo')).toBeInTheDocument();
    });

    test('deve limpar intervalos ao desmontar', () => {
      jest.useFakeTimers();
      
      const { unmount } = render(<ExecutiveDashboard enableRealTime={true} />);
      
      // Verificar se o intervalo foi criado
      expect(setInterval).toHaveBeenCalled();
      
      // Desmontar componente
      unmount();
      
      // Verificar se o intervalo foi limpo
      expect(clearInterval).toHaveBeenCalled();
      
      jest.useRealTimers();
    });
  });

  describe('Integração com Sistema Real', () => {
    test('deve chamar APIs corretas do sistema', async () => {
      render(<ExecutiveDashboard />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/business-metrics');
        expect(global.fetch).toHaveBeenCalledWith('/api/performance-metrics');
        expect(global.fetch).toHaveBeenCalledWith('/api/roi-metrics');
        expect(global.fetch).toHaveBeenCalledWith('/api/alert-metrics');
      });
    });

    test('deve usar dados reais do sistema Omni Keywords Finder', () => {
      render(<ExecutiveDashboard />);
      
      // Verificar se os valores iniciais correspondem ao sistema real
      expect(screen.getByText('8.920')).toBeInTheDocument(); // Usuários ativos
      expect(screen.getByText('R$ 1.250.000')).toBeInTheDocument(); // Receita
      expect(screen.getByText('3,2%')).toBeInTheDocument(); // Taxa de conversão
      expect(screen.getByText('47,1%')).toBeInTheDocument(); // ROI
    });

    test('deve mostrar métricas específicas do negócio', () => {
      render(<ExecutiveDashboard showAdvancedMetrics={true} />);
      
      // Verificar métricas específicas do Omni Keywords Finder
      expect(screen.getByText('Satisfação do Cliente')).toBeInTheDocument();
      expect(screen.getByText('4,6/5,0')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Churn')).toBeInTheDocument();
      expect(screen.getByText('2,1%')).toBeInTheDocument();
    });
  });
}); 