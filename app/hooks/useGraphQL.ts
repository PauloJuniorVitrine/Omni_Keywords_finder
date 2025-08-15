/**
 * Hook GraphQL - Omni Keywords Finder
 * 
 * Este hook implementa cliente GraphQL otimizado com:
 * - Cache inteligente
 * - Query deduplication
 * - Error handling
 * - Type safety
 * - Optimistic updates
 * 
 * Autor: Sistema Omni Keywords Finder
 * Data: 2024-12-19
 * Versão: 1.0.0
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// TIPOS
// =============================================================================

interface GraphQLRequest {
  query: string;
  variables?: Record<string, any>;
  operationName?: string;
}

interface GraphQLResponse<T = any> {
  data?: T;
  errors?: GraphQLError[];
}

interface GraphQLError {
  message: string;
  locations?: Array<{ line: number; column: number }>;
  path?: string[];
  extensions?: Record<string, any>;
}

interface GraphQLConfig {
  endpoint: string;
  headers?: Record<string, string>;
  timeout?: number;
  cacheTime?: number;
  retryCount?: number;
  retryDelay?: number;
}

interface UseGraphQLOptions {
  skip?: boolean;
  pollInterval?: number;
  errorPolicy?: 'none' | 'ignore' | 'all';
  fetchPolicy?: 'cache-first' | 'cache-and-network' | 'network-only' | 'no-cache';
}

// =============================================================================
// CACHE E UTILITÁRIOS
// =============================================================================

// Cache global para queries GraphQL
const graphqlCache = new Map<string, { data: any; timestamp: number; ttl: number }>();

// Queries em andamento para deduplication
const pendingQueries = new Map<string, Promise<any>>();

// Configuração padrão
const DEFAULT_CONFIG: GraphQLConfig = {
  endpoint: '/graphql/query',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  cacheTime: 5 * 60 * 1000, // 5 minutos
  retryCount: 3,
  retryDelay: 1000,
};

// Utilitários
const generateCacheKey = (request: GraphQLRequest): string => {
  return JSON.stringify({
    query: request.query,
    variables: request.variables || {},
    operationName: request.operationName || '',
  });
};

const isCacheValid = (cacheEntry: { data: any; timestamp: number; ttl: number }): boolean => {
  return Date.now() - cacheEntry.timestamp < cacheEntry.ttl;
};

const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

const exponentialBackoff = (attempt: number, baseDelay: number): number => {
  return Math.min(baseDelay * Math.pow(2, attempt), 30000);
};

// =============================================================================
// CLIENTE GRAPHQL
// =============================================================================

class GraphQLClient {
  private config: GraphQLConfig;
  private abortController: AbortController | null = null;

  constructor(config: Partial<GraphQLConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  async execute<T = any>(
    request: GraphQLRequest,
    options: UseGraphQLOptions = {}
  ): Promise<GraphQLResponse<T>> {
    const cacheKey = generateCacheKey(request);
    
    // Verifica cache primeiro
    if (options.fetchPolicy !== 'network-only' && options.fetchPolicy !== 'no-cache') {
      const cached = graphqlCache.get(cacheKey);
      if (cached && isCacheValid(cached)) {
        return { data: cached.data };
      }
    }

    // Verifica se já existe uma query pendente (deduplication)
    if (pendingQueries.has(cacheKey)) {
      return await pendingQueries.get(cacheKey)!;
    }

    // Cria promise para deduplication
    const queryPromise = this.executeRequest<T>(request, options);
    pendingQueries.set(cacheKey, queryPromise);

    try {
      const result = await queryPromise;
      
      // Salva no cache se bem-sucedido
      if (result.data && options.fetchPolicy !== 'no-cache') {
        graphqlCache.set(cacheKey, {
          data: result.data,
          timestamp: Date.now(),
          ttl: this.config.cacheTime!,
        });
      }
      
      return result;
    } finally {
      pendingQueries.delete(cacheKey);
    }
  }

  private async executeRequest<T = any>(
    request: GraphQLRequest,
    options: UseGraphQLOptions = {}
  ): Promise<GraphQLResponse<T>> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.config.retryCount!; attempt++) {
      try {
        // Cancela request anterior se existir
        if (this.abortController) {
          this.abortController.abort();
        }

        this.abortController = new AbortController();

        const response = await fetch(this.config.endpoint, {
          method: 'POST',
          headers: {
            ...this.config.headers,
            'Authorization': `Bearer ${this.getAuthToken()}`,
          },
          body: JSON.stringify(request),
          signal: this.abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result: GraphQLResponse<T> = await response.json();

        // Trata erros GraphQL
        if (result.errors && result.errors.length > 0) {
          if (options.errorPolicy === 'ignore') {
            return { data: result.data };
          } else if (options.errorPolicy === 'all') {
            return result;
          } else {
            throw new Error(result.errors[0].message);
          }
        }

        return result;

      } catch (error) {
        lastError = error as Error;

        // Se foi cancelado, não tenta novamente
        if (error instanceof Error && error.name === 'AbortError') {
          throw error;
        }

        // Se não é a última tentativa, aguarda antes de tentar novamente
        if (attempt < this.config.retryCount!) {
          const delay = exponentialBackoff(attempt, this.config.retryDelay!);
          await sleep(delay);
        }
      }
    }

    throw lastError || new Error('GraphQL request failed after all retries');
  }

  private getAuthToken(): string {
    // Implementar lógica para obter token de autenticação
    // Por exemplo, do localStorage ou contexto de autenticação
    return localStorage.getItem('auth_token') || '';
  }

  abort(): void {
    if (this.abortController) {
      this.abortController.abort();
    }
  }

  clearCache(pattern?: string): void {
    if (pattern) {
      for (const key of graphqlCache.keys()) {
        if (key.includes(pattern)) {
          graphqlCache.delete(key);
        }
      }
    } else {
      graphqlCache.clear();
    }
  }

  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: graphqlCache.size,
      keys: Array.from(graphqlCache.keys()),
    };
  }
}

// Instância global do cliente
const graphqlClient = new GraphQLClient();

// =============================================================================
// HOOKS
// =============================================================================

export function useGraphQL<T = any>(
  query: string,
  variables?: Record<string, any>,
  options: UseGraphQLOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [refetchCount, setRefetchCount] = useState(0);

  const request: GraphQLRequest = {
    query,
    variables,
  };

  const executeQuery = useCallback(async () => {
    if (options.skip) return;

    setLoading(true);
    setError(null);

    try {
      const result = await graphqlClient.execute<T>(request, options);
      setData(result.data || null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [query, JSON.stringify(variables), options.skip, options.fetchPolicy]);

  // Executa query na montagem e quando dependências mudam
  useEffect(() => {
    executeQuery();
  }, [executeQuery, refetchCount]);

  // Polling
  useEffect(() => {
    if (!options.pollInterval || options.skip) return;

    const interval = setInterval(() => {
      setRefetchCount(prev => prev + 1);
    }, options.pollInterval);

    return () => clearInterval(interval);
  }, [options.pollInterval, options.skip]);

  const refetch = useCallback(() => {
    setRefetchCount(prev => prev + 1);
  }, []);

  return { data, loading, error, refetch };
}

export function useGraphQLMutation<T = any, V = Record<string, any>>(
  mutation: string
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (variables?: V) => {
    setLoading(true);
    setError(null);

    try {
      const result = await graphqlClient.execute<T>({
        query: mutation,
        variables: variables as Record<string, any>,
      });
      
      setData(result.data || null);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [mutation]);

  return { execute, data, loading, error };
}

export function useGraphQLSubscription<T = any>(
  subscription: string,
  variables?: Record<string, any>
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Implementação básica de subscription
    // Em produção, usar WebSocket ou Server-Sent Events
    const eventSource = new EventSource(`/graphql/subscription?query=${encodeURIComponent(subscription)}&variables=${encodeURIComponent(JSON.stringify(variables || {}))}`);

    eventSource.onmessage = (event) => {
      try {
        const result = JSON.parse(event.data);
        setData(result.data);
        setLoading(false);
      } catch (err) {
        setError(err as Error);
        setLoading(false);
      }
    };

    eventSource.onerror = (err) => {
      setError(new Error('Subscription error'));
      setLoading(false);
    };

    return () => {
      eventSource.close();
    };
  }, [subscription, JSON.stringify(variables)]);

  return { data, loading, error };
}

// =============================================================================
// HOOKS ESPECIALIZADOS
// =============================================================================

export function useNichos(options: UseGraphQLOptions = {}) {
  const query = `
    query GetNichos($ativo: Boolean) {
      nichos(ativo: $ativo) {
        id
        nome
        descricao
        ativo
        dataCriacao
        categorias {
          id
          nome
          descricao
          ativo
        }
      }
    }
  `;

  return useGraphQL(query, {}, options);
}

export function useKeywords(filtros?: any, options: UseGraphQLOptions = {}) {
  const query = `
    query GetKeywords($filtros: KeywordFilterInput) {
      keywords(filtros: $filtros) {
        id
        keyword
        volume
        dificuldade
        cpc
        categoria
        nicho
        dataColeta
        score
      }
    }
  `;

  return useGraphQL(query, { filtros }, options);
}

export function useExecucoes(nichoId?: string, options: UseGraphQLOptions = {}) {
  const query = `
    query GetExecucoes($nichoId: ID, $limit: Int, $offset: Int) {
      execucoes(nichoId: $nichoId, limit: $limit, offset: $offset) {
        id
        nichoId
        categoriaId
        status
        dataInicio
        dataFim
        parametros
        resultado
      }
    }
  `;

  return useGraphQL(query, { nichoId, limit: 20, offset: 0 }, options);
}

export function useBusinessMetrics(tipo?: string, periodo?: string, options: UseGraphQLOptions = {}) {
  const query = `
    query GetBusinessMetrics($tipo: String, $periodo: String) {
      businessMetrics(tipo: $tipo, periodo: $periodo) {
        id
        nome
        valor
        tipo
        periodo
        dataCalculo
        tendencia
      }
    }
  `;

  return useGraphQL(query, { tipo, periodo }, options);
}

// =============================================================================
// MUTATIONS ESPECIALIZADAS
// =============================================================================

export function useCreateNicho() {
  const mutation = `
    mutation CreateNicho($input: NichoInput!) {
      createNicho(input: $input) {
        nicho {
          id
          nome
          descricao
          ativo
        }
        success
        message
      }
    }
  `;

  return useGraphQLMutation(mutation);
}

export function useCreateExecucao() {
  const mutation = `
    mutation CreateExecucao($input: ExecucaoInput!) {
      createExecucao(input: $input) {
        execucao {
          id
          nichoId
          status
          dataInicio
        }
        success
        message
      }
    }
  `;

  return useGraphQLMutation(mutation);
}

// =============================================================================
// UTILITÁRIOS
// =============================================================================

export const clearGraphQLCache = (pattern?: string) => {
  graphqlClient.clearCache(pattern);
};

export const getGraphQLCacheStats = () => {
  return graphqlClient.getCacheStats();
};

export const abortGraphQLRequests = () => {
  graphqlClient.abort();
};

// Exporta tipos
export type {
  GraphQLRequest,
  GraphQLResponse,
  GraphQLError,
  GraphQLConfig,
  UseGraphQLOptions,
}; 