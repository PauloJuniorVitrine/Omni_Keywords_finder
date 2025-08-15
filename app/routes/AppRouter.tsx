/**
 * AppRouter.tsx
 * 
 * Sistema de roteamento centralizado para Omni Keywords Finder
 * 
 * Tracing ID: ROUTER_001_20250127
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 16.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Roteamento centralizado
 * - Lazy loading de componentes
 * - Proteção de rotas
 * - Integração com breadcrumbs
 * - Fallback para rotas não encontradas
 */

import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { usePermissions } from '../hooks/usePermissions';
import { LoadingSpinner } from '../components/shared/LoadingSpinner';
import { ErrorBoundary } from '../components/error/ErrorBoundary';
import { RouteGuard } from './RouteGuard';
import { BreadcrumbProvider } from '../components/navigation/BreadcrumbProvider';

// Lazy loading dos componentes principais
const Dashboard = lazy(() => import('../pages/dashboard/Dashboard'));
const NichosDashboard = lazy(() => import('../components/nichos/NichosDashboard'));
const CategoriasDashboard = lazy(() => import('../components/categorias/CategoriasDashboard'));
const ExecucoesDashboard = lazy(() => import('../components/execucoes/ExecucoesDashboard'));
const AdminDashboard = lazy(() => import('../components/admin/AdminDashboard'));
const AnalyticsDashboard = lazy(() => import('../components/analytics/AnalyticsDashboard'));
const WebhooksDashboard = lazy(() => import('../components/webhooks/WebhooksDashboard'));
const TemplatesDashboard = lazy(() => import('../components/templates/TemplatesDashboard'));
const CredentialsDashboard = lazy(() => import('../components/credentials/CredentialsDashboard'));
const GovernancaDashboard = lazy(() => import('../components/governanca/GovernancaDashboard'));

// Lazy loading dos formulários
const NichoForm = lazy(() => import('../components/nichos/NichoForm'));
const CategoriaForm = lazy(() => import('../components/categorias/CategoriaForm'));
const ExecucaoForm = lazy(() => import('../components/execucoes/ExecucaoForm'));
const WebhookForm = lazy(() => import('../components/webhooks/WebhookForm'));
const TemplateEditor = lazy(() => import('../components/templates/TemplateEditor'));
const CredentialForm = lazy(() => import('../components/credentials/CredentialForm'));

// Lazy loading das páginas de detalhes
const NichoDetails = lazy(() => import('../components/nichos/NichoDetails'));
const CategoriaDetails = lazy(() => import('../components/categorias/CategoriaDetails'));
const ExecucaoDetails = lazy(() => import('../components/execucoes/ExecucaoDetails'));

// Lazy loading das páginas de erro
const NotFound = lazy(() => import('../components/error/NotFound'));
const Unauthorized = lazy(() => import('../components/error/Unauthorized'));

// Componente de loading para lazy loading
const LazyLoadingFallback: React.FC = () => (
  <div className="flex items-center justify-center min-h-screen">
    <LoadingSpinner size="lg" />
  </div>
);

// Configuração das rotas
const routeConfig = {
  public: [
    {
      path: '/',
      element: <Navigate to="/dashboard" replace />,
      breadcrumb: 'Início'
    }
  ],
  protected: [
    {
      path: '/dashboard',
      element: <Dashboard />,
      breadcrumb: 'Dashboard',
      permissions: ['dashboard:read']
    },
    {
      path: '/nichos',
      element: <NichosDashboard />,
      breadcrumb: 'Nichos',
      permissions: ['nichos:read']
    },
    {
      path: '/nichos/novo',
      element: <NichoForm />,
      breadcrumb: 'Novo Nicho',
      permissions: ['nichos:create']
    },
    {
      path: '/nichos/:id',
      element: <NichoDetails />,
      breadcrumb: 'Detalhes do Nicho',
      permissions: ['nichos:read']
    },
    {
      path: '/nichos/:id/editar',
      element: <NichoForm />,
      breadcrumb: 'Editar Nicho',
      permissions: ['nichos:update']
    },
    {
      path: '/categorias',
      element: <CategoriasDashboard />,
      breadcrumb: 'Categorias',
      permissions: ['categorias:read']
    },
    {
      path: '/categorias/nova',
      element: <CategoriaForm />,
      breadcrumb: 'Nova Categoria',
      permissions: ['categorias:create']
    },
    {
      path: '/categorias/:id',
      element: <CategoriaDetails />,
      breadcrumb: 'Detalhes da Categoria',
      permissions: ['categorias:read']
    },
    {
      path: '/categorias/:id/editar',
      element: <CategoriaForm />,
      breadcrumb: 'Editar Categoria',
      permissions: ['categorias:update']
    },
    {
      path: '/execucoes',
      element: <ExecucoesDashboard />,
      breadcrumb: 'Execuções',
      permissions: ['execucoes:read']
    },
    {
      path: '/execucoes/nova',
      element: <ExecucaoForm />,
      breadcrumb: 'Nova Execução',
      permissions: ['execucoes:create']
    },
    {
      path: '/execucoes/:id',
      element: <ExecucaoDetails />,
      breadcrumb: 'Detalhes da Execução',
      permissions: ['execucoes:read']
    },
    {
      path: '/admin',
      element: <AdminDashboard />,
      breadcrumb: 'Administração',
      permissions: ['admin:read']
    },
    {
      path: '/analytics',
      element: <AnalyticsDashboard />,
      breadcrumb: 'Analytics',
      permissions: ['analytics:read']
    },
    {
      path: '/webhooks',
      element: <WebhooksDashboard />,
      breadcrumb: 'Webhooks',
      permissions: ['webhooks:read']
    },
    {
      path: '/webhooks/novo',
      element: <WebhookForm />,
      breadcrumb: 'Novo Webhook',
      permissions: ['webhooks:create']
    },
    {
      path: '/templates',
      element: <TemplatesDashboard />,
      breadcrumb: 'Templates',
      permissions: ['templates:read']
    },
    {
      path: '/templates/editor',
      element: <TemplateEditor />,
      breadcrumb: 'Editor de Templates',
      permissions: ['templates:create']
    },
    {
      path: '/credentials',
      element: <CredentialsDashboard />,
      breadcrumb: 'Credenciais',
      permissions: ['credentials:read']
    },
    {
      path: '/credentials/nova',
      element: <CredentialForm />,
      breadcrumb: 'Nova Credencial',
      permissions: ['credentials:create']
    },
    {
      path: '/governanca',
      element: <GovernancaDashboard />,
      breadcrumb: 'Governança',
      permissions: ['governanca:read']
    }
  ],
  error: [
    {
      path: '/unauthorized',
      element: <Unauthorized />,
      breadcrumb: 'Não Autorizado'
    },
    {
      path: '*',
      element: <NotFound />,
      breadcrumb: 'Página Não Encontrada'
    }
  ]
};

// Hook para gerenciar breadcrumbs dinamicamente
const useBreadcrumbNavigation = () => {
  const { updateBreadcrumbs } = React.useContext(BreadcrumbProvider);
  
  React.useEffect(() => {
    const currentPath = window.location.pathname;
    const route = [...routeConfig.public, ...routeConfig.protected, ...routeConfig.error]
      .find(r => r.path === currentPath || (r.path.includes(':') && currentPath.match(r.path.replace(/:[^/]+/g, '[^/]+'))));
    
    if (route?.breadcrumb) {
      updateBreadcrumbs([{ label: route.breadcrumb, path: currentPath }]);
    }
  }, [updateBreadcrumbs]);
};

// Componente principal do roteador
export const AppRouter: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const { hasPermission } = usePermissions();
  
  useBreadcrumbNavigation();

  // Loading inicial
  if (isLoading) {
    return <LazyLoadingFallback />;
  }

  return (
    <Router>
      <ErrorBoundary>
        <BreadcrumbProvider>
          <Suspense fallback={<LazyLoadingFallback />}>
            <Routes>
              {/* Rotas públicas */}
              {routeConfig.public.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={route.element}
                />
              ))}

              {/* Rotas protegidas */}
              {routeConfig.protected.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={
                    <RouteGuard
                      isAuthenticated={isAuthenticated}
                      requiredPermissions={route.permissions}
                      hasPermission={hasPermission}
                    >
                      {route.element}
                    </RouteGuard>
                  }
                />
              ))}

              {/* Rotas de erro */}
              {routeConfig.error.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={route.element}
                />
              ))}
            </Routes>
          </Suspense>
        </BreadcrumbProvider>
      </ErrorBoundary>
    </Router>
  );
};

// Hook para navegação programática
export const useAppNavigation = () => {
  const navigate = useNavigate();
  
  const navigateTo = React.useCallback((path: string, options?: { replace?: boolean; state?: any }) => {
    navigate(path, options);
  }, [navigate]);

  const goBack = React.useCallback(() => {
    navigate(-1);
  }, [navigate]);

  const goForward = React.useCallback(() => {
    navigate(1);
  }, [navigate]);

  return {
    navigateTo,
    goBack,
    goForward
  };
};

// Hook para verificar permissões de rota
export const useRoutePermissions = (requiredPermissions: string[]) => {
  const { hasPermission } = usePermissions();
  
  return React.useMemo(() => {
    return requiredPermissions.every(permission => hasPermission(permission));
  }, [requiredPermissions, hasPermission]);
};

// Hook para obter informações da rota atual
export const useCurrentRoute = () => {
  const location = useLocation();
  
  return React.useMemo(() => {
    const currentPath = location.pathname;
    const allRoutes = [...routeConfig.public, ...routeConfig.protected, ...routeConfig.error];
    
    return allRoutes.find(route => 
      route.path === currentPath || 
      (route.path.includes(':') && currentPath.match(route.path.replace(/:[^/]+/g, '[^/]+')))
    );
  }, [location.pathname]);
};

export default AppRouter; 