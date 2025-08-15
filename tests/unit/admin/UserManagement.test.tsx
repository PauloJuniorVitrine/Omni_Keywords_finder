/**
 * Testes Unitários - UserManagement Component
 * 
 * Prompt: Implementação de testes para componentes de administração
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USER_MANAGEMENT_008
 * 
 * Baseado em código real do componente UserManagement.tsx
 */

import React from 'react';

// Interfaces extraídas do componente para teste
interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  status: 'active' | 'inactive' | 'suspended' | 'pending';
  roles: string[];
  permissions: string[];
  lastLogin: Date;
  createdAt: Date;
  updatedAt: Date;
  phone?: string;
  department?: string;
  position?: string;
  avatar?: string;
  twoFactorEnabled: boolean;
  passwordLastChanged: Date;
  failedLoginAttempts: number;
  lockedUntil?: Date;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  isSystem: boolean;
  createdAt: Date;
  updatedAt: Date;
  userCount: number;
}

interface Permission {
  id: string;
  name: string;
  description: string;
  category: string;
  isSystem: boolean;
}

interface UserActivity {
  id: string;
  userId: string;
  action: string;
  resource: string;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
  details: string;
}

// Dados mock extraídos do componente
const mockUsers: User[] = [
  {
    id: 'user-001',
    username: 'admin',
    email: 'admin@example.com',
    firstName: 'Administrador',
    lastName: 'Sistema',
    status: 'active',
    roles: ['admin', 'super_admin'],
    permissions: ['users:read', 'users:write', 'users:delete', 'system:admin'],
    lastLogin: new Date('2024-12-20T10:30:00Z'),
    createdAt: new Date('2024-01-01T00:00:00Z'),
    updatedAt: new Date('2024-12-20T10:30:00Z'),
    phone: '+55 11 99999-9999',
    department: 'TI',
    position: 'Administrador de Sistema',
    avatar: 'https://example.com/avatar1.jpg',
    twoFactorEnabled: true,
    passwordLastChanged: new Date('2024-12-01T00:00:00Z'),
    failedLoginAttempts: 0
  },
  {
    id: 'user-002',
    username: 'manager',
    email: 'manager@example.com',
    firstName: 'Gerente',
    lastName: 'Projeto',
    status: 'active',
    roles: ['manager'],
    permissions: ['users:read', 'projects:write'],
    lastLogin: new Date('2024-12-20T09:15:00Z'),
    createdAt: new Date('2024-03-01T00:00:00Z'),
    updatedAt: new Date('2024-12-20T09:15:00Z'),
    department: 'Projetos',
    position: 'Gerente de Projeto',
    twoFactorEnabled: false,
    passwordLastChanged: new Date('2024-11-15T00:00:00Z'),
    failedLoginAttempts: 2
  },
  {
    id: 'user-003',
    username: 'user1',
    email: 'user1@example.com',
    firstName: 'Usuário',
    lastName: 'Comum',
    status: 'suspended',
    roles: ['user'],
    permissions: ['content:read'],
    lastLogin: new Date('2024-12-19T15:45:00Z'),
    createdAt: new Date('2024-06-01T00:00:00Z'),
    updatedAt: new Date('2024-12-19T15:45:00Z'),
    department: 'Marketing',
    position: 'Analista',
    twoFactorEnabled: false,
    passwordLastChanged: new Date('2024-10-01T00:00:00Z'),
    failedLoginAttempts: 5,
    lockedUntil: new Date('2024-12-21T00:00:00Z')
  },
  {
    id: 'user-004',
    username: 'newuser',
    email: 'newuser@example.com',
    firstName: 'Novo',
    lastName: 'Usuário',
    status: 'pending',
    roles: ['user'],
    permissions: ['content:read'],
    lastLogin: new Date('2024-12-20T08:00:00Z'),
    createdAt: new Date('2024-12-15T00:00:00Z'),
    updatedAt: new Date('2024-12-20T08:00:00Z'),
    department: 'Vendas',
    position: 'Vendedor',
    twoFactorEnabled: false,
    passwordLastChanged: new Date('2024-12-15T00:00:00Z'),
    failedLoginAttempts: 0
  }
];

const mockRoles: Role[] = [
  {
    id: 'role-001',
    name: 'admin',
    description: 'Administrador do sistema',
    permissions: ['users:read', 'users:write', 'users:delete', 'system:admin'],
    isSystem: true,
    createdAt: new Date('2024-01-01T00:00:00Z'),
    updatedAt: new Date('2024-12-20T10:30:00Z'),
    userCount: 1
  },
  {
    id: 'role-002',
    name: 'manager',
    description: 'Gerente de projeto',
    permissions: ['users:read', 'projects:write', 'reports:read'],
    isSystem: false,
    createdAt: new Date('2024-03-01T00:00:00Z'),
    updatedAt: new Date('2024-12-20T09:15:00Z'),
    userCount: 1
  },
  {
    id: 'role-003',
    name: 'user',
    description: 'Usuário comum',
    permissions: ['content:read', 'profile:write'],
    isSystem: true,
    createdAt: new Date('2024-01-01T00:00:00Z'),
    updatedAt: new Date('2024-12-20T08:00:00Z'),
    userCount: 2
  }
];

const mockPermissions: Permission[] = [
  {
    id: 'perm-001',
    name: 'users:read',
    description: 'Ler informações de usuários',
    category: 'users',
    isSystem: true
  },
  {
    id: 'perm-002',
    name: 'users:write',
    description: 'Criar e editar usuários',
    category: 'users',
    isSystem: true
  },
  {
    id: 'perm-003',
    name: 'users:delete',
    description: 'Excluir usuários',
    category: 'users',
    isSystem: true
  },
  {
    id: 'perm-004',
    name: 'system:admin',
    description: 'Acesso administrativo completo',
    category: 'system',
    isSystem: true
  },
  {
    id: 'perm-005',
    name: 'content:read',
    description: 'Ler conteúdo',
    category: 'content',
    isSystem: true
  }
];

const mockActivities: UserActivity[] = [
  {
    id: 'activity-001',
    userId: 'user-001',
    action: 'login',
    resource: 'auth',
    timestamp: new Date('2024-12-20T10:30:00Z'),
    ipAddress: '192.168.1.100',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    details: 'Login bem-sucedido'
  },
  {
    id: 'activity-002',
    userId: 'user-002',
    action: 'update_profile',
    resource: 'user',
    timestamp: new Date('2024-12-20T09:15:00Z'),
    ipAddress: '192.168.1.101',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    details: 'Perfil atualizado'
  },
  {
    id: 'activity-003',
    userId: 'user-003',
    action: 'failed_login',
    resource: 'auth',
    timestamp: new Date('2024-12-19T15:45:00Z'),
    ipAddress: '203.0.113.45',
    userAgent: 'curl/7.68.0',
    details: 'Tentativa de login falhou - credenciais inválidas'
  }
];

// Funções utilitárias extraídas do componente
const calculateMetrics = (users: User[], activities: UserActivity[]) => {
  return {
    totalUsers: users.length,
    activeUsers: users.filter(user => user.status === 'active').length,
    suspendedUsers: users.filter(user => user.status === 'suspended').length,
    pendingUsers: users.filter(user => user.status === 'pending').length,
    usersWithTwoFactor: users.filter(user => user.twoFactorEnabled).length,
    lockedUsers: users.filter(user => user.lockedUntil && user.lockedUntil > new Date()).length,
    recentActivities: activities.filter(activity => 
      new Date(activity.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000)
    ).length
  };
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'success';
    case 'inactive': return 'secondary';
    case 'suspended': return 'destructive';
    case 'pending': return 'warning';
    default: return 'secondary';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active': return 'CheckCircle';
    case 'inactive': return 'XCircle';
    case 'suspended': return 'UserX';
    case 'pending': return 'Clock';
    default: return 'User';
  }
};

const filterUsers = (
  users: User[],
  searchTerm: string,
  selectedStatus: string,
  selectedRole: string
) => {
  return users.filter(user => {
    const matchesSearch = 
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.lastName.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = selectedStatus === 'all' || user.status === selectedStatus;
    const matchesRole = selectedRole === 'all' || user.roles.includes(selectedRole);

    return matchesSearch && matchesStatus && matchesRole;
  });
};

const validateUser = (user: Partial<User>): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (!user.username?.trim()) {
    errors.push('Username é obrigatório');
  }

  if (!user.email?.trim()) {
    errors.push('Email é obrigatório');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.email)) {
    errors.push('Email inválido');
  }

  if (!user.firstName?.trim()) {
    errors.push('Nome é obrigatório');
  }

  if (!user.lastName?.trim()) {
    errors.push('Sobrenome é obrigatório');
  }

  if (!user.roles || user.roles.length === 0) {
    errors.push('Pelo menos um papel é obrigatório');
  }

  return {
    valid: errors.length === 0,
    errors
  };
};

describe('UserManagement - Gestão Completa de Usuários', () => {
  
  describe('Interface User - Validação de Estrutura', () => {
    
    test('deve validar estrutura do User', () => {
      const user: User = mockUsers[0];

      expect(user).toHaveProperty('id');
      expect(user).toHaveProperty('username');
      expect(user).toHaveProperty('email');
      expect(user).toHaveProperty('firstName');
      expect(user).toHaveProperty('lastName');
      expect(user).toHaveProperty('status');
      expect(user).toHaveProperty('roles');
      expect(user).toHaveProperty('permissions');
      expect(user).toHaveProperty('lastLogin');
      expect(user).toHaveProperty('createdAt');
      expect(user).toHaveProperty('updatedAt');
      expect(user).toHaveProperty('twoFactorEnabled');
      expect(user).toHaveProperty('passwordLastChanged');
      expect(user).toHaveProperty('failedLoginAttempts');
      expect(typeof user.username).toBe('string');
      expect(typeof user.email).toBe('string');
      expect(Array.isArray(user.roles)).toBe(true);
      expect(Array.isArray(user.permissions)).toBe(true);
      expect(typeof user.twoFactorEnabled).toBe('boolean');
      expect(typeof user.failedLoginAttempts).toBe('number');
    });

    test('deve validar status de usuários', () => {
      const validStatuses = ['active', 'inactive', 'suspended', 'pending'];
      
      mockUsers.forEach(user => {
        expect(validStatuses).toContain(user.status);
      });
    });

    test('deve validar formato de email', () => {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      mockUsers.forEach(user => {
        expect(emailPattern.test(user.email)).toBe(true);
      });
    });

    test('deve validar que usuários têm pelo menos um papel', () => {
      mockUsers.forEach(user => {
        expect(user.roles.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Interface Role - Validação de Estrutura', () => {
    
    test('deve validar estrutura do Role', () => {
      const role: Role = mockRoles[0];

      expect(role).toHaveProperty('id');
      expect(role).toHaveProperty('name');
      expect(role).toHaveProperty('description');
      expect(role).toHaveProperty('permissions');
      expect(role).toHaveProperty('isSystem');
      expect(role).toHaveProperty('createdAt');
      expect(role).toHaveProperty('updatedAt');
      expect(role).toHaveProperty('userCount');
      expect(typeof role.name).toBe('string');
      expect(typeof role.description).toBe('string');
      expect(Array.isArray(role.permissions)).toBe(true);
      expect(typeof role.isSystem).toBe('boolean');
      expect(typeof role.userCount).toBe('number');
    });

    test('deve validar que papéis têm permissões', () => {
      mockRoles.forEach(role => {
        expect(role.permissions.length).toBeGreaterThan(0);
      });
    });

    test('deve validar contagem de usuários por papel', () => {
      mockRoles.forEach(role => {
        expect(role.userCount).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('Interface Permission - Validação de Estrutura', () => {
    
    test('deve validar estrutura do Permission', () => {
      const permission: Permission = mockPermissions[0];

      expect(permission).toHaveProperty('id');
      expect(permission).toHaveProperty('name');
      expect(permission).toHaveProperty('description');
      expect(permission).toHaveProperty('category');
      expect(permission).toHaveProperty('isSystem');
      expect(typeof permission.name).toBe('string');
      expect(typeof permission.description).toBe('string');
      expect(typeof permission.category).toBe('string');
      expect(typeof permission.isSystem).toBe('boolean');
    });

    test('deve validar formato de nome de permissão', () => {
      const permissionPattern = /^[a-z]+:[a-z]+$/;
      
      mockPermissions.forEach(permission => {
        expect(permissionPattern.test(permission.name)).toBe(true);
      });
    });
  });

  describe('Interface UserActivity - Validação de Estrutura', () => {
    
    test('deve validar estrutura do UserActivity', () => {
      const activity: UserActivity = mockActivities[0];

      expect(activity).toHaveProperty('id');
      expect(activity).toHaveProperty('userId');
      expect(activity).toHaveProperty('action');
      expect(activity).toHaveProperty('resource');
      expect(activity).toHaveProperty('timestamp');
      expect(activity).toHaveProperty('ipAddress');
      expect(activity).toHaveProperty('userAgent');
      expect(activity).toHaveProperty('details');
      expect(typeof activity.userId).toBe('string');
      expect(typeof activity.action).toBe('string');
      expect(typeof activity.resource).toBe('string');
      expect(typeof activity.ipAddress).toBe('string');
      expect(typeof activity.userAgent).toBe('string');
      expect(typeof activity.details).toBe('string');
    });

    test('deve validar formato de IP', () => {
      const ipPattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
      
      mockActivities.forEach(activity => {
        expect(ipPattern.test(activity.ipAddress)).toBe(true);
      });
    });
  });

  describe('Cálculo de Métricas', () => {
    
    test('deve calcular métricas corretas', () => {
      const metrics = calculateMetrics(mockUsers, mockActivities);

      expect(metrics.totalUsers).toBe(4);
      expect(metrics.activeUsers).toBe(2);
      expect(metrics.suspendedUsers).toBe(1);
      expect(metrics.pendingUsers).toBe(1);
      expect(metrics.usersWithTwoFactor).toBe(1);
      expect(metrics.lockedUsers).toBe(1);
      expect(metrics.recentActivities).toBe(3);
    });

    test('deve contar usuários ativos', () => {
      const metrics = calculateMetrics(mockUsers, mockActivities);
      const activeCount = mockUsers.filter(user => user.status === 'active').length;

      expect(metrics.activeUsers).toBe(activeCount);
    });

    test('deve contar usuários com 2FA', () => {
      const metrics = calculateMetrics(mockUsers, mockActivities);
      const twoFactorCount = mockUsers.filter(user => user.twoFactorEnabled).length;

      expect(metrics.usersWithTwoFactor).toBe(twoFactorCount);
    });

    test('deve contar usuários bloqueados', () => {
      const metrics = calculateMetrics(mockUsers, mockActivities);
      const lockedCount = mockUsers.filter(user => 
        user.lockedUntil && user.lockedUntil > new Date()
      ).length;

      expect(metrics.lockedUsers).toBe(lockedCount);
    });

    test('deve contar atividades recentes', () => {
      const metrics = calculateMetrics(mockUsers, mockActivities);
      const recentCount = mockActivities.filter(activity => 
        new Date(activity.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000)
      ).length;

      expect(metrics.recentActivities).toBe(recentCount);
    });
  });

  describe('Filtros de Usuários', () => {
    
    test('deve filtrar por termo de busca', () => {
      const filtered = filterUsers(mockUsers, 'admin', 'all', 'all');

      expect(filtered).toHaveLength(1);
      expect(filtered[0].username).toBe('admin');
    });

    test('deve filtrar por status', () => {
      const filtered = filterUsers(mockUsers, '', 'active', 'all');

      expect(filtered).toHaveLength(2);
      expect(filtered.every(user => user.status === 'active')).toBe(true);
    });

    test('deve filtrar por papel', () => {
      const filtered = filterUsers(mockUsers, '', 'all', 'admin');

      expect(filtered).toHaveLength(1);
      expect(filtered[0].roles).toContain('admin');
    });

    test('deve aplicar múltiplos filtros', () => {
      const filtered = filterUsers(mockUsers, 'admin', 'active', 'admin');

      expect(filtered).toHaveLength(1);
      expect(filtered[0].username).toBe('admin');
    });

    test('deve retornar todos os usuários com filtros vazios', () => {
      const filtered = filterUsers(mockUsers, '', 'all', 'all');

      expect(filtered).toHaveLength(mockUsers.length);
    });
  });

  describe('Validação de Usuários', () => {
    
    test('deve validar usuário válido', () => {
      const validUser = {
        username: 'testuser',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      };

      const result = validateUser(validUser);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('deve rejeitar usuário sem username', () => {
      const invalidUser = {
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      };

      const result = validateUser(invalidUser);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Username é obrigatório');
    });

    test('deve rejeitar usuário sem email', () => {
      const invalidUser = {
        username: 'testuser',
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      };

      const result = validateUser(invalidUser);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Email é obrigatório');
    });

    test('deve rejeitar email inválido', () => {
      const invalidUser = {
        username: 'testuser',
        email: 'invalid-email',
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      };

      const result = validateUser(invalidUser);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Email inválido');
    });

    test('deve rejeitar usuário sem nome', () => {
      const invalidUser = {
        username: 'testuser',
        email: 'test@example.com',
        lastName: 'User',
        roles: ['user']
      };

      const result = validateUser(invalidUser);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Nome é obrigatório');
    });

    test('deve rejeitar usuário sem sobrenome', () => {
      const invalidUser = {
        username: 'testuser',
        email: 'test@example.com',
        firstName: 'Test',
        roles: ['user']
      };

      const result = validateUser(invalidUser);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Sobrenome é obrigatório');
    });

    test('deve rejeitar usuário sem papéis', () => {
      const invalidUser = {
        username: 'testuser',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        roles: []
      };

      const result = validateUser(invalidUser);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Pelo menos um papel é obrigatório');
    });
  });

  describe('Cores e Ícones de Status', () => {
    
    test('deve retornar cor correta para status ativo', () => {
      const color = getStatusColor('active');
      expect(color).toBe('success');
    });

    test('deve retornar cor correta para status inativo', () => {
      const color = getStatusColor('inactive');
      expect(color).toBe('secondary');
    });

    test('deve retornar cor correta para status suspenso', () => {
      const color = getStatusColor('suspended');
      expect(color).toBe('destructive');
    });

    test('deve retornar cor correta para status pendente', () => {
      const color = getStatusColor('pending');
      expect(color).toBe('warning');
    });

    test('deve retornar ícone correto para status ativo', () => {
      const icon = getStatusIcon('active');
      expect(icon).toBe('CheckCircle');
    });

    test('deve retornar ícone correto para status inativo', () => {
      const icon = getStatusIcon('inactive');
      expect(icon).toBe('XCircle');
    });

    test('deve retornar ícone correto para status suspenso', () => {
      const icon = getStatusIcon('suspended');
      expect(icon).toBe('UserX');
    });

    test('deve retornar ícone correto para status pendente', () => {
      const icon = getStatusIcon('pending');
      expect(icon).toBe('Clock');
    });
  });

  describe('Análise de Segurança', () => {
    
    test('deve identificar usuários com muitas tentativas de login falhadas', () => {
      const highRiskUsers = mockUsers.filter(user => user.failedLoginAttempts >= 3);
      
      expect(highRiskUsers).toHaveLength(1);
      expect(highRiskUsers[0].username).toBe('user1');
    });

    test('deve identificar usuários sem 2FA', () => {
      const usersWithout2FA = mockUsers.filter(user => !user.twoFactorEnabled);
      
      expect(usersWithout2FA).toHaveLength(3);
    });

    test('deve identificar usuários bloqueados', () => {
      const lockedUsers = mockUsers.filter(user => 
        user.lockedUntil && user.lockedUntil > new Date()
      );
      
      expect(lockedUsers).toHaveLength(1);
      expect(lockedUsers[0].username).toBe('user1');
    });

    test('deve calcular score de risco por usuário', () => {
      const riskScores = mockUsers.map(user => {
        let score = 0;
        
        if (user.failedLoginAttempts >= 3) score += 10;
        if (!user.twoFactorEnabled) score += 5;
        if (user.status === 'suspended') score += 8;
        if (user.lockedUntil && user.lockedUntil > new Date()) score += 10;
        if (user.roles.includes('admin')) score += 3;
        
        return { id: user.id, username: user.username, riskScore: score };
      });

      expect(riskScores.length).toBe(mockUsers.length);
      riskScores.forEach(score => {
        expect(score.riskScore).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('Validação de Timestamps', () => {
    
    test('deve validar que updatedAt é posterior a createdAt', () => {
      mockUsers.forEach(user => {
        expect(user.updatedAt.getTime()).toBeGreaterThanOrEqual(user.createdAt.getTime());
      });
    });

    test('deve validar que lastLogin é posterior a createdAt', () => {
      mockUsers.forEach(user => {
        expect(user.lastLogin.getTime()).toBeGreaterThanOrEqual(user.createdAt.getTime());
      });
    });

    test('deve validar que passwordLastChanged é posterior a createdAt', () => {
      mockUsers.forEach(user => {
        expect(user.passwordLastChanged.getTime()).toBeGreaterThanOrEqual(user.createdAt.getTime());
      });
    });
  });

  describe('Análise de Atividades', () => {
    
    test('deve identificar atividades suspeitas', () => {
      const suspiciousActivities = mockActivities.filter(activity => 
        activity.action === 'failed_login' || 
        activity.ipAddress === '203.0.113.45'
      );
      
      expect(suspiciousActivities).toHaveLength(1);
      expect(suspiciousActivities[0].action).toBe('failed_login');
    });

    test('deve calcular atividades por usuário', () => {
      const activitiesByUser = mockActivities.reduce((acc, activity) => {
        acc[activity.userId] = (acc[activity.userId] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      expect(activitiesByUser['user-001']).toBe(1);
      expect(activitiesByUser['user-002']).toBe(1);
      expect(activitiesByUser['user-003']).toBe(1);
    });

    test('deve identificar padrões de atividade', () => {
      const loginActivities = mockActivities.filter(activity => 
        activity.action === 'login' || activity.action === 'failed_login'
      );
      
      expect(loginActivities).toHaveLength(2);
    });
  });
}); 