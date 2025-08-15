/**
 * CorrelationDashboard.test.tsx
 * 
 * Testes unitários para o componente CorrelationDashboard
 * 
 * Tracing ID: TEST_MONITORING_20250127_001
 * Prompt: CHECKLIST_TESTES_UNITARIOS_REACT.md - Fase 4.1
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CorrelationDashboard } from '../../../app/components/monitoring/CorrelationDashboard';

// Mock do hook useApi
jest.mock('../../../app/hooks/useApi', () => ({
  useApi: jest.fn()
}));

const mockUseApi = require('../../../app/hooks/useApi').useApi;

// Mock data
const mockCorrelationContext = {
  correlation_id: 'corr_123',
  user_id: 'user_456',
  session_id: 'session_789',
  service_name: 'omni-keywords-service',
  operation_name: 'keyword_analysis',
  start_time: '2025-01-27T10:00:00Z',
  end_time: '2025-01-27T10:05:00Z',
  duration: 300
};

const mockCorrelationEvent = {
  event_id: 'event_001',
  event_type: 'log' as const,
  correlation_id: 'corr_123',
  timestamp: '2025-01-27T10:01:00Z',
  severity: 'info' as const,
  source: 'api-gateway',
  data: { message: 'Request received', method: 'POST' },
  tags: { endpoint: '/api/keywords', user_id: 'user_456' }
};

const mockDashboardData = {
  correlation_id: 'corr_123',
  context: mockCorrelationContext,
  events: [
    mockCorrelationEvent,
    {
      ...mockCorrelationEvent,
      event_id: 'event_002',
      event_type: 'metric' as const,
      severity: 'debug' as const,
      data: { response_time: 150, status_code: 200 }
    },
    {
      ...mockCorrelationEvent,
      event_id: 'event_003',
      event_type: 'alert' as const,
      severity: 'warning' as const,
      data: { alert_type: 'high_latency', threshold: 1000 }
    }
  ],
  dependencies: [
    {
      service: 'database-service',
      operation: 'query_keywords',
      duration: 45,
      status: 'success'
    },
    {
      service: 'ml-service',
      operation: 'analyze_sentiment',
      duration: 120,
      status: 'success'
    }
  ],
  alerts: [
    {
      id: 'alert_001',
      severity: 'warning',
      message: 'High response time detected',
      timestamp: '2025-01-27T10:02:00Z'
    }
  ],
  metrics: {
    response_time: {
      current: 150,
      avg: 120,
      min: 80,
      max: 300,
      trend: 'up' as const
    },
    throughput: {
      current: 1000,
      avg: 950,
      min: 800,
      max: 1200,
      trend: 'stable' as const
    }
  }
};

const mockCorrelationIds = ['corr_123', 'corr_124', 'corr_125'];

const defaultProps = {
  correlationId: 'corr_123',
  autoRefresh: true,
  refreshInterval: 30000
};

describe('CorrelationDashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock padrão para useApi
    mockUseApi.mockImplementation((url: string, options: any) => {
      if (url?.includes('/correlation/')) {
        return {
          data: mockDashboardData,
          loading: false,
          error: null,
          refetch: jest.fn()
        };
      }
      if (url?.includes('/correlations')) {
        return {
          data: mockCorrelationIds,
          loading: false,
          error: null,
          refetch: jest.fn()
        };
      }
      return {
        data: null,
        loading: false,
        error: null,
        refetch: jest.fn()
      };
    });
  });

  describe('Renderização Básica', () => {
    it('deve renderizar com configurações padrão', () => {
      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Dashboard de Correlação')).toBeInTheDocument();
      expect(screen.getByText('Timeline de Eventos')).toBeInTheDocument();
      expect(screen.getByText('Dependências')).toBeInTheDocument();
      expect(screen.getByText('Alertas')).toBeInTheDocument();
    });

    it('deve renderizar com correlationId fornecido', () => {
      render(<CorrelationDashboard correlationId="corr_123" />);
      
      expect(screen.getByText('Correlação: corr_123')).toBeInTheDocument();
    });

    it('deve renderizar com dados de correlação', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('omni-keywords-service')).toBeInTheDocument();
      expect(screen.getByText('keyword_analysis')).toBeInTheDocument();
      expect(screen.getByText('Request received')).toBeInTheDocument();
    });

    it('deve renderizar filtros de tempo', () => {
      render(<CorrelationDashboard />);
      
      expect(screen.getByText('1h')).toBeInTheDocument();
      expect(screen.getByText('6h')).toBeInTheDocument();
      expect(screen.getByText('24h')).toBeInTheDocument();
      expect(screen.getByText('7d')).toBeInTheDocument();
    });

    it('deve renderizar filtros de severidade', () => {
      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Todas')).toBeInTheDocument();
      expect(screen.getByText('Debug')).toBeInTheDocument();
      expect(screen.getByText('Info')).toBeInTheDocument();
      expect(screen.getByText('Warning')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Critical')).toBeInTheDocument();
    });
  });

  describe('Estados de Loading e Erro', () => {
    it('deve mostrar loading inicial', () => {
      mockUseApi.mockImplementation(() => ({
        data: null,
        loading: true,
        error: null,
        refetch: jest.fn()
      }));

      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Carregando dados de correlação...')).toBeInTheDocument();
      expect(screen.getByText('🔄')).toBeInTheDocument();
    });

    it('deve mostrar erro quando API falha', () => {
      const mockError = new Error('API Error');
      mockUseApi.mockImplementation(() => ({
        data: null,
        loading: false,
        error: mockError,
        refetch: jest.fn()
      }));

      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Erro ao carregar dashboard')).toBeInTheDocument();
      expect(screen.getByText('API Error')).toBeInTheDocument();
      expect(screen.getByText('Tentar novamente')).toBeInTheDocument();
    });

    it('deve chamar refetch ao clicar em tentar novamente', async () => {
      const user = userEvent.setup();
      const mockRefetch = jest.fn();
      
      mockUseApi.mockImplementation(() => ({
        data: null,
        loading: false,
        error: new Error('API Error'),
        refetch: mockRefetch
      }));

      render(<CorrelationDashboard />);
      
      const retryButton = screen.getByText('Tentar novamente');
      await user.click(retryButton);
      
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe('Filtros e Controles', () => {
    it('deve filtrar por severidade', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      const severityFilter = screen.getByLabelText('Filtrar por severidade');
      await user.selectOptions(severityFilter, 'warning');
      
      expect(severityFilter).toHaveValue('warning');
    });

    it('deve filtrar por fonte', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      const sourceFilter = screen.getByLabelText('Filtrar por fonte');
      await user.selectOptions(sourceFilter, 'api-gateway');
      
      expect(sourceFilter).toHaveValue('api-gateway');
    });

    it('deve alterar intervalo de tempo', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      const timeRangeButton = screen.getByText('6h');
      await user.click(timeRangeButton);
      
      expect(timeRangeButton).toHaveClass('active');
    });

    it('deve alternar visibilidade da timeline', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      const timelineToggle = screen.getByLabelText('Mostrar/Ocultar Timeline');
      await user.click(timelineToggle);
      
      expect(timelineToggle).toBeChecked();
    });

    it('deve alternar visibilidade das dependências', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      const dependenciesToggle = screen.getByLabelText('Mostrar/Ocultar Dependências');
      await user.click(dependenciesToggle);
      
      expect(dependenciesToggle).toBeChecked();
    });

    it('deve alternar visibilidade dos alertas', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      const alertsToggle = screen.getByLabelText('Mostrar/Ocultar Alertas');
      await user.click(alertsToggle);
      
      expect(alertsToggle).toBeChecked();
    });
  });

  describe('Timeline de Eventos', () => {
    it('deve renderizar eventos na timeline', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('Request received')).toBeInTheDocument();
      expect(screen.getByText('📝')).toBeInTheDocument(); // Log icon
      expect(screen.getByText('📊')).toBeInTheDocument(); // Metric icon
      expect(screen.getByText('🚨')).toBeInTheDocument(); // Alert icon
    });

    it('deve mostrar detalhes do evento ao clicar', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      const eventItem = screen.getByText('Request received').closest('div');
      await user.click(eventItem!);
      
      expect(screen.getByText('Detalhes do Evento')).toBeInTheDocument();
      expect(screen.getByText('event_001')).toBeInTheDocument();
      expect(screen.getByText('api-gateway')).toBeInTheDocument();
    });

    it('deve aplicar filtros na timeline', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard {...defaultProps} />);
      
      // Filtrar por warning
      const severityFilter = screen.getByLabelText('Filtrar por severidade');
      await user.selectOptions(severityFilter, 'warning');
      
      // Apenas eventos warning devem aparecer
      expect(screen.getByText('High response time detected')).toBeInTheDocument();
      expect(screen.queryByText('Request received')).not.toBeInTheDocument();
    });

    it('deve agrupar eventos por tipo', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('Logs (1)')).toBeInTheDocument();
      expect(screen.getByText('Métricas (1)')).toBeInTheDocument();
      expect(screen.getByText('Alertas (1)')).toBeInTheDocument();
    });
  });

  describe('Dependências', () => {
    it('deve renderizar lista de dependências', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('database-service')).toBeInTheDocument();
      expect(screen.getByText('ml-service')).toBeInTheDocument();
      expect(screen.getByText('query_keywords')).toBeInTheDocument();
      expect(screen.getByText('analyze_sentiment')).toBeInTheDocument();
    });

    it('deve mostrar duração das dependências', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('45ms')).toBeInTheDocument();
      expect(screen.getByText('120ms')).toBeInTheDocument();
    });

    it('deve mostrar status das dependências', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      const statusElements = screen.getAllByText('success');
      expect(statusElements).toHaveLength(2);
    });

    it('deve aplicar cores baseadas no status', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      const successElements = screen.getAllByText('success');
      successElements.forEach(element => {
        expect(element).toHaveClass('text-green-600');
      });
    });
  });

  describe('Alertas', () => {
    it('deve renderizar lista de alertas', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('High response time detected')).toBeInTheDocument();
      expect(screen.getByText('warning')).toBeInTheDocument();
    });

    it('deve mostrar timestamp dos alertas', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText(/2025-01-27/)).toBeInTheDocument();
    });

    it('deve aplicar cores baseadas na severidade', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      const warningElement = screen.getByText('warning');
      expect(warningElement).toHaveClass('text-yellow-600');
    });
  });

  describe('Métricas', () => {
    it('deve renderizar métricas do sistema', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('Response Time')).toBeInTheDocument();
      expect(screen.getByText('Throughput')).toBeInTheDocument();
      expect(screen.getByText('150ms')).toBeInTheDocument();
      expect(screen.getByText('1000 req/s')).toBeInTheDocument();
    });

    it('deve mostrar tendências das métricas', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('↗️')).toBeInTheDocument(); // Up trend
      expect(screen.getByText('→')).toBeInTheDocument(); // Stable trend
    });

    it('deve mostrar valores min/max/avg', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      expect(screen.getByText('Min: 80ms')).toBeInTheDocument();
      expect(screen.getByText('Max: 300ms')).toBeInTheDocument();
      expect(screen.getByText('Avg: 120ms')).toBeInTheDocument();
    });
  });

  describe('Seleção de Correlação', () => {
    it('deve mostrar lista de correlações disponíveis', () => {
      render(<CorrelationDashboard />);
      
      expect(screen.getByText('corr_123')).toBeInTheDocument();
      expect(screen.getByText('corr_124')).toBeInTheDocument();
      expect(screen.getByText('corr_125')).toBeInTheDocument();
    });

    it('deve permitir seleção de correlação', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard />);
      
      const correlationSelect = screen.getByLabelText('Selecionar correlação');
      await user.selectOptions(correlationSelect, 'corr_124');
      
      expect(correlationSelect).toHaveValue('corr_124');
    });

    it('deve atualizar dados ao selecionar nova correlação', async () => {
      const user = userEvent.setup();
      const mockRefetch = jest.fn();
      
      mockUseApi.mockImplementation(() => ({
        data: mockDashboardData,
        loading: false,
        error: null,
        refetch: mockRefetch
      }));

      render(<CorrelationDashboard />);
      
      const correlationSelect = screen.getByLabelText('Selecionar correlação');
      await user.selectOptions(correlationSelect, 'corr_124');
      
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe('Auto-refresh', () => {
    it('deve configurar auto-refresh quando habilitado', () => {
      render(<CorrelationDashboard autoRefresh={true} refreshInterval={5000} />);
      
      expect(screen.getByText('Auto-refresh: 5s')).toBeInTheDocument();
    });

    it('deve desabilitar auto-refresh quando configurado', () => {
      render(<CorrelationDashboard autoRefresh={false} />);
      
      expect(screen.getByText('Auto-refresh: Desabilitado')).toBeInTheDocument();
    });

    it('deve permitir refresh manual', async () => {
      const user = userEvent.setup();
      const mockRefetch = jest.fn();
      
      mockUseApi.mockImplementation(() => ({
        data: mockDashboardData,
        loading: false,
        error: null,
        refetch: mockRefetch
      }));

      render(<CorrelationDashboard />);
      
      const refreshButton = screen.getByLabelText('Atualizar dados');
      await user.click(refreshButton);
      
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados para filtros', () => {
      render(<CorrelationDashboard />);
      
      expect(screen.getByLabelText('Filtrar por severidade')).toBeInTheDocument();
      expect(screen.getByLabelText('Filtrar por fonte')).toBeInTheDocument();
      expect(screen.getByLabelText('Selecionar correlação')).toBeInTheDocument();
    });

    it('deve ter roles apropriados para elementos interativos', () => {
      render(<CorrelationDashboard />);
      
      expect(screen.getByRole('button', { name: /atualizar dados/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeInTheDocument();
    });

    it('deve ser navegável por teclado', async () => {
      const user = userEvent.setup();
      render(<CorrelationDashboard />);
      
      const severityFilter = screen.getByLabelText('Filtrar por severidade');
      severityFilter.focus();
      
      await user.tab();
      expect(screen.getByLabelText('Filtrar por fonte')).toHaveFocus();
    });

    it('deve ter aria-labels para elementos de status', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      const statusElements = screen.getAllByText('success');
      statusElements.forEach(element => {
        expect(element).toHaveAttribute('aria-label', 'Status: success');
      });
    });
  });

  describe('Performance', () => {
    it('deve memoizar dados filtrados', () => {
      render(<CorrelationDashboard {...defaultProps} />);
      
      // Verificar se os dados filtrados são calculados apenas quando necessário
      const filteredEvents = screen.getAllByTestId('event-item');
      expect(filteredEvents).toHaveLength(3);
    });

    it('deve otimizar re-renders', () => {
      const { rerender } = render(<CorrelationDashboard {...defaultProps} />);
      
      const initialRender = screen.getByText('Dashboard de Correlação');
      
      rerender(<CorrelationDashboard {...defaultProps} />);
      
      const reRender = screen.getByText('Dashboard de Correlação');
      expect(reRender).toBe(initialRender);
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com lista vazia de eventos', () => {
      mockUseApi.mockImplementation(() => ({
        data: { ...mockDashboardData, events: [] },
        loading: false,
        error: null,
        refetch: jest.fn()
      }));

      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Nenhum evento encontrado')).toBeInTheDocument();
    });

    it('deve lidar com lista vazia de dependências', () => {
      mockUseApi.mockImplementation(() => ({
        data: { ...mockDashboardData, dependencies: [] },
        loading: false,
        error: null,
        refetch: jest.fn()
      }));

      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Nenhuma dependência encontrada')).toBeInTheDocument();
    });

    it('deve lidar com lista vazia de alertas', () => {
      mockUseApi.mockImplementation(() => ({
        data: { ...mockDashboardData, alerts: [] },
        loading: false,
        error: null,
        refetch: jest.fn()
      }));

      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Nenhum alerta encontrado')).toBeInTheDocument();
    });

    it('deve lidar com muitos eventos', () => {
      const manyEvents = Array.from({ length: 100 }, (_, i) => ({
        ...mockCorrelationEvent,
        event_id: `event_${i}`,
        timestamp: new Date(Date.now() + i * 1000).toISOString()
      }));

      mockUseApi.mockImplementation(() => ({
        data: { ...mockDashboardData, events: manyEvents },
        loading: false,
        error: null,
        refetch: jest.fn()
      }));

      render(<CorrelationDashboard />);
      
      expect(screen.getByText('100 eventos')).toBeInTheDocument();
    });

    it('deve lidar com dados malformados', () => {
      mockUseApi.mockImplementation(() => ({
        data: { ...mockDashboardData, events: null, dependencies: undefined },
        loading: false,
        error: null,
        refetch: jest.fn()
      }));

      render(<CorrelationDashboard />);
      
      expect(screen.getByText('Dados inválidos')).toBeInTheDocument();
    });
  });

  describe('Integração com Sistema', () => {
    it('deve integrar com sistema de temas', () => {
      render(<CorrelationDashboard />);
      
      const dashboard = screen.getByTestId('correlation-dashboard');
      expect(dashboard).toHaveClass('dark:bg-gray-900');
    });

    it('deve integrar com sistema de classes utilitárias', () => {
      render(<CorrelationDashboard className="custom-dashboard" />);
      
      const dashboard = screen.getByTestId('correlation-dashboard');
      expect(dashboard).toHaveClass('custom-dashboard');
    });

    it('deve integrar com sistema de animações', () => {
      render(<CorrelationDashboard />);
      
      const timeline = screen.getByTestId('timeline-container');
      expect(timeline).toHaveClass('animate-fade-in');
    });
  });
}); 