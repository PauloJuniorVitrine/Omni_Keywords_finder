import React, { useState, useEffect, useRef } from 'react';

export interface ShakeProps {
  children: React.ReactNode;
  intensity?: 'light' | 'medium' | 'strong' | 'custom';
  direction?: 'horizontal' | 'vertical' | 'both';
  distance?: number;
  duration?: number;
  delay?: number;
  repeat?: number | 'infinite';
  trigger?: 'onMount' | 'onHover' | 'onClick' | 'onError' | 'manual';
  className?: string;
  style?: React.CSSProperties;
  onAnimationStart?: () => void;
  onAnimationEnd?: () => void;
}

export const Shake: React.FC<ShakeProps> = ({
  children,
  intensity = 'medium',
  direction = 'horizontal',
  distance = 10,
  duration = 500,
  delay = 0,
  repeat = 1,
  trigger = 'onMount',
  className = '',
  style = {},
  onAnimationStart,
  onAnimationEnd
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const getIntensityDistance = () => {
    switch (intensity) {
      case 'light':
        return 5;
      case 'medium':
        return 10;
      case 'strong':
        return 20;
      case 'custom':
        return distance;
      default:
        return 10;
    }
  };

  const getKeyframes = () => {
    const dist = getIntensityDistance();
    
    switch (direction) {
      case 'horizontal':
        return `
          @keyframes shake-horizontal {
            0%, 100% {
              transform: translateX(0);
            }
            10%, 30%, 50%, 70%, 90% {
              transform: translateX(-${dist}px);
            }
            20%, 40%, 60%, 80% {
              transform: translateX(${dist}px);
            }
          }
        `;
      
      case 'vertical':
        return `
          @keyframes shake-vertical {
            0%, 100% {
              transform: translateY(0);
            }
            10%, 30%, 50%, 70%, 90% {
              transform: translateY(-${dist}px);
            }
            20%, 40%, 60%, 80% {
              transform: translateY(${dist}px);
            }
          }
        `;
      
      case 'both':
        return `
          @keyframes shake-both {
            0%, 100% {
              transform: translate(0, 0);
            }
            10%, 30%, 50%, 70%, 90% {
              transform: translate(-${dist}px, -${dist}px);
            }
            20%, 40%, 60%, 80% {
              transform: translate(${dist}px, ${dist}px);
            }
          }
        `;
      
      default:
        return '';
    }
  };

  const getAnimationName = () => {
    return `shake-${direction}`;
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
      ? `${getAnimationName()} ${duration}ms ease-in-out ${delay}ms ${repeat}`
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
export const LightShake: React.FC<Omit<ShakeProps, 'intensity'>> = (props) => (
  <Shake {...props} intensity="light" />
);

export const MediumShake: React.FC<Omit<ShakeProps, 'intensity'>> = (props) => (
  <Shake {...props} intensity="medium" />
);

export const StrongShake: React.FC<Omit<ShakeProps, 'intensity'>> = (props) => (
  <Shake {...props} intensity="strong" />
);

// Direction-specific components
export const ShakeHorizontal: React.FC<Omit<ShakeProps, 'direction'>> = (props) => (
  <Shake {...props} direction="horizontal" />
);

export const ShakeVertical: React.FC<Omit<ShakeProps, 'direction'>> = (props) => (
  <Shake {...props} direction="vertical" />
);

export const ShakeBoth: React.FC<Omit<ShakeProps, 'direction'>> = (props) => (
  <Shake {...props} direction="both" />
);

// Specialized shake animations
export const ErrorShake: React.FC<Omit<ShakeProps, 'trigger' | 'intensity'> & { 
  onError?: () => void;
}> = ({ onError, ...props }) => {
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  return (
    <Shake
      {...props}
      intensity="medium"
      trigger="manual"
      repeat={3}
      onAnimationStart={handleError}
    >
      {props.children}
    </Shake>
  );
};

export const AttentionShake: React.FC<Omit<ShakeProps, 'trigger' | 'intensity'> & {
  attentionLevel?: 'low' | 'medium' | 'high';
}> = ({ attentionLevel = 'medium', ...props }) => {
  const getAttentionIntensity = () => {
    switch (attentionLevel) {
      case 'low':
        return 'light';
      case 'medium':
        return 'medium';
      case 'high':
        return 'strong';
      default:
        return 'medium';
    }
  };

  return (
    <Shake
      {...props}
      intensity={getAttentionIntensity()}
      trigger="onMount"
      repeat={2}
    >
      {props.children}
    </Shake>
  );
};

// Shake with rotation
export const ShakeRotate: React.FC<Omit<ShakeProps, 'direction'> & {
  rotationAngle?: number;
}> = ({ rotationAngle = 5, ...props }) => {
  const [isAnimating, setIsAnimating] = useState(false);

  const getRotateKeyframes = () => `
    @keyframes shake-rotate {
      0%, 100% {
        transform: rotate(0deg);
      }
      25% {
        transform: rotate(-${rotationAngle}deg);
      }
      75% {
        transform: rotate(${rotationAngle}deg);
      }
    }
  `;

  const startAnimation = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    props.onAnimationStart?.();
  };

  useEffect(() => {
    if (props.trigger === 'onMount') {
      startAnimation();
    }
  }, [props.trigger]);

  const animationStyles: React.CSSProperties = {
    animation: isAnimating 
      ? `shake-rotate ${props.duration || 500}ms ease-in-out ${props.delay || 0}ms ${props.repeat || 1}`
      : 'none',
    ...props.style
  };

  return (
    <>
      <style>{getRotateKeyframes()}</style>
      <div
        className={props.className}
        style={animationStyles}
        onMouseEnter={props.trigger === 'onHover' ? startAnimation : undefined}
        onClick={props.trigger === 'onClick' ? startAnimation : undefined}
      >
        {props.children}
      </div>
    </>
  );
};

// Shake with scale
export const ShakeScale: React.FC<Omit<ShakeProps, 'direction'> & {
  scaleFactor?: number;
}> = ({ scaleFactor = 0.95, ...props }) => {
  const [isAnimating, setIsAnimating] = useState(false);

  const getScaleKeyframes = () => `
    @keyframes shake-scale {
      0%, 100% {
        transform: scale(1);
      }
      50% {
        transform: scale(${scaleFactor});
      }
    }
  `;

  const startAnimation = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    props.onAnimationStart?.();
  };

  useEffect(() => {
    if (props.trigger === 'onMount') {
      startAnimation();
    }
  }, [props.trigger]);

  const animationStyles: React.CSSProperties = {
    animation: isAnimating 
      ? `shake-scale ${props.duration || 500}ms ease-in-out ${props.delay || 0}ms ${props.repeat || 1}`
      : 'none',
    ...props.style
  };

  return (
    <>
      <style>{getScaleKeyframes()}</style>
      <div
        className={props.className}
        style={animationStyles}
        onMouseEnter={props.trigger === 'onHover' ? startAnimation : undefined}
        onClick={props.trigger === 'onClick' ? startAnimation : undefined}
      >
        {props.children}
      </div>
    </>
  );
}; 