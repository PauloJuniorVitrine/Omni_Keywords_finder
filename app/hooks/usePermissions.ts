/**
 * usePermissions.ts
 * 
 * Hook para gerenciamento de permissões e autorização
 * 
 * Tracing ID: HOOK_PERMISSIONS_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.2
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Verificação de permissões específicas
 * - Verificação de roles
 * - Cache de permissões
 * - Integração com sistema de autenticação
 */

import { useCallback, useMemo } from 'react';
import { useAuth } from './useAuth';

// Tipos de permissões
export type Permission = 
  // Dashboard
  | 'dashboard:read'
  | 'dashboard:write'
  
  // Nichos
  | 'nichos:read'
  | 'nichos:create'
  | 'nichos:update'
  | 'nichos:delete'
  
  // Categorias
  | 'categorias:read'
  | 'categorias:create'
  | 'categorias:update'
  | 'categorias:delete'
  
  // Execuções
  | 'execucoes:read'
  | 'execucoes:create'
  | 'execucoes:update'
  | 'execucoes:delete'
  | 'execucoes:execute'
  
  // Webhooks
  | 'webhooks:read'
  | 'webhooks:create'
  | 'webhooks:update'
  | 'webhooks:delete'
  
  // Templates
  | 'templates:read'
  | 'templates:create'
  | 'templates:update'
  | 'templates:delete'
  
  // Credenciais
  | 'credentials:read'
  | 'credentials:create'
  | 'credentials:update'
  | 'credentials:delete'
  
  // Analytics
  | 'analytics:read'
  | 'analytics:export'
  
  // Administração
  | 'admin:read'
  | 'admin:write'
  | 'admin:delete'
  
  // Governança
  | 'governanca:read'
  | 'governanca:write'
  | 'governanca:delete';

// Tipos de roles
export type Role = 'admin' | 'manager' | 'user' | 'viewer';

// Mapeamento de roles para permissões
const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  admin: [
    'dashboard:read', 'dashboard:write',
    'nichos:read', 'nichos:create', 'nichos:update', 'nichos:delete',
    'categorias:read', 'categorias:create', 'categorias:update', 'categorias:delete',
    'execucoes:read', 'execucoes:create', 'execucoes:update', 'execucoes:delete', 'execucoes:execute',
    'webhooks:read', 'webhooks:create', 'webhooks:update', 'webhooks:delete',
    'templates:read', 'templates:create', 'templates:update', 'templates:delete',
    'credentials:read', 'credentials:create', 'credentials:update', 'credentials:delete',
    'analytics:read', 'analytics:export',
    'admin:read', 'admin:write', 'admin:delete',
    'governanca:read', 'governanca:write', 'governanca:delete'
  ],
  manager: [
    'dashboard:read',
    'nichos:read', 'nichos:create', 'nichos:update',
    'categorias:read', 'categorias:create', 'categorias:update',
    'execucoes:read', 'execucoes:create', 'execucoes:update', 'execucoes:execute',
    'webhooks:read', 'webhooks:create', 'webhooks:update',
    'templates:read', 'templates:create', 'templates:update',
    'credentials:read', 'credentials:create',
    'analytics:read', 'analytics:export',
    'governanca:read'
  ],
  user: [
    'dashboard:read',
    'nichos:read',
    'categorias:read',
    'execucoes:read', 'execucoes:create', 'execucoes:execute',
    'webhooks:read',
    'templates:read',
    'analytics:read'
  ],
  viewer: [
    'dashboard:read',
    'nichos:read',
    'categorias:read',
    'execucoes:read',
    'analytics:read'
  ]
};

// Interface para o hook
interface UsePermissionsReturn {
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  hasRole: (role: Role) => boolean;
  hasAnyRole: (roles: Role[]) => boolean;
  getUserPermissions: () => Permission[];
  getUserRoles: () => Role[];
  canAccess: (resource: string, action: string) => boolean;
}

export const usePermissions = (): UsePermissionsReturn => {
  const { user, isAuthenticated } = useAuth();

  // Obter permissões do usuário
  const getUserPermissions = useCallback((): Permission[] => {
    if (!isAuthenticated || !user) {
      return [];
    }

    // Permissões explícitas do usuário
    const explicitPermissions = user.permissions || [];
    
    // Permissões baseadas no role
    const rolePermissions = ROLE_PERMISSIONS[user.role as Role] || [];
    
    // Combinar permissões (sem duplicatas)
    const allPermissions = [...new Set([...explicitPermissions, ...rolePermissions])];
    
    return allPermissions as Permission[];
  }, [user, isAuthenticated]);

  // Obter roles do usuário
  const getUserRoles = useCallback((): Role[] => {
    if (!isAuthenticated || !user) {
      return [];
    }

    const roles: Role[] = [];
    
    // Role principal do usuário
    if (user.role) {
      roles.push(user.role as Role);
    }
    
    // Roles adicionais (se implementado no futuro)
    // if (user.additionalRoles) {
    //   roles.push(...user.additionalRoles);
    // }
    
    return roles;
  }, [user, isAuthenticated]);

  // Verificar permissão específica
  const hasPermission = useCallback((permission: Permission): boolean => {
    if (!isAuthenticated || !user) {
      return false;
    }

    const userPermissions = getUserPermissions();
    return userPermissions.includes(permission);
  }, [isAuthenticated, user, getUserPermissions]);

  // Verificar se tem qualquer uma das permissões
  const hasAnyPermission = useCallback((permissions: Permission[]): boolean => {
    if (!isAuthenticated || !user) {
      return false;
    }

    const userPermissions = getUserPermissions();
    return permissions.some(permission => userPermissions.includes(permission));
  }, [isAuthenticated, user, getUserPermissions]);

  // Verificar se tem todas as permissões
  const hasAllPermissions = useCallback((permissions: Permission[]): boolean => {
    if (!isAuthenticated || !user) {
      return false;
    }

    const userPermissions = getUserPermissions();
    return permissions.every(permission => userPermissions.includes(permission));
  }, [isAuthenticated, user, getUserPermissions]);

  // Verificar role específico
  const hasRole = useCallback((role: Role): boolean => {
    if (!isAuthenticated || !user) {
      return false;
    }

    const userRoles = getUserRoles();
    return userRoles.includes(role);
  }, [isAuthenticated, user, getUserRoles]);

  // Verificar se tem qualquer um dos roles
  const hasAnyRole = useCallback((roles: Role[]): boolean => {
    if (!isAuthenticated || !user) {
      return false;
    }

    const userRoles = getUserRoles();
    return roles.some(role => userRoles.includes(role));
  }, [isAuthenticated, user, getUserRoles]);

  // Verificar acesso a recurso/ação (método genérico)
  const canAccess = useCallback((resource: string, action: string): boolean => {
    const permission = `${resource}:${action}` as Permission;
    return hasPermission(permission);
  }, [hasPermission]);

  // Memoizar permissões do usuário para performance
  const userPermissions = useMemo(() => getUserPermissions(), [getUserPermissions]);
  const userRoles = useMemo(() => getUserRoles(), [getUserRoles]);

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    getUserPermissions: () => userPermissions,
    getUserRoles: () => userRoles,
    canAccess
  };
};

export default usePermissions; 