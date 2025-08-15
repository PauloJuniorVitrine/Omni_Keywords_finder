import { useState, useEffect, useRef, useCallback } from 'react';

export type AnimationType = 
  | 'fadeIn' | 'fadeOut' | 'slideIn' | 'slideOut' | 'bounce' | 'pulse' | 'shake'
  | 'scaleIn' | 'scaleOut' | 'rotate' | 'flip' | 'zoomIn' | 'zoomOut';

export type AnimationEasing = 
  | 'linear' | 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out'
  | 'bounce' | 'elastic' | 'cubic-bezier';

export interface AnimationConfig {
  type: AnimationType;
  duration?: number;
  delay?: number;
  easing?: AnimationEasing;
  repeat?: number | 'infinite';
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';
  fillMode?: 'none' | 'forwards' | 'backwards' | 'both';
}

export interface AnimationState {
  isAnimating: boolean;
  isVisible: boolean;
  hasCompleted: boolean;
  progress: number;
}

export interface UseAnimationReturn {
  state: AnimationState;
  start: () => void;
  stop: () => void;
  reset: () => void;
  toggle: () => void;
  setConfig: (config: Partial<AnimationConfig>) => void;
  animationStyles: React.CSSProperties;
}

export const useAnimation = (
  initialConfig: AnimationConfig,
  trigger: 'manual' | 'onMount' | 'onScroll' | 'onHover' | 'onClick' = 'manual'
): UseAnimationReturn => {
  const [config, setConfig] = useState<AnimationConfig>(initialConfig);
  const [state, setState] = useState<AnimationState>({
    isAnimating: false,
    isVisible: false,
    hasCompleted: false,
    progress: 0
  });

  const elementRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<Animation | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const getKeyframes = useCallback((type: AnimationType) => {
    switch (type) {
      case 'fadeIn':
        return [
          { opacity: 0 },
          { opacity: 1 }
        ];
      
      case 'fadeOut':
        return [
          { opacity: 1 },
          { opacity: 0 }
        ];
      
      case 'slideIn':
        return [
          { transform: 'translateX(-100%)', opacity: 0 },
          { transform: 'translateX(0)', opacity: 1 }
        ];
      
      case 'slideOut':
        return [
          { transform: 'translateX(0)', opacity: 1 },
          { transform: 'translateX(100%)', opacity: 0 }
        ];
      
      case 'bounce':
        return [
          { transform: 'translateY(0)' },
          { transform: 'translateY(-20px)' },
          { transform: 'translateY(0)' }
        ];
      
      case 'pulse':
        return [
          { transform: 'scale(1)' },
          { transform: 'scale(1.1)' },
          { transform: 'scale(1)' }
        ];
      
      case 'shake':
        return [
          { transform: 'translateX(0)' },
          { transform: 'translateX(-10px)' },
          { transform: 'translateX(10px)' },
          { transform: 'translateX(-10px)' },
          { transform: 'translateX(10px)' },
          { transform: 'translateX(0)' }
        ];
      
      case 'scaleIn':
        return [
          { transform: 'scale(0)', opacity: 0 },
          { transform: 'scale(1)', opacity: 1 }
        ];
      
      case 'scaleOut':
        return [
          { transform: 'scale(1)', opacity: 1 },
          { transform: 'scale(0)', opacity: 0 }
        ];
      
      case 'rotate':
        return [
          { transform: 'rotate(0deg)' },
          { transform: 'rotate(360deg)' }
        ];
      
      case 'flip':
        return [
          { transform: 'rotateY(0deg)' },
          { transform: 'rotateY(180deg)' }
        ];
      
      case 'zoomIn':
        return [
          { transform: 'scale(0.5)', opacity: 0 },
          { transform: 'scale(1)', opacity: 1 }
        ];
      
      case 'zoomOut':
        return [
          { transform: 'scale(1)', opacity: 1 },
          { transform: 'scale(0.5)', opacity: 0 }
        ];
      
      default:
        return [
          { opacity: 0 },
          { opacity: 1 }
        ];
    }
  }, []);

  const getEasingFunction = useCallback((easing: AnimationEasing) => {
    switch (easing) {
      case 'bounce':
        return 'cubic-bezier(0.68, -0.55, 0.265, 1.55)';
      case 'elastic':
        return 'cubic-bezier(0.175, 0.885, 0.32, 1.275)';
      default:
        return easing;
    }
  }, []);

  const start = useCallback(() => {
    if (!elementRef.current || state.isAnimating) return;

    setState(prev => ({
      ...prev,
      isAnimating: true,
      isVisible: true,
      hasCompleted: false,
      progress: 0
    }));

    const keyframes = getKeyframes(config.type);
    const timing = {
      duration: config.duration || 1000,
      delay: config.delay || 0,
      easing: getEasingFunction(config.easing || 'ease-out'),
      iterations: config.repeat === 'infinite' ? Infinity : (config.repeat || 1),
      direction: config.direction || 'normal',
      fill: config.fillMode || 'forwards'
    };

    animationRef.current = elementRef.current.animate(keyframes, timing);

    animationRef.current.onfinish = () => {
      setState(prev => ({
        ...prev,
        isAnimating: false,
        hasCompleted: true,
        progress: 100
      }));
    };

    animationRef.current.oncancel = () => {
      setState(prev => ({
        ...prev,
        isAnimating: false
      }));
    };
  }, [config, state.isAnimating, getKeyframes, getEasingFunction]);

  const stop = useCallback(() => {
    if (animationRef.current) {
      animationRef.current.cancel();
    }
    setState(prev => ({
      ...prev,
      isAnimating: false
    }));
  }, []);

  const reset = useCallback(() => {
    stop();
    setState({
      isAnimating: false,
      isVisible: false,
      hasCompleted: false,
      progress: 0
    });
  }, [stop]);

  const toggle = useCallback(() => {
    if (state.isAnimating) {
      stop();
    } else {
      start();
    }
  }, [state.isAnimating, start, stop]);

  const updateConfig = useCallback((newConfig: Partial<AnimationConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
  }, []);

  // Handle different triggers
  useEffect(() => {
    if (trigger === 'onMount') {
      start();
    }
  }, [trigger, start]);

  useEffect(() => {
    if (trigger === 'onScroll' && elementRef.current) {
      observerRef.current = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            start();
            observerRef.current?.disconnect();
          }
        },
        { threshold: 0.1 }
      );

      observerRef.current.observe(elementRef.current);

      return () => {
        observerRef.current?.disconnect();
      };
    }
  }, [trigger, start]);

  const handleHover = useCallback(() => {
    if (trigger === 'onHover') {
      start();
    }
  }, [trigger, start]);

  const handleClick = useCallback(() => {
    if (trigger === 'onClick') {
      start();
    }
  }, [trigger, start]);

  const animationStyles: React.CSSProperties = {
    opacity: state.isVisible ? 1 : 0,
    transform: state.isVisible ? 'none' : 'translateX(-100%)'
  };

  return {
    state,
    start,
    stop,
    reset,
    toggle,
    setConfig: updateConfig,
    animationStyles,
    ref: elementRef,
    onMouseEnter: handleHover,
    onClick: handleClick
  };
};

// Specialized animation hooks
export const useFadeIn = (config?: Partial<AnimationConfig>) => {
  return useAnimation({
    type: 'fadeIn',
    duration: 600,
    easing: 'ease-out',
    ...config
  });
};

export const useSlideIn = (config?: Partial<AnimationConfig>) => {
  return useAnimation({
    type: 'slideIn',
    duration: 800,
    easing: 'ease-out',
    ...config
  });
};

export const useBounce = (config?: Partial<AnimationConfig>) => {
  return useAnimation({
    type: 'bounce',
    duration: 1000,
    easing: 'ease-in-out',
    repeat: 1,
    ...config
  });
};

export const usePulse = (config?: Partial<AnimationConfig>) => {
  return useAnimation({
    type: 'pulse',
    duration: 1000,
    easing: 'ease-in-out',
    repeat: 'infinite',
    ...config
  });
};

export const useShake = (config?: Partial<AnimationConfig>) => {
  return useAnimation({
    type: 'shake',
    duration: 500,
    easing: 'ease-in-out',
    repeat: 1,
    ...config
  });
};

// Hook for staggered animations
export const useStaggeredAnimation = (
  items: any[],
  baseConfig: AnimationConfig,
  staggerDelay: number = 100
) => {
  const animations = items.map((_, index) => 
    useAnimation({
      ...baseConfig,
      delay: (baseConfig.delay || 0) + (index * staggerDelay)
    })
  );

  const startAll = useCallback(() => {
    animations.forEach(animation => animation.start());
  }, [animations]);

  const stopAll = useCallback(() => {
    animations.forEach(animation => animation.stop());
  }, [animations]);

  const resetAll = useCallback(() => {
    animations.forEach(animation => animation.reset());
  }, [animations]);

  return {
    animations,
    startAll,
    stopAll,
    resetAll
  };
}; 