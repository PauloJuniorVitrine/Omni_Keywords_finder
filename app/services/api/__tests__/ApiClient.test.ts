/**
 * Testes para ApiClient
 * 
 * Prompt: Implementação de testes para APIs críticas
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_API_CLIENT_001
 * 
 * Testes baseados APENAS no código real do ApiClient.ts
 */

import { ApiClient } from '../ApiClient';

// Mock do fetch global
global.fetch = jest.fn();

describe('ApiClient', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    jest.clearAllMocks();
    apiClient = new ApiClient({
      baseURL: 'https://api.example.com',
      timeout: 5000,
      retries: 2,
      retryDelay: 1000
    });
  });

  describe('Configuração Inicial', () => {
    it('deve inicializar com configurações padrão', () => {
      const client = new ApiClient({ baseURL: 'https://api.example.com' });

      expect(client.getAuthToken()).toBeNull();
    });

    it('deve inicializar com token de autenticação', () => {
      const token = 'auth-token-123';
      const client = new ApiClient({
        baseURL: 'https://api.example.com',
        authToken: token
      });

      expect(client.getAuthToken()).toBe(token);
    });

    it('deve definir configurações customizadas', () => {
      const config = {
        baseURL: 'https://custom-api.com',
        timeout: 10000,
        retries: 5,
        retryDelay: 2000
      };

      const client = new ApiClient(config);

      expect(client.getAuthToken()).toBeNull();
    });
  });

  describe('Gerenciamento de Token', () => {
    it('deve definir token de autenticação', () => {
      const token = 'new-token-456';
      
      apiClient.setAuthToken(token);

      expect(apiClient.getAuthToken()).toBe(token);
    });

    it('deve remover token de autenticação', () => {
      apiClient.setAuthToken('some-token');
      apiClient.setAuthToken(null);

      expect(apiClient.getAuthToken()).toBeNull();
    });
  });

  describe('Requisições HTTP - GET', () => {
    it('deve fazer requisição GET com sucesso', async () => {
      const mockResponse = {
        data: { users: [{ id: 1, name: 'John' }] },
        status: 200,
        success: true
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });

      const result = await apiClient.get('/users');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/users',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );
    });

    it('deve incluir token de autenticação nos headers', async () => {
      const token = 'auth-token-123';
      apiClient.setAuthToken(token);

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: {} })
      });

      await apiClient.get('/protected');

      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/protected',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${token}`
          })
        })
      );
    });

    it('deve incluir headers customizados', async () => {
      const customHeaders = {
        'X-Custom-Header': 'custom-value',
        'Accept': 'application/xml'
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: {} })
      });

      await apiClient.get('/users', { headers: customHeaders });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/users',
        expect.objectContaining({
          headers: expect.objectContaining(customHeaders)
        })
      );
    });
  });

  describe('Requisições HTTP - POST', () => {
    it('deve fazer requisição POST com dados', async () => {
      const postData = { name: 'John', email: 'john@example.com' };
      const mockResponse = {
        data: { id: 1, ...postData },
        status: 201,
        success: true
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => mockResponse
      });

      const result = await apiClient.post('/users', postData);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/users',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData)
        })
      );
    });

    it('deve fazer requisição POST sem dados', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: {} })
      });

      await apiClient.post('/users');

      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/users',
        expect.objectContaining({
          method: 'POST',
          body: undefined
        })
      );
    });
  });

  describe('Requisições HTTP - PUT', () => {
    it('deve fazer requisição PUT com dados', async () => {
      const putData = { name: 'John Updated', email: 'john.updated@example.com' };
      const mockResponse = {
        data: { id: 1, ...putData },
        status: 200,
        success: true
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });

      const result = await apiClient.put('/users/1', putData);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/users/1',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData)
        })
      );
    });
  });

  describe('Requisições HTTP - PATCH', () => {
    it('deve fazer requisição PATCH com dados', async () => {
      const patchData = { name: 'John Updated' };
      const mockResponse = {
        data: { id: 1, name: 'John Updated' },
        status: 200,
        success: true
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });

      const result = await apiClient.patch('/users/1', patchData);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/users/1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(patchData)
        })
      );
    });
  });

  describe('Requisições HTTP - DELETE', () => {
    it('deve fazer requisição DELETE', async () => {
      const mockResponse = {
        data: null,
        status: 204,
        success: true
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 204,
        json: async () => mockResponse
      });

      const result = await apiClient.delete('/users/1');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/users/1',
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });
  });

  describe('Upload de Arquivos', () => {
    it('deve fazer upload de arquivo com progresso', async () => {
      const file = new File(['file content'], 'test.txt', { type: 'text/plain' });
      const onProgress = jest.fn();

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: { fileId: '123' } })
      });

      const result = await apiClient.uploadFile('/upload', file, onProgress);

      expect(result).toEqual({ success: true, data: { fileId: '123' } });
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/upload',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      );
    });

    it('deve fazer upload de arquivo sem callback de progresso', async () => {
      const file = new File(['file content'], 'test.txt', { type: 'text/plain' });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: { fileId: '123' } })
      });

      const result = await apiClient.uploadFile('/upload', file);

      expect(result).toEqual({ success: true, data: { fileId: '123' } });
    });
  });

  describe('Download de Arquivos', () => {
    it('deve fazer download de arquivo', async () => {
      const mockBlob = new Blob(['file content'], { type: 'text/plain' });
      
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        blob: async () => mockBlob
      });

      // Mock do createObjectURL e revokeObjectURL
      const mockCreateObjectURL = jest.fn().mockReturnValue('blob:mock-url');
      const mockRevokeObjectURL = jest.fn();
      
      Object.defineProperty(window, 'URL', {
        value: {
          createObjectURL: mockCreateObjectURL,
          revokeObjectURL: mockRevokeObjectURL
        }
      });

      // Mock do document.createElement
      const mockLink = {
        href: '',
        download: '',
        click: jest.fn()
      };
      
      jest.spyOn(document, 'createElement').mockReturnValue(mockLink as any);

      await apiClient.downloadFile('/download/file.pdf', 'downloaded-file.pdf');

      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.example.com/download/file.pdf',
        expect.objectContaining({
          method: 'GET'
        })
      );
    });
  });

  describe('Retry e Timeout', () => {
    it('deve tentar novamente em caso de falha', async () => {
      const mockResponse = { success: true, data: {} };

      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValue({
          ok: true,
          status: 200,
          json: async () => mockResponse
        });

      const result = await apiClient.get('/users');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('deve falhar após número máximo de tentativas', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(apiClient.get('/users')).rejects.toThrow('Network error');
      expect(global.fetch).toHaveBeenCalledTimes(3); // 1 tentativa + 2 retries
    });

    it('deve respeitar timeout configurado', async () => {
      const slowResponse = new Promise(resolve => 
        setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 10000)
      );

      (global.fetch as jest.Mock).mockReturnValue(slowResponse);

      await expect(apiClient.get('/slow-endpoint')).rejects.toThrow();
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve tratar erro 401 - Não autorizado', async () => {
      const onUnauthorized = jest.fn();
      apiClient = new ApiClient({
        baseURL: 'https://api.example.com',
        onUnauthorized
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ success: false, message: 'Unauthorized' })
      });

      await expect(apiClient.get('/protected')).rejects.toThrow();
      expect(onUnauthorized).toHaveBeenCalled();
    });

    it('deve tratar erro 403 - Proibido', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ success: false, message: 'Forbidden' })
      });

      await expect(apiClient.get('/forbidden')).rejects.toThrow('Forbidden');
    });

    it('deve tratar erro 404 - Não encontrado', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ success: false, message: 'Not Found' })
      });

      await expect(apiClient.get('/not-found')).rejects.toThrow('Not Found');
    });

    it('deve tratar erro 500 - Erro interno do servidor', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ success: false, message: 'Internal Server Error' })
      });

      await expect(apiClient.get('/error')).rejects.toThrow('Internal Server Error');
    });

    it('deve tratar erro de rede', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(apiClient.get('/network-error')).rejects.toThrow('Network error');
    });

    it('deve tratar erro de timeout', async () => {
      const timeoutResponse = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout')), 10000)
      );

      (global.fetch as jest.Mock).mockReturnValue(timeoutResponse);

      await expect(apiClient.get('/timeout')).rejects.toThrow();
    });
  });

  describe('Callback de Erro Global', () => {
    it('deve chamar callback de erro global', async () => {
      const onError = jest.fn();
      apiClient = new ApiClient({
        baseURL: 'https://api.example.com',
        onError
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ success: false, message: 'Server Error' })
      });

      await expect(apiClient.get('/error')).rejects.toThrow();
      expect(onError).toHaveBeenCalledWith(expect.objectContaining({
        message: 'Server Error',
        status: 500
      }));
    });
  });

  describe('Parsing de Resposta', () => {
    it('deve parsear resposta JSON válida', async () => {
      const mockData = { users: [{ id: 1, name: 'John' }] };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockData
      });

      const result = await apiClient.get('/users');

      expect(result).toEqual(mockData);
    });

    it('deve tratar resposta vazia', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 204,
        json: async () => null
      });

      const result = await apiClient.get('/empty');

      expect(result).toEqual(null);
    });

    it('deve tratar resposta de texto', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        text: async () => 'plain text response'
      });

      const result = await apiClient.get('/text');

      expect(result).toBe('plain text response');
    });
  });

  describe('Configurações de Requisição', () => {
    it('deve usar timeout customizado por requisição', async () => {
      const slowResponse = new Promise(resolve => 
        setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 10000)
      );

      (global.fetch as jest.Mock).mockReturnValue(slowResponse);

      await expect(apiClient.get('/slow', { timeout: 1000 })).rejects.toThrow();
    });

    it('deve usar número de retries customizado por requisição', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(apiClient.get('/retry', { retries: 1 })).rejects.toThrow();
      expect(global.fetch).toHaveBeenCalledTimes(2); // 1 tentativa + 1 retry
    });

    it('deve usar delay de retry customizado', async () => {
      jest.useFakeTimers();

      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const requestPromise = apiClient.get('/retry', { retryDelay: 2000 });

      jest.advanceTimersByTime(1000);
      expect(global.fetch).toHaveBeenCalledTimes(1);

      jest.advanceTimersByTime(1000);
      expect(global.fetch).toHaveBeenCalledTimes(2);

      jest.useRealTimers();
    });
  });

  describe('Integração ApiClient', () => {
    it('deve manter estado consistente durante múltiplas requisições', async () => {
      const token = 'auth-token-123';
      apiClient.setAuthToken(token);

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: {} })
      });

      // Múltiplas requisições
      await apiClient.get('/users');
      await apiClient.post('/users', { name: 'John' });
      await apiClient.put('/users/1', { name: 'John Updated' });
      await apiClient.delete('/users/1');

      expect(global.fetch).toHaveBeenCalledTimes(4);
      
      // Verificar se todas as requisições incluíram o token
      (global.fetch as jest.Mock).mock.calls.forEach(call => {
        expect(call[1].headers).toHaveProperty('Authorization', `Bearer ${token}`);
      });
    });

    it('deve lidar com mudança de token durante requisições', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: {} })
      });

      // Primeira requisição sem token
      await apiClient.get('/public');

      // Definir token
      apiClient.setAuthToken('new-token');

      // Segunda requisição com token
      await apiClient.get('/protected');

      const calls = (global.fetch as jest.Mock).mock.calls;
      expect(calls[0][1].headers).not.toHaveProperty('Authorization');
      expect(calls[1][1].headers).toHaveProperty('Authorization', 'Bearer new-token');
    });
  });

  describe('Performance ApiClient', () => {
    it('deve evitar requisições duplicadas simultâneas', async () => {
      const mockResponse = { success: true, data: {} };
      let resolvePromise: (value: any) => void;
      
      const pendingPromise = new Promise(resolve => {
        resolvePromise = resolve;
      });

      (global.fetch as jest.Mock).mockReturnValue(pendingPromise);

      // Iniciar múltiplas requisições simultâneas
      const request1 = apiClient.get('/users');
      const request2 = apiClient.get('/users');
      const request3 = apiClient.get('/users');

      // Resolver a primeira requisição
      resolvePromise!({
        ok: true,
        status: 200,
        json: async () => mockResponse
      });

      const results = await Promise.all([request1, request2, request3]);

      expect(results).toEqual([mockResponse, mockResponse, mockResponse]);
      expect(global.fetch).toHaveBeenCalledTimes(1); // Apenas uma requisição real
    });
  });
}); 