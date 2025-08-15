/**
 * BreadcrumbProvider.tsx
 * 
 * Provider para gerenciamento de breadcrumbs
 * 
 * Tracing ID: BREADCRUMB_PROVIDER_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Gerenciamento de breadcrumbs
 * - Navegação hierárquica
 * - Integração com roteamento
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

interface Breadcrumb {
  label: string;
  path: string;
  active?: boolean;
}

interface BreadcrumbContextType {
  breadcrumbs: Breadcrumb[];
  updateBreadcrumbs: (breadcrumbs: Breadcrumb[]) => void;
  addBreadcrumb: (breadcrumb: Breadcrumb) => void;
  removeBreadcrumb: (path: string) => void;
  clearBreadcrumbs: () => void;
  setActiveBreadcrumb: (path: string) => void;
}

const BreadcrumbContext = createContext<BreadcrumbContextType | undefined>(undefined);

interface BreadcrumbProviderProps {
  children: ReactNode;
}

export const BreadcrumbProvider: React.FC<BreadcrumbProviderProps> = ({ children }) => {
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([]);

  const updateBreadcrumbs = useCallback((newBreadcrumbs: Breadcrumb[]) => {
    setBreadcrumbs(newBreadcrumbs);
  }, []);

  const addBreadcrumb = useCallback((breadcrumb: Breadcrumb) => {
    setBreadcrumbs(prev => {
      // Verificar se já existe um breadcrumb com o mesmo path
      const existingIndex = prev.findIndex(b => b.path === breadcrumb.path);
      
      if (existingIndex !== -1) {
        // Atualizar breadcrumb existente
        const updated = [...prev];
        updated[existingIndex] = { ...breadcrumb, active: true };
        // Marcar outros como inativos
        updated.forEach((b, index) => {
          if (index !== existingIndex) {
            b.active = false;
          }
        });
        return updated;
      } else {
        // Adicionar novo breadcrumb
        const updated = prev.map(b => ({ ...b, active: false }));
        return [...updated, { ...breadcrumb, active: true }];
      }
    });
  }, []);

  const removeBreadcrumb = useCallback((path: string) => {
    setBreadcrumbs(prev => {
      const filtered = prev.filter(b => b.path !== path);
      // Marcar o último como ativo
      if (filtered.length > 0) {
        filtered[filtered.length - 1].active = true;
      }
      return filtered;
    });
  }, []);

  const clearBreadcrumbs = useCallback(() => {
    setBreadcrumbs([]);
  }, []);

  const setActiveBreadcrumb = useCallback((path: string) => {
    setBreadcrumbs(prev => 
      prev.map(b => ({ ...b, active: b.path === path }))
    );
  }, []);

  const value: BreadcrumbContextType = {
    breadcrumbs,
    updateBreadcrumbs,
    addBreadcrumb,
    removeBreadcrumb,
    clearBreadcrumbs,
    setActiveBreadcrumb
  };

  return (
    <BreadcrumbContext.Provider value={value}>
      {children}
    </BreadcrumbContext.Provider>
  );
};

// Hook para usar o contexto
export const useBreadcrumbs = () => {
  const context = useContext(BreadcrumbContext);
  if (context === undefined) {
    throw new Error('useBreadcrumbs must be used within a BreadcrumbProvider');
  }
  return context;
};

// Componente de breadcrumbs
export const BreadcrumbNavigation: React.FC = () => {
  const { breadcrumbs } = useBreadcrumbs();

  if (breadcrumbs.length === 0) {
    return null;
  }

  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {breadcrumbs.map((breadcrumb, index) => (
          <li key={breadcrumb.path} className="flex items-center">
            {index > 0 && (
              <svg 
                className="w-4 h-4 text-gray-400 mx-2" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            )}
            <span className={`
              text-sm font-medium
              ${breadcrumb.active 
                ? 'text-blue-600 dark:text-blue-400' 
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }
            `}>
              {breadcrumb.label}
            </span>
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default BreadcrumbProvider; 