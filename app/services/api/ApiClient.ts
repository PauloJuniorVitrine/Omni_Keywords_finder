/**
 * 🌐 Serviço ApiClient - Cliente HTTP para API
 * 🎯 Objetivo: Comunicação robusta com backend
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: FRONTEND_API_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
  success: boolean;
  errors?: string[];
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

export interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  authToken?: string;
  onUnauthorized?: () => void;
  onError?: (error: ApiError) => void;
}

class ApiClient {
  private config: ApiClientConfig;
  private authToken: string | null = null;

  constructor(config: ApiClientConfig) {
    this.config = {
      timeout: 10000,
      retries: 3,
      retryDelay: 1000,
      ...config
    };
    
    this.authToken = config.authToken || null;
  }

  /**
   * Define o token de autenticação
   */
  setAuthToken(token: string | null): void {
    this.authToken = token;
  }

  /**
   * Obtém o token de autenticação
   */
  getAuthToken(): string | null {
    return this.authToken;
  }

  /**
   * Faz uma requisição HTTP
   */
  async request<T = any>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = this.config.timeout,
      retries = this.config.retries || 3,
      retryDelay = this.config.retryDelay || 1000
    } = config;

    const url = `${this.config.baseURL}${endpoint}`;
    const requestHeaders = this.buildHeaders(headers);

    let lastError: ApiError | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          method,
          headers: requestHeaders,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        const responseData = await this.parseResponse(response);

        if (response.ok) {
          return {
            data: responseData,
            status: response.status,
            success: true
          };
        } else {
          const error: ApiError = {
            message: responseData.message || 'Erro na requisição',
            status: response.status,
            code: responseData.code,
            details: responseData
          };

          // Tratar erros específicos
          if (response.status === 401) {
            this.config.onUnauthorized?.();
            throw error;
          }

          if (response.status >= 500 && attempt < retries) {
            lastError = error;
            await this.delay(retryDelay * Math.pow(2, attempt));
            continue;
          }

          throw error;
        }
      } catch (error) {
        if (error instanceof Error) {
          if (error.name === 'AbortError') {
            throw {
              message: 'Timeout na requisição',
              status: 408
            } as ApiError;
          }

          if (attempt < retries) {
            lastError = {
              message: error.message,
              status: 0
            };
            await this.delay(retryDelay * Math.pow(2, attempt));
            continue;
          }
        }

        throw error;
      }
    }

    throw lastError || {
      message: 'Erro desconhecido',
      status: 0
    };
  }

  /**
   * Requisição GET
   */
  async get<T = any>(endpoint: string, config?: Omit<RequestConfig, 'method' | 'body'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  /**
   * Requisição POST
   */
  async post<T = any>(endpoint: string, data?: any, config?: Omit<RequestConfig, 'method'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'POST', body: data });
  }

  /**
   * Requisição PUT
   */
  async put<T = any>(endpoint: string, data?: any, config?: Omit<RequestConfig, 'method'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PUT', body: data });
  }

  /**
   * Requisição PATCH
   */
  async patch<T = any>(endpoint: string, data?: any, config?: Omit<RequestConfig, 'method'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PATCH', body: data });
  }

  /**
   * Requisição DELETE
   */
  async delete<T = any>(endpoint: string, config?: Omit<RequestConfig, 'method' | 'body'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }

  /**
   * Upload de arquivo
   */
  async uploadFile<T = any>(
    endpoint: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();

    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          onProgress?.(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            resolve({
              data,
              status: xhr.status,
              success: true
            });
          } catch (error) {
            reject({
              message: 'Erro ao processar resposta',
              status: xhr.status
            });
          }
        } else {
          reject({
            message: xhr.statusText || 'Erro no upload',
            status: xhr.status
          });
        }
      });

      xhr.addEventListener('error', () => {
        reject({
          message: 'Erro de rede',
          status: 0
        });
      });

      xhr.open('POST', `${this.config.baseURL}${endpoint}`);
      
      // Adicionar headers de autenticação
      if (this.authToken) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.authToken}`);
      }
      
      xhr.setRequestHeader('Content-Type', 'multipart/form-data');
      xhr.send(formData);
    });
  }

  /**
   * Download de arquivo
   */
  async downloadFile(endpoint: string, filename?: string): Promise<void> {
    const response = await fetch(`${this.config.baseURL}${endpoint}`, {
      headers: this.buildHeaders()
    });

    if (!response.ok) {
      throw {
        message: 'Erro ao baixar arquivo',
        status: response.status
      };
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'download';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  /**
   * Construir headers da requisição
   */
  private buildHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...customHeaders
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  /**
   * Parsear resposta da API
   */
  private async parseResponse(response: Response): Promise<any> {
    const contentType = response.headers.get('content-type');
    
    if (contentType?.includes('application/json')) {
      return response.json();
    }
    
    if (contentType?.includes('text/')) {
      return response.text();
    }
    
    return response.blob();
  }

  /**
   * Delay para retry
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Instância global do cliente API
const apiClient = new ApiClient({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  retries: 3,
  retryDelay: 1000,
  onUnauthorized: () => {
    // Redirecionar para login ou limpar token
    localStorage.removeItem('authToken');
    window.location.href = '/login';
  },
  onError: (error) => {
    console.error('API Error:', error);
  }
});

export default apiClient;
export { ApiClient }; 