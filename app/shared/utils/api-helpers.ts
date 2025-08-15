/**
 * 📋 UTILITÁRIOS DE API COMPARTILHADOS
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Este arquivo contém utilitários para facilitar o uso da API
 * compartilhados entre backend e frontend.
 */

import { 
  ApiResponse, 
  ApiError, 
  RequestConfig, 
  ApiConfig, 
  CacheEntry,
  PaginationParams,
  HttpMethod 
} from '../types/api';

// ============================================================================
// CONFIGURAÇÕES PADRÃO
// ============================================================================

export const DEFAULT_API_CONFIG: ApiConfig = {
  base_url: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  retry_attempts: 3,
  retry_delay: 1000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  auth_type: 'bearer',
  rate_limit: 100,
  cache_enabled: true,
  cache_duration: 300000, // 5 minutos
};

// ============================================================================
// GERADOR DE TRACING ID
// ============================================================================

/**
 * Gera um tracing ID único para rastreamento de requisições
 */
export const generateTracingId = (): string => {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 15);
  const session = Math.random().toString(36).substring(2, 10);
  
  return `trace_${timestamp}_${random}_${session}`;
};

/**
 * Extrai tracing ID de uma resposta da API
 */
export const extractTracingId = (response: ApiResponse<any>): string => {
  return response.tracing_id || generateTracingId();
};

// ============================================================================
// VALIDAÇÃO DE DADOS
// ============================================================================

/**
 * Valida se um objeto é uma resposta válida da API
 */
export const isValidApiResponse = <T>(response: any): response is ApiResponse<T> => {
  return (
    response &&
    typeof response === 'object' &&
    typeof response.success === 'boolean' &&
    typeof response.timestamp === 'string' &&
    typeof response.tracing_id === 'string'
  );
};

/**
 * Valida se um objeto é um erro válido da API
 */
export const isValidApiError = (error: any): error is ApiError => {
  return (
    error &&
    typeof error === 'object' &&
    typeof error.code === 'string' &&
    typeof error.message === 'string'
  );
};

/**
 * Valida parâmetros de paginação
 */
export const validatePaginationParams = (params: Partial<PaginationParams>): PaginationParams => {
  return {
    page: Math.max(1, params.page || 1),
    limit: Math.min(100, Math.max(1, params.limit || 20)),
    sort_by: params.sort_by,
    sort_order: params.sort_order === 'asc' ? 'asc' : 'desc',
  };
};

// ============================================================================
// CONSTRUÇÃO DE URLs E PARÂMETROS
// ============================================================================

/**
 * Constrói query string a partir de um objeto
 */
export const buildQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, String(item)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  
  return searchParams.toString();
};

/**
 * Constrói URL completa com parâmetros
 */
export const buildApiUrl = (
  endpoint: string, 
  params?: Record<string, any>,
  config: Partial<ApiConfig> = {}
): string => {
  const apiConfig = { ...DEFAULT_API_CONFIG, ...config };
  const baseUrl = apiConfig.base_url.replace(/\/$/, '');
  const cleanEndpoint = endpoint.replace(/^\//, '');
  
  let url = `${baseUrl}/${cleanEndpoint}`;
  
  if (params && Object.keys(params).length > 0) {
    const queryString = buildQueryString(params);
    if (queryString) {
      url += `?${queryString}`;
    }
  }
  
  return url;
};

/**
 * Substitui parâmetros de path em uma URL
 */
export const replacePathParams = (
  url: string, 
  params: Record<string, string>
): string => {
  let result = url;
  
  Object.entries(params).forEach(([key, value]) => {
    result = result.replace(`:${key}`, encodeURIComponent(value));
  });
  
  return result;
};

// ============================================================================
// CACHE UTILITIES
// ============================================================================

/**
 * Gera chave de cache baseada em endpoint e parâmetros
 */
export const generateCacheKey = (
  endpoint: string, 
  params?: Record<string, any>
): string => {
  const baseKey = endpoint.replace(/[^a-zA-Z0-9]/g, '_');
  const paramsKey = params ? JSON.stringify(params) : '';
  
  return `api_${baseKey}_${Buffer.from(paramsKey).toString('base64')}`;
};

/**
 * Verifica se um item de cache ainda é válido
 */
export const isCacheValid = <T>(entry: CacheEntry<T>): boolean => {
  return new Date(entry.expires_at) > new Date();
};

/**
 * Cria um novo item de cache
 */
export const createCacheEntry = <T>(
  key: string, 
  data: T, 
  duration: number = DEFAULT_API_CONFIG.cache_duration
): CacheEntry<T> => {
  const now = new Date();
  const expiresAt = new Date(now.getTime() + duration);
  
  return {
    key,
    data,
    expires_at: expiresAt.toISOString(),
    created_at: now.toISOString(),
    access_count: 0,
    last_accessed: now.toISOString(),
  };
};

/**
 * Atualiza estatísticas de acesso do cache
 */
export const updateCacheAccess = <T>(entry: CacheEntry<T>): CacheEntry<T> => {
  return {
    ...entry,
    access_count: entry.access_count + 1,
    last_accessed: new Date().toISOString(),
  };
};

// ============================================================================
// TRATAMENTO DE ERROS
// ============================================================================

/**
 * Cria um erro de API padronizado
 */
export const createApiError = (
  code: string,
  message: string,
  details?: Record<string, any>,
  stack?: string
): ApiError => {
  return {
    code,
    message,
    details,
    stack,
  };
};

/**
 * Cria uma resposta de erro padronizada
 */
export const createErrorResponse = <T>(
  error: ApiError,
  tracingId: string = generateTracingId()
): ApiResponse<T> => {
  return {
    success: false,
    error,
    timestamp: new Date().toISOString(),
    tracing_id: tracingId,
  };
};

/**
 * Cria uma resposta de sucesso padronizada
 */
export const createSuccessResponse = <T>(
  data: T,
  message?: string,
  tracingId: string = generateTracingId()
): ApiResponse<T> => {
  return {
    success: true,
    data,
    message,
    timestamp: new Date().toISOString(),
    tracing_id: tracingId,
  };
};

/**
 * Mapeia códigos de erro HTTP para códigos de erro da API
 */
export const mapHttpErrorToApiError = (status: number, message?: string): ApiError => {
  const errorMap: Record<number, { code: string; message: string }> = {
    400: { code: 'BAD_REQUEST', message: 'Requisição inválida' },
    401: { code: 'UNAUTHORIZED', message: 'Não autorizado' },
    403: { code: 'FORBIDDEN', message: 'Acesso negado' },
    404: { code: 'NOT_FOUND', message: 'Recurso não encontrado' },
    405: { code: 'METHOD_NOT_ALLOWED', message: 'Método não permitido' },
    409: { code: 'CONFLICT', message: 'Conflito de dados' },
    422: { code: 'VALIDATION_ERROR', message: 'Erro de validação' },
    429: { code: 'RATE_LIMIT_EXCEEDED', message: 'Limite de taxa excedido' },
    500: { code: 'INTERNAL_SERVER_ERROR', message: 'Erro interno do servidor' },
    502: { code: 'BAD_GATEWAY', message: 'Erro de gateway' },
    503: { code: 'SERVICE_UNAVAILABLE', message: 'Serviço indisponível' },
    504: { code: 'GATEWAY_TIMEOUT', message: 'Timeout do gateway' },
  };
  
  const defaultError = { code: 'UNKNOWN_ERROR', message: 'Erro desconhecido' };
  const mappedError = errorMap[status] || defaultError;
  
  return createApiError(
    mappedError.code,
    message || mappedError.message,
    { http_status: status }
  );
};

/**
 * Verifica se um erro é recuperável (pode ser tentado novamente)
 */
export const isRetryableError = (error: ApiError): boolean => {
  const retryableCodes = [
    'RATE_LIMIT_EXCEEDED',
    'INTERNAL_SERVER_ERROR',
    'BAD_GATEWAY',
    'SERVICE_UNAVAILABLE',
    'GATEWAY_TIMEOUT',
    'NETWORK_ERROR',
    'TIMEOUT_ERROR',
  ];
  
  return retryableCodes.includes(error.code);
};

// ============================================================================
// UTILITÁRIOS DE REQUISIÇÃO
// ============================================================================

/**
 * Prepara headers para uma requisição
 */
export const prepareHeaders = (
  headers: Record<string, string> = {},
  authToken?: string,
  config: Partial<ApiConfig> = {}
): Record<string, string> => {
  const apiConfig = { ...DEFAULT_API_CONFIG, ...config };
  const defaultHeaders = { ...apiConfig.headers };
  
  // Adiciona token de autenticação se fornecido
  if (authToken && apiConfig.auth_type === 'bearer') {
    defaultHeaders.Authorization = `Bearer ${authToken}`;
  }
  
  // Adiciona tracing ID
  defaultHeaders['X-Tracing-ID'] = generateTracingId();
  
  // Adiciona headers customizados
  return { ...defaultHeaders, ...headers };
};

/**
 * Prepara configuração de requisição
 */
export const prepareRequestConfig = (
  method: HttpMethod,
  url: string,
  data?: any,
  config: Partial<RequestConfig> = {}
): RequestConfig => {
  return {
    method,
    url,
    data,
    timeout: DEFAULT_API_CONFIG.timeout,
    retry: true,
    retry_attempts: DEFAULT_API_CONFIG.retry_attempts,
    retry_delay: DEFAULT_API_CONFIG.retry_delay,
    ...config,
  };
};

/**
 * Serializa dados para envio na requisição
 */
export const serializeRequestData = (data: any): string => {
  if (data instanceof FormData) {
    return data as any;
  }
  
  if (data instanceof URLSearchParams) {
    return data.toString();
  }
  
  if (typeof data === 'object' && data !== null) {
    return JSON.stringify(data);
  }
  
  return String(data);
};

/**
 * Deserializa dados da resposta
 */
export const deserializeResponseData = async (response: Response): Promise<any> => {
  const contentType = response.headers.get('content-type');
  
  if (contentType?.includes('application/json')) {
    return response.json();
  }
  
  if (contentType?.includes('text/')) {
    return response.text();
  }
  
  if (contentType?.includes('multipart/form-data')) {
    return response.formData();
  }
  
  return response.blob();
};

// ============================================================================
// UTILITÁRIOS DE PAGINAÇÃO
// ============================================================================

/**
 * Calcula informações de paginação
 */
export const calculatePagination = (
  total: number,
  page: number,
  limit: number
): {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  offset: number;
} => {
  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.max(1, Math.min(page, totalPages));
  const offset = (currentPage - 1) * limit;
  
  return {
    page: currentPage,
    limit,
    total,
    total_pages: totalPages,
    has_next: currentPage < totalPages,
    has_prev: currentPage > 1,
    offset,
  };
};

/**
 * Extrai parâmetros de paginação de uma URL
 */
export const extractPaginationFromUrl = (url: string): PaginationParams => {
  const urlObj = new URL(url);
  const page = parseInt(urlObj.searchParams.get('page') || '1', 10);
  const limit = parseInt(urlObj.searchParams.get('limit') || '20', 10);
  const sortBy = urlObj.searchParams.get('sort_by') || undefined;
  const sortOrder = (urlObj.searchParams.get('sort_order') as 'asc' | 'desc') || 'desc';
  
  return validatePaginationParams({ page, limit, sort_by: sortBy, sort_order: sortOrder });
};

// ============================================================================
// UTILITÁRIOS DE PERFORMANCE
// ============================================================================

/**
 * Mede tempo de execução de uma função
 */
export const measureExecutionTime = async <T>(
  fn: () => Promise<T>,
  tracingId?: string
): Promise<{ result: T; executionTime: number }> => {
  const startTime = performance.now();
  const result = await fn();
  const endTime = performance.now();
  
  const executionTime = endTime - startTime;
  
  // Log de performance (opcional)
  if (process.env.NODE_ENV === 'development') {
    console.log(`[PERF] ${tracingId || 'unknown'} - ${executionTime.toFixed(2)}ms`);
  }
  
  return { result, executionTime };
};

/**
 * Debounce para evitar múltiplas requisições
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Throttle para limitar frequência de requisições
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let lastCall = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
};

// ============================================================================
// UTILITÁRIOS DE LOGGING
// ============================================================================

/**
 * Log estruturado para requisições
 */
export const logApiRequest = (
  method: HttpMethod,
  url: string,
  tracingId: string,
  data?: any
): void => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`🌐 API Request [${tracingId}]`);
    console.log('Method:', method);
    console.log('URL:', url);
    if (data) {
      console.log('Data:', data);
    }
    console.groupEnd();
  }
};

/**
 * Log estruturado para respostas
 */
export const logApiResponse = (
  tracingId: string,
  response: ApiResponse<any>,
  executionTime?: number
): void => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`✅ API Response [${tracingId}]`);
    console.log('Success:', response.success);
    console.log('Timestamp:', response.timestamp);
    if (executionTime) {
      console.log('Execution Time:', `${executionTime.toFixed(2)}ms`);
    }
    if (response.data) {
      console.log('Data:', response.data);
    }
    if (response.error) {
      console.error('Error:', response.error);
    }
    console.groupEnd();
  }
};

/**
 * Log estruturado para erros
 */
export const logApiError = (
  tracingId: string,
  error: ApiError,
  context?: Record<string, any>
): void => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`❌ API Error [${tracingId}]`);
    console.error('Code:', error.code);
    console.error('Message:', error.message);
    if (error.details) {
      console.error('Details:', error.details);
    }
    if (context) {
      console.error('Context:', context);
    }
    console.groupEnd();
  }
};

// ============================================================================
// UTILITÁRIOS DE VALIDAÇÃO
// ============================================================================

/**
 * Valida formato de email
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Valida formato de URL
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Valida formato de UUID
 */
export const isValidUuid = (uuid: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

/**
 * Sanitiza string removendo caracteres perigosos
 */
export const sanitizeString = (str: string): string => {
  return str
    .replace(/[<>]/g, '') // Remove < e >
    .replace(/javascript:/gi, '') // Remove javascript:
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim();
};

// ============================================================================
// EXPORTAÇÕES
// ============================================================================

export {
  DEFAULT_API_CONFIG,
  generateTracingId,
  extractTracingId,
  isValidApiResponse,
  isValidApiError,
  validatePaginationParams,
  buildQueryString,
  buildApiUrl,
  replacePathParams,
  generateCacheKey,
  isCacheValid,
  createCacheEntry,
  updateCacheAccess,
  createApiError,
  createErrorResponse,
  createSuccessResponse,
  mapHttpErrorToApiError,
  isRetryableError,
  prepareHeaders,
  prepareRequestConfig,
  serializeRequestData,
  deserializeResponseData,
  calculatePagination,
  extractPaginationFromUrl,
  measureExecutionTime,
  debounce,
  throttle,
  logApiRequest,
  logApiResponse,
  logApiError,
  isValidEmail,
  isValidUrl,
  isValidUuid,
  sanitizeString,
}; 