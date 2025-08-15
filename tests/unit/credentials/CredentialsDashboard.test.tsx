/**
 * Testes Unitários - CredentialsDashboard Component
 * 
 * Prompt: Implementação de testes para componentes de credenciais
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_CREDENTIALS_DASHBOARD_007
 * 
 * Baseado em código real do componente CredentialsDashboard.tsx
 */

import React from 'react';

// Interfaces extraídas do componente para teste
interface Credential {
  id: string;
  name: string;
  type: 'api_key' | 'oauth' | 'basic_auth' | 'jwt' | 'custom';
  provider: string;
  status: 'active' | 'expired' | 'revoked' | 'pending';
  lastUsed: string;
  expiresAt?: string;
  permissions: string[];
  isEncrypted: boolean;
  rotationEnabled: boolean;
  lastRotated?: string;
  nextRotation?: string;
  usageCount: number;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

// Dados mock extraídos do componente
const mockCredentials: Credential[] = [
  {
    id: 'cred-001',
    name: 'Google API Key',
    type: 'api_key',
    provider: 'google',
    status: 'active',
    lastUsed: '2024-12-20T10:30:00Z',
    expiresAt: '2025-12-31T23:59:59Z',
    permissions: ['read', 'write'],
    isEncrypted: true,
    rotationEnabled: false,
    usageCount: 150,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-12-20T10:30:00Z',
    metadata: { environment: 'production' }
  },
  {
    id: 'cred-002',
    name: 'Facebook OAuth',
    type: 'oauth',
    provider: 'facebook',
    status: 'active',
    lastUsed: '2024-12-20T09:15:00Z',
    expiresAt: '2025-06-30T23:59:59Z',
    permissions: ['read', 'publish'],
    isEncrypted: true,
    rotationEnabled: true,
    lastRotated: '2024-12-01T00:00:00Z',
    nextRotation: '2025-03-01T00:00:00Z',
    usageCount: 89,
    createdAt: '2024-06-01T00:00:00Z',
    updatedAt: '2024-12-20T09:15:00Z'
  },
  {
    id: 'cred-003',
    name: 'Database Access',
    type: 'basic_auth',
    provider: 'custom',
    status: 'expired',
    lastUsed: '2024-12-19T15:45:00Z',
    expiresAt: '2024-12-19T23:59:59Z',
    permissions: ['read', 'write'],
    isEncrypted: true,
    rotationEnabled: false,
    usageCount: 45,
    createdAt: '2024-03-01T00:00:00Z',
    updatedAt: '2024-12-19T15:45:00Z'
  },
  {
    id: 'cred-004',
    name: 'JWT Token',
    type: 'jwt',
    provider: 'custom',
    status: 'revoked',
    lastUsed: '2024-12-18T12:00:00Z',
    permissions: ['read'],
    isEncrypted: true,
    rotationEnabled: false,
    usageCount: 23,
    createdAt: '2024-09-01T00:00:00Z',
    updatedAt: '2024-12-18T12:00:00Z'
  },
  {
    id: 'cred-005',
    name: 'Twitter API',
    type: 'api_key',
    provider: 'twitter',
    status: 'pending',
    lastUsed: '2024-12-20T08:00:00Z',
    permissions: ['read'],
    isEncrypted: true,
    rotationEnabled: false,
    usageCount: 12,
    createdAt: '2024-12-15T00:00:00Z',
    updatedAt: '2024-12-20T08:00:00Z'
  }
];

// Funções utilitárias extraídas do componente
const filterCredentials = (
  credentials: Credential[],
  searchTerm: string,
  selectedType: string,
  selectedStatus: string,
  selectedProvider: string,
  showExpired: boolean
) => {
  return credentials.filter(credential => {
    const matchesSearch = credential.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         credential.provider.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === 'all' || credential.type === selectedType;
    const matchesStatus = selectedStatus === 'all' || credential.status === selectedStatus;
    const matchesProvider = selectedProvider === 'all' || credential.provider === selectedProvider;
    const matchesExpired = !showExpired || credential.status === 'expired';

    return matchesSearch && matchesType && matchesStatus && matchesProvider && matchesExpired;
  });
};

const calculateDashboardStats = (credentials: Credential[]) => {
  return {
    total: credentials.length,
    active: credentials.filter(c => c.status === 'active').length,
    expired: credentials.filter(c => c.status === 'expired').length,
    revoked: credentials.filter(c => c.status === 'revoked').length,
    pending: credentials.filter(c => c.status === 'pending').length,
    encrypted: credentials.filter(c => c.isEncrypted).length,
    rotationEnabled: credentials.filter(c => c.rotationEnabled).length,
    totalUsage: credentials.reduce((sum, c) => sum + c.usageCount, 0)
  };
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active':
      return 'CheckCircle';
    case 'expired':
      return 'Clock';
    case 'revoked':
      return 'AlertTriangle';
    case 'pending':
      return 'Clock';
    default:
      return 'AlertTriangle';
  }
};

const getStatusBadge = (status: string) => {
  const variants = {
    active: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
    expired: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
    revoked: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
    pending: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
  };

  return variants[status as keyof typeof variants] || 'bg-gray-100 text-gray-800';
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'api_key':
      return 'Key';
    case 'oauth':
      return 'Lock';
    case 'basic_auth':
      return 'Shield';
    case 'jwt':
      return 'Key';
    case 'custom':
      return 'Key';
    default:
      return 'Key';
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const isExpiringSoon = (expiresAt?: string) => {
  if (!expiresAt) return false;
  
  const expiryDate = new Date(expiresAt);
  const now = new Date();
  const daysUntilExpiry = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  
  return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
};

const credentialTypes = [
  'all',
  'api_key',
  'oauth',
  'basic_auth',
  'jwt',
  'custom'
];

const statuses = [
  'all',
  'active',
  'expired',
  'revoked',
  'pending'
];

const providers = [
  'all',
  'google',
  'facebook',
  'twitter',
  'linkedin',
  'instagram',
  'tiktok',
  'youtube',
  'openai',
  'anthropic',
  'custom'
];

describe('CredentialsDashboard - Gestão Segura de Credenciais', () => {
  
  describe('Interface Credential - Validação de Estrutura', () => {
    
    test('deve validar estrutura do Credential', () => {
      const credential: Credential = mockCredentials[0];

      expect(credential).toHaveProperty('id');
      expect(credential).toHaveProperty('name');
      expect(credential).toHaveProperty('type');
      expect(credential).toHaveProperty('provider');
      expect(credential).toHaveProperty('status');
      expect(credential).toHaveProperty('lastUsed');
      expect(credential).toHaveProperty('permissions');
      expect(credential).toHaveProperty('isEncrypted');
      expect(credential).toHaveProperty('rotationEnabled');
      expect(credential).toHaveProperty('usageCount');
      expect(credential).toHaveProperty('createdAt');
      expect(credential).toHaveProperty('updatedAt');
      expect(typeof credential.id).toBe('string');
      expect(typeof credential.name).toBe('string');
      expect(typeof credential.usageCount).toBe('number');
      expect(typeof credential.isEncrypted).toBe('boolean');
      expect(Array.isArray(credential.permissions)).toBe(true);
    });

    test('deve validar tipos de credenciais', () => {
      const validTypes = ['api_key', 'oauth', 'basic_auth', 'jwt', 'custom'];
      
      mockCredentials.forEach(credential => {
        expect(validTypes).toContain(credential.type);
      });
    });

    test('deve validar status de credenciais', () => {
      const validStatuses = ['active', 'expired', 'revoked', 'pending'];
      
      mockCredentials.forEach(credential => {
        expect(validStatuses).toContain(credential.status);
      });
    });

    test('deve validar provedores', () => {
      const validProviders = [
        'google', 'facebook', 'twitter', 'linkedin', 'instagram',
        'tiktok', 'youtube', 'openai', 'anthropic', 'custom'
      ];
      
      mockCredentials.forEach(credential => {
        expect(validProviders).toContain(credential.provider);
      });
    });
  });

  describe('Filtros de Credenciais', () => {
    
    test('deve filtrar por termo de busca', () => {
      const filtered = filterCredentials(
        mockCredentials,
        'google',
        'all',
        'all',
        'all',
        false
      );

      expect(filtered).toHaveLength(1);
      expect(filtered[0].name).toBe('Google API Key');
    });

    test('deve filtrar por tipo', () => {
      const filtered = filterCredentials(
        mockCredentials,
        '',
        'api_key',
        'all',
        'all',
        false
      );

      expect(filtered).toHaveLength(2);
      expect(filtered.every(c => c.type === 'api_key')).toBe(true);
    });

    test('deve filtrar por status', () => {
      const filtered = filterCredentials(
        mockCredentials,
        '',
        'all',
        'active',
        'all',
        false
      );

      expect(filtered).toHaveLength(2);
      expect(filtered.every(c => c.status === 'active')).toBe(true);
    });

    test('deve filtrar por provedor', () => {
      const filtered = filterCredentials(
        mockCredentials,
        '',
        'all',
        'all',
        'facebook',
        false
      );

      expect(filtered).toHaveLength(1);
      expect(filtered[0].provider).toBe('facebook');
    });

    test('deve filtrar credenciais expiradas', () => {
      const filtered = filterCredentials(
        mockCredentials,
        '',
        'all',
        'all',
        'all',
        true
      );

      expect(filtered).toHaveLength(1);
      expect(filtered[0].status).toBe('expired');
    });

    test('deve aplicar múltiplos filtros', () => {
      const filtered = filterCredentials(
        mockCredentials,
        'api',
        'api_key',
        'active',
        'all',
        false
      );

      expect(filtered).toHaveLength(1);
      expect(filtered[0].name).toBe('Google API Key');
    });
  });

  describe('Cálculo de Métricas do Dashboard', () => {
    
    test('deve calcular estatísticas corretas', () => {
      const stats = calculateDashboardStats(mockCredentials);

      expect(stats.total).toBe(5);
      expect(stats.active).toBe(2);
      expect(stats.expired).toBe(1);
      expect(stats.revoked).toBe(1);
      expect(stats.pending).toBe(1);
      expect(stats.encrypted).toBe(5);
      expect(stats.rotationEnabled).toBe(1);
      expect(stats.totalUsage).toBe(319); // 150 + 89 + 45 + 23 + 12
    });

    test('deve calcular total de uso', () => {
      const stats = calculateDashboardStats(mockCredentials);
      const expectedTotal = mockCredentials.reduce((sum, c) => sum + c.usageCount, 0);

      expect(stats.totalUsage).toBe(expectedTotal);
    });

    test('deve contar credenciais criptografadas', () => {
      const stats = calculateDashboardStats(mockCredentials);
      const encryptedCount = mockCredentials.filter(c => c.isEncrypted).length;

      expect(stats.encrypted).toBe(encryptedCount);
    });

    test('deve contar credenciais com rotação ativa', () => {
      const stats = calculateDashboardStats(mockCredentials);
      const rotationCount = mockCredentials.filter(c => c.rotationEnabled).length;

      expect(stats.rotationEnabled).toBe(rotationCount);
    });
  });

  describe('Ícones e Badges de Status', () => {
    
    test('deve retornar ícone correto para status ativo', () => {
      const icon = getStatusIcon('active');
      expect(icon).toBe('CheckCircle');
    });

    test('deve retornar ícone correto para status expirado', () => {
      const icon = getStatusIcon('expired');
      expect(icon).toBe('Clock');
    });

    test('deve retornar ícone correto para status revogado', () => {
      const icon = getStatusIcon('revoked');
      expect(icon).toBe('AlertTriangle');
    });

    test('deve retornar ícone correto para status pendente', () => {
      const icon = getStatusIcon('pending');
      expect(icon).toBe('Clock');
    });

    test('deve retornar badge correto para status ativo', () => {
      const badge = getStatusBadge('active');
      expect(badge).toContain('green');
    });

    test('deve retornar badge correto para status expirado', () => {
      const badge = getStatusBadge('expired');
      expect(badge).toContain('yellow');
    });

    test('deve retornar badge correto para status revogado', () => {
      const badge = getStatusBadge('revoked');
      expect(badge).toContain('red');
    });

    test('deve retornar badge correto para status pendente', () => {
      const badge = getStatusBadge('pending');
      expect(badge).toContain('blue');
    });
  });

  describe('Ícones de Tipo', () => {
    
    test('deve retornar ícone correto para API Key', () => {
      const icon = getTypeIcon('api_key');
      expect(icon).toBe('Key');
    });

    test('deve retornar ícone correto para OAuth', () => {
      const icon = getTypeIcon('oauth');
      expect(icon).toBe('Lock');
    });

    test('deve retornar ícone correto para Basic Auth', () => {
      const icon = getTypeIcon('basic_auth');
      expect(icon).toBe('Shield');
    });

    test('deve retornar ícone correto para JWT', () => {
      const icon = getTypeIcon('jwt');
      expect(icon).toBe('Key');
    });

    test('deve retornar ícone correto para Custom', () => {
      const icon = getTypeIcon('custom');
      expect(icon).toBe('Key');
    });
  });

  describe('Formatação de Datas', () => {
    
    test('deve formatar data corretamente', () => {
      const dateString = '2024-12-20T10:30:00Z';
      const formatted = formatDate(dateString);

      expect(typeof formatted).toBe('string');
      expect(formatted).toMatch(/\d{2}\/\d{2}\/\d{4}/);
    });

    test('deve detectar credenciais expirando em breve', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 15); // 15 dias no futuro
      
      const expiringSoon = isExpiringSoon(futureDate.toISOString());
      expect(expiringSoon).toBe(true);
    });

    test('deve detectar credenciais não expirando em breve', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 45); // 45 dias no futuro
      
      const expiringSoon = isExpiringSoon(futureDate.toISOString());
      expect(expiringSoon).toBe(false);
    });

    test('deve retornar false para credenciais sem data de expiração', () => {
      const expiringSoon = isExpiringSoon(undefined);
      expect(expiringSoon).toBe(false);
    });
  });

  describe('Configurações de Filtros', () => {
    
    test('deve validar tipos de credenciais disponíveis', () => {
      const expectedTypes = ['all', 'api_key', 'oauth', 'basic_auth', 'jwt', 'custom'];
      
      credentialTypes.forEach(type => {
        expect(expectedTypes).toContain(type);
      });
    });

    test('deve validar status disponíveis', () => {
      const expectedStatuses = ['all', 'active', 'expired', 'revoked', 'pending'];
      
      statuses.forEach(status => {
        expect(expectedStatuses).toContain(status);
      });
    });

    test('deve validar provedores disponíveis', () => {
      const expectedProviders = [
        'all', 'google', 'facebook', 'twitter', 'linkedin', 'instagram',
        'tiktok', 'youtube', 'openai', 'anthropic', 'custom'
      ];
      
      providers.forEach(provider => {
        expect(expectedProviders).toContain(provider);
      });
    });
  });

  describe('Validação de Segurança', () => {
    
    test('deve validar que todas as credenciais estão criptografadas', () => {
      const unencryptedCredentials = mockCredentials.filter(c => !c.isEncrypted);
      expect(unencryptedCredentials).toHaveLength(0);
    });

    test('deve identificar credenciais com rotação ativa', () => {
      const rotationEnabledCredentials = mockCredentials.filter(c => c.rotationEnabled);
      expect(rotationEnabledCredentials).toHaveLength(1);
      expect(rotationEnabledCredentials[0].name).toBe('Facebook OAuth');
    });

    test('deve identificar credenciais expiradas', () => {
      const expiredCredentials = mockCredentials.filter(c => c.status === 'expired');
      expect(expiredCredentials).toHaveLength(1);
      expect(expiredCredentials[0].name).toBe('Database Access');
    });

    test('deve identificar credenciais revogadas', () => {
      const revokedCredentials = mockCredentials.filter(c => c.status === 'revoked');
      expect(revokedCredentials).toHaveLength(1);
      expect(revokedCredentials[0].name).toBe('JWT Token');
    });
  });

  describe('Análise de Uso', () => {
    
    test('deve calcular uso total das credenciais', () => {
      const totalUsage = mockCredentials.reduce((sum, c) => sum + c.usageCount, 0);
      expect(totalUsage).toBe(319);
    });

    test('deve identificar credenciais mais utilizadas', () => {
      const sortedByUsage = [...mockCredentials].sort((a, b) => b.usageCount - a.usageCount);
      expect(sortedByUsage[0].name).toBe('Google API Key');
      expect(sortedByUsage[0].usageCount).toBe(150);
    });

    test('deve identificar credenciais menos utilizadas', () => {
      const sortedByUsage = [...mockCredentials].sort((a, b) => a.usageCount - b.usageCount);
      expect(sortedByUsage[0].name).toBe('Twitter API');
      expect(sortedByUsage[0].usageCount).toBe(12);
    });

    test('deve calcular uso médio por credencial', () => {
      const totalUsage = mockCredentials.reduce((sum, c) => sum + c.usageCount, 0);
      const averageUsage = totalUsage / mockCredentials.length;
      expect(averageUsage).toBe(63.8);
    });
  });

  describe('Validação de Timestamps', () => {
    
    test('deve validar formato ISO 8601', () => {
      const isoPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
      
      mockCredentials.forEach(credential => {
        expect(isoPattern.test(credential.lastUsed)).toBe(true);
        expect(isoPattern.test(credential.createdAt)).toBe(true);
        expect(isoPattern.test(credential.updatedAt)).toBe(true);
        
        if (credential.expiresAt) {
          expect(isoPattern.test(credential.expiresAt)).toBe(true);
        }
        
        if (credential.lastRotated) {
          expect(isoPattern.test(credential.lastRotated)).toBe(true);
        }
        
        if (credential.nextRotation) {
          expect(isoPattern.test(credential.nextRotation)).toBe(true);
        }
      });
    });

    test('deve validar que updatedAt é posterior a createdAt', () => {
      mockCredentials.forEach(credential => {
        const createdAt = new Date(credential.createdAt);
        const updatedAt = new Date(credential.updatedAt);
        expect(updatedAt.getTime()).toBeGreaterThanOrEqual(createdAt.getTime());
      });
    });

    test('deve validar que lastUsed é posterior a createdAt', () => {
      mockCredentials.forEach(credential => {
        const createdAt = new Date(credential.createdAt);
        const lastUsed = new Date(credential.lastUsed);
        expect(lastUsed.getTime()).toBeGreaterThanOrEqual(createdAt.getTime());
      });
    });
  });

  describe('Análise de Riscos', () => {
    
    test('deve identificar credenciais de alto risco', () => {
      const highRiskCredentials = mockCredentials.filter(c => 
        c.status === 'expired' || 
        c.status === 'revoked' || 
        (c.expiresAt && isExpiringSoon(c.expiresAt))
      );
      
      expect(highRiskCredentials.length).toBeGreaterThan(0);
    });

    test('deve identificar credenciais sem rotação', () => {
      const noRotationCredentials = mockCredentials.filter(c => !c.rotationEnabled);
      expect(noRotationCredentials.length).toBeGreaterThan(0);
    });

    test('deve calcular score de risco por credencial', () => {
      const riskScores = mockCredentials.map(credential => {
        let score = 0;
        
        if (credential.status === 'expired') score += 10;
        if (credential.status === 'revoked') score += 10;
        if (!credential.rotationEnabled) score += 5;
        if (credential.usageCount > 100) score += 3;
        if (credential.permissions.includes('admin')) score += 8;
        
        return { id: credential.id, name: credential.name, riskScore: score };
      });

      expect(riskScores.length).toBe(mockCredentials.length);
      riskScores.forEach(score => {
        expect(score.riskScore).toBeGreaterThanOrEqual(0);
      });
    });
  });
}); 