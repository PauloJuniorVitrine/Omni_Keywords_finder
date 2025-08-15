/**
 * useAuth.ts
 * 
 * Hook de autenticação e autorização
 * 
 * Tracing ID: HOOK-001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS, getAuthToken, setAuthToken, removeAuthToken, getAuthHeaders } from '../config/api';

// Tipos
interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  permissions: string[];
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface LoginResponse {
  user: User;
  token: string;
  refreshToken: string;
  expiresIn: number;
}

interface RefreshResponse {
  token: string;
  refreshToken: string;
  expiresIn: number;
}

// Estado inicial
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

export const useAuth = () => {
  const [state, setState] = useState<AuthState>(initialState);

  // Verificar token existente no carregamento
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = getAuthToken();
        
        if (token) {
          // Verificar se o token é válido
          const isValid = await validateToken(token);
          
          if (isValid) {
            const user = await fetchUserProfile(token);
            setState({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            // Token inválido, limpar
            logout();
          }
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        console.error('Erro ao inicializar autenticação:', error);
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: 'Erro ao carregar sessão' 
        }));
      }
    };

    initializeAuth();
  }, []);

  // Função para fazer login
  const login = useCallback(async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      const response = await fetch(API_ENDPOINTS.auth.login, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Erro no login');
      }

      const data: LoginResponse = await response.json();

      // Salvar token
      setAuthToken(data.token);
      
      // Salvar refresh token se rememberMe estiver ativo
      if (credentials.rememberMe) {
        localStorage.setItem('refreshToken', data.refreshToken);
      }

      setState({
        user: data.user,
        token: data.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido no login';
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: errorMessage 
      }));
      return false;
    }
  }, []);

  // Função para fazer logout
  const logout = useCallback(async (): Promise<void> => {
    try {
      const token = getAuthToken();
      
      if (token) {
        // Chamar endpoint de logout
        await fetch(API_ENDPOINTS.auth.logout, {
          method: 'POST',
          headers: getAuthHeaders(token),
        });
      }
    } catch (error) {
      console.error('Erro no logout:', error);
    } finally {
      // Limpar dados locais
      removeAuthToken();
      localStorage.removeItem('refreshToken');
      
      setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  }, []);

  // Função para renovar token
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const refreshTokenValue = localStorage.getItem('refreshToken');
      
      if (!refreshTokenValue) {
        throw new Error('Refresh token não encontrado');
      }

      const response = await fetch(API_ENDPOINTS.auth.refresh, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken: refreshTokenValue }),
      });

      if (!response.ok) {
        throw new Error('Falha ao renovar token');
      }

      const data: RefreshResponse = await response.json();

      // Atualizar tokens
      setAuthToken(data.token);
      localStorage.setItem('refreshToken', data.refreshToken);

      setState(prev => ({
        ...prev,
        token: data.token,
      }));

      return true;
    } catch (error) {
      console.error('Erro ao renovar token:', error);
      logout();
      return false;
    }
  }, [logout]);

  // Função para validar token
  const validateToken = useCallback(async (token: string): Promise<boolean> => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.refresh, {
        method: 'POST',
        headers: getAuthHeaders(token),
      });

      return response.ok;
    } catch (error) {
      return false;
    }
  }, []);

  // Função para buscar perfil do usuário
  const fetchUserProfile = useCallback(async (token: string): Promise<User> => {
    const response = await fetch('/api/user/profile', {
      headers: getAuthHeaders(token),
    });

    if (!response.ok) {
      throw new Error('Erro ao buscar perfil do usuário');
    }

    return response.json();
  }, []);

  // Função para verificar permissões
  const hasPermission = useCallback((permission: string): boolean => {
    if (!state.user) return false;
    return state.user.permissions.includes(permission);
  }, [state.user]);

  // Função para verificar role
  const hasRole = useCallback((role: string): boolean => {
    if (!state.user) return false;
    return state.user.role === role;
  }, [state.user]);

  // Função para limpar erro
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    // Estado
    user: state.user,
    token: state.token,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,
    
    // Ações
    login,
    logout,
    refreshToken,
    clearError,
    
    // Utilitários
    hasPermission,
    hasRole,
  };
};

export default useAuth; 