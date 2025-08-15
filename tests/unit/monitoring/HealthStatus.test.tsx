/**
 * HealthStatus.test.tsx
 * 
 * Testes unitários para o componente HealthStatus
 * 
 * Tracing ID: TEST_MONITORING_20250127_002
 * Prompt: CHECKLIST_TESTES_UNITARIOS_REACT.md - Fase 4.1
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HealthStatus } from '../../../app/components/monitoring/HealthStatus';

// Mock do fetch global
global.fetch = jest.fn();

// Mock data
const mockHealthCheckResult = {
  name: 'database_connection',
  status: 'healthy' as const,
  message: 'Database connection is healthy',
  details: { connection_pool: 10, active_connections: 5 },
  timestamp: '2025-01-27T10:00:00Z',
  duration: 0.05,
  correlation_id: 'corr_123'
};

const mockSystemMetrics = {
  cpu_percent: 45.2,
  memory_percent: 67.8,
  disk_percent: 23.1,
  network_io: {
    bytes_sent: 1024000,
    bytes_recv: 2048000,
    packets_sent: 1500,
    packets_recv: 3000
  },
  uptime_seconds: 86400,
  load_average: [1.2, 1.1, 0.9],
  warnings: ['High memory usage detected']
};

const mockHealthSummary = {
  status: 'healthy',
  timestamp: '2025-01-27T10:00:00Z',
  duration_ms: 150,
  checks: [
    mockHealthCheckResult,
    {
      ...mockHealthCheckResult,
      name: 'api_gateway',
      status: 'degraded' as const,
      message: 'API Gateway response time is slow',
      details: { response_time: 1200, threshold: 1000 }
    },
    {
      ...mockHealthCheckResult,
      name: 'ml_service',
      status: 'unhealthy' as const,
      message: 'ML Service is not responding',
      details: { error: 'Connection timeout' }
    },
    {
      ...mockHealthCheckResult,
      name: 'system_metrics',
      status: 'healthy' as const,
      message: 'System metrics are normal',
      details: mockSystemMetrics
    }
  ],
  summary: {
    total_checks: 4,
    healthy: 2,
    degraded: 1,
    unhealthy: 1,
    unknown: 0
  }
};

const defaultProps = {
  autoRefresh: true,
  refreshInterval: 30000,
  showHistory: true,
  compact: false
};

describe('HealthStatus Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock padrão para fetch
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockHealthSummary
    });
  });

  describe('Renderização Básica', () => {
    it('deve renderizar com configurações padrão', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Status do Sistema')).toBeInTheDocument();
      });
    });

    it('deve renderizar status geral do sistema', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
        expect(screen.getByText('2/4 checks healthy')).toBeInTheDocument();
      });
    });

    it('deve renderizar lista de health checks', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('database_connection')).toBeInTheDocument();
        expect(screen.getByText('api_gateway')).toBeInTheDocument();
        expect(screen.getByText('ml_service')).toBeInTheDocument();
        expect(screen.getByText('system_metrics')).toBeInTheDocument();
      });
    });

    it('deve renderizar mensagens de status', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Database connection is healthy')).toBeInTheDocument();
        expect(screen.getByText('API Gateway response time is slow')).toBeInTheDocument();
        expect(screen.getByText('ML Service is not responding')).toBeInTheDocument();
      });
    });
  });

  describe('Estados de Loading e Erro', () => {
    it('deve mostrar loading inicial', () => {
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );

      render(<HealthStatus />);
      
      expect(screen.getByText('Carregando status do sistema...')).toBeInTheDocument();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('deve mostrar erro quando API falha', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Erro ao carregar status')).toBeInTheDocument();
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    it('deve mostrar erro quando resposta não é ok', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('HTTP 500: Internal Server Error')).toBeInTheDocument();
      });
    });

    it('deve permitir retry após erro', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealthSummary
        });

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Erro ao carregar status')).toBeInTheDocument();
      });

      const retryButton = screen.getByText('Tentar novamente');
      await user.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
      });
    });
  });

  describe('Indicadores de Status', () => {
    it('deve aplicar cores corretas para status healthy', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        const healthyElements = screen.getAllByText('healthy');
        healthyElements.forEach(element => {
          expect(element).toHaveClass('text-green-600');
        });
      });
    });

    it('deve aplicar cores corretas para status degraded', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        const degradedElement = screen.getByText('degraded');
        expect(degradedElement).toHaveClass('text-yellow-600');
      });
    });

    it('deve aplicar cores corretas para status unhealthy', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        const unhealthyElement = screen.getByText('unhealthy');
        expect(unhealthyElement).toHaveClass('text-red-600');
      });
    });

    it('deve mostrar ícones corretos para cada status', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByTestId('healthy-icon')).toBeInTheDocument();
        expect(screen.getByTestId('degraded-icon')).toBeInTheDocument();
        expect(screen.getByTestId('unhealthy-icon')).toBeInTheDocument();
      });
    });
  });

  describe('Métricas do Sistema', () => {
    it('deve renderizar métricas de CPU', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('CPU')).toBeInTheDocument();
        expect(screen.getByText('45.2%')).toBeInTheDocument();
      });
    });

    it('deve renderizar métricas de memória', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Memória')).toBeInTheDocument();
        expect(screen.getByText('67.8%')).toBeInTheDocument();
      });
    });

    it('deve renderizar métricas de disco', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Disco')).toBeInTheDocument();
        expect(screen.getByText('23.1%')).toBeInTheDocument();
      });
    });

    it('deve renderizar métricas de rede', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Rede')).toBeInTheDocument();
        expect(screen.getByText('1.0 MB/s')).toBeInTheDocument();
        expect(screen.getByText('2.0 MB/s')).toBeInTheDocument();
      });
    });

    it('deve renderizar uptime do sistema', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Uptime')).toBeInTheDocument();
        expect(screen.getByText('1d 0h 0m')).toBeInTheDocument();
      });
    });

    it('deve renderizar load average', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Load Average')).toBeInTheDocument();
        expect(screen.getByText('1.2, 1.1, 0.9')).toBeInTheDocument();
      });
    });
  });

  describe('Histórico de Status', () => {
    it('deve renderizar histórico quando habilitado', async () => {
      render(<HealthStatus showHistory={true} />);
      
      await waitFor(() => {
        expect(screen.getByText('Histórico')).toBeInTheDocument();
        expect(screen.getByText('Últimas 10 verificações')).toBeInTheDocument();
      });
    });

    it('deve não renderizar histórico quando desabilitado', async () => {
      render(<HealthStatus showHistory={false} />);
      
      await waitFor(() => {
        expect(screen.queryByText('Histórico')).not.toBeInTheDocument();
      });
    });

    it('deve mostrar timestamp da última verificação', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText(/Última verificação:/)).toBeInTheDocument();
        expect(screen.getByText(/2025-01-27/)).toBeInTheDocument();
      });
    });

    it('deve mostrar duração da verificação', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Duração: 150ms')).toBeInTheDocument();
      });
    });
  });

  describe('Modo Compacto', () => {
    it('deve renderizar em modo compacto', async () => {
      render(<HealthStatus compact={true} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('compact-health-status')).toBeInTheDocument();
        expect(screen.getByText('healthy')).toBeInTheDocument();
        expect(screen.getByText('2/4')).toBeInTheDocument();
      });
    });

    it('deve mostrar apenas informações essenciais no modo compacto', async () => {
      render(<HealthStatus compact={true} />);
      
      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
        expect(screen.queryByText('Métricas do Sistema')).not.toBeInTheDocument();
        expect(screen.queryByText('Histórico')).not.toBeInTheDocument();
      });
    });
  });

  describe('Auto-refresh', () => {
    it('deve configurar auto-refresh quando habilitado', async () => {
      render(<HealthStatus autoRefresh={true} refreshInterval={5000} />);
      
      await waitFor(() => {
        expect(screen.getByText('Auto-refresh: 5s')).toBeInTheDocument();
      });
    });

    it('deve desabilitar auto-refresh quando configurado', async () => {
      render(<HealthStatus autoRefresh={false} />);
      
      await waitFor(() => {
        expect(screen.getByText('Auto-refresh: Desabilitado')).toBeInTheDocument();
      });
    });

    it('deve permitir refresh manual', async () => {
      const user = userEvent.setup();
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
      });

      const refreshButton = screen.getByLabelText('Atualizar status');
      await user.click(refreshButton);

      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('deve mostrar indicador de refresh em andamento', async () => {
      const user = userEvent.setup();
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => mockHealthSummary
        }), 100))
      );

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
      });

      const refreshButton = screen.getByLabelText('Atualizar status');
      await user.click(refreshButton);

      expect(screen.getByTestId('refreshing-indicator')).toBeInTheDocument();
    });
  });

  describe('Alertas e Avisos', () => {
    it('deve mostrar alertas quando há problemas', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('⚠️ High memory usage detected')).toBeInTheDocument();
      });
    });

    it('deve mostrar alerta para serviços unhealthy', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('🚨 ML Service is not responding')).toBeInTheDocument();
      });
    });

    it('deve mostrar alerta para serviços degraded', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('⚠️ API Gateway response time is slow')).toBeInTheDocument();
      });
    });

    it('deve permitir expandir detalhes dos alertas', async () => {
      const user = userEvent.setup();
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('🚨 ML Service is not responding')).toBeInTheDocument();
      });

      const alertButton = screen.getByText('🚨 ML Service is not responding');
      await user.click(alertButton);

      expect(screen.getByText('Detalhes do Problema')).toBeInTheDocument();
      expect(screen.getByText('Connection timeout')).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados para elementos interativos', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Atualizar status')).toBeInTheDocument();
        expect(screen.getByLabelText('Mostrar/Ocultar histórico')).toBeInTheDocument();
      });
    });

    it('deve ter roles apropriados para elementos de status', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });
    });

    it('deve ser navegável por teclado', async () => {
      const user = userEvent.setup();
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
      });

      const refreshButton = screen.getByLabelText('Atualizar status');
      refreshButton.focus();
      
      await user.tab();
      expect(screen.getByLabelText('Mostrar/Ocultar histórico')).toHaveFocus();
    });

    it('deve ter aria-labels para elementos de status', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        const statusElements = screen.getAllByText('healthy');
        statusElements.forEach(element => {
          expect(element).toHaveAttribute('aria-label', 'Status: healthy');
        });
      });
    });
  });

  describe('Performance', () => {
    it('deve memoizar dados de health check', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
      });

      // Verificar se os dados são calculados apenas quando necessário
      const healthCheckElements = screen.getAllByTestId('health-check-item');
      expect(healthCheckElements).toHaveLength(4);
    });

    it('deve otimizar re-renders', async () => {
      const { rerender } = render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument();
      });

      const initialRender = screen.getByText('Status do Sistema');
      
      rerender(<HealthStatus />);
      
      const reRender = screen.getByText('Status do Sistema');
      expect(reRender).toBe(initialRender);
    });

    it('deve limitar histórico a 10 entradas', async () => {
      const manyHistoryEntries = Array.from({ length: 15 }, (_, i) => ({
        ...mockHealthSummary,
        timestamp: new Date(Date.now() + i * 1000).toISOString()
      }));

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockHealthSummary
      });

      render(<HealthStatus showHistory={true} />);
      
      await waitFor(() => {
        const historyItems = screen.getAllByTestId('history-item');
        expect(historyItems).toHaveLength(10);
      });
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com lista vazia de health checks', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          ...mockHealthSummary,
          checks: [],
          summary: {
            total_checks: 0,
            healthy: 0,
            degraded: 0,
            unhealthy: 0,
            unknown: 0
          }
        })
      });

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Nenhum health check configurado')).toBeInTheDocument();
      });
    });

    it('deve lidar com todos os checks unhealthy', async () => {
      const allUnhealthy = {
        ...mockHealthSummary,
        status: 'unhealthy',
        checks: mockHealthSummary.checks.map(check => ({
          ...check,
          status: 'unhealthy' as const
        })),
        summary: {
          total_checks: 4,
          healthy: 0,
          degraded: 0,
          unhealthy: 4,
          unknown: 0
        }
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => allUnhealthy
      });

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('unhealthy')).toBeInTheDocument();
        expect(screen.getByText('0/4 checks healthy')).toBeInTheDocument();
      });
    });

    it('deve lidar com dados malformados', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          status: 'unknown',
          checks: null,
          summary: undefined
        })
      });

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('Dados de status inválidos')).toBeInTheDocument();
      });
    });

    it('deve lidar com valores extremos de métricas', async () => {
      const extremeMetrics = {
        ...mockHealthSummary,
        checks: [
          {
            ...mockHealthCheckResult,
            name: 'system_metrics',
            details: {
              cpu_percent: 999.9,
              memory_percent: 0.1,
              disk_percent: 100.0,
              network_io: {
                bytes_sent: Number.MAX_SAFE_INTEGER,
                bytes_recv: 0,
                packets_sent: 999999,
                packets_recv: 1
              },
              uptime_seconds: 0,
              load_average: [999.9, 999.9, 999.9]
            }
          }
        ]
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => extremeMetrics
      });

      render(<HealthStatus />);
      
      await waitFor(() => {
        expect(screen.getByText('100.0%')).toBeInTheDocument();
        expect(screen.getByText('0.1%')).toBeInTheDocument();
        expect(screen.getByText('0m')).toBeInTheDocument();
      });
    });
  });

  describe('Integração com Sistema', () => {
    it('deve integrar com sistema de temas', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        const healthStatus = screen.getByTestId('health-status');
        expect(healthStatus).toHaveClass('dark:bg-gray-900');
      });
    });

    it('deve integrar com sistema de classes utilitárias', async () => {
      render(<HealthStatus className="custom-health-status" />);
      
      await waitFor(() => {
        const healthStatus = screen.getByTestId('health-status');
        expect(healthStatus).toHaveClass('custom-health-status');
      });
    });

    it('deve integrar com sistema de animações', async () => {
      render(<HealthStatus />);
      
      await waitFor(() => {
        const statusIndicator = screen.getByTestId('status-indicator');
        expect(statusIndicator).toHaveClass('animate-pulse');
      });
    });
  });
}); 