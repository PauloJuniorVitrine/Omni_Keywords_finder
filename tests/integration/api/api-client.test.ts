/**
 * Testes de Integração para API Client
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 9.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { ApiClient } from '../../../app/services/api/ApiClient';
import { globalCache } from '../../../app/services/cache/intelligent-cache';
import { cacheInvalidationManager } from '../../../app/services/cache/cache-invalidation';

// Mock do fetch global
global.fetch = jest.fn();

// Mock do cache global
jest.mock('../../../app/services/cache/intelligent-cache', () => ({
  globalCache: {
    get: jest.fn(),
    set: jest.fn(),
    delete: jest.fn()
  }
}));

// Mock do cache invalidation manager
jest.mock('../../../app/services/cache/cache-invalidation', () => ({
  cacheInvalidationManager: {
    processEvent: jest.fn()
  }
}));

describe('ApiClient Integration Tests', () => {
  let apiClient: ApiClient;
  const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    jest.clearAllMocks();
    apiClient = new ApiClient({
      baseURL: 'https://api.example.com',
      timeout: 5000,
      retries: 3
    });
  });

  describe('Configuração e inicialização', () => {
    it('deve configurar cliente com opções corretas', () => {
      expect(apiClient.getBaseURL()).toBe('https://api.example.com');
      expect(apiClient.getTimeout()).toBe(5000);
      expect(apiClient.getRetries()).toBe(3);
    });

    it('deve configurar headers padrão', () => {
      const headers = apiClient.getDefaultHeaders();
      expect(headers['Content-Type']).toBe('application/json');
      expect(headers['Accept']).toBe('application/json');
    });

    it('deve configurar interceptors', () => {
      const requestInterceptors = apiClient.getRequestInterceptors();
      const responseInterceptors = apiClient.getResponseInterceptors();
      
      expect(requestInterceptors.length).toBeGreaterThan(0);
      expect(responseInterceptors.length).toBeGreaterThan(0);
    });
  });

  describe('Requisições HTTP básicas', () => {
    it('deve fazer requisição GET com sucesso', async () => {
      const mockResponse = { id: 1, name: 'Test User' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      const response = await apiClient.get('/users/1');

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/users/1',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(response.data).toEqual(mockResponse);
      expect(response.status).toBe(200);
      expect(response.success).toBe(true);
    });

    it('deve fazer requisição POST com dados', async () => {
      const postData = { name: 'New User', email: 'test@example.com' };
      const mockResponse = { id: 2, ...postData };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      const response = await apiClient.post('/users', postData);

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/users',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(response.data).toEqual(mockResponse);
      expect(response.status).toBe(201);
    });

    it('deve fazer requisição PUT com dados', async () => {
      const putData = { name: 'Updated User' };
      const mockResponse = { id: 1, ...putData };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      const response = await apiClient.put('/users/1', putData);

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/users/1',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData)
        })
      );

      expect(response.data).toEqual(mockResponse);
    });

    it('deve fazer requisição DELETE', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => null,
        headers: new Headers()
      } as Response);

      const response = await apiClient.delete('/users/1');

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/users/1',
        expect.objectContaining({
          method: 'DELETE'
        })
      );

      expect(response.status).toBe(204);
    });

    it('deve fazer requisição PATCH com dados', async () => {
      const patchData = { name: 'Patched User' };
      const mockResponse = { id: 1, ...patchData };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      const response = await apiClient.patch('/users/1', patchData);

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/users/1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(patchData)
        })
      );

      expect(response.data).toEqual(mockResponse);
    });
  });

  describe('Tratamento de erros', () => {
    it('deve tratar erro 400 (Bad Request)', async () => {
      const errorResponse = { error: 'Invalid data', field: 'email' };
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => errorResponse,
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      try {
        await apiClient.post('/users', { email: 'invalid' });
        fail('Deveria ter lançado erro');
      } catch (error: any) {
        expect(error.status).toBe(400);
        expect(error.message).toBe('Bad Request');
        expect(error.data).toEqual(errorResponse);
      }
    });

    it('deve tratar erro 401 (Unauthorized)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({ error: 'Invalid token' }),
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      try {
        await apiClient.get('/protected');
        fail('Deveria ter lançado erro');
      } catch (error: any) {
        expect(error.status).toBe(401);
        expect(error.message).toBe('Unauthorized');
      }
    });

    it('deve tratar erro 404 (Not Found)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ error: 'Resource not found' }),
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      try {
        await apiClient.get('/users/999');
        fail('Deveria ter lançado erro');
      } catch (error: any) {
        expect(error.status).toBe(404);
        expect(error.message).toBe('Not Found');
      }
    });

    it('deve tratar erro 500 (Internal Server Error)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' }),
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      try {
        await apiClient.get('/users');
        fail('Deveria ter lançado erro');
      } catch (error: any) {
        expect(error.status).toBe(500);
        expect(error.message).toBe('Internal Server Error');
      }
    });

    it('deve tratar erro de rede', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      try {
        await apiClient.get('/users');
        fail('Deveria ter lançado erro');
      } catch (error: any) {
        expect(error.message).toBe('Network error');
        expect(error.isNetworkError).toBe(true);
      }
    });

    it('deve tratar timeout', async () => {
      const timeoutClient = new ApiClient({
        baseURL: 'https://api.example.com',
        timeout: 100
      });

      mockFetch.mockImplementationOnce(() => {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              ok: true,
              status: 200,
              json: async () => ({}),
              headers: new Headers()
            } as Response);
          }, 200);
        });
      });

      try {
        await timeoutClient.get('/users');
        fail('Deveria ter lançado erro de timeout');
      } catch (error: any) {
        expect(error.message).toContain('timeout');
        expect(error.isTimeoutError).toBe(true);
      }
    });
  });

  describe('Retry automático', () => {
    it('deve tentar novamente em caso de erro 500', async () => {
      const retryClient = new ApiClient({
        baseURL: 'https://api.example.com',
        retries: 2
      });

      // Primeira tentativa falha
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' }),
        headers: new Headers()
      } as Response);

      // Segunda tentativa falha
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' }),
        headers: new Headers()
      } as Response);

      // Terceira tentativa sucesso
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
        headers: new Headers()
      } as Response);

      const response = await retryClient.get('/users');

      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(response.success).toBe(true);
    });

    it('deve parar de tentar após número máximo de tentativas', async () => {
      const retryClient = new ApiClient({
        baseURL: 'https://api.example.com',
        retries: 2
      });

      // Todas as tentativas falham
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' }),
        headers: new Headers()
      } as Response);

      try {
        await retryClient.get('/users');
        fail('Deveria ter lançado erro após todas as tentativas');
      } catch (error: any) {
        expect(mockFetch).toHaveBeenCalledTimes(3); // 1 inicial + 2 retries
        expect(error.status).toBe(500);
      }
    });
  });

  describe('Cache integration', () => {
    it('deve usar cache para requisições GET', async () => {
      const cachedData = { id: 1, name: 'Cached User' };
      (globalCache.get as jest.Mock).mockReturnValue(cachedData);

      const response = await apiClient.get('/users/1', { useCache: true });

      expect(globalCache.get).toHaveBeenCalledWith('api:GET:/users/1');
      expect(response.data).toEqual(cachedData);
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('deve armazenar resposta no cache', async () => {
      const mockResponse = { id: 1, name: 'Test User' };
      (globalCache.get as jest.Mock).mockReturnValue(null);
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' })
      } as Response);

      await apiClient.get('/users/1', { useCache: true });

      expect(globalCache.set).toHaveBeenCalledWith(
        'api:GET:/users/1',
        mockResponse,
        expect.any(Number)
      );
    });

    it('deve invalidar cache em requisições POST', async () => {
      const postData = { name: 'New User' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({ id: 2, ...postData }),
        headers: new Headers()
      } as Response);

      await apiClient.post('/users', postData);

      expect(cacheInvalidationManager.processEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'api:post',
          resource: '/users'
        })
      );
    });
  });

  describe('Interceptors', () => {
    it('deve executar request interceptors', async () => {
      const requestInterceptor = jest.fn((config) => {
        config.headers['X-Custom-Header'] = 'test';
        return config;
      });

      apiClient.addRequestInterceptor(requestInterceptor);

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers()
      } as Response);

      await apiClient.get('/users');

      expect(requestInterceptor).toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Custom-Header': 'test'
          })
        })
      );
    });

    it('deve executar response interceptors', async () => {
      const responseInterceptor = jest.fn((response) => {
        response.data.intercepted = true;
        return response;
      });

      apiClient.addResponseInterceptor(responseInterceptor);

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 1 }),
        headers: new Headers()
      } as Response);

      const response = await apiClient.get('/users');

      expect(responseInterceptor).toHaveBeenCalled();
      expect(response.data.intercepted).toBe(true);
    });
  });

  describe('Upload de arquivos', () => {
    it('deve fazer upload de arquivo', async () => {
      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const formData = new FormData();
      formData.append('file', file);

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ url: 'https://example.com/uploads/test.txt' }),
        headers: new Headers()
      } as Response);

      const response = await apiClient.upload('/upload', formData);

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/upload',
        expect.objectContaining({
          method: 'POST',
          body: formData
        })
      );

      expect(response.data.url).toBe('https://example.com/uploads/test.txt');
    });

    it('deve fazer upload com progress callback', async () => {
      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const formData = new FormData();
      formData.append('file', file);

      const progressCallback = jest.fn();

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
        headers: new Headers()
      } as Response);

      await apiClient.upload('/upload', formData, { onProgress: progressCallback });

      expect(mockFetch).toHaveBeenCalled();
    });
  });

  describe('WebSocket integration', () => {
    it('deve configurar WebSocket connection', () => {
      const wsClient = apiClient.createWebSocketClient('/ws');

      expect(wsClient).toBeDefined();
      expect(typeof wsClient.connect).toBe('function');
      expect(typeof wsClient.disconnect).toBe('function');
      expect(typeof wsClient.send).toBe('function');
    });
  });

  describe('Rate limiting', () => {
    it('deve respeitar rate limiting', async () => {
      const rateLimitedClient = new ApiClient({
        baseURL: 'https://api.example.com',
        rateLimit: { requests: 2, window: 1000 }
      });

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers()
      } as Response);

      // Primeiras duas requisições devem funcionar
      await rateLimitedClient.get('/users');
      await rateLimitedClient.get('/users');

      // Terceira requisição deve ser rate limited
      try {
        await rateLimitedClient.get('/users');
        fail('Deveria ter sido rate limited');
      } catch (error: any) {
        expect(error.message).toContain('rate limit');
      }
    });
  });

  describe('Métricas e logging', () => {
    it('deve registrar métricas de requisição', async () => {
      const startTime = Date.now();
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers()
      } as Response);

      await apiClient.get('/users');

      const metrics = apiClient.getMetrics();
      expect(metrics.totalRequests).toBe(1);
      expect(metrics.successfulRequests).toBe(1);
      expect(metrics.averageResponseTime).toBeGreaterThan(0);
    });

    it('deve registrar erros nas métricas', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' }),
        headers: new Headers()
      } as Response);

      try {
        await apiClient.get('/users');
      } catch (error) {
        // Erro esperado
      }

      const metrics = apiClient.getMetrics();
      expect(metrics.totalRequests).toBe(1);
      expect(metrics.failedRequests).toBe(1);
      expect(metrics.errorRate).toBe(1);
    });
  });
}); 