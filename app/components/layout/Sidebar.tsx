/**
 * Sidebar.tsx
 * 
 * Componente de navegação lateral
 * 
 * Tracing ID: SIDEBAR_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Navegação principal
 * - Menu colapsável
 * - Filtros por permissões
 * - Indicadores de status
 */

import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { usePermissions } from '../../hooks/usePermissions';
import { useAppStore } from '../../store/AppStore';

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

interface MenuItem {
  id: string;
  label: string;
  path: string;
  icon: React.ReactNode;
  permissions?: string[];
  roles?: string[];
  badge?: number;
  children?: MenuItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  collapsed = false, 
  onToggle 
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { hasPermission, hasRole } = usePermissions();
  const { state } = useAppStore();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  // Ícones SVG inline
  const icons = {
    dashboard: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z" />
      </svg>
    ),
    nichos: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    categorias: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
      </svg>
    ),
    execucoes: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    analytics: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    webhooks: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
      </svg>
    ),
    templates: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    credentials: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
      </svg>
    ),
    admin: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    governanca: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    )
  };

  // Configuração do menu
  const menuItems: MenuItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/dashboard',
      icon: icons.dashboard,
      permissions: ['dashboard:read']
    },
    {
      id: 'nichos',
      label: 'Nichos',
      path: '/nichos',
      icon: icons.nichos,
      permissions: ['nichos:read'],
      badge: state.data.nichos.length
    },
    {
      id: 'categorias',
      label: 'Categorias',
      path: '/categorias',
      icon: icons.categorias,
      permissions: ['categorias:read'],
      badge: state.data.categorias.length
    },
    {
      id: 'execucoes',
      label: 'Execuções',
      path: '/execucoes',
      icon: icons.execucoes,
      permissions: ['execucoes:read'],
      badge: state.data.execucoes.filter(e => e.status === 'executando').length
    },
    {
      id: 'analytics',
      label: 'Analytics',
      path: '/analytics',
      icon: icons.analytics,
      permissions: ['analytics:read']
    },
    {
      id: 'webhooks',
      label: 'Webhooks',
      path: '/webhooks',
      icon: icons.webhooks,
      permissions: ['webhooks:read']
    },
    {
      id: 'templates',
      label: 'Templates',
      path: '/templates',
      icon: icons.templates,
      permissions: ['templates:read']
    },
    {
      id: 'credentials',
      label: 'Credenciais',
      path: '/credentials',
      icon: icons.credentials,
      permissions: ['credentials:read']
    },
    {
      id: 'admin',
      label: 'Administração',
      path: '/admin',
      icon: icons.admin,
      permissions: ['admin:read'],
      roles: ['admin']
    },
    {
      id: 'governanca',
      label: 'Governança',
      path: '/governanca',
      icon: icons.governanca,
      permissions: ['governanca:read'],
      roles: ['admin', 'manager']
    }
  ];

  // Filtrar itens por permissões
  const filteredMenuItems = menuItems.filter(item => {
    // Verificar permissões
    if (item.permissions && item.permissions.length > 0) {
      const hasRequiredPermissions = item.permissions.every(permission => 
        hasPermission(permission)
      );
      if (!hasRequiredPermissions) return false;
    }

    // Verificar roles
    if (item.roles && item.roles.length > 0) {
      const hasRequiredRole = item.roles.some(role => 
        hasRole(role)
      );
      if (!hasRequiredRole) return false;
    }

    return true;
  });

  const handleItemClick = (item: MenuItem) => {
    if (item.children) {
      // Toggle submenu
      setExpandedItems(prev => 
        prev.includes(item.id) 
          ? prev.filter(id => id !== item.id)
          : [...prev, item.id]
      );
    } else {
      // Navegar para a página
      navigate(item.path);
    }
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const isExpanded = (itemId: string) => {
    return expandedItems.includes(itemId);
  };

  return (
    <aside className={`
      bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
      transition-all duration-300 ease-in-out
      ${collapsed ? 'w-16' : 'w-64'}
      h-full overflow-y-auto
    `}>
      {/* Header da sidebar */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        {!collapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">OK</span>
            </div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Menu
            </h2>
          </div>
        )}
        {collapsed && (
          <div className="flex justify-center">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">OK</span>
            </div>
          </div>
        )}
      </div>

      {/* Menu items */}
      <nav className="p-2">
        <ul className="space-y-1">
          {filteredMenuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => handleItemClick(item)}
                className={`
                  w-full flex items-center px-3 py-2 text-sm font-medium rounded-md
                  transition-colors duration-200
                  ${isActive(item.path)
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                  }
                  ${collapsed ? 'justify-center' : 'justify-between'}
                `}
                title={collapsed ? item.label : undefined}
              >
                <div className="flex items-center space-x-3">
                  <span className="flex-shrink-0">
                    {item.icon}
                  </span>
                  {!collapsed && (
                    <span>{item.label}</span>
                  )}
                </div>
                
                {!collapsed && (
                  <div className="flex items-center space-x-2">
                    {item.badge && item.badge > 0 && (
                      <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                        {item.badge}
                      </span>
                    )}
                    {item.children && (
                      <svg 
                        className={`w-4 h-4 transition-transform duration-200 ${
                          isExpanded(item.id) ? 'rotate-180' : ''
                        }`} 
                        fill="currentColor" 
                        viewBox="0 0 20 20"
                      >
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                )}
              </button>

              {/* Submenu */}
              {item.children && !collapsed && isExpanded(item.id) && (
                <ul className="mt-1 ml-6 space-y-1">
                  {item.children.map((child) => (
                    <li key={child.id}>
                      <button
                        onClick={() => navigate(child.path)}
                        className={`
                          w-full flex items-center px-3 py-2 text-sm rounded-md
                          transition-colors duration-200
                          ${isActive(child.path)
                            ? 'bg-blue-50 dark:bg-blue-800 text-blue-600 dark:text-blue-400'
                            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                          }
                        `}
                      >
                        <span className="flex-shrink-0 mr-3">
                          {child.icon}
                        </span>
                        <span>{child.label}</span>
                        {child.badge && child.badge > 0 && (
                          <span className="ml-auto inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                            {child.badge}
                          </span>
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer da sidebar */}
      {!collapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            <p>Versão {state.config.version}</p>
            <p className="capitalize">{state.config.environment}</p>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar; 