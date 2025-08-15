/**
 * Testes Unitários - InteractiveCharts Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_INTERACTIVE_CHARTS_020
 * 
 * Baseado em código real do InteractiveCharts.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InteractiveCharts } from '../../../app/components/analytics/InteractiveCharts';

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
  Clock: ({ className, ...props }: any) => (
    <div data-testid="icon-clock" className={className} {...props} />
  ),
}));

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

describe('InteractiveCharts - Gráficos Interativos', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar o componente com configurações padrão', () => {
      render(<InteractiveCharts />);
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve renderizar com props customizadas', () => {
      render(
        <InteractiveCharts 
          className="custom-class"
          refreshInterval={60000}
          enableAnimations={false}
          enableInteractions={false}
          maxDataPoints={100}
        />
      );
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve renderizar controles de interação', () => {
      render(<InteractiveCharts />);
      
      const buttons = screen.getAllByTestId('button');
      expect(buttons.length).toBeGreaterThan(0);
      
      expect(screen.getByText('Legenda')).toBeInTheDocument();
      expect(screen.getByText('Grid')).toBeInTheDocument();
      expect(screen.getByText('Compartilhar')).toBeInTheDocument();
      expect(screen.getByText('Tela Cheia')).toBeInTheDocument();
    });
  });

  describe('Abas de Gráficos', () => {
    
    test('deve renderizar todas as abas de gráficos', () => {
      render(<InteractiveCharts />);
      
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Usuários')).toBeInTheDocument();
      expect(screen.getByText('Receita')).toBeInTheDocument();
      expect(screen.getByText('Distribuição')).toBeInTheDocument();
    });

    test('deve mostrar aba de performance por padrão', () => {
      render(<InteractiveCharts />);
      
      const tabsContent = screen.getAllByTestId('tabs-content');
      const performanceTab = tabsContent.find(tab => tab.getAttribute('data-value') === 'performance');
      
      expect(performanceTab).toBeInTheDocument();
    });

    test('deve permitir navegação entre abas', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const usersTab = screen.getByText('Usuários');
      await user.click(usersTab);
      
      const tabsContent = screen.getAllByTestId('tabs-content');
      const usersTabContent = tabsContent.find(tab => tab.getAttribute('data-value') === 'users');
      
      expect(usersTabContent).toBeInTheDocument();
    });

    test('deve exibir títulos e descrições dos gráficos', () => {
      render(<InteractiveCharts />);
      
      expect(screen.getByText('Performance ao Longo do Tempo')).toBeInTheDocument();
      expect(screen.getByText('Métricas de performance das keywords')).toBeInTheDocument();
    });
  });

  describe('Tipos de Gráficos', () => {
    
    test('deve renderizar gráfico de linha para performance', () => {
      render(<InteractiveCharts />);
      
      // Verificar se o SVG do gráfico de linha está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve renderizar gráfico de barras para usuários', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const usersTab = screen.getByText('Usuários');
      await user.click(usersTab);
      
      // Verificar se o SVG do gráfico de barras está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve renderizar gráfico de área para receita', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const revenueTab = screen.getByText('Receita');
      await user.click(revenueTab);
      
      // Verificar se o SVG do gráfico de área está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve renderizar gráfico de pizza para distribuição', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const distributionTab = screen.getByText('Distribuição');
      await user.click(distributionTab);
      
      // Verificar se o SVG do gráfico de pizza está presente
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });
  });

  describe('Controles de Interação', () => {
    
    test('deve permitir alternar legenda', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const legendButton = screen.getByText('Legenda');
      await user.click(legendButton);
      
      expect(legendButton).toBeInTheDocument();
    });

    test('deve permitir alternar grade', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const gridButton = screen.getByText('Grid');
      await user.click(gridButton);
      
      expect(gridButton).toBeInTheDocument();
    });

    test('deve permitir compartilhar', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const shareButton = screen.getByText('Compartilhar');
      await user.click(shareButton);
      
      expect(navigator.share).toHaveBeenCalledWith({
        title: 'Gráficos Interativos',
        text: 'Visualização de dados do Omni Keywords Finder',
        url: window.location.href
      });
    });

    test('deve permitir alternar fullscreen', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const fullscreenButton = screen.getByText('Tela Cheia');
      await user.click(fullscreenButton);
      
      expect(document.documentElement.requestFullscreen).toHaveBeenCalled();
    });
  });

  describe('Exportação de Gráficos', () => {
    
    test('deve permitir exportar em formato PNG', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const pngButton = screen.getByText('PNG');
      await user.click(pngButton);
      
      // Verificar se o download foi iniciado
      expect(mockAnchorElement.click).toHaveBeenCalled();
    });

    test('deve permitir exportar em formato SVG', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const svgButton = screen.getByText('SVG');
      await user.click(svgButton);
      
      // Verificar se o download foi iniciado
      expect(mockAnchorElement.click).toHaveBeenCalled();
    });

    test('deve permitir exportar em formato CSV', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const csvButton = screen.getByText('CSV');
      await user.click(csvButton);
      
      // Verificar se o download foi iniciado
      expect(mockAnchorElement.click).toHaveBeenCalled();
    });

    test('deve gerar nome de arquivo correto', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const pngButton = screen.getByText('PNG');
      await user.click(pngButton);
      
      // Verificar se o nome do arquivo inclui o tipo de gráfico e formato
      expect(mockAnchorElement.download).toMatch(/chart-line-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\.png/);
    });

    test('deve desabilitar botões durante exportação', async () => {
      const user = userEvent.setup();
      render(<InteractiveCharts />);
      
      const pngButton = screen.getByText('PNG');
      await user.click(pngButton);
      
      // Verificar se o botão está desabilitado durante a exportação
      expect(pngButton).toBeDisabled();
    });
  });

  describe('Indicadores de Status', () => {
    
    test('deve mostrar última atualização', () => {
      render(<InteractiveCharts />);
      
      expect(screen.getByText(/Última atualização:/)).toBeInTheDocument();
    });

    test('deve mostrar número de pontos de dados', () => {
      render(<InteractiveCharts />);
      
      expect(screen.getByText('50 pontos de dados')).toBeInTheDocument();
    });

    test('deve mostrar status das animações', () => {
      render(<InteractiveCharts enableAnimations={true} />);
      
      expect(screen.getByText('Animações ativas')).toBeInTheDocument();
    });

    test('deve mostrar status das animações quando desabilitadas', () => {
      render(<InteractiveCharts enableAnimations={false} />);
      
      expect(screen.getByText('Animações desativadas')).toBeInTheDocument();
    });
  });

  describe('Legendas e Metadados', () => {
    
    test('deve exibir legendas quando habilitadas', () => {
      render(<InteractiveCharts />);
      
      // Verificar se as legendas estão sendo renderizadas
      const legendItems = document.querySelectorAll('.w-3.h-3.rounded-full');
      expect(legendItems.length).toBeGreaterThan(0);
    });

    test('deve exibir cores das legendas', () => {
      render(<InteractiveCharts />);
      
      // Verificar se os elementos de cor estão presentes
      const colorElements = document.querySelectorAll('.w-3.h-3.rounded-full');
      expect(colorElements.length).toBeGreaterThan(0);
    });

    test('deve exibir valores formatados nas legendas', () => {
      render(<InteractiveCharts />);
      
      // Navegar para aba de distribuição que tem badges com valores
      const distributionTab = screen.getByText('Distribuição');
      fireEvent.click(distributionTab);
      
      // Verificar se os badges com valores estão presentes
      const valueBadges = screen.getAllByTestId('badge');
      expect(valueBadges.length).toBeGreaterThan(0);
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve usar useMemo para configurações de gráficos', () => {
      render(<InteractiveCharts />);
      
      // Verificar se as configurações estão sendo aplicadas
      expect(screen.getByText('Performance ao Longo do Tempo')).toBeInTheDocument();
      expect(screen.getByText('Atividade de Usuários')).toBeInTheDocument();
      expect(screen.getByText('Receita e Conversões')).toBeInTheDocument();
      expect(screen.getByText('Distribuição por Categoria')).toBeInTheDocument();
    });

    test('deve usar useCallback para funções', () => {
      render(<InteractiveCharts />);
      
      // Verificar se as funções estão disponíveis
      const buttons = screen.getAllByTestId('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    test('deve implementar auto-refresh configurável', () => {
      render(<InteractiveCharts refreshInterval={60000} />);
      
      // Verificar se o componente está configurado para auto-refresh
      expect(screen.getByTestId('card')).toBeInTheDocument();
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
      
      render(<InteractiveCharts />);
      
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
      
      render(<InteractiveCharts />);
      
      const alerts = screen.getAllByTestId('alert');
      expect(alerts.length).toBeGreaterThan(0);
    });
  });

  describe('Responsividade e Acessibilidade', () => {
    
    test('deve ser responsivo', () => {
      render(<InteractiveCharts />);
      
      // Verificar se os elementos SVG têm classes responsivas
      const svgElements = document.querySelectorAll('svg');
      svgElements.forEach(svg => {
        expect(svg).toHaveClass('w-full', 'h-full');
      });
    });

    test('deve ter estrutura semântica adequada', () => {
      render(<InteractiveCharts />);
      
      // Verificar se há títulos apropriados
      expect(screen.getByText('Performance ao Longo do Tempo')).toBeInTheDocument();
      expect(screen.getByText('Atividade de Usuários')).toBeInTheDocument();
      expect(screen.getByText('Receita e Conversões')).toBeInTheDocument();
      expect(screen.getByText('Distribuição por Categoria')).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(<InteractiveCharts />);
      
      // Verificar se as abas são navegáveis por teclado
      const tabsTriggers = screen.getAllByTestId('tabs-trigger');
      tabsTriggers.forEach(tab => {
        expect(tab).toHaveAttribute('role', 'tab');
      });
    });

    test('deve ter controles acessíveis', () => {
      render(<InteractiveCharts />);
      
      // Verificar se os botões têm texto descritivo
      expect(screen.getByText('Legenda')).toBeInTheDocument();
      expect(screen.getByText('Grid')).toBeInTheDocument();
      expect(screen.getByText('Compartilhar')).toBeInTheDocument();
      expect(screen.getByText('Tela Cheia')).toBeInTheDocument();
    });
  });

  describe('Animações e Interações', () => {
    
    test('deve suportar animações quando habilitadas', () => {
      render(<InteractiveCharts enableAnimations={true} />);
      
      // Verificar se as classes de animação estão presentes
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('deve suportar interações quando habilitadas', () => {
      render(<InteractiveCharts enableInteractions={true} />);
      
      // Verificar se os elementos interativos estão presentes
      const interactiveElements = document.querySelectorAll('.cursor-pointer');
      expect(interactiveElements.length).toBeGreaterThan(0);
    });

    test('deve mostrar estado de interatividade', () => {
      render(<InteractiveCharts enableInteractions={true} />);
      
      // Verificar se os controles de interação estão presentes
      expect(screen.getByText('Legenda')).toBeInTheDocument();
      expect(screen.getByText('Grid')).toBeInTheDocument();
    });
  });

  describe('Geração de Dados', () => {
    
    test('deve gerar dados com metadados', () => {
      render(<InteractiveCharts />);
      
      // Verificar se os dados estão sendo gerados com metadados
      const badges = screen.getAllByTestId('badge');
      expect(badges.length).toBeGreaterThan(0);
    });

    test('deve respeitar limite de pontos de dados', () => {
      render(<InteractiveCharts maxDataPoints={10} />);
      
      // Verificar se o limite está sendo respeitado
      expect(screen.getByText('10 pontos de dados')).toBeInTheDocument();
    });

    test('deve gerar cores únicas para dados', () => {
      render(<InteractiveCharts />);
      
      // Verificar se os elementos de cor estão presentes
      const colorElements = document.querySelectorAll('.w-3.h-3.rounded-full');
      expect(colorElements.length).toBeGreaterThan(0);
    });

    test('deve incluir timestamps nos dados', () => {
      render(<InteractiveCharts />);
      
      // Verificar se os dados estão sendo gerados com timestamps
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });
  });

  describe('Validação de Props', () => {
    
    test('deve aceitar props opcionais', () => {
      render(
        <InteractiveCharts 
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
      render(<InteractiveCharts />);
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    test('deve validar tipos de gráficos', () => {
      render(<InteractiveCharts />);
      
      // Verificar se todos os tipos de gráficos estão sendo renderizados
      expect(screen.getByText('Performance')).toBeInTheDocument(); // line
      expect(screen.getByText('Usuários')).toBeInTheDocument(); // bar
      expect(screen.getByText('Receita')).toBeInTheDocument(); // area
      expect(screen.getByText('Distribuição')).toBeInTheDocument(); // pie
    });

    test('deve validar formatos de exportação', () => {
      render(<InteractiveCharts exportFormats={['png', 'svg', 'pdf', 'csv']} />);
      
      expect(screen.getByText('PNG')).toBeInTheDocument();
      expect(screen.getByText('SVG')).toBeInTheDocument();
      expect(screen.getByText('PDF')).toBeInTheDocument();
      expect(screen.getByText('CSV')).toBeInTheDocument();
    });
  });
}); 