/**
 * 🔐 AuthInterceptor.ts
 * 🎯 Objetivo: Interceptor para autenticação automática
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: AUTH_INTERCEPTOR_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import { RequestInterceptor, ResponseInterceptor, ErrorInterceptor, ApiRequestConfig, ApiResponse, ApiError } from '../ApiClient';

// Interceptor de requisição para autenticação
export const authRequestInterceptor: RequestInterceptor = async (config: ApiRequestConfig) => {
  // Se a requisição deve pular autenticação, retornar config original
  if (config.skipAuth) {
    return config;
  }

  // Obter token de autenticação
  const token = localStorage.getItem('authToken');
  const refreshToken = localStorage.getItem('refreshToken');

  // Se não há token, tentar usar refresh token
  if (!token && refreshToken) {
    try {
      const newToken = await refreshAuthToken(refreshToken);
      if (newToken) {
        localStorage.setItem('authToken', newToken);
      }
    } catch (error) {
      // Se falhar ao renovar token, limpar tokens e redirecionar para login
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
      throw new Error('Sessão expirada. Faça login novamente.');
    }
  }

  // Adicionar token ao header se disponível
  if (token) {
    config.headers = {
      ...config.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  return config;
};

// Interceptor de resposta para renovação de token
export const authResponseInterceptor: ResponseInterceptor = async (response: ApiResponse) => {
  // Se a resposta indica token expirado, tentar renovar
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (refreshToken) {
      try {
        const newToken = await refreshAuthToken(refreshToken);
        if (newToken) {
          localStorage.setItem('authToken', newToken);
          
          // Retry da requisição original com novo token
          // Esta lógica seria implementada no cliente principal
          throw new Error('Token renewed, retry request');
        }
      } catch (error) {
        // Se falhar ao renovar, limpar tokens e redirecionar
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        throw new Error('Sessão expirada. Faça login novamente.');
      }
    } else {
      // Sem refresh token, redirecionar para login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      throw new Error('Sessão expirada. Faça login novamente.');
    }
  }

  return response;
};

// Interceptor de erro para tratamento de erros de autenticação
export const authErrorInterceptor: ErrorInterceptor = async (error: ApiError) => {
  // Se o erro é de autenticação (401), tentar renovar token
  if (error.status === 401) {
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (refreshToken) {
      try {
        const newToken = await refreshAuthToken(refreshToken);
        if (newToken) {
          localStorage.setItem('authToken', newToken);
          error.message = 'Token renewed, retry request';
          return error;
        }
      } catch (refreshError) {
        // Se falhar ao renovar, limpar tokens e redirecionar
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        error.message = 'Sessão expirada. Faça login novamente.';
        return error;
      }
    } else {
      // Sem refresh token, redirecionar para login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      error.message = 'Sessão expirada. Faça login novamente.';
      return error;
    }
  }

  return error;
};

// Função para renovar token de autenticação
async function refreshAuthToken(refreshToken: string): Promise<string | null> {
  try {
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const data = await response.json();
    return data.access_token || null;
  } catch (error) {
    console.error('Error refreshing token:', error);
    return null;
  }
}

// Função para verificar se o usuário está autenticado
export function isAuthenticated(): boolean {
  const token = localStorage.getItem('authToken');
  return !!token;
}

// Função para obter informações do usuário do token
export function getUserFromToken(): any | null {
  const token = localStorage.getItem('authToken');
  
  if (!token) {
    return null;
  }

  try {
    // Decodificar JWT token (sem verificar assinatura no frontend)
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

// Função para logout
export function logout(): void {
  localStorage.removeItem('authToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  
  // Redirecionar para login
  window.location.href = '/login';
}

// Função para verificar se o token está expirado
export function isTokenExpired(): boolean {
  const token = localStorage.getItem('authToken');
  
  if (!token) {
    return true;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    
    return payload.exp < currentTime;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true;
  }
}

// Função para obter tempo restante do token
export function getTokenTimeRemaining(): number {
  const token = localStorage.getItem('authToken');
  
  if (!token) {
    return 0;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    
    return Math.max(0, payload.exp - currentTime);
  } catch (error) {
    console.error('Error getting token time remaining:', error);
    return 0;
  }
} 