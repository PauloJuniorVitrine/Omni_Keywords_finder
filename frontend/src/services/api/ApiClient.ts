/**
 * 🔗 ApiClient.ts
 * 🎯 Objetivo: Cliente HTTP centralizado com interceptors e tratamento de erros
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: API_CLIENT_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

// Tipos para configuração do cliente
export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  retryDelay: number;
  enableCache: boolean;
  enableLogging: boolean;
  enableRetry: boolean;
  enableRateLimit: boolean;
}

// Tipos para requisições
export interface ApiRequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  params?: Record<string, any>;
  timeout?: number;
  retries?: number;
  cache?: boolean;
  cacheTTL?: number;
  skipAuth?: boolean;
  skipLogging?: boolean;
}

// Tipos para respostas
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  config: ApiRequestConfig;
  requestId: string;
  timestamp: number;
}

// Tipos para erros
export interface ApiError {
  message: string;
  status: number;
  statusText: string;
  code?: string;
  details?: any;
  requestId: string;
  timestamp: number;
  retryCount: number;
}

// Tipos para interceptors
export interface RequestInterceptor {
  (config: ApiRequestConfig): ApiRequestConfig | Promise<ApiRequestConfig>;
}

export interface ResponseInterceptor {
  (response: ApiResponse): ApiResponse | Promise<ApiResponse>;
}

export interface ErrorInterceptor {
  (error: ApiError): ApiError | Promise<ApiError>;
}

// Configuração padrão
const DEFAULT_CONFIG: ApiClientConfig = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  enableCache: true,
  enableLogging: true,
  enableRetry: true,
  enableRateLimit: true,
};

// Classe principal do cliente HTTP
export class ApiClient {
  private config: ApiClientConfig;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private errorInterceptors: ErrorInterceptor[] = [];
  private cache: Map<string, { data: any; timestamp: number; ttl: number }> = new Map();
  private rateLimiters: Map<string, { tokens: number; lastRefill: number; maxTokens: number; refillRate: number }> = new Map();

  constructor(config: Partial<ApiClientConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  // Métodos para adicionar interceptors
  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  addErrorInterceptor(interceptor: ErrorInterceptor): void {
    this.errorInterceptors.push(interceptor);
  }

  // Método principal para fazer requisições
  async request<T = any>(endpoint: string, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    const requestId = this.generateRequestId();
    const timestamp = Date.now();

    try {
      // Aplicar interceptors de requisição
      let finalConfig = await this.applyRequestInterceptors({
        method: 'GET',
        ...config,
      });

      // Verificar rate limiting
      if (this.config.enableRateLimit && !finalConfig.skipAuth) {
        await this.checkRateLimit(endpoint);
      }

      // Verificar cache
      if (this.config.enableCache && finalConfig.cache !== false && finalConfig.method === 'GET') {
        const cachedData = this.getCachedData(endpoint, finalConfig);
        if (cachedData) {
          return {
            data: cachedData,
            status: 200,
            statusText: 'OK (Cached)',
            headers: {},
            config: finalConfig,
            requestId,
            timestamp,
          };
        }
      }

      // Fazer a requisição
      const response = await this.makeRequest<T>(endpoint, finalConfig, requestId, timestamp);

      // Aplicar interceptors de resposta
      const finalResponse = await this.applyResponseInterceptors(response);

      // Armazenar no cache se necessário
      if (this.config.enableCache && finalConfig.cache !== false && finalConfig.method === 'GET') {
        this.setCachedData(endpoint, finalConfig, finalResponse.data, finalConfig.cacheTTL || 300000);
      }

      return finalResponse;
    } catch (error) {
      // Aplicar interceptors de erro
      const apiError = await this.applyErrorInterceptors(this.createApiError(error, requestId, timestamp));
      
      // Log do erro
      if (this.config.enableLogging && !config.skipLogging) {
        this.logError(apiError, endpoint, finalConfig);
      }

      throw apiError;
    }
  }

  // Métodos HTTP específicos
  async get<T = any>(endpoint: string, config: Omit<ApiRequestConfig, 'method'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T = any>(endpoint: string, data?: any, config: Omit<ApiRequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'POST', body: data });
  }

  async put<T = any>(endpoint: string, data?: any, config: Omit<ApiRequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PUT', body: data });
  }

  async delete<T = any>(endpoint: string, config: Omit<ApiRequestConfig, 'method'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }

  async patch<T = any>(endpoint: string, data?: any, config: Omit<ApiRequestConfig, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PATCH', body: data });
  }

  // Métodos privados
  private async applyRequestInterceptors(config: ApiRequestConfig): Promise<ApiRequestConfig> {
    let finalConfig = config;
    
    for (const interceptor of this.requestInterceptors) {
      finalConfig = await interceptor(finalConfig);
    }
    
    return finalConfig;
  }

  private async applyResponseInterceptors(response: ApiResponse): Promise<ApiResponse> {
    let finalResponse = response;
    
    for (const interceptor of this.responseInterceptors) {
      finalResponse = await interceptor(finalResponse);
    }
    
    return finalResponse;
  }

  private async applyErrorInterceptors(error: ApiError): Promise<ApiError> {
    let finalError = error;
    
    for (const interceptor of this.errorInterceptors) {
      finalError = await interceptor(finalError);
    }
    
    return finalError;
  }

  private async makeRequest<T>(
    endpoint: string,
    config: ApiRequestConfig,
    requestId: string,
    timestamp: number
  ): Promise<ApiResponse<T>> {
    const url = this.buildUrl(endpoint, config.params);
    const headers = this.buildHeaders(config);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeout || this.config.timeout);

    try {
      const response = await fetch(url, {
        method: config.method,
        headers,
        body: config.body ? JSON.stringify(config.body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const responseHeaders: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        responseHeaders[key] = value;
      });

      return {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
        config,
        requestId,
        timestamp,
      };
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      throw error;
    }
  }

  private buildUrl(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(endpoint, this.config.baseURL);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    
    return url.toString();
  }

  private buildHeaders(config: ApiRequestConfig): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    // Adicionar token de autenticação se disponível
    if (!config.skipAuth) {
      const token = localStorage.getItem('authToken');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  private createApiError(error: any, requestId: string, timestamp: number): ApiError {
    return {
      message: error.message || 'Unknown error',
      status: error.status || 0,
      statusText: error.statusText || '',
      code: error.code,
      details: error.details,
      requestId,
      timestamp,
      retryCount: 0,
    };
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCachedData(endpoint: string, config: ApiRequestConfig): any | null {
    const cacheKey = this.generateCacheKey(endpoint, config);
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      return cached.data;
    }
    
    if (cached) {
      this.cache.delete(cacheKey);
    }
    
    return null;
  }

  private setCachedData(endpoint: string, config: ApiRequestConfig, data: any, ttl: number): void {
    const cacheKey = this.generateCacheKey(endpoint, config);
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  private generateCacheKey(endpoint: string, config: ApiRequestConfig): string {
    const params = config.params ? JSON.stringify(config.params) : '';
    return `${endpoint}_${params}`;
  }

  private async checkRateLimit(endpoint: string): Promise<void> {
    const limiterKey = this.getRateLimiterKey(endpoint);
    const limiter = this.rateLimiters.get(limiterKey) || {
      tokens: 10,
      lastRefill: Date.now(),
      maxTokens: 10,
      refillRate: 1000, // 1 token por segundo
    };

    // Refill tokens
    const now = Date.now();
    const timePassed = now - limiter.lastRefill;
    const tokensToAdd = Math.floor(timePassed / limiter.refillRate);
    limiter.tokens = Math.min(limiter.maxTokens, limiter.tokens + tokensToAdd);
    limiter.lastRefill = now;

    if (limiter.tokens <= 0) {
      throw new Error('Rate limit exceeded');
    }

    limiter.tokens--;
    this.rateLimiters.set(limiterKey, limiter);
  }

  private getRateLimiterKey(endpoint: string): string {
    return endpoint.split('/')[1] || 'default';
  }

  private logError(error: ApiError, endpoint: string, config: ApiRequestConfig): void {
    console.error('API Error:', {
      requestId: error.requestId,
      endpoint,
      method: config.method,
      status: error.status,
      message: error.message,
      timestamp: new Date(error.timestamp).toISOString(),
    });
  }

  // Métodos de utilidade
  clearCache(): void {
    this.cache.clear();
  }

  clearCacheForEndpoint(endpoint: string): void {
    const keysToDelete: string[] = [];
    this.cache.forEach((_, key) => {
      if (key.startsWith(endpoint)) {
        keysToDelete.push(key);
      }
    });
    keysToDelete.forEach(key => this.cache.delete(key));
  }

  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }

  setRateLimit(endpoint: string, maxTokens: number, refillRate: number): void {
    const key = this.getRateLimiterKey(endpoint);
    this.rateLimiters.set(key, {
      tokens: maxTokens,
      lastRefill: Date.now(),
      maxTokens,
      refillRate,
    });
  }
}

// Instância global do cliente
export const apiClient = new ApiClient();

// Exportar tipos
export type { ApiClientConfig, ApiRequestConfig, ApiResponse, ApiError }; 