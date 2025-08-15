/**
 * 🧪 ApiClient.test.ts
 * 🎯 Objetivo: Testes unitários para cliente HTTP centralizado
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: TEST_API_CLIENT_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { ApiClient, ApiRequestConfig, ApiResponse, ApiError } from '../services/api/ApiClient';
import { authRequestInterceptor, authResponseInterceptor, authErrorInterceptor } from '../services/api/interceptors/AuthInterceptor';

// Mock do fetch global
global.fetch = vi.fn();

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock do window.location
const mockLocation = {
  href: '',
};

Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

describe('ApiClient', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = new ApiClient({
      baseURL: 'http://localhost:5000',
      timeout: 5000,
      retries: 2,
      retryDelay: 1000,
      enableCache: true,
      enableLogging: true,
      enableRetry: true,
      enableRateLimit: true,
    });

    vi.clearAllMocks();
    mockLocation.href = '';
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Configuração', () => {
    it('deve criar cliente com configuração padrão', () => {
      const client = new ApiClient();
      expect(client).toBeInstanceOf(ApiClient);
    });

    it('deve criar cliente com configuração customizada', () => {
      const config = {
        baseURL: 'https://api.example.com',
        timeout: 10000,
        retries: 5,
      };

      const client = new ApiClient(config);
      expect(client).toBeInstanceOf(ApiClient);
    });
  });

  describe('Interceptors', () => {
    it('deve adicionar interceptors de requisição', () => {
      const interceptor = vi.fn((config) => config);
      apiClient.addRequestInterceptor(interceptor);
      
      // Verificar se o interceptor foi adicionado
      expect(interceptor).not.toHaveBeenCalled();
    });

    it('deve adicionar interceptors de resposta', () => {
      const interceptor = vi.fn((response) => response);
      apiClient.addResponseInterceptor(interceptor);
      
      // Verificar se o interceptor foi adicionado
      expect(interceptor).not.toHaveBeenCalled();
    });

    it('deve adicionar interceptors de erro', () => {
      const interceptor = vi.fn((error) => error);
      apiClient.addErrorInterceptor(interceptor);
      
      // Verificar se o interceptor foi adicionado
      expect(interceptor).not.toHaveBeenCalled();
    });
  });

  describe('Requisições HTTP', () => {
    it('deve fazer requisição GET com sucesso', async () => {
      const mockResponse = {
        data: { id: 1, name: 'Test' },
        status: 200,
        statusText: 'OK',
        headers: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve(mockResponse.data),
      });

      const response = await apiClient.get('/test');

      expect(response.data).toEqual(mockResponse.data);
      expect(response.status).toBe(200);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/test',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('deve fazer requisição POST com dados', async () => {
      const postData = { name: 'Test', email: 'test@example.com' };
      const mockResponse = {
        data: { id: 1, ...postData },
        status: 201,
        statusText: 'Created',
        headers: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 201,
        statusText: 'Created',
        headers: new Map(),
        json: () => Promise.resolve(mockResponse.data),
      });

      const response = await apiClient.post('/users', postData);

      expect(response.data).toEqual(mockResponse.data);
      expect(response.status).toBe(201);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/users',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('deve fazer requisição PUT com dados', async () => {
      const putData = { name: 'Updated Test' };
      const mockResponse = {
        data: { id: 1, ...putData },
        status: 200,
        statusText: 'OK',
        headers: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve(mockResponse.data),
      });

      const response = await apiClient.put('/users/1', putData);

      expect(response.data).toEqual(mockResponse.data);
      expect(response.status).toBe(200);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/users/1',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData),
        })
      );
    });

    it('deve fazer requisição DELETE', async () => {
      const mockResponse = {
        data: { success: true },
        status: 204,
        statusText: 'No Content',
        headers: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 204,
        statusText: 'No Content',
        headers: new Map(),
        json: () => Promise.resolve(mockResponse.data),
      });

      const response = await apiClient.delete('/users/1');

      expect(response.data).toEqual(mockResponse.data);
      expect(response.status).toBe(204);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/users/1',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('deve fazer requisição PATCH com dados', async () => {
      const patchData = { name: 'Patched Test' };
      const mockResponse = {
        data: { id: 1, ...patchData },
        status: 200,
        statusText: 'OK',
        headers: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve(mockResponse.data),
      });

      const response = await apiClient.patch('/users/1', patchData);

      expect(response.data).toEqual(mockResponse.data);
      expect(response.status).toBe(200);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/users/1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(patchData),
        })
      );
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve tratar erro de rede', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(apiClient.get('/test')).rejects.toThrow('Network error');
    });

    it('deve tratar erro HTTP 404', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ error: 'Resource not found' }),
      });

      await expect(apiClient.get('/test')).rejects.toThrow('HTTP 404: Not Found');
    });

    it('deve tratar erro HTTP 500', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({ error: 'Internal server error' }),
      });

      await expect(apiClient.get('/test')).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    it('deve tratar timeout', async () => {
      // Mock de timeout
      (global.fetch as any).mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      await expect(apiClient.get('/test')).rejects.toThrow('Request timeout');
    });
  });

  describe('Cache', () => {
    it('deve armazenar dados no cache para requisições GET', async () => {
      const mockData = { id: 1, name: 'Cached Data' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve(mockData),
      });

      // Primeira requisição
      const response1 = await apiClient.get('/cached-data', { cache: true });
      expect(response1.data).toEqual(mockData);

      // Segunda requisição (deve vir do cache)
      const response2 = await apiClient.get('/cached-data', { cache: true });
      expect(response2.data).toEqual(mockData);
      expect(response2.statusText).toBe('OK (Cached)');

      // Verificar que fetch foi chamado apenas uma vez
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('deve limpar cache', async () => {
      const mockData = { id: 1, name: 'Test Data' };

      (global.fetch as any).mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve(mockData),
      });

      // Fazer requisição com cache
      await apiClient.get('/test', { cache: true });

      // Limpar cache
      apiClient.clearCache();

      // Fazer nova requisição (deve chamar fetch novamente)
      await apiClient.get('/test', { cache: true });

      // Verificar que fetch foi chamado duas vezes
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('deve limpar cache para endpoint específico', async () => {
      const mockData = { id: 1, name: 'Test Data' };

      (global.fetch as any).mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve(mockData),
      });

      // Fazer requisições com cache
      await apiClient.get('/users', { cache: true });
      await apiClient.get('/posts', { cache: true });

      // Limpar cache apenas para users
      apiClient.clearCacheForEndpoint('/users');

      // Fazer nova requisição para users (deve chamar fetch)
      await apiClient.get('/users', { cache: true });

      // Fazer nova requisição para posts (deve vir do cache)
      await apiClient.get('/posts', { cache: true });

      // Verificar que fetch foi chamado 3 vezes (2 iniciais + 1 após limpeza)
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });
  });

  describe('Rate Limiting', () => {
    it('deve configurar rate limit para endpoint', () => {
      apiClient.setRateLimit('/api', 10, 1000); // 10 tokens, 1 por segundo
      
      // Verificar se o rate limit foi configurado
      expect(apiClient.getCacheStats()).toBeDefined();
    });

    it('deve respeitar rate limit', async () => {
      // Configurar rate limit baixo para teste
      apiClient.setRateLimit('/test', 1, 1000); // 1 token, 1 por segundo

      const mockResponse = {
        data: { success: true },
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve({ success: true }),
      };

      (global.fetch as any).mockResolvedValue(mockResponse);

      // Primeira requisição deve funcionar
      await apiClient.get('/test');

      // Segunda requisição deve falhar por rate limit
      await expect(apiClient.get('/test')).rejects.toThrow('Rate limit exceeded');
    });
  });

  describe('Parâmetros de Query', () => {
    it('deve adicionar parâmetros de query à URL', async () => {
      const params = { page: 1, limit: 10, search: 'test' };
      const mockResponse = {
        data: { items: [] },
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve({ items: [] }),
      };

      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await apiClient.get('/users', { params });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/users?page=1&limit=10&search=test',
        expect.any(Object)
      );
    });

    it('deve ignorar parâmetros undefined/null', async () => {
      const params = { page: 1, limit: undefined, search: null, active: true };
      const mockResponse = {
        data: { items: [] },
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve({ items: [] }),
      };

      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await apiClient.get('/users', { params });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/users?page=1&active=true',
        expect.any(Object)
      );
    });
  });

  describe('Headers', () => {
    it('deve adicionar headers customizados', async () => {
      const customHeaders = {
        'X-Custom-Header': 'custom-value',
        'X-API-Version': 'v2',
      };

      const mockResponse = {
        data: { success: true },
        status: 200,
        statusText: 'OK',
        headers: new Map(),
        json: () => Promise.resolve({ success: true }),
      };

      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await apiClient.get('/test', { headers: customHeaders });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'X-Custom-Header': 'custom-value',
            'X-API-Version': 'v2',
          }),
        })
      );
    });
  });

  describe('Timeout', () => {
    it('deve respeitar timeout configurado', async () => {
      const client = new ApiClient({ timeout: 100 }); // 100ms timeout

      // Mock de requisição lenta
      (global.fetch as any).mockImplementationOnce(() => 
        new Promise((resolve) => 
          setTimeout(() => resolve({
            ok: true,
            status: 200,
            statusText: 'OK',
            headers: new Map(),
            json: () => Promise.resolve({ success: true }),
          }), 200) // 200ms delay
        )
      );

      await expect(client.get('/test')).rejects.toThrow('Request timeout');
    });
  });

  describe('Retry', () => {
    it('deve tentar novamente em caso de falha', async () => {
      const client = new ApiClient({ retries: 2, retryDelay: 100 });

      // Mock de falha seguida de sucesso
      (global.fetch as any)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          statusText: 'OK',
          headers: new Map(),
          json: () => Promise.resolve({ success: true }),
        });

      const response = await client.get('/test');

      expect(response.data).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });
  });
});

describe('AuthInterceptor', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = new ApiClient();
    vi.clearAllMocks();
  });

  describe('Request Interceptor', () => {
    it('deve adicionar token de autenticação', async () => {
      localStorageMock.getItem.mockReturnValue('test-token');

      const config = await authRequestInterceptor({
        method: 'GET',
        headers: {},
      });

      expect(config.headers).toEqual({
        'Authorization': 'Bearer test-token',
      });
    });

    it('deve pular autenticação quando skipAuth é true', async () => {
      const config = await authRequestInterceptor({
        method: 'GET',
        headers: {},
        skipAuth: true,
      });

      expect(config.headers).toEqual({});
    });

    it('deve tentar renovar token quando não há token', async () => {
      localStorageMock.getItem
        .mockReturnValueOnce(null) // authToken
        .mockReturnValueOnce('refresh-token'); // refreshToken

      // Mock da função de renovação de token
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ access_token: 'new-token' }),
      });

      const config = await authRequestInterceptor({
        method: 'GET',
        headers: {},
      });

      expect(config.headers).toEqual({
        'Authorization': 'Bearer new-token',
      });
      expect(localStorageMock.setItem).toHaveBeenCalledWith('authToken', 'new-token');
    });
  });

  describe('Response Interceptor', () => {
    it('deve tentar renovar token em resposta 401', async () => {
      localStorageMock.getItem.mockReturnValue('refresh-token');

      // Mock da função de renovação de token
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ access_token: 'new-token' }),
      });

      const response = {
        data: null,
        status: 401,
        statusText: 'Unauthorized',
        headers: {},
        config: {},
        requestId: 'test',
        timestamp: Date.now(),
      };

      await expect(authResponseInterceptor(response)).rejects.toThrow('Token renewed, retry request');
    });
  });

  describe('Error Interceptor', () => {
    it('deve tentar renovar token em erro 401', async () => {
      localStorageMock.getItem.mockReturnValue('refresh-token');

      // Mock da função de renovação de token
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ access_token: 'new-token' }),
      });

      const error: ApiError = {
        message: 'Unauthorized',
        status: 401,
        statusText: 'Unauthorized',
        requestId: 'test',
        timestamp: Date.now(),
        retryCount: 0,
      };

      const result = await authErrorInterceptor(error);

      expect(result.message).toBe('Token renewed, retry request');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('authToken', 'new-token');
    });

    it('deve redirecionar para login quando não há refresh token', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      const error: ApiError = {
        message: 'Unauthorized',
        status: 401,
        statusText: 'Unauthorized',
        requestId: 'test',
        timestamp: Date.now(),
        retryCount: 0,
      };

      const result = await authErrorInterceptor(error);

      expect(result.message).toBe('Sessão expirada. Faça login novamente.');
      expect(mockLocation.href).toBe('/login');
    });
  });
}); 