/**
 * useApi.ts
 * 
 * Hook para integração com APIs
 * 
 * Tracing ID: USE_API_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.2.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Chamadas de API centralizadas
 * - Interceptors para autenticação
 * - Tratamento de erros
 * - Loading states
 * - Cache automático
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useAuth } from './useAuth';
import { useAppStore } from '../store/AppStore';

interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

interface ApiError {
  message: string;
  status: number;
  statusText: string;
  data?: any;
}

interface ApiRequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  cache?: boolean;
  cacheTTL?: number;
  retry?: number;
  retryDelay?: number;
}

interface UseApiReturn<T = any> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  execute: (config?: ApiRequestConfig) => Promise<ApiResponse<T>>;
  reset: () => void;
}

interface ApiCache {
  data: any;
  timestamp: number;
  ttl: number;
}

// Cache global para requisições
const apiCache = new Map<string, ApiCache>();

// Configuração base da API
const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
  cacheTTL: 5 * 60 * 1000, // 5 minutos
};

// Função para gerar chave de cache
const generateCacheKey = (url: string, config: ApiRequestConfig): string => {
  const method = config.method || 'GET';
  const body = config.body ? JSON.stringify(config.body) : '';
  return `${method}:${url}:${body}`;
};

// Função para verificar se cache é válido
const isCacheValid = (cache: ApiCache): boolean => {
  return Date.now() - cache.timestamp < cache.ttl;
};

// Função para limpar cache expirado
const cleanupExpiredCache = () => {
  for (const [key, cache] of apiCache.entries()) {
    if (!isCacheValid(cache)) {
      apiCache.delete(key);
    }
  }
};

// Limpar cache expirado periodicamente
setInterval(cleanupExpiredCache, 60000); // A cada minuto

export const useApi = <T = any>(endpoint: string, initialConfig?: ApiRequestConfig): UseApiReturn<T> => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const { token, logout } = useAuth();
  const { actions } = useAppStore();
  const abortControllerRef = useRef<AbortController | null>(null);

  // Função para fazer requisição com retry
  const executeWithRetry = useCallback(async (
    url: string, 
    config: ApiRequestConfig, 
    retryCount = 0
  ): Promise<ApiResponse<T>> => {
    try {
      // Configurar headers
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...config.headers,
      };

      // Adicionar token de autenticação
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Configurar timeout
      const timeout = config.timeout || API_CONFIG.timeout;
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const timeoutId = setTimeout(() => {
        controller.abort();
      }, timeout);

      // Fazer requisição
      const response = await fetch(url, {
        method: config.method || 'GET',
        headers,
        body: config.body ? JSON.stringify(config.body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Verificar se a requisição foi cancelada
      if (controller.signal.aborted) {
        throw new Error('Request timeout');
      }

      // Verificar status da resposta
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: 'Unknown error' };
        }

        // Verificar se é erro de autenticação
        if (response.status === 401) {
          logout();
          throw new Error('Sessão expirada. Faça login novamente.');
        }

        throw {
          message: errorData.message || `HTTP ${response.status}`,
          status: response.status,
          statusText: response.statusText,
          data: errorData,
        };
      }

      // Processar resposta
      const responseData = await response.json();
      
      const apiResponse: ApiResponse<T> = {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
      };

      return apiResponse;

    } catch (err) {
      // Verificar se deve tentar novamente
      const shouldRetry = retryCount < (config.retry || API_CONFIG.retryAttempts) &&
        err instanceof Error && 
        (err.message.includes('timeout') || err.message.includes('network'));

      if (shouldRetry) {
        const delay = config.retryDelay || API_CONFIG.retryDelay;
        await new Promise(resolve => setTimeout(resolve, delay));
        return executeWithRetry(url, config, retryCount + 1);
      }

      throw err;
    }
  }, [token, logout]);

  // Função principal para executar requisição
  const execute = useCallback(async (config: ApiRequestConfig = {}): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      const url = `${API_CONFIG.baseURL}${endpoint}`;
      const cacheKey = generateCacheKey(endpoint, config);
      const useCache = config.cache !== false && config.method === 'GET';

      // Verificar cache
      if (useCache && apiCache.has(cacheKey)) {
        const cached = apiCache.get(cacheKey)!;
        if (isCacheValid(cached)) {
          setData(cached.data);
          setLoading(false);
          return {
            data: cached.data,
            status: 200,
            statusText: 'OK (cached)',
            headers: {},
          };
        }
      }

      // Fazer requisição
      const response = await executeWithRetry(url, config);

      // Salvar no cache se necessário
      if (useCache) {
        const ttl = config.cacheTTL || API_CONFIG.cacheTTL;
        apiCache.set(cacheKey, {
          data: response.data,
          timestamp: Date.now(),
          ttl,
        });
      }

      setData(response.data);
      return response;

    } catch (err) {
      const apiError: ApiError = {
        message: err instanceof Error ? err.message : 'Erro desconhecido',
        status: (err as any).status || 0,
        statusText: (err as any).statusText || '',
        data: (err as any).data,
      };

      setError(apiError);

      // Adicionar notificação de erro
      actions.addNotification({
        type: 'error',
        title: 'Erro na API',
        message: apiError.message,
      });

      throw apiError;
    } finally {
      setLoading(false);
    }
  }, [endpoint, executeWithRetry, actions]);

  // Função para resetar estado
  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    
    // Cancelar requisição em andamento
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset,
  };
};

// Hook para requisições GET
export const useGet = <T = any>(endpoint: string, cache = true) => {
  return useApi<T>(endpoint, { method: 'GET', cache });
};

// Hook para requisições POST
export const usePost = <T = any>(endpoint: string) => {
  return useApi<T>(endpoint, { method: 'POST' });
};

// Hook para requisições PUT
export const usePut = <T = any>(endpoint: string) => {
  return useApi<T>(endpoint, { method: 'PUT' });
};

// Hook para requisições DELETE
export const useDelete = <T = any>(endpoint: string) => {
  return useApi<T>(endpoint, { method: 'DELETE' });
};

// Hook para requisições PATCH
export const usePatch = <T = any>(endpoint: string) => {
  return useApi<T>(endpoint, { method: 'PATCH' });
};

// Função utilitária para limpar cache
export const clearApiCache = (pattern?: string) => {
  if (pattern) {
    for (const key of apiCache.keys()) {
      if (key.includes(pattern)) {
        apiCache.delete(key);
      }
    }
  } else {
    apiCache.clear();
  }
};

// Função utilitária para obter estatísticas do cache
export const getApiCacheStats = () => {
  const total = apiCache.size;
  const valid = Array.from(apiCache.values()).filter(isCacheValid).length;
  const expired = total - valid;

  return {
    total,
    valid,
    expired,
    size: JSON.stringify(Array.from(apiCache.entries())).length,
  };
};

export default useApi; 