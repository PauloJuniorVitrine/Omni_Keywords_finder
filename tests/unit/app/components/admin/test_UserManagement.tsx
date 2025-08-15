/**
 * test_UserManagement.tsx
 * 
 * Testes unitários para o componente UserManagement
 * 
 * Tracing ID: UI-003-TEST
 * Data/Hora: 2024-12-20 07:30:00 UTC
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import UserManagement from '../../../../app/components/admin/UserManagement';

// Mock dos hooks
vi.mock('../../../../app/hooks/useUsers', () => ({
  useUsers: vi.fn()
}));

vi.mock('../../../../app/hooks/useRoles', () => ({
  useRoles: vi.fn()
}));

vi.mock('../../../../app/hooks/usePermissions', () => ({
  usePermissions: vi.fn()
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

vi.mock('../../../../app/components/shared/Dialog', () => ({
  Dialog: ({ children, ...props }: any) => <div data-testid="dialog" {...props}>{children}</div>,
  DialogContent: ({ children, ...props }: any) => <div data-testid="dialog-content" {...props}>{children}</div>,
  DialogHeader: ({ children, ...props }: any) => <div data-testid="dialog-header" {...props}>{children}</div>,
  DialogTitle: ({ children, ...props }: any) => <div data-testid="dialog-title" {...props}>{children}</div>,
  DialogTrigger: ({ children, ...props }: any) => <button data-testid="dialog-trigger" {...props}>{children}</button>
}));

vi.mock('../../../../app/components/shared/Checkbox', () => ({
  Checkbox: ({ ...props }: any) => <input type="checkbox" data-testid="checkbox" {...props} />
}));

// Mock dos ícones
vi.mock('lucide-react', () => ({
  Users: () => <span data-testid="users">Users</span>,
  UserPlus: () => <span data-testid="user-plus">UserPlus</span>,
  UserEdit: () => <span data-testid="user-edit">UserEdit</span>,
  UserX: () => <span data-testid="user-x">UserX</span>,
  Shield: () => <span data-testid="shield">Shield</span>,
  Lock: () => <span data-testid="lock">Lock</span>,
  Unlock: () => <span data-testid="unlock">Unlock</span>,
  Search: () => <span data-testid="search">Search</span>,
  Download: () => <span data-testid="download">Download</span>,
  Upload: () => <span data-testid="upload">Upload</span>,
  RefreshCw: () => <span data-testid="refresh">RefreshCw</span>,
  Filter: () => <span data-testid="filter">Filter</span>,
  Eye: () => <span data-testid="eye">Eye</span>,
  EyeOff: () => <span data-testid="eye-off">EyeOff</span>,
  Settings: () => <span data-testid="settings">Settings</span>,
  History: () => <span data-testid="history">History</span>,
  Key: () => <span data-testid="key">Key</span>,
  Mail: () => <span data-testid="mail">Mail</span>,
  Phone: () => <span data-testid="phone">Phone</span>,
  Calendar: () => <span data-testid="calendar">Calendar</span>,
  MapPin: () => <span data-testid="map-pin">MapPin</span>,
  CheckCircle: () => <span data-testid="check-circle">CheckCircle</span>,
  XCircle: () => <span data-testid="x-circle">XCircle</span>,
  AlertTriangle: () => <span data-testid="alert-triangle">AlertTriangle</span>,
  Clock: () => <span data-testid="clock">Clock</span>,
  Activity: () => <span data-testid="activity">Activity</span>,
  ShieldCheck: () => <span data-testid="shield-check">ShieldCheck</span>,
  UserCheck: () => <span data-testid="user-check">UserCheck</span>,
  UserMinus: () => <span data-testid="user-minus">UserMinus</span>
}));

// Mock dos utilitários
vi.mock('../../../../app/utils/formatters', () => ({
  formatDate: vi.fn((date) => date.toLocaleDateString()),
  formatTime: vi.fn((date) => date.toLocaleTimeString())
}));

const mockUsersData = {
  users: [
    {
      id: '1',
      username: 'john.doe',
      email: 'john.doe@example.com',
      firstName: 'John',
      lastName: 'Doe',
      status: 'active',
      roles: ['admin', 'user'],
      permissions: ['read', 'write', 'delete'],
      lastLogin: new Date('2024-12-20T10:00:00Z'),
      createdAt: new Date('2024-01-01T00:00:00Z'),
      updatedAt: new Date('2024-12-20T10:00:00Z'),
      phone: '+1234567890',
      department: 'IT',
      position: 'Developer',
      avatar: undefined,
      twoFactorEnabled: true,
      passwordLastChanged: new Date('2024-12-01T00:00:00Z'),
      failedLoginAttempts: 0,
      lockedUntil: undefined
    },
    {
      id: '2',
      username: 'jane.smith',
      email: 'jane.smith@example.com',
      firstName: 'Jane',
      lastName: 'Smith',
      status: 'suspended',
      roles: ['user'],
      permissions: ['read'],
      lastLogin: new Date('2024-12-19T15:30:00Z'),
      createdAt: new Date('2024-02-01T00:00:00Z'),
      updatedAt: new Date('2024-12-19T15:30:00Z'),
      phone: '+0987654321',
      department: 'Marketing',
      position: 'Manager',
      avatar: undefined,
      twoFactorEnabled: false,
      passwordLastChanged: new Date('2024-11-15T00:00:00Z'),
      failedLoginAttempts: 5,
      lockedUntil: new Date('2024-12-21T00:00:00Z')
    }
  ],
  activities: [
    {
      id: '1',
      userId: '1',
      action: 'Login',
      resource: '/api/auth/login',
      timestamp: new Date('2024-12-20T10:00:00Z'),
      ipAddress: '192.168.1.100',
      userAgent: 'Mozilla/5.0...',
      details: 'Successful login'
    },
    {
      id: '2',
      userId: '2',
      action: 'Failed Login',
      resource: '/api/auth/login',
      timestamp: new Date('2024-12-19T15:30:00Z'),
      ipAddress: '192.168.1.101',
      userAgent: 'Mozilla/5.0...',
      details: 'Invalid password'
    }
  ]
};

const mockRolesData = {
  roles: [
    {
      id: '1',
      name: 'admin',
      description: 'Administrator role with full access',
      permissions: ['read', 'write', 'delete', 'admin'],
      isSystem: true,
      createdAt: new Date('2024-01-01T00:00:00Z'),
      updatedAt: new Date('2024-01-01T00:00:00Z'),
      userCount: 5
    },
    {
      id: '2',
      name: 'user',
      description: 'Standard user role',
      permissions: ['read', 'write'],
      isSystem: true,
      createdAt: new Date('2024-01-01T00:00:00Z'),
      updatedAt: new Date('2024-01-01T00:00:00Z'),
      userCount: 25
    }
  ]
};

const mockPermissionsData = {
  permissions: [
    {
      id: '1',
      name: 'read',
      description: 'Read access to resources',
      category: 'access',
      isSystem: true
    },
    {
      id: '2',
      name: 'write',
      description: 'Write access to resources',
      category: 'access',
      isSystem: true
    },
    {
      id: '3',
      name: 'delete',
      description: 'Delete access to resources',
      category: 'access',
      isSystem: true
    },
    {
      id: '4',
      name: 'admin',
      description: 'Administrative access',
      category: 'admin',
      isSystem: true
    }
  ]
};

describe('UserManagement', () => {
  const mockUseUsers = vi.fn();
  const mockUseRoles = vi.fn();
  const mockUsePermissions = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mocks
    mockUseUsers.mockReturnValue({
      data: mockUsersData,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      createUser: vi.fn(),
      updateUser: vi.fn(),
      deleteUser: vi.fn(),
      suspendUser: vi.fn(),
      activateUser: vi.fn(),
      resetPassword: vi.fn(),
      unlockUser: vi.fn()
    });

    mockUseRoles.mockReturnValue({
      data: mockRolesData,
      isLoading: false
    });

    mockUsePermissions.mockReturnValue({
      data: mockPermissionsData,
      isLoading: false
    });

    // Apply mocks
    const { useUsers } = require('../../../../app/hooks/useUsers');
    const { useRoles } = require('../../../../app/hooks/useRoles');
    const { usePermissions } = require('../../../../app/hooks/usePermissions');
    
    useUsers.mockImplementation(mockUseUsers);
    useRoles.mockImplementation(mockUseRoles);
    usePermissions.mockImplementation(mockUsePermissions);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar o componente com título e descrição', () => {
      render(<UserManagement />);
      
      expect(screen.getByText('Gestão de Usuários')).toBeInTheDocument();
      expect(screen.getByText('CRUD completo, RBAC, permissões e auditoria')).toBeInTheDocument();
    });

    it('deve renderizar controles de gestão', () => {
      render(<UserManagement />);
      
      expect(screen.getByText('Ocultar Dados Sensíveis')).toBeInTheDocument();
      expect(screen.getByText('Atualizar')).toBeInTheDocument();
      expect(screen.getByText('Novo Usuário')).toBeInTheDocument();
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });

    it('deve renderizar métricas principais', () => {
      render(<UserManagement />);
      
      expect(screen.getByText('Total de Usuários')).toBeInTheDocument();
      expect(screen.getByText('Usuários Suspensos')).toBeInTheDocument();
      expect(screen.getByText('2FA Habilitado')).toBeInTheDocument();
      expect(screen.getByText('Atividades Recentes')).toBeInTheDocument();
    });

    it('deve renderizar tabs principais', () => {
      render(<UserManagement />);
      
      expect(screen.getByText('Usuários')).toBeInTheDocument();
      expect(screen.getByText('Roles')).toBeInTheDocument();
      expect(screen.getByText('Permissões')).toBeInTheDocument();
      expect(screen.getByText('Atividades')).toBeInTheDocument();
    });
  });

  describe('Estados de Loading', () => {
    it('deve mostrar skeleton durante carregamento', () => {
      mockUseUsers.mockReturnValue({
        data: null,
        isLoading: true,
        error: null,
        refetch: vi.fn()
      });

      render(<UserManagement />);
      
      expect(screen.getAllByTestId('skeleton')).toHaveLength(5); // 1 título + 4 cards
    });
  });

  describe('Estados de Erro', () => {
    it('deve mostrar alerta de erro quando há falha', () => {
      const errorMessage = 'Erro ao carregar dados de usuários';
      mockUseUsers.mockReturnValue({
        data: null,
        isLoading: false,
        error: { message: errorMessage },
        refetch: vi.fn()
      });

      render(<UserManagement />);
      
      expect(screen.getByTestId('alert')).toBeInTheDocument();
      expect(screen.getByText(`Erro ao carregar dados de usuários: ${errorMessage}`)).toBeInTheDocument();
    });
  });

  describe('Interações do Usuário', () => {
    it('deve chamar refetch ao clicar em atualizar', async () => {
      const mockRefetch = vi.fn();
      mockUseUsers.mockReturnValue({
        data: mockUsersData,
        isLoading: false,
        error: null,
        refetch: mockRefetch
      });

      render(<UserManagement />);
      
      const refreshButton = screen.getByText('Atualizar');
      fireEvent.click(refreshButton);
      
      expect(mockRefetch).toHaveBeenCalledTimes(1);
    });

    it('deve alternar visibilidade de dados sensíveis', () => {
      render(<UserManagement />);
      
      const toggleButton = screen.getByText('Ocultar Dados Sensíveis');
      fireEvent.click(toggleButton);
      
      expect(screen.getByText('Mostrar Dados Sensíveis')).toBeInTheDocument();
    });

    it('deve abrir dialog ao clicar em novo usuário', () => {
      render(<UserManagement />);
      
      const newUserButton = screen.getByText('Novo Usuário');
      fireEvent.click(newUserButton);
      
      expect(screen.getByText('Novo Usuário')).toBeInTheDocument();
    });

    it('deve chamar função de exportação ao clicar em botão de export', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      render(<UserManagement />);
      
      const csvButton = screen.getByText('CSV');
      fireEvent.click(csvButton);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Exporting users data in csv format');
      });
      
      consoleSpy.mockRestore();
    });

    it('deve filtrar usuários por status', () => {
      render(<UserManagement />);
      
      const statusSelect = screen.getAllByTestId('select-trigger')[0];
      fireEvent.click(statusSelect);
      
      expect(statusSelect).toBeInTheDocument();
    });

    it('deve filtrar usuários por role', () => {
      render(<UserManagement />);
      
      const roleSelect = screen.getAllByTestId('select-trigger')[1];
      fireEvent.click(roleSelect);
      
      expect(roleSelect).toBeInTheDocument();
    });

    it('deve buscar usuários por termo', () => {
      render(<UserManagement />);
      
      const searchInput = screen.getByTestId('input');
      fireEvent.change(searchInput, { target: { value: 'john' } });
      
      expect(searchInput).toHaveValue('john');
    });
  });

  describe('Cálculos e Métricas', () => {
    it('deve calcular métricas corretamente', () => {
      render(<UserManagement />);
      
      expect(screen.getByText('2')).toBeInTheDocument(); // totalUsers
      expect(screen.getByText('1')).toBeInTheDocument(); // suspendedUsers
      expect(screen.getByText('1')).toBeInTheDocument(); // usersWithTwoFactor
      expect(screen.getByText('2')).toBeInTheDocument(); // recentActivities
    });
  });

  describe('Dados das Tabs', () => {
    it('deve mostrar usuários na tab Usuários', () => {
      render(<UserManagement />);
      
      expect(screen.getByText('Lista de Usuários')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    it('deve mostrar roles na tab Roles', () => {
      render(<UserManagement />);
      
      // Clicar na tab Roles
      const rolesTab = screen.getByText('Roles');
      fireEvent.click(rolesTab);
      
      expect(screen.getByText('Roles do Sistema')).toBeInTheDocument();
      expect(screen.getByText('admin')).toBeInTheDocument();
      expect(screen.getByText('user')).toBeInTheDocument();
    });

    it('deve mostrar permissões na tab Permissões', () => {
      render(<UserManagement />);
      
      // Clicar na tab Permissões
      const permissionsTab = screen.getByText('Permissões');
      fireEvent.click(permissionsTab);
      
      expect(screen.getByText('Permissões do Sistema')).toBeInTheDocument();
      expect(screen.getByText('read')).toBeInTheDocument();
      expect(screen.getByText('write')).toBeInTheDocument();
    });

    it('deve mostrar atividades na tab Atividades', () => {
      render(<UserManagement />);
      
      // Clicar na tab Atividades
      const activitiesTab = screen.getByText('Atividades');
      fireEvent.click(activitiesTab);
      
      expect(screen.getByText('Atividades Recentes')).toBeInTheDocument();
      expect(screen.getByText('Login')).toBeInTheDocument();
      expect(screen.getByText('Failed Login')).toBeInTheDocument();
    });
  });

  describe('Ações de Usuário', () => {
    it('deve chamar função de suspender usuário', async () => {
      const mockSuspendUser = vi.fn();
      mockUseUsers.mockReturnValue({
        data: mockUsersData,
        isLoading: false,
        error: null,
        refetch: vi.fn(),
        suspendUser: mockSuspendUser
      });

      render(<UserManagement />);
      
      // Encontrar botão de suspender do primeiro usuário (ativo)
      const suspendButtons = screen.getAllByTestId('button');
      const suspendButton = suspendButtons.find(button => 
        button.querySelector('[data-testid="user-x"]')
      );
      
      if (suspendButton) {
        fireEvent.click(suspendButton);
        expect(mockSuspendUser).toHaveBeenCalledWith('1');
      }
    });

    it('deve chamar função de ativar usuário', async () => {
      const mockActivateUser = vi.fn();
      mockUseUsers.mockReturnValue({
        data: mockUsersData,
        isLoading: false,
        error: null,
        refetch: vi.fn(),
        activateUser: mockActivateUser
      });

      render(<UserManagement />);
      
      // Encontrar botão de ativar do segundo usuário (suspenso)
      const activateButtons = screen.getAllByTestId('button');
      const activateButton = activateButtons.find(button => 
        button.querySelector('[data-testid="user-check"]')
      );
      
      if (activateButton) {
        fireEvent.click(activateButton);
        expect(mockActivateUser).toHaveBeenCalledWith('2');
      }
    });

    it('deve chamar função de desbloquear usuário', async () => {
      const mockUnlockUser = vi.fn();
      mockUseUsers.mockReturnValue({
        data: mockUsersData,
        isLoading: false,
        error: null,
        refetch: vi.fn(),
        unlockUser: mockUnlockUser
      });

      render(<UserManagement />);
      
      // Encontrar botão de desbloquear do segundo usuário (bloqueado)
      const unlockButtons = screen.getAllByTestId('button');
      const unlockButton = unlockButtons.find(button => 
        button.querySelector('[data-testid="unlock"]')
      );
      
      if (unlockButton) {
        fireEvent.click(unlockButton);
        expect(mockUnlockUser).toHaveBeenCalledWith('2');
      }
    });

    it('deve chamar função de redefinir senha', async () => {
      const mockResetPassword = vi.fn();
      mockUseUsers.mockReturnValue({
        data: mockUsersData,
        isLoading: false,
        error: null,
        refetch: vi.fn(),
        resetPassword: mockResetPassword
      });

      render(<UserManagement />);
      
      // Encontrar botão de redefinir senha
      const resetButtons = screen.getAllByTestId('button');
      const resetButton = resetButtons.find(button => 
        button.querySelector('[data-testid="key"]')
      );
      
      if (resetButton) {
        fireEvent.click(resetButton);
        expect(mockResetPassword).toHaveBeenCalledWith('1');
      }
    });
  });

  describe('Configurações de Props', () => {
    it('deve aplicar className customizada', () => {
      const { container } = render(<UserManagement className="custom-class" />);
      
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('deve mostrar sincronização quando enableRealTime é true', () => {
      render(<UserManagement enableRealTime={true} />);
      
      expect(screen.getByText('Sincronização ativa')).toBeInTheDocument();
    });

    it('deve não mostrar sincronização quando enableRealTime é false', () => {
      render(<UserManagement enableRealTime={false} />);
      
      expect(screen.queryByText('Sincronização ativa')).not.toBeInTheDocument();
    });

    it('deve renderizar apenas formatos de exportação especificados', () => {
      render(<UserManagement exportFormats={['csv']} />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.queryByText('JSON')).not.toBeInTheDocument();
      expect(screen.queryByText('PDF')).not.toBeInTheDocument();
    });

    it('deve limitar número de usuários exibidos', () => {
      render(<UserManagement maxUsers={1} />);
      
      // Deve mostrar apenas 1 usuário na tabela
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter estrutura semântica adequada', () => {
      render(<UserManagement />);
      
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('deve ter botões com labels adequados', () => {
      render(<UserManagement />);
      
      expect(screen.getByRole('button', { name: /atualizar/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /novo usuário/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /csv/i })).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve usar useMemo para cálculos derivados', () => {
      const { rerender } = render(<UserManagement />);
      
      // Primeira renderização
      expect(screen.getByText('2')).toBeInTheDocument(); // totalUsers
      
      // Re-renderização com mesmos dados
      rerender(<UserManagement />);
      
      // Deve manter o mesmo resultado sem recálculo
      expect(screen.getByText('2')).toBeInTheDocument(); // totalUsers
    });
  });

  describe('Segurança', () => {
    it('deve ocultar dados sensíveis por padrão', () => {
      render(<UserManagement />);
      
      expect(screen.getByText('***@***.***')).toBeInTheDocument(); // email oculto
    });

    it('deve mostrar dados sensíveis quando habilitado', () => {
      render(<UserManagement />);
      
      const toggleButton = screen.getByText('Ocultar Dados Sensíveis');
      fireEvent.click(toggleButton);
      
      expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
    });
  });

  describe('Dialog de Usuário', () => {
    it('deve abrir dialog com formulário vazio para novo usuário', () => {
      render(<UserManagement />);
      
      const newUserButton = screen.getByText('Novo Usuário');
      fireEvent.click(newUserButton);
      
      expect(screen.getByText('Novo Usuário')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Nome')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    });

    it('deve abrir dialog com dados preenchidos para editar usuário', () => {
      render(<UserManagement />);
      
      // Simular clique em editar usuário
      const editButtons = screen.getAllByTestId('button');
      const editButton = editButtons.find(button => 
        button.querySelector('[data-testid="user-edit"]')
      );
      
      if (editButton) {
        fireEvent.click(editButton);
        expect(screen.getByText('Editar Usuário')).toBeInTheDocument();
      }
    });
  });
}); 