/**
 * useAuth.test.ts
 * 
 * Testes unitários para o hook useAuth
 * 
 * Tracing ID: TEST-USE-AUTH-001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth } from '../../app/hooks/useAuth';
import { API_ENDPOINTS, getAuthToken, setAuthToken, removeAuthToken } from '../../app/config/api';

// Mock do fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock do localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

// Mock das funções de API
jest.mock('../../app/config/api', () => ({
  API_ENDPOINTS: {
    auth: {
      login: '/api/auth/login',
      logout: '/api/auth/logout',
      refresh: '/api/auth/refresh',
    },
  },
  getAuthToken: jest.fn(),
  setAuthToken: jest.fn(),
  removeAuthToken: jest.fn(),
  getAuthHeaders: jest.fn(() => ({ 'Authorization': 'Bearer test-token' })),
}));

// Mock do console.error para evitar logs nos testes
const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    
    // Mock do localStorage global
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });
  });

  afterAll(() => {
    consoleSpy.mockRestore();
  });

  describe('Inicialização', () => {
    it('deve inicializar com estado padrão', () => {
      (getAuthToken as jest.Mock).mockReturnValue(null);

      const { result } = renderHook(() => useAuth());

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('deve carregar token existente do localStorage', async () => {
      const mockToken = 'existing-token';
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user' as const,
        permissions: ['read'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      (getAuthToken as jest.Mock).mockReturnValue(mockToken);
      
      // Mock da validação de token
      mockFetch
        .mockResolvedValueOnce({ ok: true }) // validateToken
        .mockResolvedValueOnce({ 
          ok: true, 
          json: () => Promise.resolve(mockUser) 
        }); // fetchUserProfile

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe(mockToken);
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('deve limpar token inválido na inicialização', async () => {
      const mockToken = 'invalid-token';
      (getAuthToken as jest.Mock).mockReturnValue(mockToken);
      
      // Mock de token inválido
      mockFetch.mockResolvedValue({ ok: false });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(removeAuthToken).toHaveBeenCalled();
    });
  });

  describe('Login', () => {
    it('deve fazer login com sucesso', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123',
        rememberMe: true,
      };

      const mockResponse = {
        user: {
          id: 'user-1',
          email: 'test@example.com',
          name: 'Test User',
          role: 'user' as const,
          permissions: ['read'],
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
        },
        token: 'new-token',
        refreshToken: 'refresh-token',
        expiresIn: 3600,
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { result } = renderHook(() => useAuth());

      let loginResult: boolean;
      await act(async () => {
        loginResult = await result.current.login(credentials);
      });

      expect(loginResult).toBe(true);
      expect(result.current.user).toEqual(mockResponse.user);
      expect(result.current.token).toBe(mockResponse.token);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(setAuthToken).toHaveBeenCalledWith(mockResponse.token);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', mockResponse.refreshToken);
    });

    it('deve lidar com erro no login', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'wrong-password',
      };

      const errorResponse = {
        message: 'Credenciais inválidas',
      };

      mockFetch.mockResolvedValue({
        ok: false,
        json: () => Promise.resolve(errorResponse),
      });

      const { result } = renderHook(() => useAuth());

      let loginResult: boolean;
      await act(async () => {
        loginResult = await result.current.login(credentials);
      });

      expect(loginResult).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe('Credenciais inválidas');
    });

    it('deve lidar com erro de rede no login', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };

      mockFetch.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAuth());

      let loginResult: boolean;
      await act(async () => {
        loginResult = await result.current.login(credentials);
      });

      expect(loginResult).toBe(false);
      expect(result.current.error).toBe('Network error');
    });
  });

  describe('Logout', () => {
    it('deve fazer logout com sucesso', async () => {
      const mockToken = 'test-token';
      (getAuthToken as jest.Mock).mockReturnValue(mockToken);

      mockFetch.mockResolvedValue({ ok: true });

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(removeAuthToken).toHaveBeenCalled();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken');
    });

    it('deve fazer logout mesmo com erro na API', async () => {
      const mockToken = 'test-token';
      (getAuthToken as jest.Mock).mockReturnValue(mockToken);

      mockFetch.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(removeAuthToken).toHaveBeenCalled();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken');
    });
  });

  describe('Refresh Token', () => {
    it('deve renovar token com sucesso', async () => {
      const mockRefreshToken = 'refresh-token';
      const mockNewToken = 'new-token';
      const mockNewRefreshToken = 'new-refresh-token';

      localStorageMock.getItem.mockReturnValue(mockRefreshToken);

      const mockResponse = {
        token: mockNewToken,
        refreshToken: mockNewRefreshToken,
        expiresIn: 3600,
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { result } = renderHook(() => useAuth());

      let refreshResult: boolean;
      await act(async () => {
        refreshResult = await result.current.refreshToken();
      });

      expect(refreshResult).toBe(true);
      expect(setAuthToken).toHaveBeenCalledWith(mockNewToken);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', mockNewRefreshToken);
    });

    it('deve lidar com erro na renovação do token', async () => {
      localStorageMock.getItem.mockReturnValue('invalid-refresh-token');

      mockFetch.mockResolvedValue({ ok: false });

      const { result } = renderHook(() => useAuth());

      let refreshResult: boolean;
      await act(async () => {
        refreshResult = await result.current.refreshToken();
      });

      expect(refreshResult).toBe(false);
      expect(removeAuthToken).toHaveBeenCalled();
    });

    it('deve lidar com refresh token não encontrado', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      const { result } = renderHook(() => useAuth());

      let refreshResult: boolean;
      await act(async () => {
        refreshResult = await result.current.refreshToken();
      });

      expect(refreshResult).toBe(false);
      expect(removeAuthToken).toHaveBeenCalled();
    });
  });

  describe('Verificação de Permissões', () => {
    it('deve verificar permissões corretamente', () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'admin' as const,
        permissions: ['read', 'write', 'delete'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      // Mock do estado com usuário logado
      const { result } = renderHook(() => useAuth());
      
      // Simular usuário logado
      act(() => {
        (result.current as any).user = mockUser;
      });

      expect(result.current.hasPermission('read')).toBe(true);
      expect(result.current.hasPermission('write')).toBe(true);
      expect(result.current.hasPermission('delete')).toBe(true);
      expect(result.current.hasPermission('admin')).toBe(false);
    });

    it('deve retornar false para permissões quando não há usuário', () => {
      const { result } = renderHook(() => useAuth());

      expect(result.current.hasPermission('read')).toBe(false);
      expect(result.current.hasPermission('write')).toBe(false);
    });
  });

  describe('Verificação de Role', () => {
    it('deve verificar roles corretamente', () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'admin' as const,
        permissions: ['read', 'write'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      const { result } = renderHook(() => useAuth());
      
      // Simular usuário logado
      act(() => {
        (result.current as any).user = mockUser;
      });

      expect(result.current.hasRole('admin')).toBe(true);
      expect(result.current.hasRole('user')).toBe(false);
      expect(result.current.hasRole('viewer')).toBe(false);
    });

    it('deve retornar false para roles quando não há usuário', () => {
      const { result } = renderHook(() => useAuth());

      expect(result.current.hasRole('admin')).toBe(false);
      expect(result.current.hasRole('user')).toBe(false);
    });
  });

  describe('Limpeza de Erro', () => {
    it('deve limpar erro corretamente', () => {
      const { result } = renderHook(() => useAuth());

      // Simular erro
      act(() => {
        (result.current as any).error = 'Test error';
      });

      expect(result.current.error).toBe('Test error');

      // Limpar erro
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Estados de Loading', () => {
    it('deve mostrar loading durante login', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };

      // Mock de resposta lenta
      mockFetch.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({ ok: true, json: () => Promise.resolve({}) }), 100)
        )
      );

      const { result } = renderHook(() => useAuth());

      let loginPromise: Promise<boolean>;
      act(() => {
        loginPromise = result.current.login(credentials);
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        await loginPromise;
      });

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Persistência de Dados', () => {
    it('deve salvar refresh token quando rememberMe é true', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123',
        rememberMe: true,
      };

      const mockResponse = {
        user: { id: 'user-1', email: 'test@example.com', name: 'Test', role: 'user', permissions: [], createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-01T00:00:00Z' },
        token: 'new-token',
        refreshToken: 'refresh-token',
        expiresIn: 3600,
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.login(credentials);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'refresh-token');
    });

    it('não deve salvar refresh token quando rememberMe é false', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123',
        rememberMe: false,
      };

      const mockResponse = {
        user: { id: 'user-1', email: 'test@example.com', name: 'Test', role: 'user', permissions: [], createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-01T00:00:00Z' },
        token: 'new-token',
        refreshToken: 'refresh-token',
        expiresIn: 3600,
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.login(credentials);
      });

      expect(localStorageMock.setItem).not.toHaveBeenCalledWith('refreshToken', 'refresh-token');
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve lidar com erro na inicialização', async () => {
      (getAuthToken as jest.Mock).mockReturnValue('test-token');
      
      mockFetch.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Erro ao carregar sessão');
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('deve lidar com erro desconhecido no login', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };

      mockFetch.mockRejectedValue('Unknown error');

      const { result } = renderHook(() => useAuth());

      await act(async () => {
        await result.current.login(credentials);
      });

      expect(result.current.error).toBe('Erro desconhecido no login');
    });
  });
}); 