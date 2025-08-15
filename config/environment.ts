/**
 * Configuração de Variáveis de Ambiente
 * 
 * Prompt: Implementação de itens de criticidade baixa - 11.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { z } from 'zod';

// Schema de validação para variáveis de ambiente
const EnvironmentSchema = z.object({
  // API Configuration
  API_BASE_URL: z.string().url(),
  API_TIMEOUT: z.string().transform(Number).pipe(z.number().min(1000).max(30000)),
  API_RETRY_ATTEMPTS: z.string().transform(Number).pipe(z.number().min(1).max(10)),
  
  // Authentication
  AUTH_TOKEN_KEY: z.string().min(1),
  AUTH_REFRESH_TOKEN_KEY: z.string().min(1),
  AUTH_TOKEN_EXPIRY: z.string().transform(Number).pipe(z.number().min(300).max(86400)),
  
  // WebSocket
  WS_URL: z.string().url().optional(),
  WS_RECONNECT_INTERVAL: z.string().transform(Number).pipe(z.number().min(1000).max(30000)).optional(),
  
  // Logging & Monitoring
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']),
  ENABLE_TELEMETRY: z.string().transform(val => val === 'true'),
  ENABLE_ANALYTICS: z.string().transform(val => val === 'true'),
  
  // Performance
  CACHE_TTL: z.string().transform(Number).pipe(z.number().min(60).max(3600)),
  MAX_CONCURRENT_REQUESTS: z.string().transform(Number).pipe(z.number().min(1).max(50)),
  
  // Development
  NODE_ENV: z.enum(['development', 'staging', 'production']),
  ENABLE_DEBUG_MODE: z.string().transform(val => val === 'true'),
  
  // External Services
  SENTRY_DSN: z.string().url().optional(),
  ANALYTICS_ID: z.string().optional(),
  
  // Feature Flags
  ENABLE_OFFLINE_MODE: z.string().transform(val => val === 'true'),
  ENABLE_BACKGROUND_SYNC: z.string().transform(val => val === 'true'),
  ENABLE_OPTIMISTIC_UPDATES: z.string().transform(val => val === 'true'),
});

// Tipo inferido do schema
export type Environment = z.infer<typeof EnvironmentSchema>;

// Valores padrão para desenvolvimento
const defaultValues: Partial<Environment> = {
  API_BASE_URL: 'http://localhost:3001/api',
  API_TIMEOUT: 10000,
  API_RETRY_ATTEMPTS: 3,
  AUTH_TOKEN_KEY: 'auth_token',
  AUTH_REFRESH_TOKEN_KEY: 'refresh_token',
  AUTH_TOKEN_EXPIRY: 3600,
  LOG_LEVEL: 'info',
  ENABLE_TELEMETRY: false,
  ENABLE_ANALYTICS: false,
  CACHE_TTL: 300,
  MAX_CONCURRENT_REQUESTS: 10,
  NODE_ENV: 'development',
  ENABLE_DEBUG_MODE: true,
  ENABLE_OFFLINE_MODE: false,
  ENABLE_BACKGROUND_SYNC: false,
  ENABLE_OPTIMISTIC_UPDATES: true,
};

/**
 * Carrega e valida variáveis de ambiente
 */
export function loadEnvironment(): Environment {
  try {
    // Coleta variáveis do processo
    const envVars = {
      API_BASE_URL: process.env.API_BASE_URL,
      API_TIMEOUT: process.env.API_TIMEOUT,
      API_RETRY_ATTEMPTS: process.env.API_RETRY_ATTEMPTS,
      AUTH_TOKEN_KEY: process.env.AUTH_TOKEN_KEY,
      AUTH_REFRESH_TOKEN_KEY: process.env.AUTH_REFRESH_TOKEN_KEY,
      AUTH_TOKEN_EXPIRY: process.env.AUTH_TOKEN_EXPIRY,
      WS_URL: process.env.WS_URL,
      WS_RECONNECT_INTERVAL: process.env.WS_RECONNECT_INTERVAL,
      LOG_LEVEL: process.env.LOG_LEVEL,
      ENABLE_TELEMETRY: process.env.ENABLE_TELEMETRY,
      ENABLE_ANALYTICS: process.env.ENABLE_ANALYTICS,
      CACHE_TTL: process.env.CACHE_TTL,
      MAX_CONCURRENT_REQUESTS: process.env.MAX_CONCURRENT_REQUESTS,
      NODE_ENV: process.env.NODE_ENV,
      ENABLE_DEBUG_MODE: process.env.ENABLE_DEBUG_MODE,
      SENTRY_DSN: process.env.SENTRY_DSN,
      ANALYTICS_ID: process.env.ANALYTICS_ID,
      ENABLE_OFFLINE_MODE: process.env.ENABLE_OFFLINE_MODE,
      ENABLE_BACKGROUND_SYNC: process.env.ENABLE_BACKGROUND_SYNC,
      ENABLE_OPTIMISTIC_UPDATES: process.env.ENABLE_OPTIMISTIC_UPDATES,
    };

    // Combina com valores padrão
    const combinedEnv = { ...defaultValues, ...envVars };

    // Remove valores undefined
    const cleanEnv = Object.fromEntries(
      Object.entries(combinedEnv).filter(([_, value]) => value !== undefined)
    );

    // Valida usando o schema
    const validatedEnv = EnvironmentSchema.parse(cleanEnv);

    console.log('[ENVIRONMENT] Configuração carregada com sucesso');
    return validatedEnv;
  } catch (error) {
    console.error('[ENVIRONMENT] Erro ao carregar configuração:', error);
    throw new Error(`Falha na validação das variáveis de ambiente: ${error}`);
  }
}

// Instância singleton da configuração
export const env = loadEnvironment();

/**
 * Utilitário para verificar se estamos em produção
 */
export const isProduction = env.NODE_ENV === 'production';

/**
 * Utilitário para verificar se debug está habilitado
 */
export const isDebugEnabled = env.ENABLE_DEBUG_MODE && !isProduction;

/**
 * Utilitário para obter configuração de API
 */
export const getApiConfig = () => ({
  baseUrl: env.API_BASE_URL,
  timeout: env.API_TIMEOUT,
  retryAttempts: env.API_RETRY_ATTEMPTS,
  maxConcurrent: env.MAX_CONCURRENT_REQUESTS,
});

/**
 * Utilitário para obter configuração de autenticação
 */
export const getAuthConfig = () => ({
  tokenKey: env.AUTH_TOKEN_KEY,
  refreshTokenKey: env.AUTH_REFRESH_TOKEN_KEY,
  tokenExpiry: env.AUTH_TOKEN_EXPIRY,
}); 