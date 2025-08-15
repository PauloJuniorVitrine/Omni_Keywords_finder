/**
 * Lazy Loading Components - Omni Keywords Finder
 * Tracing ID: LAZY_LOADING_20250127_001
 * 
 * Sistema de carregamento sob demanda para componentes pesados
 * Reduz bundle size inicial e melhora performance de carregamento
 */

import { lazy, Suspense } from 'react';

// Loading components
const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    <span className="ml-2 text-gray-600">Carregando...</span>
  </div>
);

const LoadingSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
);

// Dashboard Components - Lazy Loading
export const DashboardOverview = lazy(() => 
  import('../dashboard/DashboardOverview').then(module => ({
    default: module.DashboardOverview
  }))
);

export const DashboardAnalytics = lazy(() => 
  import('../dashboard/DashboardAnalytics').then(module => ({
    default: module.DashboardAnalytics
  }))
);

export const DashboardCharts = lazy(() => 
  import('../dashboard/DashboardCharts').then(module => ({
    default: module.DashboardCharts
  }))
);

// Analytics Components - Lazy Loading
export const AnalyticsOverview = lazy(() => 
  import('../analytics/AnalyticsOverview').then(module => ({
    default: module.AnalyticsOverview
  }))
);

export const AnalyticsCharts = lazy(() => 
  import('../analytics/AnalyticsCharts').then(module => ({
    default: module.AnalyticsCharts
  }))
);

export const AnalyticsReports = lazy(() => 
  import('../analytics/AnalyticsReports').then(module => ({
    default: module.AnalyticsReports
  }))
);

export const AnalyticsHeatmap = lazy(() => 
  import('../analytics/AnalyticsHeatmap').then(module => ({
    default: module.AnalyticsHeatmap
  }))
);

// Admin Components - Lazy Loading
export const AdminUsers = lazy(() => 
  import('../admin/AdminUsers').then(module => ({
    default: module.AdminUsers
  }))
);

export const AdminSettings = lazy(() => 
  import('../admin/AdminSettings').then(module => ({
    default: module.AdminSettings
  }))
);

export const AdminLogs = lazy(() => 
  import('../admin/AdminLogs').then(module => ({
    default: module.AdminLogs
  }))
);

export const AdminPerformance = lazy(() => 
  import('../admin/AdminPerformance').then(module => ({
    default: module.AdminPerformance
  }))
);

// Keywords Components - Lazy Loading
export const KeywordsAnalyzer = lazy(() => 
  import('../keywords/KeywordsAnalyzer').then(module => ({
    default: module.KeywordsAnalyzer
  }))
);

export const KeywordsGenerator = lazy(() => 
  import('../keywords/KeywordsGenerator').then(module => ({
    default: module.KeywordsGenerator
  }))
);

export const KeywordsOptimizer = lazy(() => 
  import('../keywords/KeywordsOptimizer').then(module => ({
    default: module.KeywordsOptimizer
  }))
);

// Advanced Components - Lazy Loading
export const AdvancedAnalytics = lazy(() => 
  import('../analytics/AdvancedAnalytics').then(module => ({
    default: module.AdvancedAnalytics
  }))
);

export const MLPredictions = lazy(() => 
  import('../ml/MLPredictions').then(module => ({
    default: module.MLPredictions
  }))
);

export const CompetitorAnalysis = lazy(() => 
  import('../competitors/CompetitorAnalysis').then(module => ({
    default: module.CompetitorAnalysis
  }))
);

// Wrapper component para lazy loading com Suspense
export const LazyComponent = ({ 
  component: Component, 
  fallback = <LoadingSpinner />,
  ...props 
}: {
  component: React.LazyExoticComponent<any>;
  fallback?: React.ReactNode;
  [key: string]: any;
}) => (
  <Suspense fallback={fallback}>
    <Component {...props} />
  </Suspense>
);

// HOC para lazy loading com error boundary
export const withLazyLoading = (Component: React.LazyExoticComponent<any>) => {
  return (props: any) => (
    <Suspense fallback={<LoadingSpinner />}>
      <Component {...props} />
    </Suspense>
  );
};

// Preload function para carregar componentes antecipadamente
export const preloadComponent = (componentLoader: () => Promise<any>) => {
  return () => {
    componentLoader();
  };
};

// Preload critical components
export const preloadCriticalComponents = () => {
  // Preload dashboard components when user is authenticated
  if (typeof window !== 'undefined') {
    const preloadDashboard = () => {
      import('../dashboard/DashboardOverview');
      import('../dashboard/DashboardAnalytics');
    };
    
    // Preload after 2 seconds of idle time
    setTimeout(preloadDashboard, 2000);
  }
};

// Lazy loading with intersection observer
export const useLazyLoad = (ref: React.RefObject<HTMLElement>, callback: () => void) => {
  React.useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            callback();
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [ref, callback]);
};

// Export all lazy components
export default {
  DashboardOverview,
  DashboardAnalytics,
  DashboardCharts,
  AnalyticsOverview,
  AnalyticsCharts,
  AnalyticsReports,
  AnalyticsHeatmap,
  AdminUsers,
  AdminSettings,
  AdminLogs,
  AdminPerformance,
  KeywordsAnalyzer,
  KeywordsGenerator,
  KeywordsOptimizer,
  AdvancedAnalytics,
  MLPredictions,
  CompetitorAnalysis,
  LazyComponent,
  withLazyLoading,
  preloadComponent,
  preloadCriticalComponents,
  useLazyLoad
}; 