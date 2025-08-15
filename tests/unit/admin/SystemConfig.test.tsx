/**
 * Testes Unitários - SystemConfig Component
 * 
 * Prompt: Implementação de testes para componentes de administração
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_SYSTEM_CONFIG_010
 * 
 * Baseado em código real do componente SystemConfig.tsx
 */

import React from 'react';

// Interfaces extraídas do componente para teste
interface SystemConfigData {
  general: {
    appName: string;
    appVersion: string;
    environment: 'development' | 'staging' | 'production';
    timezone: string;
    language: string;
    dateFormat: string;
    timeFormat: string;
    currency: string;
    maxFileSize: number;
    sessionTimeout: number;
  };
  security: {
    passwordMinLength: number;
    passwordRequireUppercase: boolean;
    passwordRequireLowercase: boolean;
    passwordRequireNumbers: boolean;
    passwordRequireSymbols: boolean;
    maxLoginAttempts: number;
    lockoutDuration: number;
    twoFactorEnabled: boolean;
    sslRequired: boolean;
    corsOrigins: string[];
    apiRateLimit: number;
  };
  performance: {
    cacheEnabled: boolean;
    cacheTTL: number;
    compressionEnabled: boolean;
    gzipLevel: number;
    maxConcurrentRequests: number;
    requestTimeout: number;
    databasePoolSize: number;
    backgroundJobWorkers: number;
    memoryLimit: number;
    cpuLimit: number;
  };
  database: {
    type: 'sqlite' | 'postgresql' | 'mysql' | 'mongodb';
    host: string;
    port: number;
    name: string;
    username: string;
    password: string;
    sslEnabled: boolean;
    connectionPool: number;
    timeout: number;
    maxConnections: number;
    migrationsEnabled: boolean;
  };
  api: {
    version: string;
    baseUrl: string;
    corsEnabled: boolean;
    corsOrigins: string[];
    rateLimitEnabled: boolean;
    rateLimitWindow: number;
    rateLimitMax: number;
    authenticationRequired: boolean;
    apiKeyRequired: boolean;
    documentationEnabled: boolean;
  };
}

// Dados mock extraídos do componente
const mockSystemConfig: SystemConfigData = {
  general: {
    appName: 'Omni Keywords Finder',
    appVersion: '1.0.0',
    environment: 'production',
    timezone: 'America/Sao_Paulo',
    language: 'pt-BR',
    dateFormat: 'DD/MM/YYYY',
    timeFormat: 'HH:mm:ss',
    currency: 'BRL',
    maxFileSize: 10485760,
    sessionTimeout: 3600
  },
  security: {
    passwordMinLength: 8,
    passwordRequireUppercase: true,
    passwordRequireLowercase: true,
    passwordRequireNumbers: true,
    passwordRequireSymbols: true,
    maxLoginAttempts: 5,
    lockoutDuration: 900,
    twoFactorEnabled: true,
    sslRequired: true,
    corsOrigins: ['https://app.example.com', 'https://admin.example.com'],
    apiRateLimit: 1000
  },
  performance: {
    cacheEnabled: true,
    cacheTTL: 3600,
    compressionEnabled: true,
    gzipLevel: 6,
    maxConcurrentRequests: 100,
    requestTimeout: 30000,
    databasePoolSize: 10,
    backgroundJobWorkers: 5,
    memoryLimit: 512,
    cpuLimit: 2
  },
  database: {
    type: 'postgresql',
    host: 'localhost',
    port: 5432,
    name: 'omni_keywords_finder',
    username: 'postgres',
    password: 'secure_password_123',
    sslEnabled: true,
    connectionPool: 10,
    timeout: 30000,
    maxConnections: 100,
    migrationsEnabled: true
  },
  api: {
    version: 'v1',
    baseUrl: 'https://api.example.com',
    corsEnabled: true,
    corsOrigins: ['https://app.example.com'],
    rateLimitEnabled: true,
    rateLimitWindow: 60000,
    rateLimitMax: 1000,
    authenticationRequired: true,
    apiKeyRequired: true,
    documentationEnabled: true
  }
};

// Funções utilitárias extraídas do componente
const validateConfig = (config: SystemConfigData): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  // Validações gerais
  if (!config.general.appName?.trim()) {
    errors.push('Nome da aplicação é obrigatório');
  }

  if (!config.general.appVersion?.trim()) {
    errors.push('Versão da aplicação é obrigatória');
  }

  if (!['development', 'staging', 'production'].includes(config.general.environment)) {
    errors.push('Ambiente deve ser development, staging ou production');
  }

  if (!config.general.timezone?.trim()) {
    errors.push('Fuso horário é obrigatório');
  }

  // Validações de segurança
  if (config.security.passwordMinLength < 6) {
    errors.push('Senha deve ter pelo menos 6 caracteres');
  }

  if (config.security.maxLoginAttempts < 1) {
    errors.push('Máximo de tentativas de login deve ser pelo menos 1');
  }

  if (config.security.lockoutDuration < 60) {
    errors.push('Duração do bloqueio deve ser pelo menos 60 segundos');
  }

  if (config.security.apiRateLimit < 1) {
    errors.push('Rate limit da API deve ser pelo menos 1');
  }

  // Validações de performance
  if (config.performance.cacheTTL < 0) {
    errors.push('TTL do cache deve ser positivo');
  }

  if (config.performance.gzipLevel < 1 || config.performance.gzipLevel > 9) {
    errors.push('Nível de compressão gzip deve estar entre 1 e 9');
  }

  if (config.performance.maxConcurrentRequests < 1) {
    errors.push('Máximo de requisições concorrentes deve ser pelo menos 1');
  }

  if (config.performance.requestTimeout < 1000) {
    errors.push('Timeout da requisição deve ser pelo menos 1000ms');
  }

  if (config.performance.databasePoolSize < 1) {
    errors.push('Tamanho do pool de conexões deve ser pelo menos 1');
  }

  if (config.performance.backgroundJobWorkers < 1) {
    errors.push('Número de workers deve ser pelo menos 1');
  }

  if (config.performance.memoryLimit < 64) {
    errors.push('Limite de memória deve ser pelo menos 64MB');
  }

  if (config.performance.cpuLimit < 0.1) {
    errors.push('Limite de CPU deve ser pelo menos 0.1');
  }

  // Validações de banco de dados
  if (!['sqlite', 'postgresql', 'mysql', 'mongodb'].includes(config.database.type)) {
    errors.push('Tipo de banco de dados deve ser sqlite, postgresql, mysql ou mongodb');
  }

  if (!config.database.host?.trim()) {
    errors.push('Host do banco de dados é obrigatório');
  }

  if (config.database.port < 1 || config.database.port > 65535) {
    errors.push('Porta do banco de dados deve estar entre 1 e 65535');
  }

  if (!config.database.name?.trim()) {
    errors.push('Nome do banco de dados é obrigatório');
  }

  if (!config.database.username?.trim()) {
    errors.push('Usuário do banco de dados é obrigatório');
  }

  if (config.database.connectionPool < 1) {
    errors.push('Pool de conexões deve ser pelo menos 1');
  }

  if (config.database.timeout < 1000) {
    errors.push('Timeout do banco deve ser pelo menos 1000ms');
  }

  if (config.database.maxConnections < 1) {
    errors.push('Máximo de conexões deve ser pelo menos 1');
  }

  // Validações de API
  if (!config.api.version?.trim()) {
    errors.push('Versão da API é obrigatória');
  }

  if (!config.api.baseUrl?.trim()) {
    errors.push('URL base da API é obrigatória');
  }

  if (!config.api.baseUrl.startsWith('http://') && !config.api.baseUrl.startsWith('https://')) {
    errors.push('URL base da API deve começar com http:// ou https://');
  }

  if (config.api.rateLimitWindow < 1000) {
    errors.push('Janela de rate limit deve ser pelo menos 1000ms');
  }

  if (config.api.rateLimitMax < 1) {
    errors.push('Máximo de rate limit deve ser pelo menos 1');
  }

  return {
    valid: errors.length === 0,
    errors
  };
};

const updateConfigPath = (config: SystemConfigData, path: string, value: any): SystemConfigData => {
  const newConfig = JSON.parse(JSON.stringify(config));
  const keys = path.split('.');
  let current = newConfig;

  for (let i = 0; i < keys.length - 1; i++) {
    current = current[keys[i]];
  }

  current[keys[keys.length - 1]] = value;
  return newConfig;
};

const getConfigValue = (config: SystemConfigData, path: string): any => {
  const keys = path.split('.');
  let current = config;

  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return undefined;
    }
  }

  return current;
};

const calculateConfigScore = (config: SystemConfigData): number => {
  let score = 100;

  // Penalizar configurações inseguras
  if (config.security.passwordMinLength < 8) score -= 10;
  if (!config.security.twoFactorEnabled) score -= 5;
  if (!config.security.sslRequired) score -= 10;
  if (config.security.maxLoginAttempts > 10) score -= 5;

  // Penalizar configurações de performance inadequadas
  if (!config.performance.cacheEnabled) score -= 5;
  if (config.performance.cacheTTL < 300) score -= 5;
  if (!config.performance.compressionEnabled) score -= 5;
  if (config.performance.maxConcurrentRequests < 50) score -= 5;

  // Penalizar configurações de banco inadequadas
  if (config.database.connectionPool < 5) score -= 5;
  if (config.database.timeout < 5000) score -= 5;
  if (!config.database.sslEnabled) score -= 10;

  // Penalizar configurações de API inadequadas
  if (!config.api.corsEnabled) score -= 5;
  if (!config.api.rateLimitEnabled) score -= 10;
  if (config.api.rateLimitMax > 10000) score -= 5;
  if (!config.api.authenticationRequired) score -= 10;

  return Math.max(0, score);
};

const getConfigRecommendations = (config: SystemConfigData): string[] => {
  const recommendations: string[] = [];

  if (config.security.passwordMinLength < 12) {
    recommendations.push('Aumentar comprimento mínimo da senha para 12 caracteres');
  }

  if (!config.security.twoFactorEnabled) {
    recommendations.push('Habilitar autenticação de dois fatores');
  }

  if (!config.security.sslRequired) {
    recommendations.push('Requerer SSL para todas as conexões');
  }

  if (config.performance.cacheTTL < 1800) {
    recommendations.push('Aumentar TTL do cache para pelo menos 30 minutos');
  }

  if (config.performance.maxConcurrentRequests < 100) {
    recommendations.push('Aumentar limite de requisições concorrentes');
  }

  if (!config.database.sslEnabled) {
    recommendations.push('Habilitar SSL para conexões de banco de dados');
  }

  if (config.database.connectionPool < 10) {
    recommendations.push('Aumentar tamanho do pool de conexões');
  }

  if (!config.api.rateLimitEnabled) {
    recommendations.push('Habilitar rate limiting na API');
  }

  if (!config.api.authenticationRequired) {
    recommendations.push('Requerer autenticação para todas as APIs');
  }

  return recommendations;
};

const validateEnvironmentConfig = (config: SystemConfigData): { valid: boolean; warnings: string[] } => {
  const warnings: string[] = [];

  if (config.general.environment === 'production') {
    if (config.general.appVersion.includes('dev') || config.general.appVersion.includes('alpha') || config.general.appVersion.includes('beta')) {
      warnings.push('Versão de produção não deve conter dev, alpha ou beta');
    }

    if (!config.security.sslRequired) {
      warnings.push('SSL deve ser obrigatório em produção');
    }

    if (!config.security.twoFactorEnabled) {
      warnings.push('2FA deve ser habilitado em produção');
    }

    if (config.performance.cacheTTL < 3600) {
      warnings.push('Cache TTL deve ser pelo menos 1 hora em produção');
    }

    if (config.database.type === 'sqlite') {
      warnings.push('SQLite não é recomendado para produção');
    }

    if (!config.database.sslEnabled) {
      warnings.push('SSL deve ser habilitado para banco de dados em produção');
    }
  }

  return {
    valid: warnings.length === 0,
    warnings
  };
};

describe('SystemConfig - Configurações do Sistema', () => {
  
  describe('Interface SystemConfigData - Validação de Estrutura', () => {
    
    test('deve validar estrutura do SystemConfigData', () => {
      const config: SystemConfigData = mockSystemConfig;

      expect(config).toHaveProperty('general');
      expect(config).toHaveProperty('security');
      expect(config).toHaveProperty('performance');
      expect(config).toHaveProperty('database');
      expect(config).toHaveProperty('api');
      expect(typeof config.general.appName).toBe('string');
      expect(typeof config.security.passwordMinLength).toBe('number');
      expect(typeof config.performance.cacheEnabled).toBe('boolean');
      expect(typeof config.database.type).toBe('string');
      expect(typeof config.api.version).toBe('string');
    });

    test('deve validar estrutura das configurações gerais', () => {
      const general = mockSystemConfig.general;

      expect(general).toHaveProperty('appName');
      expect(general).toHaveProperty('appVersion');
      expect(general).toHaveProperty('environment');
      expect(general).toHaveProperty('timezone');
      expect(general).toHaveProperty('language');
      expect(general).toHaveProperty('dateFormat');
      expect(general).toHaveProperty('timeFormat');
      expect(general).toHaveProperty('currency');
      expect(general).toHaveProperty('maxFileSize');
      expect(general).toHaveProperty('sessionTimeout');
      expect(typeof general.appName).toBe('string');
      expect(typeof general.appVersion).toBe('string');
      expect(typeof general.maxFileSize).toBe('number');
      expect(typeof general.sessionTimeout).toBe('number');
    });

    test('deve validar estrutura das configurações de segurança', () => {
      const security = mockSystemConfig.security;

      expect(security).toHaveProperty('passwordMinLength');
      expect(security).toHaveProperty('passwordRequireUppercase');
      expect(security).toHaveProperty('passwordRequireLowercase');
      expect(security).toHaveProperty('passwordRequireNumbers');
      expect(security).toHaveProperty('passwordRequireSymbols');
      expect(security).toHaveProperty('maxLoginAttempts');
      expect(security).toHaveProperty('lockoutDuration');
      expect(security).toHaveProperty('twoFactorEnabled');
      expect(security).toHaveProperty('sslRequired');
      expect(security).toHaveProperty('corsOrigins');
      expect(security).toHaveProperty('apiRateLimit');
      expect(typeof security.passwordMinLength).toBe('number');
      expect(typeof security.twoFactorEnabled).toBe('boolean');
      expect(Array.isArray(security.corsOrigins)).toBe(true);
    });

    test('deve validar estrutura das configurações de performance', () => {
      const performance = mockSystemConfig.performance;

      expect(performance).toHaveProperty('cacheEnabled');
      expect(performance).toHaveProperty('cacheTTL');
      expect(performance).toHaveProperty('compressionEnabled');
      expect(performance).toHaveProperty('gzipLevel');
      expect(performance).toHaveProperty('maxConcurrentRequests');
      expect(performance).toHaveProperty('requestTimeout');
      expect(performance).toHaveProperty('databasePoolSize');
      expect(performance).toHaveProperty('backgroundJobWorkers');
      expect(performance).toHaveProperty('memoryLimit');
      expect(performance).toHaveProperty('cpuLimit');
      expect(typeof performance.cacheEnabled).toBe('boolean');
      expect(typeof performance.cacheTTL).toBe('number');
      expect(typeof performance.gzipLevel).toBe('number');
    });

    test('deve validar estrutura das configurações de banco de dados', () => {
      const database = mockSystemConfig.database;

      expect(database).toHaveProperty('type');
      expect(database).toHaveProperty('host');
      expect(database).toHaveProperty('port');
      expect(database).toHaveProperty('name');
      expect(database).toHaveProperty('username');
      expect(database).toHaveProperty('password');
      expect(database).toHaveProperty('sslEnabled');
      expect(database).toHaveProperty('connectionPool');
      expect(database).toHaveProperty('timeout');
      expect(database).toHaveProperty('maxConnections');
      expect(database).toHaveProperty('migrationsEnabled');
      expect(typeof database.type).toBe('string');
      expect(typeof database.host).toBe('string');
      expect(typeof database.port).toBe('number');
      expect(typeof database.sslEnabled).toBe('boolean');
    });

    test('deve validar estrutura das configurações de API', () => {
      const api = mockSystemConfig.api;

      expect(api).toHaveProperty('version');
      expect(api).toHaveProperty('baseUrl');
      expect(api).toHaveProperty('corsEnabled');
      expect(api).toHaveProperty('corsOrigins');
      expect(api).toHaveProperty('rateLimitEnabled');
      expect(api).toHaveProperty('rateLimitWindow');
      expect(api).toHaveProperty('rateLimitMax');
      expect(api).toHaveProperty('authenticationRequired');
      expect(api).toHaveProperty('apiKeyRequired');
      expect(api).toHaveProperty('documentationEnabled');
      expect(typeof api.version).toBe('string');
      expect(typeof api.baseUrl).toBe('string');
      expect(typeof api.corsEnabled).toBe('boolean');
      expect(Array.isArray(api.corsOrigins)).toBe(true);
    });
  });

  describe('Validação de Configurações', () => {
    
    test('deve validar configuração válida', () => {
      const result = validateConfig(mockSystemConfig);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('deve rejeitar configuração sem nome da aplicação', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'general.appName', '');
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Nome da aplicação é obrigatório');
    });

    test('deve rejeitar configuração sem versão', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'general.appVersion', '');
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Versão da aplicação é obrigatória');
    });

    test('deve rejeitar ambiente inválido', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'general.environment', 'invalid');
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Ambiente deve ser development, staging ou production');
    });

    test('deve rejeitar senha muito curta', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'security.passwordMinLength', 4);
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Senha deve ter pelo menos 6 caracteres');
    });

    test('deve rejeitar tentativas de login inválidas', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'security.maxLoginAttempts', 0);
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Máximo de tentativas de login deve ser pelo menos 1');
    });

    test('deve rejeitar nível de compressão inválido', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'performance.gzipLevel', 10);
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Nível de compressão gzip deve estar entre 1 e 9');
    });

    test('deve rejeitar tipo de banco inválido', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'database.type', 'invalid');
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Tipo de banco de dados deve ser sqlite, postgresql, mysql ou mongodb');
    });

    test('deve rejeitar URL base inválida', () => {
      const invalidConfig = updateConfigPath(mockSystemConfig, 'api.baseUrl', 'invalid-url');
      const result = validateConfig(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('URL base da API deve começar com http:// ou https://');
    });
  });

  describe('Atualização de Configurações', () => {
    
    test('deve atualizar configuração por caminho', () => {
      const updatedConfig = updateConfigPath(mockSystemConfig, 'general.appName', 'Novo Nome');
      const value = getConfigValue(updatedConfig, 'general.appName');

      expect(value).toBe('Novo Nome');
    });

    test('deve atualizar configuração aninhada', () => {
      const updatedConfig = updateConfigPath(mockSystemConfig, 'security.passwordMinLength', 12);
      const value = getConfigValue(updatedConfig, 'security.passwordMinLength');

      expect(value).toBe(12);
    });

    test('deve obter valor de configuração por caminho', () => {
      const value = getConfigValue(mockSystemConfig, 'general.appName');
      expect(value).toBe('Omni Keywords Finder');
    });

    test('deve retornar undefined para caminho inexistente', () => {
      const value = getConfigValue(mockSystemConfig, 'general.inexistente');
      expect(value).toBeUndefined();
    });

    test('deve manter outras configurações inalteradas', () => {
      const updatedConfig = updateConfigPath(mockSystemConfig, 'general.appName', 'Novo Nome');
      const originalValue = getConfigValue(mockSystemConfig, 'security.passwordMinLength');
      const updatedValue = getConfigValue(updatedConfig, 'security.passwordMinLength');

      expect(updatedValue).toBe(originalValue);
    });
  });

  describe('Cálculo de Score de Configuração', () => {
    
    test('deve calcular score para configuração padrão', () => {
      const score = calculateConfigScore(mockSystemConfig);

      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });

    test('deve penalizar configurações inseguras', () => {
      const insecureConfig = updateConfigPath(mockSystemConfig, 'security.passwordMinLength', 6);
      const score = calculateConfigScore(insecureConfig);

      expect(score).toBeLessThan(100);
    });

    test('deve penalizar falta de 2FA', () => {
      const no2FAConfig = updateConfigPath(mockSystemConfig, 'security.twoFactorEnabled', false);
      const score = calculateConfigScore(no2FAConfig);

      expect(score).toBeLessThan(100);
    });

    test('deve penalizar falta de SSL', () => {
      const noSSLConfig = updateConfigPath(mockSystemConfig, 'security.sslRequired', false);
      const score = calculateConfigScore(noSSLConfig);

      expect(score).toBeLessThan(100);
    });

    test('deve penalizar configurações de performance inadequadas', () => {
      const poorPerformanceConfig = updateConfigPath(mockSystemConfig, 'performance.cacheEnabled', false);
      const score = calculateConfigScore(poorPerformanceConfig);

      expect(score).toBeLessThan(100);
    });

    test('deve penalizar configurações de banco inadequadas', () => {
      const poorDBConfig = updateConfigPath(mockSystemConfig, 'database.sslEnabled', false);
      const score = calculateConfigScore(poorDBConfig);

      expect(score).toBeLessThan(100);
    });
  });

  describe('Recomendações de Configuração', () => {
    
    test('deve gerar recomendações para configuração padrão', () => {
      const recommendations = getConfigRecommendations(mockSystemConfig);

      expect(Array.isArray(recommendations)).toBe(true);
    });

    test('deve recomendar senha mais longa', () => {
      const shortPasswordConfig = updateConfigPath(mockSystemConfig, 'security.passwordMinLength', 8);
      const recommendations = getConfigRecommendations(shortPasswordConfig);

      expect(recommendations).toContain('Aumentar comprimento mínimo da senha para 12 caracteres');
    });

    test('deve recomendar habilitar 2FA', () => {
      const no2FAConfig = updateConfigPath(mockSystemConfig, 'security.twoFactorEnabled', false);
      const recommendations = getConfigRecommendations(no2FAConfig);

      expect(recommendations).toContain('Habilitar autenticação de dois fatores');
    });

    test('deve recomendar habilitar SSL', () => {
      const noSSLConfig = updateConfigPath(mockSystemConfig, 'security.sslRequired', false);
      const recommendations = getConfigRecommendations(noSSLConfig);

      expect(recommendations).toContain('Requerer SSL para todas as conexões');
    });

    test('deve recomendar aumentar TTL do cache', () => {
      const shortCacheConfig = updateConfigPath(mockSystemConfig, 'performance.cacheTTL', 300);
      const recommendations = getConfigRecommendations(shortCacheConfig);

      expect(recommendations).toContain('Aumentar TTL do cache para pelo menos 30 minutos');
    });

    test('deve recomendar habilitar rate limiting', () => {
      const noRateLimitConfig = updateConfigPath(mockSystemConfig, 'api.rateLimitEnabled', false);
      const recommendations = getConfigRecommendations(noRateLimitConfig);

      expect(recommendations).toContain('Habilitar rate limiting na API');
    });
  });

  describe('Validação de Ambiente', () => {
    
    test('deve validar configuração de produção', () => {
      const productionConfig = updateConfigPath(mockSystemConfig, 'general.environment', 'production');
      const result = validateEnvironmentConfig(productionConfig);

      expect(result.valid).toBe(false); // Deve ter warnings
      expect(result.warnings.length).toBeGreaterThan(0);
    });

    test('deve alertar sobre versão de desenvolvimento em produção', () => {
      const productionConfig = updateConfigPath(mockSystemConfig, 'general.appVersion', '1.0.0-dev');
      const result = validateEnvironmentConfig(productionConfig);

      expect(result.warnings).toContain('Versão de produção não deve conter dev, alpha ou beta');
    });

    test('deve alertar sobre falta de SSL em produção', () => {
      const productionConfig = updateConfigPath(mockSystemConfig, 'security.sslRequired', false);
      const result = validateEnvironmentConfig(productionConfig);

      expect(result.warnings).toContain('SSL deve ser obrigatório em produção');
    });

    test('deve alertar sobre SQLite em produção', () => {
      const productionConfig = updateConfigPath(mockSystemConfig, 'database.type', 'sqlite');
      const result = validateEnvironmentConfig(productionConfig);

      expect(result.warnings).toContain('SQLite não é recomendado para produção');
    });

    test('deve validar configuração de desenvolvimento sem warnings', () => {
      const devConfig = updateConfigPath(mockSystemConfig, 'general.environment', 'development');
      const result = validateEnvironmentConfig(devConfig);

      expect(result.valid).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });
  });

  describe('Validação de Tipos de Dados', () => {
    
    test('deve validar tipos de ambiente', () => {
      const validEnvironments = ['development', 'staging', 'production'];
      
      validEnvironments.forEach(env => {
        const config = updateConfigPath(mockSystemConfig, 'general.environment', env);
        const result = validateConfig(config);
        expect(result.valid).toBe(true);
      });
    });

    test('deve validar tipos de banco de dados', () => {
      const validDBTypes = ['sqlite', 'postgresql', 'mysql', 'mongodb'];
      
      validDBTypes.forEach(type => {
        const config = updateConfigPath(mockSystemConfig, 'database.type', type);
        const result = validateConfig(config);
        expect(result.valid).toBe(true);
      });
    });

    test('deve validar níveis de compressão gzip', () => {
      for (let level = 1; level <= 9; level++) {
        const config = updateConfigPath(mockSystemConfig, 'performance.gzipLevel', level);
        const result = validateConfig(config);
        expect(result.valid).toBe(true);
      }
    });

    test('deve validar portas de banco de dados', () => {
      const validPorts = [3306, 5432, 27017, 6379];
      
      validPorts.forEach(port => {
        const config = updateConfigPath(mockSystemConfig, 'database.port', port);
        const result = validateConfig(config);
        expect(result.valid).toBe(true);
      });
    });
  });

  describe('Análise de Segurança', () => {
    
    test('deve identificar configurações de segurança fracas', () => {
      const weakConfig = updateConfigPath(mockSystemConfig, 'security.passwordMinLength', 4);
      const result = validateConfig(weakConfig);

      expect(result.valid).toBe(false);
      expect(result.errors.some(error => error.includes('senha'))).toBe(true);
    });

    test('deve identificar falta de autenticação na API', () => {
      const noAuthConfig = updateConfigPath(mockSystemConfig, 'api.authenticationRequired', false);
      const recommendations = getConfigRecommendations(noAuthConfig);

      expect(recommendations).toContain('Requerer autenticação para todas as APIs');
    });

    test('deve identificar falta de rate limiting', () => {
      const noRateLimitConfig = updateConfigPath(mockSystemConfig, 'api.rateLimitEnabled', false);
      const recommendations = getConfigRecommendations(noRateLimitConfig);

      expect(recommendations).toContain('Habilitar rate limiting na API');
    });

    test('deve calcular score de segurança', () => {
      const secureConfig = updateConfigPath(mockSystemConfig, 'security.passwordMinLength', 12);
      const score = calculateConfigScore(secureConfig);

      expect(score).toBeGreaterThanOrEqual(0);
    });
  });
}); 