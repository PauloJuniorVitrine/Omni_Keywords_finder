/**
 * TransitionProvider.tsx
 * 
 * Provider de transições com animações otimizadas e configuração flexível
 * 
 * Tracing ID: UI_TRANSITION_PROVIDER_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 15.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useBranding } from '@/components/branding/BrandingProvider';

// Tipos de transições
type TransitionType = 
  | 'fade'
  | 'slide'
  | 'scale'
  | 'rotate'
  | 'flip'
  | 'bounce'
  | 'zoom'
  | 'slide-up'
  | 'slide-down'
  | 'slide-left'
  | 'slide-right'
  | 'custom';

// Direções de transição
type TransitionDirection = 'in' | 'out' | 'both';

// Configuração de transição
interface TransitionConfig {
  type: TransitionType;
  duration: number;
  delay: number;
  easing: string;
  direction: TransitionDirection;
  customKeyframes?: string;
  customProperties?: Record<string, string>;
}

// Estado de transição
interface TransitionState {
  isTransitioning: boolean;
  currentTransition: TransitionConfig | null;
  transitionQueue: TransitionConfig[];
}

// Contexto de transições
interface TransitionContextType {
  state: TransitionState;
  startTransition: (config: TransitionConfig) => Promise<void>;
  stopTransition: () => void;
  clearQueue: () => void;
  isTransitioning: boolean;
  addToQueue: (config: TransitionConfig) => void;
  processQueue: () => void;
}

const TransitionContext = createContext<TransitionContextType | undefined>(undefined);

// Hook para usar transições
export const useTransitions = () => {
  const context = useContext(TransitionContext);
  if (!context) {
    throw new Error('useTransitions must be used within a TransitionProvider');
  }
  return context;
};

// Props do provider
interface TransitionProviderProps {
  children: ReactNode;
  defaultConfig?: Partial<TransitionConfig>;
  enableReducedMotion?: boolean;
  maxConcurrentTransitions?: number;
  autoProcessQueue?: boolean;
}

// Configuração padrão
const defaultTransitionConfig: TransitionConfig = {
  type: 'fade',
  duration: 300,
  delay: 0,
  easing: 'ease-in-out',
  direction: 'both'
};

// Configurações predefinidas
const predefinedTransitions: Record<string, TransitionConfig> = {
  fade: {
    type: 'fade',
    duration: 300,
    delay: 0,
    easing: 'ease-in-out',
    direction: 'both'
  },
  slide: {
    type: 'slide',
    duration: 400,
    delay: 0,
    easing: 'ease-out',
    direction: 'both'
  },
  scale: {
    type: 'scale',
    duration: 250,
    delay: 0,
    easing: 'ease-out',
    direction: 'both'
  },
  bounce: {
    type: 'bounce',
    duration: 600,
    delay: 0,
    easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    direction: 'both'
  },
  zoom: {
    type: 'zoom',
    duration: 200,
    delay: 0,
    easing: 'ease-out',
    direction: 'both'
  }
};

export const TransitionProvider: React.FC<TransitionProviderProps> = ({
  children,
  defaultConfig = {},
  enableReducedMotion = true,
  maxConcurrentTransitions = 3,
  autoProcessQueue = true
}) => {
  const { config: brandingConfig } = useBranding();
  const [state, setState] = useState<TransitionState>({
    isTransitioning: false,
    currentTransition: null,
    transitionQueue: []
  });

  const [activeTransitions, setActiveTransitions] = useState<Set<string>>(new Set());
  const [reducedMotion, setReducedMotion] = useState(false);

  // Detectar preferência de movimento reduzido
  useEffect(() => {
    if (enableReducedMotion) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      setReducedMotion(mediaQuery.matches);

      const handleChange = (event: MediaQueryListEvent) => {
        setReducedMotion(event.matches);
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [enableReducedMotion]);

  // Iniciar transição
  const startTransition = useCallback(async (config: TransitionConfig): Promise<void> => {
    return new Promise((resolve) => {
      // Se movimento reduzido está ativado, pular animação
      if (reducedMotion) {
        resolve();
        return;
      }

      const transitionId = Math.random().toString(36).substr(2, 9);
      
      setState(prev => ({
        ...prev,
        isTransitioning: true,
        currentTransition: config
      }));

      setActiveTransitions(prev => new Set(prev).add(transitionId));

      // Verificar limite de transições simultâneas
      if (activeTransitions.size >= maxConcurrentTransitions) {
        setState(prev => ({
          ...prev,
          transitionQueue: [...prev.transitionQueue, config]
        }));
        resolve();
        return;
      }

      // Executar transição
      const duration = config.duration || defaultTransitionConfig.duration;
      const delay = config.delay || defaultTransitionConfig.delay;

      setTimeout(() => {
        setState(prev => ({
          ...prev,
          isTransitioning: false,
          currentTransition: null
        }));

        setActiveTransitions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transitionId);
          return newSet;
        });

        resolve();
      }, duration + delay);
    });
  }, [reducedMotion, activeTransitions.size, maxConcurrentTransitions]);

  // Parar transição atual
  const stopTransition = useCallback(() => {
    setState(prev => ({
      ...prev,
      isTransitioning: false,
      currentTransition: null
    }));
    setActiveTransitions(new Set());
  }, []);

  // Limpar fila de transições
  const clearQueue = useCallback(() => {
    setState(prev => ({
      ...prev,
      transitionQueue: []
    }));
  }, []);

  // Adicionar à fila
  const addToQueue = useCallback((config: TransitionConfig) => {
    setState(prev => ({
      ...prev,
      transitionQueue: [...prev.transitionQueue, config]
    }));
  }, []);

  // Processar fila
  const processQueue = useCallback(async () => {
    if (state.transitionQueue.length === 0) return;

    const nextTransition = state.transitionQueue[0];
    setState(prev => ({
      ...prev,
      transitionQueue: prev.transitionQueue.slice(1)
    }));

    await startTransition(nextTransition);
  }, [state.transitionQueue, startTransition]);

  // Processar fila automaticamente
  useEffect(() => {
    if (autoProcessQueue && state.transitionQueue.length > 0 && activeTransitions.size < maxConcurrentTransitions) {
      processQueue();
    }
  }, [autoProcessQueue, state.transitionQueue, activeTransitions.size, maxConcurrentTransitions, processQueue]);

  const contextValue: TransitionContextType = {
    state,
    startTransition,
    stopTransition,
    clearQueue,
    isTransitioning: state.isTransitioning,
    addToQueue,
    processQueue
  };

  return (
    <TransitionContext.Provider value={contextValue}>
      {children}
    </TransitionContext.Provider>
  );
};

// Componente de transição
interface TransitionProps {
  children: ReactNode;
  type?: TransitionType;
  duration?: number;
  delay?: number;
  easing?: string;
  direction?: TransitionDirection;
  show?: boolean;
  className?: string;
  onEnter?: () => void;
  onExit?: () => void;
  onEntered?: () => void;
  onExited?: () => void;
  customKeyframes?: string;
  customProperties?: Record<string, string>;
}

export const Transition: React.FC<TransitionProps> = ({
  children,
  type = 'fade',
  duration,
  delay,
  easing,
  direction = 'both',
  show = true,
  className = '',
  onEnter,
  onExit,
  onEntered,
  onExited,
  customKeyframes,
  customProperties
}) => {
  const { startTransition } = useTransitions();
  const [isVisible, setIsVisible] = useState(show);
  const [isAnimating, setIsAnimating] = useState(false);

  // Configuração da transição
  const config: TransitionConfig = {
    type,
    duration: duration || predefinedTransitions[type]?.duration || defaultTransitionConfig.duration,
    delay: delay || predefinedTransitions[type]?.delay || defaultTransitionConfig.delay,
    easing: easing || predefinedTransitions[type]?.easing || defaultTransitionConfig.easing,
    direction,
    customKeyframes,
    customProperties
  };

  // Gerar classes CSS baseadas no tipo de transição
  const getTransitionClasses = () => {
    const baseClasses = 'transition-all duration-300 ease-in-out';
    
    switch (type) {
      case 'fade':
        return `${baseClasses} ${isVisible ? 'opacity-100' : 'opacity-0'}`;
      
      case 'slide':
        return `${baseClasses} ${isVisible ? 'translate-x-0' : 'translate-x-full'}`;
      
      case 'slide-up':
        return `${baseClasses} ${isVisible ? 'translate-y-0' : 'translate-y-full'}`;
      
      case 'slide-down':
        return `${baseClasses} ${isVisible ? 'translate-y-0' : '-translate-y-full'}`;
      
      case 'slide-left':
        return `${baseClasses} ${isVisible ? 'translate-x-0' : '-translate-x-full'}`;
      
      case 'slide-right':
        return `${baseClasses} ${isVisible ? 'translate-x-0' : 'translate-x-full'}`;
      
      case 'scale':
        return `${baseClasses} ${isVisible ? 'scale-100' : 'scale-0'}`;
      
      case 'zoom':
        return `${baseClasses} ${isVisible ? 'scale-100' : 'scale-50'}`;
      
      case 'rotate':
        return `${baseClasses} ${isVisible ? 'rotate-0' : 'rotate-180'}`;
      
      case 'flip':
        return `${baseClasses} ${isVisible ? 'rotate-y-0' : 'rotate-y-180'}`;
      
      case 'bounce':
        return `${baseClasses} ${isVisible ? 'animate-bounce' : 'scale-0'}`;
      
      case 'custom':
        return baseClasses;
      
      default:
        return baseClasses;
    }
  };

  // Efeito para controlar visibilidade
  useEffect(() => {
    if (show !== isVisible) {
      setIsAnimating(true);
      
      if (show) {
        // Entrada
        onEnter?.();
        setIsVisible(true);
        
        startTransition(config).then(() => {
          setIsAnimating(false);
          onEntered?.();
        });
      } else {
        // Saída
        onExit?.();
        
        startTransition(config).then(() => {
          setIsVisible(false);
          setIsAnimating(false);
          onExited?.();
        });
      }
    }
  }, [show, isVisible, config, startTransition, onEnter, onExit, onEntered, onExited]);

  // Aplicar propriedades customizadas
  const customStyles: React.CSSProperties = {
    transitionDuration: `${config.duration}ms`,
    transitionDelay: `${config.delay}ms`,
    transitionTimingFunction: config.easing,
    ...customProperties
  };

  if (!isVisible && !isAnimating) {
    return null;
  }

  return (
    <div
      className={`${getTransitionClasses()} ${className}`}
      style={customStyles}
    >
      {children}
    </div>
  );
};

// Hook para animações de entrada
export const useEnterAnimation = (config?: Partial<TransitionConfig>) => {
  const { startTransition } = useTransitions();
  const [hasEntered, setHasEntered] = useState(false);

  const enter = useCallback(async () => {
    if (!hasEntered) {
      await startTransition({
        ...defaultTransitionConfig,
        ...config,
        direction: 'in'
      });
      setHasEntered(true);
    }
  }, [hasEntered, startTransition, config]);

  return { enter, hasEntered };
};

// Hook para animações de saída
export const useExitAnimation = (config?: Partial<TransitionConfig>) => {
  const { startTransition } = useTransitions();
  const [isExiting, setIsExiting] = useState(false);

  const exit = useCallback(async () => {
    if (!isExiting) {
      setIsExiting(true);
      await startTransition({
        ...defaultTransitionConfig,
        ...config,
        direction: 'out'
      });
    }
  }, [isExiting, startTransition, config]);

  return { exit, isExiting };
};

// Componente de transição de página
interface PageTransitionProps {
  children: ReactNode;
  route: string;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({
  children,
  route,
  className = ''
}) => {
  const [currentRoute, setCurrentRoute] = useState(route);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    if (route !== currentRoute) {
      setIsTransitioning(true);
      
      // Simular transição de página
      setTimeout(() => {
        setCurrentRoute(route);
        setIsTransitioning(false);
      }, 300);
    }
  }, [route, currentRoute]);

  return (
    <Transition
      type="fade"
      show={!isTransitioning}
      className={className}
    >
      {children}
    </Transition>
  );
};

// Componente de transição de lista
interface ListTransitionProps {
  children: ReactNode;
  className?: string;
  staggerDelay?: number;
}

export const ListTransition: React.FC<ListTransitionProps> = ({
  children,
  className = '',
  staggerDelay = 50
}) => {
  const childrenArray = React.Children.toArray(children);

  return (
    <div className={className}>
      {childrenArray.map((child, index) => (
        <Transition
          key={index}
          type="slide-up"
          delay={index * staggerDelay}
          show={true}
        >
          {child}
        </Transition>
      ))}
    </div>
  );
};

export default TransitionProvider; 