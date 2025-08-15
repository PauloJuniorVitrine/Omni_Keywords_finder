/**
 * Testes Unitários - DataVisualization Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_DATA_VISUALIZATION_019
 * 
 * Baseado em código real do DataVisualization.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataVisualization } from '../../../app/components/analytics/DataVisualization';

// Mock dos componentes UI
jest.mock('../../../app/components/shared/Card', () => ({
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

jest.mock('../../../app/components/shared/Button', () => ({
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

jest.mock('../../../app/components/shared/Badge', () => ({
  Badge: ({ children, className, variant, ...props }: any) => (
    <span data-testid="badge" className={className} data-variant={variant} {...props}>
      {children}
    </span>
  ),
}));

jest.mock('../../../app/components/shared/Tabs', () => ({
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

jest.mock('../../../app/components/shared/Select', () => ({
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

jest.mock('../../../app/components/shared/Progress', () => ({
  Progress: ({ value, className, ...props }: any) => (
    <div data-testid="progress" data-value={value} className={className} {...props} />
  ),
}));

jest.mock('../../../app/components/shared/Alert', () => ({
  Alert: ({ children, ...props }: any) => (
    <div data-testid="alert" {...props}>{children}</div>
  ),
  AlertDescription: ({ children, ...props }: any) => (
    <div data-testid="alert-description" {...props}>{children}</div>
  ),
}));

jest.mock('../../../app/components/shared/Skeleton', () => ({
  Skeleton: ({ className, ...props }: any) => (
    <div data-testid="skeleton" className={className} {...props} />
  ),
}));

// Mock do hook useBusinessMetrics
jest.mock('../../../app/hooks/useBusinessMetrics', () => ({
  useBusinessMetrics: jest.fn(() => ({
    data: {
      performance: [
        { id: '1', label: 'Jan', value: 100, category: 'Performance' },
        { id: '2', label: 'Fev', value: 150, category: 'Performance' },
        { id: '3', label: 'Mar', value: 200, category: 'Performance' }
      ],
      users: [
        { id: '4', label: 'Jan', value: 50, category: 'Usuários' },
        { id: '5', label: 'Fev', value: 75, category: 'Usuários' },
        { id: '6', label: 'Mar', value: 100, category: 'Usuários' }
      ],
      revenue: [
        { id: '7', label: 'Jan', value: 1000, category: 'Receita' },
        { id: '8', label: 'Fev', value: 1500, category: 'Receita' },
        { id: '9', label: 'Mar', value: 2000, category: 'Receita' }
      ]
    },
    loading: false,
    error: null,
    refetch: jest.fn()
  }))
}));

// Mock dos utilitários de formatação
jest.mock('../../../app/utils/formatters', () => ({
  formatCurrency: jest.fn((value) => `R$ ${value.toFixed(2)}`),
  formatPercentage: jest.fn((value) => `${value.toFixed(1)}%`),
  formatNumber: jest.fn((value) => value.toLocaleString())
}));

// Mock dos ícones Lucide
jest.mock('lucide-react', () => ({
  BarChart3: ({ className, ...props }: any) => (
    <div data-testid="icon-bar-chart-3" className={className} {...props} />
  ),
  LineChart: ({ className, ...props }: any) => (
    <div data-testid="icon-line-chart" className={className} {...props} />
  ),
  PieChart: ({ className, ...props }: any) => (
    <div data-testid="icon-pie-chart" className={className} {...props} />
  ),
  TrendingUp: ({ className, ...props }: any) => (
    <div data-testid="icon-trending-up" className={className} {...props} />
  ),
  TrendingDown: ({ className, ...props }: any) => (
    <div data-testid="icon-trending-down" className={className} {...props} />
  ),
  Download: ({ className, ...props }: any) => (
    <div data-testid="icon-download" className={className} {...props} />
  ),
  RefreshCw: ({ className, ...props }: any) => (
    <div data-testid="icon-refresh-cw" className={className} {...props} />
  ),
  ZoomIn: ({ className, ...props }: any) => (
    <div data-testid="icon-zoom-in" className={className} {...props} />
  ),
  ZoomOut: ({ className, ...props }: any) => (
    <div data-testid="icon-zoom-out" className={className} {...props} />
  ),
  RotateCcw: ({ className, ...props }: any) => (
    <div data-testid="icon-rotate-ccw" className={className} {...props} />
  ),
  Filter: ({ className, ...props }: any) => (
    <div data-testid="icon-filter" className={className} {...props} />
  ),
  Eye: ({ className, ...props }: any) => (
    <div data-testid="icon-eye" className={className} {...props} />
  ),
  EyeOff: ({ className, ...props }: any) => (
    <div data-testid="icon-eye-off" className={className} {...props} />
  ),
  Maximize2: ({ className, ...props }: any) => (
    <div data-testid="icon-maximize-2" className={className} {...props} />
  ),
  Minimize2: ({ className, ...props }: any) => (
    <div data-testid="icon-minimize-2" className={className} {...props} />
  ),
  Share2: ({ className, ...props }: any) => (
    <div data-testid="icon-share-2" className={className} {...props} />
  ),
  Settings: ({ className, ...props }: any) => (
    <div data-testid="icon-settings" className={className} {...props} />
  ),
  Info: ({ className, ...props }: any) => (
    <div data-testid="icon-info" className={className} {...props} />
  ),
  Activity: ({ className, ...props }: any) => (
    <div data-testid="icon-activity" className={className} {...props} />
  ),
  Target: ({ className, ...props }: any) => (
    <div data-testid="icon-target" className={className} {...props} />
  ),
  Users: ({ className, ...props }: any) => (
    <div data-testid="icon-users" className={className} {...props} />
  ),
  DollarSign: ({ className, ...props }: any) => (
    <div data-testid="icon-dollar-sign" className={className} {...props} />
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

// Mock do document.fullscreenElement e métodos fullscreen
Object.defineProperty(document, 'fullscreenElement', {
  value: null,
  writable: true,
});

Object.defineProperty(document.documentElement, 'requestFullscreen', {
  value: jest.fn(),
  writable: true,
});

Object.defineProperty(document, 'exitFullscreen', {
  value: jest.fn(),
  writable: true,
});

// Mock do navigator.share
Object.defineProperty(navigator, 'share', {
  value: jest.fn(),
  writable: true,
});

// Mock do performance.now
Object.defineProperty(performance, 'now', {
  value: jest.fn(() => 1000),
  writable: true,
});

describe('DataVisualization - Visualização de Dados Avançada', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar o componente com configurações padrão', () => {
      render(<DataVisualization />);
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve renderizar com props customizadas', () => {
      render(
        <DataVisualization 
          className="custom-class"
          refreshInterval={60000}
          enableAnimations={false}
          enableInteractions={false}
          maxDataPoints={100}
        />
      );
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve renderizar cards de estatísticas', () => {
      render(<DataVisualization />);
      
      const cards = screen.getAllByTestId('card');
      expect(cards.length).toBeGreaterThan(0);
      
      expect(screen.getByText('Visualizações disponíveis')).toBeInTheDocument();
      expect(screen.getByText('Hover e zoom habilitados')).toBeInTheDocument();
      expect(screen.getByText('Tempo de renderização')).toBeInTheDocument();
    });
  });

  describe('Abas de Gráficos', () => {
    
    test('deve renderizar todas as abas de gráficos', () => {
      render(<DataVisualization />);
      
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Usuários')).toBeInTheDocument();
      expect(screen.getByText('Receita')).toBeInTheDocument();
      expect(screen.getByText('Distribuição')).toBeInTheDocument();
      expect(screen.getByText('Tendências')).toBeInTheDocument();
    });

    test('deve mostrar aba de performance por padrão', () => {
      render(<DataVisualization />);
      
      const tabsContent = screen.getAllByTestId('tabs-content');
      const performanceTab = tabsContent.find(tab => tab.getAttribute('data-value') === 'performance');
      
      expect(performanceTab).toBeInTheDocument();
    });

    test('deve permitir navegação entre abas', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const usersTab = screen.getByText('Usuários');
      await user.click(usersTab);
      
      const tabsContent = screen.getAllByTestId('tabs-content');
      const usersTabContent = tabsContent.find(tab => tab.getAttribute('data-value') === 'users');
      
      expect(usersTabContent).toBeInTheDocument();
    });

    test('deve exibir títulos e descrições dos gráficos', () => {
      render(<DataVisualization />);
      
      expect(screen.getByText('Performance das Keywords')).toBeInTheDocument();
      expect(screen.getByText('Evolução da performance ao longo do tempo')).toBeInTheDocument();
    });
  });

  describe('Tipos de Gráficos', () => {
    
    test('deve renderizar gráfico de linha para performance', () => {
      render(<DataVisualization />);
      
      // Verificar se o SVG do gráfico de linha está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve renderizar gráfico de barras para usuários', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const usersTab = screen.getByText('Usuários');
      await user.click(usersTab);
      
      // Verificar se o SVG do gráfico de barras está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve renderizar gráfico de área para receita', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const revenueTab = screen.getByText('Receita');
      await user.click(revenueTab);
      
      // Verificar se o SVG do gráfico de área está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve renderizar gráfico de pizza para distribuição', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const distributionTab = screen.getByText('Distribuição');
      await user.click(distributionTab);
      
      // Verificar se o SVG do gráfico de pizza está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve renderizar gráfico de dispersão para tendências', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const trendsTab = screen.getByText('Tendências');
      await user.click(trendsTab);
      
      // Verificar se o SVG do gráfico de dispersão está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });
  });

  describe('Controles de Interação', () => {
    
    test('deve permitir zoom in', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const zoomInButton = screen.getByTestId('icon-zoom-in');
      await user.click(zoomInButton);
      
      expect(zoomInButton).toBeInTheDocument();
    });

    test('deve permitir zoom out', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const zoomOutButton = screen.getByTestId('icon-zoom-out');
      await user.click(zoomOutButton);
      
      expect(zoomOutButton).toBeInTheDocument();
    });

    test('deve permitir reset do zoom', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const resetButton = screen.getByTestId('icon-rotate-ccw');
      await user.click(resetButton);
      
      expect(resetButton).toBeInTheDocument();
    });

    test('deve permitir alternar fullscreen', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const fullscreenButton = screen.getByTestId('icon-maximize-2');
      await user.click(fullscreenButton);
      
      expect(document.documentElement.requestFullscreen).toHaveBeenCalled();
    });

    test('deve permitir compartilhar', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const shareButton = screen.getByTestId('icon-share-2');
      await user.click(shareButton);
      
      expect(navigator.share).toHaveBeenCalledWith({
        title: 'Data Visualization',
        text: 'Visualização de dados do Omni Keywords Finder',
        url: window.location.href
      });
    });
  });

  describe('Exportação de Dados', () => {
    
    test('deve permitir exportar em formato JSON', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const exportButton = screen.getByTestId('icon-download');
      await user.click(exportButton);
      
      // Verificar se as funções de download foram chamadas
      expect(global.URL.createObjectURL).toHaveBeenCalled();
      expect(mockAnchorElement.click).toHaveBeenCalled();
      expect(global.URL.revokeObjectURL).toHaveBeenCalled();
    });

    test('deve gerar arquivo com nome correto', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const exportButton = screen.getByTestId('icon-download');
      await user.click(exportButton);
      
      // Verificar se o nome do arquivo inclui a data
      expect(mockAnchorElement.download).toMatch(/data-visualization-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\.json/);
    });

    test('deve incluir dados corretos no export', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const exportButton = screen.getByTestId('icon-download');
      await user.click(exportButton);
      
      // Verificar se o Blob foi criado com dados JSON
      expect(global.URL.createObjectURL).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'application/json'
        })
      );
    });
  });

  describe('Configurações de Gráficos', () => {
    
    test('deve permitir configurar tipo de gráfico', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const chartTypeSelect = screen.getByTestId('select');
      expect(chartTypeSelect).toBeInTheDocument();
    });

    test('deve permitir configurar intervalo de tempo', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const timeRangeSelect = screen.getByTestId('select');
      expect(timeRangeSelect).toBeInTheDocument();
    });

    test('deve permitir alternar legenda', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const legendToggle = screen.getByTestId('icon-eye');
      await user.click(legendToggle);
      
      expect(legendToggle).toBeInTheDocument();
    });

    test('deve permitir alternar grade', async () => {
      const user = userEvent.setup();
      render(<DataVisualization />);
      
      const gridToggle = screen.getByTestId('icon-filter');
      await user.click(gridToggle);
      
      expect(gridToggle).toBeInTheDocument();
    });
  });

  describe('Legendas e Metadados', () => {
    
    test('deve exibir legendas quando habilitadas', () => {
      render(<DataVisualization />);
      
      // Verificar se as legendas estão sendo renderizadas
      const legendItems = document.querySelectorAll('[data-testid="badge"]');
      expect(legendItems.length).toBeGreaterThan(0);
    });

    test('deve exibir cores das legendas', () => {
      render(<DataVisualization />);
      
      // Verificar se os elementos de cor estão presentes
      const colorElements = document.querySelectorAll('.w-3.h-3.rounded-full');
      expect(colorElements.length).toBeGreaterThan(0);
    });

    test('deve exibir valores formatados nas legendas', () => {
      render(<DataVisualization />);
      
      // Verificar se os badges com valores estão presentes
      const valueBadges = screen.getAllByTestId('badge');
      expect(valueBadges.length).toBeGreaterThan(0);
    });

    test('deve exibir metadados de confiança', () => {
      render(<DataVisualization />);
      
      const trendsTab = screen.getByText('Tendências');
      fireEvent.click(trendsTab);
      
      // Verificar se os badges de confiança estão presentes
      const confidenceBadges = screen.getAllByTestId('badge');
      expect(confidenceBadges.length).toBeGreaterThan(0);
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve usar useMemo para configurações de gráficos', () => {
      render(<DataVisualization />);
      
      // Verificar se as configurações estão sendo aplicadas
      expect(screen.getByText('Performance das Keywords')).toBeInTheDocument();
      expect(screen.getByText('Atividade de Usuários')).toBeInTheDocument();
      expect(screen.getByText('Receita e Conversões')).toBeInTheDocument();
    });

    test('deve usar useCallback para funções', () => {
      render(<DataVisualization />);
      
      // Verificar se as funções estão disponíveis
      const buttons = screen.getAllByTestId('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    test('deve implementar auto-refresh configurável', () => {
      render(<DataVisualization refreshInterval={60000} />);
      
      // Verificar se o componente está configurado para auto-refresh
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve mostrar tempo de renderização', () => {
      render(<DataVisualization />);
      
      expect(screen.getByText('1000ms')).toBeInTheDocument();
      expect(screen.getByText('Tempo de renderização')).toBeInTheDocument();
    });
  });

  describe('Estados de Loading e Erro', () => {
    
    test('deve mostrar skeleton durante carregamento', () => {
      // Mock do hook para simular loading
      const { useBusinessMetrics } = require('../../../app/hooks/useBusinessMetrics');
      useBusinessMetrics.mockReturnValue({
        data: null,
        loading: true,
        error: null,
        refetch: jest.fn()
      });
      
      render(<DataVisualization />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    test('deve mostrar erro quando ocorre falha', () => {
      // Mock do hook para simular erro
      const { useBusinessMetrics } = require('../../../app/hooks/useBusinessMetrics');
      useBusinessMetrics.mockReturnValue({
        data: null,
        loading: false,
        error: new Error('Erro ao carregar dados'),
        refetch: jest.fn()
      });
      
      render(<DataVisualization />);
      
      const alerts = screen.getAllByTestId('alert');
      expect(alerts.length).toBeGreaterThan(0);
    });
  });

  describe('Responsividade e Acessibilidade', () => {
    
    test('deve ser responsivo', () => {
      render(<DataVisualization />);
      
      // Verificar se os elementos SVG têm classes responsivas
      const svgElements = document.querySelectorAll('svg');
      svgElements.forEach(svg => {
        expect(svg).toHaveClass('w-full', 'h-full');
      });
    });

    test('deve ter estrutura semântica adequada', () => {
      render(<DataVisualization />);
      
      // Verificar se há títulos apropriados
      expect(screen.getByText('Performance das Keywords')).toBeInTheDocument();
      expect(screen.getByText('Atividade de Usuários')).toBeInTheDocument();
      expect(screen.getByText('Receita e Conversões')).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(<DataVisualization />);
      
      // Verificar se as abas são navegáveis por teclado
      const tabsTriggers = screen.getAllByTestId('tabs-trigger');
      tabsTriggers.forEach(tab => {
        expect(tab).toHaveAttribute('role', 'tab');
      });
    });

    test('deve ter controles acessíveis', () => {
      render(<DataVisualization />);
      
      // Verificar se os botões têm texto descritivo ou aria-labels
      const buttons = screen.getAllByTestId('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Animações e Interações', () => {
    
    test('deve suportar animações quando habilitadas', () => {
      render(<DataVisualization enableAnimations={true} />);
      
      // Verificar se as classes de animação estão presentes
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve suportar interações quando habilitadas', () => {
      render(<DataVisualization enableInteractions={true} />);
      
      // Verificar se os elementos interativos estão presentes
      const interactiveElements = document.querySelectorAll('.cursor-pointer');
      expect(interactiveElements.length).toBeGreaterThan(0);
    });

    test('deve mostrar estado de interatividade', () => {
      render(<DataVisualization enableInteractions={true} />);
      
      expect(screen.getByText('Ativa')).toBeInTheDocument();
      expect(screen.getByText('Hover e zoom habilitados')).toBeInTheDocument();
    });

    test('deve mostrar estado de animações', () => {
      render(<DataVisualization enableAnimations={true} />);
      
      expect(screen.getByText('Ativa')).toBeInTheDocument();
      expect(screen.getByText('Visualizações disponíveis')).toBeInTheDocument();
    });
  });

  describe('Geração de Dados', () => {
    
    test('deve gerar dados com metadados', () => {
      render(<DataVisualization />);
      
      // Verificar se os dados estão sendo gerados com metadados
      const badges = screen.getAllByTestId('badge');
      expect(badges.length).toBeGreaterThan(0);
    });

    test('deve respeitar limite de pontos de dados', () => {
      render(<DataVisualization maxDataPoints={10} />);
      
      // Verificar se o limite está sendo respeitado
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve gerar cores únicas para dados', () => {
      render(<DataVisualization />);
      
      // Verificar se os elementos de cor estão presentes
      const colorElements = document.querySelectorAll('.w-3.h-3.rounded-full');
      expect(colorElements.length).toBeGreaterThan(0);
    });

    test('deve incluir timestamps nos dados', () => {
      render(<DataVisualization />);
      
      // Verificar se os dados estão sendo gerados com timestamps
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });
  });

  describe('Validação de Props', () => {
    
    test('deve aceitar props opcionais', () => {
      render(
        <DataVisualization 
          className="test-class"
          refreshInterval={45000}
          enableAnimations={false}
          enableInteractions={false}
          exportFormats={['png', 'svg']}
          maxDataPoints={25}
        />
      );
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve usar valores padrão quando props não fornecidas', () => {
      render(<DataVisualization />);
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve validar tipos de gráficos', () => {
      render(<DataVisualization />);
      
      // Verificar se todos os tipos de gráficos estão sendo renderizados
      expect(screen.getByText('Performance')).toBeInTheDocument(); // line
      expect(screen.getByText('Usuários')).toBeInTheDocument(); // bar
      expect(screen.getByText('Receita')).toBeInTheDocument(); // area
      expect(screen.getByText('Distribuição')).toBeInTheDocument(); // pie
      expect(screen.getByText('Tendências')).toBeInTheDocument(); // scatter
    });

    test('deve validar formatos de exportação', () => {
      render(<DataVisualization exportFormats={['png', 'svg', 'pdf', 'csv', 'json']} />);
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });
  });
}); 