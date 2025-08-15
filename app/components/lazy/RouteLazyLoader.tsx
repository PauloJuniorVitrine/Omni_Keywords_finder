/**
 * RouteLazyLoader - Componente para lazy loading de rotas com code splitting
 * 
 * Prompt: Implementação de lazy loading para Criticalidade 3.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { lazy, Suspense } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface RouteLazyLoaderProps {
  routePath: string;
  componentPath: string;
  preloadOnHover?: boolean;
  preloadOnFocus?: boolean;
  showLoadingIndicator?: boolean;
  loadingText?: string;
}

const RouteLoadingFallback: React.FC<{ text?: string }> = ({ text = 'Carregando página...' }) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    minHeight="400px"
    p={4}
  >
    <CircularProgress size={50} />
    <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
      {text}
    </Typography>
  </Box>
);

const RouteLazyLoader: React.FC<RouteLazyLoaderProps> = ({
  routePath,
  componentPath,
  preloadOnHover = true,
  preloadOnFocus = true,
  showLoadingIndicator = true,
  loadingText
}) => {
  const [isPreloaded, setIsPreloaded] = React.useState(false);
  const [preloadError, setPreloadError] = React.useState<Error | null>(null);

  // Dynamic import function
  const loadComponent = () => {
    try {
      // Dynamic import based on component path
      return import(/* webpackChunkName: "[request]" */ `../${componentPath}`);
    } catch (error) {
      console.error(`Failed to load component for route ${routePath}:`, error);
      throw error;
    }
  };

  const LazyComponent = lazy(loadComponent);

  // Preload logic
  const preloadComponent = React.useCallback(async () => {
    if (isPreloaded || preloadError) return;

    try {
      await loadComponent();
      setIsPreloaded(true);
    } catch (error) {
      setPreloadError(error as Error);
      console.warn(`Preload failed for route ${routePath}:`, error);
    }
  }, [isPreloaded, preloadError, routePath]);

  // Preload on hover
  React.useEffect(() => {
    if (!preloadOnHover) return;

    const handleMouseEnter = () => {
      preloadComponent();
    };

    const element = document.querySelector(`[data-route="${routePath}"]`);
    if (element) {
      element.addEventListener('mouseenter', handleMouseEnter);
      return () => element.removeEventListener('mouseenter', handleMouseEnter);
    }
  }, [preloadOnHover, preloadComponent, routePath]);

  // Preload on focus
  React.useEffect(() => {
    if (!preloadOnFocus) return;

    const handleFocus = () => {
      preloadComponent();
    };

    const element = document.querySelector(`[data-route="${routePath}"]`);
    if (element) {
      element.addEventListener('focus', handleFocus);
      return () => element.removeEventListener('focus', handleFocus);
    }
  }, [preloadOnFocus, preloadComponent, routePath]);

  const LoadingComponent = showLoadingIndicator ? (
    <RouteLoadingFallback text={loadingText} />
  ) : null;

  return (
    <Suspense fallback={LoadingComponent}>
      <LazyComponent />
    </Suspense>
  );
};

export default RouteLazyLoader; 