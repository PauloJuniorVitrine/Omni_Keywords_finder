/**
 * Configuração centralizada de API
 * 
 * Prompt: FIXTYPE-001 - Sincronização de Endpoints
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * @author Paulo Júnior
 * @description Configuração centralizada para padronizar endpoints entre frontend e backend
 */

// Configurações de ambiente
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api';
const API_VERSION = 'v1';

// Configuração completa da API
export const API_CONFIG = {
  baseUrl: API_BASE_URL,
  prefix: API_PREFIX,
  version: API_VERSION,
  timeout: 30000, // 30 segundos
  retryAttempts: 3,
  retryDelay: 1000, // 1 segundo
} as const;

// Endpoints padronizados
export const API_ENDPOINTS = {
  // Nichos
  nichos: {
    list: `${API_PREFIX}/nichos`,
    create: `${API_PREFIX}/nichos`,
    update: (id: number) => `${API_PREFIX}/nichos/${id}`,
    delete: (id: number) => `${API_PREFIX}/nichos/${id}`,
    get: (id: number) => `${API_PREFIX}/nichos/${id}`,
  },
  
  // Categorias
  categorias: {
    list: (nichoId?: number) => 
      nichoId ? `${API_PREFIX}/nichos/${nichoId}/categorias` : `${API_PREFIX}/categorias`,
    create: (nichoId?: number) => 
      nichoId ? `${API_PREFIX}/nichos/${nichoId}/categorias` : `${API_PREFIX}/categorias`,
    update: (id: number) => `${API_PREFIX}/categorias/${id}`,
    delete: (id: number) => `${API_PREFIX}/categorias/${id}`,
    get: (id: number) => `${API_PREFIX}/categorias/${id}`,
  },
  
  // Prompts
  prompts: {
    base: {
      list: (categoriaId?: number) => 
        categoriaId ? `${API_PREFIX}/categorias/${categoriaId}/prompts-base` : `${API_PREFIX}/prompts-base`,
      create: `${API_PREFIX}/prompts-base`,
      update: (id: number) => `${API_PREFIX}/prompts-base/${id}`,
      delete: (id: number) => `${API_PREFIX}/prompts-base/${id}`,
      get: (id: number) => `${API_PREFIX}/prompts-base/${id}`,
      upload: `${API_PREFIX}/prompts-base/upload`,
    },
    preenchidos: {
      list: `${API_PREFIX}/prompts-preenchidos`,
      create: `${API_PREFIX}/prompts-preenchidos`,
      update: (id: number) => `${API_PREFIX}/prompts-preenchidos/${id}`,
      delete: (id: number) => `${API_PREFIX}/prompts-preenchidos/${id}`,
      get: (id: number) => `${API_PREFIX}/prompts-preenchidos/${id}`,
      download: (id: number) => `${API_PREFIX}/prompts-preenchidos/${id}/download`,
    },
  },
  
  // Dados Coletados
  dadosColetados: {
    list: (categoriaId?: number) => 
      categoriaId ? `${API_PREFIX}/categorias/${categoriaId}/dados-coletados` : `${API_PREFIX}/dados-coletados`,
    create: `${API_PREFIX}/dados-coletados`,
    update: (id: number) => `${API_PREFIX}/dados-coletados/${id}`,
    delete: (id: number) => `${API_PREFIX}/dados-coletados/${id}`,
    get: (id: number) => `${API_PREFIX}/dados-coletados/${id}`,
  },
  
  // Estatísticas
  stats: {
    geral: `${API_PREFIX}/stats`,
    nicho: (nichoId: number) => `${API_PREFIX}/stats/nichos/${nichoId}`,
    categoria: (categoriaId: number) => `${API_PREFIX}/stats/categorias/${categoriaId}`,
  },
  
  // Validação
  validacao: {
    prompt: `${API_PREFIX}/validacao/prompt`,
    lacunas: (categoriaId: number) => `${API_PREFIX}/validacao/lacunas/${categoriaId}`,
  },
  
  // Autenticação
  auth: {
    login: `${API_PREFIX}/auth/login`,
    logout: `${API_PREFIX}/auth/logout`,
    refresh: `${API_PREFIX}/auth/refresh`,
    oauth2: {
      login: (provider: string) => `${API_PREFIX}/auth/oauth2/login/${provider}`,
      callback: (provider: string) => `${API_PREFIX}/auth/oauth2/callback/${provider}`,
    },
  },
  
  // Credenciais
  credentials: {
    validate: `${API_PREFIX}/credentials/validate`,
    list: `${API_PREFIX}/credentials`,
    create: `${API_PREFIX}/credentials`,
    update: (id: number) => `${API_PREFIX}/credentials/${id}`,
    delete: (id: number) => `${API_PREFIX}/credentials/${id}`,
  },
  
  // Governança
  governanca: {
    logs: `${API_PREFIX}/governanca/logs`,
    regras: {
      atual: `${API_PREFIX}/governanca/regras/atual`,
      upload: `${API_PREFIX}/governanca/regras/upload`,
      editar: `${API_PREFIX}/governanca/regras/editar`,
    },
  },
  
  // Processamento
  processamento: {
    keywords: `${API_PREFIX}/processar_keywords`,
    exportar: `${API_PREFIX}/exportar_keywords`,
  },
  
  // Documentação
  docs: {
    openapi: `${API_PREFIX}/docs/openapi.json`,
    swagger: `${API_PREFIX}/docs/swagger`,
    typescript: `${API_PREFIX}/docs/typescript`,
  },
  
  // Health
  health: `${API_PREFIX}/health`,
} as const;

// Headers padrão
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
} as const;

// Função para obter headers com autenticação
export const getAuthHeaders = (token?: string): Record<string, string> => {
  const headers = { ...DEFAULT_HEADERS };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// Função para construir URL completa
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseUrl}${endpoint}`;
};

// Função para obter token do localStorage
export const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

// Função para salvar token no localStorage
export const setAuthToken = (token: string): void => {
  localStorage.setItem('authToken', token);
};

// Função para remover token do localStorage
export const removeAuthToken = (): void => {
  localStorage.removeItem('authToken');
};

// Configuração de retry
export const RETRY_CONFIG = {
  attempts: API_CONFIG.retryAttempts,
  delay: API_CONFIG.retryDelay,
  backoff: 'exponential' as const,
} as const;

// Tipos de erro da API
export enum API_ERROR_TYPES {
  NETWORK_ERROR = 'NETWORK_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

// Interface para erros da API
export interface APIError {
  type: API_ERROR_TYPES;
  message: string;
  status?: number;
  details?: Record<string, any>;
  timestamp: string;
}

// Função para criar erro da API
export const createAPIError = (
  type: API_ERROR_TYPES,
  message: string,
  status?: number,
  details?: Record<string, any>
): APIError => ({
  type,
  message,
  status,
  details,
  timestamp: new Date().toISOString(),
});

// Configuração de cache
export const CACHE_CONFIG = {
  defaultTTL: 5 * 60 * 1000, // 5 minutos
  maxSize: 100, // máximo 100 itens
  cleanupInterval: 60 * 1000, // limpeza a cada 1 minuto
} as const;

export default API_CONFIG; 