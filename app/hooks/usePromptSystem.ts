/**
 * Hook personalizado para gerenciar o sistema de preenchimento de lacunas
 * 
 * Tracing ID: FIXTYPE-001_HOOK_UPDATE_20241227_001
 * Data: 2024-12-27
 * 
 * Atualizado com timeout e retry automático
 * Tracing ID: FIXTYPE-006_HOOK_TIMEOUT_2025_001
 * Data: 2025-01-27
 * 
 * Atualizado com tratamento de erros centralizado
 * Tracing ID: FIXTYPE-008_ERROR_HANDLER_2025_001
 * Data: 2025-01-27
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useLoadingWithTimeout } from './useLoadingWithTimeout';
import { useErrorHandler } from '../utils/errorHandler';
import {
  Nicho,
  Categoria,
  PromptBase,
  DadosColetados,
  CreateNichoRequest,
  CreateCategoriaRequest,
  DashboardStats,
  ApiResponse
} from '../types/api-sync';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Funções auxiliares para chamadas da API com tratamento de erros
const apiCall = async (endpoint: string, options: RequestInit = {}, context?: Record<string, any>) => {
  return executeWithRetry(async () => {
    const response = await fetch(`${API_BASE_URL}/api/prompt-system${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
      const appError = processError(new Error(error.detail || `HTTP ${response.status}`), {
        ...context,
        endpoint,
        statusCode: response.status
      });
      handleError(appError);
      throw appError;
    }

    return response.json();
  }, context);
};

const apiUpload = async (endpoint: string, formData: FormData, context?: Record<string, any>) => {
  return executeWithRetry(async () => {
    const response = await fetch(`${API_BASE_URL}/api/prompt-system${endpoint}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
      const appError = processError(new Error(error.detail || `HTTP ${response.status}`), {
        ...context,
        endpoint,
        statusCode: response.status
      });
      handleError(appError);
      throw appError;
    }

    return response.json();
  }, context);
};

export const usePromptSystem = () => {
  const queryClient = useQueryClient();
  const { processError, executeWithRetry, handleError, getUserFriendlyMessage } = useErrorHandler();

  // Funções para buscar dados
  const getNichos = async (): Promise<Nicho[]> => {
    return apiCall('/nichos', {}, { action: 'getNichos', componentName: 'usePromptSystem' });
  };

  const getCategorias = async (nichoId?: string): Promise<Categoria[]> => {
    const params = nichoId ? `?nicho_id=${nichoId}` : '';
    return apiCall(`/categorias${params}`, {}, { 
      action: 'getCategorias', 
      componentName: 'usePromptSystem',
      nichoId 
    });
  };

  const getPromptsBase = async (categoriaId: string): Promise<PromptBase | null> => {
    return apiCall(`/prompts-base/${categoriaId}`, {}, { 
      action: 'getPromptsBase', 
      componentName: 'usePromptSystem',
      categoriaId 
    });
  };

  const getDadosColetados = async (categoriaId?: string): Promise<DadosColetados[]> => {
    const params = categoriaId ? `?categoria_id=${categoriaId}` : '';
    return apiCall(`/dados-coletados${params}`, {}, { 
      action: 'getDadosColetados', 
      componentName: 'usePromptSystem',
      categoriaId 
    });
  };

  const getPromptsPreenchidos = async (filters?: {
    nichoId?: string;
    categoriaId?: string;
    status?: string;
  }): Promise<any[]> => {
    const params = new URLSearchParams();
    if (filters?.nichoId) params.append('nicho_id', filters.nichoId);
    if (filters?.categoriaId) params.append('categoria_id', filters.categoriaId);
    if (filters?.status) params.append('status', filters.status);
    
    const queryString = params.toString();
    return apiCall(`/prompts-preenchidos${queryString ? `?${queryString}` : ''}`);
  };

  const getStats = async (): Promise<DashboardStats> => {
    return apiCall('/stats');
  };

  // Mutations para criar/atualizar dados
  const createNicho = useMutation({
    mutationFn: (data: CreateNichoRequest) => apiCall('/nichos', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nichos'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const updateNicho = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateNichoRequest> }) =>
      apiCall(`/nichos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nichos'] });
    },
  });

  const deleteNicho = useMutation({
    mutationFn: (id: string) => apiCall(`/nichos/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nichos'] });
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const createCategoria = useMutation({
    mutationFn: (data: CreateCategoriaRequest) => apiCall('/categorias', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const updateCategoria = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateCategoriaRequest> }) =>
      apiCall(`/categorias/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
    },
  });

  const deleteCategoria = useMutation({
    mutationFn: (id: string) => apiCall(`/categorias/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categorias'] });
      queryClient.invalidateQueries({ queryKey: ['prompts-base'] });
      queryClient.invalidateQueries({ queryKey: ['dados-coletados'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const uploadPromptBase = useMutation({
    mutationFn: ({ categoriaId, file }: { categoriaId: string; file: File }) => {
      const formData = new FormData();
      formData.append('categoria_id', categoriaId);
      formData.append('arquivo', file);
      return apiUpload('/prompts-base', formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts-base'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const createDadosColetados = useMutation({
    mutationFn: (data: Partial<DadosColetados>) => apiCall('/dados-coletados', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dados-coletados'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const updateDadosColetados = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<DadosColetados> }) =>
      apiCall(`/dados-coletados/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dados-coletados'] });
    },
  });

  const deleteDadosColetados = useMutation({
    mutationFn: (id: string) => apiCall(`/dados-coletados/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dados-coletados'] });
      queryClient.invalidateQueries({ queryKey: ['prompts-preenchidos'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  // Mutations para processamento
  const processarPreenchimento = useMutation({
    mutationFn: ({ categoriaId, dadosId }: { categoriaId: number; dadosId: number }) =>
      apiCall(`/processar/${categoriaId}/${dadosId}`, { method: 'POST' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts-preenchidos'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const processarLote = useMutation({
    mutationFn: (nichoId: number): Promise<ApiResponse<any>> =>
      apiCall(`/processar-lote/${nichoId}`, { method: 'POST' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts-preenchidos'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  // Funções para download
  const downloadPromptPreenchido = async (promptId: number): Promise<{
    id: number;
    conteudo: string;
    nome_arquivo: string;
    created_at: string;
  }> => {
    return apiCall(`/prompts-preenchidos/${promptId}/download`);
  };

  // Funções para validação
  const validarPrompt = async (categoriaId: number, conteudo: string) => {
    return apiCall('/validar-prompt', {
      method: 'POST',
      body: JSON.stringify({ categoria_id: categoriaId, conteudo }),
    });
  };

  const detectarLacunas = async (categoriaId: number) => {
    return apiCall(`/detectar-lacunas/${categoriaId}`);
  };

  return {
    // Queries
    getNichos,
    getCategorias,
    getPromptsBase,
    getDadosColetados,
    getPromptsPreenchidos,
    getStats,

    // Mutations - Nichos
    createNicho,
    updateNicho,
    deleteNicho,

    // Mutations - Categorias
    createCategoria,
    updateCategoria,
    deleteCategoria,

    // Mutations - Prompts
    uploadPromptBase,

    // Mutations - Dados Coletados
    createDadosColetados,
    updateDadosColetados,
    deleteDadosColetados,

    // Mutations - Processamento
    processarPreenchimento,
    processarLote,

    // Funções auxiliares
    downloadPromptPreenchido,
    validarPrompt,
    detectarLacunas,
  };
}; 