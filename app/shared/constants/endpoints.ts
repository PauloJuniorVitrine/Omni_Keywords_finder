/**
 * @fileoverview Constantes de endpoints compartilhadas backend-frontend
 * @prompt COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md
 * @ruleset enterprise_control_layer.yaml
 * @execution 2025-01-27T15:30:00Z
 * @tracing_id COMM_CHECKLIST_20250127_001
 */

// ============================================================================
// CONFIGURAÇÕES BASE
// ============================================================================

export const API_VERSION = 'v1';
export const API_BASE_PATH = `/api/${API_VERSION}`;

// ============================================================================
// ENDPOINTS DE AUTENTICAÇÃO
// ============================================================================

export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE_PATH}/auth/login`,
  LOGOUT: `${API_BASE_PATH}/auth/logout`,
  REFRESH: `${API_BASE_PATH}/auth/refresh`,
  REGISTER: `${API_BASE_PATH}/auth/register`,
  FORGOT_PASSWORD: `${API_BASE_PATH}/auth/forgot-password`,
  RESET_PASSWORD: `${API_BASE_PATH}/auth/reset-password`,
  VERIFY_EMAIL: `${API_BASE_PATH}/auth/verify-email`,
  PROFILE: `${API_BASE_PATH}/auth/profile`,
  UPDATE_PROFILE: `${API_BASE_PATH}/auth/profile`,
  CHANGE_PASSWORD: `${API_BASE_PATH}/auth/change-password`,
} as const;

// ============================================================================
// ENDPOINTS DE KEYWORDS
// ============================================================================

export const KEYWORDS_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/keywords`,
  SEARCH: `${API_BASE_PATH}/keywords/search`,
  ANALYZE: `${API_BASE_PATH}/keywords/analyze`,
  BATCH_ANALYZE: `${API_BASE_PATH}/keywords/batch-analyze`,
  SUGGESTIONS: `${API_BASE_PATH}/keywords/suggestions`,
  RELATED: `${API_BASE_PATH}/keywords/related`,
  TRENDS: `${API_BASE_PATH}/keywords/trends`,
  COMPETITION: `${API_BASE_PATH}/keywords/competition`,
  EXPORT: `${API_BASE_PATH}/keywords/export`,
} as const;

// ============================================================================
// ENDPOINTS DE BLOGS
// ============================================================================

export const BLOGS_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/blogs`,
  ANALYZE: `${API_BASE_PATH}/blogs/analyze`,
  BATCH_ANALYZE: `${API_BASE_PATH}/blogs/batch-analyze`,
  KEYWORDS: `${API_BASE_PATH}/blogs/keywords`,
  CONTENT_GAPS: `${API_BASE_PATH}/blogs/content-gaps`,
  TECHNICAL_ISSUES: `${API_BASE_PATH}/blogs/technical-issues`,
  SEO_SCORE: `${API_BASE_PATH}/blogs/seo-score`,
  COMPETITORS: `${API_BASE_PATH}/blogs/competitors`,
  EXPORT: `${API_BASE_PATH}/blogs/export`,
} as const;

// ============================================================================
// ENDPOINTS DE ANÁLISE
// ============================================================================

export const ANALYSIS_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/analysis`,
  KEYWORD: `${API_BASE_PATH}/analysis/keyword`,
  BLOG: `${API_BASE_PATH}/analysis/blog`,
  COMPETITOR: `${API_BASE_PATH}/analysis/competitor`,
  BATCH: `${API_BASE_PATH}/analysis/batch`,
  STATUS: `${API_BASE_PATH}/analysis/status`,
  CANCEL: `${API_BASE_PATH}/analysis/cancel`,
  RESULTS: `${API_BASE_PATH}/analysis/results`,
  EXPORT: `${API_BASE_PATH}/analysis/export`,
} as const;

// ============================================================================
// ENDPOINTS DE NOTIFICAÇÕES
// ============================================================================

export const NOTIFICATIONS_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/notifications`,
  MARK_READ: `${API_BASE_PATH}/notifications/mark-read`,
  MARK_ALL_READ: `${API_BASE_PATH}/notifications/mark-all-read`,
  DELETE: `${API_BASE_PATH}/notifications/delete`,
  SETTINGS: `${API_BASE_PATH}/notifications/settings`,
  PREFERENCES: `${API_BASE_PATH}/notifications/preferences`,
} as const;

// ============================================================================
// ENDPOINTS DE RELATÓRIOS
// ============================================================================

export const REPORTS_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/reports`,
  KEYWORD_REPORT: `${API_BASE_PATH}/reports/keyword`,
  BLOG_REPORT: `${API_BASE_PATH}/reports/blog`,
  COMPETITOR_REPORT: `${API_BASE_PATH}/reports/competitor`,
  SEO_AUDIT: `${API_BASE_PATH}/reports/seo-audit`,
  CUSTOM: `${API_BASE_PATH}/reports/custom`,
  SCHEDULE: `${API_BASE_PATH}/reports/schedule`,
  EXPORT: `${API_BASE_PATH}/reports/export`,
  TEMPLATES: `${API_BASE_PATH}/reports/templates`,
} as const;

// ============================================================================
// ENDPOINTS DE COLETORES
// ============================================================================

export const COLLECTORS_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/collectors`,
  GSC: `${API_BASE_PATH}/collectors/gsc`,
  SEMRUSH: `${API_BASE_PATH}/collectors/semrush`,
  AHREFS: `${API_BASE_PATH}/collectors/ahrefs`,
  MOZ: `${API_BASE_PATH}/collectors/moz`,
  CUSTOM: `${API_BASE_PATH}/collectors/custom`,
  RUN: `${API_BASE_PATH}/collectors/run`,
  STATUS: `${API_BASE_PATH}/collectors/status`,
  CONFIG: `${API_BASE_PATH}/collectors/config`,
  SCHEDULE: `${API_BASE_PATH}/collectors/schedule`,
} as const;

// ============================================================================
// ENDPOINTS DE CONFIGURAÇÃO
// ============================================================================

export const CONFIG_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/config`,
  API_CONFIG: `${API_BASE_PATH}/config/api`,
  USER_PREFERENCES: `${API_BASE_PATH}/config/preferences`,
  SYSTEM_CONFIG: `${API_BASE_PATH}/config/system`,
  FEATURE_FLAGS: `${API_BASE_PATH}/config/feature-flags`,
  RATE_LIMITS: `${API_BASE_PATH}/config/rate-limits`,
  CACHE_CONFIG: `${API_BASE_PATH}/config/cache`,
} as const;

// ============================================================================
// ENDPOINTS DE TELEMETRIA
// ============================================================================

export const TELEMETRY_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/telemetry`,
  EVENTS: `${API_BASE_PATH}/telemetry/events`,
  METRICS: `${API_BASE_PATH}/telemetry/metrics`,
  PERFORMANCE: `${API_BASE_PATH}/telemetry/performance`,
  ERRORS: `${API_BASE_PATH}/telemetry/errors`,
  SESSION: `${API_BASE_PATH}/telemetry/session`,
} as const;

// ============================================================================
// ENDPOINTS DE AUDITORIA
// ============================================================================

export const AUDIT_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/audit`,
  LOGS: `${API_BASE_PATH}/audit/logs`,
  SYSTEM_LOGS: `${API_BASE_PATH}/audit/system-logs`,
  USER_ACTIONS: `${API_BASE_PATH}/audit/user-actions`,
  SECURITY: `${API_BASE_PATH}/audit/security`,
  EXPORT: `${API_BASE_PATH}/audit/export`,
} as const;

// ============================================================================
// ENDPOINTS DE WEBSOCKET
// ============================================================================

export const WEBSOCKET_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/ws`,
  ANALYSIS_PROGRESS: `${API_BASE_PATH}/ws/analysis-progress`,
  REAL_TIME_NOTIFICATIONS: `${API_BASE_PATH}/ws/notifications`,
  COLLECTOR_UPDATES: `${API_BASE_PATH}/ws/collector-updates`,
  SYSTEM_ALERTS: `${API_BASE_PATH}/ws/system-alerts`,
} as const;

// ============================================================================
// ENDPOINTS DE HEALTH CHECK
// ============================================================================

export const HEALTH_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/health`,
  READY: `${API_BASE_PATH}/health/ready`,
  LIVE: `${API_BASE_PATH}/health/live`,
  DETAILED: `${API_BASE_PATH}/health/detailed`,
  METRICS: `${API_BASE_PATH}/health/metrics`,
} as const;

// ============================================================================
// ENDPOINTS DE UTILITÁRIOS
// ============================================================================

export const UTILS_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/utils`,
  VALIDATE: `${API_BASE_PATH}/utils/validate`,
  SANITIZE: `${API_BASE_PATH}/utils/sanitize`,
  FORMAT: `${API_BASE_PATH}/utils/format`,
  CONVERT: `${API_BASE_PATH}/utils/convert`,
  GENERATE_ID: `${API_BASE_PATH}/utils/generate-id`,
} as const;

// ============================================================================
// ENDPOINTS DE EXPORTAÇÃO
// ============================================================================

export const EXPORT_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/export`,
  KEYWORDS: `${API_BASE_PATH}/export/keywords`,
  BLOGS: `${API_BASE_PATH}/export/blogs`,
  ANALYSIS: `${API_BASE_PATH}/export/analysis`,
  REPORTS: `${API_BASE_PATH}/export/reports`,
  AUDIT: `${API_BASE_PATH}/export/audit`,
  CUSTOM: `${API_BASE_PATH}/export/custom`,
} as const;

// ============================================================================
// ENDPOINTS DE BATCH OPERATIONS
// ============================================================================

export const BATCH_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/batch`,
  KEYWORDS: `${API_BASE_PATH}/batch/keywords`,
  BLOGS: `${API_BASE_PATH}/batch/blogs`,
  ANALYSIS: `${API_BASE_PATH}/batch/analysis`,
  EXPORT: `${API_BASE_PATH}/batch/export`,
  STATUS: `${API_BASE_PATH}/batch/status`,
  CANCEL: `${API_BASE_PATH}/batch/cancel`,
} as const;

// ============================================================================
// ENDPOINTS DE CACHE
// ============================================================================

export const CACHE_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/cache`,
  GET: `${API_BASE_PATH}/cache/get`,
  SET: `${API_BASE_PATH}/cache/set`,
  DELETE: `${API_BASE_PATH}/cache/delete`,
  CLEAR: `${API_BASE_PATH}/cache/clear`,
  STATS: `${API_BASE_PATH}/cache/stats`,
  KEYS: `${API_BASE_PATH}/cache/keys`,
} as const;

// ============================================================================
// ENDPOINTS DE RATE LIMITING
// ============================================================================

export const RATE_LIMIT_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/rate-limit`,
  INFO: `${API_BASE_PATH}/rate-limit/info`,
  RESET: `${API_BASE_PATH}/rate-limit/reset`,
  WHITELIST: `${API_BASE_PATH}/rate-limit/whitelist`,
  BLACKLIST: `${API_BASE_PATH}/rate-limit/blacklist`,
} as const;

// ============================================================================
// ENDPOINTS DE VERSÃO E COMPATIBILIDADE
// ============================================================================

export const VERSION_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/version`,
  INFO: `${API_BASE_PATH}/version/info`,
  COMPATIBILITY: `${API_BASE_PATH}/version/compatibility`,
  CHANGELOG: `${API_BASE_PATH}/version/changelog`,
  DEPRECATED: `${API_BASE_PATH}/version/deprecated`,
} as const;

// ============================================================================
// ENDPOINTS DE DESENVOLVIMENTO
// ============================================================================

export const DEV_ENDPOINTS = {
  BASE: `${API_BASE_PATH}/dev`,
  API_EXPLORER: `${API_BASE_PATH}/dev/api-explorer`,
  REQUEST_LOGGER: `${API_BASE_PATH}/dev/request-logger`,
  MOCK_DATA: `${API_BASE_PATH}/dev/mock-data`,
  TEST_ENDPOINTS: `${API_BASE_PATH}/dev/test`,
  DEBUG: `${API_BASE_PATH}/dev/debug`,
} as const;

// ============================================================================
// MÉTODOS HTTP
// ============================================================================

export const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  PATCH: 'PATCH',
  DELETE: 'DELETE',
  HEAD: 'HEAD',
  OPTIONS: 'OPTIONS',
} as const;

// ============================================================================
// HEADERS PADRÃO
// ============================================================================

export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'X-API-Version': API_VERSION,
  'X-Request-ID': '', // Será preenchido dinamicamente
  'X-Client-Version': '1.0.0',
} as const;

// ============================================================================
// CÓDIGOS DE STATUS HTTP
// ============================================================================

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

// ============================================================================
// CÓDIGOS DE ERRO PERSONALIZADOS
// ============================================================================

export const ERROR_CODES = {
  // Autenticação
  INVALID_CREDENTIALS: 'AUTH_001',
  TOKEN_EXPIRED: 'AUTH_002',
  TOKEN_INVALID: 'AUTH_003',
  INSUFFICIENT_PERMISSIONS: 'AUTH_004',
  
  // Validação
  VALIDATION_ERROR: 'VAL_001',
  REQUIRED_FIELD: 'VAL_002',
  INVALID_FORMAT: 'VAL_003',
  FIELD_TOO_LONG: 'VAL_004',
  FIELD_TOO_SHORT: 'VAL_005',
  
  // Rate Limiting
  RATE_LIMIT_EXCEEDED: 'RATE_001',
  TOO_MANY_REQUESTS: 'RATE_002',
  
  // Recursos
  RESOURCE_NOT_FOUND: 'RES_001',
  RESOURCE_ALREADY_EXISTS: 'RES_002',
  RESOURCE_IN_USE: 'RES_003',
  
  // Análise
  ANALYSIS_FAILED: 'ANALYSIS_001',
  ANALYSIS_TIMEOUT: 'ANALYSIS_002',
  ANALYSIS_CANCELLED: 'ANALYSIS_003',
  
  // Sistema
  INTERNAL_ERROR: 'SYS_001',
  SERVICE_UNAVAILABLE: 'SYS_002',
  DATABASE_ERROR: 'SYS_003',
  CACHE_ERROR: 'SYS_004',
  
  // Integração
  EXTERNAL_API_ERROR: 'INT_001',
  EXTERNAL_API_TIMEOUT: 'INT_002',
  EXTERNAL_API_RATE_LIMIT: 'INT_003',
} as const;

// ============================================================================
// TIMEOUTS
// ============================================================================

export const TIMEOUTS = {
  DEFAULT: 30000, // 30 segundos
  SHORT: 5000,    // 5 segundos
  LONG: 120000,   // 2 minutos
  ANALYSIS: 300000, // 5 minutos
  UPLOAD: 600000,   // 10 minutos
} as const;

// ============================================================================
// RETRY CONFIGURAÇÕES
// ============================================================================

export const RETRY_CONFIG = {
  MAX_ATTEMPTS: 3,
  DELAY: 1000, // 1 segundo
  BACKOFF_MULTIPLIER: 2,
  MAX_DELAY: 10000, // 10 segundos
} as const;

// ============================================================================
// CACHE CONFIGURAÇÕES
// ============================================================================

export const CACHE_CONFIG = {
  DEFAULT_TTL: 300000, // 5 minutos
  SHORT_TTL: 60000,    // 1 minuto
  LONG_TTL: 3600000,   // 1 hora
  MAX_SIZE: 1000,      // 1000 entradas
} as const;

// ============================================================================
// PAGINAÇÃO PADRÃO
// ============================================================================

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
  MIN_LIMIT: 1,
} as const;

// ============================================================================
// FORMATOS DE EXPORTAÇÃO
// ============================================================================

export const EXPORT_FORMATS = {
  JSON: 'json',
  CSV: 'csv',
  XLSX: 'xlsx',
  PDF: 'pdf',
} as const;

// ============================================================================
// TIPOS DE CONTEÚDO
// ============================================================================

export const CONTENT_TYPES = {
  JSON: 'application/json',
  CSV: 'text/csv',
  XLSX: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  PDF: 'application/pdf',
  FORM_DATA: 'multipart/form-data',
  URL_ENCODED: 'application/x-www-form-urlencoded',
} as const;

// ============================================================================
// FUNÇÕES UTILITÁRIAS
// ============================================================================

/**
 * Constrói URL completa para um endpoint
 */
export const buildUrl = (endpoint: string, params?: Record<string, any>): string => {
  if (!params) return endpoint;
  
  const url = new URL(endpoint, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, String(value));
    }
  });
  
  return url.pathname + url.search;
};

/**
 * Constrói URL para endpoint com ID
 */
export const buildUrlWithId = (baseEndpoint: string, id: string): string => {
  return `${baseEndpoint}/${id}`;
};

/**
 * Constrói URL para endpoint com query parameters
 */
export const buildUrlWithQuery = (
  baseEndpoint: string,
  query: Record<string, any>
): string => {
  return buildUrl(baseEndpoint, query);
};

/**
 * Obtém endpoint completo com base no ambiente
 */
export const getFullEndpoint = (endpoint: string): string => {
  const baseUrl = process.env.REACT_APP_API_BASE_URL || '';
  return `${baseUrl}${endpoint}`;
};

// ============================================================================
// EXPORTAÇÕES
// ============================================================================

export {
  // Endpoints principais
  AUTH_ENDPOINTS,
  KEYWORDS_ENDPOINTS,
  BLOGS_ENDPOINTS,
  ANALYSIS_ENDPOINTS,
  NOTIFICATIONS_ENDPOINTS,
  REPORTS_ENDPOINTS,
  COLLECTORS_ENDPOINTS,
  CONFIG_ENDPOINTS,
  TELEMETRY_ENDPOINTS,
  AUDIT_ENDPOINTS,
  WEBSOCKET_ENDPOINTS,
  HEALTH_ENDPOINTS,
  UTILS_ENDPOINTS,
  EXPORT_ENDPOINTS,
  BATCH_ENDPOINTS,
  CACHE_ENDPOINTS,
  RATE_LIMIT_ENDPOINTS,
  VERSION_ENDPOINTS,
  DEV_ENDPOINTS,
  
  // Configurações
  HTTP_METHODS,
  DEFAULT_HEADERS,
  HTTP_STATUS,
  ERROR_CODES,
  TIMEOUTS,
  RETRY_CONFIG,
  CACHE_CONFIG,
  PAGINATION,
  EXPORT_FORMATS,
  CONTENT_TYPES,
  
  // Funções utilitárias
  buildUrl,
  buildUrlWithId,
  buildUrlWithQuery,
  getFullEndpoint,
}; 