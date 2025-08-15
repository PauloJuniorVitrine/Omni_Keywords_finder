/**
 * LazyLoader - Componente para gerenciar lazy loading com Suspense
 * 
 * Prompt: Implementação de lazy loading para Criticalidade 3.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { Suspense, lazy, ComponentType } from 'react';
import { Box, CircularProgress, Typography, Skeleton } from '@mui/material';

interface LazyLoaderProps {
  component: () => Promise<{ default: ComponentType<any> }>;
  fallback?: React.ReactNode;
  errorBoundary?: React.ComponentType<any>;
  preload?: boolean;
  timeout?: number;
  showSkeleton?: boolean;
  skeletonProps?: {
    variant?: 'text' | 'rectangular' | 'circular';
    width?: number | string;
    height?: number | string;
    rows?: number;
  };
}

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
}

const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError }) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    p={3}
    textAlign="center"
  >
    <Typography variant="h6" color="error" gutterBottom>
      Erro ao carregar componente
    </Typography>
    <Typography variant="body2" color="text.secondary" gutterBottom>
      {error.message}
    </Typography>
    <button onClick={resetError} style={{ marginTop: '1rem' }}>
      Tentar novamente
    </button>
  </Box>
);

const DefaultLoadingFallback: React.FC<{ showSkeleton?: boolean; skeletonProps?: any }> = ({ 
  showSkeleton = false, 
  skeletonProps = {} 
}) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    p={3}
    minHeight="200px"
  >
    {showSkeleton ? (
      <Box width="100%">
        <Skeleton variant="rectangular" width="100%" height={60} />
        <Skeleton variant="text" width="80%" />
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="40%" />
      </Box>
    ) : (
      <>
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Carregando...
        </Typography>
      </>
    )}
  </Box>
);

class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ComponentType<ErrorFallbackProps> },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('LazyLoader Error:', error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback;
      return <FallbackComponent error={this.state.error} resetError={this.resetError} />;
    }

    return this.props.children;
  }
}

const LazyLoader: React.FC<LazyLoaderProps> = ({
  component,
  fallback,
  errorBoundary = DefaultErrorFallback,
  preload = false,
  timeout = 10000,
  showSkeleton = false,
  skeletonProps = {}
}) => {
  const LazyComponent = lazy(component);

  // Preload logic
  React.useEffect(() => {
    if (preload) {
      const preloadComponent = async () => {
        try {
          await component();
        } catch (error) {
          console.warn('Preload failed:', error);
        }
      };
      preloadComponent();
    }
  }, [component, preload]);

  const LoadingFallback = fallback || (
    <DefaultLoadingFallback showSkeleton={showSkeleton} skeletonProps={skeletonProps} />
  );

  return (
    <ErrorBoundary fallback={errorBoundary}>
      <Suspense fallback={LoadingFallback}>
        <LazyComponent />
      </Suspense>
    </ErrorBoundary>
  );
};

export default LazyLoader; 