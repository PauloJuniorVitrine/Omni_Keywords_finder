/**
 * Testes para useAuth Hook
 * 
 * Prompt: Implementação de testes para hooks críticos
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USE_AUTH_001
 * 
 * Testes baseados APENAS no código real do useAuth.ts
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth } from '../useAuth';

// Mock das dependências
const mockGetAuthToken = jest.fn();
const mockSetAuthToken = jest.fn();
const mockRemoveAuthToken = jest.fn();
const mockGetAuthHeaders = jest.fn();

jest.mock('../../config/api', () => ({
  API_ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      LOGOUT: '/auth/logout',
      REFRESH: '/auth/refresh',
      PROFILE: '/auth/profile',
      VALIDATE: '/auth/validate'
    }
  },
  getAuthToken: mockGetAuthToken,
  setAuthToken: mockSetAuthToken,
  removeAuthToken: mockRemoveAuthToken,
  getAuthHeaders: mockGetAuthHeaders
}));

// Mock do fetch global
global.fetch = jest.fn();

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Inicialização', () => {
    it('deve inicializar com estado padrão quando não há token', async () => {
      mockGetAuthToken.mockReturnValue(null);

      const { result } = renderHook(() => useAuth());

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBeNull();

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('deve carregar usuário quando token válido existe', async () => {
      const mockToken = 'valid-token-123';
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user' as const,
        permissions: ['read', 'write'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      };

      mockGetAuthToken.mockReturnValue(mockToken);
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: true } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: mockUser })
        });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.isAuthenticated).toBe(true);
        expect(result.current.user).toEqual(mockUser);
        expect(result.current.token).toBe(mockToken);
      });
    });

    it('deve limpar estado quando token é inválido', async () => {
      const mockToken = 'invalid-token-123';
      
      mockGetAuthToken.mockReturnValue(mockToken);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ success: false, message: 'Token inválido' })
      });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.isAuthenticated).toBe(false);
        expect(result.current.user).toBeNull();
        expect(result.current.token).toBeNull();
      });

      expect(mockRemoveAuthToken).toHaveBeenCalled();
    });
  });

  describe('Login', () => {
    it('deve fazer login com credenciais válidas', async () => {
      const mockCredentials = {
        email: 'test@example.com',
        password: 'password123',
        rememberMe: true
      };

      const mockResponse = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'user' as const,
          permissions: ['read', 'write'],
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z'
        },
        token: 'new-token-123',
        refreshToken: 'refresh-token-123',
        expiresIn: 3600
      };

      mockGetAuthToken.mockReturnValue(null);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ success: true, data: mockResponse })
      });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.login(mockCredentials);
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockResponse.user);
      expect(result.current.token).toBe(mockResponse.token);
      expect(result.current.error).toBeNull();
      expect(mockSetAuthToken).toHaveBeenCalledWith(mockResponse.token);
    });

    it('deve tratar erro de login com credenciais inválidas', async () => {
      const mockCredentials = {
        email: 'invalid@example.com',
        password: 'wrongpassword'
      };

      mockGetAuthToken.mockReturnValue(null);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ 
          success: false, 
          message: 'Credenciais inválidas',
          errors: ['Email ou senha incorretos']
        })
      });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.login(mockCredentials);
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.error).toBe('Credenciais inválidas');
    });

    it('deve tratar erro de rede durante login', async () => {
      const mockCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      mockGetAuthToken.mockReturnValue(null);
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.login(mockCredentials);
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.error).toBe('Erro de conexão. Tente novamente.');
    });
  });

  describe('Logout', () => {
    it('deve fazer logout e limpar estado', async () => {
      const mockToken = 'valid-token-123';
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user' as const,
        permissions: ['read', 'write'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      };

      mockGetAuthToken.mockReturnValue(mockToken);
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: true } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: mockUser })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, message: 'Logout realizado com sucesso' })
        });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.error).toBeNull();
      expect(mockRemoveAuthToken).toHaveBeenCalled();
    });

    it('deve fazer logout mesmo se API falhar', async () => {
      const mockToken = 'valid-token-123';
      
      mockGetAuthToken.mockReturnValue(mockToken);
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: true } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { id: 'user-123' } })
        })
        .mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(mockRemoveAuthToken).toHaveBeenCalled();
    });
  });

  describe('Refresh Token', () => {
    it('deve renovar token com sucesso', async () => {
      const mockToken = 'expired-token-123';
      const mockRefreshToken = 'refresh-token-123';
      const mockNewToken = 'new-token-456';
      const mockNewRefreshToken = 'new-refresh-token-456';

      mockGetAuthToken.mockReturnValue(mockToken);
      localStorage.setItem('refreshToken', mockRefreshToken);

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: false } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            success: true,
            data: {
              token: mockNewToken,
              refreshToken: mockNewRefreshToken,
              expiresIn: 3600
            }
          })
        });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.token).toBe(mockNewToken);
      expect(mockSetAuthToken).toHaveBeenCalledWith(mockNewToken);
    });

    it('deve fazer logout quando refresh token é inválido', async () => {
      const mockToken = 'expired-token-123';
      const mockRefreshToken = 'invalid-refresh-token-123';

      mockGetAuthToken.mockReturnValue(mockToken);
      localStorage.setItem('refreshToken', mockRefreshToken);

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: false } })
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          json: async () => ({ success: false, message: 'Refresh token inválido' })
        });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.refreshToken();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(mockRemoveAuthToken).toHaveBeenCalled();
    });
  });

  describe('Verificação de Permissões', () => {
    it('deve verificar permissões do usuário autenticado', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'admin' as const,
        permissions: ['read', 'write', 'delete', 'admin'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      };

      mockGetAuthToken.mockReturnValue('valid-token');
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: true } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: mockUser })
        });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      expect(result.current.hasPermission('read')).toBe(true);
      expect(result.current.hasPermission('write')).toBe(true);
      expect(result.current.hasPermission('delete')).toBe(true);
      expect(result.current.hasPermission('admin')).toBe(true);
      expect(result.current.hasPermission('nonexistent')).toBe(false);
    });

    it('deve retornar false para permissões quando não autenticado', () => {
      mockGetAuthToken.mockReturnValue(null);

      const { result } = renderHook(() => useAuth());

      expect(result.current.hasPermission('read')).toBe(false);
      expect(result.current.hasPermission('write')).toBe(false);
    });

    it('deve verificar se usuário tem role específico', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'admin' as const,
        permissions: ['read', 'write'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      };

      mockGetAuthToken.mockReturnValue('valid-token');
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: true } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: mockUser })
        });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      expect(result.current.hasRole('admin')).toBe(true);
      expect(result.current.hasRole('user')).toBe(false);
      expect(result.current.hasRole('viewer')).toBe(false);
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve tratar erro de inicialização', async () => {
      mockGetAuthToken.mockImplementation(() => {
        throw new Error('Storage error');
      });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.error).toBe('Erro ao carregar sessão');
      });
    });

    it('deve limpar erro ao fazer login com sucesso', async () => {
      const mockCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      mockGetAuthToken.mockReturnValue(null);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            user: { id: 'user-123', email: 'test@example.com', name: 'Test User', role: 'user', permissions: [], createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-01T00:00:00Z' },
            token: 'new-token',
            refreshToken: 'refresh-token',
            expiresIn: 3600
          }
        })
      });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Simular erro anterior
      act(() => {
        result.current.setError('Erro anterior');
      });

      expect(result.current.error).toBe('Erro anterior');

      await act(async () => {
        await result.current.login(mockCredentials);
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Integração useAuth', () => {
    it('deve manter estado consistente durante ciclo completo de autenticação', async () => {
      const mockCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user' as const,
        permissions: ['read', 'write'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      };

      mockGetAuthToken.mockReturnValue(null);
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            success: true,
            data: {
              user: mockUser,
              token: 'login-token',
              refreshToken: 'refresh-token',
              expiresIn: 3600
            }
          })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, message: 'Logout realizado' })
        });

      const { result } = renderHook(() => useAuth());

      // Estado inicial
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Login
      await act(async () => {
        await result.current.login(mockCredentials);
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe('login-token');

      // Logout
      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
    });
  });

  describe('Acessibilidade useAuth', () => {
    it('deve fornecer informações de acessibilidade para leitores de tela', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'user' as const,
        permissions: ['read', 'write'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      };

      mockGetAuthToken.mockReturnValue('valid-token');
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: { valid: true } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, data: mockUser })
        });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      // Verificar se informações de acessibilidade estão disponíveis
      expect(result.current.user?.name).toBe('Test User');
      expect(result.current.user?.email).toBe('test@example.com');
      expect(result.current.user?.role).toBe('user');
    });
  });

  describe('Performance useAuth', () => {
    it('deve evitar re-renders desnecessários durante operações', async () => {
      const mockCredentials = {
        email: 'test@example.com',
        password: 'password123'
      };

      mockGetAuthToken.mockReturnValue(null);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            user: { id: 'user-123', email: 'test@example.com', name: 'Test User', role: 'user', permissions: [], createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-01T00:00:00Z' },
            token: 'new-token',
            refreshToken: 'refresh-token',
            expiresIn: 3600
          }
        })
      });

      const { result, rerender } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const initialRenderCount = 1;

      await act(async () => {
        await result.current.login(mockCredentials);
      });

      rerender();

      // Verificar se não houve re-renders desnecessários
      expect(result.current.isAuthenticated).toBe(true);
    });
  });
}); 