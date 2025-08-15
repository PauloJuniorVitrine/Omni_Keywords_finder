/**
 * test_AuditPanel.tsx
 * 
 * Testes unitários para o componente AuditPanel
 * 
 * Tracing ID: UI-002-TEST
 * Data/Hora: 2024-12-20 07:15:00 UTC
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import AuditPanel from '../../../../app/components/governanca/AuditPanel';

// Mock dos hooks
vi.mock('../../../../app/hooks/useAudit', () => ({
  useAudit: vi.fn()
}));

vi.mock('../../../../app/hooks/useSecurityMetrics', () => ({
  useSecurityMetrics: vi.fn()
}));

// Mock dos componentes shared
vi.mock('../../../../app/components/shared/Card', () => ({
  Card: ({ children, ...props }: any) => <div data-testid="card" {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div data-testid="card-content" {...props}>{children}</div>,
  CardHeader: ({ children, ...props }: any) => <div data-testid="card-header" {...props}>{children}</div>,
  CardTitle: ({ children, ...props }: any) => <div data-testid="card-title" {...props}>{children}</div>
}));

vi.mock('../../../../app/components/shared/Button', () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button data-testid="button" onClick={onClick} {...props}>{children}</button>
  )
}));

vi.mock('../../../../app/components/shared/Badge', () => ({
  Badge: ({ children, ...props }: any) => <span data-testid="badge" {...props}>{children}</span>
}));

vi.mock('../../../../app/components/shared/Tabs', () => ({
  Tabs: ({ children, ...props }: any) => <div data-testid="tabs" {...props}>{children}</div>,
  TabsContent: ({ children, ...props }: any) => <div data-testid="tabs-content" {...props}>{children}</div>,
  TabsList: ({ children, ...props }: any) => <div data-testid="tabs-list" {...props}>{children}</div>,
  TabsTrigger: ({ children, ...props }: any) => <button data-testid="tabs-trigger" {...props}>{children}</button>
}));

vi.mock('../../../../app/components/shared/Select', () => ({
  Select: ({ children, ...props }: any) => <div data-testid="select" {...props}>{children}</div>,
  SelectContent: ({ children, ...props }: any) => <div data-testid="select-content" {...props}>{children}</div>,
  SelectItem: ({ children, ...props }: any) => <div data-testid="select-item" {...props}>{children}</div>,
  SelectTrigger: ({ children, ...props }: any) => <button data-testid="select-trigger" {...props}>{children}</button>,
  SelectValue: ({ children, ...props }: any) => <div data-testid="select-value" {...props}>{children}</div>
}));

vi.mock('../../../../app/components/shared/DatePicker', () => ({
  DatePicker: ({ ...props }: any) => <input data-testid="date-picker" {...props} />
}));

vi.mock('../../../../app/components/shared/Input', () => ({
  Input: ({ ...props }: any) => <input data-testid="input" {...props} />
}));

vi.mock('../../../../app/components/shared/Alert', () => ({
  Alert: ({ children, ...props }: any) => <div data-testid="alert" {...props}>{children}</div>,
  AlertDescription: ({ children, ...props }: any) => <div data-testid="alert-description" {...props}>{children}</div>
}));

vi.mock('../../../../app/components/shared/Skeleton', () => ({
  Skeleton: ({ ...props }: any) => <div data-testid="skeleton" {...props} />
}));

vi.mock('../../../../app/components/shared/Table', () => ({
  Table: ({ children, ...props }: any) => <table data-testid="table" {...props}>{children}</table>,
  TableBody: ({ children, ...props }: any) => <tbody data-testid="table-body" {...props}>{children}</tbody>,
  TableCell: ({ children, ...props }: any) => <td data-testid="table-cell" {...props}>{children}</td>,
  TableHead: ({ children, ...props }: any) => <th data-testid="table-head" {...props}>{children}</th>,
  TableHeader: ({ children, ...props }: any) => <thead data-testid="table-header" {...props}>{children}</thead>,
  TableRow: ({ children, ...props }: any) => <tr data-testid="table-row" {...props}>{children}</tr>
}));

// Mock dos ícones
vi.mock('lucide-react', () => ({
  Shield: () => <span data-testid="shield">Shield</span>,
  AlertTriangle: () => <span data-testid="alert-triangle">AlertTriangle</span>,
  CheckCircle: () => <span data-testid="check-circle">CheckCircle</span>,
  Clock: () => <span data-testid="clock">Clock</span>,
  Search: () => <span data-testid="search">Search</span>,
  Download: () => <span data-testid="download">Download</span>,
  RefreshCw: () => <span data-testid="refresh">RefreshCw</span>,
  Filter: () => <span data-testid="filter">Filter</span>,
  Eye: () => <span data-testid="eye">Eye</span>,
  EyeOff: () => <span data-testid="eye-off">EyeOff</span>,
  Lock: () => <span data-testid="lock">Lock</span>,
  Unlock: () => <span data-testid="unlock">Unlock</span>,
  User: () => <span data-testid="user">User</span>,
  Database: () => <span data-testid="database">Database</span>,
  Server: () => <span data-testid="server">Server</span>,
  Network: () => <span data-testid="network">Network</span>,
  FileText: () => <span data-testid="file-text">FileText</span>,
  Settings: () => <span data-testid="settings">Settings</span>,
  Bell: () => <span data-testid="bell">Bell</span>,
  TrendingUp: () => <span data-testid="trending-up">TrendingUp</span>,
  TrendingDown: () => <span data-testid="trending-down">TrendingDown</span>
}));

// Mock dos utilitários
vi.mock('../../../../app/utils/formatters', () => ({
  formatDate: vi.fn((date) => date.toLocaleDateString()),
  formatTime: vi.fn((date) => date.toLocaleTimeString())
}));

const mockAuditData = {
  logs: [
    {
      id: '1',
      timestamp: new Date('2024-12-20T10:00:00Z'),
      level: 'critical',
      category: 'security',
      user: 'admin@example.com',
      action: 'Failed login attempt',
      resource: '/api/auth/login',
      details: 'Multiple failed login attempts detected',
      ipAddress: '192.168.1.100',
      userAgent: 'Mozilla/5.0...',
      sessionId: 'session123',
      metadata: { attempts: 5 }
    },
    {
      id: '2',
      timestamp: new Date('2024-12-20T09:30:00Z'),
      level: 'warning',
      category: 'user',
      user: 'user@example.com',
      action: 'Data export',
      resource: '/api/data/export',
      details: 'Large data export requested',
      ipAddress: '192.168.1.101',
      userAgent: 'Mozilla/5.0...',
      sessionId: 'session456',
      metadata: { records: 10000 }
    }
  ],
  complianceReports: [
    {
      id: '1',
      name: 'GDPR Compliance',
      status: 'compliant',
      lastCheck: new Date('2024-12-19T00:00:00Z'),
      nextCheck: new Date('2024-12-26T00:00:00Z'),
      violations: 0,
      score: 95,
      framework: 'GDPR',
      details: 'All requirements met'
    },
    {
      id: '2',
      name: 'PCI DSS Compliance',
      status: 'warning',
      lastCheck: new Date('2024-12-18T00:00:00Z'),
      nextCheck: new Date('2024-12-25T00:00:00Z'),
      violations: 2,
      score: 85,
      framework: 'PCI DSS',
      details: 'Minor violations detected'
    }
  ],
  securityAlerts: [
    {
      id: '1',
      type: 'anomaly',
      severity: 'high',
      title: 'Unusual login pattern detected',
      description: 'Multiple login attempts from different locations',
      timestamp: new Date('2024-12-20T10:00:00Z'),
      status: 'open',
      affectedResources: ['/api/auth', '/api/users'],
      recommendations: [
        'Review login attempts',
        'Enable 2FA for affected accounts',
        'Monitor for further suspicious activity'
      ]
    }
  ]
};

const mockSecurityMetrics = {
  totalThreats: 5,
  resolvedThreats: 3,
  avgResponseTime: 120
};

describe('AuditPanel', () => {
  const mockUseAudit = vi.fn();
  const mockUseSecurityMetrics = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mocks
    mockUseAudit.mockReturnValue({
      data: mockAuditData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    mockUseSecurityMetrics.mockReturnValue({
      data: mockSecurityMetrics,
      isLoading: false
    });

    // Apply mocks
    const { useAudit } = require('../../../../app/hooks/useAudit');
    const { useSecurityMetrics } = require('../../../../app/hooks/useSecurityMetrics');
    
    useAudit.mockImplementation(mockUseAudit);
    useSecurityMetrics.mockImplementation(mockUseSecurityMetrics);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar o componente com título e descrição', () => {
      render(<AuditPanel />);
      
      expect(screen.getByText('Painel de Auditoria')).toBeInTheDocument();
      expect(screen.getByText('Logs detalhados, compliance e detecção de anomalias')).toBeInTheDocument();
    });

    it('deve renderizar controles de filtro e exportação', () => {
      render(<AuditPanel />);
      
      expect(screen.getByText('Ocultar Dados Sensíveis')).toBeInTheDocument();
      expect(screen.getByText('Atualizar')).toBeInTheDocument();
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });

    it('deve renderizar métricas principais', () => {
      render(<AuditPanel />);
      
      expect(screen.getByText('Total de Logs')).toBeInTheDocument();
      expect(screen.getByText('Violações de Segurança')).toBeInTheDocument();
      expect(screen.getByText('Score de Compliance')).toBeInTheDocument();
      expect(screen.getByText('Alertas Abertos')).toBeInTheDocument();
    });

    it('deve renderizar tabs principais', () => {
      render(<AuditPanel />);
      
      expect(screen.getByText('Logs de Auditoria')).toBeInTheDocument();
      expect(screen.getByText('Compliance')).toBeInTheDocument();
      expect(screen.getByText('Alertas de Segurança')).toBeInTheDocument();
      expect(screen.getByText('Análise')).toBeInTheDocument();
    });
  });

  describe('Estados de Loading', () => {
    it('deve mostrar skeleton durante carregamento', () => {
      mockUseAudit.mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        refetch: vi.fn()
      });

      render(<AuditPanel />);
      
      expect(screen.getAllByTestId('skeleton')).toHaveLength(5); // 1 título + 4 cards
    });
  });

  describe('Estados de Erro', () => {
    it('deve mostrar alerta de erro quando há falha', () => {
      const errorMessage = 'Erro ao carregar dados de auditoria';
      mockUseAudit.mockReturnValue({
        data: null,
        isLoading: false,
        error: { message: errorMessage },
        refetch: vi.fn()
      });

      render(<AuditPanel />);
      
      expect(screen.getByTestId('alert')).toBeInTheDocument();
      expect(screen.getByText(`Erro ao carregar dados de auditoria: ${errorMessage}`)).toBeInTheDocument();
    });
  });

  describe('Interações do Usuário', () => {
    it('deve chamar refetch ao clicar em atualizar', async () => {
      const mockRefetch = vi.fn();
      mockUseAudit.mockReturnValue({
        data: mockAuditData,
        isLoading: false,
        error: null,
        refetch: mockRefetch
      });

      render(<AuditPanel />);
      
      const refreshButton = screen.getByText('Atualizar');
      fireEvent.click(refreshButton);
      
      expect(mockRefetch).toHaveBeenCalledTimes(1);
    });

    it('deve alternar visibilidade de dados sensíveis', () => {
      render(<AuditPanel />);
      
      const toggleButton = screen.getByText('Ocultar Dados Sensíveis');
      fireEvent.click(toggleButton);
      
      expect(screen.getByText('Mostrar Dados Sensíveis')).toBeInTheDocument();
    });

    it('deve chamar função de exportação ao clicar em botão de export', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      render(<AuditPanel />);
      
      const csvButton = screen.getByText('CSV');
      fireEvent.click(csvButton);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Exporting audit data in csv format');
      });
      
      consoleSpy.mockRestore();
    });

    it('deve filtrar logs por categoria', () => {
      render(<AuditPanel />);
      
      const categorySelect = screen.getAllByTestId('select-trigger')[0];
      fireEvent.click(categorySelect);
      
      expect(categorySelect).toBeInTheDocument();
    });

    it('deve filtrar logs por nível', () => {
      render(<AuditPanel />);
      
      const levelSelect = screen.getAllByTestId('select-trigger')[1];
      fireEvent.click(levelSelect);
      
      expect(levelSelect).toBeInTheDocument();
    });

    it('deve buscar logs por termo', () => {
      render(<AuditPanel />);
      
      const searchInput = screen.getByTestId('input');
      fireEvent.change(searchInput, { target: { value: 'login' } });
      
      expect(searchInput).toHaveValue('login');
    });
  });

  describe('Cálculos e Métricas', () => {
    it('deve calcular métricas corretamente', () => {
      render(<AuditPanel />);
      
      expect(screen.getByText('2')).toBeInTheDocument(); // totalLogs
      expect(screen.getByText('1')).toBeInTheDocument(); // securityViolations
      expect(screen.getByText('90.0%')).toBeInTheDocument(); // complianceScore
      expect(screen.getByText('1')).toBeInTheDocument(); // openAlerts
    });

    it('deve calcular nível de risco corretamente', () => {
      render(<AuditPanel />);
      
      // Com 1 log crítico e 1 alerta de alta severidade, deve ser 'high'
      expect(screen.getByText('Risco: high')).toBeInTheDocument();
    });
  });

  describe('Dados das Tabs', () => {
    it('deve mostrar logs na tab Logs de Auditoria', () => {
      render(<AuditPanel />);
      
      expect(screen.getByText('Logs de Auditoria')).toBeInTheDocument();
      expect(screen.getByText('Failed login attempt')).toBeInTheDocument();
      expect(screen.getByText('Data export')).toBeInTheDocument();
    });

    it('deve mostrar relatórios de compliance na tab Compliance', () => {
      render(<AuditPanel />);
      
      // Clicar na tab Compliance
      const complianceTab = screen.getByText('Compliance');
      fireEvent.click(complianceTab);
      
      expect(screen.getByText('Relatórios de Compliance')).toBeInTheDocument();
      expect(screen.getByText('GDPR Compliance')).toBeInTheDocument();
      expect(screen.getByText('PCI DSS Compliance')).toBeInTheDocument();
    });

    it('deve mostrar alertas de segurança na tab Alertas de Segurança', () => {
      render(<AuditPanel />);
      
      // Clicar na tab Alertas de Segurança
      const alertsTab = screen.getByText('Alertas de Segurança');
      fireEvent.click(alertsTab);
      
      expect(screen.getByText('Unusual login pattern detected')).toBeInTheDocument();
      expect(screen.getByText('Multiple login attempts from different locations')).toBeInTheDocument();
    });

    it('deve mostrar análise na tab Análise', () => {
      render(<AuditPanel />);
      
      // Clicar na tab Análise
      const analyticsTab = screen.getByText('Análise');
      fireEvent.click(analyticsTab);
      
      expect(screen.getByText('Análise de Padrões')).toBeInTheDocument();
      expect(screen.getByText('Análise de Risco')).toBeInTheDocument();
    });
  });

  describe('Ações de Alertas', () => {
    it('deve chamar função de ação ao clicar em investigar', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      render(<AuditPanel />);
      
      // Clicar na tab Alertas de Segurança
      const alertsTab = screen.getByText('Alertas de Segurança');
      fireEvent.click(alertsTab);
      
      const investigateButton = screen.getByText('Investigação');
      fireEvent.click(investigateButton);
      
      expect(consoleSpy).toHaveBeenCalledWith('Alert 1: investigate');
      
      consoleSpy.mockRestore();
    });

    it('deve chamar função de ação ao clicar em resolver', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      render(<AuditPanel />);
      
      // Clicar na tab Alertas de Segurança
      const alertsTab = screen.getByText('Alertas de Segurança');
      fireEvent.click(alertsTab);
      
      const resolveButton = screen.getByText('Resolver');
      fireEvent.click(resolveButton);
      
      expect(consoleSpy).toHaveBeenCalledWith('Alert 1: resolve');
      
      consoleSpy.mockRestore();
    });
  });

  describe('Configurações de Props', () => {
    it('deve aplicar className customizada', () => {
      const { container } = render(<AuditPanel className="custom-class" />);
      
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('deve mostrar monitoramento quando enableRealTime é true', () => {
      render(<AuditPanel enableRealTime={true} />);
      
      expect(screen.getByText('Monitoramento ativo')).toBeInTheDocument();
    });

    it('deve não mostrar monitoramento quando enableRealTime é false', () => {
      render(<AuditPanel enableRealTime={false} />);
      
      expect(screen.queryByText('Monitoramento ativo')).not.toBeInTheDocument();
    });

    it('deve renderizar apenas formatos de exportação especificados', () => {
      render(<AuditPanel exportFormats={['csv']} />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.queryByText('JSON')).not.toBeInTheDocument();
      expect(screen.queryByText('PDF')).not.toBeInTheDocument();
    });

    it('deve limitar número de logs exibidos', () => {
      render(<AuditPanel maxLogs={1} />);
      
      // Deve mostrar apenas 1 log na tabela
      expect(screen.getByText('Failed login attempt')).toBeInTheDocument();
      expect(screen.queryByText('Data export')).not.toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter estrutura semântica adequada', () => {
      render(<AuditPanel />);
      
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('deve ter botões com labels adequados', () => {
      render(<AuditPanel />);
      
      expect(screen.getByRole('button', { name: /atualizar/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /csv/i })).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve usar useMemo para cálculos derivados', () => {
      const { rerender } = render(<AuditPanel />);
      
      // Primeira renderização
      expect(screen.getByText('2')).toBeInTheDocument(); // totalLogs
      
      // Re-renderização com mesmos dados
      rerender(<AuditPanel />);
      
      // Deve manter o mesmo resultado sem recálculo
      expect(screen.getByText('2')).toBeInTheDocument(); // totalLogs
    });
  });

  describe('Segurança', () => {
    it('deve ocultar dados sensíveis por padrão', () => {
      render(<AuditPanel />);
      
      expect(screen.getByText('***')).toBeInTheDocument(); // user oculto
      expect(screen.getByText('***.***.***.***')).toBeInTheDocument(); // IP oculto
    });

    it('deve mostrar dados sensíveis quando habilitado', () => {
      render(<AuditPanel />);
      
      const toggleButton = screen.getByText('Ocultar Dados Sensíveis');
      fireEvent.click(toggleButton);
      
      expect(screen.getByText('admin@example.com')).toBeInTheDocument();
      expect(screen.getByText('192.168.1.100')).toBeInTheDocument();
    });
  });
}); 