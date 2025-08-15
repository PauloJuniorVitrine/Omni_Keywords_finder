import React, { useState, useEffect, useRef } from 'react';

export interface PulseProps {
  children: React.ReactNode;
  intensity?: 'light' | 'medium' | 'strong';
  duration?: number;
  delay?: number;
  repeat?: number | 'infinite';
  trigger?: 'onMount' | 'onHover' | 'onClick' | 'manual';
  className?: string;
  style?: React.CSSProperties;
  onAnimationStart?: () => void;
  onAnimationEnd?: () => void;
}

export const Pulse: React.FC<PulseProps> = ({
  children,
  intensity = 'medium',
  duration = 1000,
  delay = 0,
  repeat = 'infinite',
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const getIntensityScale = () => {
    switch (intensity) {
      case 'light':
        return 1.05;
      case 'medium':
        return 1.1;
      case 'strong':
        return 1.2;
      default:
        return 1.1;
    }
  };

  const getKeyframes = () => {
    const scale = getIntensityScale();
    return `
      @keyframes pulse-${intensity} {
        0% {
          transform: scale(1);
        }
        50% {
          transform: scale(${scale});
        }
        100% {
          transform: scale(1);
        }
      }
    `;
  };

  const startAnimation = () => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    onAnimationStart?.();
    
    if (repeat !== 'infinite') {
      setTimeout(() => {
        setIsAnimating(false);
        onAnimationEnd?.();
      }, delay + (duration * repeat));
    }
  };

  const stopAnimation = () => {
    setIsAnimating(false);
    onAnimationEnd?.();
  };

  // Handle different triggers
  useEffect(() => {
    if (trigger === 'onMount') {
      startAnimation();
    }
  }, [trigger]);

  const handleHover = () => {
    if (trigger === 'onHover') {
      if (!isAnimating) {
        startAnimation();
      }
    }
  };

  const handleMouseLeave = () => {
    if (trigger === 'onHover' && repeat === 'infinite') {
      stopAnimation();
    }
  };

  const handleClick = () => {
    if (trigger === 'onClick') {
      startAnimation();
    }
  };

  const animationStyles: React.CSSProperties = {
    animation: isAnimating 
      ? `pulse-${intensity} ${duration}ms ease-in-out ${delay}ms ${repeat}`
      : 'none',
    ...style
  };

  return (
    <>
      <style>{getKeyframes()}</style>
      <div
        ref={elementRef}
        className={className}
        style={animationStyles}
        onMouseEnter={handleHover}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
      >
        {children}
      </div>
    </>
  );
};

// Intensity-specific components
export const LightPulse: React.FC<Omit<PulseProps, 'intensity'>> = (props) => (
  <Pulse {...props} intensity="light" />
);

export const MediumPulse: React.FC<Omit<PulseProps, 'intensity'>> = (props) => (
  <Pulse {...props} intensity="medium" />
);

export const StrongPulse: React.FC<Omit<PulseProps, 'intensity'>> = (props) => (
  <Pulse {...props} intensity="strong" />
);

// Pulse with different effects
export interface PulseGlowProps extends Omit<PulseProps, 'intensity'> {
  color?: string;
  blur?: number;
}

export const PulseGlow: React.FC<PulseGlowProps> = ({
  children,
  color = '#3b82f6',
  blur = 10,
  duration = 1000,
  delay = 0,
  repeat = 'infinite',
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isAnimating, setIsAnimating] = useState(false);

  const getGlowKeyframes = () => `
    @keyframes pulse-glow {
      0% {
        box-shadow: 0 0 0 0 ${color}40;
      }
      70% {
        box-shadow: 0 0 0 ${blur}px ${color}00;
      }
      100% {
        box-shadow: 0 0 0 0 ${color}00;
      }
    }
  `;

  const startAnimation = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    onAnimationStart?.();
  };

  useEffect(() => {
    if (trigger === 'onMount') {
      startAnimation();
    }
  }, [trigger]);

  const animationStyles: React.CSSProperties = {
    animation: isAnimating 
      ? `pulse-glow ${duration}ms ease-in-out ${delay}ms ${repeat}`
      : 'none',
    ...style
  };

  return (
    <>
      <style>{getGlowKeyframes()}</style>
      <div
        className={className}
        style={animationStyles}
        onMouseEnter={trigger === 'onHover' ? startAnimation : undefined}
        onClick={trigger === 'onClick' ? startAnimation : undefined}
      >
        {children}
      </div>
    </>
  );
};

// Pulse with scale effect
export interface PulseScaleProps extends Omit<PulseProps, 'intensity'> {
  scale?: number;
}

export const PulseScale: React.FC<PulseScaleProps> = ({
  children,
  scale = 1.1,
  duration = 1000,
  delay = 0,
  repeat = 'infinite',
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isAnimating, setIsAnimating] = useState(false);

  const getScaleKeyframes = () => `
    @keyframes pulse-scale {
      0% {
        transform: scale(1);
      }
      50% {
        transform: scale(${scale});
      }
      100% {
        transform: scale(1);
      }
    }
  `;

  const startAnimation = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    onAnimationStart?.();
  };

  useEffect(() => {
    if (trigger === 'onMount') {
      startAnimation();
    }
  }, [trigger]);

  const animationStyles: React.CSSProperties = {
    animation: isAnimating 
      ? `pulse-scale ${duration}ms ease-in-out ${delay}ms ${repeat}`
      : 'none',
    ...style
  };

  return (
    <>
      <style>{getScaleKeyframes()}</style>
      <div
        className={className}
        style={animationStyles}
        onMouseEnter={trigger === 'onHover' ? startAnimation : undefined}
        onClick={trigger === 'onClick' ? startAnimation : undefined}
      >
        {children}
      </div>
    </>
  );
};

// Pulse with opacity effect
export const PulseOpacity: React.FC<Omit<PulseProps, 'intensity'>> = ({
  children,
  duration = 1000,
  delay = 0,
  repeat = 'infinite',
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isAnimating, setIsAnimating] = useState(false);

  const getOpacityKeyframes = () => `
    @keyframes pulse-opacity {
      0% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
      100% {
        opacity: 1;
      }
    }
  `;

  const startAnimation = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    onAnimationStart?.();
  };

  useEffect(() => {
    if (trigger === 'onMount') {
      startAnimation();
    }
  }, [trigger]);

  const animationStyles: React.CSSProperties = {
    animation: isAnimating 
      ? `pulse-opacity ${duration}ms ease-in-out ${delay}ms ${repeat}`
      : 'none',
    ...style
  };

  return (
    <>
      <style>{getOpacityKeyframes()}</style>
      <div
        className={className}
        style={animationStyles}
        onMouseEnter={trigger === 'onHover' ? startAnimation : undefined}
        onClick={trigger === 'onClick' ? startAnimation : undefined}
      >
        {children}
      </div>
    </>
  );
}; 