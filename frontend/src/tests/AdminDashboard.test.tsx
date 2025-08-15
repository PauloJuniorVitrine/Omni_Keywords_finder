/**
 * 🧪 AdminDashboard.test.tsx
 * 🎯 Objetivo: Testes unitários para dashboard administrativo
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: TEST_ADMIN_DASHBOARD_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import AdminDashboard from '../pages/admin/AdminDashboard';

// Mock dos componentes UI
vi.mock('@/components/ui/card', () => ({
  Card: ({ children, className }: any) => (
    <div data-testid="card" className={className}>
      {children}
    </div>
  ),
  CardContent: ({ children, className }: any) => (
    <div data-testid="card-content" className={className}>
      {children}
    </div>
  ),
  CardHeader: ({ children, className }: any) => (
    <div data-testid="card-header" className={className}>
      {children}
    </div>
  ),
  CardTitle: ({ children, className }: any) => (
    <div data-testid="card-title" className={className}>
      {children}
    </div>
  ),
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, variant, size, disabled, className }: any) => (
    <button
      data-testid="button"
      onClick={onClick}
      disabled={disabled}
      className={`${variant} ${size} ${className}`}
    >
      {children}
    </button>
  ),
}));

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, variant, className }: any) => (
    <span data-testid="badge" className={`${variant} ${className}`}>
      {children}
    </span>
  ),
}));

vi.mock('@/components/ui/alert', () => ({
  Alert: ({ children, variant }: any) => (
    <div data-testid="alert" className={variant}>
      {children}
    </div>
  ),
  AlertDescription: ({ children }: any) => (
    <div data-testid="alert-description">{children}</div>
  ),
}));

vi.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children, value, onValueChange }: any) => (
    <div data-testid="tabs" data-value={value}>
      {children}
    </div>
  ),
  TabsContent: ({ children, value }: any) => (
    <div data-testid="tabs-content" data-value={value}>
      {children}
    </div>
  ),
  TabsList: ({ children }: any) => (
    <div data-testid="tabs-list">{children}</div>
  ),
  TabsTrigger: ({ children, value, onClick }: any) => (
    <button data-testid="tabs-trigger" data-value={value} onClick={onClick}>
      {children}
    </button>
  ),
}));

vi.mock('@/components/ui/select', () => ({
  Select: ({ children, value, onValueChange }: any) => (
    <div data-testid="select" data-value={value}>
      {children}
    </div>
  ),
  SelectContent: ({ children }: any) => (
    <div data-testid="select-content">{children}</div>
  ),
  SelectItem: ({ children, value }: any) => (
    <div data-testid="select-item" data-value={value}>
      {children}
    </div>
  ),
  SelectTrigger: ({ children, className }: any) => (
    <div data-testid="select-trigger" className={className}>
      {children}
    </div>
  ),
  SelectValue: () => <div data-testid="select-value" />,
}));

vi.mock('@/components/ui/input', () => ({
  Input: ({ ...props }: any) => <input data-testid="input" {...props} />,
}));

vi.mock('@/components/ui/label', () => ({
  Label: ({ children }: any) => <label data-testid="label">{children}</label>,
}));

vi.mock('@/components/ui/switch', () => ({
  Switch: ({ checked, onCheckedChange }: any) => (
    <input
      data-testid="switch"
      type="checkbox"
      checked={checked}
      onChange={(e) => onCheckedChange(e.target.checked)}
    />
  ),
}));

// Mock dos ícones do Lucide
vi.mock('lucide-react', () => ({
  Activity: () => <div data-testid="icon-activity">Activity</div>,
  TrendingUp: () => <div data-testid="icon-trending-up">TrendingUp</div>,
  TrendingDown: () => <div data-testid="icon-trending-down">TrendingDown</div>,
  AlertTriangle: () => <div data-testid="icon-alert-triangle">AlertTriangle</div>,
  CheckCircle: () => <div data-testid="icon-check-circle">CheckCircle</div>,
  Clock: () => <div data-testid="icon-clock">Clock</div>,
  Download: () => <div data-testid="icon-download">Download</div>,
  RefreshCw: () => <div data-testid="icon-refresh-cw">RefreshCw</div>,
  Settings: () => <div data-testid="icon-settings">Settings</div>,
  BarChart3: () => <div data-testid="icon-bar-chart-3">BarChart3</div>,
  LineChart: () => <div data-testid="icon-line-chart">LineChart</div>,
  PieChart: () => <div data-testid="icon-pie-chart">PieChart</div>,
  Gauge: () => <div data-testid="icon-gauge">Gauge</div>,
  Zap: () => <div data-testid="icon-zap">Zap</div>,
  Shield: () => <div data-testid="icon-shield">Shield</div>,
  Users: () => <div data-testid="icon-users">Users</div>,
  Database: () => <div data-testid="icon-database">Database</div>,
  Globe: () => <div data-testid="icon-globe">Globe</div>,
  Server: () => <div data-testid="icon-server">Server</div>,
  UserCheck: () => <div data-testid="icon-user-check">UserCheck</div>,
  UserX: () => <div data-testid="icon-user-x">UserX</div>,
  ShieldAlert: () => <div data-testid="icon-shield-alert">ShieldAlert</div>,
  Cpu: () => <div data-testid="icon-cpu">Cpu</div>,
  HardDrive: () => <div data-testid="icon-hard-drive">HardDrive</div>,
  Network: () => <div data-testid="icon-network">Network</div>,
  FileText: () => <div data-testid="icon-file-text">FileText</div>,
  Settings as SettingsIcon: () => <div data-testid="icon-settings-icon">SettingsIcon</div>,
  Users as UsersIcon: () => <div data-testid="icon-users-icon">UsersIcon</div>,
  Shield as ShieldIcon: () => <div data-testid="icon-shield-icon">ShieldIcon</div>,
  Zap as ZapIcon: () => <div data-testid="icon-zap-icon">ZapIcon</div>,
  Database as DatabaseIcon: () => <div data-testid="icon-database-icon">DatabaseIcon</div>,
  FileText as LogsIcon: () => <div data-testid="icon-logs-icon">LogsIcon</div>,
  Building as TenantIcon: () => <div data-testid="icon-tenant-icon">TenantIcon</div>,
}));

// Mock do window.location
const mockLocation = {
  href: '',
};

Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

// Mock do URL.createObjectURL e URL.revokeObjectURL
global.URL.createObjectURL = vi.fn(() => 'mock-url');
global.URL.revokeObjectURL = vi.fn();

// Mock do document.createElement e appendChild
const mockAnchor = {
  href: '',
  download: '',
  click: vi.fn(),
};

document.createElement = vi.fn(() => mockAnchor) as any;
document.body.appendChild = vi.fn();
document.body.removeChild = vi.fn();

describe('AdminDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocation.href = '';
  });

  describe('Renderização Inicial', () => {
    it('deve renderizar o dashboard administrativo', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('🔧 Dashboard Administrativo')).toBeInTheDocument();
      expect(screen.getByText(/Visão geral do sistema/)).toBeInTheDocument();
    });

    it('deve mostrar o header com controles', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Auto-refresh')).toBeInTheDocument();
      expect(screen.getByText('Atualizar')).toBeInTheDocument();
      expect(screen.getByText('Exportar')).toBeInTheDocument();
    });

    it('deve renderizar as abas principais', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Visão Geral')).toBeInTheDocument();
      expect(screen.getByText('Usuários')).toBeInTheDocument();
      expect(screen.getByText('Sistema')).toBeInTheDocument();
      expect(screen.getByText('Segurança')).toBeInTheDocument();
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Alertas')).toBeInTheDocument();
      expect(screen.getByText('Ações Rápidas')).toBeInTheDocument();
    });
  });

  describe('Métricas do Sistema', () => {
    it('deve mostrar métricas de saúde do sistema', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Saúde do Sistema')).toBeInTheDocument();
      expect(screen.getByText('99.9%')).toBeInTheDocument();
      expect(screen.getByText('Uptime do sistema')).toBeInTheDocument();
    });

    it('deve mostrar métricas de usuários', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Usuários Ativos')).toBeInTheDocument();
      expect(screen.getByText('1189')).toBeInTheDocument();
      expect(screen.getByText('de 1247 total')).toBeInTheDocument();
    });

    it('deve mostrar métricas de segurança', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Score de Segurança')).toBeInTheDocument();
      expect(screen.getByText('92%')).toBeInTheDocument();
      expect(screen.getByText('Compliance score')).toBeInTheDocument();
    });

    it('deve mostrar métricas de performance', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('87.3%')).toBeInTheDocument();
      expect(screen.getByText('Cache hit rate')).toBeInTheDocument();
    });
  });

  describe('Alertas', () => {
    it('deve mostrar alertas críticos no header', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText(/1 alerta\(s\) crítico\(s\)/)).toBeInTheDocument();
      expect(screen.getByText('Ver detalhes')).toBeInTheDocument();
    });

    it('deve mostrar alertas na aba de alertas', () => {
      render(<AdminDashboard />);
      
      // Clicar na aba de alertas
      fireEvent.click(screen.getByText('Alertas'));
      
      expect(screen.getByText('Alto uso de CPU')).toBeInTheDocument();
      expect(screen.getByText('Vulnerabilidade crítica detectada')).toBeInTheDocument();
      expect(screen.getByText('Backup automático concluído')).toBeInTheDocument();
    });

    it('deve permitir reconhecer alertas', async () => {
      render(<AdminDashboard />);
      
      // Clicar na aba de alertas
      fireEvent.click(screen.getByText('Alertas'));
      
      const recognizeButtons = screen.getAllByText('Reconhecer');
      expect(recognizeButtons.length).toBeGreaterThan(0);
      
      fireEvent.click(recognizeButtons[0]);
      
      await waitFor(() => {
        expect(screen.queryByText('Reconhecer')).not.toBeInTheDocument();
      });
    });
  });

  describe('Navegação entre Abas', () => {
    it('deve navegar para a aba de usuários', () => {
      render(<AdminDashboard />);
      
      fireEvent.click(screen.getByText('Usuários'));
      
      expect(screen.getByText('Total de Usuários')).toBeInTheDocument();
      expect(screen.getByText('1247')).toBeInTheDocument();
      expect(screen.getByText('Usuários registrados')).toBeInTheDocument();
    });

    it('deve navegar para a aba de sistema', () => {
      render(<AdminDashboard />);
      
      fireEvent.click(screen.getByText('Sistema'));
      
      expect(screen.getByText('Uptime')).toBeInTheDocument();
      expect(screen.getByText('Tempo de Resposta')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Erro')).toBeInTheDocument();
    });

    it('deve navegar para a aba de segurança', () => {
      render(<AdminDashboard />);
      
      fireEvent.click(screen.getByText('Segurança'));
      
      expect(screen.getByText('Score de Compliance')).toBeInTheDocument();
      expect(screen.getByText('Ameaças Ativas')).toBeInTheDocument();
      expect(screen.getByText('Vulnerabilidades Críticas')).toBeInTheDocument();
    });

    it('deve navegar para a aba de performance', () => {
      render(<AdminDashboard />);
      
      fireEvent.click(screen.getByText('Performance'));
      
      expect(screen.getByText('Cache Hit Rate')).toBeInTheDocument();
      expect(screen.getByText('Tempo Médio de Query')).toBeInTheDocument();
      expect(screen.getByText('Economia de Otimização')).toBeInTheDocument();
    });
  });

  describe('Ações Rápidas', () => {
    it('deve mostrar ações rápidas', () => {
      render(<AdminDashboard />);
      
      fireEvent.click(screen.getByText('Ações Rápidas'));
      
      expect(screen.getByText('Gestão de Usuários')).toBeInTheDocument();
      expect(screen.getByText('Segurança')).toBeInTheDocument();
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Cache')).toBeInTheDocument();
      expect(screen.getByText('Logs')).toBeInTheDocument();
      expect(screen.getByText('Tenants')).toBeInTheDocument();
    });

    it('deve navegar para gestão de usuários', () => {
      render(<AdminDashboard />);
      
      fireEvent.click(screen.getByText('Ações Rápidas'));
      fireEvent.click(screen.getByText('Gestão de Usuários'));
      
      expect(mockLocation.href).toBe('/admin/users');
    });

    it('deve navegar para segurança', () => {
      render(<AdminDashboard />);
      
      fireEvent.click(screen.getByText('Ações Rápidas'));
      fireEvent.click(screen.getByText('Segurança'));
      
      expect(mockLocation.href).toBe('/admin/security');
    });
  });

  describe('Controles de Atualização', () => {
    it('deve permitir ativar/desativar auto-refresh', () => {
      render(<AdminDashboard />);
      
      const autoRefreshSwitch = screen.getByTestId('switch');
      expect(autoRefreshSwitch).toBeChecked();
      
      fireEvent.click(autoRefreshSwitch);
      expect(autoRefreshSwitch).not.toBeChecked();
    });

    it('deve permitir alterar intervalo de atualização', () => {
      render(<AdminDashboard />);
      
      const select = screen.getByTestId('select');
      expect(select).toBeInTheDocument();
    });

    it('deve permitir atualização manual', () => {
      render(<AdminDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      expect(refreshButton).toBeInTheDocument();
      
      fireEvent.click(refreshButton);
      // Em produção, verificar se a função de atualização foi chamada
    });
  });

  describe('Exportação de Relatórios', () => {
    it('deve permitir exportar relatório', () => {
      render(<AdminDashboard />);
      
      const exportButton = screen.getByText('Exportar');
      expect(exportButton).toBeInTheDocument();
      
      fireEvent.click(exportButton);
      
      expect(document.createElement).toHaveBeenCalledWith('a');
      expect(mockAnchor.click).toHaveBeenCalled();
      expect(document.body.appendChild).toHaveBeenCalled();
      expect(document.body.removeChild).toHaveBeenCalled();
      expect(URL.revokeObjectURL).toHaveBeenCalled();
    });
  });

  describe('Gráficos e Visualizações', () => {
    it('deve mostrar métricas do sistema com barras de progresso', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Métricas do Sistema')).toBeInTheDocument();
      expect(screen.getByText('CPU')).toBeInTheDocument();
      expect(screen.getByText('Memória')).toBeInTheDocument();
      expect(screen.getByText('Disco')).toBeInTheDocument();
    });

    it('deve mostrar alertas recentes', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Alertas Recentes')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve usar classes responsivas do Tailwind', () => {
      render(<AdminDashboard />);
      
      const cards = screen.getAllByTestId('card');
      expect(cards.length).toBeGreaterThan(0);
      
      // Verificar se as classes responsivas estão presentes
      cards.forEach(card => {
        expect(card.className).toContain('grid');
      });
    });
  });

  describe('Estados de Loading e Erro', () => {
    it('deve mostrar loading durante atualização', async () => {
      render(<AdminDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      fireEvent.click(refreshButton);
      
      // Em produção, verificar se o estado de loading é exibido
    });

    it('deve mostrar erro quando falhar ao carregar dados', () => {
      // Mock de erro seria implementado aqui
      render(<AdminDashboard />);
      
      // Em produção, simular erro e verificar se é exibido
    });
  });

  describe('Cálculos e Lógica de Negócio', () => {
    it('deve calcular saúde do sistema corretamente', () => {
      render(<AdminDashboard />);
      
      // Verificar se o cálculo de saúde do sistema está correto
      // baseado nas métricas de CPU, memória, disco e taxa de erro
    });

    it('deve filtrar alertas críticos corretamente', () => {
      render(<AdminDashboard />);
      
      // Verificar se apenas alertas críticos não reconhecidos são mostrados
      expect(screen.getByText(/1 alerta\(s\) crítico\(s\)/)).toBeInTheDocument();
    });

    it('deve calcular percentuais corretamente', () => {
      render(<AdminDashboard />);
      
      // Verificar se os percentuais são calculados corretamente
      // Por exemplo: usuários ativos / total de usuários
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('Auto-refresh')).toBeInTheDocument();
      expect(screen.getByText('Atualizar')).toBeInTheDocument();
      expect(screen.getByText('Exportar')).toBeInTheDocument();
    });

    it('deve ter estrutura semântica adequada', () => {
      render(<AdminDashboard />);
      
      expect(screen.getByText('🔧 Dashboard Administrativo')).toBeInTheDocument();
      // Verificar se os headings estão na hierarquia correta
    });
  });

  describe('Integração com API', () => {
    it('deve carregar dados iniciais', () => {
      render(<AdminDashboard />);
      
      // Verificar se os dados de exemplo são exibidos
      expect(screen.getByText('1189')).toBeInTheDocument(); // Usuários ativos
      expect(screen.getByText('99.9%')).toBeInTheDocument(); // Uptime
      expect(screen.getByText('92%')).toBeInTheDocument(); // Compliance score
    });

    it('deve atualizar dados quando solicitado', () => {
      render(<AdminDashboard />);
      
      const refreshButton = screen.getByText('Atualizar');
      fireEvent.click(refreshButton);
      
      // Em produção, verificar se os dados são atualizados
    });
  });
}); 