/**
 * MicroInteractions.tsx
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Criticalidade 4.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Componente responsável por micro-interações da interface
 * - Hover effects
 * - Loading animations  
 * - Page transitions
 */

import React from 'react';
import { styled, keyframes } from '@mui/material/styles';
import { Box, CircularProgress, Fade, Grow, Slide } from '@mui/material';

// ===== ANIMAÇÕES CSS =====
const pulseAnimation = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const shimmerAnimation = keyframes`
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
`;

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

// ===== COMPONENTES ESTILIZADOS =====
const HoverableCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[1],
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  cursor: 'pointer',
  
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
    backgroundColor: theme.palette.action.hover,
  },
  
  '&:active': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  }
}));

const LoadingShimmer = styled(Box)(({ theme }) => ({
  width: '100%',
  height: '20px',
  background: `linear-gradient(90deg, 
    ${theme.palette.grey[200]} 25%, 
    ${theme.palette.grey[100]} 50%, 
    ${theme.palette.grey[200]} 75%)`,
  backgroundSize: '200px 100%',
  animation: `${shimmerAnimation} 1.5s infinite`,
  borderRadius: theme.shape.borderRadius,
}));

const PulseButton = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  cursor: 'pointer',
  display: 'inline-flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  transition: 'all 0.2s ease',
  
  '&:hover': {
    animation: `${pulseAnimation} 0.6s ease-in-out`,
    backgroundColor: theme.palette.primary.dark,
  }
}));

const AnimatedContainer = styled(Box)(({ theme }) => ({
  animation: `${fadeInUp} 0.6s ease-out`,
}));

// ===== INTERFACES =====
interface MicroInteractionsProps {
  children: React.ReactNode;
  variant?: 'hover' | 'pulse' | 'fade' | 'slide';
  delay?: number;
}

interface LoadingAnimationProps {
  size?: 'small' | 'medium' | 'large';
  variant?: 'circular' | 'shimmer' | 'dots';
  message?: string;
}

interface PageTransitionProps {
  children: React.ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  timeout?: number;
}

// ===== COMPONENTES PRINCIPAIS =====

/**
 * Componente para hover effects e micro-interações
 */
export const HoverEffect: React.FC<MicroInteractionsProps> = ({ 
  children, 
  variant = 'hover',
  delay = 0 
}) => {
  const getTransitionComponent = () => {
    switch (variant) {
      case 'pulse':
        return (
          <PulseButton>
            {children}
          </PulseButton>
        );
      case 'fade':
        return (
          <Fade in timeout={300 + delay}>
            <Box>{children}</Box>
          </Fade>
        );
      case 'slide':
        return (
          <Slide direction="up" in timeout={400 + delay}>
            <Box>{children}</Box>
          </Slide>
        );
      default:
        return (
          <HoverableCard>
            {children}
          </HoverableCard>
        );
    }
  };

  return getTransitionComponent();
};

/**
 * Componente para animações de loading
 */
export const LoadingAnimation: React.FC<LoadingAnimationProps> = ({
  size = 'medium',
  variant = 'circular',
  message = 'Carregando...'
}) => {
  const sizeMap = {
    small: 20,
    medium: 40,
    large: 60
  };

  const renderLoadingVariant = () => {
    switch (variant) {
      case 'shimmer':
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <LoadingShimmer />
            <LoadingShimmer sx={{ width: '70%' }} />
            <LoadingShimmer sx={{ width: '50%' }} />
          </Box>
        );
      case 'dots':
        return (
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {[0, 1, 2].map((index) => (
              <Box
                key={index}
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: 'primary.main',
                  animation: `${pulseAnimation} 1.4s ease-in-out infinite`,
                  animationDelay: `${index * 0.2}s`
                }}
              />
            ))}
          </Box>
        );
      default:
        return (
          <CircularProgress 
            size={sizeMap[size]} 
            thickness={4}
            sx={{
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              }
            }}
          />
        );
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      gap: 2,
      padding: 2
    }}>
      {renderLoadingVariant()}
      {message && (
        <Box sx={{ 
          color: 'text.secondary', 
          fontSize: '0.875rem',
          animation: `${fadeInUp} 0.6s ease-out 0.2s both`
        }}>
          {message}
        </Box>
      )}
    </Box>
  );
};

/**
 * Componente para transições de página
 */
export const PageTransition: React.FC<PageTransitionProps> = ({
  children,
  direction = 'up',
  timeout = 300
}) => {
  return (
    <Grow in timeout={timeout}>
      <AnimatedContainer>
        {children}
      </AnimatedContainer>
    </Grow>
  );
};

/**
 * Hook para controlar animações
 */
export const useMicroInteractions = () => {
  const [isAnimating, setIsAnimating] = React.useState(false);

  const triggerAnimation = React.useCallback((duration: number = 300) => {
    setIsAnimating(true);
    setTimeout(() => setIsAnimating(false), duration);
  }, []);

  return {
    isAnimating,
    triggerAnimation
  };
};

export default {
  HoverEffect,
  LoadingAnimation,
  PageTransition,
  useMicroInteractions
}; 