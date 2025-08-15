/**
 * AuthContext.tsx
 * 
 * Contexto de autenticação para Omni Keywords Finder
 * 
 * Tracing ID: AUTH_CONTEXT_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.2
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Contexto de autenticação centralizado
 * - Integração com useAuth hook
 * - Proteção de rotas
 * - Refresh token automático
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { usePermissions } from '../hooks/usePermissions';

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

interface AuthContextType {
  // Estado
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Ações
  login: (credentials: { email: string; password: string; rememberMe?: boolean }) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  clearError: () => void;
  
  // Permissões
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  
  // Utilitários
  isTokenExpired: () => boolean;
  getTokenExpirationTime: () => number | null;
}

// Contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const auth = useAuth();
  const permissions = usePermissions();
  const [tokenExpiration, setTokenExpiration] = useState<number | null>(null);

  // Verificar expiração do token
  const isTokenExpired = (): boolean => {
    if (!tokenExpiration) return true;
    return Date.now() >= tokenExpiration;
  };

  // Obter tempo de expiração do token
  const getTokenExpirationTime = (): number | null => {
    return tokenExpiration;
  };

  // Configurar expiração do token
  useEffect(() => {
    if (auth.token) {
      try {
        // Decodificar JWT para obter expiração
        const payload = JSON.parse(atob(auth.token.split('.')[1]));
        if (payload.exp) {
          setTokenExpiration(payload.exp * 1000); // Converter para milissegundos
        }
      } catch (error) {
        console.error('Erro ao decodificar token:', error);
        setTokenExpiration(null);
      }
    } else {
      setTokenExpiration(null);
    }
  }, [auth.token]);

  // Refresh automático do token
  useEffect(() => {
    if (auth.isAuthenticated && tokenExpiration) {
      const timeUntilExpiration = tokenExpiration - Date.now();
      const refreshThreshold = 5 * 60 * 1000; // 5 minutos antes da expiração

      if (timeUntilExpiration <= refreshThreshold && timeUntilExpiration > 0) {
        // Token vai expirar em breve, renovar
        const refreshTimer = setTimeout(() => {
          auth.refreshToken();
        }, timeUntilExpiration - refreshThreshold);

        return () => clearTimeout(refreshTimer);
      }
    }
  }, [auth.isAuthenticated, tokenExpiration, auth.refreshToken]);

  // Verificar expiração periodicamente
  useEffect(() => {
    if (auth.isAuthenticated) {
      const checkExpiration = () => {
        if (isTokenExpired()) {
          console.warn('Token expirado, fazendo logout...');
          auth.logout();
        }
      };

      const interval = setInterval(checkExpiration, 60000); // Verificar a cada minuto
      return () => clearInterval(interval);
    }
  }, [auth.isAuthenticated, auth.logout]);

  const contextValue: AuthContextType = {
    // Estado
    user: auth.user,
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    error: auth.error,
    
    // Ações
    login: auth.login,
    logout: auth.logout,
    refreshToken: auth.refreshToken,
    clearError: auth.clearError,
    
    // Permissões
    hasPermission: permissions.hasPermission,
    hasRole: permissions.hasRole,
    
    // Utilitários
    isTokenExpired,
    getTokenExpirationTime
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook para usar o contexto
export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};

// Componente de proteção de rota
interface ProtectedRouteProps {
  children: ReactNode;
  requiredPermissions?: string[];
  requiredRoles?: string[];
  fallback?: ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions = [],
  requiredRoles = [],
  fallback = <div>Carregando...</div>
}) => {
  const { isAuthenticated, isLoading, hasPermission, hasRole } = useAuthContext();

  if (isLoading) {
    return <>{fallback}</>;
  }

  if (!isAuthenticated) {
    return <div>Você precisa estar logado para acessar esta página.</div>;
  }

  // Verificar permissões
  if (requiredPermissions.length > 0) {
    const hasRequiredPermissions = requiredPermissions.every(permission => 
      hasPermission(permission)
    );
    
    if (!hasRequiredPermissions) {
      return <div>Você não tem permissão para acessar esta página.</div>;
    }
  }

  // Verificar roles
  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some(role => 
      hasRole(role)
    );
    
    if (!hasRequiredRole) {
      return <div>Você não tem o role necessário para acessar esta página.</div>;
    }
  }

  return <>{children}</>;
};

export default AuthProvider; 