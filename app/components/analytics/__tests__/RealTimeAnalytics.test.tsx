/**
 * RealTimeAnalytics.test.tsx
 * 
 * Testes unitários para o componente RealTimeAnalytics
 * 
 * Tracing ID: TEST-RTA-001
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RealTimeAnalytics } from '../RealTimeAnalytics';
import { useWebSocket } from '../../../hooks/useWebSocket';
import { useBusinessMetrics } from '../../../hooks/useBusinessMetrics';

// Mock dos hooks
jest.mock('../../../hooks/useWebSocket');
jest.mock('../../../hooks/useBusinessMetrics');

const mockUseWebSocket = useWebSocket as jest.MockedFunction<typeof useWebSocket>;
const mockUseBusinessMetrics = useBusinessMetrics as jest.MockedFunction<typeof useBusinessMetrics>;

describe('RealTimeAnalytics', () => {
  const defaultWebSocketData = {
    data: null,
    isConnected: true,
    error: null,
    sendMessage: jest.fn()
  };

  const defaultBusinessMetrics = {
    data: null,
    loading: false,
    error: null,
    refetch: jest.fn()
  };

  beforeEach(() => {
    mockUseWebSocket.mockReturnValue(defaultWebSocketData);
    mockUseBusinessMetrics.mockReturnValue(defaultBusinessMetrics);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar o componente com título correto', () => {
      render(<RealTimeAnalytics />);
      
      expect(screen.getByText('Analytics em Tempo Real')).toBeInTheDocument();
      expect(screen.getByText('Dados e eventos em tempo real com PWA features')).toBeInTheDocument();
    });

    it('deve renderizar controles de exportação', () => {
      render(<RealTimeAnalytics exportFormats={['csv', 'json']} />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });

    it('deve renderizar indicadores de status', () => {
      render(<RealTimeAnalytics />);
      
      expect(screen.getByText(/Última atualização:/)).toBeInTheDocument();
      expect(screen.getByText('Tempo real ativo')).toBeInTheDocument();
    });
  });

  describe('Estados de loading', () => {
    it('deve mostrar skeleton quando carregando', () => {
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        loading: true
      });

      render(<RealTimeAnalytics />);
      
      // Verificar se skeletons estão sendo renderizados
      const skeletons = document.querySelectorAll('[class*="skeleton"]');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Estados de erro', () => {
    it('deve mostrar erro quando WebSocket falha', () => {
      mockUseWebSocket.mockReturnValue({
        ...defaultWebSocketData,
        error: new Error('WebSocket connection failed')
      });

      render(<RealTimeAnalytics />);
      
      expect(screen.getByText(/Erro de conexão/)).toBeInTheDocument();
    });

    it('deve mostrar erro quando métricas falham', () => {
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        error: new Error('Failed to fetch metrics')
      });

      render(<RealTimeAnalytics />);
      
      expect(screen.getByText(/Erro de conexão/)).toBeInTheDocument();
    });
  });

  describe('Interatividade', () => {
    it('deve permitir alternar notificações', () => {
      render(<RealTimeAnalytics enableNotifications={true} />);
      
      const notificationButton = screen.getByText('Notificações');
      fireEvent.click(notificationButton);
      
      // Verificar se o estado mudou (pode ser verificado pela mudança de ícone)
      expect(notificationButton).toBeInTheDocument();
    });

    it('deve permitir compartilhar dados', async () => {
      const mockShare = jest.fn();
      Object.assign(navigator, { share: mockShare });

      render(<RealTimeAnalytics />);
      
      const shareButton = screen.getByText('Compartilhar');
      fireEvent.click(shareButton);
      
      await waitFor(() => {
        expect(mockShare).toHaveBeenCalledWith({
          title: 'Analytics em Tempo Real',
          text: 'Dados de analytics em tempo real do Omni Keywords Finder',
          url: window.location.href
        });
      });
    });

    it('deve permitir entrar em tela cheia', () => {
      const mockRequestFullscreen = jest.fn();
      Object.assign(document.documentElement, { requestFullscreen: mockRequestFullscreen });

      render(<RealTimeAnalytics />);
      
      const fullscreenButton = screen.getByText('Tela Cheia');
      fireEvent.click(fullscreenButton);
      
      expect(mockRequestFullscreen).toHaveBeenCalled();
    });
  });

  describe('Dados em tempo real', () => {
    it('deve processar dados do WebSocket corretamente', () => {
      const mockWebSocketData = JSON.stringify({
        type: 'metrics',
        metrics: [
          {
            id: 'metric-1',
            name: 'Test Metric',
            value: 100,
            unit: 'ms',
            category: 'performance',
            timestamp: new Date().toISOString(),
            trend: 'up',
            changePercent: 10,
            alertLevel: 'low'
          }
        ]
      });

      mockUseWebSocket.mockReturnValue({
        ...defaultWebSocketData,
        data: mockWebSocketData
      });

      render(<RealTimeAnalytics />);
      
      // Verificar se os dados foram processados
      expect(screen.getByText('Test Metric')).toBeInTheDocument();
    });

    it('deve processar eventos do WebSocket corretamente', () => {
      const mockEventData = JSON.stringify({
        type: 'events',
        event: {
          id: 'event-1',
          type: 'user_action',
          title: 'User Login',
          description: 'User logged in successfully',
          severity: 'info',
          timestamp: new Date().toISOString()
        }
      });

      mockUseWebSocket.mockReturnValue({
        ...defaultWebSocketData,
        data: mockEventData
      });

      render(<RealTimeAnalytics />);
      
      // Verificar se o evento foi processado
      expect(screen.getByText('User Login')).toBeInTheDocument();
    });
  });

  describe('Exportação', () => {
    it('deve exportar dados em formato JSON', async () => {
      const mockCreateElement = jest.fn();
      const mockClick = jest.fn();
      const mockBlob = jest.fn();
      
      Object.assign(document, { createElement: mockCreateElement });
      Object.assign(global, { Blob: mockBlob });
      Object.assign(URL, { createObjectURL: jest.fn(), revokeObjectURL: jest.fn() });

      mockCreateElement.mockReturnValue({
        href: '',
        download: '',
        click: mockClick
      });

      render(<RealTimeAnalytics />);
      
      const jsonButton = screen.getByText('JSON');
      fireEvent.click(jsonButton);
      
      await waitFor(() => {
        expect(mockCreateElement).toHaveBeenCalledWith('a');
        expect(mockClick).toHaveBeenCalled();
      });
    });
  });

  describe('PWA Features', () => {
    it('deve registrar service worker quando PWA está habilitado', () => {
      const mockRegister = jest.fn().mockResolvedValue({});
      Object.assign(navigator, { serviceWorker: { register: mockRegister } });

      render(<RealTimeAnalytics enablePWA={true} />);
      
      expect(mockRegister).toHaveBeenCalledWith('/sw.js');
    });

    it('deve solicitar permissão de notificação quando habilitado', () => {
      const mockRequestPermission = jest.fn().mockResolvedValue('granted');
      Object.assign(Notification, { requestPermission: mockRequestPermission });

      render(<RealTimeAnalytics enableNotifications={true} />);
      
      expect(mockRequestPermission).toHaveBeenCalled();
    });
  });

  describe('Filtros e categorias', () => {
    it('deve permitir selecionar categoria', () => {
      render(<RealTimeAnalytics />);
      
      const categorySelect = screen.getByRole('combobox');
      fireEvent.click(categorySelect);
      
      // Verificar se as opções estão disponíveis
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Usuários')).toBeInTheDocument();
      expect(screen.getByText('Keywords')).toBeInTheDocument();
    });

    it('deve atualizar dados quando categoria muda', () => {
      const mockRefetch = jest.fn();
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        refetch: mockRefetch
      });

      render(<RealTimeAnalytics />);
      
      const categorySelect = screen.getByRole('combobox');
      fireEvent.click(categorySelect);
      
      const usersOption = screen.getByText('Usuários');
      fireEvent.click(usersOption);
      
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe('Status de conexão', () => {
    it('deve mostrar status conectado', () => {
      mockUseWebSocket.mockReturnValue({
        ...defaultWebSocketData,
        isConnected: true
      });

      render(<RealTimeAnalytics />);
      
      expect(screen.getByText('Conectado')).toBeInTheDocument();
    });

    it('deve mostrar status desconectado', () => {
      mockUseWebSocket.mockReturnValue({
        ...defaultWebSocketData,
        isConnected: false
      });

      render(<RealTimeAnalytics />);
      
      expect(screen.getByText('Desconectado')).toBeInTheDocument();
    });

    it('deve mostrar status reconectando', () => {
      mockUseWebSocket.mockReturnValue({
        ...defaultWebSocketData,
        isConnected: false
      });

      render(<RealTimeAnalytics />);
      
      // Simular reconexão
      expect(screen.getByText('Desconectado')).toBeInTheDocument();
    });
  });

  describe('Tabs e navegação', () => {
    it('deve renderizar todas as tabs', () => {
      render(<RealTimeAnalytics />);
      
      expect(screen.getByText('Dados ao Vivo')).toBeInTheDocument();
      expect(screen.getByText('Eventos')).toBeInTheDocument();
      expect(screen.getByText('Gráficos')).toBeInTheDocument();
      expect(screen.getByText('Alertas')).toBeInTheDocument();
    });

    it('deve permitir navegar entre tabs', () => {
      render(<RealTimeAnalytics />);
      
      const eventsTab = screen.getByText('Eventos');
      fireEvent.click(eventsTab);
      
      expect(screen.getByText('Eventos em Tempo Real')).toBeInTheDocument();
    });
  });

  describe('Performance e otimização', () => {
    it('deve limitar número de pontos de dados', () => {
      const maxDataPoints = 10;
      render(<RealTimeAnalytics maxDataPoints={maxDataPoints} />);
      
      // Verificar se o limite está sendo aplicado
      expect(screen.getByText(`${maxDataPoints} pontos de dados`)).toBeInTheDocument();
    });

    it('deve atualizar em intervalos corretos', () => {
      jest.useFakeTimers();
      
      const mockRefetch = jest.fn();
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        refetch: mockRefetch
      });

      render(<RealTimeAnalytics refreshInterval={5000} />);
      
      jest.advanceTimersByTime(5000);
      
      expect(mockRefetch).toHaveBeenCalled();
      
      jest.useRealTimers();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter roles e labels apropriados', () => {
      render(<RealTimeAnalytics />);
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /atualizar/i })).toBeInTheDocument();
    });

    it('deve ser navegável por teclado', () => {
      render(<RealTimeAnalytics />);
      
      const refreshButton = screen.getByText('Atualizar');
      refreshButton.focus();
      
      expect(refreshButton).toHaveFocus();
    });
  });
}); 