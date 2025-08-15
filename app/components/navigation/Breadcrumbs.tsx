/**
 * Breadcrumbs.tsx
 * 
 * Sistema de breadcrumbs dinâmicos para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 7.1
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useMemo, useCallback } from 'react';
import { 
  ChevronRight, 
  Home, 
  Folder, 
  FileText, 
  Settings, 
  Users, 
  BarChart3,
  Search,
  Play,
  Database,
  Shield,
  Bell,
  HelpCircle
} from 'lucide-react';

// Types
export interface BreadcrumbItem {
  label: string;
  path: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  metadata?: Record<string, any>;
}

export interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  showHome?: boolean;
  maxItems?: number;
  separator?: React.ReactNode;
  className?: string;
  onItemClick?: (item: BreadcrumbItem, index: number) => void;
  truncateLongLabels?: boolean;
  showIcons?: boolean;
  responsive?: boolean;
  theme?: 'light' | 'dark' | 'auto';
}

// Route mapping for automatic breadcrumbs
const ROUTE_CONFIG = {
  '/': { label: 'Home', icon: <Home className="w-4 h-4" /> },
  '/dashboard': { label: 'Dashboard', icon: <BarChart3 className="w-4 h-4" /> },
  '/nichos': { label: 'Nichos', icon: <Folder className="w-4 h-4" /> },
  '/categorias': { label: 'Categorias', icon: <FileText className="w-4 h-4" /> },
  '/execucoes': { label: 'Execuções', icon: <Play className="w-4 h-4" /> },
  '/admin': { label: 'Administração', icon: <Settings className="w-4 h-4" /> },
  '/users': { label: 'Usuários', icon: <Users className="w-4 h-4" /> },
  '/analytics': { label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
  '/search': { label: 'Busca', icon: <Search className="w-4 h-4" /> },
  '/database': { label: 'Banco de Dados', icon: <Database className="w-4 h-4" /> },
  '/security': { label: 'Segurança', icon: <Shield className="w-4 h-4" /> },
  '/notifications': { label: 'Notificações', icon: <Bell className="w-4 h-4" /> },
  '/help': { label: 'Ajuda', icon: <HelpCircle className="w-4 h-4" /> },
};

// Dynamic route patterns
const DYNAMIC_ROUTES = {
  '/nichos/:id': { label: 'Detalhes do Nicho', icon: <Folder className="w-4 h-4" /> },
  '/categorias/:id': { label: 'Detalhes da Categoria', icon: <FileText className="w-4 h-4" /> },
  '/execucoes/:id': { label: 'Detalhes da Execução', icon: <Play className="w-4 h-4" /> },
  '/users/:id': { label: 'Perfil do Usuário', icon: <Users className="w-4 h-4" /> },
};

/**
 * Hook para gerar breadcrumbs automaticamente baseado na URL
 */
export const useBreadcrumbs = (currentPath: string = '/') => {
  return useMemo(() => {
    const pathSegments = currentPath.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [];
    
    // Adicionar home se necessário
    breadcrumbs.push({
      label: 'Home',
      path: '/',
      icon: <Home className="w-4 h-4" />
    });

    // Construir breadcrumbs dinamicamente
    let currentPathBuilder = '';
    
    pathSegments.forEach((segment, index) => {
      currentPathBuilder += `/${segment}`;
      
      // Verificar se é uma rota conhecida
      const routeConfig = ROUTE_CONFIG[currentPathBuilder as keyof typeof ROUTE_CONFIG];
      
      if (routeConfig) {
        breadcrumbs.push({
          label: routeConfig.label,
          path: currentPathBuilder,
          icon: routeConfig.icon
        });
      } else {
        // Verificar padrões dinâmicos
        const dynamicPattern = Object.keys(DYNAMIC_ROUTES).find(pattern => {
          const patternSegments = pattern.split('/').filter(Boolean);
          const currentSegments = currentPathBuilder.split('/').filter(Boolean);
          
          if (patternSegments.length !== currentSegments.length) return false;
          
          return patternSegments.every((patternSeg, i) => {
            return patternSeg.startsWith(':') || patternSeg === currentSegments[i];
          });
        });
        
        if (dynamicPattern) {
          const dynamicConfig = DYNAMIC_ROUTES[dynamicPattern as keyof typeof DYNAMIC_ROUTES];
          breadcrumbs.push({
            label: dynamicConfig.label,
            path: currentPathBuilder,
            icon: dynamicConfig.icon
          });
        } else {
          // Fallback para segmentos desconhecidos
          breadcrumbs.push({
            label: segment.charAt(0).toUpperCase() + segment.slice(1),
            path: currentPathBuilder,
            icon: <FileText className="w-4 h-4" />
          });
        }
      }
    });

    return breadcrumbs;
  }, [currentPath]);
};

/**
 * Componente principal de Breadcrumbs
 */
export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  showHome = true,
  maxItems = 5,
  separator = <ChevronRight className="w-4 h-4 text-gray-400" />,
  className = '',
  onItemClick,
  truncateLongLabels = true,
  showIcons = true,
  responsive = true,
  theme = 'auto'
}) => {
  // Se não foram fornecidos items, usar hook automático
  const currentPath = typeof window !== 'undefined' ? window.location.pathname : '/';
  const autoItems = useBreadcrumbs(currentPath);
  const breadcrumbItems = items || autoItems;

  // Filtrar e limitar items
  const displayItems = useMemo(() => {
    let filtered = breadcrumbItems;
    
    if (!showHome) {
      filtered = filtered.filter(item => item.path !== '/');
    }
    
    if (filtered.length > maxItems) {
      const start = filtered.slice(0, 1);
      const end = filtered.slice(-(maxItems - 2));
      const middle = [{ label: '...', path: '', disabled: true }];
      return [...start, ...middle, ...end];
    }
    
    return filtered;
  }, [breadcrumbItems, showHome, maxItems]);

  // Handler para clique nos items
  const handleItemClick = useCallback((item: BreadcrumbItem, index: number) => {
    if (item.disabled) return;
    
    if (item.onClick) {
      item.onClick();
    } else if (onItemClick) {
      onItemClick(item, index);
    } else if (item.path && item.path !== currentPath) {
      // Navegação padrão
      window.history.pushState({}, '', item.path);
      // Disparar evento de mudança de rota
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  }, [onItemClick, currentPath]);

  // Truncar labels longos
  const truncateLabel = useCallback((label: string) => {
    if (!truncateLongLabels || label.length <= 20) return label;
    return label.substring(0, 17) + '...';
  }, [truncateLongLabels]);

  // Classes de tema
  const getThemeClasses = () => {
    switch (theme) {
      case 'dark':
        return 'text-gray-300 bg-gray-800 border-gray-700';
      case 'light':
        return 'text-gray-700 bg-white border-gray-200';
      default:
        return 'text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700';
    }
  };

  return (
    <nav 
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${getThemeClasses()} ${className}`}
      aria-label="Breadcrumb"
    >
      <ol className="flex items-center space-x-2">
        {displayItems.map((item, index) => (
          <li key={`${item.path}-${index}`} className="flex items-center">
            {/* Separator */}
            {index > 0 && (
              <span className="mx-2" aria-hidden="true">
                {separator}
              </span>
            )}
            
            {/* Breadcrumb Item */}
            <button
              onClick={() => handleItemClick(item, index)}
              disabled={item.disabled}
              className={`
                flex items-center space-x-1 px-2 py-1 rounded-md transition-all duration-200
                ${item.disabled 
                  ? 'text-gray-400 cursor-not-allowed' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white cursor-pointer'
                }
                ${index === displayItems.length - 1 
                  ? 'font-semibold text-blue-600 dark:text-blue-400' 
                  : 'text-gray-600 dark:text-gray-400'
                }
                ${responsive ? 'text-sm sm:text-base' : 'text-base'}
              `}
              aria-current={index === displayItems.length - 1 ? 'page' : undefined}
            >
              {/* Icon */}
              {showIcons && item.icon && (
                <span className="flex-shrink-0">
                  {item.icon}
                </span>
              )}
              
              {/* Label */}
              <span className={responsive ? 'hidden sm:inline' : 'inline'}>
                {truncateLabel(item.label)}
              </span>
              
              {/* Mobile: apenas ícone para items não finais */}
              {responsive && index < displayItems.length - 1 && item.icon && (
                <span className="sm:hidden">
                  {item.icon}
                </span>
              )}
            </button>
          </li>
        ))}
      </ol>
      
      {/* Indicador de profundidade */}
      {displayItems.length > 3 && (
        <div className="ml-auto text-xs text-gray-500 dark:text-gray-400">
          {displayItems.length} níveis
        </div>
      )}
    </nav>
  );
};

/**
 * Componente de breadcrumbs compacto para espaços pequenos
 */
export const CompactBreadcrumbs: React.FC<BreadcrumbsProps> = (props) => {
  return (
    <Breadcrumbs
      {...props}
      maxItems={3}
      truncateLongLabels={true}
      responsive={true}
      className={`${props.className || ''} text-sm`}
    />
  );
};

/**
 * Componente de breadcrumbs com dropdown para items extras
 */
export const DropdownBreadcrumbs: React.FC<BreadcrumbsProps & {
  dropdownItems?: BreadcrumbItem[];
}> = ({ dropdownItems, ...props }) => {
  const [showDropdown, setShowDropdown] = React.useState(false);
  
  return (
    <div className="relative">
      <Breadcrumbs {...props} />
      
      {dropdownItems && dropdownItems.length > 0 && (
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="ml-2 p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            aria-label="Mostrar mais breadcrumbs"
          >
            <ChevronRight className="w-4 h-4 rotate-90" />
          </button>
          
          {showDropdown && (
            <div className="absolute top-full left-0 mt-1 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
              {dropdownItems.map((item, index) => (
                <button
                  key={index}
                  onClick={() => {
                    item.onClick?.();
                    setShowDropdown(false);
                  }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                >
                  {item.icon && <span>{item.icon}</span>}
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Breadcrumbs; 