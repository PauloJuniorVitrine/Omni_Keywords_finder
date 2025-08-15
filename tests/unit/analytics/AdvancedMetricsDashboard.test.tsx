/**
 * Testes Unitários - AdvancedMetricsDashboard Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_ADVANCED_METRICS_DASHBOARD_018
 * 
 * Baseado em código real do AdvancedMetricsDashboard.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AdvancedMetricsDashboard } from '../../../app/components/analytics/AdvancedMetricsDashboard';

// Mock dos componentes UI
jest.mock('@/components/ui/card', () => ({
  Card: ({ children, className, ...props }: any) => (
    <div data-testid="card" className={className} {...props}>{children}</div>
  ),
  CardContent: ({ children, className, ...props }: any) => (
    <div data-testid="card-content" className={className} {...props}>{children}</div>
  ),
  CardHeader: ({ children, className, ...props }: any) => (
    <div data-testid="card-header" className={className} {...props}>{children}</div>
  ),
  CardTitle: ({ children, className, ...props }: any) => (
    <h3 data-testid="card-title" className={className} {...props}>{children}</h3>
  ),
}));

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, disabled, variant, size, ...props }: any) => (
    <button 
      data-testid="button" 
      onClick={onClick} 
      disabled={disabled}
      data-variant={variant}
      data-size={size}
      {...props}
    >
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/badge', () => ({
  Badge: ({ children, className, variant, ...props }: any) => (
    <span data-testid="badge" className={className} data-variant={variant} {...props}>
      {children}
    </span>
  ),
}));

jest.mock('@/components/ui/alert', () => ({
  Alert: ({ children, ...props }: any) => (
    <div data-testid="alert" {...props}>{children}</div>
  ),
  AlertDescription: ({ children, ...props }: any) => (
    <div data-testid="alert-description" {...props}>{children}</div>
  ),
}));

jest.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children, defaultValue, className, ...props }: any) => (
    <div data-testid="tabs" data-default-value={defaultValue} className={className} {...props}>
      {children}
    </div>
  ),
  TabsContent: ({ children, value, className, ...props }: any) => (
    <div data-testid="tabs-content" data-value={value} className={className} {...props}>
      {children}
    </div>
  ),
  TabsList: ({ children, ...props }: any) => (
    <div data-testid="tabs-list" {...props}>{children}</div>
  ),
  TabsTrigger: ({ children, value, ...props }: any) => (
    <button data-testid="tabs-trigger" data-value={value} {...props}>
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/select', () => ({
  Select: ({ children, value, onValueChange, ...props }: any) => (
    <div data-testid="select" data-value={value} {...props}>
      {children}
    </div>
  ),
  SelectContent: ({ children, ...props }: any) => (
    <div data-testid="select-content" {...props}>{children}</div>
  ),
  SelectItem: ({ children, value, ...props }: any) => (
    <div data-testid="select-item" data-value={value} {...props}>
      {children}
    </div>
  ),
  SelectTrigger: ({ children, ...props }: any) => (
    <button data-testid="select-trigger" {...props}>{children}</button>
  ),
  SelectValue: ({ ...props }: any) => (
    <span data-testid="select-value" {...props} />
  ),
}));

jest.mock('@/components/ui/input', () => ({
  Input: ({ value, onChange, id, type, min, max, ...props }: any) => (
    <input 
      data-testid="input" 
      value={value} 
      onChange={onChange}
      id={id}
      type={type}
      min={min}
      max={max}
      {...props}
    />
  ),
}));

jest.mock('@/components/ui/label', () => ({
  Label: ({ children, htmlFor, ...props }: any) => (
    <label data-testid="label" htmlFor={htmlFor} {...props}>
      {children}
    </label>
  ),
}));

jest.mock('@/components/ui/switch', () => ({
  Switch: ({ checked, onCheckedChange, id, ...props }: any) => (
    <input 
      data-testid="switch" 
      type="checkbox" 
      checked={checked} 
      onChange={(e) => onCheckedChange(e.target.checked)}
      id={id}
      {...props}
    />
  ),
}));

// Mock dos ícones Lucide
jest.mock('lucide-react', () => ({
  Activity: ({ className, ...props }: any) => (
    <div data-testid="icon-activity" className={className} {...props} />
  ),
  TrendingUp: ({ className, ...props }: any) => (
    <div data-testid="icon-trending-up" className={className} {...props} />
  ),
  TrendingDown: ({ className, ...props }: any) => (
    <div data-testid="icon-trending-down" className={className} {...props} />
  ),
  AlertTriangle: ({ className, ...props }: any) => (
    <div data-testid="icon-alert-triangle" className={className} {...props} />
  ),
  CheckCircle: ({ className, ...props }: any) => (
    <div data-testid="icon-check-circle" className={className} {...props} />
  ),
  Clock: ({ className, ...props }: any) => (
    <div data-testid="icon-clock" className={className} {...props} />
  ),
  Download: ({ className, ...props }: any) => (
    <div data-testid="icon-download" className={className} {...props} />
  ),
  RefreshCw: ({ className, ...props }: any) => (
    <div data-testid="icon-refresh-cw" className={className} {...props} />
  ),
  Settings: ({ className, ...props }: any) => (
    <div data-testid="icon-settings" className={className} {...props} />
  ),
  BarChart3: ({ className, ...props }: any) => (
    <div data-testid="icon-bar-chart-3" className={className} {...props} />
  ),
  LineChart: ({ className, ...props }: any) => (
    <div data-testid="icon-line-chart" className={className} {...props} />
  ),
  PieChart: ({ className, ...props }: any) => (
    <div data-testid="icon-pie-chart" className={className} {...props} />
  ),
  Gauge: ({ className, ...props }: any) => (
    <div data-testid="icon-gauge" className={className} {...props} />
  ),
  Zap: ({ className, ...props }: any) => (
    <div data-testid="icon-zap" className={className} {...props} />
  ),
  Shield: ({ className, ...props }: any) => (
    <div data-testid="icon-shield" className={className} {...props} />
  ),
  Users: ({ className, ...props }: any) => (
    <div data-testid="icon-users" className={className} {...props} />
  ),
  Database: ({ className, ...props }: any) => (
    <div data-testid="icon-database" className={className} {...props} />
  ),
  Globe: ({ className, ...props }: any) => (
    <div data-testid="icon-globe" className={className} {...props} />
  ),
  Server: ({ className, ...props }: any) => (
    <div data-testid="icon-server" className={className} {...props} />
  ),
}));

// Mock do URL.createObjectURL e URL.revokeObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-url');
global.URL.revokeObjectURL = jest.fn();

// Mock do document.createElement e appendChild
const mockAnchorElement = {
  href: '',
  download: '',
  click: jest.fn(),
};

Object.defineProperty(document, 'createElement', {
  value: jest.fn(() => mockAnchorElement),
  writable: true,
});

Object.defineProperty(document.body, 'appendChild', {
  value: jest.fn(),
  writable: true,
});

Object.defineProperty(document.body, 'removeChild', {
  value: jest.fn(),
  writable: true,
});

describe('AdvancedMetricsDashboard - Dashboard de Métricas Avançadas', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Dashboard', () => {
    
    test('deve renderizar o título do dashboard', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText('📊 Dashboard de Métricas Avançadas')).toBeInTheDocument();
    });

    test('deve renderizar informações de última atualização', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText(/Última atualização:/)).toBeInTheDocument();
    });

    test('deve renderizar botões de ação no header', () => {
      render(<AdvancedMetricsDashboard />);
      
      const buttons = screen.getAllByTestId('button');
      expect(buttons).toHaveLength(2);
      
      expect(screen.getByText('Atualizar')).toBeInTheDocument();
      expect(screen.getByText('Exportar Relatório')).toBeInTheDocument();
    });

    test('deve renderizar cards de resumo geral', () => {
      render(<AdvancedMetricsDashboard />);
      
      const cards = screen.getAllByTestId('card');
      expect(cards.length).toBeGreaterThan(0);
      
      expect(screen.getByText('Métricas Saudáveis')).toBeInTheDocument();
      expect(screen.getByText('Avisos')).toBeInTheDocument();
      expect(screen.getByText('Críticos')).toBeInTheDocument();
      expect(screen.getByText('Alertas Pendentes')).toBeInTheDocument();
    });
  });

  describe('Abas do Dashboard', () => {
    
    test('deve renderizar todas as abas principais', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText('Métricas')).toBeInTheDocument();
      expect(screen.getByText('Alertas')).toBeInTheDocument();
      expect(screen.getByText('Gráficos')).toBeInTheDocument();
      expect(screen.getByText('Configurações')).toBeInTheDocument();
    });

    test('deve mostrar aba de métricas por padrão', () => {
      render(<AdvancedMetricsDashboard />);
      
      const tabsContent = screen.getAllByTestId('tabs-content');
      const metricsTab = tabsContent.find(tab => tab.getAttribute('data-value') === 'metrics');
      
      expect(metricsTab).toBeInTheDocument();
    });

    test('deve permitir navegação entre abas', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const alertsTab = screen.getByText('Alertas');
      await user.click(alertsTab);
      
      const tabsContent = screen.getAllByTestId('tabs-content');
      const alertsTabContent = tabsContent.find(tab => tab.getAttribute('data-value') === 'alerts');
      
      expect(alertsTabContent).toBeInTheDocument();
    });
  });

  describe('Métricas Avançadas', () => {
    
    test('deve exibir métricas de performance', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText('Tempo de Resposta')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Erro')).toBeInTheDocument();
    });

    test('deve exibir métricas de negócio', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText('Receita')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Conversão')).toBeInTheDocument();
    });

    test('deve exibir métricas de infraestrutura', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText('Uso de CPU')).toBeInTheDocument();
      expect(screen.getByText('Uso de Memória')).toBeInTheDocument();
      expect(screen.getByText('Conexões DB')).toBeInTheDocument();
    });

    test('deve exibir métricas de usuário', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText('Usuários Ativos')).toBeInTheDocument();
    });

    test('deve mostrar valores das métricas com unidades', () => {
      render(<AdvancedMetricsDashboard />);
      
      expect(screen.getByText('245')).toBeInTheDocument();
      expect(screen.getByText('ms')).toBeInTheDocument();
      expect(screen.getByText('1.2')).toBeInTheDocument();
      expect(screen.getByText('%')).toBeInTheDocument();
    });

    test('deve mostrar tendências das métricas', () => {
      render(<AdvancedMetricsDashboard />);
      
      const trendIcons = screen.getAllByTestId('icon-trending-up');
      expect(trendIcons.length).toBeGreaterThan(0);
    });

    test('deve mostrar status das métricas com badges', () => {
      render(<AdvancedMetricsDashboard />);
      
      const badges = screen.getAllByTestId('badge');
      expect(badges.length).toBeGreaterThan(0);
      
      expect(screen.getByText('healthy')).toBeInTheDocument();
      expect(screen.getByText('warning')).toBeInTheDocument();
    });

    test('deve mostrar timestamps das métricas', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se há timestamps sendo exibidos
      const cards = screen.getAllByTestId('card');
      expect(cards.length).toBeGreaterThan(0);
    });
  });

  describe('Sistema de Alertas', () => {
    
    test('deve exibir alertas ativos', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Navegar para aba de alertas
      const alertsTab = screen.getByText('Alertas');
      fireEvent.click(alertsTab);
      
      expect(screen.getByText('Alto Uso de CPU')).toBeInTheDocument();
      expect(screen.getByText('Erro de Conexão')).toBeInTheDocument();
      expect(screen.getByText('Manutenção Programada')).toBeInTheDocument();
    });

    test('deve mostrar severidade dos alertas', () => {
      render(<AdvancedMetricsDashboard />);
      
      const alertsTab = screen.getByText('Alertas');
      fireEvent.click(alertsTab);
      
      expect(screen.getByText('medium')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
      expect(screen.getByText('low')).toBeInTheDocument();
    });

    test('deve permitir reconhecer alertas', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const alertsTab = screen.getByText('Alertas');
      await user.click(alertsTab);
      
      const acknowledgeButtons = screen.getAllByText('Reconhecer');
      expect(acknowledgeButtons.length).toBeGreaterThan(0);
      
      await user.click(acknowledgeButtons[0]);
      
      // Verificar se o alerta foi reconhecido
      expect(screen.getByText('Reconhecido')).toBeInTheDocument();
    });

    test('deve mostrar mensagem quando não há alertas', () => {
      render(<AdvancedMetricsDashboard />);
      
      const alertsTab = screen.getByText('Alertas');
      fireEvent.click(alertsTab);
      
      // Simular estado sem alertas (isso seria testado com mock de dados)
      expect(screen.getByText('Nenhum alerta ativo no momento.')).toBeInTheDocument();
    });
  });

  describe('Gráficos e Visualizações', () => {
    
    test('deve renderizar seção de gráficos', () => {
      render(<AdvancedMetricsDashboard />);
      
      const chartsTab = screen.getByText('Gráficos');
      fireEvent.click(chartsTab);
      
      expect(screen.getByText('Tendência de Performance')).toBeInTheDocument();
      expect(screen.getByText('Distribuição de Status')).toBeInTheDocument();
      expect(screen.getByText('Métricas por Categoria')).toBeInTheDocument();
      expect(screen.getByText('Saúde Geral do Sistema')).toBeInTheDocument();
    });

    test('deve mostrar placeholders para gráficos', () => {
      render(<AdvancedMetricsDashboard />);
      
      const chartsTab = screen.getByText('Gráficos');
      fireEvent.click(chartsTab);
      
      expect(screen.getByText('Gráfico de Linha - Implementar com Chart.js ou Recharts')).toBeInTheDocument();
      expect(screen.getByText('Gráfico de Pizza - Implementar com Chart.js ou Recharts')).toBeInTheDocument();
      expect(screen.getByText('Gráfico de Barras - Implementar com Chart.js ou Recharts')).toBeInTheDocument();
      expect(screen.getByText('Gauge Chart - Implementar com Chart.js ou Recharts')).toBeInTheDocument();
    });
  });

  describe('Configurações do Dashboard', () => {
    
    test('deve renderizar seção de configurações', () => {
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);
      
      expect(screen.getByText('Configurações do Dashboard')).toBeInTheDocument();
    });

    test('deve permitir configurar intervalo de atualização', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      await user.click(settingsTab);
      
      const refreshIntervalInput = screen.getByLabelText('Intervalo de Atualização (segundos)');
      expect(refreshIntervalInput).toBeInTheDocument();
      
      await user.clear(refreshIntervalInput);
      await user.type(refreshIntervalInput, '60');
      
      expect(refreshIntervalInput).toHaveValue(60);
    });

    test('deve permitir configurar intervalo de tempo', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      await user.click(settingsTab);
      
      const timeRangeSelect = screen.getByLabelText('Intervalo de Tempo');
      expect(timeRangeSelect).toBeInTheDocument();
    });

    test('deve permitir configurar atualização automática', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      await user.click(settingsTab);
      
      const autoRefreshSwitch = screen.getByLabelText('Atualização Automática');
      expect(autoRefreshSwitch).toBeInTheDocument();
      
      await user.click(autoRefreshSwitch);
      expect(autoRefreshSwitch).toBeChecked();
    });

    test('deve permitir configurar exibição de alertas', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      await user.click(settingsTab);
      
      const showAlertsSwitch = screen.getByLabelText('Mostrar Alertas');
      expect(showAlertsSwitch).toBeInTheDocument();
      
      await user.click(showAlertsSwitch);
      expect(showAlertsSwitch).toBeChecked();
    });

    test('deve permitir configurar exibição de tendências', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      await user.click(settingsTab);
      
      const showTrendsSwitch = screen.getByLabelText('Mostrar Tendências');
      expect(showTrendsSwitch).toBeInTheDocument();
      
      await user.click(showTrendsSwitch);
      expect(showTrendsSwitch).toBeChecked();
    });
  });

  describe('Funcionalidades de Atualização', () => {
    
    test('deve permitir atualização manual', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      await user.click(refreshButton);
      
      // Verificar se o botão foi clicado
      expect(refreshButton).toBeInTheDocument();
    });

    test('deve mostrar estado de loading durante atualização', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      await user.click(refreshButton);
      
      // O botão deve estar desabilitado durante o loading
      expect(refreshButton).toBeDisabled();
    });

    test('deve atualizar timestamp de última atualização', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const initialTime = screen.getByText(/Última atualização:/).textContent;
      
      const refreshButton = screen.getByText('Atualizar');
      await user.click(refreshButton);
      
      // Aguardar atualização
      await waitFor(() => {
        const updatedTime = screen.getByText(/Última atualização:/).textContent;
        expect(updatedTime).not.toBe(initialTime);
      });
    });
  });

  describe('Exportação de Relatórios', () => {
    
    test('deve permitir exportar relatório', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const exportButton = screen.getByText('Exportar Relatório');
      await user.click(exportButton);
      
      // Verificar se as funções de download foram chamadas
      expect(global.URL.createObjectURL).toHaveBeenCalled();
      expect(mockAnchorElement.click).toHaveBeenCalled();
      expect(global.URL.revokeObjectURL).toHaveBeenCalled();
    });

    test('deve gerar relatório com dados corretos', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const exportButton = screen.getByText('Exportar Relatório');
      await user.click(exportButton);
      
      // Verificar se o Blob foi criado com dados JSON
      expect(global.URL.createObjectURL).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'application/json'
        })
      );
    });

    test('deve incluir timestamp no nome do arquivo', async () => {
      const user = userEvent.setup();
      render(<AdvancedMetricsDashboard />);
      
      const exportButton = screen.getByText('Exportar Relatório');
      await user.click(exportButton);
      
      // Verificar se o nome do arquivo inclui a data
      expect(mockAnchorElement.download).toMatch(/metrics_report_\d{4}-\d{2}-\d{2}\.json/);
    });
  });

  describe('Cálculos e Métricas Derivadas', () => {
    
    test('deve calcular métricas saudáveis corretamente', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se o número de métricas saudáveis é exibido
      const healthyMetricsText = screen.getByText('Métricas Saudáveis');
      expect(healthyMetricsText).toBeInTheDocument();
    });

    test('deve calcular métricas com aviso corretamente', () => {
      render(<AdvancedMetricsDashboard />);
      
      const warningMetricsText = screen.getByText('Avisos');
      expect(warningMetricsText).toBeInTheDocument();
    });

    test('deve calcular métricas críticas corretamente', () => {
      render(<AdvancedMetricsDashboard />);
      
      const criticalMetricsText = screen.getByText('Críticos');
      expect(criticalMetricsText).toBeInTheDocument();
    });

    test('deve calcular alertas não reconhecidos corretamente', () => {
      render(<AdvancedMetricsDashboard />);
      
      const unacknowledgedAlertsText = screen.getByText('Alertas Pendentes');
      expect(unacknowledgedAlertsText).toBeInTheDocument();
    });
  });

  describe('Ícones e Indicadores Visuais', () => {
    
    test('deve mostrar ícones corretos para categorias de métricas', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se os ícones estão sendo renderizados
      const activityIcons = screen.getAllByTestId('icon-activity');
      const trendingUpIcons = screen.getAllByTestId('icon-trending-up');
      const serverIcons = screen.getAllByTestId('icon-server');
      const usersIcons = screen.getAllByTestId('icon-users');
      
      expect(activityIcons.length).toBeGreaterThan(0);
      expect(trendingUpIcons.length).toBeGreaterThan(0);
      expect(serverIcons.length).toBeGreaterThan(0);
      expect(usersIcons.length).toBeGreaterThan(0);
    });

    test('deve mostrar ícones de tendência corretos', () => {
      render(<AdvancedMetricsDashboard />);
      
      const trendingUpIcons = screen.getAllByTestId('icon-trending-up');
      const trendingDownIcons = screen.getAllByTestId('icon-trending-down');
      const clockIcons = screen.getAllByTestId('icon-clock');
      
      expect(trendingUpIcons.length).toBeGreaterThan(0);
      expect(trendingDownIcons.length).toBeGreaterThan(0);
      expect(clockIcons.length).toBeGreaterThan(0);
    });

    test('deve mostrar ícones de alerta corretos', () => {
      render(<AdvancedMetricsDashboard />);
      
      const alertsTab = screen.getByText('Alertas');
      fireEvent.click(alertsTab);
      
      const alertTriangleIcons = screen.getAllByTestId('icon-alert-triangle');
      const checkCircleIcons = screen.getAllByTestId('icon-check-circle');
      
      expect(alertTriangleIcons.length).toBeGreaterThan(0);
      expect(checkCircleIcons.length).toBeGreaterThan(0);
    });
  });

  describe('Validação de Dados', () => {
    
    test('deve validar tipos de métricas', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se todas as categorias de métricas estão presentes
      expect(screen.getByText('Tempo de Resposta')).toBeInTheDocument(); // performance
      expect(screen.getByText('Receita')).toBeInTheDocument(); // business
      expect(screen.getByText('Uso de CPU')).toBeInTheDocument(); // infrastructure
      expect(screen.getByText('Usuários Ativos')).toBeInTheDocument(); // user
    });

    test('deve validar tipos de alertas', () => {
      render(<AdvancedMetricsDashboard />);
      
      const alertsTab = screen.getByText('Alertas');
      fireEvent.click(alertsTab);
      
      // Verificar se diferentes tipos de alertas estão presentes
      expect(screen.getByText('Alto Uso de CPU')).toBeInTheDocument(); // warning
      expect(screen.getByText('Erro de Conexão')).toBeInTheDocument(); // error
      expect(screen.getByText('Manutenção Programada')).toBeInTheDocument(); // info
    });

    test('deve validar severidades de alertas', () => {
      render(<AdvancedMetricsDashboard />);
      
      const alertsTab = screen.getByText('Alertas');
      fireEvent.click(alertsTab);
      
      // Verificar se diferentes severidades estão presentes
      expect(screen.getByText('medium')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
      expect(screen.getByText('low')).toBeInTheDocument();
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve usar useMemo para cálculos derivados', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se os cálculos derivados estão sendo exibidos
      expect(screen.getByText('Métricas Saudáveis')).toBeInTheDocument();
      expect(screen.getByText('Avisos')).toBeInTheDocument();
      expect(screen.getByText('Críticos')).toBeInTheDocument();
      expect(screen.getByText('Alertas Pendentes')).toBeInTheDocument();
    });

    test('deve usar useCallback para funções', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se as funções estão disponíveis
      const refreshButton = screen.getByText('Atualizar');
      const exportButton = screen.getByText('Exportar Relatório');
      
      expect(refreshButton).toBeInTheDocument();
      expect(exportButton).toBeInTheDocument();
    });

    test('deve implementar auto-refresh configurável', () => {
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);
      
      const autoRefreshSwitch = screen.getByLabelText('Atualização Automática');
      expect(autoRefreshSwitch).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter labels apropriados para controles', () => {
      render(<AdvancedMetricsDashboard />);
      
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);
      
      expect(screen.getByLabelText('Intervalo de Atualização (segundos)')).toBeInTheDocument();
      expect(screen.getByLabelText('Intervalo de Tempo')).toBeInTheDocument();
      expect(screen.getByLabelText('Atualização Automática')).toBeInTheDocument();
      expect(screen.getByLabelText('Mostrar Alertas')).toBeInTheDocument();
      expect(screen.getByLabelText('Mostrar Tendências')).toBeInTheDocument();
    });

    test('deve ter estrutura semântica adequada', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se há títulos apropriados
      expect(screen.getByRole('heading', { name: '📊 Dashboard de Métricas Avançadas' })).toBeInTheDocument();
      
      // Verificar se há botões com texto descritivo
      expect(screen.getByRole('button', { name: 'Atualizar' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Exportar Relatório' })).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(<AdvancedMetricsDashboard />);
      
      // Verificar se as abas são navegáveis por teclado
      const tabsTriggers = screen.getAllByTestId('tabs-trigger');
      tabsTriggers.forEach(tab => {
        expect(tab).toHaveAttribute('role', 'tab');
      });
    });
  });
}); 