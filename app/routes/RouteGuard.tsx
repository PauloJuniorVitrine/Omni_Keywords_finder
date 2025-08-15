/**
 * RouteGuard.tsx
 * 
 * Componente para proteção de rotas
 * 
 * Tracing ID: ROUTE_GUARD_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.2
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Proteção de rotas por autenticação
 * - Verificação de permissões
 * - Redirecionamento automático
 * - Loading states
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { usePermissions } from '../hooks/usePermissions';
import { LoadingSpinner } from '../components/shared/LoadingSpinner';

interface RouteGuardProps {
  children: React.ReactNode;
  isAuthenticated: boolean;
  requiredPermissions?: string[];
  hasPermission: (permission: string) => boolean;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export const RouteGuard: React.FC<RouteGuardProps> = ({
  children,
  isAuthenticated,
  requiredPermissions = [],
  hasPermission,
  fallback,
  redirectTo = '/login'
}) => {
  const location = useLocation();
  const { isLoading } = useAuth();

  // Loading state
  if (isLoading) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Verificando permissões..." />
      </div>
    );
  }

  // Verificar autenticação
  if (!isAuthenticated) {
    // Salvar a rota atual para redirecionamento após login
    const currentPath = location.pathname + location.search;
    return (
      <Navigate 
        to={`${redirectTo}?redirect=${encodeURIComponent(currentPath)}`} 
        replace 
      />
    );
  }

  // Verificar permissões
  if (requiredPermissions.length > 0) {
    const hasAllPermissions = requiredPermissions.every(permission => 
      hasPermission(permission)
    );

    if (!hasAllPermissions) {
      // Redirecionar para página de acesso negado
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // Renderizar conteúdo protegido
  return <>{children}</>;
};

// Hook para verificar permissões de rota
export const useRouteGuard = (requiredPermissions: string[] = []) => {
  const { isAuthenticated, isLoading } = useAuth();
  const { hasPermission } = usePermissions();
  const location = useLocation();

  const canAccess = React.useMemo(() => {
    if (!isAuthenticated) return false;
    
    if (requiredPermissions.length === 0) return true;
    
    return requiredPermissions.every(permission => hasPermission(permission));
  }, [isAuthenticated, requiredPermissions, hasPermission]);

  const redirectPath = React.useMemo(() => {
    if (!isAuthenticated) {
      const currentPath = location.pathname + location.search;
      return `/login?redirect=${encodeURIComponent(currentPath)}`;
    }
    
    if (!canAccess) {
      return '/unauthorized';
    }
    
    return null;
  }, [isAuthenticated, canAccess, location]);

  return {
    canAccess,
    isLoading,
    redirectPath,
    isAuthenticated
  };
};

// Componente de proteção de rota com hook
export const ProtectedRoute: React.FC<{
  children: React.ReactNode;
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
}> = ({ children, requiredPermissions = [], fallback }) => {
  const { canAccess, isLoading, redirectPath } = useRouteGuard(requiredPermissions);

  if (isLoading) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Carregando..." />
      </div>
    );
  }

  if (redirectPath) {
    return <Navigate to={redirectPath} replace />;
  }

  return <>{children}</>;
};

// Componente para rotas públicas (apenas usuários não autenticados)
export const PublicRoute: React.FC<{
  children: React.ReactNode;
  redirectTo?: string;
}> = ({ children, redirectTo = '/dashboard' }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Carregando..." />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
};

// Componente para rotas com roles específicos
export const RoleBasedRoute: React.FC<{
  children: React.ReactNode;
  allowedRoles: string[];
  fallback?: React.ReactNode;
}> = ({ children, allowedRoles, fallback }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Verificando permissões..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!user || !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export default RouteGuard; 