// Animation constants
export const ANIMATION_DURATIONS = {
  fast: 200,
  normal: 400,
  slow: 800,
  verySlow: 1200
} as const;

export const ANIMATION_EASINGS = {
  linear: 'linear',
  ease: 'ease',
  easeIn: 'ease-in',
  easeOut: 'ease-out',
  easeInOut: 'ease-in-out',
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  elastic: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
  smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
  sharp: 'cubic-bezier(0.4, 0, 0.6, 1)'
} as const;

export const ANIMATION_DELAYS = {
  none: 0,
  short: 100,
  medium: 200,
  long: 500
} as const;

// Animation presets
export const ANIMATION_PRESETS = {
  fadeIn: {
    duration: ANIMATION_DURATIONS.normal,
    easing: ANIMATION_EASINGS.easeOut,
    delay: ANIMATION_DELAYS.none
  },
  fadeOut: {
    duration: ANIMATION_DURATIONS.fast,
    easing: ANIMATION_EASINGS.easeIn,
    delay: ANIMATION_DELAYS.none
  },
  slideIn: {
    duration: ANIMATION_DURATIONS.slow,
    easing: ANIMATION_EASINGS.smooth,
    delay: ANIMATION_DELAYS.none
  },
  slideOut: {
    duration: ANIMATION_DURATIONS.normal,
    easing: ANIMATION_EASINGS.sharp,
    delay: ANIMATION_DELAYS.none
  },
  bounce: {
    duration: ANIMATION_DURATIONS.slow,
    easing: ANIMATION_EASINGS.bounce,
    delay: ANIMATION_DELAYS.none
  },
  pulse: {
    duration: ANIMATION_DURATIONS.slow,
    easing: ANIMATION_EASINGS.easeInOut,
    delay: ANIMATION_DELAYS.none
  },
  shake: {
    duration: ANIMATION_DURATIONS.fast,
    easing: ANIMATION_EASINGS.easeInOut,
    delay: ANIMATION_DELAYS.none
  },
  scaleIn: {
    duration: ANIMATION_DURATIONS.normal,
    easing: ANIMATION_EASINGS.elastic,
    delay: ANIMATION_DELAYS.none
  },
  scaleOut: {
    duration: ANIMATION_DURATIONS.fast,
    easing: ANIMATION_EASINGS.sharp,
    delay: ANIMATION_DELAYS.none
  }
} as const;

// Utility functions
export const createKeyframes = (name: string, keyframes: Record<string, any>[]): string => {
  const keyframeString = keyframes
    .map((frame, index) => {
      const percentage = (index / (keyframes.length - 1)) * 100;
      const properties = Object.entries(frame)
        .map(([key, value]) => `${key}: ${value}`)
        .join('; ');
      return `${percentage}% { ${properties} }`;
    })
    .join('\n');

  return `@keyframes ${name} {\n${keyframeString}\n}`;
};

export const createAnimation = (
  name: string,
  duration: number = ANIMATION_DURATIONS.normal,
  easing: string = ANIMATION_EASINGS.easeOut,
  delay: number = ANIMATION_DELAYS.none,
  repeat: number | 'infinite' = 1,
  direction: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse' = 'normal',
  fillMode: 'none' | 'forwards' | 'backwards' | 'both' = 'forwards'
): string => {
  return `${name} ${duration}ms ${easing} ${delay}ms ${repeat} ${direction} ${fillMode}`;
};

export const getStaggeredDelay = (
  index: number,
  baseDelay: number = ANIMATION_DELAYS.none,
  staggerDelay: number = ANIMATION_DELAYS.short
): number => {
  return baseDelay + (index * staggerDelay);
};

export const calculateProgress = (
  startTime: number,
  duration: number,
  currentTime: number = Date.now()
): number => {
  const elapsed = currentTime - startTime;
  return Math.min(Math.max(elapsed / duration, 0), 1);
};

export const interpolate = (
  start: number,
  end: number,
  progress: number,
  easing: (t: number) => number = (t) => t
): number => {
  const easedProgress = easing(progress);
  return start + (end - start) * easedProgress;
};

// Easing functions
export const easingFunctions = {
  linear: (t: number): number => t,
  
  easeIn: (t: number): number => t * t,
  
  easeOut: (t: number): number => 1 - Math.pow(1 - t, 2),
  
  easeInOut: (t: number): number => 
    t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  
  bounce: (t: number): number => {
    if (t < 1 / 2.75) {
      return 7.5625 * t * t;
    } else if (t < 2 / 2.75) {
      return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
    } else if (t < 2.5 / 2.75) {
      return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
    } else {
      return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
    }
  },
  
  elastic: (t: number): number => {
    if (t === 0) return 0;
    if (t === 1) return 1;
    
    return Math.pow(2, -10 * t) * Math.sin((t - 0.075) * (2 * Math.PI) / 0.3) + 1;
  },
  
  back: (t: number): number => {
    const s = 1.70158;
    return t * t * ((s + 1) * t - s);
  },
  
  smooth: (t: number): number => {
    return t * t * (3 - 2 * t);
  }
};

// Animation helpers
export const createFadeInKeyframes = (): string => {
  return createKeyframes('fadeIn', [
    { opacity: 0 },
    { opacity: 1 }
  ]);
};

export const createSlideInKeyframes = (direction: 'left' | 'right' | 'up' | 'down' = 'left'): string => {
  const transforms = {
    left: ['translateX(-100%)', 'translateX(0)'],
    right: ['translateX(100%)', 'translateX(0)'],
    up: ['translateY(-100%)', 'translateY(0)'],
    down: ['translateY(100%)', 'translateY(0)']
  };

  return createKeyframes(`slideIn${direction.charAt(0).toUpperCase() + direction.slice(1)}`, [
    { transform: transforms[direction][0], opacity: 0 },
    { transform: transforms[direction][1], opacity: 1 }
  ]);
};

export const createBounceKeyframes = (): string => {
  return createKeyframes('bounce', [
    { transform: 'translateY(0)' },
    { transform: 'translateY(-20px)' },
    { transform: 'translateY(0)' }
  ]);
};

export const createPulseKeyframes = (): string => {
  return createKeyframes('pulse', [
    { transform: 'scale(1)' },
    { transform: 'scale(1.05)' },
    { transform: 'scale(1)' }
  ]);
};

export const createShakeKeyframes = (intensity: number = 10): string => {
  return createKeyframes('shake', [
    { transform: 'translateX(0)' },
    { transform: `translateX(-${intensity}px)` },
    { transform: `translateX(${intensity}px)` },
    { transform: `translateX(-${intensity}px)` },
    { transform: `translateX(${intensity}px)` },
    { transform: 'translateX(0)' }
  ]);
};

// Animation timing functions
export const createStaggeredAnimation = (
  items: any[],
  baseConfig: typeof ANIMATION_PRESETS.fadeIn,
  staggerDelay: number = ANIMATION_DELAYS.short
) => {
  return items.map((_, index) => ({
    ...baseConfig,
    delay: baseConfig.delay + (index * staggerDelay)
  }));
};

export const createSequentialAnimation = (
  items: any[],
  baseConfig: typeof ANIMATION_PRESETS.fadeIn,
  sequenceDelay: number = ANIMATION_DURATIONS.normal
) => {
  return items.map((_, index) => ({
    ...baseConfig,
    delay: baseConfig.delay + (index * sequenceDelay)
  }));
};

// Performance optimization
export const shouldReduceMotion = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

export const getOptimizedDuration = (baseDuration: number): number => {
  return shouldReduceMotion() ? Math.min(baseDuration, 200) : baseDuration;
};

export const getOptimizedEasing = (baseEasing: string): string => {
  return shouldReduceMotion() ? ANIMATION_EASINGS.linear : baseEasing;
};

// Animation validation
export const validateAnimationConfig = (config: any): boolean => {
  const requiredFields = ['duration', 'easing'];
  return requiredFields.every(field => config.hasOwnProperty(field));
};

export const sanitizeAnimationConfig = (config: any) => {
  return {
    duration: Math.max(0, Math.min(config.duration || 400, 5000)),
    easing: Object.values(ANIMATION_EASINGS).includes(config.easing) 
      ? config.easing 
      : ANIMATION_EASINGS.easeOut,
    delay: Math.max(0, Math.min(config.delay || 0, 2000)),
    repeat: config.repeat === 'infinite' ? 'infinite' : Math.max(0, Math.min(config.repeat || 1, 10))
  };
};

// Export all keyframes as a single stylesheet
export const generateAnimationStylesheet = (): string => {
  const keyframes = [
    createFadeInKeyframes(),
    createSlideInKeyframes('left'),
    createSlideInKeyframes('right'),
    createSlideInKeyframes('up'),
    createSlideInKeyframes('down'),
    createBounceKeyframes(),
    createPulseKeyframes(),
    createShakeKeyframes()
  ];

  return keyframes.join('\n\n');
}; 