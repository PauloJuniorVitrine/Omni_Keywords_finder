/**
 * Testes Unitários - Hooks GraphQL Frontend
 * 
 * Tracing ID: TEST_GRAPHQL_HOOKS_2025_001
 * Data/Hora: 2025-01-27 18:30:00 UTC
 * Versão: 1.0
 * Status: 🚀 IMPLEMENTAÇÃO
 * 
 * Testes para os hooks GraphQL do frontend
 */

import { renderHook } from '@testing-library/react';

// Mock do fetch global
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock do localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Importa hooks para teste
import {
  useGraphQL,
  useGraphQLMutation,
  useNichos,
  useKeywords,
  clearGraphQLCache,
  getGraphQLCacheStats,
} from '../../../app/hooks/useGraphQL';

// =============================================================================
// MOCKS E UTILITÁRIOS
// =============================================================================

const mockGraphQLResponse = (data: any, errors?: any[]) => ({
  ok: true,
  json: () => Promise.resolve({ data, errors }),
});

const mockGraphQLError = (message: string) => ({
  ok: true,
  json: () => Promise.resolve({ 
    data: null, 
    errors: [{ message, locations: [], path: [] }] 
  }),
});

// =============================================================================
// TESTES PARA HOOKS BÁSICOS
// =============================================================================

describe('useGraphQL Hook', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockLocalStorage.getItem.mockReturnValue('mock-token');
  });

  afterEach(() => {
    clearGraphQLCache();
  });

  it('should execute query successfully', async () => {
    const mockData = { nichos: [{ id: '1', nome: 'Test Nicho' }] };
    mockFetch.mockResolvedValueOnce(mockGraphQLResponse(mockData));

    const { result } = renderHook(() =>
      useGraphQL('query { nichos { id nome } }')
    );

    // Aguarda a execução assíncrona
    await new Promise(resolve => setTimeout(resolve, 100));

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
  });

  it('should handle GraphQL errors', async () => {
    mockFetch.mockResolvedValueOnce(mockGraphQLError('GraphQL Error'));

    const { result } = renderHook(() =>
      useGraphQL('query { invalid }')
    );

    // Aguarda a execução assíncrona
    await new Promise(resolve => setTimeout(resolve, 100));

    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toBe('GraphQL Error');
  });
});

describe('useGraphQLMutation Hook', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockLocalStorage.getItem.mockReturnValue('mock-token');
  });

  it('should execute mutation successfully', async () => {
    const mockData = { 
      createNicho: { 
        nicho: { id: '1', nome: 'New Nicho' },
        success: true,
        message: 'Nicho created successfully'
      } 
    };
    mockFetch.mockResolvedValueOnce(mockGraphQLResponse(mockData));

    const { result } = renderHook(() =>
      useGraphQLMutation('mutation CreateNicho($input: NichoInput!) { createNicho(input: $input) { nicho { id nome } success message } }')
    );

    const mutationResult = await result.current.execute({
      input: { nome: 'New Nicho', descricao: 'Test', ativo: true }
    });

    expect(mutationResult.data).toEqual(mockData);
    expect(result.current.loading).toBe(false);
  });
});

describe('Specialized Hooks', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockLocalStorage.getItem.mockReturnValue('mock-token');
  });

  describe('useNichos', () => {
    it('should fetch nichos successfully', async () => {
      const mockData = {
        nichos: [
          { id: '1', nome: 'Nicho 1', descricao: 'Desc 1', ativo: true },
          { id: '2', nome: 'Nicho 2', descricao: 'Desc 2', ativo: false }
        ]
      };
      mockFetch.mockResolvedValueOnce(mockGraphQLResponse(mockData));

      const { result } = renderHook(() => useNichos());

      // Aguarda a execução assíncrona
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(result.current.data).toEqual(mockData);
    });
  });

  describe('useKeywords', () => {
    it('should fetch keywords with filters', async () => {
      const mockData = {
        keywords: [
          { id: '1', keyword: 'test keyword', volume: 1000, dificuldade: 0.5 }
        ]
      };
      mockFetch.mockResolvedValueOnce(mockGraphQLResponse(mockData));

      const filtros = { nicho_id: '1', volume_min: 500 };
      const { result } = renderHook(() => useKeywords(filtros));

      // Aguarda a execução assíncrona
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(result.current.data).toEqual(mockData);
    });
  });
});

describe('GraphQL Utilities', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('should clear cache', () => {
    clearGraphQLCache();
    const stats = getGraphQLCacheStats();

    expect(stats.size).toBe(0);
    expect(stats.keys).toHaveLength(0);
  });

  it('should get cache stats', () => {
    const stats = getGraphQLCacheStats();
    
    expect(stats).toHaveProperty('size');
    expect(stats).toHaveProperty('keys');
    expect(Array.isArray(stats.keys)).toBe(true);
  });
}); 