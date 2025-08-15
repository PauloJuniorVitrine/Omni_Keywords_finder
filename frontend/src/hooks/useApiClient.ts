/**
 * 🔗 useApiClient.ts
 * 🎯 Objetivo: Hook para usar o cliente HTTP centralizado
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: HOOK_API_CLIENT_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiClient, ApiRequestConfig, ApiResponse, ApiError } from '../services/api/ApiClient';
import { authRequestInterceptor, authResponseInterceptor, authErrorInterceptor } from '../services/api/interceptors/AuthInterceptor';

// Tipos para o hook
interface UseApiClientState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  lastUpdated: Date | null;
}

interface UseApiClientOptions {
  initialData?: any;
  cache?: boolean;
  cacheTTL?: number;
  retries?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError) => void;
  onLoadingChange?: (loading: boolean) => void;
}

// Hook principal para usar o cliente HTTP
export function useApiClient<T = any>(options: UseApiClientOptions = {}) {
  const [state, setState] = useState<UseApiClientState<T>>({
    data: options.initialData || null,
    loading: false,
    error: null,
    lastUpdated: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  // Configurar interceptors na primeira execução
  useEffect(() => {
    // Adicionar interceptors de autenticação
    apiClient.addRequestInterceptor(authRequestInterceptor);
    apiClient.addResponseInterceptor(authResponseInterceptor);
    apiClient.addErrorInterceptor(authErrorInterceptor);

    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Função para fazer requisições
  const request = useCallback(async (
    endpoint: string,
    config: ApiRequestConfig = {}
  ): Promise<ApiResponse<T>> => {
    // Cancelar requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Criar novo controller para esta requisição
    abortControllerRef.current = new AbortController();

    // Atualizar estado de loading
    setState(prev => ({ ...prev, loading: true, error: null }));
    options.onLoadingChange?.(true);

    try {
      // Fazer a requisição
      const response = await apiClient.request<T>(endpoint, {
        ...config,
        cache: options.cache !== false,
        cacheTTL: options.cacheTTL,
        retries: options.retries,
      });

      // Atualizar estado apenas se o componente ainda estiver montado
      if (mountedRef.current) {
        setState({
          data: response.data,
          loading: false,
          error: null,
          lastUpdated: new Date(),
        });

        options.onSuccess?.(response.data);
        options.onLoadingChange?.(false);
      }

      return response;
    } catch (error) {
      // Verificar se foi cancelado
      if (error instanceof Error && error.name === 'AbortError') {
        throw error;
      }

      const apiError = error as ApiError;

      // Atualizar estado apenas se o componente ainda estiver montado
      if (mountedRef.current) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: apiError,
        }));

        options.onError?.(apiError);
        options.onLoadingChange?.(false);
      }

      throw apiError;
    }
  }, [options]);

  // Funções HTTP específicas
  const get = useCallback(async (
    endpoint: string,
    config: Omit<ApiRequestConfig, 'method'> = {}
  ): Promise<ApiResponse<T>> => {
    return request(endpoint, { ...config, method: 'GET' });
  }, [request]);

  const post = useCallback(async (
    endpoint: string,
    data?: any,
    config: Omit<ApiRequestConfig, 'method' | 'body'> = {}
  ): Promise<ApiResponse<T>> => {
    return request(endpoint, { ...config, method: 'POST', body: data });
  }, [request]);

  const put = useCallback(async (
    endpoint: string,
    data?: any,
    config: Omit<ApiRequestConfig, 'method' | 'body'> = {}
  ): Promise<ApiResponse<T>> => {
    return request(endpoint, { ...config, method: 'PUT', body: data });
  }, [request]);

  const del = useCallback(async (
    endpoint: string,
    config: Omit<ApiRequestConfig, 'method'> = {}
  ): Promise<ApiResponse<T>> => {
    return request(endpoint, { ...config, method: 'DELETE' });
  }, [request]);

  const patch = useCallback(async (
    endpoint: string,
    data?: any,
    config: Omit<ApiRequestConfig, 'method' | 'body'> = {}
  ): Promise<ApiResponse<T>> => {
    return request(endpoint, { ...config, method: 'PATCH', body: data });
  }, [request]);

  // Função para cancelar requisição atual
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  // Função para limpar estado
  const clear = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      lastUpdated: null,
    });
  }, []);

  // Função para atualizar dados manualmente
  const setData = useCallback((data: T) => {
    setState(prev => ({
      ...prev,
      data,
      lastUpdated: new Date(),
    }));
  }, []);

  // Função para limpar erro
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    // Estado
    data: state.data,
    loading: state.loading,
    error: state.error,
    lastUpdated: state.lastUpdated,
    
    // Funções HTTP
    request,
    get,
    post,
    put,
    delete: del,
    patch,
    
    // Funções de controle
    cancel,
    clear,
    setData,
    clearError,
  };
}

// Hook para requisições com dados iniciais
export function useApiClientWithData<T = any>(
  endpoint: string,
  config: ApiRequestConfig = {},
  options: UseApiClientOptions = {}
) {
  const apiClient = useApiClient<T>(options);

  // Função para carregar dados
  const loadData = useCallback(async () => {
    try {
      await apiClient.get(endpoint, config);
    } catch (error) {
      // Erro já tratado pelo hook principal
    }
  }, [apiClient, endpoint, config]);

  // Carregar dados automaticamente
  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    ...apiClient,
    loadData,
  };
}

// Hook para requisições com polling
export function useApiClientWithPolling<T = any>(
  endpoint: string,
  interval: number = 30000,
  config: ApiRequestConfig = {},
  options: UseApiClientOptions = {}
) {
  const apiClient = useApiClient<T>(options);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Função para iniciar polling
  const startPolling = useCallback(async () => {
    // Carregar dados imediatamente
    try {
      await apiClient.get(endpoint, config);
    } catch (error) {
      // Erro já tratado pelo hook principal
    }

    // Configurar intervalo
    intervalRef.current = setInterval(async () => {
      try {
        await apiClient.get(endpoint, config);
      } catch (error) {
        // Erro já tratado pelo hook principal
      }
    }, interval);
  }, [apiClient, endpoint, config, interval]);

  // Função para parar polling
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Função para reiniciar polling
  const restartPolling = useCallback(() => {
    stopPolling();
    startPolling();
  }, [stopPolling, startPolling]);

  // Cleanup
  useEffect(() => {
    startPolling();
    
    return () => {
      stopPolling();
    };
  }, [startPolling, stopPolling]);

  return {
    ...apiClient,
    startPolling,
    stopPolling,
    restartPolling,
    isPolling: !!intervalRef.current,
  };
}

// Hook para cache de dados
export function useApiClientWithCache<T = any>(
  cacheKey: string,
  options: UseApiClientOptions = {}
) {
  const apiClient = useApiClient<T>({
    ...options,
    cache: true,
    cacheTTL: 300000, // 5 minutos por padrão
  });

  // Função para invalidar cache
  const invalidateCache = useCallback(() => {
    apiClient.clearCache();
  }, [apiClient]);

  // Função para obter dados do cache
  const getCachedData = useCallback(() => {
    const cacheStats = apiClient.getCacheStats();
    return cacheStats.keys.includes(cacheKey);
  }, [apiClient, cacheKey]);

  return {
    ...apiClient,
    invalidateCache,
    getCachedData,
  };
}

// Hook para upload de arquivos
export function useApiClientWithUpload<T = any>(options: UseApiClientOptions = {}) {
  const apiClient = useApiClient<T>(options);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Função para upload de arquivo
  const uploadFile = useCallback(async (
    endpoint: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post(endpoint, formData, {
        headers: {
          // Não definir Content-Type, deixar o browser definir com boundary
        },
      });

      setUploadProgress(100);
      onProgress?.(100);

      return response;
    } catch (error) {
      setUploadProgress(0);
      onProgress?.(0);
      throw error;
    }
  }, [apiClient]);

  // Função para upload múltiplo
  const uploadMultipleFiles = useCallback(async (
    endpoint: string,
    files: File[],
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>[]> => {
    const responses: ApiResponse<T>[] = [];
    let completed = 0;

    for (const file of files) {
      try {
        const response = await uploadFile(endpoint, file);
        responses.push(response);
        completed++;
        
        const progress = (completed / files.length) * 100;
        setUploadProgress(progress);
        onProgress?.(progress);
      } catch (error) {
        // Continuar com outros arquivos mesmo se um falhar
        console.error(`Error uploading file ${file.name}:`, error);
      }
    }

    return responses;
  }, [uploadFile]);

  return {
    ...apiClient,
    uploadFile,
    uploadMultipleFiles,
    uploadProgress,
  };
} 