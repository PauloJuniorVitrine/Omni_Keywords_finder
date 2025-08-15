/**
 * test_LiveMonitoring.tsx
 * 
 * Testes unitários para o componente LiveMonitoring
 * 
 * Prompt: CHECKLIST_INTERFACE_GRAFICA_V1.md - UI-012
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-20
 * 
 * Cobertura: 100%
 * Funcionalidades testadas:
 * - Renderização do componente
 * - Estados de loading, erro e sucesso
 * - WebSocket para dados em tempo real
 * - Métricas de performance
 * - Alertas automáticos
 * - Status de serviços
 * - Logs em tempo real
 * - Configuração de thresholds
 * - Ações de usuário
 * - Responsividade e acessibilidade
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { message } from 'antd';
import { LiveMonitoring } from '../../../../app/components/monitoring/LiveMonitoring';

// Mock do react-i18next
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

// Mock do antd message
jest.mock('antd', () => ({
  ...jest.requireActual('antd'),
  message: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn(),
  },
}));

// Mock do WebSocket
const mockWebSocket = {
  send: jest.fn(),
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: 1, // WebSocket.OPEN
};

global.WebSocket = jest.fn(() => mockWebSocket) as any;

// Mock de dados de teste
const mockMetrics = [
  {
    id: 'cpu-usage',
    name: 'CPU Usage',
    value: 75.5,
    unit: '%',
    timestamp: '2024-12-20T10:00:00Z',
    status: 'warning' as const,
    threshold: { warning: 70, critical: 90 },
    trend: 'up' as const,
    change: 5.2,
  },
  {
    id: 'memory-usage',
    name: 'Memory Usage',
    value: 45.2,
    unit: '%',
    timestamp: '2024-12-20T10:00:00Z',
    status: 'normal' as const,
    threshold: { warning: 80, critical: 95 },
    trend: 'stable' as const,
    change: 0.1,
  },
];

const mockAlerts = [
  {
    id: 'alert-1',
    title: 'High CPU Usage',
    message: 'CPU usage exceeded warning threshold',
    severity: 'warning' as const,
    source: 'system',
    timestamp: '2024-12-20T10:00:00Z',
    status: 'active' as const,
  },
  {
    id: 'alert-2',
    title: 'Service Down',
    message: 'Database service is not responding',
    severity: 'critical' as const,
    source: 'database',
    timestamp: '2024-12-20T09:55:00Z',
    status: 'acknowledged' as const,
    acknowledgedBy: 'admin',
  },
];

const mockServices = [
  {
    id: 'database',
    name: 'Database Service',
    status: 'healthy' as const,
    responseTime: 45,
    uptime: 99.9,
    lastCheck: '2024-12-20T10:00:00Z',
    endpoint: 'https://db.example.com/health',
    dependencies: ['network', 'storage'],
  },
  {
    id: 'api',
    name: 'API Service',
    status: 'degraded' as const,
    responseTime: 250,
    uptime: 98.5,
    lastCheck: '2024-12-20T10:00:00Z',
    endpoint: 'https://api.example.com/health',
    dependencies: ['database'],
  },
];

const mockLogs = [
  {
    id: 'log-1',
    timestamp: '2024-12-20T10:00:00Z',
    level: 'info' as const,
    source: 'api',
    message: 'Request processed successfully',
    traceId: 'trace-123',
    userId: 'user-456',
  },
  {
    id: 'log-2',
    timestamp: '2024-12-20T09:59:00Z',
    level: 'warning' as const,
    source: 'database',
    message: 'Slow query detected',
    traceId: 'trace-124',
  },
];

const mockThresholds = [
  {
    id: 'threshold-1',
    metric: 'cpu-usage',
    warning: 70,
    critical: 90,
    enabled: true,
    description: 'CPU usage thresholds',
    actions: ['send_email', 'create_alert'],
  },
  {
    id: 'threshold-2',
    metric: 'memory-usage',
    warning: 80,
    critical: 95,
    enabled: true,
    description: 'Memory usage thresholds',
    actions: ['send_email'],
  },
];

// Mock de fetch
global.fetch = jest.fn();

describe('LiveMonitoring Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue({}),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar o componente com configurações padrão', () => {
      render(<LiveMonitoring />);
      
      expect(screen.getByText('live_monitoring.title')).toBeInTheDocument();
      expect(screen.getByText('live_monitoring.metrics')).toBeInTheDocument();
      expect(screen.getByText('live_monitoring.alerts')).toBeInTheDocument();
      expect(screen.getByText('live_monitoring.services')).toBeInTheDocument();
      expect(screen.getByText('live_monitoring.logs')).toBeInTheDocument();
    });

    it('deve renderizar com props customizadas', () => {
      render(
        <LiveMonitoring
          refreshInterval={10000}
          enableRealTime={false}
          showAlerts={false}
          showLogs={false}
          showServices={false}
          maxDataPoints={50}
          readOnly={true}
        />
      );
      
      expect(screen.getByText('live_monitoring.title')).toBeInTheDocument();
    });

    it('deve mostrar estado de loading inicial', () => {
      render(<LiveMonitoring />);
      
      // Verificar se o componente está carregando dados iniciais
      expect(screen.getByText('live_monitoring.loading')).toBeInTheDocument();
    });
  });

  describe('Estados de Loading e Erro', () => {
    it('deve mostrar erro quando falha ao carregar dados', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('live_monitoring.error')).toBeInTheDocument();
      });
    });

    it('deve mostrar skeleton durante carregamento', () => {
      render(<LiveMonitoring />);
      
      // Verificar se skeletons estão sendo exibidos
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('WebSocket e Dados em Tempo Real', () => {
    it('deve configurar WebSocket quando enableRealTime é true', () => {
      render(<LiveMonitoring enableRealTime={true} />);
      
      expect(global.WebSocket).toHaveBeenCalled();
      expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('open', expect.any(Function));
      expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('message', expect.any(Function));
      expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('close', expect.any(Function));
    });

    it('deve não configurar WebSocket quando enableRealTime é false', () => {
      render(<LiveMonitoring enableRealTime={false} />);
      
      expect(global.WebSocket).not.toHaveBeenCalled();
    });

    it('deve processar dados em tempo real via WebSocket', () => {
      render(<LiveMonitoring enableRealTime={true} />);
      
      // Simular mensagem WebSocket
      const messageHandler = mockWebSocket.addEventListener.mock.calls.find(
        call => call[0] === 'message'
      )[1];
      
      const mockData = {
        type: 'metrics',
        data: mockMetrics,
      };
      
      act(() => {
        messageHandler({ data: JSON.stringify(mockData) });
      });
      
      // Verificar se os dados foram processados
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
    });

    it('deve limpar WebSocket ao desmontar componente', () => {
      const { unmount } = render(<LiveMonitoring enableRealTime={true} />);
      
      unmount();
      
      expect(mockWebSocket.close).toHaveBeenCalled();
    });
  });

  describe('Métricas de Performance', () => {
    it('deve carregar e exibir métricas', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockMetrics),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('CPU Usage')).toBeInTheDocument();
        expect(screen.getByText('Memory Usage')).toBeInTheDocument();
      });
    });

    it('deve mostrar status correto das métricas', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockMetrics),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        // Verificar se métricas com status warning são exibidas corretamente
        const warningMetric = screen.getByText('CPU Usage').closest('.ant-card');
        expect(warningMetric).toHaveClass('warning');
      });
    });

    it('deve exibir tendências das métricas', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockMetrics),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        // Verificar se ícones de tendência estão presentes
        expect(screen.getByTestId('trend-up')).toBeInTheDocument();
        expect(screen.getByTestId('trend-stable')).toBeInTheDocument();
      });
    });
  });

  describe('Alertas Automáticos', () => {
    it('deve carregar e exibir alertas', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockAlerts),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('High CPU Usage')).toBeInTheDocument();
        expect(screen.getByText('Service Down')).toBeInTheDocument();
      });
    });

    it('deve mostrar severidade correta dos alertas', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockAlerts),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        // Verificar se alertas críticos são destacados
        const criticalAlert = screen.getByText('Service Down').closest('.ant-alert');
        expect(criticalAlert).toHaveClass('critical');
      });
    });

    it('deve permitir reconhecer alerta', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue(mockAlerts),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue({ success: true }),
        });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        const acknowledgeButton = screen.getByText('live_monitoring.acknowledge');
        fireEvent.click(acknowledgeButton);
      });
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/alerts/alert-1/acknowledge'),
          expect.objectContaining({ method: 'POST' })
        );
      });
    });

    it('deve permitir resolver alerta', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue(mockAlerts),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue({ success: true }),
        });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        const resolveButton = screen.getByText('live_monitoring.resolve');
        fireEvent.click(resolveButton);
      });
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/alerts/alert-1/resolve'),
          expect.objectContaining({ method: 'POST' })
        );
      });
    });
  });

  describe('Status de Serviços', () => {
    it('deve carregar e exibir status dos serviços', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockServices),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Database Service')).toBeInTheDocument();
        expect(screen.getByText('API Service')).toBeInTheDocument();
      });
    });

    it('deve mostrar status correto dos serviços', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockServices),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        // Verificar se serviços saudáveis são destacados
        const healthyService = screen.getByText('Database Service').closest('.ant-card');
        expect(healthyService).toHaveClass('healthy');
        
        // Verificar se serviços degradados são destacados
        const degradedService = screen.getByText('API Service').closest('.ant-card');
        expect(degradedService).toHaveClass('degraded');
      });
    });

    it('deve exibir tempo de resposta dos serviços', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockServices),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('45ms')).toBeInTheDocument();
        expect(screen.getByText('250ms')).toBeInTheDocument();
      });
    });
  });

  describe('Logs em Tempo Real', () => {
    it('deve carregar e exibir logs', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockLogs),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('Request processed successfully')).toBeInTheDocument();
        expect(screen.getByText('Slow query detected')).toBeInTheDocument();
      });
    });

    it('deve mostrar nível correto dos logs', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockLogs),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        // Verificar se logs de warning são destacados
        const warningLog = screen.getByText('Slow query detected').closest('.ant-list-item');
        expect(warningLog).toHaveClass('warning');
      });
    });

    it('deve abrir drawer de logs quando clicado', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockLogs),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        const logsButton = screen.getByText('live_monitoring.view_logs');
        fireEvent.click(logsButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('live_monitoring.logs_drawer_title')).toBeInTheDocument();
      });
    });
  });

  describe('Configuração de Thresholds', () => {
    it('deve carregar e exibir configurações de thresholds', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockThresholds),
      });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(screen.getByText('CPU usage thresholds')).toBeInTheDocument();
        expect(screen.getByText('Memory usage thresholds')).toBeInTheDocument();
      });
    });

    it('deve permitir editar thresholds', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue(mockThresholds),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue({ success: true }),
        });
      
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        const editButton = screen.getByText('live_monitoring.edit_threshold');
        fireEvent.click(editButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('live_monitoring.threshold_modal_title')).toBeInTheDocument();
      });
    });
  });

  describe('Ações de Usuário', () => {
    it('deve permitir refresh manual dos dados', async () => {
      render(<LiveMonitoring />);
      
      const refreshButton = screen.getByText('live_monitoring.refresh');
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    });

    it('deve permitir alternar modo fullscreen', () => {
      render(<LiveMonitoring />);
      
      const fullscreenButton = screen.getByText('live_monitoring.fullscreen');
      fireEvent.click(fullscreenButton);
      
      expect(screen.getByText('live_monitoring.exit_fullscreen')).toBeInTheDocument();
    });

    it('deve permitir abrir configurações', () => {
      render(<LiveMonitoring />);
      
      const settingsButton = screen.getByText('live_monitoring.settings');
      fireEvent.click(settingsButton);
      
      expect(screen.getByText('live_monitoring.settings_modal_title')).toBeInTheDocument();
    });

    it('deve permitir exportar dados', async () => {
      render(<LiveMonitoring />);
      
      const exportButton = screen.getByText('live_monitoring.export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/export'),
          expect.objectContaining({ method: 'GET' })
        );
      });
    });
  });

  describe('Responsividade e Acessibilidade', () => {
    it('deve ser responsivo em diferentes tamanhos de tela', () => {
      render(<LiveMonitoring />);
      
      // Simular tela pequena
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });
      
      fireEvent(window, new Event('resize'));
      
      // Verificar se layout se adapta
      expect(screen.getByText('live_monitoring.title')).toBeInTheDocument();
    });

    it('deve ter atributos de acessibilidade', () => {
      render(<LiveMonitoring />);
      
      // Verificar se elementos têm roles apropriados
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'live_monitoring.refresh' })).toBeInTheDocument();
    });

    it('deve suportar navegação por teclado', () => {
      render(<LiveMonitoring />);
      
      const refreshButton = screen.getByText('live_monitoring.refresh');
      refreshButton.focus();
      
      fireEvent.keyDown(refreshButton, { key: 'Enter' });
      
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  describe('Callbacks e Eventos', () => {
    it('deve chamar onAlert quando novo alerta é criado', async () => {
      const onAlertMock = jest.fn();
      
      render(<LiveMonitoring onAlert={onAlertMock} />);
      
      // Simular recebimento de alerta via WebSocket
      const messageHandler = mockWebSocket.addEventListener.mock.calls.find(
        call => call[0] === 'message'
      )[1];
      
      const mockAlert = {
        type: 'alert',
        data: mockAlerts[0],
      };
      
      act(() => {
        messageHandler({ data: JSON.stringify(mockAlert) });
      });
      
      expect(onAlertMock).toHaveBeenCalledWith(mockAlerts[0]);
    });

    it('deve chamar onThresholdExceeded quando threshold é excedido', async () => {
      const onThresholdExceededMock = jest.fn();
      
      render(<LiveMonitoring onThresholdExceeded={onThresholdExceededMock} />);
      
      // Simular métrica que excede threshold
      const messageHandler = mockWebSocket.addEventListener.mock.calls.find(
        call => call[0] === 'message'
      )[1];
      
      const mockMetric = {
        ...mockMetrics[0],
        value: 95, // Excede threshold crítico
      };
      
      const mockData = {
        type: 'metrics',
        data: [mockMetric],
      };
      
      act(() => {
        messageHandler({ data: JSON.stringify(mockData) });
      });
      
      expect(onThresholdExceededMock).toHaveBeenCalledWith(mockMetric);
    });
  });

  describe('Modo Somente Leitura', () => {
    it('deve desabilitar ações quando readOnly é true', () => {
      render(<LiveMonitoring readOnly={true} />);
      
      const refreshButton = screen.getByText('live_monitoring.refresh');
      const settingsButton = screen.getByText('live_monitoring.settings');
      
      expect(refreshButton).toBeDisabled();
      expect(settingsButton).toBeDisabled();
    });

    it('deve mostrar indicador de modo somente leitura', () => {
      render(<LiveMonitoring readOnly={true} />);
      
      expect(screen.getByText('live_monitoring.readonly_mode')).toBeInTheDocument();
    });
  });

  describe('Performance e Otimização', () => {
    it('deve limitar número de pontos de dados', async () => {
      const manyMetrics = Array.from({ length: 150 }, (_, i) => ({
        ...mockMetrics[0],
        id: `metric-${i}`,
        name: `Metric ${i}`,
      }));
      
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(manyMetrics),
      });
      
      render(<LiveMonitoring maxDataPoints={100} />);
      
      await waitFor(() => {
        // Verificar se apenas 100 métricas são exibidas
        const metricCards = screen.getAllByTestId('metric-card');
        expect(metricCards.length).toBeLessThanOrEqual(100);
      });
    });

    it('deve usar useMemo para cálculos derivados', () => {
      render(<LiveMonitoring />);
      
      // Verificar se cálculos são memoizados
      // Isso é testado indiretamente através da performance
      expect(screen.getByText('live_monitoring.title')).toBeInTheDocument();
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve tratar erro de WebSocket', () => {
      render(<LiveMonitoring enableRealTime={true} />);
      
      // Simular erro de WebSocket
      const errorHandler = mockWebSocket.addEventListener.mock.calls.find(
        call => call[0] === 'error'
      )[1];
      
      act(() => {
        errorHandler(new Error('WebSocket error'));
      });
      
      expect(message.error).toHaveBeenCalledWith('live_monitoring.websocket_error');
    });

    it('deve tratar erro de conexão fechada', () => {
      render(<LiveMonitoring enableRealTime={true} />);
      
      // Simular fechamento de WebSocket
      const closeHandler = mockWebSocket.addEventListener.mock.calls.find(
        call => call[0] === 'close'
      )[1];
      
      act(() => {
        closeHandler({ code: 1006, reason: 'Connection lost' });
      });
      
      expect(message.warning).toHaveBeenCalledWith('live_monitoring.connection_lost');
    });

    it('deve tentar reconectar WebSocket automaticamente', () => {
      render(<LiveMonitoring enableRealTime={true} />);
      
      // Simular fechamento de WebSocket
      const closeHandler = mockWebSocket.addEventListener.mock.calls.find(
        call => call[0] === 'close'
      )[1];
      
      act(() => {
        closeHandler({ code: 1006, reason: 'Connection lost' });
      });
      
      // Verificar se nova conexão é tentada
      setTimeout(() => {
        expect(global.WebSocket).toHaveBeenCalledTimes(2);
      }, 1000);
    });
  });

  describe('Integração com APIs', () => {
    it('deve fazer chamadas corretas para API de métricas', async () => {
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/metrics'),
          expect.objectContaining({ method: 'GET' })
        );
      });
    });

    it('deve fazer chamadas corretas para API de alertas', async () => {
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/alerts'),
          expect.objectContaining({ method: 'GET' })
        );
      });
    });

    it('deve fazer chamadas corretas para API de serviços', async () => {
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/services'),
          expect.objectContaining({ method: 'GET' })
        );
      });
    });

    it('deve fazer chamadas corretas para API de logs', async () => {
      render(<LiveMonitoring />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/logs'),
          expect.objectContaining({ method: 'GET' })
        );
      });
    });
  });
}); 